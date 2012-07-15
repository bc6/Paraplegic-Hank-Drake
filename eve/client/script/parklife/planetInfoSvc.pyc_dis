#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/parklife/planetInfoSvc.py
import service
import uicls
import uiconst
import util
import trinity
from collections import defaultdict

class PlanetInfoSvc(service.Service):
    __guid__ = 'svc.planetInfo'
    __notifyevents__ = ['OnSessionChanged',
     'DoBallsAdded',
     'DoBallRemove',
     'OnLocalHackProgressUpdated']
    __servicename__ = 'PlanetInfo'
    __displayname__ = 'Planet Info Caching Service'
    __dependencies__ = ['michelle']

    def Run(self, memStream = None):
        self.state = service.SERVICE_START_PENDING
        self.LogInfo('PlanetInfo::Starting')
        self.Reset()
        self.hackProgress = {}
        self.state = service.SERVICE_RUNNING

    def Stop(self, memStream = None):
        if not trinity.app:
            return
        self.LogInfo('PlanetInfo::Stopping')
        self.Reset()

    def OnSessionChanged(self, isremote, session, change):
        if session.charid is None:
            return
        if 'solarsystemid' in change:
            self.Reset()

    def OnLocalHackProgressUpdated(self, hackedObjectID, hackProgress):
        self.hackProgress[hackedObjectID] = hackProgress
        bracket = sm.GetService('bracket').GetBracket(hackedObjectID)
        if bracket and bracket.sr.orbitalHackLocal is not None:
            bracket.UpdateHackProgress(hackProgress)

    def GetMyHackProgress(self, itemID):
        return self.hackProgress.get(itemID, None)

    def Reset(self):
        self.LogInfo('PlanetInfo::Reset')
        self.planets = set()
        self.orbitals = set()
        self.orbitalsByPlanetID = defaultdict(lambda : defaultdict(set))

    def GetOrbitalsForPlanet(self, planetID, groupID):
        if planetID in self.orbitalsByPlanetID and groupID in self.orbitalsByPlanetID[planetID]:
            return self.orbitalsByPlanetID[planetID][groupID]
        return set()

    def DoBallsAdded(self, ballItems, *args, **kwargs):
        for ball, slimItem in ballItems:
            if slimItem.groupID == const.groupPlanet:
                self._AddPlanet(ball, slimItem)
            elif util.IsOrbital(slimItem.categoryID):
                self._AddOrbital(ball, slimItem)

    def DoBallRemove(self, ball, slimItem, *args, **kwargs):
        if slimItem.groupID == const.groupPlanet and slimItem.itemID in self.planets:
            self._RemovePlanet(ball, slimItem)
        elif util.IsOrbital(slimItem.categoryID) and slimItem.itemID in self.orbitals:
            self._RemoveOrbital(ball, slimItem)

    def _AddPlanet(self, ball, slimItem):
        self.planets.add(slimItem.itemID)

    def _RemovePlanet(self, ball, slimItem):
        self.planets.remove(slimItem.itemID)
        if slimItem.itemID in self.orbitalsByPlanetID:
            del self.orbitalsByPlanetID[slimItem.itemID]

    def _AddOrbital(self, ball, slimItem):
        self.orbitals.add(slimItem.itemID)
        self.orbitalsByPlanetID[slimItem.planetID][slimItem.groupID].add(slimItem.itemID)

    def _RemoveOrbital(self, ball, slimItem):
        self.orbitals.remove(slimItem.itemID)
        if slimItem.planetID in self.orbitalsByPlanetID:
            for groupID, groupList in self.orbitalsByPlanetID[slimItem.planetID].iteritems():
                if slimItem.itemID in groupList:
                    groupList.remove(slimItem.itemID)
                    if len(groupList) == 0:
                        del self.orbitalsByPlanetID[slimItem.planetID][groupID]
                    break