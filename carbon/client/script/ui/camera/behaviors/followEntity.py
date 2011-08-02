import cameras
import geo2
import math
import mathUtil
ANIM_HIP_HEIGHT = 0.9735
DEFAULT_CAM_BOUNCE_SCALAR = 0.6
MAX_CAMERA_LAG_TIME = 0.7
MAX_FUTURE_MOVE_TIME = 3.0
MAX_TELEPORT_DISTANCE_FOR_CAM_PAN_SQ = 25.0
MIN_TELEPORT_DISTANCE_FOR_CAM_PAN_SQ = 0.7071

class FollowEntityBehavior(cameras.CameraBehavior):
    __guid__ = 'cameras.FollowEntityBehavior'

    def __init__(self, entID):
        self.entID = entID
        self.boneName = 'Hips'
        self.camBounceScalar = DEFAULT_CAM_BOUNCE_SCALAR
        self.farYShift = 0.0
        self.closeYShift = 0.0
        self.farXShift = 0.0
        self.closeXShift = 0.0
        self.closeShiftDist = 0.0
        self.farShiftDist = 0.0
        self.isCameraSmoothing = False
        self.cameraLagTime = 0.0
        self.previousPosition = (0, 0, 0)
        self.defaultBoneShift = 0.0



    def SetCameraShiftData(self, yShift, xShift, shiftDistances):
        self.farYShift = yShift[0]
        self.closeYShift = yShift[1]
        self.farXShift = xShift[0]
        self.closeXShift = xShift[1]
        self.closeShiftDist = shiftDistances[0]
        self.farShiftDist = shiftDistances[1]



    def SetShiftBone(self, boneName):
        self.boneName = boneName



    def SetDefaultBoneShift(self, defaultShift):
        self.defaultBoneShift = defaultShift



    def ProcessCameraUpdate(self, camera, now, frameTime):
        shiftYDiff = self.closeYShift - self.farYShift
        shiftXDiff = self.closeXShift - self.farXShift
        factorRange = self.farShiftDist - self.closeShiftDist
        shiftFactor = max(0.0, min(1.0, (camera.distance - self.closeShiftDist) / factorRange))
        yShift = self.closeYShift - shiftYDiff * shiftFactor
        xShift = self.closeXShift - shiftXDiff * shiftFactor
        camera.poiModifier = (camera.poiModifier[0], camera.poiModifier[1] + self.ShiftAlongBone(), camera.poiModifier[2])
        entityPos = self.GetEntityPosition(camera, frameTime)
        camera.SetPointOfInterest((entityPos[0] + xShift, entityPos[1] + yShift, entityPos[2]))



    def ShiftAlongBone(self):
        entity = self._GetEntity(self.entID)
        if entity is not None:
            animController = entity.GetComponent('animation').controller
            if animController is not None:
                boneTransform = animController.animationNetwork.GetBoneTransform(self.boneName)
                if boneTransform:
                    (translation, orientation,) = boneTransform
                    return (translation[1] - ANIM_HIP_HEIGHT) * self.camBounceScalar
        return self.defaultBoneShift



    def GetEntityPosition(self, camera, frameTime):
        entity = self._GetEntity(self.entID)
        if entity is not None:
            entityPos = entity.GetComponent('position').position
            distancePos = (entityPos[0], 0.0, entityPos[2])
            prevDistancePos = (self.previousPosition[0], 0.0, self.previousPosition[2])
            distSq = geo2.Vec3DistanceSq(prevDistancePos, distancePos)
            if distSq < MAX_TELEPORT_DISTANCE_FOR_CAM_PAN_SQ and distSq > MIN_TELEPORT_DISTANCE_FOR_CAM_PAN_SQ or self.isCameraSmoothing:
                self.isCameraSmoothing = True
                self.cameraLagTime += frameTime
                if self.cameraLagTime >= MAX_CAMERA_LAG_TIME:
                    self.cameraLagTime = MAX_CAMERA_LAG_TIME
                    self.isCameraSmoothing = False
                progression = math.sin(self.cameraLagTime / MAX_CAMERA_LAG_TIME * (math.pi * 0.5))
                entityPos = geo2.Lerp(self.previousPosition, entityPos, progression)
            if not self.isCameraSmoothing:
                self.previousPosition = entityPos
                self.cameraLagTime = 0.0
            return entityPos
        return (0, 0, 0)



    def OnBehaviorAdded(self, camera):
        entity = self._GetEntity(self.entID)
        positionComponent = entity.GetComponent('position')
        (playerYaw, _, _,) = geo2.QuaternionRotationGetYawPitchRoll(positionComponent.rotation)
        camera.SetRotationWithYaw(playerYaw)
        self.previousPosition = positionComponent.position



    def SetPreviousPosition(self, pos):
        self.previousPosition = pos




