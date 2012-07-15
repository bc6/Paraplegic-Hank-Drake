#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/dogma/dogmaItems/fittableDogmaItem.py
import dogmax

class FittableDogmaItem(dogmax.BaseDogmaItem):
    __guid__ = 'dogmax.FittableDogmaItem'

    def Unload(self):
        super(FittableDogmaItem, self).Unload()
        if self.location and self.itemID in self.location.fittedItems:
            del self.location.fittedItems[self.itemID]