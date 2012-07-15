#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/dogma/dogmaItems/moduleDogmaItem.py
import dogmax
import util

class ModuleDogmaItem(dogmax.ShipFittableDogmaItem):
    __guid__ = 'dogmax.ModuleDogmaItem'

    def GetEnvironmentInfo(self):
        otherID = None
        locationDogmaItem = self.location
        if locationDogmaItem is not None:
            otherID = locationDogmaItem.subLocations.get(self.flagID, None)
            if otherID is None:
                other = self.dogmaLocation.GetChargeNonDB(locationDogmaItem.itemID, self.flagID)
                if other is not None:
                    otherID = other.itemID
        return util.KeyVal(itemID=self.itemID, shipID=self.GetShipID(), charID=self.GetPilot(), otherID=otherID, targetID=None, effectID=None)

    def IsOnline(self):
        return const.effectOnline in self.activeEffects