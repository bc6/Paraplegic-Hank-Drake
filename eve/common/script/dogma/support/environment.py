import blue
import random

class Environment:
    __guid__ = 'dogmax.Environment'
    itemID = None
    charID = None
    shipID = None
    targetID = None
    targetIDs = None
    otherID = None
    startTime = None
    currentStartTime = None
    currentSeed = None
    iterationSuccess = None
    random = None
    registered = False
    registrations = None
    shipGroupID = None
    shipCategoryID = None
    targetTypeID = None
    otherTypeID = None
    itemTypeID = None
    graphicInfo = None
    unexpectedStop = False
    actualEffectID = None

    def __init__(self, itemID, charID, shipID, targetID, otherID, effectID, dogmaLM, expressionID):
        self.effectID = effectID
        self.dogmaLM = dogmaLM
        self.expressionID = expressionID
        self.slaves = None
        self.graphicInfo = None
        if itemID:
            self.itemID = itemID
            if type(itemID) is tuple:
                self.itemTypeID = itemID[2]
            else:
                self.itemTypeID = dogmaLM.GetItem(itemID).typeID
        if charID:
            self.charID = charID
        if shipID:
            self.shipID = shipID
            item = dogmaLM.GetItem(shipID)
            self.shipGroupID = item.groupID
            self.shipCategoryID = item.categoryID
        if targetID:
            self.targetID = targetID
            self.targetTypeID = dogmaLM.GetItem(targetID).typeID
        if otherID:
            self.otherID = otherID
            if type(otherID) is tuple:
                self.otherTypeID = otherID[2]
            else:
                self.otherTypeID = dogmaLM.GetItem(otherID).typeID
        self.actualEffectID = effectID
        if effectID in (const.effectUseMissiles, const.effectWarpDisruptSphere) and self.otherTypeID is not None:
            defEffectID = dogmaLM.dogmaStaticMgr.defaultEffectByType.get(self.otherTypeID)
            if defEffectID is not None:
                self.actualEffectID = defEffectID



    def Line(self):
        return [self.itemID,
         self.charID,
         self.shipID,
         self.targetID,
         self.otherID,
         [],
         self.effectID]



    def UpdateOtherID(self, otherID):
        self.otherID = otherID
        if type(otherID) is tuple:
            self.otherTypeID = otherID[2]
        else:
            self.otherTypeID = self.dogmaLM.inventory2.GetItem(otherID).typeID



    def Effect(self):
        return self.dogmaLM.broker.effects[self.effectID]



    def OnStart(self, effect, t):
        if self.currentStartTime is None:
            if effect.rangeChance or effect.electronicChance or effect.propulsionChance:
                self.random = random.WichmannHill(blue.os.GetTime(1))
                self.registrations = []
        self.currentStartTime = t
        if self.random is not None:
            self.currentSeed = self.GetRandomSeed()



    def GetRandomSeed(self):
        return self.random._seed



    def UpdateCurrentSeed(self):
        self.currentSeed = self.GetRandomSeed()



    def Random(self):
        return self.random.random()




