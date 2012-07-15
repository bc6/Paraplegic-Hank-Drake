#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/camera/characterOffsetBehavior.py
import geo2
import util
import math
import cameras
import trinity
import mathUtil
LERP_SPEED = 5
LERP_TIME = 0.5 * const.SEC
MIN_PLERP_TIME_LIMIT = 0.045
CHARACTER_OFFSET_FACTOR = 0.28
ZOOM_COLLISION_TOLERANCE = 0.01
OPTIMAL_SCREEN_ASPECT_RATIO = 1.7
AVATAR_MIN_DISPLAY_DISTANCE = 0.45
AVATAR_SHOULDER_HEIGHT = 1.55
NORMAL_COLLISION_SPHERE = 0.199
ZOOM_COLLISION_SPHERE = 0.209
MALE = True
FEMALE = False

class CharacterOffsetBehavior(cameras.CameraBehavior):
    __guid__ = 'cameras.CharacterOffsetBehavior'

    def __init__(self, charEntID):
        cameras.CameraBehavior.__init__(self)
        self.entity = None
        self.model = None
        self.colliding = False
        self.useLerp = False
        self.entityID = charEntID
        self.cameraOffsetModifier = 1.0
        self.desiredZoom = 0
        self.lerpTimeLeft = 0
        self.charGender = None
        self.desiredPoi = None
        self.lerpPoiCamStats = (0, 0, 0)
        self.lerpPoiAvatarStats = (0, 0, 0)
        self.lastCenterPoint = (0, 0, 0)

    def AdjustOffset(self, newOffsetModifier):
        if newOffsetModifier is not None:
            self.cameraOffsetModifier = newOffsetModifier

    def CalcCorrectCameraPoi(self, yaw, pitch, overrideZoom = None):
        zoom = overrideZoom
        if zoom is None:
            zoom = self.camera.userSelectedZoom
        zoomPerc = 1.0 - (zoom - self.camera.minZoom) / (self.camera.maxZoom - self.camera.minZoom)
        charOffsetFactor = cameras.CHARACTER_OFFSET_FACTOR * self.cameraOffsetModifier
        if zoom < self.camera.minZoom:
            zoomPerc = zoom / self.camera.minZoom
        charOffsetFactor *= zoomPerc
        screenAspectRatio = float(trinity.app.width) / float(trinity.app.height)
        if screenAspectRatio < cameras.OPTIMAL_SCREEN_ASPECT_RATIO:
            shorten = screenAspectRatio / cameras.OPTIMAL_SCREEN_ASPECT_RATIO
            charOffsetFactor *= shorten
        x = self.centerPoint[0]
        z = self.centerPoint[2]
        x0 = x + math.cos(yaw - math.pi / 2) * charOffsetFactor
        z0 = z + math.sin(yaw - math.pi / 2) * charOffsetFactor
        if self.charGender == FEMALE:
            interestYoffset = 0.1
            interestYoffsetWhenFar = -0.32
        else:
            interestYoffset = 0.2
            interestYoffsetWhenFar = -0.5
        verticalPitchOffset = -math.sin(max(0, pitch - math.pi / 2)) * 0.1
        interestYoffset = interestYoffset + interestYoffsetWhenFar * (1.0 - zoomPerc) + verticalPitchOffset
        shoulderOffsetPoint = (x0, self.centerPoint[1] + interestYoffset, z0)
        return shoulderOffsetPoint

    def AvoidCollision(self):
        criticalFailInfo = self.gameWorld.SweptSphere(self.centerPoint, self.cameraAdvancedPos, cameras.NORMAL_COLLISION_SPHERE)
        if criticalFailInfo:
            safeSpot = geo2.Vec3Add(criticalFailInfo[0], (val * cameras.NORMAL_COLLISION_SPHERE for val in criticalFailInfo[1]))
            if not self.colliding:
                self.colliding = True
                self.desiredPoi = None
            newZoom = geo2.Vec3Distance(self.camera.poi, safeSpot)
            self.camera.collisionZoom = self.camera.zoom = self.camera.desiredZoom = newZoom
        elif self.colliding:
            self.camera.desiredZoom = self.camera.userSelectedZoom
            self.camera.collisionZoom = self.camera.zoom
            self.colliding = False

    def CalcCamCurrAndAdvancedPosition(self):
        self.centerPoint = (self.entity.GetComponent('position').position[0], self.entity.GetComponent('position').position[1] + cameras.AVATAR_SHOULDER_HEIGHT, self.entity.GetComponent('position').position[2])
        cameraAdvancedPos = self.camera.YawPitchDistToPoint(self.camera.yaw, self.camera.pitch, self.camera.userSelectedZoom)
        advancedPoi = self.CalcCorrectCameraPoi(self.camera.yaw, self.camera.pitch)
        cameraAdvancedPos = geo2.Vec3Add(cameraAdvancedPos, advancedPoi)
        self.cameraAdvancedPos = cameraAdvancedPos

    def HandleZooming(self):
        if self.camera.zoomRequest is None:
            return
        if abs(self.camera.zoomRequest - self.camera.zoom) < const.FLOAT_TOLERANCE or abs(self.camera.zoomRequest - self.desiredZoom) < const.FLOAT_TOLERANCE:
            self.camera.zoomRequest = None
            return
        self.useLerp = False
        if self.desiredPoi is not None:
            self.camera.zoomRequest = self.desiredZoom + self.camera.lastScrollDelta
            if self.camera.zoomRequest > self.camera.maxZoom:
                self.camera.zoomRequest = self.camera.maxZoom
            elif self.camera.zoomRequest < self.camera.minZoom:
                self.camera.zoomRequest = self.camera.minZoom
            self.useLerp = True
        zoomingOut = False
        if self.camera.zoomRequest > self.camera.zoom:
            zoomingOut = True
        futurePoi = self.CalcCorrectCameraPoi(self.camera.yaw, self.camera.pitch, overrideZoom=self.camera.zoomRequest)
        cameraAdvancedPos = geo2.Vec3Add(futurePoi, self.camera.YawPitchDistToPoint(self.camera.yaw, self.camera.pitch, self.camera.zoomRequest))
        futurePoiCollision = self.gameWorld.SweptSphere(self.centerPoint, cameraAdvancedPos, cameras.ZOOM_COLLISION_SPHERE)
        collAtSource = self.gameWorld.SphereTest(self.centerPoint, cameras.ZOOM_COLLISION_SPHERE)
        vect = geo2.Vec3Normalize(geo2.Vec3Subtract(self.cameraAdvancedPos, self.centerPoint))
        cameraAdvancedPos = geo2.Vec3Add(self.centerPoint, (val * self.camera.zoomRequest for val in vect))
        currPosCollision = self.gameWorld.SweptSphere(self.centerPoint, cameraAdvancedPos, cameras.NORMAL_COLLISION_SPHERE)
        if futurePoiCollision and not currPosCollision and collAtSource:
            futurePoiCollision = None
        if not self.colliding:
            if futurePoiCollision is None:
                self.desiredPoi = self.CalcCorrectCameraPoi(self.camera.yaw, self.camera.pitch, overrideZoom=self.camera.zoomRequest)
                cameraAdvancedPos = geo2.Vec3Add(self.desiredPoi, self.camera.YawPitchDistToPoint(self.camera.yaw, self.camera.pitch, self.camera.zoomRequest))
                checkColl = self.gameWorld.SweptSphere(self.centerPoint, cameraAdvancedPos, cameras.ZOOM_COLLISION_SPHERE)
                if checkColl:
                    self.desiredPoi = None
                else:
                    self.desiredZoom = self.camera.zoomRequest
                    self.camera.userSelectedZoom = self.camera.zoomRequest
                    self.lerpPoiCamStats = (self.camera.yaw, self.camera.pitch, 0.0)
                    self.lerpPoiAvatarStats = self.entity.GetComponent('position').position
                    self.CalcCamCurrAndAdvancedPosition()
            else:
                safeSpot = geo2.Vec3Add(futurePoiCollision[0], (val * cameras.ZOOM_COLLISION_SPHERE for val in futurePoiCollision[1]))
                dist = max(self.camera.minZoom, geo2.Vec3Distance(self.centerPoint, safeSpot))
                dist = min(self.camera.maxZoom, dist)
                if abs(dist - self.camera.zoom) > ZOOM_COLLISION_TOLERANCE:
                    oldPoi = self.desiredPoi
                    self.desiredPoi = self.CalcCorrectCameraPoi(self.camera.yaw, self.camera.pitch, overrideZoom=dist)
                    cameraAdvancedPos = geo2.Vec3Add(self.desiredPoi, self.camera.YawPitchDistToPoint(self.camera.yaw, self.camera.pitch, dist))
                    checkColl = self.gameWorld.SweptSphere(self.centerPoint, cameraAdvancedPos, cameras.ZOOM_COLLISION_SPHERE)
                    if checkColl:
                        self.desiredPoi = oldPoi
                    elif zoomingOut and dist < self.camera.zoom:
                        self.desiredPoi = oldPoi
                    else:
                        self.CalcCamCurrAndAdvancedPosition()
                        self.desiredZoom = dist
                        self.camera.userSelectedZoom = dist
                        self.lerpPoiCamStats = (self.camera.yaw, self.camera.pitch, 0.0)
                        self.lerpPoiAvatarStats = self.entity.GetComponent('position').position
        elif futurePoiCollision is None:
            self.desiredZoom = self.camera.zoomRequest
            self.camera.userSelectedZoom = self.camera.zoomRequest
            self.desiredPoi = self.CalcCorrectCameraPoi(self.camera.yaw, self.camera.pitch, overrideZoom=self.camera.zoomRequest)
            self.lerpPoiCamStats = (self.camera.yaw, self.camera.pitch, 0.0)
            self.lerpPoiAvatarStats = self.entity.GetComponent('position').position
            self.CalcCamCurrAndAdvancedPosition()
        self.lerpTimeLeft = LERP_TIME
        self.startZoom = self.camera.zoom
        self.originalPoi = self.camera.poi
        self.camera.zoomRequest = None

    def HandlePointOfInterest(self):
        if self.desiredPoi is not None:
            camMoved = geo2.Vec3Distance(self.lerpPoiCamStats, (self.camera.yaw, self.camera.pitch, 0.0))
            avatarMoved = geo2.Vec3Distance(self.lerpPoiAvatarStats, self.entity.GetComponent('position').position)
            if camMoved > const.FLOAT_TOLERANCE or avatarMoved > const.FLOAT_TOLERANCE:
                self.desiredPoi = self.CalcCorrectCameraPoi(self.camera.yaw, self.camera.pitch)
                if avatarMoved > const.FLOAT_TOLERANCE:
                    vect = geo2.Vec3Normalize(geo2.Vec3Subtract(self.centerPoint, self.lastCenterPoint))
                    dist = geo2.Vec3Distance(self.lastCenterPoint, self.centerPoint)
                    self.camera.poi = geo2.Vec3Add(self.camera.poi, (val * dist for val in vect))
                self.lerpPoiCamStats = (self.camera.yaw, self.camera.pitch, 0.0)
                self.lerpPoiAvatarStats = self.entity.GetComponent('position').position
                self.useLerp = True
            if self.useLerp:
                newPoi = geo2.Vec3Lerp(self.camera.poi, self.desiredPoi, self.frameTime * LERP_SPEED)
                zoom = mathUtil.Lerp(self.camera.zoom, self.desiredZoom, self.frameTime * LERP_SPEED)
            else:
                newPoi = self.PlerpVec3(self.originalPoi, self.desiredPoi, self.lerpTimeLeft)
                zoom = self.Plerp(self.startZoom, self.desiredZoom, self.lerpTimeLeft)
            self.camera.zoom = self.camera.collisionZoom = self.camera.desiredZoom = zoom
            self.lerpTimeLeft -= self.frameTime * const.SEC
            if geo2.Vec3Distance(newPoi, self.desiredPoi) < const.FLOAT_TOLERANCE and abs(self.camera.zoom - self.desiredZoom) < const.FLOAT_TOLERANCE:
                self.desiredPoi = None
                self.camera.zoom = self.camera.collisionZoom = self.camera.desiredZoom = self.desiredZoom
        else:
            newPoi = self.CalcCorrectCameraPoi(self.camera.yaw, self.camera.pitch)
        self.camera.SetPointOfInterest(newPoi)

    def Plerp(self, start, end, timeLeft):
        doneSoFar = LERP_TIME - timeLeft
        percDone = doneSoFar / LERP_TIME
        if percDone > 1.0:
            return end
        percToEnd = math.sin(percDone * math.pi - math.pi / 2.0) / 2.0 + 0.5
        distance = (end - start) * percToEnd
        currDist = start + distance
        return currDist

    def PlerpVec3(self, start, end, timeLeft):
        doneSoFar = LERP_TIME - timeLeft
        percDone = doneSoFar / LERP_TIME
        if percDone > 1.0:
            return end
        percToEnd = math.sin(percDone * math.pi - math.pi / 2.0) / 2.0 + 0.5
        distance = geo2.Vec3Length(geo2.Vec3Subtract(end, start)) * percToEnd
        vector = geo2.Vec3Normalize(geo2.Vec3Subtract(end, start))
        currPoint = geo2.Vec3Add(start, (val * distance for val in vector))
        return currPoint

    def HandleModelVisibility(self):
        avatarPosRelativeToCamera = (self.centerPoint[0], self.camera.cameraPosition[1], self.centerPoint[2])
        if geo2.Vec3Distance(avatarPosRelativeToCamera, self.camera.cameraPosition) < cameras.AVATAR_MIN_DISPLAY_DISTANCE:
            self.model.display = False
        else:
            self.model.display = True

    def AcquireGameworldObjects(self):
        if self.gameWorld is None:
            self._LoadGameWorld()
            if self.gameWorld is None:
                raise RuntimeError('Problem retrieving the game world. ID:', session.worldspaceid)
        if self.entity is None:
            self.entity = self._GetEntity(self.entityID)
            if self.entity is None:
                raise RuntimeError("Problem retrieving the avatar's entity. cameras.CameraBehavior._GetEntity returned None for entityID", self.entityID)
        if self.model is None:
            self.model = self._GetEntityModel(self.entityID)
            if self.model is None:
                raise RuntimeError("Problem retrieving the avatar's model object. entityClient.FindEntityByID returned None for entityID", self.entityID)

    def Reset(self):
        self.model = None
        self.entity = None
        self.gameWorld = None
        self._LoadGameWorld()

    def ProcessCameraUpdate(self, camera, now, frameTime):
        self.camera = camera
        self.frameTime = frameTime
        self.AcquireGameworldObjects()
        if self.entity is None or session.worldspaceid is None or self.gameWorld is None:
            return
        if self.charGender is None:
            try:
                self.charGender = self.entity.GetComponent('info').gender
            except:
                sys.exc_clear()

        self.camera.CalcCameraDirection()
        self.CalcCamCurrAndAdvancedPosition()
        self.HandleModelVisibility()
        self.HandlePointOfInterest()
        self.HandleZooming()
        if self.gameWorld is not None:
            self.AvoidCollision()
        else:
            self._LoadGameWorld()
        self.lastCenterPoint = self.centerPoint


exports = util.AutoExports('cameras', locals())