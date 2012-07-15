#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/uitest/uitestContainerLayer.py
import uicls
import uiutil
import uthread
import blue
import base
import trinity

class ContainerLayer(uicls.Container):
    __guid__ = 'uicls.ContainerLayer'
    __renderObject__ = trinity.Tr2Sprite2dLayer
    default_name = 'ContainerLayer'
    default_opacity = 1.0

    def ApplyAttributes(self, attributes):
        uicls.PyContainer.ApplyAttributes(self, attributes)
        self.clearBackground = True
        self.backgroundColor = (0, 0, 0, 0)
        opacity = attributes.get('opacity', self.default_opacity)
        if opacity is not None:
            self.SetOpacity(opacity)

    def SetOpacity(self, opacity):
        r, g, b, a = self.color
        self.color = (r,
         g,
         b,
         opacity)

    def GetOpacity(self):
        return self.color[3]

    opacity = property(GetOpacity, SetOpacity)