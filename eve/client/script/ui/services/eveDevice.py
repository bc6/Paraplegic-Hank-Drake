import blue
import trinity
import svc
from util import ReadYamlFile
NVIDIA_VENDORID = 4318

class EveDeviceMgr(svc.device):
    __guid__ = 'svc.eveDevice'
    __replaceservice__ = 'device'

    def AppRun(self):
        if not settings.public.generic.Get('resourceUnloading', 1):
            trinity.SetEveSpaceObjectResourceUnloadingEnabled(0)
        self.defaultPresentationInterval = self.d3dconst.D3DPRESENT_INTERVAL_ONE
        self.deviceCategories = ReadYamlFile('res:/videoCardCategories.yaml')
        if prefs.GetValue('depthEffectsEnabled', self.GetDefaultDepthEffectsEnabled()) and not self.SupportsDepthEffects():
            prefs.SetValue('depthEffectsEnabled', False)
        if prefs.HasKey('shadowsEnabled'):
            shadowsEnabled = prefs.GetValue('shadowsEnabled')
            if not prefs.HasKey('shadowQuality'):
                if not shadowsEnabled:
                    prefs.SetValue('shadowQuality', 0)
                else:
                    prefs.SetValue('shadowQuality', self.GetDefaultShadowQuality())
            prefs.DeleteValue('shadowsEnabled')
        if prefs.HasKey('bloomType'):
            bloomType = prefs.GetValue('bloomType')
            if not prefs.HasKey('postProcessingQuality'):
                if bloomType == 0 or bloomType == 1:
                    prefs.SetValue('postProcessingQuality', bloomType)
                else:
                    prefs.SetValue('postProcessingQuality', 2)
            prefs.DeleteValue('bloomType')
        if not prefs.HasKey('antiAliasing'):
            set = settings.public.device.Get('DeviceSettings', {}).copy()
            msType = set.get('MultiSampleType', 0)
            set['MultiSampleType'] = 0
            set['MultiSampleQuality'] = 0
            settings.public.device.Set('DeviceSettings', set)
            self.settings.SaveSettings()
            antiAliasing = 0
            if msType >= 8:
                antiAliasing = 3
            elif msType >= 4:
                antiAliasing = 2
            elif msType >= 2:
                antiAliasing = 1
            prefs.SetValue('antiAliasing', antiAliasing)



    def GetMSAATypeFromQuality(self, quality):
        if quality == 0:
            return 0
        if not hasattr(self, 'msaaTypes'):
            set = self.GetSettings()
            formats = [set.BackBufferFormat, set.AutoDepthStencilFormat, trinity.TRIFMT_A16B16G16R16F]
            self.GetMultiSampleQualityOptions(set, formats)
        if quality >= len(self.msaaTypes):
            quality = len(self.msaaTypes) - 1
        return self.msaaTypes[quality]



    def GetShaderModel(self, val):
        if val == 3:
            shaderModel = trinity.GetMaxShaderModelSupported()
            if prefs.GetValue('depthEffectsEnabled', self.GetDefaultDepthEffectsEnabled()):
                if shaderModel == 'SM_3_0_HI':
                    shaderModel = 'SM_3_0_DEPTH'
            return shaderModel
        return 'SM_3_0_LO'



    def GetWindowModes(self):
        self.LogInfo('GetWindowModes')
        adapter = self.CurrentAdapter()
        if self.GetFormatNameByConst(adapter['Format']) not in self.formatTable:
            return [(mls.UI_SHARED_FULLSCREEN, 0)]
        else:
            if blue.win32.IsTransgaming():
                return [(mls.UI_SHARED_WINDOWMODE, 1), (mls.UI_SHARED_FULLSCREEN, 0)]
            return [(mls.UI_SHARED_WINDOWMODE, 1), (mls.UI_SHARED_FULLSCREEN, 0), (mls.UI_SHARED_FIXEDWINDOW, 2)]



    def GetAppShaderModel(self):
        shaderQuality = prefs.GetValue('shaderQuality', self.GetDefaultShaderQuality())
        return self.GetShaderModel(shaderQuality)



    def GetAppSettings(self):
        settings = {}
        lodQuality = prefs.GetValue('lodQuality', self.GetDefaultLodQuality())
        if lodQuality == 1:
            settings = {'eveSpaceSceneVisibilityThreshold': 15.0,
             'eveSpaceSceneLowDetailThreshold': 140.0,
             'eveSpaceSceneMediumDetailThreshold': 480.0}
        elif lodQuality == 2:
            settings = {'eveSpaceSceneVisibilityThreshold': 6,
             'eveSpaceSceneLowDetailThreshold': 70,
             'eveSpaceSceneMediumDetailThreshold': 240}
        elif lodQuality == 3:
            settings = {'eveSpaceSceneVisibilityThreshold': 3.0,
             'eveSpaceSceneLowDetailThreshold': 35.0,
             'eveSpaceSceneMediumDetailThreshold': 120.0}
        return settings



    def GetAppMipLevelSkipExclusionDirectories(self):
        return ['res:/Texture/IntroScene', 'res:/UI/Texture']



    def GetAppScene(self):
        return 'res:/Scene/emptyscene.red'



    def IsWindowed(self, settings = None):
        if settings is None:
            settings = self.GetSettings()
        if blue.win32.IsTransgaming():
            return not sm.GetService('cider').GetFullscreen()
        return settings.Windowed



    def SetToSafeMode(self):
        prefs.SetValue('textureQuality', 2)
        prefs.SetValue('shaderQuality', 1)
        prefs.SetValue('hdrEnabled', 0)
        prefs.SetValue('postProcessingQuality', 0)
        prefs.SetValue('shadowQuality', 0)
        prefs.SetValue('resourceCacheEnabled', 0)



    def SetDevice(self, device, tryAgain = 1, fallback = 0, keepSettings = 1, hideTitle = None, userModified = False, muteExceptions = False, updateWindowPosition = True):
        svc.device.SetDevice(self, device, tryAgain, fallback, keepSettings, hideTitle, userModified, muteExceptions, updateWindowPosition)
        sm.GetService('cider').SetFullscreen(sm.GetService('cider').GetFullscreen())



    def ToggleWindowed(self, *args):
        if blue.win32.IsTransgaming():
            cider = sm.GetService('cider')
            cider.SetFullscreen(not cider.GetFullscreen())
        else:
            svc.device.ToggleWindowed(self, args)



    def GetMultiSampleQualityOptions(self, settings = None, formats = None):
        self.LogInfo('GetMultiSampleQualityOptions')
        if settings is None:
            settings = self.GetSettings()
        if formats is None:
            formats = [settings.BackBufferFormat, settings.AutoDepthStencilFormat]
        (vID, dID,) = self.GetVendorIDAndDeviceID()
        self.msaaOptions = [(mls.UI_GENERIC_DISABLED, 0)]
        self.msaaTypes = [0]

        def Supported(msType):
            supported = True
            for format in formats:
                qualityLevels = self.D3D().CheckDeviceMultiSampleType(settings.Adapter, settings.DeviceType, format, settings.Windowed, msType)
                supported = supported and qualityLevels

            return supported


        if Supported(2):
            self.msaaOptions.append((mls.UI_GENERIC_LOW, 1))
            self.msaaTypes.append(2)
        if Supported(4):
            self.msaaOptions.append((mls.UI_GENERIC_MEDIUM, 2))
            self.msaaTypes.append(4)
        if Supported(8):
            self.msaaOptions.append((mls.UI_GENERIC_HIGH, 3))
            self.msaaTypes.append(8)
        elif Supported(6):
            self.msaaOptions.append((mls.UI_GENERIC_HIGH, 3))
            self.msaaTypes.append(6)
        return self.msaaOptions



    def GetDefaultFastCharacterCreation(self):
        return 0



    def GetDefaultClothSimEnabled(self):
        shaderModel = trinity.GetShaderModel()
        if shaderModel.startswith('SM_3'):
            return 1
        else:
            return 0



    def GetDefaultCharTextureQuality(self):
        return 1



    def GetDefaultInteriorGraphicsQuality(self):
        return self.GetDeviceCategory()



    def EnforceDeviceSettings(self, settings):
        settings.BackBufferFormat = self.GetBackbufferFormats()[0][1]
        settings.AutoDepthStencilFormat = self.GetStencilFormats()[0][1]
        settings.MultiSampleType = 0
        settings.MultiSampleQuality = 0
        return settings



    def SupportsDepthEffects(self):
        return trinity.renderJobUtils.DeviceSupportsIntZ()



    def GetDefaultDepthEffectsEnabled(self):
        return trinity.renderJobUtils.DeviceSupportsIntZ() and not trinity.GetMaxShaderModelSupported().startswith('SM_2')



    def GetDefaultShadowQuality(self):
        return self.GetDeviceCategory()



    def GetDefaultPostProcessingQuality(self):
        if not self.IsBloomSupported():
            return 0
        return self.GetDeviceCategory()



    def GetAdapterResolutionsAndRefreshRates(self, set = None):
        (options, resoptions,) = svc.device.GetAdapterResolutionsAndRefreshRates(self, set)
        if set.Windowed:
            maxWidth = trinity.app.GetVirtualScreenWidth()
            maxHeight = trinity.app.GetVirtualScreenHeight()
            maxOp = ('%sx%s' % (maxWidth, maxHeight), (maxWidth, maxHeight))
            if maxOp not in options:
                options.append(maxOp)
        return (options, resoptions)



    def GetDeviceCategory(self):
        if self.CheckIfHighEndGraphicsDevice():
            return 2
        if self.CheckIfMediumGraphicsDevice():
            return 1
        if self.CheckIfLowEndGraphicsDevice():
            return 0
        return 2



    def CheckIfHighEndGraphicsDevice(self):
        identifier = trinity.d3d.GetAdapterIdentifier()
        if identifier is None:
            return False
        deviceID = identifier.get('DeviceId', None)
        vendorID = identifier.get('VendorId', None)
        return (vendorID, deviceID) in self.deviceCategories['high']



    def CheckIfMediumGraphicsDevice(self):
        identifier = trinity.d3d.GetAdapterIdentifier()
        if identifier is None:
            return False
        deviceID = identifier.get('DeviceId', None)
        vendorID = identifier.get('VendorId', None)
        return (vendorID, deviceID) in self.deviceCategories['medium']



    def CheckIfLowEndGraphicsDevice(self):
        identifier = trinity.d3d.GetAdapterIdentifier()
        if identifier is None:
            return False
        deviceID = identifier.get('DeviceId', None)
        vendorID = identifier.get('VendorId', None)
        return (vendorID, deviceID) in self.deviceCategories['low']



    def GetAppFeatureState(self, featureName, featureDefaultState):
        defaultInteriorGraphicsQuality = self.GetDefaultInteriorGraphicsQuality()
        interiorGraphicsQuality = prefs.GetValue('interiorGraphicsQuality', defaultInteriorGraphicsQuality)
        postProcessingQuality = prefs.GetValue('postProcessingQuality', self.GetDefaultPostProcessingQuality())
        shaderQuality = prefs.GetValue('shaderQuality', self.GetDefaultShaderQuality())
        shadowQuality = prefs.GetValue('shadowQuality', self.GetDefaultShadowQuality())
        if featureName == 'Interior.ParticlesEnabled':
            return interiorGraphicsQuality == 2
        else:
            if featureName == 'Interior.LensflaresEnabled':
                return interiorGraphicsQuality >= 1
            if featureName == 'Interior.lowSpecMaterialsEnabled':
                return interiorGraphicsQuality == 0
            if featureName == 'Interior.ssaoEnbaled':
                identifier = trinity.d3d.GetAdapterIdentifier()
                if identifier is not None:
                    vendorID = identifier.get('VendorId', None)
                    if vendorID != 4318:
                        return False
                return postProcessingQuality != 0 and shaderQuality > 1
            if featureName == 'Interior.dynamicShadows':
                return shadowQuality > 1
            if featureName == 'Interior.lightPerformanceLevel':
                return interiorGraphicsQuality
            if featureName == 'Interior.clothSimulation':
                identifier = trinity.d3d.GetAdapterIdentifier()
                if identifier is None:
                    return featureDefaultState
                vendorID = identifier.get('VendorId', None)
                return vendorID == NVIDIA_VENDORID and prefs.GetValue('charClothSimulation', featureDefaultState) and interiorGraphicsQuality == 2 and not blue.win32.IsTransgaming()
            if featureName == 'CharacterCreation.clothSimulation':
                return prefs.GetValue('charClothSimulation', featureDefaultState)
            return featureDefaultState




