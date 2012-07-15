#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/control/slider.py
import uiutil
import mathUtil
import uthread
import util
import blue
import uicls
import uiconst
import localizationUtil
import xtriui

class Slider(uicls.Container):
    __guid__ = 'xtriui.Slider'
    default_align = uiconst.RELATIVE
    default_getvaluefunc = None
    default_setlabelfunc = None
    default_gethintfunc = None
    default_endsliderfunc = None
    default_onsetvaluefunc = None
    default_width = 10
    default_height = 10

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.SetSliderLabel = attributes.get('setlabelfunc', self.default_setlabelfunc)
        self.GetSliderHint = attributes.get('gethintfunc', self.GetSliderHint)
        self.GetSliderValue = attributes.get('getvaluefunc', self.default_getvaluefunc)
        self.EndSetSliderValue = attributes.get('endsliderfunc', self.default_endsliderfunc)
        self.OnSetValue = attributes.get('onsetvaluefunc', self.default_onsetvaluefunc)
        self.value = None
        self.valueproportion = None
        self.increments = []
        self.label = None
        self.top = 0
        self.dragging = False
        self.valueHint = uicls.SliderHint(parent=uicore.layer.hint, align=uiconst.TOPLEFT)
        uicls.Sprite(parent=self, padding=(0, 0, 0, 0), name='handle', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Slider/handle.png', align=uiconst.TOALL)
        uicls.Frame(parent=self.parent, color=(0.5, 0.5, 0.5, 0.3))

    def Startup(self, sliderID, minValue, maxValue, config = None, displayName = None, increments = None, usePrefs = 0, startVal = None):
        self.sliderID = sliderID
        self.minValue = minValue
        self.maxValue = maxValue
        self.config = config
        self.usePrefs = usePrefs
        for each in self.parent.children:
            if each.name == 'label':
                self.label = each

        self.displayName = displayName
        if increments:
            self.SetIncrements(increments)
        if config:
            if len(config) == 3:
                cfgName, prefsType, defaultValue = config
                if prefsType:
                    rec = util.GetAttrs(settings, *prefsType)
                    if rec is not None:
                        value = rec.Get(cfgName, defaultValue)
                    else:
                        value = defaultValue
                else:
                    value = defaultValue
                self.name = config[0]
            else:
                if usePrefs:
                    value = prefs.GetValue(config, (maxValue - minValue) * 0.5)
                else:
                    value = settings.user.ui.Get(config, (maxValue - minValue) * 0.5)
                if value is None:
                    value = 0.0
                else:
                    value = max(minValue, min(maxValue, value))
                self.name = config
            nval = (float(value) - self.minValue) / (self.maxValue - self.minValue)
            self.SlideTo(nval, 1)
            self.SetValue(nval)
        elif startVal is not None:
            self.SlideTo(startVal, 1)
            self.SetValue(startVal)
        else:
            self.state = uiconst.UI_NORMAL

    def SetIncrements(self, increments, draw = 1):
        if len(increments) < 3:
            return
        self.increments = [[], []]
        for inc in increments:
            self.increments[0].append(inc)
            self.increments[1].append((inc - self.minValue) / float(self.maxValue - self.minValue))

        if draw:
            self.DrawIncrement()

    def DrawIncrement(self):
        if self.increments:
            l, t, w, h = self.parent.GetAbsolute()
            maxX = w - self.width
            uicls.Line(parent=self.parent, align=uiconst.RELATIVE, height=2, width=maxX - 1, left=self.width / 2, top=self.height + 2)
            i = 0
            for each in self.increments[1]:
                height = 5
                if i in (0, len(self.increments[1]) - 1):
                    height = 10
                uicls.Line(parent=self.parent, align=uiconst.RELATIVE, height=height, width=1, left=int(each * maxX) + self.width / 2 - 1, top=self.height - 6)
                i += 1

    def SetLabel(self, label, leftright = 'left'):
        uicls.EveLabelSmall(text='<%s>%s' % (leftright, label), parent=self.parent, left=4, top=-4, width=self.parent.width, state=uiconst.UI_DISABLED)

    def GetValue(self):
        return self.value

    def MorphTo(self, value, time = 150.0):
        if getattr(self, 'morphTo', None) is not None:
            self.pendingMorph = (value, time)
            return
        self.morphTo = value
        startPos = self.value / (self.maxValue - self.minValue)
        endPos = value / (self.maxValue - self.minValue)
        start, ndt = blue.os.GetWallclockTime(), 0.0
        while ndt != 1.0:
            ndt = min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / time, 1.0)
            newVal = mathUtil.Lerp(startPos, endPos, ndt)
            self.SlideTo(newVal)
            self.SetValue(newVal)
            blue.pyos.synchro.Yield()

        self.morphTo = None
        if getattr(self, 'pendingMorph', None):
            value, time = self.pendingMorph
            self.MorphTo(value, time)
        self.pendingMorph = None

    def SlideTo(self, value, update = 1):
        if update:
            uiutil.Update(self, 'Slider::SlideTo')
        l, t, w, h = self.parent.GetAbsolute()
        maxX = w - self.width
        left = max(0, int(maxX * value))
        if self.increments:
            steps = [ int(incproportion * maxX) for incproportion in self.increments[1] ]
            left = self.FindClosest(left, steps)
        self.left = int(left)
        self.state = uiconst.UI_NORMAL

    def SetValue(self, value):
        if self.increments:
            value = self.FindClosest(self.RoundValue(value), self.increments[1])
        value = max(0.0, min(1.0, value))
        nval = self.minValue + (-self.minValue + self.maxValue) * value
        self.value = nval
        self.valueproportion = value
        if self.GetSliderValue:
            self.GetSliderValue(self.sliderID, self.GetValue())
        self.UpdateLabel()
        if self.OnSetValue:
            self.OnSetValue(self)

    def RoundValue(self, value):
        return float('%.2f' % value)

    def FindClosest(self, check, values):
        mindiff = self.maxValue - self.minValue
        found = self.maxValue - self.minValue
        for value in values:
            diff = abs(value - check)
            if diff < mindiff:
                mindiff = diff
                found = value

        return found

    def UpdateLabel(self):
        if self.label:
            if self.SetSliderLabel:
                self.SetSliderLabel(self.label, self.sliderID, self.displayName, self.GetValue())
            elif self.displayName:
                self.label.text = self.displayName
            else:
                self.label.text = localizationUtil.FormatNumeric(self.GetValue(), decimalPlaces=2)

    def OnMouseDown(self, *blah):
        offset = uicore.uilib.x - self.absoluteLeft
        self.offset = offset
        self.dragging = 1

    def OnMouseUp(self, *blah):
        uicore.uilib.UnclipCursor()
        self.dragging = 0
        if self.config:
            if len(self.config) == 3:
                cfgName, prefsType, defaultValue = self.config
                if prefsType:
                    rec = util.GetAttrs(settings, *prefsType)
                    if rec is not None:
                        value = rec.Set(cfgName, self.value)
            if self.usePrefs:
                prefs.SetValue(self.config, self.value)
            else:
                settings.user.ui.Set(self.config, self.value)
        if self.EndSetSliderValue:
            self.EndSetSliderValue(self)

    def OnMouseMove(self, *blah):
        if self.dragging:
            screenLoc = uicore.uilib.x - self.offset
            localX = max(0, screenLoc - self.parent.absoluteLeft)
            maxX = self.parent.absoluteRight - self.parent.absoluteLeft - self.width
            localX = min(maxX, localX)
            if self.increments:
                steps = [ int(incproportion * maxX) for incproportion in self.increments[1] ]
                localX = self.FindClosest(localX, steps)
            if self.left == localX:
                return
            self.left = localX
            self.SetValue(localX / float(maxX))
            self.ShowValueHint()

    def OnMouseEnter(self, *blah):
        self.ShowValueHint()

    def OnMouseExit(self, *blah):
        self.valueHint.LoadHint(None)

    def ShowValueHint(self):
        self.valueHint.LoadHint(self.GetSliderHint(self.sliderID, self.displayName, self.GetValue()))
        self.valueHint.width = self.valueHint.sr.textobj.textwidth + self.valueHint.sr.textobj.left * 2
        self.valueHint.left = self.absoluteLeft + self.width / 2 - self.valueHint.width / 2
        self.valueHint.top = self.absoluteTop - self.valueHint.height - self.valueHint.pointer.height + 4

    def GetSliderHint(self, idname, dname, value):
        return localizationUtil.FormatNumeric(value, decimalPlaces=2)


class SliderHint(uicls.Hint):
    __guid__ = 'uicls.SliderHint'
    default_name = 'sliderhint'

    def Prepare_(self):
        uicls.Hint.Prepare_(self)
        self.pointer = uicls.Sprite(parent=self, name='downwardPointer', pos=(0, -8, 18, 12), align=uiconst.CENTERBOTTOM, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Hint/pointerToBottomCenter.png', color=(1, 1, 1, 1))
        self.frame.SetRGBA(0, 0, 0, 1)