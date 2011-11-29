import cef
import service
import graphicWrappers
import collections
import geo2
import trinity

class PhysicalPortalClientComponent:
    __guid__ = 'component.PhysicalPortalClientComponent'


class PhysicalPortalClient(service.Service):
    __guid__ = 'svc.physicalPortalClient'
    __componentTypes__ = [cef.PhysicalPortalComponentView.GetComponentCodeName()]
    __dependencies__ = ['graphicClient']

    def __init__(self):
        service.Service.__init__(self)
        self.isServiceReady = False



    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.isServiceReady = True



    def CreateComponent(self, name, state):
        component = PhysicalPortalClientComponent()
        renderObject = trinity.Tr2InteriorPhysicalPortal()
        component.renderObject = renderObject
        graphicWrappers.Wrap(renderObject)
        renderObject.maxBounds = (state['scaleX'], state['scaleY'], state['scaleZ'])
        renderObject.minBounds = (-state['scaleX'], -state['scaleY'], -state['scaleZ'])
        component.cellA = state['cellA']
        component.cellB = state['cellB']
        return component



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['Has RenderObject'] = component.renderObject is not None
        if component.renderObject:
            report['Position'] = component.renderObject.GetPosition()
            report['Rotation'] = component.renderObject.GetRotationYawPitchRoll()
            report['Scale'] = component.renderObject.GetScale()
            report['cellA'] = component.cellA
            report['cellB'] = component.cellB
        return report



    def PrepareComponent(self, sceneID, entityID, component):
        component.renderObject.name = str(entityID)
        scene = self.graphicClient.GetScene(sceneID)
        component.renderObject.AddToScene(scene)



    def SetupComponent(self, entity, component):
        positionComponent = entity.GetComponent('position')
        if positionComponent:
            component.renderObject.SetPosition(positionComponent.position)
            if hasattr(component.renderObject, 'SetRotationYawPitchRoll'):
                component.renderObject.SetRotationYawPitchRoll(geo2.QuaternionRotationGetYawPitchRoll(positionComponent.rotation))
        scene = self.graphicClient.GetScene(entity.scene.sceneID)
        cells = scene.cells
        if component.cellA and component.cellB:
            cellAObj = scene._GetCell(component.cellA)
            cellBObj = scene._GetCell(component.cellB)
            component.renderObject.ConnectCells(cellAObj, cellBObj)



    def UnRegisterComponent(self, entity, component):
        scene = self.graphicClient.GetScene(entity.scene.sceneID)
        component.renderObject.RemoveFromScene(scene)




