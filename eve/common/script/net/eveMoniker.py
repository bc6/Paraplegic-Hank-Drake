import macho
import const
from util import Moniker

def GetLocationBindParams():
    if session.solarsystemid:
        return (session.solarsystemid, const.groupSolarSystem)
    if session.stationid:
        return (session.stationid, const.groupStation)
    if session.worldspaceid:
        return (session.worldspaceid, const.groupWorldSpace)
    raise RuntimeError('You have no place to go')



def GetLocationSessionCheck():
    if session.solarsystemid:
        return {'solarsystemid': session.solarsystemid}
    if session.stationid:
        return {'stationid': session.stationid}
    if session.worldspaceid:
        return {'worldspaceid': session.worldspaceid}
    raise RuntimeError('You have no location to check on')



def CharGetDogmaLocation():
    moniker = Moniker('dogmaIM', GetLocationBindParams())
    moniker.SetSessionCheck(GetLocationSessionCheck())
    return moniker



def GetStationDogmaLocation():
    moniker = Moniker('dogmaIM', (session.stationid2, const.groupStation))
    moniker.SetSessionCheck({'stationid2': session.stationid2})
    return moniker



def GetShipAccess():
    if session.solarsystemid:
        moniker = Moniker('ship', (session.solarsystemid, const.groupSolarSystem))
        moniker.SetSessionCheck({'solarsystemid': session.solarsystemid})
    elif session.stationid2:
        moniker = Moniker('ship', (session.stationid2, const.groupStation))
        moniker.SetSessionCheck({'stationid2': session.stationid2})
    return moniker



def GetStationShipAccess():
    moniker = Moniker('ship', (session.stationid2, const.groupStation))
    moniker.SetSessionCheck({'stationid2': session.stationid2})
    return moniker



def GetEntityAccess():
    if session.solarsystemid is not None:
        moniker = Moniker('entity', session.solarsystemid)
        moniker.SetSessionCheck({'solarsystemid': session.solarsystemid})
        return moniker
    raise RuntimeError('EntityAccess only available in-flight but session is %s' % (session,))



def GetPOSMgr():
    if session.solarsystemid is not None:
        moniker = Moniker('posMgr', session.solarsystemid)
        moniker.SetSessionCheck({'solarsystemid': session.solarsystemid})
        return moniker
    raise RuntimeError('POSMgr only available in-flight but session is %s' % (session,))



def CharGetSkillHandler():
    moniker = Moniker('skillMgr', GetLocationBindParams())
    moniker.SetSessionCheck(GetLocationSessionCheck())
    return moniker



def GetReprocessingManager():
    moniker = GetReprocessingManagerEx(session.stationid2)
    moniker.SetSessionCheck({'stationid2': session.stationid2})
    return moniker



def GetReprocessingManagerEx(stationID):
    return Moniker('reprocessingSvc', stationID)



def GetCorpStationManager():
    moniker = GetCorpStationManagerEx(session.stationid2)
    moniker.SetSessionCheck({'stationid2': session.stationid2})
    return moniker



def GetCorpStationManagerEx(stationID):
    return Moniker('corpStationMgr', stationID)



def GetSolarSystemInventoryMgr(solarsystemID):
    return Moniker('invbroker', (solarsystemID, const.groupSolarSystem))



def GetStationInventoryMgr(stationID):
    return Moniker('invbroker', (stationID, const.groupStation))



def GetWorldSpaceInventoryMgr(worldSpaceID):
    return Moniker('invbroker', (worldSpaceID, const.groupWorldSpace))



def GetInventoryMgr():
    if session.solarsystemid:
        moniker = GetSolarSystemInventoryMgr(session.solarsystemid)
        moniker.SetSessionCheck({'solarsystemid': session.solarsystemid})
        return moniker
    if session.stationid:
        moniker = GetStationInventoryMgr(session.stationid)
        moniker.SetSessionCheck({'stationid': session.stationid})
        return moniker
    if session.worldspaceid:
        moniker = GetWorldSpaceInventoryMgr(session.worldspaceid)
        moniker.SetSessionCheck({'worldspaceid': session.worldspaceid})
        return moniker
    raise RuntimeError('Caller not in solsys nor station', session)



def GetAggressionManager():
    moniker = Moniker('aggressionMgr', session.solarsystemid)
    moniker.SetSessionCheck({'solarsystemid': session.solarsystemid})
    return moniker



def GetBallPark(solarsystemID):
    moniker = Moniker('beyonce', solarsystemID)
    moniker.SetSessionCheck({'solarsystemid': solarsystemID})
    return moniker



def GetCourierMissionCreator(stationID):
    return Moniker('missionMgr', ('courier', stationID))



def GetAgent(agentID, stationID = None):
    if stationID is not None:
        nodeID = sm.services['machoNet'].CheckAddressCache('station', stationID)
        if nodeID is not None:
            sm.services['machoNet'].SetNodeOfAddress('agentMgr', agentID, nodeID)
    return Moniker('agentMgr', agentID)



def GetCorpRegistry():
    moniker = GetCorpRegistryEx(session.corpid, 1)
    moniker.SetSessionCheck({'corpid': session.corpid})
    return moniker



def GetCorpRegistryEx(corpID, isMaster = 0):
    if macho.mode == 'server':
        isMaster = isMaster or sm.StartServiceAndWaitForRunningState('corpRegistry').IsCorpLocal(corpID)
    return Moniker('corpRegistry', (corpID, isMaster))



def GetAlliance():
    if session.allianceid is None:
        raise RuntimeError('YouAreNotInAnAllianceAtTheMoment')
    moniker = GetAllianceEx(session.allianceid, 1)
    moniker.SetSessionCheck({'allianceid': session.allianceid})
    return moniker



def GetAllianceEx(allianceID, isMaster = 0):
    if macho.mode == 'server':
        isMaster = isMaster or sm.StartServiceAndWaitForRunningState('allianceRegistry').IsAllianceLocal(allianceID)
    return Moniker('allianceRegistry', (allianceID, isMaster))



def GetWar():
    ownerID = session.corpid
    ownerType = 'corpid'
    if session.allianceid:
        ownerID = session.allianceid
        ownerType = 'allianceid'
    moniker = GetWarEx(ownerID, 1)
    moniker.SetSessionCheck({ownerType: ownerID})
    return moniker



def GetWarEx(allianceOrCorpID, isMaster = 0):
    if macho.mode == 'server':
        isMaster = isMaster or sm.StartServiceAndWaitForRunningState('warRegistry').IsAllianceOrCorpLocal(allianceOrCorpID)
    return Moniker('warRegistry', (allianceOrCorpID, isMaster))



def GetFleet(fleetID = None):
    fleetID = fleetID or session.fleetid
    moniker = Moniker('fleetObjectHandler', fleetID)
    return moniker



def GetPlanet(planetID):
    return Moniker('planetMgr', planetID)



def GetPlanetBaseManager(planetID):
    return Moniker('planetBaseBroker', planetID)



def GetPlanetOrbitalRegistry(solarSystemID):
    return Moniker('planetOrbitalRegistryBroker', solarSystemID)


exports = {'moniker.GetAgent': GetAgent,
 'moniker.CharGetDogmaLocation': CharGetDogmaLocation,
 'moniker.GetStationDogmaLocation': GetStationDogmaLocation,
 'moniker.GetShipAccess': GetShipAccess,
 'moniker.GetStationShipAccess': GetStationShipAccess,
 'moniker.GetEntityAccess': GetEntityAccess,
 'moniker.GetPOSMgr': GetPOSMgr,
 'moniker.CharGetSkillHandler': CharGetSkillHandler,
 'moniker.GetCorpStationManager': GetCorpStationManager,
 'moniker.GetCorpStationManagerEx': GetCorpStationManagerEx,
 'moniker.GetInventoryMgr': GetInventoryMgr,
 'moniker.GetStationInventoryMgr': GetStationInventoryMgr,
 'moniker.GetAggressionManager': GetAggressionManager,
 'moniker.GetBallPark': GetBallPark,
 'moniker.GetCourierMissionCreator': GetCourierMissionCreator,
 'moniker.GetReprocessingManager': GetReprocessingManager,
 'moniker.GetReprocessingManagerEx': GetReprocessingManagerEx,
 'moniker.GetCorpRegistry': GetCorpRegistry,
 'moniker.GetCorpRegistryEx': GetCorpRegistryEx,
 'moniker.GetAlliance': GetAlliance,
 'moniker.GetAllianceEx': GetAllianceEx,
 'moniker.GetWar': GetWar,
 'moniker.GetWarEx': GetWarEx,
 'moniker.GetFleet': GetFleet,
 'moniker.GetPlanet': GetPlanet,
 'moniker.GetPlanetBaseManager': GetPlanetBaseManager,
 'moniker.GetPlanetOrbitalRegistry': GetPlanetOrbitalRegistry}

