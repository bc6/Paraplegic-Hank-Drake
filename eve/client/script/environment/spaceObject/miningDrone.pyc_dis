#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/environment/spaceObject/miningDrone.py
import spaceObject
import turretSet
TURRET_GFXID = 11521

class MiningDrone(spaceObject.CombatDroneLight):
    __guid__ = 'spaceObject.MiningDrone'

    def FitHardpoints(self, blocking = False):
        if self.fitted:
            return
        if self.model is None:
            self.LogWarn('FitHardpoints - No model')
            return
        self.fitted = True
        if not settings.user.ui.Get('turretsEnabled', 1):
            return
        ts = turretSet.TurretSet.AddTurretToModel(self.model, TURRET_GFXID, 1)
        if ts is not None:
            self.modules[self.id] = ts


exports = {'spaceObject.MiningDrone': MiningDrone}