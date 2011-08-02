import listentry
import uthread
import uicls
import uiconst
import trinity
import form
import util
import uiutil

class VirtualGoodsStore(uicls.Window):
    __guid__ = 'form.VirtualGoodsStore'
    __notifyevents__ = ['OnAccountChange_Local', 'OnUIColorsChanged']
    default_height = 360
    default_width = 930
    default_windowID = 'VirtualGoodsStore'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.storeSvc = sm.GetService('store')
        self.scope = 'station'
        self.SetMinSize([700, 360])
        self.SetCaption(mls.UI_VGSTORE_VGSTORE)
        self.SetTopparentHeight(0)
        self.lastWidth = self.width
        cornerSize = 7
        imageHeight = 160
        imageWidth = 215
        (color, bgColor, comp, compsub,) = sm.GetService('window').GetWindowColors()
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
        for (contName, adSlotID,) in containerInfo:
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

        moneyCont = uicls.Container(parent=topButtonCont, name='moneyCont', align=uiconst.TOTOP, pos=(0, 22, 0, 50))
        b = uicls.Label(text='<right>%s' % mls.UI_GENERIC_BALANCE, parent=moneyCont, align=uiconst.TOPRIGHT, pos=(16, 6, 100, 32), state=uiconst.UI_DISABLED, fontsize=9, letterspace=2, uppercase=1, autoheight=False, autowidth=False)
        self.aurWealthLabel = uicls.Label(text='<right>%s' % util.FmtAUR(0), parent=moneyCont, name='aurWealth', align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, pos=(16, 20, 300, 32), fontsize=14, autoheight=False, autowidth=False)
        self.aurWealthLabel.amount = 0
        btnPadding = 6
        redeemPlexBtn = uicls.Button(parent=topButtonCont, name='redeemPlexBtn', label=mls.UI_VGSTORE_REDEEMPLEX, func=self.RedeemPlex, pos=(0,
         const.defaultPadding + cornerSize,
         0,
         0), align=uiconst.BOTTOMRIGHT)
        top = redeemPlexBtn.top + redeemPlexBtn.height + btnPadding
        buyPlexOnlineBtn = uicls.Button(parent=topButtonCont, name='buyPlexOnline', label=mls.UI_VGSTORE_BUYPLEXONLINE, func=self.BuyPlexOnline, pos=(0,
         top,
         0,
         0), align=uiconst.BOTTOMRIGHT)
        top = buyPlexOnlineBtn.top + buyPlexOnlineBtn.height + btnPadding
        buyPlexMarketBtn = uicls.Button(parent=topButtonCont, name='buyPlexMarket', label=mls.UI_VGSTORE_BUYPLEXMARKET, func=self.BuyPlexFromMarket, pos=(0,
         top,
         0,
         0), align=uiconst.BOTTOMRIGHT)
        top = buyPlexMarketBtn.top + buyPlexMarketBtn.height + btnPadding
        sellPlexBtn = uicls.Button(parent=topButtonCont, name='sellPlexBtn', label=mls.UI_VGSTORE_CONVERTPLEX, func=self.SellPlex, pos=(0,
         top,
         0,
         50), align=uiconst.BOTTOMRIGHT)
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
         mls.UI_GENERIC_GENDER: 100,
         mls.UI_GENERIC_PRICE: 100}
        self.scroll.sr.defaultColumnWidth = {mls.UI_VGSTORE_ITEMNAME: 350}
        self.scroll.sr.minColumnWidth = {mls.UI_VGSTORE_ITEMNAME: 100}
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
        for (offerID, offerKV,) in offers.iteritems():
            invType = cfg.invtypes.Get(offerKV.typeID)
            if offerKV.numberOffered > 1:
                itemName = mls.UI_VGSTORE_ITEMNAMEWITHQTY % {'itemName': invType.typeName,
                 'qty': offerKV.numberOffered}
            else:
                itemName = invType.typeName
            if offerKV.genderRestrictions == const.FEMALE:
                genderText = mls.UI_GENERIC_FEMALE
            elif offerKV.genderRestrictions == const.MALE:
                genderText = mls.UI_GENERIC_MALE
            else:
                genderText = mls.UI_GENERIC_UNISEX
            url = '<url=showinfo:%d>' % offerKV.typeID
            label = '%(url)s<color=-2039584>%(itemName)s</url><t>%(gender)s<t><right><fontsize=14><b>%(price)s</b>' % {'url': url,
             'itemName': itemName,
             'gender': genderText,
             'price': util.FmtAUR(offerKV.price)}
            data = uiutil.Bunch()
            data.itemLabel = '%s<color=-2039584>%s</url>' % (url, itemName)
            data.genderLabel = genderText
            data.priceLabel = '<right><fontsize=14><b>%s</b>' % util.FmtAUR(offerKV.price)
            data.offerID = offerID
            data.offerKV = offerKV
            data.label = 'bla'
            data.Set('sort_ ', offerID)
            data.Set('sort_%s' % mls.UI_VGSTORE_ITEMNAME, itemName)
            data.Set('sort_%s' % mls.UI_GENERIC_GENDER, genderText)
            data.Set('sort_%s' % mls.UI_GENERIC_PRICE, offerKV.price)
            entry = listentry.Get('VStoreEntry', data=data)
            scrolllist.append(entry)

        self.scroll.Load(contentList=scrolllist, headers=[' ',
         mls.UI_VGSTORE_ITEMNAME,
         mls.UI_GENERIC_GENDER,
         mls.UI_GENERIC_PRICE])



    def SellPlex(self, *args):
        sm.GetService('window').GetWindow('convertPlexWindow', decoClass=form.ConvertPlexWindow, create=1, maximize=1)



    def RedeemPlex(self, *args):
        sm.GetService('redeem').OpenRedeemWindow(session.charid, session.stationid)



    def BuyPlexFromMarket(self, *args):
        sm.StartService('marketutils').ShowMarketDetails(typeID=const.typePilotLicence, orderID=None)



    def BuyPlexOnline(self, *args):
        PLEX_URL = 'https://secure.eveonline.com/PLEX.aspx'
        uicore.cmd.OpenBrowser(PLEX_URL)



    def OnFirstAdClicked(self, *args):
        pass



    def OnSecondAdClicked(self, *args):
        pass



    def OnThirdAdClicked(self, *args):
        pass



    def StoreScalingCol(self, sender, *args):
        if sender is None:
            return 
        (l, t, w, h,) = self.scroll.GetAbsolute()
        minColumnWidth = self.scroll.sr.minColumnWidth.get(sender.sr.column, 24)
        if self.scroll.scalingcol and self.scroll.sr.scaleLine:
            self.scroll.sr.scaleLine.left = max(minColumnWidth, min(w - self.unresizablePadding, uicore.uilib.x - l - 2))



    def OnEndScale_(self, *args):
        scaler = getattr(self.scroll.sr.scrollHeaders.children[2], 'bar', None)
        if scaler is None:
            return 
        minColumnWidth = 100
        (l, t, w, h,) = self.scroll.GetAbsolute()
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
        (color, bgColor, comp, compsub,) = sm.GetService('window').GetWindowColors()
        for frame in self.frames:
            frame.SetRGB(*bgColor)





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
        self.itemNameCont.label = uicls.Label(parent=self.itemNameCont, name='itemNameLabel', left=self.labelMargin, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
        self.itemNameCont.label.OnMouseEnter = self.OnItemNameEnter
        self.itemNameCont.label.OnClick = (self.OnItemNameClick, self.itemNameCont.label)
        self.itemNameCont.label.GetMenu = self.ItemNameGetMenu
        self.genderCont = uicls.Container(name='genderCont', parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=False)
        self.genderCont.label = uicls.Label(parent=self.genderCont, name='genderLabel', left=self.labelMargin, align=uiconst.CENTERLEFT)
        self.priceCont = uicls.Container(name='priceCont', parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=False)
        self.priceCont.label = uicls.Label(parent=self.priceCont, name='priceLabel', left=self.labelMargin + 5, align=uiconst.CENTERRIGHT)
        self.buyCont = uicls.Container(name='buyCont', parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOALL, clipChildren=True)
        buyBtn = uicls.Button(parent=self.buyCont, name='buyBtn', label=mls.UI_CMD_BUY, func=self.BuyItem, pos=(34, 0, 0, 0), align=uiconst.CENTERRIGHT, idx=0, top=1)
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
        for (container, width,) in zip(self.columnContainers, newCols):
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
        (node, width,) = args
        node.height = 72
        return node.height



    def OnClick(self, *args):
        if self.sr.Get('selection', None) is None:
            self.sr.selection = uicls.Fill(parent=self, align=uiconst.TOPLEFT, top=1, height=self.height - 3, width=5000, color=(1.0, 1.0, 1.0, 0.125))
        self.sr.selection.state = uiconst.UI_DISABLED
        self.sr.node.scroll.SelectNode(self.sr.node)



    def GetMenu(self, *args):
        m = [(mls.UI_CMD_BUYTHIS, self.BuyItem)]
        m += sm.GetService('menu').GetMenuFormItemIDTypeID(itemID=None, typeID=self.typeID, ignoreMarketDetails=0)
        if util.IsPreviewable(self.typeID):
            m += [(mls.UI_CMD_PREVIEW, sm.GetService('preview').PreviewType, (self.typeID,))]
        m += sm.GetService('menu').GetGMTypeMenu(self.typeID, divs=True)
        return m



    def OnItemNameEnter(self, *args):
        self.OnMouseEnter()



    def OnItemNameClick(self, label, *args):
        if label._activeLink is None:
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
        self.captionLabel = uicls.CaptionLabel(parent=self.sr.topParent, name='itemName', align=uiconst.CENTERLEFT, text='', pos=(64 + 2 * padding,
         0,
         0,
         0), uppercase=False, letterspace=0)
        firstCont = uicls.Container(parent=self.sr.main, name='firstCont', align=uiconst.TOTOP, pos=(0,
         0,
         0,
         self.contHeights))
        self.firstLabel = uicls.Label(text='', parent=firstCont, name='firstLabel', align=uiconst.CENTERLEFT, left=padding, top=0, fontsize=9, letterspace=2, linespace=9)
        self.firstValue = uicls.Label(text='', parent=firstCont, name='firstValue', align=uiconst.CENTERLEFT, left=inputLeft, top=0, fontsize=9, letterspace=2, linespace=9)
        qtyCont = uicls.Container(parent=self.sr.main, name='secondCont', align=uiconst.TOTOP, pos=(0,
         0,
         0,
         self.contHeights))
        self.qtyLabel = uicls.Label(text=mls.UI_GENERIC_QUANTITY, parent=qtyCont, name='secondLabel', align=uiconst.CENTERLEFT, left=padding, top=0, fontsize=9, letterspace=2, linespace=9)
        self.qtyEdit = uicls.SinglelineEdit(name='qtyEdit', parent=qtyCont, setvalue=0, maxLength=32, pos=(inputLeft,
         0,
         60,
         0), label='', align=uiconst.CENTERLEFT, ints=[0, 1000000])
        self.qtyEdit.OnChange = self.OnChanged_quantity
        self.qtyAvailLabel = uicls.Label(text='', parent=qtyCont, name='qtyAvailLabel', align=uiconst.CENTERLEFT, left=self.qtyEdit.left + self.qtyEdit.width + padding, top=0, fontsize=9, letterspace=2, linespace=9)
        totalCont = uicls.Container(parent=self.sr.main, name='totalCont', align=uiconst.TOTOP, pos=(0,
         0,
         0,
         self.contHeights))
        width = self.width - inputLeft - 20
        self.totalLabel = uicls.Label(text='', parent=totalCont, name='totalLabel', align=uiconst.CENTERLEFT, left=padding, top=0, fontsize=9, letterspace=2, linespace=9)
        self.totalValueLabel = uicls.CaptionLabel(text='', parent=totalCont, align=uiconst.CENTERLEFT, left=inputLeft, uppercase=False, letterspace=0, width=width, autowidth=0)



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
        self.CloseX()



    def OnChanged_quantity(self, value, *args):
        if value.startswith('-'):
            return self.qtyEdit.SetValue(0)
        v = value or 0
        qty = max(0, int(v))
        if qty > self.qtyEdit.integermode[1]:
            qty = self.qtyEdit.integermode[1]
            self.qtyEdit.SetValue(qty)
        total = qty * self.rate
        totalText = '<color=%s>%s' % (self.totalColor, util.FmtAUR(total))
        self.totalValueLabel.text = totalText
        self.CheckHeights(self.totalValueLabel)




class BuyVGoodsWindow(VGoodsBuyWindow):
    __guid__ = 'form.BuyVGoodsWindow'

    def ApplyAttributes(self, attributes):
        VGoodsBuyWindow.ApplyAttributes(self, attributes)
        self.totalColor = '0xfff1f202'
        self.LoadWnd(attributes.offerKV)
        self.btns = uicls.ButtonGroup(btns=[[mls.UI_CMD_BUY,
          self.Buy,
          (),
          None], [mls.UI_CMD_CANCEL,
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
        self.SetCaption(mls.UI_VGSTORE_BUYTYPENAME % {'typeName': typeName})
        if self.offerKV.numberOffered > 1:
            text = '%sx %s' % (self.offerKV.numberOffered, typeName)
        else:
            text = typeName
        self.captionLabel.text = text
        self.firstLabel.text = mls.UI_GENERIC_PRICE
        priceText = util.FmtAUR(self.pricePerItem)
        self.firstValue.text = priceText
        initialQty = 1
        self.qtyEdit.SetValue(initialQty)
        self.qtyAvailLabel.text = ''
        self.totalLabel.text = mls.UI_GENERIC_TOTAL
        initialTotalValue = initialQty * self.pricePerItem
        totalText = util.FmtAUR(initialTotalValue)
        totalText = '<color=%s>%s' % (self.totalColor, totalText)
        self.totalValueLabel.text = text = totalText



    def Buy(self, *args):
        qty = self.qtyEdit.GetValue()
        qty = max(0, qty)
        if qty <= 0:
            return 
        sm.GetService('store').AcceptOffer(self.offerKV.offerID, qty)
        self.CloseX()




class ConvertPlexWindow(VGoodsBuyWindow):
    __guid__ = 'form.ConvertPlexWindow'

    def ApplyAttributes(self, attributes):
        VGoodsBuyWindow.ApplyAttributes(self, attributes)
        self.totalColor = '0xff05adae'
        windowText = mls.UI_VGSTORE_CONVERTPLEX
        self.exchangeRate = self.rate = sm.GetService('store').GetPlexToAURExchangeRate()
        self.localPlexes = sm.GetService('store').GetAvailableLocalPlexes()
        self.topImage.SetTexturePath('res:/UI/Texture/Icons/7_64_12.png')
        self.SetCaption(windowText)
        self.captionLabel.text = windowText
        self.firstLabel.text = mls.UI_VGSTORE_EXCHANGERATE
        self.firstValue.text = mls.UI_VGSTORE_AURFORPLEX % {'numAUR': util.FmtAmt(self.exchangeRate)}
        numLocalPlexes = sum((i.stacksize for i in self.localPlexes))
        if numLocalPlexes > 0:
            initialQty = 1
        else:
            initialQty = 0
        self.qtyEdit.SetValue(initialQty)
        self.qtyEdit.IntMode(0, numLocalPlexes)
        availableText = mls.UI_VGSTORE_NUMAVAILABLE % {'numItems': util.FmtAmt(numLocalPlexes)}
        self.qtyAvailLabel.text = availableText
        self.totalLabel.text = mls.UI_VGSTORE_PAYOUT
        initialTotalValue = initialQty * self.exchangeRate
        totalText = util.FmtAmt(initialTotalValue)
        self.totalText = '<color=%s>%s x %s' % (self.totalColor, totalText, mls.UI_GENERIC_AUR)
        self.totalValueLabel.text = self.totalText
        self.btns = uicls.ButtonGroup(btns=[[mls.UI_VGSTORE_EXCHANGE,
          self.Sell,
          (),
          None], [mls.UI_CMD_CANCEL,
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
        self.CloseX()




