#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/environment/spaceObject/basicOrbital.py
import blue
import entities
import spaceObject
import uthread

class BasicOrbital(spaceObject.PlayerOwnedStructure):

    def Assemble(self):
        self.SetStaticRotation()

    def OnSlimItemUpdated(self, slimItem):
        orbitalState = getattr(slimItem, 'orbitalState', None)
        orbitalTimestamp = getattr(slimItem, 'orbitalTimestamp', blue.os.GetSimTime())
        fxSequencer = sm.GetService('FxSequencer')
        if not hasattr(self, 'orbitalState'):
            if orbitalState in (entities.STATE_ANCHORING, entities.STATE_ANCHORED):
                uthread.pool('SpaceObject::BasicOrbital::OnSlimItemUpdated', fxSequencer.OnSpecialFX, slimItem.itemID, slimItem.itemID, None, None, None, [], 'effects.AnchorDrop', 0, 1, 0)
            elif orbitalState in (entities.STATE_IDLE, entities.STATE_OPERATING):
                uthread.pool('SpaceObject::BasicOrbital::OnSlimItemUpdated', fxSequencer.OnSpecialFX, slimItem.itemID, slimItem.itemID, None, None, None, [], 'effects.StructureOnlined', 0, 1, 0)
        else:
            if orbitalState == entities.STATE_ANCHORING and self.orbitalState == entities.STATE_UNANCHORED:
                uthread.pool('SpaceObject::BasicOrbital::OnSlimItemUpdated', fxSequencer.OnSpecialFX, slimItem.itemID, slimItem.itemID, None, None, None, [], 'effects.AnchorDrop', 0, 1, 0)
            if orbitalState == entities.STATE_ONLINING and self.orbitalState == entities.STATE_ANCHORED:
                uthread.pool('SpaceObject::BasicOrbital::OnSlimItemUpdated', fxSequencer.OnSpecialFX, slimItem.itemID, slimItem.itemID, None, None, None, [], 'effects.StructureOnline', 0, 1, 0)
            if orbitalState == entities.STATE_IDLE and self.orbitalState == entities.STATE_ONLINING:
                uthread.pool('SpaceObject::BasicOrbital::OnSlimItemUpdated', fxSequencer.OnSpecialFX, slimItem.itemID, slimItem.itemID, None, None, None, [], 'effects.StructureOnlined', 0, 1, 0)
            if orbitalState == entities.STATE_ANCHORED and self.orbitalState in (entities.STATE_OFFLINING, entities.STATE_IDLE, entities.STATE_OPERATING):
                uthread.pool('SpaceObject::BasicOrbital::OnSlimItemUpdated', fxSequencer.OnSpecialFX, slimItem.itemID, slimItem.itemID, None, None, None, [], 'effects.StructureOffline', 0, 1, 0)
            if orbitalState == entities.STATE_UNANCHORING and self.orbitalState == entities.STATE_ANCHORED:
                uthread.pool('SpaceObject::BasicOrbital::OnSlimItemUpdated', fxSequencer.OnSpecialFX, slimItem.itemID, slimItem.itemID, None, None, None, [], 'effects.AnchorLift', 0, 1, 0)
        self.orbitalState = orbitalState
        self.orbitalTimestamp = orbitalTimestamp

    def IsAnchored(self):
        self.LogInfo('Anchor State = ', not self.isFree)
        return not self.isFree

    def IsOnline(self):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        return slimItem.orbitalState is not None and slimItem.orbitalState in (entities.STATE_OPERATING, entities.STATE_IDLE)


exports = {'spaceObject.BasicOrbital': BasicOrbital}