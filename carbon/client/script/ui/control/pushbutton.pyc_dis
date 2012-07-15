#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/pushbutton.py
import fontConst
import uicls
import uiconst
import uiutil
import uthread
import trinity

class PushButtonCore(uicls.Container):
    __guid__ = 'uicls.PushButtonCore'
    default_name = 'pushButton'
    default_align = uiconst.RELATIVE
    default_width = 32
    default_height = 32
    default_icon = None
    default_state = uiconst.UI_NORMAL

    def Prepare_(self, *args, **kw):
        self.sr.icon = uicls.Icon(name='icon', parent=self, align=uiconst.RELATIVE, state=uiconst.UI_DISABLED)
        self.sr.underlay = uicls.Frame(parent=self, frameConst=uiconst.FRAME_FILLED_CORNER4, state=uiconst.UI_HIDDEN, color=(1.0, 1.0, 1.0, 0.3), name='underlay')
        self._isActive = False

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.Prepare_()
        icon = attributes.get('icon', self.default_icon)
        if icon:
            self.SetIcon(icon)

    def SetUnderlayPadding(self, padding):
        self.sr.underlay.padLeft, self.sr.underlay.padTop, self.sr.underlay.padRight, self.sr.underlay.padBottom = padding

    def OnClick(self, *args):
        pass

    def OnMouseDown(self, *args):
        self.sr.icon.top = 1

    def OnMouseUp(self, *args):
        self.sr.icon.top = 0

    def OnMouseEnter(self, *args):
        self.sr.underlay.state = uiconst.UI_DISABLED

    def OnMouseExit(self, *args):
        if not self._isActive:
            self.sr.underlay.state = uiconst.UI_HIDDEN

    def SetIcon(self, icon):
        self.sr.icon.LoadIcon(icon)
        self.width = self.sr.icon.width
        self.height = self.sr.icon.height

    def MakeInactive(self):
        self._isActive = False
        self.sr.underlay.state = uiconst.UI_HIDDEN
        self.sr.icon.top = 0

    def MakeActive(self):
        self._isActive = True
        self.sr.underlay.state = uiconst.UI_DISABLED
        groupID = getattr(self, 'groupID', None)
        if groupID:
            for each in self.parent.children:
                if each != self and isinstance(each, PushButtonCore) and getattr(each, 'groupID', None) == groupID:
                    each.MakeInactive()