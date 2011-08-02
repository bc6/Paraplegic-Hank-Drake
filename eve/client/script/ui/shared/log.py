import blue
import uthread
import uix
import uiutil
import xtriui
import form
import log
import util
import listentry
import service
import os
import draw
import base
import sys
import uicls
import uiconst
globals().update(service.consts)
MAX_MSGS = 256
SEC = 10000000L
MIN = SEC * 60L
HOUR = MIN * 60L
DAY = HOUR * 24L

class Logger(service.Service):
    __exportedcalls__ = {'AddMessage': [],
     'AddCombatMessage': [],
     'AddText': [],
     'Show': [],
     'GetLog': [ROLE_SERVICE]}
    __guid__ = 'svc.logger'
    __notifyevents__ = ['ProcessSessionChange']
    __servicename__ = 'logger'
    __displayname__ = 'Logger Client Service'
    __dependencies__ = []
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.LogInfo('Starting Logger')
        self.broken = 0
        self.Reset()
        self.timer = None
        self.newfileAttempts = 0
        self.addmsg = []
        self.combatMessagePeriod = 10000L * prefs.GetValue('combatMessagePeriod', 200)
        self.lastCombatMessage = 0



    def Stop(self, memStream = None):
        self.DumpToLog()
        self.messages = []
        self.msglog = []
        self.timer = None
        self.addmsg = []



    def ProcessSessionChange(self, isremote, session, change):
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed:
            if eve.session.charid:
                self.DumpToLog()
                self.Reset()
        elif not eve.session.charid:
            self.Stop()



    def GetLog(self, maxsize = const.petitionMaxCombatLogSize, *args):
        log.LogInfo('Getting logfiles')
        self.DumpToLog()
        now = util.FmtDate(blue.os.GetTime()).replace('.', '')[:8]
        yesterday = util.FmtDate(blue.os.GetTime() - DAY).replace('.', '')[:8]
        root = blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL) + '/EVE/logs/Gamelogs'
        logs = []
        for each in os.listdir(root):
            filename = os.path.join(root, each)
            fooname = filename[:-11]
            if fooname.endswith(now) or fooname.endswith(yesterday):
                logs.append((each, filename))

        logs.sort(reverse=True)
        ret = []
        bytesread = 0
        for (k, filename,) in logs:
            f = None
            try:
                f = file(filename)
                tmp = f.read()
                f.close()
                line = '\n\n%s:\n%s' % (filename.encode('utf8', 'replace'), tmp)
                bytesread += len(line)
                ret.append(line)
                if bytesread > maxsize:
                    break
            except:
                log.LogException()
                sys.exc_clear()
                if f and not f.closed:
                    f.close()

        log.LogInfo('Getting logfiles done')
        ret.reverse()
        return ''.join(ret)[(-maxsize):]



    def Reset(self, newFileOnly = 0):
        self.resettime = blue.os.GetTime()
        if not newFileOnly:
            self.messages = []
            self.msglog = ['-' * 60 + '\n', '  %s\n' % mls.UI_SHARED_LOGGAMELOG.encode('utf8', 'replace')]
            if eve.session.charid:
                self.msglog.append(('  %s: %s\n' % (mls.UI_SHARED_LOGLISTENER, cfg.eveowners.Get(eve.session.charid).name)).encode('utf8', 'replace'))
            self.msglog += [('  %s: %s\n' % (mls.UI_SHARED_LOGSESSIONSTARTED, util.FmtDate(self.resettime))).encode('utf8', 'replace'),
             '',
             '-' * 60 + '\n',
             '']
            self.DumpToLog()



    def Show(self, *args):
        if eve.session.charid:
            wnd = self.GetWnd(1)
            wnd.Maximize()



    def GetWnd(self, new = 0):
        wnd = sm.GetService('window').GetWindow('logger')
        if not wnd and new:
            wnd = sm.GetService('window').GetWindow('logger', decoClass=form.Logger, create=1)
            wnd.SetCaption(mls.UI_SHARED_LOG)
            wnd.SetMinSize([256, 195])
            wnd.SetWndIcon('ui_34_64_4', hidden=True)
            wnd.SetTopparentHeight(0)
            wnd.SetScope('all')
            wnd.OnClose_ = self.CloseWnd
            wnd.OnEndMaximize = self.OnEndMaximize
            wnd.GetMenu = self.GetWndMenu
            wnd.OnTabSelect = self.OnTabSelect
            margin = const.defaultPadding
            scroll = uicls.Scroll(parent=uiutil.GetChild(wnd, 'main'), id='loggerScroll', padding=(margin,
             margin,
             margin,
             margin))
            wnd.sr.scroll = scroll
            settings = uicls.Container(name='settings', parent=scroll.parent, pos=(const.defaultPadding * 2,
             const.defaultPadding * 2,
             const.defaultPadding * 2,
             const.defaultPadding * 2))
            wnd.sr.settings = settings
            maintabs = uicls.TabGroup(name='tabparent', parent=scroll.parent, idx=0)
            maintabs.Startup([[mls.UI_SHARED_LOG,
              scroll,
              self,
              'log'], [mls.UI_GENERIC_SETTINGS,
              settings,
              self,
              'settings']], 'loggertabs')
        return wnd



    def Load(self, key):
        if key == 'log':
            self.LoadAllMessages()
        elif key == 'settings':
            if not getattr(self, 'settingsinited', 0):
                self.LoadSettings()
                self.settingsinited = 1



    def OnTabSelect(self):
        self.LoadAllMessages()



    def LoadSettings(self):
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            for (hint, config,) in ((mls.UI_SHARED_LOGSHOWINFO, 'showinfologmessages'),
             (mls.UI_SHARED_LOGSHOWWARN, 'showwarninglogmessages'),
             (mls.UI_SHARED_LOGSHOWERROR, 'showerrorlogmessages'),
             (mls.UI_SHARED_LOGSHOWCOMBAT, 'showcombatlogmessages'),
             (mls.UI_SHARED_LOGSHOWNOTIFY, 'shownotifylogmessages'),
             (mls.UI_SHARED_LOGSHOWQUESTION, 'showquestionlogmessages')):
                uicls.Checkbox(text=hint, parent=wnd.sr.settings, configName=config, retval=None, checked=settings.user.ui.Get(config, 1), groupname=None, prefstype=('user', 'ui'))

            uicls.Container(name='push', align=uiconst.TOTOP, height=4, parent=wnd.sr.settings)
            for amt in (100, 1000):
                uicls.Checkbox(text=mls.UI_SHARED_LOGSHOWNUMMESSAGES % {'num': amt}, parent=wnd.sr.settings, configName='logmessageamount', retval=amt, checked=amt == settings.user.ui.Get('logmessageamount', 100), groupname='logamount', prefstype=('user', 'ui'))




    def OnEndMaximize(self, *args):
        self.LoadAllMessages()



    def LoadAllMessages(self):
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed and wnd.state in (uiconst.UI_NORMAL, uiconst.UI_PICKCHILDREN) and self.messages:
            showmsgs = []
            maxlog = settings.user.ui.Get('logmessageamount', 100)
            t = len(self.messages)
            r = min(maxlog, t)
            for _i in xrange(r):
                i = t - 1 - _i
                (text, msgtext, msgtype,) = self.messages[i]
                if not self.ShowMessage(msgtype):
                    continue
                entry = listentry.Get('Text', {'text': text,
                 'canOpen': mls.UI_GENERIC_LOGMESSAGE,
                 'line': 1})
                showmsgs.append(entry)

            wnd.sr.scroll.Load(contentList=showmsgs, reversesort=True, headers=[mls.UI_GENERIC_TIME, mls.UI_GENERIC_TYPE, mls.UI_GENERIC_MESSAGE])



    def CloseWnd(self, *args):
        self.inited = 0
        self.settingsinited = 0
        self.timer = None
        self.addmsg = []



    def AddMessage(self, msg, msgtype = None):
        if msg.type == 'error' and not settings.user.ui.Get('logerrors', 0):
            return 
        self.AddText(msg.text, msgtype or msg.type or 'notify', msg)



    def AddCombatMessage(self, msgKey, msgTextArgs):
        msg = cfg.GetMessage(msgKey, msgTextArgs)
        if msg.type == 'error' and not settings.user.ui.Get('logerrors', 0):
            return 
        now = blue.os.GetTime()
        if now - self.lastCombatMessage < self.combatMessagePeriod:
            display = 0
        else:
            display = 1
            self.lastCombatMessage = now
        self.AddText(msg.text, 'combat')
        if display:
            sm.GetService('gameui').Say(msg.text)



    def AddText(self, msgtext, msgtype = None, msg = None):
        if msgtype:
            msgtype = msgtype.replace('infomodal', 'info')
        text = msgtext
        color = {'error': '<color=0xffeb3700>',
         'warning': '<color=0xffffd800>',
         'slash': '<color=0xffff5500>',
         'combat': '<color=0xffff0000>'}.get(msgtype, '<color=0xffffffff>')
        time = blue.os.GetTime()
        if msgtype:
            label = getattr(mls, 'UI_SHARED_LOG' + msgtype.upper())
        else:
            label = mls.UI_SYSMENU_GENERIC
        if not self.broken:
            self.msglog.append(('[%20s ] (%s) %s\n' % (util.FmtDate(time), msgtype, msgtext)).encode('utf8', 'replace'))
            if len(self.msglog) == 20:
                self.DumpToLog()
        if not self.ShowMessage(msgtype):
            return 
        text = '%s<t>%s%s</color><t>%s' % (util.FmtDate(blue.os.GetTime(), 'nl'),
         color,
         label,
         msgtext)
        self.messages.append((text, msgtext, msgtype))
        maxlog = settings.user.ui.Get('logmessageamount', 100)
        if len(self.messages) > maxlog * 2:
            self.messages = self.messages[(-maxlog):]
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed and wnd.state in (uiconst.UI_NORMAL, uiconst.UI_PICKCHILDREN):
            if wnd.sr.scroll.state != uiconst.UI_HIDDEN:
                self.addmsg.append(listentry.Get('Text', {'text': text,
                 'canOpen': 'Log message',
                 'line': 1}))
                if not self.timer:
                    self._AddText()



    def _AddText(self):
        if not self.addmsg:
            self.timer = None
            return 
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed and wnd.state in (uiconst.UI_NORMAL, uiconst.UI_PICKCHILDREN):
            if wnd.sr.scroll.state != uiconst.UI_HIDDEN:
                maxlog = settings.user.ui.Get('logmessageamount', 100)
                if not self.timer:
                    self.timer = base.AutoTimer(1000, self._AddText)
                if len(wnd.sr.scroll.sr.nodes) == 0:
                    wnd.sr.scroll.LoadHeaders([mls.UI_GENERIC_TIME, mls.UI_GENERIC_TYPE, mls.UI_GENERIC_MESSAGE])
                wnd.sr.scroll.AddEntries(0, self.addmsg)
                self.addmsg = []
                revSorting = wnd.sr.scroll.GetSortDirection() or wnd.sr.scroll.GetSortBy() is None
                if revSorting:
                    wnd.sr.scroll.RemoveEntries(wnd.sr.scroll.GetNodes()[maxlog:])
                else:
                    wnd.sr.scroll.RemoveEntries(wnd.sr.scroll.GetNodes()[:(-maxlog)])



    def ShowMessage(self, msgtype):
        return settings.user.ui.Get('show%slogmessages' % msgtype, 1)



    def DumpToLog(self):
        if self.broken or not self.msglog:
            return 
        logfile = None
        try:
            filename = self.GetLogfileName()
            try:
                logfile = file(filename, 'a')
            except:
                if self.newfileAttempts < 3:
                    log.LogWarn('Failed to open the logfile %s, creating new logfile...' % filename)
                    filename = self.GetLogfileName(1)
                    log.LogWarn('new logfile name is: ', filename)
                    logfile = file(filename, 'a')
                    self.newfileAttempts += 1
                else:
                    self.broken = 1
                    log.LogException(toAlertSvc=0)
                sys.exc_clear()
            if logfile:
                try:
                    logfile.writelines(self.msglog)
                    logfile.close()
                except IOError:
                    log.LogException(toAlertSvc=0)
                    sys.exc_clear()
                self.msglog = []
        except:
            log.LogException(toAlertSvc=0)
            sys.exc_clear()
        if logfile and not logfile.closed:
            logfile.close()



    def CopyLog(self):
        self.DumpToLog()
        logfile = None
        try:
            filename = self.GetLogfileName()
            logfile = file(filename)
            ret = logfile.read()
            logfile.close()
            blue.pyos.SetClipboardData(ret)
        except:
            log.LogException()
            sys.exc_clear()
        if logfile and not logfile.closed:
            logfile.close()



    def GetLogfileName(self, reset = 0):
        if reset:
            self.Reset(reset)
        filename = '%s' % util.FmtDate(self.resettime)
        filename = filename.replace('\\', '_').replace('?', '_').replace('*', '_').replace(':', '').replace('.', '').replace(' ', '_').replace('/', '_')
        filename = blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL) + '/EVE/logs/Gamelogs/%s.txt' % filename
        return filename



    def GetWndMenu(self, *args):
        wnd = self.GetWnd()
        if wnd:
            m = uicls.Window.GetMenu(wnd)
            m += [None, (mls.UI_CMD_CAPTURELOG, self.DumpToLog), (mls.UI_CMD_COPYLOG, self.CopyLog)]
            return m




class LoggerWindow(uicls.Window):
    __guid__ = 'form.Logger'


