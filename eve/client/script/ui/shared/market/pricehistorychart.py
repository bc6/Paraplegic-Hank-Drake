import uix
import uiutil
import xtriui
import uthread
import util
import blue
import base
import listentry
import trinity
import uicls
import uiconst
from pychartdir import *

class PriceHistoryParent(uicls.Container):
    __guid__ = 'xtriui.PriceHistoryParent'
    __nonpersistvars__ = []

    def init(self):
        self.inited = 0
        self.sr.pricehistory = None



    def Startup(self):
        self.sr.pricehistory = xtriui.PriceHistory(name='ph', parent=self, align=uiconst.TOALL, pos=(const.defaultPadding,
         0,
         const.defaultPadding,
         0))
        self.inited = 1



    def LoadType(self, invType):
        self.sr.pricehistory.Render(invType)




class PriceHistory(uicls.Container):
    __guid__ = 'xtriui.PriceHistory'
    __nonpersistvars__ = []
    __update_on_reload__ = 1

    def init(self):
        self.line = None
        self.marker = None
        self.highlow = None
        self.underlay = None
        self.markerparent = None
        self.wantrefresh = 1
        self.rendering = 0
        self.typerecord = None
        self.sr.options = uicls.Container(name='options', parent=self, align=uiconst.TOBOTTOM, height=42)
        self.optionsinited = 0
        self.sr.updateTimer = None
        setLicenseCode('DIST-0000-05de-f7ec-ffbeURDT-232Q-M544-C2XM-BD6E-C452')
        self.months = [mls.UI_GENERIC_JANUARYSHORT,
         mls.UI_GENERIC_FEBRUARYSHORT,
         mls.UI_GENERIC_MARCHSHORT,
         mls.UI_GENERIC_APRILSHORT,
         mls.UI_GENERIC_MAYSHORT,
         mls.UI_GENERIC_JUNESHORT,
         mls.UI_GENERIC_JULYSHORT,
         mls.UI_GENERIC_AUGUSTSHORT,
         mls.UI_GENERIC_SEPTEMBERSHORT,
         mls.UI_GENERIC_OCTOBERSHORT,
         mls.UI_GENERIC_NOVEMBERSHORT,
         mls.UI_GENERIC_DECEMBERSHORT]



    def _OnResize(self, *args):
        if self.rendering:
            return 
        if self.typerecord:
            self.sr.updateTimer = base.AutoTimer(500, self.UpdateSize)



    def UpdateSize(self):
        uthread.new(self.Render, self.typerecord)
        self.sr.updateTimer = None



    def InitOptions(self):
        uix.Flush(self.sr.options)
        idx = settings.user.ui.Get('pricehistorytype', 0)
        btn = uicls.Button(parent=self.sr.options, label=[mls.UI_CMD_SHOWTABLE, mls.UI_CMD_SHOWGRAPH][idx], align=uiconst.TOPLEFT, pos=(0, 16, 0, 0), func=self.ToggleView, args='self', fixedwidth=100)
        pos = btn.width + btn.left + 10
        timeOptions = [['5 %s' % mls.UI_GENERIC_DAYS, 5],
         ['10 %s' % mls.UI_GENERIC_DAYS, 10],
         [mls.UI_GENERIC_MONTH, 30],
         ['3 %s' % mls.UI_GENERIC_MONTHS, 90],
         ['6 %s' % mls.UI_GENERIC_MONTHS, 180],
         [mls.UI_GENERIC_YEAR, 365]]
        timeCombo = uicls.Combo(label=mls.UI_GENERIC_TIME, parent=self.sr.options, options=timeOptions, name='pricehistorytime', select=settings.user.ui.Get('pricehistorytime', 90), callback=self.ChangeOption, pos=(pos,
         16,
         0,
         0))
        pos += timeCombo.width + 10
        graphTipCont = uicls.Container(name='graphTipCont', parent=self.sr.options, align=uiconst.BOTTOMLEFT, height=20, width=200, left=pos, top=0)
        self.graphTip = uicls.Label(text=mls.UI_MARKET_PRICEHISTORYCHARTHINT, parent=graphTipCont, left=0, top=0, align=uiconst.TOALL, fontsize=12, state=uiconst.UI_DISABLED, idx=0, autowidth=False, autoheight=False)
        graphTipCont.height = self.graphTip.textheight + 10
        self.graphTip.state = [uiconst.UI_NORMAL, uiconst.UI_HIDDEN][settings.user.ui.Get('pricehistorytype', 0)]
        self.optionsinited = 1



    def OnCheckboxChange(self, sender, *args):
        settings.user.ui.Set(sender.name, bool(sender.checked))
        self.InitOptions()
        if self.typerecord:
            uthread.new(self.Render, self.typerecord)



    def ToggleView(self, btn, *args):
        settings.user.ui.Set('pricehistorytype', not settings.user.ui.Get('pricehistorytype', 0))
        btn.SetLabel([mls.UI_CMD_SHOWTABLE, mls.UI_CMD_SHOWGRAPH][settings.user.ui.Get('pricehistorytype', 0)])
        btn.width = 100
        self.graphTip.state = [uiconst.UI_NORMAL, uiconst.UI_HIDDEN][settings.user.ui.Get('pricehistorytype', 0)]
        if self.typerecord:
            uthread.new(self.Render, self.typerecord)



    def CheckBoxChange(self, checkbox):
        settings.user.ui.Set(checkbox.data['config'], checkbox.data['value'])
        self.InitOptions()
        if self.typerecord:
            uthread.new(self.Render, self.typerecord)



    def ChangeOption(self, entry, header, value, *args):
        settings.user.ui.Set('pricehistorytime', value)
        self.InitOptions()
        if self.typerecord:
            uthread.new(self.Render, self.typerecord)



    def GetSize(self):
        (abswidth, absheight,) = (self.absoluteRight - self.absoluteLeft, self.absoluteBottom - self.absoluteTop)
        if not abswidth or not absheight:
            uiutil.Update(self, 'PriceHistory::GetSize')
            (abswidth, absheight,) = (self.absoluteRight - self.absoluteLeft, self.absoluteBottom - self.absoluteTop)
        return (abswidth, absheight - self.sr.options.height)



    def RenderTable(self):
        scroll = uicls.Scroll(parent=self, padding=(1, 1, 1, 1))
        scroll.sr.id = 'pricehistoryscroll'
        scroll.smartSort = 0
        scroll.OnColumnChanged = self.OnColumnChanged
        history = sm.GetService('marketQuote').GetPriceHistory(self.typerecord.typeID)
        windowData = settings.user.ui.Get('pricehistorytime', 90)
        if len(history) > windowData:
            history = history[(-(windowData + 1)):]
        scrolllist = []
        for rec in history:
            text = '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (util.FmtDate(rec[0]),
             util.FmtAmt(rec[5]),
             util.FmtAmt(rec[4]),
             util.FmtCurrency(rec[1], currency=None),
             util.FmtCurrency(rec[2], currency=None),
             util.FmtCurrency(rec[3], currency=None))
            data = {'tabs': [],
             'text': text,
             'sort_%s' % mls.UI_GENERIC_QUANTITY: rec[4],
             'sort_%s' % mls.UI_GENERIC_ORDERSCAP: rec[5],
             'sort_%s' % mls.UI_GENERIC_LOW: rec[1],
             'sort_%s' % mls.UI_GENERIC_HIGH: rec[2],
             'sort_%s' % mls.UI_GENERIC_AVERAGESHORT: rec[3],
             'sort_%s' % mls.UI_GENERIC_DATE: rec[0]}
            data2 = util.KeyVal()
            data2.label = text
            scrolllist.append(listentry.Get('Generic', data=data2))

        scroll.Load(fixedEntryHeight=18, contentList=scrolllist, headers=[mls.UI_GENERIC_DATE,
         mls.UI_GENERIC_ORDERSCAP,
         mls.UI_GENERIC_QUANTITY,
         mls.UI_GENERIC_LOW,
         mls.UI_GENERIC_HIGH,
         mls.UI_GENERIC_AVERAGESHORT])



    def OnColumnChanged(self, *args):
        if self.typerecord:
            uthread.new(self.Render, self.typerecord)



    def GetLocale(self):
        fontSize = 7.5
        fontFace = 'arial.ttc'
        if prefs.languageID == 'ZH':
            fontFace = 'simsun.ttc'
            fontSize = 8
        return (fontFace, fontSize)



    def GetChart(self, typeID, days):
        history = sm.GetService('marketQuote').GetPriceHistory(typeID)
        timeStamps = []
        volData = []
        closeData = []
        lowData = []
        highData = []
        for x in history:
            if x[0] in timeStamps:
                continue
            timeStamps.append(x[0])
            volData.append(x[4])
            closeData.append(x[3])
            lowData.append(x[1])
            highData.append(x[2])

        availableData = len(timeStamps)
        windowData = settings.user.ui.Get('pricehistorytime', 90)
        (fontFace, fontSize,) = self.GetLocale()
        trimData = availableData - windowData
        (graphWidth, graphHeight,) = self.GetSize()
        for i in range(len(timeStamps)):
            stamp = timeStamps[i]
            (year, month, wd, day, hour, min, sec, ms,) = util.GetTimeParts(stamp)
            timeStamps[i] = chartTime(year, month, day)

        isExtrapolated = 0
        daysAdded = 0
        if trimData < 0:
            daysAdded = -trimData
            isExtrapolated = 1
            trimData = 0
        elif windowData < 30:
            daysAdded = 5
            isExtrapolated = 1
        lastStamp = timeStamps[-1]
        for i in range(daysAdded):
            timeStamps.append(lastStamp + (i + 1) * 86400)

        actualData = availableData - trimData
        if windowData > 90:
            labels = ArrayMath(timeStamps).trim(trimData).selectStartOfMonth().result()
        elif windowData >= 10:
            labels = ArrayMath(timeStamps).trim(trimData).selectStartOfWeek().result()
        else:
            labels = ArrayMath(timeStamps).trim(trimData).selectStartOfDay().result()
        priceWidth = graphWidth
        priceHeight = graphHeight
        c = XYChart(priceWidth, priceHeight, Transparent)
        c.setMonthNames(self.months)
        palette = whiteOnBlackPalette
        BORDER_COLOR = 8947848
        palette[1] = BORDER_COLOR
        c.setColors(whiteOnBlackPalette)
        c.setBackground(Transparent)
        c.setTransparentColor(-1)
        c.setAntiAlias(1, 1)
        if availableData == 0:
            textBox = c.addText(20, graphHeight / 5, mls.UI_MARKET_NOHISTORICDATA, 'normal', 24)
            return c.makeChart2(PNG)
        axis = c.yAxis()
        axis.setLabelStyle(fontFace, fontSize)
        axis.setAutoScale(0.1, 0.1, 0.3)
        axis.setTickDensity(40, -1)
        axis = c.yAxis2()
        axis.setLabelFormat('{value|,}')
        axis.setLabelStyle(fontFace, fontSize)
        axis.setAutoScale(0.8, 0.0, 1.0)
        axis.setColors(BORDER_COLOR, Transparent)
        c.xAxis().setLabels2(labels, '{value|d mmm}')
        if windowData == 90:
            c.xAxis().setLabelStep(2)
        elif windowData == 365:
            c.xAxis().setLabelStep(2)
        c.xAxis().setLabelStyle(fontFace, fontSize)
        c.setXAxisOnTop()
        c.setPlotArea(70, 20, priceWidth - 110, priceHeight - 40, 1711276032, -1, -1, 5592405)
        legend = c.addLegend(105, 18, 0, fontFace, fontSize)
        legend.setBackground(Transparent)
        legend.setWidth(priceWidth - 150)
        trimmedCloseData = ArrayMath(closeData).trim(trimData).result()
        lst = []
        if not settings.user.ui.Get('market_setting_minmax', 1) and not settings.user.ui.Get('market_setting_donchian', 1):
            highData = lowData = closeData
        hloLayer = c.addHLOCLayer(ArrayMath(highData).trim(trimData).result(), ArrayMath(lowData).trim(trimData).result(), trimmedCloseData, [])
        hiloCol = LtoI(3724541696L) if settings.user.ui.Get('market_setting_minmax', 1) else Transparent
        hloLayer.getDataSet(0).setDataColor(hiloCol)
        hloLayer.getDataSet(2).setDataColor(Transparent)
        hloLayer.getDataSet(3).setDataColor(Transparent)
        if settings.user.ui.Get('market_setting_movingavg5', 1) or settings.user.ui.Get('market_setting_movingavg20', 1):
            if isExtrapolated:
                if settings.user.ui.Get('market_setting_movingavg5', 1):
                    avg5 = c.addLineLayer2()
                    lineColor = avg5.xZoneColor(actualData - 1, 16711680, c.dashLineColor(13647936, DashLine))
                    avg5.addDataSet(ArrayMath(closeData + 5 * isExtrapolated * closeData[-1:]).movAvg(5).trim(trimData).result(), lineColor, mls.UI_MARKET_MOVINGAVG5)
                if settings.user.ui.Get('market_setting_movingavg20', 1):
                    avg20 = c.addLineLayer2()
                    lineColor = avg20.xZoneColor(actualData - 1, 6750054, c.dashLineColor(4247616, DashLine))
                    avg20.addDataSet(ArrayMath(closeData + 5 * isExtrapolated * closeData[-1:]).movAvg(20).trim(trimData).result(), lineColor, mls.UI_MARKET_MOVINGAVG20)
            else:
                if settings.user.ui.Get('market_setting_movingavg5', 1):
                    avg5 = c.addLineLayer(ArrayMath(closeData).movAvg(5).trim(trimData).result(), 16711680, mls.UI_MARKET_MOVINGAVG5)
                if settings.user.ui.Get('market_setting_movingavg20', 1):
                    avg20 = c.addLineLayer(ArrayMath(closeData).movAvg(20).trim(trimData).result(), 6750054, mls.UI_MARKET_MOVINGAVG20)
        if settings.user.ui.Get('market_setting_donchian', 1):
            upperBand = ArrayMath(highData).movMax(5).trim(trimData).result()
            lowerBand = ArrayMath(lowData).movMin(5).trim(trimData).result()
            uLayer = c.addLineLayer(upperBand, LtoI(2868864614L), mls.UI_MARKET_DONCHIANCHANNEL)
            lLayer = c.addLineLayer(lowerBand, LtoI(2868864614L))
            c.addInterLineLayer(uLayer.getLine(), lLayer.getLine(), LtoI(3674170982L))
        if settings.user.ui.Get('market_setting_mediandayprice', 1):
            lineLayer = c.addLineLayer(ArrayMath(closeData).trim(trimData).result(), Transparent, mls.UI_MARKET_MEDIANDAYPRICE)
            lineLayer.getDataSet(0).setDataSymbol(SquareSymbol, 5, fillColor=16776960, edgeColor=3355392)
        if settings.user.ui.Get('market_setting_volume', 1):
            barLayer = c.addBarLayer(ArrayMath(volData).trim(trimData).result(), 10092441)
            barLayer.setBorderColor(Transparent)
            barLayer.getDataSet(0).setUseYAxis2(1)
            if windowData <= 30:
                barLayer.setBarWidth(3)
        val = max(trimmedCloseData)
        lf = '{value|2,.}'
        if val < 10000L:
            lf = '{value|2,.}'
        elif val < 1000000L:
            lf = '{={value}/1000|2,.}%s' % mls.K_FOR_THOUSAND
        elif val < 1000000000L:
            lf = '{={value}/1000000|2,.}%s' % mls.M_FOR_MILLION
        elif val < 1000000000000L:
            lf = '{={value}/1000000000|2,.}%s' % mls.B_FOR_BILLION
        else:
            lf = '{={value}/1000000000000|2,.}%s' % mls.T_FOR_TRILLION
        c.yAxis().setLabelFormat(lf)
        c.layout()
        yAxis = c.yAxis2()
        ticks = yAxis.getTicks()
        if len(ticks) > 2:
            for i in range(3):
                markValue = ticks[i]
                mark = yAxis.addMark(markValue, Transparent, util.FmtAmt(markValue, fmt='ss', showFraction=1), fontFace, fontSize)
                mark.setMarkColor(Transparent, 16777215, 16777215)

        return c.makeChart2(PNG)



    def Render(self, typeRecord):
        if self.rendering:
            return 
        self.typerecord = typeRecord
        if not self.optionsinited:
            self.InitOptions()
        uiutil.FlushList(self.children[1:])
        if settings.user.ui.Get('pricehistorytype', 0):
            self.RenderTable()
            return 
        (graphWidth, graphHeight,) = self.GetSize()
        if graphWidth < 2 or graphHeight < 2:
            return 
        self.rendering = 1
        try:
            days = settings.user.ui.Get('pricehistorytime', 90)
            buf = self.GetChart(self.typerecord.typeID, days)
            surface = trinity.device.CreateOffscreenPlainSurface(graphWidth, graphHeight, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
            surface.LoadSurfaceFromFileInMemory(buf)
            linegr = uicls.Sprite(align=uiconst.TOALL)
            linegr.texture.atlasTexture = uicore.uilib.CreateTexture(graphWidth, graphHeight)
            linegr.texture.atlasTexture.CopyFromSurface(surface)
            self.children.append(linegr)
            linegr.GetMenu = self.GetGraphMenu

        finally:
            self.rendering = 0




    def GetGraphMenu(self, *args):
        PRICE_FILTERS = {'movingavg5': mls.UI_MARKET_MOVINGAVG5,
         'movingavg20': mls.UI_MARKET_MOVINGAVG20,
         'donchian': mls.UI_MARKET_DONCHIANCHANNEL,
         'mediandayprice': mls.UI_MARKET_MEDIANDAYPRICE,
         'minmax': mls.UI_MARKET_MINMAX,
         'volume': mls.UI_GENERIC_VOLUME}
        m = []
        for (name, label,) in PRICE_FILTERS.iteritems():
            m.append(('%s %s' % ([mls.UI_GENERIC_SHOW, mls.UI_GENERIC_HIDE][settings.user.ui.Get('market_setting_' + name, 1)], label), self.Toggle, (name,)))

        return m



    def Toggle(self, name):
        name = 'market_setting_' + name
        curr = settings.user.ui.Get(name, 1)
        settings.user.ui.Set(name, not curr)
        self.InitOptions()
        if self.typerecord:
            uthread.new(self.Render, self.typerecord)




class HistoryEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.HistoryEntry'

    def Startup(self, *etc):
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.label = uicls.Label(text='', parent=self, left=6, top=2, width=1000, autowidth=False, fontsize=12, state=uiconst.UI_DISABLED, idx=0)
        self.state = uiconst.UI_NORMAL



    def Load(self, node):
        self.sr.node = node
        data = node
        self.sr.label.text = data.text




