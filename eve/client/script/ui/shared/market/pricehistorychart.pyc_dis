#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/market/pricehistorychart.py
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
import localization
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
        self.months = [GetStrippedLabel('/Carbon/UI/Common/Months/JanuaryShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/FebruaryShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/MarchShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/AprilShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/MayShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/JuneShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/JulyShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/AugustShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/SeptemberShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/OctoberShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/NovemberShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/DecemberShort')]

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
        showingPriceHistoryType = settings.user.ui.Get('pricehistorytype', 0)
        if showingPriceHistoryType:
            buttonLabel = localization.GetByLabel('UI/PriceHistory/ShowGraph')
        else:
            buttonLabel = localization.GetByLabel('UI/PriceHistory/ShowTable')
        btn = uicls.Button(parent=self.sr.options, label=buttonLabel, align=uiconst.TOPLEFT, pos=(0, 16, 0, 0), func=self.ToggleView, args='self', fixedwidth=100)
        pos = btn.width + btn.left + 10
        timeOptions = [[localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Day', days=5), 5],
         [localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Day', days=10), 10],
         [localization.GetByLabel('UI/Common/DateWords/Month'), 30],
         [localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Month', months=3), 90],
         [localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Month', months=6), 180],
         [localization.GetByLabel('UI/Common/DateWords/Year'), 365]]
        timeLabel = localization.GetByLabel('/Carbon/UI/Common/Time')
        timeCombo = uicls.Combo(label=timeLabel, parent=self.sr.options, options=timeOptions, name='pricehistorytime', select=settings.user.ui.Get('pricehistorytime', 90), callback=self.ChangeOption, pos=(pos,
         16,
         0,
         0))
        pos += timeCombo.width + 10
        graphTipCont = uicls.Container(name='graphTipCont', parent=self.sr.options, align=uiconst.BOTTOMLEFT, height=20, width=200, left=pos, top=0)
        self.graphTip = uicls.EveLabelMedium(text=localization.GetByLabel('UI/Market/PriceHistory/RightClickHintForChart'), parent=graphTipCont, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, idx=0)
        graphTipCont.height = self.graphTip.textheight + 10
        if showingPriceHistoryType:
            self.graphTip.state = uiconst.UI_HIDDEN
        else:
            self.graphTip.state = uiconst.UI_NORMAL
        self.optionsinited = 1

    def OnCheckboxChange(self, sender, *args):
        settings.user.ui.Set(sender.name, bool(sender.checked))
        self.InitOptions()
        if self.typerecord:
            uthread.new(self.Render, self.typerecord)

    def ToggleView(self, btn, *args):
        settings.user.ui.Set('pricehistorytype', not settings.user.ui.Get('pricehistorytype', 0))
        showingPriceHistoryType = settings.user.ui.Get('pricehistorytype', 0)
        if showingPriceHistoryType:
            btnLabel = localization.GetByLabel('UI/PriceHistory/ShowGraph')
        else:
            btnLabel = localization.GetByLabel('UI/PriceHistory/ShowTable')
        btn.SetLabel(btnLabel)
        btn.width = 100
        if showingPriceHistoryType:
            self.graphTip.state = uiconst.UI_HIDDEN
        else:
            self.graphTip.state = uiconst.UI_NORMAL
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
        abswidth, absheight = self.absoluteRight - self.absoluteLeft, self.absoluteBottom - self.absoluteTop
        if not abswidth or not absheight:
            uiutil.Update(self, 'PriceHistory::GetSize')
            abswidth, absheight = self.absoluteRight - self.absoluteLeft, self.absoluteBottom - self.absoluteTop
        return (abswidth, absheight - self.sr.options.height)

    def RenderTable(self):
        scroll = uicls.Scroll(parent=self, padding=(1, 1, 1, 1))
        scroll.sr.id = 'pricehistoryscroll'
        scroll.smartSort = 0
        scroll.OnColumnChanged = self.OnColumnChanged
        history = sm.GetService('marketQuote').GetPriceHistory(self.typerecord.typeID)
        windowData = settings.user.ui.Get('pricehistorytime', 90)
        if len(history) > windowData:
            history = history[-(windowData + 1):]
        scrolllist = []
        for rec in history:
            text = '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (util.FmtDate(rec[0]),
             util.FmtAmt(rec[5]),
             util.FmtAmt(rec[4]),
             util.FmtCurrency(rec[1], currency=None),
             util.FmtCurrency(rec[2], currency=None),
             util.FmtCurrency(rec[3], currency=None))
            data = util.KeyVal()
            data.label = text
            data.Set('sort_%s' % localization.GetByLabel('UI/Market/PriceHistory/Quantity'), rec[4])
            data.Set('sort_%s' % localization.GetByLabel('UI/Market/PriceHistory'), rec[5])
            data.Set('sort_%s' % localization.GetByLabel('UI/Market/PriceHistory/LowestPrice'), rec[1])
            data.Set('sort_%s' % localization.GetByLabel('UI/Market/PriceHistory/HighestPrice'), rec[2])
            data.Set('sort_%s' % localization.GetByLabel('UI/Market/PriceHistory/AveragePrice'), rec[3])
            data.Set('sort_%s' % localization.GetByLabel('UI/Common/Date'), rec[0])
            scrolllist.append(listentry.Get('Generic', data=data))

        headers = [localization.GetByLabel('UI/Common/Date'),
         localization.GetByLabel('UI/Market/PriceHistory'),
         localization.GetByLabel('UI/Market/PriceHistory/Quantity'),
         localization.GetByLabel('UI/Market/PriceHistory/LowestPrice'),
         localization.GetByLabel('UI/Market/PriceHistory/HighestPrice'),
         localization.GetByLabel('UI/Market/PriceHistory/AveragePrice')]
        scroll.Load(fixedEntryHeight=18, contentList=scrolllist, headers=headers)

    def OnColumnChanged(self, *args):
        if self.typerecord:
            uthread.new(self.Render, self.typerecord)

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
        fontFace = sm.GetService('font').GetFontDefault()
        fontSize = int(8 * uicore.desktop.dpiScaling)
        trimData = availableData - windowData
        graphWidth, graphHeight = self.GetSize()
        graphWidth = int(graphWidth * uicore.desktop.dpiScaling)
        graphHeight = int(graphHeight * uicore.desktop.dpiScaling)
        for i in range(len(timeStamps)):
            stamp = timeStamps[i]
            year, month, wd, day, hour, min, sec, ms = util.GetTimeParts(stamp)
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
            textBox = c.addText(20, graphHeight / 5, localization.GetByLabel('UI/PriceHistory/NoDataAvailable'), 'normal', 24)
            return c.makeChart2(PNG)
        axis = c.yAxis()
        axis.setLabelStyle(fontFace, fontSize)
        axis.setAutoScale(0.1, 0.1, 0.3)
        axis.setTickDensity(int(40 * uicore.desktop.dpiScaling), -1)
        axis = c.yAxis2()
        axis.setLabelFormat('{value|,}')
        axis.setLabelStyle(fontFace, fontSize)
        axis.setAutoScale(0.8, 0.0, 1.0)
        axis.setColors(BORDER_COLOR, Transparent)
        labelFormatter = localization.GetByLabel('UI/PriceHistory/PriceHistoryYAxisFormatter')
        labelFormatter = labelFormatter.replace('(', '{').replace(')', '}')
        c.xAxis().setLabels2(labels, labelFormatter)
        if windowData == 90:
            c.xAxis().setLabelStep(2)
        elif windowData == 365:
            c.xAxis().setLabelStep(2)
        c.xAxis().setLabelStyle(fontFace, fontSize)
        c.setXAxisOnTop()
        paLeft = int(70 * uicore.desktop.dpiScaling)
        paTop = int(20 * uicore.desktop.dpiScaling)
        if boot.region == 'optic':
            paRight = int(130 * uicore.desktop.dpiScaling)
        else:
            paRight = int(112 * uicore.desktop.dpiScaling)
        paBottom = int(40 * uicore.desktop.dpiScaling)
        c.setPlotArea(paLeft, paTop, priceWidth - paRight, priceHeight - paBottom, 1711276032, -1, -1, 5592405)
        legendLeft = int(105 * uicore.desktop.dpiScaling)
        legendTop = int(18 * uicore.desktop.dpiScaling)
        legend = c.addLegend(legendLeft, legendTop, 0, fontFace, fontSize)
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
                    daysText = uiutil.StripTags(localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantityShort/Day', value=5), stripOnly=['localized'])
                    label = uiutil.StripTags(localization.GetByLabel('UI/PriceHistory/MovingAvg', numDays=daysText), stripOnly=['localized'])
                    avg5.addDataSet(ArrayMath(closeData + 5 * isExtrapolated * closeData[-1:]).movAvg(5).trim(trimData).result(), lineColor, label)
                if settings.user.ui.Get('market_setting_movingavg20', 1):
                    avg20 = c.addLineLayer2()
                    lineColor = avg20.xZoneColor(actualData - 1, 6750054, c.dashLineColor(4247616, DashLine))
                    daysText = uiutil.StripTags(localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantityShort/Day', value=20), stripOnly=['localized'])
                    label = uiutil.StripTags(localization.GetByLabel('UI/PriceHistory/MovingAvg', numDays=daysText), stripOnly=['localized'])
                    avg20.addDataSet(ArrayMath(closeData + 5 * isExtrapolated * closeData[-1:]).movAvg(20).trim(trimData).result(), lineColor, label)
            else:
                if settings.user.ui.Get('market_setting_movingavg5', 1):
                    daysText = uiutil.StripTags(localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantityShort/Day', value=5), stripOnly=['localized'])
                    avg5 = c.addLineLayer(ArrayMath(closeData).movAvg(5).trim(trimData).result(), 16711680, uiutil.StripTags(localization.GetByLabel('UI/PriceHistory/MovingAvg', numDays=daysText), stripOnly=['localized']))
                if settings.user.ui.Get('market_setting_movingavg20', 1):
                    daysText = uiutil.StripTags(localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantityShort/Day', value=20), stripOnly=['localized'])
                    avg20 = c.addLineLayer(ArrayMath(closeData).movAvg(20).trim(trimData).result(), 6750054, uiutil.StripTags(localization.GetByLabel('UI/PriceHistory/MovingAvg', numDays=daysText), stripOnly=['localized']))
        if settings.user.ui.Get('market_setting_donchian', 1):
            upperBand = ArrayMath(highData).movMax(5).trim(trimData).result()
            lowerBand = ArrayMath(lowData).movMin(5).trim(trimData).result()
            uLayer = c.addLineLayer(upperBand, LtoI(2868864614L), GetStrippedLabel('UI/PriceHistory/DonchianChannel'))
            lLayer = c.addLineLayer(lowerBand, LtoI(2868864614L))
            c.addInterLineLayer(uLayer.getLine(), lLayer.getLine(), LtoI(3674170982L))
        if settings.user.ui.Get('market_setting_mediandayprice', 1):
            lineLayer = c.addLineLayer(ArrayMath(closeData).trim(trimData).result(), Transparent, GetStrippedLabel('UI/PriceHistory/MedianDayPrice'))
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
            lf = GetStrippedLabel('UI/Market/PriceHistory/YaxisFormattingThousand', fmtString='{={value}/1000|2,.}')
        elif val < 1000000000L:
            lf = GetStrippedLabel('UI/Market/PriceHistory/YaxisFormattingMillion', fmtString='{={value}/1000000|2,.}')
        elif val < 1000000000000L:
            lf = GetStrippedLabel('UI/Market/PriceHistory/YaxisFormattingBillion', fmtString='{={value}/1000000000|2,.}')
        else:
            lf = GetStrippedLabel('UI/Market/PriceHistory/YaxisFormattingTrillion', fmtString='{={value}/1000000000000|2,.}T')
        c.yAxis().setLabelFormat(lf)
        c.layout()
        yAxis = c.yAxis2()
        ticks = yAxis.getTicks()
        if len(ticks) > 2:
            for i in range(3):
                markValue = ticks[i]
                label = uiutil.StripTags(util.FmtAmt(markValue, fmt='ss', showFraction=1), stripOnly=['localized'])
                mark = yAxis.addMark(markValue, Transparent, label, fontFace, fontSize)
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
        graphWidth, graphHeight = self.GetSize()
        graphWidth = int(graphWidth * uicore.desktop.dpiScaling)
        graphHeight = int(graphHeight * uicore.desktop.dpiScaling)
        if graphWidth < 2 or graphHeight < 2:
            return
        self.rendering = 1
        try:
            days = settings.user.ui.Get('pricehistorytime', 90)
            buf = self.GetChart(self.typerecord.typeID, days)
            hostBitmap = trinity.Tr2HostBitmap(graphWidth, graphHeight, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
            hostBitmap.LoadFromPngInMemory(buf)
            linegr = uicls.Sprite(align=uiconst.TOALL)
            linegr.texture.atlasTexture = uicore.uilib.CreateTexture(graphWidth, graphHeight)
            linegr.texture.atlasTexture.CopyFromHostBitmap(hostBitmap)
            self.children.append(linegr)
            linegr.GetMenu = self.GetGraphMenu
        finally:
            self.rendering = 0

    def GetGraphMenu(self, *args):
        avg5 = localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantityShort/Day', value=5)
        avg20 = localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantityShort/Day', value=20)
        PRICE_FILTERS = {'movingavg5': (localization.GetByLabel('UI/Market/PriceHistory/ShowMovingAvg', numDays=avg5), localization.GetByLabel('UI/Market/PriceHistory/HideMovingAvg', numDays=avg5)),
         'movingavg20': (localization.GetByLabel('UI/Market/PriceHistory/ShowMovingAvg', numDays=avg20), localization.GetByLabel('UI/Market/PriceHistory/HideMovingAvg', numDays=avg20)),
         'donchian': (localization.GetByLabel('UI/Market/PriceHistory/ShowDonchianChannel'), localization.GetByLabel('UI/Market/PriceHistory/HideDonchianChannel')),
         'mediandayprice': (localization.GetByLabel('UI/Market/PriceHistory/ShowMedianDayPrice'), localization.GetByLabel('UI/Market/PriceHistory/HideMedianDayPrice')),
         'minmax': (localization.GetByLabel('UI/Market/PriceHistory/ShowMinMax'), localization.GetByLabel('UI/Market/PriceHistory/HideMinMax')),
         'volume': (localization.GetByLabel('UI/Market/PriceHistory/ShowVolume'), localization.GetByLabel('UI/Market/PriceHistory/HideVolume'))}
        m = []
        for name, labels in PRICE_FILTERS.iteritems():
            showing = settings.user.ui.Get('market_setting_' + name, 1)
            if showing:
                string = labels[1]
            else:
                string = labels[0]
            m.append((string, self.Toggle, (name,)))

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
        self.sr.label = uicls.EveLabelMedium(text='', parent=self, left=6, top=2, width=1000, state=uiconst.UI_DISABLED, idx=0)
        self.state = uiconst.UI_NORMAL

    def Load(self, node):
        self.sr.node = node
        data = node
        self.sr.label.text = data.text


def GetStrippedLabel(path, **kwargs):
    label = localization.GetByLabel(path, **kwargs)
    if isinstance(label, basestring):
        label = uiutil.StripTags(label, stripOnly=['localized'])
    return label