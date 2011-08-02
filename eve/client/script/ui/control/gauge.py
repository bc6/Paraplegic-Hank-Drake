import uiconst
import util
import uicls
import uthread

class _GaugeBase(uicls.Container):
    __guid__ = 'uicls._GaugeBase'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_left = 0
    default_top = 0
    default_width = 100
    default_height = 30

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        labelTxt = attributes.Get('label', '')
        subTxt = attributes.Get('subText', '')
        self.uiEffects = uicls.UIEffects()
        self.markers = {}
        self.busy = False
        self.queuedSetValue = None
        self.label = uicls.Label(text=labelTxt.upper(), parent=self, align=uiconst.RELATIVE, autowidth=1, autoheight=1, letterspace=1, fontsize=10, state=uiconst.UI_DISABLED)
        self.subText = uicls.Label(text=subTxt, parent=self, align=uiconst.RELATIVE, autowidth=1, autoheight=1, letterspace=1, fontsize=10, top=self.height - 10, state=uiconst.UI_DISABLED)
        self.gaugeCont = uicls.Container(parent=self, name='gaugeCont', pos=(0,
         12,
         self.width,
         self.height - 24), align=uiconst.TOPLEFT)



    def _SetValue(self, gauge, value, frequency):
        if not self or self.destroyed:
            return 
        self.busy = True
        self.value = value
        self.uiEffects.MorphUIMassSpringDamper(gauge, 'width', int(self.width * value), newthread=0, float=0, dampRatio=0.6, frequency=frequency, minVal=0, maxVal=self.width, maxTime=2.0)
        if not self or self.destroyed:
            return 
        self.busy = False
        if self.queuedSetValue:
            nextSetValue = self.queuedSetValue
            self.queuedSetValue = None
            self._SetValue(*nextSetValue)



    def ShowMarker(self, value, width = 1, color = util.Color.WHITE):
        self.HideMarker(value)
        left = int(self.width * value)
        marker = uicls.Fill(parent=self.gaugeCont, name='marker', color=color, align=uiconst.TOPLEFT, pos=(left,
         0,
         width,
         self.gaugeCont.height), state=uiconst.UI_DISABLED, idx=0)
        self.markers[value] = marker



    def ShowMarkers(self, values, width = 1, color = util.Color.WHITE):
        for value in values:
            self.ShowMarker(value, width, color)




    def HideMarker(self, value):
        if value in self.markers:
            self.markers[value].Close()
            self.markers.pop(value)



    def HideAllMarkers(self):
        for marker in self.markers.values():
            marker.Close()

        self.markers = {}



    def SetSubText(self, text):
        self.subText.SetText(text)



    def SetText(self, text):
        self.label.text = text




class Gauge(_GaugeBase):
    __guid__ = 'uicls.Gauge'
    default_name = 'Gauge'

    def ApplyAttributes(self, attributes):
        _GaugeBase.ApplyAttributes(self, attributes)
        color = attributes.Get('color', util.Color.WHITE)
        backgroundColor = attributes.Get('backgroundColor', None)
        self.value = attributes.Get('value', 0.0)
        self.cyclic = attributes.Get('cyclic', False)
        self.gauge = uicls.Fill(parent=self.gaugeCont, name='gauge', align=uiconst.TOLEFT, width=0, color=color)
        if backgroundColor is None:
            backgroundColor = util.Color(*color).SetAlpha(0.2).GetRGBA()
        uicls.Fill(parent=self.gaugeCont, name='background', color=backgroundColor)
        self.SetValueInstantly(self.value)



    def SetValue(self, value, frequency = 10.0):
        if self.value == value:
            return 
        if self.busy:
            self.queuedSetValue = (self.gauge, value, frequency)
            return 
        if self.cyclic and self.value > value:
            self.SetValueInstantly(value, gaugeNum)
        else:
            uthread.new(self._SetValue, self.gauge, value, frequency)



    def SetValueInstantly(self, value):
        self.value = value
        self.gauge.width = int(self.width * value)




class GaugeMultiValue(_GaugeBase):
    __guid__ = 'uicls.GaugeMultiValue'
    default_name = 'GaugeMultiValue'

    def ApplyAttributes(self, attributes):
        _GaugeBase.ApplyAttributes(self, attributes)
        colors = attributes.Get('colors', [])
        values = attributes.Get('values', [])
        backgroundColor = attributes.Get('backgroundColor', util.Color.WHITE)
        numGauges = len(colors)
        self.gauges = []
        for gaugeNum in xrange(numGauges):
            gauge = uicls.Fill(parent=self.gaugeCont, name='gauge%s' % gaugeNum, align=uiconst.TOPLEFT, pos=(0,
             0,
             0,
             self.gaugeCont.height), color=colors[gaugeNum])
            self.gauges.append(gauge)

        backgroundColor = util.Color(*backgroundColor).SetAlpha(0.2).GetRGBA()
        uicls.Fill(parent=self.gaugeCont, name='background', color=backgroundColor)
        for (gaugeNum, value,) in enumerate(values):
            self.SetValueInstantly(gaugeNum, value)




    def SetValue(self, gaugeNum, value, frequency = 10.0):
        if self.busy:
            self.queuedSetValue = (self.gauges[gaugeNum], value, frequency)
            return 
        uthread.new(self._SetValue, self.gauges[gaugeNum], value, frequency)



    def SetValueInstantly(self, gaugeNum, value):
        self.gauges[gaugeNum].width = int(self.width * value)




