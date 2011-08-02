import sys
import uix
import uiutil
import mathUtil
import uthread
import blue
import util
import lg
import service
import base
import uicls
import uiconst
import trinity

class FittingSlot(uicls.FittingSlotLayout):
    __guid__ = 'xtriui.FittingSlot'
    __notifyevents__ = ['OnRefreshModuleBanks']

    def ApplyAttributes(self, attributes):
        uicls.FittingSlotLayout.ApplyAttributes(self, attributes)
        self.isInvItem = 1
        self.isChargeable = 0
        self.quantity = 1
        self.shell = None
        self.linkDragging = 0
        self.id = None
        self.charge = None
        self.scaleFactor = 1.0
        self.utilButtons = []



    def IsMine(self, item):
        return item.flagID == self.flag and item.locationID == eve.session.shipid



    def Startup(self, flag, powerType, shell, scaleFactor = 1.0):
        self.flag = flag
        self.locationFlag = flag
        self.powerType = powerType
        self._emptyHint = self.PrimeToEmptySlotHint()
        sm.GetService('inv').Register(self)
        self.invReady = 1
        self.sr.groupMark.parent.left = int(self.sr.groupMark.parent.left * scaleFactor)
        self.sr.groupMark.parent.top = int(self.sr.groupMark.parent.top * scaleFactor)
        self.sr.groupMark.GetMenu = self.GetGroupMenu
        sm.RegisterNotify(self)
        self.SetFitting(None, shell)



    def OnRefreshModuleBanks(self):
        self.SetGroup()



    def SetGroup(self):
        if not session.shipid:
            return 
        allGroupsDict = settings.user.ui.Get('linkedWeapons_groupsDict', {})
        groupDict = allGroupsDict.get(session.shipid, {})
        ret = self.GetBankGroup(groupDict)
        if ret is None:
            self.sr.groupMark.parent.state = uiconst.UI_HIDDEN
            return 
        groupNumber = ret.groupNumber
        self.sr.groupMark.parent.state = uiconst.UI_PICKCHILDREN
        self.sr.groupMark.parent.SetRotation(-self.GetRotation())
        if groupNumber < 0:
            availGroups = [1,
             2,
             3,
             4,
             5,
             6,
             7,
             8]
            for (masterID, groupNum,) in groupDict.iteritems():
                if groupNum in availGroups:
                    availGroups.remove(groupNum)

            groupNumber = availGroups[0] if availGroups else ''
        self.sr.groupMark.LoadIcon('ui_73_16_%s' % (176 + groupNumber))
        self.sr.groupMark.hint = mls.UI_SHARED_WEAPONLINK_GROUPNUM % {'groupNumber': groupNumber}
        groupDict[ret.masterID] = groupNumber
        allGroupsDict[session.shipid] = groupDict
        settings.user.ui.Set('linkedWeapons_groupsDict', allGroupsDict)



    def GetBankGroup(self, groupDict):
        module = getattr(self, 'module', None)
        if not module:
            return 
        stateManager = sm.StartService('godma').GetStateManager()
        isInWeaponBank = stateManager.IsInWeaponBank(self.module.itemID)
        if not isInWeaponBank:
            return 
        masterID = isInWeaponBank
        if masterID in groupDict:
            groupNumber = groupDict.get(masterID)
        else:
            groupNumber = -1
        ret = util.KeyVal()
        ret.masterID = masterID
        ret.groupNumber = groupNumber
        return ret



    def PrepareUtilButtons(self):
        for btn in self.utilButtons:
            btn.Close()

        self.utilButtons = []
        if not self.module or not sm.StartService('godma').GetStateManager().IsItemLoaded(self.module.itemID):
            return 
        toggleLabel = mls.UI_CMD_PUTOFFLINE if bool(util.GetAttrs(self, 'module', 'online', 'isActive')) is True else mls.UI_CMD_PUTONLINE
        (myrad, cos, sin, cX, cY,) = self.radCosSin
        btns = []
        if self.charge:
            btns += [(mls.UI_CMD_REMOVECHARGE,
              'ui_38_16_200',
              self.Unfit,
              1,
              0), (mls.UI_CMD_SHOW_CHARGE_INFO,
              'ui_38_16_208',
              self.ShowChargeInfo,
              1,
              0), ('',
              cfg.invtypes.Get(self.typeID).IconFile(),
              None,
              1,
              0)]
        isRig = False
        for effect in cfg.dgmtypeeffects.get(self.typeID, []):
            if effect.effectID == const.effectRigSlot:
                isRig = True
                break

        isSubSystem = cfg.invtypes.Get(self.typeID).categoryID == const.categorySubSystem
        if isRig:
            btns += [(mls.UI_CMD_DESTROY,
              'ui_38_16_200',
              self.Unfit,
              1,
              0), (mls.UI_CMD_SHOWINFO,
              'ui_38_16_208',
              self.ShowInfo,
              1,
              0)]
        elif isSubSystem:
            btns += [(mls.UI_CMD_SHOWINFO,
              'ui_38_16_208',
              self.ShowInfo,
              1,
              0)]
        else:
            btns += [(mls.UI_CMD_UNFIT_MODULE,
              'ui_38_16_200',
              self.UnfitModule,
              1,
              0), (mls.UI_CMD_SHOWINFO,
              'ui_38_16_208',
              self.ShowInfo,
              1,
              0), (toggleLabel,
              'ui_38_16_207',
              self.ToggleOnline,
              bool(util.GetAttrs(self, 'module', 'online')),
              1)]
        rad = myrad - 34
        i = 0
        for (hint, icon, func, active, onlinebtn,) in btns:
            left = int((rad - i * 16) * cos) + cX - 16 / 2
            top = int((rad - i * 16) * sin) + cY - 16 / 2
            icon = uicls.Icon(icon=icon, parent=self.parent, pos=(left,
             top,
             16,
             16), idx=0, pickRadius=-1, ignoreSize=True)
            icon.OnMouseEnter = self.ShowUtilButtons
            icon.hint = hint
            icon.color.a = 0.0
            icon.isActive = active
            if active:
                icon.OnClick = func
            else:
                icon.hint += ' (%s)' % mls.UI_GENERIC_DISABLED
            if onlinebtn == 1:
                self.sr.onlineButton = icon
            self.utilButtons.append(icon)
            i += 1




    def PrimeToEmptySlotHint(self):
        if self.flag in [const.flagHiSlot0,
         const.flagHiSlot1,
         const.flagHiSlot2,
         const.flagHiSlot3,
         const.flagHiSlot4,
         const.flagHiSlot5,
         const.flagHiSlot6,
         const.flagHiSlot7]:
            return mls.UI_GENERIC_EMPTY_HIGH_POWER_SLOT
        if self.flag in [const.flagMedSlot0,
         const.flagMedSlot1,
         const.flagMedSlot2,
         const.flagMedSlot3,
         const.flagMedSlot4,
         const.flagMedSlot5,
         const.flagMedSlot6,
         const.flagMedSlot7]:
            return mls.UI_GENERIC_EMPTY_MEDIUM_POWER_SLOT
        if self.flag in [const.flagLoSlot0,
         const.flagLoSlot1,
         const.flagLoSlot2,
         const.flagLoSlot3,
         const.flagLoSlot4,
         const.flagLoSlot5,
         const.flagLoSlot6,
         const.flagLoSlot7]:
            return mls.UI_GENERIC_EMPTY_LOW_POWER_SLOT
        if self.flag in [const.flagSubSystemSlot0,
         const.flagSubSystemSlot1,
         const.flagSubSystemSlot2,
         const.flagSubSystemSlot3,
         const.flagSubSystemSlot4]:
            return mls.UI_GENERIC_EMPTY_SUBSYSTEM_SLOT
        if self.flag in [const.flagRigSlot0, const.flagRigSlot1, const.flagRigSlot2]:
            return mls.UI_GENERIC_EMPTY_RIG_SLOT
        return mls.UI_GENERIC_EMPTY_SLOT



    def SetFitting(self, invItem, shell = None, putOnline = 0):
        if self.destroyed:
            return 
        lg.Info('fitting', 'SetFitting', self.flag, invItem and cfg.invtypes.Get(invItem.typeID).Group().name)
        self.Draggable_blockDrag = invItem is None
        self.shell = shell or self.shell
        chargehint = ''
        if invItem and self.IsCharge(invItem.typeID):
            self.charge = invItem
            chargehint = '%s %s: %s' % (cfg.invtypes.Get(invItem.typeID).name, mls.UI_GENERIC_QTY, invItem.stacksize)
            ship = sm.services['godma'].GetStateManager().GetItem(session.shipid)
            cap = ship.GetCapacity(self.flag)
            if cap.capacity == 0:
                portion = 1.0
            else:
                portion = cap.used / cap.capacity
            step = max(0, min(4, int(portion * 5.0)))
            self.sr.chargeIndicator.rectTop = 10 * step
            self.sr.chargeIndicator.state = uiconst.UI_NORMAL
            self.sr.chargeIndicator.hint = '%s %d%%' % (cfg.invtypes.Get(self.charge.typeID).name, portion * 100)
        elif invItem is None:
            self.id = None
            self.isChargeable = 0
            self.typeID = None
            self.module = None
            self.charge = None
            self.fitted = 0
            self.isChargeable = 0
            self.HideUtilButtons(1)
            self.sr.chargeIndicator.state = uiconst.UI_HIDDEN
        else:
            self.id = invItem.itemID
            self.typeID = invItem.typeID
            self.module = invItem
            self.fitted = 1
            self.charge = None
            if cfg.IsChargeCompatible(invItem):
                self.isChargeable = 1
                self.sr.chargeIndicator.rectTop = 0
                self.sr.chargeIndicator.state = uiconst.UI_NORMAL
                self.sr.chargeIndicator.hint = mls.UI_INFLIGHT_NOCHARGE
            else:
                self.isChargeable = 0
                self.sr.chargeIndicator.state = uiconst.UI_HIDDEN
        if self.typeID:
            modulehint = '%s' % cfg.invtypes.Get(self.typeID).name
            if self.charge:
                modulehint += '<br>%s %s: %s' % (cfg.invtypes.Get(self.charge.typeID).name, mls.UI_GENERIC_QTY, self.charge.stacksize)
        else:
            modulehint = self._emptyHint
        self.hint = modulehint
        self.opacity = 1.0
        self.state = uiconst.UI_NORMAL
        self.PrepareUtilButtons()
        if putOnline:
            uthread.new(self.DelayedOnlineAttempt, eve.session.shipid, invItem.itemID)
        icon = self.sr.flagIcon
        icon.SetAlign(uiconst.CENTER)
        iconSize = int(48 * self.scaleFactor)
        icon.SetSize(iconSize, iconSize)
        icon.SetPosition(0, 0)
        if self.charge or self.module:
            icon.LoadIconByTypeID((self.charge or self.module).typeID, ignoreSize=True)
            icon.parent.SetRotation(-self.GetRotation())
        else:
            rev = 0
            slotIcon = {const.flagSubSystemSlot0: 'ui_81_64_9',
             const.flagSubSystemSlot1: 'ui_81_64_10',
             const.flagSubSystemSlot2: 'ui_81_64_11',
             const.flagSubSystemSlot3: 'ui_81_64_12',
             const.flagSubSystemSlot4: 'ui_81_64_13'}.get(self.flag, None)
            if slotIcon is None:
                slotIcon = {const.effectLoPower: 'ui_81_64_5',
                 const.effectMedPower: 'ui_81_64_6',
                 const.effectHiPower: 'ui_81_64_7',
                 const.effectRigSlot: 'ui_81_64_8'}.get(self.powerType, None)
            else:
                rev = 1
            if slotIcon is not None:
                icon.LoadIcon(slotIcon, ignoreSize=True)
            if rev:
                icon.parent.SetRotation(mathUtil.DegToRad(180.0))
            else:
                icon.parent.SetRotation(0.0)
        icon.state = uiconst.UI_PICKCHILDREN
        self.SetGroup()
        self.UpdateOnlineDisplay()
        self.Hilite(0)



    def ColorUnderlay(self, color = None):
        a = self.sr.underlay.color.a
        (r, g, b,) = color or (1.0, 1.0, 1.0)
        self.sr.underlay.color.SetRGB(r, g, b, a)
        self.UpdateOnlineDisplay()



    def UpdateOnlineDisplay(self):
        if getattr(self, 'module', None) and sm.StartService('godma').GetStateManager().IsItemLoaded(self.module.itemID) and getattr(self.module, 'online', None):
            isActive = self.module.online.isActive
            if isActive:
                self.sr.flagIcon.color.a = 1.0
                if util.GetAttrs(self, 'sr', 'onlineButton') and self.sr.onlineButton.hint == mls.UI_CMD_PUTONLINE:
                    self.sr.onlineButton.hint = mls.UI_CMD_PUTOFFLINE
                    uicore.UpdateHint(self.sr.onlineButton)
            else:
                self.sr.flagIcon.color.a = 0.25
                if util.GetAttrs(self, 'sr', 'onlineButton') and self.sr.onlineButton.hint == mls.UI_CMD_PUTOFFLINE:
                    self.sr.onlineButton.hint = mls.UI_CMD_PUTONLINE
                    uicore.UpdateHint(self.sr.onlineButton)
        elif self.sr.flagIcon:
            self.sr.flagIcon.color.a = 1.0



    def ToggleOnline(self, *args):
        if not self.module or not self.module.effects:
            return 
        if 'rigSlot' in self.module.effects:
            return 
        isActive = util.GetAttrs(self, 'module', 'online', 'isActive')
        if isActive:
            self.ChangeOnline(0)
        else:
            self.ChangeOnline(1)



    def DelayedOnlineAttempt(self, shipID, moduleID):
        blue.pyos.synchro.Sleep(500)
        if shipID != eve.session.shipid:
            return 
        ship = sm.GetService('godma').GetItem(shipID)
        if ship is not None:
            for module in ship.modules:
                if module.itemID == moduleID:
                    try:
                        online = getattr(module, 'online', None)
                        if online and not online.isActive:
                            self.OnlineClick()
                    except UserError as e:
                        if e.msg == 'ModuleTooDamagedToBeOnlined':
                            eve.Message(e.msg, e.dict)
                        elif not ('effectname' in e.dict and e.dict['effectname'] == 'online') or e.msg == 'ModuleTooDamagedToBeOnlined':
                            eve.Message(e.msg, e.dict)
                        sys.exc_clear()
                    return 




    def AddItem(self, item):
        for each in sm.GetService('godma').GetItem(eve.session.shipid).modules:
            if each.itemID == item.itemID:
                self.SetFitting(each, putOnline=0)
                return 
        else:
            self.SetFitting(item)




    def UpdateItem(self, item, *etc):
        self.SetFitting(item)



    def RemoveItem(self, item):
        if self.charge and self.charge.itemID == item.itemID:
            self.charge = None
            self.SetFitting(self.module)
        elif self.module and self.module.itemID == item.itemID:
            self.SetFitting(None)



    def IsCharge(self, typeID):
        return cfg.invtypes.Get(typeID).categoryID == const.categoryCharge



    def Add(self, item, sourceLocation = None):
        if not getattr(item, 'typeID', None):
            return 
        if not sm.GetService('menu').RigFittingCheck(item):
            return 
        requiredSkills = sm.GetService('info').GetRequiredSkills(item.typeID)
        for (skillID, level,) in requiredSkills:
            if getattr(sm.GetService('skills').HasSkill(skillID), 'skillLevel', 0) < level:
                sm.GetService('tutorial').OpenTutorialSequence_Check(uix.skillfittingTutorial)
                break

        if self.IsCharge(item.typeID) and self.isChargeable:
            self.shell.inventory.Add(item.itemID, item.locationID, qty=1, flag=self.locationFlag)
        validFitting = False
        for effect in cfg.dgmtypeeffects.get(item.typeID, []):
            if effect.effectID in (const.effectHiPower,
             const.effectMedPower,
             const.effectLoPower,
             const.effectSubSystem,
             const.effectRigSlot):
                validFitting = True
                if effect.effectID == self.powerType:
                    ship = sm.GetService('godma').GetItem(eve.session.shipid)
                    if ship:
                        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
                        isFitted = item.locationID == session.shipid and item.flagID != const.flagCargo
                        if isFitted and shift:
                            if getattr(self, 'module', None):
                                if self.module.typeID == item.typeID:
                                    stateManager = sm.GetService('godma').GetStateManager()
                                    stateManager.LinkWeapons(self.module.itemID, item.itemID, item.typeID)
                                    return 
                                else:
                                    eve.Message('CustomNotify', {'notify': mls.UI_SHARED_WEAPONLINK_NOTSAME})
                                    return 
                        newItemID = ship.inventory.moniker.Add(item.itemID, item.locationID, qty=1, flag=self.locationFlag)
                        uthread.new(sm.services['godma'].GetStateManager().DelayedOnlineAttempt, session.shipid, newItemID)
                    return 
                eve.Message('ItemDoesntFitPower', {'item': cfg.invtypes.Get(item.typeID).name,
                 'slotpower': cfg.dgmeffects.Get(self.powerType).displayName,
                 'itempower': cfg.dgmeffects.Get(effect.effectID).displayName})

        if not validFitting:
            raise UserError('ItemNotHardware', {'itemname': (TYPEID, item.typeID)})



    def SetState(self, *args):
        self.UpdateOnlineDisplay()



    def OnlineClick(self, *args):
        effect = None
        for module in self.shell.modules:
            if module.itemID == self.id:
                effect = module.online

        if effect:
            effect.Toggle()



    def GetMenu(self):
        if self.typeID and self.id:
            m = []
            if eve.session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
                m += [(str(self.id), self.CopyItemIDToClipboard, (self.id,)), None]
            m += [(mls.UI_CMD_SHOWINFO, self.ShowInfo)]
            if 'rigSlot' in self.module.effects:
                if eve.session.stationid is not None:
                    m += [(mls.UI_CMD_DESTROY, self.Unfit)]
            elif eve.session.stationid is not None:
                m += [(mls.UI_CMD_UNFIT, self.Unfit)]
            for key in self.module.effects.iterkeys():
                effect = self.module.effects[key]
                if effect.effectName == 'online':
                    m.append(None)
                    if self.module.online.isActive:
                        m.append((mls.UI_CMD_PUTOFFLINE, self.ChangeOnline, (0,)))
                    else:
                        m.append((mls.UI_CMD_PUTONLINE, self.ChangeOnline, (1,)))

            m += self.GetGroupMenu()
            return m



    def GetGroupMenu(self, *args):
        stateManager = sm.StartService('godma').GetStateManager()
        masterID = stateManager.IsInWeaponBank(self.id)
        if masterID:
            return [(mls.UI_CMD_UNLINK, self.UnlinkModule, (masterID,))]
        return []



    def OnClick(self, *args):
        uicore.registry.SetFocus(self)
        self.ToggleOnline()



    def ChangeOnline(self, on = 1):
        stateManager = sm.StartService('godma').GetStateManager()
        masterID = stateManager.IsInWeaponBank(self.id)
        if masterID:
            if not on:
                ret = eve.Message('CustomQuestion', {'header': mls.UI_GENERIC_CONFIRM,
                 'question': mls.UI_SHARED_WEAPONLINK_OFFLINE}, uiconst.YESNO)
                if ret != uiconst.ID_YES:
                    return 
        for key in self.module.effects.keys():
            effect = self.module.effects[key]
            if effect.effectName == 'online':
                if on:
                    effect.Activate()
                else:
                    effect.Deactivate()




    def CopyItemIDToClipboard(self, itemID):
        blue.pyos.SetClipboardData(str(itemID))



    def ShowChargeInfo(self, *args):
        if self.charge:
            sm.GetService('info').ShowInfo(self.charge.typeID, self.charge.itemID)



    def ShowInfo(self, *args):
        sm.GetService('info').ShowInfo(self.typeID, self.id)



    def UnfitModule(self, *args):
        stateManager = sm.GetService('godma').GetStateManager()
        if session.stationid:
            stateManager.UnloadModuleToContainer(self.id, (const.containerHangar,))
        else:
            stateManager.UnloadModuleToContainer(self.id, (session.shipid,), flag=const.flagCargo)



    def Unfit(self, *args):
        if self.powerType == const.effectRigSlot:
            ship = sm.GetService('godma').GetItem(eve.session.shipid)
            if ship is None:
                return 
            ret = eve.Message('RigUnFittingInfo', {}, uiconst.OKCANCEL)
            if ret != uiconst.ID_OK:
                return 
            ship.inventory.DestroyFitting(self.id)
        elif self.charge:
            stateMgr = sm.StartService('godma').GetStateManager()
            if type(self.charge.itemID) is tuple:
                chargeIDs = stateMgr.GetSubLocationsInBank(self.charge.itemID)
                if chargeIDs:
                    if eve.session.stationid:
                        eve.GetInventory(const.containerHangar).MultiAdd(chargeIDs, eve.session.shipid, flag=const.flagHangar, fromManyFlags=True)
                    else:
                        eve.GetInventoryFromId(eve.session.shipid).MultiAdd(chargeIDs, eve.session.shipid, flag=const.flagCargo)
                elif eve.session.stationid:
                    self.shell.inventory.RemoveChargeToHangar(self.charge.itemID)
                else:
                    self.shell.inventory.RemoveChargeToCargo(self.charge.itemID)
            else:
                crystalIDs = stateMgr.GetCrystalsInBank(self.charge.itemID)
            if crystalIDs:
                if eve.session.stationid:
                    eve.GetInventory(const.containerHangar).MultiAdd(crystalIDs, eve.session.shipid, flag=const.flagHangar, fromManyFlags=True)
                else:
                    eve.GetInventoryFromId(eve.session.shipid).MultiAdd(crystalIDs, eve.session.shipid, flag=const.flagCargo)
            elif eve.session.stationid:
                eve.GetInventory(const.containerHangar).Add(self.charge.itemID, eve.session.shipid)
            else:
                eve.GetInventoryFromId(eve.session.shipid).Add(self.charge.itemID, eve.session.shipid, qty=None, flag=const.flagCargo)
        else:
            stateManager = sm.StartService('godma').GetStateManager()
            masterID = stateManager.IsInWeaponBank(self.id)
            if masterID:
                ret = eve.Message('CustomQuestion', {'header': mls.UI_GENERIC_CONFIRM,
                 'question': mls.UI_SHARED_WEAPONLINK_UNFIT}, uiconst.YESNO)
                if ret != uiconst.ID_YES:
                    return 
            if eve.session.stationid:
                eve.GetInventory(const.containerHangar).Add(self.id, eve.session.shipid)
            else:
                eve.GetInventoryFromId(eve.session.shipid).Add(self.id, eve.session.shipid, qty=None, flag=const.flagCargo)



    def UnlinkModule(self, masterID):
        stateMgr = sm.StartService('godma').GetStateManager()
        stateMgr.DestroyWeaponBank(masterID)



    def _OnEndDrag(self, *args):
        self.left = self.top = -2



    def OnEndDrag(self, *args):
        if self.module is not None:
            sm.ScatterEvent('OnResetSlotLinkingMode', self.module.typeID)



    def OnMouseEnter(self, *args):
        if not eve.dragData:
            if getattr(self, 'module', None) is not None:
                self.ShowUtilButtons()
            else:
                self.Hilite(1)
                eve.Message('ListEntryEnter')



    def OnMouseExit(self, *args):
        if not (getattr(self, 'module', None) or eve.dragData):
            self.Hilite(0)



    def ShowUtilButtons(self, *args):
        fittingbase = self.FindParentByName('fittingbase')
        fittingbase.ClearSlotsWithMenu()
        fittingbase.AddToSlotsWithMenu(self)
        for button in self.utilButtons:
            if button.isActive:
                button.color.a = 1.0
            else:
                button.color.a = 0.25

        self.utilButtonsTimer = base.AutoTimer(500, self.HideUtilButtons)



    def HideUtilButtons(self, force = 0):
        mo = uicore.uilib.mouseOver
        if not force and (mo in self.utilButtons or mo == self or uiutil.IsUnder(mo, self)):
            return 
        for button in self.utilButtons:
            button.color.a = 0.0

        self.utilButtonsTimer = None



    def Hilite(self, state):
        if state:
            self.sr.underlay.color.a = 1.0
        else:
            self.sr.underlay.color.a = 0.3



    def GetDragData(self, *args):
        l = []
        if not self.IsChargeEmpty():
            l.extend(self.GetChargeDragNodes())
        if l:
            return l
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if shift:
            godmaStateManager = sm.StartService('godma').stateManager
            isGroupable = godmaStateManager.IsGroupable(self.module.groupID)
            if not isGroupable:
                return []
            if getattr(self, 'module', None):
                sm.ScatterEvent('OnStartSlotLinkingMode', self.module.typeID)
        l.append(uix.GetItemData(self.module, 'list'))
        return l



    def OnDropData(self, dragObj, nodes):
        chargeTypeID = None
        chargeItems = []
        for node in nodes:
            if node.__guid__ not in ('listentry.InvItem', 'xtriui.InvItem', 'listentry.InvFittingItem'):
                continue
            item = node.rec
            if not getattr(item, 'typeID', None):
                lg.Info('fittingUI', 'Dropped a non-item here', item)
                return 
            if self.isChargeable and self.IsCharge(item.typeID):
                if chargeTypeID is None:
                    chargeTypeID = item.typeID
                if chargeTypeID == item.typeID:
                    chargeItems.append(item)
            elif sm.GetService('godma').GetStateManager().IsInWeaponBank(item.itemID):
                ret = eve.Message('CustomQuestion', {'header': mls.UI_GENERIC_CONFIRM,
                 'question': mls.UI_SHARED_WEAPONLINK_UNFIT}, uiconst.YESNO)
                if ret == uiconst.ID_YES:
                    eve.Message('DragDropSlot')
                    uthread.new(self.Add, item)
            elif item.categoryID == const.categorySubSystem and getattr(self, 'module', None) is not None:
                if not sm.GetService('godma').GetStateManager().CheckFutileSubSystemSwitch(item.typeID, item.itemID):
                    eve.Message('DragDropSlot')
                    uthread.new(self.Add, item)
            else:
                eve.Message('DragDropSlot')
                uthread.new(self.Add, item)

        if len(chargeItems):
            sm.GetService('godma').GetStateManager().DropLoadChargeToModule(self.id, chargeTypeID, chargeItems=chargeItems)



    def IsChargeEmpty(self):
        return self.charge is None



    def GetChargeType(self):
        if self.IsChargeEmpty():
            return None
        return self.charge.typeID



    def GetChargeDragNodes(self, *args):
        if not self.charge:
            return []
        return [uix.GetItemData(self.charge, 'list')]



exports = {'xtriui.FittingSlot': FittingSlot}

