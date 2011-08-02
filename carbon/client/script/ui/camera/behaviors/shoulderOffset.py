import cameras
import geo2
import math
import mathUtil

class ShoulderOffsetBehavior(cameras.CameraBehavior):
    __guid__ = 'cameras.ShoulderOffsetBehavior'

    def __init__(self, entID):
        self.entID = entID
        self.overShoulder = True
        self.startZoomFade = 1.0
        self.endZoomFade = 3.0
        self.startRotFade = 0.2
        self.endRotFade = 1.0
        self.shoulderShift = 0.25



    def SetOffsetData(self, startZoomFade, endZoomFade, startRotFade, endRotFade, shoulderShift):
        self.startZoomFade = startZoomFade
        self.endZoomFade = endZoomFade
        self.startRotFade = startRotFade
        self.endRotFade = endRotFade
        self.shoulderShift = shoulderShift



    def ProcessCameraUpdate(self, camera, now, frameTime):
        startPOI = camera.poi
        camera.SetPointOfInterest(geo2.Vec3Add(startPOI, self.DetermineShoulderOffset(camera.GetYaw(), camera.GetPitch(), camera.distance)))



    def SetCamOverTheShoulder(self, shoulder = True):
        self.overShoulder = shoulder



    def GetCamOverTheShoulder(self):
        return self.overShoulder



    def DetermineShoulderOffset(self, camYaw, camPitch, dist):
        shoulderShiftVector = (0, 0, 0)
        entity = self._GetEntity(self.entID)
        if entity:
            rot = entity.GetComponent('position').rotation
            (yaw, pitch, roll,) = geo2.QuaternionRotationGetYawPitchRoll(rot)
            camRot = abs((camYaw + yaw + 3 * math.pi / 2) % (2 * math.pi) - math.pi)
            if self.overShoulder and dist != 0 and dist < self.endZoomFade and camRot < self.endRotFade:
                self.shoulderShift = 0.25 * self.overShoulder
                shoulderShiftVector = geo2.QuaternionTransformVector(rot, (-self.shoulderShift, 0, 0))
                if dist > self.startZoomFade:
                    interp = (self.endZoomFade - dist) / (self.endZoomFade - self.startZoomFade)
                    interp = 3 * interp * interp - 2 * interp * interp * interp
                    shoulderShiftVector = geo2.Vec3Scale(shoulderShiftVector, interp)
                if camRot > self.startRotFade:
                    interp = (self.endRotFade - camRot) / (self.endRotFade - self.startRotFade)
                    interp = 3 * interp * interp - 2 * interp * interp * interp
                    shoulderShiftVector = geo2.Vec3Scale(shoulderShiftVector, interp)
        return shoulderShiftVector




