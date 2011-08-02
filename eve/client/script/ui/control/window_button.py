import uiutil
import uiconst
import uicls
import blue
import weakref
import trinity

class WindowButton(uicls.Container):
    __guid__ = 'uicls.WindowButton'
    default_width = 100
    default_height = 18
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.RELATIVE

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        wnd = attributes.wnd
        self.sr.label = uicls.Label(text='', parent=self, fontsize=10, letterspace=1, left=8, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, uppercase=1)
        self.sr.hilite = uicls.Fill(parent=self, name='hilite', state=uiconst.UI_HIDDEN, color=(1.0, 1.0, 1.0, 0.25))
        self.sr.blink = uicls.Fill(parent=self, name='hilite', state=uiconst.UI_HIDDEN, color=(1.0, 1.0, 1.0, 0.25))
        uicls.Frame(parent=self, name='dot', texturePath='res:/UI/Texture/Shared/windowButtonDOT.png', cornerSize=6, spriteEffect=trinity.TR2_SFX_DOT)
        uicls.WindowBaseColor(parent=self, transparent=False)
        uicls.Frame(parent=self, name='shadow', texturePath='res:/UI/Texture/Shared/windowShadow.png', cornerSize=9, offset=-4, state=uiconst.UI_DISABLED, color=(0.0, 0.0, 0.0, 0.25), align=uiconst.TOALL)
        self.sr.icon = None
        self.wnd_wr = weakref.ref(wnd)
        self.SetIcon(wnd.headerIconNo, 12)
        self.SetLabel(wnd.GetCaption())
        self.SetBlink(0)
        self.sr.hint = wnd.headerIconHint



    def OnClick(self, *args):
        if self.wnd_wr and self.wnd_wr():
            wnd = self.wnd_wr()
        else:
            wnd = None
        sm.GetService('window').NotMinimized(self)
        eve.Message('ListEntryClick')
        if not self.destroyed:
            self.Close()
        if wnd:
            wnd.Maximize(expandIfCollapsed=0)



    def GetMenu(self, *args):
        if self.wnd_wr and self.wnd_wr():
            wnd = self.wnd_wr()
        else:
            wnd = None
        if wnd is not None and not wnd.destroyed:
            return uicls.Window.GetMenu(wnd)
        return []



    def OnMouseEnter(self, *args):
        self.sr.hilite.state = uiconst.UI_DISABLED



    def OnMouseExit(self, *args):
        self.sr.hilite.state = uiconst.UI_HIDDEN



    def SetLabel(self, labeltext):
        labeltext = labeltext.strip()
        if len(labeltext) > 32:
            labeltext = '%s...' % labeltext[:32]
        self.sr.label.text = labeltext
        self.width = self.sr.label.width + self.sr.label.left + 8



    def SetIcon(self, iconNo, shiftLabel = 16, hint = None):
        if self.sr.icon:
            self.sr.icon.Close()
        if iconNo is None:
            self.sr.label.left = 8
        else:
            self.sr.icon = uicls.Icon(icon=iconNo, parent=self, pos=(2, 0, 16, 16), align=uiconst.RELATIVE, idx=0, state=uiconst.UI_DISABLED)
            self.sr.label.left = 8 + shiftLabel
        self.sr.hint = hint
        self.width = self.sr.label.width + self.sr.label.left + 8
        sm.GetService('window').RefreshWindowBtns()



    def SetBlink(self, blink = True):
        if blink:
            uicore.effect.BlinkSpriteRGB(self.sr.blink, 0.5, 0.5, 0.5, 750, 10000, passColor=1)
            self.sr.blink.state = uiconst.UI_DISABLED
        else:
            self.sr.blink.state = uiconst.UI_HIDDEN
            uicore.effect.StopBlink(self.sr.blink)




