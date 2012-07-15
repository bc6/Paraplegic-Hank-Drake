#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/environment/spaceObject/sovereigntyInfrastructueHub.py
import trinity
import blue
import spaceObject
import pos
import sys
SHIELD_EFFECT = 'effects.ModifyShieldResonance'
ARMOR_EFFECT = 'effects.StructureRepair'

class SovereigntyInfrastructueHub(spaceObject.PlayerOwnedStructure):

    def __init__(self):
        spaceObject.PlayerOwnedStructure.__init__(self)
        self.fx = sm.GetService('FxSequencer')
        if self.id not in self.ballpark.slimItems:
            return
        slimItem = self.ballpark.slimItems[self.id]
        posState = getattr(slimItem, 'posState', None)
        if posState is None:
            return
        if posState == pos.STRUCTURE_SHIELD_REINFORCE:
            self.ShieldReinforced(True)
        elif posState == pos.STRUCTURE_ARMOR_REINFORCE:
            self.ArmorReinforced(True)

    def OnSlimItemUpdated(self, slimItem):
        posState = getattr(slimItem, 'posState', None)
        posTime = getattr(slimItem, 'posTimestamp', blue.os.GetWallclockTime())
        posDelay = getattr(slimItem, 'posDelayTime', 0)
        self.HandleStateChange(posState, posTime, posDelay)

    def HandleStateChange(self, posState, posTime, posDelay):
        self.ShieldReinforced(False)
        self.ArmorReinforced(False)
        if posState == pos.STRUCTURE_SHIELD_REINFORCE:
            self.ShieldReinforced(True)
        elif posState == pos.STRUCTURE_ARMOR_REINFORCE:
            self.ArmorReinforced(True)

    def ShieldReinforced(self, startEffect):
        self.fx.OnSpecialFX(self.id, None, None, None, None, [], SHIELD_EFFECT, False, startEffect, True, repeat=sys.maxint)

    def ArmorReinforced(self, startEffect):
        self.fx.OnSpecialFX(self.id, None, None, None, None, [], ARMOR_EFFECT, False, startEffect, True, repeat=sys.maxint)


exports = {'spaceObject.SovereigntyInfrastructueHub': SovereigntyInfrastructueHub}