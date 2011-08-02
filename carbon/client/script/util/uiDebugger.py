import uiconst
import blue
import uiutil
import util
import uicls
import math
import uthread
MODE_OFF = 0
MODE_SELECTED = 1
MODE_PARENT = 2
MODE_CHILDREN = 3

class UIDebugger(uicls.Window):
    __guid__ = 'form.UIDebugger'
    default_width = 450
    default_height = 300
    default_minSize = (default_width, default_height)

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetCaption('UI Debugger')
        if hasattr(self, 'SetTopparentHeight'):
            self.SetTopparentHeight(0)
        self.keyUpCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.KeyUpListener)
        self.mouseEnterCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self.MouseEnterListener)
        self.animationThread = None
        self.mode = MODE_SELECTED
        self.highlightLock = False
        self.hierarchy = []
        self.ancestorConts = []
        self.childrenConts = []
        self.selectedCont = None
        self.currCont = None
        self.highlightCont = uicls.Container(parent=uicore.desktop, align=uiconst.TOALL, state=uiconst.UI_DISABLED, idx=0)
        topCont = uicls.Container(parent=self.sr.maincontainer, align=uiconst.TOTOP, height=22, padding=(3, 3, 3, 0))
        uicls.Label(parent=topCont, text='Highlight mode:', align=uiconst.TOLEFT, autowidth=True, autoheight=True, padRight=5, padTop=1)
        uicls.Checkbox(parent=topCont, text='Off', align=uiconst.TOLEFT, configName='toggleAnimationCheckbox', groupname='modeGroup', checked=False, callback=self.OnRadioButtonChange, retval=MODE_OFF, width=100)
        uicls.Checkbox(parent=topCont, text='Selected', align=uiconst.TOLEFT, configName='toggleAnimationCheckbox', groupname='modeGroup', checked=True, callback=self.OnRadioButtonChange, retval=MODE_SELECTED, width=100)
        uicls.Checkbox(parent=topCont, text='Ancestors', align=uiconst.TOLEFT, configName='toggleAnimationCheckbox', groupname='modeGroup', checked=False, callback=self.OnRadioButtonChange, retval=MODE_PARENT, width=100)
        uicls.Checkbox(parent=topCont, text='Children', align=uiconst.TOLEFT, configName='toggleAnimationCheckbox', groupname='modeGroup', checked=False, callback=self.OnRadioButtonChange, retval=MODE_CHILDREN, width=100)
        uicls.Label(parent=topCont, text='Press <color=green>CTRL</color> to lock/unlock container highlight', align=uiconst.TOPRIGHT, autowidth=True, autoheight=True)
        uicls.Label(parent=self.sr.maincontainer, text='Double click entries to move up/down the hierarchy', align=uiconst.TOBOTTOM, autowidth=True, autoheight=True)
        self.scroll = uicls.Scroll(parent=self.sr.maincontainer, name='scroll', align=uiconst.TOALL)



    def OnRadioButtonChange(self, cb):
        self.mode = cb.data['value']
        if self.mode == MODE_OFF:
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



    def OnClose_(self, *args):
        self.CleanContHighLight()
        uicore.event.UnregisterForTriuiEvents(self.mouseEnterCookie)
        uicore.event.UnregisterForTriuiEvents(self.keyUpCookie)
        uicore.desktop.children.remove(self.highlightCont)



    def MouseEnterListener(self, cont, *args):
        cont = uicore.event.GetMouseOver()
        if not cont or not self.mouseEnterCookie or self.destroyed:
            return False
        if self.mode == MODE_OFF:
            return True
        if self.highlightLock or cont == self.currCont:
            return True
        self.HighlightCont(cont)
        self.currCont = cont
        return True



    def HighlightCont(self, cont):
        self.CleanContHighLight()
        ancestors = self.GetAncestors(cont)
        children = getattr(cont, 'children', [])
        numTotal = len(ancestors) + len(children) + 1
        num = 0
        for (contList, hlList, showMode,) in ((ancestors, self.ancestorConts, MODE_PARENT), (children, self.childrenConts, MODE_CHILDREN)):
            for c in contList:
                if c == self.highlightCont:
                    continue
                color = self.GetColor(num, numTotal)
                hlCont = HighlightCont(parent=self.highlightCont, pos=c.GetAbsolute(), cont=c, color=color.GetRGBA(), show=self.mode == showMode)
                hlList.append((c, hlCont, color))
                num += 1


        color = util.Color('RED')
        hlCont = HighlightCont(parent=self.highlightCont, pos=cont.GetAbsolute(), cont=cont, color=color.GetRGBA())
        self.selectedCont = (cont, hlCont, color)
        self.UpdateScroll()



    def UpdateScroll(self):
        scrolllist = []
        scrolllist.append(uicls.ScrollEntryNode(decoClass=uicls.SE_Generic, label='Ancestors', fontsize=18, showline=True))
        for (i, (c, h, color,),) in enumerate(self.ancestorConts):
            scrolllist.append(self.GetScrollEntry(c, h, color))

        scrolllist.append(uicls.ScrollEntryNode(decoClass=uicls.SE_Generic, label='Selected', fontsize=18, showline=True))
        scrolllist.append(self.GetScrollEntry(*self.selectedCont))
        scrolllist.append(uicls.ScrollEntryNode(decoClass=uicls.SE_Generic, label='Children', fontsize=18, showline=True))
        for (i, (c, h, color,),) in enumerate(self.childrenConts):
            scrolllist.append(self.GetScrollEntry(c, h, color))

        self.scroll.Load(contentList=scrolllist, headers=['Name',
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
         'triClass'], ignoreSort=True)



    def GetScrollEntry(self, c, h, color):
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
         getattr(c, '__cid__', '-')), OnMouseEnter=self.OnListentryMouseEnter, OnMouseExit=self.OnListentryMouseExit, OnDblClick=self.OnListentryDblClick, OnClick=self.OnListentryClick, OnGetMenu=self.ListentryGetMenu, cont=c, highlightCont=h, hint=self._GetLabelRecurs('', c))



    def ListentryGetMenu(self, entry):
        return [('Animate', self._GetAnimationWindow, (entry.sr.node.cont,)), ('Copy path', self._CopyPath, (entry.sr.node.cont,))]



    def _GetAnimationWindow(self, cont):
        wnd = sm.GetService('window').GetWindow('UIAnimationTest')
        if wnd:
            wnd.SetAnimationObject(cont)
        else:
            sm.GetService('window').GetWindow('UIAnimationTest', create=1, animObj=cont)



    def _CopyPath(self, obj):
        ret = ''
        while True:
            if obj == uicore.desktop or not obj.parent:
                break
            index = obj.parent.children.index(obj)
            ret = '.children[%s]' % index + ret
            obj = obj.parent

        ret = 'uicore.desktop' + ret
        blue.pyos.SetClipboardData(ret)



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
        for stateName in ('ABSOLUTE', 'RELATIVE', 'TOPLEFT', 'TOPRIGHT', 'BOTTOMLEFT', 'BOTTOMRIGHT', 'TOLEFT', 'TOTOP', 'TOBOTTOM', 'TORIGHT', 'TOALL', 'CENTERLEFT', 'CENTERRIGHT', 'CENTERTOP', 'CENTERBOTTOM', 'CENTER'):
            stateConst = getattr(uiconst, stateName, None)
            if stateConst == alignVal:
                return stateName

        return '<color=red>%s</color>' % alignVal



STATE_HIDDEN = 1
STATE_TRANSPARENT = 2
STATE_NORMAL = 3
STATE_HOVER = 4

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
        uicls.Frame(parent=self, color=color, width=2)
        self.fill = uicls.Fill(parent=self, color=util.Color(*color).SetAlpha(0.2).GetRGBA())
        label = cont.name
        self.label = uicls.Label(parent=self, text=label, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, top=-12, autowidth=True, autoheight=True, color=color)
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




