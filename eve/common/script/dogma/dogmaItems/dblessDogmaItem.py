import dogmax

class FakeItemFromDBLessDogmaItem(object):
    pass

class DBLessDogmaItem(dogmax.ChargeDogmaItem):
    __guid__ = 'dogmax.DBLessDogmaItem'

    def __init__(self, dogmaLocation, itemKey):
        item = FakeItemFromDBLessDogmaItem()
        item.itemID = itemKey
        item.typeID = itemKey[2]
        typeObj = cfg.invtypes.Get(item.typeID)
        item.groupID = typeObj.groupID
        item.categoryID = typeObj.categoryID
        super(DBLessDogmaItem, self).__init__(dogmaLocation, item)
        self.fittedItems = {}
        self.subLocations = {}



    def Load(self):
        self.attributes = attrs = {}



    def Unload(self):
        super(DBLessDogmaItem, self).Unload()
        self.dogmaLocation.RemoveSubLocationFromLocation(self.itemID)



    def SetLocation(self, locationID, locationDogmaItem, flagID):
        super(DBLessDogmaItem, self).SetLocation(locationID, locationDogmaItem, flagID)
        locationDogmaItem.SetSubLocation(self.itemID)
        locationDogmaItem.MarkDirty()



    def UnsetLocation(self, locationDogmaItem):
        super(DBLessDogmaItem, self).UnsetLocation(locationDogmaItem)
        locationDogmaItem.RemoveSubLocation(self.itemID)




