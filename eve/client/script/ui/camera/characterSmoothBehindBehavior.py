import geo2
import util
import cameras
import cameraUtils
SMOOTH_BEHIND_ANIMATION_SPEED = 0.04
SMOOTH_BEHIND_ANIMATION_SPEED_REALLY_FAST = 0.1

class CharacterSmoothBehindBehavior(cameras.CameraBehavior):
    __guid__ = 'cameras.CharacterSmoothBehindBehavior'

    def __init__(self, charEntID):
        cameras.CameraBehavior.__init__(self)
        self.charEntID = charEntID
        self.entity = None
        self.model = None
        self.camera = None
        self.frameTime = 0
        self.rotationSpeed = cameras.SMOOTH_BEHIND_ANIMATION_SPEED
        self.lastAvatarPosition = (0, 0, 0)
        self.lastAvatarRotation = (0, 0, 0)
        self.enableTriggerableSmoothBehind = 0
        self.smoothBehindEnabled = 1
        self.smoothBehind = False



    def SmoothBehind(self):
        yawDiff = cameraUtils.GetAngleFromEntityToCamera(self.entity)
        if abs(yawDiff) > const.FLOAT_TOLERANCE:
            if yawDiff < 0:
                if abs(yawDiff) > self.rotationSpeed:
                    self.camera.yaw -= self.rotationSpeed
                else:
                    self.camera.yaw -= abs(yawDiff)
                    self.smoothBehind = False
            elif abs(yawDiff) > self.rotationSpeed:
                self.camera.yaw += self.rotationSpeed
            else:
                self.camera.yaw += abs(yawDiff)
                self.smoothBehind = False
        else:
            self.smoothBehind = False



    def ProcessCameraUpdate(self, camera, now, frameTime):
        if not self.smoothBehindEnabled:
            return 
        self.camera = camera
        self.frameTime = frameTime
        if self.entity is None:
            self.entity = self._GetEntity(self.charEntID)
            if self.entity is None:
                raise RuntimeError("Problem retrieving the avatar's entity. cameras.CameraBehavior._GetEntity returned None for entityID", self.charEntID)
        if self.model is None:
            self.model = self._GetEntityModel(self.charEntID)
            if self.model is None:
                raise RuntimeError("Problem retrieving the avatar's model object. entityClient.FindEntityByID returned None for entityID", self.charEntID)
        if not camera.mouseLeftButtonDown and not camera.mouseRightButtonDown:
            avatarHasMoved = geo2.Vec3Distance(self.model.translation, self.lastAvatarPosition) > const.FLOAT_TOLERANCE
            avatarHasRotated = geo2.Vec3Distance(geo2.QuaternionRotationGetYawPitchRoll(self.model.rotation), self.lastAvatarRotation) > const.FLOAT_TOLERANCE
            movementDetected = avatarHasMoved or avatarHasRotated
            self.lastAvatarPosition = self.model.translation
            self.lastAvatarRotation = geo2.QuaternionRotationGetYawPitchRoll(self.model.rotation)
            if movementDetected:
                self.rotationSpeed = cameras.SMOOTH_BEHIND_ANIMATION_SPEED_REALLY_FAST
            else:
                self.rotationSpeed = cameras.SMOOTH_BEHIND_ANIMATION_SPEED
            if self.enableTriggerableSmoothBehind:
                if movementDetected:
                    self.smoothBehind = True
            else:
                self.smoothBehind = True
        else:
            self.smoothBehind = False
        if self.smoothBehind:
            self.SmoothBehind()



exports = util.AutoExports('cameras', locals())

