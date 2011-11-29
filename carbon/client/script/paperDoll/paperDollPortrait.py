import os
import geo2
import trinity
import blue
import yaml
import math
import bluepy
import geo2
import paperDoll as PD

def ApplySuffix(basePath, suffix):
    path = '{0}{1}'.format(basePath, suffix)
    return path



class PortraitTools(object):
    __metaclass__ = bluepy.CCP_STATS_ZONE_PER_METHOD
    __guid__ = 'paperDoll.PortraitTools'

    @staticmethod
    def BindHeroShader(effect, isOptimized, suffix):
        if not isOptimized:
            effect.effectFilePath = 'res:/Graphics/Effect/Managed/Interior/Avatar/skinnedavatarbrdf_detailed' + suffix
        else:
            effect.effectFilePath = 'res:/Graphics/Effect/Managed/Interior/Avatar/avatarbrdfcombined_detailed' + suffix
        while effect.effectResource.isLoading:
            PD.Yield()

        effect.PopulateParameters()
        for res in effect.resources:
            if res.name == 'NormalDetailMap':
                res.resourcePath = 'res:/Texture/Global/NormalNoise_N.dds'
                break

        for par in effect.parameters:
            if par.name == 'NormalDetailStrength':
                par.value = 0.25
            if par.name == 'NormalDetailTiling':
                par.value = 50.0




    def SetupWrinkleMapControls(self, avatar, effects, pdDoll):
        if avatar is None:
            return 
        set = trinity.TriCurveSet()
        set.name = 'Wrinkles'
        for s in avatar.curveSets:
            if s.name == 'Wrinkles':
                for bind in s.bindings:
                    if hasattr(bind, 'copyValueCallable'):
                        bind.copyValueCallable = None

                avatar.curveSets.remove(s)
                break

        avatar.curveSets.append(set)
        weakAvatar = blue.BluePythonWeakRef(avatar)
        pdDoll.LoadBindPose()

        def CreateBoneDriver(set, bone1, bone2, zone, min, max, oldMin, oldMax, curveDictionary, name, tweakData):
            if bone1 in pdDoll.bindPose and bone1 in pdDoll.boneOffsets and bone2 in pdDoll.bindPose and bone2 in pdDoll.boneOffsets:
                bindPosePos1 = pdDoll.bindPose[bone1]['translation']
                offset1 = pdDoll.boneOffsets[bone1]['translation']
                bindPosePos2 = pdDoll.bindPose[bone2]['translation']
                offset2 = pdDoll.boneOffsets[bone2]['translation']
                realPos1 = (bindPosePos1[0] / 100.0 + offset1[0], bindPosePos1[1] / 100.0 + offset1[1], bindPosePos1[2] / 100.0 + offset1[2])
                realPos2 = (bindPosePos2[0] / 100.0 + offset2[0], bindPosePos2[1] / 100.0 + offset2[1], bindPosePos2[2] / 100.0 + offset2[2])
                bindPoseDist = geo2.Vec3Distance(bindPosePos1, bindPosePos2) / 100.0
                dist = geo2.Vec3Distance(realPos1, realPos2)
                multiplier = dist / bindPoseDist
                oldMin = oldMin * multiplier
                oldMax = oldMax * multiplier

            def GetOrMakeCurve(bone, set, curveDictionary, name):
                curve = curveDictionary.get((weakAvatar, bone), None)
                if curve is not None:
                    return curve
                curve = trinity.Tr2BoneMatrixCurve()
                curve.bone = bone
                curve.name = name
                curveDictionary[(weakAvatar, bone)] = curve
                set.curves.append(curve)
                return curve


            curve1 = GetOrMakeCurve(bone1, set, curveDictionary, 'bone1')
            curve2 = GetOrMakeCurve(bone2, set, curveDictionary, 'bone2')
            bind = trinity.TriValueBinding()
            set.bindings.append(bind)

            def distanceBinding(curve1, curve2, min, max, parameters, index, gamma):
                avatar = weakAvatar.object
                if avatar is None:
                    return 
                curve1.skinnedObject = avatar
                curve2.skinnedObject = avatar
                if curve1.startValue == curve1.currentValue or curve2.startValue == curve2.currentValue:
                    curve1.skinnedObject = None
                    curve2.skinnedObject = None
                    return 
                p1 = curve1.currentValue[3]
                p2 = curve2.currentValue[3]
                dist = geo2.Vec3Distance(p1, p2)
                d = 1.0 - (dist - min) * 1 / (max - min)
                if d < 0:
                    d = 0
                elif d > 1:
                    d = 1
                if gamma != 1.0:
                    d = math.pow(d, gamma)
                if False:
                    trinity.GetDebugRenderer().DrawLine((p1[0], p1[1], p1[2]), 4294967295L, (p2[0], p2[1], p2[2]), 4294967295L)
                    trinity.GetDebugRenderer().Print3D((p1[0], p1[1], p1[2]), 4294967295L, str(dist))
                    trinity.GetDebugRenderer().Print3D((p2[0], p2[1], p2[2]), 4294967295L, str(d))
                for p_ in parameters:
                    p = p_.object
                    if p is None:
                        continue
                    if index == 1:
                        p.v1 = d
                    if index == 2:
                        p.v2 = d
                    if index == 3:
                        p.v3 = d
                    if index == 4:
                        p.v4 = d

                curve1.skinnedObject = None
                curve2.skinnedObject = None


            zone = zone - 1
            paramIndex = zone / 4 + 1
            index = zone % 4 + 1
            param = 'WrinkleNormalStrength' + str(paramIndex)
            parameters = []
            for fx in effects:
                for p in fx.parameters:
                    if p.name == param:
                        parameters.append(blue.BluePythonWeakRef(p))


            gammaCurves = tweakData.get('gammaCurves', {})
            gamma = gammaCurves.get(name, gammaCurves.get('default', 1.0))
            bind.copyValueCallable = lambda source, dest: distanceBinding(curve1, curve2, oldMin, oldMax, parameters, index, gamma)



        def CreateAxisDriver(set, jointName, zone, axis, maxValue, name, tweakData, pdDoll):
            avatar = weakAvatar.object
            if avatar is None or not hasattr(avatar, 'animationUpdater') or avatar.animationUpdater is None or not hasattr(avatar.animationUpdater, 'network') or avatar.animationUpdater.network is None:
                return 
            bind = trinity.TriValueBinding()
            set.bindings.append(bind)
            if not hasattr(avatar.animationUpdater, 'network'):
                return 
            jointIndex = avatar.animationUpdater.network.GetBoneIndex(jointName)
            if jointIndex == -1:
                print "Error: Can't find bone for axis control: " + jointName
                return 
            if not type(jointIndex) == type(1):
                print 'Non-int returned for bone in axis: ' + str(jointIndex) + ', name:' + jointName
                return 
            bindPosePos = pdDoll.bindPose[jointName]
            if jointName in pdDoll.boneOffsets:
                offset = pdDoll.boneOffsets[jointName]
            else:
                offset = {'translation': [0, 0, 0]}
            startPos = [0,
             0,
             0,
             0,
             0,
             0,
             0,
             0,
             0,
             (bindPosePos['translation'][0] + offset['translation'][0]) / 100.0,
             (bindPosePos['translation'][1] + offset['translation'][1]) / 100.0,
             (bindPosePos['translation'][2] + offset['translation'][2]) / 100.0]

            def AxisBinding(startPos, jointIndex, axis, maxValue, parameters, index, gamma):
                avatar = weakAvatar.object
                if avatar is None:
                    return 
                if not hasattr(avatar.animationUpdater, 'network') or avatar.animationUpdater.network is None:
                    return 
                newPos = avatar.animationUpdater.network.GetRawTrackData(jointIndex)
                diff = (newPos[9] - startPos[9], newPos[10] - startPos[10], newPos[11] - startPos[11])
                value = 0
                if axis == 'x':
                    value = diff[0]
                elif axis == 'y':
                    value = diff[1]
                elif axis == 'z':
                    value = diff[2]
                finalValue = 0
                max = maxValue
                if max < 0:
                    max = -max
                    value = -value
                if value > max:
                    finalValue = 1.0
                elif value < 0:
                    finalValue = 0.0
                else:
                    finalValue = value / max
                if gamma != 1.0:
                    finalValue = math.pow(finalValue, gamma)
                for p_ in parameters:
                    p = p_.object
                    if p is None:
                        continue
                    if index == 1:
                        p.v1 = finalValue
                    if index == 2:
                        p.v2 = finalValue
                    if index == 3:
                        p.v3 = finalValue
                    if index == 4:
                        p.v4 = finalValue



            zone = zone - 1
            paramIndex = zone / 4 + 1
            index = zone % 4 + 1
            param = 'WrinkleNormalStrength' + str(paramIndex)
            parameters = []
            for fx in effects:
                for p in fx.parameters:
                    if p.name == param:
                        parameters.append(blue.BluePythonWeakRef(p))


            gammaCurves = tweakData.get('gammaCurves', {})
            gamma = gammaCurves.get(name, gammaCurves.get('default', 1.0))
            bind.name = 'AxisBind'
            bind.copyValueCallable = lambda source, dest: AxisBinding(startPos, jointIndex, axis, maxValue, parameters, index, gamma)


        rootFolder = 'R:/'
        if not blue.rot.loadFromContent:
            rootFolder = 'res:/'
        faceSetupPath = rootFolder + 'Graphics/Character/Global/FaceSetup/BasicFace.face'
        if pdDoll.gender != PD.GENDER.FEMALE:
            faceSetupPath = rootFolder + 'Graphics/Character/Global/FaceSetup/BasicFaceMale.face'
        file = blue.ResFile()
        if not file.FileExists(faceSetupPath):
            return 
        file.open(faceSetupPath)
        data = yaml.load(file, Loader=yaml.CLoader)
        file.close()
        faceTweaksPath = rootFolder + 'Graphics/Character/Global/FaceSetup/FaceTweakSettings.yaml'
        file = blue.ResFile()
        file.open(faceTweaksPath)
        tweakData = yaml.load(file, Loader=yaml.CLoader)
        file.close()
        curveDictionary = {}
        if data:
            for d in data:
                entry = data[d]
                if len(entry) == 7:
                    CreateBoneDriver(set, entry[0], entry[1], entry[2], entry[3] / 100.0, entry[4] / 100.0, entry[5] / 100.0, entry[6] / 100.0, curveDictionary, d, tweakData)
                elif len(entry) == 4:
                    CreateAxisDriver(set, entry[0], entry[1], entry[2], entry[3] / 100.0, d, tweakData, pdDoll)

        wrinkleMultiplier = tweakData.get('wrinkleMultiplier', 1.0)
        correctionMultiplier = tweakData.get('correctionMultiplier', 1.0)
        for fx in effects:
            for p in fx.parameters:
                if p.name == 'WrinkleParams':
                    p.value = (wrinkleMultiplier,
                     correctionMultiplier,
                     0.0,
                     0.0)


        set.Play()
        return set



    @staticmethod
    def BindLinearAvatarBRDF(effect, suffix):
        path = effect.effectFilePath.lower()
        pathSansSuffix = path[:path.rfind('.')]
        if pathSansSuffix.endswith('skinnedavatarbrdf') or pathSansSuffix.endswith('skinnedavatarbrdfdouble') or pathSansSuffix.endswith('clothavatar'):
            effect.effectFilePath = ApplySuffix(pathSansSuffix + 'linear', suffix)
        elif pathSansSuffix.endswith('skinnedavatarbrdflinear') or pathSansSuffix.endswith('skinnedavatarbrdfdoublelinear') or pathSansSuffix.endswith('clothavatarlinear'):
            effect.effectFilePath = ApplySuffix(pathSansSuffix, suffix)



    @staticmethod
    def TweakDiffuseSampler(effect):
        for r in effect.resources:
            if r.name == 'DiffuseMap':
                r.Srgb = True
                r.maxAnisotropy = 16
                r.addressUMode = 3
                r.addressVMode = 3
                r.useAllOverrides = True
                return 




    @staticmethod
    def BindSkinShader(effect, wrinkleFx, scattering, buildDataManager, gender, use_png, fxSuffix):
        name = effect.name.lower()
        path = effect.effectFilePath.lower()
        if name.startswith('c_skin'):
            wasDouble = 'double' in path
            fxPath = PD.SKINNED_AVATAR_SINGLEPASS_DOUBLE_PATH if wasDouble else PD.SKINNED_AVATAR_SINGLEPASS_SINGLE_PATH
            effect.effectFilePath = ApplySuffix(fxPath[:-3], fxSuffix)
            while effect.effectResource.isLoading:
                PD.Yield()

            effect.PopulateParameters()
            PD.SetOrAddMap(effect, 'BeckmannLookup', 'res:/Texture/Global/beckmannSpecular.dds')
            PortraitTools.TweakDiffuseSampler(effect)
            suffix = 'tga'
            if use_png and not blue.rot.loadFromContent:
                suffix = 'png'
            headMods = buildDataManager.GetModifiersByCategory(PD.DOLL_PARTS.HEAD)
            if PD.GENDER_ROOT:
                if gender == PD.GENDER.FEMALE:
                    headFolderGeneric = 'res:/Graphics/Character/Female/Paperdoll/head/Head_Generic'
                else:
                    headFolderGeneric = 'res:/Graphics/Character/Male/Paperdoll/head/Head_Generic'
            elif gender == PD.GENDER.FEMALE:
                headFolderGeneric = 'res:/Graphics/Character/Modular/Female/head/Head_Generic'
            else:
                headFolderGeneric = 'res:/Graphics/Character/Modular/Male/head/Head_Generic'
            headFolder = headFolderGeneric
            for hm in headMods:
                headFolder = os.path.dirname(hm.redfile)

            resFile = blue.ResFile()
            if scattering:
                if headFolder != '' and resFile.FileExists(headFolder + '/SkinMap.' + suffix):
                    PD.SetOrAddMap(effect, 'SkinMap', headFolder + '/SkinMap.' + suffix)
                else:
                    PD.SetOrAddMap(effect, 'SkinMap', headFolderGeneric + '/SkinMap.' + suffix)
            if wrinkleFx is not None:
                PD.SetOrAddMap(effect, 'WrinkleZoneMap', PD.FEMALE_WRINKLE_FACEZONE_PREFIX + suffix)
                if headFolder != '' and resFile.FileExists(headFolder + '/WrinkleNormal.' + suffix):
                    PD.SetOrAddMap(effect, 'WrinkleNormalMap', headFolder + '/WrinkleNormal.' + suffix)
                else:
                    PD.SetOrAddMap(effect, 'WrinkleNormalMap', headFolderGeneric + '/WrinkleNormal.' + suffix)
                if headFolder != '' and resFile.FileExists(headFolder + '/WrinkleNormalCorrection.' + suffix):
                    PD.SetOrAddMap(effect, 'WrinkleNormalCorrectionMap', headFolder + '/WrinkleNormalCorrection.' + suffix)
                else:
                    PD.SetOrAddMap(effect, 'WrinkleNormalCorrectionMap', headFolderGeneric + '/WrinkleNormalCorrection.' + suffix)
                if headFolder != '' and resFile.FileExists(headFolder + '/WrinkleDiffuse.' + suffix):
                    PD.SetOrAddMap(effect, 'WrinkleDiffuseMap', headFolder + '/WrinkleDiffuse.' + suffix)
                else:
                    PD.SetOrAddMap(effect, 'WrinkleDiffuseMap', headFolderGeneric + '/WrinkleDiffuse.' + suffix)
                wrinkleFx.append(effect)
        elif name.startswith('c_standard'):

            def AddClothingCube(effect):
                for res in effect.resources:
                    if res.name == 'ClothingReflectionCube':
                        return 

                res = trinity.TriTextureCubeParameter()
                res.name = 'ClothingReflectionCube'
                res.resourcePath = 'res:/Texture/Global/GenericReflection_cube.dds'
                effect.resources.append(res)


            AddClothingCube(effect)
        elif name.startswith('c_eyewetness'):
            effect.effectFilePath = ApplySuffix(PD.SKINNED_AVATAR_EYEWETNESS_SHADER[:-3], fxSuffix)
        elif name.startswith('c_tongue'):
            effect.effectFilePath = ApplySuffix(PD.SKINNED_AVATAR_TONGUE_SHADER[:-3], fxSuffix)
        elif name.startswith('c_teeth'):
            effect.effectFilePath = ApplySuffix(PD.SKINNED_AVATAR_TEETH_SHADER[:-3], fxSuffix)
        elif name.startswith('c_eyes'):
            effect.effectFilePath = ApplySuffix(PD.SKINNED_AVATAR_EYE_SHADER[:-3], fxSuffix)

            def AddEyeCube(effect):
                for res in effect.resources:
                    if res.name == 'EyeReflectionCube':
                        return 

                res = trinity.TriTextureCubeParameter()
                res.name = 'EyeReflectionCube'
                res.resourcePath = PD.EYE_SHADER_REFLECTION_CUBE_PATH
                effect.resources.append(res)


            AddEyeCube(effect)



    def BindCustomShaders(effect, useFastShaders, doll):
        path = effect.effectFilePath.lower()
        name = effect.name.lower()
        if 'glassshader' in path:
            for res in effect.resources:
                if res.name == 'GlassReflectionCube':
                    return 

            res = trinity.TriTextureCubeParameter()
            res.name = 'GlassReflectionCube'
            res.resourcePath = PD.GLASS_SHADER_REFLECTION_CUBE_PATH
            effect.resources.append(res)
        elif name.startswith('c_s2'):
            for res in effect.resources:
                if res.name == 'ClothingReflectionCube':
                    return 

            res = trinity.TriTextureCubeParameter()
            res.name = 'ClothingReflectionCube'
            res.resourcePath = 'res:/Texture/Global/GenericReflection_cube.dds'
            effect.resources.append(res)
            for name in ['CellReflectionMap', 'CellReflection2ndMap']:
                res = trinity.TriTextureCubeParameter()
                res.name = name
                effect.resources.append(res)

        fastFx = '_fast.fx'
        if useFastShaders and fastFx not in path and path in PD.SHADERS_THAT_CAN_SWITCH_TO_FAST_SHADER_MODE:
            effect.effectFilePath = ApplySuffix(effect.effectFilePath[:-3], fastFx)
        elif doll.useDXT5N:
            effect.effectFilePath = ApplySuffix(effect.effectFilePath[:-3], '_dxt5n.fx')



    @staticmethod
    def BindHeroHairShader(effect, suffix):
        path = effect.effectFilePath.lower()
        if path.find('hair') == -1:
            return False
        if path.find('clothavatarhair') != -1:
            effect.effectFilePath = ApplySuffix('res:/Graphics/Effect/Managed/Interior/Avatar/clothavatarhair_detailed', suffix)
        else:
            effect.effectFilePath = ApplySuffix('res:/Graphics/Effect/Managed/Interior/Avatar/skinnedavatarhair_detailed', suffix)
        while effect.effectResource.isLoading:
            PD.Yield()

        name = effect.name.lower()
        effect.PopulateParameters()
        PD.SetOrAddMap(effect, 'HairNoise', 'res:/Texture/Global/noise1d.dds')
        PD.SetOrAddMap(effect, 'TangentMap', 'res:/Texture/Global/50gray.dds' if not name.startswith('c_hair_head') else 'res:/Texture/Global/HeadTangents.dds')
        PortraitTools.TweakDiffuseSampler(effect)
        return True



    @staticmethod
    def BindHeroClothShader(effect, useDXT5n):
        path = effect.effectFilePath.lower()
        if 'clothavatar' not in path or 'clothavatarhair' in path:
            return 
        suffix = '_dxt5n.fx' if useDXT5n else '.fx'
        effect.effectFilePath = ApplySuffix('res:/Graphics/Effect/Managed/Interior/Avatar/ClothAvatarLinear', suffix)
        while effect.effectResource.isLoading:
            PD.Yield()

        effect.PopulateParameters()
        PortraitTools.TweakDiffuseSampler(effect)



    @staticmethod
    def SetupStubble(meshes, name, stubblePath, adding = True):
        ret = []
        stubbleName = '{0}Stubble'.format(name)
        stubbleMeshes = (mesh for mesh in meshes if mesh.name.startswith(PD.DOLL_PARTS.HEAD))
        for mesh in stubbleMeshes:
            if adding:
                if any(map(lambda x: 'stubble' in x.name.lower(), mesh.decalAreas)):
                    ret.append(mesh)
                    continue
                c_skin_areas = (area for area in mesh.opaqueAreas if area.effect.name.lower().startswith('c_skin_'))
                for area in c_skin_areas:
                    stubbleArea = trinity.Tr2MeshArea()
                    stubbleArea.name = stubbleName
                    stubbleArea.index = area.index
                    stubbleArea.count = area.count
                    stubbleArea.effect = trinity.Load(stubblePath)
                    for resource in stubbleArea.effect.resources:
                        if resource.name == 'LengthTexture':
                            while resource.resource.IsLoading():
                                PD.Yield()


                    mesh.decalAreas.append(stubbleArea)
                    ret.append(mesh)
                    if PD.SkinSpotLightShadows.instance:
                        PD.SkinSpotLightShadows.instance.CreateEffectParamsForMesh(mesh, False)
                    for instance in PD.SkinLightmapRenderer.instances:
                        if instance():
                            instance().BindLightmapShader(mesh)


            else:
                targetAreasToRemove = [ area for area in mesh.decalAreas if area.name == stubbleName ]
                for ta in targetAreasToRemove:
                    mesh.decalAreas.remove(ta)


        return ret



    @staticmethod
    def HandleRemovedStubble(removedModifiers, buildDataManager):
        stubbleMods = (mod for mod in removedModifiers if mod.stubblePath)
        for mod in stubbleMods:
            stubbleMeshes = buildDataManager.GetMeshes(PD.DOLL_PARTS.HEAD)
            PortraitTools.SetupStubble(stubbleMeshes, mod.name, mod.stubblePath, False)




    @staticmethod
    def GetStubbleHash(addedAndChangedModifiers):
        for mod in iter(addedAndChangedModifiers):
            if mod.stubblePath:
                return 'active'

        return ''



    @staticmethod
    def HandleUpdatedStubble(addedAndChangedModifiers, buildDataManager):
        stubbleMods = (mod for mod in addedAndChangedModifiers if mod.stubblePath)
        stubbleMeshes = buildDataManager.GetMeshes(PD.DOLL_PARTS.HEAD)
        for mod in stubbleMods:
            meshes = PortraitTools.SetupStubble(stubbleMeshes[:], mod.name, mod.stubblePath, True)
            mod.meshes = meshes
            for mesh in iter(mod.meshes):
                for area in mesh.decalAreas:
                    fx = area.effect
                    wt = mod.weight
                    length = 0.003 + wt * 0.0027
                    alpha = 0.25 + wt * 2.25
                    for p in fx.parameters:
                        if p.name == 'MaterialDiffuseColor':
                            col = mod.colorizeData[0]
                            p.value = (col[0],
                             col[1],
                             col[2],
                             1.0)
                        if p.name == 'FurLength':
                            p.value = length
                        if p.name == 'AlphaMultiplier':
                            p.value = alpha







    @staticmethod
    def RebindDXT5ShadersForSM2(meshes):
        if meshes is None:
            return 
        for mesh in meshes:
            effects = PD.GetEffectsFromMesh(mesh)
            for effect in effects:
                path = effect.effectFilePath.lower()
                if '_dxt5n.fx' not in path:
                    continue
                path = path[:-9] + '.fx'
                if path not in PD.SHADERS_THAT_CAN_SWITCH_TO_FAST_SHADER_MODE:
                    continue
                path = path[:-3] + '_fast_dxt5n.fx'
                effect.effectFilePath = path






