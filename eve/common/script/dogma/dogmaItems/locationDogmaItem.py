import dogmax
import weakref
import log
import sys

class LocationDogmaItem(dogmax.BaseDogmaItem):
    __guid__ = 'dogmax.LocationDogmaItem'

    def __init__(self, dogmaLocation, item):
        super(LocationDogmaItem, self).__init__(dogmaLocation, item)
        self.fittedItems = {}
        self.subLocations = {}



    def Unload(self):
        super(LocationDogmaItem, self).Unload()
        for itemKey in self.subLocations.values():
            self.dogmaLocation.UnloadItem(itemKey)

        for itemKey in self.fittedItems.keys():
            self.dogmaLocation.UnloadItem(itemKey)

        if self.itemID in self.dogmaLocation.moduleListsByShipGroup:
            del self.dogmaLocation.moduleListsByShipGroup[self.itemID]



    def OnItemLoaded(self):
        self.dogmaLocation.LoadItemsInLocation(self.itemID)
        self.dogmaLocation.LoadSublocations(self.itemID)



    def ValidFittingFlag(self, flagID):
        if const.flagLoSlot0 <= flagID <= const.flagHiSlot7:
            return True
        return False



    def SetSubLocation(self, itemKey):
        flagID = itemKey[1]
        if flagID in self.subLocations:
            log.LogTraceback('SetSubLocation used for subloc with flag %s' % strx(self.subLocations[flagID]))
        self.subLocations[flagID] = itemKey



    def RemoveSubLocation(self, itemKey):
        flagID = itemKey[1]
        subLocation = self.subLocations.get(flagID, None)
        if subLocation is not None:
            if subLocation != itemKey:
                log.LogTraceback('RemoveSubLocation used for subloc with occupied flag %s' % strx((itemKey, subLocation)))
            del self.subLocations[flagID]



    def RegisterFittedItem(self, dogmaItem, flagID):
        if self.ValidFittingFlag(flagID) or dogmaItem.itemID == self.itemID or flagID == const.flagPilot:
            self.fittedItems[dogmaItem.itemID] = weakref.proxy(dogmaItem)
            self.dogmaLocation.moduleListsByShipGroup[self.itemID][dogmaItem.groupID].add(dogmaItem.itemID)



    def UnregisterFittedItem(self, dogmaItem):
        groupID = dogmaItem.groupID
        itemID = dogmaItem.itemID
        try:
            self.dogmaLocation.moduleListsByShipGroup[self.itemID][groupID].remove(itemID)
        except KeyError:
            self.dogmaLocation.LogError("UnregisterFittedItem::Tried to remove item from mlsg but group wasn't there", strx(dogmaItem))
            sys.exc_clear()
        except IndexError:
            self.dogmaLocation.LogError("UnregisterFittedItem::Tried to remove item from mlsg but it wasn't there", strx(dogmaItem))
            sys.exc_clear()
        try:
            del self.fittedItems[dogmaItem.itemID]
        except KeyError:
            self.dogmaLocation.LogError("UnregisterFittedItem::Tried to remove item from fittedItems but it wasn't there", strx(dogmaItem))



    def GetFittedItems(self):
        return self.fittedItems



    def GetShipID(self):
        return self.itemID



    def GetPersistables(self):
        ret = super(LocationDogmaItem, self).GetPersistables()
        ret.update(self.fittedItems.keys())
        return ret



    def _FlushEffects(self):
        stackTraceCount = 0
        for fittedItem in self.fittedItems.itervalues():
            if fittedItem.itemID == self.itemID:
                continue
            stackTraceCount += fittedItem.FlushEffects()

        stackTraceCount += super(dogmax.LocationDogmaItem, self)._FlushEffects()
        return stackTraceCount




