import localization
import localizationUtil
import locale
import blue
import re
import copy
import time
import icu
propertyHandlersInitialized = False
PROPERTY_HANDLERS = {'character': 'CharacterPropertyHandler',
 'item': 'ItemPropertyHandler',
 'location': 'LocationPropertyHandler',
 'numeric': 'NumericPropertyHandler'}
messageTagCache = {}
systemLocale = icu.Locale.getBaseName(icu.Locale())

def _RegisterPropertyHandlers():
    global propertyHandlersInitialized
    import __builtin__
    while not hasattr(__builtin__, 'sm'):
        blue.synchro.Yield()

    for (variableName, handlerClassName,) in PROPERTY_HANDLERS.iteritems():
        if hasattr(localization, str(handlerClassName)):
            localization.LogInfo("Mapping variable type '", variableName, "' to property handler 'localization.", handlerClassName, "'.")
            PROPERTY_HANDLERS[variableName] = getattr(localization, handlerClassName)().GetProperty
        else:
            localization.LogInfo("Could not find specified property handler for variable type '", variableName, "' (localization.", handlerClassName, '). Mapping to debug property handler.')
            PROPERTY_HANDLERS[variableName] = _UndefinedPropertyHandlerFactory(variableName)

    propertyHandlersInitialized = True



def _Parse(sourceText, messageID, languageID, **kwargs):
    if messageID and (messageID, languageID) in messageTagCache:
        tags = copy.deepcopy(messageTagCache[(messageID, languageID)])
    elif not isinstance(sourceText, localizationUtil.LocalizationSafeString):
        sourceText = localizationUtil.LocalizationSafeString(sourceText, messageID=messageID)
    tags = _Tokenize(sourceText)
    messageTagCache[(messageID, languageID)] = copy.deepcopy(tags)
    if not tags:
        return sourceText
    for (tagName, tag,) in tags.iteritems():
        if tag['variableName'] in kwargs:
            tag['variableValue'] = kwargs[tag['variableName']]
        else:
            localization.LogWarn("Unreferenced tag '", tagName, "' in messageID ", messageID, '. Source string: ', sourceText)

    parsedText = sourceText
    for (tagName, tag,) in tags.iteritems():
        if tag['propertyName']:
            tag['propertyValue'] = _GetPropertyValue(tag['variableType'], tag['propertyName'], tag['variableValue'], languageID)
        if tag['isConditional']:
            replaceText = _ProcessConditional(tagName, tag, languageID)
            if replaceText:
                parsedText = parsedText.replace(tagName, replaceText)
        else:
            parsedText = VARIABLE_TYPE_DATA[tag['variableType']]['handlerFunction'](parsedText, tagName, tag)

    return parsedText



def _CharacterHandler(originalText, tag, tagData):
    result = _ApplyModifiers(unicode(tagData['propertyValue']), tagData)
    return originalText.replace(tag, result)



def _ItemHandler(originalText, tag, tagData):
    result = _ApplyModifiers(unicode(tagData['propertyValue']), tagData)
    return originalText.replace(tag, result)



def _LocationHandler(originalText, tag, tagData):
    result = _ApplyModifiers(unicode(tagData['propertyValue']), tagData)
    return originalText.replace(tag, result)



def _CharacterListHandler(originalText, tag, tagData):
    result = _ApplyModifiers(unicode(tagData['propertyValue']), tagData)
    return originalText.replace(tag, result)



def _MessageHandler(originalText, tag, tagData):
    result = _ApplyModifiers(unicode(tagData['variableValue']), tagData)
    return originalText.replace(tag, result)



def _TimeHandler(originalText, tag, tagData):
    value = tagData['variableValue']
    dateFormat = tagData['kwargs'].get('date', 'short')
    timeFormat = tagData['kwargs'].get('time', 'short')
    dateTimeString = localizationUtil.FormatTime(value, dateFormat=dateFormat, timeFormat=timeFormat)
    if not dateTimeString:
        localization.LogError('A parse error has occured.  Source string: ', originalText)
        return originalText
    result = _ApplyModifiers(dateTimeString, tagData)
    return originalText.replace(tag, result)



def _FormattedTimeHandler(originalText, tag, tagData):
    value = tagData['variableValue']
    try:
        formatString = tagData['kwargs']['format']
    except KeyError as e:
        return originalText
    if isinstance(value, long):
        (year, month, weekday, day, hour, minute, second, msec,) = blue.os.GetTimeParts(value)
        day_of_year = 1
        is_daylight_savings = -1
        value = (year,
         month,
         day,
         hour,
         minute,
         second,
         weekday,
         day_of_year,
         is_daylight_savings)
    elif not isinstance(value, (time.struct_time, tuple)):
        localization.LogError('formattedtime only accepts blue time, struct_time, or tuples as values, but we recieved a ', type(value).__name__, '.  Source string: ', originalText)
        return originalText
    dateTimeString = time.strftime(formatString, value)
    result = _ApplyModifiers(unicode(dateTimeString), tagData)
    return originalText.replace(tag, result)



def _QuantityTimeHandler(originalText, tag, tagData):
    value = tagData['variableValue']
    fromMark = tagData['kwargs'].get('from', None)
    toMark = tagData['kwargs'].get('to', None)
    dateTimeString = localizationUtil.FormatQuantityTime(value, showFrom=fromMark, showTo=toMark, writtenForm='writtenForm' in tagData['args'])
    if not dateTimeString:
        localization.LogError('A parse error has occured.  Source string: ', originalText)
        return originalText
    result = _ApplyModifiers(unicode(dateTimeString), tagData)
    return originalText.replace(tag, result)



def _NumericHandler(originalText, tag, tagData):
    value = tagData['variableValue']
    useGrouping = 'useGrouping' in tagData['args']
    decimalPlaces = int(tagData['kwargs']['decimalPlaces']) if 'decimalPlaces' in tagData['kwargs'] else localization.DEFAULT_DECIMAL_PLACES
    leadingZeroes = int(tagData['kwargs']['leadingZeroes']) if 'leadingZeroes' in tagData['kwargs'] else localization.DEFAULT_LEADING_ZEROES
    numericString = localizationUtil.FormatNumeric(value, useGrouping=useGrouping, decimalPlaces=decimalPlaces, leadingZeroes=leadingZeroes)
    if not numericString:
        localization.LogError('A parse error has occured.  Source string: ', originalText)
        return originalText
    return originalText.replace(tag, numericString)



def _GenericHandler(originalText, tag, tagData):
    result = _ApplyModifiers(unicode(tagData['variableValue']), tagData)
    return originalText.replace(tag, result)



def _ApplyModifiers(message, tagData):
    if 'showInfolink' in tagData['args']:
        pass
    if 'capitalize' in tagData['args']:
        return message.capitalize()
    if 'uppercase' in tagData['args']:
        return message.upper()
    if 'lowercase' in tagData['args']:
        return message.lower()
    if 'titlecase' in tagData['args']:
        return message.title()
    return message



def _Tokenize(sourceText):
    sourceText = unicode(sourceText)
    sourceText = sourceText.replace('\r\n', ' ').replace('\n', ' ')
    tags = dict([ (each, None) for each in re.findall('(\\{(?!\\{).*?\\})', sourceText) ])
    for tag in tags.keys()[:]:
        originalTag = tag
        tag = tag[1:-1]
        if not len(tag.strip()):
            del tags[originalTag]
            continue
        tokens = re.split('(""|"[^"]+"|->|[:.,=])', tag)
        tokens = [ token.strip() for token in tokens if token if token.strip() ]
        token = tokens.pop(0)
        if token not in VARIABLE_TYPE_DATA:
            message = "Invalid datatype '" + token + "' in tag '" + originalTag + "' in string '" + sourceText + "'"
            localization.LogError(message)
            del tags[originalTag]
            continue
        variableType = token
        if len(tokens) < 2 or tokens[0] != ':':
            message = "Invalid datatype declaration in tag '" + originalTag + "' in string '" + sourceText + "'"
            localization.LogError(message)
            del tags[originalTag]
            continue
        tokens.pop(0)
        token = tokens.pop(0)
        if not _IsValidVariableName(token):
            message = "Invalid variable token '" + token + "' in tag '" + originalTag + "' in string '" + sourceText + "'"
            localization.LogError(message)
            del tags[originalTag]
            continue
        variableName = token
        for (tagName, tagInfo,) in [ (tagName, tagInfo) for (tagName, tagInfo,) in tags.iteritems() if tagInfo ]:
            if tagInfo['variableName'] == variableName and tagInfo['variableType'] != variableType:
                message = "Declaration error: '" + token + "' has already been declared as type '" + tagInfo['variableType'] + "'. Please check tag '" + tagName + "' in string '" + sourceText + "'"
                localization.LogError(message)
                del tags[tagName]
                continue

        propertyName = None
        tagArgs = []
        tagKwargs = {}
        isConditional = False
        conditionalValues = []
        if tokens and tokens[0] == '.':
            propertyName = tokens.pop(0)
            while tokens and tokens[0] != ',' and tokens[0] != '->':
                propertyName += tokens.pop(0)

            if not _IsValidAttributeName(propertyName):
                message = "Invalid property token '" + propertyName + "' in tag '" + originalTag + "' in string '" + sourceText + "'"
                localization.LogError(message)
                del tags[originalTag]
                continue
            propertyName = propertyName[1:]
        parseError = False
        if tokens and tokens[0] == ',':
            while tokens and tokens[0] == ',':
                tokens.pop(0)
                arg = tokens.pop(0)
                if tokens and tokens[0] == '=':
                    tokens.pop(0)
                    if tokens and tokens[0].isalnum():
                        tagKwargs[arg] = tokens.pop(0)
                    elif tokens and tokens[0].startswith('"') and tokens[0].endswith('"'):
                        tagKwargs[arg] = tokens.pop(0)[1:-1]
                    else:
                        parseError = True
                        message = repr(tokens[0]) + 'is not a valid keyword argument value.  Source tag: ' + repr(originalTag)
                        localization.LogError(message)
                        break
                else:
                    tagArgs.append(arg)

            if parseError:
                del tags[originalTag]
                continue
        elif tokens and tokens[0] == '->':
            validConditionalProperties = ('gender', 'genders', 'quantity')
            if propertyName not in validConditionalProperties:
                message = repr(variableName) + '.' + repr(propertyName) + ' is not a valid property; it cannot be used in conditional statements.  Valid properties are: ' + str(validConditionalProperties)
                localization.LogError(message)
                del tags[originalTag]
                continue
            else:
                isConditional = True
                tokens.pop(0)
                while tokens and len(tokens[0]) >= 2 and tokens[0].startswith('"') and tokens[0].endswith('"'):
                    conditionalValues.append(tokens[0][1:-1])
                    tokens.pop(0)
                    if tokens and tokens[0] == ',':
                        tokens.pop(0)
                    elif tokens:
                        parseError = True
                        message = "Unexpected token '" + repr(tokens[0]) + "' encountered. Source tag: " + repr(originalTag)
                        localization.LogError(message)

                if parseError:
                    del tags[originalTag]
                    continue
        if len(set(tagArgs).intersection(set(VARIABLE_TYPE_DATA[variableType]['args']))) < len(tagArgs):
            localization.LogError('Error in messageID ', messageID, " - Variable '", variableName, "' (type: ", variableType, ') contains an modifier not available for this type. Source string: ', sourceText, ' - Modifiers:', tagArgs)
            del tags[originalTag]
            continue
        if len(set(tagKwargs).intersection(set(VARIABLE_TYPE_DATA[variableType]['kwargs']))) < len(tagKwargs):
            localization.LogError('Error in messageID ', messageID, " - Variable '", variableName, "' (type: ", variableType, ') contains a keyword modifier not available for this type. Source string: ', sourceText, ' - Modifiers:', tagKwargs)
            del tags[originalTag]
            continue
        tags[originalTag] = {'variableType': variableType,
         'variableName': variableName,
         'variableValue': None,
         'propertyName': propertyName,
         'propertyValue': None,
         'isConditional': isConditional,
         'conditionalValues': conditionalValues,
         'args': tagArgs,
         'kwargs': tagKwargs}

    return tags



def _IsValidVariableName(string):
    results = re.findall('[a-zA-Z_]+\\w?', string)
    return results and results[0] == string



def _IsValidAttributeName(string):
    results = re.findall('[\\.[a-zA-Z_]+\\w*]*', string)
    return results and results[0] == string



def _GetPropertyValue(variableType, propertyName, value, languageID):
    if not propertyHandlersInitialized:
        _RegisterPropertyHandlers()
    return PROPERTY_HANDLERS[variableType](propertyName, value, languageID)



def _ProcessConditional(tagName, tag, languageID):
    try:
        if tag['propertyName'] == 'gender':
            if tag['propertyValue'] >= len(tag['conditionalValues']):
                localization.LogError('Insufficient parameters for gender conditional statement; source tag:', tagName)
                return tagName
            return tag['conditionalValues'][(tag['propertyValue'] % len(tag['conditionalValues']))]
        else:
            if tag['propertyName'] == 'quantity':
                quantityCategory = _GetQuantityCategory(tag['propertyValue'], languageID)
                if quantityCategory >= len(tag['conditionalValues']):
                    localization.LogError('Insufficient parameters for quantity conditional statement; quantity category is ', quantityCategory, ', but only ', len(tag['conditionalValues']), ' values were provided in the conditional statement.  Source tag:', tagName)
                    return tagName
                return tag['conditionalValues'][quantityCategory]
            localization.LogError("'", repr(tag['propertyName']), "' is not a valid property of '", repr(tag['variableName']), "', or someone forgot to write code to handle the '", repr(tag['propertyName']), "' property for the '", repr(tag['variableType']), "' variable type.")
            return tagName
    except TypeError as e:
        localization.LogError("'", repr(tag['propertyValue']), "' is not a valid value for '", repr(tag['variableName']), '.', repr(tag['propertyName']), "' property.")
        return tagName
    localization.LogError("Someone forgot to write code to handle the '", repr(tag['propertyName']), "' property for the '", repr(tag['variableType']), "' variable type.")
    return tagName



def _UndefinedPropertyHandlerFactory(variableName):
    return lambda propertyName, variableID, languageID: _UndefinedPropertyHandler(variableName, propertyName, variableID, languageID)



def _UndefinedPropertyHandler(variableName, propertyName, variableID, languageID):
    localization.LogError("No property handler defined for variables of type '", variableName, "' on ", boot.role, '.')
    return '?' + variableName + '.' + propertyName



def _GetQuantityCategory(quantity, languageID):
    try:
        return QUANTITY_CATEGORY_MAP[languageID](quantity)
    except KeyError as e:
        localization.LogError("No quantity category defined for language '", languageID, "'; defaulting to English rules.")
        return QUANTITY_CATEGORY_MAP['en-us'](quantity)



def _GetType1QuantityCategory(quantity):
    return 0



def _GetType2QuantityCategory(quantity):
    if quantity == 1 or quantity == -1:
        return 0
    else:
        return 1



def _GetType3QuantityCategory(quantity):
    if quantity < 0:
        quantity = -quantity
    if quantity != 11 and quantity % 10 == 1:
        return 0
    else:
        if (quantity < 12 or quantity > 14) and 2 <= quantity % 10 <= 4:
            return 1
        return 2


BASIC_TEXT_MODIFIERS = ['capitalize',
 'uppercase',
 'lowercase',
 'titlecase']
VARIABLE_TYPE_DATA = {'character': {'args': BASIC_TEXT_MODIFIERS + ['showInfolink'],
               'kwargs': [],
               'handlerFunction': _CharacterHandler},
 'item': {'args': BASIC_TEXT_MODIFIERS + ['showInfolink'],
          'kwargs': [],
          'handlerFunction': _ItemHandler},
 'location': {'args': BASIC_TEXT_MODIFIERS + ['showInfolink'],
              'kwargs': [],
              'handlerFunction': _LocationHandler},
 'characterlist': {'args': [],
                   'kwargs': [],
                   'handlerFunction': _CharacterListHandler},
 'message': {'args': BASIC_TEXT_MODIFIERS,
             'kwargs': [],
             'handlerFunction': _MessageHandler},
 'time': {'args': BASIC_TEXT_MODIFIERS + ['showInfolink'],
          'kwargs': ['date', 'time'],
          'handlerFunction': _TimeHandler},
 'formattedtime': {'args': BASIC_TEXT_MODIFIERS + ['showInfolink', 'showTimeZone'],
                   'kwargs': ['format'],
                   'handlerFunction': _FormattedTimeHandler},
 'quantitytime': {'args': BASIC_TEXT_MODIFIERS + ['showInfolink', 'writtenForm', 'condensedWrittenForm'],
                  'kwargs': ['from', 'to'],
                  'handlerFunction': _QuantityTimeHandler},
 'numeric': {'args': ['useGrouping'],
             'kwargs': ['decimalPlaces', 'leadingZeroes'],
             'handlerFunction': _NumericHandler},
 'generic': {'args': BASIC_TEXT_MODIFIERS,
             'kwargs': [],
             'handlerFunction': _GenericHandler}}
QUANTITY_CATEGORY_MAP = {'en-us': _GetType2QuantityCategory,
 'ja': _GetType1QuantityCategory,
 'ru': _GetType3QuantityCategory,
 'P1': _GetType2QuantityCategory}
exports = {'localization._Parse': _Parse,
 'localization.messageTagCache': messageTagCache,
 'localization.systemLocale': systemLocale}

