#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/particleObjectClient.py
import cef
import service
import trinity
import util
import GameWorld
import uthread
import weakref
import blue

class ParticleObjectComponent:
    __guid__ = 'component.ParticleObjectComponent'

    def __init__(self):
        self.redFile = ''
        self.positionOffset = (0, 0, 0)
        self.trinityObject = None
        self.callback = None
        self.depthOffset = 0
        self.maxParticleRadius = 0
        self.shBoundsMin = (0, 0, 0)
        self.shBoundsMax = (0, 0, 0)


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
        if 'shBoundsMin' in state:
            component.shBoundsMin = util.UnpackStringToTuple(state['shBoundsMin'])
        if 'shBoundsMax' in state:
            component.shBoundsMax = util.UnpackStringToTuple(state['shBoundsMax'])
        component.depthOffset = float(state.get('depthOffset', 0))
        component.maxParticleRadius = float(state.get('maxParticleRadius', 0))
        return component

    def WaitForGeometry(self, renderObject):
        if renderObject is None:
            return
        for mesh in renderObject.meshes:
            geometry = mesh.geometry
            if geometry is None:
                continue
            while geometry.isLoading and not geometry.isPrepared:
                blue.synchro.Yield()

    def PrepareComponent(self, sceneID, entityID, component):
        if component.redFile == '':
            return
        if not sm.GetService('device').GetAppFeatureState('Interior.ParticlesEnabled', True):
            return
        component.trinityObject = trinity.Load(component.redFile)
        self.WaitForGeometry(component.trinityObject)
        if hasattr(component.trinityObject, 'depthOffset'):
            component.trinityObject.depthOffset = component.depthOffset
        if hasattr(component.trinityObject, 'maxParticleRadius'):
            component.trinityObject.maxParticleRadius = component.maxParticleRadius
        if hasattr(component.trinityObject, 'shBoundsMin'):
            component.trinityObject.shBoundsMin = component.shBoundsMin
        if hasattr(component.trinityObject, 'shBoundsMax'):
            component.trinityObject.shBoundsMax = component.shBoundsMax
        component.trinityObject.BindLowLevelShaders()

    def SetupComponent(self, entity, component):
        if component.trinityObject is None:
            return
        self.AddToScene(entity, component)

    def AddToScene(self, entity, component):
        if component.trinityObject is None:
            component.trinityObject = trinity.Load(component.redFile)
        if hasattr(component.trinityObject, 'depthOffset'):
            component.trinityObject.depthOffset = component.depthOffset
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