import cef

class AudioEmitterComponentView(cef.BaseComponentView):
    __guid__ = 'cef.AudioEmitterComponentView'
    __COMPONENT_ID__ = const.cef.AUDIO_EMMITTER_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Audio Emitter'
    __COMPONENT_CODE_NAME__ = 'audioEmitter'
    EVENT_NAME = 'initialEventName'
    SOUND_ID = 'initialSoundID'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.EVENT_NAME, '', cls.OPTIONAL, const.cef.COMPONENTDATA_STRING_TYPE)
        cls._AddInput(cls.SOUND_ID, -1, cls.OPTIONAL, const.cef.COMPONENTDATA_ID_TYPE)



AudioEmitterComponentView.SetupInputs()

