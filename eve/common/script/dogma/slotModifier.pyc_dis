#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/dogma/slotModifier.py
import dogmaXP

class SlotModifier(dogmaXP.Effect):
    __guid__ = 'dogmaXP.SlotModifier'
    __effectIDs__ = ['effectSlotModifier']
    __modifier_only__ = 0

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.AddModifier(const.dgmAssModAdd, shipID, const.attributeHiSlots, itemID, const.attributeHiSlotModifier)
        dogmaLM.AddModifier(const.dgmAssModAdd, shipID, const.attributeMedSlots, itemID, const.attributeMedSlotModifier)
        dogmaLM.AddModifier(const.dgmAssModAdd, shipID, const.attributeLowSlots, itemID, const.attributeLowSlotModifier)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(const.dgmAssModAdd, shipID, const.attributeHiSlots, itemID, const.attributeHiSlotModifier)
        dogmaLM.RemoveModifier(const.dgmAssModAdd, shipID, const.attributeMedSlots, itemID, const.attributeMedSlotModifier)
        dogmaLM.RemoveModifier(const.dgmAssModAdd, shipID, const.attributeLowSlots, itemID, const.attributeLowSlotModifier)

    RestrictedStop = Stop