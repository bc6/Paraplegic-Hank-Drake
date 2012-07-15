#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/environment/effects/WarpDisruptFieldGenerating.py
import effects

class WarpDisruptFieldGenerating(effects.ShipEffect):
    __guid__ = 'effects.WarpDisruptFieldGenerating'

    def __init__(self, trigger, *args):
        effects.ShipEffect.__init__(self, trigger, *args)
        self.moduleTypeID = trigger.moduleTypeID
        self.radius = 20000.0
        if trigger.graphicInfo is not None:
            self.realRadius = trigger.graphicInfo.range
        else:
            self.realRadius = self.fxSequencer.GetType(self.moduleTypeID).warpScrambleRange

    def Prepare(self):
        effects.ShipEffect.Prepare(self)
        radius = self.realRadius
        scale = radius / self.radius
        self.gfxModel.scaling = (scale, scale, scale)