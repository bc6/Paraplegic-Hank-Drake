#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/cef/componentViews/shipHologramView.py
import cef

class ShipHologramComponentView(cef.BaseComponentView):
    __guid__ = 'cef.ShipHologramComponentView'
    __COMPONENT_ID__ = const.cef.SHIP_HOLOGRAM_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Ship Hologram'
    __COMPONENT_CODE_NAME__ = 'shipHologram'
    __SHOULD_SPAWN__ = {'client': True}
    POSITION_OFFSET = 'positionOffset'
    SPOTLIGHT_ORIGIN = 'spotlightOrigin'
    SHIP_TARGET_SIZE = 'shipTargetSize'
    COLOR = 'color'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.SHIP_TARGET_SIZE, 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Ship Target Size')
        cls._AddInput(cls.POSITION_OFFSET, '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='Position Offset')
        cls._AddInput(cls.SPOTLIGHT_ORIGIN, '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='Spotlight Origin')
        cls._AddInput(cls.COLOR, '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='Color')


ShipHologramComponentView.SetupInputs()