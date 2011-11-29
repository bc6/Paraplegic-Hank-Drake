import blue
import base
import uthread
import types
import traceback
import log
import stackless
import util
import sys
import trinity
import uiconst
import triui
import localization
SEC = 10000000L
MIN = SEC * 60L
HOUR = MIN * 60L

class Eve():

    def __init__(self):
        self._Eve__stationItem = None
        self.clocksynchronizing = 0
        self.clocklastsynchronized = None
        self.rot = blue.Rot()
        self.session = None
        self.taketime = 1
        self.noErrorPopups = 0
        self.dragData = None
        self.maxzoom = 30.0
        self.minzoom = 1000000.0
        self.dev = None
        self.fontFactor = 1.0
        self.themeColor = (0 / 256.0,
         0 / 256.0,
         0 / 256.0,
         192 / 256.0)
        self.themeBgColor = (128 / 256.0,
         128 / 256.0,
         128 / 256.0,
         128 / 256.0)
        self.themeCompColor = (2 / 256.0,
         4 / 256.0,
         8 / 256.0,
         110 / 256.0)
        self.themeCompSubColor = (2 / 256.0,
         4 / 256.0,
         8 / 256.0,
         115 / 256.0)
        self.focus = None
        self.active = None
        self.hiddenUIState = None
        self.chooseWndMenu = None
        self.rookieState = None
        blue.pyos.exceptionHandler = self.ExceptionHandler
        self.logAllGlobalTriuiEvents = 0
        blue.pyos.synchro.timesyncs.append(self.OnTimerResync)
        try:
            import app
            app.ui
        except:
            sys.exc_clear()
        import __builtin__
        if hasattr(__builtin__, 'eve'):
            __builtin__.eve.Release()
        __builtin__.eve = self



    def SetRookieState(self, state):
        if state != self.rookieState:
            self.rookieState = state
            sm.ChainEvent('ProcessRookieStateChange', state)
            settings.user.ui.Set('RookieState', state)



    def OnTimerResync(self, old, new):
        if self.session and self.session.nextSessionChange:
            diff = new - old
            log.general.Log('Readjusting next session change by %.3f seconds' % (diff / 10000000.0), log.LGINFO)
            self.session.nextSessionChange += diff



    def GetDev(self):
        if self.dev is None:
            self.dev = trinity.device
        return self.dev



    def ClearStationItem(self):
        self._Eve__stationItem = None



    def SetStationItemBits(self, bits):
        self._Eve__stationItem = util.Row(['hangarGraphicID',
         'ownerID',
         'itemID',
         'serviceMask',
         'stationTypeID'], bits)



    def HasInvalidStationItem(self):
        return self._Eve__stationItem is None or self._Eve__stationItem.itemID != self.session.stationid



    def __getattr__(self, key):
        if key == 'stationItem':
            if self.session.stationid2 and self.HasInvalidStationItem():
                self.SetStationItemBits(sm.RemoteSvc('stationSvc').GetStationItemBits())
            return self._Eve__stationItem
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        raise AttributeError, key



    def __del__(self):
        print 'Eve is released.'



    def Release(self):
        import sys
        print 'Eve is releasing, my refcount is',
        print sys.getrefcount(self)
        sm.UnregisterNotify(self)
        if self.session is not None:
            base.CloseSession(self.session)
        blue.pyos.exceptionHandler = None



    def Message(self, *args, **kw):
        if args and args[0] == 'IgnoreToTop':
            return 
        if not getattr(uicore, 'desktop', None):
            return 
        curr = stackless.getcurrent()
        if curr.is_main:
            uthread.new(self._Message, *args, **kw).context = 'eve.Message'
        else:
            return apply(self._Message, args, kw)



    def _Message(self, msgkey, dict = None, buttons = None, suppress = None, prioritize = 0, ignoreNotFound = 0, default = None, modal = True):
        if type(msgkey) not in types.StringTypes:
            raise RuntimeError('Invalid argument, msgkey must be a string', msgkey)
        msg = cfg.GetMessage(msgkey, dict, onNotFound='raise')
        if msg.text and settings.public.generic.Get('showMessageId', 0):
            rawMsg = cfg.GetMessage(msgkey, None, onDictMissing=None)
            if rawMsg.text:
                newMsgText = '{message}<br>------------------<br>[Message ID: <b>{messageKey}</b>]<br>{rawMessage}'
                rawMsg.text = rawMsg.text.replace('<', '&lt;').replace('>', '&gt;')
                msg.text = newMsgText.format(message=msg.text, messageKey=msgkey, rawMessage=rawMsg.text)
        if uicore.desktop is None:
            try:
                log.general.Log("Some dude is trying to send a message with eve.Message before  it's ready.  %s,%s,%s,%s" % (strx(msgkey),
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
        if buttons is not None and msg.type not in ('warning', 'question', 'fatal'):
            raise RuntimeError('Cannot override buttons except in warning, question and fatal messages', msg, buttons, msg.type)
        supp = settings.user.suppress.Get('suppress.' + msgkey, None)
        if supp is not None:
            if suppress is not None:
                return suppress
            else:
                return supp
        if not msg.suppress and suppress is not None:
            log.general.Log('eve.Message() called with the suppress parameter without a suppression specified in the message itself - %s / %s' % (msgkey, dict), log.LGWARN)
        elif suppress in (uiconst.ID_CLOSE, uiconst.ID_CANCEL):
            log.general.Log('eve.Message() called with the suppress parameter of ID_CLOSE or ID_CANCEL which is not supported suppression - %s / %s' % (msgkey, dict), log.LGWARN)
        self.LocalSvc('audio').AudioMessage(msg, dict, prioritize)
        sm.ScatterEvent('OnEveMessage', msgkey)
        if uicore.uilib:
            gameui = self.LocalSvc('gameui')
        else:
            gameui = None
        if msg.type in ('hint', 'notify', 'warning', 'question', 'infomodal', 'info'):
            sm.GetService('logger').AddMessage(msg)
        if msg.type in ('info', 'infomodal', 'warning', 'question', 'error', 'fatal', 'windowhelp'):
            supptext = None
            if msg.suppress:
                if buttons in [None, triui.OK]:
                    supptext = localization.GetByLabel('/Carbon/UI/Common/DoNotShowAgain')
                else:
                    supptext = localization.GetByLabel('/Carbon/UI/Common/DoNotAskAgain')
            if gameui:
                if buttons is None:
                    buttons = uiconst.OK
                if msg.icon == '':
                    msg.icon = None
                icon = msg.icon
                if icon is None:
                    icon = {'info': triui.INFO,
                     'infomodal': triui.INFO,
                     'warning': triui.WARNING,
                     'question': triui.QUESTION,
                     'error': triui.ERROR,
                     'fatal': triui.FATAL}.get(msg.type, triui.ERROR)
                customicon = None
                if dict:
                    customicon = dict.get('customicon', None)
                msgtitle = msg.title
                if msg.title is None:
                    msgTitles = {'info': localization.GetByLabel('UI/Common/Information'),
                     'infomodal': localization.GetByLabel('UI/Common/Information'),
                     'warning': localization.GetByLabel('UI/Generic/Warning'),
                     'question': localization.GetByLabel('UI/Common/Question'),
                     'error': localization.GetByLabel('UI/Common/Error'),
                     'fatal': localization.GetByLabel('UI/Common/Fatal')}
                    msgtitle = msgTitles.get(msg.type, localization.GetByLabel('UI/Common/Information'))
                (ret, supp,) = gameui.MessageBox(msg.text, msgtitle, buttons, icon, supptext, customicon, default=default, modal=modal)
                if supp and ret not in (uiconst.ID_CLOSE, uiconst.ID_CANCEL):
                    if not suppress or ret == suppress:
                        settings.user.suppress.Set('suppress.' + msgkey, ret)
                        sm.GetService('settings').SaveSettings()
                return ret
        elif msg.type in ('notify', 'hint', 'event'):
            if gameui:
                return gameui.Say(msg.text)
        elif msg.type in ('audio',):
            pass
        elif msg.type == '':
            if msgkey in ('BrowseHtml', 'BrowseIGB'):
                sm.GetService('ui').Browse(msgkey, dict)
            elif msgkey == 'OwnerPopup':
                ownerID = dict.get('ownerID', const.ownerSystem)
                sm.StartService('gameui').MessageBox(dict.get('body', ''), dict.get('title', ''), triui.OK, triui.INFO)
            else:
                return msg
        else:
            raise RuntimeError('Unknown message type', msg)



    def IsDestroyedWindow(self, tb):
        try:
            argnames = tb.tb_frame.f_code.co_varnames[:(tb.tb_frame.f_code.co_argcount + 1)]
            locals_ = tb.tb_frame.f_locals.copy()
            if argnames:
                for each in argnames:
                    try:
                        theStr = repr(locals_[each])
                        if theStr and theStr.find('destroyed=1') != -1:
                            return theStr
                    except:
                        sys.exc_clear()

            return 0
        except AttributeError:
            sys.exc_clear()
            return 0



    def ExceptionHandler(self, exctype, exc, tb, message = ''):
        try:
            if isinstance(exc, UserError):
                self.Message(exc.msg, exc.dict)
            else:
                toMsgWindow = prefs.GetValue('showExceptions', 0)
                if isinstance(exc, RuntimeError) and len(exc.args) and exc.args[0] == 'ErrMessageNotFound':
                    if toMsgWindow:
                        self.Message('ErrMessageNotFound', exc.args[1])
                else:
                    toMsgWindow = toMsgWindow and not self.noErrorPopups
                    if isinstance(exc, AttributeError):
                        deadWindowCheck = self.IsDestroyedWindow(tb)
                        if deadWindowCheck:
                            name = ''
                            try:
                                nameIdx = deadWindowCheck.find('name=')
                                if nameIdx != -1:
                                    nameIdx += 6
                                    endNameIdx = deadWindowCheck[nameIdx:].find('",')
                                    if endNameIdx != -1:
                                        name = deadWindowCheck[nameIdx:(nameIdx + endNameIdx)]
                            except:
                                sys.exc_clear()
                            log.LogWarn('Message sent to dead window:', name)
                            exctype = exc = tb = None
                            return 
                    if getattr(exc, 'msg', None) == 'DisconnectedFromServer':
                        toMsgWindow = 0
                    severity = log.LGERR
                    extraText = '; caught by eve.ExceptionHandler'
                    if message:
                        extraText += '\nContext info: ' + message
                    return log.LogException(extraText=extraText, toMsgWindow=toMsgWindow, exctype=exctype, exc=exc, tb=tb, severity=severity)
        except:
            exctype = exc = tb = None
            print 'Something fux0red with default exception handling!!'
            traceback.print_exc()
            sys.exc_clear()



    def LocalSvc(self, serviceName):
        return self.session.ConnectToService(serviceName)



    def RemoteSvc(self, serviceName):
        log.LogTraceback('eve.RemoteSvc is no longer supported. Please use sm.RemoteSvc instead')
        conn = self.LocalSvc('connection')
        return conn.ConnectToService(serviceName)



    def ProxySvc(self, serviceName):
        log.LogTraceback('eve.ProxySvc is no longer supported. Please use sm.ProxySvc instead')
        conn = self.LocalSvc('connection')
        return conn.ConnectToProxyService(serviceName)



    def MachoPing(self, *args):
        sm.services['machoNet'].Ping(*args)



    def Ping(self, count = 5):
        server = sm.ProxySvc('machoNet')
        total = 0.0
        if count > 0:
            display = 1
        else:
            display = 0
            count = -count
        if display:
            print 'Pinging server ',
        for i in xrange(count):
            t = blue.os.GetWallclockTimeNow()
            servertime = server.GetTime()
            servertime = server.GetTime()
            servertime = server.GetTime()
            servertime = server.GetTime()
            t2 = blue.os.GetWallclockTimeNow()
            ping = blue.os.TimeAsDouble(t2 - t) / 4.0
            total = total + ping
            if display:
                print int(ping * 1000),
                print 'ms.',
            blue.pyos.synchro.SleepWallclock(1000)

        avg = total * 1000 / float(count)
        if display:
            print 'Average ping %.1f ms.' % (avg,)
        return avg



    def SynchronizeClock(self, firstTime = 1, maxIterations = 5):
        log.general.Log('eve.synchronizeClock called', log.LGINFO)
        if not firstTime:
            if self.clocklastsynchronized is not None and blue.os.GetWallclockTime() - self.clocklastsynchronized < HOUR:
                return 
        if self.clocksynchronizing:
            return 
        self.clocklastsynchronized = blue.os.GetWallclockTime()
        self.clocksynchronizing = 1
        try:
            diff = 0
            goodCount = 0
            lastElaps = None
            log.general.Log('***   ***   ***   ***   Clock Synchronizing loop initiating      ***   ***   ***   ***', log.LGINFO)
            for i in range(maxIterations):
                myTime = blue.os.GetWallclockTimeNow()
                serverTime = sm.ProxySvc('machoNet').GetTime()
                now = blue.os.GetWallclockTimeNow()
                elaps = now - myTime
                serverTime += elaps / 2
                diff = float(now - serverTime) / float(SEC)
                if diff > 2.0 and not firstTime:
                    logflag = log.LGERR
                else:
                    logflag = log.LGINFO
                log.general.Log('Synchronizing clock diff %.3f sec elaps %f sec.' % (diff, elaps / float(SEC)), logflag)
                if lastElaps is None or elaps < lastElaps and elaps < SEC:
                    goodCount += 1
                    log.general.Log('Synchronizing clock:  iteration completed, setting time', logflag)
                    blue.pyos.synchro.ResetClock(serverTime)
                    lastElaps = elaps
                else:
                    log.general.Log('Synchronizing clock:  iteration ignored as it was less accurate (%f) than our current time (%f)' % (elaps / float(SEC), lastElaps / float(SEC)), log.LGINFO)
                if goodCount >= 3:
                    break
                firstTime = 0

            log.general.Log('***   ***   ***   ***   Clock Synchronizing loop completed       ***   ***   ***   ***', log.LGINFO)

        finally:
            self.clocksynchronizing = 0




    def IsClockSynchronizing(self):
        if self.clocksynchronizing:
            log.general.Log('Clock synchronization in progress', log.LGINFO)
        return self.clocksynchronizing



    def WaitForResourceLoad(self, timeLimit = None):
        trinity.WaitForResourceLoads()



import __builtin__
__builtin__.srv = None
e = Eve()
exports = {'eve.eve': e}

