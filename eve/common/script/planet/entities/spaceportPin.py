import const
import planet
import blue
import planetCommon

class SpaceportPin(planet.StoragePin):
    __guid__ = 'planet.SpaceportPin'
    __slots__ = ['lastLaunchTime']

    def __init__(self, typeID):
        planet.StoragePin.__init__(self, typeID)



    def OnStartup(self, id, ownerID, latitude, longitude):
        planet.StoragePin.OnStartup(self, id, ownerID, latitude, longitude)
        self.lastLaunchTime = None



    def IsSpaceport(self):
        return True



    def GetLaunchCycleTime(self):
        return 60 * SEC



    def GetNextLaunchTime(self):
        if self.lastLaunchTime is not None:
            return self.lastLaunchTime + self.GetLaunchCycleTime()



    def CanLaunch(self, commodities, launchTime = None):
        for (commodityTypeID, commodityQty,) in commodities.iteritems():
            if commodityTypeID not in self.contents or self.contents[commodityTypeID] < 1:
                return False

        lt = launchTime
        if launchTime is None:
            lt = blue.os.GetTime()
        nextLaunchTime = self.GetNextLaunchTime()
        if nextLaunchTime is None or nextLaunchTime <= lt:
            return True
        return False



    def FetchLaunchCommodities(self, commodities):
        commodsToLaunch = {}
        for (commodityTypeID, commodityQty,) in commodities.iteritems():
            qtyLaunched = int(self.RemoveCommodity(commodityTypeID, int(commodityQty)))
            if qtyLaunched is not None and qtyLaunched > 0:
                commodsToLaunch[commodityTypeID] = qtyLaunched

        return commodsToLaunch



    def CanImportCommodities(self, commodities):
        volume = planetCommon.GetCommodityTotalVolume(commodities)
        if self.capacityUsed + volume > self.GetCapacity():
            return False
        return True



    def Serialize(self, full = False):
        data = planet.StoragePin.Serialize(self, full)
        data.lastLaunchTime = self.lastLaunchTime
        return data



    def GetImportTax(self, commodities):
        importTaxRate = self.eventHandler.GetTypeAttribute(self.typeID, const.attributeImportTax)
        totalTax = 0.0
        for (typeID, qty,) in commodities.iteritems():
            multiplier = 1.0
            for attribute in cfg.dgmtypeattribs.get(typeID, []):
                if attribute.attributeID == const.attributeImportTaxMultiplier:
                    multiplier = attribute.value

            totalTax += qty * cfg.invtypes.Get(typeID).volume * importTaxRate * multiplier

        return totalTax



    def GetExportTax(self, commodities):
        exportTaxRate = self.eventHandler.GetTypeAttribute(self.typeID, const.attributeExportTax)
        totalTax = 0.0
        for (typeID, qty,) in commodities.iteritems():
            multiplier = 1.0
            for attribute in cfg.dgmtypeattribs.get(typeID, []):
                if attribute.attributeID == const.attributeExportTaxMultiplier:
                    multiplier = attribute.value

            totalTax += qty * cfg.invtypes.Get(typeID).volume * exportTaxRate * multiplier

        return totalTax



    def HasDifferingState(self, otherPin):
        if self.lastLaunchTime != getattr(otherPin, 'lastLaunchTime', None):
            return True
        return planet.BasePin.HasDifferingState(self, otherPin)



exports = {'planet.SpaceportPin': SpaceportPin}

