import spaceObject
import timecurves
import nodemanager
import state
import trinity
import blue
from string import split, lower
emitterMap = {('low', 'fuel'): 'fuel_low.blue',
 ('med', 'fuel'): 'fuel_med.blue',
 ('high', 'fuel'): 'fuel_high.blue',
 ('low', 'oxygen'): 'oxygen_low.blue',
 ('med', 'oxygen'): 'oxygen_med.blue',
 ('high', 'oxygen'): 'oxygen_high.blue',
 ('low', 'electric'): 'electric_low.blue',
 ('med', 'electric'): 'electric_med.blue',
 ('high', 'electric'): 'electric_high.blue',
 ('low', 'radiation'): 'radioactive_low.blue',
 ('med', 'radiation'): 'radiation_med.blue',
 ('high', 'radiation'): 'radiation_high.blue',
 ('low', 'plasma'): 'plasma_low.blue',
 ('med', 'plasma'): 'plasma_med.blue',
 ('high', 'plasma'): 'plasma_high.blue'}

class Capsule(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.Capsule'

    def __init__(self):
        spaceObject.SpaceObject.__init__(self)
        self.targets = []
        self.cloakedCopy = None
        self.cloakedShaderStorage = None



    def LoadModel(self, fileName = None, useInstance = False):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        fileName = self.GetTrinityVersionFilename(cfg.invtypes.Get(slimItem.typeID).GraphicFile())
        spaceObject.SpaceObject.LoadModel(self, fileName, useInstance)



    def Assemble(self):
        if self.model is None:
            self.LogWarn('Capsule::Assemble - No model')
            return 
        if self.model.__bluetype__ != 'eve.EveShip':
            self.targets = nodemanager.FindNodes(self.model, 'locator_damage', 'trinity.TriSplTransform')
        else:
            self.targets = self.model.damageLocators
        self.UnSync()
        self.FitBoosters2()



    def Explode(self):
        return spaceObject.SpaceObject.Explode(self, 'res:/Model/Effect/capsule_explosion.blue')



    def Release(self):
        if self.released:
            return 
        if self.explodeOnRemove:
            self.Explode()
        self.KillCloakedCopy()
        spaceObject.SpaceObject.Release(self, 'Capsule')
        self.cloakShaderStorage = None



    def KillCloakedCopy(self):
        if self.cloakedCopy:
            scene = sm.StartService('sceneManager').GetRegisteredScene('default')
            scene.models.fremove(self.cloakedCopy)
            self.cloakedCopy = None
            self.LogInfo('Removed cloaked copy')



    def DoPartition(self, *args):
        apply(self.OnPartition, args)



    def OnDamageState(self, damageState):
        if self.model is None:
            self.LogWarn('OnDamageState - No model')
            return 
        self.SetDamageStateSingle(damageState[2])



    def SetDamageStateSingle(self, health):
        if self.model.__bluetype__ == 'eve.EveShip':
            self.SetDamageStateSingleDX9(health)
        elif self.model.__bluetype__ == 'trinity.EveShip2':
            self.SetDamageStateSingleScene2(health)
        else:
            self.SetDamageStateSingleDX8(health)



    def SetDamageStateSingleDX8(self, health):
        damage = 1.0 - health
        locator2use = self.targets[0]
        if damage < 0.2:
            return 
        if damage < 0.6:
            state = 0
        elif damage < 0.8:
            state = 1
        else:
            state = 2
        states = ['low', 'med', 'high']
        theType = lower(split(locator2use.name, '_')[-1])
        emitterName = emitterMap[(states[state], theType)]
        emitter = blue.os.LoadObject('res:/Emitter/Damage/' + emitterName)
        if self.id == eve.session.shipid:
            for node in emitter.Find('audio.Node'):
                node.Stop()

            for node in emitter.Find('audio.SoundNode'):
                node.Stop()

        inthere = False
        for c in locator2use.children:
            if c.name == emitter.name:
                inthere = True
                break

        if not inthere:
            del locator2use.children[:]
            locator2use.children.append(emitter)



    def SetDamageStateSingleDX9(self, health):
        damage = 1.0 - health
        if damage < 0.2:
            damageEmitter = None
            for child in self.model.children:
                if getattr(child, 'name', '') == 'damageEmitter':
                    damageEmitter = child
                    break

            if damageEmitter is not None:
                self.model.children.fremove(damageEmitter)
            self.burning = False
        elif self.id == sm.StartService('state').GetExclState(state.lookingAt):
            self.burning = True
            emitter = blue.os.LoadObject('res:/Emitter/Damage/fuel_low.blue')
            emitter.name = 'damageEmitter'
            if self.id != eve.session.shipid:
                for node in emitter.Find('audio.Node'):
                    node.Stop()

                for node in emitter.Find('audio.SoundNode'):
                    node.Stop()

            if len(self.model.damageLocators):
                emitter.scaling.SetXYZ(0.2, 0.2, 0.2)
                furthestBack = self.model.damageLocators[0]
                for locatorTranslation in self.model.damageLocators:
                    if locatorTranslation.z > furthestBack.z:
                        furthestBack = locatorTranslation

                emitter.translation = furthestBack
                self.model.children.append(emitter)



    def SetDamageStateSingleScene2(self, health):
        damage = 1.0 - health
        if damage < 0.2:
            damageEmitter = None
            for child in self.model.children:
                if getattr(child, 'name', '') == 'damageEmitter':
                    damageEmitter = child
                    break

            if damageEmitter is not None:
                self.model.children.fremove(damageEmitter)
            self.burning = False
        elif self.id == sm.StartService('state').GetExclState(state.lookingAt):
            self.burning = True
            emitter = trinity.Load('res:/Emitter/Damage/fuel_low.red')
            emitter.name = 'damageEmitter'
            emitter.scaling = (0.2, 0.2, 0.2)
            if len(self.model.damageLocators):
                emitter.translation = (self.model.damageLocators[0].x, self.model.damageLocators[0].y, self.model.damageLocators[0].z)
            self.model.children.append(emitter)



exports = {'spaceObject.Capsule': Capsule}

