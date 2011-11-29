import spaceObject
import blue
import timecurves
import uthread
import util
import trinity
import random

class ScannerProbe(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.ScannerProbe'
    __notifyevents__ = ['OnSlimItemChange']

    def __init__(self):
        spaceObject.SpaceObject.__init__(self)
        sm.RegisterNotify(self)



    def Release(self, origin = None):
        sm.UnregisterNotify(self)
        spaceObject.SpaceObject.Release(self)



    def FakeWarp(self):
        blue.pyos.synchro.SleepSim(random.randint(100, 1000))
        url = 'res:/Model/Effect3/ProbeWarp.red'
        gfx = trinity.Load(url)
        if gfx.__bluetype__ != 'trinity.EveRootTransform':
            root = trinity.EveRootTransform()
            root.children.append(gfx)
            root.name = url
            gfx = root
        gfx.translationCurve = self
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        scene2.objects.append(gfx)
        uthread.pool('ScannerProbe::HideBall', self.HideBall)
        uthread.pool('ScannerProbe::DelayedRemove', self.DelayedRemove, 3000, self.model)
        uthread.pool('ScannerProbe::DelayedRemove', self.DelayedRemove, 3000, gfx)



    def DelayedRemove(self, duration, gfx):
        if gfx is None:
            return 
        if duration != 0:
            blue.pyos.synchro.SleepSim(duration)
        if hasattr(gfx, 'translationCurve'):
            gfx.translationCurve = None
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        if scene2 is not None:
            scene2.objects.fremove(gfx)



    def HideBall(self):
        blue.pyos.synchro.SleepSim(500)
        self.model.display = 0



    def OnSlimItemChange(self, oldItem, newItem):
        if oldItem.itemID != self.id or not getattr(newItem, 'warpingAway', 0):
            return 
        uthread.pool('ScanProbe::FakeWarp', self.FakeWarp)



    def Assemble(self):
        slimItem = sm.StartService('michelle').GetItem(self.id)
        spaceObject.SpaceObject.Assemble(self)



    def Explode(self):
        explosionURL = 'res:/Emitter/explosion_end.blue'
        return spaceObject.SpaceObject.Explode(self, explosionURL, absoluteScaling=0.25, scaling=0.8 + random.random() * 0.4, randomRotation=True)



    def LoadModel(self, fileName = None, useInstance = False):
        slimItem = sm.StartService('michelle').GetItem(self.id)
        self.LogInfo('Scanner Probe - LoadModel', slimItem.nebulaType)
        fileName = cfg.invtypes.Get(slimItem.typeID).GraphicFile()
        fileName = self.GetTrinityVersionFilename(fileName)
        spaceObject.SpaceObject.LoadModel(self, fileName, useInstance)



exports = {'spaceObject.ScannerProbe': ScannerProbe}

