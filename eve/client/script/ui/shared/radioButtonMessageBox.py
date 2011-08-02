import blue
import uix
import uiutil
import xtriui
import types
import uix
import draw
import uthread
import form
import uicls
import uiconst

class RadioButtonMessageBox(form.MessageBox):
    __guid__ = 'form.RadioButtonMessageBox'
    __nonpersistvars__ = ['suppress']

    def Execute(self, text, title, buttons, radioOptions, icon, suppText, customicon = None, height = None, width = None, default = None, modal = True):
        height = height or 230
        width = width or 340
        self.HideHeader()
        self.SetMinSize([width, height])
        self.width = width
        self.height = height
        self.DefineIcons(icon, customicon)
        if title is None:
            title = mls.UI_GENERIC_INFORMATION
        self.sr.main = uiutil.FindChild(self, 'main')
        push = uicls.Container(name='push', align=uiconst.TOLEFT, parent=self.sr.topParent, width=64)
        caption = uicls.CaptionLabel(text=title, align=uiconst.CENTERLEFT, parent=self.sr.topParent, left=64, width=270, autowidth=0)
        self.SetTopparentHeight(max(56, caption.textheight + 16))
        self.sr.radioContainer = uicls.Container(name='radioContainer', parent=self.sr.main, align=uiconst.TOBOTTOM, left=6, top=const.defaultPadding, width=const.defaultPadding, height=40)
        push = uicls.Container(name='push', align=uiconst.TOLEFT, parent=self.sr.radioContainer, width=4)
        self.sr.radioContainer2 = uicls.Container(name='radioContainer', parent=self.sr.radioContainer, align=uiconst.TOALL, pos=(6,
         const.defaultPadding,
         6,
         const.defaultPadding))
        self.sr.textContainer = uicls.Container(name='textContainer', parent=self.sr.main, align=uiconst.TOALL, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        if text:
            edit = uicls.Edit(parent=self.sr.textContainer, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding), readonly=1)
            self.edit = edit
            uthread.new(self.SetText, text)
        h = 0
        if radioOptions:
            self.radioboxID = 'radioButtonMessageBox_%s' % repr(title)
            radioSelection = settings.user.ui.Get(self.radioboxID, 'radioboxOption1Selected')
            for (index, label,) in enumerate(radioOptions):
                checkBox = uicls.Checkbox(text=label, parent=self.sr.radioContainer, configName=self.radioboxID, retval='radioboxOption%dSelected' % (index + 1), checked='radioboxOption%dSelected' % (index + 1) == radioSelection, groupname=self.radioboxID, callback=self.OnCheckboxChange)
                h += checkBox.height

        self.sr.radioContainer.height = h
        if suppText:
            self.ShowSupp(suppText)
        self.DefineButtons(buttons, default=default)
        if modal:
            uicore.registry.SetFocus(self)



    def ShowSupp(self, text):
        bottom = uicls.Container(name='suppressContainer', parent=self.sr.main, align=uiconst.TOBOTTOM, height=20, idx=0)
        if self.edit:
            self.edit.height = 0
        self.sr.suppCheckbox = uicls.Checkbox(text=text, parent=bottom, configName='suppress', retval=0, checked=0, groupname=None, callback=self.ChangeSupp, align=uiconst.TOPLEFT, pos=(6, 0, 320, 0))



    def OnCheckboxChange(self, checkbox, *args):
        config = checkbox.data['config']
        if checkbox.data.has_key('value'):
            if checkbox.data['value'] is None:
                settings.user.ui.Set(config, checkbox.checked)
            else:
                settings.user.ui.Set(config, checkbox.data['value'])



    def GetRadioSelection(self):
        return settings.user.ui.Get(self.radioboxID, 'radioboxOption1Selected')




