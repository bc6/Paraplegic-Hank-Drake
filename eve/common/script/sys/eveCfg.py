import blue
import util
import sys
import types
import string
import cPickle
import re
import random
import copy
import uthread
import log
import svc
import const
import service
import dbutil
import macho
import yaml
import math
globals().update(service.consts)
from sys import *
import standingUtil

class Standings():
    __guid__ = 'sys.Standings'
    __passbyvalue__ = 1

    def __init__(self, fromID, fromFactionID, fromCorpID, fromCharID, toID, toFactionID, toCorpID, toCharID):
        (self.fromID, self.fromFactionID, self.fromCorpID, self.fromCharID, self.toID, self.toFactionID, self.toCorpID, self.toCharID,) = (fromID,
         fromFactionID,
         fromCorpID,
         fromCharID,
         toID,
         toFactionID,
         toCorpID,
         toCharID)
        self.faction = util.KeyVal(faction=0.0, corp=0.0, char=0.0)
        self.corp = util.KeyVal(faction=0.0, corp=0.0, char=0.0)
        self.char = util.KeyVal(faction=0.0, corp=0.0, char=0.0)



    def __str__(self):
        return 'Standing from %s toward %s: faction:(%s,%s,%s), corp:(%s,%s,%s), char:(%s,%s,%s)' % (self.fromID,
         self.toID,
         self.faction.faction,
         self.faction.corp,
         self.faction.char,
         self.corp.faction,
         self.corp.corp,
         self.corp.char,
         self.char.faction,
         self.char.corp,
         self.char.char)



    def __repr__(self):
        return self.__str__()



    def CanUseAgent(self, level, agentTypeID = None, noL1Check = 1):
        return CanUseAgent(level, agentTypeID, self.faction.char, self.corp.char, self.char.char, self.fromCorpID, self.fromFactionID, {}, noL1Check)



    def __getattr__(self, theKey):
        if theKey == 'minimum':
            m = None
            for each in (self.faction, self.corp, self.char):
                for other in (each.faction, each.corp, each.char):
                    if other != 0.0 and (m is None or other < m):
                        m = other


            if m is None:
                return 0.0
            return m
        if theKey == 'maximum':
            m = None
            for each in (self.faction, self.corp, self.char):
                for other in (each.faction, each.corp, each.char):
                    if other != 0.0 and (m is None or other > m):
                        m = other


            if m is None:
                return 0.0
            return m
        if theKey == 'direct':
            if self.fromID == self.fromFactionID:
                tmp = self.faction
            elif self.fromID == self.fromCorpID:
                tmp = self.corp
            elif self.fromID == self.fromCharID:
                tmp = self.char
            if self.toID == self.toFactionID:
                return tmp.faction
            else:
                if self.toID == self.toCorpID:
                    return tmp.corp
                if self.toID == self.toCharID:
                    return tmp.char
                return 0.0
        elif theKey == 'all':
            return [(self.fromFactionID, self.toFactionID, self.faction.faction),
             (self.fromFactionID, self.toCorpID, self.faction.corp),
             (self.fromFactionID, self.toCharID, self.faction.char),
             (self.fromCorpID, self.toFactionID, self.corp.faction),
             (self.fromCorpID, self.toCorpID, self.corp.corp),
             (self.fromCorpID, self.toCharID, self.corp.char),
             (self.fromCharID, self.toFactionID, self.char.faction),
             (self.fromCharID, self.toCorpID, self.char.corp),
             (self.fromCharID, self.toCharID, self.char.char)]
        raise AttributeError(theKey)




def CanUseAgent(level, agentTypeID, fac, coc, cac, fromCorpID, fromFactionID, skills, noL1Check = 1):
    if agentTypeID == const.agentTypeAura:
        return True
    else:
        if level == 1 and agentTypeID != const.agentTypeResearchAgent and noL1Check:
            return 1
        m = (level - 1) * 2.0 - 1.0
        if boot.role == 'client':
            bonus = 0.0
            if not skills:
                char = sm.GetService('godma').GetItem(eve.session.charid)
                for skill in char.skills.itervalues():
                    if skill.typeID in (const.typeConnections, const.typeDiplomacy, const.typeCriminalConnections):
                        skills[skill.typeID] = skill.skillLevel

                skills[0] = 0
            (unused, facBonus,) = standingUtil.GetStandingBonus(fac, fromFactionID, skills)
            (unused, cocBonus,) = standingUtil.GetStandingBonus(coc, fromFactionID, skills)
            (unused, cacBonus,) = standingUtil.GetStandingBonus(cac, fromFactionID, skills)
            if facBonus > 0.0:
                fac = (1.0 - (1.0 - fac / 10.0) * (1.0 - facBonus / 10.0)) * 10.0
            if cocBonus > 0.0:
                coc = (1.0 - (1.0 - coc / 10.0) * (1.0 - cocBonus / 10.0)) * 10.0
            if cacBonus > 0.0:
                cac = (1.0 - (1.0 - cac / 10.0) * (1.0 - cacBonus / 10.0)) * 10.0
        if max(fac, coc, cac) >= m and min(fac, coc, cac) > -2.0:
            if agentTypeID == const.agentTypeResearchAgent and coc < m - 2.0:
                return 0
            return 1
        return 0



class EveDataConfig(svc.dataconfig):
    __guid__ = 'svc.eveDataconfig'
    __replaceservice__ = 'dataconfig'

    def __init__(self):
        svc.dataconfig.__init__(self)
        import __builtin__
        __builtin__.SEC = 10000000L
        __builtin__.MIN = SEC * 60L
        __builtin__.HOUR = MIN * 60L
        __builtin__.DAY = HOUR * 24L
        __builtin__.WEEK = DAY * 7L
        __builtin__.MONTH = DAY * 30L
        __builtin__.YEAR = MONTH * 12L
        __builtin__.OWNERID = 1
        __builtin__.OWNERID = 2
        __builtin__.LOCID = 3
        __builtin__.TYPEID = 4
        __builtin__.TYPEID2 = 5
        __builtin__.TYPEIDL = 29
        __builtin__.BPTYPEID = 6
        __builtin__.GROUPID = 7
        __builtin__.GROUPID2 = 8
        __builtin__.CATID = 9
        __builtin__.CATID2 = 10
        __builtin__.DGMATTR = 11
        __builtin__.DGMFX = 12
        __builtin__.DGMTYPEFX = 13
        __builtin__.AMT = 18
        __builtin__.AMT2 = 19
        __builtin__.AMT3 = 20
        __builtin__.DIST = 21
        __builtin__.TYPEIDANDQUANTITY = 24
        __builtin__.OWNERIDNICK = 25
        __builtin__.SESSIONSENSITIVESTATIONID = 26
        __builtin__.SESSIONSENSITIVELOCID = 27
        __builtin__.ISK = 28
        __builtin__.AUR = 30



    def _CreateConfig(self):
        return EveConfig()




class EveConfig(util.config):
    __guid__ = 'util.EveConfig'

    def __init__(self):
        util.config.__init__(self)
        self.fmtMapping[OWNERID] = lambda value, value2: cfg.eveowners.Get(value).ownerName
        self.fmtMapping[OWNERIDNICK] = lambda value, value2: cfg.eveowners.Get(value).ownerName.split(' ')[0]
        self.fmtMapping[LOCID] = lambda value, value2: cfg.evelocations.Get(value).locationName
        self.fmtMapping[SESSIONSENSITIVELOCID] = self._EveConfig__FormatSessionSensitiveLOCID
        self.fmtMapping[SESSIONSENSITIVESTATIONID] = self._EveConfig__FormatSessionSensitiveStationID
        self.fmtMapping[TYPEID] = lambda value, value2: cfg.invtypes.Get(value).typeName
        self.fmtMapping[TYPEID2] = lambda value, value2: cfg.invtypes.Get(value).description
        self.fmtMapping[TYPEIDL] = self.TypeNameList
        self.fmtMapping[BPTYPEID] = lambda value, value2: cfg.invbptypes.Get(value).blueprintTypeName
        self.fmtMapping[GROUPID] = lambda value, value2: cfg.invgroups.Get(value).groupName
        self.fmtMapping[GROUPID2] = lambda value, value2: cfg.invgroups.Get(value).description
        self.fmtMapping[CATID] = lambda value, value2: cfg.invcategories.Get(value).categoryName
        self.fmtMapping[CATID2] = lambda value, value2: cfg.invcategories.Get(value).description
        self.fmtMapping[AMT] = lambda value, value2: util.FmtAmt(value)
        self.fmtMapping[AMT2] = lambda value, value2: util.FmtISK(value)
        self.fmtMapping[AMT3] = lambda value, value2: util.FmtISK(value)
        self.fmtMapping[ISK] = lambda value, value2: util.FmtISK(value)
        self.fmtMapping[AUR] = lambda value, value2: util.FmtAUR(value)
        self.fmtMapping[DIST] = lambda value, value2: util.FmtDist(value)
        self.fmtMapping[TYPEIDANDQUANTITY] = self._EveConfig__FormatTypeIDAndQuantity
        self.crystalgroups = []
        self.planetattributes = Recordset(Row, None)



    def Release(self):
        util.config.Release(self)
        self.graphics = None
        self.icons = None
        self.sounds = None
        self.invgroups = None
        self.invtypes = None
        self.invbptypes = None
        self.invmetagroups = None
        self.invmetatypes = None
        self.ramaltypes = None
        self.ramaltypesdetailpercategory = None
        self.ramaltypesdetailpergroup = None
        self.ramactivities = None
        self.ramtyperequirements = None
        self.invtypematerials = None
        self.ramcompletedstatuses = None
        self.mapcelestialdescriptions = None
        self.dgmattribs = None
        self.dgmeffects = None
        self.dgmtypeattribs = None
        self.dgmtypeeffects = None
        self.dgmunits = None
        self.eveowners = None
        self.evelocations = None
        self.corptickernames = None
        self.allianceshortnames = None
        self.factions = None
        self.npccorporations = None
        self.crystalgroups = None
        self.certificates = None
        self.certificaterelationships = None
        self.locationwormholeclasses = None
        self.locationscene = None
        self.planetattributes = None
        self.schematics = None
        self.schematicstypemap = None
        self.schematicspinmap = None
        self.schematicsByPin = None
        self.schematicsByType = None
        self.billtypes = None
        self.bloodlineNames = None
        self.overviewDefaults = None
        self.overviewDefaultGroups = None
        self.positions = None



    def IsChargeCompatible(self, item):
        if not item[const.ixSingleton]:
            return 0
        else:
            return item[const.ixGroupID] in self.__chargecompatiblegroups__



    def IsShipFittingFlag(self, flag):
        return flag >= const.flagSlotFirst and flag <= const.flagSlotLast or flag >= const.flagRigSlot0 and flag <= const.flagRigSlot7 or flag >= const.flagSubSystemSlot0 and flag <= const.flagSubSystemSlot7



    def IsFittableCategory(self, categoryID):
        return categoryID in (const.categoryModule, const.categorySubSystem, const.categoryStructureUpgrade)



    def IsSubSystemVisible(self, flag):
        return flag >= const.flagSubSystemSlot0 and flag < const.flagSubSystemSlot0 + const.visibleSubSystems



    def IsContainer(self, item):
        if not item.singleton:
            return 0
        else:
            return item.categoryID in self.__containercategories__ or item.groupID in self.__containergroups__



    def GetItemVolume(self, item, qty = None, invmgr = None):
        if item.typeID == const.typePlasticWrap:
            if invmgr is None:
                volume = eve.GetInventoryFromId(item.itemID).GetCapacity().used
            else:
                volume = invmgr.GetInventoryFromIdEx(item.itemID, -1).GetCapacity().used
        elif item.categoryID == const.categoryShip and not item.singleton and item.groupID in self.__containerVolumes__ and item.typeID != const.typeBHMegaCargoShip:
            volume = self.__containerVolumes__[item.groupID]
        else:
            volume = cfg.invtypes.Get(item.typeID).volume
        if volume != -1:
            if qty is None:
                qty = item.stacksize
            if qty < 0:
                qty = 1
            volume *= qty
        return volume



    def GetTypeVolume(self, typeID, qty = -1):
        if typeID == const.typePlasticWrap:
            raise RuntimeError('GetTypeVolume: cannot determine volume of plastic from type alone')
        ty = cfg.invtypes.Get(typeID)
        item = util.KeyVal(typeID=typeID, groupID=ty.groupID, categoryID=ty.categoryID, quantity=qty, singleton=-qty if qty < 0 else 0, stacksize=qty if qty >= 0 else 1)
        return self.GetItemVolume(item)



    def AppGetStartupData(self):
        configSvc = sm.GetService('config')
        initdata = configSvc.GetInitVals()
        self.GotInitData(initdata)



    def ReportLoginProgress(self, section, stepNum, totalSteps = None):
        if totalSteps is not None:
            self.totalLogonSteps = totalSteps
        if macho.mode == 'client':
            sm.ChainEvent('ProcessLoginProgress', 'loginprogress::miscinitdata', section, stepNum, self.totalLogonSteps)
        else:
            cfg.LogInfo(section, stepNum)



    def GotInitData(self, initdata):
        cfg.LogInfo('App GotInitData')
        util.config.GotInitData(self, initdata)
        self.dgmunits = self.LoadBulk('dgmunits', const.cacheDogmaUnits, Recordset(Row, 'unitID'))
        self.ReportLoginProgress('coreInitData1', self.totalLogonSteps - const.cfgLogonSteps / 2)
        self.invbptypes = self.LoadBulk('invbptypes', const.cacheInvBlueprintTypes, Recordset(Row, 'blueprintTypeID'))
        self.invcategories = self.LoadBulk('invcategories', const.cacheInvCategories, Recordset(InvCategory, 'categoryID'))
        self.invmetagroups = self.LoadBulk('invmetagroups', const.cacheInvMetaGroups, Recordset(InvMetaGroup, 'metaGroupID'))
        self.invgroups = self.LoadBulk('invgroups', const.cacheInvGroups, Recordset(InvGroup, 'groupID'))
        self.invtypes = self.LoadBulk('invtypes', const.cacheInvTypes, Recordset(InvType, 'typeID'))
        self.invtypereactions = self.LoadBulk('invtypereactions', const.cacheInvTypeReactions, None, 'reactionTypeID')
        self.invmetatypes = self.LoadBulk('invmetatypes', const.cacheInvMetaTypes, Recordset(Row, 'typeID'))
        self.invmetatypesByParent = self.LoadBulk('invmetatypesByParent', const.cacheInvMetaTypes, None, 'parentTypeID')
        invcontrabandtypes = self.LoadBulk(None, const.cacheInvContrabandTypes)
        self.invcontrabandTypesByFaction = {}
        self.invcontrabandFactionsByType = {}
        self.bulkIDsToCfgNames[const.cacheInvContrabandTypes] = ['invcontrabandTypesByFaction', 'invcontrabandFactionsByType']
        for each in invcontrabandtypes:
            if each.factionID not in self.invcontrabandTypesByFaction:
                self.invcontrabandTypesByFaction[each.factionID] = {}
            self.invcontrabandTypesByFaction[each.factionID][each.typeID] = each
            if each.typeID not in self.invcontrabandFactionsByType:
                self.invcontrabandFactionsByType[each.typeID] = {}
            self.invcontrabandFactionsByType[each.typeID][each.factionID] = each

        self.ReportLoginProgress('coreInitData2', self.totalLogonSteps - const.cfgLogonSteps / 2 + 1)
        self.dgmattribs = self.LoadBulk('dgmattribs', const.cacheDogmaAttributes, Recordset(DgmAttribute, 'attributeID'))
        self.dgmeffects = self.LoadBulk('dgmeffects', const.cacheDogmaEffects, Recordset(DgmEffect, 'effectID'))
        self.dgmtypeattribs = self.LoadBulk('dgmtypeattribs', const.cacheDogmaTypeAttributes, None, 'typeID')
        self.dgmtypeeffects = self.LoadBulk('dgmtypeeffects', const.cacheDogmaTypeEffects, None, 'typeID')
        self.shiptypes = self.LoadBulk('shiptypes', const.cacheShipTypes, Recordset(Row, 'shipTypeID'))
        self.ramaltypes = self.LoadBulk('ramaltypes', const.cacheRamAssemblyLineTypes, Recordset(Row, 'assemblyLineTypeID'))
        self.ramaltypesdetailpercategory = self.LoadBulk('ramaltypesdetailpercategory', const.cacheRamAssemblyLineTypesCategory, None, 'assemblyLineTypeID', virtualColumns=[('activityID', RamActivityVirtualColumn)])
        self.ramaltypesdetailpergroup = self.LoadBulk('ramaltypesdetailpergroup', const.cacheRamAssemblyLineTypesGroup, None, 'assemblyLineTypeID', virtualColumns=[('activityID', RamActivityVirtualColumn)])
        self.ramactivities = self.LoadBulk('ramactivities', const.cacheRamActivities, Recordset(RamActivity, 'activityID'))
        self.ramcompletedstatuses = self.LoadBulk('ramcompletedstatuses', const.cacheRamCompletedStatuses, Recordset(RamCompletedStatus, 'completedStatus'))
        self.invtypematerials = self.LoadBulk('invtypematerials', const.cacheInvTypeMaterials, None, 'typeID')
        ramtyperequirements = self.LoadBulk('ramtyperequirements', const.cacheRamTypeRequirements)
        d = {}
        for row in ramtyperequirements:
            key = (row.typeID, row.activityID)
            if key in d:
                d[key].append(row)
            else:
                d[key] = [row]

        self.ramtyperequirements = d
        self.mapcelestialdescriptions = self.LoadBulk('mapcelestialdescriptions', const.cacheMapCelestialDescriptions, Recordset(MapCelestialDescription, 'itemID'))
        self.certificates = self.LoadBulk('certificates', const.cacheCertificates, Recordset(Certificate, 'certificateID'))
        self.certificaterelationships = self.LoadBulk('certificaterelationships', const.cacheCertificateRelationships, Recordset(Row, 'relationshipID'))
        self.certificateRelationshipsByChildID = self.LoadBulk('certificateRelationshipsByChildID', const.cacheCertificateRelationships, Recordset(Row, 'relationshipID'))
        self.locationwormholeclasses = self.LoadBulk('locationwormholeclasses', const.cacheMapLocationWormholeClasses, Recordset(Row, 'locationID'))
        self.locationscenes = self.LoadBulk('locationscenes', const.cacheMapLocationScenes, Recordset(Row, 'locationID'))
        self.ReportLoginProgress('coreInitData3', self.totalLogonSteps - const.cfgLogonSteps / 2 + 2)
        self.schematics = self.LoadBulk('schematics', const.cachePlanetSchematics, Recordset(Schematic, 'schematicID'))
        self.schematicstypemap = self.LoadBulk('schematicstypemap', const.cachePlanetSchematicsTypeMap, None, 'schematicID')
        self.schematicspinmap = self.LoadBulk('schematicspinmap', const.cachePlanetSchematicsPinMap, None, 'schematicID')
        self.schematicsByPin = self.LoadBulk('schematicsByPin', const.cachePlanetSchematicsPinMap, None, 'pinTypeID')
        self.schematicsByType = self.LoadBulk('schematicsByType', const.cachePlanetSchematicsTypeMap, None, 'typeID')
        self.groupsByCategories = self.LoadBulk('groupsByCategories', const.cacheInvGroups, None, 'categoryID')
        self.typesByGroups = self.LoadBulk('typesByGroups', const.cacheInvTypes, None, 'groupID')
        self.typesByMarketGroups = self.LoadBulk('typesByMarketGroups', const.cacheInvTypes, None, 'marketGroupID')
        self.billtypes = self.LoadBulk('billtypes', const.cacheActBillTypes, Recordset(Billtype, 'billTypeID'))
        self.overviewDefaults = self.LoadBulk('overviewDefaults', const.cacheChrDefaultOverviews, Recordset(OverviewDefault, 'overviewID'))
        self.overviewDefaultGroups = self.LoadBulk('overviewDefaultGroups', const.cacheChrDefaultOverviewGroups, None, 'overviewID')
        self.bloodlineNames = self.LoadBulk('bloodlineNames', const.cacheChrBloodlineNames, None, 'bloodlineID')
        self.factions = self.LoadBulk('factions', const.cacheChrFactions, Recordset(Row, 'factionID'))
        self.npccorporations = self.LoadBulk('npccorporations', const.cacheCrpNpcCorporations, Recordset(Row, 'corporationID'))
        self.corptickernames = self.LoadBulk('corptickernames', const.cacheCrpTickerNamesStatic, Recordset(CrpTickerNames, 'corporationID', 'GetCorpTickerNamesEx', 'GetMultiCorpTickerNamesEx'), tableID=const.cacheCrpNpcCorporations)
        self.LoadEveOwners()
        self.LoadEveLocations()
        allianceshortnameRowHeader = blue.DBRowDescriptor((('allianceID', const.DBTYPE_I4), ('shortName', const.DBTYPE_WSTR)))
        self.allianceshortnameRowset = dbutil.CRowset(allianceshortnameRowHeader, [])
        self.allianceshortnames = Recordset(AllShortNames, 'allianceID', 'GetAllianceShortNamesEx', 'GetMultiAllianceShortNamesEx')
        self.ConvertData(self.allianceshortnameRowset, self.allianceshortnames)
        positionRowHeader = blue.DBRowDescriptor((('itemID', const.DBTYPE_I8),
         ('x', const.DBTYPE_R5),
         ('y', const.DBTYPE_R5),
         ('z', const.DBTYPE_R5),
         ('yaw', const.DBTYPE_R4),
         ('pitch', const.DBTYPE_R4),
         ('roll', const.DBTYPE_R4)))
        positionRowset = dbutil.CRowset(positionRowHeader, [])
        self.positions = Recordset(Position, 'itemID', 'GetPositionEx', 'GetPositionsEx')
        self.ConvertData(positionRowset, self.positions)
        self.__containercategories__ = (const.categoryStation,
         const.categoryShip,
         const.categoryTrading,
         const.categoryStructure)
        self.__containergroups__ = (const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer,
         const.groupConstellation,
         const.groupRegion,
         const.groupSolarSystem,
         const.groupMissionContainer)
        self.__chargecompatiblegroups__ = (const.groupFrequencyMiningLaser,
         const.groupEnergyWeapon,
         const.groupProjectileWeapon,
         const.groupMissileLauncher,
         const.groupCapacitorBooster,
         const.groupHybridWeapon,
         const.groupScanProbeLauncher,
         const.groupComputerInterfaceNode,
         const.groupMissileLauncherBomb,
         const.groupMissileLauncherCruise,
         const.groupMissileLauncherDefender,
         const.groupMissileLauncherAssault,
         const.groupMissileLauncherSiege,
         const.groupMissileLauncherHeavy,
         const.groupMissileLauncherHeavyAssault,
         const.groupMissileLauncherRocket,
         const.groupMissileLauncherStandard,
         const.groupMissileLauncherCitadel,
         const.groupMissileLauncherSnowball,
         const.groupBubbleProbeLauncher,
         const.groupSensorBooster,
         const.groupRemoteSensorBooster,
         const.groupRemoteSensorDamper,
         const.groupTrackingComputer,
         const.groupTrackingDisruptor,
         const.groupTrackingLink,
         const.groupWarpDisruptFieldGenerator)
        self.__containerVolumes__ = {const.groupAssaultShip: 2500.0,
         const.groupBattlecruiser: 15000.0,
         const.groupBattleship: 50000.0,
         const.groupBlackOps: 50000.0,
         const.groupCapitalIndustrialShip: 1000000.0,
         const.groupCapsule: 500.0,
         const.groupCarrier: 1000000.0,
         const.groupCombatReconShip: 10000.0,
         const.groupCommandShip: 15000.0,
         const.groupCovertOps: 2500.0,
         const.groupCruiser: 10000.0,
         const.groupStrategicCruiser: 10000.0,
         const.groupDestroyer: 5000.0,
         const.groupDreadnought: 1000000.0,
         const.groupElectronicAttackShips: 2500.0,
         const.groupEliteBattleship: 50000.0,
         const.groupExhumer: 3750.0,
         const.groupForceReconShip: 10000.0,
         const.groupFreighter: 1000000.0,
         const.groupFrigate: 2500.0,
         const.groupHeavyAssaultShip: 10000.0,
         const.groupHeavyInterdictors: 10000.0,
         const.groupIndustrial: 20000.0,
         const.groupIndustrialCommandShip: 500000.0,
         const.groupInterceptor: 2500.0,
         const.groupInterdictor: 5000.0,
         const.groupJumpFreighter: 1000000.0,
         const.groupLogistics: 10000.0,
         const.groupMarauders: 50000.0,
         const.groupMiningBarge: 3750.0,
         const.groupSupercarrier: 1000000.0,
         const.groupPrototypeExplorationShip: 500.0,
         const.groupRookieship: 2500.0,
         const.groupShuttle: 500.0,
         const.groupStealthBomber: 2500.0,
         const.groupTitan: 10000000.0,
         const.groupTransportShip: 20000.0,
         const.groupCargoContainer: 1000.0,
         const.groupMissionContainer: 1000.0,
         const.groupSecureCargoContainer: 1000.0,
         const.groupAuditLogSecureContainer: 1000.0,
         const.groupFreightContainer: 1000.0,
         963: 5000}



    def __prepdict(self, dict):
        dict = copy.deepcopy(dict)
        if charsession:
            for (k, v,) in {'session.char': (OWNERID, charsession.charid),
             'session.nick': (OWNERIDNICK, charsession.charid),
             'session.corp': (OWNERID, charsession.corpid),
             'session.station': (LOCID, charsession.stationid),
             'session.solarsystem': (LOCID, charsession.solarsystemid2),
             'session.constellation': (LOCID, charsession.constellationid),
             'session.region': (LOCID, charsession.regionid),
             'session.location': (LOCID, charsession.locationid)}.iteritems():
                if v[1] is not None:
                    dict[k] = v

        for (k, v,) in dict.iteritems():
            if type(v) != types.TupleType:
                continue
            value2 = None
            if len(v) >= 3:
                value2 = v[2]
            dict[k] = self.FormatConvert(v[0], v[1], value2)

        return dict



    def __FormatTypeIDAndQuantity(self, typeID, quantity):
        if boot.role == 'client':
            languageID = eve.session.languageID
        elif charsession:
            languageID = charsession.languageID
        elif session and session.languageID:
            languageID = session.languageID
        else:
            languageID = prefs.languageID
        if languageID != 'EN':
            return '%d %s' % (quantity, self.invtypes.Get(typeID).typeName)
        if quantity > 1 or quantity == 0:
            plural = 1
        else:
            plural = 0
        quantity = self.__numberstrings__.get(quantity, quantity)
        if typeID == const.typeCredits:
            r = '%s credit%s' % (quantity, ['', 's'][plural])
        elif typeID in (const.typeSlaver,):
            r = '%s %s%s' % (quantity, cfg.invtypes.Get(typeID).typeName, ['', 's'][plural])
        elif self.invtypes.Get(typeID).groupID == const.groupPirateDrone:
            r = '%s %s%s' % (quantity, self.invtypes.Get(typeID).typeName, ['', 's'][plural])
        elif self.invtypes.Get(typeID).groupID in (const.groupProjectileAmmo, const.groupHybridAmmo):
            tn = self.invtypes.Get(typeID).typeName
            if tn.endswith(' S'):
                if tn.endswith(' Charge S'):
                    tn = 'small %s charge%s' % (tn[:-9], ['', 's'][plural])
                else:
                    tn = 'small %s ammunition' % tn[:-2]
            elif tn.endswith(' M'):
                if tn.endswith(' Charge M'):
                    tn = 'medium %s charge%s' % (tn[:-9], ['', 's'][plural])
                else:
                    tn = 'medium %s ammunition' % tn[:-2]
            elif tn.endswith(' L'):
                if tn.endswith(' Charge L'):
                    tn = 'large %s charge%s' % (tn[:-9], ['', 's'][plural])
                else:
                    tn = 'large %s ammunition' % tn[:-2]
            r = '%s unit%s of %s' % (quantity, ['', 's'][plural], tn)
        elif self.invgroups.Get(self.invtypes.Get(typeID).groupID).categoryID == const.categoryEntity:
            r = '%s %s%s' % (quantity, cfg.invtypes.Get(typeID).typeName, ['', 's'][plural])
        elif cfg.invtypes.Get(typeID).typeName.endswith('Unit') or cfg.invtypes.Get(typeID).typeName.endswith('unit'):
            r = '%s %s%s' % (quantity, cfg.invtypes.Get(typeID).typeName, ['', 's'][plural])
        else:
            r = '%s unit%s of %s' % (quantity, ['', 's'][plural], cfg.invtypes.Get(typeID).typeName)
        if cfg.invtypes.Get(typeID).typeName[-2:] == 'ss':
            if r.endswith('sss'):
                r = r[:-1]
        elif r.endswith('ss'):
            r = r[:-1]
        return r



    def __FormatSessionSensitiveStationID(self, stationID, solarsystemID):
        if boot.role == 'client':
            sess = eve.session
            (bla, regionID, constellationID, gra, sma,) = sm.GetService('map').GetParentLocationID(solarsystemID, gethierarchy=1)
        else:
            sess = charsession
            stationStuff = sm.services['stationSvc'].GetStation(stationID)
            (regionID, constellationID,) = (stationStuff.regionID, stationStuff.constellationID)
        ret = cfg.evelocations.Get(stationID).name
        if sess:
            if solarsystemID and solarsystemID != sess.solarsystemid and ret.find(cfg.evelocations.Get(solarsystemID).name) == -1:
                ret += mls.COMMON_INTHESYSTEM % {'system': cfg.evelocations.Get(solarsystemID).name}
            if constellationID and constellationID != sess.constellationid:
                ret += mls.COMMON_INTHECONSTELLATION % {'constellation': cfg.evelocations.Get(constellationID).name}
                if regionID and regionID != sess.regionid:
                    ret += mls.COMMON_OFTHEREGION % {'region': cfg.evelocations.Get(regionID).name}
        return ret



    def __FormatSessionSensitiveLOCID(self, solarsystemID, bla):
        if boot.role == 'client':
            sess = eve.session
            (bla, regionID, constellationID, gra, sma,) = sm.GetService('map').GetParentLocationID(solarsystemID, gethierarchy=1)
        else:
            sess = charsession
            (regionID, constellationID,) = (None, None)
        system = cfg.evelocations.Get(solarsystemID).name
        ret = system
        if sess:
            if constellationID and constellationID != sess.constellationid:
                if regionID and regionID != sess.regionid:
                    ret = mls.UI_COMMON_INTHESYSTEMINTHECONSTOFTHEREG % {'system': system,
                     'constellation': cfg.evelocations.Get(constellationID).name,
                     'region': cfg.evelocations.Get(regionID).name}
                else:
                    ret = mls.UI_COMMON_INTHESYSTEMINTHECONST % {'system': system,
                     'constellation': cfg.evelocations.Get(constellationID).name}
        return ret



    def TypeNameList(self, value, value2):
        if len(value) == 1:
            return cfg.invtypes.Get(value[0]).typeName
        leadingTypeNames = [ cfg.invtypes.Get(typeID).typeName for typeID in value[:-1] ]
        return ', '.join(leadingTypeNames) + ' ' + mls.AND + ' ' + cfg.invtypes.Get(value[-1]).typeName



    def GetCrystalGroups(self):
        if not self.crystalgroups:
            crystalGroupIDs = [ x.groupID for x in cfg.groupsByCategories.get(const.categoryCharge, []) if x.groupName.endswith('Crystal') ]
            self.crystalgroups.extend(crystalGroupIDs)
            scriptGroupIDs = [ x.groupID for x in cfg.groupsByCategories.get(const.categoryCharge, []) if x.groupName.endswith('Script') ]
            self.crystalgroups.extend(scriptGroupIDs)
        return self.crystalgroups



    def GetLocationWormholeClass(self, solarSystemID, constellationID, regionID):
        try:
            try:
                wormholeClass = self.locationwormholeclasses.Get(solarSystemID, 0).wormholeClassID
            except KeyError:
                try:
                    wormholeClass = self.locationwormholeclasses.Get(constellationID, 0).wormholeClassID
                except KeyError:
                    try:
                        wormholeClass = self.locationwormholeclasses.Get(regionID, 0).wormholeClassID
                    except KeyError:
                        wormholeClass = 0

        finally:
            return wormholeClass




    def GetLocationScene(self, solarSystemID):
        try:
            try:
                sceneID = self.locationscenes.Get(solarSystemID, 0).sceneID
            except KeyError:
                sceneID = 0

        finally:
            return sceneID




    def GetLocationSceneIndex(self, solarSystemID, constellationID, regionID):
        if util.IsWormholeSystem(solarSystemID):
            nebulaType = -self.GetLocationWormholeClass(solarSystemID, constellationID, regionID)
        else:
            nebulaType = self.GetLocationScene(solarSystemID)
        return nebulaType



    def LoadEveOwners(self):
        npccharacters = self.LoadBulk(None, const.cacheChrNpcCharacters, Recordset(Row, 'characterID'))
        rowDescriptor = blue.DBRowDescriptor((('ownerID', const.DBTYPE_I4), ('ownerName', const.DBTYPE_WSTR), ('typeID', const.DBTYPE_I2)))
        self.eveowners = Recordset(EveOwners, 'ownerID', 'GetOwnersEx', 'GetMultiOwnersEx')
        self.eveowners.header = ['ownerID', 'ownerName', 'typeID']
        bloodlinesToTypes = {const.bloodlineDeteis: const.typeCharacterDeteis,
         const.bloodlineCivire: const.typeCharacterCivire,
         const.bloodlineSebiestor: const.typeCharacterSebiestor,
         const.bloodlineBrutor: const.typeCharacterBrutor,
         const.bloodlineAmarr: const.typeCharacterAmarr,
         const.bloodlineNiKunni: const.typeCharacterNiKunni,
         const.bloodlineGallente: const.typeCharacterGallente,
         const.bloodlineIntaki: const.typeCharacterIntaki,
         const.bloodlineStatic: const.typeCharacterStatic,
         const.bloodlineModifier: const.typeCharacterModifier,
         const.bloodlineAchura: const.typeCharacterAchura,
         const.bloodlineJinMei: const.typeCharacterJinMei,
         const.bloodlineKhanid: const.typeCharacterKhanid,
         const.bloodlineVherokior: const.typeCharacterVherokior}
        for row in self.factions:
            self.eveowners.data[row.factionID] = blue.DBRow(rowDescriptor, [row.factionID, row.factionName, const.typeFaction])

        for row in self.npccorporations:
            self.eveowners.data[row.corporationID] = blue.DBRow(rowDescriptor, [row.corporationID, row.corporationName, const.typeCorporation])

        for row in npccharacters:
            self.eveowners.data[row.characterID] = blue.DBRow(rowDescriptor, [row.characterID, row.characterName, bloodlinesToTypes[row.bloodlineID]])

        self.eveowners.data[1] = blue.DBRow(rowDescriptor, [1, 'EVE System', 0])



    def LoadEveLocations(self):
        regions = self.LoadBulk(None, const.cacheMapRegionsTable, Recordset(Row, 'regionID'))
        constellations = self.LoadBulk(None, const.cacheMapConstellationsTable, Recordset(Row, 'constellationID'))
        solarsystems = self.LoadBulk(None, const.cacheMapSolarSystemsTable, Recordset(Row, 'solarSystemID'))
        stations = self.LoadBulk(None, 2209987, Recordset(Row, 'stationID'))
        rowDescriptor = blue.DBRowDescriptor((('locationID', const.DBTYPE_I4),
         ('locationName', const.DBTYPE_WSTR),
         ('x', const.DBTYPE_R5),
         ('y', const.DBTYPE_R5),
         ('z', const.DBTYPE_R5)))
        self.evelocations = Recordset(EveLocations, 'locationID', 'GetLocationsEx', 'GetMultiLocationsEx')
        self.evelocations.header = ['locationID',
         'locationName',
         'x',
         'y',
         'z']
        for row in regions:
            self.evelocations.data[row.regionID] = blue.DBRow(rowDescriptor, [row.regionID,
             row.regionName,
             row.x,
             row.y,
             -row.z])

        for row in constellations:
            self.evelocations.data[row.constellationID] = blue.DBRow(rowDescriptor, [row.constellationID,
             row.constellationName,
             row.x,
             row.y,
             -row.z])

        for row in solarsystems:
            self.evelocations.data[row.solarSystemID] = blue.DBRow(rowDescriptor, [row.solarSystemID,
             row.solarSystemName,
             row.x,
             row.y,
             -row.z])

        for row in stations:
            self.evelocations.data[row.stationID] = blue.DBRow(rowDescriptor, [row.stationID,
             row.stationName,
             row.x,
             row.y,
             -row.z])





class InvGroup(Row):
    __guid__ = 'sys.InvGroup'

    def Parent(self):
        return cfg.invgroups.Get(self.parentID)



    def Category(self):
        return cfg.invcategories.Get(self.categoryID)



    def Types(self):
        data = []
        for t in cfg.invtypes:
            if t.groupID == self.id:
                data.append(t.line)

        ret = Recordset(InvType, 'typeID', (cfg.invtypes.header, data))
        try:
            ret.Get(-1)
        except KeyError:
            sys.exc_clear()
        return ret



    def __getattr__(self, name):
        if name == '_groupName':
            return Row.__getattr__(self, 'groupName')
        if name == 'name':
            name = 'groupName'
        value = Row.__getattr__(self, name)
        if name == 'groupName':
            return Tr(value, 'inventory.groups.groupName', self.dataID)
        return value



    def __str__(self):
        try:
            cat = self.Category()
            return 'InvGroup ID: %d, category: %d %s,  "%s"' % (self.groupID,
             cat.id,
             cat.name,
             self.groupName)
        except:
            sys.exc_clear()
            return 'InvGroup containing crappy data'




class InvCategory(Row):
    __guid__ = 'sys.InvCategory'

    def __getattr__(self, name):
        if name == '_categoryName':
            return Row.__getattr__(self, 'categoryName')
        if name == 'name' or name == 'description':
            name = 'categoryName'
        value = Row.__getattr__(self, name)
        if name == 'categoryName':
            return Tr(value, 'inventory.categories.categoryName', self.dataID)
        return value



    def __str__(self):
        return 'InvCategory ID: %d,   "%s"' % (self.categoryID, self.categoryName)



    def IsHardware(self):
        return self.id == const.categoryModule or self.id == const.categoryImplant or self.id == const.categorySubSystem




class InvType(Row):
    __guid__ = 'sys.InvType'

    def Category(self):
        return cfg.invcategories.Get(self.categoryID)



    def Group(self):
        return cfg.invgroups.Get(self.groupID)



    def Graphic(self):
        try:
            if self.graphicID is not None:
                return cfg.graphics.Get(self.graphicID)
            else:
                return 
        except Exception:
            return 



    def GraphicFile(self):
        try:
            return cfg.graphics.Get(self.graphicID).graphicFile
        except Exception:
            return ''



    def Icon(self):
        try:
            if self.iconID is not None:
                return cfg.icons.Get(self.iconID)
            else:
                return 
        except Exception:
            return 



    def IconFile(self):
        try:
            return cfg.icons.Get(self.iconID).iconFile
        except Exception:
            return ''



    def Sound(self):
        try:
            if self.soundID is not None:
                return cfg.sounds.Get(self.soundID)
            else:
                return 
        except Exception:
            return 



    def Illegality(self, factionID = None):
        if factionID:
            return cfg.invcontrabandFactionsByType.get(self.id, {}).get(factionID, None)
        else:
            return cfg.invcontrabandFactionsByType.get(self.id, {})



    def HardwareType(self):
        raise RuntimeError('Not implemented at the moment')



    def ShipType(self):
        return cfg.shiptypes.Get(self.id)



    def __getattr__(self, name):
        if name == '_typeName':
            return Row.__getattr__(self, 'typeName')
        else:
            if name == 'name':
                name = 'typeName'
            if name == 'categoryID':
                return cfg.invgroups.Get(self.groupID).categoryID
            value = Row.__getattr__(self, name)
            if name == 'typeName':
                return Tr(value, 'inventory.types.typeName', self.dataID)
            if name == 'description':
                return Tr(value, 'inventory.types.description', self.dataID)
            return value



    def __str__(self):
        return 'InvType ID: %d, group: %d,  "%s"' % (self.typeID, self.groupID, self.typeName)




def StackSize(item):
    if item[const.ixQuantity] < 0:
        return 1
    return item[const.ixQuantity]



def Singleton(item):
    if item[const.ixQuantity] < 0:
        return -item[const.ixQuantity]
    if 30000000 <= item[const.ixLocationID] < 40000000:
        return 1
    return 0



def RamActivityVirtualColumn(row):
    return cfg.ramaltypes.Get(row.assemblyLineTypeID).activityID



def IsSystem(ownerID):
    return ownerID <= 10000



def IsNPC(ownerID):
    return ownerID < 90000000 and ownerID > 10000



def IsNPCCorporation(ownerID):
    return ownerID < 2000000 and ownerID >= 1000000



def IsNPCCharacter(ownerID):
    return ownerID < 4000000 and ownerID >= 3000000



def IsSystemOrNPC(ownerID):
    return ownerID < 90000000



def IsFaction(ownerID):
    if ownerID >= 500000 and ownerID < 1000000:
        return 1
    else:
        return 0



def IsCorporation(ownerID):
    if ownerID >= 1000000 and ownerID < 2000000:
        return 1
    else:
        if ownerID < 98000000 or ownerID > 2147483647:
            return 0
        if boot.role == 'server' and sm.GetService('standing2').IsKnownToBeAPlayerCorp(ownerID):
            return 1
        return cfg.eveowners.Get(ownerID).IsCorporation()



def IsCharacter(ownerID):
    if ownerID >= 3000000 and ownerID < 4000000:
        return 1
    else:
        if ownerID < 90000000 or ownerID > 2147483647:
            return 0
        if boot.role == 'server' and sm.GetService('standing2').IsKnownToBeAPlayerCorp(ownerID):
            return 0
        return cfg.eveowners.Get(ownerID).IsCharacter()



def IsPlayerAvatar(itemID):
    return IsCharacter(itemID)



def IsOwner(ownerID, fetch = 1):
    if ownerID >= 500000 and ownerID < 1000000 or ownerID >= 1000000 and ownerID < 2000000 or ownerID >= 3000000 and ownerID < 4000000:
        return 1
    if IsNPC(ownerID):
        return 0
    if ownerID < 90000000 or ownerID > 2147483647:
        return 0
    if fetch:
        oi = cfg.eveowners.Get(ownerID)
        if oi.groupID in (const.groupCharacter, const.groupCorporation):
            return 1
        else:
            return 0
    else:
        return 0



def IsAlliance(ownerID):
    if ownerID < 99000000 or ownerID > 2147483647:
        return 0
    else:
        if boot.role == 'server' and sm.GetService('standing2').IsKnownToBeAPlayerCorp(ownerID):
            return 0
        return cfg.eveowners.Get(ownerID).IsAlliance()



def IsRegion(itemID):
    return itemID >= 10000000 and itemID < 20000000



def IsConstellation(itemID):
    return itemID >= 20000000 and itemID < 30000000



def IsSolarSystem(itemID):
    return itemID >= 30000000 and itemID < 40000000



def IsCelestial(itemID):
    return itemID >= 40000000 and itemID < 50000000



def IsWormholeSystem(itemID):
    return itemID >= const.mapWormholeSystemMin and itemID < const.mapWormholeSystemMax



def IsWormholeConstellation(constellationID):
    return constellationID >= const.mapWormholeConstellationMin and constellationID < const.mapWormholeConstellationMax



def IsWormholeRegion(regionID):
    return regionID >= const.mapWormholeRegionMin and regionID < const.mapWormholeRegionMax



def IsUniverseCelestial(itemID):
    return itemID >= const.minUniverseCelestial and itemID <= const.maxUniverseCelestial



def IsStargate(itemID):
    return itemID >= 50000000 and itemID < 60000000



def IsStation(itemID):
    return itemID >= 60000000 and itemID < 64000000



def IsWorldSpace(itemID):
    return itemID >= const.mapWorldSpaceMin and itemID < const.mapWorldSpaceMax



def IsOutpost(itemID):
    return itemID >= 61000000 and itemID < 64000000



def IsTrading(itemID):
    return itemID >= 64000000 and itemID < 66000000



def IsOfficeFolder(itemID):
    return itemID >= 66000000 and itemID < 68000000



def IsFactoryFolder(itemID):
    return itemID >= 68000000 and itemID < 70000000



def IsUniverseAsteroid(itemID):
    return itemID >= 70000000 and itemID < 80000000



def IsJunkLocation(locationID):
    if locationID >= 2000:
        return 0
    else:
        if locationID in (6, 8, 10, 23, 25):
            return 1
        if locationID > 1000 and locationID < 2000:
            return 1
        return 0



def IsControlBunker(itemID):
    return itemID >= 80000000 and itemID < 80100000



def IsPlayerItem(itemID):
    return itemID >= const.minPlayerItem and itemID < const.minFakeItem



def IsFakeItem(itemID):
    return itemID > const.minFakeItem



def IsNewbieSystem(itemID):
    default = [30002547,
     30001392,
     30002715,
     30003489,
     30005305,
     30004971,
     30001672,
     30002505,
     30000141,
     30003410,
     30005042,
     30001407]
    optional = [30001722,
     30002518,
     30003388,
     30003524,
     30005015,
     30010141,
     30011392,
     30011407,
     30011672,
     30012505,
     30012547,
     30012715,
     30013410,
     30013489,
     30014971,
     30015042,
     30015305,
     30020141,
     30021392,
     30021407,
     30021672,
     30022505,
     30022547,
     30022715,
     30023410,
     30023489,
     30024971,
     30025042,
     30025305,
     30030141,
     30031392,
     30031407,
     30031672,
     30032505,
     30032547,
     30032715,
     30033410,
     30033489,
     30034971,
     30035042,
     30035305,
     30040141,
     30041392,
     30041407,
     30041672,
     30042505,
     30042547,
     30042715,
     30043410,
     30043489,
     30044971,
     30045042,
     30045305]
    if boot.region == 'optic':
        return itemID in default + optional
    return itemID in default



def IsStructure(categoryID):
    return categoryID in (const.categorySovereigntyStructure, const.categoryStructure)



def IsOrbital(categoryID):
    return categoryID == const.categoryOrbital



def IsPreviewable(typeID):
    type = cfg.invtypes.GetIfExists(typeID)
    if type is None:
        return False
    groupID = type.groupID
    categoryID = type.categoryID
    return categoryID in const.previewCategories or groupID in const.previewGroups



def IsPlaceable(typeID):
    type = cfg.invtypes.GetIfExists(typeID)
    if type is None:
        return False
    return const.categoryPlaceables == type.categoryID



class EveOwners(Row):
    __guid__ = 'cfg.EveOwners'

    def __getattr__(self, name):
        if name == 'name' or name == 'description':
            name = 'ownerName'
        elif name == 'groupID':
            return cfg.invtypes.Get(self.typeID).groupID
        value = Row.__getattr__(self, name)
        if name == 'ownerName' and IsSystemOrNPC(self.ownerID):
            if self.IsFaction():
                return Tr(value, 'character.factions.factionName', self.ownerID)
            if self.IsCorporation():
                return Tr(value, 'corporation.npcCorporations.corporationName', self.ownerID)
            if self.IsCharacter():
                return Tr(value, 'character.npcCharacters.characterName', self.ownerID)
        return value



    def __str__(self):
        return 'EveOwner ID: %d, "%s"' % (self.ownerID, self.ownerName)



    def IsSystem(self):
        return self.ownerID <= 15



    def IsNPC(self):
        return IsNPC(self.ownerID)



    def IsCharacter(self):
        return self.groupID == const.groupCharacter



    def IsCorporation(self):
        return self.groupID == const.groupCorporation



    def IsAlliance(self):
        return self.typeID == const.typeAlliance



    def IsFaction(self):
        return self.groupID == const.groupFaction



    def Type(self):
        return cfg.invtypes.Get(self.typeID)



    def Group(self):
        return cfg.invgroups.Get(self.groupID)




class CrpTickerNames(Row):
    __guid__ = 'cfg.CrpTickerNames'

    def __getattr__(self, name):
        if name == 'name' or name == 'description':
            return self.tickerName
        else:
            return Row.__getattr__(self, name)



    def __str__(self):
        return 'CorpTicker ID: %d, "%s"' % (self.corporationID, self.tickerName)




class DgmAttribute(Row):
    __guid__ = 'cfg.DgmAttribute'

    def __getattr__(self, name):
        value = Row.__getattr__(self, name)
        if name == 'displayName':
            if len(value) == 0:
                value = self.attributeName
            value = Tr(value, 'dogma.attributes.displayName', self.dataID)
        return value




class DgmEffect(Row):
    __guid__ = 'cfg.DgmEffect'

    def __getattr__(self, name):
        value = Row.__getattr__(self, name)
        if name == 'displayName':
            if len(value) == 0:
                value = self.effectName
            value = Tr(value, 'dogma.effects.displayName', self.dataID)
        if name == 'description':
            value = Tr(value, 'dogma.effects.description', self.dataID)
        return value




class AllShortNames(Row):
    __guid__ = 'cfg.AllShortNames'

    def __getattr__(self, name):
        if name == 'name' or name == 'description':
            return self.shortName
        else:
            return Row.__getattr__(self, name)



    def __str__(self):
        return 'AllianceShortName ID: %d, "%s"' % (self.allianceID, self.shortName)




class EveLocations(Row):
    __guid__ = 'dbrow.Location'

    def __getattr__(self, name):
        if name == 'name' or name == 'description':
            name = 'locationName'
        value = Row.__getattr__(self, name)
        return value



    def __str__(self):
        return 'EveLocation ID: %d, "%s"' % (self.locationID, self.locationName)



    def Station(self):
        return cfg.GetSvc('stationSvc').GetStation(self.id)




class RamCompletedStatus(Row):
    __guid__ = 'cfg.RamCompletedStatus'

    def __getattr__(self, name):
        if name == 'name':
            name = 'completedStatusText'
        value = Row.__getattr__(self, name)
        if name == 'completedStatusText':
            value = Tr(value, 'dbo.ramCompletedStatuses.completedStatusText', self.completedStatus)
        elif name == 'description':
            return Tr(value, 'dbo.ramCompletedStatuses.description', self.completedStatus)
        return value



    def __str__(self):
        try:
            return 'RamCompletedStatus ID: %d, "%s"' % (self.completedStatus, self.completedStatusText)
        except:
            sys.exc_clear()
            return 'RamCompletedStatus containing crappy data'




class RamActivity(Row):
    __guid__ = 'cfg.RamActivity'

    def __getattr__(self, name):
        if name == 'name':
            name = 'activityName'
        value = Row.__getattr__(self, name)
        if name == 'activityName':
            value = Tr(value, 'dbo.ramActivities.activityName', self.activityID)
        elif name == 'description':
            return Tr(value, 'dbo.ramActivities.description', self.activityID)
        return value



    def __str__(self):
        try:
            return 'RamActivity ID: %d, "%s"' % (self.activityID, self.activityName)
        except:
            sys.exc_clear()
            return 'RamActivity containing crappy data'




class MapCelestialDescription(Row):
    __guid__ = 'cfg.MapCelestialDescription'

    def __getattr__(self, name):
        value = Row.__getattr__(self, name)
        if name == 'description':
            value = Tr(value, 'map.itemDescriptions.description', self.dataID)
        return value



    def __str__(self):
        return 'MapCelestialDescriptions ID: %d' % self.itemID




class InvMetaGroup(Row):
    __guid__ = 'cfg.InvMetaGroup'

    def __getattr__(self, name):
        if name == '_metaGroupName':
            return Row.__getattr__(self, 'metaGroupName')
        if name == 'name':
            name = 'metaGroupName'
        value = Row.__getattr__(self, name)
        if name == 'metaGroupName':
            return Tr(value, 'inventory.metaGroups.metaGroupName', self.dataID)
        return value



    def __str__(self):
        try:
            cat = self.Category()
            return 'InvMetaGroup ID: %d, "%s"' % (self.groupID,
             cat.id,
             cat.name,
             self.metaGroupName)
        except:
            sys.exc_clear()
            return 'InvMetaGroup containing crappy data'




class Certificate(Row):
    __guid__ = 'cfg.Certificate'

    def __getattr__(self, name):
        value = Row.__getattr__(self, name)
        if name == 'description':
            value = Tr(value, 'cert.certificates.description', self.dataID)
        return value



    def __str__(self):
        return 'Certificate ID: %d' % self.certificateID




class Schematic(Row):
    __guid__ = 'cfg.Schematic'

    def __getattr__(self, name):
        value = Row.__getattr__(self, name)
        if name == 'schematicName':
            value = Tr(value, 'planet.schematics.schematicName', self.dataID)
        return value



    def __str__(self):
        return 'Schematic: %s (%d)' % (self.schematicName, self.schematicID)



    def __cmp__(self, other):
        if type(other) == types.IntType:
            return types.IntType.__cmp__(self.schematicID, other)
        else:
            return Row.__cmp__(self, other)




class Billtype(Row):
    __guid__ = 'cfg.Billtype'

    def __getattr__(self, name):
        value = Row.__getattr__(self, name)
        if name == 'billTypeName':
            value = Tr(value, 'accounting.billTypes.billTypeName', self.dataID)
        return value



    def __str__(self):
        return 'Billtype ID: %d' % self.billTypeID




class InvItem2(Row):
    __guid__ = 'sys.InvItem2'

    def __init__(self, recordset, key, customfields = None):
        Row.__init__(self, recordset, key)
        self.__dict__['customfields'] = customfields



    def __getattr__(self, name):
        customfields = self.__dict__['customfields']
        if customfields is not None and name in customfields:
            fieldindex = customfields.index(name)
            return Row.__getattr__(self, 'customInfo')[fieldindex]
        else:
            return Row.__getattr__(self, name)



    def __repr__(self):
        ret = Row.__repr__(self)
        fields = self.customfields
        if fields is not None:
            for i in xrange(len(fields)):
                ret = ret + '%s:%s%s\r\n' % (fields[i], ' ' * (23 - len(fields[i])), self.__getattr__(fields[i]))

        return ret



    def Type(self):
        return cfg.invtypes.Get(self.typeID)



    def Group(self):
        return cfg.invgroups.Get(self.groupID)



    def Category(self):
        return cfg.invcategories.Get(self.categoryID)



    def Owner(self):
        return cfg.eveowners.Get(self.ownerID)



    def Location(self):
        return cfg.evelocations.Get(self.locationID)




class InvBall(InvItem2):

    def __init__(self, recordset, key, fields = []):
        InvItem2.__init__(self, recordset, key, ['x',
         'y',
         'z',
         'radius'] + fields)



    def __getattr__(self, name):
        if name == 'name':
            return cfg.evelocations.Get(self.itemID).name
        else:
            if name == 'description':
                return cfg.evelocations.Get(self.itemID).description
            return InvItem2.__getattr__(self, name)




class PropertyBag():

    def __init__(self):
        self.Reset()



    def LoadFromMoniker(self, moniker_dict):
        import base64
        import cPickle
        self.__dict__['bag'] = cPickle.loads(base64.decodestring(moniker_dict))



    def GetMoniker(self):
        import base64
        import cPickle
        tupl = (self.__guid__, base64.encodestring(cPickle.dumps(self.__dict__['bag'])))
        return base64.encodestring(cPickle.dumps(tupl, 1)).rstrip()



    def AddProperty(self, propertyName, propertyValue):
        self.__dict__['bag'][propertyName] = propertyValue



    def HasProperty(self, propertyName):
        return self.__dict__['bag'].has_key(propertyName)



    def GetProperty(self, propertyName):
        if self.__dict__['bag'].has_key(propertyName):
            return self.__dict__['bag'][propertyName]



    def RemoveProperty(self, propertyName):
        if self.__dict__['bag'].has_key(propertyName):
            del self.__dict__['bag'][propertyName]



    def GetProperties(self):
        return self.__dict__['bag'].items()



    def Reset(self):
        self.__dict__['bag'] = {}




class OrderTypeInfo():
    __guid__ = 'util.OrderTypeInfo'
    __passbyvalue__ = 1

    def __init__(self, typeID, subTypeID = None):
        self.SetBlueprintInfo(typeID)
        self.subTypeID = subTypeID
        self.isBlueprint = self.IsBlueprint()
        self.isVoucher = self.IsVoucher()



    def SetBlueprintInfo(self, typeID, productivityLevel = 0, materialLevel = 0, isCopy = 1):
        self.typeID = typeID
        self.productivityLevel = productivityLevel
        self.materialLevel = materialLevel
        self.isCopy = isCopy



    def IsVoucher(self):
        return cfg.invtypes.Get(self.typeID).groupID == const.groupVoucher



    def IsBlueprint(self):
        return cfg.invtypes.Get(self.typeID).categoryID == const.categoryBlueprint



    def ItemMeetsRequirements(self, item, info):
        if self.IsVoucher():
            if not hasattr(item, '__vouchertype__'):
                raise RuntimeError('ItemNeedsToBeAVoucherIfItIsAVoucher')
            vti = item.GetTypeInfo()
            myvti = (self.typeID, self.subTypeID)
            return vti == myvti
        if self.IsBlueprint():
            if self.typeID != item.typeID:
                return 0
            if item.categoryID == const.categoryBlueprint:
                materialLevelRequired = self.materialLevel
                productivityLevelRequired = self.productivityLevel
                isCopy = self.isCopy
            if materialLevelRequired == 0 and productivityLevelRequired == 0 and isCopy != 1:
                return 1
            if not info:
                raise RuntimeError('PassTheBlueprintInfoInParam_info')
            isCopy = self.isCopy
            if isCopy is not None:
                if info.isCopy and isCopy == 0:
                    return 0
            if info.materialLevel >= materialLevelRequired and info.productivityLevel >= productivityLevelRequired:
                return 1
        raise RuntimeError('Slowness comparison detected')



    def GetDescription(self):
        typeID = self.typeID
        subTypeID = self.subTypeID
        description = ''
        if self.IsVoucher():
            if typeID == const.typeCompanyShares:
                description = mls.COMMON_SHARES
                if subTypeID is not None:
                    description = mls.COMMON_SHARESDESCRIPTION % {'shares': cfg.eveowners.Get(subTypeID).name}
                return description
            if typeID == const.typeBookmark:
                description = mls.COMMON_BOOKMARK
                if subTypeID is not None:
                    description = '%s - %s' % (description, cfg.evelocations.Get(subTypeID).name)
                return description
            if typeID == const.typePlayerKill:
                description = mls.COMMON_KILL
                if subTypeID is not None:
                    description = '%s: %s' % (description, cfg.eveowners.Get(subTypeID).name)
                return description
        elif self.IsBlueprint():
            materialLevel = self.materialLevel
            productivityLevel = self.productivityLevel
            isCopy = self.isCopy
            description = cfg.invtypes.Get(typeID).name
            if productivityLevel:
                description = mls.COMMON_PRODUCTIVITYDESCRIPTION % {'type': description,
                 'prodLevel': productivityLevel}
            if materialLevel:
                description = mls.COMMON_MATERIALDESCRIPTION % {'type': description,
                 'matLevel': materialLevel}
            if isCopy is not None:
                description = mls.COMMON_COPYDESCRIPTION % {'type': description,
                 'isCopy': isCopy}
            return description
        if typeID is not None:
            return cfg.invtypes.Get(typeID).name



    def GetTypeKey(self):
        return (self.typeID, self.subTypeID)



    def __getstate__(self):
        if self.isBlueprint:
            return (self.typeID,
             self.productivityLevel,
             self.materialLevel,
             self.isCopy)
        if self.isVoucher:
            return (self.typeID, self.subTypeID)
        return self.typeID



    def __setstate__(self, state):
        if type(state) == type(0):
            self.__init__(state)
        elif len(state) == 2:
            self.__init__(*state)
        elif len(state) == 4:
            self.SetBlueprintInfo(*state)
            self.subTypeID = None
            self.isBlueprint = 1
            self.isVoucher = 0




class OverviewDefault(Row):
    __guid__ = 'sys.OverviewDefault'

    def __getattr__(self, name):
        if name == '_overviewName':
            return Row.__getattr__(self, 'overviewName')
        if name == 'name':
            name = 'overviewName'
        value = Row.__getattr__(self, name)
        if name == 'overviewName':
            return Tr(value, 'character.defaultOverviews.overviewName', self.dataID)
        return value




class Position(Row):
    __guid__ = 'cfg.Position'

    @property
    def latitude(self):
        return self.x



    @property
    def longitude(self):
        return self.y



    @property
    def radius(self):
        return self.z




def IsWarInHostileState(row):
    if not row.retracted or blue.os.GetTime() - row.retracted < 24 * const.HOUR:
        if blue.os.GetTime() - row.timeDeclared >= 24 * const.HOUR:
            return 1
    return 0



def IsWarActive(row):
    if not row.retracted or blue.os.GetTime() - row.retracted < 24 * const.HOUR:
        return 1
    return 0



def IsPolarisFrigate(typeID):
    return typeID in (const.typePolarisCenturion,
     const.typePolarisCenturionFrigate,
     const.typePolarisInspectorFrigate,
     const.typePolarisLegatusFrigate)



def GetReprocessingOptions(types):
    options = util.Rowset(['typeID', 'isRecyclable', 'isRefinable'])
    optionTypes = {}
    noneTypes = [const.typeCredits, const.typeBookmark, const.typeBiomass]
    noneGroups = [const.groupRookieship, const.groupMineral]
    noneCategories = [const.categoryBlueprint, const.categoryReaction]
    for key in types.iterkeys():
        typeID = key
        isRecyclabe = 0
        isRefinable = 0
        typeInfo = cfg.invtypes.Get(typeID)
        if typeID not in noneTypes and typeInfo.groupID not in noneGroups and typeInfo.categoryID not in noneCategories:
            if cfg.invtypematerials.has_key(typeID):
                materials = cfg.invtypematerials[typeID]
                if len(materials) > 0:
                    if typeInfo.categoryID == const.categoryAsteroid or typeInfo.groupID == const.groupHarvestableCloud:
                        isRefinable = 1
                    else:
                        isRecyclabe = 1
        options.lines.append([typeID, isRecyclabe, isRefinable])

    for option in options:
        optionTypes[option.typeID] = option

    return optionTypes



def MakeConstantName(val, prefix):
    name = val.replace(' ', '')
    if name == '':
        name = 'invalidName_' + val
    name = prefix + name[0].upper() + name[1:]
    ret = ''
    okey = range(ord('a'), ord('z') + 1) + range(ord('A'), ord('Z') + 1) + range(ord('0'), ord('9') + 1)
    for ch in name:
        if ord(ch) in okey:
            ret += ch

    if ret == '':
        ret = 'invalidName_' + ret
    elif ord(ret[0]) in range(ord('0'), ord('9') + 1):
        ret = '_' + ret
    return ret



def IsFlagSubSystem(flag):
    return flag >= const.flagSubSystemSlot0 and flag <= const.flagSubSystemSlot7



def GetShipFlagLocationName(flag):
    if flag >= const.flagHiSlot0 and flag <= const.flagHiSlot7:
        locationName = mls.UI_GENERIC_HIGHSLOT
    elif flag >= const.flagMedSlot0 and flag <= const.flagMedSlot7:
        locationName = mls.UI_GENERIC_MEDSLOT
    elif flag >= const.flagLoSlot0 and flag <= const.flagLoSlot7:
        locationName = mls.UI_GENERIC_LOWSLOT
    elif flag >= const.flagRigSlot0 and flag <= const.flagRigSlot7:
        locationName = mls.UI_GENERIC_RIGSLOT
    elif flag >= const.flagSubSystemSlot0 and flag <= const.flagSubSystemSlot7:
        locationName = mls.UI_GENERIC_SUBSYSTEM
    elif flag == const.flagCargo:
        locationName = mls.UI_GENERIC_CARGO
    elif flag == const.flagDroneBay:
        locationName = mls.UI_GENERIC_DRONEBAY
    elif flag == const.flagShipHangar:
        locationName = mls.UI_GENERIC_SHIPBAY
    elif flag == const.flagHangar or flag >= const.flagCorpSAG2 and flag <= const.flagCorpSAG7:
        locationName = mls.UI_GENERIC_CORPHANGAR
    elif flag == const.flagSpecializedFuelBay:
        locationName = mls.UI_GENERIC_FUELBAY
    elif flag == const.flagSpecializedOreHold:
        locationName = mls.UI_GENERIC_OREHOLD
    elif flag == const.flagSpecializedGasHold:
        locationName = mls.UI_GENERIC_GASHOLD
    elif flag == const.flagSpecializedMineralHold:
        locationName = mls.UI_GENERIC_MINERALHOLD
    elif flag == const.flagSpecializedSalvageHold:
        locationName = mls.UI_GENERIC_SALVAGEHOLD
    elif flag == const.flagSpecializedShipHold:
        locationName = mls.UI_GENERIC_SHIPHOLD
    elif flag == const.flagSpecializedSmallShipHold:
        locationName = mls.UI_GENERIC_SMALLSHIPHOLD
    elif flag == const.flagSpecializedMediumShipHold:
        locationName = mls.UI_GENERIC_MEDIUMSHIPHOLD
    elif flag == const.flagSpecializedLargeShipHold:
        locationName = mls.UI_GENERIC_LARGESHIPHOLD
    elif flag == const.flagSpecializedIndustrialShipHold:
        locationName = mls.UI_GENERIC_INDUSTRIALSHIPHOLD
    elif flag == const.flagSpecializedAmmoHold:
        locationName = mls.UI_GENERIC_AMMOHOLD
    else:
        locationName = ''
    return locationName



def GetPlanetWarpInPoint(planetID, locVec, r):
    dx = float(locVec[0])
    dz = float(locVec[2])
    f = float(dz) / float(math.sqrt(dx ** 2 + dz ** 2))
    if dz > 0 and dx > 0 or dz < 0 and dx > 0:
        f *= -1.0
    theta = math.asin(f)
    myRandom = random.Random(planetID)
    rr = (myRandom.random() - 1.0) / 3.0
    theta += rr
    offset = 1000000
    FACTOR = 20.0
    dd = math.pow((FACTOR - 5.0 * math.log10(r / 1000000) - 0.5) / FACTOR, FACTOR) * FACTOR
    dd = min(10.0, max(0.0, dd))
    dd += 0.5
    offset += r * dd
    d = r + offset
    x = 1000000
    z = 0
    x = math.sin(theta) * d
    z = math.cos(theta) * d
    y = r * math.sin(rr) * 0.5
    return util.KeyVal(x=x, y=y, z=z)



def GraphicFile(graphicID):
    try:
        return cfg.graphics.Get(graphicID).graphicFile
    except Exception:
        return ''



def IconFile(iconID):
    try:
        return cfg.icons.Get(iconID).iconFile
    except Exception:
        return ''



def GetCurrencyTypeFromKey(accountKeyID):
    if accountKeyID in const.aurAccounts:
        return const.creditsAURUM
    else:
        if accountKeyID == const.accountingKeyDustMPlex:
            return const.creditsDustMPLEX
        return const.creditsISK



def GetActiveShip():
    if session.stationid2:
        shipID = sm.GetService('clientDogmaIM').GetDogmaLocation().shipID
    else:
        shipID = session.shipid
    return shipID


exports = {'util.GraphicFile': GraphicFile,
 'util.IconFile': IconFile,
 'util.StackSize': StackSize,
 'util.Singleton': Singleton,
 'util.RamActivityVirtualColumn': RamActivityVirtualColumn,
 'util.IsNPC': IsNPC,
 'util.IsSystem': IsSystem,
 'util.IsSystemOrNPC': IsSystemOrNPC,
 'util.IsFaction': IsFaction,
 'util.IsCorporation': IsCorporation,
 'util.IsCharacter': IsCharacter,
 'util.IsPlayerAvatar': IsPlayerAvatar,
 'util.IsOwner': IsOwner,
 'util.IsRegion': IsRegion,
 'util.IsConstellation': IsConstellation,
 'util.IsSolarSystem': IsSolarSystem,
 'util.IsCelestial': IsCelestial,
 'util.IsWormholeSystem': IsWormholeSystem,
 'util.IsWormholeConstellation': IsWormholeConstellation,
 'util.IsWormholeRegion': IsWormholeRegion,
 'util.IsNewbieSystem': IsNewbieSystem,
 'util.IsUniverseCelestial': IsUniverseCelestial,
 'util.IsStargate': IsStargate,
 'util.IsStation': IsStation,
 'util.IsWorldSpace': IsWorldSpace,
 'util.IsStructure': IsStructure,
 'util.IsOutpost': IsOutpost,
 'util.IsTrading': IsTrading,
 'util.IsOfficeFolder': IsOfficeFolder,
 'util.IsFactoryFolder': IsFactoryFolder,
 'util.IsUniverseAsteroid': IsUniverseAsteroid,
 'util.IsJunkLocation': IsJunkLocation,
 'util.IsControlBunker': IsControlBunker,
 'util.IsPlayerItem': IsPlayerItem,
 'util.IsFakeItem': IsFakeItem,
 'util.IsPreviewable': IsPreviewable,
 'util.CanUseAgent': CanUseAgent,
 'util.IsWarInHostileState': IsWarInHostileState,
 'util.IsWarActive': IsWarActive,
 'util.IsAlliance': IsAlliance,
 'util.IsPolarisFrigate': IsPolarisFrigate,
 'util.GetReprocessingOptions': GetReprocessingOptions,
 'util.MakeConstantName': MakeConstantName,
 'util.IsFlagSubSystem': IsFlagSubSystem,
 'util.GetShipFlagLocationName': GetShipFlagLocationName,
 'util.GetPlanetWarpInPoint': GetPlanetWarpInPoint,
 'util.IsPlaceable': IsPlaceable,
 'util.IsOrbital': IsOrbital,
 'util.GetCurrencyTypeFromKey': GetCurrencyTypeFromKey,
 'util.GetActiveShip': GetActiveShip,
 'util.DgmAttribute': DgmAttribute,
 'util.DgmEffect': DgmEffect}

