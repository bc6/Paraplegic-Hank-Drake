import effects
FX_SCALE_EFFECT_SYMMETRICAL = 1
FX_SCALE_EFFECT_NONE = 0

class CargoScan(effects.StretchEffect):
    __guid__ = 'effects.CargoScan'
    __gfx__ = 'res:/Model/Effect3/CargoScan.red'
    __scaling__ = FX_SCALE_EFFECT_NONE

    def __init__(self, trigger):
        self.ballIDs = [trigger.shipID, trigger.targetID]
        self.gfx = None
        self.gfxModel = None



    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


class ShipScan(effects.StretchEffect):
    __guid__ = 'effects.ShipScan'
    __gfx__ = 'res:/Model/Effect3/ShipScan.red'
    __scaling__ = FX_SCALE_EFFECT_NONE

    def __init__(self, trigger):
        self.ballIDs = [trigger.shipID, trigger.targetID]
        self.gfx = None
        self.gfxModel = None



    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


class SurveyScan(effects.ShipEffect):
    __guid__ = 'effects.SurveyScan'
    __gfx__ = 'res:/Model/Effect3/SurveyScan.red'
    __scaling__ = FX_SCALE_EFFECT_SYMMETRICAL

    def __init__(self, trigger):
        self.ballIDs = [trigger.shipID, trigger.targetID]
        self.gfx = None
        self.gfxModel = None



    def _Key(trigger):
        return (trigger.shipID,
         trigger.targetID,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


class TargetScan(effects.StretchEffect):
    __guid__ = 'effects.TargetScan'
    __gfx__ = 'res:/Model/Effect3/SurveyScan2.red'

    def _Key(trigger):
        return (trigger.shipID,
         trigger.targetID,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


