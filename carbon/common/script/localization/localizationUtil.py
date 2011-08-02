import localization
import blue
import util
import uiutil
import time
import icu
import copy
from functools import partial
QUANTITY_TIME_MAP = {('year', 'second'): 'UI/Generic/DateTimeQuantity/YearToSecond',
 ('year', 'minute'): 'UI/Generic/DateTimeQuantity/YearToMinute',
 ('year', 'hour'): 'UI/Generic/DateTimeQuantity/YearToHour',
 ('year', 'day'): 'UI/Generic/DateTimeQuantity/YearToDay',
 ('year', 'month'): 'UI/Generic/DateTimeQuantity/YearToMonth',
 ('year', 'year'): 'UI/Generic/DateTimeQuantity/Year',
 ('month', 'second'): 'UI/Generic/DateTimeQuantity/MonthToSecond',
 ('month', 'minute'): 'UI/Generic/DateTimeQuantity/MonthToMinute',
 ('month', 'hour'): 'UI/Generic/DateTimeQuantity/MonthToHour',
 ('month', 'day'): 'UI/Generic/DateTimeQuantity/MonthToDay',
 ('month', 'month'): 'UI/Generic/DateTimeQuantity/Month',
 ('day', 'second'): 'UI/Generic/DateTimeQuantity/DayToSecond',
 ('day', 'minute'): 'UI/Generic/DateTimeQuantity/DayToMinute',
 ('day', 'hour'): 'UI/Generic/DateTimeQuantity/DayToHour',
 ('day', 'day'): 'UI/Generic/DateTimeQuantity/Day',
 ('hour', 'second'): 'UI/Generic/DateTimeQuantity/HourToSecond',
 ('hour', 'minute'): 'UI/Generic/DateTimeQuantity/HourToMinute',
 ('hour', 'hour'): 'UI/Generic/DateTimeQuantity/Hour',
 ('minute', 'second'): 'UI/Generic/DateTimeQuantity/MinuteToSecond',
 ('minute', 'minute'): 'UI/Generic/DateTimeQuantity/Minute',
 ('second', 'second'): 'UI/Generic/DateTimeQuantity/Second'}
WRITTEN_QUANTITY_TIME_MAP = {('year', 'second'): 'UI/Generic/WrittenDateTimeQuantity/YearToSecond',
 ('year', 'minute'): 'UI/Generic/WrittenDateTimeQuantity/YearToMinute',
 ('year', 'hour'): 'UI/Generic/WrittenDateTimeQuantity/YearToHour',
 ('year', 'day'): 'UI/Generic/WrittenDateTimeQuantity/YearToDay',
 ('year', 'month'): 'UI/Generic/WrittenDateTimeQuantity/YearToMonth',
 ('year', 'year'): 'UI/Generic/WrittenDateTimeQuantity/Year',
 ('month', 'second'): 'UI/Generic/WrittenDateTimeQuantity/MonthToSecond',
 ('month', 'minute'): 'UI/Generic/WrittenDateTimeQuantity/MonthToMinute',
 ('month', 'hour'): 'UI/Generic/WrittenDateTimeQuantity/MonthToHour',
 ('month', 'day'): 'UI/Generic/WrittenDateTimeQuantity/MonthToDay',
 ('month', 'month'): 'UI/Generic/WrittenDateTimeQuantity/Month',
 ('day', 'second'): 'UI/Generic/WrittenDateTimeQuantity/DayToSecond',
 ('day', 'minute'): 'UI/Generic/WrittenDateTimeQuantity/DayToMinute',
 ('day', 'hour'): 'UI/Generic/WrittenDateTimeQuantity/DayToHour',
 ('day', 'day'): 'UI/Generic/WrittenDateTimeQuantity/Day',
 ('hour', 'second'): 'UI/Generic/WrittenDateTimeQuantity/HourToSecond',
 ('hour', 'minute'): 'UI/Generic/WrittenDateTimeQuantity/HourToMinute',
 ('hour', 'hour'): 'UI/Generic/WrittenDateTimeQuantity/Hour',
 ('minute', 'second'): 'UI/Generic/WrittenDateTimeQuantity/MinuteToSecond',
 ('minute', 'minute'): 'UI/Generic/WrittenDateTimeQuantity/Minute',
 ('second', 'second'): 'UI/Generic/WrittenDateTimeQuantity/Second'}
SMALL_WRITTEN_QUANTITY_TIME_MAP = {'year': 'UI/Generic/WrittenDateTimeQuantity/LessThanOneYear',
 'month': 'UI/Generic/WrittenDateTimeQuantity/LessThanOneMonth',
 'day': 'UI/Generic/WrittenDateTimeQuantity/LessThanOneDay',
 'hour': 'UI/Generic/WrittenDateTimeQuantity/LessThanOneHour',
 'minute': 'UI/Generic/WrittenDateTimeQuantity/LessThanOneMinute',
 'second': 'UI/Generic/WrittenDateTimeQuantity/LessThanOneSecond'}

class LocalizationSafeString(unicode):

    def __new__(cls, value, messageID = None, nestLevel = 0):
        message = unicode.__new__(cls, value)
        import localizationUtil
        if isinstance(value, localizationUtil.LocalizationSafeString):
            message.nestLevel = value.nestLevel
            message.messageID = value.messageID
        if messageID or not isinstance(value, localizationUtil.LocalizationSafeString):
            message.messageID = messageID
        if nestLevel or not isinstance(value, localizationUtil.LocalizationSafeString):
            message.nestLevel = nestLevel
        message.initialized = True
        return message



    def __setattr__(self, attr, value):
        if hasattr(self, 'initialized'):
            raise AttributeError('You cannot assign attributes to this class.')
        else:
            return unicode.__setattr__(self, attr, value)



    def replace(self, old, new, maxreplace = 0):
        nestLevel = 0
        import localizationUtil
        if isinstance(new, localizationUtil.LocalizationSafeString):
            nestLevel = max(self.nestLevel, new.nestLevel + 1)
        if maxreplace:
            return LocalizationSafeString(unicode.replace(self, old, new, maxreplace), nestLevel=nestLevel)
        else:
            return LocalizationSafeString(unicode.replace(self, old, new), nestLevel=nestLevel)



    def __add__(self, other):
        return LocalizationSafeString(unicode.__add__(self, other))



    def __iadd__(self, other):
        return LocalizationSafeString(unicode.__add__(self, other))



    def join(self, iterable):
        return LocalizationSafeString(unicode.join(self, iterable))




def IsHardcodedString(text):
    import localizationUtil
    isHardcoded = not isinstance(text, localizationUtil.LocalizationSafeString)
    if isHardcoded:
        pass
    return isHardcoded



def WrapHardcodedString(text, color = '0xaaff00ff'):
    text = uiutil.StripTags(text, stripOnly=['color'])
    text = '<color=%s>^_%s_^</color>' % (color, text)
    return LocalizationSafeString(text)



def SetHardcodedStringDetection(isEnabled):
    localization.hardcodedStringDetectionIsEnabled = isEnabled
    prefs.showHardcodedStrings = isEnabled



def IsHarcodedStringDetectionEnabled():
    return getattr(localization, 'hardcodedStringDetectionIsEnabled', False)



def GetLanguageID():
    try:
        return localization.ISO639_TO_LOCALE_SHORT[session.languageID]
    except (KeyError, AttributeError) as e:
        return localization.LOCALE_SHORT_ENGLISH



def FormatNumeric(value, useGrouping = False, decimalPlaces = localization.DEFAULT_DECIMAL_PLACES, leadingZeroes = localization.DEFAULT_LEADING_ZEROES):
    numberFormat = icu.NumberFormat.createInstance(icu.Locale(localization.systemLocale))
    numberFormat.setMaximumFractionDigits(6)
    numberFormat.setMinimumFractionDigits(6)
    numberFormat.setGroupingUsed(useGrouping)
    if decimalPlaces is not None and decimalPlaces != 0:
        numberFormat.setMinimumFractionDigits(decimalPlaces)
        numberFormat.setMaximumFractionDigits(decimalPlaces)
    if leadingZeroes:
        numberFormat.setMinimumIntegerDigits(leadingZeroes)
    if not decimalPlaces and isinstance(value, int):
        numberFormat.setMaximumFractionDigits(0)
    return LocalizationSafeString(numberFormat.format(value), messageID=-1)



def FormatTime(value, dateFormat = 'short', timeFormat = 'short', showInfoLink = False):
    datetimeFormats = {'none': -1,
     'short': 3,
     'medium': 2,
     'long': 1,
     'full': 0}
    if dateFormat not in datetimeFormats or timeFormat not in datetimeFormats:
        localization.LogError("The date/time combination '", dateFormat, "', '", timeFormat, "' is not a valid combination for the 'time' variable.")
        return None
    if dateFormat == 'none' and timeFormat == 'none':
        localization.LogError("You cannot specify 'none' for both the 'date' field and the 'time' field in a 'time' variable.")
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
        localization.LogError("The 'time' variable only accepts blue time, struct_time, a time float, or tuples as values, but we recieved a ", type(value).__name__, '.')
        return None
    icuLocale = icu.Locale.createFromName(localization.systemLocale)
    if dateFormat is 'none':
        formatter = icu.DateFormat.createTimeInstance(datetimeFormats[timeFormat], icuLocale)
    elif timeFormat is 'none':
        formatter = icu.DateFormat.createDateInstance(datetimeFormats[dateFormat], icuLocale)
    else:
        formatter = icu.DateFormat.createDateTimeInstance(datetimeFormats[dateFormat], datetimeFormats[timeFormat], icuLocale)
    return LocalizationSafeString(formatter.format(value), messageID=-1)



def FormatQuantityTime(value, showFrom = 'year', showTo = 'second', writtenForm = False, showInfoLink = False):
    try:
        if writtenForm:
            dateTimeQuantityLabel = WRITTEN_QUANTITY_TIME_MAP[(showFrom, showTo)]
        else:
            dateTimeQuantityLabel = QUANTITY_TIME_MAP[(showFrom, showTo)]
    except KeyError:
        localization.LogError("The from/to pair '", showFrom, "'/'", showTo, "' is not a valid combination for quantitytime.")
        return 
    if isinstance(value, long):
        (year, month, weekday, day, hour, minute, second, msec,) = blue.os.GetTimeParts(value)
        year -= 1601
        month -= 1
        day -= 1
        day_of_year = 1
        is_daylight_savings = -1
    elif isinstance(value, (time.struct_time, tuple)):
        (year, month, day, hour, minute, second, weekday, day_of_year, is_daylight_savings,) = value
    else:
        localization.LogError('quantitytime only accepts blue time, struct_time, or tuples as values, but we recieved a ', type(value).__name__, '.')
        return 
    if showFrom != 'year':
        month += year * 12
        year = 0
        if showFrom != 'month':
            day += month * 30
            month = 0
            if showFrom != 'day':
                hour += day * 24
                day = 0
                if showFrom != 'hour':
                    minute += hour * 60
                    hour = 0
                    if showFrom != 'minute':
                        second += minute * 60
                        minute = 0
    timeDict = {'year': year,
     'month': month,
     'day': day,
     'hour': hour,
     'minute': minute,
     'second': second}
    smallAmountOfTimeRemaining = None
    for timePart in ('year', 'month', 'day', 'hour', 'minute', 'second'):
        if timeDict[timePart] != 0:
            if smallAmountOfTimeRemaining == False:
                smallAmountOfTimeRemaining = True
            break
        if showFrom == showTo and timePart == showFrom:
            smallAmountOfTimeRemaining = False

    if smallAmountOfTimeRemaining:
        dateTimeQuantityLabel = SMALL_WRITTEN_QUANTITY_TIME_MAP[showFrom]
    return LocalizationSafeString(localization.GetByLabel(dateTimeQuantityLabel, years=year, months=month, days=day, hours=hour, minutes=minute, seconds=second), messageID=-1)



def FormatGenericList(iterable, languageID = None):
    delimiterDict = {'en-us': u', ',
     'ja': u'\u3001',
     'zh-cn': u'\uff0c'}
    stringList = [ unicode(each) for each in iterable ]
    delimeter = delimiterDict.get(languageID, delimiterDict['en-us'])
    return LocalizationSafeString(delimeter.join(stringList))



def LocaleSort(iterable):
    return sorted(iterable)



def MakeRowDicts(rowList, columnNames, tableUniqueKey = None):
    tableData = {}
    rowCount = 0
    for aRow in rowList:
        rowData = {}
        rowKeyValue = False
        if tableUniqueKey:
            rowKeyValue = getattr(aRow, tableUniqueKey)
        for aColumn in columnNames:
            columnData = getattr(aRow, aColumn)
            rowData[aColumn] = columnData

        if tableUniqueKey and rowKeyValue:
            tableData[rowKeyValue] = rowData
        else:
            tableData[rowCount] = rowData
        rowCount = rowCount + 1

    return tableData



def GetEnabledLanguages():
    resultSet = sm.GetService('DB2').zlocalization.LanguageCodes_SelectEnabled()
    import localizationUtil
    languageCodesDict = MakeRowDicts(resultSet, resultSet.columns, localization.COLUMN_LANGUAGE_CODE_STRING)
    return languageCodesDict



def GetLocaleIDFromLocaleShortCode(languageID):
    languageCodesDict = GetEnabledLanguages()
    if languageCodesDict and languageID in languageCodesDict:
        return languageCodesDict[languageID]['languageID']



def Find(query, groupID = None, projectID = None, languageIDs = None, recursive = True):
    return list(_Find(query, groupID, projectID, languageIDs, recursive))



def _Find(query, groupID = None, projectID = None, languageIDs = None, recursive = True):
    results = set()
    if projectID:
        project = localization.Project.Get(projectID)
        messages = project.GetMessagesByGroupID(groupID)
    else:
        messages = localization.Message.GetMessagesByGroupID(groupID)
    if query.isdigit():
        messageID = int(query)
        results.union([ message.messageID for message in localization.Message.GetMyRows(groupID=groupID, messageID=messageID) ])
    for message in messages:
        if not query:
            results.add(message.messageID)
            continue
        if message.label and _IsSubstringInString(query, message.label):
            results.add(message.messageID)
            continue
        if message.context and _IsSubstringInString(query, message.context):
            results.add(message.messageID)
            continue
        selectedLanguageIDs = languageIDs or [ languageID for languageID in GetEnabledLanguages() ]
        for languageID in selectedLanguageIDs:
            messageText = message.GetTextEntry(languageID)
            if messageText and _IsSubstringInString(query, messageText.text):
                results.add(message.messageID)
                break

        if message.messageID in results:
            continue

    if recursive:
        subgroups = localization.MessageGroup.GetMessageGroupsByParentID(groupID, projectID)
        for subgroup in subgroups:
            results = results.union(_Find(query, subgroup.groupID, projectID, languageIDs, recursive))

    return results



def _IsSubstringInString(substring, string):
    return substring.lower() in string.lower()



class LocalizationSystemError(Exception):
    pass
exports = util.AutoExports('localizationUtil', locals())

