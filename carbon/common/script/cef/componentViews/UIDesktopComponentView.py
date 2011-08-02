import cef

class UIDesktopComponentView(cef.BaseComponentView):
    __guid__ = 'cef.UIDesktopComponentView'
    __COMPONENT_ID__ = const.cef.UIDESKTOP_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'UIDesktop'
    __COMPONENT_CODE_NAME__ = 'UIDesktopComponent'
    UI_DESKTOP_NAME = 'uiDesktopName'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.UI_DESKTOP_NAME, '', cls.MANDATORY, const.cef.COMPONENTDATA_STRING_TYPE)



UIDesktopComponentView.SetupInputs()

