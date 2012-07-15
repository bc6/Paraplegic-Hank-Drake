#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/planet/baseColony.py
from __future__ import with_statement
import bluepy
from planet import SurfacePoint
import weakref
import log
import planetCommon
import blue
import util
import blue.heapq as heapq
import types
import math
import localization
from PlanetResources import builder

class BaseColony:
    __guid__ = 'planet.BaseColony'
    __name__ = 'BaseColony'

    def __init__(self, planet, ownerID):
        self.ownerID = ownerID
        self.planet = weakref.proxy(planet)
        self.planetBroker = weakref.proxy(planet.planetBroker)
        self.planetID = planet.planetID
        self.Init()

    def Init(self):
        self.colonyData = None
        self.simQueue = []
        self.currentSimTime = None
        self.temporaryIDMap = {}

    def RegisterTemporaryID(self, oldID, newID):
        self.temporaryIDMap[oldID] = newID

    def IsTemporaryID(self, id):
        return type(id) is types.TupleType

    def GetRealIDFromTemporaryID(self, oldID):
        return self.temporaryIDMap.get(oldID, None)

    def ClearTemporaryIDs(self):
        self.temporaryIDMap = {}

    def GetColonyData(self):
        return self.colonyData

    def SetColonyData(self, newData):
        self.colonyData = newData
        newData.SetEventHandler(self)
        self.simQueue = []
        self.currentSimTime = None
        self.RecalculateCurrentSimTime()

    def GetPin(self, pinID):
        if self.colonyData is None:
            return
        return self.colonyData.GetPin(pinID)

    def GetLink(self, endpoint1, endpoint2):
        if self.colonyData is None:
            return
        if endpoint1 > endpoint2:
            endpoint1, endpoint2 = endpoint2, endpoint1
        return self.colonyData.GetLink(endpoint1, endpoint2)

    def GetRoute(self, routeID):
        if self.colonyData is None:
            return
        return self.colonyData.GetRoute(routeID)

    def Serialize(self):
        if self.colonyData is None:
            return
        data = self.colonyData.Serialize()
        data.currentSimTime = self.currentSimTime
        return data

    def GetPlanetRadius(self):
        return self.planet.radius

    def GetResourceType(self, typeID):
        return self.planet.GetResourceHarmonic(typeID)

    def AdvanceSimulation(self, advanceTime):
        if self.currentSimTime is None:
            self.LogWarn('AdvanceSimulation :: Unable to advance, currentSimTime is None')
            return
        self.currentSimTime += advanceTime
        if self.colonyData is not None:
            for pin in self.colonyData.pins.itervalues():
                if pin.lastRunTime is not None:
                    pin.lastRunTime += advanceTime

    @bluepy.TimedFunction('BaseColony::SchedulePin')
    def SchedulePin(self, pin):
        nextRunTime = pin.GetNextRunTime()
        for evalTime, evalPinID in self.simQueue:
            if evalPinID == pin.id:
                if nextRunTime is None or nextRunTime < evalTime:
                    self.LogInfo('SchedulePin::Rescheduling pin', pin.id, 'from', evalTime, 'to', self.currentSimTime)
                    self.simQueue.remove((evalTime, evalPinID))
                else:
                    return

        if nextRunTime is None or nextRunTime < self.currentSimTime:
            self.AddTimer(pin.id, self.currentSimTime)
        else:
            self.AddTimer(pin.id, nextRunTime)

    def PrimeSimulation(self, simEndTime, clearQueue = True):
        if clearQueue:
            self.simQueue = []
        if self.colonyData is None:
            return
        for pin in self.colonyData.pins.itervalues():
            if pin.CanRun(simEndTime):
                self.SchedulePin(pin)

    def RecalculateCurrentSimTime(self):
        if self.colonyData is None or len(self.colonyData.pins) < 1:
            self.currentSimTime = blue.os.GetWallclockTime()
            return
        for pin in self.colonyData.pins.itervalues():
            if not pin.IsStorage() and pin.lastRunTime is not None:
                if self.currentSimTime is None:
                    self.currentSimTime = pin.lastRunTime
                elif pin.lastRunTime < self.currentSimTime:
                    self.currentSimTime = pin.lastRunTime

        if self.currentSimTime is None:
            self.currentSimTime = blue.os.GetWallclockTime()

    def AddTimer(self, pinID, runTime):
        self.LogInfo('AddTimer :: pinID', pinID, 'at', runTime)
        heapq.heappush(self.simQueue, (runTime, pinID))

    def RunSimulation(self, runSimUntil = None, beNice = True):
        if self.colonyData is None:
            raise RuntimeError('Attempting to run simulation on a colony without attached colonyData')
        with self.planetBroker.LockedService(self.ownerID):
            if self.currentSimTime is None:
                self.RecalculateCurrentSimTime()
            if self.currentSimTime is None:
                raise RuntimeError('CurrentSimTime is none for character', self.ownerID, '. This is a fatal error that can cause infinite looping.')
            simEndTime = runSimUntil if runSimUntil is not None else blue.os.GetWallclockTime()
            with bluepy.Timer('BaseColony::PrimeSimulation'):
                self.PrimeSimulation(simEndTime)
            with bluepy.Timer('BaseColony::RunSimulation'):
                while len(self.simQueue) > 0:
                    simTime, simPinID = heapq.heappop(self.simQueue)
                    if simTime > simEndTime:
                        break
                    self.currentSimTime = simTime
                    simPin = self.GetPin(simPinID)
                    if simPin is None:
                        log.LogTraceback('Unable to find scheduled pin! This should never happen!')
                        continue
                    with bluepy.TimerPush('EvaluatePin::' + simPin.__guid__):
                        if not simPin.CanRun(self.currentSimTime):
                            continue
                        self.EvaluatePin(simPin)
                    if beNice:
                        blue.pyos.BeNice()

                self.currentSimTime = simEndTime
            return simEndTime

    def EvaluatePin(self, pin):
        self.LogInfo('EvaluatePin ::', pin.id, '(', pin.typeID, ') at', self.currentSimTime)
        if not pin.CanActivate() and not pin.IsActive():
            return
        self.LogInfo('EvaluatePin ::', pin.id, '(', pin.typeID, ') Running pin')
        with bluepy.TimerPush('Run'):
            commods = pin.Run(self.currentSimTime)
        if pin.IsConsumer():
            self.LogInfo('EvaluatePin :: Consumer detected, routing inputs', pin.id)
            with bluepy.TimerPush('RouteCommodityInput'):
                self.RouteCommodityInput(pin)
        if pin.IsActive() or pin.CanActivate():
            self.LogInfo('EvaluatePin ::', pin.id, 'Scheduling pin')
            self.SchedulePin(pin)
        if len(commods) == 0:
            return
        self.LogInfo('EvaluatePin ::', pin.id, 'Routing outputs')
        with bluepy.TimerPush('RouteCommodityOutput'):
            self.RouteCommodityOutput(pin, commods)
        self.LogInfo('EvaluatePin ::', pin.id, 'Done')

    def StimulateIdlePin(self, pin):
        if pin is None:
            raise RuntimeError('Cannot stimulate a None pin')
        if pin.IsStorage():
            self.RouteCommodityOutput(pin, pin.GetContents())
        if pin.IsConsumer():
            pin.hasReceivedInputs = True
        if not pin.IsActive() and pin.CanActivate():
            self.SchedulePin(pin)

    def InstallSchematicForPin(self, charID, pinID, schematicID, skipSimulation = False):
        if self.colonyData is None:
            raise RuntimeError('Unable to perform schematic installation - no colony data')
        try:
            schematicID = int(schematicID)
        except ValueError:
            log.LogException('Failed to convert schematicID %s to int' % schematicID)
            raise 

        processPin = self.GetPin(pinID)
        if not processPin:
            raise RuntimeError('Unable to install schematic - cannot find pin')
        processPin.InstallSchematic(schematicID)
        if not skipSimulation:
            self.StimulateIdlePin(processPin)
        self.OnSchematicInstalled(pinID, schematicID)

    def InstallProgram(self, charID, pinID, programType, cycleTime, expiryTime, qtyPerCycle, headRadius):
        if self.colonyData is None:
            raise RuntimeError('Unable to perform program installation - no colony data')
        ecuPin = self.GetPin(pinID)
        if not ecuPin or cfg.invtypes.Get(ecuPin.typeID).groupID != const.groupExtractionControlUnitPins:
            raise RuntimeError('Unable to install program - pin does not exist or is not an ECU')
        lastRunTime = ecuPin.InstallProgram(programType, cycleTime, expiryTime, qtyPerCycle, headRadius)
        self.OnProgramInstalled(pinID)
        return lastRunTime

    def RouteCommodityOutput(self, sourcePin, commodities):
        if self.colonyData is None:
            raise RuntimeError('No colony data attached - cannot route commodity output')
        pinsReceivingCommodities = {}
        done = False
        for isStorageRoutes, listOfRoutes in enumerate(self.colonyData.GetSortedRoutesForPin(sourcePin.id, commodities)):
            if done:
                break
            while listOfRoutes:
                dummy, (destID, commodityTypeID, qty) = heapq.heappop(listOfRoutes)
                maxAmount = None
                if isStorageRoutes:
                    maxAmount = math.ceil(float(commodities.get(commodityTypeID, 0)) / (len(listOfRoutes) + 1))
                typeID, qty = self.TransferCommodities(sourcePin.id, destID, commodityTypeID, qty, commodities, maxAmount=maxAmount)
                if typeID in commodities:
                    commodities[typeID] -= qty
                    if commodities[typeID] <= 0:
                        del commodities[typeID]
                if qty > 0:
                    if destID not in pinsReceivingCommodities:
                        pinsReceivingCommodities[destID] = {}
                    if typeID not in pinsReceivingCommodities[destID]:
                        pinsReceivingCommodities[destID][typeID] = 0
                    pinsReceivingCommodities[destID][typeID] += qty
                if len(commodities) <= 0:
                    done = True
                    break

        for receivingPinID, commodsAdded in pinsReceivingCommodities.iteritems():
            receivingPin = self.GetPin(receivingPinID)
            if receivingPin.IsConsumer():
                self.SchedulePin(receivingPin)
            if not sourcePin.IsStorage() and receivingPin.IsStorage():
                self.LogInfo('RouteCommodityOutput :: Redistributing added commods', commodsAdded, 'from', sourcePin.id, 'via', receivingPin.id)
                self.RouteCommodityOutput(receivingPin, commodsAdded)

    def RouteCommodityInput(self, destinationPin):
        if self.colonyData is None:
            raise RuntimeError('No colony data attached - cannot route commodity input')
        routesToEvaluate = self.colonyData.GetDestinationRoutesForPin(destinationPin.id)
        for routeID in routesToEvaluate:
            route = self.colonyData.GetRoute(routeID)
            sourcePinID = route.GetSourcePinID()
            sourcePin = self.GetPin(sourcePinID)
            if sourcePin is None:
                self.LogWarn('Route', routeID, 'has nonexistent source pin', sourcePinID)
                continue
            if not sourcePin.IsStorage():
                continue
            storedCommods = sourcePin.GetContents()
            if len(storedCommods) < 1:
                continue
            self.LogInfo('RouteCommodityInput :: Routing', storedCommods, 'from', route.GetSourcePinID(), 'to', route.GetDestinationPinID())
            self.ExecuteRoute(routeID, storedCommods)

    def ExecuteRoute(self, routeID, commodities):
        if self.colonyData is None:
            raise RuntimeError('Unable to execute route - no colony data')
        route = self.colonyData.GetRoute(routeID)
        if not route:
            self.LogError('ExecuteRoute :: Cannot find route', routeID)
            return (0, 0)
        sourceID, destID, typeID, qty = route.GetRoutingInfo()
        return self.TransferCommodities(sourceID, destID, typeID, qty, commodities)

    def TransferCommodities(self, sourcePinID, destPinID, typeID, qty, commodities, maxAmount = None):
        if self.colonyData is None:
            raise RuntimeError('Unable to execute route - no colony data')
        sourcePin = self.GetPin(sourcePinID)
        if not sourcePin:
            raise RuntimeError('Unable to find pin', sourcePinID)
        commodsToPush = {}
        if typeID not in commodities:
            return (0, 0)
        amtToMove = min(commodities[typeID], qty)
        if maxAmount is not None:
            amtToMove = min(maxAmount, amtToMove)
        if amtToMove <= 0:
            return (0, 0)
        destPin = self.GetPin(destPinID)
        if not destPin:
            raise RuntimeError('Unable to find pin', destPinID)
        amtMoved = destPin.AddCommodity(typeID, amtToMove)
        if sourcePin.IsStorage():
            sourcePin.RemoveCommodity(typeID, amtMoved)
        return (typeID, amtMoved)

    def ExecuteExpeditedTransfer(self, sourceID, destinationID, commodities, minBandwidth, runTime):
        if self.colonyData is None:
            raise RuntimeError('Unable to execute expedited transfer - no colony data')
        sourcePin = self.GetPin(sourceID)
        if not sourcePin:
            raise RuntimeError('Unable to find pin', sourceID)
        if not sourcePin.IsStorage():
            raise RuntimeError('Expedited transfer attempted from non-storage pin! This is bad!', sourceID)
        commodsToPush = {}
        contents = sourcePin.GetContents()
        for typeID, qty in commodities.iteritems():
            if typeID not in contents:
                self.LogInfo('Expedited transfer unable to transfer type', typeID, 'as this was not in the commodities available')
                continue
            commodsToPush[typeID] = int(min(contents[typeID], qty))
            if commodsToPush[typeID] < 1:
                del commodsToPush[typeID]

        if len(commodsToPush) < 1:
            return
        destPin = self.GetPin(destinationID)
        if not destPin:
            raise RuntimeError('Unable to find pin', destinationID)
        commodsMoved = {}
        for typeID, quantity in commodsToPush.iteritems():
            commodsMoved[typeID] = destPin.AddCommodity(typeID, quantity)

        for typeID, quantity in commodsMoved.iteritems():
            sourcePin.RemoveCommodity(typeID, quantity)

        sourcePin.ExecuteTransfer(runTime, planetCommon.GetExpeditedTransferTime(minBandwidth, commodsMoved))
        self.StimulateIdlePin(destPin)

    def ValidateCreatePin(self, charID, typeID, latitude, longitude):
        if self.colonyData is None:
            raise RuntimeError('Unable to validate pin creation - no colony data')
        self.PreValidateCreatePin(charID, typeID, latitude, longitude)
        typeObj = cfg.invtypes.Get(typeID)
        if typeObj.groupID == const.groupCommandPins:
            if self.colonyData.commandPin is not None:
                raise UserError('CannotBuildMultipleCommandPins')
        elif self.colonyData.commandPin is None:
            raise UserError('CannotManagePlanetWithoutCommandCenter')
        t = planetCommon.GetPinEntityType(typeID)
        if t is None:
            raise UserError('InvalidPinType')
        planetTypeRestriction = self.GetTypeAttribute(typeID, const.attributePlanetRestriction)
        if planetTypeRestriction is not None and planetTypeRestriction != self.planet.GetPlanetTypeID():
            raise UserError('CannotCreatePinWrongPlanetType')
        cpuUsage = self.GetTypeAttribute(typeID, const.attributeCpuLoad)
        cpuOutput = self.GetTypeAttribute(typeID, const.attributeCpuOutput)
        powerUsage = self.GetTypeAttribute(typeID, const.attributePowerLoad)
        powerOutput = self.GetTypeAttribute(typeID, const.attributePowerOutput)
        if cpuOutput <= 0 and cpuUsage + self.colonyData.GetColonyCpuUsage() > self.colonyData.GetColonyCpuSupply():
            raise UserError('CannotAddToColonyCPUUsageExceeded', {'typeName': cfg.invtypes.Get(typeID).name})
        if powerOutput <= 0 and powerUsage + self.colonyData.GetColonyPowerUsage() > self.colonyData.GetColonyPowerSupply():
            raise UserError('CannotAddToColonyPowerUsageExceeded', {'typeName': cfg.invtypes.Get(typeID).name})
        self.PostValidateCreatePin(charID, typeID, latitude, longitude)

    def PreValidateCreatePin(self, charID, typeID, latitude, longitude):
        pass

    def PostValidateCreatePin(self, charID, typeID, latitude, longitude):
        pass

    def ValidateRemovePin(self, charID, pinID):
        self.PreValidateRemovePin(charID, pinID)
        if self.colonyData is None:
            raise RuntimeError('Unable to validate pin removal - no colony data')
        if pinID not in self.colonyData.pins:
            raise UserError('PinDoesNotExist')
        self.PostValidateRemovePin(charID, pinID)

    def PreValidateRemovePin(self, charID, pinID):
        pass

    def PostValidateRemovePin(self, charID, pinID):
        pass

    def ValidateCreateLink(self, charID, endpoint1ID, endpoint2ID, linkTypeID, level = 0):
        if self.colonyData is None:
            raise RuntimeError('Unable to validate link creation - no colony data')
        if endpoint1ID > endpoint2ID:
            endpoint1ID, endpoint2ID = endpoint2ID, endpoint1ID
        self.PreValidateCreateLink(charID, endpoint1ID, endpoint2ID, linkTypeID, level)
        if self.colonyData.commandPin is None:
            raise UserError('CannotManagePlanetWithoutCommandCenter')
        link = self.GetLink(endpoint1ID, endpoint2ID)
        if link is not None:
            raise UserError('LinkAlreadyExists')
        pin1 = self.GetPin(endpoint1ID)
        pin2 = self.GetPin(endpoint2ID)
        if not pin1 or not pin2:
            raise UserError('PinDoesNotExist')
        if pin1.ownerID != charID or pin2.ownerID != charID:
            raise UserError('CanOnlyManageOwnPins')
        if pin1 == pin2 or endpoint1ID == endpoint2ID:
            raise UserError('CannotLinkPinsToThemselves')
        if not pin1.CanLinkTo(pin2) or not pin2.CanLinkTo(pin1):
            raise UserError('CannotLinkPins', {'parent': (TYPEID, pin1.typeID),
             'child': (TYPEID, pin2.typeID)})
        linkLength = planetCommon.GetDistanceBetweenPins(pin1, pin2, self.GetPlanetRadius())
        params = planetCommon.GetUsageParametersForLinkType(linkTypeID)
        addlCpuUsage = planetCommon.GetCpuUsageForLink(linkTypeID, linkLength, level, params)
        addlPowerUsage = planetCommon.GetPowerUsageForLink(linkTypeID, linkLength, level, params)
        if addlCpuUsage + self.colonyData.GetColonyCpuUsage() > self.colonyData.GetColonyCpuSupply():
            raise UserError('CannotAddToColonyCPUUsageExceeded', {'typeName': cfg.invtypes.Get(linkTypeID).name})
        if addlPowerUsage + self.colonyData.GetColonyPowerUsage() > self.colonyData.GetColonyPowerSupply():
            raise UserError('CannotAddToColonyPowerUsageExceeded', {'typeName': cfg.invtypes.Get(linkTypeID).name})
        self.PostValidateCreateLink(charID, endpoint1ID, endpoint2ID, linkTypeID, level)

    def PreValidateCreateLink(self, charID, endpoint1ID, endpoint2ID, linkTypeID, level):
        pass

    def PostValidateCreateLink(self, charID, endpoint1ID, endpoint2ID, linkTypeID, level):
        pass

    def ValidateRemoveLink(self, charID, endpoint1, endpoint2):
        if self.colonyData is None:
            raise RuntimeError('Unable to validate link removal - no colony data')
        if endpoint1 > endpoint2:
            endpoint1, endpoint2 = endpoint2, endpoint1
        if (endpoint1, endpoint2) not in self.colonyData.links:
            raise UserError('LinkDoesNotExist')

    def ValidateCreateRoute(self, charID, path, typeID, quantity):
        if self.colonyData is None:
            raise RuntimeError('Unable to validate routing path - no colony data')
        self.PreValidateCreateRoute(path, typeID, quantity)
        if typeID is None or quantity < 1:
            raise UserError('CreateRouteWithoutCommodities')
        if len(path) < 2:
            raise UserError('CreateRouteTooShort')
        if len(path) - 2 > planetCommon.MAX_WAYPOINTS:
            raise UserError('CannotRouteTooManyWaypoints')
        sourcePin = self.GetPin(path[0])
        destinationPin = self.GetPin(path[-1])
        if sourcePin.IsStorage() and not destinationPin.IsConsumer():
            raise UserError('CannotRouteStorageMustGoToConsumer')
        if not destinationPin.IsConsumer() and not destinationPin.IsStorage():
            raise UserError('CannotRouteDestinationWillNotAccept')
        if sourcePin.IsProducer():
            routes = self.colonyData.GetSourceRoutesForPin(sourcePin.id)
            totalCommodsUsed = {}
            for route in routes:
                routeTypeID = route.GetType()
                if routeTypeID not in totalCommodsUsed:
                    totalCommodsUsed[routeTypeID] = route.GetQuantity()
                else:
                    totalCommodsUsed[routeTypeID] += route.GetQuantity()

            sourceProducts = sourcePin.GetProductMaxOutput()
            if typeID not in sourceProducts:
                raise UserError('CreateRouteCommodityNotProduced', {'typeName': (TYPEID, typeID)})
            if typeID not in totalCommodsUsed:
                totalCommodsUsed[typeID] = quantity
            else:
                totalCommodsUsed[typeID] += quantity
            if totalCommodsUsed[typeID] > sourceProducts[typeID]:
                raise UserError('CreateRouteCommodityProductionTooSmall', {'typeName': (TYPEID, typeID)})
        if destinationPin.IsConsumer():
            consumables = destinationPin.GetConsumables()
            if typeID not in consumables:
                raise UserError('CreateRouteDestinationCannotAcceptCommodity', {'typeName': (TYPEID, typeID)})
        additionalBandwidth = cfg.invtypes.Get(typeID).volume * quantity
        pinCycleTime = 0.0
        if sourcePin.IsProducer():
            pinCycleTime = sourcePin.GetCycleTime()
        elif sourcePin.IsStorage() and destinationPin.IsConsumer():
            pinCycleTime = destinationPin.GetCycleTime()
        else:
            pinCycleTime = max(sourcePin.GetCycleTime(), destinationPin.GetCycleTime())
        if pinCycleTime is not None and pinCycleTime != 0.0:
            additionalBandwidth = planetCommon.GetBandwidth(additionalBandwidth, pinCycleTime)
        else:
            self.LogWarn('ValidateCreateRoute :: Calculating bandwidth on path', path, 'with invalid source/dest pins')
        prevID = None
        for pinID in path:
            pin = self.GetPin(pinID)
            if not pin:
                raise UserError('RouteFailedValidationPinDoesNotExist')
            if pin.ownerID != charID:
                raise UserError('RouteFailedValidationPinNotYours')
            if prevID is None:
                prevID = pinID
                continue
            link = self.GetLink(prevID, pinID)
            if link is None:
                raise UserError('RouteFailedValidationLinkDoesNotExist')
            if not link.CanRouteBandwidth(additionalBandwidth):
                raise UserError('RouteFailedValidationCannotRouteCommodities')
            prevID = pinID

        self.PostValidateCreateRoute(path, typeID, quantity)

    def PreValidateCreateRoute(self, path, typeID, quantity):
        pass

    def PostValidateCreateRoute(self, path, typeID, quantity):
        pass

    def ValidateRemoveRoute(self, charID, routeID):
        if self.colonyData is None:
            raise RuntimeError('Unable to validate route removal - no colony data')
        if routeID not in self.colonyData.routes:
            raise UserError('RouteDoesNotExist')

    def ValidateInstallSchematic(self, charID, pinID, schematicID):
        if self.colonyData is None:
            raise RuntimeError('Unable to validate schematic installation - no colony data')
        try:
            schematicID = int(schematicID)
        except ValueError:
            log.LogException('Failed to convert schematicID %s to int' % schematicID)
            raise 

        self.PreValidateInstallSchematic(charID, pinID, schematicID)
        processPin = self.GetPin(pinID)
        if not processPin:
            raise UserError('PinDoesNotExist')
        if processPin.ownerID != charID:
            raise UserError('CanOnlyManageOwnPins')
        if not callable(getattr(processPin, 'InstallSchematic', None)):
            raise UserError('CannotAssignSchematicToPinType')
        if schematicID not in cfg.schematics:
            raise UserError('InvalidSchematic')
        schematicObj = cfg.schematics.Get(schematicID)
        if not schematicObj:
            raise UserError('InvalidSchematic')
        self.PostValidateInstallSchematic(charID, pinID, schematicID)

    def PreValidateInstallSchematic(self, charID, pinID, schematicID):
        pass

    def PostValidateInstallSchematic(self, charID, pinID, schematicID):
        pass

    def ValidateSetLinkLevel(self, charID, endpoint1ID, endpoint2ID, newLevel):
        if self.colonyData is None:
            raise RuntimeError('Unable to validate link level - no colony data')
        if endpoint1ID > endpoint2ID:
            endpoint1ID, endpoint2ID = endpoint2ID, endpoint1ID
        self.PreValidateSetLinkLevel(charID, endpoint1ID, endpoint2ID, newLevel)
        link = self.colonyData.GetLink(endpoint1ID, endpoint2ID)
        if not link:
            raise UserError('PinDoesNotExist')
        if newLevel > planetCommon.LINK_MAX_UPGRADE:
            raise UserError('CannotUpgradeLinkAlreadyMaxed', {'typeName': cfg.invtypes.Get(link.typeID).name})
        if newLevel > link.level:
            params = planetCommon.GetUsageParametersForLinkType(link.typeID)
            oldCpu = planetCommon.GetCpuUsageForLink(link.typeID, link.GetDistance(), link.level, params)
            newCpu = planetCommon.GetCpuUsageForLink(link.typeID, link.GetDistance(), newLevel, params)
            oldPower = planetCommon.GetPowerUsageForLink(link.typeID, link.GetDistance(), link.level, params)
            newPower = planetCommon.GetPowerUsageForLink(link.typeID, link.GetDistance(), newLevel, params)
            cpuDelta = newCpu - oldCpu
            powerDelta = newPower - oldPower
            if cpuDelta + self.colonyData.GetColonyCpuUsage() > self.colonyData.GetColonyCpuSupply():
                raise UserError('CannotAddToColonyCPUUsageExceeded', {'typeName': cfg.invtypes.Get(link.typeID).name})
            if powerDelta + self.colonyData.GetColonyPowerUsage() > self.colonyData.GetColonyPowerSupply():
                raise UserError('CannotAddToColonyPowerUsageExceeded', {'typeName': cfg.invtypes.Get(link.typeID).name})
        self.PostValidateSetLinkLevel(charID, endpoint1ID, endpoint2ID, newLevel)

    def ValidateCommandCenterUpgrade(self, level):
        self.PreValidateCommandCenterUpgrade(level)
        if self.colonyData is None:
            raise RuntimeError('Unable to validate command center upgrade - no colony data')
        if level <= self.colonyData.level:
            raise RuntimeError("We can't downgrade")
        if level > planetCommon.GetMaxCommandUpgradeLevel():
            raise RuntimeError('Trying to upgrade past maximum level')
        self.PostValidateCommandCenterUpgrade(level)

    def PostValidateCommandCenterUpgrade(self, level):
        pass

    def PreValidateCommandCenterUpgrade(self, level):
        pass

    def PreValidateSetLinkLevel(self, charID, endpoint1ID, endpoint2ID, newLevel):
        pass

    def PostValidateSetLinkLevel(self, charID, endpoint1ID, endpoint2ID, newLevel):
        pass

    def ValidateExpeditedTransfer(self, charID, path, commodities, runTime):
        if self.colonyData is None:
            raise RuntimeError('Unable to validate expedited transfer - no colony data')
        self.PreValidateExpeditedTransfer(path, commodities, runTime)
        if len(path) < 2:
            raise UserError('CreateRouteTooShort')
        if len(commodities) < 1:
            raise UserError('CreateRouteWithoutCommodities')
        sourcePin = self.GetPin(path[0])
        destinationPin = self.GetPin(path[-1])
        if not sourcePin.IsStorage():
            raise UserError('RouteFailedValidationExpeditedSourceNotStorage')
        for typeID, quantity in commodities.iteritems():
            if typeID not in sourcePin.contents:
                raise UserError('RouteFailedValidationExpeditedSourceLacksCommodity', {'typeName': cfg.invtypes.Get(typeID).name})
            if quantity > sourcePin.contents[typeID]:
                raise UserError('RouteFailedValidationExpeditedSourceLacksCommodityQty', {'typeName': cfg.invtypes.Get(typeID).name,
                 'qty': quantity})
            if destinationPin.CanAccept(typeID, quantity) < 1:
                raise UserError('RouteFailedValidationExpeditedDestinationCannotAccept', {'typeName': cfg.invtypes.Get(typeID).name})

        minBandwidth = None
        prevID = None
        for pinID in path:
            pin = self.GetPin(pinID)
            if not pin:
                raise UserError('RouteFailedValidationPinDoesNotExist')
            if pin.ownerID != charID:
                raise UserError('RouteFailedValidationPinNotYours')
            if prevID is None:
                prevID = pinID
                continue
            link = self.GetLink(prevID, pinID)
            if link is None:
                raise UserError('RouteFailedValidationLinkDoesNotExist')
            if minBandwidth is None or link.GetTotalBandwidth() < minBandwidth:
                minBandwidth = link.GetTotalBandwidth()
            prevID = pinID

        if minBandwidth is None or minBandwidth < 0.0:
            log.LogTraceback('Path traversed link with no bandwidth')
            raise UserError('RouteFailedValidationNoBandwidthAvailable')
        if not sourcePin.CanTransfer(commodities, runTime):
            raise UserError('RouteFailedValidationExpeditedSourceNotReady')
        self.PostValidateExpeditedTransfer(path, commodities, runTime)
        return minBandwidth

    def PreValidateExpeditedTransfer(self, path, commodities, runTime):
        pass

    def PostValidateExpeditedTransfer(self, path, commodities, runTime):
        pass

    def ValidateAddExtractorHead(self, pinID, headID, latitude, longitude):
        if self.colonyData is None:
            raise RuntimeError('Unable to validate new extractor head - no colony data')
        if latitude < 0 or latitude > math.pi:
            raise RuntimeError('Invalid value for latitude - must be between 0..pi')
        if longitude < 0 or longitude > 2 * math.pi:
            raise RuntimeError('Invalid value for longitude - must be between 0..2pi')
        self.PreValidateAddExtractorHead(pinID, latitude, longitude)
        pin = self.GetPin(pinID)
        if not pin:
            raise UserError('PinDoesNotExist')
        if not pin.IsExtractor():
            raise UserError('PinDoesNotHaveHeads')
        if pin.FindHead(headID) is not None:
            raise UserError('CannotAddHeadAlreadyExists')
        if len(pin.heads) >= planetCommon.ECU_MAX_HEADS:
            raise UserError('CannotPlaceHeadLimitReached')
        cpuDelta = pin.GetCpuUsage(numHeads=len(pin.heads) + 1) - pin.GetCpuUsage()
        powerDelta = pin.GetPowerUsage(numHeads=len(pin.heads) + 1) - pin.GetPowerUsage()
        if cpuDelta + self.colonyData.GetColonyCpuUsage() > self.colonyData.GetColonyCpuSupply():
            raise UserError('CannotAddToColonyCPUUsageExceeded', {'typeName': (const.UE_LOC, 'UI/PI/Common/ExtractorHead')})
        if powerDelta + self.colonyData.GetColonyPowerUsage() > self.colonyData.GetColonyPowerSupply():
            raise UserError('CannotAddToColonyPowerUsageExceeded', {'typeName': (const.UE_LOC, 'UI/PI/Common/ExtractorHead')})
        spA = SurfacePoint(radius=self.GetPlanetRadius(), theta=pin.longitude, phi=pin.latitude)
        spB = SurfacePoint(radius=self.GetPlanetRadius(), theta=longitude, phi=latitude)
        angleBetween = spA.GetAngleBetween(spB)
        areaOfInfluence = pin.GetAreaOfInfluence()
        if angleBetween > areaOfInfluence:
            raise UserError('CannotPlaceHeadTooFarAway', {'maxDist': util.FmtDist(areaOfInfluence * self.planet.radius)})
        self.PostValidateAddExtractorHead(pinID, latitude, longitude)

    def PreValidateAddExtractorHead(self, pinID, latitude, longitude):
        pass

    def PostValidateAddExtractorHead(self, pinID, latitude, longitude):
        pass

    def ValidateRemoveExtractorHead(self, pinID, headID):
        if self.colonyData is None:
            raise RuntimeError('Unable to validate extractor head removal - no colony data')
        self.PreValidateRemoveExtractorHead(pinID, headID)
        pin = self.GetPin(pinID)
        if not pin:
            raise UserError('PinDoesNotExist')
        if not pin.IsExtractor():
            raise UserError('PinDoesNotHaveHeads')
        if pin.FindHead(headID) is None:
            raise UserError('CannotRemoveHeadNotPresent')
        self.PostValidateRemoveExtractorHead(pinID, headID)

    def PreValidateRemoveExtractorHead(self, pinID, headID):
        pass

    def PostValidateRemoveExtractorHead(self, pinID, headID):
        pass

    def ValidateMoveExtractorHead(self, pinID, headID, latitude, longitude):
        if self.colonyData is None:
            raise RuntimeError('Unable to validate extractor head movement - no colony data')
        if latitude < 0 or latitude > math.pi:
            raise RuntimeError('Invalid value for latitude - must be between 0..pi')
        if longitude < 0 or longitude > 2 * math.pi:
            raise RuntimeError('Invalid value for longitude - must be between 0..2pi')
        self.PreValidateMoveExtractorHead(pinID, headID, latitude, longitude)
        pin = self.GetPin(pinID)
        if not pin:
            raise UserError('PinDoesNotExist')
        if not pin.IsExtractor():
            raise UserError('PinDoesNotHaveHeads')
        if pin.FindHead(headID) is None:
            raise UserError('CannotMoveHeadNotPresent')
        spA = SurfacePoint(theta=pin.longitude, phi=pin.latitude)
        spB = SurfacePoint(theta=longitude, phi=latitude)
        angleBetween = spA.GetAngleBetween(spB)
        areaOfInfluence = pin.GetAreaOfInfluence()
        if angleBetween > areaOfInfluence:
            raise UserError('CannotPlaceHeadTooFarAway', {'maxDist': util.FmtDist(angleBetween * self.planet.radius)})
        self.PostValidateMoveExtractorHead(pinID, headID, latitude, longitude)

    def PreValidateMoveExtractorHead(self, pinID, headID, latitude, longitude):
        pass

    def PostValidateMoveExtractorHead(self, pinID, headID, latitude, longitude):
        pass

    def ValidateInstallProgram(self, pinID, typeID, headRadius):
        if self.colonyData is None:
            raise RuntimeError('Unable to validate new extractor head - no colony data')
        self.PreValidateInstallProgram(pinID, typeID, headRadius)
        pin = self.GetPin(pinID)
        if not pin:
            raise UserError('PinDoesNotExist')
        if not pin.IsExtractor():
            raise UserError('PinDoesNotHaveHeads')
        if headRadius < planetCommon.RADIUS_DRILLAREAMIN or headRadius > planetCommon.RADIUS_DRILLAREAMAX:
            raise RuntimeError('Cannot install a program with a completely bonkers radius')
        self.PostValidateInstallProgram(pinID, typeID, headRadius)

    def PreValidateInstallProgram(self, pinID, typeID, headRadius):
        pass

    def PostValidateInstallProgram(self, pinID, typeID, headRadius):
        pass

    def GetImportEndpoints(self):
        endpoints = []
        if self.colonyData is not None:
            for pin in self.colonyData.pins.itervalues():
                if not pin.IsCommandCenter() and pin.IsSpaceport():
                    endpoints.append(util.KeyVal(id=pin.id, capacity=pin.GetCapacity(), capacityUsed=pin.capacityUsed))

        return endpoints

    def OnPinCreated(self, pinID):
        self.planet.OnPinCreated(self.ownerID, pinID)

    def OnPinRemoved(self, pinID):
        for evalTime, evalPinID in self.simQueue[:]:
            if evalPinID == pinID:
                self.simQueue.remove((evalTime, evalPinID))

        self.planet.OnPinRemoved(self.ownerID, pinID)

    def OnLinkCreated(self, parentID, childID):
        self.planet.OnLinkCreated(self.ownerID, parentID, childID)

    def OnLinkRemoved(self, parentID, childID):
        self.planet.OnLinkRemoved(self.ownerID, parentID, childID)

    def OnRouteCreated(self, routeID):
        route = self.GetRoute(routeID)
        if not route:
            raise RuntimeError('Unable to find recently-created route')
        sourcePin = self.GetPin(route.GetSourcePinID())
        destPin = self.GetPin(route.GetDestinationPinID())
        if sourcePin.IsStorage():
            self.ExecuteRoute(routeID, sourcePin.GetContents())
        else:
            self.StimulateIdlePin(sourcePin)
        if not destPin.IsStorage() and not destPin.IsActive() and destPin.CanActivate():
            self.SchedulePin(destPin)
        self.planet.OnRouteCreated(self.ownerID, routeID)

    def OnRouteRemoved(self, routeID):
        self.planet.OnRouteRemoved(self.ownerID, routeID)

    def OnSchematicInstalled(self, pinID, schematicID):
        self.planet.OnSchematicInstalled(self.ownerID, pinID, schematicID)

    def OnProgramInstalled(self, pinID):
        pass

    def OnLinkUpgraded(self, parentPinID, childPinID):
        self.planet.OnLinkUpgraded(self.ownerID, parentPinID, childPinID)

    def LogInfo(self, *args):
        self.planetBroker.LogInfo('( Colony PID:', self.planetID, ', Owner:', self.ownerID, ') | ', *args)

    def LogWarn(self, *args):
        self.planetBroker.LogWarn('( Colony PID:', self.planetID, ', Owner:', self.ownerID, ') | ', *args)

    def LogError(self, *args):
        self.planetBroker.LogError('( Colony PID:', self.planetID, ', Owner:', self.ownerID, ') | ', *args)

    def LogNotice(self, *args):
        self.planetBroker.LogNotice('( Colony PID:', self.planetID, ', Owner:', self.ownerID, ') | ', *args)

    def GetTypeAttribute(self, typeID, attributeID):
        raise NotImplementedError('GetTypeAttribute must be specifically implemented on the client and server')

    @bluepy.TimedFunction('BaseColony::CreateProgram')
    def CreateProgram(self, harmonic, ecuPinID, resourceTypeID, points = None, headRadius = None):
        ecuPin = self.GetPin(ecuPinID)
        if points is None:
            points = ecuPin.heads
        if headRadius is None:
            headRadius = ecuPin.GetExtractorHeadRadius()
        overlapFactor = self.GetTypeAttribute(ecuPin.typeID, const.attributeEcuOverlapFactor)
        maxVolume = self.GetTypeAttribute(ecuPin.typeID, const.attributeEcuMaxVolume)
        overlapModifiers = {}
        heads = []
        for index, longitude, latitude in points:
            heads.append((index, SurfacePoint(theta=latitude, phi=longitude)))
            overlapModifiers[index] = 1.0

        distance = {}
        valueByIndex = {}
        for index, surfacePoint in heads:
            theta = 2.0 * math.pi - surfacePoint.theta
            phi = surfacePoint.phi
            valueByIndex[index] = max(builder.GetValueAt(harmonic, theta, phi), 0)
            for index2, surfacePoint2 in heads:
                if index == index2:
                    continue
                key = tuple(sorted([index, index2]))
                if key not in distance:
                    distance[key] = surfacePoint.GetDistanceToOther(surfacePoint2)

        with bluepy.TimerPush('OverlapOwnHeads'):
            for (head1, head2), dist in distance.iteritems():
                if dist < headRadius * 2:
                    radiusSquared = headRadius ** 2
                    overlap = (2 * radiusSquared * math.acos(0.5 * (dist / headRadius)) - 0.5 * dist * math.sqrt(4 * radiusSquared - dist ** 2)) / (math.pi * radiusSquared)
                    modifier = min(1, max(0, 1 - overlap * overlapFactor))
                    valueByIndex[head1] *= modifier
                    valueByIndex[head2] *= modifier
                    overlapModifiers[head1] *= modifier
                    overlapModifiers[head2] *= modifier

        with bluepy.TimerPush('OverlapOthersHeads'):
            otherHeadsInfo = []
            for pin in self.colonyData.GetECUs(ecuPinID):
                if pin.programType != resourceTypeID:
                    continue
                otherHeadsInfo.append((pin.GetExtractorHeadRadius(), pin.heads))

            headArea = math.pi * headRadius ** 2
            for index, surfacePoint1 in heads:
                modifier = 1
                for otherHeadRadius, otherHeads in otherHeadsInfo:
                    if modifier == 0:
                        break
                    for index2, longitude2, latitude2 in otherHeads:
                        surfacePoint2 = SurfacePoint(theta=latitude2, phi=longitude2)
                        d, R, r = surfacePoint1.GetDistanceToOther(surfacePoint2), headRadius, otherHeadRadius
                        if d > R + r:
                            continue
                        r2, R2, d2 = r ** 2, R ** 2, d ** 2
                        alpha = (d2 + r2 - R2) / (2 * d * r)
                        if alpha < -1:
                            overlap = math.pi * r2 / headArea
                        elif alpha > 1:
                            overlap = 1
                        else:
                            f1 = r ** 2 * math.acos(alpha)
                            f2 = R ** 2 * math.acos((d ** 2 + R ** 2 - r ** 2) / (2 * d * R))
                            f3 = 0.5 * math.sqrt((-d + r + R) * (d + r - R) * (d - r + R) * (d + r + R))
                            A = f1 + f2 - f3
                            overlap = A / headArea
                        modifier *= min(1, max(0, 1 - overlap * 2 * overlapFactor))

                valueByIndex[index] *= modifier
                overlapModifiers[index] *= modifier

        for index, modifier in overlapModifiers.iteritems():
            overlapModifiers[index] = 1.0 - modifier

        maxValue = maxVolume * sum(valueByIndex.values())
        programLength = planetCommon.GetProgramLengthFromHeadRadius(headRadius)
        cycleTime = planetCommon.GetCycleTimeFromProgramLength(programLength)
        numCycles = int(programLength / cycleTime)
        cycleTime = int(cycleTime * HOUR)
        return (int(maxValue),
         cycleTime,
         numCycles,
         overlapModifiers)