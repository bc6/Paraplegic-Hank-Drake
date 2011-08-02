import effects
import blue
FX_SCALE_EFFECT_SYMMETRICAL = 1
FX_SCALE_EFFECT_NONE = 0
FX_USEBALLTRANSLATION = 1
FX_USEBALLROTATION = 2

class Jettison(effects.ShipEffect):
    __guid__ = 'effects.Jettison'
    __gfx__ = 'res:/Model/Effect3/Jettison.red'
    __scaling__ = FX_SCALE_EFFECT_NONE

    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


