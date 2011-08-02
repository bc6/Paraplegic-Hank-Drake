import effects
FX_SCALE_EFFECT_SYMMETRICAL = 1
FX_SCALE_EFFECT_NONE = 0
FX_USEBALLTRANSLATION = 1
FX_USEBALLROTATION = 2

class ScanStrengthBonus(effects.ShipEffect):
    __guid__ = 'effects.ScanStrengthBonusActivate'
    __gfx__ = 'res:/Model/Effect3/ECCM.red'
    __scaling__ = FX_SCALE_EFFECT_SYMMETRICAL
    __positioning__ = FX_USEBALLTRANSLATION

    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


class ScanStrengthBonusTarget(effects.ShipEffect):
    __guid__ = 'effects.ScanStrengthBonusTarget'
    __gfx__ = 'res:/Model/Effect3/ECCM.red'
    __scaling__ = FX_SCALE_EFFECT_SYMMETRICAL

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

    def Start(self, duration):
        shipID = self.ballIDs[0]
        targetID = self.ballIDs[1]
        if eve.session and eve.session.shipid and (settings.user.ui.Get('notifyMessagesEnabled', 1) or eve.session.shipid in (shipID, targetID)):
            jammerName = sm.GetService('bracket').GetBracketName(shipID)
            targetName = sm.GetService('bracket').GetBracketName(targetID)
            if eve.session.shipid == targetID:
                eve.Message('TargetJammedBy', {'jammer': jammerName})
            elif eve.session.shipid == shipID:
                eve.Message('TargetJammedSuccess', {'jammed': targetName})
            else:
                eve.Message('TargetJammedOtherBy', {'jammer': jammerName,
                 'jammed': targetName})
        effects.ShipEffect.Start(self, duration)




