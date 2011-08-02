import effects

class ArmorRepair(effects.ShipRenderEffect):
    __guid__ = 'effects.ArmorRepair'
    __gfx__ = 'res:/Model/Effect3/ArmorRepair.red'

    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


class RemoteArmorRepair(effects.StretchEffect):
    __guid__ = 'effects.RemoteArmourRepair'
    __gfx__ = 'res:/Model/Effect3/RemoteArmorRepair.red'

    def _Key(trigger):
        return (trigger.shipID,
         trigger.targetID,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


