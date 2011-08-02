import uicls
import uiutil
import uiconst

class IconCore(uicls.Sprite):
    __guid__ = 'uicls.IconCore'
    default_name = 'icon'
    default_icon = None
    default_ignoreSize = 0
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0

    def ApplyAttributes(self, attributes):
        uicls.Sprite.ApplyAttributes(self, attributes)
        icon = attributes.get('icon', self.default_icon)
        if icon:
            ignoreSize = attributes.get('ignoreSize', self.default_ignoreSize)
            self.LoadIcon(icon, ignoreSize=ignoreSize)
        onClick = attributes.get('OnClick', None)
        if onClick:
            self.OnClick = onClick




