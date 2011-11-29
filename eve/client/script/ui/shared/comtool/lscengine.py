import service
import types
import copy
import util
import form
import blue
import uthread
import uix
import uiutil
import util
import xtriui
import listentry
import sys
import log
import stackless
import uiconst
import dbutil
import uicls
import localization
SECOND = 10000000L
CHTERR_NOSUCHCHANNEL = -3
CHTERR_ALREADYEXISTS = -6
MINIMUM_EMC_UPDATE_TIME = 60L * SECOND

def GetDisplayName(channelID, systemOverride = 0, otherID = None):
    if type(channelID) == types.IntType:
        if channelID in sm.StartService('LSC').channels:
            channel = sm.StartService('LSC').channels[channelID]
            if channel.info.temporary:
                title = ''
                for charID in channel.memberList:
                    if charID != eve.session.charid:
                        title += cfg.eveowners.Get(charID).name + ', '

                if not title and otherID:
                    title += cfg.eveowners.Get(otherID).name
                else:
                    title = title[:-2]
                if len(title) == 0 and len(channel.info.displayName) > 0:
                    title = channel.info.displayName
                if len(channel.memberList) > 2:
                    if title:
                        return localization.GetByLabel('UI/Chat/GroupChat', title=title)
                    else:
                        return localization.GetByLabel('UI/Chat/GroupChatAlone')
                else:
                    if title:
                        return localization.GetByLabel('UI/Chat/PrivateChat', title=title)
                    else:
                        return localization.GetByLabel('UI/Chat/PrivateChatAlone')
            elif channel.info.groupMessageID:
                if channel.info.channelMessageID == const.CHAT_SYSTEM_CHANNEL:
                    if channel.info.displayName is not None:
                        return channel.info.displayName
                    else:
                        return localization.GetByLabel('UI/Chat/SystemChannels')
                else:
                    if channel.info.displayName is not None:
                        return channel.info.displayName
                    else:
                        return localization.GetByMessageID(channel.info.channelMessageID)
            else:
                if channel.info.ownerID == const.ownerSystem:
                    return localization.GetByMessageID(channel.info.channelMessageID)
                else:
                    return channel.info.displayName
    elif type(channelID[0]) is types.TupleType:
        channelID = channelID[0]
    k = channelID[0]
    v = channelID[1]
    if k == 'global':
        return localization.GetByLabel('UI/Common/Global')
    if k == 'corpid':
        if eve.session.corpid == v and not systemOverride:
            return localization.GetByLabel('UI/Common/Corp')
        else:
            return localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Common/Corp'), featureName=cfg.eveowners.Get(v).name)
    elif k == 'fleetid':
        return localization.GetByLabel('UI/Fleet/Fleet')
    if k == 'squadid':
        return localization.GetByLabel('UI/Fleet/Squad')
    if k == 'wingid':
        return localization.GetByLabel('UI/Fleet/Wing')
    if k == 'warfactionid':
        if eve.session.warfactionid == v and not systemOverride:
            return localization.GetByLabel('UI/Common/Militia')
        else:
            return localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Common/Militia'), featureName=cfg.eveowners.Get(v).name)
    elif k == 'allianceid':
        if eve.session.allianceid == v and not systemOverride:
            return localization.GetByLabel('UI/Common/Alliance')
        else:
            return localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Common/Alliance'), featureName=cfg.eveowners.Get(v).name)
    elif k == 'solarsystemid2':
        if eve.session.solarsystemid2 == v and not systemOverride:
            return localization.GetByLabel('UI/Chat/Local')
        else:
            return localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Chat/Local'), featureName=cfg.evelocations.Get(v).name)
    elif k == 'solarsystemid':
        if eve.session.solarsystemid == v and not systemOverride:
            return localization.GetByLabel('UI/Common/LocationTypes/System')
        else:
            return localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Common/LocationTypes/System'), featureName=cfg.evelocations.Get(v).name)
    elif k == 'constellationid':
        if eve.session.constellationid == v and not systemOverride:
            return localization.GetByLabel('UI/Common/LocationTypes/Constellation')
        else:
            return localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Common/LocationTypes/Constellation'), featureName=cfg.evelocations.Get(v).name)
    elif k == 'regionid':
        if eve.session.regionid == v and not systemOverride:
            return localization.GetByLabel('UI/Common/LocationTypes/Region')
        else:
            return localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Common/LocationTypes/Region'), featureName=cfg.evelocations.Get(v).name)
    elif k.startswith('incursion'):
        constellationName = sm.GetService('incursion').GetConstellationNameFromTaleIDForIncursionChat(v)
        return localization.GetByLabel('UI/Chat/IncursionConstellationChannel', constellationName=constellationName)
    return str(channelID)



def ConfigKeyFromChannelID(channelID):
    if type(channelID) == types.IntType:
        return channelID
    else:
        if type(channelID[0]) == types.TupleType:
            if channelID[0][0] == 'corpid' and channelID[0][1] != eve.session.corpid:
                return str(channelID[0][0]) + str(channelID[0][1])
            return str(channelID[0][0])
        return str(channelID[0])



def ChannelHash(criteria):
    if type(criteria) == types.IntType:
        return criteria
    criteria = list(criteria)
    criteria.sort()
    criteria = tuple(criteria)
    tmp = {criteria: True}
    return criteria



def ChannelRecyclableHash(channelID):
    if type(channelID) == types.TupleType:
        k = []
        for stuff in channelID:
            k.append(stuff[0])

        return tuple(k)
    else:
        return channelID



def __getAclRowDescriptor():
    return blue.DBRowDescriptor((('accessor', const.DBTYPE_I4),
     ('mode', const.DBTYPE_I4),
     ('untilWhen', const.DBTYPE_FILETIME),
     ('originalMode', const.DBTYPE_I4),
     ('reason', const.DBTYPE_WSTR),
     ('admin', const.DBTYPE_WSTR)))



def GetAccessInfo(channel, role, charID, *ids):
    if role & (service.ROLE_CHTADMINISTRATOR | service.ROLE_GMH):
        return (CHTMODE_CREATOR, None)
    if type(channel.channelID) == types.IntType:
        if channel.info.ownerID == charID:
            return (CHTMODE_CREATOR, None)
        else:
            public = (CHTMODE_NOTSPECIFIED, None)
            other = (None, None)
            deleteList = []
            deleting = False
            for each in channel.acl:
                if each.untilWhen and each.untilWhen < blue.os.GetWallclockTime():
                    deleteList.append(each)
                    deleting = True
                if deleting:
                    continue
                if each.accessor == charID:
                    return (each.mode, blue.DBRow(__getAclRowDescriptor(), [each.accessor,
                      each.mode,
                      each.untilWhen,
                      each.originalMode,
                      each.reason,
                      each.admin]))
                if each.accessor is None:
                    public = (each.mode, blue.DBRow(__getAclRowDescriptor(), [each.accessor,
                      each.mode,
                      each.untilWhen,
                      each.originalMode,
                      each.reason,
                      each.admin]))
                elif each.accessor in ids:
                    if other[0] is None or other[0] > each.mode:
                        other = (each.mode, blue.DBRow(__getAclRowDescriptor(), [each.accessor,
                          each.mode,
                          each.untilWhen,
                          each.originalMode,
                          each.reason,
                          each.admin]))

            if deleting:
                for each in deleteList:
                    channel.acl.remove(each)

                return GetAccessInfo(channel, role, charID, *ids)
            if other[0] is not None:
                return other
            return public
    else:
        if charID in channel.recentSpeakerList:
            if channel.recentSpeakerList[charID].role & (service.ROLE_CHTADMINISTRATOR | service.ROLE_GMH):
                return (CHTMODE_CREATOR, None)
        if charID in channel.memberList:
            if channel.memberList[charID].role & (service.ROLE_CHTADMINISTRATOR | service.ROLE_GMH):
                return (CHTMODE_CREATOR, None)
        return (CHTMODE_CONVERSATIONALIST, None)


CHTMODE_CREATOR = 8 + 4 + 2 + 1
CHTMODE_OPERATOR = 4 + 2 + 1
CHTMODE_CONVERSATIONALIST = 2 + 1
CHTMODE_SPEAKER = 2
CHTMODE_LISTENER = 1
CHTMODE_NOTSPECIFIED = -1
CHTMODE_DISALLOWED = -2
CHTERR_NOSUCHCHANNEL = -3
CHTERR_ACCESSDENIED = -4
CHTERR_INCORRECTPASSWORD = -5
CHTERR_ALREADYEXISTS = -6
CHTERR_TOOMANYCHANNELS = -7
CHT_MAX_USERS_PER_IMMEDIATE_CHANNEL = 50
CHT_MAX_INPUT = 253

class LargeScaleChat(service.Service):
    __guid__ = 'svc.LSC'
    __displayname__ = 'Large-Scale Chat Service'
    __configvalues__ = {'rookieHelpChannel': 1,
     'helpChannelEN': 2,
     'helpChannelDE': 40,
     'helpChannelRU': 55,
     'helpChannelJA': 56}
    __exportedcalls__ = {'GetChannels': [],
     'Invite': [],
     'CreateOrJoinChannel': [],
     'RenameChannel': [],
     'SetChannelMOTD': [],
     'SetChannelLanguageRestriction': [],
     'AccessControl': [],
     'DestroyChannel': [],
     'JoinChannel': [service.ROLE_SERVICE],
     'LeaveChannel': [],
     'ForgetChannel': [],
     'SendMessage': [],
     'IsJoined': [],
     'GetMembers': [],
     'ChatInvite': [service.ROLE_SERVICE],
     'GetChannelInfo': [],
     'GetMemberInfo': [],
     'IsForgettable': [],
     'IsOperator': [],
     'IsCreator': [],
     'IsGagged': [],
     'IsSpeaker': [],
     'GetMyAccessInfo': [],
     'Settings': [],
     'GetChannelPasswordAndJoin': [service.ROLE_SERVICE],
     'AskYesNoQuestion': [service.ROLE_SERVICE],
     'GetChannelMessages': [service.ROLE_SERVICE],
     'JoinOrLeaveChannel': [],
     'GetChannelIDFromName': []}
    __notifyevents__ = ['OnLSC',
     'OnSessionChanged',
     'OnMessage',
     'ProcessRookieStateChange',
     'OnCorporationMemberChanged']
    __dependencies__ = ['settings']
    __exitdependencies__ = ['gameui', 'ui']

    def LocalEchoAll(self, msg, charid):
        for channelID in self.channels.keys():
            channel = self.channels[channelID]
            if channel.window and type(channel.channelID) is tuple and channel.channelID[0][0] == 'solarsystemid2':
                channel.window.Speak(msg, charid, 1)




    def OnSessionChanged(self, isremote, sess, change):
        if eve.rookieState and eve.rookieState < sm.GetService('tutorial').GetOtherRookieFilter('defaultchannels'):
            return 
        self.settings.LoadSettings()
        leave = []
        if 'regionid' in change and change['regionid'][0]:
            leave.append([('regionid', change['regionid'][0])])
        if 'constellationid' in change and change['constellationid'][0]:
            leave.append([('constellationid', change['constellationid'][0])])
        if 'solarsystemid2' in change and change['solarsystemid2'][0]:
            leave.append([('solarsystemid2', change['solarsystemid2'][0])])
        if 'allianceid' in change and change['allianceid'][0]:
            leave.append([('allianceid', change['allianceid'][0])])
            leave.append(change['allianceid'][0])
        if 'corpid' in change and change['corpid'][0]:
            leave.append([('corpid', change['corpid'][0])])
            leave.append(change['corpid'][0])
            self.messageList = None
            self.messageListIndexed = None
        if 'fleetid' in change and change['fleetid'][0]:
            leave.append([('fleetid', change['fleetid'][0])])
        if 'warfactionid' in change and change['warfactionid'][0]:
            leave.append([('warfactionid', change['warfactionid'][0])])
        if 'charid' in change and change['charid'][0]:
            leave.append([('global', 0)])
            self.messageList = None
            self.messageListIndexed = None
        windows = {}
        if leave:
            self.LeaveChannels(leave, saveWindows=windows, sessionChangeDriven=True, unsubscribe=True)
        if sess.charid:
            join = []
            if 'regionid' in change and change['regionid'][1] and settings.char.ui.Get('lscengine_mychannels_region', 0):
                join.append([('regionid', change['regionid'][1])])
            if 'constellationid' in change and change['constellationid'][1] and settings.char.ui.Get('lscengine_mychannels_constellation', 1):
                join.append([('constellationid', change['constellationid'][1])])
            if 'solarsystemid2' in change and change['solarsystemid2'][1]:
                join.append([('solarsystemid2', change['solarsystemid2'][1])])
            if 'allianceid' in change and change['allianceid'][1]:
                join.append([('allianceid', change['allianceid'][1])])
            if 'corpid' in change and change['corpid'][1]:
                join.append([('corpid', change['corpid'][1])])
                join.append(change['corpid'][1])
            if 'fleetid' in change and change['fleetid'][1]:
                join.append([('fleetid', change['fleetid'][1])])
            if 'warfactionid' in change and change['warfactionid'][1]:
                join.append([('warfactionid', change['warfactionid'][1])])
            if 'charid' in change and change['charid'][1]:
                join.append(change['charid'][1])
            if 'corpid' in change and change['corpid'][1]:
                join.append(change['corpid'][1])
            if 'allianceid' in change and change['allianceid'][1]:
                join.append(change['allianceid'][1])
            import __builtin__
            if hasattr(__builtin__, 'settings'):
                for channelID in settings.char.ui.Get('lscengine_mychannels', []):
                    if channelID not in join:
                        join.append(channelID)

            if eve.session.role & service.ROLE_NEWBIE and self.rookieHelpChannel not in join and not self.rookieJoined:
                self.rookieJoined = True
                join.append(self.rookieHelpChannel)
            if join:
                self.JoinChannels(join, restoreWindows=windows, maximize=0)
        for window in windows.itervalues():
            if window == sm.GetService('focus').GetFocusChannel():
                sm.GetService('focus').SetFocusChannel()
            if window is not None and not window.destroyed:
                window.Close()




    def OnMessage(self, recipients, messageID, senderID, subject, created):
        if self.messageList is not None:
            if self.channelList is None:
                self.messageList = None
                self.messageListIndexed = None
            for recipient in recipients:
                if recipient in self.channelListIndexed:
                    li = [recipient,
                     messageID,
                     senderID,
                     subject,
                     created,
                     0]
                    self.messageList.InsertNew(*li)
                    self.messageListIndexed[messageID] = li




    def ProcessRookieStateChange(self, state):
        if eve.rookieState and eve.rookieState < sm.GetService('tutorial').GetOtherRookieFilter('defaultchannels'):
            self.LeaveChannels(self.channels.keys(), savePrefs=0)
        else:
            self.rookieJoined = False
            self.InitChannels()



    def Run(self, memStream = None):
        self.rookieJoined = False
        self.updateEMC = False
        self.messageList = None
        self.messageListIndexed = None
        self.channels = {}
        self.forgettables = {}
        self.channelList = None
        self.channelListIndexed = {}
        self.joiningChannels = {}
        self.semaphore = uthread.Semaphore()
        self.lastEMCUpdate = 0
        uthread.worker('LSC::DecayRecent', self._LargeScaleChat__DecayRecent)
        import cPickle
        if memStream:
            memStream.Seek(0)
            dump = memStream.Read()
            if len(dump):
                self.LeaveChannels(cPickle.loads(str(dump)), savePrefs=0)
        self.InitChannels()



    def InitChannels(self):
        if eve.rookieState and eve.rookieState < sm.GetService('tutorial').GetOtherRookieFilter('defaultchannels'):
            return 
        join = []
        if eve.session is not None and eve.session.charid:
            self.settings.LoadSettings()
            if eve.session.regionid and settings.char.ui.Get('lscengine_mychannels_region', 0):
                join.append([('regionid', eve.session.regionid)])
            if eve.session.constellationid and settings.char.ui.Get('lscengine_mychannels_constellation', 1):
                join.append([('constellationid', eve.session.constellationid)])
            if eve.session.solarsystemid2:
                join.append([('solarsystemid2', eve.session.solarsystemid2)])
            if eve.session.allianceid:
                join.append([('allianceid', eve.session.allianceid)])
                join.append(eve.session.allianceid)
            if eve.session.corpid:
                join.append([('corpid', eve.session.corpid)])
                join.append(eve.session.corpid)
            if eve.session.fleetid:
                join.append([('fleetid', eve.session.fleetid)])
            if eve.session.warfactionid:
                join.append([('warfactionid', eve.session.warfactionid)])
            if eve.session.charid:
                join.append(eve.session.charid)
                import __builtin__
                if hasattr(__builtin__, 'settings'):
                    for channelID in settings.char.ui.Get('lscengine_mychannels', []):
                        if channelID not in join:
                            join.append(channelID)

            if eve.session.role & service.ROLE_NEWBIE and self.rookieHelpChannel not in join and not self.rookieJoined:
                self.rookieJoined = True
                join.append(self.rookieHelpChannel)
            if join:
                uthread.worker('LSC::ProcessSessionChange::JoinChannels', self.JoinChannels, join, maximize=0)



    def __SaveChannelPrefs(self, channelID = None):
        prefs = settings.char.ui.Get('lscengine_mychannels', [])
        prefs2 = copy.copy(prefs)
        if channelID in prefs2:
            prefs2.remove(channelID)
        settings.char.ui.Set('lscengine_mychannels_region', 0)
        settings.char.ui.Set('lscengine_mychannels_constellation', 0)
        for channelID in self.channels:
            if channelID in prefs2:
                continue
            if type(channelID) == types.IntType:
                if not self.channels[channelID].info.temporary:
                    prefs2.append(channelID)
            else:
                if channelID[0][0] == 'regionid':
                    settings.char.ui.Set('lscengine_mychannels_region', 0)
                if channelID[0][0] == 'constellationid':
                    settings.char.ui.Set('lscengine_mychannels_constellation', 1)

        for each in (self.rookieHelpChannel,
         eve.session.charid,
         eve.session.corpid,
         eve.session.allianceid):
            if each in prefs2:
                prefs2.remove(each)

        prefs.sort()
        prefs2.sort()
        if prefs != prefs2:
            settings.char.ui.Set('lscengine_mychannels', prefs2)



    def Stop(self, memStream = None):
        if self.channels:
            import cPickle
            memStream.Write(cPickle.dumps(self.channels.keys(), True))
        self._LargeScaleChat__SaveChannelPrefs()



    def __DecayRecent(self):
        while self.state == service.SERVICE_RUNNING:
            blue.pyos.synchro.SleepWallclock(60000)
            try:
                self._LargeScaleChat__DecayRecentLoop()
            except:
                log.LogException('Error in __DecayRecentLoop')
                sys.exc_clear()




    def __DecayRecentLoop(self):
        t = blue.os.GetWallclockTimeNow()
        numDel = 0
        for channel in self.channels.itervalues():
            if isinstance(channel.channelID, int) and channel.info and channel.info.memberless and channel.window is not None and not channel.window.destroyed:
                delLst = []
                for charID in channel.recentSpeakerList:
                    blue.pyos.BeNice()
                    member = channel.recentSpeakerList[charID]
                    if blue.os.GetWallclockTime() - member.extra > 15 * MIN:
                        delLst.append(member.charID)

                numDel += len(delLst)
                for d in delLst:
                    self.DelRecentSpeakerFromWindow(channel, d)


        if numDel > 0:
            self.LogInfo('__DecayRecent deleted', numDel, ' recent speakers in', float(blue.os.GetWallclockTimeNow() - t) / float(SEC), 'sec')



    def DelRecentSpeakerFromWindow(self, channel, memberID):
        del channel.recentSpeakerList[memberID]
        if self.IsMemberless(channel.channelID):
            channel.window.DelRecentSpeaker(memberID)



    def OnLSC(self, channelID, estimatedMemberCount, method, who, args):
        if util.IsFullLogging():
            self.LogInfo('OnLSC(', (channelID,
             estimatedMemberCount,
             method,
             who,
             args), ')')
        while channelID in self.joiningChannels:
            self.LogInfo('OnLSC waiting until join channels completed')
            blue.pyos.synchro.SleepWallclock(250)

        (whoAllianceID, whoCorpID, who, whoRole, whoCorpRole, whoWarFactionID,) = who
        if type(who) == types.IntType:
            whoCharID = who
            whoEOL = []
        else:
            whoCharID = who[0]
            whoEOL = who
        if whoEOL and whoCharID not in cfg.eveowners:
            cfg.eveowners.Hint(whoCharID, whoEOL)
        whoMode = -1
        if channelID not in self.channels:
            if method != 'JoinChannel':
                uthread.worker('LSC::LeaveChannel', sm.RemoteSvc('LSC').LeaveChannel, channelID, 0)
            return 
        channel = self.channels[channelID]
        if self.IsMemberless(channelID):
            self._LargeScaleChat__SetEstimatedMemberCount(channel, estimatedMemberCount)
        else:
            self._LargeScaleChat__SetEstimatedMemberCount(channel, len(channel.memberList))
        if method == 'SendMessage':
            (role, ai,) = GetAccessInfo(channel, whoRole, whoCharID, whoCorpID, whoAllianceID)
            if role >= CHTMODE_SPEAKER:
                if channel.window and not channel.window.destroyed:
                    spammers = getattr(sm.GetService('LSC'), 'spammerList', set())
                    addressBookSvc = sm.GetService('addressbook')
                    isBlocked = whoCharID != session.charid and (addressBookSvc.IsBlocked(whoCharID) or addressBookSvc.IsBlocked(whoCorpID) or addressBookSvc.IsBlocked(whoAllianceID))
                    if not isBlocked and whoCharID not in spammers:
                        if whoCharID not in channel.recentSpeakerList:
                            channel.window.AddRecentSpeaker(whoCharID, whoCorpID, whoAllianceID, whoWarFactionID)
                        channel.recentSpeakerList[whoCharID] = blue.DBRow(self._LargeScaleChat__getRecentSpeakerListRowDescriptor(), [whoCharID,
                         whoCorpID,
                         whoAllianceID,
                         whoWarFactionID,
                         whoRole,
                         blue.os.GetWallclockTime()])
                        channel.window.Speak(args[0], whoCharID)
        elif method == 'VoiceNotification':
            if args[0] == 1:
                eve.Message('CustomNotify', {'notify': '%s is speaking' % who})
        elif method == 'VoiceStatus':
            if args[0] == 0:
                eve.Message('CustomNotify', {'notify': '%s has left voice chat' % who})
            if args[0] == 1:
                eve.Message('CustomNotify', {'notify': '%s has joined voice chat' % who})
            if args[0] == 2:
                eve.Message('CustomNotify', {'notify': '%s has been muted' % who})
        elif method == 'JoinChannel':
            if channel.window and not channel.window.destroyed:
                if whoCharID not in channel.memberList:
                    channel.memberList[whoCharID] = [whoCharID,
                     whoCorpID,
                     whoAllianceID,
                     whoWarFactionID,
                     whoRole,
                     blue.os.GetWallclockTime()]
                    if not self.IsMemberless(channelID):
                        self._LargeScaleChat__SetEstimatedMemberCount(channel, len(channel.memberList))
                    channel.window.AddMember(whoCharID, whoCorpID, whoAllianceID, whoWarFactionID)
        elif method == 'AnnouncePresence':
            if channel.window and not channel.window.destroyed:
                if whoCharID not in channel.memberList:
                    channel.memberList[whoCharID] = [whoCharID,
                     whoCorpID,
                     whoAllianceID,
                     whoWarFactionID,
                     whoRole,
                     blue.os.GetWallclockTime()]
                    if not self.IsMemberless(channelID):
                        self._LargeScaleChat__SetEstimatedMemberCount(channel, len(channel.memberList))
                    channel.window.AddMember(whoCharID, whoCorpID, whoAllianceID, whoWarFactionID)
        elif method == 'KickUser':
            if channel.window and not channel.window.destroyed:
                if args[0] in channel.memberList or args[0] in channel.recentSpeakerList:
                    if args[0] in channel.memberList:
                        del channel.memberList[args[0]]
                        if not self.IsMemberless(channelID):
                            self._LargeScaleChat__SetEstimatedMemberCount(channel, len(channel.memberList))
                        channel.window.DelMember(args[0])
                    if args[0] in channel.recentSpeakerList:
                        self.DelRecentSpeakerFromWindow(channel, args[0])
                    if eve.session.charid == args[0] or CHTMODE_CONVERSATIONALIST < GetAccessInfo(channel, eve.session.role, eve.session.charid, eve.session.corpid, eve.session.allianceid)[0]:
                        if args[2]:
                            reason = args[2]
                        else:
                            reason = localization.GetByLabel('UI/Generic/None')
                        if args[1]:
                            kickMsg = localization.GetByLabel('UI/Chat/KickMessageWithTime', kicked=args[0], admin=whoCharID, effectiveUntil=args[1], reason=reason)
                        else:
                            kickMsg = localization.GetByLabel('UI/Chat/KickMessage', kicked=args[0], admin=whoCharID, reason=reason)
                        channel.window.Speak(kickMsg, const.ownerSystem)
        elif method == 'LeaveChannel':
            if channel.window and not channel.window.destroyed:
                if whoCharID in channel.memberList:
                    del channel.memberList[whoCharID]
                    if not self.IsMemberless(channelID):
                        self._LargeScaleChat__SetEstimatedMemberCount(channel, len(channel.memberList))
                    channel.window.DelMember(whoCharID)
                if whoCharID in channel.recentSpeakerList:
                    self.DelRecentSpeakerFromWindow(channel, whoCharID)
        elif method == 'RenameChannel':
            channel.info.displayName = args[0]
            if channel.window is not None and not channel.window.destroyed:
                channel.window.RenameChannel(args[0])
                renameMsg = localization.GetByLabel('UI/Chat/ChannelNameChanged', newName=args[0], admin=whoCharID)
                channel.window.Speak(renameMsg, const.ownerSystem)
        elif method == 'SetChannelMOTD':
            channel.info.motd = args[0]
            if channel.window and not channel.window.destroyed:
                try:
                    if args[0]:
                        msg = localization.GetByLabel('UI/Chat/ChannelMotdChanged', newMotd=args[0], admin=whoCharID)
                    else:
                        msg = localization.GetByLabel('UI/Chat/ChannelMotdCleared', admin=whoCharID)
                    channel.window.Speak(msg, const.ownerSystem)
                except:
                    log.LogException()
                    sys.exc_clear()
        elif method == 'SetChannelLanguageRestriction':
            channel.info.languageRestriction = args[0]
            if channel.window and not channel.window.destroyed:
                try:
                    if args[0]:
                        msg = localization.GetByLabel('UI/Chat/ChannelLanguageRestrictionSet', admin=whoCharID)
                    else:
                        msg = localization.GetByLabel('UI/Chat/ChannelLanguageRestrictionCleared', admin=whoCharID)
                    channel.window.Speak(msg, const.ownerSystem)
                except:
                    log.LogException()
                    sys.exc_clear()
        elif method == 'SetChannelPassword':
            channel.info.password = args[0]
            if args[0]:
                msg = localization.GetByLabel('UI/Chat/ChannelPasswordChanged', admin=whoCharID)
            else:
                msg = localization.GetByLabel('UI/Chat/ChannelPasswordCleared', admin=whoCharID)
            channel.window.Speak(msg, const.ownerSystem)
        elif method == 'SetChannelCreator':
            if channel.window and not channel.window.destroyed:
                msg = localization.GetByLabel('UI/Chat/ChannelOwnerChanged', oldOwner=channel.info.ownerID, newOwner=args[0])
                channel.window.Speak(msg, const.ownerSystem)
                if channel.info.ownerID == const.ownerSystem or args[0] == const.ownerSystem:
                    sm.GetService('channels').RefreshMine(1)
            channel.info.ownerID = args[0]
        elif method == 'SetChannelMemberless':
            channel.info.memberless = args[0]
            if channel.window and not channel.window.destroyed:
                try:
                    if channel.info.memberless:
                        msg = localization.GetByLabel('UI/Chat/ChannelEngagedDelayedMode', admin=whoCharID)
                        channel.window.Speak(msg, const.ownerSystem)
                    else:
                        msg = localization.GetByLabel('UI/Chat/ChannelEngagedImmediateMode', admin=whoCharID, maxMembers=CHT_MAX_USERS_PER_IMMEDIATE_CHANNEL)
                        channel.window.Speak(msg, const.ownerSystem)
                        channel.memberList = args[1].Index('charID')
                        self._LargeScaleChat__SetEstimatedMemberCount(channel, len(channel.memberList), True)
                        channel.window.InitUsers(0)
                    channel.window.UpdateUserIconHint()
                except:
                    log.LogException()
                    sys.exc_clear()
        elif method == 'DestroyChannel':
            del self.channels[channelID]
            window = channel.window
            channel.window = None
            if window is not None and not window.destroyed:
                if window == sm.GetService('focus').GetFocusChannel():
                    sm.GetService('focus').SetFocusChannel()
                window.Close()
            self._LargeScaleChat__SaveChannelPrefs(channelID)
        elif method == 'AccessControl':
            done = False
            for acl in channel.acl:
                if acl.accessor == args[0]:
                    if args[1] == CHTMODE_NOTSPECIFIED:
                        channel.acl.remove(acl)
                    else:
                        acl.mode = args[1]
                        acl.untilWhen = args[2]
                        acl.originalMode = args[3]
                        acl.reason = args[4]
                        acl.admin = args[5]
                    done = True
                    if args[1] & CHTMODE_SPEAKER == CHTMODE_SPEAKER and args[2] and args[2] < blue.os.GetWallclockTime() and sm.GetService('vivox').Enabled():
                        self.LogInfo('calling voice ungag')
                        sm.GetService('vivox').UnGag(args[0], channel.channelID)
                    break

            if not done and args[1] != CHTMODE_NOTSPECIFIED:
                channel.acl.InsertNew([args[0],
                 args[1],
                 args[2],
                 args[3],
                 args[4],
                 args[5]])
            if args[0] and args[0] in (eve.session.charid, eve.session.corpid, eve.session.allianceid) and CHTMODE_LISTENER > GetAccessInfo(channel, eve.session.role, eve.session.charid, eve.session.corpid, eve.session.allianceid)[0]:
                uthread.worker('LSC::LeaveChannel', sm.RemoteSvc('LSC').LeaveChannel, channelID, 1)
                del self.channels[channelID]
                window = channel.window
                channel.window = None
                if window is not None and not window.destroyed:
                    if window == sm.GetService('focus').GetFocusChannel():
                        sm.GetService('focus').SetFocusChannel()
                    window.Close()
                self._LargeScaleChat__SaveChannelPrefs(channelID)
            elif args[0] and CHTMODE_LISTENER == args[1]:
                if args[0] in channel.memberList or args[0] in channel.recentSpeakerList:
                    if self.IsGagged(channel.channelID, args[0]):
                        if sm.GetService('vivox').Enabled():
                            if sm.GetService('vivox').IsVoiceChannel(channelID):
                                self.LogInfo('calling voice gag')
                                sm.GetService('vivox').Gag(args[0], channel.channelID, args[2])
                        if channel.window and not channel.window.destroyed:
                            if args[0] in (eve.session.charid, eve.session.corpid, eve.session.allianceid) or CHTMODE_CONVERSATIONALIST < GetAccessInfo(channel, eve.session.role, eve.session.charid, eve.session.corpid, eve.session.allianceid)[0]:
                                if args[4]:
                                    reason = args[4]
                                else:
                                    reason = localization.GetByLabel('UI/Generic/None')
                                if args[2]:
                                    muteMsg = localization.GetByLabel('UI/Chat/MuteMessageWithTime', muted=args[0], admin=whoCharID, effectiveUntil=args[2], reason=reason)
                                else:
                                    muteMsg = localization.GetByLabel('UI/Chat/MuteMessage', muted=args[0], admin=whoCharID, reason=reason)
                                channel.window.Speak(muteMsg, const.ownerSystem)
                    elif channel.window and not channel.window.destroyed:
                        if args[0] in (eve.session.charid, eve.session.corpid, eve.session.allianceid) or CHTMODE_CONVERSATIONALIST < GetAccessInfo(channel, eve.session.role, eve.session.charid, eve.session.corpid, eve.session.allianceid)[0]:
                            msg = localization.GetByLabel('UI/Chat/UnmuteMessage', unmuted=args[0], admin=whoCharID)
                            channel.window.Speak(msg, const.ownerSystem)
            elif args[0] is None:
                if channel.window and not channel.window.destroyed:
                    if args[1] == CHTMODE_CONVERSATIONALIST:
                        channel.window.Speak(localization.GetByLabel('UI/Chat/ChannelAccessAllowed', admin=whoCharID), const.ownerSystem)
                    elif args[1] == CHTMODE_SPEAKER:
                        channel.window.Speak(localization.GetByLabel('UI/Chat/ChannelAccessAllowedSpeaker', admin=whoCharID), const.ownerSystem)
                    elif args[1] == CHTMODE_NOTSPECIFIED:
                        channel.window.Speak(localization.GetByLabel('UI/Chat/ChannelAccessBlocked', admin=whoCharID), const.ownerSystem)
                    elif args[1] == CHTMODE_LISTENER:
                        channel.window.Speak(localization.GetByLabel('UI/Chat/ChannelAccessModerated', admin=whoCharID), const.ownerSystem)
            if channel.channelID == eve.session.charid:
                sm.GetService('addressbook').RefreshWindow()
                if util.IsCharacter(args[0]) and sm.GetService('addressbook').IsInAddressBook(args[0], 'contact'):
                    sm.GetService('onlineStatus').GetOnlineStatus(args[0])



    def OnCorporationMemberChanged(self, memberID, change):
        if 'corporationID' in change:
            (oldCorpID, newCorpID,) = change['corporationID']
            channelID = (('corpid', oldCorpID),)
            if oldCorpID == eve.session.corpid and channelID in self.channels:
                channel = self.channels[channelID]
                if channel.window and not channel.window.destroyed:
                    if memberID in channel.memberList:
                        del channel.memberList[memberID]
                        self._LargeScaleChat__SetEstimatedMemberCount(channel, len(channel.memberList))
                        channel.window.DelMember(memberID)



    def GetMemberInfo(self, channelID, charID):
        if channelID not in self.channels:
            return None
        if charID in self.channels[channelID].recentSpeakerList:
            return self.channels[channelID].recentSpeakerList[charID]
        if charID in self.channels[channelID].memberList:
            return self.channels[channelID].memberList[charID]



    def GetChannelInfo(self, channelID):
        return self.channels.get(channelID, None)



    def GetMembers(self, channelID, recent = 0):
        if channelID not in self.channels:
            return 
        channel = self.channels[channelID]
        if recent:
            return channel.recentSpeakerList
        if self.IsMemberless(channelID):
            if (channel.lastRefreshed is None or blue.os.GetWallclockTime() - channel.lastRefreshed >= 5 * MIN) and not stackless.getcurrent().block_trap:
                channel.lastRefreshed = blue.os.GetWallclockTime()
                ret = sm.RemoteSvc('LSC').GetMembers(channelID)
                if ret is not None:
                    channel.memberList = ret = ret.Index('charID')
                for charid in channel.memberList:
                    if charid not in cfg.eveowners:
                        member = channel.memberList[charid]
                        if member.extra and len(member.extra) > 0:
                            cfg.eveowners.Hint(charid, member.extra)

                return ret
        return channel.memberList



    def IsMemberless(self, channelID):
        self._LargeScaleChat__GetChannelList()
        if channelID not in self.channels:
            return True
        else:
            channel = self.channels[channelID]
            if isinstance(channelID, int) and channel.info is not None:
                return channel.info.memberless
            for (attribute, value,) in channelID:
                if attribute == 'corpid' and not util.IsNPC(value) or attribute == 'fleetid' or attribute == 'squadid' or attribute == 'wingid' or attribute == 'solarsystemid2' and not util.IsMemberlessLocal(channelID):
                    return False

            return True



    def IsJoined(self, channelID):
        self._LargeScaleChat__GetChannelList()
        if channelID not in self.channels:
            return False
        if isinstance(channelID, int) and self.channels[channelID].info is not None and self.channels[channelID].info.mailingList:
            return self.channelListIndexed[channelID].subscribed
        if self.channels[channelID].window is None or self.channels[channelID].window.destroyed:
            return False
        return True



    def GetMyAccessInfo(self, channelID):
        self._LargeScaleChat__GetChannelList()
        if channelID not in self.channels:
            return None
        channel = self.channels[channelID]
        return GetAccessInfo(channel, eve.session.role, eve.session.charid, eve.session.corpid, eve.session.allianceid)



    def IsSpeaker(self, channelID):
        self._LargeScaleChat__GetChannelList()
        if channelID not in self.channels:
            return 0
        channel = self.channels[channelID]
        return CHTMODE_SPEAKER <= GetAccessInfo(channel, eve.session.role, eve.session.charid, eve.session.corpid, eve.session.allianceid)[0]



    def IsLanguageRestricted(self, channelID):
        self._LargeScaleChat__GetChannelList()
        if channelID not in self.channels:
            return 0
        channel = self.channels[channelID]
        if isinstance(channelID, tuple) or channel.info is None:
            return 0
        return channel.info.languageRestriction



    def __GetChannelList(self, refresh = 0):
        if eve.rookieState and eve.rookieState < sm.GetService('tutorial').GetOtherRookieFilter('defaultchannels'):
            return []
        s = self.semaphore
        s.acquire()
        try:
            last = blue.pyos.taskletTimer.EnterTasklet('LSCEngine::GetChannelList')
            try:
                if refresh or self.channelList is None:
                    self.channelList = sm.RemoteSvc('LSC').GetChannels()
                    self.channelListIndexed = self.channelList.Index('channelID')
                    self.forgettables = {}
                    join = []
                    __niow__ = (const.ownerSystem, eve.session.charid)
                    for channel in self.channelList:
                        ownerID = channel.ownerID
                        channelID = channel.channelID
                        mailingList = channel.mailingList
                        subscribed = channel.subscribed
                        last2 = blue.pyos.taskletTimer.EnterTasklet('LSCEngine::GetChannelList::OtherStuff')
                        try:
                            if ownerID not in __niow__:
                                self.forgettables[channelID] = True
                            if mailingList and subscribed:
                                if channelID not in join and channelID in (session.charid, session.corpid, session.allianceid):
                                    join.append(channelID)
                            if channelID == self.rookieHelpChannel and channelID not in join and eve.session.role & service.ROLE_NEWBIE and not self.rookieJoined:
                                self.rookieJoined = True
                                join.append(self.rookieHelpChannel)

                        finally:
                            blue.pyos.taskletTimer.ReturnFromTasklet(last2)


                    if join:
                        uthread.worker('LSC::__GetChannelList::JoinChannels', self.JoinChannels, join, maximize=0)

            finally:
                blue.pyos.taskletTimer.ReturnFromTasklet(last)

            return self.channelList

        finally:
            s.release()




    def GetChannels(self, refresh = 0):
        channelList = []
        for channel in self._LargeScaleChat__GetChannelList(refresh):
            if not channel.mailingList:
                channelList.append(channel)

        if eve.session is not None and eve.session.charid:
            tmp = []
            if eve.session.regionid:
                tmp.append((('regionid', eve.session.regionid),))
            if eve.session.constellationid:
                tmp.append((('constellationid', eve.session.constellationid),))
            if eve.session.solarsystemid2:
                tmp.append((('solarsystemid2', eve.session.solarsystemid2),))
            if eve.session.allianceid:
                tmp.append((('allianceid', eve.session.allianceid),))
            if eve.session.corpid:
                tmp.append((('corpid', eve.session.corpid),))
            if eve.session.fleetid:
                tmp.append((('fleetid', eve.session.fleetid),))
            if eve.session.warfactionid:
                tmp.append((('warfactionid', eve.session.warfactionid),))
            if eve.session.role & (service.ROLE_LEGIONEER | service.ROLE_GML) > 0:
                schools = sm.GetService('cc').GetData('schools')
                for s in schools:
                    tmp.append((('corpid', s.corporationID),))

            for channelID in tmp:
                if channelID in self.channels:
                    emc = self.channels[channelID].estimatedMemberCount
                else:
                    emc = 0
                channelList.append(util.KeyVal(channelID=channelID, displayName=None, estimatedMemberCount=emc, groupMessageID=const.CHAT_SYSTEM_CHANNEL, channelMessageID=GetDisplayName(channelID), temporary=0))

        return channelList



    def GetChannelWindow(self, channelID):
        if (channelID,) in self.channels:
            channelID = (channelID,)
        if channelID in self.channels:
            return self.channels[channelID].window



    def IsForgettable(self, channelID):
        self._LargeScaleChat__GetChannelList()
        if type(channelID) != types.IntType:
            return 0
        if self.IsJoined(channelID):
            return 0
        return self.forgettables.get(channelID, 0)



    def IsOperator(self, channelID, charID = None):
        self._LargeScaleChat__GetChannelList()
        if channelID not in self.channels:
            return 0
        channel = self.channels[channelID]
        if charID is None:
            charID = eve.session.charid
            corpID = eve.session.corpid
            allianceID = eve.session.allianceid
            role = eve.session.role
        else:
            corpID = None
            allianceID = None
            role = 0
            if charID in channel.memberList:
                corpID = channel.memberList[charID].corpID
                allianceID = channel.memberList[charID].allianceID
                role = channel.memberList[charID].role
            elif charID in channel.recentSpeakerList:
                corpID = channel.recentSpeakerList[charID].corpID
                allianceID = channel.recentSpeakerList[charID].allianceID
                role = channel.recentSpeakerList[charID].role
        return CHTMODE_OPERATOR <= GetAccessInfo(channel, role, charID, corpID, allianceID)[0]



    def GetMemberCount(self, channelID):
        if channelID not in self.channels:
            return 0
        else:
            channel = self.channels[channelID]
            if self.IsMemberless(channelID):
                return channel.estimatedMemberCount
            return len(channel.memberList)



    def __SetEstimatedMemberCount(self, channel, emc, forceUpdate = False):
        if emc is not None:
            if channel.estimatedMemberCount == emc:
                return 
            channel.estimatedMemberCount = emc
        if self.channelList is not None:
            for each in self.channelList:
                if channel.channelID == each.channelID:
                    each.estimatedMemberCount = channel.estimatedMemberCount

            if channel.channelID in self.channelListIndexed:
                self.channelListIndexed[channel.channelID].estimatedMemberCount = channel.estimatedMemberCount
        if forceUpdate or self.lastEMCUpdate > 0 and blue.os.GetWallclockTime() - self.lastEMCUpdate >= MINIMUM_EMC_UPDATE_TIME:
            self._LargeScaleChat__UpdateEMC()



    def __UpdateEMC(self):
        if not self.updateEMC:
            self.lastEMCUpdate = blue.os.GetWallclockTime()
            self.updateEMC = True
            uthread.worker('LSC::UpdateEMCWorker', self._LargeScaleChat__UpdateEMCWorker)



    def __UpdateEMCWorker(self):
        if not self.updateEMC:
            return 
        self.updateEMC = False
        sm.GetService('channels').RefreshMine()



    def IsCreator(self, channelID):
        self._LargeScaleChat__GetChannelList()
        if channelID not in self.channels:
            return 0
        channel = self.channels[channelID]
        return CHTMODE_CREATOR == GetAccessInfo(channel, eve.session.role, eve.session.charid, eve.session.corpid, eve.session.allianceid)[0]



    def IsOwner(self, channelInfo):
        if getattr(channelInfo, 'ownerID', None) == session.charid:
            return 1
        return 0



    def __getRecentSpeakerListRowDescriptor(self):
        return blue.DBRowDescriptor((('charID', const.DBTYPE_I4),
         ('corpID', const.DBTYPE_I4),
         ('allianceID', const.DBTYPE_I4),
         ('warFactionID', const.DBTYPE_I4),
         ('role', const.DBTYPE_I8),
         ('extra', const.DBTYPE_FILETIME)))



    def IsGagged(self, channelID, charID):
        self._LargeScaleChat__GetChannelList()
        if channelID not in self.channels:
            return 0
        channel = self.channels[channelID]
        if charID == eve.session.charid:
            return CHTMODE_SPEAKER > GetAccessInfo(channel, eve.session.role, eve.session.charid, eve.session.corpid, eve.session.allianceid)[0]
        if charID in channel.recentSpeakerList:
            return CHTMODE_SPEAKER > GetAccessInfo(channel, channel.recentSpeakerList[charID].role, charID, channel.recentSpeakerList[charID].corpID, channel.recentSpeakerList[charID].allianceID)[0]
        if charID in channel.memberList:
            return CHTMODE_SPEAKER > GetAccessInfo(channel, channel.memberList[charID].role, charID, channel.memberList[charID].corpID, channel.memberList[charID].allianceID)[0]
        return CHTMODE_SPEAKER > GetAccessInfo(channel, 0, charID)[0]



    def CreateOrJoinChannel(self, displayName, create = True):
        displayName = displayName.strip()
        s = self.semaphore
        s.acquire()
        try:
            if self.channelList is not None:
                found = False
                for channel in self.channelList:
                    if channel.displayName and util.CaseFoldEquals(channel.displayName.strip(), displayName):
                        found = True
                        break

                if not found:
                    self.channelList = None

        finally:
            s.release()

        if create == True:
            eve.Message('ChannelTryingToCreate')
            ret = sm.RemoteSvc('LSC').CreateChannel(displayName, joinExisting=False, memberless=0, create=True)
            if ret:
                (info, acl, memberList,) = ret
            else:
                return 
            if info == CHTERR_ALREADYEXISTS:
                if eve.Message('LSCJoinInstead', {'displayName': displayName}, uiconst.YESNO) == uiconst.ID_YES:
                    eve.Message('ChannelTryingToJoin')
                    ret = sm.RemoteSvc('LSC').CreateChannel(displayName, joinExisting=True, memberless=0, create=False)
                    if ret:
                        (info, acl, memberList,) = ret
                    else:
                        return 
                else:
                    return 
        else:
            eve.Message('ChannelTryingToJoin')
            ret = sm.RemoteSvc('LSC').CreateChannel(displayName, joinExisting=True, memberless=0, create=False)
            if ret:
                (info, acl, memberList,) = ret
            else:
                return 
            if info == CHTERR_NOSUCHCHANNEL:
                if eve.Message('LSCChannelDoesNotExistCreate', {'displayName': displayName}, uiconst.YESNO) == uiconst.ID_YES:
                    eve.Message('ChannelTryingToCreate')
                    (info, acl, memberList,) = sm.RemoteSvc('LSC').CreateChannel(displayName, joinExisting=False, memberless=0, create=True)
                else:
                    return 
        if info.channelID in self.channels:
            window = self.channels[info.channelID].window
            if window is not None and not window.destroyed:
                window.Maximize()
                return 
        wndID = 'chatchannel_%s' % ConfigKeyFromChannelID(info.channelID)
        window = form.LSCChannel.Open(windowID=wndID, showIfInStack=self.ShowIfInStack(), channelID=-1)
        recentSpeakerList = dbutil.CRowset(self._LargeScaleChat__getRecentSpeakerListRowDescriptor(), []).Index('charID')
        memberList = memberList.Index('charID')
        self.channels[info.channelID] = util.KeyVal(channelID=info.channelID, info=info, acl=acl, recentSpeakerList=recentSpeakerList, memberList=memberList, window=window, estimatedMemberCount=1, lastRefreshed=None)
        if window and not window.destroyed:
            window.Startup(info.channelID)
        self._LargeScaleChat__SetEstimatedMemberCount(self.channels[info.channelID], None, True)
        self._LargeScaleChat__SaveChannelPrefs()
        sm.ScatterEvent('OnChannelsJoined', [info.channelID])



    def __InvalidateChannelList(self, channelID):
        s = self.semaphore
        s.acquire()
        try:
            if self.channelList is not None:
                found = False
                for channel in self.channelList:
                    if channel.channelID == channelID:
                        found = True
                        break

                if not found:
                    self.channelList = None

        finally:
            s.release()




    def Invite(self, otherID, channelID = None):
        if type(otherID) not in (types.IntType, types.LongType):
            log.LogTraceback('Illegal otherID %s' % (otherID,))
            eve.Message('CustomError', {'error': localization.GetByLabel('UI/Chat/ErrorNotACharacter')})
            return 
        if util.IsNPC(otherID) or not util.IsCharacter(otherID):
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Chat/ErrorNotAPlayerCharacter')})
            return 
        if channelID:
            self._LargeScaleChat__InvalidateChannelList(channelID)
            self.JoinChannel(channelID)
            channelName = self.channels[channelID].info.displayName
            addAllowed = True
            for channel in self.channels[channelID].acl:
                accessor = channel.accessor
                mode = channel.mode
                if accessor is None and mode >= CHTMODE_SPEAKER:
                    addAllowed = False
                    break

            util.CSPAChargedAction('CSPAChatCheck', sm.RemoteSvc('LSC'), 'Invite', otherID, channelID, channelName, addAllowed)
        else:
            (info, acl, memberList,) = sm.RemoteSvc('LSC').CreateChannel('Private Chat', joinExisting=False, temporary=True, noCallThrottling=True)
            channelID = info.channelID
            self._LargeScaleChat__InvalidateChannelList(channelID)
            self.joiningChannels[channelID] = 1
            try:
                if info.channelID in self.channels:
                    window = self.channels[info.channelID].window
                    if window is not None and not window.destroyed:
                        window.Maximize()
                        util.CSPAChargedAction('CSPAChatCheck', sm.RemoteSvc('LSC'), 'Invite', otherID, channelID, 'Private Chat', False)
                        return 
                recentSpeakerList = dbutil.CRowset(self._LargeScaleChat__getRecentSpeakerListRowDescriptor(), []).Index('charID')
                memberList = memberList.Index('charID')
                self.channels[info.channelID] = util.KeyVal(channelID=info.channelID, info=info, acl=acl, recentSpeakerList=recentSpeakerList, memberList=memberList, window=None, estimatedMemberCount=1, lastRefreshed=None)
                try:
                    invited = util.CSPAChargedAction('CSPAChatCheck', sm.RemoteSvc('LSC'), 'Invite', otherID, channelID, 'Private Chat', False)
                    if not invited:
                        self.LeaveChannel(info.channelID)
                        return 
                except:
                    self.LeaveChannel(info.channelID)
                    raise 
                self._LargeScaleChat__SaveChannelPrefs()
                wndID = 'chatchannel_%s' % ConfigKeyFromChannelID(info.channelID)
                window = form.LSCChannel.Open(windowID=wndID, showIfInStack=self.ShowIfInStack(), channelID=-1)
                self.channels[info.channelID].window = window
                self._LargeScaleChat__SetEstimatedMemberCount(self.channels[info.channelID], None, True)
                if window and not window.destroyed:
                    window.Startup(info.channelID, otherID)

            finally:
                del self.joiningChannels[channelID]




    def __JoinChannelHelper(self, channelID, info, acl, memberList, restoreWindows):
        memberList = memberList.Index('charID')
        recentSpeakerList = dbutil.CRowset(self._LargeScaleChat__getRecentSpeakerListRowDescriptor(), []).Index('charID')
        if isinstance(channelID, int) and info is not None and info.mailingList:
            self.channels[channelID] = util.KeyVal(channelID=channelID, info=info, acl=acl, recentSpeakerList=recentSpeakerList, memberList=memberList, window=None, estimatedMemberCount=len(memberList), lastRefreshed=None)
        else:
            for charID in memberList:
                member = memberList[charID]
                if member.extra and charID not in cfg.eveowners:
                    cfg.eveowners.Hint(charID, member.extra)
                    member.extra = None

            k = ChannelRecyclableHash(channelID)
            if k in restoreWindows:
                window = restoreWindows[k]
                del restoreWindows[k]
                self.channels[channelID] = util.KeyVal(channelID=channelID, info=info, acl=acl, recentSpeakerList=recentSpeakerList, memberList=memberList, window=window, estimatedMemberCount=len(memberList), lastRefreshed=None)
                if self.IsMemberless(channelID):
                    self.channels[channelID].lastRefreshed = blue.os.GetWallclockTime()
                window.Restart(channelID)
            else:
                wndID = 'chatchannel_%s' % ConfigKeyFromChannelID(channelID)
                wndExist = form.LSCChannel.GetIfOpen(windowID=wndID)
                window = form.LSCChannel.Open(windowID=wndID, showIfInStack=self.ShowIfInStack(), channelID=-1)
                self.channels[channelID] = util.KeyVal(channelID=channelID, info=info, acl=acl, recentSpeakerList=recentSpeakerList, memberList=memberList, window=window, estimatedMemberCount=len(memberList), lastRefreshed=None)
                if self.IsMemberless(channelID):
                    if channelID not in self.channels:
                        self.LogError('Channel ', channelID, 'removed while joining')
                        return 
                    self.channels[channelID].lastRefreshed = blue.os.GetWallclockTime()
                if not wndExist and window and not window.destroyed:
                    window.Startup(channelID)
                if eve.rookieState and eve.rookieState < sm.GetService('tutorial').GetOtherRookieFilter('defaultchannels'):
                    self.LeaveChannel(channelID)
                    return 
        self._LargeScaleChat__SaveChannelPrefs(channelID)
        self._LargeScaleChat__SetEstimatedMemberCount(self.channels[channelID], None, True)



    def ShowIfInStack(self):
        currentFocusChannel = sm.GetService('focus').GetFocusChannel()
        if currentFocusChannel and not currentFocusChannel.destroyed and currentFocusChannel.input == uicore.registry.GetFocus():
            return 0
        return 1



    def JoinChannel(self, channelID):
        return self.JoinChannels([channelID])



    def JoinOrLeaveChannel(self, channelID, onlyJoin = False):
        s = sm.StartService('channels').semaphore
        s.acquire()
        try:
            if sm.GetService('LSC').IsJoined(channelID):
                if not onlyJoin:
                    sm.GetService('LSC').LeaveChannel(channelID)
            else:
                sm.GetService('LSC').JoinChannel(channelID)

        finally:
            s.release()

        sm.ScatterEvent('OnJoinLeaveChannel', channelID)



    def JoinChannels(self, channelIDs, restoreWindows = {}, maximize = 0):
        if sm.GetService('vivox').Subscriber():
            sm.GetService('vivox').Init()
        if eve.rookieState and eve.rookieState < sm.GetService('tutorial').GetOtherRookieFilter('defaultchannels'):
            return 
        toJoin = []
        for channelID in channelIDs:
            channelID = ChannelHash(channelID)
            if channelID in self.channels:
                channel = self.channels[channelID]
                if isinstance(channelID, int) and channel.info is not None and channel.info.mailingList:
                    pass
            else:
                window = channel.window
                if window is not None and not window.destroyed:
                    if maximize:
                        window.Maximize()
                        continue
                        continue
                if channelID not in self.joiningChannels:
                    self.joiningChannels[channelID] = 1
                    toJoin.append(channelID)

        try:
            if not toJoin:
                return 
            ret = sm.RemoteSvc('LSC').JoinChannels(toJoin, eve.session.role)
            argsList = []
            for (channelID, ok, tmp,) in ret:
                if not ok or not tmp:
                    self._LargeScaleChat__SaveChannelPrefs(channelID)
                    continue
                (info, acl, memberList,) = tmp
                argsList.append((channelID,
                 info,
                 acl,
                 memberList,
                 restoreWindows))

            self.CallJoinChannelHelper(argsList)
            s = self.semaphore
            s.acquire()
            try:
                (m, c,) = (False, False)
                for (channelID, ok, tmp,) in ret:
                    if ok:
                        continue
                    (msg, dict,) = tmp
                    if msg in ('LSCCannotJoin', 'LSCWrongPassword') and type(channelID) == types.IntType:
                        self._LargeScaleChat__SaveChannelPrefs(channelID)
                    uthread.new(eve.Message, msg, dict)
                    if self.channelList is not None:
                        for channel in self.channelList:
                            if channel.channelID == channelID:
                                if channel.mailingList:
                                    m = True
                                else:
                                    c = True
                                break



            finally:
                s.release()

            if c:
                uthread.worker('LSC::JoinChannels::RefreshMine', sm.GetService('channels').RefreshMine)

        finally:
            for channelID in toJoin:
                if channelID in self.joiningChannels:
                    del self.joiningChannels[channelID]

            sm.ScatterEvent('OnChannelsJoined', toJoin)




    def CallJoinChannelHelper(self, argsList):
        for args in argsList:
            self._LargeScaleChat__JoinChannelHelper(*args)




    def OpenChannel(self, channelID, ok, tmp, restoreWindows = {}, maximize = 0):
        if not tmp:
            self._LargeScaleChat__SaveChannelPrefs(channelID)
            return 
        lock = self.semaphore
        lock.acquire()
        try:
            (mail, refresh,) = (False, False)
            if ok:
                (info, acl, memberList,) = tmp
                uthread.new(self._LargeScaleChat__JoinChannelHelper, channelID, info, acl, memberList, restoreWindows)
            else:
                (msg, dict,) = tmp
                if msg in ('LSCCannotJoin', 'LSCWrongPassword') and type(channelID) == types.IntType:
                    self._LargeScaleChat__SaveChannelPrefs(channelID)
                uthread.new(eve.Message, msg, dict)
                if self.channelList is not None:
                    for channel in self.channelList:
                        if channel.channelID == channelID:
                            if channel.mailingList:
                                mail = True
                            else:
                                refresh = True
                            break


        finally:
            lock.release()

        if refresh:
            uthread.worker('LSC::JoinChannels::RefreshMine', sm.GetService('channels').RefreshMine)



    def LeaveChannel(self, channelID, unsubscribe = False, destruct = True):
        return self.LeaveChannels([channelID], unsubscribe, destruct=destruct)



    def LeaveChannels(self, channelIDs, unsubscribe = False, saveWindows = None, savePrefs = True, sessionChangeDriven = False, destruct = True):
        toLeave = []
        for channelID in channelIDs:
            channelID = ChannelHash(channelID)
            try:
                announce = False
                if channelID in self.channels:
                    channel = self.channels[channelID]
                    if eve.session.charid in channel.recentSpeakerList:
                        announce = True
                    elif not self.IsMemberless(channelID):
                        announce = True
                        self._LargeScaleChat__SetEstimatedMemberCount(self.channels[channelID], 0, True)
                    elif type(channelID) == types.IntType:
                        announce = channel.info and not channel.info.memberless and not channel.info.mailingList
                    del self.channels[channelID]
                    if channel.window is not None and not channel.window.destroyed:
                        if saveWindows is not None:
                            k = ChannelRecyclableHash(channelID)
                            saveWindows[k] = channel.window
                            channel.window = None
                        else:
                            wnd = channel.window
                            channel.window = None
                            if wnd == sm.GetService('focus').GetFocusChannel():
                                sm.GetService('focus').SetFocusChannel()
                            if destruct:
                                wnd.Close()
                    if not sessionChangeDriven or type(channelID) == types.IntType or channelID[0] != 'solarsystemid2':
                        toLeave.append((channelID, announce))
                if unsubscribe and channelID in self.channelListIndexed:
                    self.channelListIndexed[channelID].subscribed = 0
                    for each in self.channelList:
                        if each.channelID == channelID:
                            each.subscribed = 0
                            break


            finally:
                if savePrefs:
                    self._LargeScaleChat__SaveChannelPrefs(channelID)
                sm.ScatterEvent('OnChannelsLeft', toLeave)


        if toLeave:
            uthread.worker('LSCEngine::LeaveChannels::Leave', self.Leave, toLeave, unsubscribe)



    def Leave(self, leave, unsubscribe):
        sm.RemoteSvc('LSC').LeaveChannels(leave, unsubscribe, eve.session.role)
        self._LargeScaleChat__UpdateEMC()



    def DestroyChannel(self, channelInfo, *args):
        channelID = channelInfo.channelID
        if type(channelID) != types.IntType:
            raise UserError('LSCCannotDestroy', {'msg': localization.GetByLabel('UI/Chat/ErrorCannotDestroySystemChannel')})
        displayName = channelInfo.displayName
        if eve.Message('LSCConfirmDestroyChannel', {'displayName': displayName}, uiconst.YESNO) != uiconst.ID_YES:
            return 
        try:
            sm.RemoteSvc('LSC').DestroyChannel(channelID, *args)

        finally:
            self._LargeScaleChat__SaveChannelPrefs(channelID)




    def ForgetChannel(self, *args):
        sm.RemoteSvc('LSC').ForgetChannel(*args)



    def RenameChannel(self, *args):
        sm.RemoteSvc('LSC').RenameChannel(*args)



    def SetChannelMOTD(self, *args):
        sm.RemoteSvc('LSC').SetChannelMOTD(*args)



    def SetChannelLanguageRestriction(self, *args):
        sm.RemoteSvc('LSC').SetChannelLanguageRestriction(*args)



    def SendMessage(self, channelID, message):
        if channelID not in self.channels:
            raise RuntimeError("You're not in that channel.  Close the window please...")
        channel = self.channels[channelID]
        (role, ai,) = GetAccessInfo(channel, eve.session.role, eve.session.charid, eve.session.corpid, eve.session.allianceid)
        if role < CHTMODE_SPEAKER:
            if ai is None or not ai.untilWhen or not ai.reason or not ai.admin:
                raise UserError('LSCCannotSendMessage', {'msg': localization.GetByLabel('UI/Chat/ChatEngine/YouAreNotAbleToSpeak')})
            else:
                reason = ai.reason or localization.GetByLabel('UI/Chat/NotSpecified')
                untilwhen = [(DATETIME, ai.untilWhen), localization.GetByLabel('UI/Chat/NotSpecified')][(ai.untilWhen is None)]
                gagger = ai.admin or localization.GetByLabel('UI/Chat/NotSpecified')
            raise UserError('YouHaveBeenGagged', {'reason': reason,
             'untilwhen': untilwhen,
             'gagger': gagger})
        if type(message) not in types.StringTypes:
            message = str(message)
        if len(message) > CHT_MAX_INPUT:
            message = message[:CHT_MAX_INPUT] + '...'
        sm.RemoteSvc('LSC').SendMessage(channelID, message)



    def AccessControl(self, *args):
        sm.RemoteSvc('LSC').AccessControl(*args)



    def Settings(self, channelID):
        if not self.IsOperator(channelID):
            if isinstance(channelID, tuple):
                channelType = channelID[0][0]
                if channelType in ('corpid', 'allianceid'):
                    if session.corprole & const.corpRoleChatManager != const.corpRoleChatManager:
                        return 
                elif channelType == 'fleetid':
                    if not sm.GetService('fleet').IsBoss():
                        return 
                else:
                    return 
            else:
                return 
        dlg = form.ChannelSettingsDialog.Open(channelID=channelID)
        dlg.ShowModal()
        acls = dlg.acls
        if dlg.config:
            if isinstance(channelID, tuple) and channelID[0][0] == 'fleetid':
                newMotd = dlg.config.get('motd', None)
                if newMotd:
                    sm.GetService('fleet').SetRemoteMotd(newMotd)
            else:
                sm.RemoteSvc('LSC').Configure(channelID, **dlg.config)
        if acls:
            for (k, v,) in acls.iteritems():
                if type(v) == types.IntType:
                    sm.RemoteSvc('LSC').AccessControl(channelID, k, v)
                else:
                    sm.RemoteSvc('LSC').AccessControl(channelID, k, *v)




    def GetChannelPasswordAndJoin(self, title, channelID, displayName):
        uthread.new(self.AttemptToOpenChannel_thread, title, channelID, displayName)



    def AttemptToOpenChannel_thread(self, title, channelID, displayName):
        success = False
        channelname = 'LSC:' + str(channelID)
        self.settings.LoadSettings()
        password = settings.user.ui.Get('%sPassword' % channelname, '')
        if password:
            success = self.TryOpenChannel(channelID, channelname, password, savePassword=1)
        if success is False:
            self.PromptForPassword(title, channelID, channelname, displayName)



    def PromptForPassword(self, title, channelID, channelname, displayName):
        settings.user.ui.Set('%sPassword' % channelname, '')
        tries = 3
        tmp = None
        savePassword = 0
        for retry in range(tries):
            if retry > 0:
                label = localization.GetByLabel('UI/Menusvc/PleaseTryEnteringPasswordAgain')
            else:
                label = localization.GetByLabel('UI/Menusvc/PleaseEnterPassword')
            format = [{'type': 'btline'},
             {'type': 'labeltext',
              'label': label,
              'text': '',
              'frame': 1,
              'labelwidth': 240},
             {'type': 'edit',
              'setvalue': '',
              'label': '_hide',
              'key': 'name',
              'required': 1,
              'frame': 1,
              'maxLength': 50,
              'passwordChar': u'\u2022',
              'setfocus': 1},
             {'type': 'checkbox',
              'required': 1,
              'setvalue': savePassword,
              'key': 'savepassword',
              'label': '_hide',
              'text': localization.GetByLabel('UI/Chat/SavePassword'),
              'frame': 1},
             {'type': 'bbline'},
             {'type': 'errorcheck',
              'errorcheck': uix.NamePopupErrorCheck}]
            retval = uix.HybridWnd(format, title, 1, None, uiconst.OKCANCEL, minW=240, minH=100)
            if retval is None:
                password = None
                break
            password = retval.get('name', '')
            savePassword = retval.get('savepassword', 0)
            tmp = self.TryOpenChannel(channelID, channelname, password, savePassword)
            if tmp is True:
                return 
            if tmp is None:
                break

        if tmp is False and password is not None:
            self.OpenChannel(channelID, 0, ('LSCWrongPassword', {'channelName': displayName}))



    def TryOpenChannel(self, channelID, channelname, password, savePassword = 0):
        try:
            if password is not None:
                tmp = sm.RemoteSvc('LSC').JoinChannel(channelID, password=password)
                if tmp is not None:
                    if savePassword == 1:
                        settings.user.ui.Set('%sPassword' % channelname, password)
                    else:
                        settings.user.ui.Set('%sPassword' % channelname, '')
                    self.OpenChannel(channelID, 1, tmp)
                    return True
                settings.user.ui.Set('%sPassword' % channelname, '')
            else:
                return 
        except (UserError,) as e:
            sys.exc_clear()
            self.OpenChannel(channelID, 0, (e.msg, e.dict))
            return 
        except (RuntimeError,) as e:
            sys.exc_clear()
            self.OpenChannel(channelID, 0, e.args)
            return 
        return False



    def AskYesNoQuestion(self, question, props, defaultChoice = 1):
        if defaultChoice:
            defaultChoice = uiconst.ID_YES
        else:
            defaultChoice = uiconst.ID_NO
        return eve.Message(question, props, uiconst.YESNO, defaultChoice) == uiconst.ID_YES



    def GetChannelMessages(self):
        bs = []
        for channelID in self.channels:
            try:
                channel = self.channels[channelID]
                if channel.window:
                    messages = []
                    for each in channel.window.messages:
                        messages.append(each[0:4])

                    bs.append((channel.window.sr.caption.text, messages))
            except:
                log.LogException()
                sys.exc_clear()

        return bs



    def ChatInvite(self, invitorID, invitorName, invitorGender, channelID, uberdude = 0):
        try:
            if not uberdude:
                reason = self._LargeScaleChat__ConfirmInvitation(invitorID, invitorName, invitorGender, channelID)
                if reason is not None:
                    return reason
            if not self.IsJoined(channelID):
                self._LargeScaleChat__InvalidateChannelList(channelID)
                self.JoinChannel(channelID)
        except:
            log.LogException()
            sys.exc_clear()
            return 'ChtInviteException'



    def __ConfirmInvitation(self, invitorID, invitorName, invitorGender, channelID):
        self.settings.LoadSettings()
        if invitorID == eve.session.charid:
            return 'ChtCannotInviteSelf'
        blocked = sm.GetService('addressbook').IsBlocked(invitorID)
        if blocked:
            return 'ChtBlockedBefore'
        if settings.user.ui.Get('autoRejectInvitations', 0):
            return 'ChtRejected'
        if sm.GetService('addressbook').IsInAddressBook(invitorID, 'contact'):
            return 
        if form.ChatInviteWnd.GetIfOpen(windowID='Chat Invitation from %s' % invitorName):
            return 'ChtAlreadyInvited'
        if channelID in self.channels:
            return 'ChtAlreadyInChannel'
        if currentcall:
            currentcall.UnLockSession()
        wnd = form.ChatInviteWnd.Open(windowID='Chat Invitation from %s' % invitorName, invitorID=invitorID, invitorName=invitorName)
        if wnd.OnScale_:
            wnd.OnScale_(wnd)
        stack = uicore.registry.GetStack('invitestack', useDefaultPos=True)
        if stack is not None:
            stack.InsertWnd(wnd, 0, 1, 1)
            stack.MakeUnResizeable()
        state = uiconst.UI_PICKCHILDREN
        if wnd.sr.stack is None:
            state = uiconst.UI_NORMAL
        dialog = wnd.ShowDialog(modal=False, state=state)
        retval = wnd.result
        if retval:
            if retval == 'accept':
                return 
            if retval == 'acceptadd':
                uthread.new(sm.GetService('addressbook').AddToPersonal, invitorID, 'contact')
                return 
            if retval == 'block':
                uthread.new(sm.GetService('addressbook').BlockOwner, invitorID)
                return 'ChtBlockedNow'
        return 'ChtRejected'



    def GetChannelIDFromName(self, channelName, *args):
        if self.channelList is None:
            return 
        for channel in self.channelList:
            if channel.displayName and channel.displayName.lower() == channelName.lower():
                return channel.channelID





class ChannelSettingsDialog(uicls.Window):
    __guid__ = 'form.ChannelSettingsDialog'
    __notifyevents__ = ['OnLSC']
    default_windowID = 'ChannelSettingsDialog'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.channelID = attributes.channelID
        self.config = None
        self.searchStr = ''
        self.acls = {}
        self.config = {}
        self.defaultAccess = None
        self.SetScope('all')
        self.Confirm = self.ValidateOK
        self.SetWndIcon('ui_9_64_2')
        self.SetMinSize([315, 345])
        self.sr.generaltab = uicls.Container(name='tab', parent=self.sr.main, align=uiconst.TOALL, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding, state=uiconst.UI_HIDDEN)
        self.sr.allowedtab = uicls.Container(name='tab', parent=self.sr.main, align=uiconst.TOALL, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding, state=uiconst.UI_HIDDEN)
        self.sr.blockedtab = uicls.Container(name='tab', parent=self.sr.main, align=uiconst.TOALL, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding, state=uiconst.UI_HIDDEN)
        self.sr.operatorstab = uicls.Container(name='tab', parent=self.sr.main, align=uiconst.TOALL, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding, state=uiconst.UI_HIDDEN)
        self.sr.mutedtab = uicls.Container(name='tab', parent=self.sr.main, align=uiconst.TOALL, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding, state=uiconst.UI_HIDDEN)
        self.sr.gamemasterstab = uicls.Container(name='tab', parent=self.sr.main, align=uiconst.TOALL, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding, state=uiconst.UI_HIDDEN)
        self.sr.standardBtns = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Common/Buttons/OK'),
          self.OnOK,
          (),
          81], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.OnCancel,
          (),
          81]])
        self.sr.main.children.insert(0, self.sr.standardBtns)
        self.sr.hint = None
        channel = sm.GetService('LSC').GetChannelInfo(self.channelID)
        if not channel.info.mailingList:
            self.SetCaption(localization.GetByLabel('UI/Chat/ChannelConfiguration'))
        self.maintabs = uicls.TabGroup(name='tabparent', parent=self.sr.main, idx=0)
        propertyPages = [[localization.GetByLabel('UI/Generic/General'),
          self.sr.generaltab,
          self,
          'general']]
        if isinstance(self.channelID, int):
            propertyPages.append([localization.GetByLabel('UI/Chat/Allowed'),
             self.sr.allowedtab,
             self,
             'allowed'])
            propertyPages.append([localization.GetByLabel('UI/Chat/Blocked'),
             self.sr.blockedtab,
             self,
             'blocked'])
            propertyPages.append([localization.GetByLabel('UI/Chat/Muted'),
             self.sr.mutedtab,
             self,
             'muted'])
            propertyPages.append([localization.GetByLabel('UI/Chat/Operators'),
             self.sr.operatorstab,
             self,
             'operators'])
            if eve.session.role & (service.ROLE_CHTADMINISTRATOR | service.ROLE_GMH):
                propertyPages.append([localization.GetByLabel('UI/Chat/GMExtras'),
                 self.sr.gamemasterstab,
                 self,
                 'gamemasters'])
        self.maintabs.Startup(propertyPages, 'channelconfigurationpanel', autoselecttab=1)



    def Load(self, args):
        tab = None
        if args == 'general':
            tab = self.sr.generaltab
            self.OnGeneralTab()
        elif args == 'allowed':
            tab = self.sr.allowedtab
            self.OnAllowedTab()
        elif args == 'blocked':
            tab = self.sr.blockedtab
            self.OnBlockedTab()
        elif args == 'operators':
            tab = self.sr.operatorstab
            self.OnOperatorsTab()
        elif args == 'muted':
            tab = self.sr.mutedtab
            self.OnMutedTab()
        elif args == 'gamemasters':
            tab = self.sr.gamemasterstab
            self.OnGameMastersTab()
        for each in (self.sr.generaltab,
         self.sr.allowedtab,
         self.sr.blockedtab,
         self.sr.operatorstab,
         self.sr.gamemasterstab):
            if each is not tab:
                each.state = uiconst.UI_HIDDEN
            else:
                each.state = uiconst.UI_NORMAL




    def OnGeneralTab(self):
        if not self.sr.Get('general_initialized', 0):
            channel = sm.GetService('LSC').GetChannelInfo(self.channelID)
            if channel.info.mailingList:
                return 
            uicls.Container(name='lpush', align=uiconst.TOLEFT, parent=self.sr.generaltab, width=const.defaultPadding)
            uicls.Container(name='rpush', align=uiconst.TORIGHT, parent=self.sr.generaltab, width=const.defaultPadding)
            if isinstance(self.channelID, int):
                if channel.info.displayName is not None:
                    container = uicls.Container(name='container', align=uiconst.TOTOP, parent=self.sr.generaltab, height=18, top=const.defaultPadding)
                    uicls.EveLabelSmall(text=localization.GetByLabel('UI/Chat/ChannelName'), parent=container, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
                    self.sr.channelName = uicls.SinglelineEdit(name='channelName', parent=container, setvalue=channel.info.displayName, pos=(0, 0, 150, 0), align=uiconst.TORIGHT, maxLength=50)
                container = uicls.Container(name='container', align=uiconst.TOTOP, parent=self.sr.generaltab, height=18, top=const.defaultPadding)
                uicls.EveLabelSmall(text=localization.GetByLabel('UI/Chat/Password'), parent=container, align=uiconst.TOALL, width=100, state=uiconst.UI_DISABLED)
                self.sr.password = uicls.SinglelineEdit(name='password', parent=container, setvalue=channel.info.password, pos=(0, 0, 150, 0), align=uiconst.TORIGHT, maxLength=20, passwordCharacter=u'\u2022')
                container = uicls.Container(name='container', align=uiconst.TOTOP, parent=self.sr.generaltab, height=18, top=const.defaultPadding)
                uicls.EveLabelSmall(text=localization.GetByLabel('UI/Chat/RetypePassword'), parent=container, align=uiconst.TOALL, width=100, state=uiconst.UI_DISABLED)
                self.sr.retyped = uicls.SinglelineEdit(name='retyped', parent=container, setvalue=channel.info.password, pos=(0, 0, 150, 0), align=uiconst.TORIGHT, maxLength=20, passwordCharacter=u'\u2022')
                container = uicls.Container(name='container', align=uiconst.TOTOP, parent=self.sr.generaltab, height=18, top=const.defaultPadding)
                uicls.EveLabelSmall(text=localization.GetByLabel('UI/Chat/DefaultAccess'), parent=container, align=uiconst.TOALL, width=100, state=uiconst.UI_DISABLED)
                modes = [(localization.GetByLabel('UI/Chat/Allowed'), CHTMODE_CONVERSATIONALIST), (localization.GetByLabel('UI/Chat/Moderated'), CHTMODE_LISTENER), (localization.GetByLabel('UI/Chat/Blocked'), CHTMODE_NOTSPECIFIED)]
                self.sr.combo = uicls.Combo(label='', parent=container, options=modes, name='combo', align=uiconst.TORIGHT, width=150)
                self.sr.combo.Startup(modes)
                self.sr.combo.SelectItemByValue(CHTMODE_NOTSPECIFIED)
                self.sr.combo.state = uiconst.UI_NORMAL
                self.defaultAccess = CHTMODE_NOTSPECIFIED
                for chan in channel.acl:
                    accessor = chan.accessor
                    mode = chan.mode
                    if accessor is None:
                        if mode in (CHTMODE_CONVERSATIONALIST,
                         CHTMODE_SPEAKER,
                         CHTMODE_LISTENER,
                         CHTMODE_DISALLOWED):
                            self.sr.combo.SelectItemByValue(mode)
                            self.defaultAccess = mode
                            break

                container = uicls.Container(name='container', align=uiconst.TOTOP, parent=self.sr.generaltab, height=18, top=const.defaultPadding)
                uicls.EveLabelSmall(text=localization.GetByLabel('UI/Chat/MemberList'), parent=container, align=uiconst.TOALL, width=100, state=uiconst.UI_DISABLED)
                ops = [(localization.GetByLabel('UI/Chat/DelayedMode'), 1), (localization.GetByLabel('UI/Chat/ImmediateMode', maxUsers=CHT_MAX_USERS_PER_IMMEDIATE_CHANNEL), 0)]
                self.sr.memberless = uicls.Combo(label='', parent=container, options=ops, name='memberless', align=uiconst.TORIGHT, width=150)
                self.sr.memberless.SelectItemByValue(channel.info.memberless)
            container = uicls.Container(name='container', align=uiconst.TOALL, parent=self.sr.generaltab, pos=(0,
             const.defaultPadding,
             0,
             const.defaultPadding))
            uicls.EveLabelSmall(text=localization.GetByLabel('UI/Chat/Motd'), parent=container, align=uiconst.TOALL, width=100, state=uiconst.UI_DISABLED)
            if isinstance(self.channelID, tuple) and self.channelID[0][0] == 'fleetid':
                currentMotd = sm.GetService('fleet').GetMotd()
            else:
                currentMotd = channel.info.motd
            self.sr.motd = uicls.EditPlainText(parent=container, showattributepanel=1, maxLength=4000, setvalue=currentMotd or '', padTop=20)
            self.sr.general_initialized = 1



    def GoTo(self, URL, data = None, args = {}, scrollTo = None):
        uicore.cmd.OpenBrowser(URL, data=data, args=args)



    def OnGameMastersTab(self):
        if not self.sr.Get('gm_initialized', 0):
            uicls.Container(name='lpush', align=uiconst.TOLEFT, parent=self.sr.gamemasterstab, width=const.defaultPadding)
            uicls.Container(name='rpush', align=uiconst.TORIGHT, parent=self.sr.gamemasterstab, width=const.defaultPadding)
            channel = sm.GetService('LSC').GetChannelInfo(self.channelID)
            container = uicls.Container(name='container', align=uiconst.TOTOP, parent=self.sr.gamemasterstab, height=18, top=const.defaultPadding)
            uicls.EveLabelSmall(text=localization.GetByLabel('UI/Chat/Creator'), parent=container, align=uiconst.TOALL, width=100, state=uiconst.UI_DISABLED)
            self.sr.creator = uicls.SinglelineEdit(name='creator', parent=container, setvalue=cfg.eveowners.Get(channel.info.ownerID).name, align=uiconst.TORIGHT, pos=(0, 0, 150, 0), maxLength=50)
            container = uicls.Container(name='container', align=uiconst.TOTOP, parent=self.sr.gamemasterstab, height=18, top=const.defaultPadding)
            uicls.EveLabelSmall(text=localization.GetByLabel('UI/Chat/LanguageRestriction'), parent=container, align=uiconst.TOALL, width=100, state=uiconst.UI_DISABLED)
            ops = [(localization.GetByLabel('UI/Chat/LanguageRestrictionOn'), 1), (localization.GetByLabel('UI/Chat/LanguageRestrictionOff'), 0)]
            self.sr.languageRestriction = uicls.Combo(label='', parent=container, options=ops, name='languageRestriction', align=uiconst.TORIGHT, width=150)
            self.sr.languageRestriction.SelectItemByValue(channel.info.languageRestriction)
            self.sr.gm_initialized = 1



    def OnAllowedTab(self):
        if not self.sr.Get('allowed_initialized', 0):
            self.sr.allowed_initialized = 1
            btnParent = uicls.Container(name='button', parent=self.sr.allowedtab, align=uiconst.TOTOP, height=26)
            self.sr.allow = uicls.Button(parent=btnParent, label=localization.GetByLabel('UI/Chat/AddToAllowedList'), func=self._ChannelSettingsDialog__Allow, align=uiconst.CENTER)
            self.sr.allowedlist = uicls.Scroll(parent=self.sr.allowedtab)
            self.sr.allowedlist.multiSelect = False
            channel = sm.GetService('LSC').GetChannelInfo(self.channelID)
            scrolllist = []
            accessor = []
            for each in channel.acl:
                accessor.append(each.accessor)

            cfg.eveowners.Prime(accessor)
            for chan in channel.acl:
                accessor = chan.accessor
                originalMode = chan.originalMode
                mode = chan.mode
                if (originalMode or mode) not in (CHTMODE_SPEAKER, CHTMODE_CONVERSATIONALIST):
                    continue
                if accessor is not None:
                    ownerName = cfg.eveowners.Get(accessor).name
                    if ownerName is not None:
                        ownerName = ownerName.lower()
                    scrolllist.append((ownerName, listentry.Get('ChannelACL', {'charID': accessor,
                      'RemoveACL': self._ChannelSettingsDialog__RemoveAllowed})))

            scrolllist = uiutil.SortListOfTuples(scrolllist)
            uthread.new(self.sr.allowedlist.Load, 24, scrolllist)



    def __RemoveAllowed(self, ownerIDs):
        for ownerID in ownerIDs:
            self.acls[ownerID] = CHTMODE_NOTSPECIFIED

        selected = [ each for each in self.sr.allowedlist.GetSelected() if each.info.ownerID in ownerIDs ]
        self.sr.allowedlist.RemoveEntries(selected)



    def __Allow(self, *args):
        dlg = form.PCOwnerPickerDialog.Open()
        dlg.ShowModal()
        ownerID = dlg.ownerID
        if not ownerID:
            return 
        if ownerID in self.acls:
            if self.acls[ownerID] != CHTMODE_NOTSPECIFIED:
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Chat/AccessControlAlreadyExists', name=cfg.eveowners.Get(ownerID).name)})
                return 
        else:
            channel = sm.GetService('LSC').GetChannelInfo(self.channelID)
            for chan in channel.acl:
                accessor = chan.accessor
                mode = chan.mode
                originalMode = chan.originalMode
                if accessor == ownerID:
                    if (originalMode or mode) in (CHTMODE_SPEAKER, CHTMODE_CONVERSATIONALIST):
                        return 
                    if (originalMode or mode) != CHTMODE_NOTSPECIFIED:
                        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Chat/AccessControlAlreadyExists', name=cfg.eveowners.Get(ownerID).name)})
                        return 

        idx = 0
        for each in self.sr.allowedlist.GetNodes():
            if each.charID == ownerID:
                return 
            if util.CaseFoldCompare(cfg.eveowners.Get(each.charID).name, cfg.eveowners.Get(ownerID).name) > 0:
                break
            idx += 1

        self.sr.allowedlist.AddEntries(idx, [listentry.Get('ChannelACL', {'charID': ownerID,
          'info': cfg.eveowners.Get(ownerID),
          'RemoveACL': self._ChannelSettingsDialog__RemoveAllowed})])
        if channel.channelID == channel.info.ownerID:
            self.acls[ownerID] = CHTMODE_SPEAKER
        else:
            self.acls[ownerID] = CHTMODE_CONVERSATIONALIST



    def OnBlockedTab(self):
        if not self.sr.Get('blocked_initialized', 0):
            self.sr.blocked_initialized = 1
            btnParent = uicls.Container(name='button', parent=self.sr.blockedtab, align=uiconst.TOTOP, height=26)
            self.sr.allow = uicls.Button(parent=btnParent, label=localization.GetByLabel('UI/Chat/AddToBlockedList'), func=self._ChannelSettingsDialog__Block, align=uiconst.CENTER)
            self.sr.blockedlist = uicls.Scroll(parent=self.sr.blockedtab)
            self.sr.blockedlist.multiSelect = False
            channel = sm.GetService('LSC').GetChannelInfo(self.channelID)
            scrolllist = []
            accessor = []
            for each in channel.acl:
                accessor.append(each.accessor)

            cfg.eveowners.Prime(accessor)
            for each in channel.acl:
                if each.mode != CHTMODE_DISALLOWED:
                    continue
                if each.accessor is not None:
                    ownerName = cfg.eveowners.Get(each.accessor).name
                    if ownerName is not None:
                        ownerName = ownerName.lower()
                    scrolllist.append((ownerName, listentry.Get('ChannelACL', {'charID': each.accessor,
                      'RemoveACL': self._ChannelSettingsDialog__RemoveBlocked,
                      'acl': each,
                      'GetLabel': self._ChannelSettingsDialog__GetACLLabel})))

            scrolllist = uiutil.SortListOfTuples(scrolllist)
            uthread.new(self.sr.blockedlist.Load, 24, scrolllist)



    def __RemoveBlocked(self, ownerIDs):
        for ownerID in ownerIDs:
            self.acls[ownerID] = CHTMODE_NOTSPECIFIED

        selected = [ each for each in self.sr.blockedlist.GetSelected() if each.info.ownerID in ownerIDs ]
        self.sr.blockedlist.RemoveEntries(selected)



    def __Block(self, *args):
        dlg = form.PCOwnerPickerDialog.Open()
        dlg.ShowModal()
        ownerID = dlg.ownerID
        if not ownerID:
            return 
        if ownerID in self.acls:
            if self.acls[ownerID] != CHTMODE_NOTSPECIFIED:
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Chat/AccessControlAlreadyExists', name=cfg.eveowners.Get(ownerID).name)})
                return 
        else:
            channel = sm.GetService('LSC').GetChannelInfo(self.channelID)
            for chan in channel.acl:
                accessor = chan.accessor
                originalMode = chan.originalMode
                mode = chan.mode
                if accessor == ownerID:
                    if (originalMode or mode) == CHTMODE_DISALLOWED:
                        return 
                    if (originalMode or mode) != CHTMODE_NOTSPECIFIED:
                        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Chat/AccessControlAlreadyExists', name=cfg.eveowners.Get(ownerID).name)})
                        return 

        idx = 0
        for each in self.sr.blockedlist.GetNodes():
            if each.charID == ownerID:
                return 
            if util.CaseFoldCompare(cfg.eveowners.Get(each.charID).name, cfg.eveowners.Get(ownerID).name) > 0:
                break
            idx += 1

        self.sr.blockedlist.AddEntries(idx, [listentry.Get('ChannelACL', {'charID': ownerID,
          'RemoveACL': self._ChannelSettingsDialog__RemoveBlocked})])
        self.acls[ownerID] = CHTMODE_DISALLOWED



    def OnOperatorsTab(self):
        if not self.sr.Get('operators_initialized', 0):
            self.sr.operators_initialized = 1
            btnParent = uicls.Container(name='button', parent=self.sr.operatorstab, align=uiconst.TOTOP, height=26)
            self.sr.allow = uicls.Button(parent=btnParent, label=localization.GetByLabel('UI/Chat/AddToOperatorList'), func=self._ChannelSettingsDialog__Op, align=uiconst.CENTER)
            self.sr.operatorslist = uicls.Scroll(parent=self.sr.operatorstab)
            self.sr.operatorslist.multiSelect = False
            channel = sm.GetService('LSC').GetChannelInfo(self.channelID)
            scrolllist = []
            accessors = []
            for chan in channel.acl:
                accessors.append(chan.accessor)

            cfg.eveowners.Prime(accessors)
            for chan in channel.acl:
                accessor = chan.accessor
                originalMode = chan.originalMode
                mode = chan.mode
                if (originalMode or mode) != CHTMODE_OPERATOR:
                    continue
                if accessor is not None:
                    ownerName = cfg.eveowners.Get(accessor).name
                    if ownerName is not None:
                        ownerName = ownerName.lower()
                    scrolllist.append((ownerName, listentry.Get('ChannelACL', {'charID': accessor,
                      'RemoveACL': self._ChannelSettingsDialog__RemoveOperators})))

            scrolllist = uiutil.SortListOfTuples(scrolllist)
            uthread.new(self.sr.operatorslist.Load, 24, scrolllist)



    def __RemoveOperators(self, ownerIDs):
        for ownerID in ownerIDs:
            self.acls[ownerID] = CHTMODE_NOTSPECIFIED

        selected = [ each for each in self.sr.operatorslist.GetSelected() if each.info.ownerID in ownerIDs ]
        self.sr.operatorslist.RemoveEntries(selected)



    def __Op(self, *args):
        dlg = form.PCOwnerPickerDialog.Open()
        dlg.ShowModal()
        ownerID = dlg.ownerID
        if not ownerID:
            return 
        if ownerID in self.acls:
            if self.acls[ownerID] != CHTMODE_NOTSPECIFIED:
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Chat/AccessControlAlreadyExists', name=cfg.eveowners.Get(ownerID).name)})
                return 
        else:
            channel = sm.GetService('LSC').GetChannelInfo(self.channelID)
            for chan in channel.acl:
                accessor = chan.accessor
                mode = chan.mode
                originalMode = chan.originalMode
                if accessor == ownerID:
                    if (originalMode or mode) == CHTMODE_OPERATOR:
                        return 
                    if (originalMode or mode) != CHTMODE_NOTSPECIFIED:
                        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Chat/AccessControlAlreadyExists', name=cfg.eveowners.Get(ownerID).name)})
                        return 

        idx = 0
        for each in self.sr.operatorslist.GetNodes():
            if each.charID == ownerID:
                return 
            if util.CaseFoldCompare(cfg.eveowners.Get(each.charID).name, cfg.eveowners.Get(ownerID).name) > 0:
                break
            idx += 1

        self.sr.operatorslist.AddEntries(idx, [listentry.Get('ChannelACL', {'charID': ownerID,
          'RemoveACL': self._ChannelSettingsDialog__RemoveOperators})])
        self.acls[ownerID] = CHTMODE_OPERATOR



    def OnMutedTab(self):
        if not self.sr.Get('muted_initialized', 0):
            self.sr.muted_initialized = 1
            textContainer = uicls.Container(name='scroll', parent=self.sr.mutedtab, left=const.defaultPadding, top=const.defaultPadding, align=uiconst.TOTOP, height=22, width=300)
            text = uicls.EveLabelSmall(text=localization.GetByLabel('UI/Chat/HowtoMuteHint'), parent=textContainer, align=uiconst.TOALL)
            textContainer.height = text.textheight
            self.sr.mutedlist = uicls.Scroll(parent=self.sr.mutedtab)
            channel = sm.GetService('LSC').GetChannelInfo(self.channelID)
            scrolllist = []
            for each in channel.acl:
                if each.untilWhen is not None and each.untilWhen < blue.os.GetWallclockTime() or each.mode != CHTMODE_LISTENER:
                    continue
                if each.accessor is not None:
                    ownerName = cfg.eveowners.Get(each.accessor).name
                    if ownerName is not None:
                        ownerName = ownerName.lower()
                    scrolllist.append((ownerName, listentry.Get('ChannelACL', {'charID': each.accessor,
                      'RemoveACL': self._ChannelSettingsDialog__RemoveMuted,
                      'acl': each,
                      'GetLabel': self._ChannelSettingsDialog__GetACLLabel})))

            scrolllist = uiutil.SortListOfTuples(scrolllist)
            uthread.new(self.sr.mutedlist.Load, 24, scrolllist)



    def __RemoveMuted(self, ownerIDs):
        for ownerID in ownerIDs:
            self.acls[ownerID] = (CHTMODE_NOTSPECIFIED, blue.os.GetWallclockTime() - 30 * MIN, '')

        selected = [ each for each in self.sr.mutedlist.GetSelected() if each.info.ownerID in ownerIDs ]
        self.sr.mutedlist.RemoveEntries(selected)



    def __GetACLLabel(self, data):
        ret = cfg.eveowners.Get(data.charID).name
        if data.acl:
            reason = data.acl.reason or localization.GetByLabel('UI/Generic/None')
            admin = data.acl.admin or localization.GetByLabel('UI/Generic/None')
            if data.acl.untilWhen:
                ret = localization.GetByLabel('UI/Chat/AclLabelWithDate', char=data.charID, admin=admin, reason=reason, when=data.acl.untilWhen)
            else:
                ret = localization.GetByLabel('UI/Chat/AclLabel', char=data.charID, admin=admin, reason=reason)
        return ret



    def Confirm(self):
        self.OnOK()



    def ValidateOK(self):
        if self.sr.Get('general_initialized', 0):
            if isinstance(self.channelID, int):
                if self.sr.Get('channelName') and not self.sr.channelName.GetValue().strip():
                    eve.Message('ChannelNameEmpty')
                    return False
                channel = sm.GetService('LSC').GetChannelInfo(self.channelID)
                if channel is None or not channel.info.mailingList:
                    new = self.sr.password.GetValue() or ''
                    con = self.sr.retyped.GetValue() or ''
                    if new:
                        new = new.strip()
                        if new != con:
                            eve.Message('ChtPasswordMismatch')
                            return False
                        if len(new) < 3 and len(new):
                            eve.Message('ChtNewPasswordInvalid')
                            return False
        return True



    def OnOK(self, *args):
        if not self.ValidateOK():
            return 
        channel = sm.GetService('LSC').GetChannelInfo(self.channelID)
        if channel is None:
            return 
        if self.sr.Get('general_initialized', 0):
            if not channel.info.mailingList:
                motd = self.sr.motd.GetValue(html=0).strip()
                while motd.endswith('<br>'):
                    motd = motd[:-4].strip()

                if motd != (channel.info.motd or ''):
                    self.config['motd'] = motd
            if isinstance(self.channelID, int):
                if self.sr.Get('channelName'):
                    displayName = self.sr.channelName.GetValue().strip()
                    if displayName != channel.info.displayName:
                        self.config['displayName'] = displayName
                if not channel.info.mailingList:
                    password = self.sr.password.GetValue().strip()
                    if password == '':
                        password = None
                    if password != '|||||' and password != channel.info.password:
                        self.config['oldPassword'] = channel.info.password
                        self.config['newPassword'] = password
                    if self.sr.memberless.GetValue() != channel.info.memberless:
                        self.config['memberless'] = self.sr.memberless.GetValue()
                if self.defaultAccess != self.sr.combo.GetValue():
                    self.acls[None] = self.sr.combo.GetValue()
        if self.sr.Get('gm_initialized', 0):
            if self.sr.languageRestriction.GetValue() != channel.info.languageRestriction:
                self.config['languageRestriction'] = self.sr.languageRestriction.GetValue()
            if self.sr.creator.GetValue() != cfg.eveowners.Get(channel.info.ownerID).name:
                if self.sr.creator.GetValue() in (localization.GetByLabel('UI/Chat/ChatEngine/YouAreNotAbleToSpeak'), localization.GetByLabel('UI/Chat/ChatEngine/System'), localization.GetByLabel('UI/Chat/ChatEngine/Public')):
                    ownerID = const.ownerSystem
                else:
                    result = sm.RemoteSvc('lookupSvc').LookupPCOwners(self.sr.creator.GetValue(), 1)
                    if result and len(result) == 1:
                        ownerID = result[0].ownerID
                    else:
                        ownerID = None
                if ownerID is None:
                    eve.Message('CustomInfo', {localization.GetByLabel('UI/Chat/ChatEngine/NameNotValid', creatorName=str(self.sr.creator.GetValue()))})
                    return 
                self.config['creator'] = ownerID
        self.CloseByUser()



    def OnCancel(self, *args):
        self.config = None
        self.acls = None
        self.CloseByUser()



    def OnLSC(self, channelID, estimatedMemberCount, method, who, args):
        if method == 'DestroyChannel':
            if self.channelID == channelID:
                self.CloseByUser()




class PCOwnerPickerDialog(uicls.Window):
    __guid__ = 'form.PCOwnerPickerDialog'
    default_windowID = 'PCOwnerPickerDialog'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.ownerID = None
        self.searchStr = ''
        self.SetScope('all')
        self.SetMinSize([355, 300])
        self.SetWndIcon('ui_7_64_6')
        self.SetCaption(localization.GetByLabel('UI/Chat/SelectAllianceCorpChar'))
        self.Confirm = self.ValidateOK
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.multiSelect = False
        self.sr.standardBtns = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Generic/OK'),
          self.OnOK,
          (),
          81], [localization.GetByLabel('UI/Generic/Cancel'),
          self.OnCancel,
          (),
          81]])
        self.sr.main.children.insert(0, self.sr.standardBtns)
        self.label = uicls.EveHeaderSmall(text=localization.GetByLabel('UI/Chat/TypeSearchString'), parent=self.sr.topParent, left=70, top=16, state=uiconst.UI_NORMAL)
        inpt = self.sr.inpt = uicls.SinglelineEdit(name='edit', parent=self.sr.topParent, pos=(self.label.left + self.label.width + 6,
         self.label.top - 4,
         86,
         0), align=uiconst.TOPLEFT, maxLength=37)
        btn = uicls.Button(parent=self.sr.topParent, label=localization.GetByLabel('UI/Common/Buttons/Search'), pos=(inpt.left + inpt.width + 2,
         inpt.top,
         0,
         0), func=self.Search, btn_default=1)



    def Search(self, *args):
        scrolllist = []
        results = []
        self.ShowLoad()
        try:
            hint = ''
            self.searchStr = self.GetSearchStr()
            self.SetHint()
            if len(self.searchStr) < 1:
                hint = localization.GetByLabel('UI/Common/PleaseTypeSomething')
                return 
            result = sm.RemoteSvc('lookupSvc').LookupOwners(self.searchStr, 0)
            if result is None or not len(result):
                hint = localization.GetByLabel('UI/Chat/NoAllianceCorpCharFound', searchstr=self.searchStr)
                return 
            for r in result:
                results.append(r.ownerID)

            cfg.eveowners.Prime(results)
            for r in result:
                owner = cfg.eveowners.Get(r.ownerID)
                scrolllist.append(listentry.Get('SearchEntry', {'label': r.ownerName,
                 'typeID': r.typeID,
                 'itemID': r.ownerID,
                 'confirmOnDblClick': 1,
                 'listvalue': [r.ownerName, r.ownerID]}))


        finally:
            self.sr.scroll.Load(fixedEntryHeight=18, contentList=scrolllist)
            self.SetHint(hint)
            self.HideLoad()




    def GetSearchStr(self):
        return self.sr.inpt.GetValue().strip()



    def Confirm(self):
        self.OnOK()



    def ValidateOK(self):
        if self.searchStr != self.GetSearchStr():
            self.Search()
            return False
        if self.ownerID is None:
            return False
        return True



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)



    def OnOK(self, *args):
        sel = self.sr.scroll.GetSelected()
        if sel:
            self.ownerID = sel[0].itemID
            self.CloseByUser()
        else:
            info = localization.GetByLabel('UI/Chat/MustSelectOneChoice')
            raise UserError('CustomInfo', {'info': info})



    def OnCancel(self, *args):
        self.ownerID = None
        self.CloseByUser()




class SearchEntry(listentry.Item):
    __guid__ = 'listentry.SearchEntry'

    def GetMenu(self, *args):
        scroll = self.sr.node.scroll
        scroll.DeselectAll()
        scroll.SelectNode(self.sr.node)
        return []




class ChannelACL(listentry.User):
    __guid__ = 'listentry.ChannelACL'

    def GetMenu(self, *args):
        scroll = self.sr.node.scroll
        scroll.DeselectAll()
        scroll.SelectNode(self.sr.node)
        m = [(localization.GetByLabel('UI/Chat/RemoveSelected'), self._ChannelACL__Remove), None]
        return m



    def __Remove(self, *args):
        scroll = self.sr.node.scroll
        if not scroll:
            return 
        selected = [ each.info.ownerID for each in scroll.GetSelected() ]
        if selected:
            self.sr.node.RemoveACL(selected)




class ChatInviteWnd(uicls.Window):
    __guid__ = 'form.ChatInviteWnd'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.invitorID = attributes.invitorID
        self.invitorName = attributes.invitorName
        self.result = None
        self.SetCaption(localization.GetByLabel('UI/Chat/ChatInvite'))
        self.SetMinSize([350, 200])
        self.MakeUnResizeable()
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.ConstructLayout()



    def ConstructLayout(self):
        invitorCont = uicls.Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 70), padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         0))
        invitorImgCont = uicls.Container(name='imgCont', parent=invitorCont, align=uiconst.TOLEFT, pos=(0, 0, 64, 0), padding=(0,
         0,
         const.defaultPadding,
         0))
        invitorNameCont = uicls.Container(name='topRightCont', parent=invitorCont, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(const.defaultPadding,
         0,
         0,
         0))
        label = localization.GetByLabel('UI/Chat/InvitedToConversation', inviter=self.invitorID)
        icon = uiutil.GetOwnerLogo(invitorImgCont, self.invitorID, size=64, noServerCall=True)
        uicls.EveLabelMedium(text=label, parent=invitorNameCont, left=0, top=0, align=uiconst.CENTERLEFT, width=270, state=uiconst.UI_NORMAL, idx=0)
        controlsCont = uicls.Container(name='centerCont', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 154), padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         const.defaultPadding))
        self.buttons = []
        cb1 = uicls.Checkbox(text=localization.GetByLabel('UI/Chat/AcceptInvitation'), parent=controlsCont, configName='accept', retval=0, checked=1, groupname='chatInvite', pos=(6, 0, 300, 0), align=uiconst.TOPLEFT)
        self.buttons.append(cb1)
        cb2 = uicls.Checkbox(text=localization.GetByLabel('UI/Chat/AcceptInvitationAndAddContact'), parent=controlsCont, configName='acceptadd', retval=1, checked=0, groupname='chatInvite', pos=(6, 17, 300, 0), align=uiconst.TOPLEFT)
        self.buttons.append(cb2)
        cb3 = uicls.Checkbox(text=localization.GetByLabel('UI/Chat/RejectInvitation'), parent=controlsCont, configName='reject', retval=0, checked=0, groupname='chatInvite', pos=(6,
         34,
         300,
         0), align=uiconst.TOPLEFT)
        self.buttons.append(cb3)
        cb4 = uicls.Checkbox(text=localization.GetByLabel('UI/Chat/RejectInvitationAndBlock'), parent=controlsCont, configName='block', retval=1, checked=0, groupname='chatInvite', pos=(6,
         51,
         300,
         0), align=uiconst.TOPLEFT)
        self.buttons.append(cb4)
        self.btnGroup = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Generic/OK'),
          self.Confirm,
          (),
          81,
          1,
          1,
          0]], parent=self.sr.main, idx=0)



    def Confirm(self, *args):
        for button in self.buttons:
            if button.checked:
                action = button.data['config']

        self.result = action
        self.SetModalResult(1)



exports = {'chat.GetAccessInfo': GetAccessInfo,
 'chat.CHTMODE_CREATOR': CHTMODE_CREATOR,
 'chat.CHTMODE_OPERATOR': CHTMODE_OPERATOR,
 'chat.CHTMODE_CONVERSATIONALIST': CHTMODE_CONVERSATIONALIST,
 'chat.CHTMODE_SPEAKER': CHTMODE_SPEAKER,
 'chat.CHTMODE_LISTENER': CHTMODE_LISTENER,
 'chat.CHTMODE_NOTSPECIFIED': CHTMODE_NOTSPECIFIED,
 'chat.CHTMODE_DISALLOWED': CHTMODE_DISALLOWED,
 'chat.CHTERR_NOSUCHCHANNEL': CHTERR_NOSUCHCHANNEL,
 'chat.CHTERR_ACCESSDENIED': CHTERR_ACCESSDENIED,
 'chat.CHTERR_INCORRECTPASSWORD': CHTERR_INCORRECTPASSWORD,
 'chat.CHTERR_ALREADYEXISTS': CHTERR_ALREADYEXISTS,
 'chat.CHTERR_TOOMANYCHANNELS': CHTERR_TOOMANYCHANNELS,
 'chat.GetDisplayName': GetDisplayName}

