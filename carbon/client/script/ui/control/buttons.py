import fontConst
import uicls
import uiconst
import uiutil
import uthread
import trinity
import audioConst

class ButtonCore(uicls.Container):
    __guid__ = 'uicls.ButtonCore'
    default_name = 'button'
    default_align = uiconst.RELATIVE
    default_label = ''
    default_width = 100
    default_height = 20
    default_func = None
    default_args = None
    default_mouseupfunc = None
    default_mousedownfunc = None
    default_fixedwidth = None
    default_state = uiconst.UI_NORMAL
    default_fontsize = fontConst.DEFAULT_FONTSIZE
    default_fontStyle = None
    default_fontFamily = None
    default_fontPath = None

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.isTabStop = 1
        self.resetTop = None
        self.blinking = 0
        self.disabled = False
        for each in ('btn_modalresult', 'btn_default', 'btn_cancel'):
            if each in attributes:
                attr = attributes.get(each, None)
                setattr(self, each, attr)

        self.Prepare_()
        self.fixedwidth = attributes.get('fixedwidth', self.default_fixedwidth)
        self.func = attributes.get('func', self.default_func)
        self.args = attributes.get('args', self.default_args)
        self.mouseupfunc = attributes.get('mouseupfunc', self.default_mouseupfunc)
        self.mousedownfunc = attributes.get('mousedownfunc', self.default_mousedownfunc)
        self.fontStyle = attributes.get('fontStyle', self.default_fontStyle)
        self.fontFamily = attributes.get('fontFamily', self.default_fontFamily)
        self.fontPath = attributes.get('fontPath', self.default_fontPath)
        self.fontsize = attributes.get('fontsize', self.default_fontsize)
        if self.sr.label:
            if attributes.fontFamily:
                self.sr.label.fontFamily = attributes.fontFamily
            if attributes.fontsize:
                self.sr.label.fontsize = attributes.fontsize
            label = attributes.get('label', self.default_label)
            if hasattr(self, 'SetLabel_'):
                self.SetLabel_(label)



    def Prepare_(self):
        self.sr.label = uicls.Label(parent=self, state=uiconst.UI_DISABLED, align=uiconst.CENTER, bold=1, uppercase=1, idx=0, fontFamily=self.fontFamily, fontStyle=self.fontStyle, fontPath=self.fontPath, fontsize=self.fontsize)
        self.sr.activeframe = uicls.Frame(parent=self, name='activeframe', state=uiconst.UI_HIDDEN, color=(1.0, 1.0, 1.0, 0.5), frameConst=uiconst.FRAME_BORDER1_SHADOW_CORNER4)
        self.sr.hilite = uicls.Fill(parent=self, name='hilite', state=uiconst.UI_HIDDEN, color=(1.0, 1.0, 1.0, 0.25), padding=(2, 2, 2, 2))
        uicls.Frame(parent=self, name='background', state=uiconst.UI_DISABLED, frameConst=uiconst.FRAME_BORDER1_SHADOW_CORNER4, color=(1.0, 1.0, 1.0, 0.5))



    def Enable(self):
        self.opacity = 1.0
        self.state = uiconst.UI_NORMAL
        self.disabled = False



    def Disable(self):
        self.opacity = 0.5
        self.Hilite_(False)
        self.disabled = True



    def SetLabel(self, label):
        self.SetLabel_(label)



    def SetLabel_(self, label):
        if not self or self.destroyed:
            return 
        text = self.text = label
        text = text.replace('<center>', '').replace('</center>', '')
        self.sr.label.text = text
        self.Update_Size_()



    def Update_Size_(self):
        self.width = min(256, self.fixedwidth or max(48, self.sr.label.width + 24))
        lt = max(2, self.sr.label.textheight / 12) - 2
        self.sr.label.top = lt
        self.height = min(32, self.sr.label.textheight + 2)



    def Confirm(self, *args):
        if uiutil.IsVisible(self):
            uthread.new(self.OnClick, self)



    def OnSetFocus(self, *args):
        if self and not self.destroyed and self.parent and self.parent.name == 'inlines':
            browser = uiutil.GetBrowser(self)
            if browser:
                browser.ShowNodeIdx(self.parent.parent.sr.node.idx)
        if self and not self.destroyed and self.sr and self.sr.activeframe:
            self.sr.activeframe.state = uiconst.UI_DISABLED
        btns = self.GetDefaultBtnsInSameWnd()
        if btns:
            self.SetWndDefaultFrameState(btns, 0)



    def GetDefaultBtnsInSameWnd(self, *args):
        wndAbove = uiutil.GetWindowAbove(self) or uicore.desktop
        btns = uiutil.FindChildByClass(wndAbove, (uicls.ButtonCore,), ['trinity.Tr2Sprite2dContainer'], withAttributes=[('btn_default', 1)])
        return btns



    def SetWndDefaultFrameState(self, btns, on = 1):
        for btn in btns:
            if btn == self:
                continue
            frame = uiutil.GetAttrs(btn, 'sr', 'defaultActiveFrame')
            if frame:
                frame.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][(on == 1)]




    def OnKillFocus(self, *etc):
        if self and not self.destroyed and self.sr and self.sr.activeframe:
            self.sr.activeframe.state = uiconst.UI_HIDDEN
        btns = self.GetDefaultBtnsInSameWnd()
        if btns:
            self.SetWndDefaultFrameState(btns, 1)



    def OnMouseDown(self, *args):
        if self.disabled:
            return 
        if not self.resetTop:
            self.resetTop = True
            self._ShiftContent(1)
        if self.mousedownfunc:
            if type(self.args) == tuple:
                self.mousedownfunc(*self.args)
            else:
                self.mousedownfunc(self.args or self)



    def OnMouseUp(self, *args):
        if self.resetTop:
            self.resetTop = False
            self._ShiftContent(-1)
        if self.mouseupfunc:
            if type(self.args) == tuple:
                self.mouseupfunc(*self.args)
            else:
                self.mouseupfunc(self.args or self)



    def OnMouseExit(self, *args):
        if not self.blinking:
            self.Hilite_(False)
        if self.resetTop:
            self.resetTop = False
            self._ShiftContent(-1)



    def OnMouseEnter(self, *args):
        if self.destroyed or not getattr(self, 'func', None):
            return 
        if self.func or self.mousedownfunc or getattr(self, 'action', None):
            if not self.blinking:
                self.Hilite_(True)



    def OnClick(self, *blah):
        if not self or self.destroyed:
            return 
        if self.disabled:
            return 
        if not self.func:
            return 
        if audioConst.BTNCLICK_DEFAULT:
            uicore.Message(audioConst.BTNCLICK_DEFAULT)
        if type(self.args) == tuple:
            self.func(*self.args)
        else:
            self.func(self.args or self)
        if not self.destroyed and self.sr.hilite and uicore.uilib.mouseOver != self and not self.blinking:
            self.Hilite_(False)



    def Hilite_(self, on):
        if self.disabled:
            return 
        if self.sr.hilite:
            if on:
                self.sr.hilite.state = uiconst.UI_DISABLED
            else:
                self.sr.hilite.state = uiconst.UI_HIDDEN



    def Blink(self, on_off = 1, blinks = 1000, time = 800):
        if self.sr.hilite:
            if on_off:
                (r, g, b,) = self.sr.hilite.GetRGB()
                r = min(1.0, r * 1.25)
                g = min(1.0, g * 1.25)
                b = min(1.0, b * 1.25)
                uicore.effect.BlinkSpriteRGB(self.sr.hilite, r, g, b, time, blinks)
                self.sr.hilite.state = uiconst.UI_DISABLED
            else:
                self.sr.hilite.state = uiconst.UI_HIDDEN
                uicore.effect.StopBlink(self.sr.hilite)
        self.blinking = on_off



    def _ShiftContent(self, shift):
        for each in self.children:
            if each.align in uiconst.AFFECTEDBYPUSHALIGNMENTS:
                each.padTop += shift
                each.padBottom -= shift
            else:
                each.top += shift





