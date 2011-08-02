import svc
import util

class EveEntityClient(svc.entityClient):
    __guid__ = 'svc.eveEntityClient'
    __replaceservice__ = 'entityClient'
    __notifyevents__ = ['ProcessSessionChange']
    __dependencies__ = svc.entityClient.__dependencies__[:]
    __dependencies__.extend(('proximity', 'movementClient', 'paperDollClient', 'apertureClient', 'gameWorldClient', 'minigameClient', 'collisionMeshClient', 'playerComponentClient', 'animationClient', 'zactionClient', 'perceptionClient', 'contextMenuClient', 'proximityTrigger', 'position', 'boundingVolume', 'elevatorClient', 'aimingClient', 'simpleTestClient', 'netStateClient', 'entitySpawnClient', 'selectionClient'))
    __entitysystems__ = svc.entityClient.__entitysystems__[:]
    __entitysystems__.extend(('audio', 'selectionClient', 'contextMenuClient', 'infoClient', 'tutorial', 'netStateClient', 'bracketClient', 'proximityTrigger', 'shipHologram'))

    def Run(self, *etc):
        svc.entityClient.Run(self)



    def ProcessSessionChange(self, isRemote, session, change):
        if 'worldspaceid' in change:
            (leavingWorldSpaceID, enteringWorldSpaceID,) = change['worldspaceid']
            if util.IsStation(enteringWorldSpaceID) and not prefs.GetValue('loadstationenv', 1):
                return 
            if leavingWorldSpaceID != enteringWorldSpaceID and leavingWorldSpaceID in self.scenes:
                self.UnloadEntityScene(leavingWorldSpaceID)
            if enteringWorldSpaceID:
                scene = self.LoadEntitySceneAndBlock(enteringWorldSpaceID)



    def IsClientSideOnly(self, sceneID):
        return util.IsStation(sceneID)




