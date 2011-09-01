import sys
import service
import blue
import base
import uix
import uicls
import uiutil
import uthread
import state
import log
import xtriui
import util
import uiconst

class TargetMgr(service.Service):
    __guid__ = 'svc.target'
    __exportedcalls__ = {'LockTarget': [],
     'UnlockTarget': [],
     'ClearTargets': [],
     'GetActiveTargetID': [],
     'GetTargets': [],
     'GetTargeting': [],
     'SetAsInterest': [],
     'StartLockTarget': [],
     'FailLockTarget': []}
    __notifyevents__ = ['OnTarget',
     'OnTargets',
     'ProcessSessionChange',
     'OnSpecialFX',
     'DoBallsAdded',
     'DoBallRemove',
     'DoBallClear',
     'OnStateChange']
    __dependencies__ = ['michelle', 'godma', 'settings']
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        self.viewMode = 'normal'
        self.preViewMode = None
        self.Reset()
        if eve.session.shipid and not eve.session.stationid:
            self.godma.GetStateManager().RefreshTargets()
        sm.GetService('ui').SortGlobalLayer()



    def Stop(self, stream):
        service.Service.Stop(self)
        self.viewMode = 'normal'
        self.CheckViewMode()
        self.Reset()



    def PlaceOrigin(self):
        if self.origin is not None:
            return 
        par = uicore.layer.target
        origin = uicls.Container(name='targetOrigin', parent=par, align=uiconst.RELATIVE, width=16, height=16, state=uiconst.UI_NORMAL)
        origin.OnMouseDown = (self.OnOriginMD, origin)
        origin.OnMouseUp = (self.OnOriginMU, origin)
        origin.GetMenu = self.GetOriginMenu
        origin.hint = mls.UI_INFLIGHT_TARGETSORIGIN
        origin.leftline = uicls.Line(parent=origin, align=uiconst.RELATIVE, width=4, height=1, left=-4, top=7, color=(1.0, 1.0, 1.0, 1.0))
        origin.topline = uicls.Line(parent=origin, align=uiconst.RELATIVE, width=1, height=4, left=7, top=-4, color=(1.0, 1.0, 1.0, 1.0))
        origin.rightline = uicls.Line(parent=origin, align=uiconst.RELATIVE, width=4, height=1, left=15, top=7, color=(1.0, 1.0, 1.0, 1.0))
        origin.bottomline = uicls.Line(parent=origin, align=uiconst.RELATIVE, width=1, height=4, left=7, top=15, color=(1.0, 1.0, 1.0, 1.0))
        origin.opacity = 0.25
        uicls.Icon(icon='ui_38_16_72', parent=origin, state=uiconst.UI_DISABLED)
        self.origin = origin
        self.PositionOriginWithAnchors()
        self.UpdateOriginDirection()



    def PositionOriginWithAnchors(self):
        if not self.origin:
            return 
        origin = self.origin
        ((cX, cY,), (toLeft, toTop,),) = self.GetOriginPosition(getDirection=1)
        (pl, pt, pw, ph,) = origin.parent.GetAbsolute()
        originAlign = self.GetOriginAlign(toLeft, toTop)
        origin.SetAlign(originAlign)
        if toLeft:
            origin.left = pw - cX - 8
        else:
            origin.left = cX - 8
        if toTop:
            origin.top = ph - cY - 8
        else:
            origin.top = cY - 8



    def GetOriginMenu(self):
        if settings.user.ui.Get('targetOriginLocked', 0):
            m = [(mls.UI_INFLIGHT_UNLOCKTARGETSORIGIN, self.UnlockOrigin)]
        else:
            m = [(mls.UI_INFLIGHT_LOCKTARGETSORIGIN, self.LockOrigin)]
        if settings.user.ui.Get('alignHorizontally', 1):
            m += [(mls.UI_INFLIGHT_ARRANGETARGETSVERTICALLY, self.ToggleAlignment)]
        else:
            m += [(mls.UI_INFLIGHT_ARRANGETARGETSHORIZONTALLY, self.ToggleAlignment)]
        return m



    def UnlockOrigin(self, *args):
        settings.user.ui.Set('targetOriginLocked', 0)



    def LockOrigin(self, *args):
        settings.user.ui.Set('targetOriginLocked', 1)



    def ToggleAlignment(self, *args):
        current = settings.user.ui.Get('alignHorizontally', 1)
        settings.user.ui.Set('alignHorizontally', not current)
        self.ArrangeTargets()



    def GetTargetLayerAbsolutes(self):
        d = uicore.desktop
        wnd = uicore.layer.target
        if wnd and not wnd.state == uiconst.UI_HIDDEN:
            (pl, pt, pw, ph,) = wnd.GetAbsolute()
        else:
            (pl, pt, pw, ph,) = d.GetAbsolute()
        return (wnd,
         pl,
         pt,
         pw,
         ph)



    def GetOriginPosition(self, inPixels = 1, getDirection = 0):
        d = uicore.desktop
        (wnd, pl, pt, pw, ph,) = self.GetTargetLayerAbsolutes()
        myPrefs = settings.user.ui.Get('targetOrigin', None)
        if myPrefs is None:
            selecteditem = sm.GetService('window').GetWindow('selecteditemview')
            if selecteditem and not selecteditem.IsMinimized():
                stack = getattr(selecteditem.sr, 'stack', None)
                if stack:
                    selecteditem = stack
                topAlignedWindows = selecteditem.FindConnectingWindows(selecteditem, 'top')
                (left, top, width, height,) = sm.GetService('window').GetGroupAbsolute(topAlignedWindows)
                dw = d.width
                dh = d.height
            else:
                (left, top, width, height, dw, dh,) = sm.GetService('window').GetWndPositionAndSize('selecteditemview')
            portionalCY = top / float(dh)
            if left + width < d.width / 2:
                portionalCX = (left + width - pl) / float(pw)
            elif left >= d.width / 2:
                portionalCX = (left - pl) / float(pw)
            portionalCX = (d.width - 300) / float(dw)
            portionalCY = 16 / float(d.height)
        else:
            (portionalCX, portionalCY,) = myPrefs
        if inPixels:
            ret = (int(portionalCX * pw), int(portionalCY * ph))
        else:
            ret = (portionalCX, portionalCY)
        if getDirection:
            return (ret, (bool(portionalCX > 0.5), bool(portionalCY > 0.5)))
        return ret



    def OnOriginMU(self, origin, btn, *args):
        if btn != 0 or settings.user.ui.Get('targetOriginLocked', 0):
            return 
        if uicore.uilib.mouseOver == self.origin:
            (par, tl, tt, tw, th,) = self.GetTargetLayerAbsolutes()
            origin.left = uicore.uilib.x - origin.grab[0]
            origin.top = uicore.uilib.y - origin.grab[1]
            origin.opacity = 0.25
            d = uicore.desktop
            (l, t, w, h,) = origin.GetAbsolute()
            cX = l - tl + w / 2
            cY = t - tt + h / 2
            pcX = cX / float(tw)
            pcY = cY / float(th)
            settings.user.ui.Set('targetOrigin', (pcX, pcY))
        self.ArrangeTargets()
        sm.GetService('ui').ForceCursorUpdate()
        origin.dragging = 0
        uicore.uilib.UnclipCursor()
        origin.hint = mls.UI_INFLIGHT_TARGETSORIGIN



    def OnOriginMD(self, origin, btn, *args):
        if btn != 0 or settings.user.ui.Get('targetOriginLocked', 0):
            return 
        origin.opacity = 1.0
        (l, t, w, h,) = origin.GetAbsolute()
        (pl, pt, pw, ph,) = origin.parent.GetAbsolute()
        origin.grab = [uicore.uilib.x - l, uicore.uilib.y - t]
        origin.dragging = 1
        origin.SetAlign(uiconst.ABSOLUTE)
        origin.left = l
        origin.top = t
        uthread.new(self.BeginDrag, origin)
        d = uicore.desktop
        (gx, gy,) = origin.grab
        uicore.uilib.ClipCursor(gx, gy, d.width - (origin.width - gx), d.height - (origin.height - gy))



    def UpdateOriginDirection(self):
        if not self.origin:
            return 
        origin = self.origin
        d = uicore.desktop
        (l, t, w, h,) = origin.GetAbsolute()
        cX = l + w / 2
        cY = t + h / 2
        if cX > d.width / 2:
            origin.leftline.state = uiconst.UI_NORMAL
            origin.rightline.state = uiconst.UI_HIDDEN
        else:
            origin.rightline.state = uiconst.UI_NORMAL
            origin.leftline.state = uiconst.UI_HIDDEN
        if cY > d.height / 2:
            origin.topline.state = uiconst.UI_NORMAL
            origin.bottomline.state = uiconst.UI_HIDDEN
        else:
            origin.bottomline.state = uiconst.UI_NORMAL
            origin.topline.state = uiconst.UI_HIDDEN



    def BeginDrag(self, origin):
        while not origin.destroyed and getattr(origin, 'dragging', 0):
            uicore.uilib.SetCursor(uiconst.UICURSOR_NONE)
            origin.left = uicore.uilib.x - origin.grab[0]
            origin.top = uicore.uilib.y - origin.grab[1]
            self.UpdateOriginDirection()
            if uicore.uilib.mouseOver == self.origin:
                self.origin.hint = mls.UI_INFLIGHT_MOVINGORIGIN
            else:
                self.origin.hint = ''
            blue.pyos.synchro.Sleep(1)




    def Reset(self):
        self.dogmaLM = None
        self.targets = []
        self.targetsByID = {}
        self.pendingTargets = []
        self.pendingTargeters = []
        self.targetedBy = []
        self.targeting = []
        self.autoTargeting = []
        self.weaponsOnMe = {}
        self.caminterest = None
        self.needtarget = []
        self.teams = [[], []]
        self.origin = None
        uiutil.Flush(uicore.layer.target)



    def CheckViewMode(self):
        toggleWnds = {'main': [ each for each in uicore.layer.main.children ],
         'inflight': [ each for each in uicore.layer.inflight.children if each.name not in 'l_target' ]}
        if self.viewMode == 'normal':
            if self.origin:
                self.origin.state = uiconst.UI_NORMAL
            if self.preViewMode:
                for wnd in toggleWnds:
                    layer = uicore.layer.Get(wnd)
                    for (state, name,) in self.preViewMode:
                        wnd = uiutil.FindChild(layer, name)
                        if wnd:
                            wnd.state = state


            self.preViewMode = None
        elif self.origin:
            self.origin.state = uiconst.UI_HIDDEN
        self.preViewMode = []
        for (layer, children,) in toggleWnds.iteritems():
            for wnd in children:
                if wnd and wnd.name not in ('l_bracket', 'inflightnav'):
                    self.preViewMode.append((wnd.state, wnd.name))
                    wnd.state = uiconst.UI_HIDDEN





    def IsObserving(self):
        return bool(self.viewMode == 'observe')



    def ToggleTeam(self, itemID):
        current = self.GetTeam(itemID)
        if itemID in self.teams[current]:
            self.teams[current].remove(itemID)
        new = not current
        if itemID not in self.teams[new]:
            self.teams[new].append(itemID)
        settings.user.ui.Set('targetTeamsII', self.teams[:])
        self.ArrangeTargets()



    def RemoveFromTeam(self, itemID, reset = 0):
        obs = self.IsObserving()
        if obs:
            if reset:
                settings.user.ui.Set('targetTeamsII', [[], []])
            current = self.GetTeam(itemID)
            if itemID in self.teams[current]:
                self.teams[current].remove(itemID)



    def MoveUp(self, itemID):
        current = self.GetTeam(itemID)
        teamOrder = self.teams[current]
        idx = 0
        if itemID in teamOrder:
            idx = teamOrder.index(itemID) - 1
        self.SetTeamOrder(itemID, idx)
        self.ArrangeTargets()



    def MoveDown(self, itemID):
        current = self.GetTeam(itemID)
        teamOrder = self.teams[current]
        idx = 0
        if itemID in teamOrder:
            idx = teamOrder.index(itemID) + 1
        self.SetTeamOrder(itemID, idx)
        self.ArrangeTargets()



    def GetTeam(self, itemID):
        return itemID not in self.teams[0]



    def GetTeamOrder(self, itemID):
        current = self.GetTeam(itemID)
        teamOrder = self.teams[current]
        if itemID in teamOrder:
            return teamOrder.index(itemID)
        return -1



    def SetTeamOrder(self, itemID, idx):
        idx = max(0, idx)
        current = self.GetTeam(itemID)
        if itemID in self.teams[current]:
            self.teams[current].remove(itemID)
        self.teams[current].insert(idx, itemID)



    def ToggleViewMode(self):
        self.viewMode = ['normal', 'observe'][(self.viewMode == 'normal')]
        self.Reset()
        if eve.session.shipid and not eve.session.stationid:
            self.godma.GetStateManager().RefreshTargets()
        self.CheckViewMode()
        if self.viewMode == 'observe':
            sm.GetService('neocom').ShowHideNeoComLeftSide(hide=True)
        else:
            sm.GetService('neocom').ShowHideNeoComLeftSide(hide=False)
        sm.GetService('ui').SortGlobalLayer()



    def Show(self):
        wnd = uicore.layer.target
        if wnd:
            for each in wnd.children:
                each.state = uiconst.UI_NORMAL




    def GetDogmaLM(self):
        if self.dogmaLM is None:
            self.dogmaLM = self.godma.GetDogmaLM()
        return self.dogmaLM



    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, area, guid, isOffensive, start, active, duration = -1, repeat = None, startTime = None, graphicInfo = None):
        if isOffensive and targetID == eve.session.shipid:
            self.weaponsOnMe[shipID] = self.weaponsOnMe.get(shipID, 0) + (-1, +1)[start]



    def OnStateChange(self, itemID, flag, true, *args):
        if flag == state.selected and true and self.needtarget and len(self.needtarget) > 0:
            if not self.IsTarget(itemID):
                self.HideTargetingCursor()
                target = self.needtarget[0]
                if hasattr(target, 'GetDefaultEffect'):
                    effect = self.needtarget[0].GetDefaultEffect()
                    if effect is not None and effect.effectName == 'targetPassively':
                        uthread.pool('TargetManager::OnStateChange-->ActivateTargetPassively', self.LockTargetPassively, itemID, self.needtarget[0])
                    else:
                        uthread.pool('TargetManager::OnStateChange-->LockTarget', self.TryLockTarget, itemID)
                elif target is None:
                    self.LogError("target doesn't have a GetDefaultEffect because it None")
                elif hasattr(target, '__class__'):
                    self.LogError(target.__class__.__name__, "doesn't have GetDefaultEffect attr")
                else:
                    self.LogError(target, "doesn't have GetDefaultEffect attr")
                self.needtarget = []



    def ProcessSessionChange(self, isRemote, session, change):
        if not isRemote:
            return 
        spaceShipChange = not change.has_key('solarsystemid') and change.has_key('shipid')
        if not sm.GetService('connection').IsConnected() or eve.session.stationid is not None or eve.session.charid is None:
            self.CleanUp()
        elif spaceShipChange and change['shipid'][0] is not None:
            self.OnTargetClear()
            self.pendingTargeters = []
        changingShipsInSpace = spaceShipChange and session.solarsystemid and session.shipid
        loggingDirectlyIntoSpace = change.get('solarsystemid', (1, 1))[0] is None and not eve.session.stationid
        undocking = base.IsUndockingSessionChange(session, change)
        if changingShipsInSpace or loggingDirectlyIntoSpace or undocking:
            for otherID in self.targetedBy:
                sm.GetService('state').SetState(otherID, state.threatTargetsMe, 0)

            uthread.new(self.godma.GetStateManager().RefreshTargets)
        self.dogmaLM = None



    def CleanUp(self):
        self.viewMode = 'normal'
        self.CheckViewMode()
        self.targets = []
        self.dogmaLM = None



    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::targetMgr')
        try:
            return self.DoBallsAdded_(*args, **kw)

        finally:
            t.PopTimer(timer)




    def DoBallsAdded_(self, lst):
        for (ball, slimItem,) in lst:
            if ball.id in self.pendingTargets:
                self.OnTargetAdded(ball.id)
            if ball.id in self.pendingTargeters:
                self.OnTargetByOther(ball.id)




    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return 
        self.LogInfo('DoBallRemove::targetMgr', ball.id)
        if ball.id in self.pendingTargets or ball.id in self.autoTargeting or ball.id in self.targeting:
            sm.GetService('audio').StopSoundLoop('TargetLocking', 'wise:/msg_TargetLocked_play')
        self.ClearTarget(ball.id)



    def DoBallClear(self, solitem):
        self.CleanUp()



    def OnTargets(self, targets):
        for each in targets:
            self.OnTarget(*each[1:])




    def OnTarget(self, what, tid = None, reason = None):
        if what == 'add':
            self.OnTargetAdded(tid)
        elif what == 'clear':
            self.OnTargetClear()
        elif what == 'lost':
            self.OnTargetLost(tid, reason)
        elif what == 'otheradd':
            self.OnTargetByOther(tid)
        elif what == 'otherlost':
            self.OnTargetByOtherLost(tid, reason)



    def OnTargetAdded(self, tid):
        if self.origin is None:
            self.PlaceOrigin()
        if tid in self.targeting:
            self.targeting.remove(tid)
        if tid in self.autoTargeting:
            self.autoTargeting.remove(tid)
        sm.GetService('audio').StopSoundLoop('TargetLocking', 'wise:/msg_TargetLocked_play')
        slimItem = None
        bp = sm.GetService('michelle').GetBallpark()
        if bp is not None:
            slimItem = bp.GetInvItem(tid)
        if bp is None or slimItem is None:
            if tid not in self.pendingTargets:
                self.pendingTargets.append(tid)
            return 
        sm.GetService('state').SetState(tid, state.targeting, 0)
        sm.GetService('state').SetState(tid, state.targeted, 1)
        if tid in self.pendingTargets:
            self.pendingTargets.remove(tid)
        if tid in self.targets:
            self.ClearTarget(tid)
        obs = self.IsObserving()
        if obs and not (tid in self.teams[0] or tid in self.teams[1]):
            self.teams[1].append(tid)
        target = xtriui.Target(name='target', parent=uicore.layer.target, align=uiconst.TOPRIGHT, width=[96, 160][obs], height=[128, 80][obs], state=uiconst.UI_NORMAL)
        target.Startup(slimItem)
        bracket = sm.GetService('bracket').GetBracket(tid)
        if bracket and bracket.sr.targetItem:
            bracket.sr.targetItem.state = [uiconst.UI_DISABLED, uiconst.UI_HIDDEN][obs]
        self.ArrangeTargets()
        self.targetsByID[slimItem.itemID] = target
        if not self.GetActiveTargetID():
            sm.GetService('state').SetState(tid, state.activeTarget, 1)
            if sm.GetService('state').GetExclState(state.selected) is None:
                sm.GetService('state').SetState(tid, state.selected, 1)
        if tid not in self.targets:
            self.targets.append(tid)



    def OrderTarget(self, who):
        if who not in self.needtarget[:]:
            self.needtarget.append(who)
        self.ShowTargetingCursor()



    def CancelTargetOrder(self, who = None):
        if not who and len(self.needtarget):
            for each in self.needtarget:
                if each and not each.destroyed:
                    each.waitingForActiveTarget = 0

            self.needtarget = []
        elif who in self.needtarget:
            self.needtarget.remove(who)
            who.waitingForActiveTarget = 0
        if not len(self.needtarget):
            self.HideTargetingCursor()



    def ShowTargetingCursor(self):
        nav = uix.GetInflightNav(0)
        if nav:
            nav.sr.tcursor.state = uiconst.UI_DISABLED



    def HideTargetingCursor(self):
        nav = uix.GetInflightNav(0)
        if nav:
            nav.sr.tcursor.state = uiconst.UI_HIDDEN



    def GetOriginAlign(self, toLeft, toTop):
        if toLeft:
            if toTop:
                align = uiconst.BOTTOMRIGHT
            else:
                align = uiconst.TOPRIGHT
        elif toTop:
            align = uiconst.BOTTOMLEFT
        else:
            align = uiconst.TOPLEFT
        return align



    def ArrangeTargets(self):
        self.PositionOriginWithAnchors()
        self.UpdateOriginDirection()
        obs = self.IsObserving()
        if obs:
            if self.origin:
                self.origin.state = uiconst.UI_HIDDEN
            uicore.layer.target.width = 20
            vertOffset = prefs.GetValue('tournamentVOffset', 10)
            horizOffset = prefs.GetValue('tournamentHOffset', 20)
            vertPush = prefs.GetValue('tournamentSpacing', 10)
            for target in uicore.layer.target.children:
                if getattr(target, '__guid__', None) != 'xtriui.Target':
                    continue
                team = self.GetTeam(target.itemID)
                order = self.GetTeamOrder(target.itemID)
                target.left = horizOffset
                target.top = order * (target.height - vertPush) + vertOffset
                if team:
                    target.SetAlign(uiconst.TOPRIGHT)
                else:
                    target.SetAlign(uiconst.TOPLEFT)
                target.state = uiconst.UI_NORMAL
                flag = uiutil.FindChild(target, 'flag')
                if flag is not None:
                    flag.state = uiconst.UI_HIDDEN

        else:
            ((cX, cY,), (toLeft, toTop,),) = self.GetOriginPosition(getDirection=1)
            originAlign = self.GetOriginAlign(toLeft, toTop)
            if self.origin:
                self.origin.state = uiconst.UI_NORMAL
            horizontally = settings.user.ui.Get('alignHorizontally', 1)
            x = 0
            y = 0
            (par, pl, pt, pw, ph,) = self.GetTargetLayerAbsolutes()
            if toLeft:
                baseleft = pw - cX - 16 + 48
            else:
                baseleft = cX + 16
            if toTop:
                basetop = ph - cY
            else:
                basetop = cY + 16
            margin = 2
            colOffset = 0
            for target in uicore.layer.target.children:
                if getattr(target, '__guid__', None) != 'xtriui.Target':
                    continue
                target.left = baseleft + (margin + (target.width + margin) * (x + colOffset))
                target.top = basetop + (margin + (target.height + margin) * y)
                target.state = uiconst.UI_NORMAL
                target.SetAlign(originAlign)
                if horizontally:
                    if target.left + target.width * 2 >= pw:
                        y += 1
                        x = 0
                    else:
                        x += 1
                elif target.top + target.height * 2 >= ph:
                    x += 1
                    y = 0
                else:
                    y += 1




    def SelectNextTarget(self):
        activeID = self.GetActiveTargetID()
        if activeID is None:
            return 
        index = self.targets.index(activeID) - 1
        if index < 0:
            index = -1
        self._SetSelected(self.targets[index])



    def SelectPrevTarget(self):
        activeID = self.GetActiveTargetID()
        if activeID is None:
            return 
        index = self.targets.index(activeID) + 1
        if index > len(self.targets) - 1:
            index = 0
        self._SetSelected(self.targets[index])



    def _SetSelected(self, targetID):
        sm.GetService('state').SetState(targetID, state.selected, 1)
        sm.GetService('state').SetState(targetID, state.activeTarget, 1)



    def OnTargetLost(self, tid, reason):
        (sm.GetService('state').SetState(tid, state.targeted, 0), sm.GetService('state').GetExclState(state.activeTarget))
        if sm.GetService('state').GetExclState(state.activeTarget) == tid:
            sm.GetService('state').SetState(tid, state.activeTarget, 0)
        if tid in self.pendingTargets:
            self.pendingTargets.remove(tid)
            sm.GetService('audio').StopSoundLoop('TargetLocking', 'wise:/msg_TargetLocked_play')
        self.LogInfo('OnTargetLost ', tid)
        self.ClearTarget(tid)



    def OnTargetByOther(self, otherID):
        sm.GetService('state').SetState(otherID, state.threatTargetsMe, 1)
        if otherID in self.targetedBy:
            self.LogError('already targeted by', otherID)
        else:
            self.targetedBy.append(otherID)
        bp = sm.GetService('michelle').GetBallpark()
        if bp is not None:
            slimItem = bp.GetInvItem(otherID)
        if bp is None or slimItem is None:
            if otherID not in self.pendingTargeters:
                self.pendingTargeters.append(otherID)
            return 
        if otherID in self.pendingTargeters:
            self.pendingTargeters.remove(otherID)
        tgts = self.GetTargets() + self.targeting
        if otherID != eve.session.shipid and otherID not in tgts and otherID not in self.autoTargeting:
            if min(settings.user.ui.Get('autoTargetBack', 1), sm.GetService('godma').GetItem(session.charid).maxLockedTargets, sm.GetService('godma').GetItem(session.shipid).maxLockedTargets) > len(tgts) and len(self.autoTargeting) < settings.user.ui.Get('autoTargetBack', 1):
                self.autoTargeting.append(otherID)
                uthread.pool('TargetManages::OnTargetByOther-->LockTarget', self.LockTarget, otherID, autotargeting=1)



    def GetTarget(self, targetID):
        return self.targetsByID.get(targetID, None)



    def OnTargetByOtherLost(self, otherID, reason):
        sm.GetService('state').SetState(otherID, state.threatTargetsMe, 0)
        if otherID in self.pendingTargeters:
            self.pendingTargeters.remove(otherID)
        try:
            self.targetedBy.remove(otherID)
        except ValueError:
            self.LogInfo('was not targeted by', otherID)
            sys.exc_clear()



    def OnTargetClear(self):
        for tid in self.targets[:]:
            sm.GetService('state').SetState(tid, state.activeTarget, 0)
            sm.GetService('state').SetState(tid, state.targeting, 0)
            sm.GetService('state').SetState(tid, state.targeted, 0)
            self.CancelTargetOrder()
            self.ClearTarget(tid)




    def GetTargetedBy(self):
        return self.targetedBy



    def GetTargeting(self):
        return self.targeting



    def ClearTarget(self, tid):
        self.LogInfo('ClearTarget', tid)
        if tid in self.targetsByID:
            t = self.targetsByID[tid]
            del self.targetsByID[tid]
            t.Close()
        if tid in self.targets:
            self.targets.remove(tid)
            self.ArrangeTargets()
        if tid in self.pendingTargets:
            self.pendingTargets.remove(tid)
        if tid == self.caminterest:
            camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
            camera.interest = None
        if not len(self.targets):
            if self.origin is not None and not self.origin.destroyed:
                self.origin.Close()
                self.origin = None
        active = sm.GetService('state').GetExclState(state.activeTarget)
        if active is None and self.targets:
            sm.GetService('state').SetState(self.targets[0], state.activeTarget, 1)



    def BeingTargeted(self, targetID):
        return targetID in self.targeting



    def StartLockTarget(self, tid, autotargeting = 0):
        if tid in self.GetTargets():
            self.ClearTarget(tid)
            sm.GetService('state').SetState(tid, state.targeting, 0)
            sm.GetService('audio').StopSoundLoop('TargetLocking')
        if tid in self.targeting:
            return 
        self.LogInfo('targetMgr: Locking Target for ', tid)
        sm.GetService('audio').StartSoundLoop('TargetLocking')
        sm.GetService('state').SetState(tid, state.targeting, 1)
        self.targeting.append(tid)



    def FailLockTarget(self, tid):
        if tid in self.targeting:
            self.targeting.remove(tid)
        if tid in self.autoTargeting:
            self.autoTargeting.remove(tid)
        sm.GetService('state').SetState(tid, state.targeted, 0)
        sm.GetService('state').SetState(tid, state.targeting, 0)
        sm.GetService('audio').StopSoundLoop('TargetLocking')
        sm.ScatterEvent('OnFailLockTarget', tid)



    def TryLockTarget(self, itemID):
        if itemID in self.GetTargeting() or itemID in self.targetsByID:
            return 
        slimItem = uix.GetBallparkRecord(itemID)
        if not slimItem:
            return 
        if slimItem.groupID in (const.groupPlanet, const.groupMoon, const.groupAsteroidBelt):
            return 
        try:
            self.LockTarget(itemID)
        except Exception as e:
            self.FailLockTarget(itemID)
            sys.exc_clear()



    def IsInTargetingRange(self, itemID):
        if session.shipid is None or eve.session.solarsystemid is None or itemID == session.shipid:
            return False
        if itemID is None or util.IsUniverseCelestial(itemID):
            return 
        shipItem = sm.GetService('godma').GetStateManager().GetItem(eve.session.shipid)
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return False
        otherBall = bp and bp.GetBall(itemID) or None
        if otherBall is None:
            return False
        dist = otherBall and max(0, otherBall.surfaceDist)
        isInRange = dist is not None and shipItem is not None and shipItem and dist < shipItem.maxTargetRange
        return isInRange



    def LockTarget(self, tid, autotargeting = 0):
        self.StartLockTarget(tid, autotargeting)
        try:
            (flag, targetList,) = self.GetDogmaLM().AddTarget(tid)
            if not flag:
                self.OnTargetAdded(tid)
        except UserError as e:
            self.FailLockTarget(tid)
            if autotargeting:
                sys.exc_clear()
                return 
            if e.msg == 'DeniedShipChanged':
                sys.exc_clear()
                return 
            eve.Message(e.msg, e.dict)
            raise 
        self.LogInfo('targetMgr: Locking Target for ', tid, ' done')



    def UnlockTarget(self, tid):
        if tid in self.targets:
            self.GetDogmaLM().RemoveTarget(tid)
            self.RemoveFromTeam(tid)



    def ToggleLockTarget(self, targetID):
        if self.IsTarget(targetID):
            self.UnlockTarget(targetID)
        else:
            self.TryLockTarget(targetID)



    def LockTargetPassively(self, tid, smb):
        self.StartLockTarget(tid, 0)
        try:
            smb.OnStateChange(tid, state.activeTarget, True)
        except UserError as e:
            self.FailLockTarget(tid)
            if e.msg == 'DeniedShipChanged':
                sys.exc_clear()
                return 
            raise 
        self.LogInfo('targetMgr: PassiveLocking Target for ', tid, ' done')



    def ClearTargets(self):
        self.GetDogmaLM().ClearTargets()



    def GetActiveTargetID(self):
        selected = sm.GetService('state').GetExclState(state.activeTarget)
        if selected and selected in self.targets:
            return selected



    def GetTargets(self):
        return self.targets



    def IsTarget(self, targetID):
        return targetID in self.targets



    def SetAsInterest(self, id):
        if id is None:
            uthread.new(self.ResetInterest)
            return 
        self.caminterest = id
        sm.StartService('camera').SetCameraInterest(id)



    def ResetInterest(self):
        self.caminterest = None
        blue.pyos.synchro.Sleep(1000)
        if self.caminterest is None:
            sm.StartService('camera').SetCameraInterest(None)




