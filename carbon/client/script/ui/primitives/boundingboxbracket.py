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

    def ApplyAttributes(self, attributes):
        proj = trinity.Tr2ProjectBoundingBoxBracket()
        self.projectBracket = proj
        cs = uicore.uilib.bracketCurveSet
        cs.curves.append(self.projectBracket)
        self.leftBinding = trinity.CreatePythonBinding(cs, proj, 'projectedX', self, 'left')
        self.topBinding = trinity.CreatePythonBinding(cs, proj, 'projectedY', self, 'top')
        self.widthBinding = trinity.CreatePythonBinding(cs, proj, 'projectedWidth', self, 'width')
        self.heightBinding = trinity.CreatePythonBinding(cs, proj, 'projectedHeight', self, 'height')
        uicls.Container.ApplyAttributes(self, attributes)
        self.trackObject = attributes.get('trackObject', None)
        self.projectBracket.minProjectedWidth = attributes.get('minWidth', self.default_minWidth)
        self.projectBracket.minProjectedHeight = attributes.get('minHeight', self.default_minHeight)
        self.projectBracket.maxProjectedWidth = attributes.get('maxWidth', self.default_maxWidth)
        self.projectBracket.maxProjectedHeight = attributes.get('maxHeight', self.default_maxHeight)



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




