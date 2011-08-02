import geo2
import cameras
import GameWorld
CAMERA_COLLISION_SWEEP_SPHERE_RADIUS = 0.1
CAMERA_COLLISION_SWEEP_COUNT = 5
CAMERA_COLLISION_SWEEP_LOOK_AHEAD = 0.5
CAMERA_CUSHION_MAX = 1.25
CAMERA_CUSHION_MIN = 1.025
CAMERA_AVERAGE_VELOCITY_FRAMES = 5
CAMERA_FALLBACK_RATE = 1.5
CAMERA_FALLBACK_TIME = 0.0001 * const.SEC
CAMERA_COLLISION_OCCLUSION_FARTHEST_TO_USE = 3
CAMERA_COLLISION_OCCLUSION_CHECKS = 10
import random
CAMERA_COLLISION_OCCLUSION_OFFSETS = []
for i in xrange(CAMERA_COLLISION_OCCLUSION_CHECKS):
    CAMERA_COLLISION_OCCLUSION_OFFSETS.append((random.random() - 0.5, random.random() - 0.5))


class CameraCollisionBehavior(cameras.CameraBehavior):
    __guid__ = 'cameras.CameraCollisionBehavior'

    def __init__(self):
        self.gameWorldClient = sm.GetService('gameWorldClient')
        self.pastPositions = None
        self.onFrame = 0
        self.lastCameraDistChange = 0.0
        self.camera = None



    def ProcessCameraUpdate(self, camera, now, frameTime):
        if not session.worldspaceid:
            return 
        self.camera = camera
        self.camera.distance = self.camera.zoom
        yaw = self.camera.GetYaw()
        pitch = self.camera.GetPitch()
        (velPOI, velYaw, velPitch,) = self._UpdateVelocities(self.camera.GetBasePointOfInterest(), yaw, pitch, now)
        maxDist = self._CalcMaxDistance(self.camera.GetBasePointOfInterest(), yaw, pitch, velPOI, velYaw, velPitch)
        self.camera.distance = self._DetermineDistanceToUse(maxDist, now, frameTime)



    def _UpdateVelocities(self, poi, yaw, pitch, curTime):
        if self.pastPositions is None:
            self.pastPositions = [(curTime,
              poi,
              yaw,
              pitch)] * CAMERA_AVERAGE_VELOCITY_FRAMES
            self.onFrame = 0
        curFrame = self.pastPositions[self.onFrame]
        if curFrame[0] == curTime:
            velPOI = (0, 0, 0)
            velYaw = 0
            velPitch = 0
        else:
            timeDelta = float(curTime - curFrame[0]) / const.SEC
            velPOI = geo2.Vec3Scale(geo2.Vec3Subtract(poi, curFrame[1]), 1.0 / timeDelta)
            velYaw = (yaw - curFrame[2]) / timeDelta
            velPitch = (pitch - curFrame[3]) / timeDelta
        self.pastPositions[self.onFrame] = (curTime,
         poi,
         yaw,
         pitch)
        self.onFrame += 1
        if self.onFrame >= CAMERA_AVERAGE_VELOCITY_FRAMES:
            self.onFrame = 0
        return (velPOI, velYaw, velPitch)



    def _DetermineDistanceToUse(self, maxDist, time, frameTime):
        dist = self.camera.distance
        if self.camera.prevCameraDist is None:
            self.camera.prevCameraDist = maxDist / CAMERA_CUSHION_MAX
        if dist > maxDist / CAMERA_CUSHION_MIN:
            dist = maxDist / CAMERA_CUSHION_MAX
            self.lastCameraDistChange = time
        if dist > self.camera.prevCameraDist:
            if time > self.lastCameraDistChange + CAMERA_FALLBACK_TIME:
                distChange = dist - self.camera.prevCameraDist
                maxChange = CAMERA_FALLBACK_RATE * frameTime
                if distChange > maxChange:
                    distChange = maxChange
                dist = self.camera.prevCameraDist + distChange
            else:
                dist = self.camera.prevCameraDist
        self.camera.prevCameraDist = dist
        return dist



    def _DetermineAcceptableDistance(self, startPoint, endPoint):
        gameWorld = self.gameWorldClient.GetGameWorld(session.worldspaceid)
        if gameWorld is None:
            return geo2.Vec3Distance(endPoint, startPoint)
        forVec = geo2.Vec3Subtract(endPoint, startPoint)
        forVec = geo2.Vec3Normalize(forVec)
        upVec = (0.0, 1.0, 0.0)
        sideVec = geo2.Vec3Cross(forVec, upVec)
        sideVec = geo2.Vec3Normalize(sideVec)
        traces = []
        for (x, y,) in CAMERA_COLLISION_OCCLUSION_OFFSETS:
            offset = geo2.Vec3Add(geo2.Vec3Scale(sideVec, x), geo2.Vec3Scale(upVec, y))
            traces.append((geo2.Vec3Add(startPoint, offset), geo2.Vec3Add(endPoint, offset)))

        collisionGroups = 1 << GameWorld.GROUP_COLLIDABLE_NON_PUSHABLE
        distances = gameWorld.MultiLineTestLengths(traces, collisionGroups)
        maxDist = geo2.Vec3Distance(endPoint, startPoint)
        for (i, d,) in enumerate(distances):
            if d is None:
                distances[i] = maxDist

        distances.sort()
        maxDist = distances[(-CAMERA_COLLISION_OCCLUSION_FARTHEST_TO_USE)]
        epAsVec = geo2.Vector(endPoint[0], endPoint[1], endPoint[2])
        spAsVec = geo2.Vector(startPoint[0], startPoint[1], startPoint[2])
        hits = gameWorld.MultiHitLineTest(spAsVec, epAsVec, collisionGroups)
        useDist = maxDist
        if hits:
            useDist = 0
            for (i, (pos, normal,),) in enumerate(hits):
                curDist = geo2.Vec3Distance(pos, startPoint)
                if curDist > maxDist:
                    if i % 2 == 0:
                        useDist = maxDist
                    break
                if i % 2 == 0:
                    useDist = curDist
            else:
                if len(hits) % 2 == 0:
                    useDist = maxDist

        return useDist



    def _CalcMaxDistance(self, cameraPOI, yaw, pitch, vPOI, vYaw, vPitch):
        maxDist = self.camera.maxZoom * CAMERA_CUSHION_MAX
        if not self.gameWorldClient.HasGameWorld(session.worldspaceid):
            return maxDist
        if vYaw == 0 and vPitch == 0 and vPOI == (0, 0, 0):
            offset = self.camera.YawPitchDistToPoint(yaw, pitch, maxDist)
            cameraPos = geo2.Vec3Add(offset, cameraPOI)
            return self._DetermineAcceptableDistance(cameraPOI, cameraPos)
        gameWorld = self.gameWorldClient.GetGameWorld(session.worldspaceid)
        dist = maxDist
        distDec = maxDist / CAMERA_COLLISION_SWEEP_COUNT
        oneOverSweepCount = 1.0 / (CAMERA_COLLISION_SWEEP_COUNT - 1)
        poiInc = geo2.Vec3Scale(vPOI, CAMERA_COLLISION_SWEEP_LOOK_AHEAD)
        poiInc = geo2.Vec3Scale(poiInc, oneOverSweepCount)
        yawInc = CAMERA_COLLISION_SWEEP_LOOK_AHEAD * vYaw / (CAMERA_COLLISION_SWEEP_COUNT - 1)
        pitchInc = CAMERA_COLLISION_SWEEP_LOOK_AHEAD * vPitch / (CAMERA_COLLISION_SWEEP_COUNT - 1)
        curMaxDist = maxDist
        for i in xrange(CAMERA_COLLISION_SWEEP_COUNT):
            offset = self.camera.YawPitchDistToPoint(yaw, pitch, dist)
            cameraPos = geo2.Vec3Add(offset, cameraPOI)
            potentialMaxDist = maxDist / dist * self._DetermineAcceptableDistance(cameraPOI, cameraPos)
            if potentialMaxDist < curMaxDist:
                curMaxDist = potentialMaxDist
            dist -= distDec
            yaw += yawInc
            pitch += pitchInc
            if gameWorld is not None:
                nextPOI = geo2.Vec3Add(cameraPOI, poiInc)
                result = gameWorld.SweptSphere(cameraPOI, nextPOI, CAMERA_COLLISION_SWEEP_SPHERE_RADIUS)
                if result is None:
                    cameraPOI = nextPOI

        return curMaxDist




