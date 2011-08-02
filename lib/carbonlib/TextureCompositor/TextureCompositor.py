import trinity
import blue
import types
import os
import sys
import time
import log
import bluepy
import paperDoll as PD
(RUN_RENDER_JOB, RETURN_RENDER_JOB,) = range(2)
rm = blue.resMan
EFFECT_LOCATION = 'res:/Graphics/Effect/Utility/Compositing'

def GetEffectsToCache():
    names = ['SimpleBlit',
     'MaskedNormalBlit',
     'TwistNormalBlit',
     'ColorFill',
     'BlitIntoAlpha1',
     'BlitIntoAlpha2',
     'BlitIntoAlphaWithZones',
     'ColorizedBlit',
     'ColorizedBlit_AlphaTest',
     'ColorizedCopyBlit',
     'PatternBlit']
    effects = []
    for each in names:
        effect = trinity.Tr2Effect()
        effect.effectFilePath = EFFECT_LOCATION + '/' + each + '.fx'
        effects.append(effect)

    return effects



class TextureCompositor(object):
    __metaclass__ = bluepy.CCP_STATS_ZONE_PER_METHOD
    cachedEffects = None
    autoSizeReduce = {256: '_256',
     512: '_512',
     4096: '_4K'}
    autoSizeFallback = {256: '_512'}
    autoSizeEnable = True
    autoSizeWarn = True

    def __init__(self, renderTarget, targetWidth = 0):
        self.renderJob = None
        self.renderTarget = renderTarget
        self.resourcesToLoad = []
        self.targetWidth = targetWidth
        self.resFile = blue.ResFile()
        self.lastUsedResources = []
        self.SetStartingState()
        if not TextureCompositor.cachedEffects:
            TextureCompositor.cachedEffects = GetEffectsToCache()



    def FindExactSourceMatch(self, path):
        if TextureCompositor.autoSizeEnable and self.targetWidth in TextureCompositor.autoSizeReduce:
            r = self.resFile
            testPath = path[:-4] + TextureCompositor.autoSizeReduce[self.targetWidth] + path[-4:].lower()
            if PD.PerformanceOptions.useLod2DDS and testPath.endswith('_256.png'):
                testPath = '{0}_256.dds'.format(testPath[:-8])
                if r.FileExists(testPath):
                    r.Close()
                    return path
                log.LogWarn('Compositing: LOD2 texture missing: ' + testPath + ' for ' + path)
            if r.FileExists(testPath):
                path = testPath
            else:
                fallbackSuffix = TextureCompositor.autoSizeFallback.get(self.targetWidth, '')
                testPath = path[:-4] + fallbackSuffix + path[-4:]
                if fallbackSuffix and r.FileExists(testPath):
                    if TextureCompositor.autoSizeWarn:
                        log.LogWarn('Compositing: found LOD1 fallback texture: ' + testPath + ' for ' + path)
                    path = testPath
                elif TextureCompositor.autoSizeWarn:
                    log.LogWarn('Compositing: no LOD speedup, fallback also not found: ' + testPath + ' for ' + path)
            r.Close()
        return path



    def SetStartingState(self):
        self.isReady = False
        self.isDone = False
        self.texturesWithCutouts = []
        self.texturesByResourceID = {}
        self.resourcesToLoad = []



    def AppendResource(self, effect, paramName, resPath, cutoutName = None, paramType = None, mapType = ''):
        if paramType is None:
            paramType = trinity.TriTexture2DParameter()
        paramRes = None
        error = False
        skipLoad = False
        if not resPath:
            error = True
        elif type(resPath) in types.StringTypes:
            if type(resPath) == types.UnicodeType:
                resPath = str(resPath)
            paramRes = blue.motherLode.Lookup(resPath)
            if not paramRes:
                resPath = self.FindExactSourceMatch(resPath)
                paramRes = rm.GetResource(resPath)
        elif type(resPath) == trinity.TriTextureRes:
            paramRes = resPath
            skipLoad = True
        elif hasattr(resPath, 'resource'):
            paramRes = resPath.resource
        else:
            error = True
        if error or paramRes is None:
            raise Exception('Invalid resource passed to texture compositor!')
            sys.exc_clear()
        param = paramType
        param.name = paramName
        param.SetResource(paramRes)
        item = (paramRes,
         effect,
         cutoutName,
         mapType)
        if cutoutName:
            self.texturesWithCutouts.append(item)
        if not skipLoad:
            self.texturesByResourceID[id(paramRes)] = item
            self.resourcesToLoad.append(paramRes)
        effect.resources.append(param)



    def AppendParameter(self, effect, paramType, paramName, paramValue):
        param = paramType
        param.name = paramName
        if type(paramValue) == type([]):
            paramValue = tuple(paramValue)
        param.value = paramValue
        effect.parameters.append(param)



    def MakeEffect(self, effectName):
        effect = trinity.Tr2Effect()
        effect.effectFilePath = EFFECT_LOCATION + '/' + effectName + '.fx'
        self.resourcesToLoad.append(effect.effectResource)
        return effect



    def Start(self, clear = True):
        self.SetStartingState()
        self.renderJob = trinity.CreateRenderJob('Texture Compositing')
        self.renderJob.SetRenderTarget(self.renderTarget)
        self.renderJob.SetDepthStencil(None)
        if clear:
            cl = self.renderJob.Clear((0.0, 0.0, 0.0, 0.0), 1.0)
            cl.isDepthCleared = False
        self.renderJob.SetStdRndStates(trinity.RM_FULLSCREEN)



    def End(self):
        isDone = False
        while not isDone:
            isLoading = len(self.resourcesToLoad) > 0
            while isLoading:
                isLoading = False
                for each in self.resourcesToLoad:
                    isLoading = each.isLoading
                    if isLoading:
                        blue.synchro.Yield()
                        break


            isDone = True
            for each in iter(self.resourcesToLoad):
                if each.isLoading:
                    isDone = False
                    break


        self.isReady = True
        self.lastUsedResources = self.resourcesToLoad



    def Finalize(self, format, w, h, generateMipmap = False, textureToCopyTo = None):
        if not (format and w and h):
            raise AttributeError('Must provide format, width and height parameters and they must not be None')
        if self.isReady:
            tex = None
            if format and w and h:
                for r in iter(self.texturesWithCutouts):
                    cutout = [r[0].cutoutX,
                     r[0].cutoutY,
                     r[0].cutoutWidth,
                     r[0].cutoutHeight]
                    self.AppendParameter(r[1], trinity.Tr2Vector4Parameter(), r[2], cutout)

                if not textureToCopyTo:
                    pool = trinity.TRIPOOL_MANAGED
                    usage = 0
                    if not trinity.settings.GetValue('useManagedDX9Buffers'):
                        pool = trinity.TRIPOOL_DEFAULT
                        usage = trinity.TRIUSAGE_DYNAMIC
                    tex = None
                    copy = None
                    while tex is None and w > 8:
                        try:
                            tex = trinity.device.CreateTexture(w, h, 0 if generateMipmap else 1, usage, format, pool)
                        except (trinity.E_OUTOFMEMORY, trinity.D3DERR_OUTOFVIDEOMEMORY):
                            w /= 2
                            h /= 2
                            blue.synchro.Yield()

                else:
                    tex = textureToCopyTo
                if tex:
                    copy = self.renderJob.CopyRtToTexture(tex)
                    copy.generateMipmap = generateMipmap
                if tex:
                    for step in iter(self.renderJob.steps):
                        if type(step) == trinity.TriStepRenderEffect:
                            lowPath = step.effect.effectFilePath.lower()
                            if lowPath.endswith('simpleblit.fx') or lowPath.endswith('copyblit.fx'):
                                mapType = ''
                                mapFormat = 0
                                for res in iter(step.effect.resources):
                                    if res.name == 'Texture':
                                        r = self.texturesByResourceID.get(id(res.resource))
                                        if r:
                                            mapType = r[3]
                                            mapFormat = res.resource.format

                                if mapType == 'N' and mapFormat == trinity.TRIFMT_A8L8:
                                    step.effect.effectFilePath = step.effect.effectFilePath[:-3] + '_N16.fx'

                    self.renderJob.ScheduleChained()
                    try:
                        self.renderJob.WaitForFinish()
                    except Exception:
                        self.renderJob.CancelChained()
                        raise 
            self.texturesWithCutouts = []
            self.texturesByResourceID.clear()
            self.isDone = True
            return tex
        raise AttributeError('isReady must be true when Finalize() is called.')



    def CompositeTexture(self, effect, subrect = None):
        vp = trinity.TriViewport()
        if subrect:
            vp.x = subrect[0]
            vp.y = subrect[1]
            vp.width = subrect[2] - subrect[0]
            vp.height = subrect[3] - subrect[1]
        else:
            rdesc = self.renderTarget.GetDesc()
            vp.x = 0
            vp.y = 0
            vp.width = rdesc['Width']
            vp.height = rdesc['Height']
        self.renderJob.SetViewport(vp)
        self.renderJob.RenderEffect(effect)



    def CopyBlitTexture(self, path, subrect = None, srcRect = None, isNormalMap = False):
        effect = self.MakeEffect('Copyblit')
        self.AppendResource(effect, 'Texture', path, 'TextureReverseUV', mapType='N' if isNormalMap else '')
        if srcRect:
            self.AppendParameter(effect, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_SEPARATEALPHABLENDENABLE, 1)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ZERO)
        self.CompositeTexture(effect, subrect)



    def MaskedNormalBlitTexture(self, path, strength, subrect = None, srcRect = None):
        effect = self.MakeEffect('MaskedNormalBlit')
        self.AppendResource(effect, 'Texture', path, 'TextureReverseUV')
        self.AppendParameter(effect, trinity.TriFloatParameter(), 'Strength', strength)
        if srcRect:
            self.AppendParameter(effect, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_SEPARATEALPHABLENDENABLE, 1)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ZERO)
        self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        self.CompositeTexture(effect, subrect)



    def TwistNormalBlitTexture(self, path, strength, subrect = None, srcRect = None):
        effect = self.MakeEffect('TwistNormalBlit')
        self.AppendResource(effect, 'Texture', path, 'TextureReverseUV')
        self.AppendParameter(effect, trinity.TriFloatParameter(), 'Strength', strength)
        if srcRect:
            self.AppendParameter(effect, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_SEPARATEALPHABLENDENABLE, 1)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ZERO)
        self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        self.CompositeTexture(effect, subrect)



    def FillColor(self, color, subrect = None, skipAlpha = False, addAlpha = False):
        effect = self.MakeEffect('ColorFill')
        self.AppendParameter(effect, trinity.Tr2Vector4Parameter(), 'color1', color)
        self.renderJob.SetRenderState(trinity.D3DRS_SEPARATEALPHABLENDENABLE, 1)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        if skipAlpha:
            self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ZERO)
        else:
            self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        if addAlpha:
            self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        else:
            self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ZERO)
        self.CompositeTexture(effect, subrect)



    def SubtractAlphaFromAlpha(self, path, subrect = None, srcRect = None):
        effect = self.MakeEffect('BlitIntoAlpha1')
        self.AppendResource(effect, 'Texture', path, 'TextureReverseUV')
        if srcRect:
            self.AppendParameter(effect, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_SEPARATEALPHABLENDENABLE, 1)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_REVSUBTRACT)
        self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        self.CompositeTexture(effect, subrect)



    def BlitTextureIntoAlpha(self, path, subrect = None, srcRect = None):
        effect = self.MakeEffect('BlitIntoAlpha1')
        effect2 = self.MakeEffect('BlitIntoAlpha2')
        self.AppendResource(effect, 'Texture', path, 'TextureReverseUV')
        self.AppendResource(effect2, 'Texture', path, 'TextureReverseUV')
        self.AppendResource(effect2, 'Mask', path, 'MaskReverseUV')
        if srcRect:
            self.AppendParameter(effect, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
            self.AppendParameter(effect2, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_SEPARATEALPHABLENDENABLE, 1)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_REVSUBTRACT)
        self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        self.CompositeTexture(effect, subrect)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        self.CompositeTexture(effect2, subrect)



    def BlitTextureIntoAlphaWithMask(self, path, mask, subrect = None, srcRect = None):
        effect = self.MakeEffect('BlitIntoAlpha1')
        effect2 = self.MakeEffect('BlitIntoAlpha2')
        self.AppendResource(effect, 'Texture', path, 'TextureReverseUV')
        self.AppendResource(effect2, 'Texture', path, 'TextureReverseUV')
        self.AppendResource(effect2, 'Mask', mask, 'MaskReverseUV')
        if srcRect:
            self.AppendParameter(effect, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
            self.AppendParameter(effect2, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_SEPARATEALPHABLENDENABLE, 1)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_REVSUBTRACT)
        self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        self.CompositeTexture(effect, subrect)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        self.CompositeTexture(effect2, subrect)



    def BlitAlphaIntoAlphaWithMask(self, path, mask, subrect = None, srcRect = None):
        effect = self.MakeEffect('BlitIntoAlpha1')
        effect2 = self.MakeEffect('BlitIntoAlpha2')
        self.AppendResource(effect, 'Texture', mask, 'TextureReverseUV')
        self.AppendResource(effect2, 'Texture', path, 'TextureReverseUV')
        self.AppendResource(effect2, 'Mask', mask, 'MaskReverseUV')
        if srcRect:
            self.AppendParameter(effect, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
            self.AppendParameter(effect2, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_SEPARATEALPHABLENDENABLE, 1)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_REVSUBTRACT)
        self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        self.CompositeTexture(effect, subrect)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        self.CompositeTexture(effect2, subrect)



    def BlitAlphaIntoAlphaWithMaskAndZones(self, path, mask, zone, values, subrect = None, srcRect = None):
        effect = self.MakeEffect('BlitIntoAlpha1')
        effect2 = self.MakeEffect('BlitIntoAlphaWithZones')
        self.AppendResource(effect, 'Texture', mask, 'TextureReverseUV')
        self.AppendResource(effect2, 'Texture', path, 'TextureReverseUV')
        self.AppendResource(effect2, 'Mask', mask, 'MaskReverseUV')
        self.AppendResource(effect2, 'ZoneMap', zone, 'ZoneReverseUV')
        if srcRect:
            self.AppendParameter(effect, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
            self.AppendParameter(effect2, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
        self.AppendParameter(effect2, trinity.Tr2Vector4Parameter(), 'Color1', values)
        self.renderJob.SetRenderState(trinity.D3DRS_SEPARATEALPHABLENDENABLE, 1)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_REVSUBTRACT)
        self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        self.CompositeTexture(effect, subrect)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        self.CompositeTexture(effect2, subrect)



    def BlitTexture(self, path, maskPath, weight, subrect = None, addAlpha = False, skipAlpha = False, srcRect = None, multAlpha = False, isNormalMap = False):
        effect = self.MakeEffect('SimpleBlit')
        self.AppendResource(effect, 'Texture', path, 'TextureReverseUV', mapType='N' if isNormalMap else '')
        self.AppendResource(effect, 'Mask', maskPath, 'MaskReverseUV')
        self.AppendParameter(effect, trinity.TriFloatParameter(), 'Strength', weight)
        if multAlpha:
            self.AppendParameter(effect, trinity.TriFloatParameter(), 'MultAlpha', 1.0)
        if srcRect:
            self.AppendParameter(effect, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_SEPARATEALPHABLENDENABLE, 1)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        if skipAlpha:
            self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ZERO)
        else:
            self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        if addAlpha:
            self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        else:
            self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ZERO)
        self.CompositeTexture(effect, subrect)



    def ColorizedBlitTexture(self, detail, zone, overlay, color1, color2, color3, subrect = None, addAlpha = False, skipAlpha = False, useAlphaTest = False, srcRect = None, weight = 1.0, mask = None):
        if useAlphaTest:
            effect = self.MakeEffect('ColorizedBlit_AlphaTest')
        else:
            effect = self.MakeEffect('ColorizedBlit')
        self.AppendResource(effect, 'DetailMap', detail, 'DetailReverseUV')
        self.AppendResource(effect, 'ZoneMap', zone, 'ZoneReverseUV')
        self.AppendResource(effect, 'OverlayMap', overlay, 'OverlayReverseUV')
        self.AppendParameter(effect, trinity.TriFloatParameter(), 'Strength', weight)
        if mask:
            self.AppendResource(effect, 'MaskMap', mask, 'MaskReverseUV2')
        self.AppendParameter(effect, trinity.TriVector4Parameter(), 'Color1', color1)
        self.AppendParameter(effect, trinity.TriVector4Parameter(), 'Color2', color2)
        self.AppendParameter(effect, trinity.TriVector4Parameter(), 'Color3', color3)
        if srcRect:
            self.AppendParameter(effect, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
        if mask:
            self.AppendParameter(effect, trinity.TriFloatParameter(), 'UseMask', 1.0)
        self.renderJob.SetRenderState(trinity.D3DRS_SEPARATEALPHABLENDENABLE, 1)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        if skipAlpha:
            self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ZERO)
        else:
            self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        if addAlpha:
            self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        else:
            self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ZERO)
        self.CompositeTexture(effect, subrect)



    def ColorizedCopyBlitTexture(self, detail, zone, overlay, color1, color2, color3, subrect = None, addAlpha = False, srcRect = None, weight = 1.0):
        effect = self.MakeEffect('ColorizedCopyBlit')
        self.AppendResource(effect, 'DetailMap', detail, 'DetailReverseUV')
        self.AppendResource(effect, 'ZoneMap', zone, 'ZoneReverseUV')
        self.AppendResource(effect, 'OverlayMap', overlay, 'OverlayReverseUV')
        self.AppendParameter(effect, trinity.TriFloatParameter(), 'Strength', weight)
        self.AppendParameter(effect, trinity.TriVector4Parameter(), 'Color1', color1)
        self.AppendParameter(effect, trinity.TriVector4Parameter(), 'Color2', color2)
        self.AppendParameter(effect, trinity.TriVector4Parameter(), 'Color3', color3)
        if srcRect:
            self.AppendParameter(effect, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_SEPARATEALPHABLENDENABLE, 1)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ZERO)
        self.CompositeTexture(effect, subrect)



    def PatternBlitTexture(self, pattern, detail, zone, overlay, patterncolor1, patterncolor2, patterncolor3, color2, color3, subrect = None, patternTransform = (0, 0, 8, 8), patternRotation = 0.0, addAlpha = False, skipAlpha = False, srcRect = None):
        effect = self.MakeEffect('PatternBlit')
        self.AppendResource(effect, 'PatternMap', pattern, 'PatternReverseUV')
        self.AppendResource(effect, 'DetailMap', detail, 'DetailReverseUV')
        self.AppendResource(effect, 'ZoneMap', zone, 'ZoneReverseUV')
        self.AppendResource(effect, 'OverlayMap', overlay, 'OverlayReverseUV')
        self.AppendParameter(effect, trinity.TriVector4Parameter(), 'PatternColor1', patterncolor1)
        self.AppendParameter(effect, trinity.TriVector4Parameter(), 'PatternColor2', patterncolor2)
        self.AppendParameter(effect, trinity.TriVector4Parameter(), 'PatternColor3', patterncolor3)
        self.AppendParameter(effect, trinity.TriVector4Parameter(), 'PatternTransform', patternTransform)
        self.AppendParameter(effect, trinity.TriFloatParameter(), 'PatternRotation', patternRotation)
        self.AppendParameter(effect, trinity.TriVector4Parameter(), 'Color2', color2)
        self.AppendParameter(effect, trinity.TriVector4Parameter(), 'Color3', color3)
        if srcRect:
            self.AppendParameter(effect, trinity.Tr2Vector4Parameter(), 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_SEPARATEALPHABLENDENABLE, 1)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        if skipAlpha:
            self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ZERO)
        else:
            self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        if addAlpha:
            self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        else:
            self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ZERO)
        self.CompositeTexture(effect, subrect)




def GetAsResource(resPath):
    paramRes = None
    error = False
    if not resPath:
        error = True
    elif type(resPath) in types.StringTypes:
        if type(resPath) == types.UnicodeType:
            resPath = str(resPath)
        paramRes = rm.GetResource(resPath)
    elif type(resPath) == trinity.TriTextureRes:
        paramRes = resPath
    elif hasattr(resPath, 'resource'):
        paramRes = resPath.resource
    else:
        error = True
    if error:
        raise Exception('Invalid resourced passed to texture compositor!')
    else:
        return paramRes



def Resize(map, finalSize, format = None):
    map = GetAsResource(map)
    format = format or trinity.TRIFMT_A8R8G8B8
    while map.isLoading:
        blue.synchro.Yield()

    baseTexture = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, finalSize[0], finalSize[1], format, trinity.TRIMULTISAMPLE_NONE, 0, 1)
    t = TextureCompositor(baseTexture)
    t.Start()
    t.BlitTexture(map, map, 1.0, addAlpha=True, skipAlpha=False)
    t.End()
    tex = t.Finalize(format=format, w=finalSize[0], h=finalSize[1])
    return tex



def ExpandMap(map, finalSize):
    map = GetAsResource(map)
    while map.isLoading:
        blue.synchro.Yield()

    baseTexture = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, finalSize[0], finalSize[1], trinity.TRIFMT_A8R8G8B8, trinity.TRIMULTISAMPLE_NONE, 0, 1)
    mapWidth = int(1.0 / map.cutoutWidth * map.width)
    mapHeight = int(1.0 / map.cutoutHeight * map.height)
    mult = int(max(1.0, mapWidth / finalSize[0], mapHeight / finalSize[1]))
    t = TextureCompositor(baseTexture)
    t.Start()
    t.BlitTexture(map, map, 1.0, subrect=(0,
     0,
     mapWidth / mult,
     mapHeight / mult), addAlpha=True, skipAlpha=False)
    t.End()
    tex = t.Finalize(format=trinity.TRIFMT_A8R8G8B8, w=finalSize[0], h=finalSize[1])
    return tex



def ShowTestResult(baseTexture):
    ddsPath = 'c:\\temp\\test.dds'
    baseTexture.SaveTextureToFile(ddsPath)
    import TextureTools as nvtt
    import mayatools.TextureToolsPy as nvpy
    dds = nvtt.DirectDrawSurface(ddsPath)
    im = nvtt.Image()
    dds.mipmap(im, 0, 0)
    im.saveTGA('c:\\temp\\test.tga')
    nvpy.viewImage(im)



def Test():
    baseTexture = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, 1024, 1024, trinity.TRIFMT_A8R8G8B8, trinity.TRIMULTISAMPLE_NONE, 0, 1)
    t = TextureCompositor(baseTexture)
    t.Start()
    path = 'res:/Graphics/Character/Modular/Female/SkinTone/Black/Comp_Body_D.dds'
    nm = 'res:/Graphics/Character/Modular/Female/Outer/TrenchVictorianSkinned/Comp_Body_MM.dds'
    t.CopyBlitTexture(path)
    t.BlitTexture(nm, nm, 1.0, addAlpha=True, skipAlpha=True)
    tex = t.End(format=trinity.TRIFMT_A8R8G8B8, w=1024, h=1024)
    ShowTestResult(tex)



def Test2():
    baseTexture = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, 128, 128, trinity.TRIFMT_A8R8G8B8, trinity.TRIMULTISAMPLE_NONE, 0, 1)
    A = 'res:/TestCases/TextureAtlas/075_64.dds'
    B = 'res:/TestCases/TextureAtlas/009_64.dds'
    t = TextureCompositor(baseTexture)
    t.Start()
    t.CopyBlitTexture(A, None, (0.5, 0, 1, 0.5))
    t.BlitTexture(B, B, 1.0, addAlpha=True, skipAlpha=False, subrect=(0, 0, 64, 128))
    t.BlitTexture(B, B, 1.0, addAlpha=True, skipAlpha=False, subrect=(64, 0, 64, 128))
    tex = t.End(format=trinity.TRIFMT_A8R8G8B8, w=128, h=128)
    ShowTestResult(tex)



def Test3():
    B = 'res:/graphics/decals/CCP.dds'
    tex = ExpandMap(B, (2048, 1024))
    ShowTestResult(tex)



def Test4():
    baseTexture = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, 1024, 1024, trinity.TRIFMT_A8R8G8B8, trinity.TRIMULTISAMPLE_NONE, 0, 1)
    t = TextureCompositor(baseTexture)
    t.Start()
    A = 'res:/Graphics/Character/Modular/Female/SkinTone/Black/Comp_Body_D.dds'
    B = 'res:/graphics/decals/CCP.dds'
    B = ExpandMap(B, (1024, 1024))
    t.CopyBlitTexture(A)
    t.BlitTexture(B, B, 1.0, addAlpha=True, skipAlpha=True)
    tex = t.End(format=trinity.TRIFMT_A8R8G8B8, w=1024, h=1024)
    ShowTestResult(tex)



def Test5():
    B = 'res:/graphics/decals/CCP.dds'
    tex = Resize(B, (128, 128))
    ShowTestResult(tex)



def Test6():
    baseTexture = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, 1024, 1024, trinity.TRIFMT_A8R8G8B8, trinity.TRIMULTISAMPLE_NONE, 0, 1)
    t = TextureCompositor(baseTexture)
    t.Start()
    t.FillColor((0, 0, 1, 1))
    tex = t.End(format=trinity.TRIFMT_A8R8G8B8, w=1024, h=1024)
    ShowTestResult(tex)



def Test7():
    baseTexture = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, 1024, 512, trinity.TRIFMT_A8R8G8B8, trinity.TRIMULTISAMPLE_NONE, 0, 1)
    A = 'res:/Graphics/Character/Modular/Male/head/Caldari_Deteis/CD_Male_Body_D.tga'
    realPath = blue.rot.PathToFilename(A)
    print 'Real Path: ' + realPath
    B = 'res:/Graphics/Character/Modular/Male/Makeup/Eyebrows/Eyebrows_01/Colorize_Head_L.tga'
    bMask = 'res:/Graphics/Character/Modular/Male/Makeup/Eyebrows/Eyebrows_01/Colorize_Head_L.tga'
    o = 'res:/texture/global/stub.dds'
    t = TextureCompositor(baseTexture)
    t.Start()
    t.CopyBlitTexture(A, None)
    zone = 'res:/Graphics/Character/Modular/Male/Makeup/Eyebrows/Eyebrows_01/Colorize_Head_Z.tga'
    t.ColorizedBlitTexture(B, zone, o, (1, 1, 1, 1), (1, 1, 1, 1), (1, 1, 1, 1), skipAlpha=True, useAlphaTest=True)
    t.End()
    tex = t.Finalize(format=trinity.TRIFMT_A8R8G8B8, w=1024, h=512)
    tex.SaveTextureToFile('C:/temp/SpecMap.tga', trinity.TRIIFF_TGA)



def Test8():
    baseTexture = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, 1024, 1024, trinity.TRIFMT_A8R8G8B8, trinity.TRIMULTISAMPLE_NONE, 0, 1)
    A = 'R:\\Graphics\\Character\\Modular\\Female\\head\\Caldari_Deteis/CD_Female_Head_N.tga'
    B = 'R:\\Graphics\\Character\\Modular\\Female\\BodyShapes\\TwistMap/Female_Head_TN.tga'
    t = TextureCompositor(baseTexture)
    t.Start()
    t.CopyBlitTexture(A, None)
    t.TwistNormalBlitTexture(B, 1.0)
    t.End()
    tex = t.Finalize(format=trinity.TRIFMT_A8R8G8B8, w=1024, h=1024)
    tex.SaveTextureToFile('R:/twistedNormal.tga', trinity.TRIIFF_TGA)



def RunTest(s = ''):
    import uthread
    exec 'uthread.new( Test%s )' % s



