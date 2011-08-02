import service
import sys
import blue
import uthread
import trinity
import util
import log

class Const(object):

    def __init__(self, theDict):
        self._dict = theDict



    def __getattr__(self, attr):
        try:
            return self._dict[attr]
        except KeyError:
            raise AttributeError, 'our dict has no key ' + attr



    def __getitem__(self, key):
        return self._dict[key]




class AttribDict(dict):

    def __init__(self, other = {}):
        dict.__init__(self, other)



    def __getattr__(self, attr):
        return self[attr]



    def __setattr__(self, attr, val):
        self[attr] = val




class Rect(object):
    __slots__ = ['width', 'height', 'aspect']

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.aspect = float(width) / float(height)



    def __lt__(self, other):
        return self.aspect < other.aspect or self.aspect == other.aspect and self.width < other.width



    def __eq__(self, other):
        return self.width == other.width and self.height == other.height




class AdapterMode(AttribDict):
    __slots__ = ['rect']

    def __init__(self, other):
        AttribDict.__init__(self, other)
        self.rect = Rect(self.Width, self.Height)



    def __lt__(self, other):
        if self.rect < other.rect:
            return 1
        if self.rect > other.rect:
            return 0
        return self.Format < other.Format



    def __eq__(self, other):
        return self.rect == other.rect and self.Format == other.Format




def Uniq(seq):
    for i in xrange(len(seq)):
        if i >= len(seq):
            break
        while i + 1 < len(seq) and seq[i] == seq[(i + 1)]:
            del seq[i + 1]





class DeviceMgr(service.Service):
    __guid__ = 'svc.device'
    __servicename__ = 'device'
    __displayname__ = 'Device Service'
    __startupdependencies__ = ['settings']
    __exportedcalls__ = {'SetDevice': [],
     'GetSettings': [],
     'GetSaveMode': [],
     'ResetMonitor': [],
     'ToggleWindowed': [],
     'CreateDevice': [],
     'PrepareMain': [],
     'CurrentAdapter': [],
     'GetAdapters': [],
     'GetWindowModes': [],
     'GetAdapterResolutionsAndRefreshRates': [],
     'GetBackbufferFormats': [],
     'GetStencilFormats': [],
     'GetMultiSampleTypes': [],
     'GetMultiSampleQualityOptions': [],
     'GetPresentationIntervalOptions': []}
    __depthStencilFormatNameList__ = ['D3DFMT_D24S8',
     'D3DFMT_D24X4S4',
     'D3DFMT_D32',
     'D3DFMT_D24X8',
     'D3DFMT_D16',
     'D3DFMT_D15S1',
     'D3DFMT_D24FS8',
     'D3DFMT_D16_LOCKABLE',
     'D3DFMT_D32F_LOCKABLE',
     'D3DFMT_VERTEXDATA',
     'D3DFMT_INDEX16',
     'D3DFMT_INDEX32']

    def Run(self, memStream = None):
        self.LogInfo('Starting DeviceMgr')
        self.d3d = self.GetD3D()
        self.d3dconst = Const(self.d3d.D3DCONST)
        if settings.public.device.Get('vsync', 1):
            self.defaultPresentationInterval = self.d3dconst.D3DPRESENT_INTERVAL_DEFAULT
        else:
            self.defaultPresentationInterval = self.d3dconst.D3DPRESENT_INTERVAL_IMMEDIATE
        self.minimumSize = {'width': 1024,
         'height': 768}
        self.AppRun()



    def Initialize(self):
        self.d3d = self.GetD3D()
        self.d3dconst = Const(self.d3d.D3DCONST)
        consts = self.d3dconst
        self.formatTable = {'D3DFMT_A2R10G10B10': 'D3DFMT_A2R10G10B10',
         'D3DFMT_A8R8G8B8': 'D3DFMT_X8R8G8B8',
         'D3DFMT_X8R8G8B8': 'D3DFMT_X8R8G8B8',
         'D3DFMT_A1R5G5B5': 'D3DFMT_X1R5G5B5',
         'D3DFMT_X1R5G5B5': 'D3DFMT_X1R5G5B5',
         'D3DFMT_R5G6B5': 'D3DFMT_R5G6B5'}
        self.bbToDisplay = {}
        for (key, val,) in self.formatTable.items():
            self.bbToDisplay[consts[key]] = consts[val]

        self.displayToBb = {}
        for (key, val,) in self.bbToDisplay.items():
            self.displayToBb.setdefault(val, []).append(key)

        self.formatNames = self.formatTable.keys()
        self.validFormats = [ consts[name] for name in self.formatNames ]
        self.validDisplayFormats = self.displayToBb.keys()
        self.formatNameMap = {}
        for name in self.formatNames:
            self.formatNameMap[consts[name]] = name

        self.displayFormats = [ (self.GetFancyFormatName(name),
         name,
         consts[self.formatTable.get(name, name)],
         consts[name]) for name in self.formatTable.keys() ]
        preferedOrder = ('A2R10G10B10', 'X8R8G8B8', 'A8R8G8B8', 'R5G6B5', 'X1R5G5B5', 'A1R5G5B5')
        self.preferedFormats = [ consts[('D3DFMT_' + name)] for name in preferedOrder ]

        def CmpFormat(x, y):
            ix = self.preferedFormats.index(x[3])
            iy = self.preferedFormats.index(y[3])
            if ix > iy:
                return 1
            if ix < iy:
                return -1
            return 0


        self.displayFormats.sort(CmpFormat)
        self.depthStencilFormats = [ consts[name] for name in self.__depthStencilFormatNameList__ ]
        self.settingsBackup = None
        self.positionBackup = None
        self.resolutionBackup = None
        attempt = [(self.d3dconst.D3DDEVTYPE_HAL, ''), (self.d3dconst.D3DDEVTYPE_SW, '')]
        self.adapters = None
        while not self.adapters:
            for a in attempt:
                self.devtype = a[0]
                self.adapters = self.FindDeviceTypeAdapters(a[0], a[1])
                if self.adapters:
                    break

            if not self.adapters:
                self.d3d.Initialize()

        self.LogInfo('valid adapters: %s using device type %s' % (self.adapters, self.devtype))
        if self.devtype != self.d3dconst.D3DDEVTYPE_HAL:
            self.LogInfo('Warning, no HAL adapter found.')
        self.desktopMode = Const(self.d3d.GetAdapterDisplayMode(None))
        self.preFullScreenPosition = None



    def GetFancyFormatName(self, format):
        format = format.lower()
        bits = {}
        for key in 'rgbax':
            idx = format.find(key)
            bit = 0
            if key != -1:
                try:
                    bit = int(format[(idx + 1):(idx + 3)])
                except:
                    try:
                        bit = int(format[(idx + 1):(idx + 2)])
                    except:
                        pass
                    sys.exc_clear()
            bits[key] = bit

        totalbits = bits['r'] + bits['g'] + bits['b'] + bits['a'] + bits['x']
        fancy = mls.UI_GENERIC_DEVICEMGR7 % {'bit': bits['r'] + bits['g'] + bits['b']}
        if bits['a']:
            fancy += ' ' + mls.UI_GENERIC_DEVICEMGR8 % {'bit': bits['a']}
        if settings.public.device.Get('advancedDevice', 0):
            fancy += ' (%s)' % format.replace('d3dfmt_', '').upper()
        return fancy



    def GetFancyStencilName(self, format):
        format = format.lower().replace('d3dfmt_', '')
        if format.find('vertexdata') != -1:
            return mls.UI_GENERIC_DEVICEMGR3
        idx = format.find('index')
        if idx != -1:
            bit = 0
            try:
                bit = int(format[(idx + 1):(idx + 3)])
            except:
                try:
                    bit = int(format[(idx + 1):(idx + 2)])
                except:
                    pass
                sys.exc_clear()
            return mls.UI_GENERIC_DEVICEMGR4 % {'bit': bit}
        bits = {}
        for key in 'dsx':
            idx = format.find(key)
            bit = 0
            if idx != -1:
                try:
                    bit = int(format[(idx + 1):(idx + 3)])
                except:
                    try:
                        bit = int(format[(idx + 1):(idx + 2)])
                    except:
                        pass
                    sys.exc_clear()
            bits[key] = bit

        totalbits = bits['d'] + bits['s']
        fancy = mls.UI_GENERIC_DEVICEMGR5 % {'totalbits': totalbits}
        if bits['s']:
            fancy += ' ' + mls.UI_GENERIC_DEVICEMGR6 % {'bit': bits['s']}
        return fancy



    def GetFancySampleTypeName(self, sampletype):
        return {'D3DMULTISAMPLE_NONE': mls.UI_GENERIC_DISABLED,
         'D3DMULTISAMPLE_NONMASKABLE': mls.UI_GENERIC_DEVICEMGR2,
         'D3DMULTISAMPLE_2_SAMPLES': mls.UI_GENERIC_DEVICEMGR1,
         'D3DMULTISAMPLE_3_SAMPLES': mls.UI_GENERIC_DEVICEMGR1,
         'D3DMULTISAMPLE_4_SAMPLES': mls.UI_GENERIC_DEVICEMGR1,
         'D3DMULTISAMPLE_5_SAMPLES': mls.UI_GENERIC_DEVICEMGR1,
         'D3DMULTISAMPLE_6_SAMPLES': mls.UI_GENERIC_DEVICEMGR1,
         'D3DMULTISAMPLE_7_SAMPLES': mls.UI_GENERIC_DEVICEMGR1,
         'D3DMULTISAMPLE_8_SAMPLES': mls.UI_GENERIC_DEVICEMGR1,
         'D3DMULTISAMPLE_9_SAMPLES': mls.UI_GENERIC_DEVICEMGR1,
         'D3DMULTISAMPLE_10_SAMPLES': mls.UI_GENERIC_DEVICEMGR1,
         'D3DMULTISAMPLE_11_SAMPLES': mls.UI_GENERIC_DEVICEMGR1,
         'D3DMULTISAMPLE_12_SAMPLES': mls.UI_GENERIC_DEVICEMGR1,
         'D3DMULTISAMPLE_13_SAMPLES': mls.UI_GENERIC_DEVICEMGR1,
         'D3DMULTISAMPLE_14_SAMPLES': mls.UI_GENERIC_DEVICEMGR1,
         'D3DMULTISAMPLE_15_SAMPLES': mls.UI_GENERIC_DEVICEMGR1,
         'D3DMULTISAMPLE_16_SAMPLES': mls.UI_GENERIC_DEVICEMGR1}.get(sampletype.upper(), sampletype)



    def Stop(self, memStream = None):
        self.LogInfo('Stopping DeviceMgr')
        del self.d3dconst
        del self.d3d
        service.Service.Stop(self)



    def HandleResizeEvent(self, *args):
        triapp = trinity.app
        clientRect = triapp.GetClientRect(triapp.hwnd)
        width = clientRect.right - clientRect.left
        height = clientRect.bottom - clientRect.top
        deviceSettings = self.GetSettings()
        deviceSettings.BackBufferWidth = width
        deviceSettings.BackBufferHeight = height
        keepSettings = deviceSettings.Windowed and not triapp.isMaximized
        uthread.new(self.SetDevice, deviceSettings, keepSettings=keepSettings, updateWindowPosition=False)



    def ForceSize(self, width = 512, height = 512):
        deviceSettings = self.GetSettings()
        deviceSettings.BackBufferWidth = width
        deviceSettings.BackBufferHeight = height
        deviceSettings.Windowed = True
        triapp = trinity.app
        triapp.minimumWidth = width
        triapp.minimumHeight = height
        uthread.new(self.SetDevice, deviceSettings, updateWindowPosition=False)



    def CreateDevice(self):
        self.LogInfo('CreateDevice')
        if '/safemode' in blue.pyos.GetArg():
            self.SetToSafeMode()
        triapp = trinity.app
        triapp.title = uicore.triappargs['title']
        triapp.hideTitle = 1
        triapp.fullscreen = 0
        triapp.Create()
        triapp.minimumWidth = self.minimumSize['width']
        triapp.minimumHeight = self.minimumSize['height']
        dev = trinity.device
        while not dev.DoesD3DDeviceExist():
            try:
                self.Initialize()
                triapp = trinity.app
                trinity.device.disableAsyncLoad = not bool(settings.public.generic.Get('asyncLoad', 1))
                defaultScene = self.GetAppScene()
                dev.scene = blue.os.LoadObject(defaultScene)
                dev.scene.bgColor.SetRGB(0.0, 0.0, 0.0)
                dev.scene.display = 0
                if self.IsHDRSupported() and prefs.GetValue('hdrEnabled', self.GetDefaultHDRState()):
                    dev.hdrEnable = True
                else:
                    dev.hdrEnable = False
                self.SetResourceCacheSize()
                blue.os.sleeptime = 0
                blue.rot.cacheTimeout = 60 * settings.public.generic.Get('userotcache', 1)
                dev.mipLevelSkipCount = prefs.GetValue('textureQuality', self.GetDefaultTextureQuality())
                self.PrepareMain(True)
                trinity.SetShaderModel(self.GetAppShaderModel())
            except trinity.D3DERR_NOTAVAILABLE as e:
                sys.exc_clear()
                self.d3d.Initialize()

        if not blue.win32.IsTransgaming():
            resizeEventHandler = blue.BlueEventToPython()
            resizeEventHandler.handler = self.HandleResizeEvent
            triapp.resizeEventListener = resizeEventHandler
        for (k, v,) in self.GetAppSettings().iteritems():
            trinity.settings.SetValue(k, v)

        for dir in self.GetAppMipLevelSkipExclusionDirectories():
            trinity.AddMipLevelSkipExclusionDirectory(dir)




    def PrepareMain(self, muteExceptions = False):
        self.LogInfo('PrepareMain')
        safe = self.GetSaveMode().__dict__
        personal = settings.public.device.Get('DeviceSettings', safe).copy()
        safe.update(personal)
        triapp = trinity.app
        set = util.KeyVal()
        set.__doc__ = 'Device set'
        set.__dict__ = safe
        set.hDeviceWindow = triapp.GetHwnd()
        self.SetDevice(set, hideTitle=not set.Windowed, muteExceptions=muteExceptions)



    def ResetMonitor(self, fallback = 1, *args):
        self.LogInfo('ResetMonitor')
        set = self.GetSaveMode()
        self.SetDevice(set, fallback=fallback, hideTitle=not set.Windowed)



    def FindDeviceTypeAdapters(self, deviceType, filterBy = ''):
        result = []
        for adapter in range(self.d3d.GetAdapterCount()):
            description = self.d3d.GetAdapterIdentifier(adapter)['Description']
            if filterBy not in description:
                break
            for format in self.validFormats:
                displayFormat = self.bbToDisplay[format]
                if self.d3d.CheckDeviceType(adapter, deviceType, displayFormat, format, 0):
                    result.append(adapter)
                    break


        return result



    def GetValidVertexProcessing(self, adapter = 0):
        caps = self.d3d.GetDeviceCaps(adapter, self.devtype)
        c = self.d3dconst
        modes = {'software': c.D3DCREATE_SOFTWARE_VERTEXPROCESSING}
        if caps['DevCaps'] & c.D3DDEVCAPS_HWTRANSFORMANDLIGHT:
            modes['hardware'] = c.D3DCREATE_HARDWARE_VERTEXPROCESSING
            modes['mixed'] = c.D3DCREATE_MIXED_VERTEXPROCESSING
            if caps['DevCaps'] & c.D3DDEVCAPS_PUREDEVICE:
                modes['pure haredware'] = c.D3DCREATE_HARDWARE_VERTEXPROCESSING | c.D3DCREATE_PUREDEVICE
        return modes



    def GetValidDepthStencilFormats(self, adapter, displayFormat, backBufferFormat):
        c = self.d3dconst
        result = []
        for f in self.depthStencilFormats:
            if not self.d3d.CheckDeviceFormat(adapter, self.devtype, displayFormat, c.D3DUSAGE_DEPTHSTENCIL, c.D3DRTYPE_SURFACE, f):
                continue
            if not self.d3d.CheckDepthStencilMatch(adapter, self.devtype, displayFormat, backBufferFormat, f):
                continue
            result.append(f)

        return result



    def GetValidWindowedFormats(self, adapter = 0, displayFormat = None):
        if not displayFormat:
            displayFormat = self.desktopMode.Format
        c = self.d3dconst
        if displayFormat not in self.validFormats:
            return []
        result = []
        for bbFormat in self.preferedFormats:
            if not self.d3d.CheckDeviceType(adapter, self.devtype, displayFormat, bbFormat, 1):
                continue
            if not self.d3d.CheckDeviceFormat(adapter, self.devtype, displayFormat, c.D3DUSAGE_RENDERTARGET, c.D3DRTYPE_SURFACE, bbFormat):
                continue
            dsFormats = self.GetValidDepthStencilFormats(adapter, displayFormat, bbFormat)
            for dsFormat in dsFormats:
                result.append((bbFormat, dsFormat))


        return result



    def GetValidFullscreenModes(self, adapter = 0):
        result = []
        c = self.d3dconst
        for format in self.validFormats:
            displayFormat = self.bbToDisplay[format]
            if not self.d3d.CheckDeviceType(adapter, self.devtype, displayFormat, format, 0):
                continue
            if not self.GetValidDepthStencilFormats(adapter, displayFormat, format):
                continue
            modes = self.d3d.EnumAdapterModes(adapter, format)
            result.extend(modes)

        result = [ mode for mode in result if mode['Height'] > 0 if mode['Width'] > 0 ]
        result = [ AdapterMode(item) for item in result ]
        result.sort()
        Uniq(result)
        if not result:
            raise RuntimeError('No valid fullscreen modes found')
        return result



    def GetDefaultVertexProcessing(self, adapter = 0):
        vp = self.GetValidVertexProcessing(adapter)
        return vp.get('hardware', vp['software'])



    def GetDefaultWindowedMode(self, adapter = None, dim = None):
        self.LogInfo('GetDefaultWindowedMode')
        formats = self.GetValidWindowedFormats(adapter)
        self.LogInfo('Valid windowed formats:', formats)
        if not formats:
            return 
        if dim:
            (width, height,) = dim
        else:
            (width, height,) = (self.desktopMode.Width, self.desktopMode.Height)
        if width > self.desktopMode.Width or height > self.desktopMode.Height:
            return 
        displayFormat = self.desktopMode.Format
        chosen = None
        for bbFormat in self.displayToBb[displayFormat]:
            for f in formats:
                if f[0] == bbFormat:
                    chosen = f
                    break

            if chosen:
                break

        if not chosen:
            chosen = formats[0]
        (bbFormat, dsFormat,) = chosen
        self.LogInfo('Chosen format', bbFormat, dsFormat)
        result = {'Windowed': 1,
         'BackBufferFormat': bbFormat,
         'AutoDepthStencilFormat': dsFormat,
         'BackBufferWidth': width,
         'BackBufferHeight': height}
        return result



    def GetDefaultFullscreenMode(self, adapter, dim = None):
        self.LogInfo('GetDefaultFullscreenMode')
        modes = self.GetValidFullscreenModes(adapter)
        if dim:
            a = {}
            for mode in modes:
                aspect = float(mode.Width) / float(mode.Height)
                if aspect not in a:
                    a[aspect] = []
                a[aspect].append(mode)

            (width, height,) = dim
            aspect = float(width) / float(height)
            closest = None
            for other in a.keys():
                if closest is None or abs(other - aspect) < abs(closest - aspect):
                    closest = other

            modes = a[closest]
            greater = [ mode for mode in modes if mode.Height >= height if mode.Width >= width ]
            if greater:
                modes = greater
            else:
                modes.reverse()
            (width, height,) = (modes[0].Width, modes[0].Height)
        else:
            (width, height,) = (modes[-1].Width, modes[-1].Height)
        modes = [ mode for mode in modes if mode.Height == height if mode.Width == width ]
        dsFormat = None
        for bbFormat in self.preferedFormats:
            displayFormat = self.bbToDisplay[bbFormat]
            m = None
            for mode in modes:
                if mode.Format == displayFormat:
                    m = mode
                    break

            if not m:
                continue
            if not self.d3d.CheckDeviceType(adapter, self.devtype, displayFormat, bbFormat, 0):
                continue
            dsFormats = self.GetValidDepthStencilFormats(adapter, displayFormat, bbFormat)
            if not dsFormats:
                continue
            dsFormat = dsFormats[0]
            break

        if not dsFormat:
            raise RuntimeError('No Defautl Fullscreen mode found')
        result = {'Windowed': 0,
         'BackBufferFormat': bbFormat,
         'AutoDepthStencilFormat': dsFormat,
         'BackBufferWidth': width,
         'BackBufferHeight': height}
        return result



    def GetFailsafeMode(self, adapter, windowed, dimensions = None):
        desktopdim = (self.desktopMode.Width, self.desktopMode.Height)
        if not dimensions:
            dimensions = desktopdim
        mode = None
        if windowed:
            mode = self.GetDefaultWindowedMode(adapter, dimensions)
            if not mode:
                return 
        else:
            mode = self.GetDefaultFullscreenMode(adapter, dimensions)
        if not mode:
            mode = self.GetDefaultFullscreenMode(adapter, None)
        mode = Const(mode)
        presentation = AttribDict()
        presentation.BackBufferWidth = mode.BackBufferWidth
        presentation.BackBufferHeight = mode.BackBufferHeight
        presentation.BackBufferFormat = mode.BackBufferFormat
        presentation.AutoDepthStencilFormat = mode.AutoDepthStencilFormat
        presentation.Windowed = mode.Windowed
        presentation.BackBufferCount = 1
        presentation.MultiSampleType = self.d3dconst.D3DMULTISAMPLE_NONE
        presentation.MultiSampleQuality = 0
        presentation.SwapEffect = self.d3dconst.D3DSWAPEFFECT_DISCARD
        presentation.hDeviceWindow = None
        presentation.EnableAutoDepthStencil = 1
        presentation.Flags = self.d3dconst.D3DPRESENTFLAG_DISCARD_DEPTHSTENCIL
        presentation.FullScreen_RefreshRateInHz = 0
        presentation.PresentationInterval = self.defaultPresentationInterval
        creation = AttribDict()
        creation.Adapter = adapter
        creation.DeviceType = self.devtype
        vp = self.GetDefaultVertexProcessing(adapter)
        creation.BehaviorFlags = vp | self.d3dconst.D3DCREATE_FPU_PRESERVE
        creation.PresentationParameters = presentation
        return creation



    def ValidatePresentation(self, adapter, pp):
        pp = Const(pp)
        if pp.Windowed:
            selected = (pp.BackBufferFormat, pp.AutoDepthStencilFormat)
            valid = self.GetValidWindowedFormats(adapter)
            if valid and selected in valid:
                return 1
        else:
            valid = self.GetValidFullscreenModes(adapter)
            displayFormat = self.bbToDisplay[pp.BackBufferFormat]
            valid = [ item for item in valid if item.Format == displayFormat if item.Width == pp.BackBufferWidth if item.Height == pp.BackBufferHeight ]
            if valid:
                if pp.AutoDepthStencilFormat in self.GetValidDepthStencilFormats(adapter, displayFormat, pp.BackBufferFormat):
                    return 1
        return 0



    def FixupPresentation(self, adapter, pp):
        if self.ValidatePresentation(adapter, pp):
            return pp
        pp = AttribDict(pp)
        create = self.GetFailsafeMode(adapter, pp.Windowed, (pp.BackBufferWidth, pp.BackBufferHeight))
        if not create:
            create = self.GetFailsafeMode(adapter, 0, (pp.BackBufferWidth, pp.BackBufferHeight))
        return create.PresentationParameters



    def CreationToSettings(self, creation):
        set = util.KeyVal()
        set.__doc__ = 'Device set'
        for t in ['BackBufferFormat',
         'FullScreen_RefreshRateInHz',
         'Windowed',
         'BackBufferWidth',
         'BackBufferHeight',
         'BackBufferCount',
         'MultiSampleType',
         'MultiSampleQuality',
         'EnableAutoDepthStencil',
         'PresentationInterval',
         'hDeviceWindow',
         'SwapEffect',
         'Flags',
         'AutoDepthStencilFormat']:
            set.__dict__[t] = creation.PresentationParameters[t]

        set.Adapter = creation.Adapter
        set.DeviceType = creation.DeviceType
        set.BehaviorFlags = creation.BehaviorFlags
        return set



    def GetSaveMode(self):
        self.LogInfo('GetSaveMode')
        set = self.GetSettings()
        windowed = 0
        adapter = self.adapters[0]
        create = self.GetFailsafeMode(adapter, windowed, (trinity.device.adapterWidth, trinity.device.adapterHeight))
        if not create:
            create = self.GetFailsafeMode(adapter, not windowed, (trinity.device.adapterWidth, trinity.device.adapterHeight))
        return self.CreationToSettings(create)



    def GetPreferedResolution(self, windowed):
        if windowed:
            lastWindowed = settings.public.device.Get('WindowedResolution', None)
            if lastWindowed is not None:
                return lastWindowed
            else:
                return (trinity.device.adapterWidth, trinity.device.adapterHeight)
        else:
            lastFullScreen = settings.public.device.Get('FullScreenResolution', None)
            if lastFullScreen is not None:
                return lastFullScreen
            else:
                return (trinity.device.adapterWidth, trinity.device.adapterHeight)



    def ToggleWindowed(self, *args):
        self.LogInfo('ToggleWindowed')
        triapp = trinity.app
        set = self.GetSettings()
        if set.Windowed:
            wr = triapp.GetWindowRect()
            self.preFullScreenPosition = (wr.left, wr.top)
        set.FullScreen_RefreshRateInHz = [self.CurrentAdapter()['RefreshRate'], 0][(not set.Windowed)]
        set.Windowed = not set.Windowed
        (set.BackBufferWidth, set.BackBufferHeight,) = self.GetPreferedResolution(set.Windowed)
        self.SetDevice(set, hideTitle=not set.Windowed)



    def EnforceDeviceSettings(self, deviceSettings):
        advanced = settings.public.device.Get('advancedDevice', 0)
        deviceSettings.PresentationInterval = (self.defaultPresentationInterval, deviceSettings.PresentationInterval)[advanced]
        return deviceSettings



    def SetDevice(self, device, tryAgain = 1, fallback = 0, keepSettings = 1, hideTitle = None, userModified = False, muteExceptions = False, updateWindowPosition = True):
        if hideTitle is None:
            hideTitle = not device.Windowed
        self.LogInfo('SetDevice: tryAgain', tryAgain, 'fallback', fallback, 'keepSettings', keepSettings, 'hideTitle', hideTitle, 'deviceDict', device.__dict__)
        if not hasattr(self, 'd3d'):
            return 
        if not fallback:
            device = self.EnforceDeviceSettings(device)
        change = self.CheckDeviceDifference(device, getChange=1)
        dev = trinity.device
        if not change and tryAgain and dev.DoesD3DDeviceExist():
            return 
        sm.ChainEvent('ProcessDeviceChange')
        self.LogInfo('SetDevice: Found a difference')
        pr = []
        for (k, v,) in device.__dict__.items():
            pr.append((k, v))

        pr.sort()
        self.LogInfo(' ')
        self.LogInfo('-' * 100)
        self.LogInfo('SetDevice')
        self.LogInfo('-' * 100)
        for (k, v,) in pr:
            extra = ''
            if k in change:
                extra = '   >> this one changed, it was ' + str(change[k][0])
            self.LogInfo('        ' + str(k) + ':    ' + str(v) + extra)

        self.LogInfo('-' * 100)
        triapp = trinity.app
        if tryAgain:
            self.resolutionBackup = (trinity.device.adapterWidth, trinity.device.adapterHeight)
            self.settingsBackup = self.GetSettings()
            if self.settingsBackup.Windowed:
                wr = triapp.GetWindowRect()
                self.positionBackup = (wr.left, wr.top)
        try:
            triapp.hideTitle = hideTitle
            triapp.AdjustWindowForChange(device.Windowed, settings.public.device.Get('FixedWindow', False))
            self.LogInfo('before')
            self.LogInfo(repr(device.__dict__))
            if device.Adapter not in self.adapters:
                device.Adapter = self.adapters[0]
            device.__dict__.update(self.FixupPresentation(device.Adapter, device.__dict__))
            self.LogInfo('apter')
            self.LogInfo(repr(device.__dict__))
            if device.__dict__.has_key('BehaviorFlags'):
                behaviorFlags = device.BehaviorFlags
            else:
                behaviorFlags = self.d3dconst.D3DCREATE_FPU_PRESERVE
                vp = self.GetDefaultVertexProcessing(device.Adapter)
                behaviorFlags |= vp
            dev = trinity.device
            dev.viewport.width = device.BackBufferWidth
            dev.viewport.height = device.BackBufferHeight
            while True:
                try:
                    triapp.ChangeDevice(device.Adapter, behaviorFlags, self.devtype, device.__dict__)
                    break
                except trinity.D3DERR_DEVICELOST:
                    blue.pyos.synchro.Sleep(1000)

        except Exception as e:
            self.LogInfo(repr(device.__dict__))
            if tryAgain and self.settingsBackup:
                sys.exc_clear()
                self.LogInfo('SetDevice failed, trying again with backup settings')
                self.SetDevice(self.settingsBackup, 0, keepSettings=keepSettings)
                return 
            if not fallback:
                sys.exc_clear()
                self.LogInfo('SetDevice with backup settings failed, falling back to savemode')
                set = self.GetSaveMode()
                self.SetDevice(set, fallback=1, tryAgain=0, hideTitle=not set.Windowed, keepSettings=False)
                return 
            if muteExceptions:
                log.LogException()
                sys.exc_clear()
            self.LogInfo('SetDevice failed completely')
            self.LogInfo('-' * 100)
            self.LogInfo(' ')
            return 
        self.LogInfo(' ')
        self.SetBloom(dev)
        if updateWindowPosition:
            self.UpdateWindowPosition(device)
        else:
            wr = triapp.GetWindowRect()
            triapp.SetWindowPos(wr.left, wr.top)
        sm.ScatterEvent('OnSetDevice')
        trinity.device.ditherEnable = settings.public.device.Get('ditherbackbuffer', 1)
        if uicore.desktop:
            uicore.desktop.UpdateSize()
        if keepSettings:
            set = self.GetSettings()
            keep = set.__dict__
            del keep['hDeviceWindow']
            settings.public.device.Set('DeviceSettings', keep)
            self.settings.SaveSettings()
            self.LogInfo('Keeping device settings:', repr(keep))
            if set.Windowed:
                settings.public.device.Set('WindowedResolution', (set.BackBufferWidth, set.BackBufferHeight))
            else:
                settings.public.device.Set('FullScreenResolution', (set.BackBufferWidth, set.BackBufferHeight))
                if userModified and self.resolutionBackup and self.resolutionBackup != (set.BackBufferWidth, set.BackBufferHeight):
                    self.AskForConfirmation()
        sm.ScatterEvent('OnEndChangeDevice', change)
        unsupportedModels = ['SM_1_1', 'SM_2_0_LO', 'SM_2_0_HI']
        maxCardModel = trinity.GetMaxShaderModelSupported()
        if maxCardModel in unsupportedModels:
            ret = blue.win32.MessageBox(mls.UI_SHADER_MODEL_ERROR, 'Outdated graphics card detected', 48)
            blue.pyos.Quit('Shader Model version check failed.')



    def UpdateWindowPosition(self, set = None):
        if set is None:
            set = self.GetSettings()
        triapp = trinity.app
        (x, y,) = (0, 0)
        if set.Windowed:
            currentAdapter = self.CurrentAdapter()
            if self.preFullScreenPosition:
                (x, y,) = self.preFullScreenPosition
            else:
                x = (currentAdapter['Width'] - set.BackBufferWidth) / 2
                y = (currentAdapter['Height'] - set.BackBufferHeight) / 2 - 32
            x = max(0, min(x, currentAdapter['Width'] - set.BackBufferWidth))
            y = max(0, min(y, currentAdapter['Height'] - set.BackBufferHeight))
        triapp.SetWindowPos(x, y)



    def AskForConfirmation(self):
        loadingSvc = sm.GetService('loading')
        if hasattr(loadingSvc, 'CountDownWindow'):
            sm.GetService('loading').CountDownWindow(mls.UI_SHARED_KEEPCHANGES, 15000, self.KeepChanges, self.DiscardChanges, inModalLayer=1)



    def DiscardChanges(self, *args):
        if self.settingsBackup:
            self.SetDevice(self.settingsBackup)



    def KeepChanges(self, *args):
        pass



    def CheckDeviceDifference(self, set, getChange = 0):
        current = self.GetSettings()
        change = {}
        for (k, v,) in set.__dict__.items():
            if k in ('FullScreen_RefreshRateInHz', 'hDeviceWindow', '__doc__'):
                continue
            initvalue = getattr(current, k, 'not set')
            if initvalue == 'not set' or initvalue != v:
                if not getChange:
                    return (k, initvalue, v)
                change[k] = (initvalue, v)

        if getChange:
            return change
        return 0



    def ForceSetup(self, device, z = 0):
        behaviorFlags = self.d3dconst.D3DCREATE_FPU_PRESERVE
        vp = self.GetDefaultVertexProcessing(0)
        behaviorFlags |= vp
        dev = trinity.device
        dev.viewport.width = device.BackBufferWidth
        dev.viewport.height = device.BackBufferHeight
        triapp = trinity.app
        triapp.ChangeDevice(device.Adapter, behaviorFlags, self.devtype, device.__dict__)



    def GetSettings(self, *args):
        current = trinity.device.GetPresentParameters()
        triapp = trinity.app
        set = util.KeyVal()
        set.__doc__ = 'Device set'
        set.__dict__ = current
        set.Adapter = trinity.device.adapter
        if set.Adapter not in self.adapters:
            set.Adapter = self.adapters[0]
        set.hDeviceWindow = triapp.GetHwnd()
        set.SwapEffect = self.D3D().D3DCONST['D3DSWAPEFFECT_DISCARD']
        set.DeviceType = self.devtype
        if not self.IsShadowingSupported() or not prefs.GetValue('shadowsEnabled', self.GetDefaultShadowState()):
            set.Flags = self.D3D().D3DCONST['D3DPRESENTFLAG_DISCARD_DEPTHSTENCIL']
        else:
            set.Flags = 0
        vp = self.GetDefaultVertexProcessing(set.Adapter)
        set.BehaviorFlags = vp | self.D3D().D3DCONST['D3DCREATE_FPU_PRESERVE']
        return set



    def GetD3D(self):
        rot = blue.os.CreateInstance('blue.Rot')
        D3D = rot.GetInstance('tri:/Direct3D', 'trinity.TriDirect3D')
        return D3D



    def D3D(self):
        return self.d3d



    def CurrentAdapter(self, set = None):
        self.LogInfo('CurrentAdapter')
        set = set or self.GetSettings()
        return self.D3D().GetAdapterDisplayMode(set.Adapter)



    def GetAdapters(self):
        self.LogInfo('GetAdapters')
        options = []
        for i in xrange(self.D3D().GetAdapterCount()):
            identifier = self.D3D().GetAdapterIdentifier(i)
            options.append((identifier['Description'], i))

        return options



    def GetAdaptersEnumerated(self):
        self.LogInfo('GetAdapters')
        options = []
        for i in xrange(self.D3D().GetAdapterCount()):
            identifierDesc = self.D3D().GetAdapterIdentifier(i)['Description']
            identifierDesc += ' ' + str(i + 1)
            options.append((identifierDesc, i))

        return options



    def GetWindowModes(self):
        self.LogInfo('GetWindowModes')
        adapter = self.CurrentAdapter()
        if blue.win32.IsTransgaming() or self.GetFormatNameByConst(adapter['Format']) not in self.formatTable:
            return [(mls.UI_SHARED_FULLSCREEN, 0)]
        else:
            return [(mls.UI_SHARED_WINDOWMODE, 1), (mls.UI_SHARED_FULLSCREEN, 0)]



    def GetBackbufferFormats(self, set = None):
        self.LogInfo('GetBackbufferFormats')
        set = set or self.GetSettings()
        options = []
        for (fancyName, formatName, adapterFormatVal, formatVal,) in self.displayFormats:
            if set.Windowed:
                adapterFormatVal = self.CurrentAdapter()['Format']
                if formatName == 'D3DFMT_A2R10G10B10':
                    continue
            if not self.D3D().GetAdapterModeCount(set.Adapter, adapterFormatVal):
                continue
            if not self.D3D().CheckDeviceFormat(set.Adapter, set.DeviceType, adapterFormatVal, self.D3D().D3DCONST['D3DUSAGE_RENDERTARGET'], self.D3D().D3DCONST['D3DRTYPE_SURFACE'], formatVal):
                continue
            if self.D3D().CheckDeviceType(set.Adapter, set.DeviceType, adapterFormatVal, formatVal, set.Windowed):
                options.append((fancyName, formatVal))

        return options



    def GetFormatNameByConst(self, const):
        names = self.d3d.inverseConstants[const]
        for n in names:
            if n.startswith('D3DFMT'):
                return n




    def DebugRes(self):
        currentAdapter = self.CurrentAdapter()
        set = self.GetSettings()
        if set.Windowed:
            set.FullScreen_RefreshRateInHz = 0
            checkFormat = currentAdapter['Format']
        else:
            formatName = self.GetFormatNameByConst(set.BackBufferFormat)
            checkFormat = self.D3D().D3DCONST[self.formatTable.get(formatName, formatName)]
            if not set.FullScreen_RefreshRateInHz:
                set.FullScreen_RefreshRateInHz = currentAdapter['RefreshRate']



    def GetAdapterResolutionsAndRefreshRates(self, set = None):
        self.LogInfo('GetAdapterResolutionsAndRefreshRates')
        currentAdapter = self.CurrentAdapter()
        set = set or self.GetSettings()
        if set.Windowed:
            set.FullScreen_RefreshRateInHz = 0
            checkFormat = currentAdapter['Format']
        else:
            formatName = self.GetFormatNameByConst(set.BackBufferFormat)
            checkFormat = self.D3D().D3DCONST[self.formatTable.get(formatName, formatName)]
            if not set.FullScreen_RefreshRateInHz:
                set.FullScreen_RefreshRateInHz = currentAdapter['RefreshRate']
        options = []
        refresh = {}
        for ops in self.D3D().EnumAdapterModes(set.Adapter, checkFormat):
            if ops['Width'] < self.minimumSize['width'] or ops['Height'] < self.minimumSize['height']:
                continue
            if set.Windowed and ops['RefreshRate'] - trinity.device.adapterRefreshRate > 1:
                continue
            option = ('%sx%s' % (ops['Width'], ops['Height']), (ops['Width'], ops['Height']))
            if option not in options:
                options.append(option)
            if (ops['Width'], ops['Height']) not in refresh:
                refresh[(ops['Width'], ops['Height'])] = []
            if not set.Windowed and ops['RefreshRate'] not in refresh[(ops['Width'], ops['Height'])]:
                refresh[(ops['Width'], ops['Height'])].append(ops['RefreshRate'])

        option = ('%sx%s' % (currentAdapter['Width'], currentAdapter['Height']), (currentAdapter['Width'], currentAdapter['Height']))
        if option not in options:
            options.append(option)
        if (currentAdapter['Width'], currentAdapter['Height']) not in refresh:
            refresh[(currentAdapter['Width'], currentAdapter['Height'])] = [currentAdapter['RefreshRate']]
        resoptions = []
        if (set.BackBufferWidth, set.BackBufferHeight) in refresh:
            resoptions = [ (str(rr) + ' ' + mls.UI_GENERIC_SHORTHERTZ, rr) for rr in refresh[(set.BackBufferWidth, set.BackBufferHeight)] ]
        return (options, resoptions)



    def GetStencilFormats(self, set = None):
        self.LogInfo('GetStencilFormats')
        set = set or self.GetSettings()
        options = []
        for format in self.__depthStencilFormatNameList__:
            if not self.D3D().CheckDeviceFormat(set.Adapter, set.DeviceType, self.CurrentAdapter()['Format'], self.D3D().D3DCONST['D3DUSAGE_DEPTHSTENCIL'], self.D3D().D3DCONST['D3DRTYPE_SURFACE'], self.D3D().D3DCONST[format]):
                continue
            if self.D3D().CheckDepthStencilMatch(set.Adapter, set.DeviceType, self.CurrentAdapter()['Format'], set.BackBufferFormat, self.D3D().D3DCONST[format]):
                options.append((self.GetFancyStencilName(format), self.D3D().D3DCONST[format]))

        return options



    def GetMultiSampleTypes(self, set = None):
        self.LogInfo('GetMultiSampleTypes')
        set = set or self.GetSettings()
        options = []
        mst = [ item for item in self.d3d.constants.iterkeys() if item.startswith('D3DMULTISAMPLE') ]
        for sampletype in mst:
            ret = self.D3D().CheckDeviceMultiSampleType(set.Adapter, set.DeviceType, set.BackBufferFormat, set.Windowed, self.D3D().D3DCONST[sampletype])
            if not ret:
                continue
            options.append((self.GetFancySampleTypeName(sampletype), self.D3D().D3DCONST[sampletype]))

        return options



    def GetMultiSampleQualityOptions(self, settings = None, formats = None):
        self.LogInfo('GetMultiSampleQualityOptions')
        if settings is None:
            settings = self.GetSettings()
        if formats is None:
            formats = [settings.BackBufferFormat, settings.AutoDepthStencilFormat]
        (vID, dID,) = self.GetVendorIDAndDeviceID()
        options = [(mls.UI_GENERIC_DISABLED, (0, 0))]
        qualityLevelsSupported = {}
        for i in range(2, 9):
            supported = True
            for format in formats:
                qualityLevels = self.D3D().CheckDeviceMultiSampleType(settings.Adapter, settings.DeviceType, format, settings.Windowed, i)
                supported = supported and qualityLevels

            if supported:
                qualityLevelsSupported[i] = qualityLevels
                if i != 8 or vID != 4318:
                    options.append(('%sx' % i, (i, 0)))

        if vID == 4318:
            if qualityLevelsSupported.get(trinity.TRIMULTISAMPLE_4_SAMPLES, 0) > 2:
                options.append(('8x', (trinity.TRIMULTISAMPLE_4_SAMPLES, 2)))
            if qualityLevelsSupported.get(trinity.TRIMULTISAMPLE_8_SAMPLES, 0) > 0:
                options.append(('8xQ', (trinity.TRIMULTISAMPLE_8_SAMPLES, 0)))
            if qualityLevelsSupported.get(trinity.TRIMULTISAMPLE_4_SAMPLES, 0) > 4:
                options.append(('16x', (trinity.TRIMULTISAMPLE_4_SAMPLES, 4)))
            if qualityLevelsSupported.get(trinity.TRIMULTISAMPLE_8_SAMPLES, 0) > 2:
                options.append(('16xQ', (trinity.TRIMULTISAMPLE_8_SAMPLES, 2)))
        return options



    def GetMultiSampleOption(self, type, quality):
        (vID, dID,) = self.GetVendorIDAndDeviceID()
        if vID == 4318:
            options = {(0, 0): mls.UI_GENERIC_DISABLED,
             (2, 0): '2x',
             (3, 0): '3x',
             (4, 0): '4x',
             (5, 0): '5x',
             (6, 0): '6x',
             (7, 0): '7x',
             (4, 2): '8x',
             (8, 0): '8xQ',
             (4, 4): '16x',
             (8, 2): '16xQ'}
        else:
            options = {(0, 0): mls.UI_GENERIC_DISABLED,
             (2, 0): '2x',
             (3, 0): '3x',
             (4, 0): '4x',
             (5, 0): '5x',
             (6, 0): '6x',
             (7, 0): '7x',
             (8, 0): '8x'}
        return (options[(type, quality)], (type, quality))



    def GetPresentationIntervalOptions(self, set = None):
        self.LogInfo('GetPresentationIntervalOptions')
        set = set or self.GetSettings()
        options = []
        presentintvals = {'D3DPRESENT_INTERVAL_IMMEDIATE': mls.UI_SYSMENU_INTERVAL_IMMEDIATE,
         'D3DPRESENT_INTERVAL_DEFAULT': mls.UI_SYSMENU_INTERVAL_DEFAULT,
         'D3DPRESENT_INTERVAL_ONE': mls.UI_SYSMENU_INTERVAL_ONE}
        if not set.Windowed:
            presentintvals['D3DPRESENT_INTERVAL_TWO'] = mls.UI_SYSMENU_INTERVAL_TWO
            presentintvals['D3DPRESENT_INTERVAL_THREE'] = mls.UI_SYSMENU_INTERVAL_THREE
            presentintvals['D3DPRESENT_INTERVAL_FOUR'] = mls.UI_SYSMENU_INTERVAL_FOUR
        for (key, value,) in presentintvals.iteritems():
            options.append((value, self.D3D().D3DCONST[key]))

        return options



    def GetDepthBufferType(self, set = None):
        self.LogInfo('GetPresentationIntervalOptions')
        set = set or self.GetSettings()
        options = [mls.UI_SHARED_ZBUFFER, mls.UI_SHARED_WBUFFER]
        presentintvals = ['D3DZB_TRUE', 'D3DZB_USEW']
        options = zip(options, map(lambda intval: self.D3D().D3DCONST[intval], presentintvals))
        return options



    def SupportsSM3(self, adapter = 0):
        caps = self.D3D().GetDeviceCaps(adapter, self.devtype)
        vertexShaderVersion = caps['VertexShaderVersion']
        pixelShaderVersion = caps['PixelShaderVersion']
        return vertexShaderVersion >= 3.0 and pixelShaderVersion >= 3.0



    def SetBloom(self, dev = None):
        if not self.IsBloomSupported():
            return 
        bloomType = prefs.GetValue('bloomType', self.GetDefaultBloomType())
        try:
            if dev is None:
                dev = trinity.GetDevice()
            if bloomType == 0:
                dev.postProcess = None
            elif bloomType == 1:
                dev.postProcess = trinity.Load('res:/PostProcess/BloomExp.red')
                dev.postProcess.display = True
            elif bloomType == 3:
                dev.postProcess = trinity.Load('res:/PostProcess/BloomVivid.red')
                dev.postProcess.display = True
            self.bloomType = bloomType
        except Exception as e:
            dev.postProcess = None
            self.LogError('Error loading bloom file: ', e)



    def GetBloom(self):
        dev = trinity.device
        return getattr(self, 'bloomType', 0)



    def SetHdr(self, enabled):
        dev = trinity.GetDevice()
        if self.IsHDRSupported():
            if dev.hdrEnable != enabled:
                dev.hdrEnable = enabled



    def IsHdrEnabled(self):
        dev = trinity.device
        return bool(dev.hdrEnable and dev.postProcess)



    def GetShadowBufferSize(self):
        dev = trinity.device
        return dev.shadowBufferSize



    def SetResourceCacheSize(self):
        cacheSize = 1
        if prefs.GetValue('resourceCacheEnabled', self.GetDefaultResourceState()):
            textureQuality = prefs.GetValue('textureQuality', self.GetDefaultTextureQuality())
            if textureQuality == 2:
                cacheSize = 1
            elif textureQuality == 1:
                cacheSize = 32
            cacheSize = 128
        self.LogInfo('Setting resource cache size to', cacheSize, 'MB')
        dev = trinity.device
        MEG = 1048576
        finalSize = cacheSize * MEG
        blue.motherLode.maxMemUsage = finalSize
        return finalSize



    def GetResourceCacheSize(self):
        dev = trinity.device
        return dev.GetResourceCacheSize()



    def ResetDevice(self):
        dev = trinity.device
        self.SetHdr(bool(prefs.GetValue('hdrEnabled', self.GetDefaultHDRState())))
        dev.ResetDeviceResources()



    def SetToSafeMode(self):
        prefs.SetValue('textureQuality', 2)
        prefs.SetValue('shaderQuality', 1)
        prefs.SetValue('hdrEnabled', 0)
        prefs.SetValue('bloomType', 0)
        prefs.SetValue('shadowsEnabled', 0)
        prefs.SetValue('resourceCacheEnabled', 0)



    def GetVendorIDAndDeviceID(self):
        dev = trinity.GetDevice()
        identifier = self.D3D().GetAdapterIdentifier(dev.adapter)
        vendorID = identifier['VendorId']
        deviceID = identifier['DeviceId']
        return (vendorID, deviceID)



    def GetDefaultTextureQuality(self):
        if blue.win32.IsTransgaming():
            (vID, dID,) = self.GetVendorIDAndDeviceID()
            if vID == 32902 and dID == 10146:
                return 2
            else:
                if vID == 32902 and dID == 10754:
                    return 2
                if vID == 4098 and dID == 29063:
                    return 1
                if vID == 4098 and dID == 29125:
                    return 1
                if vID == 4318 and dID == 917:
                    return 1
                if vID == 4318 and dID == 913:
                    return 1
                return 0
        else:
            return 0



    def GetDefaultShaderQuality(self):
        if blue.win32.IsTransgaming():
            (vID, dID,) = self.GetVendorIDAndDeviceID()
            if vID == 32902 and dID == 10146:
                return 1
            else:
                if vID == 32902 and dID == 10754:
                    return 1
                if vID == 4098 and dID == 29063:
                    return 1
                if vID == 4098 and dID == 29125:
                    return 1
                if vID == 4318 and dID == 917:
                    return 1
                if vID == 4318 and dID == 913:
                    return 1
                return 3
        else:
            return 3



    def GetDefaultLodQuality(self):
        return 3



    def GetDefaultBloomType(self):
        return 0



    def GetDefaultHDRState(self):
        return 0



    def GetDefaultShadowState(self):
        if self.SupportsSM3():
            return 1
        else:
            return 0



    def GetDefaultResourceState(self):
        return 0



    def IsHDRSupported(self):
        if blue.win32.IsTransgaming():
            (vID, dID,) = self.GetVendorIDAndDeviceID()
            if vID == 32902 and dID == 10146:
                return False
            if vID == 32902 and dID == 10754:
                return False
            if vID == 4098 and dID == 29063:
                return False
            if vID == 4098 and dID == 29125:
                return False
            if vID == 4098 and dID == 29257:
                return False
            if vID == 4318 and dID == 917:
                return False
            if vID == 4318 and dID == 913:
                return False
        if self.SupportsSM3():
            return True
        else:
            return False



    def IsShadowingSupported(self):
        if blue.win32.IsTransgaming():
            (vID, dID,) = self.GetVendorIDAndDeviceID()
            if vID == 32902 and dID == 10146:
                return False
            if vID == 32902 and dID == 10754:
                return False
            if vID == 4098 and dID == 29063:
                return False
            if vID == 4098 and dID == 29125:
                return False
            if vID == 4098 and dID == 29257:
                return False
            if vID == 4318 and dID == 917:
                return False
            if vID == 4318 and dID == 913:
                return False
        if self.SupportsSM3():
            return True
        else:
            return False



    def IsBloomSupported(self):
        if blue.win32.IsTransgaming():
            (vID, dID,) = self.GetVendorIDAndDeviceID()
            if vID == 32902 and dID == 10146:
                return False
            if vID == 32902 and dID == 10754:
                return False
            if vID == 4098 and dID == 29063:
                return False
            if vID == 4098 and dID == 29125:
                return False
            if vID == 4098 and dID == 29257:
                return False
            if vID == 4318 and dID == 917:
                return False
            if vID == 4318 and dID == 913:
                return False
        return True



    def AppRun(self):
        pass



    def GetAppShaderModel(self):
        sm = None
        if settings.public.device.Get('shaderModelLow', 0):
            sm = 'SM_3_0_LO'
        else:
            sm = 'SM_3_0_HI'
        return sm



    def GetAppSettings(self):
        return {}



    def GetAppMipLevelSkipExclusionDirectories(self):
        return []



    def GetAppScene(self):
        return 'res:/Scene/emptyscene.blue'



    def GetAppFeatureState(self, featureName, featureDefault):
        return featureDefault




