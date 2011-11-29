import trinity
import spaceObject
import turret
import nodemanager
import state
import uthread
import log
import math

class Ship(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.Ship'
    __notifyevents__ = ['OnModularShipReady']

    def __init__(self):
        spaceObject.SpaceObject.__init__(self)
        self.activeTargetID = None
        self.gainCurve = trinity.TriScalarCurve()
        self.gainCurve.value = 0.0
        self.boosterAniMats = []
        self.boosters = []
        self.targets = []
        self.missiles = []
        self.audioEntities = []
        self.shipSpeedParameter = None
        self.turrets = []
        self.modules = {}
        self.cloakedCopy = None
        self.cloakedShaderStorage = None
        self.fitted = False
        self.burning = False
        self.isTech3 = False
        self.loadingModel = False



    def DoPartition(self, *args):
        apply(self.OnPartition, args)



    def Prepare(self, spaceMgr):
        self.spaceMgr = spaceMgr
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        if slimItem is None:
            return 
        techLevel = sm.StartService('godma').GetTypeAttribute(slimItem.typeID, const.attributeTechLevel)
        if techLevel == 3.0:
            self.isTech3 = True
            subsystems = {}
            for module in slimItem.modules:
                group = cfg.invtypes.Get(module[1]).Group()
                if group.categoryID == const.categorySubSystem:
                    subsystems[group.groupID] = module[1]

            t3ShipSvc = sm.StartService('t3ShipSvc')
            sm.RegisterNotify(self)
            uthread.new(t3ShipSvc.GetTech3ShipFromDict, slimItem.typeID, subsystems, self.id)
            self.loadingModel = True
        else:
            spaceObject.SpaceObject.Prepare(self, spaceMgr)



    def OnModularShipReady(self, id, modelPath):
        if self.id == id:
            model = trinity.Load(modelPath)
            spaceObject.SpaceObject.LoadModel(self, None, False, loadedModel=model)
            self.Assemble()
            self.Display(1)
            sm.UnregisterNotify(self)
            self.loadingModel = False



    def LoadModel(self, fileName = None, useInstance = False):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        if slimItem is None:
            return 
        fileName = self.GetTrinityVersionFilename(cfg.invtypes.Get(slimItem.typeID).GraphicFile())
        spaceObject.SpaceObject.LoadModel(self, fileName, useInstance)



    def Assemble(self):
        bp = sm.StartService('michelle').GetBallpark()
        if bp is None:
            self.LogInfo('Assemble - could not get ballpark, so no destiny sim running. This should never happen!')
            return 
        slimItem = bp.GetInvItem(self.id)
        if not slimItem:
            self.LogInfo('Assemble - could not find the item so not assembling')
            return 
        self.typeID = slimItem.typeID
        self.UnSync()
        tfs = self.model.Find('trinity.TriSplTransform')
        self.boosters = filter(lambda node: node.name.startswith('locator_booster'), tfs)
        self.targets = filter(lambda node: node.name.startswith('locator_damage'), tfs)
        self.missiles = filter(lambda node: node.name.startswith('locator_missile'), tfs)
        if self.model.__bluetype__ == 'trinity.EveShip2':
            if len(self.model.damageLocators) == 0:
                self.LogError('Type', self.typeID, 'has no damage locators')
        elif self.model.__bluetype__ != 'eve.EveShip':
            if len(self.targets) == 0:
                self.LogError('Type', self.typeID, 'has no damage locators')
        elif len(self.model.damageLocators) == 0:
            self.LogError('Type', self.typeID, 'has no damage locators')
        dummyTarget = trinity.TriTransform()
        dummyTarget.name = 'locator_damage_dummy'
        self.model.children.append(dummyTarget)
        self.targets = [dummyTarget]
        self.runningupdate = 0
        self.boosterType = 'booster_blue'
        self.boosterSound = None
        if self.id == eve.session.shipid:
            self.FitHardpoints()
        self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        self.FitBoosters2()



    def Release(self):
        if self.released:
            return 
        if self.model is None:
            return 
        for (booster, animat,) in self.boosterAniMats:
            animat.emissiveRenderScale = None

        self.modules = {}
        if self.explodeOnRemove:
            self.Explode()
        self.KillCloakedCopy()
        self.boosterAniMats = []
        self.boosters = []
        self.targets = []
        self.missiles = []
        self.audioEntities = []
        self.generalAudioEntity = None
        spaceObject.SpaceObject.Release(self, 'Ship')
        self.cloakShaderStorage = None



    def KillCloakedCopy(self):
        if getattr(self, 'cloakedCopy', None) is not None:
            cloakedCopy = self.cloakedCopy
            scene = sm.StartService('sceneManager').GetRegisteredScene('default')
            scene.models.fremove(cloakedCopy)
            scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
            scene2.objects.fremove(cloakedCopy)
            if hasattr(cloakedCopy, 'translationCurve'):
                cloakedCopy.translationCurve = None
            if hasattr(cloakedCopy, 'rotationCurve'):
                cloakedCopy.rotationCurve = None
            self.cloakedCopy = None
            self.LogInfo('Removed cloaked copy of ship')



    def LookAtMe(self):
        if not self.model:
            return 
        if not self.fitted:
            self.FitHardpoints()



    def CheckHardpointsForXLGuns(self):
        if self.fitted:
            return 
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        if slimItem is None:
            self.LogError('no invitem property for ship')
            return 
        for (moduleID, typeID,) in slimItem.modules:
            graphicFile = cfg.invtypes.Get(typeID).GraphicFile()
            if graphicFile[1] == 'h':
                return True

        return False



    def ModuleListFromMichelleSlimItem(self, slimItem):
        list = []
        for (moduleID, typeID,) in slimItem.modules:
            list.append((moduleID, typeID))

        list.sort()
        return list



    def PrepareFiringSequence(self, effectWrapper, slaveTurrets, targetID):
        if effectWrapper.itemID in self.modules:
            turretModule = self.modules[effectWrapper.itemID]
            turretModule.TakeAim(targetID)
            for slaveTurret in slaveTurrets:
                turretModule = self.modules[slaveTurret]
                turretModule.TakeAim(targetID)

        else:
            log.LogInfo('PrepareFiringSequence - item not found')



    def EnterWarp(self):
        for t in self.turrets:
            t.EnterWarp()




    def ExitWarp(self):
        for t in self.turrets:
            t.ExitWarp()




    def UnfitHardpoints(self):
        if not self.fitted:
            return 
        newModules = {}
        for (key, val,) in self.modules.iteritems():
            if val not in self.turrets:
                newModules[key] = val

        self.modules = newModules
        del self.turrets[:]
        self.fitted = False



    def FitHardpoints(self):
        if self.fitted:
            return 
        if self.model is None:
            self.LogWarn('FitHardpoints - No model')
            return 
        self.fitted = True
        newTurretSetDict = turret.TurretSet.FitTurrets(self.id, self.model)
        self.turrets = []
        for (key, val,) in newTurretSetDict.iteritems():
            self.modules[key] = val
            self.turrets.append(val)




    def KillBooster(self):
        if self.shipSpeedParameter is not None:
            self.shipSpeedParameter.value = 0.0



    def OnDamageState(self, damageState):
        if self.model is None:
            return 
        self.SetDamageStateSingle(damageState[2])



    def SetDamageStateSingle(self, health):
        damage = 1.0 - health
        effectPosition = trinity.TriVector()
        if damage < 0.2:
            for each in list(self.model.particleSystems):
                if each.name == 'damage':
                    self.model.particleSystems.remove(each)

            for each in list(self.model.particleEmitters):
                if each.name == 'damage':
                    self.model.particleEmitters.remove(each)

            self.burning = False
        elif self.id == sm.StartService('state').GetExclState(state.lookingAt) and not self.burning:
            self.burning = True
            if len(self.model.damageLocators):
                furthestBack = self.model.damageLocators[0]
                for locatorTranslation in self.model.damageLocators:
                    if locatorTranslation.z > furthestBack.z:
                        furthestBack = locatorTranslation

                effectPosition = furthestBack
            scale = math.sqrt(self.model.boundingSphereRadius / 30.0)
            effect = trinity.Load('res:/Emitter/Damage/fuel_low.red')
            for each in effect.children:
                for emitter in each.particleEmitters:
                    emitter.name = 'damage'
                    emitter.position = (effectPosition.x, effectPosition.y, effectPosition.z)
                    emitter.minRadius *= scale
                    emitter.maxRadius *= scale
                    emitter.minSizeBirth *= scale
                    emitter.minSizeDeath *= scale
                    emitter.maxSizeBirth *= scale
                    emitter.maxSizeDeath *= scale
                    emitter.minLifetime *= scale
                    emitter.maxLifetime *= scale
                    self.model.particleEmitters.append(emitter)

                for system in each.particleSystems:
                    system.name = 'damage'
                    self.model.particleSystems.append(system)


            effect = None



    def Explode(self):
        explosionCleanupTime = None
        if self.radius < 20.0:
            explosionURL = 'res:/Emitter/tracerexplosion/NPCDeathS2.blue'
        elif self.radius < 80.0:
            explosionURL = 'res:/Emitter/tracerexplosion/NPCDeathM2.blue'
        elif self.radius < 1500.0:
            explosionURL = 'res:/Emitter/tracerexplosion/NPCDeathL2.blue'
        elif self.radius < 6000.0:
            explosionURL = 'res:/Model/Effect/CapitalDeath.blue'
        else:
            explosionCleanupTime = 25000
            explosionURL = 'res:/Model/Effect/TitanDeath.blue'
        return spaceObject.SpaceObject.Explode(self, explosionURL, explosionCleanupDelay=explosionCleanupTime)



    def ShakeShip(self, magnitude, repeat = 1, stepLength = 0.1, timeout = 10.0):
        log.LogException('You should not be using Ship::ShakeShip. It breaks other stuff.')



    def TargetIdleTurrets(self):
        pass



    def SetMainColor(self):
        godmaStateManager = sm.StartService('godma').GetStateManager()
        godmaType = godmaStateManager.GetType(599)
        mainColor = trinity.TriColor()
        mainColor.FromInt(godmaType.mainColor)
        mats = nodemanager.FindNodes(self.model, 'main', 'trinity.TriMaterial')
        stages = nodemanager.FindNodes(self.model, 'main', 'trinity.TriTextureStage')
        if len(mats) == 0 and len(stages) == 0:
            return 
        for m in mats:
            m.diffuse = mainColor.CopyTo()
            m.ambient = mainColor.CopyTo()
            m.ambient.Scale(0.25)

        for stage in stages:
            stage.customColor = mainColor.CopyTo()




exports = {'spaceObject.Ship': Ship}

