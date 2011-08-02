import uicls
import blue
import uiconst
import uix
import form
import uthread
import uiutil

class WindowStack(uicls.WindowStackCore):
    __guid__ = 'uicls.WindowStack'

    def Check(self, updatewnd = 0, autoselecttab = 1, checknone = 0):
        if self is None or self.destroyed:
            return 
        if checknone and len(self.sr.content.children) == 0:
            sm.GetService('window').UnregisterStack(self.name)
            self.SelfDestruct()
            return 
        self.SetMinWH()
        tabs = []
        label = ''
        someoneunkillable = 0
        allLite = True
        for wnd in self.sr.content.children:
            if wnd is None or wnd.destroyed:
                continue
            tabs.append([wnd.GetCaption(),
             wnd,
             self,
             wnd])
            wnd.HideHeader()
            wnd.HideBackground()
            if not wnd.IsPinned():
                allLite = False
            wnd.state = uiconst.UI_PICKCHILDREN
            label = label + wnd.GetCaption() + '-'
            if not wnd._killable:
                someoneunkillable = 1

        sm.GetService('window').ToggleLiteWindowAppearance(self, allLite)
        if someoneunkillable:
            self.MakeUnKillable()
        else:
            self.MakeKillable()
        if len(tabs):
            if len(label):
                label = label[:-1]
            self.sr.tabs.Flush()
            maintabs = uicls.TabGroup(parent=self.sr.tabs, name='tabparent', groupID=self.name, tabs=tabs, autoselecttab=autoselecttab)
            maintabs.rightMargin = 80
            alltabs = maintabs.GetTabs()
            if alltabs:
                for i in xrange(len(alltabs)):
                    tab = alltabs[i]
                    wnd = self.sr.content.children[i]
                    tab.GetMenu = wnd.GetMenu
                    tab.SetIcon(wnd.headerIconNo, 14, getattr(wnd.sr.headerIcon, 'hint', ''), getattr(wnd.sr.headerIcon, 'GetMenu', None))

                self.SetCaption(label)



    def OnPin_(self, *args):
        for wnd in self.sr.content.children:
            if wnd is None or wnd.destroyed:
                continue
            wnd._SetPinned(self.IsPinned())




    def OnUnpin_(self, *args):
        for wnd in self.sr.content.children:
            if wnd is None or wnd.destroyed:
                continue
            wnd._SetPinned(self.IsPinned())




    def RemoveWnd(self, wnd, grab, correctpos = 1, idx = 0, dragging = 0, check = 1):
        if wnd.parent != self.sr.content:
            return 
        if hasattr(wnd, 'OnTabSelect'):
            uthread.worker('WindowStack::RemoveWnd', wnd.OnTabSelect)
        if self.IsPinned():
            sm.GetService('window').ToggleLiteWindowAppearance(wnd, True)
        wnd._detaching = True
        uiutil.Transplant(wnd, self.parent, idx)
        wnd.sr.stack = None
        wnd.sr.tab = None
        wnd.align = uiconst.RELATIVE
        wnd.state = uiconst.UI_NORMAL
        wnd.grab = grab
        wnd.width = wnd._fixedWidth or self.width
        wnd.height = wnd._fixedHeight or self.height
        if dragging:
            uthread.new(wnd.BeginDrag)
        wnd.ShowHeader()
        wnd.ShowBackground()
        wnd.sr.resizers.state = uiconst.UI_PICKCHILDREN
        if correctpos:
            wnd.left = uicore.uilib.x - grab[0]
            wnd.top = uicore.uilib.y - grab[1]
        if check:
            self.Check()
        wnd.RegisterStackID()
        wnd._detaching = False
        wnd._dragging = dragging
        if len(self.sr.content.children) == 1 and not self.IsCollapsed():
            w = self.sr.content.children[0]
            (aL, aT, aW, aH,) = self.GetAbsolute()
            (x, y,) = (aL, aT)
            self.RemoveWnd(w, (0, 0), 1, 1, check=0)
            (w.left, w.top,) = (x, y)
            return 
        if len(self.sr.content.children) == 0:
            self.sr.tabs.Close()
            self.SelfDestruct()



    def Detach(self, wnd, grab):
        if settings.user.windows.Get('lockwhenpinned', 0) and self.IsPinned():
            return 0
        return uicls.WindowStackCore.Detach(self, wnd, grab)



    def GetCollapsedHeight(self):
        return self.sr.tabs.height + 4




