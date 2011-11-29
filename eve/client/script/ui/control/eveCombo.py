import uicls
import uiconst
import uiutil
import uthread
import listentry
import fontConst

class Combo(uicls.ComboCore):
    __guid__ = 'uicls.Combo'
    default_fontsize = fontConst.EVE_MEDIUM_FONTSIZE
    default_labelleft = None
    default_align = uiconst.TOPLEFT
    default_width = 86
    default_height = 18

    def ApplyAttributes(self, attributes):
        self.labelleft = attributes.get('labelleft', self.default_labelleft)
        uicls.ComboCore.ApplyAttributes(self, attributes)
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
        if label:
            self.sr.label.text = label
            if self.labelleft is not None:
                self.sr.label.top = 0
                self.sr.label.SetAlign(uiconst.CENTERLEFT)
            self.sr.label.state = uiconst.UI_DISABLED
        else:
            self.sr.label.state = uiconst.UI_HIDDEN



    def Prepare_SelectedText_(self):
        self.sr.selected = uicls.EveLabelMedium(text='', parent=self.sr.textclipper, name='value', top=2, left=6, state=uiconst.UI_DISABLED)



    def Prepare_Underlay_(self):
        self.sr.background = uicls.Container(name='_underlay', parent=self, state=uiconst.UI_DISABLED)
        self.sr.backgroundFrame = uicls.BumpedUnderlay(parent=self.sr.background)



    def Prepare_Label_(self):
        self.sr.label = uicls.EveLabelSmall(text='', parent=self, name='label', top=-13, left=1, state=uiconst.UI_HIDDEN, idx=1)



    def Prepare_OptionMenu_(self):
        uicore.layer.menu.Flush()
        menu = uicls.Container(parent=uicore.layer.menu, pos=(0, 0, 200, 200), align=uiconst.RELATIVE)
        menu.sr.scroll = uicls.Scroll(parent=menu)
        uicls.Fill(parent=menu, color=(0.0, 0.0, 0.0, 1.0))
        return (menu, menu.sr.scroll, listentry.Generic)



    def Startup(self, *args):
        pass




