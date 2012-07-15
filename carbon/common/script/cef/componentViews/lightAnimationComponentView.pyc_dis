#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/cef/componentViews/lightAnimationComponentView.py
import cef

class LightAnimationComponentView(cef.BaseComponentView):
    __guid__ = 'cef.LightAnimationComponentView'
    __COMPONENT_ID__ = const.cef.LIGHT_ANIMATION_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Light Animation Curveset'
    __COMPONENT_CODE_NAME__ = 'LightAnimationComponent'
    __SHOULD_SPAWN__ = {'client': True}
    RED_FILE = 'resPath'
    ANIMATION_LENGTH = 'length'
    START_DELAY = 'startDelay'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.RED_FILE, '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Red File')
        cls._AddInput(cls.ANIMATION_LENGTH, 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Animation Length')
        cls._AddInput(cls.START_DELAY, 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Start Delay')


LightAnimationComponentView.SetupInputs()