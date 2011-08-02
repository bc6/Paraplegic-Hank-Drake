import blue
import trinity
import spaceObject
import uthread
import nodemanager
import timecurves
import base
import util
import random
import turret
TURRET_GFXID_FIGHTERBOMBER = {const.raceAmarr: 11515,
 const.raceGallente: 11517,
 const.raceCaldari: 11516,
 const.raceMinmatar: 11518}
TURRET_GFXID_COMBATDRONE = {const.raceAmarr: 11504,
 const.raceGallente: 11506,
 const.raceCaldari: 11505,
 const.raceMinmatar: 11508}
TURRET_GFXID_GENERIC = 11507

class CombatDroneLight(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.CombatDroneLight'

    def __init__(self):
        spaceObject.SpaceObject.__init__(self)
        self.modules = {}
        self.targets = []
        self.fitted = False
        self.boosters = None
        self.model = None
        self.npcDrone = True



    def LoadModel(self, fileName = None, useInstance = False):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        self.typeID = slimItem.typeID
        if settings.user.ui.Get('droneModelsEnabled', 1) or not self.npcDrone:
            fileName = self.GetTrinityVersionFilename(cfg.invtypes.Get(slimItem.typeID).GraphicFile())
        else:
            fileName = 'res:/dx9/model/drone/DroneModelsDisabled.red'
        spaceObject.SpaceObject.LoadModel(self, fileName, useInstance)



    def Assemble(self):
        if not (settings.user.ui.Get('droneModelsEnabled', 1) or not self.npcDrone):
            return 
        self.FitBoosters2(alwaysOn=True)
        self.SetupAmbientAudio()
        if hasattr(self.model, 'ChainAnimationEx'):
            self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)



    def FitHardpoints(self):
        if self.fitted:
            return 
        if self.model is None:
            self.LogWarn('FitHardpoints - No model')
            return 
        self.fitted = True
        if not settings.user.ui.Get('turretsEnabled', 1):
            return 
        turretTypeID = None
        to = cfg.invtypes.Get(self.typeID)
        raceID = to.raceID
        groupID = to.groupID
        turretGraphicID = TURRET_GFXID_GENERIC
        if raceID is not None:
            if groupID == const.groupFighterBomber:
                turretGraphicID = TURRET_GFXID_FIGHTERBOMBER[raceID]
            else:
                turretGraphicID = TURRET_GFXID_COMBATDRONE[raceID]
        if turretGraphicID is not None:
            ts = turret.TurretSet.AddTurretToModel(self.model, turretGraphicID, 1)
            if ts is not None:
                self.modules[self.id] = ts



    def Release(self):
        if self.released:
            return 
        self.modules = None
        spaceObject.SpaceObject.Release(self)



    def Explode(self):
        if not (settings.user.ui.Get('droneModelsEnabled', 1) or not self.npcDrone) or not settings.user.ui.Get('explosionEffectsEnabled', 1):
            return False
        explosionURL = 'res:/Emitter/explosion_end.blue'
        return spaceObject.SpaceObject.Explode(self, explosionURL, absoluteScaling=0.25, scaling=0.8 + random.random() * 0.4, randomRotation=True)



exports = {'spaceObject.CombatDroneLight': CombatDroneLight}

