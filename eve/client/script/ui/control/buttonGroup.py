import fontConst
import uicls
import uiconst

class EveButtonGroup(uicls.ButtonGroupCore):
    __guid__ = 'uicls.ButtonGroup'
    default_fontsize = fontConst.EVE_SMALL_FONTSIZE

    def ApplyAttributes(self, attributes):
        uicls.ButtonGroupCore.ApplyAttributes(self, attributes)
        sm.GetService('window').CheckControlAppearance(self)




