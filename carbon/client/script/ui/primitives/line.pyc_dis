#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/primitives/line.py
import uicls
import uiutil
import uiconst
import blue
import trinity

class Line(uicls.Fill):
    __guid__ = 'uicls.Line'
    default_name = 'line'
    default_weight = 1
    default_align = uiconst.TOTOP
    default_color = (1.0, 1.0, 1.0, 0.25)
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        uicls.Fill.ApplyAttributes(self, attributes)
        if attributes.align in (uiconst.TOTOP,
         uiconst.TOBOTTOM,
         uiconst.TOLEFT,
         uiconst.TORIGHT,
         uiconst.TOTOP_NOPUSH,
         uiconst.TOBOTTOM_NOPUSH,
         uiconst.TOLEFT_NOPUSH,
         uiconst.TORIGHT_NOPUSH):
            weight = attributes.get('weight', self.default_weight)
            self.SetPosition(0, 0)
            self.SetSize(weight, weight)