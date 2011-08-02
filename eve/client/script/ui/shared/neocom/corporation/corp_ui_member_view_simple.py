import blue
import uthread
import util
import xtriui
import uix
import form
import listentry
import lg
import draw
import uiconst
import uicls

class CorpMembersViewSimple(uicls.Container):
    __guid__ = 'form.CorpMembersViewSimple'
    __nonpersistvars__ = []

    def init(self):
        self.memberIDs = []
        self.viewPerPage = 10
        self.viewFrom = 0
        self.labelResults = None



    def CreateWindow(self):
        wndOutputArea = uicls.Container(name='output', parent=self, align=uiconst.TOTOP, height=48)
        captionparent = uicls.Container(name='captionparent', parent=wndOutputArea, align=uiconst.TOTOP, width=136, height=16)
        self.labelResults = uicls.Label(text='%s:' % mls.UI_CORP_RESULTS, parent=captionparent, align=uiconst.TOTOP, height=16, state=uiconst.UI_NORMAL)
        wndResultsBar = uicls.Container(name='results', parent=wndOutputArea, align=uiconst.TOTOP, height=16)
        wndNavBtns = uicls.Container(name='sidepar', parent=wndResultsBar, align=uiconst.TORIGHT, width=52)
        label = uicls.Container(name='text', parent=wndResultsBar, align=uiconst.TOLEFT, width=150, height=16)
        uicls.Label(text='%s:' % mls.UI_CORP_MEMBERSPERPAGE, parent=label, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        optlist = [['10', 10],
         ['25', 25],
         ['50', 50],
         ['100', 100],
         ['500', 500]]
        countcombo = uicls.Combo(label='', parent=wndResultsBar, options=optlist, name='membersperpage', callback=self.OnComboChange, width=146, pos=(150, 0, 0, 0))
        countcombo.sr.label.width = 200
        countcombo.sr.label.top = -16
        self.sr.MembersPerPage = countcombo
        btn = uix.GetBigButton(24, wndNavBtns, 0, 0)
        btn.OnClick = (self.Navigate, -1)
        btn.hint = mls.UI_GENERIC_PREVIOUS
        btn.state = uiconst.UI_HIDDEN
        btn.sr.icon.LoadIcon('ui_23_64_1')
        self.backBtn = btn
        btn = uix.GetBigButton(24, wndNavBtns, 24, 0)
        btn.OnClick = (self.Navigate, 1)
        btn.hint = mls.UI_GENERIC_VIEWMORE
        btn.state = uiconst.UI_HIDDEN
        btn.sr.icon.LoadIcon('ui_23_64_2')
        self.fwdBtn = btn
        uicls.Container(name='push', parent=wndOutputArea, align=uiconst.TOTOP, height=24)
        self.outputScrollContainer = uicls.Container(name='output', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.scroll = uicls.Scroll(parent=self.outputScrollContainer)



    def PopulateView(self, memberIDs = None):
        if memberIDs is not None:
            self.memberIDs = memberIDs
        self.labelResults.text = '%s: (%s)' % (mls.UI_CORP_RESULTS, len(self.memberIDs))
        nFrom = self.viewFrom
        nTo = nFrom + self.viewPerPage
        scrolllist = []
        memberIDsToDisplay = []
        for memberID in self.memberIDs:
            memberIDsToDisplay.append(memberID)

        cfg.eveowners.Prime(memberIDsToDisplay)
        totalNum = len(memberIDsToDisplay)
        if totalNum is not None:
            self.ShowHideBrowse(totalNum)
        for charID in memberIDsToDisplay:
            scrolllist.append(listentry.Get('User', {'charID': charID}))

        scrolllist = scrolllist[nFrom:nTo]
        self.scroll.Load(None, scrolllist)



    def OnComboChange(self, entry, header, value, *args):
        if entry.name == 'membersperpage':
            self.viewPerPage = value
            uthread.new(self.PopulateView)



    def Navigate(self, direction, *args):
        self.viewFrom = max(0, self.viewFrom + direction * self.viewPerPage)
        uthread.new(self.PopulateView)



    def ShowHideBrowse(self, totalNum):
        if self.viewFrom == 0:
            self.backBtn.state = uiconst.UI_HIDDEN
        else:
            self.backBtn.state = uiconst.UI_NORMAL
        if self.viewFrom + self.viewPerPage >= totalNum:
            self.fwdBtn.state = uiconst.UI_HIDDEN
        else:
            self.fwdBtn.state = uiconst.UI_NORMAL




