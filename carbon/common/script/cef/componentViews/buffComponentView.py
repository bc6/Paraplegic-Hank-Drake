import cef

class BuffComponentView(cef.BaseComponentView):
    __guid__ = 'cef.BuffComponentView'
    __COMPONENT_ID__ = const.cef.BUFF_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Buff'
    __COMPONENT_CODE_NAME__ = 'buff'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)



BuffComponentView.SetupInputs()

