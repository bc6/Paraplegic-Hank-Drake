import blue
import trinity
import spaceObject
import destiny
import uthread
import nodemanager
import timecurves
import base
import util
import turret
import random
import turret
from string import split
entityExplosionsS = ['res:/Emitter/tracerexplosion/NPCDeathS1.blue', 'res:/Emitter/tracerexplosion/NPCDeathS3.blue', 'res:/Emitter/tracerexplosion/NPCDeathS4.blue']
entityExplosionsM = ['res:/Emitter/tracerexplosion/NPCDeathM1.blue', 'res:/Emitter/tracerexplosion/NPCDeathM3.blue', 'res:/Emitter/tracerexplosion/NPCDeathM4.blue']
entityExplosionsL = ['res:/Emitter/tracerexplosion/NPCDeathL1.blue', 'res:/Emitter/tracerexplosion/NPCDeathL3.blue', 'res:/Emitter/tracerexplosion/NPCDeathL4.blue']

class EntityShip(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.EntityShip'

    def __init__(self):
        spaceObject.SpaceObject.__init__(self)
        self.gfxTurretID = None
        self.boosters = []
        self.targets = []
        self.turretList = []
        self.fitted = False
        self.typeID = None
        self.modules = {}
        self.model = None



    def LoadModel(self, fileName = None, useInstance = False):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        self.typeID = slimItem.typeID
        godmaStateManager = sm.StartService('godma').GetStateManager()
        godmaType = godmaStateManager.GetType(self.typeID)
        self.gfxBoosterID = godmaType.gfxBoosterID
        self.turretTypeID = godmaType.gfxTurretID
        fileName = self.GetTrinityVersionFilename(cfg.invtypes.Get(slimItem.typeID).GraphicFile())
        spaceObject.SpaceObject.LoadModel(self, fileName, useInstance)



    def Assemble(self):
        if self.gfxBoosterID == 0:
            self.LogError('Entity type %s has invalid gfxBoosterID ( not set) ' % self.typeID)
            self.gfxBoosterID = 395
        if self.model is not None:
            self.FitBoosters2(self.gfxBoosterID)
            if hasattr(self.model, 'ChainAnimationEx'):
                self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
            self.SetupAmbientAudio()



    def LookAtMe(self):
        if self.model is None:
            return 
        if not self.fitted:
            self.FitHardpoints()



    def FitHardpoints(self):
        if self.model is None:
            return 
        if self.model is None:
            self.LogWarn('FitHardpoints - No model')
            return 
        if self.fitted:
            return 
        turretLocatorCount = self.model.GetTurretLocatorCount()
        newTurretSet = turret.TurretSet.FitTurret(self.model, self.typeID, self.turretTypeID, 1, turretLocatorCount)
        if newTurretSet is None:
            return 
        self.fitted = True
        self.modules[self.id] = newTurretSet



    def FitBoosters(self, graphicID):
        graphicURL = util.GraphicFile(graphicID)
        if graphicURL == '':
            slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
            self.LogError('Entity type', slimItem.typeID, 'has invalid gfxBoosterID (', graphicID, ')')
            self.gfxBoosterID = 395
        b = blue.os.LoadObject(graphicURL)
        self.boosterType = split(graphicURL, '/')[-1:][0][:-5]
        for booster in self.boosters:
            del booster.children[:]
            booster.object = b.object.CopyTo()
            booster.display = 1




    def Explode(self):
        if self.typeID is None:
            return 
        effectOffset = self.typeID % 3
        if self.radius < 100.0:
            explosionURL = entityExplosionsS[(self.typeID % 3)]
        elif self.radius < 400.0:
            explosionURL = entityExplosionsM[(self.typeID % 3)]
        else:
            explosionURL = entityExplosionsL[(self.typeID % 3)]
        return spaceObject.SpaceObject.Explode(self, explosionURL, randomRotation=True)



    def Release(self):
        if self.released:
            return 
        for loc in self.turretList:
            if hasattr(loc, 'object'):
                loc.object = None

        for turretPair in self.modules.itervalues():
            turretPair.Release()
            turretPair.owner = None

        self.modules = {}
        self.boosters = []
        self.targets = []
        self.turretList = []
        spaceObject.SpaceObject.Release(self)



exports = {'spaceObject.EntityShip': EntityShip}

