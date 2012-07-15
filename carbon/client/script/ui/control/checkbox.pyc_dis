#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/checkbox.py
import uthread
import uiconst
import uiutil
import uicls
import log

class CheckboxCore(uicls.Container):
    __guid__ = 'uicls.CheckboxCore'
    default_name = 'checkbox'
    default_align = uiconst.TOTOP
    default_text = ''
    default_height = 20
    default_configName = None
    default_retval = None
    default_checked = 0
    default_groupname = None
    default_callback = None
    default_prefstype = ('public', 'ui')
    default_clipChildren = 1
    default_state = uiconst.UI_NORMAL
    default_wrapLabel = True
    default_fontsize = 10
    default_fontStyle = None
    default_fontFamily = None
    default_fontPath = None

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self._groupName = None
        self._checked = False
        self.isTabStop = 1
        self.sr.label = None
        self.sr.active = None
        self.sr.diode = None
        self.cursor = 1
        self.name = ''
        self.wrapLabel = attributes.get('wrapLabel', self.default_wrapLabel)
        self.fontStyle = attributes.get('fontStyle', self.default_fontStyle)
        self.fontFamily = attributes.get('fontFamily', self.default_fontFamily)
        self.fontPath = attributes.get('fontPath', self.default_fontPath)
        self.fontsize = attributes.get('fontsize', self.default_fontsize)
        self.Prepare_()
        self.data = {'config': attributes.get('configName', self.default_configName),
         'value': attributes.get('retval', self.default_retval),
         'prefstype': attributes.get('prefstype', self.default_prefstype)}
        if self.data['config'] is not None:
            self.name = self.data['config']
        self.OnChange = attributes.get('callback', self.default_callback)
        self.SetGroup(attributes.get('groupname', self.default_groupname))
        self.SetChecked(attributes.get('checked', self.default_checked), 0)
        self.SetLabelText(attributes.get('text', self.default_text))

    def Prepare_(self):
        self.Prepare_Label_()
        self.Prepare_Active_()

    def Prepare_Label_(self):
        if not self.wrapLabel:
            align = uiconst.CENTERLEFT
            padding = 0
            pos = (18, 0, 0, 0)
        else:
            align = uiconst.TOTOP
            padding = (18, 2, 0, 0)
            pos = (0, 0, 0, 0)
        self.sr.label = uicls.Label(text='', parent=self, name='text', align=align, fontStyle=self.fontStyle, fontFamily=self.fontFamily, fontPath=self.fontPath, fontsize=self.fontsize, letterspace=1, state=uiconst.UI_DISABLED, padding=padding, pos=pos, uppercase=1, maxLines=1 if not self.wrapLabel else None)
        self.sr.label.OnSizeChanged = self.OnSizeChanged

    def Prepare_Active_(self):
        self.sr.active = uicls.Icon(name='active', parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, pos=(0, 0, 16, 16), icon='ui_1_16_157')

    def Prepare_Diode_(self):
        if not self.sr.diode:
            self.sr.diode = uicls.ImageButton(name='diode', parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(0, 0, 16, 16), icon='ui_1_16_111', idx=0)
        if self._groupName:
            icon = 111
            uiutil.MapIcon(self.sr.active, 'ui_1_16_157')
        else:
            icon = 112
            uiutil.MapIcon(self.sr.active, 'ui_1_16_158')
        if self._checked:
            icon -= 2
            self.sr.diode.SetRGB(1.0, 1.0, 1.0, 1.0)
        else:
            self.sr.diode.SetRGB(1.0, 1.0, 1.0, 0.7)
        self.sr.diode.SetMouseIdleIcon('ui_1_16_%s' % icon)
        self.sr.diode.SetMouseOverIcon('ui_1_16_%s' % (icon + 16))
        self.sr.diode.SetMouseDownIcon('ui_1_16_%s' % (icon + 32))

    def OnSizeChanged(self, *args):
        self.RefreshHeight()

    def OnMouseUp(self, *args):
        if uicore.uilib.mouseOver is self:
            uthread.new(self.ToggleState)

    def ToggleState(self):
        if not self or self.destroyed:
            return
        if self._groupName is None:
            self.SetChecked(not self._checked)
            return
        par = uiutil.GetWindowAbove(self)
        if par is None:
            par = self.parent
        for each in par.Find('trinity.Tr2Sprite2dContainer'):
            if each == self:
                continue
            if isinstance(each, uicls.CheckboxCore) and each._groupName == self._groupName:
                each.SetChecked(0, 0)

        if not self.destroyed:
            self.SetChecked(1)

    def OnChar(self, char, flag):
        if char == uiconst.VK_SPACE:
            uthread.pool('checkbox::OnChar', self.ToggleState)
            return 1

    def OnSetFocus(self, *args):
        if self and not self.destroyed and self.parent and self.parent.name == 'inlines':
            if self.parent.parent and self.parent.parent.sr.node:
                browser = uiutil.GetBrowser(self)
                if browser:
                    uthread.new(browser.ShowObject, self)
        if self.sr.active:
            self.sr.active.state = uiconst.UI_DISABLED

    def OnKillFocus(self, *etc):
        if self.sr.active:
            self.sr.active.state = uiconst.UI_HIDDEN

    def SetValue(self, value):
        self.SetChecked(value)

    def GetValue(self):
        return self._checked

    def GetGroup(self):
        return self._groupName

    def SetGroup(self, groupName):
        force = groupName != self._groupName
        self._groupName = groupName
        if force:
            self.Prepare_Diode_()
        self.SetChecked(self._checked, 0)

    def SetLabelText(self, labeltext):
        self.RefreshHeight()
        self.sr.label.text = labeltext
        if self.GetAlign() not in (uiconst.TOTOP, uiconst.TOBOTTOM):
            self.ChangeWidth()
        self.RefreshHeight()

    def ChangeWidth(self, *args):
        self.width = max(20, self.sr.label.padLeft + self.sr.label.left + self.sr.label.textwidth + self.sr.label.padRight) + 1

    def GetLabelText(self):
        return self.sr.label.GetText()

    def SetTextColor(self, color):
        self.sr.label.SetTextColor(color)

    def SetChecked(self, onoff, report = 1):
        onoff = onoff or 0
        self._checked = bool(onoff)
        self.Prepare_Diode_()
        if report:
            self.UpdateSettings()
            if self.OnChange:
                self.OnChange(self)

    def UpdateSettings(self):
        prefstype = self.data.get('prefstype', None)
        if prefstype is None:
            return
        if self._groupName and not self._checked:
            return
        config = self.data.get('config', None)
        value = self.data.get('value', None)
        if value is None:
            value = self._checked
        s = uiutil.GetAttrs(settings, *prefstype)
        try:
            s.Set(config, value)
        except:
            log.LogError('Failed to assign setting to: %s, %s' % (prefstype, config))

    def RefreshHeight(self):
        minHeight = 12
        if self.sr.diode:
            minHeight = self.sr.diode.height + 2
        self.height = max(minHeight, self.sr.label.textheight + self.sr.label.top * 2)

    def GetSelectedFromGroup(self):
        if self._groupName:
            par = uiutil.GetWindowAbove(self)
            if par is None:
                par = self.parent
            for each in par.Find('trinity.Tr2Sprite2dContainer'):
                if isinstance(each, uicls.CheckboxCore) and each._groupName == self._groupName:
                    if each.GetValue():
                        return each