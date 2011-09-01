import service
import blue
import uthread
import uix
import uiutil
import operator
import util
import base
import form
import listentry
import gc
import types
import sys
import slprofile
import pstats
import blue
import stackless
import trinity
import log
import uicls
import uiconst
from service import ROLE_IGB
import pychartdir as chart
chart.setLicenseCode('DIST-0000-05de-f7ec-ffbeURDT-232Q-M544-C2XM-BD6E-C452')
GRAPH_MEMORY = 1
GRAPH_PERFORMANCE = 2
GRAPH_HEAP = 3

class Monitor(service.Service):
    __exportedcalls__ = {'Show': [],
     'ShowOutstandingTab': [ROLE_IGB]}
    __dependencies__ = ['settings']
    __update_on_reload__ = 0
    __guid__ = 'svc.monitor'
    __servicename__ = 'monitor'
    __displayname__ = 'Monitor Service'

    def Run(self, memStream = None):
        self.LogInfo('Starting MonitorSvc')
        self.started = False



    def UpdateHeapHistory(self):
        heaps = blue.MemoryTrackerGetAllProcessHeapsSizes()
        for (i, h,) in enumerate(heaps):
            if i not in self.heaphistory:
                self.heaphistory[i] = []
            self.heaphistory[i].append((blue.os.GetTime(), h))




    def Stop(self, memStream = None):
        if self.started:
            self.CleanUp()



    def Show(self):
        if not self.started:
            self.started = True
            self.CleanUp()
            self.ResetCounters()
            self.tabs = None
            self.numModels = 0
            self.heaphistory = {}
            if prefs.GetValue('heapinfo', 0):
                self.heaphistorytimer = base.AutoTimer(1000, self.UpdateHeapHistory)
        wnd = self.GetWnd(1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()
            self.uitimer = base.AutoTimer(100, self.UpdateUI)
            self.modeltimer = base.AutoTimer(1000, self.UpdateNumModels)
            self.graphtimer = base.AutoTimer(20000, self.UpdateGraph)
            self.heapgraphtimer = base.AutoTimer(20000, self.UpdateHeapGraph)
        wnd.sr.updateTimer = None



    def ShowOutstandingTab(self):
        self.Show()
        blue.pyos.synchro.Sleep(500)
        tabName = 'Outstanding_tab'
        tab = self.tabs.sr.Get(tabName)
        tab.Select(1)



    def _OnResize(self, *args):
        if self.tabs and self.tabs.GetSelectedArgs() in ('memory', 'performance', 'heap'):
            self.GetWnd().sr.updateTimer = base.AutoTimer(500, self.UpdateSize)



    def GetGraphMenu(self, *args):
        MEMORY_FILTERS = {'total_memory': 'Total Memory',
         'python_memory': 'Python Memory',
         'blue_memory': 'Blue Memory',
         'other_memory': 'Other Memory',
         'working_set': 'Working Set'}
        PERFORMANCE_FILTERS = {'fps': 'FPS',
         'thread_cpu': 'Thread CPU'}
        if self.GetGraphType() == GRAPH_PERFORMANCE:
            filters = PERFORMANCE_FILTERS
        elif self.GetGraphType() == GRAPH_MEMORY:
            filters = MEMORY_FILTERS
        else:
            return []
        m = []
        for (name, label,) in filters.iteritems():
            m.append(('%s %s' % (['Show', 'Hide'][settings.user.ui.Get('monitor_setting_' + name, 1)], label), self.ToggleMemory, (name,)))

        m.append(None)
        m.append(('Time', self.MemoryTimeMenu()))
        return m



    def GetHeapGraphMenu(self, *args):
        m = []
        for (k, v,) in self.heaphistory.iteritems():
            m.append(('%s %s' % (['Show', 'Hide'][settings.user.ui.Get('monitor_setting_heap_%s' % k, 1)], 'Heap #%s' % k), self.ToggleHeap, (k,)))

        m.append(None)
        return m



    def ToggleHeap(self, name):
        name = 'monitor_setting_heap_%s' % name
        curr = settings.user.ui.Get(name, 1)
        settings.user.ui.Set(name, not curr)
        uthread.new(self.GetHeapGraph)



    def ToggleMemory(self, name):
        name = 'monitor_setting_' + name
        curr = settings.user.ui.Get(name, 1)
        settings.user.ui.Set(name, not curr)
        uthread.new(self.GetGraph)



    def MemoryTimeMenu(self):
        m = []
        for i in [5,
         10,
         30,
         60,
         120,
         9999]:
            m.append(('last %s minutes' % i if i < 9999 else 'Since counter started', self.SetMemoryTime, (i,)))

        return m



    def SetMemoryTime(self, n):
        settings.user.ui.Set('monitor_setting_memory_time', n)
        uthread.new(self.GetGraph)



    def UpdateGraph(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed and self.tabs and hasattr(self.tabs, 'GetSelectedArgs') and self.tabs.GetSelectedArgs() in ('memory', 'performance'):
            self.LogInfo('Updating memory graph')
            self.GetGraph()



    def UpdateHeapGraph(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed and self.tabs and hasattr(self.tabs, 'GetSelectedArgs') and self.tabs.GetSelectedArgs() in ('heap',):
            self.LogInfo('Updating heap graph')
            self.GetHeapGraph()



    def UpdateSize(self):
        uthread.new(self.GetGraph)
        uthread.new(self.GetHeapGraph)
        self.GetWnd(1).sr.updateTimer = None



    def CleanUp(self):
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            wnd.CloseX()
        self.timer = None
        self.uitimer = None
        self.modeltimer = None
        self.graphtimer = None
        self.laststats = {}
        self.maxPeaks = {}
        self.lastresetstats = {}
        self.lastVM = None
        self.lastVMDelta = 0
        self.totalVMDelta = 0
        self.statsdiffs = {}
        self.showing = None
        self.settingsinited = 0
        self.pythonProfile = None



    def GetWnd(self, new = 0):
        wnd = uicore.registry.GetWindow('MonitorWnd')
        if wnd is None and new:
            wnd = uicls.MonitorWnd(parent=uicore.layer.main)
            wnd.OnClose = self.CloseWnd
            wnd._OnResize = self._OnResize
            if hasattr(wnd, 'SetTopparentHeight'):
                wnd.SetTopparentHeight(0)
            main = wnd.sr.maincontainer
            topcontainer = uicls.Container(name='push', parent=main, align=uiconst.TOTOP, height=46, clipChildren=1)
            if eve.session.role & (service.ROLE_QA | service.ROLE_PROGRAMMER) or not blue.pyos.packaged:
                w = wnd.sr.telemetryButton = uicls.Button(parent=topcontainer, label='Telemetry', align=uiconst.TOPRIGHT, autowidth=1, autoheight=1, func=self.RunTelemetry)
            w = wnd.sr.fpsText = uicls.Label(text='', parent=topcontainer, align=uiconst.TOPLEFT, top=0, left=8, autowidth=1, autoheight=1)
            w = wnd.sr.vmText = uicls.Label(text='', parent=topcontainer, align=uiconst.TOPLEFT, top=14, left=8, autowidth=1, autoheight=1)
            w = wnd.sr.cacheText = uicls.Label(text='', parent=topcontainer, align=uiconst.TOPLEFT, top=28, left=8, autowidth=1, autoheight=1)
            self.tabs = maintabs = uicls.TabGroup(parent=main)
            wnd.sr.scroll = uicls.Scroll(parent=main, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            wnd.sr.scroll.sr.id = 'monitorscroll'
            textonly = uicls.Container(name='textonly', parent=main, clipChildren=1, pos=(8, 8, 8, 8))
            graph = wnd.sr.graph = uicls.Container(name='graph', parent=main, clipChildren=1, pos=(8, 8, 8, 8))
            txt = uicls.Label(text='', parent=textonly, align=uiconst.TOALL, tabs=[80,
             120,
             160,
             200,
             240,
             280], state=uiconst.UI_DISABLED, autowidth=False, autoheight=False)
            wnd.sr.statustext = txt
            wnd.sr.settings = uicls.Container(name='settings', parent=main, clipChildren=1, pos=(8, 8, 8, 8))
            w = wnd.sr.cursorText = uicls.Label(text='', parent=wnd.sr.settings, align=uiconst.TOTOP, autowidth=1, autoheight=1)
            w = wnd.sr.faText = uicls.Label(text='', parent=wnd.sr.settings, align=uiconst.TOTOP, autowidth=1, autoheight=1)
            w = wnd.sr.moText = uicls.Label(text='', parent=wnd.sr.settings, align=uiconst.TOTOP, autowidth=1, autoheight=1)
            w = wnd.sr.queueText = uicls.Label(text='', parent=wnd.sr.settings, align=uiconst.TOTOP, autowidth=1, autoheight=1)
            wnd.sr.settingsInner = uicls.Container(name='settingsInner', parent=wnd.sr.settings, align=uiconst.TOALL)
            tabs = [['Main',
              wnd.sr.settings,
              self,
              'settings'],
             ['Network',
              textonly,
              self,
              'network'],
             ['Rot',
              wnd.sr.scroll,
              self,
              'rot'],
             ['Timers',
              wnd.sr.scroll,
              self,
              'timers'],
             ['Objects',
              wnd.sr.scroll,
              self,
              'objects'],
             ['Memory',
              graph,
              self,
              'memory'],
             ['Performance',
              graph,
              self,
              'performance'],
             ['Outstanding',
              wnd.sr.scroll,
              self,
              'outstanding']]
            if prefs.GetValue('heapinfo', 0):
                tabs.append(['Heap',
                 graph,
                 self,
                 'heap'])
            if session.role & service.ROLEMASK_ELEVATEDPLAYER:
                tabs.extend([['Logs',
                  wnd.sr.scroll,
                  self,
                  'logs']])
            self.tabs.Startup(tabs, 'monitortabs')
            bottomCont = uicls.Container(parent=main, align=uiconst.TOBOTTOM, height=24, idx=0)
            wnd.sr.resetWnd = uicls.Container(name='resetwnd', parent=bottomCont, align=uiconst.TOTOP, height=24, idx=0)
            wnd.sr.logWnd = uicls.Container(name='logwnd', parent=bottomCont, align=uiconst.TOTOP, height=24, idx=0)
            btns = uicls.ButtonGroup(btns=[['Start',
              self.StartLogInMemory,
              (),
              51],
             ['Stop',
              self.StopLogInMemory,
              (),
              51],
             ['Clear',
              self.ClearLogInMemory,
              (),
              51],
             ['Config',
              self.ConfigLogInMemory,
              (),
              51],
             ['Refresh',
              self.RefreshLogInMemory,
              (),
              51],
             ['Attach',
              self.AttachToLogServer,
              (),
              51]])
            wnd.sr.logWnd.children.insert(0, btns)
            uicls.Line(parent=wnd.sr.resetWnd, align=uiconst.TOTOP)
            uicls.Button(parent=wnd.sr.resetWnd, label='Reset', align=uiconst.CENTER, func=self.Reset)
            wnd.SetMinSize([400, 300])
            wnd.Maximize(1)
            uiutil.Transplant(wnd, uicore.layer.abovemain)
        return wnd



    def Load(self, args):
        wnd = self.GetWnd()
        if wnd:
            wnd.sr.logWnd.state = uiconst.UI_HIDDEN
            wnd.sr.resetWnd.state = uiconst.UI_HIDDEN
            self.timer = None
            if args == 'objects':
                wnd.sr.resetWnd.state = uiconst.UI_NORMAL
                self.GetObjects()
            elif args in ('memory', 'performance'):
                blue.pyos.synchro.Sleep(100)
                self.GetGraph()
            elif args in ('heap',):
                self.GetHeapGraph()
            elif args == 'network':
                wnd.sr.resetWnd.state = uiconst.UI_NORMAL
                self.UpdateData()
                self.timer = base.AutoTimer(1000, self.UpdateData)
            elif args == 'rot':
                wnd.sr.resetWnd.state = uiconst.UI_NORMAL
                self.UpdateROT(force=True)
                self.timer = base.AutoTimer(1000, self.UpdateROT)
            elif args == 'settings':
                if not self.settingsinited:
                    self.LoadSettings()
                    self.settingsinited = 1
            elif args == 'timers':
                wnd.sr.resetWnd.state = uiconst.UI_NORMAL
                self.UpdateTimers()
                self.timer = base.AutoTimer(2500, self.UpdateTimers)
            elif args == 'outstanding':
                self.UpdateOutstanding()
                self.timer = base.AutoTimer(10, self.UpdateOutstanding)
            elif args == 'logs':
                self.ShowLogs()
            self.showing = args



    def ShowLogs(self):
        wnd = self.GetWnd()
        if wnd:
            wnd.sr.logWnd.state = uiconst.UI_NORMAL
            wnd.sr.scroll.Load(contentList=[])
            self.UpdateLogs()



    def LoadSettings(self):
        wnd = self.GetWnd()
        uicls.Label(text='<br><b>Debug Settings</b> (changing these settings is <b>not</b> recommended):', parent=wnd.sr.settingsInner, align=uiconst.TOTOP, autowidth=1, autoheight=1)
        if wnd:
            for (cfgname, value, label, checked, group,) in [['userotcache',
              None,
              'Enable rot cache',
              settings.public.generic.Get('userotcache', 1),
              None],
             ['lazyLoading',
              None,
              'Enable Lazy model loading',
              settings.public.generic.Get('lazyLoading', 1),
              None],
             ['preload',
              None,
              'Enable Preloading',
              settings.public.generic.Get('preload', 1),
              None],
             ['asyncLoad',
              None,
              'Enable Asyncronous Loading (change requires reboot)',
              settings.public.generic.Get('asyncLoad', 1),
              None],
             ['resourceUnloading',
              None,
              'Enable Resource Unloading',
              settings.public.generic.Get('resourceUnloading', 1),
              None]]:
                uicls.Checkbox(text=label, parent=wnd.sr.settingsInner, configName=cfgname, retval=value, checked=checked, groupname=group, callback=self.CheckBoxChange, prefstype=('generic',))




    def CheckBoxChange(self, checkbox):
        config = checkbox.data['config']
        if config == 'userotcache':
            blue.rot.cacheTimeout = 60 * settings.public.generic.Get('userotcache', 1)
        elif config == 'resourceUnloading':
            trinity.SetEveSpaceObjectResourceUnloadingEnabled(settings.public.generic.Get('resourceUnloading', 1))



    def RunTelemetry(self, *args):
        blue.synchro.Sleep(5000)
        blue.statistics.StartTelemetry('localhost')
        blue.synchro.Sleep(20000)
        blue.statistics.StopTelemetry()



    def Reset(self, *args):
        self.ResetCounters()
        self.lastresetstats = sm.GetService('machoNet').GetConnectionProperties()
        self.laststats = {}
        self.rotinited = 0
        self.lastVM = None
        self.lastVMDelta = 0
        self.totalVMDelta = 0
        self.maxPeaks = {}
        self.typeBag = {}



    def ResetCounters(self, *args):
        self.intvals = [5000,
         10000,
         15000,
         30000,
         60000]
        self.counter = [[],
         [],
         [],
         [],
         [],
         []]
        self.ticker = 0
        self.packets_outTotal = 0
        self.packets_inTotal = 0
        self.bytes_outTotal = 0
        self.bytes_inTotal = 0



    def UpdateROT(self, force = False):
        wnd = self.GetWnd()
        if wnd:
            try:
                rot = blue.rot.LiveCount()
                if not getattr(self, 'rotinited', 0) or force:
                    scrolllist = []
                    for (k, v,) in rot.iteritems():
                        scrolllist.append(listentry.Get('Generic', {'totalDelta': 0,
                         'typeName': k,
                         'peakValue': v,
                         'lastValue': v,
                         'label': '%s<t>%s<t>%s<t>%s' % (k,
                                   0,
                                   v,
                                   v)}))

                    wnd.sr.scroll.Load(contentList=scrolllist, headers=['type',
                     'delta',
                     'instances',
                     'peak'], fixedEntryHeight=18)
                    self.showing = 'rot'
                    self.rotinited = 1
                    return 
                for entry in wnd.sr.scroll.GetNodes():
                    v = rot[entry.typeName]
                    d = v - entry.lastValue
                    td = d + entry.totalDelta
                    entry.totalDelta = td
                    peak = self.maxPeaks.get(entry.typeName, -1)
                    p = max(peak, v)
                    self.maxPeaks[entry.typeName] = p
                    c = ['<color=0xff00ff00>', '<color=0xffff0000>'][(td > 0)]
                    entry.label = '%s<t>%s%s<color=0xffffffff><t>%s<t>%s' % (entry.typeName,
                     c,
                     td,
                     v,
                     p)
                    if entry.panel:
                        entry.panel.sr.label.text = entry.label
                    entry.lastValue = v

                wnd.sr.scroll.RefreshSort()
            except:
                self.timer = None
                sys.exc_clear()



    def UpdateNumModels(self):
        scene1 = sm.GetService('sceneManager').GetActiveScene1()
        scene2 = sm.GetService('sceneManager').GetActiveScene2()
        s2 = 0
        if scene2 is not None and hasattr(scene2, 'objects'):
            s2 = len(scene2.objects)
        s1 = 0
        if scene1 is not None:
            s1 = len(scene1.models)
        self.numModels = s1 + s2



    def UpdateUI(self):
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            return 
        (hd, li,) = blue.pyos.ProbeStuff()
        info = util.Row(list(hd), li)
        virtualMem = info.pagefileUsage / 1024
        if self.lastVM is None:
            self.lastVM = virtualMem
        delta = virtualMem - self.lastVM
        self.totalVMDelta += delta
        self.lastVM = virtualMem
        delta = delta or self.lastVMDelta
        self.lastVMDelta = delta
        dc = ['<color=0xff00ff00>', '<color=0xffff0000>'][(delta > 0)]
        tdc = ['<color=0xff00ff00>', '<color=0xffff0000>'][(self.totalVMDelta > 0)]
        try:
            dev = trinity.device
            fps = 'Fps: %.1f - Models: %d' % (blue.os.fps, self.numModels)
            if wnd.sr.fpsText.text != fps:
                wnd.sr.fpsText.text = fps
            vm = 'VM Size/D/TD: %sK / %s%sK<color=0xffffffff> / %s%sK' % (util.FmtAmt(virtualMem),
             dc,
             util.FmtAmt(delta),
             tdc,
             util.FmtAmt(self.totalVMDelta))
            if wnd.sr.vmText.text != vm:
                wnd.sr.vmText.text = vm
            inUse = util.FmtAmt(blue.motherLode.memUsage / 1024)
            total = util.FmtAmt(blue.motherLode.maxMemUsage / 1024)
            num = blue.motherLode.size()
            vm = 'Resource Cache Usage: %sK / %sK - %s objects' % (inUse, total, num)
            if wnd.sr.cacheText.text != vm:
                wnd.sr.cacheText.text = vm
            c = 'Cursor: %d, %d' % (uicore.uilib.x, uicore.uilib.y)
            if wnd.sr.cursorText.text != c:
                wnd.sr.cursorText.text = c
            fa = 'Focus/Active: %s/%s' % (getattr(uicore.registry.GetFocus(), 'name', 'None'), getattr(uicore.registry.GetActive(), 'name', 'None'))
            if wnd.sr.faText.text != fa:
                wnd.sr.faText.text = fa
            mo = 'MouseOver: %s' % self.GetTrace(uicore.uilib.mouseOver)
            if wnd.sr.moText.text != mo:
                wnd.sr.moText.text = mo
            spaceMgr = sm.StartService('space')
            mo = 'Lazy Queue: %s' % getattr(spaceMgr, 'lazyLoadQueueCount', 0)
            if session.role & service.ROLEMASK_ELEVATEDPLAYER:
                mo += ' - Preload Queue: %s' % getattr(spaceMgr, 'preloadQueueCount', 22)
            if wnd.sr.queueText.text != mo:
                wnd.sr.queueText.text = mo
        except Exception as e:
            print 'e',
            print e
            self.uitimer = None
            sys.exc_clear()



    def GetTrace(self, item):
        trace = ''
        while item.parent:
            trace = '/' + item.name + trace
            item = item.parent

        return trace



    def UpdateTimers(self):
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            return 
        scrolllist = []
        for timer in base.AutoTimer.autoTimers.iterkeys():
            label = str(timer.method)
            label = label[1:]
            label = label.split(' ')
            label = ' '.join(label[:3])
            scrolllist.append(listentry.Get('Generic', {'label': '%s<t>%s<t>%s' % (label, timer.interval, timer.run)}))

        wnd.sr.scroll.Load(contentList=scrolllist, headers=['method', 'interval', 'run'], fixedEntryHeight=18)



    def UpdateLogs(self):
        import blue
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            return 
        scrolllist = []
        entries = blue.logInMemory.GetEntries()
        for e in entries:
            s = {0: 'Info',
             1: 'Notice',
             2: 'Warning',
             3: 'Error'}.get(e[2], 'Unknown')
            label = '%s<t>%s::%s<t>%s<t>%s' % (util.FmtDate(e[3], 'nl'),
             e[0],
             e[1],
             s,
             e[4].replace('<', '&gt;'))
            scrolllist.append(listentry.Get('Generic', {'label': label}))

        scrolllist.sort()
        wnd.sr.scroll.Load(contentList=scrolllist, headers=['time',
         'channel',
         'severity',
         'message'], fixedEntryHeight=18)



    def StartLogInMemory(self):
        blue.logInMemory.Start()
        self.RefreshLogInMemory()



    def StopLogInMemory(self):
        blue.logInMemory.Stop()
        self.RefreshLogInMemory()



    def ClearLogInMemory(self):
        blue.logInMemory.Clear()
        self.RefreshLogInMemory()



    def RefreshLogInMemory(self):
        self.UpdateLogs()



    def ConfigLogInMemory(self, *args):
        format = []
        threshold = blue.logInMemory.threshold
        capacity = blue.logInMemory.capacity
        i = n = w = e = 0
        if threshold == 0:
            i = 1
        elif threshold == 1:
            n = 1
        elif threshold == 2:
            w = 1
        elif threshold == 3:
            e = 1
        format.append({'type': 'edit',
         'setvalue': '%s' % capacity,
         'key': 'capacity',
         'label': 'capacity',
         'required': 1,
         'maxlength': 5})
        format.append({'type': 'checkbox',
         'required': 1,
         'group': 'threshold',
         'height': 16,
         'setvalue': i,
         'key': 0,
         'label': '',
         'text': 'Info'})
        format.append({'type': 'checkbox',
         'required': 0,
         'group': 'threshold',
         'height': 16,
         'setvalue': n,
         'key': 1,
         'label': '',
         'text': 'Notice'})
        format.append({'type': 'checkbox',
         'required': 0,
         'group': 'threshold',
         'height': 16,
         'setvalue': w,
         'key': 2,
         'label': '',
         'text': 'Warning'})
        format.append({'type': 'checkbox',
         'required': 0,
         'group': 'threshold',
         'height': 16,
         'setvalue': e,
         'key': 3,
         'label': '',
         'text': 'Error'})
        retval = uix.HybridWnd(format, 'Configure In-memory Logging', 1, None, uiconst.OKCANCEL, minW=200, minH=80, unresizeAble=1, ignoreCurrent=0)
        if retval is None:
            return 
        threshold = retval['threshold']
        capacity = retval['capacity']
        blue.logInMemory.threshold = int(threshold)
        blue.logInMemory.capacity = int(capacity)



    def AttachToLogServer(self):
        blue.AttachToLogServer()
        uicore.Message('CustomInfo', {'info': 'Done attaching to Log Server.'})



    def UpdateOutstanding(self):
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            return 
        scrolllist = []
        for ct in base.outstandingCallTimers:
            method = ct[0]
            t = ct[1]
            label = '%s<t>%s<t>%s' % (method, util.FmtDate(t, 'nl'), util.FmtTime(blue.os.GetTime(1) - t))
            scrolllist.append(listentry.Get('Generic', {'label': label}))

        wnd.sr.scroll.Load(contentList=scrolllist, headers=['method', 'time', 'dt'], fixedEntryHeight=18)



    def UpdateData(self):
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            return 
        try:
            self.ticker += self.intvals[0]
            if self.ticker > self.intvals[-1]:
                self.ticker = self.intvals[0]
            stats = sm.GetService('machoNet').GetConnectionProperties()
            if self.laststats == {}:
                self.laststats = stats
            if self.lastresetstats != {}:
                for key in stats.iterkeys():
                    stats[key] = stats[key] - self.lastresetstats[key]

            props = [('Packets out', 'packets_out', 0),
             ('Packets in', 'packets_in', 0),
             ('Kilobytes out', 'bytes_out', 1),
             ('Kilobytes in', 'bytes_in', 1)]
            for i in xrange(len(self.counter) - 1):
                self.counter[i].append([ stats[key] - self.laststats[key] for (header, key, K,) in props ])
                self.counter[i] = self.counter[i][(-(self.intvals[i] / 1000)):]

            self.counter[-1].append([ stats[key] - self.laststats[key] for (header, key, K,) in props ])
            if wnd.state != uiconst.UI_NORMAL:
                self.laststats = stats
                return 
            statusstr = ''
            for tme in self.intvals:
                statusstr += '<t>%s' % util.FmtDate(long(tme * 10000), 'ss')

            statusstr += '<t>total<br>'
            valueIdx = 0
            for (header, key, K,) in props:
                statusstr += '%s' % header
                for intvals in self.counter:
                    value = reduce(operator.add, [ intval[valueIdx] for intval in intvals ], 0)
                    if not value:
                        statusstr += '<t>-'
                    else:
                        statusstr += '<t>%s' % [value, '%.1f' % (value / 1024.0)][K]

                statusstr += '<br>'
                valueIdx = valueIdx + 1

            statusstr += 'Outstanding<t>%s<br>' % (stats['calls_outstanding'],)
            statusstr += 'Blocking Calls<t>%s<br>' % stats['blocking_calls']
            block_time = stats['blocking_call_times']
            if block_time >= 0:
                secs = util.SecsFromBlueTimeDelta(block_time)
                statusstr += 'Blocking time<t>%sH<t>%sM<t>%sS<br>' % util.HoursMinsSecsFromSecs(secs)
            elif not hasattr(self, 'warnedBlockingTimeNegative'):
                self.warnedBlockingTimeNegative = True
                log.LogTraceback('Blocking time is negative?')
            wnd.sr.statustext.text = statusstr
            self.laststats = stats
        except:
            self.timer = None
            raise 



    def GetGraphType(self):
        if self.tabs and hasattr(self.tabs, 'GetSelectedArgs'):
            return {'memory': GRAPH_MEMORY,
             'performance': GRAPH_PERFORMANCE,
             'heap': GRAPH_HEAP}.get(self.tabs.GetSelectedArgs(), None)



    def GetObjects(self, num = 1000000, drill = None, textDrill = None, b = 0, e = 100):
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            return 
        dict = {}
        import weakref
        for object in gc.get_objects():
            tp = type(object)
            if not isinstance(object, weakref.ProxyType):
                try:
                    tp = object.__class__
                except AttributeError:
                    sys.exc_clear()
            dict[tp] = dict.get(tp, 0) + 1

        dict2 = {}
        for (k, v,) in dict.iteritems():
            n = k.__module__ + '.' + k.__name__
            dict2[n] = dict2.get(n, 0) + v

        scrolllist = []
        items = dict2.items()
        items.sort()
        for (tp, inst,) in items:
            scrolllist.append(listentry.Get('Generic', {'OnDblClick': self.ClickEntry,
             'instType': tp,
             'label': '%s<t>%s' % (tp, util.FmtAmt(inst))}))

        wnd.sr.scroll.Load(contentList=scrolllist, headers=['type', 'instances'], fixedEntryHeight=18)



    def GetHeapGraph(self):
        if self.GetGraphType() != GRAPH_HEAP:
            return 
        fontSize = 7.5
        fontFace = 'arial.ttc'
        wnd = self.GetWnd()
        uiutil.FlushList(wnd.sr.graph.children)
        (w, h,) = (wnd.sr.graph.absoluteRight - wnd.sr.graph.absoluteLeft, wnd.sr.graph.absoluteBottom - wnd.sr.graph.absoluteTop)
        width = w
        height = h
        c = chart.XYChart(width, height, bgColor=chart.Transparent)
        c.setColors(chart.whiteOnBlackPalette)
        c.setBackground(chart.Transparent)
        c.setTransparentColor(-1)
        c.setAntiAlias(1, 1)
        offsX = 60
        offsY = 17
        canvasWidth = width - 1 * offsX - 50
        canvasHeight = height - offsY * 2.5
        plotArea = c.setPlotArea(offsX, offsY, canvasWidth, canvasHeight, 1711276032, -1, -1, 5592405)
        import random
        c.addLegend(85, 18, 0, fontFace, fontSize).setBackground(chart.Transparent)
        random.seed(1001)
        for (k, lst,) in self.heaphistory.iteritems():
            name = 'monitor_setting_heap_%s' % k
            if not settings.user.ui.Get(name, 1):
                continue
            memData = []
            timeData = []
            for (t, n,) in lst:
                memData.append(n / 1024 / 1024)
                (year, month, wd, day, hour, minutes, sec, ms,) = util.GetTimeParts(t)
                timeData.append(chart.chartTime(year, month, day, hour, minutes, sec))

            lines = c.addLineLayer()
            l = (random.randint(0, 15), random.randint(0, 255), random.randint(0, 255))
            l = '0x%X%X%Xee' % (l[0], l[1], l[2])
            lines.addDataSet(memData, int(l, 16), '#%s' % k).setLineWidth(1)
            lines.setXData(timeData)

        c.xAxis().setDateScale3('{value|hh:nn}')
        leftAxis = c.yAxis()
        leftAxis.setTitle('Heap Size (MB)')
        buf = c.makeChart2(chart.PNG)
        surface = trinity.device.CreateOffscreenPlainSurface(w, h, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
        surface.LoadSurfaceFromFileInMemory(buf)
        linegr = uicls.Sprite(parent=wnd.sr.graph, align=uiconst.TOALL)
        linegr.GetMenu = self.GetHeapGraphMenu
        linegr.texture.atlasTexture = uicore.uilib.CreateTexture(width, height)
        linegr.texture.atlasTexture.CopyFromSurface(surface)



    def GetGraph(self):
        isPerf = False
        if self.GetGraphType() == GRAPH_PERFORMANCE:
            isPerf = True
        fontSize = 7.5
        fontFace = 'arial.ttc'
        wnd = self.GetWnd()
        uiutil.FlushList(wnd.sr.graph.children)
        (w, h,) = (wnd.sr.graph.absoluteRight - wnd.sr.graph.absoluteLeft, wnd.sr.graph.absoluteBottom - wnd.sr.graph.absoluteTop)
        minutes = settings.user.ui.Get('monitor_setting_memory_time', 60)
        trend = blue.pyos.cpuUsage[(-minutes * 60 / 10):]
        memCounters = {}
        perfCounters = {}
        mega = 1.0 / 1024.0 / 1024.0
        timeData = []
        memData = []
        pymemData = []
        bluememData = []
        othermemData = []
        workingsetData = []
        ppsData = []
        fpsData = []
        threadCpuData = []
        procCpuData = []
        lastT = lastpf = 0
        t1 = 0
        if len(trend) > 1:
            (t, cpu, mem, sched,) = trend[0]
            lastT = t
            lastpf = mem[-1]
            t1 = trend[0][0]
        benice = blue.pyos.BeNice
        for (t, cpu, mem, sched,) in trend:
            benice()
            elap = t - t1
            t1 = t
            (mem, pymem, workingset, pagefaults, bluemem,) = mem
            (fps, nr_1, ny, ns, dur, nr_2,) = sched
            fpsData.append(fps)
            memData.append(mem * mega)
            pymemData.append(pymem * mega)
            bluememData.append(bluemem * mega)
            othermem = (mem - pymem - bluemem) * mega
            if othermem < 0:
                othermem = 0
            othermemData.append(othermem)
            workingsetData.append(workingset * mega)
            (thread_u, proc_u,) = cpu
            if elap:
                thread_cpupct = thread_u / float(elap) * 100.0
                proc_cpupct = proc_u / float(elap) * 100.0
            else:
                thread_cpupct = proc_cpupct = 0.0
            threadCpuData.append(thread_cpupct)
            procCpuData.append(proc_cpupct)
            dt = t - lastT
            lastT = t
            pf = pagefaults - lastpf
            lastpf = pagefaults
            pps = pf / (dt * 1e-07) if dt else 0
            ppsData.append(pps)
            (year, month, wd, day, hour, minutes, sec, ms,) = util.GetTimeParts(t)
            timeData.append(chart.chartTime(year, month, day, hour, minutes, sec))

        if len(ppsData) > 1:
            ppsData[0] = ppsData[1]
        memCounters['blue_memory'] = (False,
         bluememData,
         3377390,
         1,
         False)
        memCounters['other_memory'] = (False,
         othermemData,
         16776960,
         1,
         False)
        memCounters['python_memory'] = (False,
         pymemData,
         65280,
         1,
         False)
        memCounters['total_memory'] = (False,
         memData,
         16711680,
         2,
         False)
        memCounters['working_set'] = (False,
         workingsetData,
         65535,
         1,
         False)
        memCounters['thread_cpu'] = (True,
         threadCpuData,
         6749952,
         1,
         True)
        memCounters['fps'] = (True,
         fpsData,
         16711680,
         1,
         False)
        width = w
        height = h
        c = chart.XYChart(width, height, bgColor=chart.Transparent)
        c.setColors(chart.whiteOnBlackPalette)
        c.setBackground(chart.Transparent)
        c.setTransparentColor(-1)
        c.setAntiAlias(1, 1)
        offsX = 60
        offsY = 17
        canvasWidth = width - 1 * offsX - 50
        canvasHeight = height - offsY * 2.5
        plotArea = c.setPlotArea(offsX, offsY, canvasWidth, canvasHeight, 1711276032, -1, -1, 5592405)
        c.addLegend(85, 18, 0, fontFace, fontSize).setBackground(chart.Transparent)
        if len(timeData) > 1:
            c.xAxis().setDateScale3('{value|hh:nn}')
        lines = c.addLineLayer()
        lines2 = c.addLineLayer2()
        lines2.setUseYAxis2()
        leftAxis = c.yAxis()
        rightAxis = c.yAxis2()
        if isPerf:
            leftAxis.setTitle('Frames per second')
            rightAxis.setTitle('CPU (%)')
        else:
            leftAxis.setTitle('Memory (MB)')
        for (i, k,) in enumerate(memCounters.keys()):
            if settings.user.ui.Get('monitor_setting_%s' % k, 1):
                title = k.replace('_', ' ').capitalize()
                if isPerf == memCounters[k][0]:
                    data = memCounters[k][1]
                    col = memCounters[k][2]
                    lineWidth = memCounters[k][3]
                    if not memCounters[k][4]:
                        l = lines
                    else:
                        l = lines2
                    l.addDataSet(data, col, title).setLineWidth(lineWidth)

        lines.setXData(timeData)
        lines2.setXData(timeData)
        if trend:
            pf = trend[-1][2][-1]
            label = 'Working set: %iMB, Virtual mem: %iMB, Page faults: %s' % (workingsetData[-1], memData[-1], util.FmtAmt(pf))
            c.addText(offsX, 2, label)
        buf = c.makeChart2(chart.PNG)
        surface = trinity.device.CreateOffscreenPlainSurface(w, h, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
        surface.LoadSurfaceFromFileInMemory(buf)
        linegr = uicls.Sprite(parent=wnd.sr.graph, align=uiconst.TOALL)
        linegr.GetMenu = self.GetGraphMenu
        linegr.texture.atlasTexture = uicore.uilib.CreateTexture(width, height)
        linegr.texture.atlasTexture.CopyFromSurface(surface)



    def ClickEntry(self, entry, *args):
        typeName = entry.sr.node.instType.__name__
        inst = gc.get_objects()
        alldict = {}
        for object in inst:
            s = type(object)
            alldict.setdefault(s, []).append(object)

        attrs = {'BlueWrapper': ['__typename__', '__guid__'],
         'instance': ['__class__', '__guid__'],
         'class': ['__guid__', '__class__', '__repr__']}
        attr = attrs.get(typeName, None)
        if attr is None:
            return 
        dict = {}
        for i in alldict[entry.sr.node.instType]:
            stringval = ''
            for a in attr:
                stringval += str(getattr(i, a, None))[:24] + '<t>'

            dict.setdefault(stringval, []).append(i)

        scrolllist = []
        for (tp, inst,) in dict.iteritems():
            if tp == 'None<t>' * len(attr):
                continue
            scrolllist.append(listentry.Get('Generic', {'label': '%s%s' % (tp, util.FmtAmt(len(inst)))}))

        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            return 
        wnd.wnd.sr.scroll.Load(contentList=scrolllist, headers=attr + ['instances'], fixedEntryHeight=18)



    def CloseWnd(self, *args):
        self.settingsinited = 0
        self.showing = None
        self.rotinited = 0
        self.uitimer = None
        self.modeltimer = None
        self.graphtimer = None
        self.timer = None
        self.lastVM = None
        self.lastVMDelta = 0
        self.totalVMDelta = 0




class MonitorWnd(uicls.Window):
    __guid__ = 'uicls.MonitorWnd'
    windowID = 'MonitorWnd'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.windowID = 'MonitorWnd'
        self.scope = 'all'
        self.SetCaption('Monitor')




