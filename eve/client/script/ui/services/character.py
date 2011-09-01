import service
import paperDoll
import paperDollSculpting
import paperDollUtil
import trinity
import log
import blue
import ccConst
import ccUtil
import types
import bluepy
import geo2
import util
import uiutil
import random
import colorsys
import yaml
import uthread
WEIGHT_MODIFIER_PATH = ['bodyshapes/fatshape']
MUSCLE_MODIFIER_PATH = ['bodyshapes/muscularshape']
POTBELLY_PATH = ['bodyshapes/abs_forwardshape']
THIN_MODIFIER_PATH = ['bodyshapes/thinshape']
CATEGORY_NAMES = [paperDoll.HEAD_CATEGORIES.FACEMODIFIERS, paperDoll.DOLL_EXTRA_PARTS.BODYSHAPES, paperDoll.DOLL_EXTRA_PARTS.UTILITYSHAPES]
WEIGHT_BREAK_DOWNS = [('weightUpDown', 'up', 'down'), ('weightLeftRight', 'left', 'right'), ('weightForwardBack', 'forward', 'back')]

class Character(service.Service):
    __update_on_reload__ = 1
    __guid__ = 'svc.character'
    __exportedcalls__ = {}
    __notifyevents__ = ['OnGraphicSettingsChanged']

    @bluepy.CCP_STATS_ZONE_METHOD
    def __init__(self):
        service.Service.__init__(self)
        self.characters = {}
        self.characterMetadata = {}
        self.index = 0
        self.sculpting = None
        self.sculptingActive = False
        self.scene = None
        self.animationBloodlineData = None
        self.preloadedResources = []
        self.cachedHairColorVariations = {}
        self.cachedEyeshadowColorVariations = {}
        self.cachedHeadTattooColorVariations = {}
        self.hairColorRestrictions = None
        self.eyeshadowColorRestrictions = None
        self.headTattooColorRestrictions = None
        self.baseHairColors = None
        self.tuckingOptions = {}
        for (k, (modifierName, locationName, subKey,),) in ccConst.TUCKMAPPING.iteritems():
            self.tuckingOptions[modifierName] = subKey

        self.assetsToIDs = {'male': None,
         'female': None}
        self.animNetwork = blue.resMan.GetResource(ccConst.CHARACTER_CREATION_NETWORK)
        self.textureQuality = 1
        self.cachedPortraitInfo = {}



    @bluepy.CCP_STATS_ZONE_METHOD
    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.factory = sm.GetService('paperDollClient').dollFactory
        defaultClothSim = int(trinity.GetMaxShaderModelSupported() == 'SM_3_0_HI')
        self.factory.clothSimulationActive = prefs.GetValue('charClothSimulation', defaultClothSim)
        self.paperDollManager = paperDoll.PaperDollManager(self.factory)



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnGraphicSettingsChanged(self, changes):
        if 'textureQuality' in changes:
            if len(self.characters):
                dollID = self.characters.keys()[0]
                pdc = self.characters[dollID]
                pdc.doll.buildDataManager.SetAllAsDirty()
                pdc.Update()
        if 'charTextureQuality' in changes:
            textureQuality = prefs.GetValue('charTextureQuality', sm.GetService('device').GetDefaultCharTextureQuality())
            self.SetTextureQuality(textureQuality)
        if 'shaderQuality' in changes:
            if len(self.characters):
                dollID = self.characters.keys()[0]
                pdc = self.characters[dollID]
                if trinity.GetShaderModel().startswith('SM_3'):
                    pdc.doll.useFastShader = False
                else:
                    pdc.doll.useFastShader = True
        if self.sculpting is not None:
            self.sculpting.SetupPickScene(doUpdate=False)



    @bluepy.CCP_STATS_ZONE_METHOD
    def PreloadItems(self, gender, items):
        return 
        self.preloadedResources = []
        if gender == ccConst.GENDERID_FEMALE:
            options = self.factory.femaleOptions
        elif gender == ccConst.GENDERID_MALE:
            options = self.factory.maleOptions
        else:
            log.LogWarn('Preloading failed. Invalid gender!')
            return 
        resources = []
        for cat in options:
            for item in items:
                if item in cat:
                    resources.append(options[cat])


        for paths in resources:
            for path in paths:
                try:
                    whitelist = ['.png', '.dds', '.gr2']
                    if path.lower()[-4:] in whitelist:
                        self.preloadedResources.append(blue.resMan.GetResource(path))
                except:
                    log.LogException()





    @bluepy.CCP_STATS_ZONE_METHOD
    def ClearPreloads(self):
        self.preLoadedResources = []



    def InitializeNewCharacter(self, charID, genderID, bloodlineID):
        plugList = self.GetAvailableTypesByCategory('makeup/implants', genderID, bloodlineID)
        if len(plugList) > 0:
            self.ApplyTypeToDoll(charID, plugList[0], doUpdate=False)
        self.EnsureUnderwear(charID, genderID, bloodlineID)
        if genderID == ccConst.GENDERID_MALE:
            self.ApplyTypeToDoll(charID, ccConst.BASE_HAIR_TYPE_MALE, doUpdate=False)
        else:
            self.ApplyTypeToDoll(charID, ccConst.BASE_HAIR_TYPE_FEMALE, doUpdate=False)
        self.RandomizeDollCategory(charID, 'skintone', 0)
        self.RandomizeDollCategory(charID, 'makeup/eyes', 0)
        self.RandomizeDollCategory(charID, 'makeup/eyebrows', 0)
        (p, s,) = self.GetAvailableColorsForCategory('hair', genderID, bloodlineID)
        primary = random.choice(p)
        secondary = random.choice(s)
        self.SetColorValueByCategory(charID, 'hair', primary, secondary, doUpdate=False)
        self.SetHairDarkness(charID, 0.5)
        self.SynchronizeHairColors(charID)



    def GetNewCharacterMetadata(self, genderID, bloodlineID):
        return util.KeyVal(genderID=genderID, bloodlineID=bloodlineID, types={}, typeColors={}, typeWeights={}, typeSpecularity={}, hairDarkness=0.0, appearanceID=0)



    def RemoveFromCharacterMetadata(self, charID, category):
        if category in self.characterMetadata[charID].types:
            self.characterMetadata[charID].types.pop(category, None)
            self.characterMetadata[charID].typeColors.pop(category, None)
            self.characterMetadata[charID].typeSpecularity.pop(category, None)
            self.characterMetadata[charID].typeWeights.pop(category, None)



    @bluepy.CCP_STATS_ZONE_METHOD
    def AddCharacterToScene(self, charID, scene, gender, bloodlineID = None, dna = None, position = (0.0, 0.0, 0.0), updateDoll = True):
        applyNewCharacterTypes = False
        if charID in self.characters:
            character = self.characters[charID]
            character.MoveToScene(scene)
        elif dna is not None:
            randomDoll = paperDollUtil.CreateRandomDollNoClothes(gender, bloodlineID, noRandomize=True)
            self.characters[charID] = character = self.paperDollManager.SpawnDoll(scene, doll=randomDoll, updateDoll=updateDoll)
        else:
            applyNewCharacterTypes = True
            randomDoll = paperDollUtil.CreateRandomDollNoClothes(gender, bloodlineID, noRandomize=prefs.GetValue('NoRandomize', 0))
            self.characters[charID] = character = self.paperDollManager.SpawnDoll(scene, doll=randomDoll, updateDoll=updateDoll)
        self.characterMetadata[charID] = self.GetNewCharacterMetadata(ccUtil.PaperDollGenderToGenderID(gender), bloodlineID)
        self.scene = scene
        if character is None:
            log.LogError('AddCharacterToScene: Character', charID, 'not created')
            return 
        avatar = character.avatar
        networkPath = ccConst.CHARACTER_CREATION_NETWORK
        self.factory.CreateGWAnimation(avatar, networkPath)
        network = avatar.animationUpdater.network
        if network is not None:
            network.SetControlParameter('ControlParameters|BindPose', 1.0)
            if character.doll.gender == paperDoll.GENDER.FEMALE:
                network.SetAnimationSetIndex(0)
            else:
                network.SetAnimationSetIndex(1)
        if applyNewCharacterTypes and not prefs.GetValue('NoRandomize', 0):
            self.InitializeNewCharacter(charID, ccUtil.PaperDollGenderToGenderID(gender), bloodlineID)
        elif dna is not None:
            self.ApplyDBRowToDoll(charID, gender, bloodlineID, dna)
        return character



    @bluepy.CCP_STATS_ZONE_METHOD
    def RemoveCharacter(self, charID):
        if charID not in self.characters:
            return 
        avatar = self.characters[charID].avatar
        if avatar and avatar in self.scene.dynamics:
            self.scene.dynamics.remove(avatar)
        paperDollCharacter = self.characters.pop(charID)
        self.paperDollManager.RemovePaperDollCharacter(paperDollCharacter)
        del paperDollCharacter
        del self.characterMetadata[charID]



    @bluepy.CCP_STATS_ZONE_METHOD
    def TearDown(self):
        self.preloadedResources = []
        self.paperDollManager.ClearDolls()
        self.characters = {}
        sceneManager = sm.GetService('sceneManager')
        sceneManager.UnregisterScene2('characterCreation')
        if self.sculpting is not None:
            self.sculpting.avatar = None
            if self.sculpting.highlightGhost is not None:
                self.sculpting.highlightGhost.avatar = None
            if self.sculpting.bodyHighlightGhost is not None:
                self.sculpting.bodyHighlightGhost.avatar = None
            self.sculpting.scene = None
            self.sculpting.pickScene = None
            self.sculpting = None



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetModifierByPath(self, charID, path):
        if charID in self.characters:
            doll = self.characters[charID].doll
            return doll.GetBuildDataByResPath(path, includeFuture=True)



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetModifiersByCategory(self, charID, category):
        if charID not in self.characters:
            return None
        doll = self.characters[charID].doll
        ret = []
        mods = doll.buildDataManager.GetModifiersAsList(includeFuture=True)
        for m in mods:
            resPath = m.GetResPath()
            resPathSplit = resPath.split('/')
            categSplit = category.split('/')
            match = True
            for (i, each,) in enumerate(categSplit):
                if not (len(resPathSplit) > i and resPathSplit[i] == each):
                    match = False
                    break

            if match:
                ret.append(m)

        return ret



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateDoll(self, charID, fromWhere = None, registerDna = True):
        if charID not in self.characters:
            return 
        doll = self.characters[charID].doll
        avatar = self.characters[charID].avatar
        if self.sculpting:
            self.sculpting.UpdateBlendShapes([])
        else:
            doll.Update(self.factory, avatar)

        def wait_t():
            while doll.IsBusyUpdating():
                blue.synchro.Yield()

            if registerDna:
                uicore.layer.charactercreation.TryStoreDna(doll.lastUpdateRedundant, fromWhere)
            sm.ScatterEvent('OnDollUpdated', charID, doll.lastUpdateRedundant, fromWhere)
            uicore.layer.charactercreation.UnlockNavigation()


        uthread.new(wait_t)



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateTattoos(self, charID, doUpdate = True):
        if charID not in self.characters:
            return 
        pdc = self.characters[charID]

        def fun_t():
            while pdc.doll.IsBusyUpdating():
                blue.synchro.Yield()

            tattooModifiers = pdc.doll.buildDataManager.GetModifiersByCategory(paperDoll.BODY_CATEGORIES.TATTOO)
            if tattooModifiers:
                for each in tattooModifiers:
                    each.IsDirty = True

            if doUpdate:
                pdc.Update()


        uthread.new(fun_t)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetDollBloodline(self, charID, bloodlineID):
        self.characterMetadata[charID].bloodlineID = bloodlineID
        doll = self.characters[charID].doll
        gender = doll.gender
        limitPath = 'res:/Graphics/Character/Global/FaceSetup/ScultpingLimits/' + paperDollUtil.bloodlineAssets[bloodlineID] + '_' + gender + '_blendshape_limits.yaml'
        doll.AddBlendshapeLimitsFromFile(limitPath)
        self.AdaptDollAnimationData(paperDollUtil.bloodlineAssets[bloodlineID], self.characters[charID].avatar, gender)



    @bluepy.CCP_STATS_ZONE_METHOD
    def ResetDoll(self, charID, bloodlineID = None):
        if bloodlineID is not None:
            self.SetDollBloodline(charID, bloodlineID)
        if self.characterMetadata[charID].bloodlineID:
            self.ApplyItemToDoll(charID, 'head', paperDollUtil.bloodlineAssets[self.characterMetadata[charID].bloodlineID], doUpdate=True)



    @bluepy.CCP_STATS_ZONE_METHOD
    def AdaptDollAnimationData(self, bloodline, avatar, gender):
        if not self.animationBloodlineData:
            animPath = 'res:/Graphics/Character/Global/FaceSetup/AnimationData.yaml'
            rf = blue.ResFile()
            if rf.FileExists(animPath):
                f = rf.open(animPath)
                self.animationBloodlineData = yaml.load(f, Loader=yaml.CLoader)
                f.close()
        network = avatar.animationUpdater.network
        allParameters = network.GetAllControlParameters()
        for param in self.animationBloodlineData[bloodline][gender]:
            try:
                paramName = 'ControlParameters|' + param
                if paramName in allParameters:
                    network.SetControlParameter(paramName, self.animationBloodlineData[bloodline][gender][param])
            except:
                log.LogWarn('Invalid control parameter for bloodline: ' + param)




    @bluepy.CCP_STATS_ZONE_METHOD
    def SetCharacterWeight(self, charID, weight, doUpdate = True):
        doll = self.characters[charID].doll
        avatar = self.characters[charID].avatar
        network = avatar.animationUpdater.network
        if network is not None:
            network.SetControlParameter('ControlParameters|WeightAdjustment', weight)
        for mod in THIN_MODIFIER_PATH:
            limit = doll.modifierLimits.get(mod.split('/')[-1])
            multiplier = 1.0
            if limit and len(limit) == 2:
                multiplier = limit[1]
            modifier = self.GetModifierByPath(charID, mod)
            if modifier is None:
                modifier = doll.AddResource(mod, 0.0, self.factory)
            if weight <= 0.5:
                modifier.weight = (1 - weight * 2.0) * multiplier
            else:
                modifier.weight = 0.0

        for mod in WEIGHT_MODIFIER_PATH:
            modifier = self.GetModifierByPath(charID, mod)
            doll.RemoveResource(mod, self.factory)

        belly = 0.0
        for mod in POTBELLY_PATH:
            modifier = self.GetModifierByPath(charID, mod)
            if modifier and modifier.weight > 0.0:
                belly = modifier.weight
                doll.RemoveResource(mod, self.factory)

        m = self.GetCharacterMuscularity(charID)
        for mod in MUSCLE_MODIFIER_PATH:
            modifier = self.GetModifierByPath(charID, mod)
            doll.RemoveResource(mod, self.factory)

        self.SetCharacterMuscularity(charID, m, doUpdate=False)
        if belly > 0.0:
            for mod in POTBELLY_PATH:
                doll.AddResource(mod, belly, self.factory)

        for mod in WEIGHT_MODIFIER_PATH:
            limit = doll.modifierLimits.get(mod.split('/')[-1])
            multiplier = 1.0
            if limit and len(limit) == 2:
                multiplier = limit[1]
            modifier = self.GetModifierByPath(charID, mod)
            if modifier is None:
                modifier = doll.AddResource(mod, 0.0, self.factory)
            if weight >= 0.5:
                modifier.weight = (weight - 0.5) * 2.0 * multiplier
            else:
                modifier.weight = 0.0

        if doUpdate:
            self.UpdateTattoos(charID, doUpdate=False)
            self.UpdateDoll(charID, fromWhere='SetCharacterWeight')



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetCharacterWeight(self, charID):
        doll = self.characters[charID].doll
        avatar = self.characters[charID].avatar
        ret = []
        for mod in WEIGHT_MODIFIER_PATH:
            limit = doll.modifierLimits.get(mod.split('/')[-1])
            multiplier = 1.0
            if limit and len(limit) == 2:
                multiplier = limit[1]
            modifier = self.GetModifierByPath(charID, mod)
            if modifier is not None:
                if modifier.weight > 0.0:
                    return 0.5 + modifier.weight * 0.5 / multiplier

        for mod in THIN_MODIFIER_PATH:
            limit = doll.modifierLimits.get(mod.split('/')[-1])
            multiplier = 1.0
            if limit and len(limit) == 2:
                multiplier = limit[1]
            modifier = self.GetModifierByPath(charID, mod)
            if modifier is not None:
                return (1 - modifier.weight / multiplier) * 0.5

        return 0.5



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetCharacterMuscularity(self, charID, weight, doUpdate = True):
        doll = self.characters[charID].doll
        avatar = self.characters[charID].avatar
        for mod in MUSCLE_MODIFIER_PATH:
            limit = doll.modifierLimits.get(mod.split('/')[-1])
            multiplier = 1.0
            if limit and len(limit) == 2:
                multiplier = limit[1]
            modifier = self.GetModifierByPath(charID, mod)
            if modifier is None:
                modifier = doll.AddResource(mod, 0.0, self.factory)
            modifier.weight = weight * multiplier

        if doUpdate:
            self.UpdateTattoos(charID, doUpdate=False)
            self.UpdateDoll(charID, fromWhere='SetCharacterMuscularity')



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetCharacterMuscularity(self, charID):
        doll = self.characters[charID].doll
        avatar = self.characters[charID].avatar
        ret = []
        for mod in MUSCLE_MODIFIER_PATH:
            limit = doll.modifierLimits.get(mod.split('/')[-1])
            multiplier = 1.0
            if limit and len(limit) == 2:
                multiplier = limit[1]
            modifier = self.GetModifierByPath(charID, mod)
            if modifier is not None:
                ret = modifier.weight / multiplier
            else:
                ret = 0.0

        return ret



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetModifierByCategory(self, charID, category, getAll = False):
        modifiers = self.GetModifiersByCategory(charID, category)
        if not modifiers:
            return None
        else:
            if getAll:
                return modifiers
            if category == paperDoll.HAIR_CATEGORIES.BEARD:
                for modifier in modifiers:
                    if modifier.name != 'stubble':
                        return modifier

            return modifiers[0]



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetEyeshadowColors(self, bloodlineID, genderID):
        colorVars = self.LoadEyeShadowColorVariations(bloodlineID, genderID)
        return self.GetModifierColors(colorVars=colorVars)



    @bluepy.CCP_STATS_ZONE_METHOD
    def LoadEyeShadowColorVariations(self, bloodlineID, genderID):
        if genderID != ccConst.GENDERID_FEMALE:
            log.LogError('LoadEyeShadowColorVariations - can only use this for females')
            return []
        cached = self.cachedEyeshadowColorVariations.get((bloodlineID, genderID))
        if cached is not None:
            return cached
        if self.eyeshadowColorRestrictions is None:
            self.eyeshadowColorRestrictions = [ccUtil.LoadFromYaml(ccConst.EYESHADOWCOLOR_RESTRICTION_FEMALE)]
        variations = self.GetModifierColorVariation(bloodlineID, self.eyeshadowColorRestrictions[genderID], ccConst.EYESHADOWCOLORS[genderID])
        self.cachedEyeshadowColorVariations[(bloodlineID, genderID)] = variations
        return variations



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetHairColors(self, bloodlineID, genderID):
        colorVars = self.LoadHairColorVariations(bloodlineID, genderID)
        if self.baseHairColors is None:
            self.baseHairColors = [ccUtil.LoadFromYaml(ccConst.BASE_HAIR_COLOR_FEMALE), ccUtil.LoadFromYaml(ccConst.BASE_HAIR_COLOR_MALE)]
        baseColor = self.baseHairColors[genderID]
        if baseColor is None:
            log.LogWarn('Failed to load base color for hair')
            baseColor = (0.5, 0.5, 0.5, 1.0)
        return self.GetModifierColors(colorVars=colorVars)



    @bluepy.CCP_STATS_ZONE_METHOD
    def LoadHairColorVariations(self, bloodlineID, genderID):
        if bloodlineID is None or genderID is None:
            log.LogError('LoadHairColorVariations - bloodlineID and genderID must not be None')
            return []
        cached = self.cachedHairColorVariations.get((bloodlineID, genderID))
        if cached is not None:
            return cached
        if self.hairColorRestrictions is None:
            self.hairColorRestrictions = [ccUtil.LoadFromYaml(ccConst.HAIRCOLOR_RESTRICTION_FEMALE), ccUtil.LoadFromYaml(ccConst.HAIRCOLOR_RESTRICTION_MALE)]
        variations = self.GetModifierColorVariation(bloodlineID, self.hairColorRestrictions[genderID], ccConst.HAIRCOLORS[genderID])
        self.cachedHairColorVariations[(bloodlineID, genderID)] = variations
        return variations



    def GetHeadTattooColors(self, bloodlineID, genderID):
        colorVars = self.LoadHeadTattooVariations(bloodlineID, genderID)
        return self.GetModifierColors(colorVars=colorVars)



    @bluepy.CCP_STATS_ZONE_METHOD
    def LoadHeadTattooVariations(self, bloodlineID, genderID):
        if bloodlineID is None or genderID is None:
            log.LogError('LoadHeadTattooVariations - bloodlineID and genderID must not be None')
            return []
        cached = self.cachedHeadTattooColorVariations.get((bloodlineID, genderID))
        if cached is not None:
            return cached
        if self.headTattooColorRestrictions is None:
            self.headTattooColorRestrictions = [ccUtil.LoadFromYaml(ccConst.HEADTATTOOCOLOR_RESTRICTION_FEMALE), ccUtil.LoadFromYaml(ccConst.HEADTATTOOCOLOR_RESTRICTION_MALE)]
        variations = self.GetModifierColorVariation(bloodlineID, self.headTattooColorRestrictions[genderID], ccConst.HEADTATTOOCOLORS[genderID])
        self.cachedHeadTattooColorVariations[(bloodlineID, genderID)] = variations
        return variations



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetModifierColorVariation(self, bloodlineID, restrictions, path):
        variations = {}
        for each in restrictions:
            if bloodlineID not in restrictions[each]:
                colorFile = path + each
                var = ccUtil.LoadFromYaml(colorFile)
                if var is not None:
                    variations[each.split('.')[0]] = var
                else:
                    log.LogWarn('GetModifierColorVariation - Could not load color file:', colorFile)

        return variations



    def GetModifierColors(self, colorVars):
        retColorsA = []
        retColorsBC = []
        for each in colorVars:
            color = colorVars[each]['colors']
            if color and type(color[0]) == types.TupleType:
                if each.lower().endswith('_a'):
                    displayColor = color[0]
                    (r, g, b, a,) = displayColor
                    yiq = colorsys.rgb_to_yiq(r, g, b)
                    retColorsA.append((yiq, (each, (r,
                       g,
                       b,
                       1.0), colorVars[each])))
                elif each.lower().endswith('_bc'):
                    displayColor = color[1]
                    (r, g, b, a,) = displayColor
                    yiq = colorsys.rgb_to_yiq(r, g, b)
                    retColorsBC.append((yiq, (each, (r,
                       g,
                       b,
                       1.0), colorVars[each])))
                else:
                    print 'Unsupported modifier color',
                    print each

        retColorsA = uiutil.SortListOfTuples(retColorsA)
        retColorsBC = uiutil.SortListOfTuples(retColorsBC)
        return (retColorsA, retColorsBC)



    def SetHairDarkness(self, charID, darkness):
        if darkness != self.characterMetadata[charID].hairDarkness:
            self.characterMetadata[charID].hairDarkness = darkness
            self.SynchronizeHairColors(charID)



    def GetHairDarkness(self, charID):
        return self.characterMetadata[charID].hairDarkness



    @bluepy.CCP_STATS_ZONE_METHOD
    def SynchronizeHairColors(self, charID):
        hairData = self.GetModifierByCategory(charID, ccConst.hair)
        if hairData is not None:
            colorizeData = hairData.colorizeData
            (orgA, orgB, orgC,) = colorizeData
            newA = geo2.Vector(*orgA)
            lowA = newA * 0.2
            newA = geo2.Vec4Lerp(lowA, newA, self.characterMetadata[charID].hairDarkness)
            adjustedColor = (newA, orgB, orgC)
            for hairModifier in (ccConst.beard, ccConst.eyebrows):
                if hairModifier == ccConst.beard:
                    hms = self.GetModifierByCategory(charID, hairModifier, getAll=True)
                else:
                    hms = [self.GetModifierByCategory(charID, hairModifier)]
                if hms is None:
                    continue
                for hm in hms:
                    if hm:
                        hm.colorizeData = adjustedColor
                        hm.pattern = hairData.pattern
                        hm.patternData = hairData.patternData
                        hm.specularColorData = hairData.specularColorData
                        hm.SetColorVariation('none')





    @bluepy.CCP_STATS_ZONE_METHOD
    def GetAvailableColorsForCategory(self, categoryPath, genderID, bloodlineID):
        if categoryPath == ccConst.hair:
            return self.GetHairColors(bloodlineID, genderID)
        if categoryPath == ccConst.t_head:
            return self.GetHeadTattooColors(bloodlineID, genderID)
        if genderID == ccConst.GENDERID_FEMALE and categoryPath == ccConst.eyeshadow:
            return self.GetEyeshadowColors(bloodlineID, genderID)
        if type(genderID) is int:
            genderID = ccUtil.GenderIDToPaperDollGender(genderID)
        combined = {}
        typeData = self.GetAvailableTypesByCategory(categoryPath, genderID, bloodlineID, getTypesOnly=True)
        for each in typeData:
            modifier = self.factory.CollectBuildData(each[0], self.factory.GetOptionsByGender(genderID))
            combined.update(modifier.colorVariations)

        doneA = []
        doneBC = []
        retColorsA = []
        retColorsBC = []
        for (colorName, colorData,) in combined.iteritems():
            if categoryPath.startswith(ccConst.lipstick):
                if colorName.find('_glossy') != -1 or colorName.find('_medium') != -1:
                    continue
            displayColor = colorData.get('colors') if colorData else None
            if displayColor is None:
                log.LogWarn('No colors in colorData when calling GetAvailableColorsForCategory', categoryPath, genderID, bloodlineID)
                continue
            if type(displayColor) == types.TupleType or type(displayColor) == types.ListType:
                displayColor = colorData['colors'][0]
                (r, g, b, a,) = displayColor
            else:
                (r, g, b,) = displayColor
            (h, s, v,) = colorsys.rgb_to_hsv(r, g, b)
            (r, g, b,) = colorsys.hsv_to_rgb(h, s * 0.8, v * 0.8)
            yiq = colorsys.rgb_to_yiq(r, g, b)
            if colorName.lower().endswith('_bc'):
                if colorData['colors'] not in doneBC:
                    retColorsBC.append((yiq, (colorName, (r,
                       g,
                       b,
                       1.0), colorData)))
                    doneBC.append(colorData['colors'])
            elif colorData['colors'] not in doneA:
                retColorsA.append((yiq, (colorName, (r,
                   g,
                   b,
                   1.0), colorData)))
                doneA.append(colorData['colors'])

        retColorsA = uiutil.SortListOfTuples(retColorsA)
        retColorsBC = uiutil.SortListOfTuples(retColorsBC)
        return (retColorsA, retColorsBC)



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetCharacterColorVariations(self, charID, category):
        colors = []
        selectedIndex = None
        modifier = self.GetModifierByCategory(charID, category)
        if modifier:
            colorVars = modifier.GetColorVariations()
            if category == ccConst.skintone:
                bloodline = self.characterMetadata[charID].bloodlineID
                bloodlineFilter = {1: 'deteis',
                 2: 'civire',
                 11: 'achura',
                 7: 'gallente',
                 8: 'intaki',
                 12: 'jinmei',
                 3: 'sebiestor',
                 4: 'brutor',
                 14: 'vherokior',
                 5: 'amarr',
                 13: 'khanid',
                 6: 'nikunni'}
                filter = bloodlineFilter[bloodline]
                newColorVars = []
                for c in colorVars:
                    if c.startswith(filter):
                        newColorVars.append(c)

                colorVars = newColorVars
            if category == ccConst.lipstick:
                newColorVars = []
                for c in colorVars:
                    if c.lower().endswith('_medium'):
                        newColorVars.append(c)

                colorVars = newColorVars
            selectedColor = modifier.GetColorizeData()
            for (i, cv,) in enumerate(colorVars):
                c = modifier.GetColorsFromColorVariation(cv)
                if selectedColor == c:
                    selectedIndex = i
                colors.append((cv, c))

        return (colors, selectedIndex)



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetAvailableTypesByCategory(self, category, gender, bloodline, getTypesOnly = False):
        if type(gender) is int:
            gender = ccUtil.GenderIDToPaperDollGender(gender)
        types = self.factory.ListTypes(gender, category)
        ret = []
        retData = []
        resFile = blue.ResFile()
        availableTypeIDs = sm.GetService('cc').GetMyApparel()
        hasContentRole = session.role & service.ROLE_CONTENT
        inLimitedRecustomization = util.GetAttrs(uicore, 'layer', 'charactercreation', 'mode') == ccConst.MODE_LIMITED_RECUSTOMIZATION
        for (i, each,) in enumerate(types):
            typeData = self.factory.GetItemType(each)
            if typeData is None:
                log.LogWarn('GetItemType for path returned None', each)
                continue
            (assetID, assetTypeID,) = self.GetAssetAndTypeIDsFromPath(gender, each)
            if not hasContentRole and assetTypeID is not None and (assetTypeID not in availableTypeIDs or not inLimitedRecustomization):
                continue
            if len(typeData) == 4:
                restrictions = typeData[-1]
                if type(restrictions) == list:
                    if bloodline not in restrictions:
                        retType = typeData[:-1]
                        ret.append(((assetTypeID is None, i), (assetID, retType, assetTypeID)))
                        retData.append(retType)
            else:
                ret.append(((assetTypeID is None, i), (assetID, typeData, assetTypeID)))
                retData.append(typeData)

        if getTypesOnly:
            return retData
        ret = uiutil.SortListOfTuples(ret)
        return ret



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetAvailableItemsByCategory(self, category, gender, bloodline, showVariations = False):
        if type(gender) is int:
            gender = ccUtil.GenderIDToPaperDollGender(gender)
        items = self.factory.ListOptions(gender, category, showVariations)
        self.PreloadItems(gender, items)
        return items



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetCategoryFromResPath(self, resPath):
        parts = resPath.split('/')
        return '/'.join(parts[:-1])



    @bluepy.CCP_STATS_ZONE_METHOD
    def ApplyTypeToDoll(self, charID, itemType, weight = 1.0, doUpdate = True, rawColorVariation = None):
        if itemType is None:
            return 
        genderID = self.characterMetadata[charID].genderID
        if type(itemType) is not tuple:
            charGender = ccUtil.GenderIDToPaperDollGender(genderID)
            itemTypeData = self.factory.GetItemType(itemType)
            if itemTypeData is None:
                log.LogError("Item type file is missing can can't be loaded", itemType)
                return 
            (assetID, assetTypeID,) = self.GetAssetAndTypeIDsFromPath(charGender, itemType)
            itemType = (assetID, itemTypeData[:3], assetTypeID)
        doll = self.characters[charID].doll
        category = self.GetCategoryFromResPath(itemType[1][0])
        activeMod = self.GetModifierByCategory(charID, category)
        if activeMod:
            doll.RemoveResource(activeMod.GetResPath(), self.factory)
        modifier = doll.AddItemType(self.factory, itemType[1], weight, rawColorVariation)
        self.characterMetadata[charID].types[category] = itemType[0]
        if ccUtil.HasUserDefinedWeight(category):
            self.characterMetadata[charID].typeWeights[category] = weight
        if category in (ccConst.hair, ccConst.beard, ccConst.eyebrows):
            self.SynchronizeHairColors(charID)
        if doUpdate:
            self.UpdateDoll(charID, fromWhere='ApplyTypeToDoll')
        return modifier



    @bluepy.CCP_STATS_ZONE_METHOD
    def ApplyItemToDoll(self, charID, category, name, removeFirst = False, variation = None, doUpdate = True):
        doll = self.characters[charID].doll
        modifier = None
        modifierFoundForVariationSwitch = False
        if name and variation:
            modifier = self.GetModifierByCategory(charID, category)
            if modifier and modifier.name.split(paperDoll.SEPERATOR_CHAR)[-1] == name:
                modifier.SetVariation(variation)
                modifierFoundForVariationSwitch = True
        if not modifierFoundForVariationSwitch:
            if removeFirst:
                if name:
                    modifier = self.GetModifierByCategory(charID, category)
                    if modifier:
                        self.RemoveFromCharacterMetadata(charID, category)
                        doll.RemoveResource(modifier.respath, self.factory)
                else:
                    modifiers = self.GetModifierByCategory(charID, category, getAll=True)
                    if modifiers:
                        self.RemoveFromCharacterMetadata(charID, category)
                        for modifier in modifiers:
                            doll.RemoveResource(modifier.respath, self.factory)

            if name:
                modifier = doll.AddResource(category + '/' + name, 1.0, self.factory, variation=variation)
            elif not removeFirst:
                modifier = self.GetModifierByCategory(charID, category)
                if modifier:
                    self.RemoveFromCharacterMetadata(charID, category)
                    doll.RemoveResource(modifier.GetResPath(), self.factory)
        if doUpdate:
            self.UpdateDoll(charID, fromWhere='ApplyItemToDoll')
        return modifier



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetColorValueByCategory(self, charID, category, colorVar1, colorVar2, doUpdate = True):
        if colorVar1 is None:
            log.LogError('SetColorValue - No Color variation passed in!')
            return 
        (color1Value, color1Name, color2Name, variation,) = self.GetColorsToUse(colorVar1, colorVar2)
        modifier = self.GetModifierByCategory(charID, category)
        if not modifier:
            return 
        if color1Value:
            self.characterMetadata[charID].typeColors[category] = (color1Name, None)
            modifier.SetColorizeData(color1Value)
        elif colorVar2 is not None:
            self.characterMetadata[charID].typeColors[category] = (color1Name, color2Name)
            modifier.SetColorVariationDirectly(variation)
        else:
            self.characterMetadata[charID].typeColors[category] = (color1Name, None)
            modifier.SetColorVariationDirectly(variation)
        if category == ccConst.hair:
            self.SynchronizeHairColors(charID)
        if doUpdate:
            self.UpdateDoll(charID, fromWhere='SetColorValueByCategory')



    def GetColorsToUse(self, colorVar1, colorVar2, *args):
        if colorVar1 is None:
            log.LogError('GetColorsToUse - No Color variation passed in!')
            return (None, None, None, None)
        else:
            if len(colorVar1) == 3:
                colorVar1 = (colorVar1[0], colorVar1[2])
            if colorVar2 is not None and len(colorVar2) == 3:
                colorVar2 = (colorVar2[0], colorVar2[2])
            (color1Name, color1Value,) = colorVar1
            if type(color1Value) == types.TupleType:
                return (color1Value,
                 color1Name,
                 None,
                 None)
            if colorVar2 is not None:
                (color2Name, color2Value,) = colorVar2
                variation = {}
                if 'colors' in color1Value:
                    variation['colors'] = [color1Value['colors'][0], color2Value['colors'][1], color2Value['colors'][2]]
                if 'pattern' in color1Value:
                    variation['pattern'] = color1Value['pattern']
                if 'patternColors' in color1Value:
                    variation['patternColors'] = [color1Value['patternColors'][0], color2Value['patternColors'][1], color2Value['patternColors'][2]]
                if 'patternColors' in color1Value:
                    variation['patternColors'] = color1Value['patternColors']
                if 'specularColors' in color1Value:
                    variation['specularColors'] = [color1Value['specularColors'][0], color2Value['specularColors'][1], color2Value['specularColors'][2]]
                return (None,
                 color1Name,
                 color2Name,
                 variation)
            return (None,
             color1Name,
             None,
             color1Value)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetColorSpecularityByCategory(self, charID, category, specularity, doUpdate = True):
        modifier = self.GetModifierByCategory(charID, category)
        if modifier:
            self.characterMetadata[charID].typeSpecularity[category] = specularity
            m1 = 1.0 + 0.4 * specularity
            s1 = 0.5 + 0.3 * specularity
            s2 = 0.5 - 0.2 * specularity
            modifier.SetColorVariationSpecularity([(s1,
              s1,
              s1,
              m1), (s2,
              s2,
              s2,
              1.0), (0.5, 0.5, 0.5, 1.0)])
            if doUpdate:
                self.UpdateDoll(charID, fromWhere='SetColorSpecularityByCategory')



    def GetColorSpecularityByCategory(self, charID, category):
        return self.characterMetadata[charID].typeSpecularity.get(category, 0.5)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetWeightByCategory(self, charID, category, weight, doUpdate = True):
        modifier = self.GetModifierByCategory(charID, category)
        if not modifier and charID in self.characters:
            doll = self.characters[charID].doll
            if doll.gender == paperDoll.GENDER.FEMALE:
                gender = 0
            else:
                gender = 1
            options = self.GetAvailableItemsByCategory(category, gender, self.characterMetadata[charID].bloodlineID)
            if options:
                name = options[0]
                modifier = doll.AddResource(category + '/' + name, 1.0, self.factory)
        if modifier:
            if ccUtil.HasUserDefinedWeight(category):
                self.characterMetadata[charID].typeWeights[category] = weight
            modifier.weight = weight
            if doUpdate:
                self.UpdateDoll(charID, 'SetWeightByCategory')



    def GetWeightByCategory(self, charID, category):
        weight = self.characterMetadata[charID].typeWeights.get(category, 0)
        sliderWeight = self.GetSliderWeight(charID, category, weight)
        return sliderWeight



    def GetTrueWeight(self, charID, category, sliderWeight):
        weight = sliderWeight
        if category in ccConst.weightLimits:
            limits = ccConst.weightLimits[category]
            color = self.characterMetadata[charID].typeColors.get(category, None)
            minMax = limits.get(color, None) or limits.get('default', None)
            if minMax:
                diff = minMax[1] - minMax[0]
                weight = minMax[0] + diff * weight
        return weight



    def GetSliderWeight(self, charID, category, trueWeight):
        weight = trueWeight
        if category in ccConst.weightLimits:
            limits = ccConst.weightLimits[category]
            color = self.characterMetadata[charID].typeColors.get(category, None)
            minMax = limits.get(color, None) or limits.get('default', None)
            diff = minMax[1] - minMax[0]
            weight = (weight - minMax[0]) / diff
        return weight



    @bluepy.CCP_STATS_ZONE_METHOD
    def SculptCallBack(self, zone, isFront):
        uicore.layer.charactercreation.ChangeSculptCursor(zone, isFront)



    @bluepy.CCP_STATS_ZONE_METHOD
    def StartEditMode(self, charID, scene, camera, mode = 'sculpt', showPreview = False, callback = None, pickCallback = None, inactiveZones = [], resetAll = False, skipPickSceneReset = False, useThread = 1):
        if useThread:
            uthread.new(self.StartEditMode_t, *(charID,
             scene,
             camera,
             mode,
             showPreview,
             callback,
             pickCallback,
             inactiveZones,
             resetAll,
             skipPickSceneReset))
        else:
            character = self.characters.get(charID, None)
            if character is None or character.doll.IsBusyUpdating():
                return 
            self.StartEditMode_t(charID, scene, camera, mode, showPreview, callback, pickCallback, inactiveZones, resetAll, skipPickSceneReset)



    @bluepy.CCP_STATS_ZONE_METHOD
    def StartEditMode_t(self, charID, scene, camera, mode, showPreview, callback, pickCallback, inactiveZones, resetAll, skipPickSceneReset):
        character = self.characters.get(charID, None)
        count = 0
        while (character is None or character.doll.IsBusyUpdating()) and count < 100:
            count += 1
            blue.synchro.Yield()

        if character is None:
            return 
        if not self.sculpting or resetAll:
            if self.sculpting and self.sculpting.highlightGhost:
                if self.sculpting.highlightGhost.renderStepSlot and self.sculpting.highlightGhost.renderStepSlot.object:
                    self.sculpting.highlightGhost.renderStepSlot.object.job = None
            self.sculpting = paperDollSculpting.Sculpting(character.avatar, character.doll, scene, camera, self.factory, mode=mode, callback=callback, pickCallback=pickCallback, inactiveZones=inactiveZones)
        else:
            self.sculpting.Reset(character.doll, character.avatar, camera=camera, mode=mode, callback=callback, pickCallback=pickCallback, inactiveZones=inactiveZones, skipPickSceneReset=skipPickSceneReset)
        self.sculptingActive = True
        gender = character.doll.gender
        isMale = gender == 'male'
        if showPreview:
            self.sculpting.RunHighlightPreview(isMale)



    @bluepy.CCP_STATS_ZONE_METHOD
    def StopEditing(self, *args, **kwds):
        if self.sculpting is not None:
            self.sculpting.Stop()
        self.sculptingActive = False



    @bluepy.CCP_STATS_ZONE_METHOD
    def IsSculptingReady(self):
        if not self.sculpting:
            return False
        return self.sculpting.IsReady()



    @bluepy.CCP_STATS_ZONE_METHOD
    def StartPosing(self, charID, callback = None):
        avatar = self.characters[charID].avatar
        network = avatar.animationUpdater.network
        if network is not None:
            network.SetControlParameter('ControlParameters|BindPose', 0.0)
        uicore.layer.charactercreation.StartEditMode(showPreview=False, mode='animation', callback=callback)



    @bluepy.CCP_STATS_ZONE_METHOD
    def StopPosing(self, charID):
        avatar = self.characters[charID].avatar
        network = avatar.animationUpdater.network
        if network is not None:
            network.SetControlParameter('ControlParameters|BindPose', 1.0)



    @bluepy.CCP_STATS_ZONE_METHOD
    def ChangePose(self, v, charID, *args):
        avatar = self.characters[charID].avatar
        if hasattr(avatar.animationUpdater, 'network'):
            network = avatar.animationUpdater.network
            if network is not None:
                controlParameter = 'ControlParameters|PortraitPoseNumber'
                network.SetControlParameter(controlParameter, float(v))



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetControlParametersFromList(self, params, charID):
        if charID not in self.characters:
            return 
        avatar = self.characters[charID].avatar
        if not hasattr(avatar.animationUpdater, 'network'):
            return 
        network = avatar.animationUpdater.network
        for param in params:
            network.SetControlParameter(param[0], param[1])




    @bluepy.CCP_STATS_ZONE_METHOD
    def ResetFacePose(self, charID):
        if charID not in self.characters:
            return 
        self.SetControlParametersFromList(ccConst.FACE_POSE_CONTROLPARAMS, charID)
        genderID = self.characterMetadata[charID].genderID
        avatar = self.characters[charID].avatar
        network = avatar.animationUpdater.network
        if genderID == 1:
            network.SetControlParameter('ControlParameters|HeadLookTarget', (0.0, 1.6, 0.5))
        else:
            network.SetControlParameter('ControlParameters|HeadLookTarget', (0.0, 1.5, 0.5))



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetTextureQuality(self, quality):
        self.textureQuality = quality
        resolution = ccConst.TEXTURE_RESOLUTIONS[quality]
        for each in self.characters:
            character = self.characters[each]
            character.doll.textureResolution = resolution
            self.UpdateDollsAvatar(character)




    @bluepy.CCP_STATS_ZONE_METHOD
    def EnableClothSimulation(self, value):
        self.factory.clothSimulationActive = bool(value)
        characters = list(self.characters.values())
        for character in sm.GetService('paperDollClient').paperDollManager:
            characters.append(character)

        for character in characters:
            character.UpdateClothSimulationStatus()




    def MatchDNA(self, character, dna):
        character.doll.MatchDNA(self.factory, dna)



    def UpdateDollsAvatar(self, character, *args):
        character.doll.Update(self.factory, character.avatar)



    def GetSculpting(self, *args):
        return self.sculpting



    def GetSculptingActive(self, *args):
        return self.sculptingActive



    @bluepy.CCP_STATS_ZONE_METHOD
    def RandomizeCharacterSculpting(self, charID, doUpdate = False):
        blue.synchro.Yield()
        if charID in self.characters:
            randomizer = paperDoll.EveDollRandomizer(self.factory)
            randomizer.gender = ccUtil.GenderIDToPaperDollGender(self.characterMetadata[charID].genderID)
            randomizer.bloodline = self.characterMetadata[charID].bloodlineID
            randomizer.SetSculptingLimits()
            blendshapeOptions = randomizer.GetBlendshapeOptions()
            randomizer.ApplyRandomizedResourcesToCharacter(charID, blendshapeOptions)
            if self.sculptingActive:
                self.sculpting.UpdateFieldsBasedOnExistingValues(self.characters[charID].doll)
            wt = self.GetCharacterWeight(charID)
            self.SetCharacterWeight(charID, wt, doUpdate=False)
            if doUpdate:
                self.UpdateDoll(charID, fromWhere='RandomizeCharacterSculpting')



    @bluepy.CCP_STATS_ZONE_METHOD
    def RandomizeCharacterGroups(self, charID, categoryList, doUpdate = False, fullRandomization = False):
        if charID in self.characters:
            doHairDarkness = False
            for category in categoryList:
                if category in (ccConst.hair, ccConst.beard, ccConst.eyebrows):
                    doHairDarkness = True
                addWeight = False
                weightFrom = 0.1
                if fullRandomization and category.startswith('makeup/'):
                    weightTo = 0.3
                else:
                    weightTo = 1.0
                doll = self.characters[charID].doll
                modifier = self.GetModifierByCategory(charID, category)
                if modifier:
                    self.RemoveFromCharacterMetadata(charID, category)
                    doll.RemoveResource(modifier.GetResPath(), self.factory)
                if category in ccConst.addWeightToCategories:
                    addWeight = True
                oddsDict = {}
                if doll.gender == ccConst.GENDERID_FEMALE:
                    oddsDict = ccConst.femaleOddsOfSelectingNone.copy()
                    if fullRandomization:
                        oddsDict.update(ccConst.femaleOddsOfSelectingNoneFullRandomize)
                else:
                    oddsDict = ccConst.maleOddsOfSelectingNone.copy()
                    if fullRandomization:
                        oddsDict.update(ccConst.maleOddsOfSelectingNoneFullRandomize)
                oddsOfSelectingNone = oddsDict.get(category, None)
                self.RandomizeDollCategory(charID, category, oddsOfSelectingNone, addWeight, weightFrom, weightTo, fullRandomization)

            if doHairDarkness:
                hairDarkness = round(random.random(), 2)
                self.SetHairDarkness(charID, hairDarkness)
            if doUpdate:
                self.UpdateDoll(charID, fromWhere='RandomizeCharacterGroups')



    def RandomizeDollCategory(self, charID, category, oddsOfSelectingNone, addWeight = None, weightFrom = 0, weightTo = 1.0, fullRandomization = False):
        blue.synchro.Yield()
        randomizer = paperDoll.EveDollRandomizer(self.factory)
        randomizer.gender = self.characters[charID].doll.GetDNA()[0]
        randomizer.bloodline = self.characterMetadata[charID].bloodlineID
        randomizer.fullRandomization = fullRandomization
        randomizer.AddCategoryForWhitelistRandomization(category, oddsOfSelectingNone)
        if addWeight:
            randomizer.AddPathForWeightRandomization(category, weightFrom, weightTo)
        options = randomizer.GetResources()
        randomizer.ApplyRandomizedResourcesToCharacter(charID, options)



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetPoseData(self):
        self.sculpting.UpdateAnimation([])
        poseDataDict = self.sculpting.animationController.GetAllControlParameterValuesByName(True)
        for k in poseDataDict.keys():
            if k not in paperDollUtil.FACIAL_POSE_PARAMETERS.__dict__:
                del poseDataDict[k]

        return poseDataDict



    @bluepy.CCP_STATS_ZONE_METHOD
    def ValidateDollCustomizationComplete(self, charID):
        genderString = self.characters[charID].doll.gender
        for (category, assetID,) in self.characterMetadata[charID].types.iteritems():
            if assetID is None:
                self.LogError('Invalid asset chosen for category ', category, '. Please make sure the asset has an associated ID.')

        dolData = self.GetCharacterAppearanceInfo(charID)
        return paperDollUtil.HasRequiredClothing(genderString, dolData.modifiers)



    def GetSingleCharactersDoll(self, charID):
        return self.characters[charID].doll



    def GetSingleCharactersAvatar(self, charID):
        avatar = None
        try:
            avatar = self.characters[charID].avatar
        except KeyError:
            pass
        return avatar



    def GetSingleCharacter(self, charID, *args):
        return self.characters[charID]



    def GetSingleCharactersMetadata(self, charID, *args):
        return self.characterMetadata[charID]



    def GetTypeColors(self, charID, cat):
        return self.characterMetadata[charID].typeColors.get(cat, (None, None))



    def GetAssetAndTypeIDsFromPath(self, gender, assetPath):
        if self.assetsToIDs[gender] is None:
            self.assetsToIDs[gender] = {}
            for row in cfg.paperdollResources:
                if row.resGender == gender == paperDoll.GENDER.MALE:
                    self.assetsToIDs[gender][row.resPath.lower()] = (row.paperdollResourceID, row.typeID)

        assetPath = assetPath.lower()
        if assetPath in self.assetsToIDs[gender]:
            return self.assetsToIDs[gender][assetPath]
        else:
            self.LogError('Asset ID', assetPath, 'does not have an associated ID!!')
            return (None, None)



    def GetCharacterAppearanceInfo(self, charID):
        dollDNA = self.characters[charID].doll.GetDNA()
        return paperDoll.ConvertDNAForDB(dollDNA, self.characterMetadata[charID])



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetDNAFromDBRowsForEntity(self, entityID, dollDNA, gender, bloodline):
        self.ApplyDBRowToDoll(entityID, gender, bloodline, dollDNA)
        doll = self.GetSingleCharactersDoll(entityID)
        dna = doll.GetDNA()
        del self.characters[entityID]
        del self.characterMetadata[entityID]
        return dna



    def ConvertWeightKeyValue(self, weight, prefix, posName, negName):
        if prefix in ('thin', 'fat', 'muscular'):
            fmt = '%(prefix)sshape'
        else:
            fmt = '%(prefix)s_%(dir)sshape'
        if weight < 0.0:
            key = fmt % {'prefix': prefix,
             'dir': negName}
            return (key, abs(weight))
        if weight > 0.0:
            key = fmt % {'prefix': prefix,
             'dir': posName}
            return (key, abs(weight))
        return (None, None)



    def CachePortraitInfo(self, charID, info):
        self.cachedPortraitInfo[charID] = info



    def GetCachedPortraitInfo(self, charID):
        return self.cachedPortraitInfo.get(charID, None)



    def EnsureUnderwear(self, charID, genderID, bloodlineID):
        doll = self.GetSingleCharactersDoll(charID)
        bottomUnderwearCount = len(doll.buildDataManager.GetModifiersByCategory(paperDoll.BODY_CATEGORIES.BOTTOMUNDERWEAR))
        if bottomUnderwearCount == 0:
            bottomUnderwearTypes = self.GetAvailableTypesByCategory(ccConst.bottomunderwear, genderID, bloodlineID)
            if doll.gender == paperDoll.GENDER.FEMALE:
                topUnderwearTypes = self.GetAvailableTypesByCategory(ccConst.topunderwear, genderID, bloodlineID)
            if len(bottomUnderwearTypes) > 0:
                self.ApplyTypeToDoll(charID, bottomUnderwearTypes[0], doUpdate=False)
            if doll.gender == paperDoll.GENDER.FEMALE and len(topUnderwearTypes) > 0:
                self.ApplyTypeToDoll(charID, topUnderwearTypes[0], doUpdate=False)



    @bluepy.CCP_STATS_ZONE_METHOD
    def ApplyDBRowToDoll(self, charID, gender, bloodlineID, dbRow):
        if charID not in self.characters:
            randomDoll = paperDollUtil.CreateRandomDollNoClothes(gender, bloodlineID, noRandomize=True)
            self.characters[charID] = util.KeyVal(doll=randomDoll, avatar=None)
            self.characterMetadata[charID] = self.GetNewCharacterMetadata(ccUtil.PaperDollGenderToGenderID(gender), bloodlineID)
        sculptLocations = cfg.paperdollSculptingLocations
        modifierLocations = cfg.paperdollModifierLocations
        colors = cfg.paperdollColors
        colorNames = cfg.paperdollColorNames
        resources = cfg.paperdollResources
        if dbRow is None:
            self.LogWarn('Not applying anything to paperdoll, since dbRow is None')
            return 
        self.characterMetadata[charID].appearanceID = dbRow.appearance.appearanceID
        for sculptRow in dbRow.sculpts:
            sculptInto = sculptLocations.GetIfExists(sculptRow.sculptLocationID)
            if sculptInto is None:
                self.LogError('Sculpting information for ', sculptRow.sculptLocationID, 'is missing from BSD, skipping sculpting location.')
                continue
            for (colName, posName, negName,) in WEIGHT_BREAK_DOWNS:
                (k, v,) = self.ConvertWeightKeyValue(getattr(sculptRow, colName, 0.0), sculptInto.weightKeyPrefix, posName, negName)
                if k is not None and v is not None:
                    catName = sculptInto.weightKeyCategory.lower()
                    path = paperDoll.SEPERATOR_CHAR.join([catName, k])
                    self.ApplyItemToDoll(charID, catName, k, doUpdate=False)
                    self.SetWeightByCategory(charID, path, v, doUpdate=False)


        modifierWeights = {}
        for colorRow in dbRow.colors:
            colorInfo = colors.GetIfExists(colorRow.colorID)
            if colorInfo is None:
                self.LogError('Color info missing for  ', colorRow.colorID)
                continue
            if colorInfo.hasWeight:
                modifierWeights[colorInfo.colorKey] = colorRow.weight

        modifierObjects = {}
        for modifierRow in dbRow.modifiers:
            modifierInfo = modifierLocations.GetIfExists(modifierRow.modifierLocationID)
            resourcesInfo = resources.GetIfExists(modifierRow.paperdollResourceID)
            if modifierInfo is None or resourcesInfo is None:
                self.LogError('Modifier or resource information missing for ', modifierRow.modifierLocationID, modifierRow.paperdollResourceID)
                continue
            weight = modifierWeights.get(modifierInfo.modifierKey, 1.0)
            if modifierRow.paperdollResourceVariation != 0 and modifierInfo.variationKey != '':
                self.ApplyItemToDoll(charID, modifierInfo.variationKey, self.tuckingOptions[modifierInfo.variationKey], removeFirst=True, variation='v%d' % modifierRow.paperdollResourceVariation, doUpdate=False)
            modifierObjects[modifierInfo.modifierKey] = self.ApplyTypeToDoll(charID, resourcesInfo.resPath, weight=weight, doUpdate=False)

        genderID = ccUtil.PaperDollGenderToGenderID(gender)
        self.EnsureUnderwear(charID, genderID, bloodlineID)
        for colorRow in dbRow.colors:
            colorInfo = colors.GetIfExists(colorRow.colorID)
            if colorInfo is None:
                self.LogError('No color info for ', colorRow.colorID)
                continue
            colorNameInfo = colorNames.GetIfExists(colorRow.colorNameA)
            if colorNameInfo is None:
                self.LogError('colorA index not in BSD data ', colorRow.colorNameA)
                continue
            colorNameA = colorNameInfo.colorName
            colorNameBC = None
            if colorRow.colorNameBC != 0:
                colorNameInfo = colorNames.GetIfExists(colorRow.colorNameBC)
                if colorNameInfo is not None:
                    colorNameBC = colorNameInfo.colorName
                else:
                    self.LogError('colorBC index not in BSD data ', colorRow.colorNameBC)
            if colorInfo.colorKey == ccConst.skintone:
                mod = self.ApplyItemToDoll(charID, ccConst.skintone, 'basic', doUpdate=False)
                skinColor = (colorNameA, mod.colorVariations[colorNameA])
                self.SetColorValueByCategory(charID, ccConst.skintone, skinColor, None, doUpdate=False)
            elif colorInfo.colorKey not in modifierObjects:
                self.LogError('%s not in modifierObjects' % colorInfo.colorKey)
                continue
            mod = modifierObjects[colorInfo.colorKey]
            if colorNameA not in mod.colorVariations:
                colorVarA = ('default', mod.colorVariations.get('default', None))
            else:
                colorVarA = (colorNameA, mod.colorVariations[colorNameA])
            colorVarBC = None
            if colorInfo.hasSecondary and colorNameBC is not None:
                colorVarBC = (colorNameBC, mod.colorVariations.get(colorNameBC, None))
            self.SetColorValueByCategory(charID, colorInfo.colorKey, colorVarA, colorVarBC, doUpdate=False)
            if colorInfo.hasGloss:
                self.SetColorSpecularityByCategory(charID, colorInfo.colorKey, colorRow.gloss, doUpdate=False)
            if colorInfo.colorKey == ccConst.hair:
                self.SetHairDarkness(charID, dbRow.appearance.hairDarkness)
                self.SynchronizeHairColors(charID)





