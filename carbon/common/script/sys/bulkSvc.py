import service
import blue
import os
import hashlib
import macho
import dbutil
import sys
BULK_SYSTEM_PATH = blue.os.ResolvePathForWriting(u'app:/bulkdata/')
BULK_CACHE_PATH = blue.os.ResolvePathForWriting(u'cache:/bulkdata/%s/' % str(macho.version))
BULK_FILE_EXT = '.cache2'
VERSION_FILENAME = 'version'

class BulkSvc(service.Service):
    __guid__ = 'svc.bulkSvc'

    def Run(self, ms = None):
        self.state = service.SERVICE_START_PENDING
        self.lastLoginProgressID = 0
        basePath = blue.os.ResolvePathForWriting(u'cache:/bulkdata')
        if boot.role == 'client':
            path = basePath + '/' + str(macho.version) + '/'
            self.SetBulkCachePath(path)
        else:
            machoSvc = sm.GetService('machoNet')
            path = basePath + 'Svc%s/%s/' % (machoSvc.GetBasePortNumber(), macho.version)
            self.SetBulkCachePath(path)
            polarisID = self.session.ConnectToSolServerService('machoNet').GetNodeFromAddress(const.cluster.SERVICE_POLARIS, 0)
            self.bulkMgr = self.session.ConnectToRemoteService('bulkMgr', nodeID=polarisID)
            self.UpdateBulk()
        self.state = service.SERVICE_RUNNING



    def Connect(self):
        self.bulkMgr = sm.RemoteSvc('bulkMgr')
        self.UpdateBulk()



    def UpdateLoginProgress(self, name, totalSteps = None):
        self.lastLoginProgressID += 1
        cfg.ReportLoginProgress(name, self.lastLoginProgressID, totalSteps)



    def UpdateBulk(self, doHashCheck = True):
        self.LogInfo('Lets see if there is some new bulk data for us')
        self.CheckCacheVersion()
        (changeID, branch, fullFileLock,) = self.GetVersion()
        if fullFileLock:
            serverBulkIDs = self.bulkMgr.GetAllBulkIDs()
            clientBulkIDs = self.GetCurrentBulkIDs()
            idsToRemove = [ cID for cID in clientBulkIDs if cID in serverBulkIDs ]
            for bulkID in idsToRemove:
                serverBulkIDs.remove(bulkID)
                clientBulkIDs.remove(bulkID)

            self.LogInfo('I was at some point stopped while getting full files. Now getting the rest.')
            self.UpdateFullBulkFiles(serverBulkIDs, clientBulkIDs)
            (changeID, branch, fullFileLock,) = self.GetVersion()
        if changeID is None:
            self.UpdateFullBulkFiles()
            (changeID, branch, fullFileLock,) = self.GetVersion()
            self.LogInfo('bulk updated done, we are now at', changeID)
            return 
        if doHashCheck:
            hashValue = self.GetHash()
        else:
            hashValue = None
        updateData = self.bulkMgr.UpdateBulk(changeID, hashValue, branch)
        updateType = updateData['type']
        self.allowUnsubmitted = updateData['allowUnsubmitted']
        if 'version' in updateData:
            serverVersion = updateData['version']
        if 'data' in updateData:
            updateInfo = updateData['data']
        if updateType == const.updateBulkStatusOK:
            self.LogInfo('Bulk data is up to date:', changeID)
            return 
        if updateType == const.updateBulkStatusHashMismatch:
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
        if updateType in [const.updateBulkStatusWrongBranch, const.updateBulkStatusClientNewer, const.updateBulkStatusTooManyRevisions]:
            if updateType == const.updateBulkStatusWrongBranch:
                self.LogError('Client is at different branch than the server so I need to fetch everything.')
            elif updateType == const.updateBulkStatusClientNewer:
                self.LogError('Client is at changeID', changeID, 'but the server is at lower changeID', serverVersion, 'so I need to fetch everything.')
            else:
                self.LogWarn('The server has too many revisions for us. So we should fetch everything. We are at changeID', changeID, 'server is at', serverVersion)
            self.UpdateFullBulkFiles()
            (serverChangeID, branch,) = self.bulkMgr.GetVersion()
            self.SetVersion(serverChangeID, branch)
            self.LogInfo('bulk updated done, we are now at', serverVersion)
            return 
        if updateType == const.updateBulkStatusNeedToUpdate:
            self.UpdateLoginProgress('loginprogress::gettingbulkdata', updateInfo['chunkCount'])
            self.UpdateChangedRows(updateInfo['chunk'], updateInfo['changedTablesKeys'])
            self.UpdateDeletedRows(updateInfo['toBeDeleted'], updateInfo['changedTablesKeys'])
            for chunkNumber in xrange(1, updateInfo['chunkCount']):
                self.LogInfo('We have more chunks. Now fetching chunk', chunkNumber)
                self.UpdateLoginProgress('loginprogress::gettingbulkdata', updateInfo['chunkCount'])
                toBeChanged = self.bulkMgr.GetChunk(changeID, chunkNumber)
                self.UpdateChangedRows(toBeChanged, updateInfo['changedTablesKeys'])

            branch = updateInfo['branch']
            self.SetVersion(serverVersion, branch)
            self.LogInfo('bulk updated done, we are now at', serverVersion)
        else:
            raise RuntimeError('Unknown updateType from server', updateType)



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
        (changeID, branch, fullFileLock,) = self.GetVersion()
        if changeID is None:
            (serverChangeID, serverBranch,) = self.bulkMgr.GetVersion()
            branch = serverBranch
            changeID = serverChangeID
        self.SetVersion(changeID, branch, True)
        bulks = {}
        if toDelete is None:
            toDelete = self.GetCurrentBulkIDs()
        if toGet is None or len(toGet) > 0:
            (toBeChanged, bulksEndingInChunk, numberOfChunks, chunkSetID, self.allowUnsubmitted,) = self.bulkMgr.GetFullFiles(toGet)
            if toGet is None:
                self.LogInfo('Asked the server for all bulk files. I will get them in', numberOfChunks, 'chunk(s) - Got one chunk (number 0) already')
            else:
                self.LogInfo('Asked the server for', len(toGet), 'full bulk file(s) I will get them in', numberOfChunks, 'chunk(s) - Got one chunk (number 0) already')
            bulks = {}
            for chunkNumber in xrange(0, numberOfChunks):
                self.UpdateLoginProgress('loginprogress::gettingbulkdata', numberOfChunks)
                if chunkNumber != 0:
                    (toBeChanged, bulksEndingInChunk,) = self.bulkMgr.GetFullFilesChunk(chunkSetID, chunkNumber)
                self.LogInfo('Got bulkdata chunk', chunkNumber + 1, 'of', numberOfChunks, 'from chunkset', chunkSetID)
                for bulkID in toBeChanged:
                    changes = toBeChanged[bulkID]
                    if bulkID in bulks:
                        for row in changes:
                            bulks[bulkID].append(row)

                    else:
                        bulks[bulkID] = changes

                if bulksEndingInChunk is not None:
                    toRemove = []
                    for bulkID in bulksEndingInChunk:
                        self.LogInfo('Saving full bulk file:', bulkID)
                        self.SaveBulkToFile(bulkID, bulks[bulkID])
                        if bulkID in toDelete:
                            toDelete.remove(bulkID)
                        toRemove.append(bulkID)

                    for bulkID in toRemove:
                        del bulks[bulkID]


            self.lastLoginProgressID = 0
        else:
            self.LogInfo('Only removing bulk files so UpdateFullBulkFiles did not need to call the server.')
        for bulkID in toDelete:
            self.DeleteBulkFile(bulkID)

        self.SetVersion(changeID, branch)



    def GetKeyValues(self, keyNames, row):
        numberOfKeys = len(keyNames)
        if numberOfKeys == 1:
            return row[keyNames[0]]
        if numberOfKeys == 2:
            return (row[keyNames[0]], row[keyNames[1]])
        if numberOfKeys == 3:
            return (row[keyNames[0]], row[keyNames[1]], row[keyNames[2]])



    def GetUnsubmittedChanges(self):
        if not self.allowUnsubmitted:
            self.LogInfo('Server is not configured to allow fetching of unsubmitted BSD data')
            return 
        self.LogInfo('Updating cfg with unsubmitted BSD data')
        unsubmitted = self.bulkMgr.GetUnsubmittedChanges()
        if unsubmitted is None:
            self.LogInfo('Server had no unsubmitted BSD data for us')
            return 
        toBeChanged = unsubmitted['toBeChanged']
        toBeDeleted = unsubmitted['toBeDeleted']
        changedTablesKeys = unsubmitted['changedTablesKeys']
        chunkCount = unsubmitted['chunkCount']
        for chunkNumber in xrange(0, chunkCount):
            self.LogInfo('Starting on unsubmitted chunk ', chunkNumber + 1, 'of', chunkCount)
            if chunkNumber != 0:
                toBeChanged = self.bulkMgr.GetUnsubmittedChunk(chunkNumber)
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
                                    self.LogError('Error in GetUnsubmittedChanges. Key does not exist in the row we wanted to update.', keyNames, row)
                                    continue
                                cfgEntry.data[keyValues] = row

                        elif isinstance(cfgEntry, dbutil.CFilterRowset):
                            filterColumnName = cfgEntry.columnName
                            if cfgEntry.indexName is not None:
                                self.LogError('BulkSvc.GetUnsubmittedChanges() - Unsupported cfgEntry', cfgName.len(changes))
                                continue
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
                                    rowDescriptor = cfgEntry.itervalues().next().header
                                    cfgEntry[keyValue] = dbutil.CRowset(rowDescriptor, [changedRow])

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
                    self.LogWarn('There is an unsubmitted change in bulk', bulkID, "and I don't know what cfg entry it belongs to. Skipping it")


        for (bulkID, changes,) in toBeDeleted.iteritems():
            if bulkID not in cfg.bulkIDsToCfgNames:
                self.LogWarn('There is unsubmitted delete change in bulk', bulkID, " that I don't know what cfg entry it belongs to. Skipping it")
                continue
            for cfgName in cfg.bulkIDsToCfgNames[bulkID]:
                cfgEntry = getattr(cfg, cfgName, None)
                if isinstance(cfgEntry, sys.Recordset):
                    for key in changes:
                        if key in cfgEntry.data:
                            del cfgEntry.data[key]
                        else:
                            self.LogWarn("Can't find revision for an unsubmitted revisions I wanted to delete", cfgName)

                elif isinstance(cfgEntry, dbutil.CFilterRowset):
                    if cfgEntry.indexName is not None:
                        self.LogError('BulkSvc.GetUnsubmittedChanges() - Unsupported cfgEntry', cfgName, len(changes))
                        continue
                    filterColumnName = cfgEntry.columnName
                    keyNames = changedTablesKeys[bulkID]
                    toDelete = []
                    for (filterKey, filterRows,) in cfgEntry.iteritems():
                        for (i, filterRow,) in enumerate(filterRows):
                            key = tuple((getattr(filterRow, keyName, None) for keyName in keyNames))
                            if key in changes:
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





    def LoadBulkFromFile(self, bulkID):
        fileName = self.GetBulkCachePath() + str(bulkID) + BULK_FILE_EXT
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
        fileName = self.GetBulkCachePath() + str(bulkID) + BULK_FILE_EXT
        if os.path.exists(fileName):
            return True
        else:
            if includeSystemFolder:
                fileName = BULK_SYSTEM_PATH + str(bulkID) + BULK_FILE_EXT
                return os.path.exists(fileName)
            return False



    def SaveBulkToFile(self, bulkID, value):
        fileName = self.GetBulkCachePath() + str(bulkID) + BULK_FILE_EXT
        marshalData = blue.marshal.Save(value)
        blue.win32.AtomicFileWrite(fileName, marshalData)



    def DeleteBulkFile(self, bulkID):
        fileName = self.GetBulkCachePath() + str(bulkID) + BULK_FILE_EXT
        if os.path.exists(fileName):
            try:
                os.remove(fileName)
                self.LogInfo("Deleted local cached bulk file because I didn't like it", bulkID)
            except:
                self.LogWarn('I was trying to delete a bulk file but could not:', fileName)



    def GetCurrentBulkIDs(self):
        bulkFiles = set()
        for filename in os.listdir(self.GetBulkCachePath()):
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



    def CheckCacheVersion(self):
        cacheVersionfileName = self.GetBulkCachePath() + VERSION_FILENAME
        if os.path.exists(cacheVersionfileName):
            systemVersionfileName = BULK_SYSTEM_PATH + VERSION_FILENAME
            if not os.path.exists(systemVersionfileName):
                return 
            with open(cacheVersionfileName, 'rb') as versionFile:
                marshalData = versionFile.read()
            cacheVersion = blue.marshal.Load(marshalData)['changeID']
            with open(systemVersionfileName, 'rb') as versionFile:
                marshalData = versionFile.read()
            systemVersion = blue.marshal.Load(marshalData)['changeID']
            if cacheVersion < systemVersion:
                self.LogInfo('System folder has bulkdata version', systemVersion, ', cache folder has', cacheVersion, '. Deleting cache')
                bulkIDs = self.GetCurrentBulkIDs()
                try:
                    os.remove(cacheVersionfileName)
                    for bulkID in bulkIDs:
                        self.DeleteBulkFile(bulkID)

                except:
                    self.LogError('Error removing files from the bulkdata cache folder')



    def GetVersion(self):
        version = None
        branch = None
        fullFileLock = False
        fileName = self.GetBulkCachePath() + VERSION_FILENAME
        if os.path.exists(fileName):
            with open(fileName, 'rb') as versionFile:
                marshalData = versionFile.read()
            data = blue.marshal.Load(marshalData)
            version = data['changeID']
            branch = data['branch']
            if 'fullFileLock' in data:
                fullFileLock = True
        else:
            fileName = BULK_SYSTEM_PATH + VERSION_FILENAME
            if os.path.exists(fileName):
                with open(fileName, 'rb') as versionFile:
                    marshalData = versionFile.read()
                data = blue.marshal.Load(marshalData)
                version = data['changeID']
                branch = data['branch']
        return (version, branch, fullFileLock)



    def SetVersion(self, changeID, branch, fullFileLock = False):
        data = {'changeID': changeID,
         'branch': branch}
        if fullFileLock:
            data['fullFileLock'] = True
        fileName = self.GetBulkCachePath() + VERSION_FILENAME
        marshalData = blue.marshal.Save(data)
        blue.win32.AtomicFileWrite(fileName, marshalData)



    def GetBulkCachePath(self):
        return self.buldCachePath



    def SetBulkCachePath(self, path):
        self.LogInfo('Using bulkdata cache path:', path)
        self.buldCachePath = path
        try:
            if not os.path.exists(self.buldCachePath):
                os.makedirs(self.buldCachePath)
        except:
            self.LogError('Error creating bulk cache folder', self.buldCachePath)
            raise UserError('BulkDirCreationError')




