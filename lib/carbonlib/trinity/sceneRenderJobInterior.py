from trinity.sceneRenderJobBase import SceneRenderJobBase
import interiorVisualizations as iVis
import trinity
import blue

def CreateSceneRenderJobInterior(name = None, stageKey = None):
    newRJ = SceneRenderJobInterior()
    if name is not None:
        newRJ.ManualInit(name)
    else:
        newRJ.ManualInit()
    newRJ.SetMultiViewStage(stageKey)
    return newRJ



class SceneRenderJobInterior(SceneRenderJobBase):
    renderStepOrder = ['UPDATE_SCENE',
     'UPDATE_STEREO',
     'UPDATE_BACKGROUND_SCENE',
     'UPDATE_BACKGROUND_CAMERA',
     'UPDATE_UI',
     'SET_DEPTH',
     'SET_BACKGROUND_RT',
     'SET_VIEWPORT',
     'SET_BACKGROUND_PROJECTION',
     'SET_BACKGROUND_VIEW',
     'CLEAR_BACKGROUND_RT',
     'RENDER_BACKGROUND_SCENE',
     'CLEAR_BACKGROUND_DEPTH',
     'SET_PROJECTION',
     'SET_VIEW',
     'VISIBILITY_QUERY',
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
     'RENDER_LIGHTS',
     'RENDER_SSAO',
     'SET_VAR_SSAO',
     'SET_FINAL_RT',
     'CLEAR_FINAL_RT',
     'SET_VAR_LIGHTS',
     'RENDER_GATHER',
     'RENDER_FLARES',
     'END_MANAGED_RENDERING',
     'UPDATE_TOOLS',
     'RENDER_INFO',
     'RENDER_PROXY',
     'RENDER_VISUAL',
     'RENDER_TOOLS',
     'RESTORE_DEPTH',
     'RENDER_UI']
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
       'SET_FINAL_RT',
       'SET_VAR_LIGHTS']),
     ('GATHER_PASS', False, ['SET_VIEWPORT',
       'SET_VIEW',
       'SET_PROJECTION',
       'SET_VISIBILITY_RESULT',
       'SET_VISUALIZATION',
       'ENABLE_WIREFRAME',
       'DISABLE_CUBEMAP',
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
       iVis.DepthVisualization,
       iVis.OcclusionVisualization]),
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
       iVis.PrePassLightNormalVisualization,
       iVis.PrePassLightDepthVisualization,
       iVis.PrePassLightWorldPositionVisualization,
       iVis.PrePassLightOverdrawVisualization,
       iVis.ShadowOnlyVisualization])]

    def _ManualInit(self, name = 'SceneRenderJobInterior'):
        self.depthFormat = None
        self.prePassFormat = None
        self.lightAccumulationFormat = None
        self.backBufferDepthStencil = None
        self.backBufferRenderTarget = None
        self.prePassDepthStencil = None
        self.prePassRenderTarget = None
        self.lightAccumulationTarget = None
        self.renderTargetList = None
        self.ui = None
        self.backgroundScene = None
        self.backgroundUpdateFunction = None
        self.swapChain = None



    def _SetScene(self, scene):
        self.SetStepAttr('UPDATE_SCENE', 'object', scene)
        self.SetStepAttr('VISIBILITY_QUERY', 'queryable', scene)
        self.SetStepAttr('SET_VISIBILITY_RESULT', 'queryable', scene)
        self.SetStepAttr('BEGIN_MANAGED_RENDERING', 'scene', scene)
        self.SetStepAttr('RENDER_PREPASS', 'scene', scene)
        self.SetStepAttr('RENDER_LIGHTS', 'scene', scene)
        self.SetStepAttr('RENDER_GATHER', 'scene', scene)
        self.SetStepAttr('RENDER_FLARES', 'scene', scene)
        self.SetStepAttr('END_MANAGED_RENDERING', 'scene', scene)



    def _CreateBasicRenderSteps(self):
        self.AddStep('UPDATE_SCENE', trinity.TriStepUpdate(self.GetScene()))
        result = trinity.Tr2VisibilityResults()
        self.AddStep('VISIBILITY_QUERY', trinity.TriStepVisibilityQuery(self.GetScene(), result))
        self.AddStep('SET_VISIBILITY_RESULT', trinity.TriStepSetVisibilityResults(self.GetScene(), result))
        if self.swapChain is None:
            self.AddStep('SET_PREPASS_RT', trinity.TriStepSetRenderTarget())
        else:
            self.AddStep('SET_PREPASS_RT', trinity.TriStepSetRenderTarget(self.swapChain.object.backBuffer))
        self.AddStep('CLEAR_PREPASS', trinity.TriStepClear((0, 0, 0, 0), 1.0, 0))
        self.AddStep('BEGIN_MANAGED_RENDERING', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_BEGIN_RENDER))
        self.AddStep('RENDER_PREPASS', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_PRE_PASS))
        if self.swapChain is None:
            self.AddStep('SET_LIGHT_RT', trinity.TriStepSetRenderTarget())
        else:
            self.AddStep('SET_LIGHT_RT', trinity.TriStepSetRenderTarget(self.swapChain.object.backBuffer))
        self.AddStep('CLEAR_LIGHTS', trinity.TriStepClear((0, 0, 0, 0), None, None))
        self.AddStep('RENDER_LIGHTS', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_LIGHT_PASS))
        if self.swapChain is None:
            self.AddStep('SET_FINAL_RT', trinity.TriStepSetRenderTarget())
        else:
            self.AddStep('SET_FINAL_RT', trinity.TriStepSetRenderTarget(self.swapChain.object.backBuffer))
        self.AddStep('CLEAR_FINAL_RT', trinity.TriStepClear((0, 0, 0, 0), None, None))
        self.AddStep('RENDER_GATHER', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_GATHER_PASS))
        self.AddStep('RENDER_FLARES', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_FLARE_PASS))
        self.AddStep('END_MANAGED_RENDERING', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_END_RENDER))



    def ChooseBufferFormats(self):
        shaderModel = trinity.GetShaderModel()
        self.depthFormat = trinity.TRIFMT_D24S8
        customDepthFormat = False
        if shaderModel == 'SM_3_0_HI':
            self.prePassFormat = trinity.TRIFMT_A16B16G16R16
            self.lightAccumulationFormat = trinity.TRIFMT_A16B16G16R16F
        elif shaderModel == 'SM_3_0_DEPTH':
            self.depthFormat = trinity.TRIFMT_INTZ
            self.prePassFormat = trinity.TRIFMT_A16B16G16R16
            self.lightAccumulationFormat = trinity.TRIFMT_A16B16G16R16F
            customDepthFormat = True
        else:
            self.prePassFormat = trinity.TRIFMT_A8R8G8B8
            self.lightAccumulationFormat = trinity.TRIFMT_A8R8G8B8
        if not customDepthFormat:
            self.RemoveStep('SET_DEPTH')
            self.RemoveStep('RESTORE_DEPTH')



    def DoReleaseResources(self, level):
        self.SetRenderTargets(None, None, None, None, None)
        self.renderTargetList = None
        self.backBufferDepthStencil = None
        self.backBufferRenderTarget = None
        self.prePassDepthStencil = None
        self.prePassRenderTarget = None
        self.lightAccumulationTarget = None



    def DoPrepareResources(self):
        if not self.enabled or not self.canCreateRenderTargets:
            return 
        white = blue.resMan.GetResource('res:/Texture/Global/white.dds')
        self.AddStep('SET_VAR_SSAO', trinity.TriStepSetVariableStore('SSAOMap', white))
        if self.renderTargetList is None:
            device = trinity.device
            self.ChooseBufferFormats()
            if self.swapChain is None:
                if self.backBufferDepthStencil is None:
                    self.backBufferDepthStencil = device.GetDepthStencilSurface()
                if self.backBufferRenderTarget is None:
                    self.backBufferRenderTarget = device.GetRenderTarget()
                width = device.GetPresentParameters()['BackBufferWidth']
                height = device.GetPresentParameters()['BackBufferHeight']
            elif self.backBufferDepthStencil is None:
                self.backBufferDepthStencil = self.swapChain.object.depthStencilBuffer
            if self.backBufferRenderTarget is None:
                self.backBufferRenderTarget = self.swapChain.object.backBuffer
            width = self.swapChain.object.backBuffer.width
            height = self.swapChain.object.backBuffer.height
            if self.depthFormat is not None and self.prePassDepthStencil is None:
                if self.depthFormat == self.backBufferDepthStencil.format:
                    self.prePassDepthStencil = self.backBufferDepthStencil
                else:
                    self.prePassDepthStencil = device.CreateTexture(width, height, 1, trinity.TRIUSAGE_DEPTHSTENCIL, self.depthFormat, trinity.TRIPOOL_DEFAULT)
            if self.prePassFormat is not None and self.prePassRenderTarget is None:
                self.prePassRenderTarget = device.CreateTexture(width, height, 1, trinity.TRIUSAGE_RENDERTARGET, self.prePassFormat, trinity.TRIPOOL_DEFAULT)
            if self.lightAccumulationFormat is not None and self.lightAccumulationTarget is None:
                self.lightAccumulationTarget = device.CreateTexture(width, height, 1, trinity.TRIUSAGE_RENDERTARGET, self.lightAccumulationFormat, trinity.TRIPOOL_DEFAULT)
            self.renderTargetList = (blue.BluePythonWeakRef(self.backBufferDepthStencil),
             blue.BluePythonWeakRef(self.backBufferRenderTarget),
             blue.BluePythonWeakRef(self.prePassDepthStencil),
             blue.BluePythonWeakRef(self.prePassRenderTarget),
             blue.BluePythonWeakRef(self.lightAccumulationTarget))
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
            self.AddStep('CLEAR_FINAL_RT', trinity.TriStepClear((0, 0, 0, 0), None, None))
            self.RemoveStep('CLEAR_BACKGROUND_RT')
            self.RemoveStep('CLEAR_BACKGROUND_DEPTH')
            self.backgroundScene = None
        else:
            self.AddStep('UPDATE_BACKGROUND_SCENE', trinity.TriStepUpdate(scene))
            self.AddStep('RENDER_BACKGROUND_SCENE', trinity.TriStepRenderScene(scene))
            self.AddStep('CLEAR_BACKGROUND_RT', trinity.TriStepClear((0, 0, 0, 0), 1.0, 0))
            self.AddStep('CLEAR_BACKGROUND_DEPTH', trinity.TriStepClear(None, 1.0, 0))
            self.RemoveStep('CLEAR_FINAL_RT')
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



    def SetSSAO(self, ssaoStep):
        if ssaoStep is not None:
            if type(self.prePassDepthStencil) is trinity.TriTextureRes:
                ssaoStep.depthTexture = self.prePassDepthStencil
            else:
                ssaoStep.depthTexture = self.prePassRenderTarget
            ssaoStep.normalTexture = self.prePassRenderTarget
            self.AddStep('RENDER_SSAO', ssaoStep)
        else:
            self.RemoveStep('RENDER_SSAO')



    def SetRenderTargets(self, backBufferDepthStencil, backBufferRenderTarget, prePassDepthStencil, prePassRenderTarget, lightAccumulationTarget):
        if prePassRenderTarget is not None:
            self.SetStepAttr('SET_PREPASS_RT', 'target', prePassRenderTarget.GetSurfaceLevel(0))
        else:
            self.SetStepAttr('SET_PREPASS_RT', 'target', None)
        if lightAccumulationTarget is not None:
            self.SetStepAttr('SET_LIGHT_RT', 'target', lightAccumulationTarget.GetSurfaceLevel(0))
        else:
            self.SetStepAttr('SET_LIGHT_RT', 'target', None)
        self.SetStepAttr('SET_FINAL_RT', 'target', backBufferRenderTarget)
        if self.backgroundScene is not None:
            self.AddStep('SET_BACKGROUND_RT', trinity.TriStepSetRenderTarget(backBufferRenderTarget))
        if prePassDepthStencil is not None:
            if type(prePassDepthStencil) is trinity.TriTextureRes:
                self.AddStep('SET_DEPTH', trinity.TriStepSetDepthStencil(prePassDepthStencil.GetSurfaceLevel(0)))
                self.AddStep('SET_VAR_LIGHTS_DEPTH', trinity.TriStepSetVariableStore('LightPrePassDepthMap', prePassDepthStencil))
            elif type(prePassDepthStencil) is trinity.TriSurface:
                self.SetStepAttr('SET_DEPTH', 'target', prePassDepthStencil)
        else:
            self.SetStepAttr('SET_DEPTH', 'target', None)
        self.SetStepAttr('RESTORE_DEPTH', 'target', backBufferDepthStencil)
        self.AddStep('SET_VAR_LIGHTS_PREPASS', trinity.TriStepSetVariableStore('LightPrePassMap', prePassRenderTarget))
        self.AddStep('SET_VAR_LIGHTS', trinity.TriStepSetVariableStore('LightAccumulationMap', lightAccumulationTarget))
        if type(prePassDepthStencil) is trinity.TriTextureRes:
            self.SetStepAttr('RENDER_SSAO', 'depthTexture', prePassDepthStencil)
        else:
            self.SetStepAttr('RENDER_SSAO', 'depthTexture', prePassRenderTarget)
        self.SetStepAttr('RENDER_SSAO', 'normalTexture', prePassRenderTarget)



    def GetRenderTargets(self):
        return self.renderTargetList



    def SetClearColor(self, color):
        step = self.GetStep('CLEAR_BACKGROUND_RT')
        if step is not None:
            step.color = color
        step = self.GetStep('CLEAR_FINAL_RT')
        if step is not None:
            step.color = color



    def SetSwapChain(self, swapChain):
        self.swapChain = blue.BluePythonWeakRef(swapChain)




