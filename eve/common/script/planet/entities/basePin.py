import const
import math
import blue
import weakref
import log
import util
import planetCommon
STATE_EDITMODE = -2
STATE_DISABLED = -1
STATE_IDLE = 0
STATE_ACTIVE = 1

class BasePin(object):
    __guid__ = 'planet.BasePin'
    __slots__ = ['id',
     'latitude',
     'longitude',
     'ownerID',
     'lastRunTime',
     'typeID',
     'activityState',
     'capacityUsed',
     'contents',
     'links',
     'eventHandler',
     'inEditMode',
     '__weakref__']

    def __init__(self, typeID):
        self.id = None
        self.latitude = None
        self.longitude = None
        self.ownerID = None
        self.lastRunTime = None
        self.typeID = typeID
        self.activityState = STATE_IDLE
        self.capacityUsed = 0
        self.contents = {}
        self.eventHandler = None
        self.inEditMode = False



    def Startup(self, id, eventHandler, ownerID, latitude, longitude, lastRunTime, state = None):
        self.id = id
        self.eventHandler = weakref.proxy(eventHandler)
        self.ownerID = ownerID
        self.lastRunTime = lastRunTime
        self.SetLatitude(latitude)
        self.SetLongitude(longitude)
        if state is not None:
            self.activityState = state
        self.OnStartup(id, ownerID, latitude, longitude)



    def IsInEditMode(self):
        return self.inEditMode



    def OnStartup(self, id, ownerID, latitude, longitude):
        pass



    def SetState(self, newState):
        self.activityState = newState



    def SetLatitude(self, latitude):
        self.latitude = min(math.pi, max(-math.pi, latitude))



    def SetLongitude(self, longitude):
        self.longitude = abs(longitude % (2 * math.pi))



    def GetDistance(self, otherInstallation):
        diffLong = self.longitude - otherInstallation.longitude
        cosDiffLong = math.cos(diffLong)
        cosMyLat = math.cos(self.latitude)
        sinMyLat = math.sin(self.latitude)
        cosOthLat = math.cos(otherInstallation.latitude)
        sinOthLat = math.sin(otherInstallation.latitude)
        nom1 = (cosMyLat + math.sin(diffLong)) ** 2
        nom2 = (cosMyLat * sinOthLat - sinMyLat * cosOthLat * cosDiffLong) ** 2
        denom = sinMyLat * sinOthLat + cosMyLat * cosOthLat * cosDiffLong
        return math.atan2(math.sqrt(nom1 + nom2), denom)



    def SetContents(self, newContents):
        self.contents = dict(newContents)
        self.capacityUsed = 0
        for (typeID, qty,) in self.contents.iteritems():
            self.capacityUsed += qty * cfg.invtypes.Get(typeID).volume




    def _AddCommodity(self, typeID, quantity):
        quantityToAdd = self.CanAccept(typeID, quantity)
        if quantityToAdd < 1:
            return 0
        if self.GetCapacity() is not None:
            newTypeObj = cfg.invtypes.Get(typeID)
            self.capacityUsed += quantityToAdd * newTypeObj.volume
        if typeID not in self.contents:
            self.contents[typeID] = quantityToAdd
        else:
            self.contents[typeID] += quantityToAdd
        return quantityToAdd



    def _RemoveCommodity(self, typeID, quantity):
        if typeID not in self.contents:
            return 0
        qtyRemoved = 0
        if self.contents[typeID] <= quantity:
            qtyRemoved = self.contents[typeID]
            del self.contents[typeID]
        else:
            qtyRemoved = quantity
            self.contents[typeID] -= qtyRemoved
        if self.GetCapacity() is not None:
            self.capacityUsed = max(0, self.capacityUsed - cfg.invtypes.Get(typeID).volume * qtyRemoved)
        return qtyRemoved



    def CanAccept(self, typeID, quantity):
        if self.activityState < STATE_IDLE:
            return 0
        if self.GetCapacity() is not None:
            newTypeObj = cfg.invtypes.Get(typeID)
            newVolume = newTypeObj.volume * quantity
            capacityRemaining = max(0, self.GetCapacity() - self.capacityUsed)
            if newVolume > capacityRemaining or quantity == -1:
                return int(capacityRemaining / newTypeObj.volume)
            else:
                return quantity
        else:
            return max(0, quantity)



    def CanRemove(self, typeID, quantity):
        if self.activityState < STATE_IDLE:
            return 0
        if typeID not in self.contents:
            return 0
        return min(self.contents[typeID], quantity)



    def AddCommodity(self, typeID, quantity):
        return self._AddCommodity(typeID, quantity)



    def RemoveCommodity(self, typeID, quantity):
        return self._RemoveCommodity(typeID, quantity)



    def CanLinkTo(self, linkToPin):
        if linkToPin == self or linkToPin.id == self.id:
            return False
        return True



    def CanActivate(self):
        if self.activityState < STATE_IDLE:
            return False
        return True



    def GetNextRunTime(self):
        try:
            if self.lastRunTime is not None:
                return self.lastRunTime + self.GetCycleTime()
        except Exception:
            log.LogException('GetNextRunTime, GetCycleTime unexpectedly gave us None', self.id, self.typeID)



    def CanRun(self, runTime = None):
        if not self.CanActivate():
            return False
        rt = runTime
        if runTime is None:
            rt = blue.os.GetWallclockTime()
        nextRunTime = self.GetNextRunTime()
        if nextRunTime is None or nextRunTime <= rt:
            return True
        return False



    def GetContents(self):
        return self.contents.copy()



    def Run(self, runTime):
        self.lastRunTime = runTime
        self.activityState = min(self.activityState, STATE_IDLE)
        return {}



    def IsActive(self):
        return self.activityState > STATE_IDLE



    def IsJunction(self):
        return False



    def IsStorage(self):
        return False



    def IsConsumer(self):
        return False



    def GetConsumables(self):
        return {}



    def IsSpaceport(self):
        return False



    def IsCommandCenter(self):
        return False



    def IsExtractor(self):
        return False



    def IsProcessor(self):
        return False



    def IsProducer(self):
        return False



    def GetProducts(self):
        return {}



    def GetProductMaxOutput(self):
        return self.GetProducts()



    def Serialize(self, full = False):
        data = util.KeyVal(id=self.id, latitude=self.latitude, longitude=self.longitude, ownerID=self.ownerID, lastRunTime=self.lastRunTime, typeID=self.typeID, contents=self.contents.copy(), state=self.activityState)
        return data



    def GetCycleTime(self):
        return 60 * SEC



    def GetCapacity(self):
        return None



    def GetPowerUsage(self):
        return self.eventHandler.GetTypeAttribute(self.typeID, const.attributePowerLoad)



    def GetPowerOutput(self):
        return self.eventHandler.GetTypeAttribute(self.typeID, const.attributePowerOutput)



    def GetCpuUsage(self):
        return self.eventHandler.GetTypeAttribute(self.typeID, const.attributeCpuLoad)



    def GetCpuOutput(self):
        return self.eventHandler.GetTypeAttribute(self.typeID, const.attributeCpuOutput)



    def GetOutputVolumePerHour(self):
        cycleTime = self.GetCycleTime()
        if not self.IsProducer() or not cycleTime:
            return 0.0
        volumePerCycle = planetCommon.GetCommodityTotalVolume(self.GetProducts())
        volumePerHour = planetCommon.GetBandwidth(volumePerCycle, cycleTime)
        return volumePerHour



    def HasDifferingContents(self, otherPinContents):
        for (typeID, qty,) in self.contents.iteritems():
            if typeID not in otherPinContents or otherPinContents[typeID] != qty:
                return True

        for (typeID, qty,) in otherPinContents.iteritems():
            if typeID not in self.contents or self.contents[typeID] != qty:
                return True

        return False



    def HasDifferingState(self, otherPin):
        if self.lastRunTime != otherPin.lastRunTime:
            return True
        if self.activityState != otherPin.activityState:
            return True
        return False



    def LogInfo(self, *args, **keywords):
        self.eventHandler.LogInfo(self.id, ' | ', *args)



    def LogWarn(self, *args, **keywords):
        self.eventHandler.LogWarn(self.id, ' | ', *args)



    def LogError(self, *args, **keywords):
        self.eventHandler.LogError(self.id, ' | ', *args)



    def LogNotice(self, *args, **keywords):
        self.eventHandler.LogNotice(self.id, ' | ', *args)



exports = {'planet.BasePin': BasePin,
 'planet.STATE_EDITMODE': STATE_EDITMODE,
 'planet.STATE_DISABLED': STATE_DISABLED,
 'planet.STATE_IDLE': STATE_IDLE,
 'planet.STATE_ACTIVE': STATE_ACTIVE}

