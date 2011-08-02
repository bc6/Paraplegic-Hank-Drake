import cef

class ShipHologramComponentView(cef.BaseComponentView):
    __guid__ = 'cef.ShipHologramComponentView'
    __COMPONENT_ID__ = const.cef.SHIP_HOLOGRAM_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Ship Hologram'
    __COMPONENT_CODE_NAME__ = 'shipHologram'
    POSITION_OFFSET = 'positionOffset'
    SPOTLIGHT_ORIGIN = 'spotlightOrigin'
    SHIP_TARGET_SIZE = 'shipTargetSize'
    COLOR = 'color'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.SHIP_TARGET_SIZE, 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE)
        cls._AddInput(cls.POSITION_OFFSET, '(0.0,0.0,0.0)', cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE)
        cls._AddInput(cls.SPOTLIGHT_ORIGIN, '(0.0,0.0,0.0)', cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE)
        cls._AddInput(cls.COLOR, '(0.0,0.0,0.0)', cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE)



ShipHologramComponentView.SetupInputs()

