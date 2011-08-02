import effects
FX_SCALE_EFFECT_SYMMETRICAL = 1
FX_USEBALLTRANSLATION = 1
FX_SCALE_EFFECT_NONE = 0

class ECMBurst(effects.ShipEffect):
    __guid__ = 'effects.ECMBurst'
    __gfx__ = 'res:/Model/Effect3/EcmBurst.red'
    __scaling__ = FX_SCALE_EFFECT_NONE
    __positioning__ = FX_USEBALLTRANSLATION

    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


