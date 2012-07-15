#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/cef/componentViews/animationComponentView.py
import cef

class AnimationComponentView(cef.BaseComponentView):
    __guid__ = 'cef.AnimationComponentView'
    __COMPONENT_ID__ = const.cef.ANIMATION_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Animation'
    __COMPONENT_CODE_NAME__ = 'animation'
    __COMPONENT_DEPENDENCIES__ = [const.cef.POSITION_COMPONENT_ID, const.cef.INFO_COMPONENT_ID]
    UPDATER = 'updater'
    CONTROLLER = 'controller'
    POSE_STATE = 'poseState'
    RES_PATH = 'resPath'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.UPDATER, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE, displayName='Updater')
        cls._AddInput(cls.CONTROLLER, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE, displayName='Controller')
        cls._AddInput(cls.POSE_STATE, '', cls.RUNTIME, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Pose State')
        cls._AddInput(cls.RES_PATH, None, cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='animation network', fileTypes='MOR Files (*.mor)|*.mor')


AnimationComponentView.SetupInputs()