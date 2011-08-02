import const
import planet
import blue

class StoragePin(planet.BasePin):
    __guid__ = 'planet.StoragePin'
    __slots__ = []

    def OnStartup(self, id, ownerID, latitude, longitude):
        pass



    def GetCycleTime(self):
        return 0



    def GetCapacity(self):
        return cfg.invtypes.Get(self.typeID).capacity



    def IsStorage(self):
        return True



    def CanActivate(self):
        return False



    def CanRun(self, runTime = None):
        return False



    def GetNextTransferTime(self):
        if self.lastRunTime is not None:
            return self.lastRunTime



    def CanTransfer(self, commodities, transferTime = None):
        for (typeID, quantity,) in commodities.iteritems():
            if typeID not in self.contents:
                return False
            if quantity > self.contents[typeID]:
                return False

        tt = transferTime
        if transferTime is None:
            tt = blue.os.GetTime()
        nextTransferTime = self.GetNextTransferTime()
        if nextTransferTime is None or nextTransferTime <= tt:
            return True
        return False



    def ExecuteTransfer(self, runTime, expeditedTransferTime):
        self.lastRunTime = runTime + expeditedTransferTime



    def GetFreeSpace(self):
        capacity = self.GetCapacity()
        usedSpace = 0
        for (typeID, qty,) in self.contents.iteritems():
            usedSpace += cfg.invtypes.Get(typeID).volume * qty

        return capacity - usedSpace



exports = {'planet.StoragePin': StoragePin}

