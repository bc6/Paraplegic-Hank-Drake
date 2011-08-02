import effects

class EnergyTransfer(effects.StretchEffect):
    __guid__ = 'effects.EnergyTransfer'
    __gfx__ = 'res:/Model/Effect3/EnergyTransfer.red'

    def _Key(trigger):
        return (trigger.shipID,
         trigger.targetID,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


