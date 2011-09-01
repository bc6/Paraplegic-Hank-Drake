import blue
import uthread
import uix
import uiutil
import util
import state
import base
import random
import _weakref
import uicls
import uiconst
import xtriui
accuracyThreshold = 0.8

class Target(uicls.Container):
    __guid__ = 'xtriui.Target'
    __notifyevents__ = ['ProcessShipEffect',
     'OnShowAccuracy',
     'OnStateChange',
     'OnJamStart',
     'OnJamEnd',
     'OnSlimItemChange',
     'OnDroneStateChange2',
     'OnDroneControlLost',
     'OnStateSetupChance',
     'OnSetPlayerStanding',
     'OnItemNameChange']

    def init(self):
        self.gaugesInited = 0
        self.gaugesVisible = 0
        self.lastDistance = None
        self.sr.gaugeParent = None
        self.sr.gauge_shield = None
        self.sr.gauge_armor = None
        self.sr.gauge_structure = None
        self.sr.updateTimer = None
        self.drones = {}
        self.timers = {}
        self.jammers = {}
        self.timerNames = {'propulsion': mls.UI_INFLIGHT_SCRAMBLINGSHORT,
         'electronic': mls.UI_INFLIGHT_JAMMINGSHORT,
         'unknown': mls.UI_INFLIGHT_MISCELLANEOUSSHORT}



    def Startup(self, slimItem):
        sm.RegisterNotify(self)
        obs = sm.GetService('target').IsObserving()
        self.ball = _weakref.ref(sm.GetService('michelle').GetBall(slimItem.itemID))
        self.slimItem = _weakref.ref(slimItem)
        self.wannalook = 1
        self.id = slimItem.itemID
        self.itemID = slimItem.itemID
        self.updatedamage = slimItem.categoryID != const.categoryAsteroid and slimItem.groupID != const.groupHarvestableCloud
        iconPar = uicls.Container(parent=self, width=64, height=64, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        icon = uicls.Icon(parent=iconPar, align=uiconst.TOALL, typeID=slimItem.typeID, size=64)
        self.sr.iconPar = iconPar
        self.slimForFlag = slimItem
        self.SetStandingIcon()
        self.sr.hilite = uicls.Fill(parent=iconPar, color=(1.0, 1.0, 1.0, 0.125), state=uiconst.UI_HIDDEN)
        self.sr.activeTarget = xtriui.ActiveTarget(parent=iconPar)
        rot = uiutil.GetChild(self.sr.activeTarget, 'rotate')
        sm.GetService('ui').Rotate(rot, 2.0)
        sm.GetService('ui').BlinkSpriteA(rot.children[0], 1.0, 500.0, 0)
        self.sr.diode = uicls.Fill(parent=self, color=(0.0, 1.0, 0.0, 1.0), align=uiconst.TOLEFT, width=6, state=uiconst.UI_HIDDEN)
        self.InRangeHide()
        self.sr.label = uicls.Label(text=' ', parent=self, left=[0, 74][obs], top=68, width=[96, 128][obs], autowidth=False, state=uiconst.UI_DISABLED, fontsize=[9, 14][obs], letterspace=[1, 0][obs], uppercase=[1, 0][obs])
        self.SetTargetLabel()
        self.sr.assigned = uicls.Container(name='assigned', align=uiconst.TOPLEFT, parent=self, width=32, height=128, left=64)
        self.sr.updateTimer = base.AutoTimer(random.randint(750, 1000), self.UpdateData)
        self.UpdateData()
        selected = sm.GetService('state').GetExclState(state.selected)
        self.Select(selected == slimItem.itemID)
        hilited = sm.GetService('state').GetExclState(state.mouseOver)
        self.Hilite(hilited == slimItem.itemID)
        activeTargetID = sm.GetService('target').GetActiveTargetID()
        self.ActiveTarget(activeTargetID == slimItem.itemID)
        drones = sm.GetService('michelle').GetDrones()
        for key in drones:
            droneState = drones[key]
            if droneState.targetID == self.id:
                self.drones[droneState.droneID] = droneState.typeID

        self.UpdateDrones()



    def OnItemNameChange(self, *args):
        uthread.new(self.SetTargetLabel)



    def SetTargetLabel(self):
        obs = sm.GetService('target').IsObserving()
        self.label = uix.GetSlimItemName(self.slimForFlag)
        if self.slimForFlag.corpID:
            self.label += ' [%s]' % cfg.corptickernames.Get(self.slimForFlag.corpID).tickerName
        if obs:
            self.label = sm.GetService('bracket').DisplayName(self.slimForFlag, uix.GetSlimItemName(self.slimForFlag))
        self.UpdateData()



    def OnSetPlayerStanding(self, *args):
        self.SetStandingIcon()



    def OnStateSetupChance(self, *args):
        self.SetStandingIcon()



    def SetStandingIcon(self):
        stateMgr = sm.GetService('state')
        flag = stateMgr.CheckStates(self.slimForFlag, 'flag')
        self.standingIcon = uix.SetStateFlagForFlag(self, flag, top=51, left=36, showHint=False)



    def OnSlimItemChange(self, oldSlim, newSlim):
        uthread.new(self._OnSlimItemChange, oldSlim, newSlim)



    def _OnSlimItemChange(self, oldSlim, newSlim):
        if self.itemID != oldSlim.itemID or self.destroyed:
            return 
        self.itemID = newSlim.itemID
        self.slimItem = _weakref.ref(newSlim)
        if oldSlim.corpID != newSlim.corpID or oldSlim.charID != newSlim.charID:
            self.label = uix.GetSlimItemName(newSlim)
            self.UpdateData()



    def OnStateChange(self, itemID, flag, true, *args):
        if not self.destroyed:
            uthread.new(self._OnStateChange, itemID, flag, true)



    def _OnStateChange(self, itemID, flag, true):
        if self.destroyed or self.itemID != itemID:
            return 
        if flag == state.mouseOver:
            self.Hilite(true)
        elif flag == state.selected:
            self.Select(true)
        elif flag == state.activeTarget:
            self.ActiveTarget(true)



    def Hilite(self, state):
        if self.sr.hilite:
            self.sr.hilite.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][state]



    def Select(self, state):
        pass



    def OnJamStart(self, sourceBallID, moduleID, targetBallID, jammingType, startTime, duration):
        if jammingType not in self.jammers:
            self.jammers[jammingType] = {}
        self.jammers[jammingType][(sourceBallID, moduleID, targetBallID)] = (startTime, duration)
        self.CheckJam()



    def OnJamEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        if self and not self.destroyed and hasattr(self, 'jammers'):
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
                if targetBallID == self.id:
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
                self.ShowTimer(jammingType, startTime, duration, self.timerNames.get(jammingType, '???'))
            else:
                self.KillTimer(jammingType)




    def ShowTimer(self, timerID, startTime, duration, label):
        check = self.GetTimer(timerID)
        if check:
            if check.endTime <= startTime + duration:
                check.Close()
            else:
                return 
        timer = uicls.Container(name='%s' % timerID, parent=self.sr.gaugeParent, align=uiconst.TOTOP, height=8)
        timer.endTime = startTime + duration
        timer.timerID = timerID
        self.ArrangeGauges()
        uicls.Container(name='push', parent=timer, align=uiconst.TOBOTTOM, height=1)
        t1 = uicls.Label(text=label, parent=timer, left=68, top=-1, state=uiconst.UI_DISABLED, fontsize=9, letterspace=1, uppercase=1)
        uicls.Line(parent=timer, align=uiconst.TOTOP, color=(1.0, 1.0, 1.0, 0.5))
        uicls.Line(parent=timer, align=uiconst.TOBOTTOM, color=(1.0, 1.0, 1.0, 0.5))
        uicls.Line(parent=timer, align=uiconst.TOLEFT, color=(1.0, 1.0, 1.0, 0.5))
        uicls.Line(parent=timer, align=uiconst.TORIGHT, color=(1.0, 1.0, 1.0, 0.5))
        t = uicls.Label(text='', parent=timer, left=5, top=0, fontsize=9, letterspace=1, state=uiconst.UI_NORMAL)
        p = uicls.Fill(parent=timer, align=uiconst.TOLEFT)
        timer.height = max(8, t.textheight - 2, t1.textheight - 2)
        duration = float(duration)
        while 1 and not timer.destroyed:
            now = blue.os.GetTime()
            dt = blue.os.TimeDiffInMs(startTime, now)
            timeLeft = (duration - dt) / 1000.0
            timer.timeLeft = timeLeft
            if timer.destroyed or dt > duration:
                t.text = mls.UI_GENERIC_DONE
                p.width = 0
                break
            t.text = '%.1f %s' % (timeLeft, uix.Plural(timeLeft, 'UI_GENERIC_SECONDSHORT'))
            p.width = int(62 * ((duration - dt) / duration))
            timer.height = max(8, t.textheight - 2)
            blue.pyos.synchro.Yield()

        blue.pyos.synchro.Sleep(250)
        if not timer.destroyed and not self.destroyed:
            t.text = ''
            blue.pyos.synchro.Sleep(250)
        if not timer.destroyed and not self.destroyed:
            t.text = mls.UI_GENERIC_DONE
            blue.pyos.synchro.Sleep(250)
        if not timer.destroyed and not self.destroyed:
            t.text = ''
            blue.pyos.synchro.Sleep(250)
        if not timer.destroyed and not self.destroyed:
            t.text = mls.UI_GENERIC_DONE
            blue.pyos.synchro.Sleep(250)
        if not timer.destroyed and not self.destroyed:
            t.text = ''
            timer.Close()
        if not self.destroyed:
            self.ArrangeGauges()



    def KillTimer(self, timerID):
        timer = self.GetTimer(timerID)
        if timer:
            timer.Close()



    def GetTimer(self, timerID):
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('gaugeParent') and hasattr(self.sr.gaugeParent, 'children'):
            for each in self.sr.gaugeParent.children:
                if each.name == '%s' % timerID:
                    return each

        else:
            return None



    def ArrangeGauges(self):
        if self.gaugesInited:
            self.sr.gaugeParent.height = sum([ each.height for each in self.sr.gaugeParent.children if each.state != uiconst.UI_HIDDEN ])
            self.sr.label.top = self.sr.gaugeParent.top + self.sr.gaugeParent.height + 5



    def UpdateDamage(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            self.sr.updateTimer = None
            return 
        dmg = bp.GetDamageState(self.itemID)
        if dmg is not None:
            self.SetDamageState(dmg)



    def SetDamageState(self, state):
        self.InitGauges()
        visible = 0
        for (i, gauge,) in enumerate((self.sr.gauge_shield, self.sr.gauge_armor, self.sr.gauge_structure)):
            if state[i] is None:
                gauge.state = uiconst.UI_HIDDEN
            else:
                (l, t, w, h,) = gauge.GetAbsolute()
                gauge.sr.bar.width = max(int((w - 2) * state[i]), 0)
                gauge.state = uiconst.UI_DISABLED
                visible += 1

        self.gaugesVisible = visible
        self.ArrangeGauges()



    def InitGauges(self):
        if self.gaugesInited:
            self.sr.gaugeParent.state = uiconst.UI_NORMAL
            return 
        obs = sm.GetService('target').IsObserving()
        if obs:
            par = uicls.Container(name='gauges', parent=self, align=uiconst.TOPLEFT, width=64, height=32, top=0, left=74, state=uiconst.UI_NORMAL)
        else:
            par = uicls.Container(name='gauges', parent=self, align=uiconst.TOPLEFT, width=66, height=32, top=66, left=0, state=uiconst.UI_NORMAL)
        for each in ('SHIELD', 'ARMOR', 'STRUCTURE'):
            g = uicls.Container(name='gauge_%s' % each.lower(), parent=par, align=uiconst.TOTOP, height=6, top=2)
            t = uicls.Label(text=getattr(mls, 'UI_GENERIC_' + each + 'SHORT', each), parent=g, left=68, top=-1, state=uiconst.UI_DISABLED, fontsize=9, letterspace=1)
            g.height = max(6, t.textheight - 4)
            barpar = uicls.Container(name='barpar', parent=g, align=uiconst.TOALL, left=1, top=1, width=1, height=1)
            g.sr.bar = uicls.Fill(parent=barpar, align=uiconst.TOLEFT)
            uicls.Fill(parent=barpar, color=(158 / 256.0,
             11 / 256.0,
             14 / 256.0,
             1.0))
            uicls.Frame(parent=g, color=(1.0, 1.0, 1.0, 0.5))
            setattr(self.sr, 'gauge_%s' % each.lower(), g)

        uicls.Container(name='push', parent=par, align=uiconst.TOTOP, height=2)
        self.sr.gaugeParent = par
        self.gaugesInited = 1
        self.ArrangeGauges()



    def GetShipID(self):
        return self.itemID



    def GetIcon(self, icon, typeID, size):
        if not self.destroyed:
            icon.LoadIconByTypeID(typeID)
            icon.SetSize(size, size)



    def _OnClose(self, *args):
        sm.UnregisterNotify(self)
        self.sr.updateTimer = None
        self.sr.hoverTimer = None



    def ProcessShipEffect(self, godmaStm, effectState):
        slimItem = self.slimItem()
        if slimItem and effectState.environment[3] == slimItem.itemID:
            if effectState.start:
                if self.GetWeapon(effectState.itemID):
                    return 
                moduleInfo = self.GetModuleInfo(effectState.itemID)
                if moduleInfo:
                    self.AddWeapon(moduleInfo)
            else:
                self.RemoveWeapon(effectState.itemID)



    def AddWeapon(self, moduleInfo):
        if self is None or self.destroyed:
            return 
        icon = uicls.Icon(parent=self.sr.assigned, align=uiconst.RELATIVE, width=16, height=16, state=uiconst.UI_HIDDEN, typeID=moduleInfo.typeID, size=32)
        icon.sr.moduleID = moduleInfo.itemID
        icon.OnClick = (self.ClickWeapon, icon)
        self.ArrangeWeapons()



    def ClickWeapon(self, icon):
        shipui = uicore.layer.shipui
        if shipui:
            module = shipui.GetModule(icon.sr.moduleID)
            if module:
                module.Click()



    def IsEffectActivatible(self, effect):
        return effect.isDefault and effect.effectName != 'online' and effect.effectCategory in (const.dgmEffActivation, const.dgmEffTarget)



    def RemoveWeapon(self, moduleID):
        icon = self.GetWeapon(moduleID)
        if icon:
            icon.Close()
        self.ArrangeWeapons()



    def ArrangeWeapons(self):
        if self and not self.destroyed and self.sr.assigned:
            size = [32, 16][(len(self.sr.assigned.children) > 2)]
            left = 0
            top = 0
            for icon in self.sr.assigned.children:
                icon.width = icon.height = size
                icon.left = left
                icon.top = top
                top += size
                if top == 64:
                    top = 0
                    left += size
                icon.state = uiconst.UI_NORMAL




    def GetWeapon(self, moduleID):
        if self is None or self.destroyed:
            return 
        if self.sr.assigned:
            for each in self.sr.assigned.children:
                if each.sr.moduleID == moduleID:
                    return each




    def GetModuleInfo(self, moduleID):
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        if ship is None:
            return 
        for module in ship.modules:
            if module.itemID == moduleID:
                return module




    def OnClick(self, *args):
        self.wannalook = 0
        sm.GetService('state').SetState(self.itemID, state.selected, 1)
        sm.GetService('state').SetState(self.itemID, state.activeTarget, 1)
        sm.GetService('menu').TacticalItemClicked(self.itemID)



    def OnMouseUp(self, btn):
        self.wannalook = 1



    def GetMenu(self):
        obs = sm.GetService('target').IsObserving()
        m = []
        if obs:
            m += [('Toggle Team', sm.GetService('target').ToggleTeam, (self.itemID,))]
            m += [('Move Up', sm.GetService('target').MoveUp, (self.itemID,))]
            m += [('Move Down', sm.GetService('target').MoveDown, (self.itemID,))]
        m += sm.GetService('menu').CelestialMenu(self.itemID)
        return m



    def OnMouseHover(self, *args):
        pass



    def OnMouseDown(self, *args):
        pass



    def OnMouseEnter(self, *args):
        sm.GetService('state').SetState(self.id, state.mouseOver, 1)
        self.sr.hoverTimer = base.AutoTimer(3000, self.Hover)



    def Hover(self):
        if uicore.uilib.mouseOver == self and self.wannalook:
            uiutil.SetOrder(self, 0)
            sm.GetService('target').SetAsInterest(self.itemID)



    def OnMouseExit(self, *args):
        sm.GetService('state').SetState(self.itemID, state.mouseOver, 0)
        sm.GetService('target').SetAsInterest(None)
        self.sr.hoverTimer = None



    def UpdateData(self):
        ball = self.ball()
        if not ball:
            return 
        obs = sm.GetService('target').IsObserving()
        if not obs:
            dist = ball.surfaceDist
            self.sr.label.text = '%s<br>%s' % (self.label, util.FmtDist(dist))
        else:
            self.sr.label.text = '%s' % self.label
        if self.updatedamage:
            self.UpdateDamage()



    def ActiveTarget(self, true):
        if self.destroyed:
            return 
        if true and not sm.GetService('target').IsObserving():
            self.sr.iconPar.width = self.sr.iconPar.height = 56
            self.sr.iconPar.left = self.sr.iconPar.top = 5
            self.sr.activeTarget.state = uiconst.UI_DISABLED
        else:
            self.sr.iconPar.width = self.sr.iconPar.height = 64
            self.sr.iconPar.left = self.sr.iconPar.top = 1
            self.sr.activeTarget.state = uiconst.UI_HIDDEN



    def OnShowAccuracy(self, method = None):
        if not self or self.destroyed:
            return 
        if method:
            self.SetAccuracy(method(self.itemID))
        else:
            self.SetAccuracy(None)



    def SetAccuracy(self, acc):
        if self.destroyed:
            return 
        if acc is None:
            self.InRangeHide()
        elif acc[0] >= accuracyThreshold:
            self.InRangeOn()
        else:
            self.InRangeOff()



    def InRangeOn(self):
        self.sr.diode.state = uiconst.UI_DISABLED



    def InRangeOff(self):
        self.sr.diode.state = uiconst.UI_DISABLED



    def InRangeHide(self):
        self.sr.diode.state = uiconst.UI_HIDDEN



    def OnDroneStateChange2(self, itemID, oldActivityState, activityState):
        michelle = sm.GetService('michelle')
        droneState = michelle.GetDroneState(itemID)
        if activityState in (const.entityCombat, const.entityEngage, const.entityMining):
            if droneState.targetID == self.id:
                self.drones[itemID] = droneState.typeID
            elif self.drones.has_key(itemID):
                del self.drones[itemID]
        elif self.drones.has_key(itemID):
            del self.drones[itemID]
        self.UpdateDrones()



    def OnDroneControlLost(self, droneID):
        if self.drones.has_key(droneID):
            del self.drones[droneID]
        self.UpdateDrones()



    def UpdateDrones(self):
        if not self.drones:
            self.RemoveWeapon('drones')
            return 
        droneIcon = self.GetWeapon('drones')
        if not droneIcon:
            icon = uicls.Sprite(align=uiconst.RELATIVE, width=16, height=16, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/Icons/56_64_5.png', parent=self.sr.assigned)
            icon.sr.moduleID = 'drones'
            self.ArrangeWeapons()
        self.UpdateDroneHint()



    def UpdateDroneHint(self):
        dronesByTypeID = {}
        droneIcon = self.GetWeapon('drones')
        for (droneID, droneTypeID,) in self.drones.iteritems():
            if not dronesByTypeID.has_key(droneTypeID):
                dronesByTypeID[droneTypeID] = 0
            dronesByTypeID[droneTypeID] += 1

        string = mls.UI_GENERIC_DRONES
        for (droneTypeID, number,) in dronesByTypeID.iteritems():
            typeName = cfg.invtypes.Get(droneTypeID).typeName
            string += '<br>'
            string += typeName
            string += ': '
            string += str(number)

        droneIcon.hint = string




