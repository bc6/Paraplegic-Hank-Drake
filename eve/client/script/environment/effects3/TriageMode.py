import effects

class TriageMode(effects.ShipRenderEffect):
    __guid__ = 'effects.TriageMode'
    __gfx__ = 'res:/Model/Effect3/TriageMode.red'
    __scaleTime__ = 0

    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


