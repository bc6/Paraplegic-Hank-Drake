#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/dogma/dogmaItems/slimDogmaItem.py
RESISTANCEMATRIX = {const.attributeShieldCharge: [1,
                               1,
                               1,
                               1],
 const.attributeArmorDamage: [1,
                              1,
                              1,
                              1],
 const.attributeDamage: [1,
                         1,
                         1,
                         1]}

class SlimDogmaItem(object):
    __guid__ = 'dogmax.SlimDogmaItem'

    def __init__(self, dogmaLocation, item, attributes = None):
        self.dogmaLocation = dogmaLocation
        self.itemID = item.itemID
        self.typeID = item.typeID
        self.groupID = item.groupID
        self.categoryID = item.categoryID
        self.ownerID = None
        self.attributes = {}
        self.attributeCache = {}
        if attributes is not None:
            self.attributes.update(attributes)
            self.attributeCache.update(attributes)
        self.activeEffects = {}

    def CacheValue(self, attributeID, value):
        self.attributeCache[attributeID] = value

    def ClearCache(self, attributeID = None):
        if attributeID is None:
            self.attributeCache = {}
        else:
            try:
                del self.attributeCache[attributeID]
            except KeyError:
                pass

    def CanAttributeBeModified(self):
        return True

    def GetPilot(self):
        return None

    def GetValue(self, attributeID):
        try:
            return self.attributeCache[attributeID]
        except KeyError:
            return self.dogmaLocation.GetAttributeValue(self.itemID, attributeID)

    def GetResistanceMatrix(self):
        return RESISTANCEMATRIX