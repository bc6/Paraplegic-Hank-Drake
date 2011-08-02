import cef

class LoadedLightComponentView(cef.BaseComponentView):
    __guid__ = 'cef.LoadedLightComponentView'
    __COMPONENT_ID__ = const.cef.LOADED_LIGHT_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Loaded Light'
    __COMPONENT_CODE_NAME__ = 'loadedLight'
    RED_FILE = 'resPath'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.RED_FILE, '', cls.MANDATORY, const.cef.COMPONENTDATA_STRING_TYPE)



LoadedLightComponentView.SetupInputs()

