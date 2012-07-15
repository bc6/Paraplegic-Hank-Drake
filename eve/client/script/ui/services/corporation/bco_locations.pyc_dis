#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/services/corporation/bco_locations.py
import util
import corpObject
import uicls
import uthread
import form

class LocationsO(corpObject.base):
    __guid__ = 'corpObject.locations'

    def __init__(self, boundObject):
        corpObject.base.__init__(self, boundObject)
        self.lock = None
        self.itemIDOfficeFolderIDByCorporationID = None
        self.myCorporationsOffices = None
        self.myCoprorationsStations = None
        self.offices = None

    def Lock(self):
        if self.lock is None:
            self.lock = uthread.Semaphore()
        self.lock.acquire()

    def Unlock(self):
        self.lock.release()
        if self.lock.IsCool():
            self.lock = None

    def DoSessionChanging(self, isRemote, session, change):
        if 'stationid2' in change:
            self.itemIDOfficeFolderIDByCorporationID = None
            self.offices = None
        if 'corpid' in change:
            self.myCorporationsOffices = None
            self.myCoprorationsStations = None

    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' in change:
            oldID, newID = change['corpid']
            if newID is not None:
                if not util.IsNPC(newID):
                    self.GetMyCorporationsOffices()

    def PrimeStationOffices(self):
        if not session.stationid2:
            return
        if self.offices is not None:
            return
        try:
            self.Lock()
            if self.offices is not None:
                return
            corpStationMgr = self.GetCorpStationManager()
            corpStationMgr.Bind()
            self.offices = corpStationMgr.GetStationOffices()
            self.itemIDOfficeFolderIDByCorporationID = util.IndexRowset(['corporationID', 'itemID', 'officeFolderID'], [], 'corporationID')
            owners = []
            for office in self.offices:
                owners.append(office.corporationID)
                self.itemIDOfficeFolderIDByCorporationID[office.corporationID] = [office.corporationID, office.itemID, office.officeFolderID]

            cfg.eveowners.Prime(owners)
        finally:
            self.Unlock()

    def GetPublicStationInfo(self):
        return self.corp__corporations.GetCorporation(eve.stationItem.ownerID)

    def HasCorporationOffice(self, corpID):
        self.PrimeStationOffices()
        if self.itemIDOfficeFolderIDByCorporationID is not None:
            if self.itemIDOfficeFolderIDByCorporationID.has_key(corpID):
                return True
        return False

    def GetCorporationsWithOfficesAtStation(self):
        self.PrimeStationOffices()
        res = util.Rowset(self.corp__corporations.GetCorporation().header)
        if self.itemIDOfficeFolderIDByCorporationID is not None:
            for corpID in self.itemIDOfficeFolderIDByCorporationID.iterkeys():
                try:
                    corporation = self.corp__corporations.GetCorporation(corpID)
                    res.lines.append(corporation)
                except:
                    self.LogWarn('GetCorporationsWithOfficesAtStation() could not get corporation with id = %s. Probably invalid.' % corpID)

        return res

    def GetOffices(self):
        self.PrimeStationOffices()
        return self.offices

    def GetOffice(self, corpID = None):
        if not session.stationid2:
            return
        uthread.Lock(self, 'populatingItemIDOfficeFolderIDByCorporationID')
        try:
            if self.itemIDOfficeFolderIDByCorporationID is None:
                corpStationMgr = self.GetCorpStationManager()
                corpStationMgr.Bind()
                offices = corpStationMgr.GetCorporateStationOffice()
                self.itemIDOfficeFolderIDByCorporationID = util.IndexRowset(['corporationID',
                 'itemID',
                 'officeFolderID',
                 'stationID'], [], 'corporationID')
                for office in offices:
                    self.itemIDOfficeFolderIDByCorporationID[office.corporationID] = [office.corporationID, office.itemID, office.officeFolderID]

        finally:
            uthread.UnLock(self, 'populatingItemIDOfficeFolderIDByCorporationID')

        if corpID is None:
            corpID = eve.session.corpid
        if self.itemIDOfficeFolderIDByCorporationID.has_key(corpID):
            return self.itemIDOfficeFolderIDByCorporationID[corpID]

    def GetOffice_NoWireTrip(self):
        corpID = eve.session.corpid
        if self.itemIDOfficeFolderIDByCorporationID is not None:
            if self.itemIDOfficeFolderIDByCorporationID.has_key(corpID):
                return self.itemIDOfficeFolderIDByCorporationID[corpID]

    def GetOfficeFolderIDForOfficeID(self, officeID):
        self.PrimeStationOffices()
        if self.itemIDOfficeFolderIDByCorporationID is not None:
            for office in self.itemIDOfficeFolderIDByCorporationID.itervalues():
                if office.itemID == officeID:
                    return office.officeFolderID

    def AddOffice(self, corporationID, officeID, folderID):
        if self.itemIDOfficeFolderIDByCorporationID is None:
            self.itemIDOfficeFolderIDByCorporationID = util.IndexRowset(['corporationID', 'itemID', 'officeFolderID'], [], 'corporationID')
        self.itemIDOfficeFolderIDByCorporationID[corporationID] = [corporationID, officeID, folderID]

    def RemoveOffice(self, corporationID, officeID, folderID):
        if self.itemIDOfficeFolderIDByCorporationID is not None:
            if self.itemIDOfficeFolderIDByCorporationID.has_key(corporationID):
                del self.itemIDOfficeFolderIDByCorporationID[corporationID]

    def OnOfficeRentalChanged(self, corporationID, officeID, folderID):
        oldOfficeID = None
        if self.itemIDOfficeFolderIDByCorporationID is not None:
            if self.itemIDOfficeFolderIDByCorporationID.has_key(corporationID):
                oldOfficeID = self.itemIDOfficeFolderIDByCorporationID[corporationID].itemID
        if officeID is not None and folderID is not None:
            self.AddOffice(corporationID, officeID, folderID)
        else:
            self.RemoveOffice(corporationID, officeID, folderID)
        lobby = form.Lobby.GetIfOpen()
        if lobby:
            lobby.ReloadOfficesIfVisible()
            if officeID is None:
                lobby.LoadButtons()
        if corporationID != eve.session.corpid:
            return

    def DoesCharactersCorpOwnThisStation(self):
        if not session.stationid2:
            return
        return not util.IsNPC(eve.session.corpid) and eve.session.corpid == eve.stationItem.ownerID

    def GetMyCorporationsOffices(self):
        if self.myCorporationsOffices is None:
            self.myCorporationsOffices = self.GetCorpRegistry().GetOffices()
        return self.myCorporationsOffices

    def GetMyCorporationsStations(self):
        if self.myCoprorationsStations is None:
            self.myCoprorationsStations = self.GetCorpRegistry().GetStations()
        return self.myCoprorationsStations