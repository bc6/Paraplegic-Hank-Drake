import geo2
import math
import cameras

class SofaCamera(cameras.IncarnaCamera):
    __guid__ = 'cameras.SofaCamera'

    def __init__(self):
        cameras.IncarnaCamera.__init__(self)
        self.zoomAccelerate = 1.0
        self.zoom = self.desiredZoom = 2.9
        self.minPitch = 1.5
        self.maxPitch = 2.0



    def SetEntity(self, entity):
        rot = entity.GetComponent('position').rotation
        (yaw, pitch, roll,) = geo2.QuaternionRotationGetYawPitchRoll(rot)
        self.SetYaw(yaw)




