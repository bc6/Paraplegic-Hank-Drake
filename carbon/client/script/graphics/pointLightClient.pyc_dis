#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/pointLightClient.py
import cef
import graphics
import graphicWrappers
import trinity
import util

class PointLightClientComponent:
    __guid__ = 'component.PointLightClientComponent'


class PointLightClient(graphics.LightClient):
    __guid__ = 'svc.pointLightClient'
    __componentTypes__ = [cef.PointLightComponentView.GetComponentCodeName()]

    def CreateComponent(self, name, state):
        component = PointLightClientComponent()
        renderObject = trinity.Tr2InteriorLightSource()
        component.renderObject = renderObject
        graphicWrappers.Wrap(renderObject)
        component.originalPrimaryLighting = bool(state['primaryLighting'])
        component.originalSecondaryLighting = bool(state['secondaryLighting'])
        component.performanceLevel = state['performanceLevel']
        renderObject.SetColor((state['red'], state['green'], state['blue']))
        renderObject.SetRadius(state['radius'])
        renderObject.SetFalloff(state['falloff'])
        renderObject.shadowImportance = state['shadowImportance']
        renderObject.primaryLighting = bool(state['primaryLighting'])
        renderObject.secondaryLighting = bool(state['secondaryLighting'])
        renderObject.secondaryLightingMultiplier = state['secondaryLightingMultiplier']
        renderObject.affectTransparentObjects = bool(state['affectTransparentObjects'])
        renderObject.shadowResolution = int(state['shadowResolution'])
        renderObject.shadowCasterTypes = int(state['shadowCasterTypes'])
        renderObject.projectedTexturePath = state['projectedTexturePath'].encode()
        renderObject.isStatic = bool(state['isStatic'])
        renderObject.importanceScale = state['importanceScale']
        renderObject.importanceBias = state['importanceBias']
        renderObject.enableShadowLOD = bool(state['enableShadowLOD'])
        renderObject.specularIntensity = float(state.get('specularIntensity', '1'))
        renderObject.useKelvinColor = bool(state['useKelvinColor'])
        customMaterialResPath = state.get('customMaterialPath', '')
        if customMaterialResPath != '':
            renderObject.customMaterial = trinity.Load(customMaterialResPath)
        renderObject.useKelvinColor = bool(state['useKelvinColor'])
        if renderObject.useKelvinColor:
            renderObject.kelvinColor.temperature = state['temperature']
            renderObject.kelvinColor.tint = state['tint']
            renderObject.kelvinColor.whiteBalance = int(state['whiteBalance'])
        component.originalShadowCasterTypes = renderObject.shadowCasterTypes
        component.useBoundingBox = bool(state['useBoundingBox'])
        if component.useBoundingBox:
            component.bbPos = util.UnpackStringToTuple(state['bbPos'])
            component.bbRot = util.UnpackStringToTuple(state['bbRot'])
            component.bbScale = util.UnpackStringToTuple(state['bbScale'])
            renderObject.boundingBox = trinity.Tr2InteriorOrientedBoundingBox()
        component.renderObject.name = self.GetName(state['_spawnID'])
        return component

    def ApplyShadowCasterType(self, entity):
        component = entity.GetComponent('pointLight')
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
        component = entity.GetComponent('pointLight')
        if component is None:
            return
        appPerformanceLevel = sm.GetService('device').GetAppFeatureState('Interior.lightPerformanceLevel', 2)
        if component.performanceLevel > appPerformanceLevel:
            component.renderObject.primaryLighting = False
            component.renderObject.secondaryLighting = False
        else:
            component.renderObject.primaryLighting = component.originalPrimaryLighting
            component.renderObject.secondaryLighting = component.originalSecondaryLighting