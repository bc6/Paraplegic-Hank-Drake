#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/environment/eveVivoxService.py
import uthread
import svc
import service
import blue
import types
import moniker
import util
import vivox
import vivoxConstants
import uiconst
import localization

class EveVivoxService(svc.vivox):
    __guid__ = 'svc.evevivox'
    __servicename__ = 'evevivox'
    __replaceservice__ = 'vivox'
    __exportedcalls__ = {}
    __notifyevents__ = ['OnChannelsJoined', 'OnLSC']
    __notifyevents__.extend(svc.vivox.__notifyevents__)

    def AppRun(self, ms):
        self.fleetSpeakerCount = {}
        self.wingSpeakerCount = {}
        self.mutedParticipants = {}
        self.prettyChannelNames = {}
        self.gameSoundsMuted = False
        self.activeSpeakers = set()
        self.sendMessageOnLogIn = not self.Enabled()
        sm.RegisterNotify(self)

    def GetServerInfo(self):
        if eve.session.role & service.ROLE_GML:
            return self.vivoxServer

    def AppCanJoinChannel(self, eveChannelID, suppress = False):
        if type(eveChannelID) is types.TupleType:
            if type(eveChannelID[0]) is types.TupleType:
                eveChannelID = eveChannelID[0]
        if type(eveChannelID) is types.TupleType and eveChannelID[0] not in [const.vcPrefixFleet, const.vcPrefixWing, const.vcPrefixSquad] or type(eveChannelID) is types.IntType:
            virtualChannels = 0
            for each in self.members:
                for virtual in [const.vcPrefixFleet, const.vcPrefixWing, const.vcPrefixSquad]:
                    if virtual in each:
                        virtualChannels += 1

            if self.connector.ChannelJoinInProgressCount() - virtualChannels >= 2:
                eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Voice/TooManyChannels')})
                return False
        if type(eveChannelID) == types.TupleType:
            for key in self.members.keys():
                if type(eveChannelID[0]) == types.TupleType:
                    eveChannelID = eveChannelID[0]
                if eveChannelID[0] in key:
                    self.LeaveChannel(self.GetCcpChannelName(key))

        if self.connector.ChannelJoinInProgressCount() > 6:
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Voice/TooManyChannels')})
            return False
        return True

    def AppSetSpeakingChannel(self, eveChannelID):
        self.LogInfo('SetSpeakingChannel(', eveChannelID, ')')
        vivoxChannelName = self.GetVivoxChannelName(eveChannelID)
        isMuted = sm.GetService('fleet').IsVoiceMuted(eveChannelID)
        if self.IsVoiceChannel(eveChannelID) and isMuted == False and not self.gaggedAt.has_key(vivoxChannelName):
            if self.speakingChannel:
                if self.IsVoiceChannel(self.GetCcpChannelName(self.speakingChannel)):
                    self.SetTabColor(self.speakingChannel, 'listen')
                else:
                    self.SetTabColor(self.speakingChannel, None)
            uthread.pool('vivox::SetSpeakingChannel', self._SetSpeakingChannel, self.GetVivoxChannelName(eveChannelID), self.speakingChannel)
            self.speakingChannel = self.GetVivoxChannelName(eveChannelID)
            if eveChannelID == 'Echo':
                return
            self.SetTabColor(self.speakingChannel, 'speak')
        elif eveChannelID is None and self.speakingChannel:
            self.SetTabColor(self.speakingChannel, 'listen')
            uthread.pool('vivox::SetSpeakingChannel', self._SetSpeakingChannel, 'muted', self.speakingChannel)
            self.speakingChannel = None
        elif sm.GetService('fleet').IsVoiceMuted(eveChannelID) or self.gaggedAt.has_key(vivoxChannelName):
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Voice/MutedInChannel')})

    def _SetSpeakingChannel(self, vivoxChannelName, oldChannelName):
        self.LogInfo('_SetSpeakingChannel(', vivoxChannelName, ')')
        if vivoxChannelName == 'muted':
            self.connector.SetSpeakingChannel('')
        else:
            self.connector.SetSpeakingChannel(vivoxChannelName)
        if vivoxChannelName == 'Echo' or vivoxChannelName == 'muted':
            eveOldChannelID = self.GetCcpChannelName(oldChannelName)
            eveChannelID = None
            sm.ScatterEvent('OnVoiceSpeakingChannelSet', eveChannelID, eveOldChannelID)
        else:
            eveChannelID = self.GetCcpChannelName(vivoxChannelName)
            eveOldChannelID = self.GetCcpChannelName(oldChannelName)
            sm.ScatterEvent('OnVoiceSpeakingChannelSet', eveChannelID, eveOldChannelID)

    def AppGag(self, charID, eveChannelID, time):
        vivoxChannelName = self.GetVivoxChannelName(eveChannelID)
        if int(charID) == int(self.charid):
            self.gaggedAt[vivoxChannelName] = vivoxChannelName
            if self.GetSpeakingChannel() == eveChannelID:
                self.SetSpeakingChannel(None)
            self.LogInfo('I was gagged at', vivoxChannelName)
            blue.pyos.synchro.SleepWallclock(blue.os.TimeDiffInMs(blue.os.GetWallclockTime(), time))
            self.UnGag(charID, eveChannelID)
        else:
            self.LogInfo('someone was gagged at', charID, vivoxChannelName)

    def AppUnGag(self, charID, eveChannelID):
        vivoxChannelName = self.GetVivoxChannelName(eveChannelID)
        if int(charID) == int(self.charid) and vivoxChannelName in self.gaggedAt:
            self.gaggedAt.pop(vivoxChannelName)
            self.EnableGlobalPushToTalkMode('talk')
            self.LogInfo('I was ungagged at', vivoxChannelName)
            if self.GetSpeakingChannel() == 0:
                self.SetSpeakingChannel(eveChannelID)
        else:
            self.LogInfo('someone was ungagged at', charID, vivoxChannelName)

    def LeaderGagging(self, eveChannelID, leader, exclusionList, state):
        if self.LoggedIn():
            vivoxChannelName = self.GetVivoxChannelName(eveChannelID)
            if state == True:
                voiceIcon = 2
            else:
                voiceIcon = 0
            if self.members.has_key(vivoxChannelName):
                mutedParticipants = []
                for each in self.members[vivoxChannelName]:
                    if int(each[0]) not in exclusionList and int(each[0]) != leader:
                        self.members[vivoxChannelName][self.members[vivoxChannelName].index(each)] = [each[0], voiceIcon, each[2]]
                        mutedParticipants.append([each[0], voiceIcon, each[0]])

                if session.charid not in exclusionList:
                    if state == True and self.speakingChannel == vivoxChannelName:
                        self.LogInfo('Leader is gaging muting myself')
                        self.SetSpeakingChannel(None)
                    elif self.speakingChannel is None:
                        self.LogInfo('No longer muted')
                        self.SetSpeakingChannel(eveChannelID)
                wnd = sm.GetService('LSC').GetChannelWindow(eveChannelID)
                if wnd is not None:
                    wnd.RefreshVoiceStatus(mutedParticipants)

    def ExclusionChange(self, charid, eveChannelID, state):
        if self.LoggedIn():
            vivoxChannelName = self.GetVivoxChannelName(eveChannelID)
            if state == True:
                voiceIcon = 2
            else:
                voiceIcon = 0
            if self.members.has_key(vivoxChannelName):
                for each in self.members[vivoxChannelName]:
                    if int(each[0]) == charid:
                        self.members[vivoxChannelName][self.members[vivoxChannelName].index(each)] = [charid, voiceIcon, each[2]]
                        if charid == session.charid:
                            if state == True and self.speakingChannel == vivoxChannelName:
                                self.SetSpeakingChannel(None)
                            wnd = sm.GetService('LSC').GetChannelWindow(eveChannelID)
                            if wnd is not None:
                                wnd.RefreshVoiceStatus([[charid, voiceIcon, self.vivoxUserName]])

    def AppCreateAccountSendNotifyMessage(self):
        eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Voice/CreatingAccount')})

    def AppEnableGlobalPushToTalkMode(self, binding, key):
        self.LogInfo('EnableGlobalPushToTalkMode', binding, key)
        if key == None:
            key = settings.user.audio.Get('talkBinding', 4)
        if key == 1:
            key = 0
        inputValue = [(binding, key)]
        self.connector.EnableGlobalPushToTalkMode(inputValue)
        self.pushToTalkEnabled = True

    def AppDisableGlobalPushToTalkMode(self):
        self.connector.DisableGlobalPushToTalkMode()
        self.connector.Mute(1)
        self.pushToTalkEnabled = False

    def AppGetAvailableKeyBindings(self):
        availableKeyBindings = [(localization.GetByLabel('UI/Generic/None'), 1),
         (localization.GetByLabel('UI/SystemMenu/MiddleMouseButton'), 4),
         (localization.GetByLabel('UI/SystemMenu/LeftCtrl'), 162),
         (localization.GetByLabel('UI/SystemMenu/RightCtrl'), 163),
         (localization.GetByLabel('UI/SystemMenu/LeftAlt'), 164),
         (localization.GetByLabel('UI/SystemMenu/RightAlt'), 165),
         (localization.GetByLabel('UI/Generic/KeyPad0'), 96),
         (localization.GetByLabel('UI/SystemMenu/RightShift'), 161)]
        return availableKeyBindings

    def AppCanJoinEchoChannel(self):
        if len(self.members.keys()) != 0:
            if eve.Message('VoiceConfirmEcho', {}, uiconst.YESNO) == uiconst.ID_YES:
                return True
            else:
                return False
        return True

    def SetVoiceIcon(self, charid, vivoxChannelName, status):
        if vivoxChannelName not in self.members.keys():
            return
        participants = self.members[vivoxChannelName]
        for each in participants:
            if each[0] is charid:
                each[1] = status

        eveChannelName = self.GetCcpChannelName(vivoxChannelName)
        if type(eveChannelName) is types.TupleType:
            wnd = sm.GetService('LSC').GetChannelWindow((eveChannelName,))
        else:
            wnd = sm.GetService('LSC').GetChannelWindow(eveChannelName)
        if wnd:
            uthread.pool('eveVivoxService::SetVoiceIcon', wnd.VoiceIconChange, charid, status)

    def MoveToTop(self, eveCharid, eveChannelName):
        if settings.user.audio.Get('talkMoveToTopBtn', 0):
            wnd = sm.GetService('LSC').GetChannelWindow(eveChannelName)
            if wnd:
                wnd.MoveToTop(eveCharid)

    def SetTabColor(self, vivoxChannelName, color):
        if not vivoxChannelName:
            return
        eveChannelID = self.GetCcpChannelName(vivoxChannelName)
        wnd = sm.GetService('LSC').GetChannelWindow(eveChannelID)
        if not wnd:
            return
        icon = None
        tip = None
        if color:
            if color.lower() == 'speak':
                icon = 'ui_38_16_197'
                tip = localization.GetByLabel('UI/Voice/YouAreSpeaking')
            else:
                icon = 'ui_38_16_196'
                tip = localization.GetByLabel('UI/Voice/YouAreListening')
        wnd.SetHeaderIcon(icon, 12, tip)

    def TabNudge(self, eveChannelID):
        vivoxChannelName = self.GetVivoxChannelName(eveChannelID)
        if self.members.has_key(vivoxChannelName):
            if self.GetSpeakingChannel() == vivoxChannelName:
                self.SetTabColor(vivoxChannelName, 'speak')
            else:
                self.SetTabColor(vivoxChannelName, 'listen')

    def LeaveFleetChannels(self):
        if self.members:
            for each in [const.vcPrefixFleet,
             const.vcPrefixSquad,
             const.vcPrefixWing,
             const.vcPrefixFleet]:
                for channel in self.members:
                    if each in channel:
                        self.LeaveChannel(channel)

    def JoinFleetChannels(self):
        if not self.LoggedIn() or settings.user.audio.Get('talkAutoJoinFleet', 1) == 0:
            return
        if session.squadid > 0 and const.vcPrefixSquad + str(session.squadid) not in self.members:
            self.JoinChannel((const.vcPrefixSquad, session.squadid))
        if session.wingid > 0 and const.vcPrefixWing + str(session.wingid) not in self.members:
            self.JoinChannel((const.vcPrefixWing, session.wingid))
        if session.fleetid > 0 and const.vcPrefixFleet + str(session.fleetid) not in self.members:
            self.JoinChannel((const.vcPrefixFleet, session.fleetid))

    def ApplyChannelPriority(self, vivoxChannelName, speaker, isSpeaking):
        if const.vcPrefixFleet in vivoxChannelName:
            isMuted = len(self.fleetSpeakerCount)
            if isSpeaking:
                if not self.fleetSpeakerCount.has_key(speaker):
                    self.fleetSpeakerCount[speaker] = 1
            elif self.fleetSpeakerCount.has_key(speaker):
                self.fleetSpeakerCount.pop(speaker)
            if len(self.fleetSpeakerCount) > 0 and isMuted == 0:
                for each in self.members.keys():
                    if const.vcPrefixFleet not in each:
                        uthread.pool('vivox::ApplyChannelPriority', self.SetChannelOutputVolume, each, vivoxConstants.VXVOLUME_LOW)
                        self.LogInfo('ApplyChannelPriority mute')

            elif len(self.fleetSpeakerCount) == 0 and isMuted > 0:
                for each in self.members.keys():
                    if const.vcPrefixFleet not in each:
                        uthread.pool('vivox::ApplyChannelPriority', self.SetChannelOutputVolume, each, vivoxConstants.VXVOLUME_DEFAULT)
                        self.LogInfo('ApplyChannelPriority unmute')

        elif const.vcPrefixWing in vivoxChannelName:
            isMuted = len(self.wingSpeakerCount)
            if isSpeaking:
                if not self.wingSpeakerCount.has_key(speaker):
                    self.wingSpeakerCount[speaker] = 1
            elif self.wingSpeakerCount.has_key(speaker):
                self.wingSpeakerCount.pop(speaker)
            if len(self.wingSpeakerCount) > 0 and isMuted == 0:
                for each in self.members.keys():
                    if const.vcPrefixFleet not in each and const.vcPrefixWing not in each:
                        uthread.pool('vivox::ApplyChannelPriority', self.SetChannelOutputVolume, each, vivoxConstants.VXVOLUME_LOW)
                        self.LogInfo('ApplyChannelPriority mute')

            elif len(self.wingSpeakerCount) == 0 and isMuted > 0:
                for each in self.members.keys():
                    if const.vcPrefixFleet not in each and const.vcPrefixWing not in each:
                        uthread.pool('vivox::ApplyChannelPriority', self.SetChannelOutputVolume, each, vivoxConstants.VXVOLUME_DEFAULT)
                        self.LogInfo('ApplyChannelPriority unmute')

    def StopChannelPriority(self):
        self.LogInfo('StopChannelPriority')
        self.wingSpeakerCount = {}
        self.fleetSpeakerCount = {}
        for each in self.members.keys():
            uthread.pool('vivox::StopChannelPriority', self.SetChannelOutputVolume, each, vivoxConstants.VXVOLUME_DEFAULT)

    def GetPrettyChannelName(self, eveChannelName):
        c = ''
        if type(eveChannelName) is types.TupleType:
            t = eveChannelName[0]
            key = eveChannelName[0] + str(eveChannelName[1])
            if self.prettyChannelNames.has_key(key):
                return self.prettyChannelNames[key]
            if t.startswith(const.vcPrefixCorp):
                c = localization.GetByLabel('UI/Common/Corporation')
            elif t.startswith(const.vcPrefixFleet):
                c = localization.GetByLabel('UI/Fleet/Fleet')
            elif t.startswith(const.vcPrefixWing):
                c = localization.GetByLabel('UI/Fleet/Wing')
            elif t.startswith(const.vcPrefixSquad):
                c = localization.GetByLabel('UI/Fleet/Squad')
            elif t.startswith(const.vcPrefixAlliance):
                c = localization.GetByLabel('UI/Common/Alliance')
        else:
            key = eveChannelName
            if self.prettyChannelNames.has_key(key):
                return self.prettyChannelNames[key]
            channel = sm.services['LSC'].channels.get(eveChannelName, None)
            if channel:
                c = channel.info.displayName
        self.prettyChannelNames[key] = c
        return c

    def OnChannelsJoined(self, channels):
        for channel in channels:
            if self.IsVoiceChannel(channel):
                speakingChannel = self.GetSpeakingChannel()
                if type(speakingChannel) is types.TupleType:
                    speakingChannel = (speakingChannel,)
                self.SetTabColor(self.GetVivoxChannelName(channel), ['listen', 'speak'][speakingChannel == channel])
            else:
                joinCorporationChannel = settings.user.ui.Get('chatJoinCorporationChannelOnLogin', 0)
                joinCorporationChannel = joinCorporationChannel and self.GetVivoxChannelName(channel).startswith(const.vcPrefixCorp)
                if type(channel) is types.TupleType:
                    joinCorporationChannel = joinCorporationChannel and not util.IsNPC(channel[0][1])
                joinAllianceChannel = settings.user.ui.Get('chatJoinAllianceChannelOnLogin', 0)
                joinAllianceChannel = joinAllianceChannel and self.GetVivoxChannelName(channel).startswith(const.vcPrefixAlliance)
                shouldAutoJoin = joinCorporationChannel or joinAllianceChannel
                if shouldAutoJoin:
                    if self.vivoxLoginState == vivoxConstants.VXCLOGINSTATE_LOGGEDIN:
                        self.JoinChannel(channel)
                    elif channel not in self.autoJoinQueue:
                        self.autoJoinQueue.append(channel)

    def OnSessionDisconnect(self):
        if self.LoggedIn():
            self.DisableGlobalPushToTalkMode()
            setattr(self, 'userSessionDisconnected', 1)
            for each in self.members.keys():
                uthread.pool('vivox::OnSessionDisconnect', self.SetChannelOutputVolume, each, vivoxConstants.VXVOLUME_OFF)

    def OnSessionReconnect(self):
        if self.LoggedIn():
            if settings.user.audio.Get('talkBinding', 4):
                self.EnableGlobalPushToTalkMode('talk')
            setattr(self, 'userSessionDisconnected', 0)
            for each in self.members.keys():
                uthread.pool('vivox::OnSessionReconnect', self.SetChannelOutputVolume, each, vivoxConstants.VXVOLUME_DEFAULT)

    def OnLSC(self, channelID, estimatedMemberCount, method, who, args):
        if method == 'RenameChannel' and channelID in self.prettyChannelNames:
            self.prettyChannelNames[channelID] = args[0]

    def AppOnLoggedIn(self):
        if self.sendMessageOnLogIn:
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Voice/Enabled')})
        self.sendMessageOnLogIn = True
        if settings.user.audio.Get('talkBinding', 4):
            self.EnableGlobalPushToTalkMode('talk')
        if settings.user.audio.Get('TalkInputDevice', 0):
            self.SetPreferredAudioInputDevice(settings.user.audio.Get('TalkInputDevice', 0), restartAudioTest=0)
        if settings.user.audio.Get('TalkOutputDevice', 0):
            self.SetPreferredAudioOutputDevice(settings.user.audio.Get('TalkOutputDevice', 0), restartAudioTest=0)

    def AppOnLoggedOut(self):
        eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Voice/LoggedOut')})

    def AppOnAccountNotFound(self):
        eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Voice/AccountNotFound')})

    def AppAccountCreated(self):
        eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Voice/Initializing')})
        self.LogInfo('Account created')

    def AppCreateAccountFailed(self):
        eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Voice/CreatingAccountFailed')})

    def _OnJoinedChannel(self, channelName = 0):
        self.LogInfo('_OnJoinedChannel channelName', channelName)
        self.members[channelName] = []
        if channelName == 'Echo':
            sm.ScatterEvent('OnEchoChannel', True)
            self.SetSpeakingChannel('Echo')
            return
        eveChannelName = self.GetCcpChannelName(channelName)
        uthread.new(self.voiceMgr.LogChannelJoined, channelName).context = 'vivoxService::_OnJoinChannel::LogChannelJoined'
        eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Voice/JoinedChannel', channel=self.GetPrettyChannelName(eveChannelName))})
        isRestrictedFleetChannel = False
        for each in [const.vcPrefixFleet, const.vcPrefixSquad, const.vcPrefixWing]:
            if each in channelName:
                if sm.GetService('fleet').GetChannelMuteStatus(eveChannelName) == True:
                    exclusionList = sm.GetService('fleet').GetExclusionList()
                    if exclusionList.has_key(eveChannelName) == False:
                        isRestrictedFleetChannel = True
                    elif exclusionList.has_key(eveChannelName) and session.charid not in exclusionList[eveChannelName]:
                        isRestrictedFleetChannel = True

        self.SetTabColor(channelName, 'listen')
        sm.ScatterEvent('OnVoiceChannelJoined', eveChannelName)
        if self.speakingChannel is None and isRestrictedFleetChannel == False:
            self.SetSpeakingChannel(eveChannelName)
        uthread.pool('vivox::_OnJoinedChannel', self.GetParticipants, channelName)

    def _OnLeftChannel(self, channelName):
        self.LogInfo('_OnLeftChannel', channelName)
        if channelName == 'Echo':
            self.echo = False
            sm.ScatterEvent('OnEchoChannel', False)
            sm.ScatterEvent('OnVoiceChannelLeft', channelName)
            if self.members.has_key(channelName):
                self.members.pop(channelName)
            if channelName == self.speakingChannel:
                self.speakingChannel = None
            return
        uthread.new(self.voiceMgr.LogChannelLeft, channelName).context = 'vivoxService::_OnJoinChannel::LogChannelLeft'
        if self.members.has_key(channelName):
            tmp = []
            for members in self.members[channelName]:
                tmp.append([members[0], None, members[2]])

            self.members[channelName] = tmp
            eveChannelName = self.GetCcpChannelName(channelName)
            wnd = sm.GetService('LSC').GetChannelWindow(eveChannelName)
            if wnd is not None:
                wnd.RefreshVoiceStatus(self.members[channelName])
            self.SetTabColor(channelName, None)
            if len(self.members.keys()) == 0 and self.autoJoinQueue == ['Echo']:
                if self.connector.ChannelJoinInProgressCount() == 0:
                    self.JoinEchoChannel()
            self.LogInfo('_OnLeftChannel popping', channelName)
            self.members.pop(channelName)
            if channelName == self.speakingChannel:
                self.speakingChannel = None
            if len(self.members.keys()) == 0 and self.autoJoinQueue == ['Echo']:
                self.JoinEchoChannel()
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Voice/LeftChannel', channel=self.GetPrettyChannelName(eveChannelName))})
            sm.ScatterEvent('OnVoiceChannelLeft', eveChannelName)

    def AppOnParticipantLeft(self, username, channelName):
        self.SetVoiceIcon(self.GetCharIdFromUri(username), channelName, vivoxConstants.NOTJOINED)

    def AppOnParticipantJoined(self, charid, channelName):
        voiceIcon = vivoxConstants.JOINED
        for each in [const.vcPrefixFleet, const.vcPrefixSquad, const.vcPrefixWing]:
            if each in channelName:
                if sm.GetService('fleet').GetChannelMuteStatus(self.GetCcpChannelName(channelName)) == True:
                    exclusionList = sm.GetService('fleet').GetExclusionList()
                    if int(charid) not in exclusionList:
                        voiceIcon = vivoxConstants.MUTED

        self.SetVoiceIcon(charid, channelName, voiceIcon)

    def OnParticipantStateChanged(self, uri, channelName, isSpeaking, isLocallyMuted, energy):
        if settings.user.audio.Get('talkChannelPriority', 0) and not getattr(self, 'userSessionDisconnected', 0):
            self.ApplyChannelPriority(channelName, uri, isSpeaking)
        if channelName != 'Echo':
            eveCharID = self.GetCharIdFromUri(uri)
            if self.members.has_key(channelName):
                pass
            else:
                self.LogWarn('OnParticipantJoinedOrStateChanged Im missing a channel here baby: ', channelName)
            self.SetVoiceIcon(eveCharID, channelName, isSpeaking)
            eveChannelID = self.GetCcpChannelName(channelName)
            if isSpeaking:
                self.MoveToTop(eveCharID, eveChannelID)
            if eveCharID != eve.session.charid:
                if isSpeaking and settings.user.audio.Get('listenMutesGameSounds', 0):
                    self.PushActiveSpeaker(eveCharID)
                elif not isSpeaking:
                    self.PopActiveSpeaker(eveCharID)
            sm.ScatterEvent('OnSpeakingEvent', eveCharID, eveChannelID, isSpeaking)
        elif self.intensityCallback and hasattr(self.intensityCallback, 'OnMicrophoneIntensityEvent'):
            self.intensityCallback.OnMicrophoneIntensityEvent(energy)

    def AppOnKeyEvent(self, name, pressed):
        if name == 'talk':
            if pressed == 0:
                self.PopActiveSpeaker(eve.session.charid)
            elif pressed != 0 and settings.user.audio.Get('talkMutesGameSounds', 0):
                self.PushActiveSpeaker(eve.session.charid)

    def PopActiveSpeaker(self, charid):
        self.activeSpeakers.discard(charid)
        self.LogInfo('Removing', charid, 'from the list of active speakers. We are now down to', len(self.activeSpeakers))
        if self.gameSoundsMuted and len(self.activeSpeakers) == 0:
            self.gameSoundsMuted = False
            sm.GetService('audio').UnmuteSounds()

    def PushActiveSpeaker(self, charid):
        if charid in self.activeSpeakers:
            return
        self.activeSpeakers.add(charid)
        self.LogInfo('Adding', charid, 'to the list of active speakers. We are now up to', len(self.activeSpeakers))
        if not self.gameSoundsMuted and len(self.activeSpeakers) > 0:
            self.gameSoundsMuted = True
            sm.GetService('audio').MuteSounds()

    def IsChannelPersistent(self, vivoxChannelName):
        if const.vcPrefixCorp in vivoxChannelName or const.vcPrefixAlliance in vivoxChannelName:
            return True
        return False

    def IsChannelProtected(self, vivoxChannelName):
        isFleetChannel = False
        for each in [const.vcPrefixFleet]:
            if each in vivoxChannelName:
                isFleetChannel = True
                break

        if self.IsChannelPersistent(vivoxChannelName) or isFleetChannel:
            return True
        return False

    def AppAddToACL(self, vivoxChannelName):
        isCorpChannel = const.vcPrefixCorp in vivoxChannelName
        isAllianceChannel = const.vcPrefixAlliance in vivoxChannelName
        isFleetChannel = False
        for each in [const.vcPrefixFleet]:
            if each in vivoxChannelName:
                isFleetChannel = True
                prefixLen = len(each)
                break

        success = False
        if isCorpChannel:
            success = moniker.GetCorpRegistry().AddToVoiceChat(vivoxChannelName)
        elif isAllianceChannel:
            success = moniker.GetAlliance().AddToVoiceChat(vivoxChannelName)
        elif isFleetChannel:
            fleetid = vivoxChannelName[prefixLen:]
            success = moniker.GetFleet(fleetid).AddToVoiceChat(vivoxChannelName)
        if success:
            uthread.pool('vivox::JoinChannel', self._JoinChannel, vivoxChannelName)
        else:
            self.LogError('Could not add voice chat user to ACL.')