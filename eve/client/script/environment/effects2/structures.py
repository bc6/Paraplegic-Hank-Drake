import effects
FX_SCALE_EFFECT_SYMMETRICAL = 1
FX_USEBALLTRANSLATION = 1
FX_SCALE_EFFECT_NONE = 0

class StructureOffline(effects.GenericEffect):
    __guid__ = 'effects.StructureOffline'

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



    def Start(self, duration):
        ballID = self.ballIDs[0]
        ball = sm.GetService('michelle').GetBall(ballID)
        if ball is None:
            return 
        if hasattr(ball, 'OfflineAnimation'):
            ball.OfflineAnimation(1)
        else:
            sm.GetService('FxSequencer').LogWarn("error, can't run graphical effect StructureOffline on ", ball.id)




class StructureOnlined(effects.GenericEffect):
    __guid__ = 'effects.StructureOnlined'

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



    def Start(self, duration):
        ballID = self.ballIDs[0]
        ball = sm.GetService('michelle').GetBall(ballID)
        print '================ id',
        print ball
        if ball is None:
            return 
        if hasattr(ball, 'OnlineAnimation'):
            ball.OnlineAnimation(1)
        else:
            sm.GetService('FxSequencer').LogWarn("error, can't run graphical effect StructureOnlined on ", ball.id)




class StructureOnline(effects.GenericEffect):
    __guid__ = 'effects.StructureOnline'

    def __init__(self, trigger):
        if trigger.moduleID is not None and trigger.moduleID != trigger.shipID:
            self.ballIDs = [trigger.moduleID]
        else:
            self.ballIDs = [trigger.shipID]
        self.gfx = None



    def Start(self, duration):
        ballID = self.ballIDs[0]
        ball = sm.GetService('michelle').GetBall(ballID)
        if ball is None:
            return 
        if hasattr(ball, 'OnlineAnimation'):
            ball.OnlineAnimation(1)
        else:
            sm.GetService('FxSequencer').LogWarn("error, can't run graphical effect StructureOnline on ", ball.id)




