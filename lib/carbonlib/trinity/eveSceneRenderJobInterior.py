from trinity.sceneRenderJobBase import SceneRenderJobBase
from trinity.renderJobUtils import renderTargetManager as rtm
import interiorVisualizations as iVis
import trinity
import blue
import yaml
import uthread
import geo2

def CreateEveSceneRenderJobInterior(name = None, stageKey = None):
    newRJ = EveSceneRenderJobInterior()
    if name is not None:
        newRJ.ManualInit(name)
    else:
        newRJ.ManualInit()
    newRJ.SetMultiViewStage(stageKey)
    return newRJ



class EveSceneRenderJobInterior(SceneRenderJobBase):
    renderStepOrder = ['UPDATE_SCENE',
     'UPDATE_BACKGROUND_SCENE',
     'UPDATE_STEREO',
     'UPDATE_BACKGROUND_CAMERA',
     'UPDATE_UI',
     'SET_VIEWPORT',
     'SET_DEPTH',
     'SET_BACKGROUND_RT',
     'SET_BACKGROUND_PROJECTION',
     'SET_BACKGROUND_VIEW',
     'CLEAR_BACKGROUND_RT',
     'RENDER_BACKGROUND_SCENE',
     'CLEAR_BACKGROUND_DEPTH',
     'SET_PROJECTION',
     'SET_VIEW',
     'VISIBILITY_QUERY',
     'SET_VISIBILITY_RESULT',
     'SET_VISUALIZATION',
     'SET_DEPTH',
     'SET_PREPASS_RT',
     'CLEAR_PREPASS',
     'BEGIN_MANAGED_RENDERING',
     'RENDER_PREPASS',
     'SET_LIGHT_RT',
     'CLEAR_LIGHTS',
     'SET_VAR_LIGHTS_DEPTH',
     'SET_VAR_LIGHTS_PREPASS',
     'SET_VAR_LIGHT_LUT',
     'SET_VAR_LIGHT_FRESNEL',
     'RENDER_LIGHTS',
     'RENDER_SSAO',
     'SET_VAR_SSAO',
     'SET_GATHER_RT',
     'CLEAR_GATHER_RT',
     'SET_VAR_LIGHTS',
     'SET_FOG_MAP',
     'RENDER_GATHER',
     'UPDATE_LUT',
     'SET_VAR_POST_PROCESS_GATHER',
     'SET_ILR_THRESHOLD_RT',
     'SET_VAR_ILR_KERNEL_THRESHOLD',
     'RENDER_ILR_THRESHOLD',
     'SET_VAR_ILR_THRESHOLD_0',
     'SET_VAR_ILR_KERNEL_0',
     'SET_ILR_BLOOM_RT_0',
     'RENDER_ILR_BLOOM_0',
     'SET_VAR_ILR_THRESHOLD_1',
     'SET_VAR_ILR_KERNEL_1',
     'SET_ILR_BLOOM_RT_1',
     'RENDER_ILR_BLOOM_1',
     'SET_VAR_ILR_MERGE_BLOOM0',
     'SET_VAR_ILR_MERGE_BLOOM1',
     'SET_VAR_ILR_MERGE_BLOOM2',
     'SET_ILR_MERGE_RT',
     'RENDER_ILR_MERGE',
     'SET_POST_PROCESS_DEPTH_STENCIL',
     'SET_POST_PROCESS_COMPOSITE_RT',
     'SET_VAR_ILR_BLOOM',
     'SET_VAR_ILR_REFLECTIONS_0',
     'SET_VAR_ILR_REFLECTIONS_1',
     'SET_VAR_ILR_TINT_0',
     'SET_VAR_ILR_TINT_1',
     'POST_PROCESS',
     'RENDER_FLARES',
     'END_MANAGED_RENDERING',
     'UPDATE_TOOLS',
     'RENDER_INFO',
     'RENDER_VISUAL',
     'RENDER_TOOLS',
     'RESTORE_DEPTH',
     'RENDER_UI',
     'PRESENT_SWAPCHAIN']
    multiViewStages = [('SETUP', True, ['UPDATE_SCENE',
       'UPDATE_BACKGROUND_SCENE',
       'SET_DEPTH',
       'BEGIN_MANAGED_RENDERING']),
     ('SETUP_BACKGROUND_RENDERING', True, ['SET_GATHER_RT', 'CLEAR_BACKGROUND_RT']),
     ('SETUP_VIEW', False, ['SET_VIEWPORT',
       'SET_PROJECTION',
       'SET_VIEW',
       'VISIBILITY_QUERY',
       'FILTER_VISIBILITY_RESULT']),
     ('RENDER_BACKGROUNDS', False, ['SET_VIEWPORT',
       'UPDATE_BACKGROUND_CAMERA',
       'SET_BACKGROUND_PROJECTION',
       'SET_BACKGROUND_VIEW',
       'RENDER_BACKGROUND_SCENE']),
     ('RESTORE_FROM_BACKGROUND_RENDERING', True, ['CLEAR_BACKGROUND_DEPTH']),
     ('SETUP_PREPASS_PASS', True, ['SET_PREPASS_RT', 'CLEAR_PREPASS']),
     ('PREPASS', False, ['SET_VIEWPORT',
       'SET_VIEW',
       'SET_PROJECTION',
       'SET_VISIBILITY_RESULT',
       'SET_VISUALIZATION',
       'ENABLE_WIREFRAME',
       'RENDER_PREPASS',
       'RESTORE_WIREFRAME']),
     ('SETUP_LIGHT_PASS', True, ['SET_LIGHT_RT',
       'CLEAR_LIGHTS',
       'SET_VAR_LIGHT_LUT',
       'SET_VAR_LIGHT_FRESNEL',
       'SET_VAR_LIGHTS_DEPTH',
       'SET_VAR_LIGHTS_PREPASS']),
     ('LIGHT_PASS', False, ['SET_VIEWPORT',
       'SET_VIEW',
       'SET_PROJECTION',
       'SET_VISIBILITY_RESULT',
       'SET_VISUALIZATION',
       'RENDER_LIGHTS']),
     ('SETUP_GATHER', True, ['RENDER_SSAO',
       'SET_VAR_SSAO',
       'SET_GATHER_RT',
       'SET_VAR_LIGHTS']),
     ('GATHER_PASS', False, ['SET_VIEWPORT',
       'SET_VIEW',
       'SET_PROJECTION',
       'SET_VISIBILITY_RESULT',
       'SET_VISUALIZATION',
       'ENABLE_WIREFRAME',
       'DISABLE_CUBEMAP',
       'SET_FOG_MAP',
       'RENDER_GATHER',
       'ENABLE_CUBEMAP',
       'RESTORE_WIREFRAME',
       'RENDER_FLARES']),
     ('END_MANAGED_RENDERING', True, ['END_MANAGED_RENDERING']),
     ('TOOLS', False, ['SET_VIEWPORT',
       'SET_VIEW',
       'SET_PROJECTION',
       'UPDATE_TOOLS',
       'RENDER_INFO',
       'RENDER_PROXY',
       'RENDER_VISUAL',
       'RENDER_TOOLS',
       'RENDER_KYNAPSE']),
     ('TEARDOWN', True, ['RESTORE_DEPTH'])]
    visualizations = [iVis.DisableVisualization,
     ('Geometry', [iVis.WhiteVisualization,
       iVis.ObjectNormalVisualization,
       iVis.ShadedObjectNormalVisualization,
       iVis.TangentVisualization,
       iVis.BiTangentVisualization,
       iVis.TexCoord0Visualization,
       iVis.TexCoord1Visualization,
       iVis.TexelDensityVisualization,
       iVis.OverdrawVisualization,
       iVis.DepthVisualization]),
     ('Textures', [('Normal Map', [iVis.NormalMapVisualization,
         iVis.NormalMapWorldVisualization,
         iVis.NormalMapUnpackedVisualization,
         iVis.NormalMapRedInvertedVisualization,
         iVis.NormalMapGreenInvertedVisualization,
         iVis.NormalMapBothInvertedVisualization]),
       ('Shaded Normal Map', [iVis.ShadedNormalMapVisualization,
         iVis.ShadedNormalMapUnpackedVisualization,
         iVis.ShadedNormalMapRedInvertedVisualization,
         iVis.ShadedNormalMapGreenInvertedVisualization,
         iVis.ShadedNormalMapBothInvertedVisualization]),
       iVis.GlowMapVisualization,
       iVis.GlowMapUnpackedVisualization,
       iVis.SpecularMapVisualization,
       iVis.SpecularMapUnpackedVisualization,
       iVis.DiffuseMapVisualization,
       iVis.ReflectionMapVisualization,
       iVis.AOMapVisualization]),
     ('Lighting', [('Enlighten', [iVis.EnlightenDetailChartsVisualization,
         iVis.EnlightenTargetChartsVisualization,
         iVis.EnlightenOnlyVisualization,
         iVis.EnlightenTargetDetailVisualization,
         iVis.EnlightenOutputDensityVisualization,
         iVis.EnlightenAlbedoVisualization,
         iVis.EnlightenObjectTexcoordVisualization,
         iVis.EnlightenNaughtyPixelsVisualization]),
       ('All Light Volumes', [iVis.LightVolumeWhiteVisualization,
         iVis.LightVolumeNormalVisualization,
         iVis.LightVolumeShadowResolutionVisualization,
         iVis.LightVolumeShadowRelativeResolutionVisualization]),
       ('Primary Light Volumes', [iVis.PrimaryLightVolumeWhiteVisualization,
         iVis.PrimaryLightVolumeNormalVisualization,
         iVis.PrimaryLightVolumeShadowResolutionVisualization,
         iVis.PrimaryLightVolumeShadowRelativeResolutionVisualization]),
       ('Secondary Light Volumes', [iVis.SecondaryLightVolumeWhiteVisualization,
         iVis.SecondaryLightVolumeNormalVisualization,
         iVis.SecondaryLightVolumeShadowResolutionVisualization,
         iVis.SecondaryLightVolumeShadowRelativeResolutionVisualization]),
       ('Shadowcasting Light Volumes', [iVis.ShadowcastingLightVolumeWhiteVisualization,
         iVis.ShadowcastingLightVolumeNormalVisualization,
         iVis.ShadowcastingLightVolumeShadowResolutionVisualization,
         iVis.ShadowcastingLightVolumeShadowRelativeResolutionVisualization]),
       ('Transparent Light Volumes', [iVis.TransparentLightVolumeWhiteVisualization,
         iVis.TransparentLightVolumeNormalVisualization,
         iVis.TransparentLightVolumeShadowResolutionVisualization,
         iVis.TransparentLightVolumeShadowRelativeResolutionVisualization]),
       iVis.PrePassLightingOnlyVisualization,
       iVis.PrePassLightingDiffuseVisualization,
       iVis.PrePassLightingSpecularVisualization,
       iVis.PrePassLightNormalVisualization,
       iVis.PrePassLightDepthVisualization,
       iVis.PrePassLightWorldPositionVisualization,
       iVis.PrePassLightOverdrawVisualization,
       iVis.ShadowOnlyVisualization])]

    def _ManualInit(self, name = 'EveSceneRenderJobInterior'):
        self.depthFormat = None
        self.prePassFormat = None
        self.lightAccumulationFormat = None
        self.backBufferDepthStencil = None
        self.backBufferRenderTarget = None
        self.prePassDepthStencil = None
        self.prePassRenderTarget = None
        self.lightAccumulationTarget = None
        self.renderTargetCount = {}
        self.gatherTarget = None
        self.ilrMergeTarget = None
        self.ilrBloomTarget0 = None
        self.ilrBloomTarget1 = None
        self.ilrBloomTarget2 = None
        self.ilrBloomFormat = None
        self.ssaoTarget = None
        self.renderTargetList = None
        self.ui = None
        self.backgroundScene = None
        self.backgroundUpdateFunction = None
        self.swapChain = None
        self.numShadowUpdates = 2
        self.ilrThresholdShader = None
        self.ilrBloomShader = None
        self.ilrMergeShader = None
        self.ilrEnabled = True
        self.lutEnabled = False
        self.noiseEnabled = False
        self.fxaaEnabled = False
        self.fxaaQuality = 'FXAA_Low'
        self.ssaoEnabled = False
        self.postProcessShader = trinity.Tr2ShaderMaterial()
        self.postProcessShader.highLevelShaderName = 'PostProcess'
        self.postProcessingParameters = {}
        self.fogTexturePath = ''
        self.previousLUTMap = None
        self.nextLUTMap = None
        self.lutBlend = 0
        self.lutTransitions = None
        self.lutPreviousTime = 0L
        self.noiseAmounts = (0.0, 0.0, 0.0, 1.0)
        self.lightingLUT = None
        self.fresnelLUT = None
        self.SetSettingsBasedOnPerformancePreferences()
        self.ChooseBufferFormats()



    def Enable(self):
        SceneRenderJobBase.Enable(self)
        self.SetSettingsBasedOnPerformancePreferences()



    def SetSettingsBasedOnPerformancePreferences(self):
        if not self.enabled:
            return 
        deviceSvc = sm.GetService('device')
        defaultInteriorGraphicsQuality = deviceSvc.GetDefaultInteriorGraphicsQuality()
        interiorGraphicsQuality = prefs.GetValue('interiorGraphicsQuality', defaultInteriorGraphicsQuality)
        shadowQuality = prefs.GetValue('shadowQuality', deviceSvc.GetDefaultShadowQuality())
        postProcessing = prefs.GetValue('postProcessingQuality', deviceSvc.GetDefaultPostProcessingQuality())
        self.fxaaEnabled = prefs.GetValue('antiAliasing', 0) > 0
        self.fxaaQuality = self._GetFXAAQuality(prefs.GetValue('antiAliasing', 0))
        self.numShadowUpdates = shadowQuality
        if shadowQuality != 0:
            self.numShadowUpdates = 4
        enableSSAO = deviceSvc.GetAppFeatureState('Interior.ssaoEnbaled', True)
        self.EnableSSAO(enableSSAO)
        if postProcessing == 0:
            self.EnableLUT(False)
            self.EnableILR(False)
            self.EnableNoise(False)
        elif postProcessing == 1:
            self.EnableLUT(False)
            self.EnableILR(False)
            self.EnableNoise(False)
        else:
            self.EnableLUT(True)
            self.EnableILR(True)
            self.EnableNoise(True)
        self.EnableFXAA(self.fxaaEnabled, self.fxaaQuality)
        self.ApplyPerformancePreferencesToScene()



    def ApplyPerformancePreferencesToScene(self):
        defaultInteriorGraphicsQuality = sm.GetService('device').GetDefaultInteriorGraphicsQuality()
        interiorGraphicsQuality = prefs.GetValue('interiorGraphicsQuality', defaultInteriorGraphicsQuality)
        currentScene = self.GetScene()
        if currentScene is not None:
            currentScene.shadowUpdatesPerFrame = self.numShadowUpdates



    def _GetFXAAQuality(self, quality):
        if quality == 3:
            return 'FXAA_High'
        if quality == 2:
            return 'FXAA_Medium'
        if quality == 1:
            return 'FXAA_LOW'
        return ''



    def _GetRenderTargetIndex(self, format, width, height):
        key = (format, width, height)
        count = self.renderTargetCount.get(key, 0)
        self.renderTargetCount[key] = count + 1
        return count



    def _SetScene(self, scene):
        if hasattr(scene, 'id'):
            path = 'res:/Graphics/PostProcess/%i_postprocess.red' % scene.id
            self._LoadPostprocessingParameters(path, scene, False)
        elif scene is not None:
            self._ApplyDefaultPostprocessingParameters(scene)
        self.ApplyPerformancePreferencesToScene()
        if scene is None:
            visibility = self.GetStep('VISIBILITY_QUERY')
            if visibility is not None and hasattr(visibility, 'results'):
                visibility.results.Clear()
        self.SetStepAttr('UPDATE_SCENE', 'object', scene)
        self.SetStepAttr('VISIBILITY_QUERY', 'queryable', scene)
        self.SetStepAttr('SET_VISIBILITY_RESULT', 'queryable', scene)
        self.SetStepAttr('BEGIN_MANAGED_RENDERING', 'scene', scene)
        self.SetStepAttr('RENDER_PREPASS', 'scene', scene)
        self.SetStepAttr('RENDER_LIGHTS', 'scene', scene)
        self.SetStepAttr('RENDER_GATHER', 'scene', scene)
        self.SetStepAttr('RENDER_FLARES', 'scene', scene)
        self.SetStepAttr('END_MANAGED_RENDERING', 'scene', scene)



    def ReloadPostprocessingParameters(self):
        scene = self.GetScene()
        if not scene:
            return None
        if hasattr(scene, 'id'):
            path = 'res:/Graphics/PostProcess/%i_postprocess.red' % scene.id
            self._LoadPostprocessingParameters(path, scene, True)
        else:
            self.postProcessingParameters = {}



    def _LoadPostprocessingParameters(self, path, scene, forceReload):
        rf = blue.ResFile()
        if rf.FileExists(path):
            rf.Open(path)
            yamlStr = rf.read()
            rf.close()
            data = yaml.load(yamlStr)
            self._ApplyPostprocessingParameters(data, scene, forceReload)
        else:
            self._ApplyDefaultPostprocessingParameters(scene)



    def _GetUpdateLUTCallback(self):

        def UpdateLUT():
            if self.view.object is None or self.lutTransitions is None:
                return 
            position = geo2.MatrixInverse(self.view.object.transform)[3]
            closest = None
            closestDistance = 0
            for transition in self.lutTransitions:
                distance = geo2.Vec4Dot(position, transition['plane'])
                if closest is None or abs(distance) < abs(closestDistance):
                    closest = transition
                    closestDistance = distance

            transitionTime = 1
            if closest is not None:
                if closestDistance > 0:
                    map = closest['mapA']
                    transitionTime = closest['toSideATime']
                else:
                    map = closest['mapB']
                    transitionTime = closest['toSideBTime']
                if map != self.nextLUTMap:
                    if map == self.previousLUTMap:
                        temp = self.nextLUTMap
                        self.nextLUTMap = self.previousLUTMap
                        self.previousLUTMap = temp
                        self.lutBlend = 1 - self.lutBlend
                    elif self.previousLUTMap is None:
                        self.previousLUTMap = map
                        self.nextLUTMap = map
                        self.lutBlend = 0
                    else:
                        self.previousLUTMap = self.nextLUTMap
                        self.nextLUTMap = map
                        self.lutBlend = 0
                    self.SetLUTMaps(self.previousLUTMap, self.nextLUTMap)
            time = blue.os.GetTime(0)
            if self.lutPreviousTime == 0L:
                self.lutPreviousTime = time
            dt = min(blue.os.TimeDiffInMs(self.lutPreviousTime, time) / 1000.0, 0.1)
            self.lutPreviousTime = time
            self.lutBlend = min(self.lutBlend + dt / transitionTime, 1.0)
            self.SetLUTBlendAmount(self.lutBlend)


        return UpdateLUT



    def _ApplyPostprocessingParameters(self, data, scene, forceReload):
        self.postProcessingParameters = data
        scene.minFogDistance = data['fog']['minFogDistance']
        scene.maxFogDistance = data['fog']['maxFogDistance']
        scene.maxFogAmount = data['fog']['maxFogAmount']
        self.fogTexturePath = data['fog']['texture']
        texture = blue.resMan.GetResource(self.fogTexturePath)
        if forceReload:
            texture.Reload()
        self.AddStep('SET_FOG_MAP', trinity.TriStepSetVariableStore('FogRampMap', texture))
        if not self.enabled or not self.canCreateRenderTargets:
            return 
        self._RebuildPostProcess()



    def _ApplyDefaultPostprocessingParameters(self, scene):
        scene.maxFogAmount = 0
        self.fogTexturePath = ''
        self.AddStep('SET_FOG_MAP', trinity.TriStepSetVariableStore('FogRampMap', trinity.TriTextureRes()))
        self.EnableLUT(False)
        self.EnableNoise(False)



    def _CreateBasicRenderSteps(self):
        self.AddStep('UPDATE_SCENE', trinity.TriStepUpdate(self.GetScene()))
        result = trinity.Tr2VisibilityResults()
        self.AddStep('VISIBILITY_QUERY', trinity.TriStepVisibilityQuery(self.GetScene(), result))
        self.AddStep('SET_VISIBILITY_RESULT', trinity.TriStepSetVisibilityResults(self.GetScene(), result))
        self.AddStep('SET_PREPASS_RT', trinity.TriStepSetRenderTarget())
        self.AddStep('CLEAR_PREPASS', trinity.TriStepClear((0, 0, 0, 0), 1.0, 0))
        self.AddStep('BEGIN_MANAGED_RENDERING', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_BEGIN_RENDER))
        self.AddStep('RENDER_PREPASS', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_PRE_PASS))
        self.AddStep('SET_LIGHT_RT', trinity.TriStepSetRenderTarget())
        self.AddStep('CLEAR_LIGHTS', trinity.TriStepClear((0, 0, 0, 0), None, None))
        self.AddStep('RENDER_LIGHTS', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_LIGHT_PASS))
        if self.swapChain is None:
            self.AddStep('SET_GATHER_RT', trinity.TriStepSetRenderTarget())
        else:
            self.AddStep('SET_GATHER_RT', trinity.TriStepSetRenderTarget(self.swapChain.backBuffer))
        self.AddStep('CLEAR_GATHER_RT', trinity.TriStepClear((0, 0, 0, 0), None, None))
        self.AddStep('RENDER_GATHER', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_GATHER_PASS))
        self.AddStep('RENDER_FLARES', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_FLARE_PASS))
        self.AddStep('END_MANAGED_RENDERING', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_END_RENDER))



    def AddBloomStep(self, source, target, step, kernelWidth):
        self.AddStep('SET_VAR_ILR_THRESHOLD_%d' % step, trinity.TriStepSetVariableStore('BloomMap', source))
        self.AddStep('SET_VAR_ILR_KERNEL_%d' % step, trinity.TriStepSetVariableStore('BloomWidth', (kernelWidth / source.width, kernelWidth / source.height)))
        self.AddStep('SET_ILR_BLOOM_RT_%d' % step, trinity.TriStepSetRenderTarget(target.GetSurfaceLevel(0)))
        self.AddStep('RENDER_ILR_BLOOM_%d' % step, trinity.TriStepRenderFullScreenShader(self.ilrBloomShader))



    def ChooseBufferFormats(self):
        shaderModel = trinity.GetShaderModel()
        self.depthFormat = trinity.TRIFMT_D24S8
        customDepthFormat = False
        if shaderModel == 'SM_3_0_HI':
            self.prePassFormat = trinity.TRIFMT_A16B16G16R16
            self.lightAccumulationFormat = trinity.TRIFMT_A16B16G16R16F
            self.ilrBloomFormat = trinity.TRIFMT_A16B16G16R16F
            self.gatherFormat = trinity.TRIFMT_A16B16G16R16F
        elif shaderModel == 'SM_3_0_DEPTH':
            self.depthFormat = trinity.TRIFMT_INTZ
            self.prePassFormat = trinity.TRIFMT_A16B16G16R16
            self.lightAccumulationFormat = trinity.TRIFMT_A16B16G16R16F
            self.ilrBloomFormat = trinity.TRIFMT_A16B16G16R16F
            self.gatherFormat = trinity.TRIFMT_A16B16G16R16F
            customDepthFormat = True
        else:
            self.prePassFormat = trinity.TRIFMT_A16B16G16R16
            self.ilrBloomFormat = trinity.TRIFMT_A16B16G16R16F
            self.lightAccumulationFormat = trinity.TRIFMT_A8R8G8B8
            self.gatherFormat = trinity.TRIFMT_A8R8G8B8
        if not customDepthFormat:
            self.RemoveStep('SET_DEPTH')
            self.RemoveStep('RESTORE_DEPTH')



    def DoReleaseResources(self, level):
        self.SetRenderTargets(None, None, None, None, None, None, None, None, None, None, None)
        self.renderTargetList = None
        self.backBufferDepthStencil = None
        self.gatherTarget = None
        self.backBufferRenderTarget = None
        self.prePassDepthStencil = None
        self.prePassRenderTarget = None
        self.lightAccumulationTarget = None
        self.ilrMergeTarget = None
        self.ilrBloomTarget0 = None
        self.ilrBloomTarget1 = None
        self.ilrBloomTarget2 = None
        self.ssaoTarget = None
        self.renderTargetCount = {}



    def InitializeShaders(self):
        self.ilrBloomShader = trinity.Tr2ShaderMaterial()
        self.ilrBloomShader.highLevelShaderName = 'ILR_Bloom'
        self.ilrBloomShader.BindLowLevelShader(['none'])
        self.ilrThresholdShader = trinity.Tr2ShaderMaterial()
        self.ilrThresholdShader.highLevelShaderName = 'ILR_Threshold'
        self.ilrThresholdShader.BindLowLevelShader(['none'])
        self.ilrMergeShader = trinity.Tr2ShaderMaterial()
        self.ilrMergeShader.highLevelShaderName = 'ILR_Merge'
        self.ilrMergeShader.BindLowLevelShader(['none'])



    def DoPrepareResources(self):
        if not self.enabled or not self.canCreateRenderTargets:
            return 
        if self.fogTexturePath != '':
            texture = blue.resMan.GetResource(self.fogTexturePath)
            self.AddStep('SET_FOG_MAP', trinity.TriStepSetVariableStore('FogRampMap', texture))
        self.lightingLUT = blue.resMan.GetResource('res:/Graphics/Shared_Texture/Global/prepassLightLookup.dds')
        self.fresnelLUT = blue.resMan.GetResource('res:/Graphics/Shared_Texture/Global/prepassLightLookupFresnel.dds')
        self.AddStep('SET_VAR_LIGHT_LUT', trinity.TriStepSetVariableStore('LightingLUT', self.lightingLUT))
        self.AddStep('SET_VAR_LIGHT_FRESNEL', trinity.TriStepSetVariableStore('FresnelLUT', self.fresnelLUT))
        if self.renderTargetList is None:
            device = trinity.device
            width = device.GetPresentParameters()['BackBufferWidth']
            height = device.GetPresentParameters()['BackBufferHeight']
            self.ChooseBufferFormats()
            if self.backBufferDepthStencil is None:
                if self.swapChain is None:
                    self.backBufferDepthStencil = device.GetDepthStencilSurface()
                else:
                    self.backBufferDepthStencil = self.swapChain.depthStencilBuffer
            if self.backBufferRenderTarget is None:
                if self.swapChain is None:
                    self.backBufferRenderTarget = device.GetRenderTarget()
                else:
                    self.backBufferRenderTarget = self.swapChain.backBuffer
            if self.depthFormat is not None and self.prePassDepthStencil is None:
                if self.depthFormat == self.backBufferDepthStencil.format:
                    self.prePassDepthStencil = self.backBufferDepthStencil
                else:
                    self.prePassDepthStencil = rtm.GetTexture(self._GetRenderTargetIndex(self.depthFormat, width, height), width, height, 1, trinity.TRIUSAGE_DEPTHSTENCIL, self.depthFormat, trinity.TRIPOOL_DEFAULT)
            if self.prePassFormat is not None and self.prePassRenderTarget is None:
                self.prePassRenderTarget = rtm.GetTexture(self._GetRenderTargetIndex(self.prePassFormat, width, height), width, height, 1, trinity.TRIUSAGE_RENDERTARGET, self.prePassFormat, trinity.TRIPOOL_DEFAULT)
            if self.lightAccumulationFormat is not None and self.lightAccumulationTarget is None:
                self.lightAccumulationTarget = rtm.GetTexture(self._GetRenderTargetIndex(self.lightAccumulationFormat, width, height), width, height, 1, trinity.TRIUSAGE_RENDERTARGET, self.lightAccumulationFormat, trinity.TRIPOOL_DEFAULT)
            self._RebuildPostProcess()
            if self.ssaoEnabled:
                self.ssaoTarget = self.CreateSSAORenderTarget()
            else:
                self.ssaoTarget = blue.resMan.GetResource('res:/Texture/Global/white.dds')
            self.renderTargetList = (blue.BluePythonWeakRef(self.backBufferDepthStencil),
             blue.BluePythonWeakRef(self.backBufferRenderTarget),
             blue.BluePythonWeakRef(self.prePassDepthStencil),
             blue.BluePythonWeakRef(self.prePassRenderTarget),
             blue.BluePythonWeakRef(self.lightAccumulationTarget),
             blue.BluePythonWeakRef(self.ilrBloomTarget0),
             blue.BluePythonWeakRef(self.ilrBloomTarget1),
             blue.BluePythonWeakRef(self.ilrBloomTarget2),
             blue.BluePythonWeakRef(self.ilrMergeTarget),
             blue.BluePythonWeakRef(self.gatherTarget),
             blue.BluePythonWeakRef(self.ssaoTarget))
        thingToSet = (x.object for x in self.renderTargetList)
        self.SetRenderTargets(*thingToSet)



    def SetUI(self, ui):
        if ui is None:
            self.RemoveStep('UPDATE_UI')
            self.RemoveStep('RENDER_UI')
        else:
            self.AddStep('UPDATE_UI', trinity.TriStepUpdate(ui))
            self.AddStep('RENDER_UI', trinity.TriStepRenderUI(ui))



    def SetCameraView(self, view):
        SceneRenderJobBase.SetCameraView(self, view)
        self.UpdateBackgroundCameraCallbackWithNewForegroundCamera()



    def SetCameraProjection(self, proj):
        SceneRenderJobBase.SetCameraProjection(self, proj)
        self.UpdateBackgroundCameraCallbackWithNewForegroundCamera()



    def GetBackgroundUpdateCallbackFunction(self, foregroundView, foregroundProjection, f):

        def CameraUpdateCallbackClosure():
            return f(foregroundView, foregroundProjection)


        return CameraUpdateCallbackClosure



    def GetBackgroundCameraUpdateFunction(self, backgroundView, backgroundProjection, backgroundNearClip, backgroundFarClip, translation, rotation):
        import geo2
        additionalViewTranform = geo2.MatrixTransformation((0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0), rotation, translation)

        def UpdateBackgroundCamera(foregroundView, foregroundProjection):
            foregroundViewInverted = geo2.MatrixInverse(foregroundView.transform)
            backgroundViewInverted = geo2.MatrixMultiply(foregroundViewInverted, additionalViewTranform)
            backgroundView.transform = geo2.MatrixInverse(backgroundViewInverted)
            originalProjection = foregroundProjection.transform
            if originalProjection[3][3] == 0:
                new33 = backgroundFarClip / (backgroundNearClip - backgroundFarClip)
                new43 = backgroundNearClip * backgroundFarClip / (backgroundNearClip - backgroundFarClip)
                newProjectionTransform = (originalProjection[0],
                 originalProjection[1],
                 (originalProjection[2][0],
                  originalProjection[2][1],
                  new33,
                  originalProjection[2][3]),
                 (originalProjection[3][0],
                  originalProjection[3][1],
                  new43,
                  originalProjection[3][3]))
                backgroundProjection.CustomProjection(newProjectionTransform)
            else:
                new33 = 1.0 / (backgroundNearClip - backgroundFarClip)
                new43 = backgroundNearClip / (backgroundNearClip - backgroundFarClip)
                newProjectionTransform = (originalProjection[0],
                 originalProjection[1],
                 (originalProjection[2][0],
                  originalProjection[2][1],
                  new33,
                  originalProjection[2][3]),
                 (originalProjection[3][0],
                  originalProjection[3][1],
                  new43,
                  originalProjection[3][3]))
                backgroundProjection.CustomProjection(newProjectionTransform)


        return UpdateBackgroundCamera



    def SetBackgroundCameraViewAndProjection(self, view, projection, updateFunction):
        self.backgroundUpdateFunction = None
        if view is None or projection is None:
            self.RemoveStep('SET_BACKGROUND_PROJECTION')
            self.RemoveStep('SET_BACKGROUND_VIEW')
            self.RemoveStep('UPDATE_BACKGROUND_CAMERA')
        else:
            self.AddStep('SET_BACKGROUND_VIEW', trinity.TriStepSetView(view))
            self.AddStep('SET_BACKGROUND_PROJECTION', trinity.TriStepSetProjection(projection))
            self.backgroundUpdateFunction = updateFunction
            self.UpdateBackgroundCameraCallbackWithNewForegroundCamera()



    def UpdateBackgroundCameraCallbackWithNewForegroundCamera(self):
        originalView = None
        if self.view is not None:
            originalView = self.view.object
            if originalView is None:
                return 
        else:
            return 
        originalProjection = None
        if self.projection is not None:
            originalProjection = self.projection.object
            if originalProjection is None:
                return 
        else:
            return 
        if self.backgroundUpdateFunction is None:
            return 
        if originalProjection is not None and originalView is not None:
            callback = self.GetBackgroundUpdateCallbackFunction(originalView, originalProjection, self.backgroundUpdateFunction)
            upd = self.AddStep('UPDATE_BACKGROUND_CAMERA', trinity.TriStepPythonCB())
            if upd is not None:
                upd.SetCallback(callback)
                return True



    def SetBackgroundScene(self, scene):
        if scene is None:
            self.RemoveStep('UPDATE_BACKGROUND_SCENE')
            self.RemoveStep('RENDER_BACKGROUND_SCENE')
            self.AddStep('CLEAR_GATHER_RT', trinity.TriStepClear((0, 0, 0, 0), None, None))
            self.RemoveStep('CLEAR_BACKGROUND_RT')
            self.RemoveStep('CLEAR_BACKGROUND_DEPTH')
            self.RemoveStep('SET_BACKGROUND_RT')
            self.backgroundScene = None
        else:
            self.AddStep('UPDATE_BACKGROUND_SCENE', trinity.TriStepUpdate(scene))
            self.AddStep('RENDER_BACKGROUND_SCENE', trinity.TriStepRenderScene(scene))
            self.AddStep('CLEAR_BACKGROUND_RT', trinity.TriStepClear((0, 0, 0, 0), 1.0, 0))
            self.AddStep('CLEAR_BACKGROUND_DEPTH', trinity.TriStepClear(None, 1.0, 0))
            self.RemoveStep('CLEAR_GATHER_RT')
            if self.gatherTarget is not None:
                self.AddStep('SET_BACKGROUND_RT', trinity.TriStepSetRenderTarget(self.gatherTarget.GetSurfaceLevel(0)))
            self.backgroundScene = blue.BluePythonWeakRef(scene)



    def EnableSceneUpdate(self, isEnabled):
        if isEnabled:
            self.AddStep('UPDATE_SCENE', trinity.TriStepUpdate(self.GetScene()))
        else:
            self.RemoveStep('UPDATE_SCENE')



    def EnableVisibilityQuery(self, isEnabled):
        if isEnabled:
            result = trinity.Tr2VisibilityResults()
            self.AddStep('VISIBILITY_QUERY', trinity.TriStepVisibilityQuery(self.GetScene(), result))
            self.AddStep('SET_VISIBILITY_RESULT', trinity.TriStepSetVisibilityResults(self.GetScene(), result))
        else:
            self.RemoveStep('VISIBILITY_QUERY ')
            self.RemoveStep('SET_VISIBILITY_RESULT')



    def EnableBackBufferClears(self, isEnabled):
        if isEnabled:
            self.AddStep('CLEAR_PREPASS', trinity.TriStepClear((0, 0, 0, 0), 1.0, 0))
            self.AddStep('CLEAR_LIGHTS', trinity.TriStepClear((0, 0, 0, 0), None, None))
        else:
            self.RemoveStep('CLEAR_PREPASS')
            self.RemoveStep('CLEAR_LIGHTS')



    def CreateSSAORenderTarget(self):
        device = trinity.device
        width = device.GetPresentParameters()['BackBufferWidth']
        height = device.GetPresentParameters()['BackBufferHeight']
        ssaoFormat = trinity.TRIFMT_R5G6B5
        target = rtm.GetTexture(self._GetRenderTargetIndex(ssaoFormat, width, height), width, height, 1, trinity.TRIUSAGE_RENDERTARGET, ssaoFormat, trinity.TRIPOOL_DEFAULT)
        if target is None:
            ssaoFormat = trinity.TRIFMT_A8R8G8B8
            target = rtm.GetTexture(self._GetRenderTargetIndex(ssaoFormat, width, height), width, height, 1, trinity.TRIUSAGE_RENDERTARGET, ssaoFormat, trinity.TRIPOOL_DEFAULT)
        return target



    def EnableSSAO(self, enable):
        self.ssaoEnabled = enable
        if enable:
            try:
                ssao = trinity.Load('res://Graphics/postprocess/SSAO.red')
                blue.resMan.Wait()
                ssao.useNormalTexture = True
                self.AddStep('RENDER_SSAO', ssao)
            except:
                pass
            if self.enabled and self.canCreateRenderTargets:
                try:
                    self.ssaoTarget = self.CreateSSAORenderTarget()
                except:
                    self.ssaoTarget = blue.resMan.GetResource('res:/Texture/Global/white.dds')
            if type(self.prePassDepthStencil) is trinity.TriTextureRes:
                self.SetStepAttr('RENDER_SSAO', 'depthTexture', self.prePassDepthStencil)
            else:
                self.SetStepAttr('RENDER_SSAO', 'depthTexture', self.prePassRenderTarget)
            self.SetStepAttr('RENDER_SSAO', 'normalTexture', self.prePassRenderTarget)
            self.SetStepAttr('RENDER_SSAO', 'outputTexture', self.ssaoTarget)
            self.AddStep('SET_VAR_SSAO', trinity.TriStepSetVariableStore('SSAOMap', self.ssaoTarget))
        else:
            self.ssaoTarget = blue.resMan.GetResource('res:/Texture/Global/white.dds')
            self.AddStep('SET_VAR_SSAO', trinity.TriStepSetVariableStore('SSAOMap', self.ssaoTarget))
            self.RemoveStep('RENDER_SSAO')



    def LoadILRSettings(self):
        import yaml
        scene = self.GetScene()
        if not scene:
            return 
        if hasattr(scene, 'id'):
            resPath = 'res:\\Graphics\\PostProcess\\ILR_%s.yaml' % scene.id
            if resPath is None:
                return 
        else:
            return 
        rf = blue.ResFile()
        if rf.FileExists(resPath):
            rf.Open(resPath)
            yamlStr = rf.read()
            rf.close()
            ilrValues = yaml.load(yamlStr)
            ref0 = (ilrValues.get('Reflection0', 1),
             ilrValues.get('Reflection1', 1),
             ilrValues.get('Reflection2', 1),
             ilrValues.get('Reflection3', 1))
            ref1 = (ilrValues.get('Reflection4', 1),
             ilrValues.get('Reflection5', 1),
             ilrValues.get('Reflection6', 1),
             ilrValues.get('Intensity', 1))
            tint0 = (ilrValues.get('TintR_Center', 1),
             ilrValues.get('TintG_Center', 1),
             ilrValues.get('TintB_Center', 1),
             1.0)
            tint1 = (ilrValues.get('TintR_Edge', 1),
             ilrValues.get('TintG_Edge', 1),
             ilrValues.get('TintB_Edge', 1),
             1.0)
            width = ilrValues.get('BloomWidth', 1)
            self.SetReflections(ref0, ref1)
            self.SetTints(tint0, tint1)
            self.SetBlurKernel(width)



    def SetReflections(self, ref0, ref1):
        self.AddStep('SET_VAR_ILR_REFLECTIONS_0', trinity.TriStepSetVariableStore('BloomReflections0', ref0))
        self.AddStep('SET_VAR_ILR_REFLECTIONS_1', trinity.TriStepSetVariableStore('BloomReflections1', ref1))



    def SetTints(self, tint0, tint1):
        self.AddStep('SET_VAR_ILR_TINT_0', trinity.TriStepSetVariableStore('BloomTint0', tint0))
        self.AddStep('SET_VAR_ILR_TINT_1', trinity.TriStepSetVariableStore('BloomTint1', tint1))



    def SetBlurKernel(self, width = 1.5):
        self.AddBloomStep(self.ilrBloomTarget0, self.ilrBloomTarget1, 0, width)
        self.AddBloomStep(self.ilrBloomTarget1, self.ilrBloomTarget2, 1, width * 2)



    def SetLUTMaps(self, LUTMap0, LUTMap1):
        if LUTMap0 is None:
            self.postProcessShader['LUTMap0'] = None
        else:
            rebind = False
            if 'LUTMap0' not in self.postProcessShader.parameters:
                param = trinity.TriTexture2DParameter()
                param.name = 'LUTMap0'
                self.postProcessShader.parameters['LUTMap0'] = param
                rebind = True
            self.postProcessShader.parameters['LUTMap0'].SetResource(LUTMap0)
            if 'LUTMap1' not in self.postProcessShader.parameters:
                param = trinity.TriTexture2DParameter()
                param.name = 'LUTMap1'
                self.postProcessShader.parameters['LUTMap1'] = param
                rebind = True
            self.postProcessShader.parameters['LUTMap1'].SetResource(LUTMap1)
            if rebind:
                self.postProcessShader.BindLowLevelShader([])



    def SetLUTBlendAmount(self, lutBlend):
        if 'LUTBlendAmount' not in self.postProcessShader.parameters:
            param = trinity.Tr2FloatParameter()
            param.name = 'LUTBlendAmount'
            self.postProcessShader.parameters['LUTBlendAmount'] = param
            self.postProcessShader.BindLowLevelShader([])
        self.postProcessShader.parameters['LUTBlendAmount'].value = lutBlend



    def SetLUTInfluence(self, LUTInfluence):
        self.LUTInfluence = LUTInfluence
        if 'LUTInfluence' not in self.postProcessShader.parameters:
            param = trinity.Tr2FloatParameter()
            param.name = 'LUTInfluence'
            self.postProcessShader.parameters['LUTInfluence'] = param
            self.postProcessShader.BindLowLevelShader([])
        self.postProcessShader.parameters['LUTInfluence'].value = LUTInfluence



    def EnableLUT(self, enable):
        self.lutEnabled = enable
        if self.enabled and self.renderTargetList is not None:
            self._RebuildPostProcess()



    def EnableFXAA(self, enable, mode = 'FXAA_Medium'):
        self.fxaaEnabled = enable
        self.fxaaQuality = mode
        if self.enabled and self.renderTargetList is not None:
            self._RebuildPostProcess()



    def HasPostProcess(self):
        return self.fxaaEnabled or self.lutEnabled or self.ilrEnabled or self.noiseEnabled



    def EnableILR(self, isEnabled):
        self.ilrEnabled = isEnabled
        if self.enabled and self.renderTargetList is not None:
            self._RebuildPostProcess()



    def EnableNoise(self, isEnabled):
        self.noiseEnabled = isEnabled
        if self.enabled and self.renderTargetList is not None:
            self._RebuildPostProcess()



    def _RebuildPostProcess(self):
        BLOOM_BUFFER_SCALE_0 = 4
        BLOOM_BUFFER_SCALE_1 = 4
        BLOOM_BUFFER_SCALE_2 = 8
        device = trinity.device
        width = device.GetPresentParameters()['BackBufferWidth']
        height = device.GetPresentParameters()['BackBufferHeight']
        if not blue.win32.IsTransgaming() and trinity.d3d:
            identifier = trinity.d3d.GetAdapterIdentifier()
            if identifier is not None:
                vendorID = identifier.get('VendorId', None)
                if vendorID == 4098 and blue.os.osMajor <= 5:
                    self.ilrEnabled = False
        if self.HasPostProcess():
            if self.AddStep('POST_PROCESS', trinity.TriStepRenderFullScreenShader(self.postProcessShader)) is None:
                return 
            if self.gatherTarget is None:
                self.gatherTarget = rtm.GetTexture(self._GetRenderTargetIndex(self.gatherFormat, width, height), width, height, 1, trinity.TRIUSAGE_RENDERTARGET, self.gatherFormat, trinity.TRIPOOL_DEFAULT)
            trinity.GetVariableStore().RegisterVariable('GatherMap', self.gatherTarget)
            if self.ilrEnabled:
                if self.ilrBloomFormat is not None and self.ilrBloomTarget0 is None:
                    index = self._GetRenderTargetIndex(self.ilrBloomFormat, width / BLOOM_BUFFER_SCALE_0, height / BLOOM_BUFFER_SCALE_0)
                    self.ilrBloomTarget0 = rtm.GetTexture(index, width / BLOOM_BUFFER_SCALE_0, height / BLOOM_BUFFER_SCALE_0, 1, trinity.TRIUSAGE_RENDERTARGET, self.ilrBloomFormat, trinity.TRIPOOL_DEFAULT)
                    index = self._GetRenderTargetIndex(self.ilrBloomFormat, width / BLOOM_BUFFER_SCALE_1, height / BLOOM_BUFFER_SCALE_1)
                    self.ilrBloomTarget1 = rtm.GetTexture(index, width / BLOOM_BUFFER_SCALE_1, height / BLOOM_BUFFER_SCALE_1, 1, trinity.TRIUSAGE_RENDERTARGET, self.ilrBloomFormat, trinity.TRIPOOL_DEFAULT)
                    index = self._GetRenderTargetIndex(self.ilrBloomFormat, width / BLOOM_BUFFER_SCALE_2, height / BLOOM_BUFFER_SCALE_2)
                    self.ilrBloomTarget2 = rtm.GetTexture(index, width / BLOOM_BUFFER_SCALE_2, height / BLOOM_BUFFER_SCALE_2, 1, trinity.TRIUSAGE_RENDERTARGET, self.ilrBloomFormat, trinity.TRIPOOL_DEFAULT)
                    index = self._GetRenderTargetIndex(self.ilrBloomFormat, width / BLOOM_BUFFER_SCALE_0, height / BLOOM_BUFFER_SCALE_0)
                    self.ilrMergeTarget = rtm.GetTexture(index, width / BLOOM_BUFFER_SCALE_0, height / BLOOM_BUFFER_SCALE_0, 1, trinity.TRIUSAGE_RENDERTARGET, self.ilrBloomFormat, trinity.TRIPOOL_DEFAULT)
            self.InitializeShaders()
            if self.ilrEnabled:
                self.AddStep('RENDER_ILR_THRESHOLD', trinity.TriStepRenderFullScreenShader(self.ilrThresholdShader))
                self.SetReflections((-0.6, -0.5, -0.15, -0.3), (1.4, 1.8, -1.5, 1))
                self.AddStep('SET_VAR_ILR_MERGE_BLOOM0', trinity.TriStepSetVariableStore('BloomMap', self.ilrBloomTarget0))
                self.AddStep('SET_VAR_ILR_MERGE_BLOOM1', trinity.TriStepSetVariableStore('BloomMap1', self.ilrBloomTarget1))
                self.AddStep('SET_VAR_ILR_MERGE_BLOOM2', trinity.TriStepSetVariableStore('BloomMap2', self.ilrBloomTarget2))
                self.AddStep('SET_ILR_MERGE_RT', trinity.TriStepSetRenderTarget(self.ilrMergeTarget.GetSurfaceLevel(0)))
                self.AddStep('RENDER_ILR_MERGE', trinity.TriStepRenderFullScreenShader(self.ilrMergeShader))
                self.SetBlurKernel()
                trinity.GetVariableStore().RegisterVariable('BloomMap', self.ilrBloomTarget0)
                trinity.GetVariableStore().RegisterVariable('BloomMap1', self.ilrBloomTarget0)
                trinity.GetVariableStore().RegisterVariable('BloomMap2', self.ilrBloomTarget0)
                trinity.GetVariableStore().RegisterVariable('BloomWidth', (0.0, 0.0))
                trinity.GetVariableStore().RegisterVariable('BloomReflections0', (0.0, 0.0, 0.0, 0.0))
                trinity.GetVariableStore().RegisterVariable('BloomReflections1', (0.0, 0.0, 0.0, 0.0))
                trinity.GetVariableStore().RegisterVariable('BloomTint0', (0.0, 0.0, 0.0, 0.0))
                trinity.GetVariableStore().RegisterVariable('BloomTint1', (0.0, 0.0, 0.0, 0.0))
                self.ilrBloomShader.BindLowLevelShader(['none'])
                self.ilrThresholdShader.BindLowLevelShader(['none'])
                self.ilrMergeShader.BindLowLevelShader(['none'])
            else:
                self.ilrBloomTarget0 = None
                self.ilrBloomTarget1 = None
                self.ilrBloomTarget2 = None
                self.ilrMergeTarget = None
                self._ClearILRSteps()
            self.postProcessShader.defaultSituation = ''
            if self.ilrEnabled:
                self.postProcessShader.defaultSituation = 'ILR'
            if self.lutEnabled:
                if 'lut' in self.postProcessingParameters:
                    self.lutTransitions = self.postProcessingParameters['lut']['transitions']
                    for transition in self.lutTransitions:
                        transition['plane'] = (transition['normal'][0],
                         transition['normal'][1],
                         transition['normal'][2],
                         -geo2.Vec3Dot(transition['point'], transition['normal']))
                        transition['mapA'] = blue.resMan.GetResource(transition['sideA'])
                        transition['mapB'] = blue.resMan.GetResource(transition['sideB'])

                    update = self.AddStep('UPDATE_LUT', trinity.TriStepPythonCB())
                    if update is not None:
                        update.SetCallback(self._GetUpdateLUTCallback())
                        self.SetLUTInfluence(self.postProcessingParameters['lut']['influence'])
                    self.postProcessShader.defaultSituation += ' LUT'
            else:
                self.RemoveStep('UPDATE_LUT')
            if self.noiseEnabled:
                if 'noise' in self.postProcessingParameters:
                    self.noiseAmounts = (self.postProcessingParameters['noise']['darkAmount'],
                     self.postProcessingParameters['noise']['darkIntensity'],
                     self.postProcessingParameters['noise']['brightAmount'],
                     self.postProcessingParameters['noise']['brightIntensity'])
                    self.postProcessShader.defaultSituation += ' Noise'
                noise = trinity.TriTexture2DParameter()
                noise.name = 'NoiseMap'
                noise.resourcePath = 'res:/Texture/Global/noise.dds'
                self.postProcessShader.parameters['NoiseMap'] = noise
                noiseAmount = trinity.Tr2Vector4Parameter()
                noiseAmount.name = 'NoiseAmount'
                noiseAmount.value = self.noiseAmounts
                self.postProcessShader.parameters['NoiseAmount'] = noiseAmount
            if self.fxaaEnabled:
                self.postProcessShader.defaultSituation += ' ' + self.fxaaQuality
            self.postProcessShader.BindLowLevelShader([])
            self.SetStepAttr('SET_GATHER_RT', 'target', self.gatherTarget.GetSurfaceLevel(0))
            self.AddStep('SET_VAR_POST_PROCESS_GATHER', trinity.TriStepSetVariableStore('GatherMap', self.gatherTarget))
            self.AddStep('SET_POST_PROCESS_DEPTH_STENCIL', trinity.TriStepSetDepthStencil(None))
            self.AddStep('SET_POST_PROCESS_COMPOSITE_RT', trinity.TriStepSetRenderTarget(self.backBufferRenderTarget))
            if self.backgroundScene is not None:
                self.AddStep('SET_BACKGROUND_RT', trinity.TriStepSetRenderTarget(self.gatherTarget.GetSurfaceLevel(0)))
            if self.ilrEnabled:
                self.AddStep('SET_ILR_THRESHOLD_RT', trinity.TriStepSetRenderTarget(self.ilrBloomTarget0.GetSurfaceLevel(0)))
                self.AddStep('SET_VAR_ILR_KERNEL_THRESHOLD', trinity.TriStepSetVariableStore('BloomWidth', (1.5 / self.gatherTarget.width, 1.5 / self.gatherTarget.height)))
                self.AddStep('SET_VAR_ILR_BLOOM', trinity.TriStepSetVariableStore('BloomMap', self.ilrMergeTarget))
                self.LoadILRSettings()
        else:
            self.RemoveStep('POST_PROCESS')
            self.RemoveStep('SET_VAR_POST_PROCESS_GATHER')
            self.RemoveStep('SET_POST_PROCESS_DEPTH_STENCIL')
            self.RemoveStep('SET_POST_PROCESS_COMPOSITE_RT')
            self._ClearILRSteps()
            self.AddStep('SET_GATHER_RT', trinity.TriStepSetRenderTarget(self.backBufferRenderTarget))
            if self.backgroundScene is not None:
                self.AddStep('SET_BACKGROUND_RT', trinity.TriStepSetRenderTarget(self.backBufferRenderTarget))
            self.gatherTarget = None
            self.ilrBloomTarget0 = None
            self.ilrBloomTarget1 = None
            self.ilrBloomTarget2 = None
            self.ilrMergeTarget = None
        self.renderTargetList = (blue.BluePythonWeakRef(self.backBufferDepthStencil),
         blue.BluePythonWeakRef(self.backBufferRenderTarget),
         blue.BluePythonWeakRef(self.prePassDepthStencil),
         blue.BluePythonWeakRef(self.prePassRenderTarget),
         blue.BluePythonWeakRef(self.lightAccumulationTarget),
         blue.BluePythonWeakRef(self.ilrBloomTarget0),
         blue.BluePythonWeakRef(self.ilrBloomTarget1),
         blue.BluePythonWeakRef(self.ilrBloomTarget2),
         blue.BluePythonWeakRef(self.ilrMergeTarget),
         blue.BluePythonWeakRef(self.gatherTarget),
         blue.BluePythonWeakRef(self.ssaoTarget))



    def _ClearILRSteps(self):
        self.RemoveStep('SET_VAR_ILR_BLOOM')
        self.RemoveStep('SET_VAR_ILR_REFLECTIONS_0')
        self.RemoveStep('SET_VAR_ILR_REFLECTIONS_1')
        self.RemoveStep('SET_VAR_ILR_THRESHOLD_0')
        self.RemoveStep('SET_VAR_ILR_KERNEL_0')
        self.RemoveStep('SET_ILR_BLOOM_RT_0')
        self.RemoveStep('RENDER_ILR_BLOOM_0')
        self.RemoveStep('SET_VAR_ILR_THRESHOLD_1')
        self.RemoveStep('SET_VAR_ILR_KERNEL_1')
        self.RemoveStep('SET_ILR_BLOOM_RT_1')
        self.RemoveStep('RENDER_ILR_BLOOM_1')
        self.RemoveStep('SET_VAR_ILR_MERGE_BLOOM0')
        self.RemoveStep('SET_VAR_ILR_MERGE_BLOOM1')
        self.RemoveStep('SET_VAR_ILR_MERGE_BLOOM2')
        self.RemoveStep('SET_ILR_MERGE_RT')
        self.RemoveStep('RENDER_ILR_MERGE')
        self.RemoveStep('SET_ILR_THRESHOLD_RT')
        self.RemoveStep('SET_VAR_ILR_KERNEL_THRESHOLD')
        self.RemoveStep('RENDER_ILR_THRESHOLD')
        self.RemoveStep('SET_VAR_ILR_TINT_0')
        self.RemoveStep('SET_VAR_ILR_TINT_1')



    def SetRenderTargets(self, backBufferDepthStencil, backBufferRenderTarget, prePassDepthStencil, prePassRenderTarget, lightAccumulationTarget, ilrBloomTarget0, ilrBloomTarget1, ilrBloomTarget2, ilrMergeTarget, gatherTarget, ssaoTarget):
        if prePassRenderTarget is not None:
            self.SetStepAttr('SET_PREPASS_RT', 'target', prePassRenderTarget.GetSurfaceLevel(0))
        else:
            self.SetStepAttr('SET_PREPASS_RT', 'target', None)
        if lightAccumulationTarget is not None:
            self.SetStepAttr('SET_LIGHT_RT', 'target', lightAccumulationTarget.GetSurfaceLevel(0))
        else:
            self.SetStepAttr('SET_LIGHT_RT', 'target', None)
        if prePassDepthStencil is not None:
            if type(prePassDepthStencil) is trinity.TriTextureRes:
                self.AddStep('SET_DEPTH', trinity.TriStepSetDepthStencil(prePassDepthStencil.GetSurfaceLevel(0)))
                self.AddStep('SET_VAR_LIGHTS_DEPTH', trinity.TriStepSetVariableStore('LightPrePassDepthMap', prePassDepthStencil))
        else:
            self.SetStepAttr('SET_DEPTH', 'target', None)
        self.AddStep('RESTORE_DEPTH', trinity.TriStepSetDepthStencil(backBufferDepthStencil))
        self.AddStep('SET_VAR_LIGHTS_PREPASS', trinity.TriStepSetVariableStore('LightPrePassMap', prePassRenderTarget))
        self.AddStep('SET_VAR_LIGHTS', trinity.TriStepSetVariableStore('LightAccumulationMap', lightAccumulationTarget))
        self.AddStep('SET_VAR_SSAO', trinity.TriStepSetVariableStore('SSAOMap', ssaoTarget))
        if type(prePassDepthStencil) is trinity.TriTextureRes:
            self.SetStepAttr('RENDER_SSAO', 'depthTexture', prePassDepthStencil)
        else:
            self.SetStepAttr('RENDER_SSAO', 'depthTexture', prePassRenderTarget)
        self.SetStepAttr('RENDER_SSAO', 'normalTexture', prePassRenderTarget)
        self.SetStepAttr('RENDER_SSAO', 'outputTexture', ssaoTarget)
        if gatherTarget is not None:
            self.SetStepAttr('SET_GATHER_RT', 'target', gatherTarget.GetSurfaceLevel(0))
            if self.backgroundScene is not None:
                self.AddStep('SET_BACKGROUND_RT', trinity.TriStepSetRenderTarget(gatherTarget.GetSurfaceLevel(0)))
            self.AddStep('SET_VAR_POST_PROCESS_GATHER', trinity.TriStepSetVariableStore('GatherMap', gatherTarget))
            self.AddStep('SET_POST_PROCESS_DEPTH_STENCIL', trinity.TriStepSetDepthStencil(None))
            self.AddStep('SET_POST_PROCESS_COMPOSITE_RT', trinity.TriStepSetRenderTarget(backBufferRenderTarget))
        else:
            self.SetStepAttr('SET_GATHER_RT', 'target', backBufferRenderTarget)
            if self.backgroundScene is not None:
                self.AddStep('SET_BACKGROUND_RT', trinity.TriStepSetRenderTarget(backBufferRenderTarget))
            self.RemoveStep('SET_POST_PROCESS_DEPTH_STENCIL')
            self.RemoveStep('SET_POST_PROCESS_COMPOSITE_RT')
        if ilrBloomTarget0 is not None:
            self.AddStep('SET_ILR_THRESHOLD_RT', trinity.TriStepSetRenderTarget(ilrBloomTarget0.GetSurfaceLevel(0)))
            self.AddStep('SET_VAR_ILR_KERNEL_THRESHOLD', trinity.TriStepSetVariableStore('BloomWidth', (1.5 / gatherTarget.width, 1.5 / gatherTarget.height)))
            self.AddStep('SET_VAR_ILR_BLOOM', trinity.TriStepSetVariableStore('BloomMap', ilrMergeTarget))
        else:
            self.RemoveStep('SET_ILR_THRESHOLD_RT')
            self.RemoveStep('SET_VAR_POST_PROCESS_GATHER')
            self.RemoveStep('SET_VAR_ILR_BLOOM')
        self.lightingLUT = blue.resMan.GetResource('res:/Graphics/Shared_Texture/Global/prepassLightLookup.dds')
        self.fresnelLUT = blue.resMan.GetResource('res:/Graphics/Shared_Texture/Global/prepassLightLookupFresnel.dds')
        self.AddStep('SET_VAR_LIGHT_LUT', trinity.TriStepSetVariableStore('LightingLUT', self.lightingLUT))
        self.AddStep('SET_VAR_LIGHT_FRESNEL', trinity.TriStepSetVariableStore('FresnelLUT', self.fresnelLUT))



    def GetRenderTargets(self):
        return self.renderTargetList



    def SetClearColor(self, color):
        step = self.GetStep('CLEAR_BACKGROUND_RT')
        if step is not None:
            step.color = color
        step = self.GetStep('CLEAR_GATHER_RT')
        if step is not None:
            step.color = color



    def SetSwapChain(self, swapChain):
        self.DoReleaseResources(1)
        if swapChain is None:
            self.RemoveStep('PRESENT_SWAPCHAIN')
            self.swapChain = None
        else:
            self.AddStep('PRESENT_SWAPCHAIN', trinity.TriStepPresentSwapChain(swapChain))
            self.swapChain = swapChain
        self.DoPrepareResources()



    def GetInsiderVisualizationMenu(self):
        if not self.enabled:
            return [('None', None)]
        return self._CreateVisualizationMenu(self.visualizations)



    def _CreateVisualizationMenu(self, visualizations):
        menu = []
        for entry in visualizations:
            if type(entry) == tuple:
                menu.append((entry[0], self._CreateVisualizationMenu(entry[1])))
            elif type(entry) == list:
                menu.append(self._CreateVisualizationMenu(entry))
            elif type(entry) == type('string'):
                pass
            elif hasattr(entry, 'displayName'):
                menu.append((entry.displayName, self.InsiderVisualizationSelected, [entry]))

        return menu



    def InsiderVisualizationSelected(self, visualisation):
        if self.enabled:
            self.ApplyVisualization(visualisation)




