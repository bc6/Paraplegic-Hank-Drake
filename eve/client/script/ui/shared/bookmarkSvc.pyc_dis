#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/bookmarkSvc.py
import blue
import bookmarkUtil
import util
import uiutil
import log
import sys
import uthread
from service import Service
from collections import defaultdict
CACHE_EXPIRATION_TIME = 5 * const.MIN

class BookmarkSvc(Service):
    __guid__ = 'svc.bookmarkSvc'
    __startupdependencies__ = ['machoNet']
    __notifyevents__ = ['OnBookmarkAdded', 'OnBookmarkDeleted', 'OnBookmarkAdd']

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        self.corpBookmarkMgr = sm.RemoteSvc('corpBookmarkMgr')
        self.bookmarkMgr = sm.RemoteSvc('bookmark')
        self.lastUpdateTime = None
        self.validCategories = (const.categoryCelestial,
         const.categoryAsteroid,
         const.categoryStation,
         const.categoryShip,
         const.categoryStructure,
         const.categoryPlanetaryInteraction)
        self.bookmarksPrimed = False

    def PrimeBookmarks(self):
        self.bookmarkCache = {}
        self.folders = {}
        if not util.IsNPC(session.corpid):
            bookmarks, folders = self.corpBookmarkMgr.GetBookmarks()
            self.bookmarkCache.update(bookmarks)
            self.folders.update(folders)
        bookmarks, folders = self.bookmarkMgr.GetBookmarks()
        self.bookmarkCache.update({bookmark.bookmarkID:bookmark for bookmark in bookmarks})
        self.folders.update({folder.folderID:folder for folder in folders})
        self.lastUpdateTime = blue.os.GetWallclockTime()
        self.bookmarksPrimed = True

    def GetBookmarks(self):
        if not self.bookmarksPrimed:
            self.PrimeBookmarks()
        elif self.lastUpdateTime is None or blue.os.GetWallclockTime() - self.lastUpdateTime > CACHE_EXPIRATION_TIME:
            bookmarks, folders = self.corpBookmarkMgr.GetBookmarks()
            self.ClearCorpBookmarksAndFolders()
            self.bookmarkCache.update(bookmarks)
            self.folders.update(folders)
            self.lastUpdateTime = blue.os.GetWallclockTime()
        return self.bookmarkCache

    def GetBookmarksAndFolders(self):
        return (self.GetBookmarks(), self.folders)

    def ClearCorpBookmarksAndFolders(self):
        for bookmarkID, bookmark in self.bookmarkCache.items():
            if bookmark.ownerID == session.corpid:
                del self.bookmarkCache[bookmarkID]

        for folderID, folder in self.folders.items():
            if folder.ownerID == session.corpid:
                del self.folders[folderID]

    def GetBookmark(self, bookmarkID):
        return self.bookmarkCache[bookmarkID]

    def CreateFolder(self, ownerID, folderName):
        bookmarkMgr = self.bookmarkMgr if ownerID == session.charid else self.corpBookmarkMgr
        folder = bookmarkMgr.CreateFolder(folderName)
        if folder:
            self.folders[folder.folderID] = folder
            self.RefreshWindow()

    def UpdateFolder(self, ownerID, folderID, folderName):
        bookmarkMgr = self.bookmarkMgr if ownerID == session.charid else self.corpBookmarkMgr
        if bookmarkMgr.UpdateFolder(folderID, folderName):
            self.folders[folderID].folderName = folderName
            self.RefreshWindow()

    def MoveBookmarksToFolder(self, ownerID, folderID, bookmarkIDs):
        folderOwnerID = ownerID
        if folderOwnerID == session.corpid:
            bookmarkMgr = self.corpBookmarkMgr
        elif folderOwnerID == session.charid:
            bookmarkMgr = self.bookmarkMgr
        else:
            raise RuntimeError('Folder neither owned by corp not char %s', ownerID)
        bookmarksToCopy = []
        bookmarksToMove = set()
        for bookmarkID in bookmarkIDs:
            bookmark = self.bookmarkCache[bookmarkID]
            if bookmark.ownerID == folderOwnerID:
                bookmarksToMove.add(bookmarkID)
            else:
                bookmarksToCopy.append(bookmarkID)

        if len(bookmarksToMove) > 0:
            rows = bookmarkMgr.MoveBookmarksToFolder(folderID, bookmarkIDs)
            for row in rows:
                try:
                    self.bookmarkCache[row.bookmarkID].folderID = row.folderID
                except KeyError:
                    sys.exc_clear()

        if len(bookmarksToCopy) > 0:
            newBookmarks, message = bookmarkMgr.CopyBookmarks(bookmarksToCopy, folderID)
            if message is not None:
                uthread.new(eve.Message, *message)
            self.bookmarkCache.update(newBookmarks)

    def UpdateBookmark(self, bookmarkID, ownerID, memo, note, folderID):
        bookmark = self.bookmarkCache[bookmarkID]
        if bookmark.ownerID == session.corpid:
            self.corpBookmarkMgr.UpdateBookmark(bookmarkID, ownerID, memo, note, folderID)
        else:
            self.corpBookmarkMgr.UpdatePlayerBookmark(bookmarkID, ownerID, memo, note, folderID)
        bookmark.memo = memo
        bookmark.note = note
        bookmark.folderID = folderID
        bookmark.ownerID = ownerID
        self.RefreshWindow()

    def OnBookmarkAdded(self, bookmark):
        self.bookmarkCache[bookmark.bookmarkID] = bookmark
        sm.GetService('neocom').Blink('addressbook')
        self.RefreshWindow()

    def OnBookmarkDeleted(self, bookmarkID):
        try:
            del self.bookmarkCache[bookmarkID]
            sm.GetService('neocom').Blink('addressbook')
            self.RefreshWindow()
        except KeyError:
            pass

    def OnBookmarkAdd(self, bookmark, refresh = 1):
        self.bookmarkCache[bookmark.bookmarkID] = bookmark
        if refresh:
            self.RefreshWindow()

    def RefreshWindow(self):
        sm.ScatterEvent('OnRefreshBookmarks')

    def GetValidBookmarks(self):
        ret = []
        for bookmark in self.bookmarkCache.itervalues():
            typeOb = cfg.invtypes.Get(bookmark.typeID)
            if typeOb.categoryID not in self.validCategories:
                continue
            ret.append(bookmark)

        return ret

    def GetBookmarksForOwner(self, ownerID):
        return {bm.bookmarkID:bm for bm in self.GetBookmarks().itervalues() if bm.ownerID == ownerID}

    def GetMyBookmarks(self):
        return self.GetBookmarksForOwner(session.charid)

    def GetCorpBookmarks(self):
        if util.IsNPC(session.corpid):
            return {}
        return self.GetBookmarksForOwner(session.corpid)

    def GetAgentBookmarks(self):
        bookmarks = {}
        agentMenu = sm.GetService('journal').GetMyAgentJournalBookmarks()
        if agentMenu:
            for missionNameID, bms, agentID in agentMenu:
                missionName = unicode(missionNameID) + unicode(agentID)
                for bm in bms:
                    c = bm.copy()
                    c.missionName = missionName
                    c.hint = bm.hint
                    c.memo = c.hint + '\t'
                    c.bookmarkID = ('agentmissions',
                     c.agentID,
                     c.locationType,
                     c.locationNumber)
                    bookmarks[c.bookmarkID] = c

        return bookmarks

    def GetAllBookmarks(self):
        bms = self.GetBookmarks().copy()
        bms.update(self.GetAgentBookmarks())
        return bms

    def GetBookmarksInFoldersForOwner(self, ownerID):
        bookmarkFolders = defaultdict(lambda : util.KeyVal(bookmarks=[], folderID=None, folderName='', ownerID=session.charid))
        bms, folders = self.GetBookmarksAndFolders()
        for folder in folders.itervalues():
            if folder.ownerID == ownerID:
                kv = util.KeyVal(folder)
                kv.bookmarks = []
                bookmarkFolders[folder.folderID] = kv

        for bm in bms.itervalues():
            folderID = bm.folderID
            if folderID not in folders:
                folderID = None
            elif folders[bm.folderID].ownerID != ownerID:
                folderID = None
            if bm.ownerID == ownerID:
                bookmarkFolders[folderID].bookmarks.append(bm)

        return bookmarkFolders

    def UpdateFoldersToDB(self):
        info = []
        listGroupIDs = set()
        for group in uicore.registry.GetListGroups('places2_%s' % session.charid).itervalues():
            listGroupIDs.add(group['id'])
            bookmarkIDs = set()
            for bookmarkID in group['groupItems']:
                try:
                    bookmark = self.bookmarkCache[bookmarkID]
                except KeyError:
                    sys.exc_clear()
                    continue

                if bookmark.folderID is not None:
                    continue
                bookmarkIDs.add(bookmarkID)

            if len(bookmarkIDs) > 0:
                info.append((bookmarkIDs, group['label']))

        if len(info) > 0:
            rows, folders = self.corpBookmarkMgr.MoveFoldersToDB(info)
            self.folders.update(folders)
            for row in rows:
                bookmark = self.bookmarkCache.get(row.bookmarkID)
                if bookmark is None:
                    self.LogError("UpdateFoldersToDB::Didn't find bookmark", row.bookmarkID)
                    continue
                bookmark.folderID = row.folderID

        for listGroupID in listGroupIDs:
            uicore.registry.DeleteListGroup(listGroupID)

        self.RefreshWindow()

    def BookmarkLocation(self, itemID, ownerID, name, comment, typeID, locationID = None, folderID = None):
        memo = self.ZipMemo(name[:100], '')
        bookmarkID, itemID, typeID, x, y, z, locationID = sm.RemoteSvc('bookmark').BookmarkLocation(itemID, ownerID, memo, comment, folderID=folderID)
        if bookmarkID:
            bm = util.KeyVal()
            bm.bookmarkID = bookmarkID
            bm.ownerID = ownerID
            bm.itemID = itemID
            bm.typeID = typeID
            bm.flag = None
            bm.memo = memo
            bm.created = blue.os.GetWallclockTimeNow()
            bm.x = x
            bm.y = y
            bm.z = z
            bm.locationID = locationID
            bm.note = comment
            bm.folderID = folderID
            bm.creatorID = session.charid
            self.bookmarkCache[bookmarkID] = bm
            self.RefreshWindow()
            sm.ScatterEvent('OnBookmarkCreated', bookmarkID, comment)

    def BookmarkScanResult(self, locationID, name, comment, resultID, ownerID, folderID = None):
        memo = self.ZipMemo(name[:100], '')
        bookmarkID, itemID, typeID, x, y, z, locationID = self.bookmarkMgr.BookmarkScanResult(locationID, memo, comment, resultID, ownerID, folderID=folderID)
        if bookmarkID:
            bm = util.KeyVal()
            bm.bookmarkID = bookmarkID
            bm.ownerID = ownerID
            bm.itemID = None
            bm.typeID = typeID
            bm.flag = None
            bm.memo = memo
            bm.created = blue.os.GetWallclockTimeNow()
            bm.x = x
            bm.y = y
            bm.z = z
            bm.locationID = locationID
            bm.note = comment
            bm.folderID = folderID
            bm.creatorID = session.charid
            self.bookmarkCache[bookmarkID] = bm
            self.RefreshWindow()
            sm.ScatterEvent('OnBookmarkCreated', bookmarkID, comment)

    def DeleteBookmarks(self, bookmarkIDs):
        bookmarksByOwner = defaultdict(set)
        for bookmarkID in bookmarkIDs:
            bookmark = self.bookmarkCache[bookmarkID]
            bookmarksByOwner[bookmark.ownerID].add(bookmarkID)

        deletedBookmarkIDs = []
        if session.corpid in bookmarksByOwner:
            deletedBookmarkIDs.extend(self.DeleteCorpBookmarks(bookmarksByOwner[session.corpid]))
        if session.charid in bookmarksByOwner:
            deletedBookmarkIDs.extend(self.DeletePersonalBookmarks(bookmarksByOwner[session.charid]))
        self.RefreshWindow()
        sm.ScatterEvent('OnBookmarksDeleted', deletedBookmarkIDs)

    def DeleteCorpBookmarks(self, bookmarkIDs):
        deletedBookmarks = self.corpBookmarkMgr.DeleteBookmarks(bookmarkIDs)
        deletedBookmarkIDs = []
        for bookmark in deletedBookmarks:
            bookmarkID = bookmark.bookmarkID
            try:
                del self.bookmarkCache[bookmarkID]
            except KeyError:
                self.LogError('Failed to delete bookmark locally', bookmarkID)
                sys.exc_clear()

            deletedBookmarkIDs.append(bookmarkID)

        return deletedBookmarkIDs

    def DeletePersonalBookmarks(self, bookmarkIDs):
        self.bookmarkMgr.DeleteBookmarks(bookmarkIDs)
        for bookmarkID in bookmarkIDs:
            try:
                del self.bookmarkCache[bookmarkID]
            except KeyError:
                self.LogError('Failed to delete bookmark locally', bookmarkID)
                sys.exc_clear()

        return bookmarkIDs

    def ZipMemo(self, *parts):
        return uiutil.Zip(*parts)

    def UnzipMemo(self, s):
        split = uiutil.Unzip(s)
        if len(split) == 1:
            return (split[0], '')
        return split[:2]

    def GetFoldersForOwner(self, ownerID):
        folders = set()
        for folder in self.folders.itervalues():
            if folder.ownerID == ownerID:
                folders.add(folder)

        return folders

    def DeleteFolder(self, folderID):
        folder = self.folders[folderID]
        deleteFolder = True
        if folder.ownerID == session.charid:
            bookmarks = self.bookmarkMgr.DeleteFolder(folderID)
        else:
            bookmarkIDs = set()
            isModerator = util.IsBookmarkModerator(session.corprole)
            for bookmarkID, bookmark in self.bookmarkCache.iteritems():
                if bookmark.folderID != folderID:
                    continue
                if not isModerator and getattr(bookmark, 'creatorID', None) != session.charid:
                    raise UserError('CantDeleteCorpBookmarksNotDirector')
                bookmarkIDs.add(bookmarkID)

            deleteFolder, bookmarks = self.corpBookmarkMgr.DeleteFolder(folderID, bookmarkIDs)
        if deleteFolder:
            try:
                del self.folders[folderID]
            except KeyError:
                log.LogTraceback('DeleteFolder - Failed to del folder')
                sys.exc_clear()

        else:
            uthread.new(eve.Message, 'BookmarkFolderNotDeleted')
        for bookmark in bookmarks:
            try:
                del self.bookmarkCache[bookmark.bookmarkID]
            except KeyError:
                self.LogInfo('DeleteFolder - bookmark not there', bookmark.bookmarkID)
                sys.exc_clear()

        self.RefreshWindow()

    def GetFolder(self, folderID):
        return self.folders.get(folderID)

    def HandleBookmarksDeleted(self, bookmarkIDs):
        for bookmarkID in bookmarkIDs:
            try:
                del self.bookmarkCache[bookmarkID]
            except KeyError:
                self.LogWarn('HandleBookmarksDeleted - Did not find bookmark', bookmarkID)
                sys.exc_clear()

        self.RefreshWindow()