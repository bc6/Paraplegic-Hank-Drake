import service
import blue
import destiny
import time
import types
import uix
import uthread
import stackless
import math
import util
import marshalstrings
INFINITY_AND_BEYOND = 1000000
DEFAULT_AVOIDANCE = [30000142]

class PathfinderSvc(service.Service):
    __exportedcalls__ = {'SetPodKillAvoidance': [],
     'SetTollAvoidance': [],
     'SetRouteType': [],
     'GetPodKillAvoidance': [],
     'GetTollAvoidance': [],
     'GetRouteType': [],
     'GetRouteTypes': [],
     'GetPathFromCurrent': [],
     'GetPathBetween': [],
     'GetJumpCountFromCurrent': [],
     'GetWaypointPath': [],
     'GetSystemsFromCurrent': [],
     'MakeDirty': [],
     'SetSystemAvoidance': []}
    __guid__ = 'svc.pathfinder'
    __servicename__ = 'pathfinder'
    __displayname__ = 'Pathfinder Service'
    __notifyevents__ = ['ProcessSessionChange']
    __dependencies__ = ['map']
    __startupdependencies__ = ['settings']

    def Run(self, memStream = None):
        self.LogInfo('Starting Pathfinder Service')
        self.routeTypes = {'safe': [0.45, 1.0],
         'unsafe': [0.0, 0.45],
         'unsafe + zerosec': [-1.0, 0.45],
         'shortest': [-1.0, 1.0]}
        self.avoidPodKill = settings.char.ui.Get('pfAvoidPodKill', 0)
        self.avoidSystems = settings.char.ui.Get('pfAvoidSystems', 1)
        self.avoidTolls = settings.char.ui.Get('pfAvoidTolls', 0)
        self.routeType = settings.char.ui.Get('pfRouteType', 'safe')
        self.dirty = {}
        self.cache = {}
        self.systemsByJumpCount = {}
        self.prepared = {}
        for routeType in self.routeTypes.keys():
            self.dirty[routeType] = 1
            self.cache[routeType] = {}
            self.systemsByJumpCount[routeType] = {}
            self.prepared[routeType] = 0

        self.currentSystemID = -1
        self.lastPKversionNumber = -1
        self.solarsystems = []
        self.locks = {}



    def PrepareCache(self):
        if self.prepared[self.routeType]:
            return 
        self.prepared[self.routeType] = 1
        self.mapcache = sm.GetService('map').GetMapCache()
        self.solarsystems = []
        for regionID in self.mapcache['hierarchy'].iterkeys():
            regionDict = self.mapcache['hierarchy'][regionID]
            for constellationID in regionDict.iterkeys():
                self.solarsystems += regionDict[constellationID].keys()
                self.LogInfo('Handling', constellationID, regionDict[constellationID].keys())


        for solarsystemID in self.solarsystems:
            item = self.GetItem(solarsystemID, 1)
            ssitem = item.item
            jumps = [ locID for jumpgroup in item.jumps for locID in jumpgroup ]
            self.cache[self.routeType][solarsystemID] = [0.0,
             solarsystemID,
             None,
             0,
             jumps,
             0.0,
             0,
             0.0]

        for entry in self.cache[self.routeType].itervalues():
            entry[4] = [ self.cache[self.routeType][solarSystemID] for solarSystemID in entry[4] ]

        for each in sm.RemoteSvc('map').GetSolarSystemPseudoSecurities():
            if each.solarSystemID in self.cache[self.routeType]:
                self.cache[self.routeType][each.solarSystemID][5] = round(max(each.security, 0.0), 1)

        self.LogInfo("PrepareCache has now prepared routeType '", self.routeType, "' with", len(self.cache[self.routeType]), 'entries')



    def GetItem(self, itemID, retall = 0):
        self.PrepareCache()
        if 'items' not in self.mapcache:
            self.LogInfo('Pathfinder: Error asking for item ', itemID, ', there is no items')
            return None
        if itemID in self.mapcache['items']:
            if retall:
                return self.mapcache['items'][itemID]
            else:
                return self.mapcache['items'][itemID].item



    def SetPodKillAvoidance(self, pkAvoid):
        if pkAvoid != self.avoidPodKill:
            self.ClearAvoids()
            self.lastPKversionNumber = -1
            self.MakeDirty()
        self.avoidPodKill = pkAvoid
        settings.char.ui.Set('pfAvoidPodKill', pkAvoid)



    def GetPodKillAvoidance(self):
        return self.avoidPodKill



    def SetSystemAvoidance(self, pkAvoid = None):
        self.ClearAvoids()
        self.lastPKversionNumber = -1
        self.MakeDirty()
        if pkAvoid != None:
            self.avoidSystems = pkAvoid
            settings.char.ui.Set('pfAvoidSystems', pkAvoid)



    def GetSystemAvoidance(self):
        return self.avoidSystems



    def GetAvoidanceItems(self, expandSystems = False):
        items = settings.char.ui.Get('autopilot_avoidance2', DEFAULT_AVOIDANCE)
        if expandSystems:
            items = sm.StartService('map').ExpandItems(items)
        return items



    def SetAvoidanceItems(self, items):
        settings.char.ui.Set('autopilot_avoidance2', items)
        sm.ScatterEvent('OnAvoidanceItemsChanged')



    def AddAvoidanceItem(self, itemID):
        items = self.GetAvoidanceItems()
        items.append(itemID)
        self.SetAvoidanceItems(items)
        self.SetSystemAvoidance()
        sm.StartService('starmap').UpdateRoute()



    def RemoveAvoidanceItem(self, itemID):
        items = self.GetAvoidanceItems()
        if itemID in items:
            items.remove(itemID)
            self.SetAvoidanceItems(items)
            self.SetSystemAvoidance()
            sm.StartService('starmap').UpdateRoute()



    def ClearAvoids(self):
        self.PrepareCache()
        for route in self.routeTypes:
            for system in self.cache[route].itervalues():
                system[6] = 0





    def RefreshPodKills(self):
        if self.lastPKversionNumber == -1:
            podKills = sm.RemoteSvc('map').GetHistory(3, 24)
            args = (3, 24)
            versionNumber = self.lastPKversionNumber = sm.GetService('objectCaching').GetCachedMethodCallVersion(None, 'map', 'GetHistory', args)
            self.LogInfo('Updating pod kill cache to version #', versionNumber)
            self.PrepareCache()
            for system in podKills:
                if system.value3 > 0:
                    if system.solarSystemID in self.cache[self.routeType]:
                        self.cache[self.routeType][system.solarSystemID][6] = system.value3

            return 1
        args = (3, 24)
        versionNumber = sm.GetService('objectCaching').GetCachedMethodCallVersion(None, 'map', 'GetHistory', args)
        if versionNumber != self.lastPKversionNumber:
            self.LogInfo('Pod kill cache version mismatch #', versionNumber)
            self.lastPKversionNumber = -1
            return self.RefreshPodKills()
        return 0



    def MakeDirty(self):
        for routes in self.dirty.iterkeys():
            self.dirty[routes] = 1




    def SetRouteType(self, routeType):
        if routeType not in self.routeTypes:
            raise AttributeError, 'Route type should be one of %s' % self.routeTypes
        self.routeType = routeType
        settings.char.ui.Set('pfRouteType', routeType)



    def GetRouteType(self):
        return self.routeType



    def GetRouteTypes(self):
        return self.routeTypes



    def SetTollAvoidance(self, tollAvoid):
        if tollAvoid != self.avoidTolls:
            self.MakeDirty()
        self.avoidTolls = tollAvoid
        settings.char.ui.Set('pfAvoidTolls', tollAvoid)



    def GetTollAvoidance(self):
        return self.avoidsTolls



    def GetPathFromCurrent(self, toID):
        return self.GetPathBetween(eve.session.solarsystemid2, toID)



    def GetSystemsFromCurrent(self, cnt):
        uthread.ReentrantLock(self)
        try:
            self.Refresh(eve.session.solarsystemid2)
            if cnt in self.systemsByJumpCount[self.routeType]:
                return self.systemsByJumpCount[self.routeType][cnt]
            else:
                return []

        finally:
            uthread.UnLock(self)




    def RefreshSystemsByJumpCount(self):
        self.systemsByJumpCount[self.routeType] = {}
        self.PrepareCache()
        for system in self.cache[self.routeType].itervalues():
            if system[0] in self.systemsByJumpCount[self.routeType]:
                self.systemsByJumpCount[self.routeType][system[0]].append(system[1])
            else:
                self.systemsByJumpCount[self.routeType][system[0]] = [system[1]]




    def Refresh(self, solarsystemID, toID = None):
        if solarsystemID is None:
            return 
        isAvoidance = self.avoidPodKill or self.avoidSystems
        if self.currentSystemID != solarsystemID:
            self.currentSystemID = solarsystemID
            self.MakeDirty()
        if self.avoidSystems:
            avoidanceSystems = self.GetAvoidanceItems(True)
            self.LogInfo('Refresh for ', solarsystemID, "with routeType '", self.routeType, "' (avoiding", len(avoidanceSystems), 'systems)')
            for systemID in avoidanceSystems:
                if systemID in self.cache[self.routeType]:
                    oldVal = self.cache[self.routeType][systemID][6]
                    if systemID != toID:
                        self.cache[self.routeType][systemID][6] = 1
                    else:
                        self.cache[self.routeType][systemID][6] = 0
                    if oldVal != self.cache[self.routeType][systemID][6]:
                        self.LogInfo('Data dirty after avoidance setting')
                        self.MakeDirty()

        else:
            self.LogInfo('Refresh for ', solarsystemID, "with routeType '", self.routeType, "'")
        if self.avoidPodKill:
            dirt = self.RefreshPodKills()
            if dirt and not self.dirty[self.routeType]:
                self.MakeDirty()
        if not self.dirty[self.routeType]:
            return 
        self.PrepareCache()
        self.LogInfo('Updating path cache to', self.currentSystemID)
        penalty = settings.char.ui.Get('pfPenalty', 50.0)
        penalty = math.exp(0.15 * penalty)
        now = time.clock()
        destiny.FindShortestPath(self.cache[self.routeType], self.currentSystemID, isAvoidance, self.routeTypes[self.routeType][0], self.routeTypes[self.routeType][1], penalty)
        self.RefreshSystemsByJumpCount()
        self.LogInfo('Refresh done in:', time.clock() - now)
        self.dirty[self.routeType] = 0



    def GetShortestJumpCountFromCurrent(self, toID):
        uthread.Lock(self, 'JumpCalculation')
        try:
            tempPrev = self.routeType
            self.routeType = 'shortest'
            self.PrepareCache()
            locationID = eve.session.solarsystemid2
            self.Refresh(locationID, toID)
            if type(toID) == types.ListType:
                ret = []
                for systemID in toID:
                    ret.append(self.cache[self.routeType][systemID][0])

                self.routeType = tempPrev
                return ret
            else:
                ret = self.cache[self.routeType][toID][0]
                self.routeType = tempPrev
                return ret

        finally:
            uthread.UnLock(self, 'JumpCalculation')




    def GetJumpCountFromCurrent(self, toID, locationID = None):
        uthread.Lock(self, 'JumpCalculation')
        try:
            self.PrepareCache()
            if locationID is None:
                locationID = eve.session.solarsystemid2
            if type(toID) == types.ListType:
                ret = []
                for systemID in toID:
                    self.Refresh(locationID, systemID)
                    ret.append(self.cache[self.routeType][systemID][0])

                return ret
            else:
                self.Refresh(locationID, toID)
                return self.cache[self.routeType][toID][0]

        finally:
            uthread.UnLock(self, 'JumpCalculation')




    def GetMultiJumpCounts(self, solarSystemPairs):
        uthread.Lock(self, 'JumpCalculation')
        try:
            ret = {}
            self.PrepareCache()
            for (fromID, toID,) in solarSystemPairs:
                self.Refresh(fromID, toID)
                ret[(fromID, toID)] = self.cache[self.routeType][toID][0]

            return ret

        finally:
            uthread.UnLock(self, 'JumpCalculation')




    def GetWaypointPath(self, waypoints):
        if len(waypoints) < 2:
            raise AttributeError, 'There should be at least two waypoints'
        fromID = waypoints[0]
        path = []
        for toID in waypoints[1:]:
            segment = self.GetPathBetween(fromID, toID)
            if segment is None:
                path = []
                break
            path += segment[:-1]
            fromID = toID

        if len(path) > 0:
            path.append(toID)
        return path



    def GetPathBetween(self, fromID, toID):
        uthread.ReentrantLock(self)
        try:
            self.PrepareCache()
            self.LogInfo('Getting path between', fromID, 'and', toID)
            self.Refresh(fromID, toID)
            vertex = self.cache[self.routeType][toID]
            if vertex[0] >= INFINITY_AND_BEYOND:
                return 
            else:
                path = []
                while vertex is not None:
                    path.append(vertex[1])
                    vertex = vertex[2]

                path.reverse()
                return path

        finally:
            uthread.UnLock(self)




    def ProcessSessionChange(self, isRemote, session, change, cheat = 0):
        uthread.ReentrantLock(self)
        try:
            if 'solarsystemid' in change:
                self.Refresh(session.solarsystemid2)

        finally:
            uthread.UnLock(self)





