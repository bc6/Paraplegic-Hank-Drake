import uiconst
import uiutil
import uicls
import uthread
import _weakref
import localization
import log
import fontConst
import blue

class ComboCore(uicls.Container):
    __guid__ = 'uicls.ComboCore'
    default_name = 'combo'
    default_align = uiconst.TOTOP
    default_label = ''
    default_state = uiconst.UI_NORMAL
    default_fontsize = fontConst.DEFAULT_FONTSIZE
    default_fontStyle = None
    default_fontFamily = None
    default_fontPath = None
    default_shadow = [(1, -1, -1090519040)]
    default_prefskey = None
    default_options = []
    default_select = None
    default_callback = None
    default_adjustWidth = False
    default_width = 100
    default_height = 20
    default_cursor = uiconst.UICURSOR_SELECT

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.isTabStop = 1
        self.sr.activeframe = None
        self.sr.label = None
        self.selectedValue = None
        self._expanding = False
        self._comboDropDown = None
        self.adjustWidth = attributes.get('adjustWidth', self.default_adjustWidth)
        self.prefskey = attributes.get('prefskey', self.default_prefskey)
        self.fontStyle = attributes.get('fontStyle', self.default_fontStyle)
        self.fontFamily = attributes.get('fontFamily', self.default_fontFamily)
        self.fontPath = attributes.get('fontPath', self.default_fontPath)
        self.fontsize = attributes.get('fontsize', self.default_fontsize)
        self.shadow = attributes.get('shadow', self.default_shadow)
        self.Prepare_()
        self.OnChange = attributes.get('callback', self.default_callback)
        self.SetLabel_(attributes.get('label', self.default_label))
        self.LoadOptions(attributes.get('options', self.default_options), attributes.get('select', self.default_select))
        currentAlign = self.GetAlign()
        if self.adjustWidth and currentAlign not in (uiconst.TOTOP, uiconst.TOBOTTOM, uiconst.TOALL):
            self.AutoAdjustWidth_()
        else:
            self.width = attributes.get('width', self.default_width)
        if currentAlign in (uiconst.TOLEFT, uiconst.TORIGHT, uiconst.TOALL):
            self.height = 0
        else:
            self.height = self.default_height



    def Prepare_(self):
        self.sr.content = uicls.Container(parent=self, name='__maincontent')
        self.sr.textclipper = uicls.Container(parent=self.sr.content, name='__textclipper', clipChildren=True)
        self.Prepare_SelectedText_()
        self.Prepare_Expander_()
        self.Prepare_ActiveFrame_()
        self.Prepare_Underlay_()
        self.Prepare_Label_()



    def Prepare_SelectedText_(self):
        self.sr.selected = uicls.Label(text='', fontStyle=self.fontStyle, fontFamily=self.fontFamily, fontPath=self.fontPath, fontsize=self.fontsize, parent=self.sr.textclipper, name='value', align=uiconst.CENTERLEFT, left=6, state=uiconst.UI_DISABLED)



    def Prepare_Underlay_(self):
        self.sr.underlay = uicls.Frame(name='__underlay', color=(0.0, 0.0, 0.0, 0.5), frameConst=uiconst.FRAME_FILLED_CORNER0, parent=self)



    def Prepare_Expander_(self):
        self.sr.expanderParent = uicls.Container(parent=self.sr.content, align=uiconst.TORIGHT, pos=(0, 0, 16, 0), idx=0, state=uiconst.UI_DISABLED, name='__expanderParent')
        self.sr.expander = uicls.Icon(parent=self.sr.expanderParent, align=uiconst.CENTER, icon='ui_1_16_129', pos=(1, -1, 0, 0))



    def Prepare_ActiveFrame_(self):
        self.sr.activeframe = uicls.Frame(name='__activeframe', parent=self, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, idx=0, color=(1.0, 1.0, 1.0, 0.75))



    def Prepare_Label_(self):
        self.sr.label = uicls.Label(text='', parent=self, name='label', align=uiconst.TOPLEFT, pos=(1, -13, 0, 0), fontsize=9, letterspace=2, state=uiconst.UI_DISABLED, idx=0)



    def HideText(self):
        self.sr.textclipper.state = uiconst.UI_HIDDEN



    def Close(self, *args, **kwds):
        self.Cleanup(0)
        uicls.Container.Close(self, *args, **kwds)



    def Confirm(self):
        if self.OnChange:
            val = self.GetValue()
            key = self.GetKey()
            self.OnChange(self, key, val)
        if not self.destroyed:
            self.Cleanup()



    def OnUp(self, *args):
        if not self._Expanded():
            self.Expand()
        if self._Expanded():
            self._comboDropDown().sr.scroll.BrowseNodes(1)



    def OnDown(self, *args):
        if not self._Expanded():
            self.Expand()
        if self._Expanded():
            self._comboDropDown().sr.scroll.BrowseNodes(0)



    def SetHint(self, hint):
        self.hint = hint



    def SetLabel_(self, label):
        pass



    def OnSetFocus(self, *args):
        if self and not self.destroyed and self.parent and self.parent.name == 'inlines':
            if self.parent.parent and self.parent.parent.sr.node:
                browser = uiutil.GetBrowser(self)
                if browser:
                    uthread.new(browser.ShowObject, self)
        if self.sr.activeframe:
            self.sr.activeframe.state = uiconst.UI_DISABLED



    def OnKillFocus(self, *etc):
        if self.sr.activeframe:
            self.sr.activeframe.state = uiconst.UI_HIDDEN



    def LoadOptions(self, entries, select = None, hints = None):
        screwed = [ each for each in entries if not isinstance(each[0], basestring) ]
        if screwed:
            raise RuntimeError('NonStringKeys', repr(screwed))
        entries = entries or [(localization.GetByLabel('/Carbon/UI/Controls/Combo/NoChoices'), None, None)]
        self.entries = entries
        self.hints = hints
        if select == '__random__':
            import random
            select = random.choice(entries)[1]
        elif select is None:
            select = self.entries[0][1]
        success = self.SelectItemByValue(select)
        if not success:
            self.SelectItemByValue(self.entries[0][1])
        self.AutoAdjustWidth_()



    def AutoAdjustWidth_(self):
        currentAlign = self.GetAlign()
        if self.adjustWidth and self.entries and currentAlign not in (uiconst.TOTOP, uiconst.TOBOTTOM, uiconst.TOALL):
            arrowContainerWidth = 25
            self.width = max([ uicore.font.GetTextWidth(each[0], fontFamily=self.fontFamily, fontStyle=self.fontStyle, fontPath=self.fontPath, fontsize=self.fontsize) + arrowContainerWidth for each in self.entries ] + [self.default_width])



    def GetKey(self):
        return self.sr.selected.text



    def GetValue(self):
        if self.selectedValue is not None:
            return self.selectedValue
        else:
            return 



    def GetIndex(self):
        if self.sr.selected.text:
            i = 0
            for each in self.entries:
                label = each[0]
                if label == self.sr.selected.text:
                    return i
                i += 1




    def SelectItemByIndex(self, i):
        self.SelectItemByLabel(self.entries[i][0])



    def SelectItemByLabel(self, label):
        for each in self.entries:
            if each[0] == label:
                self.sr.selected.text = label
                self.selectedValue = each[1]
                return 

        raise RuntimeError('LabelNotInEntries', label)



    def SelectItemByValue(self, val):
        for each in self.entries:
            if each[1] == val:
                self.sr.selected.text = each[0]
                self.selectedValue = val
                return True

        log.LogWarn('ValueNotInEntries', val)
        return False


    SetValue = SelectItemByValue

    def UpdateSettings(self):
        prefskey = self.prefskey
        if prefskey is None:
            return 
        config = prefskey[-1]
        prefstype = prefskey[:-1]
        s = uiutil.GetAttrs(settings, *prefstype)
        if s:
            s.Set(config, self.GetValue())



    def _Expanded(self):
        return bool(self._comboDropDown and self._comboDropDown())



    def OnMouseDown(self, *args):
        if not self._Expanded():
            uthread.new(self.Expand)



    def Prepare_OptionMenu_(self):
        uicore.layer.menu.Flush()
        menu = uicls.Container(parent=uicore.layer.menu, pos=(0, 0, 200, 200), align=uiconst.RELATIVE)
        menu.sr.scroll = uicls.Scroll(parent=menu)
        uicls.Fill(parent=menu, color=(0.0, 0.0, 0.0, 1.0))
        return (menu, menu.sr.scroll, uicls.SE_Generic)



    def Expand(self):
        if self._expanding:
            return 
        self._expanding = True
        uicore.Message('ComboExpand')
        log.LogInfo('Combo', self.name, 'expanding')
        (menu, scroll, entryClass,) = self.Prepare_OptionMenu_()
        i = 0
        maxw = 0
        selIdx = 0
        scrolllist = []
        for each in self.entries:
            label = each[0]
            returnValue = each[1]
            if len(each) > 2:
                hint = each[2]
            elif self.hints:
                hint = self.hints.get(label, '')
            else:
                hint = ''
            data = {}
            data['OnClick'] = self.OnEntryClick
            data['data'] = (label, returnValue)
            data['label'] = unicode(label)
            data['fontStyle'] = self.fontStyle
            data['fontFamily'] = self.fontFamily
            data['fontPath'] = self.fontPath
            data['fontsize'] = self.fontsize
            data['shadow'] = (self.shadow,)
            data['decoClass'] = entryClass
            data['hint'] = hint
            if returnValue == self.selectedValue:
                data['selected'] = True
                selIdx = i
            scrolllist.append(uicls.ScrollEntryNode(**data))
            maxw = max(maxw, uicore.font.GetTextWidth(data['label'], fontsize=self.fontsize, fontFamily=self.fontFamily, fontStyle=self.fontStyle, fontPath=self.fontPath))
            i += 1

        (l, t, w, h,) = self.GetAbsolute()
        menu.width = max(maxw + 24, w)
        scroll.LoadContent(contentList=scrolllist)
        totalHeight = sum([ each.height for each in scroll.sr.nodes[:6] ])
        menu.height = totalHeight + 2 + scroll.padTop + scroll.padBottom
        menu.left = l
        menu.top = min(t + h + 1, uicore.desktop.height - menu.height - 8)
        scroll.SetSelected(selIdx)
        scroll.OnKillFocus = self.OnScrollFocusLost
        scroll.OnSelectionChange = self.OnScrollSelectionChange
        scroll.Confirm = self.Confirm
        scroll.OnUp = self.OnUp
        scroll.OnDown = self.OnDown
        scroll.OnRight = self.Confirm
        scroll.OnLeft = self.Confirm
        self._comboDropDown = _weakref.ref(menu)
        self._expanding = False
        uthread.new(self.ShowSelected, selIdx)



    def GetExpanderIconWidth(self):
        if self.sr.expanderParent:
            return self.sr.expanderParent.width + self.sr.expanderParent.padLeft + self.sr.expanderParent.padRight
        return 0



    def ShowSelected(self, selectedIndex, *args):
        blue.pyos.synchro.Yield()
        scroll = self._comboDropDown().sr.scroll
        uicore.registry.SetFocus(scroll)
        scroll.ShowNodeIdx(selectedIndex)



    def OnEntryClick(self, entry, *args):
        uicore.Message('ComboEntrySelect')
        (key, val,) = entry.sr.node.data
        self.SelectItemByValue(val)
        self.Cleanup()
        if self.OnChange:
            self.OnChange(self, key, val)
        log.LogInfo('Combo.OnEntryClick END')



    def OnComboClose(self, *args):
        self.Cleanup(0)



    def Cleanup(self, setfocus = 1):
        self._comboDropDown = None
        uicore.layer.menu.Flush()
        if setfocus:
            uicore.registry.SetFocus(self)



    def OnScrollFocusLost(self, *args):
        uthread.new(self.Confirm)



    def OnScrollSelectionChange(self, selected):
        if selected:
            self.SelectItemByLabel(selected[0].label)



    def OnChar(self, enteredChar, *args):
        if enteredChar < 32 and enteredChar != uiconst.VK_RETURN:
            return False
        if not self._Expanded():
            self.Expand()
        return True




class SelectCore(uicls.ScrollCore):
    __guid__ = 'uicls.SelectCore'

    def LoadEntries(self, entries):
        scrolllist = []
        for (entryName, entryValue, selected,) in entries:
            scrolllist.append(uicls.ScrollEntryNode(label=entryName, value=entryValue, isSelected=selected))

        self.LoadContent(contentList=scrolllist)



    def GetValue(self):
        return [ node.value for node in self.GetSelected() ] or None



    def SetValue(self, val):
        if type(val) != list:
            val = [val]
        for node in self.GetNodes():
            if node.value in val:
                self._SelectNode(node)





