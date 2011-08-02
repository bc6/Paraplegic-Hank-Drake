import cef

class MovementComponentView(cef.BaseComponentView):
    __guid__ = 'cef.MovementComponentView'
    __COMPONENT_ID__ = const.cef.MOVEMENT_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Movement'
    __COMPONENT_CODE_NAME__ = 'movement'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)



MovementComponentView.SetupInputs()

