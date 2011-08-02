import svc
import const
from sceneManager import SCENE_TYPE_SPACE
from sceneManager import SCENE_TYPE_INTERIOR
import util
import log

class EveWorldSpaceClient(svc.worldSpaceClient):
    __guid__ = 'svc.eveWorldSpaceClient'
    __replaceservice__ = 'worldSpaceClient'
    __exportedcalls__ = svc.worldSpaceClient.__exportedcalls__.copy()
    __dependencies__ = svc.worldSpaceClient.__dependencies__[:]
    __dependencies__.extend(['navigation'])
    __notifyevents__ = svc.worldSpaceClient.__notifyevents__[:]

    def Run(self, *args, **kwargs):
        svc.worldSpaceClient.Run(self, *args, **kwargs)



    def OnLoadEntityScene(self, sceneID):
        self.LogInfo('Loading worldspace for entity scene', sceneID)
        worldspace = self.LoadWorldSpaceInstance(sceneID)
        self.WaitForInstance(sceneID)
        self.LogInfo('Done Loading worldspace for entity scene', sceneID)
        if sceneID == session.worldspaceid:
            self.activeWorldSpace = session.worldspaceid



    def OnUnloadEntityScene(self, sceneID):
        pass



    def OnEntitySceneUnloaded(self, sceneID):
        self.UnloadWorldSpaceInstance(sceneID)



    def TearDownWorldSpaceRendering(self):
        sceneManager = sm.GetService('sceneManager')
        sceneManager.SetSceneType(SCENE_TYPE_SPACE)



    def GetWorldSpaceTypeIDFromWorldSpaceID(self, worldSpaceID):
        if util.IsStation(worldSpaceID):
            return 32580
            stationType = cfg.invtypes.Get(eve.stationItem.stationTypeID)
            stationRace = stationType['raceID']
            if stationRace == const.raceCaldari:
                return 32581
            else:
                if stationRace == const.raceMinmatar:
                    return 32580
                if stationRace == const.raceAmarr:
                    return 32578
                if stationRace == const.raceGallente:
                    return 32579
                if stationRace == const.raceJove:
                    return 32579
                msg = 'Trying to load world space for race with ID %s. Race not found. Loading Minmatar world space instead.' % stationRace
                self.LogWarn(msg)
                return 32580
        return sm.RemoteSvc('worldSpaceServer').GetWorldSpaceTypeIDFromWorldSpaceID(worldSpaceID)



    def GetWorldSpaceInventoryTypeIDFromWorldSpaceID(self, worldSpaceID):
        worldSpaceTypeID = self.GetWorldSpaceTypeIDFromWorldSpaceID(worldSpaceID)
        return worldSpaceTypeID



    def GetWorldSpaceSafeSpot(self, worldSpaceID):
        worldspaceDesc = cfg.worldspaces.Get(self.GetWorldSpaceInventoryTypeIDFromWorldSpaceID(worldSpaceID))
        safespotloc = (worldspaceDesc.safeSpotX, worldspaceDesc.safeSpotY, worldspaceDesc.safeSpotZ)
        safespotrot = (worldspaceDesc.safeSpotRotY, 0, 0)
        return (safespotloc, safespotrot)




