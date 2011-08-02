import cef

class InteriorStaticComponentView(cef.BaseComponentView):
    __guid__ = 'cef.InteriorStaticComponentView'
    __COMPONENT_ID__ = const.cef.INTERIOR_STATIC_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'InteriorStatic'
    __COMPONENT_CODE_NAME__ = 'interiorStatic'
    GRAPHIC_ID = 'graphicID'
    CELL_ID = 'cellID'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.GRAPHIC_ID, -1, cls.OPTIONAL, const.cef.COMPONENTDATA_GRAPHIC_ID_TYPE, displayName='Graphic ID')
        cls._AddInput(cls.CELL_ID, '', cls.SPAWN_MANDATORY, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Cell ID')



InteriorStaticComponentView.SetupInputs()

