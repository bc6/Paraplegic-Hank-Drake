import GameWorld
import service
import AI

class AimingClient(AI.aimingCommon):
    __guid__ = 'svc.aimingClient'
    __notifyevents__ = []
    __dependencies__ = ['gameWorldClient', 'perceptionClient']

    def __init__(self):
        self.aimingServer = None
        AI.aimingCommon.__init__(self)



    def Run(self, *etc):
        self.aimingServer = sm.RemoteSvc('aimingServer')
        self.gameWorldService = self.gameWorldClient
        service.Service.Run(self, etc)



    def PrepareComponent(self, sceneID, entityID, component):
        if sceneID not in self.sceneManagers:
            self.LogError('SceneID in prepare aiming component has no previous manager ', sceneID, entityID)
            return 
        component.entData = AI.AimingEntityData()
        component.entData.entID = entityID



    def MakeAimingManager(self):
        return GameWorld.AimingManagerClient()



    def GetTargetEntityID(self, entity, targetType):
        if entity.scene.sceneID not in self.sceneManagers:
            self.LogError("Trying to get targets for an entity that doesn't have a scene", entity.entityID)
            return None
        aimingManager = self.sceneManagers[entity.scene.sceneID]
        targetedEntityID = aimingManager.GetTargetEntityID(entity.entityID, targetType)
        if targetedEntityID == 0:
            return None
        return targetedEntityID



    def IsTargetClientServerValid(self, targetClientServerFlag):
        return targetClientServerFlag & const.aiming.AIMING_CLIENTSERVER_FLAG_CLIENT




