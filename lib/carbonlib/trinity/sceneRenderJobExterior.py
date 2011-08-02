from trinity.sceneRenderJobBase import SceneRenderJobBase
import trinity
import blue

def CreateSceneRenderJobExterior(name = None):
    newRJ = SceneRenderJobExterior()
    if name is not None:
        newRJ.ManualInit(name)
    else:
        newRJ.ManualInit()
    return newRJ



class SceneRenderJobExterior(SceneRenderJobBase):
    renderStepOrder = ['SET_PROJECTION',
     'SET_VIEW',
     'SET_VIEWPORT',
     'UPDATE_SCENE',
     'UPDATE_UI',
     'SET_RENDER_TARGET',
     'SET_DEPTH_STENCIL',
     'CLEAR',
     'RENDER_SCENE',
     'RENDER_POST_PROCESS',
     'POST_RENDER_CB',
     'UPDATE_TOOLS',
     'RENDER_INFO',
     'RENDER_PROXY',
     'RENDER_VISUAL',
     'RENDER_TOOLS',
     'RENDER_UI']

    def _ManualInit(self, name = 'SceneRenderJobExterior'):
        self.ui = None



    def _SetScene(self, scene):
        self.SetStepAttr('UPDATE_SCENE', 'object', scene)
        self.SetStepAttr('RENDER_SCENE', 'scene', scene)



    def _CreateBasicRenderSteps(self):
        self.AddStep('UPDATE_SCENE', trinity.TriStepUpdate(self.GetScene()))
        self.AddStep('SET_RENDER_TARGET', trinity.TriStepSetRenderTarget(trinity.device.GetRenderTarget()))
        self.AddStep('SET_DEPTH_STENCIL', trinity.TriStepSetDepthStencil(trinity.device.GetDepthStencilSurface()))
        self.AddStep('CLEAR', trinity.TriStepClear((0, 0, 0, 0), 1.0, 0))
        self.AddStep('RENDER_SCENE', trinity.TriStepRenderScene(self.GetScene()))



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
            self.AddStep('SET_VIEW', trinity.TriStepSetView(camera.viewMatrix))
            self.AddStep('SET_PROJECTION', trinity.TriStepSetProjection(camera.projectionMatrix))



    def EnableSceneUpdate(self, isEnabled):
        if isEnabled:
            self.AddStep('UPDATE_SCENE', trinity.TriStepUpdate(self.GetScene()))
        else:
            self.RemoveStep('UPDATE_SCENE')



    def DoPrepareResources(self):
        pass



    def DoReleaseResources(self, level):
        pass




