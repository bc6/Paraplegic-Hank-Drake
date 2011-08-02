import uthread
import uicls
import uiutil
import uiconst

class WindowStackCore(uicls.Window):
    __guid__ = 'uicls.WindowStackCore'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.sr.tabs = uicls.Container(parent=self.sr.maincontainer, name='__tabs', align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, pos=(0, 0, 0, 20), idx=0)
        self._detaching = 0
        self._inserting = 0



    def Prepare_LoadingIndicator_(self):
        self.sr.loadingIndicator = None
        self.sr.loadingBlock = None



    def Prepare_Header_(self):
        self.sr.captionParent = None
        self.sr.caption = None



    def UpdateCaption(self):
        self.SetCaption(self.GetCaption())



    def GetCaption(self, update = 1):
        caption = ''
        for wnd in self.sr.content.children:
            if wnd is not None and not wnd.destroyed:
                caption = '%s%s-' % (caption, wnd.GetCaption(update))

        if caption != '':
            return caption[:-1]
        return caption



    def GetCollapsedHeight(self):
        return self.sr.tabs.height + 10



    def OnCollapsed_(self, *args):
        self.sr.content.state = uiconst.UI_HIDDEN



    def OnExpanded_(self, *args):
        self.sr.content.state = uiconst.UI_NORMAL



    def OnClose_(self, *args):
        for wnd in self.sr.content.children[:]:
            if wnd is not None and not wnd.destroyed:
                wnd._SetOpen(False)
                wnd.SelfDestruct(0)




    def OnEndScale_(self, *args):
        for wnd in self.sr.content.children:
            if wnd.state == uiconst.UI_PICKCHILDREN:
                wnd.OnEndScale_(wnd)




    def InsertWnd(self, wnd, adjustlocation = 1, show = 0, hilite = 0):
        self._inserting = True
        (l, t, mywidth, myheight,) = self.GetAbsolute()
        if not len(self.sr.content.children) and adjustlocation:
            self.width = max(mywidth, wnd.width)
            self.height = max(myheight, wnd.height)
            self.left = wnd.left
            self.top = wnd.top
        if wnd.IsCollapsed():
            wnd.Expand()
        uiutil.Transplant(wnd, self.sr.content)
        wnd.align = uiconst.TOALL
        wnd.startingup = True
        wnd.left = wnd.top = wnd.width = wnd.height = 0
        wnd.startingup = False
        wnd.sr.stack = self
        wnd.sr.resizers.state = uiconst.UI_HIDDEN
        wnd.state = uiconst.UI_HIDDEN
        wnd.sr.loadingIndicator.Stop()
        self.Check(0, show != 1)
        if show:
            self.ShowWnd(wnd, hilite)
        wnd.CloseHeaderButtons()
        wnd.RegisterStackID(self)
        self.CleanupParent('snapIndicator')
        self._inserting = False



    def SetMinWH(self):
        allMinW = 0
        allMinH = 0
        for each in self.sr.content.children:
            allMinW = max(allMinW, each.minsize[0])
            allMinH = max(allMinH, each.minsize[1])

        if self.IsCollapsed():
            self.minsize = [allMinW, allMinH]
        else:
            self.SetMinSize([allMinW, allMinH])



    def ShowWnd(self, wnd, hilite = 0):
        tabparent = self.sr.tabs.children[0]
        if wnd not in self.sr.content.children or wnd is None or wnd.destroyed:
            return 
        if tabparent is None or tabparent.destroyed:
            return 
        tabparent.ShowPanel(wnd, hilite)



    def GetActiveWindow(self):
        if len(self.sr.tabs.children):
            tabparent = self.sr.tabs.children[0]
            if tabparent is None or tabparent.destroyed:
                return 
            return tabparent.GetVisible()



    def Detach(self, wnd, grab):
        if wnd is not None and not wnd.destroyed and not getattr(wnd, '_detaching', 0):
            self._detaching = True
            self.RemoveWnd(wnd, grab, 1, 0, 1)
            if not self.destroyed:
                self._detaching = False
            return 1



    def RemoveWnd(self, wnd, grab, correctpos = 1, idx = 0, dragging = 0, check = 1):
        if wnd.parent != self.sr.content:
            return 
        if hasattr(wnd, 'OnTabSelect'):
            uthread.worker('WindowStack::RemoveWnd', wnd.OnTabSelect)
        wnd._detaching = True
        uiutil.Transplant(wnd, self.parent, idx)
        wnd.sr.stack = None
        wnd.sr.tab = None
        wnd.align = uiconst.TOPLEFT
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
            self.SelfDestruct()



    def Check(self, updatewnd = 0, autoselecttab = 1, checknone = 0):
        if self is None or self.destroyed:
            return 
        if checknone and len(self.sr.content.children) == 0:
            self.SelfDestruct()
            return 
        self.SetMinWH()
        tabs = []
        label = ''
        someoneunkillable = False
        for wnd in self.sr.content.children:
            if wnd is None or wnd.destroyed:
                continue
            tabData = uiutil.Bunch()
            tabData.label = wnd.GetCaption() or wnd.windowID or '-'
            tabData.panel = wnd
            tabData.code = self
            tabData.args = wnd
            tabs.append(tabData)
            wnd.HideHeader()
            wnd.HideBackground()
            wnd.state = uiconst.UI_PICKCHILDREN
            label = label + wnd.GetCaption() + '-'
            if not wnd._killable:
                someoneunkillable = True

        if someoneunkillable:
            self.MakeUnKillable()
        else:
            self.MakeKillable()
        if len(tabs):
            if len(label):
                label = label[:-1]
            uiutil.Flush(self.sr.tabs)
            maintabs = self.GetTabGroupClass()(parent=self.sr.tabs, name='tabparent')
            maintabs.LoadTabs(tabs, autoselecttab)
            allTabs = maintabs.GetTabs()
            if allTabs:
                for i in xrange(len(allTabs)):
                    tab = allTabs[i]
                    wnd = self.sr.content.children[i]
                    tab.GetMenu = getattr(wnd, 'GetMenu', None)
                    tab.SetIcon(wnd.headerIconNo, getattr(wnd.sr.headerIcon, 'hint', ''), getattr(wnd.sr.headerIcon, 'GetMenu', None))

            self.SetCaption(label)



    def GetTabGroupClass(self):
        return uicls.TabGroup



    def GetMenu(self):
        menu = []
        if self._killable:
            menu.append((mls.UI_CMD_CLOSEWINDOWSTACK, self._CloseClick))
        if not self.sr.stack and self.IsMinimizable():
            if self.state == uiconst.UI_NORMAL:
                menu.append((mls.UI_CMD_MINIMIZEWINDOWSTACK, self.ToggleVis))
            else:
                menu.append((mls.UI_CMD_MAXIMIZEWINDOWSTACK, self.ToggleVis))
        return menu



    def IsMinimizable(self):
        for each in self.sr.content.children:
            if not each.IsMinimizable():
                return False

        return True



    def Load(self, wnd):
        if self.IsCollapsed() and not self._detaching and not self._inserting:
            self.Expand()
        for _wnd in self.sr.content.children:
            if _wnd is not wnd:
                _wnd.state = uiconst.UI_HIDDEN

        wnd.state = uiconst.UI_PICKCHILDREN



    def GetMinWidth(self, checkgroup = 1):
        trueMinWidth = self.minsize[0]
        for wnd in self.sr.content.children:
            trueMinWidth = max(wnd.GetMinWidth(), trueMinWidth)

        return trueMinWidth



    def GetMinHeight(self):
        trueMinHeight = self.minsize[1]
        for wnd in self.sr.content.children:
            trueMinHeight = max(wnd.GetMinHeight(), trueMinHeight)

        return trueMinHeight



    def OnStartMaximize_(self, *args):
        for wnd in self.sr.content.children:
            wnd.OnStartMaximize_(wnd)




    def OnEndMaximize_(self, *args):
        for wnd in self.sr.content.children:
            wnd.OnEndMaximize_(wnd)




    def OnStartMinimize_(self, *args):
        for wnd in self.sr.content.children:
            wnd.OnStartMinimize_(wnd)




    def OnEndMinimize_(self, *args):
        for wnd in self.sr.content.children:
            wnd.OnEndMinimize_(wnd)





