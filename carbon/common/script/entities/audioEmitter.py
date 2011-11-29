import util
INITIAL_EVENT_NAME = 'initialEventName'
INITIAL_SOUND_ID = 'initialSoundID'
EMITTER_GROUP_NAME = 'groupName'

class AudioEmitterComponent:
    __guid__ = 'audio.AudioEmitterComponent'

    def __init__(self):
        self.initialEventName = None
        self.initialSoundID = None
        self.groupName = None



exports = util.AutoExports('audio', locals())

