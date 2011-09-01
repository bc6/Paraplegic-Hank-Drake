import sys
import log
import svc
import util
import blue
import audio2
import trinity
import cameras
import service
import uthread
MAX_MOUSE_DELTA = 500
MOUSE_LOOK_SPEED = 0.005
MOUSE_MOVE_DELTA_FALLOFF = 0.5
MAX_MOUSE_SCREEN_FRACTION_JUMP = 1.85
MOUSE_MOVE_DELTA_HISTORY_BUFFER_LENGTH = 10

class EveCameraClient(svc.cameraClient):
    __guid__ = 'svc.eveCameraClient'
    __replaceservice__ = 'cameraClient'
    __exportedcalls__ = {'GetCameraSettings': [],
     'CheckCameraOffsets': [],
     'CheckMouseLookSpeed': []}
    __dependencies__ = svc.cameraClient.__dependencies__[:]
    __dependencies__.extend(['mouseInput', 'sceneManager'])
    __startupdependencies__ = svc.cameraClient.__startupdependencies__[:]
    __startupdependencies__.extend(['settings'])
    __notifyevents__ = svc.cameraClient.__notifyevents__[:]
    __notifyevents__.extend(['OnEntityCreated', 'OnEntityDeleted'])

    def Run(self, *etc):
        svc.cameraClient.Run(self, *etc)
        self.cameraStack = [cameras.AvatarCamera()]
        self.sharedCameras = {'Default Startup Camera': self.cameraStack[0]}
        self.entityLoop = None
        self.invertYAxis = False
        self.mouseSmooth = True
        self.mouseLookSpeed = cameras.MOUSE_LOOK_SPEED
        self.desiredDeltaX = 0
        self.desiredDeltaY = 0
        self.lastDeltaX = 0
        self.lastDeltaY = 0
        self.currAverageDeltaX = 0
        self.currAverageDeltaY = 0
        self.ignoreNextMouseUpdate = False
        self.mouseDeltaHistory = []
        self.mouseInput.RegisterCallback(const.INPUT_TYPE_MOUSEDOWN, self.OnMouseDown)
        self.mouseInput.RegisterCallback(const.INPUT_TYPE_MOUSEUP, self.OnMouseUp)
        self.mouseInput.RegisterCallback(const.INPUT_TYPE_MOUSEMOVE, self.OnMouseMove)
        self.mouseInput.RegisterCallback(const.INPUT_TYPE_MOUSEWHEEL, self.OnMouseWheel)



    def Stop(self, stream):
        self.mouseInput.UnRegisterCallback(const.INPUT_TYPE_MOUSEDOWN, self.OnMouseDown)
        self.mouseInput.UnRegisterCallback(const.INPUT_TYPE_MOUSEUP, self.OnMouseUp)
        self.mouseInput.UnRegisterCallback(const.INPUT_TYPE_MOUSEMOVE, self.OnMouseMove)
        self.mouseInput.UnRegisterCallback(const.INPUT_TYPE_MOUSEWHEEL, self.OnMouseWheel)



    def OnMouseDown(self, button, posX, posY, entityID):
        activeCamera = self.GetActiveCamera()
        activeCamera.OnMouseDown(posX, posY, button)



    def OnMouseUp(self, button, posX, posY, entityID):
        activeCamera = self.GetActiveCamera()
        activeCamera.OnMouseUp(posX, posY, button)



    def OnMouseMove(self, deltaX, deltaY, entityID):
        if self.ignoreNextMouseUpdate:
            self.desiredDeltaX = self.lastDeltaX * self.mouseLookSpeed
            self.desiredDeltaY = self.lastDeltaY * self.mouseLookSpeed
            self.ignoreNextMouseUpdate = False
            return 
        overflow = False
        if abs(deltaX) > trinity.app.width / cameras.MAX_MOUSE_SCREEN_FRACTION_JUMP:
            if deltaX < 0 and self.lastDeltaX > 0 or deltaX > 0 and self.lastDeltaX < 0:
                self.desiredDeltaX = self.lastDeltaX * self.mouseLookSpeed
                overflow = True
        if abs(deltaY) > trinity.app.height / cameras.MAX_MOUSE_SCREEN_FRACTION_JUMP:
            if deltaY < 0 and self.lastDeltaY > 0 or deltaY > 0 and self.lastDeltaY < 0:
                self.desiredDeltaY = self.lastDeltaY * self.mouseLookSpeed
                overflow = True
        if overflow:
            return 
        if self.invertYAxis:
            deltaY = -deltaY
        self.lastDeltaX = deltaX
        self.lastDeltaY = deltaY
        self.desiredDeltaX = deltaX * self.mouseLookSpeed
        self.desiredDeltaY = deltaY * self.mouseLookSpeed
        activeCamera = self.GetActiveCamera()
        activeCamera.OnMouseMove(deltaX, deltaY)



    def OnMouseWheel(self, delta):
        activeCamera = self.GetActiveCamera()
        if hasattr(activeCamera, 'AdjustZoom'):
            activeCamera.AdjustZoom(delta * cameras.MOUSE_LOOK_SPEED)



    def GetCameraSettings(self):
        offset = settings.user.ui.Get('incarnaCameraOffset', 1.0)
        invertY = settings.user.ui.Get('incarnaCameraInvertY', 0)
        mouseLookSpeed = settings.user.ui.Get('incarnaCameraMouseLookSpeed', cameras.MOUSE_LOOK_SPEED)
        mouseSmooth = settings.user.ui.Get('incarnaCameraMouseSmooth', 1)
        mySettings = util.KeyVal(charOffsetSetting=offset, invertY=invertY, mouseLookSpeed=mouseLookSpeed, mouseSmooth=mouseSmooth)
        return mySettings



    def ApplyUserSettings(self):
        self.CheckCameraOffsets()
        self.CheckInvertY()
        self.CheckMouseLookSpeed()
        self.CheckMouseSmooth()



    def CheckCameraOffsets(self):
        offset = settings.user.ui.Get('incarnaCameraOffset', 1.0)
        offsetBehaviors = []
        for cam in self.cameraStack:
            offsetBehavior = cam.GetBehavior(cameras.CharacterOffsetBehaviour)
            if offsetBehavior:
                offsetBehaviors.append(offsetBehavior)

        for offsetBehavior in offsetBehaviors:
            offsetBehavior.AdjustOffset(offset)




    def CheckInvertY(self):
        self.invertYAxis = settings.user.ui.Get('incarnaCameraInvertY', 0)



    def CheckMouseLookSpeed(self):
        self.mouseLookSpeed = settings.user.ui.Get('incarnaCameraMouseLookSpeed', cameras.MOUSE_LOOK_SPEED)



    def CheckMouseSmooth(self):
        self.mouseSmooth = settings.user.ui.Get('incarnaCameraMouseSmooth', 1)



    def OnEntityCreated(self, entityID):
        if entityID == session.charid:
            self.OnAvatarEnterWorldspace(entityID)
            self.StartCamera()
            self.ApplyUserSettings()



    def Disable(self):
        svc.cameraClient.Disable(self)
        self.StopCamera()



    def Enable(self):
        svc.cameraClient.Enable(self)
        self.StartCamera()



    def OnEntityDeleted(self, entityID, sceneID):
        if entityID == session.charid:
            self.StopCamera()
            self.GetActiveCamera().Reset()
            self.audioListener = None



    def OnEntitySceneUnloaded(self, sceneID):
        for camera in self.cameraStack:
            for (id, behaviour,) in camera.cameraBehaviors:
                if hasattr(behaviour, 'gameWorld'):
                    if behaviour.gameWorld and behaviour.gameWorld.instanceID == sceneID:
                        behaviour.gameWorld = None


        self.ClearCameraStack()



    def ClearCameraStack(self):
        self.cameraStack = [cameras.AvatarCamera()]
        self.sharedCameras = {'Default Startup Camera': self.cameraStack[0]}



    def StartCamera(self):
        self.entityLoop = uthread.new(self.CameraLoop)
        self.entityLoop.context = 'CameraClient::CameraLoop'



    def StopCamera(self):
        if self.entityLoop is not None and self.entityLoop.alive:
            self.entityLoop.kill()



    def OnAvatarEnterWorldspace(self, playerEntID):
        self.ResetCameras()
        self.SetAudioListener(audio2.GetListener(0))
        defaultCamera = cameras.AvatarCamera()
        if self.audioListener is not None:
            defaultCamera.audio2Listener = self.audioListener
        self.cameraStack = [defaultCamera]
        self._CreateCameraRenderJob()
        defaultCamera.Update()
        self.sharedCameras = {'Default Incarna Avatar Camera': defaultCamera}
        defaultCamera.AddBehavior(cameras.CharacterOffsetBehaviour(playerEntID), priority=1)
        defaultCamera.AddBehavior(cameras.ZoomFovBehavior(), priority=2)



    def _CreateCameraRenderJob(self):
        self.sceneManager.RefreshJob(self.GetActiveCamera())



    def ApplyMouseDeltaMoveSmoothing(self, activeCamera):
        self.mouseDeltaHistory.insert(0, (self.desiredDeltaX, self.desiredDeltaY))
        if len(self.mouseDeltaHistory) > cameras.MOUSE_MOVE_DELTA_HISTORY_BUFFER_LENGTH:
            self.mouseDeltaHistory.pop()
        self.desiredDeltaX = 0
        self.desiredDeltaY = 0
        averageWeight = 1.0
        averageDecrease = cameras.MOUSE_MOVE_DELTA_FALLOFF
        deltaX = 0
        deltaY = 0
        divideBy = 0
        for entry in self.mouseDeltaHistory:
            deltaX += entry[0] * averageWeight
            deltaY += entry[1] * averageWeight
            divideBy += averageWeight
            averageWeight *= averageDecrease

        deltaX = deltaX / divideBy
        deltaY = deltaY / divideBy
        self.currAverageDeltaX = deltaX / self.mouseLookSpeed
        self.currAverageDeltaY = deltaY / self.mouseLookSpeed
        activeCamera.SetDesiredMouseDelta(deltaX, deltaY)



    def CameraLoop(self):
        while self.state != service.SERVICE_STOPPED:
            if self.enabled:
                self.TickCamera()
            blue.pyos.synchro.Sleep(5)




    def TickCamera(self):
        try:
            activeCam = self.GetActiveCamera()
            if self.mouseSmooth:
                self.ApplyMouseDeltaMoveSmoothing(activeCam)
            else:
                activeCam.SetDesiredMouseDelta(self.desiredDeltaX, self.desiredDeltaY)
                self.desiredDeltaX = 0
                self.desiredDeltaY = 0
            activeCam.UpdateProjectionMatrix()
            activeCam.Update()
        except Exception:
            log.LogException('Error in CameraLoop')
            sys.exc_clear()



exports = util.AutoExports('cameras', locals())

