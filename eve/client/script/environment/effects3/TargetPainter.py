import effects

class TargetPainter(effects.StretchEffect):
    __guid__ = 'effects.TargetPaint'
    __gfx__ = 'res:/Model/Effect3/TargetPaint.red'

    def _Key(trigger):
        return (trigger.shipID,
         trigger.targetID,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


