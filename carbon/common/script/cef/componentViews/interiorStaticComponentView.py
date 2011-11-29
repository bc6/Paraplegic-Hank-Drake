import cef

class InteriorStaticComponentView(cef.BaseComponentView):
    __guid__ = 'cef.InteriorStaticComponentView'
    __COMPONENT_ID__ = const.cef.INTERIOR_STATIC_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'InteriorStatic'
    __COMPONENT_CODE_NAME__ = 'interiorStatic'
    __SHOULD_SPAWN__ = {'client': True}
    __DESCRIPTION__ = 'Contains the graphicID, cell and handles the loading for static objects'
    GRAPHIC_ID = 'graphicID'
    CELL_NAME = 'cellName'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.GRAPHIC_ID, -1, cls.RECIPE, const.cef.COMPONENTDATA_GRAPHIC_ID_TYPE, displayName='Graphic ID')
        cls._AddInput(cls.CELL_NAME, 'DefaultCell', cls.SPAWN_ONLY, const.cef.COMPONENTDATA_CELL_TYPE, displayName='Cell Name')
        cls._AddInput('depthOffset', 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Transparency Depth Offset')



InteriorStaticComponentView.SetupInputs()

