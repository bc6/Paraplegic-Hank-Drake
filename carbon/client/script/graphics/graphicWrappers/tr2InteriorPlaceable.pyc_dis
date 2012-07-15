#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/graphicWrappers/tr2InteriorPlaceable.py
import graphicWrappers
import util
import weakref

class Tr2InteriorPlaceable(util.BlueClassNotifyWrap('trinity.Tr2InteriorPlaceable'), graphicWrappers.TrinityTransformMatrixMixinWrapper):
    __guid__ = 'graphicWrappers.Tr2InteriorPlaceable'

    @staticmethod
    def Wrap(triObject, resPath):
        Tr2InteriorPlaceable(triObject)
        triObject.InitTransformMatrixMixinWrapper()
        triObject.AddNotify('transform', triObject._TransformChange)
        triObject.scene = None
        return triObject

    def AddToScene(self, scene):
        if self.scene and self.scene():
            self.RemoveFromScene(self.scene())
        scene.AddDynamicToScene(self)
        self.scene = weakref.ref(scene)

    def RemoveFromScene(self, scene):
        scene.RemoveDynamicFromScene(self)
        self.scene = None

    def _TransformChange(self, transform):
        self.InitTransformMatrixMixinWrapper()
        self.OnTransformChange()

    def IsLoading(self):
        if self.placeableRes:
            if self.placeableRes.visualModel and util.IsTr2ModelLoading(self.placeableRes.visualModel):
                return True
        return False

    def OnTransformChange(self):
        pass

    def OnPositionChange(self):
        pass

    def OnRotationChange(self):
        pass

    def OnScaleChange(self):
        pass