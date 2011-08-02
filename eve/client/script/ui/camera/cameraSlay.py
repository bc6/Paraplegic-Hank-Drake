import math
import cameras

class CameraSlay(cameras.IncarnaCamera):
    __guid__ = 'cameras.CameraSlay'

    def __init__(self, minPitch, maxPitch):
        cameras.IncarnaCamera.__init__(self)
        self.minPitch = minPitch
        self.maxPitch = maxPitch
        self.minZoom = 0
        self.maxZoom = 1.5
        self.freeze = False



    def Update(self):
        if not self.freeze:
            cameras.IncarnaCamera.Update(self)




class CameraSlayBehavior(cameras.CameraBehavior):
    __guid__ = 'cameras.CameraSlayBehavior'

    def __init__(self, centerPoint):
        self.centerPoint = centerPoint
        self.originalYaw = None
        self.originalPitch = None



    def ProcessCameraUpdate(self, camera, now, frameTime):
        minPitch = 2.0 * math.pi / 4.0
        pitchRange = math.pi - minPitch
        currPitchLevel = camera.pitch - pitchRange
        maxSphereRadius = 1.8
        percOfPi = 1.0 - currPitchLevel / pitchRange
        percOfDistToCenter = currPitchLevel / pitchRange
        addUp = 1.2 * math.sin(math.pi / 2.0 * percOfDistToCenter)
        currRadius = maxSphereRadius * math.sin(math.pi / 2.0 * percOfPi)
        yaw = camera.yaw
        pitch = camera.pitch
        x = self.centerPoint[0]
        y = self.centerPoint[1]
        z = self.centerPoint[2]
        x0 = x + currRadius * math.cos(yaw)
        z0 = z + currRadius * math.sin(yaw)
        poi = (x0, y + addUp, z0)
        camera.SetPointOfInterest(poi)




