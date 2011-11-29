import cef

class PhysicalPortalComponentView(cef.BaseComponentView):
    __guid__ = 'cef.PhysicalPortalComponentView'
    __COMPONENT_ID__ = const.cef.PHYSICAL_PORTAL_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Physical Portal'
    __COMPONENT_CODE_NAME__ = 'physicalPortal'
    __SHOULD_SPAWN__ = {'client': True}
    __DESCRIPTION__ = 'A physical portal links two cells together visually'
    SCALE_X = 'scaleX'
    SCALE_Y = 'scaleY'
    SCALE_Z = 'scaleZ'
    CELL_A = 'cellA'
    CELL_B = 'cellB'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.SCALE_X, 1.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='X Scale')
        cls._AddInput(cls.SCALE_Y, 1.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Y Scale')
        cls._AddInput(cls.SCALE_Z, 1.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Z Scale')
        cls._AddInput((cls.CELL_A, cls.CELL_B), (None, None), cls.SPAWN_ONLY, const.cef.COMPONENTDATA_PORTAL_CELL_TYPE, displayName='Cells')



PhysicalPortalComponentView.SetupInputs()

