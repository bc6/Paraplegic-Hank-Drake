import geo2
import trinity
import util
import weakref
import graphicWrappers

class Tr2InteriorOccluder(util.BlueClassNotifyWrap('trinity.Tr2InteriorOccluder'), graphicWrappers.TrinityTransformMatrixMixinWrapper):
    __guid__ = 'graphicWrappers.Tr2InteriorOccluder'

    @staticmethod
    def Wrap(triObject, resPath):
        Tr2InteriorOccluder(triObject)
        triObject.InitTransformMatrixMixinWrapper()
        triObject.AddNotify('transform', triObject._TransformChange)
        triObject.cellName = ''
        triObject.scene = None
        return triObject



    def SetCell(self, cellName):
        if self.cellName != cellName:
            self.cellName = cellName
            if self.scene and self.scene():
                self.AddToScene(self.scene())



    def AddToScene(self, scene):
        if self.scene and self.scene():
            scene.RemoveOccluder(self)
        scene.AddOccluder(self, self.cellName)
        self.scene = weakref.ref(scene)



    def RemoveFromScene(self, scene):
        scene.RemoveOccluder(self)
        self.scene = None
        self.cellName = None



    def _TransformChange(self, transform):
        self.OnTransformChange()



    def OnTransformChange(self):
        pass



    def OnPositionChange(self):
        pass



    def OnRotationChange(self):
        pass



    def OnScaleChange(self):
        pass




