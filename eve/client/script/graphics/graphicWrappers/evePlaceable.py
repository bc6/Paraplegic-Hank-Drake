import util
import trinity
import graphicWrappers

def SwapShadersToInterior(obj):
    for mesh in obj.placeableRes.visualModel.meshes:
        for areaName in ('opaqueAreas', 'decalAreas', 'transparentAreas', 'additiveAreas'):
            areas = getattr(mesh, areaName)
            for area in areas:
                if 'default_glow_' in area.name.lower() or 'glow_default_' in area.name.lower():
                    if type(area.effect) is trinity.Tr2Effect:
                        area.effect.effectFilePath = 'res:/Graphics/Effect/Managed/Interior/Static/StaticStandardWithGlowSH.fx'
                    else:
                        area.effect.highLevelShaderName = 'StaticStandardWithGlowSH'
                elif type(area.effect) is trinity.Tr2Effect:
                    area.effect.effectFilePath = 'res:/Graphics/Effect/Managed/Interior/Static/StaticFresnelReflectionSH.fx'
                else:
                    area.effect.highLevelShaderName = 'StaticFresnelReflectionSH'






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
        SwapShadersToInterior(returnObject)
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
        SwapShadersToInterior(returnObject)
        return returnObject



    def AddToScene(self, scene):
        scene.AddPlaceableToScene(self)



    def RemoveFromScene(self, scene):
        scene.RemovePlaceableFromScene(self)



    def _TransformChange(self, transform):
        self.OnTransformChange()



    def OnTransformChange(self):
        pass




