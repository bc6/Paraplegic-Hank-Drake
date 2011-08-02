import localization
import localizationUtil
import util
import xml.etree.ElementTree
ADDED = 'Added text'
UPDATED = 'Updated text'
UNCHANGED = 'Unchanged text'
SKIPPED = 'Skipped messageID'
EMPTY_TAG = 'Empty tags'
IMPORT_BATCH_SIZE = 1000

def ExportToXMLFileFromDatabase(fileName, projectID = None):
    if not fileName:
        return 
    textsElement = _ExportXMLElementsFromDataRows(_GetExportDataFromDatabase(projectID))
    textsElementTree = xml.etree.ElementTree.ElementTree(textsElement)
    try:
        textsElementTree.write(fileName, encoding='utf-8')
    except TypeError as anError:
        newMessage = "Is there perhaps an attribute on XML Element with None value? ElementTree doesn't like that."
        raise TypeError(anError.args, newMessage)
    return True



def ExportXMLFromDatabase(projectID = None):
    return _ExportXMLFromDataRows(_GetExportDataFromDatabase(projectID))



def ImportFromXMLFileIntoDatabase(fileName):
    if not fileName:
        return 
    textDataTree = xml.etree.ElementTree.ElementTree()
    textDataTree.parse(fileName)
    return _ImportXMLIntoDatabase(textRootElement=textDataTree)



def ImportXMLIntoDatabase(translatedTextXML):
    if not translatedTextXML:
        localization.LogError('Import function received an empty xml string. Cannot do anything with it.')
        return None
    textRootElement = xml.etree.ElementTree.fromstringlist(translatedTextXML.encode('utf-8'))
    return _ImportXMLIntoDatabase(textRootElement=textRootElement)



def _GetExportDataFromDatabase(projectID = None):
    db2service = sm.GetService('DB2')
    return db2service.zlocalization.GetTextDataForXMLExport(1, projectID)



def _ExportXMLFromDataRows(dataRows):
    textsElement = _ExportXMLElementsFromDataRows(dataRows)
    try:
        textsXMLString = xml.etree.ElementTree.tostring(textsElement, encoding='utf-8').decode('utf-8')
    except TypeError as anError:
        newMessage = "Is there perhaps an attribute on XML Element with None value? ElementTree doesn't like that."
        raise TypeError(anError.args, newMessage)
    return textsXMLString



def _ExportXMLElementsFromDataRows(dataForXMLResultSet):
    textDataElement = xml.etree.ElementTree.Element(tag=localization.EXPORT_XML_TEXT_ROOT)
    messagesExported = 0
    metaDataExported = 0
    englishTextsResultSet = dataForXMLResultSet[0]
    allPropertiesResultSet = dataForXMLResultSet[1]
    allMetaDataResultSet = dataForXMLResultSet[2]
    requestedLanguagesResultSet = dataForXMLResultSet[3]
    translationsResultSet = dataForXMLResultSet[4]
    languageCodesDict = localizationUtil.MakeRowDicts(requestedLanguagesResultSet, requestedLanguagesResultSet.columns, localization.COLUMN_LANGUAGEID)
    messageAndPropertyToMetaDataIndex = {}
    messageToTranslatedIndex = {}
    typeAndLanguageToPropertiesIndex = {}
    for aTranslatedEntry in translationsResultSet:
        messageToTranslatedIndex[(aTranslatedEntry.messageID, languageCodesDict[aTranslatedEntry.languageID][localization.COLUMN_LANGUAGE_CODE_STRING])] = aTranslatedEntry

    for allMetaData in allMetaDataResultSet:
        languageCodeString = languageCodesDict[allMetaData.languageID][localization.COLUMN_LANGUAGE_CODE_STRING]
        messageAndPropertyToMetaDataIndex[(allMetaData.messageID, languageCodeString, allMetaData.propertyName)] = allMetaData

    for aProperty in allPropertiesResultSet:
        aPropertyList = typeAndLanguageToPropertiesIndex.get((aProperty.wordTypeID, aProperty.languageCodeString), None)
        if aPropertyList is None:
            aPropertyList = typeAndLanguageToPropertiesIndex[(aProperty.wordTypeID, aProperty.languageCodeString)] = []
        aPropertyList.append(aProperty)

    for aTextRow in englishTextsResultSet:
        attributes = {localization.EXPORT_XML_MESSAGEID: str(aTextRow.messageID),
         localization.EXPORT_XML_DATAID: str(aTextRow.dataID)}
        textRowLabel = '' if aTextRow.label is None else aTextRow.label
        attributes[localization.EXPORT_XML_PATH] = textRowLabel if aTextRow.FullPath is None else aTextRow.FullPath + localization.FOLDER_NAME_CHAR_SEPARATOR + textRowLabel
        messageElement = xml.etree.ElementTree.Element(localization.EXPORT_XML_MESSAGE, attrib=attributes)
        textDataElement.append(messageElement)
        messagesExported += 1
        englishTextElement = _MakeXMLLanguageTextElements(messageElement, aTextRow, localization.LOCALE_SHORT_ENGLISH, {})
        descriptionElement = xml.etree.ElementTree.Element(localization.EXPORT_XML_DESCRIPTION)
        descriptionElement.text = aTextRow.context
        messageElement.append(descriptionElement)
        englishMetaElement = _MakeXMLLanguageMetaDataElements(englishTextElement, aTextRow, localization.LOCALE_SHORT_ENGLISH, typeAndLanguageToPropertiesIndex, messageAndPropertyToMetaDataIndex)
        if englishMetaElement is not None:
            metaDataExported += 1
        translationsElement = xml.etree.ElementTree.Element(tag=localization.EXPORT_XML_TRANSLATIONS)
        messageElement.append(translationsElement)
        for aLanguageEntry in requestedLanguagesResultSet:
            if aLanguageEntry.languageCodeString != localization.LOCALE_SHORT_ENGLISH:
                languageTextElement = _MakeXMLLanguageTextElements(translationsElement, aTextRow, aLanguageEntry.languageCodeString, messageToTranslatedIndex)
                if aTextRow.wordTypeID is not None:
                    if aLanguageEntry.languageCodeString != localization.LOCALE_SHORT_ENGLISH:
                        languageMetaElement = _MakeXMLLanguageMetaDataElements(languageTextElement, aTextRow, aLanguageEntry.languageCodeString, typeAndLanguageToPropertiesIndex, messageAndPropertyToMetaDataIndex)
                        if languageMetaElement is not None:
                            metaDataExported += 1


    localization.LogInfo("Export method exported '%i' message(s) and '%i' metaData entries (including english metadata) " % (messagesExported, metaDataExported))
    return textDataElement



def _MakeXMLLanguageTextElements(parentElement, aTextRow, languageCodeString, messageToTranslatedIndex):
    languageTextElement = xml.etree.ElementTree.Element(languageCodeString)
    parentElement.append(languageTextElement)
    if languageCodeString == localization.LOCALE_SHORT_ENGLISH:
        attributes = {}
    else:
        attributes = {localization.EXPORT_XML_STATUS: localization.EXPORT_XML_TRANSLATE}
    languageTextEntryElement = xml.etree.ElementTree.Element(localization.EXPORT_XML_TEXT, attrib=attributes)
    languageTextElement.append(languageTextEntryElement)
    aTranslatedEntry = messageToTranslatedIndex.get((aTextRow.messageID, languageCodeString), None)
    if aTranslatedEntry:
        languageTextEntryElement.text = aTranslatedEntry.text
    else:
        languageTextEntryElement.text = aTextRow.text
    return languageTextElement



def _MakeXMLLanguageMetaDataElements(parentElement, aTextRow, languageCodeString, typeAndLanguageToPropertiesIndex, messageAndPropertyToMetaDataIndex):
    languageMetaElement = None
    aProperties = typeAndLanguageToPropertiesIndex.get((aTextRow.wordTypeID, languageCodeString))
    if aProperties:
        languageMetaElement = xml.etree.ElementTree.Element(localization.EXPORT_XML_METADATA)
        parentElement.append(languageMetaElement)
        for aProperty in aProperties:
            if languageCodeString == localization.LOCALE_SHORT_ENGLISH:
                attributes = {}
            else:
                attributes = {localization.EXPORT_XML_STATUS: localization.EXPORT_XML_TRANSLATE}
            languageProperty = xml.etree.ElementTree.Element(aProperty.propertyName, attrib=attributes)
            languageMetaElement.append(languageProperty)
            languageMetaDataRow = messageAndPropertyToMetaDataIndex.get((aTextRow.messageID, languageCodeString, aProperty.propertyName), None)
            if languageMetaDataRow is not None:
                languageProperty.text = languageMetaDataRow.metaDataValue

    return languageMetaElement



def _ImportXMLIntoDatabase(textRootElement):
    import bsdWrappers
    db2service = sm.GetService('DB2')
    if not db2service:
        localization.LogError('didnt get the DB2 service. db2service = %s' % db2service)
        return (None, None)
    updatedTextEntries = {ADDED: 0,
     UPDATED: 0,
     UNCHANGED: 0,
     SKIPPED: 0,
     EMPTY_TAG: 0}
    updatedMetaDataEntries = {ADDED: 0,
     UPDATED: 0,
     UNCHANGED: 0,
     EMPTY_TAG: 0}
    bsdTableService = sm.GetService('bsdTable')
    messageTextsTable = bsdTableService.GetTable(localization.MESSAGE_TEXTS_TABLE)
    metaDataTable = bsdTableService.GetTable(localization.WORD_METADATA_TABLE)
    messagesTable = bsdTableService.GetTable(localization.MESSAGES_TABLE)
    languageCodesResultSet = db2service.zlocalization.LanguageCodes_SelectEnabled()
    allPropertiesResultSet = db2service.zlocalization.WordTypes_GetAllProperties()
    import localizationXMLUtil
    updatesResults = _GetUpdatesListForImportIntoDatabase(textRootElement, languageCodesResultSet, allPropertiesResultSet, messagesTable, localizationXMLUtil.testEnglishImport)
    (listOfTextImports, listOfMetaDataImports, textEntriesStats, metaDataEntriesStats,) = updatesResults
    updatedTextEntries.update(textEntriesStats)
    updatedMetaDataEntries.update(metaDataEntriesStats)
    iterationNumber = 0
    for anEntry in listOfTextImports:
        if iterationNumber == 0:
            bsdWrappers.TransactionStart()
        elif iterationNumber % IMPORT_BATCH_SIZE == 0:
            bsdWrappers.TransactionEnd('Import text operation batch. %s items processed so far.' % iterationNumber)
            bsdWrappers.TransactionStart()
        updateStatus = _ImportTextEntry(anEntry[0], anEntry[1], anEntry[2], messageTextsTable, localizationXMLUtil.testCompareWithEnglish)
        updatedTextEntries[updateStatus] += 1
        iterationNumber += 1

    if iterationNumber > 0:
        bsdWrappers.TransactionEnd('Import text operation batch. %s items processed so far.' % iterationNumber)
    iterationNumber = 0
    for anEntry in listOfMetaDataImports:
        if iterationNumber == 0:
            bsdWrappers.TransactionStart()
        elif iterationNumber % IMPORT_BATCH_SIZE == 0:
            bsdWrappers.TransactionEnd('Import metadata operation batch. %s items processed so far.' % iterationNumber)
            bsdWrappers.TransactionStart()
        updateStatus = _ImportMetaDataEntry(anEntry[0], anEntry[1], anEntry[2], metaDataTable)
        updatedMetaDataEntries[updateStatus] += 1
        iterationNumber += 1

    if iterationNumber > 0:
        bsdWrappers.TransactionEnd('Import metadata operation batch. %s items processed so far.' % iterationNumber)
    return (updatedTextEntries, updatedMetaDataEntries)



def _GetUpdatesListForImportIntoDatabase(textRootElement, languageCodesResultSet, allPropertiesResultSet, messagesTable, testEnglishImport = False):
    listOfTextImports = []
    listOfMetaDataImports = []
    updatedTextEntries = {SKIPPED: 0,
     EMPTY_TAG: 0}
    updatedMetaDataEntries = {EMPTY_TAG: 0}
    propertyAndLanguageToPropertiesIndex = {}
    for aProperty in allPropertiesResultSet:
        propertyAndLanguageToPropertiesIndex[(aProperty.propertyName, aProperty.languageCodeString)] = aProperty

    if textRootElement is not None:
        allMessageElements = textRootElement.findall(localization.EXPORT_XML_MESSAGE)
        for aMessageElement in allMessageElements:
            dataID = int(aMessageElement.get(localization.EXPORT_XML_DATAID))
            messageID = int(aMessageElement.get(localization.EXPORT_XML_MESSAGEID))
            messageRows = messagesTable.GetRowByKey(messageID)
            if not messageRows:
                localization.LogError("Import didnt find a matching messageID in DB; skipping importing this entry : '%s'" % messageID)
                updatedTextEntries[SKIPPED] += 1
                continue
            translationElement = aMessageElement.find(localization.EXPORT_XML_TRANSLATIONS)
            languageElements = list(translationElement)
            if testEnglishImport:
                languageElements.append(aMessageElement.find(localization.LOCALE_SHORT_ENGLISH))
            for aLanguageElement in languageElements:
                languageTextElement = aLanguageElement.find(localization.EXPORT_XML_TEXT)
                languageCodeString = aLanguageElement.tag
                languageID = languageCodeString
                translatedText = languageTextElement.text
                if translatedText:
                    listOfTextImports.append((messageID, translatedText, languageID))
                else:
                    updatedTextEntries[EMPTY_TAG] += 1
                metaDataElement = aLanguageElement.find(localization.EXPORT_XML_METADATA)
                if metaDataElement is not None:
                    languageMetaDataElements = list(metaDataElement)
                    for aPropertyElement in languageMetaDataElements:
                        propertyName = aPropertyElement.tag
                        metaDataText = aPropertyElement.text
                        if metaDataText:
                            try:
                                aPropertyEntry = propertyAndLanguageToPropertiesIndex[(propertyName, languageCodeString)]
                                wordPropertyID = aPropertyEntry.wordPropertyID
                                listOfMetaDataImports.append((messageID, wordPropertyID, metaDataText))
                            except IndexError as e:
                                localization.LogError("Import didnt find a matching property in DB; skipping importing this property (messageID,property) : '%s,%s'" % (messageID, propertyName))
                        else:
                            updatedMetaDataEntries[EMPTY_TAG] += 1



    return (listOfTextImports,
     listOfMetaDataImports,
     updatedTextEntries,
     updatedMetaDataEntries)



def _ImportMetaDataEntry(messageID, wordPropertyID, metaDataText, metaDataTable):
    updateStatus = UNCHANGED
    metaDataEntries = metaDataTable.GetRows(messageID=messageID, wordPropertyID=wordPropertyID)
    if metaDataEntries and len(metaDataEntries):
        if metaDataEntries[0].metaDataValue != metaDataText:
            metaDataEntries[0].metaDataValue = metaDataText
            updateStatus = UPDATED
        else:
            updateStatus = UNCHANGED
    else:
        metaDataTable.AddRow(metaDataValue=metaDataText, messageID=messageID, wordPropertyID=wordPropertyID)
        updateStatus = ADDED
    return updateStatus



def _ImportTextEntry(messageID, translatedText, languageID, messageTextsTable, testCompareWithEnglish = False):
    updateStatus = UNCHANGED
    englishText = localization.MessageText.GetMessageTextByMessageID(messageID, localization.LOCALE_SHORT_ENGLISH)
    if englishText is None:
        localization.LogError("Import didnt find a matching english text in DB; skipping importing this entry. messageID : '%s'" % messageID)
        return updateStatus
    existingTranslation = localization.MessageText.GetMessageTextByMessageID(messageID, languageID)
    isPassingEnglishTest = True
    if testCompareWithEnglish:
        isPassingEnglishTest = englishText.text != translatedText
    if existingTranslation:
        if existingTranslation.text != translatedText and isPassingEnglishTest:
            existingTranslation.text = translatedText
            updateStatus = UPDATED
        else:
            updateStatus = UNCHANGED
    elif isPassingEnglishTest:
        localization.MessageText.Create(messageID, languageID, text=translatedText)
        updateStatus = ADDED
    else:
        updateStatus = EMPTY_TAG
    return updateStatus


exports = util.AutoExports('localizationXMLUtil', locals())
exports['localizationXMLUtil.testEnglishImport'] = False
exports['localizationXMLUtil.testCompareWithEnglish'] = False

