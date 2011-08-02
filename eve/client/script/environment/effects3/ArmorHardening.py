import effects

class ArmorHardening(effects.ShipRenderEffect):
    __guid__ = 'effects.ArmorHardening'
    __gfx__ = 'res:/Model/Effect3/ArmorHardening.red'

    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


