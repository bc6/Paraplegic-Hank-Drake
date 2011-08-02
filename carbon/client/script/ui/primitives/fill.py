import uicls
import uiutil
import uiconst
import trinity
import blue

class PyFill(uicls.Sprite):
    __guid__ = 'uicls.FillCore'
    default_name = 'fill'
    default_color = (1.0, 1.0, 1.0, 0.25)
    default_align = uiconst.TOALL
    default_state = uiconst.UI_DISABLED
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    default_filter = False
    default_spriteEffect = trinity.TR2_SFX_FILL

exports = {'uicls.Fill': PyFill}

