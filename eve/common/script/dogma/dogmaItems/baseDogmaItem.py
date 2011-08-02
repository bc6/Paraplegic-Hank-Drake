import dogmax
import weakref
import util
import log
import sys

class BaseDogmaItem(dogmax.SlimDogmaItem):
    __guid__ = 'dogmax.BaseDogmaItem'

    def __init__(self, dogmaLocation, item):
        super(BaseDogmaItem, self).__init__(dogmaLocation, item)
        self.location = None
        self.flagID = None
        self.isDirty = False
        self.fittingFlags = set()



    def __str__(self):
        return '<%s::%s::%s>' % (self.__guid__, self.itemID, self.typeID)



    def __repr__(self):
        return '<%s::%s::%s>' % (self.__guid__, self.itemID, self.typeID)



    def Load(self, item, instanceRow):
        categoryID = item.categoryID
        typeID = item.typeID
        groupID = item.groupID
        ownerID = item.ownerID
        flag = item.flagID
        if ownerID:
            ownerOb = cfg.eveowners.Get(ownerID)
            if ownerOb.typeID == const.typeCorporation or ownerOb.IsNPC() or ownerOb.IsSystem():
                ownerID = None
        self.flagID = None
        attrs = self.attributes
        attrs.update(self.dogmaLocation.GetAttributesForType(typeID))
        attributesByIdx = self.dogmaLocation.GetAttributesByIndex()
        for (attributeIdx, attributeID,) in attributesByIdx.iteritems():
            v = instanceRow[attributeIdx]
            if v != 0:
                if type(v) is bool:
                    v = int(v)
                attrs[attributeID] = v




    def PostLoadAction(self):
        pass



    def GetLocationInfo(self):
        locationID = None
        if self.location is not None:
            locationID = self.location.itemID
        return (self.ownerID, locationID, self.flagID)



    def GetItemInfo(self):
        (ownerID, locationID, flagID,) = self.GetLocationInfo()
        return (self.typeID,
         self.groupID,
         self.categoryID,
         ownerID,
         locationID,
         flagID)



    def SetItemInfo(self, typeID, groupID, categoryID, ownerID, locationDogmaItem, flagID):
        self.typeID = typeID
        self.groupID = groupID
        self.categoryID = categoryID
        self.ownerID = ownerID
        if locationDogmaItem is None:
            self.location = None
        else:
            self.location = weakref.proxy(locationDogmaItem)
        self.flagID = flagID



    def GetPilot(self):
        return self.ownerID



    @property
    def locationID(self):
        if self.location is None:
            return 
        return self.location.itemID



    def SetLocation(self, locationID, locationDogmaItem, flagID):
        self.location = weakref.proxy(locationDogmaItem)
        self.flagID = flagID



    def UnsetLocation(self, locationDogmaItem):
        self.location = None



    def MarkDirty(self):
        self.isDirty = True



    def UnmarkDirty(self):
        self.isDirty = False



    def RegisterEffect(self, effectID, effectStart, duration, environment, repeat):
        self.activeEffects[effectID] = [effectStart,
         duration,
         environment,
         repeat]



    def UnregisterEffect(self, effectID, environment):
        del self.activeEffects[effectID]



    def IsEffectRegistered(self, effectID, environment):
        return effectID in self.activeEffects



    def Unload(self):
        stackTraceCount = self.FlushEffects()
        if stackTraceCount:
            log.LogTraceback('FlushEffectsFromItem %s stack traced %s times, this is to provide higher context' % (self.itemID, stackTraceCount))



    def OnItemLoaded(self):
        pass



    def GetEnvironmentInfo(self):
        return util.KeyVal(itemID=self.itemID, shipID=self.itemID, charID=None, otherID=None, targetID=None, effectID=None)



    def GetPersistables(self):
        return set([self.itemID])



    def IsOnline(self):
        return False



    def IsActive(self):
        return False



    def FlushEffects(self):
        flushAddedToUnloading = False
        unloadingItems = self.dogmaLocation.unloadingItems
        itemID = self.itemID
        if itemID not in unloadingItems:
            unloadingItems.add(itemID)
            flushAddedToUnloading = True
        try:
            stackTraceCount = self._FlushEffects()

        finally:
            if flushAddedToUnloading and itemID in unloadingItems:
                unloadingItems.remove(itemID)

        return stackTraceCount



    def _FlushEffects(self):
        stackTraceCount = 0
        itemID = self.itemID
        dogmaLM = self.dogmaLocation
        for effectID in self.activeEffects.keys():
            if isinstance(effectID, tuple):
                (effectID, shipID,) = effectID
            effect = dogmaLM.dogmaStaticMgr.effects[effectID]
            try:
                if effect.effectCategory == const.dgmEffDungeon:
                    dogmaLM.StopDungeonEffect(itemID, effectID)
                elif effect.effectCategory == const.dgmEffSystem:
                    dogmaLM.StopMultiEffect(itemID, effectID)
                else:
                    dogmaLM.StopEffect(effectID, itemID, forced=True)
            except Exception:
                stackTraceCount += 1
                log.LogException()
                sys.exc_clear()

        activeDungeonEffectsByItem = dogmaLM.activeDungeonEffectsByItem
        for effectTuple in activeDungeonEffectsByItem.get(itemID, [])[:]:
            if not isinstance(effectTuple, tuple):
                continue
            (effectBeaconID, effectID,) = effectTuple
            try:
                dogmaLM.StopMultiEffectOnItem(effectBeaconID, effectID, itemID)
            except Exception:
                stackTraceCount += 1
                log.LogException()
                sys.exc_clear()

        if itemID in activeDungeonEffectsByItem:
            del activeDungeonEffectsByItem[itemID]
        return stackTraceCount



    def CanFitItem(self, dogmaItem, flagID):
        return False




