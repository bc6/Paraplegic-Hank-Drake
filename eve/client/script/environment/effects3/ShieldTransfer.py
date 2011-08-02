import effects

class ShieldTransfer(effects.StretchEffect):
    __guid__ = 'effects.ShieldTransfer'
    __gfx__ = 'res:/Model/Effect3/ShieldTransfer.red'

    def _Key(trigger):
        return (trigger.shipID,
         trigger.targetID,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


