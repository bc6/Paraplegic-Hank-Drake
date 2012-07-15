#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/browser/browserSession.py
import browserutil
import corebrowserutil
import blue
import uthread
import browserConst
import uiconst
import localization

class CoreBrowserSession():

    def Startup(self, sessionName, initialUrl = None, browserEventHandler = None, autoHandleLockdown = True, *args):
        self.name = sessionName
        self.statusText = ''
        self.securityInfo = 0
        self.awaitingTitle = True
        self.loading = False
        self.logToHistory = False
        self.cursorType = 0
        self.isViewSourceMode = False
        self.hint = ''
        self.currentUrl = initialUrl
        if self.currentUrl is None:
            self.currentUrl = 'about:blank'
        self.hidden = self.currentUrl == 'about:blank'
        self.browserEventHandler = browserEventHandler
        self.autoHandleLockdown = autoHandleLockdown
        self.AppStartup(sessionName, initialUrl, browserEventHandler, autoHandleLockdown)
        self.SetupBrowserSession(autoHandleLockdown=autoHandleLockdown)
        stat = blue.statistics.Find('browser/numRequests')
        if stat is None:
            stat = blue.CcpStatisticsEntry()
            stat.name = 'browser/numRequests'
            stat.resetPerFrame = False
            stat.type = 1
            blue.statistics.Register(stat)
        self.numRequestsStat = stat

    def SetupBrowserSession(self, autoHandleLockdown = True):
        self.browserHostManager = sm.GetService('browserHostManager').GetBrowserHost()
        self.browser = sm.GetService('browserHostManager').GetNewBrowserView()
        self.AttachBrowserCallbacks()
        if autoHandleLockdown:
            self.SetBrowserLockdown(sm.GetService('sites').IsBrowserInLockdown())
        self.AppSetupBrowserSession()

    def Cleanup(self):
        self.browserEventHandler = None
        self.browserHostManager = None
        if self.browser is not None:
            self.browser.OnChangeTargetURL = None
            self.browser.OnReceiveTitle = None
            self.browser.OnBeginNavigation = None
            self.browser.OnFinishLoading = None
            self.browser.OnBlockLoading = None
            self.browser.OnChangeCursor = None
            self.browser.OnBeginLoading = None
            self.browser.OnProcessSecurityInfo = None
            self.browser.OnChangeTooltip = None
            self.browser.OnChangeKeyboardFocus = None
            self.browser.OnJavascriptPrompt = None
            self.browser.OnOpenContextMenu = None
            self.browser.OnBrowserViewCrash = None
            self.browser.OnSurfaceReady = None
        sm.GetService('browserHostManager').ReleaseBrowserView(self.browser)
        self.browser = None
        self.AppCleanup()

    def _OnClientBrowserLockdownChange(self, *args):
        self.SetBrowserLockdown(sm.GetService('sites').IsBrowserInLockdown())

    def BrowseTo(self, url = None, *args, **kwargs):
        actualUrl = url
        if actualUrl is None:
            actualUrl = 'about:blank'
        if not self.IsAlive():
            self.ReattachBrowserSession()
        if type(actualUrl) is not str:
            actualUrl = actualUrl.encode('cp1252', 'ignore')
        self.browser.BrowseTo(actualUrl)

    def SetViewSourceMode(self, mode):
        self.isViewSourceMode = mode
        self.browser.SetViewSourceMode(mode)

    def HistoryBack(self, *args):
        if not self.IsAlive():
            self.ReattachBrowserSession()
        self.browser.HistoryOffset(-1)

    def HistoryForward(self, *args):
        if not self.IsAlive():
            self.ReattachBrowserSession()
        self.browser.HistoryOffset(1)

    def ReloadPage(self, *args):
        if self.currentUrl:
            if not self.IsAlive():
                self.ReattachBrowserSession()
        self.browser.BrowseTo(self.currentUrl)

    def StopLoading(self, *args):
        self.browser.Stop()

    def GoHome(self, *args):
        url = self.AppGetHomepage()
        self.BrowseTo(url)

    def GetCurrentURL(self):
        return self.currentUrl

    def OnSetFocus(self, *args):
        if self.browser and self.browser.alive:
            self.browser.Focus()

    def OnKillFocus(self, *args):
        if self.browser and self.browser.alive:
            self.browser.Unfocus()

    def _OnBeginNavigation(self, url, frameName):
        if frameName == '_blank':
            if self.browserEventHandler and hasattr(self.browserEventHandler, 'AddTab'):
                self.browserEventHandler.AddTab(tabUrl=url)
                return
        self.statusText = localization.GetByLabel('/Carbon/UI/Browser/BrowsingTo', url=url)
        self.loading = True
        self.numRequestsStat.Inc()
        if not frameName or frameName == 'main':
            self.awaitingTitle = True
            self.hidden = url == 'about:blank'
        if self.browserEventHandler and hasattr(self.browserEventHandler, '_OnBeginNavigation'):
            self.browserEventHandler._OnBeginNavigation(self, url, frameName)

    def _OnBeginLoading(self, url, frameName, status, mimeType):
        if not frameName or frameName == 'main':
            self.currentUrl = url
            if status > 0:
                self.logToHistory = True
        if self.browserEventHandler and hasattr(self.browserEventHandler, '_OnBeginLoading'):
            self.browserEventHandler._OnBeginLoading(self, url, frameName, status, mimeType)

    def _OnProcessSecurityInfo(self, securityInfo):
        self.securityInfo = securityInfo
        if self.browserEventHandler and hasattr(self.browserEventHandler, '_OnProcessSecurityInfo'):
            self.browserEventHandler._OnProcessSecurityInfo(self, securityInfo)

    def _OnFinishLoading(self):
        self.statusText = localization.GetByLabel('UI/Browser/FinishedLoading')
        self.loading = False
        if self.awaitingTitle:
            self._OnReceiveTitle(localization.GetByLabel('UI/Browser/UntitledPage'), '')
        if self.browserEventHandler and hasattr(self.browserEventHandler, '_OnFinishLoading'):
            self.browserEventHandler._OnFinishLoading(self)

    def _OnBlockLoading(self, statusCode):
        if statusCode == corebrowserutil.LoadErrors.ABORTED:
            return
        if statusCode == corebrowserutil.LoadErrors.BLACKLIST:
            self.AppOnBlockBlacklistSite()
            return
        if statusCode == corebrowserutil.LoadErrors.WHITELIST:
            self.AppOnBlockNonWhitelistSite()
            return
        self.AppOnBlockLoading(statusCode)

    def _OnReceiveTitle(self, title, frameName):
        if frameName == '' or frameName == 'main':
            self.title = title
            self.awaitingTitle = False
        if self.browserEventHandler and hasattr(self.browserEventHandler, '_OnReceiveTitle'):
            self.browserEventHandler._OnReceiveTitle(self, title, frameName)

    def _OnChangeTooltip(self, tooltip):
        if self.browserEventHandler and hasattr(self.browserEventHandler, '_OnChangeTooltip'):
            self.browserEventHandler._OnChangeTooltip(self, tooltip)

    def _OnChangeKeyboardFocus(self, focus):
        pass

    def _OnChangeTargetURL(self, url):
        if self.browserEventHandler and hasattr(self.browserEventHandler, '_OnChangeTargetURL'):
            self.browserEventHandler._OnChangeTargetURL(self, url)

    def _OnJavascriptPrompt(self, messageText):
        if self.browserEventHandler and hasattr(self.browserEventHandler, '_OnJavascriptPrompt'):
            self.browserEventHandler._OnJavascriptPrompt(self, messageText)

    def _OnOpenContextMenu(self, nodeType, linkUrl, imageUrl, pageUrl, frameUrl, editFlags):
        if not self.browser:
            return
        self.AppOnOpenContextMenu(nodeType, linkUrl, imageUrl, pageUrl, frameUrl, editFlags)

    def _OnChangeCursor(self, cursorType):
        self.cursorType = cursorType
        if self.browserEventHandler and hasattr(self.browserEventHandler, '_OnChangeCursor'):
            self.browserEventHandler._OnChangeCursor(self, cursorType)

    def _OnBrowserViewCrash(self):
        sm.GetService('browserHostManager').ReleaseBrowserView(self.browser)
        self.browser = corebrowserutil.CrashedBrowserViewHost()
        if self.browserEventHandler and hasattr(self.browserEventHandler, '_OnBrowserViewCrash'):
            self.browserEventHandler._OnBrowserViewCrash(self)

    def IsAlive(self):
        return self.browser is not None and self.browser.alive

    def SetBrowserLockdown(self, mode):
        self.browser.SetBrowserLockdown(mode)

    def AttachBrowserCallbacks(self):
        if self.browser is None:
            return
        self.browser.OnChangeTargetURL = self._OnChangeTargetURL
        self.browser.OnReceiveTitle = self._OnReceiveTitle
        self.browser.OnBeginNavigation = self._OnBeginNavigation
        self.browser.OnFinishLoading = self._OnFinishLoading
        self.browser.OnBlockLoading = self._OnBlockLoading
        self.browser.OnChangeCursor = self._OnChangeCursor
        self.browser.OnBeginLoading = self._OnBeginLoading
        self.browser.OnProcessSecurityInfo = self._OnProcessSecurityInfo
        self.browser.OnChangeTooltip = self._OnChangeTooltip
        self.browser.OnChangeKeyboardFocus = self._OnChangeKeyboardFocus
        self.browser.OnJavascriptPrompt = self._OnJavascriptPrompt
        self.browser.OnOpenContextMenu = self._OnOpenContextMenu
        self.browser.OnBrowserViewCrash = self._OnBrowserViewCrash

    def ReattachBrowserSession(self):
        if self.browser is None or not self.browser.alive:
            self.SetupBrowserSession()
            if self.browserEventHandler and hasattr(self.browserEventHandler, 'OnReattachBrowserSession'):
                self.browserEventHandler.OnReattachBrowserSession(self)

    def PerformCommand(self, cmd):
        self.browser.PerformCommand(cmd)
        if self.browserEventHandler is not None and hasattr(self.browserEventHandler, 'SetBrowserFocus'):
            self.browserEventHandler.SetBrowserFocus()

    def ViewSourceOfUrl(self, url):
        if self.browserEventHandler is not None and hasattr(self.browserEventHandler, 'ViewSourceOfUrl'):
            self.browserEventHandler.ViewSourceOfUrl(url)

    def LaunchNewTab(self, url):
        if self.browserEventHandler is not None and hasattr(self.browserEventHandler, 'AddTab'):
            self.browserEventHandler.AddTab(tabUrl=url)

    def CopyText(self, textToCopy):
        blue.pyos.SetClipboardData(textToCopy)

    def AddJavascriptCallback(self, callbackName, callbackFunction):
        if not self:
            return
        if not hasattr(self, 'browser') or self.browser is None:
            return
        self.browser.RegisterJavaScriptCallback(self.AppGetJavascriptObjectName(), callbackName, callbackFunction)

    def SetBrowserSize(self, width, height):
        if self.IsAlive():
            self.browser.SetSize(width, height)

    def SetBrowserSurface(self, browserSurface, browserSurfaceCallback):
        if self.IsAlive():
            self.browser.surface = browserSurface
            self.browser.OnSurfaceReady = browserSurfaceCallback

    def OnKeyDown(self, vkey, flag):
        if self.browser is not None and self.browser.alive:
            if vkey == uiconst.VK_RETURN:
                return
            self.browser.InjectKeyDown(vkey, flag)

    def OnKeyUp(self, vkey, flag):
        if self.browser is not None and self.browser.alive:
            self.browser.InjectKeyUp(vkey, flag)

    def OnChar(self, char, flag):
        if self.browser is not None and self.browser.alive:
            if char == uiconst.VK_RETURN:
                self.browser.InjectKeyDown(char, flag)
            self.browser.InjectChar(char, flag)
            return True

    def OnMouseMove(self, x, y, *args):
        if self.browser is not None and self.browser.alive:
            self.browser.InjectMouseMove(x, y)

    def OnMouseDown(self, *args):
        if self.browser is not None and self.browser.alive:
            self.browser.InjectMouseDown(args[0])

    def OnMouseUp(self, *args):
        if self.browser is not None and self.browser.alive:
            self.browser.InjectMouseUp(args[0])

    def OnMouseWheel(self, *args):
        if self.browser is not None and self.browser.alive:
            self.browser.InjectMouseWheel(uicore.uilib.dz)

    def AppStartup(self, sessionName, initialUrl, browserEventHandler, autoHandleLockdown):
        pass

    def AppCleanup(self):
        pass

    def AppGetJavascriptObjectName(self):
        return 'CCPBrowser'

    def AppSetupBrowserSession(self):
        pass

    def AppGetHomepage(self):
        return corebrowserutil.DefaultHomepage()

    def AppOnBlockLoading(self, statusCode):
        pass

    def AppOnBlockBlacklistSite(self):
        pass

    def AppOnBlockNonWhitelistSite(self):
        pass

    def AppOnOpenContextMenu(self, nodeType, linkUrl, imageUrl, pageUrl, frameUrl, editFlags):
        pass


exports = {'browser.CoreBrowserSession': CoreBrowserSession}