#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/localization/localizationSyncUtil.py
import localization
import util
from collections import defaultdict
MAX_GROUP_DEPTH = 500

def SyncDataFromRegisteredTables(listOfRegistered = None, syncBatchSize = 1000):
    import bsd
    bsdTableService = sm.GetService('bsdTable')
    bsdService = sm.GetService('BSD')
    dbzlocalization = sm.GetService('DB2').GetSchema('zlocalization')
    groupTable = bsdTableService.GetTable(localization.MESSAGE_GROUPS_TABLE)
    messagesTable = bsdTableService.GetTable(localization.MESSAGES_TABLE)
    messageTextsTable = bsdTableService.GetTable(localization.MESSAGE_TEXTS_TABLE)
    keyToMessageMappingsTable = bsdTableService.GetTable(localization.MESSAGE_MAPPING_TABLE)
    localization.LogInfo('Loading BSD table information...')
    messagesTable.WaitForColumnsAllLoaded()
    messageTextsTable.WaitForColumnsAllLoaded()
    keyToMessageMappingsTable.WaitForColumnsAllLoaded()
    localization.LogInfo('BSD table information loaded.')
    if not bsd.login.IsLoggedIn():
        localization.LogError('localizationSyncUtil: Cannot sync because we are not logged into BSD.')
        return
    allRegistered = []
    if not listOfRegistered:
        getSubmittedOnly = 1
        allRegistered = dbzlocalization.RegisteredResources_Select(getSubmittedOnly)
    else:
        regTable = bsdTableService.GetTable(localization.EXTERNAL_REGISTRATION_TABLE)
        for aResourceID in listOfRegistered:
            resourceRow = regTable.GetRowByKey(keyId1=aResourceID, _getDeleted=False)
            if resourceRow:
                allRegistered.append(resourceRow)

    updatedEntriesPerTable = {}
    localization.LogInfo('Beginning sync operation. Processing %s registered tables...' % len(allRegistered))
    bsdUserID = bsd.login.GetCurrentUserId()
    contentServerName = localization.CONTENT_DATABASE_MAP.get(_GetCurrentDatabase(), 'localhost')
    currentReleaseID = None
    currentReleaseName = 'None'
    currentLinkType = None
    currentLinkID = None
    currentChangeID = 0
    changelistDescription = None
    changeIDsInDescription = []
    deletionChangeTextAdded = False
    descriptionOfOriginalChangelists = []
    for registeredRowIndex, aRow in enumerate(allRegistered):
        localization.LogInfo('Processing table %s of %s...' % (registeredRowIndex + 1, len(allRegistered)))
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
        fullLocationName = tableSchema + '.' + tableName + '.' + textColumnName
        syncResult = defaultdict(int)
        updatedEntriesPerTable['.'.join((aRow.schemaRegName, aRow.tableRegName, aRow.columnRegName))] = syncResult
        allTableData = None
        if registeredTypeID == localization.REGISTERED_TYPE_DYNAMIC:
            try:
                allTableData = dbzlocalization.RegisteredResources_SelectOnRegisteredResource(tableRegID)
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
            sourceChangelists = {None: util.KeyVal(userID=None, userName='unknown (no userID)', releaseID=None, releaseName='None', linkType=None, linkID=None)}
            cachedGroupPaths = {}
            possibleOrphanedGroups = set()
            updatedMappedEntries = []
            localization.LogInfo('Fetching group and changelist information...')
            query = 'SELECT DISTINCT REV.changeID, C.userID, U.userName, C.releaseID, R.releaseName, C.linkType, C.linkID FROM zstatic.changes C\n  INNER JOIN zstatic.revisions REV on REV.changeID = C.changeID\n  INNER JOIN %s T on T.revisionID = REV.revisionID\n  INNER JOIN zstatic.users U ON C.userID = U.userID\n  LEFT JOIN zstatic.releases R on C.releaseID = R.releaseID\n  WHERE REV.submitDate is not NULL' % (tableSchema + '.' + tableName)
            try:
                rs = sm.GetService('DB2').SQL(query)
                for row in rs:
                    sourceChangelists[row.changeID] = row

            except SQLError as e:
                pass

            for aTableRow in allTableData:
                keyIDValue = getattr(aTableRow, uniqueIDName, None)
                if registeredTypeID == localization.REGISTERED_TYPE_DYNAMIC and groupPathName is not None:
                    groupPathString = getattr(aTableRow, groupPathName, None)
                    if groupPathString and groupPathString not in cachedGroupPaths:
                        groupID, isNewGroup = _ResolveDynamicPath(groupPathString, aRow.groupID, wordTypeID)
                        cachedGroupPaths[groupPathString] = groupID
                        if isNewGroup == True:
                            mappingEntry = localization.KeyToMessageMapping.GetMapping(keyIDValue, tableRegID)
                            if mappingEntry is not None:
                                messageEntry = localization.Message.GetMessageByID(mappingEntry.messageID)
                                if messageEntry is not None:
                                    possibleOrphanedGroups.add(messageEntry.groupID)

            localization.LogInfo("Processing %s rows from target '%s'..." % (len(allTableData), fullLocationName))
            rowIndex = 0
            while rowIndex < len(allTableData):
                with bsd.BsdTransaction():
                    transactionBundle = localization.Message.CreateMessageDataBundle()
                    for aTableRow in allTableData[rowIndex:rowIndex + syncBatchSize]:
                        if registeredTypeID == localization.REGISTERED_TYPE_DYNAMIC and groupPathName is not None:
                            groupPathString = getattr(aTableRow, groupPathName, None)
                            if groupPathString is not None and groupPathString != '':
                                groupID = cachedGroupPaths[groupPathString]
                            else:
                                groupID = aRow.groupID
                        englishText = getattr(aTableRow, textColumnName, None)
                        keyIDValue = getattr(aTableRow, uniqueIDName, None)
                        descriptionText = '%s.%s.%s: %s' % (tableSchema,
                         tableName,
                         textColumnName,
                         str(keyIDValue))
                        try:
                            unicode(englishText)
                        except UnicodeDecodeError as e:
                            localization.LogError('Invalid text data in row, skipping entry:', aTableRow)
                            syncResult[localization.KeyToMessageMapping.UNCHANGED_ENTRY] += 1
                            rowIndex += 1
                            continue

                        updateAction = localization.KeyToMessageMapping.AddOrUpdateEntry(keyID=keyIDValue, tableRegID=tableRegID, groupID=groupID, label=None, englishText=englishText, descriptionText=descriptionText, transactionBundle=transactionBundle, returnOnly=True)
                        if updateAction not in (localization.KeyToMessageMapping.UNCHANGED_ENTRY, localization.KeyToMessageMapping.SKIPPED_ENTRY):
                            sourceReleaseID = sourceChangelists[aTableRow.changeID].releaseID
                            sourceLinkType = sourceChangelists[aTableRow.changeID].linkType
                            sourceLinkID = sourceChangelists[aTableRow.changeID].linkID
                            if not currentChangeID or sourceReleaseID != currentReleaseID or sourceLinkType != currentLinkType or sourceLinkID != currentLinkID:
                                localization.LogInfo("Row %s (of %s) was submitted under release '%s' with linkType '%s' and linkID '%s', but the current changelist is for release '%s' with linkType '%s' and linkID '%s'.  Creating a new changelist and starting a new batch from this point..." % (rowIndex + 1,
                                 len(allTableData),
                                 sourceChangelists[aTableRow.changeID].releaseName,
                                 sourceLinkType,
                                 sourceLinkID,
                                 currentReleaseName,
                                 currentLinkType,
                                 currentLinkID))
                                changelistDescription = "Migrating external localizable content from '%s' to localization system tables.  The original content was created or modified in release '%s' in the following BSD changelists:\n" % (fullLocationName, sourceChangelists[aTableRow.changeID].releaseName)
                                changeIDsInDescription = []
                                currentReleaseID = sourceReleaseID
                                currentReleaseName = sourceChangelists[aTableRow.changeID].releaseName
                                currentLinkType = sourceLinkType
                                currentLinkID = sourceLinkID
                                currentChangeID = bsdService.ChangeAdd(bsdUserID, changeText=changelistDescription, linkType=currentLinkType, linkID=currentLinkID, releaseID=currentReleaseID)
                                deletionChangeTextAdded = False
                            localization.KeyToMessageMapping.AddOrUpdateEntry(keyID=keyIDValue, tableRegID=tableRegID, groupID=groupID, label=None, englishText=englishText, descriptionText=descriptionText, transactionBundle=transactionBundle)
                            if aTableRow.changeID not in changeIDsInDescription:
                                if aTableRow.changeID:
                                    descriptionOfOriginalChange = 'Change %s by %s (http://%s:50001/gd/bsd.py?action=Change&changeID=%s)\n' % (aTableRow.changeID,
                                     sourceChangelists[aTableRow.changeID].userName,
                                     contentServerName,
                                     aTableRow.changeID)
                                    changelistDescription += descriptionOfOriginalChange
                                    descriptionOfOriginalChangelists.append(descriptionOfOriginalChange)
                                else:
                                    descriptionOfOriginalChange = 'Change by unknown user (' + fullLocationName + ' is not registered in BSD)\n'
                                    changelistDescription += descriptionOfOriginalChange
                                    descriptionOfOriginalChangelists.append(descriptionOfOriginalChange)
                                changeIDsInDescription.append(aTableRow.changeID)
                                bsdService.ChangeEdit(bsdUserID, currentChangeID, changelistDescription, linkType=currentLinkType, linkID=currentLinkID, releaseID=currentReleaseID)
                        syncResult[updateAction] += 1
                        if updateAction != localization.KeyToMessageMapping.SKIPPED_ENTRY:
                            updatedMappedEntries.append(keyIDValue)
                        rowIndex += 1

            localization.LogInfo('Finished processing %s rows. Results: %s' % (len(allTableData), dict(syncResult)))
            mappingsForResource = localization.KeyToMessageMapping.GetMappingsForRegisteredResource(tableRegID)
            if len(updatedMappedEntries) < len(mappingsForResource):
                localization.LogInfo('Searching %s records for obsolete mappings and orphaned groups...' % len(mappingsForResource))
                for aMappingEntry in mappingsForResource:
                    keyIDValue = aMappingEntry.keyID
                    if keyIDValue not in updatedMappedEntries:
                        messageEntry = localization.Message.GetMessageByID(aMappingEntry.messageID)
                        if messageEntry is not None and messageEntry.groupID != aRow.groupID:
                            groupEntry = groupTable.GetRowByKey(keyId1=messageEntry.groupID)
                            if groupEntry.isReadOnly:
                                possibleOrphanedGroups.add(groupEntry.groupID)
                        if not currentChangeID:
                            changelistDescription = 'Automatic deletion of obsolete localization mapping entries and orphaned groups.\n'
                            currentChangeID = bsdService.ChangeAdd(bsdUserID, changeText=changelistDescription, linkType=None, linkID=None, releaseID=None)
                            currentReleaseID = None
                            deletionChangeTextAdded = True
                        elif currentChangeID and not deletionChangeTextAdded:
                            changelistDescription += 'Additionally, automatically deleting obsolete localization mapping entries and orphaned groups.\n'
                            bsdService.ChangeEdit(bsdUserID, currentChangeID, changelistDescription, linkType=currentLinkType, linkID=currentLinkID, releaseID=currentReleaseID)
                            currentReleaseID = None
                            deletionChangeTextAdded = True
                        aMappingEntry.Delete()
                        syncResult[localization.KeyToMessageMapping.DELETED_ENTRY] += 1

            localization.LogInfo('Finished searching for obsolete mappings and orphaned groups.  %s mapping entries were deleted.  %s potentially orphaned groups were detected.' % (syncResult[localization.KeyToMessageMapping.DELETED_ENTRY], len(possibleOrphanedGroups)))
            with bsd.BsdTransaction():
                i = 0
                while i < MAX_GROUP_DEPTH:
                    possibleOrphanedGroups = _DeleteOrphanedGroupsFrom(possibleOrphanedGroups, cachedGroupPaths.values(), messagesTable, groupTable)
                    if len(possibleOrphanedGroups) == 0:
                        break
                    elif len(possibleOrphanedGroups) == 1:
                        if aRow.groupID in possibleOrphanedGroups:
                            break
                    i = i + 1

    return (updatedEntriesPerTable, descriptionOfOriginalChangelists)


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
            localization.LogInfo("Deleting orphaned group '%s'..." % groupRow.groupName)
            groupRow.Delete()

    return setOfParentGroups


def _GetCurrentDatabase():
    connectionString = sm.GetService('DB2').CreateConnectionString()
    for kv in connectionString.split(';'):
        if '=' in kv:
            key, value = kv.split('=')
            key = key.strip().lower()
            if key == 'database':
                return value


exports = util.AutoExports('localizationSyncUtil', locals())