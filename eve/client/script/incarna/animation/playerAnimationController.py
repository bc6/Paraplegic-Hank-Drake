import animation
import cameraUtils
import GameWorld
import math
import mathCommon
import geo2
import svc
import log
import util
import blue
MAXIMUM_HEAD_LOOK_ANGLE = 2.5
ONE_EIGHTY_ANIM_TURN_ANGLE = 0.8
MIN_ACCELERATED_TURN_ANGLE = 0.05
ACCELERATED_TURN_MULTIPLIER = 2
MAX_VEL_VS_MODEL_ANGLE_DIFFERENCE = math.pi / 2
AVATAR_COLLISION_RESTRICTION_ANGLE = math.pi / 5
STOP_DELAY = int(0.05 * const.SEC)

class PlayerAnimationController(animation.BipedAnimationController):
    __guid__ = 'animation.PlayerAnimationController'

    def Run(self):
        animation.BipedAnimationController.Run(self)
        self.walkSpeed = 2.0
        self.flyMode = False
        self.cameraBoundRotation = True
        self.renderDebugCollisionCapsules = False
        self.renderDebugControlParameters = False
        self.leftButtonDown = False
        self.rightButtonDown = False
        self.lastHeading = (0, 0, 0)
        self.lastSpeed = 0
        self.delayTimerEnd = 0
        self.delayTimerActive = False
        self.lastDesiredHeadingYaw = False
        self.ignoreTurnAngleUnmodified = False
        self.cameraClient = sm.GetService('cameraClient')
        self.aoClient = sm.GetService('actionObjectClientSvc')
        self.mouseInputService = sm.GetService('mouseInput')
        self.mouseInputService.RegisterCallback(const.INPUT_TYPE_MOUSEDOWN, self.OnMouseDown)
        self.mouseInputService.RegisterCallback(const.INPUT_TYPE_MOUSEUP, self.OnMouseUp)
        self.AddBehavior(animation.walkTypeBehaviour())



    def Stop(self, stream):
        self.mouseInputService.UnRegisterCallback(const.INPUT_TYPE_MOUSEDOWN, self.OnMouseDown)
        self.mouseInputService.UnRegisterCallback(const.INPUT_TYPE_MOUSEUP, self.OnMouseUp)



    def Reset(self):
        self.cameraBoundRotation = True
        self.leftButtonDown = False
        self.rightButtonDown = False



    def OnMouseDown(self, button, posX, posY, entityID):
        if button is const.INPUT_TYPE_LEFTCLICK:
            self.leftButtonDown = True
            if self.rightButtonDown:
                self.cameraBoundRotation = True
        if button is const.INPUT_TYPE_RIGHTCLICK:
            self.rightButtonDown = True
            if not self.leftButtonDown:
                self.cameraBoundRotation = False



    def OnMouseUp(self, button, posX, posY, entityID):
        if button is const.INPUT_TYPE_LEFTCLICK:
            self.leftButtonDown = False
            if self.rightButtonDown:
                self.cameraBoundRotation = False
        if button is const.INPUT_TYPE_RIGHTCLICK:
            self.rightButtonDown = False
            self.cameraBoundRotation = True



    def SetFlyMode(self, flyMode):
        self.flyMode = flyMode



    def _UpdateHook(self):
        animation.BipedAnimationController._UpdateHook(self)



    def UpdateMovement(self):
        self.ProcessNewMovement(self.entityRef.GetComponent('movement').avatar.localHeading)



    def UpdateIdlePose(self):
        pass



    def StartStopDelayTimer(self):
        self.delayTimerEnd = blue.os.GetTime() + STOP_DELAY
        self.delayTimerActive = True



    def StopStopDelayTimer(self):
        self.delayTimerEnd = 0
        self.delayTimerActive = False



    def CheckForStop(self, heading):
        returnValue = heading
        speed = geo2.Vec3Length(returnValue)
        if not self.delayTimerActive and speed < const.FLOAT_TOLERANCE and self.lastSpeed > 0:
            returnValue = self.lastHeading
            self.StartStopDelayTimer()
        if self.delayTimerActive and self.delayTimerEnd > blue.os.GetTime():
            if speed < const.FLOAT_TOLERANCE:
                returnValue = self.lastHeading
            else:
                self.StopStopDelayTimer()
        if self.delayTimerActive and self.delayTimerEnd <= blue.os.GetTime():
            self.ignoreTurnAngleUnmodified = False
            self.StopStopDelayTimer()
        return returnValue



    def ProcessNewMovement(self, heading):
        turnAngle = 0.0
        turnAngleUnmodified = 0.0
        headingToApply = self.CheckForStop(heading)
        speed = geo2.Vec3Length(headingToApply)
        isStarting = self.lastSpeed < const.FLOAT_TOLERANCE and speed > 0
        if isStarting and self.delayTimerActive is False:
            self.ignoreTurnAngleUnmodified = True
        isPathing = isinstance(self.entityRef.movement.avatar.GetActiveMoveMode(), GameWorld.PathToMode)
        if not isPathing:
            if speed > const.FLOAT_TOLERANCE:
                if self.aoClient.IsEntityUsingActionObject(self.entityRef.entityID):
                    if self.delayTimerActive is False:
                        self.aoClient.ExitActionObject(self.entityRef.entityID)
                    return 
                if self.cameraBoundRotation:
                    desiredHeadingYaw = cameraUtils.CalcDesiredPlayerHeading(headingToApply)
                    if abs(desiredHeadingYaw - self.lastDesiredHeadingYaw) > const.FLOAT_TOLERANCE:
                        self.ignoreTurnAngleUnModified = False
                    self.lastDesiredHeadingYaw = desiredHeadingYaw
                    turnAngle = cameraUtils.GetAngleFromEntityToYaw(self.entityRef, desiredHeadingYaw)
                    turnAngle = turnAngle / math.pi
                    turnAngleUnmodified = turnAngle
                    if abs(turnAngle) > MIN_ACCELERATED_TURN_ANGLE and abs(turnAngle) < ONE_EIGHTY_ANIM_TURN_ANGLE:
                        turnAngle = min(ONE_EIGHTY_ANIM_TURN_ANGLE, max(-ONE_EIGHTY_ANIM_TURN_ANGLE, turnAngle * ACCELERATED_TURN_MULTIPLIER))
                    if abs(turnAngle) < const.FLOAT_TOLERANCE:
                        turnAngle = 0.0
                else:
                    speed = max(0.0, headingToApply[2])
                if self.entityRef.movement.avatar.collisionForwards:
                    if abs(turnAngle) < animation.AVATAR_COLLISION_RESTRICTION_ANGLE:
                        if not self.CheckSpecialCollisionCases():
                            speed = 0.0
                self.SetControlParameter('TurnAngle', turnAngle)
                if self.ignoreTurnAngleUnmodified is False or isStarting:
                    self.SetControlParameter('TurnAngleUnmodified', turnAngleUnmodified)
        else:
            self.SetControlParameter('TurnAngle', turnAngle)
            self.SetControlParameter('TurnAngleUnmodified', turnAngleUnmodified)
        self.SetControlParameter('Speed', speed)
        self.lastHeading = headingToApply
        self.lastSpeed = speed
        if self.renderDebugCollisionCapsules:
            self.RenderDebugCollisionCapsules()
        if self.renderDebugControlParameters:
            self.RenderDebugControlParameters(speed, turnAngle)



    def CheckSpecialCollisionCases(self):
        modelYaw = geo2.QuaternionRotationGetYawPitchRoll(self.entityRef.paperdoll.doll.avatar.rotation)[0]
        velocityYaw = mathCommon.GetYawAngleFromDirectionVector(self.entityRef.movement.avatar.velOrientation)
        diff = abs(modelYaw - abs(velocityYaw))
        if diff > animation.MAX_VEL_VS_MODEL_ANGLE_DIFFERENCE:
            return True
        else:
            return False



    def ToggleDebugRenderCollisionCapsules(self):
        self.renderDebugCollisionCapsules = not self.renderDebugCollisionCapsules



    def ToggleDebugRenderControlParameters(self):
        self.renderDebugControlParameters = not self.renderDebugControlParameters



    def RenderDebugCollisionCapsules(self):
        playerPosition = (self.entityRef.movement.avatar.pos[0], self.entityRef.movement.avatar.pos[1] + self.entityRef.movement.avatar.height / 5, self.entityRef.movement.avatar.pos[2])
        velOrientation = self.entityRef.movement.avatar.velOrientation
        collisionDetectionFeelerLength = self.entityRef.movement.avatar.collisionDetectionFeelerLength
        rot = geo2.QuaternionRotationGetYawPitchRoll(self.entityRef.paperdoll.doll.avatar.rotation)
        avatarVector = mathCommon.CreateDirectionVectorFromYawAngle(rot[0])
        avatarFwd = geo2.Vec3Add(playerPosition, (val * collisionDetectionFeelerLength for val in avatarVector))
        fwrd = geo2.Vec3Add(playerPosition, (val * collisionDetectionFeelerLength for val in velOrientation))
        back = geo2.Vec3Add(playerPosition, (val * -collisionDetectionFeelerLength for val in velOrientation))
        leftVector = (velOrientation[2], velOrientation[1], -velOrientation[0])
        left = geo2.Vec3Add(playerPosition, (val * collisionDetectionFeelerLength for val in leftVector))
        rightVector = (-leftVector[0], -leftVector[1], -leftVector[2])
        right = geo2.Vec3Add(playerPosition, (val * collisionDetectionFeelerLength for val in rightVector))
        debugRender = sm.GetService('debugRenderClient')
        if not debugRender.GetDebugRendering():
            debugRender.SetDebugRendering(True)
        debugRender.RenderCapsule(playerPosition, avatarFwd, self.entityRef.movement.avatar.collisionDetectionCapsuleRadius, 4294967295L, 20)
        debugRender.RenderCapsule(playerPosition, fwrd, self.entityRef.movement.avatar.collisionDetectionCapsuleRadius, 4294967040L, 20)
        debugRender.RenderCapsule(playerPosition, back, self.entityRef.movement.avatar.collisionDetectionCapsuleRadius, 4294901760L, 20)
        debugRender.RenderCapsule(playerPosition, left, self.entityRef.movement.avatar.collisionDetectionCapsuleRadius, 4278255360L, 20)
        debugRender.RenderCapsule(playerPosition, right, self.entityRef.movement.avatar.collisionDetectionCapsuleRadius, 4278190335L, 20)



    def RenderDebugControlParameters(self, speed, turnAngle):
        debugRender = sm.GetService('debugRenderClient')
        if not debugRender.GetDebugRendering():
            debugRender.SetDebugRendering(True)
        text = 'Speed ' + str(speed) + '\n' + 'TurnAngle: ' + str(turnAngle)
        position = self.entPos
        position = (position[0], position[1] + self.entityRef.movement.avatar.height, position[2])
        debugRender.RenderText(position, text, color=4294901760L, time=0, fade=False)



exports = util.AutoExports('animation', locals())

