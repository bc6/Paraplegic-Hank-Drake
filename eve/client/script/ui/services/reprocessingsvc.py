import service
import util
import xtriui
import uix
import uiutil
import moniker
import lg
import listentry
import uthread
import sys
import uiconst
import uicls

class ReprocessingSvc(service.Service):
    __exportedcalls__ = {'ReprocessDlg': [],
     'GetReprocessingSvc': [],
     'GetOptionsForItemTypes': [],
     'IsVisible': []}
    __guid__ = 'svc.reprocessing'
    __notifyevents__ = ['ProcessSessionChange', 'DoSessionChanging']
    __servicename__ = 'reprocessing'
    __displayname__ = 'Reprocessing Service'
    __dependencies__ = ['settings']

    def __init__(self):
        service.Service.__init__(self)
        self.optionsByItemType = {}
        self.crits = {}



    def LogInfo(self, *args):
        lg.Info(self.__guid__, *args)



    def Run(self, memStream = None):
        self.LogInfo('Starting Reprocessing Service')
        self.ReleaseReprocessingSvc()



    def Stop(self, memStream = None):
        self.ReleaseReprocessingSvc()



    def __EnterCriticalSection(self, k, v = None):
        if (k, v) not in self.crits:
            self.crits[(k, v)] = uthread.CriticalSection((k, v))
        self.crits[(k, v)].acquire()



    def __LeaveCriticalSection(self, k, v = None):
        self.crits[(k, v)].release()
        if (k, v) in self.crits and self.crits[(k, v)].IsCool():
            del self.crits[(k, v)]



    def ProcessSessionChange(self, isremote, session, change):
        if 'charid' in change or 'stationid' in change:
            self.ReleaseReprocessingSvc()



    def DoSessionChanging(self, isRemote, session, change):
        if 'charid' in change or 'stationid' in change:
            sm.StopService(self.__guid__[4:])



    def GetReprocessingSvc(self):
        if hasattr(self, 'moniker') and self.moniker is not None:
            return self.moniker
        self.moniker = moniker.GetReprocessingManager()
        return self.moniker



    def ReleaseReprocessingSvc(self):
        if hasattr(self, 'moniker') and self.moniker is not None:
            self.moniker = None



    def ReprocessDlg(self, items = None, outputOwner = None, outputFlag = None):
        if eve.session.shipid:
            uthread.new(self.uthread_ReprocessDlg, items, outputOwner, outputFlag)
        elif eve.Message('AskActivateShip', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            sm.GetService('station').SelectShipDlg()



    def uthread_ReprocessDlg(self, items, outputOwner, outputFlag):
        self._ReprocessingSvc__EnterCriticalSection('reprocessingDlg')
        try:
            wnd = sm.GetService('window').GetWindow('reprocessing')
            if wnd:
                if items is not None:
                    wnd.DoSelectItems(items)
            else:
                uicore.cmd.OpenReprocessingPlant(items, outputOwner, outputFlag)
            if wnd is not None and not wnd.destroyed:
                wnd.Maximize()

        finally:
            self._ReprocessingSvc__LeaveCriticalSection('reprocessingDlg')




    def GetOptionsForItemTypes(self, itemtypes):
        typesToGet = {}
        for typeID in itemtypes.iterkeys():
            if not self.optionsByItemType.has_key(typeID):
                typesToGet[typeID] = 0

        if len(typesToGet):
            types = util.GetReprocessingOptions(typesToGet)
            for typeID in types.iterkeys():
                option = types[typeID]
                self.optionsByItemType[typeID] = option

        out = {}
        for typeID in itemtypes.iterkeys():
            if self.optionsByItemType.has_key(typeID):
                out[typeID] = self.optionsByItemType[typeID]

        return out



    def IsVisible(self):
        wnd = sm.GetService('window').GetWindow('reprocessing')
        if wnd is not None and not wnd.destroyed:
            return bool(wnd.state != uiconst.UI_HIDDEN)
        return False



MINSCROLLWIDTH = 64

class ReprocessingDialog(uicls.Window):
    __guid__ = 'form.ReprocessingDialog'
    default_width = 405
    default_height = 270

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        items = attributes.get('items', [])
        outputOwner = attributes.outputOwner
        outputFlag = attributes.outputFlag
        self.items = {}
        self.quotes = {}
        self.invCookie = None
        self.invReady = 0
        self.crits = {}
        self.closing = False
        self.outputOwnerAndFlag = [None, None]
        self.inputOwnerAndFlag = [None, None]
        self.selectedItemIDs = {}
        self.comboLocationOutput = None
        self.comboLocationInput = None
        self.reprocessing = 0
        self.scrollWidth = MINSCROLLWIDTH
        office = sm.GetService('corp').GetOffice()
        if office is None and (outputOwner is not None or outputFlag is not None):
            outputOwner = eve.session.charid
            outputFlag = const.flagHangar
        self.outputOwnerAndFlag = [outputOwner, outputFlag]
        self.SetScope('station')
        self.Confirm = self.ValidateOK
        self.OnClose_ = self.OnCloseReprocessing
        self.SetCaption(mls.UI_GENERIC_REPROCESSING)
        self.SetWndIcon('ui_17_128_1')
        self.SetMinSize([350, 270])
        (parentText, hintText,) = self._ReprocessingDialog__GetStdText()
        if self is None or self.destroyed:
            return 
        self.sr.msgparent = uicls.Label(text=parentText, parent=self.sr.topParent, fontsize=10, letterspace=1, uppercase=1, left=12, width=150, tabs=[110, 164], idx=0, autowidth=False, align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL)
        self.sr.msgparent.hint = hintText
        self.sr.msgparent.top = 3
        self.sr.textContainer = uicls.Container(name='textContainer', align=uiconst.TOBOTTOM, parent=self.sr.main, height=14, left=const.defaultPadding, top=const.defaultPadding, state=uiconst.UI_HIDDEN)
        self.sr.statusText = uicls.Label(text=mls.UI_SHARED_REPROCESSINPROGRESS, parent=self.sr.textContainer, state=uiconst.UI_DISABLED, align=uiconst.CENTERTOP)
        self.sr.mainContainer = uicls.Container(name='mainContainer', align=uiconst.TOALL, parent=self.sr.main, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.firstContainer = uicls.Container(name='firstContainer', parent=self.sr.mainContainer, align=uiconst.TOLEFT, width=286)
        divider = xtriui.Divider(name='divider', align=uiconst.TOLEFT, width=const.defaultPadding, parent=self.sr.mainContainer, state=uiconst.UI_NORMAL)
        divider.Startup(self.sr.firstContainer, 'width', 'x', MINSCROLLWIDTH, self.scrollWidth)
        divider.OnSizeChanged = self.OnVerticalDividerSizeChanged
        self.sr.divider = divider
        self.sr.itemscroll = uicls.Scroll(name='itemscroll', parent=self.sr.firstContainer)
        self.sr.itemscroll.sr.id = 'reprocess'
        self.sr.itemscroll.Load(contentList=[])
        self.sr.itemscroll.multiSelect = 0
        self.sr.itemscroll.sr.minColumnWidth = {mls.UI_GENERIC_NAME: 66}
        self.sr.itemscroll.OnNewHeaders = self.OnNewHeadersSet
        self.sr.itemscroll.allowFilterColumns = 1
        self.sr.itemscroll.SetColumnsHiddenByDefault(uix.GetInvItemDefaultHiddenHeaders())
        self.sr.quotescroll = uicls.Scroll(name='quotescroll', parent=self.sr.mainContainer)
        self.sr.quotescroll.sr.id = 'reprocessing_quotes'
        self.sr.quotescroll.Load(contentList=[])
        self.sr.standardBtns = uicls.ButtonGroup(btns=[['reprocessingServiceGetQuotesBtn',
          mls.UI_STATION_GETQUOTE,
          self.OnGetQoutes,
          (),
          81], ['reprocessingServiceReprocessBtn',
          mls.UI_CMD_REPROCESS,
          self.OnOK,
          (),
          81], ['reprocessingServiceCancelBtn',
          mls.UI_CMD_CANCEL,
          self.OnCancel,
          (),
          81]], forcedButtonNames=True, parent=self.sr.main, idx=0)
        self.sr.reprocessBtn = uiutil.GetChild(self.sr.standardBtns, 'reprocessingServiceReprocessBtn')
        self.sr.quotesBtn = uiutil.GetChild(self.sr.standardBtns, 'reprocessingServiceGetQuotesBtn')
        items = self.DoSelectItems(items)
        self.showAllItems = False
        if len(items) == 0:
            self.showAllItems = True
        items = self.DrawLocationSelector(items, outputOwner, outputFlag, office)
        self.Register()
        self.LoadItems(items)
        self._OnResize()
        self.isready = 1
        self.UpdateButtons()
        uthread.new(self.OnGetQoutes)



    def LogInfo(self, *args):
        lg.Info(self.__guid__, *args)



    def __EnterCriticalSection(self, k, v = None):
        if (k, v) not in self.crits:
            self.crits[(k, v)] = uthread.CriticalSection((k, v))
        self.crits[(k, v)].acquire()



    def __LeaveCriticalSection(self, k, v = None):
        self.crits[(k, v)].release()
        if (k, v) in self.crits and self.crits[(k, v)].IsCool():
            del self.crits[(k, v)]



    def OnComboChangeOutput(self, entry, header, value, *args):
        uthread.new(self.OnComboChangeOutputImpl, entry.name, value)



    def OnComboChangeOutputImpl(self, entryName, value):
        self.outputOwnerAndFlag = value



    def OnComboChangeInput(self, entry, header, value, *args):
        uthread.new(self.OnComboChangeInputImpl, entry.name, value)



    def OnComboChangeInputImpl(self, entryName, value):
        self.inputOwnerAndFlag = value
        self.outputOwnerAndFlag = value
        items = []
        (ownerID, flag,) = value
        if ownerID == eve.session.corpid:
            office = sm.GetService('corp').GetOffice()
            if office is not None:
                folder = eve.GetInventoryFromId(office.officeFolderID)
                folder.List()
                hangar = eve.GetInventoryFromId(office.itemID)
                items = hangar.List(flag)
        elif ownerID == eve.session.charid:
            hangar = eve.GetInventory(const.containerHangar)
            items = hangar.List(flag)
        self.selectedItemIDs = {}
        self.LoadItems(items)



    def OnShowAllCheckboxChange(self, cbox):
        self.showAllItems = cbox.GetValue()
        self._ReprocessingDialog__LoadItems()
        self._ReprocessingDialog__LoadQuotes()



    def DoSelectItems(self, items, *args):
        if items is None:
            items = []
        else:
            for item in items:
                self.selectedItemIDs[item.itemID] = True

        if getattr(self, 'isready', 0):
            calls = []
            calls.append((self._ReprocessingDialog__LoadItems, ()))
            calls.append((self._ReprocessingDialog__LoadQuotes, ()))
            uthread.parallel(calls)
        uthread.new(self.UpdateButtons)
        return items



    def OnVerticalDividerSizeChanged(self):
        (l, t, w, h,) = self.sr.firstContainer.GetAbsolute()
        absWidth = self.absoluteRight - self.absoluteLeft
        if w > absWidth - MINSCROLLWIDTH:
            w = absWidth - MINSCROLLWIDTH
            ratio = float(w) / absWidth
            settings.user.ui.Set('reprocessing_firstcontainer_width', ratio)
            self._OnResize()
            return 
        ratio = float(w) / absWidth
        settings.user.ui.Set('reprocessing_firstcontainer_width', ratio)



    def _OnResize(self, *args):
        if self and not self.destroyed and self.sr.Get('firstContainer', None) is not None:
            absWidth = self.absoluteRight - self.absoluteLeft
            self.scrollWidth = absWidth - 34 - MINSCROLLWIDTH
            width = (absWidth - 46) / 2
            ratio = settings.user.ui.Get('reprocessing_firstcontainer_width', 0.5)
            h = int(ratio * absWidth)
            if h > self.scrollWidth:
                h = self.scrollWidth
            self.sr.firstContainer.width = max(MINSCROLLWIDTH, h)
            if uiutil.GetAttrs(self.sr.itemscroll, 'sr', 'hint', '_OnResize'):
                self.sr.itemscroll.sr.hint._OnResize()
            self.sr.divider.max = self.scrollWidth



    def DrawLocationSelector(self, items, outputOwner, outputFlag, office = None):
        optlist = [[mls.UI_GENERIC_MYHANGAR, (eve.session.charid, const.flagHangar)]]
        if office is not None:
            folder = eve.GetInventoryFromId(office.officeFolderID)
            folder.List()
            hangar = eve.GetInventoryFromId(office.itemID)
            paramsByDivision = {1: (const.flagHangar, const.corpRoleHangarCanQuery1, const.corpRoleHangarCanTake1),
             2: (const.flagCorpSAG2, const.corpRoleHangarCanQuery2, const.corpRoleHangarCanTake2),
             3: (const.flagCorpSAG3, const.corpRoleHangarCanQuery3, const.corpRoleHangarCanTake3),
             4: (const.flagCorpSAG4, const.corpRoleHangarCanQuery4, const.corpRoleHangarCanTake4),
             5: (const.flagCorpSAG5, const.corpRoleHangarCanQuery5, const.corpRoleHangarCanTake5),
             6: (const.flagCorpSAG6, const.corpRoleHangarCanQuery6, const.corpRoleHangarCanTake6),
             7: (const.flagCorpSAG7, const.corpRoleHangarCanQuery7, const.corpRoleHangarCanTake7)}
            divisions = sm.GetService('corp').GetDivisionNames()
            i = 0
            while i < 7:
                i += 1
                (flag, roleCanQuery, roleCanTake,) = paramsByDivision[i]
                if eve.session.corprole & roleCanQuery != roleCanQuery:
                    continue
                if eve.session.corprole & roleCanTake != roleCanTake:
                    continue
                divisionName = divisions[i]
                optlist.append([divisionName + ' - %s' % mls.UI_GENERIC_CORPHANGAR, (eve.session.corpid, flag)])

        toppar = uicls.Container(name='options', parent=self.sr.topParent, align=uiconst.TOPLEFT, pos=(0, 0, 120, 52))
        toppar.left = 72
        theLeft = 1
        if outputOwner is not None and outputFlag is not None:
            self.comboLocationOutput = uicls.Combo(label=mls.UI_RMR_OUTPUTLOCATION, parent=toppar, options=optlist, name='location_output', callback=self.OnComboChangeOutput, pos=(theLeft,
             16,
             0,
             0), width=98, align=uiconst.TOPLEFT)
            self.comboLocationOutput.SelectItemByValue((outputOwner, outputFlag))
        else:
            self.inputOwnerAndFlag = (eve.session.charid, const.flagHangar)
            self.comboLocationInput = uicls.Combo(label=mls.UI_RMR_INPUTLOCATION, parent=toppar, options=optlist, name='location_input', callback=self.OnComboChangeInput, pos=(theLeft,
             16,
             0,
             0), width=98, align=uiconst.TOPLEFT)
            self.comboLocationInput.SelectItemByValue(self.inputOwnerAndFlag)
            hangar = eve.GetInventory(const.containerHangar)
            items = hangar.List(const.flagHangar)
        self.sr.showallcheckbox = uicls.Checkbox(text=mls.UI_STATION_SHOWALL, parent=toppar, configName='showallhangaritems', retval='show_all_items', callback=self.OnShowAllCheckboxChange, checked=self.showAllItems, pos=(theLeft,
         36,
         98,
         0))
        return items



    def LoadItems(self, items):
        self.items = {}
        self.quotes = {}
        for item in items:
            if item.flagID == const.flagReward:
                continue
            if item.groupID == const.groupMineral:
                continue
            if item.itemID in (eve.session.shipid, eve.session.charid):
                continue
            self.items[item.itemID] = item

        self._ReprocessingDialog__LoadItems()



    def OnGetQoutes(self, *args):
        uiutil.FindChild(self, 'reprocessingServiceGetQuotesBtn').Disable()
        itemKeys = []
        for item in self.sr.itemscroll.GetNodes():
            if item.checked:
                itemKeys.append(item.rec.itemID)

        if len(itemKeys):
            self.quotes = sm.GetService('reprocessing').GetReprocessingSvc().GetQuotes(itemKeys)
            self._ReprocessingDialog__LoadQuotes()
            uiutil.FindChild(self, 'reprocessingServiceReprocessBtn').Enable()



    def OnNewHeadersSet(self, *args):
        self._ReprocessingDialog__LoadItems()



    def __LoadItems(self, *args):
        if self is None or self.destroyed:
            return 
        self._ReprocessingDialog__EnterCriticalSection('__LoadItems')
        try:
            self.sr.itemscroll.ShowHint()
            itemtypes = {}
            for each in self.items.itervalues():
                if each.flagID == const.flagReward:
                    continue
                itemtypes[each.typeID] = 0

            optionsByItemType = sm.GetService('reprocessing').GetOptionsForItemTypes(itemtypes)
            scrolllist = []
            for item in self.items.itervalues():
                if item.flagID == const.flagReward:
                    continue
                option = optionsByItemType[item.typeID]
                if option.isRecyclable or option.isRefinable:
                    if item.categoryID == const.categoryAsteroid or item.groupID == const.groupHarvestableCloud:
                        flag = 1
                    else:
                        flag = 0
                    itemName = ''
                    isContainer = item.groupID in (const.groupCargoContainer,
                     const.groupSecureCargoContainer,
                     const.groupAuditLogSecureContainer,
                     const.groupFreightContainer) and item.singleton
                    if item.categoryID == const.categoryShip or isContainer:
                        shipName = cfg.evelocations.GetIfExists(item.itemID)
                        if shipName is not None:
                            itemName = shipName.locationName
                    ty = cfg.invtypes.Get(item.typeID)
                    data = uix.GetItemData(item, 'details', scrollID=self.sr.itemscroll.sr.id)
                    isChecked = [True, False][(not not item.stacksize < ty.portionSize)]
                    if isChecked:
                        if not self.selectedItemIDs.has_key(item.itemID):
                            isChecked = False
                    if not isChecked:
                        if self.selectedItemIDs.has_key(item.itemID):
                            del self.selectedItemIDs[item.itemID]
                    if not self.showAllItems and not isChecked:
                        continue
                    data.info = item
                    data.typeID = item.typeID
                    data.getIcon = 1
                    data.item = item
                    data.flag = flag
                    data.checked = isChecked
                    data.cfgname = item.itemID
                    data.retval = item.itemID
                    data.OnChange = self.OnItemSelectedChanged
                    data.scrollID = self.sr.itemscroll.sr.id
                    scrolllist.append(listentry.Get('ItemCheckbox', data))

            self.sr.itemscroll.sr.iconMargin = 24
            self.sr.itemscroll.sr.fixedEntryHeight = 24
            self.sr.itemscroll.Load(None, scrolllist, headers=uix.GetInvItemDefaultHeaders(), noContentHint=mls.UI_STATION_NOTHINGFITFORREPROCESSING)
            if not len(scrolllist):
                self.sr.itemscroll.ShowHint(mls.UI_STATION_NOTHINGFITFORREPROCESSING)

        finally:
            self._ReprocessingDialog__LeaveCriticalSection('__LoadItems')




    def OnItemSelectedChanged(self, checkbox):
        itemID = checkbox.data['retval']
        if checkbox.GetValue():
            self.LogInfo(itemID, 'CHECKED')
            item = self.items[itemID]
            ty = cfg.invtypes.Get(item.typeID)
            if item.stacksize < ty.portionSize:
                checkbox.SetValue(False)
                if self.selectedItemIDs.has_key(itemID):
                    del self.selectedItemIDs[itemID]
                raise UserError('QuantityLessThanMinimumPortion', {'typename': ty.name,
                 'portion': ty.portionSize})
            self.selectedItemIDs[itemID] = True
        else:
            self.LogInfo(itemID, 'UNCHECKED')
            if self.selectedItemIDs.has_key(itemID):
                del self.selectedItemIDs[itemID]
        self.sr.quotescroll.Clear()
        self.UpdateButtons()



    def UpdateButtons(self):
        self.sr.reprocessBtn.Disable()
        self.sr.quotesBtn.Disable()
        self.sr.quotescroll.Load(contentList=[], noContentHint=mls.UI_STATION_NOTHINGFITFORREPROCESSING)
        for item in self.sr.itemscroll.GetNodes():
            if item.checked:
                self.sr.quotesBtn.Enable()
                self.sr.quotescroll.Load(contentList=[], noContentHint=mls.UI_STATION_NOQUOTE)
                break




    def __LoadQuotes(self):
        if self is None or self.destroyed:
            return 
        self._ReprocessingDialog__EnterCriticalSection('__LoadQuotes')
        try:
            self.sr.quotescroll.ShowHint('')
            materials = {}
            for entry in self.sr.itemscroll.GetNodes():
                if entry is None or not entry.checked:
                    continue
                itemID = entry.itemID
                if not self.quotes.has_key(itemID):
                    continue
                for recoverable in self.quotes[itemID].recoverables:
                    if not materials.has_key(recoverable.typeID):
                        materials[recoverable.typeID] = (recoverable.client, recoverable.station, recoverable.unrecoverable)
                    else:
                        (client, station, unrecoverable,) = materials[recoverable.typeID]
                        materials[recoverable.typeID] = (recoverable.client + client, recoverable.station + station, recoverable.unrecoverable + unrecoverable)


            scrolllist = []
            for (typeID, quote,) in materials.iteritems():
                (client, station, unrecoverable,) = quote
                label = '%s<t>%s<t>%s<t>%s' % (cfg.invtypes.Get(typeID).typeName,
                 util.FmtAmt(client),
                 util.FmtAmt(station),
                 util.FmtAmt(unrecoverable))
                scrolllist.append(listentry.Get('Item', {'itemID': None,
                 'typeID': typeID,
                 'label': label,
                 'getIcon': 1}))

            self.sr.quotescroll.sr.iconMargin = 24
            self.sr.quotescroll.sr.fixedEntryHeight = 24
            self.sr.quotescroll.Load(None, scrolllist, headers=[mls.UI_STATION_MATERIAL,
             mls.UI_STATION_YOURECEIVE,
             mls.UI_STATION_WETAKE,
             mls.UI_STATION_UNRECOVERABLE], noContentHint=mls.UI_STATION_NOTHINGFITFORREPROCESSING)

        finally:
            self._ReprocessingDialog__LeaveCriticalSection('__LoadQuotes')




    def __GetStdText(self):
        rinfo = sm.GetService('reprocessing').GetReprocessingSvc().GetReprocessingInfo()
        owner = cfg.eveowners.Get(eve.stationItem.ownerID)
        location = cfg.evelocations.Get(eve.stationItem.itemID)
        hintText = mls.UI_STATION_TEXT43 % {'ownername': owner.name,
         'locationname': location.name,
         'yield': self.FmtPercent(rinfo['yield'], 2),
         'combinedyield': self.FmtPercent(rinfo['combinedyield'], 2),
         'wetake1': util.FmtAmt(rinfo['wetake'][1], showFraction=2),
         'wetake2': self.FmtPercent(rinfo['wetake'][0], 2)}
        parentText = mls.UI_STATION_REPROCESSINGSTATS % {'yield': '<b>%s</b>' % self.FmtPercent(rinfo['yield'], 2),
         'combinedyield': '<b>%s</b>' % self.FmtPercent(rinfo['combinedyield'], 2),
         'wetake1': '<b>%s</b>' % util.FmtAmt(rinfo['wetake'][1], showFraction=2),
         'wetake2': '<b>%s</b>' % self.FmtPercent(rinfo['wetake'][0], 2)}
        return (parentText, hintText)



    def FmtPercent(self, value, demicals = 1):
        value = value * 100.0
        return '%s%%' % util.FmtAmt(value, showFraction=demicals)



    def IsVisible(self):
        return self is not None and self.state == uiconst.UI_NORMAL



    def OnCloseReprocessing(self, *args):
        self.Unregister()
        uicls.Window.OnClose_(self, args)



    def Register(self):
        self.invReady = 1
        self.invCookie = sm.GetService('inv').Register(self)



    def Unregister(self):
        self.invReady = 0
        if getattr(self, 'invCookie', None) is not None:
            sm.GetService('inv').Unregister(self.invCookie)
            self.invCookie = None



    def IsMine(self, item):
        self.LogInfo('IsMine item:', item)
        (ownerID, flag,) = self.inputOwnerAndFlag
        if ownerID is not None and flag is not None:
            self.LogInfo('Using ownerID and flag')
            if item.flagID != flag:
                self.LogInfo('Not mine by flag')
                return False
            if item.ownerID != ownerID:
                return False
            if item.ownerID == eve.session.charid:
                if item.locationID != eve.session.stationid:
                    return False
            elif item.ownerID == eve.session.corpid:
                office = sm.GetService('corp').GetOffice()
                if office is None:
                    return False
                if item.locationID != office.itemID:
                    return False
            else:
                return False
            return True
        else:
            return self.items.has_key(item.itemID)



    def AddItem(self, item):
        self.LogInfo('AddItem item:', item)
        if item.itemID in (eve.session.shipid, eve.session.charid):
            return 
        if item.flagID == const.flagReward:
            return 
        if item.groupID == const.groupMineral:
            return 
        if self.items.has_key(item.itemID):
            return 
        if self is None or self.destroyed:
            return 
        self.items[item.itemID] = item
        quote = uthread.parallel([(sm.GetService('reprocessing').GetReprocessingSvc().GetQuotes, ([item.itemID],))])[0]
        if self is None or self.destroyed:
            return 
        if quote.has_key(item.itemID):
            self.quotes[item.itemID] = quote[item.itemID]
        elif self.quotes.has_key(item.itemID):
            del self.quotes[item.itemID]
        calls = []
        calls.append((self._ReprocessingDialog__LoadItems, ()))
        calls.append((self._ReprocessingDialog__LoadQuotes, ()))
        uthread.parallel(calls)



    def UpdateItem(self, item, change):
        self.LogInfo('UpdateItem item:', item)
        if item.itemID in (eve.session.shipid, eve.session.charid):
            return 
        if item.flagID == const.flagReward:
            return 
        if item.groupID == const.groupMineral:
            return 
        if not self.items.has_key(item.itemID):
            return 
        if self is None or self.destroyed:
            return 
        self.items[item.itemID] = item
        quote = uthread.parallel([(sm.GetService('reprocessing').GetReprocessingSvc().GetQuotes, ([item.itemID],))])[0]
        if self is None or self.destroyed:
            return 
        if quote.has_key(item.itemID):
            self.quotes[item.itemID] = quote[item.itemID]
        elif self.quotes.has_key(item.itemID):
            del self.quotes[item.itemID]
        calls = []
        calls.append((self._ReprocessingDialog__LoadItems, ()))
        calls.append((self._ReprocessingDialog__LoadQuotes, ()))
        uthread.parallel(calls)



    def RemoveItem(self, item):
        if self.reprocessing == 1:
            return 
        self.LogInfo('RemoveItem item:', item)
        if item.itemID in (eve.session.shipid, eve.session.charid):
            return 
        if item.flagID == const.flagReward:
            return 
        if item.groupID == const.groupMineral:
            return 
        if not self.items.has_key(item.itemID):
            return 
        if self is None or self.destroyed:
            return 
        if self.items.has_key(item.itemID):
            del self.items[item.itemID]
        if self.quotes.has_key(item.itemID):
            del self.quotes[item.itemID]
        if self.selectedItemIDs.has_key(item.itemID):
            del self.selectedItemIDs[item.itemID]
        calls = []
        calls.append((self._ReprocessingDialog__LoadItems, ()))
        calls.append((self._ReprocessingDialog__LoadQuotes, ()))
        uthread.parallel(calls)



    def ValidateOK(self):
        return 1



    def OnOK(self, *args):
        if not self.ValidateOK():
            return 
        items = []
        lockedItemIDs = []
        fromLocation = None
        try:
            for entry in self.sr.itemscroll.GetNodes():
                if entry is None or not entry.checked:
                    continue
                itemID = entry.itemID
                if itemID == session.shipid:
                    eve.Message('CannotReprocessActive')
                if not self.quotes.has_key(itemID):
                    continue
                item = self.items[itemID]
                if fromLocation is None:
                    fromLocation = item.locationID
                if fromLocation != item.locationID:
                    continue
                if item.categoryID == const.categoryAsteroid or item.groupID == const.groupHarvestableCloud:
                    msg = 'lockRefining'
                else:
                    msg = 'lockReprocessing'
                sm.GetService('invCache').TryLockItem(item.itemID, msg, {'itemType': cfg.invtypes.Get(item.typeID).typeName}, 1)
                lockedItemIDs.append(item.itemID)
                items.append(itemID)

            try:
                try:
                    if len(items):
                        (ownerID, flag,) = self.outputOwnerAndFlag
                        self.reprocessing = 1
                        self.sr.textContainer.state = uiconst.UI_DISABLED
                        skipChecks = []
                        while True:
                            try:
                                sm.GetService('reprocessing').GetReprocessingSvc().Reprocess(items, fromLocation, ownerID, flag, True, skipChecks)
                            except UserError as e:
                                sys.exc_clear()
                                buttons = uiconst.YESNO
                                default = uiconst.ID_YES
                                msg = cfg.GetMessage(e.msg, e.dict, onNotFound='return')
                                if msg.type not in ('warning', 'question'):
                                    buttons = None
                                    default = None
                                ret = eve.Message(e.msg, e.dict, buttons=buttons, default=default)
                                if ret == uiconst.ID_YES:
                                    skipChecks.append(e.msg)
                                    continue
                            break

                except:
                    sys.exc_clear()

            finally:
                self.Unregister()
                self.reprocessing = 0
                self.CloseX()


        finally:
            for itemID in lockedItemIDs:
                sm.GetService('invCache').UnlockItem(itemID)

            if util.GetAttrs(self, 'sr', 'textContainer') is not None:
                self.sr.textContainer.state = uiconst.UI_HIDDEN




    def OnCancel(self, *args):
        self.items = {}
        self.CloseX()




