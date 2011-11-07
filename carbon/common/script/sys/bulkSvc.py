import service
import blue
import os
import hashlib
import macho
import dbutil
import sys
BULK_SYSTEM_PATH = blue.os.rootpath + 'bulkdata/'
BULK_CACHE_PATH = blue.os.cachepath + 'bulkdata/' + str(macho.version) + '/'
BULK_FILE_EXT = '.cache2'
VERSION_FILENAME = 'version'

class BulkSvc(service.Service):
    __guid__ = 'svc.bulkSvc'

    def Run(self, ms = None):
        self.state = service.SERVICE_START_PENDING
        try:
            if not os.path.exists(BULK_CACHE_PATH):
                os.makedirs(BULK_CACHE_PATH)
        except:
            self.LogError('Error creating bulk cache folder', BULK_CACHE_PATH)
            raise UserError('BulkDirCreationError')
        self.bulkMgr = sm.RemoteSvc('bulkMgr')
        self.branch = None
        self.lastLoginProgressID = 0
        self.UpdateBulk()
        self.state = service.SERVICE_RUNNING



    def UpdateLoginProgress(self, name, totalSteps = None):
        self.lastLoginProgressID += 1
        cfg.ReportLoginProgress(name, self.lastLoginProgressID, totalSteps)



    def UpdateBulk(self, doHashCheck = True):
        self.LogInfo('Lets see if there is some new bulk data for us')
        (changeID, self.branch,) = self.GetVersion()
        if changeID is None:
            self.UpdateFullBulkFiles()
            (serverChangeID, self.branch,) = self.bulkMgr.GetVersion()
            self.SetVersion(serverChangeID)
            self.LogInfo('bulk updated done, we are now at', serverChangeID)
            return 
        if doHashCheck:
            hashValue = self.GetHash()
        else:
            hashValue = None
        updateData = self.bulkMgr.UpdateBulk(changeID, hashValue, self.branch)
        if updateData is None:
            self.LogInfo('Bulk data is up to date:', changeID)
            return 
        updateType = updateData[0]
        updateInfo = updateData[1]
        if updateType == 1:
            serverBulkIDs = updateInfo
            clientBulkIDs = self.GetCurrentBulkIDs()
            idsToRemove = [ cID for cID in clientBulkIDs if cID in serverBulkIDs ]
            for bulkID in idsToRemove:
                serverBulkIDs.remove(bulkID)
                clientBulkIDs.remove(bulkID)

            self.LogInfo('We agreed on ', len(idsToRemove), 'bulk files. Need to add', len(serverBulkIDs), 'files and remove', len(clientBulkIDs), 'files')
            self.UpdateFullBulkFiles(serverBulkIDs, clientBulkIDs)
            self.UpdateBulk(False)
            return 
        if updateType in (0, 2, 4):
            if updateType == 0:
                self.LogWarn('Client is at different branch than the server so I need to fetch everything.')
            elif updateType == 2:
                self.LogWarn('Client is at changeID', changeID, 'but the server is at lower changeID', updateInfo, 'so I need to fetch everything.')
            else:
                self.LogWarn('The server has too many revisions for us. So we should fetch everything. We are at changeID', changeID, 'server is at', updateInfo)
            self.UpdateFullBulkFiles()
            self.SetVersion(updateInfo)
            self.LogInfo('bulk updated done, we are now at', updateInfo)
            return 
        self.UpdateLoginProgress('loginprogress::gettingbulkdata', updateInfo['chunkCount'])
        self.UpdateChangedRows(updateInfo['chunk'], updateInfo['changedTablesKeys'])
        self.UpdateDeletedRows(updateInfo['toBeDeleted'], updateInfo['changedTablesKeys'])
        for chunkNumber in xrange(1, updateInfo['chunkCount']):
            self.LogInfo('We have more chunks. Now fetching chunk', chunkNumber)
            toBeChanged = self.bulkMgr.GetChunk(changeID, chunkNumber)
            self.UpdateLoginProgress('loginprogress::gettingbulkdata', updateInfo['chunkCount'])
            self.UpdateChangedRows(toBeChanged, updateInfo['changedTablesKeys'])

        self.branch = updateInfo['branch']
        self.SetVersion(updateInfo['changeID'])
        self.LogInfo('bulk updated done, we are now at', updateInfo['changeID'])



    def UpdateChangedRows(self, toBeChanged, allKeyNames):
        for bulkID in toBeChanged:
            changes = toBeChanged[bulkID]
            if self.BulkExists(bulkID):
                self.LogInfo('Going to merge new bulk data into', bulkID)
                keyNames = allKeyNames[bulkID]
                clientData = self.LoadBulkFromFile(bulkID)
                changedDataKeys = []
                changedIndex = {}
                for (i, row,) in enumerate(changes):
                    keyValue = self.GetKeyValues(keyNames, row)
                    changedDataKeys.append(keyValue)
                    changedIndex[keyValue] = i

                for (i, row,) in enumerate(clientData):
                    rowKey = self.GetKeyValues(keyNames, row)
                    if rowKey in changedDataKeys:
                        clientData[i] = changes[changedIndex[rowKey]]
                        changedDataKeys.remove(rowKey)
                        self.LogInfo('bulk %s : updated key %s' % (bulkID, rowKey))

                for row in changedDataKeys:
                    clientData.append(changes[changedIndex[row]])
                    self.LogInfo('bulk %s : inserted key %s' % (bulkID, row))

                self.SaveBulkToFile(bulkID, clientData)
            else:
                self.LogError('No bulk file found for', bulkID, ". Why I don't know. Should be fixed by now. So I guess bulk is somewhere broken.")




    def UpdateDeletedRows(self, toBeDeleted, allKeyNames):
        for bulkID in toBeDeleted:
            if not self.BulkExists(bulkID):
                self.LogError('I was told to delete keys in bulk', bulkID, 'but the bulk does not exist. Doing nothing with it.')
                continue
            self.LogInfo('Removing data from bulk', bulkID)
            keyNames = allKeyNames[bulkID]
            clientData = self.LoadBulkFromFile(bulkID)
            clientDataToDelete = []
            keysToDelete = toBeDeleted[bulkID]
            for (i, row,) in enumerate(clientData):
                rowKey = self.GetKeyValues(keyNames, row)
                if rowKey in keysToDelete:
                    clientDataToDelete.append(i)
                    self.LogInfo('bulk %s : removing key %s' % (bulkID, rowKey))

            clientDataToDelete.sort(reverse=True)
            for i in clientDataToDelete:
                del clientData[i]

            self.SaveBulkToFile(bulkID, clientData)




    def UpdateFullBulkFiles(self, toGet = None, toDelete = None):
        bulks = {}
        if toGet is None or len(toGet) > 0:
            (chunk, numberOfChunks, chunkSetID, self.branch,) = self.bulkMgr.GetFullFiles(toGet)
            if toGet is None:
                self.LogInfo('Asked the server for all bulk files. I will get them in', numberOfChunks, 'chunk(s) - Got one chunk (number 0) already')
            else:
                self.LogInfo('Asked the server for', len(toGet), 'full bulk file(s) I will get them in', numberOfChunks, 'chunk(s) - Got one chunk (number 0) already')
            bulks = {}
            self.UpdateLoginProgress('loginprogress::gettingbulkdata', numberOfChunks)
            for bulkID in chunk:
                bulks[bulkID] = chunk[bulkID]

            for chunkNumber in xrange(1, numberOfChunks):
                toBeChanged = self.bulkMgr.GetFullFilesChunk(chunkSetID, chunkNumber)
                self.UpdateLoginProgress('loginprogress::gettingbulkdata', numberOfChunks)
                self.LogInfo('Got chunk', chunkNumber, 'from chunkset', chunkSetID)
                for bulkID in toBeChanged:
                    changes = toBeChanged[bulkID]
                    if bulkID in bulks:
                        for row in changes:
                            bulks[bulkID].append(row)

                    else:
                        bulks[bulkID] = changes


            self.lastLoginProgressID = 1
        else:
            self.LogInfo('Only removing bulk files so UpdateFullBulkFiles did not need to call the server.')
        if toDelete is None:
            toDelete = self.GetCurrentBulkIDs()
        for bulkID in bulks:
            self.LogInfo('Saving full bulk file:', bulkID)
            self.SaveBulkToFile(bulkID, bulks[bulkID])
            if bulkID in toDelete:
                toDelete.remove(bulkID)

        for bulkID in toDelete:
            self.DeleteBulkFile(bulkID)




    def GetKeyValues(self, keyNames, row):
        numberOfKeys = len(keyNames)
        if numberOfKeys == 1:
            return row[keyNames[0]]
        if numberOfKeys == 2:
            return (row[keyNames[0]], row[keyNames[1]])
        if numberOfKeys == 3:
            return (row[keyNames[0]], row[keyNames[1]], row[keyNames[2]])



    def GetUnsubmittedChanges(self):
        if not prefs.GetValue('allowUnsubmittedRevisions', 1):
            self.LogInfo('Client has allowUnsubmittedRevisions set to 0. Not fetching unsubmitted BSD data')
            return 
        unsubmitted = self.bulkMgr.GetUnsubmittedChanges()
        if unsubmitted is None:
            self.LogInfo('Server had no unsubmitted BSD data for us')
            return 
        toBeChanged = unsubmitted['toBeChanged']
        toBeDeleted = unsubmitted['toBeDeleted']
        changedTablesKeys = unsubmitted['changedTablesKeys']
        self.LogInfo('Updating cfg with unsubmitted BSD data')
        for (bulkID, changes,) in toBeChanged.iteritems():
            if bulkID in cfg.bulkIDsToCfgNames:
                for cfgName in cfg.bulkIDsToCfgNames[bulkID]:
                    cfgEntry = getattr(cfg, cfgName, None)
                    if isinstance(cfgEntry, sys.Recordset):
                        keyNames = changedTablesKeys[bulkID]
                        for row in changes:
                            try:
                                keyValues = self.GetKeyValues(keyNames, row)
                            except KeyError as e:
                                self.LogError('== == == == == == == == == == == == == == == == == == == ==')
                                self.LogError('Error in GetUnsubmittedChanges. Key does not exist in the row we wanted to update.')
                                self.LogError('keyNames:', keyNames, ', bulkID:', bulkID, ', cfgName:', cfgName)
                                self.LogError('row:', row)
                                self.LogError('header:', row.__header__)
                                self.LogError(e)
                                self.LogError('== == == == == == == == == == == == == == == == == == == ==')
                                continue
                            cfgEntry.data[keyValues] = row

                    elif isinstance(cfgEntry, dbutil.CFilterRowset):
                        filterColumnName = cfgEntry.columnName
                        for changedRow in changes:
                            keyValue = changedRow[filterColumnName]
                            if keyValue in cfgEntry:
                                cfgRows = cfgEntry[keyValue]
                                for (i, cfgRow,) in enumerate(cfgRows):
                                    for keyName in changedTablesKeys[bulkID]:
                                        if cfgRow[keyName] != changedRow[keyName]:
                                            break
                                    else:
                                        cfgEntry[keyValue][i] = changedRow
                                        break

                                else:
                                    cfgEntry[keyValue].append(changedRow)

                            else:
                                cfgEntry[keyValue] = [changedRow]

                    elif isinstance(cfgEntry, dbutil.CRowset):
                        toDelete = []
                        keyNames = changedTablesKeys[bulkID]
                        for (i, row,) in enumerate(cfgEntry):
                            rowKey = self.GetKeyValues(keyNames, row)
                            if rowKey in changes:
                                toDelete.append(i)

                        toDelete.sort(reverse=True)
                        for i in toDelete:
                            del cfgEntry[i]

                    else:
                        self.LogWarn('cfgEntry not of type: Recordset, CFilterRowset or CRowset. not updating unsubmitted revisions for it.', cfgName, bulkID)

            else:
                self.LogWarn('There is an unsubmitted change in bulk', bulkID, " that I don't know what cfg entry it belongs to. Skipping it")

        for bulkID in toBeDeleted:
            changes = toBeDeleted[bulkID]
            if bulkID in cfg.bulkIDsToCfgNames:
                for cfgName in cfg.bulkIDsToCfgNames[bulkID]:
                    cfgEntry = getattr(cfg, cfgName, None)
                    if isinstance(cfgEntry, sys.Recordset):
                        for key in changes:
                            if key in cfgEntry.data:
                                del cfgEntry.data[key]
                            else:
                                self.LogWarn("Can't find revision for an unsubmitted revisions I wanted to delete")

                    elif isinstance(cfgEntry, dbutil.CFilterRowset):
                        filterColumnName = cfgEntry.columnName
                        keyNames = changedTablesKeys[bulkID]
                        numberOfKeys = len(keyNames)
                        key1 = keyNames[0]
                        if numberOfKeys == 2:
                            key2 = keyNames[1]
                            (changesKey1, changesKey2,) = zip(*changes)
                        elif numberOfKeys == 3:
                            key2 = keyNames[1]
                            key3 = keyNames[2]
                            (changesKey1, changesKey2, changesKey3,) = zip(*changes)
                        toDelete = []
                        for filterKey in cfgEntry:
                            for (i, filterRows,) in enumerate(cfgEntry[filterKey]):
                                if numberOfKeys == 1 and filterRows[key1] in changes:
                                    toDelete.append((i, filterKey))
                                elif numberOfKeys == 2:
                                    if filterRows[key1] in changesKey1 and filterRows[key2] in changesKey2:
                                        toDelete.append((i, filterKey))
                                elif numberOfKeys == 3:
                                    if filterRows[key1] in changesKey1 and filterRows[key2] in changesKey2 and filterRows[key3] in changesKey3:
                                        toDelete.append((i, filterKey))


                        toDelete.sort(reverse=True)
                        for (ix, filterKey,) in toDelete:
                            del cfgEntry[filterKey][ix]
                            if len(cfgEntry[filterKey]) == 0:
                                del cfgEntry[filterKey]

                    elif isinstance(cfgEntry, dbutil.CRowset):
                        toDelete = []
                        keyNames = changedTablesKeys[bulkID]
                        for (i, row,) in enumerate(cfgEntry):
                            rowKey = self.GetKeyValues(keyNames, row)
                            if rowKey in changes:
                                toDelete.append(i)

                        toDelete.sort(reverse=True)
                        for i in toDelete:
                            del cfgEntry[i]

                    else:
                        self.LogWarn('cfgEntry not of type: Recordset, CFilterRowset or CRowset. not deleting unsubmitted revisions for it.', cfgName, bulkID)

            else:
                self.LogWarn('There is unsubmitted delete change in bulk', bulkID, " that I don't know what cfg entry it belongs to. Skipping it")




    def LoadBulkFromFile(self, bulkID):
        fileName = BULK_CACHE_PATH + str(bulkID) + BULK_FILE_EXT
        if os.path.exists(fileName):
            with open(fileName, 'rb') as bulkFile:
                marshalData = bulkFile.read()
            return blue.marshal.Load(marshalData)
        fileName = BULK_SYSTEM_PATH + str(bulkID) + BULK_FILE_EXT
        if os.path.exists(fileName):
            with open(fileName, 'rb') as bulkFile:
                marshalData = bulkFile.read()
            return blue.marshal.Load(marshalData)
        raise RuntimeError('File for bulk %d not found' % bulkID)



    def BulkExists(self, bulkID, includeSystemFolder = True):
        fileName = BULK_CACHE_PATH + str(bulkID) + BULK_FILE_EXT
        if os.path.exists(fileName):
            return True
        else:
            if includeSystemFolder:
                fileName = BULK_SYSTEM_PATH + str(bulkID) + BULK_FILE_EXT
                return os.path.exists(fileName)
            return False



    def SaveBulkToFile(self, bulkID, value):
        fileName = BULK_CACHE_PATH + str(bulkID) + BULK_FILE_EXT
        marshalData = blue.marshal.Save(value)
        blue.win32.AtomicFileWrite(fileName, marshalData)



    def DeleteBulkFile(self, bulkID):
        fileName = BULK_CACHE_PATH + str(bulkID) + BULK_FILE_EXT
        if os.path.exists(fileName):
            try:
                os.remove(fileName)
                self.LogInfo("Deleted local cached bulk file because I didn't like it", bulkID)
            except:
                self.LogWarn('I was trying to delete a bulk file but could not:', fileName)



    def GetCurrentBulkIDs(self):
        bulkFiles = set()
        for filename in os.listdir(BULK_CACHE_PATH):
            if filename.lower().endswith(BULK_FILE_EXT):
                try:
                    bulkFiles.add(int(filename[:(-len(BULK_FILE_EXT))]))
                except:
                    self.LogWarn("Found a file in the cache bulkdata folder that I don't like, ignoring it.", filename)

        if os.path.exists(BULK_SYSTEM_PATH):
            for filename in os.listdir(BULK_SYSTEM_PATH):
                if filename.lower().endswith(BULK_FILE_EXT):
                    try:
                        bulkFiles.add(int(filename[:(-len(BULK_FILE_EXT))]))
                    except:
                        self.LogWarn("Found a file in the system bulkdata folder that I don't like, ignoring it.", filename)

        return list(bulkFiles)



    def GetHash(self):
        bulkIDs = self.GetCurrentBulkIDs()
        bulkIDs.sort()
        m = hashlib.md5()
        m.update(str(bulkIDs))
        return m.hexdigest()



    def GetVersion(self):
        version = None
        branch = None
        fileName = BULK_CACHE_PATH + VERSION_FILENAME
        if os.path.exists(fileName):
            with open(fileName, 'rb') as versionFile:
                marshalData = versionFile.read()
            data = blue.marshal.Load(marshalData)
            version = data['changeID']
            branch = data['branch']
        else:
            fileName = BULK_SYSTEM_PATH + VERSION_FILENAME
            if os.path.exists(fileName):
                with open(fileName, 'rb') as versionFile:
                    marshalData = versionFile.read()
                data = blue.marshal.Load(marshalData)
                version = data['changeID']
                branch = data['branch']
        if version is not None:
            self.LogInfo('Client is at bulk version', version)
        else:
            self.LogWarn('Did not find the bulk version')
        return (version, branch)



    def SetVersion(self, changeID):
        data = {'changeID': changeID,
         'branch': self.branch}
        fileName = BULK_CACHE_PATH + VERSION_FILENAME
        marshalData = blue.marshal.Save(data)
        blue.win32.AtomicFileWrite(fileName, marshalData)




