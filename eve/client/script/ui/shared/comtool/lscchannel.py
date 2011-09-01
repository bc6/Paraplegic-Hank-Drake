import uix
import uiutil
import xtriui
import form
import uthread
import blue
import re
import util
import listentry
import chat
import sys
import types
import service
import log
import uiconst
import uicls
import base
import vivoxConstants
from itertools import izip, imap
seemsURL = re.compile('\\bwww\\.[^ \\s><]*|\\bhttps?://[^ \\s><]*')
ROLE_SLASH = service.ROLE_GML | service.ROLE_LEGIONEER
ROLE_TRANSAM = service.ROLE_TRANSLATION | service.ROLE_TRANSLATIONADMIN | service.ROLE_TRANSLATIONEDITOR
MAXMSGS = 100
CHT_MAX_INPUT = 253
CHANNELTYPEMODES = [{'no': mls.UI_SHARED_CHANNELHINT17}, {'recent': mls.UI_SHARED_CHANNELHINT18}, {'all': ''}]
CHANNELTEXTMODES = [{'no': mls.UI_GENERIC_SHOWTEXTONLY}, {'small': mls.UI_GENERIC_SHOWTEXTWITHSMALLPORTRAIT}, {'big': mls.UI_GENERIC_SHOWTEXTWITHBIGPORTRAIT}]
_tfrom = u'1370,-_*+=^~@\u263b\u3002\u03bc\u03bf\u043c\u043e\u0441'
_tto = u'leto...........momoc'
_spamTrans = dict(izip(imap(ord, _tfrom), _tto))
for ordinal in [u' ',
 u'\\',
 u'|',
 u'/',
 u'!',
 u'(',
 u')',
 u'[',
 u']',
 u'{',
 u'}',
 u'<',
 u'>',
 u'"',
 u"'",
 u'`',
 u'\xb4']:
    _spamTrans[ord(ordinal)] = None

_dotsubst = re.compile('\\.{2,}')

def NormalizeForSpam(s):
    return _dotsubst.sub('.', unicode(s).lower().translate(_spamTrans).replace('dot', '.'))



@util.Memoized
def GetTaboos():
    bannedPhrasesInChat = sm.GetService('sites').GetBannedInChatList()
    return map(NormalizeForSpam, bannedPhrasesInChat)



def IsSpam(text):
    normtext = NormalizeForSpam(text)
    for taboo in GetTaboos():
        if taboo in normtext:
            foundSpam = True
            idx = text.find(taboo)
            if idx > 0:
                foundSpam = False
                while idx > 0:
                    if text[(idx - 1)].isalnum():
                        idx = text.find(taboo, idx + 1)
                    else:
                        foundSpam = True
                        break

                return foundSpam
            return True
    else:
        return False




class LSCStack(uicls.WindowStack):
    __guid__ = 'form.LSCStack'
    default_width = 317
    default_height = 200

    def default_left(self):
        (leftpush, rightpush,) = sm.GetService('neocom').GetSideOffset()
        return leftpush



    def default_top(self):
        dh = uicore.desktop.height
        return dh - self.default_height




class Channel(uicls.Window):
    __guid__ = 'form.LSCChannel'
    __notifyevents__ = ['OnSpeakingEvent']
    default_stackID = 'LSCStack'
    default_width = 317
    default_height = 200

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        channelID = attributes.channelID
        otherID = attributes.otherID
        self.memberCount = 0
        self.channelID = None
        self.output = None
        self.userlist = None
        self.voiceOnlyMembers = []
        self.waiting = None
        self.uss_w = None
        self.uss_x = None
        self.input = None
        self.mode = None
        self.scaling = 0
        self.messages = []
        self.closing = 0
        self.inputs = ['']
        self.inputIndex = None
        self.channelInitialized = 0
        self.loadingmessages = 0
        self.changingfont = 0
        self.waitingForReturn = 0
        self.loadQueue = 0
        self.Startup(channelID, otherID)



    def Startup(self, channelID, otherID = None):
        if channelID == -1:
            return 
        self.channelID = channelID
        chatlog = '\r\n\r\n\n---------------------------------------------------------------\n\n  Channel ID:      %s\n  Channel Name:    %s\n  Listener:        %s\n  Session started: %s\n---------------------------------------------------------------\n\n' % (channelID,
         chat.GetDisplayName(channelID),
         cfg.eveowners.Get(eve.session.charid).name,
         util.FmtDate(blue.os.GetTime()))
        self.scope = 'all'
        self.windowCaption = chat.GetDisplayName(channelID).split('\\')[-1]
        try:
            self.mode = int(settings.user.ui.Get('%s_mode' % self.name, 1))
            self.usermode = int(settings.user.ui.Get('%s_usermode' % self.name, 1))
        except:
            log.LogTraceback('Settings corrupt, default mode engaged')
            self.mode = 0
            self.usermode = 1
            sys.exc_clear()
        self.logfile = None
        if settings.user.ui.Get('logchat', 1):
            try:
                filename = '%s_%s' % (chat.GetDisplayName(channelID, otherID=otherID), util.FmtDate(blue.os.GetTime()))
                filename = filename.replace('\\', '_').replace('?', '_').replace('*', '_').replace(':', '').replace('.', '').replace(' ', '_')
                filename = filename.replace('/', '_').replace('"', '_').replace('-', '_').replace('|', '_').replace('<', '_').replace('>', '_')
                filename = blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL) + '/EVE/logs/Chatlogs/%s.txt' % filename
                self.logfile = blue.os.CreateInstance('blue.ResFile')
                if not self.logfile.Open(filename, 0):
                    self.logfile.Create(filename)
                self.logfile.Write(chatlog.encode('utf-16'))
            except:
                self.logfile = None
                log.LogTraceback('Failed to instantiate log file')
                sys.exc_clear()
        self.SetWndIcon('ui_9_64_2')
        self.HideMainIcon()
        self.SetMinSize([250, 150])
        if type(channelID) != types.IntType and not eve.session.role & (service.ROLE_CHTADMINISTRATOR | service.ROLE_GMH):
            if channelID[0][0] not in ('global', 'regionid', 'constellationid'):
                self.MakeUnKillable()
                if self.sr.stack:
                    self.sr.stack.Check()
        btnparent = uicls.Container(parent=self.sr.topParent, idx=0, pos=(0, 0, 0, 16), name='btnparent', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOTOP)
        nopicture = uicls.Icon(parent=btnparent, left=38, name='nopicture', state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT)
        nopicture.icon = 'ui_38_16_158'
        nopicture.mouseoverIcon = 'ui_38_16_174'
        smallpicture = uicls.Icon(parent=btnparent, left=54, name='smallpicture', state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT)
        smallpicture.icon = 'ui_38_16_157'
        smallpicture.mouseoverIcon = 'ui_38_16_173'
        bigpicture = uicls.Icon(parent=btnparent, left=70, name='bigpicture', state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT)
        bigpicture.icon = 'ui_38_16_159'
        bigpicture.mouseoverIcon = 'ui_38_16_175'
        nouserlist = uicls.Icon(parent=btnparent, left=54, name='nouserlist', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        nouserlist.icon = 'ui_38_16_153'
        nouserlist.mouseoverIcon = 'ui_38_16_169'
        recentuserlist = uicls.Icon(parent=btnparent, left=40, name='recentuserlist', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        recentuserlist.icon = 'ui_38_16_154'
        recentuserlist.mouseoverIcon = 'ui_38_16_170'
        alluserlist = uicls.Icon(parent=btnparent, left=26, name='alluserlist', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        alluserlist.icon = 'ui_38_16_155'
        alluserlist.mouseoverIcon = 'ui_38_16_171'
        self.sr.topParent.align = uiconst.TOALL
        self.sr.topParent.padLeft = const.defaultPadding
        self.sr.topParent.padRight = const.defaultPadding
        self.sr.topParent.padTop = 0
        self.sr.topParent.padBottom = const.defaultPadding
        self.SetTopparentHeight(0)
        iconClipper = uiutil.FindChild(self, 'iconclipper')
        if iconClipper:
            iconClipper.top = -1
        self.userlist = uicls.Scroll(parent=self.sr.topParent, name='userlist', align=uiconst.TORIGHT)
        self.userlist.width = settings.user.ui.Get('%s_userlistwidth' % self.name, 128)
        div = uicls.Container(name='userlistdiv', parent=self.sr.topParent, width=const.defaultPadding, state=uiconst.UI_NORMAL, align=uiconst.TORIGHT)
        div.OnMouseDown = self.UserlistStartScale
        div.OnMouseUp = self.UserlistEndScale
        div.OnMouseMove = self.UserlistScaling
        div.cursor = 18
        self.sr.userlistdiv = div
        if not sm.GetService('LSC').IsMemberless(self.channelID) and self.usermode == 1:
            self.usermode = 2
        if type(self.channelID) != types.IntType and self.channelID[0][0] in ('global', 'regionid', 'constellationid') and self.usermode == 2:
            self.usermode = 1
        self.userlistbtns = []
        for (x, mode,) in enumerate(CHANNELTYPEMODES):
            displayMode = mode.items()[0][0]
            displayHint = mode.items()[0][1]
            btn = uiutil.GetChild(self, '%suserlist' % displayMode)
            btn.OnClick = (self.ModeChange,
             btn,
             x,
             'userlist')
            btn.OnMouseEnter = (self.ModeBtnEnter,
             btn,
             x,
             'userlist')
            btn.OnMouseExit = (self.ModeBtnLeave,
             btn,
             x,
             'userlist')
            btn.hint = displayHint
            self.userlistbtns.append(btn)

        self.InitChannelModeButtons()
        self.modebtns = []
        for (x, mode,) in enumerate(CHANNELTEXTMODES):
            displayMode = mode.items()[0][0]
            displayHint = mode.items()[0][1]
            btn = uiutil.GetChild(self, '%spicture' % displayMode)
            btn.OnClick = (self.ModeChange,
             btn,
             x,
             'mode')
            btn.OnMouseEnter = (self.ModeBtnEnter,
             btn,
             x,
             'mode')
            btn.OnMouseExit = (self.ModeBtnLeave,
             btn,
             x,
             'mode')
            btn.hint = displayHint
            self.modebtns.append(btn)

        self.output = uicls.Scroll(parent=self.sr.topParent, name='chatoutput_%s' % channelID)
        self.output.stickToBottom = 1
        self.output.OnContentResize = self.OnOutputResize
        self.input = uicls.EditPlainText(parent=self.sr.topParent, align=uiconst.TOBOTTOM, name='input%s' % self.name, height=settings.user.ui.Get('chatinputsize_%s' % self.name, 64), maxLength=CHT_MAX_INPUT, idx=0)
        self.input.ValidatePaste = self.ValidatePaste
        divider = xtriui.Divider(name='divider', align=uiconst.TOTOP, idx=1, height=const.defaultPadding, parent=self.input, state=uiconst.UI_NORMAL)
        divider.Startup(self.input, 'height', 'y', 48, 96)
        divider.OnSizeChanged = self.OnInputSizeChanged
        self.input.OnReturn = self.InputKeyUp
        self.input.CtrlUp = self.CtrlUp
        self.input.CtrlDown = self.CtrlDown
        self.input.RegisterFocus = self.RegisterFocus
        uiutil.SetOrder(divider, 0)
        btn = uicls.Icon(name='channelWndIcon', icon='ui_73_16_10', parent=self.sr.topParent, pos=(0, 0, 16, 16), align=uiconst.TOPRIGHT, hint=mls.UI_CMD_OPENCHANNELWND)
        btn.OnClick = self.OpenChannelWindow
        self.sr.smaller = uicls.Label(text='a-', parent=self.sr.topParent, left=4, fontsize=9, mousehilite=1, letterspace=1, state=uiconst.UI_NORMAL)
        self.sr.smaller.OnClick = (self.ChangeFont, -1)
        self.sr.smaller.hint = mls.UI_GENERIC_DECREASEFONTSIZE
        self.sr.smaller.top = -self.sr.smaller.textheight + 16
        self.sr.bigger = uicls.Label(text='A+', parent=self.sr.topParent, left=20, fontsize=12, mousehilite=1, letterspace=1, state=uiconst.UI_NORMAL)
        self.sr.bigger.OnClick = (self.ChangeFont, 1)
        self.sr.bigger.hint = mls.UI_GENERIC_INCREASEFONTSIZE
        self.sr.bigger.top = -self.sr.bigger.textheight + 16
        self.ChangeFont()
        self.UpdateUserIconHint()
        self.SetupUserlist(self.usermode)
        self.channelInitialized = 1
        self.UpdateCaption(1)
        self.IsBrowser = 1
        try:
            self.SpeakMOTD()
        except:
            log.LogException()
            sys.exc_clear()
        focus = uicore.registry.GetFocus()
        if not (focus and (isinstance(focus, uicls.EditCore) or isinstance(focus, uicls.SinglelineEditCore))):
            uicore.registry.SetFocus(self.input)
        else:
            uicore.registry.RegisterFocusItem(self.input)



    def default_left(self):
        (leftpush, rightpush,) = sm.GetService('neocom').GetSideOffset()
        return leftpush



    def default_top(self):
        dh = uicore.desktop.height
        return dh - self.default_height



    def OnOutputResize(self, clipperWidth, clipperHeight, *args, **kw):
        self.resizeTimer = base.AutoTimer(100, self.DelayedOutputResize, clipperWidth, clipperHeight)



    def DelayedOutputResize(self, width, height):
        self.resizeTimer = None
        uicls.Scroll.OnContentResize(self.output, width, height)



    def GetStackClass(self):
        return form.LSCStack



    def __GetMOTD(self):
        if type(self.channelID) == types.IntType:
            if sm.IsServiceRunning('LSC') and self.channelID in sm.services['LSC'].channels:
                return sm.services['LSC'].channels[self.channelID].info.motd or ''
        return ''



    def SpeakMOTD(self, whine = False):
        motd = self._Channel__GetMOTD()
        if motd or whine:
            self.Speak('%s: ' % mls.UI_SHARED_CHANNELMOTD + motd, const.ownerSystem)



    def Spam(self):
        while getattr(self, 'spam', 0) == 1:
            self._Channel__Output('a b c d f g h i j k l m n o p r s t u v x y z asd\xe6lf akjdf\xe6laksjdf \xe6lasdfkj \xe6al kfj\xe6laksfj \xe6laskdfjal\xe6sk fja\xe6lskdfj a\xe6lsdfkja \xe6ldfkja\xe6dkj\xe6alsdfk jadfkja\xe6lfk\xe6aldfkja\xe6slfkd a\xe6ldfkja\xe6ldfkja\xe6ldfkjadfl\xe6k ', eve.session.charid, 1)
            blue.pyos.synchro.Yield()




    def Restart(self, channelID):
        self.channelID = channelID
        self.windowCaption = chat.GetDisplayName(channelID).split('\\')[-1]
        self.SetupUserlist(self.usermode)
        if self.messages:
            self.messages = [ msg for msg in self.messages if msg[2] != const.ownerSystem or not msg[1].startswith(mls.UI_SHARED_CHANNELCHANGEDTO) ]
            self.LoadMessages()
        try:
            self.InitChannelModeButtons()
            if util.IsMemberlessLocal(channelID):
                self.Speak(mls.UI_SHARED_CHANNELCHANGEDTO_WORM, const.ownerSystem)
            else:
                self.Speak('%s %s' % (mls.UI_SHARED_CHANNELCHANGEDTO, chat.GetDisplayName(channelID, systemOverride=1).split('\\')[-1]), const.ownerSystem)
            self.SpeakMOTD()
        except:
            log.LogException()
            sys.exc_clear()



    def InitChannelModeButtons(self):
        for (x, mode,) in enumerate(CHANNELTYPEMODES):
            displayMode = mode.items()[0][0]
            displayHint = mode.items()[0][1]
            name = '%suserlist' % displayMode
            for btn in self.userlistbtns:
                if btn.name == name:
                    break
            else:
                continue

            btn.state = uiconst.UI_NORMAL
            btn.hint = displayHint
            if displayMode == 'all':
                if type(self.channelID) != types.IntType and self.channelID[0][0] in ('global', 'regionid', 'constellationid'):
                    btn.state = uiconst.UI_DISABLED
                elif util.IsMemberlessLocal(self.channelID):
                    btn.state = uiconst.UI_DISABLED
            elif displayMode == 'recent':
                if not sm.StartService('LSC').IsMemberless(self.channelID):
                    btn.state = uiconst.UI_DISABLED
                    btn.hint = mls.UI_SHARED_CHANNELHINT1
            if self.usermode != 0 and btn.state == uiconst.UI_DISABLED and x in (1, 2):
                idx = [1, 2][(x == 1)]
                settings.user.ui.Set('%s_usermode' % self.name, idx)
                self.SetupUserlist(idx)
            if x == 2 and btn.state != uiconst.UI_DISABLED:
                self.UpdateUserIconHint()




    def RefreshVoiceStatus(self, statusData):
        if len(statusData) == 0:
            return 
        for each in statusData:
            (charID, status, uri,) = each
            entry = self.GetUserEntry(int(charID))
            if not entry:
                continue
            entry.voiceStatus = status
            if entry.panel:
                entry.panel.SetVoiceIcon(status, charID in self.voiceOnlyMembers)




    def VoiceIconChange(self, charID, status):
        if status == vivoxConstants.NOTJOINED and charID in self.voiceOnlyMembers:
            self.voiceOnlyMembers.remove(charID)
            self.DelMember(charID)
            return 
        entry = self.GetUserEntry(int(charID))
        if not entry:
            if sm.GetService('LSC').IsMemberless(self.channelID) and status != vivoxConstants.TALKING:
                return 
            if charID == session.charid:
                if status != vivoxConstants.TALKING:
                    return 
            else:
                self.voiceOnlyMembers.append(charID)
            self.userlist.AddEntries(-1, [listentry.Get('ChatUser', {'charID': charID,
              'info': cfg.eveowners.Get(charID),
              'color': None,
              'channelID': self.channelID,
              'voiceStatus': status,
              'voiceOnly': charID != session.charid})])
            return 
        entry.voiceStatus = status
        if entry.panel:
            entry.panel.SetVoiceIcon(status, charID in self.voiceOnlyMembers)



    def OnSpeakingEvent(self, charID, channelID, isSpeaking):
        if isSpeaking and channelID == self.channelID and settings.public.audio.Get('talkMoveToTopBtn', 0):
            self.MoveToTop(charID)



    def MoveToTop(self, charid):
        entry = self.GetUserEntry(int(charid))
        if entry is not None:
            self.userlist.RemoveEntries([entry])
            self.userlist.AddEntries(0, [entry])



    def GetUserEntry(self, charID):
        for each in self.userlist.GetNodes():
            if each.charID == charID:
                return each




    def OpenChannelWindow(self, *args):
        wnd = sm.GetService('window').GetWindow('channels', 1, decoClass=form.Channels)
        if wnd:
            wnd.Maximize()



    def UpdateUserIconHint(self):
        if type(self.channelID) != types.IntType and self.channelID[0][0] in ('global', 'regionid', 'constellationid'):
            self.userlistbtns[2].hint = mls.UI_SHARED_CHANNELHINT2
        elif sm.GetService('LSC').IsMemberless(self.channelID):
            self.userlistbtns[2].hint = mls.UI_SHARED_CHANNELHINT3
        else:
            self.userlistbtns[2].hint = mls.UI_SHARED_CHANNELHINT4



    def ChangeFont(self, add = 0, *args):
        if self.changingfont:
            return 
        fontsize = settings.user.ui.Get('chatfontsize_%s' % self.name, 12)
        if add <= -1 and min(fontsize + add, fontsize - add) < 9 or add >= 1 and max(fontsize + add, fontsize - add) > 28:
            return 
        newsize = fontsize + add
        self.changingfont = 1
        self.fontsize = newsize
        self.letterSpace = 0
        if self.fontsize <= 10:
            self.letterSpace = 1
        self.LoadMessages()
        self.input.SetDefaultFontSize(newsize)
        settings.user.ui.Set('chatfontsize_%s' % self.name, newsize)
        self.changingfont = 0



    def OnEndMinimize_(self, *args):
        self.OnTabDeselect()



    def OnEndMaximize_(self, *args):
        self.OnTabSelect()



    def OnInputSizeChanged(self):
        settings.user.ui.Set('chatinputsize_%s' % self.name, self.input.height)



    def __Settings(self, *args):
        sm.GetService('LSC').Settings(self.channelID)



    def GetMenu(self, *args):
        m = uicls.Window.GetMenu(self)
        m += [None]
        if type(self.channelID) == types.IntType and sm.GetService('LSC').IsOperator(self.channelID):
            m.append((mls.UI_CMD_SETTINGS, self._Channel__Settings))
        prefsName = 'chatWindowBlink_%s' % self.name
        if settings.user.ui.Get(prefsName, 1):
            m.append((mls.UI_CMD_BLINKOFF, settings.user.ui.Set, (prefsName, 0)))
        else:
            m.append((mls.UI_CMD_BLINKON, settings.user.ui.Set, (prefsName, 1)))
        if sm.GetService('vivox').Enabled() and sm.GetService('vivox').LoggedIn():
            m += [None]
            fleetChannels = ['fleet', 'wing', 'squad']
            excludedFromVoiceChannels = ['regionid',
             'solarsystemid',
             'constellationid',
             'allianceid',
             'warfactionid',
             'incursion']
            excludedFromVoice = False
            isFleetChannel = False
            if type(self.channelID) == types.TupleType:
                if util.IsNPC(self.channelID[0][1]):
                    excludedFromVoice = True
                for excludedChannelName in excludedFromVoiceChannels:
                    if self.channelID[0][0].startswith(excludedChannelName):
                        excludedFromVoice = True
                        break

                for fleetChannelName in fleetChannels:
                    if self.channelID[0][0].startswith(fleetChannelName):
                        isFleetChannel = True
                        break

            elif type(self.channelID) == types.IntType:
                excludedFromVoice = self.channelID >= 0 and self.channelID <= 1000
            else:
                raise RuntimeError('LSC only supports channel IDs of tuple or int type.')
            if not excludedFromVoice:
                if sm.GetService('vivox').IsVoiceChannel(self.channelID):
                    m.append((mls.UI_CMD_LEAVEAUDIO, self.VivoxLeaveAudio))
                    currentSpeakingChannel = sm.GetService('vivox').GetSpeakingChannel()
                    if type(currentSpeakingChannel) is types.TupleType:
                        currentSpeakingChannel = (currentSpeakingChannel,)
                    if currentSpeakingChannel != self.channelID:
                        m.append((mls.UI_CMD_MAKESPEAKINGCHANNEL, self.VivoxSetAsSpeakingChannel))
                elif isFleetChannel:
                    if sm.GetService('fleet').GetOptions().isVoiceEnabled:
                        m.append((mls.UI_CMD_JOINAUDIO, self.VivoxJoinAudio))
                else:
                    m.append((mls.UI_CMD_JOINAUDIO, self.VivoxJoinAudio))
        return m



    def VivoxJoinAudio(self, *args):
        sm.GetService('vivox').JoinChannel(self.channelID)
        sm.GetService('vivox').SetSpeakingChannel(self.channelID)



    def VivoxLeaveAudio(self, *args):
        sm.GetService('vivox').LeaveChannel(self.channelID)
        self.DelVoiceUsers(self.voiceOnlyMembers)



    def VivoxSetAsSpeakingChannel(self, *args):
        sm.GetService('vivox').SetSpeakingChannel(self.channelID)



    def VivoxMuteMe(self, *args):
        sm.GetService('vivox').Mute(1)



    def VivoxLeaderGag(self, *args):
        sm.GetService('fleet').SetVoiceMuteStatus(1, self.channelID)



    def VivoxLeaderUngag(self, *args):
        sm.GetService('fleet').SetVoiceMuteStatus(0, self.channelID)



    def OnDropData(self, dragObj, *args):
        pass



    def OnClose_(self, *args):
        if getattr(self, 'closing', 0):
            return 
        self.closing = 1
        self.output = None
        self.input = None
        self.userlist = None
        self.messages = []
        if self.logfile is not None:
            self.logfile.Close()
            self.logfile = None
        if sm.IsServiceRunning('LSC'):
            sm.GetService('LSC').LeaveChannel(self.channelID, destruct=0)
            sm.GetService('vivox').LeaveChannel(self.channelID)



    def RenameChannel(self, newName):
        self.windowCaption = newName.split('\\')[-1]
        self.UpdateCaption()



    def UpdateCaption(self, startingup = 0, localEcho = 0):
        if self.channelInitialized:
            label = chat.GetDisplayName(self.channelID).split('\\')[-1]
            label.replace('conversation', 'conv.')
            label.replace('channel', 'ch.')
            memberCount = sm.GetService('LSC').GetMemberCount(self.channelID)
            if memberCount != self.memberCount:
                self.memberCount = memberCount
            if type(self.channelID) == types.IntType or self.channelID[0] not in ('global', 'regionid', 'constellationid'):
                if self.memberCount > 2:
                    label += ' [%d]' % self.memberCount
            self.SetCaption(label)



    def ModeBtnEnter(self, sender, idx, set, *args):
        btns = getattr(self, set + 'btns', None)
        mode = [self.usermode, self.mode][(set == 'mode')]
        i = 0
        for each in btns:
            if i != mode:
                each.LoadIcon(each.icon)
            i = i + 1

        if idx != mode:
            sender.LoadIcon(sender.mouseoverIcon)



    def ModeBtnLeave(self, sender, idx, set, *args):
        mode = [self.usermode, self.mode][(set == 'mode')]
        if idx != mode:
            sender.LoadIcon(sender.icon)



    def ModeChange(self, sender, idx, set, *args):
        if self.destroyed:
            return 
        if set == 'mode':
            if self.mode == idx:
                return 
            self.mode = idx
            self.LoadMessages()
            settings.user.ui.Set('%s_mode' % self.name, idx)
            uicore.registry.SetFocus(self)
        else:
            settings.user.ui.Set('%s_usermode' % self.name, idx)
            self.SetupUserlist(idx)



    def SetupUserlist(self, mode):
        if self.destroyed:
            return 
        if mode == 0:
            self.userlist.Load(contentList=[])
            self.userlist.state = self.sr.userlistdiv.state = uiconst.UI_HIDDEN
        else:
            minW = 50
            maxW = 200
            self.userlist.width = min(maxW, max(minW, self.userlist.width))
            self.userlist.state = uiconst.UI_PICKCHILDREN
            self.sr.userlistdiv.state = uiconst.UI_NORMAL
            self.InitUsers(mode == 1)
        if self.channelInitialized and not self.destroyed:
            self.LoadMessages()
        self.usermode = mode
        for each in self.userlistbtns:
            each.LoadIcon(each.icon)

        active = self.userlistbtns[mode]
        active.LoadIcon(active.mouseoverIcon)



    def RegisterFocus(self, edit, *args):
        sm.GetService('focus').SetFocusChannel(self)



    def SetCharFocus(self, char):
        uicore.registry.SetFocus(self.input)
        uix.Flush(uicore.layer.menu)
        if char is not None:
            self.input.OnChar(char, 0)



    def OnTabDeselect(self):
        if self.channelInitialized and not self.destroyed:
            self.UnloadMessages()
            if getattr(self, 'unloadUserlistScrollProportion', None) is None:
                self.unloadUserlistScrollProportion = self.userlist.GetScrollProportion()
            self.userlist.Load(contentList=[])



    def OnTabSelect(self):
        if getattr(self, 'channelInitialized', False) and not self.destroyed:
            uicore.registry.SetFocus(self.input)
            if self.input is not None:
                self.input.DoSizeUpdate()
            self.LoadMessages()
            if self.usermode != 0:
                self.InitUsers(self.usermode == 1)



    def LoadMessages(self):
        if not self.output or self.state == uiconst.UI_HIDDEN:
            return 
        self.loadQueue = 1
        if self.loadingmessages:
            return 
        self.loadingmessages = 1
        uthread.new(self._LoadMessages)
        self.loadingmessages = 0



    def _LoadMessages(self):
        if self.destroyed:
            return 
        try:
            spammers = getattr(sm.GetService('LSC'), 'spammerList', set())
            while not self.destroyed and self.loadQueue and self.state != uiconst.UI_HIDDEN:
                self.loadQueue = 0
                if self.destroyed:
                    break
                portion = self.output.GetScrollProportion() or getattr(self, 'unloadScrollProportion', 0.0)
                self.unloadScrollProportion = None
                scrollList = []
                for each in self.messages:
                    if each[2] not in spammers:
                        scrollList.append(self.GetChatEntry(each, each[2] == eve.session.charid))

                log.LogInfo('About to load', len(scrollList), 'entries to chat output of channel', self.channelID)
                self.output.Load(contentList=scrollList, scrollTo=portion)
                for each in self.modebtns:
                    each.LoadIcon(each.icon)

                active = self.modebtns[self.mode]
                active.LoadIcon(active.mouseoverIcon)


        finally:
            if not self.destroyed:
                self.loadingmessages = 0




    def UnloadMessages(self):
        if self.loadingmessages or not self.output:
            return 
        if getattr(self, 'unloadScrollProportion', None) is None:
            self.unloadScrollProportion = self.output.GetScrollProportion()
        self.output.Load(contentList=[])



    def GetChatEntry(self, msg, localEcho = False):
        (who, txt, charid, time, colorkey,) = msg
        return listentry.Get('ChatEntry', {'text': FormatTxt(msg, self.mode, self.fontsize, self.letterSpace, localEcho),
         'mode': self.mode,
         'fontsize': self.fontsize,
         'letterspace': self.letterSpace,
         'charid': charid,
         'channelid': self.channelID,
         'msg': msg,
         'textbuff': None})



    def __LocalEcho(self, txt):
        self._Channel__Output(txt, eve.session.charid, 1)



    def Speak(self, txt, charid, localEcho = 0):
        self._Channel__Output(txt, charid, localEcho)



    def __Output(self, txt, charid, localEcho):
        blink = charid not in (eve.session.charid, const.ownerSystem)
        colorkey = 0
        if charid == eve.session.charid:
            if not localEcho:
                self.waitingForReturn = 0
                return 
            if len(txt) > 253:
                txt = txt[:253] + '...'
            colorkey = eve.session.role
        elif charid == const.ownerSystem:
            colorkey = service.ROLE_ADMIN
        elif type(charid) not in types.StringTypes:
            mi = sm.GetService('LSC').GetMemberInfo(self.channelID, charid)
            if mi:
                colorkey = mi.role
        if not localEcho and IsSpam(txt):
            return 
        self.UpdateCaption(localEcho=localEcho)
        if type(charid) in types.StringTypes:
            who = charid
        else:
            who = cfg.eveowners.Get(charid).name
        time = blue.os.GetTime()
        if self.destroyed:
            return 
        if self.logfile is not None and self.logfile.size > 0:
            line = '[%20s ] %s > %s\r\n' % (util.FmtDate(time), who, uiutil.StripTags(txt).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&'))
            try:
                self.logfile.Write(line.encode('utf-16'))
            except IOError:
                log.LogException(toAlertSvc=0)
                sys.exc_clear()
        msg = [who,
         txt,
         charid,
         time,
         colorkey]
        updateOutput = bool(self.state != uiconst.UI_HIDDEN)
        self.messages.append(msg)
        if len(self.messages) >= MAXMSGS:
            self.messages.pop(0)
            if self.output.GetNodes():
                self.output.RemoveEntries([self.output.GetNodes()[0]])
        if updateOutput:
            self.output.AddEntries(-1, [self.GetChatEntry(msg, localEcho)])
        if settings.user.ui.Get('chatWindowBlink_%s' % self.name, 1) and blink:
            stack = self.sr.Get('stack', None)
            if self.state == uiconst.UI_HIDDEN and self.sr.tab and hasattr(self.sr.tab, 'Blink'):
                self.sr.tab.Blink(1)
            stack = self.sr.Get('stack', None)
            if self.state == uiconst.UI_HIDDEN and self.sr.btn and hasattr(self.sr.btn, 'SetBlink'):
                self.sr.btn.SetBlink(1)
            elif self.sr.stack is not None and (self.sr.stack.state != uiconst.UI_NORMAL or self.state != uiconst.UI_NORMAL):
                if self.sr.stack.sr.btn and hasattr(self.sr.stack.sr.btn, 'SetBlink'):
                    stack.sr.btn.SetBlink(1)
            if self.state == uiconst.UI_HIDDEN:
                self.SetBlinking()



    def ValidatePaste(self, text):
        text = text.replace('<t>', '  ')
        text = uiutil.StripTags(text, ignoredTags=['b', 'i', 'u'])
        return text



    def InputKeyUp(self, *args):
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if shift:
            return 
        if self.waitingForReturn and blue.os.GetTime() - self.waitingForReturn < MIN:
            txt = self.input.GetValue(html=0)
            txt = txt.rstrip()
            cursorPos = -1
            self.input.SetValue(txt, cursorPos=cursorPos)
            eve.Message('uiwarning03')
            return 
        NUM_SECONDS = 4
        if session.userType == 23 and (type(self.channelID) != types.IntType or self.channelID < 2100000000 and self.channelID > 0):
            lastMessageTime = long(getattr(self, 'lastMessageTime', blue.os.GetTime() - 1 * MIN))
            if blue.os.GetTime() - lastMessageTime < NUM_SECONDS * SEC:
                eve.Message('LSCTrialRestriction_SendMessage', {'sec': (NUM_SECONDS * SEC - (blue.os.GetTime() - lastMessageTime)) / SEC})
                return 
            setattr(self, 'lastMessageTime', blue.os.GetTime())
        txt = self.input.GetValue(html=0)
        self.input.SetValue('')
        txt = txt.strip()
        while txt.endswith('<br>'):
            txt = txt[:-4]

        txt = txt.strip()
        while txt.startswith('<br>'):
            txt = txt[4:]

        txt = txt.strip()
        if not txt or len(txt) <= 0:
            return 
        if sm.GetService('LSC').IsLanguageRestricted(self.channelID):
            try:
                if unicode(txt) != unicode(txt).encode('ascii', 'replace'):
                    uicore.registry.BlockConfirm()
                    eve.Message('LscLanguageRestrictionViolation')
                    return 
            except:
                log.LogTraceback('Gurgle?')
                sys.exc_clear()
                eve.Message('uiwarning03')
                return 
        if boot.region == 'optic':
            try:
                bw = str(mls.textLabels['UI_SHARED_OPTICBANWORDS'][1]).decode('utf-7')
                banned = [ word for word in bw.split() if word ]
                for bword in banned:
                    if txt.startswith('/') and not (txt.startswith('/emote') or txt.startswith('/me')):
                        txt = txt
                    else:
                        txt = txt.replace(bword, '*')

            except Exception:
                log.LogTraceback('Borgle?')
                sys.exc_clear()
        if not sm.GetService('LSC').IsSpeaker(self.channelID):
            borki = '%s<br>' % mls.UI_SHARED_CHANNELHINT5
            access = sm.GetService('LSC').GetMyAccessInfo(self.channelID)
            hasAccessInfo = True
            if access[1] is None:
                hasAccessInfo = False
            borki += '%s: ' % mls.UI_GENERIC_REASON + (hasAccessInfo and access[1].reason or 'Not Specified') + '<br>'
            if hasAccessInfo and access[1].untilWhen:
                borki += '%s: ' % mls.UI_SHARED_UNTIL + util.FmtDate(access[1].untilWhen) + '<br>'
            else:
                borki += '%s<br>' % mls.UI_SHARED_UNTILNOTSPECIFIED
            borki += '%s: ' % mls.UI_GENERIC_ADMIN + (hasAccessInfo and access[1].admin or mls.UI_SHARED_NOTSPECIFIED) + '<br>'
            self._Channel__LocalEcho(borki)
        if txt != '' and txt.replace('\r', '').replace('\n', '').replace('<br>', '').replace(' ', '').replace('/emote', '').replace('/me', '') != '':
            if txt.startswith('/me'):
                txt = '/emote' + txt[3:]
            spoke = 0
            if self.inputs[-1] != txt:
                self.inputs.append(txt)
                self.inputIndex = None
            nobreak = uiutil.StripTags(txt.replace('<br>', ''))
            if nobreak.startswith('/') and not (nobreak.startswith('/emote') or nobreak == '/'):
                for commandLine in uiutil.StripTags(txt.replace('<br>', '\n')).split('\n'):
                    try:
                        slashRes = uicore.cmd.Execute(commandLine)
                        if slashRes is not None:
                            sm.GetService('logger').AddText('slash result: %s' % slashRes, 'slash')
                        elif nobreak.startswith('/tutorial') and eve.session and eve.session.role & service.ROLE_GML:
                            sm.GetService('tutorial').SlashCmd(commandLine)
                        elif eve.session and eve.session.role & ROLE_SLASH:
                            if commandLine.lower().startswith('/mark'):
                                sm.StartService('logger').LogError('SLASHMARKER: ', (eve.session.userid, eve.session.charid), ': ', commandLine)
                            slashRes = sm.GetService('slash').SlashCmd(commandLine)
                            if slashRes is not None:
                                sm.GetService('logger').AddText('slash result: %s' % slashRes, 'slash')
                        self._Channel__LocalEcho('/slash: ' + commandLine)
                    except:
                        self._Channel__LocalEcho('/slash failed: ' + commandLine)
                        raise 

            else:
                stext = uiutil.StripTags(txt, ignoredTags=['b',
                 'i',
                 'u',
                 'url',
                 'br'])
                try:
                    if type(self.channelID) != types.IntType and self.channelID[0][0] in ('constellationid', 'regionid') and util.IsWormholeSystem(eve.session.solarsystemid2):
                        self._Channel__Output(mls.UI_GENERIC_NOCHANNELACCESS_WORMHOLE, 1, 1)
                        return 
                    self.waitingForReturn = blue.os.GetTime()
                    self._Channel__LocalEcho(stext)
                    if not IsSpam(stext):
                        sm.GetService('LSC').SendMessage(self.channelID, stext)
                    else:
                        self.waitingForReturn = 0
                except:
                    self.waitingForReturn = 0
                    raise 



    def CtrlDown(self, editctrl, *args):
        self.BrowseInputs(1)



    def CtrlUp(self, editctrl, *args):
        self.BrowseInputs(-1)



    def BrowseInputs(self, updown):
        if self.inputIndex is None:
            self.inputIndex = len(self.inputs) - 1
        else:
            self.inputIndex += updown
        if self.inputIndex < 0:
            self.inputIndex = len(self.inputs) - 1
        elif self.inputIndex >= len(self.inputs):
            self.inputIndex = 0
        self.input.SetValue(self.inputs[self.inputIndex], cursorPos=-1)



    def InitUsers(self, recent):
        members = sm.GetService('LSC').GetMembers(self.channelID, recent)
        if members is None:
            self.userlist.ShowHint('List not available')
        else:
            idsToPrime = set()
            for charID in members:
                if charID not in cfg.eveowners:
                    idsToPrime.add(charID)

            if idsToPrime:
                cfg.eveowners.Prime(idsToPrime)
            scrollProportion = self.userlist.GetScrollProportion() or getattr(self, 'unloadUserlistScrollProportion', 0.0)
            self.unloadUserlistScrollProportion = None
            audioStatus = dict(sm.GetService('vivox').GetMemberVoiceStatus(self.channelID) or [])
            try:
                self.userlist.ShowHint()
                scrolllist = []
                for charID in members:
                    member = members[charID]
                    charinfo = cfg.eveowners.Get(member.charID)
                    if member.charID in audioStatus:
                        voiceStatus = audioStatus.pop(member.charID)
                    else:
                        voiceStatus = None
                    scrolllist.append((charinfo.name.lower(), listentry.Get('ChatUser', {'charID': member.charID,
                      'corpID': member.corpID,
                      'allianceID': member.allianceID,
                      'warFactionID': member.warFactionID,
                      'info': charinfo,
                      'color': GetColor(member.role),
                      'channelID': self.channelID,
                      'voiceStatus': voiceStatus})))

                if sm.GetService('LSC').IsMemberless(self.channelID):
                    for charID in audioStatus.keys():
                        if charID not in self.voiceOnlyMembers:
                            audioStatus.pop(charID)

                if len(audioStatus) > 0:
                    cfg.eveowners.Prime(audioStatus.keys())
                    for (charID, voiceStatus,) in audioStatus.iteritems():
                        if charID == session.charid:
                            continue
                        charinfo = cfg.eveowners.Get(charID)
                        scrolllist.append((charinfo.name.lower(), listentry.Get('ChatUser', {'charID': charID,
                          'info': cfg.eveowners.Get(charID),
                          'color': None,
                          'channelID': self.channelID,
                          'voiceStatus': voiceStatus,
                          'voiceOnly': True})))

                scrolllist = uiutil.SortListOfTuples(scrolllist)
                self.userlist.Load(contentList=scrolllist, scrollTo=scrollProportion)
            except RuntimeError as e:
                if e.args[0] == 'dictionary changed size during iteration':
                    sys.exc_clear()
                    self.InitUsers(recent)
                    return 
                raise e



    def AddMember(self, *args, **keywords):
        if not sm.GetService('LSC').IsMemberless(self.channelID):
            self._Channel__AddUser(*args, **keywords)



    def AddRecentSpeaker(self, *args, **keywords):
        if sm.GetService('LSC').IsMemberless(self.channelID):
            self._Channel__AddUser(*args, **keywords)



    def __AddUser(self, charid, corpid, allianceid, warfactionid, refresh = 1, sort = 1, load = 1, color = None):
        if self.destroyed or not self.channelInitialized or not self.userlist:
            return 
        self.userlist.ShowHint()
        newcharinfo = cfg.eveowners.Get(charid)
        idx = 0
        for each in self.userlist.GetNodes():
            if each.charID == charid:
                if hasattr(each, 'voiceOnly'):
                    try:
                        self.DelVoiceUsers([charid])
                    except ValueError:
                        pass
                    break
                return 
            if util.CaseFoldCompare(each.info.name, newcharinfo.name) > 0:
                break
            idx += 1

        audioStatus = dict(sm.GetService('vivox').GetMemberVoiceStatus(self.channelID) or [])
        if charid in audioStatus:
            voiceStatus = audioStatus[charid]
        else:
            voiceStatus = None
        self.userlist.AddEntries(idx, [listentry.Get('ChatUser', {'charID': charid,
          'corpID': corpid,
          'allianceID': allianceid,
          'warFactionID': warfactionid,
          'info': cfg.eveowners.Get(charid),
          'color': color,
          'channelID': self.channelID,
          'voiceStatus': voiceStatus})])
        if self.sr.stack is not None and self.sr.stack.sr.btn:
            self.sr.stack.sr.btn.SetLabel(self.sr.stack.GetCaption())
        else:
            self.UpdateCaption()



    def DelMember(self, *args, **keywords):
        if not sm.GetService('LSC').IsMemberless(self.channelID):
            self._Channel__DelUser(*args, **keywords)



    def DelRecentSpeaker(self, *args, **keywords):
        self._Channel__DelUser(*args, **keywords)



    def __DelUser(self, charid):
        for each in self.userlist.GetNodes():
            if each.charID == charid:
                self.userlist.RemoveEntries([each])
                break
        else:
            return 

        self._Channel__UpdateAfterDeletion()



    def DelVoiceUsers(self, charids):
        for charID in charids:
            if charID in self.voiceOnlyMembers:
                self.voiceOnlyMembers.remove(charID)

        entries = []
        for each in self.userlist.GetNodes():
            if each.charID in charids:
                entries.append(each)

        if len(entries) < 1:
            return 
        self.userlist.RemoveEntries(entries)
        self._Channel__UpdateAfterDeletion()



    def __UpdateAfterDeletion(self):
        if self.sr.stack is not None and self.sr.stack.sr.btn:
            self.sr.stack.sr.btn.SetLabel(self.sr.stack.GetCaption())
        else:
            self.UpdateCaption()



    def UserlistStartScale(self, *args):
        self.uss_w = self.userlist.width
        self.uss_x = uicore.uilib.x
        self.scaling = 1



    def UserlistScaling(self, *args):
        if self.scaling:
            minW = 50
            maxW = 200
            diffx = uicore.uilib.x - self.uss_x
            self.userlist.width = min(maxW, max(minW, self.uss_w - diffx))



    def UserlistEndScale(self, *args):
        self.scaling = 0
        settings.user.ui.Set('%s_userlistwidth' % self.name, self.userlist.width)
        self.LoadMessages()



    def GoTo(self, URL, data = None, args = {}, scrollTo = None):
        uicore.cmd.OpenBrowser(URL, data=data, args=args)




class ChannelMenu(list):

    def __init__(self, channelID, charID):
        self.channelID = channelID
        self.charID = charID
        commands = []
        if charID != const.ownerSystem and sm.GetService('LSC').IsOperator(channelID):
            if not sm.GetService('LSC').IsOperator(channelID, charID):
                if sm.GetService('LSC').IsGagged(channelID, charID):
                    commands.append((mls.UI_CMD_ALLOWSPEAKING, self._ChannelMenu__UnGag))
                else:
                    commands.append((mls.UI_CMD_MUTE, self._ChannelMenu__Gag))
                commands.append((mls.UI_CMD_KICK, self._ChannelMenu__Kick))
        self.append((mls.UI_CMD_REPORTISKSPAMMER, self.ReportISKSpammer))
        if commands:
            self.append((mls.UI_CMD_CHANNEL, commands))



    def ExcludeFromVoiceMute(self, *args):
        sm.GetService('fleet').ExcludeFromVoiceMute(self.charID, self.channelID)



    def AddToVoiceMute(self, *args):
        sm.GetService('fleet').AddToVoiceMute(self.charID, self.channelID)



    def ReportISKSpammer(self, *args):
        sm.GetService('menu').ReportISKSpammer(self.charID, self.channelID)



    def __Gag(self, *args):
        import chat
        format = []
        format.append({'type': 'bbline'})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'edit',
         'key': 'minutes',
         'setvalue': 30,
         'label': mls.UI_SHARED_MINTOINF,
         'frame': 1,
         'maxLength': 5,
         'intonly': [0, 43200]})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'textedit',
         'key': 'reason',
         'label': mls.UI_GENERIC_REASON,
         'frame': 1,
         'maxLength': 255})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'btline'})
        retval = uix.HybridWnd(format, mls.UI_GENERIC_GAG + ' ' + cfg.eveowners.Get(self.charID).name, 1, None, uiconst.OKCANCEL, minW=300, minH=160)
        if retval is not None:
            if retval['minutes']:
                untilWhen = blue.os.GetTime() + retval['minutes'] * MIN
            else:
                untilWhen = None
            sm.GetService('LSC').AccessControl(self.channelID, self.charID, chat.CHTMODE_LISTENER, untilWhen, retval['reason'])



    def __UnGag(self, *args):
        import chat
        mode = sm.GetService('LSC').GetChannelInfo(self.channelID).acl[0].mode
        if mode == 1:
            sm.RemoteSvc('LSC').AccessControl(self.channelID, self.charID, chat.CHTMODE_CONVERSATIONALIST)
        else:
            sm.GetService('LSC').AccessControl(self.channelID, self.charID, chat.CHTMODE_NOTSPECIFIED, blue.os.GetTime() - 30 * MIN, '')



    def __Kick(self, *args):
        import chat
        format = []
        format.append({'type': 'bbline'})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'edit',
         'key': 'minutes',
         'setvalue': 30,
         'label': mls.UI_GENERIC_MINUTES,
         'frame': 1,
         'maxLength': 5,
         'intonly': [0, 43200]})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'textedit',
         'key': 'reason',
         'label': mls.UI_GENERIC_REASON,
         'frame': 1,
         'maxLength': 255})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'btline'})
        retval = uix.HybridWnd(format, 'Kick %s' % cfg.eveowners.Get(self.charID).name, 1, None, uiconst.OKCANCEL, minW=300, minH=160)
        if retval is not None:
            if retval['minutes']:
                untilWhen = blue.os.GetTime() + retval['minutes'] * MIN
            else:
                untilWhen = None
            sm.GetService('LSC').AccessControl(self.channelID, self.charID, chat.CHTMODE_DISALLOWED, untilWhen, retval['reason'])




class ChatUser(listentry.User):
    __guid__ = 'listentry.ChatUser'

    def Load(self, node, *args):
        node.GetMenu = self.GetNodeMenu
        listentry.User.Load(self, node, *args)
        self.SetVoiceIcon(node.voiceStatus, hasattr(node, 'voiceOnly') and node.voiceOnly)



    def GetNodeMenu(self, *args):
        return [None] + ChannelMenu(self.sr.node.channelID, self.sr.node.charID)



    def SetVoiceIcon(self, state, voiceOnly = False):
        if self.sr.voiceIcon is None:
            self.sr.voiceIcon = uicls.Icon(icon='ui_38_16_106', parent=self, pos=(16, 3, 0, 0), align=uiconst.TOPRIGHT, idx=0, state=uiconst.UI_DISABLED, hint='')
        if state is None:
            self.sr.voiceIcon.state = uiconst.UI_HIDDEN
        elif voiceOnly:
            icon = {0: 'ui_73_16_42',
             1: 'ui_73_16_44',
             2: 'ui_73_16_43'}.get(state, None)
        else:
            icon = {0: 'ui_38_16_106',
             1: 'ui_38_16_108',
             2: 'ui_38_16_107'}.get(state, None)
        if icon is None:
            self.sr.voiceIcon.state = uiconst.UI_HIDDEN
            log.LogWarn('Unsupported voice state flag', state)
            return 
        iconpath = icon
        uiutil.MapIcon(self.sr.voiceIcon, iconpath)
        self.sr.voiceIcon.state = uiconst.UI_NORMAL
        return self.sr.voiceIcon




class ChatEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.ChatEntry'
    __notifyevents__ = ['OnPortraitCreated']
    allowDynamicResize = True

    def Startup(self, *args):
        self.sr.text = uicls.Label(text='', parent=self, align=uiconst.TOTOP, padRight=5, state=uiconst.UI_NORMAL, color=None)
        self.sr.text.GetMenu = self.GetMenu
        self.sr.picParent = uicls.Container(name='picpar', parent=self, align=uiconst.TOPLEFT, width=34, height=34, left=2, top=2)
        self.sr.pic = uicls.Icon(parent=self.sr.picParent, align=uiconst.TOALL, padLeft=1, padTop=1, padRight=1, padBottom=1)
        uicls.Frame(parent=self.sr.picParent, color=(1.0, 1.0, 1.0, 0.125))
        sm.RegisterNotify(self)



    def Load(self, node):
        data = node
        self.sr.picParent.width = self.sr.picParent.height = [34, 34, 66][node.mode]
        self.picloaded = 0
        self.sr.text.busy = 1
        if node.mode and type(self.sr.node.charid) not in types.StringTypes:
            self.sr.text.padLeft = [5, 43, 75][node.mode]
            self.sr.picParent.state = uiconst.UI_NORMAL
            self.LoadPortrait()
        else:
            self.sr.text.padLeft = 5
            self.sr.picParent.state = uiconst.UI_HIDDEN
        self.sr.text.padTop = [2, 0][(node.mode == 0)]
        self.sr.text.specialIndent = [0, 10][(node.mode == 0)]
        self.sr.text.fontsize = node.fontsize
        self.sr.text.letterspace = node.letterspace
        self.sr.text.busy = 0
        self.sr.text.text = data.text



    def LoadPortrait(self, orderIfMissing = True):
        if self is None or self.destroyed:
            return 
        if self.sr.node.charid == const.ownerSystem:
            self.sr.pic.LoadIcon('ui_6_64_7')
            return 
        size = [32, 64][(self.sr.node.mode - 1)]
        if sm.GetService('photo').GetPortrait(self.sr.node.charid, size, self.sr.pic, orderIfMissing, callback=True):
            self.picloaded = 1



    def OnPortraitCreated(self, charID):
        if self is None or self.destroyed:
            return 
        if self.sr.node and charID == self.sr.node.charid and not self.picloaded:
            self.LoadPortrait(False)



    def GetDynamicHeight(node, width):
        if node.mode and type(node.charid) not in types.StringTypes:
            padLeft = [5, 43, 75][node.mode]
        else:
            padLeft = 5
        height = uicore.font.GetTextHeight(node.text, width=width - 5 - padLeft, fontsize=node.fontsize, letterspace=node.letterspace, specialIndent=[0, 10][(node.mode == 0)])
        return max([0, 41, 73][node.mode], height + [4, 0][(node.mode == 0)])



    def GetMenu(self):
        m = []
        if self.sr.text._activeLink:
            if self.sr.text._activeLink.startswith('showinfo:'):
                ids = self.sr.text._activeLink[9:].split('//')
                try:
                    typeID = int(ids[0])
                    if len(ids) > 1:
                        itemID = int(ids[1])
                        m = sm.StartService('menu').GetMenuFormItemIDTypeID(itemID, typeID, ignoreMarketDetails=0)
                        if cfg.invtypes.Get(typeID).Group().id == const.groupCharacter:
                            m += [None]
                            m += ChannelMenu(self.sr.node.channelid, itemID)
                    else:
                        m = uicls.BaseLink().GetLinkMenu(self.sr.text, self.sr.text._activeLink.replace('&amp;', '&'))
                except:
                    log.LogTraceback('failed to convert string to ids in chat entry:GetMenu')
                    sys.exc_clear()
            else:
                m = uicls.BaseLink().GetLinkMenu(self.sr.text, self.sr.text._activeLink.replace('&amp;', '&'))
        m += [None,
         (mls.UI_CMD_COPY, self.CopyText),
         (mls.UI_CMD_COPYALL, self.CopyAll),
         (mls.UI_CMD_TOGGLETIMESTAMP, self.ToggleTimestamp)]
        return m



    def ToggleTimestamp(self, *args):
        c = settings.user.ui.Get('timestampchat', 0)
        settings.user.ui.Set('timestampchat', not c)
        channelWindow = sm.GetService('LSC').GetChannelWindow(self.sr.node.channelid)
        if channelWindow:
            channelWindow.LoadMessages()



    def CopyText(self):
        (who, txt, charid, time, colorkey,) = self.sr.node.msg
        timestr = ''
        if settings.user.ui.Get('timestampchat', 0):
            (year, month, wd, day, hour, min, sec, ms,) = util.GetTimeParts(time)
            timestr = '[%02d:%02d:%02d] ' % (hour, min, sec)
        t = '%s%s > %s' % (timestr, who, txt.replace('&gt;', '>').replace('&amp;', '&'))
        blue.pyos.SetClipboardData(t)



    def CopyAll(self):
        t = ''
        for node in self.sr.node.scroll.GetNodes():
            (who, txt, charid, time, colorkey,) = node.msg
            timestr = ''
            if settings.user.ui.Get('timestampchat', 0):
                (year, month, wd, day, hour, min, sec, ms,) = util.GetTimeParts(time)
                timestr = '[%02d:%02d:%02d] ' % (hour, min, sec)
            t += '%s%s > %s\r\n' % (timestr, who, txt.replace('&gt;', '>').replace('&amp;', '&'))

        blue.pyos.SetClipboardData(t)




def GetColor(role, asInt = 0):
    for (colorkey, color, intCol,) in [(service.ROLE_QA, '0xff0099ff', LtoI(4278229503L)),
     (service.ROLE_WORLDMOD, '0xffac75ff', LtoI(4289492479L)),
     (service.ROLE_GMH, '0xffee6666', LtoI(4293813862L)),
     (service.ROLE_GML, '0xffffff20', LtoI(4294967072L)),
     (service.ROLE_CENTURION, '0xff00ff00', LtoI(4278255360L)),
     (service.ROLE_LEGIONEER, '0xff00ffcc', LtoI(4278255564L)),
     (service.ROLE_ADMIN, '0xffee6666', LtoI(4293813862L))]:
        if role & colorkey == colorkey:
            return [color, intCol][asInt]

    return ['0xffe0e0e0', LtoI(4292927712L)][asInt]



def FormatTxt(msg, mode = 0, fontsize = 12, letterSpace = 0, localEcho = False):
    (who, txt, charid, time, colorkey,) = msg
    if type(charid) in types.StringTypes:
        return txt
    color = GetColor(colorkey)
    timestr = ''
    if settings.user.ui.Get('timestampchat', 0):
        (year, month, wd, day, hour, min, sec, ms,) = util.GetTimeParts(time)
        timestr = '<color=%s>[%02d:%02d:%02d]</color> ' % (color,
         hour,
         min,
         sec)
    if charid == const.ownerSystem:
        info = 'showinfo:5//%s' % (eve.session.solarsystemid or eve.session.solarsystemid2)
    else:
        info = 'showinfo:1373//%s' % charid
    if txt.startswith('/emote'):
        return '%s<url:%s><color=%s>* %s</color></url><color=%s> %s</color>' % (timestr,
         info,
         color,
         who,
         color,
         LinkURLs(txt[7:], color))
    if txt.startswith('/slash') and localEcho:
        return '<color=0xff00dddd>%s</color>' % txt[1:]
    return '%s<url:%s><color=%s>%s</color></url><color=%s> &gt; %s</color>' % (timestr,
     info,
     color,
     who,
     color,
     LinkURLs(txt, color))



def LinkURLs(txt, color):
    index = 0
    match = seemsURL.search(txt)
    while match:
        (start, end,) = match.span()
        group = grouplink = match.group()
        if group.startswith('www'):
            grouplink = 'http://%s' % group
        if not start or txt[(index + start - 1)] not in ('>', '"', '='):
            txt = txt[:(index + start)] + '</color><url:' + grouplink + '>' + group + '</url><color=' + color + '>' + txt[(index + end):]
            index += 2 * end + 36
        else:
            index += end
        match = seemsURL.search(txt[index:])

    return txt


exports = {'chat.GetColor': GetColor,
 'chat.FormatTxt': FormatTxt}

