#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/planet/entities/processPin.py
import const
import planet
import blue
import util
import planetCommon

class ProcessPin(planet.BasePin):
    __guid__ = 'planet.ProcessPin'
    __slots__ = ['schematicID',
     'cycleTime',
     'hasReceivedInputs',
     'receivedInputsLastCycle',
     'demands',
     'products']

    def __init__(self, typeID):
        planet.BasePin.__init__(self, typeID)
        self.schematicID = None
        self.cycleTime = None
        self.hasReceivedInputs = True
        self.receivedInputsLastCycle = True
        self.demands = {}
        self.products = {}

    def CanAccept(self, typeID, quantity):
        if typeID not in self.demands:
            return 0
        if quantity < 0:
            quantity = self.demands[typeID]
        remainingSpace = self.demands[typeID]
        if typeID in self.contents:
            remainingSpace = self.demands[typeID] - self.contents[typeID]
        if remainingSpace < quantity:
            return remainingSpace
        return quantity

    def HasEnoughInputs(self):
        for demandTypeID, demandQty in self.demands.iteritems():
            if demandTypeID not in self.contents:
                return False
            if demandQty > self.contents[demandTypeID]:
                return False

        return True

    def CanActivate(self):
        if self.activityState < planet.STATE_IDLE:
            return False
        if self.schematicID is None:
            return False
        if self.IsActive():
            return True
        if self.hasReceivedInputs or self.receivedInputsLastCycle:
            return True
        if not self.HasEnoughInputs():
            return False
        return True

    def GetNextRunTime(self):
        if not self.IsActive() and self.HasEnoughInputs():
            return None
        else:
            return planet.BasePin.GetNextRunTime(self)

    def CanRun(self, runTime = None):
        if not self.IsActive() and not self.CanActivate():
            return False
        rt = runTime
        if runTime is None:
            rt = blue.os.GetWallclockTime()
        nextRunTime = self.GetNextRunTime()
        if nextRunTime is None or nextRunTime <= rt:
            return True
        return False

    def Run(self, runTime):
        products = {}
        if self.IsActive():
            products = self.products.copy()
        canConsume = True
        for demandTypeID, demandQty in self.demands.iteritems():
            if demandTypeID not in self.contents:
                canConsume = False
                break
            if demandQty > self.contents[demandTypeID]:
                canConsume = False
                break

        if canConsume:
            for demandTypeID, demandQty in self.demands.iteritems():
                self.RemoveCommodity(demandTypeID, demandQty)

            self.SetState(planet.STATE_ACTIVE)
        else:
            self.SetState(planet.STATE_IDLE)
        self.receivedInputsLastCycle = self.hasReceivedInputs
        self.hasReceivedInputs = False
        self.lastRunTime = runTime
        return products

    def InstallSchematic(self, schematicID):
        schematicObj = cfg.schematics.Get(schematicID)
        if not schematicObj:
            raise RuntimeError('Schematic with schematicID', schematicID, 'does not exist')
        if schematicID not in cfg.schematicspinmap:
            self.LogError('AUTHORING ERROR :: Schematic ID', schematicID, 'cannot be assigned to any pin types!')
            return
        if schematicID not in cfg.schematicstypemap:
            self.LogError('AUTHORING ERROR :: Schematic ID', schematicID, 'has no inputs or outputs!')
            return
        typeOK = False
        for pinRow in cfg.schematicspinmap.get(schematicID, []):
            if self.typeID == pinRow.pinTypeID:
                typeOK = True
                break

        if not typeOK:
            raise UserError('CannotAssignSchematicToPinType')
        self.SetSchematic(schematicObj)
        self.SetState(planet.STATE_IDLE)

    def SetSchematic(self, schematic):
        self.demands = {}
        self.products = {}
        for commodity in cfg.schematicstypemap.get(schematic.schematicID, []):
            if commodity.isInput:
                self.demands[commodity.typeID] = commodity.quantity
            else:
                self.products[commodity.typeID] = commodity.quantity

        self.schematicID = schematic.schematicID
        self.cycleTime = schematic.cycleTime * SEC
        newContents = {}
        for commodityID, quantity in self.contents.iteritems():
            if commodityID in self.demands:
                newContents[commodityID] = quantity if quantity < self.demands[commodityID] else self.demands[commodityID]

        self.contents = newContents

    def AddCommodity(self, typeID, quantity):
        qtyAdded = self._AddCommodity(typeID, quantity)
        if qtyAdded > 0:
            self.hasReceivedInputs = True
        return qtyAdded

    def IsConsumer(self):
        return True

    def GetConsumables(self):
        return self.demands.copy()

    def IsProducer(self):
        return True

    def IsProcessor(self):
        return True

    def GetCycleTime(self):
        return self.cycleTime

    def GetProducts(self):
        return self.products.copy()

    def GetInputBufferState(self):
        productsRatio = 0
        for typeID, qty in self.demands.iteritems():
            productsRatio += float(self.contents.get(typeID, 0)) / qty

        return 1 - productsRatio / len(self.demands)

    def HasDifferingState(self, otherPin):
        if self.schematicID != getattr(otherPin, 'schematicID', -1):
            return True
        return planet.BasePin.HasDifferingState(self, otherPin)

    def Serialize(self, full = False):
        data = planet.BasePin.Serialize(self, full)
        data.schematicID = self.schematicID
        data.hasReceivedInputs = self.hasReceivedInputs
        data.receivedInputsLastCycle = self.receivedInputsLastCycle
        return data


exports = {'planet.ProcessPin': ProcessPin}