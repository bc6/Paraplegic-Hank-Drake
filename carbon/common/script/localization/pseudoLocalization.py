import localization
import localizationUtil
import __builtin__
import random
import blue
import re
TEXT_EXPANSION_RANGES = {1: (1, 10),
 2: (11, 20),
 3: (21, 30),
 4: (31, 50),
 5: (51, 70),
 6: (70, 9999)}
TEXT_EXPANSION_AMOUNTS = {localization.NO_REPLACEMENT: {1: 1.0,
                               2: 1.0,
                               3: 1.0,
                               4: 1.0,
                               5: 1.0,
                               6: 1.0},
 localization.DIACRITIC_REPLACEMENT: {1: 6.667,
                                      2: 3.333,
                                      3: 2.667,
                                      4: 1.333,
                                      5: 1.333,
                                      6: 1.0},
 localization.CYRILLIC_REPLACEMENT: {1: 6.667,
                                     2: 3.333,
                                     3: 2.667,
                                     4: 1.333,
                                     5: 1.333,
                                     6: 1.0},
 localization.DOUBLE_BYTE_REPLACEMENT: {1: 1.0,
                                        2: 1.0,
                                        3: 1.0,
                                        4: 1.0,
                                        5: 1.0,
                                        6: 1.0}}
DIACRITIC_REPLACEMENT_MAP = {'A': u'\xc0\xc1\xc2\xc3\xc4\xc5',
 'B': u'\xdf',
 'C': u'\xc7',
 'D': u'\xd0',
 'E': u'\xc8\xc9\xca\xcb',
 'I': u'\xcc\xcd\xce\xcf',
 'L': u'\xa3',
 'N': u'\xd1',
 'O': u'\xd2\xd3\xd4\xd5\xd6\xd8',
 'P': u'\xde',
 'S': u'\u0160',
 'U': u'\xd9\xda\xdb\xdc',
 'Y': u'\u0178\xa5\xdd',
 'Z': u'\u017d',
 'a': u'\xe0\xe1\xe2\xe3\xe4\xe5',
 'c': u'\xa2\xe7',
 'd': u'\xf0',
 'e': u'\xe8\xe9\xea\xeb',
 'i': u'\xa1\xec\xed\xee\xef',
 'n': u'\xf1',
 'o': u'\xf2\xf3\xf4\xf5\xf6\xf8',
 'p': u'\xfe',
 's': u'\u0161',
 'u': u'\xf9\xfa\xfb\xfc',
 'y': u'\xfd\xff',
 'z': u'\u017e'}
CYRILLIC_REPLACEMENT_MAP = {'A': u'\u0410\u0414',
 'B': u'\u0412\u042a\u042c',
 'C': u'\u0421',
 'D': u'\u042d',
 'E': u'\u0415',
 'F': u'\u0492',
 'G': u'\u0404',
 'H': u'\u041d',
 'I': u'\u0406',
 'J': u'\u0408',
 'K': u'\u041a',
 'L': u'\u0413',
 'M': u'\u041c',
 'N': u'\u0418\u041b\u041f',
 'O': u'\u041e',
 'P': u'\u0420',
 'Q': u'\u0472',
 'R': u'\u042f',
 'S': u'\u0405',
 'T': u'\u0422',
 'U': u'\u0426',
 'V': u'\u0474',
 'W': u'\u0428\u0429',
 'X': u'\u0416\u0425',
 'Y': u'\u0423',
 'Z': u'\u04e0',
 'a': u'\u0430\u0434',
 'b': u'\u0432\u044a\u044c',
 'c': u'\u0441',
 'd': u'\u0431',
 'e': u'\u0435',
 'f': u'\u0493',
 'g': u'\u0499',
 'h': u'\u043d',
 'i': u'\u0456',
 'j': u'\u0458',
 'k': u'\u043a',
 'l': u'\u04c0',
 'm': u'\u043c',
 'n': u'\u0438\u043b\u043f',
 'o': u'\u043e',
 'p': u'\u0440',
 'q': u'\u0473',
 'r': u'\u0433\u044f',
 's': u'\u0455',
 't': u'\u0442',
 'u': u'\u0446',
 'v': u'\u0477',
 'w': u'\u0448\u0449',
 'x': u'\u0436\u0445',
 'y': u'\u0443',
 'z': u'\u04e1'}
DOUBLE_BYTE_REPLACEMENT_MAP = {'A': u'\uff21',
 'B': u'\uff22',
 'C': u'\uff23',
 'D': u'\uff24',
 'E': u'\uff25',
 'F': u'\uff26',
 'G': u'\uff27',
 'H': u'\uff28',
 'I': u'\uff29',
 'J': u'\uff2a',
 'K': u'\uff2b',
 'L': u'\uff2c',
 'M': u'\uff2d',
 'N': u'\uff2e',
 'O': u'\uff2f',
 'P': u'\uff30',
 'Q': u'\uff31',
 'R': u'\uff32',
 'S': u'\uff33',
 'T': u'\uff34',
 'U': u'\uff35',
 'V': u'\uff36',
 'W': u'\uff37',
 'X': u'\uff38',
 'Y': u'\uff39',
 'Z': u'\uff3a',
 'a': u'\uff41',
 'b': u'\uff42',
 'c': u'\uff43',
 'd': u'\uff44',
 'e': u'\uff45',
 'f': u'\uff46',
 'g': u'\uff47',
 'h': u'\uff48',
 'i': u'\uff49',
 'j': u'\uff4a',
 'k': u'\uff4b',
 'l': u'\uff4c',
 'm': u'\uff4d',
 'n': u'\uff4e',
 'o': u'\uff4f',
 'p': u'\uff50',
 'q': u'\uff51',
 'r': u'\uff52',
 's': u'\uff53',
 't': u'\uff54',
 'u': u'\uff55',
 'v': u'\uff56',
 'w': u'\uff57',
 'x': u'\uff58',
 'y': u'\uff59',
 'z': u'\uff5a'}
PSEUDOLOCALIZATION_MAP = {localization.NO_REPLACEMENT: {},
 localization.DIACRITIC_REPLACEMENT: DIACRITIC_REPLACEMENT_MAP,
 localization.CYRILLIC_REPLACEMENT: CYRILLIC_REPLACEMENT_MAP,
 localization.DOUBLE_BYTE_REPLACEMENT: DOUBLE_BYTE_REPLACEMENT_MAP}

def Pseudolocalize(englishString):
    if boot.role != 'client':
        return englishString
    else:
        if not hasattr(__builtin__, 'settings'):
            characterReplacementMethod = localization.DIACRITIC_REPLACEMENT
            showMessageID = False
            enableBoundaryMarkers = True
            enableTextExpansion = False
            textExpansionAmount = 0.0
        else:
            characterReplacementMethod = settings.user.localization.Get('characterReplacementMethod', localization.DIACRITIC_REPLACEMENT)
            showMessageID = settings.user.localization.Get('showMessageID', 0)
            enableBoundaryMarkers = settings.user.localization.Get('enableBoundaryMarkers', 0)
            enableTextExpansion = settings.user.localization.Get('enableTextExpansion', 0)
            textExpansionAmount = settings.user.localization.Get('textExpansionAmount', 0.0)
        messageID = None
        if isinstance(englishString, localizationUtil.LocalizationSafeString):
            pseudolocalizedString = unicode(englishString)
            messageID = englishString.messageID
        else:
            pseudolocalizedString = unicode(englishString)
        if enableTextExpansion:
            pseudolocalizedString = _PerformTextExpansion(pseudolocalizedString, textExpansionAmount, characterReplacementMethod)
        pseudolocalizedString = _PerformCharacterReplacement(pseudolocalizedString, characterReplacementMethod)
        if showMessageID:
            pseudolocalizedString = _AddMessageID(pseudolocalizedString, messageID=messageID)
        if enableBoundaryMarkers:
            pseudolocalizedString = _AddBoundaryMarkers(pseudolocalizedString)
        if isinstance(englishString, localizationUtil.LocalizationSafeString):
            return localizationUtil.LocalizationSafeString(pseudolocalizedString, messageID=messageID)
        return pseudolocalizedString



def _IsLocalizable(englishString):
    if not englishString:
        return False
    if not isinstance(englishString, str) and not isinstance(englishString, unicode):
        return False
    htmlTagFound = False
    for character in englishString:
        if character == '<':
            htmlTagFound = True
        if htmlTagFound is True and character == '>':
            htmlTagFound = False
        elif htmlTagFound is True:
            continue
        else:
            if htmlTagFound is False and character.isalpha():
                return True

    return False



def _AddBoundaryMarkers(englishString):
    return '[' + englishString + ']'



def _AddMessageID(englishString, messageID = None):
    return '<color=0xaaff0000>[%d]</color>%s' % (messageID or -1, englishString)



def _PerformTextExpansion(englishString, textExpansionAmount, characterReplacementMethod):
    sanitizedEnglishString = re.sub('<[^>]*?>', '', englishString)
    sanitizedEnglishString = re.sub('^[0-9]+', '', sanitizedEnglishString)
    sanitizedEnglishString = sanitizedEnglishString.replace(' ', '')
    alphaIndices = []
    tagLevel = 0
    tagOpen = False
    for (index, character,) in enumerate(englishString):
        if character == '<':
            if tagLevel == 0:
                tagOpen = True
            tagLevel += 1
        if tagLevel > 0 and character == '>':
            tagLevel -= 1
            if tagLevel == 0:
                tagOpen = False
        if tagLevel == 0 and character.isalpha():
            alphaIndices.append(index)

    initialLength = len(alphaIndices)
    for (expansionRange, minMax,) in TEXT_EXPANSION_RANGES.iteritems():
        (minChars, maxChars,) = minMax
        if minChars <= initialLength <= maxChars:
            break

    expansionAmount = TEXT_EXPANSION_AMOUNTS[characterReplacementMethod][expansionRange] * textExpansionAmount + 1.0
    desiredLength = int(initialLength * expansionAmount)
    alphabeticCharacters = [ character for character in sanitizedEnglishString if character.isalpha() ]
    alphabeticCharacters = list(set(alphabeticCharacters))
    while len(alphaIndices) < desiredLength:
        characterIndex = random.choice(alphaIndices)
        characterToDouble = englishString[characterIndex]
        englishString = englishString[:characterIndex] + characterToDouble + englishString[characterIndex:]
        for (index, value,) in enumerate(alphaIndices):
            if value > characterIndex:
                alphaIndices[index] = value + 1

        alphaIndices.append(characterIndex + 1)

    return englishString



def _PerformCharacterReplacement(englishString, characterReplacementMethod):
    pseudolocalizedString = ''
    htmlTagFound = False
    for character in englishString:
        if character == '<':
            htmlTagFound = True
        if htmlTagFound is True and character == '>':
            htmlTagFound = False
        elif htmlTagFound is True:
            pseudolocalizedString += character
            continue
        if character in PSEUDOLOCALIZATION_MAP[characterReplacementMethod]:
            pseudolocalizedString += random.choice(PSEUDOLOCALIZATION_MAP[characterReplacementMethod][character])
        else:
            pseudolocalizedString += character

    return pseudolocalizedString


exports = {'localization.Pseudolocalize': Pseudolocalize}

