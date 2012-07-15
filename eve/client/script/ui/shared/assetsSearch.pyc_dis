#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/assetsSearch.py
import re
import uicls
import uiconst
import base
import localization
import localizationUtil
from collections import namedtuple
REGEX = re.compile("\n    \\b(?P<key>\\w+):\\s*          # a single keyword followed by a : like 'min:'\n    (?P<value>[\\w\\s]+)          # the value can be any combination of whitespaces and alphanumerical letters\n    (?![\\w+:])                  # we dont want to include a word that is followed by : since it will mark a new keyword\n    ", re.UNICODE + re.IGNORECASE + re.VERBOSE)
KeywordOption = namedtuple('KeywordOption', 'keyword optionDescription specialOptions matchFunction')

def ParseString(text):
    matches = REGEX.findall(text)
    if matches:
        key, value = matches[0]
        key = key + ':'
        text = text[:text.find(key)]
    return (text.strip(), matches)


def MatchType(conditions, word, value):
    typeName = value

    def CheckType(item):
        t = cfg.invtypes.Get(item.typeID)
        return t.name.lower().find(typeName) > -1

    conditions.append(CheckType)


def MatchGroup(conditions, word, value):
    groupName = value

    def CheckGroup(item):
        g = cfg.invgroups.Get(item.groupID)
        return g.name.lower().find(groupName) > -1

    conditions.append(CheckGroup)


def MatchCategory(conditions, word, value):
    categoryName = value

    def CheckCategory(item):
        c = cfg.invcategories.Get(item.categoryID)
        return c.name.lower().find(categoryName) > -1

    conditions.append(CheckCategory)


def MatchMinimumQuantity(conditions, word, value):
    quantity = int(value)

    def CheckMinQuantity(item):
        return item.stacksize >= quantity

    conditions.append(CheckMinQuantity)


def MatchMaximumQuantity(conditions, word, value):
    quantity = int(value)

    def CheckMaxQuantity(item):
        return item.stacksize <= quantity

    conditions.append(CheckMaxQuantity)


def MatchMetalevel(conditions, word, value):
    level = int(value)

    def CheckMetaLevel(item):
        metaLevel = int(sm.GetService('godma').GetTypeAttribute(item.typeID, const.attributeMetaLevel, 0))
        return level == metaLevel

    conditions.append(CheckMetaLevel)


def MatchMetagroup(conditions, word, value):
    groupName = value

    def CheckMetaGroup(item):
        metaGroupID = int(sm.GetService('godma').GetTypeAttribute(item.typeID, const.attributeMetaGroupID, 0))
        if metaGroupID > 0:
            metaGroup = cfg.invmetagroups.Get(metaGroupID)
            return groupName in metaGroup.name.lower()
        return False

    conditions.append(CheckMetaGroup)


def MatchTechlevel(conditions, word, value):
    level = int(value)

    def CheckTechLevel(item):
        techLevel = int(sm.GetService('godma').GetTypeAttribute(item.typeID, const.attributeTechLevel, 1))
        return level == techLevel

    conditions.append(CheckTechLevel)


def MatchMinSecurity(conditions, word, value):
    uiSvc = sm.GetService('ui')
    secLevel = float(value)

    def CheckMinSecurity(item):
        solarSystemID = uiSvc.GetStation(item.locationID).solarSystemID
        systemSec = sm.GetService('map').GetSecurityStatus(solarSystemID)
        return systemSec >= secLevel

    conditions.append(CheckMinSecurity)


def MatchMaxSecurity(conditions, word, value):
    uiSvc = sm.GetService('ui')
    secLevel = float(value)

    def CheckMaxSecurity(item):
        solarSystemID = uiSvc.GetStation(item.locationID).solarSystemID
        systemSec = sm.GetService('map').GetSecurityStatus(solarSystemID)
        return systemSec <= secLevel

    conditions.append(CheckMaxSecurity)


def MatchSecurityClass(conditions, word, value):
    if localization.GetByLabel('UI/Inventory/AssetSearch/OptionSecurityHigh').startswith(value):
        secClass = [const.securityClassHighSec]
    elif localization.GetByLabel('UI/Inventory/AssetSearch/OptionSecurityLow').startswith(value):
        secClass = [const.securityClassLowSec]
    elif localization.GetByLabel('UI/Inventory/AssetSearch/OptionSecurityNull').startswith(value) or localization.GetByLabel('UI/Inventory/AssetSearch/OptionSecurityZero').startswith(value):
        secClass = [const.securityClassZeroSec]
    elif localization.GetByLabel('UI/Inventory/AssetSearch/OptionSecurityEmpire').startswith(value):
        secClass = [const.securityClassHighSec, const.securityClassLowSec]
    else:
        return
    uiSvc = sm.GetService('ui')

    def CheckSecurityClass(item):
        solarSystemID = uiSvc.GetStation(item.locationID).solarSystemID
        systemSecClass = sm.GetService('map').GetSecurityClass(solarSystemID)
        return systemSecClass in secClass

    conditions.append(CheckSecurityClass)


def MatchSolarSystem(conditions, word, value):
    uiSvc = sm.GetService('ui')
    name = value

    def CheckSolarSystem(item):
        solarSystemID = uiSvc.GetStation(item.locationID).solarSystemID
        item = sm.GetService('map').GetItem(solarSystemID)
        return name in item.itemName.lower()

    conditions.append(CheckSolarSystem)


def MatchConstellation(conditions, word, value):
    uiSvc = sm.GetService('ui')
    name = value

    def CheckConstellation(item):
        solarSystemID = uiSvc.GetStation(item.locationID).solarSystemID
        mapSvc = sm.GetService('map')
        constellationID = mapSvc.GetConstellationForSolarSystem(solarSystemID)
        item = mapSvc.GetItem(constellationID)
        return name in item.itemName.lower()

    conditions.append(CheckConstellation)


def MatchRegion(conditions, word, value):
    uiSvc = sm.GetService('ui')
    name = value

    def CheckRegion(item):
        solarSystemID = uiSvc.GetStation(item.locationID).solarSystemID
        mapSvc = sm.GetService('map')
        regionID = mapSvc.GetRegionForSolarSystem(solarSystemID)
        item = mapSvc.GetItem(regionID)
        return name in item.itemName.lower()

    conditions.append(CheckRegion)


def MatchStationName(conditions, word, value):
    name = value

    def CheckStation(item):
        stationName = cfg.evelocations.Get(item.locationID).locationName.lower()
        return name in stationName

    conditions.append(CheckStation)


def MatchBlueprint(conditions, word, value):
    if localization.GetByLabel('UI/Inventory/AssetSearch/OptionBlueprintCopy').startswith(value):
        isBpo = False
    elif localization.GetByLabel('UI/Inventory/AssetSearch/OptionBlueprintOriginal').startswith(value):
        isBpo = True
    else:
        return

    def CheckBlueprintType(item):
        if item.categoryID == const.categoryBlueprint:
            if isBpo:
                return item.singleton != const.singletonBlueprintCopy
            else:
                return item.singleton == const.singletonBlueprintCopy
        return False

    conditions.append(CheckBlueprintType)


class SearchBox(uicls.SinglelineEdit):
    __guid__ = 'assets.SearchBox'
    default_dynamicHistoryWidth = True

    def ApplyAttributes(self, attributes):
        uicls.SinglelineEdit.ApplyAttributes(self, attributes)
        self.blockSetValue = True
        self.TEXTRIGHTMARGIN = 1
        self.searchKeywords = attributes.get('keywords', [])
        self.CreateLayout()

    def SetValue(self, text, *args, **kwargs):
        oldText = self.GetValue()
        uicls.SinglelineEdit.SetValue(self, text, *args, **kwargs)
        self.caretIndex = self.GetCursorFromIndex(self.GetSmartCaretIndex(oldText, text))
        self.RefreshCaretPosition()

    def GetSmartCaretIndex(self, oldText, newText):
        oldText = oldText[::-1]
        newText = newText[::-1]
        for i in xrange(len(oldText)):
            if oldText[i] != newText[i]:
                return len(newText) - i

        return len(newText)

    def CreateLayout(self):
        self.optionIcon = uicls.Sprite(parent=self.sr.maincontainer, name='options', texturePath='res:/UI/Texture/Icons/38_16_229.png', pos=(0, 0, 16, 16), align=uiconst.TORIGHT, idx=0, hint=localization.GetByLabel('UI/Inventory/AssetSearch/KeywordOptionsHint'))
        self.optionIcon.SetAlpha(0.8)
        self.optionIcon.OnClick = self.OnOptionClick

    def OnOptionClick(self):
        self.ShowHistoryMenu(self.GetStaticHints())

    def GetStaticHints(self):
        currentText = self.GetValue(registerHistory=0)
        currentText = currentText.rstrip()
        if currentText:
            currentText += ' '
        hints = []
        for kw in self.searchKeywords:
            hints.append((localization.GetByLabel('UI/Inventory/AssetSearch/KeywordHint', keyword=kw.keyword, description=kw.optionDescription), '%s%s: ' % (currentText, kw.keyword)))

        return hints

    def GetDynamicHints(self):
        hints = []
        caretIndex = self.caretIndex[0]
        currentText = self.GetValue(registerHistory=0)
        headText, tailText = currentText[:caretIndex], currentText[caretIndex:]
        tailText = tailText.lstrip()
        trimmedText = headText.rstrip()
        if trimmedText.endswith(':'):
            strippedText, lastWord = self.SplitText(trimmedText, removeSeprator=True)
            if lastWord:
                for kw in self.IterMatchingKeywords(lastWord):
                    if kw.specialOptions:
                        for option in kw.specialOptions:
                            hints.append((localization.GetByLabel('UI/Inventory/AssetSearch/OptionHint', keyword=kw.keyword, option=option), '%s%s: %s %s' % (strippedText,
                              kw.keyword,
                              option,
                              tailText)))

        else:
            strippedText, lastWord = self.SplitText(trimmedText, removeSeprator=False)
            freeText, matches = ParseString(trimmedText)
            if lastWord:
                if matches and lastWord == matches[-1][1].lower():
                    keyword, value = matches[-1]
                    for kw in self.IterMatchingKeywords(keyword):
                        value = value.lower()
                        if kw.specialOptions:
                            for option in kw.specialOptions:
                                if option.startswith(value):
                                    hints.append((localization.GetByLabel('UI/Inventory/AssetSearch/OptionHint', keyword=kw.keyword, option=option), '%s%s %s' % (strippedText, option, tailText)))

                            break

                else:
                    for kw in self.IterMatchingKeywords(lastWord):
                        hints.append((localization.GetByLabel('UI/Inventory/AssetSearch/KeywordHint', keyword=kw.keyword, description=kw.optionDescription), '%s%s: %s' % (strippedText, kw.keyword, tailText)))

        return hints

    def IterMatchingKeywords(self, keyword):
        keyword = keyword.lower()
        for kw in self.searchKeywords:
            if kw.keyword.startswith(keyword):
                yield kw

    def SplitText(self, baseText, removeSeprator = False):
        strippedText, lastWord = (None, None)
        parts = baseText.split()
        if parts:
            lastWord = parts[-1]
            strippedText = baseText[:-len(lastWord)]
            if removeSeprator:
                lastWord = lastWord[:-1]
            if strippedText:
                strippedText = strippedText.rstrip() + ' '
        return (strippedText, '' if lastWord is None else lastWord.lower())

    def TryRefreshHistory(self, currentString):
        self.refreshHistoryTimer = base.AutoTimer(200, self.TryRefreshHistory_Thread, currentString)

    def TryRefreshHistory_Thread(self, currentString):
        if currentString.rstrip().endswith(':'):
            self.CheckHistory()
        self.refreshHistoryTimer = None

    def OnHistoryClick(self, clickedString):
        self.TryRefreshHistory(clickedString)

    def OnComboChange(self, combo, label, value, *args):
        self.SetValue(label, updateIndex=0)
        self.TryRefreshHistory(value)

    def GetValid(self):
        valid = uicls.SinglelineEdit.GetValid(self)
        history = [ (text, text) for text in valid ]
        hints = self.GetDynamicHints()
        return hints + history

    def Confirm(self, *args):
        active = getattr(self, 'active', None)
        if active:
            text = active.string
            self.SetValue(text)
        uicls.SinglelineEdit.Confirm(self, *args)
        if active:
            self.TryRefreshHistory(text)


def GetSearchKeywords():
    keywords = [KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordType'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionType'), None, MatchType),
     KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordGroup'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionGroup'), None, MatchGroup),
     KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordCategory'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionCategory'), None, MatchCategory),
     KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordMinimumQuantity'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionMinimumQuantity'), None, MatchMinimumQuantity),
     KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordMaximumQuantity'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionMaximumQuantity'), None, MatchMaximumQuantity),
     KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordMetalevel'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionMetalevel'), None, MatchMetalevel),
     KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordMetagroup'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionMetagroup'), localizationUtil.Sort([ cfg.invmetagroups.Get(groupID).metaGroupName.lower() for groupID in const.metaGroupsUsed ]), MatchMetagroup),
     KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordTechLevel'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionTechLevel'), ['1', '2', '3'], MatchTechlevel),
     KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordMinSecurityLevel'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionMinSecurityLevel'), None, MatchMinSecurity),
     KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordMaxSecurityLevel'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionMaxSecurityLevel'), None, MatchMaxSecurity),
     KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordSecurityClass'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionSecurityClass'), localizationUtil.Sort([localization.GetByLabel('UI/Inventory/AssetSearch/OptionSecurityHigh'),
      localization.GetByLabel('UI/Inventory/AssetSearch/OptionSecurityEmpire'),
      localization.GetByLabel('UI/Inventory/AssetSearch/OptionSecurityLow'),
      localization.GetByLabel('UI/Inventory/AssetSearch/OptionSecurityNull'),
      localization.GetByLabel('UI/Inventory/AssetSearch/OptionSecurityZero')]), MatchSecurityClass),
     KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordSolarSystem'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionSolarSystem'), None, MatchSolarSystem),
     KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordConstellation'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionConstellation'), None, MatchConstellation),
     KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordRegion'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionRegion'), None, MatchRegion),
     KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordStationName'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionStationName'), None, MatchStationName),
     KeywordOption(localization.GetByLabel('UI/Inventory/AssetSearch/KeywordBlueprint'), localization.GetByLabel('UI/Inventory/AssetSearch/DescriptionBlueprint'), localizationUtil.Sort([localization.GetByLabel('UI/Inventory/AssetSearch/OptionBlueprintCopy'), localization.GetByLabel('UI/Inventory/AssetSearch/OptionBlueprintOriginal')]), MatchBlueprint)]
    return localizationUtil.Sort(keywords, key=lambda x: x.keyword)


exports = {'assets.ParseString': ParseString,
 'assets.GetSearchKeywords': GetSearchKeywords}