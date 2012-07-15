#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/world/eveWorldSpaceClient.py
import svc
import const
import util

class EveWorldSpaceClient(svc.worldSpaceClient):
    __guid__ = 'svc.eveWorldSpaceClient'
    __replaceservice__ = 'worldSpaceClient'
    __exportedcalls__ = svc.worldSpaceClient.__exportedcalls__.copy()
    __dependencies__ = svc.worldSpaceClient.__dependencies__[:]
    __dependencies__.extend(['navigation'])

    def OnLoadEntityScene(self, sceneID):
        self.LogInfo('Loading worldspace for entity scene', sceneID)
        self.LoadWorldSpaceInstance(sceneID)
        self.WaitForInstance(sceneID)
        self.LogInfo('Done Loading worldspace for entity scene', sceneID)
        if sceneID == session.worldspaceid:
            self.activeWorldSpace = session.worldspaceid

    def OnUnloadEntityScene(self, sceneID):
        pass

    def OnEntitySceneUnloaded(self, sceneID):
        self.UnloadWorldSpaceInstance(sceneID)

    def GetWorldSpaceTypeIDFromWorldSpaceID(self, worldSpaceID):
        if util.IsStation(worldSpaceID):
            stationType = cfg.invtypes.Get(eve.stationItem.stationTypeID)
            stationRace = stationType['raceID']
            configVals = sm.GetService('machoNet').GetGlobalConfig()
            if stationRace == const.raceCaldari:
                if configVals.get('CaldariCQEnabled', '1') == '1':
                    return const.typeCaldariCaptainsQuarters
            else:
                if stationRace == const.raceMinmatar:
                    return const.typeMinmatarCaptainsQuarters
                if stationRace == const.raceAmarr:
                    if configVals.get('AmarrCQEnabled', '1') == '1':
                        return const.typeAmarrCaptainsQuarters
                elif stationRace == const.raceGallente:
                    if configVals.get('GallenteCQEnabled', '1') == '1':
                        return const.typeGallenteCaptainsQuarters
                elif stationRace == const.raceJove:
                    if configVals.get('GallenteCQEnabled', '1') == '1':
                        return const.typeGallenteCaptainsQuarters
            return const.typeMinmatarCaptainsQuarters
        return sm.RemoteSvc('worldSpaceServer').GetWorldSpaceTypeIDFromWorldSpaceID(worldSpaceID)

    def GetWorldSpaceInventoryTypeIDFromWorldSpaceID(self, worldSpaceID):
        worldSpaceTypeID = self.GetWorldSpaceTypeIDFromWorldSpaceID(worldSpaceID)
        return worldSpaceTypeID

    def GetWorldSpaceSafeSpot(self, worldSpaceID):
        worldspaceDesc = cfg.worldspaces.Get(self.GetWorldSpaceInventoryTypeIDFromWorldSpaceID(worldSpaceID))
        safespotloc = (worldspaceDesc.safeSpotX, worldspaceDesc.safeSpotY, worldspaceDesc.safeSpotZ)
        safespotrot = (worldspaceDesc.safeSpotRotY, 0, 0)
        return (safespotloc, safespotrot)