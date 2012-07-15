#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/dogma/dogmaItems/shipFittableDogmaItem.py
import dogmax
import weakref

class ShipFittableDogmaItem(dogmax.FittableDogmaItem):
    __guid__ = 'dogmax.ShipFittableDogmaItem'

    def __init__(self, dogmaLocation, item):
        super(ShipFittableDogmaItem, self).__init__(dogmaLocation, item)
        self.lastStopTime = None

    def SetLocation(self, locationID, locationDogmaItem, flagID):
        if locationDogmaItem is None:
            self.dogmaLocation.LogError('SetLocation called with no locationDogmaItem', self.itemID)
            return
        self.flagID = flagID
        oldData = self.GetLocationInfo()
        if self.IsValidFittingCategory(locationDogmaItem.categoryID):
            self.location = weakref.proxy(locationDogmaItem)
            if locationDogmaItem.categoryID == const.categoryShip:
                self.ownerID = self.dogmaLocation.pilotsByShipID.get(self.location.itemID, None)
            locationDogmaItem.RegisterFittedItem(self, flagID)
        else:
            self.dogmaLocation.LogError('SetLocation::ShipFittable item fitted to something other than ship')
        return oldData

    @property
    def ownerID(self):
        if self.location is None:
            return
        return self.location.ownerID

    @ownerID.setter
    def ownerID(self, inOwnerID):
        try:
            if self.location is not None:
                if self.location.ownerID != inOwnerID:
                    self.dogmaLocation.LogError('Setting ownerID on a ShipFittableDogmaItem to something that disagrees with its location!', self.location.ownerID, inOwnerID)
        except:
            pass

    def UnsetLocation(self, locationDogmaItem):
        self.location = None
        self.ownerID = None
        locationDogmaItem.UnregisterFittedItem(self)

    def GetShipID(self):
        if self.location is None:
            return
        return self.location.itemID

    def SetLastStopTime(self, lastStopTime):
        self.lastStopTime = lastStopTime

    def IsActive(self):
        for effectID in self.activeEffects:
            if effectID == const.effectOnline:
                continue
            effect = self.dogmaLocation.GetEffect(effectID)
            if effect.effectCategory in (const.dgmEffActivation, const.dgmEffTarget):
                return True

        return False

    def IsValidFittingCategory(self, categoryID):
        return categoryID == const.categoryShip

    def GetPilot(self):
        if self.location is not None:
            return self.location.GetPilot()