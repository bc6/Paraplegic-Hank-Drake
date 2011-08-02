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
import const
from math import asin, atan2
SCENE_TYPE_CHARACTER_CREATION = 0
SCENE_TYPE_INTERIOR = 1
SCENE_TYPE_SPACE = 2
WORMHOLE_SCENES = ['res:/Scene/Askur/askur.red',
 'res:/dx9/Scene/Wormholes/wormhole_class_01.red',
 'res:/dx9/Scene/Wormholes/wormhole_class_02.red',
 'res:/dx9/Scene/Wormholes/wormhole_class_03.red',
 'res:/dx9/Scene/Wormholes/wormhole_class_04.red',
 'res:/dx9/Scene/Wormholes/wormhole_class_05.red',
 'res:/dx9/Scene/Wormholes/wormhole_class_06.red']
KNOWN_SCENES = ['res:/Scene/Askur/askur.red',
 'res:/dx9/scene/Universe/a01_cube.red',
 'res:/dx9/scene/Universe/a02_cube.red',
 'res:/dx9/scene/Universe/a03_cube.red',
 'res:/dx9/scene/Universe/a04_cube.red',
 'res:/dx9/scene/Universe/a05_cube.red',
 'res:/dx9/scene/Universe/a06_cube.red',
 'res:/dx9/scene/Universe/a07_cube.red',
 'res:/dx9/scene/Universe/a08_cube.red',
 'res:/dx9/scene/Universe/a09_cube.red',
 'res:/dx9/scene/Universe/a10_cube.red',
 'res:/dx9/scene/Universe/c01_cube.red',
 'res:/dx9/scene/Universe/c02_cube.red',
 'res:/dx9/scene/Universe/c03_cube.red',
 'res:/dx9/scene/Universe/c04_cube.red',
 'res:/dx9/scene/Universe/c05_cube.red',
 'res:/dx9/scene/Universe/c06_cube.red',
 'res:/dx9/scene/Universe/c07_cube.red',
 'res:/dx9/scene/Universe/c08_cube.red',
 'res:/dx9/scene/Universe/c09_cube.red',
 'res:/dx9/scene/Universe/c10_cube.red',
 'res:/dx9/scene/Universe/c11_cube.red',
 'res:/dx9/scene/Universe/c12_cube.red',
 'res:/dx9/scene/Universe/g01_cube.red',
 'res:/dx9/scene/Universe/g02_cube.red',
 'res:/dx9/scene/Universe/g03_cube.red',
 'res:/dx9/scene/Universe/g04_cube.red',
 'res:/dx9/scene/Universe/g05_cube.red',
 'res:/dx9/scene/Universe/g06_cube.red',
 'res:/dx9/scene/Universe/g07_cube.red',
 'res:/dx9/scene/Universe/g08_cube.red',
 'res:/dx9/scene/Universe/g09_cube.red',
 'res:/dx9/scene/Universe/g10_cube.red',
 'res:/dx9/scene/Universe/g11_cube.red',
 'res:/dx9/scene/Universe/j01_cube.red',
 'res:/dx9/scene/Universe/j02_cube.red',
 'res:/dx9/scene/Universe/m01_cube.red',
 'res:/dx9/scene/Universe/m02_cube.red',
 'res:/dx9/scene/Universe/m03_cube.red',
 'res:/dx9/scene/Universe/m04_cube.red',
 'res:/dx9/scene/Universe/m05_cube.red',
 'res:/dx9/scene/Universe/m06_cube.red',
 'res:/dx9/scene/Universe/m07_cube.red',
 'res:/dx9/scene/Universe/m08_cube.red',
 'res:/dx9/scene/Universe/m09_cube.red',
 'res:/dx9/scene/Universe/m10_cube.red',
 'res:/dx9/scene/Universe/m11_cube.red',
 'res:/dx9/scene/Universe/s01_cube.red',
 'res:/dx9/scene/Universe/s02_cube.red',
 'res:/dx9/scene/Universe/s03_cube.red']

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
     'GetIncarnaRenderJob': []}
    __startupdependencies__ = ['settings', 'device']
    __notifyevents__ = ['OnGraphicSettingsChanged']

    def __init__(self):
        service.Service.__init__(self)
        self.ProcessImportsAndCreateScenes()
        self.renderLoopJob = None
        self.secondaryRenderJob = None
        self.secondarySceneContext = None
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
        self.sceneType = None
        trinity.device.RegisterResource(self)
        self.interiorRenderJobCreated = False



    def ProcessImportsAndCreateScenes(self):
        from trinity.sceneRenderJobSpace import CreateSceneRenderJobSpace
        from trinity.eveSceneRenderJobInterior import CreateEveSceneRenderJobInterior
        self.fisRenderJob = CreateSceneRenderJobSpace()
        self.incarnaRenderJob = CreateEveSceneRenderJobInterior()
        self.incarnaRenderJob.CreateBasicRenderSteps()



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
        rj.Clear((0.0, 0.0, 0.0, 0.0), 1.0)
        rj.SetProjection(self.projection)
        rj.SetView(self.view)
        paperDoll.SkinSpotLightShadows.CreateShadowStep(rj)
        paperDoll.SkinLightmapRenderer.CreateScatterStep(rj, self.scene2)
        if self.showUIBackdropScene:
            self.renderUIBackdropScene = rj.RenderScene(self.uiBackdropScene)
            self.renderUIBackdropScene.name = 'Render BackdropScene'
        self.renderInteriorSceneStep = rj.RenderScene(self.scene2)
        self.renderInteriorSceneStep.name = 'Render Interiors'
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
            backgroundView = trinity.TriView()
            backgroundProjection = trinity.TriProjection()
            backGroundCameraUpdateFunction = self.incarnaRenderJob.GetBackgroundCameraUpdateFunction(backgroundView, backgroundProjection, 10.0, 40000.0, sceneTranslation, sceneRotation)
            self.incarnaRenderJob.SetBackgroundCameraViewAndProjection(backgroundView, backgroundProjection, backGroundCameraUpdateFunction)



    def SetSceneType(self, sceneType):
        if self.sceneType == sceneType:
            self.CreateJob()
            return 
        hasOverlay = sm.GetService('gameui').HasActiveOverlay()
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
        elif sceneType == SCENE_TYPE_CHARACTER_CREATION:
            log.LogInfo('Setting up character creation scene rendering')
            self.incarnaRenderJob.Disable()
            self.fisRenderJob.Disable()
            self.ApplyClothSimulationSettings()
        elif sceneType == SCENE_TYPE_SPACE:
            log.LogInfo('Setting up space scene rendering')
            self.incarnaBackgroundScene = None
            self.incarnaRenderJob.Disable()
            self.incarnaRenderJob.SetScene(None)
            self.incarnaRenderJob.SetBackgroundScene(None)
            self.fisRenderJob.Enable()
            self.fisRenderJob.UseFXAA(False)
            if self.secondarySceneContext is not None:
                scene1 = self.secondarySceneContext.scene1
                scene2 = self.secondarySceneContext.scene2
                key = self.secondarySceneContext.sceneKey
                camera = self.secondarySceneContext.camera
                self.secondarySceneContext = None
                self.secondaryRenderJob = None
                self.SetActiveScenes(scene1, scene2, key)
                self.SetActiveCamera(camera)
        self.CreateJob()



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



    def GetSceneFromIndex(self, idx):
        try:
            if idx < 0:
                scene = WORMHOLE_SCENES[(-idx)]
            else:
                scene = KNOWN_SCENES[idx]
        except:
            log.LogException()
            scene = KNOWN_SCENES[0]
        return scene



    def GetScene(self, location = None):
        if location is None:
            location = (eve.session.solarsystemid2, eve.session.constellationid, eve.session.regionid)
        idx = cfg.GetLocationSceneIndex(*location)
        scene = self.GetSceneFromIndex(idx)
        return scene



    def DeriveTextureFromSceneName(self, scenePath):
        texturePath = ''
        if 'wormhole' in scenePath.lower():
            texturePath = '%s_cube.dds' % scenePath.split('.')[0]
        else:
            lst = scenePath.split('/')
            name = lst[-1].split('.')[0]
            texturePath = 'res:/dx9/scene/universe/%s.dds' % name
        return texturePath



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




    def PrepareScene(self, scene, inflight = 0):
        if inflight:
            scene.nebula.children[0].object.areas[0].shader = eve.rot.GetInstance(self.GetNebulaShaderPath())
            scene.fogStart = -500.0
            scene.fogEnd = 25000.0
            scene.fogEnable = 1
            scene.fogColor.SetRGB(0.0, 0.0, 0.0)
            scene.fogTableMode = trinity.TRIFOG_LINEAR
        if getattr(scene, 'dustfield', None) is not None:
            scene.dustfield = None
        planets = []
        for celestial in scene.models:
            b = getattr(celestial, 'translationCurve', None)
            if b and b.__guid__ == 'spaceObject.Planet':
                planets.append(b)

        if len(planets) < 3:
            return 
        A = planets[0].GetVectorAt(blue.os.GetTime(1))
        B = planets[1].GetVectorAt(blue.os.GetTime(1))
        C = planets[2].GetVectorAt(blue.os.GetTime(1))
        A.Scale(1e-07)
        B.Scale(1e-07)
        C.Scale(1e-07)
        VA = A - B
        VB = C - B
        up = trinity.TriVector(0.0, 1.0, 0.0)
        normal = trinity.TriVector()
        normal.SetCrossProduct(VA, VB)
        normal.Normalize()
        rotation = trinity.TriQuaternion()
        rotation.SetRotationArc(normal, up)
        if not len(scene.nebula.children):
            return 
        nebula = scene.nebula.children[0]
        nebula.scaling.z = 1.0
        nebula.object.areas[0].areaTextures[0].rotation = rotation



    def CreateScene2FromScene(self, s1):
        s1.Update(0L)
        s2 = trinity.EveSpaceScene()
        textures = s1.nebula.children[0].object.areas[0].areaTextures
        s2.envMap1ResPath = textures[0].pixels.encode('ascii')
        if len(textures) > 1:
            s2.envMap2ResPath = textures[1].pixels.encode('ascii')
        rot1 = textures[0].rotation
        s2.envMapRotation = (rot1.x,
         rot1.y,
         rot1.z,
         rot1.w)
        scale1 = textures[0].scaling
        s2.envMapScaling = (scale1.x, scale1.y, scale1.z)
        diff1 = s1.sunDiffuseForShaders
        s2.sunDiffuseColor = (diff1.x, diff1.y, diff1.z)
        dir1 = s1.sunLight.direction
        s2.sunDirection = (dir1.x, dir1.y, dir1.z)
        amb1 = s1.ambientLight
        s2.ambientColor = (amb1.r, amb1.g, amb1.b)
        fog1 = s1.fogColor
        s2.fogColor = (fog1.r, fog1.g, fog1.b)
        s2.fogStart = s1.rangeFogStart
        s2.fogEnd = s1.rangeFogEnd
        s2.fogMax = 0.0
        return s2



    def PrepareBackgroundLandscapes(self, scene, scene2):
        starSeed = 0
        securityStatus = 1
        if eve.session.stationid is not None:
            return 
        if scene is None or scene2 is None:
            return 
        if bool(eve.session.solarsystemid2):
            starSeed = int(eve.session.constellationid)
            securityStatus = sm.StartService('map').GetSecurityStatus(eve.session.solarsystemid)
        scene2.starfield = trinity.Load('res:/dx9/scene/starfield/spritestars.red')
        if scene2.starfield is not None:
            scene2.starfield.seed = starSeed
            scene2.starfield.maxDist = 200
            if util.IsWormholeSystem(eve.session.solarsystemid):
                scene2.starfield.numStars = 0
            else:
                scene2.starfield.numStars = 250 + int(500 * securityStatus)
        scene2.backgroundEffect = trinity.Load('res:/dx9/scene/starfield/starfieldNebula.red')
        if scene2.backgroundEffect is not None:
            node = nodemanager.FindNode(scene2.backgroundEffect.resources, 'NebulaMap', 'trinity.TriTexture2DParameter')
            if node is not None:
                node.resourcePath = scene2.envMap1ResPath
        if scene2.starfield is None or scene2.backgroundEffect is None:
            return 
        scene.nebula.display = False
        scene.pointStarfield.display = False
        scene2.backgroundRenderingEnabled = True



    def SetupSceneForRendering(self, scene1, scene2, key = None):
        trinity.device.scene = None
        self.SetActiveScenes(scene1, scene2, key)



    def GetIncarnaRenderJob(self):
        return self.incarnaRenderJob



    def LoadScene(self, scenefile, sceneName = '', fov = None, leaveUntouched = 0, inflight = 0, registerKey = None):
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
                if sceneFromFile.__bluetype__ == 'trinity.TriScene':
                    scene = sceneFromFile
                    camera = scene.camera
                    scene.camera = None
                    scene2 = self.CreateScene2FromScene(scene)
                else:
                    scene = trinity.TriScene()
                    camera = trinity.EveCamera()
                    scene2 = sceneFromFile
                if inflight:
                    if scene2.dustfield is None:
                        scene2.dustfield = trinity.Load('res:/dx9/scene/dustfield.red')
                    scene2.dustfield.camera = camera
                    scene2.dustfield.ballpark = sm.GetService('michelle').GetBallpark()
                if leaveUntouched:
                    self.SetupSceneForRendering(scene, scene2, registerKey)
                    return scene
                self.PrepareCamera(camera)
                self.PrepareScene(scene, inflight)
                self.PrepareBackgroundLandscapes(scene, scene2)
                if fov:
                    camera.fieldOfView = fov
                if registerKey:
                    self.RegisterCamera(registerKey, camera)
                    self.RegisterScenes(registerKey, scene, scene2)
                    if self.scene2 is None or self.scene2 not in self.registeredScenes2.values():
                        self.SetupSceneForRendering(scene, scene2, registerKey)
                        self.SetCamera(camera)
                else:
                    self.SetupSceneForRendering(scene, scene2, registerKey)
                    self.SetCamera(camera)
                bp = sm.GetService('michelle').GetBallparkForScene(scene)
                if bp is not None:
                    scene.ballpark = bp
                else:
                    scene.ballpark = None
                camera.audio2Listener = audio2.GetListener(0)
                if bp is not None:
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

