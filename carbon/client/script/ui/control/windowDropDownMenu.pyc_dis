#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/windowDropDownMenu.py
import uicls
import uiconst

class WindowDropDownMenuCore(uicls.Container):
    __guid__ = 'uicls.WindowDropDownMenuCore'
    default_height = 10
    default_align = uiconst.TOLEFT
    default_state = uiconst.UI_NORMAL

    def Setup(self, name, GetMenu):
        self.name = name
        self.expandOnLeft = 1
        self.PrepareLayout()
        self.GetMenu = GetMenu

    def PrepareLayout(self):
        uicls.Line(parent=self, align=uiconst.TORIGHT)
        self.label = uicls.Label(text=self.name, parent=self, align=uiconst.CENTER, fontsize=9, letterspace=1, top=1, state=uiconst.UI_DISABLED, uppercase=1)
        self.hilite = uicls.Fill(parent=self, state=uiconst.UI_HIDDEN, padding=1)
        self.width = self.label.width + 10
        self.cursor = uiconst.UICURSOR_SELECT

    def OnMouseEnter(self):
        self.hilite.state = uiconst.UI_DISABLED

    def OnMouseExit(self):
        self.hilite.state = uiconst.UI_HIDDEN

    def GetMenuPosition(self, *args):
        return (self.absoluteLeft, self.absoluteBottom + 2)