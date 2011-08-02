import xtriui
import uiutil
import uiconst
import const
import listentry
import base
import blue
import uix
import planet
import uthread
import util
import uicls
import planetCommon

class DraggableItem(listentry.Item):
    __guid__ = 'listentry.DraggableItem'

    def GetDragData(self, *args):
        return self.sr.node.scroll.GetSelectedNodes(self.sr.node)




class PlanetaryImportExportUI(uicls.Window):
    __guid__ = 'form.PlanetaryImportExportUI'
    __notifyevents__ = ['OnItemChange',
     'OnPlanetPinsChanged',
     'OnBallparkCall',
     'OnRefreshPins']

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        cargoLinkID = attributes.cargoLinkID
        spaceportPinID = attributes.spaceportPinID
        exportMode = attributes.exportMode or False
        self.id = self.cargoLinkID = cargoLinkID
        self.cargoLink = eve.GetInventoryFromId(cargoLinkID)
        if not self.cargoLink:
            raise RuntimeError('PlanetaryImportExportUI::Cannot find cargo link with ID', cargoLinkID)
        bp = sm.GetService('michelle').GetBallpark()
        if cargoLinkID not in bp.slimItems:
            raise RuntimeError('OpenPlanetCargoLinkImportWindow::Failed to get cargo link data for link ID', cargoLinkID)
        cargoLinkItem = bp.slimItems[cargoLinkID]
        self.planetID = planetID = cargoLinkItem.planetID
        self.cargoLinkLevel = cargoLinkItem.level
        self.planet = sm.GetService('planetSvc').GetPlanet(planetID)
        self.sourceContents = {}
        self.transferContents = {}
        self.exportMode = exportMode
        self.spaceportPinID = spaceportPinID
        self.SetCaption(mls.UI_PI_IMEX_PLANETARYCUSTOMS % {'planet': cfg.evelocations.Get(self.planet.planetID).name})
        self.SetMinSize([720, 400])
        self.SetWndIcon('53_11')
        self.MakeUnstackable()
        uicls.WndCaptionLabel(text=mls.UI_PI_IMEX_PLANETARYCUSTOMS % {'planet': cfg.evelocations.Get(self.planet.planetID).name}, subcaption=mls.UI_PI_IMEX_CUSTOMS_SUBCAPTION, parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.ConstructLayout()
        self.scope = 'inflight'
        sm.GetService('inv').Register(self)
        self.ResetContents()
        self.SetImportOrExportMode(exportMode)
        blue.pyos.synchro.Yield()
        self._OnResize()



    def ConstructLayout(self):
        pad = const.defaultPadding
        self.sr.footer = uicls.Container(name='footer', parent=self.sr.main, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 25), padding=(pad,
         pad,
         pad,
         pad))
        self.sr.cols = uicls.Container(name='colums', parent=self.sr.main, align=uiconst.TOALL)
        uicls.Line(parent=self.sr.cols, align=uiconst.TOTOP)
        uicls.Line(parent=self.sr.cols, align=uiconst.TOBOTTOM)
        self.sr.col1 = uicls.Container(name='col1', parent=self.sr.cols, align=uiconst.TOLEFT, padding=(pad,
         pad,
         pad,
         pad), clipChildren=True)
        self.sr.col2 = uicls.Container(name='col2', parent=self.sr.cols, align=uiconst.TOLEFT, padding=(pad,
         pad,
         pad,
         pad), clipChildren=True)
        uicls.Line(parent=self.sr.cols, align=uiconst.TOLEFT)
        self.sr.col3 = uicls.Container(name='col3', parent=self.sr.cols, align=uiconst.TOLEFT, padding=(pad,
         pad,
         pad,
         pad), clipChildren=True)
        self.sr.radioBtns = uicls.Container(name='radioBtns', parent=self.sr.topParent, align=uiconst.TOPRIGHT, pos=(0, 10, 70, 50))
        importBox = uicls.Checkbox(text=mls.UI_CMD_IMPORT, parent=self.sr.radioBtns, configName='import', retval=0, checked=not self.exportMode, groupname='radioGroup', callback=self.OnImportExportRadiobuttonsChanged)
        exportBox = uicls.Checkbox(text=mls.UI_CMD_EXPORT, parent=self.sr.radioBtns, configName='export', retval=1, checked=self.exportMode, groupname='radioGroup', callback=self.OnImportExportRadiobuttonsChanged)
        colTopHeight = 60
        self.sr.sourceHeader = uicls.Container(name='sourceHeader', parent=self.sr.col1, align=uiconst.TOTOP, padding=(pad,
         0,
         pad,
         pad), pos=(0,
         0,
         0,
         colTopHeight))
        self.sr.sourceList = uicls.Container(name='sourceList', parent=self.sr.col1, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.sr.transferHeader = uicls.Container(name='transferHeader', parent=self.sr.col2, align=uiconst.TOTOP, padding=(pad,
         0,
         pad,
         pad), pos=(0,
         0,
         0,
         colTopHeight))
        self.sr.transferList = uicls.Container(name='transferList', parent=self.sr.col2, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.sr.destHeader = uicls.Container(name='destHeader', parent=self.sr.col3, align=uiconst.TOTOP, padding=(pad,
         0,
         pad,
         pad), pos=(0,
         0,
         0,
         colTopHeight))
        self.sr.destList = uicls.Container(name='destList', parent=self.sr.col3, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.sr.footerLeft = uicls.Container(name='footerLeft', parent=self.sr.footer, align=uiconst.TOLEFT)
        self.sr.footerRight = uicls.Container(name='footerRight', parent=self.sr.footer, align=uiconst.TORIGHT)
        btns = [(mls.UI_PI_EXPORTFROMPLANET,
          self.GoForTransfer,
          (),
          None)]
        btns = uicls.ButtonGroup(btns=btns, parent=self.sr.footerRight, line=0)
        self.transferBtn = btns.GetBtnByIdx(0)
        self.SetTransferBtnText()
        self.sr.footerText = uicls.Label(text='', parent=self.sr.transferHeader, fontsize=10, letterspace=1, top=20, state=uiconst.UI_NORMAL)
        btns = [(mls.UI_GENERIC_ADD,
          self.AddBtnClicked,
          (),
          None), (mls.UI_PI_TRANSFER_CMDREMOVE,
          self.RemoveBtnClicked,
          (),
          None)]
        btns = uicls.ButtonGroup(btns=btns, parent=self.sr.footerLeft, line=0)
        for b in btns.children[0].children:
            b.SetHint(mls.UI_PI_HINT_HOLDSHIFTTOSPLIT)

        self._PlanetaryImportExportUI__OnResizeUpdate()
        self.sr.sourceListScroll = uicls.Scroll(parent=self.sr.sourceList, name='sourceList')
        content = self.sr.sourceListScroll.sr.content
        content.OnDropData = self.OnSourceScrollDropData
        self.sr.transferHeaderText = uicls.Label(text=mls.UI_PI_TRANSFER_TRANSFERCONTENTS, parent=self.sr.transferHeader, align=uiconst.TOPLEFT, fontsize=16, state=uiconst.UI_NORMAL)
        self.sr.transferListScroll = uicls.Scroll(parent=self.sr.transferList, name='transferList')
        content = self.sr.transferListScroll.sr.content
        content.OnDropData = self.OnTransferScrollDropData
        self.sr.destListScroll = uicls.Scroll(parent=self.sr.destList)
        self.DrawSourceAndDestHeaders()
        if self.exportMode:
            uicore.registry.SetFocus(exportBox)
        else:
            uicore.registry.SetFocus(importBox)



    def DrawSourceAndDestHeaders(self):
        self.sr.sourceHeader.Flush()
        self.sr.destHeader.Flush()
        if self.exportMode:
            spaceportCont = self.sr.sourceHeader
            cargoLinkCont = self.sr.destHeader
        else:
            spaceportCont = self.sr.destHeader
            cargoLinkCont = self.sr.sourceHeader
        self.sr.cargoLinkHeader = uicls.Label(text='', parent=cargoLinkCont, align=uiconst.TOPLEFT, fontsize=16, state=uiconst.UI_NORMAL)
        self.sr.cargoLinkHeader.text = mls.UI_PI_IMEX_CUSTOMSHANGAR
        self.sr.spaceportGauge = uicls.Gauge(parent=spaceportCont, value=0.0, color=planetCommon.PLANET_COLOR_STORAGE, label='%s:' % mls.UI_GENERIC_CAPACITY, left=0, top=22, state=uiconst.UI_HIDDEN)
        self.sr.destCombo = uicls.Combo(label=None, parent=spaceportCont, options=[], name='imex_import_select', callback=self.OnSpaceportComboChanged, width=70, align=uiconst.TOTOP)



    def LoadDestComboOptions(self):
        colony = self.planet.GetColony(session.charid)
        if colony is None:
            return [(mls.UI_PI_IMEX_NOSPACEPORTS, None)]
        self.endpoints = colony.GetImportEndpoints()
        if len(self.endpoints) < 1:
            return [(mls.UI_PI_IMEX_NOSPACEPORTS, None)]
        options = []
        for endpoint in self.endpoints:
            pin = self.planet.GetPin(endpoint.id)
            options.append((planetCommon.GetGenericPinName(pin.typeID, pin.id), endpoint.id))

        if not self.spaceportPinID:
            self.spaceportPinID = options[0][1]
        self.sr.destCombo.LoadOptions(options, select=self.spaceportPinID)



    def SetTransferBtnText(self):
        if self.exportMode:
            self.transferBtn.SetLabel(mls.UI_PI_EXPORTFROMPLANET)
        else:
            self.transferBtn.SetLabel(mls.UI_PI_IMPORTTOPLANET)



    def OnTransferScrollDropData(self, dragObj, nodes, *args):
        if nodes[0].scroll.name == 'sourceList':
            self.AddCommodity(nodes)



    def OnSourceScrollDropData(self, dragObj, nodes, *args):
        if nodes[0].scroll.name == 'transferList':
            self.RemoveCommodity(nodes)



    def OnItemChange(self, item = None, change = None):
        locationIdx = const.ixLocationID
        if self.id not in (item[locationIdx], change.get(locationIdx, 'No location change')):
            return 
        self.SetCargoLinkContent()
        self.transferContents = {}
        self.RefreshLists()



    def OnRefreshPins(self, pinIDs):
        if not self or self.destroyed:
            return 
        if self.spaceportPinID in pinIDs:
            self.ResetContents()



    def OnPlanetPinsChanged(self, planetID):
        if self.planet.planetID == planetID:
            for endpoint in self.endpoints:
                if not self.planet.GetPin(endpoint.id):
                    self.CloseX()
                    return 

            self.ResetContents()



    def OnImportExportRadiobuttonsChanged(self, radioButton):
        isExport = radioButton.data['value']
        self.SetImportOrExportMode(isExport)



    def SetImportOrExportMode(self, isExport):
        if isExport:
            self.exportMode = True
            self.sourceContents = self.spaceportContents
        else:
            self.exportMode = False
            self.sourceContents = self.cargoLinkContents
        self.DrawSourceAndDestHeaders()
        self.ResetContents()
        self.SetTransferBtnText()



    def OnResizeUpdate(self, *args):
        if not self or self.destroyed:
            return 
        uthread.new(self._PlanetaryImportExportUI__OnResizeUpdate)



    def __OnResizeUpdate(self):
        if not self.sr.col1:
            return 
        (width, height,) = self.GetAbsoluteSize()
        desiredWidth = (width - 25) / 3
        self.sr.col1.width = desiredWidth
        self.sr.col2.width = desiredWidth
        self.sr.col3.width = desiredWidth
        self.sr.footerLeft.width = 2 * desiredWidth + 3 * const.defaultPadding
        self.sr.footerRight.width = desiredWidth + const.defaultPadding



    def AddBtnClicked(self, *args):
        selected = self.sr.sourceListScroll.GetSelected()
        self.AddCommodity(selected)



    def RemoveBtnClicked(self, *args):
        selected = self.sr.transferListScroll.GetSelected()
        self.RemoveCommodity(selected)



    def AddCommodity(self, commodities):
        toMove = {}
        if len(commodities) == 1 and uicore.uilib.Key(uiconst.VK_SHIFT):
            selectedItem = commodities[0]
            typeID = selectedItem.typeID
            itemID = selectedItem.itemID
            typeName = cfg.invtypes.Get(selectedItem.typeID).name
            ret = uix.QtyPopup(selectedItem.quantity, 1, selectedItem.quantity, None, mls.UI_PI_TRANSFER_SELECTQUANTITYTOTRANSFER % {'typeName': typeName})
            if ret and 'qty' in ret:
                toMove[(itemID, typeID)] = min(selectedItem.quantity, max(1, ret['qty']))
        else:
            for entry in commodities:
                toMove[(entry.itemID, entry.typeID)] = entry.quantity

        for (id, qty,) in toMove.iteritems():
            self._MoveStuff(id, qty, self.sourceContents, self.transferContents)

        self.RefreshLists()



    def RemoveCommodity(self, commodities):
        toMove = {}
        if len(commodities) == 1 and uicore.uilib.Key(uiconst.VK_SHIFT):
            selectedItem = commodities[0]
            itemID = selectedItem.itemID
            typeName = cfg.invtypes.Get(selectedItem.typeID).name
            ret = uix.QtyPopup(selectedItem.quantity, 1, selectedItem.quantity, None, mls.UI_PI_TRANSFER_SELECTQUANTITYTOREMOVE % {'typeName': typeName})
            if ret and 'qty' in ret:
                toMove[(itemID, selectedItem.typeID)] = min(selectedItem.quantity, max(1, ret['qty']))
        else:
            for entry in commodities:
                toMove[(entry.itemID, entry.typeID)] = entry.quantity

        for (id, qty,) in toMove.iteritems():
            self._MoveStuff(id, qty, self.transferContents, self.sourceContents)

        self.RefreshLists()



    def _MoveStuff(self, id, quantity, fromDict, toDict):
        fromDict[id].quantity -= quantity
        if id not in toDict:
            name = cfg.invtypes.Get(id[1]).name
            toDict[id] = util.KeyVal(itemID=fromDict[id].itemID, typeID=fromDict[id].typeID, quantity=quantity, name=name)
        else:
            toDict[id].quantity += quantity
        if fromDict[id].quantity <= 0:
            del fromDict[id]



    def GoForTransfer(self, *args):
        if len(self.transferContents) < 1:
            raise UserError('PleaseSelectCommoditiesToImport')
        if self.spaceportPinID is None:
            raise UserError('CannotImportEndpointNotFound')
        planetUI = sm.GetService('planetUI')
        planet = planetUI.GetCurrentPlanet()
        if planet is not None and planet.IsInEditMode():
            raise UserError('CannotImportExportInEditMode')
        if self.exportMode:
            transferOrder = {}
            for itemVoucher in self.transferContents.itervalues():
                transferOrder[itemVoucher.typeID] = itemVoucher.quantity

            try:
                cargoLinkInv = eve.GetInventoryFromId(self.cargoLinkID)
                cargoLinkInv.ExportFromPlanet(self.spaceportPinID, transferOrder)

            finally:
                if self and not self.destroyed:
                    self.HideLoad()

        else:
            transferOrder = {}
            for itemVoucher in self.transferContents.itervalues():
                transferOrder[itemVoucher.itemID] = itemVoucher.quantity

            try:
                cargoLinkInv = eve.GetInventoryFromId(self.cargoLinkID)
                cargoLinkInv.ImportToPlanet(self.spaceportPinID, transferOrder)

            finally:
                if self and not self.destroyed:
                    self.HideLoad()




    def SetCargoLinkContent(self):
        self.cargoLinkContents = {}
        for item in self.cargoLink.List():
            name = cfg.invtypes.Get(item.typeID).name
            self.cargoLinkContents[(item.itemID, item.typeID)] = util.KeyVal(itemID=item.itemID, typeID=item.typeID, quantity=item.stacksize, name=name)




    def SetSpaceportContent(self, spaceportID):
        self.spaceportContents = {}
        if not spaceportID:
            return 
        pin = self.planet.GetPin(spaceportID)
        if not pin:
            raise UserError('CannotImportEndpointNotFound')
        for (typeID, qty,) in pin.GetContents().iteritems():
            name = cfg.invtypes.Get(typeID).name
            self.spaceportContents[(None, typeID)] = util.KeyVal(itemID=None, typeID=typeID, quantity=qty, name=name)




    def LoadContentToScroll(self, contentList, scroll, OnDropDataCallback = None):
        scrollHeaders = ['', mls.UI_GENERIC_COMMODITY, mls.UI_GENERIC_QUANTITY]
        scrollContents = []
        scrollNoContentText = mls.UI_GENERIC_NOITEMSFOUND
        for item in contentList.values():
            lbl = '<t>%s<t>%d' % (item.name, item.quantity)
            data = util.KeyVal(label=lbl, typeID=item.typeID, itemID=item.itemID, quantity=item.quantity, getIcon=1)
            if OnDropDataCallback:
                data.OnDropData = OnDropDataCallback
            scrollContents.append(listentry.Get('DraggableItem', data=data))

        sortBy = scroll.GetSortBy()
        if sortBy is None:
            sortBy = mls.UI_GENERIC_COMMODITY
        scroll.LoadContent(contentList=scrollContents, headers=scrollHeaders, noContentHint=scrollNoContentText, sortby=sortBy)
        scroll.RefreshSort()



    def ResetContents(self):
        self.SetCargoLinkContent()
        self.SetSpaceportContent(self.spaceportPinID)
        self.transferContents = {}
        self.RefreshLists()
        self.LoadDestComboOptions()



    def RefreshLists(self, *args):
        if self.exportMode:
            dest = self.cargoLinkContents
            self.sourceContents = self.spaceportContents
        else:
            dest = self.spaceportContents
            self.sourceContents = self.cargoLinkContents
        self.LoadContentToScroll(self.sourceContents, self.sr.sourceListScroll, self.OnSourceScrollDropData)
        self.LoadContentToScroll(dest, self.sr.destListScroll)
        self.LoadContentToScroll(self.transferContents, self.sr.transferListScroll, self.OnTransferScrollDropData)
        self.RefreshHeaderInfo()



    def RefreshHeaderInfo(self):
        self.sr.spaceportGauge.state = uiconst.UI_HIDDEN
        if self.spaceportPinID is not None:
            pin = self.planet.GetPin(self.spaceportPinID)
            if not pin:
                return 
            self.sr.spaceportGauge.state = uiconst.UI_DISABLED
            self.sr.spaceportGauge.SetText(mls.UI_GENERIC_CAPACITY)
            self.sr.spaceportGauge.SetSubText('%.1f / %.1f (%3.2f%%)' % (pin.capacityUsed, pin.GetCapacity(), pin.capacityUsed / pin.GetCapacity() * 100.0))
            self.sr.spaceportGauge.SetValue(pin.capacityUsed / pin.GetCapacity())
        self.RefreshCostText()



    def OnSpaceportComboChanged(self, comboItem, spaceportName, spaceportPinID, *args):
        if self.spaceportPinID != spaceportPinID:
            self.spaceportPinID = spaceportPinID
            self.ResetContents()



    def RefreshCostText(self):
        commods = {}
        for itemVoucher in self.transferContents.itervalues():
            if itemVoucher.typeID not in commods:
                commods[itemVoucher.typeID] = itemVoucher.quantity
            else:
                commods[itemVoucher.typeID] += itemVoucher.quantity

        pin = self.planet.GetPin(self.spaceportPinID)
        if pin is not None:
            if self.exportMode:
                self.sr.footerText.text = mls.UI_PI_IMEX_IMPORTTAX % {'amount': util.FmtISK(pin.GetExportTax(commods))}
            else:
                self.sr.footerText.text = mls.UI_PI_IMEX_IMPORTTAX % {'amount': util.FmtISK(pin.GetImportTax(commods))}




