import service
import uix
import uiconst
import trinity
import util
import spaceObject
import planet
import blue
import uthread
import log
import math
import uicls
import geo2
from planetCommon import PLANET_TEXTURE_SIZE, PLANET_ZOOM_MAX, PLANET_SCALE
from planetCommon import PLANET_RESOURCE_TEX_WIDTH, PLANET_RESOURCE_TEX_HEIGHT
from PlanetResources import builder
from pychartdir import XYChart, Transparent, NoValue
from planetUtil import MATH_2PI
SQRT_NUM_SAMPLES = 80
LINER_BLENDING_RATIO = 0.8
RESOURCE_BASE_COLOR = (1, 1, 1, 0.175)
AMBIENT_SOUNDS = {const.typePlanetEarthlike: util.KeyVal(start='wise:/terrestrial_play', stop='wise:/terrestrial_stop'),
 const.typePlanetGas: util.KeyVal(start='wise:/gas_play', stop='wise:/gas_stop'),
 const.typePlanetIce: util.KeyVal(start='wise:/ice_play', stop='wise:/ice_stop'),
 const.typePlanetLava: util.KeyVal(start='wise:/lava_play', stop='wise:/lava_stop'),
 const.typePlanetOcean: util.KeyVal(start='wise:/oceanic_play', stop='wise:/oceanic_stop'),
 const.typePlanetSandstorm: util.KeyVal(start='wise:/barren_play', stop='wise:/barren_stop'),
 const.typePlanetThunderstorm: util.KeyVal(start='wise:/storm_play', stop='wise:/storm_stop'),
 const.typePlanetPlasma: util.KeyVal(start='wise:/plasma_play', stop='wise:/plasma_stop'),
 const.typePlanetShattered: util.KeyVal(start='wise:/plasma_play', stop='wise:/plasma_stop')}

class ResourceRenderAbortedError(Exception):
    pass

class PlanetUISvc(service.Service):
    __guid__ = 'svc.planetUI'
    __notifyevents__ = ['OnGraphicSettingsChanged', 'OnSetDevice', 'OnSessionChanged']
    __exportedcalls__ = {}
    __servicename__ = 'planetUI'
    __displayname__ = 'Planet UI Client Service'
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.state = service.SERVICE_START_PENDING
        self.LogInfo('Starting Planet UI Client Svc')
        uicore.layer.planet.Flush()
        self.planetID = None
        self.format = trinity.TRIFMT_A8R8G8B8
        self.renderTarget = None
        self.offscreenSurface = None
        self.busy = 0
        self.isLoadingResource = False
        self.selectedResourceTypeID = None
        self.minimizedWindows = []
        self.planetAccessRequired = None
        self.currSphericalHarmonic = None
        self.spherePinsPendingLoad = []
        self.spherePinLoadThread = None
        self.planet = None
        self.curveLineDrawer = planet.ui.CurveLineDrawer()
        self.myPinManager = planet.ui.MyPinManager()
        self.otherPinManager = planet.ui.OtherPinManager()
        self.eventManager = planet.ui.EventManager()
        self.planetRoot = None
        self.trinityPlanet = None
        self.planetTransform = None
        self.resourceLayer = None
        self.pinTransform = None
        self.pinOthersTransform = None
        self.modeController = None
        self.scanController = None
        self.currentContainer = None
        self.planetNav = None
        self.planetUIContainer = uicls.Container(parent=uicore.layer.planet, name='planetUIContainer', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.state = service.SERVICE_RUNNING
        self.LogInfo('Planet UI Client Svc Started')



    def Stop(self, memStream = None):
        if trinity.device is None:
            return 
        self.LogInfo('service is stopping')
        self.renderTarget = None
        self.offscreenSurface = None
        if self.spherePinLoadThread:
            self.spherePinLoadThread.kill()
            self.spherePinLoadThread = None
        self.Reset()



    def Reset(self):
        self.LogInfo('PlanetUISvc Reset')
        self.minimizedWindows = []
        self.CleanScene()
        sm.ScatterEvent('OnPlanetUIReset')



    def CleanScene(self):
        self.LogInfo('CleanScene')
        self.CloseCurrentlyOpenContainer()
        self.planetUIContainer.Flush()
        if self.planetTransform is not None:
            del self.planetTransform.children[:]
        if self.planetRoot is not None:
            del self.planetRoot.children[:]
        self.planetTransform = None
        self.pinTransform = None
        self.pinOthersTransform = None
        if self.trinityPlanet is not None:
            self.trinityPlanet.model = None
            self.trinityPlanet = None
        self.planetRoot = None
        self.planetNav = None
        if self.scanController is not None:
            self.scanController.Close()
            self.scanController = None
        self.resourceLayer = None
        self.ClosePlanetModeContainer()
        self.isLoadingResource = False



    def MinimizeWindows(self):
        windowSvc = sm.GetService('window')
        lobby = windowSvc.GetWindow('lobby')
        if lobby and not lobby.destroyed and lobby.state != uiconst.UI_HIDDEN and not lobby.IsMinimized() and not lobby.IsCollapsed():
            windowSvc.MinimizeWindow(lobby, animate=False)
            self.minimizedWindows.append('lobby')



    def Open(self, planetID):
        if self.planetID == planetID and self.IsOpen():
            return 
        if self.IsOpen():
            if not self.Close(False):
                return 
        if planetID is None:
            raise RuntimeError('Must supply a valid planet ID.')
        if getattr(self, 'busy', 0):
            return 
        self.busy = 1
        if not self.IsOpen() or self.planetID != planetID:
            try:
                self._Open(planetID)
            except UserError as e:
                self.busy = 0
                if session.solarsystemid is not None:
                    sm.GetService('bracket').Show()
                raise 
        if session.stationid2:
            uicore.layer.charcontrol.CloseView()
        else:
            uicore.layer.shipui.Hide()
        self.busy = 0



    def _Open(self, planetID):
        mapSvc = sm.GetService('map')
        planetData = mapSvc.GetPlanetInfo(planetID)
        planetChanged = planetID != self.planetID
        oldPlanetID = self.planetID
        self.planetID = planetID
        self.typeID = planetData.typeID
        self.solarSystemID = planetData.solarSystemID
        try:
            self.InitUI(planetChanged)
        except:
            self.Stop()
            self.Run()
            raise 
        if session.solarsystemid is not None:
            sm.GetService('bracket').Hide()
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_general_opening_play')
        sm.ScatterEvent('OnPlanetViewChanged', planetID, oldPlanetID)
        try:
            self.planetNav.camera.Open()
        except AttributeError:
            pass
        sm.GetService('starmap').DecorateNeocom()
        sm.StartService('audio').SendUIEvent(unicode(AMBIENT_SOUNDS[self.typeID].start))
        self.planetAccessRequired = session.solarsystemid2 == self.solarSystemID or sm.GetService('planetSvc').IsPlanetColonizedByMe(planetID)



    def IsOpen(self):
        sceneManager = sm.GetService('sceneManager')
        planetScene = sceneManager.GetRegisteredScene2('planet')
        activeScene2 = sceneManager.GetActiveScene2()
        alternativeactiveScene2 = None
        if sceneManager.secondarySceneContext is not None:
            alternativeactiveScene2 = sceneManager.secondarySceneContext.scene2
        if planetScene is not None and (planetScene == activeScene2 or planetScene == alternativeactiveScene2):
            return True
        else:
            return False



    def Close(self, clearAll = True):
        if getattr(self, 'busy', 0):
            return True
        currentPlanet = self.GetCurrentPlanet()
        if currentPlanet and currentPlanet.IsInEditMode():
            if eve.Message('ExitPlanetModeWhileInEditMode', {}, uiconst.YESNO) != uiconst.ID_YES:
                return False
            currentPlanet.RevertChanges()
        self.busy = 1
        try:
            self.planetNav.camera.Close()
        except AttributeError:
            pass
        if hasattr(self, 'typeID'):
            sm.StartService('audio').SendUIEvent(unicode(AMBIENT_SOUNDS[self.typeID].stop))
        if self.IsOpen():
            if len(self.minimizedWindows) > 0:
                windowSvc = sm.GetService('window')
                for wndName in self.minimizedWindows:
                    wnd = windowSvc.GetWindow(wndName)
                    if wnd and wnd.IsMinimized():
                        wnd.Maximize()

                self.minimizedWindows = []
            if getattr(self, 'planetNav', None):
                settings.char.ui.Set('planet_camera_zoom', self.planetNav.zoom)
            else:
                settings.char.ui.Set('planet_camera_zoom', 1.0)
            sm.GetService('sceneManager').SetRegisteredScenes('default')
            if eve.session.stationid2:
                sm.GetService('gameui').OpenExclusive('charcontrol', 1)
                uix.GetWorldspaceNav()
                uicore.registry.SetFocus(uicore.GetLayer('charcontrol'))
            else:
                uix.GetInflightNav()
            sm.GetService('bracket').Show()
            uicore.layer.planet.state = uiconst.UI_HIDDEN
        sm.GetService('starmap').DecorateNeocom()
        self.busy = 0
        self.ClosePlanetModeContainer()
        self.myPinManager.OnPlanetViewClosed()
        self.otherPinManager.OnPlanetViewClosed()
        self.eventManager.OnPlanetViewClosed()
        self.CleanScene()
        self.StopSpherePinLoadThread()
        sm.ScatterEvent('OnPlanetViewChanged', None, self.planetID)
        if session.stationid:
            uicore.layer.charcontrol.Show()
        else:
            uicore.layer.shipui.Show()
        self.LogPlanetAccess()
        self.planetID = None
        self.planet = None
        self.selectedResourceTypeID = None
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_general_closing_play')
        if clearAll:
            self.renderTarget = None
            self.offscreenSurface = None
            self.cameraScene = None
            self.planetScene = None
            sm.GetService('sceneManager').UnregisterScene('planet')
            sm.GetService('sceneManager').UnregisterScene2('planet')
            sm.GetService('sceneManager').UnregisterCamera('planet')
        return True



    def InitUI(self, planetChanged):
        self.LogInfo('Initializing UI')
        self.StartLoadingBar('planet_ui_init', mls.UI_PI_PLANET_MODE, mls.UI_PI_LOADING_PLANET_RESOURCES, 5)
        try:
            sm.GetService('planetSvc').GetPlanet(self.planetID)
        except UserError as e:
            self.StopLoadingBar('planet_ui_init')
            raise 
        except Exception:
            eve.Message('PlanetLoadingFailed', {'planet': (LOCID, self.planetID)})
            self.StopLoadingBar('planet_ui_init')
            log.LogException()
            return 
        mapSvc = sm.GetService('map')
        if mapSvc.IsOpen():
            mapSvc.Close()
        if not self.IsOpen():
            self.MinimizeWindows()
        newScene = False
        if self.planetRoot is None or planetChanged:
            self.CreateScene()
            newScene = True
        self.UpdateLoadingBar('planet_ui_init', mls.UI_PI_PLANET_MODE, mls.UI_PI_LOADING_PLANET_RESOURCES, 1, 5)
        sm.GetService('sceneManager').SetRegisteredScenes('planet')
        uicore.layer.map.state = uiconst.UI_HIDDEN
        uicore.layer.systemmap.state = uiconst.UI_HIDDEN
        uicore.layer.planet.state = uiconst.UI_PICKCHILDREN
        self.UpdateLoadingBar('planet_ui_init', mls.UI_PI_PLANET_MODE, mls.UI_PI_LOADING_PLANET_RESOURCES, 2, 5)
        self.InitTrinityTransforms()
        self.InitUIContainers()
        self.InitLinesets()
        self.UpdateLoadingBar('planet_ui_init', mls.UI_PI_PLANET_MODE, mls.UI_PI_LOADING_PLANET_RESOURCES, 3, 5)
        if newScene:
            self.planetNav.zoom = 1.0
        else:
            self.planetNav.zoom = settings.char.ui.Get('planet_camera_zoom', 1.0)
        self.SetPlanet()
        self.zoom = sm.GetService('planetUI').planetNav.camera.zoom
        self.eventManager.OnPlanetViewOpened()
        self.myPinManager.OnPlanetViewOpened()
        self.otherPinManager.OnPlanetViewOpened()
        uthread.new(self.FocusCameraOnCommandCenter, 3.0)
        self.UpdateLoadingBar('planet_ui_init', mls.UI_PI_PLANET_MODE, mls.UI_PI_LOADING_PLANET_RESOURCES, 4, 5)
        self.ClosePlanetModeContainer()
        sm.GetService('neocom').SetXtraText()
        self.modeController = planet.ui.PlanetModeContainer(parent=uicore.layer.neocom.GetChild('neocomLeftside'), align=uiconst.TOTOP, pos=(0, 0, 0, 355))
        self.UpdateLoadingBar('planet_ui_init', mls.UI_PI_PLANET_MODE, mls.UI_PI_LOADING_PLANET_RESOURCES, 5, 5)
        self.StopLoadingBar('planet_ui_init')



    def ResetPlanetModeContainer(self):
        self.ClosePlanetModeContainer()
        self.modeController = planet.ui.PlanetModeContainer(parent=uicore.layer.neocom.GetChild('neocomLeftside'), align=uiconst.TOTOP, pos=(0, 0, 0, 355))



    def InitUIContainers(self):
        self.pinInfoParent = uicls.Container(parent=self.planetUIContainer, name='pinInfoParent', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.planetNav = uix.GetPlanetNav()



    def InitTrinityTransforms(self):
        self.pinTransform = trinity.EveTransform()
        self.pinTransform.name = 'myPins'
        self.pinOthersTransform = trinity.EveTransform()
        self.pinOthersTransform.name = 'othersPins'
        self.planetTransform.children.append(self.pinTransform)
        self.planetTransform.children.append(self.pinOthersTransform)



    def InitLinesets(self):
        self.curveLineDrawer.CreateLineSet('links', self.pinTransform, 'res:/UI/Texture/Planet/link.dds', scale=1.009)
        self.curveLineDrawer.CreateLineSet('linksExtraction', self.pinTransform, 'res:/UI/Texture/Planet/link.dds', scale=1.001)
        self.curveLineDrawer.CreateLineSet('rubberLink', self.pinTransform, 'res:/UI/Texture/Planet/link.dds', scale=1.0089)
        self.curveLineDrawer.CreateLineSet('otherLinks', self.pinOthersTransform, 'res:/UI/Texture/Planet/link.dds', scale=1.0049)



    def ClosePlanetModeContainer(self):
        if self.modeController is not None:
            self.modeController.Close()
            self.modeController = None
        sm.GetService('starmap').DecorateNeocom()



    def CreateRenderTarget(self):
        deviceSvc = sm.GetService('device')
        textureQuality = prefs.GetValue('textureQuality', deviceSvc.GetDefaultTextureQuality())
        self.maxSizeLimit = size = PLANET_TEXTURE_SIZE >> textureQuality
        rt = None
        while rt is None:
            try:
                rt = trinity.device.CreateRenderTarget(2 * size, size, self.format, trinity.TRIMULTISAMPLE_NONE, 0, 0)
            except trinity.D3DERR_OUTOFVIDEOMEMORY:
                if size < 2:
                    return 
                self.maxSizeLimit = size = size / 2
                rt = None
            except:
                return 

        self.LogInfo('CreateRenderTarget textureQuality', textureQuality, 'size', size, 'maxSizeLimit', self.maxSizeLimit)
        return rt



    def CreateOffscreenSurface(self):
        deviceSvc = sm.GetService('device')
        textureQuality = prefs.GetValue('textureQuality', deviceSvc.GetDefaultTextureQuality())
        size = PLANET_TEXTURE_SIZE >> textureQuality
        self.LogInfo('CreateOffscreenPlainSurface textureQuality', textureQuality, 'size', size)
        return trinity.device.CreateOffscreenPlainSurface(2 * size, size, self.format, trinity.TRIPOOL_SYSTEMMEM)



    def CreateScene(self):
        self.LogInfo('CreateScene')
        self.planetScene = self.GetPlanetScene()
        self.planetRoot = trinity.EveRootTransform()
        self.planetRoot.name = 'planetRoot'
        self.planetScene.objects.append(self.planetRoot)
        camera = trinity.EveCamera()
        cameraParent = trinity.TriTransform()
        cameraParent.name = 'cameraParent'
        camera.parent = cameraParent
        camera.translationFromParent.z = PLANET_ZOOM_MAX
        self.LoadPlanet()
        sm.GetService('sceneManager').RegisterCamera('planet', camera)
        sm.GetService('sceneManager').RegisterScenes('planet', None, self.planetScene)



    def GetScene(self):
        (regionID, constellationID, solarSystemID,) = sm.GetService('map').GetItem(self.solarSystemID, True).hierarchy
        scene = sm.GetService('sceneManager').GetScene(location=(solarSystemID, constellationID, regionID))
        return scene



    def GetPlanetScene(self):
        scenepath = self.GetScene()
        scene = trinity.Load(scenepath)
        scene2 = trinity.EveSpaceScene()
        textures = scene.nebula.children[0].object.areas[0].areaTextures
        scene2.envMap1ResPath = textures[0].pixels.encode('ascii')
        if len(textures) > 1:
            scene2.envMap2ResPath = textures[1].pixels.encode('ascii')
        rot1 = textures[0].rotation
        scene2.envMapRotation = (rot1.x,
         rot1.y,
         rot1.z,
         rot1.w)
        scale1 = textures[0].scaling
        scene2.envMapScaling = (scale1.x, scale1.y, scale1.z)
        scene2.backgroundEffect = trinity.Load('res:/dx9/scene/starfield/starfieldNebula.red')
        if scene2.backgroundEffect is not None:
            for node in scene2.backgroundEffect.resources.Find('trinity.TriTexture2DParameter'):
                if node.name == 'NebulaMap':
                    node.resourcePath = scene2.envMap1ResPath

        scene2.backgroundRenderingEnabled = True
        return scene2



    def LoadPlanet(self):
        self.LogInfo('LoadPlanet planet', self.planetID, 'type', self.typeID, 'system', self.solarSystemID)
        planet = spaceObject.Planet()
        planet.typeID = self.typeID
        planet.LoadPlanet(self.planetID, forPhotoService=True, rotate=False, hiTextures=True)
        self.trinityPlanet = planet
        if planet.model is None or planet.model.highDetail is None:
            return 
        planetTransform = trinity.EveTransform()
        planetTransform.name = 'planet'
        planetTransform.scaling = (PLANET_SCALE, PLANET_SCALE, PLANET_SCALE)
        planetTransform.children.append(planet.model.highDetail)
        self.PreProcessPlanet()
        scene = self.planetScene
        trinity.WaitForResourceLoads()
        for t in planet.model.highDetail.children:
            if t.mesh is not None:
                if len(t.mesh.transparentAreas) > 0:
                    t.sortValueMultiplier = 2.0

        scene.sunDirection = (0.0, 0.0, 1.0)
        scene.sunDiffuseColor = (1.0, 1.0, 1.0, 1.0)
        self.planetTransform = planetTransform
        self.planetRoot.children.append(self.planetTransform)



    def GetCurrentPlanet(self):
        if not self.planetID:
            return None
        return sm.GetService('planetSvc').GetPlanet(self.planetID)



    def PreProcessPlanet(self):
        if self.renderTarget is None:
            self.renderTarget = trinity.TriSurfaceManaged(self.CreateRenderTarget)
        if self.offscreenSurface is None:
            self.offscreenSurface = trinity.TriSurfaceManaged(self.CreateOffscreenSurface)
        self.trinityPlanet.DoPreProcessEffect(self.maxSizeLimit, self.format, self.renderTarget, self.offscreenSurface)



    def StartLoadingBar(self, key, tile, action, total):
        if getattr(self, 'loadingBarActive', None) is None:
            sm.GetService('loading').ProgressWnd(tile, action, 0, total)
            self.loadingBarActive = key



    def UpdateLoadingBar(self, key, tile, action, part, total):
        if getattr(self, 'loadingBarActive', None) == key:
            sm.GetService('loading').ProgressWnd(tile, action, part, total)



    def StopLoadingBar(self, key):
        if getattr(self, 'loadingBarActive', None) == key:
            sm.GetService('loading').StopCycle()
            self.loadingBarActive = None



    def OnSetDevice(self):
        if self.IsOpen():
            self.planetNav.camera.ManualZoom(0.0)



    def OnGraphicSettingsChanged(self, changes):
        if self.IsOpen() and self.trinityPlanet is not None and ('textureQuality' in changes or 'shaderQuality' in changes):
            self.PreProcessPlanet()
            if self.selectedResourceTypeID is not None:
                self.ShowResource(self.selectedResourceTypeID)



    def ShowResource(self, resourceTypeID):
        self.LogInfo('ShowResource', resourceTypeID)
        oldResourceTypeID = self.selectedResourceTypeID
        self.selectedResourceTypeID = resourceTypeID
        if resourceTypeID is None:
            if self.resourceLayer is not None:
                self.resourceLayer.display = False
            self.otherPinManager.HideOtherPlayersExtractors()
            if self.modeController is not None and hasattr(self.modeController, 'resourceControllerTab') and self.modeController.resourceControllerTab is not None:
                self.modeController.resourceControllerTab.ResourceSelected(resourceTypeID)
        elif not getattr(self, 'isLoadingResource', False):
            if self.modeController is not None and hasattr(self.modeController, 'resourceControllerTab') and self.modeController.resourceControllerTab is not None:
                self.modeController.resourceControllerTab.ResourceSelected(resourceTypeID)
            self.isLoadingResource = True
            uthread.new(self._ShowResource, resourceTypeID)
            self.modeController.resourceControllerTab.ResourceSelected(resourceTypeID)
        elif oldResourceTypeID != resourceTypeID:
            while self.isLoadingResource:
                blue.pyos.synchro.Sleep(50)

            if resourceTypeID == self.selectedResourceTypeID:
                self.ShowResource(resourceTypeID)



    def _ShowResource(self, resourceTypeID):
        self.LogInfo('_ShowResource', resourceTypeID)
        inRange = False
        try:
            try:
                (inRange, texture,) = self.GetResourceAndRender(resourceTypeID)
                if self.planetTransform is not None:
                    self.EnableResourceLayer()
                    self.SetResourceTexture(texture)
            except ResourceRenderAbortedError as e:
                pass

        finally:
            self.isLoadingResource = False
            if self.modeController is not None and hasattr(self.modeController, 'resourceControllerTab') and self.modeController.resourceControllerTab is not None:
                self.modeController.resourceControllerTab.StopLoadingResources(resourceTypeID)
            if self.otherPinManager is not None and inRange:
                self.otherPinManager.RenderOtherPlayersExtractors(resourceTypeID)




    def EnableResourceLayer(self):
        if self.planetTransform is not None:
            if self.resourceLayer is None:
                self.LogInfo('_ShowResource no resourceLayer found. Loading resource layer')
                self.resourceLayer = trinity.Load('res:/dx9/model/worldobject/planet/uiplanet.red')
                trinity.WaitForResourceLoads()
                effect = self.resourceLayer.mesh.transparentAreas[0].effect
                for resource in effect.resources:
                    if resource.name == 'ColorRampMap':
                        resource.resourcePath = 'res:/dx9/model/worldobject/planet/resource_colorramp.dds'

                for param in effect.parameters:
                    if param.name == 'MainColor':
                        param.value = RESOURCE_BASE_COLOR
                    elif param.name == 'ResourceTextureInfo':
                        param.value = (PLANET_RESOURCE_TEX_WIDTH,
                         PLANET_RESOURCE_TEX_HEIGHT,
                         0,
                         0)

                offset = trinity.TriFloatParameter()
                offset.name = 'HeatOffset'
                offset.value = 0.0
                effect.parameters.append(offset)
                stretch = trinity.TriFloatParameter()
                stretch.name = 'HeatStretch'
                stretch.value = 1.0
                effect.parameters.append(stretch)
                self.planetTransform.children.append(self.resourceLayer)
            else:
                self.resourceLayer.display = True
            (low, hi,) = settings.char.ui.Get('planet_resource_display_range', (0.0, 1.0))
            self.SetResourceDisplayRange(low, hi)



    def GetResourceTexture(self):
        effect = self.resourceLayer.mesh.transparentAreas[0].effect
        for resource in effect.resources:
            if resource.name == 'ResourceDistMap':
                return resource




    def GetResourceAndRender(self, resourceTypeID):
        self.LogInfo('GetResourceAndRender resourceTypeID', resourceTypeID)
        planet = sm.GetService('planetSvc').GetPlanet(self.planetID)
        (inRange, sh,) = planet.GetResourceData(resourceTypeID)
        self.currSphericalHarmonic = sh
        sh = builder.CopySH(sh)
        builder.ScaleSH(sh, 1.0 / const.planetResourceMaxValue)
        chart = self.ChartResourceLayer(sh)
        buf = chart.makeChart2(chart.PNG)
        if resourceTypeID != self.selectedResourceTypeID:
            raise ResourceRenderAbortedError
        texture = trinity.device.CreateTexture(PLANET_RESOURCE_TEX_WIDTH, PLANET_RESOURCE_TEX_HEIGHT, 1, 0, trinity.TRIFMT_X8R8G8B8, trinity.TRIPOOL_MANAGED)
        if resourceTypeID != self.selectedResourceTypeID:
            raise ResourceRenderAbortedError
        texture.GetSurfaceLevel(0).LoadSurfaceFromFileInMemory(buf)
        if resourceTypeID != self.selectedResourceTypeID:
            raise ResourceRenderAbortedError
        return (inRange, texture)



    def GetCurrentResourceValueAt(self, phi, theta):
        if not self.currSphericalHarmonic:
            return None
        return builder.GetValueAt(self.currSphericalHarmonic, phi, theta)



    def OnSessionChanged(self, isRemote, sess, change):
        if 'stationid' in change and change['stationid'][1] is None and self.IsOpen():
            sm.GetService('bracket').Hide()



    def CreateChartFromSamples(self, width, height, dataX, dataY, dataZ, rangeXY = None):
        startTime = blue.os.GetTime()
        if rangeXY:
            (minX, minY, maxX, maxY,) = rangeXY
        else:
            minX = min(dataX)
            maxX = max(dataX)
            minY = min(dataY)
            maxY = max(dataY)
        maxZ = max(dataZ)
        minZ = min(dataZ)
        chart = XYChart(width, height)
        chart.setPlotArea(0, 0, width, height, Transparent, Transparent, Transparent, Transparent, Transparent)
        layer = chart.addContourLayer(dataX, dataY, dataZ)
        chart.xAxis().setLinearScale(minX, maxX, NoValue)
        chart.xAxis().setColors(Transparent)
        chart.yAxis().setLinearScale(maxY, minY, NoValue)
        chart.yAxis().setColors(Transparent)
        colorAxis = layer.colorAxis()
        colorAxis.setColorGradient(True, [long(max(0, minZ)) << 24, long(min(255, maxZ)) << 24])
        layer.setSmoothInterpolation(True)
        layer.setContourColor(Transparent)
        self.LogInfo('CreateChartFromSamples width', width, 'height', height, 'render time', float(blue.os.GetTime() - startTime) / const.SEC, 'seconds')
        return chart



    def GenerateSamplePoints(self, sqrtNumSamples):
        self.LogInfo('GenerateSamplePoints creating', sqrtNumSamples ** 2, 'samples for chart generation')
        thetaSamples = []
        phiSamples = []
        scale = 1.0 / (sqrtNumSamples - 1)
        for a in xrange(sqrtNumSamples):
            y = a * scale
            phi = MATH_2PI * y
            for b in xrange(sqrtNumSamples):
                x = b * scale
                linear = math.pi * x * LINER_BLENDING_RATIO
                theta = math.acos(1 - x * 2) * (1 - LINER_BLENDING_RATIO) + linear
                thetaSamples.append(theta)
                phiSamples.append(phi)


        return (thetaSamples, phiSamples)



    def ChartResourceLayer(self, resSH):
        resourceTypeID = self.selectedResourceTypeID
        if not hasattr(self, 'thetaSamples'):
            (self.thetaSamples, self.phiSamples,) = self.GenerateSamplePoints(SQRT_NUM_SAMPLES)
        data = []
        for i in xrange(len(self.thetaSamples)):
            value = builder.GetValueAt(resSH, self.phiSamples[i], self.thetaSamples[i])
            data.append(value)
            blue.pyos.BeNice()
            if resourceTypeID != self.selectedResourceTypeID:
                raise ResourceRenderAbortedError

        chart = self.CreateChartFromSamples(PLANET_RESOURCE_TEX_WIDTH, PLANET_RESOURCE_TEX_HEIGHT, self.phiSamples, self.thetaSamples, data)
        return chart



    def SetResourceTexture(self, texture):
        effect = self.resourceLayer.mesh.transparentAreas[0].effect
        for resource in effect.resources:
            if resource.name == 'ResourceDistMap':
                resource.SetResource(texture)




    def SetResourceDisplayRange(self, low, hi):
        settings.char.ui.Set('planet_resource_display_range', (low, hi))
        stretch = 1.0 / (hi - low)
        offset = -low * stretch
        if self.planetTransform is not None:
            if self.resourceLayer is not None:
                effect = self.resourceLayer.mesh.transparentAreas[0].effect
                for param in effect.parameters:
                    if param.name == 'HeatStretch':
                        param.value = stretch
                    elif param.name == 'HeatOffset':
                        param.value = offset




    def OpenPlanetCargoLinkImportWindow(self, cargoLinkID, spaceportPinID = None, exportMode = False):
        windowSvc = sm.GetService('window')
        wnd = windowSvc.GetWindow('PlanetaryImportExportUI')
        if wnd:
            if wnd.cargoLinkID != cargoLinkID:
                wnd.CloseX()
                wnd = None
            else:
                wnd.Maximize()
        if not wnd:
            windowSvc.GetWindow('PlanetaryImportExportUI', create=1, maximize=1, cargoLinkID=cargoLinkID, spaceportPinID=spaceportPinID, exportMode=exportMode)



    def GetSurveyWindow(self, ecuPinID):
        wnd = sm.GetService('window').GetWindow('PlanetSurvey', create=1, ecuPinID=ecuPinID)
        if wnd.ecuPinID != ecuPinID:
            self.CloseSurveyWindow()
            self.myPinManager.EnterSurveyMode(ecuPinID)
        else:
            self.EnterSurveyMode(ecuPinID)
        return sm.GetService('window').GetWindow('PlanetSurvey')



    def EnterSurveyMode(self, ecuPinID):
        if self.modeController is not None and hasattr(self.modeController, 'resourceControllerTab') and self.modeController.resourceControllerTab is not None:
            self.modeController.resourceControllerTab.EnterSurveyMode()



    def ExitSurveyMode(self):
        if self.modeController is not None and hasattr(self.modeController, 'resourceControllerTab') and self.modeController.resourceControllerTab is not None:
            self.modeController.resourceControllerTab.ExitSurveyMode()
        self.myPinManager.LockHeads()



    def CloseSurveyWindow(self):
        wnd = sm.GetService('window').GetWindow('PlanetSurvey')
        if wnd:
            wnd.SelfDestruct()



    def GMShowResource(self, resourceTypeID, layer):
        self.LogInfo('GMShowResource', resourceTypeID, layer)
        planet = sm.GetService('planetSvc').GetPlanet(self.planetID)
        data = planet.remoteHandler.GMGetCompleteResource(resourceTypeID, layer)
        sh = builder.CreateSHFromBuffer(data.data, data.numBands)
        self.ShowSH(sh, scaleIt=layer == 'base')



    def ShowSH(self, sh, scaleIt = True):
        if scaleIt:
            builder.ScaleSH(sh, 1.0 / const.planetResourceMaxValue)
        chart = self.ChartResourceLayer(sh)
        buf = chart.makeChart2(chart.PNG)
        texture = trinity.device.CreateTexture(PLANET_RESOURCE_TEX_WIDTH, PLANET_RESOURCE_TEX_HEIGHT, 1, 0, trinity.TRIFMT_X8R8G8B8, trinity.TRIPOOL_MANAGED)
        texture.GetSurfaceLevel(0).LoadSurfaceFromFileInMemory(buf)
        if self.planetTransform is not None:
            self.EnableResourceLayer()
            self.SetResourceTexture(texture)



    def GMCreateNuggetLayer(self, typeID):
        self.planet.remoteHandler.GMCreateNuggetLayer(self.planetID, typeID)
        self.GMShowResource(typeID, 'nuggets')



    def LogPlanetAccess(self):
        if self.planetAccessRequired is not None:
            planetAccessed = 1 if self.planetAccessRequired else 0
            myPlanets = sm.GetService('planetSvc').GetMyPlanets()
            colonized = 0
            for p in myPlanets:
                if p.planetID == self.planetID:
                    colonized = 1
                    break

            sm.GetService('infoGatheringSvc').LogInfoEvent(eventTypeID=const.infoEventPlanetUserAccess, itemID=session.charid, int_1=planetAccessed, int_2=1, int_3=colonized)
            self.planetAccessRequired = None



    def SetPlanet(self, planetID = None):
        pID = planetID
        if pID is None:
            pID = self.planetID
        self.planet = sm.GetService('planetSvc').GetPlanet(pID)
        self.planet.StartTicking()



    def OpenContainer(self, pin):
        self.CloseCurrentlyOpenContainer()
        self.currentContainer = pin.GetContainer(parent=self.planetUIContainer)
        self.currentExpandedPin = pin



    def CloseCurrentlyOpenContainer(self):
        if not self.currentContainer:
            return 
        self.planetUIContainer.children.remove(self.currentContainer)
        self.currentContainer.updateInfoContTimer.KillTimer()
        self.currentContainer.Close()
        self.currentContainer = None
        self.currentExpandedPin.OnSomethingElseClicked()
        self.currentExpandedPin = None
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_pininteraction_close_play')



    def FocusCameraOnCommandCenter(self, time = 1.0):
        for p in self.myPinManager.pinsByID.values():
            if p.pin.IsCommandCenter():
                try:
                    self.planetNav.camera.AutoOrbit(p.surfacePoint, newZoom=0.3, time=time)
                except AttributeError:
                    pass
                return 




    def OnPlanetZoomChanged(self, zoom):
        self.zoom = zoom
        self.curveLineDrawer.ChangeLineSetWidth('links', 1.1 - zoom)
        self.myPinManager.OnPlanetZoomChanged(zoom)



    def VerifySimulation(self):
        self.planet.GMVerifySimulation()



    def GetLocalDistributionReport(self, surfacePoint):
        report = self.planet.GetLocalDistributionReport(surfacePoint)
        txtMsg = 'latitude: %3.2f\xb0   longitude: %3.2f\xb0 <br><br>Name (typeID): base * quality - depletion = final (raw)<br><br>' % (math.degrees(surfacePoint.phi), math.degrees(surfacePoint.theta))
        for k in report['base'].keys():
            txtMsg += '%s (%d): %3.3f * %3.3f - %3.3f = %3.3f (%3.3f)<br>' % (cfg.invtypes.Get(k).name,
             k,
             report['base'][k],
             report['quality'][k],
             report['deplete'][k],
             report['final'][k],
             report['raw'][k])

        uthread.new(eve.Message, 'CustomInfo', {'info': txtMsg}).context = 'gameui.ServerMessage'



    def AddDepletionPoint(self, point):
        self.myPinManager.AddDepletionPoint(point)



    def CancelInstallProgram(self, pinID, pinData):
        currentPlanet = self.GetCurrentPlanet()
        if currentPlanet is None:
            return 
        pin = currentPlanet.CancelInstallProgram(pinID, pinData)
        if pin is not None:
            self.myPinManager.ReRenderPin(pin)



    def LoadSpherePinResources(self, spherePin, textureName):
        self.spherePinsPendingLoad.append((spherePin, textureName))
        if not self.spherePinLoadThread:
            self.spherePinLoadThread = uthread.new(self._LoadSpherePinResources)



    def _LoadSpherePinResources(self):
        while True:
            trinity.WaitForResourceLoads()
            while self.spherePinsPendingLoad:
                (spherePin, textureName,) = self.spherePinsPendingLoad.pop()
                spherePin.pinEffect.PopulateParameters()
                for res in spherePin.pinEffect.resources:
                    if res.name == 'Layer1Map':
                        res.resourcePath = textureName
                    elif res.name == 'Layer2Map':
                        res.resourcePath = 'res:/dx9/texture/UI/pinCircularRamp.dds'

                spherePin.pickEffect.PopulateParameters()
                for res in spherePin.pickEffect.resources:
                    if res.name == 'Layer1Map':
                        res.resourcePath = textureName

                spherePin.pinColor = spherePin.pinColor
                spherePin.geometryResPath = 'res:/dx9/model/worldobject/planet/PlanetSphere.gr2'

            blue.pyos.synchro.Yield()




    def StopSpherePinLoadThread(self):
        if self.spherePinLoadThread:
            self.spherePinLoadThread.kill()
            self.spherePinLoadThread = None



    def EnteredEditMode(self, planetID):
        if self.planetID == planetID and self.myPinManager is not None:
            self.myPinManager.OnPlanetEnteredEditMode()



    def ExitedEditMode(self, planetID):
        if self.planetID == planetID and self.myPinManager is not None:
            self.myPinManager.OnPlanetExitedEditMode()




