import os
import sys
import trinity
import blue
import bluepy
import uthread
import log
import yaml
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

class UVCalculator(object):
    UVs = {PD.DOLL_PARTS.HEAD: PD.HEAD_UVS,
     PD.DOLL_PARTS.BODY: PD.BODY_UVS,
     PD.DOLL_PARTS.HAIR: PD.HAIR_UVS,
     PD.DOLL_PARTS.ACCESSORIES: PD.ACCE_UVS}

    @staticmethod
    def BoxCoversX(x, box):
        if x >= box[0] and x < box[2]:
            return True
        return False



    @staticmethod
    def GetHeightAt(x, returnUVs):
        height = 0
        newX = x
        for r in returnUVs:
            if UVCalculator.BoxCoversX(x, r):
                if r[3] > height:
                    height = r[3]
                    newX = r[2]

        return (height, newX)



    @staticmethod
    def BoxIntersects(x, y, box, uv):
        for vert in ((x, y),
         (x + box[0], y),
         (x, y + box[1]),
         (x + box[0], y + box[1])):
            if vert[0] > uv[0] and vert[0] < uv[2] and vert[1] > uv[1] and vert[1] < uv[3]:
                return True

        return False



    @staticmethod
    def BoxFits(x, y, box, target, returnUVs):
        if x < 0 or x + box[0] > target[0] or y < 0:
            return False
        for r in returnUVs:
            if UVCalculator.BoxIntersects(x, y, box, r):
                return False

        return True



    @staticmethod
    def PackTextures(textures, target):
        watermark = 0
        returnUVs = []
        xinc = 0.001953125
        for t in textures:
            candidates = {}
            minInc = 100000
            x = 0.0
            while x < 1.0:
                currentX = x
                (h, x,) = UVCalculator.GetHeightAt(currentX, returnUVs)
                inc = h + t[1]
                if UVCalculator.BoxFits(currentX, h, t, target, returnUVs):
                    if inc < minInc:
                        minInc = inc
                        candidates[inc] = (currentX, h)
                if x == currentX:
                    x += xinc

            if candidates:
                final = candidates[minInc]
                returnUVs.append((final[0],
                 final[1],
                 final[0] + t[0],
                 final[1] + t[1]))
                watermark = final[1] + t[1]

        if watermark > target[1]:
            factor = target[1] / watermark
            for ix in xrange(len(returnUVs)):
                returnUVs[ix] = [returnUVs[ix][0] * factor,
                 returnUVs[ix][1] * factor,
                 returnUVs[ix][2] * factor,
                 returnUVs[ix][3] * factor]

        return returnUVs



    @staticmethod
    def GetMapSize(modifier):
        tag = PD.ACCESSORIES_CATEGORIES.ACCESSORIES
        path = modifier.mapL.get(tag) or modifier.mapD.get(tag)
        if path:
            param = trinity.TriTexture2DParameter()
            param.resourcePath = path
            while param.resource.isLoading:
                PD.Yield()

            return (param.resource.width, param.resource.height)



    @staticmethod
    def CalculateAccessoryUVs(buildDataManager):
        accesorieModifiers = buildDataManager.GetModifiersByPart(PD.DOLL_PARTS.ACCESSORIES, showHidden=True)
        targetBox = (1.0, 1.0)
        textures = []
        for modifier in iter(accesorieModifiers):
            adjustedSize = (0.0, 0.0)
            amSize = modifier.accessoryMapSize or UVCalculator.GetMapSize(modifier)
            if amSize:
                adjustedSize = [amSize[0] / 512.0, amSize[1] / 512.0]
                if adjustedSize[0] > 0.5:
                    adjustedSize[0] = 0.5
                if adjustedSize[1] > 0.5:
                    adjustedSize[1] = 0.5
            textures.append(adjustedSize)

        result = UVCalculator.PackTextures(textures, targetBox)
        for ix in xrange(len(accesorieModifiers)):
            mod = accesorieModifiers[ix]
            mod.ulUVs = (result[ix][0], result[ix][1])
            mod.lrUVs = (result[ix][2], result[ix][3])




    @staticmethod
    def ApplyUVs(buildDataManager, renderDriver):
        UVCalculator.CalculateAccessoryUVs(buildDataManager)
        defaultUVs = dict(UVCalculator.UVs)
        modifierGenerator = (modifier for modifier in buildDataManager.GetSortedModifiers() if modifier.weight > 0 if modifier.IsMeshContainingModifier())
        for modifier in modifierGenerator:
            meshes = list(modifier.meshes)
            if modifier.clothData:
                meshes.append(modifier.clothData)
            modifierUVCategory = buildDataManager.CategoryToPart(modifier.categorie)
            for mesh in iter(meshes):
                uvCategory = modifierUVCategory
                if uvCategory == PD.DOLL_PARTS.HAIR and hasattr(mesh, 'decalAreas') and mesh.decalAreas:
                    for area in mesh.decalAreas:
                        if 'stubble' in area.name.lower():
                            uvCategory = PD.DOLL_PARTS.HEAD
                            break

                if hasattr(mesh, 'opaqueAreas') and hasattr(mesh, 'decalAreas') and hasattr(mesh, 'transparentAreas'):
                    for area in tuple(mesh.opaqueAreas) + tuple(mesh.decalAreas) + tuple(mesh.transparentAreas):
                        for category in defaultUVs:
                            if category.lower() + 'uv' in area.name.lower():
                                uvCategory = category
                                break


                fxs = PD.GetEffectsFromMesh(mesh)
                for fx in iter(fxs):
                    if type(fx) != trinity.Tr2ShaderMaterial and fx.effectResource and fx.effectResource.isLoading:
                        while fx.effectResource.isLoading:
                            PD.Yield()

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
                        width = defaultUVs[uvCategory][2] - defaultUVs[uvCategory][0]
                        height = defaultUVs[uvCategory][3] - defaultUVs[uvCategory][1]
                        computedUVs = (defaultUVs[uvCategory][0] + modifier.ulUVs[0] * width,
                         defaultUVs[uvCategory][1] + modifier.ulUVs[1] * height,
                         defaultUVs[uvCategory][0] + modifier.lrUVs[0] * width,
                         defaultUVs[uvCategory][1] + modifier.lrUVs[1] * height)
                    elif type(mesh) is trinity.Tr2ClothingActor:
                        computedUVs = (defaultUVs[uvCategory][0],
                         defaultUVs[uvCategory][3],
                         defaultUVs[uvCategory][2],
                         defaultUVs[uvCategory][1])
                    else:
                        computedUVs = (defaultUVs[uvCategory][0],
                         defaultUVs[uvCategory][1],
                         defaultUVs[uvCategory][2],
                         defaultUVs[uvCategory][3])
                    transformUV0.value = computedUVs


            renderDriver.OnModifierUVChanged(modifier)





class UpdateRuleBundle(object):
    __metaclass__ = bluepy.CCP_STATS_ZONE_PER_METHOD
    __guid__ = 'paperDoll.UpdateRuleBundle'

    def __init__(self):
        self.forcesLooseTop = False
        self.hidesBootShin = False
        self.swapTops = False
        self.swapBottom = False
        self.swapSocks = False
        self.undoMaskedShaders = False
        self.rebuildHair = False
        self.mapsToComposite = list(PD.MAPS)
        self.blendShapesOnly = False
        self.decalsOnly = False
        self.doDecals = False
        self.doBlendShapes = False
        self.doStubble = False
        self.meshesChanged = False
        self.partsToComposite = []
        self.dirtyDecalModifiers = []
        self.videoMemoryFailure = False



    def __str__(self):
        s = '{0}\n'.format(id(self))
        for (key, value,) in self.__dict__.iteritems():
            s += '\t{0} := {1}\n'.format(key, value)

        return s



    def DiscoverState(self, dirtyModifiers, avatar):
        allModifiersBlendShapes = False
        someModifiersBlendShapes = False
        allModifiersDecals = False
        someModifiersDecals = False
        for modifier in iter(dirtyModifiers):
            isBlendShapeModifier = modifier.IsBlendshapeModifier()
            isDecalModifier = not isBlendShapeModifier and modifier.decalData is not None and (modifier.IsDirty or not modifier.IsTextureContainingModifier())
            if modifier.stubblePath:
                self.doStubble = True
            if isDecalModifier:
                self.dirtyDecalModifiers.append(modifier)
            someModifiersBlendShapes = isBlendShapeModifier or someModifiersBlendShapes
            allModifiersBlendShapes = isBlendShapeModifier and allModifiersBlendShapes
            someModifiersDecals = isDecalModifier or someModifiersDecals
            allModifiersDecals = isDecalModifier and allModifiersDecals

        self.blendShapesOnly = allModifiersBlendShapes
        self.decalsOnly = allModifiersDecals and avatar is not None
        self.doBlendShapes = someModifiersBlendShapes
        self.doDecals = someModifiersDecals and avatar is not None




class MapBundle(object):
    __metaclass__ = bluepy.CCP_STATS_ZONE_PER_METHOD
    __guid__ = 'paperDoll.MapBundle'

    def __init__(self):
        self.diffuseMap = None
        self.specularMap = None
        self.normalMap = None
        self.maskMap = None
        self.baseResolution = None
        self.hashKeys = {}
        self.mapResolutions = {PD.MASK_MAP: PD.PerformanceOptions.maskMapTextureSize}
        self.mapResolutionFactors = {}
        self.SetBaseResolution(2048, 1024)
        self.busyDownScaling = False



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
        for mapType in PD.RESIZABLE_MAPS:
            factor = self.mapResolutionFactors.get(mapType, PD.PerformanceOptions.textureSizeFactors[mapType])
            self.SetMapTypeResolutionFactor(mapType, factor)




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
            while self.busyDownScaling:
                PD.Yield(frameNice=False)

            self.busyDownScaling = True
            sourceIsCompressed = mapSource.format == trinity.TRIFMT_DXT5
            targetTex = trinity.device.CreateTexture(resolution[0], resolution[1], 1, trinity.TRIUSAGE_DYNAMIC if trinity.device.UsingEXDevice() else 0, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_DEFAULT if trinity.device.UsingEXDevice() else trinity.TRIPOOL_MANAGED)
            fx = trinity.Tr2Effect()
            fx.effectFilePath = 'res:/Graphics/Effect/Utility/Compositing/Copyblit.fx'
            PD.BeFrameNice()
            while fx.effectResource.isLoading:
                PD.Yield()

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
            try:
                renderTarget = RTM.GetRenderTarget(trinity.TRIFMT_A8R8G8B8, vp.width, vp.height)
            except (trinity.E_OUTOFMEMORY, trinity.D3DERR_OUTOFVIDEOMEMORY):
                sys.exc_clear()
                self.busyDownScaling = False
                return 
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
            self.busyDownScaling = False


        t = uthread.new(fun, mapType, mapSource, resolution)
        uthread.schedule(t)



    def SetMapTypeResolutionFactor(self, mapType, factor):
        oldFactor = self.mapResolutionFactors.get(mapType, 1)
        self.mapResolutionFactors[mapType] = factor
        shift = factor - 1
        newResolution = (self.baseResolution[0] >> shift, self.baseResolution[1] >> shift)
        if newResolution[0] < 16:
            self.mapResolutionFactors[mapType] = oldFactor
            return 
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



    def ReCreate(self, includeFixedSizeMaps = True):
        del self.diffuseMap
        del self.specularMap
        del self.normalMap
        if includeFixedSizeMaps:
            del self.maskMap
        self.diffuseMap = None
        self.specularMap = None
        self.normalMap = None
        if includeFixedSizeMaps:
            self.maskMap = None
        for key in list(self.hashKeys.iterkeys()):
            if not self[key]:
                del self.hashKeys[key]




    def __repr__(self):
        s = 'Base resolution: w{}\th{}'.format(self.baseResolution[0], self.baseResolution[1])
        for mapType in PD.MAPS:
            if self[mapType]:
                cMap = self[mapType]
                s = '{}\n{}\tw{}\th{}'.format(s, PD.MAPNAMES[mapType], cMap.width, cMap.height)

        return s



    def __del__(self):
        del self.diffuseMap
        del self.specularMap
        del self.normalMap
        del self.maskMap




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
        self.verbose = False
        self.skipCompositing = False
        self.preloadedResources = list()
        self.calculatedSubrects = dict()
        self.CalculateSubrects()
        self.PreloadedGenericHeadModifiers = {PD.GENDER.MALE: None,
         PD.GENDER.FEMALE: None}
        self.PreloadShaders()
        uthread.new(self.PreloadGenericHeadsOnceLoaded_t)
        if PD.PerformanceOptions.preloadNudeAssets:
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
            PD.Yield()

        for genderData in self.resData.genderData.itervalues():
            for respath in PD.DEFAULT_NUDE_PARTS:
                entry = genderData.GetPathsToEntries()[respath]
                filenames = entry.files
                for filename in filenames:
                    if '_4k' in filename:
                        continue
                    if 'wrinkle' in filename or filename.startswith('skinmap'):
                        continue
                    if filename.endswith('.png'):
                        ddsTest = filename[:-4] + '.dds'
                        if ddsTest in filenames:
                            continue
                    resourcePath = entry.GetFullResPath(filename)
                    resource = blue.resMan.GetResource(resourcePath)
                    if resource and resource not in self.preloadedResources:
                        self.preloadedResources.append(resource)






    def PreloadGenericHeadsOnceLoaded_t(self):
        while not self.IsLoaded:
            PD.Yield()

        self.PreloadedGenericHeadModifiers[PD.GENDER.MALE] = self.CollectBuildData(PD.GENDER.MALE, 'head/head_generic')
        self.PreloadedGenericHeadModifiers[PD.GENDER.FEMALE] = self.CollectBuildData(PD.GENDER.FEMALE, 'head/head_generic')



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

        while doYield:
            doYield = False
            for lgr in loadingGrannyResources.itervalues():
                if lgr.isLoading:
                    doYield = True
                    break

            if doYield:
                try:
                    PD.Yield(frameNice=False)
                except RuntimeError:
                    PD.BeFrameNice()

        if loadingGrannyResources:
            meshCount = len(meshes)
            for mIdx in xrange(meshCount):
                mesh = meshes[mIdx]
                grannyResource = loadingGrannyResources.get(mesh.name)
                index = mesh.meshIndex
                if grannyResource and grannyResource.isGood and grannyResource.meshCount > index:
                    geometryRes = grannyResource.CreateGeometryRes()
                    geometryRes.name = 'PaperDoll: ' + mesh.name + ' morphed'
                    morphNames = grannyResource.GetAllMeshMorphNamesNoDigits(index)
                    blendShapeMeshCache[mesh.name] = (grannyResource, geometryRes, morphNames)
                elif loadingGrannyResources.get(mesh.name):
                    del loadingGrannyResources[mesh.name]

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




    @staticmethod
    @bluepy.CCP_STATS_ZONE_FUNCTION
    def ProcessBlendshapesForCloth(clothActor, morphTargets, avatar = None, clothMorphValues = None):
        clothMorphValues = clothMorphValues if clothMorphValues is not None else {}
        if clothActor.morphRes is None:
            clothActor.morphRes = blue.resMan.GetResource(clothActor.resPath.lower().replace('.apb', '_bs.gr2'), 'raw')
        while clothActor.morphRes.isLoading:
            PD.Yield()

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



    @staticmethod
    @bluepy.CCP_STATS_ZONE_FUNCTION
    def BindMapsToMeshes(meshes, mapBundle, prepass = False):
        colorNdotLLookupMap = 'ColorNdotLLookupMap'
        fresnelLookupMap = 'FresnelLookupMap'
        ndotLLibrary = 'res:/Texture/Global/NdotLLibrary.png'
        for mesh in iter(meshes):
            effects = PD.GetEffectsFromMesh(mesh, allowShaderMaterial=prepass, includePLP=prepass)
            for fx in (effect for effect in effects if effect is not None):
                if type(fx) != trinity.Tr2ShaderMaterial:
                    for r in iter(fx.resources):
                        if mapBundle.diffuseMap and r.name == PD.MAPNAMES[PD.DIFFUSE_MAP]:
                            Factory.SetResourceTexture(r, mapBundle.diffuseMap)
                        elif mapBundle.specularMap and r.name == PD.MAPNAMES[PD.SPECULAR_MAP]:
                            Factory.SetResourceTexture(r, mapBundle.specularMap)
                        elif mapBundle.normalMap and r.name == PD.MAPNAMES[PD.NORMAL_MAP]:
                            Factory.SetResourceTexture(r, mapBundle.normalMap)
                        elif mapBundle.maskMap and r.name == PD.MAPNAMES[PD.MASK_MAP]:
                            Factory.SetResourceTexture(r, mapBundle.maskMap)

                elif type(fx) == trinity.Tr2ShaderMaterial:
                    if mapBundle.diffuseMap and PD.MAPNAMES[PD.DIFFUSE_MAP] in fx.parameters:
                        fx.parameters[PD.MAPNAMES[PD.DIFFUSE_MAP]].SetResource(mapBundle.diffuseMap)
                    if mapBundle.specularMap and PD.MAPNAMES[PD.SPECULAR_MAP] in fx.parameters:
                        fx.parameters[PD.MAPNAMES[PD.SPECULAR_MAP]].SetResource(mapBundle.specularMap)
                    if mapBundle.normalMap and PD.MAPNAMES[PD.NORMAL_MAP] in fx.parameters:
                        fx.parameters[PD.MAPNAMES[PD.NORMAL_MAP]].SetResource(mapBundle.normalMap)
                    if mapBundle.maskMap and PD.MAPNAMES[PD.MASK_MAP] in fx.parameters:
                        fx.parameters[PD.MAPNAMES[PD.MASK_MAP]].SetResource(mapBundle.maskMap)
                    fx.RebuildCachedDataInternal()
                ndotLres = None
                fresnelLookupMapRes = None
                if type(fx) != trinity.Tr2ShaderMaterial:
                    for r in iter(fx.resources):
                        if r.name == colorNdotLLookupMap:
                            ndotLres = r
                        elif r.name == fresnelLookupMap:
                            fresnelLookupMapRes = r

                if ndotLres is None:
                    res = trinity.TriTexture2DParameter()
                    res.name = colorNdotLLookupMap
                    res.resourcePath = ndotLLibrary
                    if type(fx) == trinity.Tr2ShaderMaterial:
                        fx.parameters[res.name] = res
                    else:
                        fx.resources.append(res)
                else:
                    ndotLres.resourcePath = ndotLLibrary
                if fresnelLookupMapRes is None:
                    res = trinity.TriTexture2DParameter()
                    res.name = fresnelLookupMap
                    res.resourcePath = PD.FRESNEL_LOOKUP_MAP
                    if type(fx) == trinity.Tr2ShaderMaterial:
                        fx.parameters[res.name] = res
                    else:
                        fx.resources.append(res)
                else:
                    fresnelLookupMapRes.resourcePath = PD.FRESNEL_LOOKUP_MAP





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
                        os.utime(filePath, None)
                        cachedTexture = blue.resMan.GetResourceW(rotPath)
                        return cachedTexture
        except Exception:
            sys.exc_clear()



    @bluepy.CCP_STATS_ZONE_METHOD
    def SaveMaps(self, hashKey, maps):
        cachePath = self.GetMapCachePath()
        if not cachePath:
            return 
        try:
            for (i, each,) in enumerate(maps):
                if each is not None:
                    textureWidth = each.width
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



    def RebindAnimations(self, avatar, visualModel):
        if avatar:
            avatar.ResetAnimationBindings()
        elif visualModel:
            visualModel.ResetAnimationBindings()



    @bluepy.CCP_STATS_ZONE_METHOD
    def CreateAnimationOffsets(self, avatar, doll):
        if avatar.animationUpdater and getattr(avatar.animationUpdater, 'network', None):
            if doll.boneOffsets:
                setOffset = avatar.animationUpdater.network.boneOffset.SetOffset
                for bone in doll.boneOffsets.iterkeys():
                    trans = doll.boneOffsets[bone][PD.TRANSLATION]
                    setOffset(bone, *trans)




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
        isNormalMap = mapType == PD.NORMAL_MAP
        if not partsToComposite or PD.DOLL_PARTS.BODY in partsToComposite:
            PD.BeFrameNice()
            baseBodyTexture = genTex.get(PD.DOLL_PARTS.BODY, '')
            if baseBodyTexture:
                comp.CopyBlitTexture(baseBodyTexture, self.GetSubRect(PD.DOLL_PARTS.BODY, w, h), isNormalMap=isNormalMap, alphaMultiplier=0.0 if isNormalMap else 1.0)
            self._CompositeTexture(modifierList, PD.DOLL_PARTS.BODY, comp, mapType, w, h, addAlpha=True, lod=lod)
        if not partsToComposite or PD.DOLL_PARTS.HEAD in partsToComposite or PD.DOLL_PARTS.HAIR in partsToComposite:
            PD.BeFrameNice()
            baseHeadTexture = genTex.get(PD.DOLL_PARTS.HEAD, '')
            if baseHeadTexture:
                comp.CopyBlitTexture(baseHeadTexture, self.GetSubRect(PD.DOLL_PARTS.HEAD, w, h), isNormalMap=isNormalMap, alphaMultiplier=0.0 if isNormalMap else 1.0)
            self._CompositeTexture(modifierList, PD.DOLL_PARTS.HEAD, comp, mapType, w, h, addAlpha=False, lod=lod)
        if not partsToComposite or PD.DOLL_PARTS.HAIR in partsToComposite:
            PD.BeFrameNice()
            self._CompositeTexture(modifierList, PD.DOLL_PARTS.HAIR, comp, mapType, w, h, addAlpha=False, lod=lod)
        if not partsToComposite or PD.DOLL_PARTS.ACCESSORIES in partsToComposite:
            PD.BeFrameNice()
            self._CompositeTexture(modifierList, PD.DOLL_PARTS.ACCESSORIES, comp, mapType, w, h, addAlpha=False, lod=lod)



    @bluepy.CCP_STATS_ZONE_METHOD
    def CompositeCombinedTexture(self, mapType, gender, buildDataManager, mapBundle, textureCompositor, compressionSettings = None, partsToComposite = None, copyToExistingTexture = False, lod = None):
        try:
            if compressionSettings is None:
                compressionSettings = self
            (w, h,) = mapBundle.GetResolutionByMapType(mapType)
            textureFormat = trinity.TRIFMT_A8R8G8B8
            renderTarget = RTM.GetRenderTarget(textureFormat, w, h)
            w = renderTarget.width
            h = renderTarget.height
            textureCompositor.renderTarget = renderTarget
            textureCompositor.targetWidth = w
            textureCompositor.Start(clear=False)
            if mapBundle[mapType]:
                textureCompositor.CopyBlitTexture(mapBundle[mapType])
            self.CompositeStepsFunction(buildDataManager, gender, mapType, partsToComposite, textureCompositor, w, h, lod=lod)
            textureCompositor.End()
            while not textureCompositor.isReady:
                PD.Yield()

            if copyToExistingTexture:
                tex = textureCompositor.Finalize(textureFormat, w, h, generateMipmap=compressionSettings.generateMipmap, textureToCopyTo=mapBundle[mapType])
            else:
                tex = textureCompositor.Finalize(textureFormat, w, h, generateMipmap=compressionSettings.generateMipmap)
            textureCompositor.renderTarget = None
            compressedTexture = Factory.ApplyCompressionSettingToTexture(compressionSettings, tex, mapType)
            if compressedTexture:
                tex = compressedTexture
            return tex
        except (trinity.E_OUTOFMEMORY, trinity.D3DERR_OUTOFVIDEOMEMORY):
            raise 
        except TaskletExit:
            if textureCompositor:
                textureCompositor.renderTarget = None
            raise 



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
        compressedTexture = trinity.device.CreateTexture(tex.width, tex.height, 1, trinity.TRIUSAGE_DYNAMIC if trinity.device.UsingEXDevice() else 0, trinity.TRIFMT_DXT5, trinity.TRIPOOL_DEFAULT if trinity.device.UsingEXDevice() else trinity.TRIPOOL_MANAGED)
        compressionFormat = COMPRESS_DXT5n if mapType is PD.NORMAL_MAP else COMPRESS_DXT5
        while not compressedTexture.isPrepared:
            PD.Yield(frameNice=False)

        try:
            trinity.device.CompressSurfaceWithQuality(tex.GetSurfaceLevel(0), compressedTexture.GetSurfaceLevel(0), compressionFormat, qualityLevel)
            while not compressedTexture.isPrepared:
                PD.Yield(frameNice=False)

        except TaskletExit:
            raise 
        AddMarker('compress done')
        return compressedTexture



    @bluepy.CCP_STATS_ZONE_METHOD
    def _CompositeDiffuseMap(self, modifierList, bodyPart, textureCompositor, width, height, addAlpha = False, lod = 0):
        for m in iter(modifierList):
            PD.BeFrameNice()
            if m.stubblePath and lod in [PD.LOD_SKIN, PD.LOD_SCATTER_SKIN]:
                continue
            subrect = self.GetSubRect(bodyPart, width, height, m)
            srcRect = None
            texture = m.mapD
            skipAlpha = False
            useAlphaTest = False
            if m.colorize and bodyPart in m.mapL:
                if bodyPart not in m.mapO:
                    m.mapO[bodyPart] = PD.TEXTURE_STUB
                if bodyPart not in m.mapZ:
                    m.mapZ[bodyPart] = PD.TEXTURE_STUB
                if m.categorie in (PD.BODY_CATEGORIES.SKINTONE,
                 PD.BODY_CATEGORIES.SKINTYPE,
                 PD.HEAD_CATEGORIES.MAKEUP,
                 PD.BODY_CATEGORIES.TATTOO,
                 PD.BODY_CATEGORIES.SCARS,
                 PD.DOLL_EXTRA_PARTS.BODYSHAPES,
                 PD.HEAD_CATEGORIES.FACEMODIFIERS):
                    if PD.MAKEUP_GROUPS.IMPLANTS in m.group:
                        skipAlpha = False
                        addAlpha = True
                    elif PD.MAKEUP_GROUPS.EYELASHES in m.group or PD.MAKEUP_GROUPS.EYEBROWS in m.group:
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
                    patternPath = '{0}/{1}_z.dds'.format(patternDir, m.pattern)
                    if blue.rot.loadFromContent:
                        if not os.path.exists(PD.OUTSOURCING_JESSICA_PATH):
                            patternPath = patternPath.replace('.dds', '.tga')
                    textureCompositor.PatternBlitTexture(patternPath, m.mapL[bodyPart], m.mapZ[bodyPart], m.mapO[bodyPart], colors[0], colors[1], colors[2], colors[3], colors[4], subrect, patternTransform=colors[5], patternRotation=colors[6], addAlpha=addAlpha, skipAlpha=skipAlpha)
            if bodyPart in texture and not (m.colorize and m.categorie == PD.BODY_CATEGORIES.TATTOO):
                maskname = tname = texture[bodyPart]
                if not (isinstance(tname, basestring) and PD.SKIN_GENERIC_PATH in tname.lower()):
                    if bodyPart in texture:
                        maskname = texture[bodyPart]
                    elif bodyPart in m.mapL:
                        maskname = m.mapL[bodyPart]
                    skipAlpha = False
                    if m.categorie in (PD.BODY_CATEGORIES.SKINTONE,
                     PD.BODY_CATEGORIES.SKINTYPE,
                     PD.HEAD_CATEGORIES.MAKEUP,
                     PD.BODY_CATEGORIES.TATTOO,
                     PD.BODY_CATEGORIES.SCARS,
                     PD.DOLL_EXTRA_PARTS.BODYSHAPES,
                     PD.HEAD_CATEGORIES.ARCHETYPES,
                     PD.HEAD_CATEGORIES.FACEMODIFIERS):
                        if PD.MAKEUP_GROUPS.EYELASHES in m.group:
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
    def _CompositeSpecularMap--- This code section failed: ---
0	SETUP_LOOP        '801'
3	LOAD_GLOBAL       'iter'
6	LOAD_FAST         'modifierList'
9	CALL_FUNCTION_1   ''
12	GET_ITER          ''
13	FOR_ITER          '800'
16	STORE_FAST        'm'
19	LOAD_GLOBAL       'PD'
22	LOAD_ATTR         'BeFrameNice'
25	CALL_FUNCTION_0   ''
28	POP_TOP           ''
29	LOAD_FAST         'm'
32	LOAD_ATTR         'stubblePath'
35	POP_JUMP_IF_FALSE '68'
38	LOAD_FAST         'lod'
41	LOAD_GLOBAL       'PD'
44	LOAD_ATTR         'LOD_SKIN'
47	LOAD_GLOBAL       'PD'
50	LOAD_ATTR         'LOD_SCATTER_SKIN'
53	BUILD_LIST_2      ''
56	COMPARE_OP        'in'
59_0	COME_FROM         '35'
59	POP_JUMP_IF_FALSE '68'
62	JUMP_BACK         '13'
65	JUMP_FORWARD      '68'
68_0	COME_FROM         '65'
68	LOAD_FAST         'self'
71	LOAD_ATTR         'GetSubRect'
74	LOAD_FAST         'bodyPart'
77	LOAD_FAST         'width'
80	LOAD_FAST         'height'
83	LOAD_FAST         'm'
86	CALL_FUNCTION_4   ''
89	STORE_FAST        'subrect'
92	LOAD_CONST        ''
95	STORE_FAST        'srcRect'
98	LOAD_GLOBAL       'False'
101	STORE_FAST        'skipAlpha'
104	LOAD_FAST         'm'
107	LOAD_ATTR         'mapSRG'
110	LOAD_ATTR         'get'
113	LOAD_FAST         'bodyPart'
116	CALL_FUNCTION_1   ''
119	DUP_TOP           ''
120	STORE_FAST        'maskname'
123	STORE_FAST        'tname'
126	LOAD_FAST         'bodyPart'
129	LOAD_FAST         'm'
132	LOAD_ATTR         'mapSRG'
135	COMPARE_OP        'in'
138	POP_JUMP_IF_FALSE '13'
141	LOAD_FAST         'm'
144	LOAD_ATTR         'categorie'
147	LOAD_GLOBAL       'PD'
150	LOAD_ATTR         'BODY_CATEGORIES'
153	LOAD_ATTR         'TATTOO'
156	COMPARE_OP        '=='
159	JUMP_IF_TRUE_OR_POP '195'
162	LOAD_GLOBAL       'isinstance'
165	LOAD_FAST         'tname'
168	LOAD_GLOBAL       'basestring'
171	CALL_FUNCTION_2   ''
174	JUMP_IF_FALSE_OR_POP '195'
177	LOAD_GLOBAL       'PD'
180	LOAD_ATTR         'SKIN_GENERIC_PATH'
183	LOAD_FAST         'tname'
186	LOAD_ATTR         'lower'
189	CALL_FUNCTION_0   ''
192	COMPARE_OP        'in'
195_0	COME_FROM         '159'
195_1	COME_FROM         '174'
195	UNARY_NOT         ''
196	POP_JUMP_IF_FALSE '13'
199	LOAD_FAST         'bodyPart'
202	LOAD_FAST         'm'
205	LOAD_ATTR         'mapD'
208	COMPARE_OP        'in'
211	POP_JUMP_IF_FALSE '230'
214	LOAD_FAST         'm'
217	LOAD_ATTR         'mapD'
220	LOAD_FAST         'bodyPart'
223	BINARY_SUBSCR     ''
224	STORE_FAST        'maskname'
227	JUMP_FORWARD      '261'
230	LOAD_FAST         'bodyPart'
233	LOAD_FAST         'm'
236	LOAD_ATTR         'mapL'
239	COMPARE_OP        'in'
242	POP_JUMP_IF_FALSE '261'
245	LOAD_FAST         'm'
248	LOAD_ATTR         'mapL'
251	LOAD_FAST         'bodyPart'
254	BINARY_SUBSCR     ''
255	STORE_FAST        'maskname'
258	JUMP_FORWARD      '261'
261_0	COME_FROM         '227'
261_1	COME_FROM         '258'
261	LOAD_GLOBAL       'True'
264	STORE_FAST        'skipAlpha'
267	LOAD_GLOBAL       'True'
270	STORE_FAST        'addAlpha'
273	LOAD_FAST         'm'
276	LOAD_ATTR         'useSkin'
279	POP_JUMP_IF_FALSE '303'
282	LOAD_FAST         'tname'
285	LOAD_ATTR         'replace'
288	LOAD_CONST        '_S.'
291	LOAD_CONST        '_SR.'
294	CALL_FUNCTION_2   ''
297	STORE_FAST        'tname'
300	JUMP_FORWARD      '303'
303_0	COME_FROM         '300'
303	LOAD_GLOBAL       'False'
306	STORE_FAST        'doColorizedStep'
309	LOAD_FAST         'm'
312	LOAD_ATTR         'colorize'
315	POP_JUMP_IF_FALSE '577'
318	LOAD_FAST         'm'
321	LOAD_ATTR         'specularColorData'
324_0	COME_FROM         '315'
324	POP_JUMP_IF_FALSE '577'
327	LOAD_FAST         'bodyPart'
330	LOAD_FAST         'm'
333	LOAD_ATTR         'mapL'
336	COMPARE_OP        'in'
339	STORE_FAST        'doColorizedStep'
342	LOAD_FAST         'bodyPart'
345	LOAD_GLOBAL       'PD'
348	LOAD_ATTR         'DOLL_PARTS'
351	LOAD_ATTR         'HAIR'
354	COMPARE_OP        '=='
357	POP_JUMP_IF_FALSE '394'
360	LOAD_FAST         'textureCompositor'
363	LOAD_ATTR         'CopyBlitTexture'
366	LOAD_FAST         'tname'
369	LOAD_CONST        'subrect'
372	LOAD_FAST         'subrect'
375	LOAD_CONST        'srcRect'
378	LOAD_FAST         'srcRect'
381	CALL_FUNCTION_513 ''
384	POP_TOP           ''
385	LOAD_GLOBAL       'True'
388	STORE_FAST        'doColorizedStep'
391	JUMP_FORWARD      '394'
394_0	COME_FROM         '391'
394	LOAD_FAST         'doColorizedStep'
397	POP_JUMP_IF_FALSE '577'
400	LOAD_FAST         'bodyPart'
403	LOAD_FAST         'm'
406	LOAD_ATTR         'mapO'
409	COMPARE_OP        'not in'
412	POP_JUMP_IF_FALSE '434'
415	LOAD_GLOBAL       'PD'
418	LOAD_ATTR         'TEXTURE_STUB'
421	LOAD_FAST         'm'
424	LOAD_ATTR         'mapO'
427	LOAD_FAST         'bodyPart'
430	STORE_SUBSCR      ''
431	JUMP_FORWARD      '434'
434_0	COME_FROM         '431'
434	LOAD_FAST         'bodyPart'
437	LOAD_FAST         'm'
440	LOAD_ATTR         'mapZ'
443	COMPARE_OP        'not in'
446	POP_JUMP_IF_FALSE '468'
449	LOAD_GLOBAL       'PD'
452	LOAD_ATTR         'TEXTURE_STUB'
455	LOAD_FAST         'm'
458	LOAD_ATTR         'mapZ'
461	LOAD_FAST         'bodyPart'
464	STORE_SUBSCR      ''
465	JUMP_FORWARD      '468'
468_0	COME_FROM         '465'
468	LOAD_FAST         'm'
471	LOAD_ATTR         'specularColorData'
474	STORE_FAST        'colors'
477	LOAD_FAST         'textureCompositor'
480	LOAD_ATTR         'ColorizedBlitTexture'
483	LOAD_FAST         'm'
486	LOAD_ATTR         'mapSRG'
489	LOAD_FAST         'bodyPart'
492	BINARY_SUBSCR     ''
493	LOAD_FAST         'm'
496	LOAD_ATTR         'mapZ'
499	LOAD_FAST         'bodyPart'
502	BINARY_SUBSCR     ''
503	LOAD_FAST         'm'
506	LOAD_ATTR         'mapO'
509	LOAD_FAST         'bodyPart'
512	BINARY_SUBSCR     ''
513	LOAD_FAST         'colors'
516	LOAD_CONST        ''
519	BINARY_SUBSCR     ''
520	LOAD_FAST         'colors'
523	LOAD_CONST        1
526	BINARY_SUBSCR     ''
527	LOAD_FAST         'colors'
530	LOAD_CONST        2
533	BINARY_SUBSCR     ''
534	LOAD_CONST        'mask'
537	LOAD_FAST         'maskname'
540	LOAD_CONST        'subrect'
543	LOAD_FAST         'subrect'
546	LOAD_CONST        'addAlpha'
549	LOAD_FAST         'addAlpha'
552	LOAD_CONST        'skipAlpha'
555	LOAD_FAST         'skipAlpha'
558	LOAD_CONST        'weight'
561	LOAD_FAST         'm'
564	LOAD_ATTR         'weight'
567	CALL_FUNCTION_1286 ''
570	POP_TOP           ''
571	JUMP_ABSOLUTE     '577'
574	JUMP_FORWARD      '577'
577_0	COME_FROM         '574'
577	LOAD_FAST         'doColorizedStep'
580	POP_JUMP_IF_TRUE  '638'
583	LOAD_FAST         'textureCompositor'
586	LOAD_ATTR         'BlitTexture'
589	LOAD_FAST         'tname'
592	LOAD_FAST         'maskname'
595	LOAD_FAST         'm'
598	LOAD_ATTR         'weight'
601	LOAD_CONST        'subrect'
604	LOAD_FAST         'subrect'
607	LOAD_CONST        'addAlpha'
610	LOAD_FAST         'addAlpha'
613	LOAD_CONST        'skipAlpha'
616	LOAD_FAST         'skipAlpha'
619	LOAD_CONST        'srcRect'
622	LOAD_FAST         'srcRect'
625	LOAD_CONST        'multAlpha'
628	LOAD_GLOBAL       'False'
631	CALL_FUNCTION_1283 ''
634	POP_TOP           ''
635	JUMP_FORWARD      '638'
638_0	COME_FROM         '635'
638	LOAD_FAST         'm'
641	LOAD_ATTR         'colorize'
644	POP_JUMP_IF_FALSE '766'
647	LOAD_FAST         'm'
650	LOAD_ATTR         'specularColorData'
653	POP_JUMP_IF_FALSE '766'
656	LOAD_FAST         'bodyPart'
659	LOAD_FAST         'm'
662	LOAD_ATTR         'mapZ'
665	COMPARE_OP        'in'
668_0	COME_FROM         '644'
668_1	COME_FROM         '653'
668	POP_JUMP_IF_FALSE '766'
671	LOAD_FAST         'm'
674	LOAD_ATTR         'specularColorData'
677	LOAD_CONST        ''
680	BINARY_SUBSCR     ''
681	LOAD_CONST        3
684	BINARY_SUBSCR     ''
685	LOAD_FAST         'm'
688	LOAD_ATTR         'specularColorData'
691	LOAD_CONST        1
694	BINARY_SUBSCR     ''
695	LOAD_CONST        3
698	BINARY_SUBSCR     ''
699	LOAD_FAST         'm'
702	LOAD_ATTR         'specularColorData'
705	LOAD_CONST        2
708	BINARY_SUBSCR     ''
709	LOAD_CONST        3
712	BINARY_SUBSCR     ''
713	LOAD_CONST        1.0
716	BUILD_TUPLE_4     ''
719	STORE_FAST        'values'
722	LOAD_FAST         'textureCompositor'
725	LOAD_ATTR         'BlitAlphaIntoAlphaWithMaskAndZones'
728	LOAD_FAST         'tname'
731	LOAD_FAST         'maskname'
734	LOAD_FAST         'm'
737	LOAD_ATTR         'mapZ'
740	LOAD_FAST         'bodyPart'
743	BINARY_SUBSCR     ''
744	LOAD_FAST         'values'
747	LOAD_CONST        'subrect'
750	LOAD_FAST         'subrect'
753	LOAD_CONST        'srcRect'
756	LOAD_FAST         'srcRect'
759	CALL_FUNCTION_516 ''
762	POP_TOP           ''
763	JUMP_ABSOLUTE     '797'
766	LOAD_FAST         'textureCompositor'
769	LOAD_ATTR         'BlitAlphaIntoAlphaWithMask'
772	LOAD_FAST         'tname'
775	LOAD_FAST         'maskname'
778	LOAD_CONST        'subrect'
781	LOAD_FAST         'subrect'
784	LOAD_CONST        'srcRect'
787	LOAD_FAST         'srcRect'
790	CALL_FUNCTION_514 ''
793	POP_TOP           ''
794	JUMP_BACK         '13'
797	JUMP_BACK         '13'
800_0	COME_FROM         '13'
800	POP_BLOCK         ''
801_0	COME_FROM         '0'

Syntax error at or near `COME_FROM' token at offset 800_0

    @bluepy.CCP_STATS_ZONE_METHOD
    def _CompositeNormalMap(self, modifierList, bodyPart, textureCompositor, width, height, addAlpha = False, lod = None):
        for m in iter(modifierList):
            PD.BeFrameNice()
            if m.categorie == PD.DOLL_EXTRA_PARTS.BODYSHAPES and lod > PD.LOD_0:
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
                 PD.BODY_CATEGORIES.SKINTYPE,
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
             PD.BODY_CATEGORIES.SKINTYPE,
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
            PD.BeFrameNice()
            texture = m.mapMask
            subrect = self.GetSubRect(bodyPart, width, height, m)
            srcRect = None
            skipAlpha = False
            if bodyPart in texture:
                maskname = tname = texture[bodyPart]
                tname = texture[bodyPart].lower()
                textureCompositor.BlitTexture(tname, maskname, m.weight, subrect=subrect, addAlpha=addAlpha, skipAlpha=skipAlpha, srcRect=srcRect, multAlpha=False)
                if not (isinstance(tname, basestring) and PD.SKIN_GENERIC_PATH in tname):
                    skipAlpha = False
                    if m.categorie in (PD.BODY_CATEGORIES.SKINTONE,
                     PD.BODY_CATEGORIES.SKINTYPE,
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


class OutOfVideoMemoryException(Exception):
    __guid__ = 'paperDoll.OutOfVideoMemoryException'


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
        self._Doll__updateFrameStamp = -1
        self._Doll__useFastShader = False
        self.renderDriver = PD.renderDrivers.RenderDriverNCC()
        self.lastRenderDriverClass = None
        self._currentUpdateTasklet = None
        self._UpdateTaskletChildren = []
        self.decalBaker = None
        trinity.device.RegisterResource(self)
        self.deviceResetAvatar = None
        self.useMaskedShaders = False
        self.useDXT5N = False
        self.usePrepassAlphaTestHair = False
        self.blendShapeMeshCache = {}
        self.tempClothMeshes = []
        self.tempClothCache = {}
        self.clothMorphValues = {}



    def __del__(self):
        self.StopPaperDolling()
        self.skinLightmapRenderer = None
        del self.mapBundle



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
        if self.currentLOD == PD.LOD_SCATTER_SKIN and not self.usePrepass:

            def skinCreate_t():
                if self.skinLightmapRenderer is None:
                    self.skinLightmapRenderer = PD.SkinLightmapRenderer(useOptix=self.currentLOD == PD.LOD_RAYTRACE)
                self.skinLightmapRenderer.SetSkinnedObject(self.deviceResetAvatar)
                self.skinLightmapRenderer.StartRendering()
                self.deviceResetAvatar = None


            t = uthread.new(skinCreate_t)
            uthread.schedule(t)



    def StopPaperDolling(self, clearMaps = True):
        for each in self.buildDataManager.GetModifiersAsList():
            each.ClearCachedData()

        if clearMaps:
            self.mapBundle.ReCreate()
        self.decalBaker = None



    def SetUsePrepass(self, val = True):
        self.usePrepass = val
        if val == True:
            self.lastRenderDriverClass = self.renderDriver.__class__
            if PD.PerformanceOptions.collapseShadowMesh or PD.PerformanceOptions.collapseMainMesh or PD.PerformanceOptions.collapsePLPMesh:
                self.renderDriver = PD.renderDrivers.RenderDriverCollapsePLP()
            else:
                self.renderDriver = PD.renderDrivers.RenderDriverPLP()
        elif self.lastRenderDriverClass:
            lastClass = self.renderDriver.__class__
            self.renderDriver = self.lastRenderDriverClass()
            self.lastRenderDriverClass = lastClass



    def IsPrepass(self):
        if self.usePrepass:
            return True
        return False



    def GetMorphsFromGr2(self, gr2Path):
        names = {}
        resMan = blue.resMan
        gr2Res = resMan.GetResource(gr2Path, 'raw')
        while gr2Res.isLoading:
            PD.Yield()

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
        modifierList = buildDataManager.GetModifiersAsList()
        forcesLooseTop = False
        hidesBootShin = False
        swapTops = False
        swapBottom = False
        swapSocks = False
        useMaskedShaders = False
        for modifier in iter(modifierList):
            useMaskedShaders = True
            metaData = modifier.metaData
            if metaData:
                forcesLooseTop = forcesLooseTop or metaData.forcesLooseTop
                hidesBootShin = hidesBootShin or metaData.hidesBootShin
                swapTops = swapTops or metaData.swapTops
                swapBottom = swapBottom or metaData.swapBottom
                swapSocks = swapSocks or metaData.swapSocks

        if not useMaskedShaders and self.useMaskedShaders:
            updateRuleBundle.undoMaskedShaders = True
        if hidesBootShin:
            buildDataManager.ChangeDesiredOrder(PD.BODY_CATEGORIES.FEET, PD.BODY_CATEGORIES.FEETTUCKED)
        else:
            buildDataManager.ChangeDesiredOrder(PD.BODY_CATEGORIES.FEETTUCKED, PD.BODY_CATEGORIES.FEET)
        if forcesLooseTop:
            buildDataManager.ChangeDesiredOrder(PD.BODY_CATEGORIES.BOTTOMOUTERTUCKED, PD.BODY_CATEGORIES.BOTTOMOUTER)
        else:
            buildDataManager.ChangeDesiredOrder(PD.BODY_CATEGORIES.BOTTOMOUTER, PD.BODY_CATEGORIES.BOTTOMOUTERTUCKED)
        if swapTops:
            buildDataManager.ChangeDesiredOrder(PD.BODY_CATEGORIES.TOPMIDDLE, PD.BODY_CATEGORIES.TOPTIGHT)
        else:
            buildDataManager.ChangeDesiredOrder(PD.BODY_CATEGORIES.TOPTIGHT, PD.BODY_CATEGORIES.TOPMIDDLE)
        if swapBottom:
            buildDataManager.ChangeDesiredOrder(PD.BODY_CATEGORIES.TOPUNDERWEARTUCKED, PD.BODY_CATEGORIES.TOPUNDERWEAR)
        else:
            buildDataManager.ChangeDesiredOrder(PD.BODY_CATEGORIES.TOPUNDERWEAR, PD.BODY_CATEGORIES.TOPUNDERWEARTUCKED)
        if swapSocks:
            buildDataManager.ChangeDesiredOrder(PD.BODY_CATEGORIES.SOCKS, PD.BODY_CATEGORIES.SOCKSTUCKED)
        else:
            buildDataManager.ChangeDesiredOrder(PD.BODY_CATEGORIES.SOCKSTUCKED, PD.BODY_CATEGORIES.SOCKS)
        self.useMaskedShaders = useMaskedShaders
        updateRuleBundle.forcesLooseTop = forcesLooseTop
        updateRuleBundle.hidesBootShin = hidesBootShin
        updateRuleBundle.swapTops = swapTops
        updateRuleBundle.swapBottom = swapBottom
        updateRuleBundle.swapSocks = swapSocks



    def AdjustGr2PathForLod(self, gr2Path, resDataEntry):
        adjustedGr2Path = resDataEntry.GetGeoLodMatch(gr2Path, self.currentLOD)
        return adjustedGr2Path



    def __AdjustMeshForLod(self, mesh, resDataEntry):
        mesh.geometryResPath = self.AdjustGr2PathForLod(mesh.geometryResPath, resDataEntry)



    def AdjustRedFileForLod(self, redfile, resDataEntry):
        if not (resDataEntry and PD.PerformanceOptions.useLodForRedfiles):
            return redfile
        return resDataEntry.GetGeoLodMatch(redfile, self.currentLOD)



    def _ProcessRules(self, factory, buildDataManager, modifierList, updateRuleBundle, useCloth = False):
        if not modifierList:
            return 
        if updateRuleBundle.rebuildHair:
            hairModifiers = [ x for x in buildDataManager.GetHairModifiers() if x not in modifierList ]
            modifierList.extend(hairModifiers)
        loadedObjects = {}
        modifiersWithDataToLoad = [ modifier for modifier in modifierList if modifier.weight > 0 and modifier.redfile and not modifier.meshes or modifier.IsMeshDirty() ]
        modLen = len(modifiersWithDataToLoad)
        remIdx = []
        AdjustRedFileForLod = self.AdjustRedFileForLod
        GetResDataEntryByFullResPath = factory.resData.GetEntryByFullResPath
        LoadObject = blue.os.LoadObject
        for i in xrange(modLen):
            modifier = modifiersWithDataToLoad[i]
            redfile = modifier.clothOverride if useCloth and modifier.clothOverride else modifier.redfile
            if id(modifier) not in loadedObjects:
                resDataEntry = GetResDataEntryByFullResPath(redfile)
                redfileLod = AdjustRedFileForLod(redfile, resDataEntry)
                self.renderDriver.OnModifierRedfileLoaded(modifier, redfileLod)
                if not modifier.meshes or redfileLod != modifier.redfile:
                    objToLoad = LoadObject(redfileLod)
                    if objToLoad is None:
                        objToLoad = LoadObject(redfile)
                    loadedObjects[id(modifier)] = objToLoad
                else:
                    remIdx.insert(0, i)
            PD.BeFrameNice()

        for i in iter(remIdx):
            del modifiersWithDataToLoad[i]

        pathCache = {}
        for modifier in iter(modifiersWithDataToLoad):
            modifier.ClearCachedData()
            newBodyPart = loadedObjects.get(id(modifier), None)
            if newBodyPart and hasattr(newBodyPart, 'meshes'):
                for (i, mesh,) in enumerate(newBodyPart.meshes):
                    oldPath = mesh.geometryResPath
                    newPath = pathCache.get(oldPath)
                    if newPath:
                        mesh.geometryResPath = newPath
                    else:
                        self._Doll__AdjustMeshForLod(mesh, resDataEntry)
                        pathCache[oldPath] = mesh.geometryResPath
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





    @bluepy.CCP_STATS_ZONE_METHOD
    def __ApplyUVs(self):
        UVCalculator.ApplyUVs(self.buildDataManager, self.renderDriver)



    def _HandleBlendShapes(self, removedModifiers = None, avatar = None, updateClothMeshes = True):
        self.decalBaker = None
        self.SpawnUpdateChildTasklet(self._Doll__HandleBlendShapes_t, removedModifiers, updateClothMeshes, avatar)



    @bluepy.CCP_STATS_ZONE_METHOD
    def __HandleBlendShapes_t(self, removedModifiers, updateClothMeshes, avatar):
        try:
            self.busyHandlingBlendshapes = True
            PD.BeFrameNice()
            modifierList = self.buildDataManager.GetModifiersAsList()
            morphTargets = self.buildDataManager.GetMorphTargets()
            if morphTargets:
                meshGeometryResPaths = {}
                for modifier in iter(modifierList):
                    meshGeometryResPaths.update(modifier.meshGeometryResPaths)

                meshesWithCloth = self.buildDataManager.GetMeshes(includeClothMeshes=True)
                clothMeshes = [ mesh for mesh in meshesWithCloth if type(mesh) == trinity.Tr2ClothingActor ]
                meshes = [ mesh for mesh in meshesWithCloth if type(mesh) == trinity.Tr2Mesh ]
                Factory.ApplyMorphTargetsToMeshes(meshes, morphTargets, self.blendShapeMeshCache, meshGeometryResPaths, clothMeshes=clothMeshes, updateClothMeshes=updateClothMeshes, avatar=avatar, clothMorphValues=self.clothMorphValues)
                self.renderDriver.OnApplyMorphTargets(meshes, morphTargets, self.clothMorphValues)
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
        modifiersDone = {}
        for modifier in (modifier for modifier in self.buildDataManager.GetModifiersAsList() if modifier.poseData):
            if modifier.respath not in modifiersDone:
                modifiersDone[modifier.respath] = None
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
                if PD.MAKEUP_GROUPS.EYELASHES in makeup.group:
                    foundEyelashes = True
                    break

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
        if not factory.resData.QueryPathByGender(self.gender, pathlower):
            log.LogWarn("Paperdoll - Doll::CreateModifierFromFootPrint is creating modifier that doesn't exist in options.")
            modifier = PD.BuildData(pathlower)
            modifier.weight = float(footPrint[PD.DNA_STRINGS.WEIGHT])
            doDecal(modifier)
        else:
            variation = footPrint.get(PD.DNA_STRINGS.VARIATION)
            modifier = self._AddResource(pathlower, footPrint.get(PD.DNA_STRINGS.WEIGHT), factory, variation=variation)
            modifier.pattern = footPrint.get(PD.DNA_STRINGS.PATTERN, '')
            modifier.tuck = footPrint.get(PD.DNA_STRINGS.TUCK, False)
            if isinstance(footPrint.get(PD.DNA_STRINGS.COLORS), basestring):
                colorData = eval(footPrint.get(PD.DNA_STRINGS.COLORS))
            else:
                colorData = footPrint.get(PD.DNA_STRINGS.COLORS)
            colorizeDataSet = False
            if colorData:
                if modifier.pattern:
                    modifier.patternData = colorData
                    if len(modifier.patternData) == 5:
                        modifier.patternData.append((0, 0, 8, 8))
                        modifier.patternData.append(0.0)
                else:
                    modifier.colorizeData = colorData
                    colorizeDataSet = True
            if PD.DNA_STRINGS.SPECULARCOLORS in footPrint:
                modifier.specularColorData = footPrint.get(PD.DNA_STRINGS.SPECULARCOLORS)
            colorVariation = footPrint.get(PD.DNA_STRINGS.COLORVARIATION, '')
            if colorVariation and not (colorVariation == 'default' and colorizeDataSet):
                modifier.SetColorVariation(footPrint[PD.DNA_STRINGS.COLORVARIATION])
            doDecal(modifier)
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
            PD.BeFrameNice()

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
        PD.BeFrameNice()
        modifier = None
        removedModifiers = self.buildDataManager.GetDirtyModifiers(removedBit=True)
        for removedModifier in iter(removedModifiers):
            if removedModifier.respath == res:
                removedModifier.weight = weight
                removedModifier.dependantModifiers = {}
                modifier = removedModifier
                break

        modifier = modifier or factory.CollectBuildData(self.gender, res, weight)
        categorie = modifier.categorie
        l1rModifier = None
        if modifier.metaData.lod1Replacement:
            modifier.lodCutoff = PD.LOD_0
            l1rModifier = self._AddResource(modifier.metaData.lod1Replacement, 1.0, factory, privilegedCaller=privilegedCaller)
            l1rModifier.lodCutoff = PD.LOD_99
            l1rModifier.lodCutin = PD.LOD_1
            self.buildDataManager.HideModifier(l1rModifier)
        if modifier.metaData.lod2Replacement:
            if l1rModifier:
                l1rModifier.lodCutoff = PD.LOD_1
            else:
                modifier.lodCutoff = PD.LOD_1
            l2rModifier = self._AddResource(modifier.metaData.lod2Replacement, 1.0, factory, privilegedCaller=privilegedCaller)
            l2rModifier.lodCutoff = PD.LOD_99
            l2rModifier.lodCutin = PD.LOD_2
            self.buildDataManager.HideModifier(l2rModifier)
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
            item = factory.GetItemType(itemType, gender=self.gender)
        if item is None:
            log.LogError('Unable to Set Item type:', itemType, 'on doll')
            return 
        self.RemoveResource(item[0], factory)
        return self.AddItemType(factory, item, weight, rawColorVariation)



    def AddItemType(self, factory, itemType, weight = 1.0, rawColorVariation = None):
        if type(itemType) is not tuple:
            itemType = factory.GetItemType(itemType, gender=self.gender)
        if type(itemType) is tuple:
            return self.AddResource(itemType[0], weight, factory, variation=itemType[1], colorVariation=itemType[2], rawColorVariation=rawColorVariation)



    def ApplyVariationsToModifier(self, modifier, colorization = None, variation = None, colorVariation = None, rawColorVariation = None):
        if colorization is not None:
            modifier.SetColorizeData(colorization)
        if variation is not None:
            modifier.SetVariation(variation)
        if colorVariation is not None:
            modifier.SetColorVariation(colorVariation)
        if rawColorVariation is not None:
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



    def SpawnUpdateChildTasklet(self, fun, *args):
        t = uthread.new(fun, *args)
        t.context = 'paperDoll::Doll::Update'
        uthread.schedule(t)
        self._UpdateTaskletChildren.append(t)



    def ReapUpdateChildTasklets(self):
        try:
            try:
                for t in self._UpdateTaskletChildren:
                    if t:
                        t.kill()

            except KillUpdateException:
                sys.exc_clear()

        finally:
            del self._UpdateTaskletChildren[:]




    def _DelayedUpdateCall(self, factory, avatar, visualModel, LODMode):
        self.hasDelayedUpdateCallPending = True
        PD.Yield()
        while self._currentUpdateTasklet and self._currentUpdateTasklet.alive:
            PD.Yield()

        self.hasDelayedUpdateCallPending = False
        self.Update(factory, avatar, visualModel, LODMode)



    def Update(self, factory, avatar = None, visualModel = None, LODMode = False):
        currentFrame = trinity.GetCurrentFrameCounter()
        PD.statistics.updateCount.Inc()
        if self.hasDelayedUpdateCallPending:
            return 
        if self._Doll__updateFrameStamp == currentFrame:
            log.LogWarn('paperDoll::Doll::Update is being called more than once on the same frame for the same doll instance! Fix your code so you only call Update after all needed changes have been applied.')
            return 
        if self._currentUpdateTasklet and self._currentUpdateTasklet.alive and self._Doll__updateFrameStamp < currentFrame:
            self.KillUpdate()
            if not self.hasDelayedUpdateCallPending:
                uthread.new(self._DelayedUpdateCall, factory, avatar, visualModel, LODMode)
            return 
        self._Doll__updateFrameStamp = currentFrame
        self._currentUpdateTasklet = uthread.new(self.Update_t, *(factory, avatar, visualModel))
        self._currentUpdateTasklet.context = 'paperDoll::Doll::Update'
        if blue.os.GetWallclockTimeNow() - blue.os.GetWallclockTime() < 50000:
            uthread.schedule(self._currentUpdateTasklet)



    def KillUpdate(self):
        if self._currentUpdateTasklet and self._currentUpdateTasklet.alive:
            self._currentUpdateTasklet.raise_exception(KillUpdateException, 'Preemptively killing Update')



    def IsBusyUpdating(self):
        return self._currentUpdateTasklet and self._currentUpdateTasklet.alive



    def Update_t(self, factory, avatar, visualModel):
        try:
            try:
                sTime = blue.os.GetTime()
                buildDataManager = self.buildDataManager
                while self.busyLoadingDNA or not factory.IsLoaded:
                    PD.Yield()

                LODMode = self.previousLOD != self.currentLOD
                buildDataManager.Lock()
                updateRuleBundle = UpdateRuleBundle()
                if LODMode:
                    PD.Yield()
                else:
                    PD.BeFrameNice()
                if avatar and hasattr(avatar, 'visualModel') and not visualModel:
                    visualModel = avatar.visualModel
                AddMarker('Update Start')
                self.renderDriver.OnBeginUpdate(self)
                if PD.PerformanceOptions.EnsureCompleteBody:
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
                if not dirtyModifiers and self.mapBundle.AllMapsGood():
                    raise RedundantUpdateException('Warning - Call made to PaperDoll.Update() when no modifier is dirty!')
                PD.BeFrameNice()
                self._AnalyzeBuildDataForRules(updateRuleBundle, buildDataManager)
                updateRuleBundle.DiscoverState(dirtyModifiers, avatar)
                if not (updateRuleBundle.blendShapesOnly or updateRuleBundle.decalsOnly):
                    self._ProcessRules(factory, buildDataManager, addedAndChangedModifiers, updateRuleBundle, factory.clothSimulationActive)
                    self.ApplyBoneOffsets()
                updateRuleBundle.meshesChanged = not self.hasUpdatedOnce or any((modifier for modifier in addedAndChangedModifiers if modifier.IsMeshContainingModifier() if modifier.IsMeshDirty() or modifier.HasWeightPulse())) or any((modifier.IsMeshContainingModifier() for modifier in removedModifiers))
                if not updateRuleBundle.blendShapesOnly and updateRuleBundle.meshesChanged and avatar:
                    factory.CreateAnimationOffsets(avatar, self)
                if self.modifierLimits:
                    for modifier in iter(addedAndChangedModifiers):
                        limit = self.modifierLimits.get(modifier.name)
                        if limit:
                            if modifier.weight > limit[1]:
                                modifier.weight = limit[1]
                            elif modifier.weight < limit[0]:
                                modifier.weight = limit[0]

                if updateRuleBundle.doDecals:
                    self.BakeDecals_t(factory, updateRuleBundle.dirtyDecalModifiers)
                if updateRuleBundle.doBlendShapes and not updateRuleBundle.meshesChanged:
                    self._HandleBlendShapes(removedModifiers, avatar)
                if factory.clothSimulationActive and avatar and updateRuleBundle.meshesChanged:
                    self.LoadClothData(addedAndChangedModifiers)
                if self.currentLOD <= PD.LOD_SKIN:
                    hashStubble = PD.PortraitTools.GetStubbleHash(addedAndChangedModifiers)
                else:
                    hashStubble = None
                if updateRuleBundle.meshesChanged:
                    self._Doll__ApplyUVs()
                if visualModel and (self.currentLOD <= self.previousLOD or not self.mapBundle.AllMapsGood()):
                    textureCompositingStartTime = blue.os.GetTime()
                    if self.hasUpdatedOnce and self.mapBundle.AllMapsGood():
                        updateRuleBundle.partsToComposite = buildDataManager.GetPartsFromMaps(dirtyModifiers)
                    self.WaitForChildTaskletsToFinish()
                    while self.mapBundle.busyDownScaling:
                        PD.Yield()

                    if self.hasUpdatedOnce and self.mapBundle.AllMapsGood():
                        updateRuleBundle.mapsToComposite = buildDataManager.GetMapsToComposite(dirtyModifiers)
                    if buildDataManager.desiredOrderChanged:
                        if (self.mapBundle.AllMapsGood() or updateRuleBundle.partsToComposite) and PD.DOLL_PARTS.BODY not in updateRuleBundle.partsToComposite:
                            updateRuleBundle.partsToComposite.append(PD.DOLL_PARTS.BODY)
                        updateRuleBundle.mapsToComposite = list(PD.MAPS)
                    blendShapeVector = [ modifier.weight for modifier in buildDataManager.GetModifiersAsList() if modifier.IsBlendshapeModifier() if modifier.weight != 0.0 ]
                    hES = (self.compressionSettings, hashStubble, blendShapeVector)
                    hashKey = buildDataManager.HashForMaps(hashableElements=hES)
                    mapsTypesComposited = self.CompositeTextures(factory, hashKey, updateRuleBundle)
                    if updateRuleBundle.videoMemoryFailure:
                        raise OutOfVideoMemoryException('Out of video memory!')
                    if not updateRuleBundle.blendShapesOnly:
                        self.WaitForTexturesToComposite(factory, hashKey, mapsTypesComposited, textureCompositingStartTime)
                    else:
                        timeCompositedSec = PD.statistics.GetTimeDiffInSeconds(textureCompositingStartTime)
                        PD.statistics.compositeTime.Add(timeCompositedSec)
                compSet = self.compressionSettings if self.compressionSettings is not None else factory
                self.useDXT5N = compSet and compSet.compressTextures and compSet.AllowCompress(PD.NORMAL_MAP)
                meshes = buildDataManager.GetMeshes(includeClothMeshes=factory.clothSimulationActive)
                if updateRuleBundle.meshesChanged:
                    self._HandleBlendShapes(removedModifiers, avatar)
                self.WaitForChildTaskletsToFinish()
                if updateRuleBundle.meshesChanged:
                    self.ConfigureMaskedShader(updateRuleBundle)
                    self.renderDriver.ApplyShaders(self, meshes)
                    if visualModel:
                        factory.RemoveMeshesFromVisualModel(visualModel)
                    if visualModel:
                        factory.AppendMeshesToVisualModel(visualModel, meshes)
                        visualModel.ResetAnimationBindings()
                    if avatar and avatar.clothMeshes is not None:
                        if len(avatar.clothMeshes) > 0:
                            del avatar.clothMeshes[:]
                        if factory.clothSimulationActive:
                            for mesh in iter(meshes):
                                if type(mesh) is trinity.Tr2ClothingActor:
                                    avatar.clothMeshes.append(mesh)

                Factory.BindMapsToMeshes(meshes, self.mapBundle, self.usePrepass)
                if avatar and self.usePrepass:
                    avatar.BindLowLevelShaders()
                if self.currentLOD <= PD.LOD_SKIN and updateRuleBundle.doStubble:

                    def doStubble():
                        PD.PortraitTools.HandleRemovedStubble(removedModifiers, buildDataManager)
                        PD.PortraitTools.HandleUpdatedStubble(addedAndChangedModifiers, buildDataManager)
                        factory.RebindAnimations(avatar, visualModel)


                    self.SpawnUpdateChildTasklet(doStubble)
                self.renderDriver.OnFinalizeAvatar(visualModel, avatar, updateRuleBundle, self, factory)
                self.previousLOD = self.currentLOD
                self.WaitForChildTaskletsToFinish()
                self.renderDriver.OnEndUpdate(avatar, visualModel, self, factory)
                factory.RebindAnimations(avatar, visualModel)
                if avatar:
                    freq = PD.PerformanceOptions.updateFreq.get(self.overrideLod, 0)
                    if freq == 0:
                        avatar.updatePeriod = 0
                    else:
                        avatar.updatePeriod = 1.0 / freq
                if self.currentLOD == PD.LOD_SCATTER_SKIN and self.skinLightmapRenderer is None:
                    self.skinLightmapRenderer = PD.SkinLightmapRenderer(useOptix=self.currentLOD == PD.LOD_RAYTRACE)
                    self.skinLightmapRenderer.SetSkinnedObject(avatar)
                    self.skinLightmapRenderer.StartRendering()
                if self.skinLightmapRenderer is not None and visualModel and avatar and not LODMode:
                    self.skinLightmapRenderer.SetSkinnedObject(avatar)
                buildDataManager.NotifyUpdate()
                self.lastUpdateRedundant = False
                self.hasUpdatedOnce = True
            except RedundantUpdateException as err:
                self.lastUpdateRedundant = True
                sys.exc_clear()
            except KillUpdateException as err:
                self.lastUpdateRedundant = True
                sys.exc_clear()
            except OutOfVideoMemoryException as err:
                self.lastUpdateRedundant = True
                log.LogException(str(err))
                newSize = map(lambda x: x / 2, self.mapBundle.baseResolution)
                shadow = PD.SkinSpotLightShadows.instance
                if shadow and shadow.GetShadowMapResolution() > newSize[0]:
                    shadow.SetShadowMapResolution(shadow.GetShadowMapResolution() / 2)
                self.hasUpdatedOnce = False
                self.SetTextureSize(newSize)
            except Exception as err:
                log.LogException(str(err))
                sys.exc_clear()

        finally:
            self.ReapUpdateChildTasklets()
            self.buildDataManager.UnLock()
            timeUpdatingSec = PD.statistics.GetTimeDiffInSeconds(sTime)
            PD.statistics.updateTime.Add(timeUpdatingSec)
            if not updateRuleBundle.videoMemoryFailure:
                uthread.new(self.NotifyUpdateDoneListeners_t)
            self._currentUpdateTasklet = None
            if updateRuleBundle.videoMemoryFailure:
                uthread.new(self.Update, factory, avatar, visualModel)
            AddMarker('End Start')




    def NotifyUpdateDoneListeners_t(self):
        for listener in self.onUpdateDoneListeners:
            uthread.new(listener)




    def AddUpdateDoneListener(self, callBack):
        if callBack not in self.onUpdateDoneListeners:
            self.onUpdateDoneListeners.append(callBack)



    def WaitForChildTaskletsToFinish(self):
        try:
            PD.WaitForAll(self._UpdateTaskletChildren, lambda x: x.alive)
        except KillUpdateException:
            raise 



    def WaitForTexturesToComposite(self, factory, hashKey, mapsTypesComposited, textureCompositingStartTime):
        self.WaitForChildTaskletsToFinish()
        PD.statistics.mapsComposited.Add(len(mapsTypesComposited))
        if factory.allowTextureCache and mapsTypesComposited:
            mapsToSave = [ self.mapBundle[mapType] for mapType in mapsTypesComposited if self.mapBundle[mapType].isGood ]
            uthread.new(factory.SaveMaps, hashKey, mapsToSave)
        timeCompositedSec = PD.statistics.GetTimeDiffInSeconds(textureCompositingStartTime)
        PD.statistics.compositeTime.Add(timeCompositedSec)



    def ConfigureMaskedShader(self, updateRuleBundle):
        if self.useMaskedShaders or updateRuleBundle.undoMaskedShaders:
            applicableModifiers = (modifier for modifier in self.buildDataManager.GetModifiersAsList() if modifier.categorie in PD.MASKING_CATEGORIES)
            for modifier in applicableModifiers:
                for mesh in iter(modifier.meshes):
                    self.ConfigureMeshForMaskedShader(mesh, remove=updateRuleBundle.undoMaskedShaders)





    def ConfigureMeshForMaskedShader(self, mesh, remove = False):
        decalToOpaque = []
        fx = PD.GetEffectsFromAreaList(mesh.opaqueAreas)
        for f in iter(fx):
            for p in f.parameters:
                if p.name == 'CutMaskInfluence':
                    p.value = 0.85


        for decalArea in mesh.decalAreas:
            f = decalArea.effect
            if f is None:
                continue
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
        for transparentArea in mesh.transparentAreas:
            f = transparentArea.effect
            if f is None:
                continue
            for p in f.parameters:
                if p.name == 'CutMaskInfluence':
                    p.value = 1.0





    def BakeDecals_t(self, factory, decalModifiers):
        if decalModifiers:
            createTargetAvatar = False
            if self.decalBaker is None:
                createTargetAvatar = True
                self.decalBaker = PD.DecalBaker(factory)
            elif not self.decalBaker.HasAvatar():
                createTargetAvatar = True
            self.decalBaker.Initialize()
            if createTargetAvatar:
                self.decalBaker.CreateTargetAvatarFromDoll(self)
                self._UpdateTaskletChildren.append(self.decalBaker.avatarShaderSettingTasklet)
            self.decalBaker.SetSize(self.textureResolution)
            for decalModifier in decalModifiers:
                try:
                    try:
                        try:
                            self.decalBaker.BakeDecalToModifier(decalModifier.decalData, decalModifier)
                        except TypeError:
                            return 

                    finally:
                        self._UpdateTaskletChildren.append(self.decalBaker.decalSettingTasklet)
                        self._UpdateTaskletChildren.append(self.decalBaker.bakingTasklet)

                    while not self.decalBaker.isReady:
                        PD.Yield()

                    decalModifier.mapL.update(decalModifier.mapD)
                    decalModifier.colorize = True
                except KillUpdateException:
                    decalModifier.IsDirty = True
                    raise 




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
                tex = factory.FindCachedTexture(hashKey, self.mapBundle.GetResolutionByMapType(i)[0], PD.MAPS[i])
                if tex:
                    tex.Reload()
                textureCache[i] = tex

            PD.WaitForAll(textureCache.values(), lambda x: x is not None and x.isLoading)
            for i in xrange(mapCount):
                if textureCache.get(i) and textureCache[i].isGood:
                    self.mapBundle.SetMapByTypeIndex(i, textureCache[i], hashKey)

        if self.compressionSettings is not None:
            self.compressionSettings.generateMipmap = False
        mapsTypesComposited = []
        textureCompositor = tc.TextureCompositor(resData=factory.resData)
        for mapTypeIndex in updateRuleBundle.mapsToComposite:
            existingMap = self.mapBundle[mapTypeIndex]
            if existingMap and existingMap.isGood and hashKey == self.mapBundle.hashKeys.get(mapTypeIndex):
                continue
            else:
                mapsTypesComposited.append(mapTypeIndex)


        def CompositeTasklet_t():
            copyToExistingTexture = len(mapsTypesComposited) == 1 and not updateRuleBundle.meshesChanged
            for mapTypeIndex in mapsTypesComposited:
                PD.BeFrameNice()
                texture = None
                try:
                    texture = factory.CompositeCombinedTexture(mapTypeIndex, self.gender, self.buildDataManager, self.mapBundle, textureCompositor, self.compressionSettings, partsToComposite=updateRuleBundle.partsToComposite, copyToExistingTexture=copyToExistingTexture, lod=self.currentLOD)
                except (trinity.E_OUTOFMEMORY, trinity.D3DERR_OUTOFVIDEOMEMORY):
                    updateRuleBundle.videoMemoryFailure = True
                    sys.exc_clear()
                    break
                if texture:
                    self.mapBundle.SetMapByTypeIndex(mapTypeIndex, texture, hashKey)



        self.SpawnUpdateChildTasklet(CompositeTasklet_t)
        return mapsTypesComposited



    def LoadBindPose(self):
        filename = 'res:/Graphics/Character/Global/FaceSetup/BaseFemaleBindPose.yaml'
        if self.gender == PD.GENDER.MALE:
            filename = 'res:/Graphics/Character/Global/FaceSetup/BaseMaleBindPose.yaml'
        self.bindPose = PD.LoadYamlFileNicely(filename)



    def LoadClothData(self, modifierList):
        clothMeshes = []
        clothModifierGenerator = (modifier for modifier in modifierList if modifier.clothPath if not modifier.clothData)
        for modifier in clothModifierGenerator:
            clothLoadPath = modifier.clothPath
            if not clothLoadPath:
                modifier.clothData = None
                continue
            if clothLoadPath:
                clothData = blue.os.LoadObject(clothLoadPath)
                if clothData and type(clothData) == trinity.Tr2ClothingActor:
                    clothData.name = modifier.name
                    clothMeshes.append(clothData)
                else:
                    clothData = None
                modifier.clothData = clothData

        PD.WaitForAll(clothMeshes, lambda x: x.clothingRes.isLoading)
        return clothMeshes



    def SuspendCloth(self, avatar = None, factory = None):
        for m in self.buildDataManager.GetModifiersAsList():
            if m.categorie != PD.DOLL_PARTS.HAIR and m.clothData:
                meshPath = m.clothPath.lower().replace('_physx.red', '.red')
                bsMesh = m.clothData.resPath.lower().replace('.apb', '_bs.gr2')
                cacheKey = meshPath + m.currentColorVariation
                if cacheKey not in self.tempClothCache:
                    item = blue.os.LoadObject(meshPath)
                    if hasattr(item, 'meshes') and len(item.meshes):
                        while item.meshes[0].isLoading:
                            PD.Yield()

                        dl = []
                        for mesh in item.meshes:
                            mesh.geometryResPath = bsMesh

                        for delMesh in dl:
                            item.meshes.remove(delMesh)

                        Factory.BindMapsToMeshes(item.meshes, self.mapBundle)
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
        morphTargets = self.buildDataManager.GetMorphTargets()
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
                PD.Yield()

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
            self.mapBundle.ReCreate(includeFixedSizeMaps=False)
        for modifier in self.buildDataManager.GetModifiersAsList():
            if modifier.IsTextureContainingModifier() and not modifier.IsDirty:
                modifier.IsDirty = True




    def getbusyUpdating(self):
        return self._currentUpdateTasklet is not None or any(map(lambda x: x.alive, self._UpdateTaskletChildren))


    busyUpdating = property(fget=lambda self: self.getbusyUpdating())

    def setoverrideLod(self, newLod, affectTextureSize = True):
        oldLod = self.currentLOD
        self.currentLOD = newLod
        self.previousLOD = oldLod
        self.buildDataManager.SetLOD(newLod)
        if oldLod == PD.LOD_SKIN and newLod == PD.LOD_SCATTER_SKIN:
            self.buildDataManager.SetAllAsDirty()
            return 
        if oldLod == PD.LOD_SCATTER_SKIN and newLod >= PD.LOD_SKIN:
            self.skinLightmapRenderer = None
            if newLod == PD.LOD_SKIN:
                return 
        if self.gender == PD.GENDER.MALE:
            for bm in self.buildDataManager.GetModifiersByCategory(PD.HAIR_CATEGORIES.BEARD):
                bm.IsDirty = True

        for modifier in self.buildDataManager.GetModifiersAsList():
            if modifier.IsMeshContainingModifier():
                modifier.IsDirty = True
                del modifier.meshes[:]
                modifier.meshGeometryResPaths = {}

        if affectTextureSize and newLod >= 0 and newLod < len(PD.PerformanceOptions.lodTextureSizes):
            self.SetTextureSize(*PD.PerformanceOptions.lodTextureSizes[newLod])


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


