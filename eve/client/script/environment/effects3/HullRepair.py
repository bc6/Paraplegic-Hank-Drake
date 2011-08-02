import effects

class HullRepair(effects.ShipRenderEffect):
    __guid__ = 'effects.StructureRepair'
    __gfx__ = 'res:/Model/Effect3/HullRepair.red'

    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


