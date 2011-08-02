import effects

class WarpScramble(effects.StretchEffect):
    __guid__ = 'effects.WarpScramble'
    __gfx__ = 'res:/Model/Effect3/WarpScrambler.red'

    def Key(trigger):
        return (trigger.shipID,
         trigger.targetID,
         None,
         None,
         trigger.guid)


    Key = staticmethod(Key)

    def Start(self, duration):
        effects.StretchEffect.Start(self, duration)
        shipID = self.GetEffectShipID()
        targetID = self.GetEffectTargetID()
        if eve.session and eve.session.shipid and (settings.user.ui.Get('notifyMessagesEnabled', 1) or eve.session.shipid in (shipID, targetID)):
            bracketSvc = sm.StartService('bracket')
            jammerName = bracketSvc.GetBracketName2(shipID)
            targetName = bracketSvc.GetBracketName2(targetID)
            if eve.session.shipid == targetID:
                eve.Message('WarpScrambledBy', {'scrambler': jammerName})
            elif eve.session.shipid == shipID:
                eve.Message('WarpScrambledSuccess', {'scrambled': targetName})
            else:
                eve.Message('WarpScrambledOtherBy', {'scrambler': jammerName,
                 'scrambled': targetName})




