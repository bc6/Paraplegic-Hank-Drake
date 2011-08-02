import xtriui
import uix
import uiutil
import mathUtil
import uthread
import blue
import draw
import uicls
import uiconst

class ExpandableMenuContainer(uicls.Container):
    __guid__ = 'xtriui.ExpandableMenuContainer'

    def init(self):
        self.sizecallback = None
        self.multipleExpanded = False
        self.headerApperance = 'default'
        self.sr.menus = []
        self.sr.menusByLabel = {}



    def _OnClose(self):
        self.sizecallback = None
        self.sr.menus = None
        self.sr.menusByLabel = None



    def Load(self, menuData, prefsKey = None):
        self.singleton = bool(len(menuData) == 1)
        for data in menuData:
            em = xtriui.ExpandableMenu(parent=self, align=uiconst.TOTOP, height=18, state=uiconst.UI_NORMAL, name=data[0])
            em.prefsKey = prefsKey
            self.sr.menus.append(em)
            self.sr.menusByLabel[data[0]] = em
            em.Load(*data)

        if prefsKey and not self.multipleExpanded:
            active = settings.user.ui.Get('expandableMenu', {}).get(prefsKey, None)
            if active:
                for each in self.children:
                    if each.name == active:
                        uthread.new(each.Expand)

            else:
                uthread.new(self.children[0].Expand)



    def _OnResize(self):
        uicls.Container._OnResize(self)
        if self.multipleExpanded:
            (pl, pt, pw, ph,) = self.GetAbsolute()
            expanded = []
            totalHeight = 0
            for each in self.children:
                if each in self.sr.menus and each._expanded:
                    expanded.append(each)
                totalHeight += each.height

            diff = ph - totalHeight
            if diff and expanded:
                portion = diff / len(expanded)
                for each in expanded:
                    if totalHeight < ph:
                        newHeight = min(each._lastExpandedHeight, each.height + portion)
                    else:
                        newHeight = max(48, each.height + portion)
                    each.SetHeight(newHeight)




    def ExpandMenuByLabel(self, label):
        if label in self.sr.menusByLabel:
            self.sr.menusByLabel[label].Expand()




class ExpandableMenu(uicls.Container):
    __guid__ = 'xtriui.ExpandableMenu'

    def _OnResize(self):
        uicls.Container._OnResize(self)
        if not self._changing:
            self.sr.content.height = self.height - self.GetMinHeight() - self.sr.content.top



    def AddHeaderContent(self, content, hideOnMaximize = 1):
        self._hideHeaderContentOnMaximize = hideOnMaximize
        self.sr.headerContent = content
        self.sr.headerParent.children.insert(0, content)
        if self.sr.content.state == uiconst.UI_HIDDEN:
            self.sr.headerContent.opacity = 1.0
        elif hideOnMaximize:
            self.sr.headerContent.opacity = 0.0



    def Load(self, label, content, callback, dropCallback = None, maxHeight = None, headerContent = None, hideHeaderContentOnMaximize = 1, resizeAble = False):
        self._changing = False
        self._break = False
        self._expanded = False
        self._maxHeight = maxHeight or 128
        self._loaded = False
        self._lastExpandedHeight = None
        self._hideHeaderContentOnMaximize = hideHeaderContentOnMaximize
        self._resizeAble = resizeAble
        divider = xtriui.Divider(parent=self.parent, align=uiconst.TOTOP, height=4, state=uiconst.UI_NORMAL, name='divider')
        divider.Startup(self, 'height', 'y', 48, maxHeight or 256)
        divider.OnSizeChanged = self._OnSizeChanged
        divider.OnSizeChangeStarting = self._OnSizeChangeStarting
        self.sr.divider = divider
        headerParent = uicls.Container(parent=self, name='headerParent', align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=24)
        self.sr.headerParent = headerParent
        contentParent = uicls.Container(parent=self, name='contentParent', align=uiconst.TOALL, state=uiconst.UI_NORMAL, pos=(0, 1, 0, 1))
        self.sr.content = content
        self.sr.callback = callback
        if dropCallback:
            self.OnDropData = dropCallback
        t = uicls.Label(text='<b>' + label + '</b>', parent=headerParent, state=uiconst.UI_DISABLED, left=22, align=uiconst.CENTERLEFT)
        self.sr.headerLabel = t
        self._headerLabel = label
        expander = uicls.Icon(icon='ui_38_16_228', align=uiconst.CENTERLEFT)
        expander.SetAlpha(0.8)
        expander.state = uiconst.UI_DISABLED
        expander.left = 4
        headerParent.children.append(expander)
        self.sr.backgroundFrame = uicls.BumpedUnderlay(parent=headerParent, padding=(-1, 1, -1, 1))
        self.sr.expanderIcon = expander
        headerParent.height = max(20, t.textheight + 6)
        self._minHeight = headerParent.height
        if content:
            contentParent.children.append(content)
        if headerContent:
            self.AddHeaderContent(headerContent)
        if self.parent.multipleExpanded:
            current = settings.user.ui.Get('multipleExpandableMenu', {})
            if self.prefsKey in current and self.name in current[self.prefsKey]:
                (lastHeight, expanded,) = current[self.prefsKey][self.name]
                if expanded:
                    uthread.new(self.Expand, lastHeight)
                    return 
            else:
                uthread.new(self.Expand)
                return 
        self.Collapse(startup=1)
        self._loaded = True



    def SetHeader(self, newlabel, addon = 0, hint = None):
        if addon:
            newlabel = self._headerLabel + newlabel
        self.sr.headerLabel.text = '<b>' + newlabel + '</b>'
        if hint:
            self.sr.headerLabel.state = uiconst.UI_NORMAL
            self.sr.headerLabel.hint = hint
            self.sr.headerLabel.OnClick = self.OnClick
        else:
            self.sr.headerLabel.state = uiconst.UI_DISABLED



    def _OnSizeChangeStarting(self, *args):
        (pl, pt, pw, ph,) = self.parent.GetAbsolute()
        contentHeight = 0
        for each in self.parent.children:
            if each.align in (uiconst.TOTOP, uiconst.TOBOTTOM):
                contentHeight += each.height

        self.sr.divider.SetMinMax(maxValue=self.height + (ph - contentHeight))



    def _OnSizeChanged(self, *args):
        self._lastExpandedHeight = self.height
        if self.parent.multipleExpanded:
            self.Register()



    def OnClick(self, *args):
        if not self._changing:
            if self._expanded:
                self.Collapse()
            else:
                self.Expand()



    def Expand(self, lastHeight = None, time = None, *args):
        if self._changing:
            return 
        self._changing = True
        if not self.parent.multipleExpanded:
            for each in self.parent.children[:]:
                if isinstance(each, ExpandableMenu) and each != self:
                    uthread.new(each.Collapse)

        if self.sr.callback:
            self.sr.callback(not self._loaded)
        self.sr.content.align = uiconst.TOTOP
        self._loaded = True
        sh = self.height
        (pl, pt, pw, ph,) = self.parent.GetAbsolute()
        spreadData = []
        eh = self.GetMaxHeight()
        self.sr.expanderIcon.LoadIcon('ui_38_16_229')
        self.sr.content.state = uiconst.UI_NORMAL
        self.sr.content.height = eh - self.GetMinHeight() - self.sr.content.top
        if time == -1:
            self.height = sh + int(eh - sh)
            self.sr.content.opacity = 1.0
            if spreadData:
                for (menu, menuSh, menuEh,) in spreadData:
                    menu.SetHeight(menuSh - int(menuSh - menuEh))

            if self.parent.sizecallback:
                self.parent.sizecallback(self)
        else:
            (start, ndt,) = (blue.os.GetTime(), 0.0)
            time = time or 250.0
            while ndt != 1.0:
                ndt = max(ndt, min(blue.os.TimeDiffInMs(start) / time, 1.0))
                self.height = sh + int((eh - sh) * ndt)
                self.sr.content.opacity = 1.0 * ndt
                if self.sr.headerContent and self._hideHeaderContentOnMaximize:
                    self.sr.headerContent.opacity = 1.0 - 1.0 * ndt
                if spreadData:
                    for (menu, menuSh, menuEh,) in spreadData:
                        menu.SetHeight(menuSh - int((menuSh - menuEh) * ndt))

                if self.parent.sizecallback:
                    self.parent.sizecallback(self)
                blue.pyos.synchro.Yield()
                if self.destroyed or self._break:
                    break
                uiutil.Update(self.sr.content)

        if self.destroyed:
            return 
        self.height = eh
        self._changing = False
        self._break = False
        self._expanded = True
        self._lastExpandedHeight = self.height
        self.sr.content.opacity = 1.0
        if self.sr.headerContent and self._hideHeaderContentOnMaximize:
            self.sr.headerContent.opacity = 0.0
        if self._resizeAble:
            self.sr.divider.state = uiconst.UI_NORMAL
        else:
            self.sr.divider.state = uiconst.UI_DISABLED
        self.Register()



    def Register(self):
        if self.prefsKey:
            if self.parent.multipleExpanded:
                current = settings.user.ui.Get('multipleExpandableMenu', {})
                if self.prefsKey not in current:
                    current[self.prefsKey] = {}
                current[self.prefsKey][self.name] = (self._lastExpandedHeight, self._expanded)
                settings.user.ui.Set('multipleExpandableMenu', current)
            else:
                current = settings.user.ui.Get('expandableMenu', {})
                if self._expanded:
                    current[self.prefsKey] = self.name
                elif self.prefsKey in current and current[self.prefsKey] == self.name:
                    del current[self.prefsKey]
                settings.user.ui.Set('expandableMenu', current)



    def AlterHeight(self, amount):
        if self._expanded:
            self.height = max(self.GetMinHeight(), self.height + amount)
            self.sr.content.height = self.height - self.GetMinHeight() - self.sr.content.top
            return True



    def SetHeight(self, height):
        if self._expanded:
            self.height = height
            self.sr.content.height = self.height - self.GetMinHeight() - self.sr.content.top
            return True



    def Collapse(self, startup = 0):
        if self._changing:
            self._break = True
        self._changing = True
        self.sr.divider.state = uiconst.UI_DISABLED
        sh = self.height
        eh = self.GetMinHeight()
        (pl, pt, pw, ph,) = self.parent.GetAbsolute()
        spreadData = []
        self.sr.expanderIcon.LoadIcon('ui_38_16_228')
        if not startup:
            if self.sr.headerContent:
                sho = self.sr.headerContent.opacity
            (start, ndt,) = (blue.os.GetTime(), 0.0)
            time = 250.0
            while ndt != 1.0:
                ndt = max(ndt, min(blue.os.TimeDiffInMs(start) / time, 1.0))
                self.height = sh - int((sh - eh) * ndt)
                self.sr.content.opacity = 1.0 - 1.0 * ndt
                if self.sr.headerContent and self._hideHeaderContentOnMaximize:
                    self.sr.headerContent.opacity = mathUtil.Lerp(sho, 1.0, ndt)
                if spreadData:
                    for (menu, menuSh, menuEh,) in spreadData:
                        menu.SetHeight(menuSh - int((menuSh - menuEh) * ndt))

                if self.parent.sizecallback:
                    self.parent.sizecallback(self)
                blue.pyos.synchro.Yield()
                if self.destroyed or self._break:
                    break

        if self.destroyed:
            return 
        self._changing = False
        self._break = False
        self.height = eh
        self._expanded = False
        self.sr.content.state = uiconst.UI_HIDDEN
        self.sr.content.opacity = 0.0
        if self.sr.headerContent:
            self.sr.headerContent.opacity = 1.0
        if not startup:
            self.Register()



    def GetMinHeight(self):
        return self._minHeight



    def GetMaxHeight(self):
        if hasattr(self.sr.content, 'GetTotalHeight'):
            totalHeight = self.sr.content.top + self.sr.content.GetTotalHeight() + self.GetMinHeight() + 5
            return min(totalHeight, self._maxHeight)
        if hasattr(self.sr.content, 'GetContentHeight'):
            totalHeight = self.sr.content.top + self.sr.content.GetContentHeight() + self.GetMinHeight() + 5
            return min(totalHeight, self._maxHeight)
        if getattr(self.sr.content, 'sumContent', 0):
            totalHeight = self.sr.content.top + sum([ each.height for each in self.sr.content.children ]) + self.GetMinHeight()
            return min(totalHeight, self._maxHeight)
        return self._maxHeight




