import uix
import uiconst
import uiutil
import xtriui
import form
import blue
import util
import listentry
import uthread
import uicls
import fleetbr
import fleetcommon
BROADCAST_HEIGHT = 46

class FleetWindow(uicls.Window):
    __guid__ = 'form.FleetWindow'
    __notifyevents__ = ['OnFleetBroadcast_Local', 'OnSpeakingEvent_Local', 'OnBroadcastScopeChange']
    default_width = 400
    default_height = 300

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        tabIdx = attributes.tabIdx
        self.isFlat = settings.user.ui.Get('flatFleetView', True)
        self.scope = 'all'
        self.broadcastMenuItems = []
        self.SetCaption(mls.UI_FLEET_FLEET)
        self.SetTopparentHeight(0)
        self.SetWndIcon('53_16')
        self.SetHeaderIcon()
        hicon = self.sr.headerIcon
        hicon.GetMenu = self.GetFleetMenuTop
        hicon.expandOnLeft = 1
        hicon.hint = mls.UI_FLEET_FORMFLEET
        currentryActiveColumn = settings.user.ui.Get('activeSortColumns', {})
        self.sr.main = uiutil.GetChild(self, 'main')
        self.InitBroadcastBottom()
        myFleetParent = uicls.Container(name='myfleet', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        uicls.Container(name='push', parent=myFleetParent, width=const.defaultPadding, align=uiconst.TOLEFT)
        uicls.Container(name='push', parent=myFleetParent, width=const.defaultPadding, align=uiconst.TORIGHT)
        self.sr.myFleetContent = form.FleetView(parent=myFleetParent, name='fleetfinderpar', pos=(0, 0, 0, 0))
        broadcastsParent = uicls.Container(name='broadcasts', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.broadcastsContent = form.FleetBroadcastView(parent=broadcastsParent, name='fleetfinderpar', pos=(0, 0, 0, 0))
        fleetFinderParent = uicls.Container(name='fleetfinder', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.fleetFinderContent = form.FleetFinderWindow(parent=fleetFinderParent, name='fleetfinderpar', pos=(0, 0, 0, 0))
        settingsParent = uicls.Container(name='settings', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.startPage = uicls.Container(name='startpage', parent=self.sr.main, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        myFleetParent.children.append(self.startPage)
        self.sr.tabs = uicls.TabGroup(name='fleettabs', parent=self.sr.main, idx=0)
        tabs = []
        inFleetTabs = [[mls.UI_FLEET_MYFLEET,
          myFleetParent,
          self,
          'myfleet'], [mls.UI_FLEET_HISTORY,
          broadcastsParent,
          self,
          'broadcasts']]
        fleetFinderTabs = [[mls.UI_FLEET_FLEETFINDER,
          fleetFinderParent,
          self,
          'fleetfinder']]
        if session.fleetid is not None:
            tabs.extend(inFleetTabs)
        tabs.extend(fleetFinderTabs)
        self.sr.tabs.Startup(tabs, 'fleettabs', autoselecttab=1)
        if session.fleetid:
            tabToOpen = mls.UI_FLEET_MYFLEET
        else:
            tabToOpen = mls.UI_FLEET_FLEETFINDER
        uthread.new(self.sr.tabs.ShowPanelByName, tabToOpen)
        if settings.user.ui.Get('fleetFinderBroadcastsVisible', False) and session.fleetid:
            self.ToggleBroadcasts()



    def OnClose_(self, *args):
        pass



    def ToggleBroadcasts(self, *args):
        if self.sr.broadcastBottom.state != uiconst.UI_HIDDEN:
            self.sr.broadcastBottom.state = uiconst.UI_HIDDEN
            self.sr.broadcastExpanderIcon.texturePath = 'res:/UI/Texture/Shared/expanderUp.png'
            settings.user.ui.Set('fleetFinderBroadcastsVisible', False)
        else:
            self.sr.broadcastBottom.state = uiconst.UI_PICKCHILDREN
            self.sr.broadcastExpanderIcon.texturePath = 'res:/UI/Texture/Shared/expanderDown.png'
            settings.user.ui.Set('fleetFinderBroadcastsVisible', True)
        self.UpdateMinSize()



    def InitBroadcastBottom(self):
        self.sr.broadcastBottom = uicls.Container(name='broadcastBottom', parent=self.sr.main, align=uiconst.TOBOTTOM, height=BROADCAST_HEIGHT, state=uiconst.UI_HIDDEN)
        broadcastHeaderParent = uicls.Container(name='lastbroadcastheader', parent=self.sr.main, align=uiconst.TOBOTTOM, state=uiconst.UI_NORMAL, height=24)
        broadcastHeaderParent.padBottom = 3
        expanderCont = uicls.Container(name='expanderCont', parent=broadcastHeaderParent, align=uiconst.TORIGHT, state=uiconst.UI_NORMAL, width=18)
        expanderCont.OnClick = self.ToggleBroadcasts
        c = '<b>%s</b>' % mls.UI_FLEET_BROADCASTS
        c = ''
        t = uicls.Label(text=c, parent=broadcastHeaderParent, state=uiconst.UI_DISABLED, left=6, align=uiconst.CENTERLEFT)
        broadcastHeaderParent.height = max(16, t.textheight + 2)
        self.sr.broadcastHeaderParent = broadcastHeaderParent
        expander = uicls.Sprite(parent=expanderCont, pos=(5, 0, 11, 11), name='expandericon', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/expanderUp.png', align=uiconst.TOPRIGHT)
        self.sr.broadcastExpanderIcon = expander
        uix.Flush(self.sr.broadcastBottom)
        self.sr.lastBroadcastCont = uicls.Container(name='lastBroadcastCont', parent=broadcastHeaderParent, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_NORMAL)
        t = uicls.Label(text='<color=0xFF999999>%s</color>' % mls.UI_FLEET_NOBROADCASTS, parent=self.sr.lastBroadcastCont, left=6, top=1, width=500, autowidth=False, state=uiconst.UI_NORMAL)
        self.sr.lastVoiceEventCont = uicls.Container(name='lastVoiceEventCont', parent=self.sr.broadcastBottom, align=uiconst.TOPLEFT, top=0, left=0, height=20, width=200, state=uiconst.UI_NORMAL)
        uicls.Label(text='<color=0xFF999999>%s</color>' % mls.UI_FLEET_NOVOICEBROADCASTS, parent=self.sr.lastVoiceEventCont, left=6, top=0, width=500, autowidth=False)
        self.sr.actionsCont = uicls.Container(name='actionsCont', parent=self.sr.broadcastBottom, align=uiconst.TOBOTTOM, height=26, state=uiconst.UI_NORMAL)
        self.sr.toggleCont = uicls.Container(name='toggleCont', parent=self.sr.actionsCont, align=uiconst.TOBOTTOM, height=26, state=uiconst.UI_PICKCHILDREN)
        self.sr.line = uicls.Container(name='lineparent', align=uiconst.TOTOP, parent=self.sr.actionsCont, idx=0, height=1)
        uicls.Line(parent=self.sr.line, align=uiconst.TOALL)
        self.InitActions()



    def GetLastBroadcastMenu(self, broadcast):
        m = []
        func = getattr(fleetbr, 'GetMenu_%s' % broadcast.name, None)
        if func:
            m = func(broadcast.charID, broadcast.solarSystemID, broadcast.itemID)
            m += [None]
        m += fleetbr.GetMenu_Member(broadcast.charID)
        m += [None]
        m += fleetbr.GetMenu_Ignore(broadcast.name)
        return m



    def GetLastVoiceEventMenu(self, broadcast):
        m = []
        func = getattr(fleetbr, 'GetMenu_%s' % broadcast.name, None)
        if func:
            m = func(broadcast.charID, broadcast.solarSystemID, broadcast.itemID)
            m += [None]
        m += fleetbr.GetMenu_Member(broadcast.charID)
        return m



    def UpdateMinSize(self):
        args = self.sr.tabs.GetSelectedArgs()
        if not args:
            return 
        if args == 'fleetfinder':
            self.sr.broadcastBottom.state = uiconst.UI_HIDDEN
        elif settings.user.ui.Get('fleetFinderBroadcastsVisible', False) and session.fleetid:
            self.sr.broadcastBottom.state = uiconst.UI_NORMAL
        s = [uiconst.UI_NORMAL, uiconst.UI_HIDDEN][(not session.fleetid or args == 'fleetfinder')]
        self.sr.broadcastHeaderParent.state = s
        minHeight = 220
        minWidth = 256
        if session.fleetid:
            minHeight = 120
        if self.sr.broadcastBottom.state != uiconst.UI_HIDDEN:
            minHeight += BROADCAST_HEIGHT
        self.SetMinSize([minWidth, minHeight])



    def Load(self, args):
        wnd = self
        if wnd is None or wnd.destroyed:
            return 
        if args == 'myfleet':
            self.sr.myFleetContent.state = uiconst.UI_NORMAL
            self.sr.myFleetContent.Load(args)
        elif args == 'broadcasts':
            self.broadcastsContent.Load('option1')
        elif args == 'fleetfinder':
            self.fleetFinderContent.Load(args)
        self.UpdateMinSize()



    def GotoTab(self, idx):
        self.sr.tabs.SelectByIdx(idx)



    def GetFleetMenuTop(self):
        fleetSvc = sm.GetService('fleet')
        if session.fleetid is None:
            ret = [(mls.UI_FLEET_FORMFLEET, lambda : sm.GetService('menu').InviteToFleet(eve.session.charid))]
            ret.append(None)
        else:
            ret = [(mls.UI_FLEET_LEAVE, fleetSvc.LeaveFleet)]
            ret.append(None)
            if session.fleetrole in [const.fleetRoleLeader, const.fleetRoleWingCmdr, const.fleetRoleSquadCmdr]:
                ret.append((mls.UI_FLEET_REGROUP, lambda : fleetSvc.Regroup()))
            if fleetSvc.HasActiveBeacon(session.charid):
                ret.append((mls.UI_FLEET_BROADCASTBEACON, lambda : fleetSvc.SendBroadcast_JumpBeacon()))
            if fleetSvc.IsBoss():
                options = fleetSvc.GetOptions()
                ret.append(([mls.UI_FLEET_SETFREEMOVE, mls.UI_FLEET_UNSETFREEMOVE][options.isFreeMove], lambda : fleetSvc.SetOptions(isFreeMove=not options.isFreeMove)))
                ret.append(([mls.UI_FLEET_SETVOICEENABLED, mls.UI_FLEET_UNSETVOICEENABLED][options.isVoiceEnabled], lambda : fleetSvc.SetOptions(isVoiceEnabled=not options.isVoiceEnabled)))
            ret.append(None)
            ret.extend([None, [mls.UI_FLEET_BROADCASTS, self.broadcastMenuItems]])
            ret.append((mls.UI_FLEET_BROADCASTSETTINGS, lambda : sm.GetService('window').GetWindow('broadcastsettings', decoClass=form.BroadcastSettings, maximize=1, create=1)))
            ret.append(([mls.UI_FLEET_SETHEIRARCHY, mls.UI_FLEET_SETFLAT][(not self.isFlat)], self.ToggleFlat))
            if fleetSvc.IsCommanderOrBoss():
                ret.append(None)
                ret.append((mls.UI_FLEET_SHOWFLEETCOMPOSITION, fleetSvc.OpenFleetCompositionWindow))
            if fleetSvc.IsBoss():
                ret.append((mls.UI_FLEET_OPENJOINREQUESTS, fleetSvc.OpenJoinRequestWindow))
                if fleetSvc.options.isRegistered:
                    ret.append((mls.UI_FLEET_EDITREGISTRATION, sm.GetService('fleet').OpenRegisterFleetWindow))
                    ret.append((mls.UI_FLEET_UNREGISTER, sm.GetService('fleet').UnregisterFleet))
                else:
                    ret.append((mls.UI_FLEET_REGISTERFLEET, sm.GetService('fleet').OpenRegisterFleetWindow))
        return ret



    def ToggleFlat(self):
        self.isFlat = not self.isFlat
        settings.user.ui.Set('flatFleetView', self.isFlat)
        self.sr.myFleetContent.isFlat = self.isFlat
        self.sr.myFleetContent.HandleFleetChanged()



    def UpdateHeader(self):
        if self and not self.destroyed:
            self.sr.node = self.sr.myFleetContent.GetHeaderData('fleet', session.fleetid, 0)
            fleetName = mls.UI_FLEET_FLEET
            cmdrTextAlpha = 190
            fleetName %= {'alpha': cmdrTextAlpha}
            self.sr.headerIcon.hint = mls.UI_FLEET_FLEETMENU
            nMembers = len(self.sr.myFleetContent.members)
            info = sm.GetService('fleet').GetMemberInfo(session.charid)
            if info is None:
                return 
            if info.role == const.fleetRoleLeader:
                caption = '%s (%d)' % (fleetName, nMembers)
            elif info.role == const.fleetRoleWingCmdr:
                caption = '%s (%d) / %s' % (fleetName, nMembers, info.wingName)
            else:
                caption = '%s (%d) / %s / %s' % (fleetName,
                 nMembers,
                 info.wingName,
                 info.squadName)
            self.SetCaption(caption)



    def InitActions(self):
        broadcasts = ('EnemySpotted', 'HealArmor', 'HealShield', 'HealCapacitor', 'InPosition', 'NeedBackup', 'HoldPosition', 'Location')

        def BroadcastSender(name, *args):
            return lambda *args: getattr(sm.GetService('fleet'), 'SendBroadcast_%s' % name)()


        left = 6
        hmargin = 2
        self.broadcastMenuItems = []
        for name in broadcasts:
            par = xtriui.FleetAction(parent=self.sr.actionsCont, align=uiconst.TOPLEFT, top=4, left=left, width=21, height=16, state=uiconst.UI_NORMAL)
            par.OnClick = BroadcastSender(name)
            left += hmargin + par.width + 1
            hint = '%s: %s' % (mls.UI_FLEET_BROADCAST, getattr(mls, 'UI_FLEET_BROADCAST_%s' % name.upper()))
            icon = fleetbr.types[name]['smallIcon']
            par.Startup(hint, icon)
            par.align = uiconst.RELATIVE
            self.broadcastMenuItems.append((hint, BroadcastSender(name)))

        self.SetBroadcastScopeButton()
        if eve.session.fleetrole in (const.fleetRoleLeader, const.fleetRoleWingCmdr, const.fleetRoleSquadCmdr):
            self.broadcastMenuItems.append(('%s: %s' % (mls.UI_FLEET_BROADCAST, mls.UI_FLEET_TRAVELTOME), sm.GetService('fleet').SendBroadcast_TravelTo, (eve.session.solarsystemid2,)))
        self.broadcastMenuItems += [None]



    def OnBroadcastScopeChange(self):
        self.SetBroadcastScopeButton()



    def CycleBroadcastScope(self, *args):
        sm.GetService('fleet').CycleBroadcastScope()



    def SetBroadcastScopeButton(self):
        uix.Flush(self.sr.toggleCont)
        scope = sm.GetService('fleet').broadcastScope
        hint = mls.UI_FLEET_CYCLEBROADCASTSCOPE % {'name': fleetbr.GetBroadcastScopeName(scope)}
        self.sr.broadcastScopeButton = par = xtriui.FleetAction(parent=self.sr.toggleCont, align=uiconst.TOPRIGHT, top=4, left=4, width=21, height=16, state=uiconst.UI_NORMAL)
        icon = {fleetcommon.BROADCAST_DOWN: 'ui_73_16_28',
         fleetcommon.BROADCAST_UP: 'ui_73_16_27',
         fleetcommon.BROADCAST_ALL: 'ui_73_16_29'}.get(scope, 'ui_73_16_28')
        par.OnClick = self.CycleBroadcastScope
        par.Startup(hint, icon)



    def OnLastBroadcastClick(self, broadcast):
        if not uicore.uilib.Key(uiconst.VK_CONTROL) or broadcast.itemID == session.shipid or session.shipid is None or broadcast.itemID is None or util.IsUniverseCelestial(broadcast.itemID):
            return 
        itemID = broadcast.itemID
        if sm.GetService('target').IsInTargetingRange(itemID):
            sm.GetService('target').TryLockTarget(itemID)



    def OnFleetBroadcast_Local(self, broadcast):
        caption = fleetbr.GetCaption(broadcast.charID, broadcast.broadcastName, broadcast.broadcastExtra)
        caption = '<b>%s</b>' % caption
        iconName = fleetbr.defaultIcon[1]
        t = fleetbr.types.get(broadcast.name, None)
        if t:
            iconName = t['smallIcon']
        roleIcon = fleetbr.GetRoleIconFromCharID(broadcast.charID)
        self.sr.lastBroadcastCont.Flush()
        t = uicls.Label(text=caption, parent=self.sr.lastBroadcastCont, align=uiconst.TOALL, left=25, singleline=1, state=uiconst.UI_DISABLED)
        self.sr.lastBroadcastCont.GetMenu = lambda : self.GetLastBroadcastMenu(broadcast)
        self.sr.lastBroadcastCont.OnClick = lambda : self.OnLastBroadcastClick(broadcast)
        captionHint = broadcast.broadcastName
        if broadcast.broadcastExtra:
            captionHint += ' - %s' % broadcast.broadcastExtra
        hintRole = ''
        info = sm.GetService('fleet').GetMemberInfo(int(broadcast.charID))
        hintRole = fleetbr.GetRankName(info)
        if hintRole:
            hintRole = ' - <b>%s</b>' % hintRole
        sendByHint = '%s %s%s' % (mls.UI_FLEET_SENTBY, cfg.eveowners.Get(broadcast.charID).name, hintRole)
        sentAtHint = '%s %s' % (mls.UI_FLEET_SENTAT, util.FmtDate(broadcast.time, 'nl'))
        recipientsHint = '%s %s' % (mls.UI_FLEET_SENTTO, fleetbr.GetBroadcastScopeName(broadcast.scope))
        if broadcast.where != fleetcommon.BROADCAST_UNIVERSE:
            recipientsHint += ' (%s)' % fleetbr.GetBroadcastWhereName(broadcast.where)
        self.sr.lastBroadcastCont.hint = '%s<br>%s<br>%s<br>%s' % (captionHint,
         sendByHint,
         recipientsHint,
         sentAtHint)
        icon = uicls.Icon(icon=iconName, parent=self.sr.lastBroadcastCont, align=uiconst.RELATIVE, pos=(6, 0, 16, 16), state=uiconst.UI_DISABLED)
        uthread.worker('fleet::flash', self.Flash, icon)



    def Flash(self, icon):
        timeStart = blue.os.GetTime()
        period = 0.7
        cycles = 3
        duration = period * int(cycles)
        import math
        coeff = math.pi / period
        while True:
            time = (blue.os.GetTime() - timeStart) / 10000000.0
            if time >= duration:
                icon.SetAlpha(1.0)
                return 
            icon.SetAlpha(1.0 - math.sin(coeff * (time % period)))
            blue.pyos.synchro.Sleep(10)




    def OnSpeakingEvent_Local(self, data):
        if self.destroyed:
            return 
        caption = mls.UI_FLEET_ISSPEAKINGIN % {'who': data.charName,
         'where': data.channelName}
        caption = '<b>%s</b>' % caption
        iconName = '73_35'
        roleIcon = fleetbr.GetRoleIconFromCharID(data.charID)
        uix.Flush(self.sr.lastVoiceEventCont)
        t = uicls.Label(text=caption, parent=self.sr.lastVoiceEventCont, align=uiconst.TOALL, left=25, singleline=1, autoheight=False, autowidth=False)
        lt = t
        lt.GetMenu = lambda : fleetbr.GetVoiceMenu(None, data.charID, data.channelID)
        lt.hint = '%s<br>%s' % (caption, mls.UI_FLEET_BROADCASTRECEIVEDAT % {'time': util.FmtDate(data.time, 'nl')})
        icon = uicls.Icon(align=uiconst.RELATIVE, left=6, top=0, icon=iconName, width=16, height=16)
        icon.state = uiconst.UI_DISABLED
        self.sr.lastVoiceEventCont.children.append(icon)




class FleetJoinRequestWindow(uicls.Window):
    __guid__ = 'form.FleetJoinRequestWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scope = 'all'
        self.SetCaption(mls.UI_FLEET_JOINREQUESTS)
        self.SetMinSize([256, 75])
        self.SetTopparentHeight(0)
        self.SetWndIcon('53_16')
        self.SetTopparentHeight(0)
        self.sr.main.left = self.sr.main.width = self.sr.main.top = self.sr.main.height = const.defaultPadding
        uicls.Label(text=mls.UI_FLEET_JOINREQUESTSHELP, parent=self.sr.main, align=uiconst.TOTOP, left=20, autowidth=False, state=uiconst.UI_NORMAL)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, height=6)
        self.sr.scroll = uicls.Scroll(parent=self.sr.main)
        self.sr.scroll.multiSelect = 0
        self.LoadJoinRequests()



    def OnClose_(self, *args):
        pass



    def LoadJoinRequests(self):
        scrolllist = []
        for joinRequest in sm.GetService('fleet').GetJoinRequests().itervalues():
            if joinRequest is None:
                continue
            name = cfg.eveowners.Get(joinRequest.charID).name
            data = util.KeyVal()
            data.label = name
            data.props = None
            data.checked = False
            data.charID = joinRequest.charID
            data.retval = None
            data.hint = None
            scrolllist.append((name, listentry.Get('JoinRequestField', data=data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        self.sr.scroll.Load(contentList=scrolllist)




class JoinRequestField(listentry.Generic):
    __guid__ = 'listentry.JoinRequestField'
    __nonpersistvars__ = []

    def Startup(self, *args):
        listentry.Generic.Startup(self, *args)
        self.rejectBtn = uicls.Button(parent=self, label='<color=0xFFFF5555>%s' % mls.UI_FLEET_REJECT, left=2, func=self.RejectJoinRequest, idx=0, align=uiconst.TOPRIGHT)
        self.acceptBtn = uicls.Button(parent=self, label='<color=0xFF55FF55>%s' % mls.UI_FLEET_ACCEPT, left=self.rejectBtn.left + self.rejectBtn.width + 2, func=self.AcceptJoinRequest, idx=0, align=uiconst.TOPRIGHT)



    def Load(self, node):
        listentry.Generic.Load(self, node)



    def GetHeight(self, *args):
        (node, width,) = args
        btnHeight = uix.GetTextHeight(mls.UI_CMD_LEAVE + mls.UI_CMD_JOIN, autoWidth=1, singleLine=1, fontsize=10, hspace=1, uppercase=1) + 9
        node.height = btnHeight + 2
        return node.height



    def GetMenu(self, *args):
        menuSvc = sm.GetService('menu')
        charID = self.sr.node.charID
        m = []
        m += [(mls.UI_CMD_SHOWINFO, menuSvc.ShowInfo, (int(1377),
           charID,
           0,
           None,
           None))]
        m += [None]
        m += menuSvc.CharacterMenu(charID)
        return m



    def AcceptJoinRequest(self, *args):
        charID = self.sr.node.charID
        sm.GetService('fleet').Invite(charID, None, None, None)



    def RejectJoinRequest(self, *args):
        charID = self.sr.node.charID
        sm.GetService('fleet').RejectJoinRequest(charID)




class FleetComposition(uicls.Window):
    __guid__ = 'form.FleetComposition'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scope = 'all'
        self.SetCaption(mls.UI_FLEET_FLEETCOMPOSITION)
        self.SetMinSize([360, 200])
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.sr.main.left = self.sr.main.width = self.sr.main.top = self.sr.main.height = const.defaultPadding
        self.sr.top = uicls.Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, height=34)
        self.sr.bottom = uicls.Container(name='bottomCont', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        refreshButtCont = uicls.Container(name='refreshButtCont', parent=self.sr.top, align=uiconst.TORIGHT, width=80)
        uicls.Label(text=mls.UI_FLEET_FLEETCOMPOSITIONHELP, parent=self.sr.top, align=uiconst.TOALL, left=3, autowidth=False)
        self.sr.refreshBtn = btn = uicls.Button(parent=refreshButtCont, label=mls.UI_GENERIC_REFRESH, left=2, func=self.RefreshClick, align=uiconst.TOPRIGHT)
        self.sr.scrollBroadcasts = uicls.Scroll(name='scrollComposition', parent=self.sr.bottom)
        self.sr.scrollBroadcasts.multiSelect = 0
        self.LoadComposition()
        uicore.registry.SetFocus(self.sr.scrollBroadcasts)



    def LoadComposition(self):
        fleetSvc = sm.GetService('fleet')
        if not fleetSvc.IsCommanderOrBoss():
            raise UserError('FleetNotCommanderOrBoss')
        scrolllist = []
        composition = fleetSvc.GetFleetComposition()
        members = fleetSvc.GetMembers()
        for kv in composition:
            blue.pyos.BeNice()
            member = fleetSvc.GetMemberInfo(kv.characterID)
            if not fleetSvc.IsMySubordinate(kv.characterID) and not fleetSvc.IsBoss():
                continue
            roleName = member.roleName
            data = util.KeyVal()
            name = cfg.eveowners.Get(kv.characterID).name
            locationName = cfg.evelocations.Get(kv.solarSystemID).name
            shipTypeName = '(%s)' % mls.UI_GENERIC_DOCKED
            shipGroupName = '-'
            if kv.shipTypeID is not None:
                t = cfg.invtypes.Get(kv.shipTypeID)
                shipTypeName = t.name
                shipGroupName = t.Group().name
            skillLevels = '-'
            if kv.skills:
                skillLevels = '%d - %d - %d' % (kv.skills[2], kv.skills[1], kv.skills[0])
            data.label = '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (name,
             locationName,
             shipTypeName,
             shipGroupName,
             roleName,
             skillLevels)
            data.GetMenu = self.OnCompositionEntryMenu
            data.cfgname = name
            data.retval = None
            if kv.skills is not None:
                data.hint = '%s: %s<br>%s: %s<br>%s: %s' % (mls.UI_FLEET_FLEETCOMMAND,
                 kv.skills[2],
                 mls.UI_FLEET_WINGCOMMAND,
                 kv.skills[1],
                 mls.UI_FLEET_LEADERSHIP,
                 kv.skills[0])
            data.charID = kv.characterID
            data.shipTypeID = kv.shipTypeID
            data.solarSystemID = kv.solarSystemID
            scrolllist.append(listentry.Get('Generic', data=data))

        self.sr.scrollBroadcasts.sr.id = 'scrollComposition'
        self.sr.scrollBroadcasts.Load(headers=[mls.UI_GENERIC_NAME,
         mls.UI_GENERIC_LOCATION,
         mls.UI_GENERIC_SHIPTYPE,
         mls.UI_GENERIC_SHIPGROUP,
         mls.UI_FLEET_ROLE,
         mls.UI_GENERIC_SKILLS], contentList=scrolllist)



    def OnCompositionEntryMenu(self, entry):
        m = []
        data = entry.sr.node
        m += fleetbr.GetMenu_Member(data.charID)
        if data.solarSystemID:
            m += [(mls.UI_GENERIC_SOLARSYSTEM, sm.GetService('menu').CelestialMenu(data.solarSystemID))]
        if data.shipTypeID:
            m += [(mls.UI_GENERIC_SHIPTYPE, sm.GetService('menu').GetMenuFormItemIDTypeID(None, data.shipTypeID, ignoreMarketDetails=0))]
        return m



    def RefreshClick(self, *args):
        self.LoadComposition()




