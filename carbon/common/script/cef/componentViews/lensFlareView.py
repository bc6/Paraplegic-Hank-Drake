import cef

class LensFlareComponentView(cef.BaseComponentView):
    __guid__ = 'cef.LensFlareComponentView'
    __COMPONENT_ID__ = const.cef.LENS_FLARE_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Lens Flare'
    __COMPONENT_CODE_NAME__ = 'lensFlare'
    RED_FILE = 'redFile'
    POSITION_OFFSET = 'positionOffset'
    COLOR = 'color'
    OCCLUDER_SIZE = 'occluderSize'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.RED_FILE, '', cls.MANDATORY, const.cef.COMPONENTDATA_STRING_TYPE)
        cls._AddInput(cls.OCCLUDER_SIZE, 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE)
        cls._AddInput(cls.POSITION_OFFSET, '(0.0,0.0,0.0)', cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE)
        cls._AddInput(cls.COLOR, '(0.0,0.0,0.0)', cls.OPTIONAL, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE)



LensFlareComponentView.SetupInputs()

