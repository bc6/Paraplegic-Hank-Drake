import blue
import spaceObject
import uthread
import timecurves
import trinity

class Cargo(spaceObject.DeployableSpaceObject):
    __guid__ = 'spaceObject.Cargo'

    def Assemble(self):
        self.UnSync()
        self.SetColorBasedOnStatus()
        if self.model is not None:
            self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)



    def Explode(self):
        if self.exploded:
            return False
        if self.model is None:
            return 
        self.exploded = True
        fileName = 'res:/dx9/Model/WorldObject/Cargo/cargoContainerImploding.red'
        gfx = trinity.Load(fileName)
        if gfx:
            gfx.translationCurve = self
            gfx.modelRotationCurve = self.model.modelRotationCurve
            self.explosionModel = gfx
        else:
            self.LogError('Cargo Container Misisng GFX for explosion. Could not find %s', fileName)
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        scene2.objects.append(gfx)
        return False



exports = {'spaceObject.Cargo': Cargo}

