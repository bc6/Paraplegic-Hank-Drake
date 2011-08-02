import effects
FX_SCALE_EFFECT_SYMMETRICAL = 1
FX_USEBALLTRANSLATION = 1
FX_SCALE_EFFECT_NONE = 0

class AnchoringEffect(effects.GenericEffect):
    __guid__ = None
    __gfx__ = None

    def Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    Key = staticmethod(Key)

    def __init__(self, trigger):
        if trigger.moduleID is not None and trigger.moduleID != trigger.shipID:
            self.ballIDs = [trigger.moduleID]
        else:
            self.ballIDs = [trigger.shipID]
        self.gfx = None



    def SetState(self, stateName):
        ballID = self.ballIDs[0]
        ball = sm.GetService('michelle').GetBall(ballID)
        if ball is None:
            return 
        if ball:
            if hasattr(ball, 'SetColor'):
                ball.SetColor(stateName)



    def SetDisplayOfAnchorableWarpDisruptor(self, state):
        ballID = self.ballIDs[0]
        ball = sm.GetService('michelle').GetBall(ballID)
        if ball is None:
            return 
        if hasattr(ball, 'cloud'):
            if ball.cloud:
                ball.cloud.display = state
        if hasattr(ball, 'Shieldip'):
            if ball.Shieldip:
                ball.Shieldip.display = state




class AnchorDrop(AnchoringEffect):
    __guid__ = 'effects.AnchorDrop'

    def Start(self, duration):
        ballID = self.ballIDs[0]
        ball = sm.GetService('michelle').GetBall(ballID)
        if ball is None:
            return 
        if hasattr(ball, 'SetBuiltStructureGraphics'):
            sm.GetService('FxSequencer').LogInfo('AnchorDrop: calling SetBuiltStructureGraphics ')
            ball.SetBuiltStructureGraphics(1)
        else:
            self.SetState('yellow')
            AnchoringEffect.Start(self, duration)



    def Stop(self):
        ballID = self.ballIDs[0]
        ball = sm.GetService('michelle').GetBall(ballID)
        if ball is None:
            return 
        if not hasattr(ball, 'SetBuiltStructureGraphics'):
            self.SetState('red')
            self.SetDisplayOfAnchorableWarpDisruptor(1)
            AnchoringEffect.Stop(self)




class AnchorLift(AnchoringEffect):
    __guid__ = 'effects.AnchorLift'

    def Start(self, duration):
        ballID = self.ballIDs[0]
        ball = sm.GetService('michelle').GetBall(ballID)
        if ball is None:
            return 
        if hasattr(ball, 'SetCapsuleGraphics'):
            sm.GetService('FxSequencer').LogInfo('AnchorDrop: calling SetCapsuleGraphics ')
            ball.SetCapsuleGraphics(1)
        else:
            self.SetState('yellow')
            AnchoringEffect.Start(self, duration)



    def Stop(self):
        ballID = self.ballIDs[0]
        ball = sm.GetService('michelle').GetBall(ballID)
        if ball is None:
            return 
        if not hasattr(ball, 'SetCapsuleGraphics'):
            self.SetState('green')
            AnchoringEffect.Stop(self)
        self.SetDisplayOfAnchorableWarpDisruptor(0)




