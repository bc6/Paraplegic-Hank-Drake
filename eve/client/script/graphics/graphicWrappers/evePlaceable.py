import util
import trinity
import graphicWrappers

class WodPlaceableRes(object):
    __guid__ = 'graphicWrappers.WodPlaceableRes'

    @staticmethod
    def Wrap(triObject, resPath):
        returnObject = trinity.WodPlaceable()
        returnObject.placeableResPath = resPath
        return WodPlaceable.Wrap(returnObject, resPath)



    @staticmethod
    def ConvertToInterior(triObject, resPath):
        returnObject = trinity.Tr2InteriorPlaceable()
        returnObject.placeableResPath = resPath
        return returnObject




class WodPlaceable(util.BlueClassNotifyWrap('trinity.WodPlaceable'), graphicWrappers.TrinityTransformMatrixMixinWrapper):
    __guid__ = 'graphicWrappers.WodPlaceable'

    @staticmethod
    def Wrap(triObject, resPath):
        WodPlaceable(triObject)
        triObject.AddNotify('transform', triObject._TransformChange)
        return triObject



    @staticmethod
    def ConvertToInterior(triObject, resPath):
        returnObject = trinity.Tr2InteriorPlaceable()
        returnObject.placeableResPath = triObject.placeableResPath
        return returnObject



    def AddToScene(self, scene):
        scene.AddPlaceableToScene(self)



    def RemoveFromScene(self, scene):
        scene.RemovePlaceableFromScene(self)



    def _TransformChange(self, transform):
        self.OnTransformChange()



    def OnTransformChange(self):
        pass




