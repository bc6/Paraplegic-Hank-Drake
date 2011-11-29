import service
import blue
import audio2
import trinity
import collections
import uthread
import GameWorld
import audio
import weakref
import funcDeco
import log

def Audio2JukeboxCallback(*args):
    for arg in args:
        sm.StartService('audio').OnWiseJukeboxEvent(arg)



DEFAULT_OBSTRUCTION_POLL_INTERVAL = 250
PAPERDOLL_SWITCH_GROUPS = ['Jacket', 'Pants', 'Boots']
LANGUAGE_ID_TO_BANK = {'DE': u'German/',
 'RU': u'Russian/'}

class AudioService(service.Service):
    __guid__ = 'svc.audio'
    __sessionparams__ = []
    __exportedcalls__ = {'Activate': [],
     'Deactivate': [],
     'GetMasterVolume': [],
     'SetMasterVolume': [],
     'GetUIVolume': [],
     'SetUIVolume': [],
     'GetWorldVolume': [],
     'SetWorldVolume': [],
     'SetMusicVolume': [],
     'IsActivated': []}
    __startupdependencies__ = ['settings']
    __notifyevents__ = []
    __componentTypes__ = ['audioEmitter']

    def __init__(self):
        service.Service.__init__(self)
        self.AppInit()



    def Run(self, ms = None):
        self.active = False
        self.manager = audio2.GetManager()
        aPath = blue.os.ResolvePath(u'res:/Audio')
        io = audio2.AudLowLevelIO(aPath, LANGUAGE_ID_TO_BANK.get(session.languageID, u''))
        initConf = audio2.AudConfig()
        initConf.lowLevelIO = io
        initConf.numRefillsInVoice = 8
        initConf.asyncFileOpen = True
        self.manager.config = initConf
        self.banksLoaded = False
        enabled = self.AppGetSetting('audioEnabled', 1)
        self.uiPlayer = self.jukeboxPlayer = None
        self.busChannels = {}
        for i in xrange(8):
            self.busChannels[i] = None

        self.audioEmitterComponentsByScene = collections.defaultdict(dict)
        self.audioEmitterPositionsByComponent = {}
        self.audioEmitterComponentGroupsByScene = collections.defaultdict(lambda : collections.defaultdict(list))
        trinity.SetDirectSoundPtr(audio2.GetDirectSoundPtr())
        self.AppRun()
        if enabled:
            self.Activate()
        self.obstructionPollThreadWR = None



    def StartPolling(self, pollInterval = DEFAULT_OBSTRUCTION_POLL_INTERVAL):
        if self.obstructionPollThreadWR and self.obstructionPollThreadWR():
            return 
        pollingTasklet = uthread.new(self._PollAudioPositions, pollInterval)
        pollingTasklet.context = 'AudioService::_PollAudioPositions'
        self.obstructionPollThreadWR = weakref.ref(pollingTasklet)



    def StopPolling(self):
        if self.obstructionPollThreadWR and self.obstructionPollThreadWR():
            self.obstructionPollThreadWR().kill()
            self.obstructionPollThreadWR = None



    def _PollAudioPositions(self, pollInterval = DEFAULT_OBSTRUCTION_POLL_INTERVAL):
        entityClient = sm.GetService('entityClient')
        gameWorldClient = sm.GetService('gameWorldClient')
        gps = sm.GetService('gps')
        while True:
            gameWorld = None
            playerPos = None
            sceneID = None
            player = entityClient.GetPlayerEntity()
            if player and player.HasComponent('position') and session.worldspaceid:
                playerPos = player.GetComponent('position').position
                gameWorld = gameWorldClient.GetGameWorld(session.worldspaceid)
                sceneID = player.scene.sceneID
            if playerPos and gameWorld and sceneID:
                audioEntities = set(self.audioEmitterPositionsByComponent.values()).intersection(self.audioEmitterComponentsByScene[sceneID].values())
                for audioEntity in audioEntities:
                    src = self.audioEmitterPositionsByComponent[audioEntity].position
                    p = None
                    if gps.GetEntityDistanceSquaredFromPoint(player, src) > 1e-05:
                        p = gameWorld.MultiHitLineTestWithMaterials(src, playerPos)
                    if p:
                        obstruction = len(p) * (1 / 5.0)
                        if obstruction > 1.0:
                            obstruction = 1.0
                        audioEntity.emitter.SetObstructionAndOcclusion(0, obstruction, 0.0)
                    else:
                        audioEntity.emitter.SetObstructionAndOcclusion(0, 0.0, 0.0)

            blue.pyos.synchro.SleepWallclock(pollInterval)




    def Stop(self, stream):
        self.uiPlayer = None
        self.jukeboxPlayer = None
        self.AppStop()



    def SetGlobalRTPC(self, rtpcName, value):
        if not self.IsActivated():
            return 
        audio2.SetGlobalRTPC(unicode(rtpcName), value)



    def OnWiseJukeboxEvent(self, eventName):
        sm.ScatterEvent('OnWiseJukeboxEventReceived', eventName)



    def Activate(self):
        self.manager.SetEnabled(True)
        if self.uiPlayer is None:
            self.uiPlayer = audio2.GetUIPlayer()
        if self.jukeboxPlayer is None:
            self.jukeboxPlayer = audio2.GetJukebox()
            jukeboxEventHandler = blue.os.CreateInstance('blue.BlueEventToPython')
            jukeboxEventHandler.handler = Audio2JukeboxCallback
            self.jukeboxPlayer.eventListener = jukeboxEventHandler
        if not self.banksLoaded:
            self.manager.LoadBank(u'Init.bnk')
            self.AppLoadBanks()
            self.banksLoaded = True
        self.active = True
        self.AppActivate()
        try:
            self.AppSetListener(audio2.GetListener(0))
        except:
            pass
        sm.ScatterEvent('OnAudioActivated')



    def Deactivate(self):
        self.manager.SetEnabled(False)
        self.AppDeactivate()
        self.active = False
        sm.ScatterEvent('OnAudioDeactivated')



    def GetAudioBus(self, is3D = False):
        for (outputChannel, emitterWeakRef,) in self.busChannels.iteritems():
            if emitterWeakRef is None:
                emitter = audio2.AudEmitter('Bus Channel: ' + str(outputChannel))
                if is3D:
                    emitter.SendEvent(unicode('Play_3d_audio_stream_' + str(outputChannel)))
                else:
                    emitter.SendEvent(unicode('Play_2d_audio_stream_' + str(outputChannel)))
                self.busChannels[outputChannel] = weakref.ref(emitter, self.AudioBusDeathCallback)
                return (emitter, outputChannel)

        log.logError('Bus voice starvation!')
        return (None, -1)



    @funcDeco.CallInNewThread(context='^AudioService::AudioBusDeathCallback')
    def AudioBusDeathCallback(self, audioEmitter):
        blue.synchro.SleepWallclock(2000)
        for (outputChannel, emitterWeakRef,) in self.busChannels.iteritems():
            if emitterWeakRef == audioEmitter:
                self.busChannels[outputChannel] = None




    def SetMasterVolume(self, vol = 1.0, persist = True):
        if vol < 0.0 or vol > 1.0:
            raise RuntimeError('Erroneous value received for volume')
        self.SetGlobalRTPC(unicode('volume_master'), vol)
        if persist:
            self.AppSetSetting('masterVolume', vol)



    def GetMasterVolume(self):
        return self.AppGetSetting('masterVolume', 0.4)



    def SetUIVolume(self, vol = 1.0, persist = True):
        if vol < 0.0 or vol > 1.0:
            raise RuntimeError('Erroneous value received for volume')
        self.SetGlobalRTPC(unicode('volume_ui'), vol)
        if persist:
            self.AppSetSetting('uiGain', vol)



    def GetUIVolume(self):
        return self.AppGetSetting('uiGain', 0.4)



    def SetWorldVolume(self, vol = 1.0, persist = True):
        if vol < 0.0 or vol > 1.0:
            raise RuntimeError('Erroneous value received for volume')
        self.SetGlobalRTPC(unicode('volume_world'), vol)
        if persist:
            self.AppSetSetting('worldVolume', vol)



    def GetWorldVolume(self):
        return self.AppGetSetting('worldVolume', 0.4)



    def SetMusicVolume(self, volume = 1.0, persist = True):
        volume = min(1.0, max(0.0, volume))
        self.SetGlobalRTPC(unicode('volume_music'), volume)
        if persist:
            self.AppSetSetting('eveampGain', volume)



    def IsActivated(self):
        return self.active



    def SendEntityEventBySoundID(self, entity, soundID):
        if not entity:
            log.LogError('Trying to play an audio on an entity but got None sent in instead of entity instance')
            return 
        if not self.IsActivated():
            self.LogInfo('Audio inactive - skipping sound id', soundID)
            return 
        audioEmitterComponent = entity.GetComponent('audioEmitter')
        soundEventName = cfg.sounds.GetIfExists(soundID)
        if audioEmitterComponent and soundEventName:
            if soundEventName.startswith('wise:/'):
                soundEventName = soundEventName[6:]
            audioEmitterComponent.emitter.SendEvent(unicode(soundEventName))
        elif not audioEmitterComponent:
            log.LogError('Trying to play audio', soundID, 'on entity', entity.entityID, 'that does not have an audioEmitter component')
        else:
            log.LogError('Could not find audio resource with ID', soundID)



    def SendEntityEvent(self, entity, event):
        if not entity:
            log.LogError('Trying to play an audio on an entity but got None sent in instead of entity instance')
            return 
        if not self.IsActivated():
            self.LogInfo('Audio inactive - skipping sound event', event)
            return 
        if event.startswith('wise:/'):
            event = event[6:]
        audioEmitterComponent = entity.GetComponent('audioEmitter')
        if audioEmitterComponent:
            audioEmitterComponent.emitter.SendEvent(unicode(event))
        else:
            log.LogError('Trying to play audio on entity', entity.entityID, 'that does not have an audioEmitter component')



    def SendUIEvent(self, event):
        if not self.IsActivated():
            self.LogInfo('Audio inactive - skipping UI event', event)
            return 
        if event.startswith('wise:/'):
            event = event[6:]
        self.LogInfo('Sending UI event to WWise:', event)
        self.uiPlayer.SendEvent(unicode(event))



    def SendJukeboxEvent(self, event):
        if not self.IsActivated():
            self.LogWarn('Audio inactive - skipping jukebox event', event)
            return 
        if event.startswith('wise:/'):
            event = event[6:]
        self.LogInfo('Sending Jukebox event to WWise:', event)
        self.jukeboxPlayer.SendEvent(unicode(event))



    def PlayJukeboxTrack(self, track):
        if not self.IsActivated():
            self.LogWarn('Audio inactive - skipping play track request', track)
            return 
        self.LogInfo('Playing Jukebox track', track)
        self.jukeboxPlayer.Play(unicode(track))



    def AppInit(self):
        pass



    def AppRun(self):
        pass



    def AppStop(self):
        pass



    def AppLoadBanks(self):
        pass



    def AppSetListener(self, listener):
        pass



    def AppActivate(self):
        pass



    def AppDeactivate(self):
        pass



    def AppMessage(self, message):
        pass



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



    def CreateComponent(self, name, state):
        component = audio.AudioEmitterComponent()
        component.initialEventName = state.get(audio.INITIAL_EVENT_NAME, None)
        component.initialSoundID = state.get(audio.INITIAL_SOUND_ID, None)
        component.groupName = state.get(audio.EMITTER_GROUP_NAME, None)
        if component.groupName == '':
            component.groupName = None
        component.emitter = None
        return component



    def PackUpForSceneTransfer(self, component, destinationSceneID):
        state = {}
        if component.initialEventName:
            state[audio.INITIAL_EVENT_NAME] = component.initialEventName
        if component.initialSoundID:
            state[audio.INITIAL_SOUND_ID] = component.initialSoundID
        if component.groupName:
            state[audio.EMITTER_GROUP_NAME] = component.groupName
        return True



    def UnPackFromSceneTransfer(self, component, entity, state):
        component.initialEventName = state.get(audio.INITIAL_EVENT_NAME, None)
        component.initialSoundID = state.get(audio.INITIAL_SOUND_ID, None)
        component.groupName = state.get(audio.EMITTER_GROUP_NAME, None)
        if component.groupName == '':
            component.groupName = None
        return component



    def SetupComponent(self, entity, component):
        self.audioEmitterComponentsByScene[entity.scene.sceneID][entity.entityID] = component
        component.positionObserver = None
        if component.groupName is None:
            component.emitter = audio2.AudEmitter('AudEmitter_' + str(entity.entityID))
            positionComponent = entity.GetComponent('position')
            if positionComponent:
                self.audioEmitterPositionsByComponent[component] = positionComponent
                component.positionObserver = GameWorld.PlacementObserverWrapper(component.emitter)
                positionComponent.RegisterPlacementObserverWrapper(component.positionObserver)
        else:
            groupedEntities = self.audioEmitterComponentGroupsByScene[entity.scene.sceneID][component.groupName]
            if len(groupedEntities) == 0:
                component.emitter = audio2.AudEmitterMulti('Multi_' + str(component.groupName))
                component.positionObserver = GameWorld.MultiPlacementObserverWrapper(component.emitter)
            else:
                component.emitter = groupedEntities[0].emitter
                component.positionObserver = groupedEntities[0].positionObserver
            groupedEntities.append(component)
            positionComponent = entity.GetComponent('position')
            if positionComponent:
                component.positionObserver.AddPositionComponent(positionComponent)
        if component.initialEventName:
            component.emitter.SendEvent(unicode(component.initialEventName))
        if component.initialSoundID:
            sound = cfg.sounds.GetIfExists(component.initialSoundID)
            if sound:
                component.emitter.SendEvent(unicode(sound.soundFile[6:]))



    def RegisterComponent(self, entity, component):
        paperdollComponent = entity.GetComponent('paperdoll')
        if paperdollComponent and paperdollComponent.doll and paperdollComponent.doll.GetDoll():

            def OnPaperdollUpdateDoneClosure():
                if component and paperdollComponent and paperdollComponent.doll:
                    self.UpdateComponentSwitchesWithDoll(component, paperdollComponent.doll)


            paperdollComponent.doll.GetDoll().AddUpdateDoneListener(OnPaperdollUpdateDoneClosure)



    def UpdateComponentSwitchesWithDoll(self, audioEmitter, doll):
        newSwitches = {}
        for switchGroup in PAPERDOLL_SWITCH_GROUPS:
            newSwitches[switchGroup] = 'None'

        for switchID in doll.GetDoll().buildDataManager.GetSoundTags():
            switch = cfg.sounds.GetIfExists(switchID)
            if switch and switch.soundFile.find('state:/') == 0:
                switchNames = switch.soundFile[7:].split('_')
                switchGroup = switchNames[0]
                switchType = switchNames[1]
                newSwitches[switchGroup] = switchType

        for (switchGroup, switchType,) in newSwitches.iteritems():
            audioEmitter.emitter.SetSwitch(unicode(switchGroup), unicode(switchType))




    def UnRegisterComponent(self, entity, component):
        del self.audioEmitterComponentsByScene[entity.scene.sceneID][entity.entityID]
        if component in self.audioEmitterPositionsByComponent:
            del self.audioEmitterPositionsByComponent[component]
        if component.groupName is None:
            positionComponent = entity.GetComponent('position')
            if positionComponent and component.positionObserver:
                positionComponent.UnRegisterPlacementObserverWrapper(component.positionObserver)
            component.emitter.SendEvent(u'fade_out')
            component.emitter = None
        else:
            groupedEntities = self.audioEmitterComponentGroupsByScene[entity.scene.sceneID][component.groupName]
            if component in groupedEntities:
                groupedEntities.remove(component)
            if len(groupedEntities) == 0:
                positionComponent = entity.GetComponent('position')
                if positionComponent and component.positionObserver:
                    component.positionObserver.RemovePositionComponent(positionComponent)
                component.emitter.SendEvent(u'fade_out')
                component.emitter = None
                del self.audioEmitterComponentGroupsByScene[entity.scene.sceneID][component.groupName]



    def OnEntitySceneLoaded(self, sceneID):
        uthread.new(self.SetupPlayerListener)
        self.StartPolling()



    def SetupPlayerListener(self):
        camera = sm.GetService('cameraClient').GetActiveCamera()
        if camera:
            camera.audio2Listener = audio2.GetListener(0)



    def OnEntitySceneUnloaded(self, sceneID):
        for component in self.audioEmitterComponentsByScene[sceneID]:
            component.emitter.SendEvent(u'fade_out')
            component.emitter = None

        if sceneID in self.audioEmitterComponentGroupsByScene:
            del self.audioEmitterComponentGroupsByScene[sceneID]
        if sceneID in self.audioEmitterComponentsByScene:
            del self.audioEmitterComponentsByScene[sceneID]
        self.StopPolling()



    def ReportState(self, component, entity):
        state = collections.OrderedDict()
        state['Initial Sound ID'] = component.initialSoundID
        state['Initial Event Name'] = component.initialEventName
        state['Group Name'] = component.groupName
        return state




