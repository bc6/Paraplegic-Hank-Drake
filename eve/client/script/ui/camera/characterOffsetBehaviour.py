import geo2
import util
import math
import cameras
import trinity
import mathUtil
import mathCommon
CHARACTER_OFFSET_FACTOR = 0.7
OPTIMAL_SCREEN_ASPECT_RATIO = 1.7
PITCH_OFFSET_LENGTH_MODIFIER = 0.384
ZOOM_POWER_FAR = 15
ZOOM_POWER_CLOSE = 10
MIN_CAMERA_ZOOM_ACCELERATE = 10
AVATAR_MIN_DISPLAY_DISTANCE = 0.58
COLLISION_POSPOI_TRANSITION_TIME = 1.0
POST_COLLISION_ZOOM_OUT_ACCELERATE = 1.1
ZOOM_TOGGLE_TRANSITION_SPEEDUP_FACTOR = 1.2
ZOOM_TOGGLE_TRANSITION_SPEEDUP_TEMPERING = 0.9
ZOOM_IN_ADJUSTMENT_FOR_TOGGLING_COLLISIONS = 0.05

class CharacterOffsetBehaviour(cameras.CollisionBehavior):
    __guid__ = 'cameras.CharacterOffsetBehaviour'

    def __init__(self, charEntID):
        cameras.CollisionBehavior.__init__(self)
        self.entityID = charEntID
        self.cameraOffsetModifier = 1.0
        self.toggleZoomAvatarPos = (0, 0, 0)
        self.zoomAccelerate = 1.0
        self.desiredPosAndPoiTransitionSeconds = 0.0
        self.desiredPoi = None
        self.originalPoi = None
        self.desiredZoom = None
        self.preToggleZoom = None
        self.collidingAfterZoomToggle = False
        self.lastCameraZoomData = None
        self.postZoomToggleTransitionAdjustmentRequired = False
        self.avatarHasMoved = False
        self.lastAvatarPosition = (0, 0, 0)
        self.pushUp = cameras.AVATAR_SHOULDER_HEIGHT



    def AdjustOffset(self, newOffsetModifier):
        if newOffsetModifier is not None:
            self.cameraOffsetModifier = newOffsetModifier



    def CalcCorrectCameraPoi(self, yaw, pitch, zoom, overrideCollisionLogic = False):
        if not overrideCollisionLogic:
            if self.camera.zoomToggle == cameras.CAMERA_ZOOM_FAR and abs(self.camera.zoom - self.camera.desiredZoom) < const.FLOAT_TOLERANCE:
                self.exitingCollision = False
                if not self.colliding:
                    self.camera.zoomAccelerate = 1.0
                return self.centerPoint
            if self.camera.zoomToggle == cameras.CAMERA_ZOOM_FAR and self.exitingCollision:
                self.camera.zoomAccelerate *= cameras.POST_COLLISION_ZOOM_OUT_ACCELERATE + self.frameTime
                self.camera.zoomAccelerate = min(cameras.MIN_CAMERA_ZOOM_ACCELERATE, self.camera.zoomAccelerate)
                return self.centerPoint
            if not self.colliding:
                self.camera.zoomAccelerate = 1.0
                self.exitingCollision = False
        elif self.camera.zoomToggle == cameras.CAMERA_ZOOM_FAR:
            return self.centerPoint
        pitchOffsetVectorPower = (pitch - math.pi / 2.0) / (self.camera.maxPitch - math.pi / 2.0)
        pitchOffsetVectorPower *= cameras.PITCH_OFFSET_LENGTH_MODIFIER
        if pitchOffsetVectorPower <= 0:
            pitchOffsetVectorPower = pitchOffsetVectorPower / 2.0
        pitchShiftVector = mathCommon.CreateDirectionVectorFromYawAndPitchAngle(yaw - 0, pitch + math.pi / 2.0)
        charOffsetFactor = cameras.CHARACTER_OFFSET_FACTOR * self.cameraOffsetModifier
        zoomPerc = 1.0 - (zoom - self.camera.minZoom) / (self.camera.maxZoom - self.camera.minZoom)
        if zoom < self.camera.minZoom:
            zoomPerc = zoom / self.camera.minZoom
        charOffsetFactor *= zoomPerc
        pitchOffsetVectorPower *= zoomPerc
        screenAspectRatio = float(trinity.app.width) / float(trinity.app.height)
        if screenAspectRatio < cameras.OPTIMAL_SCREEN_ASPECT_RATIO:
            shorten = screenAspectRatio / cameras.OPTIMAL_SCREEN_ASPECT_RATIO
            charOffsetFactor *= shorten
        x = self.centerPoint[0]
        z = self.centerPoint[2]
        x0 = x + math.cos(yaw - math.pi / 2) * charOffsetFactor
        z0 = z + math.sin(yaw - math.pi / 2) * charOffsetFactor
        shoulderOffsetPoint = (x0, self.centerPoint[1], z0)
        newPoi = geo2.Vec3Add(shoulderOffsetPoint, (val * pitchOffsetVectorPower for val in pitchShiftVector))
        if self.postZoomToggleTransitionAdjustmentRequired:
            diffDist = geo2.Vec3Distance(self.camera.poi, newPoi)
            if diffDist > const.FLOAT_TOLERANCE:
                x = mathUtil.Lerp(self.camera.poi[0], newPoi[0], self.frameTime * cameras.ZOOM_SPEED_MODIFIER * self.zoomAccelerate)
                y = mathUtil.Lerp(self.camera.poi[1], newPoi[1], self.frameTime * cameras.ZOOM_SPEED_MODIFIER * self.zoomAccelerate)
                z = mathUtil.Lerp(self.camera.poi[2], newPoi[2], self.frameTime * cameras.ZOOM_SPEED_MODIFIER * self.zoomAccelerate)
                testNewPoi = (x, y, z)
                newDist = geo2.Vec3Distance(self.camera.poi, testNewPoi)
                if newDist > diffDist:
                    self.postZoomToggleTransitionAdjustmentRequired = False
                    self.zoomAccelerate = 1.0
                else:
                    self.zoomAccelerate *= cameras.ZOOM_TOGGLE_TRANSITION_SPEEDUP_FACTOR
                newPoi = testNewPoi
            else:
                self.postZoomToggleTransitionAdjustmentRequired = False
            self.zoomAccelerate = 1.0
        return newPoi



    def AvoidCollision(self, cameraAdvancedPos):
        zoomPower = cameras.ZOOM_POWER_CLOSE
        if self.camera.zoomToggle == cameras.CAMERA_ZOOM_FAR:
            zoomPower = cameras.ZOOM_POWER_FAR
        properZoom = self.camera.maxZoom
        if self.camera.zoomToggle == cameras.CAMERA_ZOOM_CLOSE:
            properZoom = self.camera.minZoom
        if self.camera.zoomToggle == cameras.CAMERA_ZOOM_CLOSE:
            self.CloseZoomToggleCollision(cameraAdvancedPos, properZoom, zoomPower)
        else:
            self.FarZoomToggleCollision(cameraAdvancedPos, properZoom, zoomPower)



    def FarZoomToggleCollision(self, cameraAdvancedPos, properZoom, zoomPower):
        hit = self.gameWorld.SweptSphere(self.centerPoint, cameraAdvancedPos, cameras.NORMAL_COLLISION_SPHERE)
        if hit is not None:
            if not self.colliding:
                self.colliding = True
                self.originalZoom = properZoom
        if self.colliding:
            currDir = geo2.Vec3Normalize(geo2.Vec3Subtract(cameraAdvancedPos, self.centerPoint))
            fullZoomPos = geo2.Vec3Add(self.centerPoint, (val * self.originalZoom for val in currDir))
            hit = self.gameWorld.SweptSphere(self.centerPoint, fullZoomPos, cameras.NORMAL_COLLISION_SPHERE)
            if hit:
                safeSpot = geo2.Vec3Add(hit[0], (val * cameras.NORMAL_COLLISION_SPHERE for val in hit[1]))
                newZoom = min(self.camera.maxZoom, geo2.Vec3Distance(self.centerPoint, safeSpot))
                self.camera.poi = self.CalcCorrectCameraPoi(self.camera.yaw, self.camera.pitch, newZoom)
                self.camera.collisionZoom = self.camera.zoom = self.camera.desiredZoom = newZoom
            else:
                self.camera.desiredZoom = self.originalZoom
            self.camera.collisionZoom = self.camera.zoom
            self.colliding = False
            self.exitingCollision = True
        self.camera.poi = self.CalcCorrectCameraPoi(self.camera.yaw, self.camera.pitch, self.camera.zoom)



    def CloseZoomToggleCollision(self, cameraAdvancedPos, properZoom, zoomPower):
        criticalFailInfo = self.gameWorld.SweptSphere(self.centerPoint, cameraAdvancedPos, cameras.NORMAL_COLLISION_SPHERE)
        if criticalFailInfo:
            if not self.colliding:
                self.colliding = True
                self.originalZoom = properZoom
            safeSpot = geo2.Vec3Add(criticalFailInfo[0], (val * cameras.NORMAL_COLLISION_SPHERE for val in criticalFailInfo[1]))
            newZoom = min(self.camera.minZoom, geo2.Vec3Distance(self.centerPoint, safeSpot))
            self.camera.poi = self.CalcCorrectCameraPoi(self.camera.yaw, self.camera.pitch, newZoom)
            self.camera.collisionZoom = self.camera.zoom = self.camera.desiredZoom = newZoom
        elif self.colliding:
            self.camera.desiredZoom = self.originalZoom
            self.camera.collisionZoom = self.camera.zoom
            self.colliding = False
            self.exitingCollision = True



    def AssembleFuturePoint(self, yaw, pitch, zoom):
        cameraAdvancedPos = self.camera.YawPitchDistToPoint(yaw, pitch, zoom)
        advancedPoi = self.CalcCorrectCameraPoi(yaw, pitch, zoom)
        cameraAdvancedPos = geo2.Vec3Add(cameraAdvancedPos, advancedPoi)
        return cameraAdvancedPos



    def LerpToDesiredPosAndPoi(self):
        moveDist = geo2.Vec3Distance(self.model.translation, self.toggleZoomAvatarPos)
        if moveDist > const.FLOAT_TOLERANCE:
            moveNormal = geo2.Vec3Normalize(geo2.Vec3Subtract(self.model.translation, self.toggleZoomAvatarPos))
            self.camera.poi = geo2.Vec3Add(self.camera.poi, (val * moveDist for val in moveNormal))
            self.desiredPoi = geo2.Vec3Add(self.desiredPoi, (val * moveDist for val in moveNormal))
            self.toggleZoomAvatarPos = self.model.translation
            self.zoomAccelerate *= 1.1
            self.zoomAccelerate = min(10, self.zoomAccelerate)
        x = mathUtil.Lerp(self.camera.poi[0], self.desiredPoi[0], self.frameTime * cameras.ZOOM_SPEED_MODIFIER * self.zoomAccelerate)
        y = mathUtil.Lerp(self.camera.poi[1], self.desiredPoi[1], self.frameTime * cameras.ZOOM_SPEED_MODIFIER * self.zoomAccelerate)
        z = mathUtil.Lerp(self.camera.poi[2], self.desiredPoi[2], self.frameTime * cameras.ZOOM_SPEED_MODIFIER * self.zoomAccelerate)
        newPoi = (x, y, z)
        self.camera.zoom = mathUtil.Lerp(self.camera.zoom, self.desiredZoom, self.frameTime * cameras.ZOOM_SPEED_MODIFIER * self.zoomAccelerate)
        self.zoomAccelerate *= cameras.ZOOM_TOGGLE_TRANSITION_SPEEDUP_FACTOR + self.frameTime
        self.zoomAccelerate = self.zoomAccelerate ** cameras.ZOOM_TOGGLE_TRANSITION_SPEEDUP_TEMPERING
        poiDist = geo2.Vec3Distance(self.camera.poi, self.desiredPoi)
        if abs(self.camera.zoom - self.desiredZoom) < const.FLOAT_TOLERANCE and poiDist < const.FLOAT_TOLERANCE:
            if self.camera.zoomToggle == cameras.CAMERA_ZOOM_FAR:
                self.camera.zoomToggle = cameras.CAMERA_ZOOM_CLOSE
            else:
                self.camera.zoomToggle = cameras.CAMERA_ZOOM_FAR
            self.zoomAccelerate = 1.0
            if self.camera.zoomToggle == cameras.CAMERA_ZOOM_CLOSE:
                currProperPoi = self.CalcCorrectCameraPoi(self.camera.yaw, self.camera.pitch, self.camera.zoom, overrideCollisionLogic=True)
                distToProperPoi = geo2.Vec3Distance(currProperPoi, self.desiredPoi)
                if distToProperPoi > const.FLOAT_TOLERANCE:
                    self.postZoomToggleTransitionAdjustmentRequired = True
                    self.zoomAccelerate = 1.1
            self.camera.zoom = self.camera.desiredZoom = self.camera.collisionZoom = self.desiredZoom
            self.camera.SetPointOfInterest(self.desiredPoi)
            self.desiredPoi = None
            self.colliding = self.collidingAfterZoomToggle
            self.exitingCollision = False
            return 
        self.camera.SetPointOfInterest(newPoi)
        self.camera.desiredZoom = self.camera.collisionZoom = self.camera.zoom



    def CheckCameraCanToggleZoom(self):
        if self.lastCameraZoomData is not None:
            useLastZoomData = True
        else:
            useLastZoomData = False
        if self.camera.zoomToggle == cameras.CAMERA_ZOOM_CLOSE:
            toggleZoom = self.camera.maxZoom
            toggleZoomFlag = cameras.CAMERA_ZOOM_FAR
        else:
            toggleZoom = self.camera.minZoom
            toggleZoomFlag = cameras.CAMERA_ZOOM_CLOSE
        cameraCurrPos = self.camera.YawPitchDistToPoint(self.camera.yaw, self.camera.pitch, self.camera.zoom)
        currPoi = self.CalcCorrectCameraPoi(self.camera.yaw, self.camera.pitch, self.camera.zoom, overrideCollisionLogic=True)
        cameraCurrPos = geo2.Vec3Add(cameraCurrPos, currPoi)
        togglePos = self.camera.YawPitchDistToPoint(self.camera.yaw, self.camera.pitch, toggleZoom)
        currZoomToggle = self.camera.zoomToggle
        self.camera.zoomToggle = toggleZoomFlag
        togglePoi = self.CalcCorrectCameraPoi(self.camera.yaw, self.camera.pitch, toggleZoom, overrideCollisionLogic=True)
        self.camera.zoomToggle = currZoomToggle
        togglePos = geo2.Vec3Add(togglePos, togglePoi)
        moveNormal = geo2.Vec3Normalize(geo2.Vec3Subtract(togglePos, cameraCurrPos))
        add = 0
        hitDuringTransition = None
        while add < toggleZoom:
            if add + cameras.NORMAL_COLLISION_SPHERE > toggleZoom:
                add = toggleZoom
            pos = geo2.Vec3Add(cameraCurrPos, (val * add for val in moveNormal))
            hitDuringTransition = self.gameWorld.SphereTest(pos, cameras.NORMAL_COLLISION_SPHERE)
            add += cameras.NORMAL_COLLISION_SPHERE
            if hitDuringTransition:
                break

        togglingUnderCollisionConditions = True
        hitAtDestination = self.gameWorld.SweptSphere(togglePos, cameraCurrPos, cameras.NORMAL_COLLISION_SPHERE)
        hitting = hitAtDestination is not None or hitDuringTransition
        if not hitting and not self.colliding:
            self.camera.desiredZoom = toggleZoom
            self.camera.zoomToggle = toggleZoomFlag
            togglingUnderCollisionConditions = False
        elif not hitting and self.colliding:
            if useLastZoomData:
                self.desiredPoi = self.lastCameraZoomData.poi
                self.desiredZoom = self.lastCameraZoomData.zoom
            else:
                self.desiredPoi = togglePoi
                self.desiredZoom = toggleZoom
            self.collidingAfterZoomToggle = False
        else:
            hit = self.gameWorld.SweptSphere(self.centerPoint, togglePos, cameras.NORMAL_COLLISION_SPHERE)
            if hit and hit[0] == cameraCurrPos:
                hit = self.gameWorld.LineTest(cameraCurrPos, togglePos)
                if hit:
                    hit = (hit[1], hit[2])
                else:
                    hit = self.gameWorld.LineTest(togglePoi, togglePos)
                    if hit:
                        hit = (hit[1], hit[2])
            if hit is not None and hit[0] != cameraCurrPos:
                currZoomToggle = self.camera.zoomToggle
                desiredZoomToggle = cameras.CAMERA_ZOOM_FAR
                if currZoomToggle == cameras.CAMERA_ZOOM_FAR:
                    desiredZoomToggle = cameras.CAMERA_ZOOM_CLOSE
                self.camera.zoomToggle = desiredZoomToggle
                togglePoi = self.CalcCorrectCameraPoi(self.camera.yaw, self.camera.pitch, geo2.Vec3Distance(hit[0], self.centerPoint), overrideCollisionLogic=True)
                hitPos = geo2.Vec3Add(hit[0], (val * cameras.NORMAL_COLLISION_SPHERE for val in hit[1]))
                if self.camera.zoomToggle == cameras.CAMERA_ZOOM_CLOSE:
                    desiredZoom = min(self.camera.minZoom, geo2.Vec3Distance(self.centerPoint, hitPos))
                else:
                    desiredZoom = min(self.camera.maxZoom, geo2.Vec3Distance(self.centerPoint, hitPos))
                desiredPoi = self.CalcCorrectCameraPoi(self.camera.yaw, self.camera.pitch, desiredZoom, overrideCollisionLogic=True)
                postAdjustmentCameraPos = self.camera.YawPitchDistToPoint(self.camera.yaw, self.camera.pitch, desiredZoom)
                postAdjustmentCameraPos = geo2.Vec3Add(postAdjustmentCameraPos, desiredPoi)
                if useLastZoomData:
                    self.desiredPoi = self.lastCameraZoomData.poi
                    self.desiredZoom = self.lastCameraZoomData.zoom
                else:
                    self.desiredPoi = desiredPoi
                    self.desiredZoom = desiredZoom
                self.camera.zoomToggle = currZoomToggle
                self.originalZoom = toggleZoom
                self.collidingAfterZoomToggle = True
            elif useLastZoomData:
                self.desiredPoi = self.lastCameraZoomData.poi
                self.desiredZoom = self.lastCameraZoomData.zoom
            else:
                self.desiredPoi = togglePoi
                self.desiredZoom = toggleZoom
            self.collidingAfterZoomToggle = False
        if togglingUnderCollisionConditions:
            self.preToggleZoom = self.camera.zoom
            self.originalPoi = self.camera.poi
            self.desiredPosAndPoiTransitionSeconds = 0.0
            self.zoomAccelerate = 1.1
            self.camera.yawSpeed = 0
        if self.desiredPoi is not None:
            self.toggleZoomAvatarPos = self.model.translation
        self.camera.wantToToggleZoom = False
        self.lastCameraZoomData = None



    def CalcCameraPosition(self):
        self.centerPoint = (self.entity.position.position[0], self.entity.position.position[1] + self.pushUp, self.entity.position.position[2])
        self.cameraAdvancedPos = self.AssembleFuturePoint(self.camera.yaw, self.camera.pitch, self.camera.zoom)
        avatarPosRelativeToCamera = (self.centerPoint[0], self.cameraAdvancedPos[1], self.centerPoint[2])
        if geo2.Vec3Distance(avatarPosRelativeToCamera, self.cameraAdvancedPos) < cameras.AVATAR_MIN_DISPLAY_DISTANCE:
            self.model.display = False
        else:
            self.model.display = True
        self.avatarHasMoved = geo2.Vec3Distance(self.model.translation, self.lastAvatarPosition) > const.FLOAT_TOLERANCE
        self.lastAvatarPosition = self.model.translation



    def ProcessCameraUpdate(self, camera, now, frameTime):
        self.camera = camera
        self.frameTime = frameTime
        self.AcquireGameworldObjects()
        if self.entity is None:
            return 
        self.CalcCameraPosition()
        if abs(self.camera.mouseYawDelta) != 0:
            self.lastCameraMouseYawDelta = self.GetCameraMouseYawDelta()
            self.lastCameraZoomData = None
        if abs(self.camera.mousePitchDelta) != 0:
            self.lastCameraMousePitchDelta = self.camera.mousePitchDelta
            self.lastCameraZoomData = None
        if self.lastCameraZoomData and self.avatarHasMoved:
            self.lastCameraZoomData = None
        lerpingToAPosition = self.desiredPoi is not None
        if camera.wantToToggleZoom:
            if not self.exitingCollision and not lerpingToAPosition:
                self.CheckCameraCanToggleZoom()
                self.lastCameraZoomData = util.KeyVal(poi=self.camera.poi, zoom=self.camera.zoom)
        else:
            self.camera.wantToToggleZoom = False
        if self.desiredPoi is None:
            newPoi = self.CalcCorrectCameraPoi(self.camera.GetYaw(), self.camera.GetPitch(), self.camera.zoom)
            self.camera.SetPointOfInterest(newPoi)
            if self.gameWorld is not None:
                self.AvoidCollision(self.cameraAdvancedPos)
            else:
                self._LoadGameWorld()
        else:
            self.LerpToDesiredPosAndPoi()
            self.desiredPosAndPoiTransitionSeconds += self.frameTime



exports = util.AutoExports('cameras', locals())

