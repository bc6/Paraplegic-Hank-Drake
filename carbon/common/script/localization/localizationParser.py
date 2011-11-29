import localization
import localizationUtil
import localizationInternalUtil
import locale
import blue
import bluepy
import re
import copy
import time
import icu
initializePropertyHandlers = True
PROPERTY_HANDLERS = {'character': ('CharacterPropertyHandler', False),
 'characterlist': ('CharacterListPropertyHandler', False),
 'item': ('ItemPropertyHandler', False),
 'location': ('LocationPropertyHandler', False),
 'numeric': ('NumericPropertyHandler', False),
 'npcOrganization': ('NpcOrganizationPropertyHandler', False),
 'timeinterval': ('TimeIntervalPropertyHandler', False)}
systemLocale = icu.Locale.getBaseName(icu.Locale())
numericFormatter = None
numericFormatterEN_US = None
topLevelTagsRE = re.compile('(\\{(?!\\{).*?\\})')
tokensRE = re.compile('(""|"[^"]+"|->|[:.,=\\[\\]])')
validVariableNameRE = re.compile('[a-zA-Z_]+\\w?')
validAttributeNameRE = re.compile('[\\.[a-zA-Z_]+\\w*]*')
quoteWrappedStringRE = re.compile('"[^"]*"')
try:
    numericFormatter = icu.NumberFormat.createInstance(icu.Locale(systemLocale))
    numericFormatterEN_US = icu.NumberFormat.createInstance(icu.Locale('en_US'))
except icu.ICUError:
    pass
messageTagCache = {}

def _ClearParserCache():
    global messageTagCache
    messageTagCache = {}



def _FetchMessageTagsClient(messageID, languageID, sourceText):
    if messageID and messageID in messageTagCache:
        tags = messageTagCache[messageID]
    else:
        tags = _Tokenize(sourceText)
        if messageID is not None:
            messageTagCache[messageID] = copy.deepcopy(tags)
    return tags



def _FetchMessageTagsDefault(messageID, languageID, sourceText):
    if messageID and (messageID, languageID) in messageTagCache:
        tags = messageTagCache[(messageID, languageID)]
    else:
        tags = _Tokenize(sourceText)
        if messageID is not None:
            messageTagCache[(messageID, languageID)] = copy.deepcopy(tags)
    return tags



def _FetchMessageTags(messageID, languageID, sourceText):
    pass


if boot.role == 'client':
    _FetchMessageTags.func_code = _FetchMessageTagsClient.func_code
else:
    _FetchMessageTags.func_code = _FetchMessageTagsDefault.func_code

@bluepy.CCP_STATS_ZONE_FUNCTION
def _Parse(sourceText, messageID, languageID, returnErrors = False, **kwargs):
    tags = _FetchMessageTags(messageID, languageID, sourceText)
    if not tags:
        if returnErrors:
            return (sourceText, [])
        else:
            return sourceText
    tags = copy.deepcopy(tags)
    for (tagName, tag,) in tags.items():
        if tag['errors']:
            continue
        if tag['variableName'] in kwargs:
            tag['variableValue'] = kwargs[tag['variableName']]
        elif tag['variableName'] == 'player' and tag['variableType'] == 'character' and 'player' not in kwargs:
            if session.charid:
                tag['variableValue'] = session.charid
            else:
                message = _FormatErrorMessage(("Cannot render tag '",
                 tagName,
                 "' in messageID ",
                 messageID,
                 ": '",
                 tag['variableName'],
                 "' was not found in the keyword argument list and the player's charID could not be retrieved from the session automatically. Source string: ",
                 sourceText))
                localization.LogWarn(message)
                tag['errors'].append(message)
        else:
            message = _FormatErrorMessage(("Cannot render tag '",
             tagName,
             "' in messageID ",
             messageID,
             ": '",
             tag['variableName'],
             "' was not found in the keyword argument list. Source string: ",
             sourceText))
            localization.LogWarn(message)
            tag['errors'].append(message)
        if 'showinfo' in tag['kwargs']:
            try:
                tag['kwargs']['linkinfo'] = kwargs[tag['kwargs']['showinfo']]
            except KeyError as e:
                message = _FormatErrorMessage(("Cannot render tag '",
                 tagName,
                 "' in messageID ",
                 messageID,
                 ": 'linkinfo' kwarg '" + tag['kwargs']['showinfo'] + "' was not passed in as an input parameter. Source string: ",
                 sourceText))
                localization.LogError(message)
                tag['errors'].append(message)
        elif 'linkinfo' in tag['kwargs']:
            try:
                tag['kwargs']['linkinfo'] = kwargs[tag['kwargs']['linkinfo']]
            except KeyError as e:
                message = _FormatErrorMessage(("Cannot render tag '",
                 tagName,
                 "' in messageID ",
                 messageID,
                 ": 'linkinfo' kwarg '" + tag['kwargs']['linkinfo'] + "' was not passed in as an input parameter. Source string: ",
                 sourceText))
                localization.LogError(message)
                tag['errors'].append(message)
        if 'quantity' in VARIABLE_TYPE_DATA[tag['variableType']]['kwargs']:
            if 'quantity' in tag['kwargs']:
                try:
                    tag['kwargs']['quantity'] = kwargs[tag['kwargs']['quantity']]
                except KeyError as e:
                    localization.LogInfo("Cannot define quantity for variable '", tag['variableName'], "' in tag ", tagName, "' in messageID ", messageID, ": 'quantity' kwarg '", tag['kwargs']['quantity'], "' was not passed in as an input parameter. Defaulting quantity to 1. Source string: ", sourceText)
                    tag['kwargs']['quantity'] = 1
            else:
                tag['kwargs']['quantity'] = 1
        if tag['errors']:
            continue
        try:
            tag['propertyValue'] = _GetPropertyValue(tag['variableType'], tag['propertyName'], tag['variableValue'], languageID, *tag['args'], **tag['kwargs'])
        except Exception as e:
            tag['errors'].append('Exception when calling _GetPropertyValue with the following parameters: ' + str((tag['variableType'],
             tag['propertyName'],
             tag['variableValue'],
             languageID,
             tag['args'],
             tag['kwargs'])))
            tag['errors'].append('Details: ' + repr(e))
            continue
        if tag['propertyValue'] is None:
            continue
        if tag['variableValue'] is None:
            message = _FormatErrorMessage(("Cannot render tag '",
             tagName,
             "' in messageID ",
             messageID,
             ": '",
             tag['propertyName'] or tag['variableName'],
             "' is None. Source string: ",
             sourceText))
            localization.LogWarn(message)
            tag['errors'].append(message)
            continue
        if tag['isConditional']:
            replaceText = _ProcessConditional(tagName, tag, languageID)
            if replaceText:
                sourceText = sourceText.replace(tagName, replaceText)
        else:
            formatterFunction = VARIABLE_TYPE_DATA[tag['variableType']]['formatterFunction']
            sourceText = formatterFunction(sourceText, tagName, tag)

    if returnErrors:
        return (sourceText, reduce(lambda x, y: x + y, [ tag['errors'] for tag in tags.itervalues() ]))
    else:
        return sourceText



def _CharacterFormatter(originalText, tag, tagData):
    result = _ApplyModifiers(unicode(tagData['propertyValue']), tagData)
    return originalText.replace(tag, result)



def _NpcOrganizationFormatter(originalText, tag, tagData):
    result = _ApplyModifiers(unicode(tagData['propertyValue']), tagData)
    return originalText.replace(tag, result)



def _ItemFormatter(originalText, tag, tagData):
    result = _ApplyModifiers(unicode(tagData['propertyValue']), tagData)
    return originalText.replace(tag, result)



def _LocationFormatter(originalText, tag, tagData):
    result = _ApplyModifiers(unicode(tagData['propertyValue']), tagData)
    return originalText.replace(tag, result)



def _CharacterListFormatter(originalText, tag, tagData):
    result = _ApplyModifiers(unicode(tagData['propertyValue']), tagData)
    return originalText.replace(tag, result)



def _MessageFormatter(originalText, tag, tagData):
    result = _ApplyModifiers(unicode(localization.GetByMessageID(tagData['variableValue'])), tagData)
    return originalText.replace(tag, result)



@bluepy.CCP_STATS_ZONE_FUNCTION
def _DateTimeFormatter(originalText, tag, tagData):
    value = tagData['variableValue']
    dateFormat = tagData['kwargs'].get('date', 'short')
    timeFormat = tagData['kwargs'].get('time', 'short')
    dateTimeString = localizationUtil.FormatDateTime(value, dateFormat=dateFormat, timeFormat=timeFormat)
    if not dateTimeString:
        message = _FormatErrorMessage(('An error occurred in localizationUtil.FormatDateTime while attempting to process a tag.  Source string: ', originalText))
        localization.LogError(message)
        tagData['errors'].append(message)
        return originalText
    result = _ApplyModifiers(dateTimeString, tagData)
    return originalText.replace(tag, result)



@bluepy.CCP_STATS_ZONE_FUNCTION
def _FormattedTimeFormatter(originalText, tag, tagData):
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
        message = _FormatErrorMessage(('formattedtime only accepts blue time, struct_time, or tuples as values, but we recieved a ',
         type(value).__name__,
         '.  Source string: ',
         originalText))
        localization.LogError(message)
        tagData['errors'].append(message)
        return originalText
    dateTimeString = time.strftime(formatString, value)
    result = _ApplyModifiers(unicode(dateTimeString), tagData)
    return originalText.replace(tag, result)



@bluepy.CCP_STATS_ZONE_FUNCTION
def _TimeIntervalFormatter(originalText, tag, tagData):
    result = _ApplyModifiers(unicode(tagData['propertyValue']), tagData)
    return originalText.replace(tag, result)



@bluepy.CCP_STATS_ZONE_FUNCTION
def _NumericFormatter(originalText, tag, tagData):
    if tagData['propertyValue'] != tagData['variableValue']:
        numericString = tagData['propertyValue']
    else:
        value = tagData['variableValue']
        useGrouping = 'useGrouping' in tagData['args']
        decimalPlaces = int(tagData['kwargs']['decimalPlaces']) if 'decimalPlaces' in tagData['kwargs'] else None
        leadingZeroes = int(tagData['kwargs']['leadingZeroes']) if 'leadingZeroes' in tagData['kwargs'] else None
        numericString = localizationUtil.FormatNumeric(value, useGrouping=useGrouping, decimalPlaces=decimalPlaces, leadingZeroes=leadingZeroes)
        if not numericString:
            message = _FormatErrorMessage(('An error occurred in localizationUtil.FormatNumeric while attempting to process a tag.  Source string: ', originalText))
            localization.LogError(message)
            tagData['errors'].append(message)
            return originalText
    return originalText.replace(tag, numericString)



@bluepy.CCP_STATS_ZONE_FUNCTION
def _GenericFormatter(originalText, tag, tagData):
    result = tagData['variableValue']
    if not isinstance(result, basestring):
        result = unicode(result)
    result = _ApplyModifiers(result, tagData)
    return originalText.replace(tag, result)



@bluepy.CCP_STATS_ZONE_FUNCTION
def _ApplyModifiers(message, tagData):
    if 'capitalize' in tagData['args']:
        message = message.capitalize()
    elif 'uppercase' in tagData['args']:
        message = message.upper()
    elif 'lowercase' in tagData['args']:
        message = message.lower()
    elif 'titlecase' in tagData['args']:
        message = message.title()
    if 'linkify' in tagData['args'] and 'linkinfo' in tagData['kwargs']:
        message = _FormatErrorMessage("It is not possible to use both 'linkify' and 'linkinfo' parameters in the same tag.")
        localization.LogError(message)
        tagData['errors'].append(message)
    if 'linkify' in tagData['args']:
        variableType = tagData['variableType']
        if variableType in PROPERTY_HANDLERS:
            propertyHandler = PROPERTY_HANDLERS[variableType][0]
            message = propertyHandler.Linkify(tagData['variableValue'], message)
        else:
            errorMessage = _FormatErrorMessage(("Could not process the 'linkify' argument because no property handler could be found for the referenced variable type '", variableType, "'."))
            localization.LogError(errorMessage)
            tagData['errors'].append(errorMessage)
    if 'linkinfo' in tagData['kwargs']:
        linkData = tagData['kwargs']['linkinfo']
        message = '<a href=' + linkData[0] + ':' + '//'.join([ str(each) for each in linkData[1:] ]) + '>' + message + '</a>'
    return message



@bluepy.CCP_STATS_ZONE_FUNCTION
def _Tokenize(sourceText):
    sourceText = sourceText.replace('\r\n', ' ').replace('\n', ' ')
    tags = dict([ (each, None) for each in topLevelTagsRE.findall(sourceText) ])
    for tag in tags.keys()[:]:
        errors = []
        originalTag = tag
        tag = tag[1:-1]
        if not len(tag.strip()):
            del tags[originalTag]
            continue
        tokens = tokensRE.split(tag)
        originalTokens = [ token for token in tokens if token ]
        tokens = [ token.strip() for token in tokens if token if token.strip() ]
        try:
            variableName = None
            variableType = None
            propertyName = None
            tagArgs = []
            tagKwargs = {}
            isConditional = False
            conditionalValues = []
            token = tokens.pop(0)
            if token == '[':
                variableType = tokens.pop(0)
                if variableType not in VARIABLE_TYPE_DATA:
                    raise SyntaxError, "'" + variableType + "' is not a valid variable type"
                next = tokens.pop(0)
                if next != ']':
                    raise SyntaxError, "Expected ']' but got '%s'" % next
                variableName = tokens.pop(0)
            else:
                variableType = 'generic'
                variableName = token
            if not _IsValidVariableName(variableName):
                raise SyntaxError, 'Variable names must be alphanumeric, and begin with a letter or underscore'
            for (tagName, tagInfo,) in [ (tagName, tagInfo) for (tagName, tagInfo,) in tags.iteritems() if tagInfo ]:
                if tagInfo['variableName'] == variableName and tagInfo['variableType'] != variableType:
                    raise TypeError, "'" + variableName + "' already declared as type '" + tagInfo['variableType'] + "'."

            if tokens:
                next = tokens.pop(0)
                if next == '.':
                    propertyName = tokens.pop(0)
                    if tokens:
                        next = tokens.pop(0)
            if tokens:
                if next == '->':
                    isConditional = True
                    if variableType in VARIABLE_TYPE_DATA and 'conditionalProperties' in VARIABLE_TYPE_DATA[variableType] and propertyName not in VARIABLE_TYPE_DATA[variableType]['conditionalProperties']:
                        raise TypeError, 'You cannot use ' + unicode(variableName) + '.' + unicode(propertyName) + ' in conditional statements.  Valid properties for this variable type are: ' + str(VARIABLE_TYPE_DATA[variableType]['conditionalProperties'])
                    conditionalValue = tokens.pop(0)
                    if not _IsQuoteWrappedString(conditionalValue):
                        raise SyntaxError, "Error parsing conditional value '" + conditionalValue + "'"
                    conditionalValues.append(conditionalValue[1:-1])
                    while tokens:
                        next = tokens.pop(0)
                        if next != ',':
                            raise SyntaxError, "Expected ',' but got '%s'" % next
                        conditionalValue = tokens.pop(0)
                        if not _IsQuoteWrappedString(conditionalValue):
                            raise SyntaxError, "Error parsing conditional value '" + conditionalValue + "'"
                        conditionalValues.append(conditionalValue[1:-1])

                elif next == ',':
                    while tokens:
                        arg = tokens.pop(0).encode('ascii')
                        next = tokens.pop(0) if len(tokens) else None
                        if next in (',', None):
                            if arg not in VARIABLE_TYPE_DATA[variableType]['args']:
                                raise SyntaxError, "Modifier '" + arg + "' cannot be used with variables of type '" + variableType + "'"
                            tagArgs.append(arg)
                        elif next == '=':
                            kwargValue = tokens.pop(0)
                            if _IsQuoteWrappedString(kwargValue):
                                kwargValue = kwargValue[1:-1]
                            elif not kwargValue.isalnum():
                                raise ValueError, 'Conditional arguments must be an alphanumeric value or double-quoted string'
                            if arg not in VARIABLE_TYPE_DATA[variableType]['kwargs']:
                                raise SyntaxError, "Modifier '" + arg + "' cannot be used with variables of type '" + variableType + "'"
                            tagKwargs[arg] = kwargValue.encode('ascii')
                            next = tokens.pop(0) if len(tokens) else None
                            if next not in (',', None):
                                raise SyntaxError, "Expected ',' but got '%s'" % next
                        else:
                            raise SyntaxError, "Expected ',' or '=' but got '%s'" % next

                else:
                    raise SyntaxError, "Expected ',' but got '%s'" % next
        except (TypeError,
         ValueError,
         SyntaxError,
         IndexError) as e:
            partialTag = '{' + ''.join([ originalTokens[i] for i in xrange(len(originalTokens) - len(tokens)) ])
            message1 = 'Tokenizer error: ' + repr(e) + ' -- Stopped parsing at: ' + partialTag
            message2 = "Source tag '" + originalTag + "' Source string: '" + sourceText + "'"
            errors.append(message1)
            errors.append(message2)
            localization.LogError(message1)
            localization.LogError(message2)
        tags[originalTag] = {'variableType': variableType.encode('ascii') if variableType is not None else None,
         'variableName': variableName.encode('ascii') if variableName is not None else None,
         'variableValue': None,
         'propertyName': propertyName.encode('ascii') if propertyName is not None else None,
         'propertyValue': None,
         'isConditional': isConditional,
         'conditionalValues': conditionalValues,
         'args': tagArgs,
         'kwargs': tagKwargs,
         'errors': errors}

    return tags



def _IsValidVariableName(string):
    results = validVariableNameRE.findall(string)
    return results and results[0] == string



def _IsValidAttributeName(string):
    results = validVariableNameRE.findall(string)
    return results and results[0] == string



def _IsQuoteWrappedString(string):
    matches = quoteWrappedStringRE.findall(string)
    return len(matches) and matches[0] == string



@bluepy.CCP_STATS_ZONE_FUNCTION
def _GetPropertyValue(variableType, propertyName, value, languageID, *args, **kwargs):
    (propertyHandler, created,) = PROPERTY_HANDLERS.get(variableType, (None, None))
    if propertyHandler is None:
        if propertyName:
            localization.LogError("No property handler defined for variable type '", variableType, "'.")
            return 
        else:
            return value
    if not created:
        className = propertyHandler
        propertyHandler = getattr(localization, className)()
        PROPERTY_HANDLERS[variableType] = (propertyHandler, True)
    return propertyHandler.GetProperty(propertyName, value, languageID, *args, **kwargs)



@bluepy.CCP_STATS_ZONE_FUNCTION
def _ProcessConditional(tagName, tag, languageID):
    try:
        if VARIABLE_TYPE_DATA[tag['variableType']]['conditionalProperties'][tag['propertyName']] in (CONDITIONAL_TYPE_GENDER, CONDITIONAL_TYPE_GENDERS):
            if tag['propertyValue'] >= len(tag['conditionalValues']):
                message = _FormatErrorMessage(('Insufficient parameters for gender conditional statement; source tag:', tagName))
                localization.LogError(message)
                tag['errors'].append(message)
                return tagName
            return tag['conditionalValues'][(tag['propertyValue'] % len(tag['conditionalValues']))]
        else:
            if VARIABLE_TYPE_DATA[tag['variableType']]['conditionalProperties'][tag['propertyName']] == CONDITIONAL_TYPE_QUANTITY:
                try:
                    quantityCategory = _GetQuantityCategory(tag['propertyValue'], languageID)
                except KeyError as e:
                    message = _FormatErrorMessage(("No quantity category defined for language '", languageID, "'; cannot parse conditional statement."))
                    localization.LogError(message)
                    tag['errors'].append(message)
                    return tagName
                if quantityCategory >= len(tag['conditionalValues']):
                    message = _FormatErrorMessage(('Insufficient parameters for quantity conditional statement; quantity category is ',
                     quantityCategory,
                     ', but only ',
                     len(tag['conditionalValues']),
                     ' values were provided in the conditional statement.  Source tag:',
                     tagName))
                    localization.LogError(message)
                    tag['errors'].append(message)
                    return tagName
                return tag['conditionalValues'][quantityCategory]
            message = _FormatErrorMessage(("'",
             repr(tag['propertyName']),
             "' is not a valid conditional property for the variable '",
             repr(tag['variableName']),
             "', or someone forgot to write code to handle the '",
             repr(tag['propertyName']),
             "' property for the '",
             repr(tag['variableType']),
             "' variable type."))
            localization.LogError(message)
            tag['errors'].append(message)
            return tagName
    except TypeError as e:
        message = _FormatErrorMessage(("'",
         repr(tag['propertyValue']),
         "' is not a valid value for '",
         repr(tag['variableName']),
         '.',
         repr(tag['propertyName']),
         "' property.  Details: ",
         e))
        localization.LogError(message)
        tag['errors'].append(message)
        return tagName
    message = _FormatErrorMessage(("Someone forgot to write code to handle the '",
     repr(tag['propertyName']),
     "' property for the '",
     repr(tag['variableType']),
     "' variable type."))
    localization.LogError(message)
    tag['errors'].append(message)
    return tagName



def _GetQuantityCategory(quantity, languageID):
    return QUANTITY_CATEGORY_MAP[languageID](quantity)



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
    if not isinstance(quantity, (int, long)):
        return 2
    else:
        if quantity != 11 and quantity % 10 == 1:
            return 0
        if (quantity < 12 or quantity > 14) and 2 <= quantity % 10 <= 4:
            return 1
        return 2



def _FormatErrorMessage(args):
    return ''.join(map(unicode, args))


BASIC_TEXT_MODIFIERS = ['capitalize',
 'uppercase',
 'lowercase',
 'titlecase']
BASIC_TEXT_SETTINGS = ['linkinfo', 'showinfo']
CONDITIONAL_TYPE_GENDER = 'gender'
CONDITIONAL_TYPE_GENDERS = 'genders'
CONDITIONAL_TYPE_QUANTITY = 'quantity'
VARIABLE_TYPE_DATA = {'character': {'args': BASIC_TEXT_MODIFIERS + ['linkify'],
               'kwargs': BASIC_TEXT_SETTINGS,
               'formatterFunction': _CharacterFormatter,
               'conditionalProperties': {'gender': CONDITIONAL_TYPE_GENDER}},
 'npcOrganization': {'args': BASIC_TEXT_MODIFIERS + ['linkify'],
                     'kwargs': BASIC_TEXT_SETTINGS,
                     'formatterFunction': _NpcOrganizationFormatter,
                     'conditionalProperties': {'gender': CONDITIONAL_TYPE_GENDER}},
 'item': {'args': BASIC_TEXT_MODIFIERS + ['linkify'],
          'kwargs': BASIC_TEXT_SETTINGS + ['quantity'],
          'formatterFunction': _ItemFormatter,
          'conditionalProperties': {'gender': CONDITIONAL_TYPE_GENDER,
                                    'quantity': CONDITIONAL_TYPE_QUANTITY}},
 'location': {'args': BASIC_TEXT_MODIFIERS + ['linkify'],
              'kwargs': BASIC_TEXT_SETTINGS,
              'formatterFunction': _LocationFormatter,
              'conditionalProperties': {'gender': CONDITIONAL_TYPE_GENDER}},
 'characterlist': {'args': [],
                   'kwargs': BASIC_TEXT_SETTINGS,
                   'formatterFunction': _CharacterListFormatter,
                   'conditionalProperties': {'genders': CONDITIONAL_TYPE_GENDERS,
                                             'quantity': CONDITIONAL_TYPE_QUANTITY}},
 'messageid': {'args': BASIC_TEXT_MODIFIERS,
               'kwargs': BASIC_TEXT_SETTINGS,
               'formatterFunction': _MessageFormatter},
 'datetime': {'args': BASIC_TEXT_MODIFIERS,
              'kwargs': BASIC_TEXT_SETTINGS + ['date', 'time'],
              'formatterFunction': _DateTimeFormatter},
 'formattedtime': {'args': BASIC_TEXT_MODIFIERS,
                   'kwargs': BASIC_TEXT_SETTINGS + ['format'],
                   'formatterFunction': _FormattedTimeFormatter},
 'timeinterval': {'args': BASIC_TEXT_MODIFIERS,
                  'kwargs': BASIC_TEXT_SETTINGS + ['from', 'to'],
                  'formatterFunction': _TimeIntervalFormatter},
 'numeric': {'args': ['useGrouping'],
             'kwargs': BASIC_TEXT_SETTINGS + ['decimalPlaces', 'leadingZeroes'],
             'formatterFunction': _NumericFormatter,
             'conditionalProperties': {None: CONDITIONAL_TYPE_QUANTITY}},
 'generic': {'args': BASIC_TEXT_MODIFIERS,
             'kwargs': BASIC_TEXT_SETTINGS,
             'formatterFunction': _GenericFormatter}}
QUANTITY_CATEGORY_MAP = {'en-us': _GetType2QuantityCategory,
 'de': _GetType2QuantityCategory,
 'ja': _GetType1QuantityCategory,
 'ru': _GetType3QuantityCategory,
 'zh-Hans': _GetType1QuantityCategory}
exports = {'localization._Parse': _Parse,
 'localization._Tokenize': _Tokenize,
 'localization._ClearParserCache': _ClearParserCache,
 'localization.systemLocale': systemLocale,
 'localization.numericFormatter': numericFormatter,
 'localization.numericFormatterEN_US': numericFormatterEN_US}

