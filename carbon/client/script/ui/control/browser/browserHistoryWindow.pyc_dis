#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/browser/browserHistoryWindow.py
import uicls
import uiconst
import localization

class BrowserHistoryWindowCore(uicls.Window):
    __guid__ = 'uicls.BrowserHistoryWindowCore'
    default_windowID = 'BrowserHistoryWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetCaption(localization.GetByLabel('UI/Browser/BrowserHistory/BrowserHistoryCaption'))
        self.SetMinSize((400, 256))
        mainArea = self.GetMainArea()
        mainArea.clipChildren = 0
        mainArea.padding = 6
        clearHistory = uicls.Button(parent=mainArea, label=localization.GetByLabel('UI/Browser/BrowserHistory/ClearHistory'), func=self.ClearHistory, align=uiconst.BOTTOMRIGHT)
        self.scroll = uicls.Scroll(parent=mainArea, padBottom=clearHistory.height + 6)
        self.LoadHistory()

    def LoadHistory(self):
        self.selected = None
        scrolllist = []
        for each in sm.GetService('urlhistory').GetHistory():
            if each is not None:
                try:
                    label = localization.GetByLabel('UI/Browser/BrowserHistory/Row', title=each.title, url=each.url, date=each.ts)
                    scrolllist.append(uicls.ScrollEntryNode(decoClass=uicls.SE_Generic, label=label, retval=each, OnClick=self.OnEntryClick, OnDblClick=self.OnEntryDblClick))
                except:
                    continue

        self.scroll.sr.id = 'history_window_scroll_id'
        self.scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Browser/BrowserHistory/Title'), localization.GetByLabel('UI/Browser/BrowserHistory/URL'), localization.GetByLabel('UI/Browser/BrowserHistory/Date')])

    def OnEntryClick(self, node):
        self.selectedEntry = node.sr.node.retval

    def OnEntryDblClick(self, node):
        self.OnEntryClick(node)
        uicore.cmd.OpenBrowser(url=str(self.selectedEntry.url))

    def ClearHistory(self, *args):
        sm.GetService('urlhistory').ClearAllHistory()
        self.LoadHistory()
        sm.ScatterEvent('OnBrowserHistoryCleared')