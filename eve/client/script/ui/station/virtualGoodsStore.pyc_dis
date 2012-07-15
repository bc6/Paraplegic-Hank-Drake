#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/station/virtualGoodsStore.py
import listentry
import uthread
import uicls
import uiconst
import trinity
import form
import util
import uiutil
import blue
import localization

class VirtualGoodsStore(uicls.Window):
    __guid__ = 'form.VirtualGoodsStore'
    __notifyevents__ = ['OnAccountChange_Local', 'OnUIColorsChanged']
    default_height = 360
    default_width = 930
    default_windowID = 'VirtualGoodsStore'
    default_iconNum = 'ui_65_128_3'

    def ApplyAttributes(self, attributes):
        self.openTime = blue.os.GetWallclockTime()
        uicls.Window.ApplyAttributes(self, attributes)
        self.storeSvc = sm.GetService('store')
        self.scope = 'station'
        self.SetMinSize([700, 360])
        self.SetCaption(localization.GetByLabel('UI/VirtualGoodsStore/StoreNameCaption'))
        self.SetTopparentHeight(0)
        self.lastWidth = self.width
        self.stationID = session.stationid2
        cornerSize = 7
        imageHeight = 160
        imageWidth = 215
        color, bgColor, comp, compsub = sm.GetService('window').GetWindowColors()
        defaultTopButtonContWidth = 210
        self.frames = []
        self.unresizablePadding = 320
        topCont = uicls.Container(parent=self.sr.main, name='topCont', align=uiconst.TOTOP, pos=(0,
         0,
         0,
         imageHeight + 2 * const.defaultPadding), padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        topButtonCont = uicls.Container(parent=topCont, name='topButtonCont', align=uiconst.TORIGHT, pos=(0,
         0,
         defaultTopButtonContWidth,
         0))
        bannerCont = uicls.Container(parent=topCont, name='bannerCont', align=uiconst.TOALL, clipChildren=1)
        fallbackImagePath = 'res:/UI/Texture/Store_MarketingBox_03.png'
        contWidth = imageWidth + 2 * cornerSize
        containerInfo = [['topLeftCont', 1], ['topMiddleCont', 2], ['topRightCont', 3]]
        for contName, adSlotID in containerInfo:
            cont = uicls.Container(parent=bannerCont, name=contName, align=uiconst.TOLEFT, pos=(0,
             0,
             contWidth,
             0), padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding), state=uiconst.UI_NORMAL)
            sprite = uicls.Sprite(parent=cont, pos=(cornerSize,
             cornerSize,
             imageWidth,
             imageHeight), align=uiconst.BOTTOMLEFT, idx=0)
            sprite.texturePath = sm.GetService('photo').GetStorebanner(adSlotID, prefs.languageID, sprite)
            if not sprite.texturePath:
                sprite.texturePath = sm.GetService('photo').GetStorebanner(adSlotID, 'EN', sprite)
                if not sprite.texturePath:
                    sprite.texturePath = fallbackImagePath
            fPadding = 2
            fHeight = imageHeight - cornerSize - fPadding
            frame = uicls.Frame(parent=cont, color=bgColor, align=uiconst.TOBOTTOM, pos=(0,
             0,
             0,
             fHeight - 1), spriteEffect=trinity.TR2_SFX_FILL, padding=(fPadding,
             fPadding,
             fPadding,
             fPadding))
            self.frames.append(frame)
            setattr(self, contName, cont)

        btnPadding = 6
        redeemPlexBtn = uicls.Button(parent=topButtonCont, name='redeemPlexBtn', label=localization.GetByLabel('UI/VirtualGoodsStore/RedeemPLEX'), func=self.RedeemPlex, pos=(0,
         const.defaultPadding + cornerSize,
         0,
         0), align=uiconst.BOTTOMRIGHT)
        top = redeemPlexBtn.top + redeemPlexBtn.height + btnPadding
        buyPlexOnlineBtn = uicls.Button(parent=topButtonCont, name='buyPlexOnline', label=localization.GetByLabel('UI/VirtualGoodsStore/BuyPlexOnline'), func=self.BuyPlexOnline, pos=(0,
         top,
         0,
         0), align=uiconst.BOTTOMRIGHT)
        top = buyPlexOnlineBtn.top + buyPlexOnlineBtn.height + btnPadding
        buyPlexMarketBtn = uicls.Button(parent=topButtonCont, name='buyPlexMarket', label=localization.GetByLabel('UI/VirtualGoodsStore/BuyPLEXOnMarket'), func=self.BuyPlexFromMarket, pos=(0,
         top,
         0,
         0), align=uiconst.BOTTOMRIGHT)
        top = buyPlexMarketBtn.top + buyPlexMarketBtn.height + btnPadding
        sellPlexBtn = uicls.Button(parent=topButtonCont, name='sellPlexBtn', label=localization.GetByLabel('UI/VirtualGoodsStore/Buttons/ExchangePLEXForAUR'), func=self.SellPlex, pos=(0,
         top,
         0,
         50), align=uiconst.BOTTOMRIGHT)
        top = sellPlexBtn.top + sellPlexBtn.height + btnPadding
        self.aurWealthLabel = uicls.EveLabelLarge(text='<right>%s' % util.FmtAUR(0), parent=topButtonCont, name='aurWealth', align=uiconst.BOTTOMRIGHT, state=uiconst.UI_DISABLED, left=16, top=top, width=300)
        self.aurWealthLabel.amount = 0
        b = uicls.EveHeaderSmall(text=localization.GetByLabel('UI/VirtualGoodsStore/Balance'), parent=topButtonCont, align=uiconst.BOTTOMRIGHT, left=16, top=self.aurWealthLabel.top + self.aurWealthLabel.height, state=uiconst.UI_DISABLED)
        maxWidth = max(160, redeemPlexBtn.width, sellPlexBtn.width, buyPlexMarketBtn.width, buyPlexOnlineBtn.width)
        left = int((defaultTopButtonContWidth - maxWidth) / 2.0)
        redeemPlexBtn.width = sellPlexBtn.width = buyPlexMarketBtn.width = buyPlexOnlineBtn.width = maxWidth
        redeemPlexBtn.left = sellPlexBtn.left = buyPlexMarketBtn.left = left
        buyPlexOnlineBtn.left = b.left = self.aurWealthLabel.left = left
        scrollParent = uicls.Container(parent=self.sr.main, name='scrollParent', align=uiconst.TOALL)
        self.scroll = uicls.Scroll(parent=scrollParent, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding + 2))
        uthread.new(self.DisplayAurWealth)
        self.scroll.sr.id = 'vsgScroll'
        self.scroll.sr.fixedColumns = {' ': 72,
         localization.GetByLabel('UI/VirtualGoodsStore/Gender'): 100,
         localization.GetByLabel('UI/VirtualGoodsStore/Price'): 100}
        self.scroll.sr.defaultColumnWidth = {localization.GetByLabel('UI/VirtualGoodsStore/ItemName'): 350}
        self.scroll.sr.minColumnWidth = {localization.GetByLabel('UI/VirtualGoodsStore/ItemName'): 100}
        self.scroll.sr.notSortableColumns = [' ']
        self.scroll.ScalingCol = self.StoreScalingCol
        self.scroll.showColumnLines = False
        self.PopulateOfferScroll()

    def DisplayAurWealth(self):
        amount = sm.GetService('wallet').GetAurWealth()
        startamount = self.aurWealthLabel.amount
        color = '<color=0xff05adae>'
        self.aurWealthLabel.amount = amount
        sm.GetService('wallet').SetBalance(self.aurWealthLabel, amount, startamount, color, const.creditsAURUM, cLeft=0, showFractions=0)

    def PopulateOfferScroll(self):
        offers = self.storeSvc.GetPreparedOffers(reloadOffers=1)
        scrolllist = []
        for offerID, offerKV in offers.iteritems():
            invType = cfg.invtypes.Get(offerKV.typeID)
            if offerKV.numberOffered > 1:
                itemName = localization.GetByLabel('UI/VirtualGoodsStore/ItemNameAndQuantity', itemName=invType.typeName, quantity=offerKV.numberOffered)
            else:
                itemName = invType.typeName
            if invType.categoryID == const.categoryBlueprint:
                itemName += '<br>'
                opts = {'materialLevel': offerKV.bpME,
                 'productivityLevel': offerKV.bpPE,
                 'runs': offerKV.bpRuns}
                if offerKV.bpRuns > 0:
                    itemName += localization.GetByLabel('UI/VirtualGoodsStore/BlueprintCopy', **opts)
                else:
                    itemName += localization.GetByLabel('UI/VirtualGoodsStore/OriginalBlueprint', **opts)
            if offerKV.genderRestrictions == const.FEMALE:
                genderText = localization.GetByLabel('UI/Common/Gender/Female')
            elif offerKV.genderRestrictions == const.MALE:
                genderText = localization.GetByLabel('UI/Common/Gender/Male')
            else:
                genderText = localization.GetByLabel('UI/VirtualGoodsStore/Unisex')
            url = '<url=showinfo:%d>' % offerKV.typeID
            data = uiutil.Bunch()
            data.itemLabel = '%s%s</url>' % (url, itemName)
            data.genderLabel = genderText
            data.priceLabel = localization.GetByLabel('UI/VirtualGoodsStore/PriceLabel', price=util.FmtAUR(offerKV.price))
            data.offerID = offerID
            data.offerKV = offerKV
            data.label = 'bla'
            data.Set('sort_ ', offerID)
            data.Set('sort_%s' % localization.GetByLabel('UI/VirtualGoodsStore/ItemName'), itemName)
            data.Set('sort_%s' % localization.GetByLabel('UI/VirtualGoodsStore/Gender'), genderText)
            data.Set('sort_%s' % localization.GetByLabel('UI/VirtualGoodsStore/Price'), offerKV.price)
            entry = listentry.Get('VStoreEntry', data=data)
            scrolllist.append(entry)

        self.scroll.Load(contentList=scrolllist, headers=[' ',
         localization.GetByLabel('UI/VirtualGoodsStore/ItemName'),
         localization.GetByLabel('UI/VirtualGoodsStore/Gender'),
         localization.GetByLabel('UI/VirtualGoodsStore/Price')])

    def SellPlex(self, *args):
        form.ConvertPlexWindow.Open()

    def RedeemPlex(self, *args):
        sm.GetService('redeem').OpenRedeemWindow(session.charid, session.stationid2)

    def BuyPlexFromMarket(self, *args):
        sm.StartService('marketutils').ShowMarketDetails(typeID=const.typePilotLicence, orderID=None)

    def BuyPlexOnline(self, *args):
        plexUrl = sm.GetService('charactersheet').GetPlexUrl()
        uicore.cmd.OpenBrowser(plexUrl)

    def OnFirstAdClicked(self, *args):
        pass

    def OnSecondAdClicked(self, *args):
        pass

    def OnThirdAdClicked(self, *args):
        pass

    def StoreScalingCol(self, sender, *args):
        if sender is None:
            return
        l, t, w, h = self.scroll.GetAbsolute()
        minColumnWidth = self.scroll.sr.minColumnWidth.get(sender.sr.column, 24)
        if self.scroll.scalingcol and self.scroll.sr.scaleLine:
            self.scroll.sr.scaleLine.left = max(minColumnWidth, min(w - self.unresizablePadding, uicore.uilib.x - l - 2))

    def OnEndScale_(self, *args):
        scaler = getattr(self.scroll.sr.scrollHeaders.children[2], 'bar', None)
        if scaler is None:
            return
        minColumnWidth = 100
        l, t, w, h = self.scroll.GetAbsolute()
        lastWidth = self.lastWidth
        self.lastWidth = w
        if w < lastWidth and w - self.unresizablePadding - 72 < scaler.columnWidth:
            newWidth = w - self.unresizablePadding - 72
            currentSettings = settings.user.ui.Get('columnWidths_%s' % uiconst.SCROLLVERSION, {})
            storeScrollSettings = currentSettings.get(self.scroll.sr.id, {})
            storeScrollSettings[scaler.sr.column] = max(minColumnWidth, newWidth)
            currentSettings[self.scroll.sr.id] = storeScrollSettings
            settings.user.ui.Set('columnWidths_%s' % uiconst.SCROLLVERSION, currentSettings)
            uthread.new(self.scroll.UpdateTabStops, 'OnEndScale_')

    def _OnResize(self, *args):
        uicls.Window._OnResize(self)
        width = self.width or self.absoluteRight - self.absoluteLeft
        if width < 925:
            self.topRightCont.display = False
        else:
            self.topRightCont.display = True

    def OnAccountChange_Local(self, accountKey, ownerID, balance):
        if balance is None or accountKey != 'AURUM' or ownerID != eve.session.charid:
            return
        uthread.new(self.DisplayAurWealth)

    def OnUIColorsChanged(self):
        color, bgColor, comp, compsub = sm.GetService('window').GetWindowColors()
        for frame in self.frames:
            frame.SetRGB(*bgColor)

    def _OnClose(self, *args):
        closeTime = blue.os.GetWallclockTime()
        openFor = int(round(float(closeTime - self.openTime) / SEC))
        sm.GetService('infoGatheringSvc').LogInfoEvent(eventTypeID=const.infoEventNexCloseNex, itemID=session.charid, itemID2=self.stationID, int_1=openFor)


class VStoreEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.VStoreEntry'
    labelMargin = 5

    def ApplyAttributes(self, attributes):
        uicls.SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.sr.line = uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.hilite = uicls.Fill(parent=None, align=uiconst.TOALL, color=(1.0, 1.0, 1.0, 0.125), state=uiconst.UI_HIDDEN)
        self.sr.selection = uicls.Fill(parent=None, align=uiconst.TOALL, color=(1.0, 1.0, 1.0, 0.125), state=uiconst.UI_HIDDEN)
        self.background.append(self.hilite)
        self.background.append(self.sr.selection)
        self.typeIconCont = uicls.Container(name='typeIconCont', parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=False, width=68)
        self.typeIcon = uicls.Icon(parent=self.typeIconCont, pos=(0, 0, 64, 64), ignoreSize=True, align=uiconst.CENTER, state=uiconst.UI_NORMAL)
        self.itemNameCont = uicls.Container(name='itemNameCont', parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=False)
        self.itemNameCont.label = uicls.EveLabelMedium(parent=self.itemNameCont, name='itemNameLabel', left=self.labelMargin, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
        self.itemNameCont.label.OnMouseEnter = self.OnItemNameEnter
        self.itemNameCont.label.OnClick = (self.OnItemNameClick, self.itemNameCont.label)
        self.itemNameCont.label.GetMenu = self.ItemNameGetMenu
        self.genderCont = uicls.Container(name='genderCont', parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=False)
        self.genderCont.label = uicls.EveLabelMedium(parent=self.genderCont, name='genderLabel', left=self.labelMargin, align=uiconst.CENTERLEFT)
        self.priceCont = uicls.Container(name='priceCont', parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=False)
        self.priceCont.label = uicls.EveLabelMedium(parent=self.priceCont, name='priceLabel', left=self.labelMargin + 5, align=uiconst.CENTERRIGHT)
        self.buyCont = uicls.Container(name='buyCont', parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOALL, clipChildren=True)
        buyBtn = uicls.Button(parent=self.buyCont, name='buyBtn', label=localization.GetByLabel('UI/VirtualGoodsStore/Buttons/Buy'), func=self.BuyItem, pos=(34, 0, 0, 0), align=uiconst.CENTERRIGHT, idx=0, top=1)
        self.columnContainers = [self.typeIconCont,
         self.itemNameCont,
         self.genderCont,
         self.priceCont,
         self.buyCont]

    def Load(self, node):
        self.itemNameCont.label.text = node.itemLabel
        self.genderCont.label.text = node.genderLabel
        self.priceCont.label.text = node.priceLabel
        self.offerID = node.offerID
        self.offerKV = node.offerKV
        self.typeID = self.offerKV.typeID
        self.typeIcon.LoadIconByTypeID(typeID=self.typeID)
        if util.IsPreviewable(self.typeID):
            self.typeIcon.OnClick = (sm.GetService('preview').PreviewType, self.typeID)
            self.typeIcon.cursor = uiconst.UICURSOR_MAGNIFIER

    def OnColumnResize(self, newCols):
        for container, width in zip(self.columnContainers, newCols):
            container.width = width
            label = getattr(container, 'label', None)
            if label:
                label.width = width - 14

    def OnMouseEnter(self, *args):
        if getattr(self, 'hilite', None) is None:
            self.hilite = uicls.Fill(parent=self, align=uiconst.TOPLEFT, top=1, height=self.height - 3, width=5000, color=(1.0, 1.0, 1.0, 0.125))
        self.hilite.state = uiconst.UI_DISABLED

    def OnMouseExit(self, *args):
        if getattr(self, 'hilite', None):
            self.hilite.state = uiconst.UI_HIDDEN

    def BuyItem(self, *args):
        sm.GetService('store').GetBuyWnd(self.offerID)

    def OnDblClick(self, *args):
        self.BuyItem()

    def GetHeight(self, *args):
        node, width = args
        node.height = 72
        return node.height

    def OnClick(self, *args):
        if self.sr.Get('selection', None) is None:
            self.sr.selection = uicls.Fill(parent=self, align=uiconst.TOPLEFT, top=1, height=self.height - 3, width=5000, color=(1.0, 1.0, 1.0, 0.125))
        self.sr.selection.state = uiconst.UI_DISABLED
        self.sr.node.scroll.SelectNode(self.sr.node)

    def GetMenu(self, *args):
        m = [(uiutil.MenuLabel('UI/VirtualGoodsStore/BuyItem'), self.BuyItem)]
        m += sm.GetService('menu').GetMenuFormItemIDTypeID(itemID=None, typeID=self.typeID, ignoreMarketDetails=0)
        if util.IsPreviewable(self.typeID):
            m += [(uiutil.MenuLabel('UI/VirtualGoodsStore/PreviewItem'), sm.GetService('preview').PreviewType, (self.typeID,))]
        m += sm.GetService('menu').GetGMTypeMenu(self.typeID, divs=True)
        return m

    def OnItemNameEnter(self, *args):
        self.OnMouseEnter()

    def OnItemNameClick(self, label, *args):
        if label.GetMouseOverUrl() is None:
            self.OnClick()
        else:
            uicls.Label.OnClick(label)

    def ItemNameGetMenu(self, *args):
        return self.GetMenu()


class VGoodsBuyWindow(uicls.Window):
    __guid__ = 'form.VGoodsBuyWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        padding = 2 * const.defaultPadding
        self.contHeights = 30
        inputLeft = 130
        self.btns = None
        self.scope = 'station'
        self.SetWndIcon()
        self.SetTopparentHeight(64 + 2 * padding)
        self.SetMinSize([400, 220], 1)
        self.NoSeeThrough()
        self.MakeUnResizeable()
        self.MakeUncollapseable()
        self.topImage = uicls.Icon(parent=self.sr.topParent, pos=(padding,
         padding,
         64,
         64), texturePath='res:/UI/Texture/Icons/102_128_2.png', align=uiconst.TOPLEFT, idx=0)
        self.captionLabel = uicls.EveCaptionMedium(parent=self.sr.topParent, name='itemName', align=uiconst.CENTERLEFT, text='', pos=(64 + 2 * padding,
         0,
         320,
         0))
        firstCont = uicls.Container(parent=self.sr.main, name='firstCont', align=uiconst.TOTOP, pos=(0,
         0,
         0,
         self.contHeights))
        self.firstLabel = uicls.EveLabelSmall(text='', parent=firstCont, name='firstLabel', align=uiconst.CENTERLEFT, left=padding, top=0)
        self.firstValue = uicls.EveLabelSmall(text='', parent=firstCont, name='firstValue', align=uiconst.CENTERLEFT, left=inputLeft, top=0)
        qtyCont = uicls.Container(parent=self.sr.main, name='secondCont', align=uiconst.TOTOP, pos=(0,
         0,
         0,
         self.contHeights))
        self.qtyLabel = uicls.EveLabelSmall(text=localization.GetByLabel('UI/Common/Quantity'), parent=qtyCont, name='secondLabel', align=uiconst.CENTERLEFT, left=padding, top=0)
        self.qtyEdit = uicls.SinglelineEdit(name='qtyEdit', parent=qtyCont, setvalue=0, maxLength=32, pos=(inputLeft,
         0,
         60,
         0), label='', align=uiconst.CENTERLEFT, ints=[0, 1000000])
        self.qtyEdit.OnChange = self.OnChanged_quantity
        self.qtyAvailLabel = uicls.EveLabelSmall(text='', parent=qtyCont, name='qtyAvailLabel', align=uiconst.CENTERLEFT, left=self.qtyEdit.left + self.qtyEdit.width + padding, top=0)
        totalCont = uicls.Container(parent=self.sr.main, name='totalCont', align=uiconst.TOTOP, pos=(0,
         0,
         0,
         self.contHeights))
        width = self.width - inputLeft - 20
        self.totalLabel = uicls.EveLabelSmall(text='', parent=totalCont, name='totalLabel', align=uiconst.CENTERLEFT, left=padding, top=0)
        self.totalValueLabel = uicls.CaptionLabel(text='', parent=totalCont, align=uiconst.CENTERLEFT, left=inputLeft, uppercase=False, letterspace=0, width=width)

    def CheckHeights(self, t = None):
        if self.destroyed:
            return
        if t:
            t.parent.height = t._numLines * self.contHeights
        if self.btns is not None:
            btnHeight = self.btns.height
        else:
            btnHeight = 0
        theight = sum([ each.height for each in self.sr.main.children if each.align == uiconst.TOTOP ])
        h = theight + self.sr.topParent.height + btnHeight + 26
        self.SetMinSize([self.width, h], 1)

    def Cancel(self, *args):
        self.CloseByUser()

    def OnChanged_quantity(self, value, *args):
        if value.startswith('-'):
            return self.qtyEdit.SetValue(0)
        v = value or 0
        qty = max(0, int(v))
        if qty > self.qtyEdit.integermode[1]:
            qty = self.qtyEdit.integermode[1]
            self.qtyEdit.SetValue(qty)
        total = qty * self.rate
        totalText = self.GetTotalText(total)
        self.totalValueLabel.text = totalText
        self.CheckHeights(self.totalValueLabel)

    def GetTotalText(self, quantity):
        pass


class BuyVGoodsWindow(VGoodsBuyWindow):
    __guid__ = 'form.BuyVGoodsWindow'
    default_windowID = 'buyVGoodsWindow'

    def ApplyAttributes(self, attributes):
        VGoodsBuyWindow.ApplyAttributes(self, attributes)
        self.totalColor = '0xfff1f202'
        self.LoadWnd(attributes.offerKV)
        self.btns = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/VirtualGoodsStore/Buttons/Buy'),
          self.Buy,
          (),
          None], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.Cancel,
          (),
          None]], parent=self.sr.main, idx=0)
        self.CheckHeights()

    def LoadWnd(self, offerKV):
        self.offerKV = offerKV
        self.offerID = offerKV.offerID
        self.pricePerItem = self.rate = self.offerKV.price
        self.typeID = self.offerKV.typeID
        self.topImage.LoadIconByTypeID(typeID=self.typeID)
        if util.IsPreviewable(self.typeID):
            self.topImage.OnClick = (sm.GetService('preview').PreviewType, self.typeID)
            self.topImage.cursor = uiconst.UICURSOR_MAGNIFIER
        typeName = cfg.invtypes.Get(self.typeID).typeName
        self.SetCaption(localization.GetByLabel('UI/VirtualGoodsStore/BuyItemCaption', buyItem=typeName))
        if self.offerKV.numberOffered > 1:
            text = '%sx %s' % (self.offerKV.numberOffered, typeName)
        else:
            text = typeName
        self.captionLabel.text = text
        self.firstLabel.text = localization.GetByLabel('UI/VirtualGoodsStore/Price')
        priceText = util.FmtAUR(self.pricePerItem)
        self.firstValue.text = priceText
        initialQty = 1
        self.qtyEdit.SetValue(initialQty)
        self.qtyAvailLabel.text = ''
        self.totalLabel.text = localization.GetByLabel('UI/Common/Total')
        initialTotalValue = initialQty * self.pricePerItem
        self.totalValueLabel.text = self.GetTotalText(initialTotalValue)

    def Buy(self, *args):
        qty = self.qtyEdit.GetValue()
        qty = max(0, qty)
        if qty <= 0:
            return
        sm.GetService('store').AcceptOffer(self.offerKV.offerID, qty)
        self.CloseByUser()

    def GetTotalText(self, quantity):
        return localization.GetByLabel('UI/VirtualGoodsStore/TotalAmount', totalAmount=quantity)


class ConvertPlexWindow(VGoodsBuyWindow):
    __guid__ = 'form.ConvertPlexWindow'
    default_windowID = 'convertPlexWindow'

    def ApplyAttributes(self, attributes):
        VGoodsBuyWindow.ApplyAttributes(self, attributes)
        self.totalColor = '0xff05adae'
        windowText = localization.GetByLabel('UI/VirtualGoodsStore/ExchangePlexCaption')
        self.exchangeRate = self.rate = sm.GetService('store').GetPlexToAURExchangeRate()
        self.localPlexes = sm.GetService('store').GetAvailableLocalPlexes()
        self.topImage.SetTexturePath('res:/UI/Texture/Icons/7_64_12.png')
        self.SetCaption(windowText)
        self.captionLabel.text = windowText
        self.firstLabel.text = localization.GetByLabel('UI/VirtualGoodsStore/ExchangeRate')
        self.firstValue.text = localization.GetByLabel('UI/VirtualGoodsStore/AURperPLEX', numAUR=self.exchangeRate)
        numLocalPlexes = sum((i.stacksize for i in self.localPlexes))
        if numLocalPlexes > 0:
            initialQty = 1
        else:
            initialQty = 0
        self.qtyEdit.SetValue(initialQty)
        self.qtyEdit.IntMode(0, numLocalPlexes)
        self.qtyAvailLabel.text = localization.GetByLabel('UI/VirtualGoodsStore/PlexAvailableInHangar', numPLEX=numLocalPlexes)
        self.totalLabel.text = localization.GetByLabel('UI/VirtualGoodsStore/Payout')
        initialTotalValue = initialQty * self.exchangeRate
        totalText = util.FmtAmt(initialTotalValue)
        self.totalText = self.GetTotalText(initialTotalValue)
        self.totalValueLabel.text = self.totalText
        self.btns = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/VirtualGoodsStore/Buttons/Exchange'),
          self.Sell,
          (),
          None], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.Cancel,
          (),
          None]], parent=self.sr.main, idx=0)
        self.CheckHeights()

    def Sell(self, *args):
        qty = self.qtyEdit.GetValue()
        qty = max(0, qty)
        if qty <= 0:
            return
        sm.GetService('store').SellLocalPlexForAur([ p.itemID for p in self.localPlexes ], qty)
        self.CloseByUser()

    def GetTotalText(self, quantity):
        return localization.GetByLabel('UI/VirtualGoodsStore/TotalAURValue', totalValue=quantity)