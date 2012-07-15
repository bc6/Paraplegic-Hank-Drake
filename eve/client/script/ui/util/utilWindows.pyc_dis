#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/util/utilWindows.py
import localization
import uix
import uiutil
import util
import uiconst
import uicls

class NamePopupWnd(uicls.Window):
    __guid__ = 'form.NamePopupWnd'
    default_width = 240
    default_height = 90
    default_minSize = (default_width, default_height)
    default_windowID = 'setNewName'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Confirm, cancelFunc=self.Cancel)
        caption = attributes.get('caption', localization.GetByLabel('UI/Common/Name/TypeInName'))
        if caption is None:
            caption = localization.GetByLabel('UI/Common/Name/TypeInName')
        self.SetCaption(caption)
        self.SetTopparentHeight(0)
        self.MakeUnResizeable()
        self.label = attributes.get('label', localization.GetByLabel('UI/Common/Name/TypeInName'))
        if self.label is None:
            self.label = localization.GetByLabel('UI/Common/Name/TypeInName')
        self.setvalue = attributes.get('setvalue', '')
        self.maxLength = attributes.get('maxLength', None)
        self.passwordChar = attributes.get('passwordChar', None)
        self.funcValidator = attributes.validator or self.CheckName
        self.ConstructLayout()

    def ConstructLayout(self):
        cont = uicls.Container(parent=self.sr.main, align=uiconst.TOALL, pos=(const.defaultPadding,
         16,
         const.defaultPadding,
         const.defaultPadding))
        self.newName = uicls.SinglelineEdit(name='namePopup', parent=cont, label=self.label, setvalue=self.setvalue, align=uiconst.TOTOP, maxLength=self.maxLength, passwordCharacter=self.passwordChar, autoselect=True, OnReturn=self.Confirm)
        uicore.registry.SetFocus(self.newName)

    def CheckName(self, name, *args):
        name = self.newName.GetValue()
        if not len(name) or len(name) and len(name.strip()) < 1:
            return localization.GetByLabel('UI/Common/PleaseTypeSomething')

    def Confirm(self, *args):
        if not hasattr(self, 'newName'):
            return
        newName = self.newName.GetValue()
        error = self.funcValidator(newName)
        if error:
            eve.Message('CustomInfo', {'info': error})
        else:
            self.result = newName
            self.SetModalResult(1)

    def Cancel(self, *args):
        self.result = None
        self.SetModalResult(0)


def NamePopup(caption = None, label = None, setvalue = '', maxLength = None, passwordChar = None, validator = None):
    wnd = NamePopupWnd.Open(caption=caption, label=label, setvalue=setvalue, maxLength=maxLength, passwordChar=passwordChar, validator=validator)
    if wnd.ShowModal() == 1:
        return wnd.result


exports = {'uiutil.NamePopup': NamePopup}