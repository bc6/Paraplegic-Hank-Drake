import effects
FX_SCALE_EFFECT_SYMMETRICAL = 1
FX_SCALE_EFFECT_NONE = 0

class TrackingBoost(effects.ShipEffect):
    __guid__ = 'effects.TurretWeaponRangeTrackingSpeedMultiplyActivate'
    __gfx__ = 'res:/Model/Effect3/TrackingBoost.red'
    __scaling__ = FX_SCALE_EFFECT_NONE

    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         'effect.TrackingBoost')


    _Key = staticmethod(_Key)


class TrackingBoostTarget(effects.StretchEffect):
    __guid__ = 'effects.TurretWeaponRangeTrackingSpeedMultiplyTarget'
    __gfx__ = 'res:/Model/Effect3/TrackingBoostTarget.red'
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
         'effect.TrackingBoost')


    _Key = staticmethod(_Key)


