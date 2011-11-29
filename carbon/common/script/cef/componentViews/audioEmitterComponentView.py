import cef

class AudioEmitterComponentView(cef.BaseComponentView):
    __guid__ = 'cef.AudioEmitterComponentView'
    __COMPONENT_ID__ = const.cef.AUDIO_EMMITTER_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Audio Emitter'
    __COMPONENT_CODE_NAME__ = 'audioEmitter'
    __SHOULD_SPAWN__ = {'client': True}
    EVENT_NAME = 'initialEventName'
    SOUND_ID = 'initialSoundID'
    GROUP_NAME = 'groupName'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.EVENT_NAME, '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Initial Event Name')
        cls._AddInput(cls.SOUND_ID, -1, cls.RECIPE, const.cef.COMPONENTDATA_ID_TYPE, displayName='Initial Sound ID')
        cls._AddInput(cls.GROUP_NAME, '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Initial Group Name')



AudioEmitterComponentView.SetupInputs()

