import dogmax
import util
import weakref

class DroneDogmaItem(dogmax.BaseDogmaItem):
    __guid__ = 'dogmax.DroneDogmaItem'

    def GetEnvironmentInfo(self):
        return util.KeyVal(itemID=self.itemID, shipID=self.itemID, charID=self.ownerID, otherID=None, targetID=None, effectID=None)



    def SetLocation(self, locationID, locationDogmaItem, flagID):
        locationDogmaItem.RegisterDrone(self.itemID)
        newOwnerID = self.dogmaLocation.pilotsByShipID.get(locationID, None)
        if newOwnerID != self.ownerID:
            if self.ownerID is not None:
                self.dogmaLocation.UnregisterExternalForOwner(self.itemID, self.ownerID)
            self.ownerID = newOwnerID
            if newOwnerID is not None:
                self.dogmaLocation.RegisterExternalForOwner(self.itemID, newOwnerID)



    def UnsetLocation(self, locationDogmaItem):
        locationDogmaItem.UnregisterDrone(self.itemID)
        self.dogmaLocation.UnregisterExternalForOwner(self.itemID, self.ownerID)




