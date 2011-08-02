import trinity
import log
import paperDoll as pd
import blue
SOURCE_AREA_TYPE_OPAQUE = 0
SOURCE_AREA_TYPE_DECAL = 1
SHADOW_ALPHATEST_EFFECT_PATH = 'res:/Graphics/Effect/Managed/Interior/Avatar/ShadowAlphaTest.fx'
SHADOW_OPAQUE_EFFECT_PATH = 'res:/Graphics/Effect/Managed/Interior/Avatar/Shadow.fx'
SHADOW_CLOTH_ALPHATEST_EFFECT_PATH = 'res:/Graphics/Effect/Managed/Interior/Avatar/ShadowClothAlphaTest.fx'
SHADOW_CLOTH_OPAQUE_EFFECT_PATH = 'res:/Graphics/Effect/Managed/Interior/Avatar/ShadowCloth.fx'
COLLAPSED_SHADOW_EFFECT_PATH = 'res:/Graphics/Effect/Managed/Interior/Avatar/ShadowCollapsed.fx'
USE_DECAL_PLP_FOR_TRANSPARENT_AREAS = True
MATERIAL_ID_CONVERSION = {(0, 50, 1): 64,
 (0, 20, 11): 66,
 (0, 400, 11): 68,
 (0, 800, 11): 70,
 (5, 20, 11): 72,
 (5, 21, 11): 72,
 (10, 50, 1): 74,
 (10, 100, 1): 76,
 (10, 20, 11): 78,
 (10, 800, 11): 80,
 (11, 800, 11): 80,
 (20, 100, 1): 82,
 (10, 300, 11): 84,
 (13, 100, 1): 86}
MATERIAL_ID_EXACT = {0: 72,
 5: 72,
 10: 74,
 11: 74,
 13: 70}

def FindMaterialID(materialID, specPower1, specPower2):
    exact = MATERIAL_ID_EXACT.get(materialID, -1)
    if exact != -1:
        return exact
    specPower2 += 1
    for key in MATERIAL_ID_CONVERSION:
        if key == (materialID, specPower1, specPower2):
            return MATERIAL_ID_CONVERSION[key]

    log.LogWarn('PaperDollPrepassFixup: could not find a match for materialID = %s, specular power = (%s to %s)' % (materialID, specPower1, specPower2))
    best = None
    bestError = 10000
    for key in MATERIAL_ID_CONVERSION:
        if best is None or key[0] == materialID:
            error = abs(specPower1 - key[1]) + abs(specPower2 - key[1])
            if error < bestError:
                best = MATERIAL_ID_CONVERSION[key]
                bestError = error

    return best



def FindResourceByName(effect, resourceName):
    for res in effect.resources:
        if res.name == resourceName:
            return res




def FindParameterByName(effect, parameterName):
    for param in effect.parameters:
        if hasattr(param, 'name') and param.name == parameterName:
            return param




def CopyResource(res):
    if res is None:
        return 
    newRes = trinity.TriTexture2DParameter()
    newRes.name = res.name
    newRes.resourcePath = res.resourcePath
    if res.resourcePath == '' and res.resource is not None:
        newRes.SetResource(res.resource)
    return newRes



def CopyResources(sourceEffect, targetMaterial, resourceNames):
    if hasattr(sourceEffect, 'resources'):
        for res in sourceEffect.resources:
            if res.name not in resourceNames or type(res) != trinity.TriTexture2DParameter:
                continue
            newParameter = trinity.TriTexture2DParameter()
            newParameter.name = res.name
            newParameter.resourcePath = res.resourcePath
            if res.resourcePath == '' and res.resource is not None:
                newParameter.SetResource(res.resource)
            if type(targetMaterial) == trinity.Tr2Effect:
                targetMaterial.resources.append(newParameter)
            else:
                targetMaterial.parameters[res.name] = newParameter




def CopyParameters(sourceEffect, targetMaterial, parameterNames):
    if type(sourceEffect) != trinity.Tr2ShaderMaterial:
        for param in sourceEffect.parameters:
            if param.name not in parameterNames:
                continue
            newParameter = type(param)()
            newParameter.name = param.name
            newParameter.value = param.value
            if type(targetMaterial) == trinity.Tr2Effect:
                targetMaterial.parameters.append(newParameter)
            else:
                targetMaterial.parameters[param.name] = newParameter




def CopyAreaForPrePassShadows(area, sourceAreaType = SOURCE_AREA_TYPE_OPAQUE):
    originalEffect = area.effect
    if originalEffect is None or not hasattr(originalEffect, 'effectFilePath'):
        return 
    newArea = trinity.Tr2MeshArea()
    newArea.name = area.name
    newArea.index = area.index
    newArea.count = area.count
    newEffect = trinity.Tr2Effect()
    if originalEffect.effectFilePath.lower().find('avatar') == -1:
        if sourceAreaType == SOURCE_AREA_TYPE_DECAL and originalEffect.effectFilePath.lower().find('alphatest') == -1:
            return 
    elif originalEffect.effectFilePath.lower().find('cloth') == -1:
        if sourceAreaType == SOURCE_AREA_TYPE_DECAL:
            newEffect.effectFilePath = SHADOW_ALPHATEST_EFFECT_PATH
        else:
            newEffect.effectFilePath = SHADOW_OPAQUE_EFFECT_PATH
    elif sourceAreaType == SOURCE_AREA_TYPE_DECAL:
        newEffect.effectFilePath = SHADOW_CLOTH_ALPHATEST_EFFECT_PATH
    else:
        newEffect.effectFilePath = SHADOW_CLOTH_OPAQUE_EFFECT_PATH
    newEffect.name = originalEffect.name
    CopyResources(originalEffect, newEffect, set({'DiffuseMap', 'CutMaskMap'}))
    CopyParameters(originalEffect, newEffect, set({'TransformUV0',
     'MaterialDiffuseColor',
     'CutMaskInfluence',
     'ArrayOfCutMaskInfluence'}))
    newArea.effect = newEffect
    return newArea



def GetEffectParameter(effect, name, default):
    for p in effect.parameters:
        if p.name == name:
            return p

    return default



def CopyAreaForPrePassDepthNormal(area, sourceAreaType = SOURCE_AREA_TYPE_OPAQUE):
    originalEffect = area.effect
    if originalEffect is None:
        return 
    if hasattr(originalEffect, 'effectFilePath') and 'glass' in originalEffect.effectFilePath.lower():
        return 
    newArea = trinity.Tr2MeshArea()
    newArea.name = area.name
    newArea.index = area.index
    newArea.count = area.count
    newMaterial = trinity.Tr2ShaderMaterial()
    newMaterial.highLevelShaderName = 'NormalDepth'
    if sourceAreaType == SOURCE_AREA_TYPE_DECAL:
        newMaterial.name = 'Skinned_Cutout_NormalDepth'
        newMaterial.defaultSituation = 'AlphaCutout'
    else:
        newMaterial.name = 'Skinned_Opaque_NormalDepth'
        newMaterial.defaultSituation = ''
    if hasattr(originalEffect, 'effectFilePath') and 'double' in originalEffect.effectFilePath.lower():
        newMaterial.defaultSituation = newMaterial.defaultSituation + ' DoubleMaterial'
    if hasattr(originalEffect, 'name'):
        name = originalEffect.name.lower()
        if name.startswith('c_skin_'):
            newMaterial.defaultSituation = newMaterial.defaultSituation + ' SmoothNormal'
        elif name.startswith('c_eyes'):
            newMaterial.defaultSituation = newMaterial.defaultSituation + ' EyeShader'
    CopyResources(area.effect, newMaterial, set({'NormalMap',
     'SpecularMap',
     'DiffuseMap',
     'CutMaskMap'}))
    CopyParameters(area.effect, newMaterial, set({'TransformUV0',
     'MaterialDiffuseColor',
     'CutMaskInfluence',
     'ArrayOfCutMaskInfluence'}))
    MaterialLibraryID = FindParameterByName(area.effect, 'MaterialLibraryID')
    if MaterialLibraryID is None:
        MaterialLibraryID = 11
    else:
        MaterialLibraryID = MaterialLibraryID.x
    MaterialSpecularCurve = FindParameterByName(area.effect, 'MaterialSpecularCurve')
    if MaterialSpecularCurve is None:
        MaterialSpecularCurve = (0, 50, 0, 0)
    else:
        MaterialSpecularCurve = (MaterialSpecularCurve.x,
         MaterialSpecularCurve.y,
         MaterialSpecularCurve.z,
         MaterialSpecularCurve.w)
    param = trinity.Tr2FloatParameter()
    param.name = 'MaterialLibraryID'
    param.value = FindMaterialID(MaterialLibraryID, 1 + MaterialSpecularCurve[3], MaterialSpecularCurve[1])
    newMaterial.parameters['MaterialLibraryID'] = param
    MaterialLibraryID = FindParameterByName(area.effect, 'Material2LibraryID')
    if MaterialLibraryID is not None:
        param = trinity.Tr2FloatParameter()
        param.name = 'Material2LibraryID'
        param.value = FindMaterialID(MaterialLibraryID.x, 1 + MaterialSpecularCurve[3], MaterialSpecularCurve[1])
        newMaterial.parameters['Material2LibraryID'] = param
    newArea.effect = newMaterial
    return newArea



def CopyArea(area):
    newArea = area.CloneTo()
    if newArea.effect is not None:
        if type(newArea.effect) != trinity.Tr2ShaderMaterial:
            newArea.effect.effectFilePath = area.effect.effectFilePath
            newArea.effect.resources.removeAt(-1)
            for r in area.effect.resources:
                newRes = CopyResource(r)
                if newRes is not None:
                    newArea.effect.resources.append(newRes)

    return newArea



def CopyAreaOnly(area):
    newArea = trinity.Tr2MeshArea()
    newArea.name = area.name
    newArea.index = area.index
    newArea.count = area.count
    newArea.reversed = area.reversed
    return newArea



def CopyHairShader(fx):
    newMaterial = trinity.Tr2ShaderMaterial()
    lowPath = fx.effectFilePath.lower()
    newMaterial.highLevelShaderName = 'Hair'
    if 'detailed' in lowPath:
        newMaterial.defaultSituation = 'Detailed'
    if 'dxt5n' in lowPath:
        newMaterial.defaultSituation = newMaterial.defaultSituation + ' OPT_USE_DXT5N'
    CopyCommonAvatarMaterialParams(newMaterial, fx)
    CopyResources(fx, newMaterial, set({'TangentSampler'}))
    CopyParameters(fx, newMaterial, set({'HairParameters',
     'HairSpecularFactors1',
     'HairSpecularFactors2',
     'HairSpecularColor1',
     'HairSpecularColor2',
     'TangentMapParameters',
     'HairDiffuseBias'}))
    return newMaterial



def CopyAreaForPrePassHair(area):
    newArea = CopyArea(area)
    fx = newArea.effect
    if fx is not None and hasattr(fx, 'effectFilePath') and 'hair' in fx.effectFilePath.lower():
        newMaterial = CopyHairShader(fx)
        newArea.effect = newMaterial
        newArea.useSHLighting = True
    return newArea



def GetHighLevelShaderByName(name):
    sm = trinity.GetShaderManager()
    for shader in sm.shaderLibrary:
        if shader.name == name:
            return shader




def FindShaderMaterialParameter(mat, name):
    for param in mat.parameters:
        if param.name == name:
            return param

    logStr = name + ' target param not found in Tr2ShaderMaterial!'
    log.general.Log(logStr, log.LGERR)



def CopyCommonAvatarMaterialParams(mat, fx, meshName = None):
    CopyResources(fx, mat, set({'NormalMap',
     'SpecularMap',
     'DiffuseMap',
     'CutMaskMap',
     'FresnelLookupMap',
     'ColorNdotLLookupMap'}))
    CopyParameters(fx, mat, set({'MaterialDiffuseColor',
     'MaterialSpecularColor',
     'MaterialSpecularCurve',
     'MaterialSpecularFactors',
     'FresnelFactors',
     'MaterialLibraryID',
     'TransformUV0',
     'CutMaskInfluence'}))
    cmi = mat.parameters.get('CutMaskInfluence')
    if cmi and cmi.value >= 0.85:
        if meshName and 'drape' in meshName:
            cmi.value = 1.0
        else:
            cmi.value = 0.999
        print meshName,
        print cmi.value
    if 'MaterialDiffuseColor' not in mat.parameters:
        param = trinity.Tr2Vector4Parameter()
        param.name = 'MaterialDiffuseColor'
        param.value = (1, 1, 1, 1)
        mat.parameters['MaterialDiffuseColor'] = param



def ConvertEffectToTr2ShaderMaterial(fx, defaultSituation = None, meshName = None):
    if hasattr(fx, 'effectFilePath'):
        fxpath = fx.effectFilePath.lower()
        newMaterial = trinity.Tr2ShaderMaterial()
        if defaultSituation is not None:
            newMaterial.defaultSituation = defaultSituation
        if hasattr(fx, 'name'):
            name = fx.name.lower()
            if name.startswith('c_eyes'):
                newMaterial.defaultSituation = newMaterial.defaultSituation + ' EyeShader'
        if 'double' in fxpath:
            newMaterial.highLevelShaderName = 'SkinnedAvatarBRDFDouble'
            CopyCommonAvatarMaterialParams(newMaterial, fx, meshName)
            CopyParameters(fx, newMaterial, set({'Material2LibraryID',
             'Material2SpecularCurve',
             'Material2SpecularColor',
             'Material2SpecularFactors'}))
            if pd.IsSkin(fx):
                newMaterial.defaultSituation = newMaterial.defaultSituation + ' Skin'
            return newMaterial
        if 'skinnedavatarbrdf' in fxpath:
            newMaterial.highLevelShaderName = 'SkinnedAvatarBrdf'
            CopyCommonAvatarMaterialParams(newMaterial, fx, meshName)
            if pd.IsSkin(fx):
                newMaterial.defaultSituation = newMaterial.defaultSituation + ' Skin'
            return newMaterial
        if 'skinnedavatar' in fxpath:
            newMaterial.highLevelShaderName = 'SkinnedAvatar'
            CopyCommonAvatarMaterialParams(newMaterial, fx, meshName)
            return newMaterial
        if 'clothavatar' in fxpath:
            newMaterial.highLevelShaderName = 'ClothAvatar'
            CopyCommonAvatarMaterialParams(newMaterial, fx, meshName)
            return newMaterial
    return fx



def AddDepthNormalAreasToStandardMesh(mesh):
    mesh.depthNormalAreas.removeAt(-1)
    for area in mesh.opaqueAreas:
        newArea = CopyAreaForPrePassDepthNormal(area, SOURCE_AREA_TYPE_OPAQUE)
        if newArea is not None:
            mesh.depthNormalAreas.append(newArea)
            newArea.effect.parameters['TransformUV0'].value = (0, 0, 1, 1)




def AddPrepassAreasToStandardMesh(mesh, processDepthAreas, processDepthNormalAreas):
    opaqueAreas = mesh.opaqueAreas
    if processDepthAreas:
        mesh.depthAreas.removeAt(-1)
    if processDepthNormalAreas:
        mesh.depthNormalAreas.removeAt(-1)
    mesh.decalPrepassAreas.removeAt(-1)
    mesh.opaquePrepassAreas.removeAt(-1)
    for area in mesh.transparentAreas:
        if area.name[0:6] == 'Prepass_':
            mesh.transparentAreas.remove(area)

    for area in opaqueAreas:
        if area.effect is not None and hasattr(area.effect, 'effectFilePath') and 'glass' in area.effect.effectFilePath.lower():
            newArea = CopyArea(area)
            if newArea is not None:
                newArea.name = 'Prepass_' + newArea.name
                mesh.transparentAreas.append(newArea)
            continue
        if processDepthNormalAreas:
            newArea = CopyAreaForPrePassDepthNormal(area, SOURCE_AREA_TYPE_OPAQUE)
            if newArea is not None:
                mesh.depthNormalAreas.append(newArea)
        if processDepthAreas:
            newArea = CopyAreaForPrePassShadows(area, SOURCE_AREA_TYPE_OPAQUE)
            if newArea is not None:
                mesh.depthAreas.append(newArea)
        newArea = CopyAreaOnly(area)
        if newArea is not None:
            newArea.effect = ConvertEffectToTr2ShaderMaterial(area.effect, 'Prepass', mesh.name)
            mesh.opaquePrepassAreas.append(newArea)

    newAreas = []

    def AddAreasForRegularPLP(area):
        if area.effect is not None and hasattr(area.effect, 'effectFilePath') and 'glass' in area.effect.effectFilePath.lower():
            newArea = CopyArea(area)
            if newArea is not None:
                newArea.name = 'Prepass_' + newArea.name
                newAreas.append(newArea)
            return 
        if processDepthNormalAreas:
            newArea = CopyAreaForPrePassDepthNormal(area, SOURCE_AREA_TYPE_DECAL)
            if newArea is not None:
                mesh.depthNormalAreas.append(newArea)
        if processDepthAreas:
            newArea = CopyAreaForPrePassShadows(area, SOURCE_AREA_TYPE_DECAL)
            if newArea is not None:
                mesh.depthAreas.append(newArea)
        newArea = CopyAreaOnly(area)
        if newArea is not None:
            newArea.effect = ConvertEffectToTr2ShaderMaterial(area.effect, 'Prepass Decal', mesh.name)
            mesh.decalPrepassAreas.append(newArea)


    for area in mesh.decalAreas:
        AddAreasForRegularPLP(area)


    def IsEyeRelated(areaMesh):
        if areaMesh.effect is None or not hasattr(areaMesh.effect, 'name'):
            return False
        low = areaMesh.effect.name.lower()
        return low.startswith('c_eyes') or low.startswith('c_eyewetness') or 'eyelashes' in low


    for area in mesh.transparentAreas:
        if area.effect is None:
            continue
        if hasattr(area.effect, 'effectFilePath') and 'glassshader.fx' in area.effect.effectFilePath.lower():
            area.effect.effectFilePath = area.effect.effectFilePath[:-3] + 'cellcube.fx'
            continue
        if hasattr(area.effect, 'effectFilePath') and 'glass' in area.effect.effectFilePath.lower():
            continue
        if USE_DECAL_PLP_FOR_TRANSPARENT_AREAS and not IsEyeRelated(area):
            AddAreasForRegularPLP(area)
            area.effect = None
        else:
            newArea = CopyAreaOnly(area)
            if newArea is not None:
                if 'C_SkinShiny' in area.effect.name:
                    newArea.effect = ConvertEffectToTr2ShaderMaterial(area.effect, 'Prepass Decal', mesh.name)
                    mesh.decalPrepassAreas.append(newArea)
                else:
                    newArea.effect = ConvertEffectToTr2ShaderMaterial(area.effect, 'SHLighting', mesh.name)
                    newArea.useSHLighting = True
                    newAreas.append(newArea)
                area.debugIsHidden = True

    mesh.transparentAreas.extend(newAreas)



def AddPrepassAreasToHair(mesh, processDepthAreas, processDepthNormalAreas):
    if processDepthAreas:
        mesh.depthAreas.removeAt(-1)
    if processDepthNormalAreas:
        mesh.depthNormalAreas.removeAt(-1)
    mesh.decalPrepassAreas.removeAt(-1)
    mesh.opaquePrepassAreas.removeAt(-1)
    if processDepthAreas:
        for area in mesh.decalAreas:
            newArea = CopyAreaForPrePassShadows(area, SOURCE_AREA_TYPE_DECAL)
            if newArea is not None:
                mesh.depthAreas.append(newArea)

    for area in mesh.transparentAreas:
        if area.name[0:6] == 'Decal_':
            mesh.transparentAreas.remove(area)

    newAreas = []
    for area in mesh.transparentAreas:
        newArea = CopyAreaForPrePassHair(area)
        newArea.name = 'Decal_' + newArea.name
        if newArea is not None:
            newAreas.append(newArea)
        area.debugIsHidden = True

    mesh.transparentAreas.extend(newAreas)
    for area in mesh.decalAreas:
        newArea = CopyAreaForPrePassHair(area)
        newArea.name = 'Decal_' + newArea.name
        if newArea is not None:
            mesh.transparentAreas.append(newArea)
        area.debugIsHidden = True




def AddPrepassAreasToAvatar(avatar, visualModel, doll, clothSimulationActive = True):
    createShadows = doll.overrideLod <= pd.PerformanceOptions.shadowLod
    collapseShadowMesh = pd.PerformanceOptions.collapseShadowMesh and doll.overrideLod >= 0 and createShadows
    collapseMainMesh = pd.PerformanceOptions.collapseMainMesh and doll.overrideLod == 2
    collapsePLPMesh = pd.PerformanceOptions.collapsePLPMesh and doll.overrideLod >= 0
    if collapseMainMesh:
        collapsePLPMesh = False
    plpMeshes = []
    if collapseShadowMesh or collapseMainMesh or collapsePLPMesh:

        def FindSkinEffect(meshes):
            for mesh in iter(meshes):
                fx = pd.GetEffectsFromMesh(mesh)
                for effect in iter(fx):
                    if effect.name.lower().startswith('c_skin_'):
                        return effect




        sourceEffect = FindSkinEffect(visualModel.meshes)
        shadowEffect = None
        if sourceEffect:
            shadowEffect = pd.SkinLightmapRenderer.DuplicateEffect(sourceEffect, COLLAPSED_SHADOW_EFFECT_PATH)
        else:
            createShadows = False
        mods = doll.buildDataManager.GetSortedModifiers()
        file = blue.ResFile()
        UV = {}

        def FindTransformUV(meshes):
            for mesh in meshes:
                for areas in (mesh.opaqueAreas, mesh.decalAreas, mesh.transparentAreas):
                    for area in areas:
                        for p in area.effect.parameters:
                            if p.name == 'TransformUV0':
                                return p.value




            return (0, 0, 1, 1)


        for mod in mods:
            if mod.redfile is None or mod.redfile is '':
                continue
            UV[mod.redfile] = FindTransformUV(mod.meshes)

        if collapseMainMesh:
            del visualModel.meshes[:]
        savedUV = {}
        for param in sourceEffect.parameters:
            if param.name == 'TransformUV0':
                savedUV[param.name] = param.value
                param.value = (0, 0, 1, 1)
                break

        if shadowEffect:
            for param in shadowEffect.parameters:
                if param.name == 'TransformUV0':
                    param.value = (0, 0, 1, 1)
                    break

        builder = trinity.Tr2SkinnedModelBuilder()
        builder.createGPUMesh = True
        builder.removeReversed = True
        builder.collapseToOpaque = True
        builder.enableSubsetBuilding = True
        builder.effectPath = COLLAPSED_SHADOW_EFFECT_PATH
        builder.SetAdjustPathMethod(lambda path: doll.AdjustGr2PathForLod(path))
        builder.enableVertexChopping = False
        builder.enableVertexPadding = False
        blends = {}
        for mod in mods:
            if mod.categorie in pd.BLENDSHAPE_CATEGORIES and mod.weight > 0:
                blends[mod.name] = mod.weight
            red = mod.redfile
            if red is None or red is '':
                continue
            if 'ragdoll' in red.lower():
                continue
            peek = doll.AdjustRedFileForLod(red)
            if file.FileExists(peek):
                red = peek
            source = trinity.Tr2SkinnedModelBuilderSource()
            source.moduleResPath = red
            uv = UV.get(mod.redfile, (0, 0, 1, 1))
            source.upperLeftTexCoord = (uv[0], uv[1])
            source.lowerRightTexCoord = (uv[2], uv[3])
            builder.sourceMeshesInfo.append(source)

        for (name, weight,) in blends.iteritems():
            if weight > 0.0:
                blend = trinity.Tr2SkinnedModelBuilderBlend()
                blend.name = name
                blend.power = weight
                builder.blendshapeInfo.append(blend)

        if not builder.PrepareForBuild():
            collapseShadowMesh = False
            collapseMainMesh = False
            collapsePLPMesh = False
        else:
            buildCount = 0
            while builder.Build():
                buildCount += 1

            if pd.PerformanceOptions.collapseVerbose:
                if buildCount > 1 and doll.overrideLod == 2:
                    log.LogWarn('PD Collapse: lod2 has ' + str(buildCount) + ' meshes after collapse (expected 1).')
                if buildCount > 3 and doll.overrideLod == 0:
                    log.LogWarn('PD Collapse: lod0 has ' + str(buildCount) + ' meshes after collapse (expected 3 at most).')
            model = builder.GetSkinnedModel()

            def TransferArrayOf(destEffect, sourceEffect):
                for p in sourceEffect.parameters:
                    if p.name.startswith('ArrayOf'):
                        for q in destEffect.parameters:
                            if p.name == q.name:
                                destEffect.parameters.remove(q)
                                break

                        destEffect.parameters.append(p)



            for (count, mesh,) in enumerate(model.meshes):
                mesh.name = 'collapsed' + str(buildCount) + str(count)
                if collapseMainMesh or collapsePLPMesh:
                    for area in iter(mesh.opaqueAreas):
                        if createShadows:
                            newArea = trinity.Tr2MeshArea()
                            newArea.index = area.index
                            newArea.count = area.count
                            newArea.effect = shadowEffect
                            TransferArrayOf(shadowEffect, area.effect)
                            mesh.depthAreas.append(newArea)
                        TransferArrayOf(sourceEffect, area.effect)
                        area.effect = sourceEffect

                    if collapsePLPMesh:
                        plpMeshes.append(mesh)
                elif createShadows:
                    pd.MoveAreas(mesh.opaqueAreas, mesh.depthAreas)
                    for area in mesh.depthAreas:
                        TransferArrayOf(shadowEffect, area.effect)
                        area.effect = shadowEffect

                visualModel.meshes.append(mesh)

        if not collapseMainMesh:
            for param in sourceEffect.parameters:
                if param.name == 'TransformUV0':
                    param.value = savedUV[param.name]

        visualModel.ResetAnimationBindings()
    for mesh in visualModel.meshes:
        if mesh in plpMeshes:
            continue
        if mesh.name[0:4] == 'hair':
            AddPrepassAreasToHair(mesh, processDepthAreas=createShadows and not collapseShadowMesh, processDepthNormalAreas=not collapsePLPMesh)
        else:
            AddPrepassAreasToStandardMesh(mesh, processDepthAreas=createShadows and not collapseShadowMesh, processDepthNormalAreas=not collapsePLPMesh)

    for mesh in plpMeshes:
        AddDepthNormalAreasToStandardMesh(mesh)
        mesh.opaqueAreas.removeAt(-1)

    if doll.overrideLod == 2:
        for mesh in visualModel.meshes:
            for dn in mesh.depthNormalAreas:
                dn.effect.defaultSituation = dn.effect.defaultSituation + ' OPT_USE_OBJECT_NORMAL'


    if collapseMainMesh or collapsePLPMesh:
        for mesh in visualModel.meshes:
            for dn in mesh.depthNormalAreas:
                dn.effect.defaultSituation = dn.effect.defaultSituation + ' OPT_COLLAPSED_PLP'


    if doll.useDXT5N:
        for mesh in visualModel.meshes:
            for areas in pd.MeshAreaListIterator(mesh, includePLP=True):
                for area in areas:
                    if hasattr(area.effect, 'defaultSituation'):
                        area.effect.defaultSituation = area.effect.defaultSituation + ' OPT_USE_DXT5N'



    if clothSimulationActive:
        for mesh in avatar.clothMeshes:
            if mesh.effect and mesh.effect.name:
                mesh.depthEffect = None
                newEffect = trinity.Tr2ShaderMaterial()
                newEffect.highLevelShaderName = 'Shadow'
                newEffect.defaultSituation = 'Cloth'
                CopyResources(mesh.effect, newEffect, set({'DiffuseMap', 'CutMaskMap'}))
                CopyParameters(mesh.effect, newEffect, set({'TransformUV0', 'MaterialDiffuseColor', 'CutMaskInfluence'}))
                mesh.depthEffect = newEffect
                mesh.depthNormalEffect = None
                isTr2Effect = hasattr(mesh.effect, 'effectFilePath')
                effectIsHairEffect = False
                if isTr2Effect:
                    effectIsHairEffect = mesh.effect.effectFilePath.lower().find('hair') != -1
                if isTr2Effect and not effectIsHairEffect:
                    newEffect = trinity.Tr2ShaderMaterial()
                    newEffect.highLevelShaderName = 'NormalDepth'
                    newEffect.defaultSituation = 'Cloth'
                    if doll.useDXT5N:
                        newEffect.defaultSituation = newEffect.defaultSituation + ' OPT_USE_DXT5N'
                    CopyResources(mesh.effect, newEffect, set({'NormalMap',
                     'SpecularMap',
                     'DiffuseMap',
                     'CutMaskMap'}))
                    CopyParameters(mesh.effect, newEffect, set({'TransformUV0',
                     'MaterialSpecularCurve',
                     'MaterialLibraryID',
                     'MaterialDiffuseColor',
                     'CutMaskInfluence'}))
                    mesh.depthNormalEffect = newEffect
                if isTr2Effect:
                    reversedIsTr2Effect = hasattr(mesh.effectReversed, 'effectFilePath')
                    reversedEffectIsHair = False
                    if reversedIsTr2Effect:
                        reversedEffectIsHair = mesh.effectReversed.effectFilePath.lower().find('hair') != -1
                    if effectIsHairEffect:
                        newMaterial = CopyHairShader(mesh.effect)
                        newMaterial.name = mesh.effect.name
                        newMaterial.defaultSituation = newMaterial.defaultSituation + ' Cloth'
                        if doll.useDXT5N:
                            newMaterial.defaultSituation = newMaterial.defaultSituation + ' OPT_USE_DXT5N'
                        mesh.effect = newMaterial
                        mesh.useTransparentBatches = True
                        mesh.useSHLighting = True
                        if reversedIsTr2Effect and reversedEffectIsHair:
                            newMaterial = CopyHairShader(mesh.effectReversed)
                            newMaterial.name = mesh.effectReversed.name
                            newMaterial.defaultSituation = newMaterial.defaultSituation + ' Cloth'
                            if doll.useDXT5N:
                                newMaterial.defaultSituation = newMaterial.defaultSituation + ' OPT_USE_DXT5N'
                            mesh.effectReversed = newMaterial
                            mesh.useTransparentBatches = True
                            mesh.useSHLighting = True
                    else:
                        situation = 'Prepass Cloth'
                        if doll.useDXT5N:
                            situation = situation + ' OPT_USE_DXT5N'
                        newMaterial = ConvertEffectToTr2ShaderMaterial(mesh.effect, situation, mesh.name)
                        newMaterial.name = mesh.effect.name
                        mesh.effect = newMaterial
                        if reversedIsTr2Effect and not reversedEffectIsHair:
                            newMaterial = ConvertEffectToTr2ShaderMaterial(mesh.effectReversed, situation, mesh.name)
                            newMaterial.name = mesh.effectReversed.name
                            mesh.effectReversed = newMaterial

    avatar.BindLowLevelShaders()


exports = {'paperDoll.prePassFixup.AddPrepassAreasToAvatar': AddPrepassAreasToAvatar}

