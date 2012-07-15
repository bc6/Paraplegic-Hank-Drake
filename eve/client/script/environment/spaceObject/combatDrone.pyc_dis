#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/environment/spaceObject/combatDrone.py
import spaceObject
import turretSet
TURRET_GFXID_GENERIC = 11507

class CombatDrone(spaceObject.CombatDroneLight):
    __guid__ = 'spaceObject.CombatDrone'

    def __init__(self):
        spaceObject.CombatDroneLight.__init__(self)
        self.npcDrone = False

    def FitHardpoints(self, blocking = False):
        if self.fitted:
            return
        if self.model is None:
            self.LogWarn('FitHardpoints - No model')
            return
        self.fitted = True
        if not settings.user.ui.Get('turretsEnabled', 1):
            return
        turretGraphicID = TURRET_GFXID_GENERIC
        ts = turretSet.TurretSet.AddTurretToModel(self.model, turretGraphicID, 1)
        if ts is not None:
            self.modules[self.id] = ts


exports = {'spaceObject.CombatDrone': CombatDrone}