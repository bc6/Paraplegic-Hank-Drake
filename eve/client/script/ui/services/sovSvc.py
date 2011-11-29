import blue
import service
import form
import util
import moniker
import localization
from sovereignty import SovereigntyTab
STAT_ID_KILLS = 3
CLAIM_DAYS_TO_SECONDS = 86400

class SovService(service.Service):
    __guid__ = 'svc.sov'
    __dependencies__ = ['audio']
    __exportedcalls__ = {'GetSovOverview': [service.ROLE_IGB]}
    __notifyevents__ = ['ProcessSovStatusChanged', 'OnSessionChanged', 'OnSovereigntyAudioEvent']

    def __init__(self):
        service.Service.__init__(self)
        self.sovInfoBySystemID = {}
        self.devIndexMgr = None
        self.outpostData = None



    def Run(self, *args):
        service.Service.Run(self, *args)
        self.indexLevels = []
        for level in util.GetDevIndexLevels()[const.attributeDevIndexMilitary].itervalues():
            self.indexLevels.append(level.maxLevel)

        self.indexLevels.sort()
        self.holdTimeLevels = util.GetTimeIndexLevels()



    def GetInfrastructureHubWnd(self, hubID = None):
        form.InfrastructureHubWnd.CloseIfOpen()
        wnd = form.InfrastructureHubWnd.Open(hubID=hubID)
        return wnd



    def GetTimeIndexValuesInDays(self):
        return [ t / CLAIM_DAYS_TO_SECONDS for t in self.holdTimeLevels ]



    def ProcessSovStatusChanged(self, *args):
        (solarSystemID, newStatus,) = args
        if newStatus is None and solarSystemID in self.sovInfoBySystemID:
            del self.sovInfoBySystemID[solarSystemID]
        else:
            self.sovInfoBySystemID[solarSystemID] = newStatus
        if solarSystemID == session.solarsystemid2:
            sm.ScatterEvent('OnSystemStatusChanged')



    def GetSystemSovereigntyInfo(self, solarSystemID, forceUpdate = False):
        if not forceUpdate and solarSystemID in self.sovInfoBySystemID:
            self.LogInfo('GetSystemSovereigntyInfo: Returning cached sov info', self.sovInfoBySystemID[solarSystemID])
            return self.sovInfoBySystemID[solarSystemID]
        status = sm.RemoteSvc('sovMgr').GetSystemSovereigntyInfo(solarSystemID)
        self.sovInfoBySystemID[solarSystemID] = status
        self.LogInfo('GetSystemSovereigntyInfo: Returning sov status from server:', status)
        return status



    def GetContestedState(self, solarSystemID):
        sovInfo = self.GetSystemSovereigntyInfo(solarSystemID)
        text = ''
        if sovInfo is not None and sovInfo.contested > 0:
            numGates = sm.GetService('map').GetNumberOfStargates(solarSystemID)
            if sovInfo.contested * 2 > numGates:
                text = localization.GetByLabel('UI/Inflight/Brackets/SystemVulnerable')
            else:
                text = localization.GetByLabel('UI/Inflight/Brackets/SystemContested')
        return text



    def AddUppgrades(self, hubID, itemlist, sourceLocationID):
        inv = sm.GetService('invCache').GetInventoryFromId(hubID)
        inv.MultiAdd(itemlist, sourceLocationID)



    def CalculateUpgradeCost(self, solarsystemID, typeIDs):
        claimTime = self.GetSystemSovereigntyInfo(solarsystemID, forceUpdate=True).claimTime
        daysHeld = (blue.os.GetWallclockTimeNow() - claimTime) / const.DAY
        daysLeft = const.sovereignityBillingPeriod - daysHeld % const.sovereignityBillingPeriod
        self.LogInfo('claimTime is', claimTime, util.FmtDate(claimTime), 'which amounts to ', daysHeld, 'days. days left for this billing cycle are', daysLeft)
        total = 0
        omygodma = sm.StartService('godma')
        for tID in typeIDs:
            total = omygodma.GetTypeAttribute(tID, const.attributeSovBillSystemCost, 0)

        return (daysLeft, total)



    def GetSovOverview(self, location = None):
        wnd = form.SovereigntyOverviewWnd.Open()
        if wnd is not None and not wnd.destroyed:
            if location is not None:
                wnd.SetLocation(*location)
        return wnd



    def GetKillLast24H(self, itemID):
        historyDB = sm.RemoteSvc('map').GetHistory(STAT_ID_KILLS, 24)
        systems = set(sm.GetService('map').IterateSolarSystemIDs(itemID))
        totalKills = 0
        totalPods = 0
        for stats in historyDB:
            if stats.solarSystemID in systems:
                kills = stats.value1 - stats.value2
                totalKills += kills
                totalPods += stats.value3

        return (totalKills, totalPods)



    def GetSovOwnerID(self):
        systemItem = sm.GetService('map').GetItem(session.solarsystemid2)
        solSovOwner = None
        if systemItem:
            solSovOwner = systemItem.factionID
            if solSovOwner is None:
                sovInfo = self.GetSystemSovereigntyInfo(session.solarsystemid2)
                if sovInfo is not None:
                    solSovOwner = sovInfo.allianceID
        return solSovOwner



    def AddToBucket(self, buckets, systemOwners, systemID):
        self.counter += 1
        sovID = systemOwners.get(systemID, None)
        if sovID is None:
            sovID = sm.GetService('map').GetItem(systemID).factionID
        if sovID is not None:
            count = buckets.get(sovID, 0)
            buckets[sovID] = count + 1



    def GetDominantAllianceID(self, scope, reqRegionID, reqConstellationID, reqSolarSystemID):
        self.counter = 0
        buckets = {}
        systemOwners = {}
        data = sm.RemoteSvc('stationSvc').GetAllianceSystems()
        for info in data:
            systemOwners[info.solarSystemID] = info.allianceID

        if scope in (SovereigntyTab.World, SovereigntyTab.Changes):
            itemID = None
        elif scope == SovereigntyTab.Region:
            itemID = reqRegionID
        elif scope == SovereigntyTab.Constellation:
            itemID = reqConstellationID
        else:
            itemID = reqSolarSystemID
        for systemID in sm.GetService('map').IterateSolarSystemIDs(itemID):
            self.AddToBucket(buckets, systemOwners, systemID)

        counters = [ (count, sovID) for (sovID, count,) in buckets.iteritems() ]
        counters.sort()
        dominantID = None
        if len(counters) == 1:
            dominantID = counters[0][1]
        elif len(counters) == 0:
            dominantID = 'none'
        elif counters[-1][0] == counters[-2][0]:
            dominantID = 'contested'
        else:
            dominantID = counters[-1][1]
        return dominantID



    def GetIdFromScope(self, scope):
        if scope == 'world':
            itemID = None
        elif scope == 'region':
            itemID = session.regionid
        elif scope == 'constellation':
            itemID = session.constellationid
        else:
            itemID = session.solarsystemid2
        return itemID



    def GetActiveCynos(self, itemID):
        data = sm.RemoteSvc('map').GetBeaconCount()
        systems = set(sm.GetService('map').IterateSolarSystemIDs(itemID))
        totalModules = 0
        totalStructures = 0
        for (solarSystemID, counts,) in data.iteritems():
            if solarSystemID in systems:
                (moduleCount, structureCount,) = counts
                totalModules += moduleCount
                totalStructures += structureCount

        return util.KeyVal(cynoModules=totalModules, cynoStructures=totalStructures)



    def GetPrerequisite(self, typeID):
        reqTypeID = sm.GetService('godma').GetTypeAttribute(typeID, const.attributeSovUpgradeRequiredUpgradeID)
        reqTypeName = None
        if reqTypeID != 0 and reqTypeID is not None:
            reqTypeName = cfg.invtypes.Get(reqTypeID).typeName
        return reqTypeName



    def CanInstallUpgrade(self, typeID, hubID, devIndices = None):
        if devIndices is None:
            devIndices = self.GetDevIndexMgr().GetDevelopmentIndicesForSystem(session.solarsystemid2)
        godma = sm.GetService('godma')
        for (attributeID, data,) in devIndices.iteritems():
            value = godma.GetTypeAttribute(typeID, attributeID)
            level = self.GetDevIndexLevel(data.points)
            if value > 0 and value > level:
                return False

        sovInfo = self.GetSystemSovereigntyInfo(session.solarsystemid)
        sovereigntyLevel = int(godma.GetTypeAttribute(typeID, const.attributeDevIndexSovereignty, 0))
        sovHeldFor = (blue.os.GetWallclockTime() - sovInfo.claimTime) / const.DAY
        if util.GetTimeIndexLevelForDays(sovHeldFor) < sovereigntyLevel:
            return False
        requiredUpgradeID = int(godma.GetTypeAttribute(typeID, const.attributeSovUpgradeRequiredUpgradeID, 0))
        blockingUpgradeID = int(godma.GetTypeAttribute(typeID, const.attributeSovUpgradeBlockingUpgradeID, 0))
        if requiredUpgradeID > 0 or blockingUpgradeID > 0:
            inv = sm.GetService('invCache').GetInventoryFromId(hubID)
            found = False
            requiredUpgradeID == 0
            for upgrade in inv.List():
                if requiredUpgradeID > 0 and upgrade.typeID == requiredUpgradeID and upgrade.flagID == const.flagStructureActive:
                    found = True
                if blockingUpgradeID > 0 and upgrade.typeID == blockingUpgradeID:
                    return False

            if not found:
                return False
        outpostUpgradeLevel = int(godma.GetTypeAttribute(typeID, const.attributeSovUpgradeRequiredOutpostUpgradeLevel, 0))
        if outpostUpgradeLevel > 0:
            outpostID = None
            park = sm.GetService('michelle').GetBallpark()
            for ballID in park.globals:
                if ballID < 0:
                    continue
                slimitem = park.GetInvItem(ballID)
                if util.IsOutpost(ballID) and slimitem is not None:
                    ownerID = slimitem.ownerID
                    if ownerID in self.GetOutpostData(ballID).allianceCorpList:
                        outpostID = ballID
                    break

            if outpostID is None:
                return False
            if self.GetOutpostData(outpostID).upgradeLevel < outpostUpgradeLevel:
                return False
        return True



    def GetDevIndexMgr(self):
        if self.devIndexMgr is None:
            self.devIndexMgr = sm.RemoteSvc('devIndexManager')
        return self.devIndexMgr



    def GetOutpostData(self, outpostID):
        if self.outpostData is not None and blue.os.TimeDiffInMs(self.outpostData.updateTime, blue.os.GetWallclockTime()) > 3600000:
            return self.outpostData
        else:
            allianceSvc = sm.GetService('alliance')
            corpMgr = moniker.GetCorpStationManagerEx(outpostID)
            self.outpostData = util.KeyVal(allianceCorpList=set([ corporationID for corporationID in allianceSvc.GetMembers() ]), updateTime=blue.os.GetWallclockTime(), upgradeLevel=corpMgr.GetStationDetails(outpostID).upgradeLevel)
            return self.outpostData



    def GetUpgradeLevel(self, typeID):
        for indexID in const.developmentIndices:
            value = int(sm.GetService('godma').GetTypeAttribute(typeID, indexID, -1))
            if value >= 0:
                levelInfo = self.GetIndexLevel(value, typeID, True)
                levelInfo.indexID = indexID
                return levelInfo




    def GetInfrastructureHubItemData(self, hubID):
        inv = sm.GetService('invCache').GetInventoryFromId(hubID)
        itemData = {}
        for item in inv.List():
            itemData[item.typeID] = util.KeyVal(itemID=item.itemID, typeID=item.typeID, groupID=item.groupID, online=item.flagID == const.flagStructureActive)

        return itemData



    def GetIndexLevel(self, value, indexID, isUpgrade = False):
        if indexID == const.attributeDevIndexSovereignty:
            indexLevels = self.holdTimeLevels
        else:
            indexLevels = self.indexLevels
        if value >= indexLevels[-1]:
            return util.KeyVal(level=5, remainder=0.0)
        for (level, maxValue,) in enumerate(indexLevels):
            if value < maxValue:
                if level == 0:
                    minValue = 0.0
                else:
                    minValue = float(indexLevels[(level - 1)])
                if value < 0:
                    remainder = 0
                remainder = value - minValue
                remainder = remainder / (maxValue - minValue)
                if isUpgrade:
                    level = value
                return util.KeyVal(level=level, remainder=remainder)




    def GetLevelForIndex(self, indexID, devIndex = None):
        if indexID == const.attributeDevIndexSovereignty:
            sovInfo = self.GetSystemSovereigntyInfo(session.solarsystemid2)
            currentTime = blue.os.GetWallclockTime()
            timeDiff = currentTime - sovInfo.claimTime
            value = (currentTime - sovInfo.claimTime) / const.SEC
            increasing = True
        elif devIndex is None:
            devIndex = self.GetDevIndexMgr().GetDevelopmentIndicesForSystem(session.solarsystemid2).get(indexID, None)
        if devIndex is None:
            self.LogError('The index', indexID, 'does not exist')
            value = 0
            increasing = True
        else:
            increasing = devIndex.increasing
            value = devIndex.points
        ret = self.GetIndexLevel(value, indexID)
        ret.increasing = increasing
        return ret



    def GetAllDevelopmentIndicesMapped(self):
        systemToIndexMap = {}
        for indexInfo in sm.RemoteSvc('devIndexManager').GetAllDevelopmentIndices():
            systemToIndexMap[indexInfo.solarSystemID] = {const.attributeDevIndexMilitary: indexInfo.militaryPoints,
             const.attributeDevIndexIndustrial: indexInfo.industrialPoints,
             const.attributeDevIndexSovereignty: indexInfo.claimedFor * CLAIM_DAYS_TO_SECONDS}

        return systemToIndexMap



    def OnSessionChanged(self, isRemote, sess, change):
        if 'solarsystemid2' in change:
            self.devIndexMgr = None
            self.outpostData = None



    def GetCurrentData(self, locationID):
        if util.IsSolarSystem(locationID) and not util.IsWormholeSystem(locationID):
            constellationID = sm.GetService('map').GetParent(locationID)
            data = sm.RemoteSvc('map').GetCurrentSovData(constellationID)
            indexedData = data.Index('locationID')
            return [indexedData[locationID]]
        else:
            return sm.RemoteSvc('map').GetCurrentSovData(locationID)



    def GetRecentActivity(self):
        data = sm.RemoteSvc('map').GetRecentSovActivity()
        return data



    def GetDevIndexLevel(self, points):
        ret = 0
        for (level, value,) in enumerate(self.indexLevels):
            if value < points:
                ret = level + 1
            else:
                break

        return ret



    def OnSovereigntyAudioEvent(self, eventID, textParams):
        if eventID in const.sovAudioEventFiles:
            self.audio.SendUIEvent(unicode(const.sovAudioEventFiles[eventID][0]))
            if const.sovAudioEventFiles[eventID][1] is not None:
                eve.Message(const.sovAudioEventFiles[eventID][1], textParams)




