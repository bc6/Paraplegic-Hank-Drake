#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/primitives/vectorarc.py
import uicls
import uiconst
import trinity
import math

class VectorArc(uicls.TexturedBase):
    __guid__ = 'uicls.VectorArc'
    __renderObject__ = trinity.Tr2Sprite2dArc
    default_name = 'vectorarc'
    default_align = uiconst.TOPLEFT
    default_lineWidth = 0
    default_lineColor = (1, 1, 1, 1)
    default_radius = 10
    default_fill = True
    default_startAngle = 0
    default_endAngle = math.pi * 2
    default_spriteEffect = trinity.TR2_SFX_FILL

    def ApplyAttributes(self, attributes):
        uicls.TexturedBase.ApplyAttributes(self, attributes)
        self.lineWidth = attributes.get('lineWidth', self.default_lineWidth)
        self.lineColor = attributes.get('lineColor', self.default_lineColor)
        self.radius = attributes.get('radius', self.default_radius)
        self.fill = attributes.get('fill', self.default_fill)
        self.startAngle = attributes.get('startAngle', self.default_startAngle)
        self.endAngle = attributes.get('endAngle', self.default_endAngle)

    @apply
    def lineWidth():
        doc = '\n        The width of a line following the arc. If 0, then no line is drawn.\n        '

        def fget(self):
            return self.renderObject.lineWidth

        def fset(self, value):
            self.renderObject.lineWidth = value

        return property(**locals())

    @apply
    def lineColor():
        doc = '\n        The color of a line following the arc.\n        '

        def fget(self):
            return self.renderObject.lineColor

        def fset(self, value):
            self.renderObject.lineColor = value

        return property(**locals())

    @apply
    def radius():
        doc = '\n        The radius of the arc.\n        '

        def fget(self):
            return self.renderObject.radius

        def fset(self, value):
            self.renderObject.radius = value

        return property(**locals())

    @apply
    def startAngle():
        doc = '\n        The starting angle of the arc.\n        '

        def fget(self):
            return self.renderObject.startAngle

        def fset(self, value):
            self.renderObject.startAngle = value

        return property(**locals())

    @apply
    def endAngle():
        doc = '\n        The ending angle of the arc.\n        '

        def fget(self):
            return self.renderObject.endAngle

        def fset(self, value):
            self.renderObject.endAngle = value

        return property(**locals())

    @apply
    def fill():
        doc = '\n        If set, the arc is filled.\n        '

        def fget(self):
            return self.renderObject.fill

        def fset(self, value):
            self.renderObject.fill = value

        return property(**locals())