import form
import listentry
import service
import uiconst
import uiutil
import util
import xtriui
import uicls

class HistoryWindow(uicls.Window):
    __guid__ = 'form.BrowserHistoryWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.SetCaption(mls.UI_CMD_BROWSER_HISTORY)
        self.SetMinSize((400, 256))
        self.sr.main.clipChildren = 0
        self.sr.footerBar = uicls.Container(name='statBar', parent=self.sr.main, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 22), clipChildren=1)
        self.sr.scroll = uicls.Scroll(parent=self.sr.main)
        self.LoadHistory()
        self.sr.clearHistory = uicls.Button(parent=self.sr.footerBar, label=mls.UI_GENERIC_CLEARHISTORY, func=self.ClearHistory, align=uiconst.TOPRIGHT)



    def LoadHistory(self):
        self.selected = None
        scrolllist = []
        for each in sm.GetService('urlhistory').GetHistory():
            if each is not None:
                try:
                    label = '%s<t>%s<t>%s' % (each.title, each.url, util.FmtDate(each.ts, 'll'))
                    scrolllist.append(listentry.Get('Generic', {'label': label,
                     'retval': each,
                     'OnClick': self.OnEntryClick,
                     'OnDblClick': self.OnEntryDblClick}))
                except:
                    continue

        self.sr.scroll.sr.id = 'history_window_scroll_id'
        self.sr.scroll.Load(contentList=scrolllist, headers=[mls.UI_GENERIC_TITLE, mls.UI_GENERIC_URL, mls.DATE])



    def OnEntryClick(self, node):
        self.selectedEntry = node.sr.node.retval



    def OnEntryDblClick(self, node):
        self.OnEntryClick(node)
        brw = sm.GetService('cmd').OpenBrowser(url=str(self.selectedEntry.url))



    def ClearHistory(self, *args):
        sm.GetService('urlhistory').ClearAllHistory()
        self.LoadHistory()
        sm.ScatterEvent('OnBrowserHistoryCleared')
        sm.ScatterEvent('OnBrowserHistoryCleared')




