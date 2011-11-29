import localization
import localizationInternalUtil
import blue
import bluepy
import const
import util
import uiutil
import time
import icu
import __builtin__
import re
import mathUtil
import random
QUANTITY_TIME_SHORT_MAP = {2: '/Carbon/UI/Common/DateTimeQuantity/DateTimeShort2Elements',
 3: '/Carbon/UI/Common/DateTimeQuantity/DateTimeShort3Elements',
 4: '/Carbon/UI/Common/DateTimeQuantity/DateTimeShort4Elements',
 5: '/Carbon/UI/Common/DateTimeQuantity/DateTimeShort5Elements',
 6: '/Carbon/UI/Common/DateTimeQuantity/DateTimeShort6Elements',
 7: '/Carbon/UI/Common/DateTimeQuantity/DateTimeShort7Elements'}
QUANTITY_TIME_SHORT_WRITTEN_MAP = {2: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/DateTimeShortWritten2Elements',
 3: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/DateTimeShortWritten3Elements',
 4: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/DateTimeShortWritten4Elements',
 5: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/DateTimeShortWritten5Elements',
 6: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/DateTimeShortWritten6Elements',
 7: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/DateTimeShortWritten7Elements'}
SMALL_WRITTEN_QUANTITY_TIME_MAP = {'year': '/Carbon/UI/Common/WrittenDateTimeQuantity/LessThanOneYear',
 'month': '/Carbon/UI/Common/WrittenDateTimeQuantity/LessThanOneMonth',
 'day': '/Carbon/UI/Common/WrittenDateTimeQuantity/LessThanOneDay',
 'hour': '/Carbon/UI/Common/WrittenDateTimeQuantity/LessThanOneHour',
 'minute': '/Carbon/UI/Common/WrittenDateTimeQuantity/LessThanOneMinute',
 'second': '/Carbon/UI/Common/WrittenDateTimeQuantity/LessThanOneSecond',
 'millisecond': '/Carbon/UI/Common/WrittenDateTimeQuantity/LessThanOneMillisecond'}
TIME_CATEGORY = {'year': 7,
 'month': 6,
 'day': 5,
 'hour': 4,
 'minute': 3,
 'second': 2,
 'millisecond': 1}
QUANTITY_TIME_SHORT_WRITTEN_UNITS_MAP = {TIME_CATEGORY['year']: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/Year',
 TIME_CATEGORY['month']: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/Month',
 TIME_CATEGORY['day']: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/Day',
 TIME_CATEGORY['hour']: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/Hour',
 TIME_CATEGORY['minute']: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/Minute',
 TIME_CATEGORY['second']: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/Second',
 TIME_CATEGORY['millisecond']: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/Millisecond'}

class LocalizationSafeString(unicode):
    pass
COLOR_HARDCODED = mathUtil.LtoI(2868838655L)
COLOR_NESTED = mathUtil.LtoI(2852192255L)
COLOR_ERROR = mathUtil.LtoI(2868838400L)
LOCALIZEDREGEX = re.compile('(<.*?>)')
WHITELIST = ['<t>',
 '<br>',
 '<b>',
 '</b>',
 '<i>',
 '</i>',
 '<center>',
 '<right>',
 '<left>']
WHITELISTREGEX = re.compile('(\\r\\n|<br>|<t>|<center>|</center>|<right>|</right>|<left>|</left>|<color.*?>|</color>|<b>|</b>|<i>|</i>|<url.*?>|</url>|<a href.*?>|</a>)')
_cachedLanguageId = None

@bluepy.CCP_STATS_ZONE_FUNCTION
def CheckForLocalizationErrors(text):
    parts = LOCALIZEDREGEX.split(text)

    def GetHashFromTag(tag):
        hashIndex = tag.find('textHash=')
        if hashIndex != -1:
            searchHash = tag[(hashIndex + 9):]
            hashString = ''
            for sh in searchHash:
                if sh.isdigit() or sh == '-':
                    hashString += sh
                else:
                    break

            return hashString



    def FindLocalizedText(fromIndex):
        retText = ''
        localizedTagCount = 0
        for tag_or_text in parts[fromIndex:]:
            if tag_or_text.startswith('<localized'):
                localizedTagCount += 1
            elif tag_or_text.startswith('</localized'):
                if localizedTagCount:
                    localizedTagCount -= 1
                else:
                    break
            else:
                retText += tag_or_text

        return retText


    returnText = ''
    tagStack = []
    processedLocTag = False
    localizationError = False
    for (partIndex, each,) in enumerate(parts):
        if not each:
            continue
        if each.startswith('<localized'):
            if len(tagStack) == 0 and processedLocTag:
                localizationError = True
            hashString = GetHashFromTag(each)
            inBetween = FindLocalizedText(partIndex + 1)
            hashBetween = unicode(hash(inBetween))
            if hashString != hashBetween:
                each = each.replace('>', ' hashError=%s>' % hashBetween)
            tagStack.append(each)
            returnText += each
        elif each.startswith('</localized'):
            processedLocTag = True
            returnText += each
            if len(tagStack):
                tagStack.pop()
            else:
                localizationError = True
        elif not WHITELISTREGEX.subn('', each)[0] or len(tagStack):
            returnText += each
            if len(tagStack) == 0 and (each == '<br>' or each == '<t>'):
                processedLocTag = False
        else:
            if len(tagStack) == 0:
                localizationError = True
            returnText += each

    if len(tagStack):
        localizationError = True
    return (returnText, localizationError)



def SetHardcodedStringDetection(isEnabled):
    localization.hardcodedStringDetectionIsEnabled = isEnabled
    prefs.showHardcodedStrings = 1 if isEnabled else 0



def IsHardcodedStringDetectionEnabled():
    return getattr(localization, 'hardcodedStringDetectionIsEnabled', False)



def SetPseudolocalization(isEnabled):
    localization.pseudolocalizationIsEnabled = isEnabled
    prefs.pseudolocalizationIsEnabled = 1 if isEnabled else 0



def IsPseudolocalizationEnabled():
    return getattr(localization, 'pseudolocalizationIsEnabled', False)



@bluepy.CCP_STATS_ZONE_FUNCTION
def GetLanguageID():
    global _cachedLanguageId
    if _cachedLanguageId:
        return _cachedLanguageId
    try:
        if boot.role == 'client':
            _cachedLanguageId = localizationInternalUtil.ConvertToLanguageSet('MLS', 'languageID', prefs.languageID) or prefs.languageID
            return _cachedLanguageId
        else:
            return localizationInternalUtil.ConvertToLanguageSet('MLS', 'languageID', session.languageID) or session.languageID
    except (KeyError, AttributeError) as e:
        return localization.LOCALE_SHORT_ENGLISH



@bluepy.CCP_STATS_ZONE_FUNCTION
def ConvertToLanguageSet(fromSetName, toSetName, fromLanguageID):
    return localizationInternalUtil.ConvertToLanguageSet(fromSetName, toSetName, fromLanguageID)



@bluepy.CCP_STATS_ZONE_FUNCTION
def FormatNumeric(value, useGrouping = False, decimalPlaces = None, leadingZeroes = None):
    if not useGrouping and not decimalPlaces and isinstance(value, (int, long)):
        return localizationInternalUtil.PrepareLocalizationSafeString(str(('%0' + str(leadingZeroes or 0) + 'd') % value), messageID='numeric')
    if decimalPlaces == 0 and isinstance(value, float):
        decimalPlaces = None
        value = int(round(value))
    if not localization.numericFormatter:
        return str(value)
    localization.numericFormatter.setGroupingUsed(useGrouping)
    localization.numericFormatter.setMaximumFractionDigits(localization.DEFAULT_MAXIMUM_DECIMAL_PLACES)
    localization.numericFormatter.setMinimumFractionDigits(0)
    if decimalPlaces:
        localization.numericFormatter.setMinimumFractionDigits(decimalPlaces)
        localization.numericFormatter.setMaximumFractionDigits(decimalPlaces)
    if leadingZeroes:
        localization.numericFormatter.setMinimumIntegerDigits(leadingZeroes)
    if isinstance(value, float):
        result = localization.numericFormatter.format(value)
    else:
        formattable = localization.numericFormatterEN_US.parse(str(value))
        result = localization.numericFormatter.format(formattable)
    return localizationInternalUtil.PrepareLocalizationSafeString(result, messageID='numeric')



@bluepy.CCP_STATS_ZONE_FUNCTION
def FormatDateTime(value, dateFormat = 'short', timeFormat = 'short'):
    datetimeFormats = {'none': -1,
     'short': 3,
     'medium': 2,
     'long': 1,
     'full': 0}
    if dateFormat not in datetimeFormats or timeFormat not in datetimeFormats:
        localization.LogError("The date/time combination '", dateFormat, "', '", timeFormat, "' is not a valid combination for the 'datetime' variable.")
        return None
    if dateFormat == 'none' and timeFormat == 'none':
        localization.LogError("You cannot specify 'none' for both the 'date' field and the 'time' field in a 'datetime' variable.")
        return None
    if isinstance(value, long):
        (year, month, weekday, day, hour, minute, second, msec,) = blue.os.GetTimeParts(value)
        day_of_year = 1
        is_daylight_savings = -1
        if timeFormat in ('long', 'full'):
            localization.LogWarn("The time format '", timeFormat, "' displays time zone information, but the caller passed a blue time variable which does not contain timezone information.")
        value = time.mktime((year,
         month,
         day,
         hour,
         minute,
         second,
         weekday,
         day_of_year,
         is_daylight_savings))
    elif isinstance(value, (time.struct_time, tuple)):
        value = time.mktime(value)
    elif not isinstance(value, (time.struct_time, tuple, float)):
        localization.LogError("The 'datetime' variable only accepts blue time, struct_time, a time float, or tuples as values, but we recieved a ", type(value).__name__, '.')
        return None
    icuLocale = icu.Locale.createFromName(localization.systemLocale)
    if dateFormat is 'none':
        formatter = icu.DateFormat.createTimeInstance(datetimeFormats[timeFormat], icuLocale)
    elif timeFormat is 'none':
        formatter = icu.DateFormat.createDateInstance(datetimeFormats[dateFormat], icuLocale)
    else:
        formatter = icu.DateFormat.createDateTimeInstance(datetimeFormats[dateFormat], datetimeFormats[timeFormat], icuLocale)
    return localizationInternalUtil.PrepareLocalizationSafeString(formatter.format(value), messageID='time')



@bluepy.CCP_STATS_ZONE_FUNCTION
def FormatTimeIntervalShort(value, showFrom = 'year', showTo = 'second'):
    timeParts = _FormatTimeIntervalGetParts(value, showFrom, showTo)[:-1]
    startShowing = TIME_CATEGORY[showFrom]
    stopShowing = TIME_CATEGORY[showTo]
    usableParts = timeParts[(TIME_CATEGORY['year'] - startShowing):(TIME_CATEGORY['year'] - stopShowing + 1)]
    kwargs = {}
    for (i, part,) in enumerate(usableParts):
        key = 'value%s' % (i + 1)
        if i == len(usableParts) - 1 and showTo == 'millisecond':
            kwargs[key] = FormatNumeric(part, leadingZeroes=3)
        else:
            kwargs[key] = FormatNumeric(part, leadingZeroes=2)

    if len(usableParts) == 1:
        return kwargs['value1']
    else:
        return localization.GetByLabel(QUANTITY_TIME_SHORT_MAP[len(usableParts)], **kwargs)



@bluepy.CCP_STATS_ZONE_FUNCTION
def FormatTimeIntervalShortWritten(value, showFrom = 'year', showTo = 'second'):
    timeParts = _FormatTimeIntervalGetParts(value, showFrom, showTo)
    stopShowing = TIME_CATEGORY[showTo]
    kwargs = {}
    remainder = timeParts[-1]
    timeParts = timeParts[:-1]
    for (i, part,) in enumerate(timeParts):
        key = 'value%s' % (len(kwargs) + 1)
        part = part + (1 if remainder and TIME_CATEGORY['year'] - i == stopShowing else 0)
        if part > 0 or TIME_CATEGORY['year'] - i == stopShowing:
            kwargs[key] = localization.GetByLabel(QUANTITY_TIME_SHORT_WRITTEN_UNITS_MAP[(TIME_CATEGORY['year'] - i)], value=part)

    length = len(kwargs)
    if length == 1:
        return kwargs['value1']
    else:
        return localization.GetByLabel(QUANTITY_TIME_SHORT_WRITTEN_MAP[length], **kwargs)



@bluepy.CCP_STATS_ZONE_FUNCTION
def FormatTimeIntervalWritten(value, showFrom = 'year', showTo = 'second', languageID = None):
    timeParts = _FormatTimeIntervalGetParts(value, showFrom, showTo)
    if timeParts:
        (year, month, day, hour, minute, second, millisecond, remainder,) = timeParts
    else:
        return None
    timeList = []
    if year > 0:
        timeList.append(localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Year', years=year))
    if month > 0:
        timeList.append(localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Month', months=month))
    if day > 0:
        timeList.append(localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Day', days=day))
    if hour > 0:
        timeList.append(localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Hour', hours=hour))
    if minute > 0:
        timeList.append(localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Minute', minutes=minute))
    if second > 0:
        timeList.append(localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Second', seconds=second))
    if millisecond > 0:
        timeList.append(localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Millisecond', milliseconds=millisecond))
    length = len(timeList)
    if length == 0:
        dateTimeQuantityLabel = SMALL_WRITTEN_QUANTITY_TIME_MAP[showTo]
        return localization.GetByLabel(dateTimeQuantityLabel)
    else:
        if length == 1:
            return timeList[0]
        firstPart = FormatGenericList(timeList[:-1], languageID=languageID)
        lastPart = timeList[-1]
        return localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/ListForm', firstPart=firstPart, secondPart=lastPart)



@bluepy.CCP_STATS_ZONE_FUNCTION
def _FormatTimeIntervalGetParts(value, showFrom, showTo):
    if value < 0:
        raise ValueError('Time value must be a positive number. value = %s' % value)
    if isinstance(value, float):
        value = long(value) * const.SEC
    if not isinstance(value, long):
        raise ValueError('TimeInterval only accepts blue time (long) or python time (float) as values, but we recieved a ', type(value).__name__, '.')
    startShowing = TIME_CATEGORY[showFrom]
    stopShowing = TIME_CATEGORY[showTo]
    if stopShowing > startShowing:
        raise ValueError('The from/to pair %s/%s is not a valid combination for TimeInterval.' % (showFrom, showTo))
    year = month = day = hour = minute = second = millisecond = remainder = 0
    if startShowing >= TIME_CATEGORY['year'] and stopShowing <= TIME_CATEGORY['year']:
        year = value / const.YEAR365
        value -= const.YEAR365 * year
    if startShowing >= TIME_CATEGORY['month'] and stopShowing <= TIME_CATEGORY['month']:
        month = value / const.MONTH30
        value -= const.MONTH30 * month
    if startShowing >= TIME_CATEGORY['day'] and stopShowing <= TIME_CATEGORY['day']:
        day = value / const.DAY
        value -= const.DAY * day
    if startShowing >= TIME_CATEGORY['hour'] and stopShowing <= TIME_CATEGORY['hour']:
        hour = value / const.HOUR
        value -= const.HOUR * hour
    if startShowing >= TIME_CATEGORY['minute'] and stopShowing <= TIME_CATEGORY['minute']:
        minute = value / const.MIN
        value -= const.MIN * minute
    if startShowing >= TIME_CATEGORY['second'] and stopShowing <= TIME_CATEGORY['second']:
        second = value / const.SEC
        value -= const.SEC * second
    if startShowing >= TIME_CATEGORY['millisecond'] and stopShowing <= TIME_CATEGORY['millisecond']:
        millisecond = value / const.MSEC
        value -= const.MSEC * millisecond
    remainder = value
    return (year,
     month,
     day,
     hour,
     minute,
     second,
     millisecond,
     remainder)



@bluepy.CCP_STATS_ZONE_FUNCTION
def FormatGenericList(iterable, languageID = None):
    languageID = localizationInternalUtil.StandardizeLanguageID(languageID) or GetLanguageID()
    delimiterDict = {'en-us': u', ',
     'ja': u'\u3001',
     'zh-cn': u'\uff0c'}
    stringList = [ unicode(each) for each in iterable ]
    delimeter = delimiterDict.get(languageID, delimiterDict['en-us'])
    return localizationInternalUtil.PrepareLocalizationSafeString(delimeter.join(stringList), messageID='genericlist')



@bluepy.CCP_STATS_ZONE_FUNCTION
def Sort(iterable, cmp = None, key = lambda x: x, reverse = False, languageID = None):
    if cmp:
        raise ValueError("Passing a compare function into Sort defeats the purpose of using a language-aware sort.  You probably want to use the 'key' parameter instead.")
    languageID = languageID or localizationInternalUtil.StandardizeLanguageID(languageID) or GetLanguageID()
    collator = icu.Collator.createInstance(icu.Locale(str(languageID)))

    def caseSensitiveSubsort(left, right):
        if left.lower() == right.lower():
            return collator.compare(right, left)
        return collator.compare(left.lower(), right.lower())


    if all([ isinstance(key(each), (int, type(None))) for each in iterable ]):

        def getPronunciation(messageID):
            if not messageID:
                return ''
            if localization.IsValidMetaDataByMessageID(messageID, 'pronunciation', languageID=languageID):
                return localization.GetMetaData(messageID, 'pronunciation', languageID=languageID)
            return localization.GetByMessageID(messageID, languageID)


        return sorted(iterable, cmp=caseSensitiveSubsort, key=lambda x: uiutil.StripTags(getPronunciation(key(x))), reverse=reverse)
    return sorted(iterable, cmp=caseSensitiveSubsort, key=lambda x: uiutil.StripTags(key(x)), reverse=reverse)



def GetEnabledLanguages():
    import localizationUtil
    if localizationUtil._languageCodesDict is None:
        resultSet = sm.GetService('DB2').zlocalization.Languages_Select()
        localizationUtil._languageCodesDict = localizationInternalUtil.MakeRowDicts(resultSet, resultSet.columns, localization.COLUMN_LANGUAGE_ID)
    return localizationUtil._languageCodesDict



def ReloadEnabledLanguagesCache():
    import localizationUtil
    localizationUtil._languageCodesDict = None
    GetEnabledLanguages()



def GetLocaleIDFromLocaleShortCode(languageID):
    languageCodesDict = GetEnabledLanguages()
    if languageCodesDict and languageID in languageCodesDict:
        return languageCodesDict[languageID][localization.COLUMN_LANGUAGE_KEY]



def GetDisplayLanguageName(inLanguageID, languageID):
    inLanguageID = str(inLanguageID)
    languageID = str(languageID)
    langName = icu.Locale.createFromName(languageID).getDisplayLanguage(icu.Locale.createFromName(inLanguageID)).title()
    return localizationInternalUtil.PrepareLocalizationSafeString(langName, messageID='languageName')



def TestString(sourceText, languageID = 'en-us'):
    db2 = sm.GetService('DB2')

    def _GetRandomDateTime():
        return blue.os.GetWallclockTime()



    def _GetRandomTimeInterval():
        return const.YEAR365 * 1 * random.randint(0, 1) + const.MONTH30 * random.randint(1, 11) * random.randint(0, 1) + const.DAY * random.randint(1, 29) * random.randint(0, 1) + const.HOUR * random.randint(1, 23) * random.randint(0, 1) + const.MIN * random.randint(1, 59) * random.randint(0, 1) + const.SEC * random.randint(1, 59) * random.randint(0, 1) + const.MSEC * random.randint(1, 9999) * random.randint(0, 1)



    def _GetRandomNumeric():
        if random.randint(0, 1):
            return random.random() * pow(10, random.randint(1, 10))
        return int(random.random() * pow(10, random.randint(1, 10)))



    def _GetRandomGeneric():
        return ' '.join('Lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'.split(' ')[:random.randint(1, 19)])


    sqlData = {'character': 'SELECT TOP 1 characterID AS id FROM character.npcCharacters\n ORDER BY NEWID()',
     'npcOrganization': 'SELECT TOP 1 corporationID AS id FROM corporation.npcCorporations\n ORDER BY NEWID()',
     'item': 'SELECT TOP 1 typeID AS id FROM inventory.types\n ORDER BY NEWID()',
     'location': 'SELECT TOP 1 stationID AS id FROM staStations\n ORDER BY NEWID()',
     'messageid': 'SELECT TOP 1 messageID AS id FROM zlocalization.messages\n WHERE label IS NULL\n ORDER BY NEWID()'}
    multiRowSqlData = {'characterlist': 'SELECT TOP %s characterID AS id FROM character.npcCharacters\n ORDER BY NEWID()' % random.randint(1, 5)}
    randomData = {'datetime': _GetRandomDateTime,
     'formattedtime': _GetRandomDateTime,
     'timeinterval': _GetRandomTimeInterval,
     'numeric': _GetRandomNumeric,
     'generic': _GetRandomGeneric}
    tags = localization._Tokenize(sourceText)
    kwargs = {}
    for tag in tags.values():
        if tag['variableName'] and tag['variableType'] and tag['variableName'] not in kwargs:
            if tag['variableType'] in sqlData:
                kwargs[tag['variableName']] = db2.SQL(sqlData[tag['variableType']])[0].id
            if tag['variableType'] in multiRowSqlData:
                kwargs[tag['variableName']] = [ row.id for row in db2.SQL(multiRowSqlData[tag['variableType']]) ]
            elif tag['variableType'] in randomData:
                kwargs[tag['variableName']] = randomData[tag['variableType']]()

    for tag in tags.values():
        if 'showinfo' in tag['kwargs']:
            kwargs[tag['kwargs']['showinfo']] = (kwargs[tag['variableName']],)
        if 'quantity' in tag['kwargs']:
            kwargs[tag['kwargs']['quantity']] = random.choice([0,
             0.5,
             1,
             2,
             5])

    (result, errors,) = localization._Parse(sourceText, None, languageID, returnErrors=True, **kwargs)
    if errors:
        return errors
    return result



def Find(query, groupID = None, projectID = None, languageIDs = None, maxResults = 1000):
    return list(_Find(query, groupID, projectID, languageIDs, maxResults))



def _Find(query, groupID = None, projectID = None, languageIDs = None, maxResults = -1):
    bsdTableSvc = sm.GetService('bsdTable')
    messageTable = bsdTableSvc.GetTable('zlocalization', 'messages')
    messageTextTable = bsdTableSvc.GetTable('zlocalization', 'messageTexts')
    projectsToGroupsTable = bsdTableSvc.GetTable('zlocalization', 'projectsToGroups')
    results = set()
    if maxResults == 0:
        return results
    if projectID and groupID:
        messages = messageTable.GetRows(groupID=groupID) if projectsToGroupsTable.GetRows(groupID=groupID, projectID=projectID) else []
    elif not projectID and groupID:
        messages = messageTable.GetRows(groupID=groupID)
    elif projectID and not groupID:
        taggedGroupIDs = [ taggedGroup.groupID for taggedGroup in projectsToGroupsTable.GetRows(projectID=projectID) ]
        messages = []
        for groupID in taggedGroupIDs:
            messages += messageTable.GetRows(groupID=groupID)

    else:
        messages = messageTable.GetRows()
    if query.isdigit():
        messageID = int(query)
        if messageTable.GetRowByKey(keyId1=messageID):
            results = results.union([messageID])
    if not languageIDs:
        languageIDs = GetEnabledLanguages()
    selectedLanguagePrimaryKeys = [ GetLocaleIDFromLocaleShortCode(languageID) for languageID in languageIDs ]
    for message in messages:
        blue.pyos.BeNice()
        if maxResults != -1 and len(results) >= maxResults:
            break
        if not query:
            results.add(message.messageID)
            continue
        elif message.label and _IsSubstringInString(query, message.label):
            results.add(message.messageID)
            continue
        elif message.context and _IsSubstringInString(query, message.context):
            results.add(message.messageID)
            continue
        for languagePrimaryKey in selectedLanguagePrimaryKeys:
            messageText = messageTextTable.GetRowByKey(keyId1=message.messageID, keyId2=languagePrimaryKey)
            if messageText and messageText.text and _IsSubstringInString(query, messageText.text):
                results.add(message.messageID)
                break

        if message.messageID in results:
            continue

    if groupID:
        subgroups = localization.MessageGroup.GetMessageGroupsByParentID(groupID, projectID)
        for subgroup in subgroups:
            if maxResults != -1 and len(results) >= maxResults:
                break
            if maxResults != -1:
                maxResults -= len(results)
            results = results.union(_Find(query, subgroup.groupID, projectID, languageIDs, maxResults))

    return results



def _IsSubstringInString(substring, string):
    return substring.lower() in string.lower()



class LocalizationSystemError(Exception):
    pass
exports = util.AutoExports('localizationUtil', locals())
exports['localizationUtil._languageCodesDict'] = None

