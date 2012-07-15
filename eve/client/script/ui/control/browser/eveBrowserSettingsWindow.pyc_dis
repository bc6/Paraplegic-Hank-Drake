#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/control/browser/eveBrowserSettingsWindow.py
import uiutil
import uicls
import uiconst
import localization

class BrowserSettingsWindow(uicls.BrowserSettingsWindowCore):
    __guid__ = 'uicls.BrowserSettingsWindow'
    default_windowID = 'BrowserSettingsWindow'

    def ApplyAttributes(self, attributes):
        uicls.BrowserSettingsWindowCore.ApplyAttributes(self, attributes)
        self.SetWndIcon('ui_9_64_4')
        uicls.WndCaptionLabel(text=localization.GetByLabel('UI/Browser/BrowserSettings/BrowserSettingsCaption'), parent=self.sr.topParent)