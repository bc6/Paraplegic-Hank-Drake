#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/control/browser/eveTrustedSitePromptWindow.py
import uicls
import localization
import uiconst

class TrustedSitePromptWindow(uicls.TrustedSitePromptWindowCore):
    __guid__ = 'uicls.TrustedSitePromptWindow'

    def ApplyAttributes(self, attributes):
        uicls.TrustedSitePromptWindowCore.ApplyAttributes(self, attributes)
        self.SetWndIcon('ui_9_64_4')
        uicls.WndCaptionLabel(text=localization.GetByLabel('UI/Browser/TrustPrompt/Header'), parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.SetMinSize((430, 300))