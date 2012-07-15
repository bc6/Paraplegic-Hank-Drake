#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/minimizedwindowbutton.py
import blue
import uthread
import types
import log
import sys
import uicls
import uiutil
import uiconst
import weakref

class WindowMinimizeButtonCore(uicls.Container):
    __guid__ = 'uicls.WindowMinimizeButtonCore'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.Prepare_()
        wnd = attributes.wnd
        self.wnd_wr = weakref.ref(wnd)
        self.SetLabel(wnd.GetCaption())
        self.SetBlink(0)
        self.SetHighlight(0)
        self.hint = wnd.headerIconHint

    def Prepare_(self):
        uicls.Frame(parent=self)
        self.sr.label = uicls.Label(parent=self, state=uiconst.UI_DISABLED, fontsize=10, letterspace=1, pos=(8, 4, 0, 0), uppercase=1, idx=2)
        self.sr.icon = uicls.Icon(parent=self, state=uiconst.UI_DISABLED, icon='ui_1_16_102')
        self.sr.hilite = uicls.Fill(parent=self)
        self.sr.blink = uicls.Fill(parent=self)

    def OnClick(self, *args):
        uicore.Message('ListEntryClick')
        if self.wnd_wr and self.wnd_wr():
            wnd = self.wnd_wr()
        else:
            wnd = None
        if not self.destroyed:
            self.Close()
        if wnd:
            wnd.Maximize()

    def GetMenu(self, *args):
        if self.wnd_wr and self.wnd_wr():
            wnd = self.wnd_wr()
        else:
            wnd = None
        if not wnd.destroyed:
            return wnd.GetMenu()
        return []

    def OnMouseEnter(self, *args):
        self.SetHighlight(1)

    def OnMouseExit(self, *args):
        self.SetHighlight(0)

    def SetLabel(self, labeltext):
        if self.sr.label:
            labeltext = labeltext.strip()
            self.sr.label.text = uiutil.TruncateStringTo(labeltext, 32, '...')
            self.width = self.sr.label.width + self.sr.label.left + 8
            if self.wnd_wr and self.wnd_wr():
                wnd = self.wnd_wr()
            else:
                wnd = None
            if wnd:
                wnd.ArrangeMinimizedButtons()

    def SetBlink(self, blink = True):
        if self.sr.blink:
            if blink:
                uicore.effect.BlinkSpriteRGB(self.sr.blink, 0.5, 0.5, 0.5, 750, 10000, passColor=1)
                self.sr.blink.state = uiconst.UI_DISABLED
            else:
                self.sr.blink.state = uiconst.UI_HIDDEN
                uicore.effect.StopBlink(self.sr.blink)

    def SetHighlight(self, hilite = 1):
        if self.sr.hilite:
            if hilite:
                self.sr.hilite.state = uiconst.UI_DISABLED
            else:
                self.sr.hilite.state = uiconst.UI_HIDDEN