import effects

class ShieldBoosting(effects.ShipRenderEffect):
    __guid__ = 'effects.ShieldBoosting'
    __gfx__ = 'res:/Model/Effect3/ShieldBoosting.red'
    __scaleTime__ = 0

    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


