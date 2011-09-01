from nasty import nasty
import FxSequencer
import blue
import form
import listentry
import log
import service
import sys
import trinity
import uix
import uiutil
import mathUtil
import uthread
import util
import xtriui
import appUtils
import uiconst
import uicls
from sceneManager import SCENE_TYPE_INTERIOR
import weakref
import cameras
CACHESIZES = [0,
 32,
 128,
 256,
 512]
LEFTPADDING = 120

class SystemMenu(uicls.LayerCore):
    __guid__ = 'form.SystemMenu'
    __nonpersistvars__ = []
    __notifyevents__ = ['OnEchoChannel',
     'OnVoiceChatLoggedIn',
     'OnVoiceChatLoggedOut',
     'OnVoiceFontChanged',
     'OnEndChangeDevice',
     'OnUIColorsChanged']

    def Reset(self):
        self.sr.genericinited = 0
        self.sr.displayandgraphicsinited = 0
        self.sr.audioinited = 0
        self.sr.resetsettingsinited = 0
        self.sr.shortcutsinited = 0
        self.sr.languageinited = 0
        self.sr.abouteveinited = 0
        self.sr.wnd = None
        self.closing = 0
        self.inited = 0
        self.init_languageID = eve.session.languageID
        self.init_loadstationenv = prefs.GetValue('loadstationenv', 1)
        self.init_dockshipsanditems = settings.user.windows.Get('dockshipsanditems', 0)
        self.init_stationservicebtns = settings.user.ui.Get('stationservicebtns', 0)
        self.tempStuff = []
        self.colors = [(mls.UI_GENERIC_COLORARMYGREEN, (70 / 256.0,
           75 / 256.0,
           50 / 256.0,
           170 / 256.0)),
         (mls.UI_GENERIC_COLORBLACK, eve.themeColor),
         (mls.UI_GENERIC_COLORCOOLGRAY, (70 / 256.0,
           75 / 256.0,
           70 / 256.0,
           172 / 256.0)),
         (mls.UI_GENERIC_COLORDARKOPAQUE, (43 / 256.0,
           43 / 256.0,
           43 / 256.0,
           204 / 256.0)),
         (mls.UI_GENERIC_COLORDESERT, (111 / 256.0,
           102 / 256.0,
           82 / 256.0,
           184 / 256.0)),
         (mls.UI_GENERIC_COLORMIDGRAY, (101 / 256.0,
           100 / 256.0,
           111 / 256.0,
           171 / 256.0)),
         (mls.UI_GENERIC_COLORMIRAGE, (24 / 256.0,
           32 / 256.0,
           41 / 256.0,
           235 / 256.0)),
         (mls.UI_GENERIC_COLORNERO, (23 / 256.0,
           5 / 256.0,
           0 / 256.0,
           207 / 256.0)),
         (mls.UI_GENERIC_COLOROIL, (49 / 256.0,
           38 / 256.0,
           27 / 256.0,
           0.75)),
         (mls.UI_GENERIC_COLORSILVER, (125 / 256.0,
           125 / 256.0,
           125 / 256.0,
           130 / 256.0)),
         (mls.UI_GENERIC_COLORSTEALTH, (51 / 256.0,
           54 / 256.0,
           45 / 256.0,
           113 / 256.0)),
         (mls.UI_GENERIC_COLORSTEELGRAY, (61 / 256.0,
           55 / 256.0,
           68 / 256.0,
           172 / 256.0)),
         (mls.UI_GENERIC_COLORSWAMP, (0 / 256.0,
           21 / 256.0,
           21 / 256.0,
           181 / 256.0)),
         (mls.UI_GENERIC_COLORSBLACKPEARL, (9 / 256.0,
           30 / 256.0,
           45 / 256.0,
           201 / 256.0)),
         (mls.UI_GENERIC_COLORSDARKLUNARGREEN, (25 / 256.0,
           30 / 256.0,
           25 / 256.0,
           180 / 256.0))]
        self.backgroundcolors = [(mls.UI_GENERIC_COLORARMYGREEN, (14 / 256.0,
           28 / 256.0,
           17 / 256.0,
           170 / 256.0)),
         (mls.UI_GENERIC_COLORBLACK, eve.themeBgColor),
         (mls.UI_GENERIC_COLORCOOLGRAY, (14 / 256.0,
           28 / 256.0,
           32 / 256.0,
           172 / 256.0)),
         (mls.UI_GENERIC_COLORDARKOPAQUE, (19 / 256.0,
           19 / 256.0,
           19 / 256.0,
           204 / 256.0)),
         (mls.UI_GENERIC_COLORDESERT, (71 / 256.0,
           53 / 256.0,
           37 / 256.0,
           184 / 256.0)),
         (mls.UI_GENERIC_COLORMIDGRAY, (71 / 256.0,
           70 / 256.0,
           79 / 256.0,
           200 / 256.0)),
         (mls.UI_GENERIC_COLORMIRAGE, (34 / 256.0,
           48 / 256.0,
           59 / 256.0,
           132 / 256.0)),
         (mls.UI_GENERIC_COLORNERO, (32 / 256.0,
           32 / 256.0,
           32 / 256.0,
           145 / 256.0)),
         (mls.UI_GENERIC_COLOROIL, (116 / 256.0,
           116 / 256.0,
           116 / 256.0,
           152 / 256.0)),
         (mls.UI_GENERIC_COLORSILVER, (0.0,
           0.0,
           0.0,
           160 / 256.0)),
         (mls.UI_GENERIC_COLORSTEALTH, (25 / 256.0,
           23 / 256.0,
           15 / 256.0,
           150 / 256.0)),
         (mls.UI_GENERIC_COLORSTEELGRAY, (32 / 256.0,
           41 / 256.0,
           46 / 256.0,
           168 / 256.0)),
         (mls.UI_GENERIC_COLORSWAMP, (23 / 256.0,
           23 / 256.0,
           23 / 256.0,
           153 / 256.0)),
         (mls.UI_GENERIC_COLORSBLACKPEARL, (116 / 256.0,
           116 / 256.0,
           116 / 256.0,
           116 / 256.0)),
         (mls.UI_GENERIC_COLORSDARKLUNARGREEN, (70 / 256.0,
           75 / 256.0,
           70 / 256.0,
           200 / 256.0))]
        self.components = [(mls.UI_GENERIC_COLORARMYGREEN, (14 / 256.0,
           28 / 256.0,
           17 / 256.0,
           170 / 256.0)),
         (mls.UI_GENERIC_COLORBLACK, eve.themeCompColor),
         (mls.UI_GENERIC_COLORCOOLGRAY, (14 / 256.0,
           28 / 256.0,
           32 / 256.0,
           172 / 256.0)),
         (mls.UI_GENERIC_COLORDARKOPAQUE, (31 / 256.0,
           31 / 256.0,
           31 / 256.0,
           204 / 256.0)),
         (mls.UI_GENERIC_COLORDESERT, (71 / 256.0,
           53 / 256.0,
           37 / 256.0,
           184 / 256.0)),
         (mls.UI_GENERIC_COLORMIDGRAY, (32 / 256.0,
           32 / 256.0,
           32 / 256.0,
           128 / 256.0)),
         (mls.UI_GENERIC_COLORMIRAGE, (0 / 256.0,
           0 / 256.0,
           0 / 256.0,
           112 / 256.0)),
         (mls.UI_GENERIC_COLORNERO, (23 / 256.0,
           5 / 256.0,
           0 / 256.0,
           145 / 256.0)),
         (mls.UI_GENERIC_COLOROIL, (42 / 256.0,
           42 / 256.0,
           42 / 256.0,
           162 / 256.0)),
         (mls.UI_GENERIC_COLORSILVER, (0.0,
           0.0,
           0.0,
           61 / 256.0)),
         (mls.UI_GENERIC_COLORSTEALTH, (25 / 256.0,
           23 / 256.0,
           15 / 256.0,
           150 / 256.0)),
         (mls.UI_GENERIC_COLORSTEELGRAY, (32 / 256.0,
           41 / 256.0,
           46 / 256.0,
           168 / 256.0)),
         (mls.UI_GENERIC_COLORSWAMP, (31 / 256.0,
           61 / 256.0,
           71 / 256.0,
           121 / 256.0)),
         (mls.UI_GENERIC_COLORSBLACKPEARL, (2 / 256.0,
           4 / 256.0,
           9 / 256.0,
           110 / 256.0)),
         (mls.UI_GENERIC_COLORSDARKLUNARGREEN, (2 / 256.0,
           4 / 256.0,
           9 / 256.0,
           109 / 256.0))]
        self.componentsubs = [(mls.UI_GENERIC_COLORARMYGREEN, (182 / 256.0,
           210 / 256.0,
           182 / 256.0,
           44 / 256.0)),
         (mls.UI_GENERIC_COLORBLACK, eve.themeCompSubColor),
         (mls.UI_GENERIC_COLORCOOLGRAY, (149 / 256.0,
           194 / 256.0,
           216 / 256.0,
           16 / 256.0)),
         (mls.UI_GENERIC_COLORDARKOPAQUE, (256 / 256.0,
           256 / 256.0,
           256 / 256.0,
           16 / 256.0)),
         (mls.UI_GENERIC_COLORDESERT, (221 / 256.0,
           232 / 256.0,
           256 / 256.0,
           11 / 256.0)),
         (mls.UI_GENERIC_COLORMIDGRAY, (127 / 256.0,
           127 / 256.0,
           127 / 256.0,
           115 / 256.0)),
         (mls.UI_GENERIC_COLORMIRAGE, (0 / 256.0,
           0 / 256.0,
           0 / 256.0,
           50 / 256.0)),
         (mls.UI_GENERIC_COLORNERO, (23 / 256.0,
           5 / 256.0,
           0 / 256.0,
           145 / 256.0)),
         (mls.UI_GENERIC_COLOROIL, (25 / 256.0,
           25 / 256.0,
           25 / 256.0,
           160 / 256.0)),
         (mls.UI_GENERIC_COLORSILVER, (256 / 256.0,
           256 / 256.0,
           256 / 256.0,
           11 / 256.0)),
         (mls.UI_GENERIC_COLORSTEALTH, (206 / 256.0,
           206 / 256.0,
           206 / 256.0,
           16 / 256.0)),
         (mls.UI_GENERIC_COLORSTEELGRAY, (88 / 256.0,
           83 / 256.0,
           94 / 256.0,
           110 / 256.0)),
         (mls.UI_GENERIC_COLORSWAMP, (31 / 256.0,
           61 / 256.0,
           71 / 256.0,
           121 / 256.0)),
         (mls.UI_GENERIC_COLORSBLACKPEARL, (2 / 256.0,
           4 / 256.0,
           9 / 256.0,
           115 / 256.0)),
         (mls.UI_GENERIC_COLORSDARKLUNARGREEN, (2 / 256.0,
           4 / 256.0,
           9 / 256.0,
           114 / 256.0))]
        self.voiceFontList = None
        if sm.GetService('vivox').Enabled():
            sm.GetService('vivox').StopAudioTest()



    def OnCloseView(self):
        if self.hideUI and eve.session.userid:
            sm.GetService('cmd').ShowUI()
        if self.settings:
            self.ApplyDeviceChanges()
        if getattr(self, 'optimizeWnd', None) is not None:
            self.optimizeWnd.SelfDestruct()
        vivox = sm.GetService('vivox')
        if vivox.Enabled():
            vivox.LeaveEchoChannel()
        self.ApplyGraphicsSettings()
        self.ClearBGPostProcess()
        self.StationUpdateCheck()
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        if scene2 is not None and scene2.sunBall is not None:
            scene2.sunBall.EnableOccluders(settings.public.device.Get('sunOcclusion', 1))
        sm.GetService('sceneManager').CheckCameraOffsets()
        sm.GetService('cameraClient').ApplyUserSettings()
        if eve.session.charid:
            mapOpen = sm.GetService('map').ViewingStarMap()
            if mapOpen:
                sm.GetService('starmap').UpdateRoute()
        sm.GetService('settings').LoadSettings()
        self.Reset()
        uicore.registry.CheckMoveActiveState()
        sm.UnregisterNotify(self)



    def OnOpenView(self):
        self.Reset()
        self.sr.wnd = uicls.Container(name='sysmenu', parent=self)
        self.settings = None
        self.hideUI = not bool(eve.hiddenUIState)
        self.Setup()
        sm.RegisterNotify(self)



    def GetBackground(self, fade = 1):
        background = uicls.Fill(parent=self.sr.wnd, color=(0.0, 0.0, 0.0, 0.0), state=uiconst.UI_NORMAL)
        self.SetBGPostProcess(1)
        self.sr.bg = background
        if fade:
            uthread.new(self.FadeBG, 0.0, 0.75, 1, background, time=1000.0)
        else:
            background.color.a = 0.75
        if self.hideUI:
            sm.GetService('cmd').CmdHideUI(1)



    def SetBGPostProcess(self, saturationValue = 0):
        if not eve.session.userid:
            return 
        blue.resMan.Wait()
        sm.GetService('sceneManager').AddPostProcess('sysmenuDesaturate', 'res:/postprocess/desaturate.red')
        sm.GetService('sceneManager').SetPostProcessVariable('sysmenuDesaturate', 'SaturationFactor', saturationValue)



    def ClearBGPostProcess(self):
        if not eve.session.userid:
            return 
        sm.GetService('sceneManager').RemovePostProcess('sysmenuDesaturate')



    def FadeBG(self, fr, to, fadein, pic, time = 500.0):
        if self.sr.wnd is None or self.sr.wnd.destroyed:
            return 
        ndt = 0.0
        start = blue.os.GetTime(1)
        sceneManager = sm.GetService('sceneManager')
        while ndt != 1.0:
            ndt = min(blue.os.TimeDiffInMs(start) / time, 1.0)
            if not self or self.dead:
                return 
            if self.sr.wnd is None or self.sr.wnd.destroyed or pic is None or pic.destroyed:
                break
            pic.color.a = mathUtil.Lerp(fr, to, ndt)
            if fadein:
                sceneManager.SetPostProcessVariable('sysmenuDesaturate', 'SaturationFactor', 1 - ndt)
            else:
                sceneManager.SetPostProcessVariable('sysmenuDesaturate', 'SaturationFactor', ndt)
            blue.pyos.synchro.Yield()

        if fadein:
            sceneManager.SetPostProcessVariable('sysmenuDesaturate', 'SaturationFactor', 0)
        else:
            sceneManager.SetPostProcessVariable('sysmenuDesaturate', 'SaturationFactor', 1)
        if self.sr.wnd is None or self.sr.wnd.destroyed:
            return 
        self.inited = 1



    def GetTabs(self):
        if eve.session.userid:
            return ['displayandgraphics',
             'audioandchat',
             'generic',
             'shortcuts',
             'reset settings',
             'language',
             'about eve']
        else:
            return ['displayandgraphics',
             'audioandchat',
             'generic',
             'reset settings',
             'about eve']



    def Setup(self):
        width = 800
        push = sm.GetService('window').GetCameraLeftOffset(width, align=uiconst.CENTER, left=0)
        self.sr.wnd.state = uiconst.UI_HIDDEN
        menuarea = uicls.Container(name='menuarea', align=uiconst.CENTER, pos=(push,
         0,
         width,
         500), state=uiconst.UI_NORMAL, parent=self.sr.wnd)
        menuarea.isWindow = True
        mainclosex = uicls.Icon(icon='ui_38_16_220', parent=menuarea, pos=(2, 1, 0, 0), align=uiconst.TOPRIGHT, idx=0, state=uiconst.UI_NORMAL)
        mainclosex.OnClick = self.CloseMenuClick
        self.sr.menuarea = menuarea
        self.colWidth = (menuarea.width - 32) / 3
        menusub = uicls.Container(name='menusub', state=uiconst.UI_NORMAL, parent=menuarea, padTop=20)
        tabs = self.GetTabs()
        maintabgroups = []
        for tabname in tabs:
            if tabname == 'generic':
                label = mls.UI_SHARED_GENERALSETTINGS
            else:
                label = getattr(mls, 'UI_SYSMENU_' + tabname.replace(' ', '').upper())
            maintabgroups.append([label,
             uicls.Container(name=tabname + '_container', parent=menusub, padTop=8, padBottom=8),
             self,
             tabname])

        maintabs = uicls.TabGroup(parent=menusub, autoselecttab=True, tabs=maintabgroups, groupID='sysmenumaintabs', idx=0)
        self.sr.maintabs = maintabs
        uicls.Line(parent=menusub, align=uiconst.TOBOTTOM, padTop=-1)
        btnPar = uicls.Container(name='btnPar', parent=menusub, align=uiconst.TOBOTTOM, height=35, padTop=const.defaultPadding, idx=0)
        btn = uicls.Button(parent=btnPar, label=mls.UI_CMD_CLOSEWINDOW, func=self.CloseMenuClick, align=uiconst.CENTER)
        btn = uicls.Button(parent=btnPar, label=mls.UI_CMD_QUITGAME, func=self.QuitBtnClick, left=10, align=uiconst.CENTERRIGHT)
        if eve.session.userid:
            btn = uicls.Button(parent=btnPar, label=mls.UI_CMD_LOGOFF, func=self.Logoff, left=btn.width + btn.left + 2, align=uiconst.CENTERRIGHT)
            btn = uicls.Button(parent=btnPar, label=mls.UI_CMD_OPENPETITIONS, func=self.Petition, left=10, align=uiconst.CENTERLEFT)
        if eve.session.charid and boot.region != 'optic':
            btn = uicls.Button(parent=btnPar, label=mls.UI_CMD_CONVERTETC, func=self.ConvertETC, left=btn.width + btn.left + 2, align=uiconst.CENTERLEFT)
            btn = uicls.Button(parent=btnPar, label=mls.UI_GENERIC_REDEEMITEMS, func=self.RedeemItems, left=btn.width + btn.left + 2, align=uiconst.CENTERLEFT)
        if eve.session.userid:
            build = uicls.Label(text='%s: %s.%s' % (mls.UI_LOGIN_VERSION, boot.keyval['version'].split('=', 1)[1], boot.build), parent=self.sr.wnd, left=6, top=6, state=uiconst.UI_NORMAL)
        self.sr.wndUnderlay = uicls.WindowUnderlay(parent=menuarea)
        if eve.session.userid:
            blue.pyos.synchro.Yield()
            self.GetBackground()
        self.sr.wnd.state = uiconst.UI_NORMAL



    def CloseMenuClick(self, *args):
        uicore.cmd.OnEsc()



    def Logoff(self, *args):
        uicore.cmd.CmdLogOff()



    def Load(self, key):
        func = getattr(self, key.capitalize().replace(' ', ''), None)
        if func:
            uthread.new(func)
        uthread.new(uicore.registry.SetFocus, self.sr.menuarea)



    def InitDeviceSettings(self):
        self.settings = sm.GetService('device').GetSettings()
        self.initsettings = self.settings.copy()



    def UpdateUIColor(self, idname, value):
        if self.sr.genericinited:
            col = idname[-1]
            what = idname.split('_')[1]
            (main, backgroundcolor, component, componentsub,) = sm.GetService('window').GetWindowColors()
            if what.lower() == 'component':
                current = component
            elif what.lower() == 'componentsub':
                current = componentsub
            elif what.lower() == 'backgroundcolor':
                current = backgroundcolor
            elif what.lower() == 'color':
                current = main
            else:
                raise NotImplementedError
            colIdx = 'rgba'.index(col)
            current = list(current)
            current[colIdx] = value
            current = tuple(current)
            sm.GetService('window').SetWindowColor(what=what, *current)



    def _ColorChange(self, comboName, header, value, *args):
        for (i, color,) in enumerate('rgba'):
            slider = uiutil.FindChild(self.sr.wnd, 'wnd_%s_%s' % (comboName, color))
            if slider:
                uthread.pool('', slider.MorphTo, value[i])

        settings.user.windows.Set('wnd%s' % comboName.capitalize(), value)
        if comboName.startswith('component'):
            sm.GetService('window').SetWindowColor(what=comboName, *value)



    def ProcessDeviceSettings(self, whatChanged = ''):
        left = 80
        where = self.sr.monitorsetup
        if not where:
            return 
        set = self.settings
        deviceSvc = sm.GetService('device')
        deviceSet = deviceSvc.GetSettings()
        if where:
            uiutil.FlushList(where.children[1:])
        adapterOps = deviceSvc.GetAdaptersEnumerated()
        windowOps = deviceSvc.GetWindowModes()
        (resolutionOps, refresh,) = deviceSvc.GetAdapterResolutionsAndRefreshRates(set)
        currentRes = ('%sx%s' % (deviceSet.BackBufferWidth, deviceSet.BackBufferHeight), (deviceSet.BackBufferWidth, deviceSet.BackBufferHeight))
        windowed = set.Windowed
        if bool(set.Windowed) and settings.public.device.Get('FixedWindow', False):
            set.Windowed = 2
            windowed = 1
        elif not set.Windowed:
            settings.public.device.Set('FixedWindow', False)
        currentRes = ('%sx%s' % (deviceSet.BackBufferWidth, deviceSet.BackBufferHeight), (deviceSet.BackBufferWidth, deviceSet.BackBufferHeight))
        if windowed and currentRes not in resolutionOps:
            resolutionOps.append(currentRes)
        setBB = deviceSvc.GetPreferedResolution(windowed)
        triapp = trinity.app
        if triapp.isMaximized:
            setBB = (deviceSet.BackBufferWidth, deviceSet.BackBufferHeight)
        deviceData = [('header', mls.UI_SYSMENU_DISPLAYSETUP),
         ('text', mls.UI_SYSMENU_DISPLAYSETUP_DESCRIPTION),
         ('line',),
         ('combo',
          ('Adapter', None, set.Adapter),
          mls.UI_SYSMENU_DISPLAYADADAPTER,
          adapterOps,
          left,
          mls.UI_SYSMENU_DISPLAYADADAPTER_TOOLTIP,
          whatChanged == 'Adapter'),
         ('combo',
          ('Windowed', None, deviceSvc.IsWindowed(self.settings)),
          mls.UI_SYSMENU_WINDOWEDORFULLSCREEN,
          windowOps,
          left,
          mls.UI_SYSMENU_WINDOWEDORFULLSCREEN_TOOLTIP,
          whatChanged == 'Windowed'),
         ('combo',
          ('BackBufferSize', None, setBB),
          [mls.UI_SYSMENU_ADAPTERRESOLUTION, mls.UI_SYSMENU_WINDOWSIZE][windowed],
          resolutionOps,
          left,
          [mls.UI_SYSMENU_ADAPTERRESOLUTION_TOOLTIP, mls.UI_SYSMENU_WINDOWSIZE_TOOLTIP][windowed],
          whatChanged == 'BackBufferSize',
          triapp.isMaximized)]
        if blue.win32.IsTransgaming():
            deviceData += [('checkbox',
              ('MacMTOpenGL', ('public', 'ui'), bool(sm.GetService('cider').GetMultiThreadedOpenGL())),
              mls.UI_SYSMENU_MAC_MTOPENGL,
              None,
              None,
              mls.UI_SYSMENU_MAC_MTOPENGL_TOOLTIP)]
        options = deviceSvc.GetPresentationIntervalOptions(set)
        if set.PresentationInterval not in [ val for (label, val,) in options ]:
            set.PresentationInterval = options[1][1]
        deviceData.append(('combo',
         ('PresentationInterval', None, set.PresentationInterval),
         mls.UI_SYSMENU_PRESENTINTERVAL,
         options,
         left,
         mls.UI_SYSMENU_PRESENTINTERVAL_TOOLTIP))
        deviceData += [('line',)]
        if eve.session.userid:
            self.cameraOffsetTextAdded = 0
            deviceData.append(('slider',
             ('cameraOffset', ('user', 'ui'), 0.0),
             mls.UI_SYSMENU_CAMERACENTER,
             (-100, 100),
             120,
             10))
            deviceData.append(('toppush', 8))
            deviceData.append(('checkbox',
             ('offsetUIwithCamera', ('user', 'ui'), 0),
             mls.UI_SYSMENU_OFFSETUIWITHCAMERA,
             None,
             None,
             mls.UI_SYSMENU_OFFSETUIWITHCAMERAHINT))
            incarnaCameraSvc = sm.GetService('cameraClient')
            incarnaCamSett = incarnaCameraSvc.GetCameraSettings()
            deviceData += [('header', mls.UI_SYSMENU_CAMERA_HEADING_INCARNA_CAMERA),
             ('slider',
              ('incarnaCameraOffset', ('user', 'ui'), incarnaCamSett.charOffsetSetting),
              mls.UI_SYSMENU_CAMERACENTER,
              (-1.0, 1.0),
              120,
              10),
             ('toppush', 8),
             ('slider',
              ('incarnaCameraMouseLookSpeedSlider', ('user', 'ui'), incarnaCamSett.mouseLookSpeed),
              mls.UI_SYSMENU_CAMERALOOKSPEED,
              (-6, 6),
              120,
              10),
             ('toppush', 8),
             ('checkbox',
              ('incarnaCameraInvertY', ('user', 'ui'), incarnaCamSett.invertY),
              mls.UI_SYSMENU_CAMERA_INVERTY,
              None,
              None,
              mls.UI_SYSMENU_CAMERA_INVERTY_TOOLTIP),
             ('toppush', 8),
             ('checkbox',
              ('incarnaCameraMouseSmooth', ('user', 'ui'), incarnaCamSett.mouseSmooth),
              mls.UI_SYSMENU_CAMERA_SMOOTHMOUSE,
              None,
              None,
              mls.UI_SYSMENU_CAMERA_SMOOTHMOUSE_TOOLTIP)]
        self.ParseData(deviceData, where)
        btnPar = uicls.Container(name='btnpar', parent=where, align=uiconst.TOBOTTOM, height=32)
        btn = uicls.Button(parent=btnPar, label=mls.UI_GENERIC_APPLY, func=self.ApplyDeviceChanges, align=uiconst.CENTERTOP)



    def ApplyDeviceChanges(self, *args):
        deviceSvc = sm.GetService('device')
        if self.settings is None:
            return 
        s = self.settings.copy()
        fixedWindow = settings.public.device.Get('FixedWindow', False)
        deviceChanged = sm.GetService('device').CheckDeviceDifference(s, True)
        triapp = trinity.app
        if not deviceChanged and blue.win32.IsTransgaming():
            windowModeChanged = sm.GetService('cider').HasFullscreenModeChanged()
            deviceChanged = deviceChanged or windowModeChanged
        if deviceChanged:
            sm.GetService('device').SetDevice(s, userModified=True)
        elif triapp.fixedWindow != fixedWindow:
            triapp.AdjustWindowForChange(s.Windowed, fixedWindow)
            sm.GetService('device').UpdateWindowPosition(s)



    def OnEndChangeDevice(self, *args):
        if self and not self.dead and self.isopen:
            self.settings = sm.GetService('device').GetSettings()
            self.ProcessDeviceSettings()
            self.ProcessGraphicsSettings()



    def ChangeWindowMode(self, windowed):
        val = windowed
        if windowed == 2:
            settings.public.device.Set('FixedWindow', True)
            val = 1
        else:
            settings.public.device.Set('FixedWindow', False)
        (self.settings.BackBufferWidth, self.settings.BackBufferHeight,) = sm.GetService('device').GetPreferedResolution(val)
        if blue.win32.IsTransgaming():
            settings.public.ui.Set('MacFullscreen', not windowed)
        else:
            self.settings.Windowed = windowed



    def OnComboChange(self, combo, header, value, *args):
        if combo.name in ('Adapter', 'Windowed', 'BackBufferFormat', 'BackBufferSize', 'AutoDepthStencilFormat', 'zEnable', 'PresentationInterval', 'incarnaCameraChase', 'Anti-Aliasing'):
            rot = blue.os.CreateInstance('blue.Rot')
            triapp = trinity.app
            D3D = rot.GetInstance('tri:/Direct3D', 'trinity.TriDirect3D')
            if combo.name == 'BackBufferSize':
                setattr(self.settings, 'BackBufferWidth', value[0])
                setattr(self.settings, 'BackBufferHeight', value[1])
                if self.settings.Windowed and not triapp.isMaximized:
                    settings.public.device.Set('WindowedResolution', value)
                elif not self.settings.Windowed:
                    settings.public.device.Set('FullScreenResolution', value)
            elif combo.name == 'Anti-Aliasing':
                prefs.SetValue('antiAliasing', value)
            elif combo.name == 'Windowed':
                self.ChangeWindowMode(value)
            else:
                setattr(self.settings, combo.name, value)
            self.ProcessDeviceSettings(whatChanged=combo.name)
        elif combo.name == 'autoTargetBack':
            settings.user.ui.Set('autoTargetBack', value)
        elif combo.name in ('color', 'backgroundcolor', 'component', 'componentsub'):
            if settings.user.ui.Get('linkColorCombos', False) and header != mls.UI_SYSMENU_CUSTOMCOL:
                for box in ['color',
                 'backgroundcolor',
                 'component',
                 'componentsub']:
                    combo = uiutil.GetChild(combo.parent.parent, box)
                    combo.SelectItemByLabel(header)
                    col = self.FindColorFromName(header, getattr(self, '%ss' % box))
                    self._ColorChange(box, header, col)

            else:
                self._ColorChange(combo.name, header, value)
        elif combo.name == 'talkBinding':
            settings.user.audio.Set('talkBinding', value)
            sm.GetService('vivox').EnableGlobalPushToTalkMode('talk', value)
        elif combo.name == 'talkMoveToTopBtn':
            settings.user.audio.Set('talkMoveToTopBtn', value)
        elif combo.name == 'talkAutoJoinFleet':
            settings.user.audio.Set('talkAutoJoinFleet', value)
        elif combo.name == 'TalkOutputDevice':
            settings.user.audio.Set('TalkOutputDevice', value)
            sm.GetService('vivox').SetPreferredAudioOutputDevice(value)
        elif combo.name == 'TalkInputDevice':
            settings.user.audio.Set('TalkInputDevice', value)
            sm.GetService('vivox').SetPreferredAudioInputDevice(value)
        elif combo.name == 'fontWFactor':
            settings.user.ui.Set('fontWFactor', value)
            wnds = [ w for w in uicore.desktop.Find('trinity.Tr2Sprite2d') + uicore.desktop.Find('trinity.Tr2Sprite2dContainer') if hasattr(w, 'DoFontChange') ]
            for s in wnds:
                s.DoFontChange()

            if sm.GetService('vivox').Enabled():
                sm.GetService('vivox').StopAudioTest()
            for each in self.GetTabs():
                contName = each[:]
                config = '%sinited' % each.replace(' ', '')
                if self.sr.Get(config) and self.sr.Get(config, False):
                    parent = uiutil.GetChild(self.sr.wnd, '%s_container' % contName)
                    uix.Flush(parent)
                    setattr(self.sr, config, 0)

            self.sr.maintabs.ReloadVisible()
            sm.ScatterEvent('OnFontChanged')
        elif combo.name == 'actionmenuBtn':
            settings.user.ui.Set('actionmenuBtn', value)
        elif combo.name == 'cmenufontsize':
            settings.user.ui.Set('cmenufontsize', value)
        elif combo.name == 'snapdistance':
            settings.user.windows.Set('snapdistance', value)
        elif combo.name == 'contentEdition':
            prefs.trinityVersion = value
            self.ProcessGraphicsSettings()
        elif combo.name == 'cachesize':
            prefs.SetValue('resourceCacheSize_dx9', value)
        elif combo.name == 'dblClickUser':
            settings.user.ui.Set('dblClickUser', value)
        elif combo.name == 'shaderQuality':
            prefs.SetValue('shaderQuality', value)
            clothEnabled = value == 3
            prefs.SetValue('charClothSimulation', int(clothEnabled))
            sm.GetService('sceneManager').ApplyClothSimulationSettings()
        elif combo.name == 'textureQuality':
            prefs.SetValue('textureQuality', value)
        elif combo.name == 'lodQuality':
            prefs.SetValue('lodQuality', value)
        elif combo.name == 'postProcessingQuality':
            prefs.SetValue('postProcessingQuality', value)
        elif combo.name == 'charTextureQuality':
            prefs.SetValue('charTextureQuality', value)
        elif combo.name == 'shadowQuality':
            prefs.SetValue('shadowQuality', value)
        elif combo.name == 'interiorGraphicsQuality':
            prefs.SetValue('interiorGraphicsQuality', value)



    def OnMicrophoneIntensityEvent(self, level):
        if not self or self.destroyed:
            return 
        if not self.sr.audioinited:
            return 
        if level:
            maxW = self.sr.inputmeter.parent.GetAbsolute()[2] - 4
            level = int(maxW * level)
            if level > 100:
                level = 100
            self.sr.inputmeter.width = int(maxW * (level / 100.0))
        else:
            self.sr.inputmeter.width = 0



    def JoinLeaveEchoChannel(self, *args):
        self.echoBtn.state = uiconst.UI_DISABLED
        sm.GetService('vivox').JoinEchoChannel()



    def OnVoiceFontChanged(self):
        self._SystemMenu__RebuildAudioAndChatPanel()



    def OnEchoChannel(self, joined):
        self._SystemMenu__RebuildAudioAndChatPanel()



    def OnVoiceChatLoggedIn(self):
        self._SystemMenu__RebuildAudioAndChatPanel()



    def OnVoiceChatLoggedOut(self):
        self._SystemMenu__RebuildAudioAndChatPanel()



    def __RebuildAudioAndChatPanel(self):
        if self.sr.audioinited == 0:
            return 
        for each in self.sr.audiopanels:
            each.Flush()

        self.sr.audioinited = 0
        self.Audioandchat()



    def ReloadCommands(self, key = None):
        if not key:
            key = self.sr.currentShortcutTabKey
        self.sr.currentShortcutTabKey = key
        scrolllist = []
        for c in uicore.cmd.commandMap.GetAllCommands():
            if c.category and c.category != key:
                continue
            data = util.KeyVal()
            data.cmdname = c.name
            data.context = uicore.cmd.GetCategoryContext(c.category)
            shortcutString = c.GetShortcutAsString() or '<color=%s>(%s)</color>' % (util.Color(0.5, 0.5, 0.5).GetHex(), mls.UI_GENERIC_NONE)
            data.label = '%s<t>%s' % (c.GetDescription(), shortcutString)
            data.locked = c.isLocked
            data.refreshcallback = self.ReloadCommands
            scrolllist.append(listentry.Get('CmdListEntry', data=data))

        self.sr.active_cmdscroll.Load(contentList=scrolllist, headers=[mls.UI_GENERIC_COMMAND, mls.UI_GENERIC_SHORTCUT], scrollTo=self.sr.active_cmdscroll.GetScrollProportion())



    def RestoreShortcuts(self, *args):
        uicore.cmd.RestoreDefaults()
        self.ReloadCommands()



    def EditCommand(self, cmdName):
        uicore.cmd.EditCmd(cmdName)
        self.ReloadCommands()



    def ClearCommand(self, cmdName):
        uicore.cmd.ClearMappedCmd(cmdName)
        self.ReloadCommands()



    def Abouteve(self):
        if self.sr.abouteveinited:
            return 
        parent = uiutil.GetChild(self.sr.wnd, 'about eve_container')
        self.sr.messageArea = uicls.Edit(parent=parent, padLeft=8, padRight=8, readonly=1)
        self.sr.messageArea.AllowResizeUpdates(0)
        html = mls.UI_SYSMENU_CREDITS2 % {'title': cfg.GetMessage('ReleaseTitle').text,
         'subtitle': cfg.GetMessage('ReleaseSubtitle').text,
         'version': '%s.%s' % (boot.keyval['version'].split('=', 1)[1], boot.build),
         'year': util.FmtDate(blue.os.GetTime())[:4],
         'evecredits': mls.UI_SYSMENU_EVECREDITS}
        self.sr.messageArea.LoadHTML(html)
        self.sr.abouteveinited = 1



    def ValidateData(self, entries):
        valid = []
        for rec in entries:
            if rec[0] not in ('checkbox', 'combo', 'slider', 'button'):
                continue
            if eve.session.charid:
                valid.append(rec)
            elif len(rec) > 1:
                if rec[1] is None:
                    valid.append(rec)
                    continue
                (cfgName, prefsType, defaultValue,) = rec[1]
                if type(prefsType) is tuple:
                    if prefsType[0] == 'char':
                        if eve.session.charid:
                            valid.append(rec)
                    elif prefsType[0] == 'user':
                        if eve.session.userid:
                            valid.append(rec)
                    else:
                        valid.append(rec)
                else:
                    valid.append(rec)

        return valid



    def ParseData(self, entries, parent, validateEntries = 1):
        if validateEntries:
            validEntries = self.ValidateData(entries)
            if not validEntries:
                return 
        for rec in entries:
            if validateEntries and rec[0] in ('checkbox', 'combo', 'slider', 'button') and rec not in validEntries:
                continue
            if rec[0] == 'topcontainer':
                c = uicls.Container(name='container', align=uiconst.TOTOP, height=rec[1], parent=parent)
                if len(rec) > 2:
                    c.name = rec[2]
            elif rec[0] == 'toppush':
                uicls.Container(name='toppush', align=uiconst.TOTOP, height=rec[1], parent=parent)
            elif rec[0] == 'leftpush':
                uicls.Container(name='leftpush', align=uiconst.TOLEFT, width=rec[1], parent=parent)
            elif rec[0] == 'rightpush':
                uicls.Container(name='rightpush', align=uiconst.TORIGHT, width=rec[1], parent=parent)
            elif rec[0] == 'button':
                btnpar = uicls.Container(name='buttonpar', align=uiconst.TOTOP, height=24, parent=parent)
                args = None
                if len(rec) > 4:
                    args = rec[4]
                uicls.Button(parent=btnpar, label=rec[2], func=rec[3], args=args)
            elif rec[0] == 'header':
                if len(parent.children) > 1:
                    containerHeader = uix.GetContainerHeader(rec[1], parent, xmargin=-5)
                    containerHeader.padTop = 4
                    containerHeader.padBottom = 2
                else:
                    uix.GetContainerHeader(rec[1], parent, xmargin=1, bothlines=0)
                    uicls.Container(name='leftpush', align=uiconst.TOLEFT, width=6, parent=parent)
                    uicls.Container(name='rightpush', align=uiconst.TORIGHT, width=6, parent=parent)
                    uicls.Container(name='toppush', align=uiconst.TOTOP, height=2, parent=parent)
            elif rec[0] == 'text':
                t = uicls.Label(name='sysheader', text=rec[1], parent=parent, align=uiconst.TOTOP, padTop=2, padBottom=2, state=uiconst.UI_NORMAL)
                if len(rec) > 2:
                    self.sr.Set(rec[2], t)
            elif rec[0] == 'line':
                uicls.Line(parent=parent, align=uiconst.TOTOP, padLeft=-5, padRight=-5, color=(1.0, 1.0, 1.0, 0.25))
                uicls.Container(name='toppush', align=uiconst.TOTOP, height=6, parent=parent)
            elif rec[0] == 'checkbox':
                (cfgName, prefsType, defaultValue,) = rec[1]
                label = rec[2]
                checked = self.GetSettingsValue(cfgName, prefsType, defaultValue)
                value = None
                if len(rec) > 3 and rec[3] is not None:
                    value = rec[3]
                    checked = bool(checked == value)
                group = None
                if len(rec) > 4:
                    group = rec[4]
                hint = None
                if len(rec) > 5:
                    hint = rec[5]
                focus = None
                if len(rec) > 6:
                    focus = rec[6]
                cb = uicls.Checkbox(text=label, parent=parent, configName=cfgName, retval=value, checked=checked, groupname=group, callback=self.OnCheckBoxChange, prefstype=prefsType)
                if len(rec) > 7:
                    disabled = rec[7]
                    if disabled:
                        cb.Disable()
                if focus:
                    uicore.registry.SetFocus(cb)
                cb.sr.hint = hint
                cb.sr.label.linespace = 9
                cb.RefreshHeight()
                self.tempStuff.append(cb)
            elif rec[0] == 'combo':
                (cfgName, prefsType, defaultValue,) = rec[1]
                if prefsType:
                    defaultValue = self.GetSettingsValue(cfgName, prefsType, defaultValue)
                label = rec[2]
                options = rec[3]
                labelleft = 0
                if len(rec) > 4:
                    labelleft = rec[4]
                hint = None
                if len(rec) > 5:
                    hint = rec[5]
                focus = None
                if len(rec) > 6:
                    focus = rec[6]
                cont = uicls.Container(name='comboCont', parent=parent, align=uiconst.TOTOP, height=18)
                combo = uicls.Combo(label=label, parent=cont, options=options, name=cfgName, select=defaultValue, callback=self.OnComboChange, labelleft=labelleft, align=uiconst.TOTOP)
                if focus:
                    uicore.registry.SetFocus(combo)
                combo.parent.hint = hint
                combo.SetHint(hint)
                combo.parent.state = uiconst.UI_NORMAL
                uicls.Container(name='toppush', align=uiconst.TOTOP, height=6, parent=parent)
                if len(rec) > 7:
                    if rec[7]:
                        combo.Disable()
            elif rec[0] == 'slider':
                (cfgName, prefsType, defaultValue,) = rec[1]
                label = rec[2]
                (minVal, maxVal,) = rec[3]
                labelWidth = 0
                labelAlign = uiconst.RELATIVE
                step = None
                if len(rec) > 4:
                    lw = rec[4]
                    if lw is not None:
                        labelWidth = lw
                        labelAlign = uiconst.TOLEFT
                if len(rec) > 5:
                    step = rec[5]
                self.AddSlider(parent, rec[1], minVal, maxVal, label, height=10, labelAlign=labelAlign, labelWidth=labelWidth, startValue=defaultValue, step=step)




    def OnSetCameraSliderValue(self, value, *args):
        if getattr(self, 'cameraOffset', None) is None:
            self.cameraSlider = uiutil.FindChild(self, 'cameraOffset')
        if getattr(self, 'cameraSlider', None) is not None:
            hint = self.GetCameraOffsetHintText(value)
            self.cameraSlider.hint = self.cameraSlider.parent.hint = hint
            if not getattr(self, 'cameraOffsetTextAdded', 0):
                self.AddCameraOffsetHint(self.cameraSlider)
                self.cameraOffsetTextAdded = 1
        settings.user.ui.cameraOffset = value
        sm.GetService('sceneManager').CheckCameraOffsets()



    def OnSetIncarnaCameraSliderValue(self, value, *args):
        if getattr(self, 'incarnaCameraOffset', None) is None:
            self.incarnaCameraSlider = uiutil.FindChild(self, 'incarnaCameraOffset')
        if getattr(self, 'incarnaCameraSlider', None) is not None:
            hint = self.GetCameraOffsetHintText(value, incarna=True)
            self.incarnaCameraSlider.hint = self.incarnaCameraSlider.parent.hint = hint
            if not getattr(self, 'incarnaCameraOffsetTextAdded', 0):
                self.AddCameraOffsetHint(self.incarnaCameraSlider)
                self.incarnaCameraOffsetTextAdded = 1
        settings.user.ui.incarnaCameraOffset = value
        sm.GetService('cameraClient').CheckCameraOffsets()



    def OnSetIncarnaCameraMouseLookSpeedSliderValue(self, value, *args):
        if getattr(self, 'incarnaCameraMouseLookSpeedSlider', None) is None:
            self.incarnaCameraMouseSpeedSlider = uiutil.FindChild(self, 'incarnaCameraMouseLookSpeedSlider')
        if getattr(self, 'incarnaCameraMouseSpeedSlider', None) is not None:
            hint = self.GetCameraMouseSpeedHintText(value)
            self.incarnaCameraMouseSpeedSlider.hint = self.incarnaCameraMouseSpeedSlider.parent.hint = hint
            if not getattr(self, 'incarnaCameraMouseLookSpeedTextAdded', 0):
                self.AddCameraMouseLookSpeedHint(self.incarnaCameraMouseSpeedSlider)
                self.incarnaCameraMouseLookSpeedTextAdded = 1
        valueToUse = cameras.MOUSE_LOOK_SPEED
        if value < 0:
            value = abs(value)
            value += 1.0
            valueToUse = valueToUse / value
        elif value > 0:
            value += 1.0
            valueToUse *= value
        settings.user.ui.incarnaCameraMouseLookSpeed = valueToUse
        sm.GetService('cameraClient').CheckMouseLookSpeed()



    def AddCameraMouseLookSpeedHint(self, whichOne):
        p = whichOne.parent
        uicls.Label(name='slower', text=mls.UI_SYSMENU_SLOWERLABEL, parent=p, align=uiconst.TOPLEFT, autowidth=1, autoheight=1, top=10, uppercase=1, fontsize=9, letterspace=2, color=(1.0, 1.0, 1.0, 0.75))
        uicls.Label(name='faster', text=mls.UI_SYSMENU_FASTERLABEL, parent=p, align=uiconst.TOPRIGHT, autowidth=1, autoheight=1, top=10, uppercase=1, fontsize=9, letterspace=2, color=(1.0, 1.0, 1.0, 0.75))
        uicls.Line(name='centerLine', parent=p, width=1, height=12, align=uiconst.CENTER, left=1)
        p.parent.hint = mls.UI_SYSMENU_CAMERASPEED_HINT
        p.state = p.parent.state = uiconst.UI_NORMAL



    def AddCameraOffsetHint(self, whichOne):
        p = whichOne.parent
        uicls.Label(name='left', text=mls.UI_SYSMENU_CAMERACENTER_LEFT, parent=p, align=uiconst.TOPLEFT, autowidth=1, autoheight=1, top=10, uppercase=1, fontsize=9, letterspace=2, color=(1.0, 1.0, 1.0, 0.75))
        uicls.Label(name='right', text=mls.UI_SYSMENU_CAMERACENTER_RIGHT, parent=p, align=uiconst.TOPRIGHT, autowidth=1, autoheight=1, top=10, uppercase=1, fontsize=9, letterspace=2, color=(1.0, 1.0, 1.0, 0.75))
        uicls.Line(name='centerLine', parent=p, width=1, height=12, align=uiconst.CENTER, left=1)
        p.parent.hint = mls.UI_SYSMENU_CAMERACENTER_HINT
        p.state = p.parent.state = uiconst.UI_NORMAL



    def GetCameraMouseSpeedHintText(self, value):
        if value == 0:
            return mls.UI_GENERIC_DEFAULT
        else:
            if value < 0:
                value = abs(value) + 1.0
                return mls.UI_SYSMENU_SLOWER % {'amount': str(round(value, 1))}
            value += 1.0
            return mls.UI_SYSMENU_FASTER % {'amount': str(round(value, 1))}



    def GetCameraOffsetHintText(self, value, incarna = False):
        if incarna:
            value *= 100
        if value == 0:
            return mls.UI_SYSMENU_CAMERACENTER_CENTERED
        else:
            if value < 0:
                return '%s %s %s' % (mls.UI_SYSMENU_CAMERACENTER_LEFT, str(abs(int(value))), '%')
            return '%s %s %s' % (mls.UI_SYSMENU_CAMERACENTER_RIGHT, str(abs(int(value))), '%')



    def GetSettingsValue(self, cfgName, prefsType, defaultValue):
        if not prefsType:
            return defaultValue
        return util.GetAttrs(settings, *prefsType).Get(cfgName, defaultValue)



    def Generic(self):
        if self.sr.genericinited:
            return 
        parent = uiutil.GetChild(self.sr.wnd, 'generic_container')
        fontWidthOps = [(mls.UI_SYSMENU_CONDENSED, 'condensed'), (mls.UI_SYSMENU_NORMAL, 'normal'), (mls.UI_SYSMENU_EXPANDED, 'expanded')]
        actionbtnOps = [(mls.UI_GENERIC_LEFTMOUSEBUTTON, 0), (mls.UI_GENERIC_MIDDLEMOUSEBUTTON, 2)]
        menufontsizeOps = [('9', 9),
         ('10', 10),
         ('11', 11),
         ('12', 12),
         ('13', 13)]
        snapOps = [(mls.UI_SYSMENU_DONTSNAP, 0),
         ('3', 3),
         ('6', 6),
         ('12', 12),
         ('24', 24)]
        column = uicls.Container(name='col1', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
        column.isTabOrderGroup = 1
        uicls.Frame(parent=column)
        if settings.user.ui.Get('fontWFactor', 'normal') not in ('condensed', 'normal', 'expanded'):
            settings.user.ui.Set('fontWFactor', 'normal')
        if settings.public.generic.Get('showintro2', None) is None:
            settings.public.generic.Set('showintro2', prefs.GetValue('showintro2', 1))
        menusData = [('header', mls.UI_GENERIC_GENERAL),
         ('checkbox', ('showintro2', ('public', 'generic'), 1), mls.UI_LOGIN_SHOWINTROMOVIE2),
         ('checkbox', ('showSessionTimer', ('user', 'ui'), 0), mls.UI_SYSMENU_SHOWSESSIONTIMER),
         ('checkbox', ('rebootOnDisconnect', ('user', 'ui'), 1), mls.UI_SYSMENU_REBOOTCLIENTONDISCONNECT),
         ('checkbox', ('hdScreenshots', ('user', 'ui'), 0), mls.UI_SYSMENU_ENABLEHIGHQSHOTS),
         ('checkbox', ('windowidentification', ('user', 'ui'), 0), mls.UI_SYSMENU_SHOWWINDOWIDENTIFICATION),
         ('toppush', 4),
         ('combo',
          ('cmenufontsize', ('user', 'ui'), 10),
          mls.UI_SYSMENU_CONTEXTMENUFONTSIZE,
          menufontsizeOps,
          LEFTPADDING),
         ('combo',
          ('fontWFactor', ('user', 'ui'), 'normal'),
          mls.UI_SYSMENU_FONTWIDTH,
          fontWidthOps,
          LEFTPADDING),
         ('header', mls.UI_SYSMENU_WINDOWS),
         ('checkbox', ('stackwndsonshift', ('user', 'ui'), 0), mls.UI_SYSMENU_ONLYSTACKWINDOWSIFSHIFTPRESSED),
         ('checkbox', ('useexistinginfownd', ('user', 'ui'), 1), mls.UI_SYSMENU_TRYUSEEXSISTINGINFOWIN),
         ('checkbox', ('lockwhenpinned', ('user', 'windows'), 0), mls.UI_SYSMENU_LOCKWHENPINNED),
         ('toppush', 4),
         ('combo',
          ('snapdistance', ('user', 'windows'), 12),
          mls.UI_SYSMENU_WINDOWSNAPDISTANCE,
          snapOps,
          LEFTPADDING)]
        self.ParseData(menusData, column)
        lst = []
        if lst:
            uicls.Container(name='toppush', align=uiconst.TOTOP, height=4, parent=column)
            uix.GetContainerHeader(mls.UI_SYSMENU_EXPERIMENTAL, column, xmargin=-5)
            uicls.Container(name='toppush', align=uiconst.TOTOP, height=2, parent=column)
            scroll = uicls.Scroll(parent=column)
            scroll.name = 'experimentalFeatures'
            scroll.HideBackground()
            scrollList = []
            for each in lst:
                scrollList.append(listentry.Get('Button', {'label': each['label'],
                 'caption': each['caption'],
                 'OnClick': each['OnClick'],
                 'args': (each['args'],),
                 'singleline': 0}))

            scroll.Load(contentList=scrollList)
        if len(column.children) == 1:
            column.Close()
        column = uicls.Container(name='column', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
        column.isTabOrderGroup = 1
        uicls.Frame(parent=column)
        atOps = []
        for i in xrange(13):
            if i == 1:
                atOps.append((mls.UI_GENERIC_ONE_TARGET, i))
            else:
                atOps.append((mls.UI_GENERIC_NUM_TARGET % {'num': i}, i))

        stationData = (('header', mls.UI_SHARED_HELP),
         ('checkbox', ('showTutorials', ('char', 'ui'), 1), mls.UI_SYSMENU_SHOWTUTORIALS),
         ('checkbox', ('showWelcomPages', ('char', 'ui'), 0), mls.UI_SYSMENU_SHOWWELCOMEPAGES),
         ('header', mls.UI_GENERIC_STATION),
         ('checkbox', ('stationservicebtns', ('user', 'ui'), 0), mls.UI_SYSMENU_SMALLSTATIONSERVICEBUTTONS),
         ('checkbox', ('dockshipsanditems', ('user', 'windows'), 0), mls.UI_SYSMENU_MERGEITEMSANDSHIPSINTOSTATIONPANEL))
        self.ParseData(stationData, column)
        inflightData = (('header', mls.UI_TUTORIAL_INFLIGHT),
         ('checkbox', ('damageMessages', ('user', 'ui'), 1), mls.UI_SYSMENU_DAMAGEMESSAGESONOFF),
         ('checkbox', ('damageMessagesNoDamage', ('user', 'ui'), 1), mls.UI_SYSMENU_DAMAGEMESSAGESONOFF_NODAMAGE),
         ('checkbox', ('damageMessagesMine', ('user', 'ui'), 1), mls.UI_SYSMENU_DAMAGEMESSAGES_MINE),
         ('checkbox', ('damageMessagesEnemy', ('user', 'ui'), 1), mls.UI_SYSMENU_DAMAGEMESSAGES_ENEMY),
         ('checkbox', ('damageMessagesSimple', ('user', 'ui'), 0), mls.UI_SYSMENU_DAMAGEMESSAGES_SIMPLE),
         ('checkbox',
          ('notifyMessagesEnabled', ('user', 'ui'), 1),
          mls.UI_SYSMENU_ENABLENOTIFYMESSAGES,
          None,
          None,
          mls.UI_SYSMENU_ENABLEEWARMESSAGES_TOOLTIP),
         ('checkbox', ('targetCrosshair', ('user', 'ui'), 1), mls.UI_SYSMENU_TARGETCROSSHAIR),
         ('toppush', 4),
         ('combo',
          ('autoTargetBack', ('user', 'ui'), 1),
          mls.UI_SYSMENU_AUTOTARGETBACKTARGETS,
          atOps,
          LEFTPADDING),
         ('combo',
          ('actionmenuBtn', ('user', 'ui'), 0),
          mls.UI_SYSMENU_EXPANDACTIONMENU,
          actionbtnOps,
          LEFTPADDING))
        self.ParseData(inflightData, column)
        if settings.user.ui.Get('damageMessages', 1) == 0:
            for each in ('damageMessagesNoDamage', 'damageMessagesMine', 'damageMessagesEnemy', 'damageMessagesSimple'):
                cb = uiutil.FindChild(column, each)
                if cb:
                    cb.state = uiconst.UI_HIDDEN

        optionalUpgradeData = [('header', mls.UI_OPTIONAL_UPGRADE)]
        patchService = sm.StartService('patch')
        upgradeInfo = patchService.GetServerUpgradeInfo()
        bottomPar = uicls.Container(name='bottomPar', parent=None, align=uiconst.TOALL)
        bottomBtnPar = uicls.Container(name='bottomBtnPar', parent=bottomPar, align=uiconst.CENTERTOP, height=26)
        if upgradeInfo is not None:
            n = nasty.GetAppDataCompiledCodePath()
            if (n.build or boot.build) < upgradeInfo.build:
                optionalUpgradeData.append(('text', mls.UI_OPTIONAL_UPGRADE_AVAILABLE))
                detailsBtn = uicls.Button(parent=bottomBtnPar, label=mls.UI_GENERIC_DETAILS, func=self.GoToOptionalUpgradeDetails, args=(), pos=(0, 0, 0, 0))
                installBtn = uicls.Button(parent=bottomBtnPar, label=mls.UI_CMD_INSTALL, func=self.InstallOptionalUpgradeClick, args=(), pos=(detailsBtn.width + 2,
                 0,
                 0,
                 0))
                bottomBtnPar.width = detailsBtn.width + installBtn.width
        if nasty.IsRunningWithOptionalUpgrade():
            optionalUpgradeData.append(('text', mls.UI_RUNNING_AN_OPTIONAL_UPGRADE))
            uninstallBtn = uicls.Button(parent=bottomBtnPar, label=mls.UI_UNINSTALL, func=self.UnInstallOptionalUpgradeClick, args=(), pos=(0, 0, 0, 0))
            bottomBtnPar.width = uninstallBtn.width
        if len(optionalUpgradeData) > 1:
            self.ParseData(optionalUpgradeData, column, validateEntries=False)
        column.children.append(bottomPar)
        if len(column.children) == 1:
            column.Close()
        if eve.session.userid:
            column = uicls.Container(name='col1', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
            column.isTabOrderGroup = 1
            uicls.Frame(parent=column)
            sidepush = 120
            (main, backgroundcolor, component, componentsub,) = sm.GetService('window').GetWindowColors()
            (mr, mg, mb, ma,) = main
            (br, bg, bb, ba,) = backgroundcolor
            (cr, cg, cb, ca,) = component
            (csr, csg, csb, csa,) = componentsub
            colors = self.colors[:]
            colors.sort()
            select = self.FindColor(main, self.colors)
            if not select:
                colors.insert(0, (mls.UI_SYSMENU_CUSTOMCOL, main))
            bgcolors = self.backgroundcolors[:]
            bgcolors.sort()
            bgselect = self.FindColor(backgroundcolor, self.backgroundcolors)
            if not bgselect:
                bgcolors.insert(0, (mls.UI_SYSMENU_CUSTOMCOL, backgroundcolor))
            ccolors = self.components[:]
            ccolors.sort()
            cselect = self.FindColor(component, self.components)
            if not cselect:
                ccolors.insert(0, (mls.UI_SYSMENU_CUSTOMCOL, component))
            cscolors = self.componentsubs[:]
            cscolors.sort()
            csselect = self.FindColor(componentsub, self.componentsubs)
            if not csselect:
                cscolors.insert(0, (mls.UI_SYSMENU_CUSTOMCOL, componentsub))
            colorData = [('header', mls.CHAR_SKILL_LAYOUT),
             ('toppush', 2),
             ('checkbox', ('linkColorCombos', ('user', 'ui'), 0), mls.UI_SYSMENU_EASYTHEMESELECTION),
             ('header', mls.UI_SYSMENU_WINDOWCOL),
             ('toppush', 4),
             ('combo',
              ('color', None, select),
              mls.UI_SYSMENU_PRESETS,
              colors,
              sidepush),
             ('slider',
              ('wnd_color_r', None, mr),
              mls.UI_GENERIC_COLORRED,
              (0.0, 1.0),
              sidepush),
             ('slider',
              ('wnd_color_g', None, mg),
              mls.UI_GENERIC_COLORGREEN,
              (0.0, 1.0),
              sidepush),
             ('slider',
              ('wnd_color_b', None, mb),
              mls.UI_GENERIC_COLORBLUE,
              (0.0, 1.0),
              sidepush),
             ('slider',
              ('wnd_color_a', None, ma),
              mls.UI_GENERIC_COLORTRANSP,
              (0.0, 1.0),
              sidepush),
             ('toppush', 4),
             ('header', mls.UI_SYSMENU_BACKGRCOLOR),
             ('toppush', 4),
             ('combo',
              ('backgroundcolor', None, bgselect),
              mls.UI_SYSMENU_PRESETS,
              bgcolors,
              sidepush),
             ('slider',
              ('wnd_backgroundcolor_r', None, br),
              mls.UI_GENERIC_COLORRED,
              (0.0, 1.0),
              sidepush),
             ('slider',
              ('wnd_backgroundcolor_g', None, bg),
              mls.UI_GENERIC_COLORGREEN,
              (0.0, 1.0),
              sidepush),
             ('slider',
              ('wnd_backgroundcolor_b', None, bb),
              mls.UI_GENERIC_COLORBLUE,
              (0.0, 1.0),
              sidepush),
             ('slider',
              ('wnd_backgroundcolor_a', None, ba),
              mls.UI_GENERIC_COLORTRANSP,
              (0.0, 1.0),
              sidepush),
             ('toppush', 4),
             ('header', mls.UI_GENERIC_HEADERSUBHEADERCOLOR),
             ('toppush', 4),
             ('combo',
              ('component', None, cselect),
              mls.UI_SYSMENU_PRESETS,
              ccolors,
              sidepush),
             ('combo',
              ('componentsub', None, csselect),
              mls.UI_SYSMENU_PRESETS,
              cscolors,
              sidepush)]
            self.ParseData(colorData, column)
            if len(column.children) == 1:
                column.Close()
        self.sr.genericinited = 1



    def InstallOptionalUpgradeClick(self):
        patchService = sm.StartService('patch')
        upgrade = patchService.GetServerUpgradeInfo()
        if upgrade is not None:
            self.CloseMenuClick()
            patchService.DownloadOptionalUpgrade(upgrade)



    def UnInstallOptionalUpgradeClick(self):
        answer = eve.Message('CompiledCodeAskToRemove', {}, uiconst.YESNO)
        if answer == uiconst.ID_YES:
            sm.StartService('patch').CleanupOptionalUpgrades()



    def GoToOptionalUpgradeDetails(self):
        url = sm.StartService('patch').OptionalUpgradeGetDetailsURL()
        blue.os.ShellExecute(url)



    def Audioandchat(self):
        if self.sr.audioinited:
            return 
        parent = uiutil.GetChild(self.sr.wnd, 'audioandchat_container')
        if self.sr.audiopanels is None or len(self.sr.audiopanels) == 0:
            self.sr.audiopanels = []
            column = uicls.Container(name='column', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
            column.isTabOrderGroup = 1
            self.sr.audiopanels.append(column)
        else:
            column = self.sr.audiopanels[0]
        uicls.Frame(parent=column, idx=0)
        labelWidth = 125
        audioSvc = sm.GetService('audio')
        enabled = audioSvc.IsActivated()
        turretSuppressed = audioSvc.GetTurretSuppression()
        audioData = (('header', mls.UI_SYSMENU_AUDIOENGSETTINGS),
         ('checkbox', ('audioEnabled', ('public', 'audio'), enabled), mls.UI_SYSMENU_AUDIOENABLED),
         ('header', mls.UI_SYSMENU_VOLUMELEVEL),
         ('slider',
          ('eveampGain', ('public', 'audio'), 0.4),
          mls.UI_SYSMENU_MUSICLEVEL,
          (0.0, 1.0),
          labelWidth),
         ('slider',
          ('uiGain', ('public', 'audio'), 0.4),
          mls.UI_SYSMENU_UISOUNDLEVEL,
          (0.0, 1.0),
          labelWidth),
         ('slider',
          ('evevoiceGain', ('public', 'audio'), 0.9),
          mls.UI_SYSMENU_VOICELEVEL,
          (0.0, 1.0),
          labelWidth),
         ('slider',
          ('worldVolume', ('public', 'audio'), 0.4),
          mls.UI_SYSMENU_WORLDLEVEL,
          (0.0, 1.0),
          labelWidth),
         ('slider',
          ('masterVolume', ('public', 'audio'), 0.4),
          mls.UI_SYSMENU_MASTERLEVEL,
          (0.0, 1.0),
          labelWidth),
         ('checkbox', ('suppressTurret', ('public', 'audio'), turretSuppressed), mls.UI_SYSMENU_SUPPRESSTURRETS))
        self.ParseData(audioData, column)
        if len(self.sr.audiopanels) < 2:
            col2 = uicls.Container(name='column2', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
            col2.isTabOrderGroup = 1
            self.sr.audiopanels.append(col2)
        else:
            col2 = self.sr.audiopanels[1]
        uicls.Frame(parent=col2, idx=0)
        voiceChatMenuAvailable = boot.region != 'optic'
        if sm.GetService('vivox').LoggedIn() and voiceChatMenuAvailable:
            keybindOptions = sm.GetService('vivox').GetAvailableKeyBindings()
            try:
                outputOps = [ (each[1], each[0]) for each in sm.GetService('vivox').GetAudioOutputDevices() ]
            except:
                log.LogException()
                sys.exc_clear()
                outputOps = []
            try:
                inputOps = [ (each[1], each[0]) for each in sm.GetService('vivox').GetAudioInputDevices() ]
            except:
                log.LogException()
                sys.exc_clear()
                inputOps = []
            joinedChannels = sm.GetService('vivox').GetJoinedChannels()
            voiceHeader = mls.UI_SYSMENU_VOICESETTINGS
            voiceServerInfo = sm.GetService('vivox').GetServerInfo()
            if voiceServerInfo:
                voiceHeader += ', server: ' + voiceServerInfo
            vivoxData = [('header', voiceHeader),
             ('checkbox',
              ('voiceenabled', ('user', 'audio'), 1),
              mls.UI_SYSMENU_EVEVOICEENABLED,
              None,
              None,
              mls.UI_SYSMENU_EVEVOICEENABLED_TOOLTIP),
             ('checkbox',
              ('talkMutesGameSounds', ('user', 'audio'), 0),
              mls.UI_SYSMENU_TALKMUTESGAMESOUNDS,
              None,
              None,
              mls.UI_SYSMENU_TALKMUTESGAMESOUNDS_TOOLTIP),
             ('checkbox',
              ('listenMutesGameSounds', ('user', 'audio'), 0),
              mls.UI_SYSMENU_LISTENMUTESGAMESOUNDS,
              None,
              None,
              mls.UI_SYSMENU_LISTENMUTESGAMESOUNDS_TOOLTIP),
             ('header', mls.UI_SYSMENU_CHANNELSPECIFICSETTINGS),
             ('checkbox',
              ('talkMoveToTopBtn', ('user', 'audio'), 0),
              mls.UI_SYSMENU_TALKMOVELASTSPEAKERTOTOP,
              None,
              None,
              mls.UI_SYSMENU_TALKMOVELASTSPEAKERTOTOP_TOOLTIP),
             ('checkbox',
              ('talkAutoJoinFleet', ('user', 'audio'), 1),
              mls.UI_SYSMENU_AUTOJOINFLEETVOICE,
              None,
              None,
              mls.UI_SYSMENU_AUTOJOINFLEETVOICE_TOOLTIP),
             ('checkbox',
              ('talkChannelPriority', ('user', 'audio'), 0),
              mls.UI_SYSMENU_CHANNELPRIORITIZE,
              None,
              None,
              mls.UI_SYSMENU_CHANNELPRIORITIZE_TOOLTIP),
             ('header', mls.UI_GENERIC_CONFIGURATION),
             ('toppush', 4),
             ('combo',
              ('talkBinding', ('user', 'audio'), 4),
              mls.UI_SYSMENU_TALKKEY,
              keybindOptions,
              labelWidth),
             ('combo',
              ('TalkOutputDevice', ('user', 'audio'), 0),
              mls.UI_SYSMENU_TALKOUTPUT,
              outputOps,
              labelWidth),
             ('combo',
              ('TalkInputDevice', ('user', 'audio'), 0),
              mls.UI_SYSMENU_TALKDEVICE,
              inputOps,
              labelWidth),
             ('slider',
              ('TalkMicrophoneVolume', ('user', 'audio'), sm.GetService('vivox').defaultMicrophoneVolume),
              mls.UI_SYSMENU_TALKVOLUME,
              (0.0, 1.0),
              labelWidth),
             ('toppush', 4)]
            self.ParseData(vivoxData, col2)
            inputmeterpar = uicls.Container(name='inputmeter', align=uiconst.TOTOP, height=12, parent=col2)
            if not sm.GetService('vivox').GetSpeakingChannel() == 'Echo':
                uix.GetContainerHeader(mls.UI_SYSMENU_TALKMETERINACTIVE, col2, 0)
            else:
                subpar = uicls.Container(name='im_sub', align=uiconst.TORIGHT, width=col2.width - labelWidth - 11, parent=inputmeterpar)
                uicls.Frame(parent=subpar, width=-1)
                self.maxInputMeterWidth = subpar.width - 4
                self.sr.inputmeter = uicls.Fill(parent=subpar, left=2, top=2, width=1, height=inputmeterpar.height - 4, align=uiconst.RELATIVE, color=(1.0, 1.0, 1.0, 0.25))
                uicls.Label(text=mls.UI_SYSMENU_TALKMETER, parent=inputmeterpar, fontsize=9, letterspace=2, uppercase=1, top=2, state=uiconst.UI_NORMAL)
                sm.GetService('vivox').RegisterIntensityCallback(self)
                sm.GetService('vivox').StartAudioTest()
            if sm.GetService('vivox').GetSpeakingChannel() == 'Echo':
                echoBtnLabel = mls.UI_SYSMENU_TALKSTOPECHOTEST
                echoTextString = mls.UI_SYSMENU_TALKECHOINSTRUCTIONS
            else:
                echoBtnLabel = mls.UI_SYSMENU_TALKSTARTECHOTEST
                echoTextString = ''
            btnPar = uicls.Container(name='push', align=uiconst.TOTOP, height=30, parent=col2)
            self.echoBtn = uicls.Button(parent=btnPar, label=echoBtnLabel, func=self.JoinLeaveEchoChannel, align=uiconst.CENTER)
            uicls.Container(name='push', align=uiconst.TOTOP, height=8, parent=col2)
            self.echoText = uicls.Label(text=echoTextString, parent=col2, align=uiconst.TOTOP, fontsize=9, letterspace=1, uppercase=1, autowidth=False, state=uiconst.UI_NORMAL)
        elif eve.session.userid and voiceChatMenuAvailable:
            vivoxData = (('header', mls.UI_SYSMENU_VOICESETTINGS),
             ('checkbox',
              ('voiceenabled', ('user', 'audio'), 1),
              mls.UI_SYSMENU_EVEVOICEENABLED,
              None,
              None,
              mls.UI_SYSMENU_EVEVOICEENABLED_TOOLTIP),
             ('checkbox',
              ('talkMutesGameSounds', ('user', 'audio'), 0),
              mls.UI_SYSMENU_TALKMUTESGAMESOUNDS,
              None,
              None,
              mls.UI_SYSMENU_TALKMUTESGAMESOUNDS_TOOLTIP),
             ('checkbox',
              ('listenMutesGameSounds', ('user', 'audio'), 0),
              mls.UI_SYSMENU_LISTENMUTESGAMESOUNDS,
              None,
              None,
              mls.UI_SYSMENU_LISTENMUTESGAMESOUNDS_TOOLTIP),
             ('header', mls.UI_SYSMENU_CHANNELSPECIFICSETTINGS),
             ('text', mls.UI_SYSMENU_VOICESETTINGS_NOTCONNECTED))
            self.ParseData(vivoxData, col2, 0)
        elif voiceChatMenuAvailable:
            vivoxData = (('header', mls.UI_SYSMENU_VOICESETTINGS),
             ('text', mls.UI_SYSMENU_CHAT_NOTLOGGEDIN),
             ('header', mls.UI_SYSMENU_CHANNELSPECIFICSETTINGS),
             ('text', mls.UI_SYSMENU_VOICESETTINGS_NOTCONNECTED))
            self.ParseData(vivoxData, col2, 0)
        self.sr.audioinited = 1
        if voiceChatMenuAvailable:
            if len(self.sr.audiopanels) < 3:
                col3 = uicls.Container(name='column3', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
                col3.isTabOrderGroup = 1
                self.sr.audiopanels.append(col3)
            else:
                col3 = self.sr.audiopanels[2]
        else:
            col3 = col2
        uicls.Frame(parent=col3, idx=0)
        dblClickUserOps = [(mls.UI_CMD_SHOWINFO, 0), (mls.UI_CMD_STARTCONVERSATION, 1)]
        self.ParseData((('header', mls.UI_GENERIC_CHAT),), col3, 0)
        if eve.session.userid:
            chatData = (('checkbox', ('logchat', ('user', 'ui'), 1), mls.UI_SYSMENU_LOGCHATTOFILE),
             ('checkbox', ('autoRejectInvitations', ('user', 'ui'), 0), mls.UI_SYSMENU_AUTOREJECTINVITATIONS),
             ('toppush', 4),
             ('combo',
              ('dblClickUser', ('user', 'ui'), 0),
              mls.UI_SYSMENU_ONDOUBLECLICK,
              dblClickUserOps,
              labelWidth),
             ('toppush', 4))
            if voiceChatMenuAvailable and sm.GetService('vivox').LoggedIn():
                chatData += (('header', mls.UI_SYSMENU_CHAT_AUTOJOIN_HEADER),
                 ('checkbox', ('chatJoinCorporationChannelOnLogin', ('user', 'ui'), 0), mls.UI_SYSMENU_CHAT_AUTOJOIN_CORPORATION),
                 ('checkbox', ('chatJoinAllianceChannelOnLogin', ('user', 'ui'), 0), mls.UI_SYSMENU_CHAT_AUTOJOIN_ALLIANCE),
                 ('header', mls.UI_SYSMENU_VOICEFONT_HEADER))
        else:
            chatData = (('text', mls.UI_SYSMENU_CHAT_NOTLOGGEDIN),)
        self.ParseData(chatData, col3, 0)
        if eve.session.charid and voiceChatMenuAvailable and sm.GetService('vivox').LoggedIn():
            args = {}
            args['currentVoiceFont'] = settings.char.ui.Get('voiceFontName', mls.UI_GENERIC_NONE)
            currentVoiceFontText = uicls.Label(text=mls.UI_SYSMENU_CURRENT_VOICEFONT % args, parent=col3, align=uiconst.TOTOP, fontsize=9, letterspace=1, uppercase=1, autowidth=False, top=4)
            btnPar = uicls.Container(name='push', align=uiconst.TOTOP, height=30, parent=col3)
            self.voiceFontBtn = uicls.Button(parent=btnPar, label=mls.UI_SYSMENU_CHANGE_VOICEFONT, func=self.SelectVoiceFontDialog, args=(), align=uiconst.CENTER)
            uicls.Container(name='push', align=uiconst.TOTOP, height=8, parent=col3)



    def SelectVoiceFontDialog(self):
        wnd = sm.GetService('window').GetWindow('VoiceFontSelection')
        if wnd is None:
            wnd = sm.GetService('window').GetWindow('VoiceFontSelection', 1, decoClass=form.VoiceFontSelectionWindow)
            wnd.ShowModal()



    def Displayandgraphics(self):
        if self.sr.displayandgraphicsinited:
            return 
        parent = uiutil.GetChild(self.sr.wnd, 'displayandgraphics_container')
        column = uicls.Container(name='column', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
        column.isTabOrderGroup = 1
        uicls.Frame(parent=column, idx=0)
        self.sr.monitorsetup = column
        self.InitDeviceSettings()
        self.ProcessDeviceSettings()
        if eve.session.userid:
            column = uicls.Container(name='column', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
            column.isTabOrderGroup = 1
            uicls.Frame(parent=column, idx=0)
            self.sr.graphicssetup = column
        column = uicls.Container(name='column', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
        column.isTabOrderGroup = 1
        uicls.Frame(parent=column, idx=0)
        self.sr.graphicssetup2 = column
        self.ProcessGraphicsSettings()
        self.sr.displayandgraphicsinited = 1



    def ProcessGraphicsSettings(self, status = None):
        where = self.sr.Get('graphicssetup', None)
        where2 = self.sr.Get('graphicssetup2', None)
        deviceSvc = sm.GetService('device')
        if where:
            uiutil.FlushList(where.children[1:])
        if where2:
            uiutil.FlushList(where2.children[1:])
        leftCounter = 0
        startdownload = False
        resume = False
        cancel = False
        pause = False
        install = False
        message = None
        manualDownload = False
        graphicsData = []
        graphicsData2 = [('header', mls.UI_SYSMENU_GRAPHIC_CONTENT_SETTINGS), ('text', mls.UI_SYSMENU_GRAPHIC_CONTENT_SETTING_DESCRIPTION), ('line',)]
        shaderQualityOptions = [(mls.UI_GENERIC_LOW, 1), (mls.UI_GENERIC_HIGH, 3)]
        try:
            shaderQualityMenu = [('combo',
              ('shaderQuality', None, prefs.GetValue('shaderQuality', deviceSvc.GetDefaultShaderQuality())),
              mls.UI_SYSMENU_SHADER_QUALITY,
              shaderQualityOptions,
              LEFTPADDING,
              mls.UI_SYSMENU_SHADER_QUALITY_TOOLTIP)]
        except:
            log.LogException()
        textureQualityOptions = [(mls.UI_GENERIC_LOW, 2), (mls.UI_GENERIC_MEDIUM, 1), (mls.UI_GENERIC_HIGH, 0)]
        textureQualityMenu = [('combo',
          ('textureQuality', None, prefs.GetValue('textureQuality', deviceSvc.GetDefaultTextureQuality())),
          mls.UI_SYSMENU_TEXTURE_QUALITY,
          textureQualityOptions,
          LEFTPADDING,
          mls.UI_SYSMENU_TEXTURE_QUALITY_TOOLTIP)]
        lodQualityOptions = [(mls.UI_GENERIC_LOW, 1), (mls.UI_GENERIC_MEDIUM, 2), (mls.UI_GENERIC_HIGH, 3)]
        lodQualityMenu = [('combo',
          ('lodQuality', None, prefs.GetValue('lodQuality', deviceSvc.GetDefaultLodQuality())),
          mls.UI_SYSMENU_LOD_QUALITY,
          lodQualityOptions,
          LEFTPADDING,
          mls.UI_SYSMENU_LOD_QUALITY_TOOLTIP)]
        shadowQualityOptions = [(mls.UI_GENERIC_DISABLED, 0), (mls.UI_GENERIC_LOW, 1), (mls.UI_GENERIC_HIGH, 2)]
        shadowQualityMenu = [('combo',
          ('shadowQuality', None, prefs.GetValue('shadowQuality', deviceSvc.GetDefaultShadowQuality())),
          mls.UI_SYSMENU_SHADOWQUALITY,
          shadowQualityOptions,
          LEFTPADDING,
          mls.UI_SYSMENU_SHADOWS_TOOLTIP)]
        interiorQualityOptions = [(mls.UI_GENERIC_LOW, 0), (mls.UI_GENERIC_MEDIUM, 1), (mls.UI_GENERIC_HIGH, 2)]
        interiorQualityMenu = [('combo',
          ('interiorGraphicsQuality', None, prefs.GetValue('interiorGraphicsQuality', deviceSvc.GetDefaultInteriorGraphicsQuality())),
          mls.UI_SYSMENU_INTERIOREFFECTS,
          interiorQualityOptions,
          LEFTPADDING,
          mls.UI_SYSMENU_INTERIOREFFECTS_TOOLTIP), ('line',)]
        graphicsData2 += [('checkbox',
          ('resourceCacheEnabled', None, bool(prefs.GetValue('resourceCacheEnabled', deviceSvc.GetDefaultResourceState()))),
          mls.UI_SYSMENU_CACHE_ENABLED,
          None,
          None,
          mls.UI_SYSMENU_CACHE_TOOLTIP)]
        if deviceSvc.IsHDRSupported():
            graphicsData2 += [('checkbox',
              ('hdrEnabled', None, bool(prefs.GetValue('hdrEnabled', deviceSvc.GetDefaultHDRState()))),
              mls.UI_SYSMENU_HDR_ENABLED,
              None,
              None,
              mls.UI_SYSMENU_HDR_TOOLIP)]
        depthEffectsEnabled = prefs.GetValue('depthEffectsEnabled', deviceSvc.GetDefaultDepthEffectsEnabled())
        if deviceSvc.SupportsDepthEffects():
            graphicsData2 += [('checkbox',
              ('depthEffectsEnabled', None, depthEffectsEnabled),
              mls.UI_SYSMENU_DEPTHEFFECTS,
              None,
              None,
              mls.UI_SYSMENU_DEPTHEFFECTS_TOOLTIP)]
        graphicsData2 += [('checkbox',
          ('loadstationenv', None, prefs.GetValue('loadstationenv', 1)),
          mls.UI_SYSMENU_LOADSTATIONENVIRONMENT,
          None,
          None,
          mls.UI_SYSMENU_LOADSTATIONENVIRONMENT_TOOLTIP)]
        devicSvc = sm.GetService('device')
        hdrEnabled = prefs.GetValue('hdrEnabled', deviceSvc.GetDefaultHDRState())
        formats = [self.settings.BackBufferFormat, self.settings.AutoDepthStencilFormat, trinity.TRIFMT_A16B16G16R16F]
        options = deviceSvc.GetMultiSampleQualityOptions(self.settings, formats)
        graphicsData2.append(('combo',
         ('Anti-Aliasing', None, prefs.GetValue('antiAliasing', 0)),
         mls.UI_SYSMENU_ANTIALIASING,
         options,
         LEFTPADDING,
         mls.UI_SYSMENU_ANTIALIASING_TOOLTIP))
        postProcessingQualityOptions = [(mls.UI_GENERIC_NONE, 0), (mls.UI_GENERIC_LOW, 1), (mls.UI_GENERIC_HIGH, 2)]
        if deviceSvc.IsBloomSupported():
            graphicsData2 += [('combo',
              ('postProcessingQuality', None, prefs.GetValue('postProcessingQuality', deviceSvc.GetDefaultPostProcessingQuality())),
              mls.UI_SYSMENU_POSTPROCESS,
              postProcessingQualityOptions,
              LEFTPADDING,
              mls.UI_SYSMENU_POSTPROCESS_TOOLIP)]
        graphicsData2 += shaderQualityMenu
        graphicsData2 += textureQualityMenu
        graphicsData2 += lodQualityMenu
        graphicsData2 += shadowQualityMenu
        graphicsData2 += interiorQualityMenu
        if eve.session.userid:
            graphicsData += [('header', mls.UI_GENERIC_EFFECTS),
             ('checkbox',
              ('turretsEnabled', ('user', 'ui'), 1),
              mls.UI_SYSMENU_TURRETEFFECTS,
              None,
              None,
              mls.UI_SYSMENU_TURRETEFFECTS_TOOLTIP),
             ('checkbox',
              ('effectsEnabled', ('user', 'ui'), 1),
              mls.UI_GENERIC_EFFECTS,
              None,
              None,
              mls.UI_GENERIC_EFFECTS_TOOLTIP),
             ('checkbox',
              ('missilesEnabled', ('user', 'ui'), 1),
              mls.UI_SYSMENU_MISSILEEFFECTS,
              None,
              None,
              mls.UI_GENERIC_EFFECTS_TOOLTIP),
             ('checkbox',
              ('cameraShakeEnabled', ('user', 'ui'), 1),
              mls.UI_SYSMENU_CAMERASHAKE,
              None,
              None,
              mls.UI_SYSMENU_CAMERASHAKE_TOOLTIP),
             ('checkbox',
              ('explosionEffectsEnabled', ('user', 'ui'), 1),
              mls.UI_SYSMENU_EXPLOSIONEFFECTS,
              None,
              None,
              mls.UI_SYSMENU_EXPLOSIONEFFECTS_TOOLTIP),
             ('checkbox',
              ('droneModelsEnabled', ('user', 'ui'), 1),
              mls.UI_SYSMENU_DRONEMODELS,
              None,
              None,
              mls.UI_SYSMENU_DRONEMODELS_TOOLTIP),
             ('header', mls.UI_SYSMENU_MISC),
             ('checkbox',
              ('lod', ('user', 'ui'), 1),
              mls.UI_SYSMENU_USELOD,
              None,
              None,
              mls.UI_SYSMENU_USELOD_TOOLTIP),
             ('checkbox',
              ('sunOcclusion', ('public', 'device'), 1),
              mls.UI_SYSMENU_SUNISOCCLUDEDBYSHIPS,
              None,
              None,
              mls.UI_SYSMENU_SUNISOCCLUDEDBYSHIPS_TOOLTIP),
             ('checkbox',
              ('advancedCamera', ('user', 'ui'), 0),
              mls.UI_SYSMENU_ADVCAMMENU,
              None,
              None,
              mls.UI_SYSMENU_ADVCAMMENU_TOOLTIP)]
            if sm.GetService('lightFx').IsLightFxSupported():
                graphicsData += [('checkbox',
                  ('LightFxEnabled', ('user', 'ui'), 1),
                  mls.UI_SYSMENU_ALIENFX,
                  None,
                  None,
                  mls.UI_SYSMENU_ALIENFX_TOOLTIP)]
        graphicsData += (('header', mls.UI_SYSMENU_CHARACTER_HEADER),)
        disabled = not trinity.GetShaderModel().startswith('SM_3')
        currentFastCharacterCreationValue = bool(prefs.GetValue('fastCharacterCreation', deviceSvc.GetDefaultFastCharacterCreation())) or disabled
        currentClothSimValue = prefs.GetValue('charClothSimulation', deviceSvc.GetDefaultClothSimEnabled()) and not disabled
        graphicsData += [('checkbox',
          ('fastCharacterCreation', None, currentFastCharacterCreationValue),
          mls.UI_SYSMENU_FASTCHARACTERS,
          None,
          None,
          mls.UI_SYSMENU_FASTCHARACTERS_TOOLTIP,
          None,
          disabled)]
        graphicsData += [('checkbox',
          ('charClothSimulation', None, currentClothSimValue),
          mls.UI_SYSMENU_CLOTHSIM,
          None,
          None,
          mls.UI_SYSMENU_CLOTHSIM_TOOLTIP,
          None,
          disabled)]
        charTextureQualityOptions = [(mls.UI_GENERIC_LOW, 2), (mls.UI_GENERIC_MEDIUM, 1), (mls.UI_GENERIC_HIGH, 0)]
        graphicsData += [('combo',
          ('charTextureQuality', None, prefs.GetValue('charTextureQuality', deviceSvc.GetDefaultCharTextureQuality())),
          mls.UI_SYSMENU_TEXTURE_QUALITY,
          charTextureQualityOptions,
          LEFTPADDING,
          mls.UI_SYSMENU_TEXTURE_QUALITY_TOOLTIP)]
        if message is not None:
            graphicsData2 += [('text', message, 'dlMessage')]
        if where:
            self.ParseData(graphicsData, where, validateEntries=0)
        if where2:
            self.ParseData(graphicsData2, where2, validateEntries=0)
            optSettingsPar = uicls.Container(name='optSettingsPar', parent=where2, align=uiconst.TOTOP, height=24)
            btn = uicls.Button(parent=optSettingsPar, label=mls.UI_SYSMENU_OPTIMIZE_SETTINGS, func=self.OpenOptimizeSettings, args=(), align=uiconst.CENTERTOP)
            bottomBtnPar = uicls.Container(name='bottomBtnPar', parent=where2, align=uiconst.CENTERBOTTOM, height=32)
            bottomLeftCounter = 0
            btn = uicls.Button(parent=bottomBtnPar, label=mls.UI_GENERIC_APPLY, func=self.ApplyGraphicsSettings, args=(), pos=(bottomLeftCounter,
             0,
             0,
             0))
            bottomLeftCounter += btn.width + 2
            btn = uicls.Button(parent=bottomBtnPar, label=mls.UI_SYSMENU_RESETGRAPHICSSETTINGS, func=self.ResetGraphicsSettings, args=(), pos=(bottomLeftCounter,
             0,
             0,
             0))
            bottomLeftCounter += btn.width + 2
            bottomBtnPar.width = bottomLeftCounter



    def OpenOptimizeSettings(self):
        optimizeWnd = sm.StartService('window').GetWindow('optimizesettings')
        if optimizeWnd is None:
            self.optimizeWnd = weakref.proxy(sm.StartService('window').GetWindow('optimizesettings', 1, decoClass=form.OptimizeSettingsWindow))
            self.optimizeWnd.ShowModal()
            self.ApplyGraphicsSettings()
            sm.GetService('sceneManager').ApplyClothSimulationSettings()
        else:
            self.optimizeWnd = weakref.proxy(optimizeWnd)



    def ResetGraphicsSettings(self):
        deviceSvc = sm.GetService('device')
        prefs.hdrEnabled = deviceSvc.GetDefaultHDRState()
        prefs.postProcessingQuality = deviceSvc.GetDefaultPostProcessingQuality()
        prefs.resourceCacheEnabled = deviceSvc.GetDefaultResourceState()
        prefs.textureQuality = deviceSvc.GetDefaultTextureQuality()
        prefs.shaderQuality = deviceSvc.GetDefaultShaderQuality()
        prefs.lodQuality = deviceSvc.GetDefaultLodQuality()
        prefs.fastCharacterCreation = deviceSvc.GetDefaultFastCharacterCreation()
        prefs.charTextureQuality = deviceSvc.GetDefaultCharTextureQuality()
        prefs.optimizeSettings = 0
        prefs.depthEffectsEnabled = deviceSvc.GetDefaultDepthEffectsEnabled()
        prefs.incarnaGraphicsQuality = deviceSvc.GetDefaultInteriorGraphicsQuality()
        prefs.shadowQuality = deviceSvc.GetDefaultShadowQuality()
        settings.public.device.Set('MultiSampleType', 0)
        settings.public.device.Set('MultiSampleQuality', 0)
        settings.user.ui.Set('turretsEnabled', 1)
        settings.user.ui.Set('effectsEnabled', 1)
        settings.user.ui.Set('missilesEnabled', 1)
        settings.user.ui.Set('lod', 1)
        settings.public.device.Set('sunOcclusion', 1)
        settings.user.ui.Set('advancedCamera', 0)
        settings.user.ui.Set('cameraOffset', 0)
        settings.user.ui.Set('loadstationenv', 1)
        settings.user.ui.Set('incarnaCameraOffset', 1)
        settings.user.ui.Set('incarnaCameraInvertY', 0)
        settings.user.ui.Set('incarnaCameraMouseSmooth', 1)
        settings.user.ui.Set('incarnaCameraMouseLookSpeed', cameras.MOUSE_LOOK_SPEED)
        self.ApplyGraphicsSettings()



    def ApplyGraphicsSettings(self):
        if not self.settings:
            return 
        deviceSvc = sm.GetService('device')
        deviceSet = deviceSvc.GetSettings()
        dev = trinity.GetDevice()
        changes = []
        shadowQuality = prefs.GetValue('shadowQuality', deviceSvc.GetDefaultShadowQuality())
        textureQuality = prefs.GetValue('textureQuality', deviceSvc.GetDefaultTextureQuality())
        lodQuality = prefs.GetValue('lodQuality', deviceSvc.GetDefaultLodQuality())
        shaderQuality = prefs.GetValue('shaderQuality', deviceSvc.GetDefaultShaderQuality())
        hdrEnabled = prefs.GetValue('hdrEnabled', deviceSvc.GetDefaultHDRState())
        msType = getattr(self.settings, 'MultiSampleType', deviceSet.MultiSampleType)
        msQuality = getattr(self.settings, 'MultiSampleQuality', deviceSet.MultiSampleQuality)
        interiorGraphics = prefs.GetValue('interiorGraphicsQuality', deviceSvc.GetDefaultInteriorGraphicsQuality())
        fastCharacterCreation = prefs.GetValue('fastCharacterCreation', 0)
        charTextureQuality = prefs.GetValue('charTextureQuality', deviceSvc.GetDefaultCharTextureQuality())
        postProcessingQuality = prefs.GetValue('postProcessingQuality', deviceSvc.GetDefaultPostProcessingQuality())
        if sm.GetService('sceneManager').postProcessingQuality != postProcessingQuality:
            changes.append('postProcessingQuality')
        if sm.GetService('sceneManager').shadowQuality != shadowQuality:
            changes.append('shadowQuality')
        if deviceSvc.GetShaderModel(shaderQuality) != trinity.GetShaderModel():
            changes.append('shaderQuality')
        oldCacheSize = blue.motherLode.maxMemUsage
        newCacheSize = deviceSvc.SetResourceCacheSize()
        if oldCacheSize != newCacheSize:
            changes.append('resourceCache')
        if bool(dev.hdrEnable) != bool(hdrEnabled):
            dev.hdrEnable = hdrEnabled
            changes.append('HDR')
        oldVisThreshold = trinity.settings.GetValue('eveSpaceSceneVisibilityThreshold')
        if lodQuality == 1:
            trinity.settings.SetValue('eveSpaceSceneVisibilityThreshold', 15.0)
            trinity.settings.SetValue('eveSpaceSceneLowDetailThreshold', 140.0)
            trinity.settings.SetValue('eveSpaceSceneMediumDetailThreshold', 480.0)
        elif lodQuality == 2:
            trinity.settings.SetValue('eveSpaceSceneVisibilityThreshold', 6.0)
            trinity.settings.SetValue('eveSpaceSceneLowDetailThreshold', 70.0)
            trinity.settings.SetValue('eveSpaceSceneMediumDetailThreshold', 240.0)
        elif lodQuality == 3:
            trinity.settings.SetValue('eveSpaceSceneVisibilityThreshold', 3.0)
            trinity.settings.SetValue('eveSpaceSceneLowDetailThreshold', 35.0)
            trinity.settings.SetValue('eveSpaceSceneMediumDetailThreshold', 120.0)
        if oldVisThreshold != trinity.settings.GetValue('eveSpaceSceneVisibilityThreshold'):
            changes.append('LOD')
        if textureQuality != dev.mipLevelSkipCount:
            changes.append('textureQuality')
        if uicore.layer.charactercreation.isopen:
            if uicore.layer.charactercreation.fastCharacterCreation != fastCharacterCreation:
                uicore.layer.charactercreation.fastCharacterCreation = fastCharacterCreation
                changes.append('fastCharacterCreation')
        if 'character' in sm.services:
            if charTextureQuality != sm.GetService('character').textureQuality:
                changes.append('charTextureQuality')
        if prefs.GetValue('antiAliasing', 0) != sm.GetService('sceneManager').antiAliasingQuality:
            changes.append('antiAliasing')
        if sm.GetService('sceneManager').interiorGraphicsQuality != interiorGraphics:
            changes.append('interiorGraphics')
        resetTriggered = False
        if 'textureQuality' in changes:
            dev.mipLevelSkipCount = textureQuality
            dev.RefreshDeviceResources()
            resetTriggered = True
        if 'shaderQuality' in changes:
            message = uicls.Message(className='Message', parent=uicore.layer.modal, name='msgDeviceReset')
            message.ShowMsg(mls.UI_SYSMENU_APPLYSHADERMODELWAIT)
            blue.synchro.Sleep(200)
            trinity.SetShaderModel(deviceSvc.GetShaderModel(shaderQuality))
            message.Close()
            resetTriggered = True
        if not resetTriggered and 'HDR' in changes:
            deviceSvc.ResetDevice()
        if not self.closing:
            self.ProcessGraphicsSettings()
        if changes:
            sm.ScatterEvent('OnGraphicSettingsChanged', changes)



    def Shortcuts(self):
        if self.sr.shortcutsinited:
            return 
        parent = uiutil.GetChild(self.sr.wnd, 'shortcuts_container')
        parent.Load = self.LoadShortcutTabs
        parent.Flush()
        tabs = []
        for category in uicore.cmd.GetCommandCategoryNames():
            tabs.append([category,
             None,
             parent,
             category])

        self.sr.shortcutTabs = uicls.TabGroup(name='tabs', parent=parent, padBottom=5, tabs=tabs, groupID='tabs', autoselecttab=1, idx=0)
        col2 = uicls.Container(name='column2', parent=parent)
        col2.isTabOrderGroup = 1
        shortcutoptions = uicls.Container(name='options', align=uiconst.TOBOTTOM, height=30, top=0, parent=col2, padding=(5, 0, 5, 0))
        btns = [(mls.UI_CMD_EDITSHORTCUT, self.OnEditShortcutBtnClicked, None), (mls.UI_CMD_CLEARSHORTCUT, self.OnClearShortcutBtnClicked, None)]
        btnGroup = uicls.ButtonGroup(btns=btns, parent=shortcutoptions, line=False, subalign=uiconst.BOTTOMLEFT)
        btn = uicls.Button(parent=shortcutoptions, label=mls.UI_CMD_DEFAULTS, func=self.RestoreShortcuts, top=0, align=uiconst.BOTTOMRIGHT)
        self.sr.active_cmdscroll = uicls.Scroll(name='availscroll', align=uiconst.TOALL, parent=col2, padLeft=8, multiSelect=False, id='active_cmdscroll')
        self.sr.shortcutsinited = 1



    def OnEditShortcutBtnClicked(self, *args):
        selected = self.sr.active_cmdscroll.GetSelected()
        if not selected:
            return 
        self.EditCommand(selected[0].cmdname)



    def OnClearShortcutBtnClicked(self, *args):
        selected = self.sr.active_cmdscroll.GetSelected()
        if not selected:
            return 
        self.ClearCommand(selected[0].cmdname)



    def LoadShortcutTabs(self, key):
        self.ReloadCommands(key)



    def Resetsettings(self, reload = 0):
        if self.sr.resetsettingsinited:
            return 
        parent = uiutil.GetChild(self.sr.wnd, 'reset settings_container')
        scrollTo = None
        suppressScrollTo = None
        defaultScrollTo = None
        if reload:
            scroll = uiutil.FindChild(parent, 'tutorialResetScroll')
            if scroll:
                scrollTo = scroll.GetScrollProportion()
            scroll = uiutil.FindChild(parent, 'suppressResetScroll')
            if scroll:
                suppressScrollTo = scroll.GetScrollProportion()
            scroll = uiutil.FindChild(parent, 'defaultResetScroll')
            if scroll:
                defaultScrollTo = scroll.GetScrollProportion()
        uix.Flush(parent)
        col1 = uicls.Container(name='col1', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
        col1.isTabOrderGroup = 1
        uicls.Frame(parent=col1)
        uix.GetContainerHeader(mls.UI_SYSMENU_RESETSUPPRESSMESSAGESETTINGS, col1, 0)
        scroll = uicls.Scroll(parent=col1)
        scroll.name = 'suppressResetScroll'
        scroll.HideBackground()
        scrollList = []
        i = 0
        for each in settings.user.suppress.GetValues().keys():
            label = self.GetConfigName(each)
            entry = listentry.Get('Button', {'label': label,
             'caption': mls.UI_CMD_RESET,
             'OnClick': self.ConfigBtnClick,
             'args': (each,),
             'singleline': 0})
            scrollList.append((label, entry))

        scrollList = uiutil.SortListOfTuples(scrollList)
        scroll.Load(contentList=scrollList, scrollTo=suppressScrollTo)
        col2 = uicls.Container(name='column2', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
        col2.isTabOrderGroup = 1
        uicls.Frame(parent=col2)
        uix.GetContainerHeader(mls.UI_SYSMENU_RESETTODEFAULT, col2, (0, 1)[(i >= 12)])
        scroll = uicls.Scroll(parent=col2)
        scroll.name = 'defaultsResetScroll'
        scroll.HideBackground()
        scrollList = []
        lst = [{'label': mls.UI_CMD_RESETDEFAULTWNDPOS,
          'caption': mls.UI_CMD_RESET,
          'OnClick': self.ResetBtnClick,
          'args': 'windows'},
         {'label': mls.UI_CMD_RESETDEFAULTWNDCOL,
          'caption': mls.UI_CMD_RESET,
          'OnClick': self.ResetBtnClick,
          'args': 'window color'},
         {'label': mls.UI_CMD_RESETJUKEBOXPLAYLIST,
          'caption': mls.UI_CMD_RESET,
          'OnClick': self.ResetBtnClick,
          'args': 'jukebox playlist'},
         {'label': mls.UI_CMD_CLEARALLSETTINGS,
          'caption': mls.UI_CMD_CLEAR,
          'OnClick': self.ResetBtnClick,
          'args': 'clear settings'},
         {'label': mls.UI_CMD_CLEARALLCACHEFILES,
          'caption': mls.UI_CMD_CLEAR,
          'OnClick': self.ResetBtnClick,
          'args': 'clear cache'},
         {'label': mls.UI_CMD_CLEARMAILCACHE,
          'caption': mls.UI_CMD_CLEAR,
          'OnClick': self.ResetBtnClick,
          'args': 'clear mail'}]
        if hasattr(sm.GetService('LSC'), 'spammerList'):
            lst.append({'label': mls.UI_CMD_CLEARISKSPAMMERLIST,
             'caption': mls.UI_CMD_CLEAR,
             'OnClick': self.ResetBtnClick,
             'args': 'clear iskspammers'})
        for each in lst:
            scrollList.append(listentry.Get('Button', {'label': each['label'],
             'caption': each['caption'],
             'OnClick': each['OnClick'],
             'args': (each['args'],),
             'singleline': 0}))

        scroll.Load(contentList=scrollList, scrollTo=suppressScrollTo)
        tutorials = sm.GetService('tutorial').GetTutorials()
        if tutorials:
            col3 = uicls.Container(name='column3', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
            col3.isTabOrderGroup = 1
            uicls.Frame(parent=col3)
            uix.GetContainerHeader(mls.UI_SYSMENU_RESETTUTORIALSTATE, col3, 0)
            scroll = uicls.Scroll(parent=col3)
            scroll.name = 'tutorialResetScroll'
            scroll.HideBackground()
            all = sm.GetService('tutorial').GetValidTutorials()
            scrollList = []
            for tutorialID in all:
                if tutorialID not in tutorials:
                    continue
                seqStat = sm.GetService('tutorial').GetSequenceStatus(tutorialID)
                if seqStat:
                    label = Tr(tutorials[tutorialID].tutorialName, 'tutorial.tutorials.tutorialName', tutorials[tutorialID].dataID)
                    entry = listentry.Get('Button', {'label': label,
                     'caption': mls.UI_CMD_RESET,
                     'OnClick': self.TutorialResetBtnClick,
                     'args': (tutorialID,),
                     'singleline': 0})
                    scrollList.append((label, entry))

            scrollList = uiutil.SortListOfTuples(scrollList)
            scroll.Load(contentList=scrollList, scrollTo=scrollTo)
        self.sr.resetsettingsinited = 1



    def Language(self):
        if self.sr.languageinited:
            return 
        parent = uiutil.GetChild(self.sr.wnd, 'language_container')
        if boot.region != 'optic' or eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            column = column1 = uicls.Container(name='col1', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
            column.isTabOrderGroup = 1
            uicls.Frame(parent=column)
            languageData = [('header', mls.UI_SYSMENU_LANGUAGE)]
            langs = sm.GetService('gameui').GetLanguages()
            for (languageID, languageName, translatedName,) in langs:
                languageData.append(('checkbox',
                 ('language', None, eve.session.languageID),
                 translatedName or languageName,
                 languageID,
                 'langgroup'))

            self.ParseData(languageData, column)
            if len(column.children) == 1:
                column.Close()
            column = uicls.Container(name='column', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
            column.isTabOrderGroup = 1
            uicls.Frame(parent=column)
            columnData = [('header', mls.UI_SYSMENU_INPUTMETHODEDITOR), ('checkbox', ('nativeIME', ('user', 'ui'), True), mls.UI_SYSMENU_USEEVEIME)]
            self.ParseData(columnData, column)
            if len(column.children) == 1:
                column.Close()
        column = uicls.Container(name='col1', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
        column.isTabOrderGroup = 1
        uicls.Frame(parent=column)
        columnData = [('header', mls.UI_SYSMENU_VOICEOPTIONS), ('checkbox', ('forceEnglishVoice', ('user', 'ui'), False), mls.UI_SYSMENU_VOICEFORCEENGLISH)]
        self.ParseData(columnData, column)
        if len(column.children) == 1:
            column.Close()
        self.sr.languageinited = 1



    def AddSlider(self, where, config, minval, maxval, header, hint = '', usePrefs = 0, width = 160, height = 14, labelAlign = None, labelWidth = 0, startValue = None, step = None):
        uicls.Container(name='push', align=uiconst.TOTOP, height=[16, 4][(labelAlign is not None)], parent=where)
        _par = uicls.Container(name=config[0] + '_slider', align=uiconst.TOTOP, height=height, state=uiconst.UI_PICKCHILDREN, parent=where)
        par = uicls.Container(name=config[0] + '_slider_sub', parent=_par)
        slider = xtriui.Slider(parent=par, width=height, height=height)
        if labelAlign is not None:
            labelParent = uicls.Container(name='labelparent', parent=_par, align=labelAlign, width=labelWidth, idx=0)
            lbl = uicls.Label(text='', parent=labelParent, width=labelWidth, autowidth=False, fontsize=9, letterspace=2, tabs=[labelWidth - 22], uppercase=1, state=uiconst.UI_NORMAL)
            lbl._tabMargin = 0
        else:
            lbl = uicls.Label(text='', parent=par, width=200, autowidth=False, top=-14, fontsize=9, letterspace=2, uppercase=1, state=uiconst.UI_NORMAL)
        lbl.state = uiconst.UI_PICKCHILDREN
        lbl.name = 'label'
        slider.label = lbl
        slider.GetSliderValue = self.GetSliderValue
        slider.SetSliderLabel = self.SetSliderLabel
        slider.Startup(config[0], minval, maxval, config, header, usePrefs=usePrefs, startVal=startValue)
        slider.name = config[0]
        slider.hint = hint
        if step:
            slider.SetIncrements([ val for val in range(int(minval), int(maxval + 1), step) ], 0)
        slider.EndSetSliderValue = self.EndSliderValue
        return slider



    def FindColorFromName(self, findColor, colors):
        for (colorName, color,) in colors:
            if colorName == findColor:
                return color




    def FindColor(self, findColor, colors):
        for (colorName, color,) in colors:
            i = 0
            for c in 'rgba':
                sval = '%.2f' % findColor[i]
                vval = '%.2f' % color[i]
                if sval != vval:
                    break
                i += 1
                if i == 4:
                    return findColor





    def EndSliderValue(self, slider, *args):
        if slider.name == 'TalkMicrophoneVolume':
            value = slider.GetValue()
            settings.user.audio.Set('TalkMicrophoneVolume', value)
            sm.GetService('vivox').SetMicrophoneVolume(value)



    def SetSliderLabel(self, label, idname, dname, value):
        if idname.startswith('wnd_'):
            label.text = '%s<t>%d' % (dname, value * 255)
        elif idname not in ('cameraOffset', 'incarnaCameraOffset', 'incarnaCameraMouseLookSpeedSlider'):
            label.text = '%s %.1f' % (dname, value)
        else:
            label.text = dname



    def GetSliderValue(self, idname, value, *args):
        if idname.startswith('wnd_'):
            self.UpdateUIColor(idname, value)
        elif idname == 'eveampGain':
            sm.GetService('jukebox').SetVolume(value)
        elif idname == 'masterVolume':
            sm.GetService('audio').SetMasterVolume(value, persist=False)
        elif idname == 'uiGain':
            sm.GetService('audio').SetUIVolume(value, persist=False)
        elif idname == 'worldVolume':
            sm.GetService('audio').SetWorldVolume(value, persist=False)
        elif idname == 'evevoiceGain':
            sm.GetService('audio').SetVoiceVolume(value, persist=False)
        elif idname == 'cameraOffset':
            self.OnSetCameraSliderValue(value)
        elif idname == 'incarnaCameraOffset':
            self.OnSetIncarnaCameraSliderValue(value)
        elif idname == 'incarnaCameraMouseLookSpeedSlider':
            self.OnSetIncarnaCameraMouseLookSpeedSliderValue(value)



    def OnCheckBoxChange(self, checkbox):
        if checkbox.data.has_key('config'):
            config = checkbox.data['config']
            if config == 'language':
                langID = checkbox.data['value']
                if boot.region == 'optic' and not eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
                    langID = 'ZH'
                self.setlanguageID = langID
                self.LanguageCheck()
            if config == 'lockwhenpinned':
                wnds = sm.GetService('window').GetValidWindows(getHidden=True)
                for wnd in wnds:
                    if wnd.IsPinned():
                        if checkbox.checked:
                            wnd.Lock()
                        else:
                            wnd.Unlock()

            if config == 'audioEnabled':
                if checkbox.checked:
                    sm.GetService('audio').Activate()
                else:
                    sm.GetService('audio').Deactivate()
            if config == 'suppressTurret':
                sm.StartService('audio').SetTurretSuppression(checkbox.checked)
            if config == 'damageMessages':
                idx = checkbox.parent.children.index(checkbox) + 1
                state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][settings.user.ui.Get('damageMessages', 1)]
                for i in xrange(4):
                    checkbox.parent.children[(idx + i)].state = state

            if config == 'windowidentification':
                sm.GetService('gameui').DoWindowIdentification()
            if config == 'targetCrosshair':
                sm.GetService('bracket').Reload()
            if config == 'advancedDevice':
                self.ProcessDeviceSettings(whatChanged='advancedDevice')
            if config == 'voiceenabled':
                if checkbox.checked:
                    if hasattr(self, 'voiceFontBtn'):
                        self.voiceFontBtn.Enable()
                    sm.GetService('vivox').Login()
                elif hasattr(self, 'voiceFontBtn'):
                    self.voiceFontBtn.Disable()
                sm.GetService('vivox').LogOut()
            if config == 'talkChannelPriority':
                if not checkbox.checked:
                    sm.GetService('vivox').StopChannelPriority()
            if config == 'hdrEnabled':
                if checkbox.checked:
                    prefs.hdrEnabled = 1
                    self.ProcessGraphicsSettings()
                else:
                    prefs.hdrEnabled = 0
                    self.ProcessGraphicsSettings()
            if config == 'depthEffectsEnabled':
                if checkbox.checked:
                    prefs.depthEffectsEnabled = 1
                    self.ProcessGraphicsSettings()
                else:
                    prefs.depthEffectsEnabled = 0
                    self.ProcessGraphicsSettings()
            if config == 'fastCharacterCreation':
                if checkbox.checked:
                    prefs.fastCharacterCreation = 1
                    self.ProcessGraphicsSettings()
                else:
                    prefs.fastCharacterCreation = 0
                    self.ProcessGraphicsSettings()
            if config == 'charClothSimulation':
                prefs.charClothSimulation = checkbox.checked
                sm.GetService('sceneManager').ApplyClothSimulationSettings()
            if config == 'bloomEnabled':
                if checkbox.checked:
                    prefs.bloomEnabled = 1
                    self.ProcessGraphicsSettings()
                else:
                    prefs.bloomEnabled = 0
                    self.ProcessGraphicsSettings()
            if config == 'resourceCacheEnabled':
                prefs.resourceCacheEnabled = bool(checkbox.checked)
                self.ProcessGraphicsSettings()
            if config == 'loadstationenv':
                prefs.SetValue('loadstationenv', 1 if checkbox.checked else 0)
                eve.Message('CustomInfo', {'info': mls.UI_SYSMENU_NEEDTOREENTERCQ})
            if config == 'turretsEnabled':
                if checkbox.checked:
                    sm.GetService('FxSequencer').EnableGuids(FxSequencer.fxTurretGuids)
                else:
                    sm.GetService('FxSequencer').DisableGuids(FxSequencer.fxTurretGuids)
            if config == 'effectsEnabled':
                candidateEffects = []
                for guid in FxSequencer.fxGuids:
                    if guid not in FxSequencer.fxTurretGuids and guid not in FxSequencer.fxProtectedGuids:
                        candidateEffects.append(guid)

                if len(candidateEffects) > 0:
                    if checkbox.checked:
                        sm.GetService('FxSequencer').EnableGuids(candidateEffects)
                    else:
                        sm.GetService('FxSequencer').DisableGuids(candidateEffects)



    def GetConfigName(self, suppression):
        configTranslation = {'AgtDelayMission': mls.UI_SYSMENU_CONFIRMDELAYMISSION,
         'AgtMissionOfferWarning': mls.UI_SYSMENU_AGENTMISSIONOFFERWARNING,
         'AgtMissionAcceptBigCargo': mls.UI_SYSMENU_AGENTMISSIONACCEPTBIGCARGO,
         'AgtDeclineMission': mls.UI_SYSMENU_AGENTMISSIONDECLINEWARNING,
         'AgtDeclineOnlyMission': mls.UI_SYSMENU_AGENTDECLINEONLYMISSIONWARNING,
         'AgtDeclineImportantMission': mls.UI_SYSMENU_AGENTDECLINEIMPORTANTMISSIONWARNING,
         'AgtDeclineMissionSequence': mls.UI_SYSMENU_AGENTDECLINEMISSIONSEQUENCEWARNING,
         'AgtQuitMission': mls.UI_SYSMENU_AGENTQUITMISSIONWARNING,
         'AgtQuitImportantMission': mls.UI_SYSMENU_AGENTQUITIMPORTANTMISSIONWARNING,
         'AgtQuitMissionSequence': mls.UI_SYSMENU_AGENTQUITMISSIONSEQUENCEWARNING,
         'AgtShare': mls.UI_SYSMENU_UI_AGTSHARE,
         'AgtNotShare': mls.UI_SYSMENU_UI_AGTNOTSHARE,
         'AskPartialCargoLoad': mls.UI_SYSMENU_PARTIALMOVEBECAUSEOFLIMITEDSPACE,
         'AidWithEnemiesEmpire2': mls.UI_SYSMENU_CONFIRMAIDINGAENEMYPLAYERINEMPIRESPACE,
         'AidOutlawEmpire2': mls.UI_SYSMENU_CONFIRMAIDINGANOUTLAWINEMPIRESPACE,
         'AidGlobalCriminalEmpire2': mls.UI_SYSMENU_CONFIRMAIDINGCRIMINALFLAGGEDPLAYERINEMPIRE,
         'AttackInnocentEmpire2': mls.UI_SYSMENU_CONFIRMATTACKINGOFANINNOCENTPLAYERINEMPIRESPACE,
         'AttackInnocentEmpireAbort1': mls.UI_SYSMENU_CONFIRMATTACKINGOFANINNOCENTPLAYERINEMPIRESPACE,
         'AttackGoodNPC2': mls.UI_SYSMENU_CONFIRMATTACKINGAGOODNPC,
         'AttackGoodNPCAbort1': mls.UI_SYSMENU_CONFIRMATTACKINGAGOODNPC,
         'AttackAreaEmpire3': mls.UI_SYSMENU_CONFIRMACTIVATIONOFAREAEFFECTMODULEINEMPIRESPACE,
         'AttackAreaEmpireAbort1': mls.UI_SYSMENU_CONFIRMACTIVATINGANAREAOFEFFECTMODULEINEMPIRESPACE,
         'AttackNonEmpire2': mls.UI_SYSMENU_CONFIRMATTACKINGPLAYEROWNEDSTUFFINNON,
         'AttackNonEmpireAbort1': mls.UI_SYSMENU_CONFIRMATTACKINGPLAYEROWNEDSTUFFINNON,
         'ConfirmOneWayItemMove': mls.UI_SYSMENU_CONFIRMONEWAYITEMMOVE,
         'ConfirmJumpToUnsafeSS': mls.UI_SYSMENU_CONFIRMJUMPTOUNSAFESOLARSYSTEM,
         'ConfirmJettison': mls.UI_SYSMENU_CONFIRMJETTISIONOFITEMS,
         'AskQuitGame': mls.UI_SYSMENU_CONFIRMQUITGAME,
         'facAcceptEjectMaterialLoss': mls.UI_SYSMENU_CONFIRMEJECTINGOFBPFROMFACTORY,
         'WarnDeleteFromAddressbook': mls.UI_SYSMENU_WARNWHENDELETINGFROMADDRESSBOOK,
         'ConfirmDeleteFolder': mls.UI_SYSMENU_CONFIRMDELETINGOFFOLDERS,
         'AskCancelContinuation': mls.UI_SYSMENU_CONFIRMMODIFYINCHARACTERCREATION,
         'ConfirmClearText': mls.UI_SYSMENU_CONFIRMCLEARTEXT,
         'ConfirmAbandonDrone': mls.UI_SYSMENU_CONFIRMABANDONDRONE,
         'QueueSaveChangesOnClose': mls.UI_SHARED_SQ_APPLYCHANGES}
        if configTranslation.has_key(suppression[9:]):
            txt = configTranslation[suppression[9:]]
        else:
            msg = cfg.GetMessage(suppression[9:], -1, onNotFound='pass')
            if msg:
                txt = msg.title
            else:
                txt = suppression[9:]
            log.LogWarn('Missing system menu config translation', suppression[9:])
        return txt



    def ConfigBtnClick(self, suppress, *args):
        try:
            settings.user.suppress.Delete(suppress)
            self.sr.resetsettingsinited = 0
            self.Resetsettings(1)
        except:
            log.LogException()
            sys.exc_clear()



    def TutorialResetBtnClick(self, tutorialID, btn):
        sm.GetService('tutorial').SetSequenceStatus(tutorialID, tutorialID, None, 'reset')
        self.sr.resetsettingsinited = 0
        self.Resetsettings(1)



    def TutorialDoneResetBtnClick(self, btn, *args):
        sm.GetService('tutorial').SetSequenceDoneStatus(btn.tutorialID, None, None)
        btn.state = uiconst.UI_HIDDEN



    def ResetBtnClick(self, reset, *args):
        uicore.cmd.Reset(reset)



    def QuitBtnClick(self, *args):
        uicore.cmd.CmdQuitGame()



    def LogOutBtnClick(self, *args):
        uicore.cmd.CmdLogoutGame()



    def ConvertETC(self, *args):
        KEY_LENGTH = 16

        def IsIllegal(key):
            if key == '':
                return True
            if len(key) != KEY_LENGTH:
                eve.Message('28DaysTooShort', {'num': KEY_LENGTH})
                return True
            return False


        if eve.session.stationid is None:
            raise UserError('28DaysConvertOnlyInStation')
        if eve.Message('28DaysConvertMessage', {}, uiconst.YESNO) != uiconst.ID_YES:
            return 
        name = ''
        ret = {'name': ''}
        while ret and IsIllegal(ret['name']):
            if ret:
                name = ret['name']
            ret = uix.NamePopup(mls.UI_SHARED_CONVERTETC, mls.UI_SHARED_TYPEINETC, name, maxLength=KEY_LENGTH)

        if not ret:
            return 
        sm.GetService('loading').ProgressWnd(mls.UI_SHARED_CONVERTINGETC, '.', 1, 2)
        try:
            sm.RemoteSvc('userSvc').ConvertETCToPilotLicence(ret['name'])

        finally:
            sm.GetService('loading').ProgressWnd(mls.UI_SHARED_CONVERTINGETC, '.', 2, 2)




    def RedeemItems(self, *args):
        self.CloseMenu()
        sm.StartService('redeem').OpenRedeemWindow(session.charid, session.stationid)



    def Petition(self, *args):
        self.CloseMenu()
        sm.GetService('petition').Show()



    def CloseMenu(self, *args):
        try:
            if getattr(self, 'closing', False):
                return 
            self.closing = 1
            if self.sr.wnd:
                self.sr.wnd.state = uiconst.UI_DISABLED
            if not getattr(self, 'inited', False):
                blue.pyos.synchro.Yield()
                uicore.layer.systemmenu.CloseView()
                if self and not self.dead:
                    self.closing = 0
                return 
            if eve.session.stationid:
                self.FadeBG(1.0, 0.0, 0, self.sr.bg, 250.0)
                blue.pyos.synchro.Yield()
            else:
                self.FadeBG(1.0, 0.0, 0, self.sr.bg, 250.0)
                blue.pyos.synchro.Yield()
            if self.sr.wnd:
                self.sr.wnd.state = uiconst.UI_HIDDEN

        finally:
            uicore.layer.systemmenu.CloseView()




    def LanguageCheck(self):
        setlanguageID = getattr(self, 'setlanguageID', None)
        if setlanguageID and setlanguageID != self.init_languageID:
            if boot.region == 'optic' and eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
                sm.RemoteSvc('authentication').SetLanguageID(setlanguageID)
                return 
            ret = eve.Message('ChangeLanguageReboot', {}, uiconst.YESNO)
            if ret == uiconst.ID_YES:
                sm.RemoteSvc('authentication').SetLanguageID(setlanguageID)
                prefs.languageID = setlanguageID
                appUtils.Reboot('language change')



    def StationUpdateCheck(self):
        if eve.session.stationid:
            lobbyReloaded = False
            if self.init_dockshipsanditems != settings.user.windows.Get('dockshipsanditems', 0):
                sm.GetService('station').LoadLobby()
                lobbyReloaded = True
                sm.GetService('neocom').UpdateMenu()
            if not lobbyReloaded and self.init_stationservicebtns != settings.user.ui.Get('stationservicebtns', 0):
                uthread.new(sm.GetService('station').LoadLobby)




class CmdListEntry(listentry.Generic):
    __guid__ = 'listentry.CmdListEntry'
    __nonpersistvars__ = []

    def Startup(self, *args):
        listentry.Generic.Startup(self, args)
        self.sr.lock = uicls.Icon(icon='ui_22_32_30', parent=self, size=20, align=uiconst.CENTERRIGHT, state=uiconst.UI_HIDDEN, hint=mls.UI_SYSMENU_LOCKEDSHORTCUTHINT, ignoreSize=1)



    def Load(self, node):
        listentry.Generic.Load(self, node)
        self.sr.command = node.cmdname
        self.sr.context = node.context
        self.sr.isLocked = node.locked
        self.sr.lock.state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][node.locked]



    def GetMenu(self):
        self.OnClick()
        if self.sr.isLocked:
            return []
        m = [(mls.UI_CMD_EDITSHORTCUT, self.Edit), (mls.UI_CMD_CLEARSHORTCUT, self.Clear)]
        return m



    def OnDblClick(self, *args):
        if not self.sr.isLocked:
            self.Edit()



    def Edit(self):
        uicore.cmd.EditCmd(self.sr.command, self.sr.context)
        self.RefreshCallback()



    def Clear(self):
        self.sr.selection.state = uiconst.UI_HIDDEN
        uicore.cmd.ClearMappedCmd(self.sr.command)
        self.RefreshCallback()



    def RefreshCallback(self):
        if self.sr.node.Get('refreshcallback', None):
            self.sr.node.refreshcallback()




class VoiceFontSelectionWindow(uicls.Window):
    __guid__ = 'form.VoiceFontSelectionWindow'
    __notifyevents__ = ['OnVoiceFontsReceived']

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetWndIcon('ui_9_64_16', mainTop=-10)
        args = {}
        args['currentVoiceFont'] = settings.char.ui.Get('voiceFontName', mls.UI_GENERIC_NONE)
        self.SetCaption(mls.UI_SYSMENU_CURRENT_VOICEFONT % args)
        self.SetMinSize([240, 150])
        self.MakeUnResizeable()
        self.sr.windowCaption = uicls.CaptionLabel(text=mls.UI_SYSMENU_VOICEFONT, parent=self.sr.topParent, align=uiconst.RELATIVE, left=70, top=15, state=uiconst.UI_DISABLED, fontsize=18)
        self.voiceFonts = None
        sm.RegisterNotify(self)
        uthread.new(self.Display)



    def OnVoiceFontsReceived(self, voiceFontList):
        self.voiceFonts = [(mls.UI_GENERIC_NONE, 0)]
        for voiceFont in voiceFontList:
            mlskey = 'UI_VOICEFONT_' + voiceFont[1].upper()
            if mls.HasLabel(mlskey):
                label = getattr(mls, mlskey)
            else:
                label = mlskey
            self.voiceFonts.append((label, voiceFont[0]))

        self.Display()



    def Display(self):
        self.height = 150
        self.width = 240
        uiutil.FlushList(self.sr.main.children[0:])
        self.sr.main = uiutil.GetChild(self, 'main')
        mainContainer = uicls.Container(name='mainContainer', parent=self.sr.main, align=uiconst.TOALL, padding=(3, 3, 3, 3))
        if self.voiceFonts is None:
            self.echoText = uicls.Label(text=mls.UI_SYSMENU_RECEIVINGVOICEFONTS, parent=mainContainer, align=uiconst.TOTOP, fontsize=9, letterspace=1, uppercase=1, autowidth=False, top=2, state=uiconst.UI_NORMAL)
            sm.GetService('vivox').GetAvailableVoiceFonts()
        else:
            idx = sm.GetService('vivox').GetVoiceFont()
            self.combo = uicls.Combo(label=mls.UI_SYSMENU_VOICEFONT, parent=mainContainer, options=self.voiceFonts, name='voicefont', idx=idx, callback=self.OnComboChange, labelleft=100, align=uiconst.TOTOP, padTop=5)
            self.combo.SetHint(mls.UI_SYSMENU_VOICEFONT)
            self.combo.parent.state = uiconst.UI_NORMAL
        btns = uicls.ButtonGroup(btns=[[mls.UI_CMD_APPLY,
          self.Apply,
          (),
          66], [mls.UI_CMD_CANCEL,
          self.CloseX,
          (),
          66]], parent=mainContainer, idx=0)



    def Apply(self, *args):
        settings.char.ui.Set('voiceFontName', self.combo.GetKey())
        sm.GetService('vivox').SetVoiceFont(self.combo.selectedValue)
        sm.ScatterEvent('OnVoiceFontChanged')
        self.CloseX(args)



    def OnComboChange(self, *args):
        pass




class OptimizeSettingsWindow(uicls.Window):
    __guid__ = 'form.OptimizeSettingsWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetWndIcon('ui_9_64_16', mainTop=-10)
        self.SetCaption(mls.UI_SYSMENU_OPTIMIZE_SETTINGS)
        self.SetMinSize([360, 240])
        self.MakeUnResizeable()
        self.sr.windowCaption = uicls.CaptionLabel(text=mls.UI_SYSMENU_OPTIMIZE_SETTINGS, parent=self.sr.topParent, align=uiconst.RELATIVE, left=70, top=15, state=uiconst.UI_DISABLED, fontsize=18)
        self.SetScope('all')
        main = self.sr.main
        optimizeSettingsOptions = [(mls.UI_SYSMENU_OPTIMIZE_SETTINGS_SELECT, None),
         (mls.UI_SYSMENU_OPTIMIZE_SETTINGS_MEMORY, 1),
         (mls.UI_SYSMENU_OPTIMIZE_SETTINGS_PERFORMANCE, 2),
         (mls.UI_SYSMENU_OPTIMIZE_SETTINGS_QUALITY, 3)]
        combo = self.combo = uicls.Combo(label='', parent=main, options=optimizeSettingsOptions, name='', select=None, callback=self.OnComboChange, labelleft=0, align=uiconst.TOTOP)
        combo.SetHint(mls.UI_SYSMENU_OPTIMIZE_SETTINGS_SELECT)
        combo.SetPadding(6, 0, 6, 0)
        self.messageArea = uicls.Edit(parent=main, readonly=1, hideBackground=1, padding=6)
        self.messageArea.AllowResizeUpdates(1)
        uicls.Frame(parent=self.messageArea, color=(0.4, 0.4, 0.4, 0.5))
        self.UpdateAlignmentAsRoot()
        self.messageArea.LoadHTML('<html><body>%s</body></html>' % mls.UI_SYSMENU_OPTIMIZE_SETTINGS_SELECT_INFO)
        btns = uicls.ButtonGroup(btns=[[mls.UI_CMD_APPLY,
          self.Apply,
          (),
          66], [mls.UI_CMD_CANCEL,
          self.CloseX,
          (),
          66]], parent=main, idx=0)
        return self



    def OnComboChange(self, *args):
        idx = args[2]
        info = {1: mls.UI_SYSMENU_OPTIMIZE_SETTINGS_MEMORY_INFO,
         2: mls.UI_SYSMENU_OPTIMIZE_SETTINGS_PERFORMANCE_INFO,
         3: mls.UI_SYSMENU_OPTIMIZE_SETTINGS_QUALITY_INFO}.get(idx, mls.UI_SYSMENU_OPTIMIZE_SETTINGS_SELECT_INFO)
        self.messageArea.LoadHTML('<html><body>%s</body></html>' % info)



    def Apply(self):
        if self.combo.selectedValue is None:
            return 
        value = self.combo.selectedValue
        if value == 3:
            prefs.SetValue('textureQuality', 0)
            prefs.SetValue('shaderQuality', 3)
            prefs.SetValue('shadowQuality', 2)
            prefs.SetValue('hdrEnabled', 1)
            prefs.SetValue('postProcessingQuality', 2)
            prefs.SetValue('resourceCacheEnabled', 0)
            prefs.SetValue('lodQuality', 3)
            prefs.SetValue('depthEffectsEnabled', sm.GetService('device').SupportsDepthEffects())
            prefs.SetValue('fastCharacterCreation', 0)
            prefs.SetValue('charClothSimulation', 1)
            prefs.SetValue('charTextureQuality', 0)
            if eve.session.userid:
                settings.user.ui.Set('droneModelsEnabled', 1)
                settings.user.ui.Set('effectsEnabled', 1)
                settings.user.ui.Set('missilesEnabled', 1)
                settings.user.ui.Set('explosionEffectsEnabled', 1)
                settings.user.ui.Set('turretsEnabled', 1)
        elif value == 2:
            prefs.SetValue('textureQuality', 1)
            prefs.SetValue('shaderQuality', 1)
            prefs.SetValue('shadowQuality', 0)
            prefs.SetValue('hdrEnabled', 0)
            prefs.SetValue('postProcessingQuality', 0)
            prefs.SetValue('resourceCacheEnabled', 0)
            prefs.SetValue('lodQuality', 1)
            prefs.SetValue('depthEffectsEnabled', 0)
            settings.public.device.Set('MultiSampleQuality', 0)
            settings.public.device.Set('MultiSampleType', 0)
            prefs.SetValue('fastCharacterCreation', 1)
            prefs.SetValue('charClothSimulation', 0)
            prefs.SetValue('charTextureQuality', 1)
            if eve.session.userid:
                settings.user.ui.Set('droneModelsEnabled', 0)
                settings.user.ui.Set('effectsEnabled', 0)
                settings.user.ui.Set('missilesEnabled', 0)
                settings.user.ui.Set('explosionEffectsEnabled', 0)
                settings.user.ui.Set('turretsEnabled', 0)
        elif value == 1:
            prefs.SetValue('textureQuality', 2)
            prefs.SetValue('shaderQuality', 1)
            prefs.SetValue('shadowQuality', 0)
            prefs.SetValue('hdrEnabled', 0)
            prefs.SetValue('postProcessingQuality', 0)
            prefs.SetValue('resourceCacheEnabled', 0)
            prefs.SetValue('lodQuality', 2)
            prefs.SetValue('depthEffectsEnabled', 0)
            settings.public.device.Set('MultiSampleQuality', 0)
            settings.public.device.Set('MultiSampleType', 0)
            prefs.SetValue('fastCharacterCreation', 1)
            prefs.SetValue('charClothSimulation', 0)
            prefs.SetValue('charTextureQuality', 2)
            if eve.session.userid:
                settings.user.ui.Set('droneModelsEnabled', 0)
                settings.user.ui.Set('effectsEnabled', 1)
                settings.user.ui.Set('missilesEnabled', 1)
                settings.user.ui.Set('explosionEffectsEnabled', 1)
                settings.user.ui.Set('turretsEnabled', 1)
        self.CloseX()




