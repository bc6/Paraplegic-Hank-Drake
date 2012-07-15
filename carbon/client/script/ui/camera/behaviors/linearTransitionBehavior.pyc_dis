#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/camera/behaviors/linearTransitionBehavior.py
import math
import cameras

class LinearTransitionBehavior(cameras.CameraBehavior):
    __guid__ = 'cameras.LinearTransitionBehavior'

    def __init__(self, transitionSeconds = 1.0):
        cameras.CameraBehavior.__init__(self)
        self.transitionSeconds = transitionSeconds
        self.doneTime = 0
        self.changeX = None
        self.changeY = None
        self.changeZ = None
        self.changeYaw = None
        self.changePitch = None

    def ApplyCameraAttributes(self, camera, newPos, newYaw, newPitch, newFov):
        camera.SetPosition(newPos)
        camera.SetYaw(newYaw)
        camera.SetPitch(newPitch)
        camera.fieldOfView = newFov

    def ProcessCameraUpdate(self, camera, now, frameTime):
        self.changeX = camera.toPoint[0] - camera.fromPoint[0]
        self.changeY = camera.toPoint[1] - camera.fromPoint[1]
        self.changeZ = camera.toPoint[2] - camera.fromPoint[2]
        self.changeFov = camera.toFov - camera.fromFov
        yawDiff = camera.toRotation.yaw - camera.fromRotation.yaw
        if abs(yawDiff) > math.pi:
            yawDiff = math.pi - abs(camera.fromRotation.yaw) + (math.pi - abs(camera.toRotation.yaw))
        self.changeYaw = yawDiff
        self.changePitch = camera.toRotation.pitch - abs(camera.fromRotation.pitch)
        animPosition = min(1.0, self.doneTime / self.transitionSeconds)
        newX = camera.fromPoint[0] + self.changeX * animPosition
        newY = camera.fromPoint[1] + self.changeY * animPosition
        newZ = camera.fromPoint[2] + self.changeZ * animPosition
        newYaw = camera.fromRotation.yaw + self.changeYaw * animPosition
        newPitch = camera.fromRotation.pitch + self.changePitch * animPosition
        newFov = camera.fromFov + self.changeFov * animPosition
        self.doneTime += frameTime
        if animPosition >= 1.0:
            newX, newY, newZ = camera.toPoint[0], camera.toPoint[1], camera.toPoint[2]
            newYaw, newPitch = camera.toRotation.yaw, camera.toRotation.pitch
            newFov = camera.toFov
            self.ApplyCameraAttributes(camera, (newX, newY, newZ), newYaw, newPitch, newFov)
            camera.DoneTransitioning()
            return
        self.ApplyCameraAttributes(camera, (newX, newY, newZ), newYaw, newPitch, newFov)