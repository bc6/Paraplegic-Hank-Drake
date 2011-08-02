import xtriui
import uiutil
import uiconst
import const
import listentry
import base
import blue
import uix
import planet
import util
import uicls
import planetCommon
import math
import uthread

class ExpeditedTransferManagementWindow(uicls.Window):
    __guid__ = 'form.ExpeditedTransferManagementWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.planet = attributes.planet
        self.path = attributes.path
        if not self.path or len(self.path) < 2:
            raise UserError('CreateRouteTooShort')
        colony = self.planet.GetColony(session.charid)
        self.sourcePin = colony.GetPin(self.path[0])
        self.destinationPin = None
        minBandwidth = None
        prevID = None
        pin = None
        for pinID in self.path:
            pin = colony.GetPin(pinID)
            if not pin:
                raise UserError('RouteFailedValidationPinDoesNotExist')
            if prevID is None:
                prevID = pinID
                continue
            link = colony.GetLink(pin.id, prevID)
            if link is None:
                raise UserError('RouteFailedValidationLinkDoesNotExist')
            if minBandwidth is None or minBandwidth > link.GetTotalBandwidth():
                minBandwidth = link.GetTotalBandwidth()
            prevID = pinID

        self.availableBandwidth = minBandwidth
        self.SetCaption(mls.UI_PI_TRANSFER_TITLE % {'typeName': planetCommon.GetGenericPinName(self.sourcePin.typeID, self.sourcePin.id)})
        self.SetMinSize([500, 400])
        self.SetWndIcon('ui_7_64_16')
        self.MakeUnstackable()
        uicls.WndCaptionLabel(text=mls.UI_PI_TRANSFER_PREPARETRANSFER, subcaption=mls.UI_PI_TRANSFER_EMERGENCYTRANSFERFORM, parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.sr.main = uiutil.GetChild(self, 'main')
        self.ConstructLayout()
        self.SetSourcePinGaugeInfo()
        self.scope = 'station_inflight'
        self.ResetPinContents()
        self.SetDestination(colony.GetPin(self.path[-1]))
        self.OnResizeUpdate()
        self.updateTimer = base.AutoTimer(100, self.SetNextTransferText)



    def ConstructLayout(self):
        pad = const.defaultPadding
        self.sr.footer = uicls.Container(name='footer', parent=self.sr.main, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 25), padding=(pad,
         pad,
         pad,
         pad))
        self.sr.cols = uicls.Container(name='col1', parent=self.sr.main, align=uiconst.TOALL)
        uicls.Line(parent=self.sr.cols, align=uiconst.TOTOP)
        uicls.Line(parent=self.sr.cols, align=uiconst.TOBOTTOM)
        self.sr.col1 = uicls.Container(name='col1', parent=self.sr.cols, align=uiconst.TOLEFT, padding=(pad,
         pad,
         pad,
         pad), clipChildren=True)
        self.sr.col2 = uicls.Container(name='col1', parent=self.sr.cols, align=uiconst.TOLEFT, padding=(pad,
         pad,
         pad,
         pad), clipChildren=True)
        uicls.Line(parent=self.sr.cols, align=uiconst.TOLEFT)
        self.sr.col3 = uicls.Container(name='col1', parent=self.sr.cols, align=uiconst.TOLEFT, padding=(pad,
         pad,
         pad,
         pad), clipChildren=True)
        colTopHeight = 60
        self.sr.sourcePinHeader = uicls.Container(name='pinHeader', parent=self.sr.col1, align=uiconst.TOTOP, padding=(pad,
         0,
         pad,
         pad), pos=(0,
         0,
         0,
         colTopHeight))
        self.sr.sourcePinList = uicls.Container(name='pinList', parent=self.sr.col1, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.sr.transferHeader = uicls.Container(name='transferHeader', parent=self.sr.col2, align=uiconst.TOTOP, padding=(pad,
         0,
         pad,
         pad), pos=(0,
         0,
         0,
         colTopHeight))
        self.sr.transferList = uicls.Container(name='transferList', parent=self.sr.col2, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.sr.destPinHeader = uicls.Container(name='destPinHeader', parent=self.sr.col3, align=uiconst.TOTOP, padding=(pad,
         0,
         pad,
         pad), pos=(0,
         0,
         0,
         colTopHeight))
        self.sr.destPinList = uicls.Container(name='destPinList', parent=self.sr.col3, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.sr.footerLeft = uicls.Container(name='footerLeft', parent=self.sr.footer, align=uiconst.TOLEFT)
        self.sr.footerRight = uicls.Container(name='footerRight', parent=self.sr.footer, align=uiconst.TORIGHT)
        btns = [(mls.UI_PI_TRANSFER_CMDEXECUTETRANSFER,
          self.GoForTransfer,
          (),
          None)]
        uicls.ButtonGroup(btns=btns, parent=self.sr.footerRight, line=0)
        self.sr.volumeText = uicls.Label(text='', parent=self.sr.transferHeader, fontsize=10, letterspace=1, left=0, top=20, state=uiconst.UI_NORMAL)
        self.sr.timeText = uicls.Label(text='', parent=self.sr.transferHeader, fontsize=10, letterspace=1, left=0, top=35, state=uiconst.UI_NORMAL)
        self.sr.timeText.hint = mls.UI_PI_TRANSFER_PROCESSINGTIMEHINT
        self.sr.cooldownTimeText = uicls.Label(text='Cooldown time: 5 minutes', parent=self.sr.transferHeader, fontsize=10, letterspace=1, left=0, top=46)
        self.sr.cooldownTimeText.hint = mls.UI_PI_COOLDOWNTIMEHINT
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

        self.OnResizeUpdate()
        self.sr.sourcePinHeaderText = uicls.Label(text=planetCommon.GetGenericPinName(self.sourcePin.typeID, self.sourcePin.id), parent=self.sr.sourcePinHeader, align=uiconst.TOPLEFT, fontsize=16, left=0, state=uiconst.UI_NORMAL)
        self.sr.sourcePinSubGauge = uicls.Gauge(parent=self.sr.sourcePinHeader, value=0.0, color=planetCommon.PLANET_COLOR_STORAGE, label='%s:' % mls.UI_GENERIC_CAPACITY, left=0, top=24, state=uiconst.UI_NORMAL)
        self.sr.sourcePinListScroll = uicls.Scroll(parent=self.sr.sourcePinList, name='pinList')
        content = self.sr.sourcePinListScroll.sr.content
        content.OnDropData = self.OnSourceScrollDropData
        self.sr.transferHeaderText = uicls.Label(text=mls.UI_PI_TRANSFER_TRANSFERCONTENTS, parent=self.sr.transferHeader, align=uiconst.TOPLEFT, fontsize=16, left=0, state=uiconst.UI_NORMAL)
        self.sr.transferListScroll = uicls.Scroll(parent=self.sr.transferList, name='transferList')
        content = self.sr.transferListScroll.sr.content
        content.OnDropData = self.OnTransferScrollDropData
        self.sr.destPinText = uicls.Label(text='', parent=self.sr.destPinHeader, align=uiconst.TOTOP, fontsize=16, state=uiconst.UI_NORMAL, singleline=True)
        self.sr.destPinSubText = uicls.Label(text='', parent=self.sr.destPinHeader, align=uiconst.TOTOP, fontsize=14, top=5, state=uiconst.UI_HIDDEN)
        self.sr.destPinSubGauge = uicls.Gauge(parent=self.sr.destPinHeader, value=0.0, color=planetCommon.PLANET_COLOR_STORAGE, label='%s:' % mls.UI_GENERIC_CAPACITY, left=0, top=24, state=uiconst.UI_HIDDEN)
        self.sr.destPinListScroll = uicls.Scroll(parent=self.sr.destPinList)



    def OnTransferScrollDropData(self, dragObj, nodes, *args):
        if nodes[0].scroll.name == 'pinList':
            self.AddCommodity(nodes)



    def OnSourceScrollDropData(self, dragObj, nodes, *args):
        if nodes[0].scroll.name == 'transferList':
            self.RemoveCommodity(nodes)



    def OnResizeUpdate(self, *args):
        if self.destroyed:
            return 
        uthread.new(self._ExpeditedTransferManagementWindow__OnResizeUpdate)



    def __OnResizeUpdate(self):
        if not self.sr.col1:
            return 
        (sl, st, sw, sh,) = self.GetAbsolute()
        desiredWidth = (sw - 25) / 3
        self.sr.col1.width = desiredWidth
        self.sr.col2.width = desiredWidth
        self.sr.col3.width = desiredWidth
        self.sr.footerLeft.width = 2 * desiredWidth + 3 * const.defaultPadding
        self.sr.footerRight.width = desiredWidth + const.defaultPadding



    def AddBtnClicked(self, *args):
        selected = self.sr.sourcePinListScroll.GetSelected()
        self.AddCommodity(selected)



    def RemoveBtnClicked(self, *args):
        selected = self.sr.transferListScroll.GetSelected()
        self.RemoveCommodity(selected)



    def AddCommodity(self, selected):
        toMove = {}
        if len(selected) == 1 and uicore.uilib.Key(uiconst.VK_SHIFT):
            typeID = selected[0].typeID
            typeName = cfg.invtypes.Get(typeID).name
            ret = uix.QtyPopup(self.pinContents[typeID], 1, 1, None, mls.UI_PI_TRANSFER_SELECTQUANTITYTOTRANSFER % {'typeName': typeName})
            if ret and 'qty' in ret:
                toMove[typeID] = min(self.pinContents[typeID], max(1, ret['qty']))
        else:
            for entry in selected:
                toMove[entry.typeID] = self.pinContents[entry.typeID]

        if self.destPin.IsConsumer():
            toMove = self._ApplyConsumerFilter(toMove)
            if not toMove:
                raise UserError('ConsumerCantAcceptCommodities')
        elif self.destPin.IsStorage():
            toMove = self._ApplyMaxAmountFilter(toMove)
        for (typeID, qty,) in toMove.iteritems():
            self.pinContents[typeID] -= qty
            if self.pinContents[typeID] <= 0:
                del self.pinContents[typeID]
            if typeID not in self.transferContents:
                self.transferContents[typeID] = 0
            self.transferContents[typeID] += qty

        self.RefreshLists()



    def _ApplyConsumerFilter(self, toMove):
        newToMove = {}
        for (typeID, qty,) in toMove.iteritems():
            remainingSpace = self.destPin.CanAccept(typeID, -1)
            alreadyInTransfer = self.transferContents.get(typeID, 0)
            if remainingSpace:
                amount = min(remainingSpace - alreadyInTransfer, qty)
                if amount > 0:
                    newToMove[typeID] = amount

        return newToMove



    def _ApplyMaxAmountFilter(self, toMove):
        availableVolume = self.destPin.GetCapacity() - self.destPin.capacityUsed
        availableVolume -= planetCommon.GetCommodityTotalVolume(self.transferContents)
        transferVolume = planetCommon.GetCommodityTotalVolume(toMove)
        if transferVolume >= availableVolume:
            newToMove = {}
            if len(toMove) == 1:
                for (typeID, quantity,) in toMove.iteritems():
                    commodityVolume = cfg.invtypes.Get(typeID).volume
                    maxAmount = int(math.floor(availableVolume / commodityVolume))
                    newToMove[typeID] = maxAmount

            eve.Message('ExpeditedTransferNotEnoughSpace')
            return newToMove
        else:
            return toMove



    def RemoveCommodity(self, selected):
        toMove = {}
        if len(selected) == 1 and uicore.uilib.Key(uiconst.VK_SHIFT):
            typeID = selected[0].typeID
            typeName = cfg.invtypes.Get(typeID).name
            ret = uix.QtyPopup(self.transferContents[typeID], 1, 1, None, mls.UI_PI_TRANSFER_SELECTQUANTITYTOREMOVE % {'typeName': typeName})
            if ret and 'qty' in ret:
                toMove[typeID] = min(self.transferContents[typeID], max(1, ret['qty']))
        else:
            for entry in selected:
                toMove[entry.typeID] = self.transferContents[entry.typeID]

        for (typeID, qty,) in toMove.iteritems():
            self.transferContents[typeID] -= qty
            if self.transferContents[typeID] <= 0:
                del self.transferContents[typeID]
            if typeID not in self.pinContents:
                self.pinContents[typeID] = 0
            self.pinContents[typeID] += qty

        self.RefreshLists()



    def GoForTransfer(self, *args):
        if len(self.transferContents) < 1:
            raise UserError('PleaseSelectCommoditiesToTransfer')
        for (typeID, quantity,) in self.transferContents.iteritems():
            if typeID not in self.sourcePin.contents:
                raise UserError('RouteFailedValidationExpeditedSourceLacksCommodity', {'typeName': cfg.invtypes.Get(typeID).name})
            if quantity > self.sourcePin.contents[typeID]:
                raise UserError('RouteFailedValidationExpeditedSourceLacksCommodityQty', {'typeName': cfg.invtypes.Get(typeID).name,
                 'qty': quantity})

        if not self.sourcePin.CanTransfer(self.transferContents):
            raise UserError('RouteFailedValidationExpeditedSourceNotReady')
        if len(self.transferContents) > 0:
            self.ShowLoad()
            try:
                self.planet.TransferCommodities(self.path, self.transferContents)

            finally:
                self.ResetPinContents()
                self.HideLoad()

            self.CloseX()



    def ResetPinContents(self, *args):
        self.pinContents = self.sourcePin.contents.copy()
        self.transferContents = {}
        self.RefreshLists()



    def RefreshLists(self, *args):
        pinListItems = []
        for (typeID, qty,) in self.pinContents.iteritems():
            lbl = '<t>%s<t>%d' % (cfg.invtypes.Get(typeID).name, qty)
            data = util.KeyVal(itemID=None, typeID=typeID, label=lbl, getIcon=1, quantity=qty, OnDropData=self.OnSourceScrollDropData)
            pinListItems.append(listentry.Get('DraggableItem', data=data))

        transferListItems = []
        for (typeID, qty,) in self.transferContents.iteritems():
            lbl = '<t>%s<t>%d' % (cfg.invtypes.Get(typeID).name, qty)
            data = util.KeyVal(itemID=None, typeID=typeID, label=lbl, getIcon=1, quantity=qty, OnDropData=self.OnTransferScrollDropData)
            transferListItems.append(listentry.Get('DraggableItem', data=data))

        self.sr.sourcePinListScroll.Load(contentList=pinListItems, headers=[mls.UI_GENERIC_TYPE, mls.UI_GENERIC_NAME, mls.UI_GENERIC_QTY], noContentHint=mls.UI_PI_STOREHOUSEEMPTY)
        self.sr.transferListScroll.Load(contentList=transferListItems, headers=[mls.UI_GENERIC_TYPE, mls.UI_GENERIC_NAME, mls.UI_GENERIC_QTY], noContentHint=mls.UI_GENERIC_NOITEMSFOUND)
        transferVolume = planetCommon.GetCommodityTotalVolume(self.transferContents)
        self.sr.volumeText.text = '%s: %s m3' % (mls.UI_GENERIC_VOLUME, util.FmtAmt(transferVolume, showFraction=1))
        self.SetNextTransferText()
        self.SetCooldownTimeText()



    def SetNextTransferText(self):
        if self.sourcePin.lastRunTime is None or self.sourcePin.lastRunTime <= blue.os.GetTime():
            nextTransfer = mls.UI_GENERIC_NOW
        else:
            nextTransfer = util.FmtTime(self.sourcePin.lastRunTime - blue.os.GetTime())
        self.sr.timeText.text = '%s %s' % (mls.UI_PI_TRANSFER_NEXTTRANSFER, nextTransfer)



    def SetCooldownTimeText(self):
        time = planetCommon.GetExpeditedTransferTime(self.availableBandwidth, self.transferContents)
        self.sr.cooldownTimeText.text = '%s: %s' % (mls.UI_PI_COOLDOWNTIME, util.FmtTime(time))



    def SetSourcePinGaugeInfo(self):
        self.sr.sourcePinSubGauge.state = uiconst.UI_DISABLED
        self.sr.sourcePinSubGauge.SetText(mls.UI_GENERIC_CAPACITY)
        self.sr.sourcePinSubGauge.SetSubText('%.1f / %.1f (%3.2f%%)' % (self.sourcePin.capacityUsed, self.sourcePin.GetCapacity(), self.sourcePin.capacityUsed / self.sourcePin.GetCapacity() * 100.0))
        self.sr.sourcePinSubGauge.SetValue(self.sourcePin.capacityUsed / self.sourcePin.GetCapacity())



    def RefreshDestinationPinInfo(self):
        self.sr.destPinSubText.state = uiconst.UI_HIDDEN
        self.sr.destPinSubGauge.state = uiconst.UI_HIDDEN
        if not self.destPin:
            self.sr.destPinText.text = mls.UI_PI_TRANSFER_NOORIGINSELECTED
            self.sr.destPinSubText.text = ''
            self.sr.destPinSubText.state = uiconst.UI_DISABLED
            self.sr.destPinListScroll.Load(contentList=[], noContentHint=mls.UI_PI_TRANSFER_NOORIGINSELECTED)
            return 
        self.sr.destPinText.text = '%s: %s' % (mls.UI_GENERIC_DESTINATION, planetCommon.GetGenericPinName(self.destPin.typeID, self.destPin.id))
        scrollHeaders = []
        scrollContents = []
        scrollNoContentText = ''
        if self.destPin.IsConsumer():
            self.sr.destPinSubText.state = uiconst.UI_DISABLED
            if self.destPin.schematicID is None:
                self.sr.destPinSubText.text = mls.UI_PI_NOSCHEMATICINSTALLEDSHORT
                scrollNoContentText = mls.UI_PI_NOSCHEMATICINSTALLEDSHORT
            else:
                self.sr.destPinSubText.text = '%s: %s' % (mls.UI_PI_SCHEMATIC, cfg.schematics.Get(self.destPin.schematicID).schematicName)
                scrollHeaders = []
                demands = self.destPin.GetConsumables()
                for (typeID, qty,) in demands.iteritems():
                    remainingSpace = self.destPin.CanAccept(typeID, -1)
                    scrollContents.append(listentry.Get('StatusBar', {'label': cfg.invtypes.Get(typeID).name,
                     'status': qty - remainingSpace,
                     'total': qty}))

        elif self.destPin.IsStorage():
            self.sr.destPinSubGauge.state = uiconst.UI_DISABLED
            self.sr.destPinSubGauge.SetText(mls.UI_GENERIC_CAPACITY)
            self.sr.destPinSubGauge.SetSubText('%.1f / %.1f (%3.2f%%)' % (self.destPin.capacityUsed, self.destPin.GetCapacity(), self.destPin.capacityUsed / self.destPin.GetCapacity() * 100.0))
            self.sr.destPinSubGauge.SetValue(self.destPin.capacityUsed / self.destPin.GetCapacity())
            scrollHeaders = [mls.UI_GENERIC_TYPE, mls.UI_GENERIC_NAME, mls.UI_GENERIC_QTY]
            contents = self.destPin.GetContents()
            for (typeID, qty,) in contents.iteritems():
                lbl = '<t>%s<t>%d' % (cfg.invtypes.Get(typeID).name, qty)
                scrollContents.append(listentry.Get('DraggableItem', {'itemID': None,
                 'typeID': typeID,
                 'label': lbl,
                 'getIcon': 1,
                 'quantity': qty}))

            scrollNoContentText = mls.UI_PI_STOREHOUSEEMPTY
        self.sr.destPinListScroll.Load(contentList=scrollContents, headers=scrollHeaders, noContentHint=scrollNoContentText)



    def SetDestination(self, destinationPin):
        self.destPin = destinationPin
        self.RefreshDestinationPinInfo()




