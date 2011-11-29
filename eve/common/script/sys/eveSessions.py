import blue
import uthread
import weakref
import log
import random
import copy
import stackless
import types
import util
import macho
import sys
import math
import service
from service import *
import base
import logConst
import localization

class Session(base.CoreSession):
    __guid__ = 'base.Session'
    __persistvars__ = base.CoreSession.__persistvars__ + ['regionid',
     'constellationid',
     'allianceid',
     'warfactionid',
     'corpid',
     'fleetid',
     'fleetrole',
     'fleetbooster',
     'wingid',
     'squadid',
     'shipid',
     'stationid',
     'stationid2',
     'worldspaceid',
     'solarsystemid',
     'solarsystemid2',
     'hqID',
     'baseID',
     'rolesAtAll',
     'rolesAtHQ',
     'rolesAtBase',
     'rolesAtOther',
     'genderID',
     'bloodlineID',
     'raceID',
     'corpAccountKey',
     'inDetention',
     'battleID']
    __nonpersistvars__ = base.CoreSession.__nonpersistvars__ + ['locationid', 'corprole']
    __attributesWithDefaultValueOfZero__ = base.CoreSession.__attributesWithDefaultValueOfZero__ + ['corprole',
     'rolesAtAll',
     'rolesAtHQ',
     'rolesAtBase',
     'rolesAtOther']
    __dependant_attributes_eve__ = {'userid': ['inDetention'],
     'charid': ['corpid',
                'fleetid',
                'shipid',
                'stationid',
                'solarsystemid',
                'bloodlineID',
                'raceID',
                'genderID'],
     'corpid': ['baseID',
                'rolesAtAll',
                'rolesAtHQ',
                'rolesAtBase',
                'rolesAtOther',
                'hqID',
                'allianceid',
                'corpAccountKey',
                'warfactionid'],
     'baseID': ['corprole'],
     'rolesAtAll': ['corprole'],
     'rolesAtHQ': ['corprole'],
     'rolesAtBase': ['corprole'],
     'rolesAtOther': ['corprole'],
     'hqID': ['corprole'],
     'corpAccountKey': [],
     'stationid': ['locationid'],
     'worldspaceid': ['locationid'],
     'solarsystemid': ['locationid'],
     'locationid': ['solarsystemid2'],
     'solarsystemid2': ['constellationid'],
     'constellationid': ['regionid'],
     'fleetid': ['fleetrole',
                 'wingid',
                 'squadid',
                 'fleetbooster'],
     'wingid': ['squadid'],
     'squadid': []}
    __dependant_attributes__ = {}
    for (key, val,) in base.CoreSession.__dependant_attributes__.iteritems():
        __dependant_attributes__[key] = val + __dependant_attributes_eve__.get(key, [])

    for (key, val,) in __dependant_attributes_eve__.iteritems():
        if key not in __dependant_attributes__:
            __dependant_attributes__[key] = val


    def __init__(self, sid, localSID, role):
        base.CoreSession.__init__(self, sid, localSID, role, ['locationid', 'corprole'])
        self.additionalNoSetAttributes = ['locationid', 'corprole']
        self.additionalDistributedProps = ['locationid', 'corprole']
        self.additionalNonIntegralAttributes = ['fleetid',
         'fleetrole',
         'wingid',
         'squadid',
         'fleetbooster']
        self.longAttributes = ['corprole']
        self.additionalAttributesToPrint = ['locationid', 'corprole']
        self.additionalHexAttributes = ['corprole',
         'rolesAtAll',
         'rolesAtHQ',
         'rolesAtBase',
         'rolesAtOther']



    def RecalculateDependantAttributes(self, d):
        if 'stationid' in d or 'solarsystemid' in d or 'worldspaceid' in d:
            d['locationid'] = d.get('worldspaceid', None)
            if d['locationid'] is None:
                d['locationid'] = d.get('stationid', None)
                if d['locationid'] is None:
                    d['locationid'] = d.get('solarsystemid', None)
        if d.get('stationid', None):
            d['worldspaceid'] = d['stationid']
        for each in ('hqID', 'baseID', 'rolesAtAll', 'rolesAtHQ', 'rolesAtBase', 'rolesAtOther', 'stationid', 'solarsystemid'):
            if each in d:
                rolesAtAll = d.get('rolesAtAll', self.rolesAtAll)
                rolesAtHQ = d.get('rolesAtHQ', self.rolesAtHQ)
                rolesAtBase = d.get('rolesAtBase', self.rolesAtBase)
                rolesAtOther = d.get('rolesAtOther', self.rolesAtOther)
                hqID = d.get('hqID', self.hqID)
                baseID = d.get('baseID', self.baseID)
                stationid = d.get('stationid', self.stationid)
                solarsystemid = d.get('solarsystemid', self.solarsystemid)
                corprole = rolesAtAll | rolesAtOther
                if stationid:
                    if stationid == hqID:
                        corprole = rolesAtAll | rolesAtHQ
                    elif stationid == baseID:
                        corprole = rolesAtAll | rolesAtBase
                d['corprole'] = corprole
                break




    def RecalculateDependantAttributesWithChanges(self, changes):
        if 'stationid' in changes or 'solarsystemid' in changes or 'worldspaceid' in changes:
            old = self.locationid
            new = changes.get('worldspaceid', [None, None])[1]
            if not new:
                new = changes.get('stationid', [None, None])[1]
            if not new:
                new = changes.get('solarsystemid', [None, None])[1]
            changes['locationid'] = (old, new)
        if changes.get('stationid', None):
            newStationID = changes.get('stationid', [None, None])[1]
            if newStationID:
                changes['worldspaceid'] = changes['stationid']
        for each in ('hqID', 'baseID', 'rolesAtAll', 'rolesAtHQ', 'rolesAtBase', 'rolesAtOther', 'stationid', 'solarsystemid'):
            if each in changes:
                rolesAtAll = changes.get('rolesAtAll', [None, self.rolesAtAll])[1]
                rolesAtHQ = changes.get('rolesAtHQ', [None, self.rolesAtHQ])[1]
                rolesAtBase = changes.get('rolesAtBase', [None, self.rolesAtBase])[1]
                rolesAtOther = changes.get('rolesAtOther', [None, self.rolesAtOther])[1]
                hqID = changes.get('hqID', [None, self.hqID])[1]
                baseID = changes.get('baseID', [None, self.baseID])[1]
                stationid = changes.get('stationid', [None, self.stationid])[1]
                solarsystemid = changes.get('solarsystemid', [None, self.solarsystemid])[1]
                old = self.corprole
                corprole = rolesAtAll | rolesAtOther
                if stationid:
                    if stationid == hqID:
                        corprole = rolesAtAll | rolesAtHQ
                    elif stationid == baseID:
                        corprole = rolesAtAll | rolesAtBase
                if old != corprole:
                    changes['corprole'] = (old, corprole)
                break




eveSessionsByAttribute = {'regionid': {},
 'constellationid': {},
 'corpid': {},
 'fleetid': {},
 'wingid': {},
 'squadid': {},
 'shipid': {},
 'stationid': {},
 'stationid2': {},
 'worldspaceid': {},
 'locationid': {},
 'solarsystemid': {},
 'solarsystemid2': {},
 'allianceid': {},
 'warfactionid': {}}
base.sessionsByAttribute.update(eveSessionsByAttribute)

def GetCharLocation(charID):
    return GetCharLocation2(charID)[0:2]



def GetCharLocation2(charID):
    try:
        (x, y, z,) = GetCharLocationEx(charID)
    except RuntimeError:
        y = None
    if y is None:
        charUnboundMgr = sm.services['charUnboundMgr']
        charMgr = sm.services['charMgr']
        charUnboundMgr.MoveCharacter(charID, charMgr.GetHomeStation(charID), 0)
        (x, y, z,) = GetCharLocationEx(charID)
        if y is None:
            raise RuntimeError('Bogus character item state', charID, x, z)
    return (x, y, z)



def IsLocationNode(session):
    if not macho.mode == 'server':
        return False
    machoNet = sm.GetService('machoNet')
    currentNodeID = machoNet.GetNodeID()
    return any((session.solarsystemid and currentNodeID == machoNet.GetNodeFromAddress(const.cluster.SERVICE_BEYONCE, session.solarsystemid), session.stationid and currentNodeID == machoNet.GetNodeFromAddress('station', session.stationid), session.worldspaceid and currentNodeID == machoNet.GetNodeFromAddress(const.cluster.SERVICE_WORLDSPACE, session.worldspaceid)))



def GetCharLocationEx(charID):
    sessions = base.FindSessions('charid', [charID])
    if len(sessions) and IsLocationNode(sessions[0]):
        s = sessions[0]
        if s.solarsystemid:
            return (s.solarsystemid, const.groupSolarSystem, s.shipid)
        if s.stationid and s.shipid:
            return (s.stationid, const.groupStation, s.shipid)
        if s.stationid:
            return (s.stationid, const.groupStation, s.stationid)
        if s.worldspaceid:
            return (s.worldspaceid, const.groupWorldSpace, s.worldspaceid)
    else:
        while sm.services['DB2'].state != SERVICE_RUNNING:
            blue.pyos.synchro.SleepWallclock(100)

        rs = sm.services['DB2'].character.Characters_LocationInfo(charID)
        locationInfo = rs[0]
        if locationInfo.locationID is None:
            raise RuntimeError('No such locationID', locationInfo.locationID, 'for charID', charID)
        if locationInfo.locationGroupID in (const.groupStation, const.groupSolarSystem, const.groupWorldSpace):
            return (locationInfo.locationID, locationInfo.locationGroupID, locationInfo.characterLocationID)
        else:
            return (locationInfo.locationID, None, locationInfo.characterLocationID)



def IsUndockingSessionChange(session, change):
    goingFromStation = change.has_key('stationid') and change.get('stationid')[0]
    goingToSpace = change.has_key('solarsystemid') and change.get('solarsystemid')[1]
    return goingFromStation and goingToSpace



class SessionMgr(base.SessionMgr):
    __guid__ = 'svc.eveSessionMgr'
    __displayname__ = 'Session manager'
    __replaceservice__ = 'sessionMgr'
    __exportedcalls__ = {'GetSessionStatistics': [ROLE_SERVICE],
     'CloseUserSessions': [ROLE_SERVICE],
     'GetProxyNodeFromID': [ROLE_SERVICE],
     'GetClientIDFromID': [ROLE_SERVICE],
     'UpdateSessionAttributes': [ROLE_SERVICE],
     'ConnectToClientService': [ROLE_SERVICE],
     'PerformSessionChange': [ROLE_SERVICE],
     'GetLocalClientIDs': [ROLE_SERVICE],
     'EndAllGameSessions': [ROLE_ADMIN | ROLE_SERVICE],
     'PerformHorridSessionAttributeUpdate': [ROLE_SERVICE],
     'BatchedRemoteCall': [ROLE_SERVICE],
     'GetSessionDetails': [ROLE_SERVICE],
     'TerminateClientConnections': [ROLE_SERVICE | ROLE_ADMIN],
     'GetOrCreateSession': [ROLE_SERVICE],
     'GetInitialValuesFromCharID': [ROLE_SERVICE]}
    __dependencies__ = []
    __notifyevents__ = ['ProcessInventoryChange'] + base.SessionMgr.__notifyevents__

    def __init__(self):
        base.SessionMgr.__init__(self)
        if macho.mode == 'server':
            self.__dependencies__ += ['config',
             'station',
             'ship',
             'corporationSvc',
             'corpmgr',
             'i2',
             'stationSvc',
             'cache']
        self.sessionChangeShortCircuitReasons = ['autopilot']
        self.additionalAttribsAllowedToUpdate = ['allianceid', 'corpid']
        self.additionalStatAttribs = ['solarsystemid', 'solarsystemid2']
        self.additionalSessionDetailsAttribs = ['allianceid',
         'warfactionid',
         'corpid',
         'corprole',
         'shipid',
         'regionid',
         'constellationid',
         'solarsystemid2',
         'locationid',
         'solarsystemid',
         'stationid',
         'stationid2',
         'worldspaceid',
         'fleetid',
         'wingid',
         'squadid',
         'fleetrole',
         'fleetbooster',
         'corpAccountKey',
         'inDetention']



    def AppRun(self, memstream = None):
        if macho.mode == 'server':
            self.dbcharacter = self.DB2.GetSchema('character')



    def GetReason(self, oldReason, newReason, timeLeft):
        if timeLeft:
            seconds = int(math.ceil(max(1, timeLeft) / float(const.SEC)))
        reason = localization.GetByLabel('Sessions/BaseReason')
        if oldReason == newReason or oldReason.startswith('fleet.') and newReason.startswith('fleet.') or oldReason.startswith('corp.') and newReason.startswith('corp.'):
            if oldReason.startswith('fleet.'):
                reason = localization.GetByLabel('Sessions/FleetOperation')
                if timeLeft:
                    reason = localization.GetByLabel('Sessions/EstimatedTimeLeft', reason=reason, seconds=seconds)
            elif oldReason.startswith('corp.'):
                reason = localization.GetByLabel('Sessions/CorpOperation')
                if timeLeft:
                    reason = localization.GetByLabel('Sessions/EstimatedTimeLeft', reason=reason, seconds=seconds)
            elif oldReason == 'undock':
                reason = localization.GetByLabel('Sessions/Undocking')
                if timeLeft:
                    reason = localization.GetByLabel('Sessions/EstimatedTimeLeft', reason=reason, seconds=seconds)
            elif oldReason == 'dock':
                reason = localization.GetByLabel('Sessions/Docking')
                if timeLeft:
                    reason = localization.GetByLabel('Sessions/EstimatedTimeLeft', reason=reason, seconds=seconds)
            elif oldReason == 'jump' and newReason == 'jump':
                reason = localization.GetByLabel('Sessions/Jump')
                if timeLeft:
                    reason = localization.GetByLabel('Sessions/EstimatedTimeLeft', reason=reason, seconds=seconds)
            elif oldReason == 'jump':
                reason = localization.GetByLabel('Sessions/StartgateJump')
                if timeLeft:
                    reason = localization.GetByLabel('Sessions/StartgateJumpEstimatedTime', reason=reason, seconds=seconds)
            elif oldReason == 'eject':
                reason = localization.GetByLabel('Sessions/Ejecting')
                if timeLeft:
                    reason = localization.GetByLabel('Sessions/EjectingEstimatedTime', reason=reason, seconds=seconds)
            elif oldReason == 'evacuate':
                reason = localization.GetByLabel('Sessions/Evacuation')
                if timeLeft:
                    reason = localization.GetByLabel('Sessions/EvacuationsEstimatedTime', reason=reason, seconds=seconds)
            elif oldReason == 'board':
                reason = localization.GetByLabel('Sessions/Boarding')
                if timeLeft:
                    reason = localization.GetByLabel('Sessions/BoardingEstimatedTime', reason=reason, seconds=seconds)
            elif oldReason == 'selfdestruct':
                reason = localization.GetByLabel('Sessions/SelfDestruct')
                if timeLeft:
                    reason = localization.GetByLabel('Sessions/SelfDestructEstimatedTime', reason=reason, seconds=seconds)
            elif oldReason == 'charsel':
                reason = localization.GetByLabel('Sessions/CharacterSelection')
                if timeLeft:
                    reason = localization.GetByLabel('Sessions/CharacterSelectionEstimatedTime', reason=reason, seconds=seconds)
            elif oldReason == 'storeVessel':
                reason = localization.GetByLabel('Sessions/Embarkation')
                if timeLeft:
                    reason = localization.GetByLabel('Sessions/EmbarkationEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'autopilot':
            reason = localization.GetByLabel('Sessions/Autopilot')
            if timeLeft:
                reason = localization.GetByLabel('Sessions/AutopilotEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'undock':
            reason = localization.GetByLabel('Sessions/AreUndocking')
            if timeLeft:
                reason = localization.GetByLabel('Sessions/AreUndockingEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'dock':
            reason = localization.GetByLabel('Sessions/AreDocking')
            if timeLeft:
                reason = localization.GetByLabel('Sessions/AreDockingEstimmatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'jump':
            reason = localization.GetByLabel('Sessions/AreJumping')
            if timeLeft:
                reason = localization.GetByLabel('Sessions/AreJumpingEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'eject':
            reason = localization.GetByLabel('Sessions/AreEjecting')
            if timeLeft:
                reason = localization.GetByLabel('Sessions/AreEjectingEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'evacuate':
            reason = localization.GetByLabel('Sessions/AreEvacuating')
            if timeLeft:
                reason = localization.GetByLabel('Sessions/AreEvacuatingEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'board':
            reason = localization.GetByLabel('Sessions/AreBoarding')
            if timeLeft:
                reason = localization.GetByLabel('Sessions/AreBoardingEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'selfdestruct':
            reason = localization.GetByLabel('Sessions/AreSelfDestructing')
            if timeLeft:
                reason = localization.GetByLabel('Sessions/AreSelfDestructiongEstimateTime', reason=reason, seconds=seconds)
        elif oldReason == 'charsel':
            reason = localization.GetByLabel('Sessions/AreSelectingCharacter')
            if timeLeft:
                reason = localization.GetByLabel('Sessions/AreSelectingCharacterEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'accelerationgate':
            reason = localization.GetByLabel('Sessions/AreUsingAccelerationGate')
            if timeLeft:
                reason = localization.GetByLabel('Sessions/AreUsingAccelerationGateEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason.startswith('corp.'):
            reason = localization.GetByLabel('Sessions/CorpActivity')
            if timeLeft:
                reason = localization.GetByLabel('Sessions/CorpActivityEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason.startswith('fleet.'):
            reason = localization.GetByLabel('Sessions/FleetOperations')
            if timeLeft:
                reason = localization.GetByLabel('Sessions/FleetOperationsEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'storeVessel':
            reason = localization.GetByLabel('Sessions/AreBoardingVessel')
            if timeLeft:
                reason = localization.GetByLabel('Sessions/AreBoardingVesselEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'bookmarking':
            reason = localization.GetByLabel('Sessions/Bookmarking')
        return reason



    def TypeAndNodeValidationHook(self, idType, id):
        if macho.mode == 'server' and idType in ('allianceid', 'corpid'):
            machoNet = sm.GetService('machoNet')
            if machoNet.GetNodeID() != machoNet.GetNodeFromAddress(const.cluster.SERVICE_CHATX, id % 200):
                raise RuntimeError('Horrid session change called on incorrect node.  You must at very least perform this abomination on the right node.')



    def ProcessInventoryChange(self, items, change, isRemote, inventory2):
        if macho.mode != 'server':
            return 
        if isRemote:
            return 
        if const.ixLocationID not in change and const.ixFlag not in change:
            return 
        locationID = locationGroupID = None
        if const.ixLocationID in change:
            locationID = change[const.ixLocationID][1]
            if util.IsSolarSystem(locationID):
                locationGroupID = const.groupSolarSystem
            elif util.IsStation(locationID):
                locationGroupID = const.groupStation
        chars = {}
        if not isinstance(items, list):
            items = [items]
        for item in items:
            if item.categoryID == const.categoryShip and None not in (locationID, locationGroupID):
                inv2 = self.i2.GetInventory(locationID, locationGroupID)
                for i in inv2.SelectItems(item.itemID):
                    if i.groupID == const.groupCharacter:
                        chars[i.itemID] = self.GetSessionValuesFromItemID(item.itemID, inventory2, item)

            elif item.groupID == const.groupCharacter:
                if const.ixLocationID in change and item.customInfo == logConst.eventUndock:
                    continue
                chars[item.itemID] = self.GetSessionValuesFromItemID(item.itemID, inventory2, item)

        if len(chars) == 0:
            return 
        for (charID, updateDict,) in chars.iteritems():
            for sess in base.FindSessions('charid', [charID]):
                sess.LogSessionHistory('Transmogrifying OnInventoryChange to SetAttributes')
                sess.SetAttributes(updateDict)
                sess.LogSessionHistory('Transmogrified OnInventoryChange to SetAttributes')





    def GetSessionValuesFromItemID(self, itemID, inventory2 = None, theItem = None):
        if itemID == const.locationAbstract:
            raise RuntimeError('Invalid argument, itemID cannot be 0')

        def GetItem(id):
            return sm.services['i2'].GetItemMx(18, 5, id)


        updateDict = {'shipid': None,
         'stationid': None,
         'stationid2': None,
         'solarsystemid': None,
         'solarsystemid2': None,
         'regionid': None,
         'constellationid': None,
         'worldspaceid': None}
        solsysID = None
        while 1:
            if inventory2 is None:
                item = GetItem(itemID)
            elif theItem and theItem.itemID == itemID:
                item = theItem
            elif itemID < const.minPlayerItem:
                if util.IsStation(itemID):
                    station = self.stationSvc.GetStation(itemID)
                    updateDict['stationid'] = itemID
                    updateDict['stationid2'] = itemID
                    solsysID = station.solarSystemID
                    break
                else:
                    item = inventory2.InvGetItem(itemID)
            else:
                item = inventory2.InvGetItem(itemID, 1)
            if item.categoryID == const.categoryShip:
                updateDict['shipid'] = itemID
            elif item.groupID == const.groupStation:
                updateDict['stationid'] = itemID
                updateDict['stationid2'] = itemID
                updateDict['worldspaceid'] = itemID
                solsysID = item.locationID
                break
            elif item.groupID == const.groupWorldSpace:
                updateDict['worldspaceid'] = itemID
                locationID = item.locationID
                if not util.IsStation(locationID):
                    raise RuntimeError('Setting stationid2 = %s which is not a station!' % locationID)
                updateDict['stationid2'] = locationID
                station = self.stationSvc.GetStation(locationID)
                solsysID = station.solarSystemID
                break
            elif item.typeID == const.typeSolarSystem:
                solsysID = item.itemID
                updateDict['solarsystemid'] = itemID
                break
            elif item.locationID == const.locationAbstract:
                break
            itemID = item.locationID

        if solsysID is not None:
            primeditems = sm.services['i2'].__primeditems__
            if solsysID in primeditems:
                updateDict['solarsystemid2'] = solsysID
                updateDict['constellationid'] = primeditems[solsysID].locationID
                updateDict['regionid'] = primeditems[updateDict['constellationid']].locationID
        return updateDict



    def GetSessionValuesFromRowset(self, si):
        sessValues = {'allianceid': si.allianceID,
         'warfactionid': si.warFactionID,
         'corpid': si.corporationID,
         'hqID': si.hqID,
         'baseID': si.baseID,
         'rolesAtAll': si.roles,
         'rolesAtHQ': si.rolesAtHQ,
         'rolesAtBase': si.rolesAtBase,
         'rolesAtOther': si.rolesAtOther,
         'fleetid': None,
         'fleetrole': None,
         'fleetbooster': None,
         'wingid': None,
         'squadid': None,
         'shipid': si.shipID,
         'stationid': None,
         'solarsystemid': None,
         'regionid': None,
         'constellationid': None,
         'genderID': si.genderID,
         'bloodlineID': si.bloodlineID,
         'raceID': cfg.bloodlines.Get(si.bloodlineID).raceID,
         'corpAccountKey': si.corpAccountKey}
        if si.zoneid:
            sessValues['worldspaceid'] = si.zoneid
            sessValues['stationid2'] = si.stationID
            station = self.stationSvc.GetStation(si.stationID)
            sessValues['solarsystemid2'] = station.solarSystemID
        elif si.stationID:
            sessValues['stationid'] = si.stationID
            sessValues['stationid2'] = si.stationID
            sessValues['worldspaceid'] = si.stationID
            station = self.stationSvc.GetStation(si.stationID)
            sessValues['solarsystemid2'] = station.solarSystemID
        elif si.solarSystemID:
            sessValues['solarsystemid'] = si.solarSystemID
            sessValues['solarsystemid2'] = si.solarSystemID
        if 'solarsystemid2' in sessValues:
            if sessValues['solarsystemid2'] is not None:
                primeditems = sm.services['i2'].__primeditems__
                if sessValues['solarsystemid2'] in primeditems:
                    sessValues['constellationid'] = primeditems[sessValues['solarsystemid2']].locationID
                    sessValues['regionid'] = primeditems[sessValues['constellationid']].locationID
        return sessValues



    def GetInitialValuesFromCharID(self, charID):
        if macho.mode != 'server':
            return {}
        rs = self.dbcharacter.Characters_Session(charID)
        si = rs[0]
        return self.GetSessionValuesFromRowset(si)



    def IsPlayerCharacter(self, charID):
        return util.IsCharacter(charID) and not util.IsNPC(charID)



    def GetSession(self, charID):
        s = base.FindSessions('charid', [charID])
        if not s:
            return None
        return s[0]



    def GetUserSession(self, userid):
        s = base.FindSessions('userid', [userid])
        if not s:
            return None
        return s[0]



    def GetOrCreateSession(self, userID, charID, details):
        sessionInit = {'userid': userID,
         'userType': 13,
         'role': service.ROLE_PLAYER,
         'languageID': 'EN',
         'maxSessionTime': None,
         'inDetention': None}
        if charID:
            sess = self.GetSession(charID)
            sessionInit.update({'charid': charID})
        elif userID:
            sess = self.GetUserSession(userID)
        else:
            raise RuntimeError("Can't find or create session without identifiers")
        if not sess:
            s = base.CreateUserSession(role=details.pop('role'))
            changes = {k:v for (k, v,) in details.iteritems()}
            sessionInit['role'] |= s.role
            s.LogSessionHistory('Character/User authenticated implicitely via direct call to sessionMgr')
            s.SetAttributes(sessionInit)
            s.LogSessionHistory('Applying initial session attribute directly via direct call to sessionMgr')
            s.SetAttributes(changes)
            sess = base.FindSessions('userid', [userID])
        return sess[0]



exports = {'base.GetCharLocation': GetCharLocation,
 'base.GetCharLocationEx': GetCharLocationEx,
 'base.IsLocationNode': IsLocationNode,
 'base.IsUndockingSessionChange': IsUndockingSessionChange}

