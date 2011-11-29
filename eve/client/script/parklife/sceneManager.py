from __future__ import with_statement
import blue
import util
import log
import trinity
import audio2
import service
import nodemanager
import locks
import paperDoll
import geo2
import sys
from math import asin, atan2
SCENE_TYPE_CHARACTER_CREATION = 0
SCENE_TYPE_INTERIOR = 1
SCENE_TYPE_SPACE = 2

class SceneContext():

    def __init__(self, scene1 = None, scene2 = None, camera = None, sceneKey = 'default', sceneType = None):
        self.scene1 = scene1
        self.scene2 = scene2
        self.camera = camera
        self.sceneKey = sceneKey
        self.sceneType = sceneType




class SceneManager(service.Service):
    __guid__ = 'svc.sceneManager'
    __exportedcalls__ = {'LoadScene': [],
     'GetScene': [],
     'GetIncarnaRenderJob': [],
     'EnableIncarnaRendering': []}
    __startupdependencies__ = ['settings', 'device']
    __notifyevents__ = ['OnGraphicSettingsChanged', 'OnSessionChanged']

    def __init__(self):
        service.Service.__init__(self)
        self.ProcessImportsAndCreateScenes()
        self.renderLoopJob = None
        self.secondaryRenderJob = None
        self.secondarySceneContext = None
        self.loadingClearJob = trinity.CreateRenderJob()
        self.loadingClearJob.name = 'loadingClear'
        self.loadingClearJob.Clear((0, 0, 0, 1))
        self.loadingClearJob.enabled = False
        self.scene1 = None
        self.scene2 = None
        self.activeSceneKey = None
        self.incarnaBackgroundScene = None
        self.incarnaBackgroundTranslation = None
        self.incarnaBackgroundRotation = None
        self.viewport = None
        self.view = trinity.TriView()
        self.view.SetLookAtPosition((0, 2, -2), (0, 3, 0), (0, 1, 0))
        self.projection = trinity.TriProjection()
        self.projection.PerspectiveFov(1, trinity.device.viewport.GetAspectRatio(), 1, 3000)
        self.showUIBackdropScene = False
        self.uiBackdropScene = None
        self.ui = None
        self.camera = None
        self.charCreationCamera = None
        self.sceneType = None
        if '/skiprun' not in blue.pyos.GetArg():
            self._EnableLoadingClear()
        trinity.device.RegisterResource(self)
        self.interiorRenderJobCreated = False



    def ProcessImportsAndCreateScenes(self):
        from trinity.sceneRenderJobSpace import CreateSceneRenderJobSpace
        from trinity.eveSceneRenderJobInterior import CreateEveSceneRenderJobInterior
        self.fisRenderJob = CreateSceneRenderJobSpace()
        self.incarnaRenderJob = CreateEveSceneRenderJobInterior()
        self.incarnaRenderJob.CreateBasicRenderSteps()



    def _EnableLoadingClear(self):
        if not self.loadingClearJob.enabled:
            self.loadingClearJob.enabled = True
            trinity.device.scheduledRecurring.insert(0, self.loadingClearJob)



    def _DisableLoadingClear(self):
        if self.loadingClearJob.enabled:
            self.loadingClearJob.enabled = False
            trinity.device.scheduledRecurring.remove(self.loadingClearJob)



    def EnableIncarnaRendering(self):
        self._DisableLoadingClear()
        if self.secondaryRenderJob is None:
            self.incarnaRenderJob.Enable()



    def OnInvalidate(self, level):
        if self.renderLoopJob is not None:
            del self.renderLoopJob.steps[:]



    def OnCreate(self, device):
        if self.sceneType == SCENE_TYPE_CHARACTER_CREATION:
            self.CreateJobCharCreation()



    def CreateJob(self):
        if self.secondarySceneContext is not None:
            if self.secondarySceneContext.sceneType == SCENE_TYPE_SPACE:
                self.CreateJobFiS(self.secondarySceneContext)
        elif self.sceneType == SCENE_TYPE_CHARACTER_CREATION:
            self.CreateJobCharCreation()
        elif self.sceneType == SCENE_TYPE_INTERIOR:
            self.CreateJobInterior()
        elif self.sceneType == SCENE_TYPE_SPACE:
            self.CreateJobFiS()



    def RefreshJob(self, camera):
        if self.sceneType == SCENE_TYPE_INTERIOR:
            self.incarnaRenderJob.SetActiveCamera(camera)



    def CreateJobCharCreation(self):
        schedule = False
        if self.renderLoopJob is None:
            rj = trinity.CreateRenderJob('Scene Render Job')
            self.renderLoopJob = rj
            schedule = True
        else:
            rj = self.renderLoopJob
            del self.renderLoopJob.steps[:]
        self.updateScene1 = None
        self.updateScene2 = rj.Update(self.scene2)
        self.updateScene2.name = 'Update Scene2'
        self.updateUI = rj.Update(self.ui)
        self.updateUI.name = 'Update UI'
        if self.showUIBackdropScene:
            self.updateUiBackdropScene = rj.Update(self.uiBackdropScene)
            self.updateUiBackdropScene.name = 'Update BackdropScene'
        self.cameraUpdateStep = rj.RunJob()
        self.cameraUpdateStep.name = 'Update Camera'
        self.cameraUpdateStep.job = self.charCreationCamera
        rj.Clear((0.0, 0.0, 0.0, 0.0), 1.0)
        rj.SetProjection(self.projection)
        rj.SetView(self.view)
        paperDoll.SkinSpotLightShadows.CreateShadowStep(rj)
        paperDoll.SkinLightmapRenderer.CreateScatterStep(rj, self.scene2)
        if self.showUIBackdropScene:
            renderUIBackdropScene = rj.RenderScene(self.uiBackdropScene)
            renderUIBackdropScene.name = 'Render BackdropScene'
        renderInteriorSceneStep = rj.RenderScene(self.scene2)
        renderInteriorSceneStep.name = 'Render Interiors'
        paperDoll.AvatarGhost.CreateSculptingStep(rj)
        if schedule:
            trinity.device.scheduledRecurring.insert(0, rj)



    def AddPostProcess(self, idx, path, sceneKey = None):
        if self.fisRenderJob is not None:
            self.fisRenderJob.AddPostProcess(idx, path, sceneKey)



    def RemovePostProcess(self, idx):
        if self.fisRenderJob is not None:
            self.fisRenderJob.RemovePostProcess(idx)



    def SetPostProcessVariable(self, idx, variable, value):
        if self.fisRenderJob is not None:
            self.fisRenderJob.SetPostProcessVariable(idx, variable, value)



    def CreateJobFiS(self, sceneContext = None):
        if sceneContext is None:
            scene1 = self.scene1
            scene2 = self.scene2
            camera = self.camera
        else:
            scene1 = sceneContext.scene1
            scene2 = sceneContext.scene2
            camera = sceneContext.camera
            self.secondaryRenderJob = self.fisRenderJob
        rj = self.fisRenderJob
        rj.CreateBasicRenderSteps()
        rj.SetActiveCamera(camera)
        rj.SetScene(scene2)
        rj.SetScene1(scene1)
        rj.EnablePostProcessing(True)
        rj.EnablePostRenderCallbacks(True)
        rj.SetUI(self.ui)
        try:
            rj.DoPrepareResources()
        except trinity.D3DError:
            pass
        rj.Start()
        rj.SetSettingsBasedOnPerformancePreferences()



    def ApplyClothSimulationSettings(self):
        if 'character' not in sm.services:
            return 
        if self.sceneType == SCENE_TYPE_INTERIOR:
            clothSimulation = sm.GetService('device').GetAppFeatureState('Interior.clothSimulation', False)
            sm.GetService('character').EnableClothSimulation(clothSimulation)
        elif self.sceneType == SCENE_TYPE_CHARACTER_CREATION:
            clothSimulation = sm.GetService('device').GetAppFeatureState('CharacterCreation.clothSimulation', True)
            sm.GetService('character').EnableClothSimulation(clothSimulation)



    def OnGraphicSettingsChanged(self, changes):
        deviceSvc = sm.GetService('device')
        self.interiorGraphicsQuality = prefs.GetValue('interiorGraphicsQuality', deviceSvc.GetDefaultInteriorGraphicsQuality())
        self.shadowQuality = prefs.GetValue('shadowQuality', deviceSvc.GetDefaultShadowQuality())
        self.postProcessingQuality = prefs.GetValue('postProcessingQuality', deviceSvc.GetDefaultPostProcessingQuality())
        self.antiAliasingQuality = prefs.GetValue('antiAliasing', 0)
        self.incarnaRenderJob.SetSettingsBasedOnPerformancePreferences()
        self.fisRenderJob.SetSettingsBasedOnPerformancePreferences()
        if 'interiorGraphics' in changes:
            self.ApplyClothSimulationSettings()



    def GetIncarnaRenderJobVisualizationsMenu(self):
        return self.incarnaRenderJob.GetInsiderVisualizationMenu()



    def CreateJobInterior(self):
        activeCamera = sm.GetService('cameraClient').GetActiveCamera()
        rj = self.incarnaRenderJob
        rj.SetScene(self.scene2)
        rj.EnableSceneUpdate(True)
        rj.EnableVisibilityQuery(True)
        rj.SetUI(self.ui)
        self.SetupIncarnaBackground(self.incarnaBackgroundScene, self.incarnaBackgroundTranslation, self.incarnaBackgroundRotation)
        rj.SetActiveCamera(activeCamera)
        rj.SetSettingsBasedOnPerformancePreferences()



    def SetupIncarnaBackground(self, scene, sceneTranslation, sceneRotation):
        self.incarnaBackgroundScene = scene
        self.incarnaBackgroundTranslation = sceneTranslation
        self.incarnaBackgroundRotation = sceneRotation
        if scene is not None:
            self.incarnaRenderJob.SetBackgroundScene(scene)
            self.backgroundView = trinity.TriView()
            self.backgroundProjection = trinity.TriProjection()
            backGroundCameraUpdateFunction = self.incarnaRenderJob.GetBackgroundCameraUpdateFunction(self.backgroundView, self.backgroundProjection, 10.0, 40000.0, sceneTranslation, sceneRotation)
            self.incarnaRenderJob.SetBackgroundCameraViewAndProjection(self.backgroundView, self.backgroundProjection, backGroundCameraUpdateFunction)



    def OnSessionChanged(self, isremote, session, change):
        if 'locationid' in change:
            newLocationID = change['locationid'][1]
            if util.IsSolarSystem(newLocationID) and self.sceneType != SCENE_TYPE_SPACE:
                log.LogWarn('SceneManager: I detected a session change into space but no one has bothered to update my scene type!')
                self.SetSceneType(SCENE_TYPE_SPACE)



    def SetSceneType(self, sceneType):
        if self.sceneType == sceneType:
            if sceneType == SCENE_TYPE_INTERIOR:
                self._EnableLoadingClear()
            else:
                self.CreateJob()
            return 
        hasOverlay = sm.GetService('viewState').IsCurrentViewSecondary()
        self.sceneType = sceneType
        scene1 = self.scene1
        scene2 = self.scene2
        self.scene1 = None
        self.scene2 = None
        if self.renderLoopJob is not None:
            del self.renderLoopJob.steps[:]
            self.renderLoopJob.UnscheduleRecurring()
            self.renderLoopJob = None
        if sceneType == SCENE_TYPE_INTERIOR:
            log.LogInfo('Setting up WiS interior scene rendering')
            self.fisRenderJob.Disable()
            self.fisRenderJob.UseFXAA(True)
            self.ApplyClothSimulationSettings()
            if hasOverlay:
                self.SetActiveScenes(scene1, scene2, self.activeSceneKey)
                self.SetActiveCamera(self.camera)
            self._EnableLoadingClear()
        elif sceneType == SCENE_TYPE_CHARACTER_CREATION:
            log.LogInfo('Setting up character creation scene rendering')
            self.incarnaRenderJob.Disable()
            self.fisRenderJob.Disable()
            self.ApplyClothSimulationSettings()
            self._DisableLoadingClear()
        elif sceneType == SCENE_TYPE_SPACE:
            log.LogInfo('Setting up space scene rendering')
            self.incarnaBackgroundScene = None
            self.incarnaRenderJob.Disable()
            self.incarnaRenderJob.SetScene(None)
            self.incarnaRenderJob.SetBackgroundScene(None)
            self.fisRenderJob.Enable()
            self.fisRenderJob.UseFXAA(False)
            self._DisableLoadingClear()
            if self.secondarySceneContext is not None:
                scene1 = self.secondarySceneContext.scene1
                scene2 = self.secondarySceneContext.scene2
                key = self.secondarySceneContext.sceneKey
                camera = self.secondarySceneContext.camera
                self.secondarySceneContext = None
                self.secondaryRenderJob = None
                self.SetActiveScenes(scene1, scene2, key)
                self.SetActiveCamera(camera)



    def Initialize(self, scene1, scene2, ui):
        self.ui = ui
        self.uiBackdropScene = trinity.Tr2Sprite2dScene()
        self.uiBackdropScene.isFullscreen = True
        self.uiBackdropScene.backgroundColor = (0, 0, 0, 1)
        self.scene1 = scene1
        self.scene2 = scene2
        self.CreateJob()



    def SetActiveCamera(self, camera):
        if self.secondarySceneContext is None:
            self.camera = camera
        else:
            self.secondarySceneContext.camera = camera
        self.CreateJob()



    def SetSecondaryScene(self, scene1, scene2, sceneKey, sceneType):
        self.secondarySceneContext = SceneContext()
        self.secondarySceneContext.scene1 = scene1
        self.secondarySceneContext.scene2 = scene2
        self.secondarySceneContext.sceneKey = sceneKey
        self.secondarySceneContext.sceneType = sceneType
        self.CreateJob()
        self.secondaryRenderJob.Enable()



    def ClearSecondaryScene(self):
        self.secondarySceneContext = None
        if self.secondaryRenderJob is not None:
            self.secondaryRenderJob.Disable()
        self.secondaryRenderJob = None



    def SetActiveScenes(self, scene1, scene2, sceneKey = None):
        if getattr(scene2, '__bluetype__', None) == 'trinity.EveSpaceScene' and self.sceneType == SCENE_TYPE_INTERIOR:
            self.incarnaRenderJob.Pause()
            self.SetSecondaryScene(scene1, scene2, sceneKey, SCENE_TYPE_SPACE)
            return 
        self.activeSceneKey = sceneKey
        self.scene1 = scene1
        self.scene2 = scene2
        if self.fisRenderJob is not None and self.fisRenderJob.enabled and self.fisRenderJob != self.secondaryRenderJob:
            self.fisRenderJob.SetActiveScenes(scene1, scene2, sceneKey)
            return 
        self.CreateJob()



    def Run(self, ms):
        service.Service.Run(self, ms)
        self.registeredScenes = {}
        self.registeredScenes2 = {}
        self.registeredCameras = {}
        self.sceneLoadedEvents = {}
        self.maxFov = 1
        self.minFov = 0.05
        self.interiorGraphicsQuality = prefs.GetValue('interiorGraphicsQuality', self.device.GetDefaultInteriorGraphicsQuality())
        self.shadowQuality = prefs.GetValue('shadowQuality', self.device.GetDefaultShadowQuality())
        self.postProcessingQuality = prefs.GetValue('postProcessingQuality', self.device.GetDefaultPostProcessingQuality())
        self.antiAliasingQuality = prefs.GetValue('antiAliasing', 0)



    def SetCamera(self, camera):
        self.SetActiveCamera(camera)



    def GetRegisteredCamera(self, key, defaultOnActiveCamera = 0):
        if key in self.registeredCameras:
            return self.registeredCameras[key]
        if defaultOnActiveCamera:
            if self.secondarySceneContext is not None:
                return self.secondarySceneContext.camera
            return self.camera



    def UnregisterCamera(self, key):
        if key in self.registeredCameras:
            del self.registeredCameras[key]



    def RegisterCamera(self, key, camera):
        self.registeredCameras[key] = camera
        self.SetCameraOffset(camera)



    def SetCameraOffset(self, camera):
        camera.centerOffset = settings.user.ui.Get('cameraOffset', 0) * -0.0075



    def CheckCameraOffsets(self):
        for cam in self.registeredCameras.itervalues():
            self.SetCameraOffset(cam)




    def UnregisterScene(self, key):
        if key in self.registeredScenes:
            del self.registeredScenes[key]



    def RegisterScene(self, scene, key):
        self.registeredScenes[key] = scene



    def GetRegisteredScene(self, key, defaultOnActiveScene = 0):
        if key in self.registeredScenes:
            return self.registeredScenes[key]
        if key in self.sceneLoadedEvents and not self.sceneLoadedEvents[key].is_set():
            self.sceneLoadedEvents[key].wait()
            return self.registeredScenes[key]
        if defaultOnActiveScene:
            return self.scene1



    def UnregisterScene2(self, key):
        if key in self.registeredScenes2:
            del self.registeredScenes2[key]



    def RegisterScene2(self, scene, key):
        self.registeredScenes2[key] = scene



    def RegisterScenes(self, key, scene1, scene2):
        self.registeredScenes[key] = scene1
        self.registeredScenes2[key] = scene2



    def GetRegisteredScene2(self, key, defaultOnActiveScene = 0):
        if key in self.registeredScenes2:
            return self.registeredScenes2[key]
        if key in self.sceneLoadedEvents and not self.sceneLoadedEvents[key].is_set():
            self.sceneLoadedEvents[key].wait()
            return self.registeredScenes2[key]
        if defaultOnActiveScene:
            return self.scene2



    def SetRegisteredScenes(self, key):
        if key == 'default' and self.sceneType == SCENE_TYPE_INTERIOR:
            if self.incarnaRenderJob.enabled:
                self.incarnaRenderJob.Start()
            else:
                self.incarnaRenderJob.Enable()
            self.ClearSecondaryScene()
            self.SetActiveScenes(None, self.scene2)
            self.SetActiveCamera(self.camera)
            return 
        scene1 = self.registeredScenes.get(key, None)
        scene2 = self.registeredScenes2.get(key, None)
        camera = self.registeredCameras.get(key, None)
        self.SetupSceneForRendering(scene1, scene2, key)
        if camera:
            self.SetCamera(camera)



    def GetActiveScene1(self):
        return self.scene1



    def GetActiveScene2(self):
        return self.scene2



    def Get2DBackdropScene(self):
        return self.uiBackdropScene



    def Show2DBackdropScene(self, updateRenderJob = False):
        self.showUIBackdropScene = True
        if updateRenderJob:
            self.CreateJob()



    def Hide2DBackdropScene(self, updateRenderJob = False):
        self.showUIBackdropScene = False
        if updateRenderJob:
            self.CreateJob()



    def GetCurrentViewAndProjection(self):
        return (self.view, self.projection)



    def GetScene(self, location = None):
        if location is None:
            location = (eve.session.solarsystemid2, eve.session.constellationid, eve.session.regionid)
        resPath = cfg.GetNebula(*location)
        return resPath



    def DeriveTextureFromSceneName(self, scenePath):
        scene = trinity.Load(scenePath)
        if scene is None:
            return ''
        return scene.envMap1ResPath



    def PrepareCamera(self, camera):
        camera.fieldOfView = self.maxFov
        camera.yawMultiplier = 0.2
        camera.pitchMultiplier = 0.2
        camera.friction = 7.0
        camera.maxSpeed = 0.07
        camera.frontClip = 6.0
        camera.backClip = 10000000.0
        camera.exponent = 0.2
        camera.idleScale = 0.65
        for each in camera.zoomCurve.keys:
            each.value = self.maxFov




    def PrepareBackgroundLandscapes(self, scene):
        starSeed = 0
        securityStatus = 1
        if eve.session.stationid is not None:
            return 
        if scene is None:
            return 
        if bool(eve.session.solarsystemid2):
            starSeed = int(eve.session.constellationid)
            securityStatus = sm.StartService('map').GetSecurityStatus(eve.session.solarsystemid)
        scene.starfield = trinity.Load('res:/dx9/scene/starfield/spritestars.red')
        if scene.starfield is not None:
            scene.starfield.seed = starSeed
            scene.starfield.minDist = 40
            scene.starfield.maxDist = 80
            if util.IsWormholeSystem(eve.session.solarsystemid):
                scene.starfield.numStars = 0
            else:
                scene.starfield.numStars = 500 + int(250 * securityStatus)
        if scene.backgroundEffect is None:
            scene.backgroundEffect = trinity.Load('res:/dx9/scene/starfield/starfieldNebula.red')
            node = nodemanager.FindNode(scene.backgroundEffect.resources, 'NebulaMap', 'trinity.TriTexture2DParameter')
            if node is not None:
                node.resourcePath = scene.envMap1ResPath
        if scene.starfield is None or scene.backgroundEffect is None:
            return 
        scene.backgroundRenderingEnabled = True



    def SetupSceneForRendering(self, scene1, scene2, key = None):
        trinity.device.scene = None
        self.SetActiveScenes(scene1, scene2, key)



    def GetIncarnaRenderJob(self):
        return self.incarnaRenderJob



    def LoadScene(self, scenefile, sceneName = '', fov = None, leaveUntouched = 0, inflight = 0, registerKey = None, setupCamera = True):
        try:
            try:
                if registerKey:
                    self.sceneLoadedEvents[registerKey] = locks.Event(registerKey)
                if self.scene1 is not None:
                    self.scene1.ballpark = None
                sceneFromFile = trinity.Load(scenefile)
                if sceneFromFile is None:
                    return 
                else:
                    camera = None
                    scene = trinity.TriScene()
                    scene2 = sceneFromFile
                    if setupCamera:
                        camera = trinity.Load('res:/dx9/scene/camera.red')
                    if inflight:
                        if scene2.dustfield is None:
                            scene2.dustfield = trinity.Load('res:/dx9/scene/dustfield.red')
                        scene2.dustfield.camera = camera
                        scene2.dustfield.ballpark = sm.GetService('michelle').GetBallpark()
                        scene2.sunDiffuseColor = (1.5, 1.5, 1.5, 1.0)
                        if settings.user.ui.Get('effectsEnabled', 1) and session.solarsystemid is not None:
                            universe = getattr(self, 'universe', None)
                            if not universe:
                                universe = trinity.Load('res:/dx9/scene/starfield/universe.red')
                                setattr(self, 'universe', universe)
                            scene2.backgroundObjects.append(universe)
                            here = sm.GetService('map').GetItem(session.solarsystemid)
                            if here:
                                scale = 10000000000.0
                                position = (here.x / scale, here.y / scale, -here.z / scale)
                                universe.children[0].translation = position
                    if leaveUntouched:
                        self.SetupSceneForRendering(scene, scene2, registerKey)
                        return scene
                    if camera:
                        self.PrepareCamera(camera)
                        if fov:
                            camera.fieldOfView = fov
                    self.PrepareBackgroundLandscapes(scene2)
                    if registerKey:
                        self.RegisterCamera(registerKey, camera)
                        self.RegisterScenes(registerKey, scene, scene2)
                        if self.scene2 is None or self.scene2 not in self.registeredScenes2.values():
                            self.SetupSceneForRendering(scene, scene2, registerKey)
                            if camera:
                                self.SetCamera(camera)
                    else:
                        self.SetupSceneForRendering(scene, scene2, registerKey)
                        if camera:
                            self.SetCamera(camera)
                    bp = sm.GetService('michelle').GetBallparkForScene(scene)
                    if bp is not None:
                        scene.ballpark = bp
                    else:
                        scene.ballpark = None
                    if camera:
                        camera.audio2Listener = audio2.GetListener(0)
                    if camera and bp is not None:
                        myShipBall = bp.GetBallById(bp.ego)
                        vel = geo2.Vector(myShipBall.vx, myShipBall.vy, myShipBall.vz)
                        if geo2.Vec3Length(vel) > 0.0:
                            vel = geo2.Vec3Normalize(vel)
                            pitch = asin(-vel[1])
                            yaw = atan2(vel[0], vel[2])
                            yaw = yaw - 0.3
                            pitch = pitch - 0.15
                            camera.SetOrbit(yaw, pitch)
                    sm.ScatterEvent('OnLoadScene')
                    return scene
            except Exception:
                log.LogException('sceneManager::LoadScene')
                sys.exc_clear()

        finally:
            if registerKey and registerKey in self.sceneLoadedEvents:
                self.sceneLoadedEvents.pop(registerKey).set()




    def GetNebulaShaderPath(self):
        if sm.GetService('device').IsHdrEnabled() and bool(eve.session.solarsystemid2):
            return 'res:/UI/Shader/nebulaBloom.blue'
        else:
            return 'res:/UI/Shader/nebula.blue'



exports = {'sceneManager.SCENE_TYPE_SPACE': SCENE_TYPE_SPACE,
 'sceneManager.SCENE_TYPE_CHARACTER_CREATION': SCENE_TYPE_CHARACTER_CREATION,
 'sceneManager.SCENE_TYPE_INTERIOR': SCENE_TYPE_INTERIOR}

