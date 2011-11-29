import uicls
import trinity
import uiconst

class BoundingBoxBracket(uicls.Container):
    __guid__ = 'uicls.BoundingBoxBracket'
    default_name = 'boundingboxBracket'
    default_align = uiconst.TOPLEFT
    default_minWidth = 0.0
    default_minHeight = 0.0
    default_maxWidth = 0.0
    default_maxHeight = 0.0
    default_screenMargin = 32.0

    def ApplyAttributes(self, attributes):
        proj = trinity.Tr2ProjectBoundingBoxBracket()
        self.projectBracket = proj
        cs = uicore.uilib.bracketCurveSet
        cs.curves.append(self.projectBracket)
        self.leftBinding = trinity.CreatePythonBinding(cs, proj, 'projectedX', self, 'scaledLeft')
        self.topBinding = trinity.CreatePythonBinding(cs, proj, 'projectedY', self, 'scaledTop')
        self.widthBinding = trinity.CreatePythonBinding(cs, proj, 'projectedWidth', self, 'scaledWidth')
        self.heightBinding = trinity.CreatePythonBinding(cs, proj, 'projectedHeight', self, 'scaledHeight')
        uicls.Container.ApplyAttributes(self, attributes)
        self.trackObject = attributes.get('trackObject', None)
        self.screenMargin = attributes.get('screenMargin', self.default_screenMargin)
        pb = self.projectBracket
        if self.width:
            pb.minProjectedWidth = pb.maxProjectedWidth = self.width
        else:
            pb.minProjectedWidth = attributes.get('minWidth', self.default_minWidth)
            pb.maxProjectedWidth = attributes.get('maxWidth', self.default_maxWidth)
        if self.height:
            pb.minProjectedHeight = pb.maxProjectedHeight = self.height
        else:
            pb.minProjectedHeight = attributes.get('minHeight', self.default_minHeight)
            pb.maxProjectedHeight = attributes.get('maxHeight', self.default_maxHeight)



    def Close(self):
        uicls.Container.Close(self)
        cs = uicore.uilib.bracketCurveSet
        cs.curves.fremove(self.projectBracket)
        cs.bindings.fremove(self.leftBinding)
        cs.bindings.fremove(self.topBinding)
        cs.bindings.fremove(self.widthBinding)
        cs.bindings.fremove(self.heightBinding)
        self.leftBinding = None
        self.topBinding = None
        self.widthBinding = None
        self.heightBinding = None
        self.projectBracket = None



    @apply
    def name():
        doc = 'Name of the bracket'
        fget = uicls.Container.name.fget

        def fset(self, name):
            uicls.Container.name.fset(self, name)
            self.projectBracket.name = unicode(name)


        return property(**locals())



    @apply
    def trackObject():
        doc = '\n        The object that is supposed to dictate position of the bracket. This can be\n        any object with the ITr2BoundingBox interface, such as Tr2InteriorPlaceable.\n        '

        def fget(self):
            return self.projectBracket.object



        def fset(self, value):
            self.projectBracket.object = value


        return property(**locals())



    @apply
    def screenMargin():
        doc = '\n        The width of the margin around the screen that the object will not surpass\n        '

        def fget(self):
            return self.projectBracket.screenMargin



        def fset(self, value):
            self.projectBracket.screenMargin = value


        return property(**locals())



    @apply
    def scaledLeft():
        doc = '\n        Sets the left attribute to the given value with reverse dpi scaling applied.\n        '

        def fset(self, value):
            self.left = uicore.ReverseScaleDpi(value)


        return property(**locals())



    @apply
    def scaledTop():
        doc = '\n        Sets the top attribute to the given value with reverse dpi scaling applied.\n        '

        def fset(self, value):
            self.top = uicore.ReverseScaleDpi(value)


        return property(**locals())



    @apply
    def scaledWidth():
        doc = '\n        Sets the width attribute to the given value with reverse dpi scaling applied.\n        '

        def fset(self, value):
            self.width = uicore.ReverseScaleDpi(value)


        return property(**locals())



    @apply
    def scaledHeight():
        doc = '\n        Sets the height attribute to the given value with reverse dpi scaling applied.\n        '

        def fset(self, value):
            self.height = uicore.ReverseScaleDpi(value)


        return property(**locals())




