import uthread
import uix
import mathUtil
import base
import util
import blue
import service
import re
import state
import math
import uiutil
import uicls
import menu
import uiconst
import log
import localization
import localizationUtil
cgre = re.compile('chargeGroup\\d{1,2}')

class ModuleButton(uicls.Container):
    __guid__ = 'xtriui.ModuleButton'
    __notifyevents__ = ['OnStateChange',
     'OnItemChange',
     'OnModuleRepaired',
     'OnAmmoInBankChanged',
     'OnFailLockTarget',
     'OnChargeBeingLoadedToModule']
    __update_on_reload__ = 1
    __cgattrs__ = []
    __loadingcharges__ = []
    __chargesizecache__ = {}
    default_name = 'ModuleButton'
    default_pickRadius = 20

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)



    def _OnClose(self):
        if getattr(self, 'invCookie', None) is not None:
            sm.GetService('inv').Unregister(self.invCookie)
        uicls.Container._OnClose(self)



    def init(self):
        self.def_effect = None
        self.charge = None
        self.target = None
        self.waitingForActiveTarget = 0
        self.changingAmmo = 0
        self.reloadingAmmo = False
        self.online = False
        self.goingOnline = 0
        self.stateManager = None
        self.dogmaLocation = None
        self.autorepeat = 0
        self.autoreload = 0
        self.sr.accuracyTimer = None
        self.quantity = None
        self.invReady = 1
        self.invCookie = None
        self.isInvItem = 1
        self.isBeingRepaired = 0
        self.blinking = 0
        self.blinkingDamage = 0
        self.effect_activating = 0
        self.typeName = ''
        self.ramp_active = False
        self.isMaster = 0
        self.isPendingUnlockForDeactivate = False
        self.icon = uicls.Icon(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        sm.RegisterNotify(self)



    def Setup(self, moduleinfo, grey = None):
        if not len(self.__cgattrs__):
            self.__cgattrs__.extend([ a.attributeID for a in cfg.dgmattribs if cgre.match(a.attributeName) is not None ])
        invType = cfg.invtypes.Get(moduleinfo.typeID)
        group = cfg.invtypes.Get(moduleinfo.typeID).Group()
        self.id = moduleinfo.itemID
        self.sr.moduleInfo = moduleinfo
        self.locationFlag = moduleinfo.flagID
        self.stateManager = sm.StartService('godma').GetStateManager()
        self.dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        self.grey = grey
        self.typeName = uix.GetItemName(self.sr.moduleInfo)
        for each in ['glow',
         'busy',
         'hilite',
         'quantityParent',
         'damageState',
         'overloadBtn',
         'stackParent',
         'ramps',
         'leftRamp',
         'leftShadowRamp',
         'rightRamp',
         'rightShadowRamp',
         'groupHighlight']:
            obj = uiutil.GetChild(self.parent.parent, each)
            setattr(self.sr, each, obj)

        self.sr.leftShadowRamp.state = self.sr.rightShadowRamp.state = uiconst.UI_HIDDEN
        self.sr.ramps.opacity = 0.85
        self.sr.qtylabel = uicls.Label(text='', parent=self.sr.quantityParent, fontsize=9, letterspace=1, left=3, top=0, width=30, state=uiconst.UI_DISABLED, idx=0)
        self.sr.stacklabel = uicls.Label(text='', parent=self.sr.stackParent, fontsize=9, letterspace=1, left=5, top=0, width=30, state=uiconst.UI_DISABLED, idx=0, shadowOffset=(0, 0), color=(1.0, 1.0, 1.0, 1))
        icon = self.sr.overloadBtn
        icon.sr.hint = localization.GetByLabel('UI/Inflight/Overload/hintToggleOverload')
        icon.OnClick = self.ToggleOverload
        icon.OnMouseDown = (self.OLButtonDown, icon)
        icon.OnMouseUp = (self.OLButtonUp, icon)
        icon.OnMouseExit = (self.OLMouseExit, icon)
        self.sr.overloadButton = icon
        if cfg.IsChargeCompatible(moduleinfo):
            self.invCookie = sm.GetService('inv').Register(self)
        self.autoreload = settings.char.autoreload.Get(self.sr.moduleInfo.itemID, 1)
        if group.categoryID == const.categoryCharge:
            self.SetCharge(moduleinfo)
        else:
            self.SetCharge(None)
        self.autoreload = settings.char.autoreload.Get(self.sr.moduleInfo.itemID, 1)
        for key in moduleinfo.effects.iterkeys():
            effect = moduleinfo.effects[key]
            if self.IsEffectActivatible(effect):
                self.def_effect = effect
                if effect.isActive:
                    if effect.isDeactivating:
                        self.isDeactivating = True
                        self.SetDeactivating()
                    else:
                        self.SetActive()
            if effect.effectName == 'online':
                if effect.isActive:
                    self.ShowOnline()
                else:
                    self.ShowOffline()

        self.autoreload = settings.char.autoreload.Get(self.sr.moduleInfo.itemID, 1)
        godma = sm.StartService('godma')
        self.isBeingRepaired = godma.GetStateManager().IsModuleBeingRepaired(self.id)
        if self.isBeingRepaired:
            self.SetRepairing()
        repeat = settings.char.autorepeat.Get(self.sr.moduleInfo.itemID, -1)
        if group.groupID in (const.groupMiningLaser, const.groupStripMiner):
            self.SetRepeat(1000)
        elif repeat != -1:
            self.SetRepeat(repeat)
        else:
            repeatSet = 0
            for key in self.sr.moduleInfo.effects.iterkeys():
                effect = self.sr.moduleInfo.effects[key]
                if self.IsEffectRepeatable(effect):
                    self.SetRepeat(1000)
                    repeatSet = 1
                    break

            if not repeatSet:
                self.SetRepeat(0)
        self.autoreload = settings.char.autoreload.Get(self.sr.moduleInfo.itemID, 1)
        if not getattr(self, 'isDeactivating', False):
            self.state = uiconst.UI_NORMAL
        self.slaves = self.dogmaLocation.GetSlaveModules(self.sr.moduleInfo.itemID, session.shipid)
        moduleDamage = self.GetModuleDamage()
        if moduleDamage:
            self.SetDamage(moduleDamage / moduleinfo.hp)
        else:
            self.SetDamage(0.0)
        self.Draggable_blockDrag = 0
        self.autoreload = settings.char.autoreload.Get(self.sr.moduleInfo.itemID, 1)
        uthread.new(self.BlinkIcon)



    def OLButtonDown(self, btn, *args):
        btn.top = 6



    def OLButtonUp(self, btn, *args):
        btn.top = 5



    def OLMouseExit(self, btn, *args):
        btn.top = 5



    def ToggleOverload(self, *args):
        if settings.user.ui.Get('lockOverload', 0):
            eve.Message('error')
            eve.Message('LockedOverloadState')
            return 
        for key in self.sr.moduleInfo.effects.iterkeys():
            effect = self.sr.moduleInfo.effects[key]
            if effect.effectCategory == const.dgmEffOverload:
                active = effect.isActive
                if active:
                    eve.Message('click')
                    effect.Deactivate()
                else:
                    eve.Message('click')
                    effect.Activate()




    def SetCharge(self, charge):
        if charge and charge.stacksize != 0:
            if self.charge is None or charge.typeID != self.charge.typeID:
                self.icon.LoadIconByTypeID(charge.typeID)
            self.charge = charge
            self.stateManager.ChangeAmmoTypeForModule(self.sr.moduleInfo.itemID, charge.typeID)
            self.id = charge.itemID
            self.UpdateChargeQuantity(charge)
        else:
            self.icon.LoadIconByTypeID(self.sr.moduleInfo.typeID)
            self.sr.qtylabel.parent.state = uiconst.UI_HIDDEN
            self.quantity = 0
            self.id = self.sr.moduleInfo.itemID
            self.charge = None
        self.CheckOverload()
        self.CheckOnline()
        self.CheckMasterSlave()



    def UpdateChargeQuantity(self, charge):
        if charge is self.charge:
            if cfg.invtypes.Get(charge.typeID).groupID in cfg.GetCrystalGroups():
                self.sr.qtylabel.parent.state = uiconst.UI_HIDDEN
                return 
            self.quantity = charge.stacksize
            self.sr.qtylabel.text = '%s' % util.FmtAmt(charge.stacksize)
            self.sr.qtylabel.parent.state = uiconst.UI_DISABLED



    def ShowGroupHighlight(self):
        self.dragging = True
        self.sr.groupHighlight.state = uiconst.UI_DISABLED
        uthread.new(self.PulseGroupHighlight)



    def StopShowingGroupHighlight(self):
        self.dragging = False
        self.sr.groupHighlight.state = uiconst.UI_HIDDEN



    def PulseGroupHighlight(self):
        pulseSize = 0.4
        opacity = 1.0
        startTime = blue.os.GetSimTime()
        while self.dragging:
            self.sr.groupHighlight.opacity = opacity
            blue.pyos.synchro.SleepWallclock(200)
            if not self or self.destroyed:
                break
            sinWave = math.cos(float(blue.os.GetSimTime() - startTime) / (0.5 * const.SEC))
            opacity = min(sinWave * pulseSize + (1 - pulseSize / 2), 1)




    def SetDamage(self, damage):
        if not damage or damage < 0.0001:
            self.sr.damageState.state = uiconst.UI_HIDDEN
            return 
        imageIndex = max(1, int(damage * 8))
        self.sr.damageState.LoadTexture('res:/UI/Texture/classes/ShipUI/slotDamage_%s.png' % imageIndex)
        self.sr.damageState.state = uiconst.UI_NORMAL
        amount = self.sr.moduleInfo.damage / self.sr.moduleInfo.hp * 100
        self.sr.damageState.hint = localization.GetByLabel('UI/Inflight/Overload/hintDamagedModule', preText='', amount=amount)
        sm.GetService('ui').BlinkSpriteA(self.sr.damageState, 1.0, 2000 - 1000 * damage, 2, passColor=0)



    def GetVolume(self):
        if self.charge:
            return cfg.GetItemVolume(self.charge, 1)



    def IsMine(self, rec):
        ret = rec.locationID == eve.session.shipid and rec.flagID == self.locationFlag and cfg.invtypes.Get(rec.typeID).Group().Category().id == const.categoryCharge
        return ret



    def AddItem(self, rec):
        if cfg.invtypes.Get(rec.typeID).categoryID == const.categoryCharge:
            self.SetCharge(rec)



    def UpdateItem(self, rec, change):
        if cfg.invtypes.Get(rec.typeID).categoryID == const.categoryCharge:
            self.SetCharge(rec)



    def RemoveItem(self, rec):
        if cfg.invtypes.Get(rec.typeID).categoryID == const.categoryCharge:
            if self.charge and rec.itemID == self.id:
                self.SetCharge(None)



    def GetShell(self):
        return sm.GetService('invCache').GetInventoryFromId(eve.session.shipid)



    def GetMatchingAmmo(self, lTypeID, ignoreLoading = 0):
        lRS = cfg.dgmtypeattribs.get(lTypeID, [])
        lAttribs = util.IndexedRows(lRS, ('attributeID',))
        if lAttribs.has_key(const.attributeChargeSize):
            wantChargeSize = lAttribs[const.attributeChargeSize].value
        else:
            wantChargeSize = 0
        chargeGroups = []
        for attributeID in self.__cgattrs__:
            if lAttribs.has_key(attributeID):
                groupID = lAttribs[attributeID].value
                if groupID != 0:
                    chargeGroups.append(groupID)

        if ignoreLoading:
            return [ item for item in self.GetShell().ListCargo() if item.groupID in chargeGroups if wantChargeSize == 0 or self.IsCorrectChargeSize(item, wantChargeSize) ]
        return [ item for item in self.GetShell().ListCargo() if item.groupID in chargeGroups if wantChargeSize == 0 or self.IsCorrectChargeSize(item, wantChargeSize) ]



    def IsCorrectChargeSize(self, item, wantChargeSize):
        if not self.__chargesizecache__.has_key(item.typeID):
            cRS = cfg.dgmtypeattribs.get(item.typeID, [])
            cAttribs = util.IndexedRows(cRS, ('attributeID',))
            if cAttribs.has_key(const.attributeChargeSize):
                gotChargeSize = cAttribs[const.attributeChargeSize].value
            else:
                gotChargeSize = 0
            self.__chargesizecache__[item.typeID] = gotChargeSize
        else:
            gotChargeSize = self.__chargesizecache__[item.typeID]
        if wantChargeSize != gotChargeSize:
            return 0
        return 1



    def UnloadToCargo(self, itemID):
        self.reloadingAmmo = True
        try:
            self.dogmaLocation.UnloadChargeToContainer(session.shipid, itemID, (session.shipid,), const.flagCargo)

        finally:
            self.reloadingAmmo = False




    def ChangeAmmoType(self, typeID, quantity):
        itemID = None
        (chargeTypeID, chargeQuantity, roomForReload,) = self.GetChargeReloadInfo(ignoreCharge=1)
        matchingAmmo = [ (item.stacksize, item) for item in self.GetMatchingAmmo(self.sr.moduleInfo.typeID) if item.typeID == typeID ]
        matchingAmmo = uiutil.SortListOfTuples(matchingAmmo)
        matchingAmmo.reverse()
        self.dogmaLocation.LoadChargeToModule(self.sr.moduleInfo.itemID, typeID, chargeItems=matchingAmmo)



    def ReloadAmmo(self, itemID, quantity, preferSingletons = False):
        if not quantity:
            return 
        self.reloadingAmmo = True
        lastChargeTypeID = self.stateManager.GetAmmoTypeForModule(self.sr.moduleInfo.itemID)
        try:
            self.dogmaLocation.LoadChargeToModule(self.sr.moduleInfo.itemID, lastChargeTypeID, preferSingletons=preferSingletons)

        finally:
            self.reloadingAmmo = False




    def ReloadAllAmmo(self):
        uicore.cmd.CmdReloadAmmo()



    def BlinkIcon(self, time = None):
        if self.destroyed or self.blinking:
            return 
        startTime = blue.os.GetSimTime()
        if time is not None:
            timeToBlink = time * 10000
        while self.changingAmmo or self.reloadingAmmo or self.waitingForActiveTarget or self.goingOnline or time:
            if time is not None:
                if blue.os.GetSimTime() - startTime > timeToBlink:
                    break
            blue.pyos.synchro.SleepWallclock(250)
            if self.destroyed:
                return 
            self.icon.SetAlpha(0.25)
            blue.pyos.synchro.SleepWallclock(250)
            if self.destroyed:
                return 
            self.icon.SetAlpha(1.0)

        if self.destroyed:
            return 
        self.blinking = 0
        self.CheckOverload()
        self.CheckOnline()



    def ChangeAmmo(self, itemID, quantity, ammoType):
        if not quantity:
            return 
        self.changingAmmo = 1
        try:
            self.dogmaLocation.LoadChargeToModule(itemID, ammoType, qty=quantity)

        finally:
            if self and not self.destroyed:
                self.changingAmmo = 0




    def DoNothing(self, *args):
        pass



    def CopyItemIDToClipboard(self, itemID):
        blue.pyos.SetClipboardData(str(itemID))



    def GetMenu(self):
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        if ship is None:
            return []
        m = []
        if eve.session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            if cfg.IsChargeCompatible(self.sr.moduleInfo):
                m += [('Launcher: ' + str(self.sr.moduleInfo.itemID), self.CopyItemIDToClipboard, (self.sr.moduleInfo.itemID,))]
                if self.id != self.sr.moduleInfo.itemID:
                    m += [('Charge: ' + str(self.id), self.CopyItemIDToClipboard, (self.id,)), None]
            else:
                m += [(str(self.id), self.CopyItemIDToClipboard, (self.id,)), None]
            m += sm.GetService('menu').GetGMTypeMenu(self.sr.moduleInfo.typeID, itemID=self.id, divs=True, unload=True)
        moduleType = cfg.invtypes.Get(self.sr.moduleInfo.typeID)
        groupID = moduleType.groupID
        if cfg.IsChargeCompatible(self.sr.moduleInfo):
            (chargeTypeID, chargeQuantity, roomForReload,) = self.GetChargeReloadInfo()
            matchingAmmo = self.GetMatchingAmmo(self.sr.moduleInfo.typeID)
            ammoList = {}
            ammoSingletonList = {}
            for item in matchingAmmo:
                if item.typeID != chargeTypeID:
                    if item.singleton:
                        ammoSingletonList[item.typeID] = ammoSingletonList.get(item.typeID, []) + [item]
                    else:
                        ammoList[item.typeID] = ammoList.get(item.typeID, []) + [item]

            if roomForReload > 0:
                reloadCandidates = [ (item.stacksize, item.itemID, min(item.stacksize, roomForReload)) for item in matchingAmmo if item.typeID == chargeTypeID if item.stacksize != 0 ]
                reloadSingletonCandidates = [ (item.itemID, min(item.stacksize, roomForReload)) for item in matchingAmmo if item.typeID == chargeTypeID if item.singleton ]
            else:
                reloadCandidates = []
                reloadSingletonCandidates = []
            noOfModules = 1 if self.slaves is None else len(self.slaves) + 1
            noOfCharges = sum([ cand[1] for cand in reloadSingletonCandidates ])
            if noOfCharges >= noOfModules:
                text = (localization.GetByLabel('UI/Inflight/ModuleRacks/ReloadUsed', typeId=chargeTypeID), menu.ACTIONSGROUP)
                m.append((text, self.ReloadAmmo, (reloadSingletonCandidates[-1][0], reloadSingletonCandidates[-1][1], True)))
            noOfCharges = sum([ cand[0] for cand in reloadCandidates ])
            if noOfCharges >= noOfModules:
                reloadCandidates.sort()
                text = (localization.GetByLabel('UI/Inflight/ModuleRacks/Reload', typeID=chargeTypeID), menu.ACTIONSGROUP)
                m.append((text, self.ReloadAmmo, (reloadCandidates[-1][1], reloadCandidates[-1][2])))
                m.append((localization.GetByLabel('UI/Inflight/ModuleRacks/ReloadAll'), self.ReloadAllAmmo))
            m.append(None)
            if self.charge is not None:
                m.append((localization.GetByLabel('UI/Inflight/ModuleRacks/UnloadToCargo'), self.UnloadToCargo, (self.charge.itemID,)))
                m.append(None)
            temp = []
            if len(ammoSingletonList):
                for l in ammoSingletonList.itervalues():
                    item = l[0]
                    text = (localization.GetByLabel('UI/Inflight/ModuleRacks/AmmoTypeAndStatus', typeID=item.typeID), menu.ACTIONSGROUP)
                    temp.append((text, self.ChangeAmmoType, (item.typeID, item.stacksize)))

            m.extend(localizationUtil.Sort(temp, key=lambda x: x[0][0]))
            temp = []
            if len(ammoList):
                for l in ammoList.itervalues():
                    sumqty = sum([ each.stacksize for each in l ])
                    item = l[0]
                    qty = int(moduleType.capacity / cfg.GetItemVolume(item, 1) + 1e-07)
                    if qty:
                        text = localization.GetByLabel('UI/Inflight/ModuleRacks/AmmoTypeAndQuantity', typeID=item.typeID, sumqty=sumqty)
                        text = (text, menu.ACTIONSGROUP)
                        temp.append((text, self.ChangeAmmoType, (item.typeID, item.stacksize)))

            m.extend(localizationUtil.Sort(temp, key=lambda x: x[0][0]))
            m.append(None)
            if self.autoreload == 0:
                m.append((localization.GetByLabel('UI/Inflight/ModuleRacks/AutoReloadOn'), self.SetAutoReload, (1,)))
            else:
                m.append((localization.GetByLabel('UI/Inflight/ModuleRacks/AutoReloadOff'), self.SetAutoReload, (0,)))
        overloadLock = settings.user.ui.Get('lockOverload', 0)
        itemID = self.sr.moduleInfo.itemID
        slaves = self.dogmaLocation.GetSlaveModules(itemID, session.shipid)
        for key in self.sr.moduleInfo.effects.iterkeys():
            effect = self.sr.moduleInfo.effects[key]
            if self.IsEffectRepeatable(effect) and groupID not in (const.groupMiningLaser, const.groupStripMiner):
                if self.autorepeat == 0:
                    m.append((localization.GetByLabel('UI/Inflight/ModuleRacks/AutoRepeatOn'), self.SetRepeat, (1000,)))
                else:
                    m.append((localization.GetByLabel('UI/Inflight/ModuleRacks/AutoRepeatOff'), self.SetRepeat, (0,)))
            if effect.effectName == 'online':
                m.append(None)
                if not slaves:
                    if effect.isActive:
                        m.append((localization.GetByLabel('UI/Inflight/ModuleRacks/PutModuleOffline'), self.ChangeOnline, (0,)))
                    else:
                        m.append((localization.GetByLabel('UI/Inflight/ModuleRacks/PutModuleOnline'), self.ChangeOnline, (1,)))
            if not overloadLock and effect.effectCategory == const.dgmEffOverload:
                active = effect.isActive
                if active:
                    m.append((localization.GetByLabel('UI/Inflight/Overload/menuToggleOverloadActive'), self.Overload, (0, effect)))
                else:
                    m.append((localization.GetByLabel('UI/Inflight/Overload/menuToggleOverloadInactive'), self.Overload, (1, effect)))
                m.append((localization.GetByLabel('UI/Inflight/OverloadRack'), self.OverloadRack, ()))
                m.append((localization.GetByLabel('UI/Inflight/StopOverloadingRack'), self.StopOverloadRack, ()))

        moduleDamage = self.GetModuleDamage()
        if moduleDamage:
            if self.isBeingRepaired:
                m.append((localization.GetByLabel('UI/Inflight/menuCancelRepair'), self.CancelRepair, ()))
            else:
                m.append((localization.GetByLabel('UI/Commands/Repair'), self.RepairModule, ()))
        if slaves:
            m.append((localization.GetByLabel('UI/Fitting/ClearGroup'), self.UnlinkModule, ()))
        m += [(localization.GetByLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, (self.sr.moduleInfo.typeID,
           self.sr.moduleInfo.itemID,
           0,
           self.sr.moduleInfo))]
        return m



    def RepairModule(self):
        success = self.stateManager.RepairModule(self.sr.moduleInfo.itemID)
        if self.slaves:
            for slave in self.slaves:
                success = self.stateManager.RepairModule(slave) or success

        if success == True:
            self.isBeingRepaired = True
            self.SetRepairing()



    def CancelRepair(self):
        sm.GetService('godma').GetStateManager().StopRepairModule(self.sr.moduleInfo.itemID)



    def OnFailLockTarget(self, tid, *args):
        self.waitingForActiveTarget = 0



    def OnModuleRepaired(self, itemID):
        if itemID == self.sr.moduleInfo.itemID:
            self.RemoveRepairing()
            self.isBeingRepaired = False



    def OnAmmoInBankChanged(self, masterID):
        slaves = self.dogmaLocation.GetSlaveModules(masterID, session.shipid)
        if self.sr.moduleInfo.itemID in slaves:
            self.SetCharge(self.sr.moduleInfo)



    def OnChargeBeingLoadedToModule(self, itemIDs, chargeTypeID, time):
        if self.sr.moduleInfo.itemID not in itemIDs:
            return 
        chargeGroupID = self.stateManager.GetType(chargeTypeID).groupID
        eve.Message('LauncherLoadDelay', {'ammoGroupName': (GROUPID, chargeGroupID),
         'launcherGroupName': (GROUPID, self.sr.moduleInfo.groupID),
         'time': time / 1000})
        self.BlinkIcon(time)



    def UnlinkModule(self):
        self.dogmaLocation.DestroyWeaponBank(session.shipid, self.sr.moduleInfo.itemID)



    def Overload(self, onoff, eff):
        if onoff:
            eff.Activate()
        else:
            eff.Deactivate()



    def OverloadRack(self):
        sm.GetService('godma').OverloadRack(self.sr.moduleInfo.itemID)



    def StopOverloadRack(self):
        sm.GetService('godma').StopOverloadRack(self.sr.moduleInfo.itemID)



    def GetChargeReloadInfo(self, ignoreCharge = 0):
        moduleType = cfg.invtypes.Get(self.sr.moduleInfo.typeID)
        lastChargeTypeID = self.stateManager.GetAmmoTypeForModule(self.sr.moduleInfo.itemID)
        if self.charge and not ignoreCharge:
            chargeTypeID = self.charge.typeID
            chargeQuantity = self.charge.stacksize
        elif lastChargeTypeID is not None:
            chargeTypeID = lastChargeTypeID
            chargeQuantity = 0
        else:
            chargeTypeID = None
            chargeQuantity = 0
        if chargeTypeID is not None:
            roomForReload = int(moduleType.capacity / cfg.invtypes.Get(chargeTypeID).volume - chargeQuantity + 1e-07)
        else:
            roomForReload = 0
        return (chargeTypeID, chargeQuantity, roomForReload)



    def SetAutoReload(self, on):
        settings.char.autoreload.Set(self.sr.moduleInfo.itemID, on)
        self.autoreload = on
        self.AutoReload()



    def AutoReload(self, force = 0, useItemID = None, useQuant = None):
        if self.reloadingAmmo is not False:
            return 
        if not cfg.IsChargeCompatible(self.sr.moduleInfo) or not (self.autoreload or force):
            return 
        (chargeTypeID, chargeQuantity, roomForReload,) = self.GetChargeReloadInfo()
        if chargeQuantity > 0 and not force or roomForReload <= 0:
            return 
        shiplayer = uicore.layer.shipui
        if not shiplayer:
            return 
        self.dogmaLocation.LoadChargeToModule(self.sr.moduleInfo.itemID, chargeTypeID)
        uthread.new(self.CheckPending)



    def OnItemChange(self, item, change):
        if not self or self.destroyed or not getattr(self, 'sr', None):
            return 
        if const.ixQuantity not in change:
            return 
        if self.reloadingAmmo == item.itemID and not sm.GetService('invCache').IsItemLocked(self, item.itemID):
            shiplayer = uicore.layer.shipui
            reloadsByID = shiplayer.sr.reloadsByID
            self.reloadingAmmo = True
            if reloadsByID[item.itemID].balance:
                reloadsByID[item.itemID].send(None)
            else:
                del reloadsByID[item.itemID]



    def CheckPending(self):
        shiplayer = uicore.layer.shipui
        if not shiplayer:
            return 
        blue.pyos.synchro.SleepSim(1000)
        if shiplayer and shiplayer:
            shiplayer.CheckPendingReloads()



    def CheckOverload(self):
        if not self or self.destroyed:
            return 
        isActive = False
        hasOverloadEffect = False
        if not util.HasAttrs(self, 'sr', 'moduleInfo', 'effects'):
            return 
        for key in self.sr.moduleInfo.effects.iterkeys():
            effect = self.sr.moduleInfo.effects[key]
            if effect.effectCategory == const.dgmEffOverload:
                if effect.isActive:
                    isActive = True
                hasOverloadEffect = True

        if hasOverloadEffect:
            self.sr.overloadButton.top = 5
            if self.online:
                if isActive:
                    self.sr.overloadButton.LoadTexture('res:/UI/Texture/classes/ShipUI/slotOverloadOn.png')
                else:
                    self.sr.overloadButton.LoadTexture('res:/UI/Texture/classes/ShipUI/slotOverloadOff.png')
                self.sr.overloadButton.state = uiconst.UI_NORMAL
            else:
                self.sr.overloadButton.LoadTexture('res:/UI/Texture/classes/ShipUI/slotOverloadDisabled.png')
            self.sr.overloadButton.state = uiconst.UI_DISABLED
        else:
            self.sr.overloadButton.top = 6
            self.sr.overloadButton.LoadTexture('res:/UI/Texture/classes/ShipUI/slotOverloadDisabled.png')
            self.sr.overloadButton.state = uiconst.UI_DISABLED



    def CheckMasterSlave(self):
        if not self or self.destroyed:
            return 
        itemID = self.sr.moduleInfo.itemID
        slaves = self.dogmaLocation.GetSlaveModules(itemID, session.shipid)
        if slaves:
            self.sr.stackParent.state = uiconst.UI_DISABLED
            self.sr.stacklabel.text = len(slaves) + 1



    def CheckOnline(self, sound = 0):
        if not self or self.destroyed:
            return 
        if not util.HasAttrs(self, 'sr', 'moduleInfo', 'effects'):
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
        masterID = self.dogmaLocation.IsInWeaponBank(session.shipid, self.sr.moduleInfo.itemID)
        if masterID:
            if not on:
                ret = eve.Message('CustomQuestion', {'header': 'OFFLINE',
                 'question': "When offlining this module you will destroy the weapons bank it's in. Are you sure you want to offline it? "}, uiconst.YESNO)
                if ret != uiconst.ID_YES:
                    return 
        elif not on and eve.Message('PutOffline', {}, uiconst.YESNO) != uiconst.ID_YES:
            return 
        for key in self.sr.moduleInfo.effects.keys():
            effect = self.sr.moduleInfo.effects[key]
            if effect.effectName == 'online':
                if on:
                    effect.Activate()
                    self.goingOnline = 1
                    uthread.new(self.BlinkIcon)
                    blue.pyos.synchro.SleepSim(5000)
                    if not self or self.destroyed:
                        return 
                    self.goingOnline = 0
                else:
                    self.ShowOffline(1)
                    effect.Deactivate()
                return 




    def ShowOverload(self, on):
        self.CheckOverload()



    def ShowOnline(self):
        self.isMaster = 0
        if self.AreModulesOffline():
            self.ShowOffline()
            return 
        self.online = True
        if self.grey:
            self.icon.SetAlpha(0.1)
        elif not self.goingOnline:
            self.icon.SetAlpha(1.0)
        self.CheckOverload()



    def ShowOffline(self, ping = 0):
        self.online = False
        self.goingOnline = 0
        if self.grey:
            self.icon.SetAlpha(0.1)
        else:
            self.icon.SetAlpha(0.25)
        if ping:
            eve.Message('OnLogin')
        self.CheckOverload()
        self.state = uiconst.UI_NORMAL



    def AreModulesOffline(self):
        slaves = self.dogmaLocation.GetSlaveModules(self.sr.moduleInfo.itemID, session.shipid)
        if not slaves:
            return False
        self.isMaster = 1
        onlineEffect = self.stateManager.GetEffect(self.sr.moduleInfo.itemID, 'online')
        if onlineEffect is None or not onlineEffect.isActive:
            return True
        for slave in slaves:
            onlineEffect = self.stateManager.GetEffect(slave, 'online')
            if onlineEffect is None or not onlineEffect.isActive:
                return True

        return False



    def IsEffectRepeatable(self, effect, activatibleKnown = 0):
        if activatibleKnown or self.IsEffectActivatible(effect):
            if not effect.item.disallowRepeatingActivation:
                return effect.durationAttributeID is not None
        return 0



    def IsEffectActivatible(self, effect):
        return effect.isDefault and effect.effectName != 'online' and effect.effectCategory in (const.dgmEffActivation, const.dgmEffTarget)



    def SetRepeat(self, num):
        settings.char.autorepeat.Set(self.sr.moduleInfo.itemID, num)
        self.autorepeat = num



    def GetDefaultEffect(self):
        if not self or self.destroyed:
            return 
        if self.sr is None or self.sr.moduleInfo is None or not self.stateManager.IsItemLoaded(self.sr.moduleInfo.itemID):
            return 
        for key in self.sr.moduleInfo.effects.iterkeys():
            effect = self.sr.moduleInfo.effects[key]
            if self.IsEffectActivatible(effect):
                return effect




    def OnClick(self, *args):
        if not self or self.goingOnline or self.IsBeingDragged():
            return 
        ctrlRepeat = 0
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            ctrlRepeat = 1000
        self.Click(ctrlRepeat)



    def Click(self, ctrlRepeat = 0):
        if self.waitingForActiveTarget:
            sm.GetService('target').CancelTargetOrder(self)
            self.waitingForActiveTarget = 0
        elif self.def_effect is None:
            log.LogWarn('No default Effect available for this moduletypeID:', self.sr.moduleInfo.typeID)
        elif not self.online:
            if getattr(self, 'isMaster', None):
                eve.Message('ClickOffllineGroup')
            else:
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



    def OnEndDrag_(self, *args):
        uthread.new(uicore.layer.shipui.ResetSwapMode)



    def GetDragData(self, *args):
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
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        uicore.layer.shipui.StartDragMode(self.sr.moduleInfo.itemID, self.sr.moduleInfo.typeID)
        return [fakeNode]



    def OnDropData(self, dragObj, nodes):
        log.LogInfo('Module.OnDropData', self.id)
        flag1 = self.sr.moduleInfo.flagID
        flag2 = None
        for node in nodes:
            if node.Get('__guid__', None) == 'xtriui.ShipUIModule':
                flag2 = node.slotFlag
                break

        if flag1 == flag2:
            return 
        if flag2 is not None:
            uicore.layer.shipui.ChangeSlots(flag1, flag2)
            return 
        multiLoadCharges = True
        chargeTypeID = None
        chargeItems = []
        for node in nodes:
            if not hasattr(node, 'rec'):
                return 
            chargeItem = node.rec
            if not hasattr(chargeItem, 'categoryID'):
                return 
            if chargeItem.categoryID != const.categoryCharge:
                continue
            if chargeTypeID is None:
                chargeTypeID = chargeItem.typeID
            if chargeItem.typeID == chargeTypeID:
                chargeItems.append(chargeItem)

        if len(chargeItems) > 0:
            self.dogmaLocation.DropLoadChargeToModule(self.sr.moduleInfo.itemID, chargeTypeID, chargeItems=chargeItems)



    def OnMouseDown(self, *args):
        uicls.Container.OnMouseDown(self, *args)
        log.LogInfo('Module.OnMouseDown', self.id)
        if getattr(self, 'downTop', None) is not None:
            return 
        self.downTop = self.parent.parent.top
        self.parent.parent.top += 2



    def OnMouseUp(self, *args):
        uicls.Container.OnMouseUp(self, *args)
        if not self or self.destroyed:
            return 
        log.LogInfo('Module.OnMouseUp', self.id)
        if getattr(self, 'downTop', None) is not None:
            self.parent.parent.top = self.downTop
            self.downTop = None



    def OnMouseEnter(self, *args):
        self.HiliteOn()
        uthread.pool('ShipMobuleButton::MouseEnter', self.MouseEnter)



    def MouseEnter(self, *args):
        if self.destroyed or sm.GetService('godma').GetItem(self.sr.moduleInfo.itemID) is None:
            return 
        log.LogInfo('Module.OnMouseEnter', self.id)
        eve.Message('NeocomButtonEnter')
        self.ShowAccuracy()
        self.sr.accuracyTimer = base.AutoTimer(1000, self.ShowAccuracy)
        uthread.pool('ShipMobuleButton::OnMouseEnter-->UpdateTargetingRanges', sm.GetService('tactical').UpdateTargetingRanges, self.sr.moduleInfo, self.charge)



    def OnMouseExit(self, *args):
        log.LogInfo('Module.OnMouseExit', self.id)
        self.HiliteOff()
        sm.ScatterEvent('OnShowAccuracy', None)
        self.sr.accuracyTimer = None
        self.OnMouseUp(None)



    def OnMouseMove(self, *args):
        uicls.Container.OnMouseMove(self, *args)
        uthread.pool('ShipModuleButton::MouseMove', self.UpdateInfo)



    def ShowAccuracy(self):
        self.UpdateInfo()
        sm.ScatterEvent('OnShowAccuracy', self.GetAccuracy)



    def UpdateInfo(self):
        if not self or self.destroyed:
            return 
        if not self.stateManager.IsItemLoaded(self.id):
            return 
        self.sr.hint = ''
        if uicore.uilib.mouseOver != self:
            self.sr.accuracyTimer = None
            return 
        params = {'WeaponGroupText': '',
         'TypeText': '',
         'StatusText': '',
         'GoingOnlineText': '',
         'WaitingForTargetText': '',
         'ChangingAmmoText': '',
         'ReloadingText': '',
         'ChargesText': '',
         'OverloadText': '',
         'ModuleDamageText': '',
         'AccuracyText': '',
         'CrystalDamageText': '',
         'ShortCutText': ''}
        info = ''
        slaves = self.dogmaLocation.GetSlaveModules(self.sr.moduleInfo.itemID, session.shipid)
        if slaves:
            params['WeaponGroupText'] = localization.GetByLabel('UI/Inflight/ModuleRacks/WeaponLinking', numModules=len(slaves) + 1)
        params['TypeText'] = localization.GetByLabel('UI/Inflight/ModuleRacks/WeaponType', typeName=self.typeName)
        defEff = self.GetDefaultEffect()
        if defEff:
            params['StatusText'] = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleInactive')
            if defEff.isActive:
                params['StatusText'] = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleActive')
        if self.goingOnline:
            params['GoingOnlineText'] = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleGoingOnline')
        if self.waitingForActiveTarget:
            params['WaitingForTargetText'] = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleWaitingForTarget')
        if self.changingAmmo:
            params['ChangingAmmoText'] = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleChangingAmmo')
        if self.reloadingAmmo:
            params['ReloadingText'] = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleReloading')
        if cfg.IsChargeCompatible(self.sr.moduleInfo):
            if self.charge and self.charge.typeID:
                p = {'qty': self.charge.stacksize,
                 'typeID': self.charge.typeID}
                params['ChargesText'] = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleChargesPieces', **p)
            else:
                params['ChargesText'] = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleNoCharges')
        for key in self.sr.moduleInfo.effects.iterkeys():
            effect = self.sr.moduleInfo.effects[key]
            if effect.effectCategory == const.dgmEffOverload:
                if effect.isActive:
                    params['OverloadText'] = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleOverloadActive')
                else:
                    params['OverloadText'] = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleOverloadInactive')

        moduleDamage = self.GetModuleDamage()
        if moduleDamage:
            amount = moduleDamage / self.sr.moduleInfo.hp * 100
            params['ModuleDamageText'] = localization.GetByLabel('UI/Inflight/Overload/hintDamagedModule', preText='<br>', amount=amount)
        accuracy = self.GetAccuracy()
        acc = ''
        if accuracy is not None:
            params['AccuracyText'] = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleAccuracy', accuracy=accuracy[0])
        if self.charge:
            godmaInfo = sm.GetService('godma').GetItem(self.charge.itemID)
            if godmaInfo and godmaInfo.crystalsGetDamaged:
                damage = godmaInfo.damage
                params['CrystalDamageText'] = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleCrystalDamage', damage=damage)
        pos = uicore.layer.shipui.GetPosFromFlag(self.sr.moduleInfo.flagID)
        if pos:
            hiMedLo = ('High', 'Medium', 'Low')[pos[0]]
            slotno = pos[1] + 1
            shortcut = uicore.cmd.GetShortcutStringByFuncName('CmdActivate%sPowerSlot%i' % (hiMedLo, slotno))
            if not shortcut:
                shortcut = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleShortcutNone')
            params['ShortCutText'] = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleShortcut', shortcut=shortcut)
        if self and getattr(self, 'sr', None):
            self.sr.hint = localization.GetByLabel('UI/Inflight/ModuleRacks/hintModuleInfo', **params)



    def GetModuleDamage(self):
        moduleDamage = self.sr.moduleInfo.damage
        if self.slaves is None:
            return moduleDamage
        maxDamage = moduleDamage
        for slaveID in self.slaves:
            slave = self.stateManager.GetItem(slaveID)
            if slave is None:
                continue
            damage = self.stateManager.GetItem(slaveID).damage
            if damage > maxDamage:
                maxDamage = damage

        return maxDamage



    def GetAccuracy(self, targetID = None):
        if self is None or self.destroyed:
            return 
        else:
            return 
        if targetID is None:
            targetID = sm.GetService('target').GetActiveTargetID()
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
        self.effect_activating = 0
        self.activationTimer = None
        self.state = uiconst.UI_NORMAL
        if settings.user.ui.Get('showCycleTimer', 1):
            self.ActivateRamps()



    def SetDeactivating(self):
        self.sr.glow.state = uiconst.UI_HIDDEN
        self.sr.busy.state = uiconst.UI_DISABLED
        sm.GetService('ui').BlinkSpriteA(self.sr.busy, 0.75, 1000, None, passColor=0)
        self.state = uiconst.UI_DISABLED
        if settings.user.ui.Get('showCycleTimer', 1):
            self.DeActivateRamps()



    def SetIdle(self):
        self.sr.glow.state = uiconst.UI_HIDDEN
        self.sr.busy.state = uiconst.UI_HIDDEN
        sm.GetService('ui').StopBlink(self.sr.busy)
        sm.GetService('ui').StopBlink(self.sr.glow)
        self.state = uiconst.UI_NORMAL
        self.IdleRamps()



    def SetRepairing(self):
        self.sr.glow.state = uiconst.UI_DISABLED
        self.sr.glow.color.r = 1.0
        self.sr.glow.color.g = 1.0
        self.sr.glow.color.b = 1.0
        self.sr.glow.color.a = 1.0
        sm.GetService('ui').BlinkSpriteA(self.sr.glow, 0.9, 2500, None, passColor=0)
        self.state = uiconst.UI_NORMAL



    def RemoveRepairing(self):
        sm.GetService('ui').StopBlink(self.sr.glow)
        self.sr.glow.color.r = 0.24
        self.sr.glow.color.g = 0.67
        self.sr.glow.color.b = 0.16
        self.sr.glow.color.a = 0.75
        self.sr.glow.state = uiconst.UI_HIDDEN



    def HiliteOn(self):
        self.sr.hilite.state = uiconst.UI_DISABLED



    def HiliteOff(self):
        self.sr.hilite.state = uiconst.UI_HIDDEN



    def GetEffectByName(self, effectName):
        for key in self.sr.moduleInfo.effects.iterkeys():
            effect = self.sr.moduleInfo.effects[key]
            if effect.effectName == effectName:
                return effect




    def Update(self, effectState):
        if not self or self.destroyed:
            return 
        if not self.stateManager.IsItemLoaded(self.id):
            return 
        if self.def_effect and effectState.effectName == self.def_effect.effectName:
            if effectState.start:
                self.SetActive()
            else:
                self.SetIdle()
        effect = self.GetEffectByName(effectState.effectName)
        if effect and effect.effectCategory == const.dgmEffOverload:
            self.ShowOverload(effect.isActive)
        if effectState.effectName == 'online':
            if effectState.active:
                self.ShowOnline()
            else:
                self.ShowOffline()
        if effect.effectCategory in [const.dgmEffTarget, const.dgmEffActivation, const.dgmEffArea] and effect.effectID != const.effectOnline:
            if not effectState.active and self.quantity == 0:
                self.AutoReload()
        self.UpdateInfo()



    def ActivateEffect(self, effect, targetID = None, ctrlRepeat = 0):
        if effect and effect.effectName == 'useMissiles' or effect.effectName == 'warpDisruptSphere' and self.charge is not None:
            if self.charge is None:
                return 
            RELEVANTEFFECT = sm.GetService('godma').GetStateManager().GetDefaultEffect(self.charge.typeID)
        else:
            RELEVANTEFFECT = effect
        if RELEVANTEFFECT and not targetID and RELEVANTEFFECT.effectCategory == 2:
            targetID = sm.GetService('target').GetActiveTargetID()
            if not targetID:
                sm.GetService('target').OrderTarget(self)
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
            if RELEVANTEFFECT.isOffensive:
                if not sm.GetService('consider').DoAttackConfirmations(targetID, RELEVANTEFFECT):
                    return 
            elif RELEVANTEFFECT.isAssistance:
                if not sm.GetService('consider').DoAidConfirmations(targetID):
                    return 
            repeats = ctrlRepeat or self.autorepeat
            if not self.IsEffectRepeatable(effect, 1):
                repeats = 0
            if not self.charge:
                self.stateManager.ChangeAmmoTypeForModule(self.sr.moduleInfo.itemID, None)
            effect.Activate(targetID, repeats)



    def DeactivateEffect(self, effect):
        self.SetDeactivating()
        try:
            effect.Deactivate()
        except UserError as e:
            if e.msg == 'EffectStillActive':
                if sm.GetService('machoNet').GetClientConfigVals().get('fixStuckModules'):
                    if not self.isPendingUnlockForDeactivate:
                        self.isPendingUnlockForDeactivate = True
                        uthread.new(self.DelayButtonUnlockForDeactivate, e.dict['timeLeft'])
            raise 



    def DelayButtonUnlockForDeactivate(self, sleepTimeSec):
        blue.pyos.synchro.SleepSim(sleepTimeSec * 1000)
        if self.state == uiconst.UI_DISABLED:
            self.state = uiconst.UI_NORMAL
        self.isPendingUnlockForDeactivate = False



    def OnStateChange(self, itemID, flag, true, *args):
        if self and true and flag == state.activeTarget and self.waitingForActiveTarget:
            self.waitingForActiveTarget = 0
            self.ActivateEffect(self.def_effect, itemID)
            sm.GetService('target').CancelTargetOrder(self)



    def GetModuleType(self):
        return (self.sr.moduleInfo.typeID, self.sr.moduleInfo.itemID)



    def ActivateRamps(self):
        if not self or self.destroyed:
            return 
        if self.ramp_active:
            self.UpdateRamps()
            return 
        self.DoActivateRamps()



    def DeActivateRamps(self):
        self.UpdateRamps()



    def IdleRamps(self):
        self.ramp_active = False
        shiplayer = uicore.layer.shipui
        if not shiplayer:
            return 
        moduleID = self.sr.moduleInfo.itemID
        rampTimers = shiplayer.sr.rampTimers
        if rampTimers.has_key(moduleID):
            del rampTimers[moduleID]
        self.sr.ramps.state = uiconst.UI_HIDDEN



    def UpdateRamps(self):
        self.DoActivateRamps()



    def DoActivateRamps(self):
        if self.ramp_active:
            return 
        uthread.new(self.DoActivateRampsThread)



    def DoActivateRampsThread(self):
        if not self or self.destroyed:
            return 
        (startTime, durationInMilliseconds,) = self.GetDuration()
        if durationInMilliseconds <= 0:
            return 
        self.ramp_active = True
        self.sr.ramps.state = uiconst.UI_DISABLED
        portionDone = blue.os.TimeDiffInMs(startTime, blue.os.GetSimTime()) % durationInMilliseconds / durationInMilliseconds
        rampUpInit = min(1.0, max(0.0, portionDone * 2))
        rampDownInit = min(1.0, max(0.0, portionDone * 2 - 1.0))
        while self and not self.destroyed and self.ramp_active:
            (dummy, durationInMilliseconds,) = self.GetDuration()
            halfTheTime = durationInMilliseconds / 2.0
            funcs = [(self.SetRampUpValue, rampUpInit), (self.SetRampDownValue, rampDownInit)]
            rampUpInit = rampDownInit = 0.0
            for (i, (func, percent,),) in enumerate(funcs):
                init = percent
                if not self or self.destroyed:
                    break
                if i == 0:
                    self.sr.rightRamp.SetRotation(math.pi)
                    self.sr.rightShadowRamp.SetRotation(math.pi)
                    self.sr.leftRamp.SetRotation(math.pi)
                    self.sr.leftShadowRamp.SetRotation(math.pi)
                else:
                    self.sr.leftRamp.SetRotation(0)
                    self.sr.leftShadowRamp.SetRotation(0)
                    self.sr.rightRamp.SetRotation(math.pi)
                    self.sr.rightShadowRamp.SetRotation(math.pi)
                while not self.destroyed:
                    prePercent = percent
                    try:
                        percent = min(blue.os.TimeDiffInMs(startTime, blue.os.GetSimTime()) % halfTheTime / halfTheTime, 1.0)
                    except:
                        percent = 1.0
                    if prePercent > percent:
                        break
                    curValue = mathUtil.Lerp(init, 1.0, percent)
                    func(curValue)
                    blue.pyos.synchro.Yield()
                    if self and not self.destroyed and not self.ramp_active:
                        func(1.0)
                        break


            startTime += long(durationInMilliseconds * const.dgmTauConstant)
            if not self or self.destroyed or self.InLimboState():
                break




    def InLimboState(self):
        for each in ['goingOnline',
         'waitingForActiveTarget',
         'changingAmmo',
         'reloadingAmmo',
         'isDeactivating']:
            if getattr(self, each, False):
                return True

        return False



    def GetRampStartTime(self):
        shiplayer = uicore.layer.shipui
        if not shiplayer:
            return 
        moduleID = self.sr.moduleInfo.itemID
        rampTimers = shiplayer.sr.rampTimers
        if not rampTimers.has_key(moduleID):
            now = blue.os.GetSimTime()
            default = getattr(self.def_effect, 'startTime', now)
            if blue.os.TimeDiffInMs(default, now) > 1000.0:
                rampTimers[moduleID] = default
            else:
                rampTimers[moduleID] = now
        return rampTimers[moduleID]



    def GetDuration(self):
        rampStartTime = self.GetRampStartTime()
        durationInMilliseconds = 0.0
        attr = cfg.dgmattribs.GetIfExists(getattr(self.def_effect, 'durationAttributeID', None))
        item = self.stateManager.GetItem(self.def_effect.itemID)
        if item is None:
            return (0, 0.0)
        if attr:
            durationInMilliseconds = self.stateManager.GetAttribute(self.def_effect.itemID, attr.attributeName)
        if not durationInMilliseconds:
            durationInMilliseconds = getattr(self.def_effect, 'duration', 0.0)
        return (rampStartTime, durationInMilliseconds)



    def SetRampUpValue(self, value):
        self.sr.leftRamp.SetRotation(math.pi - math.pi * value)
        self.sr.leftShadowRamp.SetRotation(math.pi - math.pi * value)



    def SetRampDownValue(self, value):
        self.sr.rightRamp.SetRotation(math.pi - math.pi * value)
        self.sr.rightShadowRamp.SetRotation(math.pi - math.pi * value)
        if value == 1.0:
            self.sr.rightRamp.SetRotation(math.pi)
            self.sr.rightShadowRamp.SetRotation(math.pi)
            self.sr.leftRamp.SetRotation(math.pi)
            self.sr.leftShadowRamp.SetRotation(math.pi)




