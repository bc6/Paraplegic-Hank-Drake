import cef
import service
import graphicWrappers
import collections
import geo2
import trinity

class OccluderClientComponent:
    __guid__ = 'component.LightClientComponent'


class OccluderClient(service.Service):
    __guid__ = 'svc.occluderClient'
    __componentTypes__ = [cef.OccluderComponentView.GetComponentCodeName()]
    __dependencies__ = ['graphicClient']

    def __init__(self):
        service.Service.__init__(self)
        self.isServiceReady = False



    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.isServiceReady = True



    def CreateComponent(self, name, state):
        component = OccluderClientComponent()
        component.cellName = state.get('cellName', '')
        renderObject = trinity.Tr2InteriorOccluder()
        component.renderObject = renderObject
        graphicWrappers.Wrap(renderObject)
        renderObject.SetScale((state.get('scaleX', 1), state.get('scaleY', 1), state.get('scaleZ', 1)))
        return component



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['Has RenderObject'] = component.renderObject is not None
        if component.renderObject:
            report['Position'] = component.renderObject.GetPosition()
            report['Rotation'] = component.renderObject.GetRotationYawPitchRoll()
            report['Scale'] = component.renderObject.GetScale()
        return report



    def PrepareComponent(self, sceneID, entityID, component):
        component.renderObject.name = str(entityID)
        scene = self.graphicClient.GetScene(sceneID)
        component.renderObject.AddToScene(scene)
        component.renderObject.SetCell(component.cellName)



    def SetupComponent(self, entity, component):
        positionComponent = entity.GetComponent('position')
        if positionComponent:
            component.renderObject.SetPosition(positionComponent.position)
            if hasattr(component.renderObject, 'SetRotationYawPitchRoll'):
                component.renderObject.SetRotationYawPitchRoll(geo2.QuaternionRotationGetYawPitchRoll(positionComponent.rotation))




