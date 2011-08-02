import blue
import trinity
import spaceObject
import nodemanager
import timecurves
import util
import turret
import random
from string import split
TURRET_GFXID_GENERIC = 11507

class CombatDrone(spaceObject.CombatDroneLight):
    __guid__ = 'spaceObject.CombatDrone'

    def __init__(self):
        spaceObject.CombatDroneLight.__init__(self)
        self.npcDrone = False



    def FitHardpoints(self):
        if self.fitted:
            return 
        if self.model is None:
            self.LogWarn('FitHardpoints - No model')
            return 
        self.fitted = True
        if not settings.user.ui.Get('turretsEnabled', 1):
            return 
        turretGraphicID = TURRET_GFXID_GENERIC
        ts = turret.TurretSet.AddTurretToModel(self.model, turretGraphicID, 1)
        if ts is not None:
            self.modules[self.id] = ts



exports = {'spaceObject.CombatDrone': CombatDrone}

