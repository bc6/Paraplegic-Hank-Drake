#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/dogma/dogmaItems/controlTowerDogmaItem.py
import dogmax
import util

class ControlTowerDogmaItem(dogmax.LocationDogmaItem):
    __guid__ = 'dogmax.ControlTowerDogmaItem'

    def OnItemLoaded(self):
        self.dogmaLocation.FitItemToLocation(self.itemID, self.itemID, 0)
        super(ControlTowerDogmaItem, self).OnItemLoaded()

    def CanFitItem(self, dogmaItem, flagID):
        if dogmaItem.itemID == self.itemID:
            return True
        if dogmaItem.categoryID == const.categoryStructure and dogmaItem.groupID != const.groupControlTower:
            return True
        return False

    def GetEnvironmentInfo(self):
        return util.KeyVal(itemID=self.itemID, shipID=self.itemID, charID=None, otherID=None, targetID=None, effectID=None)