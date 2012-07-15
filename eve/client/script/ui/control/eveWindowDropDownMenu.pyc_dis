#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/control/eveWindowDropDownMenu.py
import uicls
import uiconst

class WindowDropDownMenu(uicls.WindowDropDownMenuCore):
    __guid__ = 'uicls.WindowDropDownMenu'

    def PrepareLayout(self):
        uicls.Line(parent=self, align=uiconst.TORIGHT)
        self.textLabel = uicls.EveLabelSmall(text=self.name, parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.hilite = uicls.Fill(parent=self, state=uiconst.UI_HIDDEN, padding=1)
        self.width = self.textLabel.width + 10
        self.cursor = uiconst.UICURSOR_SELECT

    def GetTextHeight(self):
        return self.textLabel.textheight