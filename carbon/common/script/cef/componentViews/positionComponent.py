import cef

class PositionComponentView(cef.BaseComponentView):
    __guid__ = 'cef.PositionComponentView'
    __COMPONENT_ID__ = const.cef.POSITION_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Position'
    __COMPONENT_CODE_NAME__ = 'position'
    POS = 'position'
    ROT = 'rotation'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.POS, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE)
        cls._AddInput(cls.ROT, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE)



PositionComponentView.SetupInputs()

