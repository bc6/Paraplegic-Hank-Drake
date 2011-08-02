import blue
import service
import world
import trinity
import math
import util
import geo2
import uthread
import GameWorld
import entities
from collections import defaultdict

class RoomEditClient(service.Service):
    __guid__ = 'svc.roomEditClient'
    __dependencies__ = ['worldSpaceClient']
    __componentTypes__ = ['roomEditPlaceable']
    ALLOWED_EPSILON_DEVIATION = 1e-05

    def __init__(self):
        service.Service.__init__(self)



    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.hackObjectID = None
        self.inEditMode = False
        self.backupRoomData = None
        self.backupItemEntitieStates = {}
        self.roomDataByInstance = {}
        self.roomEditGridGW = None
        self.showRoomEditGrids = True
        self.placeableGridMeshes = {}
        self.roomEditGridGW = GameWorld.GameWorld()
        self.roomEditGridGW.InitWorld('RoomEditGrid', const.GAMEWORLD_INIT_DATA, False, True)
        self.gridTypes = {}
        self.gridOwnedPlaceables = defaultdict(set)
        self.storedGridOwnedPlaceables = []



    def ShutDown(self):
        if self.inEditMode:
            self._ExitEditMode(revert=True)
        self.roomEditGridGW.ShutdownWorld()
        self.roomEditGridGW = None



    def GetNextFakeItemID(self):
        if not self.hackObjectID:
            roomData = self.GetRoomData(session.worldspaceid)
            self.hackObjectID = 0
            for itemID in roomData.placeables:
                if itemID > self.hackObjectID:
                    self.hackObjectID = itemID

            if not self.hackObjectID:
                self.hackObjectID = 1337042000
        self.hackObjectID += 1
        return self.hackObjectID



    def CreateComponent(self, name, state):
        component = entities.RoomEditPlaceableClientComponent(state)
        self._AddPlaceableWorldSpaceObject(component)
        return component



    def TearDownComponent(self, entity, component):
        self._RemovePlaceableWorldSpaceObject(component)



    def _AddPlaceableWorldSpaceObject(self, entityComponent):
        ws = self.worldSpaceClient.GetWorldSpaceInstance(entityComponent.worldspaceID)
        fakeObjRow = util.KeyVal()
        fakeObjRow.objectName = entityComponent.typeName
        fakeObjRow.graphicID = entityComponent.graphicID
        (fakeObjRow.posX, fakeObjRow.posY, fakeObjRow.posZ,) = entityComponent.translation
        (fakeObjRow.rotX, fakeObjRow.rotY, fakeObjRow.rotZ,) = entityComponent.rotation
        (fakeObjRow.scaleX, fakeObjRow.scaleY, fakeObjRow.scaleZ,) = (1.0, 1.0, 1.0)
        ws.AddObject(objectID=entityComponent.itemID, objectRow=fakeObjRow, entID=entityComponent.entID)



    def _RemovePlaceableWorldSpaceObject(self, entityComponent):
        ws = self.worldSpaceClient.GetWorldSpaceInstance(entityComponent.worldspaceID)
        ws.RemoveObject(entityComponent.itemID)



    def AddRoomEditGrid(self, respath, position = (0.0, 0.0, 0.0), rotationQuat = (0.0, 0.0, 0.0, 1.0)):
        if not self.roomEditGridGW:
            self.LogError('Tried to add a plane mesh grid to roomEdtitGridGW but the GameWorld was not loaded.', respath)
            return None
        mesh = GameWorld.CreateStaticMeshAndWait(self.roomEditGridGW, respath, position, rotationQuat)
        return mesh



    def ClearRoomEditGridGW(self):
        self.roomEditGridGW = GameWorld.GameWorld()
        self.roomEditGridGW.InitWorld('RoomEditGrid', const.GAMEWORLD_INIT_DATA, False, True)



    def GetRoomEditGridGW(self):
        return self.roomEditGridGW



    def GetRoomData(self, instanceID):
        if instanceID not in self.roomDataByInstance:
            self.LoadRoomData(instanceID)
        return self.roomDataByInstance[instanceID]



    def LoadRoomData(self, instanceID):
        self.roomDataByInstance[instanceID] = world.RoomData(instanceID)
        remoteData = sm.RemoteSvc('roomEditServer').GetRoomDataSerialized(instanceID)
        self.roomDataByInstance[instanceID].Deserialize(remoteData)



    def EnterEditMode(self):
        if self.inEditMode:
            if self.backupRoomData is not None and self.backupRoomData.instanceID != session.worldspaceid:
                return 
            return 
        self.inEditMode = True
        uthread.worker('roomEditClient::EnterEditMode', sm.RemoteSvc('roomEditServer').EnterEditMode)
        self.LoadRoomData(session.worldspaceid)
        self.backupRoomData = self.GetRoomData(session.worldspaceid).GetCopy()
        self.backupItemEntitieStates = {}
        entityScene = self.entityService.LoadEntitySceneAndBlock(session.worldspaceid)
        for itemID in self.backupRoomData.placeables:
            entity = self.entityService.FindEntityByID(itemID)
            if not entity:
                self.LogWarn('Entity for item with itemID: %s not found.' % itemID)
                continue
            self.backupItemEntitieStates[itemID] = self.entityService.GetEntityState(itemID)
            entityScene.UnregisterAndDestroyEntity(entity)
            placeable = self.backupRoomData.GetPlaceable(itemID)
            self._AddPlaceable(itemID, placeable.positionVector, placeable.rotation, placeable.typeID)




    def _ExitEditMode(self, revert = False):
        if not self.inEditMode:
            return 
        if not self.backupRoomData:
            self.LogError("Unable to revert changes because the backup doesn't exist!!")
            return 
        if self.backupRoomData.instanceID != session.worldspaceid:
            return 
        ws = self.worldSpaceClient.GetWorldSpaceInstance(session.worldspaceid)
        changes = self.backupRoomData.Diff(self.GetRoomData(session.worldspaceid))
        if revert:
            for (addedObjectID, addedGraphicID,) in changes.variantsAdded:
                targetObj = ws.GetObject(addedObjectID)
                if targetObj is None:
                    self.LogError('Unable to revert changes to object ID', addedObjectID)
                    continue
                self._SetWorldspaceObjectGraphicID(ws, targetObj, addedGraphicID)

            for (changedObjectID, changedGraphicID,) in changes.variantsMorphed:
                targetObj = ws.GetObject(changedObjectID)
                if targetObj is None:
                    self.LogError('Unable to revert changes to object ID', changedObjectID)
                    continue
                self._SetWorldspaceObjectGraphicID(ws, targetObj, changedGraphicID)

            for (removedObjectID, removedGraphicID,) in changes.variantsRemoved:
                targetObj = ws.GetObject(removedObjectID)
                if targetObj is None:
                    self.LogError('Unable to revert changes to object ID', removedObjectID)
                    continue
                defaultGraphicID = cfg.worldspaceObjects.Get(removedObjectID).graphicID
                self._SetWorldspaceObjectGraphicID(ws, targetObj, defaultGraphicID)

            entityScene = self.entityService.GetEntityScene(session.worldspaceid)
            for itemID in self.GetRoomData(session.worldspaceid).placeables:
                entity = self.entityService.FindEntityByID(itemID)
                if entity:
                    entityScene.UnregisterAndDestroyEntity(entity)

            for itemID in self.backupItemEntitieStates:
                self._AddEntityToScene(entityScene, itemID, self.backupItemEntitieStates[itemID])

            self.backupItemEntitieStates = {}
            self.roomDataByInstance[session.worldspaceid] = self.backupRoomData
            sm.RemoteSvc('roomEditServer').ExitEditMode()
        else:
            entityScene = self.entityService.GetEntityScene(session.worldspaceid)
            for item in changes.added + changes.moved:
                entity = self.entityService.FindEntityByID(item.itemID)
                if entity:
                    entityScene.UnregisterAndDestroyEntity(entity)
                if item.itemID in self.backupItemEntitieStates:
                    del self.backupItemEntitieStates[item.itemID]

            for itemID in self.backupItemEntitieStates:
                if itemID in changes.removed:
                    continue
                self._AddEntityToScene(entityScene, itemID, self.backupItemEntitieStates[itemID])

            self.backupItemEntitieStates = {}
            sm.RemoteSvc('roomEditServer').ExitEditMode(self.roomDataByInstance[session.worldspaceid].Serialize())
        self.backupRoomData = None
        self.inEditMode = False



    def _AddEntityToScene(self, entityScene, entID, entityState):
        entity = entities.Entity(entityScene, entID)
        for componentName in entityState:
            component = self.entityService.CreateComponent(componentName, entityState[componentName])
            if component:
                entity.AddComponent(componentName, component)

        entityScene.CreateAndRegisterEntity(entity)
        return entity



    def _SetWorldspaceObjectGraphicID(self, worldspace, targetObject, newGraphicID):
        objectName = targetObject.objectName
        pos = targetObject.pos
        rot = targetObject.rot
        scale = targetObject.scale
        cellName = targetObject.cellName
        systemName = targetObject.systemName
        worldspace.RemoveObject(targetObject.objectID)
        worldspace.AddObject(targetObject.objectID, objectName, newGraphicID, pos, rot, scale, cellName=cellName, systemName=systemName)



    def SubmitChanges(self):
        roomData = self.GetRoomData(session.worldspaceid)
        self._ExitEditMode()



    def RevertChanges(self):
        self._ExitEditMode(revert=True)



    def LoadRoomEditGrids(self):
        uthread.new(self._LoadRoomEditGridsTasklet).context = 'roomEditClient::LoadRoomEditGrids'



    def _LoadRoomEditGridsTasklet(self):
        roomEditGrids = {28: [('res:/../../common/res/Graphics/Interior/C_WarRoom/CWR_FloorBottom2.nxb', const.world.ROOM_EDIT_GRID_TYPE_FLOOR), ('res:/../../common/res/Graphics/Interior/C_WarRoom/CWR_FloorTop2.nxb', const.world.ROOM_EDIT_GRID_TYPE_WALL)],
         1: [('res:/../../common/res/Graphics/Interior/C_WarRoom/CWR_FloorBottom2.nxb', const.world.ROOM_EDIT_GRID_TYPE_FLOOR), ('res:/../../common/res/graphics/Interior/C_WarRoom/CWR_FloorTop2.nxb', const.world.ROOM_EDIT_GRID_TYPE_WALL)],
         553: [('res:/../../common/res/graphics/Interior/Incarna/WarRoom01/CWR_Assembled/CWR_FloorBottom2.nxb', const.world.ROOM_EDIT_GRID_TYPE_FLOOR), ('res:/../../common/res/graphics/Interior/Incarna/WarRoom01/CWR_Assembled/CWR_FloorTop2.nxb', const.world.ROOM_EDIT_GRID_TYPE_WALL)],
         50: [('res:/../../common/res/Graphics/Interior/Testscenes/Metrics/Modules/Floor/GFloor_01/ccpInteriorStatic1_A_grid_0.nxb', const.world.ROOM_EDIT_GRID_TYPE_FLOOR),
              ('res:/../../common/res/Graphics/Interior/Testscenes/Metrics/Modules/Floor/GFloor_02/ccpInteriorStatic1_A_grid_0.nxb', const.world.ROOM_EDIT_GRID_TYPE_FLOOR),
              ('res:/../../common/res/Graphics/Interior/Testscenes/Metrics/Modules/Floor/GFloor_03/ccpInteriorStatic1_A_grid_0.nxb', const.world.ROOM_EDIT_GRID_TYPE_FLOOR),
              ('res:/../../common/res/Graphics/Interior/Testscenes/Metrics/Modules/Floor/GFloor_04/ccpInteriorStatic1_A_grid_0.nxb', const.world.ROOM_EDIT_GRID_TYPE_FLOOR),
              ('res:/../../common/res/Graphics/Interior/Testscenes/Metrics/Table/Table_A_grid_0.nxb', const.world.ROOM_EDIT_GRID_TYPE_SURFACE)],
         377: [('res:/../../common/res/Graphics/Interior/Havens/ApartmentYearOne/LivingRoom.nxb', const.world.ROOM_EDIT_GRID_TYPE_FLOOR)]}
        self.ClearRoomEditGridGW()
        worldSpaceTypeID = self.worldSpaceClient.GetWorldSpaceTypeIDFromWorldSpaceID(session.worldspaceid)
        if worldSpaceTypeID in roomEditGrids:
            for (nxbFilePath, gridType,) in roomEditGrids[worldSpaceTypeID]:
                mesh = self.AddRoomEditGrid(nxbFilePath)
                self.gridTypes[mesh] = gridType

        else:
            return False
        self.RenderRoomEditGrid()
        return True



    def RenderRoomEditGrid(self):
        if not self.roomEditGridGW:
            self.LogError('No roomEdit grid loaded, cannot render')
            return 
        for job in trinity.device.scheduledRecurring:
            if job.name == 'gridLinesRenderJob':
                trinity.device.scheduledRecurring.remove(job)

        render_job = trinity.CreateRenderJob('gridLinesRenderJob')
        drawGridStep = trinity.TriStepRenderDebug()
        drawGridStep.autoClear = False
        render_job.steps.append(drawGridStep)
        render_job.ScheduleRecurring()
        gridLineColor = 1069168
        for shape in self.roomEditGridGW.staticShapes:
            for (fromPt, toPt, debugColor,) in shape.GetPhysXDebugLines():
                drawGridStep.DrawLine(toPt, gridLineColor, fromPt, gridLineColor)





    def StopRenderingGrid(self):
        for job in trinity.device.scheduledRecurring:
            if job.name == 'gridLinesRenderJob':
                trinity.device.scheduledRecurring.remove(job)




    def ToggleRenderingGrid(self):
        if self.showRoomEditGrids:
            self.StopRenderingGrid()
            self.showRoomEditGrids = False
            return 
        self.showRoomEditGrids = True
        self.RenderRoomEditGrid()



    def RefreshGrid(self):
        if self.showRoomEditGrids:
            self.RenderRoomEditGrid()



    def AddPlaceable(self, itemID, positionVector, rotation, typeID):
        self.EnterEditMode()
        roomData = self.GetRoomData(session.worldspaceid)
        roomData.PrimePlaceable(itemID, typeID, positionVector, rotation)
        self._AddPlaceable(itemID, positionVector, rotation, typeID)



    def _AddPlaceable(self, itemID, positionVector, rotation, typeID):
        componentState = {'roomEditPlaceable': {'itemID': itemID,
                               'typeID': typeID,
                               'pos': positionVector,
                               'rot': rotation,
                               'worldspaceID': session.worldspaceid}}
        entityScene = self.entityService.GetEntityScene(session.worldspaceid)
        entity = self._AddEntityToScene(entityScene, itemID, componentState)
        self.VerifyPlaceableLocation(entity)
        self.VerifyPlaceableGridAssociation(entity)
        invType = cfg.inventoryTypes.GetIfExists(typeID)
        if invType and invType.worldModelGraphicID:
            self.LoadPlaceableGridMesh(itemID, invType.worldModelGraphicID, positionVector, rotation)



    def LoadPlaceableGridMesh(self, itemID, graphicID, positionVector, rotation, refresh = True):
        testMapping = {10135: 'res:/../../common/res/Graphics/Placeable/TestAssets/TimL/CompuCube/CompCube.nxb',
         12412: 'res:/../../common/res/Graphics/Placeable/TestAssets/TimL/CompCube/CompCube.nxb'}
        if graphicID in testMapping:
            rotationQuat = geo2.QuaternionRotationSetYawPitchRoll(*rotation)
            mesh = self.AddRoomEditGrid(testMapping[graphicID], positionVector, rotationQuat)
            if not mesh:
                self.LogError('Could not load the customization grid mesh for itemID: ', itemID, ' GraphicID: ', graphicID)
                return 
            self.placeableGridMeshes[itemID] = mesh
            self.gridTypes[mesh] = const.world.ROOM_EDIT_GRID_TYPE_SURFACE
            if refresh:
                self.RefreshGrid()



    def UnLoadPlaceableGridMesh(self, itemID, refresh = True):
        if itemID in self.placeableGridMeshes:
            mesh = self.placeableGridMeshes[itemID]
            if mesh in self.gridOwnedPlaceables:
                del self.gridOwnedPlaceables[mesh]
            if mesh in self.gridTypes:
                del self.gridTypes[mesh]
            self.roomEditGridGW.RemoveStaticShape(mesh)
            del self.placeableGridMeshes[itemID]
            if refresh:
                self.RefreshGrid()



    def RemovePlaceable(self, itemID):
        self.EnterEditMode()
        roomData = self.GetRoomData(session.worldspaceid)
        roomData.RemovePlaceable(itemID)
        self.entityService.DestroyEntityByID(itemID)
        self.UnLoadPlaceableGridMesh(itemID)



    def MovePlaceable(self, itemID, translation, normal = None):
        self.EnterEditMode()
        entity = self.entityService.FindEntityByID(itemID)
        if not entity:
            self.LogError('Tried to move a placeable, but passed an invalid ID', itemID)
            return 
        component = entity.components.get('roomEditPlaceable', None)
        if not component:
            self.LogWarn('tried to move a object that is not a placeable object', itemID)
            return 
        ws = self.worldSpaceClient.GetWorldSpaceInstance(session.worldspaceid)
        object = ws.GetObject(itemID)
        if not object:
            self.LogError('Tried to update a world space object transform, but could not find object.', itemID)
            return 
        if normal:
            component.normal = normal
            normalQuat = geo2.QuaternionRotationArc(normal, (0.0, 1.0, 0.0))
            yawQuat = geo2.QuaternionRotationAxis(normal, component.localRotationY)
            newQuat = geo2.QuaternionMultiply(yawQuat, normalQuat)
            newRot = geo2.QuaternionRotationGetYawPitchRoll(newQuat)
            component.rotation = newRot
            object.rot = newRot
        component.translation = translation
        object.pos = translation
        object.Refresh()
        self.StoreGridHierarchy(component)
        self.UnLoadPlaceableGridMesh(itemID)
        self.VerifyPlaceableLocation(entity)
        self.VerifyPlaceableGridAssociation(entity)
        roomData = self.GetRoomData(session.worldspaceid)
        roomData.TransformPlaceable(itemID, component.translation, component.rotation)



    def RotatePlaceable(self, itemID, radians):
        self.EnterEditMode()
        entity = self.entityService.FindEntityByID(itemID)
        if not entity:
            self.LogError('Tried to rotate a placeable, but passed an invalid ID', itemID)
            return 
        component = entity.components.get('roomEditPlaceable', None)
        if not component:
            self.LogError('tried to rotate a entity that is not a placeable entity', itemID)
            return 
        ws = self.worldSpaceClient.GetWorldSpaceInstance(session.worldspaceid)
        object = ws.GetObject(itemID)
        if not object:
            self.LogError('Tried to update a world space object rotation, but could not find object.', itemID)
            return 
        component.localRotationY += radians
        normalQuat = geo2.QuaternionRotationArc(component.normal, (0.0, 1.0, 0.0))
        yawQuat = geo2.QuaternionRotationAxis(component.normal, component.localRotationY)
        newQuat = geo2.QuaternionMultiply(yawQuat, normalQuat)
        newRot = geo2.QuaternionRotationGetYawPitchRoll(newQuat)
        object.rot = newRot
        component.rotation = newRot
        object.Refresh()
        roomData = self.GetRoomData(session.worldspaceid)
        roomData.TransformPlaceable(itemID, component.translation, component.rotation)



    def FinalizePlaceablePosAndRot(self, itemID, targetGWStaticShape = None):
        entity = self.entityService.FindEntityByID(itemID)
        if not entity:
            self.LogError('Tried to finalize a placeable transform but passed an invalid ID', itemID)
            return 
        component = entity.components.get('roomEditPlaceable', None)
        if not component:
            self.LogWarn('tried to finalize a placeable transform but the entity is not a placeable entity', itemID)
            return 
        uthread.new(self._FinalizePlaceablePosAndRot, component).context = 'roomEditClient::FinalizePlaceablePosAndRot'
        if targetGWStaticShape in self.placeableGridMeshes.values():
            self.gridOwnedPlaceables[targetGWStaticShape].add(itemID)
        uthread.new(self._FinalizePlaceableGrid, component).context = 'roomEditClient::FinalizePlaceablePosAndRot'



    def _FinalizePlaceablePosAndRot(self, entityComponent):
        self._RemovePlaceableWorldSpaceObject(entityComponent)
        self._AddPlaceableWorldSpaceObject(entityComponent)



    def _FinalizePlaceableGrid(self, roomEditPlaceableComponent):
        self.LoadPlaceableGridMesh(roomEditPlaceableComponent.itemID, roomEditPlaceableComponent.graphicID, roomEditPlaceableComponent.translation, roomEditPlaceableComponent.rotation, refresh=False)
        self.RestoreGridHierarchy(roomEditPlaceableComponent)
        self.RefreshGrid()



    def StoreGridHierarchy(self, roomEditPlaceableComponent):
        if roomEditPlaceableComponent.itemID in self.placeableGridMeshes:
            gridStaticShape = self.placeableGridMeshes[roomEditPlaceableComponent.itemID]
            if gridStaticShape in self.gridOwnedPlaceables:
                self.storedGridOwnedPlaceables = self.gridOwnedPlaceables[gridStaticShape]
                del self.gridOwnedPlaceables[gridStaticShape]
            else:
                self.storedGridOwnedPlaceables = None



    def RestoreGridHierarchy(self, roomEditPlaceableComponent):
        if self.storedGridOwnedPlaceables:
            gridStaticShape = self.placeableGridMeshes[roomEditPlaceableComponent.itemID]
            self.gridOwnedPlaceables[gridStaticShape] = self.storedGridOwnedPlaceables



    def VerifyPlaceableLocation(self, entity):
        component = entity.components.get('roomEditPlaceable', None)
        if not component:
            self.LogError('tried to validate a entity position that is not a placeable entity', entity.entityID)
            return False
        pickResult = self._GetEntityComponentPick(component)
        if pickResult:
            (mesh, position, normal,) = pickResult
            distance = geo2.Vec3Distance(position, component.translation)
            component.validPosition = distance < self.ALLOWED_EPSILON_DEVIATION
        else:
            component.validPosition = False
        return component.validPosition



    def VerifyPlaceableGridAssociation(self, entity):
        component = entity.components.get('roomEditPlaceable', None)
        if not component:
            self.LogError('tried to validate a entity position that is not a placeable entity', entity.entityID)
            return False
        pickResult = self._GetEntityComponentPick(component)
        if not pickResult:
            component.validGridType = False
            return False
        (mesh, position, normal,) = pickResult
        if mesh not in self.gridTypes:
            self.LogError('Unable to identify grid type of a grid with entity attached to it.', entity.entityID)
            component.validGridType = False
            return False
        gridType = self.gridTypes[mesh]
        component.validGridType = gridType in component.gridTypeAssociation
        return component.validGridType



    def _GetEntityComponentPick(self, entityComponent):
        ws = self.worldSpaceClient.GetWorldSpaceInstance(session.worldspaceid)
        object = ws.GetObject(entityComponent.itemID)
        if not object:
            self.LogError('could not find a worldSpace object for placeable entity', entityComponent.itemID)
            return None
        renderObject = object.renderObject
        if not renderObject:
            while True:
                if ws.IsLoadingObject(object):
                    blue.synchro.Yield()
                    continue
                else:
                    renderObject = object.renderObject
                    if not renderObject:
                        self.LogError('could not get the renderObject of the placeable worldSpace object', object.objectID)
                        return None
                    break

        (min, max,) = renderObject.GetBoundingBoxInLocalSpace()
        height = max[1] - min[1]
        startOffset = geo2.Vec3Scale(entityComponent.normal, height)
        rayStart = geo2.Vec3Add(entityComponent.translation, startOffset)
        rayEnd = geo2.Vec3Subtract(entityComponent.translation, entityComponent.normal)
        return self.roomEditGridGW.LineTest(rayStart, rayEnd)



    def SetDetailMeshVariation(self, objectID, variantGraphicID):
        ws = self.worldSpaceClient.GetWorldSpaceInstance(session.worldspaceid)
        targetObj = ws.GetObject(objectID)
        if targetObj is None:
            self.LogError('Unable to locate object', objectID, 'in worldspace', session.worldspaceid)
            return 
        currentGraphicID = targetObj.GetGraphicID()
        if False:
            if currentGraphicID not in cfg.detailMeshesByTarget:
                if currentGraphicID not in cfg.detailMeshes:
                    raise RuntimeError('CONTENT ERROR - Current Graphic ID not found in zres.detailMeshes')
                currentGraphicID = cfg.detailMeshes[currentGraphicID]
            if variantGraphicID != currentGraphicID:
                if variantGraphicID not in cfg.detailMeshesByTarget[currentGraphicID]:
                    raise RuntimeError('Cannot fit specified detail mesh variant to target object')
        self.EnterEditMode()
        self._SetWorldspaceObjectGraphicID(ws, targetObj, variantGraphicID)
        roomData = self.GetRoomData(session.worldspaceid)
        roomData.PrimeDetailMeshVariant(objectID, variantGraphicID)




