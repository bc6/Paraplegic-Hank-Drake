#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/util/uiEventListener.py
import uiconst
import blue
import uiutil
import util
import uicls
import math
import uthread
import form
import trinity
import const

class wmConst:
    __guid__ = 'const.wm'
    WM_NULL = 0
    WM_CREATE = 1
    WM_DESTROY = 2
    WM_MOVE = 3
    WM_SIZE = 5
    WM_ACTIVATE = 6
    WM_SETFOCUS = 7
    WM_KILLFOCUS = 8
    WM_ENABLE = 10
    WM_SETREDRAW = 11
    WM_SETTEXT = 12
    WM_GETTEXT = 13
    WM_GETTEXTLENGTH = 14
    WM_PAINT = 15
    WM_CLOSE = 16
    WM_QUERYENDSESSION = 17
    WM_QUIT = 18
    WM_QUERYOPEN = 19
    WM_ERASEBKGND = 20
    WM_SYSCOLORCHANGE = 21
    WM_ENDSESSION = 22
    WM_SYSTEMERROR = 23
    WM_SHOWWINDOW = 24
    WM_CTLCOLOR = 25
    WM_WININICHANGE = 26
    WM_SETTINGCHANGE = 26
    WM_DEVMODECHANGE = 27
    WM_ACTIVATEAPP = 28
    WM_FONTCHANGE = 29
    WM_TIMECHANGE = 30
    WM_CANCELMODE = 31
    WM_SETCURSOR = 32
    WM_MOUSEACTIVATE = 33
    WM_CHILDACTIVATE = 34
    WM_QUEUESYNC = 35
    WM_GETMINMAXINFO = 36
    WM_PAINTICON = 38
    WM_ICONERASEBKGND = 39
    WM_NEXTDLGCTL = 40
    WM_SPOOLERSTATUS = 42
    WM_DRAWITEM = 43
    WM_MEASUREITEM = 44
    WM_DELETEITEM = 45
    WM_VKEYTOITEM = 46
    WM_CHARTOITEM = 47
    WM_SETFONT = 48
    WM_GETFONT = 49
    WM_SETHOTKEY = 50
    WM_GETHOTKEY = 51
    WM_QUERYDRAGICON = 55
    WM_COMPAREITEM = 57
    WM_COMPACTING = 65
    WM_WINDOWPOSCHANGING = 70
    WM_WINDOWPOSCHANGED = 71
    WM_POWER = 72
    WM_COPYDATA = 74
    WM_CANCELJOURNAL = 75
    WM_NOTIFY = 78
    WM_INPUTLANGCHANGEREQUEST = 80
    WM_INPUTLANGCHANGE = 81
    WM_TCARD = 82
    WM_HELP = 83
    WM_USERCHANGED = 84
    WM_NOTIFYFORMAT = 85
    WM_CONTEXTMENU = 123
    WM_STYLECHANGING = 124
    WM_STYLECHANGED = 125
    WM_DISPLAYCHANGE = 126
    WM_GETICON = 127
    WM_SETICON = 128
    WM_NCCREATE = 129
    WM_NCDESTROY = 130
    WM_NCCALCSIZE = 131
    WM_NCHITTEST = 132
    WM_NCPAINT = 133
    WM_NCACTIVATE = 134
    WM_GETDLGCODE = 135
    WM_NCMOUSEMOVE = 160
    WM_NCLBUTTONDOWN = 161
    WM_NCLBUTTONUP = 162
    WM_NCLBUTTONDBLCLK = 163
    WM_NCRBUTTONDOWN = 164
    WM_NCRBUTTONUP = 165
    WM_NCRBUTTONDBLCLK = 166
    WM_NCMBUTTONDOWN = 167
    WM_NCMBUTTONUP = 168
    WM_NCMBUTTONDBLCLK = 169
    WM_KEYFIRST = 256
    WM_KEYDOWN = 256
    WM_KEYUP = 257
    WM_CHAR = 258
    WM_DEADCHAR = 259
    WM_SYSKEYDOWN = 260
    WM_SYSKEYUP = 261
    WM_SYSCHAR = 262
    WM_SYSDEADCHAR = 263
    WM_KEYLAST = 264
    WM_IME_STARTCOMPOSITION = 269
    WM_IME_ENDCOMPOSITION = 270
    WM_IME_COMPOSITION = 271
    WM_IME_KEYLAST = 271
    WM_INITDIALOG = 272
    WM_COMMAND = 273
    WM_SYSCOMMAND = 274
    WM_TIMER = 275
    WM_HSCROLL = 276
    WM_VSCROLL = 277
    WM_INITMENU = 278
    WM_INITMENUPOPUP = 279
    WM_MENUSELECT = 287
    WM_MENUCHAR = 288
    WM_ENTERIDLE = 289
    WM_CTLCOLORMSGBOX = 306
    WM_CTLCOLOREDIT = 307
    WM_CTLCOLORLISTBOX = 308
    WM_CTLCOLORBTN = 309
    WM_CTLCOLORDLG = 310
    WM_CTLCOLORSCROLLBAR = 311
    WM_CTLCOLORSTATIC = 312
    WM_MOUSEFIRST = 512
    WM_MOUSEMOVE = 512
    WM_LBUTTONDOWN = 513
    WM_LBUTTONUP = 514
    WM_LBUTTONDBLCLK = 515
    WM_RBUTTONDOWN = 516
    WM_RBUTTONUP = 517
    WM_RBUTTONDBLCLK = 518
    WM_MBUTTONDOWN = 519
    WM_MBUTTONUP = 520
    WM_MBUTTONDBLCLK = 521
    WM_MOUSEWHEEL = 522
    WM_MOUSEHWHEEL = 526
    WM_PARENTNOTIFY = 528
    WM_ENTERMENULOOP = 529
    WM_EXITMENULOOP = 530
    WM_NEXTMENU = 531
    WM_SIZING = 532
    WM_CAPTURECHANGED = 533
    WM_MOVING = 534
    WM_POWERBROADCAST = 536
    WM_DEVICECHANGE = 537
    WM_MDICREATE = 544
    WM_MDIDESTROY = 545
    WM_MDIACTIVATE = 546
    WM_MDIRESTORE = 547
    WM_MDINEXT = 548
    WM_MDIMAXIMIZE = 549
    WM_MDITILE = 550
    WM_MDICASCADE = 551
    WM_MDIICONARRANGE = 552
    WM_MDIGETACTIVE = 553
    WM_MDISETMENU = 560
    WM_ENTERSIZEMOVE = 561
    WM_EXITSIZEMOVE = 562
    WM_DROPFILES = 563
    WM_MDIREFRESHMENU = 564
    WM_IME_SETCONTEXT = 641
    WM_IME_NOTIFY = 642
    WM_IME_CONTROL = 643
    WM_IME_COMPOSITIONFULL = 644
    WM_IME_SELECT = 645
    WM_IME_CHAR = 646
    WM_IME_KEYDOWN = 656
    WM_IME_KEYUP = 657
    WM_MOUSEHOVER = 673
    WM_NCMOUSELEAVE = 674
    WM_MOUSELEAVE = 675
    WM_CUT = 768
    WM_COPY = 769
    WM_PASTE = 770
    WM_CLEAR = 771
    WM_UNDO = 772
    WM_RENDERFORMAT = 773
    WM_RENDERALLFORMATS = 774
    WM_DESTROYCLIPBOARD = 775
    WM_DRAWCLIPBOARD = 776
    WM_PAINTCLIPBOARD = 777
    WM_VSCROLLCLIPBOARD = 778
    WM_SIZECLIPBOARD = 779
    WM_ASKCBFORMATNAME = 780
    WM_CHANGECBCHAIN = 781
    WM_HSCROLLCLIPBOARD = 782
    WM_QUERYNEWPALETTE = 783
    WM_PALETTEISCHANGING = 784
    WM_PALETTECHANGED = 785
    WM_HOTKEY = 786
    WM_PRINT = 791
    WM_PRINTCLIENT = 792
    WM_HANDHELDFIRST = 856
    WM_HANDHELDLAST = 863
    WM_PENWINFIRST = 896
    WM_PENWINLAST = 911
    WM_COALESCE_FIRST = 912
    WM_COALESCE_LAST = 927
    WM_DDE_FIRST = 992
    WM_DDE_INITIATE = 992
    WM_DDE_TERMINATE = 993
    WM_DDE_ADVISE = 994
    WM_DDE_UNADVISE = 995
    WM_DDE_ACK = 996
    WM_DDE_DATA = 997
    WM_DDE_REQUEST = 998
    WM_DDE_POKE = 999
    WM_DDE_EXECUTE = 1000
    WM_DDE_LAST = 1000
    WM_USER = 1024
    WM_APP = 32768
    WM_XBUTTONDOWN = 523
    WM_XBUTTONUP = 524
    MK_CONTROL = 8
    MK_LBUTTON = 1
    MK_MBUTTON = 16
    MK_RBUTTON = 2
    MK_SHIFT = 4
    MK_XBUTTON1 = 32
    MK_XBUTTON2 = 64
    XBUTTON1 = 1
    XBUTTON2 = 2

    def __init__(self):
        self.messageNamesByID = dict([ [v, k] for k, v in wmConst.__dict__.items() ])

    def GetMSGName(self, msgID):
        return self.messageNamesByID.get(msgID, None)


class UIEventListener(uicls.Window):
    __guid__ = 'form.UIEventListener'
    default_windowID = 'UIEventListener'
    default_width = 450
    default_height = 300
    default_topParentHeight = 0
    default_minSize = (default_width, default_height)
    default_caption = 'UI Event Listener'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.tabs = uicls.TabGroup(parent=self.sr.maincontainer)
        import uiEventListener
        self.windowsEventPanel = uiEventListener.WindowsEventPanel(parent=self.sr.maincontainer)
        self.uiEventPanel = uiEventListener.UIEventPanel(parent=self.sr.maincontainer)
        self.uiGlobalEventPanel = uiEventListener.UIGlobalEventPanel(parent=self.sr.maincontainer)
        self.shortcutPanel = uiEventListener.UIShortcutPanel(parent=self.sr.maincontainer)
        self.helpPanel = uiEventListener.HelpPanel(parent=self.sr.maincontainer)
        tabs = (util.KeyVal(name='windowsEvents', label='Windows events', panel=self.windowsEventPanel),
         util.KeyVal(name='uiEvents', label='UI events', panel=self.uiEventPanel),
         util.KeyVal(name='uiGlobalEvents', label='UI global events', panel=self.uiGlobalEventPanel),
         util.KeyVal(name='shortcuts', label='Shortcuts', panel=self.shortcutPanel),
         util.KeyVal(name='help', label='Help', panel=self.helpPanel))
        self.tabs.LoadTabs(tabs)


class BaseEventPanel(uicls.Container):
    __guid__ = 'uiEventListener.BaseEventPanel'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.events = []
        self.settingsName = self.__guid__.split('.')[1] + 'ignoreEvents'
        settings.user.ui.Set(self.settingsName, self.default_ignoreEvents)
        self.ignoreEvents = settings.user.ui.Get(self.settingsName, self.default_ignoreEvents)
        self.updatePending = False
        self.showMax = 100
        self.scrollUpdateRequested = False
        self.isPaused = False
        self.rightCont = uicls.Container(name='rightCont', parent=self, align=uiconst.TORIGHT, width=150, padding=3)
        uicls.Label(parent=self.rightCont, align=uiconst.TOTOP, text='<color=red>IGNORE LIST</color>')
        uicls.Label(parent=self.rightCont, align=uiconst.TOBOTTOM, text='Right-click logged entries to add that event type to ignore')
        self.ignoreScroll = uicls.Scroll(parent=self.rightCont, align=uiconst.TOALL)
        self._UpdateIgnoreScroll()
        btns = (('Clear', self.ResetEventData, ()), ('<color=green>Pause logging</color>', self.PauseResumeLogging, ()))
        btnGroup = uicls.ButtonGroup(parent=self, btns=btns)
        self.pauseResumeBtn = btnGroup.GetBtnByIdx(1)
        self.scroll = uicls.Scroll(parent=self, align=uiconst.TOALL, padding=3)
        uthread.new(self._UpdateScrollThread)

    def OnTabSelect(self):
        self.UpdateScroll()

    def ResetEventData(self):
        self.events = []
        self.scroll.Clear()

    def PauseResumeLogging(self):
        self.isPaused = not self.isPaused
        if self.isPaused:
            label = '<color=yellow>Resume logging</color>'
        else:
            label = '<color=green>Pause logging</color>'
        self.pauseResumeBtn.SetLabel(label)

    def AddEvent(self, **kw):
        time = self._GetTimestampText()
        event = util.KeyVal(**kw)
        if event.id not in self.ignoreEvents:
            self.events.insert(0, (time, event))
            self.UpdateScroll()

    def UpdateScroll(self):
        if not self.display:
            return
        self.scrollUpdateRequested = True

    def _UpdateScrollThread(self):
        updateDelay = 200
        while not self.destroyed:
            if self.scrollUpdateRequested:
                self._UpdateScroll()
                self.scrollUpdateRequested = False
                blue.synchro.SleepWallclock(updateDelay)
            else:
                blue.synchro.Yield()

    def _UpdateScroll(self):
        if self.isPaused:
            return
        wndAbove = uiutil.GetWindowAbove(uicore.uilib.mouseOver)
        if isinstance(wndAbove, form.UIEventListener) and uicore.uilib.rightbtn:
            return
        scrolllist = []
        lastTime = None
        for time, event in self.events[:self.showMax]:
            if lastTime == time:
                time = ''
            else:
                lastTime = time
            label = time + '<t>' + self.GetScrollLabel(event)
            scrolllist.append(uicls.ScrollEntryNode(decoClass=uicls.SE_Generic, label=label, fontsize=14, event=event, OnGetMenu=self.GetScrollEntryMenu))

        self.scroll.Load(contentList=scrolllist, headers=self.SCROLL_HEADERS, ignoreSort=True)

    def GetScrollEntryMenu(self, entry):
        return (('Add to ignore', self.AddEventToIgnore, (entry,)),)

    def _UpdateIgnoreScroll(self):
        scrolllist = []
        for id, name in self.ignoreEvents.iteritems():
            scrolllist.append(uicls.ScrollEntryNode(decoClass=uicls.SE_Generic, label=name, id=id, fontsize=14, OnMouseDown=self.RemoveEventFromIgnore))

        self.ignoreScroll.Load(contentList=scrolllist)

    def AddEventToIgnore(self, entry):
        event = entry.sr.node.event
        self.ignoreEvents[event.id] = event.name
        settings.user.ui.Set(self.settingsName, self.ignoreEvents)
        self._UpdateIgnoreScroll()

    def RemoveEventFromIgnore(self, entry):
        node = entry.sr.node
        if node.id in self.ignoreEvents:
            self.ignoreEvents.pop(node.id)
            settings.user.ui.Set(self.settingsName, self.ignoreEvents)
        self._UpdateIgnoreScroll()

    def _GetTimestampText(self):
        year, month, weekday, day, hour, minute, second, msec = blue.os.GetTimeParts(blue.os.GetWallclockTime())
        return '%02i:%02i:%02i.%03i' % (hour,
         minute,
         second,
         msec)


class WindowsEventPanel(BaseEventPanel):
    __guid__ = 'uiEventListener.WindowsEventPanel'
    SCROLL_HEADERS = ['time',
     'msgID',
     'wParam',
     'lParam',
     'details']
    default_ignoreEvents = {wmConst.WM_MOUSEMOVE: 'WM_MOUSEMOVE',
     wmConst.WM_NCHITTEST: 'WM_NCHITTEST',
     wmConst.WM_GETDLGCODE: 'WM_GETDLGCODE'}

    def ApplyAttributes(self, attributes):
        BaseEventPanel.ApplyAttributes(self, attributes)
        self.leftCont = uicls.Container(name='leftCont', parent=self, align=uiconst.TOLEFT, width=100)
        trinity.app.eventHandler = self.OnAppEvent

    def OnAppEvent(self, msgID, wParam, lParam):
        uicore.uilib.OnAppEvent(msgID, wParam, lParam)
        msgName = wmConst().GetMSGName(msgID)
        self.AddEvent(id=msgID, name=msgName, wParam=wParam, lParam=lParam)

    def _OnClose(self):
        trinity.app.eventHandler = uicore.uilib.OnAppEvent

    def GetScrollLabel(self, event):
        if event.name is None:
            event.name = '<color=red>%s</color>' % hex(event.id).upper()
        details = self.GetDetails(event.id, event.wParam, event.lParam)
        label = '%s<t>%s<t>%s<t>%s' % (event.name,
         hex(event.wParam).upper(),
         hex(event.lParam).upper(),
         details)
        return label

    def GetDetails(self, msgID, wParam, lParam):
        if msgID in (wmConst.WM_KEYDOWN,
         wmConst.WM_KEYUP,
         wmConst.WM_SYSKEYDOWN,
         wmConst.WM_SYSKEYUP):
            vk = uicore.cmd.GetKeyNameFromVK(wParam)
            if msgID == wmConst.WM_KEYDOWN:
                repeatCount = lParam & 65535
                if repeatCount > 1:
                    vk += ', repeatCount=%s' % repeatCount
            return vk
        if msgID == wmConst.WM_CHAR:
            return unichr(wParam)
        if msgID in (wmConst.WM_XBUTTONDOWN, wmConst.WM_XBUTTONUP):
            if wParam & 65536:
                return 'XBUTTON1'
            else:
                return 'XBUTTON2'
        return '-'


class UIEventPanel(BaseEventPanel):
    __guid__ = 'uiEventListener.UIEventPanel'
    SCROLL_HEADERS = ['time',
     'eventID',
     'object name',
     'object id',
     'class',
     'args',
     'param']
    default_ignoreEvents = {uiconst.UI_MOUSEENTER: 'OnMouseEnter',
     uiconst.UI_MOUSEEXIT: 'OnMouseExit',
     uiconst.UI_MOUSEHOVER: 'OnMouseHover',
     uiconst.UI_MOUSEMOVE: 'OnMouseMove'}

    def ApplyAttributes(self, attributes):
        BaseEventPanel.ApplyAttributes(self, attributes)
        self.realEventHandler = uicore.uilib._TryExecuteHandler
        uicore.uilib._TryExecuteHandler = self._TryExecuteHandler

    def _TryExecuteHandler(self, eventID, obj, eventArgs = None, param = None):
        handlerObj = self.realEventHandler(eventID, obj, eventArgs, param)
        if handlerObj:
            name = uicore.uilib.EVENTMAP[eventID]
            self.AddEvent(id=eventID, name=name, obj=obj, eventArgs=eventArgs, param=param)

    def _OnClose(self):
        uicore.uilib._TryExecuteHandler = self.realEventHandler

    def GetScrollLabel(self, event):
        return '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (event.name,
         event.obj.name,
         hex(id(event.obj)).upper(),
         event.obj.__guid__,
         event.eventArgs,
         event.param)


class UIGlobalEventPanel(BaseEventPanel):
    __guid__ = 'uiEventListener.UIGlobalEventPanel'
    SCROLL_HEADERS = ['time',
     'eventID',
     'called function',
     'winParams',
     'args',
     'kw']
    default_ignoreEvents = {}

    def ApplyAttributes(self, attributes):
        BaseEventPanel.ApplyAttributes(self, attributes)
        self.realEventHandler = uicore.uilib.CheckCallbacks
        uicore.uilib.CheckCallbacks = self.CheckCallbacks

    def CheckCallbacks(self, obj, msgID, param):
        callbackDict = uicore.uilib._triuiRegsByMsgID.get(msgID, {})
        for cookie, (wr, args, kw) in callbackDict.items():
            func = wr()
            name = uicore.uilib.EVENTMAP.get(msgID, '<color=red>%s</color>' % msgID)
            self.AddEvent(id=msgID, name=name, func=func, winParams=param, args=args, kw=kw)

        self.realEventHandler(obj, msgID, param)

    def _OnClose(self):
        uicore.uilib.CheckCallbacks = self.realEventHandler

    def GetScrollLabel(self, event):
        func = event.func
        if func:
            func = '%s.%s' % (func.im_class.__guid__, func.im_func.func_name)
        return '%s<t>%s<t>%s<t>%s<t>%s' % (event.name,
         func,
         event.winParams,
         event.args,
         event.kw)


class UIShortcutPanel(BaseEventPanel):
    __guid__ = 'uiEventListener.UIShortcutPanel'
    SCROLL_HEADERS = ['time', 'name']
    default_ignoreEvents = {}
    __notifyevents__ = ('OnCommandExecuted',)

    def ApplyAttributes(self, attributes):
        BaseEventPanel.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)

    def OnCommandExecuted(self, name):
        self.AddEvent(id=name, name=name)

    def GetScrollLabel(self, event):
        return event.name


class HelpPanel(uicls.Container):
    __guid__ = 'uiEventListener.HelpPanel'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        text = '\n<b>Windows events:</b> These are raw operating system events that are cought by trinity and forwarded to uicore.uilib (uilib.py) where they are processed and used to execute UI events, UI global events and shortcuts.\n\n<b>UI events:</b> UI events coming from uilib are handled by bound methods, defined in UI classes. To catch one of those events, simply define the appropriately named method within your class (OnClick for example). The meaning of the arguments passed on to the event handlers differ between events.    \n\n<b>UI global events:</b> In some cases it can be useful to listen to global events. For example, a container might be interested to know when the mouse is clicked, regardless of what is being clicked. This can be achieved by registering an event listener through uicore.uilib.RegisterForTriuiEvents\n\n<b>Shortcuts:</b> Shortcut key commands are handled in uicore.cmd (command.py and game specific file such as evecommands.py). \n'
        uicls.Label(parent=self, align=uiconst.TOALL, text=text, padding=10, fontsize=13)