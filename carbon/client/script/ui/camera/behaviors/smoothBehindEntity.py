import geo2
import mathCommon
import cameras

class SmoothBehindEntityBehavior(cameras.CameraBehavior):
    __guid__ = 'cameras.SmoothBehindEntityBehavior'

    def __init__(self, entID):
        self.lastPosition = (0, 0, 0)
        self.entID = entID
        self.minSmoothRadians = 1.0
        self.fasterThenSlowerRatio = 1.0
        self.smoothLagFactor = 1.0



    def SetBehaviorData(self, minSmoothRadians, fasterThenSlowerRatio, smoothLagFactor):
        self.minSmoothRadians = minSmoothRadians
        self.fasterThenSlowerRatio = fasterThenSlowerRatio
        self.smoothLagFactor = smoothLagFactor



    def ProcessCameraUpdate(self, camera, now, frameTime):
        self.SmoothCameraBehindPlayer(camera, frameTime)



    def SmoothCameraBehindPlayer(self, camera, frameTime):
        entity = self._GetEntity(self.entID)
        if entity:
            isMoving = entity.position.position != self.lastPosition
            self.lastPosition = entity.position.position
            if isMoving and not uicore.uilib.rightbtn and not uicore.uilib.leftbtn:
                plrYaw = geo2.QuaternionRotationGetYawPitchRoll(entity.position.rotation)[0]
                curCamYaw = camera.GetRotationAsYaw()
                diff = mathCommon.GetLesserAngleBetweenYaws(plrYaw, curCamYaw)
                maxRot = self.minSmoothRadians * frameTime
                minRot = -maxRot
                if diff > maxRot:
                    maxRot = (diff - maxRot) * self.fasterThenSlowerRatio * frameTime + maxRot
                if diff < minRot:
                    maxRot = -((diff - minRot) * self.fasterThenSlowerRatio * frameTime + minRot)
                camera.AdjustYaw(diff / self.smoothLagFactor, maxRot, ignoreUpdate=True)




