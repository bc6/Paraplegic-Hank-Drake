import dogmax

class FittableDogmaItem(dogmax.BaseDogmaItem):
    __guid__ = 'dogmax.FittableDogmaItem'

    def Unload(self):
        super(FittableDogmaItem, self).Unload()
        if self.location and self.itemID in self.location.fittedItems:
            del self.location.fittedItems[self.itemID]




