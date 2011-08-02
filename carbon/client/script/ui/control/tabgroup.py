import log
import uthread
import uicls
import uiutil
import uiconst
import trinity
import sys
import uiutil
MAINCOLOR = (1.0,
 1.0,
 1.0,
 0.5)
MINTABGROUPHEIGHT = 20

class TabGroupCore(uicls.Container):
    __guid__ = 'uicls.TabGroupCore'
    default_name = 'tabgroup'
    default_align = uiconst.TOTOP
    default_height = 32
    default_clipChildren = 0
    default_state = uiconst.UI_PICKCHILDREN
    default_leftMargin = 8
    default_rightMargin = 20
    default_minTabsize = 32

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self._inited = 0
        self._iconOnly = False
        self.leftMargin = attributes.get('leftMargin', self.default_leftMargin)
        self.rightMargin = attributes.get('rightMargin', self.default_rightMargin)
        self.minTabsize = attributes.get('minTabsize', self.default_minTabsize)
        self.sr.tabsmenu = None
        self.sr.tabs = []
        self.sr.mytabs = []
        self.sr.stretch = None
        self._resizing = 0
        self._settingsID = None
        self.sr.linkedrows = []



    def Prepare_Tabsmenu_(self):
        tri = uicls.ImageButton(icon='ui_1_16_14', parent=self, align=uiconst.BOTTOMLEFT, idx=0, state=uiconst.UI_NORMAL, pos=(0, 2, 16, 16), idleIcon='ui_1_16_14', mouseoverIcon='ui_1_16_30', mousedownIcon='ui_1_16_46', getmenu=self.GetTabLinks, expandonleft=True)
        self.sr.tabsmenu = tri



    def Prepare_Fill_(self):
        stretch = uicls.Icon(icon='ui_1_16_96', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=MAINCOLOR, name='stretch', idx=0)
        stretch.rectWidth = 2
        self.sr.stretch = stretch
        right = uicls.Icon(icon='ui_1_16_96', parent=self, align=uiconst.TORIGHT, state=uiconst.UI_DISABLED, color=MAINCOLOR, name='right', width=self.rightMargin, idx=0, ignoreSize=True)
        self.sr.right = right



    def LoadTabs(self, tabs, autoselecttab = 1, settingsID = None, iconOnly = False, silently = False):
        self._iconOnly = iconOnly
        self.sr.tabs = []
        self.sr.mytabs = []
        self.sr.tabsmenu = None
        uiutil.Flush(self)
        left = uicls.Icon(icon='ui_1_16_93', parent=self, align=uiconst.TOLEFT, state=uiconst.UI_DISABLED, color=MAINCOLOR, name='left', idx=0, width=self.leftMargin, ignoreSize=True)
        self.Prepare_Fill_()
        maxTextHeight = 0
        for data in tabs:
            newtab = self.GetTabClass()(parent=self)
            self.sr.mytabs.append(newtab)
            newtab.Startup(self, data)
            self.sr.Set('%s_tab' % data.label, newtab)
            self.sr.tabs.append(newtab)
            maxTextHeight = max(maxTextHeight, newtab.sr.label.textheight)
            if newtab.sr.icon:
                maxTextHeight = max(maxTextHeight, newtab.sr.icon.height)

        lt = max(2, maxTextHeight / 12)
        for newtab in self.sr.tabs:
            newtab.height = max(MINTABGROUPHEIGHT, maxTextHeight + lt * 2)
            newtab.sr.label.top = lt

        self.height = max(MINTABGROUPHEIGHT, maxTextHeight + lt * 2)
        left.padTop = self.height - 16
        if self.sr.right:
            self.sr.right.padTop = self.height - 16
        if self.sr.stretch:
            self.sr.stretch.padTop = self.height - 16
        self._inited = 1
        self._settingsID = settingsID
        self.UpdateSizes()
        if autoselecttab:
            self.AutoSelect(silently)



    def GetTabClass(self):
        return uicls.Tab



    def GetTabLinks(self):
        return [ (each.sr.label.text, self.SelectByIdx, (self.sr.tabs.index(each),)) for each in self.sr.tabs ]



    def _OnSizeChange_NoBlock(self, width, height):
        uicls.Container._OnSizeChange_NoBlock(self, width, height)
        self.UpdateSizes((width, height))



    def UpdateSizes(self, absSize = None):
        if not self._inited:
            return 
        if not (self.sr and self.sr.mytabs):
            return 
        if self._resizing:
            return 
        self._resizing = 1
        if not uiutil.IsUnder(self, uicore.desktop):
            self._resizing = 0
            return 
        if absSize:
            (mw, mh,) = absSize
        else:
            (mw, mh,) = (self.displayWidth, self.displayHeight)
        if self.destroyed:
            return 
        totalTabWidth = sum([ each.sr.width for each in self.sr.mytabs ])
        totalSpace = mw - self.leftMargin - self.rightMargin
        needToShrink = max(0, totalTabWidth - totalSpace)
        totalShrunk = 0
        allMin = 1
        for each in self.sr.mytabs:
            portionOfFull = each.sr.width / float(totalTabWidth)
            each.portionOfFull = portionOfFull
            each.width = min(each.sr.width, max(self.minTabsize, each.sr.width - int(needToShrink * portionOfFull)))
            if each.width > self.minTabsize:
                allMin = 0
            totalShrunk += each.sr.width - each.width

        needMore = max(0, needToShrink - totalShrunk)
        while needMore and not allMin:
            _allMin = 1
            for each in self.sr.mytabs:
                if each.width > self.minTabsize:
                    each.width -= 1
                    needMore = max(0, needMore - 1)
                if each.width > self.minTabsize:
                    _allMin = 0

            allMin = _allMin

        left = self.leftMargin
        allMin = 1
        for each in self.sr.mytabs:
            each.left = left
            left += each.width
            if each.width != self.minTabsize:
                allMin = 0

        hidden = 0
        if self.sr.tabsmenu:
            self.sr.tabsmenu.Close()
            self.sr.tabsmenu = None
        active = self.GetVisible(1)
        i = 0
        i2 = 0
        totalWidth = 0
        totalVisible = 0
        countActive = None
        startHiddenIdx = None
        for each in self.sr.mytabs:
            if allMin and (hidden or each.left + each.width > totalSpace):
                if each == active:
                    countActive = i2
                each.state = uiconst.UI_HIDDEN
                if hidden == 0:
                    startHiddenIdx = i
                hidden = 1
                i2 += 1
            else:
                each.state = uiconst.UI_NORMAL
                totalWidth += each.width
                totalVisible += 1
            i += 1

        if allMin:
            if countActive is not None and startHiddenIdx is not None:
                totalWidth = 0
                totalVisible = 0
                i = 0
                for each in self.sr.mytabs:
                    if i <= countActive:
                        each.state = uiconst.UI_HIDDEN
                    elif startHiddenIdx <= i <= startHiddenIdx + countActive:
                        each.state = uiconst.UI_NORMAL
                    if each.state == uiconst.UI_NORMAL:
                        totalWidth += each.width
                        totalVisible += 1
                    i += 1

        self.totalTabWidth = totalWidth
        totalVisibleWidth = self.leftMargin
        leftover = max(0, totalSpace - totalWidth)
        for each in self.sr.mytabs:
            if each.state == uiconst.UI_NORMAL:
                each.left = totalVisibleWidth
                each.width = min(each.sr.width, max(self.minTabsize, each.width + leftover / totalVisible))
                totalVisibleWidth += each.width

        self.UpdateStretch(mw, totalVisibleWidth)
        if hidden:
            self.Prepare_Tabsmenu_()
            self.sr.tabsmenu.left = totalVisibleWidth
            self.sr.tabsmenu.state = uiconst.UI_NORMAL
        for tabgroup in self.sr.linkedrows:
            if tabgroup != self:
                tabgroup.UpdateSizes()

        self._resizing = 0



    def GetTabs(self):
        if not self.destroyed:
            return self.sr.tabs



    def UpdateStretch(self, fullWidth, totalVisibleWidth):
        if self.sr.stretch:
            self.sr.stretch.padLeft = totalVisibleWidth



    def GetTotalWidth(self):
        tw = sum([ each.sr.width for each in self.sr.mytabs ])
        return tw + self.leftMargin + self.rightMargin



    def AddRow(self, tabgroup):
        for tab in tabgroup.sr.tabs:
            tab.sr.tabgroup = self
            self.sr.tabs.append(tab)

        self.sr.linkedrows.append(tabgroup)
        if self not in self.sr.linkedrows:
            self.sr.linkedrows.append(self)
        tabgroup.UpdateSizes()



    def AutoSelect(self, silently = 0):
        if self.destroyed:
            return 
        idx = 0
        if self._settingsID:
            idx = settings.user.tabgroups.Get(self._settingsID, 0)
        uthread.new(self.sr.tabs[min(len(self.sr.tabs) - 1, idx)].Select, silently=silently)



    def SelectByIdx(self, idx, silent = 1):
        if len(self.sr.tabs) > idx:
            self.sr.tabs[idx].Select(silent)



    def SelectPrev(self):
        idx = self.GetSelectedIdx()
        if idx is None:
            return 
        idx -= 1
        if idx < 0:
            idx = len(self.sr.tabs) - 1
        self.SelectByIdx(idx, silent=False)



    def SelectNext(self):
        idx = self.GetSelectedIdx()
        if idx is None:
            return 
        idx += 1
        if idx > len(self.sr.tabs) - 1:
            idx = 0
        self.SelectByIdx(idx, silent=False)



    def GetSelectedIdx(self):
        for (idx, tab,) in enumerate(self.sr.tabs):
            if tab.IsSelected():
                return idx




    def ShowPanel(self, panel, *args):
        for tab in self.sr.tabs:
            if tab.sr.panel == panel:
                tab.Select(1)




    def ShowPanelByName(self, panelname, blink = 1):
        if panelname:
            tab = self.sr.Get('%s_tab' % panelname, None)
            if tab:
                tab.Select(1)
        else:
            log.LogWarn('Trying to show panel', panelname)



    def BlinkPanelByName(self, panelname, blink = 1):
        if panelname:
            tab = self.sr.Get('%s_tab' % panelname, None)
            if tab:
                tab.Blink(blink)
        else:
            log.LogWarn('Trying to blink panel', panelname)



    def _OnClose(self, *args):
        self.sr.callback = None
        self.sr.linkedrows = []
        for each in self.sr.tabs:
            if each is not None and not each.destroyed:
                each.Close()

        self.sr.tabs = None
        self.btns = []
        self.sr = None
        uicls.Container._OnClose(self, *args)



    def GetVisible(self, retTab = 0):
        if self is None or self.destroyed:
            return 
        for tab in self.sr.tabs:
            if tab.IsSelected():
                if retTab:
                    return tab
                return tab.sr.panel




    def ReloadVisible(self):
        tab = self.GetVisible(1)
        if tab:
            tab.Select(1)



    def GetSelectedArgs(self):
        for tab in self.sr.tabs:
            if tab.IsSelected():
                return tab.sr.args





class TabCore(uicls.Container):
    __guid__ = 'uicls.TabCore'
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.ignoreWndDrag = 1
        self.selecting = 0
        self.sr.icon = None
        self.sr.LoadTabCallback = None
        self.isTabStop = True
        self._detachallowed = False
        self.Prepare_()



    def Prepare_(self):
        self.sr.clipper = uicls.Container(parent=self, align=uiconst.TOALL, padding=(6, 0, 6, 0), clipChildren=True, state=uiconst.UI_PICKCHILDREN, name='labelClipper')
        self.sr.label = uicls.Label(parent=self.sr.clipper, left=1, fontsize=10, letterspace=1, uppercase=1, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, name='tabLabel')
        self.sr.underlay = uicls.Frame(parent=self, name='tabBackground', color=MAINCOLOR, frameConst=('ui_1_16_94', 7, 0))



    def Startup(self, tabgroup, data):
        self.sr.blink = uicls.Frame(parent=self, align=uiconst.TOTOP, height=1, padding=(2, 3, 2, 0), state=uiconst.UI_HIDDEN, blendMode=trinity.TR2_SBM_ADD, color=(0.5, 0.5, 0.5), frameConst=('res:/UI/Texture/Frames/FILLED_BLUR4.png', 6, -6, 1))
        self.sr.args = data.get('args', None)
        self.sr.grab = [0, 0]
        self.sr.tabgroup = tabgroup
        self._selected = False
        self.sr.panel = data.get('panel', None)
        self.sr.panelparent = data.get('panelparent', None)
        self.sr.code = data.get('code', None)
        self.sr.LoadTabCallback = data.get('LoadTabCallback', None)
        self.SetLabel(data.get('label', None))
        self.SetIcon(data.get('icon', None))
        self.Deselect(False)
        self.hint = data.get('hint', None)
        if hasattr(self.sr.code, 'GetTabMenu'):
            self.GetMenu = lambda : self.sr.code.GetTabMenu(self)
        if hasattr(self.sr.panel, 'sr'):
            self.sr.panel.sr.tab = self
        self.name = data.name or data.label



    def Confirm(self, *args):
        self.OnClick()



    def OnSetFocus(self, *args):
        pass



    def OnKillFocus(self, *etc):
        pass



    def SetLabel(self, label, hint = None):
        if self.destroyed:
            return 
        if self.sr.tabgroup._iconOnly:
            self.sr.label.text = ''
        else:
            self.sr.label.text = label.strip()
            self.sr.width = self.sr.label.width + self.sr.label.left + self.sr.label.parent.padLeft * 2
        self.sr.label.hint = hint
        self.hint = hint
        self.sr.tabgroup.UpdateSizes()



    def OnDropData(self, dragObj, nodes):
        if hasattr(self, 'OnTabDropData'):
            self.OnTabDropData(dragObj, nodes)
        elif hasattr(self.sr.panel, 'OnDropData'):
            self.sr.panel.OnDropData(dragObj, nodes)



    def Blink(self, onoff = 1):
        if self.sr.blink:
            if onoff:
                uicore.effect.BlinkSpriteRGB(self.sr.blink, 0.5, 0.5, 0.5, 750, 10000, passColor=1)
                self.sr.blink.state = uiconst.UI_DISABLED
            else:
                self.sr.blink.state = uiconst.UI_HIDDEN
                uicore.effect.StopBlink(self.sr.blink)
        self.blinking = onoff



    def SetIcon(self, iconNo, shiftLabel = 14, hint = None, menufunc = None):
        if self.sr.icon:
            self.sr.icon.Close()
        self.sr.hint = hint
        if iconNo is None:
            if self.sr.label:
                self.sr.label.left = 1
        else:
            self.sr.icon = uicls.Icon(icon=iconNo, parent=self, pos=(2, 3, 16, 16), align=uiconst.TOPLEFT, idx=0, state=uiconst.UI_DISABLED)
            if self.sr.label:
                self.sr.label.left = shiftLabel
            if menufunc:
                self.sr.icon.GetMenu = menufunc
                self.sr.icon.expandOnLeft = 1
                self.sr.icon.state = uiconst.UI_NORMAL
        self.sr.hint = hint
        self.sr.width = self.sr.label.textwidth + self.sr.label.left + self.sr.label.parent.padLeft * 2
        self.sr.tabgroup.UpdateSizes()



    def OnClick(self, *args):
        if self.selecting:
            return 
        uicore.registry.SetFocus(self)
        self.sr.tabgroup.state = uiconst.UI_DISABLED
        try:
            self.Select()

        finally:
            self.sr.tabgroup.state = uiconst.UI_PICKCHILDREN




    def IsSelected(self):
        return self._selected



    def Deselect(self, notify = True):
        self._selected = False
        self.ShowDeselected_()
        if self.sr.panel:
            self.sr.panel.state = uiconst.UI_HIDDEN
            if notify:
                if hasattr(self.sr.panel, 'OnTabDeselect'):
                    self.sr.panel.OnTabDeselect()
        if self.sr.panelparent:
            self.sr.panelparent.state = uiconst.UI_HIDDEN
            if notify:
                if hasattr(self.sr.panelparent, 'OnTabDeselect'):
                    self.sr.panelparent.OnTabDeselect()



    def ShowDeselected_(self):
        if self.sr.underlay:
            self.sr.underlay.LoadFrame(('ui_1_16_94', 7, 0))
        self.padTop = 1



    def ShowSelected_(self):
        if self.sr.underlay:
            self.sr.underlay.LoadFrame(('ui_1_16_95', 7, 0))
        self.padTop = 0



    def Select(self, silently = 0):
        if self.destroyed:
            return 
        self.selecting = 1
        self.Blink(0)
        if self is None or self.destroyed:
            self.selecting = 0
            self.sr.tabgroup.state = uiconst.UI_PICKCHILDREN
            return 
        if len(self.sr.tabgroup.sr.linkedrows):
            for tabgroup in self.sr.tabgroup.sr.linkedrows:
                if self in tabgroup.sr.mytabs:
                    continue
                uiutil.SetOrder(tabgroup, 0)

        for each in self.sr.tabgroup.sr.tabs:
            if each.IsSelected():
                if hasattr(self.sr.code, 'UnloadTabPanel'):
                    self.sr.code.UnloadTabPanel(each.sr.args, each.sr.panel, each.sr.tabgroup)
            if each == self:
                continue
            notify = True
            if each.sr.panel and each.sr.panel is self.sr.panel or each.sr.panelparent and each.sr.panelparent is self.sr.panelparent:
                notify = False
            each.Deselect(notify)

        self._selected = True
        self.ShowSelected_()
        if self.sr.panelparent:
            self.sr.panelparent.state = uiconst.UI_PICKCHILDREN
            if hasattr(self.sr.panelparent, 'OnTabSelect'):
                self.sr.panelparent.OnTabSelect()
        if self.sr.panel:
            self.sr.panel.state = uiconst.UI_PICKCHILDREN
            if hasattr(self.sr.panel, 'OnTabSelect'):
                self.sr.panel.OnTabSelect()
        err = None
        if self.sr.LoadTabCallback:
            try:
                self.sr.LoadTabCallback(self.sr.args, self.sr.panel, self.sr.tabgroup)

            finally:
                self.selecting = 0

        elif hasattr(self.sr.code, 'LoadTabPanel'):
            try:
                self.sr.code.LoadTabPanel(self.sr.args, self.sr.panel, self.sr.tabgroup)

            finally:
                self.selecting = 0

        elif getattr(self.sr.code, 'Load', None):
            try:
                self.sr.code.Load(self.sr.args)
            except (StandardError,) as err:
                log.LogException(toMsgWindow=0)
                sys.exc_clear()
                if self.destroyed:
                    return 
                wnd = uiutil.GetWindowAbove(self)
                if wnd and not wnd.destroyed:
                    wnd.HideLoad()
        if not silently:
            par = self.sr.panelparent or self.sr.panel
            if par:
                uthread.new(uicore.registry.SetFocus, par)
        if self.destroyed:
            return 
        if self.sr.tabgroup._settingsID:
            settings.user.tabgroups.Set(self.sr.tabgroup._settingsID, self.sr.tabgroup.sr.tabs.index(self))
        if self and not self.destroyed:
            self.sr.tabgroup.UpdateSizes()
            self.selecting = 0
        if err and isinstance(err, UserError):
            raise err



    def OnMouseDown(self, *args):
        self._detachallowed = 1
        (aL, aT, aW, aH,) = self.GetAbsolute()
        self.sr.grab = [uicore.uilib.x - aL, uicore.uilib.y - aT]



    def OnMouseUp(self, *args):
        if not self.destroyed and hasattr(self, 'sr'):
            self._detachallowed = 0



    def OnMouseMove(self, *args):
        if self._detachallowed and uicore.uilib.mouseTravel > 24 and hasattr(self.sr.code, 'Detach'):
            uicore.uilib.ReleaseCapture()
            uthread.new(self.DoDetach)



    def OnMouseEnter(self, *args):
        pass



    def OnMouseExit(self, *args):
        pass



    def DoDetach(self, *args):
        if self is not None and not self.destroyed:
            if self.sr.code.Detach(self.sr.panel, self.sr.grab):
                if self is not None and not self.destroyed:
                    self.Close()
            else:
                self._detachallowed = 0




