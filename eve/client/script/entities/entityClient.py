import svc
import util
import uix

class EveEntityClient(svc.entityClient):
    __guid__ = 'svc.eveEntityClient'
    __replaceservice__ = 'entityClient'
    __notifyevents__ = ['ProcessSessionChange']
    __dependencies__ = svc.entityClient.__dependencies__[:]
    __dependencies__.extend(('proximity', 'movementClient', 'paperDollClient', 'apertureClient', 'gameWorldClient', 'collisionMeshClient', 'playerComponentClient', 'animationClient', 'zactionClient', 'perceptionClient', 'decisionTreeClient', 'contextMenuClient', 'proximityTrigger', 'position', 'boundingVolume', 'aimingClient', 'simpleTestClient', 'netStateClient', 'entitySpawnClient', 'selectionClient'))
    __entitysystems__ = svc.entityClient.__entitysystems__[:]
    __entitysystems__.extend(('audio', 'selectionClient', 'contextMenuClient', 'infoClient', 'tutorial', 'netStateClient', 'bracketClient', 'proximityTrigger', 'shipHologram', 'holoscreen', 'spawnLocationClient'))

    def Run(self, *etc):
        svc.entityClient.Run(self)



    def ProcessSessionChange(self, isRemote, session, change):
        if 'worldspaceid' in change:
            (leavingWorldSpaceID, enteringWorldSpaceID,) = change['worldspaceid']
            if leavingWorldSpaceID != enteringWorldSpaceID and not self.IsClientSideOnly(leavingWorldSpaceID):
                self.UnloadEntityScene(leavingWorldSpaceID)
            if enteringWorldSpaceID and not self.IsClientSideOnly(enteringWorldSpaceID):
                self.LoadEntitySceneAndBlock(enteringWorldSpaceID)



    def IsClientSideOnly(self, sceneID):
        return util.IsStation(sceneID)




