import spaceObject
import timecurves
import random
import trinity

class Comet(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.Comet'

    def Assemble(self):
        timecurves.ResetTimeCurves(self.model, self.id * 12345L)
        timecurves.ScaleTime(self.model, 5.0 + self.id % 20 / 20.0)
        x = 0.8 + 0.2 * random.random()
        y = 0.8 + 0.2 * random.random()
        z = 0.8 + 0.2 * random.random()
        self.model.scaling.SetXYZ(self.model.scaling.x * x, self.model.scaling.y * y, self.model.scaling.z * z)
        selfPos = trinity.TriVector(self.x * 1e-05, self.y * 1e-05, self.z * 1e-05)
        fwd = trinity.TriVector(0.0, 0.0, 1.0)
        selfPos.Normalize()
        self.model.rotationCurve = None
        self.model.rotation.SetRotationArc(fwd, selfPos)



exports = {'spaceObject.Comet': Comet}

