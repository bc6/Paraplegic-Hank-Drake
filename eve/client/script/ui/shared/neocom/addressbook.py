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
import uiconst
import math
import uicls
import log
import localization

class AddressBookSvc(service.Service):
    __exportedcalls__ = {'AddToPersonal': [],
     'AddToPersonalMulti': [],
     'DeleteEntryMulti': [],
     'GetBookmarks': [],
     'GetSolConReg': [],
     'BookmarkCurrentLocation': [],
     'BookmarkLocationPopup': [],
     'ZipMemo': [],
     'UnzipMemo': [],
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
     'OnRefreshBookmarks',
     'OnAgentAdded']
    __servicename__ = 'addressbook'
    __displayname__ = 'AddressBook Client Service'
    __dependencies__ = ['bookmarkSvc']
    __startupdependencies__ = ['settings']

    def __init__(self):
        service.Service.__init__(self)
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
        form.AddressBook.CloseIfOpen()



    def OnSessionChanged(self, isremote, session, change):
        if 'charid' in change and session.charid:
            self.GetContacts()
            self.RefreshWindow()



    def OnDropData(self, dragObj, nodes):
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed or not wnd.inited:
            return 
        wnd.OnDropData(dragObj, nodes)



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
            bms = self.bookmarkSvc.GetBookmarks()
            if self.contacts is not None and self.blocked is not None and self.corporateContacts is not None and self.allianceContacts is not None and self.agents is not None and bms is not None:
                return util.KeyVal(contacts=self.contacts, blocked=self.blocked, corpContacts=self.corporateContacts, allianceContacts=self.allianceContacts)
            else:
                self.contacts = {}
                self.blocked = {}
                self.corporateContacts = {}
                self.allianceContacts = {}
                self.agents = []
                tmpBlocked = []
                if session.allianceid:
                    (addressbook, self.corporateContacts, self.allianceContacts, statuses,) = uthread.parallel([(sm.RemoteSvc('charMgr').GetContactList, ()),
                     (sm.GetService('corp').GetContactList, ()),
                     (sm.GetService('alliance').GetContactList, ()),
                     (sm.GetService('onlineStatus').Prime, ())])
                else:
                    (addressbook, self.corporateContacts, statuses,) = uthread.parallel([(sm.RemoteSvc('charMgr').GetContactList, ()), (sm.GetService('corp').GetContactList, ()), (sm.GetService('onlineStatus').Prime, ())])
                for each in addressbook.addresses:
                    if util.IsNPC(each.contactID) and util.IsCharacter(each.contactID):
                        if sm.GetService('agents').IsAgent(each.contactID):
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



    def OnRefreshBookmarks(self):
        self.RefreshWindow()



    def GetBookmarks(self, *args):
        log.LogTraceback('We should call the bookmarkSvc directly')
        return self.bookmarkSvc.GetBookmarks()



    def GetAgents(self, *args):
        return self.agents



    def GetSolConReg(self, bookmark):
        solname = '-'
        conname = '-'
        regname = '-'
        mapSvc = sm.GetService('map')
        sol = None
        con = None
        reg = None
        try:
            if util.IsSolarSystem(bookmark.locationID):
                sol = mapSvc.GetItem(bookmark.locationID)
                con = mapSvc.GetItem(sol.locationID)
                reg = mapSvc.GetItem(con.locationID)
            elif util.IsConstellation(bookmark.locationID):
                sol = mapSvc.GetItem(bookmark.itemID)
                con = mapSvc.GetItem(sol.locationID)
                reg = mapSvc.GetItem(con.locationID)
            elif util.IsRegion(bookmark.locationID):
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




    def BookmarkCurrentLocation(self, *args):
        wnd = self.GetWnd()
        text = localization.GetByLabel('UI/PeopleAndPlaces/AddBookmark')
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
                text = localization.GetByLabel('UI/PeopleAndPlaces/AddBookmark')
                btn = wnd.sr.bookmarkbtns.GetBtnByLabel(text)
                btn.Enable()




    def CheckLocationID(self, locationID):
        bms = sm.GetService('bookmarkSvc').GetMyBookmarks()
        for bookmark in bms.itervalues():
            if bookmark.itemID == locationID:
                return self.UnzipMemo(bookmark.memo)[0]




    def BookmarkLocationPopup(self, locationid, typeID, parentID, note = None, scannerInfo = None):
        checkavail = self.CheckLocationID(locationid)
        locationName = self.GetDefaultLocationName(locationid, scannerInfo)
        if checkavail and locationid not in (session.shipid, session.solarsystemid):
            if eve.Message('AskProceedBookmarking', {'locationname': cfg.invtypes.Get(typeID).typeName,
             'caption': checkavail}, uiconst.YESNO) != uiconst.ID_YES:
                return 
        wnd = form.BookmarkLocationWindow.Open(locationID=locationid, typeID=typeID, parentID=parentID, scannerInfo=scannerInfo, locationName=locationName, note=note)
        wnd.Maximize()



    def GetDefaultLocationName(self, locationID, scannerInfo):
        if locationID in (session.solarsystemid, session.shipid):
            if scannerInfo is not None:
                locationName = scannerInfo.name
            else:
                locationName = localization.GetByLabel('UI/PeopleAndPlaces/SpotInSolarSystem', solarSystemName=cfg.evelocations.Get(session.solarsystemid2).name)
        else:
            mapSvc = sm.GetService('map')
            locationName = cfg.evelocations.Get(locationID).name
            locationObj = mapSvc.GetItem(locationID)
            if locationObj:
                locationName = localization.GetByLabel('UI/PeopleAndPlaces/NewBookmarkLocationLabel', loc=locationID, group=cfg.invtypes.Get(locationObj.typeID).name)
            bp = sm.GetService('michelle').GetBallpark()
            if bp:
                slimItem = uix.GetBallparkRecord(locationID)
                if slimItem is not None:
                    if locationName is None or len(locationName) == 1:
                        locationName = cfg.invtypes.Get(slimItem.typeID).Group().name
                    else:
                        locationName = localization.GetByLabel('UI/PeopleAndPlaces/NewBookmarkLocationLabel', loc=locationID, group=cfg.invtypes.Get(slimItem.typeID).Group().name)
        return locationName



    def UpdateBookmark(self, bookmarkID, header = None, note = None, folderID = -1):
        bm = self.GetBookmark(bookmarkID)
        (oldheader, oldnote,) = self.UnzipMemo(bm.memo)
        oldnote = bm.note
        oldFolderID = bm.folderID
        if header is None:
            header = oldheader
        if note is None:
            note = oldnote
        if folderID is -1:
            folderID = oldFolderID
        if note == oldnote and header == oldheader and folderID == oldFolderID:
            return 
        memo = self.ZipMemo(header[:100], '')
        if bm.memo != memo or note != oldnote or folderID != oldFolderID:
            uthread.pool('AddressBook::CorpBookmarkMgr.UpdateBookmark', sm.GetService('bookmarkSvc').UpdateBookmark, bookmarkID, memo, note, folderID)



    def BookmarkLocation(self, itemID, name, comment, typeID, locationID = None, folderID = None):
        self.bookmarkSvc.BookmarkLocation(itemID, name, comment, typeID, locationID=locationID, folderID=folderID)



    def GetBookmark(self, bookmarkID):
        return sm.GetService('bookmarkSvc').GetBookmark(bookmarkID)



    def DeleteBookmarks(self, ids, refreshWindow = True, alreadyDeleted = 0):
        if eve.Message('RemoveLocation', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return 
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.ShowLoad()
        try:
            self.bookmarkSvc.DeleteBookmarks(ids)

        finally:
            if wnd is not None and not wnd.destroyed:
                wnd.HideLoad()

        if refreshWindow:
            self.RefreshWindow()



    def EditBookmark(self, bm):
        if not hasattr(bm, 'note'):
            return 
        (oldlabel, oldnote,) = self.UnzipMemo(bm.memo)
        oldnote = bm.note
        return form.BookmarkLocationWindow(bookmark=bm, locationName=oldlabel, note=oldnote)



    def Reset(self):
        self.destinationSetOnce = 0
        self.deleted = []



    def RefreshWindow(self):
        wnd = form.AddressBook.GetIfOpen()
        if wnd is not None and not wnd.destroyed and wnd.inited:
            if getattr(wnd.sr, 'maintabs', None) is not None:
                wnd.sr.maintabs.ReloadVisible()



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



    def GetWnd(self, new = 0):
        if new:
            return form.AddressBook.ToggleOpenClose()
        else:
            return form.AddressBook.GetIfOpen()



    def CheckBoxChange(self, checkbox):
        config = checkbox.data['config']
        if checkbox.data.has_key('value'):
            if checkbox.checked:
                settings.user.ui.Set(config, checkbox.data['value'])
            else:
                settings.user.ui.Set(config, checkbox.checked)
        self.RefreshWindow()



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
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/PeopleAndPlaces/CannotBlockSelf')})
            return 
        if util.IsNPC(ownerID):
            if util.IsCharacter(ownerID):
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/PeopleAndPlaces/CannotBlockAgents')})
            elif util.IsCorporation(ownerID) or util.IsAlliance(ownerID):
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/PeopleAndPlaces/CannotBlockNPCCorps')})
            return 
        if ownerID in self.blocked:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/PeopleAndPlaces/AlreadyHaveBlocked', userName=cfg.eveowners.Get(ownerID).name)})
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



    def IsBlocked(self, ownerID):
        return ownerID in self.blocked



    def EditContacts(self, contactIDs, contactType):
        wnd = form.ContactManagementMultiEditWnd.Open(windowID='contactmanagement', entityIDs=contactIDs, contactType=contactType)
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
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/PeopleAndPlaces/CannotAddSelf')})
            return 
        if util.IsNPC(contactID) and not sm.GetService('agents').IsAgent(contactID) and util.IsCharacter(contactID):
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/PeopleAndPlaces/IsNotAnAgent', agentName=cfg.eveowners.Get(contactID).name)})
            return 
        if contactType is None and contactID in self.agents:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/PeopleAndPlaces/AlreadyAContact', contactName=cfg.eveowners.Get(contactID).name)})
            return 
        if contactType == 'contact':
            if contactID in self.contacts and not edit:
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/PeopleAndPlaces/AlreadyAContact', contactName=cfg.eveowners.Get(contactID).name)})
                return 
        if contactType == 'corpcontact':
            if contactID in self.corporateContacts and not edit:
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/PeopleAndPlaces/AlreadyACorpContact', contactName=cfg.eveowners.Get(contactID).name)})
                return 
        if contactType == 'alliancecontact':
            if contactID in self.allianceContacts and not edit:
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/PeopleAndPlaces/AlreadyAnAllianceContact', contactName=cfg.eveowners.Get(contactID).name)})
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
            wnd = windowType.Open(windowID='contactmanagement', entityID=entityID, level=relationshipID, watchlist=watchlist, isContact=isContact)
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



    def OnGroupDeleted(self, ids):
        if len(ids):
            self.DeleteBookmarks(ids, 0)



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
        ret = uix.NamePopup(localization.GetByLabel('UI/PeopleAndPlaces/LabelsLabelName'), localization.GetByLabel('UI/PeopleAndPlaces/LabelsTypeNewLabelName'), maxLength=const.mailMaxLabelSize, validator=self.CheckLabelName)
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
            return localization.GetByLabel('UI/PeopleAndPlaces/LabelsLabelNameTaken')



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
            text = localization.GetByLabel('UI/PeopleAndPlaces/LabelsLabelAssigned', labelName=labelName, contacts=len(selIDs))
            eve.Message('CustomNotify', {'notify': text})



    def RemoveLabelFromMenu(self, selIDs, labelID, labelName):
        self.RemoveLabelFromWnd(selIDs, labelID)
        text = localization.GetByLabel('UI/PeopleAndPlaces/LabelRemoved', labelName=labelName, numContacts=len(selIDs))
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
            m.append((label, (each.name, self.AssignLabelFromMenu, (selIDs, each.labelID, each.name))))

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
        self.expandedHeight = False
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
        self.sr.quickFilterClear.hint = localization.GetByLabel('UI/Calendar/Hints/Clear')
        self.sr.quickFilterClear.OnClick = self.ClearQuickFilterInput
        self.sr.quickFilterClear.OnMouseEnter = self.Nothing
        self.sr.quickFilterClear.OnMouseDown = self.Nothing
        self.sr.quickFilterClear.OnMouseUp = self.Nothing
        self.sr.quickFilterClear.OnMouseExit = self.Nothing
        self.sr.quickFilterClear.keepselection = False
        self.sr.filter = uicls.SinglelineEdit(name='filter', parent=self.sr.topLeft, maxLength=37, width=100, align=uiconst.TOPLEFT, left=const.defaultPadding, top=8, OnChange=self.SetQuickFilterInput)
        self.sr.onlinecheck = uicls.Checkbox(text=localization.GetByLabel('UI/PeopleAndPlaces/OnlineOnly'), parent=self.sr.topLeft, configName='onlinebuddyonly', retval=1, checked=settings.user.ui.Get('onlinebuddyonly', 0), groupname=None, callback=self.CheckBoxChange, align=uiconst.TOPLEFT, pos=(0, 30, 100, 0))
        if sm.GetService('addressbook').ShowLabelMenuAndManageBtn(self.formType):
            labelBtn = uix.GetBigButton(size=32, where=self.sr.topLeft, left=115, top=8, hint=localization.GetByLabel('UI/PeopleAndPlaces/LabelsManageLabels'), align=uiconst.RELATIVE)
            uiutil.MapIcon(labelBtn.sr.icon, 'ui_94_64_7', ignoreSize=True)
            labelBtn.OnClick = self.ManageLabels
        btn = uix.GetBigButton(24, self.sr.topRight, 32, const.defaultPadding)
        btn.OnClick = (self.BrowseContacts, -1)
        btn.hint = localization.GetByLabel('UI/Common/Previous')
        btn.state = uiconst.UI_HIDDEN
        btn.SetAlign(align=uiconst.TOPRIGHT)
        btn.sr.icon.LoadIcon('ui_23_64_1')
        self.sr.contactBackBtn = btn
        btn = uix.GetBigButton(24, self.sr.topRight, const.defaultPadding, const.defaultPadding)
        btn.OnClick = (self.BrowseContacts, 1)
        btn.hint = localization.GetByLabel('UI/Common/Next')
        btn.state = uiconst.UI_HIDDEN
        btn.SetAlign(uiconst.TOPRIGHT)
        btn.sr.icon.LoadIcon('ui_23_64_2')
        self.sr.contactFwdBtn = btn
        self.sr.pageCount = uicls.EveLabelMedium(text='', parent=self.sr.topRight, left=10, top=30, state=uiconst.UI_DISABLED, align=uiconst.CENTERTOP)
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
         'label': localization.GetByLabel('UI/PeopleAndPlaces/Labels'),
         'cleanLabel': localization.GetByLabel('UI/PeopleAndPlaces/Labels'),
         'id': ('contacts', 'Labels', localization.GetByLabel('UI/PeopleAndPlaces/Labels')),
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



    def GetStandingNameShort(self, standing):
        if standing == const.contactHighStanding:
            return localization.GetByLabel('UI/PeopleAndPlaces/StandingExcellent')
        if standing == const.contactGoodStanding:
            return localization.GetByLabel('UI/PeopleAndPlaces/StandingGood')
        if standing == const.contactNeutralStanding:
            return localization.GetByLabel('UI/PeopleAndPlaces/StandingNeutral')
        if standing == const.contactBadStanding:
            return localization.GetByLabel('UI/PeopleAndPlaces/StandingBad')
        if standing == const.contactHorribleStanding:
            return localization.GetByLabel('UI/PeopleAndPlaces/StandingTerrible')



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
            m.append((localization.GetByLabel('UI/PeopleAndPlaces/LabelsRename'), sm.GetService('addressbook').RenameContactLabelFromUI, (labelID,)))
            m.append(None)
            m.append((localization.GetByLabel('UI/PeopleAndPlaces/LabelsDelete'), sm.GetService('addressbook').DeleteContactLabelFromUI, (labelID, entry.sr.node.label)))
        return m



    def ManageLabels(self, *args):
        configName = '%s%s' % ('ManageLabels', self.formType)
        form.ManageLabels.Open(windowID=configName, labelType=self.formType)



    def GetStaticLabelsGroups(self):
        scrolllist = []
        labelList = [(localization.GetByLabel('UI/PeopleAndPlaces/AllContacts'), const.contactAll),
         (localization.GetByLabel('UI/PeopleAndPlaces/ExcellentStanding'), const.contactHighStanding),
         (localization.GetByLabel('UI/PeopleAndPlaces/GoodStanding'), const.contactGoodStanding),
         (localization.GetByLabel('UI/PeopleAndPlaces/NeutralStanding'), const.contactNeutralStanding),
         (localization.GetByLabel('UI/PeopleAndPlaces/BadStanding'), const.contactBadStanding),
         (localization.GetByLabel('UI/PeopleAndPlaces/TerribleStanding'), const.contactHorribleStanding)]
        if self.contactType == 'contact':
            labelList.append((localization.GetByLabel('UI/PeopleAndPlaces/Watchlist'), const.contactWatchlist))
            labelList.append((localization.GetByLabel('UI/PeopleAndPlaces/Blocked'), const.contactBlocked))
            labelList.insert(0, (localization.GetByLabel('UI/PeopleAndPlaces/Notifications'), const.contactNotifications))
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



    def GetLabelName(self, labelID, *args):
        labels = sm.GetService('addressbook').GetContactLabels(self.contactType).values()
        for label in labels:
            if labelID == label.labelID:
                return label.name




    def GetScrolllist(self, data):
        scrolllist = []
        noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoContacts')
        onlineOnly = False
        headers = True
        reverse = False
        if self.contactType == 'contact':
            settings.char.ui.Set('contacts_lastselected', data.groupID)
            onlineOnly = settings.user.ui.Get('onlinebuddyonly', 0)
            noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoContacts')
        elif self.contactType == 'corpcontact':
            settings.char.ui.Set('corpcontacts_lastselected', data.groupID)
            noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoCorpContacts')
        elif self.contactType == 'alliancecontact':
            settings.char.ui.Set('alliancecontacts_lastselected', data.groupID)
            noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoAllianceContacts')
        if data.groupID == const.contactWatchlist:
            self.sr.rightScroll.multiSelect = 1
            for contact in self.contacts:
                if not self.CheckIfAgent(contact.contactID) and util.IsCharacter(contact.contactID) and contact.inWatchlist:
                    entryTuple = sm.GetService('addressbook').GetContactEntry(data, contact, onlineOnly, contactType=self.contactType, contactLevel=contact.relationshipID, labelMask=contact.labelMask)
                    if entryTuple is not None:
                        scrolllist.append(entryTuple)

            noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoneOnWatchlist')
        elif data.groupID == const.contactBlocked:
            self.sr.rightScroll.multiSelect = 1
            for blocked in self.blocked:
                if blocked.contactID > 0 and not self.CheckIfAgent(blocked.contactID):
                    entryTuple = sm.GetService('addressbook').GetContactEntry(data, blocked, onlineOnly, contactType=self.contactType)
                    if entryTuple is not None:
                        scrolllist.append(entryTuple)

            noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoneBlockedYet')
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
            noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoNotifications')
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

            standingText = self.GetStandingNameShort(data.groupID)
            if self.contactType == 'contact':
                noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoContactsStanding', standingText=standingText)
            elif self.contactType == 'corpcontact':
                noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoCorpContactsStanding', standingText=standingText)
            elif self.contactType == 'alliancecontact':
                noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoAllianceContactsStanding', standingText=standingText)
        else:
            self.sr.rightScroll.multiSelect = 1
            for contact in self.contacts:
                if not self.CheckIfAgent(contact.contactID):
                    if self.CheckHasLabel(data.groupID, contact.labelMask):
                        entryTuple = sm.GetService('addressbook').GetContactEntry(data, contact, onlineOnly, contactType=self.contactType, contactLevel=contact.relationshipID, labelMask=contact.labelMask)
                        if entryTuple is not None:
                            scrolllist.append(entryTuple)

            noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoContactsLabel', standingText=self.GetLabelName(data.groupID))
        if onlineOnly:
            noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoOnlineContact')
        if len(self.sr.filter.GetValue()):
            noContentHint = localization.GetByLabel('UI/Common/NothingFound')
        totalNum = len(scrolllist)
        scrolllist = uiutil.SortListOfTuples(scrolllist, reverse)
        scrolllist = scrolllist[self.startPos:(self.startPos + self.numContacts)]
        return (scrolllist,
         noContentHint,
         totalNum,
         headers)



    def LoadGroupFromNode(self, data, *args):
        if self.formType == 'alliancecontact' and session.allianceid is None:
            self.sr.rightScroll.Load(fixedEntryHeight=19, contentList=[], noContentHint=localization.GetByLabel('UI/PeopleAndPlaces/OwnerNotInAnyAlliance', corpName=cfg.eveowners.Get(session.corpid).ownerName))
            return 
        (scrolllist, noContentHint, totalNum, displayHeaders,) = self.GetScrolllist(data)
        if displayHeaders:
            headers = [localization.GetByLabel('UI/Common/Name')]
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
        m.append((localization.GetByLabel('UI/PeopleAndPlaces/ManageLabels'), self.ManageLabels))
        return m



    def SetQuickFilterInput(self, *args):
        uthread.new(self._SetQuickFilterInput)



    def _SetQuickFilterInput(self):
        blue.synchro.SleepWallclock(400)
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
            if self.sr.onlinecheck.state == uiconst.UI_HIDDEN and not self.expandedHeight:
                self.sr.topCont.height += 10
                self.expandedHeight = True
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
        self.SetCaption(localization.GetByLabel('UI/PeopleAndPlaces/ContactManagement'))
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
        self.standingList = {const.contactHighStanding: localization.GetByLabel('UI/PeopleAndPlaces/ExcellentStanding'),
         const.contactGoodStanding: localization.GetByLabel('UI/PeopleAndPlaces/GoodStanding'),
         const.contactNeutralStanding: localization.GetByLabel('UI/PeopleAndPlaces/NeutralStanding'),
         const.contactBadStanding: localization.GetByLabel('UI/PeopleAndPlaces/BadStanding'),
         const.contactHorribleStanding: localization.GetByLabel('UI/PeopleAndPlaces/TerribleStanding')}
        levelList = self.standingList.keys()
        levelList.sort()
        levelText = self.standingList.get(self.level)
        self.levelText = uicls.EveLabelMedium(text=levelText, parent=levelCont, height=14, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, idx=0)
        self.levelSelector = uicls.StandingLevelSelector(name='levelCont', parent=levelCont, align=uiconst.TOTOP, height=55, padTop=4, level=self.level)
        self.levelSelector.OnStandingLevelSelected = self.OnStandingLevelSelected
        charName = cfg.eveowners.Get(self.entityID).name
        uiutil.GetOwnerLogo(imgCont, self.entityID, size=64, noServerCall=True)
        label = uicls.EveLabelMedium(text=charName, parent=nameCont, left=0, top=2, align=uiconst.TOPLEFT, width=170, state=uiconst.UI_DISABLED, idx=0)
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
            self.inWatchlistCb = uicls.Checkbox(text=localization.GetByLabel('UI/PeopleAndPlaces/AddContactToWatchlist'), parent=cbCont, configName='inWatchlistCb', retval=0, checked=self.watchlist, align=uiconst.TOPLEFT, pos=(0, 0, 210, 0))
            self.sendNotificationCb = uicls.Checkbox(text=localization.GetByLabel('UI/PeopleAndPlaces/SendNotificationTo', contactName=charName), parent=notifyCont, configName='sendNotificationCb', retval=0, checked=0, align=uiconst.TOPLEFT, pos=(0, 0, 210, 0))
            self.message = uicls.EditPlainText(setvalue='', parent=notifyCont, align=uiconst.TOALL, maxLength=120, top=26)
            self.minHeight += 120
        btnText = localization.GetByLabel('UI/PeopleAndPlaces/AddContact')
        if self.isContact:
            btnText = localization.GetByLabel('UI/PeopleAndPlaces/EditContact')
        self.btnGroup = uicls.ButtonGroup(btns=[[btnText,
          self.Confirm,
          (),
          81,
          1,
          1,
          0], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.Cancel,
          (),
          81,
          0,
          0,
          0]], parent=self.sr.main, idx=0)
        if self.level is None:
            self.levelText.text = localization.GetByLabel('UI/PeopleAndPlaces/SelectStanding')
            btn = self.btnGroup.GetBtnByLabel(btnText)
            uicore.registry.SetFocus(btn)
        uthread.new(self.SetWindowSize)



    def OnStandingLevelSelected(self, level):
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
        self.SetCaption(localization.GetByLabel('UI/PeopleAndPlaces/ContactManagement'))
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
        levelCont = uicls.Container(name='levelCont', parent=topCont, align=uiconst.TOTOP, pos=(0, 2, 0, 55), padding=(0, 0, 0, 0))
        self.standingList = {const.contactHighStanding: localization.GetByLabel('UI/PeopleAndPlaces/ExcellentStanding'),
         const.contactGoodStanding: localization.GetByLabel('UI/PeopleAndPlaces/GoodStanding'),
         const.contactNeutralStanding: localization.GetByLabel('UI/PeopleAndPlaces/NeutralStanding'),
         const.contactBadStanding: localization.GetByLabel('UI/PeopleAndPlaces/BadStanding'),
         const.contactHorribleStanding: localization.GetByLabel('UI/PeopleAndPlaces/TerribleStanding')}
        levelList = self.standingList.keys()
        levelList.sort()
        levelText = self.standingList.get(self.level)
        self.levelText = uicls.EveLabelMedium(text=levelText, parent=levelCont, left=0, top=0, align=uiconst.TOPLEFT, width=170, state=uiconst.UI_DISABLED, idx=0)
        if self.contactType != 'contact':
            splitter = uicls.Container(name='splitter', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 1), padding=(0, 0, 0, 0))
            uicls.Line(parent=splitter, align=uiconst.TOBOTTOM)
            bottomCont = uicls.Container(name='bottomCont', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            startVal = 0.5
            sliderContainer = uicls.Container(parent=bottomCont, name='sliderContainer', align=uiconst.CENTERTOP, height=20, width=210)
            self.sr.slider = self.AddSlider(sliderContainer, 'standing', -10.0, 10.0, '', startVal=startVal)
            self.sr.slider.SetValue(startVal)
            self.minHeight += 30
            boxCont = bottomCont
            levelCont.height = 15
            iconPadding = 28
            levelAlign = uiconst.CENTERTOP
            levelWidth = 210
            self.levelText.top = 4
        else:
            topCont.height = 70
            boxCont = levelCont
            boxCont.padLeft = 50
            iconPadding = 6
            levelAlign = uiconst.TOTOP
            levelWidth = 210
            self.levelText.top = -2
        levelSelectorContainer = uicls.Container(parent=boxCont, align=uiconst.TOTOP, pos=(0, 0, 0, 55), padding=(0, 0, 0, 0))
        self.levelSelector = uicls.StandingLevelSelector(name='levelCont', parent=levelSelectorContainer, align=levelAlign, pos=(0, 14, 210, 55), padding=(0, 0, 0, 0), iconPadding=iconPadding)
        self.levelSelector.OnStandingLevelSelected = self.OnStandingLevelSelected
        charnameList = ''
        for entityID in self.entityIDs:
            charName = cfg.eveowners.Get(entityID).name
            if charnameList == '':
                charnameList = '%s' % charName
            else:
                charnameList = '%s, %s' % (charnameList, charName)

        label = uicls.EveLabelMedium(text=charnameList, parent=nameCont, left=0, top=0, align=uiconst.TOPLEFT, width=self.width, state=uiconst.UI_DISABLED, idx=0)
        nameCont.state = uiconst.UI_DISABLED
        nameCont.height = label.height + 5
        self.minHeight += nameCont.height
        topCont.height = max(topCont.height, nameCont.height + levelCont.height + splitter.height)
        btnText = localization.GetByLabel('UI/PeopleAndPlaces/EditContact')
        self.btnGroup = uicls.ButtonGroup(btns=[[btnText,
          self.Confirm,
          (),
          81,
          1,
          1,
          0], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.Cancel,
          (),
          81,
          0,
          0,
          0]], parent=self.sr.main, idx=0)
        if self.level is None:
            self.levelText.text = localization.GetByLabel('UI/PeopleAndPlaces/SelectStanding')
            btn = self.btnGroup.GetBtnByLabel(btnText)
            uicore.registry.SetFocus(btn)
        uthread.new(self.SetWindowSize)



    def AddSlider(self, where, config, minval, maxval, header, hint = '', startVal = 0):
        h = 10
        _par = uicls.Container(name=config + '_slider', parent=where, align=uiconst.TOTOP, pos=(0, 0, 210, 10), padding=(0, 0, 0, 0))
        par = uicls.Container(name=config + '_slider_sub', parent=_par, align=uiconst.TOPLEFT, pos=(0, 0, 210, 10), padding=(0, 0, 0, 0))
        slider = xtriui.Slider(parent=par)
        lbl = uicls.EveLabelSmall(text='bla', parent=par, align=uiconst.TOPLEFT, width=200, left=0, top=0)
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
        self.sr.standingLabel.text = localization.GetByLabel('UI/AddressBook/SliderLabel', value=round(value, 1), standingText=uix.GetStanding(round(value, 1)))



    def OnSetValue(self, *args):
        self.levelText.text = self.sr.standingLabel.text



    def OnStandingLevelSelected(self, level):
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
            if self.levelText.text == localization.GetByLabel('UI/PeopleAndPlaces/SelectStanding'):
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
        self.SetCaption(localization.GetByLabel('UI/PeopleAndPlaces/ContactManagement'))
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
        bottomCont = uicls.Container(name='bottomCont', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.standingList = {const.contactHighStanding: localization.GetByLabel('UI/PeopleAndPlaces/ExcellentStanding'),
         const.contactGoodStanding: localization.GetByLabel('UI/PeopleAndPlaces/GoodStanding'),
         const.contactNeutralStanding: localization.GetByLabel('UI/PeopleAndPlaces/NeutralStanding'),
         const.contactBadStanding: localization.GetByLabel('UI/PeopleAndPlaces/BadStanding'),
         const.contactHorribleStanding: localization.GetByLabel('UI/PeopleAndPlaces/TerribleStanding')}
        levelList = self.standingList.keys()
        levelList.sort()
        levelText = ''
        self.levelText = uicls.EveLabelMedium(text=levelText, parent=levelCont, left=0, top=15, align=uiconst.TOPLEFT, width=170, state=uiconst.UI_DISABLED, idx=0)
        startVal = 0.5
        if self.isContact:
            startVal = self.level / 20.0 + 0.5
        sliderContainer = uicls.Container(parent=bottomCont, name='sliderContainer', align=uiconst.CENTERTOP, height=20, width=210)
        self.sr.slider = self.AddSlider(sliderContainer, 'standing', -10.0, 10.0, '', startVal=startVal)
        self.sr.slider.SetValue(startVal)
        levelSelectorContainer = uicls.Container(parent=bottomCont, align=uiconst.TOTOP, pos=(0, 0, 0, 55), padding=(0, 0, 0, 0))
        self.levelSelector = uicls.StandingLevelSelector(name='levelCont', parent=levelSelectorContainer, align=uiconst.CENTERTOP, pos=(0, 14, 210, 55), padding=(0, 0, 0, 0), iconPadding=28, level=self.level)
        self.levelSelector.OnStandingLevelSelected = self.OnStandingLevelSelected
        charName = cfg.eveowners.Get(self.entityID).name
        uiutil.GetOwnerLogo(imgCont, self.entityID, size=64, noServerCall=True)
        label = uicls.EveLabelMedium(text=charName, parent=nameCont, left=0, top=2, align=uiconst.TOPLEFT, width=170, state=uiconst.UI_DISABLED, idx=0)
        nameCont.state = uiconst.UI_DISABLED
        nameCont.height = label.height + 5
        self.minHeight += nameCont.height
        topCont.height = max(topCont.height, nameCont.height + levelCont.height + splitter.height)
        btnText = localization.GetByLabel('UI/PeopleAndPlaces/AddContact')
        if self.isContact:
            btnText = localization.GetByLabel('UI/PeopleAndPlaces/EditContact')
        self.btnGroup = uicls.ButtonGroup(btns=[[btnText,
          self.Confirm,
          (),
          81,
          1,
          1,
          0], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.Cancel,
          (),
          81,
          0,
          0,
          0]], parent=self.sr.main, idx=0)
        if self.level is None:
            self.levelText.text = localization.GetByLabel('UI/PeopleAndPlaces/SelectStanding')
        btn = self.btnGroup.GetBtnByLabel(btnText)
        uicore.registry.SetFocus(btn)
        uthread.new(self.SetWindowSize)



    def AddSlider(self, where, config, minval, maxval, header, hint = '', startVal = 0):
        h = 10
        _par = uicls.Container(name=config + '_slider', parent=where, align=uiconst.TOTOP, pos=(0, 0, 210, 10), padding=(0, 0, 0, 0))
        par = uicls.Container(name=config + '_slider_sub', parent=_par, align=uiconst.TOPLEFT, pos=(0, 0, 210, 10), padding=(0, 0, 0, 0))
        slider = xtriui.Slider(parent=par)
        lbl = uicls.EveLabelSmall(text='bla', parent=par, align=uiconst.TOPLEFT, width=200, left=-34, top=0)
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
        self.sr.standingLabel.text = localization.GetByLabel('UI/AddressBook/SliderLabel', value=round(value, 1), standingText=uix.GetStanding(round(value, 1)))



    def OnSetValue(self, *args):
        self.levelText.text = self.sr.standingLabel.text



    def OnStandingLevelSelected(self, level):
        level = level / 20.0 + 0.5
        self.sr.slider.SlideTo(level)
        self.sr.slider.SetValue(level)



    def SetWindowSize(self):
        if self and not self.destroyed:
            self.height = self.minHeight
            self.SetMinSize([200, self.minHeight])



    def Confirm(self):
        if self.levelText.text == localization.GetByLabel('UI/PeopleAndPlaces/SelectStanding'):
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




class ContactNotificationEntry(listentry.Generic):
    __guid__ = 'listentry.ContactNotificationEntry'

    def Startup(self, *args):
        listentry.Generic.Startup(self, args)
        self.sr.picture = uicls.Container(name='picture', parent=self, align=uiconst.TOPLEFT, pos=(0, 0, 32, 32), idx=0)
        self.sr.label = uicls.EveLabelMedium(text='', parent=self, align=uiconst.TOALL, top=0, left=0, state=uiconst.UI_DISABLED, idx=0)



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
        m.append((localization.GetByLabel('UI/Commands/ShowInfo'), self.ShowInfo))
        if isContact:
            m.append((localization.GetByLabel('UI/PeopleAndPlaces/EditContact'), addressBookSvc.AddToPersonalMulti, (self.senderID, 'contact', True)))
            m.append((localization.GetByLabel('UI/PeopleAndPlaces/RemoveContact'), addressBookSvc.DeleteEntryMulti, ([self.senderID], 'contact')))
        else:
            m.append((localization.GetByLabel('UI/PeopleAndPlaces/AddContact'), addressBookSvc.AddToPersonalMulti, (self.senderID, 'contact')))
        if isBlocked:
            m.append((localization.GetByLabel('UI/PeopleAndPlaces/UnblockContact'), addressBookSvc.UnblockOwner, ([self.senderID],)))
        else:
            m.append((localization.GetByLabel('UI/PeopleAndPlaces/BlockContact'), addressBookSvc.BlockOwner, (self.senderID,)))
        m.append((localization.GetByLabel('UI/PeopleAndPlaces/DeleteNotification'), self.DeleteNotifications))
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
            labelText = localization.GetByLabel('UI/PeopleAndPlaces/LabelsTextContacts')
        elif labelType == 'corpcontact':
            labelText = localization.GetByLabel('UI/PeopleAndPlaces/LabelsTextCorpContacts')
        else:
            labelText = localization.GetByLabel('UI/PeopleAndPlaces/LabelsTextAllianceContacts')
        self.labelType = labelType
        self.sr.textCont.state = uiconst.UI_DISABLED
        text = uicls.EveLabelMedium(text=labelText, parent=self.sr.textCont, left=10, top=0, state=uiconst.UI_DISABLED, align=uiconst.TOALL)
        btns = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Mail/AssignLabel'),
          self.AssignLabelFromBtn,
          None,
          81], [localization.GetByLabel('UI/Mail/LabelRemove'),
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
            raise UserError('CustomNotify', {'notify': localization.GetByLabel('UI/PeopleAndPlaces/NoLabelsSelected')})
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
            raise UserError('CustomNotify', {'notify': localization.GetByLabel('UI/PeopleAndPlaces/NoContactsSelected')})
        if scroll is None:
            selectedContacts = []
        else:
            selectedContacts = scroll.GetSelected()
        try:
            contactIDs = [ selIDs.charID for selIDs in selectedContacts ]
        except:
            raise UserError('CustomNotify', {'notify': localization.GetByLabel('UI/PeopleAndPlaces/NoContactsSelected')})
        sum = 0
        for labelID in labelsChecked:
            sum = sum + labelID

        numLabels = len(labelsChecked)
        numContacts = len(contactIDs)
        if numContacts > 0:
            if assign:
                text = localization.GetByLabel('UI/PeopleAndPlaces/LabelsAssigned', numLabels=numLabels, numContacts=numContacts)
            else:
                text = localization.GetByLabel('UI/PeopleAndPlaces/LabelsRemoved', numLabels=numLabels, numContacts=numContacts)
            eve.Message('CustomNotify', {'notify': text})
        else:
            raise UserError('CustomNotify', {'notify': localization.GetByLabel('UI/PeopleAndPlaces/NoContactsSelected')})
        if assign == 1:
            sm.StartService('addressbook').AssignLabelFromWnd(contactIDs, sum, displayNotify=0)
        else:
            sm.StartService('addressbook').RemoveLabelFromWnd(contactIDs, sum)




