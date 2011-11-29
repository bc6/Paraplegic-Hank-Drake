import cef
import service
import trinity
import util
import GameWorld
import uthread
import weakref

class ParticleObjectComponent:
    __guid__ = 'component.ParticleObjectComponent'

    def __init__(self):
        self.redFile = ''
        self.positionOffset = (0, 0, 0)
        self.trinityObject = None
        self.callback = None




class ParticleObjectClient(service.Service):
    __guid__ = 'svc.particleObjectClient'
    __displayname__ = 'Particle Object Client Service'
    __dependencies__ = ['graphicClient']
    __notifyevents__ = ['OnGraphicSettingsChanged']
    __componentTypes__ = [cef.ParticleObjectComponentView.GetComponentCodeName()]

    def __init__(self):
        service.Service.__init__(self)
        self.particleObjectEntities = weakref.WeakSet()



    def Run(self, *etc):
        service.Service.Run(self, *etc)



    def CreateComponent(self, name, state):
        component = ParticleObjectComponent()
        if 'redFile' in state:
            component.redFile = state['redFile']
        if 'positionOffset' in state:
            component.positionOffset = util.UnpackStringToTuple(state['positionOffset'])
        component.depthOffset = float(state.get('depthOffset', 0))
        return component



    def PrepareComponent(self, sceneID, entityID, component):
        if component.redFile == '':
            return 
        if not sm.GetService('device').GetAppFeatureState('Interior.ParticlesEnabled', True):
            return 
        component.trinityObject = trinity.Load(component.redFile)
        if hasattr(component.trinityObject, 'particleSystems'):
            for system in component.trinityObject.particleSystems:
                system.depthOffset = component.depthOffset




    def SetupComponent(self, entity, component):
        if component.trinityObject is None:
            return 
        self.AddToScene(entity, component)



    def AddToScene(self, entity, component):
        if component.trinityObject is None:
            component.trinityObject = trinity.Load(component.redFile)
        if hasattr(component.trinityObject, 'particleSystems'):
            for system in component.trinityObject.particleSystems:
                system.depthOffset = component.depthOffset

        scene = self.graphicClient.GetScene(entity.scene.sceneID)
        if scene:
            scene.AddDynamic(component.trinityObject)
        positionComponent = entity.GetComponent('position')
        if positionComponent:
            component.callback = GameWorld.PlacementObserverWrapper(component.trinityObject)
            positionComponent.RegisterPlacementObserverWrapper(component.callback)



    def RegisterComponent(self, entity, component):
        self.particleObjectEntities.add(entity)



    def UnRegisterComponent(self, entity, component):
        if entity in self.particleObjectEntities:
            self.particleObjectEntities.remove(entity)
        if component.trinityObject is None:
            return 
        self.RemoveFromScene(entity, component)
        component.destroyed = True



    def RemoveFromScene(self, entity, component):
        if component.callback is not None and entity.HasComponent('position'):
            entity.GetComponent('position').UnRegisterPlacementObserverWrapper(component.callback)
            component.callback = None
        scene = self.graphicClient.GetScene(entity.scene.sceneID)
        if scene:
            scene.RemoveDynamic(component.trinityObject)
        component.trinityObject = None



    def OnGraphicSettingsChanged(self, changes):
        particlesEnabled = sm.GetService('device').GetAppFeatureState('Interior.ParticlesEnabled', True)
        with uthread.BlockTrapSection():
            for entity in self.particleObjectEntities:
                particleComponent = entity.GetComponent('particleObject')
                if not particlesEnabled and particleComponent.trinityObject is not None:
                    self.RemoveFromScene(entity, particleComponent)
                elif particlesEnabled and particleComponent.trinityObject is None:
                    self.AddToScene(entity, particleComponent)





