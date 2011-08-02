import trinity
import uthread
import blue
import math
import geo2
import copy
import os
import sys
import types
import yaml
import TextureCompositor.TextureCompositor as tc
import RenderTargetManager.RenderTargetManager as rtm
import paperDoll as PD
import locks
lock = locks.RLock()
RTM = rtm.RenderTargetManager()
ST_SHADERRES = 'res:/Graphics/Effect/Managed/Interior/Avatar/SkinnedAvatarBRDF.fx'
RT_SHADERRES = 'res:/Graphics/Effect/Managed/Interior/Avatar/SkinnedAvatarTattooBRDF.fx'
BK_SHADERRES = 'res:/Graphics/Effect/Managed/Interior/Avatar/SkinnedAvatarTattooBaking.fx'
INV_SHADERRES = 'res:/Graphics/Effect/Managed/Interior/Avatar/InvisibleAvatar.fx'
EO_SHADERRES = 'res:/Graphics/Effect/Utility/Compositing/ExpandOpaque.fx'
MASK_SHADERRES = 'res:/Graphics/Effect/Managed/Interior/Avatar/SkinnedAvatarTattooMaskBaking.fx'
DECAL_PROJECTION_DISABLED = -1.0
DECAL_PROJECTION_PLANAR = 0.0
DECAL_PROJECTION_CYLINDRICAL = 1.0
DECAL_PROJECTION_CAMERA = 2.0
DECAL_PROJECTION_EO_LOD_THRESHOLD = 1

def ShowTexture(texture, showAlpha = False):
    import app.Common.RenderWindow as rw
    f = rw.CreateTextureWindow(texture, showAlpha)
    f.Show()



class DecalBaker(object):
    __guid__ = 'paperDoll.DecalBaker'

    def __init__(self, factory):
        self.factory = factory
        self._DecalBaker__avatar = None
        self._gender = None
        self.isReady = True
        self.bakeScene = None
        self.size = None
        self.isPrepared = False
        self.bakingTasklet = None
        self.avatarShaderSettingTasklet = None
        self.decalSettingTasklet = None
        if PD.GENDER_ROOT:
            self.femalePath = 'res:\\Graphics\\Character\\Female\\Paperdoll'
            self.malePath = 'res:\\Graphics\\Character\\Male\\Paperdoll'
        else:
            self.femalePath = 'res:\\Graphics\\Character\\Modular\\Female'
            self.malePath = 'res:\\Graphics\\Character\\Modular\\Male'
        self.femaleBindPose = self.GetBindPose(PD.FEMALE_DECAL_BINDPOSE)
        self.maleBindPose = self.GetBindPose(PD.MALE_DECAL_BINDPOSE)



    def GetBindPose(self, resPath):
        updater = trinity.Tr2GrannyAnimation()
        updater.resPath = resPath
        return updater



    def SetSize(self, size):
        if not (type(size) is tuple or type(size) is list) and len(size) == 2:
            raise TypeError('DecalBaker::SetSize - Size is not a tuple or list of length 2!')
        self.size = size
        self.isPrepared = False



    def __DoBlendShapes(self, doll):
        self.factory.ApplyMorphTargetsToMeshes(self._DecalBaker__avatar.visualModel.meshes, doll.GetMorphTargets())



    def __CreateNudeAvatar(self, doll):
        if doll.gender == PD.GENDER.FEMALE:
            genderPath = self.femalePath
        else:
            genderPath = self.malePath
        self._gender = doll.gender
        options = self.factory.GetOptionsByGender(doll.gender)
        avatar = trinity.Tr2IntSkinnedObject()
        avatar.visualModel = self.factory.CreateVisualModel(doll.gender)
        bodyParts = []
        for nudePartModularPath in PD.DEFAULT_NUDE_PARTS:
            bodyPartTuple = None
            if PD.DOLL_PARTS.HEAD in nudePartModularPath:
                headMod = doll.buildDataManager.GetModifiersByCategory(PD.DOLL_PARTS.HEAD)[0]
                if headMod.redfile:
                    bodyPartTuple = (headMod.name, blue.os.LoadObject(headMod.redfile))
            if not bodyPartTuple:
                mod = self.factory.CollectBuildData(nudePartModularPath, options)
                bodyPartTuple = (mod.name, blue.os.LoadObject(mod.redfile))
            bodyParts.append(bodyPartTuple)

        blue.pyos.BeNice()
        for bodyPartTuple in bodyParts:
            (modname, bodyPart,) = bodyPartTuple
            if bodyPart:
                for mesh in bodyPart.meshes:
                    mesh.name = modname
                    if len(mesh.opaqueAreas) > 0:
                        areasCount = mesh.GetAreasCount()
                        for i in xrange(areasCount):
                            areas = mesh.GetAreas(i)
                            if areas and areas != mesh.opaqueAreas:
                                del areas[:]

                        avatar.visualModel.meshes.append(mesh)


        self._DecalBaker__avatar = avatar
        self._DecalBaker__DoBlendShapes(doll)
        if doll.gender == PD.GENDER.FEMALE:
            bindPose = self.femaleBindPose
        else:
            bindPose = self.maleBindPose
        avatar.animationUpdater = bindPose
        clip = bindPose.grannyRes.GetAnimationName(0)
        bindPose.PlayAnimationEx(clip, 0, 0, 0)
        bindPose.EndAnimation()



    def CreateTargetAvatarFromDoll(self, doll):
        self.isPrepared = False
        self._DecalBaker__CreateNudeAvatar(doll)

        def PrepareAvatar_t():
            self.SetShader_t(self._DecalBaker__avatar, [], BK_SHADERRES, False)


        self.avatarShaderSettingTasklet = uthread.new(PrepareAvatar_t)
        uthread.schedule(self.avatarShaderSettingTasklet)



    def CreateTargetsOnModifier(self, modifier, asRenderTargets = False):
        format = trinity.TRIFMT_A8R8G8B8

        def validateTarget(target, width, height):
            if not (target and target.isGood and target.depth > 0):
                return False
            if target.width != width or target.height != height:
                return False
            if asRenderTargets != target.GetSurfaceLevel(0).usage == trinity.TRIUSAGE_RENDERTARGET:
                return False
            return True



        def checkCreateTargets(usage, pool):
            if modifier.decalData.bodyEnabled and not validateTarget(modifier.mapD.get(PD.DOLL_PARTS.BODY), self.size[0] / 2, self.size[1]):
                modifier.mapD[PD.DOLL_PARTS.BODY] = trinity.device.CreateTexture(self.size[0] / 2, self.size[1], 1, usage, format, pool)
            if modifier.decalData.headEnabled and not validateTarget(modifier.mapD.get(PD.DOLL_PARTS.HEAD), self.size[0] / 2, self.size[1] / 2):
                modifier.mapD[PD.DOLL_PARTS.HEAD] = trinity.device.CreateTexture(self.size[0] / 2, self.size[1] / 2, 1, usage, format, pool)


        if asRenderTargets:
            checkCreateTargets(trinity.TRIUSAGE_RENDERTARGET, trinity.TRIPOOL_DEFAULT)
        else:
            checkCreateTargets(0, trinity.TRIPOOL_MANAGED)



    def BakeDecalToModifier(self, decal, projectedDecalModifier):
        if type(self._DecalBaker__avatar) is not trinity.Tr2IntSkinnedObject:
            raise TypeError('DecalBaker::DoPrepare - Avatar is not set!')
        if type(decal) is not ProjectedDecal:
            raise TypeError('DecalBaker::BakeDecalToModifier - decal is not an instance of PaperDoll::ProjectedDecal!')
        self.isReady = False
        if projectedDecalModifier.decalData != decal:
            projectedDecalModifier.decalData = decal

        def PrepareDecal_t():
            while self.avatarShaderSettingTasklet.alive:
                blue.synchro.Yield()

            self.SetDecal_t(self._DecalBaker__avatar, decal, True, True, True)


        self.decalSettingTasklet = uthread.new(PrepareDecal_t)
        uthread.schedule(self.decalSettingTasklet)
        self.CreateTargetsOnModifier(projectedDecalModifier)
        self.bakingTasklet = uthread.new(self.DoBake_t, projectedDecalModifier)
        uthread.schedule(self.bakingTasklet)



    def _ExpandOpaque(self, bodyPart, targetTex):
        eoMaskPath = 'res:/graphics/character/global/tattoomask/{0}_opaque_mask_{1}.dds'.format(self._gender, bodyPart)
        eoMaskRes = blue.resMan.GetResource(eoMaskPath)
        fx = trinity.Tr2Effect()
        fx.effectFilePath = EO_SHADERRES
        while eoMaskRes.isLoading or fx.effectResource.isLoading:
            blue.synchro.Yield()

        tex = trinity.TriTexture2DParameter()
        tex.name = 'Mask'
        tex.SetResource(eoMaskRes)
        fx.resources.append(tex)
        v = trinity.Tr2Vector2Parameter()
        v.name = 'gMaskSize'
        v.value = (eoMaskRes.width, eoMaskRes.height)
        fx.parameters.append(v)
        tex = trinity.TriTexture2DParameter()
        tex.name = 'Texture'
        tex.SetResource(targetTex)
        fx.resources.append(tex)
        vp = trinity.TriViewport()
        vp.width = targetTex.width
        vp.height = targetTex.height
        v = trinity.Tr2Vector2Parameter()
        v.name = 'gTextureSize'
        v.value = (vp.width, vp.height)
        fx.parameters.append(v)
        useTargetTexAsRenderTarget = targetTex.GetSurfaceLevel(0).usage == trinity.TRIUSAGE_RENDERTARGET
        renderTarget = None
        if useTargetTexAsRenderTarget:
            renderTarget = targetTex.GetSurfaceLevel(0)
        else:
            renderTarget = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, vp.width, vp.height, trinity.TRIFMT_A8R8G8B8, trinity.TRIMULTISAMPLE_NONE, 0, 1)
        rj = trinity.CreateRenderJob('Expanding Opaque')
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
        if not useTargetTexAsRenderTarget:
            rj.CopyRtToTexture(targetTex)
        rj.PopRenderTarget()
        rj.ScheduleChained()
        rj.WaitForFinish()



    def _GenerateCutoutTexture(self, targetTex, uv):
        fx = trinity.Tr2Effect()
        fx.effectFilePath = 'res:/Graphics/Effect/Utility/Compositing/Copyblit.fx'
        while fx.effectResource.isLoading:
            blue.synchro.Yield()

        v = trinity.Tr2Vector4Parameter()
        v.name = 'SourceUVs'
        fx.parameters.append(v)
        v.value = uv
        tex = trinity.TriTexture2DParameter()
        tex.name = 'Texture'
        tex.SetResource(self.sourceTexture)
        fx.resources.append(tex)
        vp = trinity.TriViewport()
        vp.width = targetTex.width
        vp.height = targetTex.height
        useTargetTexAsRenderTarget = targetTex.GetSurfaceLevel(0).usage == trinity.TRIUSAGE_RENDERTARGET
        renderTarget = None
        if useTargetTexAsRenderTarget:
            renderTarget = targetTex.GetSurfaceLevel(0)
        else:
            renderTarget = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, vp.width, vp.height, trinity.TRIFMT_A8R8G8B8, trinity.TRIMULTISAMPLE_NONE, 0, 1)
        rj = trinity.CreateRenderJob('Cutting from source decal texture')
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
        if not useTargetTexAsRenderTarget:
            rj.CopyRtToTexture(targetTex)
        rj.PopRenderTarget()
        rj.ScheduleChained()
        rj.WaitForFinish()



    def DoBake_t(self, projectedDecalModifier):
        with lock:
            while self.decalSettingTasklet.alive:
                blue.synchro.Yield()

            self.bakeScene = trinity.WodBakingScene()
            self.bakeScene.Avatar = self._DecalBaker__avatar
            format = trinity.TRIFMT_A8R8G8B8
            self.sourceTexture = trinity.device.CreateTexture(self.size[0], self.size[1], 1, trinity.TRIUSAGE_RENDERTARGET, format, trinity.TRIPOOL_DEFAULT)
            sourceVP = trinity.TriViewport()
            sourceVP.width = self.size[0]
            sourceVP.height = self.size[1]
            rj = trinity.CreateRenderJob('Baking out source decal texture')
            rj.PushRenderTarget(self.sourceTexture.GetSurfaceLevel(0))
            rj.SetProjection(trinity.TriProjection())
            rj.SetView(trinity.TriView())
            rj.SetViewport(sourceVP)
            rj.SetDepthStencil(None)
            rj.Clear((0.0, 0.0, 0.0, 0.0), None)
            rj.SetStdRndStates(trinity.RM_FULLSCREEN)
            rj.Update(self.bakeScene)
            rj.RenderScene(self.bakeScene)
            rj.PopRenderTarget()
            rj.ScheduleChained()
            rj.WaitForFinish()
            if projectedDecalModifier.decalData.bodyEnabled:
                self._GenerateCutoutTexture(projectedDecalModifier.mapD[PD.DOLL_PARTS.BODY], (0, 0, 0.5, 1))
                self._ExpandOpaque(PD.DOLL_PARTS.BODY, projectedDecalModifier.mapD[PD.DOLL_PARTS.BODY])
            elif projectedDecalModifier.mapD.get(PD.DOLL_PARTS.BODY):
                del projectedDecalModifier.mapD[PD.DOLL_PARTS.BODY]
            if projectedDecalModifier.decalData.headEnabled:
                self._GenerateCutoutTexture(projectedDecalModifier.mapD[PD.DOLL_PARTS.HEAD], (0.5, 0, 1.0, 0.5))
                self._ExpandOpaque(PD.DOLL_PARTS.HEAD, projectedDecalModifier.mapD[PD.DOLL_PARTS.HEAD])
            elif projectedDecalModifier.mapD.get(PD.DOLL_PARTS.HEAD):
                del projectedDecalModifier.mapD[PD.DOLL_PARTS.HEAD]
            self.bakeScene = None
            if hasattr(self, 'sourceTexture'):
                del self.sourceTexture
            self.isReady = True



    def SetShader_t(self, avatar, targetsToIgnore, shaderres, allTargets = False):
        effect = trinity.Tr2Effect()
        effect.effectFilePath = shaderres
        while effect.effectResource.isLoading:
            blue.synchro.Yield()

        effect.PopulateParameters()
        effect.RebuildCachedData()
        for mesh in avatar.visualModel.meshes:
            areasList = [mesh.opaqueAreas, mesh.decalAreas, mesh.transparentAreas]
            if allTargets or mesh.name not in targetsToIgnore:
                for areas in areasList:
                    for area in areas:
                        transformUV = None
                        for p in area.effect.parameters:
                            if p.name == 'TransformUV0':
                                transformUV = p.value
                                break

                        area.effect = effect.CopyTo()
                        for p in area.effect.parameters:
                            if p.name == 'TransformUV0':
                                p.value = transformUV
                                break







    def SetShaderValue_t(self, avatar, ignoreTargets, name, value, allTargets = False):
        for mesh in avatar.visualModel.meshes:
            for effect in PD.GetEffectsFromMesh(mesh):
                if allTargets or mesh.name not in ignoreTargets:
                    for p in effect.parameters:
                        if p.name == name:
                            p.value = value

                effect.RebuildCachedData()





    def SetDecal_t(self, avatar, decal, setTexture, setMask, forceReload = False):
        if decal is None:
            return 
        while decal.BusyLoading():
            blue.synchro.Yield()

        for mesh in iter(avatar.visualModel.meshes):
            for effect in PD.GetEffectsFromMesh(mesh):
                layer = decal.layer
                for p in effect.parameters:
                    valuesToSet = None
                    if p.name == 'TattooYawPitchRoll':
                        valuesToSet = decal.GetYPR()
                    elif p.name == 'TattooPosition':
                        valuesToSet = decal.GetPositionAndScale()
                    elif p.name == 'TattooOptions':
                        valuesToSet = decal.GetOptions()
                    elif p.name == 'TattooDimensions':
                        valuesToSet = decal.GetDimensions()
                    elif p.name == 'TattooAspectRatio' and hasattr(decal, 'aspectRatio'):
                        valuesToSet = decal.aspectRatio
                    elif p.name == 'TattooPickingLayer':
                        valuesToSet = decal.layer
                    if type(valuesToSet) == tuple:
                        valLen = len(valuesToSet)
                        if valLen < len(p.value):
                            valuesToSet = valuesToSet + p.value[valLen:]
                    if valuesToSet:
                        p.value = valuesToSet

                resourceNameFound = False
                if setTexture:
                    resourceNameFound = self.SetTexture_t('TattooTextureMap', layer, decal.textureResource, effect, forceReload)
                if setMask and resourceNameFound:
                    resourceNameFound = self.SetTexture_t('TattooTextureMask', layer, decal.maskResource, effect, forceReload)





    def SetTexture_t(self, name, layer, texture, effect, forceReload = False):
        for (i, r,) in enumerate(effect.resources):
            if r.name == name:
                r.SetResource(texture)
                r.filterMode = trinity.TRIFILTER_LINEAR
                r.mipFilterMode = trinity.TRIFILTER_LINEAR
                return True

        return False




class ProjectedDecal(object):
    __guid__ = 'paperDoll.ProjectedDecal'

    def __init__(self):
        self.layer = 0
        self.azimuth = 0.0
        self.incline = 1.5707963267948966
        self.bodyEnabled = True
        self.headEnabled = True
        self.posx = 0.0
        self.posy = 0.0
        self.posz = 0.0
        self.scale = 0.0
        self.aspectRatio = 1.0
        self.angleRotation = 180.0
        self.mode = DECAL_PROJECTION_DISABLED
        self.flipx = False
        self.flipy = False
        self.offsety = 0.0
        self.offsetx = 0.0
        self.radius = 2.0
        self.height = 4.0
        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.planarBeta = 0.0
        self.planarScale = 0.0
        self.maskPathEnabled = False
        self.texturePath = ''
        self.maskPath = ''
        self.label = ''
        self.textureResource = None
        self.maskResource = None



    def __str__(self):
        return yaml.dump(self.__getstate__(), default_flow_style=False, Dumper=yaml.CDumper)



    def __getstate__(self):
        state = dict()
        for (key, value,) in self.__dict__.iteritems():
            if type(value) is not trinity.TriTextureRes:
                state[key] = copy.copy(value)
            else:
                state[key] = None

        return state



    def __eq__(self, other):
        if not other:
            return False
        typesThatMatter = (float,
         bool,
         str,
         int)
        for (key, val,) in other.__dict__.iteritems():
            if key not in self.__dict__:
                return False
            if type(self.__dict__[key]) in typesThatMatter:
                if self.__dict__[key] != val:
                    return False

        return True



    def __ne__(self, other):
        return not self.__eq__(other)



    def BusyLoading(self):
        if self.texturePath and not self.textureResource:
            raise AttributeError('PaperDoll::ProjectedDecal - Decal has texturepath defined but no texture resource and is not loading it!')
        if self.maskPath and not self.maskResource:
            raise AttributeError('PaperDoll::ProjectedDecal - Decal has maskpath defined but no texture resource and is not loading it!')
        loading = self.textureResource and self.textureResource.isLoading or self.maskResource and self.maskResource.isLoading
        return loading



    def __GetResourceSetPath(self, path, pathMember):
        if path:
            setattr(self, pathMember, path)
            return blue.resMan.GetResource(str(path))
        else:
            return None



    def SetTexturePath(self, path):
        self.textureResource = self._ProjectedDecal__GetResourceSetPath(path, 'texturePath')



    def SetMaskPath(self, path):
        self.maskResource = self._ProjectedDecal__GetResourceSetPath(path, 'maskPath')



    def SetCylindricalProjection(self):
        self.mode = DECAL_PROJECTION_CYLINDRICAL



    def SetPlanarProjection(self):
        self.mode = DECAL_PROJECTION_PLANAR



    def SetDisabledProjection(self):
        self.mode = DECAL_PROJECTION_DISABLED



    def SetPosition(self, posx, posy, posz):
        self.posx = posx
        self.posy = posy
        self.posz = posz



    def GetPositionAndScale(self):
        return (self.posx,
         self.posy,
         self.posz,
         self.scale)



    def SetOptions(self, angleRotation, flipX, flipY, offsetY = 0.0, offsetX = 0.0):
        self.angleRotation = angleRotation
        self.flipx = flipX
        self.flipy = flipY
        self.offsety = offsetY
        self.offsetx = offsetX



    def GetOptions(self):
        flipPack = 10.0 * float(self.flipy) + float(self.flipx)
        return (self.angleRotation,
         flipPack,
         self.offsety,
         self.offsetx)



    def SetDimensions(self, radius, height):
        self.radius = radius
        self.height = height



    def GetDimensions(self):
        if self.mode == DECAL_PROJECTION_PLANAR:
            return (self.planarBeta, self.planarScale, float(self.maskPathEnabled))
        else:
            return (self.radius, self.height, float(self.maskPathEnabled))



    def SetYPR(self, yaw, pitch, roll):
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll



    def GetYPR(self):
        return (self.yaw,
         self.pitch,
         self.roll,
         self.mode)



    @staticmethod
    def Load(source):
        inst = source
        if type(source) in types.StringTypes:
            inst = PD.LoadYamlFileNicely(source)
        projectedDecal = PD.ProjectedDecal()
        for (key, val,) in inst.__dict__.iteritems():
            if key in projectedDecal.__dict__:
                projectedDecal.__dict__[key] = val

        if inst.texturePath:
            projectedDecal.SetTexturePath(inst.texturePath)
        if inst.maskPath:
            projectedDecal.SetMaskPath(inst.maskPath)
        return projectedDecal



    @staticmethod
    def Save(source, resPath):
        f = file(resPath, 'w')
        yaml.dump(source, f, default_flow_style=False, Dumper=yaml.CDumper)
        f.flush()
        f.close()



import util
exports = util.AutoExports('paperDoll', locals())

