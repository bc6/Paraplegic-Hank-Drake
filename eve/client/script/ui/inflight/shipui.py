import sys
import blue
import uthread
import uix
import uiutil
import mathUtil
import xtriui
import form
import trinity
import util
import base
import math
import log
import lg
import destiny
import uicls
import uiconst
ICONSIZE = 32
CELLCOLOR = (0.9375, 0.3515625, 0.1953125)
groups = ('hardpoints', 'systems', 'structure')

class ShipUI(uicls.LayerCore):
    __guid__ = 'form.ShipUI'
    __notifyevents__ = ['OnShipScanCompleted',
     'OnJamStart',
     'OnJamEnd',
     'OnCargoScanComplete',
     'ProcessShipEffect',
     'DoBallRemove',
     'DoBallClear',
     'OnAutoPilotOn',
     'OnAutoPilotOff',
     'OnAttributes',
     'ProcessRookieStateChange',
     'OnSetDevice',
     'OnMapShortcut',
     'OnRestoreDefaultShortcuts',
     'OnTacticalOverlayChange',
     'OnAssumeStructureControl',
     'OnRelinquishStructureControl',
     'OnWeaponGroupsChanged',
     'OnRefreshModuleBanks',
     'OnUIColorsChanged']

    def OnUIColorsChanged(self, *args):
        if self.sr.wnd:
            mainShape = uiutil.GetChild(self.sr.wnd, 'shipuiMainShape')
            (color, bgColor, comp, compsub,) = sm.GetService('window').GetWindowColors()
            (r, g, b, a,) = color
            mainShape.SetRGB(r, g, b)



    def OnSetDevice(self):
        self.UpdatePosition()



    def ResetSelf(self):
        self.powerCells = None
        self.sr.wnd = None
        self.sr.speedtimer = None
        self.sr.capacitortimer = None
        self.sr.cargotimer = None
        self.sr.modeTimer = None
        self.sr.gaugetimer = None
        self.sr.gaugeReadout = None
        self.sr.selectedcateg = 0
        self.sr.pendingreloads = []
        self.sr.reloadsByID = {}
        self.sr.rampTimers = {}
        self.sr.main = None
        self.sr.powercore = None
        self.sr.speedNeedle = None
        self.sr.speedReadout = None
        self.sr.autopilotBtn = None
        self.sr.tacticalBtn = None
        self.sr.powerblink = None
        self.sr.speed_ro = None
        self.sr.shield_ro = None
        self.sr.armor_ro = None
        self.sr.powercore_ro = None
        self.sr.structure_ro = None
        self.sr.module_ro = None
        self.sr.currentModeHeader = None
        self.sr.hudButtons = None
        self.myHarpointFlags = []
        self.capacity = None
        self.shieldcapacity = None
        self.lastsetcapacitor = None
        self.lastsetshield = None
        self.lastsetarmor = None
        self.wantedspeed = None
        self.capacitorDone = 0
        self.sr.modules = {}
        self.ball = None
        self.initing = None
        self.initedshipid = None
        self.speedInited = 0
        self.updatingcargo = 0
        self.updatingspeed = 0
        self.slotsInited = 0
        self.jammers = {}
        self.speedupdatetimer = None
        self.genericupdatetimer = None
        self.assumingcontrol = False
        self.assumingdelay = None
        self.checkingoverloadrackstate = 0
        self.totalSlaves = 0
        self.timerNames = {'propulsion': mls.UI_INFLIGHT_SCRAMBLING,
         'electronic': mls.UI_INFLIGHT_JAMMING,
         'unknown': mls.UI_INFLIGHT_MISCELLANEOUS}



    def CheckPendingReloads(self):
        if self.sr.pendingreloads:
            rl = self.sr.pendingreloads[0]
            while rl in self.sr.pendingreloads:
                self.sr.pendingreloads.remove(rl)

            module = self.GetModule(rl)
            if module:
                module.AutoReload()



    def CheckSession(self, change):
        if sm.GetService('autoPilot').GetState():
            self.OnAutoPilotOn()
        else:
            self.OnAutoPilotOff()



    def UpdatePosition(self):
        self.sr.wnd.height = 195
        self.sr.wnd.width = uicore.desktop.width
        wndLeft = settings.user.windows.Get('shipuialignleft', 0)
        (maxRight, minLeft,) = self.GetShipuiOffsetMinMax()
        if wndLeft > maxRight or wndLeft < minLeft:
            settings.user.windows.Set('shipuialignleft', 0)
            wndLeft = 0
        self.sr.wnd.left = wndLeft
        self.sr.wnd.align = uiconst.ABSOLUTE
        if not settings.user.ui.Get('shipuialigntop', 0):
            self.sr.wnd.top = uicore.desktop.height - self.sr.wnd.height
        else:
            self.sr.wnd.top = 0
        if self.sr.gaugeReadout:
            self.sr.gaugeReadout.top = self.GetGaugeTop()
        if settings.user.ui.Get('shipuialigntop', 0):
            self.sr.indicationContainer.top = 200
        else:
            self.sr.indicationContainer.top = -50
        self.sr.timers.top = uicore.desktop.height - self.sr.timers.height - 205
        self.sr.timers.left = (uicore.desktop.width - self.sr.timers.width) / 2



    def GetGaugeTop(self, *args):
        if settings.user.ui.Get('shipuialigntop', 0):
            return 20
        else:
            return 200



    def GetShipLayerAbsolutes(self):
        d = uicore.desktop
        wnd = uicore.layer.shipui
        if wnd and not wnd.state == uiconst.UI_HIDDEN:
            (pl, pt, pw, ph,) = wnd.GetAbsolute()
        else:
            (pl, pt, pw, ph,) = d.GetAbsolute()
        return (wnd,
         pl,
         pt,
         pw,
         ph)



    def GetShipUI(self, obj):
        return self.sr.wnd



    def OnShipMouseDown(self, wnd, btn, *args):
        if btn != 0:
            return 
        self.dragging = True
        wnd = self.GetShipUI(wnd)
        if not wnd:
            return 
        (l, t, w, h,) = wnd.GetAbsolute()
        self.grab = [uicore.uilib.x - l, uicore.uilib.y - t]
        uthread.new(self.BeginDrag, wnd)



    def GetShipuiOffsetMinMax(self, *args):
        maxRight = uicore.desktop.width / 2 - self.sr.slotsContainer.width / 2
        minLeft = -(uicore.desktop.width / 2 - 180)
        return (maxRight, minLeft)



    def OnShipMouseUp(self, wnd, btn, *args):
        if btn != 0:
            return 
        wnd = self.GetShipUI(wnd)
        if wnd:
            wndLeft = settings.user.windows.Set('shipuialignleft', wnd.left)
        sm.StartService('ui').ForceCursorUpdate()
        self.dragging = False



    def BeginDrag(self, wnd):
        wnd = self.GetShipUI(wnd)
        while not wnd.destroyed and getattr(self, 'dragging', 0):
            uicore.uilib.SetCursor(uiconst.UICURSOR_DIVIDERADJUST)
            (maxRight, minLeft,) = self.GetShipuiOffsetMinMax()
            grabLocation = uicore.uilib.x - self.grab[0]
            wnd.left = max(minLeft, min(maxRight, grabLocation))
            blue.pyos.synchro.Sleep(1)




    def OnOpenView(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None or eve.session.shipid is None:
            return 
        ball = bp.GetBall(eve.session.shipid)
        self.ResetSelf()
        self.state = uiconst.UI_HIDDEN
        self.sr.wnd = ShipUIContainer(parent=self)
        timers = uicls.Container(name='timers', parent=self, width=120, height=450, align=uiconst.ABSOLUTE)
        self.sr.timers = timers
        self.sr.mainContainer = uiutil.GetChild(self.sr.wnd, 'mainContainer')
        self.sr.subContainer = uiutil.GetChild(self.sr.wnd, 'subContainer')
        self.sr.slotsContainer = uiutil.GetChild(self.sr.wnd, 'slotsContainer')
        if settings.user.ui.Get('shipuialigntop', 0):
            top = 200
        else:
            top = -50
        self.sr.indicationContainer = uicls.Container(parent=self.sr.wnd, align=uiconst.CENTERTOP, pos=(0,
         top,
         400,
         50))
        showReadout = settings.user.ui.Get('showReadout', 0)
        if showReadout:
            self.InitGaugeReadout()
        self.sr.powercore = uiutil.GetChild(self.sr.wnd, 'powercore')
        self.sr.powercore.OnMouseDown = (self.OnShipMouseDown, self.sr.powercore)
        self.sr.powercore.OnMouseUp = (self.OnShipMouseUp, self.sr.powercore)
        self.sr.powercore.GetMenu = self.GetMenu
        mExpanded = settings.user.ui.Get('modulesExpanded', 1)
        self.sr.expandbtnleft = uiutil.GetChild(self.sr.wnd, 'expandBtnLeft')
        self.sr.expandbtnleft.OnClick = (self.ClickExpand, self.sr.expandbtnleft)
        self.sr.expandbtnleft.OnMouseDown = (self.OnExpandDown, self.sr.expandbtnleft)
        self.sr.expandbtnleft.OnMouseUp = (self.OnExpandUp, self.sr.expandbtnleft)
        self.sr.expandbtnleft.side = -1
        self.sr.expandbtnleft.hint = [mls.UI_INFLIGHT_SHOWBUTTONS, mls.UI_INFLIGHT_HIDEBUTTONS][mExpanded]
        self.sr.expandbtnright = uiutil.GetChild(self.sr.wnd, 'expandBtnRight')
        self.sr.expandbtnright.OnClick = (self.ClickExpand, self.sr.expandbtnright)
        self.sr.expandbtnright.side = 1
        self.sr.expandbtnright.OnMouseDown = (self.OnExpandDown, self.sr.expandbtnright)
        self.sr.expandbtnright.OnMouseUp = (self.OnExpandUp, self.sr.expandbtnright)
        self.sr.expandbtnright.hint = [mls.UI_INFLIGHT_SHOWMODULES, mls.UI_INFLIGHT_HIDEMODULES][mExpanded]
        options = uiutil.GetChild(self.sr.wnd, 'optionsBtn')
        options.SetAlpha(0.8)
        options.OnMouseEnter = self.OptionsBtnMouseEnter
        options.OnMouseExit = self.OptionsBtnMouseExit
        options.GetMenu = self.GetOptionMenu
        options.expandOnLeft = 1
        options.hint = mls.UI_GENERIC_OPTIONS
        self.options = options
        underMain = uiutil.GetChild(self.sr.wnd, 'underMain')
        for (typeName, deg,) in [('low', -22.5), ('med', -90.0), ('hi', -157.5)]:
            miniGauge = uicls.Transform(parent=underMain, name='%s_miniGauge' % typeName, pos=(-1, 0, 83, 12), align=uiconst.CENTER, rotation=mathUtil.DegToRad(deg), idx=0)
            needle = uicls.Sprite(parent=miniGauge, name='needle', pos=(0, 0, 12, 12), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/heatGaugeNeedle.png')
            self.sr.Set('%sHeatGauge' % typeName, miniGauge)
            underlay = uiutil.FindChild(self.sr.wnd, 'heat%sUnderlay' % typeName.capitalize())
            if underlay:
                self.sr.Set('heat%sUnderlay' % typeName.capitalize(), underlay)

        self.sr.heatPick = uiutil.GetChild(self.sr.wnd, 'heatPick')
        self.structureGauge = uicls.Sprite(parent=underMain, pos=(0, 0, 148, 148), texturePath='res:/UI/Texture/classes/ShipUI/gauge3.png', align=uiconst.CENTER, spriteEffect=trinity.TR2_SFX_MODULATE, shadowOffset=(0, 1), pickRadius=54, name='structureGauge', glowColor=(0.25, 0.25, 0.25, 1.0), glowExpand=1.0)
        self.structureGauge.SetSecondaryTexturePath('res:/UI/Texture/classes/ShipUI/gaugeFill.png')
        self.structureGauge.textureSecondary.useTransform = True
        self.structureGauge.textureSecondary.rotation = 1.0
        self.armorGauge = uicls.Sprite(parent=underMain, pos=(0, 0, 148, 148), texturePath='res:/UI/Texture/classes/ShipUI/gauge2.png', align=uiconst.CENTER, spriteEffect=trinity.TR2_SFX_MODULATE, shadowOffset=(0, 1), pickRadius=64, name='armorGauge', glowColor=(0.25, 0.25, 0.25, 1.0), glowExpand=1.0)
        self.armorGauge.SetSecondaryTexturePath('res:/UI/Texture/classes/ShipUI/gaugeFill.png')
        self.armorGauge.textureSecondary.useTransform = True
        self.armorGauge.textureSecondary.rotation = 1.0
        self.shieldGauge = uicls.Sprite(parent=underMain, pos=(0, 0, 148, 148), texturePath='res:/UI/Texture/classes/ShipUI/gauge1.png', align=uiconst.CENTER, spriteEffect=trinity.TR2_SFX_MODULATE, shadowOffset=(0, 1), pickRadius=74, name='shieldGauge', glowColor=(0.25, 0.25, 0.25, 1.0), glowExpand=1.0)
        self.shieldGauge.SetSecondaryTexturePath('res:/UI/Texture/classes/ShipUI/gaugeFill.png')
        self.shieldGauge.textureSecondary.useTransform = True
        self.shieldGauge.textureSecondary.rotation = 1.0
        self.sr.wnd.state = uiconst.UI_PICKCHILDREN
        self.cookie = sm.GetService('inv').Register(self)
        sm.RegisterNotify(self)
        self.UpdatePosition()
        if ball is not None:
            self.Init(ball)
        self.DoInit()
        self.UpdatePosition()



    def OptionsBtnMouseEnter(self, *args):
        self.options.SetAlpha(1.0)



    def OptionsBtnMouseExit(self, *args):
        self.options.SetAlpha(0.8)



    def DoInit(self):
        self.InitButtons()
        self.SetButtonState()
        self.CheckExpandBtns()
        self.CheckControl()



    def CheckControl(self):
        control = sm.GetService('pwn').GetCurrentControl()
        if control:
            self.OnAssumeStructureControl()



    def SetButtonState(self):
        self.sr.slotsContainer.state = [uiconst.UI_HIDDEN, uiconst.UI_PICKCHILDREN][settings.user.ui.Get('modulesExpanded', 1)]
        self.sr.hudButtons.state = [uiconst.UI_HIDDEN, uiconst.UI_PICKCHILDREN][settings.user.ui.Get('hudButtonsExpanded', 1)]



    def InitGaugeReadout(self):
        self.sr.gaugeReadout = uicls.Container(name='gaugeReadout', parent=self.sr.mainContainer, left=self.sr.mainContainer.width / 2 + 54, top=self.GetGaugeTop(), width=200, align=uiconst.BOTTOMLEFT)
        for (left, group,) in [(20, ('shield', 'armor', 'structure'))]:
            top = 0
            for refName in group:
                t = uicls.Label(text='Xg', parent=self.sr.gaugeReadout, left=left, top=top, state=uiconst.UI_DISABLED, fontsize=9, linespace=9, letterspace=1, uppercase=1)
                self.sr.gaugeReadout.sr.Set(refName, t)
                left -= 10
                top += t.textheight
                t.text = ''


        self.sr.gaugeReadout.height = top



    def OnMapShortcut(self, *blah):
        self.RefreshShortcuts()



    def OnRestoreDefaultShortcuts(self):
        self.RefreshShortcuts()



    def OnAssumeStructureControl(self, *args):
        now = blue.os.GetTime()
        self.assumingdelay = now
        uthread.new(self.DelayedOnAssumeStructureControl, now)



    def DelayedOnAssumeStructureControl(self, issueTime):
        blue.pyos.synchro.Sleep(250)
        if self.assumingdelay is None:
            return 
        issuedAt = self.assumingdelay
        if issuedAt != issueTime:
            return 
        self.assumingdelay = None
        self.ShowStructureControl()



    def ShowStructureControl(self, *args):
        control = sm.GetService('pwn').GetCurrentControl()
        if control:
            for each in uicore.layer.shipui.children[0].children:
                if each.name in ('hudbuttons', 'slotsContainer'):
                    continue
                each.state = uiconst.UI_HIDDEN

            self.assumingcontrol = True
            self.initing = 1
            self.InitSlots()
            settings.user.ui.Set('modulesExpanded', 1)
            settings.user.ui.Set('hudButtonsExpanded', 1)
            self.InitButtons()
            self.initing = 0
            uicore.effect.MorphUI(self.sr.slotsContainer, 'left', -80, 500.0)
            uicore.effect.MorphUI(self.sr.hudButtons, 'left', 80, 500.0)



    def OnRelinquishStructureControl(self, *args):
        control = sm.GetService('pwn').GetCurrentControl()
        if not control:
            for each in uicore.layer.shipui.children[0].children:
                each.state = uiconst.UI_PICKCHILDREN

            self.assumingcontrol = False
            uicore.effect.MorphUI(self.sr.slotsContainer, 'left', 0, 500.0)
            uicore.effect.MorphUI(self.sr.hudButtons, 'left', 0, 500.0)
        self.initing = 1
        self.InitSlots()
        self.DoInit()
        self.initing = 0



    def OnWeaponGroupsChanged(self):
        if not self or self.destroyed:
            return 
        uthread.new(self.InitSlots)



    def OnRefreshModuleBanks(self):
        if not self or self.destroyed:
            return 
        uthread.new(self.InitSlots)



    def RefreshShortcuts(self):
        for ((r, i,), slot,) in self.sr.slotsByOrder.iteritems():
            hiMedLo = ('High', 'Medium', 'Low')[r]
            slotno = i + 1
            txt = uicore.cmd.GetShortcutStringByFuncName('CmdActivate%sPowerSlot%i' % (hiMedLo, slotno))
            if not txt:
                txt = '_'
            slot.sr.shortcutHint.text = '<center>' + txt




    def BlinkButton(self, key):
        btn = self.sr.Get(key.lower(), None) or self.sr.Get('%sBtn' % key.lower(), None)
        if not btn:
            for each in self.sr.modules:
                if getattr(each, 'locationFlag', None) == util.LookupConstValue('flag%s' % key, 'no'):
                    btn = each
                    break

        if not btn:
            return 
        if hasattr(btn.sr, 'icon'):
            sm.GetService('ui').BlinkSpriteA(btn.sr.icon, 1.0, 1000, None, passColor=0)
        else:
            sm.GetService('ui').BlinkSpriteA(btn, 1.0, 1000, None, passColor=0)



    def GetOptionMenu(self):
        m = []
        if not eve.rookieState:
            showPassive = settings.user.ui.Get('showPassiveModules', 1)
            m += [([mls.UI_INFLIGHT_SHOWPASSIVEMODULES, mls.UI_INFLIGHT_HIDEPASSIVEMODULES][showPassive], self.ToggleShowPassive)]
            showEmpty = settings.user.ui.Get('showEmptySlots', 0)
            m += [([mls.UI_INFLIGHT_SHOWEMPTYSLOTS, mls.UI_INFLIGHT_HIDEEMPTYSLOTS][showEmpty], self.ToggleShowEmpty)]
            lockModules = settings.user.ui.Get('lockModules', 0)
            m += [([mls.UI_INFLIGHT_LOCKMODULES, mls.UI_INFLIGHT_UNLOCKMODULES][lockModules], self.ToggleLockModules)]
            lockOverload = settings.user.ui.Get('lockOverload', 0)
            m += [([mls.UI_CMD_LOCKOVERLOADSTATE, mls.UI_CMD_UNLOCKOVERLOADSTATUS][lockOverload], self.ToggleOverloadLock)]
        showReadout = settings.user.ui.Get('showReadout', 0)
        readoutType = settings.user.ui.Get('readoutType', 1)
        m += [([mls.UI_INFLIGHT_SHOWREADOUT, mls.UI_INFLIGHT_HIDEREADOUT][showReadout], self.ToggleReadout)]
        m += [([mls.UI_INFLIGHT_PERCENTAGEREADOUT, mls.UI_INFLIGHT_ABSOLUTEREADOUT][readoutType], self.ToggleReadoutType)]
        showZoomBtns = settings.user.ui.Get('showZoomBtns', 0)
        m += [([mls.UI_INFLIGHT_SHOWZOOMBTNS, mls.UI_INFLIGHT_HIDEZOOMBTNS][showZoomBtns], self.ToggleShowZoomBtns)]
        showCycleTimer = settings.user.ui.Get('showCycleTimer', 1)
        if showCycleTimer:
            cycleText = mls.UI_SHARED_ACTIVATIONTIMEROFF
        else:
            cycleText = mls.UI_SHARED_ACTIVATIONTIMERON
        m += [(cycleText, self.ToggleCycleTimer)]
        m += [None]
        m += [(mls.UI_GENERIC_NOTIFYSETTINGS, self.ShowNotifySettingsWindow)]
        m += [None]
        alignTop = settings.user.ui.Get('shipuialigntop', 0)
        m += [([mls.UI_CMD_ALIGNTOP, mls.UI_CMD_ALIGNBOTTOM][alignTop], self.ToggleAlign)]
        return m



    def ShowNotifySettingsWindow(self):
        window = sm.GetService('window').GetWindow('NotifySettingsWindow', create=1)
        window.Maximize()



    def ToggleAlign(self):
        settings.user.ui.Set('shipuialigntop', not settings.user.ui.Get('shipuialigntop', 0))
        self.UpdatePosition()



    def ToggleReadout(self):
        current = not settings.user.ui.Get('showReadout', 0)
        settings.user.ui.Set('showReadout', current)
        if self.sr.gaugeReadout is None:
            self.InitGaugeReadout()
        self.sr.gaugeReadout.state = [uiconst.UI_HIDDEN, uiconst.UI_PICKCHILDREN][current]



    def ToggleReadoutType(self):
        current = settings.user.ui.Get('readoutType', 1)
        settings.user.ui.Set('readoutType', not current)



    def ToggleCycleTimer(self):
        current = settings.user.ui.Get('showCycleTimer', 1)
        settings.user.ui.Set('showCycleTimer', not current)
        self.InitSlots()



    def ToggleShowPassive(self):
        settings.user.ui.Set('showPassiveModules', not settings.user.ui.Get('showPassiveModules', 1))
        self.InitSlots()



    def ToggleShowZoomBtns(self):
        settings.user.ui.Set('showZoomBtns', not settings.user.ui.Get('showZoomBtns', 0))
        self.InitButtons()



    def ToggleShowEmpty(self):
        settings.user.ui.Set('showEmptySlots', not settings.user.ui.Get('showEmptySlots', 0))
        self.InitSlots()



    def ToggleLockModules(self):
        settings.user.ui.Set('lockModules', not settings.user.ui.Get('lockModules', 0))
        self.CheckGroupAllButton()



    def ToggleOverloadLock(self):
        settings.user.ui.Set('lockOverload', not settings.user.ui.Get('lockOverload', 0))



    def ShowTimer(self, timerID, startTime, duration, label):
        check = self.GetTimer(timerID)
        if check:
            if check.endTime <= startTime + duration:
                check.Close()
            else:
                return 
        timer = uicls.Container(name='%s' % timerID, parent=self.sr.timers, height=17, align=uiconst.TOBOTTOM, top=30)
        timer.endTime = startTime + duration
        uicls.Label(text=label, parent=timer, left=124, top=-1, fontsize=9, letterspace=2, linespace=8, color=(1.0, 1.0, 1.0, 0.5), uppercase=1, state=uiconst.UI_NORMAL)
        fpar = uicls.Container(parent=timer, align=uiconst.TOTOP, height=13)
        uicls.Frame(parent=fpar, color=(1.0, 1.0, 1.0, 0.5))
        t = uicls.Label(text='', parent=fpar, left=5, top=1, fontsize=9, letterspace=1, uppercase=1, state=uiconst.UI_NORMAL)
        p = uicls.Fill(parent=fpar, align=uiconst.RELATIVE, width=118, height=11, left=1, top=1, color=(1.0, 1.0, 1.0, 0.25))
        duration = float(duration)
        totalTime = float(startTime + duration * 10000 - blue.os.GetTime()) / SEC
        while 1 and not timer.destroyed:
            now = blue.os.GetTime()
            dt = blue.os.TimeDiffInMs(startTime, now)
            timeLeft = (duration - dt) / 1000.0
            timer.timeLeft = timeLeft
            if timer.destroyed or dt > duration:
                t.text = mls.UI_GENERIC_DONE
                p.width = 0
                break
            t.text = '%.3f %s' % (timeLeft, uix.Plural(timeLeft, 'UI_GENERIC_SECONDSHORT'))
            p.width = max(0, min(118, int(118 * (timeLeft / totalTime))))
            blue.pyos.synchro.Yield()

        if not timer.destroyed:
            blue.pyos.synchro.Sleep(250)
            if not t.destroyed:
                t.text = ''
            blue.pyos.synchro.Sleep(250)
            if not t.destroyed:
                t.text = mls.UI_GENERIC_DONE
            blue.pyos.synchro.Sleep(250)
            if not t.destroyed:
                t.text = ''
            blue.pyos.synchro.Sleep(250)
            if not t.destroyed:
                t.text = mls.UI_GENERIC_DONE
            blue.pyos.synchro.Sleep(250)
            if not t.destroyed:
                t.text = ''
            if not timer.destroyed:
                timer.Close()



    def KillTimer(self, timerID):
        timer = self.GetTimer(timerID)
        if timer:
            timer.Close()



    def GetTimer(self, timerID):
        for each in self.sr.timers.children:
            if each.name == '%s' % timerID:
                return each




    def OnExpandDown(self, btn, *args):
        pass



    def OnExpandUp(self, btn, *args):
        pass



    def ClickExpand(self, btn, *args):
        if btn.side == -1:
            if self.sr.hudButtons:
                self.sr.hudButtons.state = [uiconst.UI_PICKCHILDREN, uiconst.UI_HIDDEN][(self.sr.hudButtons.state == uiconst.UI_PICKCHILDREN)]
            settings.user.ui.Set('hudButtonsExpanded', self.sr.hudButtons.state == uiconst.UI_PICKCHILDREN)
        elif self.sr.slotsContainer:
            self.sr.slotsContainer.state = [uiconst.UI_PICKCHILDREN, uiconst.UI_HIDDEN][(self.sr.slotsContainer.state == uiconst.UI_PICKCHILDREN)]
        settings.user.ui.Set('modulesExpanded', self.sr.slotsContainer.state == uiconst.UI_PICKCHILDREN)
        sm.GetService('ui').StopBlink(btn)
        self.CheckExpandBtns()



    def CheckExpandBtns(self):
        if self.sr.Get('expandbtnright', None) and not self.sr.expandbtnright.destroyed:
            on = settings.user.ui.Get('modulesExpanded', 1)
            if on:
                self.sr.expandbtnright.LoadTexture('res:/UI/Texture/classes/ShipUI/expandBtnLeft.png')
            else:
                self.sr.expandbtnright.LoadTexture('res:/UI/Texture/classes/ShipUI/expandBtnRight.png')
            self.sr.expandbtnright.hint = [mls.UI_INFLIGHT_SHOWMODULES, mls.UI_INFLIGHT_HIDEMODULES][on]
        else:
            return 
        if self.sr.Get('expandbtnleft', None):
            on = settings.user.ui.Get('hudButtonsExpanded', 1)
            if on:
                self.sr.expandbtnleft.LoadTexture('res:/UI/Texture/classes/ShipUI/expandBtnRight.png')
            else:
                self.sr.expandbtnleft.LoadTexture('res:/UI/Texture/classes/ShipUI/expandBtnLeft.png')
            self.sr.expandbtnleft.hint = [mls.UI_INFLIGHT_SHOWBUTTONS, mls.UI_INFLIGHT_HIDEBUTTONS][on]



    def InitButtons(self):
        par = uiutil.FindChild(self.sr.wnd, 'hudbuttons')
        if not par:
            par = uicls.Container(name='hudbuttons', parent=self.sr.slotsContainer.parent, align=uiconst.CENTER, pos=(0, 0, 512, 256))
        par.Flush()
        grid = [[-1.0, -1.0], [-1.5, 0.0], [-1.0, 1.0]]
        BTNSIZE = 36
        w = par.width
        h = par.height
        centerX = (w - BTNSIZE) / 2
        centerY = (h - BTNSIZE) / 2
        ystep = int(ICONSIZE * 1.06)
        xstep = int(ICONSIZE * 1.3)
        step = 20
        buttons = [(mls.UI_GENERIC_CARGO,
          'inFlightCargoBtn',
          self.Cargo,
          'ui_44_32_10',
          100,
          -1.0,
          'OpenCargoHoldOfActiveShip'),
         (mls.UI_CMD_RESETCAMERA,
          'inFlightResetCameaBtn',
          self.ResetCamera,
          'ui_44_32_46',
          128,
          0.5,
          ''),
         (mls.UI_GENERIC_SCANNER,
          'inFlightScannerBtn',
          self.Scanner,
          'ui_44_32_41',
          100,
          0.0,
          'OpenScanner'),
         (mls.UI_GENERIC_TACTICAL,
          'inFlightTacticalBtn',
          self.Tactical,
          'ui_44_32_42',
          128,
          -0.5,
          'CmdToggleTacticalOverlay'),
         (mls.UI_GENERIC_AUTOPILOT,
          'inFlightAutopilotBtn',
          self.Autopilot,
          'ui_44_32_12',
          100,
          1.0,
          'CmdToggleAutopilot')]
        showZoomBtns = settings.user.ui.Get('showZoomBtns', 0)
        if showZoomBtns:
            buttons += [(mls.UI_CMD_ZOOMIN,
              'inFlightZoomInBtn',
              self.ZoomIn,
              '44_43',
              128,
              1.5,
              'CmdZoomIn'), (mls.UI_CMD_ZOOMOUT,
              'inFlightZoomOutBtn',
              self.ZoomOut,
              '44_44',
              100,
              2.0,
              'CmdZoomOut')]
        for (btnName, guiID, func, iconNum, rad, y, cmdName,) in buttons:
            if eve.rookieState and eve.rookieState < sm.GetService('tutorial').GetShipuiRookieFilter(btnName):
                continue
            slot = LeftSideButton(parent=par, iconNum=iconNum, btnName=btnName, pos=(int(centerX - rad),
             int(centerY + y * 32) - showZoomBtns * 16,
             BTNSIZE,
             BTNSIZE), name=guiID, func=func, cmdName=cmdName)
            self.sr.Set(btnName.replace(' ', '').lower(), slot)
            if btnName == mls.UI_GENERIC_TACTICAL:
                self.sr.tacticalBtn = slot
                tActive = settings.user.overview.Get('viewTactical', 0)
                uiutil.GetChild(self.sr.tacticalBtn, 'busy').state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][tActive]
                self.sr.tacticalBtn.hint = [mls.UI_CMD_SHOWTACTICALOVERLEY, mls.UI_CMD_HIDETACTICALOVERLEY][tActive]
            elif btnName == mls.UI_GENERIC_AUTOPILOT:
                self.sr.autopilotBtn = slot
                apActive = sm.GetService('autoPilot').GetState()
                uiutil.GetChild(self.sr.autopilotBtn, 'busy').state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][apActive]
                self.sr.autopilotBtn.hint = [mls.UI_CMD_ACTIVATEAUTOPILOT, mls.UI_CMD_DEACTIVATEAUTOPILOT][apActive]
            elif btnName == mls.UI_GENERIC_CARGO:
                slot.OnDropData = self.DropInCargo

        self.sr.hudButtons = par



    def _GetShortcutForCommand(self, cmdName):
        if cmdName:
            shortcut = uicore.cmd.GetShortcutStringByFuncName(cmdName)
            if shortcut:
                return ' [%s]' % shortcut
        return ''



    def DropInCargo(self, dragObj, nodes):
        bms = []
        inv = []
        for node in nodes:
            if node.Get('__guid__', None) == 'listentry.PlaceEntry':
                bms.append(node)
            elif node.rec and cfg.IsShipFittingFlag(node.rec.flagID):
                dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
                if node.rec.categoryID == const.categoryCharge:
                    dogmaLocation.UnloadChargeToContainer(session.shipid, node.itemID, (session.shipid,), const.flagCargo)
                else:
                    dogmaLocation.UnloadModuleToContainer(session.shipid, node.itemID, (session.shipid,), const.flagCargo)
            elif node.Get('__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem'):
                inv.append(node)

        if len(inv) > 0 and sm.GetService('consider').ConfirmTakeFromContainer(inv[0].rec.locationID):
            if sm.GetService('consider').ConfirmTakeIllicitGoods([ i.item for i in inv ]):
                if len(inv) > 1:
                    eve.GetInventoryFromId(eve.session.shipid).MultiAdd([ node.itemID for node in inv ], inv[0].rec.locationID, flag=const.flagCargo)
                else:
                    eve.GetInventoryFromId(eve.session.shipid).Add(inv[0].itemID, inv[0].rec.locationID, flag=const.flagCargo)
        if len(bms) > 0:
            uthread.new(self.AddBookmarks, [ node.bm.bookmarkID for node in bms ])



    def AddBookmarks(self, bookmarkIDs):
        isMove = not uicore.uilib.Key(uiconst.VK_SHIFT)
        eve.GetInventoryFromId(eve.session.shipid).AddBookmarks(bookmarkIDs, const.flagCargo, isMove)



    def Tactical(self, *args):
        sm.GetService('tactical').ToggleOnOff()
        tActive = settings.user.overview.Get('viewTactical', 0)
        uiutil.GetChild(self.sr.tacticalBtn, 'busy').state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][tActive]
        self.sr.tacticalBtn.hint = [mls.UI_CMD_SHOWTACTICALOVERLEY, mls.UI_CMD_HIDETACTICALOVERLEY][tActive]
        self.sr.tacticalBtn.hint += self._GetShortcutForCommand(self.sr.tacticalBtn.cmdName)



    def Autopilot(self, *args):
        self.AutoPilotOnOff(not sm.GetService('autoPilot').GetState())



    def ZoomIn(self, *args):
        uicore.cmd.CmdZoomIn()



    def ZoomOut(self, *args):
        uicore.cmd.CmdZoomOut()



    def ResetCamera(self, *args):
        sm.GetService('camera').ResetCamera()



    def Cargo(self, *args):
        self.ToggleCargo()



    def ToggleCargo(self):
        if eve.session.shipid:
            wnd = sm.GetService('window').GetWindow('shipCargo_%s' % eve.session.shipid)
            if wnd:
                if wnd.IsMinimized():
                    wnd.Maximize()
                elif wnd.IsCollapsed():
                    wnd.Expand()
                else:
                    wnd.CloseX()
            else:
                shipName = cfg.evelocations.Get(eve.session.shipid).name
                sm.GetService('cmd').OpenCargoHoldOfActiveShip()



    def Scanner(self, *args):
        self.ToggleScanner()



    def ToggleScanner(self):
        if eve.session.solarsystemid:
            wnd = sm.GetService('window').GetWindow('scanner', showIfInStack=False)
            if wnd is not None and not wnd.destroyed:
                if wnd.IsMinimized():
                    wnd.Maximize()
                elif wnd.IsCollapsed():
                    wnd.Expand()
                else:
                    wnd.CloseX()
            else:
                sm.GetService('window').GetWindow('scanner', create=1, decoClass=form.Scanner)



    def InitStructureSlots(self):
        currentControl = sm.GetService('pwn').GetCurrentControl()
        shipmodules = []
        charges = {}
        if currentControl:
            for (k, v,) in currentControl.iteritems():
                shipmodules.append(sm.services['godma'].GetItem(k))

        xstep = int(ICONSIZE * 2.0)
        ystep = int(ICONSIZE * 1.35)
        vgridrange = 1
        hgridrange = 5
        grid = [[1.0, 0.1]]
        myOrder = [0,
         1,
         2,
         3,
         4]
        for (i, moduleInfo,) in enumerate(shipmodules):
            if moduleInfo is None:
                continue
            myOrder[i] = moduleInfo.itemID
            if currentControl.has_key(moduleInfo.itemID):
                item = sm.services['godma'].GetItem(moduleInfo.itemID)
                if item.groupID == const.groupMobileLaserSentry and len(item.modules):
                    charges[moduleInfo.itemID] = item.modules[0]
                elif len(item.sublocations):
                    charges[moduleInfo.itemID] = item.sublocations[0]

        self.InitDrawSlots(xstep, ystep, vgridrange, hgridrange, grid, myOrder, slotType='structure')
        for moduleInfo in shipmodules:
            if moduleInfo:
                self._FitStructureSlot(moduleInfo, charges)

        self.CheckButtonVisibility(3, ['hiSlots'], 5, myOrder)
        self.slotsInited = 1



    def InitDrawSlots(self, xstep, ystep, vgridrange, hgridrange, grid, myOrder, slotType = None):
        w = self.sr.slotsContainer.width
        h = self.sr.slotsContainer.height
        centerX = (w - 64) / 2
        centerY = (h - 64) / 2
        for r in xrange(vgridrange):
            (x, y,) = grid[r]
            for i in xrange(hgridrange):
                slotFlag = myOrder[(r * hgridrange + i)]
                if slotType == 'shipslot':
                    slot = ShipSlot(parent=self.sr.slotsContainer, pos=(0,
                     int(centerY + ystep * y),
                     64,
                     64), name='slot', state=uiconst.UI_HIDDEN, align=uiconst.TOPLEFT, idx=0)
                else:
                    slot = uicls.Container(name='defenceslot', parent=self.sr.slotsContainer, width=64, height=128 + 60, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, top=166)
                slot.left = int(centerX + (x + i) * xstep) + 50
                slot.sr.module = None
                slot.sr.slotFlag = slotFlag
                slot.sr.slotPos = (r, i)
                self.sr.slotsByFlag[slotFlag] = slot
                self.sr.slotsByOrder[(r, i)] = slot
                slot.sr.shortcutHint = uicls.Label(text='<center>-', parent=slot, width=64, autowidth=False, color=(1.0, 1.0, 1.0, 0.25), shadow=[], state=uiconst.UI_DISABLED, fontsize=9, letterspace=1, linespace=8, idx=0)
                slot.sr.shortcutHint.top = 30
                if self.assumingcontrol:
                    slot.sr.shortcutHint.top -= 4


        self.RefreshShortcuts()



    def InitSlots(self):
        if not self or not hasattr(self, 'sr') or not self.sr.Get('slotsContainer'):
            return 
        self.sr.slotsContainer.Flush()
        self.sr.modules = {}
        self.sr.slotsByFlag = {}
        self.sr.slotsByOrder = {}
        self.totalSlaves = 0
        control = sm.GetService('pwn').GetCurrentControl()
        if control:
            self.assumingcontrol = True
        else:
            self.assumingcontrol = False
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        if ship is None:
            raise RuntimeError('ShipUI being inited with no ship state!')
        self.passiveFiltered = []
        if self.assumingcontrol:
            self.InitStructureSlots()
        else:
            shipmodules = ship.modules
            charges = {}
            for sublocation in ship.sublocations:
                charges[sublocation.flagID] = sublocation
                if sublocation.stacksize == 0:
                    sm.services['godma'].LogError('InitSlots.no quantity', sublocation, sublocation.flagID)

            for module in shipmodules:
                if module.categoryID == const.categoryCharge:
                    charges[module.flagID] = module

            xstep = int(ICONSIZE * 1.6)
            ystep = int(ICONSIZE * 1.4)
            vgridrange = 3
            hgridrange = 8
            grid = [[1.0, -1.0], [1.5, 0.0], [1.0, 1.0]]
            myOrder = self.GetSlotOrder()
            self.InitDrawSlots(xstep, ystep, vgridrange, hgridrange, grid, myOrder, slotType='shipslot')
            self.InitOverloadBtns(grid, shipmodules)
            self.InitGroupAllButtons()
            dogmaLocation = sm.StartService('clientDogmaIM').GetDogmaLocation()
            IsSlave = lambda itemID: dogmaLocation.IsModuleSlave(itemID, session.shipid)
            for moduleInfo in shipmodules:
                if IsSlave(moduleInfo.itemID):
                    self.totalSlaves += 1
                    continue
                self._FitSlot(moduleInfo, charges)

            self.CheckButtonVisibility(0, ['hiSlots', 'medSlots', 'lowSlots'], None, myOrder)
            self.slotsInited = 1



    def InitGroupAllButtons(self):
        w = self.sr.slotsContainer.width
        h = self.sr.slotsContainer.height
        centerX = (w - 20) / 2
        centerY = (h - 20) / 2
        ic = uicls.Icon(parent=self.sr.slotsContainer, icon='ui_73_16_251', idx=0, name='groupAllIcon', pos=(centerX + 68,
         centerY - 57,
         16,
         16), hint='')
        ic.state = uiconst.UI_HIDDEN
        ic.orgPos = ic.top
        ic.OnClick = self.OnGroupAllButtonClicked
        ic.OnMouseDown = (self.OverloadRackBtnMouseDown, ic)
        ic.OnMouseUp = (self.OverloadRackBtnMouseUp, ic)
        self.CheckGroupAllButton()



    def OnGroupAllButtonClicked(self, *args):
        if settings.user.ui.Get('lockModules', 0):
            return 
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if dogmaLocation.CanGroupAll(session.shipid):
            dogmaLocation.LinkAllWeapons(session.shipid)
        else:
            dogmaLocation.UnlinkAllWeapons(session.shipid)



    def InitOverloadBtns(self, grid, shipmodules):
        w = self.sr.slotsContainer.width
        h = self.sr.slotsContainer.height
        centerX = (w - 20) / 2
        centerY = (h - 20) / 2
        overloadEffectsByRack = {}
        modulesByRack = {}
        for module in shipmodules:
            for key in module.effects.iterkeys():
                effect = module.effects[key]
                if effect.effectID in (const.effectHiPower, const.effectMedPower, const.effectLoPower):
                    if effect.effectID not in modulesByRack:
                        modulesByRack[effect.effectID] = []
                    modulesByRack[effect.effectID].append(module)
                    for key in module.effects.iterkeys():
                        effect2 = module.effects[key]
                        if effect2.effectCategory == const.dgmEffOverload:
                            if effect.effectID not in overloadEffectsByRack:
                                overloadEffectsByRack[effect.effectID] = []
                            overloadEffectsByRack[effect.effectID].append(effect2)



        i = 0
        for each in ['Hi', 'Med', 'Lo']:
            (x, y,) = grid[i]
            par = uicls.Container(parent=self.sr.slotsContainer, name='overloadBtn' + each, width=20, height=20, align=uiconst.TOPLEFT, left=0, top=0, state=uiconst.UI_NORMAL, pickRadius=8)
            icon = uicls.Sprite(parent=par, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/overloadBtn%sOff.png' % each)
            par.left = centerX + 67 + int(x * 14)
            par.top = centerY + int(y * 14)
            par.OnClick = (self.OverloadRackBtnClick, par)
            par.OnMouseDown = (self.OverloadRackBtnMouseDown, par)
            par.OnMouseUp = (self.OverloadRackBtnMouseUp, par)
            par.OnMouseExit = (self.OverloadRackBtnMouseExit, par)
            par.orgPos = par.top
            par.active = False
            par.powerEffectID = getattr(const, 'effect%sPower' % each, None)
            par.activationID = None
            i += 1

        self.CheckOverloadRackBtnState(shipmodules)



    def ToggleRackOverload(self, what):
        if what not in ('Hi', 'Med', 'Lo') or self.sr.slotsContainer.destroyed:
            return 
        btn = uiutil.FindChild(self.sr.slotsContainer, 'overloadBtn' + what)
        if btn:
            if btn.activationID:
                uthread.new(self.OverloadRackBtnClick, btn)
            else:
                uthread.new(eve.Message, 'Disabled')



    def OverloadRackBtnClick(self, btn, *args):
        if settings.user.ui.Get('lockOverload', 0):
            eve.Message('error')
            eve.Message('LockedOverloadState')
            return 
        if btn.active:
            eve.Message('click')
            sm.GetService('godma').StopOverloadRack(btn.activationID)
        else:
            eve.Message('click')
            sm.GetService('godma').OverloadRack(btn.activationID)



    def OverloadRackBtnMouseDown(self, btn, *args):
        btn.top = btn.orgPos + 1



    def OverloadRackBtnMouseUp(self, btn, *args):
        btn.top = btn.orgPos



    def OverloadRackBtnMouseExit(self, btn, *args):
        btn.top = btn.orgPos



    def CheckOverloadRackBtnState(self, shipmodules = None):
        if self.assumingcontrol:
            return 
        if not self or not hasattr(self, 'sr') or not self.sr.Get('slotsContainer'):
            return 
        if self.checkingoverloadrackstate:
            self.checkingoverloadrackstate = 2
            return 
        self.checkingoverloadrackstate = 1
        if shipmodules is None:
            ship = sm.GetService('godma').GetItem(eve.session.shipid)
            if ship is None:
                return 
            shipmodules = ship.modules
        overloadEffectsByRack = {}
        modulesByRack = {}
        for module in shipmodules:
            for key in module.effects.iterkeys():
                effect = module.effects[key]
                if effect.effectID in (const.effectHiPower, const.effectMedPower, const.effectLoPower):
                    if effect.effectID not in modulesByRack:
                        modulesByRack[effect.effectID] = []
                    modulesByRack[effect.effectID].append(module)
                    for key in module.effects.iterkeys():
                        effect2 = module.effects[key]
                        if effect2.effectCategory == const.dgmEffOverload:
                            if effect.effectID not in overloadEffectsByRack:
                                overloadEffectsByRack[effect.effectID] = []
                            overloadEffectsByRack[effect.effectID].append(effect2)



        i = 0
        for each in ['Hi', 'Med', 'Lo']:
            btn = uiutil.GetChild(self.sr.slotsContainer, 'overloadBtn' + each)
            btn.activationID = None
            btn.active = False
            btn.children[0].LoadTexture('res:/UI/Texture/classes/ShipUI/overloadBtn%sOff.png' % each)
            btn.hint = mls.UI_CMD_OVERLOADRACK
            btn.state = uiconst.UI_DISABLED
            if btn.powerEffectID in modulesByRack:
                btn.activationID = modulesByRack[btn.powerEffectID][0].itemID
            if btn.powerEffectID in overloadEffectsByRack:
                sumInactive = sum([ 1 for olEffect in overloadEffectsByRack[btn.powerEffectID] if not olEffect.isActive ])
                if not sumInactive:
                    btn.children[0].LoadTexture('res:/UI/Texture/classes/ShipUI/overloadBtn%sOn.png' % each)
                    btn.active = True
                    btn.hint = mls.UI_CMD_STOPOVERLOADRACK
            btn.state = uiconst.UI_NORMAL

        if self.checkingoverloadrackstate == 2:
            self.checkingoverloadrackstate = 0
            return self.CheckOverloadRackBtnState(shipmodules)
        self.checkingoverloadrackstate = 0



    def CheckGroupAllButton(self):
        if self.destroyed:
            return 
        icon = uiutil.GetChild(self.sr.slotsContainer, 'groupAllIcon')
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        for (typeID, qty,) in dogmaLocation.GetGroupableTypes(session.shipid).iteritems():
            if qty > 1:
                break
        else:
            icon.state = uiconst.UI_HIDDEN
            return 

        icon.state = uiconst.UI_NORMAL
        if dogmaLocation.CanGroupAll(session.shipid):
            icon.LoadIcon('ui_73_16_252')
            hint = mls.UI_CMD_GROUPALLWEAPONS
        else:
            icon.LoadIcon('ui_73_16_251')
            hint = mls.UI_CMD_UNGROUPALLWEAPONS
        if settings.user.ui.Get('lockModules', False):
            hint = hint + ' (%s)' % mls.UI_GENERIC_LOCKED
        icon.hint = hint
        if getattr(self, 'updateGroupAllButtonThread', None):
            self.updateGroupAllButtonThread.kill()
        self.updateGroupAllButtonThread = uthread.new(self.UpdateGroupAllButton)



    def UpdateGroupAllButton(self):
        if not self or self.destroyed:
            return 
        GetOpacity = sm.GetService('clientDogmaIM').GetDogmaLocation().GetGroupAllOpacity
        if sm.GetService('clientDogmaIM').GetDogmaLocation().CanGroupAll(session.shipid):
            attributeName = 'lastGroupAllRequest'
        else:
            attributeName = 'lastUngroupAllRequest'
        icon = uiutil.GetChild(self.sr.slotsContainer, 'groupAllIcon')
        icon.state = uiconst.UI_DISABLED
        while True:
            opacity = GetOpacity(attributeName)
            if opacity > 0.999:
                break
            icon.color.a = 0.2 + opacity * 0.6
            blue.pyos.synchro.Yield()
            if not self or self.destroyed:
                return 

        icon.color.a = 1.0
        icon.state = uiconst.UI_NORMAL



    def CheckButtonVisibility(self, gidx, sTypes, totalslot, myOrder):
        totalslots = totalslot
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        lastType = ''
        showEmptySlots = settings.user.ui.Get('showEmptySlots', 0)
        totalHi = getattr(ship, 'hiSlots', 0)
        totalMed = getattr(ship, 'medSlots', 0)
        totalLow = getattr(ship, 'lowSlots', 0)
        slotUIID = 0
        for sType in sTypes:
            if totalslot is None:
                totalslots = int(getattr(ship, sType, 0))
            ignoredSlots = 0
            for sidx in xrange(totalslots):
                if sidx == 8:
                    break
                flagTypes = ['Hi',
                 'Med',
                 'Lo',
                 'Stuct']
                if not self.assumingcontrol:
                    if gidx < len(flagTypes):
                        slotFlag = getattr(const, 'flag%sSlot%s' % (flagTypes[gidx], sidx), None)
                    slot = self.sr.slotsByFlag.get(slotFlag, None)
                else:
                    slotFlag = myOrder[sidx]
                    slot = self.sr.slotsByFlag.get(slotFlag, None)
                typeNames = ['High',
                 'Medium',
                 'Low',
                 'Stuct']
                slotUIID += 1
                if gidx < len(typeNames):
                    currType = typeNames[gidx]
                    if currType != lastType:
                        slotUIID = 1
                    lastType = currType
                    if slot:
                        slot.name = 'inFlight%sSlot%s' % (typeNames[gidx], slotUIID)
                if showEmptySlots and not self.assumingcontrol:
                    if slot and slot.sr.module is None and slotFlag not in self.passiveFiltered:
                        slot.showAsEmpty = 1
                        if self.assumingcontrol:
                            slot.hint = mls.UI_INFLIGHT_EMPTYSTRUCTURECONTROLSLOT
                            slot.state = uiconst.UI_NORMAL
                        else:
                            if gidx == 0:
                                if ignoredSlots < self.totalSlaves:
                                    ignoredSlots += 1
                                    slot.ignored = 1
                                    continue
                            slot.hint = [mls.UI_INFLIGHT_EMPTYHIGHSLOT, mls.UI_INFLIGHT_EMPTYMEDIUMSLOT, mls.UI_INFLIGHT_EMPTYLOWSLOT][gidx]
                            slot.state = uiconst.UI_NORMAL
                            iconpath = ['ui_8_64_11',
                             'ui_8_64_10',
                             'ui_8_64_9',
                             'ui_44_64_14'][gidx]
                            icon = uicls.Icon(icon=iconpath, parent=slot, pos=(13, 13, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0, ignoreSize=True)
                            icon.left = (slot.width - icon.width) / 2
                            icon.color.a = 0.25

            gidx += 1




    def _FitStructureSlot(self, moduleInfo, charges):
        showPassive = settings.user.ui.Get('showPassiveModules', 1)
        if moduleInfo.categoryID != const.categoryStructure:
            return 
        if not showPassive and self.GetDefaultEffect(moduleInfo) is None:
            self.passiveFiltered.append(moduleInfo.flagID)
            return 
        slot = self.sr.slotsByFlag.get(moduleInfo.itemID, None)
        if slot is None:
            return 
        if slot.sr.module is not None:
            return 
        self.FitStructureSlot(slot, moduleInfo, charges.get(moduleInfo.itemID, None))



    def _FitSlot(self, moduleInfo, charges, grey = 0, slotUIID = 'slot'):
        showPassive = settings.user.ui.Get('showPassiveModules', 1)
        if moduleInfo.categoryID == const.categoryCharge:
            return 
        if not showPassive and self.GetDefaultEffect(moduleInfo) is None:
            self.passiveFiltered.append(moduleInfo.flagID)
            return 
        slot = self.sr.slotsByFlag.get(moduleInfo.flagID, None)
        if slot is None:
            return 
        if slot.sr.module is not None:
            return 
        self.FitSlot(slot, moduleInfo, charges.get(moduleInfo.flagID, None), grey=grey, slotUIID=slotUIID)



    def GetDefaultEffect(self, moduleInfo):
        for key in moduleInfo.effects.iterkeys():
            effect = moduleInfo.effects[key]
            if self.IsEffectActivatible(effect):
                return effect




    def IsEffectActivatible(self, effect):
        return effect.isDefault and effect.effectName != 'online' and effect.effectCategory in (const.dgmEffActivation, const.dgmEffTarget)



    def ResetSwapMode(self):
        for each in self.sr.slotsContainer.children:
            each.opacity = 1.0
            if each.sr.get('module', -1) == -1:
                continue
            if each.sr.module is None and not getattr(each, 'showAsEmpty', 0) or getattr(each, 'ignored', 0):
                each.state = uiconst.UI_HIDDEN
            if getattr(each.sr, 'module', None):
                if getattr(each, 'linkDragging', None):
                    each.linkDragging = 0
                    each.sr.module.CheckOverload()
                    each.sr.module.CheckOnline()
                    each.sr.module.CheckMasterSlave()
                    each.sr.module.StopShowingGroupHighlight()
                    each.sr.module.CheckOnline()
                each.sr.module.blockClick = 0




    def StartDragMode(self, itemID, typeID):
        for each in self.sr.slotsContainer.children:
            if not hasattr(each, 'sr') or not hasattr(each.sr, 'module'):
                continue
            if each.name.startswith('overload') or each.name == 'groupAllIcon':
                continue
            if each.sr.module is None:
                each.opacity = 0.7
            each.state = uiconst.UI_NORMAL
            if typeID is None:
                continue
            if getattr(each.sr, 'module', None) is not None:
                moduleType = each.sr.module.GetModuleType()
                isGroupable = each.sr.module.sr.moduleInfo.groupID in const.dgmGroupableGroupIDs
                if isGroupable:
                    each.linkDragging = 1
                    if each.sr.module.sr.moduleInfo.itemID == itemID:
                        each.sr.module.icon.SetAlpha(0.2)
                elif moduleType and moduleType[0] == typeID:
                    each.sr.module.ShowGroupHighlight()
            else:
                continue




    def GetPosFromFlag(self, slotFlag):
        return self.sr.slotsByFlag[slotFlag].sr.slotPos



    def GetSlotOrder(self):
        defaultOrder = []
        for r in xrange(3):
            for i in xrange(8):
                slotFlag = getattr(const, 'flag%sSlot%s' % (['Hi', 'Med', 'Lo'][r], i), None)
                if slotFlag is not None:
                    defaultOrder.append(slotFlag)


        try:
            return settings.user.ui.Get('slotOrder', {}).get(eve.session.shipid, defaultOrder)
        except:
            log.LogException()
            sys.exc_clear()
            return defaultOrder



    def ChangeSlots(self, toFlag, fromFlag):
        toModule = self.GetModuleType(toFlag)
        fromModule = self.GetModuleType(fromFlag)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if toModule and fromModule and toModule[0] == fromModule[0]:
            self.LinkWeapons(toModule, fromModule, toFlag, fromFlag, merge=not shift)
            if not sm.GetService('clientDogmaIM').GetDogmaLocation().IsModuleMaster(toModule[1], session.shipid):
                self.SwapSlots(fromFlag, toFlag)
        else:
            self.SwapSlots(toFlag, fromFlag)



    def SwapSlots(self, slotFlag1, slotFlag2):
        module1 = self.GetModuleType(slotFlag1)
        module2 = self.GetModuleType(slotFlag2)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if shift and module1 is None and module2 is not None:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            if dogmaLocation.IsInWeaponBank(session.shipid, module2[1]):
                moduleID = dogmaLocation.UngroupModule(session.shipid, module2[1])
                slotFlag2 = dogmaLocation.GetItem(moduleID).flagID
        current = self.GetSlotOrder()[:]
        flag1Idx = current.index(slotFlag1)
        flag2Idx = current.index(slotFlag2)
        current[flag1Idx] = slotFlag2
        current[flag2Idx] = slotFlag1
        all = settings.user.ui.Get('slotOrder', {})
        all[eve.session.shipid] = current
        settings.user.ui.Set('slotOrder', all)
        self.InitSlots()



    def LinkWeapons(self, master, slave, slotFlag1, slotFlag2, merge = False):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        groupID = cfg.invtypes.Get(master[0]).groupID
        areTurrets = groupID in const.dgmGroupableGroupIDs
        slaves = dogmaLocation.GetSlaveModules(slave[1], session.shipid)
        swapSlots = 0
        if slaves:
            swapSlots = 1
        if not areTurrets:
            eve.Message('CustomNotify', {'notify': mls.UI_SHARED_WEAPONLINK_NOTTHISTYPE})
            return 
        weaponLinked = dogmaLocation.LinkWeapons(session.shipid, master[1], slave[1], merge=merge)
        if weaponLinked and swapSlots:
            self.SwapSlots(slotFlag1, slotFlag2)



    def GetModuleType(self, flag):
        if not self.sr.slotsByFlag.has_key(flag):
            return None
        module = self.sr.slotsByFlag[flag].sr.module
        if not module:
            return None
        return module.GetModuleType()



    def FitSlot(self, slot, moduleInfo, charge = None, grey = 0, slotUIID = 'slot'):
        p = uiutil.GetChild(slot, 'innerArea')
        pos = (slot.width - 48) / 2
        module = xtriui.ModuleButton(parent=p, align=uiconst.TOPLEFT, width=48, height=48, top=pos, left=pos, idx=0, state=uiconst.UI_NORMAL)
        module.Setup(moduleInfo, grey=grey)
        self.sr.modules[moduleInfo.itemID] = module
        slot.sr.module = module
        slot.state = uiconst.UI_NORMAL
        slot.sr.shortcutHint.state = uiconst.UI_HIDDEN
        slot.name = slotUIID
        if charge:
            module.SetCharge(charge)
        if moduleInfo.flagID in [const.flagHiSlot0,
         const.flagHiSlot1,
         const.flagHiSlot2,
         const.flagHiSlot3,
         const.flagHiSlot4,
         const.flagHiSlot5,
         const.flagHiSlot6,
         const.flagHiSlot7]:
            self.myHarpointFlags.append(moduleInfo.flagID)



    def FitStructureSlot(self, slot, moduleInfo, charge = None):
        pos = (slot.width - 48) / 2
        module = xtriui.DefenceStructureButton(parent=slot, align=uiconst.TOPLEFT, width=64, height=250, top=0, left=0, idx=1, state=uiconst.UI_DISABLED)
        module.Setup(moduleInfo)
        self.sr.modules[moduleInfo.itemID] = module
        slot.sr.module = module
        slot.state = uiconst.UI_NORMAL
        if charge:
            module.SetCharge(charge)



    def AutoPilotOnOff(self, onoff, *args):
        if onoff:
            sm.GetService('autoPilot').SetOn()
        else:
            sm.GetService('autoPilot').SetOff('toggled by shipUI')



    def OnAutoPilotOn(self):
        uiutil.GetChild(self.sr.autopilotBtn, 'busy').state = uiconst.UI_DISABLED
        self.sr.autopilotBtn.hint = mls.UI_CMD_DEACTIVATEAUTOPILOT
        self.sr.autopilotBtn.hint += self._GetShortcutForCommand(self.sr.autopilotBtn.cmdName)



    def OnAutoPilotOff(self):
        uiutil.GetChild(self.sr.autopilotBtn, 'busy').state = uiconst.UI_HIDDEN
        self.sr.autopilotBtn.hint = mls.UI_CMD_ACTIVATEAUTOPILOT
        self.sr.autopilotBtn.hint += self._GetShortcutForCommand(self.sr.autopilotBtn.cmdName)



    def OnTacticalOverlayChange(self, isOn):
        activeIndicator = uiutil.GetChild(self.sr.tacticalBtn, 'busy')
        if isOn:
            activeIndicator.state = uiconst.UI_DISABLED
            self.sr.tacticalBtn.sr.hint = mls.UI_CMD_HIDETACTICALOVERLEY
        else:
            activeIndicator.state = uiconst.UI_HIDDEN
            self.sr.tacticalBtn.sr.hint = mls.UI_CMD_SHOWTACTICALOVERLEY



    def OnCloseView(self):
        sm.UnregisterNotify(self)
        settings.user.ui.Set('selected_shipuicateg', self.sr.selectedcateg)
        if getattr(self, 'cookie', None):
            sm.GetService('inv').Unregister(self.cookie)
            self.cookie = None



    def IsMine(self, rec):
        return rec.locationID == eve.session.shipid and rec.categoryID == const.categoryModule and rec.flagID not in (const.flagCargo, const.flagDroneBay)



    def OnInvChange(self, item, change):
        if const.ixFlag in change:
            if cfg.IsShipFittingFlag(item.flagID) or cfg.IsShipFittingFlag(change[const.ixFlag]):
                uicore.layer.shipui.CloseView()
                uicore.layer.shipui.OpenView()



    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return 
        log.LogInfo('DoBallRemove::shipui', ball.id)
        if self.ball is not None and ball.id == self.ball.id:
            self.UnhookBall()
        uthread.new(self.UpdateJammersAfterBallRemoval, ball.id)



    def UpdateJammersAfterBallRemoval(self, ballID):
        jams = self.jammers.keys()
        checkJam = 0
        for jammingType in jams:
            jam = self.jammers[jammingType]
            for id in jam.keys():
                (sourceBallID, moduleID, targetBallID,) = id
                if ballID == sourceBallID:
                    del self.jammers[jammingType][id]
                    checkJam = 1


        if checkJam:
            self.CheckJam()



    def DoBallClear(self, solItem):
        self.ball = None



    def ProcessShipEffect(self, godmaStm, effectState):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        masterID = dogmaLocation.IsInWeaponBank(session.shipid, effectState.itemID)
        if masterID:
            module = self.GetModule(masterID)
        else:
            module = self.GetModule(effectState.itemID)
        if module:
            uthread.new(module.Update, effectState)
            uthread.new(self.CheckOverloadRackBtnState)
        if effectState.error is not None:
            uthread.new(eve.Message, effectState.error[0], effectState.error[1])
        if effectState.effectName == 'online':
            self.UpdateGauges()



    def OnAttributes(self, ch):
        for each in ch:
            if each[0] == 'isOnline':
                self.CheckGroupAllButton()
            if each[0] != 'damage':
                continue
            (masterID, damage,) = sm.GetService('godma').GetStateManager().GetMaxDamagedModuleInGroup(session.shipid, each[1].itemID)
            module = self.GetModule(masterID)
            if module is None:
                continue
            module.SetDamage(damage / module.sr.moduleInfo.hp)




    def ProcessRookieStateChange(self, state):
        if eve.session.solarsystemid and self.sr.wnd:
            if not not (eve.rookieState and eve.rookieState < 21):
                self.state = uiconst.UI_HIDDEN
            else:
                self.state = uiconst.UI_PICKCHILDREN
                self.InitButtons()



    def OnJamStart(self, sourceBallID, moduleID, targetBallID, jammingType, startTime, duration):
        if jammingType not in self.jammers:
            self.jammers[jammingType] = {}
        self.jammers[jammingType][(sourceBallID, moduleID, targetBallID)] = (startTime, duration)
        self.CheckJam()



    def OnJamEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        if jammingType in self.jammers:
            id = (sourceBallID, moduleID, targetBallID)
            if id in self.jammers[jammingType]:
                del self.jammers[jammingType][id]
        self.CheckJam()



    def CheckJam(self):
        jams = self.jammers.keys()
        jams.sort()
        for jammingType in jams:
            jam = self.jammers[jammingType]
            sortList = []
            for id in jam.iterkeys():
                (sourceBallID, moduleID, targetBallID,) = id
                if targetBallID == eve.session.shipid:
                    (startTime, duration,) = jam[id]
                    sortList.append((startTime + duration, (sourceBallID,
                      moduleID,
                      targetBallID,
                      jammingType,
                      startTime,
                      duration)))

            if sortList:
                sortList = uiutil.SortListOfTuples(sortList)
                (sourceBallID, moduleID, targetBallID, jammingType, startTime, duration,) = sortList[-1]
                bracketName = sm.GetService('bracket').GetBracketName(sourceBallID)
                self.ShowTimer(jammingType, startTime, duration, '%s<br>%s' % (bracketName, self.timerNames.get(jammingType, mls.UI_INFLIGHT_NAMELESS)))
            else:
                self.KillTimer(jammingType)




    def OnShipScanCompleted(self, shipID, capacitorCharge, capacitorCapacity, hardwareList):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return 
        slimItem = bp.slimItems[shipID]
        wndName = '%s %s' % (uix.GetSlimItemName(slimItem), mls.UI_INFLIGHT_SCANRESULT)
        wnd = sm.GetService('window').GetWindow(wndName, create=1, decoClass=form.ShipScan, maximize=1, shipID=shipID, windowPrefsID='shipScan')
        if wnd:
            wnd.LoadResult(capacitorCharge, capacitorCapacity, hardwareList)



    def OnCargoScanComplete(self, shipID, cargoList):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return 
        slimItem = bp.slimItems[shipID]
        wndName = 'cargoscanner %s' % uix.GetSlimItemName(slimItem)
        wnd = sm.GetService('window').GetWindow(wndName, create=1, decoClass=form.CargoScan, maximize=1, shipID=shipID, cargoList=cargoList, windowPrefsID='cargoScan')
        if wnd:
            wnd.LoadResult(cargoList)



    def OnModify(self, op, rec, change):
        t = uthread.new(self.OnModify_thread, op, rec, change)
        t.context = 'ShipUI::OnModify'



    def OnModify_thread(self, op, rec, change):
        lg.Info('shipui', 'OnModify', op, change, rec)
        if not rec:
            return 
        if cfg.invtypes.Get(rec.typeID).categoryID != const.categoryCharge:
            lg.Warn('shipui', 'OnModify: not a charge?')
            return 
        haveThisCharge = 0
        for (flag, slot,) in self.sr.slotsByFlag.iteritems():
            if slot and slot.sr.module.charge and slot.sr.module.charge.itemID == rec.itemID:
                haveThisCharge = 1
                break

        slot = self.sr.slotsByFlag.get(rec.flagID, None)
        if slot and slot.sr.module:
            if op == 'r' or rec.stacksize == 0:
                slot.sr.module.SetCharge(None)
            elif slot.sr.module.charge and slot.sr.module.charge.itemID and slot.sr.module.charge.itemID != rec.itemID:
                lg.Info('shipui', 'Residual update in parting missile-- ignoring')
            else:
                slot.sr.module.SetCharge(rec)
        elif haveThisCharge:
            self.sr.slotsByFlag[flag].SetCharge(None)



    def UnhookBall(self):
        self.ball = None



    def Init(self, ball):
        if ball.id == self.initedshipid:
            self.ball = ball
            return 
        if self.initing:
            return 
        if eve.session.shipid is None:
            self.CloseView()
            return 
        self.initing = 1
        self.initedshipid = eve.session.shipid
        self.capacity = None
        self.ball = ball
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        if ship is None:
            raise RuntimeError('ShipUI being inited with no ship state!')
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        dogmaLocation.LoadItem(eve.session.shipid)
        self.InitSpeed()
        uthread.new(self.UpdateGauges)
        if not (eve.rookieState and eve.rookieState < 21) and not sm.GetService('planetUI').IsOpen():
            self.state = uiconst.UI_PICKCHILDREN
        self.InitSlots()
        self.initing = 0
        if not sm.GetService('map').IsOpen() and not sm.GetService('planetUI').IsOpen():
            uix.GetInflightNav()
        self.invReady = 1



    def InitSpeed(self):
        if self.speedInited:
            return 
        for btnname in ['stopButton', 'maxspeedButton']:
            newBtn = uiutil.GetChild(self.sr.wnd, btnname)
            newBtn.OnClick = (self.ClickSpeedBtn, newBtn)
            if btnname == 'maxspeedButton':
                newBtn.hint = mls.UI_INFLIGHT_SETFULLSPEED + ' (' + self.FormatSpeed(self.ball.maxVelocity) + ')'
                newBtn.OnMouseEnter = self.CheckSpeedHint
            else:
                newBtn.hint = mls.UI_INFLIGHT_STOPTHESHIP
            self.sr.Set(btnname, newBtn)

        self.sr.speedGauge = uiutil.GetChild(self.sr.wnd, 'speedNeedle')
        self.sr.speedGaugeParent = uiutil.GetChild(self.sr.wnd, 'speedGaugeParent')
        self.sr.speedGaugeParent.OnClick = self.ClickSpeedoMeter
        self.sr.speedGaugeParent.OnMouseMove = self.CheckSpeedHint
        self.sr.speedStatus = uicls.Label(text='', parent=self.sr.speedGaugeParent.parent.parent, left=0, top=127, color=(0.0, 0.0, 0.0, 1.0), width=100, autowidth=False, letterspace=1, fontsize=9, state=uiconst.UI_DISABLED, uppercase=1, idx=0, shadow=None, align=uiconst.CENTERTOP)
        self.speedInited = 1
        uthread.new(self.SetSpeed, self.ball.speedFraction, initing=1)
        self.sr.speedtimer = base.AutoTimer(133, self.UpdateSpeed)



    def ClickSpeedBtn(self, btn, *args):
        if eve.rookieState and eve.rookieState < 22:
            return 
        if btn.name == 'stopButton':
            self.StopShip()
        elif btn.name == 'maxspeedButton':
            bp = sm.GetService('michelle').GetBallpark()
            rbp = sm.GetService('michelle').GetRemotePark()
            if bp:
                ownBall = bp.GetBall(eve.session.shipid)
                if ownBall and rbp is not None and ownBall.mode == destiny.DSTBALL_STOP:
                    if not sm.GetService('autoPilot').GetState():
                        direction = trinity.TriVector(0.0, 0.0, 1.0)
                        currentDirection = self.ball.GetQuaternionAt(blue.os.GetTime())
                        direction.TransformQuaternion(currentDirection)
                        rbp.GotoDirection(direction.x, direction.y, direction.z)
            if rbp is not None:
                rbp.SetSpeedFraction(1.0)
                sm.GetService('logger').AddText('%s %s' % (mls.UI_INFLIGHT_SPEEDCHANGEDTO, self.FormatSpeed(self.ball.maxVelocity)), 'notify')
                sm.GetService('gameui').Say('%s %s' % (mls.UI_INFLIGHT_SPEEDCHANGEDTO, self.FormatSpeed(self.ball.maxVelocity)))
                self.wantedspeed = 1.0
            else:
                self.wantedspeed = None



    def GetSpeedPortion(self):
        (l, t, w, h,) = self.sr.wnd.GetAbsolute()
        centerX = l + w / 2
        centerY = t + h / 2
        y = float(uicore.uilib.y - centerY)
        x = float(uicore.uilib.x - centerX)
        if x and y:
            angle = math.atan(x / y)
            deg = angle / math.pi * 180.0
            factor = (45.0 + deg) / 90.0
            if factor < 0.05:
                return 0.0
            else:
                if factor > 0.95:
                    return 1.0
                return factor
        return 0.5



    def ClickSpeedoMeter(self, *args):
        uthread.new(self.SetSpeed, self.GetSpeedPortion())



    def CheckSpeedHint(self, *args):
        if not self.ball:
            return 
        mo = uicore.uilib.mouseOver
        ms = self.sr.Get('maxspeedButton')
        if mo == self.sr.speedGaugeParent:
            portion = self.GetSpeedPortion()
            parent = self.sr.speedGaugeParent
            speed = self.ball.GetVectorDotAt(blue.os.GetTime()).Length()
            if self.ball.mode == destiny.DSTBALL_WARP:
                hint = '%s: %s/%s' % (mls.UI_INFLIGHT_CURRENTSPEED, util.FmtDist(speed, 2), mls.UI_GENERIC_SECONDVERYSHORT)
                hint += '<br>%s' % mls.UI_INFLIGHT_CANNOTCHANGESPEEDWHILEWARPING
            else:
                fmtSpeed = self.FormatSpeed(speed)
                hint = '%s: %s' % (mls.UI_INFLIGHT_CURRENTSPEED, fmtSpeed)
                hint += '<br>%s %s' % (mls.UI_INFLIGHT_CLICKTOSETSPEEDTO, self.FormatSpeed(portion * self.ball.maxVelocity))
            parent.hint = hint
            uicore.UpdateHint(parent)
        elif ms and not ms.destroyed and mo == ms:
            ms.hint = mls.UI_INFLIGHT_SETFULLSPEED + ' (' + self.FormatSpeed(self.ball.maxVelocity) + ')'
            uicore.UpdateHint(ms)



    def FormatSpeed(self, speed):
        if speed < 100:
            return '%.1f %s' % (speed, mls.UI_GENERIC_MPERS)
        return '%i %s' % (long(speed), mls.UI_GENERIC_MPERS)



    def InitCapacitor(self, maxcap):
        self.capacitorDone = 0
        self.capacity = float(maxcap)
        self.lastsetcapacitor = None
        if self.sr.powercore is None:
            return 
        self.sr.powercore.Flush()
        self.powerCells = []
        numcol = min(18, int(maxcap / 50))
        rotstep = 360.0 / max(1, numcol)
        colWidth = max(12, min(16, numcol and int(192 / numcol)))
        for i in range(numcol):
            powerColumn = uicls.Transform(parent=self.sr.powercore, name='powerColumn', pos=(0,
             0,
             colWidth,
             56), align=uiconst.CENTER, state=uiconst.UI_DISABLED, rotation=mathUtil.DegToRad(i * -rotstep), idx=0)
            for ci in xrange(4):
                newcell = uicls.Sprite(parent=powerColumn, name='pmark', pos=(0,
                 ci * 5,
                 10 - ci * 2,
                 7), align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/capacitorCell_2.png', color=(0, 0, 0, 0))
                self.powerCells.insert(0, newcell)


        self.capacitorDone = 1



    def GetModuleForFKey(self, key):
        slot = int(key[1:])
        gidx = (slot - 1) / 8
        sidx = (slot - 1) % 8
        slot = self.sr.slotsByOrder.get((gidx, sidx), None)
        if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
            return slot.sr.module



    def GetModule(self, moduleID):
        return self.sr.modules.get(moduleID, None)



    def Hide(self):
        self.state = uiconst.UI_HIDDEN



    def Show(self):
        if not (eve.rookieState and eve.rookieState < 21):
            self.state = uiconst.UI_PICKCHILDREN



    def OnMouseEnter(self, *args):
        if uix.GetInflightNav(0):
            uix.GetInflightNav(0).HideTargetingCursor()



    def FormatReadoutValue(self, portion, total):
        if settings.user.ui.Get('readoutType', 1):
            if total == 0:
                return '0.0%'
            return '%s%%' % util.FmtAmt(portion / total * 100.0, showFraction=1)
        else:
            return '%s/%s' % (util.FmtAmt(portion, showFraction=1), util.FmtAmt(total, showFraction=1))



    def GetMenu(self):
        if not hasattr(eve.session, 'shipid'):
            return []
        return sm.GetService('menu').CelestialMenu(eve.session.shipid)



    def UpdateGauges(self):
        if getattr(self, 'updatingGauges', 0) or not self or self.destroyed:
            return 
        self.updatingGauges = 1
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        if not ship:
            self.sr.gaugetimer = None
            return 
        if not self or self.destroyed:
            return 
        if not hasattr(self, 'capacity'):
            return 
        maxcap = ship.capacitorCapacity
        if self.capacity != maxcap:
            self.InitCapacitor(maxcap)
        self.SetPower(ship.charge, float(maxcap))
        structure = max(0.0, min(1.0, float('%.2f' % (1.0 - ship.damage / ship.hp))))
        lastStructure = getattr(self, 'lastStructure', 0.0)
        armor = 0.0
        if ship.armorHP != 0:
            armor = max(0.0, min(1.0, float('%.2f' % (1.0 - ship.armorDamage / ship.armorHP))))
        lastArmor = getattr(self, 'lastArmor', 0.0)
        shield = 0.0
        if ship.shieldCapacity != 0:
            shield = max(0.0, min(1.0, float('%.2f' % (ship.shieldCharge / ship.shieldCapacity))))
        lastShield = getattr(self, 'lastShield', 0.0)
        lastLowHeat = getattr(self, 'lastLowHeat', 0.0)
        lastMedHeat = getattr(self, 'lastMedHeat', 0.0)
        lastHiHeat = getattr(self, 'lastHiHeat', 0.0)
        heatLow = ship.heatLow / ship.heatCapacityLow
        heatMed = ship.heatMed / ship.heatCapacityMed
        heatHi = ship.heatHi / ship.heatCapacityHi
        try:
            self.structureGauge.hint = mls.UI_INFLIGHT_STRUCTURESTATUS % {'portion': structure * 100,
             'left': max(0, ship.hp - ship.damage),
             'max': ship.hp}
            self.armorGauge.hint = mls.UI_INFLIGHT_ARMORSTATUS % {'portion': armor * 100,
             'left': max(0, ship.armorHP - ship.armorDamage),
             'max': ship.armorHP}
            self.shieldGauge.hint = mls.UI_INFLIGHT_SHIELDSTATUS % {'portion': shield * 100,
             'left': ship.shieldCharge,
             'max': ship.shieldCapacity}
            self.sr.heatPick.hint = mls.UI_INFLIGHT_HEATSTATUS % {'low': heatLow * 100,
             'med': heatMed * 100,
             'high': heatHi * 100}
            mo = uicore.uilib.mouseOver
            if mo in (self.structureGauge,
             self.armorGauge,
             self.shieldGauge,
             self.sr.powercore):
                uicore.UpdateHint(mo)
            if self.sr.gaugeReadout and self.sr.gaugeReadout.state != uiconst.UI_HIDDEN:
                if settings.user.ui.Get('readoutType', 1):
                    self.sr.gaugeReadout.sr.Get('shield').text = '%s: %s%%' % (mls.UI_GENERIC_SHIELD, util.FmtAmt(shield * 100, showFraction=0))
                    self.sr.gaugeReadout.sr.Get('armor').text = '%s: %s%%' % (mls.UI_GENERIC_ARMOR, util.FmtAmt(armor * 100, showFraction=0))
                    self.sr.gaugeReadout.sr.Get('structure').text = '%s: %s%%' % (mls.UI_GENERIC_STRUCTURE, util.FmtAmt(structure * 100, showFraction=0))
                else:
                    self.sr.gaugeReadout.sr.Get('shield').text = '%s: %s/%s' % (mls.UI_GENERIC_SHIELD, util.FmtAmt(ship.shieldCharge, showFraction=1), util.FmtAmt(ship.shieldCapacity, showFraction=1))
                    self.sr.gaugeReadout.sr.Get('armor').text = '%s: %s/%s' % (mls.UI_GENERIC_ARMOR, util.FmtAmt(max(0, ship.armorHP - ship.armorDamage), showFraction=1), util.FmtAmt(ship.armorHP, showFraction=1))
                    self.sr.gaugeReadout.sr.Get('structure').text = '%s: %s/%s' % (mls.UI_GENERIC_STRUCTURE, util.FmtAmt(max(0, ship.hp - ship.damage), showFraction=1), util.FmtAmt(ship.hp, showFraction=1))
            props = [(lastStructure,
              structure,
              self.structureGauge,
              None,
              1),
             (lastArmor,
              armor,
              self.armorGauge,
              None,
              1),
             (lastShield,
              shield,
              self.shieldGauge,
              None,
              1),
             (lastLowHeat,
              heatLow,
              self.sr.lowHeatGauge,
              None,
              2),
             (lastMedHeat,
              heatMed,
              self.sr.medHeatGauge,
              None,
              3),
             (lastHiHeat,
              heatHi,
              self.sr.hiHeatGauge,
              None,
              4)]
        except Exception as e:
            log.LogWarn(e)
            sys.exc_clear()
            return 
        (start, ndt,) = (blue.os.GetTime(), 0.0)
        while ndt != 1.0:
            ndt = max(ndt, min(blue.os.TimeDiffInMs(start) / 500.0, 1.0))
            for (lastval, newval, gauge, text, gaugeflag,) in props:
                lerped = mathUtil.Lerp(lastval, newval, ndt)
                if text:
                    text.text = '<center>%d%%' % (lerped * 100)
                if gaugeflag == 1:
                    gauge.textureSecondary.rotation = math.pi * (1.0 - lerped)
                if gaugeflag == 2:
                    gauge.SetRotation(mathUtil.DegToRad(-2.0 - 56.0 * lerped))
                    self.UpdateHeatGauge('Low', lerped)
                elif gaugeflag == 3:
                    gauge.SetRotation(mathUtil.DegToRad(-62.0 - 56.0 * lerped))
                    self.UpdateHeatGauge('Med', lerped)
                elif gaugeflag == 4:
                    gauge.SetRotation(mathUtil.DegToRad(-122.0 - 56.0 * lerped))
                    self.UpdateHeatGauge('Hi', lerped)

            blue.pyos.synchro.Yield()

        self.lastStructure = structure
        self.lastArmor = armor
        self.lastShield = shield
        self.lastLowHeat = heatLow
        self.lastMedHeat = heatMed
        self.lastHiHeat = heatHi
        if not self.sr.gaugetimer and hasattr(self, 'UpdateGauges'):
            self.sr.gaugetimer = base.AutoTimer(500, self.UpdateGauges)
        self.updatingGauges = 0



    def UpdateHeatGauge(self, what, val):
        if val <= 0.125:
            idx = 0
        elif val <= 0.375:
            idx = 1
        elif val <= 0.625:
            idx = 2
        elif val <= 0.875:
            idx = 3
        else:
            idx = 4
        sprite = self.sr.Get('heat%sUnderlay' % what)
        if sprite:
            sprite.LoadTexture('res:/UI/Texture/classes/ShipUI/%sHeat_%s.png' % (what.lower(), idx))



    def UpdateSpeed(self):
        if self.updatingspeed:
            return 
        self.updatingspeed = 1
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if scene is None or scene.ballpark is None:
            self.updatingspeed = 0
            return 
        if self.ball and self.ball.ballpark and self.sr.speedGauge and not self.sr.speedGauge.destroyed:
            speed = self.ball.GetVectorDotAt(blue.os.GetTime()).Length()
            try:
                realSpeed = max(0.0, min(1.0, speed / self.ball.maxVelocity))
            except:
                sys.exc_clear()
                realSpeed = 0.0
        else:
            self.updatingspeed = 0
            return 
        speedGauge = self.sr.speedGauge
        lastSpeed = getattr(self, 'lastSpeed', None)
        degRot = 90.0 * realSpeed
        if lastSpeed != speed:
            speedGauge.SetRotation(mathUtil.DegToRad(45.0 + degRot))
            if not (self.ball and self.ball.ballpark):
                self.updatingspeed = 0
                return 
            if self.ball.mode == destiny.DSTBALL_WARP:
                fmtSpeed = '<center>(%s)' % mls.UI_INFLIGHT_WARPING
            else:
                fmtSpeed = '<center>' + self.FormatSpeed(speed)
            if self.sr.speedStatus.text != fmtSpeed:
                self.sr.speedStatus.text = fmtSpeed
            self.CheckSpeedHint()
            if self.sr.speedtimer and self.sr.speedtimer.interval != 66:
                self.sr.speedtimer.interval = 66
            self.lastSpeed = speed
        elif self.sr.speedtimer and self.sr.speedtimer.interval != 133:
            self.sr.speedtimer.interval = 133
        self.updatingspeed = 0



    def StopShip(self, *args):
        uicore.cmd.CmdStopShip()
        self.wantedspeed = 0.0



    def SetSpeed(self, speed, initing = 0):
        if not self or self.destroyed:
            return 
        if eve.rookieState and eve.rookieState < 22:
            return 
        if (not self.ball or self.ball.mode == destiny.DSTBALL_WARP) and speed > 0:
            return 
        if self.ball and self.ball.ballpark is None:
            self.UnhookBall()
            return 
        if not initing and self.wantedspeed is not None and int(self.ball.speedFraction * 1000) == int(speed * 1000) == int(self.wantedspeed * 1000) and speed > 0:
            return 
        if speed <= 0.0:
            self.StopShip()
        elif speed != self.wantedspeed:
            rbp = sm.GetService('michelle').GetRemotePark()
            bp = sm.GetService('michelle').GetBallpark()
            if bp and not initing:
                ownBall = bp.GetBall(eve.session.shipid)
                if ownBall and rbp is not None and ownBall.mode == destiny.DSTBALL_STOP:
                    if not sm.GetService('autoPilot').GetState():
                        direction = trinity.TriVector(0.0, 0.0, 1.0)
                        currentDirection = self.ball.GetQuaternionAt(blue.os.GetTime())
                        direction.TransformQuaternion(currentDirection)
                        rbp.GotoDirection(direction.x, direction.y, direction.z)
            if rbp is not None:
                rbp.SetSpeedFraction(min(1.0, speed))
                if not initing and self.ball:
                    sm.GetService('logger').AddText('%s %s' % (mls.UI_INFLIGHT_SPEEDCHANGEDTO, self.FormatSpeed(speed * self.ball.maxVelocity)), 'notify')
                    sm.GetService('gameui').Say('%s %s' % (mls.UI_INFLIGHT_SPEEDCHANGEDTO, self.FormatSpeed(speed * self.ball.maxVelocity)))
        if not initing:
            self.wantedspeed = max(speed, 0.0)
        if not self.sr.speedtimer:
            self.sr.speedtimer = base.AutoTimer(133, self.UpdateSpeed)



    def SetPower(self, load, maxcap):
        if not self or not self.sr.powercore or self.sr.powercore.destroyed:
            return 
        if self.capacity is not None:
            portion = self.capacity * max(0.0, min(1.0, maxcap and float(load / maxcap) or maxcap))
            if portion:
                if self.sr.powercore and not self.sr.powercore.destroyed:
                    self.sr.powercore.hint = mls.UI_INFLIGHT_CAPACITORSTATUS % {'portion': portion / self.capacity * 100,
                     'left': portion,
                     'max': self.capacity}
        proportion = max(0.0, min(1.0, round(maxcap and load / maxcap or maxcap, 2)))
        if self.lastsetcapacitor == proportion:
            return 
        sm.ScatterEvent('OnCapacitorChange', load, maxcap, proportion)
        good = trinity.TriColor(*CELLCOLOR)
        bad = trinity.TriColor(70 / 256.0, 26 / 256.0, 13.0 / 256.0)
        bad.Scale(1.0 - proportion)
        good.Scale(proportion)
        if self.capacity is not None and self.capacitorDone and self.powerCells:
            totalCells = len(self.powerCells)
            visible = max(0, min(totalCells, int(proportion * totalCells)))
            for (ci, each,) in enumerate(self.powerCells):
                if ci >= visible:
                    each.SetRGB(0.5, 0.5, 0.5, 0.5)
                    each.glowColor = (0, 0, 0, 1)
                    each.glowFactor = 0.0
                    each.glowExpand = 0.1
                    each.shadowOffset = (0, 0)
                else:
                    each.SetRGB(0.125, 0.125, 0.125, 1)
                    each.glowColor = (bad.r + good.r,
                     bad.g + good.g,
                     bad.b + good.b,
                     1.0)
                    each.glowFactor = 0.0
                    each.glowExpand = 0.1
                    each.shadowOffset = (0, 1)

            if self.sr.powerblink is None:
                self.sr.powerblink = uicls.Sprite(parent=self, name='powerblink', state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/capacitorCellGlow.png', align=uiconst.CENTERTOP, blendMode=trinity.TR2_SBM_ADDX2, color=CELLCOLOR)
                (r, g, b,) = CELLCOLOR
                uicore.effect.BlinkSpriteRGB(self.sr.powerblink, r, g, b, 750, None)
            if visible != 0 and visible < totalCells:
                active = self.powerCells[(visible - 1)]
                uiutil.Transplant(self.sr.powerblink, active.parent, 0)
                self.sr.powerblink.top = active.top
                self.sr.powerblink.width = active.width + 3
                self.sr.powerblink.height = active.height
                self.sr.powerblink.state = uiconst.UI_DISABLED
            else:
                self.sr.powerblink.state = uiconst.UI_HIDDEN
            self.lastsetcapacitor = proportion



    def OnF(self, sidx, gidx):
        slot = self.sr.slotsByOrder.get((gidx, sidx), None)
        if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
            uthread.new(slot.sr.module.Click)
        else:
            uthread.new(eve.Message, 'Disabled')



    def OnFKeyOverload(self, sidx, gidx):
        slot = self.sr.slotsByOrder.get((gidx, sidx), None)
        if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
            if hasattr(slot.sr.module, 'ToggleOverload'):
                uthread.new(slot.sr.module.ToggleOverload)
        else:
            uthread.new(eve.Message, 'Disabled')



    def OnReloadAmmo(self):
        modulesByCharge = {}
        for module in self.sr.modules.itervalues():
            if not cfg.IsChargeCompatible(module.sr.moduleInfo):
                continue
            (chargeTypeID, chargeQuantity, roomForReload,) = module.GetChargeReloadInfo()
            if chargeTypeID in modulesByCharge:
                modulesByCharge[chargeTypeID].append(module)
            else:
                modulesByCharge[chargeTypeID] = [module]

        for (chargeTypeID, modules,) in modulesByCharge.iteritems():
            ammoList = {}
            for item in module.GetMatchingAmmo(modules[0].sr.moduleInfo.typeID, 1):
                if item.typeID == chargeTypeID and item.stacksize:
                    ammoList[item.itemID] = item.stacksize

            for module in modules:
                maxItemID = 0
                (chargeTypeID, chargeQuantity, roomForReload,) = module.GetChargeReloadInfo()
                bestItemID = None
                for (itemID, quant,) in ammoList.iteritems():
                    if quant >= roomForReload:
                        if not bestItemID or quant < ammoList[bestItemID]:
                            bestItemID = itemID
                    if not maxItemID or quant > ammoList[maxItemID]:
                        maxItemID = itemID

                bestItemID = bestItemID or maxItemID
                if bestItemID:
                    quant = min(roomForReload, ammoList[maxItemID])
                    uthread.new(module.AutoReload, 1, bestItemID, quant)
                    ammoList[bestItemID] -= quant






class Slot(uicls.Container):
    __guid__ = 'xtriui.Slot'

    def OnDropData(self, dragObj, nodes):
        flag1 = self.sr.slotFlag
        for node in nodes:
            decoClass = node.Get('__guid__', None)
            if decoClass == 'xtriui.ShipUIModule':
                flag2 = node.slotFlag
                if flag2 is not None:
                    uicore.layer.shipui.SwapSlots(flag1, node.slotFlag)
                break
            elif decoClass in ('xtriui.InvItem', 'listentry.InvItem'):
                item = node.rec
                if item.flagID == const.flagCargo and item.categoryID == const.categoryModule:
                    eve.GetInventoryFromId(eve.session.shipid).Add(item.itemID, item.locationID, qty=None, flag=flag1)
                break





class SpaceLayer(uicls.LayerCore):
    __guid__ = 'form.SpaceLayer'

    def OnCloseView(self):
        sm.GetService('tactical').CleanUp()
        sm.GetService('target').CleanUp()
        sm.GetService('bracket').CleanUp()



    def OnOpenView(self):
        pass




class NotifySettingsWindow(uicls.Window):
    __guid__ = 'form.NotifySettingsWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetWndIcon(None)
        self.SetTopparentHeight(0)
        self.SetCaption(mls.UI_GENERIC_NOTIFYSETTINGS)
        self.SetMinSize([320, 120])
        self.MakeUnResizeable()
        self.SetupUi()



    def SetupUi(self):
        notifydata = [{'checkboxLabel': mls.UI_GENERIC_NOTIFY_SHIELD,
          'checkboxName': 'shieldNotification',
          'checkboxSetting': 'shieldNotificationEnabled',
          'checkboxDefault': 1,
          'sliderName': 'shield',
          'sliderSetting': ('shieldThreshold', ('user', 'notifications'), const.defaultShieldThreshold)}, {'checkboxLabel': mls.UI_GENERIC_NOTIFY_ARMOUR,
          'checkboxName': 'armourNotification',
          'checkboxSetting': 'armourNotificationEnabled',
          'checkboxDefault': 1,
          'sliderName': 'armour',
          'sliderSetting': ('armourThreshold', ('user', 'notifications'), const.defaultArmourThreshold)}, {'checkboxLabel': mls.UI_GENERIC_NOTIFY_HULL,
          'checkboxName': 'hullNotification',
          'checkboxDefault': 1,
          'checkboxSetting': 'hullNotificationEnabled',
          'sliderName': 'hull',
          'sliderSetting': ('hullThreshold', ('user', 'notifications'), const.defaultHullThreshold)}]
        labelWidth = 150
        mainContainer = uicls.Container(name='mainContainer', parent=self.sr.main, align=uiconst.TOALL)
        for each in notifydata:
            notifytop = uicls.Container(name='notifytop', parent=mainContainer, align=uiconst.TOTOP, pos=(const.defaultPadding,
             const.defaultPadding,
             0,
             26))
            uicls.Checkbox(text=each['checkboxLabel'], parent=notifytop, configName=each['checkboxSetting'], retval=None, prefstype=('user', 'notifications'), checked=settings.user.notifications.Get(each['checkboxSetting'], each['checkboxDefault']), callback=self.CheckBoxChange, align=uiconst.TOLEFT, pos=(const.defaultPadding,
             0,
             labelWidth,
             0))
            _par = uicls.Container(name=each['sliderName'] + '_slider', align=uiconst.TORIGHT, width=labelWidth, parent=notifytop, pos=(10, 0, 160, 0))
            par = uicls.Container(name=each['sliderName'] + '_slider_sub', align=uiconst.TOTOP, parent=_par, pos=(0,
             const.defaultPadding,
             0,
             10))
            slider = xtriui.Slider(parent=par)
            lbl = uicls.Label(text='', parent=_par, align=uiconst.TOTOP, name='label', state=uiconst.UI_PICKCHILDREN, width=labelWidth, left=const.defaultPadding, top=1 + const.defaultPadding, fontsize=9, letterspace=2, tabs=[labelWidth - 22], uppercase=1, autowidth=False)
            lbl._tabMargin = 2
            slider.label = lbl
            slider.Startup(each['sliderName'], 0.0, 1.0, each['sliderSetting'], mls.UI_GENERIC_THRESHOLD)




    def CheckBoxChange(self, checkbox):
        if checkbox.name == 'shieldNotification':
            settings.user.notifications.Set('shieldNotificationEnabled', checkbox.checked)
        elif checkbox.name == 'armourNotification':
            settings.user.notifications.Set('armourNotificationEnabled', checkbox.checked)
        elif checkbox.name == 'hullNotification':
            settings.user.notifications.Set('hullNotificationEnabled', checkbox.checked)




class ShipUIContainer(uicls.Container):
    __guid__ = 'uicls.ShipUIContainer'
    default_left = 0
    default_top = 0
    default_width = 500
    default_height = 500
    default_name = 'shipui'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        overlayContainer = uicls.Container(parent=self, name='overlayContainer', pos=(0, 0, 256, 256), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)
        expandBtnRight = uicls.Sprite(parent=overlayContainer, name='expandBtnRight', pos=(170, 122, 28, 28), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/ShipUI/expandBtnRight.png')
        expandBtnLeft = uicls.Sprite(parent=overlayContainer, name='expandBtnLeft', pos=(56, 122, 28, 28), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/ShipUI/expandBtnLeft.png')
        optionsBtn = uicls.Icon(parent=overlayContainer, name='optionsBtn', pos=(180, 180, 16, 16), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, icon='ui_73_16_50')
        stopButton = uicls.Sprite(parent=overlayContainer, name='stopButton', pos=(72, 152, 18, 18), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/ShipUI/stopBtn.png')
        maxspeedButton = uicls.Sprite(parent=overlayContainer, name='maxspeedButton', pos=(164, 152, 18, 18), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/ShipUI/fullthrottleBtn.png')
        mainDot = uicls.Sprite(parent=self, name='mainDot', pos=(0, 0, 160, 160), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/mainDOT.png', spriteEffect=trinity.TR2_SFX_DOT, blendMode=trinity.TR2_SBM_ADD)
        mainContainer = uicls.Container(parent=self, name='mainContainer', pos=(0, 0, 256, 256), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)
        powercore = uicls.Container(parent=mainContainer, name='powercore', pos=(98, 97, 60, 60), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, pickRadius=30)
        subContainer = uicls.Container(parent=self, name='subContainer', pos=(0, 0, 160, 160), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)
        block_64 = uicls.Container(parent=subContainer, name='block_64', pos=(0, 0, 64, 64), align=uiconst.CENTER, state=uiconst.UI_NORMAL, pickRadius=32)
        circlepickclipper_92 = uicls.Container(parent=subContainer, name='circlepickclipper_92', pos=(0, 0, 92, 92), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN, pickRadius=46)
        heatPick = uicls.Container(parent=circlepickclipper_92, name='heatPick', pos=(0, 0, 92, 46), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        subpar = uicls.Container(parent=circlepickclipper_92, name='subpar', pos=(0, 0, 60, 80), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)
        powerPick = uicls.Container(parent=subpar, name='powerPick', pos=(6, 55, 48, 20), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        cpuPick = uicls.Container(parent=subpar, name='cpuPick', pos=(0, 70, 60, 20), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        block_88 = uicls.Container(parent=subContainer, name='block_88', pos=(0, 0, 88, 88), align=uiconst.CENTER, state=uiconst.UI_NORMAL, pickRadius=44)
        (color, bgColor, comp, compsub,) = sm.GetService('window').GetWindowColors()
        (r, g, b, a,) = color
        mainShape = uicls.Sprite(parent=self, name='shipuiMainShape', pos=(0, 0, 160, 160), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/mainUnderlay.png', color=(r,
         g,
         b,
         1))
        underMain = uicls.Container(parent=self, name='underMain', pos=(0, 0, 160, 160), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)
        divider = uicls.Sprite(parent=underMain, name='divider', pos=(56, 42, 46, 12), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/heatDivider.png')
        circlepickclipper_144 = uicls.Container(parent=underMain, name='circlepickclipper_144', pos=(8, 8, 144, 144), align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, pickRadius=-1)
        speedGaugeParent = uicls.Container(parent=circlepickclipper_144, name='speedGaugeParent', pos=(10, 72, 124, 68), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, clipChildren=True)
        speedNeedle = uicls.Transform(parent=speedGaugeParent, name='speedNeedle', pos=(-5, -6, 134, 12), align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, rotationCenter=(0.5, 0.5))
        needle = uicls.Sprite(parent=speedNeedle, name='needle', pos=(0, 0, 24, 12), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/heatGaugeNeedle.png')
        speedGaugeSprite = uicls.Sprite(parent=speedNeedle, name='speedGaugeSprite', texturePath='res:/UI/Texture/classes/ShipUI/speedoOverlay.png', pos=(-8, -73, 79, 79), state=uiconst.UI_DISABLED)
        speedoUnderlay = uicls.Sprite(parent=underMain, name='speedoUnderlay', pos=(0, 48, 104, 44), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/speedoUnderlay.png')
        heatLowUnderlay = uicls.Sprite(parent=underMain, name='heatLowUnderlay', pos=(36, 42, 27, 38), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/lowHeat_0.png')
        heatMedUnderlay = uicls.Sprite(parent=underMain, name='heatMedUnderlay', pos=(57, 36, 45, 18), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/medHeat_0.png')
        heatHiUnderlay = uicls.Sprite(parent=underMain, name='heatHiUnderlay', pos=(95, 42, 27, 38), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/hiHeat_0.png')
        slotsContainer = uicls.Container(parent=self, name='slotsContainer', pos=(0, 0, 1024, 512), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)




class ShipSlot(uicls.Container):
    __guid__ = 'xtriui.Slot'
    default_pickRadius = 24

    def OnDropData(self, dragObj, nodes):
        flag1 = self.sr.slotFlag
        for node in nodes:
            decoClass = node.Get('__guid__', None)
            if decoClass == 'xtriui.ShipUIModule':
                flag2 = node.slotFlag
                if flag2 is not None:
                    uicore.layer.shipui.SwapSlots(flag1, node.slotFlag)
                break
            elif decoClass in ('xtriui.InvItem', 'listentry.InvItem'):
                item = node.rec
                if item.flagID == const.flagCargo and item.categoryID == const.categoryModule:
                    eve.GetInventoryFromId(eve.session.shipid).Add(item.itemID, item.locationID, qty=None, flag=flag1)
                break




    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        stackParent = uicls.Container(parent=self, name='stackParent', pos=(14, 35, 12, 10), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)
        underlay = uicls.Sprite(parent=stackParent, name='underlay', pos=(0, 0, 0, 0), align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotStackUnderlay.png', color=(0.51, 0.0, 0.0, 1.0))
        quantityParent = uicls.Container(parent=self, name='quantityParent', pos=(26, 35, 24, 10), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)
        underlay = uicls.Sprite(parent=quantityParent, name='underlay', pos=(0, 0, 0, 0), align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotQuantityUnderlay.png', color=(0.0, 0.0, 0.0, 1.0))
        innerArea = uicls.Container(parent=self, name='innerArea', pos=(0, 0, 0, 0), align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        mainshape = uicls.Sprite(parent=innerArea, name='mainshape', pos=(0, 0, 0, 0), align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotMain.png')
        hilite = uicls.Sprite(parent=innerArea, name='hilite', padding=(10, 10, 10, 10), align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/slotHilite.png', blendMode=trinity.TR2_SBM_ADDX2)
        overloadBtn = uicls.Sprite(parent=self, name='overloadBtn', pos=(16, 6, 32, 16), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/ShipUI/slotOverloadDisabled.png')
        damageStatePickArea = uicls.Container(parent=self, name='damageStatePickArea', pos=(0, 0, 0, 0), align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        damageState = uicls.Sprite(parent=damageStatePickArea, name='damageState', pos=(0, 0, 64, 64), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/slotDamage_1.png')
        damageUnderlay = uicls.Sprite(parent=self, name='damageUnderlay', pos=(0, 0, 0, 0), align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotDamage_Base.png')
        ramps = uicls.Container(parent=self, name='ramps', pos=(0, 0, 64, 64), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)
        leftRampCont = uicls.Container(parent=ramps, name='leftRampCont', pos=(0, 0, 32, 64), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, clipChildren=True)
        leftRamp = uicls.Transform(parent=leftRampCont, name='leftRamp', pos=(0, 0, 64, 64), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        rampLeftSprite = uicls.Sprite(parent=leftRamp, name='rampLeftSprite', pos=(0, 0, 32, 64), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotRampLeft.png')
        leftShadowRamp = uicls.Transform(parent=leftRampCont, name='leftShadowRamp', pos=(0, 1, 64, 64), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        rampSprite = uicls.Sprite(parent=leftShadowRamp, name='rampSprite', pos=(0, 0, 32, 64), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotRampLeft.png', color=(0.0, 0.0, 0.0, 1.0))
        rightRampCont = uicls.Container(parent=ramps, name='rightRampCont', pos=(32, 0, 32, 64), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, clipChildren=True)
        rightRamp = uicls.Transform(parent=rightRampCont, name='rightRamp', pos=(-32, 0, 64, 64), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        rampRightSprite = uicls.Sprite(parent=rightRamp, name='rampRightSprite', pos=(32, 0, 32, 64), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotRampRight.png')
        rightShadowRamp = uicls.Transform(parent=rightRampCont, name='rightShadowRamp', pos=(-32, 1, 64, 64), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        rampSprite = uicls.Sprite(parent=rightShadowRamp, name='rampSprite', pos=(32, 0, 32, 64), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotRampRight.png', color=(0.0, 0.0, 0.0, 1.0))
        glow = uicls.Sprite(parent=self, name='glow', pos=(2, 2, 2, 2), align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/slotGlow.png', color=(0.24, 0.67, 0.16, 0.75))
        busy = uicls.Sprite(parent=self, name='busy', pos=(2, 2, 2, 2), align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/slotGlow.png', color=(1.0, 0.13, 0.0, 0.73))
        slot = uicls.Sprite(parent=self, name='slot', pos=(0, 0, 0, 0), align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotBase.png', color=(0.0, 0.0, 0.0, 0.38))
        groupHighlight = uicls.Container(parent=self, name='groupHighlight', pos=(0, 0, 64, 64), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)
        leftCircle = uicls.Sprite(parent=groupHighlight, name='leftCircle', pos=(0, 0, 32, 64), texturePath='res:/UI/Texture/classes/ShipUI/slotRampLeft.png')
        rightCircle = uicls.Sprite(parent=groupHighlight, name='leftCircle', pos=(32, 0, 32, 64), texturePath='res:/UI/Texture/classes/ShipUI/slotRampRight.png')




class LeftSideButton(uicls.Container):
    __guid__ = 'uicls.ShipUILeftSideButton'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.RELATIVE

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.btnName = attributes.btnName
        self.func = attributes.func
        self.cmdName = attributes.cmdName
        self.orgTop = None
        self.pickRadius = -1
        self.icon = uicls.Icon(parent=self, name='icon', pos=(0, 0, 32, 32), align=uiconst.CENTER, state=uiconst.UI_DISABLED, icon=attributes.iconNum)
        self.hilite = uicls.Sprite(parent=self, name='hilite', align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnBaseAndShadow.png', color=(0.63, 0.63, 0.63, 1.0), blendMode=trinity.TR2_SBM_ADD)
        slot = uicls.Sprite(parent=self, name='slot', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnBaseAndShadow.png')
        busy = uicls.Sprite(parent=self, name='busy', align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnGlow.png', color=(0.27, 0.72, 1.0, 0.53))



    def OnClick(self, *args):
        self.func()
        sm.GetService('ui').StopBlink(self.icon)



    def OnMouseDown(self, btn, *args):
        if getattr(self, 'orgTop', None) is None:
            self.orgTop = self.top
        self.top = self.orgTop + 2



    def OnMouseUp(self, *args):
        if getattr(self, 'orgTop', None) is not None:
            self.top = self.orgTop



    def OnMouseEnter(self, *args):
        self.hilite.state = uiconst.UI_DISABLED



    def OnMouseExit(self, *args):
        self.hilite.state = uiconst.UI_HIDDEN
        if getattr(self, 'orgTop', None) is not None:
            self.top = self.orgTop



    def GetHint(self):
        ret = self.btnName
        if self.cmdName:
            shortcut = uicore.cmd.GetShortcutStringByFuncName(self.cmdName)
            if shortcut:
                ret += ' [%s]' % shortcut
        return ret




