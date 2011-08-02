import cef

class AnimationComponentView(cef.BaseComponentView):
    __guid__ = 'cef.AnimationComponentView'
    __COMPONENT_ID__ = const.cef.ANIMATION_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Animation'
    __COMPONENT_CODE_NAME__ = 'animation'
    UPDATER = 'updater'
    CONTROLLER = 'controller'
    POSE_STATE = 'poseState'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.UPDATER, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE)
        cls._AddInput(cls.CONTROLLER, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE)
        cls._AddInput(cls.POSE_STATE, '', cls.RUNTIME, const.cef.COMPONENTDATA_STRING_TYPE)



AnimationComponentView.SetupInputs()

