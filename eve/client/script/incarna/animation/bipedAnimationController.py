import animation
import geo2
import mathCommon
import random
import blue
import log
import math
WALK_GAIT = 0.0
HISTORY_LENGTH = 10
SLOPE_TOLERANCE = 0.15
STEPS_TOLERANCE = 0.5
IDLE_TIME_MIN = 5.0 * const.SEC
IDLE_TIME_MAX = 10.0 * const.SEC

class BipedAnimationController(animation.AnimationController):
    __guid__ = 'animation.BipedAnimationController'

    def Run(self):
        self.currentLOD = 0
        self.AddBehavior(animation.headTrackAnimationBehavior())
        self.positionHistory = []
        self.velocityHistory = []
        self.slopeType = const.INCARNA_FLAT
        self.updateTimeDelta = 0
        self.lastUpdateTime = blue.os.GetWallclockTime()
        self.random = random.Random()
        self.random.seed()
        self.timeForNextIdleTrigger = blue.os.GetWallclockTime() + self._GetNextIdleTriggerOffset()



    def _GetNextIdleTriggerOffset(self):
        return self.random.random() * (IDLE_TIME_MAX - IDLE_TIME_MIN) + IDLE_TIME_MIN



    def _UpdateHook(self):
        updateTime = blue.os.GetWallclockTime()
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
        positionComponent = self.entityRef.GetComponent('position')
        self.entPos = positionComponent.position
        self.entRot = positionComponent.rotation
        movementComponent = self.entityRef.GetComponent('movement')
        self.entVel = movementComponent.physics.velocity
        if len(self.positionHistory) > 0:
            displacement = (self.entPos[0] - self.positionHistory[0][0], self.entPos[1] - self.positionHistory[0][1], self.entPos[2] - self.positionHistory[0][2])
            if self.updateTimeDelta == 0:
                scaledDelta = 0
            else:
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
        updateTime = blue.os.GetWallclockTime()
        if updateTime >= self.timeForNextIdleTrigger:
            self.timeForNextIdleTrigger = updateTime + self._GetNextIdleTriggerOffset()
            self.SetControlParameter('IdleIndex', self.random.random())
            self.SetControlParameter('TriggerIdle', 1.0)
        else:
            self.SetControlParameter('TriggerIdle', 0.0)



    def UpdateMovement(self):
        debug = sm.GetService('debugRenderClient')
        yaw = geo2.QuaternionRotationGetYawPitchRoll(self.entityRef.position.rotation)[0]
        velYaw = mathCommon.GetYawAngleFromDirectionVector(self.entVel)
        angle = mathCommon.GetLesserAngleBetweenYaws(yaw, velYaw)
        headingToApply = self.entityRef.movement.physics.velocity
        speed = geo2.Vec3Length((headingToApply[0], 0.0, headingToApply[2]))
        self.SetControlParameter('Speed', speed)
        moveState = self.entityRef.GetComponent('movement').moveState
        self.SetControlParameter('Moving', int(moveState.GetStaticStateIndex() > 0))
        immed = moveState.GetImmediateRotation()
        if immed != 0.0:
            self.SetControlParameter('TurnAngle', immed / math.pi)
        else:
            self.SetControlParameter('TurnAngle', 0.0)




