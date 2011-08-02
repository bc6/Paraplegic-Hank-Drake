import effects

class SensorBoostTarget(effects.StretchEffect):
    __guid__ = 'effects.ElectronicAttributeModifyTarget'
    __gfx__ = 'res:/Model/Effect3/SensorBoost.red'

    def _Key(trigger):
        return (trigger.shipID,
         trigger.targetID,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


