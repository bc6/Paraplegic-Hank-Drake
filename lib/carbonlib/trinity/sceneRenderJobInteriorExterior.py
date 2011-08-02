from trinity.sceneRenderJobBase import SceneRenderJobBase
from trinity.sceneRenderJobInterior import SceneRenderJobInterior
import interiorVisualizations as iVis
import trinity
import blue

def CreateSceneRenderJobInteriorExterior(name = None, stageKey = None):
    newRJ = SceneRenderJobInteriorExterior()
    if name is not None:
        newRJ.ManualInit(name)
    else:
        newRJ.ManualInit()
    newRJ.SetMultiViewStage(stageKey)
    return newRJ



class SceneRenderJobInteriorExterior(SceneRenderJobInterior):
    renderStepOrder = ['UPDATE_SCENE',
     'UPDATE_SCENE_EXTERIOR',
     'UPDATE_BACKGROUND_SCENE',
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
     'VISIBILITY_QUERY_EXTERIOR',
     'SET_VISUALIZATION',
     'SET_VISUALIZATION_EXTERIOR',
     'SET_DEPTH',
     'SET_PREPASS_RT',
     'CLEAR_PREPASS',
     'BEGIN_MANAGED_RENDERING',
     'BEGIN_MANAGED_RENDERING_EXTERIOR',
     'ENABLE_WIREFRAME',
     'DISABLE_CUBEMAP',
     'RENDER_PREPASS',
     'RENDER_PREPASS_EXTERIOR',
     'SET_LIGHT_RT',
     'CLEAR_LIGHTS',
     'SET_VAR_LIGHTS_DEPTH',
     'SET_VAR_LIGHTS_PREPASS',
     'RENDER_LIGHTS',
     'RENDER_LIGHTS_EXTERIOR',
     'RENDER_SSAO',
     'SET_FINAL_RT',
     'CLEAR_FINAL_RT',
     'SET_VAR_LIGHTS',
     'RENDER_GATHER',
     'RENDER_GATHER_EXTERIOR',
     'RENDER_FLARES',
     'END_MANAGED_RENDERING',
     'END_MANAGED_RENDERING_EXTERIOR',
     'UPDATE_TOOLS',
     'RENDER_INFO',
     'RENDER_VISUAL',
     'RENDER_TOOLS',
     'RESTORE_DEPTH',
     'ENABLE_CUBEMAP',
     'RESTORE_WIREFRAME',
     'RENDER_UI']
    multiViewStages = [('SETUP', True, ['UPDATE_SCENE',
       'UPDATE_SCENE_EXTERIOR',
       'UPDATE_BACKGROUND_SCENE',
       'SET_DEPTH',
       'BEGIN_MANAGED_RENDERING',
       'BEGIN_MANAGED_RENDERING_EXTERIOR']),
     ('SETUP_BACKGROUND_RENDERING', True, ['SET_FINAL_RT', 'CLEAR_BACKGROUND_RT']),
     ('SETUP_VIEW', False, ['SET_VIEWPORT',
       'SET_PROJECTION',
       'SET_VIEW',
       'VISIBILITY_QUERY',
       'FILTER_VISIBILITY_RESULT',
       'VISIBILITY_QUERY_EXTERIOR']),
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
       'SET_VISUALIZATION_EXTERIOR',
       'ENABLE_WIREFRAME',
       'RENDER_PREPASS',
       'RENDER_PREPASS_EXTERIOR',
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
       'SET_VISUALIZATION_EXTERIOR',
       'RENDER_LIGHTS',
       'RENDER_LIGHTS_EXTERIOR']),
     ('SETUP_GATHER', True, ['RENDER_SSAO', 'SET_FINAL_RT', 'SET_VAR_LIGHTS']),
     ('GATHER_PASS', False, ['SET_VIEWPORT',
       'SET_VIEW',
       'SET_PROJECTION',
       'SET_VISIBILITY_RESULT',
       'SET_VISUALIZATION',
       'SET_VISUALIZATION_EXTERIOR',
       'ENABLE_WIREFRAME',
       'DISABLE_CUBEMAP',
       'RENDER_GATHER',
       'RENDER_GATHER_EXTERIOR',
       'ENABLE_CUBEMAP',
       'RESTORE_WIREFRAME',
       'RENDER_FLARES']),
     ('END_MANAGED_RENDERING', True, ['END_MANAGED_RENDERING', 'END_MANAGED_RENDERING_EXTERIOR']),
     ('TOOLS', False, ['SET_VIEWPORT',
       'SET_VIEW',
       'SET_PROJECTION',
       'UPDATE_TOOLS',
       'RENDER_INFO',
       'RENDER_VISUAL',
       'RENDER_TOOLS']),
     ('TEARDOWN', True, ['RESTORE_DEPTH'])]

    def _ManualInit(self, name = 'SceneRenderJobInteriorExterior'):
        SceneRenderJobInterior._ManualInit(self, name)
        self.exteriorScene = None



    def _SetScene(self, scene):
        if scene:
            self.AddStep('UPDATE_SCENE', trinity.TriStepUpdate(scene))
            result = trinity.Tr2VisibilityResults()
            self.AddStep('VISIBILITY_QUERY', trinity.TriStepVisibilityQuery(scene, result))
            self.AddStep('SET_VISIBILITY_RESULT', trinity.TriStepSetVisibilityResults(scene, result))
            self.AddStep('BEGIN_MANAGED_RENDERING', trinity.TriStepRenderPrePass(scene, trinity.TRIPREPASS_BEGIN_RENDER))
            self.AddStep('RENDER_PREPASS', trinity.TriStepRenderPrePass(scene, trinity.TRIPREPASS_PRE_PASS))
            self.AddStep('RENDER_LIGHTS', trinity.TriStepRenderPrePass(scene, trinity.TRIPREPASS_LIGHT_PASS))
            self.AddStep('RENDER_GATHER', trinity.TriStepRenderPrePass(scene, trinity.TRIPREPASS_GATHER_PASS))
            self.AddStep('RENDER_FLARES', trinity.TriStepRenderPrePass(scene, trinity.TRIPREPASS_FLARE_PASS))
            self.AddStep('END_MANAGED_RENDERING', trinity.TriStepRenderPrePass(scene, trinity.TRIPREPASS_END_RENDER))
            if self.exteriorScene:
                try:
                    self.AddStep('DISABLE_CUBEMAP', trinity.TriStepToggleCubemap(False, scene))
                    self.AddStep('ENABLE_CUBEMAP', trinity.TriStepToggleCubemap(True, scene))
                except TypeError:
                    pass
        else:
            self.RemoveStep('DISABLE_CUBEMAP')
            self.RemoveStep('ENABLE_CUBEMAP')
            self.RemoveStep('UPDATE_SCENE')
            self.RemoveStep('VISIBILITY_QUERY')
            self.RemoveStep('SET_VISIBILITY_RESULT')
            self.RemoveStep('BEGIN_MANAGED_RENDERING')
            self.RemoveStep('RENDER_PREPASS')
            self.RemoveStep('RENDER_LIGHTS')
            self.RemoveStep('RENDER_GATHER')
            self.RemoveStep('RENDER_FLARES')
            self.RemoveStep('END_MANAGED_RENDERING')



    def SetExteriorScene(self, scene):
        if scene is None:
            self.exteriorScene = None
        else:
            self.exteriorScene = blue.BluePythonWeakRef(scene)
        if scene:
            if self.GetScene():
                try:
                    self.AddStep('DISABLE_CUBEMAP', trinity.TriStepToggleCubemap(False, self.GetScene()))
                    self.AddStep('ENABLE_CUBEMAP', trinity.TriStepToggleCubemap(True, self.GetScene()))
                except TypeError:
                    pass
            self.AddStep('UPDATE_SCENE_EXTERIOR', trinity.TriStepUpdate(scene))
            self.AddStep('VISIBILITY_QUERY_EXTERIOR', trinity.TriStepVisibilityQuery(scene, trinity.Tr2VisibilityResults()))
            self.AddStep('BEGIN_MANAGED_RENDERING_EXTERIOR', trinity.TriStepRenderPrePass(scene, trinity.TRIPREPASS_BEGIN_RENDER))
            self.AddStep('RENDER_PREPASS_EXTERIOR', trinity.TriStepRenderPrePass(scene, trinity.TRIPREPASS_PRE_PASS))
            self.AddStep('RENDER_LIGHTS_EXTERIOR', trinity.TriStepRenderPrePass(scene, trinity.TRIPREPASS_LIGHT_PASS))
            self.AddStep('RENDER_GATHER_EXTERIOR', trinity.TriStepRenderPrePass(scene, trinity.TRIPREPASS_GATHER_PASS))
            self.AddStep('END_MANAGED_RENDERING_EXTERIOR', trinity.TriStepRenderPrePass(scene, trinity.TRIPREPASS_END_RENDER))
        else:
            self.RemoveStep('DISABLE_CUBEMAP')
            self.RemoveStep('ENABLE_CUBEMAP')
            self.RemoveStep('UPDATE_SCENE_EXTERIOR')
            self.RemoveStep('VISIBILITY_QUERY_EXTERIOR')
            self.RemoveStep('BEGIN_MANAGED_RENDERING_EXTERIOR')
            self.RemoveStep('RENDER_PREPASS_EXTERIOR')
            self.RemoveStep('RENDER_LIGHTS_EXTERIOR')
            self.RemoveStep('RENDER_GATHER_EXTERIOR')
            self.RemoveStep('END_MANAGED_RENDERING_EXTERIOR')



    def _CreateBasicRenderSteps(self):
        self.AddStep('SET_PREPASS_RT', trinity.TriStepSetRenderTarget())
        self.AddStep('CLEAR_PREPASS', trinity.TriStepClear((0, 0, 0, 0), 1.0, 0))
        self.AddStep('SET_LIGHT_RT', trinity.TriStepSetRenderTarget())
        self.AddStep('CLEAR_LIGHTS', trinity.TriStepClear((0, 0, 0, 0), None, None))
        self.AddStep('SET_FINAL_RT', trinity.TriStepSetRenderTarget())
        self.AddStep('CLEAR_FINAL_RT', trinity.TriStepClear((0, 0, 0, 0), None, None))
        if self.scene and self.scene.object:
            interiorScene = self.scene.object
        else:
            interiorScene = None
        if self.exteriorScene and self.exteriorScene.object:
            exteriorScene = self.exteriorScene.object
        else:
            exteriorScene = None
        if interiorScene:
            self.AddStep('UPDATE_SCENE', trinity.TriStepUpdate(self.GetScene()))
            result = trinity.Tr2VisibilityResults()
            self.AddStep('VISIBILITY_QUERY', trinity.TriStepVisibilityQuery(self.GetScene(), result))
            self.AddStep('SET_VISIBILITY_RESULT', trinity.TriStepSetVisibilityResults(self.GetScene(), result))
            self.AddStep('BEGIN_MANAGED_RENDERING', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_BEGIN_RENDER))
            self.AddStep('RENDER_PREPASS', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_PRE_PASS))
            self.AddStep('RENDER_LIGHTS', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_LIGHT_PASS))
            self.AddStep('RENDER_GATHER', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_GATHER_PASS))
            self.AddStep('END_MANAGED_RENDERING', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_END_RENDER))
            self.AddStep('RENDER_FLARES', trinity.TriStepRenderPrePass(self.GetScene(), trinity.TRIPREPASS_FLARE_PASS))
        if exteriorScene:
            if interiorScene:
                try:
                    self.AddStep('DISABLE_CUBEMAP', trinity.TriStepToggleCubemap(False, self.scene))
                    self.AddStep('ENABLE_CUBEMAP', trinity.TriStepToggleCubemap(True, self.scene))
                except TypeError:
                    pass
            self.AddStep('UPDATE_SCENE_EXTERIOR', trinity.TriStepUpdate(exteriorScene))
            self.AddStep('VISIBILITY_QUERY_EXTERIOR', trinity.TriStepVisibilityQuery(exteriorScene, trinity.Tr2VisibilityResults()))
            self.AddStep('BEGIN_MANAGED_RENDERING_EXTERIOR', trinity.TriStepRenderPrePass(exteriorScene, trinity.TRIPREPASS_BEGIN_RENDER))
            self.AddStep('RENDER_PREPASS_EXTERIOR', trinity.TriStepRenderPrePass(exteriorScene, trinity.TRIPREPASS_PRE_PASS))
            self.AddStep('RENDER_LIGHTS_EXTERIOR', trinity.TriStepRenderPrePass(exteriorScene, trinity.TRIPREPASS_LIGHT_PASS))
            self.AddStep('RENDER_GATHER_EXTERIOR', trinity.TriStepRenderPrePass(exteriorScene, trinity.TRIPREPASS_GATHER_PASS))
            self.AddStep('END_MANAGED_RENDERING_EXTERIOR', trinity.TriStepRenderPrePass(exteriorScene, trinity.TRIPREPASS_END_RENDER))



    def SetClearColor(self, color):
        step = self.GetStep('CLEAR_BACKGROUND_RT')
        if step is not None:
            step.color = color




