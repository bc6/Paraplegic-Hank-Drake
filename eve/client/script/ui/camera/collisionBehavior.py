import geo2
import util
import math
import cameras
import trinity
import mathUtil
import cameraUtils
AVATAR_SHOULDER_HEIGHT = 1.55
AVATAR_SHOULDER_HEIGHT_ZOOM_OUT = 1.6
CLOSEST_CAMERA_DISTANCE = 0.2
ZOOM_POWER = 15
MAX_MOUSE_MOVE_DELTA = 0.08
CORNER_DETECTION_SPHERE = 0.3
NORMAL_COLLISION_SPHERE = 0.199
CRITICAL_COLLISION_SPHERE = 0.1
CAMERA_BUFFER_SPHERE_RADIUS = 0.2
NORMAL_COLLISION_SMOOTHING_STEPS = 5
CRITICAL_COLLISION_POSITIONING_RADIUS = 0.11

class CollisionBehavior(cameras.CameraBehavior):
    __guid__ = 'cameras.CollisionBehavior'

    def __init__(self):
        cameras.CameraBehavior.__init__(self)
        self.centerPoint = (0, 0, 0)
        self.model = None
        self.entity = None
        self.entityID = None
        self.camera = None
        self.collidingRight = False
        self.originalPitchDirection = 0
        self.lastCameraMouseYawDelta = 0
        self.lastCameraMousePitchDelta = 0
        self.colliding = False
        self.originalZoom = 1.0
        self.exitingCollision = False
        self.frameTime = 0
        self.pushUp = 0



    def SetEntity(self, entity):
        self.entity = entity
        self.entityID = entity.entityID



    def YawPitchDistToPoint(self, yaw, pitch, dist):
        if trinity.IsRightHanded():
            position = (dist * math.sin(pitch) * math.cos(yaw), -dist * math.cos(pitch), dist * math.sin(pitch) * math.sin(yaw))
        else:
            position = (-dist * math.sin(pitch) * math.cos(yaw), dist * math.cos(pitch), -dist * math.sin(pitch) * math.sin(yaw))
        return position



    def AvoidCollision(self, now, cameraAdvancedPos):
        cornerHit = self.gameWorld.SweptSphere(self.centerPoint, cameraAdvancedPos, cameras.CORNER_DETECTION_SPHERE)
        if cornerHit and geo2.Vec3Distance(cornerHit[0], self.centerPoint) == 0:
            cornerHit = None
        if cornerHit or self.gameWorld.SphereTest(cameraAdvancedPos, cameras.NORMAL_COLLISION_SPHERE):
            if not self.colliding:
                if self.lastCameraMouseYawDelta > 0:
                    self.collidingRight = True
                else:
                    self.collidingRight = False
                if self.lastCameraMousePitchDelta == 0:
                    self.originalPitchDirection = 1
                else:
                    self.originalPitchDirection = self.lastCameraMousePitchDelta / abs(self.lastCameraMousePitchDelta)
                self.colliding = True
                self.originalZoom = self.camera.zoom
        criticalFailInfo = self.gameWorld.SweptSphere(self.centerPoint, cameraAdvancedPos, cameras.CRITICAL_COLLISION_SPHERE)
        if criticalFailInfo:
            if abs(self.lastCameraMouseYawDelta) > abs(self.lastCameraMousePitchDelta):
                if self.collidingRight:
                    toZoom = self.camera.collisionZoom - self.lastCameraMouseYawDelta * cameras.ZOOM_POWER
                else:
                    toZoom = self.camera.collisionZoom + self.lastCameraMouseYawDelta * cameras.ZOOM_POWER
            elif self.lastCameraMousePitchDelta == 0:
                currSign = 1
            else:
                currSign = self.lastCameraMousePitchDelta / abs(self.lastCameraMousePitchDelta)
            if currSign != self.originalPitchDirection:
                toZoom = self.camera.collisionZoom + abs(self.lastCameraMousePitchDelta) * cameras.ZOOM_POWER
            else:
                toZoom = self.camera.collisionZoom - abs(self.lastCameraMousePitchDelta) * cameras.ZOOM_POWER
            desiredPos = geo2.Vec3Add(criticalFailInfo[0], (val * cameras.CRITICAL_COLLISION_POSITIONING_RADIUS for val in criticalFailInfo[1]))
            (yaw, pitch, dist,) = self.camera.PointToYawPitchDist(desiredPos)
            self.camera.zoom = self.camera.desiredZoom = self.camera.collisionZoom = dist
            self.camera.poi = self.centerPoint
        if self.colliding:
            currCollidingAdvancePoint = self.AssembleFuturePoint(self.camera.yaw, self.camera.pitch, self.camera.zoom)
            if self.gameWorld.SweptSphere(self.centerPoint, currCollidingAdvancePoint, cameras.NORMAL_COLLISION_SPHERE) is None:
                newZoom = mathUtil.Lerp(self.camera.collisionZoom, self.camera.maxZoom, self.frameTime * cameras.ZOOM_SPEED_MODIFIER)
                newZoom = min(self.camera.maxZoom, newZoom)
                amountPerFrame = abs(newZoom - self.camera.zoom) / cameras.NORMAL_COLLISION_SMOOTHING_STEPS
                self.camera.SetCollisionZoom(newZoom, amountPerFrame)
            cameraPreCollisionPos = self.AssembleFuturePoint(self.camera.yaw, self.camera.pitch, self.originalZoom)
            criticalFailInfo = self.gameWorld.SweptSphere(self.centerPoint, cameraPreCollisionPos, cameras.CAMERA_BUFFER_SPHERE_RADIUS)
            if not criticalFailInfo and cornerHit is None and not self.gameWorld.SphereTest(cameraPreCollisionPos, cameras.NORMAL_COLLISION_SPHERE):
                self.camera.desiredZoom = self.originalZoom
                self.camera.collisionZoom = self.camera.zoom
                self.colliding = False
                self.exitingCollision = True
            elif abs(self.camera.mouseYawDelta) > 0 or abs(self.camera.mousePitchDelta) > 0:
                if abs(self.camera.mouseYawDelta) > abs(self.camera.mousePitchDelta):
                    delta = self.GetCameraMouseYawDelta()
                    if self.collidingRight:
                        toZoom = self.camera.collisionZoom - delta * cameras.ZOOM_POWER
                    else:
                        toZoom = self.camera.collisionZoom + delta * cameras.ZOOM_POWER
                else:
                    delta = abs(self.camera.mousePitchDelta)
                    currSign = self.camera.mousePitchDelta / abs(self.camera.mousePitchDelta)
                    if currSign != self.originalPitchDirection:
                        toZoom = self.camera.collisionZoom + delta * cameras.ZOOM_POWER
                    else:
                        toZoom = self.camera.collisionZoom - delta * cameras.ZOOM_POWER
                zoomPos = self.camera.YawPitchDistToPoint(self.camera.yaw, self.camera.pitch, toZoom)
                zoomPos = geo2.Vec3Add(zoomPos, self.centerPoint)
                if self.camera.mouseYawDelta > const.FLOAT_TOLERANCE or self.camera.mousePitchDelta > const.FLOAT_TOLERANCE:
                    if not self.gameWorld.SphereTest(zoomPos, cameras.CRITICAL_COLLISION_SPHERE) and self.gameWorld.SweptSphere(self.centerPoint, zoomPos, cameras.NORMAL_COLLISION_SPHERE):
                        if toZoom > cameras.CLOSEST_CAMERA_DISTANCE and toZoom < self.camera.zoom:
                            amountPerFrame = abs(self.camera.collisionZoom - self.camera.zoom) / cameras.NORMAL_COLLISION_SMOOTHING_STEPS
                            self.camera.SetCollisionZoom(toZoom, amountPerFrame)
                if self.camera.collisionZoom < cameras.CLOSEST_CAMERA_DISTANCE:
                    amountPerFrame = abs(self.camera.collisionZoom - self.camera.zoom) / cameras.NORMAL_COLLISION_SMOOTHING_STEPS
                    self.camera.SetCollisionZoom(cameras.CLOSEST_CAMERA_DISTANCE, amountPerFrame)
                if self.camera.collisionZoom > self.camera.zoom:
                    amountPerFrame = abs(self.camera.collisionZoom - self.camera.zoom) / cameras.NORMAL_COLLISION_SMOOTHING_STEPS
                    self.camera.SetCollisionZoom(self.camera.zoom, amountPerFrame)



    def AssembleFuturePoint(self, yaw, pitch, zoom):
        cameraAdvancedPos = self.camera.YawPitchDistToPoint(yaw, pitch, zoom)
        cameraAdvancedPos = geo2.Vec3Add(cameraAdvancedPos, self.centerPoint)
        return cameraAdvancedPos



    def GetCameraMouseYawDelta(self):
        delta = self.camera.mouseYawDelta
        if delta < 0:
            delta = max(delta, -cameras.MAX_MOUSE_MOVE_DELTA)
        elif delta > 0:
            delta = min(delta, cameras.MAX_MOUSE_MOVE_DELTA)
        return delta



    def InitCameraPosition(self):
        yawDiff = cameraUtils.GetAngleFromEntityToCamera(self.entity)
        if abs(yawDiff) > const.FLOAT_TOLERANCE:
            newYaw = self.camera.yaw + yawDiff
            self.camera.yaw = newYaw



    def CalcCameraPosition(self):
        self.centerPoint = (self.entity.position.position[0], self.entity.position.position[1] + self.pushUp, self.entity.position.position[2])
        self.cameraAdvancedPos = self.AssembleFuturePoint(self.camera.yaw, self.camera.pitch, self.camera.zoom)



    def Reset(self):
        self.model = None
        self.entity = None
        self.gameWorld = None
        self._LoadGameWorld()



    def AcquireGameworldObjects(self):
        if self.entity is None:
            self.entity = self._GetEntity(self.entityID)
            if self.entity is not None:
                self.InitCameraPosition()
        if self.model is None:
            self.model = self._GetEntityModel(self.entityID)



    def ProcessCameraUpdate(self, camera, now, frameTime):
        self.AcquireGameworldObjects()
        if self.entity is None:
            return 
        self.camera = camera
        self.frameTime = frameTime
        self.CalcCameraPosition()
        if abs(self.camera.mouseYawDelta) != 0:
            self.lastCameraMouseYawDelta = self.GetCameraMouseYawDelta()
        if abs(self.camera.mousePitchDelta) != 0:
            self.lastCameraMousePitchDelta = self.camera.mousePitchDelta
        self.camera.SetPointOfInterest(self.centerPoint)
        if self.gameWorld is not None:
            self.AvoidCollision(now, self.cameraAdvancedPos)
        else:
            self._LoadGameWorld()



exports = util.AutoExports('cameras', locals())

