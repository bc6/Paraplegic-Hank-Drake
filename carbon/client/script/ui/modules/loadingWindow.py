import blue
import uthread
import types
import base
import uicls
import uiutil
import uiconst

class LoadingWndCore(uicls.Window):
    __guid__ = 'uicls.LoadingWndCore'
    default_windowID = 'loadingWindow'
    MINHEIGHT = 80

    def _Initialize(self, *args, **kw):
        self.abortbtn = None
        self.abortbtnpar = None
        self.sr.loading_caption = None
        self.sr.progressParent = None
        self.sr.progressBarParent = None
        self.sr.progressBar = None
        self.sr.progressText = None
        uicls.Window._Initialize(self, *args, **kw)



    def Setup(self, *args):
        self.SetPosition(0, 0)
        self.SetSize(300, self.MINHEIGHT)
        self.SetAlign(uiconst.CENTER)
        self.Lock()



    def Prepare_Header_(self):
        pass



    def Prepare_ProgressBar_(self):
        if self.sr.progressText is None:
            par = uicls.Container(name='progressParent', parent=self.sr.content, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 20))
            self.sr.content.SetPadding(6, 6, 6, 6)
            fr = uicls.Frame(parent=par, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 10), frameConst=uiconst.FRAME_BORDER1_SHADOW_CORNER0, color=(1.0, 1.0, 1.0, 0.5))
            progressbar = uicls.Fill(parent=fr.sr.content, align=uiconst.RELATIVE, pos=(1, 1, 0, 8))
            self.sr.progressBar = progressbar
            self.sr.progressBarParent = fr
            self.sr.progressText = uicls.Label(parent=par, pos=(0, 12, 300, 0), fontsize=9, uppercase=1, letterspace=2, align=uiconst.BOTTOMLEFT)
            self.sr.progressParent = par



    def Prepare_Caption_(self):
        if self.sr.loading_caption is None:
            self.sr.loading_caption = uicls.Label(align=uiconst.CENTERTOP, fontsize=22, parent=self.sr.content, letterspace=0, pos=(0, 12, 280, 0))



    def _OnClose(self, *args):
        if self.abortbtn:
            self.abortbtn.Close()
        self.abortbtn = None



    def SetAbortFunc(self, func):
        args = None
        if type(func) == types.TupleType:
            (func, args,) = func
        if self.abortbtnpar is None:
            if func is None:
                return 
            self.abortbtnpar = uicls.Container(parent=self.sr.main, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 30), state=uiconst.UI_PICKCHILDREN)
            self.abortbtn = uicls.Button(func=func, args=args, align=uiconst.CENTER)
        if func is None:
            self.abortbtnpar.state = uiconst.UI_HIDDEN
        else:
            self.abortbtnpar.state = uiconst.UI_NORMAL
            self.abortbtn.OnClick = (func, args)



    def Update_ProgressText_(self, text):
        if self.sr.progressText and self.sr.progressText.text != text:
            self.sr.progressText.text = text



    def Update_ProgressBar_(self, portion, total, useMorph):
        if not self.sr.progressBar:
            return 
        maxWidth = getattr(self, 'maxWidth', None)
        if maxWidth is None:
            (l, t, w, h,) = self.sr.progressBarParent.GetAbsolute()
            maxWidth = w - 2
        if portion is not None and total is not None:
            if portion > total:
                portion = total
            if portion / float(total) == 1.0:
                new = maxWidth
            else:
                new = int(maxWidth * portion / float(total))
        elif total == 0:
            new = maxWidth
        else:
            new = 0
        minWidth = getattr(self, 'minWidth', None)
        if minWidth is not None:
            new = max(minWidth, new)
        if new < self.sr.progressBar.width:
            self.sr.progressBar.width = new
        elif useMorph and minWidth != new:
            diff = new - self.sr.progressBar.width
            if diff > 0:
                uicore.effect.MorphUI(self.sr.progressBar, 'width', new, float(1.5 * diff), ifWidthConstrain=0)
        else:
            self.sr.progressBar.width = new
            blue.pyos.synchro.Yield()



    def Update_Height_(self):
        newheight = 12
        if self.sr.loading_caption:
            newheight += self.sr.loading_caption.textheight
        if self.sr.progressText and self.sr.progressText.text:
            newheight += self.sr.progressText.textheight
        if self.sr.progressParent:
            newheight += self.sr.progressParent.height
        newheight = max(self.MINHEIGHT, newheight)
        if self.abortbtnpar and self.abortbtnpar.state != uiconst.UI_HIDDEN:
            newheight += self.abortbtnpar.height
        if self.height != newheight:
            uicore.effect.MorphUI(self, 'height', newheight, 125.0)
            blue.pyos.synchro.SleepWallclock(250)
            self.height = newheight



    def SetStatus(self, title, strng, portion = None, total = None, abortFunc = None, useMorph = 1, autoTick = 1):
        if self is None or self.destroyed:
            return 1
        self.Prepare_ProgressBar_()
        self._SetCaption(title)
        self.SetAbortFunc(abortFunc)
        if len(strng) > 128:
            strng = strng[:128] + '...'
        self.Update_ProgressText_(strng)
        self.Update_ProgressBar_(portion, total, useMorph)
        self.Update_Height_()
        if portion is not None and total is not None:
            if portion >= total:
                self.sr.tickTimer = None
                self.stophide = 0
                self.AutoDelayHideOnProgressComplete()
            else:
                if autoTick:
                    self.sr.tickTimer = base.AutoTimer(75, self.Tick)
                else:
                    self.sr.tickTimer = None
                self.stophide = 1
                if self.parent and not self.parent.destroyed:
                    self.parent.state = uiconst.UI_NORMAL
        return 0



    def AutoDelayHideOnProgressComplete(self):
        uthread.new(self.DelayHide)
        uthread.new(self.SanityDelayHide)



    def Tick(self):
        if self.sr.progressBar:
            maxWidth = getattr(self, 'maxWidth', None)
            if maxWidth is None:
                (l, t, w, h,) = self.sr.progressBarParent.GetAbsolute()
                maxWidth = w - 2
            new = self.sr.progressBar.width + 1
            if new >= maxWidth:
                new = maxWidth
                self.sr.tickTimer = None
            self.sr.progressBar.width = new



    def _SetCaption(self, title):
        self.Prepare_Caption_()
        if self.sr.loading_caption and self.sr.get('loading_title', None) != title:
            self.sr.loading_caption.text = ['<center>', title]
            self.sr.loading_title = title



    def HideWnd(self):
        sm.GetService('loading').StopCycle()
        uthread.new(self.DelayHide)



    def DelayHide(self):
        blue.pyos.synchro.SleepWallclock(750)
        if not getattr(self, 'stophide', 0):
            uicore.layer.loading.state = uiconst.UI_HIDDEN
            if self and not self.destroyed and self.sr.progressBar:
                self.sr.progressBar.width = 0



    def SanityDelayHide(self):
        blue.pyos.synchro.SleepWallclock(5000)
        if not getattr(self, 'stophide', 0):
            uicore.layer.loading.state = uiconst.UI_HIDDEN
            if self and not self.destroyed and self.sr.progressBar:
                self.sr.progressBar.width = 0




