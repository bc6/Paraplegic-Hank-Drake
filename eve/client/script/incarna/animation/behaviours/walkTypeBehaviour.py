import animation
import blue
WALK_FLAT = 0
WALK_DOWN = -1
WALK_UP = 1
WALK_END_DELAY = int(0.15 * const.SEC)

class WalkTypeBehaviour(animation.animationBehavior):
    __guid__ = 'animation.walkTypeBehaviour'

    def __init__(self):
        animation.animationBehavior.__init__(self)
        self.previousWalkVersion = WALK_FLAT
        self.returnToWalkFlatTime = 0.0



    def Update(self, controller):
        walkVersion = WALK_FLAT
        if controller.slopeType is const.INCARNA_STEPS_UP:
            walkVersion = WALK_UP
        elif controller.slopeType is const.INCARNA_STEPS_DOWN:
            walkVersion = WALK_DOWN
        if walkVersion is not WALK_FLAT:
            self.returnToWalkFlatTime = blue.os.GetWallclockTime() + WALK_END_DELAY
        if blue.os.GetWallclockTime() < self.returnToWalkFlatTime and walkVersion is WALK_FLAT:
            walkVersion = self.previousWalkVersion
        controller.SetControlParameter('Slope', walkVersion)
        self.previousWalkVersion = walkVersion



    def Reset(self):
        self.previousWalkVersion = WALK_FLAT
        self.returnToWalkFlatTime = 0.0




