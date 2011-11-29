import cef

class ApertureComponentView(cef.BaseComponentView):
    __guid__ = 'cef.ApertureComponentView'
    __COMPONENT_ID__ = const.cef.APERTURE_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Aperture'
    __COMPONENT_CODE_NAME__ = 'aperture'
    FLAGS = 'flags'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.FLAGS, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE, displayName='Flags')



ApertureComponentView.SetupInputs()

