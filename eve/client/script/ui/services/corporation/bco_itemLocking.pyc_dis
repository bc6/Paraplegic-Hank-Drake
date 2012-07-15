#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/services/corporation/bco_itemLocking.py
import util
import blue
import corpObject

class ItemLockingO(corpObject.base):
    __guid__ = 'corpObject.itemLocking'

    def __init__(self, boundObject):
        corpObject.base.__init__(self, boundObject)
        self.itemsByLocationID = None

    def DoSessionChanging(self, isRemote, session, change):
        if 'corpid' in change:
            self.itemsByLocationID = None

    def OnLockedItemChange(self, itemID, ownerID, locationID, change):
        try:
            if self.itemsByLocationID is None:
                return
            if not self.itemsByLocationID.has_key(locationID):
                self.itemsByLocationID[locationID] = None
                return
            if self.itemsByLocationID[locationID] == None:
                return
            bAdd, bRemove = self.GetAddRemoveFromChange(change)
            items = self.itemsByLocationID[locationID]
            if bAdd:
                row = blue.DBRow(items.header)
                for columnName, changes in change.iteritems():
                    setattr(row, columnName, changes[1])

                items[itemID] = row
            elif bRemove:
                if items.has_key(itemID):
                    del items[itemID]
            elif items.has_key(itemID):
                item = items[itemID]
                for columnName in change.iterkeys():
                    setattr(item, columnName, change[columnName][1])

                items[itemID] = item
        finally:
            sm.ScatterEvent('OnLockedItemChangeUI', itemID, ownerID, locationID, change)

    def GetLockedItemsByLocation(self, locationID):
        if self.itemsByLocationID is None:
            self.GetLockedItemLocations()
        if not self.itemsByLocationID.has_key(locationID):
            return {}
        if self.itemsByLocationID[locationID] is None:
            rows = self.GetCorpRegistry().GetLockedItemsByLocation(locationID)
            self.itemsByLocationID[locationID] = rows
        return self.itemsByLocationID[locationID]

    def GetLockedItemLocations(self):
        if self.itemsByLocationID is None:
            self.itemsByLocationID = {}
            locationIDs = self.GetCorpRegistry().GetLockedItemLocations()
            for locationID in locationIDs:
                self.itemsByLocationID[locationID] = None

        return self.itemsByLocationID.keys()

    def IsItemLocked(self, item):
        itemID = item.itemID
        if not util.IsCorporation(item.ownerID):
            return 0
        if util.IsStation(item.locationID):
            if item.flagID == const.flagCorpMarket:
                roles = const.corpRoleAccountant | const.corpRoleTrader
                if eve.session.corprole & roles != 0:
                    return 0
            return 1
        return self.IsItemIDLocked(itemID, item.locationID, item.typeID)

    def IsItemIDLocked(self, itemID, locationID = None, typeID = None):
        stationID = None
        if locationID is not None:
            if eve.session.stationid:
                office = self.corp__locations.GetOffice()
                if office is not None:
                    if locationID == office.itemID:
                        stationID = eve.session.stationid
            if stationID is None:
                rows = self.corp__locations.GetMyCorporationsOffices().SelectByUniqueColumnValues('officeID', [locationID])
                if rows and len(rows):
                    for row in rows:
                        if locationID == row.officeID:
                            stationID = row.stationID
                            break

        if typeID is not None:
            if stationID is None and cfg.invtypes.Get(typeID).categoryID == const.categoryStation:
                stationID = locationID
        if stationID is None:
            stationID = eve.session.stationid or eve.session.solarsystemid
        if stationID is not None:
            return self.GetLockedItemsByLocation(stationID).has_key(itemID)
        return 0