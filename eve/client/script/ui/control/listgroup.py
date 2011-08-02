import util
import uix
import uiutil
import form
import listentry
import uiconst
import uicls
import log

class VirtualGroupWindow(uicls.Window):
    __guid__ = 'form.VirtualGroupWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        node = attributes.node
        caption = attributes.caption or 'List window'
        self.SetScope('station_inflight')
        self.SetMinSize((200, 200))
        self.SetTopparentHeight(0)
        self.sr.data = node.copy()
        main = uiutil.GetChild(self, 'main')
        main.Flush()
        icon = getattr(self.sr.data, 'showicon', '')
        if icon == 'hide':
            self.SetCaption(caption)
            self.SetWndIcon('ui_9_64_14')
        elif icon and icon[0] == '_':
            self.SetWndIcon(icon[1:], 1, size=32)
            self.SetCaption(caption)
        else:
            self.SetCaption(caption)
            self.SetWndIcon('ui_22_32_29', 1, size=32)
            if icon:
                mainicon = uiutil.GetChild(self, 'mainicon')
                mainicon.LoadIcon(icon, ignoreSize=True)
                mainicon.SetSize(32, 32)
                mainicon.state = uiconst.UI_DISABLED
            else:
                self.SetWndIcon('ui_22_32_29', 1, size=32)
        self.sr.scroll = uicls.Scroll(name='scroll', parent=main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding), align=uiconst.TOALL)
        self.sr.scroll.sr.iconMargin = getattr(self.sr.data, 'iconMargin', 0)
        ignoreTabTrimming = util.GetAttrs(node, 'scroll', 'sr', 'ignoreTabTrimming') or 0
        self.sr.scroll.sr.ignoreTabTrimming = ignoreTabTrimming
        minColumnWidth = util.GetAttrs(node, 'scroll', 'sr', 'minColumnWidth') or {}
        self.sr.scroll.sr.minColumnWidth = minColumnWidth
        self.sr.scroll.sr.content.OnDropData = self.OnDropData



    def OnClose_(self, *args):
        self.sr.data = None



    def LoadContent(self, newNode = None, newCaption = None):
        if not self or self.destroyed:
            return 
        if newNode:
            self.sr.data = newNode.Copy()
        if newCaption:
            self.SetCaption(newCaption)
        if self.sr.data.GetSubContent:
            content = self.sr.data.GetSubContent(self.sr.data, 1)
        else:
            raise RuntimeError('LoadContent: WTF')
        if self.sr.data.scroll.sr.id:
            self.sr.scroll.sr.id = '%s_%s' % (self.sr.data.scroll.sr.id, self.sr.data.id)
        self.sr.scroll.sr.fixedColumns = self.sr.data.scroll.sr.fixedColumns.copy()
        self.sr.scroll.Load(contentList=content, headers=self.sr.data.scroll.GetColumns(), fixedEntryHeight=self.sr.data.scroll.sr.fixedEntryHeight, scrolltotop=0)



    def OnDropData(self, dragObj, nodes):
        if getattr(self.sr.data, 'DropData', None):
            self.sr.data.DropData(self.sr.data.id, nodes)
            return 
        ids = []
        myListGroupID = self.sr.data.id
        for node in nodes:
            if node.__guid__ not in self.sr.data.get('allowGuids', []):
                log.LogWarn('dropnode.__guid__ has to be listed in group.node.allowGuids', node.__guid__, getattr(self.sr.data, 'allowGuids', []))
                continue
            if not node.Get('itemID', None):
                log.LogWarn('dropitem data has to have itemID')
                continue
            currentListGroupID = node.Get('listGroupID', None)
            ids.append((node.itemID, currentListGroupID, myListGroupID))

        for (itemID, currentListGroupID, myListGroupID,) in ids:
            if currentListGroupID and itemID:
                uicore.registry.RemoveFromListGroup(currentListGroupID, itemID)
            uicore.registry.AddToListGroup(myListGroupID, itemID)

        uicore.registry.ReloadGroupWindow(myListGroupID)
        if getattr(self.sr.data, 'RefreshScroll', None):
            self.sr.data.RefreshScroll()




class ListGroup(uicls.SE_ListGroupCore):
    __guid__ = 'listentry.Group'
    __notifyevents__ = ['OnUIColorsChanged']

    def Startup(self, *etc):
        self.sr.expander = uicls.Icon(parent=self, pos=(3, 1, 11, 11), name='expander', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/expanderDown.png', align=uiconst.TOPLEFT)
        self.sr.expander.OnClick = self.Toggle
        self.sr.expander.SetAlpha(0.8)
        self.sr.icon = uicls.Icon(parent=self, pos=(4, 1, 16, 16), name='icon', state=uiconst.UI_DISABLED, icon='ui_22_32_28', align=uiconst.RELATIVE, ignoreSize=True)
        self.sr.selection = uicls.Fill(parent=self, padding=(0, 1, 0, 2), name='selection', state=uiconst.UI_HIDDEN, color=(1.0, 1.0, 1.0, 0.25))
        self.sr.topLine = uicls.Line(parent=self, align=uiconst.TOTOP)
        self.sr.labelClipper = uicls.Container(parent=self, align=uiconst.TOALL, pos=(0,
         0,
         const.defaultPadding,
         0), clipChildren=1)
        self.sr.label = uicls.Label(text='', parent=self.sr.labelClipper, left=5, state=uiconst.UI_DISABLED, singleline=1, idx=0, align=uiconst.CENTERLEFT)
        self.sr.fill = uicls.Fill(parent=self, padTop=-1, padBottom=-1)
        self.OnUIColorsChanged()
        self.sr.mainLinePar = uicls.Container(parent=self, name='mainLinePar', align=uiconst.TOALL, idx=0, pos=(0, 0, 0, -15), state=uiconst.UI_DISABLED)
        self.sr.bottomLineContainer = uicls.Container(parent=self.sr.mainLinePar, name='bottomLineContainer', align=uiconst.TOBOTTOM, height=16)
        self.sr.bottomLineLeft = uicls.Icon(icon='ui_73_16_38', parent=self.sr.bottomLineContainer, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
        self.sr.bottomLineArrow = uicls.Icon(icon='ui_73_16_39', parent=self.sr.bottomLineContainer, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
        bottomLineStretch = uicls.Icon(icon='ui_73_16_38', parent=self.sr.bottomLineContainer, align=uiconst.TOALL, state=uiconst.UI_NORMAL, ignoreSize=True)
        sm.RegisterNotify(self)



    def OnUIColorsChanged(self, *args):
        (color, bgColor, comp, compsub,) = sm.GetService('window').GetWindowColors()
        if not self.destroyed:
            self.sr.fill.color.SetRGB(*comp)



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = uix.GetTextHeight(node.label, autoWidth=1, singleLine=1) + 4
        return node.height



    def Load(self, node):
        self.sr.node = node
        self.sr.id = node.id
        self.sr.subitems = node.get('subitems', []) or node.get('groupItems', [])
        self.UpdateLabel()
        self.hint = node.Get('hint', '')
        sublevel = node.Get('sublevel', 0)
        self.sr.expander.left = 16 * sublevel + 3
        self.sr.label.left = 20 + 16 * sublevel + 20
        self.sr.icon.left = 16 * sublevel + 20
        self.sr.node.selectable = node.Get('selectGroup', 0)
        self.sr.selection.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][node.Get('selected', 0)]
        self.sr.expander.state = [uiconst.UI_NORMAL, uiconst.UI_HIDDEN][node.Get('hideExpander', 0)]
        self.sr.fill.state = [uiconst.UI_DISABLED, uiconst.UI_HIDDEN][node.Get('hideFill', False)]
        self.sr.topLine.state = [uiconst.UI_DISABLED, uiconst.UI_HIDDEN][node.Get('hideTopLine', False)]
        self.UpdateBottomLine()
        if self.sr.expander.state == uiconst.UI_HIDDEN:
            self.sr.labelClipper.width = 0
        for (k, v,) in node.Get('labelstyle', {}).iteritems():
            setattr(self.sr.label, k, v)

        icon = node.Get('showicon', '')
        iconID = node.Get('iconID', None)
        if iconID:
            self.sr.icon.LoadIcon(iconID, ignoreSize=True)
            self.sr.icon.SetSize(16, 16)
            self.sr.icon.state = uiconst.UI_DISABLED
        elif icon == 'hide':
            self.sr.icon.state = uiconst.UI_HIDDEN
            self.sr.label.left -= 20
        elif icon and icon[0] == '_':
            self.sr.icon.LoadIcon(icon[1:], ignoreSize=True)
            self.sr.icon.SetSize(16, 16)
            self.sr.icon.state = uiconst.UI_DISABLED
        elif icon:
            self.sr.icon.LoadIcon(icon, ignoreSize=True)
            self.sr.icon.SetSize(16, 16)
        else:
            self.sr.icon.LoadIcon('ui_22_32_29', ignoreSize=True)
            self.sr.icon.SetSize(16, 16)
        self.sr.icon.state = uiconst.UI_DISABLED
        self.sr.icon.width = 16
        if self.sr.expander.state == uiconst.UI_HIDDEN:
            self.sr.label.left -= 16
            self.sr.icon.left -= 18
        if node.panel is not self or self is None:
            return 
        self.ShowOpenState(uicore.registry.GetListGroupOpenState(self.sr.id, default=node.Get('openByDefault', False)))
        self.RefreshGroupWindow(0)



    def OnDblClick(self, *args):
        if self.sr.node.Get('OnDblClick', None):
            self.sr.node.OnDblClick(self)
            return 
        if self.sr.node.Get('BlockOpenWindow', 0):
            return 
        self.RefreshGroupWindow(create=1)



    def RefreshGroupWindow(self, create):
        if self.sr.node:
            wnd = sm.GetService('window').GetWindow(unicode(self.sr.node.id), create=create, decoClass=form.VirtualGroupWindow, node=self.sr.node, caption=self.sr.node.label.replace('<t>', '-'))
            if wnd:
                wnd.LoadContent(self.sr.node, newCaption=self.sr.node.label)
                if create:
                    wnd.Maximize()
                if not self or self.destroyed:
                    return 
                node = self.sr.node
                if node.open:
                    self.Toggle()



    def GetNoItemEntry(self):
        return listentry.Get('Generic', {'label': mls.UI_GENERIC_NOITEM,
         'sublevel': self.sr.node.Get('sublevel', 0) + 1})



    def GetMenu(self):
        m = []
        if not self.sr.node.Get('BlockOpenWindow', 0):
            wnd = sm.GetService('window').GetWindow(unicode(self.sr.node.id))
            if wnd:
                m = [(mls.UI_CMD_SHOWWINDOW, self.RefreshGroupWindow, (1,))]
            else:
                m = [(mls.UI_CMD_OPENGROUPWINDOW, self.RefreshGroupWindow, (1,))]
        node = self.sr.node
        expandable = node.Get('expandable', 1)
        if expandable:
            if not node.open:
                m += [(mls.UI_CMD_EXPAND, self.Toggle, ())]
            else:
                m += [(mls.UI_CMD_COLLAPSE, self.Toggle, ())]
        if node.Get('state', None) != 'locked':
            m += [(mls.UI_CMD_CHANGELABEL, self.ChangeLabel)]
            m += [(mls.UI_CMD_DELETEFOLDER, self.DeleteFolder)]
        if node.Get('MenuFunction', None):
            cm = node.MenuFunction(node)
            m += cm
        return m



    def GetNewGroupName(self):
        return uix.NamePopup(mls.UI_GENERIC_TYPEINNEWNAME, mls.UI_GENERIC_TYPEINNEWNAMEFOLDER)



    def CloseWindow(self, windowID):
        wnd = sm.GetService('window').GetWindow(windowID)
        if wnd:
            wnd.SelfDestruct()



    def OnDragEnter(self, dragObj, drag, *args):
        if self.sr.node.Get('DragEnterCallback', None):
            self.sr.node.DragEnterCallback(self, drag)
        elif drag and getattr(drag[0], '__guid__', None) in self.sr.node.Get('allowGuids', []) + ['xtriui.DragIcon']:
            self.sr.selection.state = uiconst.UI_DISABLED



    def OnDragExit(self, dragObj, drag, *args):
        if self.sr.selection and not self.sr.node.selected:
            self.sr.selection.state = uiconst.UI_HIDDEN



    def ShowOpenState(self, open_):
        if self.sr.expander:
            if open_:
                self.sr.expander.LoadIcon('ui_38_16_229')
            else:
                self.sr.expander.LoadIcon('ui_38_16_228')



    def UpdateBottomLine(self):
        sublevel = self.sr.node.Get('sublevel', 0)
        isOpen = uicore.registry.GetListGroupOpenState(self.sr.id, default=self.sr.node.Get('openByDefault', True))
        self.sr.bottomLineLeft.state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][(self.sr.node.Get('hasArrow', False) and isOpen)]
        self.sr.bottomLineArrow.state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][(self.sr.node.Get('hasArrow', False) and isOpen)]
        self.sr.bottomLineLeft.width = sublevel * 16




