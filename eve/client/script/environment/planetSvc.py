import service
import moniker
import planet
import blue
import util
import uthread
import const
import planetCommon

class PlanetService(service.Service):
    __guid__ = 'svc.planetSvc'
    __servicename__ = 'planetSvc'
    __displayName__ = 'Planet Service'
    __notifyevents__ = ['OnMajorPlanetStateUpdate', 'OnPlanetChangesSubmitted', 'OnPlanetViewChanged']

    def Run(self, memStream = None):
        self.LogInfo('Starting planet service')
        self.planets = {}
        self.simPlanets = {}
        self.colonizationData = None
        self.state = service.SERVICE_RUNNING
        self.foreignColoniesByPlanet = {}
        self.commandPinsByPlanet = {}
        self.extractorsByPlanet = {}



    def GetPlanet(self, planetID):
        if planetID not in self.planets:
            self.planets[planetID] = planet.ClientPlanet(self, planetID)
        ret = self.planets[planetID]
        return ret



    def GetMyPlanets(self):
        if self.colonizationData is None:
            self.colonizationData = sm.RemoteSvc('planetMgr').GetPlanetsForChar()
        return self.colonizationData



    def IsPlanetColonizedByMe(self, planetID):
        planets = self.GetMyPlanets()
        for planet in planets:
            if planetID == planet.planetID:
                return True

        return False



    def GetColonyForCharacter(self, planetID, characterID):
        if planetID not in self.foreignColoniesByPlanet:
            self.foreignColoniesByPlanet[planetID] = {}
        colonyData = self.foreignColoniesByPlanet[planetID].get(characterID, None)
        if colonyData is None or colonyData.timestamp + planetCommon.PLANET_CACHE_TIMEOUT < blue.os.GetWallclockTime():
            self.LogInfo('GetColonyForCharacter :: Fetching fresh data due to lack of colony or expired timestamp for planet', planetID, 'character', characterID)
            remotePlanet = moniker.GetPlanet(planetID)
            colonyData = util.KeyVal(timestamp=blue.os.GetWallclockTime())
            colonyData.data = remotePlanet.GetFullNetworkForOwner(planetID, characterID)
            self.foreignColoniesByPlanet[planetID][characterID] = colonyData
        return colonyData.data



    def GetPlanetCommandPins(self, planetID):
        pinData = self.commandPinsByPlanet.get(planetID, None)
        if pinData is None or pinData.timestamp + planetCommon.PLANET_CACHE_TIMEOUT < blue.os.GetWallclockTime():
            self.LogInfo('GetPlanetCommandPins :: Fetching fresh data due to lack of data or expired timestamp for planet', planetID)
            remotePlanet = moniker.GetPlanet(planetID)
            pinData = util.KeyVal(timestamp=blue.os.GetWallclockTime())
            pinData.data = remotePlanet.GetCommandPinsForPlanet(planetID)
            self.commandPinsByPlanet[planetID] = pinData
        return pinData.data



    def GetExtractorsForPlanet(self, planetID):
        extractorData = self.extractorsByPlanet.get(planetID, None)
        if extractorData is None or extractorData.timestamp + planetCommon.PLANET_CACHE_TIMEOUT < blue.os.GetWallclockTime():
            self.LogInfo('GetPlanetExtractors :: Fetching fresh data due to lack of data or expired timestamp for planet', planetID)
            remotePlanet = moniker.GetPlanet(planetID)
            extractorData = util.KeyVal(timestamp=blue.os.GetWallclockTime())
            extractorData.data = remotePlanet.GetExtractorsForPlanet(planetID)
            self.extractorsByPlanet[planetID] = extractorData
        return extractorData.data



    def OnMajorPlanetStateUpdate(self, planetID, numCommandCentersChanged = False):
        if planetID in self.planets:
            self.planets[planetID].Init()
        if planetID in self.simPlanets:
            self.simPlanets[planetID].Init()
        if numCommandCentersChanged:
            self._UpdateColonyPresence(planetID)
        else:
            self._UpdateColonyNumberOfPins(planetID)
        sm.ScatterEvent('OnPlanetPinsChanged', planetID)



    def OnPlanetChangesSubmitted(self, planetID):
        self._UpdateColonyNumberOfPins(planetID)



    def _UpdateColonyPresence(self, planetID):
        if planetID not in self.planets:
            self.colonizationData = [ colony for colony in self.colonizationData if colony.planetID != planetID ]
        elif self.colonizationData is not None:
            colony = self.planets[planetID].GetColony(session.charid)
            if colony is None or colony.colonyData is None or len(colony.colonyData.pins) < 1:
                self.colonizationData = [ colony for colony in self.colonizationData if colony.planetID != planetID ]
            else:
                addColony = True
                for c in self.colonizationData:
                    if c.planetID == planetID:
                        c.numberOfPins = len(colony.colonyData.pins)
                        addColony = False
                        break

                if addColony:
                    newEntry = util.KeyVal(solarSystemID=self.planets[planetID].solarSystemID, planetID=planetID, typeID=self.planets[planetID].GetPlanetTypeID(), numberOfPins=len(colony.colonyData.pins))
                    self.colonizationData.append(newEntry)
        sm.ScatterEvent('OnColonyPinCountUpdated', planetID)



    def _UpdateColonyNumberOfPins(self, planetID):
        planet = self.planets.get(planetID, None)
        if not planet:
            return 
        data = self.GetMyPlanets()
        for dataRow in data:
            if dataRow.planetID == planetID:
                colony = planet.GetColony(session.charid)
                if colony is not None and colony.colonyData is not None:
                    if dataRow.numberOfPins != len(colony.colonyData.pins):
                        dataRow.numberOfPins = len(colony.colonyData.pins)
                        sm.ScatterEvent('OnColonyPinCountUpdated', planetID)
                else:
                    dataRow.numberOfPins = 0
                    sm.ScatterEvent('OnColonyPinCountUpdated', planetID)
                break




    def OnPlanetViewChanged(self, newPlanetID, oldPlanetID):
        if oldPlanetID in self.planets:
            self.planets[oldPlanetID].StopTicking()



    def ScatterOnPlanetCommandCenterDeployedOrRemoved(self, planetID):
        self._UpdateColonyPresence(planetID)
        sm.ScatterEvent('OnPlanetCommandCenterDeployedOrRemoved')




