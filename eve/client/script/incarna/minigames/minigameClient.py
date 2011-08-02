import trinity
import service
import moniker
import entities
import minigames
import minigameConst
DEFAULT_DISABLESEAMLESS = 1

class MinigameClient(service.Service):
    __guid__ = 'svc.minigameClient'
    __servicename__ = 'svc.minigameClient'
    __displayname__ = 'Incarna Client Minigame Service'
    __dependencies__ = ['entityClient']
    __exportedcalls__ = {'StartMinigame': [service.ROLE_ANY]}
    __notifyevents__ = ['OnMinigameServerMessage']
    __componentTypes__ = ['minigameLogic', 'minigameConfig']

    def Run(self, memStream = None):
        self.managesEntity = []
        self.componentCount = 0



    def OnDoubleClick(self, entityID):
        if entityID is not None and entityID in self.managesEntity:
            self.StartMinigame(entityID)



    def CreateComponent(self, name, state):
        if name == 'minigameLogic':
            component = minigames.MinigameControllerClientComponent(state)
        elif name == 'minigameConfig':
            component = minigames.MinigameConfigClientComponent(state)
        return component



    def SetupComponent(self, entity, component):
        if entity.entityID not in self.managesEntity:
            self.managesEntity.append(entity.entityID)
        component.entityID = entity.entityID



    def RegisterComponent(self, entity, component):
        if self.componentCount == 0:
            sm.GetService('mouseInput').RegisterCallback(const.INPUT_TYPE_DOUBLECLICK, self.OnDoubleClick)
        self.componentCount += 1
        interiorPlaceable = entity.components['interiorPlaceable']
        interiorPlaceable.renderObject.translation = entity.components['position'].position
        interiorPlaceable.renderObject.rotation = entity.components['position'].rotation
        if isinstance(component, minigames.MinigameControllerClientComponent):
            audioEmitter = None
            if hasattr(entity.components['audioEmitter'], 'emitter'):
                audioEmitter = entity.components['audioEmitter'].emitter
            configComponent = entity.components['minigameConfig']
            component.minigameController.Setup(entity.entityID, interiorPlaceable.renderObject, configComponent, component.state, audioEmitter)



    def UnRegisterComponent(self, entity, component):
        if component is minigames.MinigameControllerClientComponent:
            component.minigameController.Terminate()
        self.componentCount -= 1
        if self.componentCount == 0:
            sm.GetService('mouseInput').UnRegisterCallback(const.INPUT_TYPE_DOUBLECLICK, self.OnDoubleClick)
            self.managesEntity = []



    def StartMinigame(self, entityID):
        scene = self.entityClient.GetEntityScene(session.worldspaceid)
        if entityID in scene.entities:
            entity = scene.entities[entityID]
            component = entity.components['minigameLogic']
            component.JoinGame()



    def OnMinigameServerMessage(self, sceneID, entityID, *args):
        scene = self.entityClient.GetEntityScene(session.worldspaceid)
        if entityID in scene.entities:
            entity = scene.entities[entityID]
            component = entity.components['minigameLogic']
            component.OnMinigameServerMessage(entityID, *args)




