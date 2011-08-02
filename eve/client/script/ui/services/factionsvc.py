import service
import blue
import bluepy
import util

class Faction(service.Service):
    __exportedcalls__ = {'GetFaction': [],
     'GetFactionEx': [],
     'GetCorpsOfFaction': [],
     'GetFactionLocations': [],
     'GetFactionOfSolarSystem': [],
     'GetPirateFactionsOfRegion': []}
    __guid__ = 'svc.faction'
    __notifyevents__ = ['OnSessionChanged']
    __servicename__ = 'account'
    __displayname__ = 'Faction Service'

    def __init__(self):
        service.Service.__init__(self)



    def Run(self, memStream = None):
        self.LogInfo('Starting Faction Svc')
        self.factions = {}
        self.factionIDbyNPCCorpID = None
        self.factionRegions = None
        self.factionConstellations = None
        self.factionSolarSystems = None
        self.factionRaces = None
        self.factionStationCount = None
        self.factionSolarSystemCount = None
        self.npcCorpInfo = None
        self.corpsByFactionID = {}
        self.currentFactionID = None



    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid2' in change:
            self.currentFactionID = (eve.session.solarsystemid2, self.GetFactionOfSolarSystem(eve.session.solarsystemid2))



    def GetCurrentFactionID(self):
        if self.currentFactionID is None:
            self.currentFactionID = (eve.session.solarsystemid2, self.GetFactionOfSolarSystem(eve.session.solarsystemid2))
        return self.currentFactionID[1]



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetFactionOfSolarSystem(self, solarsystemID):
        if self.factionRegions is None:
            self.GetData()
        if not hasattr(self, 'foss'):
            self.foss = {}
            for each in (self.factionSolarSystems, self.factionConstellations, self.factionRegions):
                for (factionID, theIDs,) in each.iteritems():
                    for theID in theIDs:
                        self.foss[theID] = factionID



        (bla, regionID, constellationID, gra, sma,) = sm.GetService('map').GetParentLocationID(solarsystemID, gethierarchy=1)
        return self.foss.get(solarsystemID, self.foss.get(constellationID, self.foss.get(regionID, None)))



    def GetPirateFactionsOfRegion(self, regionID):
        return {10000001: (500019,),
         10000002: (500010,),
         10000003: (500010,),
         10000005: (500011,),
         10000006: (500011,),
         10000007: (500011,),
         10000008: (500011,),
         10000009: (500011,),
         10000010: (500010,),
         10000011: (500011,),
         10000012: (500011,),
         10000014: (500019,),
         10000015: (500010,),
         10000016: (500010,),
         10000020: (500019,),
         10000022: (500019,),
         10000023: (500010,),
         10000025: (500011,),
         10000028: (500011,),
         10000029: (500010,),
         10000030: (500011,),
         10000031: (500011,),
         10000032: (500020,),
         10000033: (500010,),
         10000035: (500010,),
         10000036: (500019,),
         10000037: (500020,),
         10000038: (500012,),
         10000039: (500019,),
         10000041: (500020,),
         10000042: (500011,),
         10000043: (500019,),
         10000044: (500020,),
         10000045: (500010,),
         10000046: (500020,),
         10000047: (500019,),
         10000048: (500020,),
         10000049: (500012, 500019),
         10000050: (500012,),
         10000051: (500020,),
         10000052: (500012,),
         10000054: (500012,),
         10000055: (500010,),
         10000056: (500011,),
         10000057: (500020,),
         10000058: (500020,),
         10000059: (500019,),
         10000060: (500012,),
         10000061: (500011,),
         10000062: (500011,),
         10000063: (500012,),
         10000064: (500020,),
         10000065: (500012,),
         10000067: (500012,),
         10000068: (500020,)}.get(regionID, ())



    def GetFactionLocations(self, factionID):
        if self.factionRegions is None:
            self.GetData()
        return (self.factionRegions.get(factionID, []), self.factionConstellations.get(factionID, []), self.factionSolarSystems.get(factionID, []))



    def GetFactionInfo(self, factionID):
        if self.factionRegions is None:
            self.GetData()
        return (self.factionRaces.get(factionID, [1,
          2,
          4,
          8]), self.factionStationCount.get(factionID, 0), self.factionSolarSystemCount.get(factionID, 0))



    def Stop(self, memStream = None):
        (self.factionIDbyNPCCorpID, self.factionRegions, self.factionConstellations, self.factionSolarSystems, self.factionRaces, self.factionAllies, self.factionEnemies,) = (None, None, None, None, None, None, None)



    def GetFaction(self, corporationID):
        if self.factionIDbyNPCCorpID is None:
            self.GetData()
        return self.factionIDbyNPCCorpID.get(corporationID, None)



    def GetFactionEx(self, factionID = None):
        if not self.factions:
            factions = sm.RemoteSvc('charMgr').GetFactions()
            for (i, faction,) in enumerate(factions):
                self.factions[faction.factionID] = factions[i]

        if self.factions:
            if factionID:
                return self.factions.get(factionID, None)
            else:
                return self.factions



    def GetNPCCorpInfo(self, corpID):
        if self.npcCorpInfo is None:
            self.GetData()
        return self.npcCorpInfo.get(corpID, None)



    def GetCorpsOfFaction(self, factionID):
        if not self.corpsByFactionID:
            self.GetData()
        return self.corpsByFactionID.get(factionID, [])



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetData(self):
        (self.factionIDbyNPCCorpID, self.factionRegions, self.factionConstellations, self.factionSolarSystems, self.factionRaces, self.factionStationCount, self.factionSolarSystemCount, self.npcCorpInfo,) = sm.RemoteSvc('corporationSvc').GetFactionInfo()
        for (corpID, factionID,) in self.factionIDbyNPCCorpID.iteritems():
            if factionID not in self.corpsByFactionID:
                self.corpsByFactionID[factionID] = []
            if corpID not in self.corpsByFactionID[factionID]:
                self.corpsByFactionID[factionID].append(corpID)

        owners = {}
        for (k, v,) in self.factionIDbyNPCCorpID.iteritems():
            owners[k] = 0
            owners[v] = 0

        owners = owners.keys()
        if len(owners):
            cfg.eveowners.Prime(owners)




