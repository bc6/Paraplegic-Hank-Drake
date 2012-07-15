#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/camera/cameraClient.py
import util
import uthread
import trinity
import service
import cameras

class CameraClient(service.Service):
    __guid__ = 'svc.cameraClient'
    __notifyevents__ = ['OnSetDevice']
    THREAD_CONTEXT = __guid__.split('.')[-1]

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.trinityViewMatrix = trinity.TriView()
        self.trinityProjectionMatrix = trinity.TriProjection()
        self.cameraStartupInfo = None
        self.audioListener = None
        self.enabled = False
        self.transition = False
        defaultCamera = cameras.PolarCamera()
        defaultCamera.SetTrinityMatrixObjects(self.trinityViewMatrix, self.trinityProjectionMatrix)
        self.sharedCameras = {'Basic Camera': defaultCamera}
        self.cameraStack = [defaultCamera]

    def RegisterCameraStartupInfo(self, yaw, pitch, zoom):
        self.cameraStartupInfo = util.KeyVal(yaw=yaw, pitch=pitch, zoom=zoom)
        cam = self.GetActiveCamera()
        cam.yaw = yaw
        cam.pitch = pitch

    def AddSharedCamera(self, cameraName, cameraObj, setActive = False, transitionBehaviors = []):
        cameraObj.SetTrinityMatrixObjects(self.trinityViewMatrix, self.trinityProjectionMatrix)
        self.sharedCameras[cameraName] = cameraObj
        if setActive:
            self.PushActiveCamera(cameraObj, transitionBehaviors)

    def RemoveSharedCamera(self, cameraName):
        if cameraName in self.sharedCameras:
            del self.sharedCameras[cameraName]
        else:
            self.LogWarn('Attempting to remove shared camera ' + cameraName + " but it doesn't exist in the available cameras!")

    def GetSharedCamera(self, cameraName):
        if cameraName in self.sharedCameras:
            return self.sharedCameras[cameraName]

    def ResetCameras(self):
        for camera in self.cameraStack:
            camera.Reset()

    def ResetLayerInfo(self):
        for camera in self.cameraStack:
            camera.ResetLayer()

    def Disable(self):
        self.enabled = False

    def Enable(self):
        self.enabled = True

    def SetAudioListener(self, listener):
        self.audioListener = listener
        self.GetActiveCamera().audio2Listener = listener

    def PushActiveCamera(self, cameraObj, transitionBehaviors = []):
        cameraObj.SetTrinityMatrixObjects(self.trinityViewMatrix, self.trinityProjectionMatrix)
        if transitionBehaviors:
            uthread.new(self._PushAndTransition, cameraObj, transitionBehaviors).context = 'CameraClient::_PushAndTransitionNewCamera'
        else:
            if self.audioListener is not None:
                cameraObj.audio2Listener = self.audioListener
            self._PushNewCamera(cameraObj)

    def _PushAndTransition(self, cameraObj, transitionBehaviors):
        if self.audioListener is not None:
            cameraObj.audio2Listener = self.audioListener
        transitionCamera = cameras.TransitionCamera()
        transitionCamera.fieldOfView = cameraObj.fieldOfView
        transitionCamera.SetTrinityMatrixObjects(self.trinityViewMatrix, self.trinityProjectionMatrix)
        for transitionbehavior in transitionBehaviors:
            transitionCamera.AddBehavior(transitionbehavior)

        transitionCamera.SetTransitionTargets(self.GetActiveCamera(), cameraObj, pushing=True)
        self.transition = True
        self._PushNewCamera(transitionCamera)

    def _PushNewCamera(self, camera):
        if len(self.cameraStack):
            activeCamera = self.GetActiveCamera()
            activeCamera.Deactivate()
        self.cameraStack.append(camera)
        self._CreateCameraRenderJob()
        camera.Update()

    def PopAndPush(self, newCamera):
        if len(self.cameraStack) > 1:
            self.cameraStack.append(newCamera)
            self.cameraStack.remove(self.cameraStack[-2])
        else:
            self.cameraStack.append(newCamera)
        self.GetActiveCamera().UpdateProjectionMatrix()
        self._CreateCameraRenderJob()

    def PopActiveCamera(self, transitionBehaviors = []):
        if len(self.cameraStack) > 1:
            if transitionBehaviors:
                uthread.new(self._PopAndTransition, transitionBehaviors).context = 'CameraClient._PopAndTransition'
            else:
                self.GetActiveCamera().Deactivate()
                self.cameraStack.pop()
                self.GetActiveCamera().UpdateProjectionMatrix()
                self._CreateCameraRenderJob()
        else:
            self.LogWarn('Attempting to pop the default camera!  Cannot clear the camera stack!')

    def _PopAndTransition(self, transitionBehaviors):
        transitionCamera = cameras.TransitionCamera()
        transitionCamera.fieldOfView = self.GetActiveCamera().fieldOfView
        transitionCamera.SetTrinityMatrixObjects(self.trinityViewMatrix, self.trinityProjectionMatrix)
        for transitionbehavior in transitionBehaviors:
            transitionCamera.AddBehavior(transitionbehavior)

        transitionCamera.SetTransitionTargets(self.GetActiveCamera(), self.cameraStack[-2], pushing=False)
        self.transition = True
        self._PushNewCamera(transitionCamera)

    def SetDefaultCamera(self, camera, clearStack = True):
        if clearStack:
            self.cameraStack = [camera]
        else:
            self.cameraStack[0] = camera
        self.GetActiveCamera().UpdateProjectionMatrix()
        self._CreateCameraRenderJob()

    def GetDefaultCamera(self):
        return self.cameraStack[0]

    def GetActiveCamera(self):
        return self.cameraStack[-1]

    def GetCameraStack(self):
        return self.cameraStack

    def OnSetDevice(self):
        self.GetActiveCamera().UpdateProjectionMatrix()

    def _CreateCameraRenderJob(self):
        pass