import uicls
import trinity

class Bracket(uicls.Container):
    __guid__ = 'uicls.Bracket'
    default_name = 'bracket'

    def ApplyAttributes(self, attributes):
        self.projectBracket = trinity.EveProjectBracket()
        self.projectBracket.bracket = self.GetRenderObject()
        uicore.uilib.bracketCurveSet.curves.append(self.projectBracket)
        uicls.Container.ApplyAttributes(self, attributes)



    def Close(self):
        uicls.Container.Close(self)
        uicore.uilib.bracketCurveSet.curves.fremove(self.projectBracket)
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
    def trackTransform():
        doc = 'The trinity.Tr2Transform that is supposed to dictate position of the bracket'

        def fget(self):
            if self.projectBracket:
                return self.projectBracket.trackTransform



        def fset(self, value):
            self.projectBracket.trackTransform = value


        return property(**locals())



    @apply
    def trackBall():
        doc = 'The destiny.Ball that is supposed to dictate position of the bracket'

        def fget(self):
            if self.projectBracket:
                return self.projectBracket.trackBall



        def fset(self, value):
            self.projectBracket.trackBall = value


        return property(**locals())



    @apply
    def ballTrackingScaling():
        doc = 'Scaling factor applied when using trackBall.'

        def fget(self):
            return self.projectBracket.ballTrackingScaling



        def fset(self, value):
            self.projectBracket.ballTrackingScaling = value


        return property(**locals())



    @apply
    def dock():
        doc = "If True, the bracket will dock to the side of it's parent container when the \n        projection is out of scope. If False, the bracket will disappear."

        def fget(self):
            return self.projectBracket.dock



        def fset(self, value):
            self.projectBracket.dock = value


        return property(**locals())



    @apply
    def left():
        doc = 'The x-coordinate of the bracket.'

        def fget(self):
            return self.renderObject.displayX


        fset = uicls.Base.left.fset
        return property(**locals())



    @apply
    def top():
        doc = 'The y-coordinate of the bracket.'

        def fget(self):
            return self.renderObject.displayY


        fset = uicls.Base.top.fset
        return property(**locals())



    @apply
    def minDispRange():
        doc = 'Bracket is hidden if the camera is closer to the object than this value'

        def fget(self):
            return self.projectBracket.minDispRange



        def fset(self, value):
            self.projectBracket.minDispRange = value


        return property(**locals())



    @apply
    def maxDispRange():
        doc = 'Bracket is hidden if the camera is farther from the object than this value'

        def fget(self):
            return self.projectBracket.maxDispRange



        def fset(self, value):
            self.projectBracket.maxDispRange = value


        return property(**locals())




