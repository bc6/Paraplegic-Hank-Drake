#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/planet/entities/extractorPin.py
import const
import planet
import math
import blue
EXTRACTOR_MAX_CYCLES = 120

class ExtractorPin(planet.BasePin):
    __guid__ = 'planet.ExtractorPin'
    __slots__ = ['products',
     'depositType',
     'depositQtyPerCycle',
     'depositQtyRemaining',
     'depositExpiryTime',
     'cycleTime',
     'installTime']

    def __init__(self, typeID):
        planet.BasePin.__init__(self, typeID)
        self.products = {}
        self.depositType = None
        self.depositQtyPerCycle = 0
        self.depositQtyRemaining = 0
        self.depositExpiryTime = None
        self.cycleTime = None
        self.installTime = None

    def GetCycleTime(self):
        return self.cycleTime

    def GetBaseCycleTime(self):
        return self.eventHandler.GetTypeAttribute(self.typeID, const.attributePinCycleTime)

    def GetBaseExtractionQty(self):
        return self.eventHandler.GetTypeAttribute(self.typeID, const.attributePinExtractionQuantity)

    def CanAccept(self, typeID, quantity):
        return 0

    def AddCommodity(self, typeID, quantity):
        return 0

    def Run(self, runTime):
        self.lastRunTime = runTime
        if self.depositType is None:
            return {}
        products = {}
        if self.IsActive():
            products[self.depositType] = self.depositQtyPerCycle if self.depositQtyPerCycle < self.depositQtyRemaining else self.depositQtyRemaining
            self.depositQtyRemaining -= products[self.depositType]
            if self.depositQtyRemaining <= 0:
                self.ClearDeposit()
        return products

    def CanInstallDeposit(self):
        if self.depositType is None:
            return True
        if self.depositQtyRemaining <= 0:
            return True
        return False

    def InstallDeposit(self, cycleTime, depositProductTypeID, depositQtyPerCycle, depositTotalQty, depositExpiryTime, lastRunTime = None, installTime = None):
        self.depositType = int(depositProductTypeID)
        self.depositQtyPerCycle = depositQtyPerCycle
        if self.depositQtyPerCycle <= 0:
            self.LogError('ownerID', self.ownerID, '| Extractor pin error, zero depositQtyPerCycle. Defaulting to', EXTRACTOR_MAX_CYCLES, 'cycles to extract')
            self.depositQtyPerCycle = int(math.ceil(depositTotalQty / EXTRACTOR_MAX_CYCLES))
        if depositTotalQty / self.depositQtyPerCycle > EXTRACTOR_MAX_CYCLES:
            self.LogError('ownerID', self.ownerID, '| Extractor pin error, number of cycles from', depositTotalQty, '/', self.depositQtyPerCycle, 'exceeds acceptable limit. Clamping to', EXTRACTOR_MAX_CYCLES, 'cycles.')
            depositTotalQty = self.depositQtyPerCycle * EXTRACTOR_MAX_CYCLES
        self.depositQtyRemaining = depositTotalQty
        self.depositExpiryTime = depositExpiryTime
        self.cycleTime = cycleTime
        self.SetState(planet.STATE_ACTIVE)
        if lastRunTime is not None:
            self.lastRunTime = lastRunTime
        else:
            self.lastRunTime = blue.os.GetWallclockTime()
        if installTime is not None:
            self.installTime = installTime
        else:
            self.installTime = self.lastRunTime
        return self.lastRunTime

    def ClearDeposit(self):
        self.depositType = None
        self.depositQtyPerCycle = 0
        self.depositQtyRemaining = 0
        self.depositExpiryTime = None
        self.installTime = None
        self.SetState(planet.STATE_IDLE)

    def CanActivate(self):
        if self.activityState < planet.STATE_IDLE:
            return False
        return self.depositType is not None and self.depositQtyRemaining > 0

    def IsActive(self):
        return self.depositType is not None and self.activityState > planet.STATE_IDLE

    def GetDepositInformation(self):
        if self.depositType is None:
            return
        return [self.id,
         int(self.depositType),
         self.cycleTime / const.SEC,
         self.depositQtyPerCycle,
         self.depositQtyRemaining,
         self.installTime,
         self.depositExpiryTime]

    def IsProducer(self):
        return True

    def IsExtractor(self):
        return True

    def GetProducts(self):
        if self.depositType is None:
            return {}
        else:
            return {self.depositType: self.depositQtyPerCycle}

    def GetTimeToDepletion(self):
        if self.depositType is not None and self.depositQtyPerCycle > 0:
            currCycle = blue.os.GetWallclockTime() - self.lastRunTime
            currCycleTimeLeft = self.cycleTime - currCycle
            numCyclesLeft = math.ceil((self.depositQtyRemaining - self.depositQtyPerCycle) / float(self.depositQtyPerCycle))
            totalTimeLeft = numCyclesLeft * self.cycleTime + currCycleTimeLeft
        else:
            totalTimeLeft = None
        return totalTimeLeft

    def GetTimeToExpiry(self):
        return self.depositExpiryTime - blue.os.GetWallclockTime()

    def Serialize(self, full = False):
        data = planet.BasePin.Serialize(self, full)
        data.cycleTime = self.cycleTime
        data.depositType = int(self.depositType) if self.depositType is not None else None
        data.depositQtyPerCycle = self.depositQtyPerCycle
        data.depositQtyRemaining = self.depositQtyRemaining
        data.depositExpiryTime = self.depositExpiryTime
        data.installTime = self.installTime
        return data

    def GetExtractionType(self):
        return int(self.eventHandler.GetTypeAttribute(self.typeID, const.attributeHarvesterType))

    def HasDifferingDeposit(self, otherPin):
        if self.installTime != otherPin.installTime:
            return True
        if self.GetCycleTime() != otherPin.GetCycleTime():
            return True
        if self.depositQtyPerCycle != otherPin.depositQtyPerCycle:
            return True
        if self.depositQtyRemaining != otherPin.depositQtyRemaining:
            return True
        if self.depositExpiryTime != otherPin.depositExpiryTime:
            return True
        return False