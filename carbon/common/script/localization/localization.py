import __builtin__
import cPickle as pickle
import blue
import miscUtil
import log
import locale
import localization
import localizationUtil
import util
import re
import uthread
import os
logChannel = log.GetChannel('Localization')

def LogInfo(*args):
    logChannel.Log('Localization module: ' + ''.join(map(strx, args)), logChannel.flags['INFO'])



def LogWarn(*args):
    logChannel.Log('Localization module: ' + ''.join(map(strx, args)), logChannel.flags['WARN'])



def LogError(*args):
    logChannel.Log('Localization module: ' + ''.join(map(strx, args)), logChannel.flags['ERR'])



class Localization(object):
    __guid__ = 'localization.Localization'
    PICKLE_PREFIX = 'localization_'
    PICKLE_MAIN = 'main'
    PICKLE_MAIN_NAME = PICKLE_PREFIX + PICKLE_MAIN
    PICKLE_EXT = '.pickle'
    COMMON_FILE_PATH = blue.os.rootpath + '../common/res/localization/'
    COMMON_RESOURCE_PATH = 'res:/localization/'
    FIELD_LABELS = 'labels'
    FIELD_LANGUAGES = 'languages'
    FIELD_MAPPING = 'mapping'
    FIELD_REGISTRATION = 'registration'
    FIELD_TYPES = 'types'
    LANGUAGE_FIELD_CODE = 0
    LANGUAGE_FIELD_TEXTS = 1
    LANGUAGE_FIELD_DATA = 2
    LANGUAGE_NUMBER_OF_FIELDS = 3
    IDENTIFIER_TYPE_NAMES = ['characters',
     'characterLists',
     'items',
     'locations',
     'dateTimes',
     'dateTimeQuantities',
     'numericQuantities',
     'undefined']
    IS_INVALID_TYPE = 0
    IS_INVALID_PROPERTY = 1
    IS_VALID_TYPE_AND_PROPERTY = 2
    PICKLE_PROTOCOL = 2

    def __init__(self):
        self._InitializeTextData()
        self._ReadLocalizationPickle()
        uthread.worker('localization::_SetHardcodedStringDetection', self._SetHardcodedStringDetection)
        print 'Cerberus localization module loaded on',
        print boot.role



    @classmethod
    def GetResourceFilePaths(cls, filePath = COMMON_FILE_PATH, fileNamePrepend = PICKLE_PREFIX, fileExtension = PICKLE_EXT, projectID = None):
        filenameList = []
        mainPicklePath = os.path.abspath(filePath + fileNamePrepend + cls.PICKLE_MAIN + fileExtension)
        filenameList.append(mainPicklePath)
        db2service = sm.GetService('DB2')
        for row in db2service.zlocalization.LanguageCodes_SelectEnabled():
            languagePicklePath = os.path.abspath(filePath + fileNamePrepend + row.languageCodeString + fileExtension)
            filenameList.append(languagePicklePath)

        return filenameList



    @classmethod
    def WriteLocalizationPickle(cls, getSubmittedOnly = False, projectID = None):
        return Localization.WriteLocalizationPickleToFile(cls.COMMON_FILE_PATH, cls.PICKLE_PREFIX, cls.PICKLE_EXT, getSubmittedOnly, projectID)



    @classmethod
    def WriteLocalizationPickleToFile(cls, filePath, fileNamePrepend, fileExtension, getSubmittedOnly = False, projectID = None):
        if not filePath or not fileNamePrepend or not fileExtension:
            raise localizationUtil.LocalizationSystemError('Filepath strings are incomplete. filePath, fileNamePrepend, fileExtension : %s, %s, %s.' % (filePath, fileNamePrepend, fileExtension))
        exportedFilenames = []
        db2service = sm.GetService('DB2')
        if not db2service:
            raise localizationUtil.LocalizationSystemError('didnt get the DB2 service. db2service = %s' % db2service)
        languageIDToCode = {}
        messagePerLanguage = {}
        metaDataPerLanguage = {}
        languageCodesResultSet = db2service.zlocalization.LanguageCodes_SelectEnabled()
        languageCodesDict = localizationUtil.MakeRowDicts(languageCodesResultSet, languageCodesResultSet.columns, localization.COLUMN_LANGUAGE_CODE_STRING)
        getTableDataForPicklingResultSet = db2service.zlocalization.GetTableDataForPickling(1 if getSubmittedOnly else 0, projectID)
        messageResultSet = getTableDataForPicklingResultSet[0]
        wordMetaResultSet = getTableDataForPicklingResultSet[1]
        registrationResultSet = getTableDataForPicklingResultSet[2]
        mappingResultSet = getTableDataForPicklingResultSet[3]
        labelsResultSet = getTableDataForPicklingResultSet[4]
        typesWithPropertiesSet = getTableDataForPicklingResultSet[5]
        messageTextsDict = localizationUtil.MakeRowDicts(rowList=messageResultSet, columnNames=[localization.COLUMN_MESSAGEID, localization.COLUMN_LANGUAGEID, localization.COLUMN_TEXT])
        wordMetaDataDict = localizationUtil.MakeRowDicts(rowList=wordMetaResultSet, columnNames=wordMetaResultSet.columns)
        registrationDict = localizationUtil.MakeRowDicts(rowList=registrationResultSet, columnNames=registrationResultSet.columns)
        mappingDict = localizationUtil.MakeRowDicts(rowList=mappingResultSet, columnNames=mappingResultSet.columns)
        labelsDict = localizationUtil.MakeRowDicts(rowList=labelsResultSet, columnNames=labelsResultSet.columns, tableUniqueKey=localization.COLUMN_MESSAGEID)
        typesWithPropertiesDict = localizationUtil.MakeRowDicts(rowList=typesWithPropertiesSet, columnNames=typesWithPropertiesSet.columns)
        for languageCodeRow in languageCodesResultSet:
            languageCodeString = getattr(languageCodeRow, localization.COLUMN_LANGUAGE_CODE_STRING)
            languageID = getattr(languageCodeRow, localization.COLUMN_LANGUAGEID)
            languageIDToCode[languageID] = languageCodeString
            messagePerLanguage[languageCodeString] = {}
            metaDataPerLanguage[languageCodeString] = {}

        registrationData = {}
        for aRowKey in registrationDict:
            aRow = registrationDict[aRowKey]
            registrationData[aRow[localization.COLUMN_SCHEMA_REG_NAME] + '.' + aRow[localization.COLUMN_TABLE_REG_NAME] + '.' + aRow[localization.COLUMN_COLUMN_REG_NAME]] = aRow[localization.COLUMN_TABLE_REG_ID]

        mappingData = {}
        for aRowKey in mappingDict:
            aRow = mappingDict[aRowKey]
            mappingData[(aRow[localization.COLUMN_TABLE_REG_ID], aRow[localization.COLUMN_KEY_ID])] = aRow[localization.COLUMN_MESSAGEID]

        typesWithPropertiesData = {}
        for aRowKey in typesWithPropertiesDict:
            aRow = typesWithPropertiesDict[aRowKey]
            languageToProperties = typesWithPropertiesData.get(aRow[localization.COLUMN_TYPE_NAME], None)
            if languageToProperties is None:
                languageToProperties = {}
                typesWithPropertiesData[aRow[localization.COLUMN_TYPE_NAME]] = languageToProperties
            propertyList = languageToProperties.get(aRow[localization.COLUMN_LANGUAGE_CODE_STRING], None)
            if propertyList is None and aRow[localization.COLUMN_PROPERTY_NAME] is not None:
                propertyList = []
                languageToProperties[aRow[localization.COLUMN_LANGUAGE_CODE_STRING]] = propertyList
            if propertyList is not None:
                propertyList.append(aRow[localization.COLUMN_PROPERTY_NAME])

        filename = filePath + fileNamePrepend + cls.PICKLE_MAIN + fileExtension
        with open(filename, 'wb') as pickleFile:
            dataToPickle = {}
            dataToPickle[Localization.FIELD_LABELS] = labelsDict
            dataToPickle[Localization.FIELD_LANGUAGES] = languageCodesDict
            dataToPickle[Localization.FIELD_REGISTRATION] = registrationData
            dataToPickle[Localization.FIELD_MAPPING] = mappingData
            dataToPickle[Localization.FIELD_TYPES] = typesWithPropertiesData
            pickle.dump(dataToPickle, pickleFile, Localization.PICKLE_PROTOCOL)
        exportedFilenames.append(os.path.abspath(filename))
        pickleFile = None
        for aMessageKeyEntry in messageTextsDict:
            messageLanguageID = messageTextsDict[aMessageKeyEntry][localization.COLUMN_LANGUAGEID]
            aMessageID = messageTextsDict[aMessageKeyEntry][localization.COLUMN_MESSAGEID]
            aLanguageCode = languageIDToCode[messageLanguageID]
            messagePerLanguage[aLanguageCode][aMessageID] = messageTextsDict[aMessageKeyEntry][localization.COLUMN_TEXT]

        for aMetaEntryKey in wordMetaDataDict:
            metaLanguageID = wordMetaDataDict[aMetaEntryKey][localization.COLUMN_LANGUAGEID]
            aPropertyName = wordMetaDataDict[aMetaEntryKey][localization.COLUMN_PROPERTY_NAME]
            languageMetaEntry = metaDataPerLanguage[languageIDToCode[metaLanguageID]]
            aMessageID = wordMetaDataDict[aMetaEntryKey][localization.COLUMN_MESSAGEID]
            if aMessageID not in languageMetaEntry or languageMetaEntry[aMessageID] is None:
                languageMetaEntry[aMessageID] = {}
            languageMetaEntry[aMessageID][aPropertyName] = wordMetaDataDict[aMetaEntryKey][localization.COLUMN_METADATA_VALUE]

        for aLanguageCode in messagePerLanguage:
            filename = filePath + fileNamePrepend + aLanguageCode + fileExtension
            with open(filename, 'wb') as pickleFile:
                dataToPickle = (aLanguageCode, messagePerLanguage[aLanguageCode], metaDataPerLanguage[aLanguageCode])
                pickle.dump(dataToPickle, pickleFile, Localization.PICKLE_PROTOCOL)
            pickleFile = None
            exportedFilenames.append(os.path.abspath(filename))

        return exportedFilenames



    def GetByMapping(self, resourceName, keyID, propertyName = None, languageID = None, **kwargs):
        try:
            tableRegID = self.tableRegistration[resourceName]
            messageID = self.messageMapping[(tableRegID, keyID)]
            if propertyName is None:
                return self.GetByMessageID(messageID, languageID, **kwargs)
            else:
                return self.GetMetaData(messageID, propertyName, languageID)
        except KeyError as e:
            LogError("mapping wasn't found for resourceName,keyID,propertyName,languageID : '%s',%s,%s,%s" % (resourceName,
             keyID,
             propertyName,
             languageID))
            return '[no data:%s,%s]' % (resourceName, keyID)



    def GetByMessageID(self, messageID, languageID = None, **kwargs):
        languageID = languageID or localizationUtil.GetLanguageID()
        textString = None
        if languageID == localization.LOCALE_PSEUDOLOC:
            textString = self._GetByMessageID(messageID, localization.LOCALE_SHORT_ENGLISH, **kwargs)
            if textString is not None:
                return localization.Pseudolocalize(localizationUtil.LocalizationSafeString(textString, messageID=messageID))
        else:
            textString = self._GetByMessageID(messageID, languageID, **kwargs)
            if textString is not None:
                return localizationUtil.LocalizationSafeString(textString, messageID=messageID)
        return '[no message:%s]' % messageID



    def GetByLabel(self, labelNameAndPath, languageID = None, **kwargs):
        try:
            messageID = self.languageLabels[labelNameAndPath][localization.COLUMN_MESSAGEID]
        except KeyError as e:
            LogError('A non-existent label was requested. Label: %s, %s' % (labelNameAndPath, languageID))
            return '[no label:%s]' % labelNameAndPath
        return self.GetByMessageID(messageID, languageID, **kwargs)



    def IsValidMessageID(self, messageID, languageID = None):
        languageID = languageID or localizationUtil.GetLanguageID()
        if languageID == localization.LOCALE_PSEUDOLOC:
            languageID = localization.LOCALE_SHORT_ENGLISH
        text = self.languageTexts.get(languageID, {}).get(messageID, None)
        if text is None:
            return False
        else:
            return True



    def IsValidLabel(self, labelNameAndPath, languageID = None):
        messageRow = self.languageLabels.get(labelNameAndPath, None)
        if messageRow is None:
            return False
        messageID = messageRow[localization.COLUMN_MESSAGEID]
        return self.IsValidMessageID(messageID, languageID)



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
        languageID = languageID or localizationUtil.GetLanguageID()
        if languageID == localization.LOCALE_PSEUDOLOC:
            languageID = localization.LOCALE_SHORT_ENGLISH
        metaData = self.languageMetaData.get(languageID, {}).get(messageID, {}).get(propertyName, None)
        if metaData is None:
            return False
        else:
            return True



    def IsValidTypeAndProperty(self, typeName, propertyName, languageID = None):
        returnValue = None
        languageID = languageID or localizationUtil.GetLanguageID()
        if languageID == localization.LOCALE_PSEUDOLOC:
            languageID = localization.LOCALE_SHORT_ENGLISH
        foundType = self.languageTypesWithProperties.get(typeName, None)
        if foundType is not None:
            foundPropertyList = foundType.get(languageID, None)
            if foundPropertyList is not None:
                if propertyName in foundPropertyList:
                    returnValue = self.IS_VALID_TYPE_AND_PROPERTY
                else:
                    returnValue = self.IS_INVALID_PROPERTY
            else:
                returnValue = self.IS_INVALID_PROPERTY
        else:
            returnValue = self.IS_INVALID_TYPE
        if returnValue is None:
            returnValue = self.IS_INVALID_TYPE
            LogError('IsValidTypeAndProperty wasnt able to determine if type and property were valid: %s,%s' % (typeName, propertyName))
        return returnValue



    def GetMetaData(self, messageID, propertyName, languageID = None):
        if languageID is None:
            languageID = localizationUtil.GetLanguageID()
        if languageID == localization.LOCALE_PSEUDOLOC:
            englishString = self._GetMetaData(messageID, propertyName, localization.LOCALE_SHORT_ENGLISH)
            if englishString is not None:
                return localization.Pseudolocalize(localizationUtil.LocalizationSafeString(englishString, messageID=messageID))
        else:
            propertyString = self._GetMetaData(messageID, propertyName, languageID)
            if propertyString is not None:
                return localizationUtil.LocalizationSafeString(propertyString, messageID)
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
        if languageID is None:
            languageID = localizationUtil.GetLanguageID()
        return self._GetAllMetaDataPerLanguage(messageID, languageID)



    def GetPlaceholderLabel(self, englishText, **kwargs):
        parsedText = localization._Parse(englishText, None, localization.LOCALE_SHORT_ENGLISH, **kwargs)
        LogWarn('Placeholder label (%s) needs to be replaced.' % englishText)
        if localizationUtil.GetLanguageID() == localization.LOCALE_PSEUDOLOC:
            parsedText = localization.Pseudolocalize(parsedText)
        return localizationUtil.LocalizationSafeString('!_%s_!' % parsedText, messageID=None)



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
                self.languageLabels[pathAndLabelKey] = dataRow

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
        return True



    def _UnloadLanguageLocalizationData(self, aLangCode):
        textData = self.languageTexts.get(aLangCode, None)
        if textData is not None:
            del self.languageTexts[aLangCode]
        metaData = self.languageMetaData.get(aLangCode, None)
        if metaData is not None:
            del self.languageMetaData[aLangCode]



    def _ReadLanguageLocalizationData(self, aLangCode, unPickledObject):
        if unPickledObject and len(unPickledObject) == self.LANGUAGE_NUMBER_OF_FIELDS:
            self._UnloadLanguageLocalizationData(aLangCode)
            self.languageTexts[aLangCode] = unPickledObject[self.LANGUAGE_FIELD_TEXTS]
            self.languageMetaData[aLangCode] = unPickledObject[self.LANGUAGE_FIELD_DATA]
        else:
            LogError("didn't find required parts in unpickled object. File name = %s" % (self.PICKLE_PREFIX + aLangCode + self.PICKLE_EXT))
            return False
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



    def _InitializeTextData(self):
        self.languagesDefined = {}
        self.languageLabels = {}
        self.languageTexts = {}
        self.languageMetaData = {}
        self.languageTypesWithProperties = {}
        self.tableRegistration = {}
        self.messageMapping = {}



    def _ReadLocalizationPickle(self):
        pickleFile = miscUtil.GetCommonResource(self.COMMON_RESOURCE_PATH + self.PICKLE_MAIN_NAME + self.PICKLE_EXT)
        if not pickleFile:
            LogError('pickleFile is None. Name = %s' % (self.PICKLE_MAIN_NAME + self.PICKLE_EXT))
            return False
        pickledData = pickleFile.Read()
        if not pickledData:
            LogError('pickledData is None. File name = %s' % (self.PICKLE_MAIN_NAME + self.PICKLE_EXT))
            return False
        unPickledObject = pickle.loads(pickledData)
        readStatus = self._ReadMainLocalizationData(unPickledObject)
        pickleFile.Close()
        del unPickledObject
        del pickledData
        del pickleFile
        if readStatus == False:
            return False
        for aLangCode in self.languagesDefined:
            pickleFile = miscUtil.GetCommonResource(self.COMMON_RESOURCE_PATH + self.PICKLE_PREFIX + aLangCode + self.PICKLE_EXT)
            if not pickleFile:
                LogError('pickle file is None. Name = %s' % (self.PICKLE_PREFIX + aLangCode + self.PICKLE_EXT))
                return False
            pickledData = pickleFile.Read()
            if not pickledData:
                LogError('pickled data is None. File name = %s' % (self.PICKLE_PREFIX + aLangCode + self.PICKLE_EXT))
                return False
            unPickledObject = pickle.loads(pickledData)
            readStatus = self._ReadLanguageLocalizationData(aLangCode, unPickledObject)
            pickleFile.Close()
            del unPickledObject
            del pickledData
            del pickleFile
            if readStatus == False:
                return False

        return True



    def _GetByMessageID(self, messageID, languageID, **kwargs):
        try:
            text = self.languageTexts[languageID][messageID]
        except KeyError as e:
            text = self.languageTexts[localization.LOCALE_SHORT_ENGLISH].get(messageID, None)
            LogError('a non existent messageID was requested. messageID, languageID: %s, %s.  English found: %s' % (messageID, languageID, text is not None))
            if text:
                return localization._Parse(text, messageID, localization.LOCALE_SHORT_ENGLISH, **kwargs)
            return 
        return localization._Parse(text, messageID, languageID, **kwargs)



    def _GetAllMetaDataPerLanguage(self, messageID, languageID):
        properties = self.languageMetaData.get(languageID, {}).get(messageID, None)
        if properties is not None:
            properties = properties.copy()
        return properties



    def _GetMetaData(self, messageID, propertyName, languageID):
        return self.languageMetaData.get(languageID, {}).get(messageID, {}).get(propertyName, None)



    def _SetHardcodedStringDetection(self):
        if boot.role == 'client':
            while not hasattr(__builtin__, 'prefs'):
                blue.synchro.Yield()

            localizationUtil.SetHardcodedStringDetection(getattr(prefs, 'showHardcodedStrings', False))



LOCALIZATION_REF = None
if boot.appname == 'WOD':
    LOCALIZATION_REF = Localization()
elif boot.appname == 'EVE' and hasattr(prefs, 'enableCerberusLocalizationModule') and prefs.enableCerberusLocalizationModule == 1:
    LOCALIZATION_REF = Localization()
if LOCALIZATION_REF is not None:
    exports = {'localization.WriteLocalizationPickle': Localization.WriteLocalizationPickle,
     'localization.WriteLocalizationPickleToFile': Localization.WriteLocalizationPickleToFile,
     'localization.GetByMessageID': LOCALIZATION_REF.GetByMessageID,
     'localization.GetByLabel': LOCALIZATION_REF.GetByLabel,
     'localization.GetPlaceholderLabel': LOCALIZATION_REF.GetPlaceholderLabel,
     'localization.GetByMapping': LOCALIZATION_REF.GetByMapping,
     'localization.GetMetaData': LOCALIZATION_REF.GetMetaData,
     'localization.GetAllMetaDataPerLanguage': LOCALIZATION_REF.GetAllMetaDataPerLanguage,
     'localization.GetAllMetaData': LOCALIZATION_REF.GetAllMetaData,
     'localization.IsValidTypeAndProperty': LOCALIZATION_REF.IsValidTypeAndProperty,
     'localization.IsValidLabel': LOCALIZATION_REF.IsValidLabel,
     'localization.IsValidMessageID': LOCALIZATION_REF.IsValidMessageID,
     'localization.IsValidMetaDataByMessageID': LOCALIZATION_REF.IsValidMetaDataByMessageID,
     'localization.IsValidMetaDataByMapping': LOCALIZATION_REF.IsValidMetaDataByMapping,
     'localization.GetResourceFilePaths': Localization.GetResourceFilePaths,
     'localization.LogInfo': LogInfo,
     'localization.LogWarn': LogWarn,
     'localization.LogError': LogError,
     'localization._ReadLocalizationPickle': LOCALIZATION_REF._ReadLocalizationPickle,
     'localization.LOCALIZATION_REF': LOCALIZATION_REF}

