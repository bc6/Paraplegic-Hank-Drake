import uiconst
import uicls
import uiutil
import mathUtil
import math
import base
import uthread
SMALLSLIDER = 1
TEXTURESIZE = 164
SETTINGS = {SMALLSLIDER: {'name': 'small',
               'radius': 65,
               'textureWidth': 56,
               'textureHeight': 136,
               'rotationRangeLeft': (5.0471258177, (math.pi * 2 - 5.0471258177) * 2),
               'rotationRangeRight': (5.0471258177 - math.pi, (math.pi * 2 - 5.0471258177) * 2),
               'centerOffsetLeft': (71, 136 / 2),
               'centerOffsetRight': (-15, 136 / 2),
               'comboSize': (142, 136)}}

class CharCreationSingleSlider(uicls.Container):
    __guid__ = 'uicls.CharCreationSingleSlider'
    default_name = 'CharCreationSingleSlider'
    default_align = uiconst.CENTER
    default_state = uiconst.UI_PICKCHILDREN
    default_pickRadius = 75

    def ApplyAttributes(self, attributes):
        for each in uicore.layer.main.children:
            if each.name == self.default_name:
                each.Close()

        uicls.Container.ApplyAttributes(self, attributes)
        if attributes.parent is None:
            uicore.layer.main.children.append(self)
        self.SetSize(TEXTURESIZE, TEXTURESIZE)
        settings = {'radius': 72,
         'textureWidth': 164,
         'textureHeight': 164,
         'texturePath': 'res:/UI/Texture/CharacterCreation/ovalSlider_1.dds',
         'rotationRange': (4.97, math.pi * 2 - 0.53),
         'centerOffset': (82, 82)}
        self.sr.slider = uicls.CharCreationOvalSlider(parent=self, align=uiconst.CENTERLEFT, sliderSetting=settings, OnSetValue=attributes.get('OnSetValue', None), setValue=attributes.get('setValue', 0.0), invertSlider=attributes.get('invertSlider', False), modifierName=attributes.modifierName, increments=attributes.get('incrementsSlider', None))
        if attributes.label:
            uicls.CCLabel(parent=self.sr.slider, fontsize=13, align=uiconst.BOTTOMRIGHT, text=attributes.label, letterspace=2, top=-20, uppercase=True)




class CharCreationDoubleSlider(uicls.Container):
    __guid__ = 'uicls.CharCreationDoubleSlider'
    default_name = 'CharCreationDoubleSlider'
    default_align = uiconst.CENTER
    default_state = uiconst.UI_PICKCHILDREN
    default_pickRadius = 75

    def ApplyAttributes(self, attributes):
        for each in uicore.layer.main.children:
            if each.name == self.default_name:
                each.Close()

        uicls.Container.ApplyAttributes(self, attributes)
        if attributes.parent is None:
            uicore.layer.main.children.append(self)
        self.SetSize(TEXTURESIZE, TEXTURESIZE)
        settings1 = {'radius': 72,
         'textureWidth': 82,
         'textureHeight': 164,
         'texturePath': 'res:/UI/Texture/CharacterCreation/ovalSlider_2_1.dds',
         'rotationRange': (4.97, math.pi - 0.53),
         'centerOffset': (82, 82)}
        self.sr.slider1 = uicls.CharCreationOvalSlider(parent=self, align=uiconst.CENTERLEFT, sliderSetting=settings1, OnSetValue=attributes.get('OnSetValue1', None), setValue=attributes.get('setValue1', 0.0), invertSlider=attributes.get('invertSlider1', False), modifierName=attributes.modifierName1, increments=attributes.get('incrementsSlider1', None))
        if attributes.label1:
            uicls.CCLabel(parent=self.sr.slider1, fontsize=12, align=uiconst.BOTTOMRIGHT, text=attributes.label1, letterspace=2, top=-20, uppercase=True, left=13)
        settings2 = {'radius': 72,
         'textureWidth': 82,
         'textureHeight': 164,
         'texturePath': 'res:/UI/Texture/CharacterCreation/ovalSlider_2_2.dds',
         'rotationRange': (math.pi * 0.5 + 0.27, math.pi - 0.53),
         'centerOffset': (0, 82)}
        self.sr.slider2 = uicls.CharCreationOvalSlider(parent=self, align=uiconst.CENTERRIGHT, sliderSetting=settings2, OnSetValue=attributes.get('OnSetValue2', None), setValue=attributes.get('setValue2', 0.0), invertSlider=attributes.get('invertSlider2', True), modifierName=attributes.modifierName2, increments=attributes.get('incrementsSlider2', None))
        if attributes.label2:
            uicls.CCLabel(parent=self.sr.slider2, fontsize=12, align=uiconst.BOTTOMLEFT, text=attributes.label2, letterspace=2, top=-20, uppercase=True, left=13)




class CharCreationTripleSlider(uicls.Container):
    __guid__ = 'uicls.CharCreationTripleSlider'
    default_name = 'CharCreationTripleSlider'
    default_align = uiconst.CENTER
    default_state = uiconst.UI_PICKCHILDREN
    default_pickRadius = 75

    def ApplyAttributes(self, attributes):
        for each in uicore.layer.main.children:
            if each.name == self.default_name:
                each.Close()

        uicls.Container.ApplyAttributes(self, attributes)
        if attributes.parent is None:
            uicore.layer.main.children.append(self)
        self.SetSize(TEXTURESIZE, TEXTURESIZE)
        settings1 = {'radius': 72,
         'textureWidth': 82,
         'textureHeight': 117,
         'texturePath': 'res:/UI/Texture/CharacterCreation/ovalSlider_3_1.dds',
         'rotationRange': (4.975, math.pi * 0.502),
         'centerOffset': (82, 35)}
        self.sr.slider1 = uicls.CharCreationOvalSlider(parent=self, align=uiconst.BOTTOMLEFT, sliderSetting=settings1, OnSetValue=attributes.get('OnSetValue1', None), setValue=attributes.get('setValue1', 0.0), invertSlider=attributes.get('invertSlider1', False), modifierName=attributes.modifierName1, increments=attributes.get('incrementsSlider1', None))
        if attributes.label1:
            uicls.CCLabel(parent=self.sr.slider1, fontsize=12, align=uiconst.BOTTOMRIGHT, text=attributes.label1, letterspace=2, top=-10, uppercase=True, left=12)
        settings2 = {'radius': 72,
         'textureWidth': 82,
         'textureHeight': 118,
         'texturePath': 'res:/UI/Texture/CharacterCreation/ovalSlider_3_2.dds',
         'rotationRange': (2.88, math.pi * 0.502),
         'centerOffset': (0, 36)}
        self.sr.slider2 = uicls.CharCreationOvalSlider(parent=self, align=uiconst.BOTTOMRIGHT, sliderSetting=settings2, OnSetValue=attributes.get('OnSetValue2', None), setValue=attributes.get('setValue2', 0.0), invertSlider=attributes.get('invertSlider2', True), modifierName=attributes.modifierName2, increments=attributes.get('incrementsSlider2', None))
        if attributes.label2:
            uicls.CCLabel(parent=self.sr.slider2, fontsize=12, align=uiconst.BOTTOMLEFT, text=attributes.label2, letterspace=2, top=-10, uppercase=True, left=12)
        settings3 = {'radius': 72,
         'textureWidth': 164,
         'textureHeight': 48,
         'texturePath': 'res:/UI/Texture/CharacterCreation/ovalSlider_3_3.dds',
         'rotationRange': (0.78, math.pi * 0.502),
         'centerOffset': (82, 82)}
        self.sr.slider3 = uicls.CharCreationOvalSlider(parent=self, align=uiconst.TOPLEFT, sliderSetting=settings3, OnSetValue=attributes.get('OnSetValue3', None), setValue=attributes.get('setValue3', 0.0), invertSlider=attributes.get('invertSlider3', False), modifierName=attributes.modifierName3, increments=attributes.get('incrementsSlider3', None))
        if attributes.label3:
            uicls.CCLabel(parent=self.sr.slider3, fontsize=12, align=uiconst.CENTERTOP, text=attributes.label3, letterspace=2, top=-20, uppercase=True)




class CharCreationOvalSlider(uicls.Container):
    __guid__ = 'uicls.CharCreationOvalSlider'
    default_name = 'CharCreationOvalSlider'
    default_align = uiconst.CENTER
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self._invertedValue = False
        self._lastCallbackValue = None
        self.incrementStopToValue = {}
        settings = attributes.sliderSetting
        textureRadius = settings['radius']
        textureWidth = settings['textureWidth']
        textureHeight = settings['textureHeight']
        texturePath = settings['texturePath']
        centerOffset = settings['centerOffset']
        rotationRange = settings['rotationRange']
        texturePath = settings['texturePath']
        self.increments = attributes.increments
        if self.increments is None:
            self.increments = None
        else:
            self.increments.sort()
        self.textureRadius = textureRadius
        self.modifierName = attributes.modifierName
        self.SetSize(textureWidth, textureHeight)
        self.SetRotationCenterOffset(*centerOffset)
        self.SetRotationRange(*rotationRange)
        if attributes.get('invertSlider', False):
            self.InvertSlider()
        self.sr.marker = uicls.Sprite(parent=self, align=uiconst.TOPLEFT, pos=(0, 0, 16, 16), texturePath='res:/UI/Texture/CharacterCreation/OvalSliderHandle.dds', ignoreSize=True)
        self.sr.marker.OnMouseDown = self.OnMarkerMouseDown
        self.sr.marker.OnMouseEnter = self.OnMarkerMouseEnter
        self.sr.marker.OnMouseExit = self.OnMarkerMouseExit
        self.sr.ghostMarker = uicls.Sprite(parent=self, align=uiconst.TOPLEFT, pos=(0, 0, 16, 16), texturePath='res:/UI/Texture/CharacterCreation/OvalSliderHandle.dds', ignoreSize=True, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.5))
        bg = uicls.Sprite(parent=self, align=uiconst.TOPLEFT, texturePath=texturePath, ignoreSize=True, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 1.0), pos=(0,
         0,
         textureWidth,
         textureHeight))
        self.DrawIncrements()
        self.DrawFill()
        self.sr.fill = uicls.Container(parent=self, align=uiconst.BOTTOMLEFT, clipChildren=True, pos=(0,
         0,
         textureWidth,
         textureHeight))
        self.SetValue(attributes.get('setValue', 0.0))
        setvalueCallback = attributes.get('OnSetValue', None)
        if setvalueCallback:
            self.OnSetValue = setvalueCallback



    def OnMarkerMouseDown(self, *args):
        self.OnMouseDown()



    def OnMarkerMouseEnter(self, *args):
        self.sr.marker.texture.resPath = 'res:/UI/Texture/CharacterCreation/OvalSliderHandle_MO.dds'



    def OnMarkerMouseExit(self, *args):
        self.sr.marker.texture.resPath = 'res:/UI/Texture/CharacterCreation/OvalSliderHandle.dds'



    def OnMouseDown(self, *args):
        if uicore.uilib.leftbtn:
            sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_down_play'))
            self.UpdateMarkerPosition(jump=True)
            self.sr.updateTimer = base.AutoTimer(10, self.UpdateSlider)



    def OnMouseWheel(self, *args):
        delta = uicore.uilib.dz
        if self.increments:
            current = self.GetValue()
            currentIndex = self.increments.index(current)
            newIndex = max(0, min(len(self.increments) - 1, currentIndex + [-1, 1][(delta > 0)]))
            newVal = self.increments[newIndex]
            self.SetValue(newVal)
            self._OnSetValue(self, self._value)
        else:
            self.SetValue(self.GetValue() + [-0.01, 0.01][(delta > 0)])
            self._OnSetValue(self, self._value)



    def UpdateSlider(self, *args):
        if not uicore.uilib.leftbtn:
            self.sr.updateTimer = None
            self.sr.ghostMarker.state = uiconst.UI_HIDDEN
            self.sr.marker.texture.resPath = 'res:/UI/Texture/CharacterCreation/OvalSliderHandle.dds'
            sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_down_play'))
            self._OnSetValue(self, self._value)
            return 
        self.sr.marker.texture.resPath = 'res:/UI/Texture/CharacterCreation/OvalSliderHandle_MD.dds'
        self.UpdateMarkerPosition()



    def SetIncrements(self, increments):
        self.increments = increments
        self.DrawIncrements()



    def DrawIncrements(self):
        for each in self.children[:]:
            if each.name == 'incrementMarker':
                each.Close()

        if not self.increments or len(self.increments) < 2:
            return 
        (fromAngle, toAngle, rotationRange,) = self.rotationRange
        numberic = True
        try:
            for each in self.increments:
                float(each)

        except:
            numberic = False
        self.incrementStopToValue = {}
        if numberic:
            useIncrements = self.increments
        else:
            step = 1.0 / len(self.increments) - 1
            useIncrements = [ i * step for (i, each,) in enumerate(self.increments) ]
        for (i, step,) in enumerate(useIncrements):
            radianAngle = fromAngle + rotationRange * step
            (l, t, w, h,) = self.GetAbsolute()
            (ox, oy,) = self.centerOffset
            radius = self.textureRadius + 1
            cos = math.cos(radianAngle + math.pi)
            sin = math.sin(radianAngle + math.pi)
            left = int(radius * cos) + ox - 4
            top = int(radius * sin) + oy - 4
            self.incrementStopToValue[step] = self.increments[i]
            icon = uicls.Icon(parent=self, pos=(left,
             top,
             8,
             8), icon='ui_3_8_1', color=(1.0,
             1.0,
             1.0,
             step * 0.5), state=uiconst.UI_DISABLED, name='incrementMarker')




    def DrawFill(self):
        step = math.pi / 90.0
        (fromAngle, toAngle, rotationRange,) = self.rotationRange
        (l, t, w, h,) = self.GetAbsolute()
        (ox, oy,) = self.centerOffset
        radius = self.textureRadius
        startAngle = fromAngle + math.pi
        while startAngle < fromAngle + rotationRange + math.pi:
            cos = math.cos(startAngle)
            sin = math.sin(startAngle)
            left = int(radius * cos) + ox - 8
            top = int(radius * sin) + oy - 8
            fillDot = uicls.Sprite(parent=self, align=uiconst.TOPLEFT, pos=(left,
             top,
             16,
             16), texturePath='res:/UI/Texture/CharacterCreation/ovalSlider_Filler.dds', ignoreSize=True, state=uiconst.UI_DISABLED, name='fillDot', color=(0.3, 0.3, 0.3, 1.0))
            startAngle += step




    def UpdateFillByValue(self, value):
        dots = [ each for each in self.children if each.name == 'fillDot' ]
        if self._invertedValue:
            totalVisible = len(dots) * (1.0 - value)
            for (i, dot,) in enumerate(dots):
                if i > totalVisible:
                    dot.state = uiconst.UI_DISABLED
                else:
                    dot.state = uiconst.UI_HIDDEN

        else:
            totalVisible = len(dots) * value
            for (i, dot,) in enumerate(dots):
                if i < totalVisible:
                    dot.state = uiconst.UI_DISABLED
                else:
                    dot.state = uiconst.UI_HIDDEN




    def InvertSlider(self):
        self._invertedValue = True



    def SetRotationCenterOffset(self, x = 0, y = 0):
        self.centerOffset = (x, y)



    def SetRotationRange(self, fromAngle, rotationRange):
        toAngle = self.ClampAngle(fromAngle + rotationRange)
        self.rotationRange = (fromAngle, toAngle, rotationRange)



    def GetRotationAngleFromCenterToMouse(self):
        (x, y,) = (uicore.uilib.x, uicore.uilib.y)
        (l, t, w, h,) = self.GetAbsolute()
        (ox, oy,) = self.centerOffset
        (px, py,) = (l + ox, t + oy)
        tn = (abs(x - px) or 1e-07) / float(abs(y - py) or 1e-07)
        if y < py:
            if x > px:
                rot = math.pi * 0.5 + math.atan(tn)
            else:
                rot = math.pi * 0.5 - math.atan(tn)
        elif x > px:
            rot = math.pi * 1.5 - math.atan(tn)
        else:
            rot = math.pi * 1.5 + math.atan(tn)
        return rot



    def UpdateMarkerPosition(self, jump = False):
        angle = self.GetRotationAngleFromCenterToMouse()
        (fromAngle, toAngle, rotationRange,) = self.rotationRange
        if angle < fromAngle and toAngle < angle:
            fromDiff = abs(angle - fromAngle)
            toDiff = abs(angle - toAngle)
            if fromDiff < toDiff:
                angle = fromAngle
            else:
                angle = toAngle
        if fromAngle + rotationRange > math.pi * 2 and 0.0 < angle <= toAngle:
            angle += math.pi * 2
        portion = (angle - fromAngle) / rotationRange
        if self._invertedValue:
            portion = 1.0 - portion
        nonIncrementedValue = None
        if self.increments:
            nonIncrementedValue = portion
            portion = self.FindIncrementValue(portion)
        self.SetValue(portion, jump, nonIncrementedValue)



    def FindIncrementValue(self, fromValue):
        if fromValue < 0:
            return self.increments[0]
        if fromValue > 1.0:
            return self.increments[-1]
        nextStep = 0.0
        for (i, step,) in enumerate(self.increments):
            if i != len(self.increments) - 1:
                nextStep = self.increments[(i + 1)]
            if step <= fromValue <= nextStep:
                if abs(step - fromValue) < abs(nextStep - fromValue):
                    return step
                return nextStep

        return nextStep



    def ClampAngle(self, angle):
        if angle > math.pi * 2:
            angle -= math.pi * 2
        elif angle < 0:
            angle += math.pi * 2
        return angle



    def GetValue(self):
        return self._value



    def SetValue(self, value, jump = False, nonIncrementedValue = None):
        value = min(1.0, max(0.0, value))
        if nonIncrementedValue is not None:
            nonIncrementedValue = min(1.0, max(0.0, nonIncrementedValue))
        self._value = value
        niSetAngle = None
        (fromAngle, toAngle, rotationRange,) = self.rotationRange
        if self._invertedValue:
            setAngle = self.ClampAngle(fromAngle + rotationRange - rotationRange * value)
            if nonIncrementedValue:
                niSetAngle = self.ClampAngle(fromAngle + rotationRange - rotationRange * nonIncrementedValue)
        else:
            setAngle = self.ClampAngle(fromAngle + rotationRange * value)
            if nonIncrementedValue:
                niSetAngle = self.ClampAngle(fromAngle + rotationRange * nonIncrementedValue)
        self.MoveMarkerByAngle(setAngle, niSetAngle)
        if self._lastCallbackValue != value:
            self._lastCallbackValue = value
            self.UpdateFillByValue(value)



    def _OnSetValue(self, ctrl, stopvalue):
        if stopvalue in self.incrementStopToValue:
            self.OnSetValue(self, self.incrementStopToValue[stopvalue])
        else:
            self.OnSetValue(self, stopvalue)



    def OnSetValue(self, ctrl, value):
        pass



    def MoveMarkerByAngle(self, radianAngle, nonIncrementAngle = None):
        (l, t, w, h,) = self.GetAbsolute()
        (ox, oy,) = self.centerOffset
        radius = self.textureRadius
        cos = math.cos(radianAngle + math.pi)
        sin = math.sin(radianAngle + math.pi)
        left = int(radius * cos) + ox - self.sr.marker.width / 2
        top = int(radius * sin) + oy - self.sr.marker.height / 2
        self.sr.marker.SetPosition(left, top)
        if nonIncrementAngle is not None:
            cos = math.cos(nonIncrementAngle + math.pi)
            sin = math.sin(nonIncrementAngle + math.pi)
            left = int(radius * cos) + ox - self.sr.ghostMarker.width / 2
            top = int(radius * sin) + oy - self.sr.ghostMarker.height / 2
            self.sr.ghostMarker.SetPosition(left, top)
            self.sr.ghostMarker.state = uiconst.UI_DISABLED
        else:
            self.sr.ghostMarker.state = uiconst.UI_HIDDEN




