import xtriui
import uix
import uiutil
import cPickle
import form
import blue
import service
import urlparse
import listentry
import browserutil
import util
import os
import uiconst
import uicls
import uthread

class WebsiteTrustManagementWindow(uicls.Window):
    __guid__ = 'form.WebsiteTrustManagementWindow'
    __notifyevents__ = ['OnTrustedSitesChange']

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        initialUrl = attributes.initialUrl
        self.SetWndIcon('ui_9_64_4')
        self.SetCaption(mls.UI_SHARED_TRUSTEDSITES)
        uicls.WndCaptionLabel(text=mls.UI_BROWSER_TRUSTMANAGEMENT_HEADER, parent=self.sr.topParent)
        self.SetMinSize((368, 300))
        self.sr.main.top = 2
        self.sr.inputContainer = uicls.Container(name='inputContainer', parent=self.sr.main, align=uiconst.TOTOP, height=50)
        self.sr.bodyContainer = uicls.Container(name='bodyContainer', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.sr.trustContainer = uicls.Container(name='trustContainer', parent=self.sr.bodyContainer, align=uiconst.TOTOP, height=76)
        self.sr.ignoreContainer = uicls.Container(name='ignoreContainer', parent=self.sr.bodyContainer, align=uiconst.TOBOTTOM, height=76)
        uicls.Line(parent=self.sr.inputContainer, align=uiconst.TOBOTTOM, color=(0.5, 0.5, 0.5, 0.75))
        uicls.Line(parent=self.sr.inputContainer, align=uiconst.TOTOP, color=(0.5, 0.5, 0.5, 0.75))
        uicls.Line(parent=self.sr.ignoreContainer, align=uiconst.TOTOP, color=(0.5, 0.5, 0.5, 0.75))
        urlInputContainer = uicls.Container(name='urlInputContainer', parent=self.sr.inputContainer, align=uiconst.TOTOP, height=22, top=3)
        inputButtonContainer = uicls.Container(name='urlInputButtonContainer', parent=self.sr.inputContainer, align=uiconst.TOBOTTOM, height=20)
        self.sr.urlText = uicls.Label(text=mls.UI_GENERIC_URL, parent=urlInputContainer, align=uiconst.TOLEFT, left=6, autoheight=False, state=uiconst.UI_DISABLED, uppercase=1, fontsize=10, letterspace=1)
        self.sr.urlInput = uicls.SinglelineEdit(name='urlInput', parent=urlInputContainer, align=uiconst.TOALL, pos=(8, 0, 8, 0))
        self.sr.trustBtn = uicls.Button(parent=inputButtonContainer, label=mls.UI_CMD_TRUSTSITE, align=uiconst.TORIGHT, pos=(4, 0, 0, 0), padBottom=3, func=self.TrustSite)
        self.sr.trustBtn.hint = mls.UI_BROWSER_TRUSTMGMT_TRUSTHINT
        self.sr.ignoreBtn = uicls.Button(parent=inputButtonContainer, label=mls.UI_CMD_IGNORESITE, align=uiconst.TORIGHT, pos=(4, 0, 0, 0), padBottom=3, func=self.IgnoreSite)
        self.sr.ignoreBtn.hint = mls.UI_BROWSER_TRUSTMGMT_IGNOREHINT
        trustBtnContainer = uicls.Container(name='trustBtnContainer', parent=self.sr.trustContainer, align=uiconst.TOBOTTOM, height=22)
        trustRemoveBtn = uicls.Button(parent=trustBtnContainer, label=mls.UI_CMD_REMOVE, align=uiconst.TORIGHT, pos=(4, 0, 0, 0), padBottom=3, func=self.RemoveTrustedSite)
        trustRemoveBtn.hint = mls.UI_BROWSER_TRUSTMGMT_REMOVETRUSTHINT
        trustTextContainer = uicls.Container(name='trustTextContainer', parent=self.sr.trustContainer, align=uiconst.TOTOP, height=14)
        uicls.Label(text=mls.UI_SHARED_TRUSTEDSITES, parent=trustTextContainer, uppercase=1, letterspace=1, state=uiconst.UI_DISABLED, fontsize=10, left=10, top=3)
        trustScrollContainer = uicls.Container(name='trustScrollContainer', parent=self.sr.trustContainer, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.sr.trustScroll = uicls.Scroll(parent=trustScrollContainer, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        ignoreBtnContainer = uicls.Container(name='ignoreBtnContainer', parent=self.sr.ignoreContainer, align=uiconst.TOBOTTOM, height=22)
        ignoreRemoveBtn = uicls.Button(parent=ignoreBtnContainer, label=mls.UI_CMD_REMOVE, align=uiconst.TORIGHT, pos=(4, 0, 0, 0), padBottom=3, func=self.RemoveIgnoredSite)
        ignoreRemoveBtn.hint = mls.UI_BROWSER_TRUSTMGMT_REMOVEIGNOREDHINT
        ignoreTextContainer = uicls.Container(name='ignoreTextContainer', parent=self.sr.ignoreContainer, align=uiconst.TOTOP, height=14)
        uicls.Label(text=mls.UI_BROWSER_IGNOREDSITES, parent=ignoreTextContainer, uppercase=1, letterspace=1, state=uiconst.UI_DISABLED, fontsize=10, left=10, top=3)
        ignoreScrollContainer = uicls.Container(name='ignoreScrollContainer', parent=self.sr.ignoreContainer, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.sr.ignoreScroll = uicls.Scroll(parent=ignoreScrollContainer, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.inited = 1
        self.sitesSvc = sm.GetService('sites')
        self.RefreshSites()
        if initialUrl is not None:
            self.sr.urlInput.SetValue(initialUrl)



    def _OnResize(self, *args):
        uthread.new(self._WebsiteTrustManagementWindow__OnResize, *args)



    def __OnResize(self, *args):
        if not self or not self.inited:
            return 
        bodyHeight = self.sr.bodyContainer.absoluteBottom - self.sr.bodyContainer.absoluteTop
        halfSize = int(bodyHeight / 2)
        if halfSize * 2 != bodyHeight:
            self.sr.trustContainer.height = halfSize + 1
        else:
            self.sr.trustContainer.height = halfSize
        self.sr.ignoreContainer.height = halfSize



    def TrustSite(self, *args):
        value = self.sr.urlInput.GetValue()
        if not value:
            eve.Message('trustedSiteManagementPleaseEnterUrl')
            return 
        value = value.strip()
        if value is not None and len(value) > 0:
            self.sitesSvc.AddTrustedSite(value)
        else:
            eve.Message('trustedSiteManagementPleaseEnterUrl')



    def IgnoreSite(self, *args):
        value = self.sr.urlInput.GetValue()
        if not value:
            eve.Message('trustedSiteManagementPleaseEnterUrl')
            return 
        value = value.strip()
        if value is not None and len(value) > 0:
            self.sitesSvc.AddIgnoredSite(value)
        else:
            eve.Message('trustedSiteManagementPleaseEnterUrl')



    def RemoveTrustedSite(self, *args):
        selected = self.sr.trustScroll.GetSelected()
        if not len(selected):
            eve.Message('trustedSiteManagementPleaseSelectSite')
            return 
        for entry in selected:
            self.sitesSvc.RemoveTrustedSite(entry.retval)




    def RemoveIgnoredSite(self, *args):
        selected = self.sr.ignoreScroll.GetSelected()
        if not len(selected):
            eve.Message('trustedSiteManagementPleaseSelectSite')
            return 
        for entry in selected:
            self.sitesSvc.RemoveTrustedSite(entry.retval)




    def OnTrustedSitesChange(self, *etc):
        self.RefreshSites()



    def OnGetTrustMenu(self, entry):
        return [(mls.UI_CMD_REMOVE, sm.GetService('sites').RemoveTrustedSite, (entry.sr.node.retval,))]



    def RefreshSites(self):
        trustScrollList = []
        ignoreScrollList = []
        for (key, value,) in self.sitesSvc.GetTrustedSites().iteritems():
            if value.auto:
                continue
            trustScrollList.append(listentry.Get('Generic', {'label': key,
             'retval': key,
             'trustData': value,
             'GetMenu': self.OnGetTrustMenu}))

        for (key, value,) in self.sitesSvc.GetIgnoredSites().iteritems():
            if value.auto:
                continue
            ignoreScrollList.append(listentry.Get('Generic', {'label': key,
             'retval': key,
             'trustData': value,
             'GetMenu': self.OnGetTrustMenu}))

        self.sr.trustScroll.Load(contentList=trustScrollList)
        self.sr.ignoreScroll.Load(contentList=ignoreScrollList)




class TrustedSitePromptWindow(uicls.Window):
    __guid__ = 'form.TrustedSitePrompt'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        trustUrl = attributes.trustUrl
        inputUrl = attributes.inputUrl
        self.SetWndIcon('ui_9_64_4')
        self.SetCaption(mls.UI_GENERIC_ASKTRUSTEDSITES)
        self.SetMinSize((400, 300))
        self.sr.main = main = uiutil.GetChild(self, 'main')
        uicls.WndCaptionLabel(text=mls.UI_BROWSER_TRUSTPROMPT_HEADER, parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.sr.ignoreAlwaysBtnPar = uicls.Container(name='ignoreAlwaysBtnPar', parent=self.sr.main, align=uiconst.TOBOTTOM, height=22, top=2)
        self.sr.ignoreBtnPar = uicls.Container(name='ignoreBtnPar', parent=self.sr.main, align=uiconst.TOBOTTOM, height=22, top=2)
        self.sr.trustBtn = uicls.Button(parent=self.sr.ignoreBtnPar, label=mls.UI_BROWSER_TRUSTPROMPT_TRUSTSITE, align=uiconst.TOLEFT, pos=(4, 0, 0, 0), func=self.TrustSite)
        self.sr.trustBtn.hint = mls.UI_BROWSER_TRUSTPROMPT_TRUSTBUTTONHINT
        self.sr.ignoreBtn = uicls.Button(parent=self.sr.ignoreBtnPar, label=mls.UI_BROWSER_TRUSTPROMPT_IGNOREONCE, align=uiconst.TORIGHT, pos=(4, 0, 0, 0), func=self.IgnoreThisRequest)
        self.sr.ignoreBtn.hint = mls.UI_BROWSER_TRUSTPROMPT_IGNOREONCEHINT
        self.sr.ignoreAlwaysBtn = uicls.Button(parent=self.sr.ignoreAlwaysBtnPar, label=mls.UI_BROWSER_TRUSTPROMPT_IGNOREALWAYS, align=uiconst.TORIGHT, pos=(4, 0, 0, 0), func=self.AlwaysIgnoreRequests)
        self.sr.ignoreAlwaysBtn.hint = mls.UI_BROWSER_TRUSTPROMPT_IGNOREALWAYSHINT
        self.sr.sourcePar = uicls.Container(name='sourcePar', parent=self.sr.main, align=uiconst.TOBOTTOM, height=30)
        self.sr.sourceTxtPar = uicls.Container(name='sourceTxtPar', parent=self.sr.sourcePar, align=uiconst.TOTOP, height=14)
        self.sr.sourceUrlPar = uicls.Container(name='sourceUrlPar', parent=self.sr.sourcePar, align=uiconst.TOTOP, height=14)
        self.sr.sourceTxt = uicls.Label(text=mls.UI_BROWSER_TRUSTPROMPT_REQUESTFROM, parent=self.sr.sourceTxtPar, state=uiconst.UI_DISABLED, fontsize=10, letterspace=1, uppercase=1, color=(0.5, 0.5, 0.5, 0.7), align=uiconst.TOALL, left=8, autowidth=False, autoheight=False)
        self.sr.sourceUrl = uicls.Label(text=inputUrl, parent=self.sr.sourceUrlPar, state=uiconst.UI_NORMAL, fontsize=10, letterspace=1, uppercase=1, color=(0.5, 0.5, 0.5, 0.7), align=uiconst.TOALL, left=16, autowidth=False, autoheight=False)
        self.sr.sourceUrl.hint = inputUrl
        uicls.Line(parent=self.sr.sourcePar, align=uiconst.TOTOP, color=(0.4, 0.4, 0.4, 0.9))
        self.sr.promptPar = uicls.Container(name='promptPar', parent=self.sr.main, align=uiconst.TOALL, pos=(8, 2, 8, 2))
        self.sr.promptTxt = uicls.Edit(setvalue=mls.UI_BROWSER_TRUSTPROMPT_TRUSTDESCRIPTION % trustUrl, parent=self.sr.promptPar, readonly=1, align=uiconst.TOALL)
        self.trustUrl = trustUrl
        self.inputUrl = inputUrl



    def TrustSite(self, *args):
        sm.GetService('sites').AddTrustedSite(self.trustUrl)
        self.CloseX()



    def IgnoreThisRequest(self, *args):
        self.CloseX()



    def AlwaysIgnoreRequests(self, *args):
        sm.GetService('sites').AddIgnoredSite(self.inputUrl)
        self.CloseX()



exports = {'form.WebsiteTrustManagementWindow': WebsiteTrustManagementWindow,
 'form.TrustedSitePrompt': TrustedSitePromptWindow}

