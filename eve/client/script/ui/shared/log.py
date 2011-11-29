import blue
import uthread
import uix
import uiutil
import xtriui
import form
import log
import util
import listentry
import localization
import service
import os
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
        self.newfileAttempts = 0
        self.addmsg = []
        self.combatMessagePeriod = 10000L * prefs.GetValue('combatMessagePeriod', 200)
        self.lastCombatMessage = 0



    def Stop(self, memStream = None):
        self.DumpToLog()
        self.messages = []
        self.msglog = []
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
        (year, month, weekday, day, hour, minute, second, msec,) = blue.os.GetTimeParts(blue.os.GetWallclockTime())
        now = '%d%.2d%.0d' % (year, month, day)
        (year, month, weekday, day, hour, minute, second, msec,) = blue.os.GetTimeParts(blue.os.GetWallclockTime() - DAY)
        yesterday = '%d%.2d%.0d' % (year, month, day)
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
        self.resettime = blue.os.GetWallclockTime()
        if not newFileOnly:
            self.messages = []
            self.msglog = ['-' * 60 + '\n', '  %s\n' % localization.GetByLabel('UI/Accessories/Log/GameLog').encode('utf8', 'replace')]
            if eve.session.charid:
                self.msglog.append(('  %s: %s\n' % (localization.GetByLabel('UI/Accessories/Log/Listener'), cfg.eveowners.Get(eve.session.charid).name)).encode('utf8', 'replace'))
            self.msglog += [('  %s: %s\n' % (localization.GetByLabel('UI/Accessories/Log/SessionStarted'), util.FmtDate(self.resettime))).encode('utf8', 'replace'),
             '',
             '-' * 60 + '\n',
             '']
            self.DumpToLog()



    def GetWnd(self):
        return form.Logger.GetIfOpen()



    def GetMessages(self):
        self.addmsg = []
        return self.messages



    def GetPendingMessages(self):
        retval = self.addmsg
        self.addmsg = []
        return retval



    def AddMessage(self, msg, msgtype = None):
        if msg.type == 'error' and not settings.user.ui.Get('logerrors', 0):
            return 
        self.AddText(msg.text, msgtype or msg.type or 'notify', msg)



    def AddCombatMessage(self, msgKey, msgTextArgs):
        msg = cfg.GetMessage(msgKey, msgTextArgs)
        if msg.type == 'error' and not settings.user.ui.Get('logerrors', 0):
            return 
        now = blue.os.GetWallclockTime()
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
        messages = {'error': localization.GetByLabel('UI/Accessories/Log/LogError'),
         'warning': localization.GetByLabel('UI/Accessories/Log/LogWarn'),
         'slash': localization.GetByLabel('UI/Accessories/Log/LogSlash'),
         'combat': localization.GetByLabel('UI/Accessories/Log/LogCombat'),
         'notify': localization.GetByLabel('UI/Accessories/Log/LogNotify'),
         'question': localization.GetByLabel('UI/Accessories/Log/LogQuestion'),
         'info': localization.GetByLabel('UI/Accessories/Log/LogInfo'),
         'hint': localization.GetByLabel('UI/Accessories/Log/LogHint')}
        time = blue.os.GetWallclockTime()
        if msgtype:
            if msgtype in messages:
                label = messages[msgtype]
            else:
                label = msgtype
        else:
            label = localization.GetByLabel('UI/Accessories/Log/Generic')
        if not self.broken:
            self.msglog.append(('[%20s ] (%s) %s\n' % (util.FmtDate(time), msgtype, msgtext)).encode('utf8', 'replace'))
            if len(self.msglog) == 20:
                self.DumpToLog()
        if not self.ShowMessage(msgtype):
            return 
        text = localization.GetByLabel('UI/Accessories/Log/MessageOutput', logtime=blue.os.GetWallclockTime(), color=color, label=label, message=msgtext)
        self.messages.append((text, msgtext, msgtype))
        maxlog = settings.user.ui.Get('logmessageamount', 100)
        if len(self.messages) > maxlog * 2:
            self.messages = self.messages[(-maxlog):]
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            self.addmsg.append((text, msgtext, msgtype))



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
        (year, month, weekday, day, hour, minute, second, msec,) = blue.os.GetTimeParts(self.resettime)
        filename = '%d%.2d%.2d_%.2d%.2d%.2d' % (year,
         month,
         day,
         hour,
         minute,
         second)
        filename = blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL) + '/EVE/logs/Gamelogs/%s.txt' % filename
        return filename




class LoggerWindow(uicls.Window):
    __guid__ = 'form.Logger'
    default_windowID = 'logger'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetCaption(localization.GetByLabel('UI/Accessories/Log/Log'))
        self.SetMinSize([256, 195])
        self.SetWndIcon('ui_34_64_4', hidden=True)
        self.SetTopparentHeight(0)
        self.SetScope('all')
        margin = const.defaultPadding
        scroll = uicls.Scroll(parent=uiutil.GetChild(self, 'main'), padding=margin)
        scroll.Load(contentList=[], fixedEntryHeight=18, headers=[localization.GetByLabel('UI/Common/DateWords/Time'), localization.GetByLabel('UI/Accessories/Log/Type'), localization.GetByLabel('UI/Accessories/Log/Message')])
        self.sr.scroll = scroll
        settings = uicls.Container(name='settings', parent=scroll.parent, pos=(const.defaultPadding * 2,
         const.defaultPadding * 2,
         const.defaultPadding * 2,
         const.defaultPadding * 2))
        self.sr.settings = settings
        maintabs = uicls.TabGroup(name='tabparent', parent=scroll.parent, idx=0)
        maintabs.Startup([[localization.GetByLabel('UI/Accessories/Log/Log'),
          scroll,
          self,
          'log'], [localization.GetByLabel('UI/Accessories/Log/Settings'),
          settings,
          self,
          'settings']], 'loggertabs')
        self.timer = base.AutoTimer(1000, self.CheckMessages)



    def CheckMessages(self):
        if uiutil.IsVisible(self.sr.scroll):
            messages = sm.GetService('logger').GetPendingMessages()
            if messages:
                entryList = []
                maxlog = settings.user.ui.Get('logmessageamount', 100)
                for msg in messages:
                    (text, msgtext, msgtype,) = msg
                    if not self.ShowMessage(msgtype):
                        continue
                    entryList.append(listentry.Get('Text', {'text': text,
                     'canOpen': localization.GetByLabel('UI/Accessories/Log/LogMessage'),
                     'line': 1}))

                self.sr.scroll.AddEntries(0, entryList)
                revSorting = self.sr.scroll.GetSortDirection() or self.sr.scroll.GetSortBy() is None
                if revSorting:
                    self.sr.scroll.RemoveEntries(self.sr.scroll.GetNodes()[maxlog:])
                else:
                    self.sr.scroll.RemoveEntries(self.sr.scroll.GetNodes()[:(-maxlog)])



    def GetMenu(self, *args):
        m = uicls.Window.GetMenu(self)
        m += [None, (localization.GetByLabel('UI/Accessories/Log/CaptureLog'), sm.GetService('logger').DumpToLog), (localization.GetByLabel('UI/Accessories/Log/CopyLog'), sm.GetService('logger').CopyLog)]
        return m



    def OnTabSelect(self):
        self.LoadAllMessages()



    def Load(self, key):
        if key == 'log':
            self.LoadAllMessages()
        elif key == 'settings':
            if not getattr(self, 'settingsinited', 0):
                self.LoadSettings()
                self.settingsinited = 1



    def LoadSettings(self):
        for (hint, config,) in ((localization.GetByLabel('UI/Accessories/Log/ShowInfo'), 'showinfologmessages'),
         (localization.GetByLabel('UI/Accessories/Log/ShowWarn'), 'showwarninglogmessages'),
         (localization.GetByLabel('UI/Accessories/Log/ShowError'), 'showerrorlogmessages'),
         (localization.GetByLabel('UI/Accessories/Log/ShowCombat'), 'showcombatlogmessages'),
         (localization.GetByLabel('UI/Accessories/Log/ShowNotify'), 'shownotifylogmessages'),
         (localization.GetByLabel('UI/Accessories/Log/ShowQuestion'), 'showquestionlogmessages')):
            uicls.Checkbox(text=hint, parent=self.sr.settings, configName=config, retval=None, checked=settings.user.ui.Get(config, 1), groupname=None, prefstype=('user', 'ui'))

        uicls.Container(name='push', align=uiconst.TOTOP, height=4, parent=self.sr.settings)
        for amt in (100, 1000):
            uicls.Checkbox(text=localization.GetByLabel('UI/Accessories/Log/ShowNumMessages', num=amt), parent=self.sr.settings, configName='logmessageamount', retval=amt, checked=amt == settings.user.ui.Get('logmessageamount', 100), groupname='logamount', prefstype=('user', 'ui'))




    def OnEndMaximize(self, *args):
        self.LoadAllMessages()



    def _OnClose(self, *args):
        self.timer = None



    def LoadAllMessages(self):
        showmsgs = []
        maxlog = settings.user.ui.Get('logmessageamount', 100)
        messages = sm.GetService('logger').GetMessages()
        t = len(messages)
        r = min(maxlog, t)
        for _i in xrange(r):
            i = t - 1 - _i
            (text, msgtext, msgtype,) = messages[i]
            if not self.ShowMessage(msgtype):
                continue
            entry = listentry.Get('Text', {'text': text,
             'canOpen': localization.GetByLabel('UI/Accessories/Log/LogMessage'),
             'line': 1})
            showmsgs.append(entry)

        self.sr.scroll.Load(contentList=showmsgs, headers=[localization.GetByLabel('UI/Common/DateWords/Time'), localization.GetByLabel('UI/Accessories/Log/Type'), localization.GetByLabel('UI/Accessories/Log/Message')])



    def ShowMessage(self, msgtype):
        return settings.user.ui.Get('show%slogmessages' % msgtype, 1)




