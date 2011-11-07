import service
import trinity
import util
import geo2
import uthread

class LensFlareComponent:
    __guid__ = 'component.LensFlareComponent'

    def __init__(self):
        self.redFile = ''
        self.positionOffset = (0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.occluderSize = 0.1
        self.trinityObject = None




class LensFlareClient(service.Service):
    __guid__ = 'svc.lensFlareClient'
    __displayname__ = 'Lens Flare Client Service'
    __dependencies__ = ['graphicClient']
    __notifyevents__ = ['OnGraphicSettingsChanged']
    __componentTypes__ = ['lensFlare']

    def __init__(self):
        service.Service.__init__(self)
        self.flareEntities = set()



    def Run(self, *etc):
        service.Service.Run(self, *etc)



    def CreateComponent(self, name, state):
        component = LensFlareComponent()
        if 'redFile' in state:
            component.redFile = state['redFile']
        if 'positionOffset' in state:
            component.positionOffset = util.UnpackStringToTuple(state['positionOffset'])
        if 'color' in state:
            component.color = util.UnpackStringToTuple(state['color'])
        if 'occluderSize' in state:
            component.occluderSize = state['occluderSize']
        return component



    def PrepareComponent(self, sceneID, entityID, component):
        if component.redFile == '':
            return 
        if not sm.GetService('device').GetAppFeatureState('Interior.LensflaresEnabled', True):
            return 
        component.trinityObject = trinity.Load(component.redFile)



    def SetupComponent(self, entity, component):
        if component.trinityObject is None:
            return 
        self.AddToScene(entity, component)



    def AddToScene(self, entity, component):
        if component.trinityObject is None:
            component.trinityObject = trinity.Load(component.redFile)
        scene = self.graphicClient.GetScene(entity.scene.sceneID)
        if scene:
            scene.AddDynamic(component.trinityObject)
        positionComponent = entity.GetComponent('position')
        if positionComponent is not None and component.trinityObject is not None:
            component.trinityObject.transform = geo2.MatrixMultiply(geo2.MatrixRotationQuaternion(positionComponent.rotation), geo2.MatrixTranslation(positionComponent.position[0], positionComponent.position[1], positionComponent.position[2]))



    def RegisterComponent(self, entity, component):
        self.flareEntities.add(entity)



    def UnRegisterComponent(self, entity, component):
        self.flareEntities.remove(entity)
        if component.trinityObject is None:
            return 
        self.RemoveFromScene(entity, component)
        component.destroyed = True



    def RemoveFromScene(self, entity, component):
        scene = self.graphicClient.GetScene(entity.scene.sceneID)
        if scene:
            scene.RemoveDynamic(component.trinityObject)
        component.trinityObject = None



    def OnGraphicSettingsChanged(self, changes):
        flaresEnabled = sm.GetService('device').GetAppFeatureState('Interior.LensflaresEnabled', True)
        with uthread.BlockTrapSection():
            for entity in self.flareEntities:
                flareComponent = entity.GetComponent('lensFlare')
                if not flaresEnabled and flareComponent.trinityObject is not None:
                    self.RemoveFromScene(entity, flareComponent)
                elif flaresEnabled and flareComponent.trinityObject is None:
                    self.AddToScene(entity, flareComponent)





