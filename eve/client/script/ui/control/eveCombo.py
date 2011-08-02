import xtriui
import uix
import uiutil
import uthread
import util
import blue
import _weakref
import listentry
import menu
import types
import draw
import uicls
import uiconst
import log

class Combo(uicls.ComboCore):
    __guid__ = 'uicls.Combo'
    default_fontsize = 12
    default_labelleft = None
    default_align = uiconst.TOPLEFT
    default_width = 86
    default_height = 18

    def ApplyAttributes(self, attributes):
        self.labelleft = attributes.get('labelleft', self.default_labelleft)
        uicls.ComboCore.ApplyAttributes(self, attributes)
        self.cursor = uiconst.UICURSOR_SELECT
        uthread.new(sm.GetService('window').CheckControlAppearance, self)
        self.sr.expander.LoadIcon('ui_38_16_229')
        self.sr.expander.SetAlpha(0.8)
        self.sr.expander.top = 0
        self.sr.expander.left = -1



    def SetLabel_(self, label):
        if self.labelleft is not None:
            self.padLeft = self.labelleft
            self.sr.label.left = -self.labelleft
            self.sr.label.width = self.labelleft - 6
            self.sr.label.autowidth = 0
            self.sr.label.letterspace = 1
            self.sr.label.linespace = 9
        if label:
            self.sr.label.text = uiutil.UpperCase(label)
            if self.labelleft is not None:
                self.sr.label.top = 0
                self.sr.label.SetAlign(uiconst.CENTERLEFT)
            self.sr.label.state = uiconst.UI_DISABLED
        else:
            self.sr.label.state = uiconst.UI_HIDDEN



    def Prepare_SelectedText_(self):
        self.sr.selected = uicls.Label(text='', parent=self.sr.textclipper, name='value', top=2, left=6, state=uiconst.UI_DISABLED)



    def Prepare_Underlay_(self):
        self.sr.background = uicls.Container(name='_underlay', parent=self, state=uiconst.UI_DISABLED)
        self.sr.backgroundFrame = uicls.BumpedUnderlay(parent=self.sr.background)



    def Prepare_Label_(self):
        self.sr.label = uicls.Label(text='', parent=self, name='label', top=-13, fontsize=10, letterspace=1, left=1, state=uiconst.UI_HIDDEN, idx=1)



    def OnSetFocus(self, *args):
        if self and not self.destroyed and self.parent and self.parent.name == 'inlines':
            if self.parent.parent and self.parent.parent.sr.node:
                browser = uiutil.GetBrowser(self)
                if browser:
                    uthread.new(browser.ShowObject, self)
        if self.sr.activeframe:
            self.sr.activeframe.state = uiconst.UI_DISABLED



    def LoadOptions(self, entries, select = None, hints = None):
        entries = entries or [(mls.UI_GENERIC_NOCHOICES, None)]
        screwed = [ k for (k, v,) in entries if type(k) not in types.StringTypes ]
        if screwed:
            raise RuntimeError('NonStringKeys', repr(screwed))
        self.entries = entries
        self.hints = hints
        if select in (None, ''):
            select = self.entries[0][1]
        wasSelected = self.SelectItemByValue(select)
        if not wasSelected:
            self.SelectItemByValue(self.entries[0][1])
        self.AutoAdjustWidth_()



    def AutoAdjustWidth_(self):
        currentAlign = self.GetAlign()
        if self.adjustWidth and self.entries and currentAlign not in (uiconst.TOTOP, uiconst.TOBOTTOM, uiconst.TOALL):
            arrowContainerWidth = 25
            self.width = max([ uix.GetTextWidth(name) + arrowContainerWidth for (name, val,) in self.entries ] + [self.default_width])



    def OnUp(self, *args):
        if not self._Expanded():
            self.Expand()
        if self._Expanded():
            self._comboDropDown().BrowseEntries(1)



    def OnDown(self, *args):
        if not self._Expanded():
            self.Expand()
        if self._Expanded():
            self._comboDropDown().BrowseEntries(0)



    def Expand(self):
        if self._expanding:
            return 
        self._expanding = True
        if sm.GetService('connection').IsConnected():
            eve.Message('ComboExpand')
        log.LogInfo('Combo', self.name, '_expanding')
        par = uicls.Container(name='scroll', align=uiconst.TOPLEFT, width=200, height=200)
        m = uicore.layer.menu
        m.Flush()
        m.children.append(par)
        uicls.Container(name='blocker', parent=uicore.layer.menu, state=uiconst.UI_NORMAL, align=uiconst.TOALL)
        scroll = uicls.Scroll(name='_comboDropDown', parent=par, state=uiconst.UI_NORMAL)
        scroll.OnKillFocus = self.OnScrollFocusLost
        scroll.OnSelectionChange = self.OnScrollSelectionChange
        scroll.multiSelect = 0
        maxw = 0
        toth = 0
        strings = []
        scrolllist = []
        i = 0
        selIdx = 0
        for (key, val,) in self.entries:
            data = util.KeyVal()
            data.OnClick = self.OnEntryClick
            data.data = (key, val)
            data.label = unicode(key)
            if self.hints:
                data.hint = self.hints.get(key, '')
            scrolllist.append(listentry.Get('Generic', data=data))
            strings.append(unicode(key))
            if val == self.selectedValue:
                selIdx = i
            i += 1

        maxw = max([ uix.GetTextWidth(name) for name in strings ])
        self.sr.wndUnderlay = uicls.WindowUnderlay(parent=par, transparent=False)
        par.width = max(maxw + 24, self.absoluteRight - self.absoluteLeft - 2)
        scroll.Load(fixedEntryHeight=20, contentList=scrolllist)
        scroll.SetSelected(selIdx)
        scroll.ShowNodeIdx(selIdx)
        scroll.Confirm = self.Confirm
        scroll.OnRight = self.Confirm
        scroll.OnLeft = self.Confirm
        t = sum([ each.height for each in scroll.GetNodes()[:8] ])
        par.height = t + 4
        (par.left, par.top,) = (self.absoluteLeft + 1, min(self.absoluteBottom + 4, uicore.desktop.height - par.height - 8))
        par.state = uiconst.UI_NORMAL
        par.sr.scroll = scroll
        scroll.sr.scroll = scroll
        self._comboDropDown = _weakref.ref(scroll)
        self.sr.cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalClick)
        self._expanding = 0
        log.LogInfo('Combo', self.name, 'expanded')
        uicore.registry.SetFocus(scroll)



    def OnScrollSelectionChange(self, selected):
        if selected:
            self.SelectItemByLabel(selected[0].label)



    def Cleanup(self, setfocus = 1):
        if self.sr.cookie:
            uicore.event.UnregisterForTriuiEvents(self.sr.cookie)
            self.sr.cookie = None
        self._comboDropDown = None
        menu.KillAllMenus()
        if setfocus:
            uicore.registry.SetFocus(self)



    def OnChar(self, enteredChar, *args):
        if enteredChar < 32 and enteredChar != uiconst.VK_RETURN:
            return False
        if not self._Expanded():
            self.Expand()
        return True



    def OnGlobalMouseDown(self, downOn):
        if not uiutil.IsUnder(downOn, self._comboDropDown):
            uicore.layer.menu.Flush()



    def OnGlobalClick(self, fromwhere, *etc):
        if self._comboDropDown and self._comboDropDown():
            if uicore.uilib.mouseOver == self._comboDropDown() or uiutil.IsUnder(fromwhere, self._comboDropDown()):
                log.LogInfo('Combo.OnGlobalClick Ignoring all clicks from comboDropDown')
                return 1
        self.Cleanup()
        return 0



    def Startup(self, *args):
        pass



    def OnScrollFocusLost(self, *args):
        uthread.new(self.Confirm)




class Select(uicls.Scroll):
    __guid__ = 'xtriui.Select'

    def init(self):
        uicls.Scroll.init(self)
        self.isTabStop = 1



    def Startup(self, entries):
        uicls.Scroll.Startup(self)
        self.LoadEntries(entries)



    def LoadEntries(self, entries):
        uiutil.Update(self)
        scrolllist = []
        for (entryName, entryValue, selected,) in entries:
            scrolllist.append(listentry.Get('Generic', {'label': entryName,
             'value': entryValue,
             'isSelected': selected}))

        self.Load(contentList=scrolllist)



    def GetValue(self):
        return [ node.value for node in self.GetSelected() ] or None



    def SetValue(self, val):
        if type(val) != list:
            val = [val]
        for node in self.GetNodes():
            if node.value in val:
                self._SelectNode(node)





