#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/directionalLightClient.py
import cef
import graphics
import trinity
import util

class DirectionalLightClientComponent:
    __guid__ = 'component.DirectionalLightClientComponent'


class DirectionalLightClient(graphics.LightClient):
    __guid__ = 'svc.directionalLightClient'
    __componentTypes__ = [cef.DirectionalLightComponentView.GetComponentCodeName()]

    def CreateComponent(self, name, state):
        component = DirectionalLightClientComponent()
        renderObject = trinity.Tr2InteriorDirectionalLight()
        component.renderObject = renderObject
        renderObject.color = (state['red'], state['green'], state['blue'])
        renderObject.shadowImportance = state['shadowImportance']
        renderObject.primaryLighting = bool(state['primaryLighting'])
        renderObject.secondaryLighting = bool(state['secondaryLighting'])
        renderObject.secondaryLightingMultiplier = state['secondaryLightingMultiplier']
        renderObject.affectTransparentObjects = bool(state['affectTransparentObjects'])
        renderObject.shadowResolution = int(state['shadowResolution'])
        component.originalShadowCasterTypes = int(state['shadowCasterTypes'])
        renderObject.isStatic = bool(state['isStatic'])
        renderObject.specularIntensity = float(state.get('specularIntensity', '1'))
        renderObject.useKelvinColor = bool(state['useKelvinColor'])
        if renderObject.useKelvinColor:
            renderObject.kelvinColor.temperature = state['temperature']
            renderObject.kelvinColor.tint = state['tint']
            renderObject.kelvinColor.whiteBalance = int(state['whiteBalance'])
        renderObject.useExplicitBounds = bool(state['useExplicitBounds'])
        if renderObject.useExplicitBounds:
            renderObject.explicitBoundsMin = util.UnpackStringToTuple(state['explicitBoundsMin'])
            renderObject.explicitBoundsMax = util.UnpackStringToTuple(state['explicitBoundsMax'])
        renderObject.LODDistribution = state['LODDistribution']
        renderObject.shadowLODs = state['shadowLODs']
        renderObject.LODBlendRegion = state['LODBlendRegion']
        renderObject.direction = util.UnpackStringToTuple(state['direction'])
        component.renderObject.name = self.GetName(state['_spawnID'])
        return component

    def SetupComponent(self, entity, component):
        self.ApplyShadowCasterType(entity)

    def ApplyShadowCasterType(self, entity):
        component = entity.GetComponent('directionalLight')
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