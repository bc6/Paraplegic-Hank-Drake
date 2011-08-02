import sys
import blue
import uthread
import uix
import xtriui
import form
import cPickle
import listentry
import util
import types
import service
import chat
import draw
import uiutil
import uiconst
import uicls

class ChannelsSvc(service.Service):
    __exportedcalls__ = {'Show': [],
     'RefreshMine': []}
    __guid__ = 'svc.channels'
    __notifyevents__ = ['ProcessSessionChange']
    __servicename__ = 'channels'
    __displayname__ = 'Channels Client Service'
    __dependencies__ = []
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.LogInfo('Starting Channels')
        self.semaphore = uthread.Semaphore()



    def Stop(self, memStream = None):
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            wnd.SelfDestruct()



    def ProcessSessionChange(self, isremote, session, change):
        if session.charid is None:
            self.Stop()



    def Show(self):
        wnd = self.GetWnd(1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()



    def GetWnd(self, create = 0):
        if create:
            sm.GetService('tutorial').OpenTutorialSequence_Check(uix.advchannelsTutorial)
        return sm.GetService('window').GetWindow('channels', create, decoClass=form.Channels)



    def SetHint(self, hintstr = None):
        wnd = self.GetWnd()
        if wnd is not None:
            wnd.sr.scroll.ShowHint(hintstr)



    def CreateOrJoinChannel(self, name, doCreate = True):
        s = self.semaphore
        s.acquire()
        try:
            if len(name) > 60:
                raise UserError('ChatCustomChannelNameTooLong', {'max': 60})
            if len(name.split('\\')) > [1, 2][(eve.session.role & (service.ROLE_CHTADMINISTRATOR | service.ROLE_GMH) != 0)]:
                raise UserError('ChatCustomChannelNameNoSeparators')
            sm.GetService('LSC').CreateOrJoinChannel(name, create=doCreate)
            self.RefreshMine()

        finally:
            s.release()




    def RefreshMine(self, reload = 0):
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            wnd.ShowContent(reload)




class ChannelField(listentry.Generic):
    __guid__ = 'listentry.ChannelField'
    __nonpersistvars__ = ['groupID',
     'status',
     'active',
     'selection',
     'channel']

    def Startup(self, *args):
        listentry.Generic.Startup(self, *args)
        self.joinleaveBtn = uicls.Button(parent=self, label=mls.UI_CMD_JOIN, func=self.JoinLeaveChannelFromBtn, idx=0, left=2, align=uiconst.CENTERRIGHT)



    def Load(self, node):
        listentry.Generic.Load(self, node)
        if type(self.sr.node.channel.channelID) == types.IntType or self.sr.node.channel.channelID[0][0] in ('global', 'regionid', 'constellationid') or self.sr.node.channel.channelID[0][0] == 'corpid' and self.sr.node.channel.channelID[0][1] != session.corpid:
            self.joinleaveBtn.state = uiconst.UI_NORMAL
            if self.sr.node.isJoined:
                self.joinleaveBtn.SetLabel(mls.UI_CMD_LEAVE)
            else:
                self.joinleaveBtn.SetLabel(mls.UI_CMD_JOIN)
        else:
            self.joinleaveBtn.state = uiconst.UI_HIDDEN



    def GetHeight(self, *args):
        (node, width,) = args
        btnHeight = uix.GetTextHeight(mls.UI_CMD_LEAVE + mls.UI_CMD_JOIN, autoWidth=1, singleLine=1, fontsize=10, hspace=1, uppercase=1) + 9
        node.height = btnHeight + 2
        return node.height



    def OnDblClick(self, *args):
        channelID = self.sr.node.channel.channelID
        if type(channelID) != types.IntType and not eve.session.role & (service.ROLE_CHTADMINISTRATOR | service.ROLE_GMH):
            if channelID[0][0] not in ('global', 'regionid', 'constellationid'):
                return 
        self.JoinLeaveChannel()



    def GetMenu(self):
        self.OnClick()
        channelID = self.sr.node.channel.channelID
        menu = []
        if type(self.sr.node.channel.channelID) == types.IntType or self.sr.node.channel.channelID[0][0] in ('global', 'regionid', 'constellationid'):
            if sm.GetService('LSC').IsJoined(channelID):
                menu.append((mls.UI_CMD_LEAVECHANNEL, self.JoinLeaveChannel, (channelID,)))
            else:
                menu.append((mls.UI_CMD_JOINCHANNEL, self.JoinLeaveChannel, (channelID,)))
        if sm.GetService('LSC').IsOwner(self.sr.node.channel) or type(channelID) != types.IntType and getattr(channelID, 'ownerID', 0) > 100000000 and sm.GetService('LSC').IsCreator(channelID):
            menu.append((mls.UI_CMD_DELETECHANNEL, self.DeleteChannel))
        elif sm.GetService('LSC').IsForgettable(channelID):
            menu.append((mls.UI_CMD_FORGETCHANNEL, self.ForgetChannel))
        if type(channelID) == types.IntType and sm.GetService('LSC').IsOperator(channelID):
            menu.append((mls.UI_CMD_SETTINGS, self.Settings))
        if len(menu):
            return menu



    def Settings(self, *args):
        sm.GetService('LSC').Settings(self.sr.node.channel.channelID)



    def JoinLeaveChannelFromBtn(self, *args):
        self.JoinLeaveChannel()



    def JoinLeaveChannel(self, chID = None, *args):
        channelID = chID if chID != None else self.sr.node.channel.channelID
        self.state = uiconst.UI_DISABLED
        sm.GetService('LSC').JoinOrLeaveChannel(channelID)
        self.state = uiconst.UI_NORMAL



    def DeleteChannel(self, *args):
        self.state = uiconst.UI_DISABLED
        try:
            sm.GetService('LSC').DestroyChannel(self.sr.node.channel)
            sm.GetService('channels').RefreshMine(reload=True)

        finally:
            self.state = uiconst.UI_NORMAL



    DeleteChannel = uiutil.ParanoidDecoMethod(DeleteChannel, ('sr', 'node', 'channel'))

    def ForgetChannel(self, *args):
        self.state = uiconst.UI_DISABLED
        try:
            sm.GetService('LSC').ForgetChannel(self.sr.node.channel.channelID)
            sm.GetService('channels').RefreshMine(reload=True)

        finally:
            self.state = uiconst.UI_NORMAL



    ForgetChannel = uiutil.ParanoidDecoMethod(ForgetChannel, ('sr', 'node', 'channel', 'channelID'))


class MailboxField(listentry.Generic):
    __guid__ = 'listentry.MailboxField'
    __nonpersistvars__ = ['groupID',
     'status',
     'active',
     'selection',
     'channel']

    def Startup(self, *args):
        listentry.Generic.Startup(self, *args)
        if sm.StartService('LSC').IsCreator(self.sr.node.channel.channelID):
            self.joinleaveBtn = uicls.Button(parent=self, label=mls.UI_CMD_DELETE, func=self.DeleteChannel, idx=0, left=2, align=uiconst.CENTERRIGHT)
        else:
            self.joinleaveBtn = uicls.Button(parent=self, label=mls.UI_CMD_SUBSCRIBE, func=self.JoinLeaveChannelFromBtn, idx=0, left=2, align=uiconst.CENTERRIGHT)



    def Load(self, node):
        listentry.Generic.Load(self, node)
        if sm.StartService('LSC').IsCreator(self.sr.node.channel.channelID):
            self.joinleaveBtn.SetLabel(mls.UI_CMD_DELETE)
        elif sm.StartService('LSC').IsJoined(self.sr.node.channel.channelID):
            self.joinleaveBtn.SetLabel(mls.UI_CMD_UNSUBSCRIBE)
        else:
            self.joinleaveBtn.SetLabel(mls.UI_CMD_SUBSCRIBE)



    def GetHeight(self, *args):
        (node, width,) = args
        btnHeight = uix.GetTextHeight(mls.UI_CMD_UNSUBSCRIBE + mls.UI_CMD_SUBSCRIBE, autoWidth=1, singleLine=1, fontsize=10, hspace=1, uppercase=1) + 9
        node.height = btnHeight + 2
        return node.height



    def GetMenu(self):
        self.OnClick()
        channelID = self.sr.node.channel.channelID
        menu = []
        if not sm.StartService('LSC').IsCreator(channelID):
            if sm.StartService('LSC').IsJoined(channelID):
                menu.append((mls.UI_CMD_UNSUBSCRIBEFROMLIST, self.JoinLeaveChannel, (channelID,)))
            else:
                menu.append((mls.UI_CMD_SUBSCRIBETOLIST, self.JoinLeaveChannel, (channelID,)))
        if sm.GetService('LSC').IsCreator(channelID):
            menu.append((mls.UI_CMD_DELETELIST, self.DeleteChannel))
        elif sm.GetService('LSC').IsForgettable(channelID):
            menu.append((mls.UI_CMD_FORGETLIST, self.ForgetChannel))
        if type(channelID) == types.IntType and sm.GetService('LSC').IsOperator(channelID):
            menu.append((mls.UI_CMD_SETTINGS, self.Settings))
        if len(menu):
            return menu



    def Settings(self, *args):
        sm.GetService('LSC').Settings(self.sr.node.channel.channelID)



    def JoinLeaveChannelFromBtn(self, *args):
        self.JoinLeaveChannel()



    def JoinLeaveChannel(self, chID = None, *args):
        channelID = chID if chID != None else self.sr.node.channel.channelID
        self.state = uiconst.UI_DISABLED
        s = sm.StartService('channels').semaphore
        s.acquire()
        try:
            if sm.GetService('LSC').IsJoined(channelID):
                sm.GetService('LSC').LeaveChannel(channelID, unsubscribe=1)
            else:
                sm.GetService('LSC').JoinChannel(channelID)
            sm.GetService('channels').RefreshMine(reload=True)

        finally:
            s.release()
            self.state = uiconst.UI_NORMAL




    def DeleteChannel(self, *args):
        self.state = uiconst.UI_DISABLED
        try:
            sm.GetService('LSC').DestroyChannel(self.sr.node.channel)
            sm.GetService('channels').RefreshMine(reload=True)

        finally:
            self.state = uiconst.UI_NORMAL



    DeleteChannel = uiutil.ParanoidDecoMethod(DeleteChannel, ('sr', 'node', 'channel'))

    def ForgetChannel(self, *args):
        self.state = uiconst.UI_DISABLED
        try:
            sm.GetService('LSC').ForgetChannel(self.sr.node.channel.channelID)
            sm.GetService('channels').RefreshMine(reload=True)

        finally:
            self.state = uiconst.UI_NORMAL



    ForgetChannel = uiutil.ParanoidDecoMethod(ForgetChannel, ('sr', 'node', 'channel', 'channelID'))


class Channels(uicls.Window):
    __guid__ = 'form.Channels'
    __neocommenuitem__ = (('Channel window', '51_10'), 'Startup', service.ROLE_GML)

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.loadingShowcontent = 0
        self.SetScope('station_inflight')
        self.SetMinSize([400, 250])
        self.SetCaption(mls.UI_SHARED_CHANNELS)
        self.SetWndIcon('ui_9_64_2')
        self.SetTopparentHeight(70)
        self.sr.inpt = inpt = uicls.SinglelineEdit(name='input', parent=self.sr.topParent, maxLength=60, left=74, top=20, width=86, label=mls.UI_SHARED_CHANNELNAME)
        joinBtn = uicls.Button(parent=self.sr.topParent, label=mls.UI_CMD_JOIN, pos=(inpt.left,
         inpt.top + inpt.height + 4,
         0,
         0), func=self.JoinChannelFromBtn, args='self', btn_default=1)
        createBtn = uicls.Button(parent=self.sr.topParent, label=mls.UI_CMD_CREATE, pos=(joinBtn.left + joinBtn.width + 2,
         joinBtn.top,
         0,
         0), func=self.CreateChannelFromBtn, args='self')
        self.sr.inpt.width = max(100, joinBtn.left + joinBtn.width - inpt.left)
        channelsMaillist = uicls.Container(name='channelsMaillist', parent=self.sr.main, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding)
        self.sr.scroll = uicls.Scroll(parent=channelsMaillist)
        self.sr.scroll.multiSelect = 0
        self.ShowContent()



    def ShowContent(self, reload = 1):
        uthread.new(self.ShowContent_thread, reload).context = 'Channels::ShowContent'



    def ShowContent_thread(self, reload = 1):
        if getattr(self, 'loadingShowcontent', 0):
            return 
        self.loadingShowcontent = 1
        try:
            channels = sm.GetService('LSC').GetChannels(reload)
            what = mls.UI_SHARED_CHANNELS
            scrolllist = []
            tree = {mls.UI_GENERIC_OTHER: {}}
            for channel in channels:
                if channel.displayName is None or getattr(channel, 'temporary', 0):
                    continue
                path = channel.displayName.split('\\')
                if len(path) > 1:
                    l = tree
                    for i in range(len(path)):
                        p = path[i].capitalize()
                        if i == len(path) - 1:
                            l[p] = channel
                        elif p not in l:
                            l[p] = {}
                            l = l[p]
                        else:
                            l = l[p]

                elif channel.ownerID == const.ownerSystem:
                    tree[mls.UI_GENERIC_OTHER][channel.displayName] = channel
                elif channel.ownerID == eve.session.charid:
                    if '%s %s' % (mls.UI_GENERIC_MY, what) not in tree:
                        tree['%s %s' % (mls.UI_GENERIC_MY, what)] = {}
                    tree[('%s %s' % (mls.UI_GENERIC_MY, what))][channel.displayName] = channel
                else:
                    if '%s %s' % (mls.UI_GENERIC_PLAYER, what) not in tree:
                        tree['%s %s' % (mls.UI_GENERIC_PLAYER, what)] = {}
                    tree[('%s %s' % (mls.UI_GENERIC_PLAYER, what))][channel.displayName] = channel

            if not self or self.destroyed:
                return 
            scrolllist = self._Channels__BuildTreeList(tree)
            h = [mls.UI_GENERIC_NAME, mls.UI_CORP_MEMBERS]
            self.sr.scroll.Load(fixedEntryHeight=24, contentList=scrolllist, headers=h)

        finally:
            if self and not self.destroyed:
                self.loadingShowcontent = 0




    def __BuildTreeList(self, tree, indent = 0):
        ret = []
        lscSvc = None
        h = [mls.UI_GENERIC_NAME, mls.UI_CORP_MEMBERS]
        guid = 'ChannelField'
        lscSvc = sm.StartService('LSC')
        for (k, v,) in tree.iteritems():
            if type(v) == types.DictType:
                group = uicore.registry.GetListGroup(('CHANNELSchannels', k))
                data = {'GetSubContent': self._Channels__GetSubContent,
                 'RefreshScroll': self.RefreshMine,
                 'label': '    ' * indent + k,
                 'id': ('CHANNELSchannels', k),
                 'groupItems': (indent, v),
                 'headers': h,
                 'iconMargin': 18,
                 'showlen': 0,
                 'state': 'locked',
                 'allowCopy': 0,
                 'showicon': 'ui_22_32_32',
                 'posttext': ' [%s]' % len(v),
                 'allowGuids': ['listentry.Group', 'listentry.%s' % guid]}
                ret.append((k, listentry.Get('Group', data)))
            else:
                data = util.KeyVal()
                data.channel = v
                data.label = '    ' * indent + '%s<t>%s' % (v.displayName.split('\\')[-1], v.estimatedMemberCount or '')
                data.isJoined = lscSvc.IsJoined(v.channelID)
                ret.append((v.displayName, listentry.Get(guid, data=data)))

        ret.sort()
        ret2 = []
        for each in ret:
            ret2.append(each[1])

        return ret2



    def RefreshMine(self, *args):
        self.ShowContent()



    def __GetSubContent(self, nodedata, newitems = 0):
        (indent, sub,) = nodedata.groupItems
        if not len(sub):
            return []
        return self._Channels__BuildTreeList(sub, indent + 1)



    def CreateChannelFromBtn(self, btn, *args):
        self.CreateOrJoinChannel(btn, create=1)



    def JoinChannelFromBtn(self, btn, *args):
        self.CreateOrJoinChannel(btn, create=0)



    def CreateOrJoinChannel(self, btn, create = 1, *args):
        name = self.sr.inpt.GetValue()
        if name.strip() == '':
            eve.Message('LookupStringMinimum', {'minimum': 1})
            return 
        try:
            channelID = sm.GetService('LSC').GetChannelIDFromName(name)
            if channelID is not None:
                wnd = sm.GetService('window').GetWindow('chatchannel_%s' % channelID, create=0, maximize=1)
                if wnd:
                    eve.Message('LSCChannelIsJoined', {'displayName': name})
                    return 
            btn.Disable()
            sm.GetService('channels').CreateOrJoinChannel(name=name, doCreate=create)

        finally:
            if not btn.dead:
                btn.Enable()





