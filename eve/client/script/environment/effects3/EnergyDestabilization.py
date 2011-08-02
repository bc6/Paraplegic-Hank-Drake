import effects

class EnergyDestabilization(effects.StretchEffect):
    __guid__ = 'effects.EnergyDestabilization'
    __gfx__ = 'res:/Model/Effect3/EnergyDestabilization.red'

    def _Key(trigger):
        return (trigger.shipID,
         trigger.targetID,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


