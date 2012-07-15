#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/primitives/vectorline.py
import uicls
import uiconst
import trinity

class VectorLine(uicls.TexturedBase):
    __guid__ = 'uicls.VectorLine'
    __renderObject__ = trinity.Tr2Sprite2dLine
    default_name = 'vectorline'
    default_align = uiconst.TOPLEFT
    default_spriteEffect = trinity.TR2_SFX_FILL_AA

    def ApplyAttributes(self, attributes):
        uicls.TexturedBase.ApplyAttributes(self, attributes)
        self.translationFrom = attributes.get('translationFrom', (0.0, 0.0))
        self.widthFrom = attributes.get('widthFrom', 1.0)
        self.translationTo = attributes.get('translationTo', (0.0, 0.0))
        self.widthTo = attributes.get('widthTo', 1.0)

    @apply
    def translationFrom():
        doc = '\n        The translation of the starting point of the line.\n        '

        def fget(self):
            return self.renderObject.translationFrom

        def fset(self, value):
            self.renderObject.translationFrom = value

        return property(**locals())

    @apply
    def translationTo():
        doc = '\n        The translation of the ending point of the line.\n        '

        def fget(self):
            return self.renderObject.translationTo

        def fset(self, value):
            self.renderObject.translationTo = value

        return property(**locals())

    @apply
    def widthFrom():
        doc = '\n        The width of the line at the starting point.\n        '

        def fget(self):
            return self.renderObject.widthFrom

        def fset(self, value):
            self.renderObject.widthFrom = value

        return property(**locals())

    @apply
    def widthTo():
        doc = '\n        The width of the line at the ending point.\n        '

        def fget(self):
            return self.renderObject.widthTo

        def fset(self, value):
            self.renderObject.widthTo = value

        return property(**locals())