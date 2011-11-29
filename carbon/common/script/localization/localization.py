import __builtin__
import cPickle as pickle
import blue
import bluepy
import miscUtil
import log
import localization
import localizationUtil
import localizationInternalUtil
import uthread
import service
import hashlib
kwargCallCounter = blue.statistics.Find('Cerberus/kwargCallCounter')
if not kwargCallCounter:
    kwargCallCounter = blue.CcpStatisticsEntry()
    kwargCallCounter.name = 'Cerberus/kwargCallCounter'
    kwargCallCounter.type = 1
    kwargCallCounter.resetPerFrame = False
    kwargCallCounter.description = 'The number of calls to _GetByMessageID with specifying kwargs'
    blue.statistics.Register(kwargCallCounter)
noKwargCallCounter = blue.statistics.Find('Cerberus/noKwargCallCounter')
if not noKwargCallCounter:
    noKwargCallCounter = blue.CcpStatisticsEntry()
    noKwargCallCounter.name = 'Cerberus/noKwargCallCounter'
    noKwargCallCounter.type = 1
    noKwargCallCounter.resetPerFrame = False
    noKwargCallCounter.description = 'The number of calls to _GetByMessageID without specifying kwargs'
    blue.statistics.Register(noKwargCallCounter)
logChannel = log.GetChannel('Localization')

def LogInfo(*args):
    logChannel.Log('Localization module: ' + ''.join(map(strx, args)), logChannel.flags['INFO'])



def LogWarn(*args):
    logChannel.Log('Localization module: ' + ''.join(map(strx, args)), logChannel.flags['WARN'])



def LogError(*args):
    logChannel.Log('Localization module: ' + ''.join(map(strx, args)), logChannel.flags['ERR'])



def LogTraceback(*args):
    logChannel.Log('Localization module: ' + ''.join(map(strx, args)), logChannel.flags['ERR'])
    log.LogTraceback('Localization module: ' + ''.join(map(strx, args)), channel='Localization', toConsole=0, toAlertSvc=0, severity=1, show_locals=0)



class Localization(object):
    __guid__ = 'localization.Localization'
    PICKLE_PREFIX = 'localization_'
    PICKLE_MAIN_NAME = 'localization_main'
    PICKLE_EXT = '.pickle'
    COMMON_RESOURCE_PATH = 'res:/localization/'
    FIELD_LABELS = 'labels'
    FIELD_LANGUAGES = 'languages'
    FIELD_MAPPING = 'mapping'
    FIELD_REGISTRATION = 'registration'
    FIELD_TYPES = 'types'
    FIELD_MAX_REVISION = 'maxRevision'
    LANGUAGE_FIELD_TEXTS = 1
    LANGUAGE_FIELD_DATA = 2

    def __init__(self):
        self._InitializeInternalVariables()
        self._InitializeTextData()
        uthread.worker('localization::_SetHardcodedStringDetection', self._SetHardcodedStringDetection)
        if not self._ReadLocalizationMainPickle():
            message = 'Cerberus localization module failed to load MAIN pickle on ' + boot.role + '.  See log server for details.'
            LogError(message)
            print message
            return 
        self._ValidateAndRepairPrefs()
        if not self._ReadLocalizationLanguagePickles():
            message = 'Cerberus localization module failed to load language pickles on ' + boot.role + '. See log server for details.'
            LogError(message)
            print message
            return 
        message = 'Cerberus localization module loaded on ' + boot.role
        LogInfo(message)
        print message



    def GetLanguages(self):
        langs = self.languagesDefined.keys()
        return langs



    @bluepy.CCP_STATS_ZONE_METHOD
    def LoadPrimaryLanguage(self, languageID = localization.LOCALE_SHORT_ENGLISH):
        languageID = localizationInternalUtil.StandardizeLanguageID(languageID)
        self._UnloadLanguageLocalizationData(self._primaryLanguageID)
        self._primaryLanguageID = languageID
        if self._primaryLanguageID in self.languagesDefined:
            if not self._LoadLanguagePickle(self._primaryLanguageID):
                return False
        else:
            LogError("Language '", languageID, "' is not enabled. Text data was not loaded.")
            return False
        return True



    @bluepy.CCP_STATS_ZONE_METHOD
    def LoadSecondaryLanguage(self, languageID):
        if boot.role != 'client':
            return False
        languageID = localizationInternalUtil.StandardizeLanguageID(languageID)
        self._UnloadLanguageLocalizationData(self._secondaryLanguageID)
        if languageID == self._primaryLanguageID:
            self._secondaryLanguageID = None
            return True
        self._secondaryLanguageID = languageID
        if self._secondaryLanguageID in self.languagesDefined:
            if not self._LoadLanguagePickle(self._secondaryLanguageID):
                return False
        else:
            LogError("Language '", languageID, "' is not enabled. Text data was not loaded.")
            return False
        return True



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetByMapping(self, resourceName, keyID, propertyName = None, languageID = None, **kwargs):
        try:
            tableRegID = self.tableRegistration[resourceName]
            messageID = self.messageMapping[(tableRegID, keyID)]
        except KeyError as e:
            LogTraceback("No mapping entry for '", resourceName, "' with keyID ", keyID, '.  Usually this is either because the source column was NULL for this row (NULL entries are not imported), or because the source column has been deleted on the content database, but not the database you are using.')
            return u'[no resource: %s, %s]' % (resourceName, keyID)
        if propertyName is None:
            return self.GetByMessageID(messageID, languageID, **kwargs)
        else:
            return self.GetMetaData(messageID, propertyName, languageID)



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetByMessageID(self, messageID, languageID = None, **kwargs):
        if messageID is None:
            return ''
        if languageID is not None:
            languageID = localizationInternalUtil.StandardizeLanguageID(languageID)
        if languageID is None:
            languageID = localizationUtil.GetLanguageID()
        textString = self._GetByMessageID(messageID, languageID, **kwargs)
        if textString is not None:
            return localizationInternalUtil.PrepareLocalizationSafeString(textString, messageID=messageID)
        return u'[no messageID: %s]' % messageID



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetByLabel(self, labelNameAndPath, languageID = None, **kwargs):
        try:
            messageID = self.languageLabels[labelNameAndPath]
        except KeyError:
            LogTraceback("No label with name '", labelNameAndPath, "'.")
            return '[no label: %s]' % labelNameAndPath
        return self.GetByMessageID(messageID, languageID, **kwargs)



    def IsValidMessageID(self, messageID, languageID = None):
        languageID = languageID or localizationUtil.GetLanguageID()
        text = self.languageTexts.get(languageID, {}).get(messageID, None)
        if text is None:
            return False
        else:
            return True



    def IsValidLabel(self, labelNameAndPath, languageID = None):
        messageID = self.languageLabels.get(labelNameAndPath, None)
        return self.IsValidMessageID(messageID, languageID)



    def IsValidMapping(self, resourceName, keyID):
        if resourceName in self.tableRegistration:
            return (self.tableRegistration[resourceName], keyID) in self.messageMapping
        return False



    def IsValidMetaDataByMapping(self, resourceName, keyID, propertyName, languageID = None):
        tableRegID = self.tableRegistration.get(resourceName, None)
        messageID = None
        if tableRegID is not None:
            messageID = self.messageMapping.get((tableRegID, keyID), None)
        if messageID is not None:
            return self.IsValidMetaDataByMessageID(messageID, propertyName, languageID)
        else:
            return False



    def IsValidMetaDataByMessageID(self, messageID, propertyName, languageID = None):
        languageID = localizationInternalUtil.StandardizeLanguageID(languageID) or localizationUtil.GetLanguageID()
        metaData = self.languageMetaData.get(languageID, {}).get(messageID, {}).get(propertyName, None)
        if metaData is None:
            return False
        else:
            return True



    def IsValidTypeAndProperty(self, typeName, propertyName, languageID = None):
        IS_INVALID_TYPE = 0
        IS_INVALID_PROPERTY = 1
        IS_VALID_TYPE_AND_PROPERTY = 2
        result = None
        languageID = localizationInternalUtil.StandardizeLanguageID(languageID) or localizationUtil.GetLanguageID()
        foundType = self.languageTypesWithProperties.get(typeName, None)
        if foundType is not None:
            foundPropertyList = foundType.get(languageID, None)
            if foundPropertyList is not None:
                if propertyName in foundPropertyList:
                    result = IS_VALID_TYPE_AND_PROPERTY
                else:
                    result = IS_INVALID_PROPERTY
            else:
                result = IS_INVALID_PROPERTY
        else:
            result = IS_INVALID_TYPE
        if result == IS_INVALID_PROPERTY:
            LogError("'%s' is not a valid property for '%s' in language '%s'." % (propertyName, typeName, languageID))
        elif result == IS_INVALID_TYPE:
            LogError("'%s' is not a valid type; cannot retrieve properties for it." % typeName)
        elif result is None:
            LogError('IsValidTypeAndProperty wasnt able to determine if type and property were valid: %s, %s' % (typeName, propertyName))
        return result == IS_VALID_TYPE_AND_PROPERTY



    def GetMetaData(self, messageID, propertyName, languageID = None):
        languageID = localizationInternalUtil.StandardizeLanguageID(languageID) or localizationUtil.GetLanguageID()
        propertyString = self._GetMetaData(messageID, propertyName, languageID)
        if propertyString is not None:
            return localizationInternalUtil.PrepareLocalizationSafeString(propertyString, messageID=messageID)
        LogError('a non existent property was requested. messageID,propertyName,languageID : %s,%s,%s' % (messageID, propertyName, languageID))
        return '[no property:%s,%s]' % (messageID, propertyName)



    def GetAllMetaData(self, messageID):
        propertiesDict = None
        if len(self.languageMetaData) > 0:
            propertiesDict = {}
            for aLanguageID in self.languageMetaData:
                propertiesDict[aLanguageID] = self._GetAllMetaDataPerLanguage(messageID, aLanguageID)

        return propertiesDict



    def GetAllMetaDataPerLanguage(self, messageID, languageID = None):
        languageID = localizationInternalUtil.StandardizeLanguageID(languageID) or localizationUtil.GetLanguageID()
        return self._GetAllMetaDataPerLanguage(messageID, languageID)



    def GetPlaceholderLabel(self, englishText, **kwargs):
        parsedText = localization._Parse(englishText, None, localization.LOCALE_SHORT_ENGLISH, **kwargs)
        LogWarn('Placeholder label (%s) needs to be replaced.' % englishText)
        return localizationInternalUtil.PreparePlaceholderString('!_%s_!' % parsedText)



    def _ValidateAndRepairPrefs(self):
        if boot.role == 'client':
            while not hasattr(__builtin__, 'prefs'):
                blue.synchro.Yield()

            prefsLanguage = prefs.GetValue('languageID', None)
            if localizationInternalUtil.ConvertToLanguageSet('MLS', 'languageID', prefsLanguage) not in self.GetLanguages():
                prefs.languageID = 'EN' if boot.region != 'optic' else 'ZH'



    def _ReadMainLocalizationData(self, unPickledObject):
        self._ClearTextData()
        if unPickledObject and self.FIELD_LABELS in unPickledObject:
            labelsDict = unPickledObject[self.FIELD_LABELS]
            for aMessageID in labelsDict:
                dataRow = labelsDict[aMessageID]
                pathAndLabelKey = None
                if dataRow[localization.COLUMN_FULLPATH]:
                    aFullPath = dataRow[localization.COLUMN_FULLPATH]
                    pathAndLabelKey = aFullPath + localization.FOLDER_NAME_CHAR_SEPARATOR + dataRow[localization.COLUMN_LABEL]
                else:
                    pathAndLabelKey = dataRow[localization.COLUMN_LABEL]
                self.languageLabels[pathAndLabelKey] = aMessageID

        else:
            LogError("didn't find 'labels' in the unpickled object. File name = %s" % (self.PICKLE_MAIN_NAME + self.PICKLE_EXT))
            return False
        if self.FIELD_LANGUAGES in unPickledObject:
            self.languagesDefined = unPickledObject[self.FIELD_LANGUAGES]
        else:
            LogError("didn't find 'languages' in the unpickled object. File name = %s" % (self.PICKLE_MAIN_NAME + self.PICKLE_EXT))
            return False
        if self.FIELD_REGISTRATION in unPickledObject and self.FIELD_MAPPING in unPickledObject:
            self.tableRegistration = unPickledObject[self.FIELD_REGISTRATION]
            self.messageMapping = unPickledObject[self.FIELD_MAPPING]
        else:
            LogError("didn't find 'mapping' or 'registration' in the unpickled object. File name = %s" % (self.PICKLE_MAIN_NAME + self.PICKLE_EXT))
            return False
        if self.FIELD_TYPES in unPickledObject:
            self.languageTypesWithProperties = unPickledObject[self.FIELD_TYPES]
        else:
            LogError("didn't find 'types' in the unpickled object. File name = %s" % (self.PICKLE_MAIN_NAME + self.PICKLE_EXT))
            return False
        if self.FIELD_MAX_REVISION in unPickledObject:
            self.maxRevision = unPickledObject[self.FIELD_MAX_REVISION]
        else:
            LogError("didn't find 'maxRevision' in the unpickled object. File name = %s" % (self.PICKLE_MAIN_NAME + self.PICKLE_EXT))
            return False
        return True



    def _UnloadLanguageLocalizationData(self, aLangCode):
        textData = self.languageTexts.get(aLangCode, None)
        if textData is not None:
            del self.languageTexts[aLangCode]
        metaData = self.languageMetaData.get(aLangCode, None)
        if metaData is not None:
            del self.languageMetaData[aLangCode]



    def _ReadLanguageLocalizationData(self, aLangCode, unPickledObject):
        if unPickledObject:
            self._UnloadLanguageLocalizationData(aLangCode)
            self.languageTexts[aLangCode] = unPickledObject[self.LANGUAGE_FIELD_TEXTS]
            self.languageMetaData[aLangCode] = unPickledObject[self.LANGUAGE_FIELD_DATA]
        else:
            LogError("didn't find required parts in unpickled object. File name = %s" % (self.PICKLE_PREFIX + aLangCode + self.PICKLE_EXT))
            return False
        self._UpdateInternalMemoryWithCache()
        return True



    def _ClearTextData(self):
        del self.languagesDefined
        del self.languageLabels
        del self.languageTexts
        del self.languageMetaData
        del self.languageTypesWithProperties
        del self.tableRegistration
        del self.messageMapping
        self._InitializeTextData()



    def _InitializeInternalVariables(self):
        self.textDataCache = {'messagePerLanguage': {},
         'metaDataPerLanguage': {},
         'labelsDict': {}}
        self.textDataCacheSet = False
        self.hashDataDictionary = {}



    def _InitializeTextData(self):
        self.languagesDefined = {}
        self.languageLabels = {}
        self.languageTexts = {}
        self.languageMetaData = {}
        self.languageTypesWithProperties = {}
        self.tableRegistration = {}
        self.messageMapping = {}
        self.maxRevision = None
        self._primaryLanguageID = None
        self._secondaryLanguageID = None



    def UpdateTextCache(self, messagePerLanguage, metaDataPerLanguage, labelsDict):
        LogInfo('Preparing to update internal text and label cache. The sizes of new data dictionaries are: ', len(messagePerLanguage), ', ', len(metaDataPerLanguage), ', ', len(labelsDict))
        self.textDataCacheSet = True
        localizationInternalUtil.UpdateDictionary(self.textDataCache['messagePerLanguage'], messagePerLanguage)
        localizationInternalUtil.UpdateDictionary(self.textDataCache['metaDataPerLanguage'], metaDataPerLanguage)
        localizationInternalUtil.UpdateDictionary(self.textDataCache['labelsDict'], labelsDict)
        self._UpdateInternalMemoryWithCache()



    def GetTextDataCache(self):
        return self.textDataCache



    def GetMaxRevision(self):
        return self.maxRevision



    def GetHashDataDictionary(self):
        return self.hashDataDictionary



    def _UpdateInternalMemoryWithCache(self):
        if self.textDataCacheSet:
            localizationInternalUtil.UpdateDictionary(self.languageTexts, self.textDataCache['messagePerLanguage'])
            localizationInternalUtil.UpdateDictionary(self.languageMetaData, self.textDataCache['metaDataPerLanguage'])
            localizationInternalUtil.UpdateDictionary(self.languageLabels, self.textDataCache['labelsDict'])



    def _ReadLocalizationMainPickle(self):
        unPickledObject = self._LoadPickleData(self.PICKLE_MAIN_NAME + self.PICKLE_EXT)
        if unPickledObject == None:
            return False
        readStatus = self._ReadMainLocalizationData(unPickledObject)
        del unPickledObject
        if readStatus == False:
            return False
        return True



    def _ReadLocalizationLanguagePickles(self):
        if boot.role == 'client':
            prefsLanguage = prefs.GetValue('languageID', None)
            if not (self.LoadPrimaryLanguage() and self.LoadSecondaryLanguage(prefsLanguage)):
                return False
        elif boot.role == 'server' or boot.role == 'proxy':
            if not self.LoadPrimaryLanguage():
                return False
            for aLangCode in self.languagesDefined:
                if aLangCode != self._primaryLanguageID and not self._LoadLanguagePickle(aLangCode):
                    return False

        return True



    def _LoadLanguagePickle(self, languageID):
        unPickledObject = self._LoadPickleData(self.PICKLE_PREFIX + languageID + self.PICKLE_EXT)
        if unPickledObject == None:
            return False
        readStatus = self._ReadLanguageLocalizationData(languageID, unPickledObject)
        del unPickledObject
        return readStatus



    def _LoadPickleData(self, pickleName):
        pickleFile = miscUtil.GetCommonResource(self.COMMON_RESOURCE_PATH + pickleName)
        if not pickleFile:
            LogError('Could not load pickle file.', pickleName, 'appears to be missing. The localization module will not be able to access labels or texts.')
            return None
        pickledData = pickleFile.Read()
        if not pickledData:
            pickleFile.Close()
            del pickleFile
            LogError('Could not read pickle data from file. ', pickleName, 'may be corrupt. The localization module will not be able to access labels or texts.')
            return None
        unPickledObject = pickle.loads(pickledData)

        def md5ForFile(file, block_size = 1048576):
            md5 = hashlib.md5()
            while True:
                data = file.read(block_size)
                if not data:
                    break
                md5.update(data)

            return md5.digest()


        self.hashDataDictionary[pickleName] = md5ForFile(pickleFile)
        pickleFile.Close()
        del pickleFile
        del pickledData
        return unPickledObject



    def _GetRawByMessageID(self, messageID, languageID = None, **kwargs):
        languageID = languageID or localizationUtil.GetLanguageID()
        try:
            text = self.languageTexts[languageID][messageID]
        except KeyError as e:
            return u'[no messageID: %s,%s]' % (messageID, languageID)
        return text



    def _GetByMessageID(self, messageID, languageID, **kwargs):
        try:
            text = self.languageTexts[languageID][messageID]
        except KeyError as e:
            text = None
            if languageID != self._primaryLanguageID:
                try:
                    text = self.languageTexts[self._primaryLanguageID].get(messageID, None)
                except KeyError as e:
                    LogError("Missing primary language '", str(self._primaryLanguageID), "' and '", languageID, "' texts for messageID ", messageID, '.')
                    return 
            if text:
                LogInfo("Missing '", languageID, "' translation for messageID ", messageID, ".  Found '", str(self._primaryLanguageID), "' version and returning that instead.  Text: ", text)
                return localization._Parse(text, messageID, self._primaryLanguageID, **kwargs)
            else:
                LogTraceback('MessageID ', messageID, ' does not exist.')
                return 
        if not kwargs:
            noKwargCallCounter.Inc()
            return text
        else:
            kwargCallCounter.Inc()
            return localization._Parse(text, messageID, languageID, **kwargs)



    def _GetAllMetaDataPerLanguage(self, messageID, languageID):
        properties = self.languageMetaData.get(languageID, {}).get(messageID, None)
        if properties is not None:
            properties = properties.copy()
        return properties



    def _GetMetaData(self, messageID, propertyName, languageID):
        return self.languageMetaData.get(languageID, {}).get(messageID, {}).get(propertyName, None)



    def _SetHardcodedStringDetection(self):
        if boot.role != 'client':
            return 
        while not hasattr(__builtin__, 'prefs'):
            blue.synchro.Yield()

        localizationUtil.SetHardcodedStringDetection(getattr(prefs, 'showHardcodedStrings', False))



LOCALIZATION_REF = Localization()
exports = {'localization.GetByMessageID': LOCALIZATION_REF.GetByMessageID,
 'localization.GetByLabel': LOCALIZATION_REF.GetByLabel,
 'localization.GetPlaceholderLabel': LOCALIZATION_REF.GetPlaceholderLabel,
 'localization.GetByMapping': LOCALIZATION_REF.GetByMapping,
 'localization.GetMetaData': LOCALIZATION_REF.GetMetaData,
 'localization.GetAllMetaDataPerLanguage': LOCALIZATION_REF.GetAllMetaDataPerLanguage,
 'localization.GetAllMetaData': LOCALIZATION_REF.GetAllMetaData,
 'localization.IsValidTypeAndProperty': LOCALIZATION_REF.IsValidTypeAndProperty,
 'localization.IsValidLabel': LOCALIZATION_REF.IsValidLabel,
 'localization.IsValidMessageID': LOCALIZATION_REF.IsValidMessageID,
 'localization.IsValidMapping': LOCALIZATION_REF.IsValidMessageID,
 'localization.IsValidMetaDataByMessageID': LOCALIZATION_REF.IsValidMetaDataByMessageID,
 'localization.IsValidMetaDataByMapping': LOCALIZATION_REF.IsValidMetaDataByMapping,
 'localization.LogInfo': LogInfo,
 'localization.LogWarn': LogWarn,
 'localization.LogError': LogError,
 'localization.LogTraceback': LogTraceback,
 'localization.LoadPrimaryLanguage': LOCALIZATION_REF.LoadPrimaryLanguage,
 'localization.LoadSecondaryLanguage': LOCALIZATION_REF.LoadSecondaryLanguage,
 'localization.GetLanguages': LOCALIZATION_REF.GetLanguages,
 'localization.UpdateTextCache': LOCALIZATION_REF.UpdateTextCache,
 'localization.GetTextDataCache': LOCALIZATION_REF.GetTextDataCache,
 'localization.GetMaxRevision': LOCALIZATION_REF.GetMaxRevision,
 'localization.GetHashDataDictionary': LOCALIZATION_REF.GetHashDataDictionary,
 'localization._ReadLocalizationMainPickle': LOCALIZATION_REF._ReadLocalizationMainPickle,
 'localization._ReadLocalizationLanguagePickles': LOCALIZATION_REF._ReadLocalizationLanguagePickles,
 'localization.LOCALIZATION_REF': LOCALIZATION_REF,
 'localization._GetRawByMessageID': LOCALIZATION_REF._GetRawByMessageID}

