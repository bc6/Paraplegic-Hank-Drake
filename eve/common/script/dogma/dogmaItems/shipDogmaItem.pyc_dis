#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/dogma/dogmaItems/shipDogmaItem.py
import dogmax
import weakref
import util
from collections import defaultdict
from itertools import izip

class ShipDogmaItem(dogmax.LocationDogmaItem):
    __guid__ = 'dogmax.ShipDogmaItem'

    def __init__(self, dogmaLocation, item):
        super(ShipDogmaItem, self).__init__(dogmaLocation, item)
        self.drones = set()
        self.damageByLayerByType = defaultdict(lambda : defaultdict(float))

    def Load(self, item, instanceRow):
        super(ShipDogmaItem, self).Load(item, instanceRow)
        self.isDirty = True

    def Unload(self):
        super(ShipDogmaItem, self).Unload()
        for droneID in self.drones.copy():
            self.dogmaLocation.UnloadItem(droneID)

        itemID = self.itemID
        if itemID in self.dogmaLocation.pilotsByShipID:
            del self.dogmaLocation.pilotsByShipID[itemID]

    def PostLoadAction(self):
        self.dogmaLocation.CheckShipOnlineModules(self.itemID)

    def OnItemLoaded(self):
        self.dogmaLocation.LoadPilot(self.itemID)
        self.dogmaLocation.FitItemToLocation(self.itemID, self.itemID, 0)
        super(ShipDogmaItem, self).OnItemLoaded()

    def CanFitItem(self, dogmaItem, flagID):
        if self.ValidFittingFlag(flagID):
            return True
        if dogmaItem.itemID == self.itemID:
            return True
        if flagID == const.flagPilot:
            return True
        return False

    def ValidFittingFlag(self, flagID):
        return cfg.IsShipFittingFlag(flagID) or flagID == const.flagDroneBay

    def SetLocation(self, locationID, locationDogmaItem, flagID):
        if locationID != self.itemID:
            raise RuntimeError('ShipDogmaItem.SetLocation::locationID is not ship (%s, %s)' % (locationID, self.itemID))
        self.fittedItems[locationID] = weakref.proxy(self)

    def SetDrones(self, drones):
        self.drones = drones

    def GetEnvironmentInfo(self):
        return util.KeyVal(itemID=self.itemID, shipID=self.itemID, charID=self.GetPilot(), otherID=None, targetID=None, effectID=None)

    def GetPersistables(self):
        ret = super(ShipDogmaItem, self).GetPersistables()
        ret.update(self.drones)
        return ret

    def RegisterDrone(self, droneID):
        self.drones.add(droneID)

    def RegisterPilot(self, pilotDogmaItem):
        pilotID = pilotDogmaItem.itemID
        self.ownerID = pilotID
        self.fittedItems[pilotID] = weakref.proxy(pilotDogmaItem)

    def UnregisterPilot(self, pilotDogmaItem):
        self.ownerID = None
        try:
            del self.fittedItems[pilotDogmaItem.itemID]
        except KeyError:
            self.dogmaLocation.LogError("ShipDogmaItem::Unregistering a pilot that isn't fitted", pilotDogmaItem.itemID)

    def UnregisterDrone(self, droneID):
        self.drones.remove(droneID)

    def _FlushEffects(self):
        ownerID = self.dogmaLocation.pilotsByShipID.get(self.itemID, None)
        if ownerID is not None:
            self.dogmaLocation.AddIgnoreOwnerEventsCount(ownerID)
        try:
            stackTraceCount = super(dogmax.ShipDogmaItem, self)._FlushEffects()
        finally:
            if ownerID is not None:
                self.dogmaLocation.DecreaseOwnerRequiredEventsCount(ownerID)

        return stackTraceCount

    def GetPilot(self):
        return self.dogmaLocation.pilotsByShipID.get(self.itemID, None)

    def RegisterDamage(self, damageByLayer):
        damageAttribs = self.dogmaLocation.dogmaStaticMgr.damageAttributes
        for attributeID, damages in damageByLayer:
            for damageAttributeID, damage in izip(damageAttribs, damages):
                self.damageByLayerByType[attributeID][damageAttributeID] += damage