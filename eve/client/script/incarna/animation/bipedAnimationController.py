import animation
import geo2
import mathCommon
import random
import blue
import log
WALK_GAIT = 0.0
HISTORY_LENGTH = 10
SLOPE_TOLERANCE = 0.15
STEPS_TOLERANCE = 0.5

class BipedAnimationController(animation.AnimationController):
    __guid__ = 'animation.BipedAnimationController'

    def Run(self):
        self.currentLOD = 0
        self.AddBehavior(animation.headTrackAnimationBehavior())
        self.positionHistory = []
        self.velocityHistory = []
        self.slopeType = const.INCARNA_FLAT
        self.updateTimeDelta = 0
        self.lastUpdateTime = blue.os.GetTime()



    def _UpdateHook(self):
        updateTime = blue.os.GetTime()
        self.updateTimeDelta = updateTime - self.lastUpdateTime
        self._UpdateEntityInfo()
        self.SetCorrectLOD()
        self.UpdateMovement()
        self.UpdateIdlePose()
        self.lastUpdateTime = updateTime



    def SetCorrectLOD(self):
        pass



    def InitIdleSpeed(self):
        idleSpeed = random.random()
        if idleSpeed < 0.5:
            idleSpeed += 0.5
        self.SetControlParameter('IdlePlaybackSpeed', idleSpeed)



    def UpdateEntitySlopeInfo(self):
        entriesInAverage = 0
        sumOfEntries = 0.0
        firstEntryFound = False
        for entry in reversed(self.velocityHistory):
            if abs(entry[1]) > const.FLOAT_TOLERANCE and not firstEntryFound:
                firstEntryFound = True
            if firstEntryFound:
                entriesInAverage += 1
                sumOfEntries += entry[1]

        self.slopeType = const.INCARNA_FLAT
        if entriesInAverage > 0:
            slopeAverage = sumOfEntries / entriesInAverage
            if slopeAverage > STEPS_TOLERANCE:
                self.slopeType = const.INCARNA_STEPS_UP
            elif slopeAverage > SLOPE_TOLERANCE:
                self.slopeType = const.INCARNA_SLOPE_UP
            elif slopeAverage < -STEPS_TOLERANCE:
                self.slopeType = const.INCARNA_STEPS_DOWN
            elif slopeAverage < -SLOPE_TOLERANCE:
                self.slopeType = const.INCARNA_SLOPE_DOWN



    def _UpdateEntityInfo(self):
        movementComponent = self.entityRef.GetComponent('movement')
        self.entPos = movementComponent.pos
        self.entRot = movementComponent.rot
        self.entVel = movementComponent.avatar.vel
        if len(self.positionHistory) > 0:
            displacement = (self.entPos[0] - self.positionHistory[0][0], self.entPos[1] - self.positionHistory[0][1], self.entPos[2] - self.positionHistory[0][2])
            scaledDelta = const.SEC / self.updateTimeDelta
            velocity = (displacement[0] * scaledDelta, displacement[1] * scaledDelta, displacement[2] * scaledDelta)
            self.velocityHistory.insert(0, velocity)
            if len(self.velocityHistory) > HISTORY_LENGTH:
                self.velocityHistory.pop()
        self.positionHistory.insert(0, self.entPos)
        if len(self.positionHistory) > HISTORY_LENGTH:
            self.positionHistory.pop()
        self.UpdateEntitySlopeInfo()



    def UpdateIdlePose(self):
        pass



    def UpdateMovement(self):
        debug = sm.GetService('debugRenderClient')
        yaw = geo2.QuaternionRotationGetYawPitchRoll(self.entityRef.movement.rot)[0]
        velYaw = mathCommon.GetYawAngleFromDirectionVector(self.entVel)
        angle = mathCommon.GetLesserAngleBetweenYaws(yaw, velYaw)
        newHeading = mathCommon.CreateDirectionVectorFromYawAngle(angle)
        newHeading = (newHeading[0], newHeading[1], newHeading[2])
        actualSpeed = geo2.Vec3Length(self.entVel)
        localHeading = newHeading if actualSpeed > 0.01 else (0.0, 0.0, 0.0)
        localHeading = (round(localHeading[0]), round(localHeading[1]), round(localHeading[2]))
        moving = geo2.Vec3Length(localHeading)
        debug.RenderText(self.entityRef.movement.pos, 'ActualSpeed: ' + str(actualSpeed) + '\n' + 'Moving: ' + str(moving), time=0, fade=False)
        self.SetControlParameter('Speed', round(moving))
        if moving:
            self.SetControlParameter('TurnAngle', 0.0)
        self.lastLocalHeading = localHeading




