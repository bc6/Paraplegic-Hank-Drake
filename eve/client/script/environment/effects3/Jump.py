import effects
import blue
import uthread
FX_SCALE_EFFECT_NONE = 0
FX_SCALE_EFFECT_SYMMETRICAL = 1
FX_SCALE_EFFECT_BOUNDING = 2
FX_USEBALLTRANSLATION = 1
FX_USEBALLROTATION = 2

def AudioWorker(emitter):
    blue.synchro.SleepWallclock(30000)



class JumpDriveIn(effects.ShipEffect):
    __guid__ = 'effects.JumpDriveIn'
    __gfx__ = 'res:\\Model\\Effect3\\JumpDrive_in.red'
    __scaling__ = FX_SCALE_EFFECT_SYMMETRICAL

    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)

    def Start(self, duration):
        shipID = self.ballIDs[0]
        michelle = sm.StartService('michelle')
        shipBall = michelle.GetBall(shipID)
        if shipBall is None:
            self.sfxMgr.LogError(self.__guid__, ' could not find a ball')
            return 
        self.PlayOldAnimations(self.gfx)



    def DelayedHide(self, shipBall, delay):
        blue.pyos.synchro.SleepSim(delay)
        if shipBall is not None and shipBall.model is not None:
            shipBall.model.display = False




class JumpDriveInBO(JumpDriveIn):
    __guid__ = 'effects.JumpDriveInBO'
    __gfx__ = 'res:\\Model\\Effect3\\JumpDriveBO_in.red'
    __scaling__ = FX_SCALE_EFFECT_SYMMETRICAL


class JumpDriveOut(JumpDriveIn):
    __guid__ = 'effects.JumpDriveOut'
    __gfx__ = 'res:\\Model\\Effect3\\JumpDrive_out.red'
    __scaling__ = FX_SCALE_EFFECT_SYMMETRICAL
    __positioning__ = FX_USEBALLTRANSLATION

    def Start(self, duration):
        shipID = self.ballIDs[0]
        michelle = sm.StartService('michelle')
        shipBall = michelle.GetBall(shipID)
        if eve.session.shipid == shipID:
            if hasattr(shipBall, 'KillBooster'):
                shipBall.KillBooster()
        self.PlayOldAnimations(self.gfx)
        uthread.new(self.DelayedHide, shipBall, 180)




class JumpDriveOutBO(JumpDriveOut):
    __guid__ = 'effects.JumpDriveOutBO'
    __gfx__ = 'res:\\Model\\Effect3\\JumpDriveBO_out.red'
    __scaling__ = FX_SCALE_EFFECT_SYMMETRICAL
    __positioning__ = FX_USEBALLTRANSLATION


class JumpIn(JumpDriveIn):
    __guid__ = 'effects.JumpIn'
    __gfx__ = 'res:/Model/Effect3/warpEntry.red'

    def Start(self, duration):
        scaling = self.gfxModel.scaling
        self.gfxModel.scaling = (scaling[0] * 0.005, scaling[1] * 0.005, scaling[2] * 0.005)
        JumpDriveIn.Start(self, duration)




class JumpOut(effects.ShipEffect):
    __guid__ = 'effects.JumpOut'
    __gfx__ = 'res:\\Model\\Effect3\\Jump_out.red'
    __scaling__ = FX_SCALE_EFFECT_SYMMETRICAL

    def __init__(self, trigger):
        self.ballIDs = [trigger.shipID, trigger.targetID]
        self.gfx = None
        self.gfxModel = None



    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)

    def Start(self, duration):
        shipID = self.ballIDs[0]
        michelle = sm.StartService('michelle')
        shipBall = michelle.GetBall(shipID)
        uthread.new(self.DelayedHide, shipBall)
        targetID = self.ballIDs[1]
        targetBall = michelle.GetBall(targetID)
        gateCurves = []
        if eve.session.shipid == shipID:
            if hasattr(shipBall, 'KillBooster'):
                shipBall.KillBooster()
        if hasattr(self.gfx, 'scaling'):
            radius = shipBall.radius
            self.gfx.scaling = (radius, radius, radius)
        listener = None
        for obs in self.gfx.observers:
            if obs.observer.name.startswith('effect_'):
                listener = obs.observer

        uthread.new(AudioWorker, listener)
        for curveSet in targetBall.model.curveSets:
            if curveSet.name == 'GateActivation':
                for curve in curveSet.curves:
                    if curve.name == 'audioEvents':
                        curve.eventListener = listener


        self.PlayNamedAnimations(targetBall.model, 'GateActivation')



    def DelayedHide(self, shipBall):
        blue.pyos.synchro.SleepSim(880)
        FxSequencer = sm.StartService('FxSequencer')
        FxSequencer.OnSpecialFX(shipBall.id, None, None, None, None, None, 'effects.Uncloak', 0, 0, 0)
        if shipBall is not None and shipBall.model is not None:
            shipBall.model.display = False




class JumpOutWormhole(JumpDriveIn):
    __guid__ = 'effects.JumpOutWormhole'
    __gfx__ = 'res:\\Model\\Effect3\\WormJump.red'

    def __init__(self, trigger):
        self.ballIDs = [trigger.shipID, trigger.targetID]
        self.gfx = None
        self.gfxModel = None



    def Start(self, duration):
        shipID = self.ballIDs[0]
        michelle = sm.StartService('michelle')
        shipBall = michelle.GetBall(shipID)
        if getattr(shipBall, 'model', None) is not None:
            FxSequencer = sm.StartService('FxSequencer')
            FxSequencer.OnSpecialFX(shipID, None, None, None, None, None, 'effects.CloakRegardless', 0, 1, 0, -1, None)
        uthread.new(self.DelayedHide, shipBall, 2000)
        wormholeID = self.ballIDs[1]
        wormholeBall = michelle.GetBall(wormholeID)
        if eve.session.shipid == shipID:
            if hasattr(shipBall, 'KillBooster'):
                shipBall.KillBooster()
        if hasattr(self.gfx, 'scaling'):
            radius = shipBall.radius
            self.gfx.scaling = (radius, radius, radius)
        self.PlayNamedAnimations(wormholeBall.model, 'Activate')
        wormholeBall.PlaySound('worldobject_wormhole_jump_play')




class GateActivity(effects.GenericEffect):
    __guid__ = 'effects.GateActivity'
    __gfx__ = None
    __scaling__ = FX_SCALE_EFFECT_NONE

    def __init__(self, trigger):
        self.ballIDs = [trigger.shipID]
        self.gfx = None
        self.gfxModel = None



    def Start(self, duration):
        gateID = self.ballIDs[0]
        michelle = sm.StartService('michelle')
        gateBall = michelle.GetBall(gateID)
        if gateBall is None:
            self.sfxMgr.LogError('GateActivity could not find a gate ball')
            return 
        if gateBall.model is None:
            self.sfxMgr.LogError('GateActivity could not find a gate ball')
            return 
        for obs in gateBall.model.observers:
            if obs.observer.name.startswith('jumpgate'):
                obs.observer.SendEvent(u'worldobject_jumpgate_jump_play')

        self.PlayNamedAnimations(gateBall.model, 'GateActivation')




class WormholeActivity(effects.GenericEffect):
    __guid__ = 'effects.WormholeActivity'
    __gfx__ = None
    __scaling__ = FX_SCALE_EFFECT_NONE

    def __init__(self, trigger):
        self.ballIDs = [trigger.shipID]
        self.gfx = None
        self.gfxModel = None



    def Start(self, duration):
        wormholeID = self.ballIDs[0]
        michelle = sm.StartService('michelle')
        wormholeBall = michelle.GetBall(wormholeID)
        if wormholeBall is None:
            self.sfxMgr.LogError('WormholeActivity could not find a wormhole ball')
            return 
        if wormholeBall.model is None:
            self.sfxMgr.LogError('WormholeActivity could not find a wormhole ball')
            return 
        self.PlayNamedAnimations(wormholeBall.model, 'Activate')
        wormholeBall.PlaySound('worldobject_wormhole_jump_play')




