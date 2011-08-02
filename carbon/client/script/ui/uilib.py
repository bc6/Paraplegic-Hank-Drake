import uiconst
import uicls
import uiutil
import uthread
import blue
import base
import trinity
import log
import math
import util
import types
import weakref
import menu
import bluepy
from util import ResFile
DBLCLICKDELAY = 250.0
UTHREADEDEVENTS = (uiconst.UI_CLICK,
 uiconst.UI_DBLCLICK,
 uiconst.UI_TRIPLECLICK,
 uiconst.UI_KEYUP,
 uiconst.UI_KEYDOWN,
 uiconst.UI_MOUSEMOVE,
 uiconst.UI_MOUSEWHEEL)
EVENTMAP = {uiconst.UI_MOUSEHOVER: 'OnMouseHover',
 uiconst.UI_MOUSEMOVE: 'OnMouseMove',
 uiconst.UI_MOUSEENTER: 'OnMouseEnter',
 uiconst.UI_MOUSEEXIT: 'OnMouseExit',
 uiconst.UI_MOUSEDOWN: 'OnMouseDown',
 uiconst.UI_MOUSEUP: 'OnMouseUp',
 uiconst.UI_MOUSEWHEEL: 'OnMouseWheel',
 uiconst.UI_CLICK: 'OnClick',
 uiconst.UI_DBLCLICK: 'OnDblClick',
 uiconst.UI_TRIPLECLICK: 'OnTripleClick',
 uiconst.UI_KEYDOWN: 'OnKeyDown',
 uiconst.UI_KEYUP: 'OnKeyUp'}
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
CLICKCOUNTRESETTIME = 250
HOVERTIME = 250

class Uilib(object):
    __members__ = ['x',
     'y',
     'z',
     'dx',
     'dy',
     'dz',
     'rootObjects',
     'mouseOver',
     'renderJob',
     'desktop']
    __guid__ = 'uicls.Uilib'

    def __init__(self, paparazziMode = False):
        if len(trinity.textureAtlasMan.atlases) == 0:
            trinity.textureAtlasMan.AddAtlas(trinity.D3DFMT_A8R8G8B8, 2048, 1024)
        self.renderObjectToPyObjectDict = weakref.WeakValueDictionary()
        self.x = -1
        self.y = -1
        self.z = 0
        self.dx = 0
        self.dy = 0
        self.dz = 0
        self._mouseOver = None
        self._capturingMouseItem = None
        self._clickItem = None
        self.exclusiveMouseFocusActive = False
        self.appfocusitem = None
        self.selectedCursorType = uiconst.UICURSOR_DEFAULT
        self._clickTime = None
        self._clickCount = 0
        self._clickTimer = None
        self._clickPosition = None
        self.rootObjects = []
        self.rootObjectsByName = {}
        self._triuiRegs = {}
        self._triuiRegsByMsgID = {}
        self._mouseButtonStates = {}
        self._mouseDownPosition = {}
        self._unresolvedKeyDown = None
        self._lastKeyDown = None
        self._charsThatCanBlock = set()
        self._appfocusitem = None
        self._modkeysOff = tuple([ 0 for x in uiconst.MODKEYS ])
        self._expandMenu = None
        self._pickProjection = trinity.TriProjection()
        self._pickView = trinity.TriView()
        self._pickViewport = trinity.TriViewport()
        self.cursorCache = {}
        self.alignIslands = []
        uicore.uilib = self
        if not paparazziMode:
            self.inSceneRenderJob = trinity.CreateRenderJob()
            self.inSceneRenderJob.name = 'In-scene UI'
            self.inSceneRenderJob.ScheduleRecurring(insertFront=True)
            self.renderJob = trinity.CreateRenderJob()
            self.renderJob.name = 'UI'
            self.sceneViewStep = self.renderJob.SetView()
            self.sceneProjectionStep = self.renderJob.SetProjection()
            videoJobStep = self.renderJob.RunJob()
            videoJobStep.name = 'Videos'
            self.videoJob = trinity.CreateRenderJob()
            self.videoJob.name = 'Update videos job'
            videoJobStep.job = self.videoJob
            self.bracketCurveSet = trinity.TriCurveSet()
            self.bracketCurveSet.Play()
            self.renderJob.Update(self.bracketCurveSet).name = 'Update brackets'
            self.renderJob.PythonCB(self.Update).name = 'Update uilib'
            isFpsEnabled = trinity.IsFpsEnabled()
            if isFpsEnabled:
                trinity.SetFpsEnabled(False)
            self.renderJob.ScheduleRecurring()
            if isFpsEnabled:
                trinity.SetFpsEnabled(True)
            self.desktop = self.CreateRootObject('Desktop', isFullscreen=True)
            trinity.app.eventHandler = self.OnAppEvent
        trinity.device.RegisterResource(self)
        self._hoverThread = None



    def __del__(self, *args):
        trinity.app.eventHandler = None
        if self.renderJob:
            self.renderJob.UnscheduleRecurring()



    def OnInvalidate(self, *args):
        self.cursorCache = {}



    def OnCreate(self, *args):
        pass



    def CreateTexture(self, width, height):
        tex = trinity.textureAtlasMan.atlases[0].CreateTexture(int(width), int(height))
        return tex



    def CreateRootObject(self, name, width = None, height = None, depthMin = None, depthMax = None, isFullscreen = False, renderTarget = None, renderJob = None):
        desktop = uicls.UIRoot(pos=(0,
         0,
         width or trinity.app.width,
         height or trinity.app.height), name=name, state=uiconst.UI_NORMAL, depthMin=depthMin, depthMax=depthMax, isFullscreen=isFullscreen, renderTarget=renderTarget, renderJob=renderJob)
        self.AddRootObject(desktop)
        return desktop



    def GetRenderJob(self):
        return self.renderJob



    def GetVideoJob(self):
        return self.videoJob



    def _GetMouseTravel(self):
        if self._mouseButtonStates.get(uiconst.MOUSELEFT, False):
            (x, y, z,) = self._mouseDownPosition[uiconst.MOUSELEFT]
            return math.sqrt(abs((x - self.x) * (x - self.x) + (y - self.y) * (y - self.y)))
        return 0


    mouseTravel = property(_GetMouseTravel)

    def _GetRightBtn(self):
        return self._mouseButtonStates.get(uiconst.MOUSERIGHT, False)


    rightbtn = property(_GetRightBtn)

    def _GetLeftBtn(self):
        return self._mouseButtonStates.get(uiconst.MOUSELEFT, False)


    leftbtn = property(_GetLeftBtn)

    def _GetMiddleBtn(self):
        return self._mouseButtonStates.get(uiconst.MOUSEMIDDLE, False)


    midbtn = property(_GetMiddleBtn)

    def ReleaseObject(self, object):
        RO = object.GetRenderObject()
        if RO in self.renderObjectToPyObjectDict:
            del self.renderObjectToPyObjectDict[RO]
        mouseOver = self.GetMouseOver()
        if mouseOver is object:
            self._mouseOver = None
        mouseCaptureItem = self.GetMouseCapture()
        if mouseCaptureItem is object:
            self.ReleaseCapture()



    def GetMouseOver(self):
        if self._mouseOver:
            mouseOver = self._mouseOver()
            if mouseOver and not mouseOver.destroyed:
                return mouseOver
            self._mouseOver = None
        return uicore.desktop


    mouseOver = property(GetMouseOver)

    def CheckWindowEnterExit(self):
        item = self.GetMouseOver()
        while item.parent:
            if isinstance(item, uicls.WindowCore) and item.state == uiconst.UI_NORMAL:
                item.ShowHeaderButtons()
                break
            if not item.parent:
                break
            item = item.parent




    def CheckAppFocus(self, hasFocus):
        if getattr(uicore, 'registry', None) is None:
            return 
        uicore.UpdateCursor(self.GetMouseOver(), 1)
        if hasFocus and self.appfocusitem and self.appfocusitem():
            f = self.appfocusitem()
            if f is not None and not f.destroyed:
                uicore.registry.SetFocus(f)
            self.appfocusitem = None
        focus = uicore.registry.GetFocus()
        if not hasFocus and focus:
            self.appfocusitem = weakref.ref(focus)
            uicore.registry.SetFocus(None)
        return 1



    def CheckAccelerators(self, vkey, flag):
        modkeys = self.GetModifierKeyState(vkey)
        if self.CheckMappedAccelerators(modkeys, vkey, flag):
            return True
        if self.CheckDirectionalAccelerators(vkey):
            return True
        return False



    def GetModifierKeyState(self, vkey = None):
        ret = []
        for key in uiconst.MODKEYS:
            ret.append(trinity.app.Key(key) and key != vkey)

        return tuple(ret)



    def CheckMappedAccelerators(self, modkeys, vkey, flag):
        ctrl = self.Key(uiconst.VK_CONTROL)
        if not ctrl and (self._modkeysOff, vkey) in uicore.cmd.commandMap.accelerators:
            cmd = uicore.cmd.commandMap.accelerators[(self._modkeysOff, vkey)]
            if cmd.ignoreModifierKey:
                if not cmd.repeatable and flag & 1073741824:
                    return False
                sm.ScatterEvent('OnCommandExecuted', cmd.name)
                ret = cmd.callback()
                if ret:
                    return ret
        if (modkeys, vkey) in uicore.cmd.commandMap.accelerators:
            cmd = uicore.cmd.commandMap.accelerators[(modkeys, vkey)]
            if not cmd.repeatable and flag & 1073741824:
                return False
            sm.ScatterEvent('OnCommandExecuted', cmd.name)
            return cmd.callback()
        return False



    def CheckDirectionalAccelerators(self, vkey):
        active = uicore.registry.GetActive()
        focus = uicore.registry.GetFocus()
        focusOrActive = focus or active
        if vkey == uiconst.VK_UP and hasattr(focusOrActive, 'OnUp'):
            uthread.pool('uisvc::CheckDirectionalAccelerators OnUp', focusOrActive.OnUp)
            return True
        if vkey == uiconst.VK_DOWN and hasattr(focusOrActive, 'OnDown'):
            uthread.pool('uisvc::CheckDirectionalAccelerators OnDown', focusOrActive.OnDown)
            return True
        if vkey == uiconst.VK_LEFT and hasattr(focusOrActive, 'OnLeft'):
            uthread.pool('uisvc::CheckDirectionalAccelerators OnLeft', focusOrActive.OnLeft)
            return True
        if vkey == uiconst.VK_RIGHT and hasattr(focusOrActive, 'OnRight'):
            uthread.pool('uisvc::CheckDirectionalAccelerators OnRight', focusOrActive.OnRight)
            return True
        if vkey == uiconst.VK_HOME and hasattr(focusOrActive, 'OnHome'):
            uthread.pool('uisvc::CheckDirectionalAccelerators OnHome', focusOrActive.OnHome)
            return True
        if vkey == uiconst.VK_END and hasattr(focusOrActive, 'OnEnd'):
            uthread.pool('uisvc::CheckDirectionalAccelerators OnEnd', focusOrActive.OnEnd)
            return True



    def RegisterForTriuiEvents(self, msgIDlst, function, *args, **kw):
        if type(msgIDlst) == int:
            msgIDlst = [msgIDlst]
        cookie = uthread.uniqueId() or uthread.uniqueId()
        self._triuiRegs[cookie] = msgIDlst
        ref = util.CallableWeakRef(function)
        for id_ in msgIDlst:
            self._triuiRegsByMsgID.setdefault(id_, {})[cookie] = (ref, args, kw)

        log.LogInfo('RegisterForTriuiEvents', cookie, msgIDlst, function, args, kw)
        return cookie



    def UnregisterForTriuiEvents(self, cookie):
        if cookie not in self._triuiRegs:
            return 
        log.LogInfo('UnregisterForTriuiEvents', cookie)
        try:
            for msgID_ in self._triuiRegs[cookie]:
                del self._triuiRegsByMsgID[msgID_][cookie]

            del self._triuiRegs[cookie]
        except KeyError as what:
            log.LogError('UnregisterForTriuiEvents: Tried to kill unexisting registration?', cookie)
            log.LogException()



    def RegisterCharsThatCanBlock(self, vkey, *args):
        self._charsThatCanBlock.add(vkey)



    def RegisterObject(self, pyObject, renderObject):
        self.renderObjectToPyObjectDict[renderObject] = pyObject



    def GetPyObjectFromRenderObject(self, RO):
        return self.renderObjectToPyObjectDict.get(RO, None)



    def AddRootObject(self, obj):
        if self.rootObjectsByName.has_key(obj.name):
            raise AttributeError('Root object already exists with this name (%s)' % obj.name)
        self.rootObjectsByName[obj.name] = obj
        if obj not in self.rootObjects:
            self.rootObjects.append(obj)



    def RemoveRootObject(self, obj):
        if obj.name in self.rootObjectsByName:
            del self.rootObjectsByName[obj.name]
        if obj in self.rootObjects:
            self.rootObjects.remove(obj)



    def FindRootObject(self, name):
        return self.rootObjectsByName.get(name, None)



    @bluepy.CCP_STATS_ZONE_METHOD
    def Update(self, *args):
        if getattr(self, 'updatingFromRoot', False):
            return 
        self.UpdateMouseOver()
        for root in self.rootObjects:
            root.UpdateAlignment()

        for island in self.alignIslands:
            island.UpdateAlignmentAsRoot()

        self.alignIslands = []



    def SetSceneCamera(self, camera):
        self.sceneViewStep.camera = camera
        self.sceneProjectionStep.projection = camera.triProjection



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateMouseOver(self, *args):
        pyObject = None
        for root in self.rootObjects:
            RO = root.GetRenderObject()
            if not RO:
                continue
            camera = root.GetCamera()
            triobj = None
            if root.renderTargetStep:
                pass
            elif camera:
                triobj = RO.PickObject(self.x, self.y, camera.projectionMatrix, camera.viewMatrix, trinity.device.viewport)
            else:
                triobj = RO.PickObject(self.x, self.y, self._pickProjection, self._pickView, self._pickViewport)
            if triobj:
                pyObject = self.GetPyObjectFromRenderObject(triobj)
                if pyObject:
                    overridePick = getattr(pyObject, 'OverridePick', None)
                    if overridePick:
                        overrideObject = overridePick(self.x, self.y)
                        if overrideObject:
                            pyObject = overrideObject
                if pyObject:
                    break

        newMouseOver = pyObject or uicore.desktop
        currentMouseOver = self.GetMouseOver()
        mouseCaptureItem = self.GetMouseCapture()
        self._mouseOver = weakref.ref(newMouseOver)
        if not mouseCaptureItem and currentMouseOver is not newMouseOver:
            if self._hoverThread:
                self._hoverThread.kill()
            if currentMouseOver:
                self._TryExecuteHandler(uiconst.UI_MOUSEEXIT, currentMouseOver, param=None)
            if newMouseOver:
                self._TryExecuteHandler(uiconst.UI_MOUSEENTER, newMouseOver, param=None)
                (hoverHandlerArgs, hoverHandler,) = self.FindEventHandler(newMouseOver, EVENTMAP[uiconst.UI_MOUSEHOVER])
                if hoverHandler:
                    self._hoverThread = uthread.new(self._HoverThread)
            uicore.CheckHint()
            uicore.CheckCursor()
            self.CheckWindowEnterExit()



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnAppEvent(self, msgID, wParam, lParam):
        returnValue = 0
        currentMouseOver = self.GetMouseOver()
        if msgID == WM_MOUSEMOVE:
            mouseX = lParam & 65535
            mouseY = lParam >> 16
            if self.x != mouseX or self.y != mouseY:
                self.dx = mouseX - self.x
                self.dy = mouseY - self.y
                self.x = mouseX
                self.y = mouseY
                self.z = 0
                mouseCaptureItem = self.GetMouseCapture()
                if mouseCaptureItem:
                    self._TryExecuteHandler(uiconst.UI_MOUSEMOVE, mouseCaptureItem, param=(wParam, lParam))
                elif currentMouseOver:
                    self._TryExecuteHandler(uiconst.UI_MOUSEMOVE, currentMouseOver, param=(wParam, lParam))
        elif msgID == WM_LBUTTONDOWN:
            self._expandMenu = uiconst.MOUSELEFT
            self._mouseButtonStates[uiconst.MOUSELEFT] = True
            self._mouseDownPosition[uiconst.MOUSELEFT] = (self.x, self.y, self.z)
            if self.exclusiveMouseFocusActive:
                self._TryExecuteHandler(uiconst.UI_MOUSEDOWN, self.GetMouseCapture(), (uiconst.MOUSELEFT,), param=(uiconst.MOUSELEFT, wParam))
            else:
                self._TryExecuteHandler(uiconst.UI_MOUSEDOWN, currentMouseOver, (uiconst.MOUSELEFT,), param=(uiconst.MOUSELEFT, wParam))
                self.SetCapture(currentMouseOver, retainFocus=self.exclusiveMouseFocusActive)
                if not uiutil.IsUnder(currentMouseOver, uicore.layer.menu):
                    uiutil.Flush(uicore.layer.menu)
                    currentFocus = uicore.registry.GetFocus()
                    if currentFocus != currentMouseOver:
                        uicore.registry.SetFocus(currentMouseOver)
        elif msgID == WM_MBUTTONDOWN:
            self._expandMenu = None
            self._mouseButtonStates[uiconst.MOUSEMIDDLE] = True
            self._mouseDownPosition[uiconst.MOUSEMIDDLE] = (self.x, self.y, self.z)
            self._TryExecuteHandler(uiconst.UI_MOUSEDOWN, currentMouseOver, (uiconst.MOUSEMIDDLE,), param=(uiconst.MOUSEMIDDLE, wParam))
            uthread.new(self.CheckAccelerators, uiconst.VK_MBUTTON, lParam)
        elif msgID == WM_RBUTTONDOWN:
            self._expandMenu = uiconst.MOUSERIGHT
            self._mouseButtonStates[uiconst.MOUSERIGHT] = True
            self._mouseDownPosition[uiconst.MOUSERIGHT] = (self.x, self.y, self.z)
            if self.exclusiveMouseFocusActive:
                self._TryExecuteHandler(uiconst.UI_MOUSEDOWN, self.GetMouseCapture(), (uiconst.MOUSERIGHT,), param=(uiconst.MOUSERIGHT, wParam))
            else:
                self._TryExecuteHandler(uiconst.UI_MOUSEDOWN, currentMouseOver, (uiconst.MOUSERIGHT,), param=(uiconst.MOUSERIGHT, wParam))
            currentFocus = uicore.registry.GetFocus()
            if currentFocus is not currentMouseOver:
                uicore.registry.SetFocus(currentMouseOver)
        elif msgID == WM_XBUTTONDOWN:
            if wParam & 65536:
                self._mouseButtonStates[uiconst.MOUSEXBUTTON1] = True
                self._TryExecuteHandler(uiconst.UI_MOUSEDOWN, currentMouseOver, (uiconst.MOUSEXBUTTON1,), param=(uiconst.MOUSEXBUTTON1, wParam))
                uthread.new(self.CheckAccelerators, uiconst.VK_XBUTTON1, lParam)
            else:
                self._mouseButtonStates[uiconst.MOUSEXBUTTON2] = True
                self._TryExecuteHandler(uiconst.UI_MOUSEDOWN, currentMouseOver, (uiconst.MOUSEXBUTTON2,), param=(uiconst.MOUSEXBUTTON2, wParam))
                uthread.new(self.CheckAccelerators, uiconst.VK_XBUTTON2, lParam)
        elif msgID == WM_LBUTTONUP:
            self._mouseButtonStates[uiconst.MOUSELEFT] = False
            mouseCaptureItem = self.GetMouseCapture()
            if mouseCaptureItem:
                if not self.exclusiveMouseFocusActive:
                    if getattr(mouseCaptureItem, 'expandOnLeft', 0) and not self.rightbtn and self._expandMenu == uiconst.MOUSELEFT and getattr(mouseCaptureItem, 'GetMenu', None):
                        (x, y, z,) = self._mouseDownPosition[uiconst.MOUSELEFT]
                        if abs(self.x - x) < 3 and abs(self.y - y) < 3:
                            uthread.new(menu.ShowMenu, mouseCaptureItem)
                    self._expandMenu = False
                self._TryExecuteHandler(uiconst.UI_MOUSEUP, mouseCaptureItem, (uiconst.MOUSELEFT,), param=(uiconst.MOUSELEFT, wParam))
                if not self.exclusiveMouseFocusActive:
                    self.ReleaseCapture()
                if currentMouseOver is not mouseCaptureItem:
                    self._TryExecuteHandler(uiconst.UI_MOUSEEXIT, mouseCaptureItem, param=(wParam, lParam))
                    self._TryExecuteHandler(uiconst.UI_MOUSEENTER, currentMouseOver, param=(wParam, lParam))
                else:
                    self._clickTimer = None
                    self._clickCount += 1
                    if self._clickCount == 1:
                        self._TryExecuteHandler(uiconst.UI_CLICK, currentMouseOver, param=(wParam, lParam))
                        self.SetClickObject(currentMouseOver)
                        self._clickPosition = (self.x, self.y)
                    else:
                        (x, y,) = self._clickPosition
                        clickObject = self.GetClickObject()
                        if clickObject is currentMouseOver and abs(self.x - x) < 5 and abs(self.y - y) < 5:
                            (dblHandlerArgs, dblHandler,) = self.FindEventHandler(clickObject, 'OnDblClick')
                            (tripHandlerArgs, tripleHandler,) = self.FindEventHandler(clickObject, 'OnTripleClick')
                            if dblHandler or tripleHandler:
                                if dblHandler and self._clickCount == 2:
                                    self._TryExecuteHandler(uiconst.UI_DBLCLICK, clickObject, param=(wParam, lParam))
                                elif tripleHandler and self._clickCount == 3:
                                    self._TryExecuteHandler(uiconst.UI_TRIPLECLICK, clickObject, param=(wParam, lParam))
                        else:
                            self._clickCount = 0
                self._clickTimer = base.AutoTimer(CLICKCOUNTRESETTIME, self.ResetClickCounter)
        elif msgID == WM_RBUTTONUP:
            self._mouseButtonStates[uiconst.MOUSERIGHT] = False
            if self.exclusiveMouseFocusActive:
                self._TryExecuteHandler(uiconst.UI_MOUSEUP, self.GetMouseCapture(), (uiconst.MOUSERIGHT,), param=(uiconst.MOUSERIGHT, wParam))
            elif not self.leftbtn and self._expandMenu == uiconst.MOUSERIGHT and getattr(currentMouseOver, 'GetMenu', None):
                (x, y, z,) = self._mouseDownPosition[uiconst.MOUSERIGHT]
                if abs(self.x - x) < 3 and abs(self.y - y) < 3:
                    uthread.new(menu.ShowMenu, currentMouseOver)
            self._expandMenu = None
            self._TryExecuteHandler(uiconst.UI_MOUSEUP, currentMouseOver, (uiconst.MOUSERIGHT,), param=(uiconst.MOUSERIGHT, wParam))
        elif msgID == WM_MBUTTONUP:
            self._mouseButtonStates[uiconst.MOUSEMIDDLE] = False
            self._TryExecuteHandler(uiconst.UI_MOUSEUP, currentMouseOver, (uiconst.MOUSEMIDDLE,), param=(uiconst.MOUSEMIDDLE, wParam))
        elif msgID == WM_XBUTTONUP:
            if wParam & 65536:
                self._mouseButtonStates[uiconst.MOUSEXBUTTON1] = False
                self._TryExecuteHandler(uiconst.UI_MOUSEUP, currentMouseOver, (uiconst.MOUSEXBUTTON1,), param=(uiconst.MOUSEXBUTTON1, wParam))
            else:
                self._mouseButtonStates[uiconst.MOUSEXBUTTON2] = False
                self._TryExecuteHandler(uiconst.UI_MOUSEUP, currentMouseOver, (uiconst.MOUSEXBUTTON2,), param=(uiconst.MOUSEXBUTTON2, wParam))
        elif msgID == WM_MOUSEWHEEL:
            mouseZ = wParam >> 16
            self.dz = mouseZ
            calledOn = None
            focus = uicore.registry.GetFocus()
            if focus:
                calledOn = self._TryExecuteHandler(uiconst.UI_MOUSEWHEEL, focus, (mouseZ,), param=(wParam, lParam))
            if calledOn is None and self.mouseOver:
                mo = self.mouseOver
                (mwHandlerArgs, mwHandler,) = self.FindEventHandler(mo, 'OnMouseWheel')
                while not mwHandler:
                    if not mo.parent or mo is uicore.uilib.desktop:
                        break
                    mo = mo.parent
                    (mwHandlerArgs, mwHandler,) = self.FindEventHandler(mo, 'OnMouseWheel')

                if mo:
                    self._TryExecuteHandler(uiconst.UI_MOUSEWHEEL, mo, (mouseZ,), param=(wParam, lParam))
        elif msgID in (WM_KEYDOWN, WM_SYSKEYDOWN):
            focus = uicore.registry.GetFocus()
            if focus:
                self._TryExecuteHandler(uiconst.UI_KEYDOWN, focus, (wParam, lParam), param=(wParam, lParam))
            if self._unresolvedKeyDown:
                (_wParam, _lParam,) = self._unresolvedKeyDown
                self._unresolvedKeyDown = None
                self.CheckAccelerators(_wParam, _lParam)
            self._unresolvedKeyDown = (wParam, lParam)
            self._lastKeyDown = (wParam, lParam)
            uthread.new(self.CheckKeyDown, wParam, lParam)
        elif msgID == WM_CHAR:
            char = wParam
            ignoreChar = False
            (lastwParam, lastlParam,) = self._lastKeyDown
            if char <= 32:
                ctrl = trinity.app.Key(uiconst.VK_CONTROL)
                if char not in (uiconst.VK_RETURN, uiconst.VK_BACK, uiconst.VK_SPACE) or ctrl:
                    ignoreChar = True
            elif lastwParam in self._charsThatCanBlock:
                alt = trinity.app.Key(uiconst.VK_MENU)
                shift = trinity.app.Key(uiconst.VK_SHIFT)
                ctrl = trinity.app.Key(uiconst.VK_CONTROL)
                function = uicore.cmd.GetFuncByShortcut((ctrl,
                 alt,
                 shift,
                 lastwParam))
                if function is not None:
                    ignoreChar = True
            if not ignoreChar:
                calledOn = self.ResolveOnChar(wParam, lParam)
                if calledOn:
                    self._unresolvedKeyDown = None
        elif msgID in (WM_KEYUP, WM_SYSKEYUP):
            focus = uicore.registry.GetFocus()
            if focus:
                self._TryExecuteHandler(uiconst.UI_KEYUP, focus, (wParam, lParam), param=(wParam, lParam))
            if wParam == uiconst.VK_SNAPSHOT:
                uicore.cmd.PrintScreen()
        elif msgID == WM_ACTIVATE:
            self.CheckAppFocus(hasFocus=wParam > 0)
            self.CheckCallbacks(obj=uicore.registry.GetFocus(), msgID=uiconst.UI_ACTIVE, param=(wParam, lParam))
        elif msgID == WM_ACTIVATEAPP:
            if self.activateAppHandler:
                returnValue = self.activateAppHandler(wParam, lParam)
        elif msgID == WM_INPUTLANGCHANGE:
            if self.inputLangChangeHandler:
                returnValue = self.inputLangChangeHandler(wParam, lParam)
        elif msgID == WM_IME_SETCONTEXT:
            if self.imeSetContextHandler:
                returnValue = self.imeSetContextHandler(wParam, lParam)
        elif msgID == WM_IME_STARTCOMPOSITION:
            if self.imeStartCompositionHandler:
                returnValue = self.imeStartCompositionHandler(wParam, lParam)
        elif msgID == WM_IME_COMPOSITION:
            if self.imeCompositionHandler:
                returnValue = self.imeCompositionHandler(wParam, lParam)
        elif msgID == WM_IME_ENDCOMPOSITION:
            if self.imeEndCompositionHandler:
                returnValue = self.imeEndCompositionHandler(wParam, lParam)
        elif msgID == WM_IME_NOTIFY:
            if self.imeNotifyHandler:
                returnValue = self.imeNotifyHandler(wParam, lParam)
        else:
            returnValue = None
        return returnValue



    def CheckCallbacks(self, obj, msgID, param):
        for (cookie, (wr, args, kw,),) in self._triuiRegsByMsgID.get(msgID, {}).items():
            try:
                if not wr() or not wr()(*(args + (obj, msgID, param)), **kw):
                    self.UnregisterForTriuiEvents(cookie)
            except UserError as what:

                def f():
                    raise what


                uthread.new(f)
            except:
                log.LogError('OnAppEvent (cookie', cookie, '): Exception when trying to process callback!')
                log.LogException()




    def ResetClickCounter(self, *args):
        self._clickTimer = None
        self._clickCount = 0



    def KillClickThreads(self):
        self._clickTimer = None



    def ResolveOnChar(self, char, flag):
        ignore = (uiconst.VK_RETURN, uiconst.VK_BACK)
        if char < 32 and char not in ignore:
            return False
        focus = uicore.registry.GetFocus()
        if focus and hasattr(focus, 'OnChar') and uiutil.IsVisible(focus):
            if not blue.win32.IsTransgaming():
                capsLock = trinity.app.GetKeyState(uiconst.VK_CAPITAL)
                if capsLock:
                    char = ord(unichr(char).upper())
            ret = focus.OnChar(char, flag)
            if ret:
                return focus



    def CheckKeyDown(self, wParam, lParam):
        blue.pyos.synchro.Yield()
        if self._unresolvedKeyDown:
            (wParam, lParam,) = self._unresolvedKeyDown
            self._unresolvedKeyDown = None
            self.CheckAccelerators(wParam, lParam)



    def _TryExecuteHandler(self, eventID, object, eventArgs = None, param = None):
        functionName = EVENTMAP.get(eventID, None)
        if functionName is None:
            raise NotImplementedError
        itemCapturingMouse = self.GetMouseCapture()
        if itemCapturingMouse:
            object = itemCapturingMouse
        retObject = None
        (handlerArgs, handler,) = self.FindEventHandler(object, functionName)
        if handler:
            retObject = object
            if eventArgs:
                args = handlerArgs + eventArgs
            else:
                args = handlerArgs
            if eventID in UTHREADEDEVENTS:
                uthread.new(handler, *args)
            else:
                handler(*args)
        self.CheckCallbacks(retObject, eventID, param)
        return retObject



    def SetWindowOrder(self, *args):
        return trinity.app.uilib.SetWindowOrder(*args)



    def FindEventHandler(self, object, handlerName):
        return object.FindEventHandler(handlerName)



    def GetMouseButtonState(self, buttonFlag):
        return self._mouseButtonStates.get(buttonFlag, False)



    def Key(self, vkey):
        return trinity.app.Key(vkey)



    def SetCursorProperties(self, *args, **kwds):
        return trinity.app.SetCursorProperties(*args, **kwds)



    def SetCursorPos(self, x, y):
        return trinity.app.SetCursorPos(x, y)



    def SetCursor(self, cursorIx):
        if self.exclusiveMouseFocusActive:
            return 
        try:
            cursorName = 'res:/UI/Cursor/cursor{0:02}.dds'.format(cursorIx)
            sur = self.cursorCache.get(cursorName, None)
            if sur is None:
                sur = trinity.device.CreateOffscreenPlainSurface(32, 32, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
                f = ResFile(cursorName)
                sur.LoadSurfaceFromFile(f)
                self.cursorCache[cursorName] = sur
            self.SetCursorProperties(16, 15, sur)
        except trinity.D3DERR_DEVICELOST:
            pass



    def RecalcWindows(self, *args, **kwds):
        pass



    def FindWindow(self, wndName, fromParent):
        return trinity.app.uilib.FindWindow(wndName, fromParent)



    def SetMouseCapture(self, item, retainFocus = False):
        self._capturingMouseItem = weakref.ref(item)
        self.exclusiveMouseFocusActive = retainFocus


    SetCapture = SetMouseCapture

    def GetMouseCapture(self):
        if self._capturingMouseItem:
            return self._capturingMouseItem()


    GetCapture = GetMouseCapture
    capture = property(GetMouseCapture)

    def SetClickObject(self, item):
        self._clickItem = weakref.ref(item)



    def GetClickObject(self):
        if self._clickItem:
            return self._clickItem()



    def ReleaseCapture(self, itemReleasing = None):
        self._capturingMouseItem = None
        self.exclusiveMouseFocusActive = False



    def ClipCursor(self, *rect):
        self._cursorClip = rect
        (l, t, r, b,) = rect
        trinity.app.ClipCursor(int(l), int(t), int(r), int(b))



    def UnclipCursor(self, *args):
        self._cursorClip = None
        trinity.app.UnclipCursor()



    def _HoverThread(self):
        while True:
            if not trinity.app.IsActive():
                return 
            blue.synchro.Sleep(HOVERTIME)
            self._TryExecuteHandler(uiconst.UI_MOUSEHOVER, self.mouseOver)
            uicore.CheckHint()





