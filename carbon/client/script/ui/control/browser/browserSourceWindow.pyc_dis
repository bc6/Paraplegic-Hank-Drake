#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/browser/browserSourceWindow.py
import uiconst
import uicls
import uiutil
import uthread
import blue
import browser
import localization

class BrowserSourceWindowCore(uicls.Window):
    __guid__ = 'uicls.BrowserSourceWindowCore'
    default_windowID = 'BrowserSourceWindowCore'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.MakeUnstackable()
        mainArea = self.GetMainArea()
        bp = browser.BrowserPane(parent=mainArea, padding=6, align=uiconst.TOALL, state=uiconst.UI_NORMAL)
        bp.Startup()
        self.browserPane = bp
        uicls.Fill(parent=mainArea, padding=const.defaultPadding, color=(0.0, 0.0, 0.0, 1.0))
        self.browserSession = browser.BrowserSession()
        self.browserSession.Startup('viewSource', browserEventHandler=self)
        self.browserSession.SetBrowserSurface(bp.GetSurface(), self.browserPane._OnSurfaceReady)
        self.browserSession.SetViewSourceMode(True)
        self.browserPane.browserSession = self.browserSession
        self.sizeChanged = False
        self.browserPane.ResizeBrowser()
        url = attributes.browseTo
        if url is not None:
            self.BrowseTo(url)

    def BrowseTo(self, url = None, *args, **kwargs):
        try:
            self.SetCaption(localization.GetByLabel('UI/Browser/HTMLSourceOf', url=url))
        except:
            self.SetCaption(url)

        self.browserSession.BrowseTo(url=url, *args)

    def OnResizeUpdate(self, *args):
        if not self.sizeChanged:
            uthread.new(self.DoResizeBrowser)
            self.sizeChanged = True

    def DoResizeBrowser(self):
        blue.pyos.synchro.SleepWallclock(250)
        if getattr(self, 'browserPane', None):
            self.browserPane.ResizeBrowser()
        self.sizeChanged = False

    def _OnClose(self, *args):
        self.browserPane.browserSession = None
        self.browserSession.Cleanup()
        self.browserSession = None