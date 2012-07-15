#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/control/eveSpinWheelPicker.py
import uicls
import uiconst
import uiutil
import trinity
import math
import uthread
import blue
import base

class SpinWheelPicker(uicls.Container):
    __guid__ = 'uicls.SpinWheelPicker'
    default_align = uiconst.CENTER
    default_left = 0
    default_top = 0
    default_width = 256
    default_height = 256
    default_name = 'SpinWheel'
    default_state = uiconst.UI_NORMAL
    default_pickRadius = 66
    TEXTURESIZE = 162
    MARKERTFSIZE = 98
    SPINRATIO = 1.0

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self._spinning = False
        self._lastAngle = 0.0
        self._tickGap = 0.0
        self._options = None
        self._value = None
        self._lastRotationDelta = None
        self._didSpin = False
        self._wheelbuffer = 0
        self._wheeling = False
        for each in uicore.layer.main.children[:]:
            if each.name == self.default_name:
                each.Close()

        if attributes.parent is None:
            uicore.layer.main.children.append(self)
        transform = uicls.Transform(parent=self, pos=(0,
         0,
         self.TEXTURESIZE,
         self.TEXTURESIZE), align=uiconst.CENTER, state=uiconst.UI_DISABLED, name='mainTransform')
        self.sr.mainTransform = transform
        sprite = uicls.Sprite(parent=transform, align=uiconst.TOALL, texturePath='res:/UI/Texture/spinWheelPicker_main.dds')
        self.sr.mainTransform = transform
        self.sr.marker = uicls.Fill(parent=self, align=uiconst.CENTER, pos=(0, -64, 2, 16), color=(1.0, 1.0, 1.0, 1.0), idx=0)
        options = attributes.Get('options', [(True, None)] + [ (False, i) for i in xrange(60) ])
        activeOptionIndex = attributes.Get('activeOptionIndex', 4)
        self.LoadOptions(options, activeOptionIndex)
        setvalueCallback = attributes.Get('OnSetValue', None)
        if setvalueCallback:
            self.OnSetValue = setvalueCallback

    def LoadOptions(self, options, activeOptionIndex = 0):
        for each in self.sr.mainTransform.children[:]:
            if each.name == 'tick':
                each.Close()

        self._options = options
        step = math.pi * 2 / len(self._options)
        self._tickGap = step
        angle = 0.0
        activeRotation = 0.0
        for i, each in enumerate(self._options):
            isZero, args = each
            markerTransform = uicls.Transform(parent=self.sr.mainTransform, pos=(0,
             0,
             self.MARKERTFSIZE,
             self.MARKERTFSIZE), align=uiconst.CENTER, state=uiconst.UI_DISABLED, name='tick', rotation=angle + math.pi * 0.25, idx=0)
            sprite = uicls.Sprite(parent=markerTransform, align=uiconst.TOPRIGHT, pos=(0, 0, 16, 16), color=(0.0, 0.0, 0.0, 1.0), texturePath='res:/UI/Texture/spinWheelPicker_marker2.dds')
            if i == activeOptionIndex:
                activeRotation = angle
            angle += step
            if isZero:
                sprite.texture.resPath = 'res:/UI/Texture/CharacterCreation/ovalSlider_Filler.dds'
                sprite.SetRGB(1.0, 0.0, 0.0)
                sprite.top = 2
                sprite.left = 2

        if activeRotation:

            def UpdateMarker(_None, newAngle):
                self.sr.mainTransform.SetRotation(newAngle)

            currentAngle = self.sr.mainTransform.GetRotation()
            uicore.effect.MorphUIMassSpringDamper(None, None, activeRotation, newthread=False, frequency=15.0, dampRatio=0.5, callback=UpdateMarker, initVal=currentAngle)
        self.SettleOnTick()

    def SettleOnTick(self):
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_circular_slider_item_selected_play'))
        currentAngle = self.sr.mainTransform.GetRotation()

        def UpdateMarker(_None, newAngle):
            if self.destroyed:
                return
            self.sr.mainTransform.SetRotation(newAngle)

        step = self._tickGap
        angle = 0.0
        value = None
        for isZero, value in self._options:
            if angle - step / 2 < 0.0 and angle - step / 2 + math.pi * 2 <= currentAngle <= angle + step / 2 + math.pi * 2:
                break
            if angle - step / 2 <= currentAngle <= angle + step / 2:
                break
            angle += step

        if abs(angle - currentAngle) > step:
            angle += math.pi * 2
        uicore.effect.MorphUIMassSpringDamper(None, None, angle, frequency=15.0, dampRatio=0.5, callback=UpdateMarker, initVal=currentAngle)
        self.SetValue(value)

    def GetValue(self):
        return self._value

    def SetValue(self, value):
        self._value = value
        self.OnSetValue(self, value)

    def OnSetValue(self, control, value):
        pass

    def RotationTick(self, *args):
        if self._spinning:
            newAngle = self.GetRotationAngleFromCenter()
            delta = self._lastAngle - newAngle
            if delta:
                self._didSpin = True
                if abs(delta) > math.pi:
                    if delta < 0.0:
                        delta += math.pi * 2
                    else:
                        delta -= math.pi * 2
            self.sr.mainTransform.Rotate(delta * self.SPINRATIO)
            self._lastRotationDelta = delta * self.SPINRATIO
            self._lastAngle = newAngle
        else:
            self.sr._rotationTimer = None

    def OnClick(self, *args):
        if self._didSpin:
            return
        mouseAngle = self.GetRotationAngleFromCenter()
        currentAngle = self.sr.mainTransform.GetRotation()
        newAngle = mouseAngle + currentAngle - math.pi * 0.5
        newAngle = self.sr.mainTransform.ClampRotation(newAngle)
        self.sr.mainTransform.SetRotation(newAngle)

        def UpdateMarker(_None, _newAngle):
            self.sr.mainTransform.SetRotation(_newAngle)

        step = self._tickGap
        angle = 0.0
        value = None
        for isZero, value in self._options:
            if angle - step / 2 < 0.0 and angle - step / 2 + math.pi * 2 <= newAngle <= angle + step / 2 + math.pi * 2:
                break
            if angle - step / 2 <= newAngle <= angle + step / 2:
                break
            angle += step

        diff = abs(angle - currentAngle)
        if diff > math.pi:
            if angle > currentAngle:
                angle -= math.pi * 2
            else:
                angle += math.pi * 2
        uicore.effect.MorphUIMassSpringDamper(None, None, angle, frequency=15.0, dampRatio=0.5, callback=UpdateMarker, initVal=currentAngle)
        self.SetValue(value)

    def OnMouseWheel(self, *args):
        if getattr(self, '_wheeling', False):
            self._wheelbuffer += uicore.uilib.dz
        else:
            uthread.new(self.MouseWheelThread, uicore.uilib.dz)

    def MouseWheelThread(self, delta):
        self._wheeling = True
        blue.pyos.synchro.SleepWallclock(100)
        if self._wheelbuffer:
            delta += self._wheelbuffer
            self._wheelbuffer = 0
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_circular_slider_item_selected_play'))
        currentAngle = self.sr.mainTransform.GetRotation()

        def UpdateMarker(_None, newAngle):
            self.sr.mainTransform.SetRotation(newAngle)

        steps = abs(delta / 120)
        if delta > 0:
            newAngle = currentAngle + self._tickGap * steps
        else:
            newAngle = currentAngle - self._tickGap * steps
        if newAngle < 0.0:
            newAngle += math.pi * 2
        elif newAngle > math.pi * 2:
            newAngle -= math.pi * 2
        step = self._tickGap
        angle = 0.0
        value = None
        for isZero, value in self._options:
            if angle - step / 2 < 0.0 and angle - step / 2 + math.pi * 2 <= newAngle <= angle + step / 2 + math.pi * 2:
                break
            if angle - step / 2 <= newAngle <= angle + step / 2:
                break
            angle += step

        diff = abs(angle - currentAngle)
        if diff > math.pi:
            if angle > currentAngle:
                angle -= math.pi * 2
            else:
                angle += math.pi * 2
        uicore.effect.MorphUIMassSpringDamper(None, None, angle, newthread=0, frequency=15.0, dampRatio=0.5, callback=UpdateMarker, initVal=currentAngle)
        self._wheeling = False
        if self._wheelbuffer:
            buff = self._wheelbuffer
            self._wheelbuffer = 0
            return self.MouseWheelThread(buff)
        self.SetValue(value)

    def OnMouseDown(self, button, *args):
        if button == uiconst.MOUSELEFT:
            sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_inventory_item_mouse_over_loop_play'))
            self._lastAngle = self.GetRotationAngleFromCenter()
            self._spinning = True
            self._didSpin = False
            self.sr._rotationTimer = base.AutoTimer(10, self.RotationTick)

    def OnMouseUp(self, button, *args):
        if button == uiconst.MOUSELEFT:
            sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_inventory_item_mouse_over_loop_stop'))
            self._spinning = False
            if self._didSpin:
                uthread.new(self.Throw)

    def Throw(self, *args):
        newAngle = self.GetRotationAngleFromCenter()
        delta = self._lastRotationDelta
        lenOptions = len(self._options)
        if delta:
            distance = delta
            steps = 20
            maxExp = math.exp(steps / 10.0)
            for i in xrange(1, steps + 1):
                iExp = math.exp(i / 10.0)
                _delta = distance - distance * (iExp / maxExp)
                self.sr.mainTransform.Rotate(_delta)
                blue.pyos.synchro.SleepWallclock(10)
                if self.destroyed or self._spinning:
                    return

        self.SettleOnTick()

    def GetRotationAngleFromCenter(self):
        x, y = uicore.uilib.x, uicore.uilib.y
        l, t, w, h = self.GetAbsolute()
        px, py = l + w / 2, t + h / 2
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
        return self.sr.mainTransform.ClampRotation(rot)