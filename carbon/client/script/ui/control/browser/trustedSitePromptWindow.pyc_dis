#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/browser/trustedSitePromptWindow.py
import uiconst
import uicls
import localization

class TrustedSitePromptWindowCore(uicls.Window):
    __guid__ = 'uicls.TrustedSitePromptWindowCore'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        trustUrl = attributes.trustUrl
        inputUrl = attributes.inputUrl
        self.SetCaption(localization.GetByLabel('UI/Browser/AskTrustedSites'))
        self.SetMinSize((400, 300))
        main = self.GetMainArea()
        self.ignoreAlwaysBtnPar = uicls.Container(name='ignoreAlwaysBtnPar', parent=main, align=uiconst.TOBOTTOM, height=22, top=2)
        self.ignoreBtnPar = uicls.Container(name='ignoreBtnPar', parent=main, align=uiconst.TOBOTTOM, height=22, top=2)
        self.trustBtn = uicls.Button(parent=self.ignoreBtnPar, label=localization.GetByLabel('UI/Browser/TrustPrompt/TrustSite'), align=uiconst.TOLEFT, pos=(4, 0, 0, 0), func=self.TrustSite)
        self.trustBtn.hint = localization.GetByLabel('UI/Browser/TrustPrompt/TrustButtonHint')
        self.ignoreBtn = uicls.Button(parent=self.ignoreBtnPar, label=localization.GetByLabel('UI/Browser/TrustPrompt/IgnoreOnce'), align=uiconst.TORIGHT, pos=(4, 0, 0, 0), func=self.IgnoreThisRequest)
        self.ignoreBtn.hint = localization.GetByLabel('UI/Browser/TrustPrompt/IgnoreOnceHint')
        self.ignoreAlwaysBtn = uicls.Button(parent=self.ignoreAlwaysBtnPar, label=localization.GetByLabel('UI/Browser/TrustPrompt/IgnoreAlways'), align=uiconst.TORIGHT, pos=(4, 0, 0, 0), func=self.AlwaysIgnoreRequests)
        self.ignoreAlwaysBtn.hint = localization.GetByLabel('UI/Browser/TrustPrompt/IgnoreAlwaysHint')
        self.sourcePar = uicls.Container(name='sourcePar', parent=main, align=uiconst.TOBOTTOM, height=32)
        self.sourceTxtPar = uicls.Container(name='sourceTxtPar', parent=self.sourcePar, align=uiconst.TOTOP, height=14)
        self.sourceUrlPar = uicls.Container(name='sourceUrlPar', parent=self.sourcePar, align=uiconst.TOTOP, height=16)
        self.sourceTxt = uicls.Label(text=localization.GetByLabel('UI/Browser/TrustPrompt/RequestFrom'), parent=self.sourceTxtPar, state=uiconst.UI_DISABLED, color=(0.5, 0.5, 0.5, 0.7), align=uiconst.TOALL, padLeft=8)
        self.sourceUrl = uicls.Label(text=inputUrl, parent=self.sourceUrlPar, state=uiconst.UI_NORMAL, color=(0.5, 0.5, 0.5, 0.7), align=uiconst.TOALL, padLeft=8)
        self.sourceUrl.hint = inputUrl
        uicls.Line(parent=self.sourcePar, align=uiconst.TOTOP, color=(0.4, 0.4, 0.4, 0.9))
        self.promptPar = uicls.Container(name='promptPar', parent=main, align=uiconst.TOALL, pos=(8, 2, 8, 2))
        trustDescription = localization.GetByLabel('UI/Browser/TrustPrompt/TrustDescription', trustUrl=trustUrl)
        self.promptTxt = uicls.Edit(setvalue=trustDescription, parent=self.promptPar, readonly=1, align=uiconst.TOALL)
        self.trustUrl = trustUrl
        self.inputUrl = inputUrl

    def TrustSite(self, *args):
        sm.GetService('sites').AddTrustedSite(self.trustUrl)
        self.CloseByUser()

    def IgnoreThisRequest(self, *args):
        self.CloseByUser()

    def AlwaysIgnoreRequests(self, *args):
        sm.GetService('sites').AddIgnoredSite(self.inputUrl)
        self.CloseByUser()