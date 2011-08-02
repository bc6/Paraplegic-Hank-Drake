import spaceObject
import trinity
import blue
import uthread
import math
import nodemanager
import random
import sys
import datetime
import util
import os
GRAVITATIONAL_CONST = 6.673e-11
rot = blue.rot

def CopyRenderTargetToTexture(renderTarget, copySurface, size, format):
    tex = None
    while tex is None:
        try:
            dev = trinity.device
            rect = trinity.TriRect(0, 0, 2 * size, size)
            dev.GetRenderTargetData(renderTarget, copySurface)
            tex = dev.CreateTexture(2 * size, size, 0, 0, format, trinity.TRIPOOL_MANAGED)
            dev.UpdateSurface(copySurface, rect, tex.GetSurfaceLevel(0))
            tex.GenerateMipMaps()
        except trinity.D3DERR_OUTOFVIDEOMEMORY:
            if size < 2:
                return 
            size /= 2
            tex = None
        except:
            return 

    return tex



class Planet(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.Planet'

    def __init__(self):
        spaceObject.SpaceObject.__init__(self)
        self.textureSet = None
        self.loaded = False
        self.forceLOD = True
        self.attributes = None
        self.modelRes = []
        self.heightMapResPath1 = ''
        self.heightMapResPath2 = ''
        self.largeTextures = False



    def Display(self, display = 1):
        pass



    def LoadModel(self):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        self.typeID = slimItem.typeID
        uthread.new(self.LoadPlanet)



    def LoadPlanet(self, itemID = None, forPhotoService = False, rotate = True, hiTextures = False):
        if itemID is None:
            itemID = self.id
        self.itemID = itemID
        if type(cfg.invtypes.Get(self.typeID).graphicID) != type(0):
            raise RuntimeError('NeedGraphicIDNotMoniker', itemID)
        self.modelPath = cfg.invtypes.Get(self.typeID).GraphicFile()
        if hiTextures:
            self.largeTextures = True
            self.modelPath = self.modelPath.replace('.red', '_HI.red')
        self.model = trinity.EvePlanet()
        if self.model is None:
            self.LogError('Could not create model for planet with id', itemID)
            return 
        self.model.translationCurve = self
        self.model.highDetail = trinity.EveTransform()
        self.model.scaling = self.radius
        self.model.radius = self.radius
        self.model.name = '%d' % itemID
        if rotate:
            rotationDirection = 1
            if self.id % 2:
                rotationDirection = -1
            random.seed(self.id)
            rotationTime = random.random() * 2000 + 3000
            yCurve = trinity.TriScalarCurve()
            yCurve.extrapolation = trinity.TRIEXT_CYCLE
            yCurve.AddKey(0.0, 1.0, 0.0, 0.0, trinity.TRIINT_LINEAR)
            yCurve.AddKey(rotationTime, rotationDirection * 360.0, 0.0, 0.0, trinity.TRIINT_LINEAR)
            yCurve.Sort()
            tilt = random.random() * 60.0 - 30.0
            pCurve = trinity.TriScalarCurve()
            pCurve.extrapolation = trinity.TRIEXT_CYCLE
            pCurve.AddKey(0.0, 1.0, 0.0, 0.0, trinity.TRIINT_HERMITE)
            pCurve.AddKey(6000.0, tilt, 0.0, 0.0, trinity.TRIINT_HERMITE)
            pCurve.AddKey(12000.0, 0.0, 0.0, 0.0, trinity.TRIINT_HERMITE)
            pCurve.Sort()
            self.model.rotationCurve = trinity.TriYPRSequencer()
            self.model.rotationCurve.YawCurve = yCurve
            self.model.rotationCurve.PitchCurve = pCurve
        if self.typeID == const.typeMoon:
            self.model.zOnlyModel = trinity.Load('res:/dx9/model/worldobject/planet/planetzonly.red')
        if self.attributes is None:
            try:
                self.attributes = cfg.planetattributes.Get(itemID)
            except:
                self.LogWarn('Could not find attributes for planet with ID', itemID)
                info = sm.GetService('map').GetPlanetInfo(itemID, hierarchy=True)
                f = blue.os.CreateInstance('blue.ResFile')
                filename = os.path.join(u'res:/planetAttributes/%d.region' % info.regionID)
                if f is not None and f.Open(filename):
                    data = f.Read()
                    planetAttributes = blue.marshal.Load(data)
                    f.Close()
                    self.attributes = planetAttributes[itemID]
                else:
                    self.LogWarn('Could not find attributes for planet with ID', itemID)
                sys.exc_clear()
        if not forPhotoService:
            self.model.resourceCallback = self.ResourceCallback
            scene2 = sm.GetService('sceneManager').GetRegisteredScene2('default')
            scene2.planets.append(self.model)



    def LoadRedFiles(self):
        planet = trinity.Load(self.modelPath)
        if planet is None:
            self.LogError('No planet was loaded!', self.modelPath)
            return False
        if planet.__bluetype__ != 'trinity.EveTransform':
            self.LogError('Invalid planet redfile, is not an EveTransform', self.modelPath)
            return False
        self.model.highDetail.children.append(planet)
        self.effectHeight = trinity.Tr2Effect()
        if self.effectHeight is None:
            self.LogError('Could not create effect for planet with id', itemID)
            return False
        self._Planet__LoadEffect()
        if self.attributes is not None:
            self._Planet__ApplyPlanetAttributes(planet, self.itemID)
        else:
            self._Planet__ApplyDefaultPlanetAttributes(planet, self.itemID)
        return True



    def Release(self):
        if hasattr(self.model, 'resourceCallback'):
            self.model.resourceCallback = None
        if hasattr(self.model, 'children'):
            del self.model.children[:]
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        scene2.planets.fremove(self.model)
        spaceObject.SpaceObject.Release(self, 'Planet')



    def GetPlanetByID(self, itemID, typeID):
        self.LogInfo('GetPlanetByID called')
        self.typeID = typeID
        self.LoadPlanet(itemID, True)



    def PrepareForWarp(self, distance, dest):
        if self.model is not None:
            self.model.PrepareForWarp(distance, dest)



    def WarpStopped(self):
        if self.model is not None:
            self.model.WarpStopped()



    def ResourceCallback(self, create, size = 2048):
        if create:
            pm = sm.GetService('space').planetManager
            pm.DoPlanetPreprocessing(self, size)
        elif self.model is None:
            return 
        heightMapParam = nodemanager.FindNode(self.model.highDetail.children, 'HeightMap', 'trinity.TriTexture2DParameter')
        if heightMapParam is None:
            self.model.resourceActionPending = False
            self.model.ready = False
            return 
        heightMapParam.SetResource(None)
        for (n, path,) in self.modelRes:
            node = nodemanager.FindNode(self.model.highDetail.children, n, 'trinity.TriTexture2DParameter')
            if node is not None:
                node.resourcePath = ''

        self.model.ready = False
        self.model.resourceActionPending = False



    def DoPreProcessEffectForPhotoSvc(self, size):
        format = trinity.TRIFMT_A8R8G8B8
        target = trinity.device.CreateRenderTarget(2 * size, size, format, trinity.TRIMULTISAMPLE_NONE, 0, 1)
        offscreen = trinity.device.CreateOffscreenPlainSurface(2 * size, size, format, trinity.TRIPOOL_SYSTEMMEM)
        vp = trinity.TriViewport()
        vp.width = 2 * size
        vp.height = size
        if not self.LoadRedFiles():
            return 
        trinity.WaitForResourceLoads()
        heightMapParam1 = nodemanager.FindNode(self.effectHeight, 'NormalHeight1', 'trinity.TriTexture2DParameter')
        if heightMapParam1 is not None:
            heightMapParam1.resourcePath = self.heightMapResPath1
        heightMapParam2 = nodemanager.FindNode(self.effectHeight, 'NormalHeight2', 'trinity.TriTexture2DParameter')
        if heightMapParam2 is not None:
            heightMapParam2.resourcePath = self.heightMapResPath2
        targetSizeParam = nodemanager.FindNode(self.effectHeight, 'TargetTextureHeight', 'trinity.TriTexture2DParameter')
        if targetSizeParam is not None:
            targetSizeParam.value = size
        trinity.WaitForResourceLoads()
        rj = trinity.CreateRenderJob('Height normal Compositing')
        rj.SetRenderTarget(target)
        rj.SetViewport(vp)
        rj.SetDepthStencil(None)
        step = rj.Clear((0.0, 0.0, 0.0, 0.0), 1.0)
        step.isDepthCleared = False
        rj.RenderEffect(self.effectHeight)
        rj.ScheduleOnce()
        rj.WaitForFinish()
        dev = trinity.device
        dev.GetRenderTargetData(target, offscreen)
        tex = dev.CreateTexture(2 * size, size, 1, 0, format, trinity.TRIPOOL_DEFAULT)
        dev.UpdateSurface(offscreen, None, tex.GetSurfaceLevel(0))
        heightMapParam = nodemanager.FindNode(self.model.highDetail.children, 'HeightMap', 'trinity.TriTexture2DParameter')
        if heightMapParam is None:
            return 
        heightMapParam.SetResource(tex)



    def DoPreProcessEffect(self, size, format, target, copySurface):
        if target is None or copySurface is None:
            self.model.resourceActionPending = False
            self.model.ready = True
            return 
        vp = trinity.TriViewport()
        vp.width = 2 * size
        vp.height = size
        trinity.WaitForResourceLoads()
        if self.model is None:
            return 
        if len(self.modelRes) == 0:
            if not self.LoadRedFiles():
                self.model.resourceActionPending = False
                self.model.ready = True
                return 
        else:
            for (n, path,) in self.modelRes:
                node = nodemanager.FindNode(self.model.highDetail.children, n, 'trinity.TriTexture2DParameter')
                if node is not None:
                    node.resourcePath = path

        heightMapParam1 = nodemanager.FindNode(self.effectHeight, 'NormalHeight1', 'trinity.TriTexture2DParameter')
        if heightMapParam1 is not None:
            heightMapParam1.resourcePath = self.heightMapResPath1
        heightMapParam2 = nodemanager.FindNode(self.effectHeight, 'NormalHeight2', 'trinity.TriTexture2DParameter')
        if heightMapParam2 is not None:
            heightMapParam2.resourcePath = self.heightMapResPath2
        targetSizeParam = nodemanager.FindNode(self.effectHeight, 'TargetTextureHeight', 'trinity.TriTexture2DParameter')
        if targetSizeParam is not None:
            targetSizeParam.value = size
        trinity.WaitForResourceLoads()
        if self.model is None:
            return 
        rj = trinity.CreateRenderJob('Height normal Compositing')
        rj.SetRenderTarget(target)
        rj.SetViewport(vp)
        rj.SetDepthStencil(None)
        step = rj.Clear((0.0, 0.0, 0.0, 0.0), 1.0)
        step.isDepthCleared = False
        rj.RenderEffect(self.effectHeight)
        rj.ScheduleOnce()
        rj.WaitForFinish()
        if self.model is None:
            return 
        tex = CopyRenderTargetToTexture(target, copySurface, size, format)
        if heightMapParam1 is not None:
            heightMapParam1.resourcePath = ''
            heightMapParam1.SetResource(None)
        if heightMapParam2 is not None:
            heightMapParam2.resourcePath = ''
            heightMapParam2.SetResource(None)
        heightMapParam = nodemanager.FindNode(self.model.highDetail.children, 'HeightMap', 'trinity.TriTexture2DParameter')
        if heightMapParam is None:
            self.model.resourceActionPending = False
            self.model.ready = True
            return 
        heightMapParam.SetResource(tex)
        self.model.ready = True
        self.model.resourceActionPending = False



    def __LoadAtmosphere(self, preset):
        if preset is not None and len(preset.children) > 0:
            atmosphere = preset.children[0]
        elif self.typeID == const.typePlanetLava:
            atmosphere = trinity.Load('res:/dx9/model/worldobject/planet/LavaAtmosphere.red')
        elif self.typeID == const.typePlanetEarthlike:
            atmosphere = trinity.Load('res:/dx9/model/worldobject/planet/Atmosphere.red')
        elif self.typeID == const.typePlanetOcean:
            atmosphere = trinity.Load('res:/dx9/model/worldobject/planet/OceanAtmosphere.red')
        elif self.typeID == const.typePlanetIce:
            atmosphere = trinity.Load('res:/dx9/model/worldobject/planet/IceAtmosphere.red')
        elif self.typeID == const.typePlanetSandstorm:
            atmosphere = trinity.Load('res:/dx9/model/worldobject/planet/SandStormAtmosphere.red')
        elif self.typeID == const.typePlanetThunderstorm:
            atmosphere = trinity.Load('res:/dx9/model/worldobject/planet/ThunderStormAtmosphere.red')
        else:
            atmosphere = None
        if atmosphere is not None:
            self.model.highDetail.children.append(atmosphere)



    def __LoadEffect(self):
        if len(self.model.highDetail.children[0].mesh.transparentAreas) > 0:
            resPath = self.model.highDetail.children[0].mesh.transparentAreas[0].effect.effectFilePath
            resPath = resPath.replace('.fx', 'BlitHeight.fx')
            self.effectHeight.effectFilePath = resPath
        elif len(self.model.highDetail.children[0].mesh.opaqueAreas) > 0:
            resPath = self.model.highDetail.children[0].mesh.opaqueAreas[0].effect.effectFilePath
            resPath = resPath.replace('.fx', 'BlitHeight.fx')
            self.effectHeight.effectFilePath = resPath
        else:
            self.LogError('Unexpected program flow! Loading fallback shader.')
            self.effectHeight.effectFilePath = 'res:/Graphics/Effect/Managed/Space/Planet/EarthlikePlanetBlitHeight.fx'



    def __ApplyPlanetAttributes(self, planet, itemID):
        preset = None
        if self.attributes[1] is not None:
            presetPath = util.GraphicFile(self.attributes[1])
            if self.largeTextures:
                presetPath = presetPath.replace('/Template/', '/Template_HI/')
            try:
                preset = trinity.Load(presetPath)
            except:
                self.LogWarn('Could not load large textures preset for planet', itemID)
                sys.exc_clear()
                return 
        if len(planet.mesh.opaqueAreas) > 0:
            for param in planet.mesh.opaqueAreas[0].effect.parameters:
                if preset is not None and len(preset.mesh.opaqueAreas) > 0:
                    self._Planet__OverrideWithPreset(preset.mesh.opaqueAreas[0].effect.parameters, param)
                self.effectHeight.parameters.append(param)

            for res in planet.mesh.opaqueAreas[0].effect.resources:
                if preset is not None and len(preset.mesh.opaqueAreas) > 0:
                    self._Planet__OverrideWithPreset(preset.mesh.opaqueAreas[0].effect.resources, res)
                self.effectHeight.resources.append(res)

        elif len(planet.mesh.transparentAreas) > 0:
            for param in planet.mesh.transparentAreas[0].effect.parameters:
                if preset is not None and len(preset.mesh.transparentAreas) > 0:
                    self._Planet__OverrideWithPreset(preset.mesh.transparentAreas[0].effect.parameters, param)
                self.effectHeight.parameters.append(param)

            for res in planet.mesh.transparentAreas[0].effect.resources:
                if preset is not None and len(preset.mesh.transparentAreas) > 0:
                    self._Planet__OverrideWithPreset(preset.mesh.transparentAreas[0].effect.resources, res)
                self.effectHeight.resources.append(res)

        if self.attributes[2] is not None and self.attributes[3] is not None:
            param1 = trinity.TriTexture2DParameter()
            param1.name = 'NormalHeight1'
            self.heightMapResPath1 = util.GraphicFile(self.attributes[2])
            self.effectHeight.resources.append(param1)
            param2 = trinity.TriTexture2DParameter()
            param2.name = 'NormalHeight2'
            self.heightMapResPath2 = util.GraphicFile(self.attributes[3])
            self.effectHeight.resources.append(param2)
            param3 = trinity.Tr2FloatParameter()
            param3.name = 'Random'
            param3.value = itemID % 100
            self.effectHeight.parameters.append(param3)
            param4 = trinity.Tr2FloatParameter()
            param4.name = 'TargetTextureHeight'
            param4.value = 2048
            self.effectHeight.parameters.append(param4)
        self._Planet__LoadAtmosphere(preset)
        if self.typeID == const.typePlanetEarthlike or self.typeID == const.typePlanetSandstorm:
            now = datetime.datetime.now()
            random.seed(now.year + now.month * 30 + now.day + self.itemID)
            val = random.randint(1, 5)
            useDense = val % 5 == 0
            if self.typeID == const.typePlanetEarthlike:
                cloudMapIDs = (3848, 3849, 3851, 3852)
                cloudCapMapIDs = (3853, 3854, 3855, 3856)
                if useDense:
                    cloudMapIDs = (3857, 3858, 3859, 3860)
                    cloudCapMapIDs = (3861, 3862, 3863, 3864)
            else:
                cloudMapIDs = (3956, 3957, 3958, 3959)
                cloudCapMapIDs = (3960, 3961, 3962, 3963)
            cloudMapIdx = random.randint(0, 3)
            cloudCapMapIdx = random.randint(0, 3)
            cloudCapNode = nodemanager.FindNode(self.model, 'CloudCapTexture', 'trinity.TriTexture2DParameter')
            cloudCapNode.resourcePath = util.GraphicFile(cloudCapMapIDs[cloudCapMapIdx])
            cloudNode = nodemanager.FindNode(self.model, 'CloudsTexture', 'trinity.TriTexture2DParameter')
            cloudNode.resourcePath = util.GraphicFile(cloudMapIDs[cloudMapIdx])
            if self.largeTextures:
                cloudCapNode.resourcePath = cloudCapNode.resourcePath.replace('.dds', '_HI.dds')
                cloudNode.resourcePath = cloudNode.resourcePath.replace('.dds', '_HI.dds')
            cloudsFactors = nodemanager.FindNode(self.model, 'CloudsFactors', 'trinity.TriVector4Parameter')
            if cloudsFactors:
                cloudsFactors.v3 = random.random() * 2.0 + 1.0
                cloudsFactors.v2 = random.random() * 0.4 + 0.6
        inhabitable = self.typeID is const.typePlanetOcean or self.typeID is const.typePlanetEarthlike
        if inhabitable and self.attributes[0] is 0:
            for textureFile in ['CityLight', 'CityDistributionTexture', 'CityDistributionMask']:
                texture = nodemanager.FindNode(self.model.highDetail, textureFile, 'trinity.TriTexture2DParameter')
                if texture is not None:
                    texture.resourcePath = ''

            coverageFactors = nodemanager.FindNode(self.model.highDetail, 'CoverageFactors', 'trinity.TriVector4Parameter')
            if coverageFactors is not None:
                coverageFactors.v4 = 0
        if len(self.modelRes) == 0:
            if len(planet.mesh.opaqueAreas) > 0:
                for res in planet.mesh.opaqueAreas[0].effect.resources:
                    if res.name != 'HeightMap':
                        self.modelRes.append((res.name, res.resourcePath))

            if len(planet.mesh.transparentAreas) > 0:
                for res in planet.mesh.transparentAreas[0].effect.resources:
                    if res.name != 'HeightMap':
                        self.modelRes.append((res.name, res.resourcePath))




    def __ApplyDefaultPlanetAttributes(self, planet, itemID):
        normalHeight = ''
        if self.typeID == const.typePlanetLava or self.typeID == const.typePlanetShattered or self.typeID == const.typePlanetPlasma:
            normalHeight = 'res:/dx9/model/worldobject/planet/Lava/Lava01_H.dds'
        elif self.typeID == const.typePlanetEarthlike:
            normalHeight = 'res:/dx9/model/worldobject/planet/Terrestrial/Terrestrial01_H.dds'
        elif self.typeID == const.typePlanetOcean:
            normalHeight = 'res:/dx9/model/worldobject/planet/Terrestrial/Terrestrial01_H.dds'
        elif self.typeID == const.typePlanetIce:
            normalHeight = 'res:/dx9/model/worldobject/planet/Ice/Ice01_H.dds'
        elif self.typeID == const.typePlanetSandstorm:
            normalHeight = 'res:/dx9/model/worldobject/planet/Sandstorm/Terrestrial01_H.dds'
        elif self.typeID == const.typePlanetGas:
            normalHeight = 'res:/dx9/model/worldobject/planet/GasGiant/GasGiant01_D.dds'
        param1 = trinity.TriTexture2DParameter()
        param1.name = 'NormalHeight1'
        self.heightMapResPath1 = normalHeight
        self.effectHeight.resources.append(param1)
        param2 = trinity.TriTexture2DParameter()
        param2.name = 'NormalHeight2'
        self.heightMapResPath2 = normalHeight
        self.effectHeight.resources.append(param2)
        param4 = trinity.Tr2FloatParameter()
        param4.name = 'TargetTextureHeight'
        param4.value = 2048
        self.effectHeight.parameters.append(param4)



    def __OverrideWithPreset(self, section, param):
        node = nodemanager.FindNode(section, param.name, param.__bluetype__)
        if node is not None:
            param = node
            n = nodemanager.FindNode(self.model.highDetail, param.name, param.__bluetype__)
            if n is not None:
                if param.__bluetype__ == 'trinity.TriVector4Parameter':
                    n.v1 = param.v1
                    n.v2 = param.v2
                    n.v3 = param.v3
                    n.v4 = param.v4
                elif param.__bluetype__ == 'trinity.TriFloatParameter':
                    n.value = param.value
                else:
                    n.resourcePath = param.resourcePath



exports = {'spaceObject.Planet': Planet}

