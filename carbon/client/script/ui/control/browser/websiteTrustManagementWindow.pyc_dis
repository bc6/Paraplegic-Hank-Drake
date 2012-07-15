#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/browser/websiteTrustManagementWindow.py
import uiconst
import uicls
import uthread
import localization

class WebsiteTrustManagementWindowCore(uicls.Window):
    __guid__ = 'uicls.WebsiteTrustManagementWindowCore'
    __notifyevents__ = ['OnTrustedSitesChange']
    default_windowID = 'WebsiteTrustManagementWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        initialUrl = attributes.initialUrl
        self.SetCaption(localization.GetByLabel('UI/Browser/TrustedSites'))
        self.SetMinSize((368, 300))
        mainArea = self.GetMainArea()
        mainArea.top = 2
        self.inputContainer = uicls.Container(name='inputContainer', parent=mainArea, align=uiconst.TOTOP, height=50)
        self.bodyContainer = uicls.Container(name='bodyContainer', parent=mainArea, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        print 'HALLO'
        self.trustContainer = uicls.Container(name='trustContainer', parent=self.bodyContainer, align=uiconst.TOTOP, height=76)
        self.ignoreContainer = uicls.Container(name='ignoreContainer', parent=self.bodyContainer, align=uiconst.TOBOTTOM, height=76)
        uicls.Line(parent=self.inputContainer, align=uiconst.TOBOTTOM, color=(0.5, 0.5, 0.5, 0.75))
        uicls.Line(parent=self.inputContainer, align=uiconst.TOTOP, color=(0.5, 0.5, 0.5, 0.75))
        uicls.Line(parent=self.ignoreContainer, align=uiconst.TOTOP, color=(0.5, 0.5, 0.5, 0.75))
        urlInputContainer = uicls.Container(name='urlInputContainer', parent=self.inputContainer, align=uiconst.TOTOP, height=22, top=3)
        inputButtonContainer = uicls.Container(name='urlInputButtonContainer', parent=self.inputContainer, align=uiconst.TOBOTTOM, height=20)
        self.urlText = uicls.Label(text=localization.GetByLabel('UI/Browser/EditBookmarks/URL'), parent=urlInputContainer, align=uiconst.TOLEFT, padLeft=6, state=uiconst.UI_DISABLED, uppercase=1, fontsize=10, letterspace=1)
        self.urlInput = uicls.SinglelineEdit(name='urlInput', parent=urlInputContainer, align=uiconst.TOTOP, padRight=const.defaultPadding, padLeft=const.defaultPadding)
        self.trustBtn = uicls.Button(parent=inputButtonContainer, label=localization.GetByLabel('UI/Browser/TrustSite'), align=uiconst.TORIGHT, padLeft=4, padBottom=3, func=self.TrustSite)
        self.trustBtn.hint = localization.GetByLabel('UI/Browser/TrustManagementTrustHint')
        self.ignoreBtn = uicls.Button(parent=inputButtonContainer, label=localization.GetByLabel('UI/Browser/IgnoreSite'), align=uiconst.TORIGHT, padLeft=4, padBottom=3, func=self.IgnoreSite)
        self.ignoreBtn.hint = localization.GetByLabel('UI/Browser/TrustManagementIgnoreHint')
        trustBtnContainer = uicls.Container(name='trustBtnContainer', parent=self.trustContainer, align=uiconst.TOBOTTOM, height=22)
        trustRemoveBtn = uicls.Button(parent=trustBtnContainer, label=localization.GetByLabel('UI/Commands/Remove'), align=uiconst.TORIGHT, padLeft=4, padBottom=3, func=self.RemoveTrustedSite)
        trustRemoveBtn.hint = localization.GetByLabel('UI/Browser/TrustManagementRemoveTrustHint')
        trustTextContainer = uicls.Container(name='trustTextContainer', parent=self.trustContainer, align=uiconst.TOTOP, height=14)
        uicls.Label(text=localization.GetByLabel('UI/Browser/TrustedSites'), parent=trustTextContainer, state=uiconst.UI_DISABLED, fontsize=10, left=10, top=3)
        trustScrollContainer = uicls.Container(name='trustScrollContainer', parent=self.trustContainer, align=uiconst.TOALL)
        self.trustScroll = uicls.Scroll(parent=trustScrollContainer, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        ignoreBtnContainer = uicls.Container(name='ignoreBtnContainer', parent=self.ignoreContainer, align=uiconst.TOBOTTOM, height=22)
        ignoreRemoveBtn = uicls.Button(parent=ignoreBtnContainer, label=localization.GetByLabel('UI/Commands/Remove'), align=uiconst.TORIGHT, padLeft=4, padBottom=3, func=self.RemoveIgnoredSite)
        ignoreRemoveBtn.hint = localization.GetByLabel('UI/Browser/TrustManagementRemoveIgnoredHint')
        ignoreTextContainer = uicls.Container(name='ignoreTextContainer', parent=self.ignoreContainer, align=uiconst.TOTOP, height=14)
        uicls.Label(text=localization.GetByLabel('UI/Browser/IgnoredSites'), parent=ignoreTextContainer, state=uiconst.UI_DISABLED, fontsize=10, left=10, top=3)
        ignoreScrollContainer = uicls.Container(name='ignoreScrollContainer', parent=self.ignoreContainer, align=uiconst.TOALL)
        self.ignoreScroll = uicls.Scroll(parent=ignoreScrollContainer, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.inited = 1
        self.sitesSvc = sm.GetService('sites')
        self.RefreshSites()
        if initialUrl is not None:
            self.urlInput.SetValue(initialUrl)

    def _OnResize(self, *args):
        uthread.new(self.__OnResize, *args)

    def __OnResize(self, *args):
        if not getattr(self, 'inited', False):
            return
        bodyHeight = self.bodyContainer.absoluteBottom - self.bodyContainer.absoluteTop
        halfSize = int(bodyHeight / 2)
        if halfSize * 2 != bodyHeight:
            self.trustContainer.height = halfSize + 1
        else:
            self.trustContainer.height = halfSize
        self.ignoreContainer.height = halfSize

    def TrustSite(self, *args):
        value = self.urlInput.GetValue()
        if not value:
            eve.Message('trustedSiteManagementPleaseEnterUrl')
            return
        value = value.strip()
        if value is not None and len(value) > 0:
            self.sitesSvc.AddTrustedSite(value)
        else:
            eve.Message('trustedSiteManagementPleaseEnterUrl')

    def IgnoreSite(self, *args):
        value = self.urlInput.GetValue()
        if not value:
            eve.Message('trustedSiteManagementPleaseEnterUrl')
            return
        value = value.strip()
        if value is not None and len(value) > 0:
            self.sitesSvc.AddIgnoredSite(value)
        else:
            eve.Message('trustedSiteManagementPleaseEnterUrl')

    def RemoveTrustedSite(self, *args):
        selected = self.trustScroll.GetSelected()
        if not len(selected):
            eve.Message('trustedSiteManagementPleaseSelectSite')
            return
        for entry in selected:
            self.sitesSvc.RemoveTrustedSite(entry.retval)

    def RemoveIgnoredSite(self, *args):
        selected = self.ignoreScroll.GetSelected()
        if not len(selected):
            eve.Message('trustedSiteManagementPleaseSelectSite')
            return
        for entry in selected:
            self.sitesSvc.RemoveTrustedSite(entry.retval)

    def OnTrustedSitesChange(self, *etc):
        self.RefreshSites()

    def OnGetTrustMenu(self, entry):
        return [(localization.GetByLabel('UI/Commands/Remove'), sm.GetService('sites').RemoveTrustedSite, (entry.sr.node.retval,))]

    def RefreshSites(self):
        trustScrollList = []
        ignoreScrollList = []
        for key, value in self.sitesSvc.GetTrustedSites().iteritems():
            if value.auto:
                continue
            trustScrollList.append(uicls.ScrollEntryNode(decoClass=uicls.SE_Generic, label=key, retval=key, trustData=value, GetMenu=self.OnGetTrustMenu))

        for key, value in self.sitesSvc.GetIgnoredSites().iteritems():
            if value.auto:
                continue
            ignoreScrollList.append(uicls.ScrollEntryNode(decoClass=uicls.SE_Generic, label=key, retval=key, trustData=value, GetMenu=self.OnGetTrustMenu))

        self.trustScroll.Load(contentList=trustScrollList)
        self.ignoreScroll.Load(contentList=ignoreScrollList)