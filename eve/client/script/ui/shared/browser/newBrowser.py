import uix
import uiutil
import xtriui
import form
import uthread
import blue
import urlparse
import browserutil
import browser
import log
import uiconst
import cgi
import uicls

class EveBrowserWindow(uicls.Window):
    __guid__ = 'form.EveBrowserWindow'
    __notifyevents__ = ['OnTrustedSitesChange',
     'OnSessionChanged',
     'OnClientBrowserLockdownChange',
     'OnClientFlaggedListsChange',
     'OnEndChangeDevice',
     'OnBrowserShowStatusBarChange',
     'OnBrowserShowNavigationBarChange',
     'OnBrowserHistoryCleared']
    default_width = 600
    default_height = 600

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        initialUrl = attributes.initialUrl
        self.reloadingTrustedSites = False
        self.awaitingTitle = False
        self.nextTabID = 1
        self.currentTab = None
        self.browserHostManager = sm.GetService('browserHostManager').GetBrowserHost()
        self.tabs = []
        self.browserButtons = (('Back',
          self.HistoryBack,
          20,
          'back'),
         ('Forward',
          self.HistoryForward,
          60,
          'next'),
         (None, None, None, None),
         ('Reload',
          self.ReloadPage,
          -40,
          'reload'),
         ('Stop',
          self.StopLoading,
          20,
          'stop'),
         (None, None, None, None),
         ('Home',
          self.GoHome,
          0,
          'home'))
        self.SetWndIcon('ui_9_64_4')
        self.SetTopparentHeight(0)
        self.MakeUnstackable()
        self.SetMinSize([260, 180])
        self.SetMaxSize([uicore.desktop.width, uicore.desktop.height])
        self.sr.menuBar = uicls.Container(name='menuBar', parent=self.sr.main, align=uiconst.TOTOP, height=16)
        uicls.Line(parent=self.sr.menuBar, align=uiconst.TOBOTTOM)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, height=2)
        self.sr.navigationBar = uicls.Container(name='navBar', parent=self.sr.main, align=uiconst.TOTOP, height=24, clipChildren=1)
        uicls.Container(name='tabShim', parent=self.sr.main, align=uiconst.TOTOP, height=4, clipChildren=0)
        self.sr.tabParent = uicls.Container(name='tabParent', parent=self.sr.main, align=uiconst.TOTOP, height=24, clipChildren=0)
        self.sr.tabLeft = uicls.Container(name='tabLeft', parent=self.sr.tabParent, align=uiconst.TOPLEFT, height=22, width=22, clipChildren=0, top=-4)
        self.sr.tabRight = uicls.Container(name='tabRight', parent=self.sr.tabParent, align=uiconst.TOPRIGHT, width=22, height=22, clipChildren=0, left=1, top=-4)
        self.sr.tabBar = uicls.Container(name='tabBar', parent=self.sr.tabParent, align=uiconst.TOALL, pos=(0, 0, 0, 0), clipChildren=1)
        self.sr.statusBar = uicls.Container(name='statusBar', parent=self.sr.main, align=uiconst.TOBOTTOM, height=22, clipChildren=1)
        self.sr.browserContainer = uicls.Container(name='browserContainer', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        if not settings.user.ui.Get('browserShowNavBar', True):
            self.sr.navigationBar.state = uiconst.UI_HIDDEN
        if not settings.user.ui.Get('browserShowStatusBar', True):
            self.sr.statusBar.state = uiconst.UI_HIDDEN
        buttonTop = uicls.Container(name='buttonTop', parent=self.sr.navigationBar, padRight=const.defaultPadding, align=uiconst.TOLEFT)
        searchTop = uicls.Container(name='urlInput', parent=self.sr.navigationBar, height=20, padTop=2, align=uiconst.TOTOP)
        for (btnLabel, btnFunc, btnRectLeft, btnName,) in self.browserButtons:
            if btnLabel is None:
                buttonTop.width += 6
                continue
            button = uicls.ImageButton(parent=buttonTop, name=btnLabel, width=20, height=20, align=uiconst.RELATIVE, top=2, left=buttonTop.width, idleIcon='res:/UI/Texture/classes/Browser/%sIdle.png' % btnName, mouseoverIcon='res:/UI/Texture/classes/Browser/%sMouseOver.png' % btnName, mousedownIcon='res:/UI/Texture/classes/Browser/%sIdle.png' % btnName, onclick=btnFunc, hint=getattr(mls, 'UI_SHARED_BROWSER' + btnLabel.upper(), ''))
            button.flag = btnLabel
            setattr(self.sr, '%sButton' % btnLabel, button)
            buttonTop.width += 20

        btnPar = uicls.Container(parent=searchTop, align=uiconst.TORIGHT)
        goBtn = uicls.Button(parent=btnPar, label=mls.UI_SHARED_BROWSERGO, func=self.OnGoBtn, align=uiconst.CENTER)
        self.sr.navigationButtonBar = buttonTop
        self.sr.goButton = goBtn
        btnPar.width = goBtn.width + 8
        iconContainer = uicls.Container(name='sslIndicator', parent=searchTop, align=uiconst.TORIGHT, width=20, padRight=4)
        uicls.Icon(name='sslIcon', icon='ui_77_32_9', parent=iconContainer, pos=(2, -3, 24, 24), hint=mls.UI_BROWSER_SECURE_CONNECTION, ignoreSize=True, state=uiconst.UI_NORMAL)
        iconContainer.state = uiconst.UI_HIDDEN
        self.sr.sslIconContainer = iconContainer
        self.sr.urlInput = uicls.SinglelineEdit(name='urlInput', parent=searchTop, pos=(0, 0, 1, 0), align=uiconst.TOALL, maxLength=1630, autoselect=True)
        self.sr.urlInput.OnReturn = self.BrowseTo
        self.sr.urlInput.OnHistoryClick = self.OnHistoryClicked
        for (name, GetMenu,) in [(mls.UI_SHARED_BROWSERVIEW, lambda : [(mls.UI_SHARED_BROWSERRELOAD, self.ReloadPage, ()), (mls.UI_CMD_VIEWSOURCE, self.DocumentSource, ()), (mls.UI_CMD_BROWSER_HISTORY, self.OpenBrowserHistory, ())]), (mls.UI_CMD_BROWSERBOOKMARKS, self.GetBookmarkMenu), (mls.UI_CMD_OPTIONS, lambda : [(mls.UI_CMD_GENERALSETTINGS, self.EditGeneralSettings, ()), None, (mls.UI_CMD_TRUSTEDSITES, self.EditSites, ('trusted',))])]:
            opt = xtriui.StandardMenu(name='menuoption', parent=self.sr.menuBar, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
            opt.Setup(name, GetMenu)

        iconContainer = uicls.Container(name='trustIndicator', parent=self.sr.statusBar, align=uiconst.TORIGHT, width=24, left=4)
        icon = uicls.Icon(name='trustIndicatorIcon', parent=iconContainer, icon='ui_77_32_7', pos=(0, -3, 24, 24), hint=mls.UI_BROWSER_TRUSTED_SITE, ignoreSize=True, state=uiconst.UI_DISABLED)
        self.sr.trustIndicatorIcon = icon
        self.sr.trustIndicatorIcon.state = uiconst.UI_HIDDEN
        iconContainer = uicls.Container(name='lockdownIndicator', parent=self.sr.statusBar, align=uiconst.TOLEFT, width=28)
        uicls.Icon(name='lockdownIndicatorIcon', parent=iconContainer, icon='ui_77_32_6', pos=(2, -3, 24, 24), hint=mls.BrowserLockdownEnabled, ignoreSize=True, state=uiconst.UI_NORMAL)
        self.sr.lockdownIconContainer = iconContainer
        self.sr.statusText = uicls.Label(text='', parent=self.sr.statusBar, singleline=1, align=uiconst.TOALL, state=uiconst.UI_NORMAL)
        self.sr.browserPaneContainer = uicls.Container(name='browserPane', parent=self.sr.browserContainer, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, pos=(const.defaultPadding,
         0,
         const.defaultPadding,
         0))
        bp = browser.BrowserPane(parent=self.sr.browserPaneContainer, padding=(6, 6, 6, 6), align=uiconst.TOALL, state=uiconst.UI_NORMAL)
        bp.Startup()
        self.sr.browserPane = bp
        self.sr.crashNotifierContainer = uicls.Container(name='crashNotifierContainer', parent=self.sr.browserContainer, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, width=240, height=80, idx=0)
        uicls.Label(text=mls.UI_BROWSER_CRASHED, parent=self.sr.crashNotifierContainer, align=uiconst.TOALL, fontsize=16, letterspace=1, autowidth=False, autoheight=False, state=uiconst.UI_NORMAL)
        uicls.Fill(parent=self.sr.crashNotifierContainer, color=(0.0, 0.0, 0.0, 1.0))
        fillContainer = uicls.Container(name='browserBackground', parent=bp.parent, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        uicls.Fill(parent=fillContainer, color=(0.0, 0.0, 0.0, 1.0))
        self.tabButtons = []
        btn = uicls.Button(parent=self.sr.tabLeft, label='-', align=uiconst.TOPLEFT, fixedwidth=22, func=self.CloseTabButton, alwaysLite=True)
        btn.hint = mls.UI_BROWSER_CLOSETAB
        self.tabButtons.append(btn)
        btn = uicls.Button(parent=self.sr.tabRight, label='+', align=uiconst.TOPLEFT, fixedwidth=22, func=self.AddTabButton, alwaysLite=True)
        btn.hint = mls.UI_BROWSER_NEWTAB
        self.tabButtons.append(btn)
        self.OnClientFlaggedListsChange()
        browseToUrl = initialUrl
        if browseToUrl is None or browseToUrl == 'home':
            browseToUrl = str(settings.user.ui.Get('HomePage2', browserutil.DefaultHomepage()))
        self.AddTab(browseToUrl)
        blue.pyos.synchro.Yield()
        uthread.new(self.ToggleButtonAppearance)



    def OnClose_(self, *args):
        sm.GetService('urlhistory').SaveHistory()
        ct = getattr(self, 'currentTab', None)
        if ct is not None:
            ct.Cleanup()
            ct = None
        if self.sr.browserPane:
            self.sr.browserPane.browserSession = None
            del self.sr.browserPane
        if getattr(self, 'tabs', None):
            for tab in self.tabs[:]:
                tab.Cleanup()
                del tab

            self.tabs = []



    def ToggleButtonAppearance(self):
        if self and not self.destroyed and hasattr(self, 'tabButtons'):
            for btn in self.tabButtons:
                btn.LiteMode(True)




    def PopulateWhitelistAndBlacklist(self):
        self.browserHostManager.ClearSiteList('Blacklist')
        self.browserHostManager.ClearSiteList('Whitelist')
        l = sm.GetService('sites').GetBrowserBlacklist()
        for url in l:
            self.browserHostManager.AddToSiteList('Blacklist', url)

        l = sm.GetService('sites').GetBrowserWhitelist()
        for url in l:
            self.browserHostManager.AddToSiteList('Whitelist', url)




    def OnClientFlaggedListsChange(self, *args):
        self.PopulateWhitelistAndBlacklist()
        self.browserHostManager.UpdateDynamicData()
        self.OnClientBrowserLockdownChange()
        self.OnTrustedSitesChange()



    def OnClientBrowserLockdownChange(self, *args):
        for tab in self.tabs:
            tab._OnClientBrowserLockdownChange(args)

        if sm.GetService('sites').IsBrowserInLockdown():
            self.sr.lockdownIconContainer.state = uiconst.UI_PICKCHILDREN
            self.sr.statusText.left = 0
        else:
            self.sr.lockdownIconContainer.state = uiconst.UI_HIDDEN
            self.sr.statusText.left = 6



    def OnEndChangeDevice(self, change, *args):
        self.SetMaxSize([uicore.desktop.width, uicore.desktop.height])



    def OnBrowserShowStatusBarChange(self, *args):
        show = settings.user.ui.Get('browserShowStatusBar', True)
        self.DisplayStatusBar(show)



    def OnBrowserShowNavigationBarChange(self, *args):
        show = settings.user.ui.Get('browserShowNavBar', True)
        self.DisplayNavigationBar(show)



    def OnBrowserHistoryCleared(self, *args):
        if self and not self.destroyed:
            self.sr.urlInput.ClearHistory()



    def AddToAllOtherSites(self, header, value):
        self.browserHostManager.SetHeader('other', header, unicode(value))



    def AddToAllTrustedSites(self, header, value):
        self.browserHostManager.SetHeader('CCP', header, unicode(value))
        self.browserHostManager.SetHeader('COMMUNITY', header, unicode(value))
        self.browserHostManager.SetHeader('trusted', header, unicode(value))



    def RemoveFromAllTrustedSites(self, header):
        self.browserHostManager.DelHeader('CCP', header)
        self.browserHostManager.DelHeader('COMMUNITY', header)
        self.browserHostManager.DelHeader('trusted', header)



    def AddToCCPTrustedSites(self, header, value):
        self.browserHostManager.SetHeader('CCP', header, unicode(value))
        self.browserHostManager.SetHeader('COMMUNITY', header, unicode(value))



    def OnSessionChanged(self, isRemote, sess, change):
        if change.has_key('regionid'):
            if eve.session.regionid:
                self.AddToAllTrustedSites('EVE_REGIONNAME', eve.session.regionid and cfg.evelocations.Get(eve.session.regionid).name)
                self.AddToAllTrustedSites('EVE_REGIONID', '%s' % eve.session.regionid)
        if change.has_key('constellationid'):
            if eve.session.constellationid:
                self.AddToAllTrustedSites('EVE_CONSTELLATIONNAME', eve.session.constellationid and cfg.evelocations.Get(eve.session.constellationid).name)
                self.AddToAllTrustedSites('EVE_CONSTELLATIONID', '%s' % eve.session.constellationid)
        if change.has_key('solarsystemid') or change.has_key('solarsystemid2'):
            ssid = eve.session.solarsystemid or eve.session.solarsystemid2
            if ssid:
                self.AddToAllTrustedSites('EVE_SOLARSYSTEMNAME', ssid and cfg.evelocations.Get(ssid).name)
                self.AddToAllTrustedSites('EVE_SOLARSYSTEMID', '%s' % ssid)
        if change.has_key('corpid'):
            if eve.session.corpid:
                self.AddToAllTrustedSites('EVE_CORPNAME', eve.session.corpid and cfg.eveowners.Get(eve.session.corpid).name)
                self.AddToAllTrustedSites('EVE_CORPID', '%s' % eve.session.corpid)
        if change.has_key('stationid'):
            if eve.session.stationid:
                self.AddToAllTrustedSites('EVE_STATIONNAME', eve.session.stationid and cfg.evelocations.Get(eve.session.stationid).name)
                self.AddToAllTrustedSites('EVE_STATIONID', '%s' % eve.session.stationid)
            else:
                self.RemoveFromAllTrustedSites('EVE_STATIONNAME')
                self.RemoveFromAllTrustedSites('EVE_STATIONID')
        if change.has_key('allianceid'):
            if eve.session.allianceid:
                self.AddToAllTrustedSites('EVE_ALLIANCENAME', eve.session.allianceid and cfg.eveowners.Get(eve.session.allianceid).name)
                self.AddToAllTrustedSites('EVE_ALLIANCEID', '%s' % eve.session.allianceid)
            else:
                self.RemoveFromAllTrustedSites('EVE_ALLIANCENAME')
                self.RemoveFromAllTrustedSites('EVE_ALLIANCEID')
        if change.has_key('corprole'):
            self.AddToAllTrustedSites('EVE_CORPROLE', '%s' % eve.session.corprole or 0)
        if change.has_key('warfactionid'):
            self.AddToAllTrustedSites('EVE_WARFACTIONID', '%s' % eve.session.warfactionid)
        if change.has_key('shipid'):
            if session.shipid:
                self.AddToAllTrustedSites('EVE_SHIPID', '%s' % session.shipid)
                self.AddToAllTrustedSites('EVE_SHIPNAME', cfg.evelocations.Get(session.shipid).name)
                shipType = sm.GetService('godma').GetItem(session.shipid)
                self.AddToAllTrustedSites('EVE_SHIPTYPEID', '%s' % shipType.typeID)
                self.AddToAllTrustedSites('EVE_SHIPTYPENAME', shipType.name)
            else:
                self.RemoveFromAllTrustedSites('EVE_SHIPID')
                self.RemoveFromAllTrustedSites('EVE_SHIPNAME')
                self.RemoveFromAllTrustedSites('EVE_SHIPTYPEID')
                self.RemoveFromAllTrustedSites('EVE_SHIPTYPENAME')



    def SetupTrustedSiteHeaders(self):
        self.browserHostManager.ClearSiteList('trusted')
        self.browserHostManager.ClearSiteList('CCP')
        self.browserHostManager.ClearSiteList('COMMUNITY')

        def SiteMatch(siteA, siteB):
            if not siteA or not siteB:
                return siteA == siteB
            if siteA.find('://') == -1:
                siteA = 'http://' + siteA
            if siteB.find('://') == -1:
                siteB = 'http://' + siteB
            parsedSiteA = urlparse.urlsplit(siteA)
            parsedSiteB = urlparse.urlsplit(siteB)
            return parsedSiteA[1] == parsedSiteB[1]


        trusted = sm.GetService('sites').GetTrustedSites()
        userTrustedSites = []
        autoTrustedSites = []
        communitySites = []
        for (site, flags,) in trusted.iteritems():
            try:
                if flags.auto == 0:
                    userTrustedSites.append(str(site))
                elif flags.community == 0:
                    autoTrustedSites.append(str(site))
                else:
                    communitySites.append(str(site))
            except:
                log.LogException('Error loading trusted sites, flags = %s' % flags)

        for site in userTrustedSites:
            cnt = False
            for siteB in autoTrustedSites:
                if SiteMatch(site, siteB):
                    cnt = True
                    break

            if cnt:
                continue
            cnt = False
            for siteB in communitySites:
                if SiteMatch(site, siteB):
                    cnt = True
                    break

            if cnt:
                continue
            self.browserHostManager.AddToSiteList('trusted', site)

        for site in autoTrustedSites:
            if site.startswith('.'):
                site = '*%s' % site
            if site.endswith('/'):
                site += '*'
            self.browserHostManager.AddToSiteList('CCP', site)

        for site in communitySites:
            if site.startswith('.'):
                site = '*%s' % site
            if site.endswith('/'):
                site += '*'
            self.browserHostManager.AddToSiteList('COMMUNITY', site)

        self.AddToAllTrustedSites('EVE_TRUSTED', 'Yes')
        self.AddToAllOtherSites('EVE_TRUSTED', 'No')
        self.AddToCCPTrustedSites('EVE_USERID', '%s' % eve.session.userid)
        self.AddToCCPTrustedSites('EVE_VERSION', '%s' % boot.build)
        if sm.GetService('machoNet').GetTransport('ip:packet:server') is not None and sm.GetService('machoNet').GetTransport('ip:packet:server').transport.address is not None:
            self.AddToAllTrustedSites('EVE_SERVERIP', sm.GetService('machoNet').GetTransport('ip:packet:server') and sm.GetService('machoNet').GetTransport('ip:packet:server').transport.address)
        if eve.session.charid:
            self.AddToAllTrustedSites('EVE_CHARNAME', eve.session.charid and cfg.eveowners.Get(eve.session.charid).name)
            self.AddToAllTrustedSites('EVE_CHARID', '%s' % eve.session.charid)
        if eve.session.corpid:
            self.AddToAllTrustedSites('EVE_CORPNAME', eve.session.corpid and cfg.eveowners.Get(eve.session.corpid).name)
            self.AddToAllTrustedSites('EVE_CORPID', '%s' % eve.session.corpid)
        if eve.session.allianceid:
            self.AddToAllTrustedSites('EVE_ALLIANCENAME', eve.session.allianceid and cfg.eveowners.Get(eve.session.allianceid).name)
            self.AddToAllTrustedSites('EVE_ALLIANCEID', '%s' % eve.session.allianceid)
        if eve.session.regionid:
            self.AddToAllTrustedSites('EVE_REGIONNAME', eve.session.regionid and cfg.evelocations.Get(eve.session.regionid).name)
            self.AddToAllTrustedSites('EVE_REGIONID', eve.session.regionid)
        if eve.session.solarsystemid or eve.session.solarsystemid2:
            self.AddToAllTrustedSites('EVE_SOLARSYSTEMNAME', (eve.session.solarsystemid or eve.session.solarsystemid2) and cfg.evelocations.Get(eve.session.solarsystemid or eve.session.solarsystemid2).name)
        if eve.session.constellationid:
            self.AddToAllTrustedSites('EVE_CONSTELLATIONNAME', eve.session.constellationid and cfg.evelocations.Get(eve.session.constellationid).name)
            self.AddToAllTrustedSites('EVE_CONSTELLATIONID', eve.session.constellationid)
        if eve.session.stationid:
            self.AddToAllTrustedSites('EVE_STATIONNAME', eve.session.stationid and cfg.evelocations.Get(eve.session.stationid).name)
            self.AddToAllTrustedSites('EVE_STATIONID', '%s' % eve.session.stationid)
        if eve.session.corprole:
            self.AddToAllTrustedSites('EVE_CORPROLE', '%s' % eve.session.corprole)
        if eve.session.warfactionid:
            self.AddToAllTrustedSites('EVE_WARFACTIONID', '%s' % eve.session.warfactionid)
        if eve.session.shipid:
            self.AddToAllTrustedSites('EVE_SHIPID', '%s' % eve.session.shipid)
            self.AddToAllTrustedSites('EVE_SHIPNAME', cfg.evelocations.Get(eve.session.shipid).name)
            shipType = sm.GetService('godma').GetItem(eve.session.shipid)
            self.AddToAllTrustedSites('EVE_SHIPTYPEID', '%s' % shipType.typeID)
            self.AddToAllTrustedSites('EVE_SHIPTYPENAME', shipType.name)
        self.browserHostManager.UpdateDynamicData()



    def _OnResize(self, *args):
        if self.GetState() != uiconst.RELATIVE:
            return 
        if self.sr.browserPane:
            self.sr.browserPane.ResizeBrowser()
            if self.sr.crashNotifierContainer.state != uiconst.UI_HIDDEN:
                self.RefreshCrashNotifierPosition()



    def OnEndMaximize(self, *args):
        self.OnResizeUpdate()



    def GoHome(self, *args):
        if self.currentTab:
            self.currentTab.GoHome(*args)



    def BrowseTo(self, url = None, *args, **kwargs):
        if self.currentTab is None:
            return 
        if url is None:
            url = self.sr.urlInput.GetValue().encode('cp1252', 'ignore')
        if type(url) is not str:
            url = url.encode('cp1252', 'ignore')
        if url.find(':/') == -1 and url != 'about:blank':
            url = 'http://' + url
        self.sr.browserPane.OnBrowseTo()
        self.currentTab.BrowseTo(url=url, *args)



    def OnHistoryClicked(self, historyString, *args, **kwargs):
        self.BrowseTo(historyString)



    def OnGoBtn(self, *args):
        url = None
        self.BrowseTo(url)



    def ReloadPage(self, *args):
        self.sr.browserPane.OnBrowseTo()
        self.currentTab.ReloadPage(*args)



    def HistoryBack(self, *args):
        self.sr.browserPane.OnBrowseTo()
        self.currentTab.HistoryBack(*args)



    def HistoryForward(self, *args):
        self.sr.browserPane.OnBrowseTo()
        self.currentTab.HistoryForward(*args)



    def StopLoading(self, *args):
        self.currentTab.StopLoading(*args)



    def GetBookmarkMenu(self, startAt = 0):
        m = []
        if startAt < 1:
            m.append((mls.UI_CMD_ADDREMOVE, self.EditBookmarks))
        allMarks = sm.GetService('sites').GetBookmarks()
        myMarks = allMarks[startAt:(startAt + 20)]
        if len(myMarks) >= 20 and len(allMarks) > startAt + 20:
            m.append((mls.UI_GENERIC_MORE, ('isDynamic', self.GetBookmarkMenu, (startAt + 20,))))
        if len(m) > 0:
            m.append(None)
        for each in myMarks:
            if each is not None:
                if each.url.find(':/') == -1:
                    each.url = 'http://' + each.url
                m.append((each.name, self.BrowseTo, (each.url,)))

        return m



    def ViewSourceOfUrl(self, url):
        wnd = sm.GetService('window').GetWindow('virtualbrowser_source', decoClass=form.EveShowSourceWindow, create=1, maximize=1)
        wnd.BrowseTo(url)



    def DocumentSource(self):
        url = self.currentTab.GetCurrentURL()
        self.ViewSourceOfUrl(url)



    def OpenBrowserHistory(self):
        if not self.destroyed:
            wnd = sm.GetService('window').GetWindow('BrowserHistoryWindow', maximize=1, create=1)



    def EditGeneralSettings(self):
        if not self.destroyed:
            wnd = sm.GetService('window').GetWindow('BrowserGeneralSettings', create=1, maximize=1, decoClass=form.BrowserGeneralSettings)
            wnd.ShowModal()



    def EditBookmarks(self):
        if not self.destroyed:
            wnd = sm.GetService('window').GetWindow('EditBookmarks', create=1, maximize=1, bookmarkName=self.sr.caption.text, url=self.sr.urlInput.GetValue())
            wnd.ShowModal()



    def EditSites(self, what):
        inputUrl = ''
        if self.currentTab is not None:
            inputUrl = self.currentTab.GetCurrentURL()
        sm.GetService('window').GetWindow('WebsiteTrustManagementWindow', decoClass=form.WebsiteTrustManagementWindow, create=1, maximize=1, initialUrl=inputUrl)



    def DisplayNavigationBar(self, display):
        if display:
            self.sr.navigationBar.state = uiconst.UI_NORMAL
        else:
            self.sr.navigationBar.state = uiconst.UI_HIDDEN



    def DisplayStatusBar(self, display):
        if display:
            self.sr.statusBar.state = uiconst.UI_NORMAL
        else:
            self.sr.statusBar.state = uiconst.UI_HIDDEN



    def DisplayTrusted(self, display):
        if display:
            self.sr.trustIndicatorIcon.state = uiconst.UI_NORMAL
        else:
            self.sr.trustIndicatorIcon.state = uiconst.UI_HIDDEN



    def IsTrusted(self, url):
        return sm.GetService('sites').IsTrusted(url)



    def OnTrustedSitesChange(self, *args):
        if self.reloadingTrustedSites:
            return 
        try:
            self.reloadingTrustedSites = True
            self.SetupTrustedSiteHeaders()

        finally:
            self.reloadingTrustedSites = False




    def RefreshCrashNotifierPosition(self):
        (l, t, w, h,) = self.GetAbsolute()
        self.sr.crashNotifierContainer.left = (w - self.sr.crashNotifierContainer.width) / 2
        self.sr.crashNotifierContainer.top = (h - self.sr.crashNotifierContainer.height) / 2



    def OnReattachBrowserSession(self, browserSession):
        self.SetupTrustedSiteHeaders()
        self.OnClientFlaggedListsChange()
        if browserSession == self.currentTab:
            self.sr.crashNotifierContainer.state = uiconst.UI_HIDDEN
            self.sr.browserPane.browserSession = browserSession
            browserSession.SetBrowserSurface(self.sr.browserPane.GetSurface(), self.sr.browserPane._OnSurfaceReady)
            self.sr.browserPane.SetCursor(browserSession.cursorType)
            self.sr.browserPane.ResizeBrowser()



    def _OnBrowserViewCrash(self, tabSession):
        if tabSession == self.currentTab:
            self.RefreshCrashNotifierPosition()
            self.sr.crashNotifierContainer.state = uiconst.UI_NORMAL



    def _OnBeginNavigation(self, tabSession, url, frameName):
        tabSession.hint = ''
        if tabSession == self.currentTab:
            self.sr.statusText.text = mls.UI_BROWSER_BROWSINGTO % url
            self.ShowLoad(doBlock=False)
            self.sr.browserPane.state = uiconst.UI_HIDDEN if self.currentTab.hidden else uiconst.UI_NORMAL



    def _OnBeginLoading(self, tabSession, url, frameName, status, mimeType):
        if frameName is None or frameName == '' or frameName == 'main':
            if tabSession == self.currentTab:
                self.sr.urlInput.SetValue(url)
                if uicore.registry.GetFocus() == self.sr.urlInput:
                    self.sr.urlInput.SelectAll()
                self.DisplayTrusted(self.IsTrusted(url))



    def _OnProcessSecurityInfo(self, tabSession, securityInfo):
        if tabSession == self.currentTab:
            self.ProcessSecurityInfo(securityInfo)



    def _OnChangeCursor(self, tabSession, cursorType):
        if tabSession == self.currentTab:
            self.sr.browserPane.SetCursor(cursorType)



    def ProcessSecurityInfo(self, securityInfo):
        try:
            secInfoInt = int(securityInfo)
        except:
            secInfoInt = 0
        if secInfoInt >= 80:
            self.sr.sslIconContainer.state = uiconst.UI_NORMAL
        else:
            self.sr.sslIconContainer.state = uiconst.UI_HIDDEN



    def _OnFinishLoading(self, tabSession):
        if tabSession == self.currentTab:
            self.sr.statusText.text = tabSession.statusText
            self.SetCaption(tabSession.title)
            self.HideLoad()



    def _OnReceiveTitle(self, tabSession, title, frameName):
        if frameName is None or frameName == '' or frameName == 'main':
            if tabSession.logToHistory:
                uthread.new(self.AddToHistory, tabSession.GetCurrentURL(), tabSession.title, blue.os.GetTime())
                tabSession.logToHistory = False
            for tabObject in self.sr.tabs.sr.tabs:
                if tabObject.sr.args == tabSession:
                    tabObject.SetLabel(title, hint=title)
                    break

            if tabSession == self.currentTab:
                self.SetCaption(title)



    def SetCaption(self, caption):
        uicls.Window.SetCaption(self, uiutil.StripTags(caption)[:50])



    def AddToHistory(self, url, title, ts):
        sm.GetService('urlhistory').AddToHistory(url, title, ts)
        w = sm.GetService('window').GetWindow('BrowserHistoryWindow')
        if w:
            w.LoadHistory()



    def _OnChangeTooltip(self, tabSession, tooltip):
        tabSession.hint = tooltip



    def _OnChangeTargetURL(self, tabSession, url):
        if tabSession == self.currentTab:
            self.sr.statusText.text = url



    def _OnJavascriptPrompt(self, tabSession, messageText):
        uthread.new(self._ShowAlert, messageText)



    def _ShowAlert(self, messageText):
        escapedText = cgi.escape(unicode(messageText))
        sm.GetService('gameui').MessageBox(str(escapedText), title=mls.UI_BROWSER_JAVASCRIPT_ALERT, buttons=uiconst.OK, modal=True)



    def SetBrowserFocus(self):
        uicore.registry.SetFocus(self.sr.browserPane)



    def AddTab(self, tabUrl = None):
        newTab = browser.BrowserSession()
        newTab.Startup('%s_%d' % (self.name, self.nextTabID), initialUrl=tabUrl, browserEventHandler=self)
        self.nextTabID += 1
        urlToBrowseTo = newTab.GetCurrentURL()
        newTab.BrowseTo(urlToBrowseTo)
        self.tabs.append(newTab)
        self.ReloadTabs(selectTab=-1)



    def AddTabButton(self, *args):
        self.AddTab()



    def CloseTab(self, tabID):
        if len(self.tabs) < 2:
            return 
        dyingTab = None
        selectTab = -1
        for i in xrange(len(self.tabs)):
            if self.tabs[i].name == tabID:
                if self.tabs[i].name == self.currentTab.name:
                    nextIdx = i if i < len(self.tabs) - 1 else i - 1
                    selectTab = nextIdx
                dyingTab = self.tabs.pop(i)
                dyingTab.Cleanup()
                break

        self.ReloadTabs(selectTab=selectTab)



    def CloseTabButton(self, *args):
        if self.currentTab is not None:
            self.CloseTab(self.currentTab.name)



    def ReloadTabs(self, selectTab = None):
        if not self.tabs or len(self.tabs) < 1:
            return 
        tabs = []
        for tab in self.tabs:
            tabs.append([tab.name,
             None,
             self,
             tab])

        uix.Flush(self.sr.tabBar)
        self.sr.tabs = uicls.TabGroup(name='tabparent', parent=self.sr.tabBar, minTabsize=50, maxTabsize=200, leftMargin=22, rightMargin=20, tabMenuMargin=8)
        self.sr.tabs.Startup(tabs, groupID=None, autoselecttab=0)
        for tabObject in self.sr.tabs.sr.tabs:
            tab = tabObject.sr.args
            tabObject.SetLabel(tab.title, hint=tab.title)

        if self.currentTab is None:
            self.currentTab = self.tabs[0]
        else:
            self.currentTab.SetBrowserSurface(None, None)
            if selectTab is not None:
                self.currentTab = self.tabs[selectTab]
        self.sr.tabs.ShowPanelByName(self.currentTab.name)



    def GetTabMenu(self, uiTab, *args):
        tabSession = uiTab.sr.args
        ops = [(mls.UI_BROWSER_NEWTAB, self.AddTab, [])]
        if len(self.tabs) > 1:
            ops.append((mls.UI_BROWSER_CLOSETAB, self.CloseTab, (tabSession.name,)))
        return ops



    def LoadTabPanel(self, tabBrowserSession, container, tabgroup):
        previousTab = None
        if self.currentTab is not None:
            self.currentTab.SetBrowserSurface(None, None)
        self.sr.statusText.text = tabBrowserSession.statusText
        self.sr.urlInput.SetValue(tabBrowserSession.GetCurrentURL())
        self.ProcessSecurityInfo(tabBrowserSession.securityInfo)
        self.SetCaption(tabBrowserSession.title)
        if tabBrowserSession.loading:
            self.ShowLoad(doBlock=False)
        else:
            self.HideLoad()
        self.DisplayTrusted(self.IsTrusted(tabBrowserSession.GetCurrentURL()))
        self.currentTab = tabBrowserSession
        self.sr.browserPane.browserSession = tabBrowserSession
        tabBrowserSession.SetBrowserSurface(self.sr.browserPane.GetSurface(), self.sr.browserPane._OnSurfaceReady)
        self.sr.browserPane.SetCursor(self.currentTab.cursorType)
        self.sr.browserPane.ResizeBrowser()
        self.sr.browserPane.state = uiconst.UI_HIDDEN if self.currentTab.hidden else uiconst.UI_NORMAL
        if self.currentTab.IsAlive():
            self.sr.crashNotifierContainer.state = uiconst.UI_HIDDEN
        else:
            self.RefreshCrashNotifierPosition()
            self.sr.crashNotifierContainer.state = uiconst.UI_NORMAL




class EveShowSourceWindow(uicls.Window):
    __guid__ = 'form.EveShowSourceWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.MakeUnstackable()
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, height=2)
        self.sr.browserPaneContainer = uicls.Container(name='browserPane', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        bp = browser.BrowserPane(parent=self.sr.browserPaneContainer, padding=(6, 6, 6, 6), align=uiconst.TOALL, state=uiconst.UI_NORMAL)
        bp.Startup()
        self.sr.browserPane = bp
        fillContainer = uicls.Container(name='browserBackground', parent=bp.parent, align=uiconst.TOALL, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        uicls.Fill(parent=fillContainer, color=(0.0, 0.0, 0.0, 1.0))
        self.browserSession = browser.BrowserSession()
        self.browserSession.Startup('viewSource', browserEventHandler=self)
        self.browserSession.SetBrowserSurface(bp.GetSurface(), self.sr.browserPane._OnSurfaceReady)
        self.browserSession.SetViewSourceMode(True)
        self.sr.browserPane.browserSession = self.browserSession
        self.sizeChanged = False
        self.sr.browserPane.ResizeBrowser()



    def BrowseTo(self, url = None, *args, **kwargs):
        self.SetCaption(mls.UI_SHARED_BROWSERHTMLSOURCEOF % url)
        self.browserSession.BrowseTo(url=url, *args)



    def OnResizeUpdate(self, *args):
        if not self.sizeChanged:
            uthread.new(self.DoResizeBrowser)
            self.sizeChanged = True



    def DoResizeBrowser(self):
        blue.pyos.synchro.Sleep(250)
        if self and self.sr and self.sr.browserPane:
            self.sr.browserPane.ResizeBrowser()
        self.sizeChanged = False



    def OnClose_(self, *args):
        self.sr.browserPane.browserSession = None
        self.browserSession.Cleanup()
        self.browserSession = None




