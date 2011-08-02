import paperDoll as PD
import random
import itertools

class AbstractRandomizer(object):
    __guid__ = 'paperDoll.AbstractRandomizer'

    @staticmethod
    def SelectManyFromCollection(collection, minElems = None, maxElems = None):
        ret = []
        if collection:
            cLen = len(collection)
            minElems = min(cLen, minElems or 0)
            maxElems = min(cLen, maxElems or cLen)
            idx = set()
            elemsToChoose = random.randint(minElems, maxElems)
            ret = random.sample(collection, elemsToChoose)
        return ret



    @staticmethod
    def SelectOneFromCollection(collection, oddsOfSelectingNone = None):
        if collection:
            oddsOfSelectingNone = oddsOfSelectingNone or 0.0
            oddsOfSelectingNone = min(oddsOfSelectingNone, 1.0)
            if random.random() >= oddsOfSelectingNone:
                return random.choice(collection)




class DollRandomizer(object):
    __guid__ = 'paperDoll.DollRandomizer'
    dollCategories = property(lambda self: list(set(self.completeDollCategories) - set(self.defaultIgnoreCategories)))
    gender = property(fget=lambda self: self.GetGender(), fset=lambda self, x: self.setgender(x))

    def setgender(self, gender):
        self._DollRandomizer__gender = gender


    options = property(fget=lambda self: self.GetOptions())
    blendshapeOptions = property(fget=lambda self: self.GetBlendshapeOptions())
    RESOURCE_OPTION = 'option'
    RESOURCE_TYPE = 'type'

    def __init__(self, modifierLoader):
        self.modifierLoader = modifierLoader
        self.categoriesThatMustHaveEntries = list(set([PD.DOLL_PARTS.HEAD,
         PD.BODY_CATEGORIES.SKINTONE,
         PD.BODY_CATEGORIES.TOPINNER,
         PD.BODY_CATEGORIES.BOTTOMINNER,
         PD.BODY_CATEGORIES.TOPMIDDLE,
         PD.BODY_CATEGORIES.BOTTOMOUTER,
         PD.BODY_CATEGORIES.FEET,
         PD.MAKEUP_EYEBROWS,
         PD.DOLL_PARTS.HAIR,
         PD.MAKEUP_EYES]))
        self.completeDollCategories = list(PD.DOLL_PARTS + PD.DOLL_EXTRA_PARTS + PD.HEAD_CATEGORIES + PD.HAIR_CATEGORIES + PD.BODY_CATEGORIES + PD.ACCESSORIES_CATEGORIES)
        self.completeDollCategories.extend([PD.MAKEUP_EYEBROWS, PD.MAKEUP_EYES])
        self.completeDollCategories = list(set(self.completeDollCategories))
        self.defaultIgnoreCategories = list(set(PD.BLENDSHAPE_CATEGORIES + (PD.DOLL_EXTRA_PARTS.DEPENDANTS,)))
        self.filterCategoriesForRandomization = []
        self._DollRandomizer__gender = None
        self._DollRandomizer__resources = None
        self._DollRandomizer__blendshapeOptions = None
        self._DollRandomizer__blendshapeLimits = {}
        self.weights = {}
        self._DollRandomizer__pathsToRandomizeWeights = {}
        self.oddsOfSelectingNoneForCategory = {}



    def ListOptions(self, category):
        return self.modifierLoader.ListOptions(self.gender, cat=category)



    def ListTypes(self, category):
        return self.modifierLoader.ListTypes(self.gender, cat=category)



    def GetGender(self):
        if not self._DollRandomizer__gender:
            if random.randint(0, 1) == 0:
                self._DollRandomizer__gender = PD.GENDER.FEMALE
            else:
                self._DollRandomizer__gender = PD.GENDER.MALE
        return self._DollRandomizer__gender



    def GetResources(self):
        if not self._DollRandomizer__resources:
            catToResources = {}

            def ChooseResource(category, resourceList, isType):
                odds = 0.0 if category in self.categoriesThatMustHaveEntries else self.oddsOfSelectingNoneForCategory.get(category, 0.22)
                res = AbstractRandomizer.SelectOneFromCollection(resourceList, oddsOfSelectingNone=odds)
                if res:
                    resourceType = self.RESOURCE_TYPE if isType else self.RESOURCE_OPTION
                    catToResources[category] = [(resourceType, res)]
                    if category in self._DollRandomizer__pathsToRandomizeWeights:
                        self.AddRandomizedWeightForOption(res, *self._DollRandomizer__pathsToRandomizeWeights[category])


            gender = self.GetGender()
            catPath = ''
            for category in self.dollCategories:
                if self.filterCategoriesForRandomization:
                    continueOut = True
                    if category in (PD.DOLL_PARTS.ACCESSORIES,
                     PD.HEAD_CATEGORIES.MAKEUP,
                     PD.BODY_CATEGORIES.TATTOO,
                     PD.BODY_CATEGORIES.SCARS):
                        for wCat in self.filterCategoriesForRandomization:
                            if category in wCat.split(PD.SEPERATOR_CHAR):
                                continueOut = False
                                break

                    else:
                        continueOut = category not in self.filterCategoriesForRandomization
                    if continueOut:
                        continue
                if category in (PD.DOLL_PARTS.ACCESSORIES,
                 PD.HEAD_CATEGORIES.MAKEUP,
                 PD.BODY_CATEGORIES.TATTOO,
                 PD.BODY_CATEGORIES.SCARS):
                    options = self.ListOptions(category)
                    for option in options:
                        subcategory = category + '/' + option
                        if not catPath or catPath and subcategory == catPath:
                            if self.filterCategoriesForRandomization:
                                if category in self.filterCategoriesForRandomization or subcategory in self.filterCategoriesForRandomization:
                                    if self.modifierLoader.CategoryHasTypes(subcategory):
                                        ChooseResource(subcategory, self.ListTypes(subcategory), True)
                                    else:
                                        ChooseResource(subcategory, self.ListOptions(subcategory), False)

                elif not catPath or catPath == category:
                    if self.modifierLoader.CategoryHasTypes(category) > 0:
                        ChooseResource(category, self.ListTypes(category), True)
                    else:
                        options = [ option for option in self.ListOptions(category) if 'nude' not in option ]
                        ChooseResource(category, options, False)

            self._DollRandomizer__resources = catToResources
        return self._DollRandomizer__resources



    def SetBlendshapeLimits(self, limitsResPath):
        data = PD.ModifierLoader.LoadBlendshapeLimits(limitsResPath)
        if data and data.get('gender') == self.gender:
            limits = data['limits']
            for key in limits:
                self._DollRandomizer__blendshapeLimits[key.lower()] = limits[key]




    def GetBlendshapeOptions(self):
        if not self._DollRandomizer__blendshapeOptions:
            self._DollRandomizer__blendshapeOptions = {}
            categories = PD.BLENDSHAPE_CATEGORIES - (PD.BLENDSHAPE_CATEGORIES.UTILITYSHAPES, PD.BLENDSHAPE_CATEGORIES.ARCHETYPES)
            for category in categories:
                options = [ option for option in self.ListOptions(category) ]
                options = AbstractRandomizer.SelectManyFromCollection(options, minElems=8)
                pairToElem = {}
                for (key, group,) in itertools.groupby(options, lambda x: x[:x.find('_')]):
                    elems = list(group)
                    if len(elems) > 0 and len(elems) < 2:
                        pairToElem[key] = elems[0]
                    else:
                        random.shuffle(elems)
                        for elem in elems:
                            for pair in PD.BLENDSHAPE_AXIS_PAIRS:
                                for pairElem in pair:
                                    if pairElem in elem:
                                        pairToElem[pair] = elem
                                        break




                options = pairToElem.values()
                self._DollRandomizer__blendshapeOptions[category] = [ (self.RESOURCE_OPTION, option) for option in options ]
                for option in options:
                    (lowerlimit, upperlimit,) = self._DollRandomizer__blendshapeLimits.get(option, (0.0, 1.0))
                    self.AddRandomizedWeightForOption(option, lowerlimit, upperlimit)


        return self._DollRandomizer__blendshapeOptions



    def AddCategoryForWhitelistRandomization(self, category, oddsOfSelectingNone = None):
        self.filterCategoriesForRandomization.append(category)
        if oddsOfSelectingNone is not None:
            self.oddsOfSelectingNoneForCategory[category] = oddsOfSelectingNone



    def AddPathForWeightRandomization(self, path, lowerlimit, upperlimit):
        if lowerlimit <= 0.0 or upperlimit > 1.0:
            raise ValueError('Limits are not within ]0.0, 1.0]')
        self._DollRandomizer__pathsToRandomizeWeights[path] = (lowerlimit, upperlimit)



    def AddRandomizedWeightForOption(self, option, lowerlimit, upperlimit):
        self.weights[option] = lowerlimit + round((upperlimit - lowerlimit) * random.random(), 4)



    def GetColorVariations(self, modifier):
        return modifier.GetColorVariations()



    def GetVariations(self, modifier):
        return modifier.GetVariations()



    def GetCategoryWeight(self, category):
        return self.weights.get(category, 1.0)



    def AddRandomizedResourcesToDoll(self, doll, randomizedResources):
        for category in randomizedResources:
            for (resType, res,) in randomizedResources[category]:
                if not res:
                    continue
                weight = self.weights.get(res, 1.0)
                if resType == self.RESOURCE_TYPE:
                    doll.AddItemType(self.modifierLoader, res, weight)
                else:
                    modifier = doll.AddResource(category + '/' + res, weight, self.modifierLoader)
                    variations = self.GetVariations(modifier)
                    colorVariations = self.GetColorVariations(modifier)
                    variation = AbstractRandomizer.SelectOneFromCollection(variations, oddsOfSelectingNone=0.3)
                    if variation:
                        modifier.SetVariation(variation)
                    variation = AbstractRandomizer.SelectOneFromCollection(colorVariations, oddsOfSelectingNone=0.3)
                    if variation:
                        modifier.SetColorVariation(variation)
                    modifier.weight = weight





    def RemoveAllOptionsByCategory(self, doll, options):
        for category in options:
            mods = doll.GetBuildDataByCategory(category)
            for m in mods:
                doll.RemoveResource(m.categorie + '/' + m.name, self.modifierLoader)





    def GetDoll(self, randomizeBlendshapes = True, doll = None):
        resourceDict = self.GetResources()
        if randomizeBlendshapes:
            blendshapeOptions = self.GetBlendshapeOptions()
        if doll is not None:
            self.RemoveAllOptionsByCategory(doll, resourceDict)
            if randomizeBlendshapes:
                self.RemoveAllOptionsByCategory(doll, blendshapeOptions)
        else:
            doll = PD.Doll('randomized', gender=self.GetGender())
        self.AddRandomizedResourcesToDoll(doll, resourceDict)
        if randomizeBlendshapes:
            self.AddRandomizedResourcesToDoll(doll, blendshapeOptions)
        return doll




