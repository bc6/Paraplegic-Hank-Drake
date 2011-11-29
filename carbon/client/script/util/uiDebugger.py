import uiconst
import blue
import uiutil
import util
import uicls
import math
import uthread
import form
import service

class UIDebugger(uicls.Window):
    __guid__ = 'form.UIDebugger'
    default_windowID = 'UIDebugger'
    default_width = 450
    default_height = 300
    default_topParentHeight = 0
    default_minSize = (default_width, default_height)
    default_caption = 'UI Debugger'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.keyUpCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.KeyUpListener)
        self.mouseEnterCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self.MouseEnterListener)
        self.animationThread = None
        self.showHighlite = True
        self.alignmentDebugMode = False
        self.highlightLock = False
        self.hierarchy = []
        self.ancestorConts = []
        self.childrenConts = []
        self.selectedCont = None
        self.currCont = None
        self.currSnapshot = 0
        self.updateScrollThread = None
        self.highlightCont = uicls.Container(parent=uicore.desktop, align=uiconst.TOALL, state=uiconst.UI_DISABLED, idx=0)
        self.leftCont = uicls.Container(name='leftcont', parent=self.sr.maincontainer, align=uiconst.TOLEFT, width=200, padding=6, clipChildren=True)
        self.infoCont = uicls.Container(name='infoCont', parent=self.leftCont, align=uiconst.TOBOTTOM, height=60)
        self.ConstructInfoCont()
        self.attributeCont = uicls.Container(name='attributeCont', parent=self.leftCont, clipChildren=True)
        topCont = uicls.Container(parent=self.sr.maincontainer, align=uiconst.TOTOP, height=22, padding=(3, 3, 3, 0), clipChildren=True)
        uicls.Checkbox(parent=topCont, text='Show highlight', align=uiconst.TOLEFT, configName='toggleAnimationCheckbox', checked=self.showHighlite, callback=self.OnShowHighliteCheckBox, width=100)
        uicls.Checkbox(parent=topCont, text='Alignment debug mode', align=uiconst.TOLEFT, checked=False, callback=self.OnAlignmentDebugModeChanged, width=150, padLeft=20)
        uicls.Checkbox(parent=topCont, text='Always on top', align=uiconst.TOLEFT, checked=False, callback=self.OnAlwaysOnTopChanged, width=100, padLeft=20)
        uicls.Checkbox(parent=topCont, text='Snapshot mode', align=uiconst.TOLEFT, checked=False, callback=self.OnSnapshotModeChanged, width=100, padLeft=20)
        uicls.Label(parent=topCont, text='Press <color=green>CTRL</color> to lock/unlock container highlight', align=uiconst.TOLEFT, padLeft=20)
        self.snapshotCont = uicls.Container(parent=self.sr.maincontainer, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, height=20, padBottom=20)
        icon = uicls.Label(parent=self.snapshotCont, align=uiconst.BOTTOMLEFT, text='Snapshots can be added by calling sm.GetService("UISnapshot").CreateSnapshot(uiObject, "Some caption")', top=-17, color=(1.0, 1.0, 1.0, 0.5))
        icon.OnClick = None
        uicls.Button(parent=self.snapshotCont, align=uiconst.TOLEFT, label='Add snapshot', func=self.OnAddSnapshotBtn)
        uicls.Button(parent=self.snapshotCont, align=uiconst.TOLEFT, label='Clear snapshots', func=self.OnClearSnapshotsBtn)
        self.prevSnapshotBtn = uicls.Button(parent=self.snapshotCont, align=uiconst.TOLEFT, label='Prev', func=self.OnPrevSnapshotBtn, padLeft=10)
        self.nextSnapshotBtn = uicls.Button(parent=self.snapshotCont, align=uiconst.TOLEFT, label='Next', func=self.OnNextSnapshotBtn)
        self.snapshotNumLabel = uicls.Label(parent=self.snapshotCont, align=uiconst.TOALL, padLeft=4, padTop=2)
        uicls.Label(parent=self.sr.maincontainer, text='Double click entries to move up/down the hierarchy', align=uiconst.TOBOTTOM)
        self.scroll = uicls.Scroll(parent=self.sr.maincontainer, name='scroll', align=uiconst.TOALL)
        self.scroll.OnSelectionChange = self.OnScrollSelectionChange



    def OnScrollSelectionChange(self, nodes):
        if not nodes:
            return 
        self.UpdateAttributeCont(nodes[0].cont)



    def UpdateAttributeCont(self, cont):
        self.attributeCont.Flush()
        if not cont:
            return 
        self.currAttrCont = cont
        uicls.Label(name='attrNameLabel', parent=self.attributeCont, text='<color=red>%s' % cont.name, fontsize=20, align=uiconst.TOTOP, padBottom=0)
        uicls.Label(name='attrGuidLabel', parent=self.attributeCont, text=cont.__guid__, fontsize=12, align=uiconst.TOTOP)
        uicls.Button(parent=self.attributeCont, align=uiconst.TOTOP, label='Open in jessica', func=self._OpenInJessica, args=(cont,), hint='Open selected object in jessica tree view')
        uicls.Button(parent=self.attributeCont, align=uiconst.TOTOP, label='Animate', func=self._GetAnimationWindow, args=(cont,), hint='Open selected object in the animation test window', padBottom=10)
        uicls.Label(parent=self.attributeCont, align=uiconst.TOTOP, text='STATE')
        options = (('UI_NORMAL', uiconst.UI_NORMAL),
         ('UI_DISABLED', uiconst.UI_DISABLED),
         ('UI_HIDDEN', uiconst.UI_HIDDEN),
         ('UI_PICKCHILDREN', uiconst.UI_PICKCHILDREN))
        for (label, value,) in options:
            self.attrStateRadioBtn = uicls.Checkbox(parent=self.attributeCont, text=label, options=options, groupname='stateGroup', name='attrStateCombo', checked=cont.state == value, retval=value, callback=self.OnAttrStateCombo, align=uiconst.TOTOP, padTop=0)

        self.attrState = cont.state
        options = (('TOPLEFT', uiconst.TOPLEFT),
         ('CENTERTOP', uiconst.CENTERTOP),
         ('TOPRIGHT', uiconst.TOPRIGHT),
         ('CENTERRIGHT', uiconst.CENTERRIGHT),
         ('BOTTOMRIGHT', uiconst.BOTTOMRIGHT),
         ('CENTERBOTTOM', uiconst.CENTERBOTTOM),
         ('BOTTOMLEFT', uiconst.BOTTOMLEFT),
         ('CENTERLEFT', uiconst.CENTERLEFT),
         ('CENTER', uiconst.CENTER),
         ('TOALL', uiconst.TOALL),
         ('TOLEFT', uiconst.TOLEFT),
         ('TOTOP', uiconst.TOTOP),
         ('TORIGHT', uiconst.TORIGHT),
         ('TOBOTTOM', uiconst.TOBOTTOM),
         ('TOLEFT_PROP', uiconst.TOLEFT_PROP),
         ('TOTOP_PROP', uiconst.TOTOP_PROP),
         ('TORIGHT_PROP', uiconst.TORIGHT_PROP),
         ('TOBOTTOM_PROP', uiconst.TOBOTTOM_PROP),
         ('TOPLEFT_PROP', uiconst.TOPLEFT_PROP),
         ('ABSOLUTE', uiconst.ABSOLUTE))
        self.attrAlignCombo = uicls.Combo(parent=self.attributeCont, label='align', options=options, name='attrAlignCombo', select=cont.align, callback=self.OnAttrsChanged, align=uiconst.TOTOP, padTop=20)
        posCont = uicls.Container(parent=self.attributeCont, align=uiconst.TOTOP, height=20, padTop=20)
        if cont.align in (uiconst.TOLEFT_PROP,
         uiconst.TOTOP_PROP,
         uiconst.TORIGHT_PROP,
         uiconst.TOBOTTOM_PROP,
         uiconst.TOPLEFT_PROP):
            ints = None
            floats = (0.0, 10.0)
        else:
            ints = (-10000, 10000)
            floats = None
        self.attrLeftEdit = uicls.SinglelineEdit(parent=posCont, name='left', align=uiconst.TOLEFT, label='left', ints=ints, floats=floats, setvalue=cont.left, OnChange=self.OnAttrsChanged, width=50)
        self.attrTopEdit = uicls.SinglelineEdit(parent=posCont, name='top', align=uiconst.TOLEFT, label='top', ints=ints, floats=floats, setvalue=cont.top, OnChange=self.OnAttrsChanged, width=50)
        self.attrWidthEdit = uicls.SinglelineEdit(parent=posCont, name='width', align=uiconst.TOLEFT, label='width', ints=ints, floats=floats, setvalue=cont.width, OnChange=self.OnAttrsChanged, width=50)
        self.attrHeightEdit = uicls.SinglelineEdit(parent=posCont, name='height', align=uiconst.TOLEFT, label='height', ints=ints, floats=floats, setvalue=cont.height, OnChange=self.OnAttrsChanged, width=50)
        padCont = uicls.Container(parent=self.attributeCont, align=uiconst.TOTOP, height=20, padTop=20)
        self.attrPadLeftEdit = uicls.SinglelineEdit(parent=padCont, name='padLeft', align=uiconst.TOLEFT, label='padLeft', ints=ints, floats=floats, setvalue=cont.padLeft, OnChange=self.OnAttrsChanged, width=50)
        self.attrPadTopEdit = uicls.SinglelineEdit(parent=padCont, name='padTop', align=uiconst.TOLEFT, label='padTop', ints=ints, floats=floats, setvalue=cont.padTop, OnChange=self.OnAttrsChanged, width=50)
        self.attrPadRightEdit = uicls.SinglelineEdit(parent=padCont, name='padRight', align=uiconst.TOLEFT, label='padRight', ints=ints, floats=floats, setvalue=cont.padRight, OnChange=self.OnAttrsChanged, width=50)
        self.attrPadBottomEdit = uicls.SinglelineEdit(parent=padCont, name='padBottom', align=uiconst.TOLEFT, label='padBottom', ints=ints, floats=floats, setvalue=cont.padBottom, OnChange=self.OnAttrsChanged, width=50)



    def ConstructInfoCont(self):
        self.infoActiveText = uicls.Label(name='infoActiveText', parent=self.infoCont, align=uiconst.TOBOTTOM)
        self.infoFocusText = uicls.Label(name='infoFocusText', parent=self.infoCont, align=uiconst.TOBOTTOM)
        self.infoCursorLocalText = uicls.Label(name='infoCursorLocalText', parent=self.infoCont, align=uiconst.TOBOTTOM)
        self.infoCursorText = uicls.Label(name='infoCursorText', parent=self.infoCont, align=uiconst.TOBOTTOM)
        uthread.new(self.UpdateInfoCont)



    def UpdateInfoCont(self):
        while not self.destroyed:
            text = '<b>Cursor:</b> (%d, %d)' % (uicore.uilib.x, uicore.uilib.y)
            self.infoCursorText.text = text
            if self.currCont:
                (x, y,) = self.currCont.GetAbsolutePosition()
                text = '<b>Cursor (local):</b> (%d, %d)' % (uicore.uilib.x - x, uicore.uilib.y - y)
            else:
                text = '-'
            self.infoCursorLocalText.text = text
            text = '<b>Focus:</b> %s' % getattr(uicore.registry.GetFocus(), 'name', 'None')
            self.infoFocusText.text = text
            text = '<b>Active:</b> %s' % getattr(uicore.registry.GetActive(), 'name', 'None')
            self.infoActiveText.text = text
            blue.synchro.SleepWallclock(50)




    def OnAttrStateCombo(self, btn):
        self.attrState = btn.data['value']
        self.OnAttrsChanged()



    def OnAttrsChanged(self, *args):
        if not self.currAttrCont:
            return 
        self.currAttrCont.state = self.attrState
        newAlign = self.attrAlignCombo.GetValue()
        updateAttrsCont = self.currAttrCont.align != newAlign
        self.currAttrCont.align = newAlign
        self.currAttrCont.left = self.attrLeftEdit.GetValue()
        self.currAttrCont.top = self.attrTopEdit.GetValue()
        self.currAttrCont.width = self.attrWidthEdit.GetValue()
        self.currAttrCont.height = self.attrHeightEdit.GetValue()
        self.currAttrCont.padLeft = self.attrPadLeftEdit.GetValue()
        self.currAttrCont.padTop = self.attrPadTopEdit.GetValue()
        self.currAttrCont.padRight = self.attrPadRightEdit.GetValue()
        self.currAttrCont.padBottom = self.attrPadBottomEdit.GetValue()
        self.HighlightCont(self.currAttrCont, updateAttrsCont=updateAttrsCont)



    def OnShowHighliteCheckBox(self, cb):
        self.showHighlite = cb.GetValue()
        if not self.showHighlite:
            self.CleanContHighLight()
            return 
        if not self.highlightLock:
            self.CleanContHighLight()
        self.HighlightCont(self.currCont)



    def KeyUpListener(self, wnd, eventID, key, *args):
        (key, id,) = key
        if key == uiconst.VK_CONTROL:
            self.ToggleHighlightLock()
        return True



    def ToggleHighlightLock(self):
        self.highlightLock = not self.highlightLock



    def _OnClose(self, *args):
        self.CleanContHighLight()
        uicore.event.UnregisterForTriuiEvents(self.mouseEnterCookie)
        uicore.event.UnregisterForTriuiEvents(self.keyUpCookie)
        uicore.desktop.children.remove(self.highlightCont)



    def MouseEnterListener(self, cont, *args):
        cont = uicore.uilib.GetMouseOver()
        if uiutil.GetWindowAbove(cont) == self:
            return True
        if not cont or not self.mouseEnterCookie or self.destroyed:
            return False
        if not self.showHighlite:
            return True
        if self.highlightLock or cont == self.currCont:
            return True
        self.HighlightCont(cont)
        self.currCont = cont
        return True



    def HighlightCont(self, cont, updateAttrsCont = True):
        self.CleanContHighLight()
        ancestors = self.GetAncestors(cont)
        children = getattr(cont, 'children', [])
        numTotal = len(ancestors) + len(children) + 1
        num = 0
        for (contList, hlList,) in ((ancestors, self.ancestorConts), (children, self.childrenConts)):
            for c in contList:
                if c == self.highlightCont:
                    continue
                color = self.GetColor(num, numTotal)
                hlCont = HighlightCont(parent=self.highlightCont, pos=c.GetAbsolute(), cont=c, color=color.GetRGBA(), show=False)
                hlList.append((c, hlCont, color))
                num += 1


        color = util.Color('RED')
        hlCont = HighlightCont(parent=self.highlightCont, pos=cont.GetAbsolute(), cont=cont, color=color.GetRGBA())
        self.selectedCont = (cont, hlCont, color)
        if updateAttrsCont:
            self.UpdateAttributeCont(cont)
        self.UpdateScroll()



    def UpdateScroll(self):
        if self.updateScrollThread:
            self.updateScrollThread.kill()
        self.updateScrollThread = uthread.new(self._UpdateScroll)



    def _UpdateScroll(self):
        blue.synchro.SleepWallclock(250)
        if self.destroyed:
            return 
        scrolllist = []
        scrolllist.append(uicls.ScrollEntryNode(decoClass=uicls.SE_Generic, label='Ancestors', fontsize=18, showline=True))
        for (i, (c, h, color,),) in enumerate(self.ancestorConts):
            scrolllist.append(self.GetScrollEntry(c, h, color))

        scrolllist.append(uicls.ScrollEntryNode(decoClass=uicls.SE_Generic, label='Selected', fontsize=18, showline=True))
        scrolllist.append(self.GetScrollEntry(*self.selectedCont))
        scrolllist.append(uicls.ScrollEntryNode(decoClass=uicls.SE_Generic, label='Children', fontsize=18, showline=True))
        for (i, (c, h, color,),) in enumerate(self.childrenConts):
            scrolllist.append(self.GetScrollEntry(c, h, color))

        self.scroll.Load(contentList=scrolllist, headers=self.GetScrollHeaders(), ignoreSort=True)



    def GetScrollHeaders(self):
        if not self.alignmentDebugMode:
            return ['Name',
             'l',
             't',
             'w',
             'h',
             'align',
             'state',
             'pl',
             'pt',
             'pr',
             'pb',
             'opacity',
             'color',
             'pyClass',
             'renderObject']
        else:
            return ['Name',
             'l',
             't',
             'w',
             'h',
             'align',
             'display',
             'dx',
             'dy',
             'dw',
             'dh',
             'alignDirty',
             'dispDirty']



    def GetScrollEntry(self, c, h, color):
        if not self.alignmentDebugMode:
            return self.GetScrollEntryNormal(c, h, color)
        else:
            return self.GetScrollEntryAlignmentDebug(c, h, color)



    def GetScrollEntryNormal(self, c, h, color):
        try:
            cCol = c.color.GetRGBA()
        except:
            cCol = '-'
        return uicls.ScrollEntryNode(decoClass=uicls.SE_Generic, label='<color=%s>%s</color><t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (color.GetHex(),
         c.name,
         c.left,
         c.top,
         c.width,
         c.height,
         self.GetAlignAsString(c),
         self.GetStateAsString(c),
         getattr(c, 'padLeft', '-'),
         getattr(c, 'padTop', '-'),
         getattr(c, 'padRight', '-'),
         getattr(c, 'padBottom', '-'),
         getattr(c, 'opacity', '-'),
         cCol,
         getattr(c, '__guid__', '-'),
         getattr(c.__renderObject__, '__name__', '-')), OnMouseEnter=self.OnListentryMouseEnter, OnMouseExit=self.OnListentryMouseExit, OnDblClick=self.OnListentryDblClick, OnClick=self.OnListentryClick, OnGetMenu=self.ListentryGetMenu, cont=c, highlightCont=h, hint=self._GetLabelRecurs('', c))



    def GetScrollEntryAlignmentDebug(self, c, h, color):
        if c.display:
            display = 'True'
        else:
            display = '<color=red>False</color>'
        if c._alignmentDirty:
            _alignmentDirty = '<color=red>True</color>'
        else:
            _alignmentDirty = 'False'
        if c._displayDirty:
            _displayDirty = '<color=red>True</color>'
        else:
            _displayDirty = 'False'
        return uicls.ScrollEntryNode(decoClass=uicls.SE_Generic, label='<color=%s>%s</color><t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (color.GetHex(),
         c.name,
         c.left,
         c.top,
         c.width,
         c.height,
         self.GetAlignAsString(c),
         display,
         c.displayX,
         c.displayY,
         c.displayWidth,
         c.displayHeight,
         _alignmentDirty,
         _displayDirty), OnMouseEnter=self.OnListentryMouseEnter, OnMouseExit=self.OnListentryMouseExit, OnDblClick=self.OnListentryDblClick, OnClick=self.OnListentryClick, OnGetMenu=self.ListentryGetMenu, cont=c, highlightCont=h)



    def ListentryGetMenu(self, entry):
        return [('Animate', self._GetAnimationWindow, (entry.sr.node.cont,)), ('Open in jessica', self._OpenInJessica, (entry.sr.node.cont,)), ('Close', entry.sr.node.cont.Close, ())]



    def _GetAnimationWindow(self, cont):
        wnd = form.UIAnimationTest.GetIfOpen()
        if wnd:
            wnd.SetAnimationObject(cont)
        else:
            form.UIAnimationTest.Open(animObj=cont)



    def _OpenInJessica(self, obj):
        try:
            import wx
            tree = wx.FindWindowByName('TreeView2')
            tree.AddUITree(obj.name, obj)
        except ImportError:
            pass



    def _GetLabelRecurs(self, label, container):
        if container.parent is not None:
            label = self._GetLabelRecurs(label, container.parent)
        return label + '\\' + container.name



    def OnListentryMouseEnter(self, entry):
        entry.sr.node.highlightCont.ShowHover()



    def OnListentryMouseExit(self, entry):
        if not entry.sr.node.highlightCont.destroyed:
            entry.sr.node.highlightCont.ShowNoHover()



    def OnListentryClick(self, entry):
        cont = entry.sr.node.cont
        if uicore.uilib.Key(uiconst.VK_MENU):
            cont.display = not cont.display



    def OnListentryDblClick(self, entry):
        self.HighlightCont(entry.sr.node.cont)



    def GetAncestors(self, cont):
        ancestorList = []
        if cont.parent is not None:
            self.GetAncestorsRecurs(cont.parent, ancestorList)
        return ancestorList



    def GetAncestorsRecurs(self, cont, ancestorList):
        if cont.parent is not None:
            self.GetAncestorsRecurs(cont.parent, ancestorList)
        if hasattr(cont, 'GetAbsolute'):
            ancestorList.append(cont)



    def GetColor(self, num, maxNum):
        hue = min(1.0, 0.1 + 0.85 * float(num) / maxNum)
        return util.Color().SetHSB(hue, 1.0, 1.0)



    def CleanContHighLight(self):
        self.highlightCont.Flush()
        self.ancestorConts = []
        self.childrenConts = []
        self.selectedCont = None



    def OnAlwaysOnTopChanged(self, checkbox):
        if checkbox.checked:
            self.SetParent(uicore.desktop, 0)
        else:
            self.SetParent(uicore.layer.main, 0)



    def OnSnapshotModeChanged(self, checkbox):
        self.scroll.Clear()
        if checkbox.checked:
            self.snapshotCont.Show()
            self.UpdateSnapshotBtns()
            if self.GetSnapshots():
                self.HighlightCont(self.GetCurrSnapshot())
            self.highlightLock = True
        else:
            self.snapshotCont.Hide()



    def OnAlignmentDebugModeChanged(self, checkbox):
        self.alignmentDebugMode = checkbox.checked
        self.UpdateScroll()



    def GetStateAsString(self, cont):
        stateVal = cont.state
        for stateName in ('UI_NORMAL', 'UI_DISABLED', 'UI_HIDDEN', 'UI_PICKCHILDREN'):
            stateConst = getattr(uiconst, stateName, None)
            if stateConst == stateVal:
                return stateName

        return '<color=red>%s</color>' % stateVal



    def GetAlignAsString(self, cont):
        if hasattr(cont, 'GetAlign'):
            alignVal = cont.GetAlign()
        else:
            alignVal = -1
        for stateName in ('ABSOLUTE', 'RELATIVE', 'TOPLEFT', 'TOPRIGHT', 'BOTTOMLEFT', 'BOTTOMRIGHT', 'TOLEFT', 'TOTOP', 'TOBOTTOM', 'TORIGHT', 'TOALL', 'TOPLEFT_PROP', 'TOTOP_PROP', 'TORIGHT_PROP', 'TOBOTTOM_PROP', 'CENTERLEFT', 'CENTERRIGHT', 'CENTERTOP', 'CENTERBOTTOM', 'CENTER'):
            stateConst = getattr(uiconst, stateName, None)
            if stateConst == alignVal:
                return stateName

        return '<color=red>%s</color>' % alignVal



    def OnAddSnapshotBtn(self, *args):
        sm.GetService('UISnapshot').CreateSnapshot(self.currAttrCont)
        self.currSnapshot = len(self.GetSnapshots()) - 1
        self.UpdateSnapshotBtns()
        self.HighlightCont(self.GetCurrSnapshot())



    def OnClearSnapshotsBtn(self, *args):
        sm.GetService('UISnapshot').ClearSnapshots()
        self.currSnapshot = 0
        self.UpdateSnapshotBtns()
        self.scroll.Clear()



    def OnPrevSnapshotBtn(self, *args):
        self.currSnapshot -= 1
        self.currSnapshot = max(self.currSnapshot, 0)
        self.UpdateSnapshotBtns()
        self.HighlightCont(self.GetCurrSnapshot())



    def OnNextSnapshotBtn(self, *args):
        self.currSnapshot += 1
        self.currSnapshot = min(self.currSnapshot, len(self.GetSnapshots()) - 1)
        self.UpdateSnapshotBtns()
        self.HighlightCont(self.GetCurrSnapshot())



    def UpdateSnapshotBtns(self):
        num = len(self.GetSnapshots())
        if num and self.currSnapshot > 0:
            self.prevSnapshotBtn.Enable()
        else:
            self.prevSnapshotBtn.Disable()
        if num and self.currSnapshot < num - 1:
            self.nextSnapshotBtn.Enable()
        else:
            self.nextSnapshotBtn.Disable()
        if num:
            self.snapshotNumLabel.SetText('%s/%s (%s)' % (self.currSnapshot + 1, num, self.GetCurrSnapshot().caption))
        else:
            self.snapshotNumLabel.SetText('0/0')
        self.snapshotNumLabel.Layout()



    def GetSnapshots(self):
        return sm.GetService('UISnapshot').snapshots



    def GetCurrSnapshot(self):
        return self.GetSnapshots()[self.currSnapshot]




class UISnapshotSvc(service.Service):
    __guid__ = 'svc.UISnapshot'
    __update_on_reload__ = 1

    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        self.snapshots = []



    def ClearSnapshots(self):
        self.snapshots = []
        w = form.UIDebugger.GetIfOpen()
        if w:
            w.UpdateSnapshotBtns()



    def CreateSnapshot(self, cont, caption = ''):
        snapshot = self._CreateSnapshot(cont)
        snapshot.caption = caption
        self.snapshots.append(snapshot)
        w = form.UIDebugger.GetIfOpen()
        if w:
            w.UpdateSnapshotBtns()



    def _CreateSnapshot(self, cont, parent = None):
        ret = uicls._FakeContainer(parent=parent, name=cont.name, align=cont.align, state=cont.state, left=cont.left, top=cont.top, width=cont.width, height=cont.height)
        ret.displayX = cont.displayX
        ret.displayY = cont.displayY
        ret.displayWidth = cont.displayWidth
        ret.displayHeight = cont.displayHeight
        ret.display = cont.display
        ret._alignmentDirty = cont._alignmentDirty
        ret._displayDirty = cont._displayDirty
        if hasattr(cont, 'children'):
            for c in cont.children:
                self._CreateSnapshot(c, ret)

        return ret



STATE_HIDDEN = 1
STATE_TRANSPARENT = 2
STATE_NORMAL = 3
STATE_HOVER = 4

class FakeContainer(uicls.Container):
    __guid__ = 'uicls._FakeContainer'
    __renderObject__ = None
    caption = 'No caption'

    def FlagAlignmentDirty(self):
        pass



    def FlagNextObjectsDirty(self, lvl = 0):
        pass



    def GetAbsolute(self):
        return (self.displayX,
         self.displayY,
         self.displayHeight,
         self.displayWidth)




class HighlightCont(uicls.Container):
    __guid__ = 'uicls._HighlightCont'
    default_align = uiconst.ABSOLUTE
    default_state = uiconst.UI_DISABLED
    default_idx = 0

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        cont = attributes.Get('cont')
        color = attributes.Get('color', util.Color.WHITE)
        show = attributes.Get('show', True)
        (l, t, w, h,) = attributes.Get('pos', (0, 0, 0, 0))
        self.renderState = STATE_NORMAL
        self.oldState = STATE_NORMAL
        uicls.Frame(bgParent=self, color=color, width=2)
        self.fill = uicls.Fill(bgParent=self, color=util.Color(*color).SetAlpha(0.2).GetRGBA())
        label = cont.name
        self.label = uicls.Label(parent=self, text=label, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, top=-12, color=color)
        if not show:
            self.ShowHidden()



    def ShowTransparent(self):
        self.renderState = STATE_TRANSPARENT
        self.UpdateState()



    def ShowNormal(self):
        self.renderState = STATE_NORMAL
        self.UpdateState()



    def ShowHover(self):
        self.oldState = self.renderState
        self.renderState = STATE_HOVER
        self.UpdateState()



    def ShowNoHover(self):
        self.renderState = self.oldState
        self.UpdateState()



    def ShowHidden(self):
        self.renderState = STATE_HIDDEN
        self.UpdateState()



    def UpdateState(self):
        if self.renderState == STATE_HOVER:
            self.label.Show()
        else:
            self.label.Hide()
        if self.renderState == STATE_NORMAL:
            self.opacity = 0.8
        elif self.renderState == STATE_TRANSPARENT:
            self.opacity = 0.3
        elif self.renderState == STATE_HOVER:
            self.opacity = 1.0
        if self.renderState == STATE_HIDDEN:
            self.state = uiconst.UI_HIDDEN
        else:
            self.state = uiconst.UI_DISABLED




