#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/uvPickingClient.py
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

    def PickEntity(self, entity, rayOrigin, rayDirection):
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
        return self.PickObject(object, rayOrigin, rayDirection, areaName=pickingComponent.areaName)

    def PickObject(self, obj, rayOrigin, rayDirection, areaName = None):
        if obj.placeableRes is None:
            return
        model = obj.placeableRes.visualModel
        if model is None:
            return
        pickingGeometry = None
        pickingMesh = None
        pickingArea = None
        pickingCount = None
        for mesh in model.meshes:
            for area in mesh.transparentAreas:
                if areaName is None or area.name == areaName:
                    pickingGeometry = mesh.geometry
                    pickingMesh = mesh.meshIndex
                    pickingArea = area.index
                    pickingCount = area.count
                    break

            for area in mesh.opaquePrepassAreas:
                if areaName is None or area.name == areaName:
                    pickingGeometry = mesh.geometry
                    pickingMesh = mesh.meshIndex
                    pickingArea = area.index
                    pickingCount = area.count
                    break

        if pickingGeometry is not None:
            world = ((obj.transform._11,
              obj.transform._12,
              obj.transform._13,
              obj.transform._14),
             (obj.transform._21,
              obj.transform._22,
              obj.transform._23,
              obj.transform._24),
             (obj.transform._31,
              obj.transform._32,
              obj.transform._33,
              obj.transform._34),
             (obj.transform._41,
              obj.transform._42,
              obj.transform._43,
              obj.transform._44))
            worldInv = geo2.MatrixInverse(world)
            origin = geo2.Vec3Transform(rayOrigin, worldInv)
            direction = geo2.Vec3TransformNormal(rayDirection, worldInv)
            for area in range(pickingCount):
                result = pickingGeometry.GetRayAreaIntersection(origin, direction, pickingMesh, pickingArea + area, trinity.TriGeometryCollisionResultFlags.ANY)
                if result is not None:
                    return result