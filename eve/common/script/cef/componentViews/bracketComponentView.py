import cef

class BracketComponentView(cef.BaseComponentView):
    __guid__ = 'cef.BracketComponentView'
    __COMPONENT_ID__ = const.cef.BRACKET_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Bracket'
    __COMPONENT_CODE_NAME__ = 'bracket'
    MAX_WIDTH = 'maxWidth'
    MAX_HEIGHT = 'maxHeight'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.MAX_WIDTH, 0.0, cls.OPTIONAL, const.cef.COMPONENTDATA_FLOAT_TYPE)
        cls._AddInput(cls.MAX_HEIGHT, 0.0, cls.OPTIONAL, const.cef.COMPONENTDATA_FLOAT_TYPE)



BracketComponentView.SetupInputs()

