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
import uiconst
import uicls
import weakref
import cameras
import appUtils
import localization
import localizationUtil
CACHESIZES = [0,
 32,
 128,
 256,
 512]
LEFTPADDING = 120
SLIDERWIDTH = 120

class SystemMenu(uicls.LayerCore):
    __guid__ = 'form.SystemMenu'
    __nonpersistvars__ = []
    __notifyevents__ = ['OnEchoChannel',
     'OnVoiceChatLoggedIn',
     'OnVoiceChatLoggedOut',
     'OnVoiceFontChanged',
     'OnEndChangeDevice',
     'OnUIColorsChanged',
     'OnUIRefresh']

    def OnUIRefresh(self):
        self.CloseView()
        uicore.layer.systemmenu.OpenView()



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
        self.init_languageID = eve.session.languageID if session.userid else prefs.languageID
        self.init_loadstationenv = prefs.GetValue('loadstationenv2', 1)
        self.init_dockshipsanditems = settings.user.windows.Get('dockshipsanditems', 0)
        self.init_stationservicebtns = settings.user.ui.Get('stationservicebtns', 0)
        self.tempStuff = []
        self.colors = [(localization.GetByLabel('UI/Common/Colors/ArmyGreen'), (70 / 256.0,
           75 / 256.0,
           50 / 256.0,
           170 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Black'), eve.themeColor),
         (localization.GetByLabel('UI/Common/Colors/CoolGray'), (70 / 256.0,
           75 / 256.0,
           70 / 256.0,
           172 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/DarkOpaque'), (43 / 256.0,
           43 / 256.0,
           43 / 256.0,
           204 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Desert'), (111 / 256.0,
           102 / 256.0,
           82 / 256.0,
           184 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/MidGray'), (101 / 256.0,
           100 / 256.0,
           111 / 256.0,
           171 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Mirage'), (24 / 256.0,
           32 / 256.0,
           41 / 256.0,
           235 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Nero'), (23 / 256.0,
           5 / 256.0,
           0 / 256.0,
           207 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Oil'), (49 / 256.0,
           38 / 256.0,
           27 / 256.0,
           0.75)),
         (localization.GetByLabel('UI/Common/Colors/Silver'), (125 / 256.0,
           125 / 256.0,
           125 / 256.0,
           130 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Stealth'), (51 / 256.0,
           54 / 256.0,
           45 / 256.0,
           113 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/SteelGray'), (61 / 256.0,
           55 / 256.0,
           68 / 256.0,
           172 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Swamp'), (0 / 256.0,
           21 / 256.0,
           21 / 256.0,
           181 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/BlackPearl'), (9 / 256.0,
           30 / 256.0,
           45 / 256.0,
           201 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/DarkLunarGreen'), (25 / 256.0,
           30 / 256.0,
           25 / 256.0,
           180 / 256.0))]
        self.backgroundcolors = [(localization.GetByLabel('UI/Common/Colors/ArmyGreen'), (14 / 256.0,
           28 / 256.0,
           17 / 256.0,
           170 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Black'), eve.themeBgColor),
         (localization.GetByLabel('UI/Common/Colors/CoolGray'), (14 / 256.0,
           28 / 256.0,
           32 / 256.0,
           172 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/DarkOpaque'), (19 / 256.0,
           19 / 256.0,
           19 / 256.0,
           204 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Desert'), (71 / 256.0,
           53 / 256.0,
           37 / 256.0,
           184 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/MidGray'), (71 / 256.0,
           70 / 256.0,
           79 / 256.0,
           200 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Mirage'), (34 / 256.0,
           48 / 256.0,
           59 / 256.0,
           132 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Nero'), (32 / 256.0,
           32 / 256.0,
           32 / 256.0,
           145 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Oil'), (116 / 256.0,
           116 / 256.0,
           116 / 256.0,
           152 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Silver'), (0.0,
           0.0,
           0.0,
           160 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Stealth'), (25 / 256.0,
           23 / 256.0,
           15 / 256.0,
           150 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/SteelGray'), (32 / 256.0,
           41 / 256.0,
           46 / 256.0,
           168 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Swamp'), (23 / 256.0,
           23 / 256.0,
           23 / 256.0,
           153 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/BlackPearl'), (116 / 256.0,
           116 / 256.0,
           116 / 256.0,
           116 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/DarkLunarGreen'), (70 / 256.0,
           75 / 256.0,
           70 / 256.0,
           200 / 256.0))]
        self.components = [(localization.GetByLabel('UI/Common/Colors/ArmyGreen'), (14 / 256.0,
           28 / 256.0,
           17 / 256.0,
           170 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Black'), eve.themeCompColor),
         (localization.GetByLabel('UI/Common/Colors/CoolGray'), (14 / 256.0,
           28 / 256.0,
           32 / 256.0,
           172 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/DarkOpaque'), (31 / 256.0,
           31 / 256.0,
           31 / 256.0,
           204 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Desert'), (71 / 256.0,
           53 / 256.0,
           37 / 256.0,
           184 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/MidGray'), (32 / 256.0,
           32 / 256.0,
           32 / 256.0,
           128 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Mirage'), (0 / 256.0,
           0 / 256.0,
           0 / 256.0,
           112 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Nero'), (23 / 256.0,
           5 / 256.0,
           0 / 256.0,
           145 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Oil'), (42 / 256.0,
           42 / 256.0,
           42 / 256.0,
           162 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Silver'), (0.0,
           0.0,
           0.0,
           61 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Stealth'), (25 / 256.0,
           23 / 256.0,
           15 / 256.0,
           150 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/SteelGray'), (32 / 256.0,
           41 / 256.0,
           46 / 256.0,
           168 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Swamp'), (31 / 256.0,
           61 / 256.0,
           71 / 256.0,
           121 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/BlackPearl'), (2 / 256.0,
           4 / 256.0,
           9 / 256.0,
           110 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/DarkLunarGreen'), (2 / 256.0,
           4 / 256.0,
           9 / 256.0,
           109 / 256.0))]
        self.componentsubs = [(localization.GetByLabel('UI/Common/Colors/ArmyGreen'), (182 / 256.0,
           210 / 256.0,
           182 / 256.0,
           44 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Black'), eve.themeCompSubColor),
         (localization.GetByLabel('UI/Common/Colors/CoolGray'), (149 / 256.0,
           194 / 256.0,
           216 / 256.0,
           16 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/DarkOpaque'), (256 / 256.0,
           256 / 256.0,
           256 / 256.0,
           16 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Desert'), (221 / 256.0,
           232 / 256.0,
           256 / 256.0,
           11 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/MidGray'), (127 / 256.0,
           127 / 256.0,
           127 / 256.0,
           115 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Mirage'), (0 / 256.0,
           0 / 256.0,
           0 / 256.0,
           50 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Nero'), (23 / 256.0,
           5 / 256.0,
           0 / 256.0,
           145 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Oil'), (25 / 256.0,
           25 / 256.0,
           25 / 256.0,
           160 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Silver'), (256 / 256.0,
           256 / 256.0,
           256 / 256.0,
           11 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Stealth'), (206 / 256.0,
           206 / 256.0,
           206 / 256.0,
           16 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/SteelGray'), (88 / 256.0,
           83 / 256.0,
           94 / 256.0,
           110 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/Swamp'), (31 / 256.0,
           61 / 256.0,
           71 / 256.0,
           121 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/BlackPearl'), (2 / 256.0,
           4 / 256.0,
           9 / 256.0,
           115 / 256.0)),
         (localization.GetByLabel('UI/Common/Colors/DarkLunarGreen'), (2 / 256.0,
           4 / 256.0,
           9 / 256.0,
           114 / 256.0))]
        self.voiceFontList = None
        if sm.GetService('vivox').Enabled():
            sm.GetService('vivox').StopAudioTest()
        self.NO_PSEUDOLOCALIZATION_PRESET = -1



    def OnCloseView(self):
        if self.hideUI and eve.session.userid:
            sm.GetService('cmd').ShowUI()
        if self.settings:
            self.ApplyDeviceChanges()
        if getattr(self, 'optimizeWnd', None) is not None:
            self.optimizeWnd.Close()
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
            if sm.GetService('viewState').IsViewActive('starmap'):
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
        start = blue.os.GetWallclockTimeNow()
        sceneManager = sm.GetService('sceneManager')
        while ndt != 1.0:
            ndt = min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / time, 1.0)
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
            return [('displayandgraphics', localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Header')),
             ('audioandchat', localization.GetByLabel('UI/SystemMenu/AudioAndChat/Header')),
             ('generic', localization.GetByLabel('UI/SystemMenu/GeneralSettings/Header')),
             ('shortcuts', localization.GetByLabel('UI/SystemMenu/Shortcuts/Header')),
             ('reset settings', localization.GetByLabel('UI/SystemMenu/ResetSettings/Header')),
             ('language', localization.GetByLabel('UI/SystemMenu/Language/Header')),
             ('about eve', localization.GetByLabel('UI/SystemMenu/AboutEve/Header'))]
        else:
            return [('displayandgraphics', localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Header')),
             ('audioandchat', localization.GetByLabel('UI/SystemMenu/AudioAndChat/Header')),
             ('generic', localization.GetByLabel('UI/SystemMenu/GeneralSettings/Header')),
             ('reset settings', localization.GetByLabel('UI/SystemMenu/ResetSettings/Header')),
             ('language', localization.GetByLabel('UI/SystemMenu/Language/Header')),
             ('about eve', localization.GetByLabel('UI/SystemMenu/AboutEve/Header'))]



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
        for (tabId, label,) in tabs:
            maintabgroups.append([label,
             uicls.Container(name=tabId + '_container', parent=menusub, padTop=8, padBottom=8),
             self,
             tabId])

        maintabs = uicls.TabGroup(parent=menusub, autoselecttab=True, tabs=maintabgroups, groupID='sysmenumaintabs', idx=0)
        self.sr.maintabs = maintabs
        uicls.Line(parent=menusub, align=uiconst.TOBOTTOM, padTop=-1)
        btnPar = uicls.Container(name='btnPar', parent=menusub, align=uiconst.TOBOTTOM, height=35, padTop=const.defaultPadding, idx=0)
        btn = uicls.Button(parent=btnPar, label=localization.GetByLabel('UI/SystemMenu/CloseWindow'), func=self.CloseMenuClick, align=uiconst.CENTER)
        btn = uicls.Button(parent=btnPar, label=localization.GetByLabel('UI/SystemMenu/QuitGame'), func=self.QuitBtnClick, left=10, align=uiconst.CENTERRIGHT)
        if eve.session.userid:
            btn = uicls.Button(parent=btnPar, label=localization.GetByLabel('UI/SystemMenu/LogOff'), func=self.Logoff, left=btn.width + btn.left + 2, align=uiconst.CENTERRIGHT)
            btn = uicls.Button(parent=btnPar, label=localization.GetByLabel('UI/SystemMenu/YourPetitions'), func=self.Petition, left=10, align=uiconst.CENTERLEFT)
        if eve.session.charid and boot.region != 'optic':
            btn = uicls.Button(parent=btnPar, label=localization.GetByLabel('UI/SystemMenu/ConvertETC'), func=self.ConvertETC, left=btn.width + btn.left + 2, align=uiconst.CENTERLEFT)
            btn = uicls.Button(parent=btnPar, label=localization.GetByLabel('UI/SystemMenu/RedeemItems'), func=self.RedeemItems, left=btn.width + btn.left + 2, align=uiconst.CENTERLEFT)
        if eve.session.userid:
            build = uicls.EveLabelMedium(text=localization.GetByLabel('UI/SystemMenu/VersionInfo', version=boot.keyval['version'].split('=', 1)[1], build=boot.build), parent=self.sr.wnd, left=6, top=6, state=uiconst.UI_NORMAL)
        self.sr.wndUnderlay = uicls.WindowUnderlay(parent=menuarea)
        if eve.session.userid:
            blue.pyos.synchro.Yield()
            self.GetBackground()
        if self.sr.wnd:
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
        windowed = self.IsWindowed()
        self.uiScaleValue = sm.GetService('device').GetUIScaleValue(windowed)



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
        currentResLabel = localization.GetByLabel('/Carbon/UI/Service/Device/ScreenSize', width=deviceSet.BackBufferWidth, height=deviceSet.BackBufferHeight)
        currentRes = (currentResLabel, (deviceSet.BackBufferWidth, deviceSet.BackBufferHeight))
        windowed = set.Windowed
        if bool(set.Windowed) and settings.public.device.Get('FixedWindow', False):
            set.Windowed = 2
            windowed = 1
        elif not set.Windowed:
            settings.public.device.Set('FixedWindow', False)
        currentResLabel = localization.GetByLabel('/Carbon/UI/Service/Device/ScreenSize', width=deviceSet.BackBufferWidth, height=deviceSet.BackBufferHeight)
        currentRes = (currentResLabel, (deviceSet.BackBufferWidth, deviceSet.BackBufferHeight))
        if windowed and currentRes not in resolutionOps:
            resolutionOps.append(currentRes)
        setBB = deviceSvc.GetPreferedResolution(windowed)
        triapp = trinity.app
        if triapp.isMaximized:
            setBB = (deviceSet.BackBufferWidth, deviceSet.BackBufferHeight)
        scalingOps = deviceSvc.GetUIScalingOptions(height=setBB[1])
        deviceData = [('header', localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/Header')),
         ('toppush', 4),
         ('combo',
          ('Windowed', None, deviceSvc.IsWindowed(self.settings)),
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/WindowedOrFullscreen'),
          windowOps,
          left,
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/WindowedOrFullscreenTooltip'),
          whatChanged == 'Windowed'),
         ('combo',
          ('BackBufferSize', None, setBB),
          [localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/AdapterResolution'), localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/WindowSize')][windowed],
          resolutionOps,
          left,
          [localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/AdapterResolutionTooltip'), localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/WindowSizeTooltip')][windowed],
          whatChanged == 'BackBufferSize',
          triapp.isMaximized),
         ('combo',
          ('UIScaling', None, self.uiScaleValue),
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/UIScaling'),
          scalingOps,
          left,
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/UIScalingTooltip'),
          whatChanged == 'UIScaling'),
         ('combo',
          ('Adapter', None, set.Adapter),
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/DisplayAdapter'),
          adapterOps,
          left,
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/DisplayAdapterTooltip'),
          whatChanged == 'Adapter')]
        if blue.win32.IsTransgaming():
            deviceData += [('checkbox',
              ('MacMTOpenGL', ('public', 'ui'), bool(sm.GetService('cider').GetMultiThreadedOpenGL())),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/UseMultithreadedOpenGL'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/UseMultithreadedOpenglToolTip'))]
        options = deviceSvc.GetPresentationIntervalOptions(set)
        if set.PresentationInterval not in [ val for (label, val,) in options ]:
            set.PresentationInterval = options[1][1]
        deviceData.append(('combo',
         ('PresentationInterval', None, set.PresentationInterval),
         localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/PresentInterval'),
         options,
         left,
         localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/PresentIntervalTooltip')))
        if eve.session.userid:
            deviceData += [('header', localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/InSpaceCameraSettings'))]
            self.cameraOffsetTextAdded = 0
            deviceData.append(('slider',
             ('cameraOffset', ('user', 'ui'), 0.0),
             'UI/SystemMenu/DisplayAndGraphics/DisplaySetup/CameraCenter',
             (-100, 100),
             120,
             10))
            deviceData.append(('toppush', 10))
            deviceData.append(('checkbox',
             ('offsetUIwithCamera', ('user', 'ui'), 0),
             localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/OffsetUIWithCamera'),
             None,
             None,
             localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/OffsetUIWithCameraTooltip')))
            incarnaCameraSvc = sm.GetService('cameraClient')
            incarnaCamSett = incarnaCameraSvc.GetCameraSettings()
            deviceData += [('header', localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/InStationCameraSettings')),
             ('slider',
              ('incarnaCameraOffset', ('user', 'ui'), incarnaCamSett.charOffsetSetting),
              'UI/SystemMenu/DisplayAndGraphics/DisplaySetup/CameraCenter',
              (-1.0, 1.0),
              120,
              10),
             ('toppush', 8),
             ('slider',
              ('incarnaCameraMouseLookSpeedSlider', ('user', 'ui'), incarnaCamSett.mouseLookSpeed),
              'UI/SystemMenu/DisplayAndGraphics/DisplaySetup/IncarnaCamera/CameraLookSpeed',
              (-6, 6),
              120,
              10),
             ('toppush', 10),
             ('checkbox',
              ('incarnaCameraInvertY', ('user', 'ui'), incarnaCamSett.invertY),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/IncarnaCamera/InvertY'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/IncarnaCamera/InvertYTooltip')),
             ('checkbox',
              ('incarnaCameraMouseSmooth', ('user', 'ui'), incarnaCamSett.mouseSmooth),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/IncarnaCamera/SmoothCamera'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/IncarnaCamera/SmoothCameraTooltip'))]
        self.ParseData(deviceData, where)
        btnPar = uicls.Container(name='btnpar', parent=where, align=uiconst.TOBOTTOM, height=32)
        btn = uicls.Button(parent=btnPar, label=localization.GetByLabel('UI/Common/Buttons/Apply'), func=self.ApplyDeviceChanges, align=uiconst.CENTERTOP)



    def ApplyDeviceChanges(self, *args):
        deviceSvc = sm.GetService('device')
        if self.settings is None:
            return 
        s = self.settings.copy()
        fixedWindow = settings.public.device.Get('FixedWindow', False)
        deviceChanged = deviceSvc.CheckDeviceDifference(s, True)
        triapp = trinity.app
        if not deviceChanged and blue.win32.IsTransgaming():
            windowModeChanged = sm.GetService('cider').HasFullscreenModeChanged()
            deviceChanged = deviceChanged or windowModeChanged
        if deviceChanged:
            deviceSvc.SetDevice(s, userModified=True)
        elif triapp.fixedWindow != fixedWindow:
            triapp.AdjustWindowForChange(s.Windowed, fixedWindow)
            deviceSvc.UpdateWindowPosition(s)
        windowed = self.IsWindowed()
        currentUIScale = deviceSvc.GetUIScaleValue(windowed)
        scaleValue = getattr(self, 'uiScaleValue', currentUIScale)
        if scaleValue != currentUIScale:
            if eve.Message('ScaleUI', {}, uiconst.YESNO, default=uiconst.ID_YES) == uiconst.ID_YES:
                deviceSvc.SetUIScaleValue(scaleValue, windowed)



    def IsWindowed(self):
        if self.settings.Windowed:
            return True
        return False



    def OnEndChangeDevice(self, *args):
        if self and not self.dead and self.isopen:
            self.settings = sm.GetService('device').GetSettings()
            self.ProcessDeviceSettings()
            self.ProcessGraphicsSettings()



    def ChangeWindowMode(self, windowed):
        val = windowed
        self.uiScaleValue = sm.GetService('device').GetUIScaleValue(windowed)
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
        if combo.name in ('Adapter', 'Windowed', 'BackBufferFormat', 'BackBufferSize', 'AutoDepthStencilFormat', 'zEnable', 'PresentationInterval', 'incarnaCameraChase', 'Anti-Aliasing', 'UIScaling'):
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
            elif combo.name == 'UIScaling':
                self.uiScaleValue = value
            else:
                setattr(self.settings, combo.name, value)
            self.ProcessDeviceSettings(whatChanged=combo.name)
        elif combo.name == 'autoTargetBack':
            settings.user.ui.Set('autoTargetBack', value)
        elif combo.name in ('color', 'backgroundcolor', 'component', 'componentsub'):
            if settings.user.ui.Get('linkColorCombos', False) and header != localization.GetByLabel('UI/Common/Colors/CustomColor'):
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
            clothEnabled = value > 1
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
        elif combo.name == 'interiorShaderQuality':
            prefs.SetValue('interiorShaderQuality', value)
        elif combo.name == 'pseudolocalizationPreset':
            settings.user.localization.Set('pseudolocalizationPreset', value)
            self.SetPseudolocalizationSettingsByPreset(value)
            self.RefreshLanguage()
        elif combo.name == 'characterReplacementMethod':
            originalPresetValue = settings.user.localization.Get('pseudolocalizationPreset', self.NO_PSEUDOLOCALIZATION_PRESET)
            originalReplaceValue = settings.user.localization.Get('characterReplacementMethod', localization.NO_REPLACEMENT)
            settings.user.localization.Set('characterReplacementMethod', value)
            if value == localization.NO_REPLACEMENT:
                localizationUtil.SetPseudolocalization(False)
            else:
                localizationUtil.SetPseudolocalization(True)
            if originalPresetValue != self.NO_PSEUDOLOCALIZATION_PRESET and originalReplaceValue != value:
                settings.user.localization.Set('pseudolocalizationPreset', self.NO_PSEUDOLOCALIZATION_PRESET)
            self.RefreshLanguage()



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
            shortcutString = c.GetShortcutAsString() or localization.GetByLabel('UI/SystemMenu/Shortcuts/NoShortcut')
            data.label = c.GetDescription() + '<t>' + shortcutString
            data.locked = c.isLocked
            data.refreshcallback = self.ReloadCommands
            scrolllist.append(listentry.Get('CmdListEntry', data=data))

        self.sr.active_cmdscroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/SystemMenu/Shortcuts/Command'), localization.GetByLabel('UI/SystemMenu/Shortcuts/Shortcut')], scrollTo=self.sr.active_cmdscroll.GetScrollProportion())



    def RestoreShortcuts(self, *args):
        uicore.cmd.RestoreDefaults()
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
        html = localization.GetByLabel('UI/SystemMenu/AboutEve/AboutEve', title=localization.GetByLabel('UI/SystemMenu/AboutEve/ReleaseTitle'), subtitle=localization.GetByLabel('UI/SystemMenu/AboutEve/ReleaseSubtitle'), version=boot.keyval['version'].split('=', 1)[1], build=boot.build, currentYear=blue.os.GetTimeParts(blue.os.GetTime())[0], EVECredits=localization.GetByLabel('UI/SystemMenu/AboutEve/EVECredits'), CarbonCredits=localization.GetByLabel('UI/SystemMenu/AboutEve/CarbonCredits'), EVEPublishingCredits=localization.GetByLabel('UI/SystemMenu/AboutEve/EVEPublishingCredits'), CCPCredits=localization.GetByLabel('UI/SystemMenu/AboutEve/CCPCredits'))
        self.sr.messageArea.LoadHTML(html)
        self.sr.abouteveinited = 1



    def ValidateData(self, entries):
        valid = []
        for rec in entries:
            if rec[0] not in ('checkbox', 'combo', 'slider', 'button'):
                valid.append(rec)
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
                t = uicls.EveLabelMedium(name='sysheader', text=rec[1], parent=parent, align=uiconst.TOTOP, padTop=2, padBottom=2, state=uiconst.UI_NORMAL)
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
                cb.RefreshHeight()
                self.tempStuff.append(cb)
            elif rec[0] == 'combo':
                (cfgName, prefsType, defaultValue,) = rec[1]
                if prefsType:
                    defaultValue = self.GetSettingsValue(cfgName, prefsType, defaultValue)
                label = rec[2]
                options = rec[3]
                if cfgName == 'UIScaling':
                    newValue = False
                    for (optionLabel, value,) in options:
                        if defaultValue == value:
                            newValue = True

                    if not newValue:
                        defaultValue = options[-1][1]
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
        if not getattr(self, 'cameraOffsetTextAdded', 0):
            if getattr(self, 'cameraOffset', None) is None:
                self.cameraSlider = uiutil.FindChild(self, 'cameraOffset')
            self.AddCameraOffsetHint(self.cameraSlider)
            self.cameraOffsetTextAdded = 1
        settings.user.ui.cameraOffset = value
        sm.GetService('sceneManager').CheckCameraOffsets()



    def OnSetIncarnaCameraSliderValue(self, value, *args):
        if not getattr(self, 'incarnaCameraOffsetTextAdded', 0):
            if getattr(self, 'incarnaCameraOffset', None) is None:
                self.incarnaCameraSlider = uiutil.FindChild(self, 'incarnaCameraOffset')
            self.AddCameraOffsetHint(self.incarnaCameraSlider)
            self.incarnaCameraOffsetTextAdded = 1
        settings.user.ui.incarnaCameraOffset = value
        sm.GetService('cameraClient').CheckCameraOffsets()



    def OnSetIncarnaCameraMouseLookSpeedSliderValue(self, value, *args):
        if not getattr(self, 'incarnaCameraMouseLookSpeedTextAdded', 0):
            if getattr(self, 'incarnaCameraMouseLookSpeedSlider', None) is None:
                self.incarnaCameraMouseSpeedSlider = uiutil.FindChild(self, 'incarnaCameraMouseLookSpeedSlider')
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
        uicls.EveLabelSmall(name='slower', text=localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/IncarnaCamera/CameraSpeedSliderSlow'), parent=p, align=uiconst.TOPLEFT, top=10, color=(1.0, 1.0, 1.0, 0.75))
        uicls.EveLabelSmall(name='faster', text=localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/IncarnaCamera/CameraSpeedSliderFast'), parent=p, align=uiconst.TOPRIGHT, top=10, color=(1.0, 1.0, 1.0, 0.75))
        uicls.Line(name='centerLine', parent=p, width=2, height=10, align=uiconst.CENTER)
        p.parent.hint = localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/IncarnaCamera/CameraSpeedSliderTooltip')
        p.state = p.parent.state = uiconst.UI_NORMAL



    def AddCameraOffsetHint(self, whichOne):
        p = whichOne.parent
        uicls.EveLabelSmall(name='left', text=localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/CameraCenterSliderLeft'), parent=p, align=uiconst.TOPLEFT, top=10, color=(1.0, 1.0, 1.0, 0.75))
        uicls.EveLabelSmall(name='right', text=localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/CameraCenterSliderRight'), parent=p, align=uiconst.TOPRIGHT, top=10, color=(1.0, 1.0, 1.0, 0.75))
        uicls.Line(name='centerLine', parent=p, width=2, height=10, align=uiconst.CENTER)
        p.parent.hint = localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/CameraCenterSliderTooltip')
        p.state = p.parent.state = uiconst.UI_NORMAL



    def GetCameraMouseSpeedHintText(self, value):
        if value == 0:
            return localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/IncarnaCamera/CameraSpeedSliderDefaultValue')
        else:
            if value < 0:
                value = abs(value) + 1.0
                return localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/IncarnaCamera/CameraSpeedSliderSlowerValue', value=value)
            value += 1.0
            return localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/IncarnaCamera/CameraSpeedSliderFasterValue', value=value)



    def GetCameraOffsetHintText(self, value, incarna = False):
        if incarna:
            value *= 100
        if value == 0:
            return localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/CameraCenterSliderCenteredValue')
        else:
            if value < 0:
                return localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/CameraCenterSliderLeftValue', value=abs(int(value)))
            return localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/CameraCenterSliderRightValue', value=abs(int(value)))



    def GetSettingsValue(self, cfgName, prefsType, defaultValue):
        if not prefsType:
            return defaultValue
        return util.GetAttrs(settings, *prefsType).Get(cfgName, defaultValue)



    def Generic(self):
        if self.sr.genericinited:
            return 
        parent = uiutil.GetChild(self.sr.wnd, 'generic_container')
        actionbtnOps = [(localization.GetByLabel('UI/Common/Input/Mouse/LeftMouseButton'), 0), (localization.GetByLabel('UI/Common/Input/Mouse/MiddleMouseButton'), 2)]
        menufontsizeOps = [(localizationUtil.FormatNumeric(9), 9),
         (localizationUtil.FormatNumeric(10), 10),
         (localizationUtil.FormatNumeric(11), 11),
         (localizationUtil.FormatNumeric(12), 12),
         (localizationUtil.FormatNumeric(13), 13)]
        snapOps = [(localization.GetByLabel('UI/SystemMenu/GeneralSettings/Windows/DontSnap'), 0),
         (localizationUtil.FormatNumeric(3), 3),
         (localizationUtil.FormatNumeric(6), 6),
         (localizationUtil.FormatNumeric(12), 12),
         (localizationUtil.FormatNumeric(24), 24)]
        column = uicls.Container(name='col1', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
        column.isTabOrderGroup = 1
        uicls.Frame(parent=column)
        if settings.public.generic.Get('showintro2', None) is None:
            settings.public.generic.Set('showintro2', prefs.GetValue('showintro2', 1))
        menusData = [('header', localization.GetByLabel('UI/SystemMenu/GeneralSettings/General/Header')),
         ('checkbox', ('showintro2', ('public', 'generic'), 1), localization.GetByLabel('UI/SystemMenu/GeneralSettings/General/ShowIntro')),
         ('checkbox', ('showSessionTimer', ('user', 'ui'), 0), localization.GetByLabel('UI/SystemMenu/GeneralSettings/General/ShowSessionTimer')),
         ('checkbox', ('hdScreenshots', ('user', 'ui'), 0), localization.GetByLabel('UI/SystemMenu/GeneralSettings/General/EnableHQScreenShots')),
         ('checkbox', ('windowidentification', ('user', 'ui'), 0), localization.GetByLabel('UI/SystemMenu/GeneralSettings/General/ShowWindowIdentification')),
         ('toppush', 4),
         ('combo',
          ('cmenufontsize', ('user', 'ui'), 10),
          localization.GetByLabel('UI/SystemMenu/GeneralSettings/General/ContextMenuFontSize'),
          menufontsizeOps,
          LEFTPADDING),
         ('header', localization.GetByLabel('UI/SystemMenu/GeneralSettings/Windows/Header')),
         ('checkbox', ('stackwndsonshift', ('user', 'ui'), 0), localization.GetByLabel('UI/SystemMenu/GeneralSettings/Windows/OnlyStackWindowsIfShiftIsPressed')),
         ('checkbox', ('useexistinginfownd', ('user', 'ui'), 1), localization.GetByLabel('UI/SystemMenu/GeneralSettings/Windows/TryUseExistingInfoWin')),
         ('toppush', 4),
         ('combo',
          ('snapdistance', ('user', 'windows'), 12),
          localization.GetByLabel('UI/SystemMenu/GeneralSettings/Windows/WindowSnapDistance'),
          snapOps,
          LEFTPADDING)]
        self.ParseData(menusData, column)
        uicls.Container(name='toppush', align=uiconst.TOTOP, height=4, parent=column)
        uix.GetContainerHeader(localization.GetByLabel('UI/SystemMenu/GeneralSettings/Crashes/Header'), column, xmargin=-5)
        uicls.Container(name='toppush', align=uiconst.TOTOP, height=2, parent=column)
        uicls.Checkbox(text=localization.GetByLabel('UI/SystemMenu/GeneralSettings/Crashes/UploadCrashDumpsToCCPEnabled'), parent=column, checked=blue.IsBreakpadEnabled(), callback=self.EnableDisableBreakpad)
        lst = []
        if lst:
            uicls.Container(name='toppush', align=uiconst.TOTOP, height=4, parent=column)
            uix.GetContainerHeader(localization.GetByLabel('UI/SystemMenu/GeneralSettings/Experimental/Header'), column, xmargin=-5)
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
                 'singleline': 0,
                 'entryWidth': self.colWidth - 16}))

            scroll.Load(contentList=scrollList)
        if len(column.children) == 1:
            column.Close()
        column = uicls.Container(name='column', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
        column.isTabOrderGroup = 1
        uicls.Frame(parent=column)
        atOps = []
        for i in xrange(13):
            if i == 0:
                atOps.append((localization.GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/ZeroTargets', targetCount=i), i))
            else:
                atOps.append((localization.GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/Targets', targetCount=i), i))

        stationData = (('header', localization.GetByLabel('UI/SystemMenu/GeneralSettings/Help/Header')),
         ('checkbox', ('showTutorials', ('char', 'ui'), 1), localization.GetByLabel('UI/SystemMenu/GeneralSettings/Help/ShowTutorials')),
         ('header', localization.GetByLabel('UI/SystemMenu/GeneralSettings/Station/Header')),
         ('checkbox', ('stationservicebtns', ('user', 'ui'), 0), localization.GetByLabel('UI/SystemMenu/GeneralSettings/Station/SmallButtons')),
         ('checkbox', ('dockshipsanditems', ('user', 'windows'), 0), localization.GetByLabel('UI/SystemMenu/GeneralSettings/Station/MergeItemsAndShips')))
        self.ParseData(stationData, column)
        inflightData = (('header', localization.GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/Header')),
         ('checkbox', ('damageMessages', ('user', 'ui'), 1), localization.GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/DamageNotifications')),
         ('checkbox', ('damageMessagesNoDamage', ('user', 'ui'), 1), localization.GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/MissedHitNotifications')),
         ('checkbox', ('damageMessagesMine', ('user', 'ui'), 1), localization.GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/ShowInflictedDamageNotifications')),
         ('checkbox', ('damageMessagesEnemy', ('user', 'ui'), 1), localization.GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/ShowIncurredDamageNotification')),
         ('checkbox', ('damageMessagesSimple', ('user', 'ui'), 0), localization.GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/SimpleDamageNotifications')),
         ('checkbox',
          ('notifyMessagesEnabled', ('user', 'ui'), 1),
          localization.GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/ShowTacticalNotifications'),
          None,
          None,
          localization.GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/ShowTacticalNotificationTooltip')),
         ('checkbox', ('targetCrosshair', ('user', 'ui'), 1), localization.GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/ShowTargettingCrosshair')),
         ('toppush', 4),
         ('combo',
          ('autoTargetBack', ('user', 'ui'), 1),
          localization.GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/AutoTargetBack'),
          atOps,
          LEFTPADDING),
         ('combo',
          ('actionmenuBtn', ('user', 'ui'), 0),
          localization.GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/ExpandActionMenu'),
          actionbtnOps,
          LEFTPADDING))
        self.ParseData(inflightData, column)
        if settings.user.ui.Get('damageMessages', 1) == 0:
            for each in ('damageMessagesNoDamage', 'damageMessagesMine', 'damageMessagesEnemy', 'damageMessagesSimple'):
                cb = uiutil.FindChild(column, each)
                if cb:
                    cb.state = uiconst.UI_HIDDEN

        optionalUpgradeData = [('header', localization.GetByLabel('UI/SystemMenu/GeneralSettings/ClientUpdate/Header'))]
        patchService = sm.StartService('patch')
        upgradeInfo = patchService.GetServerUpgradeInfo()
        bottomPar = uicls.Container(name='bottomPar', parent=None, align=uiconst.TOALL)
        bottomBtnPar = uicls.Container(name='bottomBtnPar', parent=bottomPar, align=uiconst.CENTERTOP, height=26)
        if upgradeInfo is not None:
            n = nasty.GetAppDataCompiledCodePath()
            if (n.build or boot.build) < upgradeInfo.build:
                optionalUpgradeData.append(('text', localization.GetByLabel('UI/SystemMenu/GeneralSettings/ClientUpdate/UpdateAvailable')))
                detailsBtn = uicls.Button(parent=bottomBtnPar, label=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ClientUpdate/Details'), func=self.GoToOptionalUpgradeDetails, args=(), pos=(0, 0, 0, 0))
                installBtn = uicls.Button(parent=bottomBtnPar, label=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ClientUpdate/Install'), func=self.InstallOptionalUpgradeClick, args=(), pos=(detailsBtn.width + 2,
                 0,
                 0,
                 0))
                bottomBtnPar.width = detailsBtn.width + installBtn.width
        if nasty.IsRunningWithOptionalUpgrade():
            optionalUpgradeData.append(('text', localization.GetByLabel('UI/SystemMenu/GeneralSettings/ClientUpdate/AnUpdateHasBeenApplied')))
            uninstallBtn = uicls.Button(parent=bottomBtnPar, label=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ClientUpdate/Uninstall'), func=self.UnInstallOptionalUpgradeClick, args=(), pos=(0, 0, 0, 0))
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
                colors.insert(0, (localization.GetByLabel('UI/Common/Colors/CustomColor'), main))
            bgcolors = self.backgroundcolors[:]
            bgcolors.sort()
            bgselect = self.FindColor(backgroundcolor, self.backgroundcolors)
            if not bgselect:
                bgcolors.insert(0, (localization.GetByLabel('UI/Common/Colors/CustomColor'), backgroundcolor))
            ccolors = self.components[:]
            ccolors.sort()
            cselect = self.FindColor(component, self.components)
            if not cselect:
                ccolors.insert(0, (localization.GetByLabel('UI/Common/Colors/CustomColor'), component))
            cscolors = self.componentsubs[:]
            cscolors.sort()
            csselect = self.FindColor(componentsub, self.componentsubs)
            if not csselect:
                cscolors.insert(0, (localization.GetByLabel('UI/Common/Colors/CustomColor'), componentsub))
            colorData = [('header', localization.GetByLabel('UI/SystemMenu/GeneralSettings/Layout/Header')),
             ('toppush', 2),
             ('checkbox', ('linkColorCombos', ('user', 'ui'), 0), localization.GetByLabel('UI/SystemMenu/GeneralSettings/Layout/EasyThemeSelection')),
             ('header', localization.GetByLabel('UI/SystemMenu/GeneralSettings/WindowColorHeader')),
             ('toppush', 4),
             ('combo',
              ('color', None, select),
              localization.GetByLabel('UI/SystemMenu/GeneralSettings/Layout/Presets'),
              colors,
              sidepush),
             ('slider',
              ('wnd_color_r', None, mr),
              'UI/SystemMenu/GeneralSettings/Red',
              (0.0, 1.0),
              sidepush),
             ('slider',
              ('wnd_color_g', None, mg),
              'UI/SystemMenu/GeneralSettings/Green',
              (0.0, 1.0),
              sidepush),
             ('slider',
              ('wnd_color_b', None, mb),
              'UI/SystemMenu/GeneralSettings/Blue',
              (0.0, 1.0),
              sidepush),
             ('slider',
              ('wnd_color_a', None, ma),
              'UI/SystemMenu/GeneralSettings/Transparent',
              (0.0, 1.0),
              sidepush),
             ('toppush', 4),
             ('header', localization.GetByLabel('UI/SystemMenu/GeneralSettings/BackgroundColorHeader')),
             ('toppush', 4),
             ('combo',
              ('backgroundcolor', None, bgselect),
              localization.GetByLabel('UI/SystemMenu/GeneralSettings/Layout/Presets'),
              bgcolors,
              sidepush),
             ('slider',
              ('wnd_backgroundcolor_r', None, br),
              'UI/SystemMenu/GeneralSettings/Red',
              (0.0, 1.0),
              sidepush),
             ('slider',
              ('wnd_backgroundcolor_g', None, bg),
              'UI/SystemMenu/GeneralSettings/Green',
              (0.0, 1.0),
              sidepush),
             ('slider',
              ('wnd_backgroundcolor_b', None, bb),
              'UI/SystemMenu/GeneralSettings/Blue',
              (0.0, 1.0),
              sidepush),
             ('slider',
              ('wnd_backgroundcolor_a', None, ba),
              'UI/SystemMenu/GeneralSettings/Transparent',
              (0.0, 1.0),
              sidepush),
             ('toppush', 4),
             ('header', localization.GetByLabel('UI/SystemMenu/GeneralSettings/HeaderAndSubHeaderColorHeader')),
             ('toppush', 4),
             ('combo',
              ('component', None, cselect),
              localization.GetByLabel('UI/SystemMenu/GeneralSettings/Layout/Presets'),
              ccolors,
              sidepush),
             ('combo',
              ('componentsub', None, csselect),
              localization.GetByLabel('UI/SystemMenu/GeneralSettings/Layout/Presets'),
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
        audioData = (('header', localization.GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/Header')),
         ('checkbox', ('audioEnabled', ('public', 'audio'), enabled), localization.GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/AudioEnabled')),
         ('header', localization.GetByLabel('UI/SystemMenu/AudioAndChat/VolumeLevel/Header')),
         ('slider',
          ('eveampGain', ('public', 'audio'), 0.4),
          'UI/SystemMenu/AudioAndChat/VolumeLevel/MusicLevel',
          (0.0, 1.0),
          labelWidth),
         ('slider',
          ('uiGain', ('public', 'audio'), 0.4),
          'UI/SystemMenu/AudioAndChat/VolumeLevel/UISoundLevel',
          (0.0, 1.0),
          labelWidth),
         ('slider',
          ('evevoiceGain', ('public', 'audio'), 0.9),
          'UI/SystemMenu/AudioAndChat/VolumeLevel/UIVoiceLevel',
          (0.0, 1.0),
          labelWidth),
         ('slider',
          ('worldVolume', ('public', 'audio'), 0.4),
          'UI/SystemMenu/AudioAndChat/VolumeLevel/WorldLevel',
          (0.0, 1.0),
          labelWidth),
         ('slider',
          ('masterVolume', ('public', 'audio'), 0.4),
          'UI/SystemMenu/AudioAndChat/VolumeLevel/MasterLevel',
          (0.0, 1.0),
          labelWidth),
         ('checkbox', ('suppressTurret', ('public', 'audio'), turretSuppressed), localization.GetByLabel('UI/SystemMenu/AudioAndChat/VolumeLevel/SuppressTurretSounds')))
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
            voiceHeader = localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/Header')
            voiceServerInfo = sm.GetService('vivox').GetServerInfo()
            if voiceServerInfo:
                voiceHeader = localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/Header', server=voiceServerInfo)
            vivoxData = [('header', voiceHeader),
             ('checkbox',
              ('voiceenabled', ('user', 'audio'), 1),
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/EveVoiceEnabled'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/EveVoiceEnabledTooltip')),
             ('checkbox',
              ('talkMutesGameSounds', ('user', 'audio'), 0),
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/MuteWhenITalk'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/MuteWhenITalkTooltip')),
             ('checkbox',
              ('listenMutesGameSounds', ('user', 'audio'), 0),
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/MuteWhenOthersTalk'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/MuteWhenOthersTalkTooltip')),
             ('header', localization.GetByLabel('UI/SystemMenu/AudioAndChat/ChannelSpecification/Header')),
             ('checkbox',
              ('talkMoveToTopBtn', ('user', 'audio'), 0),
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/ChannelSpecification/MoveLastSpeakerToTop'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/ChannelSpecification/MoveLastSpeakerToTopTooltip')),
             ('checkbox',
              ('talkAutoJoinFleet', ('user', 'audio'), 1),
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/ChannelSpecification/AutoJoinFleetVoice'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/ChannelSpecification/AutoJoinFleetVoiceTooltip')),
             ('checkbox',
              ('talkChannelPriority', ('user', 'audio'), 0),
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/ChannelSpecification/ChannelPrioritize'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/ChannelSpecification/ChannelPrioritizeTooltip')),
             ('header', localization.GetByLabel('UI/SystemMenu/AudioAndChat/GenericConfiguration/Header')),
             ('toppush', 4),
             ('combo',
              ('talkBinding', ('user', 'audio'), 4),
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/GenericConfiguration/TalkKey'),
              keybindOptions,
              labelWidth),
             ('combo',
              ('TalkOutputDevice', ('user', 'audio'), 0),
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/GenericConfiguration/TalkDriverOutput'),
              outputOps,
              labelWidth),
             ('combo',
              ('TalkInputDevice', ('user', 'audio'), 0),
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/GenericConfiguration/TalkDevice'),
              inputOps,
              labelWidth),
             ('slider',
              ('TalkMicrophoneVolume', ('user', 'audio'), sm.GetService('vivox').defaultMicrophoneVolume),
              'UI/SystemMenu/AudioAndChat/GenericConfiguration/InputVolume',
              (0.0, 1.0),
              labelWidth),
             ('toppush', 4)]
            self.ParseData(vivoxData, col2)
            inputmeterpar = uicls.Container(name='inputmeter', align=uiconst.TOTOP, height=12, parent=col2)
            if not sm.GetService('vivox').GetSpeakingChannel() == 'Echo':
                uix.GetContainerHeader(localization.GetByLabel('UI/SystemMenu/AudioAndChat/GenericConfiguration/TalkMeterInactive'), col2, 0)
            else:
                subpar = uicls.Container(name='im_sub', align=uiconst.TORIGHT, width=col2.width - labelWidth - 11, parent=inputmeterpar)
                uicls.Frame(parent=subpar, width=-1)
                self.maxInputMeterWidth = subpar.width - 4
                self.sr.inputmeter = uicls.Fill(parent=subpar, left=2, top=2, width=1, height=inputmeterpar.height - 4, align=uiconst.RELATIVE, color=(1.0, 1.0, 1.0, 0.25))
                uicls.EveLabelSmall(text=localization.GetByLabel('UI/SystemMenu/AudioAndChat/GenericConfiguration/TalkMeter'), parent=inputmeterpar, top=2, state=uiconst.UI_NORMAL)
                sm.GetService('vivox').RegisterIntensityCallback(self)
                sm.GetService('vivox').StartAudioTest()
            if sm.GetService('vivox').GetSpeakingChannel() == 'Echo':
                echoBtnLabel = localization.GetByLabel('UI/SystemMenu/AudioAndChat/GenericConfiguration/StopEchoTest')
                echoTextString = localization.GetByLabel('UI/SystemMenu/AudioAndChat/GenericConfiguration/EchoTestInstructions')
            else:
                echoBtnLabel = localization.GetByLabel('UI/SystemMenu/AudioAndChat/GenericConfiguration/EchoTest')
                echoTextString = ''
            btnPar = uicls.Container(name='push', align=uiconst.TOTOP, height=30, parent=col2)
            self.echoBtn = uicls.Button(parent=btnPar, label=echoBtnLabel, func=self.JoinLeaveEchoChannel, align=uiconst.CENTER)
            uicls.Container(name='push', align=uiconst.TOTOP, height=8, parent=col2)
            self.echoText = uicls.EveLabelSmall(text=echoTextString, parent=col2, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        elif eve.session.userid and voiceChatMenuAvailable:
            vivoxData = (('header', localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/Header')),
             ('checkbox',
              ('voiceenabled', ('user', 'audio'), 1),
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/EveVoiceEnabled'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/EveVoiceEnabledTooltip')),
             ('checkbox',
              ('talkMutesGameSounds', ('user', 'audio'), 0),
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/MuteWhenITalk'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/MuteWhenITalkTooltip')),
             ('checkbox',
              ('listenMutesGameSounds', ('user', 'audio'), 0),
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/MuteWhenOthersTalk'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/MuteWhenOthersTalkTooltip')),
             ('header', localization.GetByLabel('UI/SystemMenu/AudioAndChat/ChannelSpecification/Header')),
             ('text', localization.GetByLabel('UI/SystemMenu/AudioAndChat/GenericConfiguration/NotConnected')))
            self.ParseData(vivoxData, col2, 0)
        elif voiceChatMenuAvailable:
            vivoxData = (('header', localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceSettings/Header')),
             ('text', localization.GetByLabel('UI/SystemMenu/AudioAndChat/GenericConfiguration/NotLoggedIn')),
             ('header', localization.GetByLabel('UI/SystemMenu/AudioAndChat/ChannelSpecification/Header')),
             ('text', localization.GetByLabel('UI/SystemMenu/AudioAndChat/GenericConfiguration/NotConnected')))
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
        dblClickUserOps = [(localization.GetByLabel('UI/Commands/ShowInfo'), 0), (localization.GetByLabel('UI/Chat/StartConversation'), 1)]
        self.ParseData((('header', localization.GetByLabel('UI/SystemMenu/AudioAndChat/Chat/Header')),), col3, 0)
        if eve.session.userid:
            chatData = (('checkbox', ('logchat', ('user', 'ui'), 1), localization.GetByLabel('UI/SystemMenu/AudioAndChat/Chat/LogChatToFile')),
             ('checkbox', ('autoRejectInvitations', ('user', 'ui'), 0), localization.GetByLabel('UI/SystemMenu/AudioAndChat/Chat/AutoRejectInvitations')),
             ('toppush', 4),
             ('combo',
              ('dblClickUser', ('user', 'ui'), 0),
              localization.GetByLabel('UI/SystemMenu/AudioAndChat/Chat/OnDoubleClick'),
              dblClickUserOps,
              labelWidth),
             ('toppush', 4))
            if voiceChatMenuAvailable and sm.GetService('vivox').LoggedIn():
                chatData += (('header', localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceChatChannelSettings/Header')),
                 ('checkbox', ('chatJoinCorporationChannelOnLogin', ('user', 'ui'), 0), localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceChatChannelSettings/AutoJoinCorporation')),
                 ('checkbox', ('chatJoinAllianceChannelOnLogin', ('user', 'ui'), 0), localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceChatChannelSettings/AutoJoinAlliance')),
                 ('header', localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/Header')))
        else:
            chatData = (('text', localization.GetByLabel('UI/SystemMenu/AudioAndChat/GenericConfiguration/NotLoggedIn')),)
        self.ParseData(chatData, col3, 0)
        if eve.session.charid and voiceChatMenuAvailable and sm.GetService('vivox').LoggedIn():
            currentVoiceFont = settings.char.ui.Get('voiceFontName', localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/NoFontSelected'))
            currentVoiceFontText = uicls.EveLabelSmall(text=localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/SelectedFont', selectedFont=currentVoiceFont), parent=col3, align=uiconst.TOTOP, top=4)
            btnPar = uicls.Container(name='push', align=uiconst.TOTOP, height=30, parent=col3)
            self.voiceFontBtn = uicls.Button(parent=btnPar, label=localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/ChangeFont'), func=self.SelectVoiceFontDialog, args=(), align=uiconst.CENTER)
            uicls.Container(name='push', align=uiconst.TOTOP, height=8, parent=col3)



    def SelectVoiceFontDialog(self):
        wnd = form.VoiceFontSelectionWindow.GetIfOpen()
        if wnd is None:
            wnd = form.VoiceFontSelectionWindow.Open()
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
        graphicsData2 = [('header', localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Header')), ('text', localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Description'))]
        shaderQualityOptions = [(localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), 1), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/MediumQuality'), 2)]
        if deviceSvc.SupportsDepthEffects():
            shaderQualityOptions.append((localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), 3))
        try:
            shaderQualityMenu = [('combo',
              ('shaderQuality', None, prefs.GetValue('shaderQuality', deviceSvc.GetDefaultShaderQuality())),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ShaderQuality'),
              shaderQualityOptions,
              LEFTPADDING,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ShaderQualityTooltip'))]
        except:
            log.LogException()
        textureQualityOptions = [(localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), 2), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/MediumQuality'), 1), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), 0)]
        textureQualityMenu = [('combo',
          ('textureQuality', None, prefs.GetValue('textureQuality', deviceSvc.GetDefaultTextureQuality())),
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/TextureQuality'),
          textureQualityOptions,
          LEFTPADDING,
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/TextureQualityTooltip'))]
        lodQualityOptions = [(localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), 1), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/MediumQuality'), 2), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), 3)]
        lodQualityMenu = [('combo',
          ('lodQuality', None, prefs.GetValue('lodQuality', deviceSvc.GetDefaultLodQuality())),
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/LODQuality'),
          lodQualityOptions,
          LEFTPADDING,
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/LODQualityTooltip'))]
        shadowQualityOptions = [(localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/Disabled'), 0), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), 1), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), 2)]
        shadowQualityMenu = [('combo',
          ('shadowQuality', None, prefs.GetValue('shadowQuality', deviceSvc.GetDefaultShadowQuality())),
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ShadowQuality'),
          shadowQualityOptions,
          LEFTPADDING,
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ShadowQualityTooltip'))]
        interiorQualityOptions = [(localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), 0), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/MediumQuality'), 1), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), 2)]
        interiorQualityMenu = [('combo',
          ('interiorGraphicsQuality', None, prefs.GetValue('interiorGraphicsQuality', deviceSvc.GetDefaultInteriorGraphicsQuality())),
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/InteriorQuality'),
          interiorQualityOptions,
          LEFTPADDING,
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/InteriorQualityTooltip'))]
        interiorShaderQualityOptions = [(localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), 0), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), 1)]
        interiorShaderQualityMenu = [('combo',
          ('interiorShaderQuality', None, prefs.GetValue('interiorShaderQuality', 1)),
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/InteriorShaderQuality'),
          interiorShaderQualityOptions,
          LEFTPADDING,
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/InteriorShaderQualityTooltip'))]
        graphicsData2 += [('checkbox',
          ('resourceCacheEnabled', None, bool(prefs.GetValue('resourceCacheEnabled', deviceSvc.GetDefaultResourceState()))),
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ResourceCache'),
          None,
          None,
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ResourceCacheTooltip'))]
        if deviceSvc.IsHDRSupported():
            graphicsData2 += [('checkbox',
              ('hdrEnabled', None, bool(prefs.GetValue('hdrEnabled', deviceSvc.GetDefaultHDRState()))),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/HDR'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/HDRTooltip'))]
        graphicsData2 += [('checkbox',
          ('loadstationenv2', None, prefs.GetValue('loadstationenv2', 1)),
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/LoadStationEnvironment'),
          None,
          None,
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/LoadStationEnvironmentTooltip'))]
        devicSvc = sm.GetService('device')
        hdrEnabled = prefs.GetValue('hdrEnabled', deviceSvc.GetDefaultHDRState())
        formats = [self.settings.BackBufferFormat, self.settings.AutoDepthStencilFormat, trinity.TRIFMT_A16B16G16R16F]
        options = deviceSvc.GetMultiSampleQualityOptions(self.settings, formats)
        graphicsData2.append(('combo',
         ('Anti-Aliasing', None, prefs.GetValue('antiAliasing', 0)),
         localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/AntiAliasing'),
         options,
         LEFTPADDING,
         localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/AntiAliasingTooltip')))
        postProcessingQualityOptions = [(localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/NoneLabel'), 0), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), 1), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), 2)]
        if deviceSvc.IsBloomSupported():
            graphicsData2 += [('combo',
              ('postProcessingQuality', None, prefs.GetValue('postProcessingQuality', deviceSvc.GetDefaultPostProcessingQuality())),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/PostProcessing'),
              postProcessingQualityOptions,
              LEFTPADDING,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/PostProcessingTooltip'))]
        graphicsData2 += shaderQualityMenu
        graphicsData2 += textureQualityMenu
        graphicsData2 += lodQualityMenu
        graphicsData2 += shadowQualityMenu
        graphicsData2 += interiorQualityMenu
        graphicsData2 += interiorShaderQualityMenu
        if eve.session.userid:
            graphicsData += [('header', localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/Header')),
             ('checkbox',
              ('turretsEnabled', ('user', 'ui'), 1),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/TurretEffects'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/TurretEffectsTooltip')),
             ('checkbox',
              ('effectsEnabled', ('user', 'ui'), 1),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/Effects'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/EffectsTooltip')),
             ('checkbox',
              ('missilesEnabled', ('user', 'ui'), 1),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/MissileEffects'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/EffectsTooltip')),
             ('checkbox',
              ('cameraShakeEnabled', ('user', 'ui'), 1),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/CameraShake'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/CameraShakeTooltip')),
             ('checkbox',
              ('explosionEffectsEnabled', ('user', 'ui'), 1),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/ShipExplosions'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/ShipExplosionsTooltip')),
             ('checkbox',
              ('droneModelsEnabled', ('user', 'ui'), 1),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/DroneModels'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/DroneModelsTooltip')),
             ('checkbox',
              ('trailsEnabled', ('user', 'ui'), settings.user.ui.Get('effectsEnabled', 1)),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/Trails'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/TrailsTooltip')),
             ('header', localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Miscellaneous/Header')),
             ('checkbox',
              ('lod', ('user', 'ui'), 1),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Miscellaneous/UseLOD'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Miscellaneous/UseLODTooltip')),
             ('checkbox',
              ('sunOcclusion', ('public', 'device'), 1),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Miscellaneous/SunOccludedByObjects'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Miscellaneous/SunOccludedByObjectsTooltip')),
             ('checkbox',
              ('advancedCamera', ('user', 'ui'), 0),
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Miscellaneous/AdvancedCameraMenu'),
              None,
              None,
              localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Miscellaneous/AdvancedCameraMenuTooltip'))]
            if sm.GetService('lightFx').IsLightFxSupported():
                graphicsData += [('checkbox',
                  ('LightFxEnabled', ('user', 'ui'), 1),
                  localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Miscellaneous/LightLEDEffect'),
                  None,
                  None,
                  localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Miscellaneous/LightLEDEffectTooltip'))]
        graphicsData += (('header', localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/CharacterCreation/Header')),)
        disabled = not trinity.GetShaderModel().startswith('SM_3')
        currentFastCharacterCreationValue = bool(prefs.GetValue('fastCharacterCreation', deviceSvc.GetDefaultFastCharacterCreation())) or disabled
        currentClothSimValue = prefs.GetValue('charClothSimulation', deviceSvc.GetDefaultClothSimEnabled()) and not disabled
        graphicsData += [('checkbox',
          ('fastCharacterCreation', None, currentFastCharacterCreationValue),
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/CharacterCreation/LowQualityCharacters'),
          None,
          None,
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/CharacterCreation/LowQualityCharactersTooltip'),
          None,
          disabled)]
        graphicsData += [('checkbox',
          ('charClothSimulation', None, currentClothSimValue),
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/CharacterCreation/ClothHairSim'),
          None,
          None,
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/CharacterCreation/ClothHairSimTooltip'),
          None,
          disabled)]
        charTextureQualityOptions = [(localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), 2), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/MediumQuality'), 1), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), 0)]
        graphicsData += [('combo',
          ('charTextureQuality', None, prefs.GetValue('charTextureQuality', deviceSvc.GetDefaultCharTextureQuality())),
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/CharacterCreation/TextureQuality'),
          charTextureQualityOptions,
          LEFTPADDING,
          localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/CharacterCreation/TextureQualityTooltip'))]
        if message is not None:
            graphicsData2 += [('text', message, 'dlMessage')]
        if where:
            self.ParseData(graphicsData, where, validateEntries=0)
        if where2:
            self.ParseData(graphicsData2, where2, validateEntries=0)
            optSettingsPar = uicls.Container(name='optSettingsPar', parent=where2, align=uiconst.TOTOP, height=24)
            btn = uicls.Button(parent=optSettingsPar, label=localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/OptimizeSettings'), func=self.OpenOptimizeSettings, args=(), align=uiconst.CENTERTOP)
            bottomBtnPar = uicls.Container(name='bottomBtnPar', parent=where2, align=uiconst.CENTERBOTTOM, height=32)
            bottomLeftCounter = 0
            btn = uicls.Button(parent=bottomBtnPar, label=localization.GetByLabel('UI/Common/Buttons/Apply'), func=self.ApplyGraphicsSettings, args=(), pos=(bottomLeftCounter,
             0,
             0,
             0))
            bottomLeftCounter += btn.width + 2
            btn = uicls.Button(parent=bottomBtnPar, label=localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ResetGraphicSettings'), func=self.ResetGraphicsSettings, args=(), pos=(bottomLeftCounter,
             0,
             0,
             0))
            bottomLeftCounter += btn.width + 2
            bottomBtnPar.width = bottomLeftCounter



    def OpenOptimizeSettings(self):
        optimizeWnd = form.OptimizeSettingsWindow.GetIfOpen()
        if optimizeWnd is None:
            self.optimizeWnd = weakref.proxy(form.OptimizeSettingsWindow.Open())
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
        prefs.incarnaGraphicsQuality = deviceSvc.GetDefaultInteriorGraphicsQuality()
        prefs.shadowQuality = deviceSvc.GetDefaultShadowQuality()
        settings.public.device.Set('MultiSampleType', 0)
        settings.public.device.Set('MultiSampleQuality', 0)
        settings.user.ui.Set('turretsEnabled', 1)
        settings.user.ui.Set('effectsEnabled', 1)
        settings.user.ui.Set('missilesEnabled', 1)
        settings.user.ui.Set('trailsEnabled', 1)
        settings.user.ui.Set('lod', 1)
        settings.public.device.Set('sunOcclusion', 1)
        settings.user.ui.Set('advancedCamera', 0)
        settings.user.ui.Set('cameraOffset', 0)
        prefs.SetValue('loadstationenv2', 1)
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
        interiorShaderQuality = prefs.GetValue('interiorShaderQuality', deviceSvc.GetDefaultInteriorShaderQuality())
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
        if interiorShaderQuality > 0 != trinity.HasGlobalSituationFlag('OPT_INTERIOR_SM_HIGH'):
            changes.append('interiorShaderQuality')
            if interiorShaderQuality == 0:
                trinity.RemoveGlobalSituationFlags(['OPT_INTERIOR_SM_HIGH'])
            else:
                trinity.AddGlobalSituationFlags(['OPT_INTERIOR_SM_HIGH'])
            trinity.RebindAllShaderMaterials()
        resetTriggered = False
        if 'textureQuality' in changes:
            dev.mipLevelSkipCount = textureQuality
            dev.RefreshDeviceResources()
            resetTriggered = True
        if 'shaderQuality' in changes:
            message = uicls.Message(className='Message', parent=uicore.layer.modal, name='msgDeviceReset')
            message.ShowMsg(localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ApplyingSettings'))
            blue.synchro.SleepWallclock(200)
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
        categoryLabelDictionary = {'window': localization.GetByLabel('UI/SystemMenu/Shortcuts/WindowTab'),
         'combat': localization.GetByLabel('UI/SystemMenu/Shortcuts/CombatTab'),
         'general': localization.GetByLabel('UI/SystemMenu/Shortcuts/GeneralTab'),
         'navigation': localization.GetByLabel('UI/SystemMenu/Shortcuts/NavigationTab'),
         'modules': localization.GetByLabel('UI/SystemMenu/Shortcuts/ModulesTab'),
         'movement': localization.GetByLabel('UI/SystemMenu/Shortcuts/MovementTab'),
         'drones': localization.GetByLabel('UI/SystemMenu/Shortcuts/DronesTab')}
        for category in uicore.cmd.GetCommandCategoryNames():
            tabs.append([categoryLabelDictionary[category],
             None,
             parent,
             category])

        self.sr.shortcutTabs = uicls.TabGroup(name='tabs', parent=parent, padBottom=5, tabs=tabs, groupID='tabs', autoselecttab=1, idx=0)
        col2 = uicls.Container(name='column2', parent=parent)
        col2.isTabOrderGroup = 1
        shortcutoptions = uicls.Container(name='options', align=uiconst.TOBOTTOM, height=30, top=0, parent=col2, padding=(5, 0, 5, 0))
        btns = [(localization.GetByLabel('UI/SystemMenu/Shortcuts/EditShortcut'), self.OnEditShortcutBtnClicked, None), (localization.GetByLabel('UI/SystemMenu/Shortcuts/ClearShortcut'), self.OnClearShortcutBtnClicked, None)]
        btnGroup = uicls.ButtonGroup(btns=btns, parent=shortcutoptions, line=False, subalign=uiconst.BOTTOMLEFT)
        btn = uicls.Button(parent=shortcutoptions, label=localization.GetByLabel('UI/SystemMenu/Shortcuts/DefaultShortcuts'), func=self.RestoreShortcuts, top=0, align=uiconst.BOTTOMRIGHT)
        self.sr.active_cmdscroll = uicls.Scroll(name='availscroll', align=uiconst.TOALL, parent=col2, padLeft=8, multiSelect=False, id='active_cmdscroll')
        self.sr.shortcutsinited = 1



    def OnEditShortcutBtnClicked(self, *args):
        selected = self.sr.active_cmdscroll.GetSelected()
        if not selected:
            return 
        p = selected[0].panel
        p.Edit()



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
        uix.GetContainerHeader(localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/Header'), col1, 0)
        scroll = uicls.Scroll(parent=col1)
        scroll.name = 'suppressResetScroll'
        scroll.HideBackground()
        scrollList = []
        i = 0
        for each in settings.user.suppress.GetValues().keys():
            label = self.GetConfigName(each)
            entry = listentry.Get('Button', {'label': label,
             'caption': localization.GetByLabel('UI/SystemMenu/ResetSettings/Reset'),
             'OnClick': self.ConfigBtnClick,
             'args': (each,),
             'singleline': 0,
             'entryWidth': self.colWidth - 16})
            scrollList.append((label, entry))

        scrollList = uiutil.SortListOfTuples(scrollList)
        scroll.Load(contentList=scrollList, scrollTo=suppressScrollTo)
        col2 = uicls.Container(name='column2', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
        col2.isTabOrderGroup = 1
        uicls.Frame(parent=col2)
        uix.GetContainerHeader(localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/Header'), col2, (0, 1)[(i >= 12)])
        scroll = uicls.Scroll(parent=col2)
        scroll.name = 'defaultsResetScroll'
        scroll.HideBackground()
        scrollList = []
        lst = [{'label': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/WindowPosition'),
          'caption': localization.GetByLabel('UI/SystemMenu/ResetSettings/Reset'),
          'OnClick': self.ResetBtnClick,
          'args': 'windows'},
         {'label': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/WindowColors'),
          'caption': localization.GetByLabel('UI/SystemMenu/ResetSettings/Reset'),
          'OnClick': self.ResetBtnClick,
          'args': 'window color'},
         {'label': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/JukeboxPlaylist'),
          'caption': localization.GetByLabel('UI/SystemMenu/ResetSettings/Reset'),
          'OnClick': self.ResetBtnClick,
          'args': 'jukebox playlist'},
         {'label': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/ClearAllSettings'),
          'caption': localization.GetByLabel('UI/SystemMenu/ResetSettings/Clear'),
          'OnClick': self.ResetBtnClick,
          'args': 'clear settings'},
         {'label': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/ClearAllCacheFiles'),
          'caption': localization.GetByLabel('UI/SystemMenu/ResetSettings/Clear'),
          'OnClick': self.ResetBtnClick,
          'args': 'clear cache'}]
        if session.charid:
            lst.append({'label': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/ClearMailCache'),
             'caption': localization.GetByLabel('UI/SystemMenu/ResetSettings/Clear'),
             'OnClick': self.ResetBtnClick,
             'args': 'clear mail'})
        if hasattr(sm.GetService('LSC'), 'spammerList'):
            lst.append({'label': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/ClearISKSpammerList'),
             'caption': localization.GetByLabel('UI/SystemMenu/ResetSettings/Clear'),
             'OnClick': self.ResetBtnClick,
             'args': 'clear iskspammers'})
        for each in lst:
            scrollList.append(listentry.Get('Button', {'label': each['label'],
             'caption': each['caption'],
             'OnClick': each['OnClick'],
             'args': (each['args'],),
             'singleline': 0,
             'entryWidth': self.colWidth - 16}))

        scroll.Load(contentList=scrollList, scrollTo=suppressScrollTo)
        tutorials = sm.GetService('tutorial').GetTutorials()
        if tutorials:
            col3 = uicls.Container(name='column3', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
            col3.isTabOrderGroup = 1
            uicls.Frame(parent=col3)
            uix.GetContainerHeader(localization.GetByLabel('UI/SystemMenu/ResetSettings/Tutorial/Header'), col3, 0)
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
                    label = localization.GetByMessageID(tutorials[tutorialID].tutorialNameID)
                    entry = listentry.Get('Button', {'label': label,
                     'caption': localization.GetByLabel('UI/SystemMenu/ResetSettings/Reset'),
                     'OnClick': self.TutorialResetBtnClick,
                     'args': (tutorialID,),
                     'singleline': 0,
                     'entryWidth': self.colWidth - 16})
                    scrollList.append((label, entry))

            scrollList = uiutil.SortListOfTuples(scrollList)
            scroll.Load(contentList=scrollList, scrollTo=scrollTo)
        self.sr.resetsettingsinited = 1



    def RefreshLanguage(self):
        self.sr.languageinited = 0
        sm.ChainEvent('ProcessUIRefresh')
        sm.ScatterEvent('OnUIRefresh')



    def Language(self):
        if self.sr.languageinited:
            return 
        parent = uiutil.GetChild(self.sr.wnd, 'language_container')
        if boot.region != 'optic' or eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            langs = localization.GetLanguages()
            if len(langs) > 1:
                column1 = uicls.Container(name='language_column_1', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
                column1.isTabOrderGroup = 1
                uicls.Frame(parent=column1)
                languageData = [('header', localization.GetByLabel('UI/SystemMenu/Language/Header'))]
                self.ParseData(languageData, column1)
                for lang in langs:
                    convertedID = localizationUtil.ConvertToLanguageSet('languageID', 'MLS', lang)
                    if convertedID == 'JA':
                        text = localization.GetByLabel('UI/SystemMenu/Language/LanguageJapanese')
                    else:
                        text = localizationUtil.GetDisplayLanguageName(lang, lang)
                    checkbox = uicls.Checkbox(parent=column1, name='languageCheckbox_%s' % lang, text=text, retval=convertedID, groupname='languageSelection', checked=convertedID == (session.languageID if session.userid else prefs.languageID), fontsize=12, configName='language', callback=self.OnCheckBoxChange)

        column2 = uicls.Container(name='language_column_2', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
        column2.isTabOrderGroup = 1
        uicls.Frame(parent=column2)
        if boot.region != 'optic' or eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            columnData = [('header', localization.GetByLabel('UI/SystemMenu/Language/InputMethodEditor/Header')), ('checkbox', ('nativeIME', ('user', 'ui'), True), localization.GetByLabel('UI/SystemMenu/Language/InputMethodEditor/UseEveIME'))]
            self.ParseData(columnData, column2)
        columnData = [('header', localization.GetByLabel('UI/SystemMenu/Language/VoiceOptions/Header')), ('checkbox', ('forceEnglishVoice', ('public', 'audio'), False), localization.GetByLabel('UI/SystemMenu/Language/VoiceOptions/ForceEnglishVoice'))]
        self.ParseData(columnData, column2)
        column3 = uicls.Container(name='language_column_3', align=uiconst.TOLEFT, width=self.colWidth, padLeft=8, parent=parent)
        column3.isTabOrderGroup = 1
        uicls.Frame(parent=column3)
        if session and session.role & service.ROLE_QA == service.ROLE_QA:
            self.DisplayLocalizationQAOptions(column2)
            sm.RemoteSvc('localizationServer').UpdateLocalizationQASettings(showHardcodedStrings=settings.user.localization.Get('showHardcodedStrings', 0), showMessageID=settings.user.localization.Get('showMessageID', 0), enableBoundaryMarkers=settings.user.localization.Get('enableBoundaryMarkers', 0), characterReplacementMethod=settings.user.localization.Get('characterReplacementMethod', 0), enableTextExpansion=settings.user.localization.Get('enableTextExpansion', 0))
            self.DisplayPseudolocalizationSample(column3)
        self.sr.languageinited = 1



    def DisplayLocalizationQAOptions(self, column):
        localizationQAOptions = [('header', 'Localization QA Options'),
         ('checkbox', ('showMessageID', ('user', 'localization'), settings.user.localization.Get('showMessageID', 0)), 'Show MessageID'),
         ('checkbox', ('enableBoundaryMarkers', ('user', 'localization'), settings.user.localization.Get('enableBoundaryMarkers', 0)), 'Show Boundary Markers'),
         ('checkbox', ('showHardcodedStrings', ('user', 'localization'), getattr(prefs, 'showHardcodedStrings', False)), 'Show Hardcoded Strings')]
        if session.languageID == 'EN':
            conversionMethodOptions = [('No Simulation', self.NO_PSEUDOLOCALIZATION_PRESET),
             ('Simulate German', localization.GERMAN_SIMULATION),
             ('Simulate Russian', localization.RUSSIAN_SIMULATION),
             ('Simulate Japanese', localization.JAPANESE_SIMULATION)]
            localizationQAOptions += [('combo',
              ('pseudolocalizationPreset', ('user', 'localization'), self.NO_PSEUDOLOCALIZATION_PRESET),
              'Simulation Preset',
              conversionMethodOptions,
              LEFTPADDING,
              'Simulation presets auto-configure the pseudolocalization settings to test for common localization issues.')]
            replacementMethodOptions = [('No Replacement', localization.NO_REPLACEMENT),
             ('Diacritic Replacement', localization.DIACRITIC_REPLACEMENT),
             ('Cyrillic Replacement', localization.CYRILLIC_REPLACEMENT),
             ('Full-Width Replacement', localization.FULL_WIDTH_REPLACEMENT)]
            localizationQAOptions += [('header', 'Localization QA: Advanced Settings'), ('combo',
              ('characterReplacementMethod', ('user', 'localization'), localization.NO_REPLACEMENT),
              'Char. Replacement',
              replacementMethodOptions,
              LEFTPADDING,
              'The character replacement method allows you to test for specific character rendering issues.'), ('checkbox', ('enableTextExpansion', ('user', 'localization'), settings.user.localization.Get('enableTextExpansion', 0)), 'Text Expansion Enabled')]
            if settings.user.localization.Get('enableTextExpansion', 0):
                localizationQAOptions += [('slider',
                  ('textExpansionAmount', ('user', 'localization'), 0.0),
                  'UI/SystemMenu/Language/LocalizationQAAdvanced/TextExpansion',
                  (0.0, 0.5),
                  SLIDERWIDTH)]
        self.ParseData(localizationQAOptions, column)



    def DisplayPseudolocalizationSample(self, column):
        if session.languageID == 'EN':
            pseudolocalizationSample = [('header', 'Localization QA: Sample Text')]
            self.ParseData(pseudolocalizationSample, column, validateEntries=0)
            self.pseudolocalizedSampleTextLabel = uicls.EveLabelMedium(name='pseudolocSample', text=self.GetPseudolocalizationSampleText(), parent=column, align=uiconst.TOTOP, padTop=2, padBottom=2, state=uiconst.UI_NORMAL)



    def SetPseudolocalizationSettingsByPreset(self, presetValue):
        if presetValue == self.NO_PSEUDOLOCALIZATION_PRESET:
            settings.user.localization.Set('characterReplacementMethod', localization.NO_REPLACEMENT)
            settings.user.localization.Set('enableTextExpansion', 0)
            settings.user.localization.Set('textExpansionAmount', 0.0)
            localizationUtil.SetPseudolocalization(False)
        elif presetValue == localization.GERMAN_SIMULATION:
            settings.user.localization.Set('characterReplacementMethod', localization.DIACRITIC_REPLACEMENT)
            settings.user.localization.Set('enableTextExpansion', 1)
            settings.user.localization.Set('textExpansionAmount', 0.3)
            localizationUtil.SetPseudolocalization(True)
        elif presetValue == localization.RUSSIAN_SIMULATION:
            settings.user.localization.Set('characterReplacementMethod', localization.CYRILLIC_REPLACEMENT)
            settings.user.localization.Set('enableTextExpansion', 1)
            settings.user.localization.Set('textExpansionAmount', 0.3)
            localizationUtil.SetPseudolocalization(True)
        elif presetValue == localization.JAPANESE_SIMULATION:
            settings.user.localization.Set('characterReplacementMethod', localization.FULL_WIDTH_REPLACEMENT)
            settings.user.localization.Set('enableTextExpansion', 1)
            settings.user.localization.Set('textExpansionAmount', 0.0)
            localizationUtil.SetPseudolocalization(True)



    def GetPseudolocalizationSampleText(self):
        return localization.GetByLabel('UI/SystemMenu/SampleText') + ''



    def AddSlider(self, where, config, minval, maxval, header, hint = '', usePrefs = 0, width = 160, height = 14, labelAlign = None, labelWidth = 0, startValue = None, step = None):
        uicls.Container(name='push', align=uiconst.TOTOP, height=[16, 4][(labelAlign is not None)], parent=where)
        _par = uicls.Container(name=config[0] + '_slider', align=uiconst.TOTOP, height=height, state=uiconst.UI_PICKCHILDREN, parent=where)
        par = uicls.Container(name=config[0] + '_slider_sub', parent=_par)
        slider = xtriui.Slider(parent=par, width=height, height=height)
        if labelAlign is not None:
            labelParent = uicls.Container(name='labelparent', parent=_par, align=labelAlign, width=labelWidth, idx=0)
            lbl = uicls.EveLabelSmall(text='', parent=labelParent, width=labelWidth, tabs=[labelWidth - 22], state=uiconst.UI_NORMAL)
            lbl._tabMargin = 0
        else:
            lbl = uicls.EveLabelSmall(text='', parent=par, width=200, top=-14, state=uiconst.UI_NORMAL)
        lbl.state = uiconst.UI_PICKCHILDREN
        lbl.name = 'label'
        slider.label = lbl
        slider.GetSliderValue = self.GetSliderValue
        slider.SetSliderLabel = self.SetSliderLabel
        slider.GetSliderHint = self.GetSliderHint
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
        label.text = localization.GetByLabel(dname)



    def GetSliderHint(self, idname, dname, value):
        if idname.startswith('wnd_'):
            return localizationUtil.FormatNumeric(int(value * 255))
        else:
            if idname == 'cameraOffset':
                return self.GetCameraOffsetHintText(value)
            if idname == 'incarnaCameraOffset':
                return self.GetCameraOffsetHintText(value, incarna=True)
            if idname == 'incarnaCameraMouseLookSpeedSlider':
                return self.GetCameraMouseSpeedHintText(value)
            return localizationUtil.FormatNumeric(int(value * 100))



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
        elif idname == 'textExpansionAmount':
            settings.user.localization.Set(idname, value)
            if getattr(self, 'pseudolocalizedSampleTextLabel', None) is not None and hasattr(self.pseudolocalizedSampleTextLabel, 'SetText'):
                self.pseudolocalizedSampleTextLabel.SetText(self.GetPseudolocalizationSampleText())



    def EnableDisableBreakpad(self, checkbox):
        try:
            try:
                blue.EnableBreakpad(checkbox.checked)
            except RuntimeError:
                pass

        finally:
            prefs.SetValue('breakpadUpload', 1 if checkbox.checked else 0)




    def OnCheckBoxChange(self, checkbox):
        if checkbox.data.has_key('config'):
            config = checkbox.data['config']
            if config == 'language':
                langID = checkbox.data['value']
                if boot.region == 'optic' and not eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
                    langID = 'ZH'
                self.setlanguageID = langID
                self.LanguageCheck()
            elif config == 'audioEnabled':
                if checkbox.checked:
                    sm.GetService('audio').Activate()
                else:
                    sm.GetService('audio').Deactivate()
            elif config == 'suppressTurret':
                sm.StartService('audio').SetTurretSuppression(checkbox.checked)
            elif config == 'damageMessages':
                idx = checkbox.parent.children.index(checkbox) + 1
                state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][settings.user.ui.Get('damageMessages', 1)]
                for i in xrange(4):
                    checkbox.parent.children[(idx + i)].state = state

            elif config == 'windowidentification':
                sm.GetService('gameui').DoWindowIdentification()
            elif config == 'targetCrosshair':
                sm.GetService('bracket').Reload()
            elif config == 'advancedDevice':
                self.ProcessDeviceSettings(whatChanged='advancedDevice')
            elif config == 'voiceenabled':
                checkbox.Disable()
                if checkbox.checked:
                    if hasattr(self, 'voiceFontBtn'):
                        self.voiceFontBtn.Enable()
                    sm.GetService('vivox').Login()
                elif hasattr(self, 'voiceFontBtn'):
                    self.voiceFontBtn.Disable()
                sm.GetService('vivox').LogOut()
            elif config == 'talkChannelPriority':
                if not checkbox.checked:
                    sm.GetService('vivox').StopChannelPriority()
            elif config == 'hdrEnabled':
                if checkbox.checked:
                    prefs.hdrEnabled = 1
                    self.ProcessGraphicsSettings()
                else:
                    prefs.hdrEnabled = 0
                    self.ProcessGraphicsSettings()
            if config == 'fastCharacterCreation':
                if checkbox.checked:
                    prefs.fastCharacterCreation = 1
                    self.ProcessGraphicsSettings()
                else:
                    prefs.fastCharacterCreation = 0
                    self.ProcessGraphicsSettings()
            elif config == 'charClothSimulation':
                prefs.charClothSimulation = checkbox.checked
                sm.GetService('sceneManager').ApplyClothSimulationSettings()
            if config == 'bloomEnabled':
                if checkbox.checked:
                    prefs.bloomEnabled = 1
                    self.ProcessGraphicsSettings()
                else:
                    prefs.bloomEnabled = 0
                    self.ProcessGraphicsSettings()
            elif config == 'resourceCacheEnabled':
                prefs.resourceCacheEnabled = bool(checkbox.checked)
                self.ProcessGraphicsSettings()
            elif config == 'loadstationenv2':
                oldVal = prefs.GetValue('loadstationenv2', 1)
                prefs.SetValue('loadstationenv2', 1 if checkbox.checked else 0)
                if sm.GetService('viewState').IsViewActive('hangar') and oldVal:
                    sm.GetService('station').ReloadLobby()
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/NeedToEnterCQ')})
            if config == 'turretsEnabled':
                if checkbox.checked:
                    sm.GetService('FxSequencer').EnableGuids(FxSequencer.fxTurretGuids)
                else:
                    sm.GetService('FxSequencer').DisableGuids(FxSequencer.fxTurretGuids)
            elif config == 'effectsEnabled':
                candidateEffects = []
                for guid in FxSequencer.fxGuids:
                    if guid not in FxSequencer.fxTurretGuids and guid not in FxSequencer.fxProtectedGuids:
                        candidateEffects.append(guid)

                if len(candidateEffects) > 0:
                    if checkbox.checked:
                        sm.GetService('FxSequencer').EnableGuids(candidateEffects)
                    else:
                        sm.GetService('FxSequencer').DisableGuids(candidateEffects)
            elif config == 'trailsEnabled':
                trinity.settings.SetValue('eveSpaceObjectTrailsEnabled', checkbox.checked)
            if config == 'enableTextExpansion':
                self.RefreshLanguage()
            elif config in ('showMessageID', 'enableBoundaryMarkers'):
                self.RefreshLanguage()
                sm.RemoteSvc('localizationServer').UpdateLocalizationQASettings(showHardcodedStrings=settings.user.localization.Get('showHardcodedStrings', 0), showMessageID=settings.user.localization.Get('showMessageID', 0), enableBoundaryMarkers=settings.user.localization.Get('enableBoundaryMarkers', 0), characterReplacementMethod=settings.user.localization.Get('characterReplacementMethod', 0), enableTextExpansion=settings.user.localization.Get('enableTextExpansion', 0))
            elif config == 'showHardcodedStrings':
                localizationUtil.SetHardcodedStringDetection(checkbox.checked)
                self.RefreshLanguage()



    def GetConfigName(self, suppression):
        configTranslation = {'AgtDelayMission': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/DelayMissionOfferDecision'),
         'AgtMissionOfferWarning': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentMissionOfferWarning'),
         'AgtMissionAcceptBigCargo': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentMissionAcceptsBigCargo'),
         'AgtDeclineMission': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentMissionDeclineWarning'),
         'AgtDeclineOnlyMission': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentDeclineOnlyMissionWarning'),
         'AgtDeclineImportantMission': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentDeclineImportantMissionWarning'),
         'AgtDeclineMissionSequence': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentDeclineMissionSequenceWarning'),
         'AgtQuitMission': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentQuitMissionWarning'),
         'AgtQuitImportantMission': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentQuitImportantMissionWarning'),
         'AgtQuitMissionSequence': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentQuitMissionSequenceWarning'),
         'AgtShare': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentShare'),
         'AgtNotShare': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentNotSharing'),
         'AskPartialCargoLoad': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/PartialCargoLoad'),
         'AidWithEnemiesEmpire2': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AidEnemiesInEmpireSpaceWarning'),
         'AidOutlawEmpire2': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AidOutlawInEmpireSpaceWarning'),
         'AidGlobalCriminalEmpire2': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AidCriminalInEmpireSpaceWarning'),
         'AttackInnocentEmpire2': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AttackInnocentPlayerInEmpireSpaceConfirmation'),
         'AttackInnocentEmpireAbort1': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AttackInnocentPlayerInEmpireSpaceConfirmation'),
         'AttackGoodNPC2': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AttackGoodPlayerConfirmation'),
         'AttackGoodNPCAbort1': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AttackGoodPlayerConfirmation'),
         'AttackAreaEmpire3': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AreaOfEffectModuleInEmpireSpaceConfirmation'),
         'AttackAreaEmpireAbort1': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AreaOfEffectModuleInEmpireSpaceConfirmation'),
         'AttackNonEmpire2': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AttackPlayerOwnedStuffConfirmation'),
         'AttackNonEmpireAbort1': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AttackPlayerOwnedStuffConfirmation'),
         'ConfirmOneWayItemMove': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/OneWayItemMoveConfirmation'),
         'ConfirmJumpToUnsafeSS': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/JumpToUnsafeSolarSystemConfirmation'),
         'ConfirmJettison': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/JettisonItemsConfirmation'),
         'AskQuitGame': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/QuitGameConfirmation'),
         'facAcceptEjectMaterialLoss': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/EjectBluePrintFromFactoryConformation'),
         'WarnDeleteFromAddressbook': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/DeleteFromAddressBookWarning'),
         'ConfirmDeleteFolder': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/DeleteFoldersConfirmation'),
         'AskCancelContinuation': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/ModifyCharacterConfirmation'),
         'ConfirmClearText': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/ClearTextConfirmation'),
         'ConfirmAbandonDrone': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AbandonDroneConfirmation'),
         'QueueSaveChangesOnClose': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/TrainingQueueChanges'),
         'PI_Info': localization.GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/PlanetaryInteractionInfo')}
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
            ret = uix.NamePopup(localization.GetByLabel('UI/SystemMenu/ConvertEveTimeCodeHeader'), localization.GetByLabel('UI/SystemMenu/ConvertEveTimeCodeTypeInCode'), name, maxLength=KEY_LENGTH)

        if not ret:
            return 
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/SystemMenu/ConvertEveTimeCodeHeader'), '.', 1, 2)
        try:
            sm.RemoteSvc('userSvc').ConvertETCToPilotLicence(ret['name'])

        finally:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/SystemMenu/ConvertEveTimeCodeHeader'), '.', 2, 2)




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
                sm.GetService('gameui').SetLanguage(setlanguageID)
                if prefs.GetValue('suppressLanguageChangeRestart', 0):
                    eve.Message('CustomNotify', {'notify': 'Prefs override: Language changed without restart'})
                else:
                    appUtils.Reboot('language change')



    def StationUpdateCheck(self):
        if eve.session.stationid:
            if self.init_dockshipsanditems != settings.user.windows.Get('dockshipsanditems', 0):
                sm.GetService('station').ReloadLobby()
                sm.GetService('neocom').UpdateMenu()
            elif self.init_stationservicebtns != settings.user.ui.Get('stationservicebtns', 0):
                sm.GetService('station').ReloadLobby()




class CmdListEntry(listentry.Generic):
    __guid__ = 'listentry.CmdListEntry'
    __nonpersistvars__ = []

    def Startup(self, *args):
        listentry.Generic.Startup(self, args)
        self.sr.lock = uicls.Icon(icon='ui_22_32_30', parent=self, size=20, align=uiconst.CENTERRIGHT, state=uiconst.UI_HIDDEN, hint=localization.GetByLabel('UI/SystemMenu/Shortcuts/LockedShortcut'), ignoreSize=1)



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
        m = [(localization.GetByLabel('UI/SystemMenu/Shortcuts/EditShortcut'), self.Edit), (localization.GetByLabel('UI/SystemMenu/Shortcuts/ClearShortcut'), self.Clear)]
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
    default_windowID = 'VoiceFontSelection'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetWndIcon('ui_9_64_16', mainTop=-10)
        currentVoiceFont = settings.char.ui.Get('voiceFontName', localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/NoFontSelected'))
        self.SetCaption(localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/SelectedFont', selectedFont=currentVoiceFont))
        self.SetMinSize([240, 150])
        self.MakeUnResizeable()
        self.sr.windowCaption = uicls.CaptionLabel(text=localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/Header'), parent=self.sr.topParent, align=uiconst.RELATIVE, left=70, top=15, state=uiconst.UI_DISABLED, fontsize=18)
        self.voiceFonts = None
        sm.RegisterNotify(self)
        uthread.new(self.Display)



    def OnVoiceFontsReceived(self, voiceFontList):
        self.voiceFonts = [(localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/NoFontSelected'), 0)]
        voiceFontMenuLabelDictionary = {'distorted_female1': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/DistoredFemale1'),
         'distorted_female2': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/DistoredFemale2'),
         'distorted_male1': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/DistoredMale1'),
         'distorted_male2': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/DistoredMale2'),
         'female1': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/Female1'),
         'female2': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/Female2'),
         'female3': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/Female3'),
         'female4': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/Female4'),
         'female5': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/Female5'),
         'female2male': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/FemaleToMale'),
         'male1': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/Male1'),
         'male2': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/Male2'),
         'male3': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/Male3'),
         'male4': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/Male4'),
         'male5': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/Male5'),
         'male2female': localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/MaleToFemale')}
        for voiceFont in voiceFontList:
            if voiceFont[1] in voiceFontMenuLabelDictionary:
                label = voiceFontMenuLabelDictionary[voiceFont[1]]
                self.voiceFonts.append((label, voiceFont[0]))

        self.Display()



    def Display(self):
        self.height = 150
        self.width = 240
        uiutil.FlushList(self.sr.main.children[0:])
        self.sr.main = uiutil.GetChild(self, 'main')
        mainContainer = uicls.Container(name='mainContainer', parent=self.sr.main, align=uiconst.TOALL, padding=(3, 3, 3, 3))
        if self.voiceFonts is None:
            self.echoText = uicls.EveHeaderSmall(text=localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/ReceivingVoiceFonts'), parent=mainContainer, align=uiconst.TOTOP, padTop=2, state=uiconst.UI_NORMAL)
            sm.GetService('vivox').GetAvailableVoiceFonts()
        else:
            idx = sm.GetService('vivox').GetVoiceFont()
            self.combo = uicls.Combo(label=localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/VoiceFont'), parent=mainContainer, options=self.voiceFonts, name='voicefont', idx=idx, callback=self.OnComboChange, labelleft=100, align=uiconst.TOTOP, padTop=5)
            self.combo.SetHint(localization.GetByLabel('UI/SystemMenu/AudioAndChat/VoiceFont/VoiceFont'))
            self.combo.parent.state = uiconst.UI_NORMAL
        btns = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Common/Buttons/Apply'),
          self.Apply,
          (),
          66], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.CloseByUser,
          (),
          66]], parent=mainContainer, idx=0)



    def Apply(self, *args):
        settings.char.ui.Set('voiceFontName', self.combo.GetKey())
        sm.GetService('vivox').SetVoiceFont(self.combo.selectedValue)
        sm.ScatterEvent('OnVoiceFontChanged')
        self.CloseByUser(args)



    def OnComboChange(self, *args):
        pass




class OptimizeSettingsWindow(uicls.Window):
    __guid__ = 'form.OptimizeSettingsWindow'
    default_windowID = 'optimizesettings'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetWndIcon('ui_9_64_16', mainTop=-10)
        self.SetCaption(localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/Header'))
        self.SetMinSize([360, 240])
        self.MakeUnResizeable()
        self.sr.windowCaption = uicls.CaptionLabel(text=localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/Header'), parent=self.sr.topParent, align=uiconst.RELATIVE, left=70, top=15, state=uiconst.UI_DISABLED, fontsize=18)
        self.SetScope('all')
        main = self.sr.main
        optimizeSettingsOptions = [(localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsSelect'), None),
         (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsMemory'), 1),
         (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsPerformance'), 2),
         (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsQuality'), 3)]
        combo = self.combo = uicls.Combo(label='', parent=main, options=optimizeSettingsOptions, name='', select=None, callback=self.OnComboChange, labelleft=0, align=uiconst.TOTOP)
        combo.SetHint(localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsSelect'))
        combo.SetPadding(6, 0, 6, 0)
        self.messageArea = uicls.EditPlainText(parent=main, readonly=1, hideBackground=1, padding=6)
        self.messageArea.HideBackground()
        self.messageArea.RemoveActiveFrame()
        uicls.Frame(parent=self.messageArea, color=(0.4, 0.4, 0.4, 0.5))
        self.messageArea.SetValue(localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsSelectInfo'))
        btns = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Common/Buttons/Apply'),
          self.Apply,
          (),
          66], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.CloseByUser,
          (),
          66]], parent=main, idx=0)
        return self



    def OnComboChange(self, *args):
        idx = args[2]
        info = {1: localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsMemoryInfo'),
         2: localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsPerformanceInfo'),
         3: localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsQualityInfo')}.get(idx, localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsSelectInfo'))
        self.messageArea.SetValue(info)



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
            prefs.SetValue('fastCharacterCreation', 0)
            prefs.SetValue('charClothSimulation', 1)
            prefs.SetValue('charTextureQuality', 0)
            if eve.session.userid:
                settings.user.ui.Set('droneModelsEnabled', 1)
                settings.user.ui.Set('effectsEnabled', 1)
                settings.user.ui.Set('missilesEnabled', 1)
                settings.user.ui.Set('explosionEffectsEnabled', 1)
                settings.user.ui.Set('turretsEnabled', 1)
                settings.user.ui.Set('trailsEnabled', 1)
        elif value == 2:
            prefs.SetValue('textureQuality', 1)
            prefs.SetValue('shaderQuality', 1)
            prefs.SetValue('shadowQuality', 0)
            prefs.SetValue('hdrEnabled', 0)
            prefs.SetValue('postProcessingQuality', 0)
            prefs.SetValue('resourceCacheEnabled', 0)
            prefs.SetValue('lodQuality', 1)
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
                settings.user.ui.Set('trailsEnabled', 0)
        elif value == 1:
            prefs.SetValue('textureQuality', 2)
            prefs.SetValue('shaderQuality', 1)
            prefs.SetValue('shadowQuality', 0)
            prefs.SetValue('hdrEnabled', 0)
            prefs.SetValue('postProcessingQuality', 0)
            prefs.SetValue('resourceCacheEnabled', 0)
            prefs.SetValue('lodQuality', 2)
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
                settings.user.ui.Set('trailsEnabled', 0)
        self.CloseByUser()




