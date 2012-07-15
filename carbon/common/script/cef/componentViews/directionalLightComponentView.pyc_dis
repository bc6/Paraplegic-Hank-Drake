#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/cef/componentViews/directionalLightComponentView.py
import cef

class DirectionalLightComponentView(cef.BaseComponentView, cef.LightComponentViewMixin):
    __guid__ = 'cef.DirectionalLightComponentView'
    __COMPONENT_ID__ = const.cef.DIRECTIONAL_LIGHT_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'DirectionalLight'
    __COMPONENT_CODE_NAME__ = 'directionalLight'
    __SHOULD_SPAWN__ = {'client': True}
    __DESCRIPTION__ = 'A directional light. It is basically a direction and a color.'
    COLOR = ('red', 'green', 'blue')
    KELVINCOLOR = ('temperature', 'tint', 'whiteBalance')

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.COLOR, (1.0, 1.0, 1.0), cls.RECIPE, const.cef.COMPONENTDATA_COLOR_TYPE, displayName='Color')
        cls._AddInput('specularIntensity', 1.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Specular Intensity')
        cls._AddInput('primaryLighting', 1, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Primary Lighting')
        cls._AddInput('secondaryLighting', 1, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Secondary Lighting')
        cls._AddInput('secondaryLightingMultiplier', 1.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Secondary Lighting Multiplier')
        cls._AddInput('isStatic', 1, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Is Static')
        cls._AddInput('useKelvinColor', 0, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Use Kelvin Color')
        cls._AddInput(cls.KELVINCOLOR, (5500.0, 0.5, 2), cls.RECIPE, const.cef.COMPONENTDATA_KELVIN_COLOR_TYPE, displayName='Kelvin Color')
        cls._AddInput('useExplicitBounds', 0, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Use Explicit Bounds')
        cls._AddInput('explicitBoundsMin', '(-1.0,-1.0,-1.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='Explicit Bounds Min')
        cls._AddInput('explicitBoundsMax', '(1.0,1.0,1.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='Explicit Bounds Max')
        cls._AddInput('affectTransparentObjects', 1, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Affect Transparent Objects')
        cls._AddInput('shadowResolution', 256, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetShadowResolutionEnum, displayName='Shadow Resolution', sortEnum=False)
        cls._AddInput('shadowCasterTypes', 3, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetShadowCasterTypesEnum, displayName='Shadow Caster Types', sortEnum=False)
        cls._AddInput('shadowImportance', 1.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Shadow Importance')
        cls._AddInput('LODDistribution', 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='LOD Distribution')
        cls._AddInput('shadowLODs', 1, cls.RECIPE, const.cef.COMPONENTDATA_INT_TYPE, displayName='Shadow LODs')
        cls._AddInput('LODBlendRegion', 0.2, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='LOD Blend Region')
        cls._AddInput('direction', '(0.0,-1.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='Direction')


DirectionalLightComponentView.SetupInputs()