#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/entities/eveEntitySpawnClient.py
import svc
import geo2

class EveEntitySpawnClient(svc.entitySpawnClient):
    __guid__ = 'svc.eveEntitySpawnClient'
    __replaceservice__ = 'entitySpawnClient'
    __dependencies__ = svc.entitySpawnClient.__dependencies__[:]
    __dependencies__ += ['clientOnlyPlayerSpawnClient', 'cameraClient']

    def Run(self, *etc):
        svc.entitySpawnClient.Run(self, etc)
        self.charMgr = sm.RemoteSvc('charMgr')

    def _ChooseSpawnLocation(self, worldspaceID, sessionChanges = {}):
        searchTerm = None
        if 'charid' in sessionChanges and sessionChanges['charid'][0] == None:
            searchTerm = const.cef.CQ_NEWBIE_SPAWN
        elif 'stationid' in sessionChanges and sessionChanges['stationid'][0] == None:
            searchTerm = const.cef.CQ_BALCONY_SPAWN
        else:
            searchTerm = const.cef.CQ_BEDROOM_SPAWN
        if searchTerm is not None:
            spawnLocators = sm.GetService('spawnLocationClient').GetSpawnLocationsBySceneID(worldspaceID)
            for locator in spawnLocators:
                spawnLocationComponent = locator.GetComponent('spawnLocation')
                locationType = spawnLocationComponent.spawnLocationType
                if locationType == searchTerm:
                    self.cameraClient.RegisterCameraStartupInfo(spawnLocationComponent.cameraYaw, spawnLocationComponent.cameraPitch, spawnLocationComponent.cameraZoom)
                    spawnPoint = locator.GetComponent('position').position
                    xyzRot = locator.GetComponent('position').rotation
                    spawnRot = geo2.QuaternionRotationGetYawPitchRoll(xyzRot)
                    return (spawnPoint, spawnRot)

            self.LogWarn('Failed to find the locator:', searchTerm)
        spawnPoint, spawnRot = sm.GetService('worldSpaceClient').GetWorldSpaceSafeSpot(session.worldspaceid)
        self.LogWarn("Spawn point search term was None which means we don't have a defined spawn", 'location and will revert to the default safe spot')
        return (spawnPoint, spawnRot)

    def SpawnClientOnlyPlayer(self, scene, change):
        if not self.entityService.IsClientSideOnly(scene.sceneID):
            raise RuntimeError('You cannot spawn a client-side only player into a server-side created worldspace.')
        spawnPoint, spawnRot = self._ChooseSpawnLocation(scene.sceneID, change)
        self.clientOnlyPlayerSpawnClient.SpawnClientSidePlayer(scene, spawnPoint, spawnRot)