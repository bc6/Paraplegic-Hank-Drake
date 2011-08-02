import cef

class SpotLightComponentView(cef.BaseComponentView):
    __guid__ = 'cef.SpotLightComponentView'
    __COMPONENT_ID__ = const.cef.SPOT_LIGHT_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'SpotLight'
    __COMPONENT_CODE_NAME__ = 'spotLight'
    COLOR = ('red', 'green', 'blue')
    KELVINCOLOR = ('temperature', 'tint', 'whiteBalance')

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.COLOR, (1.0, 1.0, 1.0), cls.MANDATORY, const.cef.COMPONENTDATA_COLOR_TYPE, displayName='Color')
        cls._AddInput('radius', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Radius')
        cls._AddInput('coneDirectionX', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='X Direction')
        cls._AddInput('coneDirectionY', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Y Direction')
        cls._AddInput('coneDirectionZ', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Z Direction')
        cls._AddInput('coneAlphaInner', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Inner Angle')
        cls._AddInput('coneAlphaOuter', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Outer Angle')
        cls._AddInput('falloff', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Falloff')
        cls._AddInput('shadowImportance', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Shadow Importance')
        cls._AddInput('primaryLighting', 0, cls.MANDATORY, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Primary Lighting')
        cls._AddInput('secondaryLighting', 0, cls.MANDATORY, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Secondary Lighting')
        cls._AddInput('secondaryLightingMultiplier', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Secondary Lighting Multipler')
        cls._AddInput('affectTransparentObjects', 0, cls.MANDATORY, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Affect Transparent Objects')
        cls._AddInput('shadowResolution', 0, cls.MANDATORY, const.cef.COMPONENTDATA_INT_TYPE, displayName='Shadow Resolution')
        cls._AddInput('shadowCasterTypes', 0, cls.MANDATORY, const.cef.COMPONENTDATA_INT_TYPE, displayName='Shadow Caster Types')
        cls._AddInput('projectedTexturePath', '', cls.MANDATORY, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Projected Texture Path')
        cls._AddInput('isStatic', 0, cls.MANDATORY, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Is Static')
        cls._AddInput('importanceScale', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Importance Scale')
        cls._AddInput('importanceBias', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Importance Bias')
        cls._AddInput('enableShadowLOD', 0, cls.MANDATORY, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Enable Shadow LOD')
        cls._AddInput('cellIntersectionType', 0, cls.MANDATORY, const.cef.COMPONENTDATA_INT_TYPE, displayName='Cell Intersection Type')
        cls._AddInput('useKelvinColor', 0, cls.MANDATORY, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Use Kelvin Color')
        cls._AddInput(cls.KELVINCOLOR, (5500.0, 0.5, 2), cls.MANDATORY, const.cef.COMPONENTDATA_KELVIN_COLOR_TYPE, displayName='Kelvin Color')



SpotLightComponentView.SetupInputs()

