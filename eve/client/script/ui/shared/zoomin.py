import menu
import base
import uthread
import xtriui
import uix
import uiutil
import blue
import trinity
import uicls
import uiconst

class ViewPort(uicls.Container):
    __guid__ = 'xtriui.ViewPort'

    def init(self):
        self.dragging = 0
        self.state = uiconst.UI_NORMAL



    def Startup(self, w, h, level, callback):
        self.SetSize(int(w / level), int(h / level), level)
        uicore.layer.main.children.insert(0, self)
        self.left = (uicore.desktop.width - self.width) / 2
        self.top = (uicore.desktop.height - self.height) / 2
        self.callback = callback



    def SetSize(self, x, y, level):
        self.width = x
        self.height = y
        self.zoomlevel = level



    def GetRect(self):
        x1 = self.left
        x2 = self.left + self.width
        y1 = self.top
        y2 = self.top + self.height
        return (x1,
         x2,
         y1,
         y2)



    def _OnStartDrag(self, *args):
        if abs(uicore.uilib.x - self.width / 2 - self.left) > 8:
            self.left = uicore.uilib.x - self.width / 2
        if abs(uicore.uilib.y - self.height / 2 - self.top) > 8:
            self.top = uicore.uilib.y - self.height / 2



    def OnMouseMove(self, *args):
        if self.dragging:
            uthread.new(apply, self.callback, self.GetRect())



    def OnMouseUp(self, *args):
        self.dragging = 0



    def OnMouseDown(self, *args):
        self.dragging = 1




