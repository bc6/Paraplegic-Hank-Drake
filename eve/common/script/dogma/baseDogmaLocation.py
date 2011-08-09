assoc = {const.dgmAssPostPercent: 'Percentage Modifier',
 const.dgmAssPreMul: 'Multiply before addition',
 const.dgmAssPreAssignment: 'Assign before all other arithmetic',
 const.dgmAssModAdd: 'Add',
 const.dgmAssModSub: 'Subtract',
 const.dgmAssPostMul: 'Multiply after addition',
 const.dgmAssPreDiv: 'Divide before addition',
 const.dgmAssPostDiv: 'Divide after addition',
 const.dgmAssPostAssignment: 'Assign after all other arithmetic (override)',
 9: 'Special skill relationship'}
import log
import blue
import sys
import dogmax
import weakref
import math
import uthread
import bluepy
import util
from skillUtil import GetSkillLevelRaw
from collections import defaultdict

class BaseDogmaLocation():
    __guid__ = 'dogmax.BaseDogmaLocation'

    def __init__(self, broker):
        self.broker = broker
        self.onlineEffects = {const.effectOnline: True,
         const.effectOnlineForStructures: True}
        self.characterContext = {}
        self.pilotsByShipID = {}
        self.dogmaItems = {}
        self.locationID = None
        self.moduleListsByShipGroup = defaultdict(lambda : defaultdict(set))
        self.attributeChangeCallbacksByAttributeID = {}
        self.loadingItems = set()
        self.failedLoadingItems = {}
        self.crits = {}
        self.activatingEffects = {}
        self.deactivatingEffects = set()
        self.activatingEffectsByLocation = {}
        self.activatingEffectsByTarget = {}
        self.activeEffectsByShip = {}
        self.locationModifiers = {}
        self.modifiersByItemAttribute = {}
        self.modifyingItems = {}
        self.modifiersByLocationAttribute = {}
        self.modifyingLocations = {}
        self.modifiersByLocationGroupAttribute = {}
        self.modifyingLocationGroups = {}
        self.modifiersByLocationRequiredSkillAttribute = {}
        self.modifyingLocationRequiredSkill = {}
        self.modifiersByOwnerRequiredSkillAttribute = {}
        self.modifyingOwnerRequiredSkill = {}
        self.unloadingItems = set()
        self.externalsByPilot = {}
        self.extraTracebacks = True
        self.delayAttributePropagation = {}
        self.instanceRowDescriptor = blue.DBRowDescriptor((('instanceID', const.DBTYPE_I8),
         ('online', const.DBTYPE_BOOL),
         ('damage', const.DBTYPE_R5),
         ('charge', const.DBTYPE_R5),
         ('skillPoints', const.DBTYPE_I4),
         ('armorDamage', const.DBTYPE_R5),
         ('shieldCharge', const.DBTYPE_R5),
         ('incapacitated', const.DBTYPE_BOOL)))
        l = [0] + [0] * (len(self.instanceRowDescriptor) - 1)
        self.fakeInstanceRow = blue.DBRow(self.instanceRowDescriptor, l)



    def LoadItem(self, itemKey, instanceRow = None, wait = False, item = None, newInstance = False, timerName = None):
        if itemKey == self.locationID:
            return itemKey
        if self.IsItemLoaded(itemKey):
            return itemKey
        self.EnterCriticalSection('LoadItem', itemKey)
        try:
            try:
                if self.IsItemLoaded(itemKey):
                    return itemKey
                if itemKey in self.dogmaItems:
                    return itemKey
                self.loadingItems.add(itemKey)
                try:
                    dogmaItem = self._LoadItem(itemKey, instanceRow=instanceRow, item=item, newInstance=newInstance)

                finally:
                    self.loadingItems.remove(itemKey)

                if dogmaItem is not None:
                    dogmaItem.PostLoadAction()
            except Exception as e:
                self.failedLoadingItems[itemKey] = 'Exception: ' + strx(e)
                raise 

        finally:
            self.LeaveCriticalSection('LoadItem', itemKey)

        return itemKey



    def _LoadItem(self, itemKey, instanceRow = None, item = None, newInstance = False):
        self.LogInfo('BaseDogmaLocation::LoadItem', itemKey)
        if isinstance(itemKey, tuple):
            self.dogmaItems[itemKey] = dogmaItem = dogmax.DBLessDogmaItem(weakref.proxy(self), itemKey)
            dogmaItem.Load()
            self.FitItemToLocation(itemKey[0], itemKey, itemKey[1])
            return dogmaItem
        if item is None:
            item = self.GetItem(itemKey)
        if not self.IsItemWanted(item.typeID) or newInstance:
            instanceRow = self.IntroduceNewItem(item)
        else:
            instanceRow = self.GetInstance(item)
        self.LogInfo('BaseDogmaLocation::Actually Loading item', itemKey)
        self.dogmaItems[itemKey] = dogmaItem = self.GetClassForItem(item)(weakref.proxy(self), item)
        dogmaItem.Load(item, instanceRow)
        self.FitItemToLocation(item.locationID, itemKey, item.flagID)
        dogmaItem.OnItemLoaded()
        return dogmaItem



    def LoadPilot(self, shipID):
        self.LogError('LoadPilot being called in BaseDogmaLocation', shipID)



    def FitItemToLocation(self, locationID, itemID, flagID):
        isItemLoaded = itemID in self.dogmaItems
        if itemID not in self.dogmaItems:
            self.LoadItem(itemID)
            if not isItemLoaded:
                return 
        if not isItemLoaded:
            self.LoadItem(locationID)
            return 
        locationDogmaItem = self.dogmaItems.get(locationID, None)
        if locationDogmaItem is None:
            self.LogInfo('FitItemToLocation::Fitted to None item', itemID, locationID, flagID)
            return 
        dogmaItem = self.dogmaItems[itemID]
        if not locationDogmaItem.CanFitItem(dogmaItem, flagID):
            if locationDogmaItem.categoryID == const.categoryShip:
                self.LogError("Somebody asked us to fit an item to a ship that can't be fitted", locationID, itemID, flagID)
            return 
        (oldOwnerID, oldLocationID, oldFlagID,) = oldInfo = dogmaItem.GetLocationInfo()
        dogmaItem.SetLocation(locationID, locationDogmaItem, flagID)
        startedEffects = self.StartPassiveEffects(itemID, dogmaItem.typeID)
        if startedEffects is not None:
            self.UnsetItemLocation(itemID, locationID)
            for effectID in startedEffects:
                try:
                    self.StopEffect(effectID, itemID, 1)
                except UserError as e:
                    log.LogException('Failed to start effect %s' % effectID, channel='svc.dogmaIM')
                    sys.exc_clear()

            if util.IsFlagSubSystem(dogmaItem.flagID):
                raise RuntimeError('Failed to start passive effects on a subsystem')
            raise UserError('ModuleFitFailed', {'modulename': (GROUPID, dogmaItem.groupID),
             'reason': ''})
        self.RecalculateAffectedLocationModifiers(itemID, dogmaItem.typeID, dogmaItem.groupID, oldLocationID)
        locationCategoryID = locationDogmaItem.categoryID
        pilotID = dogmaItem.ownerID
        if locationCategoryID == const.categoryShip and dogmaItem.attributes.get(const.attributeIsOnline, 0):
            if pilotID is None:
                if locationID not in self.onlineByShip:
                    self.onlineByShip[locationID] = {}
                self.onlineByShip[locationID][flagID] = itemID
            else:
                self.StartModuleOnlineEffect(itemID, pilotID, dogmaItem.locationID, '', '')
        return oldInfo



    def UnfitItemFromLocation(self, locationID, itemID, flushEffects = False):
        self.UnsetItemLocation(itemID, locationID)
        dogmaItem = self.dogmaItems[itemID]
        (itemTypeID, itemGroupID,) = (dogmaItem.typeID, dogmaItem.groupID)
        for (effectID, effect,) in dogmaItem.activeEffects.items():
            if type(effectID) is tuple:
                effectID = effectID[0]
            if not flushEffects and effect[const.ACT_IDX_DURATION] != -1:
                raise UserError('ModuleEffectActive', {'modulename': (TYPEID, itemTypeID),
                 'effectname': ''})
            if self.dogmaStaticMgr.effects[effectID].effectCategory != const.dgmEffPassive:
                self.StopEffect(effectID, itemID, forced=flushEffects)

        effectsCompleted = set()
        if self.dogmaStaticMgr.effectsByType.has_key(itemTypeID):
            for effectID in self.dogmaStaticMgr.TypeGetOrderedEffectIDs(itemTypeID):
                if effectID not in dogmaItem.activeEffects:
                    continue
                effect = self.dogmaStaticMgr.effects[effectID]
                if effect.effectCategory in [const.dgmEffPassive, const.dgmEffSystem]:
                    try:
                        self.StopEffect(effectID, itemID)
                        effectsCompleted.add(effect)
                    except UserError as e:
                        for effect in effectsCompleted:
                            try:
                                info = dogmaItem.GetEnvironmentInfo()
                                env = dogmax.Environment(info.itemID, info.charID, info.shipID, None, info.otherID, effectID, weakref.proxy(self), None)
                                self.StartEffect(effect.effectID, itemID, env)
                            except UserError as e:
                                log.LogException(channel='svc.dogmaIM')
                                sys.exc_clear()

                        sys.exc_clear()

        self.RecalculateAffectedLocationModifiers(itemID, dogmaItem.typeID, dogmaItem.groupID, locationID, fromOldLocation=True)
        locationItem = self.GetItem(locationID)



    def UnsetItemLocation(self, itemKey, locationID):
        locationDogmaItem = self.dogmaItems.get(locationID, None)
        dogmaItem = self.dogmaItems[itemKey]
        if locationDogmaItem is None:
            self.LogError("UnsetItemLocation::called for location that wasn't loaded", itemKey, locationID)
            return 
        dogmaItem.UnsetLocation(locationDogmaItem)



    @bluepy.TimedFunction('DogmaLocation::StartEffect')
    def StartEffect(self, effectID, itemKey, environment, repeat = 0, byUser = 0, checksOnly = None):
        try:
            dogmaItem = self.dogmaItems[itemKey]
        except KeyError:
            self.LogError('StartEffect::Item neither loaded nor being loaded', effectID, itemKey)
            self.LoadItem(itemKey)
        dogmaItem = self.dogmaItems[itemKey]
        activateKey = (itemKey, effectID)
        if effectID not in self.dogmaStaticMgr.effectsByType.get(dogmaItem.typeID, []):
            if effectID == const.effectOnline:
                self.LogInfo("StartEffect::Online Effect being started on a type that doesn't have it", itemKey, dogmaItem.typeID, effectID)
            else:
                self.LogError("StartEffect::Effect being started on type that doesn't have it (unexpected)", itemKey, dogmaItem.typeID, effectID)
            return 
        if dogmaItem.IsEffectRegistered(effectID, environment):
            raise UserError('EffectAlreadyActive2', {'modulename': (TYPEID, dogmaItem.typeID)})
        if activateKey in self.activatingEffects:
            self.broker.LogWarn('Effect already activating o_O', activateKey, blue.os.TimeDiffInMs(self.activatingEffects[activateKey][0]) / 1000.0)
            raise UserError('EffectAlreadyActive2', {'modulename': (TYPEID, dogmaItem.typeID)})
        self.activatingEffects[activateKey] = [blue.os.GetTime(), None, environment]
        itemLocationID = dogmaItem.locationID
        if itemLocationID not in self.activatingEffectsByLocation:
            self.activatingEffectsByLocation[itemLocationID] = set([activateKey])
        else:
            self.activatingEffectsByLocation[itemLocationID].add(activateKey)
        targetID = environment.targetID
        if targetID:
            if targetID not in self.activatingEffectsByTarget:
                self.activatingEffectsByTarget[targetID] = set([activateKey])
            else:
                self.activatingEffectsByTarget[targetID].add(activateKey)
        try:
            effect = self.dogmaStaticMgr.effects[effectID]
            self.StartEffect_PreChecks(effect, dogmaItem, environment, byUser)
            duration = self.GetEffectDuration(effect, environment)
            try:
                effectStart = self._StartEffect(effect, dogmaItem, environment, duration, repeat, byUser, checksOnly)
            except dogmax.EffectFailedButShouldBeStopped:
                effectStart = blue.os.GetTime()
                repeat = 0
                sys.exc_clear()
            self.RegisterEffect(effect, dogmaItem, environment, effectStart, duration, repeat)

        finally:
            del self.activatingEffects[activateKey]
            self.activatingEffectsByLocation[itemLocationID].remove(activateKey)
            if not len(self.activatingEffectsByLocation[itemLocationID]):
                del self.activatingEffectsByLocation[itemLocationID]
            if targetID:
                self.activatingEffectsByTarget[targetID].remove(activateKey)
                if not len(self.activatingEffectsByTarget[targetID]):
                    del self.activatingEffectsByTarget[targetID]




    def _StartEffect(self, effect, dogmaItem, environment, duration, repeat, byUser, checksOnly):
        effectID = effect.effectID
        self.effectCompiler.PreStartEffectChecks(effectID, environment)
        self.ConsumeResources(environment)
        itemKey = dogmaItem.itemID
        effectStart = blue.os.GetTime()
        environment.OnStart(effect, effectStart)
        if environment.startTime is None:
            environment.startTime = effectStart
        if checksOnly is None:
            targetID = environment.targetID
            flag = self.CheckApplyModifiers(environment.shipID, itemKey, effect, targetID, environment)
            if flag is not None:
                checksOnly = not flag
        if effect.preExpression:
            if checksOnly:
                self.effectCompiler.StartEffectChecks(effectID, environment)
            else:
                self.effectCompiler.StartEffect(effectID, environment)
            if effectID == const.effectOnline:
                try:
                    for onlineEffectID in self.dogmaStaticMgr.effectsByType[dogmaItem.typeID]:
                        if self.dogmaStaticMgr.effects[onlineEffectID].effectCategory != const.dgmEffOnline:
                            continue
                        try:
                            self.StartEffect(onlineEffectID, itemKey, environment, repeat, 0)
                        except UserError:
                            self.LogError('Failed to start online effect', onlineEffectID, effectID, itemKey)
                            sys.exc_clear()

                except KeyError:
                    self.LogWarn('Onlining item with no online effects', itemKey)
        return effectStart



    def ConsumeResources(self, environment):
        pass



    def GetEffectDuration(self, effect, environment):
        if effect.durationAttributeID:
            duration = self.GetAttributeValue(environment.itemID, effect.durationAttributeID)
            if duration < 0:
                self.LogAttribute(environment.itemID, effect.durationAttributeID, '[EffectCantHaveNegativeDuration %s]' % effect.effectName, force=True)
                raise UserError('EffectCantHaveNegativeDuration', {'modulename': (TYPEID, environment.itemTypeID),
                 'duration': duration})
            elif duration < 20:
                self.broker.LogInfo('Effect', effect.effectName, 'has very conspicuous short duration', duration)
        else:
            duration = -1
        return duration



    def RegisterEffect(self, effect, dogmaItem, environment, effectStart, duration, repeat):
        effectID = effect.effectID
        dogmaItem.RegisterEffect(effectID, environment.currentStartTime, duration, environment, repeat)
        if environment.shipID not in self.activeEffectsByShip:
            self.activeEffectsByShip[environment.shipID] = {effectID: dogmaItem.itemID}
        else:
            self.activeEffectsByShip[environment.shipID][effectID] = dogmaItem.itemID



    def StartEffect_PreChecks(self, effect, dogmaItem, environment, byUser):
        if byUser and effect.effectCategory in [const.dgmEffOnline, const.dgmEffOverload]:
            raise RuntimeError('TheseEffectsShouldNeverBeUserStarted', effect.effectID)



    def CheckApplyModifiers(self, *args):
        pass



    @bluepy.TimedFunction('DogmaLocation::StopEffect')
    def StopEffect(self, effectID, itemKey, byUser = False, activationInfo = None, forced = False, forceStopRepeating = False, possiblyStopRepeat = True):
        try:
            dogmaItem = self.dogmaItems[itemKey]
        except KeyError:
            self.LogInfo("StopEffect called on an item that isn't loaded", itemKey, effectID)
            return 
        deactivateKey = (itemKey, effectID)
        if deactivateKey in self.deactivatingEffects:
            log.LogTraceback('Multiple concurrent StopEffect calls for %s' % strx(deactivateKey), channel='svc.dogmaIM')
            return 
        self.deactivatingEffects.add(deactivateKey)
        try:
            if activationInfo is None:
                try:
                    activationInfo = dogmaItem.activeEffects[effectID]
                except KeyError:
                    if (itemKey, effectID) in self.activatingEffects:
                        raise UserError('EffectStillActivating', {'moduleName': (TYPEID, dogmaItem.typeID)})
                    self.LogInfo("Stopping effect that isn't active", itemKey, effectID)
                    return 0
            if not self.PreStopEffectChecks(effectID, dogmaItem, activationInfo, forced, byUser, possiblyStopRepeat):
                return 
            error = self._StopEffect(effectID, dogmaItem, activationInfo, byUser, forced, forceStopRepeating, possiblyStopRepeat)
            self.PostStopEffectAction(effectID, dogmaItem, activationInfo, forced, byUser, error)

        finally:
            self.deactivatingEffects.remove(deactivateKey)




    def _StopEffect(self, effectID, dogmaItem, activationInfo, byUser, forced, forceStopRepeating, possiblyStopRepeat):
        if effectID in self.onlineEffects:
            effects = dogmaItem.activeEffects
            itemKey = dogmaItem.itemID
            for (otherEffectID, activationInfo2,) in effects.items():
                if otherEffectID != effectID and effects.has_key(otherEffectID):
                    otherDuration = effects[otherEffectID][const.ACT_IDX_DURATION]
                    if otherDuration == -1 and self.dogmaStaticMgr.effects[otherEffectID].effectCategory != const.dgmEffPassive:
                        self.StopEffect(otherEffectID, itemKey, False, activationInfo2)

        environment = activationInfo[const.ACT_IDX_ENV]
        self.effectCompiler.StopEffect(effectID, environment, forced)



    def PreStopEffectChecks(self, effectID, dogmaItem, activationInfo, forced, byUser, possiblyStopRepeat, *args):
        return True



    def PostStopEffectAction(self, effectID, dogmaItem, activationInfo, forced, byUser, error):
        environment = activationInfo[const.ACT_IDX_ENV]
        if dogmaItem.IsEffectRegistered(effectID, environment):
            effect = self.dogmaStaticMgr.effects[effectID]
            self.UnregisterEffect(effect, dogmaItem, environment)



    def UnregisterEffect(self, effect, dogmaItem, environment):
        effectID = effect.effectID
        dogmaItem.UnregisterEffect(effectID, environment)
        shipID = environment.shipID
        try:
            del self.activeEffectsByShip[shipID][effectID]
            if len(self.activeEffectsByShip[shipID]) == 0:
                del self.activeEffectsByShip[shipID]
        except KeyError:
            sys.exc_clear()



    def StartPassiveEffects(self, itemID, typeID):
        effectIDList = self.dogmaStaticMgr.passiveFilteredEffectsByType.get(typeID, [])
        if not effectIDList:
            return 
        dogmaItem = self.dogmaItems[itemID]
        activeEffects = dogmaItem.activeEffects
        brokerEffects = self.dogmaStaticMgr.effects
        shipID = dogmaItem.GetShipID()
        pilotID = dogmaItem.GetPilot()
        otherID = None
        fittableNonSingleton = cfg.invgroups.Get(dogmaItem.groupID).fittableNonSingleton
        sharedEnv = None
        effectsCompleted = set()
        try:
            for effectID in effectIDList:
                if pilotID is None and self.effectCompiler.IsEffectCharacterModifier(effectID):
                    continue
                if effectID in dogmaItem.activeEffects:
                    env = self.GetActiveEffectEnvironment(itemID, effectID)
                    self.LogError('Item', itemID, 'already has effect', effectID, 'env.startTime', env.startTime, blue.os.GetTime())
                    continue
                chanceAttributeID = brokerEffects[effectID].fittingUsageChanceAttributeID
                if chanceAttributeID and self.dogmaStaticMgr.TypeHasAttribute(typeID, chanceAttributeID):
                    if not self.ShouldStartChanceBasedEffect(effectID, itemID, chanceAttributeID):
                        continue
                if self.dogmaStaticMgr.effects[effectID].effectCategory == const.dgmEffSystem:
                    self.StartSystemEffect(itemID, effectID)
                    continue
                pythonEffect = self.effectCompiler.IsEffectPythonOverridden(effectID)
                if sharedEnv and not pythonEffect:
                    env = sharedEnv
                else:
                    with bluepy.Timer('LocationManager::Environment'):
                        info = dogmaItem.GetEnvironmentInfo()
                        env = dogmax.Environment(info.itemID, info.charID, info.shipID, None, info.otherID, effectID, weakref.proxy(self), None)
                    if sharedEnv is None and not pythonEffect:
                        sharedEnv = env
                self.StartEffect(effectID, itemID, env)
                effectsCompleted.add(effectID)

        except Exception:
            log.LogException('Failed to start passive effect')
            return effectsCompleted



    def ShouldStartChanceBasedEffect(self, effectID, itemID, chanceAttributeID):
        return False



    def GetEffect(self, effectID):
        return self.dogmaStaticMgr.effects[effectID]



    def IsItemSubLocation(self, itemKey):
        return type(itemKey) is tuple



    def GetAttributesForType(self, typeID):
        ret = {}
        for attribute in cfg.dgmtypeattribs.get(typeID, []):
            ret[attribute.attributeID] = attribute.value

        return ret



    def RegisterExternalForOwner(self, itemKey, ownerID):
        if not self.externalsByPilot.has_key(ownerID):
            self.externalsByPilot[ownerID] = {}
        self.LogInfo('Registered externalsByPilot item', itemKey, 'for pilot', ownerID)
        self.externalsByPilot[ownerID][itemKey] = None



    def UnregisterExternalForOwner(self, itemKey, ownerID):
        if self.externalsByPilot.has_key(ownerID):
            if self.externalsByPilot[ownerID].has_key(itemKey):
                del self.externalsByPilot[ownerID][itemKey]
                if not len(self.externalsByPilot[ownerID]):
                    del self.externalsByPilot[ownerID]
                self.LogInfo('Unregistering externalsByPilot item', itemKey, 'for pilot', ownerID)
            else:
                self.LogError('Unexpected call (1) to UnregisterExternalForOwner', itemKey, ownerID)
        else:
            self.LogError('Unexpected call (2) to UnregisterExternalForOwner', itemKey, ownerID)



    def UnloadItem(self, itemKey, item = None):
        self.unloadingItems.add(itemKey)
        try:
            self._UnloadItem(itemKey, item)

        finally:
            self.unloadingItems.remove(itemKey)




    def _UnloadItem(self, itemKey, item):
        dogmaItem = self.dogmaItems.get(itemKey, None)
        if dogmaItem is not None:
            if dogmaItem.ownerID is not None:
                ownerID = dogmaItem.ownerID
                if self.externalsByPilot.has_key(ownerID) and self.externalsByPilot[ownerID].has_key(itemKey):
                    self.UnregisterExternalForOwner(itemKey, ownerID)
            dogmaItem.Unload()
            self.RemoveItem(itemKey)
            self.LogInfo('_UnloadItem::Deleting dogmaItem', itemKey)
            del self.dogmaItems[itemKey]



    def GetClassForItem(self, item):
        if item.categoryID == const.categoryShip:
            return dogmax.ShipDogmaItem
        else:
            if item.groupID == const.groupCharacter:
                return dogmax.CharacterDogmaItem
            if item.groupID in [const.groupSurveyProbe, const.groupWarpDisruptionProbe, const.groupScannerProbe]:
                return dogmax.ProbeDogmaItem
            if item.categoryID == const.categoryCharge:
                return dogmax.ChargeDogmaItem
            if item.categoryID in (const.categoryModule, const.categorySubSystem):
                return dogmax.ModuleDogmaItem
            if item.categoryID in (const.categorySkill, const.categoryImplant):
                return dogmax.CharacterFittedDogmaItem
            if item.groupID == const.groupControlTower:
                return dogmax.ControlTowerDogmaItem
            if item.categoryID == const.categoryStructure:
                return dogmax.StructureDogmaItem
            if item.categoryID == const.categoryDrone:
                return dogmax.DroneDogmaItem
            return dogmax.BaseDogmaItem



    def GetInstance(self, item):
        return self.fakeInstanceRow



    def IntroduceNewItem(self, item):
        return self.fakeInstanceRow



    def IsItemWanted(self, typeID, groupID = None):
        return True



    def RemoveDroneFromLocation(self, shipID, droneID):
        dogmaItem = self.dogmaItems[shipID]
        try:
            dogmaItem.drones.remove(droneID)
        except KeyError:
            pass



    def AddDroneToLocation(self, shipID, droneID):
        self.dogmaItems[shipID].drones.add(droneID)



    def IsDroneFitted(self, shipID, droneID):
        try:
            return droneID in self.dogmaItems[shipID].drones
        except KeyError:
            return False



    def RegisterCallback(self, attributeID, cb):
        if isinstance(attributeID, str):
            attributeID = self.dogmaStaticMgr.attributesByName[attributeID].attributeID
        if attributeID in self.attributeChangeCallbacksByAttributeID:
            log.LogException('RegisterCallback::Overwriting a callback %s %s' % (attributeID, self.attributeChangeCallbacksByAttributeID[attributeID].func_name))
        self.attributeChangeCallbacksByAttributeID[attributeID] = cb



    def UnregisterCallback(self, attributeID):
        if isinstance(attributeID, str):
            attributeID = self.dogmaStaticMgr.attributesByName[attributeID].attributeID
        if attributeID in self.attributeChangeCallbacksByAttributeID:
            del self.attributeChangeCallbacksByAttributeID[attributeID]



    def FitItemToSelf(self, item):
        self.OnItemAddedToLocation(item.itemID, item, shipid=item.itemID)



    def GetCharacter(self, itemID, flush = False):
        pass



    def LoadSublocations(self, itemID):
        pass



    def GetAttributesByIndex(self):
        return {}



    def LoadItemsInLocation(self, itemID):
        pass



    def GetItem(self, itemID):
        pass



    def OnSublocationAddedToLocation(self, itemKey, shipid = None, pilotID = None, fitting = False, locationName = None, timerName = 'AddUnknown2'):
        pass



    def OnItemAddedToLocation(self, locationid, item, shipid = None, pilotID = None, fitting = False, locationName = None, timerName = 'AddUnknown1', byUser = False):
        pass



    def GetAttributeValue(self, itemKey, attributeID):
        try:
            return self.dogmaItems[itemKey].attributeCache[attributeID]
        except KeyError:
            sys.exc_clear()
        ret = self.CalculateAttributeValue(itemKey, attributeID)
        self.CacheValue(itemKey, attributeID, ret)
        return ret



    def CalculateAttributeValue(self, itemKey, attributeID):
        if attributeID == const.attributeSkillLevel:
            skillPoints = self.GetAttributeValue(itemKey, const.attributeSkillPoints)
            skillTimeConstant = self.GetAttributeValue(itemKey, const.attributeSkillTimeConstant)
            ret = GetSkillLevelRaw(skillPoints, skillTimeConstant)
            self.CacheValue(itemKey, attributeID, ret)
            return ret
        att = self.dogmaStaticMgr.attributes[attributeID]
        stackable = att.stackable
        highIsGood = att.highIsGood
        category = att.attributeCategory
        isSubLocation = isinstance(itemKey, tuple)
        dogmaItem = self.dogmaItems[itemKey]
        ma = att.maxAttributeID
        cap = None
        if ma:
            cap = self.GetAttributeValue(itemKey, ma)
        dogmaItem = self.dogmaItems[itemKey]
        try:
            ret = dogmaItem.attributes[attributeID]
            if type(ret) is list:
                return self.GetChargedAttributeValue(itemKey, attributeID)
            if ret > cap and cap is not None:
                dogmaItem.attributes[attributeID] = cap
            if ret is None:
                log.LogTraceback('dogmaItems[%s].attributes[%s] == None' % (itemKey, attributeID), channel='svc.dogmaIM')
        except KeyError:
            ret = None
            sys.exc_clear()
        (typeID, groupID, categoryID, ownerID, locationID, unused1,) = dogmaItem.GetItemInfo()
        if ret is None:
            ret = float(self.dogmaStaticMgr.GetTypeAttribute2(typeID, attributeID))
        mod = self.GetModifiersOnAttribute(itemKey, attributeID, locationID, groupID, ownerID, typeID)
        if not stackable:
            d = {}
            opList = []
            overrideMods = []
            for m in mod:
                affectingItemID = m[1]
                if affectingItemID not in self.dogmaItems:
                    log.LogTraceback('Unloaded modifying item %s %s %s %s' % (locationID,
                     attributeID,
                     itemKey,
                     m), channel='svc.dogmaIM')
                    continue
                categoryID = self.dogmaItems[affectingItemID].categoryID
                if categoryID in const.dgmUnnerfedCategories:
                    overrideMods.append(m)
                    continue
                op = m[0]
                v = self.GetAttributeValue(affectingItemID, m[2])
                if v == 1.0 and op in (const.dgmAssPostMul,
                 const.dgmAssPreMul,
                 const.dgmAssPostDiv,
                 const.dgmAssPreDiv):
                    continue
                if v == 0.0 and op == const.dgmAssPostPercent:
                    continue
                if op == const.dgmAssModSub:
                    v = -v
                elif op == const.dgmAssPostPercent:
                    v = (100.0 + v) / 100.0
                if not d.has_key(op):
                    opList.append(op)
                    d[op] = [v]
                else:
                    d[op].append(v)

            for m in overrideMods[:]:
                if m[1] not in self.dogmaItems:
                    self.LogError('GetAttributeValue:ModifierNotLoaded 1', (itemKey, attributeID), m, mod)
                    continue
                v = self.GetAttributeValue(m[1], m[2])
                op = m[0]
                try:
                    ret = const.dgmPreStackingNerfOperators[op](ret, v)
                except KeyError:
                    sys.exc_clear()
                    break
                overrideMods.remove(m)

            if len(d):
                for op in opList:
                    modList = d[op]
                    if op in (const.dgmAssPreMul,
                     const.dgmAssPostMul,
                     const.dgmAssPostPercent,
                     const.dgmAssPreDiv,
                     const.dgmAssPostDiv):

                        def NerfOrderedModifiers(modifierList, preferHigh):
                            if len(modifierList) > 1:
                                modifierList.sort(reverse=preferHigh)
                            factor = 1.0
                            for (i, v,) in enumerate(modifierList):
                                if i > 10:
                                    break
                                denom = math.exp((i / 2.67) ** 2.0)
                                factor *= (v - 1.0) * (1.0 / denom) + 1.0

                            return factor


                        positiveModifiers = []
                        negativeModifiers = []
                        if highIsGood:
                            t = (negativeModifiers, positiveModifiers)
                        else:
                            t = (positiveModifiers, negativeModifiers)
                        if op in (const.dgmAssPreDiv, const.dgmAssPostDiv):
                            for v in modList:
                                t[(v < 1.0)].append(v)

                            positiveIsHigh = not highIsGood
                        else:
                            for v in modList:
                                t[(v > 1.0)].append(v)

                            positiveIsHigh = highIsGood
                        factor = 1.0
                        if len(positiveModifiers):
                            factor *= NerfOrderedModifiers(positiveModifiers, positiveIsHigh)
                        if len(negativeModifiers):
                            factor *= NerfOrderedModifiers(negativeModifiers, not positiveIsHigh)
                        if op in (const.dgmAssPreDiv, const.dgmAssPostDiv):
                            ret /= factor
                        else:
                            ret *= factor
                    elif op in (const.dgmAssPreAssignment, const.dgmAssPostAssignment):
                        if highIsGood:
                            ret = max(modList)
                        else:
                            ret = min(modList)
                    elif op in (const.dgmAssModAdd, const.dgmAssModSub):
                        for v in modList:
                            ret += v


            mod = overrideMods
        for m in mod:
            op = m[0]
            if m[1] not in self.dogmaItems:
                self.LogError('GetAttributeValue:ModifierNotLoaded 2', (itemKey, attributeID), m, mod)
                continue
            v = self.GetAttributeValue(m[1], m[2])
            if op in const.dgmOperators:
                ret = const.dgmOperators[op](ret, v)

        if cap is not None:
            ret = min(ret, cap)
        if category in (10, 11, 12):
            ret = int(ret)
        if attributeID in [const.attributeCpuLoad,
         const.attributePowerLoad,
         const.attributePowerOutput,
         const.attributeCpuOutput]:
            ret = round(ret, 2)
        return ret



    def SetAttributeValue(self, itemKey, attributeID, value, dirty = True, keepLists = True):
        (value, v, dirty,) = self._SetAttributeValue(itemKey, attributeID, value, dirty, keepLists)
        return value



    def _SetAttributeValue(self, itemKey, attributeID, value, dirty, keepLists):
        if itemKey not in self.dogmaItems:
            self.broker.LogInfo('Item', itemKey, 'not loaded')
            return (0, 0, False)
        dogmaItem = self.dogmaItems[itemKey]
        v = dogmaItem.attributes.get(attributeID, None)
        if keepLists and isinstance(v, list):
            if v[0] == value:
                dirty = False
            v[0:2] = [value, blue.os.GetTime(1)]
        elif v is None:
            typeID = dogmaItem.typeID
            v = self.dogmaStaticMgr.GetTypeAttribute2(typeID, attributeID)
        if v == value:
            dirty = False
        if value is None:
            log.LogTraceback('Tried to set attributesByItemAttribute[%s][%s] to None' % (itemKey, attributeID), channel='svc.dogmaIM')
            return (0, 0, False)
        dogmaItem.attributes[attributeID] = value
        self.OnAttributeChanged(attributeID, itemKey, value, v)
        return (value, v, dirty)



    def OnDamageAttributeChange(attributeID, itemKey, value, v):
        pass



    def CacheValue(self, itemKey, attributeID, val):
        if attributeID in self.dogmaStaticMgr.chargedAttributes:
            return 
        self.dogmaItems[itemKey].CacheValue(attributeID, val)



    def ClearCache(self, itemKey, attributeID = None):
        self.dogmaItems[itemKey].ClearCache(attributeID=attributeID)



    def OnAttributeChanged(self, attributeID, itemKey, value = None, oldValue = None):
        self.ClearCache(itemKey, attributeID)
        if value is None:
            value = self.GetAttributeValue(itemKey, attributeID)
        self.CacheValue(itemKey, attributeID, value)
        ownerID = self.dogmaItems[itemKey].ownerID
        if attributeID in self.attributeChangeCallbacksByAttributeID and ownerID not in self.ignoreOwnerEvents:
            try:
                self.attributeChangeCallbacksByAttributeID[attributeID](attributeID, itemKey, value, oldValue)
            except Exception:
                log.LogException('Error broadcasting attribute change %s' % self.attributeChangeCallbacksByAttributeID[attributeID])
        if itemKey in self.modifyingItems and attributeID in self.modifyingItems[itemKey]:
            for ((affectedItemID, affectedAttributeID,), bunch,) in self.modifyingItems[itemKey][attributeID].keys():
                if affectedItemID not in self.unloadingItems and affectedItemID in self.dogmaItems:
                    self.OnAttributeChanged(affectedAttributeID, affectedItemID)

        if self.modifyingLocations.has_key(itemKey):
            if self.modifyingLocations[itemKey].has_key(attributeID):
                for (affectedLocationID, affectedAttributeID, bunch,) in self.modifyingLocations[itemKey][attributeID]:
                    self.OnLocationAttributeChanged(affectedLocationID, affectedAttributeID)

        if self.modifyingLocationGroups.has_key(itemKey):
            if self.modifyingLocationGroups[itemKey].has_key(attributeID):
                for (k, bunch,) in self.modifyingLocationGroups[itemKey][attributeID]:
                    self.OnLocationGroupAttributeChanged(*k)

        if self.modifyingLocationRequiredSkill.has_key(itemKey):
            if self.modifyingLocationRequiredSkill[itemKey].has_key(attributeID):
                for (k, skillID, bunch,) in self.modifyingLocationRequiredSkill[itemKey][attributeID]:
                    (mLocationID, mAttributeID,) = k
                    self.OnLocationRequiredSkillAttributeChanged(mLocationID, set([skillID]), mAttributeID)

        if itemKey in self.modifyingOwnerRequiredSkill:
            if attributeID in self.modifyingOwnerRequiredSkill[itemKey]:
                for (k, skillID, bunch,) in self.modifyingOwnerRequiredSkill[itemKey][attributeID]:
                    self.OnOwnerRequiredSkillAttributeChanged(k[0], set([skillID]), k[1])

        return value



    def IsItemLoaded(self, itemID):
        return itemID not in self.loadingItems and itemID in self.dogmaItems



    def IsItemLoading(self, itemID):
        return itemID in self.loadingItems



    def IsItemUnloading(self, itemKey):
        return itemKey in self.unloadingItems



    def AddModifier(self, op, itemid, attributeid, itemid2, attributeid2):
        if not itemid:
            return 
        itemAttrKey = (itemid, attributeid)
        opItemAttrKey = (op, itemid2, attributeid2)
        if not self.modifiersByItemAttribute.has_key(itemAttrKey):
            self.modifiersByItemAttribute[itemAttrKey] = {}
        elif opItemAttrKey in self.modifiersByItemAttribute[itemAttrKey]:
            if not self.modifyingItems.has_key(itemid2) or not self.modifyingItems[itemid2].has_key(attributeid2) or not self.modifyingItems[itemid2][attributeid2].has_key((itemAttrKey, opItemAttrKey)):
                self.broker.LogError('AddModifier', itemid, attributeid, itemid2, attributeid2, '- had modifier, but no modifying entry (attempting repair)')
            else:
                self.broker.LogError('AddModifier', itemid, attributeid, itemid2, attributeid2, '- already had that modifier registered (skipping)')
                return 
        self.modifiersByItemAttribute[itemAttrKey][opItemAttrKey] = None
        self.AddModifierReverse(itemid2, attributeid2, itemAttrKey, opItemAttrKey)
        if not self.IsItemLoading(itemid):
            oldValue = self.GetAttributeValue(itemid, attributeid)
        else:
            oldValue = None
        self.OnAttributeChanged(attributeid, itemid, oldValue=oldValue)



    def AddModifierReverse(self, itemid2, attributeid2, itemAttrKey, opItemAttrKey):
        if not self.modifyingItems.has_key(itemid2):
            self.modifyingItems[itemid2] = {}
        if not self.modifyingItems[itemid2].has_key(attributeid2):
            self.modifyingItems[itemid2][attributeid2] = {}
        self.modifyingItems[itemid2][attributeid2][(itemAttrKey, opItemAttrKey)] = None



    def RemoveModifier(self, op, itemid, attributeid, itemid2, attributeid2):
        if not itemid:
            return 
        oldValue = None
        itemAttrKey = (itemid, attributeid)
        opItemAttrKey = (op, itemid2, attributeid2)
        if self.modifiersByItemAttribute.has_key(itemAttrKey):
            if itemid in self.dogmaItems:
                oldValue = self.GetAttributeValue(itemid, attributeid)
            if self.modifiersByItemAttribute[itemAttrKey].has_key(opItemAttrKey):
                del self.modifiersByItemAttribute[itemAttrKey][opItemAttrKey]
            else:
                self.LogError('RemoveModifier: modifiersByItemAttribute[ia][xxx]', itemAttrKey, opItemAttrKey)
            if not len(self.modifiersByItemAttribute[itemAttrKey]):
                del self.modifiersByItemAttribute[itemAttrKey]
        else:
            self.LogError('RemoveModifier: modifiersByItemAttribute[xxx]', itemAttrKey, opItemAttrKey)
        if self.modifyingItems.has_key(itemid2):
            if self.modifyingItems[itemid2].has_key(attributeid2):
                rec2 = (itemAttrKey, opItemAttrKey)
                if self.modifyingItems[itemid2][attributeid2].has_key(rec2):
                    del self.modifyingItems[itemid2][attributeid2][rec2]
                else:
                    self.LogError('RemoveModifier: modifyingItems.remove', rec2)
                if not len(self.modifyingItems[itemid2][attributeid2]):
                    del self.modifyingItems[itemid2][attributeid2]
            else:
                self.LogError('RemoveModifier: modifyingItems[itemid2][xxx]', itemAttrKey, opItemAttrKey)
            if not len(self.modifyingItems[itemid2]):
                del self.modifyingItems[itemid2]
        else:
            self.LogError('RemoveModifier: modifyingItems[xxx]', itemAttrKey, opItemAttrKey)
        if not self.IsItemUnloading(itemid) and oldValue is not None:
            self.OnAttributeChanged(attributeid, itemid, oldValue=oldValue)



    def AddLocationGroupModifier(self, op, locationID, groupID, attributeID, itemID2, attributeID2):
        if locationID == 0:
            return 
        lga = (locationID, groupID, attributeID)
        olga = (op, itemID2, attributeID2)
        if not self.modifiersByLocationGroupAttribute.has_key(lga):
            self.modifiersByLocationGroupAttribute[lga] = []
        fwAdded = False
        if olga not in self.modifiersByLocationGroupAttribute[lga]:
            self.modifiersByLocationGroupAttribute[lga].append(olga)
            fwAdded = True
        bwAdded = self.AddLocationGroupModifierReverse(itemID2, attributeID2, lga, olga)
        if self.extraTracebacks and (not fwAdded or not bwAdded):
            log.LogTraceback('AddLocationGroupModifier found inconsistencies lga: %s olga: %s (%d %d)' % (lga,
             olga,
             fwAdded,
             bwAdded), channel='svc.dogmaIM')
        k = ('lga', lga)
        if not self.locationModifiers.has_key(locationID):
            self.locationModifiers[locationID] = {}
        self.locationModifiers[locationID][k] = None
        self.OnLocationGroupAttributeChanged(locationID, groupID, attributeID)



    def AddLocationGroupModifierReverse(self, itemid2, attributeid2, lga, olga):
        if not self.modifyingLocationGroups.has_key(itemid2):
            self.modifyingLocationGroups[itemid2] = {}
        if not self.modifyingLocationGroups[itemid2].has_key(attributeid2):
            self.modifyingLocationGroups[itemid2][attributeid2] = []
        k = (lga, olga)
        if k in self.modifyingLocationGroups[itemid2][attributeid2]:
            return False
        self.modifyingLocationGroups[itemid2][attributeid2].append(k)
        return True



    def RemoveLocationGroupModifier(self, op, locationID, groupID, attributeID, itemID2, attributeID2):
        if locationID == 0:
            return 
        k = (locationID, groupID, attributeID)
        rec = (op, itemID2, attributeID2)
        if self.modifiersByLocationGroupAttribute.has_key(k):
            try:
                self.modifiersByLocationGroupAttribute[k].remove(rec)
            except ValueError:
                self.LogError('RemoveLocationGroupModifier: modifiersByLocationGroupAttribute.remove', k, rec)
                sys.exc_clear()
            if not len(self.modifiersByLocationGroupAttribute[k]):
                del self.modifiersByLocationGroupAttribute[k]
        else:
            self.LogError('RemoveLocationGroupModifier: modifiersByLocationGroupAttribute[xxx]', k, rec)
        if self.modifyingLocationGroups.has_key(itemID2):
            if self.modifyingLocationGroups[itemID2].has_key(attributeID2):
                rec2 = (k, (op, itemID2, attributeID2))
                try:
                    self.modifyingLocationGroups[itemID2][attributeID2].remove(rec2)
                except ValueError:
                    self.LogError('RemoveLocationGroupModifier: modifyingLocationGroups.remove', rec2)
                    sys.exc_clear()
                if not len(self.modifyingLocationGroups[itemID2][attributeID2]):
                    del self.modifyingLocationGroups[itemID2][attributeID2]
            else:
                self.LogError('RemoveLocationGroupModifier: modifyingLocationGroups[itemID2][xxx]', k, rec)
            if not len(self.modifyingLocationGroups[itemID2]):
                del self.modifyingLocationGroups[itemID2]
        else:
            self.LogError('RemoveLocationGroupModifier: modifyingLocationGroups[xxx]', k, rec)
        self.RemoveLocationModifierEntry('lga', k, not self.modifiersByLocationGroupAttribute.has_key(k))
        self.OnLocationGroupAttributeChanged(locationID, groupID, attributeID)



    def StartModuleOnlineEffect(self, itemID, pilotID, locationID, locationName, timerName, context = None):
        environment = dogmax.Environment(itemID, pilotID, locationID, None, None, const.effectOnline, weakref.proxy(self), None)
        if context is not None:
            for (k, v,) in context.iteritems():
                setattr(environment, k, v)

        try:
            self.StartEffect(const.effectOnline, itemID, environment, 1, byUser=True)
        except UserError as e:
            if e.msg.startswith('EffectAlreadyActive'):
                self.LogInfo('Tried to online', itemID, 'in', locationID, 'but failed because of', e)
            else:
                self.SetAttributeValue(itemID, const.attributeIsOnline, 0)
            sys.exc_clear()



    def RemoveLocationModifierEntry(self, mt, mk, noTypeEntries = True):
        locationID = mk[0]
        k = (mt, mk)
        if self.locationModifiers.has_key(locationID):
            if self.locationModifiers[locationID].has_key(k):
                if noTypeEntries:
                    del self.locationModifiers[locationID][k]
                if not len(self.locationModifiers[locationID]):
                    del self.locationModifiers[locationID]
            else:
                self.LogError('RemoveLocationModifierEntry: modifier entry missing', k)
        else:
            self.LogError('RemoveLocationModifierEntry: location entry missing', k)



    def AddLocationRequiredSkillModifier(self, op, locationID, skillID, attributeID, itemID2, attributeID2):
        if locationID == 0:
            return 
        locAttrKey = (locationID, attributeID)
        opItemAttrKey = (op, itemID2, attributeID2)
        if not self.modifiersByLocationRequiredSkillAttribute.has_key(locAttrKey):
            self.modifiersByLocationRequiredSkillAttribute[locAttrKey] = {}
        if not self.modifiersByLocationRequiredSkillAttribute[locAttrKey].has_key(skillID):
            self.modifiersByLocationRequiredSkillAttribute[locAttrKey][skillID] = []
        fwAdded = False
        if opItemAttrKey not in self.modifiersByLocationRequiredSkillAttribute[locAttrKey][skillID]:
            self.modifiersByLocationRequiredSkillAttribute[locAttrKey][skillID].append(opItemAttrKey)
            fwAdded = True
        bwAdded = self.AddLocationRequiredSkillModifierReverse(itemID2, attributeID2, skillID, locAttrKey, opItemAttrKey)
        if self.extraTracebacks and (not fwAdded or not bwAdded):
            log.LogTraceback('AddLocationRequiredSkillModifier found inconsistencies la: %s oia: %s (%d %d)' % (locAttrKey,
             opItemAttrKey,
             fwAdded,
             bwAdded), channel='svc.dogmaIM')
        k = ('lrsa', locAttrKey)
        if not self.locationModifiers.has_key(locationID):
            self.locationModifiers[locationID] = {}
        self.locationModifiers[locationID][k] = None
        try:
            self.delayAttributePropagation[locationID][(self.OnLocationRequiredSkillAttributeChanged, attributeID)].add(skillID)
        except KeyError:
            self.OnLocationRequiredSkillAttributeChanged(locationID, set([skillID]), attributeID)



    def AddLocationRequiredSkillModifierReverse(self, itemid2, attributeid2, skillID, locAttrKey, opItemAttrKey):
        if not self.modifyingLocationRequiredSkill.has_key(itemid2):
            self.modifyingLocationRequiredSkill[itemid2] = {}
        if not self.modifyingLocationRequiredSkill[itemid2].has_key(attributeid2):
            self.modifyingLocationRequiredSkill[itemid2][attributeid2] = []
        k = (locAttrKey, skillID, opItemAttrKey)
        if k in self.modifyingLocationRequiredSkill[itemid2][attributeid2]:
            return False
        self.modifyingLocationRequiredSkill[itemid2][attributeid2].append(k)
        return True



    def RemoveLocationRequiredSkillModifier(self, op, locationID, skillID, attributeID, itemID2, attributeID2):
        if locationID == 0:
            return 
        la = (locationID, attributeID)
        rec = (op, itemID2, attributeID2)
        if self.modifiersByLocationRequiredSkillAttribute.has_key(la):
            if self.modifiersByLocationRequiredSkillAttribute[la].has_key(skillID):
                try:
                    self.modifiersByLocationRequiredSkillAttribute[la][skillID].remove(rec)
                except ValueError:
                    self.LogError('RemoveLocationRequiredSkillModifier: modifiersByLocationRequiredSkillAttribute.remove', la, skillID, rec)
                    sys.exc_clear()
                if not len(self.modifiersByLocationRequiredSkillAttribute[la][skillID]):
                    del self.modifiersByLocationRequiredSkillAttribute[la][skillID]
            else:
                self.LogError('RemoveLocationRequiredSkillModifier: modifiersByLocationRequiredSkillAttribute[la][xxx]', la, skillID, rec)
            if not len(self.modifiersByLocationRequiredSkillAttribute[la]):
                del self.modifiersByLocationRequiredSkillAttribute[la]
        else:
            self.LogError('RemoveLocationRequiredSkillModifier: modifiersByLocationRequiredSkillAttribute[xxx]', la, skillID, rec)
        if self.modifyingLocationRequiredSkill.has_key(itemID2):
            if self.modifyingLocationRequiredSkill[itemID2].has_key(attributeID2):
                rec2 = (la, skillID, rec)
                try:
                    self.modifyingLocationRequiredSkill[itemID2][attributeID2].remove(rec2)
                except ValueError:
                    self.LogError('RemoveLocationRequiredSkillModifier: modifyingLocationRequiredSkill.remove', rec2)
                    sys.exc_clear()
                if not len(self.modifyingLocationRequiredSkill[itemID2][attributeID2]):
                    del self.modifyingLocationRequiredSkill[itemID2][attributeID2]
            else:
                self.LogError('RemoveLocationRequiredSkillModifier: modifyingLocationRequiredSkill[attributeID2][xxx]', la, skillID, rec)
            if not len(self.modifyingLocationRequiredSkill[itemID2]):
                del self.modifyingLocationRequiredSkill[itemID2]
        else:
            self.LogError('RemoveLocationRequiredSkillModifier: modifyingLocationRequiredSkill[xxx]', la, skillID, rec)
        self.RemoveLocationModifierEntry('lrsa', la, not self.modifiersByLocationRequiredSkillAttribute.has_key(la))
        try:
            self.delayAttributePropagation[locationID][(self.OnLocationRequiredSkillAttributeChanged, attributeID)].add(skillID)
        except KeyError:
            self.OnLocationRequiredSkillAttributeChanged(locationID, set([skillID]), attributeID)



    def AddOwnerRequiredSkillModifier(self, op, ownerID, skillID, attributeID, itemID2, attributeID2):
        if not ownerID:
            return 
        oa = (ownerID, attributeID)
        oia = (op, itemID2, attributeID2)
        if not self.modifiersByOwnerRequiredSkillAttribute.has_key(oa):
            self.modifiersByOwnerRequiredSkillAttribute[oa] = {}
        if not self.modifiersByOwnerRequiredSkillAttribute[oa].has_key(skillID):
            self.modifiersByOwnerRequiredSkillAttribute[oa][skillID] = []
        fwAdded = False
        if oia not in self.modifiersByOwnerRequiredSkillAttribute[oa][skillID]:
            self.modifiersByOwnerRequiredSkillAttribute[oa][skillID].append(oia)
            fwAdded = True
        bwAdded = self.AddOwnerRequiredSkillModifierReverse(itemID2, attributeID2, skillID, oa, oia)
        if self.extraTracebacks and (not fwAdded or not bwAdded):
            log.LogTraceback('AddOwnerRequiredSkillModifier found inconsistencies oa: %s oia: %s (%d %d)' % (oa,
             oia,
             fwAdded,
             bwAdded), channel='svc.dogmaIM')
        try:
            self.delayAttributePropagation[ownerID][(self.OnOwnerRequiredSkillAttributeChanged, attributeID)].add(skillID)
        except KeyError:
            self.OnOwnerRequiredSkillAttributeChanged(ownerID, set([skillID]), attributeID)



    def AddOwnerRequiredSkillModifierReverse(self, itemID2, attributeID2, skillID, oa, oia):
        if not self.modifyingOwnerRequiredSkill.has_key(itemID2):
            self.modifyingOwnerRequiredSkill[itemID2] = {}
        if not self.modifyingOwnerRequiredSkill[itemID2].has_key(attributeID2):
            self.modifyingOwnerRequiredSkill[itemID2][attributeID2] = []
        k = (oa, skillID, oia)
        if k in self.modifyingOwnerRequiredSkill[itemID2][attributeID2]:
            return False
        self.modifyingOwnerRequiredSkill[itemID2][attributeID2].append((oa, skillID, oia))
        return True



    def RemoveOwnerRequiredSkillModifier(self, op, ownerID, skillID, attributeID, itemID2, attributeID2):
        if not ownerID:
            return 
        oa = (ownerID, attributeID)
        rec = (op, itemID2, attributeID2)
        if self.modifiersByOwnerRequiredSkillAttribute.has_key(oa):
            if self.modifiersByOwnerRequiredSkillAttribute[oa].has_key(skillID):
                try:
                    self.modifiersByOwnerRequiredSkillAttribute[oa][skillID].remove(rec)
                except ValueError:
                    self.LogError('RemoveOwnerRequiredSkillModifier: modifiersByOwnerRequiredSkillAttribute.remove', oa, skillID, rec)
                    sys.exc_clear()
                if not len(self.modifiersByOwnerRequiredSkillAttribute[oa][skillID]):
                    del self.modifiersByOwnerRequiredSkillAttribute[oa][skillID]
            else:
                self.LogError('RemoveOwnerRequiredSkillModifier: modifiersByOwnerRequiredSkillAttribute[oa][xxx]', oa, skillID, rec)
            if not len(self.modifiersByOwnerRequiredSkillAttribute[oa]):
                del self.modifiersByOwnerRequiredSkillAttribute[oa]
        else:
            self.LogError('RemoveOwnerRequiredSkillModifier: modifiersByOwnerRequiredSkillAttribute[xxx]', oa, skillID, rec)
        if self.modifyingOwnerRequiredSkill.has_key(itemID2):
            if self.modifyingOwnerRequiredSkill[itemID2].has_key(attributeID2):
                rec2 = (oa, skillID, rec)
                try:
                    self.modifyingOwnerRequiredSkill[itemID2][attributeID2].remove(rec2)
                except ValueError:
                    self.LogError('RemoveOwnerRequiredSkillModifier: modifyingOwnerRequiredSkill.remove', rec2)
                    sys.exc_clear()
                if not len(self.modifyingOwnerRequiredSkill[itemID2][attributeID2]):
                    del self.modifyingOwnerRequiredSkill[itemID2][attributeID2]
            else:
                self.LogError('RemoveOwnerRequiredSkillModifier: modifyingOwnerRequiredSkill[oa][xxx]', oa, skillID, rec)
            if not len(self.modifyingOwnerRequiredSkill[itemID2]):
                del self.modifyingOwnerRequiredSkill[itemID2]
        else:
            self.LogError('RemoveOwnerRequiredSkillModifier: modifyingOwnerRequiredSkill[xxx]', oa, skillID, rec)
        try:
            self.delayAttributePropagation[ownerID][(self.OnOwnerRequiredSkillAttributeChanged, attributeID)].add(skillID)
        except KeyError:
            self.OnOwnerRequiredSkillAttributeChanged(ownerID, set([skillID]), attributeID)



    def AddLocationModifier(self, op, locationid, attributeid, itemid2, attributeid2):
        if locationid == 0:
            return 
        la = (locationid, attributeid)
        ola = (op, itemid2, attributeid2)
        if not self.modifiersByLocationAttribute.has_key(la):
            self.modifiersByLocationAttribute[la] = []
        fwAdded = False
        if ola not in self.modifiersByLocationAttribute[la]:
            self.modifiersByLocationAttribute[la].append(ola)
            fwAdded = True
        bwAdded = self.AddLocationModifierReverse(itemid2, attributeid2, la, ola)
        if self.extraTracebacks and (not fwAdded or not bwAdded):
            log.LogTraceback('AddLocationModifier found inconsistencies la: %s ola: %s (%d %d)' % (la,
             ola,
             fwAdded,
             bwAdded), channel='svc.dogmaIM')
        k = ('la', la)
        if not self.locationModifiers.has_key(locationid):
            self.locationModifiers[locationid] = {}
        self.locationModifiers[locationid][k] = None
        self.OnLocationAttributeChanged(attributeid, locationid)



    def AddLocationModifierReverse(self, itemid2, attributeid2, la, ola):
        if not self.modifyingLocations.has_key(itemid2):
            self.modifyingLocations[itemid2] = {}
        if not self.modifyingLocations[itemid2].has_key(attributeid2):
            self.modifyingLocations[itemid2][attributeid2] = []
        k = (la[0], la[1], ola)
        if k in self.modifyingLocations[itemid2][attributeid2]:
            return False
        self.modifyingLocations[itemid2][attributeid2].append(k)
        return True



    def RemoveLocationModifier(self, op, locationid, attributeid, itemid2, attributeid2):
        if locationid == 0:
            return 
        la = (locationid, attributeid)
        rec = (op, itemid2, attributeid2)
        if self.modifiersByLocationAttribute.has_key(la):
            try:
                self.modifiersByLocationAttribute[la].remove(rec)
            except ValueError:
                self.LogError('RemoveLocationModifier: modifiersByLocationAttribute.remove', la, rec)
                sys.exc_clear()
            if not len(self.modifiersByLocationAttribute[la]):
                del self.modifiersByLocationAttribute[la]
        else:
            self.LogError('RemoveLocationModifier: modifiersByLocationAttribute[xxx]', la, rec)
        if self.modifyingLocations.has_key(itemid2):
            if self.modifyingLocations[itemid2].has_key(attributeid2):
                rec2 = (locationid, attributeid, rec)
                try:
                    self.modifyingLocations[itemid2][attributeid2].remove(rec2)
                except ValueError:
                    self.LogError('RemoveLocationModifier: modifyingLocations.remove', rec2)
                    sys.exc_clear()
                if not len(self.modifyingLocations[itemid2][attributeid2]):
                    del self.modifyingLocations[itemid2][attributeid2]
            else:
                self.LogError('RemoveLocationModifier: modifyingLocations[itemid2][xxx]', la, rec)
            if not len(self.modifyingLocations[itemid2]):
                del self.modifyingLocations[itemid2]
        else:
            self.LogError('RemoveLocationModifier: modifyingLocations[xxx]', la, rec)
        self.RemoveLocationModifierEntry('la', la, not self.modifiersByLocationAttribute.has_key(la))
        self.OnLocationAttributeChanged(attributeid, locationid)



    def AddGangRequiredSkillModifier(self, shipID, op, skillID, attributeID, itemID, affectingAttributeID):
        pass



    def RemoveGangRequiredSkillModifier(self, shipID, op, skillID, attributeID, itemID, affectingAttributeID):
        pass



    def AddGangShipModifier(self, shipID, op, attributeID, itemID, affectingAttributeID):
        pass



    def RemoveGangShipModifier(self, shipID, op, attributeID, itemID, affectingAttributeID):
        pass



    def AddGangGroupModifier(self, shipID, op, groupID, attributeID, itemID, affectingAttributeID):
        pass



    def RemoveGangGroupModifier(self, shipID, op, groupID, attributeID, itemID, affectingAttributeID):
        pass



    def RemoveItem(self, itemID):
        if self.modifyingItems.has_key(itemID):
            for (attID, recs,) in self.modifyingItems[itemID].iteritems():
                for (itemAttrKey, opItemAttrKey,) in recs.iterkeys():
                    if not self.modifiersByItemAttribute.has_key(itemAttrKey):
                        self.LogError('RemoveItem: IA entry missing', itemID, itemAttrKey, opItemAttrKey)
                        continue
                    if self.modifiersByItemAttribute[itemAttrKey].has_key(opItemAttrKey):
                        del self.modifiersByItemAttribute[itemAttrKey][opItemAttrKey]
                        if not len(self.modifiersByItemAttribute[itemAttrKey]):
                            del self.modifiersByItemAttribute[itemAttrKey]
                    else:
                        self.LogError('RemoveItem: IA record missing', itemID, itemAttrKey, opItemAttrKey)


            del self.modifyingItems[itemID]
        if self.modifyingLocations.has_key(itemID):
            for (attID, recs,) in self.modifyingLocations[itemID].iteritems():
                for (locationid, attributeid, record,) in recs:
                    la = (locationid, attributeid)
                    if not self.modifiersByLocationAttribute.has_key(la):
                        self.LogError('RemoveItem: LA entry missing', itemID, la)
                        continue
                    try:
                        self.modifiersByLocationAttribute[la].remove(record)
                    except ValueError:
                        self.LogError('RemoveItem: LA record missing', itemID, la, record)
                        sys.exc_clear()
                    if not len(self.modifiersByLocationAttribute[la]):
                        del self.modifiersByLocationAttribute[la]
                        self.RemoveLocationModifierEntry('la', la)


            del self.modifyingLocations[itemID]
        if self.modifyingLocationGroups.has_key(itemID):
            for (attID, recs,) in self.modifyingLocationGroups[itemID].iteritems():
                for (lga, record,) in recs:
                    if not self.modifiersByLocationGroupAttribute.has_key(lga):
                        self.LogError('RemoveItem: lga entry missing)', itemID, lga, record)
                        continue
                    try:
                        self.modifiersByLocationGroupAttribute[lga].remove(record)
                    except ValueError:
                        self.LogError('RemoveItem: lga record missing', itemID, lga, record)
                        sys.exc_clear()
                    if not len(self.modifiersByLocationGroupAttribute[lga]):
                        del self.modifiersByLocationGroupAttribute[lga]
                        self.RemoveLocationModifierEntry('lga', lga)


            del self.modifyingLocationGroups[itemID]
        if self.modifyingLocationRequiredSkill.has_key(itemID):
            for (attID, recs,) in self.modifyingLocationRequiredSkill[itemID].iteritems():
                for (la, skillID, record,) in recs:
                    if not self.modifiersByLocationRequiredSkillAttribute.has_key(la):
                        self.LogError('RemoveItem: LRSA entry missing', itemID, la, skillID, record)
                        continue
                    if self.modifiersByLocationRequiredSkillAttribute[la].has_key(skillID):
                        try:
                            self.modifiersByLocationRequiredSkillAttribute[la][skillID].remove(record)
                        except ValueError:
                            self.LogError('RemoveItem: LRSA record missing', itemID, la, skillID, record)
                            sys.exc_clear()
                        if not len(self.modifiersByLocationRequiredSkillAttribute[la][skillID]):
                            del self.modifiersByLocationRequiredSkillAttribute[la][skillID]
                    else:
                        self.LogError('RemoveItem: LRSA skill entry missing', itemID, (la, skillID, record))
                    if not len(self.modifiersByLocationRequiredSkillAttribute[la]):
                        del self.modifiersByLocationRequiredSkillAttribute[la]
                        self.RemoveLocationModifierEntry('lrsa', la)


            del self.modifyingLocationRequiredSkill[itemID]
        if self.modifyingOwnerRequiredSkill.has_key(itemID):
            for (attID, recs,) in self.modifyingOwnerRequiredSkill[itemID].iteritems():
                for (oa, skillID, record,) in recs:
                    if not self.modifiersByOwnerRequiredSkillAttribute.has_key(oa):
                        self.LogError('RemoveItem: ORSA entry missing', itemID, oa, skillID, record)
                        continue
                    if self.modifiersByOwnerRequiredSkillAttribute[oa].has_key(skillID):
                        try:
                            self.modifiersByOwnerRequiredSkillAttribute[oa][skillID].remove(record)
                        except ValueError:
                            self.LogError('RemoveItem: ORSA record missing', itemID, oa, skillID, record)
                            sys.exc_clear()
                        if not len(self.modifiersByOwnerRequiredSkillAttribute[oa][skillID]):
                            del self.modifiersByOwnerRequiredSkillAttribute[oa][skillID]
                    else:
                        self.LogError('RemoveItem: ORSA skill entry missing', itemID, oa, skillID, record)
                    if not len(self.modifiersByOwnerRequiredSkillAttribute[oa]):
                        del self.modifiersByOwnerRequiredSkillAttribute[oa]


            del self.modifyingOwnerRequiredSkill[itemID]



    def SetLocationModifier(self, itemID, state):
        if state is not None:
            self.locationModifiers[itemID] = state
        elif itemID in self.locationModifiers:
            del self.locationModifiers[itemID]



    def LogModifiers(self, itemID, attributeID, locationID, ownerID, typeID, groupID, force):
        ret = []
        GAV = self.GetAttributeValue
        if (itemID, attributeID) in self.modifiersByItemAttribute:
            imod = self.modifiersByItemAttribute[(itemID, attributeID)].keys()
        else:
            imod = []
        if self.modifiersByLocationAttribute.has_key((locationID, attributeID)):
            lmod = self.modifiersByLocationAttribute[(locationID, attributeID)]
        else:
            lmod = []
        k = (locationID, groupID, attributeID)
        if self.modifiersByLocationGroupAttribute.has_key(k):
            lgmod = self.modifiersByLocationGroupAttribute[k]
        else:
            lgmod = []
        lrsmod = []
        if self.modifiersByLocationRequiredSkillAttribute.has_key((locationID, attributeID)):
            moddict = self.modifiersByLocationRequiredSkillAttribute[(locationID, attributeID)]
            rs = self.dogmaStaticMgr.GetRequiredSkills(typeID)
            for k in rs:
                if moddict.has_key(k):
                    lrsmod.extend(moddict[k])

        orsmod = []
        if self.modifiersByOwnerRequiredSkillAttribute.has_key((ownerID, attributeID)):
            moddict = self.modifiersByOwnerRequiredSkillAttribute[(ownerID, attributeID)]
            rs = self.dogmaStaticMgr.GetRequiredSkills(typeID)
            for k in rs:
                if moddict.has_key(k):
                    orsmod.extend(moddict[k])

        for m in imod:
            desc = 'Straight item modification:'
            op = assoc[m[0]]
            itemName = self.GetLocName(m[1])
            attributeName = self.dogmaStaticMgr.attributes[m[2]].attributeName
            desc += ' %s, %s of %s' % (op, attributeName, itemName)
            ret.append(desc)
            try:
                val = GAV(m[1], m[2])
                success = 1
            except StandardError:
                val = 'No idea!'
                sys.exc_clear()
            ret.append('Value:%s' % val)

        for m in lmod:
            desc = 'Location modification:'
            op = assoc[m[0]]
            itemName = self.GetLocName(m[1])
            attributeName = self.dogmaStaticMgr.attributes[m[2]].attributeName
            desc += ' %s, %s of %s' % (op, attributeName, itemName)
            ret.append(desc)
            try:
                val = GAV(m[1], m[2])
                success = 1
            except StandardError:
                val = 'No idea!'
                sys.exc_clear()
            ret.append('Value:%s' % val)

        for m in lgmod:
            desc = 'Location/Group modification:'
            op = assoc[m[0]]
            itemName = self.GetLocName(m[1])
            attributeName = self.dogmaStaticMgr.attributes[m[2]].attributeName
            desc += ' %s, %s of %s' % (op, attributeName, itemName)
            ret.append(desc)
            try:
                val = GAV(m[1], m[2])
                success = 1
            except StandardError:
                val = 'No idea!'
                sys.exc_clear()
            ret.append('Value:%s' % val)

        for m in lrsmod:
            desc = 'Location/Required Skill modification:'
            op = assoc[m[0]]
            itemName = self.GetLocName(m[1])
            attributeName = self.dogmaStaticMgr.attributes[m[2]].attributeName
            desc += ' %s, %s of %s' % (op, attributeName, itemName)
            ret.append(desc)
            try:
                val = GAV(m[1], m[2])
                success = 1
            except StandardError:
                val = 'No idea!'
                sys.exc_clear()
            ret.append('Value:%s' % val)

        for m in orsmod:
            desc = 'Owner/Required Skill modification:'
            op = assoc[m[0]]
            itemName = self.GetLocName(m[1])
            attributeName = self.dogmaStaticMgr.attributes[m[2]].attributeName
            desc += ' %s, %s of %s' % (op, attributeName, itemName)
            ret.append(desc)
            try:
                val = GAV(m[1], m[2])
                success = 1
            except StandardError:
                val = 'No idea!'
                sys.exc_clear()
            ret.append('Value:%s' % val)

        if force or not session or not session.charid:
            for line in ret:
                self.LogError(line)

        return ret



    def GetModifiersOnAttribute(self, itemKey, attributeID, locationID, groupID, ownerID, typeID):
        mod = []
        try:
            mod.extend(self.modifiersByItemAttribute[(itemKey, attributeID)].iterkeys())
        except KeyError:
            pass
        try:
            mod.extend(self.modifiersByLocationAttribute[(locationID, attributeID)])
        except KeyError:
            pass
        try:
            mod.extend(self.modifiersByLocationGroupAttribute[(locationID, groupID, attributeID)])
        except KeyError:
            pass
        try:
            rs = self.dogmaStaticMgr.GetRequiredSkills(typeID)
            moddict = self.modifiersByLocationRequiredSkillAttribute[(locationID, attributeID)]
            for k in rs:
                try:
                    mod.extend(moddict[k])
                except KeyError:
                    pass

        except KeyError:
            pass
        try:
            moddict = self.modifiersByOwnerRequiredSkillAttribute[(ownerID, attributeID)]
            for k in rs:
                try:
                    mod.extend(moddict[k])
                except KeyError:
                    pass

        except KeyError:
            pass
        mod.sort()
        return mod



    def GetAttributeItemModifiers(self, itemID, attributeID):
        modifierList = []
        if (itemID, attributeID) not in self.modifiersByItemAttribute:
            return modifierList
        for (modifierOperation, modifyingItem, modifierAttributeID,) in self.modifiersByItemAttribute[(itemID, attributeID)].iterkeys():
            modifierValue = self.GetAttributeValue(modifyingItem, modifierAttributeID)
            modifyingItemTypeID = None
            if modifyingItem in self.dogmaItems:
                modifyingItemTypeID = self.dogmaItems[modifyingItem].typeID
            if modifierValue == 0.0 and modifierOperation in ():
                continue
            elif modifierValue == 1.0 and modifierOperation in ():
                continue
            if modifierValue == 1.0 and modifierOperation in (const.dgmAssPostMul,
             const.dgmAssPreMul,
             const.dgmAssPostDiv,
             const.dgmAssPreDiv):
                continue
            if modifierValue == 0.0 and modifierOperation in (const.dgmAssPostPercent, const.dgmAssModAdd, const.dgmAssModSub):
                continue
            modifierList.append((modifyingItem,
             modifyingItemTypeID,
             modifierOperation,
             modifierValue))

        return modifierList



    def OnLocationAttributeChanged(self, attributeID, locationID):
        try:
            fittedItems = self.dogmaItems[locationID].GetFittedItems()
        except KeyError:
            self.LogInfo('OnLocationAttributeChanged::location not loaded', locationID, attributeID)
            return 
        except AttributeError:
            self.LogInfo("OnLocationAttributeChanged::location doesn't have fitted items", locationID)
            return 
        for moduleID in fittedItems:
            self.OnAttributeChanged(attributeID, moduleID)




    def OnLocationRequiredSkillAttributeChanged(self, locationID, skillIDs, attributeID):
        try:
            fittedItems = self.dogmaItems[locationID].GetFittedItems()
        except KeyError:
            self.LogInfo('OnLocationRequiredSkillAttributeChanged::location not loaded', locationID, attributeID)
            return 
        except AttributeError:
            self.LogInfo("OnLocationRequiredSkillAttributeChanged::location doesn't have fitted items", locationID)
            return 
        for (itemKey, dogmaItem,) in fittedItems.iteritems():
            try:
                typeID = dogmaItem.typeID
            except Exception:
                log.LogException()
                sys.exc_clear()
                continue
            if skillIDs.intersection(self.dogmaStaticMgr.GetRequiredSkills(typeID)):
                self.OnAttributeChanged(attributeID, itemKey)




    def OnOwnerRequiredSkillAttributeChanged(self, ownerID, skillIDs, attributeID):
        try:
            ownerDogmaItem = self.dogmaItems[ownerID]
        except KeyError:
            self.LogInfo('OnOwnerRequiredSkillAttributeChanged::owner not loaded', ownerID, attributeID)
            sys.exc_clear()
        else:
            self.PropagateOwnerRequiredSkillAttributeChanged(ownerDogmaItem.GetFittedItems(), skillIDs, attributeID)
            location = ownerDogmaItem.location
            if location is not None:
                self.PropagateOwnerRequiredSkillAttributeChanged(location.GetFittedItems(), skillIDs, attributeID)
        self.PropagateOwnerRequiredSkillAttributeChanged(self.externalsByPilot.get(ownerID, {}), skillIDs, attributeID)



    def PropagateOwnerRequiredSkillAttributeChanged(self, d, skillIDs, attributeID):
        removals = []
        for itemKey in d:
            typeID = None
            try:
                typeID = self.dogmaItems[itemKey].typeID
            except KeyError:
                if isinstance(itemKey, tuple):
                    typeID = itemKey[2]
                else:
                    try:
                        typeID = self.inventory2.GetItem(itemKey)[const.ixTypeID]
                    except RuntimeError as e:
                        if len(e.args) and e.args[0].startswith('GetItem: Item not here'):
                            log.LogError("OnLocationRequiredSkillAttributeChanged::inventory item doesn't exist", itemKey)
                        else:
                            log.LogException('PropagateOwnerRequiredSkillAttributeChanged - failed to get the item type')
                        sys.exc_clear()
                        continue
                self.LogError("OnLocationRequiredSkillAttributeChanged::dogmaItem doesn't exist", itemKey)
                sys.exc_clear()
            if typeID is not None and skillIDs.intersection(self.dogmaStaticMgr.GetRequiredSkills(typeID)):
                self.OnAttributeChanged(attributeID, itemKey)

        for itemKey in removals:
            del d[itemKey]




    def GetModuleListByShipGroup(self, locationID, groupID):
        return self.moduleListsByShipGroup.get(locationID, {}).get(groupID, [])



    def OnLocationGroupAttributeChanged(self, locationID, groupID, attributeID):
        modules = self.moduleListsByShipGroup.get(locationID, {}).get(groupID, [])
        for moduleID in modules:
            if moduleID not in self.unloadingItems:
                self.OnAttributeChanged(attributeID, moduleID)




    def RecalculateAffectedLocationModifiers(self, itemKey, itemTypeID, itemGroupID, oldLocationID, fromOldLocation = False):
        if oldLocationID is None and fromOldLocation is True:
            return 
        dogmaItem = self.dogmaItems[itemKey]
        if fromOldLocation:
            locationID = oldLocationID
        else:
            locationID = dogmaItem.locationID
        if not locationID or not self.locationModifiers.has_key(locationID):
            return 
        requiredUpdates = set()
        requiredSkillTypes = self.dogmaStaticMgr.GetRequiredSkills(itemTypeID)
        for k in self.locationModifiers[locationID]:
            if k[0] == 'lga':
                if itemGroupID == k[1][1]:
                    requiredUpdates.add(k[1][2])
            elif k[0] == 'lrsa':
                attributeID = k[1][1]
                for skillTypeID in self.modifiersByLocationRequiredSkillAttribute.get(k[1], {}).iterkeys():
                    if skillTypeID in requiredSkillTypes:
                        requiredUpdates.add(attributeID)

            elif k[0] == 'la':
                requiredUpdates.add(k[1][1])

        for attributeID in requiredUpdates:
            self.OnAttributeChanged(attributeID, itemKey)




    def EnterCriticalSection(self, k, v):
        if (k, v) not in self.crits:
            self.crits[(k, v)] = uthread.CriticalSection((k, v))
        self.crits[(k, v)].acquire()



    def LeaveCriticalSection(self, k, v):
        self.crits[(k, v)].release()
        if (k, v) in self.crits and self.crits[(k, v)].IsCool():
            del self.crits[(k, v)]



    def LogInfo(self, *args):
        return self.broker.LogInfo(self.locationID, *args)



    def LogWarn(self, *args):
        return self.broker.LogWarn(self.locationID, *args)



    def LogError(self, *args):
        return self.broker.LogError(self.locationID, *args)



    def AddIgnoreOwnerEventsCount(self, ownerID):
        if ownerID not in self.ignoreOwnerEvents:
            self.ignoreOwnerEvents[ownerID] = 1
        else:
            self.ignoreOwnerEvents[ownerID] += 1



    def DecreaseOwnerRequiredEventsCount(self, ownerID):
        self.ignoreOwnerEvents[ownerID] -= 1
        if self.ignoreOwnerEvents[ownerID] < 1:
            del self.ignoreOwnerEvents[ownerID]



exports = {'dogmax.BaseDogmaLocation': BaseDogmaLocation}

