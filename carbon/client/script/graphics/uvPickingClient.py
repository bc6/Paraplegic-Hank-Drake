import service
import trinity
import geo2

class UVPickingComponent:
    __guid__ = 'component.UVPickingComponent'

    def __init__(self):
        self.areaName = ''




class UVPickingClient(service.Service):
    __guid__ = 'svc.uvPickingClient'
    __displayname__ = 'UV CPU Picking Service'
    __componentTypes__ = ['uvPicking']

    def __init__(self):
        service.Service.__init__(self)



    def Run(self, *etc):
        service.Service.Run(self, *etc)



    def CreateComponent(self, name, state):
        component = UVPickingComponent()
        if 'areaName' in state:
            component.areaName = state['areaName']
        return component



    def Pick(self, entity, rayOrigin, rayDirection):
        pickingComponent = entity.GetComponent('uvPicking')
        if pickingComponent is None:
            return 
        if pickingComponent.areaName is None or pickingComponent.areaName == '':
            return 
        placeableComponent = entity.GetComponent('interiorPlaceable')
        if placeableComponent is None:
            return 
        if placeableComponent.renderObject is None:
            return 
        object = placeableComponent.renderObject
        if object.placeableRes is None:
            return 
        model = object.placeableRes.visualModel
        if model is None:
            return 
        pickingGeometry = None
        pickingMesh = None
        pickingArea = None
        pickingCount = None
        for mesh in model.meshes:
            for area in mesh.transparentAreas:
                if area.name == pickingComponent.areaName:
                    pickingGeometry = mesh.geometry
                    pickingMesh = mesh.meshIndex
                    pickingArea = area.index
                    pickingCount = area.count
                    break

            for area in mesh.opaquePrepassAreas:
                if area.name == pickingComponent.areaName:
                    pickingGeometry = mesh.geometry
                    pickingMesh = mesh.meshIndex
                    pickingArea = area.index
                    pickingCount = area.count
                    break


        if pickingGeometry is not None:
            world = ((object.transform._11,
              object.transform._12,
              object.transform._13,
              object.transform._14),
             (object.transform._21,
              object.transform._22,
              object.transform._23,
              object.transform._24),
             (object.transform._31,
              object.transform._32,
              object.transform._33,
              object.transform._34),
             (object.transform._41,
              object.transform._42,
              object.transform._43,
              object.transform._44))
            worldInv = geo2.MatrixInverse(world)
            origin = geo2.Vec3Transform(rayOrigin, worldInv)
            direction = geo2.Vec3TransformNormal(rayDirection, worldInv)
            for area in range(pickingCount):
                result = pickingGeometry.GetRayAreaIntersection(origin, direction, pickingMesh, pickingArea + area, trinity.TriGeometryCollisionResultFlags.ANY)
                if result is not None:
                    return result[1]





