#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/graphicWrappers/tr2InteriorProbeVolume.py
import geo2
import trinity
import util
import weakref
import graphicWrappers

class Tr2InteriorProbeVolume(util.BlueClassNotifyWrap('trinity.Tr2InteriorProbeVolume'), graphicWrappers.TrinityTransformMatrixMixinWrapper):
    __guid__ = 'graphicWrappers.Tr2InteriorProbeVolume'

    @staticmethod
    def Wrap(triObject, resPath):
        Tr2InteriorProbeVolume(triObject)
        triObject.InitTransformMatrixMixinWrapper()
        triObject.AddNotify('transform', triObject._TransformChange)
        triObject.cellName = ''
        triObject.scene = None
        return triObject

    def SetCell(self, cellName):
        if self.cellName != cellName:
            if self.scene and self.scene():
                self.scene().RemoveProbeVolume(self)
            self.cellName = cellName
            if self.scene and self.scene():
                self.AddToScene(self.scene())

    def AddToScene(self, scene):
        if self.scene and self.scene():
            scene.RemoveProbeVolume(self)
        scene.AddProbeVolume(self, self.cellName)
        self.scene = weakref.ref(scene)

    def RemoveFromScene(self, scene):
        scene.RemoveProbeVolume(self)
        self.scene = None

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

    def SetResolution(self, res):
        self.resolutionX, self.resolutionY, self.resolutionZ = res