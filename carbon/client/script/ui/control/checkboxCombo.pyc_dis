#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/checkboxCombo.py
import uiconst
import uiutil
import uicls
import uthread
import _weakref
import localization
import log
import fontConst

class CheckboxComboCore(uicls.Container):
    __guid__ = 'uicls.CheckboxComboCore'
    default_name = 'CheckboxCombo'
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_fontsize = fontConst.DEFAULT_FONTSIZE
    default_fontStyle = None
    default_fontFamily = None
    default_fontPath = None
    default_shadow = [(1, -1, -1090519040)]
    default_options = []
    default_selected = []
    default_OnSelectionChange = None
    default_autoAdjustWidth = False
    default_minAutoWidth = 100
    default_width = 100
    default_height = 20
    default_cursor = uiconst.UICURSOR_SELECT
    isTabStop = True

    def ApplyAttributes(self, attributes):
        self.ErrorCheck(attributes)
        if attributes.align in (uiconst.TOLEFT, uiconst.TORIGHT, uiconst.TOALL):
            attributes.height = 0
        else:
            attributes.height = self.default_height
        uicls.Container.ApplyAttributes(self, attributes)
        self._expanding = False
        self._comboDropDown = None
        self.autoAdjustWidth = attributes.get('autoAdjustWidth', self.default_autoAdjustWidth)
        self.minAutoWidth = attributes.get('minAutoWidth', self.default_minAutoWidth)
        self.fontStyle = attributes.get('fontStyle', self.default_fontStyle)
        self.fontFamily = attributes.get('fontFamily', self.default_fontFamily)
        self.fontPath = attributes.get('fontPath', self.default_fontPath)
        self.fontsize = attributes.get('fontsize', self.default_fontsize)
        self.shadow = attributes.get('shadow', self.default_shadow)
        self.Prepare_()
        self.LoadOptions(attributes.get('options', self.default_options), attributes.get('selected', self.default_selected))
        if attributes.OnSelectionChange:
            self.OnSelectionChange = attributes.OnSelectionChange

    def ErrorCheck(self, attributes):
        if 'height' in attributes:
            raise RuntimeError('height cannot be set on CheckboxCombo')
        if 'width' in attributes and attributes.autoAdjustWidth:
            raise RuntimeError('Width and autoAdjustWidth cannot both be assigned to CheckboxCombo at once.', 'minAutoWidth can be used to assure minimum width when using autoAdjustWidth')
        if attributes.autoAdjustWidth and attributes.align in (uiconst.TOTOP, uiconst.TOBOTTOM, uiconst.TOALL):
            raise RuntimeError('autoAdjustWidth cannot be used with non-absolute alignments')

    def Prepare_(self):
        return uicls.Combo.Prepare_(self)

    def Prepare_SelectedText_(self):
        return uicls.Combo.Prepare_SelectedText_(self)

    def Prepare_Expander_(self):
        return uicls.Combo.Prepare_Expander_(self)

    def Prepare_ActiveFrame_(self):
        return uicls.Combo.Prepare_ActiveFrame_(self)

    def Prepare_Underlay_(self):
        return uicls.Combo.Prepare_Underlay_(self)

    def Prepare_Label_(self):
        return uicls.Combo.Prepare_Label_(self)

    def Prepare_OptionMenu_(self):
        uicore.layer.menu.Flush()
        menu = uicls.Container(parent=uicore.layer.menu, pos=(0, 0, 200, 200), align=uiconst.RELATIVE)
        scrollClipper = uicls.Container(parent=menu, clipChildren=True)
        menu.sr.scroll = uicls.Scroll(parent=scrollClipper, align=uiconst.TOPLEFT)
        menu.sr.scroll.HideBackground(alwaysHidden=True)
        menu.sr.scroll.RemoveActiveFrame()
        uicls.Fill(parent=menu, color=(1, 1, 1, 0.125))
        uicls.WindowUnderlay(parent=menu, transparent=False, padding=(0, 0, 0, 0))
        return (menu, menu.sr.scroll, uicls.SE_CheckboxComboCore)

    def Confirm(self):
        self.OnSelectionChange(self.GetKeys(), self.GetValue())
        if not self.destroyed:
            self.Cleanup()

    def LoadOptions(self, entries, selected = None, noSelectionHint = None):
        self.noSelectionHint = noSelectionHint or localization.GetByLabel('UI/Common/PleaseSelect')
        screwed = [ each for each in entries if not isinstance(each[0], basestring) ]
        if screwed:
            raise RuntimeError('NonStringKeys', repr(screwed))
        if not entries:
            raise RuntimeError('No combo entries')
        _entries = []
        for each in entries:
            doRaise = False
            if type(each) != tuple:
                doRaise = True
            elif len(each) == 2:
                label, value = each
                hint = None
            elif len(each) == 3:
                label, value, hint = each
            else:
                doRaise = True
            if doRaise:
                raise RuntimeError('Unsupported entry for CheckboxCombo', each, 'should be tuple of (label, value) or (label, value, hint)')
            _entries.append((label, value, hint))

        self.entries = _entries
        self.selectedKeys = []
        self.selectedValues = selected
        self.UpdateSelected()
        self.AutoAdjustWidth_()

    def OnEntryClick(self, entry, *args):
        uicore.Message('ComboEntrySelect')
        self.UpdateSelected()
        self.OnSelectionChange(self.GetKeys(), self.GetValue())

    def OnSelectionChange(self, entryKeys, entryValues):
        pass

    def UpdateSelected(self):
        selectedKeys = []
        menu = self.GetDropDownMenu()
        if menu:
            selectedValues = []
            for node in menu.sr.scroll.sr.nodes:
                key, val = node.data
                if node.isChecked:
                    selectedKeys.append(key)
                    selectedValues.append(val)

            self.selectedValues = selectedValues
        else:
            for option in self.entries:
                if self.IsSelectedValue(option[1]):
                    selectedKeys.append(option[0])

        self.selectedKeys = selectedKeys
        if selectedKeys:
            self.sr.selected.text = ', '.join(selectedKeys)
            if len(self.sr.selected.text) > 32:
                self.hint = '<br>'.join(selectedKeys)
            else:
                self.hint = ', '.join(selectedKeys)
        else:
            self.sr.selected.text = self.noSelectionHint
            self.hint = None

    def GetDropDownMenu(self):
        if self._comboDropDown:
            return self._comboDropDown()

    def IsSelectedValue(self, value):
        return value in self.selectedValues

    def GetKeys(self):
        return self.selectedKeys

    def GetValue(self):
        return self.selectedValues

    def Expand(self):
        if self._expanding:
            return
        self._expanding = True
        log.LogInfo('Combo', self.name, 'expanding')
        uicore.Message('ComboExpand')
        menu, scroll, entryClass = self.Prepare_OptionMenu_()
        showEntryIndex = None
        scrolllist = []
        for entryIndex, (label, returnValue, hint) in enumerate(self.entries):
            isChecked = self.IsSelectedValue(returnValue)
            if isChecked and showEntryIndex is None:
                showEntryIndex = entryIndex
            scrolllist.append(uicls.ScrollEntryNode(decoClass=entryClass, OnClick=self.OnEntryClick, data=(label, returnValue), fontStyle=self.fontStyle, fontFamily=self.fontFamily, fontPath=self.fontPath, fontsize=self.fontsize, hint=hint, isChecked=isChecked, label=label))

        l, t, w, h = self.GetAbsolute()
        endWidth = max(self.GetMaxEntryTextWidth() + 40, w)
        scroll.width = endWidth + 2
        scroll.LoadContent(contentList=scrolllist)
        endHeight = sum([ each.height for each in scroll.sr.nodes[:6] ])
        menu.left = l
        menu.top = min(t + h + 1, uicore.desktop.height - menu.height - 8)
        menu.width = endWidth
        scroll.height = endHeight + 2
        scroll.left = -1
        scroll.top = -1
        scroll.OnKillFocus = self.OnScrollFocusLost
        scroll.Confirm = self.Confirm
        scroll.OnUp = self.OnUp
        scroll.OnDown = self.OnDown
        scroll.OnRight = self.Confirm
        scroll.OnLeft = self.Confirm
        self._comboDropDown = _weakref.ref(menu)
        self.sr.cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalClick)
        self._expanding = False
        uicore.animations.FadeIn(scroll, duration=0.5)
        uicore.animations.MorphScalar(menu, 'height', startVal=10, endVal=endHeight, duration=0.125)
        if showEntryIndex is not None:
            scroll.SetSelected(showEntryIndex)
            uthread.new(self.ShowSelected, showEntryIndex)

    def AutoAdjustWidth_(self):
        currentAlign = self.GetAlign()
        if self.autoAdjustWidth and self.entries and currentAlign not in (uiconst.TOTOP, uiconst.TOBOTTOM, uiconst.TOALL):
            self.width = max(self.minAutoWidth, self.GetMaxEntryTextWidth() + self.GetExpanderIconWidth())

    def GetMaxEntryTextWidth(self):
        maxEntryWidth = 0
        for label, returnValue, hint in self.entries:
            textWidth = uicore.font.GetTextWidth(label, fontsize=self.fontsize, fontFamily=self.fontFamily, fontStyle=self.fontStyle, fontPath=self.fontPath)
            maxEntryWidth = max(maxEntryWidth, textWidth)

        return maxEntryWidth

    def ShowSelected(self, *args):
        return uicls.Combo.ShowSelected(self, *args)

    def Cleanup(self, *args, **kwds):
        return uicls.Combo.Cleanup(self, *args, **kwds)

    def OnGlobalClick(self, *args):
        return uicls.Combo.OnGlobalClick(self, *args)

    def OnScrollFocusLost(self, *args):
        uthread.new(self.Confirm)

    def OnChar(self, *args):
        return uicls.Combo.OnChar(self, *args)

    def _Expanded(self):
        return uicls.Combo._Expanded(self)

    def OnClick(self, *args):
        return uicls.Combo.OnClick(self, *args)

    def OnUp(self, *args):
        menu = self.GetDropDownMenu()
        if menu:
            menu.sr.scroll.Scroll(0.5)

    def OnDown(self, *args):
        if not self._Expanded():
            self.Expand()
        else:
            menu = self.GetDropDownMenu()
            if menu:
                menu.sr.scroll.Scroll(-0.5)

    def OnSetFocus(self, *args):
        return uicls.Combo.OnSetFocus(self, *args)

    def OnKillFocus(self, *args):
        return uicls.Combo.OnKillFocus(self, *args)

    def Close(self, *args, **kwds):
        return uicls.Combo.Close(self, *args, **kwds)

    def GetExpanderIconWidth(self):
        return uicls.Combo.GetExpanderIconWidth(self)


class SE_CheckboxComboCore(uicls.SE_BaseClassCore):
    __guid__ = 'uicls.SE_CheckboxComboCore'
    ENTRYHEIGHT = 21

    def ApplyAttributes(self, attributes):
        uicls.SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.label = uicls.Label(name='text', parent=self, pos=(22, 0, 0, 0), state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, maxLines=1)
        self.checkBox = uicls.Checkbox(parent=self, align=uiconst.CENTERLEFT, pos=(4, 0, 16, 16), state=uiconst.UI_DISABLED)
        self.hilite = uicls.Fill(name='hilite', parent=self, align=uiconst.TOALL, color=(1.0, 1.0, 1.0, 0.25), state=uiconst.UI_HIDDEN)

    def Load(self, node):
        self.label.fontFamily = node.fontFamily
        self.label.fontPath = node.fontPath
        self.label.fontStyle = node.fontStyle
        self.label.fontsize = node.fontsize
        self.label.text = node.label
        self.checkBox.SetChecked(bool(node.isChecked), report=False)

    def OnClick(self, *args):
        if self.sr.node:
            if self.sr.node.OnClick:
                self.sr.node.OnClick(self)

    def OnMouseDown(self, *args):
        uicore.Message('ListEntryClick')
        self.checkBox.SetChecked(not self.checkBox.GetValue())
        self.sr.node.isChecked = self.checkBox.GetValue()

    def OnMouseEnter(self, *args):
        uicore.Message('ListEntryEnter')
        self.hilite.state = uiconst.UI_DISABLED

    def OnMouseExit(self, *args):
        self.hilite.state = uiconst.UI_HIDDEN