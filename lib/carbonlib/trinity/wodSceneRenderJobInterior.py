from trinity.sceneRenderJobInterior import SceneRenderJobInterior
import interiorVisualizations as iVis
import trinity
import blue
import geo2
import math

def CreateWodSceneRenderJobInterior(name = None, stageKey = None):
    newRJ = WodSceneRenderJobInterior()
    if name is not None:
        newRJ.ManualInit(name)
    else:
        newRJ.ManualInit()
    newRJ.SetMultiViewStage(stageKey)
    return newRJ



class WodSceneRenderJobInterior(SceneRenderJobInterior):
    renderStepOrder = ['UPDATE_SCENE',
     'UPDATE_UI',
     'SET_VIEWPORT',
     'SET_PROJECTION',
     'SET_VIEW',
     'VISIBILITY_QUERY',
     'SET_VISUALIZATION',
     'BEGIN_MANAGED_RENDERING',
     'SET_DEPTH',
     'SET_PREPASS_RT',
     'SET_SPECULAR_RT',
     'SET_DIFFUSE_RT',
     'SET_DIFFUSELIGHT_RT',
     'CLEAR_PREPASS',
     'CLEAR_PREPASS_QUAD',
     'RENDER_PREPASS',
     'UNBIND_RT_1',
     'UNBIND_RT_2',
     'UNBIND_RT_3',
     'UNBIND_SPECULAR_PREPASS_RT',
     'SET_SPECULAR_LIGHT_RT',
     'CLEAR_LIGHTS',
     'SET_LIGHT_RT',
     'SET_SPECULAR_LIGHT_RT_1',
     'SET_VAR_LIGHTS_DEPTH',
     'SET_VAR_LIGHTS_PREPASS',
     'SET_VAR_SPECULAR_BLEND',
     'SET_LIGHT_LUT_DIFFUSE',
     'SET_LIGHT_LUT_SPECULAR',
     'SET_LIGHT_LUT_FRESNEL',
     'FAKE_SCENE_LIGHT',
     'RENDER_LIGHTS',
     'UNBIND_SPECULAR_LIGHT_RT',
     'SET_GATHER_RT',
     'SET_VAR_LIGHTS',
     'CLEAR_GATHER_COLOR',
     'FULL_GATHER_SHADER',
     'SET_SRGB_WRITE_ON',
     'RENDER_GATHER',
     'SET_SRGB_WRITE_OFF',
     'FAKE_ENHANCE_EDGES',
     'SET_VAR_FRAMEBUFFER_DIMENSIONS',
     'SET_VAR_GATHERFRAMEBUFFER_RTT',
     'SET_DOWNSAMPLE8_RT',
     'DOWN_SAMPLE_8X',
     'SET_DOWNSAMPLE16_RT',
     'DOWN_SAMPLE_2X',
     'SET_VAR_HORIZONTAL8_RT',
     'HORIZONTAL_FILTER_8',
     'SET_VAR_VERTICAL8_RT',
     'VERTICAL_FILTER_8',
     'SET_VAR_HORIZONTAL16_RT',
     'HORIZONTAL_FILTER_16',
     'SET_VAR_VERTICAL16_RT',
     'VERTICAL_FILTER_16',
     'SET_FINAL_RT',
     'POST_PROCESS',
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
     ('SETUP_BACKGROUND_RENDERING', True, ['SET_FINAL_RT', 'CLEAR_BACKGROUND_RT']),
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
     ('SETUP_PREPASS_PASS', True, ['SET_PREPASS_RT',
       'SET_SPECULAR_RT',
       'SET_DIFFUSE_RT',
       'SET_DIFFUSELIGHT_RT',
       'CLEAR_PREPASS',
       'CLEAR_PREPASS_QUAD']),
     ('PREPASS', False, ['SET_VIEWPORT',
       'SET_VIEW',
       'SET_PROJECTION',
       'SET_VISIBILITY_RESULT',
       'SET_VISUALIZATION',
       'ENABLE_WIREFRAME',
       'RENDER_PREPASS',
       'RESTORE_WIREFRAME']),
     ('SETUP_LIGHT_PASS', True, ['SET_SPECULAR_LIGHT_RT',
       'UNBIND_RT_1',
       'UNBIND_RT_2',
       'UNBIND_RT_3',
       'CLEAR_LIGHTS',
       'SET_LIGHT_RT',
       'SET_SPECULAR_LIGHT_RT_1',
       'SET_VAR_LIGHTS_DEPTH',
       'SET_VAR_LIGHTS_PREPASS',
       'SET_VAR_SPECULAR_BLEND',
       'SET_LIGHT_LUT_DIFFUSE',
       'SET_LIGHT_LUT_SPECULAR',
       'SET_LIGHT_LUT_FRESNEL',
       'FAKE_SCENE_LIGHT']),
     ('LIGHT_PASS', False, ['SET_VIEWPORT',
       'SET_VIEW',
       'SET_PROJECTION',
       'SET_VISIBILITY_RESULT',
       'SET_VISUALIZATION',
       'RENDER_LIGHTS']),
     ('SETUP_GATHER', True, ['RENDER_SSAO',
       'SET_FINAL_RT',
       'SET_VAR_LIGHTS',
       'UNBIND_SPECULAR_LIGHT_RT']),
     ('GATHER_PASS', False, ['SET_VIEWPORT',
       'SET_VIEW',
       'SET_PROJECTION',
       'SET_VISIBILITY_RESULT',
       'SET_VISUALIZATION',
       'DISABLE_CUBEMAP',
       'SET_VAR_FRAMEBUFFER_DIMENSIONS',
       'SET_SRGB_WRITE_ON',
       'RENDER_GATHER',
       'SET_SRGB_WRITE_OFF',
       'FULL_GATHER_SHADER',
       'FAKE_ENHANCE_EDGES',
       'ENABLE_CUBEMAP',
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
     ('Lighting', [iVis.WoDEnlightenOnlyVisualization,
       iVis.WoDDiffuseLightOnlyVisualization,
       iVis.WoDSpecularLightOnlyVisualization,
       iVis.WoDFinalDiffuseVisualization,
       iVis.WoDFinalSpecularVisualization]),
     ('Color', [iVis.WoDDiffuseOnlyVisualization, iVis.WoDSpecularOnlyVisualization]),
     ('Data', [iVis.WoDNormalsVisualization, iVis.WoDSurfaceStylesVisualization])]

    def DetectFakeExteriorLight(self):
        self.fakeExteriorScene = False
        fakeLightIDs = [2293,
         2542,
         2517,
         2342,
         2445,
         2355,
         2356,
         2353,
         2354,
         2335,
         2263,
         2261]
        if hasattr(self, 'sceneID'):
            if self.sceneID in fakeLightIDs:
                self.fakeExteriorScene = True
        else:
            self.sceneID = 0



    def _SetScene(self, scene):
        SceneRenderJobInterior._SetScene(self, scene)
        if hasattr(scene, 'id') is True:
            self.sceneID = scene.id
        else:
            self.sceneID = 0
        self.DetectFakeExteriorLight()



    def _ManualInit(self, name = 'WodSceneRenderJobInterior'):
        SceneRenderJobInterior._ManualInit(self)
        self._enablePostProcess = True
        if hasattr(self, 'fakeExteriorScene') is False:
            self.fakeExteriorScene = False
        self.gatherFormat = None
        self.gbufferColorFormat = None
        self.gatherTarget = None
        self.scratchA = None
        self.scratchB = None
        self.scratch16A = None
        self.scratch16B = None
        self.gatherShader = None
        self.clearQuadShader = None
        self.whiteBoxEdgeShader = None
        self.sceneLightShader = None
        self.lightAccumulationFormat = None
        self.specularPrePassRenderTarget = None
        self.diffusePrePassRenderTarget = None
        self.lightAccumulationTarget = None
        self.specularLightAccumulationTarget = None
        self.specularLUT = None
        self.fresnelLUT = None
        self.diffuseLUT = None
        self.swapChain = None



    def SetupPostProcessSteps(self):
        sm = trinity.GetShaderManager()
        for s in sm.shaderLibrary:
            if s.name == 'PostProcess':
                self.postShader = trinity.Tr2ShaderMaterial()
                self.postShader.highLevelShaderName = 'PostProcess'
                self.postShader.PopulateDefaultParameters()
                lut = self.postShader.parameters['RGBLookup']
                lut.resourcePath = 'res:/graphics/texture/BaseRGBLUT.dds'
                self.AddStep('SET_GATHER_RT', trinity.TriStepSetRenderTarget())

        if self.postShader is not None:
            self.AddStep('POST_PROCESS', trinity.TriStepRenderFullScreenShader(self.postShader))



    def _CreateBasicRenderSteps(self):
        SceneRenderJobInterior._CreateBasicRenderSteps(self)
        self.AddStep('SET_PREPASS_RT', trinity.TriStepSetRenderTargetMRT(1, None))
        self.AddStep('SET_SPECULAR_RT', trinity.TriStepSetRenderTargetMRT(2, None))
        self.AddStep('SET_DIFFUSE_RT', trinity.TriStepSetRenderTargetMRT(3, None))
        self.AddStep('SET_DIFFUSELIGHT_RT', trinity.TriStepSetRenderTargetMRT(0, None))
        self.AddStep('SET_SPECULAR_LIGHT_RT', trinity.TriStepSetRenderTargetMRT(0, None))
        self.AddStep('UNBIND_RT_1', trinity.TriStepSetRenderTargetMRT(1, None))
        self.AddStep('UNBIND_RT_2', trinity.TriStepSetRenderTargetMRT(2, None))
        self.AddStep('UNBIND_RT_3', trinity.TriStepSetRenderTargetMRT(3, None))
        self.AddStep('UNBIND_SPECULAR_LIGHT_RT', trinity.TriStepSetRenderTargetMRT(1, None))
        self.AddStep('SET_SPECULAR_LIGHT_RT_1', trinity.TriStepSetRenderTargetMRT(1, None))
        self.AddStep('SET_LIGHT_RT', trinity.TriStepSetRenderTargetMRT(0, None))
        if self.swapChain is None:
            self.AddStep('SET_FINAL_RT', trinity.TriStepSetRenderTarget())
        else:
            self.AddStep('SET_FINAL_RT', trinity.TriStepSetRenderTarget(self.swapChain.backBuffer))
        self.SetupPostProcessSteps()
        width = trinity.device.GetPresentParameters()['BackBufferWidth']
        height = trinity.device.GetPresentParameters()['BackBufferHeight']
        d = geo2.Vector(width, height, 1.0 / width, 1.0 / height)
        self.AddStep('SET_VAR_FRAMEBUFFER_DIMENSIONS', trinity.TriStepSetVariableStore('FramebufferDimensions', d))



    def ChooseBufferFormats(self):
        self.depthFormat = trinity.TRIFMT_INTZ
        self.prePassFormat = trinity.TRIFMT_A16B16G16R16
        self.lightAccumulationFormat = trinity.TRIFMT_A16B16G16R16F
        self.gatherFormat = trinity.TRIFMT_A8R8G8B8
        customDepthFormat = True
        self.gbufferColorFormat = trinity.TRIFMT_A8R8G8B8
        if not customDepthFormat:
            self.RemoveStep('SET_DEPTH')
            self.RemoveStep('RESTORE_DEPTH')



    def DoReleaseResources(self, level):
        self.renderTargetList = None
        self.backBufferDepthStencil = None
        self.backBufferRenderTarget = None
        self.prePassDepthStencil = None
        self.prePassRenderTarget = None
        self.specularPrePassRenderTarget = None
        self.diffusePrePassRenderTarget = None
        self.lightAccumulationTarget = None
        self.specularLightAccumulationTarget = None
        self.gatherTarget = None
        self.scratchA = None
        self.scratchB = None
        self.scratch16A = None
        self.scratch16B = None
        self.gatherShader = None
        self.clearQuadShader = None
        self.sceneLightShader = None
        self.whiteBoxEdgeShader = None
        self.specularLUT = None
        self.fresnelLUT = None
        self.diffuseLUT = None
        self.SetRenderTargets(None, None, None, None, None, None, None, None, None)



    def SetupOffsetsAndWeights(self, shader):
        o1 = geo2.Vector(-6.2857, -4.2857, -2.3667, -0.4746)
        o2 = geo2.Vector(1.4513, 3.3519, 5.32, 7.3077)
        w1 = geo2.Vector(0.0077, 0.0461, 0.1647, 0.324)
        w2 = geo2.Vector(0.3042, 0.1186, 0.0275, 0.0071)
        p = shader.parameters['FilterWeights1']
        p.value = w1
        p = shader.parameters['FilterWeights2']
        p.value = w2
        p = shader.parameters['FilterOffsets1']
        p.value = o1
        p = shader.parameters['FilterOffsets2']
        p.value = o2



    def SetupBloomShaderParameters(self, width, height):
        scratchWidth = math.floor(width / 8)
        scratchHeight = math.floor(height / 8)
        ds = geo2.Vector(scratchWidth, scratchHeight, 1.0 / scratchWidth, 1.0 / scratchHeight)
        self.AddStep('SET_VAR_SOURCE8_DIMENSIONS', trinity.TriStepSetVariableStore('SourceDimensions', ds))
        scratch16Width = math.floor(scratchWidth / 2)
        scratch16Height = math.floor(scratchHeight / 2)
        d16 = geo2.Vector(scratch16Width, scratch16Height, 1.0 / scratch16Width, 1.0 / scratch16Height)
        self.AddStep('SET_VAR_SOURCE16_DIMENSIONS', trinity.TriStepSetVariableStore('SourceDimensions', d16))
        self.SetupOffsetsAndWeights(self.filterShaderHorizontal8)
        p = self.filterShaderHorizontal8.parameters['FilterStuff']
        p.x = 1.0
        p.y = 0.0
        self.SetupOffsetsAndWeights(self.filterShaderHorizontal16)
        p = self.filterShaderHorizontal8.parameters['FilterStuff']
        p.x = 1.0
        p.y = 0.0
        self.SetupOffsetsAndWeights(self.filterShaderVertical8)
        p = self.filterShaderHorizontal8.parameters['FilterStuff']
        p.x = 0.0
        p.y = 1.0
        self.SetupOffsetsAndWeights(self.filterShaderVertical16)
        p = self.filterShaderHorizontal8.parameters['FilterStuff']
        p.x = 0.0
        p.y = 1.0



    def SetupBloomPingPongBuffers(self, scratchWidth, scratchHeight):
        isw = int(scratchWidth)
        ish = int(scratchHeight)
        if self.gatherFormat is not None and self.scratchA is None:
            self.scratchA = device.CreateTexture(isw, ish, 1, trinity.TRIUSAGE_RENDERTARGET, self.gatherFormat, trinity.TRIPOOL_DEFAULT)
        if self.gatherFormat is not None and self.scratchB is None:
            self.scratchB = device.CreateTexture(isw, ish, 1, trinity.TRIUSAGE_RENDERTARGET, self.gatherFormat, trinity.TRIPOOL_DEFAULT)
        isw = int(isw / 2)
        ish = int(ish / 2)
        if self.gatherFormat is not None and self.scratch16A is None:
            self.scratch16A = device.CreateTexture(isw, ish, 1, trinity.TRIUSAGE_RENDERTARGET, self.gatherFormat, trinity.TRIPOOL_DEFAULT)
        if self.gatherFormat is not None and self.scratch16B is None:
            self.scratch16B = device.CreateTexture(isw, ish, 1, trinity.TRIUSAGE_RENDERTARGET, self.gatherFormat, trinity.TRIPOOL_DEFAULT)



    def DoPrepareResources(self):
        if not self.enabled or not self.canCreateRenderTargets:
            return 
        if self.renderTargetList is None:
            device = trinity.device
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
            width = trinity.device.GetPresentParameters()['BackBufferWidth']
            height = trinity.device.GetPresentParameters()['BackBufferHeight']
            if self.depthFormat is not None and self.prePassDepthStencil is None:
                if self.depthFormat == self.backBufferDepthStencil.format:
                    self.prePassDepthStencil = self.backBufferDepthStencil
                else:
                    self.prePassDepthStencil = device.CreateTexture(width, height, 1, trinity.TRIUSAGE_DEPTHSTENCIL, self.depthFormat, trinity.TRIPOOL_DEFAULT)
            if self.lightAccumulationFormat is not None and self.lightAccumulationTarget is None:
                self.lightAccumulationTarget = device.CreateTexture(width, height, 1, trinity.TRIUSAGE_RENDERTARGET, self.lightAccumulationFormat, trinity.TRIPOOL_DEFAULT)
            if self.prePassFormat is not None and self.prePassRenderTarget is None:
                self.prePassRenderTarget = device.CreateTexture(width, height, 1, trinity.TRIUSAGE_RENDERTARGET, self.prePassFormat, trinity.TRIPOOL_DEFAULT)
            if self.lightAccumulationFormat is not None and self.specularLightAccumulationTarget is None:
                self.specularLightAccumulationTarget = device.CreateTexture(width, height, 1, trinity.TRIUSAGE_RENDERTARGET, self.lightAccumulationFormat, trinity.TRIPOOL_DEFAULT)
            if self.gbufferColorFormat is not None and self.specularPrePassRenderTarget is None:
                self.specularPrePassRenderTarget = device.CreateTexture(width, height, 1, trinity.TRIUSAGE_RENDERTARGET, self.gbufferColorFormat, trinity.TRIPOOL_DEFAULT)
            if self.gbufferColorFormat is not None and self.diffusePrePassRenderTarget is None:
                self.diffusePrePassRenderTarget = device.CreateTexture(width, height, 1, trinity.TRIUSAGE_RENDERTARGET, self.gbufferColorFormat, trinity.TRIPOOL_DEFAULT)
            if self.gatherFormat is not None and self.gatherTarget is None:
                self.gatherTarget = device.CreateTexture(width, height, 1, trinity.TRIUSAGE_RENDERTARGET, self.gatherFormat, trinity.TRIPOOL_DEFAULT)
            self.noiseTex = trinity.GetNoiseTexture()
            trinity.GetVariableStore().RegisterVariable('NoiseTexture', self.noiseTex)
            self.specularLUT = blue.resMan.GetResource('res:/Graphics/Texture/WODSpecularLUT.dds')
            self.diffuseLUT = blue.resMan.GetResource('res:/Graphics/Texture/WODDiffuseLUT.dds')
            self.fresnelLUT = blue.resMan.GetResource('res:/Graphics/Texture/WODFresnelLUT.dds')
            self.renderTargetList = (blue.BluePythonWeakRef(self.backBufferDepthStencil),
             blue.BluePythonWeakRef(self.backBufferRenderTarget),
             blue.BluePythonWeakRef(self.prePassDepthStencil),
             blue.BluePythonWeakRef(self.prePassRenderTarget),
             blue.BluePythonWeakRef(self.lightAccumulationTarget),
             blue.BluePythonWeakRef(self.gatherTarget),
             blue.BluePythonWeakRef(self.specularPrePassRenderTarget),
             blue.BluePythonWeakRef(self.diffusePrePassRenderTarget),
             blue.BluePythonWeakRef(self.specularLightAccumulationTarget))
        thingToSet = (x.object for x in self.renderTargetList)
        self.SetRenderTargets(*thingToSet)



    def SetSSAO(self, ssaoStep):
        pass



    def SetRenderTargets(self, backBufferDepthStencil, backBufferRenderTarget, prePassDepthStencil, prePassRenderTarget, lightAccumulationTarget, gatherTarget, specularPrePassRenderTarget, diffusePrePassRenderTarget, specularLightAccumulationTarget):
        SceneRenderJobInterior.SetRenderTargets(self, backBufferDepthStencil, backBufferRenderTarget, prePassDepthStencil, prePassRenderTarget, lightAccumulationTarget)
        if specularPrePassRenderTarget is not None:
            self.SetStepAttr('SET_SPECULAR_RT', 'target', specularPrePassRenderTarget.GetSurfaceLevel(0))
        else:
            self.SetStepAttr('SET_SPECULAR_RT', 'target', None)
        if diffusePrePassRenderTarget is not None:
            self.SetStepAttr('SET_DIFFUSE_RT', 'target', diffusePrePassRenderTarget.GetSurfaceLevel(0))
        else:
            self.SetStepAttr('SET_DIFFUSE_RT', 'target', None)
        if lightAccumulationTarget is not None:
            self.SetStepAttr('SET_DIFFUSELIGHT_RT', 'target', lightAccumulationTarget.GetSurfaceLevel(0))
        else:
            self.SetStepAttr('SET_DIFFUSELIGHT_RT', 'target', None)
        if self.gatherShader is None:
            self.gatherShader = trinity.Tr2ShaderMaterial()
            self.gatherShader.highLevelShaderName = 'FullDeferredGather'
            self.gatherShader.PopulateDefaultParameters()
        if self.clearQuadShader is None:
            self.clearQuadShader = trinity.Tr2ShaderMaterial()
            self.clearQuadShader.highLevelShaderName = 'ClearQuad'
        if self.whiteBoxEdgeShader is None:
            self.whiteBoxEdgeShader = trinity.Tr2ShaderMaterial()
            self.whiteBoxEdgeShader.highLevelShaderName = 'WhiteBoxEdges'
            self.whiteBoxEdgeShader.PopulateDefaultParameters()
            self.whiteBoxEdgeShader.BindLowLevelShader([])
        if prePassRenderTarget is not None:
            if self.sceneLightShader is None:
                self.sceneLightShader = trinity.Tr2ShaderMaterial()
                self.sceneLightShader.highLevelShaderName = 'FullSceneLight'
                self.sceneLightShader.PopulateDefaultParameters()
                self.sceneLightShader.parameters['NormalIDBuffer'].SetResource(prePassRenderTarget)
                self.sceneLightShader.BindLowLevelShader([])
            else:
                self.sceneLightShader.parameters['NormalIDBuffer'].SetResource(prePassRenderTarget)
                self.sceneLightShader.BindLowLevelShader([])
        else:
            self.sceneLightShader = None
        if diffusePrePassRenderTarget is not None:
            self.gatherShader.parameters['DiffuseGBuffer'].SetResource(diffusePrePassRenderTarget)
        if specularPrePassRenderTarget is not None:
            self.gatherShader.parameters['SpecularGBuffer'].SetResource(specularPrePassRenderTarget)
            self.AddStep('SET_VAR_SPECULAR_BLEND', trinity.TriStepSetVariableStore('SpecularGBuffer', specularPrePassRenderTarget))
        if specularLightAccumulationTarget is not None:
            self.gatherShader.parameters['SpecularLighting'].SetResource(specularLightAccumulationTarget)
        if lightAccumulationTarget is not None:
            self.gatherShader.parameters['DiffuseLighting'].SetResource(lightAccumulationTarget)
        if self.gatherShader is not None:
            self.AddStep('FULL_GATHER_SHADER', trinity.TriStepRenderFullScreenShader(self.gatherShader))
            self.gatherShader.BindLowLevelShader(['none'])
        if self.clearQuadShader is not None:
            self.AddStep('CLEAR_PREPASS_QUAD', trinity.TriStepRenderFullScreenShader(self.clearQuadShader))
            self.clearQuadShader.BindLowLevelShader(['none'])
        if self.sceneLightShader is not None:
            self.AddStep('FAKE_ENHANCE_EDGES', trinity.TriStepRenderFullScreenShader(self.whiteBoxEdgeShader))
            self.AddStep('FAKE_SCENE_LIGHT', trinity.TriStepRenderFullScreenShader(self.sceneLightShader))
        if lightAccumulationTarget is not None:
            self.SetStepAttr('SET_LIGHT_RT', 'target', lightAccumulationTarget.GetSurfaceLevel(0))
        else:
            self.SetStepAttr('SET_LIGHT_RT', 'target', None)
        if specularLightAccumulationTarget is not None:
            self.SetStepAttr('SET_SPECULAR_LIGHT_RT', 'target', specularLightAccumulationTarget.GetSurfaceLevel(0))
            self.SetStepAttr('SET_SPECULAR_LIGHT_RT_1', 'target', specularLightAccumulationTarget.GetSurfaceLevel(0))
        else:
            self.SetStepAttr('SET_SPECULAR_LIGHT_RT', 'target', None)
            self.SetStepAttr('SET_SPECULAR_LIGHT_RT_1', 'target', None)
        if gatherTarget is not None:
            self.SetStepAttr('SET_GATHER_RT', 'target', gatherTarget.GetSurfaceLevel(0))
            self.AddStep('SET_VAR_GATHERFRAMEBUFFER_RTT', trinity.TriStepSetVariableStore('Framebuffer', gatherTarget))
            if self.postShader is not None:
                trinity.GetVariableStore().RegisterVariable('Framebuffer', gatherTarget)
                self.postShader.BindLowLevelShader(['none'])
        else:
            self.SetStepAttr('SET_GATHER_RT', 'target', None)
        testPP = prefs.ini.GetValue('postprocessing', default=1)
        if testPP == 1:
            self._enablePostProcess = True
        else:
            self._enablePostProcess = False
        self.specularLUT = blue.resMan.GetResource('res:/Graphics/Texture/WODSpecularLUT.dds')
        self.diffuseLUT = blue.resMan.GetResource('res:/Graphics/Texture/WODDiffuseLUT.dds')
        self.fresnelLUT = blue.resMan.GetResource('res:/Graphics/Texture/WODFresnelLUT.dds')
        self.AddStep('SET_LIGHT_LUT_DIFFUSE', trinity.TriStepSetVariableStore('MaterialLUT_RdotL', self.specularLUT))
        self.AddStep('SET_LIGHT_LUT_SPECULAR', trinity.TriStepSetVariableStore('MaterialLUT_NdotV', self.fresnelLUT))
        self.AddStep('SET_LIGHT_LUT_FRESNEL', trinity.TriStepSetVariableStore('MaterialLUT_NdotL', self.diffuseLUT))
        if gatherTarget is not None:
            width = trinity.device.GetPresentParameters()['BackBufferWidth']
            height = trinity.device.GetPresentParameters()['BackBufferHeight']
            d = geo2.Vector(width, height, 1.0 / width, 1.0 / height)
            self.AddStep('SET_VAR_FRAMEBUFFER_DIMENSIONS', trinity.TriStepSetVariableStore('FramebufferDimensions', d))
        self.UpdatePostProcess(gatherTarget, backBufferRenderTarget)
        self.AddStep('SET_SRGB_WRITE_ON', trinity.TriStepSetRenderState(trinity.D3DRS_SRGBWRITEENABLE, 1))
        self.AddStep('SET_SRGB_WRITE_OFF', trinity.TriStepSetRenderState(trinity.D3DRS_SRGBWRITEENABLE, 0))
        self.AddStep('CLEAR_GATHER_COLOR', trinity.TriStepClear((0, 0, 0.4, 0), None, None))



    def UpdatePostProcess(self, gatherTarget, backbufferTarget):
        if not gatherTarget:
            return 
        if self._enablePostProcess:
            self.SetStepAttr('SET_GATHER_RT', 'target', gatherTarget.GetSurfaceLevel(0))
            self.SetStepAttr('SET_FINAL_RT', 'enabled', True)
            self.SetStepAttr('POST_PROCESS', 'enabled', True)
        else:
            self.SetStepAttr('SET_GATHER_RT', 'target', backbufferTarget)
            self.SetStepAttr('SET_FINAL_RT', 'enabled', False)
            self.SetStepAttr('POST_PROCESS', 'enabled', False)
        self.DetectFakeExteriorLight()
        if self.fakeExteriorScene:
            self.SetStepAttr('FAKE_SCENE_LIGHT', 'enabled', True)
            self.SetStepAttr('FAKE_ENHANCE_EDGES', 'enabled', True)
        else:
            self.SetStepAttr('FAKE_SCENE_LIGHT', 'enabled', False)
            self.SetStepAttr('FAKE_ENHANCE_EDGES', 'enabled', False)



    def GetEnablePostProcess(self):
        return self._enablePostProcess



    def SetEnablePostProcess(self, isEnabled):
        if self.gatherTarget is None:
            isEnabled = False
        self._enablePostProcess = isEnabled
        self.UpdatePostProcess(self.gatherTarget, self.backBufferRenderTarget)



    def SetClearColor(self, color):
        step = self.GetStep('CLEAR_GATHER_COLOR')
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




