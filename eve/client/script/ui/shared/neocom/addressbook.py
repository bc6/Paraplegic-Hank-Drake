import sys
import service
import blue
import uthread
import uix
import uiutil
import xtriui
import form
import util
import listentry
import types
import uiconst
import math
import uicls
import state
import log

class AddressBookSvc(service.Service):
    __exportedcalls__ = {'Show': [],
     'AddToPersonal': [],
     'AddToPersonalMulti': [],
     'DeleteEntryMulti': [],
     'GetMapBookmarks': [],
     'GetBookmarks': [],
     'GetSolConReg': [],
     'CreateBookmarkItem': [],
     'BookmarkCurrentLocation': [],
     'BookmarkLocationPopup': [],
     'ZipMemo': [],
     'UnzipMemo': [],
     'OnBookmarkAdd': [],
     'DeleteBookmarks': [],
     'RefreshWindow': [],
     'IsInAddressBook': [],
     'GetAddressBook': [],
     'IsBlocked': [],
     'GetRelationship': [],
     'GetContactsByMinRelationship': [],
     'AssignLabelFromWnd': [],
     'RemoveLabelFromWnd': []}
    __guid__ = 'svc.addressbook'
    __update_on_reload__ = 0
    __notifyevents__ = ['ProcessSessionChange',
     'OnDestinationSet',
     'OnSessionChanged',
     'OnContactNoLongerContact',
     'OnOrganizationContactsUpdated',
     'OnContactSlashCommand',
     'OnBookmarkAdded',
     'OnBookmarkDeleted',
     'OnAgentAdded']
    __servicename__ = 'addressbook'
    __displayname__ = 'AddressBook Client Service'
    __dependencies__ = []
    __startupdependencies__ = ['settings']

    def __init__(self):
        service.Service.__init__(self)
        self.semaphore = uthread.Semaphore(('addressbook', 0))
        self.agents = None
        self.blocked = None
        self.labels = None
        self.corporateLabels = None
        self.allianceLabels = None
        self.contactType = None
        self.contacts = None
        self.corporateContacts = None
        self.allianceContacts = None



    def Run(self, memStream = None):
        self.LogInfo('Starting AddressBook')
        self.Reset()
        if eve.session.charid:
            self.GetContacts()



    def CloseWindow(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.SelfDestruct()



    def OnSessionChanged(self, isremote, session, change):
        if 'charid' in change and session.charid:
            self.GetContacts()
            self.RefreshWindow()



    def ProcessSessionChange(self, isremote, session, change):
        if session.charid is None:
            self.CloseWindow()
            self.Reset()
        elif 'solarsystemid' in change:
            self.RefreshWindow()



    def OnContactSlashCommand(self, contactID, level):
        if level is None:
            try:
                self.contacts.pop(contactID)
            except:
                sys.exc_clear()
        elif contactID not in self.contacts:
            contact = util.KeyVal()
            contact.contactID = contactID
            contact.relationshipID = level
            contact.labelMask = 0
            contact.inWatchlist = 0
            self.contacts[contactID] = contact
        else:
            self.contacts[contactID].relationshipID = level
        sm.ScatterEvent('OnContactChange', [contactID], 'contact')



    def OnOrganizationContactsUpdated(self, ownerID, updates):
        if self.contacts is None:
            self.GetContacts()
        if ownerID == session.corpid:
            contacts = self.corporateContacts
            event = 'OnSetCorpStanding'
        elif ownerID == session.allianceid:
            contacts = self.allianceContacts
            event = 'OnSetAllianceStanding'
        else:
            self.LogError('Invalid ownerID in contact update notification', ownerID, updates)
            return 
        for update in updates:
            (contactID, level, labelMask,) = update
            if level is None and labelMask is None:
                try:
                    contacts.pop(contactID)
                except:
                    sys.exc_clear()
            elif contactID not in contacts:
                labelMask = labelMask or 0
                contact = util.KeyVal()
                contact.contactID = contactID
                contact.relationshipID = level
                contact.inWatchlist = 0
                contact.labelMask = labelMask
                contacts[contactID] = contact
            elif labelMask is None:
                contacts[contactID].relationshipID = level
            else:
                contacts[contactID].labelMask = labelMask

        sm.ScatterEvent(event)



    def GetContacts(self):
        uthread.Lock(self, 'contacts')
        try:
            if self.contacts is not None and self.blocked is not None and self.corporateContacts is not None and self.allianceContacts is not None and self.agents is not None and self.bms is not None:
                return util.KeyVal(contacts=self.contacts, blocked=self.blocked, corpContacts=self.corporateContacts, allianceContacts=self.allianceContacts)
            else:
                self.contacts = {}
                self.blocked = {}
                self.corporateContacts = {}
                self.allianceContacts = {}
                self.bms = {}
                self.agents = []
                tmpBlocked = []
                bookmarks = sm.RemoteSvc('bookmark').GetBookmarks()
                if session.allianceid:
                    (addressbook, self.corporateContacts, self.allianceContacts, statuses,) = uthread.parallel([(sm.RemoteSvc('charMgr').GetContactList, ()),
                     (sm.GetService('corp').GetContactList, ()),
                     (sm.GetService('alliance').GetContactList, ()),
                     (sm.GetService('onlineStatus').Prime, ())])
                else:
                    (addressbook, self.corporateContacts, statuses,) = uthread.parallel([(sm.RemoteSvc('charMgr').GetContactList, ()), (sm.GetService('corp').GetContactList, ()), (sm.GetService('onlineStatus').Prime, ())])
                for each in addressbook.addresses:
                    if util.IsNPC(each.contactID) and sm.GetService('agents').IsAgent(each.contactID):
                        self.agents.append(each.contactID)
                    else:
                        contact = util.KeyVal()
                        contact.contactID = each.contactID
                        contact.inWatchlist = each.inWatchlist
                        contact.relationshipID = each.relationshipID
                        contact.labelMask = each.labelMask
                        self.contacts[each.contactID] = contact

                for each in addressbook.blocked:
                    blocked = util.KeyVal()
                    blocked.contactID = each.senderID
                    self.blocked[each.senderID] = blocked

                for each in bookmarks:
                    if each.bookmarkID in self.deleted:
                        continue
                    self.bms[each.bookmarkID] = each

                cfg.eveowners.Prime(self.blocked.keys())
                cfg.eveowners.Prime(self.contacts.keys())
                cfg.eveowners.Prime(self.corporateContacts)
                cfg.eveowners.Prime(self.allianceContacts)
                cfg.eveowners.Prime(self.agents)
                return util.KeyVal(contacts=self.contacts, blocked=self.blocked, corpContacts=self.corporateContacts, allianceContacts=self.allianceContacts)

        finally:
            uthread.UnLock(self, 'contacts')




    def GetRelationship(self, charID, corporationID, allianceID = None):
        relationships = util.KeyVal()
        relationships.persToPers = const.contactNeutralStanding
        relationships.persToCorp = const.contactNeutralStanding
        relationships.persToAlliance = const.contactNeutralStanding
        relationships.corpToPers = const.contactNeutralStanding
        relationships.corpToCorp = const.contactNeutralStanding
        relationships.corpToAlliance = const.contactNeutralStanding
        relationships.allianceToPers = const.contactNeutralStanding
        relationships.allianceToCorp = const.contactNeutralStanding
        relationships.allianceToAlliance = const.contactNeutralStanding
        relationships.hasRelationship = False
        if charID in self.contacts:
            relationships.persToPers = self.contacts[charID].relationshipID
            relationships.hasRelationship = True
        if corporationID in self.contacts:
            relationships.persToCorp = self.contacts[corporationID].relationshipID
            relationships.hasRelationship = True
        if allianceID is not None and allianceID in self.contacts:
            relationships.persToAlliance = self.contacts[allianceID].relationshipID
            relationships.hasRelationship = True
        if charID in self.corporateContacts:
            relationships.corpToPers = self.corporateContacts[charID].relationshipID
            relationships.hasRelationship = True
        if corporationID in self.corporateContacts:
            relationships.corpToCorp = self.corporateContacts[corporationID].relationshipID
            relationships.hasRelationship = True
        if allianceID in self.corporateContacts:
            relationships.corpToAlliance = self.corporateContacts[allianceID].relationshipID
            relationships.hasRelationship = True
        if charID in self.allianceContacts:
            relationships.allianceToPers = self.allianceContacts[charID].relationshipID
            relationships.hasRelationship = True
        if corporationID in self.allianceContacts:
            relationships.allianceToCorp = self.allianceContacts[corporationID].relationshipID
            relationships.hasRelationship = True
        if allianceID is not None and allianceID in self.allianceContacts:
            relationships.allianceToAlliance = self.allianceContacts[allianceID].relationshipID
            relationships.hasRelationship = True
        return relationships



    def GetContactsByMinRelationship(self, relationshipID):
        contacts = set()
        for (contactID, contact,) in self.contacts.iteritems():
            if contact.relationshipID >= relationshipID:
                contacts.add(contactID)

        for (contactID, contact,) in self.corporateContacts.iteritems():
            if contact.relationshipID >= relationshipID:
                contacts.add(contactID)

        for (contactID, contact,) in self.allianceContacts.iteritems():
            if contact.relationshipID >= relationshipID:
                contacts.add(contactID)

        return contacts



    def OnDestinationSet(self, destinationID):
        self.RefreshWindow()



    def OnContactNoLongerContact(self, charID):
        pass



    def OnBookmarkAdded(self, bookmark):
        if bookmark.bookmarkID in self.bms:
            return 
        self.bms[bookmark.bookmarkID] = bookmark
        sm.GetService('neocom').Blink('addressbook')
        self.RefreshWindow()



    def OnBookmarkDeleted(self, bookmarkID):
        try:
            del self.bms[bookmarkID]
            sm.GetService('neocom').Blink('addressbook')
            self.RefreshWindow()
        except KeyError:
            pass



    def OnBookmarkAdd(self, bookmark, refresh = 1):
        if bookmark.bookmarkID in self.bms:
            return 
        self.bms[bookmark.bookmarkID] = bookmark
        if refresh:
            self.RefreshWindow()



    def GetMapBookmarks(self, suppressAgentBookmarks = 0):
        valid = [const.categoryCelestial,
         const.categoryAsteroid,
         const.categoryStation,
         const.categoryShip,
         const.categorySovereigntyStructure,
         const.categoryPlanetaryInteraction]
        ret = [ each for each in self.bms.itervalues() if cfg.invtypes.Get(each.typeID).Group().Category().id in valid ]
        if not suppressAgentBookmarks:
            agentMenu = sm.GetService('journal').GetMyAgentJournalBookmarks()
            if agentMenu:
                for (missionName, bms, agentID,) in agentMenu:
                    missionName = missionName + '%s' % agentID
                    for bm in bms:
                        c = util.KeyVal()
                        for each in bm.__dict__.iterkeys():
                            if each not in c.__dict__:
                                c.__dict__[each] = bm.__dict__[each]

                        c.missionName = missionName
                        c.hint = bm.hint
                        c.memo = c.hint + '\t'
                        c.bookmarkID = ('agentmissions',
                         c.agentID,
                         c.locationType,
                         c.locationNumber)
                        ret.append(c)


        return ret



    def __CelestialMenu(self, *args):
        return sm.GetService('menu').CelestialMenu(*args)



    def GetBookmarks(self, *args):
        return self.bms



    def BookmarkCurrentLocation(self, *args):
        wnd = self.GetWnd()
        text = mls.UI_CMD_ADDBOOKMARK
        btn = wnd.sr.bookmarkbtns.GetBtnByLabel(text)
        btn.Disable()
        try:
            if not (session.stationid or session.shipid):
                eve.Message('HavetobeatstationOrinShip')
                return 
            if session.stationid:
                stationinfo = sm.RemoteSvc('stationSvc').GetStation(session.stationid)
                self.BookmarkLocationPopup(session.stationid, stationinfo.stationTypeID, session.solarsystemid2)
            elif session.solarsystemid and session.shipid:
                bp = sm.GetService('michelle').GetBallpark()
                if bp is None:
                    return 
                slimItem = bp.GetInvItem(session.shipid)
                if slimItem is None:
                    return 
                self.BookmarkLocationPopup(session.shipid, slimItem.typeID, session.solarsystemid)

        finally:
            if wnd:
                text = mls.UI_CMD_ADDBOOKMARK
                btn = wnd.sr.bookmarkbtns.GetBtnByLabel(text)
                btn.Enable()




    def CheckLocationID(self, locationid):
        bms = self.GetMapBookmarks()
        for bookmark in bms:
            if bookmark.itemID == locationid:
                return self.UnzipMemo(bookmark.memo)[0]




    def CreateBookmarkItem(self, bookmarkID):
        if bookmarkID in self.bms:
            bookmark = self.bms[bookmarkID]
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            bookmarkitem = sm.GetService('sessionMgr').PerformSessionLockedOperation('bookmarking', sm.RemoteSvc('bookmark').CreateBookmarkVoucher, bookmarkID, bookmark.memo[:100], violateSafetyTimer=True)
            if not shift and bookmarkitem is not None:
                self.DeleteBookmarks([bookmarkID])
            return bookmarkitem



    def CreateBookmarkItems(self, bookmarkIDs):
        bookmarkIDs = bookmarkIDs[:5]
        params = []
        for bookmarkID in bookmarkIDs:
            if bookmarkID in self.bms:
                params.append((bookmarkID, self.bms[bookmarkID].memo[:100]))
            else:
                params.append((bookmarkID,))

        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        ret = sm.GetService('sessionMgr').PerformSessionLockedOperation('bookmarking', sm.RemoteSvc('bookmark').CreateBookmarkVouchers, params, violateSafetyTimer=True)
        if not shift and ret:
            self.DeleteBookmarks(bookmarkIDs)
        return ret



    def BookmarkLocationPopup(self, locationid, typeID, parentID, note = None, *args):
        cord = None
        scanResultID = None
        if locationid in (session.solarsystemid, session.shipid):
            if len(args) == 1 and isinstance(args[0], util.KeyVal):
                info = args[0]
                cord = info.position
                locationname = info.name
                scanResultID = info.id
            else:
                bp = sm.GetService('michelle').GetBallpark()
                if bp:
                    ownBall = bp.GetBall(session.shipid)
                    cord = (ownBall.x, ownBall.y, ownBall.z)
                locationname = mls.UI_SHARED_SPOTINSOLARSYSTEM % {'name': cfg.evelocations.Get(session.solarsystemid2).name}
        else:
            mapSvc = sm.GetService('map')
            locationname = cfg.evelocations.Get(locationid).name
            locationObj = mapSvc.GetItem(locationid)
            if locationObj:
                locationname = '%s ( %s )' % (locationname, cfg.invgroups.Get(locationObj.typeID).name)
            bp = sm.GetService('michelle').GetBallpark()
            if bp:
                slimItem = uix.GetBallparkRecord(locationid)
                if slimItem is not None:
                    if locationname is None or len(locationname) == 1:
                        locationname = cfg.invtypes.Get(slimItem.typeID).Group().name
                    else:
                        locationname = '%s ( %s )' % (locationname, cfg.invtypes.Get(slimItem.typeID).Group().name)
        checkavail = self.CheckLocationID(locationid)
        if checkavail and cord is None:
            if eve.Message('AskProceedBookmarking', {'locationname': locationname,
             'caption': checkavail}, uiconst.YESNO) != uiconst.ID_YES:
                return 
        format = [{'type': 'btline'},
         {'type': 'push',
          'frame': 1},
         {'type': 'edit',
          'setvalue': locationname,
          'label': mls.UI_GENERIC_LABEL,
          'key': 'caption',
          'required': 1,
          'frame': 1,
          'maxlength': 99},
         {'type': 'textedit',
          'label': mls.UI_GENERIC_NOTES,
          'setvalue': note,
          'key': 'note',
          'required': 0,
          'frame': 1,
          'maxlength': 6000}]
        if cord is not None:
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'labeltext',
             'frame': 1,
             'label': mls.UI_GENERIC_POSITION,
             'text': 'X: %s' % cord[0]})
            format.append({'type': 'labeltext',
             'frame': 1,
             'label': '',
             'text': 'Y: %s' % cord[1]})
            format.append({'type': 'labeltext',
             'frame': 1,
             'label': '',
             'text': 'Z: %s' % cord[2]})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'bbline'})
        format.append({'type': 'push'})
        retval = uix.HybridWnd(format, mls.UI_SHARED_NEWBOOKMARK, 1, buttons=uiconst.OKCANCEL, minW=340, minH=256, icon='ui_9_64_1')
        if retval:
            if scanResultID:
                self.BookmarkScanResult(locationid, retval['caption'][:100], retval['note'][:6000], scanResultID)
            else:
                self.BookmarkLocation(locationid, retval['caption'][:100], retval['note'][:6000], typeID, parentID)



    def UpdateBookmark(self, bookmarkID, header = None, note = None):
        if bookmarkID not in self.bms:
            return 
        bm = self.bms[bookmarkID]
        (oldheader, oldnote,) = self.UnzipMemo(bm.memo)
        oldnote = bm.note
        if header is None:
            header = oldheader
        if note is None:
            note = oldnote
        if note == oldnote and header == oldheader:
            return 
        memo = self.ZipMemo(header[:100], '')
        if bm.memo != memo or note != oldnote:
            uthread.pool('AddressBook::CallingRemote on UpdateBookmark', sm.RemoteSvc('bookmark').UpdateBookmark, bookmarkID, memo, note)
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.ShowLoad()
        try:
            self.bms[bookmarkID].memo = memo
            self.bms[bookmarkID].note = note
            listGroupID = uicore.registry.GetGroupIDFromItemID('places2_%s' % session.charid, bookmarkID)
            if listGroupID:
                wnd = sm.GetService('window').GetWindow(str(listGroupID))
                if wnd:
                    wnd.LoadContent()
            self.RefreshWindow()

        finally:
            if wnd is not None and not wnd.destroyed:
                wnd.HideLoad()




    def BookmarkLocation(self, itemID, name, comment, typeID, locationID = None):
        memo = self.ZipMemo(name[:100], '')
        (bookmarkID, itemID, typeID, x, y, z, locationID,) = sm.RemoteSvc('bookmark').BookmarkLocation(itemID, memo, comment)
        if bookmarkID:
            bm = util.KeyVal()
            bm.bookmarkID = bookmarkID
            bm.ownerID = session.charid
            bm.itemID = itemID
            bm.typeID = typeID
            bm.flag = None
            bm.memo = memo
            bm.created = blue.os.GetTime(1)
            bm.x = x
            bm.y = y
            bm.z = z
            bm.locationID = locationID
            bm.note = comment
            self.bms[bookmarkID] = bm
            self.RefreshWindow()
            sm.ScatterEvent('OnBookmarkCreated', bookmarkID, comment)



    def BookmarkScanResult(self, locationID, name, comment, resultID):
        memo = self.ZipMemo(name[:100], '')
        (bookmarkID, itemID, typeID, x, y, z, locationID,) = sm.RemoteSvc('bookmark').BookmarkScanResult(locationID, memo, comment, resultID)
        if bookmarkID:
            bm = util.KeyVal()
            bm.bookmarkID = bookmarkID
            bm.ownerID = session.charid
            bm.itemID = None
            bm.typeID = typeID
            bm.flag = None
            bm.memo = memo
            bm.created = blue.os.GetTime(1)
            bm.x = x
            bm.y = y
            bm.z = z
            bm.locationID = locationID
            bm.note = comment
            self.bms[bookmarkID] = bm
            self.RefreshWindow()
            sm.ScatterEvent('OnBookmarkCreated', bookmarkID, comment)



    def DeleteBookmarks(self, ids, refreshWindow = 1, alreadyDeleted = 0):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.ShowLoad()
        try:
            filteredIDs = []
            for id in ids:
                if id not in filteredIDs and id not in self.deleted:
                    filteredIDs.append(id)
                if self.bms is not None and id in self.bms:
                    del self.bms[id]

            self.deleted += filteredIDs
            if not alreadyDeleted:
                sm.RemoteSvc('bookmark').DeleteBookmarks(filteredIDs)
            sm.ScatterEvent('OnBookmarksDeleted', filteredIDs)
            if refreshWindow:
                self.RefreshWindow()

        finally:
            if wnd is not None and not wnd.destroyed:
                wnd.HideLoad()




    def EditBookmark(self, bm):
        (oldlabel, oldnotes,) = self.UnzipMemo(bm.memo)
        if not hasattr(bm, 'note'):
            return 
        oldnotes = bm.note
        format = [{'type': 'btline'},
         {'type': 'push',
          'frame': 1},
         {'type': 'edit',
          'setvalue': oldlabel,
          'label': mls.UI_GENERIC_LABEL,
          'key': 'label',
          'frame': 1,
          'required': 1,
          'maxlength': 99},
         {'type': 'textedit',
          'setvalue': oldnotes,
          'label': '_hide',
          'key': 'notes',
          'frame': 1,
          'height': 80,
          'maxlength': 6000},
         {'type': 'push',
          'frame': 1},
         {'type': 'btline'}]
        retval = uix.HybridWnd(format, mls.UI_SHARED_EDITLOCATION, 1, buttons=uiconst.OKCANCEL, minW=340, minH=256, icon='ui_9_64_1')
        if retval:
            (label, notes,) = (retval['label'], retval['notes'])
            self.UpdateBookmark(bm.bookmarkID, label, notes)



    def Reset(self):
        self.destinationSetOnce = 0
        self.deleted = []



    def Show(self):
        wnd = self.GetWnd(1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()



    def RefreshWindow(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed and wnd.inited:
            if getattr(wnd.sr, 'maintabs', None) is not None:
                wnd.sr.maintabs.ReloadVisible()



    def OnDropData(self, dragObj, nodes):
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed or not wnd.inited:
            return 
        wnd.ShowLoad()
        try:
            visibletab = wnd.sr.maintabs.GetVisible(1)
            if visibletab and hasattr(visibletab, 'OnTabDropData'):
                visibletab.OnTabDropData(dragObj, nodes)

        finally:
            if wnd is not None and not wnd.destroyed and wnd.inited:
                wnd.HideLoad()




    def DropInAgents(self, dragObj, nodes):
        self.DropInPersonal(nodes, None)



    def DropInPersonalContact(self, dragObj, nodes):
        self.DropInPersonal(nodes, 'contact')



    def DropInPersonal(self, nodes, contactType):
        for what in nodes:
            if getattr(what, '__guid__', None) not in ('listentry.User', 'listentry.Sender', 'listentry.ChatUser', 'listentry.SearchedUser'):
                return 
            if sm.GetService('agents').IsAgent(what.itemID) and contactType != None:
                eve.Message('CannotAddContactType')
                continue
            elif not sm.GetService('agents').IsAgent(what.itemID) and contactType == None:
                eve.Message('CannotAddContactType2')
                continue
            else:
                self.AddToAddressBook(what.itemID, contactType)




    def DropInBlocked(self, nodes):
        for what in nodes:
            if getattr(what, '__guid__', None) not in ('listentry.User', 'listentry.Sender', 'listentry.ChatUser', 'listentry.SearchedUser'):
                return 
            if not util.IsOwner(what.itemID) and not util.IsAlliance(what.itemID):
                self.LogWarn('Skipping block item', what.itemID, 'as this item is not a character!')
                continue
            self.BlockOwner(what.itemID)




    def DropInPlaces(self, dragObj, nodes):
        for what in nodes:
            if getattr(what, '__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem') and what.rec.typeID == const.typeBookmark and what.rec.ownerID == session.charid:
                wnd = self.GetWnd()
                if wnd is not None and not wnd.destroyed and wnd.inited:
                    wnd.ShowLoad()
                try:
                    bookmark = sm.GetService('sessionMgr').PerformSessionLockedOperation('bookmarking', sm.RemoteSvc('bookmark').AddBookmarkFromVoucher, what.rec.itemID, violateSafetyTimer=True)
                    if bookmark:
                        self.OnBookmarkAdd(bookmark, True)

                finally:
                    if wnd is not None and not wnd.destroyed and wnd.inited:
                        wnd.HideLoad()

            elif getattr(what, '__guid__', None) == 'listentry.PlaceEntry':
                listgroupID = what.listGroupID
                whatID = what.bm.bookmarkID
                if whatID and listgroupID:
                    uicore.registry.RemoveFromListGroup(listgroupID, whatID)
                    uicore.registry.ReloadGroupWindow(listgroupID)

        self.RefreshWindow()



    def Load(self, args):
        uthread.Lock(self, 'load')
        try:
            wnd = self.GetWnd()
            if not wnd or wnd.destroyed:
                return 
            wnd.sr.bookmarkbtns.state = uiconst.UI_HIDDEN
            wnd.sr.agentbtns.state = uiconst.UI_HIDDEN
            wnd.sr.scroll.sr.iconMargin = 0
            wnd.sr.scroll.sr.id = '%sAddressBookScroll' % args
            wnd.sr.scroll.sr.fixedColumns = [{'name': 64}, {}][(args == 'places')]
            wnd.sr.scroll.sr.ignoreTabTrimming = not args == 'places'
            if args == 'agents':
                self.ShowAgents()
            elif args == 'places':
                self.ShowPlaces()
            elif args == 'contact':
                self.ShowContacts('contact')
            elif args == 'corpcontact':
                self.ShowContacts('corpcontact')
            elif args == 'alliancecontact':
                self.ShowContacts('alliancecontact')
            self.lastTab = args

        finally:
            uthread.UnLock(self, 'load')




    def AddGroup(self, listID, *args):
        uicore.registry.AddListGroup(listID)
        self.RefreshWindow()



    def GetWnd(self, new = 0):
        wnd = sm.GetService('window').GetWindow('addressbook')
        if not wnd and new:
            uicore.registry.GetLockedGroup('agentgroups', 'all', mls.UI_SHARED_ALLAGENTS)
            wnd = sm.GetService('window').GetWindow('addressbook', create=1, decoClass=form.AddressBook)
            wnd.inited = 0
            wnd.SetCaption(mls.UI_SHARED_PEOPLEANDPLACES)
            wnd.SetTopparentHeight(52)
            wnd.OnClose_ = self.OnCloseWnd
            wnd.OnDropData = self.OnDropData
            wnd.SetWndIcon('ui_12_64_2', mainTop=-12)
            wnd.SetScope('station_inflight')
            wnd.sr.main = uiutil.GetChild(wnd, 'main')
            wnd.sr.scroll = uicls.Scroll(parent=wnd.sr.main, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            wnd.sr.contacts = form.ContactsForm(name='contactsform', parent=wnd.sr.main, pos=(0, 0, 0, 0))
            wnd.sr.bookmarkbtns = uicls.ButtonGroup(btns=[[mls.UI_CMD_ADDBOOKMARK,
              self.BookmarkCurrentLocation,
              (),
              81], [mls.UI_CMD_CREATEFOLDER,
              self.AddGroup,
              'places2_%s' % session.charid,
              81]], parent=wnd.sr.main, idx=0)
            wnd.sr.agentbtns = uicls.ButtonGroup(btns=[[mls.UI_CMD_CREATEFOLDER,
              self.AddGroup,
              'agentgroups',
              81], [mls.UI_SHARED_AGENTFINDER,
              uicore.cmd.OpenAgentFinder,
              'agentgroups',
              81]], parent=wnd.sr.main, idx=0)
            wnd.sr.hint = None
            grplst = [[mls.UI_GENERIC_CHARACTER, (const.groupCharacter, 0)],
             [mls.UI_GENERIC_CHARACTEREXACT, (const.groupCharacter, 1)],
             [mls.UI_GENERIC_ALLIANCE, (const.groupAlliance, 0)],
             [mls.UI_CORP_ALLIANCESHORTNAME, (const.groupAlliance, -1)],
             [mls.UI_GENERIC_CORPORATION, (const.groupCorporation, 0)],
             [mls.UI_CORP_CORPTICKER, (const.groupCorporation, -1)],
             [mls.UI_GENERIC_FACTION, (const.groupFaction, 0)],
             [mls.UI_GENERIC_STATION, (const.groupStation, 0)],
             [mls.UI_GENERIC_ASTEROIDBELT, (const.groupAsteroidBelt, 0)],
             [mls.UI_GENERIC_SOLARSYSTEM, (const.groupSolarSystem, 0)],
             [mls.UI_GENERIC_CONSTELLATION, (const.groupConstellation, 0)],
             [mls.UI_GENERIC_REGION, (const.groupRegion, 0)]]
            grplst.sort(lambda x, y: cmp(x[0], y[0]))
            wnd.sr.sgroup = group = uicls.Combo(label=mls.UI_SHARED_SEARCHTYPE, parent=wnd.sr.topParent, options=grplst, name='addressBookComboSearchType', select=settings.user.ui.Get('searchgroup', const.groupCharacter), width=86, left=74, top=20, callback=self.ChangeSearchGroup)
            wnd.sr.inpt = inpt = uicls.SinglelineEdit(name='search', parent=wnd.sr.topParent, maxLength=37, left=group.left + group.width + 6, top=group.top, width=86, label=mls.UI_SHARED_SEARCHSTRING)
            btn = uicls.Button(parent=wnd.sr.topParent, label=mls.UI_CMD_SEARCH, pos=(inpt.left + inpt.width + 2,
             inpt.top,
             0,
             0), func=self.Search, btn_default=1)
            wnd.sr.scroll.sr.content.OnDropData = self.OnDropData
            idx = settings.user.tabgroups.Get('addressbookpanel', None)
            if idx is None:
                settings.user.tabgroups.Set('addressbookpanel', 4)
            tabs = [[mls.UI_CONTACTS_CONTACTS,
              wnd.sr.contacts,
              self,
              'contact',
              None], [mls.UI_GENERIC_AGENTS,
              wnd.sr.scroll,
              self,
              'agents',
              None], [mls.UI_GENERIC_PLACES,
              wnd.sr.scroll,
              self,
              'places',
              None]]
            maintabs = uicls.TabGroup(name='tabparent', align=uiconst.TOTOP, height=18, parent=wnd.sr.main, idx=0, tabs=tabs, groupID='addressbookpanel', autoselecttab=True)
            maintabs.sr.Get('%s_tab' % mls.UI_GENERIC_AGENTS, None).OnTabDropData = self.DropInAgents
            maintabs.sr.Get('%s_tab' % mls.UI_GENERIC_PLACES, None).OnTabDropData = self.DropInPlaces
            maintabs.sr.Get('%s_tab' % mls.UI_CONTACTS_CONTACTS, None).OnTabDropData = self.DropInPersonalContact
            wnd.sr.maintabs = maintabs
            wnd.inited = 1
        return wnd



    def ChangeSearchGroup(self, entry, header, value, *args):
        settings.user.ui.Set('searchgroup', value)



    def CheckBoxChange(self, checkbox):
        config = checkbox.data['config']
        if checkbox.data.has_key('value'):
            if checkbox.checked:
                settings.user.ui.Set(config, checkbox.data['value'])
            else:
                settings.user.ui.Set(config, checkbox.checked)
        self.RefreshWindow()



    def OnCloseWnd(self, wnd, *args):
        uicore.registry.GetLockedGroup('agentgroups', 'all', mls.UI_SHARED_ALLAGENTS)



    def Search(self, *args):
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            (groupID, flag,) = wnd.sr.sgroup.GetValue()
            ret = uix.Search(wnd.sr.inpt.GetValue().strip(), groupID, modal=0, exact=flag, searchWndName='addressBookSearch')



    def OnAgentAdded(self, entityID):
        if entityID in self.agents:
            return 
        self.agents.append(entityID)
        sm.GetService('neocom').Blink('addressbook')
        self.RefreshWindow()



    def AddToPersonalMulti(self, charIDs, contactType = None, edit = 0):
        if type(charIDs) != list:
            charIDs = [charIDs]
        for charID in charIDs:
            self.AddToPersonal(charID, contactType=contactType, refresh=charID == charIDs[-1], edit=edit)




    def AddToPersonal(self, charID, contactType, refresh = 1, edit = 0):
        if charID == const.ownerSystem:
            eve.Message('CantbookmarkEveSystem')
            return 
        if contactType is None:
            if charID not in self.agents:
                try:
                    character = cfg.eveowners.Get(charID)
                except:
                    log.LogWarn('User trying to bookmark character which is not in the owners table', charID)
                    sys.exc_clear()
                    return 
                self.AddToAddressBook(charID, contactType, edit)
        else:
            self.AddToAddressBook(charID, contactType, edit)



    def BlockOwner(self, ownerID):
        if ownerID == session.charid:
            eve.Message('CustomInfo', {'info': mls.UI_SHARED_CHANNELHINT6})
            return 
        if util.IsNPC(ownerID):
            if util.IsCharacter(ownerID):
                eve.Message('CustomInfo', {'info': mls.UI_SHARED_CHANNELHINT7})
            elif util.IsCorporation(ownerID) or util.IsAlliance(ownerID):
                eve.Message('CustomInfo', {'info': mls.UI_SHARED_CHANNELHINT20})
            return 
        if ownerID in self.blocked:
            eve.Message('CustomInfo', {'info': mls.UI_SHARED_CHANNELHINT8 % {'name': cfg.eveowners.Get(ownerID).name}})
            return 
        sm.RemoteSvc('charMgr').BlockOwners([ownerID])
        blocked = util.KeyVal()
        blocked.contactID = ownerID
        self.blocked[ownerID] = blocked
        sm.ScatterEvent('OnBlockContacts', [ownerID])
        self.RefreshWindow()



    def UnblockOwner(self, ownerIDs):
        blocked = []
        for ownerID in ownerIDs:
            if ownerID in self.blocked:
                blocked.append(ownerID)
                self.blocked.pop(ownerID)

        if len(blocked):
            sm.RemoteSvc('charMgr').UnblockOwners(blocked)
            sm.ScatterEvent('OnUnblockContacts', blocked)
        self.RefreshWindow()
        wnd = self.GetWnd()



    def IsBlocked(self, ownerID):
        return ownerID in self.blocked



    def EditContacts(self, contactIDs, contactType):
        wnd = sm.GetService('window').GetWindow('contactmanagement', decoClass=form.ContactManagementMultiEditWnd, create=1, entityIDs=contactIDs, contactType=contactType)
        if wnd.ShowModal() == 1:
            results = wnd.result
            relationshipID = results
            if contactType == 'contact':
                sm.RemoteSvc('charMgr').EditContactsRelationshipID(contactIDs, relationshipID)
                for contactID in contactIDs:
                    self.contacts[contactID].relationshipID = relationshipID

            elif contactType == 'corpcontact':
                sm.GetService('corp').EditContactsRelationshipID(contactIDs, relationshipID)
                for contactID in contactIDs:
                    self.corporateContacts[contactID].relationshipID = relationshipID

            elif contactType == 'alliancecontact':
                sm.GetService('alliance').EditContactsRelationshipID(contactIDs, relationshipID)
                for contactID in contactIDs:
                    self.allianceContacts[contactID].relationshipID = relationshipID

            sm.ScatterEvent('OnContactChange', [contactIDs], contactType)



    def AddToAddressBook(self, contactID, contactType, edit = 0):
        if contactID == session.charid and contactType == 'contact':
            eve.Message('CustomInfo', {'info': mls.UI_SHARED_CHANNELHINT9})
            return 
        if util.IsNPC(contactID) and not sm.GetService('agents').IsAgent(contactID) and util.IsCharacter(contactID):
            eve.Message('CustomInfo', {'info': mls.UI_SHARED_CHANNELHINT21 % {'name': cfg.eveowners.Get(contactID).name}})
            return 
        if contactType is None and contactID in self.agents:
            eve.Message('CustomInfo', {'info': mls.UI_SHARED_CHANNELHINT10 % {'name': cfg.eveowners.Get(contactID).name,
                      'contactType': mls.UI_CONTACTS_CONTACT}})
            return 
        if contactType == 'contact':
            if contactID in self.contacts and not edit:
                eve.Message('CustomInfo', {'info': mls.UI_SHARED_CHANNELHINT10 % {'name': cfg.eveowners.Get(contactID).name,
                          'contactType': mls.UI_CONTACTS_CONTACT}})
                return 
        if contactType == 'corpcontact':
            if contactID in self.corporateContacts and not edit:
                eve.Message('CustomInfo', {'info': mls.UI_SHARED_CHANNELHINT10 % {'name': cfg.eveowners.Get(contactID).name,
                          'contactType': mls.UI_CONTACTS_CORPCONTACT}})
                return 
        if contactType == 'alliancecontact':
            if contactID in self.allianceContacts and not edit:
                eve.Message('CustomInfo', {'info': mls.UI_SHARED_CHANNELHINT10 % {'name': cfg.eveowners.Get(contactID).name,
                          'contactType': mls.UI_CONTACTS_ALLIANCECONTACT}})
                return 
        inWatchlist = False
        relationshipID = None
        labelMask = 0
        message = None
        if util.IsNPC(contactID) and sm.GetService('agents').IsAgent(contactID):
            sm.RemoteSvc('charMgr').AddContact(contactID)
            self.agents.append(contactID)
            self.RefreshWindow()
        else:
            isContact = self.IsInAddressBook(contactID, contactType)
            if contactType == 'contact':
                windowType = form.ContactManagementWnd
                entityID = contactID
                relationshipID = relationshipID
                watchlist = inWatchlist
                isContact = isContact
            else:
                windowType = form.CorpAllianceContactManagementWnd
                entityID = contactID
                relationshipID = relationshipID
                watchlist = None
                isContact = isContact
            if isContact:
                if contactType == 'contact':
                    contact = self.contacts.get(contactID)
                    relationshipID = contact.relationshipID
                    inWatchlist = watchlist = contact.inWatchlist
                    labelMask = contact.labelMask
                    startupParams = (contactID,
                     relationshipID,
                     inWatchlist,
                     isContact)
                elif contactType == 'corpcontact':
                    contact = self.corporateContacts.get(contactID)
                    relationshipID = contact.relationshipID
                    labelMask = contact.labelMask
                    startupParams = (contactID, relationshipID, isContact)
                elif contactType == 'alliancecontact':
                    contact = self.allianceContacts.get(contactID)
                    relationshipID = contact.relationshipID
                    labelMask = contact.labelMask
                    startupParams = (contactID, relationshipID, isContact)
            wnd = sm.GetService('window').GetWindow('contactmanagement', decoClass=windowType, create=1, entityID=entityID, level=relationshipID, watchlist=watchlist, isContact=isContact)
            if wnd.ShowModal() == 1:
                results = wnd.result
                if contactType == 'contact':
                    relationshipID = results[0]
                    inWatchlist = results[1]
                    sendNotification = results[2]
                    message = results[3]
                else:
                    relationshipID = results
                contact = util.KeyVal()
                contact.contactID = contactID
                contact.relationshipID = relationshipID
                contact.inWatchlist = inWatchlist
                contact.labelMask = labelMask
                if contactType == 'contact':
                    if isContact and edit:
                        func = 'EditContact'
                    else:
                        func = 'AddContact'
                    util.CSPAChargedAction('CSPAContactNotifyCheck', sm.RemoteSvc('charMgr'), func, contactID, relationshipID, inWatchlist, sendNotification, message)
                    self.contacts[contactID] = contact
                elif contactType == 'corpcontact':
                    if isContact and edit:
                        sm.GetService('corp').EditCorporateContact(contactID, relationshipID=relationshipID)
                    else:
                        sm.GetService('corp').AddCorporateContact(contactID, relationshipID=relationshipID)
                    self.corporateContacts[contactID] = contact
                elif contactType == 'alliancecontact':
                    if isContact and edit:
                        sm.GetService('alliance').EditAllianceContact(contactID, relationshipID=relationshipID)
                    else:
                        sm.GetService('alliance').AddAllianceContact(contactID, relationshipID=relationshipID)
                    self.allianceContacts[contactID] = contact
                sm.ScatterEvent('OnContactChange', [contactID], contactType)
                if util.IsCharacter(contactID) and not util.IsNPC(contactID) and contact.inWatchlist and contactType == 'contact':
                    if sm.GetService('onlineStatus').GetOnlineStatus(contactID):
                        sm.ScatterEvent('OnContactLoggedOn', contactID)
                    else:
                        sm.ScatterEvent('OnContactLoggedOff', contactID)



    def RemoveFromAddressBook(self, contactIDs, contactType):
        if contactType is None:
            if util.IsNPC(contactIDs) and sm.GetService('agents').IsAgent(contactIDs):
                sm.RemoteSvc('charMgr').DeleteContacts([contactIDs])
                self.agents.remove(contactIDs)
                self.RefreshWindow()
                return 
        charnameList = ''
        for contactID in contactIDs:
            charName = cfg.eveowners.Get(contactID).name
            if len(contactIDs) > 1:
                if charnameList == '':
                    charnameList = '%s' % charName
                else:
                    charnameList = '%s, %s' % (charnameList, charName)
            else:
                charnameList = cfg.eveowners.Get(contactID).name

        if len(contactIDs) > 1:
            msg = 'RemoveManyFromContacts'
        else:
            msg = 'RemoveOneFromContacts'
        if contactType == 'contact':
            if eve.Message(msg, {'names': charnameList}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return 
            sm.RemoteSvc('charMgr').DeleteContacts(contactIDs)
        elif contactType == 'corpcontact':
            if eve.Message(msg, {'names': charnameList}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return 
            sm.GetService('corp').RemoveCorporateContacts(contactIDs)
        elif contactType == 'alliancecontact':
            if eve.Message(msg, {'names': charnameList}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return 
            sm.GetService('alliance').RemoveAllianceContacts(contactIDs)
        scatterList = []
        for contactID in contactIDs:
            scatterList.append(contactID)
            if contactType == 'contact':
                if contactID in self.contacts:
                    self.contacts.pop(contactID)
                    if util.IsCharacter(contactID):
                        sm.GetService('onlineStatus').ClearOnlineStatus(contactID)
            elif contactType == 'corpcontact':
                if contactID in self.corporateContacts:
                    self.corporateContacts.pop(contactID)
            elif contactType == 'alliancecontact':
                if contactID in self.allianceContacts:
                    self.allianceContacts.pop(contactID)

        if len(scatterList):
            sm.ScatterEvent('OnContactChange', scatterList, contactType)



    def DeleteEntryMulti(self, charIDs, contactType = None):
        buddygroups = uicore.registry.GetListGroups('buddygroups')
        agentgroups = uicore.registry.GetListGroups('agentgroups')
        if not hasattr(charIDs, '__iter__'):
            charIDs = [charIDs]
        if contactType is None:
            if eve.Message('RemoveAgents', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return 
            for charID in charIDs:
                for listgroup in [agentgroups]:
                    for group in listgroup.itervalues():
                        if not group:
                            continue
                        if charID in group['groupItems']:
                            group['groupItems'].remove(charID)


                self.RemoveFromAddressBook(charID, contactType)

        else:
            self.RemoveFromAddressBook(charIDs, contactType)



    def ShowContacts(self, contactType, contactsForm = None):
        if contactsForm is None:
            wnd = self.GetWnd()
            if wnd is None or wnd.destroyed:
                return 
            if getattr(wnd, 'contactsIniting', 0):
                return 
            if not getattr(wnd, 'contactsInited', 0):
                wnd.contactsIniting = 1
                wnd.sr.contacts.Setup('contact')
                wnd.contactsInited = 1
                wnd.contactsIniting = 0
            contactsForm = wnd.sr.contacts
        contactsForm.LoadContactsForm(contactType)



    def ShowAgents(self):
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed:
            return 
        wnd.sr.agentbtns.state = uiconst.UI_PICKCHILDREN
        scrollData = self._GetAgentScrollData()
        scrolllist = []
        for s in scrollData:
            data = {'GetSubContent': self.GetAgentsSubContent,
             'DropData': self.DropInBuddyGroup,
             'RefreshScroll': self.RefreshWindow,
             'label': s.label,
             'id': s.id,
             'groupItems': s.groupItems,
             'headers': [mls.UI_GENERIC_NAME],
             'iconMargin': 18,
             'showlen': 0,
             'state': s.state,
             'npc': True,
             'allowCopy': 1,
             'showicon': s.logo,
             'posttext': ' [%s]' % len(s.groupItems),
             'allowGuids': ['listentry.User', 'listentry.Sender']}
            sortBy = s.sortBy
            scrolllist.append((sortBy.lower(), listentry.Get('Group', data)))

        wnd.sr.scroll.sr.iconMargin = 18
        scrolllist = uiutil.SortListOfTuples(scrolllist)
        wnd.sr.scroll.Load(contentList=scrolllist, fixedEntryHeight=None, headers=[mls.UI_GENERIC_NAME], scrolltotop=not getattr(wnd, 'personalshown', 0), noContentHint=mls.UI_SHARED_YOUDONTKNOWANYAGENTS)
        setattr(wnd, 'personalshown', 1)
        if wnd is not None and not wnd.destroyed:
            wnd.HideLoad()



    def _GetAgentScrollData(self):
        scrollData = []
        groups = uicore.registry.GetListGroups('agentgroups')
        for g in groups.iteritems():
            key = g[0]
            data = util.KeyVal(g[1])
            if key == 'all':
                data.logo = '_22_41'
                data.sortBy = ['  1', '  2'][(key == 'allcorps')]
                data.groupItems = self.agents
            else:
                data.logo = 'ui_22_32_32'
                data.sortBy = data.label
                data.state = None
                data.groupItems = filter(lambda charID: charID in self.agents, data.groupItems)
            scrollData.append(data)

        return scrollData



    def DropInBuddyGroup(self, listID_groupID, nodes, *args):
        ids = []
        for node in nodes:
            if node.Get('__guid__', None) in ('listentry.User', 'listentry.Sender') and node.itemID != session.charid:
                self.AddToPersonal(node.itemID, None, refresh=node == nodes[-1])
            currentListGroupID = node.Get('listGroupID', None)
            ids.append((node.itemID, currentListGroupID, listID_groupID))

        for (itemID, currentListGroupID, listID_groupID,) in ids:
            if currentListGroupID and itemID:
                uicore.registry.RemoveFromListGroup(currentListGroupID, itemID)
            uicore.registry.AddToListGroup(listID_groupID, itemID)

        uicore.registry.ReloadGroupWindow(listID_groupID)
        self.RefreshWindow()



    def GetAgentsSubContent(self, nodedata, newitems = 0):
        if not len(nodedata.groupItems):
            return []
        charsToPrime = []
        for charID in nodedata.groupItems:
            charsToPrime.append(charID)

        cfg.eveowners.Prime(charsToPrime)
        scrolllist = []
        for charID in nodedata.groupItems:
            if charID in self.agents:
                scrolllist.append(listentry.Get('User', {'listGroupID': nodedata.id,
                 'charID': charID,
                 'info': cfg.eveowners.Get(charID)}))

        return scrolllist



    def ShowPlaces(self):
        self.semaphore.acquire()
        wnd = self.GetWnd()
        try:
            if wnd is not None and not wnd.destroyed:
                wnd.ShowLoad()
            else:
                return 
            try:
                wnd.sr.bookmarkbtns.state = uiconst.UI_PICKCHILDREN
                places = self.GetMapBookmarks()
                bookmarkIDs = []
                locations = []
                for each in places:
                    locations.append(each.itemID)
                    bookmarkIDs.append(each.bookmarkID)

                if len(locations):
                    cfg.evelocations.Prime(locations, 0)
                scrolllist = []
                idsInGroups = []
                headers = [mls.UI_GENERIC_LABEL,
                 mls.UI_GENERIC_TYPE,
                 mls.UI_GENERIC_JUMPS,
                 mls.UI_GENERIC_SOLARSYSTEMSHORT,
                 mls.UI_GENERIC_CONSTELLATIONSHORT,
                 mls.UI_GENERIC_REGIONSHORT,
                 mls.UI_GENERIC_DATE]
                missiongroupState = uicore.registry.GetListGroupOpenState(('missiongroups', 'agentmissions'))
                agentGroup = uicore.registry.GetLockedGroup('missiongroups', 'agentmissions', mls.UI_SHARED_AGENTMISSIONS, openState=missiongroupState)
                (ok, _idsInGroups,) = self.GetAgentMissionItems(places)
                idsInGroups += _idsInGroups
                data = {'GetSubContent': self.GetPlacesSubContent_AgentMissions,
                 'DropData': self.DropInPlacesGroup_Agent,
                 'RefreshScroll': self.RefreshWindow,
                 'label': agentGroup['label'],
                 'id': agentGroup['id'],
                 'groupItems': ok,
                 'headers': headers,
                 'iconMargin': 18,
                 'showlen': 0,
                 'state': 'locked',
                 'BlockOpenWindow': 1,
                 'allowGuids': ['listentry.PlaceEntry', 'xtriui.InvItem', 'listentry.InvItem']}
                scrolllist.append(('   ', listentry.Get('Group', data)))
                for group in uicore.registry.GetListGroups('places2_%s' % session.charid).itervalues():
                    if not group:
                        continue
                    all = group['groupItems'][:]
                    ok = filter(lambda bookmarkID: bookmarkID in bookmarkIDs and not (type(bookmarkID) == types.TupleType and bookmarkID[0] == 'agentmissions'), group['groupItems'])
                    for each in ok:
                        idsInGroups.append(each)

                    data = {'GetSubContent': self.GetPlacesSubContent,
                     'DropData': self.DropInPlacesGroup,
                     'DeleteCallback': self.OnGroupDeleted,
                     'RefreshScroll': self.RefreshWindow,
                     'label': group['label'],
                     'id': group['id'],
                     'groupItems': ok,
                     'headers': headers,
                     'iconMargin': 18,
                     'showlen': 0,
                     'posttext': ' [%s]' % len(ok),
                     'allowGuids': ['listentry.PlaceEntry', 'xtriui.InvItem', 'listentry.InvItem']}
                    scrolllist.append((group['label'].lower(), listentry.Get('Group', data)))

                scrolllist = uiutil.SortListOfTuples(scrolllist)
                scrolllist += self.GetPlacesScrollList([ place for place in places if place.bookmarkID not in idsInGroups ], None)
                wnd.sr.scroll.sr.iconMargin = 18
                scrollToProportion = 0
                if getattr(self, 'lastTab', '') == 'places':
                    scrollToProportion = wnd.sr.scroll.GetScrollProportion()
                wnd.sr.scroll.Load(contentList=scrolllist, fixedEntryHeight=None, headers=headers, scrollTo=scrollToProportion, noContentHint=mls.UI_SHARED_NOKNOWNPLACES)

            finally:
                if wnd is not None and not wnd.destroyed:
                    wnd.HideLoad()


        finally:
            self.semaphore.release()




    def GetAgentMissionItems(self, places = None):
        ok = []
        idsInGroups = []
        places = places or self.GetMapBookmarks()
        for place in places:
            if type(place.bookmarkID) == types.TupleType and place.bookmarkID[0] == 'agentmissions':
                ok.append(place)
                idsInGroups.append(place.bookmarkID)

        return (ok, idsInGroups)



    def OnGroupDeleted(self, ids):
        if len(ids):
            self.DeleteBookmarks(ids, 0)



    def DropInPlacesGroup_Agent(self, listID_groupID, nodes, *args):
        pass



    def DropInPlacesGroup(self, listID_groupID, nodes, *args):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.ShowLoad()
        try:
            refresh = 0
            for node in nodes:
                if node.Get('__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem') and node.rec.typeID == const.typeBookmark and node.rec.ownerID == session.charid:
                    bookmark = sm.GetService('sessionMgr').PerformSessionLockedOperation('bookmarking', sm.RemoteSvc('bookmark').AddBookmarkFromVoucher, node.rec.itemID, violateSafetyTimer=True)
                    if bookmark:
                        self.OnBookmarkAdd(bookmark)
                        uicore.registry.AddToListGroup(listID_groupID, bookmark.bookmarkID)
                        uicore.registry.ReloadGroupWindow(listID_groupID)
                        refresh = 1
                elif node.Get('__guid__', None) == 'listentry.PlaceEntry':
                    listgroupID = node.listGroupID
                    whatID = node.bm.bookmarkID
                    if whatID and listgroupID:
                        uicore.registry.RemoveFromListGroup(listgroupID, whatID)
                        uicore.registry.ReloadGroupWindow(listgroupID)
                    uicore.registry.AddToListGroup(listID_groupID, whatID)
                    uicore.registry.ReloadGroupWindow(listID_groupID)
                    refresh = 1

            if refresh:
                self.RefreshWindow()

        finally:
            if wnd is not None and not wnd.destroyed:
                wnd.HideLoad()




    def GetPlacesSubContent_AgentMissions(self, nodedata, newitems = 0):
        if newitems:
            nodedata.groupItems = self.GetAgentMissionItems()
        agentMenu = sm.GetService('journal').GetMyAgentJournalBookmarks()
        scrolllist = []
        headers = [mls.UI_GENERIC_LABEL,
         mls.UI_GENERIC_TYPE,
         mls.UI_GENERIC_DATE,
         mls.UI_GENERIC_SOLARSYSTEMSHORT,
         mls.UI_GENERIC_CONSTELLATIONSHORT,
         mls.UI_GENERIC_REGIONSHORT]
        if agentMenu:
            for (missionName, bms, agentID,) in agentMenu:
                if bms:
                    data = {'GetSubContent': self.GetPlacesSubContent_AgentMissions2,
                     'DropData ': self.DropInPlacesGroup_Agent,
                     'RefreshScroll': self.RefreshWindow,
                     'label': missionName,
                     'id': (missionName + '%s' % agentID, missionName),
                     'groupItems': nodedata.groupItems,
                     'headers': headers,
                     'iconMargin': 18,
                     'showlen': 0,
                     'state': 'locked',
                     'sublevel': 1,
                     'BlockOpenWindow': 1,
                     'allowGuids': ['listentry.PlaceEntry', 'xtriui.InvItem', 'listentry.InvItem']}
                    scrolllist.append(listentry.Get('Group', data))

        return scrolllist



    def GetPlacesSubContent_AgentMissions2(self, nodedata, newitems = 0):
        if newitems:
            nodedata.groupItems = self.GetAgentMissionItems()
        places = self.GetMapBookmarks()
        groupID = nodedata.id
        places = [ bookmark for bookmark in nodedata.groupItems if type(bookmark.bookmarkID) == types.TupleType if bookmark.bookmarkID[0] == 'agentmissions' if bookmark.missionName == groupID[0] ]
        return self.GetPlacesScrollList(places, groupID, agents=1)



    def GetPlacesSubContent(self, nodedata, newitems = 0):
        if newitems:
            groups = uicore.registry.GetListGroups('places2_%s' % session.charid)
            group = groups[str(nodedata.id[1])]
            nodedata.groupItems = group['groupItems'][:]
        if not len(nodedata.groupItems):
            return []
        places = self.GetMapBookmarks()
        groupID = nodedata.id
        places = [ bookmark for bookmark in places if bookmark.bookmarkID in nodedata.groupItems if not (type(bookmark.bookmarkID) == types.TupleType and bookmark.bookmarkID[0] == 'agentmissions') ]
        locations = []
        for each in places:
            locations.append(each.itemID)

        if len(locations):
            cfg.evelocations.Prime(locations)
        return self.GetPlacesScrollList(places, groupID)



    def GetPlacesScrollList(self, places, groupID, agents = 0):
        scrolllist = []
        for bookmark in places:
            (hint, comment,) = self.UnzipMemo(bookmark.memo)
            (sol, con, reg,) = self.GetSolConReg(bookmark)
            typename = cfg.invgroups.Get(cfg.invtypes.Get(bookmark.typeID).groupID).name
            date = util.FmtDate(bookmark.created, 'ls')
            if bookmark and (bookmark.itemID == bookmark.locationID or bookmark.typeID == const.typeSolarSystem) and bookmark.x:
                typename = mls.UI_GENERIC_COORDINATE
            jumps = 0.0
            if 40000000 > bookmark.itemID > 30000000:
                jumps = sm.GetService('pathfinder').GetJumpCountFromCurrent(bookmark.itemID)
            elif 40000000 > bookmark.locationID > 30000000:
                jumps = sm.GetService('pathfinder').GetJumpCountFromCurrent(bookmark.locationID)
            text = '%s<t>%s<t>%d<t>%s<t>%s<t>%s<t>%s' % (hint,
             typename,
             jumps,
             sol,
             con,
             reg,
             date)
            sublevel = 2 if agents == 1 else [1, 0][(groupID is None)]
            data = {'bm': bookmark,
             'itemID': bookmark.bookmarkID,
             'tabs': [],
             'hint': hint,
             'comment': comment,
             'label': text,
             'sublevel': sublevel,
             'listGroupID': groupID}
            scrolllist.append(listentry.Get('PlaceEntry', data))

        return scrolllist



    def GetSolConReg(self, bookmark):
        solname = '-'
        conname = '-'
        regname = '-'
        mapSvc = sm.GetService('map')
        sol = None
        con = None
        reg = None
        try:
            if const.minSolarSystem < bookmark.locationID <= const.maxSolarSystem:
                sol = mapSvc.GetItem(bookmark.locationID)
                con = mapSvc.GetItem(sol.locationID)
                reg = mapSvc.GetItem(con.locationID)
            elif const.minConstellation < bookmark.locationID <= const.maxConstellation:
                sol = mapSvc.GetItem(bookmark.itemID)
                con = mapSvc.GetItem(sol.locationID)
                reg = mapSvc.GetItem(con.locationID)
            elif const.minRegion < bookmark.locationID <= const.maxRegion:
                con = mapSvc.GetItem(bookmark.itemID)
                reg = mapSvc.GetItem(con.locationID)
            elif bookmark.typeID == const.typeRegion:
                reg = mapSvc.GetItem(bookmark.itemID)
            if sol is not None:
                solname = sol.itemName
            if con is not None:
                conname = con.itemName
            if reg is not None:
                regname = reg.itemName

        finally:
            return (solname, conname, regname)




    def ZipMemo(self, *parts):
        return uiutil.Zip(*parts)



    def UnzipMemo(self, s):
        split = uiutil.Unzip(s)
        if len(split) == 1:
            return (split[0], '')
        return split[:2]



    def GetStandingsLevel(self, contactID, contactType):
        if self.IsInAddressBook(contactID, contactType):
            if contactType == 'alliancecontact':
                contact = self.allianceContacts.get(contactID, None)
                if contact is not None:
                    return contact.relationshipID
            if contactType == 'corpcontact':
                contact = self.corporateContacts.get(contactID, None)
                if contact is not None:
                    return contact.relationshipID
            if contactType == 'contact':
                contact = self.contacts.get(contactID, None)
                if contact is not None:
                    return contact.relationshipID



    def IsInAddressBook(self, contactID, contactType):
        if self.contacts is None or self.allianceContacts is None or self.corporateContacts is None:
            self.GetContacts()
        if contactType == 'alliancecontact':
            return contactID in self.allianceContacts
        if contactType == 'corpcontact':
            return contactID in self.corporateContacts
        if contactType == 'contact':
            return contactID in self.contacts or contactID in self.agents



    def GetAddressBook(self):
        return self.contacts.keys()



    def IsInWatchlist(self, ownerID):
        contacts = []
        if self.contacts is None:
            self.GetContacts()
        contact = self.contacts.get(ownerID, None)
        if contact is not None:
            return contact.inWatchlist
        return False



    def GetContactEntry(self, data, contact, onlineOnly = False, dblClick = None, contactType = None, contactLevel = None, labelMask = None, menuFunction = None, extraInfo = None, listentryType = 'User'):
        entryTuple = None
        charinfo = cfg.eveowners.Get(contact.contactID)
        if onlineOnly:
            if self.IsInWatchlist(contact.contactID):
                os = sm.GetService('onlineStatus').GetOnlineStatus(contact.contactID)
                if os:
                    entry = self.GetEntryLine(data, contact, dblClick, contactType, contactLevel, labelMask, listentryType=listentryType)
                    entryTuple = (charinfo.name.lower(), entry)
        else:
            entry = self.GetEntryLine(data, contact, dblClick, contactType, contactLevel, labelMask, menuFunction, extraInfo, listentryType)
            entryTuple = (charinfo.name.lower(), entry)
        return entryTuple



    def GetEntryLine(self, data, contact, dblClick = None, contactType = None, contactLevel = None, labelMask = None, menuFunction = None, extraInfo = None, listentryType = 'User'):
        if data is None:
            data = uiutil.Bunch()
        if data.Get('groupID', None) == const.contactBlocked:
            inWatchlist = False
        else:
            inWatchlist = getattr(contact, 'inWatchlist', False)
        entry = listentry.Get(listentryType, {'listGroupID': data.Get('id', None),
         'charID': contact.contactID,
         'showOnline': inWatchlist,
         'info': cfg.eveowners.Get(contact.contactID),
         'OnDblClick': dblClick,
         'contactType': contactType,
         'contactLevel': contactLevel,
         'labelMask': labelMask,
         'MenuFunction': menuFunction,
         'extraInfo': extraInfo})
        return entry



    def GetNotifications(self, notification):
        label = ''
        senderName = ''
        if notification.senderID is not None:
            senderName = cfg.eveowners.Get(notification.senderID).ownerName
        hint = notification.body.replace('<br>', '')
        data = util.KeyVal()
        data.label = notification.body
        data.hint = hint
        data.id = notification.notificationID
        data.typeID = notification.typeID
        data.senderID = notification.senderID
        data.data = util.KeyVal(read=notification.processed)
        data.info = notification
        data.ignoreRightClick = 1
        data.Draggable_blockDrag = 1
        entry = listentry.Get('ContactNotificationEntry', data=data)
        return (notification.created, entry)



    def RenameContactLabelFromUI(self, labelID):
        ret = uix.NamePopup(mls.UI_EVEMAIL_LABELNAME, mls.UI_EVEMAIL_LABELNAME2, maxLength=const.mailMaxLabelSize, validator=self.CheckLabelName)
        if ret is None:
            return 
        name = ret.get('name', '')
        name = name.strip()
        if name:
            self.EditContactLabel(labelID, name=name)



    def EditContactLabel(self, labelID, name = None, color = None):
        if name is None and color is None or name == '':
            raise UserError('MailLabelMustProvideName')
        self.GetSvc().EditLabel(labelID, name, color)
        labels = self.GetContactLabels(self.contactType)
        if name is not None:
            if labelID in labels:
                labels[labelID].name = name
        if color is not None:
            if labelID in labels:
                labels[labelID].color = color
        sm.ScatterEvent('OnMyLabelsChanged', self.contactType, None)



    def CreateContactLabel(self, name, color = None):
        labelID = self.GetSvc().CreateLabel(name, color)
        labels = self.GetContactLabels(self.contactType)
        labels[labelID] = util.KeyVal(labelID=labelID, name=name, color=color)
        sm.ScatterEvent('OnMyLabelsChanged', self.contactType, labelID)
        return labelID



    def GetContactLabels(self, contactType):
        uthread.Lock(self, 'labels')
        try:
            self.contactType = contactType
            if contactType == 'contact':
                if self.labels is None:
                    self.labels = self.GetSvc().GetLabels()
                return self.labels
            if contactType == 'corpcontact':
                if self.corporateLabels is None:
                    self.corporateLabels = self.GetSvc().GetLabels()
                return self.corporateLabels
            if contactType == 'alliancecontact':
                if self.allianceLabels is None:
                    self.allianceLabels = self.GetSvc().GetLabels()
                return self.allianceLabels
            raise RuntimeError('contact type missing')

        finally:
            uthread.UnLock(self, 'labels')




    def GetSvc(self):
        svc = ''
        if self.contactType == 'contact':
            svc = sm.RemoteSvc('charMgr')
        elif self.contactType == 'corpcontact':
            svc = sm.GetService('corp')
        elif self.contactType == 'alliancecontact':
            svc = sm.GetService('alliance')
        return svc



    def CheckLabelName(self, dict, *args):
        name = dict.get('name', '').strip().lower()
        myLabelNames = [ label.name.lower() for label in self.GetContactLabels(self.contactType).values() ]
        if name in myLabelNames:
            return mls.UI_EVEMAIL_LABELNAMETAKEN



    def DeleteContactLabelFromUI(self, labelID, labelName):
        if eve.Message('DeleteMailLabel', {'labelName': labelName}, uiconst.YESNO) == uiconst.ID_YES:
            self.DeleteContactLabel(labelID)



    def DeleteContactLabel(self, labelID):
        self.GetSvc().DeleteLabel(labelID)
        if self.contactType == 'contact':
            contacts = self.contacts
            self.labels = None
        elif self.contactType == 'corpcontact':
            contacts = self.corporateContacts
            self.corporateLabels = None
        elif self.contactType == 'alliancecontact':
            contacts = self.allianceContacts
            self.allianceLabels = None
        else:
            raise RuntimeError('contact type missing')
        labels = self.GetContactLabels(self.contactType)
        for (contactID, contact,) in contacts.iteritems():
            contacts[contactID].labelMask = contact.labelMask & const.maxLong - labelID

        sm.ScatterEvent('OnMyLabelsChanged', self.contactType, None)



    def AssignLabelFromMenu(self, selIDs, labelID, labelName):
        self.AssignLabelFromWnd(selIDs, labelID, labelName)



    def AssignLabelFromWnd(self, selIDs, labelID, labelName = '', displayNotify = 1):
        self.GetSvc().AssignLabels(selIDs, labelID)
        if self.contactType == 'contact':
            contacts = self.contacts
        elif self.contactType == 'corpcontact':
            contacts = self.corporateContacts
        elif self.contactType == 'alliancecontact':
            contacts = self.allianceContacts
        else:
            raise RuntimeError('contact type missing')
        for contactID in selIDs:
            if self.IsInAddressBook(contactID, self.contactType):
                contacts[contactID].labelMask = contacts[contactID].labelMask | labelID
                sm.ScatterEvent('OnEditLabel', selIDs, self.contactType)
            elif len(selIDs) == 1:
                self.AddToAddressBook(contactID, self.contactType, False)
                if self.IsInAddressBook(contactID, self.contactType):
                    contacts[contactID].labelMask = contacts[contactID].labelMask | labelID
                    sm.ScatterEvent('OnEditLabel', [contactID], self.contactType)
                else:
                    return 

        if len(selIDs) and displayNotify:
            text = mls.UI_CONTACTS_LABELASSIGNED % {'labelName': labelName,
             'numMails': len(selIDs)}
            eve.Message('CustomNotify', {'notify': text})



    def RemoveLabelFromMenu(self, selIDs, labelID, labelName):
        self.RemoveLabelFromWnd(selIDs, labelID)
        text = mls.UI_CONTACTS_LABELREMOVED % {'labelName': labelName,
         'numMails': len(selIDs)}
        eve.Message('CustomNotify', {'notify': text})



    def RemoveLabelFromWnd(self, selIDs, labelID):
        self.GetSvc().RemoveLabels(selIDs, labelID)
        if self.contactType == 'contact':
            contacts = self.contacts
        elif self.contactType == 'corpcontact':
            contacts = self.corporateContacts
        elif self.contactType == 'alliancecontact':
            contacts = self.allianceContacts
        else:
            raise RuntimeError('contact type missing')
        for contactID in selIDs:
            contacts[contactID].labelMask = contacts[contactID].labelMask & const.maxLong - labelID

        sm.ScatterEvent('OnEditLabel', selIDs, self.contactType)



    def GetAssignLabelMenu(self, sel, selIDs, contactType, *args):
        m = []
        myLabels = self.GetContactLabels(contactType).values()
        labelMask = const.maxLong
        for node in sel:
            if not hasattr(node, 'labelMask'):
                return []
            if node.labelMask is not None:
                labelMask = labelMask & node.labelMask

        for each in myLabels:
            labelID = each.labelID
            if labelMask & labelID == labelID:
                continue
            label = each.name
            m.append((label, (each.name.lower(), self.AssignLabelFromMenu, (selIDs, each.labelID, each.name))))

        m = uiutil.SortListOfTuples(m)
        return m



    def GetRemoveLabelMenu(self, sel, selIDs, contactType, *args):
        m = []
        myLabels = self.GetContactLabels(contactType).values()
        labelMask = 0
        for node in sel:
            if not hasattr(node, 'labelMask'):
                return []
            if node.labelMask is not None:
                labelMask = labelMask | node.labelMask

        for each in myLabels:
            labelID = each.labelID
            if labelMask & labelID != labelID:
                continue
            label = each.name
            m.append((label, (each.name.lower(), self.RemoveLabelFromMenu, (selIDs, each.labelID, each.name))))

        m = uiutil.SortListOfTuples(m)
        return m



    def GetLabelText(self, labelMask, contactType):
        myLabels = self.GetContactLabels(contactType)
        labelText = ''
        labelNames = []
        labels = sm.GetService('mailSvc').GetLabelMaskAsList(labelMask)
        swatchColors = sm.GetService('mailSvc').GetSwatchColors()
        for labelID in labels:
            label = myLabels.get(labelID, None)
            if label is not None:
                labelNames.append((label.name, label.color))

        labelNames.sort()
        for (each, colorID,) in labelNames:
            if colorID is None or colorID not in swatchColors:
                colorID = 0
            color = swatchColors.get(colorID)[0]
            labelText += '<color=0xBF%s>%s</color>, ' % (color, each)

        labelText = labelText[:-2]
        return labelText



    def GetLabelMask(self, ownerID):
        contacts = None
        if self.contactType == 'contact':
            contacts = self.contacts
        elif self.contactType == 'corpcontact':
            contacts = self.corporateContacts
        elif self.contactType == 'alliancecontact':
            contacts = self.allianceContacts
        if contacts is None:
            contacts = self.GetContacts()
        contact = contacts.get(ownerID, None)
        if contact is not None:
            return contact.labelMask
        return 0



    def ShowLabelMenuAndManageBtn(self, formType):
        if formType == 'contact':
            return True
        if formType == 'corpcontact':
            if (const.corpRoleDirector | const.corpRoleDiplomat) & eve.session.corprole:
                return True
        elif formType == 'alliancecontact':
            if session.allianceid and sm.GetService('alliance').GetAlliance(session.allianceid).executorCorpID == session.corpid:
                if (const.corpRoleDirector | const.corpRoleDiplomat) & eve.session.corprole:
                    return True
        return False




class PlaceEntry(uicls.Container):
    __guid__ = 'listentry.PlaceEntry'
    __nonpersistvars__ = []

    def Startup(self, *etc):
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.label = uicls.Label(text='', parent=self, left=6, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, idx=0, singleline=1)
        self.sr.icon = uicls.Icon(icon='ui_9_64_1', parent=self, pos=(4, 1, 16, 16), align=uiconst.RELATIVE, ignoreSize=True)
        self.sr.selection = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.125))



    def Load(self, node):
        self.sr.node = node
        data = node
        self.sr.label.left = 24 + data.Get('sublevel', 0) * 16
        self.sr.icon.left = 4 + data.Get('sublevel', 0) * 16
        self.sr.bm = data.bm
        self.sr.label.text = data.label
        self.id = self.sr.bm.bookmarkID
        self.groupID = self.sr.node.listGroupID
        self.sr.selection.state = (uiconst.UI_HIDDEN, uiconst.UI_DISABLED)[self.sr.node.Get('selected', 0)]
        if self.sr.bm.itemID and self.sr.bm.itemID == sm.GetService('starmap').GetDestination():
            self.sr.label.color.SetRGB(1.0, 1.0, 0.0, 1.0)
        elif self.sr.bm.locationID == session.solarsystemid2:
            self.sr.label.color.SetRGB(0.5, 1.0, 0.5, 1.0)
        else:
            self.sr.label.color.SetRGB(1.0, 1.0, 1.0, 1.0)
        self.Draggable_blockDrag = 0



    def GetHeight(_self, *args):
        (node, width,) = args
        node.height = uix.GetTextHeight(node.label, autoWidth=1, singleLine=1) + 4
        return node.height



    def OnMouseHover(self, *args):
        uthread.new(self.SetHint)



    def SetHint(self, *args):
        if not (self.sr and self.sr.node):
            return 
        bookmark = self.sr.node.bm
        hint = self.sr.node.hint
        destination = sm.GetService('starmap').GetDestination()
        if destination is not None and destination == bookmark.itemID:
            hint += ' (%s)' % mls.UI_SHARED_MAPCURRENTDESTINATION
        self.sr.hint = hint



    def OnDblClick(self, *args):
        sm.GetService('addressbook').EditBookmark(self.sr.bm)



    def OnClick(self, *args):
        self.sr.node.scroll.SelectNode(self.sr.node)
        eve.Message('ListEntryClick')
        if self.sr.node.Get('OnClick', None):
            self.sr.node.OnClick(self)



    def OnMouseExit(self, *args):
        self.sr.selection.state = (uiconst.UI_HIDDEN, uiconst.UI_DISABLED)[self.sr.node.Get('selected', 0)]



    def ShowInfo(self, *args):
        sm.GetService('info').ShowInfo(const.typeBookmark, self.sr.bm.bookmarkID)



    def GetDragData(self, *args):
        ret = []
        for each in self.sr.node.scroll.GetSelectedNodes(self.sr.node):
            if not hasattr(each, 'itemID'):
                continue
            if type(each.itemID) == types.TupleType:
                self.Draggable_blockDrag = 1
                eve.Message('CantTradeMissionBookmarks')
                return []
            ret.append(each)

        return ret



    def GetMenu(self):
        selected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        multi = len(selected) > 1
        m = []
        bmIDs = [ entry.bm.bookmarkID for entry in selected if entry.bm ]
        if session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            bmids = []
            if len(bmIDs) > 10:
                text = '%s: [...]' % mls.UI_SHARED_BOOKMARKID
            else:
                text = '%s: ' % mls.UI_SHARED_BOOKMARKID + str(bmIDs)
            m += [(text, self.CopyItemIDToClipboard, (bmIDs,)), None]
            m.append(None)
        eve.Message('ListEntryClick')
        readonly = 0
        for bmID in bmIDs:
            if type(bmID) == types.TupleType:
                readonly = 1

        if not multi:
            m += sm.GetService('menu').CelestialMenu(selected[0].bm.itemID, bookmark=selected[0].bm)
            if not readonly:
                m.append((mls.UI_CMD_EDITVIEWLOCATION, sm.GetService('addressbook').EditBookmark, (selected[0].bm,)))
        elif not readonly:
            m.append((mls.UI_CMD_REMOVELOCATION, self.Delete, (bmIDs,)))
        if self.sr.node.Get('GetMenu', None) is not None:
            m += self.sr.node.GetMenu(self.sr.node)
        return m



    def CopyItemIDToClipboard(self, itemID):
        blue.pyos.SetClipboardData(str(itemID))



    def Approach(self, *args):
        bp = sm.GetService('michelle').GetRemotePark()
        if bp:
            bp.GotoBookmark(self.sr.bm.bookmarkID)



    def WarpTo(self, *args):
        bp = sm.GetService('michelle').GetRemotePark()
        if bp:
            bp.WarpToStuff('bookmark', self.sr.bm.bookmarkID)



    def Delete(self, bmIDs = None):
        ids = bmIDs or [ entry.bm.bookmarkID for entry in self.sr.node.scroll.GetSelected() ]
        if ids:
            sm.GetService('addressbook').DeleteBookmarks(ids)



    def OnDropData(self, dragObj, nodes):
        sm.GetService('addressbook').OnDropData(self, nodes)




class ContactsForm(uicls.Container):
    __guid__ = 'form.ContactsForm'
    __notifyevents__ = ['OnContactChange',
     'OnUnblockContact',
     'OnNotificationsRefresh',
     'OnMessageChanged',
     'OnMyLabelsChanged',
     'OnEditLabel']

    def Setup(self, formType):
        sm.RegisterNotify(self)
        self.startPos = 0
        self.numContacts = const.maxContactsPerPage
        self.group = None
        self.contactType = 'contact'
        self.formType = formType
        self.DrawStuff()



    def _OnClose(self):
        sm.UnregisterNotify(self)



    def DrawStuff(self, *args):
        self.sr.topCont = uicls.Container(name='topCont', parent=self, align=uiconst.TOTOP, pos=(0, 0, 0, 45))
        self.sr.mainCont = uicls.Container(name='mainCont', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.sr.topLeft = uicls.Container(name='topCont', parent=self.sr.topCont, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(const.defaultPadding,
         0,
         0,
         0))
        self.sr.topRight = uicls.Container(name='topCont', parent=self.sr.topCont, align=uiconst.TORIGHT, pos=(0, 0, 50, 0))
        self.sr.quickFilterClear = uicls.Icon(icon='ui_73_16_210', parent=self.sr.topLeft, pos=(82, 9, 16, 16), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)
        self.sr.quickFilterClear.hint = mls.UI_CMD_CLEAR
        self.sr.quickFilterClear.OnClick = self.ClearQuickFilterInput
        self.sr.quickFilterClear.OnMouseEnter = self.Nothing
        self.sr.quickFilterClear.OnMouseDown = self.Nothing
        self.sr.quickFilterClear.OnMouseUp = self.Nothing
        self.sr.quickFilterClear.OnMouseExit = self.Nothing
        self.sr.quickFilterClear.keepselection = False
        self.sr.filter = uicls.SinglelineEdit(name='filter', parent=self.sr.topLeft, maxLength=37, width=100, align=uiconst.TOPLEFT, left=const.defaultPadding, top=8, OnChange=self.SetQuickFilterInput)
        self.sr.onlinecheck = uicls.Checkbox(text=mls.UI_GENERIC_ONLINEONLY, parent=self.sr.topLeft, configName='onlinebuddyonly', retval=1, checked=settings.user.ui.Get('onlinebuddyonly', 0), groupname=None, callback=self.CheckBoxChange, align=uiconst.TOPLEFT, pos=(0, 30, 100, 0))
        if sm.GetService('addressbook').ShowLabelMenuAndManageBtn(self.formType):
            labelBtn = uix.GetBigButton(size=32, where=self.sr.topLeft, left=115, top=8, hint=mls.UI_EVEMAIL_LABELMGMT, align=uiconst.RELATIVE)
            uiutil.MapIcon(labelBtn.sr.icon, 'ui_94_64_7', ignoreSize=True)
            labelBtn.OnClick = self.ManageLabels
        btn = uix.GetBigButton(24, self.sr.topRight, 32, const.defaultPadding)
        btn.OnClick = (self.BrowseContacts, -1)
        btn.hint = mls.UI_GENERIC_PREVIOUS
        btn.state = uiconst.UI_HIDDEN
        btn.SetAlign(align=uiconst.TOPRIGHT)
        btn.sr.icon.LoadIcon('ui_23_64_1')
        self.sr.contactBackBtn = btn
        btn = uix.GetBigButton(24, self.sr.topRight, const.defaultPadding, const.defaultPadding)
        btn.OnClick = (self.BrowseContacts, 1)
        btn.hint = mls.UI_CMD_NEXT
        btn.state = uiconst.UI_HIDDEN
        btn.SetAlign(uiconst.TOPRIGHT)
        btn.sr.icon.LoadIcon('ui_23_64_2')
        self.sr.contactFwdBtn = btn
        self.sr.pageCount = uicls.Label(text='', parent=self.sr.topRight, left=10, top=30, state=uiconst.UI_DISABLED, align=uiconst.CENTERTOP)
        leftContWidth = settings.user.ui.Get('contacts_leftContWidth', 110)
        self.sr.leftCont = uicls.Container(name='leftCont', parent=self.sr.mainCont, align=uiconst.TOLEFT, pos=(const.defaultPadding,
         0,
         leftContWidth,
         0))
        self.sr.leftScroll = uicls.Scroll(name='leftScroll', parent=self.sr.leftCont, padding=(0,
         const.defaultPadding,
         0,
         const.defaultPadding))
        self.sr.leftScroll.multiSelect = 0
        self.sr.leftScroll.sr.content.OnDropData = self.OnContactDropData
        divider = xtriui.Divider(name='divider', align=uiconst.TOLEFT, width=const.defaultPadding, parent=self.sr.mainCont, state=uiconst.UI_NORMAL)
        divider.Startup(self.sr.leftCont, 'width', 'x', 110, 200)
        self.sr.rightCont = uicls.Container(name='rightCont', parent=self.sr.mainCont, align=uiconst.TOALL, pos=(0,
         0,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.rightScroll = uicls.Scroll(name='rightScroll', parent=self.sr.rightCont, padding=(0,
         const.defaultPadding,
         0,
         0))
        self.sr.rightScroll.sr.ignoreTabTrimming = 1
        self.sr.rightScroll.multiSelect = 1
        self.sr.rightScroll.sr.content.OnDropData = self.OnContactDropData
        self.sr.rightScroll.sr.id = self.formType



    def LoadLeftSide(self):
        scrolllist = self.GetStaticLabelsGroups()
        scrolllist.insert(1, listentry.Get('Space', {'height': 16}))
        scrolllist.append(listentry.Get('Space', {'height': 16}))
        data = {'GetSubContent': self.GetLabelsSubContent,
         'MenuFunction': self.LabelGroupMenu,
         'label': mls.UI_EVEMAIL_LABELS,
         'cleanLabel': mls.UI_EVEMAIL_LABELS,
         'id': ('contacts', 'Labels', mls.UI_EVEMAIL_LABELS),
         'state': 'locked',
         'BlockOpenWindow': 1,
         'showicon': 'ui_73_16_9',
         'showlen': 0,
         'groupName': 'labels',
         'groupItems': [],
         'updateOnToggle': 0}
        scrolllist.append(listentry.Get('Group', data))
        self.sr.leftScroll.Load(contentList=scrolllist)
        if self.contactType == 'contact':
            lastViewedID = settings.char.ui.Get('contacts_lastselected', None)
        elif self.contactType == 'corpcontact':
            lastViewedID = settings.char.ui.Get('corpcontacts_lastselected', None)
        elif self.contactType == 'alliancecontact':
            lastViewedID = settings.char.ui.Get('alliancecontacts_lastselected', None)
        for entry in self.sr.leftScroll.GetNodes():
            groupID = entry.groupID
            if groupID is None:
                continue
            if groupID == lastViewedID:
                panel = entry.panel
                if panel is not None:
                    panel.OnClick()
                    return 

        if len(self.sr.leftScroll.GetNodes()) > 0:
            entry = self.sr.leftScroll.GetNodes()[0]
            panel = entry.panel
            if panel is not None:
                panel.OnClick()



    def GetLabelsSubContent(self, items):
        scrolllist = []
        myLabels = sm.GetService('addressbook').GetContactLabels(self.contactType)
        swatchColors = sm.GetService('mailSvc').GetSwatchColors()
        for each in myLabels.itervalues():
            if getattr(each, 'static', 0):
                continue
            text = each.name
            count = self.GetContactsLabelCount(each.labelID)
            label = '%s [%s]' % (each.name, count)
            colorID = each.color or 0
            color = swatchColors.get(colorID, (None, None))[0]
            data = util.KeyVal()
            data.cleanLabel = each.name
            data.label = label
            data.sublevel = 1
            data.currentView = each.labelID
            data.OnClick = self.LoadGroupFromEntry
            data.GetMenu = self.GetLabelMenu
            data.OnDropData = self.OnGroupDropData
            data.color = color
            data.colorID = colorID
            data.groupID = each.labelID
            scrolllist.append((each.name.lower(), listentry.Get('MailLabelEntry', data=data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        return scrolllist



    def GetLabelMenu(self, entry):
        labelID = entry.sr.node.currentView
        m = []
        if sm.GetService('addressbook').ShowLabelMenuAndManageBtn(self.formType):
            m.append((mls.UI_EVEMAIL_RENAMELABEL, sm.GetService('addressbook').RenameContactLabelFromUI, (labelID,)))
            m.append(None)
            m.append((mls.UI_CMD_DELETE, sm.GetService('addressbook').DeleteContactLabelFromUI, (labelID, entry.sr.node.label)))
        return m



    def ManageLabels(self, *args):
        configName = '%s%s' % ('ManageLabels', self.formType)
        wnd = sm.GetService('window').GetWindow(configName, 1, decoClass=form.ManageLabels, labelType=self.formType)
        if wnd is not None:
            wnd.Maximize()



    def GetStaticLabelsGroups(self):
        scrolllist = []
        labelList = [(mls.UI_CONTACTS_ALL, const.contactAll),
         (mls.UI_CONTACTS_HIGHSTANDING, const.contactHighStanding),
         (mls.UI_CONTACTS_GOODSTANDING, const.contactGoodStanding),
         (mls.UI_CONTACTS_NEUTRALSTANDING, const.contactNeutralStanding),
         (mls.UI_CONTACTS_BADSTANDING, const.contactBadStanding),
         (mls.UI_CONTACTS_HORRIBLESTANDING, const.contactHorribleStanding)]
        if self.contactType == 'contact':
            labelList.append((mls.UI_CONTACTS_WATCHLIST, const.contactWatchlist))
            labelList.append((mls.UI_CONTACTS_BLOCKED, const.contactBlocked))
            labelList.insert(0, (mls.UI_EVEMAIL_NOTIFICATIONS, const.contactNotifications))
            lastViewedID = settings.char.ui.Get('contacts_lastselected', None)
        elif self.contactType == 'corpcontact':
            lastViewedID = settings.char.ui.Get('corpcontacts_lastselected', None)
        elif self.contactType == 'alliancecontact':
            lastViewedID = settings.char.ui.Get('alliancecontacts_lastselected', None)
        for (label, groupID,) in labelList:
            entry = self.GetGroupEntry(groupID, label, groupID == lastViewedID)
            scrolllist.append(entry)

        if self.contactType == 'contact':
            scrolllist.insert(-1, listentry.Get('Space', {'height': 16}))
        return scrolllist



    def GetGroupEntry(self, groupID, label, selected = 0):
        data = {'GetSubContent': self.GetLeftGroups,
         'label': label,
         'cleanLabel': label,
         'id': ('contact', groupID),
         'state': 'locked',
         'BlockOpenWindow': 0,
         'disableToggle': 1,
         'expandable': 0,
         'showicon': 'hide',
         'showlen': 1,
         'groupItems': self.GetContactsCount(groupID),
         'hideNoItem': 1,
         'hideExpander': 1,
         'hideExpanderLine': 1,
         'selectGroup': 1,
         'isSelected': selected,
         'groupID': groupID,
         'OnClick': self.LoadGroupFromEntry}
        entry = listentry.Get('Group', data)
        return entry



    def LoadContactsForm(self, contactType, *args):
        self.contactType = contactType
        if contactType == 'contact':
            self.sr.topCont.height = 45
            self.sr.onlinecheck.state = uiconst.UI_NORMAL
        elif sm.GetService('addressbook').ShowLabelMenuAndManageBtn(self.formType):
            self.sr.topCont.height = 38
        else:
            self.sr.topCont.height = 32
        self.sr.onlinecheck.state = uiconst.UI_HIDDEN
        self.LoadData()
        self.LoadLeftSide()



    def CheckInGroup(self, groupID, relationshipID):
        if groupID == const.contactHighStanding:
            if relationshipID > const.contactGoodStanding:
                return True
        elif groupID == const.contactGoodStanding:
            if relationshipID > const.contactNeutralStanding and relationshipID <= const.contactGoodStanding:
                return True
        elif groupID == const.contactNeutralStanding:
            if relationshipID == const.contactNeutralStanding:
                return True
        elif groupID == const.contactBadStanding:
            if relationshipID < const.contactNeutralStanding and relationshipID >= const.contactBadStanding:
                return True
        elif groupID == const.contactHorribleStanding:
            if relationshipID < const.contactBadStanding:
                return True
        return False



    def CheckHasLabel(self, labelID, labelMask):
        if labelMask & labelID == labelID:
            return True
        else:
            return False



    def LoadGroupFromEntry(self, entry, *args):
        group = entry.sr.node
        self.blockedSelected = False
        if self.group != group.groupID:
            self.startPos = 0
            self.group = group.groupID
        if group.groupID == const.contactBlocked:
            self.blockedSelected = True
        self.LoadGroupFromNode(group)



    def CheckIfAgent(self, contactID):
        if sm.GetService('agents').IsAgent(contactID):
            return True
        if util.IsNPC(contactID) and util.IsCharacter(contactID):
            return True



    def GetContactsLabelCount(self, labelID):
        contactList = []
        for contact in self.contacts:
            if self.CheckHasLabel(labelID, contact.labelMask):
                contactList.append(contact.contactID)

        count = len(contactList)
        return count



    def GetContactsCount(self, groupID):
        contactList = []
        if groupID == const.contactBlocked:
            for blocked in self.blocked:
                contactList.append(blocked.contactID)

        elif groupID == const.contactNotifications:
            for notification in self.notifications:
                contactList.append(notification.notificationID)

        else:
            for contact in self.contacts:
                if groupID == const.contactAll:
                    contactList.append(contact.contactID)
                elif groupID == const.contactWatchlist:
                    if contact.inWatchlist:
                        contactList.append(contact.contactID)
                elif groupID == const.contactHighStanding:
                    if contact.relationshipID > const.contactGoodStanding:
                        contactList.append(contact.contactID)
                elif groupID == const.contactGoodStanding:
                    if contact.relationshipID > const.contactNeutralStanding and contact.relationshipID <= const.contactGoodStanding:
                        contactList.append(contact.contactID)
                elif groupID == const.contactNeutralStanding:
                    if contact.relationshipID == const.contactNeutralStanding:
                        contactList.append(contact.contactID)
                elif groupID == const.contactBadStanding:
                    if contact.relationshipID < const.contactNeutralStanding and contact.relationshipID >= const.contactBadStanding:
                        contactList.append(contact.contactID)
                elif groupID == const.contactHorribleStanding:
                    if contact.relationshipID < const.contactBadStanding:
                        contactList.append(contact.contactID)

        return contactList



    def GetScrolllist(self, data):
        scrolllist = []
        noContentHint = mls.UI_CONTACTS_NOCONTACTS
        onlineOnly = False
        headers = True
        reverse = False
        if self.contactType == 'contact':
            settings.char.ui.Set('contacts_lastselected', data.groupID)
            onlineOnly = settings.user.ui.Get('onlinebuddyonly', 0)
            noContentHint = mls.UI_CONTACTS_NOCONTACTS
        elif self.contactType == 'corpcontact':
            settings.char.ui.Set('corpcontacts_lastselected', data.groupID)
            noContentHint = mls.UI_CONTACTS_CORPNOCONTACTS
        elif self.contactType == 'alliancecontact':
            settings.char.ui.Set('alliancecontacts_lastselected', data.groupID)
            noContentHint = mls.UI_CONTACTS_ALLIANCENOCONTACTS
        if data.groupID == const.contactWatchlist:
            self.sr.rightScroll.multiSelect = 1
            for contact in self.contacts:
                if not self.CheckIfAgent(contact.contactID) and util.IsCharacter(contact.contactID) and contact.inWatchlist:
                    entryTuple = sm.GetService('addressbook').GetContactEntry(data, contact, onlineOnly, contactType=self.contactType, contactLevel=contact.relationshipID, labelMask=contact.labelMask)
                    if entryTuple is not None:
                        scrolllist.append(entryTuple)

            noContentHint = mls.UI_SHARED_NONEONWATCHLIST
        elif data.groupID == const.contactBlocked:
            self.sr.rightScroll.multiSelect = 1
            for blocked in self.blocked:
                if blocked.contactID > 0 and not self.CheckIfAgent(blocked.contactID):
                    entryTuple = sm.GetService('addressbook').GetContactEntry(data, blocked, onlineOnly, contactType=self.contactType)
                    if entryTuple is not None:
                        scrolllist.append(entryTuple)

            noContentHint = mls.UI_SHARED_NONEBLOCKEDYET
        elif data.groupID == const.contactAll:
            self.sr.rightScroll.multiSelect = 1
            for contact in self.contacts:
                if not self.CheckIfAgent(contact.contactID):
                    entryTuple = sm.GetService('addressbook').GetContactEntry(data, contact, onlineOnly, contactType=self.contactType, contactLevel=contact.relationshipID, labelMask=contact.labelMask)
                    if entryTuple is not None:
                        scrolllist.append(entryTuple)

        elif data.groupID == const.contactNotifications:
            self.sr.rightScroll.multiSelect = 0
            for notification in self.notifications:
                scrolllist.append(sm.GetService('addressbook').GetNotifications(notification))

            headers = False
            reverse = True
            noContentHint = mls.UI_CONTACTS_NONOTIFICATIONS
        elif data.groupID in (const.contactGoodStanding,
         const.contactHighStanding,
         const.contactNeutralStanding,
         const.contactBadStanding,
         const.contactHorribleStanding):
            self.sr.rightScroll.multiSelect = 1
            for contact in self.contacts:
                if not self.CheckIfAgent(contact.contactID):
                    if self.CheckInGroup(data.groupID, contact.relationshipID):
                        entryTuple = sm.GetService('addressbook').GetContactEntry(data, contact, onlineOnly, contactType=self.contactType, contactLevel=contact.relationshipID, labelMask=contact.labelMask)
                        if entryTuple is not None:
                            scrolllist.append(entryTuple)

            if self.contactType == 'contact':
                noContentHint = mls.UI_CONTACTS_NOCONTACTSSTANDINGS % {'standing': data.cleanLabel}
            elif self.contactType == 'corpcontact':
                noContentHint = mls.UI_CONTACTS_CORPNOCONTACTSSTANDING % {'standing': data.cleanLabel}
            elif self.contactType == 'alliancecontact':
                noContentHint = mls.UI_CONTACTS_ALLIANCENOCONTACTSSTANDING % {'standing': data.cleanLabel}
        else:
            self.sr.rightScroll.multiSelect = 1
            for contact in self.contacts:
                if not self.CheckIfAgent(contact.contactID):
                    if self.CheckHasLabel(data.groupID, contact.labelMask):
                        entryTuple = sm.GetService('addressbook').GetContactEntry(data, contact, onlineOnly, contactType=self.contactType, contactLevel=contact.relationshipID, labelMask=contact.labelMask)
                        if entryTuple is not None:
                            scrolllist.append(entryTuple)

            noContentHint = mls.UI_CONTACTS_NOCONTACTSSTANDINGS % {'standing': data.cleanLabel}
        if onlineOnly:
            noContentHint = mls.UI_CONTACTS_NOONLINECONTACT
        if len(self.sr.filter.GetValue()):
            noContentHint = mls.UI_GENERIC_NOTHINGFOUND
        totalNum = len(scrolllist)
        scrolllist = uiutil.SortListOfTuples(scrolllist, reverse)
        scrolllist = scrolllist[self.startPos:(self.startPos + self.numContacts)]
        return (scrolllist,
         noContentHint,
         totalNum,
         headers)



    def LoadGroupFromNode(self, data, *args):
        if self.formType == 'alliancecontact' and session.allianceid is None:
            self.sr.rightScroll.Load(fixedEntryHeight=19, contentList=[], noContentHint=mls.UI_CORP_OWNERNOTINANYALLIANCE % {'owner': cfg.eveowners.Get(eve.session.corpid).ownerName})
            return 
        (scrolllist, noContentHint, totalNum, displayHeaders,) = self.GetScrolllist(data)
        if displayHeaders:
            headers = [mls.UI_GENERIC_NAME]
        else:
            headers = []
        self.sr.rightScroll.Load(contentList=scrolllist, headers=headers, noContentHint=noContentHint)
        if totalNum is not None:
            self.ShowHideBrowse(totalNum)



    def CheckBoxChange(self, checkbox):
        config = checkbox.data['config']
        if checkbox.data.has_key('value'):
            if checkbox.checked:
                settings.user.ui.Set(config, checkbox.data['value'])
            else:
                settings.user.ui.Set(config, checkbox.checked)
        self.LoadContactsForm(self.contactType)



    def GetLeftGroups(self, data, *args):
        scrolllist = self.GetScrolllist(data)[0]
        return scrolllist



    def LabelGroupMenu(self, node, *args):
        m = []
        m.append((mls.UI_EVEMAIL_LABELMGMT, self.ManageLabels))
        return m



    def SetQuickFilterInput(self, *args):
        uthread.new(self._SetQuickFilterInput)



    def _SetQuickFilterInput(self):
        blue.synchro.Sleep(400)
        filter = self.sr.filter.GetValue()
        if len(filter) > 0:
            self.quickFilterInput = filter.lower()
            self.LoadContactsForm(self.contactType)
            self.sr.quickFilterClear.state = uiconst.UI_NORMAL
        else:
            prefilter = self.quickFilterInput
            self.quickFilterInput = None
            if prefilter != None:
                self.LoadContactsForm(self.contactType)
            self.sr.quickFilterClear.state = uiconst.UI_HIDDEN
            self.hintText = None



    def QuickFilter(self, rec):
        name = cfg.eveowners.Get(rec.contactID).name
        name = name.lower()
        input = self.quickFilterInput.lower()
        return name.find(input) + 1



    def Nothing(self, *args):
        pass



    def ClearQuickFilterInput(self, *args):
        self.sr.filter.SetValue('')
        self.LoadContactsForm(self.contactType)



    def LoadData(self, *args):
        self.contacts = []
        self.blocked = []
        self.notifications = []
        allContacts = sm.GetService('addressbook').GetContacts()
        if self.contactType == 'contact':
            self.contacts = allContacts.contacts.values()
            self.blocked = allContacts.blocked.values()
            self.notifications = sm.GetService('notificationSvc').GetFormattedNotifications(const.groupContacts)
        elif self.contactType == 'corpcontact':
            self.contacts = allContacts.corpContacts.values()
        elif self.contactType == 'alliancecontact':
            self.contacts = allContacts.allianceContacts.values()
        filter = self.sr.filter.GetValue()
        if len(filter):
            self.blocked = uiutil.NiceFilter(self.QuickFilter, self.blocked)
            self.contacts = uiutil.NiceFilter(self.QuickFilter, self.contacts)



    def BrowseContacts(self, backforth, *args):
        pos = max(0, self.startPos + self.numContacts * backforth)
        self.startPos = pos
        self.LoadContactsForm(self.contactType)



    def ShowHideBrowse(self, totalNum):
        btnDisplayed = 0
        if self.startPos == 0:
            self.sr.contactBackBtn.state = uiconst.UI_HIDDEN
        else:
            self.sr.contactBackBtn.state = uiconst.UI_NORMAL
            btnDisplayed = 1
        if self.startPos + self.numContacts >= totalNum:
            self.sr.contactFwdBtn.state = uiconst.UI_HIDDEN
        else:
            self.sr.contactFwdBtn.state = uiconst.UI_NORMAL
            btnDisplayed = 1
        if btnDisplayed:
            if self.sr.onlinecheck.state == uiconst.UI_HIDDEN:
                self.sr.topCont.height += 10
            numPages = int(math.ceil(totalNum / float(self.numContacts)))
            currentPage = self.startPos / self.numContacts + 1
            self.sr.pageCount.text = '%s/%s' % (currentPage, numPages)
        else:
            self.sr.pageCount.text = ''



    def OnContactDropData(self, dragObj, nodes):
        if self.contactType == 'contact' and settings.char.ui.Get('contacts_lastselected', None) == const.contactBlocked:
            sm.GetService('addressbook').DropInBlocked(nodes)
        else:
            sm.GetService('addressbook').DropInPersonal(nodes, self.contactType)



    def ReloadData(self):
        self.LoadData()
        self.LoadLeftSide()
        if len(self.sr.rightScroll.GetNodes()) < 1:
            self.BrowseContacts(-1)



    def OnNotificationsRefresh(self):
        if self.formType == 'contact' and settings.char.ui.Get('contacts_lastselected', None) == const.contactNotifications:
            self.ReloadData()



    def OnMessageChanged(self, type, messageIDs, what):
        if type == const.mailTypeNotifications and what == 'deleted':
            if self.formType == 'contact' and settings.char.ui.Get('contacts_lastselected', None) == const.contactNotifications:
                self.ReloadData()



    def OnContactChange(self, contactIDs, contactType = None):
        if contactType == self.formType:
            self.ReloadData()



    def OnMyLabelsChanged(self, contactType, labelID):
        if contactType == self.formType:
            self.LoadLeftSide()



    def OnEditLabel(self, contactIDs, contactType):
        if contactType == self.formType:
            self.ReloadData()



    def OnUnblockContact(self, contactID):
        if self.formType == 'contact':
            self.ReloadData()



    def OnGroupDropData(self, groupID, nodes, *args):
        (what, labelID, labelName,) = groupID
        contactIDs = []
        for node in nodes:
            contactIDs.append(node.itemID)

        if len(contactIDs):
            sm.StartService('addressbook').AssignLabelFromWnd(contactIDs, labelID, labelName)




class ContactManagementWnd(uicls.Window):
    __guid__ = 'form.ContactManagementWnd'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        entityID = attributes.entityID
        level = attributes.level
        watchlist = attributes.watchlist
        isContact = attributes.isContact
        self.result = None
        self.SetCaption(mls.UI_CONTACTS_CONTACTMANAGEMENT)
        self.minHeight = 105
        self.SetMinSize([250, self.minHeight])
        self.MakeUnResizeable()
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.entityID = entityID
        self.level = level
        self.watchlist = watchlist
        self.isContact = isContact
        self.notify = False
        self.ConstructLayout()



    def ConstructLayout(self):
        topCont = uicls.Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 70), padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        imgCont = uicls.Container(name='imgCont', parent=topCont, align=uiconst.TOLEFT, pos=(0, 0, 64, 0), padding=(0,
         0,
         const.defaultPadding,
         0))
        topRightCont = uicls.Container(name='topRightCont', parent=topCont, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(const.defaultPadding,
         0,
         0,
         0))
        nameCont = uicls.Container(name='nameCont', parent=topRightCont, align=uiconst.TOTOP, pos=(0, 0, 0, 20), padding=(0, 0, 0, 0))
        splitter = uicls.Container(name='splitter', parent=topRightCont, align=uiconst.TOTOP, pos=(0, 0, 0, 1), padding=(0, 0, 0, 0))
        uicls.Line(parent=splitter, align=uiconst.TOBOTTOM)
        levelCont = uicls.Container(name='levelCont', parent=topRightCont, align=uiconst.TOTOP, pos=(0, 0, 0, 55), padding=(0, 0, 0, 0))
        self.standingList = {const.contactHighStanding: mls.UI_CONTACTS_HIGHSTANDING,
         const.contactGoodStanding: mls.UI_CONTACTS_GOODSTANDING,
         const.contactNeutralStanding: mls.UI_CONTACTS_NEUTRALSTANDING,
         const.contactBadStanding: mls.UI_CONTACTS_BADSTANDING,
         const.contactHorribleStanding: mls.UI_CONTACTS_HORRIBLESTANDING}
        levelList = self.standingList.keys()
        levelList.sort()
        levelText = self.standingList.get(self.level)
        self.levelText = uicls.Label(text=levelText, parent=levelCont, left=0, top=2, align=uiconst.TOPLEFT, width=170, autowidth=0, state=uiconst.UI_DISABLED, idx=0, letterspace=2, uppercase=1)
        for (i, relationshipLevel,) in enumerate(levelList):
            leftPos = i * 26
            contName = 'level%d' % i
            level = uicls.StandingsContainer(name=contName, parent=levelCont, align=uiconst.TOPLEFT, pos=(leftPos,
             20,
             20,
             20), level=relationshipLevel, text=self.standingList.get(relationshipLevel), windowName='contactmanagement')
            setattr(self.sr, contName, level)
            level.OnClick = (self.LevelOnClick, relationshipLevel, level)
            if self.level == relationshipLevel:
                level.sr.selected.state = uiconst.UI_DISABLED
                uicore.registry.SetFocus(level)

        charName = cfg.eveowners.Get(self.entityID).name
        uiutil.GetOwnerLogo(imgCont, self.entityID, size=64, noServerCall=True)
        label = uicls.Label(text=charName, parent=nameCont, left=0, top=0, align=uiconst.TOPLEFT, width=170, autowidth=False, state=uiconst.UI_DISABLED, idx=0, letterspace=2, uppercase=1)
        nameCont.state = uiconst.UI_DISABLED
        nameCont.height = label.height + 5
        self.minHeight += nameCont.height
        topCont.height = max(topCont.height, nameCont.height + levelCont.height + splitter.height)
        if util.IsCharacter(self.entityID):
            splitter = uicls.Container(name='splitter', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 1), padding=(0, 0, 0, 0))
            uicls.Line(parent=splitter, align=uiconst.TOBOTTOM)
            bottomCont = uicls.Container(name='bottomCont', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            cbCont = uicls.Container(name='cbCont', parent=bottomCont, align=uiconst.TOTOP, pos=(0, 0, 0, 10), padding=(0,
             0,
             0,
             const.defaultPadding), state=uiconst.UI_HIDDEN)
            notifyCont = uicls.Container(name='notifyCont', parent=bottomCont, align=uiconst.TOTOP, pos=(0, 0, 0, 95), padding=(0, 0, 0, 0))
            cbCont.state = uiconst.UI_NORMAL
            self.inWatchlistCb = uicls.Checkbox(text=mls.UI_CONTACTS_ADDTOWATCHLIST, parent=cbCont, configName='inWatchlistCb', retval=0, checked=self.watchlist, align=uiconst.TOPLEFT, pos=(0, 0, 210, 0))
            self.sendNotificationCb = uicls.Checkbox(text=mls.UI_CONTACTS_SENDNOTIFICATION % {'contactName': charName}, parent=notifyCont, configName='sendNotificationCb', retval=0, checked=0, align=uiconst.TOPLEFT, pos=(0, 0, 210, 0))
            self.message = uicls.EditPlainText(setvalue='', parent=notifyCont, align=uiconst.TOALL, maxLength=120, top=26)
            self.minHeight += 120
        btnText = mls.UI_SHARED_ADDCONTACT
        if self.isContact:
            btnText = mls.UI_CONTACTS_EDITCONTACT
        self.btnGroup = uicls.ButtonGroup(btns=[[btnText,
          self.Confirm,
          (),
          81,
          1,
          1,
          0], [mls.UI_CMD_CANCEL,
          self.Cancel,
          (),
          81,
          0,
          0,
          0]], parent=self.sr.main, idx=0)
        if self.level is None:
            self.levelText.text = mls.UI_CONTACTS_SELECTSTANDING
            btn = self.btnGroup.GetBtnByLabel(btnText)
            uicore.registry.SetFocus(btn)
        uthread.new(self.SetWindowSize)



    def LevelOnClick(self, level, container, *args):
        for i in xrange(0, 5):
            cont = self.sr.Get('level%d' % i)
            cont.sr.selected.state = uiconst.UI_HIDDEN

        container.sr.selected.state = uiconst.UI_DISABLED
        self.level = level
        self.levelText.text = self.standingList.get(self.level)



    def SetWindowSize(self):
        if self and not self.destroyed:
            self.height = self.minHeight
            self.SetMinSize([200, self.minHeight])



    def Confirm(self):
        if self.level is None:
            eve.Message('NoStandingsSelected')
            return 
        relationshipID = self.level
        inWatchlist = False
        sendNotification = False
        message = None
        if util.IsCharacter(self.entityID):
            inWatchlist = self.inWatchlistCb.checked
            sendNotification = self.sendNotificationCb.checked
            message = self.message.GetValue()
        self.result = (relationshipID,
         inWatchlist,
         sendNotification,
         message)
        if getattr(self, 'isModal', None):
            self.SetModalResult(1)



    def Cancel(self):
        self.result = None
        if getattr(self, 'isModal', None):
            self.SetModalResult(0)




class ContactManagementMultiEditWnd(uicls.Window):
    __guid__ = 'form.ContactManagementMultiEditWnd'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        entityIDs = attributes.entityIDs
        contactType = attributes.contactType
        self.result = None
        self.SetCaption(mls.UI_CONTACTS_CONTACTMANAGEMENT)
        self.minHeight = 105
        self.SetMinSize([250, self.minHeight])
        self.MakeUnResizeable()
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.entityIDs = entityIDs
        self.level = None
        self.contactType = contactType
        self.ConstructLayout()



    def ConstructLayout(self):
        topCont = uicls.Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 50), padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        nameCont = uicls.Container(name='nameCont', parent=topCont, align=uiconst.TOTOP, pos=(0, 0, 0, 20), padding=(0, 0, 0, 0))
        splitter = uicls.Container(name='splitter', parent=topCont, align=uiconst.TOTOP, pos=(0, 0, 0, 1), padding=(0, 0, 0, 0))
        uicls.Line(parent=splitter, align=uiconst.TOBOTTOM)
        levelCont = uicls.Container(name='levelCont', parent=topCont, align=uiconst.TOTOP, pos=(0, 0, 0, 50), padding=(0, 0, 0, 0))
        self.standingList = {const.contactHighStanding: mls.UI_CONTACTS_HIGHSTANDING,
         const.contactGoodStanding: mls.UI_CONTACTS_GOODSTANDING,
         const.contactNeutralStanding: mls.UI_CONTACTS_NEUTRALSTANDING,
         const.contactBadStanding: mls.UI_CONTACTS_BADSTANDING,
         const.contactHorribleStanding: mls.UI_CONTACTS_HORRIBLESTANDING}
        levelList = self.standingList.keys()
        levelList.sort()
        levelText = self.standingList.get(self.level)
        self.levelText = uicls.Label(text=levelText, parent=levelCont, left=0, top=2, align=uiconst.TOPLEFT, width=170, autowidth=False, state=uiconst.UI_DISABLED, idx=0, letterspace=2, uppercase=1)
        if self.contactType != 'contact':
            splitter = uicls.Container(name='splitter', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 1), padding=(0, 0, 0, 0))
            uicls.Line(parent=splitter, align=uiconst.TOBOTTOM)
            bottomCont = uicls.Container(name='bottomCont', parent=self.sr.main, align=uiconst.TOALL, pos=(15, 0, 0, 0), padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            contWidth = 48
            startVal = 0.5
            self.sr.slider = self.AddSlider(bottomCont, 'standing', -10.0, 10.0, '', startVal=startVal)
            self.sr.slider.SetValue(startVal)
            self.minHeight += 30
            boxCont = bottomCont
            levelCont.height = 15
        else:
            topCont.height = 70
            contWidth = 26
            boxCont = levelCont
            levelCont.padLeft = 50
        for (i, relationshipLevel,) in enumerate(levelList):
            leftPos = i * contWidth
            contName = 'level%d' % i
            level = uicls.StandingsContainer(name=contName, parent=boxCont, align=uiconst.TOPLEFT, pos=(leftPos,
             20,
             20,
             20), level=relationshipLevel, text=self.standingList.get(relationshipLevel), windowName='contactmanagement')
            setattr(self.sr, contName, level)
            level.OnClick = (self.LevelOnClick, relationshipLevel, level)
            if self.level == relationshipLevel:
                level.sr.selected.state = uiconst.UI_DISABLED
                uicore.registry.SetFocus(level)

        charnameList = ''
        for entityID in self.entityIDs:
            charName = cfg.eveowners.Get(entityID).name
            if charnameList == '':
                charnameList = '%s' % charName
            else:
                charnameList = '%s, %s' % (charnameList, charName)

        label = uicls.Label(text=charnameList, parent=nameCont, left=0, top=0, align=uiconst.TOPLEFT, width=self.width, autowidth=False, state=uiconst.UI_DISABLED, idx=0, letterspace=2, uppercase=1)
        nameCont.state = uiconst.UI_DISABLED
        nameCont.height = label.height + 5
        self.minHeight += nameCont.height
        topCont.height = max(topCont.height, nameCont.height + levelCont.height + splitter.height)
        btnText = mls.UI_CONTACTS_EDITCONTACT
        self.btnGroup = uicls.ButtonGroup(btns=[[btnText,
          self.Confirm,
          (),
          81,
          1,
          1,
          0], [mls.UI_CMD_CANCEL,
          self.Cancel,
          (),
          81,
          0,
          0,
          0]], parent=self.sr.main, idx=0)
        if self.level is None:
            self.levelText.text = mls.UI_CONTACTS_SELECTSTANDING
            btn = self.btnGroup.GetBtnByLabel(btnText)
            uicore.registry.SetFocus(btn)
        uthread.new(self.SetWindowSize)



    def AddSlider(self, where, config, minval, maxval, header, hint = '', startVal = 0):
        h = 10
        _par = uicls.Container(name=config + '_slider', parent=where, align=uiconst.TOTOP, pos=(0, 0, 210, 10), padding=(0, 0, 0, 0))
        par = uicls.Container(name=config + '_slider_sub', parent=_par, align=uiconst.TOPLEFT, pos=(0, 0, 210, 10), padding=(0, 0, 0, 0))
        slider = xtriui.Slider(parent=par)
        lbl = uicls.Label(text='bla', parent=par, align=uiconst.TOPLEFT, width=200, autowidth=False, left=-34, top=0, fontsize=9, letterspace=2)
        setattr(self.sr, '%sLabel' % config, lbl)
        lbl.name = 'label'
        slider.SetSliderLabel = self.SetSliderLabel
        lbl.state = uiconst.UI_HIDDEN
        slider.Startup(config, minval, maxval, None, header, startVal=startVal)
        if startVal < minval:
            startVal = minval
        slider.value = startVal
        slider.name = config
        slider.hint = hint
        slider.OnSetValue = self.OnSetValue
        return slider



    def SetSliderLabel(self, label, idname, dname, value):
        self.sr.standingLabel.text = '%.1f (%s)' % (round(value, 1), uix.GetStanding(round(value, 1)))



    def OnSetValue(self, *args):
        self.levelText.text = self.sr.standingLabel.text



    def LevelOnClick(self, level, container, *args):
        for i in xrange(0, 5):
            cont = self.sr.Get('level%d' % i)
            cont.sr.selected.state = uiconst.UI_HIDDEN

        container.sr.selected.state = uiconst.UI_DISABLED
        if self.contactType != 'contact':
            level = level / 20.0 + 0.5
            self.sr.slider.SlideTo(level)
            self.sr.slider.SetValue(level)
        else:
            self.level = level
            self.levelText.text = self.standingList.get(self.level)



    def SetWindowSize(self, *args):
        if self and not self.destroyed:
            self.height = self.minHeight
            self.SetMinSize([200, self.minHeight])



    def Confirm(self):
        if self.contactType != 'contact':
            if self.levelText.text == mls.UI_CONTACTS_SELECTSTANDING:
                eve.Message('NoStandingsSelected')
                return 
            relationshipID = round(self.sr.slider.value, 1)
        elif self.level is None:
            eve.Message('NoStandingsSelected')
            return 
        relationshipID = self.level
        self.result = relationshipID
        if getattr(self, 'isModal', None):
            self.SetModalResult(1)



    def Cancel(self):
        self.result = None
        if getattr(self, 'isModal', None):
            self.SetModalResult(0)




class CorpAllianceContactManagementWnd(uicls.Window):
    __guid__ = 'form.CorpAllianceContactManagementWnd'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        entityID = attributes.entityID
        level = attributes.level
        isContact = attributes.isContact
        self.result = None
        self.SetCaption(mls.UI_CONTACTS_CONTACTMANAGEMENT)
        self.minHeight = 150
        self.SetMinSize([250, self.minHeight])
        self.MakeUnResizeable()
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.entityID = entityID
        self.level = level
        self.isContact = isContact
        self.notify = False
        self.ConstructLayout()



    def ConstructLayout(self):
        topCont = uicls.Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 64), padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        imgCont = uicls.Container(name='imgCont', parent=topCont, align=uiconst.TOLEFT, pos=(0, 0, 64, 0), padding=(0,
         0,
         const.defaultPadding,
         0))
        topRightCont = uicls.Container(name='topRightCont', parent=topCont, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(const.defaultPadding,
         0,
         0,
         0))
        nameCont = uicls.Container(name='nameCont', parent=topRightCont, align=uiconst.TOTOP, pos=(0, 0, 0, 20), padding=(0, 0, 0, 0))
        splitter = uicls.Container(name='splitter', parent=topRightCont, align=uiconst.TOTOP, pos=(0, 0, 0, 1), padding=(0, 0, 0, 0))
        uicls.Line(parent=splitter, align=uiconst.TOBOTTOM)
        levelCont = uicls.Container(name='levelCont', parent=topRightCont, align=uiconst.TOTOP, pos=(0, 0, 0, 25), padding=(0, 0, 0, 0))
        splitter = uicls.Container(name='splitter', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 1), padding=(0, 0, 0, 0))
        uicls.Line(parent=splitter, align=uiconst.TOBOTTOM)
        bottomCont = uicls.Container(name='bottomCont', parent=self.sr.main, align=uiconst.TOALL, pos=(15, 0, 0, 0), padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.standingList = {const.contactHighStanding: mls.UI_CONTACTS_HIGHSTANDING,
         const.contactGoodStanding: mls.UI_CONTACTS_GOODSTANDING,
         const.contactNeutralStanding: mls.UI_CONTACTS_NEUTRALSTANDING,
         const.contactBadStanding: mls.UI_CONTACTS_BADSTANDING,
         const.contactHorribleStanding: mls.UI_CONTACTS_HORRIBLESTANDING}
        levelList = self.standingList.keys()
        levelList.sort()
        levelText = ''
        self.levelText = uicls.Label(text=levelText, parent=levelCont, left=0, top=15, align=uiconst.TOPLEFT, width=170, autowidth=False, state=uiconst.UI_DISABLED, idx=0, letterspace=2, uppercase=1)
        startVal = 0.5
        if self.isContact:
            startVal = self.level / 20.0 + 0.5
        self.sr.slider = self.AddSlider(bottomCont, 'standing', -10.0, 10.0, '', startVal=startVal)
        self.sr.slider.SetValue(startVal)
        for (i, relationshipLevel,) in enumerate(levelList):
            leftPos = i * 48
            contName = 'level%d' % i
            level = uicls.StandingsContainer(name=contName, parent=bottomCont, align=uiconst.TOPLEFT, pos=(leftPos,
             20,
             20,
             20), level=relationshipLevel, text=self.standingList.get(relationshipLevel), windowName='contactmanagement')
            setattr(self.sr, contName, level)
            level.OnClick = (self.LevelOnClick, relationshipLevel, level)
            if self.level == relationshipLevel:
                level.sr.selected.state = uiconst.UI_DISABLED
                uicore.registry.SetFocus(level)

        charName = cfg.eveowners.Get(self.entityID).name
        uiutil.GetOwnerLogo(imgCont, self.entityID, size=64, noServerCall=True)
        label = uicls.Label(text=charName, parent=nameCont, left=0, top=0, align=uiconst.TOPLEFT, width=170, autowidth=False, state=uiconst.UI_DISABLED, idx=0, letterspace=2, uppercase=1)
        nameCont.state = uiconst.UI_DISABLED
        nameCont.height = label.height + 5
        self.minHeight += nameCont.height
        topCont.height = max(topCont.height, nameCont.height + levelCont.height + splitter.height)
        btnText = mls.UI_SHARED_ADDCONTACT
        if self.isContact:
            btnText = mls.UI_CONTACTS_EDITCONTACT
        self.btnGroup = uicls.ButtonGroup(btns=[[btnText,
          self.Confirm,
          (),
          81,
          1,
          1,
          0], [mls.UI_CMD_CANCEL,
          self.Cancel,
          (),
          81,
          0,
          0,
          0]], parent=self.sr.main, idx=0)
        if self.level is None:
            self.levelText.text = mls.UI_CONTACTS_SELECTSTANDING
        btn = self.btnGroup.GetBtnByLabel(btnText)
        uicore.registry.SetFocus(btn)
        uthread.new(self.SetWindowSize)



    def AddSlider(self, where, config, minval, maxval, header, hint = '', startVal = 0):
        h = 10
        _par = uicls.Container(name=config + '_slider', parent=where, align=uiconst.TOTOP, pos=(0, 0, 210, 10), padding=(0, 0, 0, 0))
        par = uicls.Container(name=config + '_slider_sub', parent=_par, align=uiconst.TOPLEFT, pos=(0, 0, 210, 10), padding=(0, 0, 0, 0))
        slider = xtriui.Slider(parent=par)
        lbl = uicls.Label(text='bla', parent=par, align=uiconst.TOPLEFT, width=200, autowidth=False, left=-34, top=0, fontsize=9, letterspace=2)
        setattr(self.sr, '%sLabel' % config, lbl)
        lbl.name = 'label'
        slider.SetSliderLabel = self.SetSliderLabel
        lbl.state = uiconst.UI_HIDDEN
        slider.Startup(config, minval, maxval, None, header, startVal=startVal)
        if startVal < minval:
            startVal = minval
        slider.value = startVal
        slider.name = config
        slider.hint = hint
        slider.OnSetValue = self.OnSetValue
        return slider



    def SetSliderLabel(self, label, idname, dname, value):
        self.sr.standingLabel.text = '%.1f (%s)' % (round(value, 1), uix.GetStanding(round(value, 1)))



    def OnSetValue(self, *args):
        self.levelText.text = self.sr.standingLabel.text



    def LevelOnClick(self, level, container, *args):
        for i in xrange(0, 5):
            cont = self.sr.Get('level%d' % i)
            cont.sr.selected.state = uiconst.UI_HIDDEN

        container.sr.selected.state = uiconst.UI_DISABLED
        level = level / 20.0 + 0.5
        self.sr.slider.SlideTo(level)
        self.sr.slider.SetValue(level)



    def SetWindowSize(self):
        if self and not self.destroyed:
            self.height = self.minHeight
            self.SetMinSize([200, self.minHeight])



    def Confirm(self):
        if self.levelText.text == mls.UI_CONTACTS_SELECTSTANDING:
            eve.Message('NoStandingsSelected')
            return 
        relationshipID = round(self.sr.slider.value, 1)
        self.result = relationshipID
        if getattr(self, 'isModal', None):
            self.SetModalResult(1)



    def Cancel(self):
        self.result = None
        if getattr(self, 'isModal', None):
            self.SetModalResult(0)




class StandingsContainer(uicls.Container):
    __guid__ = 'uicls.StandingsContainer'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        text = attributes.get('text', '')
        self.text = text
        level = attributes.get('level', None)
        self.level = level
        windowName = attributes.get('windowName', '')
        self.windowName = windowName
        self.Prepare_(text, level)
        self.cursor = 1



    def Prepare_(self, text = '', contactLevel = None, *args):
        self.isTabStop = 1
        self.state = uiconst.UI_NORMAL
        flag = None
        iconNum = 0
        if contactLevel == const.contactHighStanding:
            flag = state.flagStandingHigh
            iconNum = 3
        elif contactLevel == const.contactGoodStanding:
            flag = state.flagStandingGood
            iconNum = 3
        elif contactLevel == const.contactNeutralStanding:
            flag = state.flagStandingNeutral
            iconNum = 5
        elif contactLevel == const.contactBadStanding:
            flag = state.flagStandingBad
            iconNum = 4
        elif contactLevel == const.contactHorribleStanding:
            flag = state.flagStandingHorrible
            iconNum = 4
        if flag:
            col = sm.GetService('state').GetStateColor(flag)
            flag = uicls.Container(parent=self, pos=(0, 0, 20, 20), name='flag', state=uiconst.UI_DISABLED, align=uiconst.RELATIVE)
            selected = uicls.Frame(parent=flag, color=(1.0, 1.0, 1.0, 0.75), state=uiconst.UI_HIDDEN)
            hilite = uicls.Frame(parent=flag, color=(1.0, 1.0, 1.0, 0.75), state=uiconst.UI_HIDDEN)
            icon = uicls.Sprite(parent=flag, pos=(3, 3, 15, 15), name='icon', state=uiconst.UI_DISABLED, rectLeft=iconNum * 10, rectWidth=10, rectHeight=10, texturePath='res:/UI/Texture/classes/Bracket/flagIcons.png', align=uiconst.RELATIVE)
            fill = uicls.Fill(parent=flag, color=col)
            uicls.Frame(parent=self, color=(1.0, 1.0, 1.0, 0.2))
            fill.color.a = 0.6
            self.sr.hilite = hilite
            self.sr.selected = selected
            self.hint = text



    def OnMouseEnter(self, *args):
        self.sr.hilite.state = uiconst.UI_DISABLED



    def OnMouseExit(self, *args):
        self.sr.hilite.state = uiconst.UI_HIDDEN



    def OnSetFocus(self, *args):
        self.sr.hilite.state = uiconst.UI_DISABLED



    def OnKillFocus(self, *args):
        self.sr.hilite.state = uiconst.UI_HIDDEN



    def OnChar(self, char, *args):
        if char in (uiconst.VK_SPACE, uiconst.VK_RETURN):
            wnd = sm.GetService('window').GetWindow(self.windowName)
            if wnd:
                wnd.LevelOnClick(self.level, self)




class ContactNotificationEntry(listentry.Generic):
    __guid__ = 'listentry.ContactNotificationEntry'

    def Startup(self, *args):
        listentry.Generic.Startup(self, args)
        self.sr.picture = uicls.Container(name='picture', parent=self, align=uiconst.TOPLEFT, pos=(0, 0, 32, 32), idx=0)
        self.sr.label = uicls.Label(text='', parent=self, align=uiconst.TOALL, top=0, left=0, state=uiconst.UI_DISABLED, linespace=10, idx=0, autowidth=False, autoheight=False)



    def Load(self, node):
        self.sr.node = node
        self.notificationID = node.id
        self.senderID = node.senderID
        listentry.Generic.Load(self, node)
        self.LoadContactEntry(node)
        self.sr.label.left = 35
        self.hint = node.label



    def LoadContactEntry(self, node):
        data = node.data
        uiutil.GetOwnerLogo(self.sr.picture, node.senderID, size=32, noServerCall=True)



    def GetDragData(self, *args):
        return self.sr.node.scroll.GetSelectedNodes(self.sr.node)



    def OnDropData(self, dragObj, nodes):
        pass



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = 53
        return node.height



    def GetMenu(self, *args):
        addressBookSvc = sm.GetService('addressbook')
        isContact = addressBookSvc.IsInAddressBook(self.senderID, 'contact')
        isBlocked = addressBookSvc.IsBlocked(self.senderID)
        m = []
        m.append((mls.UI_CMD_SHOWINFO, self.ShowInfo))
        if isContact:
            m.append((mls.UI_CONTACTS_EDITCONTACT, addressBookSvc.AddToPersonalMulti, (self.senderID, 'contact', True)))
            m.append((mls.UI_CONTACTS_REMOVEFROMCONTACTS, addressBookSvc.DeleteEntryMulti, ([self.senderID], 'contact')))
        else:
            m.append((mls.UI_CONTACTS_ADDTOCONTACTS, addressBookSvc.AddToPersonalMulti, (self.senderID, 'contact')))
        if isBlocked:
            m.append((mls.UI_CMD_UNBLOCK, addressBookSvc.UnblockOwner, ([self.senderID],)))
        else:
            m.append((mls.UI_CMD_BLOCK, addressBookSvc.BlockOwner, (self.senderID,)))
        m.append((mls.UI_CONTACTS_DELETENOTIFICATION, self.DeleteNotifications))
        return m



    def DeleteNotifications(self):
        sm.GetService('notificationSvc').DeleteNotifications([self.notificationID])
        sm.ScatterEvent('OnMessageChanged', const.mailTypeNotifications, [self.notificationID], 'deleted')
        sm.ScatterEvent('OnNotificationsRefresh')



    def ShowInfo(self, *args):
        if self.destroyed:
            return 
        sm.GetService('info').ShowInfo(cfg.eveowners.Get(self.senderID).typeID, self.senderID)




class ManageLabels(form.ManageLabelsBase):
    __guid__ = 'form.ManageLabels'

    def ApplyAttributes(self, attributes):
        form.ManageLabelsBase.ApplyAttributes(self, attributes)
        labelType = attributes.labelType
        self.storedSelection = []
        if labelType == 'contact':
            labelText = mls.UI_CONTACTS_LABELTEXT % {'contactType': mls.UI_CONTACTS_CONTACTS}
        elif labelType == 'corpcontact':
            labelText = mls.UI_CONTACTS_LABELTEXT % {'contactType': mls.UI_CONTACTS_CORPCONTACTS}
        else:
            labelText = mls.UI_CONTACTS_LABELTEXT % {'contactType': mls.UI_CONTACTS_ALLIANCECONTACTS}
        self.labelType = labelType
        self.sr.textCont.state = uiconst.UI_DISABLED
        text = uicls.Label(text=labelText, parent=self.sr.textCont, left=10, top=0, autowidth=0, autoheight=0, state=uiconst.UI_DISABLED, align=uiconst.TOALL)
        btns = uicls.ButtonGroup(btns=[[mls.UI_EVEMAIL_ASSIGNLABEL,
          self.AssignLabelFromBtn,
          None,
          81], [mls.UI_EVEMAIL_REMOVELABEL,
          self.RemoveLabelFromBtn,
          None,
          81]], parent=self.sr.bottom, idx=0, line=1)
        self.LoadScroll()



    def AssignLabelFromBtn(self, *args):
        self.ManageLabel(assign=1)



    def RemoveLabelFromBtn(self, *args):
        self.ManageLabel(assign=0)



    def ManageLabel(self, assign = 1):
        labelsChecked = self.FindLabelsChecked()
        numLabels = len(labelsChecked)
        scroll = None
        if numLabels < 1:
            raise UserError('CustomNotify', {'notify': mls.UI_EVEMAIL_NOLABELSSELECTED})
        if self.labelType == 'contact':
            wnd = sm.GetService('addressbook').GetWnd()
            if wnd:
                scroll = uiutil.FindChild(wnd, 'rightScroll')
        else:
            wnd = sm.GetService('corpui').GetWnd()
            if wnd:
                if self.labelType == 'corpcontact':
                    scroll = uiutil.FindChild(wnd, 'corpcontactsform', 'rightScroll')
                elif self.labelType == 'alliancecontact':
                    scroll = uiutil.FindChild(wnd, 'alliancecontactsform', 'rightScroll')
        if not wnd:
            raise UserError('CustomNotify', {'notify': mls.UI_CONTACTS_NOCONTACTSSELECTED})
        if scroll is None:
            selectedContacts = []
        else:
            selectedContacts = scroll.GetSelected()
        try:
            contactIDs = [ selIDs.charID for selIDs in selectedContacts ]
        except:
            raise UserError('CustomNotify', {'notify': mls.UI_CONTACTS_NOCONTACTSSELECTED})
        sum = 0
        for labelID in labelsChecked:
            sum = sum + labelID

        numLabels = len(labelsChecked)
        numContacts = len(contactIDs)
        if numContacts > 0:
            if assign:
                text = mls.UI_CONTACTS_LABELSASSIGNED % {'numLabels': numLabels,
                 'numContacts': numContacts}
            else:
                text = mls.UI_CONTACTS_LABELSREMOVED % {'numLabels': numLabels,
                 'numContacts': numContacts}
            eve.Message('CustomNotify', {'notify': text})
        else:
            raise UserError('CustomNotify', {'notify': mls.UI_CONTACTS_NOCONTACTSSELECTED})
        if assign == 1:
            sm.StartService('addressbook').AssignLabelFromWnd(contactIDs, sum, displayNotify=0)
        else:
            sm.StartService('addressbook').RemoveLabelFromWnd(contactIDs, sum)




class AddressBookWindow(uicls.Window):
    __guid__ = 'form.AddressBook'
    default_width = 500
    default_height = 400
    default_minSize = (320, 307)


