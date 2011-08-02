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

class EveVivoxService(svc.vivox):
    __guid__ = 'svc.evevivox'
    __servicename__ = 'evevivox'
    __replaceservice__ = 'vivox'
    __exportedcalls__ = {}
    __notifyevents__ = ['OnChannelsJoined',
     'OnInstantVoiceInvite',
     'OnInstantVoiceReply',
     'OnInstantVoiceChannelReady']
    __notifyevents__.extend(svc.vivox.__notifyevents__)

    def AppRun(self, ms):
        self.fleetSpeakerCount = {}
        self.wingSpeakerCount = {}
        self.mutedParticipants = {}
        self.prettyChannelNames = {}
        self.UpdateLoginCount = True
        self.onInstantVoiceInviting = 0
        self.gameSoundsMuted = False
        self.activeSpeakers = set()
        self.sendMessageOnLogIn = not self.Enabled()
        sm.RegisterNotify(self)



    def AppGetServerName(self):
        return eve.serverName



    def AppInit(self):
        serverName = self.AppGetServerName()
        self.LogInfo('Vivox using serverName ', serverName)
        if serverName in ('Tranquility', '87.237.38.200', '87.237.38.200:26000'):
            self.vivoxServer = 'eve'
        elif serverName in ('Singularity', 'Test Server (Singularity)', '87.237.38.50', 'Multiplicity', 'Test Server (Multiplicity)', '87.237.38.51', 'Duality', 'Test Server (Duality)', '87.237.38.60'):
            self.vivoxServer = 'evs'
        else:
            self.vivoxServer = 'evc'
        self.LogNotice('Using vivoxServer ', self.vivoxServer)



    def GetServerInfo(self):
        if eve.session.role & service.ROLE_GML:
            return self.vivoxServer



    def AppCanJoinChannel(self, eveChannelID, suppress = False):
        if type(eveChannelID) is types.TupleType:
            if type(eveChannelID[0]) is types.TupleType:
                eveChannelID = eveChannelID[0]
        if type(eveChannelID) is types.TupleType and eveChannelID[0] not in ('inst', 'wingid', 'fleetid', 'squadid') or type(eveChannelID) is types.IntType:
            virtualChannels = 0
            for each in self.members:
                for virtual in ['inst',
                 'wingid',
                 'fleetid',
                 'squadid']:
                    if virtual in each:
                        virtualChannels += 1


            if self.connector.ChannelJoinInProgressCount() - virtualChannels >= 2:
                eve.Message('CustomNotify', {'notify': mls.UI_EVEVOICE_TOOMANYCHANNELS})
                return False
        if type(eveChannelID) == types.TupleType:
            for key in self.members.keys():
                if type(eveChannelID[0]) == types.TupleType:
                    eveChannelID = eveChannelID[0]
                if eveChannelID[0] in key:
                    self.LeaveChannel(self.GetCcpChannelName(key))

        if self.connector.ChannelJoinInProgressCount() > 6:
            eve.Message('CustomNotify', {'notify': mls.UI_EVEVOICE_TOOMANYCHANNELS})
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
                if 'inst' in self.speakingChannel:
                    self.LeaveInstantChannel()
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
            eve.Message('CustomNotify', {'notify': mls.UI_FLEET_MUTED_IN_CHANNEL})



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
            sm.RemoteSvc('LSC').VoiceStatus(eveChannelID, 2)
            blue.pyos.synchro.Sleep(blue.os.TimeDiffInMs(blue.os.GetTime(), time))
            self.UnGag(charID, eveChannelID)
        else:
            self.LogInfo('someone was gagged at', charID, vivoxChannelName)



    def AppUnGag(self, charID, eveChannelID):
        vivoxChannelName = self.GetVivoxChannelName(eveChannelID)
        if int(charID) == int(self.charid) and vivoxChannelName in self.gaggedAt:
            self.gaggedAt.pop(vivoxChannelName)
            self.EnableGlobalPushToTalkMode('talk')
            self.LogInfo('I was ungagged at', vivoxChannelName)
            sm.RemoteSvc('LSC').VoiceStatus(eveChannelID, 1)
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
        eve.Message('CustomNotify', {'notify': mls.UI_EVEVOICE_CREATINGVOICEACCOUNT})



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
        availableKeyBindings = [(mls.UI_GENERIC_NONE, 1),
         (mls.UI_SYSMENU_MIDDLEMOUSE, 4),
         (mls.UI_SYSMENU_LEFTCTRL, 162),
         (mls.UI_SYSMENU_RIGHTCTRL, 163),
         (mls.UI_SYSMENU_LEFTALT, 164),
         (mls.UI_SYSMENU_RIGHTALT, 165),
         (mls.UI_GENERIC_KEYPAD + ' 0', 96),
         (mls.UI_SYSMENU_RIGHTSHIFT, 161)]
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
                tip = mls.UI_GENERIC_YOUARESPEAKING
            else:
                icon = 'ui_38_16_196'
                tip = mls.UI_GENERIC_YOUARELISTENING
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
            for each in ['fleetid',
             'squadid',
             'wingid',
             'fleetid']:
                for channel in self.members:
                    if each in channel:
                        self.LeaveChannel(channel)





    def JoinFleetChannels(self):
        if not self.LoggedIn() or settings.user.audio.Get('talkAutoJoinFleet', 1) == 0:
            return 
        if session.squadid > 0 and 'squadid' + str(session.squadid) not in self.members:
            self.JoinChannel(('squadid', session.squadid))
        if session.wingid > 0 and 'wingid' + str(session.wingid) not in self.members:
            self.JoinChannel(('wingid', session.wingid))
        if session.fleetid > 0 and 'fleetid' + str(session.fleetid) not in self.members:
            self.JoinChannel(('fleetid', session.fleetid))



    def ApplyChannelPriority(self, vivoxChannelName, speaker, isSpeaking):
        if 'fleetid' in vivoxChannelName:
            isMuted = len(self.fleetSpeakerCount)
            if isSpeaking:
                if not self.fleetSpeakerCount.has_key(speaker):
                    self.fleetSpeakerCount[speaker] = 1
            elif self.fleetSpeakerCount.has_key(speaker):
                self.fleetSpeakerCount.pop(speaker)
            if len(self.fleetSpeakerCount) > 0 and isMuted == 0:
                for each in self.members.keys():
                    if 'fleetid' not in each:
                        uthread.pool('vivox::ApplyChannelPriority', self.SetChannelOutputVolume, each, vivoxConstants.VXVOLUME_LOW)
                        self.LogInfo('ApplyChannelPriority mute')

            elif len(self.fleetSpeakerCount) == 0 and isMuted > 0:
                for each in self.members.keys():
                    if 'fleetid' not in each:
                        uthread.pool('vivox::ApplyChannelPriority', self.SetChannelOutputVolume, each, vivoxConstants.VXVOLUME_DEFAULT)
                        self.LogInfo('ApplyChannelPriority unmute')

        elif 'wingid' in vivoxChannelName:
            isMuted = len(self.wingSpeakerCount)
            if isSpeaking:
                if not self.wingSpeakerCount.has_key(speaker):
                    self.wingSpeakerCount[speaker] = 1
            elif self.wingSpeakerCount.has_key(speaker):
                self.wingSpeakerCount.pop(speaker)
            if len(self.wingSpeakerCount) > 0 and isMuted == 0:
                for each in self.members.keys():
                    if 'fleetid' not in each and 'wingid' not in each:
                        uthread.pool('vivox::ApplyChannelPriority', self.SetChannelOutputVolume, each, vivoxConstants.VXVOLUME_LOW)
                        self.LogInfo('ApplyChannelPriority mute')

            elif len(self.wingSpeakerCount) == 0 and isMuted > 0:
                for each in self.members.keys():
                    if 'fleetid' not in each and 'wingid' not in each:
                        uthread.pool('vivox::ApplyChannelPriority', self.SetChannelOutputVolume, each, vivoxConstants.VXVOLUME_DEFAULT)
                        self.LogInfo('ApplyChannelPriority unmute')




    def StopChannelPriority(self):
        self.LogInfo('StopChannelPriority')
        self.wingSpeakerCount = {}
        self.fleetSpeakerCount = {}
        for each in self.members.keys():
            uthread.pool('vivox::StopChannelPriority', self.SetChannelOutputVolume, each, vivoxConstants.VXVOLUME_DEFAULT)




    def InstantVoice(self, toID):
        self.LogInfo('InstantVoice')
        if not self.LoggedIn():
            raise UserError('VoiceNotEnabled')
        uthread.pool('vivox::InstantVoice', self._InstantVoice, toID)



    def _InstantVoice(self, toID):
        channelID = ('inst', str(eve.session.charid))
        self.JoinChannel(channelID, persist=False)
        self.voiceMgr.InstantVoiceInvite(toID, channelID)



    def OnInstantVoiceInvite(self, eveChannelID):
        if not self.onInstantVoiceInviting:
            self.onInstantVoiceInviting = 1
            charID = int(eveChannelID[1])
            if not self.LoggedIn():
                self.voiceMgr.InstantVoiceReply(charID, -1)
                self.onInstantVoiceInviting = 0
                return 
            for channels in self.members.keys():
                if 'inst' in channels:
                    self.voiceMgr.InstantVoiceReply(charID, -2)
                    self.onInstantVoiceInviting = 0
                    return 

            if charID in sm.GetService('fleet').GetMembers():
                self.voiceMgr.InstantVoiceReply(charID, 1)
                self.JoinChannel(eveChannelID, suppress=True, persist=False)
            else:
                self.voiceMgr.InstantVoiceReply(charID, -3)
            self.onInstantVoiceInviting = 0



    def OnInstantVoiceReply(self, reply, fromID):
        myInstantChannel = 'inst' + str(eve.session.charid)
        if reply == -1:
            self.connector.LeaveChannel(myInstantChannel)
            eve.Message('CustomNotify', {'notify': mls.UI_EVEVOICE_INIVITENOTVOICEENABLED})
            sm.ScatterEvent('OnInstantVoiceChannelFailed')
        elif reply == -2:
            self.connector.LeaveChannel(myInstantChannel)
            eve.Message('CustomNotify', {'notify': mls.UI_EVEVOICE_INVITEBUSY})
            sm.ScatterEvent('OnInstantVoiceChannelFailed')
        elif reply == -3:
            self.connector.LeaveChannel(myInstantChannel)
            eve.Message('CustomNotify', {'notify': mls.UI_EVEVOICE_INVITENOTINFLEETWITHYOU})
            sm.ScatterEvent('OnInstantVoiceChannelFailed')



    def GetInstantVoiceParticipant(self):
        for k in self.members.iterkeys():
            if k.startswith('inst'):
                for member in self.members[k][:]:
                    if int(member[0]) != eve.session.charid:
                        return int(member[0])
                else:
                    self.LogWarn('GetInstantVoiceParticipant() found an insta channel with no one but us!')
                    return eve.session.charid





    def InstantVoiceResponse(self):
        WAIT_TIME = 10
        blue.pyos.synchro.Sleep(WAIT_TIME * 1000)
        if self.members.has_key('inst' + str(session.charid)):
            if len(self.members[('inst' + str(session.charid))]) == 0:
                self.LogWarn('Timeout (', WAIT_TIME, ' sec) waiting for participant to join instant chat.')
                self.LeaveInstantChannel()
                eve.Message('CustomNotify', {'notify': mls.UI_EVEVOICE_PRIVATETIMEOUT})
                sm.ScatterEvent('OnInstantVoiceChannelFailed')
                return 
        self.LogInfo('InstantVoiceResponse() - got member')



    def GetPrettyChannelName(self, eveChannelName):
        c = ''
        if type(eveChannelName) is types.TupleType:
            t = eveChannelName[0]
            key = eveChannelName[0] + str(eveChannelName[1])
            if self.prettyChannelNames.has_key(key):
                return self.prettyChannelNames[key]
            if t.startswith('corp'):
                c = mls.UI_GENERIC_CORPORATION
            elif t.startswith('fleet'):
                c = mls.UI_FLEET_FLEET
            elif t.startswith('wing'):
                c = mls.UI_FLEET_WING
            if t.startswith('squad'):
                c = mls.UI_FLEET_SQUAD
            elif t.startswith('inst'):
                c = mls.UI_FLEET_PRIVATE
            elif t.startswith('alliance'):
                c = mls.UI_GENERIC_ALLIANCE
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
                self.SetTabColor(self.GetVivoxChannelName(channel), ['listen', 'speak'][(speakingChannel == channel)])
            else:
                joinCorporationChannel = settings.user.ui.Get('chatJoinCorporationChannelOnLogin', 0) and self.GetVivoxChannelName(channel).startswith('corp')
                if type(channel) is types.TupleType:
                    joinCorporationChannel = joinCorporationChannel and not util.IsNPC(channel[0][1])
                joinAllianceChannel = settings.user.ui.Get('chatJoinAllianceChannelOnLogin', 0) and self.GetVivoxChannelName(channel).startswith('alliance')
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




    def AppOnLoggedIn(self):
        if self.sendMessageOnLogIn:
            eve.Message('CustomNotify', {'notify': mls.UI_SYSMENU_EVEVOICEENABLED})
        self.sendMessageOnLogIn = True
        if settings.user.audio.Get('talkBinding', 4):
            self.EnableGlobalPushToTalkMode('talk')
        if settings.user.audio.Get('TalkInputDevice', 0):
            self.SetPreferredAudioInputDevice(settings.user.audio.Get('TalkInputDevice', 0), restartAudioTest=0)
        if settings.user.audio.Get('TalkOutputDevice', 0):
            self.SetPreferredAudioOutputDevice(settings.user.audio.Get('TalkOutputDevice', 0), restartAudioTest=0)



    def AppOnLoggedOut(self):
        eve.Message('CustomNotify', {'notify': mls.UI_EVEVOICE_LOGGEDOUT})



    def AppOnAccountNotFound(self):
        eve.Message('CustomNotify', {'notify': mls.UI_EVEVOICE_VOICEACCOUNTNOTFOUND})



    def AppAccountCreated(self):
        eve.Message('CustomNotify', {'notify': mls.UI_EVEVOICE_VOICEACCOUNTINIT})
        self.LogInfo('Account created')



    def AppCreateAccountFailed(self):
        eve.Message('CustomNotify', {'notify': mls.UI_EVEVOICE_CREATINGVOICEACCOUNTFAILED % {'statusText': ''}})



    def _OnJoinedChannel(self, channelName = 0):
        self.LogInfo('_OnJoinedChannel channelName', channelName)
        if self.UpdateLoginCount:
            self.UpdateLoginCount = False
            self.voiceMgr.UpdateVoiceMetrics()
        self.members[channelName] = []
        if channelName == 'Echo':
            sm.ScatterEvent('OnEchoChannel', True)
            self.SetSpeakingChannel('Echo')
            return 
        eveChannelName = self.GetCcpChannelName(channelName)
        uthread.new(self.voiceMgr.LogChannelJoined, channelName).context = 'vivoxService::_OnJoinChannel::LogChannelJoined'
        eve.Message('CustomNotify', {'notify': mls.UI_EVEVOICE_JOINEDCHANNEL % {'name': self.GetPrettyChannelName(eveChannelName)}})
        if 'inst' in channelName:
            sm.ScatterEvent('OnVoiceChannelJoined', eveChannelName)
            uthread.pool('vivox::_OnJoinedChannel', self.GetParticipants, channelName)
            uthread.pool('vivox::InstantVoiceResponse', self.InstantVoiceResponse)
            return 
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
        eveChannelName = ''
        if channelName != 0:
            eveChannelName = self.GetCcpChannelName(channelName)
            sm.RemoteSvc('LSC').VoiceStatus(eveChannelName, 0)
        if type(eveChannelName) is types.TupleType and eveChannelName[0].startswith('inst'):
            if self.speakingChannel and 'inst' in self.speakingChannel and getattr(self, 'previousSpeakingChannel', None) is not None:
                self.SetSpeakingChannel(self.previousSpeakingChannel)
                self.previousSpeakingChannel = None
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
            eve.Message('CustomNotify', {'notify': mls.UI_EVEVOICE_LEFTCHANNEL % {'name': self.GetPrettyChannelName(eveChannelName)}})
            sm.ScatterEvent('OnVoiceChannelLeft', eveChannelName)



    def AppOnParticipantLeft(self, username, channelName):
        if 'inst' in channelName:
            self.LeaveChannel(self.GetCcpChannelName(channelName))
        else:
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



    def OnInstantVoiceChannelReady(self):
        eve.Message('CustomNotify', {'notify': mls.UI_EVEVOICE_PRIVATECHANNELREADY % {'name': cfg.eveowners.Get(self.GetInstantVoiceParticipant()).name}})



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




