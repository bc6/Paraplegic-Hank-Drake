from trinity.sceneRenderJobBase import SceneRenderJobBase
from trinity.renderJobUtils import renderTargetManager as rtm
import trinity
import blue
import log

def CreateSceneRenderJobSpace(name = None, stageKey = None):
    newRJ = SceneRenderJobSpace()
    if name is not None:
        newRJ.ManualInit(name)
    else:
        newRJ.ManualInit()
    newRJ.SetMultiViewStage(stageKey)
    return newRJ



class SceneRenderJobSpace(SceneRenderJobBase):
    renderStepOrder = ['UPDATE_SCENE1',
     'UPDATE_SCENE',
     'UPDATE_UI',
     'SET_CUSTOM_RT',
     'SET_DEPTH',
     'SET_VAR_DEPTH',
     'SET_VIEWPORT',
     'SET_PROJECTION',
     'SET_VIEW',
     'CLEAR',
     'RENDER_SCENE',
     'SET_SCENE1_STATES',
     'RENDER_SCENE1',
     'RJ_POSTPROCESSING',
     'SET_FINAL_RT',
     'FINAL_BLIT',
     'SET_VAR_GATHER',
     'FXAA_CLEAR',
     'FXAA',
     'POST_RENDER_CALLBACK',
     'RESTORE_DEPTH',
     'UPDATE_TOOLS',
     'RENDER_INFO',
     'RENDER_VISUAL',
     'RENDER_TOOLS',
     'RENDER_UI']
    multiViewStages = [('SETUP', True, ['SET_VIEWPORT',
       'CLEAR',
       'UPDATE_SCENE1',
       'UPDATE_SCENE',
       'SET_DEPTH',
       'SET_VAR_DEPTH']),
     ('SPACE_MAIN', False, ['SET_VIEWPORT',
       'SET_PROJECTION',
       'SET_VIEW',
       'RENDER_SCENE',
       'SET_SCENE1_STATES',
       'RENDER_SCENE1']),
     ('FINALIZE', True, ['RJ_POSTPROCESSING', 'SET_FINAL_RT', 'FINAL_BLIT']),
     ('TOOLS', False, ['SET_VIEWPORT',
       'SET_VIEW',
       'SET_PROJECTION',
       'UPDATE_TOOLS',
       'RENDER_INFO',
       'RENDER_VISUAL',
       'RENDER_TOOLS'])]
    visualizations = []
    renderTargetList = []

    def _ManualInit(self, name = 'SceneRenderJobSpace'):
        self.scene1 = None
        self.scene2 = None
        self.clientToolsScene = None
        self.activeSceneKey = None
        self.camera = None
        self.customBackBuffer = None
        self.customDepthStencil = None
        self.depthTexture = None
        self.hdrMSAATexture = None
        self.shadowMap = None
        self.postProcesses = []
        self.ui = None
        self.viewport = None
        self.hdrEnabled = False
        self.useBloom = False
        self.useShadows = False
        self.useDepth = False
        self.antiAliasingEnabled = False
        self.antiAliasingQuality = 0
        self.useFXAA = False
        self.fxaaEnabled = False
        self.fxaaQuality = 'FXAA_High'
        self.msaaEnabled = False
        self.msaaType = 4
        self.postProcessRJ = None
        self.bloomEffect = None
        self.fxaaEffect = None
        self.SetSettingsBasedOnPerformancePreferences()



    def Enable(self):
        SceneRenderJobBase.Enable(self)
        self.SetSettingsBasedOnPerformancePreferences()



    def SetScene1(self, scene):
        if scene is None:
            self.scene1 = None
        else:
            self.scene1 = blue.BluePythonWeakRef(scene)
        self.AddStep('UPDATE_SCENE1', trinity.TriStepUpdate(scene))
        self.AddStep('RENDER_SCENE1', trinity.TriStepRenderScene(scene))



    def GetScene1(self):
        if self.scene1 is None:
            return 
        else:
            return self.scene1.object



    def SetClientToolsScene(self, scene):
        if scene is None:
            self.clientToolsScene = None
        else:
            self.clientToolsScene = blue.BluePythonWeakRef(scene)
        self.AddStep('UPDATE_TOOLS', trinity.TriStepUpdate(scene))
        self.AddStep('RENDER_TOOLS', trinity.TriStepRenderScene(scene))



    def GetClientToolsScene(self):
        if self.clientToolsScene is None:
            return 
        else:
            return self.clientToolsScene.object



    def SetUI(self, ui):
        if ui is None:
            self.RemoveStep('UPDATE_UI')
            self.RemoveStep('RENDER_UI')
        else:
            self.AddStep('UPDATE_UI', trinity.TriStepUpdate(ui))
            self.AddStep('RENDER_UI', trinity.TriStepRenderUI(ui))



    def SetActiveCamera(self, camera):
        if camera is None:
            self.RemoveStep('SET_VIEW')
            self.RemoveStep('SET_PROJECTION')
        else:
            self.AddStep('SET_VIEW', trinity.TriStepSetView(None, camera))
            self.AddStep('SET_PROJECTION', trinity.TriStepSetProjection(camera.triProjection))



    def SetActiveScenes(self, scene1, scene2, key):
        self.activeSceneKey = key
        self.SetScene1(scene1)
        self.SetScene(scene2)
        if self.GetStep('RJ_POSTPROCESSING') is not None:
            self.AddStep('RJ_POSTPROCESSING', trinity.TriStepRunJob(self.CreatePostProcessRenderJob()))



    def _SetDepthMap(self):
        if self.GetScene() is None:
            return 
        if hasattr(self.GetScene(), 'depthTexture'):
            if self.msaaEnabled:
                self.GetScene().depthTexture = self.depthTexture
            else:
                self.GetScene().depthTexture = None



    def _SetShadowMap(self):
        if self.GetScene() is None:
            return 
        if self.useShadows:
            self.GetScene().shadowMap = self.shadowMap
        else:
            self.GetScene().shadowMap = None



    def EnablePostProcessing(self, enabled):
        if enabled:
            self.AddStep('RJ_POSTPROCESSING', trinity.TriStepRunJob(self.CreatePostProcessRenderJob()))
        else:
            self.RemoveStep('RJ_POSTPROCESSING')



    def EnablePostRenderCallbacks(self, enabled):
        if enabled:
            self.AddStep('POST_RENDER_CALLBACK', trinity.TriStepPostRenderCB())
        else:
            self.RemoveStep('POST_RENDER_CALLBACK')



    def AddPostProcess(self, id, path, sceneKey = None):
        entries = [ each for each in self.postProcesses if each[0] == id ]
        if len(entries) > 0:
            return 
        self.postProcesses.append((id,
         path,
         sceneKey,
         {}))
        if self.GetStep('RJ_POSTPROCESSING') is not None:
            self.AddStep('RJ_POSTPROCESSING', trinity.TriStepRunJob(self.CreatePostProcessRenderJob()))



    def RemovePostProcess(self, id):
        entries = [ each for each in self.postProcesses if each[0] == id ]
        for each in entries:
            self.postProcesses.remove(each)

        if self.GetStep('RJ_POSTPROCESSING') is not None:
            self.AddStep('RJ_POSTPROCESSING', trinity.TriStepRunJob(self.CreatePostProcessRenderJob()))



    def SetPostProcessVariable(self, id, variable, value):
        ppSteps = getattr(self.postProcessRJ, 'steps', [])
        entries = [ each for each in ppSteps if each.name == 'PostProcess ' + str(id) ]
        for each in entries:
            for stage in each.PostProcess.stages:
                for param in stage.parameters:
                    if param.name == variable:
                        param.value = value



        for each in self.postProcesses:
            if each[0] == id:
                each[3][variable] = value
                break




    def SetupPostProcess(self, rj, id, pp, variables):
        if self.hdrEnabled and self.msaaEnabled:
            step = rj.RenderPostProcess(pp, self.hdrMSAATexture.GetSurfaceLevel(0), self.hdrMSAATexture)
            step.name = 'PostProcess ' + str(id)
        elif self.hdrEnabled or self.fxaaEnabled:
            step = rj.RenderPostProcess(pp, self.customBackBuffer.GetSurfaceLevel(0), self.customBackBuffer)
            step.name = 'PostProcess ' + str(id)
        else:
            step = rj.RenderPostProcess(pp)
            step.name = 'PostProcess ' + str(id)
        for each in variables:
            self.SetPostProcessVariable(id, each, variables[each])




    def CreatePostProcessRenderJob(self):
        if not self.useBloom:
            return 
        self.postProcessRJ = rj = trinity.CreateRenderJob('PostProcessingJob')
        if self.msaaEnabled and not self.hdrEnabled:
            rj.CopySurfaceToRT(self.customBackBuffer, trinity.device.GetBackBuffer())
            rj.SetRenderTarget(trinity.device.GetBackBuffer())
        elif self.msaaEnabled:
            if self.hdrMSAATexture is None:
                return 
            rj.CopySurfaceToRT(self.customBackBuffer, self.hdrMSAATexture.GetSurfaceLevel(0))
        self.SetupPostProcess(rj, 'Bloom', self.bloomEffect, {})
        for (id, path, sceneKey, variables,) in self.postProcesses:
            if sceneKey == self.activeSceneKey or sceneKey is None:
                self.SetupPostProcess(rj, id, trinity.Load(path), variables)

        return rj



    def _SetScene(self, scene):
        self.currentMultiViewStageKey
        self.SetStepAttr('UPDATE_SCENE', 'object', scene)
        self.SetStepAttr('RENDER_SCENE', 'scene', scene)
        self.ApplyPerformancePreferencesToScene()



    def _CreateBasicRenderSteps(self):
        self.AddStep('UPDATE_SCENE1', trinity.TriStepUpdate(self.GetScene1()))
        self.AddStep('RENDER_SCENE1', trinity.TriStepRenderScene(self.GetScene1()))
        self.AddStep('UPDATE_SCENE', trinity.TriStepUpdate(self.GetScene()))
        self.AddStep('RENDER_SCENE', trinity.TriStepRenderScene(self.GetScene()))
        self.AddStep('SET_SCENE1_STATES', trinity.TriStepSetStdRndStates(trinity.RM_ALPHA_ADDITIVE))
        self.AddStep('CLEAR', trinity.TriStepClear((0.0, 0.0, 0.0, 0.0), 1.0))
        if self.clientToolsScene is not None:
            self.SetClientToolsScene(self.clientToolsScene.object)



    def DoReleaseResources(self, level):
        self.viewport = None
        self.hdrEnabled = False
        self.useBloom = False
        self.useShadows = False
        self.shadowMap = None
        self.depthTexture = None
        self.renderTargetList = None
        self.customBackBuffer = None
        self.customDepthStencil = None
        self.depthTexture = None
        self.hdrMSAATexture = None
        self._RefreshRenderTargets()



    def NotifyResourceCreationFailed(self):
        try:
            eve.Message('CustomError', {'error': mls.UI_SHARED_VIDEOMEMORYERROR})

        finally:
            pass




    def _DoPrepareResources(self):
        self.viewport = trinity.device.viewport
        width = self.viewport.width
        height = self.viewport.height
        self.useBloom = self.bloomEffect is not None
        if sm.IsServiceRunning('device'):
            settings = sm.GetService('device').GetSettings()
            defaultShaderQuality = sm.GetService('device').GetDefaultShaderQuality()
            isShadowingSupported = sm.GetService('device').IsShadowingSupported()
            self.hdrEnabled = bool(prefs.GetValue('hdrEnabled', sm.GetService('device').GetDefaultHDRState()))
            bbFormat = settings.BackBufferFormat
            dsFormat = settings.AutoDepthStencilFormat
        else:
            settings = trinity.device.GetPresentParameters()
            defaultShaderQuality = 3
            isShadowingSupported = True
            bbFormat = settings['BackBufferFormat']
            dsFormat = settings['AutoDepthStencilFormat']
            self.hdrEnabled = trinity.device.hdrEnable
        shaderQuality = prefs.GetValue('shaderQuality', defaultShaderQuality)
        self.useDepth = trinity.GetShaderModel().endswith('DEPTH')
        self._RefreshAntiAliasing()
        self._CreateRenderTargets()
        self._RefreshRenderTargets()



    def _CreateRenderTargets(self):
        self.viewport = trinity.device.viewport
        width = self.viewport.width
        height = self.viewport.height
        if sm.IsServiceRunning('device'):
            settings = sm.GetService('device').GetSettings()
            bbFormat = settings.BackBufferFormat
            dsFormat = settings.AutoDepthStencilFormat
        else:
            settings = trinity.device.GetPresentParameters()
            bbFormat = settings['BackBufferFormat']
            dsFormat = settings['AutoDepthStencilFormat']
        if self.hdrEnabled and self.msaaEnabled:
            if self._TargetDiffers(self.customBackBuffer, 'trinity.TriSurface', trinity.TRIFMT_A16B16G16R16F, self.msaaType):
                self.customBackBuffer = rtm.GetRenderTarget(0, width, height, trinity.TRIFMT_A16B16G16R16F, self.msaaType, 0, 0)
        elif self.hdrEnabled:
            if self._TargetDiffers(self.customBackBuffer, 'trinity.TriTextureRes', trinity.TRIFMT_A16B16G16R16F):
                self.customBackBuffer = rtm.GetTexture(0, width, height, 1, trinity.TRIUSAGE_RENDERTARGET, trinity.TRIFMT_A16B16G16R16F, trinity.TRIPOOL_DEFAULT)
        elif self.fxaaEnabled:
            if self._TargetDiffers(self.customBackBuffer, 'trinity.TriTextureRes', bbFormat):
                self.customBackBuffer = rtm.GetTexture(0, self.viewport.width, self.viewport.height, 1, trinity.TRIUSAGE_RENDERTARGET, bbFormat, trinity.TRIPOOL_DEFAULT)
        elif self.msaaEnabled:
            if self._TargetDiffers(self.customBackBuffer, 'trinity.TriSurface', bbFormat, self.msaaType):
                self.customBackBuffer = rtm.GetRenderTarget(0, width, height, bbFormat, self.msaaType, 0, 0)
        else:
            self.customBackBuffer = None
        if self.msaaEnabled:
            if self._TargetDiffers(self.customDepthStencil, 'trinity.TriSurface', dsFormat, self.msaaType):
                self.customDepthStencil = rtm.GetDepthStencil(0, width, height, dsFormat, self.msaaType, 0, 0)
        else:
            self.customDepthStencil = None
        if self.useDepth:
            if self._TargetDiffers(self.depthTexture, 'trinity.TriTextureRes', trinity.TRIFMT_INTZ):
                self.depthTexture = rtm.GetTexture(0, width, height, 1, trinity.TRIUSAGE_DEPTHSTENCIL, trinity.TRIFMT_INTZ, trinity.TRIPOOL_DEFAULT)
        else:
            self.depthTexture = None
        if self.hdrEnabled and self.msaaEnabled and self.useBloom:
            if self._TargetDiffers(self.hdrMSAATexture, 'trinity.TriTextureRes', trinity.TRIFMT_A16B16G16R16F):
                self.hdrMSAATexture = rtm.GetTexture(0, width, height, 1, trinity.TRIUSAGE_RENDERTARGET, trinity.TRIFMT_A16B16G16R16F, trinity.TRIPOOL_DEFAULT)
        else:
            self.hdrMSAATexture = None



    def _TargetDiffers(self, target, blueType, format, msType = 0):
        if target is None:
            return True
        if blueType != target.__bluetype__:
            return True
        if format != target.format:
            return True
        multiSampleType = getattr(target, 'multiSampleType', None)
        if multiSampleType is not None and multiSampleType != msType:
            return True
        return False



    def _RefreshRenderTargets(self):
        self.renderTargetList = (blue.BluePythonWeakRef(self.customBackBuffer),
         blue.BluePythonWeakRef(self.customDepthStencil),
         blue.BluePythonWeakRef(self.depthTexture),
         blue.BluePythonWeakRef(self.hdrMSAATexture))
        renderTargets = (x.object for x in self.renderTargetList)
        self.SetRenderTargets(*renderTargets)



    def _RefreshAntiAliasing(self):
        self.antiAliasingQuality = prefs.GetValue('antiAliasing', self.antiAliasingQuality)
        if sm.IsServiceRunning('device'):
            self.msaaQuality = sm.GetService('device').GetMSAATypeFromQuality(self.antiAliasingQuality)
        else:
            self.msaaQuality = 8
        self.fxaaQuality = self._GetFXAAQuality(self.antiAliasingQuality)
        if self.useFXAA:
            self.EnableFXAA(self.antiAliasingEnabled)
        else:
            self.EnableMSAA(self.antiAliasingEnabled)



    def UseFXAA(self, flag):
        self.useFXAA = flag
        if self.useFXAA:
            self.EnableMSAA(False)
        else:
            self.EnableFXAA(False)
        self._RefreshAntiAliasing()



    def EnableAntiAliasing(self, enable):
        self.antiAliasingEnabled = enable
        self._RefreshAntiAliasing()



    def EnableFXAA(self, enable):
        self.fxaaEnabled = enable
        if enable:
            if getattr(self, 'fxaaEffect', None) is None:
                self.fxaaEffect = trinity.Tr2ShaderMaterial()
                self.fxaaEffect.highLevelShaderName = 'PostProcess'
            self.fxaaEffect.defaultSituation = self.fxaaQuality
            self.fxaaEffect.BindLowLevelShader([])
            self.AddStep('FXAA', trinity.TriStepRenderFullScreenShader(self.fxaaEffect))
            if self.bloomEffect is None:
                self.AddStep('FXAA_CLEAR', trinity.TriStepClear((0, 0, 0, 1), 1.0))
            self.RemoveStep('FINAL_BLIT')
        else:
            self.RemoveStep('FXAA')
            self.RemoveStep('FXAA_CLEAR')
        if not self.enabled:
            return 
        self._CreateRenderTargets()
        self._RefreshRenderTargets()



    def EnableMSAA(self, enable):
        self.msaaEnabled = enable
        if not self.enabled:
            return 
        self._CreateRenderTargets()
        self._RefreshRenderTargets()



    def DoPrepareResources(self):
        if not self.enabled or not self.canCreateRenderTargets:
            return 
        try:
            self._DoPrepareResources()
        except trinity.D3DERR_OUTOFVIDEOMEMORY:
            log.LogException()
            self.DoReleaseResources(1)
            self.CreateRecoverySteps()
            uthread.new(self.NotifyResourceCreationFailed)



    def _GetFXAAQuality(self, quality):
        if quality == 3:
            return 'FXAA_High'
        if quality == 2:
            return 'FXAA_Medium'
        if quality == 1:
            return 'FXAA_LOW'
        return ''



    def SetSettingsBasedOnPerformancePreferences(self):
        if not self.enabled:
            return 
        aaQuality = prefs.GetValue('antiAliasing', 0)
        self.antiAliasingEnabled = aaQuality > 0
        self.antiAliasingQuality = aaQuality
        if sm.IsServiceRunning('device'):
            deviceSvc = sm.GetService('device')
            self.msaaQuality = sm.GetService('device').GetMSAATypeFromQuality(aaQuality)
            defaultPostProcessingQuality = deviceSvc.GetDefaultPostProcessingQuality()
            defaultShadowQuality = deviceSvc.GetDefaultShadowQuality()
            self.hdrEnabled = bool(prefs.GetValue('hdrEnabled', sm.GetService('device').GetDefaultHDRState()))
        else:
            self.msaaQuality = 8
            defaultPostProcessingQuality = 2
            defaultShadowQuality = 2
            self.hdrEnabled = trinity.device.hdrEnable
        self.fxaaQuality = self._GetFXAAQuality(aaQuality)
        self.useShadows = prefs.GetValue('shadowQuality', defaultShadowQuality) > 0
        if self.useShadows and self.shadowMap is None:
            self.shadowMap = trinity.TriShadowMap()
        elif not self.useShadows:
            self.shadowMap = None
        postProcessingQuality = prefs.GetValue('postProcessingQuality', defaultPostProcessingQuality)
        if postProcessingQuality == 0:
            self.bloomEffect = None
        elif postProcessingQuality == 1:
            self.bloomEffect = trinity.Load('res:/PostProcess/BloomExp.red')
        elif postProcessingQuality == 2:
            self.bloomEffect = trinity.Load('res:/PostProcess/BloomVivid.red')
        self.useBloom = self.bloomEffect is not None
        if self.GetStep('RJ_POSTPROCESSING') is not None:
            self.AddStep('RJ_POSTPROCESSING', trinity.TriStepRunJob(self.CreatePostProcessRenderJob()))
        self._RefreshAntiAliasing()
        self._CreateRenderTargets()
        self._RefreshRenderTargets()
        self.ApplyPerformancePreferencesToScene()



    def ApplyPerformancePreferencesToScene(self):
        self._SetShadowMap()
        self._SetDepthMap()



    def SetMultiViewStage(self, stageKey):
        self.currentMultiViewStageKey = stageKey



    def SetRenderTargets(self, customBackBuffer, customDepthStencil, depthTexture, hdrMSAATexture):
        if customBackBuffer is not None:
            if customBackBuffer.__bluetype__ == 'trinity.TriTextureRes':
                backBuffer = self.customBackBuffer.GetSurfaceLevel(0)
            else:
                backBuffer = self.customBackBuffer
            self.AddStep('SET_CUSTOM_RT', trinity.TriStepSetRenderTarget(backBuffer))
            if self.useBloom and self.hdrEnabled and self.msaaEnabled:
                self.AddStep('FINAL_BLIT', trinity.TriStepCopySurfaceToRT(self.hdrMSAATexture.GetSurfaceLevel(0), trinity.device.GetBackBuffer()))
            elif self.msaaEnabled and not self.useBloom:
                self.AddStep('FINAL_BLIT', trinity.TriStepCopySurfaceToRT(self.customBackBuffer, trinity.device.GetBackBuffer()))
            elif self.hdrEnabled and not self.msaaEnabled:
                self.AddStep('FINAL_BLIT', trinity.TriStepCopySurfaceToRT(self.customBackBuffer.GetSurfaceLevel(0), trinity.device.GetBackBuffer()))
            if self.fxaaEnabled:
                self.AddStep('SET_VAR_GATHER', trinity.TriStepSetVariableStore('GatherMap', self.customBackBuffer))
            else:
                self.RemoveStep('SET_VAR_GATHER')
            self.AddStep('SET_FINAL_RT', trinity.TriStepSetRenderTarget(trinity.device.GetBackBuffer()))
        else:
            self.RemoveStep('SET_CUSTOM_RT')
            self.RemoveStep('FINAL_BLIT')
            self.RemoveStep('SET_FINAL_RT')
            self.RemoveStep('SET_VAR_GATHER')
        if customDepthStencil is not None:
            self.AddStep('SET_DEPTH', trinity.TriStepSetDepthStencil(customDepthStencil))
            self.AddStep('RESTORE_DEPTH', trinity.TriStepSetDepthStencil(trinity.device.GetDepthStencilSurface()))
        else:
            self.RemoveStep('RESTORE_DEPTH')
        if self.depthTexture is not None:
            if not self.msaaEnabled:
                self.AddStep('SET_DEPTH', trinity.TriStepSetDepthStencil(self.depthTexture.GetSurfaceLevel(0)))
            else:
                self._SetDepthMap()
            self.AddStep('SET_VAR_DEPTH', trinity.TriStepSetVariableStore('DepthMap', self.depthTexture))
        elif not self.msaaEnabled:
            self.RemoveStep('SET_DEPTH')
        self.RemoveStep('SET_VAR_DEPTH')
        if self.GetStep('RJ_POSTPROCESSING') is not None:
            self.AddStep('RJ_POSTPROCESSING', trinity.TriStepRunJob(self.CreatePostProcessRenderJob()))



    def GetRenderTargets(self):
        return self.renderTargetList




