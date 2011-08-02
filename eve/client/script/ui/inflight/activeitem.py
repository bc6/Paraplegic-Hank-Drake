import xtriui
import base
import uix
import uiutil
import util
import blue
import state
import uthread
import uiconst
import uicls

class ActiveItem(uicls.Window):
    __guid__ = 'form.ActiveItem'
    __notifyevents__ = ['OnMultiSelect',
     'ProcessSessionChange',
     'OnStateChange',
     'DoBallRemove',
     'OnDistSettingsChange',
     'OnPlanetViewChanged']
    default_pinned = True
    default_top = 16
    default_height = 92
    default_width = 256
    default_minSize = (default_width, default_height)

    def default_left(self):
        dw = uicore.desktop.width
        (leftpush, rightpush,) = sm.GetService('neocom').GetSideOffset()
        return dw - 256 - 16 - rightpush



    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        panelname = attributes.panelname
        self.scope = 'inflight'
        self.canAnchorToOthers = 0
        self.lastActionSerial = None
        self.lastSessionChange = None
        self.laseUpdateWidth = None
        self.lastIcon = None
        self.lastBountyCheck = None
        self.bounty = None
        self.gaugesInited = None
        self.sr.actions = None
        self.sr.updateTimer = None
        self.panelID = None
        self.itemIDs = []
        self.panelname = panelname
        self.lastActionDist = None
        self.sr.hint = None
        self.sr.blink = None
        self.actions = {mls.UI_CMD_SHOWINFO: ('ui_44_32_24', 0, 0, 0, 0, 'selectedItemShowInfo', 'CmdShowItemInfo'),
         mls.UI_CMD_APPROACH: ('ui_44_32_23', 0, 0, 0, 0, 'selectedItemApproach', 'CmdApproachItem'),
         mls.UI_CMD_ALIGNTO: ('ui_44_32_59', 0, 0, 0, 0, 'selectedItemAlignTo', 'CmdAlignToItem'),
         mls.UI_CMD_ORBIT: ('ui_44_32_21', 0, 0, 1, 0, 'selectedItemOrbit', 'CmdOrbitItem'),
         mls.UI_CMD_KEEPATRANGE: ('ui_44_32_22', 0, 0, 1, 0, 'selectedItemKeepAtRange', 'CmdKeepItemAtRange'),
         mls.UI_CMD_LOCKTARGET: ('ui_44_32_17', 0, 0, 0, 0, 'selectedItemLockTarget', 'CmdToggleTargetItem'),
         mls.UI_CMD_UNLOCKTARGET: ('ui_44_32_17', 0, 0, 0, 1, 'selectedItemUnLockTarget', 'CmdToggleTargetItem'),
         mls.UI_CMD_LOOKAT: ('ui_44_32_20', 0, 0, 0, 0, 'selectedItemLookAt', 'CmdToggleLookAtItem'),
         mls.UI_CMD_RESETCAMERA: ('ui_44_32_20', 0, 0, 0, 1, 'selectedItemResetCamera', None),
         mls.UI_CMD_STARTCONVERSATION: ('ui_44_32_33', 0, 0, 0, 0, 'selectedItemStartConversation', None),
         mls.UI_CMD_OPENCARGO: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemOpenCargo', None),
         mls.UI_PI_ACCESSCARGOLINK: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemOpenCargo', None),
         mls.UI_PI_VIEW_IN_PLANET_MODE: ('ui_77_32_34', 0, 0, 0, 0, 'selectedItemViewInPlanetMode', None),
         mls.UI_PI_EXIT_PLANET_MODE: ('ui_77_32_35', 0, 0, 0, 0, 'selectedItemExitPlanetMode', None),
         mls.UI_CMD_ACCESSREFINERY: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemAccessRefinery', None),
         mls.UI_CMD_ACCESSTRONTIUMSTORAGE: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemAccessTrontiumStorage', None),
         mls.UI_CMD_ACCESSFUELSTORAGE: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemAccessFuelStorage', None),
         mls.UI_CMD_ACCESSAMMUNITION: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemAccessAmmunition', None),
         mls.UI_CMD_ACCESSCRYSTALSTORAGE: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemAccessCrystalStorage', None),
         mls.UI_CMD_ACCESSSTORAGE: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemAccessStorage', None),
         mls.UI_CMD_ACCESSVESSELS: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemAccessVessels', None),
         mls.UI_CMD_ENGAGETARGET: ('ui_44_32_4', 0, 0, 0, 0, 'selectedItemEngageTarget', None),
         mls.UI_CMD_MINE: ('ui_44_32_4', 0, 0, 0, 0, 'selectedItemMine', None),
         mls.UI_CMD_MINEREPEATEDLY: ('ui_44_32_5', 0, 0, 0, 0, 'selectedItemMineRepeatedly', None),
         mls.UI_CMD_UNANCHOR: ('ui_44_32_4', 0, 0, 0, 0, 'selectedItemUnanchor', None),
         mls.UI_CMD_RETURNANDORBIT: ('ui_44_32_3', 0, 0, 0, 0, 'selectedItemReturnAndOrbit', None),
         mls.UI_CMD_RETURNTODRONEBAY: ('ui_44_32_1', 0, 0, 0, 0, 'selectedItemReturnToDroneBay', None),
         mls.UI_CMD_SCOOPTODRONEBAY: ('ui_44_32_1', 0, 0, 0, 0, 'selectedItemScoopToDroneBay', None),
         mls.UI_CMD_LAUNCHDRONES: ('ui_44_32_2', 0, 0, 0, 0, 'selectedItemLaunchDrones', None),
         mls.UI_CMD_SCOOPTOCARGOBAY: ('ui_44_32_1', 0, 0, 0, 0, 'selectedItemScoopToCargoBay', None),
         mls.UI_CMD_BOARDSHIP: ('ui_44_32_40', 0, 0, 0, 0, 'selectedItemBoardShip', None),
         mls.UI_CMD_DOCK: ('ui_44_32_9', 0, 0, 0, 0, 'selectedItemDock', 'CmdDockOrJumpOrActivateGate'),
         mls.UI_CMD_JUMP: ('ui_44_32_39', 0, 0, 0, 0, 'selectedItemJump', 'CmdDockOrJumpOrActivateGate'),
         mls.UI_CMD_ENTERWORMHOLE: ('ui_44_32_39', 0, 0, 0, 0, 'selectedItemEnterWormhole', None),
         mls.UI_CMD_ACTIVATEGATE: ('ui_44_32_39', 0, 0, 0, 0, 'selectedItemActivateGate', 'CmdDockOrJumpOrActivateGate'),
         mls.UI_CMD_READNEWS: ('ui_44_32_47', 0, 0, 0, 0, 'selectedItemReadNews', None)}
        self.postorder = [mls.UI_CMD_ORBIT,
         mls.UI_CMD_KEEPATRANGE,
         [mls.UI_CMD_LOCKTARGET, mls.UI_CMD_UNLOCKTARGET],
         [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA],
         mls.UI_CMD_SHOWINFO]
        self.groups = {const.groupStation: [mls.UI_CMD_DOCK],
         const.groupWreck: [mls.UI_CMD_OPENCARGO],
         const.groupCargoContainer: [mls.UI_CMD_OPENCARGO],
         const.groupMissionContainer: [mls.UI_CMD_OPENCARGO],
         const.groupSecureCargoContainer: [mls.UI_CMD_OPENCARGO],
         const.groupAuditLogSecureContainer: [mls.UI_CMD_OPENCARGO],
         const.groupFreightContainer: [mls.UI_CMD_OPENCARGO],
         const.groupSpawnContainer: [mls.UI_CMD_OPENCARGO],
         const.groupDeadspaceOverseersBelongings: [mls.UI_CMD_OPENCARGO],
         const.groupPlanetaryCustomsOffices: [mls.UI_PI_ACCESSCARGOLINK],
         const.groupPlanet: [[mls.UI_PI_VIEW_IN_PLANET_MODE, mls.UI_PI_EXIT_PLANET_MODE]],
         const.groupRefiningArray: [mls.UI_CMD_ACCESSREFINERY],
         const.groupMobileReactor: [mls.UI_CMD_ACCESSSTORAGE],
         const.groupControlTower: [mls.UI_CMD_ACCESSFUELSTORAGE, mls.UI_CMD_ACCESSTRONTIUMSTORAGE],
         const.groupSilo: [mls.UI_CMD_ACCESSSTORAGE],
         const.groupAssemblyArray: [mls.UI_CMD_ACCESSSTORAGE],
         const.groupMobileLaboratory: [mls.UI_CMD_ACCESSSTORAGE],
         const.groupCorporateHangarArray: [mls.UI_CMD_ACCESSSTORAGE],
         const.groupMobileMissileSentry: [mls.UI_CMD_ACCESSAMMUNITION],
         const.groupMobileHybridSentry: [mls.UI_CMD_ACCESSAMMUNITION],
         const.groupMobileProjectileSentry: [mls.UI_CMD_ACCESSAMMUNITION],
         const.groupMobileLaserSentry: [mls.UI_CMD_ACCESSCRYSTALSTORAGE],
         const.groupShipMaintenanceArray: [mls.UI_CMD_ACCESSVESSELS],
         const.groupStargate: [mls.UI_CMD_JUMP],
         const.groupWormhole: [mls.UI_CMD_ENTERWORMHOLE],
         const.groupWarpGate: [mls.UI_CMD_ACTIVATEGATE],
         const.groupBillboard: [mls.UI_CMD_READNEWS],
         const.groupAgentsinSpace: [mls.UI_CMD_STARTCONVERSATION],
         const.groupDestructibleAgentsInSpace: [mls.UI_CMD_STARTCONVERSATION],
         const.groupMiningDrone: [mls.UI_CMD_MINE,
                                  mls.UI_CMD_MINEREPEATEDLY,
                                  mls.UI_CMD_RETURNANDORBIT,
                                  [mls.UI_CMD_LAUNCHDRONES, mls.UI_CMD_RETURNTODRONEBAY, mls.UI_CMD_SCOOPTODRONEBAY]]}
        self.categories = {const.categoryShip: [mls.UI_CMD_BOARDSHIP, mls.UI_CMD_STARTCONVERSATION],
         const.categoryDrone: [mls.UI_CMD_ENGAGETARGET, mls.UI_CMD_RETURNANDORBIT, [mls.UI_CMD_LAUNCHDRONES, mls.UI_CMD_RETURNTODRONEBAY, mls.UI_CMD_SCOOPTODRONEBAY]]}
        if self.destroyed:
            return 
        self.panelID = panelname.replace(' ', '').lower()
        self.sr.main = main = uiutil.GetChild(self, 'main')
        self.SetTopparentHeight(0)
        self.SetWndIcon()
        self.SetCaption(mls.UI_GENERIC_SELECTEDITEM)
        self.SetMinSize([256, 93])
        self.MakeUnKillable()
        main.left = main.top = main.width = main.height = const.defaultPadding
        main.clipChildren = 1
        self.sr.toparea = uicls.Container(name='toparea', align=uiconst.TOTOP, parent=self.sr.main, height=36)
        self.sr.actions = uicls.Container(name='actions', align=uiconst.TOTOP, parent=self.sr.main, left=0, top=0)
        self.sr.actions.isTabStop = 1
        self.sr.iconpar = uicls.Container(name='iconpar', align=uiconst.TOPLEFT, parent=self.sr.toparea, width=32, height=32, left=1, top=2, state=uiconst.UI_HIDDEN)
        self.sr.icon = uicls.Icon(parent=self.sr.iconpar, align=uiconst.TOALL)
        self.sr.icon.OnClick = (self.ShowInfo, self.sr.icon)
        self.sr.chariconpar = uicls.Container(name='chariconpar', align=uiconst.TOPLEFT, parent=self.sr.toparea, width=32, height=32, left=37, top=2, state=uiconst.UI_HIDDEN)
        self.sr.charicon = uicls.Icon(parent=self.sr.chariconpar, align=uiconst.TOALL)
        self.sr.charicon.OnClick = (self.ShowInfo, self.sr.charicon)
        self.sr.pushCont = uicls.Container(name='push', width=39, parent=self.sr.toparea, align=uiconst.TOLEFT)
        self.sr.text = uicls.Label(text='', parent=self.sr.toparea, align=uiconst.TOTOP, autowidth=False, left=const.defaultPadding, top=const.defaultPadding, fontsize=9, letterspace=1, uppercase=1, state=uiconst.UI_DISABLED)
        self.inited = 1
        selected = sm.GetService('state').GetExclState(state.selected)
        if selected:
            self.OnMultiSelect([selected])
        else:
            self.UpdateAll()



    def UpdateActions(self):
        self.actions = {mls.UI_CMD_SHOWINFO: ('ui_44_32_24', 0, 0, 0, 0, 'selectedItemShowInfo', 'CmdShowItemInfo'),
         mls.UI_CMD_APPROACH: ('ui_44_32_23', 0, 0, 0, 0, 'selectedItemApproach', 'CmdApproachItem'),
         mls.UI_CMD_ALIGNTO: ('ui_44_32_59', 0, 0, 0, 0, 'selectedItemAlignTo', 'CmdAlignToItem'),
         mls.UI_CMD_ORBIT: ('ui_44_32_21', 0, 0, 1, 0, 'selectedItemOrbit', 'CmdOrbitItem'),
         mls.UI_CMD_KEEPATRANGE: ('ui_44_32_22', 0, 0, 1, 0, 'selectedItemKeepAtRange', 'CmdKeepItemAtRange'),
         mls.UI_CMD_LOCKTARGET: ('ui_44_32_17', 0, 0, 0, 0, 'selectedItemLockTarget', 'CmdToggleTargetItem'),
         mls.UI_CMD_UNLOCKTARGET: ('ui_44_32_17', 0, 0, 0, 1, 'selectedItemUnLockTarget', 'CmdToggleTargetItem'),
         mls.UI_CMD_LOOKAT: ('ui_44_32_20', 0, 0, 0, 0, 'selectedItemLookAt', 'CmdToggleLookAtItem'),
         mls.UI_CMD_RESETCAMERA: ('ui_44_32_20', 0, 0, 0, 1, 'selectedItemResetCamera', None),
         mls.UI_CMD_STARTCONVERSATION: ('ui_44_32_33', 0, 0, 0, 0, 'selectedItemStartConversation', None),
         mls.UI_CMD_OPENCARGO: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemOpenCargo', None),
         mls.UI_PI_ACCESSCARGOLINK: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemOpenCargo', None),
         mls.UI_PI_VIEW_IN_PLANET_MODE: ('ui_77_32_34', 0, 0, 0, 0, 'selectedItemViewInPlanetMode', None),
         mls.UI_PI_EXIT_PLANET_MODE: ('ui_77_32_35', 0, 0, 0, 0, 'selectedItemExitPlanetMode', None),
         mls.UI_CMD_ACCESSREFINERY: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemAccessRefinery', None),
         mls.UI_CMD_ACCESSTRONTIUMSTORAGE: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemAccessTrontiumStorage', None),
         mls.UI_CMD_ACCESSFUELSTORAGE: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemAccessFuelStorage', None),
         mls.UI_CMD_ACCESSAMMUNITION: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemAccessAmmunition', None),
         mls.UI_CMD_ACCESSCRYSTALSTORAGE: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemAccessCrystalStorage', None),
         mls.UI_CMD_ACCESSSTORAGE: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemAccessStorage', None),
         mls.UI_CMD_ACCESSVESSELS: ('ui_44_32_35', 0, 0, 0, 0, 'selectedItemAccessVessels', None),
         mls.UI_CMD_ENGAGETARGET: ('ui_44_32_4', 0, 0, 0, 0, 'selectedItemEngageTarget', None),
         mls.UI_CMD_MINE: ('ui_44_32_4', 0, 0, 0, 0, 'selectedItemMine', None),
         mls.UI_CMD_MINEREPEATEDLY: ('ui_44_32_5', 0, 0, 0, 0, 'selectedItemMineRepeatedly', None),
         mls.UI_CMD_UNANCHOR: ('ui_44_32_4', 0, 0, 0, 0, 'selectedItemUnanchor', None),
         mls.UI_CMD_RETURNANDORBIT: ('ui_44_32_3', 0, 0, 0, 0, 'selectedItemReturnAndOrbit', None),
         mls.UI_CMD_RETURNTODRONEBAY: ('ui_44_32_1', 0, 0, 0, 0, 'selectedItemReturnToDroneBay', None),
         mls.UI_CMD_SCOOPTODRONEBAY: ('ui_44_32_1', 0, 0, 0, 0, 'selectedItemScoopToDroneBay', None),
         mls.UI_CMD_LAUNCHDRONES: ('ui_44_32_2', 0, 0, 0, 0, 'selectedItemLaunchDrones', None),
         mls.UI_CMD_SCOOPTOCARGOBAY: ('ui_44_32_1', 0, 0, 0, 0, 'selectedItemScoopToCargoBay', None),
         mls.UI_CMD_BOARDSHIP: ('ui_44_32_40', 0, 0, 0, 0, 'selectedItemBoardShip', None),
         mls.UI_CMD_DOCK: ('ui_44_32_9', 0, 0, 0, 0, 'selectedItemDock', 'CmdDockOrJumpOrActivateGate'),
         mls.UI_CMD_JUMP: ('ui_44_32_39', 0, 0, 0, 0, 'selectedItemJump', 'CmdDockOrJumpOrActivateGate'),
         mls.UI_CMD_ENTERWORMHOLE: ('ui_44_32_39', 0, 0, 0, 0, 'selectedItemEnterWormhole', None),
         mls.UI_CMD_ACTIVATEGATE: ('ui_44_32_39', 0, 0, 0, 0, 'selectedItemActivateGate', 'CmdDockOrJumpOrActivateGate'),
         mls.UI_CMD_READNEWS: ('ui_44_32_47', 0, 0, 0, 0, 'selectedItemReadNews', None)}



    def Blink(self, on_off = 1):
        if on_off and self.sr.blink is None:
            self.sr.blink = uicls.Fill(parent=self.sr.top, padding=(1, 1, 1, 1), color=(1.0, 1.0, 1.0, 0.25))
        if on_off:
            sm.GetService('ui').BlinkSpriteA(self.sr.blink, 0.25, 500, None, passColor=0)
        elif self.sr.blink:
            sm.GetService('ui').StopBlink(self.sr.blink)
            b = self.sr.blink
            self.sr.blink = None
            b.Close()



    def BlinkBtn(self, key):
        for btn in self.sr.actions.children:
            if btn.name.replace(' ', '').lower() == key.replace(' ', '').lower():
                sm.GetService('ui').BlinkSpriteA(btn.children[0], 1.0, 500, None, passColor=0)
            else:
                sm.GetService('ui').StopBlink(btn.children[0])




    def OnResizeUpdate(self, *args):
        self.CheckActions(forceSizeUpdate=1, ignoreScaling=1)



    def CheckActions(self, forceSizeUpdate = 0, ignoreScaling = 0):
        if self.destroyed or not self.sr.actions:
            return 
        self.sr.toparea.height = max(40, self.sr.text.textheight + self.sr.text.top * 2)
        scaling = getattr(self, 'scaling', 0) if ignoreScaling == 0 else 0
        if forceSizeUpdate and not scaling and self.ImVisible():
            (l, t, w, h,) = self.GetAbsolute()
            (al, at, aw, ah,) = self.sr.actions.GetAbsolute()
            maxHeight = t + h - at - 8
            sm.GetService('tactical').LayoutButtons(self.sr.actions, uiconst.UI_PICKCHILDREN, maxHeight)
            (gl, gt, gr, gb,) = sm.GetService('window').GetGroupRect(self.sr.actions.children)
            diff = gb - (t + h - 6)
            if diff > 0:
                self.SetHeight(self.height + diff)



    def OnClose_(self, *args):
        self.sr.updateTimer = None



    def ProcessSessionChange(self, isRemote, session, change):
        self.lastActionSerial = None
        self.lastActionDist = None
        self.lastSessionChange = blue.os.GetTime()



    def OnMultiSelect(self, itemIDs):
        self.itemIDs = itemIDs
        self.lastActionSerial = None
        self.lastActionDist = None
        self.lastBountyCheck = None
        self.bounty = None
        if self.ImVisible():
            uthread.pool('ActiveItem::UpdateAll', self.UpdateAll, 1)



    def OnStateChange(self, itemID, flag, true, *args):
        if itemID != eve.session.shipid and not self.destroyed:
            uthread.new(self._OnStateChange, itemID, flag, true)



    def _OnStateChange(self, itemID, flag, true):
        if flag == state.selected and true:
            self.OnMultiSelect([itemID])
        if itemID in self.itemIDs and flag not in (state.selected, state.mouseOver):
            self.lastActionSerial = None
            self.lastActionDist = None
            self.UpdateAll()



    def OnDistSettingsChange(self):
        uthread.new(self._OnDistSettingsChange)



    def _OnDistSettingsChange(self):
        self.lastActionSerial = None
        self.UpdateAll(1)



    def TryGetInvItem(self, itemID):
        if eve.session.shipid is None:
            return 
        ship = eve.GetInventoryFromId(eve.session.shipid)
        if ship:
            for invItem in ship.List():
                if invItem.itemID == itemID:
                    return invItem




    def GetItem(self, itemID):
        item = uix.GetBallparkRecord(itemID)
        if not item:
            item = self.TryGetInvItem(itemID)
        return item



    def Load(self, itemID):
        pass



    def OnTabSelect(self, *args):
        if not getattr(self, 'inited', 0):
            return 
        self.lastActionSerial = None
        self.UpdateAll(1)



    def OnExpanded(self, *args):
        if not getattr(self, 'inited', 0):
            return 
        self.lastActionSerial = None
        self.UpdateAll(1)



    def OnEndMaximize(self):
        if not getattr(self, 'inited', 0):
            return 
        self.lastActionSerial = None
        self.UpdateAll(1)



    def ShowHint(self, hint = None):
        if self.sr.hint is None and hint:
            self.sr.hint = uicls.CaptionLabel(text=hint, parent=self.sr.main, align=uiconst.RELATIVE, left=16, top=18, width=256)
        elif self.sr.hint:
            if hint:
                self.sr.hint.text = hint
                self.sr.hint.state = uiconst.UI_DISABLED
            else:
                self.sr.hint.state = uiconst.UI_HIDDEN



    def FlushContent(self):
        self.SetText('')
        self.ShowHint(mls.UI_INFLIGHT_NOOBJECTSELECTED)
        self.sr.actions.Flush()
        self.sr.iconpar.state = uiconst.UI_HIDDEN
        self.sr.chariconpar.state = uiconst.UI_HIDDEN
        self.HideGauges()



    def UpdateAll(self, updateActions = 0):
        if not self or self.destroyed:
            return 
        if eve.session.shipid in self.itemIDs:
            self.itemIDs.remove(eve.session.shipid)
        bp = sm.GetService('michelle').GetBallpark()
        if not self.ImVisible() or not bp or not self.itemIDs:
            self.sr.updateTimer = None
            self.FlushContent()
            return 
        goForSlim = 1
        slimItems = []
        invItems = []
        fleetMember = None
        for itemID in self.itemIDs:
            blue.pyos.BeNice()
            if sm.GetService('fleet').IsMember(itemID):
                fleetMember = cfg.eveowners.Get(itemID)
                break
            slimItem = None
            if goForSlim:
                slimItem = uix.GetBallparkRecord(itemID)
                if slimItem:
                    slimItems.append(slimItem)
            if not slimItem:
                invItem = self.TryGetInvItem(itemID)
                if invItem:
                    invItems.append(invItem)
                    goForSlim = 0

        if not slimItems and not invItems and not fleetMember:
            self.itemIDs = []
            self.lastActionSerial = None
            self.lastActionDist = None
            self.FlushContent()
            return 
        if not self or self.destroyed:
            return 
        text = ''
        blue.pyos.BeNice()
        updateActions = updateActions or 0
        typeID = None
        groupID = None
        fleetSlim = None
        if fleetMember:
            multi = 1
            text = fleetMember.name
            typeID = fleetMember.typeID
            typeOb = cfg.invtypes.Get(typeID)
            groupID = typeOb.groupID
            categoryID = typeOb.categoryID
            fleetSlim = self.GetSlimItemForCharID(fleetMember.id)
            blue.pyos.BeNice()
        elif invItems:
            text = uix.GetItemName(invItems[0])
            typeID = invItems[0].typeID
            typeOb = cfg.invtypes.Get(typeID)
            groupID = typeOb.groupID
            categoryID = typeOb.categoryID
            multi = len(invItems)
            blue.pyos.BeNice()
        elif slimItems:
            text = uix.GetSlimItemName(slimItems[0])
            typeID = slimItems[0].typeID
            groupID = slimItems[0].groupID
            categoryID = slimItems[0].categoryID
            multi = len(slimItems)
            if multi == 1:
                slimItem = slimItems[0]
                itemID = slimItem.itemID
                ball = bp.GetBall(itemID)
                if not ball:
                    self.itemIDs = []
                    self.sr.updateTimer = None
                    self.FlushContent()
                    return 
                dist = ball.surfaceDist
                if dist is not None:
                    md = None
                    myball = bp.GetBall(eve.session.shipid)
                    if myball:
                        md = myball.mode
                    text += '<br>%s: %s' % (mls.UI_GENERIC_DISTANCE, util.FmtDist(dist, maxdemicals=1))
                    if not self.lastActionDist or md != self.lastActionDist[1] or self.CheckDistanceUpdate(self.lastActionDist[0], dist):
                        self.lastActionDist = (dist, md)
                        updateActions = 1
                sec = slimItem.securityStatus
                if sec:
                    text += '<br>%s: %.1f' % (mls.UI_GENERIC_SECURITYSHORT, sec)
            blue.pyos.BeNice()
        corpID = None
        charID = None
        categoryID = None
        bountyItemID = None
        bountyTypeID = None
        bountySlim = None
        if multi > 1:
            self.HideGauges()
            text += '<br>%s (%d)' % (mls.UI_INFLIGHT_MULTIITEMSSELECTED, multi)
            blue.pyos.BeNice()
        elif multi == 1:
            if slimItems:
                if categoryID == const.categoryAsteroid or groupID in (const.groupAsteroidBelt,
                 const.groupPlanet,
                 const.groupMoon,
                 const.groupSun,
                 const.groupHarvestableCloud,
                 const.groupSecondarySun) or slimItems[0].itemID not in sm.GetService('target').GetTargets():
                    self.HideGauges()
                else:
                    damage = self.GetDamage(slimItems[0].itemID)
                    if damage:
                        self.SetDamageState(damage)
                    else:
                        self.HideGauges()
                if slimItems[0].categoryID == const.categoryShip:
                    if util.IsCharacter(slimItems[0].charID):
                        charID = slimItems[0].charID
                        categoryID = slimItems[0].categoryID
                if slimItems[0].categoryID == const.categoryEntity:
                    bountyTypeID = slimItems[0].typeID
                elif slimItems[0].charID:
                    bountyItemID = slimItems[0].charID
                    bountySlim = slimItems[0]
            elif fleetSlim:
                damage = self.GetDamage(fleetSlim.itemID)
                if damage:
                    self.SetDamageState(damage)
                else:
                    self.HideGauges()
            elif fleetMember:
                self.HideGauges()
            blue.pyos.BeNice()
        if self.lastIcon != (typeID, itemID, charID):
            uthread.pool('ActiveItem::GetIcon', self.GetIcon, typeID, itemID, charID, corpID, categoryID)
            self.lastIcon = (typeID, itemID, charID)
        else:
            self.sr.iconpar.state = uiconst.UI_PICKCHILDREN
            if categoryID == const.categoryShip and charID:
                self.sr.chariconpar.state = uiconst.UI_PICKCHILDREN
        if (bountyItemID, bountyTypeID) != self.lastBountyCheck:
            bounty = self.CheckBounty(bountyItemID, bountyTypeID, bountySlim)
            blue.pyos.BeNice()
            if bounty:
                self.bounty = '<br>%s: %s' % (mls.UI_GENERIC_BOUNTY, util.FmtISK(bounty))
            else:
                self.bounty = None
            self.lastBountyCheck = (bountyItemID, bountyTypeID)
        if self.bounty:
            text += self.bounty
        if updateActions:
            self.ReloadActions(slimItems, invItems, fleetMember, fleetSlim)
        else:
            self.CheckActions(1)
        self.SetText(text)
        self.ShowHint()
        blue.pyos.BeNice()
        self.laseUpdateWidth = self.absoluteRight - self.absoluteLeft
        if not self.sr.updateTimer and not invItems:
            self.sr.updateTimer = base.AutoTimer(500, self.UpdateAll)



    def DoBallRemove(self, ball, slimItem, terminal):
        if self.ImVisible() and ball and ball.id in self.itemIDs:
            uthread.pool('ActiveItem::UpdateAll', self.UpdateAll, 1)



    def SetText(self, text):
        if text != self.sr.text.text:
            self.sr.text.text = text
            self.CheckActions(1)



    def GetIcon(self, typeID, itemID, charID, corpID, categoryID):
        self.sr.icon.LoadIconByTypeID(typeID, itemID=itemID, ignoreSize=True)
        self.sr.icon.typeID = typeID
        self.sr.icon.itemID = itemID
        self.sr.iconpar.state = uiconst.UI_PICKCHILDREN
        self.sr.chariconpar.state = uiconst.UI_HIDDEN
        self.sr.pushCont.width = 39
        if categoryID == const.categoryShip and charID:
            typeID = cfg.eveowners.Get(charID).typeID
            self.sr.charicon.LoadIconByTypeID(typeID, itemID=charID, ignoreSize=True)
            self.sr.charicon.typeID = typeID
            self.sr.charicon.itemID = charID
            self.sr.pushCont.width = 75
            self.sr.chariconpar.state = uiconst.UI_PICKCHILDREN



    def CheckBounty(self, bountyItemID, bountyTypeID, slimItem):
        bounty = None
        if bountyTypeID:
            tmp = [ each for each in sm.GetService('godma').GetType(bountyTypeID).displayAttributes if each.attributeID == const.attributeEntityKillBounty ]
            if tmp:
                bounty = tmp[0].value
        elif slimItem:
            bounty = slimItem.bounty
        return bounty



    def GetSlimItemForCharID(self, charID):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark:
            for (itemID, rec,) in ballpark.slimItems.iteritems():
                if rec.charID == charID:
                    return rec




    def ShowInfo(self, btn, *args):
        if btn and btn.typeID:
            sm.GetService('info').ShowInfo(btn.typeID, btn.itemID)



    def CheckDistanceUpdate(self, lastdist, dist):
        diff = abs(lastdist - dist)
        if not diff:
            return False
        else:
            if dist:
                return bool(diff / dist > 0.01)
            return bool(lastdist != dist)



    def GetDamage(self, itemID):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            self.sr.dmgTimer = None
            return 
        ret = bp.GetDamageState(itemID)
        if ret is None:
            self.sr.dmgTimer = None
        return ret



    def SetDamageState(self, state):
        self.InitGauges()
        visible = 0
        for (i, gauge,) in enumerate((self.sr.gauge_shield, self.sr.gauge_armor, self.sr.gauge_structure)):
            if state[i] is None:
                gauge.state = uiconst.UI_HIDDEN
            else:
                gauge.sr.bar.width = max(int((gauge.width - 2) * state[i]), 0)
                gauge.state = uiconst.UI_DISABLED
                visible += 1

        self.gaugesVisible = visible



    def HideGauges(self):
        if self.gaugesInited:
            self.sr.gaugeParent.state = uiconst.UI_HIDDEN
            self.CheckActions(1)
            return 



    def InitGauges(self):
        if self.gaugesInited:
            self.sr.gaugeParent.state = uiconst.UI_NORMAL
            self.CheckActions(1)
            return 
        par = uicls.Container(name='gauges', parent=self.sr.toparea, align=uiconst.TORIGHT, width=82, idx=0, state=uiconst.UI_DISABLED)
        uicls.Container(name='push', parent=par, align=uiconst.TOTOP, height=4)
        uicls.Container(name='push', parent=par, align=uiconst.TORIGHT, width=18)
        for each in ('SHIELD', 'ARMOR', 'STRUCTURE'):
            g = uicls.Container(name=each, align=uiconst.TOTOP, width=64, height=9)
            uicls.Container(name='push', parent=g, align=uiconst.TOBOTTOM, height=2)
            uicls.Label(text=getattr(mls, 'UI_GENERIC_' + each + 'SHORT', each), parent=g, left=68, top=-1, width=64, autowidth=False, state=uiconst.UI_DISABLED, fontsize=9, letterspace=1, uppercase=1)
            g.name = 'gauge_%s' % each.lower()
            uicls.Line(parent=g, align=uiconst.TOTOP)
            uicls.Line(parent=g, align=uiconst.TOBOTTOM)
            uicls.Line(parent=g, align=uiconst.TOLEFT)
            uicls.Line(parent=g, align=uiconst.TORIGHT)
            g.sr.bar = uicls.Fill(parent=g, align=uiconst.TOLEFT)
            uicls.Fill(parent=g, color=(158 / 256.0,
             11 / 256.0,
             14 / 256.0,
             1.0))
            par.children.append(g)
            setattr(self.sr, 'gauge_%s' % each.lower(), g)

        self.sr.gaugeParent = par
        self.gaugesInited = 1
        self.CheckActions(1)



    def ImVisible(self):
        return bool(self.state != uiconst.UI_HIDDEN and not self.IsCollapsed() and not self.IsMinimized())



    def ReloadActions(self, slimItems, invItems, fleetMember, fleetSlim):
        if not self or self.destroyed:
            return 
        if not self.ImVisible():
            self.sr.updateTimer = None
            return 
        itemIDs = []
        actions = []
        if invItems:
            data = [ (invItem, 0, None) for invItem in invItems ]
            actions = sm.StartService('menu').InvItemMenu(data)
        elif slimItems:
            celestialData = []
            for slimItem in slimItems:
                celestialData.append((slimItem.itemID,
                 None,
                 slimItem,
                 0,
                 None,
                 None,
                 None))

            actions = sm.StartService('menu').CelestialMenu(celestialData, ignoreTypeCheck=1)
        elif fleetSlim:
            actions = sm.GetService('menu').CelestialMenu(fleetSlim.itemID, slimItem=fleetSlim, ignoreTypeCheck=1)
        elif fleetMember:
            actions = sm.GetService('menu').CharacterMenu(fleetMember.id)
        reasonsWhyNotAvailable = getattr(actions, 'reasonsWhyNotAvailable', {})
        warptoLabel = sm.GetService('menu').DefaultWarpToLabel()[0]
        warpops = {warptoLabel: ('ui_44_32_18', 0, 0, 1, 0, 'selectedItemWarpTo', 'CmdWarpToItem')}
        if not self or self.destroyed:
            return 
        self.actions.update(warpops)
        serial = ''
        valid = {}
        inactive = None
        for each in actions:
            if each:
                if isinstance(each[0], tuple):
                    name = each[0][0]
                else:
                    name = each[0]
                if name == 'Inactive':
                    inactive = each[1]
                elif name in self.actions:
                    valid[name] = each
                    if type(each[1]) not in (str, unicode):
                        serial += '%s_' % name

        if inactive:
            for each in inactive:
                if isinstance(each[0], tuple):
                    name = each[0][0]
                else:
                    name = each[0]
                if name in self.actions:
                    valid[name] = each
                    if type(each[1]) not in (str, unicode):
                        serial += '%s_' % name

        blue.pyos.BeNice()
        ph = None
        if serial != self.lastActionSerial:
            if self.absoluteLeft == 0:
                blue.pyos.synchro.Yield()
            if self.destroyed:
                return 
            self.sr.actions.Flush()
            self.sr.actions.height = 0
            groupID = None
            categoryID = None
            if slimItems:
                groupID = slimItems[0].groupID
                categoryID = slimItems[0].categoryID
            elif invItems:
                groupID = invItems[0].groupID
                categoryID = invItems[0].categoryID
            isAlignDisabled = type(valid.get(mls.UI_CMD_ALIGNTO, ('', ''))[1]) in (str, unicode)
            approachOrAlign = [mls.UI_CMD_APPROACH, mls.UI_CMD_ALIGNTO][(not isAlignDisabled)]
            order = [approachOrAlign, warptoLabel]
            if groupID and groupID in self.groups:
                order += self.groups[groupID]
            elif categoryID and categoryID in self.categories:
                order += self.categories[categoryID]
            order += self.postorder
            for actionName in order:
                if actionName is None:
                    continue
                if isinstance(actionName, tuple):
                    actionName = actionName[0]
                if type(actionName) == list:
                    action = None
                    for each in actionName:
                        tryaction = valid.get(each, None)
                        if tryaction and type(tryaction[1]) not in (str, unicode):
                            actionName = each
                            action = tryaction
                            break

                    if action is None:
                        actionName = actionName[0]
                        if actionName in valid:
                            action = valid.get(actionName)
                        elif actionName in reasonsWhyNotAvailable:
                            action = (actionName, reasonsWhyNotAvailable.get(actionName))
                        action = (actionName, mls.UI_SHARED_NOREASONGIVEN)
                elif actionName in valid:
                    action = valid.get(actionName)
                elif actionName in reasonsWhyNotAvailable:
                    action = (actionName, reasonsWhyNotAvailable.get(actionName))
                else:
                    action = (actionName, mls.UI_SHARED_NOREASONGIVEN)
                if isinstance(action[0], tuple):
                    temp = (action[0][0],) + action[1:]
                    action = temp
                disabled = type(action[1]) in (str, unicode)
                actionID = action[0]
                par = uicls.Container(parent=self.sr.actions, align=uiconst.TOPLEFT, width=32, height=32, state=uiconst.UI_HIDDEN)
                props = self.actions[actionID]
                if len(props) >= 6:
                    par.name = props[5]
                else:
                    par.name = actionID
                if len(props) >= 7:
                    cmdName = props[6]
                else:
                    cmdName = ''
                icon = xtriui.Action(icon=props[0], parent=par, align=uiconst.TOALL)
                icon.actionID = actionID
                icon.action = action
                icon.itemIDs = self.itemIDs[:]
                icon.killsub = props[3]
                icon.cmdName = cmdName
                frame = uicls.Frame(parent=par, color=(1.0,
                 1.0,
                 1.0,
                 (0.5, 0.25)[disabled]))
                if disabled:
                    icon.opacity = 0.5
                if ph and props[2]:
                    uicls.Fill(parent=par, align=uiconst.RELATIVE, height=ph, width=30, left=1, top=31 - ph)
                    icon.OnClick = None
                if props[4]:
                    x = uicls.Icon(icon='ui_44_32_8', parent=par, left=1, top=1, align=uiconst.TOALL, state=uiconst.UI_DISABLED, idx=0)

            self.lastActionSerial = serial
        self.CheckActions(1)



    def OnPlanetViewChanged(self, newPlanetID, oldPlanetID):
        for planetID in (newPlanetID, oldPlanetID):
            if planetID in self.itemIDs:
                self.OnMultiSelect(self.itemIDs)





