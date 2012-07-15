#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/camera/cameraDebugClient.py
import service
import uiconst
import cameras
import trinity
CAMERA_MOVE_SPEED = 4.0
X_AXIS = 0
Z_AXIS = 2

class CameraDebugClient(service.Service):
    __guid__ = 'svc.cameraDebugClient'
    __dependencies__ = ['debugSelectionClient', 'debugRenderClient', 'cameraClient']

    def __init__(self, *args):
        service.Service.__init__(self, *args)

    def Run(self, *args):
        service.Service.Run(self, *args)
        self.RegisterKeyEvents()

    def RegisterKeyEvents(self):
        self.keyDownCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYDOWN, self.OnGlobalKeyDownCallback)
        self.keyUpCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.OnGlobalKeyUpCallback)
        self.mouseEnterCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self.OnGlobalMouseMoveCallback)

    def UnRegisterKeyEvents(self):
        if self.keyDownCookie:
            uicore.event.UnregisterForTriuiEvents(self.keyDownCookie)
            self.keyDownCookie = None
        if self.keyUpCookie:
            uicore.event.UnregisterForTriuiEvents(self.keyUpCookie)
            self.keyUpCookie = None
        if self.mouseEnterCookie:
            uicore.event.UnregisterForTriuiEvents(self.mouseEnterCookie)
            self.mouseEnterCookie = None

    def OnGlobalKeyDownCallback(self, wnd, eventID, (vkey, flag)):
        activeCamera = self.cameraClient.GetActiveCamera()
        if type(activeCamera) is cameras.DebugCamera and activeCamera.IsUpdatingDebugCamera():
            vec = activeCamera.GetTranslationVector()
            if vkey == uicore.cmd.GetShortcutByFuncName('CmdMoveForward')[0]:
                vec[Z_AXIS] = -CAMERA_MOVE_SPEED
            if vkey == uicore.cmd.GetShortcutByFuncName('CmdMoveRotateRight')[0]:
                vec[X_AXIS] = CAMERA_MOVE_SPEED
            if vkey == uicore.cmd.GetShortcutByFuncName('CmdMoveBackward')[0]:
                vec[Z_AXIS] = CAMERA_MOVE_SPEED
            if vkey == uicore.cmd.GetShortcutByFuncName('CmdMoveRotateLeft')[0]:
                vec[X_AXIS] = -CAMERA_MOVE_SPEED
            activeCamera.SetTranslationVector(vec)
        return True

    def OnGlobalKeyUpCallback(self, wnd, eventID, (vkey, flag)):
        activeCamera = self.cameraClient.GetActiveCamera()
        if type(activeCamera) is cameras.DebugCamera:
            vec = activeCamera.GetTranslationVector()
            if vkey in (uicore.cmd.GetShortcutByFuncName('CmdMoveForward')[0], uicore.cmd.GetShortcutByFuncName('CmdMoveBackward')[0]):
                vec[Z_AXIS] = 0.0
            if vkey in (uicore.cmd.GetShortcutByFuncName('CmdMoveRotateRight')[0], uicore.cmd.GetShortcutByFuncName('CmdMoveRotateLeft')[0]):
                vec[X_AXIS] = 0.0
            activeCamera.SetTranslationVector(vec)
        return True

    def OnGlobalMouseMoveCallback(self, *args):
        activeCamera = self.cameraClient.GetActiveCamera()
        if type(activeCamera) is cameras.DebugCamera and (uicore.uilib.leftbtn or uicore.uilib.rightbtn):
            if trinity.IsRightHanded():
                dx = uicore.uilib.dx
                dy = uicore.uilib.dy
            else:
                dx = -uicore.uilib.dx
                dy = -uicore.uilib.dy
            activeCamera.AdjustDebugCamYaw(dx * self._GetMouseTurnSpeed())
            activeCamera.AdjustDebugCamPitch(dy * self._GetMouseTurnSpeed())
        return True

    def _GetMouseTurnSpeed(self):
        return 0.003

    def ToggleDebugCameraUpdate(self):
        activeCamera = self.cameraClient.GetActiveCamera()
        if type(activeCamera) is cameras.DebugCamera:
            activeCamera.ToggleDebugCameraUpdate()
            if activeCamera.IsUpdatingDebugCamera():
                sm.GetService('navigation').hasControl = False
            else:
                sm.GetService('navigation').hasControl = True