import paperDoll
import blue
import const
import random
import yaml
import util
FACIAL_POSE_PARAMETERS = util.KeyVal(PortraitPoseNumber='PortraitPoseNumber', HeadLookTarget='HeadLookTarget', HeadTilt='HeadTilt', OrientChar='OrientChar', BrowLeftCurl='BrowLeftCurl', BrowLeftTighten='BrowLeftTighten', BrowLeftUpDown='BrowLeftUpDown', BrowRightCurl='BrowRightCurl', BrowRightTighten='BrowRightTighten', BrowRightUpDown='BrowRightUpDown', EyeClose='EyeClose', EyesLookVertical='EyesLookVertical', EyesLookHorizontal='EyesLookHorizontal', SquintLeft='SquintLeft', SquintRight='SquintRight', JawSideways='JawSideways', JawUp='JawUp', PuckerLips='PuckerLips', FrownLeft='FrownLeft', FrownRight='FrownRight', SmileLeft='SmileLeft', SmileRight='SmileRight')
bloodlineAssets = {const.bloodlineAchura: 'caldari_achura',
 const.bloodlineAmarr: 'amarr_amarr',
 const.bloodlineBrutor: 'minmatar_brutor',
 const.bloodlineCivire: 'caldari_civire',
 const.bloodlineDeteis: 'caldari_deteis',
 const.bloodlineGallente: 'gallente_gallente',
 const.bloodlineIntaki: 'gallente_intaki',
 const.bloodlineJinMei: 'gallente_jinmei',
 const.bloodlineKhanid: 'amarr_khanid',
 const.bloodlineNiKunni: 'amarr_nikunni',
 const.bloodlineSebiestor: 'minmatar_sebiestor',
 const.bloodlineVherokior: 'minmatar_vherokior'}

def CreateRandomDoll(gender, bloodline, doll = None):
    ml = paperDoll.ModifierLoader()
    blue.synchro.Yield()
    randomizer = paperDoll.EveDollRandomizer(ml)
    if gender is not None:
        randomizer.gender = gender
    if bloodline is not None:
        randomizer.bloodline = bloodline
    randomizer.SetSculptingLimits()
    doll = randomizer.GetDoll(True, doll)
    randomizer.RandomizeHairColor(doll)
    return doll



def CreateRandomDollNoClothes(gender, bloodline, doll = None, noRandomize = False):
    ml = paperDoll.ModifierLoader()
    blue.synchro.Yield()
    randomizer = paperDoll.EveDollRandomizer(ml)
    randomizer.isNewCharacter = True
    if gender is not None:
        randomizer.gender = gender
    if bloodline is not None:
        randomizer.bloodline = bloodline
    randomizer.SetSculptingLimits()
    options = randomizer.ListOptions(None)
    if doll is not None:
        randomizer.RemoveAllOptionsByCategory(doll, options)
    else:
        doll = paperDoll.Doll('randomized', gender=gender)
    for x in [paperDoll.DOLL_PARTS.HEAD, paperDoll.BODY_CATEGORIES.SKIN]:
        randomizer.AddCategoryForWhitelistRandomization(x)

    resourceDict = randomizer.GetResources()
    randomizer.AddRandomizedResourcesToDoll(doll, resourceDict)
    if not noRandomize:
        blendshapes = randomizer.GetBlendshapeOptions()
        del blendshapes[paperDoll.DOLL_EXTRA_PARTS.BODYSHAPES]
        randomizer.AddRandomizedResourcesToDoll(doll, blendshapes)
    return doll


MODIFIER_LOCATION_BY_KEY = {}
REQUIRED_MODIFICATION_LOCATIONS = set()
REQUIRED_MODIFICATION_LOCATIONS_FEMALE = {}
REQUIRED_MODIFICATION_LOCATIONS_MALE = {}

def CacheRequiredModifierLocatiosn():
    if not len(MODIFIER_LOCATION_BY_KEY):
        for row in cfg.paperdollModifierLocations:
            MODIFIER_LOCATION_BY_KEY[row.modifierKey] = row.modifierLocationID

    if not len(REQUIRED_MODIFICATION_LOCATIONS):
        REQUIRED_MODIFICATION_LOCATIONS.add(MODIFIER_LOCATION_BY_KEY[paperDoll.BODY_CATEGORIES.OUTER])
        REQUIRED_MODIFICATION_LOCATIONS.add(MODIFIER_LOCATION_BY_KEY[paperDoll.BODY_CATEGORIES.TOPOUTER])
        REQUIRED_MODIFICATION_LOCATIONS.add(MODIFIER_LOCATION_BY_KEY[paperDoll.BODY_CATEGORIES.TOPMIDDLE])
    if not len(REQUIRED_MODIFICATION_LOCATIONS_FEMALE):
        REQUIRED_MODIFICATION_LOCATIONS_FEMALE[MODIFIER_LOCATION_BY_KEY[paperDoll.BODY_CATEGORIES.BOTTOMOUTER]] = mls.UI_CHARCREA_BOTTOM
        REQUIRED_MODIFICATION_LOCATIONS_FEMALE[MODIFIER_LOCATION_BY_KEY[paperDoll.BODY_CATEGORIES.FEET]] = mls.UI_CHARCREA_FEET
    if not len(REQUIRED_MODIFICATION_LOCATIONS_MALE):
        REQUIRED_MODIFICATION_LOCATIONS_MALE[MODIFIER_LOCATION_BY_KEY[paperDoll.BODY_CATEGORIES.BOTTOMOUTER]] = mls.UI_CHARCREA_BOTTOM
        REQUIRED_MODIFICATION_LOCATIONS_MALE[MODIFIER_LOCATION_BY_KEY[paperDoll.BODY_CATEGORIES.FEET]] = mls.UI_CHARCREA_FEET



def HasRequiredClothing(dollGender, dollTypes):
    CacheRequiredModifierLocatiosn()
    dollModifierLocations = set([ row.modifierLocationID for row in dollTypes ])
    missingCategoryDescriptions = []
    if len(dollModifierLocations.intersection(REQUIRED_MODIFICATION_LOCATIONS)) == 0:
        missingCategoryDescriptions.append(mls.UI_CHARCREA_TOP)
    if dollGender == 'female':
        dollCategories = REQUIRED_MODIFICATION_LOCATIONS_FEMALE
    else:
        dollCategories = REQUIRED_MODIFICATION_LOCATIONS_MALE
    for (category, description,) in dollCategories.iteritems():
        if category not in dollModifierLocations and description not in missingCategoryDescriptions:
            missingCategoryDescriptions.append(description)

    if len(missingCategoryDescriptions) > 0:
        raise UserError('MissingRequiredClothing', {'clothingList': ', '.join(missingCategoryDescriptions)})
    else:
        return True



def BuildPaperdollProcedureArgs(dollInfo):
    procargs = []
    procargs.append(yaml.dump(dollInfo.faceModifiers, Dumper=yaml.CDumper))
    procargs.append(yaml.dump(dollInfo.bodyShapes, Dumper=yaml.CDumper))
    procargs.append(yaml.dump(dollInfo.utilityShapes, Dumper=yaml.CDumper))
    procargs.append(dollInfo.typeColors['skintone'][0])
    procargs.append(dollInfo.types.get('makeup/aging'))
    procargs.append(dollInfo.types.get('makeup/freckles'))
    procargs.append(dollInfo.types.get('makeup/scarring'))
    procargs.append(dollInfo.types.get('makeup/eyes'))
    procargs.append(dollInfo.typeColors.get('makeup/eyes')[0])
    if 'makeup/eyeshadow' in dollInfo.types:
        procargs.append(dollInfo.types['makeup/eyeshadow'])
        procargs.append(dollInfo.typeWeights['makeup/eyeshadow'])
        procargs.append(dollInfo.typeColors['makeup/eyeshadow'][0])
        procargs.append(dollInfo.typeColors['makeup/eyeshadow'][1])
    else:
        procargs.extend([None] * 4)
    if 'makeup/eyeliner' in dollInfo.types:
        procargs.append(dollInfo.types['makeup/eyeliner'])
        procargs.append(dollInfo.typeWeights['makeup/eyeliner'])
        procargs.append(dollInfo.typeColors['makeup/eyeliner'][0])
    else:
        procargs.extend([None] * 3)
    if 'makeup/blush' in dollInfo.types:
        procargs.append(dollInfo.types['makeup/blush'])
        procargs.append(dollInfo.typeWeights['makeup/blush'])
        procargs.append(dollInfo.typeColors['makeup/blush'][0])
    else:
        procargs.extend([None] * 3)
    if 'makeup/lipstick' in dollInfo.types:
        procargs.append(dollInfo.types['makeup/lipstick'])
        procargs.append(dollInfo.typeWeights['makeup/lipstick'])
        procargs.append(dollInfo.typeSpecularity.get('makeup/lipstick'))
        procargs.append(dollInfo.typeColors['makeup/lipstick'][0])
    else:
        procargs.extend([None] * 4)
    procargs.append(dollInfo.types['hair'])
    procargs.append(dollInfo.typeColors['hair'][0])
    procargs.append(dollInfo.typeColors['hair'][1])
    procargs.append(dollInfo.types.get('makeup/eyebrows'))
    procargs.append(dollInfo.types.get('beard'))
    procargs.append(dollInfo.hairDarkness)
    procargs.append(dollInfo.types.get('bottominner'))
    procargs.append(dollInfo.types.get('bottomouter'))
    procargs.append(dollInfo.typeTuck.get('dependants/boottucking'))
    procargs.append(dollInfo.types.get('topmiddle'))
    procargs.append(dollInfo.typeTuck.get('dependants/drape'))
    procargs.append(dollInfo.types.get('topouter'))
    procargs.append(dollInfo.types.get('feet'))
    procargs.append(dollInfo.types.get('outer'))
    procargs.append(dollInfo.typeTuck.get('dependants/hood'))
    procargs.append(dollInfo.types.get('topinner'))
    procargs.append(dollInfo.types.get('accessories/glasses'))
    procargs.append(dollInfo.types.get('makeup/implants'))
    return procargs


exports = {'paperDollUtil.bloodlineAssets': bloodlineAssets,
 'paperDollUtil.CreateRandomDoll': CreateRandomDoll,
 'paperDollUtil.CreateRandomDollNoClothes': CreateRandomDollNoClothes,
 'paperDollUtil.HasRequiredClothing': HasRequiredClothing,
 'paperDollUtil.FACIAL_POSE_PARAMETERS': FACIAL_POSE_PARAMETERS,
 'paperDollUtil.BuildPaperdollProcedureArgs': BuildPaperdollProcedureArgs}

