import spaceObject
import trinity
import audio2

class Stargate(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.Stargate'

    def LoadModel(self, fileName = None, useInstance = False):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        filename = cfg.invtypes.Get(slimItem.typeID).GraphicFile()
        filename = self.GetTrinityVersionFilename(filename)
        spaceObject.SpaceObject.LoadModel(self, filename, useInstance)
        self.SetStaticRotation()



    def Assemble(self):
        if hasattr(self.model, 'ChainAnimationEx'):
            self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        self.SetupAmbientAudio(u'worldobject_jumpgate_atmo_play')



exports = {'spaceObject.Stargate': Stargate}

