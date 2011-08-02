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

class CursorZoom(uicls.Container):
    __guid__ = 'xtriui.CursorZoom'

    def init(self):
        self.rendering = 0
        self.state = uiconst.UI_HIDDEN
        self.name = 'zoomcursor'
        self.positiontimer = None
        self.rendertimer = None
        self.lastrenderpos = (0, 0)
        self.renderres = 16
        self.cursor = 10
        self.ignorebuffer = 0
        self.align = uiconst.RELATIVE



    def _OnClose(self):
        self.positiontimer = None
        self.rendertimer = None
        self.frombuffertimer = None
        self.sr.zoomtxt.Close()
        self.sr.pic.Close()



    def Startup(self):
        pic = uicls.Sprite(align=uiconst.TOALL, parent=self, state=uiconst.UI_HIDDEN)
        uicore.desktop.children.insert(1, self)
        self.sr.pic = pic
        self.width = self.height = 128
        self.positiontimer = base.AutoTimer(25, self.Position)
        self.frombuffertimer = base.AutoTimer(1, self.ReadFromBuffer)
        uicls.Line(parent=self, align=uiconst.RELATIVE, width=uicore.desktop.width, height=1, left=-uicore.desktop.width - 6, top=self.height / 2)
        uicls.Line(parent=self, align=uiconst.RELATIVE, width=uicore.desktop.width, height=1, left=self.width + 6, top=self.height / 2)
        uicls.Line(parent=self, align=uiconst.RELATIVE, width=1, height=uicore.desktop.height, left=self.width / 2, top=-uicore.desktop.height - 6)
        uicls.Line(parent=self, align=uiconst.RELATIVE, width=1, height=uicore.desktop.height, left=self.width / 2, top=self.height + 6)
        uicls.Frame(parent=self, padding=(-1, -1, -1, -1))
        uicls.Frame(parent=self, padding=(-5, -5, -5, -5), weight=2)
        self.sr.zoomtxt = uicls.Label(text='', parent=self, left=self.width + 12, top=self.height / 2 + 8, fontsize=9, letterspace=2, linespace=11, color=(1.0, 1.0, 1.0, 0.5))
        uiutil.SetOrder(self.sr.zoomtxt, 0)
        self.align = uiconst.ABSOLUTE
        self.Position()
        self.state = uiconst.UI_NORMAL



    def Position(self):
        if self:
            self.left = max(0, min(uicore.uilib.x - self.width / 2, uicore.desktop.width - self.width))
            self.top = max(0, min(uicore.uilib.y - self.height / 2, uicore.desktop.height - self.height))



    def SetZoomLevel(self, level):
        settings.user.ui.Set('cursorzoomlevel', level)
        if not self.destroyed:
            self.state = uiconst.UI_NORMAL
            self.positiontimer = base.AutoTimer(25, self.Position)
            self.frombuffertimer = base.AutoTimer(1, self.ReadFromBuffer)



    def RenderDetail(self):
        if self and self.rendering:
            return 
        self.rendering = 1
        buff = uiutil.GetBuffersize(self.width)
        renderres = buff / settings.user.ui.Get('cursorzoomlevel', 2)
        while renderres <= buff:
            if not self or not self.sr or not self.sr.pic:
                break
            x = self.absoluteLeft + self.width / 2
            y = self.absoluteTop + self.height / 2
            xZ = self.width / (2 * settings.user.ui.Get('cursorzoomlevel', 2))
            yZ = self.height / (2 * settings.user.ui.Get('cursorzoomlevel', 2))
            self.sr.zoomtxt.text = '%s %sx' % (mls.UI_SHARED_ZOOMLEVEL, settings.user.ui.Get('cursorzoomlevel', 2))
            self.sr.zoomtxt.text += '<br>%s 1:%s' % (mls.UI_SHARED_DETAIL, buff / renderres)
            sur = sm.GetService('photo').RenderFromScene(x - xZ, x + xZ, y - yZ, y + yZ, renderres)
            self.sr.pic.texture.AttachSurface(sur)
            self.sr.pic.state = uiconst.UI_DISABLED
            renderres = renderres * 2
            uicore.uilib.SetCursor(uiconst.UICURSOR_NONE)
            blue.pyos.synchro.Yield()

        self.state = uiconst.UI_NORMAL
        self.rendering = 0
        blue.pyos.synchro.Sleep(1000)



    def OnMouseUp(self, btn, *args):
        if btn == 1:
            current = settings.user.ui.Get('cursorzoomlevel', 2)
            m = []
            for lvl in (2, 4, 8, 16):
                m.append(('%s%s %sx' % (['  ', '\x95 '][(current == lvl)], mls.UI_SHARED_ZOOMLEVEL, lvl), self.SetZoomLevel, (lvl,)))

            mv = menu.CreateMenuView(menu.CreateMenuFromList(m), None, None)
            (x, y,) = (min(uicore.desktop.width - mv.width, uicore.uilib.x + 10), min(uicore.desktop.height - mv.height, uicore.uilib.y))
            (mv.left, mv.top,) = (x, y)
            uicore.layer.menu.children.insert(0, mv)
            self.state = uiconst.UI_HIDDEN



    def OnClick(self, *args):
        self.ignorebuffer = 1
        self.RenderDetail()
        if not self.destroyed:
            self.ignorebuffer = 0



    def ReadFromBuffer(self):
        if self.ignorebuffer:
            return 
        self.sr.pic.state = uiconst.UI_HIDDEN
        self.sr.zoomtxt.text = '%s %sx' % (mls.UI_SHARED_ZOOMLEVEL, settings.user.ui.Get('cursorzoomlevel', 2))
        (l, t, w, h,) = self.GetAbsolute()
        x = max(w / 2, min(l + w / 2, uicore.desktop.width - w / 2))
        y = max(h / 2, min(t + h / 2, uicore.desktop.height - h / 2))
        res = uiutil.GetBuffersize(w)
        s = res / settings.user.ui.Get('cursorzoomlevel', 2) / 2
        self.sr.zoomtxt.text += '<br>%s 1:%s<br>%s' % (mls.UI_SHARED_DETAIL, res / s, mls.UI_SHARED_CLICKFORMOREDETAIL)
        dev = trinity.device
        fromrect = trinity.TriRect(x - s, y - s, x + s, y + s)
        droprect = trinity.TriRect(l, t, l + w, t + h)
        sur = dev.CreateRenderTarget(s * 2, s * 2, dev.deviceFormat, 0, 0, 1)
        surrect = trinity.TriRect(0, 0, s * 2, s * 2)
        fb = dev.GetRenderTarget()
        dev.StretchRect(fb, fromrect, sur, surrect)
        dev.StretchRect(sur, surrect, fb, droprect)




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




