import uiconst
import service
import blue
import util
import uiutil
import localization

class FactionalWarfare(service.Service):
    __exportedcalls__ = {'IsEnemyFaction': [],
     'IsEnemyCorporation': [],
     'JoinFactionAsCorporation': [],
     'JoinFactionAsCharacter': [],
     'LeaveFactionAsCorporation': [],
     'WithdrawJoinFactionAsCorporation': [],
     'WithdrawLeaveFactionAsCorporation': [],
     'GetFactionalWarStatus': [],
     'GetWarFactions': [],
     'GetCorporationWarFactionID': [],
     'GetFactionCorporations': [],
     'GetFactionMilitiaCorporation': [],
     'GetCharacterRankInfo': [],
     'GetEnemies': [],
     'GetStats_FactionInfo': [],
     'GetStats_Personal': [],
     'GetStats_Corp': [],
     'GetStats_CorpPilots': [],
     'GetSystemsConqueredThisRun': [],
     'GetDistanceToEnemySystems': [],
     'GetMostDangerousSystems': [],
     'GetSystemStatus': [],
     'CheckForSafeSystem': []}
    __guid__ = 'svc.facwar'
    __servicename__ = 'facwar'
    __displayname__ = 'Factional Warfare'
    __notifyevents__ = ['OnNPCStandingChange', 'ProcessSystemStatusChanged', 'ProcessSessionChange']

    def __init__(self):
        service.Service.__init__(self)
        self.facWarSystemCount = {}
        self.warFactionByOwner = {}
        self.topStats = None
        self.statusBySystemID = {}
        self.remoteFacWarMgr = None
        self.FWSystems = None



    def Run(self, memStream = None):
        self.LogInfo('Starting Factional Warfare Svc')
        self.objectCaching = sm.GetService('objectCaching')



    @property
    def facWarMgr(self):
        if self.remoteFacWarMgr is None:
            self.remoteFacWarMgr = sm.RemoteSvc('facWarMgr')
        return self.remoteFacWarMgr



    def ProcessSystemStatusChanged(self, *args):
        if args[1]:
            sm.ScatterEvent('OnRemoteMessage', args[1][0], args[1][1])
        self.LogInfo('ProcessSystemStatusChanged() called with stateinfo', args[0])
        statusinfo = args[0]
        if statusinfo[0] == 1 and self.statusBySystemID.get(session.solarsystemid, -1) == 2 and statusinfo[1] and session.warfactionid and session.warfactionid not in statusinfo[1]:
            self.LogInfo('Not setting the new state (', statusinfo[0], ') as my warfactionid (', session.warfactionid, ') is not in list.')
            return 
        if statusinfo[0] == 2 and statusinfo[1] and session.warfactionid and session.warfactionid not in statusinfo[1]:
            self.LogInfo('Not setting the new state (', statusinfo[0], ') as my warfactionid (', session.warfactionid, ') is not in list.')
            return 
        self.LogInfo('Updating state')
        self.statusBySystemID[session.solarsystemid] = statusinfo[0]
        sm.ScatterEvent('OnSystemStatusChanged')



    def ProcessSessionChange(self, isRemote, session, change):
        if 'solarsystemid' in change:
            (lastSystem, newSystem,) = change['solarsystemid']
            if lastSystem and self.statusBySystemID.has_key(lastSystem):
                del self.statusBySystemID[lastSystem]
            if newSystem and self.statusBySystemID.has_key(newSystem):
                del self.statusBySystemID[newSystem]



    def IsEnemyFaction(self, enemyID, factionID):
        return self.facWarMgr.IsEnemyFaction(enemyID, factionID)



    def IsEnemyCorporation(self, enemyID, factionID):
        return self.facWarMgr.IsEnemyCorporation(enemyID, factionID)



    def GetSystemsConqueredThisRun(self):
        return self.facWarMgr.GetSystemsConqueredThisRun()



    def GetDistanceToEnemySystems(self):
        if session.warfactionid is None:
            return 
        enemyFactions = self.GetEnemies(session.warfactionid)
        enemySystems = [ util.KeyVal(solarSystemID=k, occupierID=v['occupierID'], numJumps=0) for (k, v,) in self.GetFacWarSystems().iteritems() if v['occupierID'] in enemyFactions ]
        for s in enemySystems:
            s.numJumps = int(sm.GetService('pathfinder').GetJumpCountFromCurrent(s.solarSystemID))
            blue.pyos.BeNice()

        enemySystems.sort(lambda x, y: cmp(x.numJumps, y.numJumps))
        return enemySystems



    def GetMostDangerousSystems(self):
        historyDB = sm.RemoteSvc('map').GetHistory(5, 24)
        dangerousSystems = []
        for each in historyDB:
            if each.value1 - each.value2 > 0:
                dangerousSystems.append(util.KeyVal(solarSystemID=each.solarSystemID, numKills=each.value1 - each.value2))

        dangerousSystems.sort(lambda x, y: cmp(y.numKills, x.numKills))
        return dangerousSystems



    def GetCorporationWarFactionID(self, corpID):
        if util.IsNPC(corpID):
            for (factionID, militiaCorpID,) in self.GetWarFactions().iteritems():
                if militiaCorpID == corpID:
                    return factionID

            return None
        ret = self.facWarMgr.GetCorporationWarFactionID(corpID)
        if not ret:
            return None
        return ret



    def GetFactionCorporations(self, factionID):
        return self.facWarMgr.GetFactionCorporations(factionID)



    def GetFacWarSystems(self):
        if self.FWSystems is None:
            self.FWSystems = self.facWarMgr.GetFWSystems()
        return self.FWSystems



    def GetFacWarSystem(self, solarSystemID = None):
        return self.GetFacWarSystems().get(solarSystemID)



    def GetFactionMilitiaCorporation(self, factionID):
        ret = self.facWarMgr.GetFactionMilitiaCorporation(factionID)
        if not ret:
            return None
        return ret



    def JoinFactionAsCharacter(self, factionID, warfactionid):
        MIN_STANDING = 0.5
        if warfactionid:
            alreadyInMilitiaLabel = localization.GetByLabel('UI/FactionWarfare/AlreadyInMilitia')
            eve.Message('CustomInfo', {'info': alreadyInMilitiaLabel})
            return 
        ownerName = cfg.eveowners.Get(factionID).name
        standing = sm.StartService('standing').GetStanding(factionID, eve.session.charid)
        if standing < MIN_STANDING and not sm.GetService('corp').UserIsCEO():
            itemID = None
            inv = sm.GetService('invCache').GetInventory(const.containerHangar)
            items = inv.List()
            for item in items:
                if item.typeID == const.typeLetterOfRecommendation:
                    itemID = item.itemID
                    break

            if itemID:
                ret = eve.Message('JoinFacWarRecommendation', {'factionName': ownerName,
                 'standing': MIN_STANDING}, uiconst.YESNO)
                if ret == uiconst.ID_YES:
                    sm.StartService('sessionMgr').PerformSessionChange('corp.joinmilitia', self.facWarMgr.JoinFactionAsCharacterRecommendationLetter, factionID, itemID)
                return 
        headerLabel = localization.GetByLabel('UI/FactionWarfare/JoinConfirmationHeader')
        bodyLabel = localization.GetByLabel('UI/FactionWarfare/JoinConfirmationQuestionPlayer', factionName=ownerName)
        ret = eve.Message('CustomQuestion', {'header': headerLabel,
         'question': bodyLabel}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            sm.GetService('sessionMgr').PerformSessionChange('corp.joinmilitia', self.facWarMgr.JoinFactionAsCharacter, factionID)
            invalidate = [('facWarMgr', 'GetMyCharacterRankInfo', ()), ('facWarMgr', 'GetMyCharacterRankOverview', ()), ('corporationSvc', 'GetEmploymentRecord', (session.charid,))]
            self.objectCaching.InvalidateCachedMethodCalls(invalidate)



    def JoinFactionAsCorporation(self, factionID, warfactionid):
        ownerName = cfg.eveowners.Get(factionID).name
        headerLabel = localization.GetByLabel('UI/FactionWarfare/JoinConfirmationHeader')
        bodyLabel = localization.GetByLabel('UI/FactionWarfare/JoinConfirmationQuestionCorp', factionName=ownerName)
        if warfactionid:
            alreadyInMilitiaLabel = localization.GetByLabel('UI/FactionWarfare/AlreadyInMilitia')
            eve.Message('CustomInfo', {'info': alreadyInMilitiaLabel})
            return 
        ret = eve.Message('CustomQuestion', {'header': headerLabel,
         'question': bodyLabel}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            self.facWarMgr.JoinFactionAsCorporation(factionID)
            sm.ScatterEvent('OnJoinMilitia')



    def LeaveFactionAsCorporation(self, factionID):
        self.facWarMgr.LeaveFactionAsCorporation(factionID)



    def WithdrawJoinFactionAsCorporation(self, factionID):
        self.facWarMgr.WithdrawJoinFactionAsCorporation(factionID)



    def WithdrawLeaveFactionAsCorporation(self, factionID):
        self.facWarMgr.WithdrawLeaveFactionAsCorporation(factionID)



    def GetFactionalWarStatus(self):
        return self.facWarMgr.GetFactionalWarStatus()



    def GetWarFactions(self):
        return self.facWarMgr.GetWarFactions()



    def GetCharacterRankInfo(self, charID, corpID = None):
        if corpID is None or self.GetCorporationWarFactionID(corpID) is not None:
            if charID == session.charid:
                return self.facWarMgr.GetMyCharacterRankInfo()
            else:
                return self.facWarMgr.GetCharacterRankInfo(charID)



    def GetCharacterRankOverview(self, charID):
        if not charID == session.charid:
            return None
        return self.facWarMgr.GetMyCharacterRankOverview()



    def RefreshCorps(self):
        return self.facWarMgr.RefreshCorps()



    def OnNPCStandingChange(self, fromID, newStanding, oldStanding):
        if fromID == self.GetFactionMilitiaCorporation(session.warfactionid):
            oldrank = self.GetCharacterRankInfo(session.charid).currentRank
            if oldrank != min(max(int(newStanding), 0), 9):
                newrank = self.facWarMgr.CheckForRankChange()
                if newrank is not None and oldrank != newrank:
                    self.DoOnRankChange(oldrank, newrank)
        invalidate = [('facWarMgr', 'GetMyCharacterRankInfo', ()), ('facWarMgr', 'GetMyCharacterRankOverview', ())]
        self.objectCaching.InvalidateCachedMethodCalls(invalidate)



    def DoOnRankChange(self, oldrank, newrank):
        messageID = 'RankGained' if newrank > oldrank else 'RankLost'
        (rankLabel, rankDescription,) = self.GetRankLabel(session.warfactionid, newrank)
        try:
            eve.Message(messageID, {'rank': rankLabel})
        except:
            sys.exc_clear()
        sm.ScatterEvent('OnRankChange', oldrank, newrank)



    def GetEnemies(self, factionID):
        warFactions = self.GetWarFactions()
        enemies = []
        for each in warFactions.iterkeys():
            if self.IsEnemyFaction(factionID, each):
                enemies.append(each)

        return enemies



    def GetStats_FactionInfo(self):
        return self.facWarMgr.GetStats_FactionInfo()



    def GetStats_Personal(self):
        header = ['you', 'top', 'all']
        data = {'killsY': {'you': 0,
                    'top': 0,
                    'all': 0},
         'killsLW': {'you': 0,
                     'top': 0,
                     'all': 0},
         'killsTotal': {'you': 0,
                        'top': 0,
                        'all': 0},
         'vpY': {'you': 0,
                 'top': 0,
                 'all': 0},
         'vpLW': {'you': 0,
                  'top': 0,
                  'all': 0},
         'vpTotal': {'you': 0,
                     'top': 0,
                     'all': 0}}
        if not self.topStats:
            self.topStats = self.facWarMgr.GetStats_TopAndAllKillsAndVPs()
        for k in ('killsY', 'killsLW', 'killsTotal', 'vpY', 'vpLW', 'vpTotal'):
            data[k]['top'] = self.topStats[0][const.groupCharacter][k]
            data[k]['all'] = self.topStats[1][const.groupCharacter][k]

        for (k, v,) in self.facWarMgr.GetStats_Character().items():
            data[k]['you'] = v

        return {'header': header,
         'data': data}



    def GetStats_Corp(self, corpID):
        header = ['your', 'top', 'all']
        data = {'killsY': {'your': 0,
                    'top': 0,
                    'all': 0},
         'killsLW': {'your': 0,
                     'top': 0,
                     'all': 0},
         'killsTotal': {'your': 0,
                        'top': 0,
                        'all': 0},
         'vpY': {'your': 0,
                 'top': 0,
                 'all': 0},
         'vpLW': {'your': 0,
                  'top': 0,
                  'all': 0},
         'vpTotal': {'your': 0,
                     'top': 0,
                     'all': 0}}
        if not self.topStats:
            self.topStats = self.facWarMgr.GetStats_TopAndAllKillsAndVPs()
        for k in ('killsY', 'killsLW', 'killsTotal', 'vpY', 'vpLW', 'vpTotal'):
            data[k]['top'] = self.topStats[0][const.groupCorporation][k]
            data[k]['all'] = self.topStats[1][const.groupCorporation][k]

        for (k, v,) in self.facWarMgr.GetStats_Corp().items():
            data[k]['your'] = v

        return {'header': header,
         'data': data}



    def GetStats_Militia(self):
        return self.facWarMgr.GetStats_Militia()



    def GetStats_CorpPilots(self):
        return self.facWarMgr.GetStats_CorpPilots()



    def GetStats_Systems(self):
        systemsThatWillSwitchNextDownTime = self.GetSystemsConqueredThisRun()
        cfg.evelocations.Prime([ d['solarsystemID'] for d in systemsThatWillSwitchNextDownTime ])
        cfg.eveowners.Prime([ d['occupierID'] for d in systemsThatWillSwitchNextDownTime ])
        tempList = []
        for each in systemsThatWillSwitchNextDownTime:
            tempList.append((each.get('taken'), each))

        systemsThatWillSwitchNextDownTime = uiutil.SortListOfTuples(tempList, reverse=1)
        return systemsThatWillSwitchNextDownTime



    def CheckOwnerInFaction(self, ownerID, factionID = None):
        factions = [ each for each in self.GetWarFactions() ]
        if not self.warFactionByOwner.has_key(ownerID):
            faction = sm.GetService('faction').GetFaction(ownerID)
            if faction and faction in factions:
                self.warFactionByOwner[ownerID] = faction
        return self.warFactionByOwner.get(ownerID, None)



    def GetSystemStatus(self):
        if self.statusBySystemID.has_key(session.solarsystemid2):
            self.LogInfo('GetSystemStatus: Returning cached status:', self.statusBySystemID[session.solarsystemid2])
            return self.statusBySystemID[session.solarsystemid2]
        status = self.facWarMgr.GetSystemStatus(session.solarsystemid2, session.warfactionid)
        self.statusBySystemID[session.solarsystemid2] = status
        self.LogInfo('GetSystemStatus: Returning status from server:', status)
        return status



    def CheckForSafeSystem(self, stationItem, factionID, solarSystemID = None):
        ss = sm.GetService('map').GetSecurityClass(solarSystemID or eve.session.solarsystemid2)
        if ss != const.securityClassHighSec:
            return True
        fosi = sm.StartService('faction').GetFaction(stationItem.ownerID)
        if fosi is None:
            return True
        foss = sm.StartService('faction').GetFactionOfSolarSystem(solarSystemID or eve.session.solarsystemid2)
        eof = self.GetEnemies(factionID)
        if foss in eof:
            return False
        return True



    def CheckStationElegibleForMilitia(self, station = None):
        if eve.session.warfactionid:
            return eve.session.warfactionid
        if station is None and not session.stationid2:
            return False
        ownerID = None
        if station:
            ownerID = station.ownerID
        elif session.stationid2:
            ownerID = eve.stationItem.ownerID
        if ownerID:
            check = self.CheckOwnerInFaction(ownerID)
            if check is not None:
                return check
        return False



    def GetRankLabel(self, factionID, rank):
        rank = min(9, rank)
        (rankLabel, rankDescription,) = ('', '')
        if rank < 0:
            rankLabel = localization.GetByLabel('UI/FactionWarfare/Ranks/NoRank')
            rankDescription = ''
        else:
            (rankPath, descPath,) = RankLabelsByFactionID.get((factionID, rank), ('UI/FactionWarfare/Ranks/NoRank', 'UI/FactionWarfare/Ranks/NoRank'))
            rankLabel = localization.GetByLabel(rankPath)
            rankDescription = localization.GetByLabel(descPath)
        return (rankLabel, rankDescription)



RankLabelsByFactionID = {(const.factionCaldariState, 0): ('UI/FactionWarfare/Ranks/RankCaldari0', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari0'),
 (const.factionCaldariState, 1): ('UI/FactionWarfare/Ranks/RankCaldari1', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari1'),
 (const.factionCaldariState, 2): ('UI/FactionWarfare/Ranks/RankCaldari2', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari2'),
 (const.factionCaldariState, 3): ('UI/FactionWarfare/Ranks/RankCaldari3', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari3'),
 (const.factionCaldariState, 4): ('UI/FactionWarfare/Ranks/RankCaldari4', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari4'),
 (const.factionCaldariState, 5): ('UI/FactionWarfare/Ranks/RankCaldari5', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari5'),
 (const.factionCaldariState, 6): ('UI/FactionWarfare/Ranks/RankCaldari6', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari6'),
 (const.factionCaldariState, 7): ('UI/FactionWarfare/Ranks/RankCaldari7', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari7'),
 (const.factionCaldariState, 8): ('UI/FactionWarfare/Ranks/RankCaldari8', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari8'),
 (const.factionCaldariState, 9): ('UI/FactionWarfare/Ranks/RankCaldari9', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari9'),
 (const.factionMinmatarRepublic, 0): ('UI/FactionWarfare/Ranks/RankMinmatar0', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar0'),
 (const.factionMinmatarRepublic, 1): ('UI/FactionWarfare/Ranks/RankMinmatar1', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar1'),
 (const.factionMinmatarRepublic, 2): ('UI/FactionWarfare/Ranks/RankMinmatar2', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar2'),
 (const.factionMinmatarRepublic, 3): ('UI/FactionWarfare/Ranks/RankMinmatar3', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar3'),
 (const.factionMinmatarRepublic, 4): ('UI/FactionWarfare/Ranks/RankMinmatar4', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar4'),
 (const.factionMinmatarRepublic, 5): ('UI/FactionWarfare/Ranks/RankMinmatar5', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar5'),
 (const.factionMinmatarRepublic, 6): ('UI/FactionWarfare/Ranks/RankMinmatar6', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar6'),
 (const.factionMinmatarRepublic, 7): ('UI/FactionWarfare/Ranks/RankMinmatar7', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar7'),
 (const.factionMinmatarRepublic, 8): ('UI/FactionWarfare/Ranks/RankMinmatar8', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar8'),
 (const.factionMinmatarRepublic, 9): ('UI/FactionWarfare/Ranks/RankMinmatar9', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar9'),
 (const.factionAmarrEmpire, 0): ('UI/FactionWarfare/Ranks/RankAmarr0', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr0'),
 (const.factionAmarrEmpire, 1): ('UI/FactionWarfare/Ranks/RankAmarr1', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr1'),
 (const.factionAmarrEmpire, 2): ('UI/FactionWarfare/Ranks/RankAmarr2', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr2'),
 (const.factionAmarrEmpire, 3): ('UI/FactionWarfare/Ranks/RankAmarr3', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr3'),
 (const.factionAmarrEmpire, 4): ('UI/FactionWarfare/Ranks/RankAmarr4', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr4'),
 (const.factionAmarrEmpire, 5): ('UI/FactionWarfare/Ranks/RankAmarr5', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr5'),
 (const.factionAmarrEmpire, 6): ('UI/FactionWarfare/Ranks/RankAmarr6', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr6'),
 (const.factionAmarrEmpire, 7): ('UI/FactionWarfare/Ranks/RankAmarr7', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr7'),
 (const.factionAmarrEmpire, 8): ('UI/FactionWarfare/Ranks/RankAmarr8', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr8'),
 (const.factionAmarrEmpire, 9): ('UI/FactionWarfare/Ranks/RankAmarr9', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr9'),
 (const.factionGallenteFederation, 0): ('UI/FactionWarfare/Ranks/RankGallente0', 'UI/FactionWarfare/Ranks/RankDescriptionGallente0'),
 (const.factionGallenteFederation, 1): ('UI/FactionWarfare/Ranks/RankGallente1', 'UI/FactionWarfare/Ranks/RankDescriptionGallente1'),
 (const.factionGallenteFederation, 2): ('UI/FactionWarfare/Ranks/RankGallente2', 'UI/FactionWarfare/Ranks/RankDescriptionGallente2'),
 (const.factionGallenteFederation, 3): ('UI/FactionWarfare/Ranks/RankGallente3', 'UI/FactionWarfare/Ranks/RankDescriptionGallente3'),
 (const.factionGallenteFederation, 4): ('UI/FactionWarfare/Ranks/RankGallente4', 'UI/FactionWarfare/Ranks/RankDescriptionGallente4'),
 (const.factionGallenteFederation, 5): ('UI/FactionWarfare/Ranks/RankGallente5', 'UI/FactionWarfare/Ranks/RankDescriptionGallente5'),
 (const.factionGallenteFederation, 6): ('UI/FactionWarfare/Ranks/RankGallente6', 'UI/FactionWarfare/Ranks/RankDescriptionGallente6'),
 (const.factionGallenteFederation, 7): ('UI/FactionWarfare/Ranks/RankGallente7', 'UI/FactionWarfare/Ranks/RankDescriptionGallente7'),
 (const.factionGallenteFederation, 8): ('UI/FactionWarfare/Ranks/RankGallente8', 'UI/FactionWarfare/Ranks/RankDescriptionGallente8'),
 (const.factionGallenteFederation, 9): ('UI/FactionWarfare/Ranks/RankGallente9', 'UI/FactionWarfare/Ranks/RankDescriptionGallente9')}

