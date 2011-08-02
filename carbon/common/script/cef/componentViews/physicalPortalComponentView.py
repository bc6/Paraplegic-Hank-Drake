import cef

class PhysicalPortalComponentView(cef.BaseComponentView):
    __guid__ = 'cef.PhysicalPortalComponentView'
    __COMPONENT_ID__ = const.cef.PHYSICAL_PORTAL_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Physical Portal'
    __COMPONENT_CODE_NAME__ = 'physicalPortal'
    SCALE_X = 'scaleX'
    SCALE_Y = 'scaleY'
    SCALE_Z = 'scaleZ'
    CELL_A = 'cellA'
    CELL_B = 'cellB'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.SCALE_X, 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='X Scale')
        cls._AddInput(cls.SCALE_Y, 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Y Scale')
        cls._AddInput(cls.SCALE_Z, 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Z Scale')
        cls._AddInput(cls.CELL_A, None, cls.SPAWN_MANDATORY, const.cef.COMPONENTDATA_CELL_TYPE, displayName='Cell A')
        cls._AddInput(cls.CELL_B, None, cls.SPAWN_MANDATORY, const.cef.COMPONENTDATA_CELL_TYPE, displayName='Cell B')



PhysicalPortalComponentView.SetupInputs()

