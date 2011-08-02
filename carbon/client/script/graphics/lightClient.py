import service
import graphicWrappers
import blue
import collections
import geo2
import trinity
import uthread

class LightClient(service.Service):
    __guid__ = 'graphics.LightClient'
    __dependencies__ = ['graphicClient']
    __notifyevents__ = ['OnGraphicSettingsChanged']

    def __init__(self):
        service.Service.__init__(self)
        self.lightEntities = []



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['Has RenderObject'] = component.renderObject is not None
        if component.renderObject:
            report['Position'] = component.renderObject.GetPosition()
        return report



    def RegisterComponent(self, entity, component):
        self.lightEntities.append(entity)



    def SetupComponent(self, entity, component):
        positionComponent = entity.GetComponent('position')
        if positionComponent:
            component.renderObject.position = positionComponent.position
            if hasattr(component.renderObject, 'SetRotationYawPitchRoll'):
                component.renderObject.SetRotationYawPitchRoll(geo2.QuaternionRotationGetYawPitchRoll(positionComponent.rotation))
        self.ApplyShadowCasterType(entity)
        self.ApplyPerformanceLevelLightDisable(entity)



    def PrepareComponent(self, sceneID, entityID, component):
        if component.renderObject is None:
            return 
        if hasattr(component.renderObject, 'name'):
            component.renderObject.name = str(entityID)
        scene = self.graphicClient.GetScene(sceneID)
        scene.AddLightSource(component.renderObject)



    def UnRegisterComponent(self, entity, component):
        scene = self.graphicClient.GetScene(entity.scene.sceneID)
        scene.RemoveLightSource(component.renderObject)
        self.lightEntities.remove(entity)



    def ApplyShadowCasterType(self, entity):
        pass



    def ApplyPerformanceLevelLightDisable(self, entity):
        pass



    def OnGraphicSettingsChanged(self, changes):
        for entity in self.lightEntities:
            self.ApplyShadowCasterType(entity)
            self.ApplyPerformanceLevelLightDisable(entity)





