import effects

class ShieldHardening(effects.ShipRenderEffect):
    __guid__ = 'effects.ModifyShieldResonance'
    __gfx__ = 'res:/Model/Effect3/ShieldHardening.red'

    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


