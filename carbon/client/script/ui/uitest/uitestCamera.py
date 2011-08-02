import cameras
import trinity
import math
import geo2
import uiutil
import blue
import mathUtil

class UICamera(cameras.BasicCamera):
    __guid__ = 'cameras.UICamera'

    def __init__(self):
        cameras.BasicCamera.__init__(self)
        self.frontClip = 0.1
        self.backClip = 100000.0
        self.pitch = math.pi / 2
        self.distance = 100.0
        self.poi = (0, 0, 0)
        self.cameraPosition = (0, 0, 1000)
        self.direction = (0, 0, 1)



    def Dolly(self, delta):
        self.distance += delta



    def Pan(self, dx, dy):
        pass



    def AdjustYaw(self, delta):
        cameras.BasicCamera.AdjustYaw(self, delta * 0.005)



    def SetYaw(self, yaw, ignoreUpdate = True):
        cameras.BasicCamera.SetYaw(self, yaw)



    def AdjustPitch(self, delta):
        cameras.BasicCamera.AdjustPitch(self, delta * 0.005)



    def Update(self):
        cameras.BasicCamera.Update(self)
        self.UpdateProjectionMatrix()



    def AdjustForDesktop(self):
        theta = self.fieldOfView * 0.5
        h = float(self.desktop.height * 0.5)
        h2 = h * h
        r = h / math.sin(theta)
        r2 = r * r
        distance = math.sqrt(r2 - h2)
        self.cameraPosition = (0, 0, distance)
        self.cameraDirection = (0, 0, -1)
        self.Update()
        print distance




