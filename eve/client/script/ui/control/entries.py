import xtriui
import uix
import uiutil
import util
import blue
import listentry
import base
import uthread
import uiconst
import uicls
import form
import log
import trinity
import bluepy
import localization
import localizationUtil
import fontConst
events = ('OnClick',
 'OnMouseDown',
 'OnMouseUp',
 'OnDblClick',
 'OnMouseHover')

class Space(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.Space'
    __params__ = ['height']

    def Load(self, node):
        self.sr.node = node



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = node.height
        return node.height




class Generic(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.Generic'
    __params__ = ['label']

    def _OnClose(self):
        for eventName in events:
            setattr(self.sr, eventName, None)

        uicls.SE_BaseClassCore._OnClose(self)



    def Startup(self, *args):
        self.sr.label = uicls.EveLabelMedium(text='', parent=self, left=5, state=uiconst.UI_DISABLED, color=None, singleline=1, align=uiconst.CENTERLEFT)
        self.sr.line = uicls.Container(name='lineparent', align=uiconst.TOBOTTOM, parent=self, height=1)
        self.sr.mainline = uicls.Fill(parent=self.sr.line)
        self.sr.selection = uicls.Fill(parent=self, padding=(1, 1, 1, 1), color=(1.0, 1.0, 1.0, 0.25))
        self.sr.hilite = uicls.Fill(parent=self, padding=(1, 1, 1, 1), color=(1.0, 1.0, 1.0, 0.25))
        for eventName in events:
            setattr(self.sr, eventName, None)

        self.sr.infoicon = None



    def Load(self, node):
        self.sr.node = node
        data = node
        self.sr.label.singleline = bool(data.Get('singleline', True))
        self.UpdateHint()
        self.confirmOnDblClick = data.Get('confirmOnDblClick', 0)
        self.typeID = data.Get('typeID', None)
        self.itemID = data.Get('itemID', None)
        if node.selected:
            self.sr.selection.state = uiconst.UI_DISABLED
        else:
            self.sr.selection.state = uiconst.UI_HIDDEN
        self.sr.hilite.state = uiconst.UI_HIDDEN
        if node.showinfo and node.typeID:
            if not self.sr.infoicon:
                self.sr.infoicon = uicls.InfoIcon(size=16, left=1, top=1, parent=self, idx=0, align=uiconst.TOPRIGHT)
                self.sr.infoicon.OnClick = self.ShowInfo
            self.sr.infoicon.state = uiconst.UI_NORMAL
        elif self.sr.infoicon:
            self.sr.infoicon.state = uiconst.UI_HIDDEN
        for eventName in events:
            if data.Get(eventName, None):
                setattr(self.sr, eventName, data.Get(eventName, None))

        self.sr.label.left = 5 + 16 * data.Get('sublevel', 0)
        if data.Get('fontsize', None):
            self.sr.label.fontsize = data.fontsize
        else:
            self.sr.label.fontsize = fontConst.EVE_MEDIUM_FONTSIZE
        if data.Get('hspace', None):
            self.sr.label.letterspace = data.hspace
        else:
            self.sr.label.letterspace = 0
        self.sr.label.text = data.label
        if data.Get('fontColor', None) is not None:
            self.sr.label.color.SetRGB(*data.fontColor)
        else:
            self.sr.label.color.SetRGB(1.0, 1.0, 1.0, 1.0)
        if data.Get('hideLines', None):
            self.sr.line.state = uiconst.UI_HIDDEN



    def UpdateHint(self):
        data = self.sr.node
        hint = data.hint
        if hint is None:
            self.hint = uiutil.ReplaceTags(data.label, (('<t>', '<br>'), ('<right>', '')))
        else:
            self.hint = hint



    def GetHeight(_self, *args):
        (node, width,) = args
        if node.vspace is not None:
            node.height = uix.GetTextHeight(node.label, singleLine=1) + node.vspace
        else:
            node.height = uix.GetTextHeight(node.label, singleLine=1) + 4
        return node.height



    def OnMouseHover(self, *args):
        if self.sr.node and self.sr.node.Get('OnMouseHover', None):
            self.sr.node.OnMouseHover(self)



    def OnMouseEnter(self, *args):
        if self.sr.node:
            eve.Message('ListEntryEnter')
            self.sr.hilite.state = uiconst.UI_DISABLED
            if self.sr.node.Get('OnMouseEnter', None):
                self.sr.node.OnMouseEnter(self)



    def OnMouseExit(self, *args):
        if self.sr.node:
            self.sr.hilite.state = uiconst.UI_HIDDEN
            if self.sr.node.Get('OnMouseExit', None):
                self.sr.node.OnMouseExit(self)



    def OnClick(self, *args):
        if util.GetAttrs(self, 'sr', 'node'):
            if self.sr.node.Get('selectable', 1):
                self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if not self or self.destroyed:
                return 
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)



    def OnDblClick(self, *args):
        if self.sr.node:
            self.sr.node.scroll.SelectNode(self.sr.node)
            if self.sr.node.Get('OnDblClick', None):
                if isinstance(self.sr.node.OnDblClick, tuple):
                    func = self.sr.node.OnDblClick[0]
                    func(self, *self.sr.node.OnDblClick[1:])
                else:
                    self.sr.node.OnDblClick(self)
            elif getattr(self, 'confirmOnDblClick', None):
                uicore.registry.Confirm()
            elif self.sr.node.Get('typeID', None):
                self.ShowInfo()



    def OnMouseDown(self, *args):
        uicls.SE_BaseClassCore.OnMouseDown(self, *args)
        if self.sr.node and self.sr.node.Get('OnMouseDown', None):
            self.sr.node.OnMouseDown(self)



    def OnMouseUp(self, *args):
        uicls.SE_BaseClassCore.OnMouseUp(self, *args)
        if not self or self.destroyed:
            return 
        if self.sr.node and self.sr.node.Get('OnMouseUp', None):
            self.sr.node.OnMouseUp(self)



    def ShowInfo(self, *args):
        if self.sr.node.Get('isStation', 0):
            stationinfo = sm.RemoteSvc('stationSvc').GetStation(self.itemID)
            sm.GetService('info').ShowInfo(stationinfo.stationTypeID, self.itemID)
            return 
        if self.sr.node.Get('typeID', None):
            abstractinfo = self.sr.node.Get('abstractinfo', None)
            sm.GetService('info').ShowInfo(self.sr.node.Get('typeID', None), self.sr.node.Get('itemID', None), abstractinfo=abstractinfo)



    def GetMenu(self):
        if not self.sr.node.Get('ignoreRightClick', 0):
            self.OnClick()
        if hasattr(self, 'sr'):
            if self.sr.node and self.sr.node.Get('GetMenu', None):
                return self.sr.node.GetMenu(self)
            if getattr(self, 'itemID', None) or getattr(self, 'typeID', None):
                return sm.GetService('menu').GetMenuFormItemIDTypeID(getattr(self, 'itemID', None), getattr(self, 'typeID', None))
        return []



    def HideLines(self):
        self.sr.line.state = uiconst.UI_HIDDEN



    def OnDropData(self, dragObj, nodes):
        data = self.sr.node
        if data.OnDropData:
            data.OnDropData(dragObj, nodes)



    def DoSelectNode(self, toggle = 0):
        self.sr.node.scroll.GetSelectedNodes(self.sr.node, toggle=toggle)




class StatusBar(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.StatusBar'
    __params__ = []

    def Startup(self, *args):
        uicls.Line(parent=self, name='white', align=uiconst.TOBOTTOM)
        self.sr.icon = uicls.Sprite(parent=self, name='icon', state=uiconst.UI_HIDDEN, align=uiconst.TOLEFT)
        self.sr.infoicon = uicls.InfoIcon(size=16, left=2, top=2, parent=self, idx=0, align=uiconst.TOPRIGHT, state=uiconst.UI_HIDDEN)
        container = uicls.Container(parent=self, padding=(0, 0, 0, 1), name='container', state=uiconst.UI_DISABLED, align=uiconst.TOALL)
        bar = uicls.Container(parent=container, pos=(5, 12, 84, 11), name='bar', state=uiconst.UI_NORMAL, align=uiconst.RELATIVE)
        uicls.Frame(parent=bar, color=(1.0, 1.0, 1.0, 0.5))
        progress = uicls.Container(parent=bar, width=20, name='progress', state=uiconst.UI_NORMAL, align=uiconst.TORIGHT)
        uicls.Fill(parent=bar, color=(1.0, 1.0, 1.0, 0.5))
        self.sr.label = uicls.EveLabelSmall(text='', parent=container, idx=0, left=6, top=2, singleline=1, state=uiconst.UI_NORMAL)
        self.sr.text = uicls.EveLabelMedium(text='', parent=container, idx=1, left=95, top=12, singleLine=1, state=uiconst.UI_NORMAL)
        self.sr.progress = progress



    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = node.label
        self.sr.text.text = '%i/%i' % (node.status, node.total)
        self.sr.progress.parent.top = self.sr.label.top + self.sr.label.textheight
        self.sr.text.top = self.sr.progress.parent.top - 2
        if node.status != 0 or node.total != 0:
            self.sr.progress.width = int(80 - 80 * (node.status / float(node.total)))
            self.sr.progress.state = uiconst.UI_DISABLED
        else:
            self.sr.progress.state = uiconst.UI_HIDDEN
        if node.iconID is not None:
            self.sr.icon.LoadIcon(node.iconID)
            self.sr.icon.state = uiconst.UI_DISABLED
        else:
            self.sr.icon.state = uiconst.UI_HIDDEN



    def GetHeight(_self, *args):
        (node, width,) = args
        labelheight = uix.GetTextHeight(node.label, fontsize=fontConst.EVE_SMALL_FONTSIZE, singleLine=1, uppercase=1)
        textheight = uix.GetTextHeight('%i/%i' % (node.status, node.total), fontsize=fontConst.EVE_MEDIUM_FONTSIZE, singleLine=1)
        node.height = 2 + labelheight + textheight
        return node.height




class Item(Generic):
    __guid__ = 'listentry.Item'
    __params__ = ['itemID', 'typeID', 'label']

    def Startup(self, *args):
        listentry.Generic.Startup(self, args)
        self.sr.label.left = 8
        self.sr.infoicon = uicls.InfoIcon(size=16, left=2, top=2, parent=self, idx=0, align=uiconst.TOPRIGHT)
        self.sr.infoicon.OnClick = self.ShowInfo
        self.sr.icon = uicls.Icon(parent=self, pos=(1, 2, 24, 24), align=uiconst.TOPLEFT, idx=0)
        self.sr.techIcon = uicls.Sprite(name='techIcon', parent=self, left=1, width=16, height=16, idx=0)
        for eventName in events:
            setattr(self.sr, eventName, None)




    def Load(self, node):
        self.sr.node = node
        data = node
        self.itemID = data.itemID
        self.typeID = data.typeID
        self.isStation = data.Get('isStation', 0)
        self.confirmOnDblClick = data.Get('confirmOnDblClick', 0)
        if node.selected:
            self.sr.selection.state = uiconst.UI_DISABLED
        else:
            self.sr.selection.state = uiconst.UI_HIDDEN
        self.sr.hilite.state = uiconst.UI_HIDDEN
        self.sr.techIcon.state = uiconst.UI_HIDDEN
        if data.getIcon and self.typeID:
            self.sr.icon.state = uiconst.UI_NORMAL
            self.sr.icon.LoadIconByTypeID(typeID=self.typeID, size=24, ignoreSize=True, isCopy=getattr(data, 'isCopy', False))
            self.sr.icon.SetSize(24, 24)
            self.sr.label.left = self.height + 4
            techSprite = uix.GetTechLevelIcon(self.sr.techIcon, 1, self.typeID)
        else:
            self.sr.icon.state = uiconst.UI_HIDDEN
            self.sr.label.left = 8
        self.sr.label.text = data.label
        self.hint = data.Get('hint', '') or data.label
        if self.typeID or self.isStation:
            self.sr.infoicon.state = uiconst.UI_NORMAL
        else:
            self.sr.infoicon.state = uiconst.UI_HIDDEN
        for eventName in events:
            if data.Get(eventName, None):
                setattr(self.sr, eventName, data.Get(eventName, None))

        if node.Get('selected', 0):
            self.sr.selection.state = uiconst.UI_DISABLED
        else:
            self.sr.selection.state = uiconst.UI_HIDDEN



    def GetHeight(_self, *args):
        (node, width,) = args
        node.height = 29
        return node.height



    def GetMenu(self):
        if not self.sr.node.Get('ignoreRightClick', 0):
            self.OnClick()
        if self.sr.node.Get('GetMenu', None):
            return self.sr.node.GetMenu(self)
        if self.itemID:
            return sm.GetService('menu').GetMenuFormItemIDTypeID(self.itemID, self.typeID, ignoreMarketDetails=0)
        if self.typeID:
            return sm.GetService('menu').GetMenuFormItemIDTypeID(None, self.typeID, ignoreMarketDetails=0)
        return []




class AutoPilotItem(Item):
    __guid__ = 'listentry.AutoPilotItem'

    def Startup(self, *args):
        listentry.Item.Startup(self, args)
        self.sr.posIndicatorCont = uicls.Container(name='posIndicator', parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=2)
        self.sr.posIndicatorNo = uicls.Fill(parent=self.sr.posIndicatorCont, color=(0.61, 0.05, 0.005, 1.0))
        self.sr.posIndicatorNo.state = uiconst.UI_HIDDEN
        self.sr.posIndicatorYes = uicls.Fill(parent=self.sr.posIndicatorCont, color=(1.0, 1.0, 1.0, 0.5))
        self.sr.posIndicatorYes.state = uiconst.UI_HIDDEN



    def GetDragData(self, *args):
        if not self.sr.node.canDrag:
            return 
        self.sr.node.scroll.SelectNode(self.sr.node)
        return [self.sr.node]



    def OnDropData(self, dragObj, nodes, *args):
        self.sr.posIndicatorNo.state = uiconst.UI_HIDDEN
        self.sr.posIndicatorYes.state = uiconst.UI_HIDDEN
        if util.GetAttrs(self, 'parent', 'OnDropData'):
            node = nodes[0]
            if self.sr.node.canDrag:
                if util.GetAttrs(node, 'panel'):
                    self.parent.OnDropData(dragObj, nodes, orderID=self.sr.node.orderID)



    def OnDragEnter(self, dragObj, nodes, *args):
        node = nodes[0]
        if self.sr.node.canDrag:
            self.sr.posIndicatorYes.state = uiconst.UI_DISABLED
        else:
            self.sr.posIndicatorNo.state = uiconst.UI_DISABLED



    def OnDragExit(self, *args):
        self.sr.posIndicatorNo.state = uiconst.UI_HIDDEN
        self.sr.posIndicatorYes.state = uiconst.UI_HIDDEN




class Push(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.Push'
    __params__ = []

    def Startup(self, *etc):
        pass



    def Load(self, node):
        self.sr.node = node



    def GetHeight(_self, *args):
        (node, width,) = args
        node.height = node.Get('height', 0) or 12
        return node.height




class Divider(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.Divider'
    __params__ = []

    def Startup(self, *etc):
        self.sr.line = uicls.Container(name='lineparent', align=uiconst.TOBOTTOM, parent=self, height=1)
        uicls.Fill(parent=self.sr.line)



    def Load(self, node):
        self.sr.node = node
        self.sr.line.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][self.sr.node.Get('line', 1)]



    def GetHeight(_self, *args):
        (node, width,) = args
        node.height = node.Get('height', 0) or 12
        return node.height




class Slider(Generic):
    __guid__ = 'listentry.Slider'
    __params__ = ['cfgname', 'retval']
    __update_on_reload__ = 1

    def Startup(self, *args):
        listentry.Generic.Startup(self, args)
        mainpar = uicls.Container(name='listentry_slider', align=uiconst.TOTOP, width=0, height=10, left=0, top=14, state=uiconst.UI_NORMAL, parent=self)
        mainpar._OnResize = self.Resize
        slider = xtriui.Slider(parent=mainpar, align=uiconst.TOPLEFT, top=20, state=uiconst.UI_NORMAL)
        lbl = uicls.EveLabelSmall(text='', parent=mainpar, width=200, left=5, top=-12)
        lbl.name = 'label'
        self.sr.lbl = lbl
        slider.SetSliderLabel = self.SetSliderLabel
        slider.GetSliderHint = lambda idname, dname, value: localizationUtil.FormatNumeric(int(value))
        self.sr.slider = slider



    def Resize(self):
        if self.sr.slider.valueproportion:
            self.sr.slider.SlideTo(self.sr.slider.valueproportion)



    def Load(self, args):
        listentry.Generic.Load(self, args)
        data = self.sr.node
        slider = self.sr.slider
        lbl = self.sr.lbl
        if data.Get('hint', None) is not None:
            lbl.hint = data.hint
        if data.Get('getvaluefunc', None) is not None:
            slider.GetSliderValue = data.getvaluefunc
        if data.Get('endsetslidervalue', None) is not None:
            slider.EndSetSliderValue = data.endsetslidervalue
        slider.Startup(data.Get('sliderID', 'slider'), data.Get('minValue', 0), data.Get('maxValue', 10), data.Get('config', None), data.Get('displayName', None), data.Get('increments', None), data.Get('usePrefs', 0), data.Get('startVal', None))



    def SetSliderLabel(self, label, idname, dname, value):
        self.sr.lbl.text = dname
        if self.sr.node.Get('setsliderlabel', None) is not None:
            self.sr.node.setsliderlabel(label, idname, dname, value)



    def GetHeight(_self, *args):
        (node, width,) = args
        node.height = node.Get('height', 0) or 32
        return node.height




class Checkbox(Generic):
    __guid__ = 'listentry.Checkbox'
    __params__ = ['cfgname', 'retval']

    def Startup(self, *args):
        listentry.Generic.Startup(self, args)
        cbox = uicls.Checkbox(align=uiconst.CENTERLEFT)
        cbox.left = 6
        cbox.width = 16
        cbox.height = 16
        cbox.data = {}
        cbox.OnChange = self.CheckBoxChange
        self.children.insert(0, cbox)
        self.sr.checkbox = cbox
        self.sr.checkbox.state = uiconst.UI_DISABLED
        self.sr.label.top = 0
        self.sr.label.SetAlign(uiconst.CENTERLEFT)



    def Load(self, args):
        listentry.Generic.Load(self, args)
        data = self.sr.node
        self.sr.checkbox.SetGroup(data.Get('group', None))
        self.sr.checkbox.SetChecked(data.checked, 0)
        self.sr.checkbox.data.update({'key': data.cfgname,
         'retval': data.retval})
        self.sr.label.text = data.label
        self.sr.checkbox.left = 6 + 16 * data.Get('sublevel', 0)
        self.sr.label.left = 24 + 16 * data.Get('sublevel', 0)



    def CheckBoxChange(self, *args):
        self.sr.node.checked = self.sr.checkbox.checked
        self.sr.node.OnChange(*args)



    def OnClick(self, *args):
        if not self or self.destroyed:
            return 
        if self.sr.checkbox.checked:
            eve.Message('DiodeDeselect')
        else:
            eve.Message('DiodeClick')
        if self.sr.checkbox.groupName is None:
            self.sr.checkbox.SetChecked(not self.sr.checkbox.checked)
            return 
        for node in self.sr.node.scroll.GetNodes():
            if node.Get('__guid__', None) in ('listentry.Checkbox', 'listentry.ImgCheckbox') and node.Get('group', None) == self.sr.checkbox.groupName:
                if node.panel:
                    node.panel.sr.checkbox.SetChecked(0, 0)
                    node.checked = 0
                else:
                    node.checked = 0

        if not self.destroyed:
            self.sr.checkbox.SetChecked(1)



    def GetHeight(_self, *args):
        (node, width,) = args
        node.height = max(19, uix.GetTextHeight(node.label, singleLine=1) + 4)
        return node.height



    def OnCharSpace(self, enteredChar, *args):
        uthread.pool('checkbox::OnChar', self.OnClick, self)
        return 1




class Progress(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.Progress'
    __params__ = ['header', 'startTime', 'duration']

    def Startup(self, args):
        header = uicls.EveLabelMedium(text='', parent=self, left=2, top=2, state=uiconst.UI_DISABLED)
        p = uicls.Container(name='gauge', parent=self, width=84, height=14, left=6, top=20, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0)
        t = uicls.EveLabelSmall(text='', parent=p, left=6, top=1, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        f = uicls.Fill(parent=p, align=uiconst.RELATIVE, width=1, height=10, left=2, top=2, color=(1.0, 1.0, 1.0, 0.25))
        uicls.Frame(parent=p, color=(1.0, 1.0, 1.0, 0.5))
        self.sr.progress = p
        self.sr.progressFill = f
        self.sr.progressHeader = header
        self.sr.progressText = t



    def Load(self, node):
        self.sr.node = node
        self.sr.progressHeader.text = node.header
        import uthread
        uthread.new(self.LoadProgress)



    def LoadProgress(self):
        if not hasattr(self, 'sr'):
            return 
        startTime = self.sr.node.startTime
        duration = self.sr.node.duration
        maxWidth = self.sr.progress.width - self.sr.progressFill.left * 2
        self.sr.progress.state = uiconst.UI_DISABLED
        while self and not self.destroyed:
            msFromStart = max(0, blue.os.TimeDiffInMs(startTime, blue.os.GetSimTime()))
            portion = 1.0
            if msFromStart:
                portion -= float(msFromStart) / duration
            self.sr.progressFill.width = int(maxWidth * portion)
            diff = max(0, duration - msFromStart)
            self.sr.progressText.text = localization.GetByLabel('UI/Control/Entries/Seconds', seconds=diff / 1000.0)
            if msFromStart > duration:
                break
            blue.pyos.synchro.Yield()




    def GetHeight(_self, *args):
        (node, width,) = args
        node.height = 40
        return node.height



MINCOLWIDTH = 16

class ColumnLine(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.ColumnLine'

    @bluepy.CCP_STATS_ZONE_METHOD
    def Startup(self, args):
        self._clicks = 0
        self.sr.clickTimer = None
        self.sr.columns = []
        self.sr.bottomLine = None
        self.sr.selection = uicls.Fill(parent=self, padTop=1, color=(0.0, 1.0, 0.0, 0.125), state=uiconst.UI_HIDDEN)
        self.sr.hilite = uicls.Fill(parent=self, padTop=1, color=(1.0, 0.0, 0.0, 0.125), state=uiconst.UI_HIDDEN)
        self.cursor = 0



    @bluepy.CCP_STATS_ZONE_METHOD
    def Load(self, node):
        self.LoadLite(node)
        if node.Get('showBottomLine', 0):
            if self.sr.bottomLine:
                self.sr.bottomLine.state = uiconst.UI_DISABLED
            else:
                self.sr.bottomLine = uicls.Line(parent=self, idx=0, align=uiconst.TOBOTTOM)
        elif self.sr.bottomLine:
            self.sr.bottomLine.state = uiconst.UI_HIDDEN
        node.needReload = 0
        if node.Get('selectable', 1):
            if node.Get('selected', 0):
                self.sr.selection.state = uiconst.UI_DISABLED
            else:
                self.sr.selection.state = uiconst.UI_HIDDEN
        else:
            self.sr.selection.state = uiconst.UI_HIDDEN
        if uicore.uilib.mouseOver is self:
            self.sr.hilite.state = uiconst.UI_DISABLED
        else:
            self.sr.hilite.state = uiconst.UI_HIDDEN
        if self.sr.Get('overlay', None):
            if self.sr.overlay in self.children:
                self.children.remove(self.sr.overlay)
            self.sr.overlay = None
        if node.Get('overlay', None) is not None:
            uiutil.Transplant(node.overlay, self, 0)
            self.sr.overlay = node.overlay
        self.UpdateOverlay()
        self.UpdateTriangles()



    def _OnSizeChange_NoBlock(self, *args):
        self.UpdateOverlay()



    def UpdateOverlay(self):
        if self.sr.Get('overlay', None):
            customTabstops = listentry.GetCustomTabstops(self.sr.node.columnID)
            if customTabstops:
                totalColWidth = sum(customTabstops)
            else:
                totalColWidth = sum([ each.width for each in self.sr.columns ])
            self.sr.overlay.left = max(totalColWidth, self.width - self.sr.overlay.width)



    def LoadLite(self, node):
        i = 0
        for each in node.texts:
            self.LoadColumn(i, each)
            i += 1

        for each in self.sr.columns[i:]:
            each.Close()

        self.sr.columns = self.sr.columns[:i]
        self.UpdateColumnOrder(0)



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateColumnOrder(self, updateEntries = 1, onlyVisible = False):
        displayOrder = settings.user.ui.Get('columnDisplayOrder_%s' % self.sr.node.columnID, None) or [ i for i in xrange(len(self.sr.columns)) ]
        customTabstops = listentry.GetCustomTabstops(self.sr.node.columnID)
        if displayOrder is not None and len(displayOrder) == len(self.sr.columns):
            left = 0
            for columnIdx in displayOrder:
                colWidth = customTabstops[columnIdx]
                col = self.sr.columns[columnIdx]
                col.left = left
                col.width = colWidth
                if not self.sr.node.Get('editable', 0):
                    col.width -= 2
                left += colWidth

        self.sr.node.customTabstops = customTabstops
        if updateEntries:
            associates = self.FindAssociatingEntries()
            for node in associates:
                if node.panel and (not onlyVisible or onlyVisible and node.panel.state != uiconst.UI_HIDDEN):
                    node.panel.UpdateColumnOrder(0)
                    node.panel.UpdateOverlay()




    def OnMouseEnter(self, *args):
        if self.sr.node:
            eve.Message('ListEntryEnter')
            if self.sr.node.Get('hilightable', 1):
                self.sr.hilite.state = uiconst.UI_DISABLED
            if self.sr.node.Get('OnMouseEnter', None):
                self.sr.node.OnMouseEnter(self)



    def OnMouseExit(self, *args):
        if self.sr.node:
            if self.sr.node.Get('hilightable', 1):
                self.sr.hilite.state = uiconst.UI_HIDDEN
            if self.sr.node.Get('OnMouseExit', None):
                self.sr.node.OnMouseExit(self)



    def OnClick(self, *args):
        if self.sr.node:
            if self.sr.node.Get('selectable', 1):
                self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)



    def GetMenu(self):
        if self.sr.node and self.sr.node.Get('scroll', None) and getattr(self.sr.node.scroll, 'GetSelectedNodes', None):
            self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        if self.sr.node and self.sr.node.Get('GetMenu', None):
            return self.sr.node.GetMenu(self)
        if getattr(self, 'itemID', None) or getattr(self, 'typeID', None):
            return sm.GetService('menu').GetMenuFormItemIDTypeID(getattr(self, 'itemID', None), getattr(self, 'typeID', None))
        return []



    def LoadColumn(self, idx, textOrObject):
        node = self.sr.node
        if len(self.sr.columns) > idx:
            col = self.sr.columns[idx]
            col.height = self.height
        else:
            col = uicls.Container(name='column_%s' % idx, parent=self, align=uiconst.TOPLEFT, height=self.height, clipChildren=1, state=uiconst.UI_PICKCHILDREN, idx=0)
            col.sr.textCtrl = uicls.Label(text='', parent=col, fontsize=self.sr.node.Get('fontsize', 12), letterspace=self.sr.node.Get('letterspace', 0), uppercase=self.sr.node.Get('uppercase', 0), state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, singleline=1)
            col.sr.textCtrl.left = self.sr.node.Get('padLeft', 6)
            col.sr.editHandle = None
            col.sr.triangle = None
            col.columnIdx = idx
            col.OnDblClick = (self.OnHeaderDblClick, col)
            col.OnClick = (self.OnHeaderClick, col)
            col.GetMenu = lambda *args: self.OnHeaderGetMenu(col)
            col.cursor = 0
            col.sr.line = uicls.Line(parent=col, align=uiconst.TORIGHT, idx=0, color=(1.0, 1.0, 1.0, 0.25))
            self.sr.columns.append(col)
        for each in col.children[:]:
            if each not in (col.sr.textCtrl,
             col.sr.editHandle,
             col.sr.triangle,
             col.sr.line,
             textOrObject):
                each.Close()

        if isinstance(textOrObject, basestring):
            col.sr.textCtrl.state = uiconst.UI_DISABLED
            col.sr.textCtrl.text = textOrObject
        else:
            col.sr.textCtrl.state = uiconst.UI_HIDDEN
            if textOrObject not in col.children:
                uiutil.Transplant(textOrObject, col, 0)
        if self.sr.node.Get('editable', 0):
            col.state = uiconst.UI_NORMAL
            if col.sr.editHandle:
                col.sr.editHandle.state = uiconst.UI_NORMAL
            else:
                par = uicls.Container(name='scaleHandle_%s' % idx, parent=col, align=uiconst.TOPRIGHT, height=self.height - 2, width=5, idx=0, state=uiconst.UI_NORMAL)
            line = uicls.Line(parent=par, align=uiconst.TOLEFT, idx=0, color=(1.0, 1.0, 1.0, 0.25))
            line.padTop = -1
            line.padBottom = -1
            par.OnMouseDown = (self.StartScaleCol, par)
            par.OnMouseUp = (self.EndScaleCol, par)
            par.OnMouseMove = (self.ScalingCol, par)
            par.cursor = 18
            par.columnIdx = idx
            col.sr.editHandle = par
        else:
            col.state = uiconst.UI_PICKCHILDREN
            if col.sr.editHandle:
                col.sr.editHandle.state = uiconst.UI_HIDDEN



    def FindAssociatingEntries(self):
        ret = []
        for node in self.sr.node.scroll.GetNodes()[(self.sr.node.idx + 1):]:
            if node.Get('columnID', None) == self.sr.node.columnID:
                ret.append(node)

        return ret



    def GetHeight(_self, *args):
        (node, width,) = args
        node.height = uix.GetTextHeight(''.join([ text for text in node.texts if isinstance(text, basestring) ]), singleLine=1) + 1
        return node.height



    def StartScaleCol(self, sender, *args):
        if uicore.uilib.rightbtn:
            return 
        (l, t, w, h,) = sender.parent.GetAbsolute()
        (sl, st, sw, sh,) = sender.GetAbsolute()
        associates = self.FindAssociatingEntries()
        self._startScalePosition = uicore.uilib.x
        self._startScalePositionDiff = sl - uicore.uilib.x
        self._scaleColumnIdx = sender.columnIdx
        self._scaleColumnInitialWidth = sender.parent.width
        self._minLeft = l + MINCOLWIDTH
        self.sr.scaleEntries = associates
        self.ScalingCol(sender)



    def ScalingCol(self, sender, *args):
        if getattr(self, '_startScalePosition', None):
            diff = uicore.uilib.x - self._startScalePosition
            sender.parent.width = max(MINCOLWIDTH, self._scaleColumnInitialWidth + diff)
            self.sr.node.customTabstops[self._scaleColumnIdx] = sender.parent.width
            self.UpdateColumnOrder(onlyVisible=True)



    def EndScaleCol(self, sender, *args):
        prefsID = self.sr.node.Get('columnID', None)
        if prefsID:
            current = settings.user.ui.Get('listentryColumns_%s' % prefsID, self.sr.node.customTabstops)
            current[self._scaleColumnIdx] = sender.parent.width
            settings.user.ui.Set('listentryColumns_%s' % prefsID, current)
        self.sr.node.customTabstops[self._scaleColumnIdx] = sender.parent.width
        self.sr.scaleEntries = None
        self._startScalePosition = 0



    def ChangeSort(self, sender, *args):
        columnID = self.sr.node.Get('columnID', None)
        if columnID:
            current = settings.user.ui.Get('columnSorts_%s' % columnID, {})
            if sender.columnIdx in current:
                direction = not current[sender.columnIdx]
            else:
                direction = False
            current[sender.columnIdx] = direction
            settings.user.ui.Set('columnSorts_%s' % columnID, current)
            current = settings.user.ui.Get('activeSortColumns', {})
            current[columnID] = sender.columnIdx
            settings.user.ui.Set('activeSortColumns', current)
        self.UpdateTriangles()
        self.UpdateColumnOrder()
        associates = self.FindAssociatingEntries()
        self.UpdateColumnSort(associates, columnID)
        callback = self.sr.node.Get('OnSortChange', None)
        if callback:
            callback()



    def UpdateColumnSort(self, entries, columnID):
        if not entries:
            return 
        startIdx = entries[0].idx
        endIdx = entries[-1].idx
        entries = listentry.SortColumnEntries(entries, columnID)
        self.sr.node.scroll.sr.nodes = self.sr.node.scroll.sr.nodes[:startIdx] + entries + self.sr.node.scroll.sr.nodes[(endIdx + 1):]
        idx = 0
        for entry in self.sr.node.scroll.GetNodes()[startIdx:]:
            if entry.Get('needReload', 0) and entry.panel:
                entry.panel.LoadLite(entry)
            idx += 1

        self.sr.node.scroll.UpdatePosition()



    def GetSortDirections(self):
        prefsID = self.sr.node.Get('columnID', None)
        if prefsID:
            return settings.user.ui.Get('columnSorts_%s' % prefsID, {})
        return {}



    def OnHeaderDblClick(self, sender, *args):
        self._clicks += 1
        self.ExecClick(sender)



    def OnHeaderClick(self, sender, *args):
        self._clicks += 1
        self.sr.clickTimer = base.AutoTimer(250, self.ExecClick, sender)



    def OnHeaderGetMenu(self, sender, *args):
        m = [(localization.GetByLabel('UI/Control/Entries/ColumnMoveForward'), self.ChangeColumnOrder, (sender, -1)), (localization.GetByLabel('UI/Control/Entries/ColumnMoveBackward'), self.ChangeColumnOrder, (sender, 1))]
        return m



    def ChangeColumnOrder(self, column, direction):
        currentDisplayOrder = settings.user.ui.Get('columnDisplayOrder_%s' % self.sr.node.columnID, None) or [ i for i in xrange(len(self.sr.node.texts)) ]
        newDisplayOrder = currentDisplayOrder[:]
        currentlyInDisplayOrder = currentDisplayOrder.index(column.columnIdx)
        newDisplayOrder.pop(currentlyInDisplayOrder)
        newDisplayOrder.insert(max(0, direction + currentlyInDisplayOrder), column.columnIdx)
        settings.user.ui.Set('columnDisplayOrder_%s' % self.sr.node.columnID, newDisplayOrder)
        self.UpdateColumnOrder()



    def ExecClick(self, sender, *args):
        if self._clicks > 1:
            self.ResetColumn(sender)
        elif self._clicks == 1:
            self.ChangeSort(sender)
        if not self.destroyed:
            self._clicks = 0
            self.sr.clickTimer = None



    def ResetColumn(self, sender, *args):
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if shift:
            idxs = []
            for i in xrange(len(self.sr.node.texts)):
                idxs.append(i)

        else:
            idxs = [sender.columnIdx]
        associates = self.FindAssociatingEntries()
        for columnIdx in idxs:
            textsInColumn = []
            columnWidths = []
            for node in [self.sr.node] + associates:
                text = node.texts[columnIdx]
                textsInColumn.append(text)
                padLeft = node.Get('padLeft', 6)
                padRight = node.Get('padRight', 6)
                fontsize = node.Get('fontsize', 12)
                hspace = node.Get('letterspace', 0)
                uppercase = node.Get('uppercase', 0)
                extraSpace = 0
                if node is self.sr.node and self.sr.node.Get('editable', 0):
                    extraSpace = 10
                if isinstance(text, basestring):
                    textWidth = sm.GetService('font').GetTextWidth(text, fontsize, hspace, uppercase)
                    if text:
                        columnWidths.append(padLeft + textWidth + padRight + 3 + extraSpace)
                    else:
                        columnWidths.append(3 + extraSpace)
                else:
                    textWidth = text.width
                    columnWidths.append(text.width)

            self.sr.node.customTabstops[columnIdx] = newWidth = max(columnWidths)
            self.UpdateColumnOrder()




    def UpdateTriangles(self):
        activeColumn = settings.user.ui.Get('activeSortColumns', {}).get(self.sr.node.columnID, 0)
        sortDirections = self.GetSortDirections()
        for column in self.sr.columns:
            direction = sortDirections.get(column.columnIdx, True)
            if column.columnIdx == activeColumn and self.sr.node.Get('editable', 0):
                if not column.sr.triangle:
                    column.sr.triangle = uicls.Icon(align=uiconst.CENTERRIGHT, pos=(3, 0, 16, 16), parent=column, idx=0, name='directionIcon', icon='ui_1_16_16')
                column.sr.triangle.state = uiconst.UI_DISABLED
                if direction == 1:
                    uiutil.MapIcon(column.sr.triangle, 'ui_1_16_16')
                else:
                    uiutil.MapIcon(column.sr.triangle, 'ui_1_16_15')
            elif column.sr.triangle:
                column.sr.triangle.state = uiconst.UI_HIDDEN





class Header(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.Header'
    __params__ = ['label']
    __notifyevents__ = ['OnUIColorsChanged']

    def Startup(self, args):
        self.sr.label = uicls.EveLabelMedium(text='', parent=self, left=8, top=0, state=uiconst.UI_DISABLED, singleline=1, align=uiconst.CENTERLEFT, bold=True)
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.mainFill = uicls.Fill(parent=self, padding=(1, 1, 1, 1))
        self.OnUIColorsChanged()
        sm.RegisterNotify(self)



    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = self.sr.node.label



    def OnUIColorsChanged(self, *args):
        (color, bgColor, comp, compsub,) = sm.GetService('window').GetWindowColors()
        if not self.destroyed:
            self.sr.mainFill.SetRGB(*comp)



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = uix.GetTextHeight(node.label, singleLine=1) + 6
        return node.height




class Subheader(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.Subheader'
    __params__ = ['label']
    __notifyevents__ = ['OnUIColorsChanged']

    def Startup(self, args):
        self.sr.label = uicls.EveLabelMedium(text='', parent=self, left=8, top=0, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, bold=True)
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.fill = uicls.Fill(parent=self, padding=(1, 1, 1, 1))
        (color, bgColor, comp, compsub,) = sm.GetService('window').GetWindowColors()
        self.sr.fill.color.SetRGB(*comp)
        sm.RegisterNotify(self)



    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = self.sr.node.label



    def OnUIColorsChanged(self, *args):
        if not self.destroyed:
            (color, bgColor, comp, compsub,) = sm.GetService('window').GetWindowColors()
            self.sr.fill.color.SetRGB(*comp)



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = uix.GetTextHeight(node.label, singleLine=1) + 6
        return node.height




class Text(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.Text'
    __params__ = ['text']

    def Startup(self, *args):
        self.sr.text = self.sr.label = uicls.EveLabelMedium(text='', parent=self, left=8, top=0, state=uiconst.UI_DISABLED, color=None, singleline=1, align=uiconst.CENTERLEFT)
        self.sr.infoicon = uicls.InfoIcon(size=16, left=2, top=2, parent=self, idx=0, align=uiconst.TOPRIGHT)
        self.sr.infoicon.OnClick = self.ShowInfo
        self.sr.icon = uicls.Icon(parent=self, pos=(1, 2, 24, 24), align=uiconst.TOPLEFT, idx=0, ignoreSize=True)
        self.sr.line = uicls.Container(name='lineparent', align=uiconst.TOBOTTOM, parent=self, idx=0, height=1)
        uicls.Fill(parent=self.sr.line)



    def Load(self, node):
        self.sr.node = node
        data = node
        self.sr.text.text = unicode(data.text)
        self.typeID = data.Get('typeID', None)
        self.itemID = data.Get('itemID', None)
        self.isStation = data.Get('isStation', 0)
        if node.Get('hint', None):
            self.hint = node.hint
        else:
            self.hint = uiutil.ReplaceTags(self.sr.text.text, ('<t>', '  '))
        if self.typeID or self.isStation and self.itemID:
            self.sr.infoicon.state = uiconst.UI_NORMAL
        else:
            self.sr.infoicon.state = uiconst.UI_HIDDEN
        gid = node.Get('iconID', None)
        iid = node.Get('icon', None)
        if gid or iid:
            if gid:
                self.sr.icon.LoadIcon(node.iconID, ignoreSize=True)
            elif iid:
                self.sr.icon.LoadIcon(node.icon, ignoreSize=True)
            self.sr.icon.SetSize(24, 24)
            self.sr.icon.state = uiconst.UI_NORMAL
            self.sr.text.left = self.height + 4
        else:
            self.sr.icon.state = uiconst.UI_HIDDEN
            self.sr.text.left = 8
        if uiutil.GetAsUnicode(self.sr.text).find('<url') != -1:
            self.sr.text.state = uiconst.UI_NORMAL
        else:
            self.sr.text.state = uiconst.UI_DISABLED
        if node.Get('line', 0):
            self.sr.line.state = uiconst.UI_DISABLED
        else:
            self.sr.line.state = uiconst.UI_HIDDEN



    def OnClick(self, *args):
        OnClick = self.sr.node.Get('OnClick', None)
        if OnClick:
            if callable(OnClick):
                OnClick()
            else:
                OnClick[0](*OnClick[1:])



    def OnDblClick(self, *args):
        if self.sr.node.Get('OnDblClick', None):
            self.sr.node.OnDblClick(self)
        elif self.sr.node.Get('canOpen', None):
            uix.TextBox(self.sr.node.canOpen, uiutil.GetAsUnicode(self.sr.node.text).replace('<t>', '<br>').replace('\r', ''), preformatted=1)



    def ShowInfo(self, *args):
        if self.sr.node.Get('isStation', 0) and self.itemID:
            stationinfo = sm.RemoteSvc('stationSvc').GetStation(self.itemID)
            sm.GetService('info').ShowInfo(stationinfo.stationTypeID, self.itemID)
            return 
        if self.sr.node.Get('typeID', None):
            sm.GetService('info').ShowInfo(self.sr.node.typeID, self.sr.node.Get('itemID', None))



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = uix.GetTextHeight(node.text, singleLine=1) + 6
        return node.height



    def CopyText(self):
        text = uiutil.GetAsUnicode(self.sr.node.text)
        blue.pyos.SetClipboardData(uiutil.StripTags(text.replace('<t>', ' ')))



    def GetMenu(self):
        m = []
        if self.sr.node.GetMenu:
            m = self.sr.node.GetMenu()
        if self.sr.node.Get('isStation', 0) and self.itemID or self.sr.node.Get('typeID', None) is not None:
            try:
                hasShowInfo = False
                for item in m:
                    if item is not None and item[0] == localization.GetByLabel('UI/Commands/ShowInfo'):
                        hasShowInfo = True
                        break

                if not hasShowInfo:
                    m += [(localization.GetByLabel('UI/Commands/ShowInfo'), self.ShowInfo), None]
            except:
                pass
        return m + [(localization.GetByLabel('UI/Common/Copy'), self.CopyText)]




class KillMail(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.KillMail'
    __params__ = ['mail']
    __nonpersistvars__ = ['selection', 'id']

    def Startup(self, *args):
        sub = uicls.Container(name='sub', parent=self, pos=(0, 0, 0, 0))
        self.sr.leftbox = uicls.Container(parent=sub, align=uiconst.TOLEFT, width=42, height=42, padding=(0, 2, 4, 2))
        self.sr.middlebox = uicls.Container(parent=sub, align=uiconst.TOALL, padding=(0, 2, 0, 0))
        self.sr.icon = uicls.Icon(parent=self.sr.leftbox, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        uicls.Frame(parent=self.sr.leftbox, color=(0.4, 0.4, 0.4, 0.5))
        self.sr.copyicon = uicls.Icon(icon='ui_73_16_1', parent=sub, pos=(4, 4, 16, 16), align=uiconst.TOPRIGHT, hint=localization.GetByLabel('UI/Control/Entries/CopyKillInfo'))
        self.sr.copyicon.OnClick = (self.GetCombatText, 1)
        self.sr.selection = uicls.Fill(parent=self, padding=(1, 1, 1, 1), color=(1.0, 1.0, 1.0, 0.25))
        self.sr.line = uicls.Container(name='lineparent', align=uiconst.TOBOTTOM, parent=self, idx=0, height=1)
        uicls.Fill(parent=self.sr.line)



    def Load(self, node):
        self.sr.node = node
        self.FillTextAndIcons()
        self.Lolite()



    def FillTextAndIcons(self):
        kill = self.sr.node.mail
        if self.height == 64:
            expanded = 1
        else:
            expanded = 0
        topLine = 14
        if eve.session.charid == kill.victimCharacterID or eve.session.corpid == kill.victimCorporationID:
            text = localization.GetByLabel('UI/Control/Entries/KillMailShipAndTime', shipTypeID=kill.victimShipTypeID, killTime=blue.os.GetWallclockTime() - kill.killTime)
            self.AddOrSetTextLine(text, configName='killMailsShipAndTimeLabel')
            text = ''
            if kill.victimShipTypeID is not None:
                self.sr.icon.LoadIconByTypeID(kill.victimShipTypeID, ignoreSize=True)
            text = self._GetCorpAndOrAllianceText(kill.finalCorporationID, kill.finalAllianceID)
            self.AddOrSetTextLine(text, configName='killerCorpOrAllianceLabel', top=topLine)
            text = ''
            if kill.finalShipTypeID is not None and kill.finalWeaponTypeID is not None:
                text = localization.GetByLabel('UI/Control/Entries/KillMailShipAndWeapon', shipTypeID=kill.finalShipTypeID, weaponTypeID=kill.finalWeaponTypeID)
            elif kill.finalShipTypeID is not None:
                text = cfg.invtypes.Get(kill.finalShipTypeID).name
            elif kill.finalWeaponTypeID is not None:
                text = cfg.invtypes.Get(kill.finalWeaponTypeID).name
            self.AddOrSetTextLine(text, configName='killerShipOrWeaponLabel', top=topLine * 2)
        elif eve.session.charid == kill.finalCharacterID or eve.session.corpid == kill.finalCorporationID:
            if kill.victimCharacterID is not None or kill.victimCorporationID is not None:
                if kill.victimCharacterID is not None:
                    text = localization.GetByLabel('UI/Control/Entries/KillMailCharacterAndTime', characterID=kill.victimCharacterID, killTime=blue.os.GetWallclockTime() - kill.killTime)
                else:
                    text = util.FormatTimeAgo(kill.killTime)
                self.AddOrSetTextLine(text, configName='victimNameOrTimeLabel')
                text = ''
                text = self._GetCorpAndOrAllianceText(kill.victimCorporationID, kill.victimAllianceID)
                self.AddOrSetTextLine(text, configName='victimCorpOrAllianceLabel', top=topLine)
                text = ''
                if kill.victimShipTypeID and kill.solarSystemID:
                    mapSvc = sm.GetService('map')
                    regionID = mapSvc.GetParent(mapSvc.GetParent(kill.solarSystemID))
                    text = localization.GetByLabel('UI/Control/Entries/KillMailShipAndSolarSystem', shipTypeID=kill.victimShipTypeID, solarSystemID=kill.solarSystemID, regionID=regionID, security=sm.GetService('map').GetSecurityStatus(kill.solarSystemID))
                elif kill.victimShipTypeID:
                    text = cfg.invtypes.Get(kill.victimShipTypeID).name
                elif kill.solarSystemID:
                    mapSvc = sm.GetService('map')
                    regionID = mapSvc.GetParent(mapSvc.GetParent(kill.solarSystemID))
                    text = localization.GetByLabel('UI/Control/Entries/KillMailSolarSystem', solarSystemID=kill.solarSystemID, regionID=regionID, security=sm.GetService('map').GetSecurityStatus(kill.solarSystemID))
                self.AddOrSetTextLine(text, configName='shipNameAndSolarSystemLabel', top=topLine * 2)
            else:
                self.AddOrSetTextLine(localization.GetByLabel('UI/Control/Entries/KillMailUnknown'), configName='unknownLabel')
            if kill.victimShipTypeID is not None:
                self.sr.icon.LoadIconByTypeID(kill.victimShipTypeID, ignoreSize=True)
        else:
            text = localization.GetByLabel('UI/Control/Entries/KillMailError')
            self.sr.icon.LoadIcon('ui_7_64_7', ignoreSize=True)
            self.sr.copyicon.state = uiconst.UI_HIDDEN
            self.GetMenu = None



    def _GetCorpAndOrAllianceText(self, corpID, allianceID):
        corpName = None
        corpTicker = ''
        allianceName = None
        allianceTicker = ''
        text = None
        if corpID is not None:
            corpName = cfg.eveowners.Get(corpID).name
            try:
                corpTicker = cfg.corptickernames.Get(corpID).tickerName
            except KeyError as e:
                pass
        if allianceID is not None:
            allianceName = cfg.eveowners.Get(allianceID).name
            try:
                allianceTicker = cfg.allianceshortnames.Get(allianceID).shortName
            except KeyError as e:
                pass
        if corpName and allianceName:
            text = localization.GetByLabel('UI/Control/Entries/KillMailCorpAndAlliance', corpName=corpName, corpTicker=corpTicker, allianceName=allianceName, allianceTicker=allianceTicker)
        elif corpName:
            text = localization.GetByLabel('UI/Control/Entries/KillMailCorpOrAlliance', name=corpName, ticker=corpTicker)
        elif allianceName:
            text = localization.GetByLabel('UI/Control/Entries/KillMailCorpOrAlliance', name=allianceName, ticker=allianceTicker)
        return text



    def AddOrSetTextLine(self, text, configName = '', top = 0):
        if text:
            label = getattr(self, configName, None)
            if label is not None:
                label.text = text
            else:
                label = uicls.EveLabelSmall(text=text, parent=self.sr.middlebox, align=uiconst.TOPLEFT, top=top)
                if configName:
                    setattr(self, configName, label)



    def GetMenu(self):
        m = []
        if self.sr.node.GetMenu:
            m = self.sr.node.GetMenu()
        return m + [(localization.GetByLabel('UI/Commands/ShowInfo'), self.RedirectToInfo, (1,)), None, (localization.GetByLabel('UI/Control/Entries/CopyKillInformation'), self.GetCombatText, (1,))]



    def RedirectToInfo(self, *args):
        kill = self.sr.node.mail
        if kill.victimCharacterID == session.charid:
            baddieGuyID = None
            if kill.finalCharacterID is None:
                baddieGuyID = kill.finalCorporationID
            else:
                baddieGuyID = kill.finalCharacterID
            char = cfg.eveowners.Get(baddieGuyID)
            sm.StartService('info').ShowInfo(int(char.Type()), baddieGuyID)
        elif kill.victimCharacterID is not None:
            char = cfg.eveowners.Get(kill.victimCharacterID)
            sm.StartService('info').ShowInfo(int(char.Type()), kill.victimCharacterID)
        elif kill.victimCorporationID is not None:
            sm.StartService('info').ShowInfo(const.typeCorporation, kill.victimCorporationID)
        elif kill.allianceID is not None:
            sm.StartService('info').ShowInfo(const.typeAlliance, kill.victimAllianceID)



    def GetCombatText(self, isCopy = 0, *args):
        mail = self.sr.node.mail
        ret = util.CombatLog_CopyText(mail)
        if isCopy:
            blue.pyos.SetClipboardData(ret.replace('<br>', '\r\n').replace('<t>', '   '))
        else:
            return ret



    def _OnClose(self):
        self.timer = None



    def OnMouseEnter(self, *args):
        self.Hilite()
        eve.Message('ListEntryEnter')



    def OnMouseExit(self, *args):
        self.Lolite()



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = 46
        return node.height



    def Hilite(self):
        self.sr.selection.state = uiconst.UI_DISABLED



    def Lolite(self):
        self.sr.selection.state = uiconst.UI_HIDDEN



    def OnDblClick(self, *args):
        mail = self.sr.node.mail
        ret = util.CombatLog_CopyText(mail)
        wnd = form.CombatDetailsWnd.GetIfOpen()
        if wnd:
            wnd.UpdateDetails(ret)
            wnd.Maximize()
        else:
            wnd = form.CombatDetailsWnd.Open(create=1, ret=ret)




class LabelText(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.LabelText'

    def Startup(self, args):
        self.sr.label = uicls.EveLabelSmall(text='', parent=self, left=8, top=4, state=uiconst.UI_DISABLED, bold=True)
        self.sr.text = uicls.EveLabelMedium(text='', parent=self, left=0, top=4, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.sr.line = uicls.Container(name='lineparent', align=uiconst.TOBOTTOM, parent=self, state=uiconst.UI_HIDDEN, height=1)
        uicls.Fill(parent=self.sr.line)



    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = self.name = self.sr.node.label
        self.sr.text.left = int(self.sr.node.Get('textpos', 128)) + 4
        self.sr.text.text = self.sr.node.text
        if self.sr.node.Get('labelAdjust', 0):
            self.sr.label.width = self.sr.node.Get('labelAdjust', 0)
        if node.Get('line', 0):
            self.sr.line.state = uiconst.UI_DISABLED
        else:
            self.sr.line.state = uiconst.UI_HIDDEN



    def GetHeight(self, *args):
        (node, width,) = args
        descwidth = min(256 - int(node.Get('textpos', 128)), width - int(node.Get('textpos', 128)) - 8)
        height = uix.GetTextHeight(node.text, fontsize=fontConst.EVE_MEDIUM_FONTSIZE, width=descwidth, hspace=0, linespace=12)
        height = max(height, uix.GetTextHeight(node.label, fontsize=fontConst.EVE_MEDIUM_FONTSIZE, width=width, hspace=0, linespace=12))
        node.height = max(19, height + 4)
        return node.height




class IconLabelText(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.IconLabelText'
    ICON_POS_REPLACES_LABEL = 0
    ICON_POS_REPLACES_TEXT = 1
    ICON_POS_IN_FRONT_OF_LABEL = 2
    ICON_POS_BEHIND_LABEL = 3
    ICON_POS_IN_FRONT_OF_TEXT = 4
    ICON_POS_BEHIND_TEXT = 5
    ICON_POS_NO_ICON = 6
    iconSize = 16
    margin = 4
    defaultTextWidth = 128

    def Startup(self, args):
        self.sr.label = uicls.EveHeaderSmall(text='', parent=self, left=8, top=4, state=uiconst.UI_DISABLED)
        self.sr.text = uicls.EveLabelMedium(text='', parent=self, left=0, top=4, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.sr.line = uicls.Container(name='lineparent', align=uiconst.TOBOTTOM, parent=self, state=uiconst.UI_HIDDEN, height=1)
        uicls.Fill(parent=self.sr.line)



    def Load(self, node):
        self.sr.node = node
        iconPositioning = self.sr.node.Get('iconPositioning', IconLabelText.ICON_POS_IN_FRONT_OF_LABEL)
        self.iconID = self.sr.node.Get('icon', None)
        if self.iconID is None:
            iconPositioning = IconLabelText.ICON_POS_NO_ICON
        hasLabel = True
        hasText = True
        if iconPositioning == IconLabelText.ICON_POS_REPLACES_LABEL:
            hasLabel = False
            textOffset = self.margin
            self.InsertIcon(textOffset)
        elif iconPositioning == IconLabelText.ICON_POS_REPLACES_TEXT:
            hasText = False
            textOffset = int(self.sr.node.Get('textpos', self.defaultTextWidth)) + self.margin
            self.InsertIcon(textOffset)
        elif iconPositioning == IconLabelText.ICON_POS_IN_FRONT_OF_LABEL:
            textOffset = self.margin
            self.InsertIcon(textOffset)
            textOffset += self.sr.icon.width
            self.sr.label.left = textOffset + self.margin
        elif iconPositioning == IconLabelText.ICON_POS_IN_FRONT_OF_TEXT:
            textOffset = self.margin + self.sr.text.left
            self.InsertIcon(textOffset)
            textOffset += self.sr.icon.width
            self.sr.text.left = textOffset + self.margin
        if hasLabel:
            self.sr.label.text = self.name = self.sr.node.label
            if self.sr.node.Get('labelAdjust', 0):
                self.sr.label.width = self.sr.node.Get('labelAdjust', 0)
        if hasText:
            self.sr.text.left = int(self.sr.node.Get('textpos', self.defaultTextWidth)) + self.margin
            self.sr.text.text = self.sr.node.text
        if iconPositioning == IconLabelText.ICON_POS_BEHIND_LABEL:
            textOffset = self.margin + self.sr.label.left + self.sr.label.width
            self.InsertIcon(textOffset)
        elif iconPositioning == IconLabelText.ICON_POS_BEHIND_TEXT:
            textOffset = self.margin + self.sr.text.left + self.sr.text.width
            self.InsertIcon(textOffset)
        if node.Get('line', 0):
            self.sr.line.state = uiconst.UI_DISABLED
        else:
            self.sr.line.state = uiconst.UI_HIDDEN



    def InsertIcon(self, offset):
        self.sr.icon = uicls.Icon(icon=self.iconID, parent=self, pos=(offset,
         1,
         self.iconSize,
         self.iconSize), align=uiconst.TOPLEFT, idx=0)



    def GetHeight(self, *args):
        (node, width,) = args
        descwidth = min(256 - int(node.Get('textpos', 128)), width - int(node.Get('textpos', 128)) - 8)
        height = uix.GetTextHeight(node.text, fontsize=fontConst.EVE_MEDIUM_FONTSIZE, width=descwidth, hspace=0, linespace=12)
        height = max(height, uix.GetTextHeight(node.label, fontsize=fontConst.EVE_MEDIUM_FONTSIZE, width=width, hspace=0, linespace=12))
        node.height = max(19, height + 4)
        return node.height




class TextTimer(Text):
    __guid__ = 'listentry.TextTimer'

    def Startup(self, *args):
        listentry.Text.Startup(self, args)
        self.sr.label = uicls.EveLabelSmall(text='', parent=self, left=8, top=2, state=uiconst.UI_DISABLED)
        self.sr.text.SetAlign(uiconst.TOPLEFT)
        self.sr.text.top = 12



    def Load(self, node):
        listentry.Text.Load(self, node)
        self.sr.label.text = self.sr.node.label
        self.sr.label.left = self.sr.text.left
        self.sr.text.top = self.sr.label.top + self.sr.label.textheight - 2
        countdownTime = node.Get('countdownTime', None)
        countupTime = node.Get('countupTime', None)
        if countdownTime is not None or countupTime is not None:
            self.UpdateTime(countdownTime, countupTime)
            self.sr.timeOutTimer = base.AutoTimer(1000, self.UpdateTime, countdownTime, countupTime)
        else:
            self.sr.text.text = localization.GetByLabel('UI/Control/Entries/TimeUnknown')
            self.sr.timeOutTimer = None



    def GetHeight(self, *args):
        (node, width,) = args
        labelheight = uix.GetTextHeight(node.label, fontsize=fontConst.EVE_SMALL_FONTSIZE, singleLine=1, uppercase=1)
        textheight = uix.GetTextHeight(node.text, fontsize=fontConst.EVE_MEDIUM_FONTSIZE, singleLine=1)
        node.height = 2 + labelheight + textheight
        return node.height



    def UpdateTime(self, countdownTime = None, countupTime = None):
        if countupTime:
            timerText = localization.GetByLabel('UI/Control/Entries/TimeAgo', time=blue.os.GetWallclockTime() - countupTime)
            self.sr.text.text = timerText
            self.hint = timerText
        elif countdownTime:
            timerText = localization.GetByLabel('UI/Control/Entries/TimeIn', time=countdownTime - blue.os.GetWallclockTime())
            self.sr.text.text = timerText
            self.hint = timerText
        if getattr(self.sr.node, 'text', None) is not None:
            self.sr.node.text = self.sr.text.text




class LabelTextTop(Text):
    __guid__ = 'listentry.LabelTextTop'

    def Startup(self, *args):
        listentry.Text.Startup(self, args)
        self.sr.label = uicls.EveLabelSmall(text='', parent=self, left=8, top=2, state=uiconst.UI_DISABLED)
        self.sr.text.SetAlign(uiconst.TOPLEFT)
        self.sr.text.top = 12



    def Load(self, node):
        listentry.Text.Load(self, node)
        self.sr.label.text = self.sr.node.label
        self.sr.label.left = self.sr.text.left
        self.sr.text.top = self.sr.label.top + self.sr.label.textheight



    def GetHeight(self, *args):
        (node, width,) = args
        labelheight = uix.GetTextHeight(node.label, fontsize=fontConst.EVE_SMALL_FONTSIZE, singleLine=1, uppercase=1)
        textheight = uix.GetTextHeight(node.text, fontsize=fontConst.EVE_MEDIUM_FONTSIZE, singleLine=1)
        node.height = 2 + labelheight + textheight
        return node.height




class LabelPlanetTextTop(LabelTextTop):
    __guid__ = 'listentry.LabelPlanetTextTop'

    def GetMenu(self):
        baseMenu = LabelTextTop.GetMenu(self)
        locationID = self.sr.node.Get('locationID', None)
        itemID = self.sr.node.Get('itemID', None)
        typeID = self.sr.node.Get('typeID', None)
        if locationID is not None and itemID is not None and itemID is not None:
            openPlanetFunc = lambda planetID: sm.GetService('viewState').ActivateView('planet', planetID=planetID)
            return [(localization.GetByLabel('UI/PI/Common/ViewInPlanetMode'), openPlanetFunc, (itemID,)), None] + baseMenu
        else:
            return baseMenu




class Button(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.Button'
    __params__ = ['label', 'caption', 'OnClick']

    def Startup(self, args):
        self.sr.label = uicls.EveLabelMedium(text='', parent=self, left=8, top=-1, state=uiconst.UI_DISABLED, singleline=1, align=uiconst.CENTERLEFT, lineSpacing=-0.2)
        self.sr.line = uicls.Container(name='lineparent', align=uiconst.TOBOTTOM, parent=self, state=uiconst.UI_HIDDEN, height=1)
        uicls.Fill(parent=self.sr.line)
        self.sr.button = uicls.Button(parent=self, label='', align=uiconst.TOPRIGHT, pos=(2, 2, 0, 0), idx=0)



    def Load(self, node):
        self.sr.node = node
        singleline = node.Get('singleline', 1)
        if self.sr.label.singleline != singleline:
            self.sr.label.singleline = singleline
        btnWidth = 0
        if self.sr.node.Get('OnClick', None):
            node = self.sr.node
            butt = self.sr.button
            ags = node.Get('args', (None,))
            self.sr.button.OnClick = lambda *args: node.OnClick(*(ags + (butt,)))
            self.sr.button.SetLabel(self.sr.node.caption)
            self.sr.button.state = uiconst.UI_NORMAL
            btnWidth = self.sr.button.width
        else:
            self.sr.button.state = uiconst.UI_HIDDEN
        if not singleline:
            (l, t, w, h,) = self.GetAbsolute()
            self.sr.label.width = w - btnWidth - self.sr.label.left * 2
        self.sr.label.text = self.sr.node.label
        self.sr.line.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][self.sr.node.Get('line', 1)]



    def GetHeight(self, *args):
        (node, width,) = args
        if node.Get('OnClick', None):
            btnLabelWidth = uix.GetTextWidth(node.caption, fontsize=fontConst.EVE_MEDIUM_FONTSIZE)
            btnWidth = min(256, max(48, btnLabelWidth + 24))
            btnLabelHeight = uix.GetTextHeight(node.caption, fontsize=fontConst.EVE_MEDIUM_FONTSIZE)
            btnHeight = min(32, btnLabelHeight + 9)
        else:
            btnWidth = 0
            btnHeight = 0
        singleline = node.Get('singleline', 1)
        if singleline:
            mainLabelHeight = uix.GetTextHeight(node.label, fontsize=fontConst.EVE_MEDIUM_FONTSIZE, singleLine=1)
            node.height = max(16, mainLabelHeight + 4, btnHeight + 2)
        else:
            width = node.Get('entryWidth', 100) - btnWidth
            mainLabelHeight = uix.GetTextHeight(node.label, width=width, fontsize=fontConst.EVE_MEDIUM_FONTSIZE)
            node.height = max(16, mainLabelHeight + 4, btnHeight + 2)
        return node.height




class Line(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.Line'
    __params__ = []

    def Startup(self, args):
        uicls.Line(parent=self, align=uiconst.TOBOTTOM, color=(1.0, 1.0, 1.0, 0.125))



    def Load(self, node):
        self.sr.node = node
        self.sr.node.height = 1



    def GetHeight(self, *args):
        (node, width,) = args
        return node.height




class Combo(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.Combo'
    __params__ = ['OnChange', 'label', 'options']

    def Startup(self, args):
        uicls.Container(name='push', parent=self, height=5, align=uiconst.TOTOP, idx=0)
        self.sr.combo = uicls.Combo(parent=self, label='', options=[], name='', callback=self.OnComboChange, align=uiconst.TOTOP)
        self.sr.push = uicls.Container(name='push', parent=self, width=128, align=uiconst.TOLEFT, idx=0)
        self.sr.label = uicls.EveLabelSmall(text='', parent=self, left=8, top=5, width=112, state=uiconst.UI_DISABLED)
        uicls.Container(name='push', parent=self, width=3, align=uiconst.TORIGHT, idx=0)
        self.sr.line = uicls.Container(name='lineparent', align=uiconst.TOBOTTOM, parent=self, idx=0, height=1)
        uicls.Fill(parent=self.sr.line)



    def Load(self, node):
        self.sr.node = node
        self.sr.combo.LoadOptions(self.sr.node.options, self.sr.node.Get('setValue', None))
        self.sr.label.text = self.sr.node.label
        self.sr.push.width = max(128, self.sr.label.textwidth + 10)
        if self.sr.node.Get('name', ''):
            self.sr.combo.name = self.sr.node.name



    def OnComboChange(self, combo, header, value, *args):
        if self.sr.node.Get('settingsUser', 0):
            settings.user.ui.Set(self.sr.node.cfgName, value)
        self.sr.node.setValue = value
        self.sr.node.OnChange(combo, header, value)



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = max(22, uix.GetTextHeight(node.label, width=112)) + 6
        return node.height




class Edit(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.Edit'
    __params__ = ['label']

    def Startup(self, args):
        uicls.Container(name='push', parent=self, height=3, align=uiconst.TOTOP)
        uicls.Container(name='push', parent=self, width=128, align=uiconst.TOLEFT)
        uicls.Container(name='push', parent=self, width=3, align=uiconst.TORIGHT)
        self.sr.edit = uicls.SinglelineEdit(name='edit', parent=self, align=uiconst.TOTOP)
        self.sr.label = uicls.EveLabelSmall(text='', parent=self, left=8, top=5, width=112, state=uiconst.UI_DISABLED)
        self.sr.line = uicls.Container(name='lineparent', align=uiconst.TOBOTTOM, parent=self, idx=0, height=1)
        uicls.Fill(parent=self.sr.line)



    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = self.sr.node.label
        self.sr.edit.floatmode = None
        self.sr.edit.integermode = None
        if self.sr.node.Get('lines', 1) != 1:
            log.LogError('listentry.Edit supports only singleline')
        if self.sr.node.Get('intmode', 0):
            (minInt, maxInt,) = self.sr.node.intmode
            self.sr.edit.IntMode(minInt, maxInt)
        elif self.sr.node.Get('floatmode', 0):
            (minFloat, maxFloat,) = self.sr.node.floatmode
            self.sr.edit.FloatMode(minFloat, maxFloat)
        if self.sr.node.Get('setValue', None) is None:
            self.sr.node.setValue = ''
        self.sr.edit.SetValue(self.sr.node.setValue)
        if self.sr.node.Get('maxLength', None):
            self.sr.edit.SetMaxLength(self.sr.node.maxLength)
        if self.sr.node.Get('name', ''):
            self.sr.edit.name = self.sr.node.name
        self.sr.edit.OnChange = self.OnChange



    def OnChange(self, *args):
        if self is not None and not self.destroyed and self.sr.node is not None:
            self.sr.node.setValue = self.sr.edit.GetValue()



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = max(22, uix.GetTextHeight(node.label, width=112)) + 6
        return node.height




class TextEdit(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.TextEdit'
    __params__ = ['label']

    def Startup(self, args):
        uicls.Container(name='push', parent=self, height=4, align=uiconst.TOTOP)
        uicls.Container(name='push', parent=self, height=4, align=uiconst.TOBOTTOM)
        uicls.Container(name='push', parent=self, width=127, align=uiconst.TOLEFT)
        uicls.Container(name='push', parent=self, width=2, align=uiconst.TORIGHT)
        self.sr.edit = uicls.EditPlainText(setvalue='', parent=self, align=uiconst.TOALL)
        self.sr.label = uicls.EveLabelSmall(text='', parent=self, left=8, top=3, width=112, state=uiconst.UI_DISABLED)
        self.sr.line = uicls.Container(name='lineparent', align=uiconst.TOBOTTOM, parent=self, idx=0, height=1)
        uicls.Fill(parent=self.sr.line)



    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = self.sr.node.label
        if self.sr.node.Get('readonly', None):
            self.sr.edit.ReadOnly()
        else:
            self.sr.edit.Editable(0)
        if self.sr.node.Get('setValue', None) is None:
            self.sr.node.setValue = ''
        self.sr.edit.SetValue(self.sr.node.setValue)
        if self.sr.node.Get('maxLength', None):
            self.sr.edit.SetMaxLength(self.sr.node.maxLength)
        if self.sr.node.Get('name', ''):
            self.sr.edit.name = self.sr.node.name
        self.sr.edit.OnChange = self.OnChange
        if getattr(self.sr.node, 'killFocus', None):
            self.sr.edit.OnKillFocus()



    def OnChange(self, *args):
        if self is not None and not self.destroyed and self.sr.node is not None:
            self.sr.node.setValue = self.sr.edit.GetValue()



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = node.Get('lines', 1) * 14 + 10
        return node.height




class ImplantEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.ImplantEntry'
    __params__ = ['label']

    def Startup(self, *etc):
        self.sr.label = uicls.EveLabelMedium(text='', parent=self, left=32, top=2, state=uiconst.UI_DISABLED)
        self.sr.timeLabel = uicls.EveLabelMedium(text='', parent=self, left=24, top=2, state=uiconst.UI_DISABLED, align=uiconst.BOTTOMRIGHT)
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.icon = uicls.Icon(icon='ui_22_32_30', parent=self, size=32, align=uiconst.RELATIVE, state=uiconst.UI_DISABLED)
        self.sr.infoicon = uicls.InfoIcon(size=16, left=2, top=2, parent=self, idx=0, align=uiconst.TOPRIGHT)
        self.sr.infoicon.OnClick = self.ShowInfo



    def Load(self, node):
        self.sr.node = node
        data = node
        if cfg.invtypes.Get(self.sr.node.implant_booster.typeID).groupID == const.groupBooster:
            slot = getattr(sm.GetService('godma').GetType(node.implant_booster.typeID), 'boosterness', None)
            timeToEnd = node.implant_booster.expiryTime
        else:
            slot = getattr(sm.GetService('godma').GetType(node.implant_booster.typeID), 'implantness', None)
            timeToEnd = None
        if slot is None:
            self.sr.label.top = 10
            self.sr.label.text = data.label
        else:
            self.sr.label.top = 2
            self.sr.label.text = localization.GetByLabel('UI/Control/Entries/ImplantLabel', implantName=data.label, slotNum=int(slot))
        self.sr.icon.LoadIcon(cfg.invtypes.Get(node.implant_booster.typeID).iconID, ignoreSize=True)
        self.sr.icon.SetSize(32, 32)
        if timeToEnd is not None:
            self.UpdateTime(timeToEnd)
            self.sr.timeOutTimer = base.AutoTimer(1000, self.UpdateTime, timeToEnd)
        else:
            self.sr.timeLabel.text = ''
            self.sr.timeOutTimer = None



    def UpdateTime(self, timeToEnd):
        timeInterval = timeToEnd - blue.os.GetWallclockTime()
        if timeInterval > MONTH:
            timeBreakAt = 'hour'
        elif timeInterval > DAY:
            timeBreakAt = 'min'
        else:
            timeBreakAt = 'sec'
        self.sr.timeLabel.text = util.FmtTimeInterval(timeInterval, timeBreakAt)



    def GetMenu(self):
        m = [(localization.GetByLabel('UI/Commands/ShowInfo'), self.ShowInfo)]
        if not cfg.invtypes.Get(self.sr.node.implant_booster.typeID).groupID == const.groupBooster and getattr(self.sr.node.implant_booster, 'itemID', None):
            m.append((localization.GetByLabel('UI/Control/Entries/ImplantUnplug'), self.RemoveImplant, (self.sr.node.implant_booster.itemID,)))
        return m



    def OnDblClick(self, *args):
        self.ShowInfo()



    def ShowInfo(self, *args):
        sm.GetService('info').ShowInfo(self.sr.node.implant_booster.typeID, getattr(self.sr.node.implant_booster, 'itemID', None))



    def RemoveImplant(self, itemID):
        if eve.Message('ConfirmUnPlugInImplant', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
            sm.GetService('godma').GetSkillHandler().RemoveImplantFromCharacter(itemID)



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = 32
        return node.height




class IconEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.IconEntry'
    __params__ = ['label']

    def Startup(self, *etc):
        self.labelleft = 32
        self.sr.label = uicls.EveLabelMedium(text='', parent=self, left=self.labelleft, top=0, width=512, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        self.sr.line = uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.icon = uicls.Icon(icon='ui_5_32_10', parent=self, pos=(0, 0, 0, 0), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        self.sr.selection = uicls.Fill(parent=self, align=uiconst.TOALL, pos=(0, 1, 0, 1), color=(1.0, 1.0, 1.0, 0.25))



    def Load(self, node):
        self.sr.node = node
        data = node
        self.sr.label.width = data.Get('maxLabelWidth', 512)
        self.sr.label.text = data.label
        if data.Get('icon', None) is not None:
            self.sr.icon.LoadIcon(data.icon, ignoreSize=True)
        iconoffset = node.Get('iconoffset', 0)
        self.sr.icon.left = iconoffset
        iconsize = node.Get('iconsize', 32)
        self.sr.icon.width = self.sr.icon.height = iconsize
        self.sr.label.left = iconsize + iconoffset
        linecolor = node.Get('linecolor', (1.0, 1.0, 1.0, 0.25))
        if node.Get('selectable', 1):
            if node.Get('selected', 0):
                self.sr.selection.state = uiconst.UI_DISABLED
            else:
                self.sr.selection.state = uiconst.UI_HIDDEN
        else:
            self.sr.selection.state = uiconst.UI_HIDDEN
        if node.Get('hint', None):
            self.hint = data.hint
        if node.Get('line', 1):
            self.sr.line.state = uiconst.UI_DISABLED
            self.sr.line.color.SetRGB(*linecolor)
        else:
            self.sr.line.state = uiconst.UI_HIDDEN



    def OnMouseEnter(self, *args):
        if self.sr.node and self.sr.node.Get('selectable', 1):
            eve.Message('ListEntryEnter')
            self.sr.selection.state = uiconst.UI_DISABLED



    def OnMouseExit(self, *args):
        if self.sr.node and self.sr.node.Get('selectable', 1):
            self.sr.selection.state = (uiconst.UI_HIDDEN, uiconst.UI_DISABLED)[self.sr.node.Get('selected', 0)]



    def OnClick(self, *args):
        if self.sr.node and self.sr.node.Get('selectable', 1):
            self.BlinkOff()
            self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')



    def GetHeight(self, *args):
        (node, width,) = args
        iconsize = node.Get('iconsize', 32)
        node.height = iconsize
        return node.height



    def Blink(self, hint = None, force = 1, blinkcount = 3, frequency = 750, bright = 0):
        blink = self.GetBlink()
        blink.state = uiconst.UI_DISABLED
        sm.GetService('ui').BlinkSpriteRGB(blink, min(1.0, self.r * (1.0 + bright * 0.25)), min(1.0, self.g * (1.0 + bright * 0.25)), min(1.0, self.b * (1.0 + bright * 0.25)), frequency, blinkcount, passColor=1)



    def BlinkOff(self):
        if self.sr.Get('blink', None) is not None:
            self.sr.blink.state = uiconst.UI_HIDDEN



    def GetBlink(self):
        if self.sr.Get('blink', None):
            return self.sr.blink
        blink = uicls.Fill(bgParent=self, name='hiliteFrame', state=uiconst.UI_HIDDEN, color=(0.28, 0.3, 0.35, 1.0), align=uiconst.TOALL)
        self.sr.blink = blink
        self.r = 0.28
        self.g = 0.3
        self.b = 0.35
        return self.sr.blink




class Icons(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.Icons'
    __params__ = ['icons']

    def Load(self, node):
        i = 0
        for each in node.icons:
            (icon, color, identifier, click,) = each
            if i >= len(self.children):
                newicon = uicls.Container(parent=self, pos=(0,
                 0,
                 self.height,
                 self.height), name='glassicon', state=uiconst.UI_NORMAL, align=uiconst.RELATIVE)
                uicls.Sprite(parent=newicon, name='dot', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/shared/windowDOT.png', align=uiconst.TOALL, spriteEffect=trinity.TR2_SFX_DOT, blendMode=trinity.TR2_SBM_ADD)
                newicon.sr.icon = uicls.Sprite(parent=newicon, name='picture', state=uiconst.UI_NORMAL, align=uiconst.TOALL)
                newicon.sr.color = uicls.Fill(parent=newicon, name='color', state=uiconst.UI_DISABLED, color=(0.45, 0.5, 1.0, 1.0))
                newicon.left = i * self.height
            else:
                newicon = self.children[i]
            if icon:
                newicon.sr.icon.LoadTexture(icon)
                newicon.sr.icon.state = uiconst.UI_DISABLED
            else:
                newicon.sr.icon.state = uiconst.UI_HIDDEN
            if color:
                newicon.sr.color.SetRGB(*color)
                newicon.sr.color.state = uiconst.UI_DISABLED
            else:
                newicon.sr.color.state = uiconst.UI_HIDDEN
            newicon.OnClick = (click, newicon)
            newicon.sr.identifier = identifier
            i += 1





class CheckEntry(Text):
    __guid__ = 'listentry.CheckEntry'

    def Startup(self, *args):
        listentry.Text.Startup(self, args)
        self.sr.text.color.SetRGB(1.0, 1.0, 1.0, 0.75)
        self.sr.have = uicls.Icon(parent=self, align=uiconst.CENTERLEFT, left=5, top=0, height=16, width=16, state=uiconst.UI_DISABLED)



    def Load(self, args):
        listentry.Text.Load(self, args)
        data = self.sr.node
        if data.checked:
            self.sr.have.LoadIcon('ui_38_16_193')
        else:
            self.sr.have.LoadIcon('ui_38_16_194')
        self.sr.have.left = 15 * data.sublevel - 11
        self.sr.text.left = 15 * data.sublevel + 5



    def GetMenu(self):
        m = []
        data = self.sr.node
        if data is not None:
            if data.Get('typeID', 0):
                m = sm.StartService('menu').GetMenuFormItemIDTypeID(None, data.typeID, ignoreMarketDetails=0)
        return m




class FittingEntry(Generic):
    __guid__ = 'listentry.FittingEntry'

    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes



    def Startup(self, *args):
        parent = uicls.Container(name='parent', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.sr.infoContainer = uicls.Container(name='infoContainer', parent=parent, align=uiconst.TORIGHT, width=16)
        self.sr.infoicon = uicls.InfoIcon(size=16, left=1, top=1, parent=self.sr.infoContainer, idx=0)
        self.sr.have = uicls.Icon(parent=parent, align=uiconst.TORIGHT, left=0, top=0, height=16, width=16)
        self.sr.label = uicls.EveLabelMedium(parent=parent, left=5, state=uiconst.UI_DISABLED, singleline=1, align=uiconst.CENTERLEFT)
        self.sr.line = uicls.Container(name='lineparent', align=uiconst.TOBOTTOM, parent=self, height=1)
        self.sr.mainline = uicls.Fill(parent=self.sr.line)
        self.sr.selection = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.25))
        self.sr.hilite = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.25))
        self.sr.infoicon.OnClick = self.ShowInfo
        self.hints = [localization.GetByLabel('UI/Control/Entries/FittingSkillMissing'), localization.GetByLabel('UI/Control/Entries/FittingSkillOK')]
        for eventName in events:
            setattr(self.sr, eventName, None)




    def Load(self, node):
        listentry.Generic.Load(self, node)
        hasSkill = self.HasSkill(node)
        if hasSkill:
            iconNum = 'ui_38_16_193'
        else:
            iconNum = 'ui_38_16_194'
        hint = self.hints[hasSkill]
        if node.Get('typeID', None) is None:
            self.sr.infoContainer.state = uiconst.UI_HIDDEN
        self.sr.have.LoadIcon(iconNum, ignoreSize=True)
        self.sr.have.SetSize(16, 16)
        self.sr.have.hint = hint



    def GetHeight(_self, *args):
        (node, width,) = args
        if node.Get('vspace', None):
            node.height = uix.GetTextHeight(node.label, singleLine=1) + node.vspace
        else:
            node.height = uix.GetTextHeight(node.label, singleLine=1) + 4
        return node.height



    def HasSkill(self, node):
        return sm.StartService('fittingSvc').HasSkillForFit(node.fitting)




class FittingEntryNonDraggable(FittingEntry):
    __guid__ = 'listentry.FittingEntryNonDraggable'

    def Startup(self, *args):
        listentry.FittingEntry.Startup(self, args)




class FittingModuleEntry(FittingEntry):
    __guid__ = 'listentry.FittingModuleEntry'

    def Startup(self, *args):
        listentry.FittingEntry.Startup(self, args)
        self.hints = [localization.GetByLabel('UI/Control/Entries/FittingModuleSkillMissing'), localization.GetByLabel('UI/Control/Entries/FittingModuleSkillOK')]



    def HasSkill(self, node):
        godma = sm.StartService('godma')
        return godma.CheckSkillRequirementsForType(node.typeID)



    def GetMenu(self):
        if not self.sr.node.Get('ignoreRightClick', 0):
            self.OnClick()
        if hasattr(self, 'sr'):
            if self.sr.node and self.sr.node.Get('GetMenu', None):
                return self.sr.node.GetMenu(self)
            if getattr(self, 'itemID', None) or getattr(self, 'typeID', None):
                return sm.GetService('menu').GetMenuFormItemIDTypeID(getattr(self, 'itemID', None), getattr(self, 'typeID', None), ignoreMarketDetails=0)
        return []




class CorpAllianceEntry(Generic):
    __guid__ = 'listentry.CorpAllianceEntry'

    def Startup(self, *args):
        listentry.Generic.Startup(self, args)



    def Load(self, node):
        listentry.Generic.Load(self, node)



    def GetDragData(self, *args):
        return [self]




class DraggableItem(Item):
    __guid__ = 'listentry.DraggableItem'

    def GetDragData(self, *args):
        return self.sr.node.scroll.GetSelectedNodes(self.sr.node)




def Get(entryType, settings = {}, data = None):
    import listentry
    decoClass = getattr(listentry, entryType)
    if data is None:
        if isinstance(settings, util.KeyVal):
            data = settings.__dict__
        else:
            data = settings
    elif isinstance(data, util.KeyVal):
        data = data.__dict__
    data['__guid__'] = getattr(decoClass, '__guid__', None)
    data['decoClass'] = decoClass
    return uicls.ScrollEntryNode(**data)



def SortColumnEntries(nodes, columnID):
    if not nodes:
        return nodes
    displayOrder = settings.user.ui.Get('columnDisplayOrder_%s' % columnID, None) or [ i for i in xrange(len(nodes[0].sortData)) ]
    c = 0
    sortData = []
    for node in nodes:
        if not c:
            c = len(node.sortData)
        elif c != len(node.sortData):
            raise RuntimeError('Mismatch in column sizes')
        sortData.append((ReorderSortData(node.sortData[:], columnID, displayOrder), node))

    sortDirections = settings.user.ui.Get('columnSorts_%s' % columnID, [0, {}])
    sortData = uiutil.SortListOfTuples(sortData)
    activeColumn = settings.user.ui.Get('activeSortColumns', {}).get(columnID, 0)
    if activeColumn in sortDirections and sortDirections[activeColumn] is False:
        sortData.reverse()
    return sortData



def ReorderSortData(sortData, columnID, displayOrder):
    if not sortData:
        return sortData
    if len(displayOrder) != len(sortData):
        return sortData
    ret = []
    activeColumn = settings.user.ui.Get('activeSortColumns', {}).get(columnID, 0)
    if activeColumn in displayOrder:
        di = displayOrder.index(activeColumn)
    else:
        di = 0
    for columnIdx in displayOrder[di:]:
        ret.append(sortData[columnIdx])

    return ret



def InitCustomTabstops(columnID, entries):
    idxs = []
    for i in xrange(len(entries[0].texts)):
        idxs.append(i)

    if not len(idxs):
        return 
    current = GetCustomTabstops(columnID)
    if current is not None:
        if len(current) == len(idxs):
            return 
    retval = []
    for columnIdx in idxs:
        textsInColumn = []
        columnWidths = []
        for node in entries:
            text = node.texts[columnIdx]
            textsInColumn.append(text)
            padLeft = node.Get('padLeft', 6)
            padRight = node.Get('padRight', 6)
            fontsize = node.Get('fontsize', 12)
            hspace = node.Get('letterspace', 0)
            uppercase = node.Get('uppercase', 0)
            if isinstance(text, basestring):
                textWidth = sm.GetService('font').GetTextWidth(text, fontsize, hspace, uppercase)
            else:
                textWidth = text.width
            extraSpace = 0
            if node.Get('editable', 0):
                extraSpace = 10
            columnWidths.append(padLeft + textWidth + padRight + 3 + extraSpace)

        retval.append(max(columnWidths))

    settings.user.ui.Set('listentryColumns_%s' % columnID, retval)



def GetCustomTabstops(columnID):
    return settings.user.ui.Get('listentryColumns_%s' % columnID, None)


exports = {'listentry.Get': Get,
 'listentry.SortColumnEntries': SortColumnEntries,
 'listentry.InitCustomTabstops': InitCustomTabstops,
 'listentry.GetCustomTabstops': GetCustomTabstops,
 'listentry.DraggableItem': DraggableItem}

