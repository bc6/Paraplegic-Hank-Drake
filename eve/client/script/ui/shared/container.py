from __future__ import division
import xtriui
import uix
import uiutil
import blue
import _weakref
import lg
import uthread
import util
import listentry
import base
import service
import sys
import uiconst
import uicls
import log
colMargin = rowMargin = 12

class VirtualInvWindow(uicls.Window):
    __guid__ = 'form.VirtualInvWindow'
    __notifyevents__ = ['OnSessionChanged', 'OnPostCfgDataChanged']

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.items = []
        self.startedUp = 0
        self.cols = None
        self.droppedIconData = (None, None)
        self.iconWidth = 64
        self.iconHeight = 92
        self.sr.resizeTimer = None
        self.shellSemaphore = uthread.Semaphore()
        self.tmpDropIdx = {}
        self.refreshingView = 0
        self.displayName = mls.UI_GENERIC_CONTAINER
        self.hasCapacity = 0
        self.locationFlag = None
        self.oneWay = 0
        self.viewOnly = 0
        self.enableQuickFilter = 1
        self.quickFilterInput = None
        self.totalCount = None
        self.changeViewModeThread = None
        self.minHeight = 34
        self.maxHeight = 68
        self.hintText = None



    def Startup(self, *args):
        self.SetMinSize((256, 180))
        self.SetWndIcon('ui_3_64_13', mainTop=-13, size=128)
        self.SetMainIconSize(64)
        self.SetTopparentHeight(self.minHeight)
        self.sr.topParent.clipChildren = 0
        self.sr.right = uicls.Container(name='right', align=uiconst.TORIGHT, parent=self.sr.topParent, left=const.defaultPadding, state=uiconst.UI_PICKCHILDREN)
        self.sr.right.width = 100 + const.defaultPadding * 2
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, state=uiconst.UI_PICKCHILDREN, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.sr.id = 'containerWnd_%s' % getattr(self, 'displayName', 'Generic')
        self.sr.scroll.OnNewHeaders = self.OnNewHeadersSet
        self.sr.scroll.allowFilterColumns = 1
        self.sr.scroll.SetColumnsHiddenByDefault(uix.GetInvItemDefaultHiddenHeaders())
        self.ownProxy = _weakref.proxy(self)
        self.sr.scroll.dad = self.ownProxy
        content = self.sr.scroll.sr.content
        content.OnDropData = self.OnContentDropData
        content.OnClick = self.OnClickContent
        content.GetMenu = lambda : GetContainerMenu(self.ownProxy)
        self.sr.cookie = sm.GetService('inv').Register(self)
        if self.enableQuickFilter:
            boxTop = const.defaultPadding + 6
            self.sr.quickFilterClear = uicls.Icon(icon='ui_73_16_210', parent=self.sr.right, pos=(82,
             boxTop + 1,
             16,
             16), align=uiconst.TOPLEFT)
            self.sr.quickFilterClear.state = uiconst.UI_HIDDEN
            self.sr.quickFilterClear.Click = self.ClearQuickFilterInput
            self.sr.quickFilterClear.hint = mls.UI_CMD_CLEAR
            self.sr.quickFilterClear.OnMouseEnter = self.Nothing
            self.sr.quickFilterClear.OnMouseDown = self.Nothing
            self.sr.quickFilterClear.OnMouseUp = self.Nothing
            self.sr.quickFilterClear.OnMouseExit = self.Nothing
            self.sr.quickFilterClear.OnClick = self.sr.quickFilterClear.Click
            self.sr.quickFilterClear.keepselection = False
            self.sr.quickFilterInputBox = uicls.SinglelineEdit(name='', parent=self.sr.right, pos=(const.defaultPadding,
             boxTop,
             100,
             0), align=uiconst.TOPRIGHT, OnChange=self.SetQuickFilterInput)
            self.sr.quickFilterInputBox.SetHistoryVisibility(0)
            uicore.registry.SetFocus(self.sr.scroll)
        if self.hasCapacity:
            self.minHeight = 52
            self.SetTopparentHeight(self.minHeight)
            self.SetMinSize((256, 198))
            self.capacityText = uicls.Label(text=' ', name='capacityText', parent=self.sr.right, left=const.defaultPadding, top=29, letterspace=1, fontsize=10, state=uiconst.UI_DISABLED, uppercase=0, color=(1.0, 1.0, 1.0, 1.0), align=uiconst.TOPRIGHT)
            self.sr.gaugeParent = uicls.Container(name='gaugeParent', align=uiconst.TOPRIGHT, parent=self.sr.right, left=const.defaultPadding, height=7, width=100, state=uiconst.UI_DISABLED, top=self.capacityText.top + self.capacityText.textheight + 1)
            uicls.Frame(parent=self.sr.gaugeParent, color=(0.5, 0.5, 0.5, 0.3))
            self.sr.gauge = uicls.Container(name='gauge', align=uiconst.TOLEFT, parent=self.sr.gaugeParent, state=uiconst.UI_PICKCHILDREN, width=0)
            uicls.Fill(parent=self.sr.gaugeParent, color=(0.0, 0.521, 0.67, 0.1))
            uicls.Fill(parent=self.sr.gauge, color=(0.0, 0.521, 0.67, 0.6))
            if self.sr.Get('quickFilterInputBox', None) is not None:
                self.sr.quickFilterInputBox.top = 7
                self.sr.quickFilterClear.top = 8
        i = 0
        j = 0
        for (num, hint, attrname, group, func,) in [(156,
          mls.UI_GENERIC_ICONS,
          'iconsModeBtn',
          'viewMode',
          lambda *args: self.ChangeViewMode(0)), (157,
          mls.UI_GENERIC_DETAILS,
          'detailsModeBtn',
          'viewMode',
          lambda *args: self.ChangeViewMode(1)), (158,
          mls.UI_GENERIC_LIST,
          'listModeBtn',
          'viewMode',
          lambda *args: self.ChangeViewMode(2))]:
            icon = xtriui.MiniButton(icon='ui_38_16_%s' % num, selectedIcon='ui_38_16_%s' % (num + 16), mouseOverIcon='ui_38_16_%s' % (num + 32), parent=self.sr.topParent, pos=(i * 13 + 52,
             10 + j * 18,
             16,
             16), align=uiconst.TOPLEFT)
            icon.groupID = group
            icon.hint = hint
            setattr(self.sr, attrname, icon)
            icon.Click = func
            if attrname == 'commandMode':
                icon.keepselection = False
            i += 1
            if i == 3:
                j += 1
                i = 0

        (self.sortIconsBy, self.sortIconsDir,) = settings.user.ui.Get('containerSortIconsBy_%s' % self.name, ('type', 0))
        self.viewMode = settings.user.ui.Get('containerViewMode_%s' % self.name, 'icons')
        uthread.new(self.ChangeViewMode, ['icons', 'details', 'list'].index(self.viewMode))
        self.invReady = 1



    def Nothing(self, *args):
        pass



    def SetQuickFilterInput(self, *args):
        uthread.new(self._SetQuickFilterInput)



    def _SetQuickFilterInput(self):
        blue.synchro.Sleep(400)
        filter = self.sr.quickFilterInputBox.GetValue()
        if len(filter) > 0:
            self.quickFilterInput = filter.lower()
            self.Refresh()
            self.sr.quickFilterClear.state = uiconst.UI_NORMAL
        else:
            prefilter = self.quickFilterInput
            self.quickFilterInput = None
            if prefilter != None:
                self.Refresh()
            self.sr.quickFilterClear.state = uiconst.UI_HIDDEN
            self.hintText = None



    def ClearQuickFilterInput(self, *args):
        self.hintText = None
        self.sr.quickFilterInputBox.SetValue('')



    def QuickFilter(self, rec):
        name = uix.GetItemName(rec).lower()
        typename = cfg.invtypes.Get(rec.typeID).name.lower()
        input = self.quickFilterInput.lower()
        return name.find(input) + 1 or typename.find(input) + 1



    def FilterOptionsChange(self, combo, label, value, *args):
        if combo and combo.name == 'filterCateg':
            if value is None:
                ops = [(mls.UI_GENERIC_ALL, None)]
            else:
                ops = sm.GetService('marketutils').GetFilterops(value)
            self.sr.filterGroup.LoadOptions(ops)
            settings.user.ui.Set('containerCategoryFilter%s' % self.name.title(), value)
        elif combo and combo.name == 'filterGroup':
            settings.user.ui.Set('containerGroupFilter%s' % self.name.title(), value)
        self.Refresh()



    def OnSessionChanged(self, isRemote, session, change):
        if not self or self.destroyed:
            return 
        if 'solarsystemid2' in change and session.solarsystemid2:
            self.Refresh()
        elif 'stationid2' in change and session.stationid2:
            self.Refresh()



    def OnPostCfgDataChanged(self, what, data):
        if what == 'evelocations':
            itemID = data[0]
            for each in self.sr.scroll.GetNodes():
                if each and getattr(each, 'item', None) and each.item.itemID == itemID:
                    each.name = None
                    uix.GetItemLabel(each.item, each, 1)
                    if each.panel:
                        each.panel.UpdateLabel()
                    return 




    def OnClose_(self, *args):
        self.ownProxy = None
        self.shellSemaphore = None
        self.items = None
        if self is not None and not self.destroyed and self.sr.Get('scroll', None) and self.sr.scroll.sr.content:
            for attr in ('OnDropData', 'OnClick', 'GetMenu'):
                if hasattr(self.sr.scroll.sr.content, attr):
                    setattr(self.sr.scroll.sr.content, attr, None)

            self.sr.scroll.dad = None
            self.sr.scroll = None
        self.capacityGauge = None
        self.capacityText = None
        if getattr(self, 'itemchangeTimer', None):
            self.itemchangeTimer.KillTimer()



    def IsMine(self, rec):
        raise NotImplementedError



    def List(self):
        if self.locationFlag:
            return self.GetShell().List(self.locationFlag)
        else:
            return self.GetShell().List()



    def Add(self, itemID, sourceLocation, quantity, dividing = False):
        dropLocation = self.GetShell().GetItem().itemID
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        stateMgr = sm.StartService('godma').GetStateManager()
        item = dogmaLocation.dogmaItems.get(itemID)
        if dropLocation == sourceLocation and not dividing:
            if getattr(item, 'flagID', None):
                if item.flagID == self.locationFlag:
                    return 
        if itemID is None:
            raise RuntimeError('None itemID???')
        if self.oneWay and not dividing and eve.Message('ConfirmOneWayItemMove', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return 
        else:
            if self.locationFlag:
                item = stateMgr.GetItem(itemID)
                if item and self.locationFlag == const.flagCargo and cfg.IsShipFittingFlag(item.flagID):
                    containerArgs = self.GetContainerArgs()
                    if item.categoryID == const.categoryCharge:
                        return dogmaLocation.UnloadChargeToContainer(item.locationID, item.itemID, containerArgs, self.locationFlag, quantity)
                    if item.categoryID == const.categoryModule:
                        return stateMgr.UnloadModuleToContainer(item.locationID, item.itemID, containerArgs, self.locationFlag)
                return self.GetShell().Add(itemID, sourceLocation, qty=quantity, flag=self.locationFlag)
            flag = None
            shell = self.GetShell()
            if getattr(shell, 'typeID', None) and cfg.invtypes.Get(shell.typeID).groupID == const.groupAuditLogSecureContainer:
                thisContainer = eve.GetInventoryFromId(self.id).item
                rollsNotNeeded = thisContainer is not None and (util.IsStation(thisContainer.locationID) or thisContainer.locationID == session.shipid)
                flag = settings.user.ui.Get('defaultContainerLock_%s' % shell.itemID, None)
                if flag is None:
                    flag = const.flagLocked
                if not rollsNotNeeded:
                    if flag == const.flagLocked and charsession.corprole & const.corpRoleEquipmentConfig == 0:
                        if eve.Message('ConfirmAddLockedItemToAuditContainer', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                            return 
                return self.GetShell().Add(itemID, sourceLocation, qty=quantity, flag=flag)
            return self.GetShell().Add(itemID, sourceLocation, qty=quantity)



    def MultiMerge(self, data, mergeSourceID):
        if self.oneWay and eve.Message('ConfirmOneWayItemMove', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return 
        ret = None
        try:
            dataReduced = []
            for d in data:
                dataReduced.append((d[0], d[1], d[2]))

            self.GetShell().MultiMerge(dataReduced, mergeSourceID)
        except UserError as what:
            if len(data) == 1 and what.args[0] in ('NotEnoughCargoSpace', 'NotEnoughCargoSpaceOverload', 'NotEnoughDroneBaySpace', 'NotEnoughDroneBaySpaceOverload', 'NoSpaceForThat', 'NoSpaceForThatOverload', 'NotEnoughChargeSpace'):
                cap = self.GetCapacity()
                free = cap.capacity - cap.used
                if free < 0:
                    raise 
                item = data[0][3]
                if item.typeID == const.typePlasticWrap:
                    volume = eve.GetInventoryFromId(item.itemID).GetCapacity().used
                else:
                    volume = cfg.GetItemVolume(item, 1)
                maxQty = min(item.stacksize, int(free / (volume or 1)))
                if maxQty <= 0:
                    if volume < 0.01:
                        req = 0.01
                    else:
                        req = util.FmtAmt(volume, showFraction=2)
                    eve.Message('NotEnoughCargoSpaceFor1Unit', {'typeName': cfg.invtypes.Get(item.typeID).name,
                     'free': util.FmtAmt(free, showFraction=2),
                     'required': req})
                    return 
                if self.DBLessLimitationsCheck(what.args[0], item):
                    return 
                if maxQty == item.stacksize:
                    errmsg = mls.UI_INFLIGHT_NOMOREUNITSINSOURCE
                else:
                    errmsg = mls.UI_INFLIGHT_NOROOMFORMOREINDEST
                ret = uix.QtyPopup(int(maxQty), 0, int(maxQty), errmsg)
                if ret is None:
                    quantity = None
                else:
                    quantity = ret['qty']
                if quantity:
                    self.GetShell().MultiMerge([(data[0][0], data[0][1], quantity)], mergeSourceID)
            else:
                raise 
            sys.exc_clear()



    def GetCapacity(self):
        return self.GetShell().GetCapacity(self.locationFlag)



    def DoGetShell(self):
        raise NotImplementedError



    def GetContainerArgs(self):
        return (self.itemID,)



    def ChangeViewMode(self, viewMode = 0):
        if self.changeViewModeThread:
            self.changeViewModeThread.kill()
        self.changeViewModeThread = uthread.new(self._ChangeViewMode, viewMode)



    def _ChangeViewMode(self, viewMode = 0):
        blue.pyos.synchro.Yield()
        if not self or self.destroyed:
            return 
        self.viewMode = ['icons', 'details', 'list'][viewMode]
        settings.user.ui.Set('containerViewMode_%s' % self.name, self.viewMode)
        self.sr.Get('%sModeBtn' % self.viewMode, None).Select()
        self.items = filter(self.IsMine, self.List())
        if self.enableQuickFilter and len(self.items):
            if self.quickFilterInput:
                self.totalCount = len(self.items)
                self.items = uiutil.NiceFilter(self.QuickFilter, self.items)
                self.UpdateHint()
                blue.pyos.synchro.Yield()
        try:
            if self.viewMode == 'icons':
                self.SortIconsBy(self.sortIconsBy, self.sortIconsDir)
            else:
                self.RefreshView()
        except UserError:
            self.SelfDestruct()
            if self.sr.Get('cookie', None):
                sm.GetService('inv').Unregister(self.sr.cookie)
            raise 
        self.DelayOnItemChange()



    def UpdateHint(self):
        if len(self.items) == 0:
            self.hintText = mls.UI_GENERIC_NOTHINGFOUND
        else:
            self.hintText = ''
        self.sr.scroll.ShowHint(self.hintText)



    def Refresh(self):
        self.ChangeViewMode(['icons', 'details', 'list'].index(self.viewMode))



    def SortIconsBy(self, sortby, direction):
        self.sortIconsBy = sortby
        self.sortIconsDir = direction
        settings.user.ui.Set('containerSortIconsBy_%s' % self.name, (sortby, direction))
        sortData = []
        for rec in self.items:
            if rec is None:
                continue
            name = uix.GetItemName(rec).lower()
            type = uix.GetCategoryGroupTypeStringForItem(rec).lower()
            id = rec.itemID
            qty = 0
            if not (rec.singleton or rec.typeID in (const.typeBookmark,)):
                qty = rec.stacksize
            if sortby == 'name':
                sortKey = (name,
                 type,
                 qty,
                 id,
                 rec)
            elif sortby == 'qty':
                sortKey = (qty,
                 type,
                 name,
                 id,
                 rec)
            elif sortby == 'type':
                sortKey = (type,
                 name,
                 qty,
                 id,
                 rec)
            else:
                log.LogError('Unknown sortkey used in container sorting', sortby, direction)
                continue
            sortData.append((sortKey, rec))

        sorted = uiutil.SortListOfTuples(sortData)
        if direction:
            sorted.reverse()
        self.items = sorted
        self.RefreshView()



    def OnResizeUpdate(self, *args):
        if self.startedUp and not self.destroyed:
            self.sr.resizeTimer = base.AutoTimer(250, self.OnEndScale_)
            if self.hasCapacity:
                uthread.new(self.RefreshCapacity)



    def OnEndScale_(self, *etc):
        self.sr.resizeTimer = None
        if self.startedUp and not self.destroyed and self.viewMode == 'icons':
            if getattr(self, 'refreshingView', False):
                self.reRefreshView = True
                return 
            oldcols = self.cols
            self.RefreshCols()
            if oldcols != self.cols:
                uthread.new(self.RefreshView)



    def AddItem(self, rec, index = None, fromWhere = None):
        if self.enableQuickFilter:
            if self.quickFilterInput:
                if not self.QuickFilter(rec):
                    return 
        lg.Info('vcont', 'AddItem', fromWhere, rec.stacksize, cfg.invtypes.Get(rec.typeID).name)
        for node in self.sr.scroll.sr.nodes:
            if self.viewMode in ('details', 'list'):
                if node is not None and node.Get('item', None) and node.item.itemID == rec.itemID:
                    lg.Warn('vcont', 'Tried to add an item that is already there??')
                    self.UpdateItem(node.item)
                    return 
            else:
                for internalNode in node.internalNodes:
                    if internalNode is not None and internalNode.item.itemID == rec.itemID:
                        lg.Warn('vcont', 'Tried to add an item that is already there??')
                        self.UpdateItem(internalNode.item)
                        return 


        self.PrimeItems([rec])
        if self.viewMode in ('details', 'list'):
            self.items.append(rec)
            self.sr.scroll.AddEntries(-1, [listentry.Get('InvItem', data=uix.GetItemData(rec, self.viewMode, self.viewOnly, container=self, scrollID=self.sr.scroll.sr.id))])
        else:
            if index is not None:
                while index < len(self.items):
                    if self.items[index] is None:
                        return self.SetItem(index, rec)
                    index += 1

                while index >= len(self.sr.scroll.sr.nodes) * self.cols:
                    self.AddRow()

                return self.SetItem(index, rec)
            else:
                if len(self.items) and None in self.items:
                    idx = self.tmpDropIdx.get(rec.itemID, None)
                    if idx is None:
                        idx = self.items.index(None)
                    return self.SetItem(idx, rec)
                if not self.cols:
                    self.RefreshCols()
                if index >= len(self.sr.scroll.sr.nodes) * self.cols:
                    self.AddRow()
                return self.SetItem(0, rec)



    def UpdateItem(self, rec, *etc):
        lg.Info('vcont', 'UpdateItem', rec and '[%s %s]' % (rec.stacksize, cfg.invtypes.Get(rec.typeID).name))
        if self.viewMode in ('details', 'list'):
            idx = 0
            for each in self.items:
                if each.itemID == rec.itemID:
                    self.items[idx] = rec
                    break
                idx += 1

            for entry in self.sr.scroll.sr.nodes:
                if entry.item.itemID == rec.itemID:
                    newentry = uix.GetItemData(rec, self.viewMode, self.viewOnly, container=self, scrollID=self.sr.scroll.sr.id)
                    entry.__dict__.update(newentry.__dict__)
                    if entry.panel:
                        entry.panel.Load(entry)
                    return 

        else:
            i = 0
            for rowNode in self.sr.scroll.sr.nodes:
                for entry in rowNode.internalNodes:
                    if entry is not None and entry.item and entry.item.itemID == rec.itemID:
                        self.SetItem(i, rec)
                        return 
                    i += 1


        lg.Warn('vcont', 'Tried to update an item that is not there??')



    def RemoveItem(self, rec):
        lg.Info('vcont', 'RemoveItem', rec and '[%s %s]' % (rec.stacksize, cfg.invtypes.Get(rec.typeID).name))
        if self.viewMode in ('details', 'list'):
            for entry in self.sr.scroll.sr.nodes:
                if entry.item.itemID == rec.itemID:
                    self.sr.scroll.RemoveEntries([entry])
                    break

            for item in self.items:
                if item.itemID == rec.itemID:
                    self.items.remove(item)

        else:
            i = 0
            for rowNode in self.sr.scroll.sr.nodes:
                si = 0
                for entry in rowNode.internalNodes:
                    if entry and entry.item and entry.item.itemID == rec.itemID:
                        self.SetItem(i, None)
                        rowNode.internalNodes[si] = None
                        break
                    si += 1
                    i += 1


            i = 0
            for item in self.items:
                if item and item.itemID == rec.itemID:
                    self.items[i] = None
                i += 1

            self.CleanupRows()



    def CleanupRows(self):
        rm = []
        for rowNode in self.sr.scroll.sr.nodes:
            internalNodes = rowNode.Get('internalNodes', [])
            if internalNodes == [None] * len(internalNodes):
                rm.append(rowNode)
            else:
                rm = []

        if rm:
            self.sr.scroll.RemoveEntries(rm)



    def OnInvChange(self, item = None, change = None):
        if not self or self.destroyed:
            return 
        self.itemchangeTimer = base.AutoTimer(1000, self.DelayOnItemChange, item, change)



    def DelayOnItemChange(self, item = None, change = None, delay = True):
        if eve.session.mutating:
            if not self or self.destroyed:
                if self:
                    self.itemchangeTimer = None
                return 
            self.itemchangeTimer = base.AutoTimer(1000, self.DelayOnItemChange, item, change)
            return 
        if self.destroyed:
            return 
        self.itemchangeTimer = None
        self.UpdateCaption()
        if delay and self.viewMode in ('details', 'list'):
            self.RefreshView()
        if self.hasCapacity:
            uthread.new(self.RefreshCapacity)



    def AddRow(self):
        self.items += [None] * self.cols
        self.sr.scroll.AddEntries(-1, [listentry.Get('VirtualContainerRow', {'lenitems': len(self.sr.scroll.sr.nodes) * self.cols,
          'rec': [None] * self.cols,
          'internalNodes': [None] * self.cols})])
        self.sr.scroll.UpdatePosition()



    def OnContentDropData(self, dragObj, nodes):
        idx = None
        if self.viewMode == 'icons' and self.cols:
            (l, t,) = self.sr.scroll.GetAbsolutePosition()
            idx = self.cols * len(self.sr.scroll.sr.nodes) + (uicore.uilib.x - l) // (64 + colMargin)
        self.OnDropDataWithIdx(nodes, idx)



    def OnDropData(self, dragObj, nodes):
        self.OnDropDataWithIdx(nodes)



    def OnDropDataWithIdx(self, nodes, idx = None):
        self.sr.scroll.ClearSelection()
        bms = []
        inv = []
        hasChargeLoaded = -1
        sourceLocation = None
        if len(nodes) and nodes[0].Get('scroll', None):
            nodes[0].scroll.ClearSelection()
        for (i, node,) in enumerate(nodes):
            if node.Get('__guid__', None) == 'listentry.PlaceEntry' and self.OnItemDropBookmark(node):
                bms.append(node)
                continue
            if node.Get('__guid__', None) in ('xtriui.ShipUIModule', 'xtriui.InvItem', 'listentry.InvItem', 'xtriui.FittingSlot', 'listentry.InvFittingItem'):
                if node.rec.categoryID == const.categoryCharge and cfg.IsShipFittingFlag(node.item.flagID):
                    hasChargeLoaded = i
                inv.append(node)
                if sourceLocation is None:
                    sourceLocation = node.rec.locationID

        if idx is not None:
            for (i, node,) in enumerate(bms + inv):
                self.tmpDropIdx[node.itemID] = idx + i

        if len(inv):
            shell = self.GetShell()
            if shell and shell.GetItemID() != sourceLocation and not sm.GetService('consider').ConfirmTakeFromContainer(sourceLocation):
                return 
            if shell and session.shipid and shell.GetItemID() == session.shipid and shell.GetItemID() != sourceLocation and not sm.GetService('consider').ConfirmTakeIllicitGoods([ node.item for node in inv ]):
                return 
            if inv[0].Get('scroll', None) == self.sr.scroll:
                for node in inv:
                    idx = self.tmpDropIdx.get(node.itemID, None)
                    if idx is None:
                        if None in self.items:
                            idx = self.items.index(None)
                        else:
                            idx = len(self.items)
                    self.OnItemDrop(idx, node)

                return 
            if len(inv) == 1:
                if hasattr(inv[0].item, 'flagID') and cfg.IsShipFittingFlag(inv[0].item.flagID):
                    itemKey = inv[0].item.itemID
                    locationID = inv[0].item.locationID
                    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
                    containerArgs = self.GetContainerArgs()
                    if inv[0].item.locationID == util.GetActiveShip():
                        if self.oneWay and eve.Message('ConfirmOneWayItemMove', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                            return 
                        if inv[0].item.categoryID == const.categoryCharge:
                            return dogmaLocation.UnloadChargeToContainer(locationID, itemKey, containerArgs, self.locationFlag)
                        if inv[0].item.categoryID == const.categoryModule:
                            return dogmaLocation.UnloadModuleToContainer(locationID, itemKey, containerArgs, self.locationFlag)
                self._Add(inv[0].item, sourceLocation=sourceLocation)
            else:
                if self.oneWay and eve.Message('ConfirmOneWayItemMove', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                    return 
                else:
                    itemIDs = [ node.itemID for node in inv ]
                    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
                    masters = dogmaLocation.GetAllSlaveModulesByMasterModule(sourceLocation)
                    if masters:
                        inBank = 0
                        for itemID in itemIDs:
                            if dogmaLocation.IsInWeaponBank(sourceLocation, itemID):
                                inBank = 1
                                break

                        if inBank:
                            ret = eve.Message('CustomQuestion', {'header': mls.UI_GENERIC_CONFIRM,
                             'question': mls.UI_SHARED_WEAPONLINK_UNFITMANY}, uiconst.YESNO)
                            if ret != uiconst.ID_YES:
                                return 
                    if hasChargeLoaded >= 0:
                        log.LogInfo('A module with a db item charge dropped from ship fitting into some container. Cannot use multimove, must remove charge first.')
                        ret = [self._Add(inv[hasChargeLoaded].item)]
                        inv.remove(inv[hasChargeLoaded])
                        for node in inv:
                            ret.append(self._Add(node.item))

                        return ret
                    if getattr(shell, 'typeID', None) and cfg.invtypes.Get(shell.typeID).groupID == const.groupAuditLogSecureContainer:
                        flag = settings.user.ui.Get('defaultContainerLock_%s' % shell.itemID, None)
                        if flag is None:
                            flag = const.flagLocked
                        return self._MultiAdd(itemIDs, sourceLocation, flag=flag)
                    if self.locationFlag:
                        return self._MultiAdd(itemIDs, sourceLocation, flag=self.locationFlag)
                    return self._MultiAdd(itemIDs, sourceLocation)
        addum = [ node.bm.bookmarkID for node in bms ]
        if addum:
            if len(addum) > 5:
                eve.Message('CannotMoveBookmarks')
                return 
            uthread.new(self.AddBookmarks, addum)



    def _MultiAdd(self, itemIDs, sourceLocation, flag = None):
        return self.GetShell().MultiAdd(itemIDs, sourceLocation, flag=flag)



    def ContainerAllowsSplit(self):
        try:
            itemID = self.itemID
        except AttributeError:
            return True
        containerItem = sm.GetService('godma').GetItem(itemID)
        if containerItem is not None and containerItem.categoryID == const.categoryStructure and containerItem.groupID != const.groupCorporateHangarArray:
            return False
        return True



    def OnItemDrop(self, index, node):
        log.LogInfo('OnItemDrop', index, node.item)
        if uicore.uilib.Key(uiconst.VK_SHIFT) and node.item.stacksize > 1 and self.ContainerAllowsSplit():
            ret = uix.QtyPopup(node.item.stacksize, 0, 1, None, mls.UI_GENERIC_DIVIDESTACK)
            if ret is not None and ret['qty'] > 0:
                self.Add(node.item.itemID, node.item.locationID, ret['qty'], dividing=True)
        elif self.viewMode not in ('details', 'list'):
            self.RemoveItem(node.item)
            self.AddItem(node.item, index)



    def OnItemDropBookmark(self, node):
        raise UserError('CanOnlyCreateVoucherInPersonalHangar')
        return False



    def UpdateIndexRegister(self):
        pass



    def AddBookmark(self, bookmarkID):
        self.AddBookmarks([bookmarkID])



    def AddBookmarks(self, bookmarkIDs):
        flag = None
        if self.oneWay and eve.Message('ConfirmOneWayItemMove', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return 
        if self.locationFlag:
            flag = self.locationFlag
        else:
            flag = const.flagNone
            shell = self.GetShell()
            shellType = cfg.invtypes.Get(shell.GetTypeID())
            if shellType.groupID == const.groupAuditLogSecureContainer:
                flag = settings.user.ui.Get('defaultContainerLock_%s' % shell.itemID, None)
                if flag is None:
                    flag = const.flagLocked
            elif shellType.groupID == const.groupStation:
                flag = const.flagHangar
        if flag is None:
            raise RuntimeError('OK Where am I going, I dont know myself.')
        if flag == const.flagDroneBay:
            raise UserError('ItemCannotBeInDroneBay')
        isMove = not uicore.uilib.Key(uiconst.VK_SHIFT)
        self.GetShell().AddBookmarks(bookmarkIDs, flag, isMove)



    def SetItem(self, index, rec):
        lg.Info('vcont', 'SetItem', index, rec and '[%s %s]' % (rec.stacksize, cfg.invtypes.Get(rec.typeID).name))
        if not self or self.destroyed:
            return 
        if index < len(self.items) and rec and self.items[index] is not None and self.items[index].itemID != rec.itemID:
            while index < len(self.items) and self.items[index] is not None:
                index += 1

        if self.cols:
            rowIndex = index // self.cols
        else:
            rowIndex = 0
        while rowIndex >= len(self.sr.scroll.sr.nodes):
            self.AddRow()
            uiutil.Update(self, 'Container::SetItem')

        while index >= len(self.items):
            self.items += [None]

        self.items[index] = rec
        try:
            self.sr.scroll.sr.nodes[rowIndex].rec[index % self.cols] = rec
            self.UpdateHint()
            node = None
            if rec:
                node = uix.GetItemData(rec, self.viewMode, self.viewOnly, container=self, scrollID=self.sr.scroll.sr.id)
                if not self or self.destroyed:
                    return 
                node.scroll = self.sr.scroll
                node.panel = None
                node.idx = index
                node.__guid__ = 'xtriui.InvItem'
            self.sr.scroll.sr.nodes[(index // self.cols)].internalNodes[index % self.cols] = node
        except IndexError:
            return 
        icon = self.GetIcon(index)
        if icon:
            if rec is None:
                icon.state = uiconst.UI_HIDDEN
                icon.sr.node = None
            else:
                icon.state = uiconst.UI_NORMAL
                node.panel = icon
                node.viewOnly = self.viewOnly
                icon.Load(node)



    def GetShell(self):
        return self.DoGetShell()



    def RefreshCols(self):
        w = self.sr.scroll.GetContentWidth()
        self.cols = max(1, w // (64 + colMargin))



    def PrimeItems(self, itemlist):
        locations = []
        for rec in itemlist:
            if rec.categoryID == const.categoryStation and rec.groupID == const.groupStation:
                locations.append(rec.itemID)
                locations.append(rec.locationID)
            if rec.categoryID == const.categoryShip and rec.singleton:
                locations.append(rec.itemID)

        if locations:
            cfg.evelocations.Prime(locations)



    def OnNewHeadersSet(self, *args):
        self.RefreshView()



    def RefreshView(self, *args):
        if getattr(self, 'refreshingView', False):
            return 
        self.refreshingView = 1
        try:
            self.PrimeItems([ rec for rec in self.items if rec is not None ])
            if not self or self.destroyed:
                return 
            if self.viewMode in ('details', 'list'):
                self.sr.scroll.sr.id = 'containerWnd_%s' % getattr(self, 'displayName', 'Generic')
                self.sr.scroll.hiliteSorted = 1
                scrolllist = []
                for rec in self.items:
                    if rec:
                        scrolllist.append(listentry.Get('InvItem', data=uix.GetItemData(rec, self.viewMode, self.viewOnly, container=self, scrollID=self.sr.scroll.sr.id)))

                self.sr.scroll.Load(contentList=scrolllist, headers=uix.GetInvItemDefaultHeaders(), scrollTo=self.sr.scroll.GetScrollProportion())
                self.sr.scroll.ShowHint(self.hintText)
            elif not self.cols:
                self.RefreshCols()
            self.SetTopparentHeight(self.minHeight)
            while self.items and self.items[-1] is None:
                self.items = self.items[:-1]

            content = []
            for i in range(len(self.items)):
                if not i % self.cols:
                    entry = [None] * self.cols
                    nodes = [None] * self.cols
                    content.append(listentry.Get('VirtualContainerRow', {'lenitems': i,
                     'rec': entry,
                     'internalNodes': nodes}))
                if self.items[i]:
                    node = uix.GetItemData(self.items[i], self.viewMode, self.viewOnly, container=self)
                    if not self or self.destroyed:
                        return 
                    node.scroll = self.sr.scroll
                    node.panel = None
                    node.__guid__ = 'xtriui.InvItem'
                    node.idx = i
                    nodes[i % self.cols] = node
                    entry[i % self.cols] = self.items[i]

            self.sr.scroll.sr.sortBy = None
            self.sr.scroll.sr.id = None
            self.sr.scroll.Load(fixedEntryHeight=self.iconHeight + rowMargin, contentList=content, scrollTo=self.sr.scroll.GetScrollProportion())
            self.sr.scroll.ShowHint(self.hintText)
            self.CleanupRows()
            self.startedUp = 1

        finally:
            if self and not self.destroyed:
                if self.viewMode == 'details':
                    self.sr.scroll.sr.minColumnWidth = {mls.UI_GENERIC_NAME: 44}
                    self.sr.scroll.UpdateTabStops()
                else:
                    self.sr.scroll.sr.minColumnWidth = {}
                self.refreshingView = 0
                if getattr(self, 'reRefreshView', False):
                    self.reRefreshView = False
                    self.RefreshCols()
                    uthread.new(self.RefreshView)




    def RefreshCapacity(self):
        cap = self.GetCapacity()
        if self.destroyed:
            return 
        (total, full,) = (cap.capacity, cap.used)
        self.capacityText.text = '%s/%s m\xb3' % (util.FmtAmt(full, showFraction=1), util.FmtAmt(total, showFraction=1))
        if total:
            proportion = min(1.0, max(0.0, full / float(total)))
        else:
            proportion = 1.0
        self.sr.gauge.width = int(proportion * self.sr.gaugeParent.width)



    def UpdateCaption(self, compact = 0):
        self.SetCaption(self.GetCaption(compact))
        if self.sr.stack:
            self.sr.stack.UpdateCaption()



    def GetCaption(self, compact = 0):
        if self.quickFilterInput:
            total = self.totalCount
            total = total or '0'
            if compact:
                return '%s [%s/%s]' % (self.displayName[0], len(filter(None, self.items)), total)
            return '%s [%s/%s]' % (self.displayName, len(filter(None, self.items)), total)
        else:
            if compact:
                return '%s [%s]' % (self.displayName[0], len(filter(None, self.items)))
            return '%s [%s]' % (self.displayName, len(filter(None, self.items)))



    def DBLessLimitationsCheck(self, errorName, item):
        return False



    def _Add(self, item, forceQuantity = 0, sourceLocation = None):
        log.LogInfo('_Add: item', item, ', forceQuantity', forceQuantity)
        locationID = eve.session.locationid
        for i in xrange(2):
            try:
                if locationID != eve.session.locationid:
                    return 
                else:
                    stateMgr = sm.StartService('godma').GetStateManager()
                    dgmItem = stateMgr.GetItem(item.itemID)
                    itemQuantity = item.stacksize
                    if itemQuantity == 1:
                        quantity = 1
                    elif uicore.uilib.Key(uiconst.VK_SHIFT) or forceQuantity:
                        if self.locationFlag is not None and item.flagID != self.locationFlag or item.locationID != getattr(self.GetShell(), 'itemID', None):
                            if getattr(self, 'hasCapacity', 0):
                                cap = self.GetCapacity()
                                capacity = cap.capacity - cap.used
                                itemvolume = cfg.GetItemVolume(item, 1) or 1
                                maxQty = capacity / itemvolume + 1e-07
                                maxQty = min(itemQuantity, int(maxQty))
                            else:
                                maxQty = itemQuantity
                            if maxQty == itemQuantity:
                                errmsg = mls.UI_INFLIGHT_NOMOREUNITSINSOURCE
                            else:
                                errmsg = mls.UI_INFLIGHT_NOROOMFORMOREINDEST
                            ret = uix.QtyPopup(int(maxQty), 0, int(maxQty), errmsg)
                        else:
                            ret = uix.QtyPopup(itemQuantity, 1, 1, None, mls.UI_GENERIC_DIVIDESTACK)
                        if ret is None:
                            quantity = None
                        else:
                            quantity = ret['qty']
                    else:
                        quantity = itemQuantity
                    if not item.itemID or not quantity:
                        return 
                    if locationID != eve.session.locationid:
                        return 
                    if sourceLocation is None:
                        sourceLocation = item.locationID
                    self.Add(item.itemID, sourceLocation, quantity)
                    return 
            except UserError as what:
                if what.args[0] in ('NotEnoughCargoSpace', 'NotEnoughCargoSpaceOverload', 'NotEnoughDroneBaySpace', 'NotEnoughDroneBaySpaceOverload', 'NoSpaceForThat', 'NoSpaceForThatOverload', 'NotEnoughChargeSpace', 'NotEnoughSpecialBaySpace', 'NotEnoughSpecialBaySpaceOverload'):
                    cap = self.GetCapacity()
                    free = cap.capacity - cap.used
                    if free < 0:
                        raise 
                    if item.typeID == const.typePlasticWrap:
                        volume = eve.GetInventoryFromId(item.itemID).GetCapacity().used
                    else:
                        volume = cfg.GetItemVolume(item, 1)
                    maxQty = min(item.stacksize, int(free / (volume or 1)))
                    if maxQty <= 0:
                        req = util.FmtAmt(volume, showFraction=2)
                        if float(req == 0.0):
                            req = '0.01'
                        eve.Message('NotEnoughCargoSpaceFor1Unit', {'typeName': cfg.invtypes.Get(item.typeID).name,
                         'free': util.FmtAmt(free, showFraction=2),
                         'required': req})
                        return 
                    if self.DBLessLimitationsCheck(what.args[0], item):
                        return 
                    forceQuantity = 1
                else:
                    raise 
                sys.exc_clear()




    def StackAll(self, securityCode = None):
        if self.oneWay and eve.Message('ConfirmOneWayItemMove', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return 
        inv = []
        for node in self.sr.scroll.sr.nodes:
            if node.Get('__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem', 'listentry.InvFittingItem'):
                inv.append(node)

        if inv and not sm.GetService('consider').ConfirmTakeFromContainer(inv[0].rec.locationID):
            return 
        if self.locationFlag:
            retval = self.GetShell().StackAll(self.locationFlag)
            self.Refresh()
            return retval
        try:
            if securityCode is None:
                retval = self.GetShell().StackAll()
            else:
                retval = self.GetShell().StackAll(securityCode=securityCode)
            self.Refresh()
            return retval
        except UserError as what:
            if what.args[0] == 'PermissionDenied':
                if securityCode:
                    caption = mls.UI_GENERIC_INCORRECTPASSWORD
                    label = mls.UI_GENERIC_PLEASETRYAGAIN
                else:
                    caption = mls.UI_GENERIC_PASSWORDREQUIRED
                    label = mls.UI_GENERIC_PLEASEENTERPASSWORD
                passw = uix.NamePopup(caption=caption, label=label, setvalue='', icon=-1, modal=1, btns=None, maxLength=50, passwordChar='*')
                if passw is None:
                    raise UserError('IgnoreToTop')
                else:
                    retval = self.StackAll(securityCode=passw['name'])
                    self.Refresh()
                    return retval
            else:
                raise 
            sys.exc_clear()



    def SelectAll(self):
        if not self.destroyed:
            self.sr.scroll.SelectAll()



    def InvertSelection(self):
        if not self.destroyed:
            self.sr.scroll.ToggleSelected()



    def GetIcons(self):
        return [ icon for row in self.sr.scroll.sr.content.children for icon in row.sr.icons if icon.state == uiconst.UI_NORMAL ]



    def OnClickContent(self, *etc):
        if not uicore.uilib.Key(uiconst.VK_CONTROL):
            self.sr.scroll.ClearSelection()



    def GetIcon(self, index):
        for each in self.sr.scroll.sr.content.children:
            if each.index == index // self.cols * self.cols:
                lg.Info('vcont', 'GetIcon(', index, ') returns', each.sr.icons[(index % self.cols)].name)
                return each.sr.icons[(index % self.cols)]

        lg.Info('vcont', 'GetIcon(', index, ') found nothing')



    def IsLockableContainer(self):
        return True




class Row(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.VirtualContainerRow'

    def Startup(self, dad):
        self.dad = dad.dad
        self.sr.icons = []



    def Load(self, node):
        self.sr.node = node
        self.index = node.lenitems
        for i in range(len(self.sr.icons), len(node.internalNodes)):
            icon = xtriui.InvItem(parent=self)
            icon.top = rowMargin
            icon.left = colMargin + (icon.width + colMargin) * i
            icon.state = uiconst.UI_HIDDEN
            icon.height = 92
            self.sr.icons.append(icon)

        for icon in self.sr.icons[self.dad.cols:]:
            icon.state = uiconst.UI_HIDDEN
            icon.sr.node = None
            icon.subnodeIdx = None

        i = 0
        for subnode in node.internalNodes:
            icon = self.sr.icons[i]
            if subnode is None:
                icon.state = uiconst.UI_HIDDEN
                icon.sr.node = None
                icon.subnodeIdx = None
            else:
                subnode.panel = icon
                icon.Load(subnode)
                icon.state = uiconst.UI_NORMAL
                icon.subnodeIdx = subnode.idx = self.index + i
            i += 1




    def GetMenu(self):
        return GetContainerMenu(self.dad)



    def OnDropData(self, dragObj, nodes):
        (l, t, w, h,) = self.GetAbsolute()
        index = self.index + (uicore.uilib.x - l) // (64 + colMargin)
        self.dad.OnDropDataWithIdx(nodes, index)



    def OnClick(self, *etc):
        self.dad.OnClickContent(self)




def GetContainerMenu(containerWindow):
    if eve.rookieState:
        return []
    m = [(mls.UI_CMD_SELECTALL, containerWindow.SelectAll), (mls.UI_CMD_INVERSESELECTION, containerWindow.InvertSelection)]
    if eve.session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
        m += [(mls.UI_CMD_REFRESH, containerWindow.Refresh)]
    if containerWindow.viewMode == 'icons':
        m += [(mls.UI_CMD_SORTBY, [(mls.UI_CMD_NAME, containerWindow.SortIconsBy, ('name', 0)),
           (mls.UI_CMD_NAMEREVERSED, containerWindow.SortIconsBy, ('name', 1)),
           None,
           (mls.UI_CMD_QUANTITY, containerWindow.SortIconsBy, ('qty', 0)),
           (mls.UI_CMD_QUANTITYREVERSED, containerWindow.SortIconsBy, ('qty', 1)),
           None,
           (mls.UI_CMD_TYPE, containerWindow.SortIconsBy, ('type', 0)),
           (mls.UI_CMD_TYPEREVERSED, containerWindow.SortIconsBy, ('type', 1))])]
    if containerWindow.viewOnly:
        return m
    containerItem = containerWindow.GetShell().GetItem()
    containerOwnerID = containerItem.ownerID
    myOwnerIDs = (session.charid, session.corpid, session.allianceid)
    containerSlim = sm.GetService('michelle').GetItem(containerItem.itemID)
    stackAll = containerItem.groupID in (const.groupStation, const.groupPlanetaryCustomsOffices) or containerOwnerID in myOwnerIDs or session.corpid == getattr(containerSlim, 'corpID', None) or session.allianceid and session.allianceid == getattr(containerSlim, 'allianceID', None)
    if stackAll:
        m += [(mls.UI_CMD_STACKALL, containerWindow.StackAll)]
    return m



class MiniButton(uicls.Icon):
    __guid__ = 'xtriui.MiniButton'

    def ApplyAttributes(self, attributes):
        self.idleIcon = attributes.icon
        self.selectedIcon = attributes.selectedIcon
        self.mouseOverIcon = attributes.mouseOverIcon
        uicls.Icon.ApplyAttributes(self, attributes)
        self.selected = 0
        self.groupID = None
        self.keepselection = True



    def OnMouseEnter(self, *args):
        self.LoadIcon(self.mouseOverIcon, ignoreSize=True)



    def OnMouseExit(self, *args):
        if self.selected:
            self.LoadIcon(self.selectedIcon, ignoreSize=True)
        else:
            self.LoadIcon(self.idleIcon, ignoreSize=True)



    def OnMouseDown(self, *args):
        self.LoadIcon(self.selectedIcon, ignoreSize=True)



    def OnMouseUp(self, *args):
        if uicore.uilib.mouseOver is self:
            self.LoadIcon(self.mouseOverIcon, ignoreSize=True)



    def OnClick(self, *args):
        if self.keepselection:
            self.Select()
        else:
            self.Deselect()
        self.Click()



    def Click(self, *args):
        pass



    def Deselect(self):
        self.selected = 0
        self.LoadIcon(self.idleIcon, ignoreSize=True)



    def Select(self):
        if self.groupID:
            for each in self.parent.children:
                if each is not self and hasattr(each, '__guid__') and each.__guid__ == self.__guid__ and each.groupID == self.groupID:
                    each.Deselect()

            self.selected = 1
        elif self.selected:
            self.Deselect()
        else:
            self.selected = 1
        if self.selected:
            self.LoadIcon(self.selectedIcon, ignoreSize=True)




