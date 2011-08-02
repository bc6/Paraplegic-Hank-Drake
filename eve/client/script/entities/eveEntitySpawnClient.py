import svc
import entities
import util
import entityCommon
import uthread
CQ_NEWBIE_SPAWN = 'NewbieStart'
CQ_DOOR_SPAWN = 'DoorStart'
CQ_BALCONY_SPAWN = 'BalconyStart'
CQ_BEDROOM_SPAWN = 'BedroomStart'

class EveEntitySpawnService(svc.entitySpawnClient):
    __guid__ = 'svc.eveEntitySpawnClient'
    __replaceservice__ = 'entitySpawnClient'
    __notifyevents__ = svc.entitySpawnClient.__notifyevents__ + ['OnSessionChanged']

    def Run(self, *etc):
        svc.entitySpawnClient.Run(self, etc)
        self.charMgr = sm.RemoteSvc('charMgr')
        self.paperDollServer = sm.RemoteSvc('paperDollServer')



    def _ChooseSpawnLocation(self, worldspaceID, sessionChanges):
        searchTerm = None
        if 'charid' in sessionChanges and sessionChanges['charid'][0] == None:
            if sm.RemoteSvc('charMgr').GetPrivateInfo(session.charid).logonCount == 0:
                searchTerm = CQ_NEWBIE_SPAWN
            else:
                searchTerm = CQ_BEDROOM_SPAWN
        elif 'stationid' in sessionChanges and sessionChanges['stationid'][0] == None:
            searchTerm = CQ_BALCONY_SPAWN
        if searchTerm:
            worldSpaceTypeID = sm.GetService('worldSpaceClient').GetWorldSpaceTypeIDFromWorldSpaceID(worldspaceID)
            worldSpaceLocatorRowSet = cfg.worldspaceLocators.get(worldSpaceTypeID, [])
            for locatorRow in worldSpaceLocatorRowSet:
                if locatorRow.locatorName == searchTerm:
                    spawnPoint = (locatorRow.posX, locatorRow.posY, locatorRow.posZ)
                    spawnRot = (locatorRow.yaw, locatorRow.pitch, locatorRow.roll)
                    return (spawnPoint, spawnRot)

            self.LogWarn('Failed to find the locator:', searchTerm)
        (spawnPoint, spawnRot,) = sm.GetService('worldSpaceClient').GetWorldSpaceSafeSpot(session.worldspaceid)
        return (spawnPoint, spawnRot)



    def SpawnClientSidePlayer(self, sessionChanges = {}):
        self.LogInfo('Spawning client side player entity for', session.charid)
        scene = self.entityService.LoadEntitySceneAndBlock(session.stationid)
        scene.WaitOnStartupEntities()
        playerTypeID = cfg.eveowners.Get(session.charid).Type().id
        serverInfoCalls = []
        serverInfoCalls.append((self.paperDollServer.GetPaperDollData, (session.charid,)))
        serverInfoCalls.append((self.charMgr.GetPublicInfo, (session.charid,)))
        (paperdolldna, pubInfo,) = uthread.parallel(serverInfoCalls)
        recipeSvc = sm.GetService('entityRecipeSvc')
        overrides = {}
        (spawnPoint, spawnRot,) = self._ChooseSpawnLocation(session.worldspaceid, sessionChanges)
        self.OverridePosition(overrides, spawnPoint, spawnRot)
        paperDollComponentID = const.cef.PAPER_DOLL_COMPONENT_ID
        overrides[paperDollComponentID] = {'gender': pubInfo.gender,
         'dna': paperdolldna,
         'typeID': playerTypeID}
        recipe = recipeSvc.GetTypeRecipe(playerTypeID, overrides)
        spawnedEntity = self.entityService.CreateEntityFromRecipe(scene, recipe, session.charid)
        scene.CreateAndRegisterEntity(spawnedEntity)
        self.LogInfo('Client side player entity spawned for', session.charid)



    def OnSessionChanged(self, isRemote, session, change):
        (oldws, newws,) = change.get('worldspaceid', (None, None))
        if newws and self.entityService.IsClientSideOnly(newws):
            if util.IsStation(newws) and not prefs.GetValue('loadstationenv', 1):
                return None
            self.SpawnClientSidePlayer(change)




