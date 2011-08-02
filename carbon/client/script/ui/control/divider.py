import uicls
import uiconst
import uthread
import blue

class DividerCore(uicls.Container):
    __guid__ = 'uicls.DividerCore'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self._dragging = False
        self._initCursor = None



    def OnMouseDown(self, *args):
        self.OnChangeStart_(self)
        self._dragging = True
        self._initCursor = (uicore.uilib.x, uicore.uilib.y)
        uthread.new(self.BeginChange)



    def BeginChange(self, *args):
        while self._dragging:
            diffx = uicore.uilib.x - self._initCursor[0]
            diffy = uicore.uilib.y - self._initCursor[1]
            self.OnChange_(self, diffx, diffy)
            blue.pyos.synchro.Sleep(1)




    def OnMouseUp(self, *args):
        self._dragging = False
        self.OnChanged_(self)



    def OnChangeStart_(self, *args):
        pass



    def OnChange_(self, *args, **kw):
        pass



    def OnChanged_(self, *args):
        pass




