#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/modules/messagebox.py
import uiconst
import uicls
import localization

class MessageBoxCore(uicls.Window):
    __guid__ = 'uicls.MessageBoxCore'
    default_width = 340
    default_height = 210

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.MakeUnMinimizable()
        self.suppress = 0
        self.name = 'modal'
        self.scope = 'all'
        self.edit = None

    def Prepare_Header_(self):
        pass

    def Prepare_Caption_(self):
        self.sr.caption = uicls.Label(text='', align=uiconst.CENTERLEFT, parent=self.sr.topArea, pos=(64, 0, 270, 0))

    def Execute(self, text, title, buttons, icon, suppText, customicon = None, height = None, default = None):
        if title is None:
            title = localization.GetByLabel('/Carbon/UI/Common/Information')
        self.sr.topArea = self.Split(uiconst.SPLITTOP, 56, line=0)
        self.SetButtons(buttons, defaultBtn=default)
        if suppText:
            self.ShowSupp(suppText)
        if title:
            self.Prepare_Caption_()
            if self.sr.caption:
                self.sr.caption.text = title
                self.sr.topArea.height = max(56, self.sr.caption.textheight + 16)
        if text:
            self.edit = uicls.Edit(parent=self.sr.content, pos=(0, 0, 0, 0), align=uiconst.TOALL, readonly=True, setvalue=text)

    def ShowSupp(self, text):
        bottom = uicls.Container(name='suppressContainer', parent=self.sr.content, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 20), idx=0)
        self.sr.suppCheckbox = uicls.Checkbox(text=text, parent=bottom, configName='suppress', callback=self.ChangeSupp, align=uiconst.RELATIVE, pos=(6, 0, 320, 18))

    def ChangeSupp(self, sender):
        self.suppress = sender.checked

    def SetText(self, txt):
        self.edit.SetValue(txt, scrolltotop=1)