import blue
import util
import sys
import types
import random
import copy
import svc
import const
import service
import dbutil
import macho
import math
import localization
import localizationUtil
import re
globals().update(service.consts)
from sys import *
import standingUtil
OWNER_AURA_IDENTIFIER = -1
OWNER_SYSTEM_IDENTIFIER = -2

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
        __builtin__.OWNERID = const.UE_OWNERID
        __builtin__.LOCID = const.UE_LOCID
        __builtin__.TYPEID = const.UE_TYPEID
        __builtin__.TYPEID2 = const.UE_TYPEID2
        __builtin__.TYPEIDL = const.UE_TYPEIDL
        __builtin__.BPTYPEID = const.UE_BPTYPEID
        __builtin__.GROUPID = const.UE_GROUPID
        __builtin__.GROUPID2 = const.UE_GROUPID2
        __builtin__.CATID = const.UE_CATID
        __builtin__.CATID2 = const.UE_CATID2
        __builtin__.DGMATTR = const.UE_DGMATTR
        __builtin__.DGMFX = const.UE_DGMFX
        __builtin__.DGMTYPEFX = const.UE_DGMTYPEFX
        __builtin__.AMT = const.UE_AMT
        __builtin__.AMT2 = const.UE_AMT2
        __builtin__.AMT3 = const.UE_AMT3
        __builtin__.DIST = const.UE_DIST
        __builtin__.TYPEIDANDQUANTITY = const.UE_TYPEIDANDQUANTITY
        __builtin__.OWNERIDNICK = const.UE_OWNERIDNICK
        __builtin__.ISK = const.UE_ISK
        __builtin__.AUR = const.UE_AUR



    def _CreateConfig(self):
        return EveConfig()




class EveConfig(util.config):
    __guid__ = 'util.EveConfig'

    def __init__(self):
        util.config.__init__(self)
        self.fmtMapping[const.UE_OWNERID] = lambda value, value2: cfg.eveowners.Get(value).ownerName
        self.fmtMapping[const.UE_OWNERIDNICK] = lambda value, value2: cfg.eveowners.Get(value).ownerName.split(' ')[0]
        self.fmtMapping[const.UE_LOCID] = lambda value, value2: cfg.evelocations.Get(value).locationName
        self.fmtMapping[const.UE_TYPEID] = lambda value, value2: cfg.invtypes.Get(value).typeName
        self.fmtMapping[const.UE_TYPEID2] = lambda value, value2: cfg.invtypes.Get(value).description
        self.fmtMapping[const.UE_TYPEIDL] = lambda value, value2: cfg.FormatConvert(const.UE_LIST, [ (const.UE_TYPEID, x) for x in value ], value2)
        self.fmtMapping[const.UE_BPTYPEID] = lambda value, value2: cfg.invbptypes.Get(value).blueprintTypeName
        self.fmtMapping[const.UE_GROUPID] = lambda value, value2: cfg.invgroups.Get(value).groupName
        self.fmtMapping[const.UE_GROUPID2] = lambda value, value2: cfg.invgroups.Get(value).description
        self.fmtMapping[const.UE_CATID] = lambda value, value2: cfg.invcategories.Get(value).categoryName
        self.fmtMapping[const.UE_CATID2] = lambda value, value2: cfg.invcategories.Get(value).description
        self.fmtMapping[const.UE_AMT] = lambda value, value2: util.FmtAmt(value)
        self.fmtMapping[const.UE_AMT2] = lambda value, value2: util.FmtISK(value)
        self.fmtMapping[const.UE_AMT3] = lambda value, value2: util.FmtISK(value)
        self.fmtMapping[const.UE_ISK] = lambda value, value2: util.FmtISK(value)
        self.fmtMapping[const.UE_AUR] = lambda value, value2: util.FmtAUR(value)
        self.fmtMapping[const.UE_DIST] = lambda value, value2: util.FmtDist(value)
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
        self.nebulas = None
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
        self.messages = None



    def GetStartupData(self):
        util.config.GetStartupData(self)
        if boot.role == 'client':
            self.messages = self.LoadBulkIndex('messages', const.cacheEveMessages, 'messageKey')



    def GetMessage(self, key, dict = None, onNotFound = 'return', onDictMissing = 'error'):
        try:
            msg = self.messages.data[key]
        except KeyError:
            if key != 'ErrMessageNotFound':
                return self.GetMessage('ErrMessageNotFound', {'msgid': key,
                 'args': dict})
            else:
                return util.KeyVal(text='Could not find message with key ' + key + '. This is most likely due to a missing or outdatad 10000001.cache2 bulkdata file, or the message is missing.', title='Message not found', type='fatal', audio='', icon='', suppress=False)
        (bodyID, titleID,) = (msg.bodyID, msg.titleID)
        if dict is not None and dict != -1:
            dict = self._EveConfig__prepdict(dict)
            title = localization.GetByMessageID(titleID, **dict) if titleID is not None else None
            text = localization.GetByMessageID(bodyID, **dict) if bodyID is not None else None
        else:
            title = localization.GetByMessageID(titleID) if titleID is not None else None
            text = localization.GetByMessageID(bodyID) if bodyID is not None else None
        return util.KeyVal(text=text, title=title, type=msg.messageType, audio=msg.urlAudio, icon=msg.urlIcon, suppress=msg.suppressable)



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
                volume = sm.GetService('invCache').GetInventoryFromId(item.itemID).GetCapacity().used
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
        configSvc.RegisterTablesForUpdates()



    def ReportLoginProgress(self, section, stepNum, totalSteps = None):
        if totalSteps is not None:
            self.totalLogonSteps = totalSteps
        if macho.mode == 'client':
            sm.ScatterEvent('OnProcessLoginProgress', 'loginprogress::gettingbulkdata', section, stepNum, self.totalLogonSteps)
        else:
            cfg.LogInfo(section, stepNum)



    def GotInitData(self, initdata):
        cfg.LogInfo('App GotInitData')
        util.config.GotInitData(self, initdata)
        self.dgmunits = self.LoadBulkIndex('dgmunits', const.cacheDogmaUnits, 'unitID')
        self.invbptypes = self.LoadBulkIndex('invbptypes', const.cacheInvBlueprintTypes, 'blueprintTypeID')
        self.invcategories = self.LoadBulkIndex('invcategories', const.cacheInvCategories, 'categoryID', InvCategory)
        self.invmetagroups = self.LoadBulkIndex('invmetagroups', const.cacheInvMetaGroups, 'metaGroupID', InvMetaGroup)
        self.invgroups = self.LoadBulkIndex('invgroups', const.cacheInvGroups, 'groupID', InvGroup)
        self.invtypes = self.LoadBulkIndex('invtypes', const.cacheInvTypes, 'typeID', InvType)
        self.invtypereactions = self.LoadBulkFilter('invtypereactions', const.cacheInvTypeReactions, 'reactionTypeID')
        self.invmetatypes = self.LoadBulkIndex('invmetatypes', const.cacheInvMetaTypes, 'typeID')
        self.invmetatypesByParent = self.LoadBulkFilter('invmetatypesByParent', const.cacheInvMetaTypes, 'parentTypeID')
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

        self.dgmattribs = self.LoadBulkIndex('dgmattribs', const.cacheDogmaAttributes, 'attributeID', DgmAttribute)
        self.dgmeffects = self.LoadBulkIndex('dgmeffects', const.cacheDogmaEffects, 'effectID', DgmEffect)
        self.dgmtypeattribs = self.LoadBulkFilter('dgmtypeattribs', const.cacheDogmaTypeAttributes, 'typeID')
        self.dgmtypeeffects = self.LoadBulkFilter('dgmtypeeffects', const.cacheDogmaTypeEffects, 'typeID')
        self.dgmexpressions = self.LoadBulkIndex('dgmexpressions', const.cacheDogmaExpressions, 'expressionID')
        self.shiptypes = self.LoadBulkIndex('shiptypes', const.cacheShipTypes, 'shipTypeID')
        self.ramaltypes = self.LoadBulkIndex('ramaltypes', const.cacheRamAssemblyLineTypes, 'assemblyLineTypeID')
        self.ramaltypesdetailpercategory = self.LoadBulkFilter('ramaltypesdetailpercategory', const.cacheRamAssemblyLineTypesCategory, 'assemblyLineTypeID', virtualColumns=[('activityID', RamActivityVirtualColumn)])
        self.ramaltypesdetailpergroup = self.LoadBulkFilter('ramaltypesdetailpergroup', const.cacheRamAssemblyLineTypesGroup, 'assemblyLineTypeID', virtualColumns=[('activityID', RamActivityVirtualColumn)])
        self.ramactivities = self.LoadBulkIndex('ramactivities', const.cacheRamActivities, 'activityID', RamActivity)
        self.ramcompletedstatuses = self.LoadBulkIndex('ramcompletedstatuses', const.cacheRamCompletedStatuses, 'completedStatus', RamCompletedStatus)
        self.invtypematerials = self.LoadBulkFilter('invtypematerials', const.cacheInvTypeMaterials, 'typeID')
        ramtyperequirements = self.LoadBulk('ramtyperequirements', const.cacheRamTypeRequirements)
        d = {}
        for row in ramtyperequirements:
            key = (row.typeID, row.activityID)
            if key in d:
                d[key].append(row)
            else:
                d[key] = [row]

        self.ramtyperequirements = d
        self.mapcelestialdescriptions = self.LoadBulkIndex('mapcelestialdescriptions', const.cacheMapCelestialDescriptions, 'itemID', MapCelestialDescription)
        self.certificates = self.LoadBulkIndex('certificates', const.cacheCertificates, 'certificateID', Certificate)
        self.certificaterelationships = self.LoadBulkIndex('certificaterelationships', const.cacheCertificateRelationships, 'relationshipID')
        self.certificateRelationshipsByChildID = self.LoadBulkIndex('certificateRelationshipsByChildID', const.cacheCertificateRelationships, 'relationshipID')
        self.locationwormholeclasses = self.LoadBulkIndex('locationwormholeclasses', const.cacheMapLocationWormholeClasses, 'locationID')
        self.nebulas = self.LoadBulkIndex('nebulas', const.cacheMapNebulas, 'locationID')
        self.schematics = self.LoadBulkIndex('schematics', const.cachePlanetSchematics, 'schematicID', Schematic)
        self.schematicstypemap = self.LoadBulkFilter('schematicstypemap', const.cachePlanetSchematicsTypeMap, 'schematicID')
        self.schematicspinmap = self.LoadBulkFilter('schematicspinmap', const.cachePlanetSchematicsPinMap, 'schematicID')
        self.schematicsByPin = self.LoadBulkFilter('schematicsByPin', const.cachePlanetSchematicsPinMap, 'pinTypeID')
        self.schematicsByType = self.LoadBulkFilter('schematicsByType', const.cachePlanetSchematicsTypeMap, 'typeID')
        self.groupsByCategories = self.LoadBulkFilter('groupsByCategories', const.cacheInvGroups, 'categoryID')
        self.typesByGroups = self.LoadBulkFilter('typesByGroups', const.cacheInvTypes, 'groupID')
        self.typesByMarketGroups = self.LoadBulkFilter('typesByMarketGroups', const.cacheInvTypes, 'marketGroupID')
        self.billtypes = self.LoadBulkIndex('billtypes', const.cacheActBillTypes, 'billTypeID', Billtype)
        self.overviewDefaults = self.LoadBulkIndex('overviewDefaults', const.cacheChrDefaultOverviews, 'overviewID', OverviewDefault)
        self.overviewDefaultGroups = self.LoadBulkFilter('overviewDefaultGroups', const.cacheChrDefaultOverviewGroups, 'overviewID')
        self.bloodlineNames = self.LoadBulkFilter('bloodlineNames', const.cacheChrBloodlineNames, 'bloodlineID')
        self.bloodlines = self.LoadBulkIndex('bloodlines', const.cacheChrBloodlines, 'bloodlineID')
        self.factions = self.LoadBulkIndex('factions', const.cacheChrFactions, 'factionID', Faction)
        self.races = self.LoadBulkIndex('races', const.cacheChrRaces, 'raceID')
        self.npccorporations = self.LoadBulkIndex('npccorporations', const.cacheCrpNpcCorporations, 'corporationID')
        self.corptickernames = self.LoadBulk('corptickernames', const.cacheCrpTickerNamesStatic, Recordset(CrpTickerNames, 'corporationID', 'GetCorpTickerNamesEx', 'GetMultiCorpTickerNamesEx'), tableID=const.cacheCrpNpcCorporations)
        self.messages = self.LoadBulkIndex('messages', const.cacheEveMessages, 'messageKey')
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
        return localization.GetByLabel('UI/Common/QuantityAndItem', quantity=quantity, item=typeID)



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




    def GetNebula(self, solarSystemID, constellationID, regionID, returnPath = True):
        try:
            try:
                graphicID = self.nebulas.Get(solarSystemID).graphicID
            except KeyError:
                try:
                    graphicID = self.nebulas.Get(constellationID).graphicID
                except KeyError:
                    try:
                        graphicID = self.nebulas.Get(regionID).graphicID
                    except KeyError:
                        graphicID = 0

        finally:
            if returnPath:
                return cfg.graphics.Get(graphicID).graphicFile
            return graphicID




    def LoadEveOwners(self):
        npccharacters = self.LoadBulkIndex(None, const.cacheChrNpcCharacters, 'characterID')
        rowDescriptor = blue.DBRowDescriptor((('ownerID', const.DBTYPE_I4),
         ('ownerName', const.DBTYPE_WSTR),
         ('typeID', const.DBTYPE_I2),
         ('gender', const.DBTYPE_I2),
         ('ownerNameID', const.DBTYPE_I4)))
        self.eveowners = Recordset(EveOwners, 'ownerID', 'GetOwnersEx', 'GetMultiOwnersEx')
        self.eveowners.header = ['ownerID',
         'ownerName',
         'typeID',
         'gender',
         'ownerNameID']
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
            self.eveowners.data[row.factionID] = blue.DBRow(rowDescriptor, [row.factionID,
             row.factionName,
             const.typeFaction,
             None,
             row.factionNameID])

        for row in self.npccorporations:
            self.eveowners.data[row.corporationID] = blue.DBRow(rowDescriptor, [row.corporationID,
             row.corporationName,
             const.typeCorporation,
             None,
             row.corporationNameID])

        for row in npccharacters:
            self.eveowners.data[row.characterID] = blue.DBRow(rowDescriptor, [row.characterID,
             row.characterName,
             bloodlinesToTypes[row.bloodlineID],
             row.gender,
             row.characterNameID])

        for i in const.auraAgentIDs:
            self.eveowners.data[i].ownerNameID = OWNER_AURA_IDENTIFIER

        self.eveowners.data[1] = blue.DBRow(rowDescriptor, [1,
         'EVE System',
         0,
         None,
         OWNER_SYSTEM_IDENTIFIER])



    def LoadEveLocations(self):
        self.regions = self.LoadBulkIndex('regions', const.cacheMapRegionsTable, 'regionID')
        self.constellations = self.LoadBulkIndex('constellations', const.cacheMapConstellationsTable, 'constellationID')
        self.solarsystems = self.LoadBulkIndex('solarsystems', const.cacheMapSolarSystemsTable, 'solarSystemID', SolarSystem)
        self.stations = self.LoadBulk('stations', const.cacheStaStationsStatic, Recordset(sys.Row, 'stationID', 'GetStationEx', 'GetMultiStationEx'))
        rowDescriptor = blue.DBRowDescriptor((('locationID', const.DBTYPE_I4),
         ('locationName', const.DBTYPE_WSTR),
         ('x', const.DBTYPE_R5),
         ('y', const.DBTYPE_R5),
         ('z', const.DBTYPE_R5),
         ('locationNameID', const.DBTYPE_I4)))
        self.evelocations = Recordset(EveLocations, 'locationID', 'GetLocationsEx', 'GetMultiLocationsEx')
        self.evelocations.header = ['locationID',
         'locationName',
         'x',
         'y',
         'z',
         'locationNameID']
        for row in self.regions:
            self.evelocations.data[row.regionID] = blue.DBRow(rowDescriptor, [row.regionID,
             row.regionName,
             row.x,
             row.y,
             row.z,
             None])

        for row in self.constellations:
            self.evelocations.data[row.constellationID] = blue.DBRow(rowDescriptor, [row.constellationID,
             row.constellationName,
             row.x,
             row.y,
             row.z,
             None])

        for row in self.solarsystems:
            self.evelocations.data[row.solarSystemID] = blue.DBRow(rowDescriptor, [row.solarSystemID,
             row.solarSystemName,
             row.x,
             row.y,
             row.z,
             None])

        for row in self.stations:
            self.evelocations.data[row.stationID] = blue.DBRow(rowDescriptor, [row.stationID,
             row.stationName,
             row.x,
             row.y,
             row.z,
             None])





def GetStrippedEnglishMessage(messageID):
    msg = localization.GetByMessageID(messageID, 'en-us')
    if msg:
        regex = '</localized>|<localized>|<localized .*?>|<localized *=.*?>'
        return ''.join(re.split(regex, msg))
    else:
        return ''



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
            return GetStrippedEnglishMessage(self.groupNameID)
        if name == 'name':
            name = 'groupName'
        value = Row.__getattr__(self, name)
        if name == 'groupName':
            return localization.GetByMessageID(self.groupNameID)
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
            return GetStrippedEnglishMessage(self.categoryNameID)
        if name == 'name' or name == 'description':
            name = 'categoryName'
        value = Row.__getattr__(self, name)
        if name == 'categoryName':
            return localization.GetByMessageID(self.categoryNameID)
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
            return GetStrippedEnglishMessage(self.typeNameID)
        else:
            if name == 'name':
                name = 'typeName'
            if name == 'categoryID':
                return cfg.invgroups.Get(self.groupID).categoryID
            if name == 'typeName':
                return localization.GetByMessageID(self.typeNameID)
            if name == 'description':
                return localization.GetByMessageID(self.descriptionID)
            return Row.__getattr__(self, name)



    def __str__(self):
        return 'InvType ID: %d, group: %d,  "%s"' % (self.typeID, self.groupID, self.typeName)




class SolarSystem(Row):
    __guid__ = 'sys.SolarSystem'

    def __getattr__(self, name):
        if name == 'pseudoSecurity':
            value = Row.__getattr__(self, 'security')
            if value > 0.0 and value < 0.05:
                return 0.05
            else:
                return value
        value = Row.__getattr__(self, name)
        return value



    def __str__(self):
        return 'SolarSystem ID: %d, name: %d' % (self.solarSystemID, self.solarSystemName)




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
    if ownerID < 90000000 or ownerID > 2147483647:
        return 0
    if boot.role == 'server' and sm.GetService('standing2').IsKnownToBeAPlayerCorp(ownerID):
        return 0
    try:
        return cfg.eveowners.Get(ownerID).IsCharacter()
    except KeyError:
        return 0



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



def IsEveUser(userID):
    if userID < const.minDustUser:
        return True
    return False



def IsDustUser(userID):
    if userID > const.minDustUser:
        return True
    return False



def IsDustCharacter(characterID):
    if characterID > const.minDustCharacter and characterID < const.maxDustCharacter:
        return True
    return False


OWNER_NAME_OVERRIDES = {OWNER_AURA_IDENTIFIER: 'UI/Agents/AuraAgentName',
 OWNER_SYSTEM_IDENTIFIER: 'UI/Chat/ChatEngine/EveSystem'}

class EveOwners(Row):
    __guid__ = 'cfg.EveOwners'

    def __getattr__(self, name):
        if name == 'name' or name == 'description':
            name = 'ownerName'
        elif name == 'groupID':
            return cfg.invtypes.Get(self.typeID).groupID
        if name == 'ownerName' and self.ownerNameID is not None:
            if self.ownerNameID > 0:
                value = localization.GetByMessageID(self.ownerNameID)
            else:
                value = localization.GetByLabel(OWNER_NAME_OVERRIDES[self.ownerNameID])
        else:
            value = Row.__getattr__(self, name)
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
            value = localization.GetByMessageID(self.displayNameID)
        return value




class DgmEffect(Row):
    __guid__ = 'cfg.DgmEffect'

    def __getattr__(self, name):
        if name == 'displayName':
            return localization.GetByMessageID(self.displayNameID)
        if name == 'description':
            return localization.GetByMessageID(self.descriptionID)
        return Row.__getattr__(self, name)




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
        if name == 'locationName' and self.locationNameID is not None:
            if isinstance(self.locationNameID, (int, long)):
                return localization.GetByMessageID(self.locationNameID)
            if isinstance(self.locationNameID, tuple):
                return localization.GetByLabel(self.locationNameID[0], **self.locationNameID[1])
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
            value = localization.GetByMessageID(self.completedStatusTextID)
        elif name == 'description':
            return localization.GetByMessageID(self.descriptionID)
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
        if name in ('activityName', 'name'):
            return localization.GetByMessageID(self.activityNameID)
        if name == 'description':
            return localization.GetByMessageID(self.descriptionID)
        return Row.__getattr__(self, name)



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
            value = localization.GetByMessageID(self.descriptionID)
        return value



    def __str__(self):
        return 'MapCelestialDescriptions ID: %d' % self.itemID




class InvMetaGroup(Row):
    __guid__ = 'cfg.InvMetaGroup'

    def __getattr__(self, name):
        if name == '_metaGroupName':
            return GetStrippedEnglishMessage(self.metaGroupNameID)
        if name == 'name':
            name = 'metaGroupName'
        value = Row.__getattr__(self, name)
        if name == 'metaGroupName':
            return localization.GetByMessageID(self.metaGroupNameID)
        return value



    def __str__(self):
        try:
            cat = self.Category()
            return 'InvMetaGroup ID: %d, "%s", "%s", "%s"' % (self.metaGroupID,
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
            value = localization.GetByMessageID(self.descriptionID)
        return value



    def __str__(self):
        return 'Certificate ID: %d' % self.certificateID




class Schematic(Row):
    __guid__ = 'cfg.Schematic'

    def __getattr__(self, name):
        if name == 'schematicName':
            return localization.GetByMessageID(self.schematicNameID)
        return Row.__getattr__(self, name)



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
            value = localization.GetByMessageID(self.billTypeNameID)
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




class OverviewDefault(Row):
    __guid__ = 'sys.OverviewDefault'

    def __getattr__(self, name):
        if name == '_overviewName':
            return Row.__getattr__(self, 'overviewName')
        if name in ('name', 'overviewName'):
            return localization.GetByMessageID(self.overviewNameID)
        value = Row.__getattr__(self, name)
        return value



    def __str__(self):
        return 'DefaultOverview ID: %d, "%s"' % (self.overviewID, self.overviewName)




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




class Faction(Row):
    __guid__ = 'cfg.Faction'

    def __getattr__(self, name):
        if name == 'factionName':
            return localization.GetByMessageID(self.factionNameID)
        return Row.__getattr__(self, name)




def IsWarInHostileState(row):
    if not row.retracted or blue.os.GetWallclockTime() - row.retracted < 24 * const.HOUR:
        if blue.os.GetWallclockTime() - row.timeDeclared >= 24 * const.HOUR:
            return 1
    return 0



def IsWarActive(row):
    if not row.retracted or blue.os.GetWallclockTime() - row.retracted < 24 * const.HOUR:
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
            if typeID in cfg.invtypematerials:
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
        locationName = localization.GetByLabel('UI/Ship/HighSlot')
    elif flag >= const.flagMedSlot0 and flag <= const.flagMedSlot7:
        locationName = localization.GetByLabel('UI/Ship/MediumSlot')
    elif flag >= const.flagLoSlot0 and flag <= const.flagLoSlot7:
        locationName = localization.GetByLabel('UI/Ship/LowSlot')
    elif flag >= const.flagRigSlot0 and flag <= const.flagRigSlot7:
        locationName = localization.GetByLabel('UI/Ship/RigSlot')
    elif flag >= const.flagSubSystemSlot0 and flag <= const.flagSubSystemSlot7:
        locationName = localization.GetByLabel('UI/Ship/Subsystem')
    elif flag == const.flagCargo:
        locationName = localization.GetByLabel('UI/Ship/CargoHold')
    elif flag == const.flagDroneBay:
        locationName = localization.GetByLabel('UI/Ship/DroneBay')
    elif flag == const.flagShipHangar:
        locationName = localization.GetByLabel('UI/Ship/ShipMaintenanceBay')
    elif flag == const.flagHangar or flag >= const.flagCorpSAG2 and flag <= const.flagCorpSAG7:
        locationName = localization.GetByLabel('UI/Corporations/Common/CorporateHangar')
    elif flag == const.flagSpecializedFuelBay:
        locationName = localization.GetByLabel('UI/Ship/FuelBay')
    elif flag == const.flagSpecializedOreHold:
        locationName = localization.GetByLabel('UI/Ship/OreHold')
    elif flag == const.flagSpecializedGasHold:
        locationName = localization.GetByLabel('UI/Ship/GasHold')
    elif flag == const.flagSpecializedMineralHold:
        locationName = localization.GetByLabel('UI/Ship/MineralHold')
    elif flag == const.flagSpecializedSalvageHold:
        locationName = localization.GetByLabel('UI/Ship/SalvageHold')
    elif flag == const.flagSpecializedShipHold:
        locationName = localization.GetByLabel('UI/Ship/ShipHold')
    elif flag == const.flagSpecializedSmallShipHold:
        locationName = localization.GetByLabel('UI/Ship/SmallShipHold')
    elif flag == const.flagSpecializedMediumShipHold:
        locationName = localization.GetByLabel('UI/Ship/MediumShipHold')
    elif flag == const.flagSpecializedLargeShipHold:
        locationName = localization.GetByLabel('UI/Ship/LargeShipHold')
    elif flag == const.flagSpecializedIndustrialShipHold:
        locationName = localization.GetByLabel('UI/Ship/IndustrialShipHold')
    elif flag == const.flagSpecializedAmmoHold:
        locationName = localization.GetByLabel('UI/Ship/AmmoHold')
    elif flag == const.flagSpecializedCommandCenterHold:
        locationName = localization.GetByLabel('UI/Ship/CommandCenterHold')
    elif flag == const.flagSpecializedPlanetaryCommoditiesHold:
        locationName = localization.GetByLabel('UI/Ship/PlanetaryCommoditiesHold')
    elif flag == const.flagSpecializedMaterialBay:
        locationName = localization.GetByLabel('UI/Ship/MaterialBay')
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



def IsBookmarkModerator(corpRole):
    return corpRole & const.corpRoleChatManager == const.corpRoleChatManager


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
 'util.IsEveUser': IsEveUser,
 'util.IsDustUser': IsDustUser,
 'util.IsDustCharacter': IsDustCharacter,
 'util.IsOrbital': IsOrbital,
 'util.GetCurrencyTypeFromKey': GetCurrencyTypeFromKey,
 'util.GetActiveShip': GetActiveShip,
 'util.DgmAttribute': DgmAttribute,
 'util.DgmEffect': DgmEffect,
 'util.IsNPCCorporation': IsNPCCorporation,
 'util.IsBookmarkModerator': IsBookmarkModerator}

