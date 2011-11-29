import cef
DEFAULT_SCALE = 1.0

class BoxLightComponentView(cef.BaseComponentView, cef.LightComponentViewMixin):
    __guid__ = 'cef.BoxLightComponentView'
    __COMPONENT_ID__ = const.cef.BOX_LIGHT_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'BoxLight'
    __COMPONENT_CODE_NAME__ = 'boxLight'
    __SHOULD_SPAWN__ = {'client': True}
    __DESCRIPTION__ = 'Parameters for a trinity box light'
    COLOR = ('red', 'green', 'blue')
    KELVINCOLOR = ('temperature', 'tint', 'whiteBalance')

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.COLOR, (1.0, 1.0, 1.0), cls.RECIPE, const.cef.COMPONENTDATA_COLOR_TYPE, displayName='Color')
        cls._AddInput('scaleX', DEFAULT_SCALE, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='X Scale')
        cls._AddInput('scaleY', DEFAULT_SCALE, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Y Scale')
        cls._AddInput('scaleZ', DEFAULT_SCALE, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Z Scale')
        cls._AddInput('falloff', 30.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Falloff')
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
        cls._AddInput('useKelvinColor', 0, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Use Kelvin Color')
        cls._AddInput(cls.KELVINCOLOR, (5500.0, 0.5, 2), cls.RECIPE, const.cef.COMPONENTDATA_KELVIN_COLOR_TYPE, displayName='Kelvin Color')
        cls._AddInput('performanceLevel', 0, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetPerformanceEnum, displayName='Performance Level', sortEnum=False)
        cls._AddInput('useBoundingBox', 0, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Use Bounding Box')
        cls._AddInput('bbPos', '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='BB Position')
        cls._AddInput('bbRot', '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='BB Rotation')
        cls._AddInput('bbScale', '(1.0,1.0,1.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='BB Scale')



BoxLightComponentView.SetupInputs()

