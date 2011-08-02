import spaceObject
import turret
TURRET_GFXID = 11521

class MiningDrone(spaceObject.CombatDroneLight):
    __guid__ = 'spaceObject.MiningDrone'

    def FitHardpoints(self):
        if self.fitted:
            return 
        if self.model is None:
            self.LogWarn('FitHardpoints - No model')
            return 
        self.fitted = True
        if not settings.user.ui.Get('turretsEnabled', 1):
            return 
        ts = turret.TurretSet.AddTurretToModel(self.model, TURRET_GFXID, 1)
        if ts is not None:
            self.modules[self.id] = ts



exports = {'spaceObject.MiningDrone': MiningDrone}

