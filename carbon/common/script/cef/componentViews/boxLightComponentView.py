import cef

class BoxLightComponentView(cef.BaseComponentView):
    __guid__ = 'cef.BoxLightComponentView'
    __COMPONENT_ID__ = const.cef.BOX_LIGHT_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'BoxLight'
    __COMPONENT_CODE_NAME__ = 'boxLight'
    COLOR = ('red', 'green', 'blue')
    KELVINCOLOR = ('temperature', 'tint', 'whiteBalance')

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.COLOR, (1.0, 1.0, 1.0), cls.MANDATORY, const.cef.COMPONENTDATA_COLOR_TYPE)
        cls._AddInput('scaleX', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE)
        cls._AddInput('scaleY', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE)
        cls._AddInput('scaleZ', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE)
        cls._AddInput('falloff', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE)
        cls._AddInput('shadowImportance', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE)
        cls._AddInput('primaryLighting', 0, cls.MANDATORY, const.cef.COMPONENTDATA_BOOL_TYPE)
        cls._AddInput('secondaryLighting', 0, cls.MANDATORY, const.cef.COMPONENTDATA_BOOL_TYPE)
        cls._AddInput('secondaryLightingMultiplier', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE)
        cls._AddInput('affectTransparentObjects', 0, cls.MANDATORY, const.cef.COMPONENTDATA_BOOL_TYPE)
        cls._AddInput('shadowResolution', 0, cls.MANDATORY, const.cef.COMPONENTDATA_INT_TYPE)
        cls._AddInput('shadowCasterTypes', 0, cls.MANDATORY, const.cef.COMPONENTDATA_INT_TYPE)
        cls._AddInput('projectedTexturePath', '', cls.MANDATORY, const.cef.COMPONENTDATA_STRING_TYPE)
        cls._AddInput('isStatic', 0, cls.MANDATORY, const.cef.COMPONENTDATA_BOOL_TYPE)
        cls._AddInput('importanceScale', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE)
        cls._AddInput('importanceBias', 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE)
        cls._AddInput('enableShadowLOD', 0, cls.MANDATORY, const.cef.COMPONENTDATA_BOOL_TYPE)
        cls._AddInput('useKelvinColor', 0, cls.MANDATORY, const.cef.COMPONENTDATA_BOOL_TYPE)
        cls._AddInput(cls.KELVINCOLOR, (5500.0, 0.5, 2), cls.MANDATORY, const.cef.COMPONENTDATA_KELVIN_COLOR_TYPE)



BoxLightComponentView.SetupInputs()

