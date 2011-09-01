import effects
import trinity
import blue
import uthread

class AccelerationGate(effects.GenericEffect):
    __guid__ = 'effects.WarpGateEffect'

    def __init__(self, trigger):
        effects.GenericEffect.__init__(self, trigger)
        self.ballIDs = [trigger.shipID, trigger.targetID]



    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)

    def _GetDuration():
        return 2


    _GetDuration = staticmethod(_GetDuration)

    def Start(self, duration):
        gateID = self.GetEffectShipID()
        targetID = self.GetEffectTargetID()
        gateBall = self.GetEffectShipBall()
        slimItem = sm.StartService('michelle').GetItem(gateID)
        if slimItem.dunMusicUrl is not None and targetID == eve.session.shipid:
            dbgInfo = ('gateID:', gateID)
            sm.StartService('jukebox').PlayStinger(slimItem.dunMusicUrl.lower(), dbgInfo)
        self.PlayNamedAnimations(gateBall.model, 'Activation')




