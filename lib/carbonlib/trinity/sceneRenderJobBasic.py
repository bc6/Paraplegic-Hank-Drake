from trinity.sceneRenderJobBase import SceneRenderJobBase
import trinity
import blue

def CreateSceneRenderJobBasic(name = None):
    newRJ = SceneRenderJobBasic()
    if name is not None:
        newRJ.ManualInit(name)
    else:
        newRJ.ManualInit()
    return newRJ



class SceneRenderJobBasic(SceneRenderJobBase):
    renderStepOrder = ['UPDATE_SCENE',
     'SET_VIEWPORT',
     'SET_PROJECTION',
     'SET_VIEW',
     'RENDER_SCENE']

    def _ManualInit(self, name = 'SceneRenderJobInterior'):
        self.ui = None



    def _SetScene(self, scene):
        self.SetStepAttr('UPDATE_SCENE', 'object', scene)
        self.SetStepAttr('RENDER_SCENE', 'scene', scene)



    def _CreateBasicRenderSteps(self):
        self.AddStep('UPDATE_SCENE', trinity.TriStepUpdate(self.GetScene()))
        self.AddStep('RENDER_SCENE', trinity.TriStepRenderScene(self.GetScene()))



    def DoReleaseResources(self, level):
        pass



    def DoPrepareResources(self):
        pass



    def SetUI(self, ui):
        if ui is None:
            self.RemoveStep('UPDATE_UI')
            self.RemoveStep('RENDER_UI')
        else:
            self.AddStep('UPDATE_UI', trinity.TriStepUpdate(ui))
            self.AddStep('RENDER_UI', trinity.TriStepRenderUI(ui))



    def EnableSceneUpdate(self, isEnabled):
        if isEnabled:
            self.AddStep('UPDATE_SCENE', trinity.TriStepUpdate(self.GetScene()))
        else:
            self.RemoveStep('UPDATE_SCENE')




