import util
import cameras

class TransitionCamera(cameras.BasicCamera):
    __guid__ = 'cameras.TransitionCamera'

    def __init__(self):
        cameras.BasicCamera.__init__(self)
        self.fromCamera = None
        self.toCamera = None
        self.pushing = False



    def SetTransitionTargets(self, fromCamera, toCamera, pushing = True):
        self.fromCamera = fromCamera
        self.toCamera = toCamera
        self.pushing = pushing
        self.SetPosition(self.fromCamera.cameraPosition)
        self.SetYaw(self.fromCamera.yaw)
        self.SetPitch(self.fromCamera.pitch)
        self.fromPoint = self.fromCamera.cameraPosition
        self.fromRotation = util.KeyVal(yaw=self.fromCamera.yaw, pitch=self.fromCamera.pitch)
        self.toPoint = self.toCamera.cameraPosition
        self.toRotation = util.KeyVal(yaw=self.toCamera.yaw, pitch=self.toCamera.pitch)
        self.fromFov = self.fromCamera.fieldOfView
        self.toFov = self.toCamera.fieldOfView



    def PerformPick(self, x, y, ignoreEntID = -1):
        pass



    def DoneTransitioning(self):
        camClient = sm.GetService('cameraClient')
        camClient.transition = False
        if self.pushing:
            camClient.PopAndPush(self.toCamera)
        else:
            camClient.PopActiveCamera()
            camClient.PopActiveCamera()



    def UpdateToCamera(self):
        self.toCamera.Update()
        self.toPoint = self.toCamera.cameraPosition
        self.toRotation = util.KeyVal(yaw=self.toCamera.yaw, pitch=self.toCamera.pitch)



    def Update(self):
        self.UpdateToCamera()
        cameras.BasicCamera.Update(self)




