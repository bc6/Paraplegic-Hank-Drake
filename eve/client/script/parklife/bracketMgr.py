import service
import form
import blue
import uix
import uiutil
import xtriui
import base
import uthread
import state
import util
import trinity
import sys
import fleetbr
import math
import stackless
import log
import uiconst
import weakref
import localization
import bluepy
SHOW_NONE = -1
SHOW_DEFAULT = 0
SHOW_ALL = 1

class BracketMgr(service.Service):
    __guid__ = 'svc.bracket'
    __update_on_reload__ = 0
    __exportedcalls__ = {'GetBracketName': [],
     'GetBracketName2': [],
     'SetBracketName': [],
     'ResetOverlaps': [],
     'CheckOverlaps': [],
     'CleanUp': [],
     'ClearBracket': [],
     'ShowAll': [],
     'ShowNone': [],
     'ShowingAll': [],
     'ShowingNone': [],
     'GetBracketProps': [],
     'Reload': [],
     'GetScanSpeed': [],
     'GetCaptureData': []}
    __notifyevents__ = ['DoBallsAdded',
     'DoBallRemove',
     'DoBallClear',
     'ProcessSessionChange',
     'OnStateChange',
     'OnDestinationSet',
     'OnPostCfgDataChanged',
     'OnBallparkCall',
     'OnSlimItemChange',
     'OnAttribute',
     'OnAttributes',
     'OnCaptureChanged',
     'OnBSDTablesChanged',
     'ProcessShipEffect']
    __dependencies__ = ['michelle',
     'tactical',
     'map',
     'settings',
     'target']

    def __init__(self):
        service.Service.__init__(self)
        self.unwantedBracketGroups = [const.groupSecondarySun]
        self.showState = SHOW_DEFAULT



    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        self.scenarioMgr = sm.StartService('scenario')
        self.Reload(False)



    def Stop(self, stream):
        self.CleanUp()



    def CleanUp(self):
        if getattr(self, 'brackets', {}):
            toRemove = self.brackets.keys()
            for each in toRemove:
                self.ClearBracket(each)

        self.brackets = {}
        self.shipLabels = None
        self.updateBrackets = []
        self.cat_mapping = {}
        self.grp_mapping = {}
        self.type_mapping = {}
        self.overlaps = []
        self.overlapsHidden = []
        self.checkingOverlaps = 0
        self.gotProps = 0
        self.updatingAll = 0
        self.showallTimer = None
        self.showHiddenTimer = None
        self.updatelazy = None
        uicore.layer.bracket.Flush()



    def Hide(self):
        l_bracket = uicore.layer.bracket
        if l_bracket:
            l_bracket.state = uiconst.UI_HIDDEN



    def Show(self):
        l_bracket = uicore.layer.bracket
        if l_bracket:
            l_bracket.state = uiconst.UI_PICKCHILDREN



    def Reload(self, waitForPark = True):
        self.specials = (const.groupLargeCollidableStructure, const.groupMoon)
        self.bypassFilter = False
        self.CleanUp()
        ballPark = sm.GetService('michelle').GetBallpark(doWait=waitForPark)
        if not ballPark:
            return 
        lst = []
        for (ballID, ball,) in ballPark.balls.iteritems():
            slimItem = ballPark.GetInvItem(ballID)
            if slimItem:
                lst.append((ball, slimItem))

        self.DoBallsAdded(lst, ignoreAsteroids=False)



    def SetupProps(self):
        self.npcSpecial = [const.groupConcordDrone,
         const.groupConvoy,
         const.groupConvoyDrone,
         const.groupCustomsOfficial,
         const.groupFactionDrone,
         const.groupMissionDrone,
         const.groupPirateDrone,
         const.groupPoliceDrone,
         const.groupRogueDrone,
         const.groupStorylineBattleship,
         const.groupStorylineFrigate,
         const.groupStorylineCruiser,
         const.groupStorylineMissionBattleship,
         const.groupStorylineMissionFrigate,
         const.groupStorylineMissionCruiser,
         const.groupAsteroidAngelCartelBattleCruiser,
         const.groupAsteroidAngelCartelBattleship,
         const.groupAsteroidAngelCartelCruiser,
         const.groupAsteroidAngelCartelDestroyer,
         const.groupAsteroidAngelCartelFrigate,
         const.groupAsteroidAngelCartelHauler,
         const.groupAsteroidAngelCartelOfficer,
         const.groupAsteroidBloodRaidersBattleCruiser,
         const.groupAsteroidBloodRaidersBattleship,
         const.groupAsteroidBloodRaidersCruiser,
         const.groupAsteroidBloodRaidersDestroyer,
         const.groupAsteroidBloodRaidersFrigate,
         const.groupAsteroidBloodRaidersHauler,
         const.groupAsteroidBloodRaidersOfficer,
         const.groupAsteroidGuristasBattleCruiser,
         const.groupAsteroidGuristasBattleship,
         const.groupAsteroidGuristasCruiser,
         const.groupAsteroidGuristasDestroyer,
         const.groupAsteroidGuristasFrigate,
         const.groupAsteroidGuristasHauler,
         const.groupAsteroidGuristasOfficer,
         const.groupAsteroidSanshasNationBattleCruiser,
         const.groupAsteroidSanshasNationBattleship,
         const.groupAsteroidSanshasNationCruiser,
         const.groupAsteroidSanshasNationDestroyer,
         const.groupAsteroidSanshasNationFrigate,
         const.groupAsteroidSanshasNationHauler,
         const.groupAsteroidSanshasNationOfficer,
         const.groupAsteroidSerpentisBattleCruiser,
         const.groupAsteroidSerpentisBattleship,
         const.groupAsteroidSerpentisCruiser,
         const.groupAsteroidSerpentisDestroyer,
         const.groupAsteroidSerpentisFrigate,
         const.groupAsteroidSerpentisHauler,
         const.groupAsteroidSerpentisOfficer,
         const.groupDeadspaceAngelCartelBattleCruiser,
         const.groupDeadspaceAngelCartelBattleship,
         const.groupDeadspaceAngelCartelCruiser,
         const.groupDeadspaceAngelCartelDestroyer,
         const.groupDeadspaceAngelCartelFrigate,
         const.groupDeadspaceBloodRaidersBattleCruiser,
         const.groupDeadspaceBloodRaidersBattleship,
         const.groupDeadspaceBloodRaidersCruiser,
         const.groupDeadspaceBloodRaidersDestroyer,
         const.groupDeadspaceBloodRaidersFrigate,
         const.groupDeadspaceGuristasBattleCruiser,
         const.groupDeadspaceGuristasBattleship,
         const.groupDeadspaceGuristasCruiser,
         const.groupDeadspaceGuristasDestroyer,
         const.groupDeadspaceGuristasFrigate,
         const.groupDeadspaceSanshasNationBattleCruiser,
         const.groupDeadspaceSanshasNationBattleship,
         const.groupDeadspaceSanshasNationCruiser,
         const.groupDeadspaceSanshasNationDestroyer,
         const.groupDeadspaceSanshasNationFrigate,
         const.groupDeadspaceSerpentisBattleCruiser,
         const.groupDeadspaceSerpentisBattleship,
         const.groupDeadspaceSerpentisCruiser,
         const.groupDeadspaceSerpentisDestroyer,
         const.groupDeadspaceSerpentisFrigate,
         const.groupDeadspaceSleeperSleeplessPatroller,
         const.groupDeadspaceSleeperSleeplessSentinel,
         const.groupDeadspaceSleeperSleeplessDefender,
         const.groupDeadspaceSleeperAwakenedPatroller,
         const.groupDeadspaceSleeperAwakenedSentinel,
         const.groupDeadspaceSleeperAwakenedDefender,
         const.groupDeadspaceSleeperEmergentPatroller,
         const.groupDeadspaceSleeperEmergentSentinel,
         const.groupDeadspaceSleeperEmergentDefender,
         const.groupDeadspaceOverseer,
         const.groupMissionAmarrEmpireBattlecruiser,
         const.groupMissionAmarrEmpireBattleship,
         const.groupMissionAmarrEmpireCruiser,
         const.groupMissionAmarrEmpireDestroyer,
         const.groupMissionAmarrEmpireFrigate,
         const.groupMissionAmarrEmpireOther,
         const.groupMissionCONCORDBattlecruiser,
         const.groupMissionCONCORDBattleship,
         const.groupMissionCONCORDCruiser,
         const.groupMissionCONCORDDestroyer,
         const.groupMissionCONCORDFrigate,
         const.groupMissionCONCORDOther,
         const.groupMissionCaldariStateBattlecruiser,
         const.groupMissionCaldariStateBattleship,
         const.groupMissionCaldariStateCruiser,
         const.groupMissionCaldariStateDestroyer,
         const.groupMissionCaldariStateFrigate,
         const.groupMissionCaldariStateOther,
         const.groupMissionGallenteFederationBattlecruiser,
         const.groupMissionGallenteFederationBattleship,
         const.groupMissionGallenteFederationCruiser,
         const.groupMissionGallenteFederationDestroyer,
         const.groupMissionGallenteFederationFrigate,
         const.groupMissionGallenteFederationOther,
         const.groupMissionKhanidBattlecruiser,
         const.groupMissionKhanidBattleship,
         const.groupMissionKhanidCruiser,
         const.groupMissionKhanidDestroyer,
         const.groupMissionKhanidFrigate,
         const.groupMissionKhanidOther,
         const.groupMissionMinmatarRepublicBattlecruiser,
         const.groupMissionMinmatarRepublicBattleship,
         const.groupMissionMinmatarRepublicCruiser,
         const.groupMissionMinmatarRepublicDestroyer,
         const.groupMissionMinmatarRepublicFrigate,
         const.groupMissionMinmatarRepublicOther,
         const.groupMissionMorduBattlecruiser,
         const.groupMissionMorduBattleship,
         const.groupMissionMorduCruiser,
         const.groupMissionMorduDestroyer,
         const.groupMissionMorduFrigate,
         const.groupMissionMorduOther,
         const.groupAsteroidAngelCartelCommanderBattleCruiser,
         const.groupAsteroidAngelCartelCommanderCruiser,
         const.groupAsteroidAngelCartelCommanderDestroyer,
         const.groupAsteroidAngelCartelCommanderFrigate,
         const.groupAsteroidBloodRaidersCommanderBattleCruiser,
         const.groupAsteroidBloodRaidersCommanderCruiser,
         const.groupAsteroidBloodRaidersCommanderDestroyer,
         const.groupAsteroidBloodRaidersCommanderFrigate,
         const.groupAsteroidGuristasCommanderBattleCruiser,
         const.groupAsteroidGuristasCommanderCruiser,
         const.groupAsteroidGuristasCommanderDestroyer,
         const.groupAsteroidGuristasCommanderFrigate,
         const.groupAsteroidRogueDroneBattleCruiser,
         const.groupAsteroidRogueDroneBattleship,
         const.groupAsteroidRogueDroneCruiser,
         const.groupAsteroidRogueDroneDestroyer,
         const.groupAsteroidRogueDroneFrigate,
         const.groupAsteroidRogueDroneHauler,
         const.groupAsteroidRogueDroneSwarm,
         const.groupAsteroidSanshasNationCommanderBattleCruiser,
         const.groupAsteroidSanshasNationCommanderCruiser,
         const.groupAsteroidSanshasNationCommanderDestroyer,
         const.groupAsteroidSanshasNationCommanderFrigate,
         const.groupAsteroidSerpentisCommanderBattleCruiser,
         const.groupAsteroidSerpentisCommanderCruiser,
         const.groupAsteroidSerpentisCommanderDestroyer,
         const.groupAsteroidSerpentisCommanderFrigate,
         const.groupDeadspaceRogueDroneBattleCruiser,
         const.groupDeadspaceRogueDroneBattleship,
         const.groupDeadspaceRogueDroneCruiser,
         const.groupDeadspaceRogueDroneDestroyer,
         const.groupDeadspaceRogueDroneFrigate,
         const.groupDeadspaceRogueDroneSwarm,
         const.groupDeadspaceOverseerFrigate,
         const.groupDeadspaceOverseerCruiser,
         const.groupDeadspaceOverseerBattleship,
         const.groupMissionGenericBattleships,
         const.groupMissionGenericCruisers,
         const.groupMissionGenericFrigates,
         const.groupMissionThukkerBattlecruiser,
         const.groupMissionThukkerBattleship,
         const.groupMissionThukkerCruiser,
         const.groupMissionThukkerDestroyer,
         const.groupMissionThukkerFrigate,
         const.groupMissionThukkerOther,
         const.groupMissionGenericBattleCruisers,
         const.groupMissionGenericDestroyers,
         const.groupAsteroidRogueDroneCommanderFrigate,
         const.groupAsteroidRogueDroneCommanderDestroyer,
         const.groupAsteroidRogueDroneCommanderCruiser,
         const.groupAsteroidRogueDroneCommanderBattleCruiser,
         const.groupAsteroidRogueDroneCommanderBattleship,
         const.groupAsteroidAngelCartelCommanderBattleship,
         const.groupAsteroidBloodRaidersCommanderBattleship,
         const.groupAsteroidGuristasCommanderBattleship,
         const.groupAsteroidSanshasNationCommanderBattleship,
         const.groupAsteroidSerpentisCommanderBattleship,
         const.groupMissionAmarrEmpireCarrier,
         const.groupMissionCaldariStateCarrier,
         const.groupMissionGallenteFederationCarrier,
         const.groupMissionMinmatarRepublicCarrier,
         const.groupMissionFighterDrone,
         const.groupMissionGenericFreighters,
         const.groupTutorialDrone,
         const.groupMissionFactionBattleships,
         const.groupMissionFactionCruisers,
         const.groupMissionFactionFrigates,
         const.groupMissionFactionIndustrials,
         const.groupInvasionSanshaNationBattleship,
         const.groupInvasionSanshaNationCapital,
         const.groupInvasionSanshaNationCruiser,
         const.groupInvasionSanshaNationFrigate,
         const.groupInvasionSanshaNationIndustrial]
        self.npcSpecialIcons = ['ui_38_16_21', 'ui_38_16_22', 'ui_38_16_23']
        inf = 1e+32
        self.cat_mapping = {const.categoryShip: ('ui_38_16_5',
                              1,
                              2000.0,
                              inf,
                              0,
                              0),
         const.categoryEntity: ('ui_38_16_5',
                                1,
                                0.0,
                                inf,
                                0,
                                0),
         const.categoryDrone: ('ui_38_16_6',
                               1,
                               0.0,
                               inf,
                               0,
                               0),
         const.categoryDeployable: ('ui_38_16_129',
                                    1,
                                    0.0,
                                    inf,
                                    0,
                                    0),
         const.categoryStructure: ('ui_38_16_129',
                                   1,
                                   0.0,
                                   inf,
                                   0,
                                   0),
         const.categorySovereigntyStructure: ('ui_38_16_129',
                                              1,
                                              0.0,
                                              inf,
                                              0,
                                              0),
         const.categoryAsteroid: ('ui_38_16_241',
                                  1,
                                  0.0,
                                  inf,
                                  0,
                                  0),
         const.categoryOrbital: ('ui_38_16_31',
                                 1,
                                 0.0,
                                 inf,
                                 0,
                                 0)}
        self.grp_mapping = {const.groupCargoContainer: ('ui_38_16_12',
                                     1,
                                     0.0,
                                     inf,
                                     0,
                                     0),
         const.groupDeadspaceOverseersBelongings: ('ui_38_16_12',
                                                   1,
                                                   0.0,
                                                   inf,
                                                   0,
                                                   0),
         const.groupFreightContainer: ('ui_38_16_12',
                                       1,
                                       0.0,
                                       inf,
                                       0,
                                       0),
         const.groupMissionContainer: ('ui_38_16_12',
                                       1,
                                       0.0,
                                       inf,
                                       0,
                                       0),
         const.groupSecureCargoContainer: ('ui_38_16_12',
                                           1,
                                           0.0,
                                           inf,
                                           0,
                                           0),
         const.groupAuditLogSecureContainer: ('ui_38_16_12',
                                              1,
                                              0.0,
                                              inf,
                                              0,
                                              0),
         const.groupSpawnContainer: ('ui_38_16_12',
                                     1,
                                     0.0,
                                     inf,
                                     0,
                                     0),
         const.groupStation: ('ui_38_16_252',
                              1,
                              7000.0,
                              inf,
                              0,
                              0),
         const.groupConstructionPlatform: ('ui_38_16_252', 1, 0.0, 50000.0, 0, 0),
         const.groupStationImprovementPlatform: ('ui_38_16_252', 1, 0.0, 50000.0, 0, 0),
         const.groupStationUpgradePlatform: ('ui_38_16_252', 1, 0.0, 50000.0, 0, 0),
         const.groupDestructibleStationServices: ('ui_38_16_135',
                                                  1,
                                                  0.0,
                                                  inf,
                                                  0,
                                                  0),
         const.groupStargate: ('ui_38_16_251',
                               1,
                               0.0,
                               inf,
                               0,
                               0),
         const.groupWarpGate: ('ui_38_16_250',
                               1,
                               0.0,
                               inf,
                               0,
                               0),
         const.groupAsteroidBelt: ('ui_38_16_253',
                                   1,
                                   50000.0,
                                   inf,
                                   -20,
                                   0),
         const.groupWreck: ('ui_38_16_29',
                            1,
                            0.0,
                            inf,
                            0,
                            0),
         const.groupSentryGun: ('ui_38_16_13',
                                1,
                                2000.0,
                                inf,
                                0,
                                0),
         const.groupMobileSentryGun: ('ui_38_16_13',
                                      1,
                                      2000.0,
                                      inf,
                                      0,
                                      0),
         const.groupProtectiveSentryGun: ('ui_38_16_13',
                                          1,
                                          2000.0,
                                          inf,
                                          0,
                                          0),
         const.groupDestructibleSentryGun: ('ui_38_16_13',
                                            1,
                                            2000.0,
                                            inf,
                                            0,
                                            0),
         const.groupDeadspaceOverseersSentry: ('ui_38_16_13',
                                               1,
                                               2000.0,
                                               inf,
                                               0,
                                               0),
         const.groupCapsule: ('ui_38_16_11',
                              1,
                              0.0,
                              inf,
                              0,
                              0),
         const.groupRookieship: ('ui_38_16_1',
                                 1,
                                 0.0,
                                 inf,
                                 0,
                                 0),
         const.groupFrigate: ('ui_38_16_1',
                              1,
                              0.0,
                              inf,
                              0,
                              0),
         const.groupShuttle: ('ui_38_16_1',
                              1,
                              0.0,
                              inf,
                              0,
                              0),
         const.groupAssaultShip: ('ui_38_16_1',
                                  1,
                                  0.0,
                                  inf,
                                  0,
                                  0),
         const.groupCovertOps: ('ui_38_16_1',
                                1,
                                0.0,
                                inf,
                                0,
                                0),
         const.groupInterceptor: ('ui_38_16_1',
                                  1,
                                  0.0,
                                  inf,
                                  0,
                                  0),
         const.groupStealthBomber: ('ui_38_16_1',
                                    1,
                                    0.0,
                                    inf,
                                    0,
                                    0),
         const.groupElectronicAttackShips: ('ui_38_16_1',
                                            1,
                                            0.0,
                                            inf,
                                            0,
                                            0),
         const.groupPrototypeExplorationShip: ('ui_38_16_1',
                                               1,
                                               0.0,
                                               inf,
                                               0,
                                               0),
         const.groupDestroyer: ('ui_38_16_2',
                                1,
                                0.0,
                                inf,
                                0,
                                0),
         const.groupCruiser: ('ui_38_16_2',
                              1,
                              0.0,
                              inf,
                              0,
                              0),
         const.groupStrategicCruiser: ('ui_38_16_2',
                                       1,
                                       0.0,
                                       inf,
                                       0,
                                       0),
         const.groupBattlecruiser: ('ui_38_16_2',
                                    1,
                                    0.0,
                                    inf,
                                    0,
                                    0),
         const.groupInterdictor: ('ui_38_16_2',
                                  1,
                                  0.0,
                                  inf,
                                  0,
                                  0),
         const.groupHeavyAssaultShip: ('ui_38_16_2',
                                       1,
                                       0.0,
                                       inf,
                                       0,
                                       0),
         const.groupLogistics: ('ui_38_16_2',
                                1,
                                0.0,
                                inf,
                                0,
                                0),
         const.groupForceReconShip: ('ui_38_16_2',
                                     1,
                                     0.0,
                                     inf,
                                     0,
                                     0),
         const.groupCombatReconShip: ('ui_38_16_2',
                                      1,
                                      0.0,
                                      inf,
                                      0,
                                      0),
         const.groupCommandShip: ('ui_38_16_2',
                                  1,
                                  0.0,
                                  inf,
                                  0,
                                  0),
         const.groupHeavyInterdictors: ('ui_38_16_2',
                                        1,
                                        0.0,
                                        inf,
                                        0,
                                        0),
         const.groupMiningBarge: ('ui_38_16_3',
                                  1,
                                  0.0,
                                  inf,
                                  0,
                                  0),
         const.groupIndustrial: ('ui_38_16_3',
                                 1,
                                 0.0,
                                 inf,
                                 0,
                                 0),
         const.groupIndustrialCommandShip: ('ui_38_16_3',
                                            1,
                                            0.0,
                                            inf,
                                            0,
                                            0),
         const.groupFreighter: ('ui_38_16_3',
                                1,
                                0.0,
                                inf,
                                0,
                                0),
         const.groupExhumer: ('ui_38_16_3',
                              1,
                              0.0,
                              inf,
                              0,
                              0),
         const.groupTransportShip: ('ui_38_16_3',
                                    1,
                                    0.0,
                                    inf,
                                    0,
                                    0),
         const.groupJumpFreighter: ('ui_38_16_3',
                                    1,
                                    0.0,
                                    inf,
                                    0,
                                    0),
         const.groupBattleship: ('ui_38_16_4',
                                 1,
                                 0.0,
                                 inf,
                                 0,
                                 0),
         const.groupDreadnought: ('ui_38_16_4',
                                  1,
                                  0.0,
                                  inf,
                                  0,
                                  0),
         const.groupCarrier: ('ui_38_16_4',
                              1,
                              0.0,
                              inf,
                              0,
                              0),
         const.groupSupercarrier: ('ui_38_16_4',
                                   1,
                                   0.0,
                                   inf,
                                   0,
                                   0),
         const.groupTitan: ('ui_38_16_4',
                            1,
                            0.0,
                            inf,
                            0,
                            0),
         const.groupEliteBattleship: ('ui_38_16_4',
                                      1,
                                      0.0,
                                      inf,
                                      0,
                                      0),
         const.groupCapitalIndustrialShip: ('ui_38_16_4',
                                            1,
                                            0.0,
                                            inf,
                                            0,
                                            0),
         const.groupMarauders: ('ui_38_16_4',
                                1,
                                0.0,
                                inf,
                                0,
                                0),
         const.groupBlackOps: ('ui_38_16_4',
                               1,
                               0.0,
                               inf,
                               0,
                               0),
         const.groupMissile: ('ui_38_16_241', 1, 0.0, 1.0, 0, 0),
         const.groupBomb: ('ui_38_16_7',
                           1,
                           0.0,
                           inf,
                           0,
                           0),
         const.groupBeacon: ('ui_38_16_14',
                             1,
                             0.0,
                             inf,
                             0,
                             0),
         const.groupPlanet: ('ui_38_16_255',
                             1,
                             0.0,
                             inf,
                             0,
                             0),
         const.groupMoon: ('ui_38_16_256',
                           0,
                           0.0,
                           inf,
                           0,
                           0),
         const.groupSun: ('ui_38_16_254',
                          1,
                          0.0,
                          inf,
                          0,
                          0),
         const.groupSecondarySun: ('ui_38_16_254', 1, 0.0, 1.0, 0, 0),
         const.groupBillboard: ('ui_38_16_241',
                                1,
                                0.0,
                                inf,
                                0,
                                0),
         const.groupMobileWarpDisruptor: ('ui_38_16_130',
                                          1,
                                          0.0,
                                          inf,
                                          0,
                                          0),
         const.groupLargeCollidableStructure: ('ui_38_16_131', 1, 0.0, 250000.0, 0, 0),
         const.groupDeadspaceOverseersStructure: ('ui_38_16_131', 1, 0.0, 250000.0, 0, 0),
         const.groupControlTower: ('ui_38_16_132',
                                   1,
                                   0.0,
                                   inf,
                                   0,
                                   0),
         const.groupMoonMining: ('ui_38_16_133',
                                 1,
                                 0.0,
                                 inf,
                                 0,
                                 0),
         const.groupMobileShieldGenerator: ('ui_38_16_134',
                                            1,
                                            0.0,
                                            inf,
                                            0,
                                            0),
         const.groupAssemblyArray: ('ui_38_16_135',
                                    1,
                                    0.0,
                                    inf,
                                    0,
                                    0),
         const.groupMobileLaboratory: ('ui_38_16_135',
                                       1,
                                       0.0,
                                       inf,
                                       0,
                                       0),
         const.groupCorporateHangarArray: ('ui_38_16_136',
                                           1,
                                           0.0,
                                           inf,
                                           0,
                                           0),
         const.groupMobileReactor: ('ui_38_16_137',
                                    1,
                                    0.0,
                                    inf,
                                    0,
                                    0),
         const.groupRefiningArray: ('ui_38_16_137',
                                    1,
                                    0.0,
                                    inf,
                                    0,
                                    0),
         const.groupMobileMissileSentry: ('ui_38_16_138',
                                          1,
                                          0.0,
                                          inf,
                                          0,
                                          0),
         const.groupMobileHybridSentry: ('ui_38_16_13',
                                         1,
                                         0.0,
                                         inf,
                                         0,
                                         0),
         const.groupMobileLaserSentry: ('ui_38_16_13',
                                        1,
                                        0.0,
                                        inf,
                                        0,
                                        0),
         const.groupMobileProjectileSentry: ('ui_38_16_13',
                                             1,
                                             0.0,
                                             inf,
                                             0,
                                             0),
         const.groupEnergyNeutralizingBattery: ('ui_38_16_238',
                                                1,
                                                0.0,
                                                inf,
                                                0,
                                                0),
         const.groupCynosuralGeneratorArray: ('ui_38_16_237',
                                              1,
                                              0.0,
                                              inf,
                                              0,
                                              0),
         const.groupCynosuralSystemJammer: ('ui_38_16_239',
                                            1,
                                            0.0,
                                            inf,
                                            0,
                                            0),
         const.groupJumpPortalArray: ('ui_38_16_236',
                                      1,
                                      0.0,
                                      inf,
                                      0,
                                      0),
         const.groupScannerArray: ('ui_38_16_240',
                                   1,
                                   0.0,
                                   inf,
                                   0,
                                   0),
         const.groupMobilePowerCore: ('ui_38_16_139',
                                      1,
                                      0.0,
                                      inf,
                                      0,
                                      0),
         const.groupMobileStorage: ('ui_38_16_148',
                                    1,
                                    0.0,
                                    inf,
                                    0,
                                    0),
         const.groupElectronicWarfareBattery: ('ui_38_16_149',
                                               1,
                                               0.0,
                                               inf,
                                               0,
                                               0),
         const.groupSensorDampeningBattery: ('ui_38_16_149',
                                             1,
                                             0.0,
                                             inf,
                                             0,
                                             0),
         const.groupStasisWebificationBattery: ('ui_38_16_149',
                                                1,
                                                0.0,
                                                inf,
                                                0,
                                                0),
         const.groupWarpScramblingBattery: ('ui_38_16_149',
                                            1,
                                            0.0,
                                            inf,
                                            0,
                                            0),
         const.groupWarpScramblingBattery: ('ui_38_16_149',
                                            1,
                                            0.0,
                                            inf,
                                            0,
                                            0),
         const.groupShieldHardeningArray: ('ui_38_16_149',
                                           1,
                                           0.0,
                                           inf,
                                           0,
                                           0),
         const.groupTrackingArray: ('ui_38_16_149',
                                    1,
                                    0.0,
                                    inf,
                                    0,
                                    0),
         const.groupStealthEmitterArray: ('ui_38_16_149',
                                          1,
                                          0.0,
                                          inf,
                                          0,
                                          0),
         const.groupAgentsinSpace: ('ui_38_16_37',
                                    1,
                                    0.0,
                                    inf,
                                    0,
                                    0),
         const.groupDestructibleAgentsInSpace: ('ui_38_16_37',
                                                1,
                                                0.0,
                                                inf,
                                                0,
                                                0),
         const.groupHarvestableCloud: ('ui_38_16_241',
                                       1,
                                       50000.0,
                                       inf,
                                       -20,
                                       0),
         const.groupScannerProbe: ('ui_38_16_120',
                                   1,
                                   0.0,
                                   inf,
                                   -20,
                                   0),
         const.groupCapturePointTower: ('ui_38_16_130',
                                        1,
                                        0.0,
                                        inf,
                                        -20,
                                        0),
         const.groupControlBunker: ('ui_38_16_164',
                                    1,
                                    0.0,
                                    inf,
                                    0,
                                    0),
         const.groupWormhole: ('ui_38_16_235',
                               1,
                               0.0,
                               inf,
                               0,
                               0),
         const.groupPlanetaryCustomsOffices: ('ui_38_16_31',
                                              1,
                                              0.0,
                                              inf,
                                              0,
                                              0)}
        for group in cfg.invgroups:
            if group.fittableNonSingleton and not self.grp_mapping.has_key(group.groupID):
                self.grp_mapping[group.groupID] = self.grp_mapping[const.groupMissile]

        for bombGroup in [const.groupBomb, const.groupBombECM, const.groupBombEnergy]:
            self.grp_mapping[bombGroup] = self.grp_mapping[const.groupBomb]

        self.type_mapping = {const.typeBeacon: ('ui_38_16_14',
                            1,
                            150000.0,
                            inf,
                            0,
                            0),
         const.typeCelestialBeaconII: ('ui_38_16_30',
                                       1,
                                       150000.0,
                                       inf,
                                       0,
                                       0),
         const.typeCelestialAgentSiteBeacon: ('ui_38_16_46',
                                              1,
                                              150000.0,
                                              inf,
                                              0,
                                              0),
         const.typeThePrizeContainer: ('ui_38_16_12',
                                       1,
                                       0.0,
                                       inf,
                                       0,
                                       0)}



    def ShowAll(self):
        if self.showState != SHOW_ALL:
            self.showState = SHOW_ALL
            bp = sm.StartService('michelle').GetBallpark(doWait=True)
            if bp is None:
                return 
            lst = []
            for (ballID, ball,) in bp.balls.iteritems():
                if ballID < 0 or ballID in self.brackets.keys():
                    continue
                slimItem = bp.GetInvItem(ballID)
                if slimItem:
                    lst.append((ball, slimItem))

            self.DoBallsAdded(lst, useFilter=False)
        self.UpdateOverviewSettings()



    def UpdateOverviewSettings(self):
        overview = sm.StartService('tactical').GetPanelForUpdate('overview')
        if overview:
            selectedTabKey = overview.GetSelectedTabKey()
            tabsettings = settings.user.overview.Get('tabsettings', {})
            tabsetting = tabsettings.get(selectedTabKey, None)
            if tabsetting:
                tabsetting['showAll'] = self.showState == SHOW_ALL
                tabsetting['showNone'] = self.showState == SHOW_NONE



    def ShowNone(self):
        if self.showState != SHOW_NONE:
            self.showState = SHOW_NONE
            bp = sm.StartService('michelle').GetBallpark(doWait=True)
            if bp is None:
                return 
            lst = []
            for (ballID, ball,) in bp.balls.iteritems():
                if ballID is None:
                    log.LogTraceback('bracketMgr::ShowNone - ballID is None!!!')
                    continue
                if ballID < 0:
                    continue
                if not self.IsWanted(ballID):
                    lst.append(ballID)

            self.ClearBrackets(lst)
        self.UpdateOverviewSettings()



    def ShowAllHidden(self):
        if not self.showHiddenTimer:
            if self.brackets.has_key(session.shipid):
                self.brackets[session.shipid].ShowTempIcon()
            self.showHiddenTimer = base.AutoTimer(100, self.StopShowingHidden)



    def ToggleShowSpecials(self):
        if not getattr(self, 'showingSpecials', False):
            self.DoToggleShowSpecials(True)
        else:
            self.DoToggleShowSpecials(False)



    def DoToggleShowSpecials(self, isShow):
        if isShow:
            self.showingSpecials = True
            bp = sm.GetService('michelle').GetBallpark()
            lst = []
            if not bp:
                return 
            for (ballID, ball,) in bp.balls.iteritems():
                if ballID in self.brackets.keys():
                    continue
                slimItem = bp.GetInvItem(ballID)
                if slimItem and slimItem.groupID in self.specials:
                    lst.append((ball, slimItem))

            self.DoBallsAdded(lst)
        else:
            self.showingSpecials = False
            lst = []
            for (ballID, ball,) in self.brackets.iteritems():
                if getattr(ball, 'groupID', None) in self.specials and not self.IsSelectedOrTargeted(ballID):
                    lst.append(ballID)

            self.ClearBrackets(lst)
        overview = sm.StartService('tactical').GetPanelForUpdate('overview')
        if overview:
            selectedTabKey = overview.GetSelectedTabKey()
            tabsettings = settings.user.overview.Get('tabsettings', {})
            tabsetting = tabsettings.get(selectedTabKey, None)
            if tabsetting:
                tabsetting['showSpecials'] = self.showingSpecials



    def ShowingAll(self):
        return self.showState == SHOW_ALL



    def ShowingNone(self):
        return self.showState == SHOW_NONE



    def StopShowingAllNone(self):
        self.showState = SHOW_DEFAULT
        lst = []
        for (ballID, ball,) in self.brackets.iteritems():
            if not self.IsWanted(ballID) and ball:
                lst.append(ballID)

        self.ClearBrackets(lst)
        self.UpdateOverviewSettings()



    def StopShowingAll(self):
        self.showState = SHOW_DEFAULT
        lst = []
        for (ballID, ball,) in self.brackets.iteritems():
            if not self.IsWanted(ballID) and ball:
                lst.append(ballID)

        self.ClearBrackets(lst)
        self.UpdateOverviewSettings()



    def StopShowingNone(self):
        self.showState = SHOW_DEFAULT
        lst = []
        for (ballID, ball,) in self.brackets.iteritems():
            if not self.IsWanted(ballID) and ball:
                lst.append(ballID)

        self.ClearBrackets(lst)
        self.UpdateOverviewSettings()
        bp = sm.StartService('michelle').GetBallpark(doWait=True)
        if bp is None:
            return 
        lst = []
        for (ballID, ball,) in bp.balls.iteritems():
            if ballID < 0 or ballID in self.brackets.keys() or ball is None:
                continue
            if self.IsWanted(ballID):
                slimItem = bp.GetInvItem(ballID)
                if slimItem:
                    lst.append((ball, slimItem))

        self.DoBallsAdded(lst, useFilter=False)
        self.UpdateOverviewSettings()



    def StopShowingHidden(self):
        alt = uicore.uilib.Key(uiconst.VK_MENU)
        if not alt:
            self.showHiddenTimer = None
            if self.brackets.has_key(session.shipid):
                self.brackets[session.shipid].HideTempIcon()



    def ClearBrackets(self, lst):
        for ballID in lst:
            self.ClearBracket(ballID)




    def IsWanted(self, ballID, ignoreState = False):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(ballID)
        if slimItem is None:
            log.LogWarn('IsWanted - ball', ballID, 'not found in park')
            return False
        else:
            if slimItem.groupID in self.unwantedBracketGroups:
                return False
            filtered = sm.GetService('tactical').GetFilteredStatesFunctionNames(isBracket=True)
            wanted = False
            isSpecial = slimItem.groupID in self.specials
            if isSpecial and getattr(self, 'showingSpecials', False):
                return True
            if not isSpecial:
                if self.showState == SHOW_ALL:
                    return True
                if self.showState == SHOW_NONE and not self.IsSelectedOrTargeted(ballID):
                    return False
            if isSpecial:
                return self.IsSelectedOrTargeted(ballID) and not ignoreState
            return sm.StartService('tactical').WantIt(slimItem, filtered, isBracket=True) or self.IsSelectedOrTargeted(ballID) and not ignoreState



    def IsSelectedOrTargeted(self, ballID):
        stateMgr = sm.GetService('state')
        for isWanted in stateMgr.GetStates(ballID, [state.selected,
         state.targeted,
         state.targeting,
         state.activeTarget]):
            if isWanted:
                return True

        return sm.StartService('target').IsTarget(ballID)



    def GetBracketName(self, objectID):
        if objectID in self.brackets:
            return self.brackets[objectID].displayName
        return ''



    def GetBracketName2(self, objectID):
        ret = self.GetBracketName(objectID)
        if ret != '':
            return ret
        slimItem = sm.GetService('michelle').GetBallpark().slimItems.get(objectID, None)
        if not objectID:
            return ''
        return self.GetDisplayNameForBracket(slimItem)



    def SetBracketName(self, objectID, newName):
        if objectID in self.brackets:
            self.brackets[objectID].displayName = newName



    def DisplayName(self, slimItem, displayName):
        shiplabel = []
        if not getattr(self, 'shipLabels', None):
            self.shipLabels = sm.GetService('state').GetShipLabels()
            self.hideCorpTicker = sm.GetService('state').GetHideCorpTicker()
        for label in self.shipLabels:
            if label['state']:
                (type, pre, post,) = (label['type'], label['pre'], label['post'])
                if type is None and slimItem.corpID and not util.IsNPC(slimItem.corpID):
                    shiplabel.append(pre)
                if type == 'corporation' and slimItem.corpID and not util.IsNPC(slimItem.corpID) and not (self.hideCorpTicker and slimItem.allianceID):
                    shiplabel += [pre, cfg.corptickernames.Get(slimItem.corpID).tickerName, post]
                if type == 'alliance' and slimItem.allianceID:
                    try:
                        shiplabel += [pre, cfg.allianceshortnames.Get(slimItem.allianceID).shortName, post]
                    except:
                        log.LogError('Failed to get allianceName, itemID:', slimItem.itemID, 'allianceID:', slimItem.allianceID)
                if type == 'pilot name':
                    shiplabel += [pre, displayName, post]
                if type == 'ship type':
                    shiplabel += [pre, cfg.invtypes.Get(slimItem.typeID).name, post]
                if type == 'ship name':
                    name = cfg.evelocations.Get(slimItem.itemID).name
                    if name:
                        shiplabel += [pre, name, post]

        return ''.join(shiplabel)



    def OnSlimItemChange(self, oldSlim, newSlim):
        if util.IsStructure(newSlim.categoryID):
            if newSlim.posState == oldSlim.posState and newSlim.posTimestamp == oldSlim.posTimestamp and newSlim.incapacitated == oldSlim.incapacitated and newSlim.controllerID == oldSlim.controllerID and newSlim.ownerID == oldSlim.ownerID:
                return 
            bracket = self.brackets.get(newSlim.itemID, None)
            if bracket:
                bracket.slimItem = newSlim
                bracket.displayName = self.GetDisplayNameForBracket(newSlim)
                bracket.UpdateStructureState(newSlim)
        elif util.IsOrbital(newSlim.categoryID):
            if newSlim.orbitalState == oldSlim.orbitalState and newSlim.orbitalTimestamp == oldSlim.orbitalTimestamp and newSlim.ownerID == oldSlim.ownerID and newSlim.orbitalHackerID == oldSlim.orbitalHackerID and newSlim.orbitalHackerProgress == oldSlim.orbitalHackerProgress:
                return 
            bracket = self.brackets.get(newSlim.itemID, None)
            if bracket is not None:
                bracket.slimItem = newSlim
                bracket.displayName = self.GetDisplayNameForBracket(newSlim)
                bracket.UpdateOrbitalState(newSlim)
        elif newSlim.categoryID == const.categoryShip and newSlim.itemID in self.brackets:
            self.brackets[newSlim.itemID].slimItem = newSlim
            self.brackets[newSlim.itemID].displayName = self.GetDisplayNameForBracket(newSlim)
        elif newSlim.categoryID == const.categoryStation:
            bracket = self.brackets.get(newSlim.itemID, None)
            if bracket:
                bracket.slimItem = newSlim
                bracket.displayName = self.GetDisplayNameForBracket(newSlim)
                bracket.UpdateOutpostState(newSlim, oldSlim)
        elif newSlim.groupID in (const.groupPlanet, const.groupPlanetaryCustomsOffices) and newSlim.corpID != oldSlim.corpID:
            bracket = self.brackets.get(newSlim.itemID, None)
            if bracket:
                bracket.slimItem = newSlim
                bracket.displayName = self.GetDisplayNameForBracket(newSlim)
            if newSlim.groupID == const.groupPlanet:
                if newSlim.corpID is not None:
                    bracket.displaySubLabel = localization.GetByLabel('UI/DustLink/ControlledBy', corpName=cfg.eveowners.Get(newSlim.corpID).name)
                else:
                    bracket.displaySubLabel = ''
        elif newSlim.itemID in self.brackets:
            self.brackets[newSlim.itemID].slimItem = newSlim
        if newSlim.corpID != oldSlim.corpID:
            if newSlim.itemID in self.brackets:
                bracket = self.brackets[newSlim.itemID]
                uthread.pool('BracketMgr::OnSlimItemChange --> UpdateStates', sm.GetService('tactical').UpdateStates, newSlim, bracket)
        if newSlim.groupID == const.groupWreck and newSlim.isEmpty and not oldSlim.isEmpty:
            sm.GetService('state').SetState(newSlim.itemID, state.flagWreckEmpty, True)
        if newSlim.groupID in [const.groupWreck, const.groupCargoContainer]:
            self.RenewBracket(newSlim)



    def ProcessSessionChange(self, isremote, session, change):
        if not sm.GetService('connection').IsConnected() or session.stationid is not None or session.worldspaceid is not None or session.charid is None:
            self.CleanUp()
        elif not change.has_key('solarsystemid') and change.has_key('shipid') and change['shipid'][0] is not None:
            (oldShipID, shipID,) = change['shipid']
            bp = sm.GetService('michelle').GetBallpark()
            (ball, slimItem,) = (bp.GetBall(oldShipID), bp.GetInvItem(oldShipID))
            if ball is not None and slimItem is not None:
                self.DoBallsAdded([(ball, slimItem)])
            (ball, slimItem,) = (bp.GetBall(shipID), bp.GetInvItem(shipID))
            if ball is not None and slimItem is not None:
                self.DoBallsAdded([(ball, slimItem)])



    def GetBracketProps(self, slimItem, ball):
        if not self.gotProps:
            self.gotProps = 1
            self.SetupProps()
        if slimItem.groupID in self.npcSpecial and ball is not None:
            if ball.radius <= 85:
                size = 0
            elif 85 < ball.radius <= 240:
                size = 1
            else:
                size = 2
            return (self.npcSpecialIcons[size],
             1,
             0.0,
             1e+32,
             0,
             0)
        return self.GetMappedBracketProps(slimItem.categoryID, slimItem.groupID, slimItem.typeID)



    def GetMappedBracketProps(self, categoryID, groupID, typeID, default = None):
        if typeID in self.type_mapping:
            return self.type_mapping[typeID]
        if groupID in self.grp_mapping:
            return self.grp_mapping[groupID]
        if categoryID in self.cat_mapping:
            return self.cat_mapping[categoryID]
        if default is not None:
            return default
        return ('ui_38_16_241', 0, 0.0, 1e+32, 0, 1)



    def SlimItemIsDungeonObjectWithTriggers(self, slimItem):
        if self.scenarioMgr.editDungeonID:
            if '/jessica' in blue.pyos.GetArg():
                import dungeon
                objectID = slimItem.dunObjectID
                if objectID:
                    obj = dungeon.Object.Get(objectID)
                    if obj is not None:
                        return obj.HasAnyTriggers()



    def PrimeLocations(self, slimItem):
        locations = []
        for each in slimItem.jumps:
            if each.locationID not in locations:
                locations.append(each.locationID)
            if each.toCelestialID not in locations:
                locations.append(each.toCelestialID)

        if len(locations):
            cfg.evelocations.Prime(locations)



    def AddTempBracket(self, itemID):
        pass



    def DoBallsAdded(self, *args, **kw):
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::BracketMgr')
        try:
            uthread.new(self.DoBallsAdded_, *args, **kw).context = blue.pyos.taskletTimer.GetCurrent() + '::DoBallsAdded_'

        finally:
            t.PopTimer(timer)




    @bluepy.CCP_STATS_ZONE_METHOD
    def DoBallsAdded_(self, lst, useFilter = True, ignoreMoons = 0, ignoreAsteroids = 1):
        uthread.worker('BracketMgr::UpdateBracketsForDungeonEditing', self.UpdateBracketsForDungeonEditing, lst)
        if not hasattr(self, 'specialGroups'):
            self.specialGroups = (const.groupMoon, const.groupLargeCollidableStructure)
        if not self.gotProps:
            self.gotProps = 1
            self.SetupProps()
        wnd = uicore.layer.bracket
        ignoreGroup = [const.groupForceField, const.groupCloud]
        ignoreCateg = []
        if ignoreAsteroids:
            ignoreCateg += [const.categoryAsteroid]
            ignoreGroup += [const.groupHarvestableCloud]
        if ignoreMoons:
            ignoreGroup += [const.groupMoon]
        filterLCS = ['wall_x',
         'wall_z',
         ' wall',
         ' barricade',
         ' fence',
         ' barrier',
         ' junction',
         ' elevator',
         ' lookout',
         ' neon sign']
        currNumNPC = 1
        currNumAsteroidBelt = 1
        currNumAsteroid = 1
        currNumStations = 1
        bracketsToUpdateSubLabel = []
        for (ball, slimItem,) in lst:
            show = 1
            if slimItem.groupID == const.groupDeadspaceOverseersStructure:
                checkName = cfg.invtypes.Get(slimItem.typeID).name.lower()
                for each in filterLCS:
                    if each in checkName:
                        show = 0
                        break

            if not show or slimItem.groupID in ignoreGroup or slimItem.categoryID in ignoreCateg:
                continue
            if not self.IsWanted(ball.id):
                continue
            bracket = self.brackets.get(ball.id, None)
            if bracket:
                self.ClearBracket(ball.id, bracket)
            panel = self.GetNewBracket()
            if hasattr(slimItem, 'typeID') and slimItem.typeID == const.typeAsteroidBelt:
                panel.name = 'bracketAsteroidBelt%s' % currNumAsteroidBelt
                currNumAsteroidBelt += 1
            elif hasattr(slimItem, 'categoryID') and slimItem.categoryID == const.categoryAsteroid:
                panel.name = 'bracketAsteroid%s' % currNumAsteroid
                currNumAsteroid += 1
            elif hasattr(slimItem, 'categoryID') and slimItem.categoryID == const.categoryStation:
                panel.name = 'bracketStation%s' % currNumStations
                currNumStations += 1
            elif hasattr(slimItem, 'ownerID') and hasattr(slimItem, 'groupID'):
                if slimItem.ownerID == const.factionUnknown and slimItem.groupID == const.groupPirateDrone:
                    panel.name = 'bracketNPCPirateDrone%s' % currNumNPC
                    currNumNPC += 1
            panel.displayName = self.GetDisplayNameForBracket(slimItem)
            if panel.displayName is None:
                panel.Close()
                continue
            if slimItem.groupID == const.groupPlanet and slimItem.corpID:
                bracketsToUpdateSubLabel.append((panel, slimItem))
            self.SetupBracketProperties(panel, ball, slimItem)
            panel.updateItem = sm.GetService('state').CheckIfUpdateItem(slimItem) and ball.id != eve.session.shipid
            panel.Startup(slimItem, ball)
            self.brackets[ball.id] = panel
            if panel.updateItem:
                self.updateBrackets.append(ball.id)
            if hasattr(self, 'capturePoints') and ball.id in self.capturePoints.keys():
                self.brackets[ball.id].UpdateCaptureProgress(self.capturePoints[ball.id])
            if util.IsOrbital(slimItem.categoryID):
                self.brackets[ball.id].UpdateOrbitalState(slimItem)

        if len(bracketsToUpdateSubLabel) > 0:
            uthread.worker('BracketMgr::UpdateSubLabels', self.UpdateSubLabels, bracketsToUpdateSubLabel)



    def GetNewBracket(self):
        bracket = xtriui.Bracket(parent=uicore.layer.bracket, name='__inflightbracket', align=uiconst.NOALIGN, state=uiconst.UI_NORMAL)
        return bracket



    def GetDisplayNameForBracket(self, slimItem):
        try:
            displayName = uix.GetSlimItemName(slimItem)
        except:
            return None
        if slimItem.groupID in self.grp_mapping.iterkeys():
            if slimItem.groupID == const.groupStation:
                displayName = uix.EditStationName(displayName, usename=1)
            elif slimItem.groupID == const.groupStargate:
                uthread.new(self.PrimeLocations, slimItem)
            elif slimItem.groupID == const.groupHarvestableCloud:
                displayName = localization.GetByLabel('UI/Generic/HarvestableCloud', item=slimItem.typeID)
            elif slimItem.categoryID == const.categoryAsteroid:
                displayName = localization.GetByLabel('UI/Generic/Asteroid', item=slimItem.typeID)
        if not util.IsOrbital(slimItem.categoryID) and slimItem.corpID:
            displayName = self.DisplayName(slimItem, displayName)
        return displayName



    def UpdateBracketsForDungeonEditing(self, objectList):
        bracketWindow = uicore.layer.bracket
        for (ball, slimItem,) in objectList:
            if not self.SlimItemIsDungeonObjectWithTriggers(slimItem):
                continue
            bracket = self.brackets.get(ball.id, None)
            if bracket:
                self.ClearBracket(ball.id, bracket)
            bracket = self.GetNewBracket()
            bracket.name = 'bracketForTriggerObject%d' % slimItem.dunObjectID
            bracket.displayName = self.GetDisplayNameForBracket(slimItem) + ' (Trigger)'
            props = self.GetBracketProps(slimItem, ball)
            props = ('ui_38_16_139',) + props[1:]
            self.SetupBracketProperties(bracket, ball, slimItem, props)
            bracket.updateItem = False
            bracket.Startup(slimItem, ball)
            self.brackets[ball.id] = bracket




    def SetupBracketProperties(self, bracket, ball, slimItem, props = None):
        if props is None:
            props = self.GetBracketProps(slimItem, ball)
        (_iconNo, _dockType, _minDist, _maxDist, _iconOffset, _logflag,) = props
        tracker = bracket.projectBracket
        tracker.trackBall = ball
        tracker.name = unicode(cfg.evelocations.Get(ball.id).locationName)
        tracker.parent = uicore.layer.inflight.GetRenderObject()
        tracker.dock = _dockType
        tracker.marginRight = tracker.marginLeft + bracket.width
        tracker.marginBottom = tracker.marginTop + bracket.height
        bracket.data = props
        bracket.invisible = ball.id == eve.session.shipid
        bracket.dock = _dockType
        bracket.minDispRange = _minDist
        bracket.maxDispRange = _maxDist
        bracket.inflight = True
        bracket.ball = ball



    def UpdateLabels(self):
        self.shipLabels = sm.GetService('state').GetShipLabels()
        self.hideCorpTicker = sm.GetService('state').GetHideCorpTicker()
        for bracket in self.brackets:
            slimItem = self.brackets[bracket].slimItem
            if slimItem.corpID:
                self.brackets[slimItem.itemID].displayName = self.GetDisplayNameForBracket(slimItem)
            if slimItem.groupID == const.groupPlanet and slimItem.corpID:
                self.brackets[slimItem.itemID].displaySubLabel = localization.GetByLabel('UI/DustLink/ControlledBy', corpName=cfg.eveowners.Get(slimItem.corpID).name)




    def UpdateSubLabels(self, updates):
        for (bracket, slimItem,) in updates:
            bracket.displaySubLabel = localization.GetByLabel('UI/DustLink/ControlledBy', corpName=cfg.eveowners.Get(slimItem.corpID).name)




    def RenewFlags(self):
        uthread.pool('BracketMgr::RenewFlags', self._RenewFlags)



    def _RenewFlags(self):
        for itemID in self.updateBrackets:
            (slimItem, bracket,) = self.GetSlimItem(itemID)
            if bracket is None:
                continue
            if slimItem:
                bracket.Load_update(slimItem)
            blue.pyos.BeNice()




    def RenewSingleFlag(self, charID):
        uthread.new(self._RenewSingleFlag, charID)



    def _RenewSingleFlag(self, charID):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return 
        for itemID in self.updateBrackets:
            (slimItem, bracket,) = self.GetSlimItem(itemID)
            if slimItem is None:
                continue
            slimCharID = getattr(slimItem, 'charID', None)
            if slimCharID is None:
                continue
            if slimCharID == charID:
                bracket.Load_update(slimItem)
                return 
            blue.pyos.BeNice()




    def GetSlimItem(self, itemID):
        bracket = self.GetBracket(itemID)
        if not bracket:
            if itemID in self.updateBrackets:
                self.updateBrackets.remove(itemID)
            return (None, None)
        slimItem = bracket.slimItem
        return (slimItem, bracket)



    def RenewBracket(self, slimItem):
        if slimItem is None:
            return 
        bracket = self.GetBracket(slimItem.itemID)
        if bracket is not None:
            bracket.Load_update(slimItem)



    def OnBallparkCall(self, funcName, args):
        if funcName == 'SetBallFree':
            (itemID, isFree,) = args
            bracket = self.GetBracket(itemID)
            if bracket:
                slimItem = bracket.slimItem
                if slimItem:
                    bracket.SetBracketAnchoredState(slimItem)



    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return 
        self.LogInfo('DoBallRemove::bracketMgr', ball.id)
        self.ClearBracket(ball.id)
        if ball.id in getattr(self, 'capturePoints', {}).keys():
            del self.capturePoints[ball.id]



    def DoBallClear(self, solitem):
        if not self.brackets:
            return 
        self.brackets = {}
        self.updateBrackets = []
        for bracket in uicore.layer.bracket.children:
            bracket.Close()




    def OnDestinationSet(self, destinationID = None):
        sg = const.groupStargate
        destinationPath = sm.GetService('starmap').GetDestinationPath()
        for each in uicore.layer.bracket.children[:]:
            if not getattr(each, 'IsBracket', 0):
                continue
            if each is None or each.destroyed or not getattr(each, 'IsBracket', None) or not each.slimItem or each.groupID != sg:
                continue
            if each.sr.icon:
                slimItem = getattr(each, 'slimItem', None)
                each.sr.icon.color.SetRGB(1.0, 1.0, 1.0)
                if slimItem.jumps[0].locationID in destinationPath:
                    each.sr.icon.color.SetRGB(1.0, 1.0, 0.0)
                    uiutil.SetOrder(each, 0)




    def OnStateChange(self, itemID, flag, true, *args):
        if flag in (state.selected, state.targeted, state.targeting):
            slimItem = uix.GetBallparkRecord(itemID)
            if slimItem and (self.showState == SHOW_NONE or slimItem.categoryID == const.categoryAsteroid or slimItem.groupID == const.groupHarvestableCloud or not self.IsWanted(slimItem.itemID, ignoreState=True)):
                bracket = self.GetBracket(itemID)
                if true and not bracket:
                    ball = sm.GetService('michelle').GetBall(slimItem.itemID)
                    if ball:
                        self.DoBallsAdded([(ball, slimItem)], useFilter=False, ignoreAsteroids=0)
                elif not true and bracket and not sm.GetService('target').IsTarget(itemID):
                    self.ClearBracket(slimItem.itemID, bracket)
                    if self.SlimItemIsDungeonObjectWithTriggers(slimItem):
                        ball = sm.GetService('michelle').GetBall(slimItem.itemID)
                        self.UpdateBracketsForDungeonEditing([(ball, slimItem)])
                    return 
        bracket = self.GetBracket(itemID)
        if bracket:
            bracket.OnStateChange(itemID, flag, true, *args)



    def OnAttribute(self, attributeName, item, newValue):
        if item.itemID == session.shipid and attributeName == 'scanResolution':
            for targetID in sm.GetService('target').GetTargeting():
                bracket = self.GetBracket(targetID)
                if bracket and hasattr(bracket, 'OnAttribute'):
                    bracket.OnAttribute(attributeName, item, newValue)




    def OnAttributes(self, changeList):
        for t in changeList:
            self.OnAttribute(*t)




    def OnPostCfgDataChanged(self, what, data):
        if what == 'evelocations':
            bracket = self.GetBracket(data[0])
            if bracket is not None and getattr(bracket, 'slimItem', None):
                bracket.displayName = self.GetDisplayNameForBracket(bracket.slimItem)



    def OnCaptureChanged(self, ballID, captureID, lastIncident, points, captureTime, lastCapturing):
        bracket = self.GetBracket(ballID)
        if not hasattr(self, 'capturePoints'):
            self.capturePoints = {}
        self.capturePoints[ballID] = {'captureID': captureID,
         'lastIncident': blue.os.GetSimTime(),
         'points': points,
         'captureTime': captureTime,
         'lastCapturing': lastCapturing}
        if bracket:
            bracket.UpdateCaptureProgress(self.capturePoints[ballID])



    def ResetOverlaps(self):
        for each in self.overlaps:
            if not getattr(each, 'IsBracket', 0):
                continue
            projectBracket = each.projectBracket
            if projectBracket:
                projectBracket.bracket = each.GetRenderObject()
                each.KillLabel()
                each.opacity = getattr(each, '_pervious_opacity', 1.0)
                each.SetAlign(uiconst.NOALIGN)

        for each in self.overlapsHidden:
            bubble = each.sr.bubble
            if bubble:
                bubble.state = uiconst.UI_PICKCHILDREN

        self.overlaps = []
        self.overlapsHidden = []



    def GetOverlapOverlap(self, sameX, minY, maxY):
        overlaps = []
        stillLeft = []
        for bracket in sameX:
            if bracket.absoluteTop > minY - 16 and bracket.absoluteBottom < maxY + 16:
                overlaps.append((bracket.displayName.lower(), bracket))
            else:
                stillLeft.append(bracket)

        return (overlaps, stillLeft)



    def CheckingOverlaps(self):
        return self.checkingOverlaps



    @bluepy.CCP_STATS_ZONE_METHOD
    def CheckOverlaps(self, sender, hideRest = 0):
        self.checkingOverlaps = sender.itemID
        self.ResetOverlaps()
        overlaps = []
        excludedC = (const.categoryAsteroid,)
        excludedG = (const.groupHarvestableCloud,)
        sameX = []
        LEFT = 0
        TOP = 1
        WIDTH = 2
        HEIGHT = 3
        BOTTOM = 4
        RIGHT = 5

        @util.Memoized
        def GetAbsolute(bracket):
            ro = bracket.GetRenderObject()
            (x, y,) = (uicore.ReverseScaleDpi(ro.translation[0]), uicore.ReverseScaleDpi(ro.translation[1]))
            centerX = x + bracket.width / 2
            centerY = y + bracket.height / 2
            return (centerX - 8,
             centerY - 8,
             16,
             16,
             centerY + 8,
             centerX + 8)


        s = GetAbsolute(sender)
        for bracket in sender.parent.children:
            if not getattr(bracket, 'IsBracket', 0) or not bracket.display or bracket.invisible and bracket.sr.tempIcon is None or bracket.categoryID in excludedC or bracket.groupID in excludedG or bracket == sender:
                continue
            b = GetAbsolute(bracket)
            overlapx = not (b[RIGHT] <= s[LEFT] or b[LEFT] >= s[RIGHT])
            overlapy = not (b[BOTTOM] <= s[TOP] or b[TOP] >= s[BOTTOM])
            if overlapx and overlapy:
                overlaps.append((bracket.displayName.lower(), bracket))
            elif overlapx and not overlapy:
                sameX.append(bracket)

        if not overlaps:
            self.checkingOverlaps = None
            sender.parent.state = uiconst.UI_PICKCHILDREN
            return 

        def GroupHeight(group):
            return sum([ GetAbsolute(b)[HEIGHT] for (name, b,) in group ])


        totalH = GroupHeight(overlaps)
        minY = sender.absoluteTop - totalH
        if sameX:
            for i in xrange(10):
                minY = sender.absoluteTop - totalH
                maxY = s[BOTTOM]
                (oo, sameX,) = self.GetOverlapOverlap(sameX, minY, maxY)
                if not oo:
                    break
                overlaps.extend(oo)
                totalH += GroupHeight(oo)

        overlaps = uiutil.SortListOfTuples(overlaps, reverse=True)

        def Nail(bracket, top):
            projectBracket = bracket.projectBracket
            if projectBracket:
                projectBracket.bracket = None
            bracket.SetAlign(uiconst.TOPLEFT)
            bracket.left = s[LEFT] + s[WIDTH] / 2 - bracket.width / 2
            bracket.top = top - (bracket.height - 16) / 2
            bracket._pervious_opacity = bracket.opacity
            bracket.opacity = 1.0
            if not bracket.sr.bubble:
                bracket.ShowLabel()
            uiutil.SetOrder(bracket, 0)


        top = s[TOP]
        Nail(sender, top)
        if sender.sr.hitchhiker:
            (lh, th, wh, hh,) = sender.sr.hitchhiker.GetAbsolute()
            top -= hh
        hasBubble = bool(sender.sr.bubble)
        if hasBubble:
            if sender.sr.bubble.data[1] in (0, 1, 2):
                top -= sender.sr.bubble.height + 8
        for bracket in overlaps:
            if top < 0:
                break
            shift = GetAbsolute(bracket)[HEIGHT]
            shift += 2
            hasBubble = bool(bracket.sr.bubble)
            if hasBubble:
                if bracket.sr.bubble.data[1] in (3, 4, 5):
                    shift += bracket.sr.bubble.height + 8
            top -= shift
            Nail(bracket, top)
            if bracket.sr.hitchhiker:
                (lh, th, wh, hh,) = bracket.sr.hitchhiker.GetAbsolute()
                top -= hh
            if hasBubble:
                if bracket.sr.bubble.data[1] in (0, 1, 2):
                    top -= bracket.sr.bubble.height + 8

        self.overlapsHidden = []
        if hideRest:
            for bracket in sender.parent.children:
                if bracket is sender or bracket in overlaps or not getattr(bracket, 'IsBracket', 0) or bracket.state != uiconst.UI_PICKCHILDREN or bracket.invisible and bracket.sr.tempIcon is None:
                    continue
                bubble = bracket.sr.bubble
                if bubble:
                    bubble.state = uiconst.UI_HIDDEN
                    self.overlapsHidden.append(bracket)

        self.overlaps = [sender] + overlaps
        sender.parent.state = uiconst.UI_PICKCHILDREN
        self.checkingOverlaps = None



    def GetBracket(self, bracketID):
        if getattr(self, 'brackets', None) is not None:
            return self.brackets.get(bracketID, None)



    def ClearBracket(self, id, bracket = None):
        if getattr(self, 'brackets'):
            bracket = bracket or self.GetBracket(id)
            if id in self.brackets:
                del self.brackets[id]
            if id in self.updateBrackets:
                self.updateBrackets.remove(id)
        if bracket is not None and not bracket.destroyed:
            bracket.Close()



    def GetScanSpeed(self, source = None, target = None):
        if source is None:
            source = eve.session.shipid
        if not source:
            return 
        scanAttributeChangeFlag = False
        myitem = sm.GetService('godma').GetItem(source)
        scanSpeed = None
        if myitem.scanResolution and target:
            slimItem = target
            targetitem = sm.GetService('godma').GetType(slimItem.typeID)
            if targetitem.AttributeExists('signatureRadius'):
                radius = targetitem.signatureRadius
            else:
                radius = 0
            if radius <= 0.0:
                bp = sm.GetService('michelle').GetBallpark()
                radius = bp.GetBall(slimItem.itemID).radius
                if radius <= 0.0:
                    radius = cfg.invtypes.Get(targetitem.typeID).radius
                    if radius <= 0.0:
                        radius = 1.0
            scanSpeed = 40000000.0 / myitem.scanResolution / math.log(radius + math.sqrt(radius * radius + 1)) ** 2.0
        if scanSpeed is None:
            scanSpeed = 2000
            log.LogWarn('GetScanSpeed returned the defauly scanspeed of %s ms ... missing scanResolution?' % scanSpeed)
        return min(scanSpeed, 180000)



    def GetCaptureData(self, ballID):
        if hasattr(self, 'capturePoints'):
            return self.capturePoints.get(ballID, None)



    def OnBSDTablesChanged(self, tableDataUpdated):
        if 'dungeon.triggers' in tableDataUpdated.iterkeys():
            if '/jessica' in blue.pyos.GetArg():
                bp = self.michelle.GetBallpark()
                objectList = []
                for slimItem in self.scenarioMgr.GetDunObjects():
                    ball = bp.GetBall(slimItem.itemID)
                    if ball:
                        objectList.append((ball, slimItem))

                self.DoBallsAdded(objectList, ignoreAsteroids=0)



    def ProcessShipEffect(self, godmaStm, effectState):
        (moduleID, characterID, shipID, targetID, otherID, areaIDs, effectID,) = effectState.environment
        if effectID == const.effectHackOrbital:
            (slimItem, bracket,) = self.GetSlimItem(targetID)
            if bracket:
                if effectState.active:
                    progress = sm.GetService('planetInfo').GetMyHackProgress(targetID)
                    bracket.BeginHacking()
                    bracket.UpdateHackProgress(progress)
                    if slimItem:
                        bracket.UpdateOrbitalState(slimItem)
                else:
                    progress = sm.GetService('planetInfo').GetMyHackProgress(targetID)
                    bracket.StopHacking(success=progress is not None and progress >= 1.0)




