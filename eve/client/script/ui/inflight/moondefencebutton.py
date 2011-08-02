import uthread
import uix
import base
import util
import blue
import re
import state
import random
import uiutil
import uicls
import uiconst
import log
cgre = re.compile('chargeGroup\\d{1,2}')

class DefenceStructureButton(uicls.Container):
    __guid__ = 'xtriui.DefenceStructureButton'
    __notifyevents__ = ['OnStateChange',
     'ProcessGodmaLocationPrimed',
     'OnGodmaItemChange',
     'OnTargetOBO',
     'OnAttribute',
     'OnStructureTargetAdded',
     'OnStructureTargetRemoved',
     'OnSlimItemChange',
     'UpdateItem']
    __update_on_reload__ = 1
    __cgattrs__ = []
    __loadingcharges__ = []
    __chargesizecache__ = {}

    def _OnClose(self):
        if self.invCookie:
            sm.GetService('inv').Unregister(self.invCookie)
        uicls.Container._OnClose(self)



    def init(self):
        self.Reset()
        sm.RegisterNotify(self)



    def Reset(self):
        self.def_effect = None
        self.charge = None
        self.target = None
        self.waitingForActiveTarget = 0
        self.blockOntarget = 0
        self.online = False
        self.goingOnline = 0
        self.sr.accuracyTimer = None
        self.quantity = None
        self.invReady = 1
        self.invCookie = None
        self.isInvItem = 1
        self.blinking = 0
        self.effect_activating = 0
        self.typeName = ''
        self.dogmaLM = None
        self.sr.sourceIcon = None
        self.sr.sourceGaugeParent = None
        self.sr.sourceGauge_shield = None
        self.sr.sourceGauge_armor = None
        self.sr.sourceGauge_structure = None
        self.sr.sourceUpdateTimer = None
        self.sr.sourceID = None
        self.sr.sourceGlow = None
        self.sr.sourceBusy = None
        self.sr.sourceQtyParent = None
        self.sourceGaugesInited = 0
        self.sourceGaugesVisible = 0
        self.id = None
        self.sr.targetIcon = None
        self.sr.targetGaugeParent = None
        self.sr.targetGauge_shield = None
        self.sr.targetGauge_armor = None
        self.sr.targetGauge_structure = None
        self.sr.targetUpdateTimer = None
        self.sr.targetID = None
        self.targetGaugesInited = 0
        self.targetGaugesVisible = 0
        self.sr.distanceUpdateTimer = None



    def Setup(self, moduleinfo):
        targetContainer = uicls.Container(name='targetCont', align=uiconst.TOPLEFT, parent=self, top=0, height=64, width=64)
        slot = DefenceModuleButton(parent=targetContainer, idx=0)
        self.sr.targetIcon = uiutil.GetChild(targetContainer, 'iconSprite')
        self.sr.targetContainer = targetContainer
        self.sr.targetContainer.state = uiconst.UI_DISABLED
        sourceContainer = uicls.Container(name='sourceCont', align=uiconst.TOPLEFT, parent=self, top=targetContainer.height + 22, height=64, width=64)
        slot = DefenceModuleButton(parent=sourceContainer, idx=0)
        self.sr.sourceIcon = uiutil.GetChild(sourceContainer, 'iconSprite')
        self.sr.sourceIcon.state = uiconst.UI_DISABLED
        self.sr.glow = uiutil.GetChild(sourceContainer, 'glow')
        self.sr.busy = uiutil.GetChild(sourceContainer, 'busy')
        self.sr.quantityParent = uiutil.GetChild(sourceContainer, 'quantityParent')
        idx = self.parent.children.index(self)
        fill = uicls.Fill(parent=self, color=(1.0, 1.0, 1.0, 0.125), state=uiconst.UI_HIDDEN, idx=idx)
        self.sr.hilite = fill
        self.sr.sourceContainer = sourceContainer
        self.sr.sourceContainer.state = uiconst.UI_DISABLED
        chargeIcon = uicls.Icon(parent=sourceContainer, align=uiconst.RELATIVE, top=32, left=6, size=24, idx=0, state=uiconst.UI_HIDDEN, ignoreSize=True)
        self.sr.chargeIcon = chargeIcon
        if not len(self.__cgattrs__):
            self.__cgattrs__.extend([ a.attributeID for a in cfg.dgmattribs if cgre.match(a.attributeName) is not None ])
        invType = cfg.invtypes.Get(moduleinfo.typeID)
        group = cfg.invtypes.Get(moduleinfo.typeID).Group()
        self.sr.moduleInfo = moduleinfo
        self.locationFlag = moduleinfo.flagID
        self.sr.sourceID = moduleinfo.itemID
        self.id = moduleinfo.itemID
        self.typeName = uix.GetItemName(self.sr.moduleInfo)
        self.sr.glow.z = 0
        self.sr.qtylabel = uicls.Label(text='', parent=self.sr.quantityParent, left=2, top=0, width=30, height=9, letterspace=1, fontsize=9, state=uiconst.UI_DISABLED, uppercase=1, idx=0, autoheight=False, autowidth=False)
        self.sr.distancelabel = uicls.Label(text='', parent=self.sr.targetContainer, left=12, top=-16, width=70, height=9, letterspace=1, fontsize=9, state=uiconst.UI_DISABLED, uppercase=1, idx=0, autoheight=False, autowidth=False)
        if cfg.IsChargeCompatible(moduleinfo):
            self.invCookie = sm.GetService('inv').Register(self)
        self.SetCharge(None)
        for key in moduleinfo.effects.iterkeys():
            effect = moduleinfo.effects[key]
            if self.IsEffectActivatible(effect):
                self.def_effect = effect
                if effect.isActive:
                    self.SetActive()
            if effect.effectName == 'online':
                if effect.isActive:
                    self.ShowOnline()
                else:
                    self.ShowOffline()

        self.state = uiconst.UI_NORMAL
        currentTarget = self.GetCurrentTarget()
        if currentTarget is not None:
            uthread.pool('DefenceMobuleButton::OnTargetAdded::', self.OnTargetAdded, currentTarget)
        self.sr.sourceUpdateTimer = base.AutoTimer(random.randint(750, 1000), self.UpdateData, 'source')
        self.UpdateData('source')
        self.sr.targetUpdateTimer = base.AutoTimer(random.randint(750, 1000), self.UpdateData, 'target')
        self.UpdateData('target')
        self.UpdateDistance()
        self.sr.distanceUpdateTimer = base.AutoTimer(random.randint(5000, 6000), self.UpdateDistance)
        self.Draggable_blockDrag = 0
        uthread.new(self.BlinkIcon)



    def HideGauge(self, loc):
        gaugeParent = None
        if getattr(self, '%sGaugesInited' % loc, None):
            gaugeParent = self.sr.Get('%sGaugeParent' % loc)
            gaugeParent.state = uiconst.UI_HIDDEN
            self.sr.distancelabel.state = uiconst.UI_HIDDEN



    def ShowGauge(self, loc):
        gaugeParent = None
        if getattr(self, '%sGaugesInited' % loc, None):
            gaugeParent = self.sr.Get('%sGaugeParent' % loc)
            gaugeParent.state = uiconst.UI_DISABLED
            self.sr.distancelabel.state = uiconst.UI_DISABLED



    def InitGauges(self, loc):
        if getattr(self, '%sGaugesInited' % loc, None):
            gaugeParent = self.sr.Get('%sGaugeParent' % loc)
            gaugeParent.state = uiconst.UI_NORMAL
            return 
        container = self.sr.Get('%sContainer' % loc)
        par = uicls.Container(name='gauges', parent=container, align=uiconst.TOPLEFT, width=52, height=32, top=59, left=6)
        for each in ('SHIELD', 'ARMOR', 'STRUCTURE'):
            g = uicls.Container(name=each, align=uiconst.TOTOP, width=52, height=8, left=-2)
            uicls.Container(name='push', parent=g, align=uiconst.TOBOTTOM, height=1)
            g.name = '%sGauge_%s' % (loc, each.lower())
            g.height = 9
            uicls.Line(parent=g, align=uiconst.TOTOP, color=(1.0, 1.0, 1.0, 0.5))
            uicls.Line(parent=g, align=uiconst.TOBOTTOM, color=(1.0, 1.0, 1.0, 0.5))
            uicls.Line(parent=g, align=uiconst.TOLEFT, color=(1.0, 1.0, 1.0, 0.5))
            uicls.Line(parent=g, align=uiconst.TORIGHT, color=(1.0, 1.0, 1.0, 0.5))
            g.sr.bar = uicls.Fill(parent=g, align=uiconst.TOLEFT)
            uicls.Fill(parent=g, color=(158 / 256.0,
             11 / 256.0,
             14 / 256.0,
             1.0))
            par.children.append(g)
            setattr(self.sr, '%sGauge_%s' % (loc, each.lower()), g)

        uicls.Container(name='push', parent=par, align=uiconst.TOTOP, height=2)
        self.sr.gaugeParent = par
        setattr(self.sr, '%sGaugeParent' % loc, par)
        setattr(self, '%sGaugesInited' % loc, 1)



    def UpdateDistance(self):
        sourceID = self.sr.Get('sourceID', None)
        targetID = self.sr.Get('targetID', None)
        if not sourceID and not targetID:
            return 
        sourceBall = sm.GetService('michelle').GetBall(sourceID)
        if not sourceBall:
            return 
        targetBall = sm.GetService('michelle').GetBall(targetID)
        if not targetBall:
            return 
        bp = sm.GetService('michelle').GetBallpark()
        dist = bp.DistanceBetween(sourceID, targetID)
        self.sr.distancelabel.text = util.FmtDist(dist)
        self.sr.distancelabel.left = self.width / 2 - self.sr.distancelabel.textwidth / 2



    def UpdateData(self, loc):
        itemID = self.sr.Get('%sID' % loc, None)
        if not itemID:
            return 
        ball = sm.GetService('michelle').GetBall(itemID)
        if not ball:
            return 
        self.UpdateDamage(loc)



    def UpdateDamage(self, loc):
        itemID = self.sr.Get('%sID' % loc, None)
        if not itemID:
            return 
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            setattr(self.sr, '%sUpdateTimer' % loc, None)
            return 
        dmg = bp.GetDamageState(itemID)
        if dmg is not None:
            self.SetDamageState(dmg, loc)



    def OnSlimItemChange(self, oldSlim, newSlim):
        if self.destroyed or self.sr.targetID != oldSlim.itemID and self.sr.sourceID != oldSlim.itemID:
            return 
        if self.sr.sourceID != oldSlim.itemID:
            self.UpdateData('source')
        elif self.sr.targetID != oldSlim.itemID:
            self.UpdateData('target')



    def SetDamageState(self, state, loc):
        self.InitGauges(loc)
        visible = 0
        ref = [self.sr.Get('%sGauge_shield' % loc, None), self.sr.Get('%sGauge_armor' % loc, None), self.sr.Get('%sGauge_structure' % loc, None)]
        for (i, gauge,) in enumerate(ref):
            if gauge is None:
                continue
            if state[i] is None:
                gauge.state = uiconst.UI_HIDDEN
            else:
                gauge.sr.bar.width = int((gauge.width - 2) * state[i])
                gauge.state = uiconst.UI_DISABLED
                visible += 1

        setattr(self, '%sGaugesVisible' % loc, visible)



    def SetCharge(self, charge):
        self.sr.sourceIcon.LoadIconByTypeID(self.sr.moduleInfo.typeID, ignoreSize=True)
        self.sr.sourceIcon.SetSize(48, 48)
        self.sr.sourceIcon.state = uiconst.UI_DISABLED
        if charge and charge.stacksize > 0:
            if self.charge is None or charge.typeID != self.charge.typeID:
                self.sr.chargeIcon.LoadIconByTypeID(charge.typeID, ignoreSize=True)
                self.sr.chargeIcon.SetSize(24, 24)
                self.sr.chargeIcon.state = uiconst.UI_DISABLED
            self.charge = charge
            self.UpdateChargeQuantity(charge)
            self.sr.qtylabel.parent.state = uiconst.UI_DISABLED
        else:
            self.sr.chargeIcon.state = uiconst.UI_HIDDEN
            self.sr.qtylabel.parent.state = uiconst.UI_HIDDEN
            self.quantity = 0
            self.sr.sourceID = self.sr.moduleInfo.itemID
            self.charge = None
        self.CheckOnline()



    def UpdateChargeQuantity(self, charge):
        if charge is self.charge:
            self.quantity = charge.stacksize
            self.sr.qtylabel.text = '%s' % util.FmtAmt(charge.stacksize)



    def SetDamage(self, damage):
        pass



    def GetVolume(self):
        if self.charge:
            return cfg.GetItemVolume(self.charge, 1)



    def GetShell(self):
        return eve.GetInventoryFromId(eve.session.shipid)



    def BlinkIcon(self):
        if self.destroyed or self.blinking:
            return 
        self.blinking = 1
        while self.waitingForActiveTarget or self.goingOnline:
            blue.pyos.synchro.Sleep(250)
            if self.destroyed:
                return 
            self.sr.sourceIcon.color.a = 0.25
            blue.pyos.synchro.Sleep(250)
            if self.destroyed:
                return 
            self.sr.sourceIcon.color.a = 1.0

        if self.destroyed:
            return 
        self.blinking = 0
        self.CheckOnline()



    def CopyItemIDToClipboard(self, itemID):
        blue.pyos.SetClipboardData(str(itemID))



    def GetMenu(self):
        if self.destroyed:
            return 
        m = []
        if self.sr.Get('sourceID', None):
            m += [(mls.UI_INFLIGHT_SOURCE, sm.GetService('menu').CelestialMenu(self.sr.sourceID))]
            m += [None]
        if self.sr.Get('targetID', None):
            m += [(mls.UI_GENERIC_TARGET, sm.GetService('menu').CelestialMenu(self.sr.targetID))]
        return m



    def ProcessGodmaLocationPrimed(self, structureID):
        structs = sm.GetService('pwn').GetCurrentControl()
        if structs.has_key(structureID):
            item = sm.services['godma'].GetItem(structureID)
            if item.groupID == const.groupMobileLaserSentry:
                if len(item.modules) == 0:
                    self.SetCharge(None)
                else:
                    self.SetCharge(item.modules[0])



    def CheckPending(self):
        shiplayer = uicore.layer.shipui
        if not shiplayer:
            return 
        blue.pyos.synchro.Sleep(1000)
        shiplayer.CheckPendingReloads()



    def CheckOnline(self, sound = 0):
        if not self or self.destroyed:
            return 
        else:
            self.ShowOnline()
            return 
        for key in self.sr.moduleInfo.effects.keys():
            effect = self.sr.moduleInfo.effects[key]
            if effect.effectName == 'online':
                if effect.isActive:
                    self.ShowOnline()
                    if sound:
                        eve.Message('OnLogin')
                else:
                    self.ShowOffline()
                return 




    def ChangeOnline(self, on = 1):
        uthread.new(self._ChangeOnline, on)



    def _ChangeOnline(self, on):
        if not on and eve.Message('PutOffline', {}, uiconst.YESNO) != uiconst.ID_YES:
            return 
        for key in self.sr.moduleInfo.effects.keys():
            effect = self.sr.moduleInfo.effects[key]
            if effect.effectName == 'online':
                if on:
                    effect.Activate()
                    self.goingOnline = 1
                    uthread.new(self.BlinkIcon)
                    blue.pyos.synchro.Sleep(5000)
                    self.goingOnline = 0
                else:
                    self.ShowOffline(1)
                    effect.Deactivate()
                return 




    def ShowOnline(self):
        self.online = True
        if not self.goingOnline:
            self.sr.sourceIcon.color.a = 1.0



    def ShowOffline(self, ping = 0):
        self.online = False
        self.goingOnline = 0
        self.sr.sourceIcon.color.a = 0.25
        if ping:
            eve.Message('OnLogin')
        self.state = uiconst.UI_NORMAL



    def IsEffectRepeatable(self, effect, activatibleKnown = 0):
        if activatibleKnown or self.IsEffectActivatible(effect):
            if not effect.item.disallowRepeatingActivation:
                return effect.durationAttributeID is not None
        return 0



    def IsEffectActivatible(self, effect):
        return effect.isDefault and effect.effectName != 'online' and effect.effectCategory in (const.dgmEffActivation, const.dgmEffTarget)



    def GetDefaultEffect(self):
        if self.sr.moduleInfo is None or sm.GetService('godma').GetItem(self.sr.sourceID) is None:
            return 
        for key in self.sr.moduleInfo.effects.iterkeys():
            effect = self.sr.moduleInfo.effects[key]
            if self.IsEffectActivatible(effect):
                return effect



    GetDefaultEffect = uiutil.ParanoidDecoMethod(GetDefaultEffect, ('sr', 'moduleInfo', 'effects'))

    def OnClick(self, *args):
        if self.goingOnline or self.IsBeingDragged():
            return 
        ctrlRepeat = 0
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            ctrlRepeat = 1000
        self.Click(ctrlRepeat)



    def Click(self, ctrlRepeat = 0):
        if self.waitingForActiveTarget:
            sm.GetService('pwntarget').CancelTargetOrder(self)
            self.HideGauge('target')
            self.waitingForActiveTarget = 0
        elif self.def_effect is None:
            log.LogWarn('No default Effect available for this moduletypeID:', self.sr.moduleInfo.typeID)
        elif not self.online:
            eve.Message('ClickOffllineModule')
        elif self.def_effect.isActive:
            self.DeactivateEffect(self.def_effect)
        elif not self.effect_activating:
            self.activationTimer = base.AutoTimer(500, self.ActivateEffectTimer)
            self.effect_activating = 1
            self.ActivateEffect(self.def_effect, ctrlRepeat=ctrlRepeat)



    def ActivateEffectTimer(self, *args):
        self.effect_activating = 0
        self.activationTimer = None



    def OnEndDrag(self, *args):
        uthread.new(uicore.layer.shipui.ResetSwapMode)



    def GetDragData(self, *args):
        return 
        if settings.user.ui.Get('lockModules', 0):
            return []
        if self.charge:
            fakeNode = uix.GetItemData(self.charge, 'icons')
            fakeNode.isCharge = 1
        else:
            fakeNode = uix.GetItemData(self.sr.moduleInfo, 'icons')
            fakeNode.isCharge = 0
        fakeNode.__guid__ = 'xtriui.ShipUIModule'
        fakeNode.slotFlag = self.sr.moduleInfo.flagID
        uicore.layer.shipui.StartSwapMode()
        return [fakeNode]



    def OnDropData(self, dragObj, nodes):
        return 
        log.LogInfo('Module.OnDropData', self.sr.sourceID)
        flag1 = self.sr.moduleInfo.flagID
        flag2 = None
        for node in nodes:
            if node.Get('__guid__', None) == 'xtriui.ShipUIModule':
                flag2 = node.slotFlag
                break

        if flag1 == flag2:
            return 
        if flag2 is not None:
            uicore.layer.shipui.SwapSlots(flag1, flag2)
            return 
        for node in nodes:
            self.Add(node.rec)




    def OnMouseDown(self, *args):
        log.LogInfo('Module.OnMouseDown', self.sr.sourceID)
        if getattr(self, 'downTop', None) is not None:
            return 
        self.downTop = self.parent.top
        self.parent.top += 2



    def OnMouseUp(self, *args):
        log.LogInfo('Module.OnMouseUp', self.sr.sourceID)
        if getattr(self, 'downTop', None) is not None:
            self.parent.top = self.downTop
            self.downTop = None



    def OnMouseEnter(self, *args):
        self.HiliteOn()
        uthread.pool('ShipMobuleButton::MouseEnter', self.MouseEnter)



    def MouseEnter(self, *args):
        if self.destroyed or sm.GetService('godma').GetItem(self.sr.moduleInfo.itemID) is None:
            return 
        log.LogInfo('Module.OnMouseEnter', self.sr.sourceID)
        eve.Message('NeocomButtonEnter')
        self.ShowAccuracy()
        self.sr.accuracyTimer = base.AutoTimer(1000, self.ShowAccuracy)
        uthread.pool('ShipMobuleButton::OnMouseEnter-->UpdateTargetingRanges', sm.GetService('tactical').UpdateTargetingRanges, self.sr.moduleInfo)



    def OnMouseExit(self, *args):
        log.LogInfo('Module.OnMouseExit', self.sr.sourceID)
        self.HiliteOff()
        sm.ScatterEvent('OnShowAccuracy', None)
        self.sr.accuracyTimer = None
        self.OnMouseUp(None)



    def OnMouseMove(self, *args):
        uthread.pool('ShipModuleButton::MouseMove', self.UpdateInfo)



    def ShowAccuracy(self):
        self.UpdateInfo()
        sm.ScatterEvent('OnShowAccuracy', self.GetAccuracy)



    def UpdateInfo(self):
        if self.destroyed:
            return 
        self.sr.hint = ''
        if uicore.uilib.mouseOver != self:
            self.sr.accuracyTimer = None
            return 
        info = '%s: %s' % (mls.UI_GENERIC_TYPE, self.typeName)
        defEff = self.GetDefaultEffect()
        if defEff:
            status = mls.UI_GENERIC_INACTIVE
            if defEff.isActive:
                status = mls.UI_GENERIC_ACTIVE
        else:
            status = ''
        info += '<br>%s: %s' % (mls.UI_GENERIC_STATUS, status)
        if self.goingOnline:
            info += ', %s' % mls.UI_INFLIGHT_GOINGONLINE.lower()
        if self.waitingForActiveTarget:
            info += ', %s' % mls.UI_INFLIGHT_WAITINGFORACTIVETARGET.lower()
        if cfg.IsChargeCompatible(self.sr.moduleInfo):
            if self.charge and self.charge.typeID:
                chargetype = cfg.invtypes.Get(self.charge.typeID)
                info += '<br>' + mls.UI_INFLIGHT_CHARGEPCS % {'qty': util.FmtAmt(self.quantity),
                 'type': chargetype.name}
            else:
                info += '<br>%s' % mls.UI_INFLIGHT_CHARGENOCHARGE
        accuracy = self.GetAccuracy()
        acc = ''
        if accuracy is not None:
            info += '<br>%s: %.2f' % (mls.UI_GENERIC_ACCURACY, accuracy[0])
        if self.charge:
            godmaInfo = sm.GetService('godma').GetItem(self.charge.itemID)
            if godmaInfo and godmaInfo.crystalsGetDamaged:
                info += '<br>%s: %.2f' % (mls.UI_GENERIC_DAMAGE, godmaInfo.damage)
        t = self.sr.Get('targetID', None)
        if t:
            slimItem = sm.GetService('michelle').GetBallpark().GetInvItem(t)
            info += '<br>%s: %s' % (mls.UI_GENERIC_TARGET, uix.GetSlimItemName(slimItem))
        pos = uicore.layer.shipui.GetPosFromFlag(self.sr.moduleInfo.itemID)
        if pos:
            slotno = pos[1] + 1
            cmd = uicore.cmd
            combo = cmd.GetShortcutByFuncName('CmdActivateHighPowerSlot%i' % slotno, True)
            if not combo:
                combo = mls.UI_GENERIC_NONE
            info += '<br>%s: %s' % (mls.UI_GENERIC_SHORTCUT, combo)
        if self and getattr(self, 'sr', None):
            self.sr.hint = info



    def GetAccuracy(self, targetID = None):
        if self is None or self.destroyed:
            return 
        else:
            return 
        if targetID is None:
            targetID = self.GetCurrentTarget()
        if targetID is None:
            return 
        for key in self.sr.moduleInfo.effects.keys():
            effect = self.sr.moduleInfo.effects[key]
            if effect.isDefault:
                if effect.effectName == 'useMissiles':
                    if self.charge is None:
                        return 
                    effect = self.sr.moduleInfo.GetChargeEffect(self.charge.typeID)
                    if effect is None:
                        return 
                if effect.trackingSpeedAttributeID is None:
                    if effect.rangeAttributeID is not None:
                        maxRange = effect.range
                else:
                    trackingSpeed = effect.trackingSpeed
                    falloff = effect.falloff
                    maxRange = effect.range
                    bp = sm.GetService('michelle').GetBallpark()
                    if bp is not None:
                        return bp.GetAccuracy(eve.session.shipid, targetID, maxRange, falloff, trackingSpeed, self.sr.moduleInfo.signatureRadius)
                    else:
                        return 
                return 




    def SetActive(self):
        self.sr.glow.state = uiconst.UI_DISABLED
        sm.GetService('ui').BlinkSpriteA(self.sr.glow, 0.75, 1000, None, passColor=0)
        self.state = uiconst.UI_NORMAL
        self.effect_activating = 0
        self.activationTimer = None



    def SetIdle(self):
        self.sr.glow.state = uiconst.UI_HIDDEN
        self.sr.busy.state = uiconst.UI_HIDDEN
        sm.GetService('ui').StopBlink(self.sr.busy)
        sm.GetService('ui').StopBlink(self.sr.glow)
        self.state = uiconst.UI_NORMAL



    def HiliteOn(self):
        self.sr.hilite.state = uiconst.UI_DISABLED



    def HiliteOff(self):
        self.sr.hilite.state = uiconst.UI_HIDDEN



    def Update(self, effectState):
        if self.def_effect and effectState.effectName == self.def_effect.effectName:
            if effectState.start:
                self.SetActive()
            else:
                self.SetIdle()
        if effectState.effectName == 'online':
            if effectState.active:
                self.ShowOnline()
            else:
                self.ShowOffline()
        self.UpdateInfo()



    def ActivateEffect(self, effect, targetID = None, ctrlRepeat = 0):
        if effect and effect.effectName == 'useMissiles':
            if self.charge is None:
                return 
            RELEVANTEFFECT = sm.GetService('godma').GetStateManager().GetDefaultEffect(self.charge.typeID)
        else:
            RELEVANTEFFECT = effect
        if RELEVANTEFFECT and not targetID and RELEVANTEFFECT.effectCategory == 2:
            targetID = self.GetCurrentTarget()
            if not targetID:
                sm.GetService('pwntarget').OrderTarget(self)
                uthread.new(self.BlinkIcon)
                self.waitingForActiveTarget = 1
                return 
        if self.sr.Get('moduleinfo'):
            for key in self.sr.moduleInfo.effects.iterkeys():
                checkeffect = self.sr.moduleInfo.effects[key]
                if checkeffect.effectName == 'online':
                    if not checkeffect.isActive:
                        self._ChangeOnline(1)
                    break

        if effect:
            michelle = sm.GetService('michelle')
            bp = michelle.GetBallpark()
            ball = bp.GetBall(targetID)
            item = bp.GetInvItem(targetID)
            effect.Activate(targetID, 9999999)



    def DeactivateEffect(self, effect):
        self.sr.glow.state = uiconst.UI_HIDDEN
        self.sr.busy.state = uiconst.UI_DISABLED
        sm.GetService('ui').BlinkSpriteA(self.sr.busy, 0.75, 1000, None, passColor=0)
        self.state = uiconst.UI_DISABLED
        effect.Deactivate()



    def OnStateChange(self, itemID, flag, true, *args):
        if true and flag == state.activeTarget and self.waitingForActiveTarget:
            self.ActivateEffect(self.def_effect, itemID)
            sm.GetService('pwntarget').CancelTargetOrder(self)
            self.waitingForActiveTarget = 0



    def OnAttribute(self, attributeName, item, newValue):
        if item.locationID == self.sr.sourceID:
            structs = sm.GetService('pwn').GetCurrentControl()
            if structs.has_key(self.sr.sourceID):
                itemStr = sm.services['godma'].GetItem(self.sr.sourceID)
                if itemStr.groupID == const.groupMobileLaserSentry:
                    self.SetCharge(itemStr.modules[0])
                else:
                    self.SetCharge(itemStr.sublocations[0])
        self.scanAttributeChangeFlag = True



    def GetCurrentTarget(self):
        return sm.GetService('pwn').GetCurrentTarget(self.sr.sourceID)



    def CountDown(self, tid):
        if self.destroyed:
            return 
        self.countDown = 1
        self.scanAttributeChangeFlag = False
        slimItem = sm.GetService('michelle').GetBallpark().GetInvItem(tid)
        source = self.sr.sourceID
        time = sm.GetService('bracket').GetScanSpeed(source, slimItem)
        if hasattr(self, 'sr') and self.sr.Get('targetContainer'):
            par = uicls.Container(parent=self.sr.targetContainer, width=52, height=13, left=6, top=62, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
            t = uicls.Label(text='', parent=par, width=200, height=12, left=6, top=1, fontsize=9, letterspace=1, uppercase=1, autoheight=False, autowidth=False, state=uiconst.UI_NORMAL)
            p = uicls.Fill(parent=par, align=uiconst.RELATIVE, width=48, height=11, left=1, top=1, color=(1.0, 1.0, 1.0, 0.25))
            uicls.Frame(parent=par, color=(1.0, 1.0, 1.0, 0.5))
            startTime = blue.os.GetTime()
            while not self.destroyed and self.countDown:
                now = blue.os.GetTime()
                dt = blue.os.TimeDiffInMs(startTime, now)
                if self.scanAttributeChangeFlag:
                    waitRatio = dt / float(time)
                    self.scanAttributeChangeFlag = False
                    time = sm.GetService('bracket').GetScanSpeed(source, slimItem)
                    startTime = now - long(time * waitRatio * 10000)
                    dt = blue.os.TimeDiffInMs(startTime, now)
                if t.destroyed:
                    return 
                t.text = '%.3f %s' % ((time - dt) / 1000.0, [mls.UI_GENERIC_SECONDSHORT, mls.UI_GENERIC_SECONDSSHORT][((time - dt) / 1000.0 > 2.0)])
                if dt > time:
                    t.text = mls.UI_INFLIGHT_LOCKED
                    break
                p.width = int(48 * ((time - dt) / time))
                blue.pyos.synchro.Yield()

            if self.destroyed:
                return 
            if not self.countDown:
                par.Close()
            p.width = 0
            blue.pyos.synchro.Sleep(250)
            if t.destroyed:
                return 
            t.text = ''
            blue.pyos.synchro.Sleep(250)
            if t.destroyed:
                return 
            t.text = mls.UI_INFLIGHT_LOCKED
            blue.pyos.synchro.Sleep(250)
            if t.destroyed:
                return 
            t.text = ''
            blue.pyos.synchro.Sleep(250)
            if t.destroyed:
                return 
            t.text = mls.UI_INFLIGHT_LOCKED
            blue.pyos.synchro.Sleep(250)
            par.Close()



    def OnTargetOBO(self, what, sid = None, tid = None, reason = None):
        uthread.new(self._OnTargetOBO, what, sid, tid, reason)



    def _OnTargetOBO(self, what, sid, tid, reason):
        if sid != self.sr.sourceID:
            return 
        if self.blockOntarget:
            return 
        self.blockOntarget = 1
        if what == 'add':
            self.OnTargetAdded(tid)
        elif what == 'clear':
            self.OnTargetClear()
        elif what == 'lost':
            self.OnTargetLost(tid, reason)
        self.blockOntarget = 0



    def OnTargetAdded(self, tid):
        if self.destroyed:
            return 
        self.ShowGauge('target')
        currentTarget = sm.GetService('pwn').GetCurrentTarget(self.sr.sourceID)
        if currentTarget != tid:
            return 
        slimItem = sm.GetService('michelle').GetBallpark().GetInvItem(tid)
        self.waitingForActiveTarget = 0
        self.sr.targetID = tid
        self.sr.targetIcon.LoadIconByTypeID(slimItem.typeID, ignoreSize=True)
        self.sr.targetIcon.SetSize(48, 48)
        self.sr.targetIcon.state = uiconst.UI_DISABLED



    def OnStructureTargetAdded(self, sid, tid):
        self.OnTargetAdded(tid)



    def OnStructureTargetRemoved(self, sid, tid):
        self.OnTargetLost(tid)



    def OnTargetLost(self, tid, reason):
        self.sr.targetIcon.LoadIcon('ui_5_64_10', ignoreSize=True)
        self.sr.targetIcon.SetSize(48, 48)
        self.sr.targetID = None
        self.HideGauge('target')
        self.waitingForActiveTarget = 0



    def OnTargetClear(self):
        self.OnTargetLost(None, None)




class DefenceModuleButton(uicls.Container):
    default_name = 'slot'
    default_width = 64
    default_height = 64
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        quantityParent = uicls.Container(parent=self, name='quantityParent', pos=(8, 10, 22, 10), align=uiconst.BOTTOMRIGHT, state=uiconst.UI_HIDDEN)
        fill = uicls.Fill(parent=quantityParent, color=(0.0, 0.0, 0.0, 1.0))
        iconSprite = uicls.Icon(parent=self, name='iconSprite', pos=(8, 6, 48, 48), state=uiconst.UI_HIDDEN)
        mainshape = uicls.Sprite(parent=self, name='mainshape', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, texturePath='res:/UI/Texture/classes/DefenceModuleButton/mainShape.png', color=(1.0, 1.0, 1.0, 0.7))
        glow = uicls.Sprite(parent=self, name='glow', pos=(-1, -1, -1, -1), align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/DefenceModuleButton/mainGlow.png', color=(0.24, 0.67, 0.16, 0.74))
        busy = uicls.Sprite(parent=self, name='busy', pos=(-2, -2, -2, -2), align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/DefenceModuleButton/mainGlow.png', color=(1.0, 0.13, 0.0, 0.73))




