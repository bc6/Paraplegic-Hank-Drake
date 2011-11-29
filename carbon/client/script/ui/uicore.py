import uthread
import blue
import localization
import log
import types
import uiutil
import uiconst
import uicls
import uitest
import trinity
import sys
import traceback
import weakref
from util import ResFile

class UIDeviceResource():

    def __init__(self):
        dev = trinity.GetDevice()
        dev.RegisterResource(self)



    def OnInvalidate(self, level):
        pass



    def OnCreate(self, dev):
        if getattr(uicore, 'uilib', None) is None:
            return 
        uicore.UpdateCursor(uicore.uilib.mouseOver, 1)
        uicore.CheckHint()
        uicore.deviceCaps = trinity.d3d.GetDeviceCaps(trinity.device.adapter, 1)




class UICoreBase():
    __guid__ = 'uicls.uicore'

    def __init__(self):
        import __builtin__
        if 'uicore' in __builtin__.__dict__.keys():
            pass
        else:
            self.newRendererEnabled = False
            self._lastCursor = None
            self._cursorSprite = None
            self._hint = None
            self.isRunning = False
            self.desktop = None
            self.dragData = None
            self.triappargs = {'title': boot.appname,
             'left': 0,
             'top': 0,
             'colordepth': 0,
             'exclusiveInput': 0,
             'refreshrate': 0}
            __builtin__.uicore = self
        blue.pyos.exceptionHandler = self._ExceptionHandler
        log.SetUiMessageFunc(self.Message)
        self.textObjects = weakref.WeakSet()
        self.deviceResource = UIDeviceResource()



    def Startup(self, layerlist):
        sm.GetService('settings').LoadSettings()
        deviceSvc = sm.StartServiceAndWaitForRunningState('device')
        deviceSvc.CreateDevice()
        self.device = deviceSvc
        uicls._ExposeCoreClassesWithOutCorePostfix()
        self.uilib = self.event = uicls.Uilib()
        self.desktop = self.uilib.desktop
        self.LoadLayers(layerlist)
        for serviceName in ['font',
         'registry',
         'loading',
         'audio',
         'ime',
         'cmd']:
            setattr(self, serviceName, sm.StartServiceAndWaitForRunningState(serviceName))

        self.effect = uicls.UIEffects()
        self.animations = uicls.UIAnimations()
        trinity.device.RegisterResource(self)
        uicore.deviceCaps = trinity.d3d.GetDeviceCaps(trinity.device.adapter, 1)
        self.isRunning = True



    def IsReady(self):
        return getattr(self, 'isRunning', False)



    def OnInvalidate(self, *args):
        self.layer.hint.Flush()
        self._hint = None



    def OnCreate(self, *args):
        self.layer.hint.Flush()
        self._hint = None



    def LoadLayers(self, layerlist):
        self.layer = uicls.LayerManager()
        self.layerData = {}
        self.layerList = layerlist
        layerlist = layerlist or self.GetDefaultLayers()
        for (layerName, className, subLayers,) in layerlist:
            self.desktop.AddLayer(layerName, className, subLayers)




    def GetDefaultLayers(self):
        layers = [('l_hint', None, None),
         ('l_menu', None, None),
         ('l_modal', None, None),
         ('l_abovemain', None, None),
         ('l_main', None, None),
         ('l_loading', None, None),
         ('l_dragging', None, None)]
        return layers



    def OnUilibEvent(self, item, msgID, args):
        if msgID == uiconst.UI_MOUSEDOWN:
            if not uiutil.IsUnder(item, self.layer.menu):
                uiutil.Flush(self.layer.menu)
            self.registry.SetFocus(item)



    def CheckCursor(self):
        self.UpdateCursor(uicore.uilib.mouseOver)



    def CheckHint(self):
        if uicore.uilib.selectedCursorType != uiconst.UICURSOR_NONE:
            self.UpdateHint(uicore.uilib.mouseOver)



    def UpdateHint(self, item, force = 0):
        if self.isRunning:
            if self._hint is None or self._hint.destroyed:
                for each in self.layer.hint.children[:]:
                    if each.__class__ in (uicls.Hint, uicls.HintCore):
                        each.Close()

                self._hint = uicls.Hint(name='hint', parent=self.layer.hint, align=uiconst.RELATIVE)
            self._hint.LoadHintFromItem(item, force)



    def UpdateCursor(self, item, force = 0):
        cursor = 0
        ic = getattr(item, 'cursor', None)
        if ic is not None and ic >= 0:
            cursor = ic
        elif item:
            if item.HasEventHandler('OnChar'):
                cursor = 7
            else:
                hasGetMenu = item.HasEventHandler('GetMenu')
                clickFunc = item.HasEventHandler('OnClick')
                if clickFunc:
                    if hasGetMenu:
                        cursor = 22
                    else:
                        cursor = 1
                elif hasGetMenu:
                    cursor = 12
        if force or self._lastCursor != cursor:
            self.uilib.SetCursor(cursor)
            self._lastCursor = cursor



    def GetLayer(self, name):
        return self.layer.GetLayer(name)



    def Message(self, *args, **kw):
        if args and args[0] == 'IgnoreToTop':
            return 
        if not hasattr(self, 'uilib') or not getattr(self.uilib, 'desktop', None):
            return 
        import stackless
        curr = stackless.getcurrent()
        if curr.is_main:
            uthread.new(self._Message, *args, **kw).context = 'uicore.Message'
        else:
            return apply(self._Message, args, kw)



    def SimpleMessage(self, title, body, buttons = uiconst.OK):
        return self.Message('CustomQuestion', dict={'header': title,
         'question': body}, buttons=buttons)



    def _Message(self, msgkey, dict = None, buttons = None, suppress = None, prioritize = 0, ignoreNotFound = 0, default = None, modal = True):
        if not isinstance(msgkey, basestring):
            raise RuntimeError('Invalid argument, msgkey must be a string', msgkey)
        try:
            msg = cfg.GetMessage(msgkey, dict, onNotFound='raise')
        except RuntimeError as what:
            if what.args[0] == 'ErrMessageNotFound':
                if ignoreNotFound:
                    return suppress
                log.LogTraceback()
                msg = cfg.GetMessage(msgkey, dict, onNotFound='return')
            else:
                raise 
        if not hasattr(self, 'desktop') or self.desktop is None:
            print "Some dude is trying to send a message with uicore.Message before  it's ready.",
            print msgkey,
            print dict,
            print buttons,
            print suppress
            try:
                log.general.Log("Some dude is trying to send a message with uicore.Message before  it's ready.  %s,%s,%s,%s" % (strx(msgkey),
                 strx(dict),
                 strx(buttons),
                 strx(suppress)), log.LGERR)
                flag = 0
                flag |= 48
                flag |= 8192
                blue.os.MessageBox(msg.text, msg.title, flag)
            except:
                sys.exc_clear()
            return 
        if buttons is not None and msg.type not in ('warning', 'question'):
            raise RuntimeError('Cannot override buttons except in warning and question', msg, buttons, msg.type)
        supp = settings.user.suppress.Get('suppress.' + msgkey, None)
        if supp is not None:
            if suppress is not None:
                return suppress
            else:
                return supp
        if msg.type in ('info', 'infomodal', 'warning', 'question', 'error', 'fatal'):
            supptext = None
            if msg.suppress:
                if buttons in [None, uiconst.OK]:
                    supptext = localization.GetByLabel('/Carbon/UI/Common/DoNotShowAgain')
                else:
                    supptext = localization.GetByLabel('/Carbon/UI/Common/DoNotAskAgain')
            if buttons is None:
                buttons = uiconst.OK
            msg.icon = msg.icon or None
            icon = msg.icon or None
            if icon is None:
                icon = {'info': uiconst.INFO,
                 'infomodal': uiconst.INFO,
                 'warning': uiconst.WARNING,
                 'question': uiconst.QUESTION,
                 'error': uiconst.ERROR,
                 'fatal': uiconst.FATAL}[msg.type]
            customicon = None
            if dict:
                customicon = dict.get('customicon', None)
            (ret, supp,) = self.MessageBox(msg.text, msg.title, buttons, icon, supptext, customicon, default=default, modal=modal)
            if supp and ret not in (uiconst.ID_CLOSE, uiconst.ID_CANCEL):
                settings.user.suppress.Set('suppress.' + msgkey, ret)
                sm.GetService('settings').SaveSettings()
            return ret
        if msg.type in ('notify', 'hint', 'event'):
            try:
                import gameui
                (ret, supp,) = gameui.Say(msg.text)
            except:
                self.Say(msg.text)
        elif msg.type != 'audio':
            raise RuntimeError('Unknown message type', msg)



    def CustomNotify(self, message):
        self.Message('CustomNotify', {'notify': message})



    def MessageBox(self, text, title = 'Wod', buttons = None, icon = None, suppText = None, customicon = None, height = None, blockconfirmonreturn = 0, default = None, modal = True):
        if not getattr(self, 'desktop', None):
            return 
        if buttons is None:
            buttons = uiconst.ID_OK
        msgbox = uicls.MessageBox.Open(parent=self.layer.abovemain)
        msgbox.blockconfirmonreturn = blockconfirmonreturn
        msgbox.Execute(text, title, buttons, icon, suppText, customicon, height, default=default)
        if modal:
            ret = msgbox.ShowModal()
        else:
            ret = msgbox.ShowDialog()
        return (ret, msgbox.suppress)



    def Say(self, msgtext, time = 100):
        for each in self.layer.abovemain.children[:]:
            if each.name == 'message':
                each.ShowMsg(msgtext)
                return 
            print each.name

        message = uicls.Message(parent=self.layer.abovemain, name='message')
        message.ShowMsg(msgtext)



    def _ExceptionHandler(self, exctype, exc, tb, message = ''):
        try:
            if isinstance(exc, UserError):
                self.Message(exc.msg, exc.dict)
            elif isinstance(exc, TaskletExit):
                return 
            toMsgWindow = prefs.GetValue('exceptionPopups', 0)
            if isinstance(exc, RuntimeError) and len(exc.args) and exc.args[0] == 'ErrMessageNotFound':
                if toMsgWindow:
                    self.Message('ErrMessageNotFound', exc.args[1])
            else:
                if getattr(exc, 'msg', None) == 'DisconnectedFromServer':
                    toMsgWindow = 0
                extraText = '; caught by ExceptionHandler'
                if message:
                    extraText += '\nContext info: ' + message
                return log.LogException(extraText=extraText, toMsgWindow=toMsgWindow, exctype=exctype, exc=exc, tb=tb, severity=log.LGERR)
        except:
            exctype = exc = tb = None
            print 'Something fux0red with default exception handling!!'
            traceback.print_exc()



    def WaitForResourceLoad(self):
        fence = trinity.device.GetCurrentResourceLoadFence()
        timeWaited = 0
        while trinity.device.GetLastResourceLoadFenceReached() < fence:
            waitMs = 100
            blue.pyos.synchro.SleepWallclock(waitMs)
            timeWaited += waitMs
            if timeWaited % 5000 == 0:
                log.general.Log('WaitForResourceLoad has waited for %d seconds! (%d vs. %d)' % (timeWaited / 1000, trinity.device.GetLastResourceLoadFenceReached(), fence), log.LGERR)




    def ScaleDpi(self, value):
        if self.desktop:
            return int(value * self.desktop.dpiScaling + 0.5)
        else:
            return int(value + 0.5)



    def ScaleDpiF(self, value):
        if self.desktop:
            return value * self.desktop.dpiScaling
        else:
            return value



    def ReverseScaleDpi(self, value):
        if self.desktop:
            return int(value / self.desktop.dpiScaling + 0.5)
        else:
            return value




def GetClass(name):
    import uicls
    custom = getattr(uicls, name, None)
    if custom:
        return custom
    core = getattr(uicls, name + 'Core', None)
    if core:
        return core
    log.LogError('Unknown class request', name)
    raise AttributeError('UI Class %s not found' % (name,))


uicorebase = UICoreBase()
ret = {'uicls.Get': GetClass,
 'gameui._boot': 1,
 'uiutil._boot': 1,
 'uitest._boot': 1,
 'menu._boot': 1,
 'globalConstants._boot': 1}
exports = ret

