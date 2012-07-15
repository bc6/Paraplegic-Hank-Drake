#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/environment/spaceObject/billboard.py
import spaceObject
import nodemanager
import uthread
import trinity
import sys
import blue

class Billboard(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.Billboard'

    def __init__(self):
        spaceObject.SpaceObject.__init__(self)

    def Assemble(self):
        self.UnSync()
        uthread.pool('Billboard::LateAssembleUpdate', self.LateAssembleUpdate)

    def LateAssembleUpdate(self):
        billboardSvc = sm.GetService('billboard')
        billboardSvc.Update(self)

    def SetMap(self, name, path, idx = 0):
        if path is None:
            return
        self.LogInfo('Setting', name, 'to', path)
        self.model.FreezeHighDetailMesh()
        try:
            textureParameters = self.model.Find('trinity.TriTexture2DParameter')
            texture = [ x for x in textureParameters if x.name == name ][idx]
            texture.resourcePath = path
        except (Exception,) as e:
            self.LogError('SetMap() - Error updating billboard map', name, path, e)
            sys.exc_clear()

    def UpdateBillboardContents(self, advertPath, facePath):
        self.LogInfo('UpdateBillboardWithPictureAndText:', advertPath, facePath)
        if self.model is None:
            return
        self.SetMap('FaceMap', facePath)
        self.SetMap('AdvertMap', advertPath)
        self.SetMap('DiffuseMap', 'cache:/Temp/headlines.dds', 1)
        self.SetMap('DiffuseMap', 'cache:/Temp/bounty_caption.dds')

    def Release(self):
        if self.released:
            return
        spaceObject.SpaceObject.Release(self)


exports = {'spaceObject.Billboard': Billboard}