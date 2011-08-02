import trinity
import blue
import bluepy
import weakref
import paperDoll as PD
import itertools
import log

def LogError(*args):
    log.Log(' '.join(map(strx, args)), log.LGERR)



class SkinLightmapRenderer:
    __guid__ = 'paperDoll.SkinLightmapRenderer'
    renderJob = None
    scene2 = None
    instances = set({})

    @staticmethod
    def Scene():
        if SkinLightmapRenderer.scene2 is None or SkinLightmapRenderer.scene2.object is None:
            jobs = trinity.device.scheduledRecurring
            for job in jobs:
                if 'paperdoll' in job.name.lower():
                    return job.steps[0].object

            return 
        return SkinLightmapRenderer.scene2.object


    LIGHTMAP_RENDERER_EFFECT = 'res:/Graphics/Effect/Managed/Interior/Avatar/SkinnedAvatarBRDFLightmapUnwrap_Single.fx'
    LIGHTMAP_RENDERER_DOUBLE_EFFECT = 'res:/Graphics/Effect/Managed/Interior/Avatar/SkinnedAvatarBRDFLightmapUnwrap_Double.fx'
    STRETCHMAP_RENDERER_EFFECT = 'res:/Graphics/Effect/Managed/Interior/Avatar/SkinnedAvatarBRDFStretchmap.fx'
    LIGHTMAP_SCATTER_EFFECT = 'res:/Graphics/Effect/Managed/Interior/Avatar/LightmapScatter.fx'
    LIGHTMAP_EXPAND_EFFECT = 'res:/Graphics/Effect/Utility/Compositing/ExpandOpaqueNoMask.fx'
    BECKMANN_LOOKUP_EFFECT = 'res:/Graphics/Effect/Managed/Interior/Avatar/SkinnedAvatarBRDFBeckmannLookup.fx'
    LIGHTMAP_APPLICATION_EFFECT = 'res:/Graphics/Effect/Managed/Interior/Avatar/SkinnedAvatarBRDFLightmapApplication_Single.fx'
    LIGHTMAP_APPLICATION_DOUBLE_EFFECT = 'res:/Graphics/Effect/Managed/Interior/Avatar/SkinnedAvatarBRDFLightmapApplication_Double.fx'
    LIGHTMAP_APPLICATION_OPTIX_EFFECT = 'res:/Graphics/Effect/Managed/Interior/Avatar/SkinnedAvatarBRDFLightmapApplication_Single_Optix.fx'
    LIGHTMAP_APPLICATION_DOUBLE_OPTIX_EFFECT = 'res:/Graphics/Effect/Managed/Interior/Avatar/SkinnedAvatarBRDFLightmapApplication_Double_Optix.fx'
    OPTIX_POSWORLD_UV_EFFECT = 'res:/Graphics/Effect/Managed/Interior/Avatar/PortraitOptiXPosWorldUVSpace.fx'
    OPTIX_NORMALWORLD_UV_EFFECT = 'res:/Graphics/Effect/Managed/Interior/Avatar/PortraitOptiXNormalWorldUVSpace.fx'
    OPTIX_POSWORLD_EFFECT = 'res:/Graphics/Effect/Managed/Interior/Avatar/PortraitOptiXPosWorld.fx'
    OPTIX_NORMALWORLD_EFFECT = 'res:/Graphics/Effect/Managed/Interior/Avatar/PortraitOptiXNormalWorld.fx'

    class Mesh:

        def __init__(self):
            self.origEffect = {}
            self.stretchmapRenderEffect = {}
            self.lightmapRenderEffect = {}
            self.lightmapApplyEffect = {}
            self.oxPosWorldUVEffect = {}
            self.oxNormalWorldUVEffect = {}
            self.oxPosWorldEffect = {}
            self.oxNormalWorldEffect = {}
            self.liveParameters = []



        def ExtractOrigEffect(self, mesh):
            for area in itertools.chain(mesh.opaqueAreas, mesh.decalAreas):
                PD.AddWeakBlue(self, 'origEffect', area, area.effect)

            return len(self.origEffect) > 0



        def CreateOptixEffects(self, includeStretchMap = False):
            for (areaRef, fx,) in self.origEffect.iteritems():
                if areaRef.object is None:
                    continue
                oxPosWorldUVEffect = SkinLightmapRenderer.DuplicateEffect(fx, SkinLightmapRenderer.OPTIX_POSWORLD_UV_EFFECT)
                oxNormalWorldUVEffect = SkinLightmapRenderer.DuplicateEffect(fx, SkinLightmapRenderer.OPTIX_NORMALWORLD_UV_EFFECT)
                oxPosWorldEffect = SkinLightmapRenderer.DuplicateEffect(fx, SkinLightmapRenderer.OPTIX_POSWORLD_EFFECT)
                oxNormalWorldEffect = SkinLightmapRenderer.DuplicateEffect(fx, SkinLightmapRenderer.OPTIX_NORMALWORLD_EFFECT)
                PD.AddWeakBlue(self, 'oxPosWorldUVEffect', areaRef.object, oxPosWorldUVEffect)
                PD.AddWeakBlue(self, 'oxNormalWorldUVEffect', areaRef.object, oxNormalWorldUVEffect)
                PD.AddWeakBlue(self, 'oxPosWorldEffect', areaRef.object, oxPosWorldEffect)
                PD.AddWeakBlue(self, 'oxNormalWorldEffect', areaRef.object, oxNormalWorldEffect)
                if includeStretchMap:
                    stretchmapRenderEffect = trinity.Tr2Effect()
                    stretchmapRenderEffect.effectFilePath = SkinLightmapRenderer.STRETCHMAP_RENDERER_EFFECT
                    stretchmapRenderEffect.parameters = fx.parameters
                    stretchmapRenderEffect.PopulateParameters()
                    stretchmapRenderEffect.RebuildCachedData()
                    PD.AddWeakBlue(self, 'stretchmapRenderEffect', areaRef.object, stretchmapRenderEffect)





    @staticmethod
    def CreateRenderTarget(width, height, format, useRT = False):
        if useRT:
            return trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, width, height, format, trinity.TRIMULTISAMPLE_NONE, 0, True)
        else:
            return trinity.device.CreateTexture(width, height, 1, trinity.TRIUSAGE_RENDERTARGET, format, trinity.TRIPOOL_DEFAULT)



    @bluepy.CCP_STATS_ZONE_METHOD
    def CreateRenderTargets(self, lightmapFormat):
        try:
            self.lightmap = self.CreateRenderTarget(self.lightmapSize[0], self.lightmapSize[1], lightmapFormat)
            self.stretchmap = self.CreateRenderTarget(min(1024, self.lightmapSize[0]), min(1024, self.lightmapSize[1]), lightmapFormat)
            self.scatteredLightmap = self.CreateRenderTarget(self.lightmapSize[0], self.lightmapSize[1], lightmapFormat)
            self.depth = trinity.TriSurfaceManaged(trinity.device.CreateDepthStencilSurface, self.lightmapSize[0], self.lightmapSize[1], trinity.TRIFMT_D24S8, trinity.TRIMULTISAMPLE_NONE, 0, 1)
        except Exception:
            self.lightmap = None
            self.stretchmap = None
            self.scatteredLightmap = None
            return False
        return True



    @bluepy.CCP_STATS_ZONE_METHOD
    def AddTex2D(self, effect, name, resourcePath = None):
        param = trinity.TriTexture2DParameter()
        param.name = name
        if resourcePath is not None:
            param.resourcePath = resourcePath
        effect.resources.append(param)
        return param



    def Print(self, msg):
        print '[Skin]',
        print msg



    def DebugPrint(self, msg):
        pass



    @bluepy.CCP_STATS_ZONE_METHOD
    def __init__(self, highQuality = True, useHDR = True, useOptix = False):
        self.useOptix = useOptix
        if True:
            raytraceWidth = 2048
            raytraceHeight = 2048
        else:
            raytraceWidth = 512
            raytraceHeight = 512
        self.raytracing = None
        self.refreshMeshes = False
        self.skinMapPath = None
        self.precomputeBeckmann = False
        self.useExpandOpaque = False
        self.lightmapEffectPreload = self.PreloadEffect(self.LIGHTMAP_RENDERER_EFFECT)
        self.lightmapDoubleEffectPreload = self.PreloadEffect(self.LIGHTMAP_RENDERER_DOUBLE_EFFECT)
        self.stretchmapEffectPreload = self.PreloadEffect(self.STRETCHMAP_RENDERER_EFFECT)
        self.lightmapApplicationEffectPreload = self.PreloadEffect(self.LIGHTMAP_APPLICATION_EFFECT)
        self.lightmapApplicationDoubleEffectPreload = self.PreloadEffect(self.LIGHTMAP_APPLICATION_DOUBLE_EFFECT)
        self.lightmapApplicationOptixEffectPreload = self.PreloadEffect(self.LIGHTMAP_APPLICATION_OPTIX_EFFECT)
        self.lightmapApplicationDoubleOptixEffectPreload = self.PreloadEffect(self.LIGHTMAP_APPLICATION_DOUBLE_OPTIX_EFFECT)
        self.lightmapScatterEffect = self.PreloadEffect(self.LIGHTMAP_SCATTER_EFFECT)
        self.lightmapExpandEffect = self.PreloadEffect(self.LIGHTMAP_EXPAND_EFFECT)
        if self.precomputeBeckmann:
            self.beckmannLookupEffect = self.PreloadEffect(self.BECKMANN_LOOKUP_EFFECT)
        self.shareOptixBuffers = False
        self.skinnedObject = None
        if self.useOptix:
            self.oxWidth = raytraceWidth
            self.oxHeight = raytraceHeight
            self.bbWidth = trinity.device.GetBackBuffer().width
            self.bbHeight = trinity.device.GetBackBuffer().height
            self.maxWidth = self.oxWidth if self.oxWidth > self.bbWidth else self.bbWidth
            self.maxHeight = self.oxHeight if self.oxHeight > self.bbHeight else self.bbHeight
            if self.shareOptixBuffers:
                self.oxWorldPosShared = self.CreateRenderTarget(self.maxWidth, self.maxHeight, trinity.TRIFMT_A32B32G32R32F, useRT=True)
                self.oxWorldNormalShared = self.CreateRenderTarget(self.maxWidth, self.maxHeight, trinity.TRIFMT_A32B32G32R32F, useRT=True)
            else:
                self.oxWorldPosMapUV = self.CreateRenderTarget(self.oxWidth, self.oxHeight, trinity.TRIFMT_A32B32G32R32F, useRT=True)
                self.oxWorldNormalMapUV = self.CreateRenderTarget(self.oxWidth, self.oxHeight, trinity.TRIFMT_A32B32G32R32F, useRT=True)
                self.oxWorldPosMap = self.CreateRenderTarget(self.bbWidth, self.bbHeight, trinity.TRIFMT_A32B32G32R32F, useRT=True)
                self.oxWorldNormalMap = self.CreateRenderTarget(self.bbWidth, self.bbHeight, trinity.TRIFMT_A32B32G32R32F, useRT=True)
            self.oxDiffuseLight = self.CreateRenderTarget(self.oxWidth, self.oxHeight, trinity.TRIFMT_A8R8G8B8, useRT=True)
            self.oxDiffuseTexture = trinity.device.CreateTexture(self.oxWidth, self.oxHeight, 1, 0, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_MANAGED)
            self.oxSpecularLight = self.CreateRenderTarget(self.bbWidth, self.bbHeight, trinity.TRIFMT_A8R8G8B8, useRT=True)
            self.oxSpecularTexture = trinity.device.CreateTexture(self.bbWidth, self.bbHeight, 1, 0, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_MANAGED)
        self.paramLightmap = self.AddTex2D(self.lightmapScatterEffect, 'Lightmap')
        self.paramStretchmap = self.AddTex2D(self.lightmapScatterEffect, 'Stretchmap')
        self.paramNoisemap = self.AddTex2D(self.lightmapScatterEffect, 'Noisemap', 'res:/Texture/Global/noise.png')
        self.paramSkinMap = self.AddTex2D(self.lightmapScatterEffect, 'SkinMap')
        self.paramExpandSource = self.AddTex2D(self.lightmapExpandEffect, 'Texture')
        self.paramDiffuseScattermap = self.AddTex2D(self.lightmapApplicationEffectPreload, 'DiffuseScatterMap')
        self.paramDiffusemap = self.AddTex2D(self.lightmapApplicationEffectPreload, 'DiffuseMap')
        if self.precomputeBeckmann:
            self.paramBeckmannLookup = self.AddTex2D(self.lightmapApplicationEffectPreload, 'BeckmannLookup')
        if highQuality:
            self.lightmapSize = (2048, 2048)
        else:
            self.lightmapSize = (512, 512)
        lightmapFormat = []
        if useHDR and not self.useOptix:
            lightmapFormat = [trinity.TRIFMT_A16B16G16R16F]
        lightmapFormat.append(trinity.TRIFMT_X8R8G8B8)
        lightmapFormat.append(trinity.TRIFMT_A8R8G8B8)
        lightmapFormat.append(trinity.TRIFMT_A8B8G8R8)
        self.lightmapRenderJob = None
        setupOK = False
        for format in lightmapFormat:
            if self.CreateRenderTargets(format):
                setupOK = True
                break

        if not setupOK:
            self.lightmapSize = (self.lightmapSize[0] / 2, self.lightmapSize[1] / 2)
            for format in lightmapFormat:
                if self.CreateRenderTargets(format):
                    setupOK = True
                    break

            if setupOK:
                self.Print('Warning: needed to downsize the lightmap resolution')
            else:
                self.Print("Error: couldn't find any lightmap render format that works :(")
                return 
        if self.precomputeBeckmann:
            try:
                self.beckmannLookup = self.CreateRenderTarget(256, 256, trinity.TRIFMT_L8)
                self.RenderBeckmannLookup()
            except Exception:
                self.Print("[Skin] Error: can't create specular lookup table texture")
                return 
        self.meshes = {}
        self.oxMeshes = {}
        SkinLightmapRenderer.instances.add(weakref.ref(self))



    @bluepy.CCP_STATS_ZONE_METHOD
    def __del__(self):
        newSet = set({})
        for instance in SkinLightmapRenderer.instances:
            if instance():
                newSet.add(instance)

        SkinLightmapRenderer.instances = newSet
        self.StopRendering()
        self.RestoreShaders()
        if self.useOptix:
            if self.shareOptixBuffers:
                del self.oxWorldPosShared
                del self.oxWorldNormalShared
            else:
                del self.oxWorldPosMapUV
                del self.oxWorldNormalMapUV
                del self.oxWorldPosMap
                del self.oxWorldNormalMap
                del self.oxDiffuseLight
                del self.oxDiffuseTexture
                del self.oxSpecularLight
                del self.oxSpecularTexture
            del self.raytracing



    @staticmethod
    def PreloadEffect(path):
        effect = trinity.Tr2Effect()
        effect.effectFilePath = path
        while effect.effectResource.isLoading:
            blue.synchro.Yield()

        effect.RebuildCachedData()
        return effect



    @bluepy.CCP_STATS_ZONE_METHOD
    def CreateExtraMaps(self, effect):
        res = self.FindResource(effect, 'DiffuseScatterMap')
        if res is None:
            res = self.AddTex2D(effect, 'DiffuseScatterMap')
        res.SetResource(self.lightmap if self.useExpandOpaque else self.scatteredLightmap)
        res = self.FindResource(effect, 'BeckmannLookup')
        if res is None:
            if self.precomputeBeckmann:
                res = self.AddTex2D(effect, 'BeckmannLookup')
            else:
                res = self.AddTex2D(effect, 'BeckmannLookup', 'res:/Texture/Global/beckmannSpecular.dds')
        if self.precomputeBeckmann:
            res.SetResource(self.beckmannLookup)



    @bluepy.CCP_STATS_ZONE_METHOD
    def CreateRaytraceMaps(self, effect):
        if self.useOptix:
            res = self.FindResource(effect, 'RaytraceLightMap')
            if res is None:
                res = self.AddTex2D(effect, 'RaytraceLightMap')
            res.SetResource(self.oxDiffuseTexture)
            res = self.FindResource(effect, 'RaytraceSpecularMap')
            if res is None:
                res = self.AddTex2D(effect, 'RaytraceSpecularMap')
            res.SetResource(self.oxSpecularTexture)
            raytraceSpecularScale = trinity.Tr2Vector4Parameter()
            raytraceSpecularScale.name = 'raytraceSpecularScale'
            raytraceSpecularScale.value = (self.bbWidth,
             self.bbHeight,
             0,
             0)
            effect.parameters.append(raytraceSpecularScale)



    @staticmethod
    def FindResource(effect, name):
        for r in effect.resources:
            if r.name == name:
                return r




    @staticmethod
    def DuplicateResource(targetEffect, sourceEffect, name):
        p = trinity.TriTexture2DParameter()
        p.name = name
        p.SetResource(SkinLightmapRenderer.FindResource(sourceEffect, name).resource)
        targetEffect.resources.append(p)



    @staticmethod
    def DuplicateEffect(fx, newPath, dupResources = True):
        newEffect = trinity.Tr2Effect()
        newEffect.effectFilePath = newPath
        newEffect.parameters = fx.parameters
        newEffect.name = fx.name
        if dupResources:
            for r in fx.resources:
                SkinLightmapRenderer.DuplicateResource(newEffect, fx, r.name)

        newEffect.PopulateParameters()
        newEffect.RebuildCachedData()
        return newEffect



    @bluepy.CCP_STATS_ZONE_METHOD
    def AddOptixMesh(self, mesh):
        m = self.Mesh()
        PD.AddWeakBlue(self, 'oxMeshes', mesh, m)
        if len(m.origEffect) == 0 and not m.ExtractOrigEffect(mesh):
            return 
        m.CreateOptixEffects()



    @bluepy.CCP_STATS_ZONE_METHOD
    def AddMesh(self, mesh):
        if mesh is None or self.lightmap is None:
            return 

        def SetupSkinMap():
            for a in itertools.chain(mesh.opaqueAreas, mesh.decalAreas):
                if a.effect is not None and a.effect.resources is not None:
                    for e in a.effect.resources:
                        if e.name == 'SkinMap':
                            self.skinMapPath = e.resourcePath
                            self.paramSkinMap.resourcePath = self.skinMapPath
                            return 




        if self.skinMapPath is None:
            SetupSkinMap()
        m = self.Mesh()
        if not m.ExtractOrigEffect(mesh):
            return 
        for (areaRef, fx,) in m.origEffect.iteritems():
            if areaRef.object is None:
                continue
            if PD.IsBeard(areaRef.object):
                PD.AddWeakBlue(m, 'lightmapRenderEffect', areaRef.object, None)
                PD.AddWeakBlue(m, 'lightmapApplyEffect', areaRef.object, fx)
                PD.AddWeakBlue(m, 'stretchmapRenderEffect', areaRef.object, None)
                PD.AddWeakBlue(m, 'oxPosWorldUVEffect', areaRef.object, None)
                PD.AddWeakBlue(m, 'oxNormalWorldUVEffect', areaRef.object, None)
                PD.AddWeakBlue(m, 'oxPosWorldEffect', areaRef.object, None)
                PD.AddWeakBlue(m, 'oxNormalWorldEffect', areaRef.object, None)
                continue
            wasDouble = 'double' in fx.effectFilePath.lower()
            singleApply = self.LIGHTMAP_APPLICATION_EFFECT if not self.useOptix else self.LIGHTMAP_APPLICATION_OPTIX_EFFECT
            doubleApply = self.LIGHTMAP_APPLICATION_DOUBLE_EFFECT if not self.useOptix else self.LIGHTMAP_APPLICATION_DOUBLE_OPTIX_EFFECT
            lightmapRenderEffect = SkinLightmapRenderer.DuplicateEffect(fx, self.LIGHTMAP_RENDERER_DOUBLE_EFFECT if wasDouble else self.LIGHTMAP_RENDERER_EFFECT)
            lightmapApplyEffect = SkinLightmapRenderer.DuplicateEffect(fx, doubleApply if wasDouble else singleApply)
            PD.AddWeakBlue(m, 'lightmapRenderEffect', areaRef.object, lightmapRenderEffect)
            PD.AddWeakBlue(m, 'lightmapApplyEffect', areaRef.object, lightmapApplyEffect)
            stretchmapRenderEffect = trinity.Tr2Effect()
            stretchmapRenderEffect.effectFilePath = self.STRETCHMAP_RENDERER_EFFECT
            stretchmapRenderEffect.parameters = fx.parameters
            PD.AddWeakBlue(m, 'stretchmapRenderEffect', areaRef.object, stretchmapRenderEffect)
            m.liveParameters.append(filter(lambda r: r[0].name.startswith('WrinkleNormalStrength') or r[0].name.startswith('spotLight'), zip(fx.parameters, lightmapRenderEffect.parameters, lightmapApplyEffect.parameters)))
            self.CreateExtraMaps(lightmapApplyEffect)
            self.CreateRaytraceMaps(lightmapRenderEffect)
            self.CreateRaytraceMaps(lightmapApplyEffect)
            stretchmapRenderEffect.PopulateParameters()
            stretchmapRenderEffect.RebuildCachedData()
            if False:
                self.DebugPrint('lightmapRenderEffect resources:')
                for p in lightmapRenderEffect.resources:
                    self.DebugPrint(p.name)

                self.DebugPrint('lightmapApplyEffect resources:')
                for p in lightmapApplyEffect.resources:
                    self.DebugPrint(p.name)


        if self.useOptix:
            self.AddOptixMesh(mesh)
        PD.AddWeakBlue(self, 'meshes', mesh, m)



    @staticmethod
    def DoChangeEffect(attrName, meshes):
        for (meshRef, meshData,) in meshes.iteritems():
            mesh = meshRef.object
            count = 0
            dictionary = getattr(meshData, attrName)
            for (areaRef, effect,) in dictionary.iteritems():
                if areaRef.object is not None:
                    areaRef.object.effect = effect





    def ChangeEffect(self, attrName, meshes = None):
        if meshes is None:
            meshes = self.meshes
        SkinLightmapRenderer.DoChangeEffect(attrName, meshes)



    @staticmethod
    def DoRestoreShaders(meshes):
        for (meshRef, meshData,) in meshes.iteritems():
            mesh = meshRef.object
            for (areaRef, effect,) in meshData.origEffect.iteritems():
                if areaRef.object:
                    areaRef.object.effect = effect





    @bluepy.CCP_STATS_ZONE_METHOD
    def RestoreShaders(self, meshes = None):
        if meshes is None:
            meshes = self.meshes
        SkinLightmapRenderer.DoRestoreShaders(meshes)



    @staticmethod
    def IsScattering(mesh):
        if mesh.name.startswith('head'):
            for a in mesh.opaqueAreas:
                if a.effect is not None:
                    name = a.effect.name.lower()
                    if name.startswith('c_skin') and 'tearduct' not in name:
                        return True

        return False



    @bluepy.CCP_STATS_ZONE_METHOD
    def BindLightmapShader(self, mesh):
        if SkinLightmapRenderer.IsScattering(mesh):
            self.AddMesh(mesh)
            return True
        if self.useOptix:
            pass
        return False



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetSkinnedObject(self, skinnedObject):
        if self.skinnedObject != skinnedObject or self.refreshMeshes:
            self.skinnedObject = skinnedObject
            self.meshes = {}
            self.oxMeshes = {}
        self.refreshMeshes = False
        if skinnedObject is None:
            return 
        haveNewMeshes = False
        for mesh in skinnedObject.visualModel.meshes:
            for meshRef in self.meshes:
                if meshRef.object == mesh:
                    break
            else:
                haveNewMeshes = self.BindLightmapShader(mesh) or haveNewMeshes


        scene2 = SkinLightmapRenderer.Scene()
        scene2.filterList.removeAt(-1)
        scene2.filterList.append(skinnedObject)
        if haveNewMeshes:
            self.RenderStretchmap()



    @bluepy.CCP_STATS_ZONE_METHOD
    def Refresh(self, immediateUpdate = False):
        self.refreshMeshes = True
        if immediateUpdate:
            self.SetSkinnedObject(self.skinnedObject)



    @staticmethod
    def DoCopyMeshesToVisual(skinnedObject, meshList):
        if skinnedObject is None or skinnedObject.visualModel is None:
            return 
        skinnedObject.visualModel.meshes.removeAt(-1)
        for mesh in meshList:
            skinnedObject.visualModel.meshes.append(mesh)




    @bluepy.CCP_STATS_ZONE_METHOD
    def CopyMeshesToVisual(self, meshList):
        SkinLightmapRenderer.DoCopyMeshesToVisual(self.skinnedObject, meshList)



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnBeforeUnwrap(self):
        self.ChangeEffect('lightmapRenderEffect')
        scene2 = SkinLightmapRenderer.Scene()
        if hasattr(scene2, 'updateShadowCubeMap'):
            scene2.updateShadowCubeMap = False
        if self.skinnedObject is not None and self.skinnedObject.visualModel is not None:
            self.savedMeshes = self.skinnedObject.visualModel.meshes[:]
        filteredMeshes = [ ref.object for ref in self.meshes.iterkeys() if ref.object is not None ]
        self.CopyMeshesToVisual(filteredMeshes)
        for meshData in self.meshes.itervalues():
            for list in meshData.liveParameters:
                for params in list:
                    params[1].value = params[0].value
                    params[2].value = params[0].value



        scene2.useFilterList = True
        trinity.settings.SetValue('apexVisualizeOnly', True)



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnAfterUnwrap(self):
        scene2 = SkinLightmapRenderer.Scene()
        if hasattr(scene2, 'updateShadowCubeMap'):
            scene2.updateShadowCubeMap = True
        self.CopyMeshesToVisual(self.savedMeshes)
        del self.savedMeshes
        scene2.useFilterList = False
        trinity.settings.SetValue('apexVisualizeOnly', False)



    @bluepy.CCP_STATS_ZONE_METHOD
    def CreateRJ(self, target, name, depthClear = 0.0, setDepthStencil = True, clearColor = (0.125, 0.125, 0.125, 1.0), isRT = False):
        rj = trinity.CreateRenderJob(name)
        rj.PushRenderTarget(target.GetSurfaceLevel(0) if not isRT else target).name = name
        if setDepthStencil:
            rj.PushDepthStencil(self.depth)
        rj.Clear(clearColor, depthClear)
        rj.SetStdRndStates(trinity.RM_FULLSCREEN)
        vp = trinity.TriViewport()
        vp.x = 0
        vp.y = 0
        if False:
            rdesc = target.GetDesc()
            vp.width = rdesc['Width']
            vp.height = rdesc['Height']
        else:
            vp.width = target.width
            vp.height = target.height
        rj.SetViewport(vp)
        return rj



    @bluepy.CCP_STATS_ZONE_METHOD
    def RenderBeckmannLookup(self):
        rj = self.CreateRJ(self.beckmannLookup, 'Beckmann precalc')
        rj.SetDepthStencil(None)
        rj.RenderEffect(self.beckmannLookupEffect)
        rj.PopRenderTarget()
        rj.PopDepthStencil()
        rj.ScheduleOnce()



    @staticmethod
    def FuncWrapper(weakSelf, func):
        if weakSelf():
            func(weakSelf())



    @bluepy.CCP_STATS_ZONE_METHOD
    def AddCallback(self, func, name, rj = None):
        cb = trinity.TriStepPythonCB()
        weakSelf = weakref.ref(self)
        cb.SetCallback(lambda : SkinLightmapRenderer.FuncWrapper(weakSelf, func))
        cb.name = name
        rj = rj if rj is not None else self.lightmapRenderJob
        rj.steps.append(cb)



    @bluepy.CCP_STATS_ZONE_METHOD
    def RenderStretchmap(self):
        if SkinLightmapRenderer.Scene() is None:
            return 
        dynamics = SkinLightmapRenderer.Scene().dynamics
        while any(map(lambda x: not x.visible, dynamics)):
            blue.synchro.Yield()

        rj = self.CreateRJ(self.stretchmap, 'Stretchmap precalc', depthClear=None, setDepthStencil=False)
        rj.PushDepthStencil(None)
        self.AddCallback(SkinLightmapRenderer.OnBeforeUnwrap, 'onBeforeUnwrap', rj)
        self.AddCallback(lambda weakSelf: weakSelf.ChangeEffect('stretchmapRenderEffect'), 'change to stretch effect', rj)
        rj.Update(SkinLightmapRenderer.Scene())
        rj.RenderScene(SkinLightmapRenderer.Scene())
        self.AddCallback(SkinLightmapRenderer.OnAfterUnwrap, 'onAfterUnwrap', rj)
        self.AddCallback(SkinLightmapRenderer.RestoreShaders, 'restoreShaders', rj)
        rj.PopDepthStencil()
        rj.PopRenderTarget()
        rj.ScheduleOnce()
        rj.WaitForFinish()
        if False:
            self.SaveTarget(self.stretchmap, 'c:/depot/smz.dds')
            self.DebugPrint('stretchmap saved to c:/depot/smz.dds')



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnBeforeBlur(self):
        rj = self.lightmapRenderJob
        self.paramLightmap.SetResource(self.lightmap if not self.useOptix else self.oxDiffuseTexture)
        self.paramStretchmap.SetResource(self.stretchmap)



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnBeforeExpand(self):
        rj = self.lightmapRenderJob
        self.paramExpandSource.SetResource(self.scatteredLightmap)



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnAfterExpand(self):
        rj = self.lightmapRenderJob
        self.ChangeEffect('lightmapApplyEffect')



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnBeforeOptixPositionsUV(self):
        scene2 = SkinLightmapRenderer.Scene()
        self.ChangeEffect('oxPosWorldUVEffect', meshes=self.oxMeshes)
        if hasattr(scene2, 'updateShadowCubeMap'):
            scene2.updateShadowCubeMap = False
        if self.skinnedObject is not None and self.skinnedObject.visualModel is not None:
            self.savedMeshes = self.skinnedObject.visualModel.meshes[:]
        filteredMeshes = [ ref.object for ref in self.oxMeshes.iterkeys() if ref.object is not None ]
        self.CopyMeshesToVisual(filteredMeshes)
        scene2.useFilterList = True



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnBeforeOptixNormalsUV(self):
        self.ChangeEffect('oxNormalWorldUVEffect', meshes=self.oxMeshes)



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnBeforeOptixPositions(self):
        self.ChangeEffect('oxPosWorldEffect', meshes=self.oxMeshes)



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnBeforeOptixNormals(self):
        self.ChangeEffect('oxNormalWorldEffect', meshes=self.oxMeshes)



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnAfterOptix(self):
        scene2 = SkinLightmapRenderer.Scene()
        self.RestoreShaders(meshes=self.oxMeshes)
        if hasattr(scene2, 'updateShadowCubeMap'):
            scene2.updateShadowCubeMap = True
        self.CopyMeshesToVisual(self.savedMeshes)
        del self.savedMeshes
        scene2.useFilterList = False



    @bluepy.CCP_STATS_ZONE_METHOD
    def RenderOptiX(self):
        scene2 = SkinLightmapRenderer.Scene()
        rj = self.CreateRJ(self.oxWorldPosMapUV, 'Optix pre-rendering', setDepthStencil=True, clearColor=(0, 0, 0, 0), depthClear=1.0, isRT=True)
        self.AddCallback(SkinLightmapRenderer.OnBeforeOptixPositionsUV, 'onBeforeOptixPositionsUV', rj)
        rj.RenderScene(scene2).name = 'Optix WorldPos (UV space)'

        def SetAndClear(rj, rt):
            rj.SetRenderTarget(rt)
            rj.Clear((0, 0, 0, 0), 1.0)


        self.AddCallback(lambda weakSelf: weakSelf.ChangeEffect('oxNormalWorldUVEffect', meshes=weakSelf.oxMeshes), '', rj)
        SetAndClear(rj, self.oxWorldNormalMapUV)
        rj.RenderScene(scene2)
        self.SetViewport(rj, self.oxWorldPosMap.width, self.oxWorldPosMap.height)
        self.AddCallback(lambda weakSelf: weakSelf.ChangeEffect('oxPosWorldEffect', meshes=weakSelf.oxMeshes), '', rj)
        SetAndClear(rj, self.oxWorldPosMap)
        rj.RenderScene(scene2)
        self.AddCallback(lambda weakSelf: weakSelf.ChangeEffect('oxNormalWorldEffect', meshes=weakSelf.oxMeshes), '', rj)
        SetAndClear(rj, self.oxWorldNormalMap)
        rj.RenderScene(scene2)
        self.AddCallback(SkinLightmapRenderer.OnAfterOptix, 'onAfterOptix', rj)
        rj.PopRenderTarget()
        rj.PopDepthStencil()
        if True:
            blue.resMan.Wait()
            blue.resMan.ClearAllCachedObjects()
            blue.motherLode.clear()
            rj.ScheduleOnce()
            rj.WaitForFinish()
            if True:
                self.SaveTarget(self.oxWorldPosMapUV, 'c:/depot/oxworldposuv.dds', isRT=True)
                self.SaveTarget(self.oxWorldNormalMapUV, 'c:/depot/oxworldnormaluv.dds', isRT=True)
                self.SaveTarget(self.oxWorldPosMap, 'c:/depot/oxworldpos.dds', isRT=True)
                self.SaveTarget(self.oxWorldNormalMap, 'c:/depot/oxworldnormal.dds', isRT=True)
            import paperDoll as PD
            path = 'res:/graphics/effect/optix'
            path = str(blue.rot.PathToFilename(path))
            self.raytracing = PD.SkinRaytracing(path, self.oxWidth, self.oxHeight)
            self.raytracing.Run(self.oxWorldPosMapUV, self.oxWorldNormalMapUV, self.oxWorldPosMap, self.oxWorldNormalMap, self.oxDiffuseLight, self.oxSpecularLight)
            if True:
                rjExtract = trinity.CreateRenderJob('extract')
                rjExtract.SetRenderTarget(self.oxDiffuseLight)
                rjExtract.SetDepthStencil(None)
                self.SetViewport(rjExtract, self.oxDiffuseLight.width, self.oxDiffuseLight.height)
                rjExtract.CopyRtToTexture(self.oxDiffuseTexture)
                rjExtract.SetRenderTarget(self.oxSpecularLight)
                rjExtract.SetDepthStencil(None)
                self.SetViewport(rjExtract, self.oxSpecularLight.width, self.oxSpecularLight.height)
                rjExtract.CopyRtToTexture(self.oxSpecularTexture)
                rjExtract.ScheduleChained()
                rjExtract.WaitForFinish()
            if True:
                self.SaveTarget(self.oxDiffuseLight, 'c:/depot/oxDiffuseLight.dds', isRT=True)
                self.SaveTarget(self.oxDiffuseTexture, 'c:/depot/oxDiffuseTexture.dds', isRT=False)
                self.SaveTarget(self.oxSpecularLight, 'c:/depot/oxSpecularLight.dds', isRT=True)
                self.SaveTarget(self.oxSpecularTexture, 'c:/depot/oxSpecularTexture.dds', isRT=False)
        else:
            rj.ScheduleRecurring()



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetViewport(self, rj, width, height):
        vp = trinity.TriViewport()
        vp.x = 0
        vp.y = 0
        vp.width = width
        vp.height = height
        rj.SetViewport(vp)



    @bluepy.CCP_STATS_ZONE_METHOD
    def RenderLightmap(self):
        if self.useOptix:
            rj = trinity.CreateRenderJob('Lightmap rendering (with Optix)')
            rj.SetStdRndStates(trinity.RM_FULLSCREEN)
            self.SetViewport(rj, self.lightmap.width, self.lightmap.height)
        else:
            rj = self.CreateRJ(self.lightmap, 'Lightmap rendering', depthClear=None, setDepthStencil=False, clearColor=(0, 0, 0, 0))
        self.lightmapRenderJob = rj
        self.AddCallback(SkinLightmapRenderer.OnBeforeUnwrap, 'onBeforeUnwrap')
        doHighZOptimization = False
        if not doHighZOptimization:
            rj.PushDepthStencil(None).name = 'Depthbuffer = None'
        if not self.useOptix:
            rj.RenderScene(SkinLightmapRenderer.Scene()).name = 'Unwrap light pass'
        self.AddCallback(SkinLightmapRenderer.OnAfterUnwrap, 'onAfterUnwrap')
        rj.SetRenderTarget(self.scatteredLightmap.GetSurfaceLevel(0)).name = 'Set Scattermap RT'
        self.AddCallback(SkinLightmapRenderer.OnBeforeBlur, 'onBeforeBlur')
        rj.SetStdRndStates(trinity.RM_FULLSCREEN)
        rj.RenderEffect(self.lightmapScatterEffect).name = 'Light blur pass'
        if self.useExpandOpaque:
            rj.SetRenderTarget(self.lightmap.GetSurfaceLevel(0)).name = 'Set Lightmap RT for expand'
            self.AddCallback(SkinLightmapRenderer.OnBeforeExpand, 'onBeforeExpand')
            rj.RenderEffect(self.lightmapExpandEffect).name = 'Expand lightmap'
        self.AddCallback(SkinLightmapRenderer.OnAfterExpand, 'onAfterExpand')
        if not self.useOptix:
            rj.PopRenderTarget().name = 'PopRT - main scene rendering'
        if not doHighZOptimization and not self.useOptix:
            rj.PopDepthStencil()
        if False:
            rj.ScheduleOnce()
            rj.WaitForFinish()
            self.SaveTarget(self.lightmap, 'c:/depot/lm.dds')
            self.SaveTarget(self.scatteredLightmap, 'c:/depot/slm.dds')
            self.SaveTarget(self.scatteredLightmap, 'c:/depot/games/wod-dev/wod/client/res/slm.dds')
        elif SkinLightmapRenderer.renderJob is not None and SkinLightmapRenderer.renderJob.object is not None:
            step = trinity.TriStepRunJob()
            step.job = rj
            SkinLightmapRenderer.renderJob.object.steps.append(step)
        else:
            rj.ScheduleRecurring()



    @staticmethod
    def SaveTarget(target, path, isRT = False):
        if isRT:
            rdesc = target.GetDesc()
            surface = trinity.TriSurfaceManaged(trinity.device.CreateOffscreenPlainSurface, rdesc['Width'], rdesc['Height'], rdesc['Format'], trinity.TRIPOOL_SYSTEMMEM)
            trinity.device.GetRenderTargetData(target, surface)
            surface.SaveSurfaceToFile(path)
        else:
            target.SaveTextureToFile(path, trinity.TRIIFF_DDS)



    def IsRendering(self):
        return self.lightmapRenderJob is not None



    @bluepy.CCP_STATS_ZONE_METHOD
    def StartRendering(self):
        if self.lightmap is None:
            return 
        if self.lightmapRenderJob is not None:
            return 
        if self.useOptix:
            self.RenderOptiX()
        self.RenderLightmap()



    @bluepy.CCP_STATS_ZONE_METHOD
    def StopRendering(self):
        if self.lightmapRenderJob is None:
            return 
        if SkinLightmapRenderer.renderJob is not None and SkinLightmapRenderer.renderJob.object is not None:
            for step in SkinLightmapRenderer.renderJob.object.steps:
                if step.job == self.lightmapRenderJob:
                    SkinLightmapRenderer.renderJob.object.steps.remove(step)
                    break

        else:
            self.lightmapRenderJob.UnscheduleRecurring()
        self.lightmapRenderJob = None



    def CreateScatterStep(renderJob, scene2):
        step = trinity.TriStepRunJob()
        step.name = 'Subsurface scattering'
        step.job = trinity.CreateRenderJob('Render scattering')
        renderJob.steps.append(step)
        SkinLightmapRenderer.renderJob = blue.BluePythonWeakRef(step.job)
        SkinLightmapRenderer.scene2 = blue.BluePythonWeakRef(scene2)




