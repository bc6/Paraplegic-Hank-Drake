import uiutil
import uiconst
import uicls
import blue
import weakref
import trinity

class WindowMinimizeButton(uicls.WindowMinimizeButtonCore):
    __guid__ = 'uicls.WindowMinimizeButton'
    default_width = 100
    default_height = 18
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.RELATIVE

    def ApplyAttributes(self, attributes):
        uicls.WindowMinimizeButtonCore.ApplyAttributes(self, attributes)
        self.SetIcon(attributes.wnd.headerIconNo, 12)



    def Prepare_(self):
        self.sr.label = uicls.EveLabelSmall(text='', parent=self, left=8, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
        self.sr.hilite = uicls.Fill(parent=self, name='hilite', state=uiconst.UI_HIDDEN, color=(1.0, 1.0, 1.0, 0.25))
        self.sr.blink = uicls.Fill(parent=self, name='hilite', state=uiconst.UI_HIDDEN, color=(1.0, 1.0, 1.0, 0.25))
        uicls.Frame(parent=self, name='dot', texturePath='res:/UI/Texture/Shared/windowButtonDOT.png', cornerSize=6, spriteEffect=trinity.TR2_SFX_DOT)
        uicls.WindowBaseColor(parent=self, transparent=False)
        uicls.Frame(parent=self, name='shadow', texturePath='res:/UI/Texture/Shared/windowShadow.png', cornerSize=9, offset=-4, state=uiconst.UI_DISABLED, color=(0.0, 0.0, 0.0, 0.25), align=uiconst.TOALL)
        self.sr.icon = None



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
        if self.wnd_wr and self.wnd_wr():
            wnd = self.wnd_wr()
        else:
            wnd = None
        if wnd:
            wnd.ArrangeMinimizedButtons()




