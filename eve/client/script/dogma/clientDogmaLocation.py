import dogmax
import sys
import weakref
import util
import string
import math
import uix
import log
import moniker
import blue
import uiutil
import uiconst
import uthread
import itertools
from collections import defaultdict
GROUPALL_THROTTLE_TIMER = 2 * const.SEC

class DogmaLocation(dogmax.BaseDogmaLocation):
    __guid__ = 'dogmax.DogmaLocation'
    __notifyevents__ = ['OnModuleAttributeChanges', 'OnWeaponBanksChanged', 'OnWeaponGroupDestroyed']

    def __init__(self, broker):
        dogmax.BaseDogmaLocation.__init__(self, broker)
        self.instanceCache = {}
        self.scatterAttributeChanges = True
        self.dogmaStaticMgr = sm.GetService('baseDogmaStaticSvc')
        self.remoteDogmaLM = None
        self.godma = sm.GetService('godma')
        self.stateMgr = self.godma.GetStateManager()
        self.fakeInstanceRow = None
        self.items = {}
        self.nextItemID = 0
        self.effectCompiler = sm.GetService('clientEffectCompiler')
        self.shipID = None
        self.LoadItem(session.charid)
        self.lastGroupAllRequest = None
        self.lastUngroupAllRequest = None
        sm.RegisterNotify(self)



    def MakeShipActive(self, shipID):
        uthread.pool('MakeShipActive', self._MakeShipActive, shipID)



    def _MakeShipActive(self, shipID):
        uthread.Lock(self, 'makeShipActive')
        try:
            if self.shipID == shipID:
                return 
            while not session.IsItSafe():
                self.LogInfo('MakeShipActive - session is mutating. Sleeping for 250ms')
                blue.pyos.synchro.Sleep(250)

            if shipID is None:
                log.LogTraceback('Unexpectedly got shipID = None')
                return 
            charItem = self.dogmaItems[session.charid]
            oldShipID = charItem.locationID
            if oldShipID == shipID:
                return 
            self.UpdateRemoteDogmaLocation()
            oldShipID = self.shipID
            self.shipID = shipID
            try:
                (self.instanceCache, self.instanceFlagQuantityCache, self.wbData,) = self.remoteShipMgr.ActivateShip(shipID, oldShipID)
            except Exception:
                self.shipID = oldShipID
                raise 
            charItems = charItem.GetFittedItems()
            self.scatterAttributeChanges = False
            try:
                self.LoadItem(self.shipID)
                if oldShipID is not None:
                    self.UnfitItemFromLocation(oldShipID, session.charid)
                for skill in charItems.itervalues():
                    for effectID in skill.activeEffects.keys():
                        self.StopEffect(effectID, skill.itemID)


                if shipID is not None:
                    self.FitItemToLocation(shipID, session.charid, const.flagPilot)
                    for skill in charItems.itervalues():
                        self.StartPassiveEffects(skill.itemID, skill.typeID)

                    shipInv = self.broker.invCache.GetInventoryFromId(shipID, locationID=session.stationid2)
                    self.LoadShipFromInventory(shipID, shipInv)
                    self.SetWeaponBanks(self.shipID, self.wbData)
                    sm.ChainEvent('ProcessActiveShipChanged', shipID, oldShipID)
                    self.UnloadItem(oldShipID)
                    if oldShipID:
                        sm.ScatterEvent('OnCapacityChange', oldShipID)

            finally:
                self.scatterAttributeChanges = True

            self.ClearInstanceCache()

        finally:
            uthread.UnLock(self, 'makeShipActive')




    def ClearInstanceCache(self):
        self.instanceCache = {}
        self.instanceFlagQuantityCache = {}
        self.wbData = None



    def UpdateRemoteDogmaLocation(self):
        if session.stationid2 is not None:
            self.remoteDogmaLM = moniker.GetStationDogmaLocation()
            self.remoteShipMgr = moniker.GetStationShipAccess()
        else:
            self.remoteDogmaLM = moniker.CharGetDogmaLocation()
            self.remoteShipMgr = moniker.GetShipAccess()



    def OnModuleAttributeChanges(self, changes):
        changes.sort(key=lambda change: change[4])
        for change in changes:
            try:
                (eventName, ownerID, itemID, attributeID, time, newValue, oldValue,) = change
                if attributeID == const.attributeQuantity:
                    if isinstance(itemID, tuple) and not self.IsItemLoaded(itemID[0]):
                        self.LogError("got an module attribute change and the item wasn't loaded", itemID)
                        continue
                    if newValue == 0:
                        self.SetAttributeValue(itemID, const.attributeQuantity, newValue)
                        self.UnfitItemFromLocation(itemID[0], itemID)
                        self.UnloadItem(itemID)
                    elif itemID != self.GetSubLocation(itemID[0], itemID[1]):
                        self.FitItemToLocation(itemID[0], itemID, itemID[1])
                    self.dogmaItems[itemID].attributes[attributeID] = newValue
                    self.SetAttributeValue(itemID, const.attributeQuantity, newValue)
                elif attributeID == const.attributeIsOnline:
                    if not self.IsItemLoaded(itemID):
                        continue
                    if newValue == self.GetAttributeValue(itemID, const.attributeIsOnline):
                        return 
                    if newValue == 0:
                        self.StopEffect(const.effectOnline, itemID)
                    else:
                        self.Activate(itemID, const.effectOnline)
                elif attributeID == const.attributeSkillPoints:
                    if not self.IsItemLoaded(itemID):
                        continue
                    dogmaItem = self.dogmaItems[itemID]
                    dogmaItem.attributes[const.attributeSkillPoints] = newValue
                    self.SetAttributeValue(itemID, const.attributeSkillPoints, newValue)
            except Exception:
                log.LogException('OnModuleAttributeChanges::Unexpected exception')
                sys.exc_clear()




    def LoadShipFromInventory(self, shipID, shipInv):
        subSystems = {}
        rigs = {}
        modules = {}
        drones = {}
        for item in shipInv.List():
            if not (cfg.IsShipFittingFlag(item.flagID) or item.flagID == const.flagDroneBay):
                continue
            self.items[item.itemID] = item
            if item.categoryID == const.categorySubSystem:
                subSystems[item.itemID] = item
            elif const.flagRigSlot0 <= item.flagID <= const.flagRigSlot7:
                rigs[item.itemID] = item
            elif const.flagLoSlot0 <= item.flagID <= const.flagHiSlot7:
                modules[item.itemID] = item
            elif item.flagID == const.flagDroneBay:
                drones[item.itemID] = item

        for items in (subSystems, rigs, modules):
            for (itemID, item,) in items.iteritems():
                self.FitItemToLocation(shipID, itemID, item.flagID)


        for (flagID, dbrow,) in self.instanceFlagQuantityCache.get(shipID, {}).iteritems():
            subLocation = (dbrow[0], dbrow[1], dbrow[2])
            if not self.IsItemLoaded(subLocation):
                self.FitItemToLocation(shipID, subLocation, flagID)

        for droneID in drones:
            self.FitItemToLocation(shipID, droneID, const.flagDroneBay)




    def FitItemToLocation(self, locationID, itemID, flagID):
        if locationID not in (self.shipID, session.charid):
            return 
        dogmax.BaseDogmaLocation.FitItemToLocation(self, locationID, itemID, flagID)



    def UnfitItemFromLocation(self, locationID, itemID, flushEffects = False):
        dogmax.BaseDogmaLocation.UnfitItemFromLocation(self, locationID, itemID, flushEffects)
        if locationID not in self.checkShipOnlineModulesPending:
            self.checkShipOnlineModulesPending.add(locationID)
            uthread.pool('LocationManager::CheckShipOnlineModules', self.CheckShipOnlineModules, locationID)



    def GetChargeNonDB(self, shipID, flagID):
        for (itemID, fittedItem,) in self.dogmaItems[shipID].GetFittedItems().iteritems():
            if isinstance(itemID, tuple):
                continue
            if fittedItem.flagID != flagID:
                continue
            if fittedItem.categoryID == const.categoryCharge:
                return fittedItem




    def GetSubSystemInFlag(self, shipID, flagID):
        shipInv = self.broker.invCache.GetInventoryFromId(shipID, locationID=session.stationid2)
        items = shipInv.List(flagID)
        if len(items) == 0:
            return None
        else:
            return self.dogmaItems[items[0].itemID]



    def GetItem(self, itemID):
        if itemID == self.shipID:
            return self.broker.invCache.GetInventoryFromId(self.shipID, locationID=session.stationid2).GetItem()
        try:
            return self.items[itemID]
        except KeyError:
            sys.exc_clear()
        return self.godma.GetItem(itemID)



    def GetCharacter(self, itemID, flush):
        return self.GetItem(itemID)



    def Activate(self, itemID, effectID):
        dogmaItem = self.dogmaItems[itemID]
        envInfo = dogmaItem.GetEnvironmentInfo()
        env = dogmax.Environment(envInfo.itemID, envInfo.charID, envInfo.shipID, envInfo.targetID, envInfo.otherID, effectID, weakref.proxy(self), None)
        env.dogmaLM = self
        self.StartEffect(effectID, itemID, env)



    def PostStopEffectAction(self, effectID, dogmaItem, activationInfo, *args):
        dogmax.BaseDogmaLocation.PostStopEffectAction(self, effectID, dogmaItem, activationInfo, *args)
        if effectID == const.effectOnline:
            shipID = dogmaItem.locationID
            if shipID not in self.checkShipOnlineModulesPending:
                self.checkShipOnlineModulesPending.add(shipID)
                uthread.pool('LocationManager::CheckShipOnlineModules', self.CheckShipOnlineModules, shipID)



    def GetInstance(self, item):
        try:
            return self.instanceCache[item.itemID]
        except KeyError:
            sys.exc_clear()
        instanceRow = [item.itemID]
        godmaItem = self.broker.godma.GetItem(item.itemID)
        for attributeID in self.GetAttributesByIndex().itervalues():
            instanceRow.append(getattr(godmaItem, self.dogmaStaticMgr.attributes[attributeID].attributeName, 0))

        return instanceRow



    def GetAttributesByIndex(self):
        return const.dgmAttributesByIdx



    def CheckSkillRequirements(self, charID, skillID, errorMsgName):
        skillItem = self.dogmaItems[skillID]
        self.CheckSkillRequirementsForType(skillItem.typeID, errorMsgName)



    def CheckSkillRequirementsForType(self, typeID, errorMsgName):
        skillSvc = sm.GetService('skills')
        missingSkills = {}
        for (requiredSkillTypeID, requiredSkillLevel,) in self.dogmaStaticMgr.GetRequiredSkills(typeID).iteritems():
            requiredSkill = skillSvc.HasSkill(requiredSkillTypeID)
            if requiredSkill is None:
                missingSkills[requiredSkillTypeID] = requiredSkillLevel
            elif self.GetAttributeValue(requiredSkill.itemID, const.attributeSkillLevel) < requiredSkillLevel:
                missingSkills[requiredSkillTypeID] = requiredSkillLevel

        if len(missingSkills) > 0:
            skillNameList = []
            for (skillTypeID, skillLevel,) in missingSkills.iteritems():
                skillName = cfg.invtypes.Get(skillTypeID).name
                if skillLevel:
                    skillName += ' %s %d' % (mls.SKILL_LEVEL, skillLevel)
                skillNameList.append(skillName)

            raise UserError(errorMsgName, {'requiredSkills': string.join(skillNameList, ', '),
             'itemName': (TYPEID, typeID)})
        return missingSkills



    def BoardShip(self, shipID, charID):
        if charID not in self.dogmaItems:
            self.LoadItem(charID)
        char = self.dogmaItems[charID]
        oldShipID = char.locationID
        charItems = char.GetFittedItems()
        for skill in charItems.itervalues():
            for effectID in skill.activeEffects.keys():
                self.StopEffect(effectID, skill.itemID)


        self.FitItemToLocation(shipID, charID, const.flagPilot)
        for skill in charItems.itervalues():
            self.StartPassiveEffects(skill.itemID, skill.typeID)




    def LoadItemsInLocation(self, itemID):
        if itemID == session.charid:
            char = self.godma.GetItem(itemID)
            for item in itertools.chain(char.skills.itervalues(), char.implants, char.boosters):
                self.LoadItem(item.itemID)




    def GetSensorStrengthAttribute(self, shipID):
        maxAttributeID = None
        maxValue = None
        for attributeID in (const.attributeScanGravimetricStrength,
         const.attributeScanLadarStrength,
         const.attributeScanMagnetometricStrength,
         const.attributeScanRadarStrength):
            val = self.GetAttributeValue(shipID, attributeID)
            if val > maxValue:
                (maxValue, maxAttributeID,) = (val, attributeID)

        return (maxAttributeID, maxValue)



    def UnfitItem(self, itemID):
        if itemID == session.charid:
            self.UnboardShip(session.charid)
        else:
            locationID = self.dogmaItems[itemID].locationID
            self.UnfitItemFromLocation(locationID, itemID)
            self.UnloadItem(itemID)
        if itemID in self.items:
            del self.items[itemID]
        if itemID in self.instanceCache:
            del self.instanceCache[itemID]



    def UnboardShip(self, charID):
        char = self.dogmaItems[charID]
        charItems = char.GetFittedItems()
        for skill in charItems.itervalues():
            for effectID in skill.activeEffects.keys():
                self.StopEffect(effectID, skill.itemID)


        self.UnfitItemFromLocation(self.shipID, charID)
        oldShipID = self.shipID
        self.shipID = None
        sm.ChainEvent('ProcessActiveShipChanged', None, oldShipID)



    def FitItem(self, item):
        self.items[item.itemID] = item
        self.FitItemToLocation(item.locationID, item.itemID, item.flagID)
        if self.dogmaStaticMgr.TypeHasEffect(item.typeID, const.effectOnline):
            try:
                self.OnlineModule(item.itemID)
            except UserError as e:
                uthread.pool('FitItem::RaiseUserError', eve.Message, e.msg, e.args[1])
            except Exception:
                log.LogException('Raised during OnlineModule')



    def OnItemChange(self, item, change):
        wasFitted = item.itemID in self.dogmaItems
        isFitted = item.locationID in (self.shipID, session.charid) and (cfg.IsShipFittingFlag(item.flagID) and item[const.ixStackSize] > 0 or item.flagID in (const.flagDroneBay,
         const.flagSkill,
         const.flagSkillInTraining,
         const.flagImplant,
         const.flagBooster))
        if wasFitted and not isFitted:
            if item.categoryID == const.categoryDrone:
                self.UnloadItem(item.itemID)
            else:
                self.UnfitItem(item.itemID)
        if not wasFitted and isFitted:
            try:
                self.FitItem(item)
            except Exception:
                log.LogException('OnItemChange unexpectedly failed fitting item %s: (%s)' % (item.itemID, change))
                raise 
        if wasFitted and isFitted and const.ixFlag in change:
            self.dogmaItems[item.itemID].flagID = item.flagID
        if isFitted and const.ixStackSize in change:
            self.SetAttributeValue(item.itemID, const.attributeQuantity, item.stacksize)
        if self.scatterAttributeChanges:
            sm.ScatterEvent('OnDogmaItemChange', item, change)



    def OnAttributeChanged(self, attributeID, itemKey, value = None, oldValue = None):
        dogmax.BaseDogmaLocation.OnAttributeChanged(self, attributeID, itemKey, value=value, oldValue=oldValue)
        if self.scatterAttributeChanges:
            sm.ScatterEvent('OnDogmaAttributeChanged', self.shipID, itemKey, attributeID, value)



    def GetShip(self):
        return self.dogmaItems[self.shipID]



    def TryFit(self, item, flagID):
        shipID = util.GetActiveShip()
        shipInv = self.broker.invCache.GetInventoryFromId(shipID, locationID=session.stationid2)
        shipInv.Add(item.itemID, item.locationID, flag=flagID)



    def GetQuantity(self, itemID):
        if isinstance(itemID, tuple):
            return self.GetAttributeValue(itemID, const.attributeQuantity)
        return self.GetItem(itemID).stacksize



    def GetSublocations(self, shipID):
        ret = set()
        for subLocation in self.dogmaItems[shipID].subLocations.itervalues():
            ret.add(self.dogmaItems[subLocation])

        return ret



    def GetSlotOther(self, shipID, flagID):
        for item in self.dogmaItems[shipID].GetFittedItems().itervalues():
            if item.flagID == flagID and item.categoryID == const.categoryModule:
                return item.itemID




    def GetCapacity(self, shipID, attributeID, flagID):
        if const.flagLoSlot0 <= flagID <= const.flagHiSlot7:
            shipDogmaItem = self.dogmaItems[shipID]
            subLocation = shipDogmaItem.subLocations.get(flagID, None)
            if subLocation is None:
                used = 0
            else:
                used = self.GetAttributeValue(subLocation, const.attributeQuantity) * cfg.invtypes.Get(subLocation[2]).volume
            moduleID = self.GetSlotOther(shipID, flagID)
            if moduleID is None:
                capacity = 0
            else:
                capacity = self.GetAttributeValue(moduleID, const.attributeCapacity)
            return util.KeyVal(capacity=capacity, used=used)
        else:
            return self.broker.invCache.GetInventoryFromId(self.shipID, locationID=session.stationid2).GetCapacity(flagID)



    def CapacitorSimulator(self, shipID):
        dogmaItem = self.dogmaItems[shipID]
        capacitorCapacity = self.GetAttributeValue(shipID, const.attributeCapacitorCapacity)
        rechargeTime = self.GetAttributeValue(shipID, const.attributeRechargeRate)
        modules = []
        totalCapNeed = 0
        for (moduleID, module,) in dogmaItem.GetFittedItems().iteritems():
            if not module.IsOnline():
                continue
            try:
                defaultEffectID = self.dogmaStaticMgr.GetDefaultEffect(module.typeID)
            except KeyError:
                defaultEffectID = None
                sys.exc_clear()
            if defaultEffectID is None:
                continue
            defaultEffect = self.dogmaStaticMgr.effects[defaultEffectID]
            durationAttributeID = defaultEffect.durationAttributeID
            dischargeAttributeID = defaultEffect.dischargeAttributeID
            if durationAttributeID is None or dischargeAttributeID is None:
                continue
            duration = self.GetAttributeValue(moduleID, durationAttributeID)
            capNeed = self.GetAttributeValue(moduleID, dischargeAttributeID)
            modules.append([capNeed, long(duration * const.dgmTauConstant), 0])
            totalCapNeed += capNeed / duration

        rechargeRateAverage = capacitorCapacity / rechargeTime
        peakRechargeRate = 2.5 * rechargeRateAverage
        tau = rechargeTime / 5
        TTL = None
        if totalCapNeed > peakRechargeRate:
            TTL = self.RunSimulation(capacitorCapacity, rechargeTime, modules)
            loadBalance = 0
        else:
            c = 2 * capacitorCapacity / tau
            k = totalCapNeed / c
            exponent = (1 - math.sqrt(1 - 4 * k)) / 2
            if exponent == 0:
                loadBalance = 1
            else:
                t = -math.log(exponent) * tau
                loadBalance = (1 - math.exp(-t / tau)) ** 2
        return (peakRechargeRate,
         totalCapNeed,
         loadBalance,
         TTL)



    def RunSimulation(self, capacitorCapacity, rechargeRate, modules):
        capacitor = capacitorCapacity
        tauThingy = float(const.dgmTauConstant) * (rechargeRate / 5.0)
        currentTime = nextTime = 0L
        while capacitor > 0.0 and nextTime < DAY:
            capacitor = (1.0 + (math.sqrt(capacitor / capacitorCapacity) - 1.0) * math.exp((currentTime - nextTime) / tauThingy)) ** 2 * capacitorCapacity
            currentTime = nextTime
            nextTime = DAY
            for data in modules:
                if data[2] == currentTime:
                    data[2] += data[1]
                    capacitor -= data[0]
                nextTime = min(nextTime, data[2])


        if capacitor > 0.0:
            return DAY
        return currentTime



    def OnlineModule(self, moduleID):
        self.Activate(moduleID, const.effectOnline)
        dogmaItem = self.dogmaItems[moduleID]
        try:
            self.remoteDogmaLM.SetModuleOnline(dogmaItem.locationID, moduleID)
        except UserError as e:
            if e.msg != 'EffectAlreadyActive2':
                raise 
        except Exception:
            self.StopEffect(const.effectOnline, moduleID)
            raise 



    def OfflineModule(self, moduleID):
        dogmaItem = self.dogmaItems[moduleID]
        self.StopEffect(const.effectOnline, moduleID)
        try:
            self.remoteDogmaLM.TakeModuleOffline(dogmaItem.locationID, moduleID)
        except Exception:
            self.Activate(moduleID, const.effectOnline)
            raise 



    def GetDragData(self, itemID):
        if itemID in self.items:
            return [uix.GetItemData(self.items[itemID], 'icons')]
        dogmaItem = self.dogmaItems[itemID]
        data = uiutil.Bunch()
        data.__guid__ = 'listentry.InvItem'
        data.item = util.KeyVal(itemID=dogmaItem.itemID, typeID=dogmaItem.typeID, groupID=dogmaItem.groupID, categoryID=dogmaItem.categoryID, flagID=dogmaItem.flagID, ownerID=dogmaItem.ownerID, locationID=dogmaItem.locationID, stacksize=self.GetAttributeValue(itemID, const.attributeQuantity))
        data.rec = data.item
        data.itemID = itemID
        data.viewMode = 'icons'
        return [data]



    def GetDisplayAttributes(self, itemID, attributes):
        ret = {}
        dogmaItem = self.dogmaItems[itemID]
        for attributeID in itertools.chain(dogmaItem.attributeCache, dogmaItem.attributes):
            if attributeID == const.attributeVolume:
                continue
            ret[attributeID] = self.GetAttributeValue(itemID, attributeID)

        return ret



    def LinkWeapons(self, shipID, toID, fromID, merge = True):
        toItem = self.dogmaItems[toID]
        fromItem = self.dogmaItems[fromID]
        if toItem.typeID != fromItem.typeID:
            self.LogInfo('LinkWeapons::Modules not of same type', toItem, fromItem)
            return 
        if toItem.groupID not in const.dgmGroupableGroupIDs:
            self.LogInfo('group not groupable', toItem, fromItem)
            return 
        if shipID is None or shipID != fromItem.locationID:
            log.LogTraceback('LinkWeapons::Modules not located in the same place')
        masterID = self.GetMasterModuleID(shipID, toID)
        if not masterID:
            masterID = toID
        slaveID = self.IsInWeaponBank(shipID, fromID)
        if slaveID:
            if merge:
                info = self.remoteDogmaLM.MergeModuleGroups(shipID, masterID, slaveID)
            else:
                info = self.remoteDogmaLM.PeelAndLink(shipID, masterID, slaveID)
        else:
            info = self.remoteDogmaLM.LinkWeapons(shipID, masterID, fromID)
        self.OnWeaponBanksChanged(shipID, info)



    def UngroupModule(self, shipID, moduleID):
        slaveID = self.remoteDogmaLM.UnlinkModule(shipID, moduleID)
        self.slaveModulesByMasterModule[shipID][moduleID].remove(slaveID)
        if not self.slaveModulesByMasterModule[shipID][moduleID]:
            del self.slaveModulesByMasterModule[shipID][moduleID]
        self.SetGroupNumbers(shipID)
        sm.ScatterEvent('OnRefreshModuleBanks')
        return slaveID



    def UnlinkAllWeapons(self, shipID):
        info = self.remoteDogmaLM.UnlinkAllModules(shipID)
        self.OnWeaponBanksChanged(shipID, info)
        self.lastUngroupAllRequest = blue.os.GetTime()



    def LinkAllWeapons(self, shipID):
        info = self.remoteDogmaLM.LinkAllWeapons(shipID)
        self.OnWeaponBanksChanged(shipID, info)
        self.lastGroupAllRequest = blue.os.GetTime()



    def GetGroupAllOpacity(self, attributeName):
        lastRequest = getattr(self, attributeName)
        if lastRequest is None:
            return 1.0
        timeDiff = blue.os.GetTime() - lastRequest
        waitTime = min(GROUPALL_THROTTLE_TIMER, GROUPALL_THROTTLE_TIMER - timeDiff)
        opacity = max(0, 1 - float(waitTime) / GROUPALL_THROTTLE_TIMER)
        return opacity



    def IsInWeaponBank(self, shipID, itemID):
        slaveModulesByMasterModule = self.slaveModulesByMasterModule.get(shipID, {})
        if itemID in slaveModulesByMasterModule:
            return itemID
        masterID = self.GetMasterModuleID(shipID, itemID)
        if masterID is not None:
            return masterID
        return False



    def GetGroupableTypes(self, shipID):
        groupableTypes = defaultdict(lambda : 0)
        self.LoadItem(shipID)
        dogmaItem = self.dogmaItems[shipID]
        for fittedItem in dogmaItem.GetFittedItems().itervalues():
            if not const.flagHiSlot0 <= fittedItem.flagID <= const.flagHiSlot7:
                continue
            if fittedItem.groupID not in const.dgmGroupableGroupIDs:
                continue
            if not fittedItem.IsOnline():
                continue
            groupableTypes[fittedItem.typeID] += 1

        return groupableTypes



    def CanGroupAll(self, shipID):
        groupableTypes = self.GetGroupableTypes(shipID)
        groups = {}
        dogmaItem = self.dogmaItems[shipID]
        for fittedItem in dogmaItem.GetFittedItems().itervalues():
            if fittedItem.groupID not in const.dgmGroupableGroupIDs:
                continue
            if not fittedItem.IsOnline():
                continue
            if not self.IsInWeaponBank(shipID, fittedItem.itemID) and groupableTypes[fittedItem.typeID] > 1:
                return True
            masterID = self.GetMasterModuleID(shipID, fittedItem.itemID)
            if masterID is None:
                masterID = fittedItem.itemID
            if fittedItem.typeID not in groups:
                groups[fittedItem.typeID] = masterID
            else:
                if groups[fittedItem.typeID] != masterID:
                    return True

        return False



    def DestroyWeaponBank(self, shipID, itemID):
        self.remoteDogmaLM.DestroyWeaponBank(shipID, itemID)
        self.OnWeaponGroupDestroyed(shipID, itemID)



    def SetWeaponBanks(self, shipID, data):
        dogmax.BaseDogmaLocation.SetWeaponBanks(self, shipID, data)
        self.SetGroupNumbers(shipID)



    def OnWeaponBanksChanged(self, shipID, info):
        self.SetWeaponBanks(shipID, info)
        sm.ScatterEvent('OnRefreshModuleBanks')



    def OnWeaponGroupDestroyed(self, shipID, itemID):
        del self.slaveModulesByMasterModule[shipID][itemID]
        self.SetGroupNumbers(shipID)
        sm.ScatterEvent('OnRefreshModuleBanks')



    def SetGroupNumbers(self, shipID):
        allGroupsDict = settings.user.ui.Get('linkedWeapons_groupsDict', {})
        groupsDict = allGroupsDict.get(shipID, {})
        for masterID in groupsDict.keys():
            if masterID not in self.slaveModulesByMasterModule[shipID]:
                del groupsDict[masterID]

        for masterID in self.slaveModulesByMasterModule[shipID]:
            if masterID in groupsDict:
                continue
            for i in xrange(1, 9):
                if i not in groupsDict.values():
                    groupsDict[masterID] = i
                    break


        settings.user.ui.Set('linkedWeapons_groupsDict', allGroupsDict)



    def GetModulesInBank(self, shipID, itemID):
        slaveModulesByMasterModule = self.slaveModulesByMasterModule.get(shipID, {})
        masterID = self.GetMasterModuleID(shipID, itemID)
        if masterID is None and itemID in slaveModulesByMasterModule:
            masterID = itemID
        elif masterID is None:
            return 
        moduleIDs = self.GetSlaveModules(masterID, shipID)
        moduleIDs.add(masterID)
        return list(moduleIDs)



    def GetAllSlaveModulesByMasterModule(self, shipID):
        slaveModulesByMasterModule = self.slaveModulesByMasterModule.get(shipID, {})
        return slaveModulesByMasterModule



    def GetMasterModuleForFlag(self, shipID, flagID):
        moduleID = self.GetSlotOther(shipID, flagID)
        if moduleID is None:
            raise RuntimeError('GetMasterModuleForFlag, no module in the flag')
        masterID = self.GetMasterModuleID(shipID, moduleID)
        if masterID is not None:
            return masterID
        return moduleID



    def UnloadChargeToContainer(self, shipID, itemID, containerArgs, flag, quantity = None):
        itemIDs = []
        if isinstance(itemID, tuple):
            itemIDs = self.GetSubLocationsInBank(shipID, itemID)
        else:
            itemIDs = self.GetCrystalsInBank(shipID, itemID)
        if len(itemIDs) == 0:
            itemIDs = [itemID]
        inv = self.broker.invCache.GetInventoryFromId(locationID=session.stationid2, *containerArgs)
        if getattr(inv, 'typeID', None) is not None and cfg.invtypes.Get(inv.typeID).groupID == const.groupAuditLogSecureContainer:
            flag = settings.user.ui.Get('defaultContainerLock_%s' % inv.itemID, None)
        try:
            inv.MultiAdd(itemIDs, shipID, flag=flag, fromManyFlags=True, qty=quantity)
        except UserError as e:
            if e.msg == 'NotEnoughCargoSpace' and len(itemIDs) > 1:
                eve.Message('NotEnoughCargoSpaceToUnloadBank')
                return 
            raise 



    def GetSubLocationsInBank(self, shipID, itemID):
        ret = []
        try:
            flagID = self.dogmaItems[itemID].flagID
        except KeyError:
            return []
        moduleID = self.GetSlotOther(shipID, flagID)
        if moduleID is None:
            return []
        moduleIDs = self.GetModulesInBank(shipID, moduleID)
        if not moduleIDs:
            return []
        shipDogmaItem = self.dogmaItems[shipID]
        for moduleID in moduleIDs:
            moduleDogmaItem = self.dogmaItems[moduleID]
            chargeID = shipDogmaItem.subLocations.get(moduleDogmaItem.flagID, None)
            if chargeID is not None:
                ret.append(chargeID)

        return ret



    def GetCrystalsInBank(self, shipID, itemID):
        flagID = self.dogmaItems[itemID].flagID
        moduleID = self.GetSlotOther(shipID, flagID)
        if moduleID is None:
            return []
        moduleIDs = self.GetModulesInBank(shipID, moduleID)
        if not moduleIDs:
            return []
        crystals = []
        for moduleID in moduleIDs:
            moduleDogmaItem = self.dogmaItems[moduleID]
            crystal = self.GetChargeNonDB(shipID, moduleDogmaItem.flagID)
            if crystal is not None:
                crystals.append(crystal.itemID)

        return crystals



    def LoadChargeToModule(self, itemID, chargeTypeID, chargeItems = None, qty = None, preferSingletons = False):
        shipID = self.dogmaItems[itemID].locationID
        masterID = self.GetMasterModuleID(shipID, itemID)
        if masterID is None:
            masterID = itemID
        if chargeItems is None:
            shipInv = self.broker.invCache.GetInventoryFromId(shipID, locationID=session.stationid2)
            chargeItems = []
            for item in shipInv.List(const.flagCargo):
                if item.typeID == chargeTypeID:
                    chargeItems.append(item)

        if not chargeItems:
            raise UserError('CannotLoadNotEnoughCharges')
        chargeLocationID = chargeItems[0].locationID
        for item in chargeItems:
            if cfg.IsShipFittingFlag(item.flagID):
                raise UserError('CantMoveChargesBetweenModules')

        if preferSingletons:
            for item in chargeItems[:]:
                if not item.singleton:
                    chargeItems.remove(item)

        if qty is not None:
            totalQty = 0
            i = 0
            for item in chargeItems:
                if totalQty >= qty:
                    break
                i += 1
                totalQty += item.stacksize

            chargeItems = chargeItems[:i]
        itemIDs = []
        for item in chargeItems:
            itemIDs.append(item.itemID)

        self.remoteDogmaLM.LoadAmmoToBank(shipID, masterID, chargeTypeID, itemIDs, chargeLocationID, qty)



    def LoadAmmoToModules(self, shipID, moduleIDs, chargeTypeID, itemID, ammoLocationID, qty = None):
        self.remoteDogmaLM.LoadAmmoToModules(shipID, moduleIDs, chargeTypeID, itemID, ammoLocationID, qty=qty)



    def DropLoadChargeToModule(self, itemID, chargeTypeID, chargeItems, qty = None, preferSingletons = False):
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            maxQty = 0
            for item in chargeItems:
                if item.typeID != chargeTypeID:
                    continue
                maxQty += item.stacksize

            if maxQty == 0:
                errmsg = mls.UI_INFLIGHT_NOMOREUNITS
            else:
                errmsg = mls.UI_INFLIGHT_NOROOMFORMORE
            qty = None
            ret = uix.QtyPopup(int(maxQty), 0, int(maxQty), errmsg)
            if ret is not None:
                qty = ret['qty']
                if qty <= 0:
                    return 
        self.LoadChargeToModule(itemID, chargeTypeID, chargeItems=chargeItems, qty=qty, preferSingletons=preferSingletons)



    def UnloadModuleToContainer(self, shipID, itemID, containerArgs, flag = None):
        if self.IsInWeaponBank(shipID, itemID):
            ret = eve.Message('CustomQuestion', {'header': mls.UI_GENERIC_CONFIRM,
             'question': mls.UI_SHARED_WEAPONLINK_UNFIT}, uiconst.YESNO)
            if ret != uiconst.ID_YES:
                return 
        item = self.GetItem(itemID)
        containerInv = eve.GetInventoryFromId(*containerArgs)
        if item is not None:
            subLocation = self.GetSubLocation(item.locationID, item.flagID)
            if subLocation is not None:
                containerInv.Add(subLocation, subLocation[0], qty=None, flag=flag)
            crystal = self.GetChargeNonDB(shipID, item.flagID)
            if crystal is not None:
                containerInv.Add(crystal.itemID, item.locationID, qty=None, flag=flag)
        if getattr(containerInv, 'typeID', None) is not None and cfg.invtypes.Get(containerInv.typeID).groupID == const.groupAuditLogSecureContainer:
            flag = settings.user.ui.Get('defaultContainerLock_%s' % containerInv.itemID, None)
        if containerArgs[0] == shipID:
            containerInv.Add(itemID, item.locationID, qty=None, flag=flag)
        elif flag is not None:
            containerInv.Add(itemID, item.locationID, qty=None, flag=flag)
        else:
            containerInv.Add(itemID, item.locationID)



    def CheckCanFit(self, locationID, itemID, flagID, fromLocationID):
        item = self.broker.invCache.FetchItem(itemID, fromLocationID)
        if item is None:
            self.LogInfo('ClientDogmaLocation::CheckCanFit - unable to fetch item', locationID, itemID, flagID, fromLocationID)
            return 
        self.CheckSkillRequirementsForType(item.typeID, 'FittingHasSkillPrerequisites')
        maxGroupFitted = self.dogmaStaticMgr.GetTypeAttribute(item.typeID, const.attributeMaxGroupFitted)
        if maxGroupFitted is not None:
            modulesByGroup = self.GetModuleListByShipGroup(locationID, item.groupID)
            if len(modulesByGroup) >= maxGroupFitted:
                shipItem = self.dogmaItems[locationID]
                raise UserError('CantFitTooManyByGroup', {'shipName': (TYPEID, shipItem.typeID),
                 'moduleName': (TYPEID, item.typeID),
                 'groupName': (GROUPID, item.groupID),
                 'noOfModules': int(maxGroupFitted),
                 'noOfModulesFitted': len(modulesByGroup)})



    def GetOnlineModules(self, shipID):
        return {module.flagID:moduleID for (moduleID, module,) in self.dogmaItems[shipID].GetFittedItems().iteritems() if module.IsOnline()}



    def ShouldStartChanceBasedEffect(self, effectID, itemID, chanceAttributeID):
        dogmaItem = self.dogmaItems[itemID]
        if dogmaItem.groupID == const.groupBooster:
            godmaItem = self.godma.GetItem(itemID)
            if godmaItem is None:
                return False
            effectName = cfg.dgmeffects.Get(effectID).effectName
            godmaEffect = godmaItem.effects.get(effectName, None)
            if godmaEffect is None:
                return False
            if godmaEffect.isActive:
                return True
        return False




