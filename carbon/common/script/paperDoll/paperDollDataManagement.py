import uthread
import copy
import yaml
import types
import hashlib
import blue
import paperDoll as PD
import bluepy
import log
import sys

class YamlPreloader():
    __guid__ = 'paperDoll.YamlPreloader'
    instance = None

    @staticmethod
    def YamlPreloaderPDFilter(yamlStr):
        yamlStr = yamlStr.replace('AvatarFactory.paperDollDataManagement.', 'paperDoll.')
        yamlStr = yamlStr.replace('AvatarFactory.', '')
        yamlStr = yamlStr.replace('tattoo.', 'paperDoll.')
        return yamlStr



    def __init__(self, verbose = False):
        self.cache = {}
        self.verbose = verbose



    def Preload(self, rootFolder, extensions = None, yamlFilter = None):
        extensions = extensions or ['.yaml']
        yamlFiles = []
        blue.statistics.EnterZone('YamlPreloader.FolderScan')
        for (root, dirs, files,) in bluepy.walk(rootFolder):
            for f in files:
                ext = f[f.rfind('.'):].lower()
                if ext in extensions:
                    yamlFiles.append(root + '/' + f)

            blue.synchro.Yield()

        blue.statistics.LeaveZone('YamlPreloader.FolderScan')
        sys.modules[PD.__name__] = PD
        blue.statistics.EnterZone('YamlPreloader.YamlLoad')
        r = blue.ResFile()
        for (i, path,) in enumerate(yamlFiles):
            if i % 10 == 0:
                blue.synchro.Yield()
                sys.modules[PD.__name__] = PD
            r.Open(path)
            try:
                yamlStr = r.Read()

            finally:
                r.Close()

            if yamlFilter is not None:
                yamlStr = yamlFilter(yamlStr)
            try:
                instance = yaml.load(yamlStr, Loader=yaml.CLoader)
                if instance is not None:
                    self.cache[str(path).lower()] = instance
            except:
                log.LogError('paperDoll::YamlPreloader::Preload - Failed loading yaml for path: {0}'.format(path))

        if PD.__name__ in sys.modules:
            del sys.modules[PD.__name__]
        blue.statistics.LeaveZone('YamlPreloader.YamlLoad')
        log.LogInfo('YamlPreloader:', len(yamlFiles), 'yaml files preloaded from', rootFolder)



    def LoadYaml(self, yamlPath):
        yamlData = self.cache.get(yamlPath.lower(), None)
        if yamlData is None:
            if self.verbose:
                log.LogInfo('Yaml cache miss for', yamlPath)
            return PD.LoadYamlFileNicely(yamlPath, enableCache=False)
        if self.verbose:
            log.LogInfo('Yaml cache hit for', yamlPath)
        return copy.deepcopy(yamlData)




def LoadYamlFileNicely(pathToFile, enableCache = True):
    if enableCache and YamlPreloader.instance is not None:
        return YamlPreloader.instance.LoadYaml(pathToFile)
    blue.pyos.BeNice()
    r = blue.ResFile()
    if r.FileExists(pathToFile):
        try:
            r.Open(pathToFile)
            yamlStr = r.Read()

        finally:
            r.Close()

        log.LogInfo('Parsing data from {0}'.format(pathToFile))
        inst = PD.NastyYamlLoad(yamlStr)
        if not inst:
            log.LogError('PaperDoll: Yaml file corrupt: ', pathToFile)
        return inst



class AvatarPartMetaData(object):
    __guid__ = 'paperDoll.AvatarPartMetaData'

    def __init__(self):
        self.dependantModifiers = []
        self.occludesModifiers = []
        self.numColorAreas = 3
        self.forcesLooseTop = False
        self.hidesBootShin = False
        self.alternativeTextureSourcePath = ''
        self.soundTag = ''
        self.defaultMetaData = True



    def __hash__(self):
        t = []
        keys = self.__dict__.keys()
        for key in keys:
            x = self.__dict__[key]
            if type(x) is types.ListType:
                x = tuple(x)
            t.append(x)

        t.sort()
        t = tuple(t)
        return hash(t)



    @staticmethod
    def Load(yamlStr):
        instance = LoadYamlFileNicely(yamlStr)
        t = PD.AvatarPartMetaData()
        for key in t.__dict__.keys():
            if key not in instance.__dict__.keys():
                instance.__dict__[key] = t.__dict__[key]

        return instance



    @staticmethod
    def FillInDefaults(instance):
        t = PD.AvatarPartMetaData()
        for key in t.__dict__.keys():
            if key not in instance.__dict__.keys():
                instance.__dict__[key] = t.__dict__[key]

        dmLen = len(instance.dependantModifiers)
        for i in xrange(dmLen):
            instance.dependantModifiers[i] = instance.dependantModifiers[i].lower()

        instance.alternativeTextureSourcePath = instance.alternativeTextureSourcePath.lower()
        return instance




class ModifierLoader():
    __guid__ = 'paperDoll.ModifierLoader'
    _ModifierLoader__sharedLoadSource = False
    _ModifierLoader__sharedMaleOptions = None
    _ModifierLoader__sharedFemaleOptions = None

    def setclothSimulationActive(self, value):
        self._clothSimulationActive = value


    clothSimulationActive = property(fget=lambda self: self._clothSimulationActive, fset=lambda self, value: self.setclothSimulationActive(value))

    def __init__(self):
        self.yamlCache = {}
        self.patterns = []
        self.maleOptions = {}
        self.femaleOptions = {}
        self.IsLoaded = False
        self.forceRunTimeOptionGeneration = False
        self._clothSimulationActive = False
        self.preloadToYamlCache = False
        uthread.new(self.LoadData_t)



    def DebugReload(self, forceRunTime = False):
        self.forceRunTimeOptionGeneration = forceRunTime
        ModifierLoader._ModifierLoader__sharedLoadSource = False
        ModifierLoader._ModifierLoader__sharedMaleOptions = None
        ModifierLoader._ModifierLoader__sharedFemaleOptions = None
        uthread.new(self.LoadData_t)



    @staticmethod
    @bluepy.CCP_STATS_ZONE_FUNCTION
    def LoadBlendshapeLimits(limitsResPath):
        data = LoadYamlFileNicely(limitsResPath)
        if data is not None:
            limits = data.get('limits')
            ret = {}
            if limits and type(limits) is dict:
                for (k, v,) in limits.iteritems():
                    ret[k.lower()] = v

                data['limits'] = ret
        return data



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetWorkingDirectory(self, gender):
        if gender == PD.GENDER.FEMALE:
            return PD.FEMALE_BASE_PATH
        else:
            return PD.MALE_BASE_PATH



    @bluepy.CCP_STATS_ZONE_METHOD
    def LoadData_t(self):
        self._LoadOptions()
        if self.preloadToYamlCache:
            self._PreloadToYamlCache()
        self._LoadPatterns()
        self.IsLoaded = True



    @bluepy.CCP_STATS_ZONE_METHOD
    def WaitUntilLoaded(self):
        while not self.IsLoaded:
            blue.synchro.Yield()




    @bluepy.CCP_STATS_ZONE_METHOD
    def _LoadPatterns(self):
        if blue.rot.loadFromContent:
            self.patterns = PD.GetPatternList()
        elif PD.GENDER_ROOT:
            optionsFile = 'res:/{0}/Character/PatternOptions.yaml'.format(PD.BASE_GRAPHICS_FOLDER)
        else:
            optionsFile = 'res:/{0}/Character/Modular/PatternOptions.yaml'.format(PD.BASE_GRAPHICS_FOLDER)
        self.patterns = LoadYamlFileNicely(optionsFile)



    @bluepy.CCP_STATS_ZONE_METHOD
    def _PreloadToYamlCache(self):

        def PreloadFromOptions(options):
            for key in options:
                for each in options[key]:
                    blue.pyos.BeNice()
                    if each.endswith('.color'):
                        entry = LoadYamlFileNicely(each)
                        self._ModifierLoader__AddToYamlCache(each, entry)
                    elif each.endswith('.pose'):
                        entry = LoadYamlFileNicely(each)
                        self._ModifierLoader__AddToYamlCache(each, entry)
                    elif each.endswith('.proj'):
                        entry = PD.ProjectedDecals.Load(each)
                        self._ModifierLoader__AddToYamlCache(each, entry)
                    elif each.endswith('.yaml'):
                        entry = LoadYamlFileNicely(each)
                        entry = PD.AvatarPartMetaData.FillInDefaults(entry)
                        entry.defaultMetaData = False
                        self._ModifierLoader__AddToYamlCache(each, entry)




        PreloadFromOptions(self.maleOptions)
        PreloadFromOptions(self.femaleOptions)



    @bluepy.CCP_STATS_ZONE_METHOD
    def _LoadOptions(self):
        if ModifierLoader._ModifierLoader__sharedLoadSource == blue.rot.loadFromContent and ModifierLoader._ModifierLoader__sharedMaleOptions and ModifierLoader._ModifierLoader__sharedFemaleOptions:
            self.maleOptions = ModifierLoader._ModifierLoader__sharedMaleOptions
            self.femaleOptions = ModifierLoader._ModifierLoader__sharedFemaleOptions
            return 

        def LoadOptionYamlFiles():
            self.maleOptions = LoadYamlFileNicely(PD.MALE_OPTION_FILE_PATH)
            self.femaleOptions = LoadYamlFileNicely(PD.FEMALE_OPTION_FILE_PATH)



        def RunTimeOptionGeneration():
            import os
            if os.path.exists(PD.OUTSOURCING_JESSICA_PATH):
                LoadOptionYamlFiles()
            else:
                self.femaleOptions = {}
                self.maleOptions = {}

            def LoadPathToOptions(path, options):
                entries = PD.CreateEntries(path)
                for entry in entries.iteritems():
                    options[entry[0]] = entry[1]

                PD.AddBlendshapeEntries(path + '/head', options, PD.BLENDSHAPE_CATEGORIES.FACEMODIFIERS)
                PD.AddBlendshapeEntries(path + '/bottomOuter', options, PD.BLENDSHAPE_CATEGORIES.BODYSHAPES)


            LoadPathToOptions(PD.FEMALE_BASE_PATH, self.femaleOptions)
            LoadPathToOptions(PD.MALE_BASE_PATH, self.maleOptions)
            LoadPathToOptions(PD.FEMALE_BASE_PATH.replace('Modular', PD.MODULAR_TEST_CASES_FOLDER), self.femaleOptions)
            LoadPathToOptions(PD.MALE_BASE_PATH.replace('Modular', PD.MODULAR_TEST_CASES_FOLDER), self.maleOptions)


        if blue.rot.loadFromContent or self.forceRunTimeOptionGeneration:
            RunTimeOptionGeneration()
        else:
            LoadOptionYamlFiles()
        ModifierLoader._ModifierLoader__sharedLoadSource = blue.rot.loadFromContent
        ModifierLoader._ModifierLoader__sharedMaleOptions = self.maleOptions
        ModifierLoader._ModifierLoader__sharedFemaleOptions = self.femaleOptions



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetOptionsByGender(self, gender):
        options = dict()
        if gender == PD.GENDER.FEMALE:
            options = self.femaleOptions
        elif gender == PD.GENDER.MALE:
            options = self.maleOptions
        return options



    def GetPatternDir(self):
        return 'res:/{0}/Character/Patterns'.format(PD.BASE_GRAPHICS_FOLDER)



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetItemType(self, itemTypePath):
        itemType = self._ModifierLoader__GetFromYamlCache(itemTypePath)
        if itemType is None:
            itemType = LoadYamlFileNicely(itemTypePath)
            self._ModifierLoader__AddToYamlCache(itemTypePath, itemType)
        return itemType



    def ListTypes(self, gender, cat = '', modifier = None):
        options = self.GetOptionsByGender(gender)
        data = self.ListOptions(gender, cat, showVariations=False)
        availableTypes = []
        for optionName in data:
            elems = options.get(cat + PD.SEPERATOR_CHAR + optionName + PD.SEPERATOR_CHAR + 'types')
            if elems:
                if modifier:
                    for elem in iter(elems):
                        if modifier.name.lower() in elem.lower():
                            availableTypes.append(elem)

                else:
                    availableTypes.extend(elems)

        return availableTypes



    def CategoryHasTypes(self, category):

        def CheckTypes(gender):
            options = self.GetOptionsByGender(gender)
            data = self.ListOptions(gender, category, showVariations=False)
            for optionName in data:
                elems = options.get(category + PD.SEPERATOR_CHAR + optionName + PD.SEPERATOR_CHAR + 'types')
                if elems:
                    return True

            return False


        return CheckTypes('female') or CheckTypes('male')



    @bluepy.CCP_STATS_ZONE_METHOD
    def ListOptions(self, gender, cat = '', showVariations = False):
        ret = {}
        variations = [ 'v%s' % x for x in xrange(99) ]

        def funC(each):
            if each.startswith(cat.lower() + PD.SEPERATOR_CHAR):
                allitems = each[(len(cat) + 1):].split(PD.SEPERATOR_CHAR)
                label = allitems[0]
                if label:
                    ret[label] = ret.get(label, [])
                    if showVariations:
                        if len(allitems) > 1:
                            if allitems[1] in variations:
                                ret[label].append(allitems[1])



        def fun(each):
            entries = each.split(PD.SEPERATOR_CHAR)
            label = entries[0] + PD.SEPERATOR_CHAR + entries[1]
            if len(entries) > 2 and entries[2] not in variations:
                label += PD.SEPERATOR_CHAR + entries[2]
            ret[label] = ''


        options = self.GetOptionsByGender(gender)
        if not options:
            log.LogError('PaperDoll - No options for gender: {0} available in ModifierLoader::ListOptions'.format(gender))
        else:
            f = funC if cat else fun
            for each in options.iterkeys():
                f(each)

        if cat and showVariations:
            ret = [ (key, tuple(ret[key])) for key in ret ]
        else:
            ret = ret.keys()
        ret.sort()
        return ret



    @bluepy.CCP_STATS_ZONE_METHOD
    def CollectBuildData(self, path, options, weight = 1.0):
        currentBuildData = PD.BuildData(path)
        currentBuildData.weight = weight
        self.LoadResource(path, options, currentBuildData)
        return currentBuildData



    @bluepy.CCP_STATS_ZONE_METHOD
    def LoadResource(self, path, options, modifier):
        if options is None:
            log.LogError('PaperDoll - NoneType passed as options to ModifierLoader::LoadResource!')
            return 
        if not options:
            log.LogWarn('PaperDoll - Empty options passed to ModifierLoader::LoadResource!')
            return 
        if path not in options:
            log.LogWarn('PaperDoll - Path {0} does not exist in the options passed to ModifierLoader::LoadResource!'.format(path))
            return 
        while not self.IsLoaded:
            blue.pyos.BeNice()

        self._ModifierLoader__GetFilesForEntry(options, modifier, path)
        modName = path.split('/')[-1]
        colorsPath = path.replace(modName, 'colors')
        if colorsPath in options.keys():
            self._ModifierLoader__GetFilesForEntry(options, modifier, colorsPath)
        path = path + '/v'
        matchingVariationPaths = [ key for key in options.keys() if key.startswith(path) ]
        for variationPath in iter(matchingVariationPaths):
            variationBd = PD.BuildData()
            self._ModifierLoader__GetFilesForEntry(options, variationBd, variationPath)
            modifier.variations[variationPath.split('/')[-1]] = variationBd

        if len(modifier.variations):
            original = copy.deepcopy(modifier)
            original.variations = {}
            modifier.variations['v0'] = original
        if 'default' in modifier.colorVariations:
            modifier.SetColorVariation('default')
        if modifier.metaData.alternativeTextureSourcePath:
            self._ModifierLoader__GetFilesForEntry(options, modifier, modifier.metaData.alternativeTextureSourcePath.lower(), sourceMapsOnly=True)



    @bluepy.CCP_STATS_ZONE_METHOD
    def __GetFromYamlCache(self, key):
        inst = self.yamlCache.get(key)
        if inst is not None:
            return copy.deepcopy(inst)



    def __AddToYamlCache(self, key, value):
        self.yamlCache[key] = value



    @bluepy.CCP_STATS_ZONE_METHOD
    def __PartFromPath(self, path, reverseLookupData = None, rvPart = None):
        pathLower = path.lower()
        for part in PD.DOLL_PARTS:
            if part.lower() in pathLower:
                return str(part)

        if '_acc_' in pathLower:
            return str(PD.DOLL_PARTS.ACCESSORIES)
        if reverseLookupData:
            for part in iter(reverseLookupData):
                if part.lower() in pathLower:
                    return str(rvPart)

        return ''



    @bluepy.CCP_STATS_ZONE_METHOD
    def __GetFilesForEntry(self, options, buildData, path, sourceMapsOnly = False):
        items = options.get(path, [])
        for each in iter(items):
            blue.pyos.BeNice()
            resPath = str(each).lower()
            each = resPath.split('/')[-1]
            each_endswith = each.endswith
            if each_endswith('.dds') and not PD.USE_PNG or each_endswith('.tga') or each_endswith('.png') and PD.USE_PNG:
                base = each.split('.')[-2]
                base_endswith = base.endswith
                partType = self._ModifierLoader__PartFromPath(base) or self._ModifierLoader__PartFromPath(resPath, PD.BODY_CATEGORIES, PD.DOLL_PARTS.BODY)
                if 'colorize_' in base:
                    buildData.colorize = True
                if base_endswith('_l'):
                    buildData.mapL[partType] = resPath
                elif base_endswith('_z'):
                    buildData.mapZ[partType] = resPath
                if base_endswith('_o'):
                    buildData.mapO[partType] = resPath
                elif base_endswith('_d'):
                    buildData.mapD[partType] = resPath
                elif base_endswith('_n'):
                    buildData.mapN[partType] = resPath
                if base_endswith('_mn'):
                    buildData.mapMN[partType] = resPath
                elif base_endswith('_tn'):
                    buildData.mapTN[partType] = resPath
                elif base_endswith('_s'):
                    buildData.mapSRG[partType] = resPath
                if base_endswith('_ao'):
                    buildData.mapAO[partType] = resPath
                elif base_endswith('_mask') or base_endswith('_m'):
                    buildData.mapMask[partType] = resPath
                    buildData.mapAO[partType] = resPath
                elif base_endswith('_mm'):
                    buildData.mapMaterial[partType] = resPath
            if not sourceMapsOnly and each_endswith('.red') and '_hood' not in each and '_hat' not in each:
                if each_endswith('_physx.red'):
                    buildData.clothPath = resPath
                    continue
                if each_endswith('_nosim.red'):
                    buildData.clothOverride = resPath
                    continue
                if each_endswith('stubble.red'):
                    buildData.stubblePath = resPath
                    buildData.colorize = True
                    continue
                if '_physx_lod' in each:
                    continue
                if each_endswith('_shader.red'):
                    buildData.shaderPath = resPath
                    continue
                buildData.redfile = resPath
            if not sourceMapsOnly and each_endswith('.yaml'):
                inst = self._ModifierLoader__GetFromYamlCache(resPath)
                if inst is None:
                    inst = LoadYamlFileNicely(resPath)
                    if inst is not None:
                        PD.AvatarPartMetaData.FillInDefaults(inst)
                        inst.defaultMetaData = False
                        self._ModifierLoader__AddToYamlCache(resPath, inst)
                if inst:
                    buildData.metaData = inst
            if not sourceMapsOnly and each_endswith('.pose'):
                inst = self._ModifierLoader__GetFromYamlCache(resPath)
                if inst is None:
                    inst = LoadYamlFileNicely(resPath)
                    if inst is not None:
                        self._ModifierLoader__AddToYamlCache(resPath, inst)
                buildData.poseData = inst
            if not sourceMapsOnly and each_endswith('.color'):
                inst = self._ModifierLoader__GetFromYamlCache(resPath)
                if inst is None:
                    inst = LoadYamlFileNicely(resPath)
                    if inst is not None:
                        self._ModifierLoader__AddToYamlCache(resPath, inst)
                varName = each.split('/')[-1].split('.')[0]
                buildData.colorVariations[varName] = inst
            if not sourceMapsOnly and each_endswith('.proj'):
                inst = self._ModifierLoader__GetFromYamlCache(resPath)
                if inst is None:
                    inst = PD.ProjectedDecal.Load(resPath)
                    if inst is not None:
                        self._ModifierLoader__AddToYamlCache(resPath, inst)
                inst.SetTexturePath(inst.texturePath)
                inst.SetMaskPath(inst.maskPath)
                buildData.decalData = inst





class BuildData(object):
    __metaclass__ = bluepy.CCP_STATS_ZONE_PER_METHOD
    __guid__ = 'paperDoll.BuildData'
    DEFAULT_COLORIZEDATA = [PD.MID_GRAY] * 3
    DEFAULT_PATTERNDATA = [PD.DARK_GRAY,
     PD.LIGHT_GRAY,
     PD.MID_GRAY,
     PD.MID_GRAY,
     PD.MID_GRAY,
     (0, 0, 8, 8),
     0.0]
    DEFAULT_SPECULARCOLORDATA = [PD.MID_GRAY] * 3

    def __del__(self):
        self.ClearCachedData()



    def __init__(self, pathName = None, name = None, categorie = None):
        object.__init__(self)
        self.name = ''
        self.categorie = categorie.lower() if categorie else ''
        extPath = None
        splits = None
        if pathName is not None:
            pathName = pathName.lower()
            splits = pathName.split(PD.SEPERATOR_CHAR)
            extPath = str(PD.SEPERATOR_CHAR.join(splits[1:]))
            self.categorie = str(splits[0])
        self.name = name.lower() if name else extPath
        if self.categorie and self.name:
            self.respath = self.categorie + PD.SEPERATOR_CHAR + self.name
        else:
            self.respath = ''
        if splits and len(splits) > 2:
            self.group = splits[1]
        else:
            self.group = ''
        self._BuildData__blendData = {}
        self.blendRes = None
        self.usingMaskedShader = False
        self.redfile = ''
        self.clothPath = ''
        self.clothOverride = ''
        self.meshes = []
        self.meshGeometryResPaths = {}
        self.dependantModifiers = {}
        self._BuildData__cmpMeshes = []
        self.clothData = None
        self.stubblePath = ''
        self.shaderPath = ''
        self.drapePath = ''
        self.decalData = None
        self.mapN = {}
        self.mapMN = {}
        self.mapTN = {}
        self.mapSRG = {}
        self.mapAO = {}
        self.mapMaterial = {}
        self.mapMask = {}
        self.mapD = {}
        self.mapL = {}
        self.mapZ = {}
        self.mapO = {}
        self.colorize = False
        self._colorizeData = list(BuildData.DEFAULT_COLORIZEDATA)
        self._BuildData__cmpColorizeData = []
        self._BuildData__pattern = ''
        self.patternData = list(BuildData.DEFAULT_PATTERNDATA)
        self._BuildData__cmpPatternData = []
        self.specularColorData = list(BuildData.DEFAULT_SPECULARCOLORDATA)
        self._BuildData__cmpSpecularColorData = []
        self.colorVariations = {}
        self.currentColorVariation = ''
        self.variations = {}
        self.variationTextureHash = ''
        self.currentVariation = ''
        self.lastVariation = ''
        self._BuildData__weight = 1.0
        self._BuildData__useSkin = False
        self.metaData = AvatarPartMetaData()
        self.poseData = None
        self._BuildData__tuck = True
        self.ulUVs = (PD.DEFAULT_UVS[0], PD.DEFAULT_UVS[1])
        self.lrUVs = (PD.DEFAULT_UVS[2], PD.DEFAULT_UVS[3])
        self._BuildData__IsHidden = False
        self.WasHidden = False
        self._BuildData__IsDirty = True
        self._BuildData__hashValue = None
        self._isTextureContainingModifier = None
        self._contributesToMapTypes = None
        self._affectedTextureParts = None



    def GetUVsForCompositing(self, bodyPart):
        if bodyPart != PD.DOLL_PARTS.ACCESSORIES:
            if bodyPart == PD.DOLL_PARTS.BODY:
                UVs = PD.BODY_UVS
            elif bodyPart == PD.DOLL_PARTS.HEAD:
                UVs = PD.HEAD_UVS
            elif bodyPart == PD.DOLL_PARTS.HAIR:
                UVs = PD.HAIR_UVS
        else:
            accUVs = PD.ACCE_UVS
            width = accUVs[2] - accUVs[0]
            height = accUVs[3] - accUVs[1]
            UVs = list((accUVs[0] + self.ulUVs[0] * width, accUVs[1] + self.ulUVs[1] * height) + (accUVs[0] + self.lrUVs[0] * width, accUVs[1] + self.lrUVs[1] * height))
        return UVs



    def IsSimilarTo(self, modifier):
        return self.name == modifier.name and self.categorie == modifier.categorie and self.respath == modifier.respath



    def MorphTo(self, modifier):
        self.SetVariation(modifier.currentVariation)
        self.SetColorVariation(modifier.currentColorVariation)
        self.colorizeData = list(modifier.colorizeData)
        self._BuildData__dirty = True



    def SetColorizeData(self, *args):
        x = args
        depth = 0
        while len(x) == 1 and type(x[0]) in (tuple, list) and depth < 5:
            x = x[0]
            depth += 1

        didChange = False
        for i in xrange(len(x)):
            if len(x) > i and type(x[i]) in (tuple, list):
                if self._colorizeData[i] != tuple(x[i]):
                    self._colorizeData[i] = tuple(x[i])
                    didChange = True

        if didChange:
            self.IsDirty = True



    def GetColorizeData(self):
        return self._colorizeData



    def GetColorVariations(self):
        return self.colorVariations.keys()



    def SetColorVariation(self, variationName):
        if variationName == 'none':
            self.currentColorVariation = 'none'
            return 
        if not self.currentColorVariation == 'none' and self.colorVariations and variationName in self.colorVariations:
            currentColorVariation = self.colorVariations[variationName]
            if not currentColorVariation:
                return 
            if 'colors' in currentColorVariation:
                for i in xrange(3):
                    self.colorizeData[i] = currentColorVariation['colors'][i]

            if 'pattern' in currentColorVariation:
                self.pattern = currentColorVariation['pattern']
            if 'patternColors' in currentColorVariation:
                arrayLength = len(currentColorVariation['patternColors'])
                for i in xrange(arrayLength):
                    self.patternData[i] = currentColorVariation['patternColors'][i]

            if 'specularColors' in currentColorVariation:
                for i in xrange(3):
                    self.specularColorData[i] = currentColorVariation['specularColors'][i]

            self.currentColorVariation = str(variationName)



    def SetColorVariationDirectly(self, variation):
        if variation is not None and type(variation) is types.DictionaryType:
            if 'colors' in variation:
                for i in xrange(3):
                    self.colorizeData[i] = variation['colors'][i]

            if 'pattern' in variation:
                self.pattern = variation['pattern']
            if 'patternColors' in variation:
                for i in xrange(5):
                    self.patternData[i] = variation['patternColors'][i]

            if 'specularColors' in variation:
                for i in xrange(3):
                    self.specularColorData[i] = variation['specularColors'][i]




    def SetColorVariationSpecularity(self, specularColor):
        self.specularColorData = specularColor



    def GetColorsFromColorVariation(self, variationName):
        if self.colorVariations and self.colorVariations.get(variationName):
            var = self.colorVariations[variationName]
            if var['pattern'] != '':
                return [var['patternColors'][0], var['patternColors'][3], var['patternColors'][4]]
            else:
                return var['colors']



    def GetVariations(self):
        return self.variations.keys()



    def SetVariation(self, variationName):
        variationName = variationName or 'v0'
        if self.variations and variationName in self.variations:
            oldRedFile = self.redfile
            oldClothPath = self.clothPath
            var = self.variations[variationName]
            doNotCopy = ['respath', 'dependantModifiers']
            for member in var.__dict__:
                if member not in doNotCopy:
                    if type(var.__dict__[member]) == str and var.__dict__[member]:
                        self.__dict__[member] = var.__dict__[member]
                    if type(var.__dict__[member]) == dict and len(var.__dict__[member]) > 0:
                        for entry in var.__dict__[member]:
                            self.__dict__[member][entry] = var.__dict__[member][entry]
                            if member.startswith('map'):
                                self.variationTextureHash = var.__dict__[member][entry]

                    if member == 'metaData':
                        if var.metaData and not var.metaData.defaultMetaData:
                            self.metaData = var.metaData

            if oldRedFile != self.redfile or oldClothPath != self.clothPath:
                del self.meshes[:]
                self.clothData = None
                self.meshGeometryResPaths = {}
            self.lastVariation = self.currentVariation
            self.currentVariation = str(variationName)



    def GetVariationMetaData(self, variationName = None):
        if variationName == '':
            variationName = 'v0'
        variationName = variationName or self.currentVariation
        variation = self.variations.get(variationName)
        if variation and variation.metaData and not variation.metaData.defaultMetaData:
            return variation.metaData



    def IsTextureContainingModifier(self):
        if self._isTextureContainingModifier is None:
            self._isTextureContainingModifier = False
            for each in self.__dict__.iterkeys():
                if each.startswith('map'):
                    if self.__dict__[each]:
                        self._isTextureContainingModifier = True
                        break

        return self._isTextureContainingModifier



    def ContributesToMapTypes(self):
        if self._contributesToMapTypes is None:
            mapTypes = list()
            if len(self.mapD.keys()) > 0 or len(self.mapL.keys()) > 0 or len(self.mapZ.keys()) > 0 or len(self.mapO.keys()) > 0:
                mapTypes.append(PD.DIFFUSE_MAP)
            if len(self.mapSRG.keys()) > 0 or len(self.mapAO.keys()) > 0 or len(self.mapMaterial.keys()) > 0:
                mapTypes.append(PD.SPECULAR_MAP)
            if len(self.mapN.keys()) > 0 or len(self.mapMN.keys()) > 0 or len(self.mapTN.keys()) > 0:
                mapTypes.append(PD.NORMAL_MAP)
            if len(self.mapMask.keys()) > 0:
                mapTypes.append(PD.MASK_MAP)
            self._contributesToMapTypes = mapTypes
        return self._contributesToMapTypes



    def GetAffectedTextureParts(self):
        if self._affectedTextureParts is None:
            parts = set()
            for each in self.__dict__.iterkeys():
                if each.startswith('map'):
                    parts.update(self.__dict__[each].keys())

            self._affectedTextureParts = parts
        return self._affectedTextureParts



    def GetDependantModifiersFullData(self):
        if self.metaData.dependantModifiers:
            parsedValues = []
            for each in self.metaData.dependantModifiers:
                if '#' in each:
                    tmpList = []
                    for elem in each.split('#'):
                        tmpList.append(elem)

                    while len(tmpList) < 3:
                        tmpList.append(None)

                    if len(tmpList) < 4:
                        tmpList.append(1.0)
                    else:
                        tmpList[3] = float(tmpList[3])
                    parsedValues.append(tuple(tmpList))
                else:
                    parsedValues.append((each,
                     None,
                     None,
                     1.0))

            return parsedValues



    def GetDependantModifierResPaths(self):
        if self.metaData.dependantModifiers:
            resPaths = []
            for resPath in self.metaData.dependantModifiers:
                if '#' in resPath:
                    resPaths.append(resPath.split('#')[0])
                else:
                    resPaths.append(resPath)

            return resPaths



    def GetOccludedModifiersFullData(self, metaDataOverride = None):
        if metaDataOverride:
            metaData = metaDataOverride
        else:
            metaData = self.metaData
        if metaData.occludesModifiers:
            parsedValues = []
            for each in metaData.occludesModifiers:
                if '#' in each:
                    tmpList = []
                    for elem in each.split('#'):
                        tmpList.append(elem)

                    if len(tmpList) < 2:
                        tmpList.append(1.0)
                    else:
                        tmpList[1] = float(tmpList[1])
                    parsedValues.append(tuple(tmpList))
                else:
                    parsedValues.append((each, 1.0))

            return parsedValues



    def GetDependantModifiers(self):
        return self.dependantModifiers.values()



    def AddDependantModifier(self, modifier):
        if self.respath == modifier.respath:
            raise AttributeError('paperDoll:BuildData:AddDependantModifier - Trying to add modifier as dependant of itself!')
        self.dependantModifiers[modifier.respath] = modifier



    def RemoveDependantModifier(self, modifier):
        if modifier.respath in self.dependantModifiers:
            del self.dependantModifiers[modifier.respath]



    def GetMeshSourcePaths(self):
        return [self.clothPath, self.redfile]



    def IsMeshContainingModifier(self):
        return any((self.meshes,
         self.clothData,
         self.clothPath,
         self.redfile))



    def IsBlendshapeModifier(self):
        return self.categorie in PD.BLENDSHAPE_CATEGORIES



    def __repr__(self):
        s = 'BuildData instance, ID%s\n' % id(self)
        s = s + 'Name: [%s]\t Category: [%s]\t RedFile: [%s]\n' % (self.name, self.categorie, self.redfile)
        s = s + 'Dirty: [%s]\t Hidden: [%s]\t Respath: [%s]\t' % (self.IsDirty, self.IsHidden, self.GetResPath())
        return s



    def __hash__(self):
        return id(self)



    def getIsDirty(self):
        if self._BuildData__IsDirty:
            return True
        if self.lastVariation != self.currentVariation:
            return True
        if self._BuildData__cmpPatternData != self.patternData:
            return True
        if self._BuildData__cmpColorizeData != self._colorizeData:
            return True
        if self._BuildData__cmpSpecularColorData != self.specularColorData:
            return True
        if self._BuildData__cmpMeshes != self.meshes:
            return True
        if self._BuildData__cmpDecalData != self.decalData:
            return True
        return False



    def setIsDirty(self, value):
        if value == False:
            self._BuildData__cmpColorizeData = list(self._colorizeData)
            self._BuildData__cmpSpecularColorData = list(self.specularColorData)
            self._BuildData__cmpPatternData = list(self.patternData)
            self._BuildData__cmpMeshes = list(self.meshes)
            if self.decalData is not None:
                self._BuildData__cmpDecalData = copy.deepcopy(self.decalData)
            else:
                self._BuildData__cmpDecalData = None
            self.lastVariation = self.currentVariation
            self.WasHidden = False
            self.WasShown = False
        else:
            self._BuildData__hashValue = None
            self._isTextureContainingModifier = None
            self._contributesToMapTypes = None
            self._affectedTextureParts = None
        self._BuildData__IsDirty = value


    IsDirty = property(fget=getIsDirty, fset=setIsDirty)

    def dirtDeco(fun):

        def new(*args):
            args[0]._BuildData__IsDirty = True
            return fun(*args)


        return new


    colorizeData = property(fset=SetColorizeData, fget=GetColorizeData)

    @dirtDeco
    def setisHidden(self, value):
        self.WasShown = value and not self._BuildData__IsHidden
        self.WasHidden = not value and self._BuildData__IsHidden
        self._BuildData__IsHidden = value


    IsHidden = property(fget=lambda self: self._BuildData__IsHidden, fset=setisHidden)

    @dirtDeco
    def setblendData(self, value):
        self._BuildData__blendData = value


    blendData = property(fget=lambda self: self._BuildData__blendData, fset=setblendData)

    @dirtDeco
    def settuck(self, value):
        self._BuildData__tuck = value


    tuck = property(fget=lambda self: self._BuildData__tuck, fset=settuck)

    @dirtDeco
    def setpattern(self, value):
        self._BuildData__pattern = value


    pattern = property(fget=lambda self: self._BuildData__pattern, fset=setpattern)

    @dirtDeco
    def setweight(self, value):
        self._BuildData__weight = value


    weight = property(fget=lambda self: self._BuildData__weight, fset=setweight)

    @dirtDeco
    def setuseSkin(self, value):
        self._BuildData__useSkin = value


    useSkin = property(fget=lambda self: self._BuildData__useSkin, fset=setuseSkin)

    def GetTypeData(self):
        return (self.respath, self.currentVariation, self.currentColorVariation)



    def ClearCachedData(self):
        del self.meshes[:]
        del self._BuildData__cmpMeshes[:]
        self.clothData = None
        self.meshGeometryResPaths = {}



    def GetResPath(self):
        return self.respath



    def GetFootPrint(self, preserveTypes = False, occlusionWeight = None):
        colorsOutput = self.colorizeData if preserveTypes else str(self.colorizeData)
        colorsSource = self.colorizeData
        if self.pattern:
            colorsOutput = self.patternData if preserveTypes else str(self.patternData)
            colorsSource = self.patternData
        data = {}
        data[PD.DNA_STRINGS.PATH] = self.GetResPath()
        serializationWeight = self.weight if not occlusionWeight else self.weight + occlusionWeight
        data[PD.DNA_STRINGS.WEIGHT] = serializationWeight
        data[PD.DNA_STRINGS.CATEGORY] = self.categorie
        if colorsSource != BuildData.DEFAULT_COLORIZEDATA:
            data[PD.DNA_STRINGS.COLORS] = colorsOutput
        if self.specularColorData != BuildData.DEFAULT_SPECULARCOLORDATA:
            data[PD.DNA_STRINGS.SPECULARCOLORS] = self.specularColorData
        if self.pattern:
            data[PD.DNA_STRINGS.PATTERN] = self.pattern
        if self.decalData:
            data[PD.DNA_STRINGS.DECALDATA] = self.decalData
        if self.currentColorVariation:
            data[PD.DNA_STRINGS.COLORVARIATION] = self.currentColorVariation
        if self.currentVariation:
            data[PD.DNA_STRINGS.VARIATION] = self.currentVariation
        return data



    def CompareFootPrint(self, other):
        if isinstance(other, BuildData):
            otherFP = other.GetFootPrint()
        else:
            otherFP = other

        def doCompare(sfp, ofp):
            ret = 1
            for (k, v,) in sfp.iteritems():
                if ofp.get(k) != v:
                    if k != PD.DNA_STRINGS.VARIATION:
                        return 0
                    ret = -1

            return ret


        selfFP = self.GetFootPrint(preserveTypes=True)
        cmpResult = doCompare(selfFP, otherFP)
        if cmpResult < 1:
            selfFP = self.GetFootPrint(preserveTypes=False)
            cmpResult = doCompare(selfFP, otherFP)
        return cmpResult



    def Hash(self):
        return hash(self)




class BuildDataManager(object):
    __metaclass__ = bluepy.CCP_STATS_ZONE_PER_METHOD
    __guid__ = 'paperDoll.BuildDataManager'

    def getmodifiers(self):
        if self._BuildDataManager__filterHidden:
            modifiersdata = {}
            for part in self._BuildDataManager__modifiers.iterkeys():
                modifiers = [ modifier for modifier in self._BuildDataManager__modifiers[part] if not modifier._BuildData__IsHidden ]
                modifiersdata[part] = modifiers

            return modifiersdata
        else:
            return self._BuildDataManager__modifiers



    def setmodifiers(self, value):
        raise AttributeError('Cannot directly set modifiers!')


    modifiersdata = property(fget=getmodifiers, fset=setmodifiers)

    def __del__(self):
        del self._BuildDataManager__sortedList
        del self._BuildDataManager__dirtyModifiersAdded
        del self._BuildDataManager__dirtyModifiersRemoved
        del self._BuildDataManager__modifiers



    def __init__(self):
        object.__init__(self)
        self._BuildDataManager__modifiers = {PD.DOLL_PARTS.BODY: [],
         PD.DOLL_PARTS.HEAD: [],
         PD.DOLL_PARTS.HAIR: [],
         PD.DOLL_PARTS.ACCESSORIES: [],
         PD.DOLL_EXTRA_PARTS.BODYSHAPES: [],
         PD.DOLL_EXTRA_PARTS.UTILITYSHAPES: [],
         PD.DOLL_EXTRA_PARTS.UNDEFINED: []}
        self.desiredOrder = PD.DESIRED_ORDER[:]
        self.desiredOrderChanged = False
        self._BuildDataManager__sortedList = []
        self._BuildDataManager__dirty = False
        self.occludeRules = {}
        self._BuildDataManager__dirtyModifiersAdded = []
        self._BuildDataManager__dirtyModifiersRemoved = []
        self._BuildDataManager__locked = False
        self._BuildDataManager__pendingModifiersToAdd = []
        self._BuildDataManager__pendingModifiersToRemove = []
        self._BuildDataManager__filterHidden = True
        self._parentModifiers = {}



    def AddParentModifier(self, modifier, parentModifier):
        parentModifiers = self.GetParentModifiers(modifier)
        if parentModifier not in parentModifiers:
            parentModifiers.append(parentModifier)
        self._parentModifiers[modifier] = parentModifiers



    def GetParentModifiers(self, modifier):
        return self._parentModifiers.get(modifier, [])



    def RemoveParentModifier(self, modifier, dependantModifier = None):
        if dependantModifier:
            parentModifiers = self.GetParentModifiers(dependantModifier)
            if modifier in parentModifiers:
                parentModifiers.remove(modifier)
        else:
            for parentModifiers in self._parentModifiers.itervalues():
                if modifier in parentModifiers:
                    parentModifiers.remove(modifier)




    def GetSoundTags(self):
        soundTags = []
        for modifier in iter(self.GetSortedModifiers()):
            soundTag = modifier.metaData.soundTag
            if soundTag and soundTag not in soundTags:
                soundTags.append(soundTag)

        return soundTags



    def Lock(self):
        self._BuildDataManager__locked = True



    def UnLock(self):
        self._BuildDataManager__locked = False
        for modifier in self._BuildDataManager__pendingModifiersToRemove:
            self.RemoveModifier(modifier)

        self._BuildDataManager__pendingModifiersToRemove = []
        for modifier in self._BuildDataManager__pendingModifiersToAdd:
            self.AddModifier(modifier)

        self._BuildDataManager__pendingModifiersToAdd = []



    def HashForMaps(self, hashableElements = None):
        hasher = hashlib.md5()
        if hashableElements:
            for he in iter(hashableElements):
                hasher.update(str(he))

        for (part, modifiers,) in self.modifiersdata.iteritems():
            hasher.update(part)
            for modifier in iter(modifiers):
                if not (modifier.IsTextureContainingModifier() or modifier.metaData.hidesBootShin or modifier.metaData.forcesLooseTop):
                    continue
                modString = '{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}'.format(modifier.name, modifier.categorie, modifier.weight, modifier.colorizeData, modifier.specularColorData, modifier.pattern, modifier.patternData, modifier.decalData, modifier.useSkin, modifier.variationTextureHash)
                if modifier.metaData.hidesBootShin or modifier.metaData.forcesLooseTop:
                    modString = '{0}{1}{2}'.format(modString, modifier.metaData.hidesBootShin, modifier.metaData.forcesLooseTop)
                hasher.update(modString)

            blue.pyos.BeNice()

        return hasher.hexdigest()



    def GetDirtyModifiers(self, changedBit = False, addedBit = False, removedBit = False, getWeightless = True):
        ret = list()
        masking = changedBit or addedBit or removedBit
        if addedBit or not masking:
            if getWeightless:
                ret.extend(self._BuildDataManager__dirtyModifiersAdded)
            else:
                ret.extend((modifier for modifier in self._BuildDataManager__dirtyModifiersAdded if modifier.weight > 0))
        if removedBit or not masking:
            if getWeightless:
                ret.extend(self._BuildDataManager__dirtyModifiersRemoved)
            else:
                ret.extend((modifier for modifier in self._BuildDataManager__dirtyModifiersRemoved if modifier.weight > 0))
        if changedBit or not masking:
            self._BuildDataManager__filterHidden = False
            changedModifiers = []
            for modifiers in self.modifiersdata.itervalues():
                if getWeightless:
                    changedModifiers.extend((modifier for modifier in modifiers if modifier.IsDirty if modifier not in self._BuildDataManager__dirtyModifiersAdded))
                else:
                    changedModifiers.extend((modifier for modifier in modifiers if modifier.IsDirty if modifier.weight > 0 if modifier not in self._BuildDataManager__dirtyModifiersAdded))

            self._BuildDataManager__filterHidden = True
            for modifier in changedModifiers:
                if modifier not in ret:
                    ret.append(modifier)

        ret = self.SortParts(ret)
        return ret



    def NotifyUpdate(self):
        del self._BuildDataManager__dirtyModifiersAdded[:]
        for modifier in iter(self._BuildDataManager__dirtyModifiersRemoved):
            modifier.ClearCachedData()

        del self._BuildDataManager__dirtyModifiersRemoved[:]
        for modifiers in self.modifiersdata.itervalues():
            for modifier in modifiers:
                modifier.IsDirty = False


        self.desiredOrderChanged = False
        self._BuildDataManager__dirty = False



    def SetAllAsDirty(self, clearMeshes = False):
        for part in self.modifiersdata.iterkeys():
            for modifier in self.modifiersdata[part]:
                modifier.IsDirty = True
                if clearMeshes:
                    modifier.ClearCachedData()


        self._BuildDataManager__dirty = True



    def RemoveMeshContainingModifiers(self, category, privilegedCaller = False):
        for modifier in self.GetModifiersByCategory(category):
            if modifier.IsMeshContainingModifier() and not self.GetParentModifiers(modifier):
                self.RemoveModifier(modifier, privilegedCaller=privilegedCaller)




    def AddModifier(self, modifier, privilegedCaller = False):
        if self._BuildDataManager__locked and not privilegedCaller:
            self._BuildDataManager__pendingModifiersToAdd.append(modifier)
        else:
            part = self.CategoryToPart(modifier.categorie)
            for existingModifier in iter(self._BuildDataManager__modifiers[part]):
                if existingModifier.respath == modifier.respath:
                    if existingModifier.IsHidden:
                        self.ShowModifier(existingModifier)
                    if modifier.weight > existingModifier.weight:
                        existingModifier.weight = modifier.weight
                        self.ApplyOccludeRules(existingModifier)
                    return 

            self.ApplyOccludeRules(modifier)
            if modifier.weight > 0:
                if modifier.categorie == PD.BODY_CATEGORIES.TOPOUTER:
                    self.RemoveMeshContainingModifiers(PD.BODY_CATEGORIES.TOPINNER, privilegedCaller=privilegedCaller)
                elif modifier.categorie == PD.BODY_CATEGORIES.BOTTOMOUTER:
                    self.RemoveMeshContainingModifiers(PD.BODY_CATEGORIES.BOTTOMINNER, privilegedCaller=privilegedCaller)
                if modifier.IsMeshContainingModifier() and modifier.categorie not in (PD.DOLL_PARTS.ACCESSORIES, PD.DOLL_EXTRA_PARTS.DEPENDANTS):
                    self.RemoveMeshContainingModifiers(modifier.categorie, privilegedCaller=privilegedCaller)
            self.OccludeModifiersByModifier(modifier)
            self._BuildDataManager__dirtyModifiersAdded.append(modifier)
            resPaths = modifier.GetDependantModifierResPaths()
            if resPaths:
                for resPath in iter(resPaths):
                    dependantModifier = self.GetModifierByResPath(resPath)
                    if dependantModifier:
                        modifier.AddDependantModifier(dependantModifier)
                        self.AddParentModifier(dependantModifier, modifier)

            for dependantModifier in iter(modifier.GetDependantModifiers()):
                self.AddModifier(dependantModifier, privilegedCaller=privilegedCaller)
                self.AddParentModifier(dependantModifier, modifier)

            if modifier in self._BuildDataManager__dirtyModifiersRemoved:
                self._BuildDataManager__dirtyModifiersRemoved.remove(modifier)
            self._BuildDataManager__modifiers[part].append(modifier)
            self._BuildDataManager__dirty = True



    def OccludeModifiersByModifier(self, modifier):
        occludeData = modifier.GetOccludedModifiersFullData()
        if occludeData:
            for (resPath, weightSubtraction,) in occludeData:
                self.UpdateOccludeRule(resPath, weightSubtraction)
                occlusionTargets = []
                if PD.SEPERATOR_CHAR not in resPath:
                    occlusionTargets.extend(self.GetModifiersByCategory(resPath))
                elif resPath.count(PD.SEPERATOR_CHAR) == 1 and resPath.split(PD.SEPERATOR_CHAR)[0] in PD.CATEGORIES_CONTAINING_GROUPS:
                    (category, group,) = resPath.split(PD.SEPERATOR_CHAR)[:2]
                    groupCandidateModifiers = self.GetModifiersByCategory(category)
                    for groupCandidateModifier in groupCandidateModifiers:
                        if group == groupCandidateModifier.group:
                            occlusionTargets.append(groupCandidateModifier)

                else:
                    targetToOcclude = self.GetModifierByResPath(resPath, includeFuture=True)
                    if targetToOcclude:
                        occlusionTargets.append(targetToOcclude)
                for targetToOcclude in occlusionTargets:
                    targetToOcclude.weight -= weightSubtraction





    def GetOcclusionWeight(self, modifier):
        occlusionWeight = 0
        for resPath in self.occludeRules.iterkeys():
            if resPath in modifier.respath:
                occlusionWeight += self.occludeRules[resPath]

        return occlusionWeight



    def ApplyOccludeRules(self, modifier):
        modifier.weight -= self.GetOcclusionWeight(modifier)



    def IsCategoryOccluded(self, category):
        for (resPath, weight,) in self.occludeRules.iteritems():
            if weight >= 1.0 and resPath == category:
                return True

        return False



    def UpdateOccludeRule(self, resPath, weight):
        occludeRule = self.occludeRules.get(resPath, 0)
        occludeRule += weight
        if occludeRule <= 0.0:
            try:
                del self.occludeRules[resPath]
            except KeyError:
                pass
        else:
            self.occludeRules[resPath] = occludeRule



    def ReverseOccludeModifiersByModifier(self, modifier, useVariation = None):
        occludeData = None
        if useVariation is not None:
            metaData = modifier.GetVariationMetaData(useVariation)
            occludeData = modifier.GetOccludedModifiersFullData(metaData)
        else:
            occludeData = modifier.GetOccludedModifiersFullData()
        if occludeData:
            for (resPath, weightSubtraction,) in occludeData:
                self.UpdateOccludeRule(resPath, -weightSubtraction)
                modifiersToReverseOcclude = []
                if PD.SEPERATOR_CHAR not in resPath:
                    for occludedModifier in self.GetModifiersByCategory(resPath):
                        modifiersToReverseOcclude.append(occludedModifier)

                elif resPath.count(PD.SEPERATOR_CHAR) == 1 and resPath.split(PD.SEPERATOR_CHAR)[0] in PD.CATEGORIES_CONTAINING_GROUPS:
                    (category, group,) = resPath.split(PD.SEPERATOR_CHAR)[:2]
                    groupCandidateModifiers = self.GetModifiersByCategory(category)
                    for groupCandidateModifier in groupCandidateModifiers:
                        if group == groupCandidateModifier.group:
                            modifiersToReverseOcclude.append(groupCandidateModifier)

                else:
                    occludedModifier = self.GetModifierByResPath(resPath)
                    if occludedModifier:
                        modifiersToReverseOcclude.append(occludedModifier)
                for target in modifiersToReverseOcclude:
                    oldWeight = target.weight
                    target.weight += weightSubtraction
                    if oldWeight <= 0 and target.weight > 0:
                        self.AddModifier(target, privilegedCaller=True)





    def RemoveModifier(self, modifier, privilegedCaller = False, occludingCall = False):
        if self._BuildDataManager__locked and not privilegedCaller:
            self._BuildDataManager__pendingModifiersToRemove.append(modifier)
        elif self.GetParentModifiers(modifier) and not occludingCall:
            log.LogWarn('paperDoll::BuildDataManager::RemoveModifier - Attempting to remove a modifier that has parent modifiers', modifier)
            return 
        if modifier in self._BuildDataManager__dirtyModifiersRemoved:
            return 
        part = self.CategoryToPart(modifier.categorie)
        if modifier in self._BuildDataManager__modifiers[part]:
            self._BuildDataManager__modifiers[part].remove(modifier)
        if modifier in self._BuildDataManager__dirtyModifiersAdded:
            self._BuildDataManager__dirtyModifiersAdded.remove(modifier)
        self._BuildDataManager__dirtyModifiersRemoved.append(modifier)
        self.ReverseOccludeModifiersByModifier(modifier)
        self.RemoveParentModifier(modifier)
        for dependantModifier in iter(modifier.GetDependantModifiers()):
            parentModifiers = self.GetParentModifiers(dependantModifier)
            if parentModifiers:
                dependantModifier.weight = 0
                for modifier in iter(parentModifiers):
                    for entry in modifier.GetDependantModifiersFullData():
                        if entry[0] == dependantModifier.respath and entry[3] > dependantModifier.weight:
                            dependantModifier.weight = entry[3]


                self.ApplyOccludeRules(dependantModifier)
            if occludingCall or len(parentModifiers) == 0:
                self.RemoveModifier(dependantModifier, privilegedCaller=privilegedCaller)

        self._BuildDataManager__dirty = True



    def SetModifiersByCategory(self, category, modifiers, privilegedCaller = False):
        self._BuildDataManager__dirty = True
        if type(modifiers) == BuildData:
            modifiers = [modifiers]
        removeModifiers = self.GetModifiersByCategory(category)
        for modifier in iter(removeModifiers):
            self.RemoveModifier(modifier, privilegedCaller=privilegedCaller)

        for modifier in iter(modifiers):
            self.AddModifier(modifier, privilegedCaller=privilegedCaller)




    def GetModifiersByCategory(self, category, showHidden = False, includeFuture = False):
        filterHiddenState = self._BuildDataManager__filterHidden
        if showHidden:
            self._BuildDataManager__filterHidden = False
        part = self.CategoryToPart(category)
        modifiers = self.modifiersdata.get(part, [])
        modifiers = [ modifier for modifier in modifiers if modifier.categorie == category ]
        if includeFuture:
            for modifier in self._BuildDataManager__pendingModifiersToAdd:
                if modifier.categorie == category:
                    modifiers.insert(0, modifier)

        self._BuildDataManager__filterHidden = filterHiddenState
        return modifiers



    def GetModifiersByPart(self, part, showHidden = False):
        filterHiddenState = self._BuildDataManager__filterHidden
        if showHidden:
            self._BuildDataManager__filterHidden = False
        modifiers = self.modifiersdata.get(part, [])
        self._BuildDataManager__filterHidden = filterHiddenState
        return modifiers



    def GetModifierByResPath(self, resPath, includeFuture = False):
        for modifier in self.GetSortedModifiers(includeFuture=includeFuture):
            if modifier.respath == resPath:
                return modifier




    def GetMeshSourcePaths(self, modifiers = None):
        meshSourcePaths = list()
        if modifiers is None:
            modifiers = self.GetSortedModifiers()
        for modifier in iter(modifiers):
            meshSourcePaths.extend(modifier.GetMeshSourcePaths())

        while None in meshSourcePaths:
            meshSourcePaths.remove(None)

        while '' in meshSourcePaths:
            meshSourcePaths.remove('')

        return meshSourcePaths



    def GetMapsToComposite(self, modifiers = None):
        mapTypes = set()
        if modifiers is None:
            modifiers = self.GetSortedModifiers()
        modGenerator = (modifier for modifier in iter(modifiers) if modifier.weight > 0)
        for modifier in modGenerator:
            mapTypes.update(modifier.ContributesToMapTypes())

        return mapTypes



    def GetPartsFromMaps(self, modifiers = None):
        parts = set()
        if modifiers is None:
            modifiers = self.GetSortedModifiers()
        modGenerator = (modifier for modifier in iter(modifiers) if modifier.weight > 0)
        for modifier in modGenerator:
            parts.update(modifier.GetAffectedTextureParts())

        return list(parts)



    def GetParts(self, modifiers = None):
        parts = set()
        if modifiers is None:
            modifiers = self.GetSortedModifiers()
        for modifier in iter(modifiers):
            part = self.CategoryToPart(modifier.categorie)
            parts.add(part)

        return list(parts)



    def HideModifiersByCategory(self, category):
        for modifier in self.GetModifiersByCategory(category):
            self.HideModifier(modifier)




    def HideModifiersByPart(self, part):
        for modifier in self.GetModifiersByPart(part):
            self.HideModifier(modifier)




    def HideModifier(self, modifier):
        self._BuildDataManager__dirty = True
        modifier.IsHidden = True
        self._BuildDataManager__dirtyModifiersRemoved.append(modifier)
        if modifier in self._BuildDataManager__dirtyModifiersAdded:
            self._BuildDataManager__dirtyModifiersAdded.remove(modifier)



    def ShowModifiersByCategory(self, category):
        self._BuildDataManager__filterHidden = False
        for modifier in self.GetModifiersByCategory(category):
            self.ShowModifier(modifier)

        self._BuildDataManager__filterHidden = True



    def ShowModifiersByPart(self, part):
        self._BuildDataManager__filterHidden = False
        for modifier in self.GetModifiersByPart(part):
            self.ShowModifier(modifier)

        self._BuildDataManager__filterHidden = True



    def ShowModifier(self, modifier):
        self._BuildDataManager__dirty = True
        modifier.IsHidden = False
        self._BuildDataManager__dirtyModifiersAdded.append(modifier)
        if modifier in self._BuildDataManager__dirtyModifiersRemoved:
            self._BuildDataManager__dirtyModifiersRemoved.remove(modifier)



    def GetHiddenModifiers(self):
        self._BuildDataManager__filterHidden = False
        modifiers = []
        for modifier in iter(self.GetModifiersAsList()):
            if modifier.IsHidden:
                modifiers.append(modifier)

        self._filterHidden = True
        return modifiers



    def GetBodyModifiers(self, remapToPart = False):
        return self.GetModifiersByPart(PD.DOLL_PARTS.BODY)



    def GetHeadModifiers(self, remapToPart = False):
        category = PD.DOLL_PARTS.HEAD
        if remapToPart:
            category = self.CategoryToPart(category, PD.DOLL_PARTS.HEAD)
        return self.GetModifiersByCategory(category)



    def GetHairModifiers(self, remapToPart = False):
        category = PD.DOLL_PARTS.HAIR
        if remapToPart:
            category = self.CategoryToPart(category, PD.DOLL_PARTS.HAIR)
        return self.GetModifiersByCategory(category)



    def GetAccessoriesModifiers(self, remapToPart = False):
        category = PD.DOLL_PARTS.ACCESSORIES
        if remapToPart:
            category = self.CategoryToPart(category, PD.DOLL_PARTS.ACCESSORIES)
        return self.GetModifiersByCategory(category)



    def GetModifiersAsList(self, includeFuture = False):
        ret = []
        if includeFuture:
            ret = list(self._BuildDataManager__pendingModifiersToAdd)
        for each in self.modifiersdata.itervalues():
            ret.extend(each)

        return ret



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetSortedModifiers(self, showHidden = False, includeFuture = False):
        if showHidden:
            filterHiddenState = self._BuildDataManager__filterHidden
            self._BuildDataManager__filterHidden = False
            modifiers = self.SortParts(self.GetModifiersAsList())
            self._BuildDataManager__filterHidden = filterHiddenState
            return modifiers
        if self._BuildDataManager__dirty or not self._BuildDataManager__sortedList:
            self._BuildDataManager__sortedList = self.SortParts(self.GetModifiersAsList())
        if includeFuture:
            ret = list(self._BuildDataManager__pendingModifiersToAdd)
            ret.extend(self._BuildDataManager__sortedList)
        return list(self._BuildDataManager__sortedList)



    def _SortPartFunc(self, modifier, dso):
        try:
            dsoIdx = dso.index(modifier.categorie) * 1000
            groups = PD.GROUPS.get(modifier.categorie, [])
            try:
                subIdx = groups.index(modifier.group)
            except ValueError:
                subIdx = 999
            dsoIdx += subIdx
        except ValueError:
            dsoIdx = -1
        return dsoIdx



    def SortParts(self, modifiersList):
        dso = self.desiredOrder
        retList = list(modifiersList)
        retList.sort(key=lambda x: self._SortPartFunc(x, dso))
        return retList



    def ChangeDesiredOrder(self, categoryA, categoryB):
        aIdx = self.desiredOrder.index(categoryA)
        bIdx = self.desiredOrder.index(categoryB)
        if aIdx > bIdx:
            self.desiredOrderChanged = True
            self._BuildDataManager__sortedList = None
            (self.desiredOrder[bIdx], self.desiredOrder[aIdx],) = (self.desiredOrder[aIdx], self.desiredOrder[bIdx])



    def GetMeshes(self, part = None, alternativeModifierList = None, includeClothMeshes = False):
        meshes = []
        parts = [part] if part else PD.DOLL_PARTS

        def CollectMeshsFrom(fromIter):
            for each in iter(fromIter):
                if each.weight > 0:
                    if part in (None, self.CategoryToPart(each.categorie)):
                        for mesh in iter(each.meshes):
                            meshes.insert(0, mesh)

                        if includeClothMeshes and each.clothData:
                            meshes.insert(0, each.clothData)



        if alternativeModifierList is not None:
            CollectMeshsFrom(alternativeModifierList)
        elif part is not None:
            for p in parts:
                CollectMeshsFrom(self.GetModifiersByPart(p))

        else:
            CollectMeshsFrom(self.GetSortedModifiers())
        return list(meshes)



    def RemapMeshes(self, destinationMeshes):
        for modifier in iter(self.GetModifiersAsList()):
            for mesh in iter(modifier.meshes):
                for destMesh in iter(destinationMeshes):
                    if mesh.name == destMesh.name:
                        mesh = destMesh
                        break






    def CategoryToPart(self, category, partFilter = None):
        if category in PD.DOLL_PARTS:
            return category
        if category in PD.BODY_CATEGORIES and partFilter in (None, PD.DOLL_PARTS.BODY):
            return PD.DOLL_PARTS.BODY
        if category in PD.HEAD_CATEGORIES and partFilter in (None, PD.DOLL_PARTS.HEAD):
            return PD.DOLL_PARTS.HEAD
        if category in PD.HAIR_CATEGORIES and partFilter in (None, PD.DOLL_PARTS.HAIR):
            return PD.DOLL_PARTS.HAIR
        if category in PD.ACCESSORIES_CATEGORIES and partFilter in (None, PD.DOLL_PARTS.ACCESSORIES):
            return PD.DOLL_PARTS.ACCESSORIES
        if category in PD.DOLL_EXTRA_PARTS.BODYSHAPES:
            return PD.DOLL_EXTRA_PARTS.BODYSHAPES
        if category in PD.DOLL_EXTRA_PARTS.UTILITYSHAPES:
            return PD.DOLL_EXTRA_PARTS.UTILITYSHAPES
        if category in PD.DOLL_EXTRA_PARTS.DEPENDANTS:
            return PD.DOLL_PARTS.BODY
        return PD.DOLL_EXTRA_PARTS.UNDEFINED



exports = {'paperDoll.LoadYamlFileNicely': LoadYamlFileNicely}

