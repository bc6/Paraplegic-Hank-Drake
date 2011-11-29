import blue
import trinity
import spaceObject
import turret
import nodemanager
import timecurves
import base
import util
import uthread
import random
import log
import sys
entityExplosionsS = ['res:/Emitter/tracerexplosion/NPCDeathS1.blue', 'res:/Emitter/tracerexplosion/NPCDeathS3.blue', 'res:/Emitter/tracerexplosion/NPCDeathS4.blue']
entityExplosionsM = ['res:/Emitter/tracerexplosion/NPCDeathM1.blue', 'res:/Emitter/tracerexplosion/NPCDeathM3.blue', 'res:/Emitter/tracerexplosion/NPCDeathM4.blue']
entityExplosionsL = ['res:/Emitter/tracerexplosion/NPCDeathL1.blue', 'res:/Emitter/tracerexplosion/NPCDeathL3.blue', 'res:/Emitter/tracerexplosion/NPCDeathL4.blue']
TURRET_TYPE_ID = {const.raceAmarr: 462,
 const.raceGallente: 569,
 const.raceCaldari: 574,
 const.raceMinmatar: 498,
 const.racePirates: 462,
 const.raceSleepers: 4049}
TURRET_FALLBACK_TYPE_ID = 462

class SentryGun(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.SentryGun'

    def __init__(self):
        spaceObject.SpaceObject.__init__(self)
        self.targets = []
        self.modules = {}
        self.fitted = False
        self.typeID = None



    def Assemble(self):
        timecurves.ScaleTime(self.model, 0.9 + random.random() * 0.2)
        self.SetStaticRotation()
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        self.typeID = slimItem.typeID
        raceID = cfg.invtypes.Get(slimItem.typeID).raceID
        self.turretTypeID = TURRET_FALLBACK_TYPE_ID
        if raceID is not None:
            self.turretTypeID = TURRET_TYPE_ID[raceID]
        if settings.user.ui.Get('turretsEnabled', 1):
            self.FitHardpoints()



    def FitHardpoints(self):
        if self.fitted:
            return 
        if self.model is None:
            self.LogWarn('FitHardpoints - No model')
            return 
        if self.typeID is None:
            self.LogWarn('FitHardpoints - No typeID')
            return 
        self.fitted = True
        self.modules = {}
        ts = turret.TurretSet.FitTurret(self.model, self.typeID, self.turretTypeID, 1)
        if self.modules and ts:
            self.modules[self.id] = ts



    def LookAtMe(self):
        if not self.model:
            return 
        if not self.fitted:
            self.FitHardpoints()



    def Release(self):
        if self.released:
            return 
        self.modules = None
        spaceObject.SpaceObject.Release(self)



    def Explode(self):
        if not settings.user.ui.Get('explosionEffectsEnabled', 1):
            return self.exploded
        if self.radius < 100.0:
            explosionURL = entityExplosionsS[(self.typeID % 3)]
        elif self.radius < 400.0:
            explosionURL = entityExplosionsM[(self.typeID % 3)]
        elif self.radius <= 900.0:
            explosionURL = entityExplosionsL[(self.typeID % 3)]
        if self.radius <= 900.0:
            return spaceObject.SpaceObject.Explode(self, explosionURL)
        if self.exploded:
            return False
        self.exploded = True
        exlosionBasePath = 'res:/Emitter/tracerexplosion/'
        if self.radius > 3000.0:
            extraPath = 'StructureDeathRadius1500.blue'
        elif self.radius > 1500.0:
            extraPath = 'StructureDeathRadius1000.blue'
        else:
            extraPath = 'StructureDeathRadius500.blue'
        explosionURL = exlosionBasePath + extraPath
        gfx = trinity.Load(explosionURL.replace('.blue', '.red'))
        if gfx is None:
            return False
        explodingObjectDisplay = [ x for x in gfx.curveSets if x.name == 'ExplodingObjectDisplay' ]
        if gfx.__bluetype__ != 'trinity.EveRootTransform':
            root = trinity.EveRootTransform()
            root.children.append(gfx)
            root.name = explosionURL
            gfx = root
        self.model.translationCurve = self
        self.model.rotationCurve = None
        gfx.translationCurve = self
        self.explosionModel = gfx
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        scene2.objects.append(gfx)
        if len(explodingObjectDisplay):
            explodingObjectDisplay = explodingObjectDisplay[0]
            explodingObjectDisplay.bindings[0].destinationObject = self.model
            self.explosionDisplayBinding = explodingObjectDisplay.bindings[0]
        return True



exports = {'spaceObject.SentryGun': SentryGun}

