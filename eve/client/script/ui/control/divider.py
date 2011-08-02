import uicls
import uiconst

class Divider(uicls.Container):
    __guid__ = 'xtriui.Divider'
    __nonpersistvars__ = []

    def init(self):
        self.dragging = 0
        self.startvalue = None
        self.initx = None
        self.inity = None
        self.cursor = 18



    def _OnClose(self):
        uicls.Container._OnClose(self)
        self.OnSizeChanged = None
        self.OnSizeChanging = None
        self.OnSizeChangeStarting = None



    def Startup(self, victim, attribute, xory, minValue = 1, maxValue = 1600):
        self.sr.victim = victim
        self.attribute = attribute
        self.xory = xory
        self.SetMinMax(minValue, maxValue)
        self.cursor = [11, 18][(xory == 'x')]



    def OnMouseDown(self, *args):
        self.dragging = 1
        self.OnSizeChangeStarting(self)
        self.initx = uicore.uilib.x
        self.inity = uicore.uilib.y
        self.initvalue = getattr(self.sr.victim, self.attribute, 0)



    def OnMouseUp(self, *args):
        self.dragging = 0
        self.OnSizeChanged()



    def SetMinMax(self, minValue = None, maxValue = None):
        if minValue is not None:
            self.min = minValue
        if maxValue is not None:
            self.max = maxValue



    def OnMouseMove(self, *args):
        if self.dragging:
            self.diffx = uicore.uilib.x - self.initx
            self.diffy = uicore.uilib.y - self.inity
            diff = getattr(self, 'diff%s' % self.xory, 0)
            if self.sr.victim.align in (uiconst.TOBOTTOM, uiconst.TORIGHT):
                diff = -diff
            newvalue = min(self.max, max(self.min, diff + self.initvalue))
            setattr(self.sr.victim, self.attribute, newvalue)
            self.OnSizeChanging()



    def OnSizeChangeStarting(self, *args):
        pass



    def OnSizeChanged(self, *args):
        pass



    def OnSizeChanging(self, *args):
        pass




