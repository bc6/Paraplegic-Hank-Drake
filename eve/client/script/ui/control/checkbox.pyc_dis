#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/control/checkbox.py
import util
import uiutil
import blue
import uthread
import uiconst
import uicls
import trinity
TOPMARGIN = 3

class Checkbox(uicls.CheckboxCore):
    __guid__ = 'uicls.Checkbox'
    default_height = 100
    default_prefstype = ('user', 'ui')

    def ApplyAttributes(self, attributes):
        uicls.CheckboxCore.ApplyAttributes(self, attributes)
        self.prefstype = attributes.get('prefstype', self.default_prefstype)
        if self.prefstype == 1:
            self.prefstype = ('char', 'ui')
        elif self.prefstype == 2:
            self.prefstype = 'prefs'

    def __getattr__(self, k):
        if k == 'groupName' and self.__dict__.has_key('_groupName'):
            return self.__dict__['_groupName']
        if k == 'checked' and self.__dict__.has_key('_checked'):
            return self.__dict__['_checked']
        return uicls.CheckboxCore.__getattr__(self, k)

    def Prepare_Label_(self):
        if self.GetAlign() == uiconst.TOPRIGHT:
            leftPad = 0
            rightPad = 16
        else:
            leftPad = 16
            rightPad = 0
        if not self.wrapLabel:
            align = uiconst.CENTERLEFT
            padding = 0
            pos = (leftPad,
             0,
             0,
             0)
            maxLines = 1
        else:
            align = uiconst.TOTOP
            padding = (leftPad,
             TOPMARGIN,
             rightPad,
             0)
            pos = (0, 0, 0, 0)
            maxLines = None
        self.sr.label = uicls.EveLabelSmall(text='', parent=self, name='text', align=align, state=uiconst.UI_DISABLED, padding=padding, pos=pos, maxLines=maxLines)

    def Prepare_Diode_(self):
        if self.sr.diode:
            self.sr.diode.Close()
        self.sr.diode = uicls.Container(parent=self, pos=(-1, 1, 16, 16), name='diode', state=uiconst.UI_DISABLED, align=uiconst.RELATIVE)
        if self._groupName is None:
            self.sr.active = uicls.Sprite(parent=self.sr.diode, pos=(0, 0, 16, 16), name='active', state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/Shared/checkboxActive.png')
            self.checkMark = uicls.Sprite(parent=self.sr.diode, pos=(0, 0, 16, 16), name='self_ok', state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/Shared/checkboxChecked.png')
            uicls.Sprite(parent=self.sr.diode, pos=(0, 0, 16, 16), name='shape', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/checkboxShape.png')
        else:
            self.sr.active = uicls.Sprite(parent=self.sr.diode, pos=(0, 0, 16, 16), name='active', state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/Shared/checkboxActiveOval.png')
            self.checkMark = uicls.Sprite(parent=self.sr.diode, pos=(0, 0, 16, 16), name='self_ok', state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/Shared/checkboxCheckedOval.png')
            uicls.Sprite(parent=self.sr.diode, pos=(0, 0, 16, 16), name='shape', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/checkboxShapeOval.png')

    def Prepare_Active_(self):
        pass

    def SetChecked(self, onoff, report = 1):
        onoff = onoff or 0
        self._checked = int(onoff)
        if self.sr.diode is None:
            self.Prepare_Diode_()
        self.checkMark.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][self._checked]
        if report:
            self.UpdateSettings()
            if self.OnChange:
                self.OnChange(self)

    def ToggleState(self, *args):
        if not self or self.destroyed:
            return
        if self._checked:
            uicore.Message('DiodeDeselect')
        else:
            uicore.Message('DiodeClick')
        uicls.CheckboxCore.ToggleState(self, *args)

    def RefreshHeight(self):
        label = uiutil.GetChild(self, 'text')
        minHeight = 12
        if self.sr.diode:
            minHeight = 18
        self.height = max(minHeight, label.textheight + TOPMARGIN * 2)

    def SetLabel(self, labeltext):
        self.SetLabelText(labeltext)