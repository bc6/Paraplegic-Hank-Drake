import os
import sys
import trinity
import blue
import bluepy
import uthread
import log
import yaml
import types
import TextureCompositor.TextureCompositor as tc
import RenderTargetManager.RenderTargetManager as rtm
import paperDoll as PD
TC_MARKERS_ENABLED = False

def AddMarker(m):
    if TC_MARKERS_ENABLED:
        trinity.graphs.AddMarker('frameTime', m)


RTM = rtm.RenderTargetManager()
COMPRESS_DXT1 = trinity.TR2DXT_COMPRESS_SQUISH_DXT1
COMPRESS_DXT5 = trinity.TR2DXT_COMPRESS_SQUISH_DXT5
COMPRESS_DXT5n = trinity.TR2DXT_COMPRESS_RT_DXT5N

class UpdateRuleBundle(object):
    __guid__ = 'paperDoll.UpdateRuleBundle'
    blendShapesOnly = property(fget=lambda self: self._UpdateRuleBundle__blendShapesOnly)
    decalsOnly = property(fget=lambda self: self._UpdateRuleBundle__decalsOnly)

    def setdoDecals(self, value):
        self._UpdateRuleBundle__doDecals = value


    doDecals = property(fget=lambda self: self._UpdateRuleBundle__doDecals or self._UpdateRuleBundle__decalsOnly, fset=setdoDecals)

    def __init__(self):
        self.forcesLooseTop = False
        self.hidesBootShin = False
        self.undoMaskedShaders = False
        self.rebuildHair = False
        self.mapsToComposite = list(PD.MAPS)
        self._UpdateRuleBundle__blendShapesOnly = False
        self._UpdateRuleBundle__decalsOnly = False
        self.meshesAddedOrRemoved = False
        self.partsToComposite = []
        self._UpdateRuleBundle__doDecals = False



    def __str__(self):
        s = '{0}\n'.format(id(self))
        for (key, value,) in self.__dict__.iteritems():
            s += '\t{0} := {1}\n'.format(key, value)

        return s



    def SetBlendShapesOnly(self, value):
        self._UpdateRuleBundle__blendShapesOnly = value



    def SetDecalsOnly(self, value):
        self._UpdateRuleBundle__decalsOnly = value




class MapBundle(object):
    __guid__ = 'paperDoll.MapBundle'

    def __init__(self):
        self.diffuseMap = None
        self.specularMap = None
        self.normalMap = None
        self.maskMap = None
        self.baseResolution = None
        self.hashKeys = {}
        self.mapResolutions = {}
        self.mapResolutionRatios = {}
        self.SetBaseResolution(2048, 1024)
        self._busyDownScaling = False



    def __getitem__(self, idx):
        if idx == PD.DIFFUSE_MAP:
            return self.diffuseMap
        if idx == PD.SPECULAR_MAP:
            return self.specularMap
        if idx == PD.NORMAL_MAP:
            return self.normalMap
        if idx == PD.MASK_MAP:
            return self.maskMap
        raise AttributeError()



    def SetBaseResolution(self, width, height):
        self.baseResolution = (width, height)
        for mapType in PD.MAPS:
            self.SetMapTypeResolutionRatio(mapType, self.mapResolutionRatios.get(mapType, PD.MAPSIZERATIOS[mapType]))




    def SetMapByTypeIndex(self, idx, mapToSet, hashKey = None):
        if idx == PD.DIFFUSE_MAP:
            self.diffuseMap = mapToSet
        elif idx == PD.SPECULAR_MAP:
            self.specularMap = mapToSet
        elif idx == PD.NORMAL_MAP:
            self.normalMap = mapToSet
        elif idx == PD.MASK_MAP:
            self.maskMap = mapToSet
        else:
            raise ValueError('paperDoll::MapBundle::SetMapByTypeIndex - Index provided is not defined or supported. It must be defined in paperDoll.MAPS')
        if hashKey:
            self.hashKeys[idx] = hashKey



    def GetResolutionByMapType(self, mapType):
        return self.mapResolutions.get(mapType, self.baseResolution)



    def DoAsyncDownScale(self, mapType, mapSource, resolution):

        def fun(mapType, mapSource, resolution):
            while self._busyDownScaling:
                blue.synchro.Yield()

            self._busyDownScaling = True
            sourceIsCompressed = mapSource.format == trinity.TRIFMT_DXT5
            targetTex = trinity.device.CreateTexture(resolution[0], resolution[1], 1, 0, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_MANAGED)
            fx = trinity.Tr2Effect()
            fx.effectFilePath = 'res:/Graphics/Effect/Utility/Compositing/Copyblit.fx'
            while fx.effectResource.isLoading:
                blue.synchro.Yield()

            v = trinity.Tr2Vector4Parameter()
            v.name = 'SourceUVs'
            v.value = (0, 0, 1, 1)
            fx.parameters.append(v)
            tex = trinity.TriTexture2DParameter()
            tex.name = 'Texture'
            tex.SetResource(mapSource)
            fx.resources.append(tex)
            vp = trinity.TriViewport()
            vp.width = targetTex.width
            vp.height = targetTex.height
            renderTarget = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, vp.width, vp.height, trinity.TRIFMT_A8R8G8B8, trinity.TRIMULTISAMPLE_NONE, 0, 1)
            rj = trinity.CreateRenderJob('Resizing texture')
            rj.PushRenderTarget(renderTarget)
            rj.SetProjection(trinity.TriProjection())
            rj.SetView(trinity.TriView())
            rj.SetViewport(vp)
            rj.SetDepthStencil(None)
            rj.Clear((0.0, 0.0, 0.0, 0.0))
            rj.SetStdRndStates(trinity.RM_FULLSCREEN)
            rj.SetRenderState(trinity.D3DRS_SEPARATEALPHABLENDENABLE, 1)
            rj.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
            rj.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ZERO)
            rj.RenderEffect(fx)
            rj.CopyRtToTexture(targetTex)
            rj.PopRenderTarget()
            rj.ScheduleChained()
            rj.WaitForFinish()
            if sourceIsCompressed:
                targetTex = Factory.PerformTextureCompression(targetTex, mapType)
            self.SetMapByTypeIndex(mapType, targetTex)
            self._busyDownScaling = False


        t = uthread.new(fun, mapType, mapSource, resolution)
        uthread.schedule(t)



    def SetMapTypeResolutionRatio(self, mapType, ratio):
        self.mapResolutionRatios[mapType] = ratio
        newResolution = (int(ratio * self.baseResolution[0]), int(ratio * self.baseResolution[1]))
        oldResolution = self.mapResolutions.get(mapType, self.baseResolution)
        if newResolution[0] < oldResolution[0]:
            map = self[mapType]
            if map and map.isGood:
                self.DoAsyncDownScale(mapType, map, newResolution)
        self.mapResolutions[mapType] = newResolution



    def AllMapsGood(self):
        for each in iter(self):
            if not each or not each.isGood:
                return False

        return True



    def __iter__(self):
        yield self.diffuseMap
        yield self.specularMap
        yield self.normalMap
        yield self.maskMap



    def ReCreate(self):
        del self.diffuseMap
        del self.specularMap
        del self.normalMap
        del self.maskMap
        self.diffuseMap = None
        self.specularMap = None
        self.normalMap = None
        self.maskMap = None
        self.hashKeys = {}



    def __del__(self):
        del self.diffuseMap
        del self.specularMap
        del self.normalMap
        del self.maskMap




class PerformanceOptions():
    __guid__ = 'paperDoll.PerformanceOptions'
    useLodForRedfiles = False
    if hasattr(const, 'PAPERDOLL_LOD_RED_FILES'):
        useLodForRedfiles = const.PAPERDOLL_LOD_RED_FILES
    collapseShadowMesh = False
    if hasattr(const, 'PAPERDOLL_COLLAPSE_SHADOWMESH'):
        collapseShadowMesh = const.PAPERDOLL_COLLAPSE_SHADOWMESH
    collapseMainMesh = False
    if hasattr(const, 'PAPERDOLL_COLLAPSE_MAINMESH'):
        collapseMainMesh = const.PAPERDOLL_COLLAPSE_MAINMESH
    collapsePLPMesh = False
    if hasattr(const, 'PAPERDOLL_COLLAPSE_PLPMESH'):
        collapsePLPMesh = const.PAPERDOLL_COLLAPSE_PLPMESH
    preloadNudeAssets = False
    if hasattr(const, 'PAPERDOLL_PRELOAD_NUDE_ASSETS'):
        preloadNudeAssets = const.PAPERDOLL_PRELOAD_NUDE_ASSETS
    shadowLod = 2
    collapseVerbose = False
    updateFreq = {}
    useLod2DDS = False
    logLodPerformance = False
    maxLodQueueActive = 1

    @staticmethod
    def SetEnableYamlCache(enable, verbose = False, preloadModularLOD = True):

        def SetEnableYamlCache_t(enable, verbose, preloadModularLOD):
            if enable:
                yamlPreloader = PD.YamlPreloader(verbose=verbose)
                extensions = ['.yaml',
                 '.pose',
                 '.type',
                 '.color']
                yamlPreloader.Preload(rootFolder=PD.MALE_BASE_PATH, extensions=extensions)
                yamlPreloader.Preload(rootFolder=PD.FEMALE_BASE_PATH, extensions=extensions)
                if preloadModularLOD:
                    maleModLodPath = PD.MALE_BASE_PATH.lower().replace('modular', 'modularlod')
                    yamlPreloader.Preload(rootFolder=maleModLodPath, extensions=extensions)
                    femaleModLodPath = PD.FEMALE_BASE_PATH.lower().replace('modular', 'modularlod')
                    yamlPreloader.Preload(rootFolder=femaleModLodPath, extensions=extensions)
                PD.YamlPreloader.instance = yamlPreloader
            else:
                PD.YamlPreloader.instance = None


        uthread.new(SetEnableYamlCache_t, enable, verbose, preloadModularLOD)



    @staticmethod
    def SetEnableLodQueue(enable):
        if enable:
            PD.LodQueue.instance = PD.LodQueue()
        else:
            PD.LodQueue.instance = None



    @staticmethod
    def EnableOptimizations():
        PerformanceOptions.useLodForRedfiles = True
        PerformanceOptions.collapseShadowMesh = False
        PerformanceOptions.collapseMainMesh = False
        PerformanceOptions.collapsePLPMesh = False
        PerformanceOptions.shadowLod = 1
        PerformanceOptions.useLod2DDS = True
        PerformanceOptions.updateFreq = {0: 0,
         1: 20,
         2: 8}
        trinity.settings.SetValue('skinnedLowDetailThreshold', 250)
        trinity.settings.SetValue('skinnedMediumDetailThreshold', 650)
        PerformanceOptions.preloadNudeAssets = True
        Factory.PreloadShaders()
        PerformanceOptions.SetEnableYamlCache(True)
        PerformanceOptions.SetEnableLodQueue(True)
        PerformanceOptions.logLodPerformance = True




class CompressionSettings():
    __guid__ = 'paperDoll.CompressionSettings'

    @bluepy.CCP_STATS_ZONE_METHOD
    def __init__(self, compressTextures = True, generateMipmap = False, qualityLevel = None):
        self.compressTextures = compressTextures
        self.generateMipmap = generateMipmap
        self.qualityLevel = qualityLevel or trinity.TR2DXT_COMPRESS_SQ_RANGE_FIT
        self.compressNormalMap = True
        self.compressSpecularMap = True
        self.compressDiffuseMap = True
        self.compressMaskMap = True



    @bluepy.CCP_STATS_ZONE_METHOD
    def __repr__(self):
        return '%i%i%i%i%i%i' % (self.compressTextures,
         self.compressNormalMap,
         self.compressSpecularMap,
         self.compressDiffuseMap,
         self.compressMaskMap,
         self.generateMipmap)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetMapCompression(self, compressNormalMap = True, compressSpecularMap = True, compressDiffuseMap = True, compressMaskMap = True):
        self.compressNormalMap = compressNormalMap
        self.compressSpecularMap = compressSpecularMap
        self.compressDiffuseMap = compressDiffuseMap
        self.compressMaskMap = compressMaskMap



    @bluepy.CCP_STATS_ZONE_METHOD
    def AllowCompress(self, textureType):
        if textureType == PD.DIFFUSE_MAP:
            return self.compressDiffuseMap
        if textureType == PD.SPECULAR_MAP:
            return self.compressSpecularMap
        if textureType == PD.NORMAL_MAP:
            return self.compressNormalMap
        if textureType == PD.MASK_MAP:
            return self.compressMaskMap




class Factory(object, CompressionSettings, PD.ModifierLoader):
    __guid__ = 'paperDoll.Factory'
    shaderPreload = None
    texturePreload = None

    def setclothSimulationActive(self, value):
        if value:
            import GameWorld
            trinity.InitializeApex(GameWorld.GWPhysXWrapper())
        self._clothSimulationActive = value
        PD.ModifierLoader.setclothSimulationActive(self, value)


    clothSimulationActive = property(fget=lambda self: self._clothSimulationActive, fset=lambda self, value: self.setclothSimulationActive(value))

    @bluepy.CCP_STATS_ZONE_METHOD
    def __init__(self, gender = None):
        object.__init__(self)
        CompressionSettings.__init__(self, compressTextures=False)
        PD.ModifierLoader.__init__(self)
        if gender:
            log.LogWarn('PaperDoll: Deprication warning, Gender is no longer a property of the Factory.')
        self.allowTextureCache = False
        self.saveTexturesToDisk = False
        self.verbose = False
        self.skipCompositing = False
        self.preloadedResources = list()
        self.calculatedSubrects = dict()
        self.CalculateSubrects()
        self.PreloadedGenericHeadModifiers = {PD.GENDER.MALE: None,
         PD.GENDER.FEMALE: None}
        self.PreloadShaders()
        uthread.new(self.PreloadGenericHeadsOnceLoaded_t)
        if PerformanceOptions.preloadNudeAssets:
            uthread.new(self.PreloadNudeResources_t)



    def CalculateSubrects(self):
        for i in range(3, 13):
            width = 2 ** i
            height = 2 ** (i - 1)
            self.calculatedSubrects[(PD.DOLL_PARTS.HEAD, width)] = self.CalcSubRect(PD.HEAD_UVS, width, height)
            self.calculatedSubrects[(PD.DOLL_PARTS.HAIR, width)] = self.CalcSubRect(PD.HAIR_UVS, width, height)
            self.calculatedSubrects[(PD.DOLL_PARTS.BODY, width)] = self.CalcSubRect(PD.BODY_UVS, width, height)




    def GetSubRect(self, bodypart, w, h, modifier = None, uvs = None):
        key = (bodypart, w)
        subrect = self.calculatedSubrects.get(key)
        if subrect is None:
            if not uvs and modifier:
                uvs = modifier.GetUVsForCompositing(bodypart)
            if uvs:
                subrect = self.CalcSubRect(uvs, w, h)
        return subrect



    @bluepy.CCP_STATS_ZONE_METHOD
    def CalcSubRect(self, inputUV, w, h):
        return (int(w * inputUV[0]),
         int(h * inputUV[1]),
         int(w * inputUV[2]),
         int(h * inputUV[3]))



    def PreloadNudeResources_t(self):
        while not self.IsLoaded:
            blue.synchro.Yield()

        settingKey = 'preloadTextureToDeviceOnPrepare'
        originalSetting = trinity.settings.GetValue(settingKey)
        trinity.settings.SetValue(settingKey, False)
        for gender in PD.GENDER:
            if gender == PD.GENDER.FEMALE:
                basePath = PD.FEMALE_BASE_PATH
            else:
                basePath = PD.MALE_BASE_PATH
            for respath in PD.DEFAULT_NUDE_PARTS:
                path = '{0}/{1}'.format(basePath, respath)
                for (root, dirs, filenames,) in bluepy.walk(path):
                    for filename in filenames:
                        if '_4k' in filename:
                            continue
                        resource = blue.resMan.GetResource('{0}/{1}'.format(root, filename))
                        blue.synchro.Yield()
                        if resource and resource not in self.preloadedResources:
                            self.preloadedResources.append(resource)




        trinity.settings.SetValue(settingKey, originalSetting)



    def PreloadGenericHeadsOnceLoaded_t(self):
        while not self.IsLoaded:
            blue.synchro.Yield()

        self.PreloadedGenericHeadModifiers[PD.GENDER.MALE] = self.CollectBuildData('head/head_generic', self.GetOptionsByGender(PD.GENDER.MALE))
        self.PreloadedGenericHeadModifiers[PD.GENDER.FEMALE] = self.CollectBuildData('head/head_generic', self.GetOptionsByGender(PD.GENDER.FEMALE))



    @staticmethod
    @bluepy.CCP_STATS_ZONE_FUNCTION
    def PreloadShaders():
        if Factory.shaderPreload is not None:
            return 
        Factory.shaderPreload = []
        for path in PD.EFFECT_PRELOAD_PATHS:
            effect = trinity.Tr2Effect()
            effect.effectFilePath = 'res:/graphics/effect/managed/interior/avatar/' + path
            Factory.shaderPreload.append(effect)

        for path in PD.COMPOSITE_PRELOAD_PATHS:
            effect = trinity.Tr2Effect()
            effect.effectFilePath = 'res:/graphics/effect/utility/compositing/' + path
            Factory.shaderPreload.append(effect)

        Factory.texturePreload = []
        for path in PD.TEXTURE_PRELOAD_PATHS:
            texture = trinity.TriTexture2DParameter()
            texture.resourcePath = path
            Factory.texturePreload.append(texture)




    @staticmethod
    @bluepy.CCP_STATS_ZONE_FUNCTION
    def ApplyMorphTargetsToMeshes(meshes, morphTargets, blendShapeMeshCache = None, meshGeometryResPaths = None, doYield = True, clothMeshes = None, updateClothMeshes = True, avatar = None, clothMorphValues = None):
        clothMeshes = clothMeshes or []
        clothMorphValues = clothMorphValues if clothMorphValues is not None else {}
        blendShapeMeshCache = blendShapeMeshCache if blendShapeMeshCache is not None else {}
        loadingGrannyResources = {}
        blue.statistics.EnterZone('ApplyMorphTargetsToMeshes::meshAnalysis')
        meshGenerator = (mesh for mesh in meshes if not (blendShapeMeshCache.get(mesh.name) and blendShapeMeshCache.get(mesh.name)[1].isGood))
        for mesh in meshGenerator:
            index = mesh.meshIndex
            path = mesh.geometryResPath
            if not path and meshGeometryResPaths is not None:
                path = meshGeometryResPaths.get(mesh.name, None)
                if not path and mesh.name[-1].isdigit():
                    for meshName in meshGeometryResPaths:
                        if meshName.startswith(mesh.name[:-1]):
                            path = meshGeometryResPaths.get(meshName, None)
                            break

                    if not path and mesh.name[-2].isdigit:
                        for meshName in meshGeometryResPaths:
                            if meshName.startswith(mesh.name[:-2]):
                                path = meshGeometryResPaths.get(meshName, None)
                                break

            if not path:
                continue
            gr2 = path
            grannyResource = blue.resMan.GetResource(gr2, 'raw')
            loadingGrannyResources[mesh.name] = grannyResource

        blue.statistics.LeaveZone()
        blue.statistics.EnterZone('ApplyMorphTargetsToMeshes::loadYield')
        while doYield:
            doYield = False
            for lgr in loadingGrannyResources.itervalues():
                if lgr.isLoading:
                    doYield = True
                    break

            if doYield:
                try:
                    blue.synchro.Yield()
                except RuntimeError:
                    blue.pyos.BeNice()

        blue.statistics.LeaveZone()
        blue.statistics.EnterZone('ApplyMorphTargetsToMeshes::finalizeCache')
        if loadingGrannyResources:
            StripDigits = PD.StripDigits
            meshCount = len(meshes)
            for mIdx in xrange(meshCount):
                mesh = meshes[mIdx]
                grannyResource = loadingGrannyResources.get(mesh.name)
                index = mesh.meshIndex
                if grannyResource and grannyResource.isGood and grannyResource.meshCount > index:
                    geometryRes = grannyResource.CreateGeometryRes()
                    count = grannyResource.GetMeshMorphCount(index)
                    morphNames = []
                    for i in xrange(count):
                        name = grannyResource.GetMeshMorphName(index, i)
                        morphNames.append(StripDigits(name))

                    blendShapeMeshCache[mesh.name] = (grannyResource, geometryRes, morphNames)
                elif loadingGrannyResources.get(mesh.name):
                    del loadingGrannyResources[mesh.name]

        blue.statistics.LeaveZone()
        blue.statistics.EnterZone('ApplyMorphTargetsToMeshes::bakeBlendshape')
        meshGenerator = (mesh for mesh in meshes if blendShapeMeshCache.get(mesh.name))
        for mesh in meshGenerator:
            (grannyResource, geometryRes, morphNames,) = blendShapeMeshCache[mesh.name]
            weights = [ morphTargets.get(name, 0.0) for name in morphNames ]
            if len(weights) > 0 and grannyResource.BakeBlendshape(mesh.meshIndex, weights, geometryRes):
                if mesh.geometry != geometryRes:
                    mesh.SetGeometryRes(geometryRes)
            else:
                del blendShapeMeshCache[mesh.name]

        if updateClothMeshes:
            for cm in clothMeshes:
                Factory.ProcessBlendshapesForCloth(cm, morphTargets, avatar, clothMorphValues=clothMorphValues)

        blue.statistics.LeaveZone()



    @staticmethod
    @bluepy.CCP_STATS_ZONE_FUNCTION
    def ProcessBlendshapesForCloth(clothActor, morphTargets, avatar = None, clothMorphValues = None):
        clothMorphValues = clothMorphValues if clothMorphValues is not None else {}
        if clothActor.morphRes is None:
            clothActor.morphRes = blue.resMan.GetResource(clothActor.resPath.lower().replace('.apb', '_bs.gr2'), 'raw')
        while clothActor.morphRes.isLoading:
            blue.synchro.Yield()

        updateBlends = True
        if clothActor.morphRes.meshCount > 0:
            StripDigits = PD.StripDigits
            count = clothActor.morphRes.GetMeshMorphCount(clothActor.morphResMeshIndex)
            morphNames = []
            for i in xrange(count):
                name = clothActor.morphRes.GetMeshMorphName(clothActor.morphResMeshIndex, i)
                morphNames.append(StripDigits(name))

            weights = [ morphTargets.get(name, 0.0) for name in morphNames ]
            key = str(clothActor)
            if key in clothMorphValues and weights == clothMorphValues[key]:
                updateBlends = False
            else:
                clothMorphValues[key] = weights
            if updateBlends:
                clothActor.SetMorphResWeights(weights)
        else:
            updateBlends = False
        if avatar is not None and updateBlends:
            if clothActor in avatar.clothMeshes:
                avatar.clothMeshes.remove(clothActor)
                avatar.clothMeshes.append(clothActor)



    @bluepy.CCP_STATS_ZONE_METHOD
    def BindGlobalMaps(self, meshes):
        effects = []
        for mesh in iter(meshes):
            effects += PD.GetEffectsFromMesh(mesh)

        for each in iter(effects):
            if each is None:
                continue
            NdotLres = None
            FresnelLookupMapRes = None
            if type(each) != trinity.Tr2ShaderMaterial:
                for r in iter(each.resources):
                    if r.name == 'ColorNdotLLookupMap':
                        NdotLres = r
                    elif r.name == 'FresnelLookupMap':
                        FresnelLookupMapRes = r

            if NdotLres is None:
                res = trinity.TriTexture2DParameter()
                res.name = 'ColorNdotLLookupMap'
                res.resourcePath = 'res:/Texture/Global/NdotLLibrary.png'
                if type(each) == trinity.Tr2ShaderMaterial:
                    each.parameters[res.name] = res
                else:
                    each.resources.append(res)
            else:
                NdotLres.resourcePath = 'res:/Texture/Global/NdotLLibrary.png'
            if FresnelLookupMapRes is None:
                res = trinity.TriTexture2DParameter()
                res.name = 'FresnelLookupMap'
                res.resourcePath = PD.FRESNEL_LOOKUP_MAP
                if type(each) == trinity.Tr2ShaderMaterial:
                    each.parameters[res.name] = res
                else:
                    each.resources.append(res)
            else:
                FresnelLookupMapRes.resourcePath = PD.FRESNEL_LOOKUP_MAP




    @bluepy.CCP_STATS_ZONE_METHOD
    def ClearAllCachedMaps(self):
        cachePath = self.GetMapCachePath()
        fileSystemPath = blue.rot.PathToFilename(cachePath)
        for (root, dirs, files,) in os.walk(fileSystemPath):
            for f in iter(files):
                os.remove(os.path.join(root, f))





    def GetMapCachePath(self):
        avatarCachePath = u''
        try:
            userCacheFolder = blue.os.ResolvePath(u'cache:')
            avatarCachePath = u'{0}/{1}'.format(userCacheFolder, u'Avatars/cachedMaps')
        except Exception:
            avatarCachePath = u''
            sys.exc_clear()
        return avatarCachePath



    def GetCacheFilePath(self, cachePath, hashKey, textureWidth, mapType):
        cacheFilePath = u''
        try:
            hashKey = str(hashKey).replace('-', '_')
            cacheFilePath = u'{0}/{1}/{2}{3}.dds'.format(cachePath, textureWidth, mapType, hashKey)
        except Exception:
            cacheFilePath = u''
            sys.exc_clear()
        return cacheFilePath



    @bluepy.CCP_STATS_ZONE_METHOD
    def FindCachedTexture(self, hashKey, textureWidth, mapType):
        cachePath = self.GetMapCachePath()
        try:
            if cachePath:
                filePath = self.GetCacheFilePath(cachePath, hashKey, textureWidth, mapType)
                if filePath:
                    rf = blue.ResFile()
                    if rf.FileExists(filePath):
                        rotPath = blue.rot.FilenameToPath(filePath)
                        cachedTexture = blue.resMan.GetResourceW(rotPath)
                        return cachedTexture
        except Exception:
            sys.exc_clear()



    @bluepy.CCP_STATS_ZONE_METHOD
    def SaveMaps(self, hashKey, textureWidth, maps):
        cachePath = self.GetMapCachePath()
        if not cachePath:
            return 
        try:
            for (i, each,) in enumerate(maps):
                if each is not None:
                    filePath = self.GetCacheFilePath(cachePath, hashKey, textureWidth, i)
                    if filePath:
                        folder = os.path.split(filePath)[0]
                        try:
                            if not os.path.exists(folder):
                                os.makedirs(folder)
                            each.SaveToDDS(filePath)
                            each.WaitForSave()
                        except OSError:
                            pass

        except Exception:
            sys.exc_clear()



    @bluepy.CCP_STATS_ZONE_METHOD
    def _CreateBiped(self, avatar, geometryRes, name = 'FactoryCreated'):
        biped = trinity.Tr2SkinnedModel()
        biped.skinScale = (1.0, 1.0, 1.0)
        biped.name = name
        if geometryRes:
            biped.geometryResPath = geometryRes
        biped.skeletonName = 'Root'
        avatar.visualModel = biped
        avatar.scaling = (1.0, 1.0, 1.0)
        return avatar



    @bluepy.CCP_STATS_ZONE_METHOD
    def CreateVisualModel(self, gender = PD.GENDER.FEMALE, geometryRes = None):
        biped = trinity.Tr2SkinnedModel()
        if not geometryRes:
            if gender == PD.GENDER.FEMALE:
                geometryRes = PD.INTERIOR_FEMALE_GEOMETRY_RESPATH
            else:
                geometryRes = PD.INTERIOR_MALE_GEOMETRY_RESPATH
        biped.geometryResPath = geometryRes
        biped.name = gender
        biped.skeletonName = 'Root'
        return biped



    @bluepy.CCP_STATS_ZONE_METHOD
    def CreateAvatar(self, geometryRes, name = 'FactoryCreated'):
        avatar = trinity.WodExtSkinnedObject()
        avatar = self._CreateBiped(avatar, geometryRes, name)
        return avatar



    @bluepy.CCP_STATS_ZONE_METHOD
    def CreateInteriorAvatar(self, geometryRes, name = 'FactoryCreated'):
        avatar = trinity.Tr2IntSkinnedObject()
        avatar = self._CreateBiped(avatar, geometryRes, name)
        return avatar



    @bluepy.CCP_STATS_ZONE_METHOD
    def RemoveAvatarFromScene(self, avatar, scene):
        if avatar is None or scene is None:
            return 
        try:
            scene.RemoveDynamic(avatar)
        except AttributeError:
            scene.Avatar = None
            sys.exc_clear()



    @bluepy.CCP_STATS_ZONE_METHOD
    def AddAvatarToScene(self, avatar, scene = None):
        if avatar is None:
            raise AttributeError('No avatar passed to Factory::AddAvatarToScene')
        if scene is not None:
            if hasattr(scene, 'Avatar'):
                scene.Avatar = avatar
                return 
            scene.AddDynamic(avatar)
            return 
        dev = trinity.device
        if dev.scene2:
            dev.scene2.AddDynamic(avatar)
        else:
            dev.scene2 = trinity.Tr2InteriorScene()
            dev.scene2.AddDynamic(avatar)



    @bluepy.CCP_STATS_ZONE_METHOD
    def CreateGWAnimation(self, avatar, morphemeNetwork):
        import GameWorld
        animation = GameWorld.GWAnimation(morphemeNetwork)
        avatar.animationUpdater = animation
        return animation



    @bluepy.CCP_STATS_ZONE_METHOD
    def CreateAnimationOffsets(self, avatar, doll):
        if avatar.animationUpdater and getattr(avatar.animationUpdater, 'network', None):
            if doll.boneOffsets:
                for bone in doll.boneOffsets:
                    trans = doll.boneOffsets[bone][PD.TRANSLATION]
                    avatar.animationUpdater.network.boneOffset.SetOffset(bone, trans[0], trans[1], trans[2])




    @bluepy.CCP_STATS_ZONE_METHOD
    def CompositeStepsFunction(self, buildDataManager, gender, mapType, partsToComposite, comp, w, h, lod = None):
        genericHeadMod = self.PreloadedGenericHeadModifiers.get(gender)
        modifierList = [ modifier for modifier in buildDataManager.GetSortedModifiers() if modifier.IsTextureContainingModifier() and modifier.weight > 0 if modifier.categorie != PD.HEAD_CATEGORIES.HEAD ]
        if mapType == PD.DIFFUSE_MAP:
            genTex = genericHeadMod.mapD
        elif mapType == PD.SPECULAR_MAP:
            genTex = genericHeadMod.mapSRG
        elif mapType == PD.NORMAL_MAP:
            genTex = genericHeadMod.mapN
        elif mapType == PD.MASK_MAP:
            genTex = genericHeadMod.mapMask
        if not partsToComposite or PD.DOLL_PARTS.BODY in partsToComposite:
            baseBodyTexture = genTex.get(PD.DOLL_PARTS.BODY, '')
            if baseBodyTexture:
                comp.CopyBlitTexture(baseBodyTexture, self.GetSubRect(PD.DOLL_PARTS.BODY, w, h))
            self._CompositeTexture(modifierList, PD.DOLL_PARTS.BODY, comp, mapType, w, h, addAlpha=True, lod=lod)
        if not partsToComposite or PD.DOLL_PARTS.HEAD in partsToComposite or PD.DOLL_PARTS.HAIR in partsToComposite:
            baseHeadTexture = genTex.get(PD.DOLL_PARTS.HEAD, '')
            if baseHeadTexture:
                comp.CopyBlitTexture(baseHeadTexture, self.GetSubRect(PD.DOLL_PARTS.HEAD, w, h))
            self._CompositeTexture(modifierList, PD.DOLL_PARTS.HEAD, comp, mapType, w, h, addAlpha=False, lod=lod)
        if not partsToComposite or PD.DOLL_PARTS.HAIR in partsToComposite:
            self._CompositeTexture(modifierList, PD.DOLL_PARTS.HAIR, comp, mapType, w, h, addAlpha=False, lod=lod)
        if not partsToComposite or PD.DOLL_PARTS.ACCESSORIES in partsToComposite:
            self._CompositeTexture(modifierList, PD.DOLL_PARTS.ACCESSORIES, comp, mapType, w, h, addAlpha=False, lod=lod)



    @bluepy.CCP_STATS_ZONE_METHOD
    def CompositeCombinedTexture(self, dollName, mapType, gender, buildDataManager, mapBundle, compressionSettings = None, textureCompositor = None, partsToComposite = None, copyToExistingTexture = False, lod = None):
        try:
            if compressionSettings is None:
                compressionSettings = self
            textureFormat = trinity.TRIFMT_A8R8G8B8
            (w, h,) = mapBundle.GetResolutionByMapType(mapType)
            renderTarget = RTM.GetRenderTarget(textureFormat, w, h)
            if renderTarget.width < w:
                log.LogWarn('PaperDoll:Factory:CompositeCombinedTexture - RenderTarget width less than requested due to low video memory.')
            w = renderTarget.width
            h = renderTarget.height
            if textureCompositor is None:
                comp = tc.TextureCompositor(renderTarget, targetWidth=w)
            else:
                comp = textureCompositor
            comp.Start(clear=False)
            if mapBundle[mapType]:
                comp.CopyBlitTexture(mapBundle[mapType])
            self.CompositeStepsFunction(buildDataManager, gender, mapType, partsToComposite, comp, w, h, lod=lod)
            comp.End()
            while not comp.isReady:
                blue.synchro.Yield()

            if copyToExistingTexture:
                tex = comp.Finalize(textureFormat, w, h, generateMipmap=compressionSettings.generateMipmap, textureToCopyTo=mapBundle[mapType])
            else:
                tex = comp.Finalize(textureFormat, w, h, generateMipmap=compressionSettings.generateMipmap)
            comp.renderTarget = None
            compressedTexture = Factory.ApplyCompressionSettingToTexture(compressionSettings, tex, mapType)
            if compressedTexture:
                tex = compressedTexture
            if self.saveTexturesToDisk:
                AddMarker('save')
                cachePath = blue.rot.PathToFilename('cache:/Avatars/' + dollName)
                if not os.path.exists(cachePath):
                    os.makedirs(cachePath)
                tex.SaveToDDS(cachePath + '/' + '/comp' + marker + '.dds')
                tex.WaitForSave()
                AddMarker('save done')
            return tex
        except TaskletExit:
            if textureCompositor:
                textureCompositor.renderTarget = None



    @staticmethod
    def ApplyCompressionSettingToTexture(compressionSettings, tex, mapType):
        compressedTexture = None
        isPC = not blue.win32.IsTransgaming()
        if compressionSettings.compressTextures and compressionSettings.AllowCompress(mapType) and isPC:
            compressedTexture = Factory.PerformTextureCompression(tex, mapType, compressionSettings.qualityLevel)
        return compressedTexture



    @staticmethod
    def PerformTextureCompression(tex, mapType, qualityLevel = trinity.TR2DXT_COMPRESS_SQ_RANGE_FIT):
        AddMarker('compress')
        compressedTexture = trinity.device.CreateTexture(tex.width, tex.height, 1, 0, trinity.TRIFMT_DXT5, trinity.TRIPOOL_MANAGED)
        compressionFormat = COMPRESS_DXT5n if mapType is PD.NORMAL_MAP else COMPRESS_DXT5
        try:
            trinity.device.CompressSurfaceWithQuality(tex.GetSurfaceLevel(0), compressedTexture.GetSurfaceLevel(0), compressionFormat, qualityLevel)
        except TaskletExit:
            raise 
        AddMarker('compress done')
        return compressedTexture



    @bluepy.CCP_STATS_ZONE_METHOD
    def _CompositeDiffuseMap(self, modifierList, bodyPart, textureCompositor, width, height, addAlpha = False, lod = 0):
        for m in iter(modifierList):
            if m.stubblePath and lod < 0:
                continue
            subrect = self.GetSubRect(bodyPart, width, height, m)
            srcRect = None
            texture = m.mapD
            skipAlpha = False
            useAlphaTest = False
            if m.colorize and bodyPart in m.mapL:
                if bodyPart not in m.mapO:
                    m.mapO[bodyPart] = 'res:/texture/global/stub.dds'
                if bodyPart not in m.mapZ:
                    m.mapZ[bodyPart] = 'res:/texture/global/stub.dds'
                if m.categorie in (PD.BODY_CATEGORIES.SKINTONE,
                 PD.HEAD_CATEGORIES.MAKEUP,
                 PD.BODY_CATEGORIES.TATTOO,
                 PD.BODY_CATEGORIES.SCARS,
                 PD.DOLL_EXTRA_PARTS.BODYSHAPES,
                 PD.HEAD_CATEGORIES.FACEMODIFIERS):
                    if 'implants/' in m.name:
                        skipAlpha = False
                        addAlpha = True
                    elif 'eyelashes/' in m.name or 'eyebrows/' in m.name:
                        skipAlpha = False
                        addAlpha = True
                        useAlphaTest = True
                    else:
                        skipAlpha = True
                        addAlpha = True
                if m.categorie == PD.DOLL_PARTS.HAIR and bodyPart == PD.DOLL_PARTS.HEAD:
                    skipAlpha = False
                    addAlpha = True
                if m.pattern == '':
                    colors = m.colorizeData
                    if bodyPart == PD.DOLL_PARTS.HAIR:
                        textureCompositor.ColorizedCopyBlitTexture(m.mapL[bodyPart], m.mapZ[bodyPart], m.mapO[bodyPart], colors[0], colors[1], colors[2], subrect)
                    else:
                        textureCompositor.ColorizedBlitTexture(m.mapL[bodyPart], m.mapZ[bodyPart], m.mapO[bodyPart], colors[0], colors[1], colors[2], subrect=subrect, addAlpha=addAlpha, skipAlpha=skipAlpha, useAlphaTest=useAlphaTest, weight=m.weight)
                else:
                    colors = m.patternData
                    patternDir = self.GetPatternDir()
                    patternPath = patternDir + '/' + m.pattern + '_z.dds'
                    if blue.rot.loadFromContent:
                        if not os.path.exists(PD.OUTSOURCING_JESSICA_PATH):
                            patternPath = patternPath.replace('.dds', '.tga')
                    textureCompositor.PatternBlitTexture(patternPath, m.mapL[bodyPart], m.mapZ[bodyPart], m.mapO[bodyPart], colors[0], colors[1], colors[2], colors[3], colors[4], subrect, patternTransform=colors[5], patternRotation=colors[6], addAlpha=addAlpha, skipAlpha=skipAlpha)
            if bodyPart in texture and not (m.colorize and m.categorie == PD.BODY_CATEGORIES.TATTOO):
                maskname = tname = texture[bodyPart]
                if not (type(tname) in types.StringTypes and '/skin/generic/' in tname.lower()):
                    if bodyPart in texture:
                        maskname = texture[bodyPart]
                    elif bodyPart in m.mapL:
                        maskname = m.mapL[bodyPart]
                    skipAlpha = False
                    if m.categorie in (PD.BODY_CATEGORIES.SKINTONE,
                     PD.HEAD_CATEGORIES.MAKEUP,
                     PD.BODY_CATEGORIES.TATTOO,
                     PD.BODY_CATEGORIES.SCARS,
                     PD.DOLL_EXTRA_PARTS.BODYSHAPES,
                     PD.HEAD_CATEGORIES.ARCHETYPES,
                     PD.HEAD_CATEGORIES.FACEMODIFIERS):
                        if 'eyelashes/' in m.name:
                            skipAlpha = False
                            addAlpha = False
                        else:
                            skipAlpha = True
                            addAlpha = True
                    if m.categorie == PD.DOLL_PARTS.HAIR and bodyPart == PD.DOLL_PARTS.HEAD:
                        skipAlpha = False
                        addAlpha = True
                    if bodyPart == PD.DOLL_PARTS.HAIR:
                        textureCompositor.CopyBlitTexture(tname, subrect=subrect, srcRect=srcRect)
                    else:
                        textureCompositor.BlitTexture(tname, maskname, m.weight, subrect=subrect, addAlpha=addAlpha, skipAlpha=skipAlpha, srcRect=srcRect, multAlpha=False)




    @bluepy.CCP_STATS_ZONE_METHOD
    def _CompositeSpecularMap(self, modifierList, bodyPart, textureCompositor, width, height, addAlpha = False, lod = 0):
        for m in iter(modifierList):
            if m.stubblePath and lod < 0:
                continue
            subrect = self.GetSubRect(bodyPart, width, height, m)
            srcRect = None
            skipAlpha = False
            maskname = tname = m.mapSRG.get(bodyPart)
            if bodyPart in m.mapSRG and not (m.categorie == PD.BODY_CATEGORIES.TATTOO or type(tname) in types.StringTypes and '/skin/generic/' in tname.lower()):
                if bodyPart in m.mapD:
                    maskname = m.mapD[bodyPart]
                elif bodyPart in m.mapL:
                    maskname = m.mapL[bodyPart]
                skipAlpha = True
                addAlpha = True
                if m.useSkin:
                    tname = tname.replace('_S.', '_SR.')
                doColorizedStep = False
                if m.colorize and m.specularColorData:
                    doColorizedStep = bodyPart in m.mapL
                    if bodyPart == PD.DOLL_PARTS.HAIR:
                        textureCompositor.CopyBlitTexture(tname, subrect=subrect, srcRect=srcRect)
                        doColorizedStep = True
                    if doColorizedStep:
                        if bodyPart not in m.mapO:
                            m.mapO[bodyPart] = 'res:/texture/global/stub.dds'
                        if bodyPart not in m.mapZ:
                            m.mapZ[bodyPart] = 'res:/texture/global/stub.dds'
                        colors = m.specularColorData
                        textureCompositor.ColorizedBlitTexture(m.mapSRG[bodyPart], m.mapZ[bodyPart], m.mapO[bodyPart], colors[0], colors[1], colors[2], mask=maskname, subrect=subrect, addAlpha=addAlpha, skipAlpha=skipAlpha, weight=m.weight)
                if not doColorizedStep:
                    textureCompositor.BlitTexture(tname, maskname, m.weight, subrect=subrect, addAlpha=addAlpha, skipAlpha=skipAlpha, srcRect=srcRect, multAlpha=False)
                if m.colorize and m.specularColorData and bodyPart in m.mapZ:
                    values = (m.specularColorData[0][3],
                     m.specularColorData[1][3],
                     m.specularColorData[2][3],
                     1.0)
                    textureCompositor.BlitAlphaIntoAlphaWithMaskAndZones(tname, maskname, m.mapZ[bodyPart], values, subrect=subrect, srcRect=srcRect)
                else:
                    textureCompositor.BlitAlphaIntoAlphaWithMask(tname, maskname, subrect=subrect, srcRect=srcRect)




    @bluepy.CCP_STATS_ZONE_METHOD
    def _CompositeNormalMap(self, modifierList, bodyPart, textureCompositor, width, height, addAlpha = False, lod = None):
        for m in iter(modifierList):
            if m.categorie == PD.DOLL_EXTRA_PARTS.BODYSHAPES and lod in (1, 2):
                continue
            texture = m.mapN
            subrect = self.GetSubRect(bodyPart, width, height, m)
            srcRect = None
            skipAlpha = False
            if bodyPart in texture and m.respath != 'skin/generic':
                maskname = tname = texture[bodyPart]
                if bodyPart in m.mapD:
                    maskname = m.mapD[bodyPart]
                elif bodyPart in m.mapL:
                    maskname = m.mapL[bodyPart]
                skipAlpha = False
                if m.categorie in (PD.BODY_CATEGORIES.SKINTONE,
                 PD.HEAD_CATEGORIES.MAKEUP,
                 PD.BODY_CATEGORIES.TATTOO,
                 PD.BODY_CATEGORIES.SCARS,
                 PD.DOLL_EXTRA_PARTS.BODYSHAPES,
                 PD.HEAD_CATEGORIES.ARCHETYPES,
                 PD.HEAD_CATEGORIES.FACEMODIFIERS):
                    skipAlpha = True
                    addAlpha = True
                elif m.categorie == PD.DOLL_PARTS.HAIR and bodyPart == PD.DOLL_PARTS.HEAD:
                    skipAlpha = False
                    addAlpha = True
                if bodyPart == PD.DOLL_PARTS.HAIR:
                    textureCompositor.CopyBlitTexture(tname, subrect=subrect, srcRect=srcRect, isNormalMap=True)
                else:
                    textureCompositor.BlitTexture(tname, maskname, m.weight, subrect=subrect, addAlpha=addAlpha, skipAlpha=skipAlpha, srcRect=srcRect, multAlpha=False, isNormalMap=True)
            mapD = m.mapD.get(bodyPart)
            mapMN = m.mapMN.get(bodyPart)
            mapTN = m.mapTN.get(bodyPart)
            if mapMN:
                textureCompositor.MaskedNormalBlitTexture(mapMN, m.weight, subrect, srcRect=srcRect)
            if mapTN:
                textureCompositor.TwistNormalBlitTexture(mapTN, m.weight, subrect, srcRect=srcRect)
            if mapD and m.categorie not in (PD.BODY_CATEGORIES.SKINTONE,
             PD.BODY_CATEGORIES.TATTOO,
             PD.BODY_CATEGORIES.SCARS,
             PD.DOLL_EXTRA_PARTS.BODYSHAPES,
             PD.HEAD_CATEGORIES.ARCHETYPES,
             PD.HEAD_CATEGORIES.FACEMODIFIERS):
                if m.categorie in PD.CATEGORIES_THATCLEAN_MATERIALMAP:
                    textureCompositor.SubtractAlphaFromAlpha(mapD, subrect, srcRect=srcRect)
                mapMM = m.mapMaterial.get(bodyPart)
                if mapMM is not None:
                    textureCompositor.BlitTextureIntoAlphaWithMask(mapMM, mapD, subrect, srcRect=srcRect)
                else:
                    textureCompositor.BlitTextureIntoAlphaWithMask(mapD, mapD, subrect, srcRect=srcRect)




    @bluepy.CCP_STATS_ZONE_METHOD
    def _CompositeMaskMap(self, modifierList, bodyPart, textureCompositor, width, height, addAlpha = False, lod = None):
        for m in iter(modifierList):
            texture = m.mapMask
            subrect = self.GetSubRect(bodyPart, width, height, m)
            srcRect = None
            skipAlpha = False
            if bodyPart in texture:
                tname = texture[bodyPart].lower()
                textureCompositor.CopyBlitTexture(tname, subrect)
                maskname = tname = texture[bodyPart]
                if not (type(tname) in types.StringTypes and '/skin/generic/' in tname.lower()):
                    if bodyPart in m.mapD:
                        maskname = m.mapD[bodyPart]
                    elif bodyPart in m.mapL:
                        maskname = m.mapL[bodyPart]
                    skipAlpha = False
                    if m.categorie in (PD.BODY_CATEGORIES.SKINTONE,
                     PD.HEAD_CATEGORIES.MAKEUP,
                     PD.BODY_CATEGORIES.TATTOO,
                     PD.BODY_CATEGORIES.SCARS,
                     PD.DOLL_EXTRA_PARTS.BODYSHAPES,
                     PD.HEAD_CATEGORIES.ARCHETYPES,
                     PD.HEAD_CATEGORIES.FACEMODIFIERS):
                        skipAlpha = True
                        addAlpha = True
                    if m.categorie == PD.DOLL_PARTS.HAIR and bodyPart == PD.DOLL_PARTS.HEAD:
                        skipAlpha = False
                        addAlpha = True
                    textureCompositor.BlitTexture(tname, maskname, m.weight, subrect=subrect, addAlpha=addAlpha, skipAlpha=skipAlpha, srcRect=srcRect, multAlpha=False)




    @bluepy.CCP_STATS_ZONE_METHOD
    def _CompositeTexture(self, modifierList, bodyPart, textureCompositor, textureType, width, height, addAlpha = False, lod = None):
        partSpecificModifierGenerator = (m for m in modifierList if bodyPart in m.GetAffectedTextureParts())
        if textureType == PD.DIFFUSE_MAP:
            return self._CompositeDiffuseMap(partSpecificModifierGenerator, bodyPart, textureCompositor, width, height, addAlpha, lod)
        if textureType == PD.SPECULAR_MAP:
            return self._CompositeSpecularMap(partSpecificModifierGenerator, bodyPart, textureCompositor, width, height, addAlpha, lod)
        if textureType == PD.NORMAL_MAP:
            return self._CompositeNormalMap(partSpecificModifierGenerator, bodyPart, textureCompositor, width, height, addAlpha, lod)
        if textureType == PD.MASK_MAP:
            return self._CompositeMaskMap(partSpecificModifierGenerator, bodyPart, textureCompositor, width, height, addAlpha, lod)
        raise ValueError('Paperdoll::Unsupported texturetype passed to compositing')



    @staticmethod
    @bluepy.CCP_STATS_ZONE_FUNCTION
    def SetResourceTexture(effectResource, texture):
        if isinstance(texture, str):
            if effectResource.resourcePath != texture:
                effectResource.resourcePath = texture
        else:
            effectResource.resourcePath = ''
            effectResource.SetResource(texture)



    @staticmethod
    @bluepy.CCP_STATS_ZONE_FUNCTION
    def BindCompositeTexturesToMeshes(meshes, mapBundle):
        for mesh in iter(meshes):
            effects = PD.GetEffectsFromMesh(mesh)
            for f in iter(effects):
                if type(f) != trinity.Tr2ShaderMaterial:
                    for r in iter(f.resources):
                        if mapBundle.diffuseMap and r.name == PD.MAPNAMES[PD.DIFFUSE_MAP]:
                            Factory.SetResourceTexture(r, mapBundle.diffuseMap)
                        elif mapBundle.specularMap and r.name == PD.MAPNAMES[PD.SPECULAR_MAP]:
                            Factory.SetResourceTexture(r, mapBundle.specularMap)
                        elif mapBundle.normalMap and r.name == PD.MAPNAMES[PD.NORMAL_MAP]:
                            Factory.SetResourceTexture(r, mapBundle.normalMap)
                        elif mapBundle.maskMap and r.name == PD.MAPNAMES[PD.MASK_MAP]:
                            Factory.SetResourceTexture(r, mapBundle.maskMap)

                else:
                    if mapBundle.diffuseMap:
                        f.parameters[PD.MAPNAMES[PD.DIFFUSE_MAP]] = mapBundle.diffuseMap
                    if mapBundle.specularMap:
                        f.parameters[PD.MAPNAMES[PD.SPECULAR_MAP]] = mapBundle.specularMap
                    if mapBundle.normalMap:
                        f.parameters[PD.MAPNAMES[PD.NORMAL_MAP]] = mapBundle.normalMap
                    if mapBundle.maskMap:
                        f.parameters[PD.MAPNAMES[PD.MASK_MAP]] = mapBundle.maskMap





    @bluepy.CCP_STATS_ZONE_METHOD
    def BuildMeshForAvatar(self, avatar, avatarName, buildSources, createDynamicLOD = False, bodyShapesActive = {}, overrideLod = 0, weldthreshold = 1e-09, meshName = 'mesh', addMesh = False, asyncLOD = False):
        builder = trinity.WodAvatar2Builder()
        avatarName = str(avatarName)
        if asyncLOD:
            builder.createGPUMesh = True
            builder.effectPath = 'res:/Graphics/Effect/Managed/Interior/Avatar/SkinnedAvatarBRDFDouble.fx'
            if overrideLod == 2:
                weldthreshold = 0
        for each in iter(buildSources):
            builder.sourceMeshesInfo.append(each)

        realBsNames = {}
        realBsNames['fatshape'] = 'FatShape'
        realBsNames['thinshape'] = 'ThinShape'
        realBsNames['muscularshape'] = 'MuscularShape'
        realBsNames['softshape'] = 'SoftShape'
        if bodyShapesActive:
            for bs in bodyShapesActive:
                for suffix in ['',
                 '1',
                 '2',
                 '3',
                 '4',
                 '5',
                 '6']:
                    blendshape1 = trinity.WodAvatar2BuilderBlend()
                    if bs in realBsNames:
                        blendshape1.name = realBsNames[bs] + suffix
                    else:
                        blendshape1.name = bs + suffix
                    blendshape1.power = bodyShapesActive[bs]
                    builder.blendshapeInfo.append(blendshape1)


        cachePath = blue.rot.PathToFilename('cache:/Avatars/' + avatarName)
        if not os.path.exists(cachePath):
            os.makedirs(cachePath)
        builder.outputName = str('cache:/Avatars/' + avatarName + '/' + meshName + '.gr2')
        builder.weldThreshold = weldthreshold

        class BuildEvent:

            def __init__(self):
                self.isDone = False
                self.succeeded = False



            def __call__(self, success):
                self.isDone = True
                self.succeeded = success



            def Wait(self):
                while not self.isDone:
                    blue.pyos.synchro.Yield()





        def BuildSkinnedModel(avatarBuilder, lod):
            avatarBuilder.lod = lod
            avatarBuilder.PrepareForBuild()
            evt = BuildEvent()
            avatarBuilder.BuildAsync(evt)
            evt.Wait()
            if not evt.succeeded:
                return None
            ret = avatarBuilder.GetSkinnedModel()
            return ret


        if asyncLOD:
            return BuildSkinnedModel(builder, overrideLod)



    @bluepy.CCP_STATS_ZONE_METHOD
    def RemoveMeshesFromVisualModel(self, visualModel, ignoreMeshes = None):
        if ignoreMeshes:
            remIdxs = []
            vmMeshCount = len(visualModel.meshes)
            for i in xrange(vmMeshCount):
                if visualModel.meshes[i] not in ignoreMeshes:
                    remIdxs.insert(0, i)

            for i in remIdxs:
                del visualModel.meshes[i]

        else:
            del visualModel.meshes[:]



    @bluepy.CCP_STATS_ZONE_METHOD
    def AppendMeshesToVisualModel(self, visualModel, meshes):
        for mesh in iter(meshes):
            if type(mesh) is trinity.Tr2Mesh and mesh not in visualModel.meshes:
                visualModel.meshes.append(mesh)




    @bluepy.CCP_STATS_ZONE_METHOD
    def RemoveMeshesFromVisualModelByCategory(self, visualModel, category):
        remList = []
        for each in iter(visualModel.meshes):
            if each.name.startswith(category):
                remList.append(each)

        for each in iter(remList):
            visualModel.meshes.remove(each)




    @bluepy.CCP_STATS_ZONE_METHOD
    def ReplaceMeshesOnAvatar(self, visualModel, meshes):
        remList = []
        for each in iter(meshes):
            for every in iter(visualModel.meshes):
                if every.name == each.name:
                    remList.append(every)


        for each in iter(remList):
            visualModel.meshes.remove(each)

        self.AppendMeshesToVisualModel(visualModel, meshes)



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetDNAFromYamlFile(self, filename):
        resFile = blue.ResFile()
        if resFile.FileExists(filename):
            resFile.Open(filename)
            yamlStr = resFile.Read()
            resFile.Close()
            if len(yamlStr) == 0:
                raise Exception('PaperDoll::Factory::GetDNAFromYamlFile - Error, loading an empty file!')
            dna = PD.NastyYamlLoad(yamlStr)
            return dna
        raise Exception('No %s file found' % filename)




class RedundantUpdateException(Exception):
    __guid__ = 'paperDoll.RedundantUpdateException'


class KillUpdateException(Exception):
    __guid__ = 'paperDoll.KillUpdateException'


class Doll(object):
    __metaclass__ = bluepy.CCP_STATS_ZONE_PER_METHOD
    __guid__ = 'paperDoll.Doll'
    _Doll__nextInstanceID = -1

    @staticmethod
    def GetInstanceID():
        Doll._Doll__nextInstanceID += 1
        return Doll._Doll__nextInstanceID



    @staticmethod
    def InstanceEquals(dollA, dollB):
        return dollA.instanceID == dollB.instanceID



    def __init__(self, name, gender = PD.GENDER.FEMALE):
        object.__init__(self)
        self.instanceID = Doll.GetInstanceID()
        self.mapBundle = MapBundle()
        self.compressionSettings = None
        self._Doll__quitRequested = False
        self.hasDelayedUpdateCallPending = False
        self.onUpdateDoneListeners = []
        self.name = name
        self.buildDataManager = PD.BuildDataManager()
        self.UVs = {PD.DOLL_PARTS.HEAD: PD.DEFAULT_UVS,
         PD.DOLL_PARTS.BODY: PD.DEFAULT_UVS,
         PD.DOLL_PARTS.HAIR: PD.DEFAULT_UVS,
         PD.DOLL_PARTS.ACCESSORIES: PD.DEFAULT_UVS}
        self.morphsLoaded = False
        self.isOptimized = False
        self.hasUpdatedOnce = False
        self.currentLOD = 0
        self.previousLOD = 0
        self.usePrepass = False
        self.avatarType = 'interior'
        self.gender = gender
        self.busyBaking = False
        self.busyLoadingDNA = False
        self.busyHandlingBlendshapes = False
        self.lastUpdateRedundant = False
        self.hairColorizeData = []
        self.boneOffsets = {}
        self.bindPose = None
        self.skinLightmapRenderer = None
        self.modifierLimits = {}
        self.textureCompositor = None
        self._Doll__updateFrameStamp = -1
        self._Doll__useFastShader = False
        self._currentUpdateTasklet = None
        self._UpdateTaskletChildren = []
        self.decalBaker = None
        trinity.device.RegisterResource(self)
        self.deviceResetAvatar = None
        self.useMaskedShaders = False
        self.useHeroHead = False
        self.useDXT5N = False
        self.blendShapeMeshCache = {}
        self.lodsInSeparateFolder = False
        if hasattr(const, 'PAPERDOLL_LODS_IN_SEPARATE_FOLDER'):
            self.lodsInSeparateFolder = const.PAPERDOLL_LODS_IN_SEPARATE_FOLDER
        self.tempClothMeshes = []
        self.tempClothCache = {}
        self.clothMorphValues = {}



    def __del__(self):
        self.StopPaperDolling()
        self.skinLightmapRenderer = None



    def GetName(self):
        return self.name



    def GetProjectedDecals(self):
        modifiers = self.buildDataManager.GetModifiersByCategory(PD.BODY_CATEGORIES.TATTOO)
        modifiers = [ modifier for modifier in modifiers if modifier.decalData ]
        return modifiers



    def AddBlendshapeLimitsFromFile(self, resPath):
        data = PD.ModifierLoader.LoadBlendshapeLimits(resPath)
        if data and data.get('gender') == self.gender:
            limits = data['limits']
            self.AddModifierLimits(limits)



    def AddModifierLimits(self, modifierLimits):
        self.modifierLimits.update(modifierLimits)



    def OnInvalidate(self, level):
        if self.skinLightmapRenderer is not None:
            self.skinLightmapRenderer.StopRendering()
            self.deviceResetAvatar = self.skinLightmapRenderer.skinnedObject
            del self.skinLightmapRenderer
            self.skinLightmapRenderer = None



    def OnCreate(self, dev):
        if self.currentLOD <= PD.LOD_SCATTER_SKIN:

            def skinCreate_t():
                if self.skinLightmapRenderer is None:
                    self.skinLightmapRenderer = PD.SkinLightmapRenderer(useOptix=self.currentLOD == PD.LOD_RAYTRACE)
                self.skinLightmapRenderer.SetSkinnedObject(self.deviceResetAvatar)
                self.skinLightmapRenderer.StartRendering()
                self.deviceResetAvatar = None


            t = uthread.new(skinCreate_t)
            uthread.schedule(t)



    def StopPaperDolling(self):
        for each in self.buildDataManager.GetModifiersAsList():
            each.ClearCachedData()

        self.mapBundle.ReCreate()



    def SetUsePrepass(self, val = True):
        self.usePrepass = val



    def IsPrepass(self):
        if self.usePrepass:
            return True
        return False



    def GetMorphsFromGr2(self, gr2Path):
        names = {}
        resMan = blue.resMan
        gr2Res = resMan.GetResource(gr2Path, 'raw')
        while gr2Res.isLoading:
            blue.synchro.Yield()

        meshCount = gr2Res.GetMeshCount()
        for i in xrange(meshCount):
            morphCount = gr2Res.GetMeshMorphCount(i)
            for j in xrange(morphCount):
                name = gr2Res.GetMeshMorphName(i, j)
                data = names.get(i, [])
                data.append(name)
                names[i] = data


        return (gr2Res, names)



    def _AnalyzeBuildDataForRules(self, updateRuleBundle, buildDataManager):
        modifierList = buildDataManager.GetSortedModifiers()
        forcesLooseTop = False
        hidesBootShin = False
        useMaskedShaders = False
        for modifier in iter(modifierList):
            useMaskedShaders = useMaskedShaders or modifier.categorie == PD.BODY_CATEGORIES.OUTER and len(modifier.mapMask) > 0
            metaData = modifier.metaData
            if metaData:
                forcesLooseTop = forcesLooseTop or metaData.forcesLooseTop
                hidesBootShin = hidesBootShin or metaData.hidesBootShin

        if not useMaskedShaders and self.useMaskedShaders:
            updateRuleBundle.undoMaskedShaders = True
        if hidesBootShin:
            buildDataManager.ChangeDesiredOrder(PD.BODY_CATEGORIES.FEET, PD.BODY_CATEGORIES.BOTTOMOUTER)
        else:
            buildDataManager.ChangeDesiredOrder(PD.BODY_CATEGORIES.BOTTOMOUTER, PD.BODY_CATEGORIES.FEET)
        if forcesLooseTop:
            buildDataManager.ChangeDesiredOrder(PD.BODY_CATEGORIES.TOPMIDDLE, PD.BODY_CATEGORIES.BOTTOMOUTER)
        else:
            buildDataManager.ChangeDesiredOrder(PD.BODY_CATEGORIES.BOTTOMOUTER, PD.BODY_CATEGORIES.TOPMIDDLE)
        self.useMaskedShaders = useMaskedShaders
        self.useHeroHead = self.currentLOD == PD.LOD_HERO
        updateRuleBundle.forcesLooseTop = forcesLooseTop
        updateRuleBundle.hidesBootShin = hidesBootShin



    def GetLODPathsToReplace(self):
        nonLodFolder = '/modular/'
        lodFolder = '/modularlod/'
        if PD.GENDER_ROOT:
            nonLodFolder = '/paperdoll/'
            lodFolder = '/paperdoll_lod/'
        return (nonLodFolder, lodFolder)



    def AdjustGr2PathForLod(self, gr2Path):
        (nonLodFolder, lodFolder,) = self.GetLODPathsToReplace()
        gr2Path = gr2Path.lower()
        originalgr2Path = gr2Path
        gr2PathWithoutExtension = gr2Path.split('.')[0]
        resfile = blue.ResFile()
        lodInPath = '_lod' in gr2Path and not gr2PathWithoutExtension.endswith('0')
        lodsInSeparateFolder = self.lodsInSeparateFolder
        if self.currentLOD > 0:
            if lodInPath:
                gr2Path = '{0}{1}.gr2'.format(gr2PathWithoutExtension[:-1], self.currentLOD)
            else:
                gr2Path = gr2Path.replace('.gr2', '_lod{0}.gr2'.format(self.currentLOD))
            if lodsInSeparateFolder:
                gr2Path = gr2Path.replace(nonLodFolder, lodFolder)
        elif self.currentLOD == 0:
            overridePath = ''
            if lodInPath:
                overridePath = '{0}a.gr2'.format(gr2PathWithoutExtension.replace(nonLodFolder, lodFolder)[:-1])
            else:
                overridePath = gr2Path.replace(nonLodFolder, lodFolder).replace('.gr2', '_loda.gr2')
            if resfile.FileExists(overridePath):
                gr2Path = overridePath
            else:
                if lodInPath:
                    gr2Path = '{0}.gr2'.format(gr2PathWithoutExtension[:-5])
                if lodsInSeparateFolder:
                    gr2Path = gr2Path.replace(lodFolder, nonLodFolder)
        elif lodInPath:
            gr2Path = '{0}.gr2'.format(gr2PathWithoutExtension[:-5])
        if lodsInSeparateFolder:
            gr2Path = gr2Path.replace(lodFolder, nonLodFolder)
        if not resfile.FileExists(originalgr2Path):
            gr2Path = originalgr2Path
        return gr2Path



    def __AdjustMeshForLod(self, mesh):
        mesh.geometryResPath = self.AdjustGr2PathForLod(mesh.geometryResPath)



    def AdjustRedFileForLod(self, redfile):
        (nonLodFolder, lodFolder,) = self.GetLODPathsToReplace()
        if not PerformanceOptions.useLodForRedfiles:
            return redfile
        resfile = blue.ResFile()
        redfileWithoutExtension = redfile.split('.')[0]
        lodInPath = '_lod' in redfile and not redfileWithoutExtension.endswith('0')
        lodsInSeparateFolder = self.lodsInSeparateFolder
        if self.currentLOD > 0:
            if lodInPath:
                newRedfilePath = redfileWithoutExtension[:-1] + '{0}.red'.format(self.currentLOD)
            else:
                newRedfilePath = redfile.replace('.red', '_lod{0}.red'.format(self.currentLOD))
            if lodsInSeparateFolder:
                newRedfilePath = newRedfilePath.replace(nonLodFolder, lodFolder)
            if resfile.FileExists(newRedfilePath):
                redfile = newRedfilePath
            return redfile
        if self.currentLOD == 0:
            if lodInPath:
                overridePath = redfileWithoutExtension.replace(nonLodFolder, lodFolder)[:-1] + 'a.red'
            else:
                overridePath = redfile.replace(nonLodFolder, lodFolder).replace('.red', '_loda.red')
            if resfile.FileExists(overridePath):
                redfile = overridePath
            return redfile
        if lodInPath:
            redfile = redfile.split('.')[0][:-5] + '.red'
        if lodsInSeparateFolder:
            redfile = redfile.replace(lodFolder, nonLodFolder)
        return redfile



    def _ProcessRules(self, buildDataManager, modifierList, updateRuleBundle, useCloth = False):
        if updateRuleBundle.rebuildHair:
            hairModifiers = [ x for x in buildDataManager.GetHairModifiers() if x not in modifierList ]
            modifierList.extend(hairModifiers)
        loadedObjects = {}
        modifiersWithDataToLoad = [ modifier for modifier in modifierList if modifier.redfile if modifier.weight > 0 ]
        modLen = len(modifiersWithDataToLoad)
        remIdx = []
        AdjustRedFileForLod = self.AdjustRedFileForLod
        LoadObject = blue.os.LoadObject
        for i in xrange(modLen):
            modifier = modifiersWithDataToLoad[i]
            redfile = modifier.clothOverride if useCloth and modifier.clothOverride else modifier.redfile
            if redfile not in loadedObjects:
                if self.useHeroHead and modifier.categorie == PD.DOLL_PARTS.HEAD:
                    redfile = redfile.replace('_generic', '_detailed')
                redfileLod = AdjustRedFileForLod(redfile)
                if not modifier.meshes or redfileLod != modifier.redfile:
                    objToLoad = LoadObject(redfileLod)
                    if objToLoad is None:
                        objToLoad = LoadObject(redfile)
                    loadedObjects[id(modifier)] = objToLoad
                else:
                    remIdx.insert(0, i)
            blue.pyos.BeNice()

        for i in iter(remIdx):
            del modifiersWithDataToLoad[i]

        for modifier in iter(modifiersWithDataToLoad):
            modifier.ClearCachedData()
            newBodyPart = loadedObjects.get(id(modifier), None)
            if newBodyPart and hasattr(newBodyPart, 'meshes'):
                for (i, mesh,) in enumerate(newBodyPart.meshes):
                    self._Doll__AdjustMeshForLod(mesh)
                    if modifier.categorie == PD.DOLL_PARTS.HAIR:
                        if mesh.name == PD.HAIR_MESH_SHAPE:
                            PD.MoveAreas(mesh.opaqueAreas, mesh.transparentAreas)
                            PD.MoveAreas(mesh.decalAreas, mesh.transparentAreas)
                        else:
                            PD.MoveAreas(mesh.opaqueAreas, mesh.decalAreas)
                            PD.MoveAreas(mesh.transparentAreas, mesh.decalAreas)
                    if mesh.name in PD.DRAPE_TUCK_NAMES:
                        PD.MoveAreas(mesh.opaqueAreas, mesh.transparentAreas)
                    if modifier.categorie not in PD.CATEGORIES_CONTAINING_GROUPS:
                        mesh.name = '{0}{1}'.format(modifier.categorie, mesh.meshIndex)
                    else:
                        mesh.name = '{0}{1}'.format(modifier.name, mesh.meshIndex)
                    if self.blendShapeMeshCache.get(mesh.name):
                        del self.blendShapeMeshCache[mesh.name]
                    modifier.meshes.append(mesh)
                    modifier.meshGeometryResPaths[mesh.name] = mesh.geometryResPath


        loadedObjects.clear()



    def __CalculateAccessoryUVs(self):

        def PackTextures(textures, target):
            watermark = 0
            returnUVs = []

            def BoxCoversX(x, box):
                if x >= box[0] and x < box[2]:
                    return True
                return False



            def GetHeightAt(x):
                height = 0
                newX = x
                for r in returnUVs:
                    if BoxCoversX(x, r):
                        if r[3] > height:
                            height = r[3]
                            newX = r[2]

                return (height, newX)



            def BoxIntersects(x, y, box, uv):
                for vert in ((x, y),
                 (x + box[0], y),
                 (x, y + box[1]),
                 (x + box[0], y + box[1])):
                    if vert[0] > uv[0] and vert[0] < uv[2] and vert[1] > uv[1] and vert[1] < uv[3]:
                        return True




            def BoxFits(x, y, box):
                if x < 0 or x + box[0] > target[0] or y < 0:
                    return False
                for r in returnUVs:
                    if BoxIntersects(x, y, box, r):
                        return False

                return True


            for t in textures:
                candidates = {}
                minInc = 100000
                x = 0.0
                while x < 1.0:
                    currentX = x
                    (h, x,) = GetHeightAt(currentX)
                    inc = h + t[1]
                    if BoxFits(currentX, h, t):
                        if inc < minInc:
                            minInc = inc
                            candidates[inc] = (currentX, h)
                    if x == currentX:
                        x += 1 / 512.0

                if len(candidates):
                    final = candidates[minInc]
                    returnUVs.append((final[0],
                     final[1],
                     final[0] + t[0],
                     final[1] + t[1]))
                    watermark = final[1] + t[1]

            if watermark > target[1]:
                factor = target[1] / watermark
                for ix in range(len(returnUVs)):
                    returnUVs[ix] = [returnUVs[ix][0] * factor,
                     returnUVs[ix][1] * factor,
                     returnUVs[ix][2] * factor,
                     returnUVs[ix][3] * factor]

            return returnUVs



        def GetMapSize(path):
            param = trinity.TriTexture2DParameter()
            param.resourcePath = path
            while param.resource.isLoading:
                blue.synchro.Yield()

            return (param.resource.width, param.resource.height)


        accesorieModifiers = self.buildDataManager.GetModifiersByPart(PD.DOLL_PARTS.ACCESSORIES)
        targetBox = (1.0, 1.0)
        textures = []
        for acc in iter(accesorieModifiers):
            tag = 'accessories'
            mapTarget = ''
            if tag in acc.mapD:
                mapTarget = acc.mapD[tag]
            if tag in acc.mapL:
                mapTarget = acc.mapL[tag]
            size = (0.0, 0.0)
            adjustedSize = (0.0, 0.0)
            if mapTarget:
                size = GetMapSize(mapTarget)
                adjustedSize = [size[0] / 512.0, size[1] / 512.0]
                if adjustedSize[0] > 0.5:
                    adjustedSize[0] = 0.5
                if adjustedSize[1] > 0.5:
                    adjustedSize[1] = 0.5
            textures.append(adjustedSize)

        result = PackTextures(textures, targetBox)
        for ix in range(len(accesorieModifiers)):
            mod = accesorieModifiers[ix]
            mod.ulUVs = (result[ix][0], result[ix][1])
            mod.lrUVs = (result[ix][2], result[ix][3])




    def __CalculateAccessorieUVs(self):
        useProperAlgorithm = True
        if useProperAlgorithm:
            self._Doll__CalculateAccessoryUVs()
            return 
        accesorieModifiers = self.buildDataManager.GetModifiersByPart(PD.DOLL_PARTS.ACCESSORIES)
        numAcc = len(accesorieModifiers)
        if numAcc > 0:
            split = 1
            if numAcc == 1:
                split = 1
            elif numAcc < 5:
                split = 2
            elif numAcc < 10:
                split = 3
            elif numAcc < 17:
                split = 4
            else:
                split = 5
                if numAcc > 25:
                    numAcc = 25
                    accesorieModifiers = accesorieModifiers[0:25]
            uvs = []
            for x in xrange(split):
                for y in xrange(split):
                    w = 1.0 / split
                    uv = [x * w,
                     y * w,
                     (x + 1) * w,
                     (y + 1) * w]
                    uvs.append(uv)


            uvIndex = 0
            for acc in iter(accesorieModifiers):
                (ula, ulb, lra, lrb,) = uvs[uvIndex]
                acc.ulUVs = (ula, ulb)
                acc.lrUVs = (lra, lrb)
                uvIndex += 1




    def __ApplyUVs(self):
        self._Doll__CalculateAccessorieUVs()
        UVs = {PD.DOLL_PARTS.HEAD: PD.HEAD_UVS,
         PD.DOLL_PARTS.BODY: PD.BODY_UVS,
         PD.DOLL_PARTS.HAIR: PD.HAIR_UVS,
         PD.DOLL_PARTS.ACCESSORIES: PD.ACCE_UVS}
        modifierGenerator = (modifier for modifier in self.buildDataManager.GetSortedModifiers() if modifier.weight > 0 if modifier.IsMeshContainingModifier())
        for modifier in modifierGenerator:
            meshes = list(modifier.meshes)
            if modifier.clothData:
                meshes.append(modifier.clothData)
            modifierUVCategory = self.buildDataManager.CategoryToPart(modifier.categorie)
            for mesh in iter(meshes):
                uvCategory = modifierUVCategory
                if uvCategory == PD.DOLL_PARTS.HAIR and hasattr(mesh, 'decalAreas') and mesh.decalAreas:
                    for area in mesh.decalAreas:
                        if 'stubble' in area.name.lower():
                            uvCategory = PD.DOLL_PARTS.HEAD
                            break

                if hasattr(mesh, 'opaqueAreas') and hasattr(mesh, 'decalAreas') and hasattr(mesh, 'transparentAreas'):
                    for area in tuple(mesh.opaqueAreas) + tuple(mesh.decalAreas) + tuple(mesh.transparentAreas):
                        for category in UVs:
                            if category.lower() + 'uv' in area.name.lower():
                                uvCategory = category
                                break


                fxs = PD.GetEffectsFromMesh(mesh)
                for fx in iter(fxs):
                    if type(fx) != trinity.Tr2ShaderMaterial and fx.effectResource and fx.effectResource.isLoading:
                        while fx.effectResource.isLoading:
                            blue.synchro.Yield()

                    transformUV0 = None
                    for effectParameter in iter(fx.parameters):
                        if effectParameter.name == 'TransformUV0':
                            transformUV0 = effectParameter
                            break

                    if not transformUV0:
                        transformUV0 = trinity.Tr2Vector4Parameter()
                        transformUV0.name = 'TransformUV0'
                        fx.parameters.append(transformUV0)
                    computedUVs = None
                    if uvCategory == PD.DOLL_PARTS.ACCESSORIES:
                        width = UVs[uvCategory][2] - UVs[uvCategory][0]
                        height = UVs[uvCategory][3] - UVs[uvCategory][1]
                        computedUVs = (UVs[uvCategory][0] + modifier.ulUVs[0] * width,
                         UVs[uvCategory][1] + modifier.ulUVs[1] * height,
                         UVs[uvCategory][0] + modifier.lrUVs[0] * width,
                         UVs[uvCategory][1] + modifier.lrUVs[1] * height)
                    elif type(mesh) is trinity.Tr2ClothingActor:
                        computedUVs = (UVs[uvCategory][0],
                         UVs[uvCategory][3],
                         UVs[uvCategory][2],
                         UVs[uvCategory][1])
                    else:
                        computedUVs = (UVs[uvCategory][0],
                         UVs[uvCategory][1],
                         UVs[uvCategory][2],
                         UVs[uvCategory][3])
                    transformUV0.value = computedUVs






    def GetMorphTargets(self, removedModifiers = None):
        modifierList = self.buildDataManager.GetSortedModifiers()
        removedModifiers = removedModifiers or self.buildDataManager.GetDirtyModifiers(removedBit=True)
        morphTargets = {}

        def Qualifier(modifier):
            return modifier.categorie in PD.BLENDSHAPE_CATEGORIES and modifier.weight != 0.0


        for modifier in iter(removedModifiers):
            if Qualifier(modifier):
                morphTargets[modifier.name] = 0

        for modifier in iter(modifierList):
            if Qualifier(modifier):
                morphTargets[modifier.name] = modifier.weight

        return morphTargets



    def _HandleBlendShapes(self, removedModifiers = None, avatar = None, updateClothMeshes = True):
        self.SpawnUpdateChildTasklet(self._Doll__HandleBlendShapes_t, removedModifiers, updateClothMeshes, avatar)



    @bluepy.CCP_STATS_ZONE_METHOD
    def __HandleBlendShapes_t(self, removedModifiers, updateClothMeshes, avatar):
        try:
            self.busyHandlingBlendshapes = True
            modifierList = self.buildDataManager.GetSortedModifiers()
            morphTargets = self.GetMorphTargets(removedModifiers)
            if morphTargets:
                meshGeometryResPaths = {}
                for modifier in iter(modifierList):
                    meshGeometryResPaths.update(modifier.meshGeometryResPaths)

                meshesWithCloth = self.buildDataManager.GetMeshes(includeClothMeshes=True)
                clothMeshes = [ mesh for mesh in meshesWithCloth if type(mesh) == trinity.Tr2ClothingActor ]
                meshes = [ mesh for mesh in meshesWithCloth if type(mesh) == trinity.Tr2Mesh ]
                Factory.ApplyMorphTargetsToMeshes(meshes, morphTargets, self.blendShapeMeshCache, meshGeometryResPaths, clothMeshes=clothMeshes, updateClothMeshes=updateClothMeshes, avatar=avatar, clothMorphValues=self.clothMorphValues)
                for mesh in iter(meshes):
                    if mesh.name not in self.blendShapeMeshCache:
                        mesh.deferGeometryLoad = False

            for mesh in self.buildDataManager.GetMeshes(alternativeModifierList=removedModifiers, includeClothMeshes=True):
                if self.blendShapeMeshCache.get(mesh.name):
                    del self.blendShapeMeshCache[mesh.name]
                if self.clothMorphValues.get(str(mesh)):
                    del self.clothMorphValues[str(mesh)]


        finally:
            self.busyHandlingBlendshapes = False




    def ApplyBoneOffsets(self):
        self.boneOffsets = {}
        modifiersDone = []
        for modifier in (modifier for modifier in self.buildDataManager.GetSortedModifiers() if modifier.poseData):
            if modifier.respath not in modifiersDone:
                modifiersDone.append(modifier.respath)
                weight = modifier.weight
                for bone in iter(modifier.poseData):
                    if bone not in self.boneOffsets:
                        newT = modifier.poseData[bone][PD.TRANSLATION]
                        newR = modifier.poseData[bone][PD.ROTATION]
                        self.boneOffsets[bone] = {}
                        self.boneOffsets[bone][PD.TRANSLATION] = (newT[0] * weight, newT[1] * weight, newT[2] * weight)
                        self.boneOffsets[bone][PD.ROTATION] = (newR[0] * weight, newR[1] * weight, newR[2] * weight)
                    else:
                        prevT = self.boneOffsets[bone][PD.TRANSLATION]
                        prevR = self.boneOffsets[bone][PD.ROTATION]
                        newT = modifier.poseData[bone][PD.TRANSLATION]
                        newR = modifier.poseData[bone][PD.ROTATION]
                        self.boneOffsets[bone][PD.TRANSLATION] = (prevT[0] + newT[0] * weight, prevT[1] + newT[1] * weight, prevT[2] + newT[2] * weight)
                        self.boneOffsets[bone][PD.ROTATION] = (prevR[0] + newR[0] * weight, prevR[1] + newR[1] * weight, prevR[2] + newR[2] * weight)





    def _EnsureCompleteBody(self, factory):

        def BodyPartSearch(modifier, categoryStartsWith):
            return modifier.IsMeshContainingModifier() and modifier.categorie.startswith(categoryStartsWith)



        def EnsureBodyPart(bodyModifiers, categoryStartsWith, defaultPart):
            if not any(map(lambda x: BodyPartSearch(x, categoryStartsWith), bodyModifiers)):
                self.AddResource(defaultPart, 1.0, factory, privilegedCaller=True)


        headModifier = self.buildDataManager.GetModifierByResPath(PD.DEFAULT_NUDE_HEAD)
        if not headModifier:
            self.AddResource(PD.DEFAULT_NUDE_HEAD, 1.0, factory, privilegedCaller=True)
        if self.currentLOD != 2:
            makeupModifiers = self.buildDataManager.GetModifiersByCategory(PD.HEAD_CATEGORIES.MAKEUP)
            foundEyelashes = False
            for makeup in iter(makeupModifiers):
                if makeup.name.startswith('eyelashes'):
                    foundEyelashes = True

            if not foundEyelashes:
                self.AddResource(PD.DEFAULT_NUDE_EYELASHES, 1.0, factory, privilegedCaller=True)
        bodyModifiers = self.buildDataManager.GetModifiersByPart(PD.DOLL_PARTS.BODY)
        EnsureBodyPart(bodyModifiers, 'bottom', PD.DEFAULT_NUDE_LEGS)
        EnsureBodyPart(bodyModifiers, PD.BODY_CATEGORIES.FEET, PD.DEFAULT_NUDE_FEET)
        EnsureBodyPart(bodyModifiers, PD.BODY_CATEGORIES.HANDS, PD.DEFAULT_NUDE_HANDS)
        EnsureBodyPart(bodyModifiers, 'top', PD.DEFAULT_NUDE_TORSO)



    def Load(self, filename, factory):
        self.LoadYaml(filename, factory)



    def LoadYaml(self, filename, factory):
        dna = factory.GetDNAFromYamlFile(filename)
        self.LoadDNA(dna, factory)



    def CreateModifierFromFootPrint(self, factory, footPrint):

        def doDecal(modifier):
            decal = footPrint.get(PD.DNA_STRINGS.DECALDATA)
            if decal:
                modifier.decalData = PD.ProjectedDecal.Load(decal)


        pathlower = footPrint[PD.DNA_STRINGS.PATH].lower()
        if pathlower not in factory.GetOptionsByGender(self.gender):
            log.LogWarn("Paperdoll - Doll::CreateModifierFromFootPrint is creating modifier that doesn't exist in options.")
            modifier = PD.BuildData(pathlower)
            modifier.weight = float(footPrint[PD.DNA_STRINGS.WEIGHT])
            doDecal(modifier)
        else:
            modifier = factory.CollectBuildData(pathlower, factory.GetOptionsByGender(self.gender))
            modifier.weight = footPrint[PD.DNA_STRINGS.WEIGHT]
            modifier.pattern = footPrint.get(PD.DNA_STRINGS.PATTERN, '')
            modifier.tuck = footPrint.get(PD.DNA_STRINGS.TUCK, False)
            if type(footPrint.get(PD.DNA_STRINGS.COLORS)) in types.StringTypes:
                colorData = eval(footPrint.get(PD.DNA_STRINGS.COLORS))
            else:
                colorData = footPrint.get(PD.DNA_STRINGS.COLORS)
            if colorData:
                if modifier.pattern:
                    modifier.patternData = colorData
                    if len(modifier.patternData) == 5:
                        modifier.patternData.append((0, 0, 8, 8))
                        modifier.patternData.append(0.0)
                else:
                    modifier.colorizeData = colorData
            if PD.DNA_STRINGS.SPECULARCOLORS in footPrint:
                modifier.specularColorData = footPrint.get(PD.DNA_STRINGS.SPECULARCOLORS)
            if footPrint.get(PD.DNA_STRINGS.COLORVARIATION, ''):
                modifier.SetColorVariation(footPrint[PD.DNA_STRINGS.COLORVARIATION])
            if footPrint.get(PD.DNA_STRINGS.VARIATION, ''):
                modifier.SetVariation(footPrint[PD.DNA_STRINGS.VARIATION])
            doDecal(modifier)
        depModFullData = modifier.GetDependantModifiersFullData()
        if depModFullData:
            for entry in depModFullData:
                depFootPrint = {}
                depFootPrint[PD.DNA_STRINGS.PATH] = entry[0]
                depFootPrint[PD.DNA_STRINGS.COLORVARIATION] = entry[1]
                depFootPrint[PD.DNA_STRINGS.VARIATION] = entry[2]
                depFootPrint[PD.DNA_STRINGS.WEIGHT] = entry[3]
                modifier.AddDependantModifier(self.CreateModifierFromFootPrint(factory, depFootPrint))

        return modifier



    def SortModifiersForBatchAdding(self, modifiers):

        def BatchAddModifierKey(modifier):
            if modifier.categorie == PD.DOLL_EXTRA_PARTS.UTILITYSHAPES:
                return 0
            else:
                if modifier.categorie == PD.DOLL_EXTRA_PARTS.DEPENDANTS:
                    return 1
                return 2


        modifiers.sort(key=lambda x: x.categorie)
        modifiers.sort(key=lambda x: BatchAddModifierKey(x))
        return modifiers



    def LoadDNA(self, data, factory, tattoos = None, buildDataManager = None):
        self.busyLoadingDNA = True
        if data[0] in PD.GENDER:
            self.gender = data[0]
            data = data[1:]
        buildDataManager = buildDataManager or self.buildDataManager
        modifiers = []
        for footPrint in iter(data):
            modifier = self.CreateModifierFromFootPrint(factory, footPrint)
            modifiers.append(modifier)
            blue.pyos.BeNice()

        modifiers = self.SortModifiersForBatchAdding(modifiers)
        for modifier in iter(modifiers):
            buildDataManager.AddModifier(modifier)

        self.busyLoadingDNA = False



    def GetDNA(self, preserveTypes = False, getHiddenModifiers = False, getWeightless = False):
        dna = [self.gender]
        modifiers = self.buildDataManager.GetSortedModifiers(showHidden=getHiddenModifiers)
        for modifier in iter(modifiers):
            ow = self.buildDataManager.GetOcclusionWeight(modifier)
            if getWeightless or ow + modifier.weight > 0.0:
                data = modifier.GetFootPrint(preserveTypes, occlusionWeight=ow)
                dna.append(data)

        return dna



    def MatchDNA(self, factory, dna):
        self.busyLoadingDNA = True
        if dna[0] in PD.GENDER:
            self.gender = dna[0]
            tempDNA = list(dna[1:])
        else:
            tempDNA = list(dna)
        remList = []
        for modifier in self.buildDataManager.GetSortedModifiers():
            found = False
            for footPrint in tempDNA:
                cmpResult = modifier.CompareFootPrint(footPrint)
                if cmpResult != 0:
                    tempDNA.remove(footPrint)
                    found = True
                    if cmpResult == -1:
                        modifier.SetVariation(footPrint.get(PD.DNA_STRINGS.VARIATION, ''))
                    break

            if not found:
                remList.append(modifier)

        for modifier in remList:
            self.buildDataManager.RemoveModifier(modifier)

        modifiers = []
        for footPrint in tempDNA:
            modifier = self.CreateModifierFromFootPrint(factory, footPrint)
            modifiers.append(modifier)

        modifiers = self.SortModifiersForBatchAdding(modifiers)
        for modifier in iter(modifiers):
            self.buildDataManager.AddModifier(modifier)

        self.busyLoadingDNA = False



    def Save(self, filename):
        f = file(filename, 'w')
        dnaData = self.GetDNA()
        yaml.dump(dnaData, f, default_flow_style=False)
        f.close()



    def GetBuildDataManager(self):
        return self.buildDataManager



    def GetBuildDataByCategory(self, category, coalesceToPart = True):
        modifiers = self.buildDataManager.GetModifiersByCategory(category)
        if coalesceToPart and not modifiers:
            if category in PD.DOLL_PARTS + PD.DOLL_EXTRA_PARTS:
                modifiers = self.buildDataManager.GetModifiersByPart(category)
        return modifiers



    def GetBuildDataByResPath(self, resPath, includeFuture = False):
        return self.buildDataManager.GetModifierByResPath(resPath, includeFuture=includeFuture)



    def _AddResource(self, res, weight, factory, colorization = None, variation = None, colorVariation = None, privilegedCaller = False, rawColorVariation = None):
        parts = res.split(PD.SEPERATOR_CHAR)
        if len(parts) == 1:
            raise Exception('Can not add a whole category to the character')
        options = factory.GetOptionsByGender(self.gender)
        modifier = factory.CollectBuildData(res, options, weight)
        categorie = modifier.categorie
        self.ApplyVariationsToModifier(modifier, colorization, variation, colorVariation, rawColorVariation=rawColorVariation)
        dependantModifiersFullData = modifier.GetDependantModifiersFullData()
        if dependantModifiersFullData:
            for parsedValues in iter(dependantModifiersFullData):
                dependantModifier = self._AddResource(parsedValues[0], parsedValues[3], factory, variation=parsedValues[2], colorVariation=parsedValues[1], privilegedCaller=privilegedCaller)
                modifier.AddDependantModifier(dependantModifier)

        if categorie in [PD.DOLL_PARTS.HAIR]:
            if categorie == PD.DOLL_PARTS.HAIR:
                hairModifiers = self.buildDataManager.GetModifiersByCategory(categorie)
                if hairModifiers:
                    modifier.colorizeData = hairModifiers[0].colorizeData
                elif self.hairColorizeData:
                    modifier.colorizeData = self.hairColorizeData
            self.buildDataManager.SetModifiersByCategory(categorie, [modifier], privilegedCaller=privilegedCaller)
        else:
            self.buildDataManager.AddModifier(modifier, privilegedCaller=privilegedCaller)
        return modifier



    def SetItemType(self, factory, itemType, weight = 1.0, rawColorVariation = None):
        if type(itemType) is not tuple:
            itemType = factory.GetItemType(itemType)
        self.RemoveResource(itemType[0], factory)
        return self.AddItemType(factory, itemType, weight, rawColorVariation)



    def AddItemType(self, factory, itemType, weight = 1.0, rawColorVariation = None):
        if type(itemType) is not tuple:
            itemType = factory.GetItemType(itemType)
        if type(itemType) is tuple:
            return self.AddResource(itemType[0], weight, factory, variation=itemType[1], colorVariation=itemType[2], rawColorVariation=rawColorVariation)



    def ApplyVariationsToModifier(self, modifier, colorization = None, variation = None, colorVariation = None, rawColorVariation = None):
        if colorization:
            modifier.SetColorizeData(colorization)
        if variation:
            modifier.SetVariation(variation)
        if colorVariation:
            modifier.SetColorVariation(colorVariation)
        if rawColorVariation:
            if colorVariation:
                log.LogWarn('paperDoll::Doll:: ApplyVariationsToModifier: applying both colorVariation and rawColorVariation')
            modifier.SetColorVariationDirectly(rawColorVariation)



    def AddResource(self, res, weight, factory, colorization = None, variation = None, colorVariation = None, privilegedCaller = False, rawColorVariation = None):
        modifier = None
        if type(res) is PD.ProjectedDecal:
            decalName = res.label or 'Decal {0}'.format(res.layer)
            modifier = PD.BuildData(name=decalName, categorie=PD.BODY_CATEGORIES.TATTOO)
            modifier.decalData = res
            self.ApplyVariationsToModifier(modifier, colorization, variation, colorVariation)
            self.buildDataManager.AddModifier(modifier, privilegedCaller=privilegedCaller)
        else:
            modifier = self._AddResource(res, weight, factory, colorization=colorization, variation=variation, colorVariation=colorVariation, privilegedCaller=privilegedCaller, rawColorVariation=rawColorVariation)
        return modifier



    def AddResources(self, resList, weight, factory):
        for each in iter(resList):
            self.AddResource(each, weight, factory)




    def RemoveResource(self, res, factory, privilegedCaller = False):
        parts = res.split(PD.SEPERATOR_CHAR)
        if len(parts) == 1:
            raise Exception('Can not remove a whole category from the character')
        categorie = str(parts[0].lower())
        modifiers = self.buildDataManager.GetModifiersByCategory(categorie, showHidden=True)
        targetFun = lambda modifier: str(modifier.respath.lower()) == str(res.lower())
        target = None
        for modifier in modifiers:
            if targetFun(modifier):
                target = modifier
                break

        if target:
            self.buildDataManager.RemoveModifier(target, privilegedCaller=privilegedCaller)
        return target



    def HandleChangedDependencies(self, factory):
        changedModifiers = self.buildDataManager.GetDirtyModifiers(changedBit=True)
        for modifier in iter(changedModifiers):
            self.buildDataManager.ReverseOccludeModifiersByModifier(modifier, modifier.lastVariation)
            self.buildDataManager.OccludeModifiersByModifier(modifier)
            resPaths = modifier.GetDependantModifierResPaths() or []
            for dependantModifier in iter(modifier.GetDependantModifiers()):
                if dependantModifier.respath not in resPaths:
                    modifier.RemoveDependantModifier(dependantModifier)
                    self.buildDataManager.RemoveParentModifier(modifier, dependantModifier)
                    self.buildDataManager.RemoveModifier(dependantModifier, privilegedCaller=True)
                else:
                    resPaths.remove(dependantModifier.respath)

            if resPaths:
                dependantModifiersFullData = modifier.GetDependantModifiersFullData()
                for entry in dependantModifiersFullData:
                    if entry[0] in resPaths:
                        dependantModifier = self._AddResource(entry[0], entry[3], factory, variation=entry[2], colorVariation=entry[3], privilegedCaller=True)
                        modifier.AddDependantModifier(dependantModifier)
                        self.buildDataManager.AddParentModifier(dependantModifier, modifier)





    def QueryModifiers(self, modifierList, fun):
        return all(map(fun, modifierList))



    def __CheckQuitRequested(self):
        if self._Doll__quitRequested:
            raise KillUpdateException('Preemptively killing Update')



    def SpawnUpdateChildTasklet(self, fun, *args):
        t = uthread.new(fun, *args)
        t.context = 'paperDoll::Doll::Update'
        uthread.schedule(t)
        self._UpdateTaskletChildren.append(t)



    def ReapUpdateChildTasklets(self):
        try:
            try:
                for t in self._UpdateTaskletChildren:
                    t.kill()

            except KillUpdateException:
                sys.exc_clear()

        finally:
            del self._UpdateTaskletChildren[:]




    def _DelayedUpdateCall(self, factory, avatar, visualModel, LODMode):
        self.hasDelayedUpdateCallPending = True
        blue.synchro.Yield()
        while self._currentUpdateTasklet:
            blue.synchro.Yield()

        self.hasDelayedUpdateCallPending = False
        self.Update(factory, avatar, visualModel, LODMode)



    def KillUpdateIfSafe(self):
        currentFrame = trinity.GetCurrentFrameCounter()
        if self._currentUpdateTasklet and self._Doll__updateFrameStamp < currentFrame and self._currentUpdateTasklet.alive:
            self._currentUpdateTasklet.raise_exception(KillUpdateException, 'Preemptively killing Update')
            return True
        return False



    def Update(self, factory, avatar = None, visualModel = None, LODMode = False):
        currentFrame = trinity.GetCurrentFrameCounter()
        if self._Doll__updateFrameStamp == currentFrame:
            log.LogWarn('paperDoll::Doll::Update is being called more than once on the same frame for the same doll instance! Fix your code so you only call Update after all needed changes have been applied.')
            return 
        if self._currentUpdateTasklet and self._Doll__updateFrameStamp < currentFrame:
            if self.KillUpdateIfSafe():
                if not self.hasDelayedUpdateCallPending:
                    uthread.new(self._DelayedUpdateCall, factory, avatar, visualModel, LODMode)
            return 
        self._Doll__updateFrameStamp = currentFrame
        self._currentUpdateTasklet = uthread.new(self.Update_t, *(factory, avatar, visualModel))
        self._currentUpdateTasklet.context = 'paperDoll::Doll::Update'
        uthread.schedule(self._currentUpdateTasklet)



    def IsBusyUpdating(self):
        return self._currentUpdateTasklet and self._currentUpdateTasklet.alive



    def Update_t(self, factory, avatar, visualModel):
        try:
            try:
                buildDataManager = self.buildDataManager
                while self.busyLoadingDNA or not factory.IsLoaded:
                    blue.synchro.Yield()

                LODMode = self.previousLOD != self.currentLOD
                buildDataManager.Lock()
                updateRuleBundle = UpdateRuleBundle()
                if not LODMode:
                    blue.pyos.BeNice()
                else:
                    blue.synchro.Yield()
                if avatar and hasattr(avatar, 'visualModel') and not visualModel:
                    visualModel = avatar.visualModel
                AddMarker('Update Start')
                PD.FullOptixRenderer.Pause()
                self._EnsureCompleteBody(factory)
                self.HandleChangedDependencies(factory)
                gdm = buildDataManager.GetDirtyModifiers
                addedModifiers = gdm(addedBit=True, getWeightless=False)
                removedModifiers = gdm(removedBit=True) if self.hasUpdatedOnce else []
                changedModifiers = gdm(changedBit=True) if self.hasUpdatedOnce else []
                if self.hasUpdatedOnce:
                    dirtyModifiers = removedModifiers + addedModifiers + changedModifiers
                    addedAndChangedModifiers = addedModifiers + changedModifiers
                else:
                    dirtyModifiers = addedModifiers
                    addedAndChangedModifiers = addedModifiers
                if not dirtyModifiers:
                    raise RedundantUpdateException('Warning - Call made to PaperDoll.Update() when no modifier is dirty!')
                if self.hasUpdatedOnce:
                    updateRuleBundle.SetBlendShapesOnly(self.QueryModifiers(dirtyModifiers, fun=lambda x: x.IsBlendshapeModifier()))
                    updateRuleBundle.SetDecalsOnly(self.QueryModifiers(dirtyModifiers, fun=lambda x: x.decalData is not None))
                if not updateRuleBundle.blendShapesOnly and avatar and self.currentLOD < 2:
                    dirtyDecalModifiers = [ decalModifier for decalModifier in buildDataManager.GetModifiersByCategory(PD.BODY_CATEGORIES.TATTOO) if decalModifier.decalData if decalModifier.IsDirty or not decalModifier.IsTextureContainingModifier() ]
                    updateRuleBundle.doDecals = len(dirtyDecalModifiers) > 0 and not updateRuleBundle.blendShapesOnly and avatar and self.currentLOD < 2
                if not (updateRuleBundle.blendShapesOnly or updateRuleBundle.decalsOnly):
                    self._AnalyzeBuildDataForRules(updateRuleBundle, buildDataManager)
                    self._ProcessRules(buildDataManager, addedAndChangedModifiers, updateRuleBundle, factory.clothSimulationActive)
                    self.ApplyBoneOffsets()
                updateRuleBundle.meshesAddedOrRemoved = not (updateRuleBundle.blendShapesOnly or updateRuleBundle.decalsOnly)
                wrinkleFx = []
                if not updateRuleBundle.blendShapesOnly and avatar:
                    factory.CreateAnimationOffsets(avatar, self)
                if not updateRuleBundle.decalsOnly and self.modifierLimits:
                    for modifier in iter(addedAndChangedModifiers):
                        limit = self.modifierLimits.get(modifier.name)
                        if limit:
                            if modifier.weight > limit[1]:
                                modifier.weight = limit[1]
                            elif modifier.weight < limit[0]:
                                modifier.weight = limit[0]

                if updateRuleBundle.blendShapesOnly or updateRuleBundle.doDecals:
                    if not updateRuleBundle.decalsOnly:
                        self._HandleBlendShapes(removedModifiers, avatar)
                    if updateRuleBundle.doDecals:
                        self.BakeDecals_t(factory, dirtyDecalModifiers)
                    self.WaitForChildTaskletsToFinish()
                if factory.clothSimulationActive and avatar and not (updateRuleBundle.decalsOnly or updateRuleBundle.blendShapesOnly):
                    self.LoadClothData(addedAndChangedModifiers)
                hashStubble = PD.PortraitTools.GetStubbleHash(addedAndChangedModifiers)
                if updateRuleBundle.meshesAddedOrRemoved:
                    self._Doll__ApplyUVs()
                while self.mapBundle._busyDownScaling:
                    blue.synchro.Yield()

                if visualModel and (self.currentLOD <= self.previousLOD or not self.mapBundle.AllMapsGood()):
                    updateRuleBundle.partsToComposite = buildDataManager.GetPartsFromMaps(dirtyModifiers)
                    if self.currentLOD > 1:
                        updateRuleBundle.mapsToComposite = [PD.DIFFUSE_MAP]
                    elif self.currentLOD == 1:
                        updateRuleBundle.mapsToComposite = [PD.DIFFUSE_MAP, PD.NORMAL_MAP]
                    elif self.hasUpdatedOnce and self.mapBundle.AllMapsGood():
                        updateRuleBundle.mapsToComposite = buildDataManager.GetMapsToComposite(dirtyModifiers)
                    if buildDataManager.desiredOrderChanged:
                        if PD.DOLL_PARTS.BODY not in updateRuleBundle.partsToComposite:
                            updateRuleBundle.partsToComposite.append(PD.DOLL_PARTS.BODY)
                        updateRuleBundle.mapsToComposite = list(PD.MAPS)
                    blendShapeVector = [ modifier.weight for modifier in buildDataManager.GetSortedModifiers() if modifier.categorie in PD.BLENDSHAPE_CATEGORIES if modifier.weight != 0.0 ]
                    hES = (self.compressionSettings, hashStubble, blendShapeVector)
                    hashKey = buildDataManager.HashForMaps(hashableElements=hES)
                    mapsTypesComposited = self.CompositeTextures(factory, hashKey, updateRuleBundle)
                    if updateRuleBundle.meshesAddedOrRemoved:
                        self.WaitForTexturesToComposite(factory, hashKey, mapsTypesComposited)
                if updateRuleBundle.meshesAddedOrRemoved:
                    meshes = buildDataManager.GetMeshes(includeClothMeshes=factory.clothSimulationActive)
                    self._HandleBlendShapes(removedModifiers, avatar)
                    self.WaitForChildTaskletsToFinish()
                    Factory.BindCompositeTexturesToMeshes(meshes, self.mapBundle)
                    factory.BindGlobalMaps(meshes)
                    self.ConfigureMaskedShader(updateRuleBundle)
                    self.ApplyShaders(meshes, wrinkleFx, factory)
                    if visualModel:
                        factory.RemoveMeshesFromVisualModel(visualModel)
                    if visualModel:
                        factory.AppendMeshesToVisualModel(visualModel, meshes)
                    if avatar and avatar.clothMeshes is not None:
                        if len(avatar.clothMeshes) > 0:
                            del avatar.clothMeshes[:]
                        if factory.clothSimulationActive:
                            for mesh in iter(meshes):
                                if type(mesh) is trinity.Tr2ClothingActor:
                                    avatar.clothMeshes.append(mesh)

                if not updateRuleBundle.blendShapesOnly and visualModel:
                    visualModel.ResetAnimationBindings()
                if visualModel and self.currentLOD < 0 and not (updateRuleBundle.decalsOnly or updateRuleBundle.blendShapesOnly):

                    def doStubble():
                        PD.PortraitTools.HandleRemovedStubble(removedModifiers, buildDataManager)
                        PD.PortraitTools.HandleUpdatedStubble(addedAndChangedModifiers, buildDataManager)


                    self.SpawnUpdateChildTasklet(doStubble)
                if not (updateRuleBundle.decalsOnly or updateRuleBundle.blendShapesOnly) and len(wrinkleFx) > 0:
                    self.LoadBindPose()
                    PD.PortraitTools().SetupWrinkleMapControls(avatar, wrinkleFx, self)
                if visualModel and avatar and self.IsPrepass():
                    PD.prePassFixup.AddPrepassAreasToAvatar(avatar, visualModel, self, factory.clothSimulationActive)
                self.WaitForChildTaskletsToFinish()
                if not updateRuleBundle.blendShapesOnly:
                    if avatar:
                        avatar.ResetAnimationBindings()
                    elif visualModel:
                        visualModel.ResetAnimationBindings()
                if avatar:
                    freq = PerformanceOptions.updateFreq.get(self.currentLOD, 0)
                    if freq == 0:
                        avatar.updatePeriod = 0
                    else:
                        avatar.updatePeriod = 1.0 / freq
                buildDataManager.NotifyUpdate()
                self.lastUpdateRedundant = False
                PD.FullOptixRenderer.NotifyUpdate()
                self.previousLOD = self.currentLOD
                self.WaitForChildTaskletsToFinish()
                if self.currentLOD <= PD.LOD_SCATTER_SKIN and self.skinLightmapRenderer is None:
                    self.skinLightmapRenderer = PD.SkinLightmapRenderer(useOptix=self.currentLOD == PD.LOD_RAYTRACE)
                    self.skinLightmapRenderer.SetSkinnedObject(avatar)
                    self.skinLightmapRenderer.StartRendering()
                if visualModel and avatar and not LODMode:
                    if self.skinLightmapRenderer is not None:
                        self.skinLightmapRenderer.SetSkinnedObject(avatar)
                self.hasUpdatedOnce = True
            except RedundantUpdateException as err:
                self.lastUpdateRedundant = True
                sys.exc_clear()
            except KillUpdateException as err:
                self.lastUpdateRedundant = True
                sys.exc_clear()
            except Exception as err:
                log.LogException(str(err))
                sys.exc_clear()

        finally:
            self.ReapUpdateChildTasklets()
            buildDataManager.UnLock()
            self._currentUpdateTasklet = None
            AddMarker('End Start')
            t = uthread.new(self.NotifyUpdateDoneListeners_t)
            uthread.schedule(t)




    def NotifyUpdateDoneListeners_t(self):
        while self.busyUpdating:
            blue.synchro.Yield()

        for listener in self.onUpdateDoneListeners:
            uthread.new(listener)




    def AddUpdateDoneListener(self, callBack):
        if callBack not in self.onUpdateDoneListeners:
            self.onUpdateDoneListeners.append(callBack)



    def WaitForChildTaskletsToFinish(self):
        try:
            while any(map(lambda x: x.alive, self._UpdateTaskletChildren)):
                blue.synchro.Yield()

        except KillUpdateException:
            raise 



    def WaitForTexturesToComposite(self, factory, hashKey, mapsTypesComposited):
        while any(map(lambda x: x.alive, self._UpdateTaskletChildren)):
            blue.synchro.Yield()

        if factory.allowTextureCache and mapsTypesComposited:
            mapsToSave = [ self.mapBundle[mapType] for mapType in mapsTypesComposited if self.mapBundle[mapType].isGood ]
            uthread.new(factory.SaveMaps, hashKey, self.mapBundle.baseResolution[0], mapsToSave)



    def ConfigureMaskedShader(self, updateRuleBundle):
        if self.useMaskedShaders or updateRuleBundle.undoMaskedShaders:
            applicableModifiers = (modifier for modifier in self.buildDataManager.GetSortedModifiers() if modifier.categorie in PD.MASKING_CATEGORIES)
            for modifier in applicableModifiers:
                for mesh in iter(modifier.meshes):
                    self.ConfigureMeshForMaskedShader(mesh, remove=updateRuleBundle.undoMaskedShaders)

                blue.pyos.BeNice()




    def ConfigureMeshForMaskedShader(self, mesh, remove = False):
        decalToOpaque = []
        fx = PD.GetEffectsFromAreaList(mesh.opaqueAreas)
        for f in iter(fx):
            for p in f.parameters:
                if p.name == 'CutMaskInfluence':
                    p.value = 0.85


        for decalArea in mesh.decalAreas:
            f = decalArea.effect
            for p in f.parameters:
                if p.name == 'CutMaskInfluence':
                    if remove:
                        if abs(p.value - 0.85) < 0.001:
                            decalToOpaque.append(decalArea)
                        p.value = 0.0
                    elif abs(p.value - 0.85) > 0.001:
                        p.value = 1.01


        if remove:
            for area in decalToOpaque:
                mesh.opaqueAreas.append(area)
                mesh.decalAreas.remove(area)

        else:
            PD.MoveAreas(mesh.opaqueAreas, mesh.decalAreas)



    def BakeDecals_t(self, factory, decalModifiers):
        if decalModifiers:
            if self.decalBaker is None:
                self.decalBaker = PD.DecalBaker(factory)
            while self.busyHandlingBlendshapes:
                blue.synchro.Yield()

            self.decalBaker.CreateTargetAvatarFromDoll(self)
            self.decalBaker.SetSize(self.textureResolution)
            for decalModifier in decalModifiers:
                self.decalBaker.BakeDecalToModifier(decalModifier.decalData, decalModifier)
                while not self.decalBaker.isReady:
                    blue.synchro.Yield()

                decalModifier.mapL.update(decalModifier.mapD)
                decalModifier.colorize = True




    def LogDNA(self, factory):
        if factory.verbose:
            lines = yaml.dump(self.GetDNA(), default_flow_style=False).splitlines()
            log.LogInfo('Building paperDoll: ' + self.name)
            for each in iter(lines):
                log.LogInfo(each)




    def CompositeTextures(self, factory, hashKey, updateRuleBundle):
        if not updateRuleBundle.blendShapesOnly and factory.allowTextureCache:
            textureCache = {}
            mapCount = len(PD.MAPS)
            for i in xrange(mapCount):
                tex = factory.FindCachedTexture(hashKey, self.mapBundle.baseResolution[0], PD.MAPS[i])
                textureCache[i] = tex

            while any(map(lambda x: x is not None and x.isLoading, textureCache.values())):
                blue.synchro.Yield()

            for i in xrange(mapCount):
                if textureCache.get(i) and textureCache[i].isGood:
                    self.mapBundle.SetMapByTypeIndex(i, textureCache[i], hashKey)

        if self.compressionSettings is not None:
            self.compressionSettings.generateMipmap = False
        mapsTypesComposited = []
        for mapTypeIndex in updateRuleBundle.mapsToComposite:
            existingMap = self.mapBundle[mapTypeIndex]
            if existingMap and existingMap.isGood and hashKey == self.mapBundle.hashKeys.get(mapTypeIndex):
                continue
            else:
                mapsTypesComposited.append(mapTypeIndex)

            def CompositeTasklet_t(mapTypeIndex):
                texture = factory.CompositeCombinedTexture(self.name, mapTypeIndex, self.gender, self.buildDataManager, self.mapBundle, self.compressionSettings, textureCompositor=self.textureCompositor, partsToComposite=updateRuleBundle.partsToComposite, copyToExistingTexture=not updateRuleBundle.meshesAddedOrRemoved, lod=self.currentLOD)
                if texture:
                    self.mapBundle.SetMapByTypeIndex(mapTypeIndex, texture, hashKey)


            self.SpawnUpdateChildTasklet(CompositeTasklet_t, mapTypeIndex)

        return mapsTypesComposited



    def ApplyShaders(self, meshes, wrinkleFx, factory):
        if not meshes:
            return 
        compSet = self.compressionSettings if self.compressionSettings is not None else factory
        self.useDXT5N = compSet and compSet.compressTextures and compSet.AllowCompress(PD.NORMAL_MAP)
        skinSpotLightShadowsActive = PD.SkinSpotLightShadows.instance is not None
        skinLightmapRendererActive = self.skinLightmapRenderer is not None
        ShaderApplyFun = self.SetInteriorShader
        tasklets = []
        asyncMeshes = {}

        def DoClothMesh(mesh):
            isHair = False
            if self.currentLOD <= 0:
                fx = PD.GetEffectsFromMesh(mesh)
                for f in iter(fx):
                    isHair = PD.PortraitTools.BindHeroHairShader(f, '.fx') or isHair
                    if self.currentLOD <= PD.LOD_SKIN:
                        PD.PortraitTools.BindHeroClothShader(f, self.useDXT5N)

            if mesh.effect:
                while type(mesh.effect) == trinity.Tr2Effect and mesh.effect.effectResource.isLoading:
                    blue.synchro.Yield()

                mesh.effect.PopulateParameters()
            if mesh.effectReversed:
                while type(mesh.effect) == trinity.Tr2Effect and mesh.effectReversed.effectResource.isLoading:
                    blue.synchro.Yield()

                mesh.effectReversed.PopulateParameters()
            if PD.SkinSpotLightShadows.instance is not None:
                PD.SkinSpotLightShadows.instance.CreateEffectParamsForMesh(mesh, isClothMesh=True)
            if isHair and hasattr(mesh, 'useTransparentBatches'):
                mesh.useTransparentBatches = True


        for mesh in iter(meshes):
            if type(mesh) is trinity.Tr2ClothingActor:
                t = uthread.new(DoClothMesh, mesh)
            elif skinSpotLightShadowsActive or skinLightmapRendererActive:
                asyncMeshes[mesh] = False
            if PD.DOLL_PARTS.HEAD in mesh.name:
                t = uthread.new(ShaderApplyFun, *(asyncMeshes, mesh, wrinkleFx))
            else:
                t = uthread.new(ShaderApplyFun, *(asyncMeshes, mesh, None))
            tasklets.append(t)
            uthread.schedule(t)

        while any(map(lambda x: x.alive, tasklets)):
            blue.synchro.Yield()

        for mesh in asyncMeshes.iterkeys():
            if skinSpotLightShadowsActive:
                PD.SkinSpotLightShadows.instance.CreateEffectParamsForMesh(mesh)
            if skinLightmapRendererActive and asyncMeshes[mesh]:
                self.skinLightmapRenderer.BindLightmapShader(mesh)




    def SetInteriorShader(self, asyncMeshes, mesh, wrinkleFx):
        fx = PD.GetEffectsFromMesh(mesh)
        tasklets = []
        for f in iter(fx):
            if type(f) == trinity.Tr2ShaderMaterial:
                continue
            t = uthread.new(self.SetInteriorShaderForFx_t, *(f,
             asyncMeshes,
             mesh,
             wrinkleFx))
            tasklets.append(t)

        while any(map(lambda x: x.alive, tasklets)):
            blue.synchro.Yield()




    def SetInteriorShaderForFx_t(self, effect, asyncMeshes, mesh, wrinkleFx):
        path = effect.effectFilePath.lower()
        if 'masked.fx' in path:
            return 
        name = effect.name.lower()
        if name.startswith('c_custom') or name.startswith('c_s2'):
            PD.PortraitTools.BindCustomShaders(effect, useFastShaders=self._Doll__useFastShader)
            return 
        if asyncMeshes:
            asyncMeshes[mesh] = True
        suffix = '.fx'
        if self._Doll__useFastShader and ('_fast.fx' in path or path in PD.SHADERS_THAT_CAN_SWITCH_TO_FAST_SHADER_MODE):
            suffix = '_fast.fx'
        if self.useDXT5N and ('_dxt5n.fx' in path or path in PD.SHADERS_TO_ENABLE_DXT5N):
            suffix = '{0}_dxt5n.fx'.format(suffix[:-3])
        if PD.DOLL_PARTS.HAIR not in path:
            if self.currentLOD >= 0:
                if 'skinnedavatarbrdf' not in path:
                    effect.effectFilePath = '{0}{1}'.format(PD.INTERIOR_AVATAR_EFFECT_FILE_PATH[:-3], suffix)
                    foundBRDF = False
                    for r in effect.resources:
                        if r.name == 'FresnelLookupMap':
                            foundBRDF = True
                            continue

                    if not foundBRDF:
                        res = trinity.TriTexture2DParameter()
                        res.name = 'FresnelLookupMap'
                        res.resourcePath = PD.FRESNEL_LOOKUP_MAP
                        effect.resources.append(res)
            elif self.currentLOD == PD.LOD_HERO:
                PD.PortraitTools.BindHeroShader(effect, self.isOptimized, suffix)
            elif self.currentLOD == PD.LOD_SKIN:
                PD.PortraitTools.BindSkinShader(effect, wrinkleFx, scattering=False, buildDataManager=self.buildDataManager, gender=self.gender, use_png=PD.USE_PNG, fxSuffix=suffix)
                PD.PortraitTools.BindLinearAvatarBRDF(effect, suffix)
            elif self.currentLOD <= PD.LOD_SCATTER_SKIN:
                PD.PortraitTools.BindSkinShader(effect, wrinkleFx, scattering=True, buildDataManager=self.buildDataManager, gender=self.gender, use_png=PD.USE_PNG, fxSuffix=suffix)
                PD.PortraitTools.BindLinearAvatarBRDF(effect, suffix)
        elif self.currentLOD <= 0:
            PD.PortraitTools.BindHeroHairShader(effect, suffix)



    def LoadBindPose(self):
        filename = 'res:/Graphics/Character/Global/FaceSetup/BaseFemaleBindPose.yaml'
        if self.gender == PD.GENDER.MALE:
            filename = 'res:/Graphics/Character/Global/FaceSetup/BaseMaleBindPose.yaml'
        self.bindPose = PD.LoadYamlFileNicely(filename)



    def LoadClothData(self, modifierList):
        clothMeshes = []
        resFile = blue.ResFile()
        for modifier in iter(modifierList):
            clothLoadPath = modifier.clothPath
            if not clothLoadPath:
                modifier.clothData = None
                continue
            if self.currentLOD > 0:
                clothLod = clothLoadPath.replace('.red', '_lod{0}.red'.format(self.currentLOD))
                if self.lodsInSeparateFolder:
                    (nonLodFolder, lodFolder,) = self.GetLODPathsToReplace()
                    clothLod = clothLod.lower().replace(nonLodFolder, lodFolder)
                if resFile.FileExists(clothLod):
                    clothLoadPath = clothLod
                else:
                    clothLoadPath = None
            if clothLoadPath:
                clothData = blue.os.LoadObject(clothLoadPath)
                if clothData:
                    clothData.name = modifier.name
                    clothMeshes.append(clothData)
                modifier.clothData = clothData

        while any(map(lambda x: x.clothingRes.isLoading, clothMeshes)):
            blue.synchro.Yield()

        return clothMeshes



    def SuspendCloth(self, avatar = None, factory = None):
        for m in self.buildDataManager.GetSortedModifiers():
            if m.categorie != PD.DOLL_PARTS.HAIR and m.clothData:
                meshPath = m.clothPath.lower().replace('_physx.red', '.red')
                bsMesh = m.clothData.resPath.lower().replace('.apb', '_bs.gr2')
                cacheKey = meshPath + m.currentColorVariation
                if cacheKey not in self.tempClothCache:
                    item = blue.os.LoadObject(meshPath)
                    if hasattr(item, 'meshes') and len(item.meshes):
                        while item.meshes[0].isLoading:
                            blue.synchro.Yield()

                        dl = []
                        for mesh in item.meshes:
                            mesh.geometryResPath = bsMesh

                        for delMesh in dl:
                            item.meshes.remove(delMesh)

                        factory.BindGlobalMaps(item.meshes)
                        Factory.BindCompositeTexturesToMeshes(item.meshes, self.mapBundle)
                    self.tempClothCache[cacheKey] = item
                else:
                    item = self.tempClothCache[cacheKey]
                if hasattr(item, 'meshes'):
                    for mesh in item.meshes:
                        if not mesh.name.endswith('_clothTemp'):
                            mesh.name = mesh.name + '_clothTemp'
                        mesh.deferGeometryLoad = False
                        avatar.visualModel.meshes.append(mesh)
                        self.tempClothMeshes.append(mesh)

                    avatar.visualModel.ResetAnimationBindings()
                clothMeshList = list(avatar.clothMeshes)
                for cm in clothMeshList:
                    if cm == m.clothData:
                        avatar.clothMeshes.remove(cm)





    def UpdateTempClothBlends(self, factory):
        meshGeometryResPaths = {}
        morphTargets = self.GetMorphTargets()
        uthread.new(factory.ApplyMorphTargetsToMeshes, self.tempClothMeshes, morphTargets, self.tempClothCache, meshGeometryResPaths)



    def RestoreCloth(self, avatar = None):
        self.tempClothMeshes = []
        for m in self.buildDataManager.GetSortedModifiers():
            if m.categorie != PD.DOLL_PARTS.HAIR and m.clothData:
                avatar.clothMeshes.append(m.clothData)

        clothInScene = False
        while not clothInScene:
            clothInScene = True
            for m in self.buildDataManager.GetSortedModifiers():
                if m.categorie != PD.DOLL_PARTS.HAIR and m.clothData:
                    if not m.clothData.isInScene:
                        clothInScene = False

            if not clothInScene:
                blue.synchro.Yield()

        dl = []
        for mesh in avatar.visualModel.meshes:
            if mesh.name.endswith('_clothTemp'):
                dl.append(mesh)

        for d in dl:
            avatar.visualModel.meshes.remove(d)




    def SetTextureSize(self, *args):
        if type(args[0]) in (list, tuple):
            (x, y,) = args[0][:2]
        else:
            (x, y,) = args
        if self.skinLightmapRenderer is not None:
            self.skinLightmapRenderer.Refresh()
        (oldX, oldY,) = self.mapBundle.baseResolution
        self.mapBundle.SetBaseResolution(x, y)
        if x > oldX and y > oldY:
            self.mapBundle.ReCreate()
        for modifier in self.buildDataManager.GetSortedModifiers():
            if modifier.IsTextureContainingModifier():
                modifier.IsDirty = True




    def getbusyUpdating(self):
        return self._currentUpdateTasklet is not None or any(map(lambda x: x.alive, self._UpdateTaskletChildren))


    busyUpdating = property(fget=lambda self: self.getbusyUpdating())

    def setoverrideLod(self, newLod):
        oldLod = self.currentLOD
        self.currentLOD = newLod
        self.previousLOD = oldLod
        if oldLod == PD.LOD_SKIN and newLod <= PD.LOD_SCATTER_SKIN:
            self.buildDataManager.SetAllAsDirty()
            return 
        if oldLod <= PD.LOD_SCATTER_SKIN and newLod >= PD.LOD_SKIN:
            self.skinLightmapRenderer = None
            if newLod == PD.LOD_SKIN:
                return 
        for modifier in self.buildDataManager.GetSortedModifiers():
            if modifier.IsMeshContainingModifier():
                modifier.IsDirty = True
                del modifier.meshes[:]
                modifier.meshGeometryResPaths = {}

        if newLod >= 0 and newLod < len(PD.LOD_TEXTURE_SIZES):
            self.SetTextureSize(*PD.LOD_TEXTURE_SIZES[newLod])


    overrideLod = property(fget=lambda self: self.currentLOD, fset=setoverrideLod)
    textureResolution = property(fget=lambda self: self.mapBundle.baseResolution, fset=SetTextureSize)

    def setusecachedrendertargets(self, value):
        log.LogWarn('PaperDoll:Doll:UseCachedRenderTargets are depricated, this call does nothing.')


    useCachedRenderTargets = property(fget=lambda self: False, fset=setusecachedrendertargets)

    def setusefastshader(self, value):
        if self._Doll__useFastShader != value:
            self._Doll__useFastShader = value
            self.buildDataManager.SetAllAsDirty(clearMeshes=True)


    useFastShader = property(fget=lambda self: self._Doll__useFastShader, fset=setusefastshader)


