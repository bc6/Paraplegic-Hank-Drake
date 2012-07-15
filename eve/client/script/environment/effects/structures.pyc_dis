#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/environment/effects/structures.py
import effects

class StructureOffline(effects.GenericEffect):
    __guid__ = 'effects.StructureOffline'

    def __init__(self, trigger, *args):
        if trigger.moduleID is not None and trigger.moduleID != trigger.shipID:
            self.ballIDs = [trigger.moduleID]
        else:
            self.ballIDs = [trigger.shipID]
        self.fxSequencer = sm.GetService('FxSequencer')
        self.gfx = None

    def Start(self, duration):
        ballID = self.ballIDs[0]
        ball = self.fxSequencer.GetBall(ballID)
        if ball is None:
            return
        if hasattr(ball, 'OfflineAnimation'):
            ball.OfflineAnimation(1)
        else:
            self.fxSequencer.LogWarn("error, can't run graphical effect StructureOffline on ", ball.id)


class StructureOnlined(effects.GenericEffect):
    __guid__ = 'effects.StructureOnlined'

    def __init__(self, trigger, *args):
        if trigger.moduleID is not None and trigger.moduleID != trigger.shipID:
            self.ballIDs = [trigger.moduleID]
        else:
            self.ballIDs = [trigger.shipID]
        self.fxSequencer = sm.GetService('FxSequencer')
        self.gfx = None

    def Start(self, duration):
        ballID = self.ballIDs[0]
        ball = self.fxSequencer.GetBall(ballID)
        if ball is None:
            return
        if hasattr(ball, 'OnlineAnimation'):
            ball.OnlineAnimation(1)
        else:
            self.fxSequencer.LogWarn("error, can't run graphical effect StructureOnlined on ", ball.id)


class StructureOnline(effects.GenericEffect):
    __guid__ = 'effects.StructureOnline'

    def __init__(self, trigger, *args):
        if trigger.moduleID is not None and trigger.moduleID != trigger.shipID:
            self.ballIDs = [trigger.moduleID]
        else:
            self.ballIDs = [trigger.shipID]
        self.fxSequencer = sm.GetService('FxSequencer')
        self.gfx = None

    def Start(self, duration):
        ballID = self.ballIDs[0]
        ball = self.fxSequencer.GetBall(ballID)
        if ball is None:
            return
        if hasattr(ball, 'OnlineAnimation'):
            ball.OnlineAnimation(1)
        else:
            self.fxSequencer.LogWarn("error, can't run graphical effect StructureOnline on ", ball.id)