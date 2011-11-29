import animation
import cameraUtils
import GameWorld
import math
import geo2
import util
import blue
import log
ONE_EIGHTY_ANIM_TURN_ANGLE = 0.8
MIN_ACCELERATED_TURN_ANGLE = 0.05
ACCELERATED_TURN_MULTIPLIER = 2
MINIMUM_MOVE_SPEED = 0.2

class PlayerAnimationController(animation.BipedAnimationController):
    __guid__ = 'animation.PlayerAnimationController'

    def Run(self):
        animation.BipedAnimationController.Run(self)
        self.flyMode = False
        self.cameraBoundRotation = True
        self.renderDebugControlParameters = False
        self.leftButtonDown = False
        self.rightButtonDown = False
        self.previousMoving = 0
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
        self.ProcessNewMovement()



    def ProcessNewMovement(self):
        moveState = self.entityRef.GetComponent('movement').moveState
        headingToApply = self.entityRef.movement.physics.velocity
        deltaTurnAngle = moveState.GetDeltaYaw()
        speed = geo2.Vec3Length((headingToApply[0], 0.0, headingToApply[2]))
        self.SetControlParameter('Speed', speed)
        maxSpeed = moveState.GetMaxSpeed()
        self.SetControlParameter('nominalSpeed', maxSpeed)
        modifier = maxSpeed
        if modifier > 0:
            modifier = speed / maxSpeed
        modifier = min(max(modifier, 0.8), 1.2)
        self.SetControlParameter('speedMod', modifier)
        moving = moveState.GetStaticStateIndex() > 0
        self.SetControlParameter('Moving', moving)
        immed = moveState.GetImmediateRotation() / math.pi
        applied = moveState.GetImmediateRotationApplied() / math.pi
        if applied != 0.0 and applied != immed:
            self.SetControlParameter('immediateTurn', immed)
        else:
            self.SetControlParameter('immediateTurn', 0)
        if moving and not self.previousMoving:
            self.SetControlParameter('immediateTurnNoReset', immed)
        if moving:
            self.SetControlParameter('TurnAngle', deltaTurnAngle / math.pi)
        else:
            self.SetControlParameter('TurnAngle', 0)
        self.previousMoving = moving
        if self.renderDebugControlParameters:
            self.RenderDebugControlParameters(speed, deltaTurnAngle / math.pi, immed, applied)



    def ToggleDebugRenderControlParameters(self):
        self.renderDebugControlParameters = not self.renderDebugControlParameters



    def RenderDebugControlParameters(self, speed, turnAngle, immed, applied):
        debugRender = sm.GetService('debugRenderClient')
        if not debugRender.GetDebugRendering():
            debugRender.SetDebugRendering(True)
        text = 'Speed ' + str(speed) + '\n' + 'TurnAngle: ' + str(turnAngle) + '\n' + 'immed ' + str(immed) + '\n' + 'applied: ' + str(applied)
        position = self.entPos
        position = (position[0] + 0.5, position[1] + self.entityRef.movement.characterController.height, position[2])
        debugRender.RenderText(position, text, color=4294901760L, time=0, fade=False)



exports = util.AutoExports('animation', locals())

