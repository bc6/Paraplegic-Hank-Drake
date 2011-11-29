import uicls
import uiutil
import uiconst

class DropDownMenu(uicls.DropDownMenuCore):
    __guid__ = 'uicls.DropDownMenu'

    def Prepare_Background_(self, *args):
        self.sr.underlay = uicls.WindowUnderlay(parent=self, transparent=False, padding=(0, 0, 0, 0))




class MenuEntryView(uicls.MenuEntryViewCore):
    __guid__ = 'uicls.MenuEntryView'

    def Prepare_Label_(self, *args):
        self.sr.label = uicls.EveLabelSmall(text='', parent=self, left=8, top=1, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)



    def Prepare_Hilite_(self, *args):
        self.sr.hilite = uicls.Fill(parent=self, color=(1.0, 1.0, 1.0, 0.25), padTop=1)



    def Setup(self, entry, size, menu, identifier):
        uicls.MenuEntryViewCore.Setup(self, entry, size, menu, identifier)
        self.sr.label.uppercase = False




