#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/control/labelLink.py
import uicls
import uiconst
from util import Color

class LabelLink(uicls.EveLabelMedium):
    __guid__ = 'uicls.LabelLink'

    def ApplyAttributes(self, attributes):
        uicls.Label.ApplyAttributes(self, attributes)
        self.state = uiconst.UI_NORMAL
        self.func = attributes.func
        self.bold = True

    def OnClick(self, *args):
        apply(self.func[0], self.func[1:])

    def OnMouseEnter(self, *args):
        self.color = Color.YELLOW

    def OnMouseExit(self, *args):
        self.color = (1.0, 1.0, 1.0, 1.0)