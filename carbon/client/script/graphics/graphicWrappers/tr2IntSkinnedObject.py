import util
import trinity
import graphicWrappers

class Tr2IntSkinnedObject(util.BlueClassNotifyWrap('trinity.Tr2IntSkinnedObject'), graphicWrappers.WodExtSkinnedObject):
    __guid__ = 'graphicWrappers.Tr2IntSkinnedObject'

    @staticmethod
    def Wrap(triObject, resPath):
        Tr2IntSkinnedObject(triObject)
        triObject.InitTransformMatrixMixinWrapper()
        triObject.AddNotify('transform', triObject._TransformChange)
        return triObject




