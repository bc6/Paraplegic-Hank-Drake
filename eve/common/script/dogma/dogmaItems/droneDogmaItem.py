import dogmax
import util
import weakref

class DroneDogmaItem(dogmax.BaseDogmaItem):
    __guid__ = 'dogmax.DroneDogmaItem'

    def GetEnvironmentInfo(self):
        return util.KeyVal(itemID=self.itemID, shipID=self.itemID, charID=self.ownerID, otherID=None, targetID=None, effectID=None)



    def SetLocation(self, locationID, locationDogmaItem, flagID):
        locationDogmaItem.RegisterDrone(self.itemID)
        self.ownerID = self.dogmaLocation.pilotsByShipID.get(locationID, None)
        if self.ownerID is not None:
            self.dogmaLocation.RegisterExternalForOwner(self.itemID, self.ownerID)



    def UnsetLocation(self, locationDogmaItem):
        locationDogmaItem.UnregisterDrone(self.itemID)
        self.dogmaLocation.UnregisterExternalForOwner(self.itemID, self.ownerID)




