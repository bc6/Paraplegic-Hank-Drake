import cef

class BracketComponentView(cef.BaseComponentView):
    __guid__ = 'cef.BracketComponentView'
    __COMPONENT_ID__ = const.cef.BRACKET_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Bracket'
    __COMPONENT_CODE_NAME__ = 'bracket'
    __SHOULD_SPAWN__ = {'client': True}
    MAX_WIDTH = 'maxWidth'
    MAX_HEIGHT = 'maxHeight'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.MAX_WIDTH, 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Max Width')
        cls._AddInput(cls.MAX_HEIGHT, 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Max Height')



BracketComponentView.SetupInputs()

