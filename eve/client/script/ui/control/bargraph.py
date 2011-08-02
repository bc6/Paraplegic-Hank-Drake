import uicls
import uiconst
import blue
import uthread
import util
import math
COLOR_FRAME = (1.0,
 1.0,
 1.0,
 0.5)

class BarGraph(uicls.Container):
    __guid__ = 'uicls.BarGraph'
    default_name = 'barGraph'
    default_maxValue = 1.0
    default_barUpdateDelayMs = 10
    default_backgroundColor = (0.0, 0.0, 0.0, 0.9)
    default_timeIndicatorColor = (1.0, 1.0, 1.0, 0.6)
    UPDATEINTERVAL_NORMAL = 100
    UPDATEINTERVAL_NEWBARS = 1500

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.barUpdateDelayMs = attributes.get('barUpdateDelayMs', self.default_barUpdateDelayMs)
        backgroundColor = attributes.get('backgroundColor', self.default_backgroundColor)
        timeIndicatorColor = attributes.get('timeIndicatorColor', self.default_timeIndicatorColor)
        self.barHintFunc = attributes.get('barHintFunc', None)
        self.bars = []
        self.busy = None
        self.queuedValues = None
        self.numBars = None
        self.setValuesThread = None
        self.timeIndicatorValue = 0.0
        self.maxValue = None
        self.xLabels = None
        self.timeIndicatorThread = None
        self.barWidth = None
        XAXISHEIGHT = 15
        YAXISWIDTH = 40
        self.yAxisCont = uicls.Container(parent=self, name='yAxisCont', align=uiconst.TOLEFT, width=YAXISWIDTH, padBottom=XAXISHEIGHT + 1)
        self.xAxisCont = uicls.Container(parent=self, name='xAxisCont', align=uiconst.TOBOTTOM, height=XAXISHEIGHT)
        self.graphCont = uicls.Container(parent=self, name='graphCont', align=uiconst.TOALL)
        self.timeIndicator = uicls.Line(parent=self.graphCont, name='timeIndicator', state=uiconst.UI_HIDDEN, align=uiconst.TOPLEFT, color=timeIndicatorColor, padding=(0, 1, 0, 1), width=1)
        self.backgroundCont = uicls.Container(parent=self, name='backgroundCont', align=uiconst.TOALL, padding=(1, 2, 1, 1), clipChildren=True)
        uicls.Frame(parent=self, color=COLOR_FRAME)
        uicls.Sprite(parent=self.backgroundCont, name='backgroundStripes', align=uiconst.TOTOP, height=500, texturePath='res:/UI/Texture/Bargraph/background_stripes.dds', ignoreSize=True, color=backgroundColor)
        self.barCont = uicls.Container(parent=self.graphCont, name='barCont', align=uiconst.TOALL, padding=(2, 2, 1, 1), clipChildren=True)



    def _CreateBars(self, numBars):
        self.barCont.Flush()
        self.bars = []
        self.numBars = numBars
        (l, t, w, h,) = self.barCont.GetAbsolute()
        self.barWidth = max(1, (w - 2) / self.numBars)
        for i in xrange(self.numBars):
            bar = Bar(parent=self.barCont, name='bar%s' % i, align=uiconst.TOLEFT, width=self.barWidth, height=h, barNum=i + 1)
            if self.barHintFunc:
                bar._GetBarHint = self.barHintFunc
            self.bars.append(bar)

        self.xAxisCont.padRight = w - self.barWidth * self.numBars - 2
        if self.xLabels:
            self.SetXLabels(self.xLabels)
        self.ShowTimeIndicator(self.timeIndicatorValue)



    def SetXLabels(self, labels):
        self.xAxisCont.Flush()
        self.xLabels = labels
        for (i, label,) in enumerate(labels):
            if i == len(labels) - 1:
                align = uiconst.TOPRIGHT
            else:
                align = uiconst.TOPLEFT
            XLabel(parent=self.xAxisCont, value=float(i) / (len(labels) - 1), text=label, align=align)




    def _CreateYAxis(self):
        self.yAxisCont.Flush()
        NUMYAXISLABELS = 5
        if self.maxValue == 0:
            return 
        for i in xrange(NUMYAXISLABELS):
            value = float(i) / (NUMYAXISLABELS - 1)
            YLabel(parent=self.yAxisCont, width=self.yAxisCont.width, value=value, text=util.FmtAmt(value * self.maxValue))

        yAxisFill = uicls.Fill(parent=self.yAxisCont, color=util.Color.WHITE)
        uthread.new(uicore.effect.Fade, 0.2, 0.0, yAxisFill, 300.0)



    def SetValues(self, values):
        if self.busy:
            self.queuedValues = values
            return 
        self.queuedValues = None
        self.busy = True
        updateInterval = self.UPDATEINTERVAL_NORMAL
        maxValue = max(values)
        lenValues = len(values)
        if self.numBars != lenValues:
            if self.setValuesThread:
                self.setValuesThread.kill()
            self._CreateBars(lenValues)
            updateInterval = self.UPDATEINTERVAL_NEWBARS
        YAXISRESCALEVALUE = 1
        while YAXISRESCALEVALUE < maxValue:
            YAXISRESCALEVALUE *= 10

        YAXISRESCALEVALUE *= 0.1
        if maxValue > self.maxValue or maxValue < self.maxValue - 1.3 * YAXISRESCALEVALUE:
            self.maxValue = int(math.ceil(float(maxValue) / YAXISRESCALEVALUE)) * YAXISRESCALEVALUE
            self._CreateYAxis()
        self.setValuesThread = uthread.new(self._SetValues, values)
        uthread.new(self._EnforceUpdateInterval, updateInterval)



    def _EnforceUpdateInterval(self, updateInterval):
        blue.pyos.synchro.Sleep(updateInterval)
        if not self or self.destroyed:
            return 
        self.busy = False
        if self.queuedValues:
            self.SetValues(self.queuedValues)



    def _SetValues(self, values):
        for (i, val,) in enumerate(values):
            if i >= self.numBars:
                continue
            bar = self.bars[i]
            if self.maxValue == 0:
                bar.SetValue(rawValue=0.0, maxRawValue=1.0)
            else:
                bar.SetValue(rawValue=val, maxRawValue=self.maxValue)
            if self.barUpdateDelayMs:
                blue.pyos.synchro.Sleep(self.barUpdateDelayMs)
                if not self or self.destroyed:
                    return 




    def ShowTimeIndicator(self, value, animate = True):
        if value is None:
            return 
        if self.barWidth is None:
            return 
        self.timeIndicatorValue = value
        (l, t, w, h,) = self.graphCont.GetAbsolute()
        self.timeIndicator.state = uiconst.UI_DISABLED
        self.timeIndicator.SetAlpha(1.0)
        p = self.barCont.padLeft
        self.timeIndicator.left = p + int(value * self.barWidth * self.numBars)
        self.timeIndicator.height = h
        if animate and self.timeIndicatorThread is None:
            self.timeIndicatorThread = uthread.new(self._AnimateTimeIndicator)



    def _AnimateTimeIndicator(self):
        x = 0.0
        CYCLETIME = 3.0
        k = 2 * math.pi / CYCLETIME
        while self and not self.destroyed:
            x = (x + 1.0 / blue.os.fps) % CYCLETIME
            self.timeIndicator.SetAlpha(0.3 * math.sin(k * x) + 0.7)
            blue.pyos.synchro.Yield()




    def HideTimeIndicator(self):
        self.timeIndicatorValue = None
        self.timeIndicator.state = uiconst.UI_HIDDEN
        if self.timeIndicatorThread is not None:
            self.timeIndicatorThread.kill()
            self.timeIndicatorThread = None




class Bar(uicls.Container):
    __guid__ = 'uicls._Bar'
    default_frequency = 14.0
    default_dampRatio = 1.41
    default_color = COLOR_FRAME
    default_disturbance = 0.5
    default_state = uiconst.UI_NORMAL
    BARHEIGHT = 150

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.frequency = attributes.Get('frequency', self.default_frequency)
        self.dampRatio = attributes.Get('dampRatio', self.default_dampRatio)
        self.color = attributes.Get('color', self.default_color)
        self.disturbance = attributes.Get('disturbance', self.default_disturbance)
        self.barNum = attributes.Get('barNum', 0)
        self.value = 0.0
        self.rawValue = 0.0
        self.maxRawValue = 1.0
        self.morphThread = None
        self.graphHeight = None
        self.backgroundFill = uicls.Fill(parent=self, color=util.Color.GetGrayRGBA(0.0, 0.5), state=uiconst.UI_HIDDEN)
        self.bar = uicls.Sprite(parent=self, align=uiconst.BOTTOMLEFT, color=self.color, texturePath='res:/UI/Texture/Bargraph/%s.dds' % self.BARHEIGHT, pos=(0,
         -self.BARHEIGHT,
         self.width,
         self.BARHEIGHT), state=uiconst.UI_DISABLED, padLeft=1)



    def SetValue(self, rawValue, maxRawValue, *args):
        if self.morphThread:
            self.morphThread.kill()
        initVal = self.value
        self.rawValue = rawValue
        self.maxRawValue = maxRawValue
        self.value = float(rawValue) / maxRawValue
        if not self.graphHeight:
            (l, t, w, h,) = self.GetAbsolute()
            self.graphHeight = h
        diffInPixels = math.fabs(self.GetTopFromValue(initVal) - self.GetTopFromValue(self.value))
        if diffInPixels > 2:
            self.morphThread = uicore.effect.MorphUIMassSpringDamper(self.bar, newVal=self.value, initVal=initVal, newthread=1, float=1, minVal=-1.0, maxVal=1.0, dampRatio=self.dampRatio, frequency=self.frequency, maxTime=3.0, callback=self.OnValueChanged)
        else:
            self.OnValueChanged(self, self.value)



    def OnValueChanged(self, bar, value, *args):
        if not self or self.destroyed:
            return 
        HUEMAX = 0.6
        hue = HUEMAX * max(0.0, 1.0 - value)
        color = util.Color().SetHSB(hue, 0.7, 0.8, 1.0).GetRGBA()
        self.bar.color.SetRGB(*color)
        self.bar.top = self.GetTopFromValue(value)
        self.value = value



    def GetTopFromValue(self, value):
        top = int(value * self.graphHeight - self.BARHEIGHT)
        top -= top % 2
        return top



    def GetHint(self):
        return self._GetBarHint(self.barNum, self.rawValue, self.maxRawValue)



    def _GetBarHint(self, num, rawValue, maxRawValue):
        return '#%s: %5.2f / %5.2f' % (num, rawValue, maxRawValue)



    def OnMouseEnter(self, *args):
        if hasattr(self, 'background'):
            self.backgroundFill.state = uiconst.UI_DISABLED



    def OnMouseExit(self, *args):
        if hasattr(self, 'background'):
            self.backgroundFill.state = uiconst.UI_HIDDEN




class LabelText(uicls.Label):
    __guid__ = 'uicls._GraphLabelText'
    default_color = (1.0, 1.0, 1.0, 0.6)
    default_fontsize = 9
    default_autoheight = True
    default_autowidth = True


class YLabel(uicls.Container):
    __guid__ = 'uicls._GraphYLabel'
    default_align = uiconst.BOTTOMRIGHT
    default_height = 20

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        value = attributes.Get('value')
        text = attributes.Get('text', '%s' % value)
        (l, t, w, h,) = self.parent.GetAbsolute()
        self.top = int(h * value)
        LabelText(parent=self, text=text, align=uiconst.BOTTOMRIGHT, top=-5, left=5)
        uicls.Line(parent=self, color=COLOR_FRAME, align=uiconst.BOTTOMRIGHT, width=4, height=1, top=-1)




class XLabel(uicls.Container):
    __guid__ = 'uicls._GraphXLabel'
    default_align = uiconst.TOPLEFT
    default_width = 100
    default_height = 20

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        value = attributes.Get('value')
        text = attributes.Get('text', '%s' % value)
        (l, t, w, h,) = self.parent.GetAbsolute()
        LabelText(parent=self, text=text, align=self.align, top=5)
        uicls.Line(parent=self, color=COLOR_FRAME, align=self.align, width=1, height=4)




