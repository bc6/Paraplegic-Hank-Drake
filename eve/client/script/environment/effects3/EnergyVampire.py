import effects

class EnergyVampire(effects.StretchEffect):
    __guid__ = 'effects.EnergyVampire'
    __gfx__ = 'res:/Model/Effect3/EnergyVampire.red'

    def _Key(trigger):
        return (trigger.shipID,
         trigger.targetID,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


