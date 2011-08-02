import service
import moniker
import planet
import blue
import util
import uthread
import const

class SpaceAudioSvc(service.Service):
    __guid__ = 'svc.spaceAudioSvc'
    __servicename__ = 'spaceAudioSvc'
    __displayName__ = 'space audio'
    __notifyevents__ = []

    def Run(self, memStream = None):
        self.LogInfo('Starting space audio service')



    def GetSoundUrlForType(self, slimItem):
        soundUrl = sm.GetService('incursion').GetSoundUrlByKey(slimItem.groupID)
        if soundUrl is None:
            soundID = cfg.invtypes.Get(slimItem.typeID).soundID
            if soundID is not None:
                soundUrl = cfg.sounds.Get(soundID).soundFile
            self.LogInfo('Return default sound for ', slimItem.typeID, '=', soundUrl)
        else:
            self.LogInfo('Incursion overriding sound for typeID', slimItem.typeID, 'to', soundUrl)
        return soundUrl




