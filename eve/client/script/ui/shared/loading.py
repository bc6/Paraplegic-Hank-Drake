import service
import blue
import uthread
import uix
import uiutil
import mathUtil
import xtriui
import form
import util
import types
import base
import uiconst
import uicls
import localization

class Loading(service.Service):
    __exportedcalls__ = {'CleanUp': [],
     'ProgressWnd': [],
     'Cycle': [],
     'StopCycle': [],
     'HideAllLoad': [],
     'FadeToBlack': [],
     'FadeFromBlack': [],
     'GoBlack': [],
     'IsLoading': []}
    __notifyevents__ = ['OnNetClientReadProgress']
    __dependencies__ = []
    __guid__ = 'svc.loading'
    __servicename__ = 'loading'
    __displayname__ = 'Loading Service'

    def Run(self, memStream = None):
        self.LogInfo('Starting LoadingSvc')
        self.soundStarted = self.explicitSound = 0
        self.loadingwnd = None
        self.disabled = 0
        self.isFadingOut = 0
        self.isFadingIn = 0
        self.fadedIn = 0
        self.loading = 0
        self.que = []
        self.done = []
        self.premature = []
        self.currentid = None
        self.cycletext = None
        self.cycling = 0
        self.fadingToBlack = 0
        self.fadingFromBlack = 0



    def Stop(self, memStream = None):
        self.CleanUp()



    def CleanUp(self):
        self.que = []
        self.StopSound()
        self.StopCycle()
        if self.loadingwnd is not None and not self.loadingwnd.destroyed:
            self.loadingwnd.Close()
            self.loadingwnd = None
        self.ClearBlackout()
        l_loading = uicore.layer.loading
        if l_loading:
            l_loading.Flush()



    def CountDownWindow(self, question, duration, confirmFunc, abortFunc, inModalLayer = False):
        startTime = blue.os.GetWallclockTime()
        if inModalLayer:
            par = uicore.layer.mloading
        else:
            par = uicore.layer.loading
        wnd = form.ProgressWnd(parent=par, idx=0)
        wnd.Startup()
        wnd._SetCaption(question)
        if confirmFunc and abortFunc:
            wnd.SetAbortConfirmFunc(abortFunc, confirmFunc)
        elif abortFunc:
            wnd.SetAbortFunc(abortFunc)
        wnd.sr.abortFunc = abortFunc
        wnd.sr.confirmFunc = confirmFunc
        wnd.CheckHeight(0)
        uthread.new(wnd.CountDown, startTime, duration)
        return wnd



    def ProgressWnd(self, title = None, strng = '', portion = 1, total = 1, explicitSound = 0, abortFunc = None, useMorph = 1, autoTick = 1):
        if self.disabled:
            return 
        if title is None:
            title = localization.GetByLabel('UI/Common/Loading')
        wnd = getattr(self, 'loadingwnd', None)
        par = uicore.layer.loading
        if not wnd or wnd.destroyed:
            wnd = form.ProgressWnd(parent=par, idx=0)
            wnd.Startup()
            self.loadingwnd = wnd
        left = sm.GetService('window').GetCameraLeftOffset(wnd.width, align=uiconst.CENTER, left=0)
        wnd.left = left
        wnd.top = 0
        if portion >= total:
            if self.soundStarted:
                self.StopSound()
        elif not self.soundStarted:
            self.soundStarted = 1
            self.explicitSound = explicitSound
        failed = wnd.SetStatus(title, strng, max(0, portion), max(0, total), abortFunc, useMorph=useMorph, autoTick=autoTick)
        if failed:
            self.loadingwnd = None
            uicore.layer.loading.state = uiconst.UI_HIDDEN



    def OnNetClientReadProgress(self, have, need):
        if self.disabled:
            return 
        if sm.StartService('connection').processingBulkData == 0:
            return 
        wnd = getattr(self, 'loadingwnd', None)
        if not wnd or wnd.destroyed:
            return 
        wnd.SetReadProgress(int(have / 1024), int(need / 1024))



    def StopSound(self):
        if self.soundStarted:
            self.soundStarted = self.explicitSound = 0



    def Cycle(self, title = None, strng = ''):
        if self.disabled:
            return 
        if title is None:
            title = localization.GetByLabel('UI/Common/Loading')
        self.cycletext = (title, strng)
        uthread.new(self._Cycle)



    def _Cycle(self):
        if self.cycling or self.disabled:
            return 
        blue.pyos.synchro.Yield()
        while self.cycletext:
            self.cycling = 1
            for i in xrange(100):
                if self.cycletext:
                    self.ProgressWnd(self.cycletext[0], self.cycletext[1], portion=i, total=100, useMorph=0)
                else:
                    uicore.layer.loading.state = uiconst.UI_HIDDEN
                    break
                blue.pyos.BeNice()


        self.cycling = 0



    def StopCycle(self):
        self.cycletext = None
        l_loading = uicore.layer.loading
        if l_loading:
            uicore.layer.loading.state = uiconst.UI_HIDDEN



    def HideAllLoad(self):
        self.StopCycle()



    def GoBlack(self):
        if self.disabled:
            return 
        self.FadeToBlack(1)



    def GetFill(self):
        if self.disabled:
            return 
        fill = None
        for each in uicore.desktop.children:
            if each.name == 'loadingblackout' and each is not None and not each.destroyed:
                fill = each
                current = fill.color.a
                break

        if fill is None or fill.destroyed:
            fill = uicls.Fill(parent=uicore.desktop, color=(0.0, 0.0, 0.0, 0.0), state=uiconst.UI_NORMAL, padding=(-2, -2, -2, -2), idx=uicore.desktop.children.index(uicore.layer.loading) + 1)
            fill.name = 'loadingblackout'
            current = 0.0
        return (fill, current)



    def IsLoading(self):
        return uicore.layer.loading.state == uiconst.UI_NORMAL or self.fadingToBlack or self.fadingFromBlack or self.cycling



    def FadeToBlack(self, time = 1000):
        if self.disabled:
            return 
        if self.fadingToBlack or not uicore.layer.loading:
            return 
        self.fadingToBlack = 1
        self.fadingFromBlack = 0
        (fill, current,) = self.GetFill()
        fill.state = uiconst.UI_NORMAL
        time = float(time)
        (start, ndt,) = (blue.os.GetWallclockTime(), 0.0)
        while ndt != 1.0 and not fill.destroyed and self.fadingToBlack:
            ndt = min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / time, 1.0)
            fill.color.a = mathUtil.Lerp(current, 1.0, ndt)
            blue.pyos.synchro.Yield()

        self.fadingToBlack = 0



    def FadeFromBlack(self, time = 1000):
        if self.disabled:
            return 
        if self.fadingFromBlack or not uicore.layer.loading:
            return 
        self.fadingFromBlack = 1
        self.fadingToBlack = 0
        (fill, current,) = self.GetFill()
        fill.state = uiconst.UI_NORMAL
        time = float(time)
        (start, ndt,) = (blue.os.GetWallclockTime(), 0.0)
        while ndt != 1.0 and not fill.destroyed and self.fadingFromBlack:
            ndt = min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / time, 1.0)
            fill.color.a = mathUtil.Lerp(current, 0.0, ndt)
            blue.pyos.synchro.Yield()

        fill.state = uiconst.UI_HIDDEN
        self.fadingFromBlack = 0



    def ClearBlackout(self):
        for each in uicore.desktop.children:
            if each.name == 'loadingblackout' and each is not None and not each.destroyed:
                each.Close()





class ProgressWnd(uicls.Container):
    __guid__ = 'form.ProgressWnd'
    __nonpersistvars__ = []
    default_left = 0
    default_top = 0
    default_width = 320
    default_height = 87
    default_windowID = 'progresswindow'
    default_state = uiconst.UI_HIDDEN
    default_align = uiconst.CENTER

    def Startup(self):
        self.abortbtn = None
        self.abortbtnpar = None
        self.confirmbtn = None
        self.abortconfirmbtnpar = None
        self.sr.progresstext = None
        self.sr.readprogress = util.KeyVal(text='', prev=0)
        self.scope = 'all'
        self.sr.main = uicls.Container(parent=self, pos=(0, 0, 0, 0), name='maincontainer', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOALL)
        self.sr.wndUnderlay = uicls.WindowUnderlay(parent=self, transparent=False)
        par = uicls.Container(name='progressParent', parent=self.sr.main, align=uiconst.TOBOTTOM, height=32)
        progress = uicls.Container(parent=par, pos=(25,
         10,
         self.width - 50,
         10), name='progressbar', state=uiconst.UI_DISABLED, align=uiconst.RELATIVE)
        self.sr.glowClipper = uicls.Container(parent=progress, pos=(0, 0, 0, 10), name='glowclipper', state=uiconst.UI_DISABLED, clipChildren=True, align=uiconst.RELATIVE)
        self.sr.glow = uicls.Container(parent=self.sr.glowClipper, pos=(0,
         0,
         progress.width,
         10), name='glow', state=uiconst.UI_DISABLED, align=uiconst.RELATIVE)
        glowFill = uicls.Fill(parent=self.sr.glow, name='glowFill', state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.5), align=uiconst.TOALL)
        shade = uicls.Container(parent=progress, pos=(0, 0, 0, 0), name='shade', state=uiconst.UI_DISABLED, align=uiconst.TOALL)
        shadeFill = uicls.Fill(parent=shade, name='shadeFill', state=uiconst.UI_DISABLED, color=(0.0, 0.0, 0.0, 0.18), align=uiconst.TOALL)
        uicls.Frame(parent=progress)
        self.sr.loading_progress = progress
        self.sr.progresstext = uicls.EveLabelMedium(text='', parent=progress, width=270, left=2, top=4, state=uiconst.UI_NORMAL)
        self.state = uiconst.UI_PICKCHILDREN



    def SetAbortFunc(self, func):
        args = None
        if type(func) == types.TupleType:
            (func, args,) = func
        if self.abortbtnpar is None:
            if func is None:
                return 
            self.abortbtnpar = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Commands/Abort'),
              func,
              args,
              66]])
            self.abortbtn = self.abortbtnpar.children[0].children[0]
            self.sr.main.children.insert(0, self.abortbtnpar)
        if func is None:
            self.abortbtnpar.state = uiconst.UI_HIDDEN
        else:
            self.abortbtnpar.state = uiconst.UI_NORMAL
            self.abortbtn.OnClick = (func, args)



    def SetAbortConfirmFunc(self, abortFunc, confirmFunc):
        abortArgs = None
        confirmArgs = None
        if type(abortFunc) == types.TupleType:
            (abortFunc, abortArgs,) = abortFunc
        if type(confirmFunc) == types.TupleType:
            (confirmFunc, confirmArgs,) = confirmFunc
        if self.abortconfirmbtnpar is None:
            self.abortconfirmbtnpar = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Common/Yes'),
              self.Confirm,
              (),
              None,
              0,
              1,
              0], [localization.GetByLabel('UI/Common/No'),
              self.Abort,
              (),
              None,
              0,
              0,
              1]])
            self.abortconfirmbtnpar.align = uiconst.TOBOTTOM
            self.confirmbtn = self.abortconfirmbtnpar.children[0].children[0]
            self.abortbtn = self.abortconfirmbtnpar.children[0].children[1]
            self.sr.main.children.insert(0, self.abortconfirmbtnpar)
        uicore.registry.AddModalWindow(self)



    def Abort(self, *args):
        if self.sr.Get('abortFunc', None) is not None:
            abortFunc = self.sr.Get('abortFunc', None)
            if type(abortFunc) == types.TupleType:
                (abortFunc, abortArgs,) = abortFunc
                abortFunc(*abortArgs)
            else:
                abortFunc()
        self.Close()



    def Confirm(self, *args):
        if self.sr.Get('confirmFunc', None) is not None:
            confirmFunc = self.sr.Get('confirmFunc', None)
            if type(confirmFunc) == types.TupleType:
                (confirmFunc, confirmArgs,) = confirmFunc
                confirmFunc(*confirmArgs)
            else:
                confirmFunc()
        self.Close()



    def SetModalResult(self, modalResult, *args):
        if modalResult in (uiconst.ID_CANCEL, uiconst.ID_NONE):
            self.Abort()



    def CountDown(self, startTime, duration):
        while True and not self.destroyed:
            dt = blue.os.TimeDiffInMs(startTime, blue.os.GetWallclockTimeNow())
            if dt > duration:
                break
            self.sr.progresstext.text = util.FmtDate(long((duration - dt) * 10000) + SEC)
            self.sr.progresstext.top = -self.sr.progresstext.height - 2
            portion = dt / float(duration)
            self.SetProgressPortion(portion)
            blue.pyos.synchro.SleepWallclock(10)

        if not self.destroyed:
            self.sr.progresstext.text = util.FmtDate(0L)
            self.Abort()



    def SetProgressPortion(self, portion, useMorph = 0):
        maxW = self.sr.loading_progress.width
        if useMorph:
            new = int(maxW * portion)
            diff = new - self.sr.glowClipper.width
            if diff > 0:
                uicore.effect.MorphUI(self.sr.glowClipper, 'width', new, float(1.5 * diff), ifWidthConstrain=0)
            else:
                self.sr.glowClipper.width = new
        else:
            self.sr.glowClipper.width = int(maxW * portion)



    def CheckHeight(self, morph = 1):
        newheight = max(86, self.sr.loading_caption.textheight + self.sr.progresstext.textheight + 40)
        if self.abortbtnpar:
            newheight += [0, self.abortbtnpar.height][(self.abortbtnpar.state != uiconst.UI_HIDDEN)]
        elif self.abortconfirmbtnpar:
            newheight += [0, self.abortconfirmbtnpar.height][(self.abortconfirmbtnpar.state != uiconst.UI_HIDDEN)]
        if self.height != newheight:
            if morph:
                uicore.effect.MorphUI(self, 'height', newheight, 125.0)
                blue.pyos.synchro.SleepWallclock(250)
            self.height = newheight



    def SetReadProgress(self, have, need):
        if self is None or self.destroyed:
            return 
        if not self.sr.readprogress.text:
            return 
        strng = localization.GetByLabel('UI/Shared/ReadProgress', text=self.sr.readprogress.text, done=have + self.sr.readprogress.prev, total=need + self.sr.readprogress.prev)
        if have == need:
            self.sr.readprogress.prev += have
        self.SetProgressPortion(have / float(need))
        if self.sr.progresstext.text != strng:
            self.sr.progresstext.text = strng
            sm.services['loading'].LogWarn('Setting progress text to: ', strng)
            blue.pyos.synchro.Yield()
        else:
            sm.services['loading'].LogWarn('Not setting progress text to: ', strng)



    def SetStatus(self, title, strng, portion = None, total = None, abortFunc = None, useMorph = 1, autoTick = 1):
        if self is None or self.destroyed:
            return 1
        self._SetCaption(title)
        self.SetAbortFunc(abortFunc)
        self.sr.readprogress = util.KeyVal(text=strng, prev=0)
        if self.sr.progresstext.text != strng:
            self.sr.progresstext.text = strng
            self.sr.progresstext.top = -self.sr.progresstext.height - 2
        self.CheckHeight()
        if portion is not None and total is not None:
            if total == 0:
                self.SetProgressPortion(1.0, useMorph)
            elif portion == 0:
                self.SetProgressPortion(0.0, useMorph)
            else:
                self.SetProgressPortion(portion / float(total), useMorph)
            if portion >= total:
                self.sr.tickTimer = None
                self.stophide = 0
                uthread.new(self.DelayHide)
                uthread.new(self.SanityDelayHide)
            else:
                if autoTick:
                    self.sr.tickTimer = base.AutoTimer(75, self.Tick)
                else:
                    self.sr.tickTimer = None
                self.stophide = 1
                if self.parent and not self.parent.destroyed:
                    self.parent.state = uiconst.UI_NORMAL
        return 0



    def Tick(self):
        new = self.sr.glowClipper.width + 1
        if new == self.sr.glowClipper.width - 10:
            self.sr.tickTimer = None
        self.sr.glowClipper.width = new



    def _SetCaption(self, title):
        if self.sr.Get('loading_caption', None) is None:
            self.sr.loading_caption = uicls.EveCaptionMedium(text=['<center>', title], parent=self.sr.main, align=uiconst.CENTERTOP, width=self.width - 50, top=12, idx=0, state=uiconst.UI_DISABLED, name='caption')
            self.sr.loading_title = title
        elif self.sr.Get('loading_title', None) != title:
            self.sr.loading_caption.text = ['<center>', title]
            self.sr.loading_title = title



    def GetMenu(self):
        return [('Close', self.HideWnd)]



    def HideWnd(self):
        sm.GetService('loading').StopCycle()
        uthread.new(self.DelayHide)



    def DelayHide(self):
        blue.pyos.synchro.SleepWallclock(750)
        if not getattr(self, 'stophide', 0):
            uicore.layer.loading.state = uiconst.UI_HIDDEN
            if self and not self.destroyed and self.sr.glowClipper:
                self.sr.glowClipper.width = 0



    def SanityDelayHide(self):
        blue.pyos.synchro.SleepWallclock(5000)
        if not getattr(self, 'stophide', 0):
            uicore.layer.loading.state = uiconst.UI_HIDDEN
            if self and not self.destroyed and self.sr.glowClipper:
                self.sr.glowClipper.width = 0




