import svc
import blue
import sys
import log
import trinity

class EveAudioService(svc.audio):
    __guid__ = 'svc.eveAudio'
    __replaceservice__ = 'audio'
    __exportedcalls__ = svc.audio.__exportedcalls__
    __exportedcalls__.update({'PlaySound': [],
     'AudioMessage': [],
     'SendUIEvent': [],
     'SendJukeboxEvent': [],
     'StartSoundLoop': [],
     'StopSoundLoop': [],
     'GetTurretSuppression': [],
     'SetTurretSuppression': [],
     'GetVoiceVolume': [],
     'SetVoiceVolume': [],
     'MuteSounds': [],
     'UnmuteSounds': []})
    __notifyevents__ = ['OnDamageStateChange']

    def AppInit(self):
        self.soundLoops = {}
        self.soundNotificationSent = [False, False, False]



    def AppRun(self):
        if blue.win32 and trinity.device and uicore.uilib:
            try:
                blue.win32.WTSRegisterSessionNotification(trinity.device.GetWindow(), 0)
                uicore.uilib.SessionChangeHandler = self.OnUserSessionChange
            except:
                sys.exc_clear()
                uicore.uilib.SessionChangeHandler = None



    def AppStop(self):
        if blue.win32 and trinity.device:
            try:
                blue.win32.WTSUnRegisterSessionNotification(trinity.device.GetWindow())
            except:
                sys.exc_clear()
        if uicore.uilib:
            uicore.uilib.SessionChangeHandler = None



    def OnUserSessionChange(self, wp, lp):
        if not self.IsActivated():
            return 
        if wp == 1:
            sm.GetService('vivox').OnSessionReconnect()
            if self.IsActivated() and self.GetMasterVolume() > 0.0:
                self.SetMasterVolume(self.GetMasterVolume(), persist=True)
        elif wp == 2:
            sm.GetService('vivox').OnSessionDisconnect()
            if self.IsActivated() and self.GetMasterVolume() > 0.0:
                self.SetMasterVolume(0.0, persist=False)



    def AppLoadBanks(self):
        self.manager.LoadBank(u'Effects.bnk')
        self.manager.LoadBank(u'Interface.bnk')
        self.manager.LoadBank(u'Modules.bnk')
        self.manager.LoadBank(u'ShipEffects.bnk')
        self.manager.LoadBank(u'Turrets.bnk')
        self.manager.LoadBank(u'Atmos.bnk')
        self.manager.LoadBank(u'Boosters.bnk')
        self.manager.LoadBank(u'Music.bnk')
        self.manager.LoadBank(u'Placeables.bnk')
        self.manager.LoadBank(u'Voice.bnk')
        self.manager.LoadBank(u'CharacterCreation.bnk')
        self.manager.LoadBank(u'Hangar.bnk')
        self.manager.LoadBank(u'Planets.bnk')
        self.manager.LoadBank(u'Incarna.bnk')



    def AppSetListener(self, listener):
        sm.GetService('sceneManager').GetRegisteredCamera(None, defaultOnActiveCamera=True).audio2Listener = listener
        sm.GetService('cameraClient').SetAudioListener(listener)



    def AppActivate(self):
        self.SetMasterVolume(self.GetMasterVolume())
        self.SetUIVolume(self.GetUIVolume())
        self.SetWorldVolume(self.GetWorldVolume())
        self.SetVoiceVolume(self.GetVoiceVolume())
        self.SetTurretSuppression(self.GetTurretSuppression())



    def PlayFootfallForEntity(self, entity):
        import materialTypes
        namesByID = {}
        for (name, ID,) in materialTypes.MATERIAL_NAMES.iteritems():
            namesByID[ID] = name

        if not entity:
            return 
        positionComponent = entity.GetComponent('position')
        audioEmitterComponent = entity.GetComponent('audioEmitter')
        if not positionComponent or not audioEmitterComponent:
            return 
        gameWorld = sm.GetService('gameWorldClient').GetGameWorld(session.worldspaceid)
        if not gameWorld:
            return 
        topPosition = (positionComponent.position[0], positionComponent.position[1] + 0.1, positionComponent.position[2])
        bottomPosition = (positionComponent.position[0], positionComponent.position[1] - 0.2, positionComponent.position[2])
        hitResult = gameWorld.MultiHitLineTestWithMaterials(topPosition, bottomPosition)
        if hitResult:
            audioEmitterComponent.emitter.SetSwitch(u'Materials', namesByID[hitResult[0][2]])
            audioEmitterComponent.emitter.SendEvent(u'footfall_loud_play')
        else:
            audioEmitterComponent.emitter.SetSwitch(u'Materials', u'Invalid')
            audioEmitterComponent.emitter.SendEvent(u'footfall_loud_play')



    def PlaySound(self, audioFile, streamed = False, loop = False, gain = -1, pan = -1, fadeInStart = 0, fadeInTime = 0, fadeOutStart = 0, fadeOutTime = 0, cookie = 0, callback = None, early = 0):
        if not self.IsActivated():
            return 
        if audioFile.startswith('wise:/'):
            self.SendUIEvent(audioFile[6:])
        else:
            self.LogError('REPORT THIS DEFECT: Audio Service ignoring a non-Wise event:', audioFile)
            log.LogTraceback('Non-wise event received: %s' % audioFile)



    def AudioMessage(self, msg, dict, prioritize = 0):
        if not self.IsActivated():
            return 
        if msg.audio:
            audiomsg = msg.audio
        else:
            return 
        if audiomsg.startswith('wise:/'):
            audiomsg = audiomsg[6:]
            self.SendUIEvent(audiomsg)
        else:
            self.LogError('REPORT THIS DEFECT: Old UI sound being played, msg:', msg, 'dict:', dict)
            log.LogTraceback('OLD UI SOUND BEING PLAYED: %s' % msg)



    def StartSoundLoop(self, rootLoopMsg):
        if not self.IsActivated():
            return 
        try:
            if rootLoopMsg not in self.soundLoops:
                self.LogInfo('StartSoundLoop starting loop with root %s' % rootLoopMsg)
                self.soundLoops[rootLoopMsg] = 1
                self.SendUIEvent('wise:/msg_%s_play' % rootLoopMsg)
            else:
                self.soundLoops[rootLoopMsg] += 1
                self.LogInfo('StartSoundLoop incrementing %s loop to %d' % (rootLoopMsg, self.soundLoops[rootLoopMsg]))
        except:
            self.LogWarn('StartSoundLoop failed - halting loop with root', rootLoopMsg)
            self.SendUIEvent('wise:/msg_%s_stop' % rootLoopMsg)
            sys.exc_clear()



    def StopSoundLoop(self, rootLoopMsg, eventMsg = None):
        if rootLoopMsg not in self.soundLoops:
            self.LogWarn('StopSoundLoop told to halt', rootLoopMsg, 'but that message is not playing!')
            return 
        try:
            self.soundLoops[rootLoopMsg] -= 1
            if self.soundLoops[rootLoopMsg] <= 0:
                self.LogInfo('StopSoundLoop halting message with root', rootLoopMsg)
                del self.soundLoops[rootLoopMsg]
                self.SendUIEvent('wise:/msg_%s_stop' % rootLoopMsg)
            else:
                self.LogInfo('StopSoundLoop decremented count of loop with root %s to %d' % (rootLoopMsg, self.soundLoops[rootLoopMsg]))
        except:
            self.LogWarn('StopSoundLoop failed due to an exception - forcibly halting', rootLoopMsg)
            self.SendUIEvent('wise:/msg_%s_stop' % rootLoopMsg)
            sys.exc_clear()
        if eventMsg is not None:
            self.SendUIEvent(eventMsg)



    def SetVoiceVolume(self, vol = 1.0, persist = True):
        if vol < 0.0 or vol > 1.0:
            raise RuntimeError('Erroneous value received for volume')
        if not self.IsActivated():
            return 
        self.SetGlobalRTPC('volume_voice', vol)
        if persist:
            self.AppSetSetting('evevoiceGain', vol)



    def GetVoiceVolume(self):
        return self.AppGetSetting('evevoiceGain', 0.9)



    def GetTurretSuppression(self):
        return self.AppGetSetting('suppressTurret', 0)



    def SetTurretSuppression(self, suppress, persist = True):
        if not self.IsActivated():
            return 
        if suppress:
            self.SetGlobalRTPC('turret_muffler', 0.0)
            suppress = 1
        else:
            self.SetGlobalRTPC('turret_muffler', 1.0)
            suppress = 0
        if persist:
            self.AppSetSetting('suppressTurret', suppress)



    def AppMessage(self, message, **kwargs):
        eve.Message(message, **kwargs)



    def AppGetSetting(self, setting, default):
        try:
            return settings.public.audio.Get(setting, default)
        except (AttributeError, NameError):
            return default



    def AppSetSetting(self, setting, value):
        try:
            settings.public.audio.Set(setting, value)
        except (AttributeError, NameError):
            pass



    def MuteSounds(self):
        self.SetMasterVolume(0.0, False)



    def UnmuteSounds(self):
        self.SetMasterVolume(self.GetMasterVolume(), False)



    def OnDamageStateChange(self, shipID, damageState):
        if session.shipid != shipID:
            return 
        for i in xrange(0, 3):
            soundEvent = None
            enabled = settings.user.notifications.Get(const.soundNotificationVars[i][0], 1)
            if not enabled:
                continue
            shouldNotify = damageState[i] <= settings.user.notifications.Get(const.soundNotificationVars[i][1], const.soundNotificationVars[i][2])
            alreadyNotified = self.soundNotificationSent[i]
            if shouldNotify and not alreadyNotified:
                self.soundNotificationSent[i] = True
                soundEvent = const.damageSoundNotifications[i]
            if alreadyNotified:
                self.soundNotificationSent[i] = shouldNotify
                continue
            if soundEvent is not None:
                self.SendUIEvent(soundEvent)





