#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/cef/componentViews/pointLightComponentView.py
import cef
DEFAULT_RADIUS = 10.0

class PointLightComponentView(cef.BaseComponentView, cef.LightComponentViewMixin):
    __guid__ = 'cef.PointLightComponentView'
    __COMPONENT_ID__ = const.cef.POINT_LIGHT_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'PointLight'
    __COMPONENT_CODE_NAME__ = 'pointLight'
    __SHOULD_SPAWN__ = {'client': True}
    __DESCRIPTION__ = 'Parameters for a trinity point light'
    COLOR = ('red', 'green', 'blue')
    KELVINCOLOR = ('temperature', 'tint', 'whiteBalance')

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.COLOR, (1.0, 1.0, 1.0), cls.RECIPE, const.cef.COMPONENTDATA_COLOR_TYPE, displayName='Color')
        cls._AddInput('radius', DEFAULT_RADIUS, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Radius')
        cls._AddInput('falloff', 1.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Falloff')
        cls._AddInput('specularIntensity', 1.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Specular Intensity')
        cls._AddInput('shadowImportance', 1.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Shadow Importance')
        cls._AddInput('primaryLighting', 1, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Primary Lighting')
        cls._AddInput('secondaryLighting', 1, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Secondary Lighting')
        cls._AddInput('secondaryLightingMultiplier', 1.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Secondary Lighting Multiplier')
        cls._AddInput('affectTransparentObjects', 1, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Affect Transparent Objects')
        cls._AddInput('shadowResolution', 256, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetShadowResolutionEnum, displayName='Shadow Resolution', sortEnum=False)
        cls._AddInput('shadowCasterTypes', 3, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetShadowCasterTypesEnum, displayName='Shadow Caster Types', sortEnum=False)
        cls._AddInput('projectedTexturePath', '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Projected Texture Path')
        cls._AddInput('isStatic', 1, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Is Static')
        cls._AddInput('importanceScale', 1.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Importance Scale')
        cls._AddInput('importanceBias', 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Importance Bias')
        cls._AddInput('enableShadowLOD', 1, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Enable Shadow LOD')
        cls._AddInput('cellIntersectionType', 0, cls.RECIPE, const.cef.COMPONENTDATA_INT_TYPE, displayName='Cell Intersection Type')
        cls._AddInput('useKelvinColor', 0, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Use Kelvin Color')
        cls._AddInput(cls.KELVINCOLOR, (5500.0, 0.5, 2), cls.RECIPE, const.cef.COMPONENTDATA_KELVIN_COLOR_TYPE, displayName='Kelvin Color')
        cls._AddInput('customMaterialPath', '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Custom Material Path')
        cls._AddInput('performanceLevel', 0, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetPerformanceEnum, displayName='Performance Level', sortEnum=False)
        cls._AddInput('performanceLevel', 0, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetPerformanceEnum, displayName='Performance Level', sortEnum=False)
        cls._AddInput('useBoundingBox', 0, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Use Bounding Box')
        cls._AddInput('bbPos', '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='BB Position')
        cls._AddInput('bbRot', '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='BB Rotation')
        cls._AddInput('bbScale', '(1.0,1.0,1.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='BB Scale')


PointLightComponentView.SetupInputs()