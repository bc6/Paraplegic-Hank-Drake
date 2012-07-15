#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/camera/incarnaCamera.py
import sys
import log
import util
import blue
import geo2
import uthread
import uiconst
import trinity
import cameras
import mathUtil
MAX_SPIN_SPEED = 15
MAX_MOUSE_DELTA = 0.2
SPIN_RESISTANCE = 0.992
SPIN_DELTA_MODIFIER = 60
ZOOM_SPEED_MODIFIER = 4.0
SPIN_FALLOFF_RATIO = 700.0
DISPLAY_MOUSE_AGAIN_DELAY = 85
CAMERA_SPIN_RELEASE_MOUSE_CUTOFF_SECONDS = 0.1
INCARNA_MAX_ZOOM = 2.9

class IncarnaCamera(cameras.PolarCamera):
    __guid__ = 'cameras.IncarnaCamera'

    def __init__(self):
        cameras.PolarCamera.__init__(self)
        self.frontClip = 0.15
        self.cameraClient = None
        self.fieldOfView = 0.7
        self.zoom = cameras.INCARNA_MAX_ZOOM
        self.properZoom = cameras.INCARNA_MAX_ZOOM
        self.desiredZoom = self.zoom
        self.collisionZoom = self.zoom
        self.collisionCorrectionPerFrame = 0
        self.minPitch = 0.885
        self.maxPitch = 2.5
        self.mouseYawDelta = 0
        self.mousePitchDelta = 0
        self.yawSpeed = 0
        self.pitchSpeed = 0
        self.secondsSinceLastMouseMoveDelta = 0
        self.lastMouseMoveDelta = (0, 0)
        self.preClickCursorPos = (0, 0)
        self.navigationLayer = None
        self.originalMouseButtonPressed = None
        self.waitForLayerCapture = False
        self.updateMouse = False
        self.defaultCursor = uiconst.UICURSOR_CROSS
        self.lastUpdateTime = blue.os.GetWallclockTime()

    def AdjustZoom(self, argument):
        pass

    def OnMouseDown(self, posX, posY, button):
        if button != const.INPUT_TYPE_LEFTCLICK and button != const.INPUT_TYPE_RIGHTCLICK:
            return
        if not self.mouseLeftButtonDown and not self.mouseRightButtonDown:
            if button == const.INPUT_TYPE_LEFTCLICK and uicore.uilib.GetMouseButtonState(uiconst.MOUSERIGHT):
                return
            if button == const.INPUT_TYPE_RIGHTCLICK and uicore.uilib.GetMouseButtonState(uiconst.MOUSELEFT):
                return
            self.waitForLayerCapture = True
            self.preClickCursorPos = (posX, posY)
            self.originalMouseButtonPressed = button
        cameras.PolarCamera.OnMouseDown(self, posX, posY, button)

    def Deactivate(self):
        self.ResetMouseCapture()

    def DisplayCursorAgain(self):
        blue.pyos.synchro.SleepWallclock(cameras.DISPLAY_MOUSE_AGAIN_DELAY)
        if self.navigationLayer:
            self.SetCursorType(self.defaultCursor)

    def ReleaseMouse(self):
        self.updateMouse = False
        self.originalMouseButtonPressed = None
        self.waitForLayerCapture = False
        self.SetCursorPos(*self.preClickCursorPos)
        uicore.uilib.UnclipCursor()
        uicore.uilib.ReleaseCapture()

    def SetCursorPos(self, x, y):
        try:
            uicore.uilib.SetCursorPos(x, y)
        except RuntimeError:
            sys.exc_clear()

    def SetCursorType(self, cursorType):
        try:
            uicore.uilib.SetCursor(cursorType)
        except RuntimeError:
            sys.exc_clear()

    def OnMouseUp(self, posX, posY, button):
        if button != const.INPUT_TYPE_LEFTCLICK and button != const.INPUT_TYPE_RIGHTCLICK:
            return
        if button == const.INPUT_TYPE_LEFTCLICK:
            self.mouseLeftButtonDown = False
        if button == const.INPUT_TYPE_RIGHTCLICK:
            self.mouseRightButtonDown = False
        if self.originalMouseButtonPressed is const.INPUT_TYPE_RIGHTCLICK and button is const.INPUT_TYPE_LEFTCLICK:
            uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
        if button == self.originalMouseButtonPressed:
            if button == self.originalMouseButtonPressed and button == const.INPUT_TYPE_RIGHTCLICK and self.mouseLeftButtonDown:
                self.originalMouseButtonPressed = const.INPUT_TYPE_LEFTCLICK
                uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
                return
            if button == self.originalMouseButtonPressed and button == const.INPUT_TYPE_LEFTCLICK and self.mouseRightButtonDown:
                self.originalMouseButtonPressed = const.INPUT_TYPE_RIGHTCLICK
                uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
                return
            self.ReleaseMouse()
            uthread.new(self.DisplayCursorAgain)
            if self.lastMouseMoveDelta[0] > 0:
                self.yawSpeed = min(cameras.MAX_SPIN_SPEED, self.lastMouseMoveDelta[0] * cameras.SPIN_DELTA_MODIFIER)
            else:
                self.yawSpeed = max(-cameras.MAX_SPIN_SPEED, self.lastMouseMoveDelta[0] * cameras.SPIN_DELTA_MODIFIER)
            if self.lastMouseMoveDelta[1] > 0:
                self.pitchSpeed = min(cameras.MAX_SPIN_SPEED, self.lastMouseMoveDelta[1] * cameras.SPIN_DELTA_MODIFIER)
            else:
                self.pitchSpeed = max(-cameras.MAX_SPIN_SPEED, self.lastMouseMoveDelta[1] * cameras.SPIN_DELTA_MODIFIER)

    def OnMouseMove(self, deltaX, deltaY):
        if self.waitForLayerCapture and (self.mouseLeftButtonDown or self.mouseRightButtonDown):
            self.SetCursorType(uiconst.UICURSOR_NONE)
            uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
            if self.navigationLayer is not None:
                uicore.uilib.SetCapture(self.navigationLayer, retainFocus=True)
                uicore.registry.SetFocus(self.navigationLayer)
            self.waitForLayerCapture = False
        if self.mouseLeftButtonDown or self.mouseRightButtonDown:
            self.updateMouse = True
            self.secondsSinceLastMouseMoveDelta = 0
        else:
            self.updateMouse = False

    def AdjustYaw(self, delta, maxRotate = None, ignoreUpdate = True):
        if delta < 0:
            delta = max(delta, -cameras.MAX_MOUSE_DELTA)
        else:
            delta = min(delta, cameras.MAX_MOUSE_DELTA)
        self.mouseYawDelta = delta
        if maxRotate:
            if delta > maxRotate:
                delta = maxRotate
            if delta < -maxRotate:
                delta = -maxRotate
        self.SetYaw(self.yaw + delta, ignoreUpdate=ignoreUpdate)

    def AdjustPitch(self, delta):
        if delta < 0:
            delta = max(delta, -cameras.MAX_MOUSE_DELTA)
        else:
            delta = min(delta, cameras.MAX_MOUSE_DELTA)
        self.mousePitchDelta = delta
        self.SetPitch(self.pitch + delta)

    def ClipLowSpinSpeed(self, value):
        if abs(value) < const.FLOAT_TOLERANCE:
            return 0.0
        return value

    def SetCollisionZoom(self, zoom, amountPerFrame):
        self.collisionZoom = zoom
        self.collisionCorrectionPerFrame = amountPerFrame

    def ClipMouseAround(self):
        margin = 10
        marginPlus = 13
        currCursorPos = (uicore.uilib.x, uicore.uilib.y)
        screenWidth = uicore.ReverseScaleDpi(trinity.app.width)
        screenHeight = uicore.ReverseScaleDpi(trinity.app.height)
        if currCursorPos[0] < margin:
            newXPos = screenWidth - marginPlus
            self.cameraClient.skipMouseFrameCount = 1
            self.SetCursorPos(newXPos, currCursorPos[1])
            currCursorPos = (newXPos, currCursorPos[1])
        if currCursorPos[1] < margin:
            newYPos = screenHeight - marginPlus
            self.cameraClient.skipMouseFrameCount = 1
            self.SetCursorPos(currCursorPos[0], newYPos)
            currCursorPos = (currCursorPos[0], newYPos)
        if currCursorPos[0] >= screenWidth - margin:
            self.cameraClient.skipMouseFrameCount = 1
            self.SetCursorPos(marginPlus, currCursorPos[1])
            currCursorPos = (marginPlus, currCursorPos[1])
        if currCursorPos[1] >= screenHeight - margin:
            self.cameraClient.skipMouseFrameCount = 1
            self.SetCursorPos(currCursorPos[0], marginPlus)
            currCursorPos = (currCursorPos[0], marginPlus)

    def HandleYawAndPitch(self):
        if not self.mouseLeftButtonDown and not self.mouseRightButtonDown:
            if self.yawSpeed != 0:
                self.SetYaw(self.yaw + self.yawSpeed * self.frameTime)
                self.yawSpeed = self.yawSpeed * pow(cameras.SPIN_RESISTANCE, self.frameTime * cameras.SPIN_FALLOFF_RATIO)
                self.yawSpeed = self.ClipLowSpinSpeed(self.yawSpeed)
            if self.pitchSpeed != 0:
                self.SetPitch(self.pitch + self.pitchSpeed * self.frameTime)
                self.pitchSpeed = self.pitchSpeed * pow(cameras.SPIN_RESISTANCE, self.frameTime * cameras.SPIN_FALLOFF_RATIO)
                self.pitchSpeed = self.ClipLowSpinSpeed(self.pitchSpeed)

    def HandleMouseMove(self):
        if self.updateMouse:
            self.AdjustYaw(self.desiredDeltaX)
            self.AdjustPitch(self.desiredDeltaY)
            self.lastMouseMoveDelta = (self.desiredDeltaX, self.desiredDeltaY)
            self.ClipMouseAround()

    def HandleMouseMoveDelta(self):
        if self.lastMouseMoveDelta != (0, 0):
            self.secondsSinceLastMouseMoveDelta += self.frameTime
            if self.secondsSinceLastMouseMoveDelta > cameras.CAMERA_SPIN_RELEASE_MOUSE_CUTOFF_SECONDS:
                self.lastMouseMoveDelta = (0, 0)

    def HandleAudioListener(self):
        if self.audio2Listener:
            faceFwd = geo2.Vec3Subtract(self.cameraPosition, self.poi)
            faceFwd = geo2.Vec3Normalize(faceFwd)
            self.audio2Listener.SetPosition(faceFwd, (0, 1, 0), self.cameraPosition)

    def ResetMouseMoveDelta(self):
        self.mouseYawDelta = 0
        self.mousePitchDelta = 0

    def HandleZooming(self):
        self.zoom = mathUtil.Lerp(self.zoom, self.desiredZoom, self.frameTime * cameras.ZOOM_SPEED_MODIFIER)
        self.collisionZoom = self.zoom

    def Init(self):
        if self.navigationLayer is None and sm.GetService('viewState').IsViewActive('station'):
            self.navigationLayer = sm.GetService('viewState').GetView('station').layer
            if self.navigationLayer is None:
                log.LogError('Could not retrieve the character control layer using uix.GetWorldspaceNav(create=0)')
            else:
                self.defaultCursor = self.navigationLayer.cursor
        if self.cameraClient is None:
            self.cameraClient = sm.GetService('cameraClient')

    def Reset(self):
        self.audio2Listener = None
        self.navigationLayer = None
        self.ResetBehaviors()

    def ResetLayer(self):
        self.navigationLayer = None
        self.ResetMouseCapture()

    def ResetMouseCapture(self):
        if self.mouseLeftButtonDown or self.mouseRightButtonDown:
            self.ReleaseMouse()
            self.SetCursorType(self.defaultCursor)
            self.mouseLeftButtonDown = self.mouseRightButtonDown = False

    def Update(self):
        self.Init()
        now = blue.os.GetWallclockTime()
        self.frameTime = float(now - self.lastUpdateTime) / const.SEC
        if self.frameTime < const.FLOAT_TOLERANCE:
            return
        self.lastUpdateTime = now
        self.HandleYawAndPitch()
        self.HandleZooming()
        self.HandleMouseMove()
        for priority, behavior in self.cameraBehaviors:
            behavior.ProcessCameraUpdate(self, now, self.frameTime)

        self.ResetMouseMoveDelta()
        self.AssembleViewMatrix(self.poi, self.yaw, self.pitch, self.zoom)
        self.HandleMouseMoveDelta()
        self.HandleAudioListener()


exports = util.AutoExports('cameras', locals())