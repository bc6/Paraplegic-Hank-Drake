import fontConst
import uicls
import uiconst
import uiutil
import uthread
import trinity
import blue

class ImageButtonCore(uicls.Sprite):
    __guid__ = 'uicls.ImageButtonCore'
    default_name = 'imageButton'
    default_align = uiconst.RELATIVE
    default_label = ''
    default_width = 32
    default_height = 32
    default_idleIcon = None
    default_mousedownIcon = None
    default_mouseoverIcon = None
    default_onclick = None
    default_onclickargs = None
    default_getmenu = None
    default_expandonleft = False
    default_whilemousedownFunc = None

    def Close(self, *args, **kw):
        if self.whileMouseDownFuncTasklet and self.whileMouseDownFuncTasklet.alive:
            self.whileMouseDownFuncTasklet.kill()
        self.whileMouseDownFuncTasklet = None
        uicls.Sprite.Close(self, *args, **kw)



    def ApplyAttributes(self, attributes):
        uicls.Sprite.ApplyAttributes(self, attributes)
        self.idleIcon = None
        self.mouseoverIcon = None
        self.mousedownIcon = None
        self.whileMouseDownFuncTasklet = None
        self.expandOnLeft = attributes.get('expandonleft', self.default_expandonleft)
        self.ClickFunc = attributes.get('onclick', self.default_onclick)
        self.ClickFuncArgs = attributes.get('onclickargs', self.default_onclickargs)
        self.GetMenu = attributes.get('getmenu', self.default_getmenu)
        self.WhileMouseDownFunc = attributes.get('whilemousedownFunc', self.default_whilemousedownFunc)
        self.SetMouseDownIcon(attributes.get('mousedownIcon', self.default_mousedownIcon), update=False)
        self.SetMouseOverIcon(attributes.get('mouseoverIcon', self.default_mouseoverIcon), update=False)
        self.SetMouseIdleIcon(attributes.get('idleIcon', self.default_idleIcon))



    def OnClick(self, *args):
        if self.ClickFunc:
            if self.ClickFuncArgs:
                self.ClickFunc(*self.ClickFuncArgs)
            else:
                self.ClickFunc()



    def OnMouseDown(self, *args):
        self.UpdateIcon()
        if self.WhileMouseDownFunc:
            self.whileMouseDownFuncTasklet = uthread.worker('imageButtonCore::', self._WhileHandleMouseDownFunc)



    def _WhileHandleMouseDownFunc(self):
        lastTime = blue.os.GetWallclockTime()
        while True:
            if self.destroyed:
                return 
            curTime = blue.os.GetWallclockTime()
            dt = float(curTime - lastTime) / const.SEC
            lastTime = curTime
            self.WhileMouseDownFunc(dt)
            blue.synchro.Yield()




    def OnMouseUp(self, *args):
        self.UpdateIcon()
        if self.whileMouseDownFuncTasklet and self.whileMouseDownFuncTasklet.alive:
            self.whileMouseDownFuncTasklet.kill()
            self.whileMouseDownFuncTasklet = None



    def OnMouseEnter(self, *args):
        self.UpdateIcon()



    def OnMouseExit(self, *args):
        self.UpdateIcon()



    def SetMouseIdleIcon(self, icon, update = True):
        self.idleIcon = icon
        if update:
            self.UpdateIcon()



    def SetMouseDownIcon(self, icon, update = True):
        self.mousedownIcon = icon
        if update:
            self.UpdateIcon()



    def SetMouseOverIcon(self, icon, update = True):
        self.mouseoverIcon = icon
        if update:
            self.UpdateIcon()



    def UpdateIcon(self):
        mo = uicore.uilib.mouseOver
        if mo == self:
            if uicore.uilib.leftbtn:
                if self.mousedownIcon:
                    uiutil.MapIcon(self, self.mousedownIcon, ignoreSize=True)
            elif self.mouseoverIcon:
                uiutil.MapIcon(self, self.mouseoverIcon, ignoreSize=True)
        elif self.idleIcon:
            uiutil.MapIcon(self, self.idleIcon, ignoreSize=True)




