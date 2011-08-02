import blue
import uix
import uiutil
import xtriui
import types
import uix
import draw
import uthread
import uicls
import uiconst

class MessageBox(uicls.Window):
    __guid__ = 'form.MessageBox'
    __nonpersistvars__ = ['suppress']

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.suppress = 0
        self.name = 'modal'
        self.scope = 'all'
        self.edit = None



    def Execute(self, text, title, buttons, icon, suppText, customicon = None, height = None, default = None, modal = True):
        if height is None:
            height = 210
        self.MakeUnMinimizable()
        self.HideHeader()
        self.SetMinSize([340, height])
        w = 340
        h = 210
        self.DefineIcons(icon, customicon)
        if title is None:
            title = mls.UI_GENERIC_INFORMATION
        self.sr.main = uiutil.FindChild(self, 'main')
        push = uicls.Container(name='push', align=uiconst.TOLEFT, parent=self.sr.topParent, width=64)
        caption = uicls.CaptionLabel(text=title, align=uiconst.CENTERLEFT, parent=self.sr.topParent, left=64, width=270, autowidth=0)
        self.SetTopparentHeight(max(56, caption.textheight + 16))
        if text:
            edit = uicls.Edit(parent=self.sr.main, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding), readonly=1)
            self.edit = edit
            uthread.new(self.SetText, text)
        self.DefineButtons(buttons, default=default)
        if suppText:
            self.ShowSupp(suppText)
        if modal:
            uicore.registry.SetFocus(self)



    def ShowSupp(self, text):
        bottom = uicls.Container(name='suppressContainer', parent=self.sr.main, align=uiconst.TOBOTTOM, height=20, idx=0)
        if self.edit:
            self.edit.height = 0
        self.sr.suppCheckbox = uicls.Checkbox(text=text, parent=bottom, configName='suppress', retval=0, checked=0, groupname=None, callback=self.ChangeSupp, align=uiconst.TOPLEFT, pos=(6, 0, 320, 0))



    def ChangeSupp(self, sender):
        self.suppress = sender.checked



    def SetText(self, txt):
        self.edit.autoScrollToBottom = 0
        self.edit.SetValue(txt, scrolltotop=1)



    def CloseX(self, *etc):
        if self.isModal:
            self.SetModalResult(uiconst.ID_CLOSE)
        else:
            uicls.Window.CloseX(self)




