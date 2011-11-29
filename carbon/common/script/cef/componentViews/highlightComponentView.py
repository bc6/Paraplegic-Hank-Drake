import cef

class HighlightComponentView(cef.BaseComponentView):
    __guid__ = 'cef.HighlightComponentView'
    __COMPONENT_ID__ = const.cef.HIGHLIGHT_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Highlight'
    __COMPONENT_CODE_NAME__ = 'highlight'
    CURVE_RES_PATH = 'curveResPath'
    HIGHLIGHT_AREAS = 'highlightAreas'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.CURVE_RES_PATH, '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Curve Res Path')
        cls._AddInput(cls.HIGHLIGHT_AREAS, '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Highlight Areas')



HighlightComponentView.SetupInputs()

