import cameras
import math
import geo2

class FlyCameraBehavior(cameras.CameraBehavior):
    __guid__ = 'cameras.FlyCameraBehavior'

    def __init__(self, transitionSeconds = 1.0):
        cameras.CameraBehavior.__init__(self)
        self.translationVector = [0.0, 0.0, 0.0]



    def GetTranslationVector(self):
        return self.translationVector



    def SetTranslationVector(self, translationVector):
        self.translationVector = translationVector



    def ProcessCameraUpdate(self, camera, now, frameTime):
        if self.translationVector != [0.0, 0.0, 0.0]:
            poi = camera.GetPointOfInterest()
            rotMatrix = geo2.MatrixRotationYawPitchRoll(math.pi / 2.0 - camera.yaw, math.pi / 2.0 - camera.pitch, 0.0)
            scaledVector = geo2.Vec3Scale(self.translationVector, frameTime)
            relativeVector = geo2.Vec3TransformCoord(scaledVector, rotMatrix)
            newPos = geo2.Vec3Add(poi, relativeVector)
            camera.SetPointOfInterest(newPos)




