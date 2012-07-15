#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/cef/componentViews/lensFlareView.py
import cef

class LensFlareComponentView(cef.BaseComponentView):
    __guid__ = 'cef.LensFlareComponentView'
    __COMPONENT_ID__ = const.cef.LENS_FLARE_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Lens Flare'
    __COMPONENT_CODE_NAME__ = 'lensFlare'
    __SHOULD_SPAWN__ = {'client': True}
    RED_FILE = 'redFile'
    POSITION_OFFSET = 'positionOffset'
    COLOR = 'color'
    OCCLUDER_SIZE = 'occluderSize'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.RED_FILE, '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Red File')
        cls._AddInput(cls.OCCLUDER_SIZE, 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Occluder Size')
        cls._AddInput(cls.POSITION_OFFSET, '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='Position Offset')
        cls._AddInput(cls.COLOR, '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='Color')


LensFlareComponentView.SetupInputs()