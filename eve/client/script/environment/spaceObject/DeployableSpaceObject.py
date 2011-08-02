import nodemanager
import trinity
import spaceObject
RED = trinity.TriColor(1.0, 0.0, 0.0)
GREEN = trinity.TriColor(0.27, 0.53, 0.22)
YELLOW = trinity.TriColor(0.53, 0.53, 0.08)
HDRScale = 3.0

class DeployableSpaceObject(spaceObject.SpaceObject):
    __guid__ = None

    def SetColorBasedOnStatus(self):
        if self.isFree == 1:
            self.SetColor('green')
        else:
            self.SetColor('red')



    def SetColor(self, col):
        mats = self.GetMaterial()
        if len(mats) == 0:
            return 
        for glow in mats:
            if col == 'red':
                glow.v1 = RED.r * HDRScale
                glow.v2 = RED.g * HDRScale
                glow.v3 = RED.b * HDRScale
            elif col == 'yellow':
                glow.v1 = YELLOW.r * HDRScale
                glow.v2 = YELLOW.g * HDRScale
                glow.v3 = YELLOW.b * HDRScale
            elif col == 'green':
                glow.v1 = GREEN.r * HDRScale
                glow.v2 = GREEN.g * HDRScale
                glow.v3 = GREEN.b * HDRScale




    def GetMaterial(self):
        if self.model is None:
            self.LogWarn('GetMaterial - No model')
            return []
        res = []
        effects = nodemanager.FindNodes(self.model, 'Armor', 'trinity.Tr2Effect')
        for each in effects:
            for glow in nodemanager.FindNodes(each, 'GlowColor', 'trinity.TriVector4Parameter'):
                res.append(glow)


        return res



exports = {'spaceObject.DeployableSpaceObject': DeployableSpaceObject}

