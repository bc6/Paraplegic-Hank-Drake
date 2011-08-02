import effects
import trinity
import blue
FX_SCALE_EFFECT_NONE = 0

class WarpDisruptFieldGenerating(effects.ShipEffect):
    __guid__ = 'effects.WarpDisruptFieldGenerating'
    __gfx__ = 'res:/Model/effect3/WarpDisruptorBubble.red'
    __scaleTime__ = 0
    __scaling__ = FX_SCALE_EFFECT_NONE

    def __init__(self, trigger):
        self.ballIDs = [trigger.shipID]
        self.gfx = None
        self.gfxModel = None
        self.moduleTypeID = trigger.moduleTypeID
        self.radius = 20000.0
        if trigger.graphicInfo is not None:
            self.realRadius = trigger.graphicInfo.range
        else:
            self.realRadius = sm.GetService('godma').GetType(self.moduleTypeID).warpScrambleRange



    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)

    def Prepare(self):
        effects.ShipEffect.Prepare(self)
        radius = self.realRadius
        scale = radius / self.radius
        self.gfxModel.scaling = (scale, scale, scale)




