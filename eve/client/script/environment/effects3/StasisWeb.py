import effects
FX_SCALE_EFFECT_SYMMETRICAL = 1

class StasisWeb(effects.ShipEffect):
    __guid__ = 'effects.ModifyTargetSpeed'
    __gfx__ = 'res:/Model/Effect3/StasisWeb.red'
    __scaling__ = FX_SCALE_EFFECT_SYMMETRICAL

    def _Key(trigger):
        return (trigger.targetID,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)

    def __init__(self, trigger):
        self.ballIDs = [trigger.shipID, trigger.targetID]
        self.gfx = None
        self.gfxModel = None



    def GetEffectShipID(self):
        return self.ballIDs[1]




