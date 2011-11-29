import service
import state
import uix
import xtriui
import base
import log
import dbg
import functools
import util
import sys
import localization

def IsStandingRelevant(action):

    @functools.wraps(action)
    def wrapper(stateSvc, slimItem):
        if slimItem.ownerID in [None, const.ownerSystem]:
            return 0
        if util.IsNPC(slimItem.ownerID):
            return 0
        return action(stateSvc, slimItem)


    return wrapper



class StateSvc(service.Service):
    __guid__ = 'svc.state'
    __exportedcalls__ = {'GetExclState': [],
     'GetStates': [],
     'SetState': [],
     'RemoveWarOwners': []}
    __notifyevents__ = ['DoBallClear', 'DoBallRemove', 'OnSessionChanged']
    __update_on_reload__ = 0
    __startupdependencies__ = ['settings']

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.logme = 0
        self.exclusive = [state.mouseOver,
         state.selected,
         state.activeTarget,
         state.lookingAt]
        self.exclusives = {}
        self.states = {}
        self.stateColors = {}
        self.stateBlinks = {}
        self.atWar = {}
        self.stateColorsInited = 0
        self.props = None
        self.smartFilterProps = None
        self.defaultBackgroundOrder = [state.flagAtWarCanFight,
         state.flagAtWarMilitia,
         state.flagSameFleet,
         state.flagCriminal,
         state.flagSameCorp,
         state.flagSameAlliance,
         state.flagDangerous,
         state.flagSameMilitia,
         state.flagStandingHigh,
         state.flagStandingGood,
         state.flagStandingHorrible,
         state.flagStandingBad,
         state.flagIsWanted,
         state.flagAgentInteractable,
         state.flagStandingNeutral,
         state.flagNoStanding]
        self.defaultBackgroundStates = [state.flagCriminal,
         state.flagDangerous,
         state.flagSameFleet,
         state.flagSameCorp,
         state.flagSameAlliance,
         state.flagAtWarCanFight,
         state.flagAtWarMilitia,
         state.flagSameMilitia]
        self.defaultFlagOrder = [state.flagAtWarCanFight,
         state.flagAtWarMilitia,
         state.flagSameFleet,
         state.flagCriminal,
         state.flagSameCorp,
         state.flagSameAlliance,
         state.flagDangerous,
         state.flagSameMilitia,
         state.flagStandingHigh,
         state.flagStandingGood,
         state.flagStandingHorrible,
         state.flagStandingBad,
         state.flagIsWanted,
         state.flagAgentInteractable,
         state.flagStandingNeutral,
         state.flagNoStanding]
        self.defaultFlagStates = [state.flagSameFleet,
         state.flagSameCorp,
         state.flagSameAlliance,
         state.flagAtWarCanFight,
         state.flagSameMilitia,
         state.flagAtWarMilitia,
         state.flagStandingHigh,
         state.flagStandingGood,
         state.flagStandingBad,
         state.flagStandingHorrible,
         state.flagCriminal,
         state.flagDangerous,
         state.flagAgentInteractable,
         state.flagStandingNeutral]
        self.defaultBlinkStates = {('background', state.flagAtWarCanFight): 1,
         ('background', state.flagAtWarMilitia): 1}
        self.ewarStates = {'warpScrambler': (state.flagWarpScrambled, const.iconModuleWarpScrambler),
         'webify': (state.flagWebified, const.iconModuleStasisWeb),
         'electronic': (state.flagECMd, const.iconModuleECM),
         'ewRemoteSensorDamp': (state.flagSensorDampened, const.iconModuleSensorDamper),
         'ewTrackingDisrupt': (state.flagTrackingDisrupted, const.iconModuleTrackingDisruptor),
         'ewTargetPaint': (state.flagTargetPainted, const.iconModuleTargetPainter),
         'ewEnergyVampire': (state.flagEnergyLeeched, const.iconModuleNosferatu),
         'ewEnergyNeut': (state.flagEnergyNeut, const.iconModuleEnergyNeutralizer)}
        self.shouldLogError = True
        self.InitFilter()



    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' in change or 'allianceid' in change:
            self.atWar = {}



    def RemoveWarOwners(self, declaredByID, againstID):
        if not self.atWar:
            return 
        if declaredByID in self.atWar:
            del self.atWar[declaredByID]
        if againstID in self.atWar:
            del self.atWar[againstID]



    def GetProps(self):
        if self.props is None:
            outlawLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/Outlaw'), localization.GetByLabel('UI/Services/State/Standing/OutlawHint'))
            dangerousLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/Dangerous'), localization.GetByLabel('UI/Services/State/Standing/DangerousHint'))
            sameFleetLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/SameFleet'), localization.GetByLabel('UI/Services/State/Standing/SameFleetHint'))
            sameCorpLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/SameCorporation'), localization.GetByLabel('UI/Services/State/Standing/SameCorporationHint'))
            sameAllianceLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/SameAlliance'), localization.GetByLabel('UI/Services/State/Standing/SameAllianceHint'))
            sameMilitiaLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/SameMilitia'), localization.GetByLabel('UI/Services/State/Standing/SameMilitiaHint'))
            atWarWithCorpLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/AtWarWithCorporationOrAlliance'), localization.GetByLabel('UI/Services/State/Standing/AtWarWithCorporationOrAllianceHint'))
            atWarWithMilitiaLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/AtWarWithMilitia'), localization.GetByLabel('UI/Services/State/Standing/AtWarWithMilitiaHint'))
            excellentLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/Excellent'), localization.GetByLabel('UI/Services/State/Standing/ExcellentHint'))
            goodLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/Good'), localization.GetByLabel('UI/Services/State/Standing/GoodHint'))
            neutralLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/Neutral'), localization.GetByLabel('UI/Services/State/Standing/NeutralHint'))
            badLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/Bad'), localization.GetByLabel('UI/Services/State/Standing/BadHint'))
            terribleLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/Terrible'), localization.GetByLabel('UI/Services/State/Standing/TerribleHint'))
            isWantedLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/IsWanted'), localization.GetByLabel('UI/Services/State/Standing/IsWantedHint'))
            agnetInteractableLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/AgentIsInteractable'), localization.GetByLabel('UI/Services/State/Standing/AgentIsInteractableHint'))
            wreckIsViewedLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/WreckIsViewed'), localization.GetByLabel('UI/Services/State/Standing/WreckIsViewedHint'))
            wreckIsEmptyLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/WreckIsEmpty'), localization.GetByLabel('UI/Services/State/Standing/WreckIsEmptyHint'))
            noStandingLabelAndHint = (localization.GetByLabel('UI/Services/State/Standing/NoStanding'), localization.GetByLabel('UI/Services/State/Standing/NoStandingHint'))
            self.props = {state.flagCriminal: (outlawLabelAndHint[0],
                                  'Criminal',
                                  'red',
                                  outlawLabelAndHint[1],
                                  5),
             state.flagDangerous: (dangerousLabelAndHint[0],
                                   'Dangerous',
                                   'yellow',
                                   dangerousLabelAndHint[1],
                                   5),
             state.flagSameFleet: (sameFleetLabelAndHint[0],
                                   'SameFleet',
                                   'purple',
                                   sameFleetLabelAndHint[1],
                                   0),
             state.flagSameCorp: (sameCorpLabelAndHint[0],
                                  'SameCorp',
                                  'green',
                                  sameCorpLabelAndHint[1],
                                  1),
             state.flagSameAlliance: (sameAllianceLabelAndHint[0],
                                      'SameAlliance',
                                      'darkBlue',
                                      sameAllianceLabelAndHint[1],
                                      1),
             state.flagSameMilitia: (sameMilitiaLabelAndHint[0],
                                     'SameMilitia',
                                     'indigo',
                                     sameMilitiaLabelAndHint[1],
                                     1),
             state.flagAtWarCanFight: (atWarWithCorpLabelAndHint[0],
                                       'AtWarCanFight',
                                       'red',
                                       atWarWithCorpLabelAndHint[1],
                                       1),
             state.flagAtWarMilitia: (atWarWithMilitiaLabelAndHint[0],
                                      'AtWarMilitia',
                                      'orange',
                                      atWarWithMilitiaLabelAndHint[1],
                                      1),
             state.flagStandingHigh: (excellentLabelAndHint[0],
                                      'StandingHigh',
                                      'darkBlue',
                                      excellentLabelAndHint[1],
                                      2),
             state.flagStandingGood: (goodLabelAndHint[0],
                                      'StandingGood',
                                      'blue',
                                      goodLabelAndHint[1],
                                      2),
             state.flagStandingNeutral: (neutralLabelAndHint[0],
                                         'StandingNeutral',
                                         'white',
                                         neutralLabelAndHint[1],
                                         4),
             state.flagStandingBad: (badLabelAndHint[0],
                                     'StandingBad',
                                     'orange',
                                     badLabelAndHint[1],
                                     3),
             state.flagStandingHorrible: (terribleLabelAndHint[0],
                                          'StandingHorrible',
                                          'red',
                                          terribleLabelAndHint[1],
                                          3),
             state.flagIsWanted: (isWantedLabelAndHint[0],
                                  'IsWanted',
                                  'black',
                                  isWantedLabelAndHint[1],
                                  5),
             state.flagAgentInteractable: (agnetInteractableLabelAndHint[0],
                                           'AgentInteractable',
                                           'blue',
                                           agnetInteractableLabelAndHint[1],
                                           6),
             state.flagWreckAlreadyOpened: (wreckIsViewedLabelAndHint[0],
                                            'WreckViewed',
                                            'white',
                                            wreckIsViewedLabelAndHint[1],
                                            1),
             state.flagWreckEmpty: (wreckIsEmptyLabelAndHint[0],
                                    'WreckEmpty',
                                    'white',
                                    wreckIsEmptyLabelAndHint[1],
                                    1),
             state.flagNoStanding: (noStandingLabelAndHint[0],
                                    'NoStanding',
                                    'white',
                                    noStandingLabelAndHint[1],
                                    4)}
        return self.props



    def GetSmartFilterProps(self):
        if self.smartFilterProps is None:
            self.smartFilterProps = {state.flagWarpScrambled: (localization.GetByLabel('UI/Services/State/InflightState/WarpScrambling'),
                                       '',
                                       '',
                                       localization.GetByLabel('UI/Services/State/InflightState/WarpScramblingHint'),
                                       0),
             state.flagWebified: (localization.GetByLabel('UI/Services/State/InflightState/Webified'),
                                  '',
                                  '',
                                  localization.GetByLabel('UI/Services/State/InflightState/WebifiedHint'),
                                  0),
             state.flagECMd: (localization.GetByLabel('UI/Services/State/InflightState/Jamming'),
                              '',
                              '',
                              localization.GetByLabel('UI/Services/State/InflightState/JammingHint'),
                              0),
             state.flagSensorDampened: (localization.GetByLabel('UI/Services/State/InflightState/SensorDamping'),
                                        '',
                                        '',
                                        localization.GetByLabel('UI/Services/State/InflightState/SensorDampingHint'),
                                        0),
             state.flagTrackingDisrupted: (localization.GetByLabel('UI/Services/State/InflightState/TrackingDisrupting'),
                                           '',
                                           '',
                                           localization.GetByLabel('UI/Services/State/InflightState/TrackingDisruptingHint'),
                                           0),
             state.flagTargetPainted: (localization.GetByLabel('UI/Services/State/InflightState/Painting'),
                                       '',
                                       '',
                                       localization.GetByLabel('UI/Services/State/InflightState/PaintingHint'),
                                       0),
             state.flagEnergyLeeched: (localization.GetByLabel('UI/Services/State/InflightState/EnergyLeeched'),
                                       '',
                                       '',
                                       localization.GetByLabel('UI/Services/State/InflightState/EnergyLeechedHint'),
                                       0),
             state.flagEnergyNeut: (localization.GetByLabel('UI/Services/State/InflightState/EnergyNeutralizing'),
                                    '',
                                    '',
                                    localization.GetByLabel('UI/Services/State/InflightState/EnergyNeutralizingHint'),
                                    0)}
        return self.smartFilterProps



    def GetStateProps(self, st = None):
        props = self.GetProps()
        if st:
            if st in props:
                return props[st]
            else:
                if self.shouldLogError:
                    log.LogTraceback('Bad state flag: %s' % st)
                    self.shouldLogError = False
                return ('', '', 'white', '', 6)
        else:
            return props



    def GetActiveStateOrder(self, where):
        return [ flag for flag in self.GetStateOrder(where) if self.GetStateState(where, flag) ]



    def GetActiveStateOrderFunctionNames(self, where):
        return [ self.GetStateProps(flag)[1] for flag in self.GetActiveStateOrder(where) ]



    def GetStateOrder(self, where):
        default = getattr(self, 'default' + where.capitalize() + 'Order', [])
        ret = settings.user.overview.Get(where.lower() + 'Order', default)
        if ret is None:
            return default
        return ret



    def GetStateState(self, where, flag):
        return flag in self.GetStateStates(where)



    def GetStateStates(self, where):
        default = getattr(self, 'default' + where.capitalize() + 'States', [])
        ret = settings.user.overview.Get(where.lower() + 'States', default)
        if ret is None:
            return default
        return ret



    def GetStateColors(self):
        return {'purple': ((0.6, 0.15, 0.9, 1.0), 'UI/Common/Colors/Purple'),
         'green': ((0.1, 0.6, 0.1, 1.0), 'UI/Common/Colors/Green'),
         'red': ((0.75, 0.0, 0.0, 1.0), 'UI/Common/Colors/Red'),
         'darkBlue': ((0.0, 0.15, 0.6, 1.0), 'UI/Common/Colors/DarkBlue'),
         'blue': ((0.2, 0.5, 1.0, 1.0), 'UI/Common/Colors/Blue'),
         'darkTurquoise': ((0.0, 0.34, 0.33, 1.0), 'UI/Common/Colors/DarkTurquoise'),
         'turquoise': ((0.0, 0.63, 0.57, 1.0), 'UI/Common/Colors/Turquoise'),
         'orange': ((1.0, 0.35, 0.0, 1.0), 'UI/Common/Colors/Orange'),
         'black': ((0.0, 0.0, 0.0, 1.0), 'UI/Common/Colors/Black'),
         'yellow': ((1.0, 0.7, 0.0, 1.0), 'UI/Common/Colors/Yellow'),
         'white': ((0.7, 0.7, 0.7, 1.0), 'UI/Common/Colors/White'),
         'indigo': ((0.3, 0.0, 0.5, 1.0), 'UI/Common/Colors/Indigo')}



    def GetStateColor(self, flag):
        self.InitColors()
        colors = self.GetStateColors()
        defColor = self.GetStateProps(flag)[2]
        return self.stateColors.get(flag, colors[defColor][0])



    def GetStateBlink(self, where, flag):
        defBlink = self.defaultBlinkStates.get((where, flag), 0)
        return settings.user.overview.Get('stateBlinks', {}).get((where, flag), defBlink)



    def GetEwarGraphicID(self, ewarType):
        (flag, gid,) = self.ewarStates[ewarType]
        return gid



    def GetEwarTypes(self):
        return self.ewarStates.items()



    def GetEwarFlag(self, ewarType):
        (flag, gid,) = self.ewarStates[ewarType]
        return flag



    def GetEwarTypeByEwarState(self, flag = None):
        if not getattr(self, 'ewartypebystate', {}):
            ret = {}
            for (ewarType, (f, gid,),) in self.ewarStates.iteritems():
                ret[f] = ewarType

            self.ewartypebystate = ret
        if flag:
            return self.ewartypebystate[flag]
        return self.ewartypebystate



    def GetEwarHint(self, ewarType):
        (flag, gid,) = self.ewarStates[ewarType]
        return self.GetSmartFilterProps()[flag][0]



    def SetStateColor(self, flag, color):
        self.InitColors()
        self.stateColors[flag] = color
        settings.user.overview.Set('stateColors', self.stateColors.copy())
        self.NotifyOnStateSetupChance('stateColor')



    def SetStateBlink(self, where, flag, blink):
        all = settings.user.overview.Get('stateBlinks', {})
        all[(where, flag)] = blink
        settings.user.overview.Set('stateBlinks', all)
        self.NotifyOnStateSetupChance('stateBlink')



    def InitColors(self, reset = 0):
        if not self.stateColorsInited or reset:
            self.stateColors = settings.user.overview.Get('stateColors', {})
            self.stateColorsInited = 1



    def ResetColors(self):
        settings.user.overview.Set('stateColors', {})
        self.InitColors(reset=True)
        self.NotifyOnStateSetupChance('stateColor')



    def InitFilter(self):
        self.filterCategs = set([const.categoryShip, const.categoryEntity, const.categoryDrone])
        self.updateCategs = self.filterCategs.copy()
        self.filterGroups = set([const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupStargate,
         const.groupWarpGate,
         const.groupAgentsinSpace,
         const.groupCosmicSignature,
         const.groupHarvestableCloud,
         const.groupForceField,
         const.groupWreck])
        if settings.user.overview.Get('applyOnlyToShips', 1):
            self.updateGroups = set()
        else:
            self.updateCategs.add(const.categoryStructure)
            self.updateCategs.add(const.categorySovereigntyStructure)
            self.updateGroups = self.filterGroups.copy()
        settings.user.ui.Set('linkedWeapons_groupsDict', {})



    def ChangeStateOrder(self, where, flag, idx):
        current = self.GetStateOrder(where)[:]
        while flag in current:
            current.remove(flag)

        if idx == -1:
            idx = len(current)
        current.insert(idx, flag)
        settings.user.overview.Set(where.lower() + 'Order', current)
        self.NotifyOnStateSetupChance('flagOrder')



    def ChangeStateState(self, where, flag, true):
        current = self.GetStateStates(where)[:]
        while flag in current:
            current.remove(flag)

        if true:
            current.append(flag)
        settings.user.overview.Set(where.lower() + 'States', current)
        self.NotifyOnStateSetupChance('flagState')



    def ChangeColumnOrder(self, column, idx):
        current = sm.GetService('tactical').GetColumnOrder()[:]
        while column in current:
            current.remove(column)

        if idx == -1:
            idx = len(current)
        current.insert(idx, column)
        settings.user.overview.Set('overviewColumnOrder', current)
        self.NotifyOnStateSetupChance('columnOrder')



    def ChangeColumnState(self, column, true):
        (current, displayColumns,) = sm.GetService('tactical').GetColumns()[:]
        while column in current:
            current.remove(column)

        if true:
            current.append(column)
        settings.user.overview.Set('overviewColumns', current)
        self.NotifyOnStateSetupChance('columns')



    def ChangeLabelOrder(self, oldidx, idx):
        labels = self.GetShipLabels()
        label = self.shipLabels.pop(oldidx)
        if idx == -1:
            idx = len(self.shipLabels)
        self.shipLabels.insert(idx, label)
        settings.user.overview.Set('shipLabels', self.shipLabels)
        sm.GetService('bracket').UpdateLabels()



    def ChangeShipLabels(self, flag, true):
        labels = self.GetShipLabels()
        type = flag['type']
        flag['state'] = true
        for i in xrange(len(self.shipLabels)):
            if self.shipLabels[i]['type'] == type:
                self.shipLabels[i] = flag
                break

        settings.user.overview.Set('shipLabels', self.shipLabels)
        sm.GetService('bracket').UpdateLabels()
        sm.GetService('tactical').RefreshOverview()



    def SetDefaultShipLabel(self, setting):
        defaults = {'default': (0, [{'state': 1,
                       'pre': '',
                       'type': 'pilot name',
                       'post': ' '},
                      {'state': 1,
                       'pre': '[',
                       'type': 'corporation',
                       'post': ']'},
                      {'state': 1,
                       'pre': '&lt;',
                       'type': 'alliance',
                       'post': '&gt;'},
                      {'state': 0,
                       'pre': "'",
                       'type': 'ship name',
                       'post': "'"},
                      {'state': 1,
                       'pre': '(',
                       'type': 'ship type',
                       'post': ')'},
                      {'state': 0,
                       'pre': '[',
                       'type': None,
                       'post': ''}]),
         'ally': (0, [{'state': 1,
                    'pre': '',
                    'type': 'pilot name',
                    'post': ''},
                   {'state': 1,
                    'pre': ' [',
                    'type': 'corporation',
                    'post': ''},
                   {'state': 1,
                    'pre': ',',
                    'type': 'alliance',
                    'post': ''},
                   {'state': 1,
                    'pre': ']',
                    'type': None,
                    'post': ''},
                   {'state': 0,
                    'pre': "'",
                    'type': 'ship name',
                    'post': "'"},
                   {'state': 0,
                    'pre': '(',
                    'type': 'ship type',
                    'post': ')'}]),
         'corpally': (0, [{'state': 1,
                        'pre': '[',
                        'type': 'corporation',
                        'post': '] '},
                       {'state': 1,
                        'pre': '',
                        'type': 'pilot name',
                        'post': ''},
                       {'state': 1,
                        'pre': ' &lt;',
                        'type': 'alliance',
                        'post': '&gt;'},
                       {'state': 0,
                        'pre': "'",
                        'type': 'ship name',
                        'post': "'"},
                       {'state': 0,
                        'pre': '(',
                        'type': 'ship type',
                        'post': ')'},
                       {'state': 0,
                        'pre': '[',
                        'type': None,
                        'post': ''}])}
        settings.user.overview.Set('hideCorpTicker', defaults.get(setting, 'default')[0])
        self.shipLabels = defaults.get(setting, 'default')[1]
        settings.user.overview.Set('shipLabels', self.shipLabels)
        sm.GetService('bracket').UpdateLabels()



    def NotifyOnStateSetupChance(self, reason):
        self.notifyStateChangeTimer = base.AutoTimer(1000, self._NotifyOnStateSetupChance, reason)



    def _NotifyOnStateSetupChance(self, reason):
        self.notifyStateChangeTimer = None
        sm.ScatterEvent('OnStateSetupChance', reason)



    def CheckIfUpdateItem(self, slimItem):
        return slimItem.categoryID in self.updateCategs or slimItem.groupID in self.updateGroups



    def CheckIfFilterItem(self, slimItem):
        return slimItem.categoryID in self.filterCategs or slimItem.groupID in self.filterGroups



    def GetStates(self, itemID, flags):
        ret = []
        for flag in flags:
            if flag in self.exclusive:
                ret.append(itemID == self.exclusives.get(flag, 0))
                continue
            ret.append(self.states.get(flag, {}).get(itemID, 0))

        return ret



    def GetExclState(self, flag):
        return self.exclusives.get(flag, None)



    def DoExclusive(self, itemID, flag, true, *args):
        excl = self.exclusives.get(flag, None)
        if true:
            if excl and excl != itemID:
                sm.ScatterEvent('OnStateChange', excl, flag, 0, *args)
            sm.ScatterEvent('OnStateChange', itemID, flag, 1, *args)
            self.exclusives[flag] = itemID
        else:
            sm.ScatterEvent('OnStateChange', itemID, flag, 0, *args)
            self.exclusives[flag] = None



    def SetState(self, itemID, flag, state, *args):
        self.LogInfo('SetState', itemID, flag, state, *args)
        if flag in self.exclusive:
            self.DoExclusive(itemID, flag, state, *args)
            return 
        states = self.states.get(flag, {})
        if state:
            states[itemID] = state
        elif itemID in states:
            del states[itemID]
        if states:
            self.states[flag] = states
        elif flag in self.states:
            del self.states[flag]
        self.LogInfo('Before OnStateChange', itemID, flag, state, *args)
        sm.ScatterEvent('OnStateChange', itemID, flag, state, *args)



    def DoBallClear(self, *etc):
        self.states = {}



    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return 
        self.LogInfo('DoBallRemove::state', ball.id)
        if ball.id in self.exclusives.itervalues():
            for state in self.exclusive:
                if self.GetExclState(state) == ball.id:
                    self.SetState(ball.id, state, 0)

        if ball.id == eve.session.shipid:
            return 
        for stateDict in self.states.values():
            if ball.id in stateDict:
                del stateDict[ball.id]




    def GetAllShipLabels(self):
        return [{'state': 1,
          'pre': '',
          'type': 'pilot name',
          'post': ' '},
         {'state': 1,
          'pre': '[',
          'type': 'corporation',
          'post': ']'},
         {'state': 1,
          'pre': '&lt;',
          'type': 'alliance',
          'post': '&gt;'},
         {'state': 0,
          'pre': "'",
          'type': 'ship name',
          'post': "'"},
         {'state': 1,
          'pre': '(',
          'type': 'ship type',
          'post': ')'},
         {'state': 0,
          'pre': '[',
          'type': None,
          'post': ''}]



    def GetShipLabels(self):
        if not getattr(self, 'shipLabels', None):
            self.shipLabels = settings.user.overview.Get('shipLabels', None) or self.GetAllShipLabels()
        return self.shipLabels



    def GetHideCorpTicker(self):
        return settings.user.overview.Get('hideCorpTicker', 0)



    def CheckStates(self, slimItem, what):
        slimItem = self.PrepareSlimItem(slimItem)
        if self.logme:
            self.LogInfo('Tactical::CheckState', slimItem)
        flag = None
        for functionName in sm.GetService('state').GetActiveStateOrderFunctionNames(what):
            if hasattr(self, 'Check' + functionName):
                if getattr(self, 'Check' + functionName, None)(slimItem):
                    flag = getattr(state, 'flag' + functionName, None)
                    break
            else:
                print 'missing function',
                print functionName

        return flag



    def PrepareSlimItem(self, item):
        try:
            item = util.KeyVal(item)
        except TypeError:
            sys.exc_clear()
        item.ownerID = getattr(item, 'ownerID', None)
        item.charID = getattr(item, 'charID', None)
        item.corpID = getattr(item, 'corpID', None)
        item.allianceID = getattr(item, 'allianceID', None)
        item.groupID = getattr(item, 'groupID', None)
        item.categoryID = getattr(item, 'categoryID', None)
        item.bounty = getattr(item, 'bounty', None)
        item.warFactionID = getattr(item, 'warFactionID', None)
        item.securityStatus = getattr(item, 'securityStatus', None)
        return item



    def _GetRelationship(self, item):
        return sm.GetService('addressbook').GetRelationship(item.ownerID, item.corpID, getattr(item, 'allianceID', None))



    @IsStandingRelevant
    def CheckStandingHigh(self, slimItem):
        relationships = self._GetRelationship(slimItem)
        return relationships.persToPers > const.contactGoodStanding or relationships.persToCorp > const.contactGoodStanding or relationships.persToAlliance > const.contactGoodStanding or relationships.corpToPers > const.contactGoodStanding or relationships.corpToCorp > const.contactGoodStanding or relationships.corpToAlliance > const.contactGoodStanding or relationships.allianceToPers > const.contactGoodStanding or relationships.allianceToCorp > const.contactGoodStanding or relationships.allianceToAlliance > const.contactGoodStanding



    @IsStandingRelevant
    def CheckStandingGood(self, slimItem):
        relationships = self._GetRelationship(slimItem)
        return relationships.persToPers > const.contactNeutralStanding and relationships.persToPers <= const.contactGoodStanding or relationships.persToCorp > const.contactNeutralStanding and relationships.persToCorp <= const.contactGoodStanding or relationships.persToAlliance > const.contactNeutralStanding and relationships.persToAlliance <= const.contactGoodStanding or relationships.corpToPers > const.contactNeutralStanding and relationships.corpToPers <= const.contactGoodStanding or relationships.corpToCorp > const.contactNeutralStanding and relationships.corpToCorp <= const.contactGoodStanding or relationships.corpToAlliance > const.contactNeutralStanding and relationships.corpToAlliance <= const.contactGoodStanding or relationships.allianceToPers > const.contactNeutralStanding and relationships.allianceToPers <= const.contactGoodStanding or relationships.allianceToCorp > const.contactNeutralStanding and relationships.allianceToCorp <= const.contactGoodStanding or relationships.allianceToAlliance > const.contactNeutralStanding and relationships.allianceToAlliance <= const.contactGoodStanding



    @IsStandingRelevant
    def CheckStandingNeutral(self, slimItem):
        relationships = self._GetRelationship(slimItem)
        return relationships.hasRelationship and (getattr(slimItem, 'allianceID', None) is None or relationships.allianceToPers == const.contactNeutralStanding and relationships.allianceToCorp == const.contactNeutralStanding and relationships.allianceToAlliance == const.contactNeutralStanding and relationships.persToPers == const.contactNeutralStanding and relationships.persToCorp == const.contactNeutralStanding and relationships.persToAlliance == const.contactNeutralStanding and relationships.corpToPers == const.contactNeutralStanding and relationships.corpToCorp == const.contactNeutralStanding and relationships.corpToAlliance == const.contactNeutralStanding and not self.CheckSameCorp(slimItem) and not self.CheckSameAlliance(slimItem))



    @IsStandingRelevant
    def CheckStandingBad(self, slimItem):
        relationships = self._GetRelationship(slimItem)
        return relationships.persToPers < const.contactNeutralStanding and relationships.persToPers >= const.contactBadStanding or relationships.persToCorp < const.contactNeutralStanding and relationships.persToCorp >= const.contactBadStanding or relationships.persToAlliance < const.contactNeutralStanding and relationships.persToAlliance >= const.contactBadStanding or relationships.corpToPers < const.contactNeutralStanding and relationships.corpToPers >= const.contactBadStanding or relationships.corpToCorp < const.contactNeutralStanding and relationships.corpToCorp >= const.contactBadStanding or relationships.corpToAlliance < const.contactNeutralStanding and relationships.corpToAlliance >= const.contactBadStanding or relationships.allianceToPers < const.contactNeutralStanding and relationships.allianceToPers >= const.contactBadStanding or relationships.allianceToCorp < const.contactNeutralStanding and relationships.allianceToCorp >= const.contactBadStanding or relationships.allianceToAlliance < const.contactNeutralStanding and relationships.allianceToAlliance >= const.contactBadStanding



    @IsStandingRelevant
    def CheckStandingHorrible(self, slimItem):
        relationships = self._GetRelationship(slimItem)
        return relationships.persToPers < const.contactBadStanding or relationships.persToCorp < const.contactBadStanding or relationships.persToAlliance < const.contactBadStanding or relationships.corpToCorp < const.contactBadStanding or relationships.corpToPers < const.contactBadStanding or relationships.corpToAlliance < const.contactBadStanding or relationships.allianceToPers < const.contactBadStanding or relationships.allianceToCorp < const.contactBadStanding or relationships.allianceToAlliance < const.contactBadStanding



    def CheckSameCorp(self, slimItem):
        if self.logme:
            self.LogInfo('Tactical::CheckSameCorp', slimItem)
        return slimItem.corpID == session.corpid and slimItem.categoryID in (const.categoryDrone,
         const.categoryShip,
         const.categoryOwner,
         const.categoryStructure,
         const.categorySovereigntyStructure,
         const.categoryOrbital)



    def CheckSameAlliance(self, slimItem):
        if self.logme:
            self.LogInfo('Tactical::CheckSameAlliance', slimItem)
        return eve.session.allianceid and getattr(slimItem, 'allianceID', None) == eve.session.allianceid



    def CheckSameFleet(self, slimItem):
        if self.logme:
            self.LogInfo('Tactical::CheckSameFleet', slimItem)
        if slimItem.charID and eve.session.fleetid:
            return sm.GetService('fleet').IsMember(slimItem.charID)
        return 0



    def CheckSameMilitia(self, slimItem):
        if self.logme:
            self.LogInfo('Tactical::CheckSameMilitia', slimItem)
        if slimItem.charID and slimItem.corpID and eve.session.warfactionid:
            return eve.session.warfactionid == slimItem.warFactionID
        return 0



    def CheckAgentInteractable(self, slimItem):
        if self.logme:
            self.LogInfo('Tactical::CheckAgentInteractable', slimItem)
        return slimItem.groupID == const.groupAgentsinSpace



    def CheckIsWanted(self, slimItem):
        if self.logme:
            self.LogInfo('Tactical::CheckIsWanted', slimItem)
        return slimItem.bounty > 0



    def CheckAtWarCanFight(self, slimItem):
        if self.logme:
            self.LogInfo('Tactical::CheckAtWarCanFight', slimItem)
        if slimItem.corpID:
            id = getattr(slimItem, 'allianceID', None) or slimItem.corpID
            if id not in self.atWar:
                self.atWar[id] = sm.StartService('war').GetRelationship(id)
            return self.atWar[id] == const.warRelationshipAtWarCanFight
        else:
            return 0



    def CheckAtWarMilitia(self, slimItem):
        if self.logme:
            self.LogInfo('Tactical::CheckAtWarMilitia', slimItem)
        if eve.session.warfactionid and slimItem.warFactionID:
            id = (slimItem.warFactionID, eve.session.warfactionid)
            if id not in self.atWar:
                self.atWar[id] = sm.StartService('facwar').IsEnemyFaction(slimItem.warFactionID, eve.session.warfactionid)
            return self.atWar[id] == True
        return 0



    def CheckDangerous(self, slimItem):
        if self.logme:
            self.LogInfo('Tactical::CheckDangerous', slimItem)
        if slimItem.charID and -0.1 > (slimItem.securityStatus or 0) >= -5.0:
            return 1
        return 0



    def CheckCriminal(self, slimItem):
        if self.logme:
            self.LogInfo('Tactical::CheckCriminal', slimItem)
        if slimItem.charID and (slimItem.securityStatus or 0) < -5.0:
            return 1
        if slimItem.charID and slimItem.groupID != const.groupCapsule:
            return min(sm.GetService('michelle').GetAggressionState(slimItem.charID), 1)
        return 0



    def CheckWreckEmpty(self, slimItem):
        return slimItem.groupID == const.groupWreck and slimItem.isEmpty



    def CheckNoStanding(self, slimItem):
        relationships = self._GetRelationship(slimItem)
        return not relationships.hasRelationship and util.IsCharacter(slimItem.ownerID)



    def CheckWreckViewed(self, slimItem):
        return sm.GetService('wreck').IsViewedWreck(slimItem.itemID)




def GetNPCGroups():
    npcGroups = {localization.GetByLabel('UI/Services/State/NonPlayerCharacter/Generic'): {localization.GetByLabel('UI/Services/State/NonPlayerCharacter/Pirate'): [const.groupAsteroidAngelCartelBattleCruiser,
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
                                                                                                                                                        const.groupInvasionSanshaNationBattleship,
                                                                                                                                                        const.groupInvasionSanshaNationCapital,
                                                                                                                                                        const.groupInvasionSanshaNationCruiser,
                                                                                                                                                        const.groupInvasionSanshaNationFrigate,
                                                                                                                                                        const.groupInvasionSanshaNationIndustrial],
                                                                               localization.GetByLabel('UI/Services/State/NonPlayerCharacter/Mission'): [const.groupMissionDrone,
                                                                                                                                                         const.groupStorylineBattleship,
                                                                                                                                                         const.groupStorylineFrigate,
                                                                                                                                                         const.groupStorylineCruiser,
                                                                                                                                                         const.groupStorylineMissionBattleship,
                                                                                                                                                         const.groupStorylineMissionFrigate,
                                                                                                                                                         const.groupStorylineMissionCruiser,
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
                                                                                                                                                         const.groupMissionGenericDestroyers],
                                                                               localization.GetByLabel('UI/Services/State/NonPlayerCharacter/Police'): [const.groupPoliceDrone],
                                                                               localization.GetByLabel('UI/Services/State/NonPlayerCharacter/Concord'): [const.groupConcordDrone],
                                                                               localization.GetByLabel('UI/Services/State/NonPlayerCharacter/Customs'): [const.groupCustomsOfficial],
                                                                               localization.GetByLabel('UI/Services/State/NonPlayerCharacter/FactionNavy'): [const.groupFactionDrone]}}
    return npcGroups


exports = util.AutoExports('util', {'GetNPCGroups': GetNPCGroups})

