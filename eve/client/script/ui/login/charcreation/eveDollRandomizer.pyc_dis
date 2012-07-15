#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/login/charcreation/eveDollRandomizer.py
import paperDoll
import paperDollUtil
import blue
import const
import random
import util
import ccUtil
import ccConst
import service
MASTER_COLORS = [ccConst.hair, ccConst.eyes]

class EveDollRandomizer(paperDoll.DollRandomizer):
    __guid__ = 'paperDoll.EveDollRandomizer'
    bloodline = property(fget=lambda self: self.GetBloodline(), fset=lambda self, x: self.setbloodline(x))

    def setbloodline(self, bloodline):
        self.__bloodline = bloodline

    def __init__(self, modifierLoader):
        paperDoll.DollRandomizer.__init__(self, modifierLoader)
        self.__bloodline = None
        self.isNewCharacter = False
        self.fullRandomization = False

    def GetBloodline(self):
        if not self.__bloodline:
            self.__bloodline = random.sample(paperDollUtil.bloodlineAssets, 1)[0]
        return self.__bloodline

    def GetColorVariations(self, modifier):
        retList = paperDoll.DollRandomizer.GetColorVariations(self, modifier)
        if modifier.categorie == paperDoll.BODY_CATEGORIES.SKINTONE and modifier.name == 'basic':
            bloodlineName = paperDollUtil.bloodlineAssets[self.GetBloodline()].split('_')[1]
            retList = [ x for x in retList if x.startswith(bloodlineName) ]
        return retList

    def ListOptions(self, category):
        opts = paperDoll.DollRandomizer.ListOptions(self, category)
        if category == paperDoll.DOLL_PARTS.HEAD:
            return [paperDollUtil.bloodlineAssets[self.GetBloodline()]]
        return opts

    def ListTypes(self, category):
        if self.isNewCharacter:
            if category == paperDoll.DOLL_PARTS.HAIR:
                if self.gender == paperDoll.GENDER.MALE:
                    return ['res:/Graphics/Character/Modular/Male/hair/Hair_Stubble_02/Types/Hair_Stubble_02.type']
                else:
                    return ['res:/Graphics/Character/Modular/Female/hair/Hair_Stubble_01/Types/Hair_Stubble_01.type']
        ret = []
        types = self.modifierLoader.ListTypes(self.gender, category)
        if self.fullRandomization:
            if category in (ccConst.skinaging, ccConst.freckles, ccConst.scarring):
                types = types[:1]
        availableTypeIDs = sm.GetService('cc').GetMyApparel()
        for each in types:
            typeData = self.modifierLoader.GetItemType(each, gender=self.gender)
            if typeData is None:
                continue
            if category in ccConst.randomizerBlacklist:
                if typeData[0].split('/')[-1] in ccConst.randomizerBlacklist[category]:
                    continue
            assetID, assetTypeID = sm.GetService('character').GetAssetAndTypeIDsFromPath(self.gender, each)
            if assetTypeID is not None and assetTypeID not in availableTypeIDs:
                continue
            if len(typeData) == 4:
                restrictions = typeData[-1]
                if type(restrictions) == list:
                    if self.bloodline not in restrictions:
                        ret.append(each)
            else:
                ret.append(each)

        return ret

    def SetSculptingLimits(self):
        bloodlineID = self.GetBloodline()
        limitPath = 'res:/Graphics/Character/Global/FaceSetup/ScultpingLimits/%s_%s_blendshape_limits.yaml' % (paperDollUtil.bloodlineAssets[bloodlineID], self.GetGender())
        self.SetBlendshapeLimits(limitPath)

    def ApplyRandomizedResourcesToCharacter(self, charID, randomizedResources):
        charSvc = sm.GetService('character')
        for cat, categoryValue in randomizedResources.iteritems():
            for resType, res in categoryValue:
                if not res:
                    continue
                var = None
                weight = self.weights.get(res, 1.0)
                if resType == self.RESOURCE_TYPE:
                    resPath = charSvc.factory.GetItemType(res, gender=self.gender)[0]
                    color1Value, color1Name, color2Name, variation = (None, None, None, None)
                    glossiness = None
                    colorizeData = None
                    if cat in MASTER_COLORS or cat.startswith('makeup') and cat != 'makeup/eyebrows' or cat.startswith('tattoo'):
                        genderID = ccUtil.PaperDollGenderToGenderID(self.gender)
                        colorsA, colorsB = charSvc.GetAvailableColorsForCategory(cat, genderID, self.bloodline)
                        colorA = []
                        colorB = []
                        if len(colorsA) > 0:
                            colorA = random.choice(colorsA)
                            colorB = None
                            if len(colorsB) > 0:
                                colorB = random.choice(colorsB)
                            color1Value, color1Name, color2Name, variation = charSvc.GetColorsToUse(colorA, colorB)
                        if color1Value:
                            colorizeData = color1Value
                        elif colorB or variation:
                            var = variation
                        elif len(colorA) > 0:
                            var = colorA[1]
                        if self.gender == paperDoll.GENDER.FEMALE and ccUtil.HasUserDefinedSpecularity(cat):
                            glossiness = round(0.3 + 0.3 * random.random(), 2)
                    modifier = charSvc.ApplyTypeToDoll(charID, res, weight, doUpdate=False, rawColorVariation=var)
                    if color1Name:
                        charSvc.characterMetadata[charID].typeColors[cat] = (color1Name, color2Name)
                    if glossiness:
                        charSvc.SetColorSpecularityByCategory(charID, cat, glossiness, doUpdate=False)
                    if colorizeData:
                        modifier.SetColorizeData(colorizeData)
                else:
                    modifier = charSvc.ApplyItemToDoll(charID, cat, res, removeFirst=True, doUpdate=False)
                    colorVariations = self.GetColorVariations(modifier)
                    colorVariation = paperDoll.AbstractRandomizer.SelectOneFromCollection(colorVariations, oddsOfSelectingNone=0)
                    if colorVariation:
                        colorTuple = (colorVariation, modifier.colorVariations[colorVariation])
                        charSvc.SetColorValueByCategory(charID, cat, colorTuple, None, doUpdate=False)
                    modifier.weight = weight

    def RandomizeHairColor(self, charID, randomizeFacialDarkness = True):
        genderID = 0 if self.gender == paperDoll.GENDER.FEMALE else 1
        charSvc = sm.GetService('character')
        p, s = charSvc.GetAvailableColorsForCategory(paperDoll.DOLL_PARTS.HAIR, genderID, self.bloodline)
        primary = random.choice(p)
        secondary = random.choice(s)
        charSvc.SetColorValueByCategory(charID, 'hair', primary, secondary, doUpdate=False)
        charSvc.SetHairDarkness(charID, random.random())
        charSvc.SynchronizeHairColors()