import blue
import xtriui
import form
import uix
import util
import listentry
import draw
import base
import uicls
import uiconst
import log
MINSCROLLHEIGHT = 64
LEFTSIDEWIDTH = 74

class MarketOrders(uicls.Container):
    __guid__ = 'form.MarketOrders'
    __nonpersistvars__ = []
    __notifyevents__ = ['OnOwnOrderChanged']

    def _OnClose(self):
        uicls.Container._OnClose(self)
        sm.UnregisterNotify(self)
        self.lastUpdateTime = None
        self.refreshOrdersTimer = None



    def OnOwnOrderChanged(self, order, reason, isCorp):
        if self and not self.destroyed and self.state != uiconst.UI_HIDDEN:
            self.RefreshOrders()



    def RefreshOrders(self):
        if self.lastUpdateTime and self.refreshOrdersTimer is None:
            diff = blue.os.TimeDiffInMs(self.lastUpdateTime)
            if diff > 30000:
                self._RefreshOrders()
            else:
                self.refreshOrdersTimer = base.AutoTimer(int(diff), self._RefreshOrders)
        else:
            self._RefreshOrders()



    def _RefreshOrders(self):
        if self and not self.destroyed:
            if not getattr(self, 'ordersInited', 0):
                self.Setup()
            self.ShowOrders(isCorp=self.isCorp, refreshing=1)
            self.refreshOrdersTimer = None
            self.lastUpdateTime = blue.os.GetTime()



    def init(self):
        self.sr.sellParent = None
        self.lastUpdateTime = None
        self.refreshOrdersTimer = None



    def Setup(self, where = None):
        self.isCorp = None
        self.where = where
        self.limits = sm.GetService('marketQuote').GetSkillLimits()
        par = uicls.Container(name='counter', parent=self, align=uiconst.TOBOTTOM, height=60, clipChildren=1)
        self.sr.counter = uicls.Label(text='', parent=par, left=const.defaultPadding + LEFTSIDEWIDTH, top=const.defaultPadding, tabs=[175, 500], state=uiconst.UI_NORMAL)
        self.sr.counter2 = uicls.Label(text='', parent=par, left=6, top=const.defaultPadding, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        ratio = settings.user.ui.Get('orderScrollHeight', 0.5)
        self.scrollHeight = self.absoluteBottom - self.absoluteTop - self.sr.counter.height - 100
        h = int(ratio * self.scrollHeight)
        sellParent = uicls.Container(name='sellParent', parent=self, align=uiconst.TOTOP, height=h)
        sellLeft = uicls.Container(name='sellLeft', parent=sellParent, align=uiconst.TOLEFT, width=LEFTSIDEWIDTH)
        sellingText = uicls.CaptionLabel(text=mls.UI_MARKET_SELLING, parent=sellLeft, align=uiconst.RELATIVE, fontsize=16, left=4, top=4, width=LEFTSIDEWIDTH)
        scroll = uicls.Scroll(name='sellscroll', parent=sellParent)
        scroll.multiSelect = 0
        scroll.smartSort = 1
        scroll.ignoreHeaderWidths = 1
        scroll.sr.id = 'ordersSellScroll'
        scroll.OnColumnChanged = self.OnOrderSellColumnChanged
        self.sr.sellScroll = scroll
        self.sr.sellParent = sellParent
        divider = xtriui.Divider(name='divider', align=uiconst.TOTOP, height=const.defaultPadding, parent=self, state=uiconst.UI_NORMAL)
        divider.Startup(sellParent, 'height', 'y', 50, self.scrollHeight)
        divider.OnSizeChanged = self.OnOrderScrollSizeChanged
        self.sr.divider = divider
        buyParent = uicls.Container(name='buyParent', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        buyLeft = uicls.Container(name='buyLeft', parent=buyParent, align=uiconst.TOLEFT, width=LEFTSIDEWIDTH)
        buyingText = uicls.CaptionLabel(text=mls.UI_MARKET_BUYING, parent=buyLeft, align=uiconst.RELATIVE, fontsize=16, left=4, top=4, width=LEFTSIDEWIDTH)
        leftsidewidth = max(LEFTSIDEWIDTH, sellingText.width + 10, buyingText.width + 10)
        sellLeft.width = leftsidewidth
        buyLeft.width = leftsidewidth
        self.sr.counter.left = const.defaultPadding + leftsidewidth
        scroll = uicls.Scroll(name='buyscroll', parent=buyParent)
        scroll.multiSelect = 0
        scroll.smartSort = 1
        scroll.ignoreHeaderWidths = 1
        scroll.sr.id = 'ordersBuyScroll'
        scroll.OnColumnChanged = self.OnOrderBuyColumnChanged
        self.sr.buyScroll = scroll
        uicls.Button(label=mls.UI_MARKET_EXPORT, align=uiconst.BOTTOMLEFT, parent=par, func=self.ExportToFile)
        sm.RegisterNotify(self)
        (w, h,) = self.GetAbsoluteSize()
        self._OnSizeChange_NoBlock(w, h)
        self.ordersInited = 1



    def OnOrderScrollSizeChanged(self):
        h = self.sr.sellParent.height
        (absWidth, absHeight,) = self.GetAbsoluteSize()
        if h > absHeight - self.sr.counter.height - 50:
            h = absHeight - self.sr.counter.height - 50
            ratio = float(h) / absHeight
            settings.user.ui.Set('orderScrollHeight', ratio)
            self._OnSizeChange_NoBlock(absWidth, absHeight)
            return 
        ratio = float(h) / absHeight
        settings.user.ui.Set('orderScrollHeight', ratio)



    def ExportToFile(self, *args):
        if self.isCorp:
            orders = sm.GetService('marketQuote').GetCorporationOrders()
        else:
            orders = sm.GetService('marketQuote').GetMyOrders()
        if len(orders) == 0:
            eve.Message('CustomInfo', {'info': mls.UI_MARKET_EXPORTNODATA})
            return 
        date = util.FmtDate(blue.os.GetTime())
        f = blue.os.CreateInstance('blue.ResFile')
        invalidChars = '\\/:*?"<>|'
        directory = blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL) + '\\EVE\\logs\\Marketlogs\\'
        filename = '%s-%s.txt' % ([mls.UI_MARKET_MYORDERS, mls.UI_MARKET_CORPORDERS][self.isCorp], util.FmtDate(blue.os.GetTime(), 'ls').replace(':', ''))
        if not f.Open(directory + filename, 0):
            f.Create(directory + filename)
        first = 1
        dateIdx = -1
        numSell = numBuy = 0
        for order in orders:
            if first:
                for key in order.__columns__:
                    f.Write('%s,' % key)
                    if key == 'charID':
                        f.Write('charName,')
                    elif key == 'regionID':
                        f.Write('regionName,')
                    elif key == 'stationID':
                        f.Write('stationName,')
                    elif key == 'solarSystemID':
                        f.Write('solarSystemName,')

                f.Write('\r\n')
                first = 0
            for key in order.__columns__:
                o = getattr(order, key, None)
                if key == 'bid':
                    if o > 0:
                        numBuy += 1
                    else:
                        numSell += 1
                if key == 'issueDate':
                    f.Write('%s,' % util.FmtDate(o, 'el').replace('T', ' '))
                elif key == 'charID':
                    f.Write('%s,%s,' % (o, str(cfg.eveowners.Get(o).name.encode('utf-8'))))
                elif key in ('stationID', 'regionID', 'solarSystemID'):
                    f.Write('%s,%s,' % (o, cfg.evelocations.Get(o).name.encode('utf-8')))
                else:
                    f.Write('%s,' % o)

            f.Write('\r\n')

        f.Close()
        eve.Message('PersonalMarketExportInfo', {'sell': numSell,
         'buy': numBuy,
         'filename': '<b>' + filename + '</b>',
         'directory': '<b>%s</b>' % directory})



    def UpdateCounter(self, current = None):
        if current is None:
            current = 0
        maxCount = self.limits['cnt']
        countertext = mls.UI_MARKET_TEXT1_2 % {'remaining': maxCount - current,
         'maxCount': maxCount,
         'order': uix.Plural(maxCount, 'UI_GENERIC_ORDER'),
         'escrow': util.FmtISK(self.totalEscrow, showFractionsAlways=False),
         'totalleft': util.FmtISK(self.totalLeft, showFractionsAlways=False),
         'feelimit': round(self.limits['fee'] * 100, 2),
         'acclimit': round(self.limits['acc'] * 100, 2),
         'income': util.FmtISK(self.totalIncome, showFractionsAlways=False),
         'expenses': util.FmtISK(self.totalExpenses, showFractionsAlways=False)}
        self.sr.counter.text = countertext
        askLimit = self.limits['ask']
        bidLimit = self.limits['bid']
        modLimit = self.limits['mod']
        visLimit = self.limits['vis']
        if askLimit == -1 and bidLimit == -1 and modLimit == -1:
            self.sr.counter2.text = mls.UI_MARKET_TEXT2
        elif askLimit == -1:
            askText = mls.UI_MARKET_LIMITEDTOSTATIONS
        elif askLimit == 0:
            askText = mls.UI_MARKET_LIMITEDTOSOLARSYSTEMS
        elif askLimit == 50:
            askText = mls.UI_MARKET_LIMITEDTOREGIONS
        else:
            askText = mls.UI_MARKET_LIMITEDTOJUMPS % {'jumps': askLimit,
             'jump': uix.Plural(askLimit, 'UI_GENERIC_JUMP')}
        if bidLimit == -1:
            bidText = mls.UI_MARKET_LIMITEDTOSTATIONS
        elif bidLimit == 0:
            bidText = mls.UI_MARKET_LIMITEDTOSOLARSYSTEMS
        elif bidLimit == 50:
            bidText = mls.UI_MARKET_LIMITEDTOREGIONS
        else:
            bidText = mls.UI_MARKET_LIMITEDTOJUMPS % {'jumps': bidLimit,
             'jump': uix.Plural(bidLimit, 'UI_GENERIC_JUMP')}
        if modLimit == -1:
            modText = mls.UI_MARKET_LIMITEDTOSTATIONS
        elif modLimit == 0:
            modText = mls.UI_MARKET_LIMITEDTOSOLARSYSTEMS
        elif modLimit == 50:
            modText = mls.UI_MARKET_LIMITEDTOREGIONS
        else:
            modText = mls.UI_MARKET_LIMITEDTOJUMPS % {'jumps': modLimit,
             'jump': uix.Plural(modLimit, 'UI_GENERIC_JUMP')}
        if visLimit == -1:
            visText = mls.UI_MARKET_LIMITEDTOSTATIONS
        elif visLimit == 0:
            visText = mls.UI_MARKET_LIMITEDTOSOLARSYSTEMS
        elif visLimit == 50:
            visText = mls.UI_MARKET_LIMITEDTOREGIONS
        else:
            visText = mls.UI_MARKET_LIMITEDTOJUMPS % {'jumps': visLimit,
             'jump': uix.Plural(visLimit, 'UI_GENERIC_JUMP')}
        self.sr.counter2.text = mls.UI_MARKET_TEXT3 % {'askText': askText,
         'bidText': bidText,
         'modText': modText,
         'visText': visText}
        self.sr.counter.parent.height = max(60, self.sr.counter.textheight + const.defaultPadding, self.sr.counter2.textheight + const.defaultPadding)



    def _OnSizeChange_NoBlock(self, newWidth, newHeight):
        if not self.destroyed and self.sr.sellParent:
            self.scrollHeight = newHeight - 60 - 50
            height = (newHeight - 46) / 2
            ratio = settings.user.ui.Get('orderScrollHeight', 0.5)
            h = int(ratio * newHeight)
            if h > self.scrollHeight:
                h = self.scrollHeight
            self.sr.sellParent.height = h
            self.sr.divider.max = self.scrollHeight



    def OnOrderBuyColumnChanged(self, *args):
        self.ShowOrders(isCorp=self.isCorp)



    def OnOrderSellColumnChanged(self, *args):
        self.ShowOrders(isCorp=self.isCorp)



    def ShowOrders(self, isCorp = False, refreshing = 0):
        if isCorp is None:
            isCorp = False
        if self.isCorp is None:
            self.isCorp = isCorp
        sscrollList = []
        sheaders = self.sr.sellScroll.sr.headers = [mls.UI_GENERIC_TYPE,
         mls.UI_GENERIC_QUANTITY,
         mls.UI_GENERIC_PRICE,
         mls.UI_GENERIC_LOCATION,
         mls.UI_GENERIC_EXPIRESIN]
        if self.isCorp:
            sheaders.append(mls.UI_GENERIC_ISSUEDBY)
            sheaders.append(mls.UI_GENERIC_WALLETDIVISION)
        visibleSHeaders = self.sr.sellScroll.GetColumns()
        bscrollList = []
        bheaders = self.sr.buyScroll.sr.headers = [mls.UI_GENERIC_TYPE,
         mls.UI_GENERIC_QUANTITY,
         mls.UI_GENERIC_PRICE,
         mls.UI_GENERIC_LOCATION,
         mls.UI_GENERIC_RANGE,
         mls.UI_GENERIC_MINVOLUME,
         mls.UI_GENERIC_EXPIRESIN]
        if self.isCorp:
            bheaders.append(mls.UI_GENERIC_ISSUEDBY)
            bheaders.append(mls.UI_GENERIC_WALLETDIVISION)
        visibleBHeaders = self.sr.buyScroll.GetColumns()
        marketUtil = sm.GetService('marketutils')
        if self.isCorp:
            orders = sm.GetService('marketQuote').GetCorporationOrders()
        else:
            orders = sm.GetService('marketQuote').GetMyOrders()
        if self.destroyed:
            return 
        self.totalEscrow = 0.0
        self.totalLeft = 0.0
        self.totalIncome = 0.0
        self.totalExpenses = 0.0
        buySelected = self.sr.buyScroll.GetSelected()
        sellSelected = self.sr.sellScroll.GetSelected()
        funcs = sm.GetService('marketutils').GetFuncMaps()
        for order in orders:
            scroll = [self.sr.sellScroll, self.sr.buyScroll][order.bid]
            if scroll == self.sr.sellScroll:
                self.totalIncome += order.price * order.volRemaining
            else:
                self.totalExpenses += order.price * order.volRemaining
            data = util.KeyVal()
            data.label = ''
            data.typeID = order.typeID
            data.order = order
            if cfg.invtypes.GetIfExists(order.typeID) is not None:
                data.showinfo = 1
            selected = [sellSelected, buySelected][order.bid]
            if selected and selected[0].order.orderID == order.orderID:
                data.isSelected = 1
            visibleHeaders = [visibleSHeaders, visibleBHeaders][order.bid]
            for header in visibleHeaders:
                funcName = funcs.get(header, None)
                if funcName == 'GetQuantity':
                    funcName = 'GetQuantitySlashVolume'
                if funcName and hasattr(marketUtil, funcName):
                    apply(getattr(marketUtil, funcName, None), (order, data))
                else:
                    log.LogWarn('Unsupported header in record', header, order)
                    data.label += '###<t>'

            data.label = data.label.rstrip('<t>')
            [sscrollList, bscrollList][order.bid].append(listentry.Get('OrderEntry', data=data))
            if order.bid:
                self.totalEscrow += order.escrow
                self.totalLeft += order.volRemaining * order.price - order.escrow

        buyScrollTo = None
        sellScrollTo = None
        if refreshing:
            buyScrollTo = self.sr.buyScroll.GetScrollProportion()
            sellScrollTo = self.sr.sellScroll.GetScrollProportion()
        self.sr.sellScroll.Load(contentList=sscrollList, headers=sheaders, scrollTo=sellScrollTo, noContentHint=mls.UI_MARKET_NOORDERSFOUND)
        self.sr.buyScroll.Load(contentList=bscrollList, headers=bheaders, scrollTo=buyScrollTo, noContentHint=mls.UI_MARKET_NOORDERSFOUND)
        if not isCorp:
            self.UpdateCounter(len(orders))




class OrderEntry(listentry.Generic):
    __guid__ = 'listentry.OrderEntry'
    __nonpersistvars__ = []

    def GetMenu(self):
        self.OnClick()
        m = []
        if self.sr.node.order.charID == session.charid:
            m.append((mls.UI_CMD_CANCELORDER, self.CancelOffer, (self.sr.node,)))
            m.append((mls.UI_CMD_MODIFYORDER, self.ModifyPrice, (self.sr.node,)))
        m.append(None)
        m += sm.GetService('menu').GetMenuFormItemIDTypeID(None, self.sr.node.order.typeID, ignoreMarketDetails=0)
        m.append(None)
        stationInfo = sm.GetService('ui').GetStation(self.sr.node.order.stationID)
        m += [(mls.UI_CMD_LOCATION, sm.GetService('menu').CelestialMenu(self.sr.node.order.stationID, typeID=stationInfo.stationTypeID, parentID=stationInfo.solarSystemID))]
        return m



    def ShowInfo(self, *args):
        sm.GetService('info').ShowInfo(self.sr.node.order.typeID)



    def CancelOffer(self, node = None):
        if eve.Message('CancelMarketOrder', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return 
        node = node if node != None else self.sr.node
        sm.GetService('marketQuote').CancelOrder(node.order.orderID, node.order.regionID)



    def ModifyPrice(self, node = None):
        node = node if node != None else self.sr.node
        sm.GetService('marketutils').ModifyOrder(node.order)




