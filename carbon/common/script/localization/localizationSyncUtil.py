import localization
import util
MAX_GROUP_DEPTH = 500

def SyncDataFromRegisteredTables(listOfRegistered = None, syncBatchSize = 1000):
    import bsdWrappers
    bsdTableService = sm.GetService('bsdTable')
    regTable = bsdTableService.GetTable(localization.EXTERNAL_REGISTRATION_TABLE)
    groupTable = bsdTableService.GetTable(localization.MESSAGE_GROUPS_TABLE)
    messagesTable = bsdTableService.GetTable(localization.MESSAGES_TABLE)
    allRegistered = []
    if not listOfRegistered:
        allRegistered = regTable.GetRows(_getDeleted=False)
    else:
        for aResourceID in listOfRegistered:
            resourceRow = regTable.GetRowByKey(keyId1=aResourceID, _getDeleted=False)
            if resourceRow:
                allRegistered.append(resourceRow)

    updatedEntriesPerTable = {}
    for aRow in allRegistered:
        tableRegID = aRow.tableRegID
        textColumnName = aRow.columnRegName
        uniqueIDName = aRow.uniqueIDName
        groupPathName = aRow.groupPathName
        groupID = aRow.groupID
        groupRow = groupTable.GetRowByKey(keyId1=groupID)
        wordTypeID = groupRow.wordTypeID
        groupRow.isReadOnly = 1
        registeredTypeID = aRow.registeredTypeID
        tableSchema = aRow.schemaRegName
        tableName = aRow.tableRegName
        syncResult = {}
        syncResult[localization.KeyToMessageMapping.UNCHANGED_ENTRY] = 0
        syncResult[localization.KeyToMessageMapping.ADDED_ENTRY] = 0
        syncResult[localization.KeyToMessageMapping.UPDATED_ENTRY] = 0
        syncResult[localization.KeyToMessageMapping.DELETED_ENTRY] = 0
        updatedEntriesPerTable['.'.join((aRow.schemaRegName, aRow.tableRegName, aRow.columnRegName))] = syncResult
        allTableData = None
        if registeredTypeID == localization.REGISTERED_TYPE_DYNAMIC:
            db2service = sm.GetService('DB2')
            try:
                allTableData = db2service.zlocalization.RegisteredResources_SelectOnRegisteredResource(tableRegID)
            except SQLError:
                localization.LogError("failed when attempting to read a table/view resource : tableRegID = '%s'" % tableRegID)
        elif registeredTypeID == localization.REGISTERED_TYPE_BSD:
            try:
                registeredTable = bsdTableService.GetTable(tableSchema + '.' + tableName)
                allTableData = registeredTable.GetRows(_getDeleted=False)
            except RuntimeError:
                localization.LogError("failed when attempting to read a BSD table : '%s'" % (tableSchema + '.' + tableName))
        else:
            localization.LogError("encountered unknown registered resource type : '%s' of type '%s'" % (tableSchema + '.' + tableName, registeredTypeID))
        if allTableData is not None:
            cachedGroupPaths = {}
            possibleOrphanedGroups = set()
            for aTableRow in allTableData:
                keyIDValue = getattr(aTableRow, uniqueIDName, None)
                if registeredTypeID == localization.REGISTERED_TYPE_DYNAMIC and groupPathName is not None:
                    groupPathString = getattr(aTableRow, groupPathName, None)
                    if groupPathString is not None and groupPathString != '':
                        if groupPathString not in cachedGroupPaths:
                            (groupID, isNewGroup,) = _ResolveDynamicPath(groupPathString, aRow.groupID, wordTypeID)
                            cachedGroupPaths[groupPathString] = groupID
                            if isNewGroup == True:
                                mappingEntry = localization.KeyToMessageMapping.GetMapping(keyIDValue, tableRegID)
                                if mappingEntry is not None:
                                    messageEntry = localization.Message.GetMessageByID(mappingEntry.messageID)
                                    if messageEntry is not None:
                                        possibleOrphanedGroups.add(messageEntry.groupID)

            updatedMappedEntries = []
            iterationNumber = 0
            for aTableRow in allTableData:
                englishText = getattr(aTableRow, textColumnName, None)
                keyIDValue = getattr(aTableRow, uniqueIDName, None)
                if iterationNumber == 0:
                    bsdWrappers.TransactionStart()
                    transactionBundle = localization.Message.CreateMessageDataBundle()
                elif iterationNumber % syncBatchSize == 0:
                    bsdWrappers.TransactionEnd()
                    bsdWrappers.TransactionStart()
                    transactionBundle = localization.Message.CreateMessageDataBundle()
                if registeredTypeID == localization.REGISTERED_TYPE_DYNAMIC and groupPathName is not None:
                    groupPathString = getattr(aTableRow, groupPathName, None)
                    if groupPathString is not None and groupPathString != '':
                        groupID = cachedGroupPaths[groupPathString]
                    else:
                        groupID = aRow.groupID
                updatedMappedEntries.append(keyIDValue)
                mappingResult = localization.KeyToMessageMapping.AddOrUpdateEntry(keyID=keyIDValue, tableRegID=tableRegID, groupID=groupID, label=None, englishText=englishText, descriptionText=None, transactionBundle=transactionBundle)
                syncResult[mappingResult] += 1
                iterationNumber += 1

            if iterationNumber > 0:
                bsdWrappers.TransactionEnd()
            mappingsForResource = localization.KeyToMessageMapping.GetMappingsForRegisteredResource(tableRegID)
            if len(updatedMappedEntries) < len(mappingsForResource):
                for aMappingEntry in mappingsForResource:
                    keyIDValue = aMappingEntry.keyID
                    if keyIDValue not in updatedMappedEntries:
                        messageEntry = localization.Message.GetMessageByID(aMappingEntry.messageID)
                        if messageEntry is not None and messageEntry.groupID != aRow.groupID:
                            groupEntry = groupTable.GetRowByKey(keyId1=messageEntry.groupID)
                            if groupEntry.isReadOnly:
                                possibleOrphanedGroups.add(groupEntry.groupID)
                        aMappingEntry.Delete()
                        syncResult[localization.KeyToMessageMapping.DELETED_ENTRY] += 1

            bsdWrappers.TransactionStart()
            i = 0
            while i < MAX_GROUP_DEPTH:
                possibleOrphanedGroups = _DeleteOrphanedGroupsFrom(possibleOrphanedGroups, cachedGroupPaths.values(), messagesTable, groupTable)
                if len(possibleOrphanedGroups) == 0:
                    break
                elif len(possibleOrphanedGroups) == 1:
                    if aRow.groupID in possibleOrphanedGroups:
                        break
                i = i + 1

            bsdWrappers.TransactionEnd()

    return updatedEntriesPerTable



def _ResolveDynamicPath(groupPathString, staticGroupID, wordTypeID):
    folderNames = groupPathString.split(localization.FOLDER_NAME_CHAR_SEPARATOR)
    currentParentID = staticGroupID
    newGroup = None
    messageGroups = sm.GetService('bsdTable').GetTable('zlocalization.messageGroups')
    for currentGroupName in folderNames:
        if newGroup is None:
            groupRows = messageGroups.GetRows(parentID=currentParentID, groupName=currentGroupName, _getDeleted=False)
            groupRow = groupRows[0] if len(groupRows) > 0 else None
        if groupRow is not None:
            currentParentID = groupRow.groupID
        else:
            newGroup = localization.MessageGroup.Create(parentID=currentParentID, groupName=currentGroupName, isReadOnly=1, wordTypeID=wordTypeID)
            currentParentID = newGroup.groupID

    if newGroup is None:
        return (groupRow.groupID, False)
    else:
        return (newGroup.groupID, True)



def _DeleteOrphanedGroupsFrom(setOfDynamicGroups, cachedGroups, messagesTable, groupTable):
    setOfParentGroups = set()
    for aGroupID in setOfDynamicGroups:
        if aGroupID in cachedGroups:
            continue
        messagesInGroup = messagesTable.GetRows(groupID=aGroupID, _getDeleted=False)
        subGroups = groupTable.GetRows(parentID=aGroupID, _getDeleted=False)
        if len(messagesInGroup) == 0 and len(subGroups) == 0:
            groupRow = localization.MessageGroup.Get(aGroupID)
            setOfParentGroups.add(groupRow.parentID)
            groupRow.Delete()

    return setOfParentGroups


exports = util.AutoExports('localizationSyncUtil', locals())

