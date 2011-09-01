import service
import trinity
import util
import geo2

class ShipHologramComponent:
    __guid__ = 'component.shipHologram'

    def __init__(self):
        self.positionOffset = (0, 0.7, 0)
        self.spotlightOrigin = (0, 0.05, 0)
        self.color = (1, 0.7, 0.5)
        self.shipTargetSize = 0.5
        self.graphicLoaded = False




class ShipHologramComponentManager(service.Service):
    __guid__ = 'svc.shipHologram'
    __displayname__ = 'Ship Hologram Component Client Service'
    __componentTypes__ = ['shipHologram']
    __notifyevents__ = ['OnActiveShipModelChange']
    __dependencies__ = ['station']

    def __init__(self):
        service.Service.__init__(self)
        self.entities = []



    def Run(self, *etc):
        service.Service.Run(self, *etc)



    def CreateComponent(self, name, state):
        component = ShipHologramComponent()
        if 'positionOffset' in state:
            component.positionOffset = util.UnpackStringToTuple(state['positionOffset'])
        if 'spotlightOrigin' in state:
            component.spotlightOrigin = util.UnpackStringToTuple(state['spotlightOrigin'])
        if 'color' in state:
            component.color = util.UnpackStringToTuple(state['color'])
        if 'shipTargetSize' in state:
            component.shipTargetSize = state['shipTargetSize']
        return component



    def PrepareComponent(self, sceneID, entityID, component):
        pass



    def SetupComponent(self, entity, component):
        interiorPlaceableComponent = entity.GetComponent('interiorPlaceable')
        hologramComponent = entity.GetComponent('shipHologram')
        if interiorPlaceableComponent is not None and hologramComponent is not None:
            shipModel = self.station.GetActiveShipModel()
            activeShipID = self.station.GetActiveShip()
            hologramComponent.graphicLoaded = True
            self.SetShipModel(entity, shipModel, activeShipID)



    def RegisterComponent(self, entity, component):
        self.entities.append(entity)



    def UnRegisterComponent(self, entity, component):
        self.entities.remove(entity)
        hologramComponent = entity.GetComponent('shipHologram')
        if hologramComponent is None or not hologramComponent.graphicLoaded:
            return 
        interiorPlaceable = entity.GetComponent('interiorPlaceable')
        if interiorPlaceable is None:
            return 
        visualModel = interiorPlaceable.renderObject.placeableRes.visualModel
        for each in visualModel.meshes:
            if each.name == 'shipHologramMesh':
                visualModel.meshes.remove(each)
                break




    def UpdateShipModels(self, shipModel = None, activeShipID = None):
        if shipModel == None:
            shipModel = self.station.GetActiveShipModel()
        if activeShipID is None:
            activeShipID = self.station.GetActiveShip()
        for each in self.entities:
            self.SetShipModel(each, shipModel, activeShipID)




    def SetShipModel(self, entity, model, activeShipID):
        hologramComponent = entity.GetComponent('shipHologram')
        if hologramComponent is None or not hologramComponent.graphicLoaded:
            return 
        interiorPlaceable = entity.GetComponent('interiorPlaceable')
        if interiorPlaceable is None:
            return 
        effect = trinity.Load('res:/graphics/interior/effect/hologram/shipHologramEffect.red')
        targetPlaceable = interiorPlaceable.renderObject
        targetVisual = targetPlaceable.placeableRes.visualModel
        mesh = None
        for each in targetVisual.meshes:
            if each.name == 'shipHologramMesh':
                mesh = each
                break

        if mesh is not None:
            targetVisual.meshes.remove(mesh)
        targetPlaceable.BoundingBoxReset()
        if model is None:
            return 
        if activeShipID is None:
            return 
        mesh = trinity.Tr2Mesh()
        mesh.name = 'shipHologramMesh'
        mesh.geometryResPath = model.mesh.geometryResPath
        maxIndex = 0
        for area in model.mesh.opaqueAreas:
            maxIndex = max(maxIndex, area.index)

        for area in model.mesh.decalAreas:
            maxIndex = max(maxIndex, area.index)

        for area in model.mesh.transparentAreas:
            maxIndex = max(maxIndex, area.index)

        meshArea = trinity.Tr2MeshArea()
        meshArea.effect = effect
        meshArea.count = maxIndex + 1
        mesh.transparentAreas.append(meshArea)
        effect.BindLowLevelShader([])
        (bbMinOriginal, bbMaxOriginal,) = targetVisual.GetBoundingBoxInLocalSpace()
        bbMinOriginal = (bbMinOriginal.x, bbMinOriginal.y, bbMinOriginal.z)
        bbMaxOriginal = (bbMaxOriginal.x, bbMaxOriginal.y, bbMaxOriginal.z)
        param = effect.parameters['ScalingAndOffset']
        x = param.x = hologramComponent.positionOffset[0]
        y = param.y = hologramComponent.positionOffset[1]
        z = param.z = hologramComponent.positionOffset[2]
        scale = hologramComponent.shipTargetSize / model.boundingSphereRadius
        boundingRadius = model.boundingSphereRadius
        if boundingRadius > 1000.0:
            boundingRadius = 1000.0
        if boundingRadius < 30.0:
            boundingRadius = 30.0
        scale *= 0.6 + 0.4 * boundingRadius / 970.0
        param.w = scale
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if getattr(dogmaLocation.GetDogmaItem(activeShipID), 'groupID', None) == const.groupCapsule:
            param.w *= 0.6
        param = effect.parameters['Color']
        param.x = hologramComponent.color[0]
        param.y = hologramComponent.color[1]
        param.z = hologramComponent.color[2]
        param = effect.parameters['SpotlightOrigin']
        param.x = hologramComponent.spotlightOrigin[0]
        param.y = hologramComponent.spotlightOrigin[1]
        param.z = hologramComponent.spotlightOrigin[2]
        targetVisual.meshes.append(mesh)
        trinity.WaitForResourceLoads()
        (bbMin, bbMax,) = model.GetLocalBoundingBox()
        if bbMin is None or bbMax is None:
            return 
        maxBounds = max(abs(bbMin.x), max(bbMax.x, max(abs(bbMin.z), bbMax.z)))
        bbMin = (-maxBounds, bbMin.y, -maxBounds)
        bbMax = (maxBounds, bbMax.y, maxBounds)
        bbMin = geo2.Vec3Scale(bbMin, scale)
        bbMax = geo2.Vec3Scale(bbMax, scale)
        bbMin = geo2.Vec3Add(bbMin, (x, y, z))
        bbMax = geo2.Vec3Add(bbMax, (x, y, z))
        bbMin = geo2.Min(bbMin, bbMinOriginal)
        bbMax = geo2.Max(bbMax, bbMaxOriginal)
        targetPlaceable.BoundingBoxOverride(bbMin, bbMax)



    def OnActiveShipModelChange(self, model):
        self.UpdateShipModels(model)




