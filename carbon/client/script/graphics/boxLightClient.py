import blue
import collections
import geo2
import graphics
import graphicWrappers
import service
import trinity
import uthread

class BoxLightClientComponent:
    __guid__ = 'component.BoxLightClientComponent'


class BoxLightClient(graphics.LightClient):
    __guid__ = 'svc.boxLightClient'
    __componentTypes__ = ['boxLight']

    def CreateComponent(self, name, state):
        component = BoxLightClientComponent()
        renderObject = trinity.Tr2InteriorBoxLight()
        component.renderObject = renderObject
        graphicWrappers.Wrap(renderObject)
        component.originalPrimaryLighting = state.GetPrimaryLighting()
        component.originalSecondaryLighting = state.GetSecondaryLighting()
        component.performanceLevel = state.GetPerformanceLevel()
        renderObject.SetColor(state.GetColor())
        renderObject.SetScaling(state.GetScaling())
        renderObject.SetFalloff(state.GetFalloff())
        renderObject.shadowImportance = state.GetShadowImportance()
        renderObject.primaryLighting = component.originalPrimaryLighting
        renderObject.secondaryLighting = component.originalSecondaryLighting
        renderObject.secondaryLightingMultiplier = state.GetSecondaryLightingMultiplier()
        renderObject.affectTransparentObjects = state.GetAffectTransparentObjects()
        renderObject.shadowResolution = state.GetShadowResolution()
        renderObject.shadowCasterTypes = state.GetShadowCasterTypes()
        renderObject.projectedTexturePath = state.GetProjectedTexturePath().encode()
        renderObject.isStatic = state.GetIsStatic()
        renderObject.importanceScale = state.GetImportanceScale()
        renderObject.importanceBias = state.GetImportanceBias()
        renderObject.enableShadowLOD = state.GetEnableShadowLOD()
        renderObject.cellIntersectionType = state.GetCellIntersectionType()
        renderObject.useKelvinColor = state.GetUseKelvinColor()
        renderObject.kelvinColor.temperature = state.GetKelvinColorTemperature()
        renderObject.kelvinColor.tint = state.GetKelvinColorTint()
        renderObject.kelvinColor.whiteBalance = state.GetKelvinColorWhiteBalance()
        component.originalShadowCasterTypes = state.GetShadowCasterTypes()
        return component



    def ApplyShadowCasterType(self, entity):
        component = entity.GetComponent('boxLight')
        if component is None:
            return 
        dynamicShadows = sm.GetService('device').GetAppFeatureState('Interior.dynamicShadows', True)
        shadowCasters = trinity.Tr2InteriorShadowCasterTypes
        if dynamicShadows:
            component.renderObject.shadowCasterTypes = component.originalShadowCasterTypes
        elif component.originalShadowCasterTypes == shadowCasters.DynamicOnly:
            component.renderObject.shadowCasterTypes = shadowCasters.None
        elif component.originalShadowCasterTypes == shadowCasters.All:
            component.renderObject.shadowCasterTypes = shadowCasters.StaticsOnly



    def ApplyPerformanceLevelLightDisable(self, entity):
        component = entity.GetComponent('boxLight')
        if component is None:
            return 
        appPerformanceLevel = sm.GetService('device').GetAppFeatureState('Interior.lightPerformanceLevel', 2)
        if component.performanceLevel > appPerformanceLevel:
            component.renderObject.primaryLighting = False
            component.renderObject.secondaryLighting = False
        else:
            component.renderObject.primaryLighting = component.originalPrimaryLighting
            component.renderObject.secondaryLighting = component.originalSecondaryLighting




