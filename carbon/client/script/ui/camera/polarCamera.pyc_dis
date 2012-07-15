#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/camera/polarCamera.py
import blue
import math
import geo2
import base
import util
import trinity
import cameras
import mathUtil
import GameWorld
import mathCommon

class PolarCamera(cameras.BasicCamera):
    __guid__ = 'cameras.PolarCamera'

    def __init__(self):
        cameras.BasicCamera.__init__(self)
        self.gameWorldClient = sm.GetService('gameWorldClient')
        self.poi = (0, 0, 0)
        self.poiModifier = (0, 0, 0)
        self.rotationSpeed = 0.0
        self.minZoom = 0.0
        self.maxZoom = 4.1
        self.minPitch = 0.05
        self.maxPitch = math.pi - 0.05
        self.minRot = -math.pi
        self.maxRot = math.pi
        self.zoom = 0.75
        self.distance = self.zoom
        self.pitch = math.pi / 2
        self.yaw = math.pi / 2
        self.prevCameraDist = self.zoom

    def PerformPick(self, x, y, ignoreEntID = -1):
        startPoint, endPoint = self.GetRay(x, y)
        if not session.worldspaceid:
            return None
        else:
            gameWorld = self.gameWorldClient.GetGameWorld(session.worldspaceid)
            if gameWorld:
                collisionGroups = 1 << GameWorld.GROUP_AVATAR | 1 << GameWorld.GROUP_COLLIDABLE_NON_PUSHABLE
                p = gameWorld.LineTestEntId(startPoint, endPoint, ignoreEntID, collisionGroups)
                return p
            return None

    def GetRotationAsYaw(self):
        return -self.yaw - math.pi / 2.0

    def GetBasePointOfInterest(self):
        return self.poi

    def GetPointOfInterest(self):
        return geo2.Vec3Add(self.poi, self.poiModifier)

    def SetPointOfInterest(self, poi):
        self.poi = poi

    def AdjustPitch(self, delta):
        self.SetPitch(self.pitch + delta)

    def SetPitch(self, value):
        self.pitch = max(min(value, self.maxPitch), self.minPitch)

    def GetPitch(self):
        return self.pitch

    def SetPosition(self, position):
        yaw, pitch, dist = self.PointToYawPitchDist(position)
        self.SetYaw(yaw)
        self.SetPitch(pitch)
        self.SetZoom(dist)

    def SetYawPitchDist(self, yaw, pitch, dist):
        self.SetYaw(yaw)
        self.SetPitch(pitch)
        self.SetZoom(dist)

    def _AssembleViewMatrix(self, cameraPOI, yaw, pitch, dist):
        camera_pitch = math.pi / 2.0 - pitch
        camera_yaw = math.pi / 2.0 - yaw
        camera_roll = 0
        camera_offset = self.YawPitchDistToPoint(yaw, pitch, dist)
        camera_location = geo2.Vec3Add(camera_offset, cameraPOI)
        matrix = util.ConvertTriToTupleMatrix(self.CreateViewMatrix(camera_location, (camera_yaw, camera_pitch, camera_roll)))
        return (matrix, camera_location)

    def AssembleViewMatrix(self, cameraPOI, yaw, pitch, dist, setInternals = False, instanceID = None):
        matrix, camera_location = self._AssembleViewMatrix(cameraPOI, yaw, pitch, dist)
        self.cameraPosition = camera_location
        if setInternals:
            self.poi = cameraPOI
            self.SetYaw(yaw)
            self.SetPitch(pitch)
        self.viewMatrix.transform = matrix

    def AssembleBaseViewMatrix(self, cameraPOI, yaw, pitch, dist):
        matrix, trash = self._AssembleViewMatrix(cameraPOI, yaw, pitch, dist)
        self.baseViewMatrix.transform = matrix

    def CreateViewMatrix(self, location, rotation):
        cameraTranslation = trinity.TriMatrix()
        cameraRotation = trinity.TriMatrix()
        x, y, z = location
        cameraTranslation.Translation(x, y, z)
        cameraRotation.RotationYawPitchRoll(rotation[0], rotation[1], rotation[2])
        cameraFinal = cameraRotation
        cameraFinal.Multiply(cameraTranslation)
        cameraFinal.Inverse()
        return cameraFinal

    def PointToYawPitchDist(self, pos):
        upVector = (0, 1, 0)
        if trinity.IsRightHanded():
            rotMatrix = geo2.MatrixLookAtRH(pos, self.poi, upVector)
        else:
            rotMatrix = geo2.MatrixLookAtLH(pos, self.poi, upVector)
        rotMatrix = geo2.MatrixTranspose(rotMatrix)
        quat = geo2.QuaternionRotationMatrix(rotMatrix)
        yaw, pitch, roll = geo2.QuaternionRotationGetYawPitchRoll(quat)
        yaw = math.pi / 2 - yaw
        pitch = math.pi / 2 - pitch
        return (yaw, pitch, geo2.Vec3Distance(pos, self.poi))

    def YawPitchDistToPoint(self, yaw, pitch, dist):
        if trinity.IsRightHanded():
            position = (dist * math.sin(pitch) * math.cos(yaw), -dist * math.cos(pitch), dist * math.sin(pitch) * math.sin(yaw))
        else:
            position = (-dist * math.sin(pitch) * math.cos(yaw), dist * math.cos(pitch), -dist * math.sin(pitch) * math.sin(yaw))
        return position

    def SetYaw(self, value, ignoreUpdate = True):
        self.yaw = value
        if self.yaw < self.minRot:
            self.yaw += math.pi * 2.0
        elif self.yaw > self.maxRot:
            self.yaw -= math.pi * 2.0

    def GetYaw(self):
        return self.yaw

    def AdjustYaw(self, delta, maxRotate = None, ignoreUpdate = True):
        if maxRotate:
            if delta > maxRotate:
                delta = maxRotate
            if delta < -maxRotate:
                delta = -maxRotate
        self.SetYaw(self.yaw + delta, ignoreUpdate=ignoreUpdate)

    def AdjustZoom(self, delta):
        if delta < 0:
            self.zoom = self.prevCameraDist
        self.zoom += delta
        if self.zoom < self.minZoom:
            self.zoom = self.minZoom
        self.zoom = min(self.zoom, self.maxZoom)
        self.prevCameraDist = self.zoom

    def SetZoom(self, zoom):
        self.prevCameraDist = self.zoom = zoom

    def VerifyMaxZoom(self):
        raise NotImplementedError('VerifyMaxZoom must be implemented on derived camera classes')

    def SmoothMove(self, targetPosition, targetRotation, targetTilt, targetDist, durationMS, callbackOnEnd = None):
        sPos, sRot, sTilt, sDist = (self.GetPointOfInterest(),
         self.yaw,
         self.pitch,
         self.zoom)
        ePos, eRot, eTilt, eDist = (targetPosition,
         targetRotation,
         targetTilt,
         targetDist)
        eRot = sRot + mathCommon.GetLesserAngleBetweenYaws(sRot, eRot)
        self._smoothMoveTimer = base.AutoTimer(50, self.UpdateSmoothMove, sPos, sRot, sTilt, sDist, ePos, eRot, eTilt, eDist, blue.os.GetWallclockTime(), float(durationMS), callbackOnEnd)

    def UpdateSmoothMove(self, sPos, sRot, sTilt, sDist, ePos, eRot, eTilt, eDist, startTime, durationMS, callbackOnEnd):
        ndt = blue.os.TimeDiffInMs(startTime, blue.os.GetWallclockTime()) / durationMS
        ndt = max(0.0, min(1.0, ndt))
        self.AssembleViewMatrix((mathUtil.Lerp(sPos[0], ePos[0], ndt), mathUtil.Lerp(sPos[1], ePos[1], ndt), mathUtil.Lerp(sPos[2], ePos[2], ndt)), mathUtil.Lerp(sRot, eRot, ndt), mathUtil.Lerp(sTilt, eTilt, ndt), mathUtil.Lerp(sDist, eDist, ndt), True)
        if ndt >= 1.0:
            self._smoothMoveTimer = None
            self.zoom = eDist
            if callbackOnEnd:
                callbackOnEnd()

    def Update(self):
        now = blue.os.GetWallclockTime()
        frameTime = float(now - self.lastUpdateTime) / const.SEC
        self.poiModifier = (0, 0, 0)
        for priority, behavior in self.cameraBehaviors:
            behavior.ProcessCameraUpdate(self, now, frameTime)

        self.lastUpdateTime = now
        if abs(self.rotationSpeed) > 0:
            self.AdjustYaw(self.rotationSpeed * frameTime)
        self.AssembleViewMatrix(self.GetPointOfInterest(), self.yaw, self.pitch, self.distance)
        self.AssembleBaseViewMatrix(self.GetBasePointOfInterest(), self.yaw, self.pitch, self.distance)

    def SetRotationSpeed(self, rotationSpeed):
        self.rotationSpeed = rotationSpeed


exports = util.AutoExports('cameras', globals())