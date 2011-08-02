import uicls
import uiconst
import uiutil
import cameras
import blue
import uthread
import log
import math
import GameWorld
import trinity
import geo2
import random

class RoomEditPrototypeUI(uicls.LayerCore):
    __guid__ = 'uicls.RoomEditPrototypeUI'
    __notifyevents__ = ['OnSessionChanged']
    SELECT_BOX_VALID_COLOR = 4279234575L
    SELECT_BOX_INVALID_COLOR = 4293922575L

    def OnOpenView(self):
        self.cameraClient = sm.GetService('cameraClient')
        self.roomEditClient = sm.GetService('roomEditClient')
        self.state = uiconst.UI_NORMAL
        self.storedMousePos = None
        self.leftDrag = False
        self.addingPlaceableSemaphore = uthread.Semaphore()
        self.pressedKeys = set([])
        self.updateKeysTasklet = uthread.new(self.UpdateKeyInput)
        self.updateKeysTasklet.context = 'roomEditPrototypeUI::OnOpenView'
        self.selectedObjectEntID = None
        self.camera = cameras.RoomEditCamera()
        self.camera.MoveCamera(0, 1.5, 0)
        sm.GetService('cameraClient').PushActiveCamera(self.camera)
        self.roomEditClient.LoadRoomEditGrids()
        playerEntity = sm.GetService('entityClient').GetPlayerEntity()
        playerEntity.movement.PushMoveMode(GameWorld.IdleMode())
        self.keydownCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYDOWN, self.KeyDown)
        self.keyupCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.KeyUp)
        sm.RegisterNotify(self)
        for job in trinity.device.scheduledRecurring:
            if job.name == 'selectionBoxRenderJob':
                trinity.device.scheduledRecurring.remove(job)

        render_job = trinity.CreateRenderJob('selectionBoxRenderJob')
        self.selectionBoxStep = trinity.TriStepRenderDebug()
        self.selectionBoxStep.autoClear = False
        render_job.steps.append(self.selectionBoxStep)
        render_job.ScheduleRecurring()
        self.selectionBoxTasklet = None
        self.SetupUI()



    def OnCloseView(self):
        self.updateKeysTasklet.kill()
        if self.selectionBoxTasklet:
            self.selectionBoxTasklet.kill()
        if self.selectionBoxStep is not None:
            self.selectionBoxStep.Clear()
            self.selectionBoxStep = None
        uicore.event.UnregisterForTriuiEvents(self.keydownCookie)
        uicore.event.UnregisterForTriuiEvents(self.keyupCookie)
        sm.UnregisterNotify(self)



    def OnSessionChanged(self, isRemote, sess, change):
        self.roomEditClient.StopRenderingGrid()



    def SetupUI(self):
        height = 150
        uicls.Button(parent=self, name='addPlaceableBtn', label='add Default Placeable', pos=(150,
         height,
         0,
         0), align=uiconst.RELATIVE, func=self.AddPlaceableButtonFunc)
        height += 20
        uicls.Button(parent=self, name='removePlaceableBtn', label='remove Selected Placeable', pos=(150,
         height,
         0,
         0), align=uiconst.RELATIVE, func=self.RemovePlaceableButtonFunc)
        height += 20
        uicls.Button(parent=self, name='toggleGridBtn', label='toggle grid view', pos=(150,
         height,
         0,
         0), align=uiconst.RELATIVE, func=self.ToggleGridButtonFunc)
        height += 20
        uicls.Button(parent=self, name='swapDetailMeshBtn', label=mls.Placeholder('Swap Detail Meshes'), pos=(150,
         height,
         0,
         0), align=uiconst.RELATIVE, func=self.SwapDetailMeshesFunc)
        height += 20
        uicls.Button(parent=self, name='submitBtn', label='apply changes (not implemented yet)', pos=(150,
         height,
         0,
         0), align=uiconst.RELATIVE, func=self.SubmitButtonFunc)
        height += 20
        uicls.Button(parent=self, name='revertBtn', label='Revert Changes (detail meshes only)', pos=(150,
         height,
         0,
         0), align=uiconst.RELATIVE, func=self.RevertButtonFunc)
        height += 20



    def OnMouseDown(self, button, *args):
        if button == uiconst.MOUSELEFT:
            pickResult = self.camera.PerformPick(uicore.uilib.x, uicore.uilib.y)
            if pickResult:
                (intersectionPoint, normal, entID,) = pickResult
                if entID != 0:
                    self.SelectObject(entID)
                    if not self.selectionBoxTasklet or not self.selectionBoxTasklet.alive:
                        self.selectionBoxTasklet = uthread.new(self._RenderSelectBoxTasklet)
                        self.selectionBoxTasklet.context = 'roomEditPrototypeUI::OnMouseDown'
                else:
                    self.SelectObject(None)
                return True
        if button == uiconst.MOUSERIGHT:
            self.cursor = uiconst.UICURSOR_NONE
            uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
            uicore.uilib.SetCapture(self)
            self.storedMousePos = (uicore.uilib.x, uicore.uilib.y)
            uicore.uilib.centerMouse = True
        return True



    def OnMouseUp(self, button, *args):
        if button == uiconst.MOUSELEFT:
            if self.selectedObjectEntID and self.leftDrag:
                self.leftDrag = False
                roomEditGridGW = self.roomEditClient.GetRoomEditGridGW()
                pickResult = self.camera.PickAgainstRoomEditGrids(uicore.uilib.x, uicore.uilib.y, roomEditGridGW)
                if pickResult:
                    (targetGWStaticShape, intersectionPoint, normal,) = pickResult
                else:
                    targetGWStaticShape = None
                self.roomEditClient.FinalizePlaceablePosAndRot(self.selectedObjectEntID, targetGWStaticShape)
        if button == uiconst.MOUSERIGHT:
            uicore.uilib.UnclipCursor()
            if uicore.uilib.GetCapture() == self:
                uicore.uilib.ReleaseCapture()
            uicore.uilib.centerMouse = False
            self.storedMousePos = None
            self.cursor = uiconst.UICURSOR_DEFAULT
        return True



    def OnMouseMove(self, *args):
        if uicore.uilib.leftbtn:
            self.leftDrag = True
            roomEditGridGW = self.roomEditClient.GetRoomEditGridGW()
            pickResult = self.camera.PickAgainstRoomEditGrids(uicore.uilib.x, uicore.uilib.y, roomEditGridGW)
            if pickResult and self.selectedObjectEntID:
                (grid, translation, normal,) = pickResult
                self.roomEditClient.MovePlaceable(self.selectedObjectEntID, translation, normal)
            elif self.selectedObjectEntID:
                pickResult = self.camera.PerformPick(uicore.uilib.x, uicore.uilib.y)
                if pickResult:
                    (translation, normal, entID,) = pickResult
                    camVec = geo2.Vec3Subtract(self.camera.GetPosition(), translation)
                    shortCamVec = geo2.Vec3Scale(camVec, 0.15)
                    newTranslation = geo2.Vec3Add(translation, shortCamVec)
                    self.roomEditClient.MovePlaceable(self.selectedObjectEntID, newTranslation)
        if uicore.uilib.rightbtn:
            lib = uicore.uilib
            dx = lib.dx
            dy = lib.dy
            mouseLookSpeed = 0.005
            self.camera.RotateCamera(-dx * mouseLookSpeed, -dy * mouseLookSpeed, 0)
        return True



    def OnMouseWheel(self, *etc):
        if self.selectedObjectEntID:
            radians = math.radians(uicore.uilib.dz / 12)
            self.roomEditClient.RotatePlaceable(self.selectedObjectEntID, radians)



    def KeyDown(self, wnd, eventID, (vkey, flag,)):
        if hasattr(uicore.registry.GetFocus(), 'OnChar'):
            self.pressedKeys.clear()
            return True
        if vkey == 87:
            self.pressedKeys.add('W')
        if vkey == 65:
            self.pressedKeys.add('A')
        if vkey == 83:
            self.pressedKeys.add('S')
        if vkey == 68:
            self.pressedKeys.add('D')
        if vkey == 32:
            self.pressedKeys.add(' ')
        if vkey == 88:
            self.pressedKeys.add('X')
        return True



    def KeyUp(self, wnd, eventID, (vkey, flag,)):
        if hasattr(uicore.registry.GetFocus(), 'OnChar'):
            self.pressedKeys.clear()
            return True
        if vkey == 87:
            self.pressedKeys.discard('W')
        if vkey == 65:
            self.pressedKeys.discard('A')
        if vkey == 83:
            self.pressedKeys.discard('S')
        if vkey == 68:
            self.pressedKeys.discard('D')
        if vkey == 32:
            self.pressedKeys.discard(' ')
        if vkey == 88:
            self.pressedKeys.discard('X')
        return True



    def UpdateKeyInput(self):
        cameraMoveRate = 0.1
        while True:
            if self.dead:
                return 
            dx = dy = dz = 0
            if 'W' in self.pressedKeys:
                dz += -cameraMoveRate
            if 'A' in self.pressedKeys:
                dx += -cameraMoveRate
            if 'S' in self.pressedKeys:
                dz += cameraMoveRate
            if 'D' in self.pressedKeys:
                dx += cameraMoveRate
            if ' ' in self.pressedKeys:
                dy += cameraMoveRate
            if 'X' in self.pressedKeys:
                dy -= cameraMoveRate
            self.camera.MoveCamera(dx, dy, dz)
            blue.synchro.Yield()




    def AddPlaceableButtonFunc(self, *args):
        try:
            self.addingPlaceableSemaphore.acquire()
            hackObjectID = self.roomEditClient.GetNextFakeItemID()
            self.roomEditClient.AddPlaceable(itemID=hackObjectID, positionVector=(0.0, 0.0, 0.0), rotationVector=(0.0, 0.0, 0.0), typeID=3621)

        finally:
            self.addingPlaceableSemaphore.release()

        self.roomEditClient.RefreshGrid()



    def RemovePlaceableButtonFunc(self, *args):
        if self.selectedObjectEntID:
            self.roomEditClient.RemovePlaceable(self.selectedObjectEntID)
            self.roomEditClient.RefreshGrid()
            self.SelectObject(None)



    def SwapDetailMeshesFunc(self, *args):
        ws = sm.GetService('worldSpaceClient').GetWorldSpaceInstance(session.worldspaceid)
        for obj in ws.GetObjects():
            gID = self.SelectDetailMeshSwap(obj.GetGraphicID())
            if gID is None:
                continue
            self.roomEditClient.SetDetailMeshVariation(obj.objectID, gID)




    def ExitEditMode(self):
        sm.GetService('cameraClient').PopActiveCamera()
        self.roomEditClient.StopRenderingGrid()
        self.selectionBoxStep.Clear()
        sm.GetService('gameui').OpenExclusive('charcontrol', 1)
        playerEntity = sm.GetService('entityClient').GetPlayerEntity()
        if playerEntity is not None and playerEntity.movement is not None:
            playerEntity.movement.PushMoveMode(GameWorld.KBMouseMode(0.0))



    def SubmitButtonFunc(self, *args):
        self.roomEditClient.SubmitChanges()
        self.ExitEditMode()



    def RevertButtonFunc(self, *args):
        self.roomEditClient.RevertChanges()
        self.ExitEditMode()



    def ToggleGridButtonFunc(self, *args):
        self.roomEditClient.ToggleRenderingGrid()



    def SelectObject(self, entID):
        self.selectedObjectEntID = entID



    def _RenderSelectBoxTasklet(self):
        entityClient = sm.GetService('entityClient')
        worldSpaceInstance = sm.GetService('worldSpaceClient').GetWorldSpaceInstance(session.worldspaceid)
        while True:
            blue.synchro.Yield()
            if self.dead:
                return 
            self.selectionBoxStep.Clear()
            if not self.selectedObjectEntID:
                return 
            entity = entityClient.FindEntityByID(self.selectedObjectEntID)
            if not entity:
                return 
            component = entity.components.get('roomEditPlaceable', None)
            if not component:
                return 
            if component.GetValidationState():
                color = self.SELECT_BOX_VALID_COLOR
            else:
                color = self.SELECT_BOX_INVALID_COLOR
            object = worldSpaceInstance.GetObject(self.selectedObjectEntID)
            if not object:
                return 
            (minPoint, maxPoint,) = object.renderObject.GetBoundingBoxInWorldSpace()
            minPoint = geo2.Vec3Add(minPoint, (-0.1, 0, -0.1))
            maxPoint = geo2.Vec3Add(maxPoint, (0.1, 0.1, 0.1))
            self.selectionBoxStep.DrawBox(minPoint, maxPoint, color)




    def SelectDetailMeshSwap(self, graphicID):
        choices = self.FindDetailMeshVariants(graphicID)
        if len(choices) < 1:
            return None
        return random.choice(choices)



    def FindDetailMeshVariants(self, graphicID):
        validVariants = []
        if graphicID not in cfg.detailMeshes and graphicID not in cfg.detailMeshesByTarget:
            return validVariants
        if graphicID in cfg.detailMeshes:
            targetGraphicID = cfg.detailMeshes.Get(graphicID).targetGraphicID
            validVariants.extend([ variation.detailGraphicID for variation in cfg.detailMeshesByTarget.get(targetGraphicID) ])
            validVariants.remove(graphicID)
        else:
            validVariants = [ variation.detailGraphicID for variation in cfg.detailMeshesByTarget.get(graphicID) ]
        return validVariants




