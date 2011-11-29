import planet
import planetCommon
import blue
import blue.heapq as heapq
import util
import weakref
import math
import localization

class ClientColony(planet.BaseColony):
    __guid__ = 'planet.ClientColony'
    __name__ = 'ClientColony'

    def Init(self):
        planet.BaseColony.Init(self)
        self.nextTemporaryPinID = 0
        self.nextTemporaryRouteID = 0
        self.cumulativePinCreationCost = 0L
        self.cumulativeUpgradeCost = 0L



    def ResetPinCreationCost(self):
        self.cumulativePinCreationCost = 0L
        self.cumulativeUpgradeCost = 0L



    def RemoveCreationCost(self, typeID):
        self.cumulativePinCreationCost -= cfg.invtypes.Get(typeID).basePrice
        if self.cumulativePinCreationCost < 0:
            self.cumulativePinCreationCost = 0L



    def GetTemporaryPinID(self):
        self.nextTemporaryPinID += 1
        return (1, self.nextTemporaryPinID)



    def GetTemporaryRouteID(self):
        self.nextTemporaryRouteID += 1
        return (2, self.nextTemporaryRouteID)



    def GetLinksAttachedToPin(self, pinID):
        if pinID not in self.linksByPin:
            return []
        return self.linksByPin[pinID]



    def SetColonyData(self, newData):
        planet.BaseColony.SetColonyData(self, newData)



    def PostValidateCreatePin(self, charID, typeID, latitude, longitude):
        typeObj = cfg.invtypes.Get(typeID)
        if typeObj.groupID != const.groupCommandPins:
            totalIskCost = self.cumulativePinCreationCost + typeObj.basePrice
            currentBalance = sm.GetService('wallet').GetWealth()
            if totalIskCost > currentBalance:
                raise UserError('CannotBuildNotEnoughCash', {'cost': util.FmtISK(typeObj.basePrice)})
            self.cumulativePinCreationCost += typeObj.basePrice
        else:
            planetRows = sm.GetService('planetSvc').GetMyPlanets()
            if len(planetRows) > 0 and sm.GetService('skills').HasSkill(const.typeOmnipotent) is None:
                deploymentSkill = sm.GetService('skills').HasSkill(const.typeInterplanetaryConsolidation)
                if deploymentSkill is None:
                    raise UserError('CannotPlaceCommandCenterNotEnoughSkill', {'maxPlanets': 1})
                elif deploymentSkill.skillLevel < len(planetRows):
                    raise UserError('CannotPlaceCommandCenterNotEnoughSkill', {'maxPlanets': len(planetRows)})
            sovInfo = sm.GetService('sov').GetSystemSovereigntyInfo(self.planet.solarSystemID)
            allianceID = sovInfo.allianceID if sovInfo else None
            if allianceID is not None and allianceID != session.allianceid:
                raise UserError('SovPreventsCommandPin')
        requiredSkills = sm.GetService('info').GetRequiredSkills(typeID)
        lackingSkills = []
        for (skillTypeID, level,) in requiredSkills:
            myLevel = sm.GetService('skills').HasSkill(skillTypeID)
            if myLevel is None or myLevel.skillLevel < level:
                if level:
                    levelTxt = localization.GetByLabel('UI/PI/Common/SkillLevel', skillLevel=level)
                else:
                    levelTxt = ''
                lacked = localization.GetByLabel('UI/PI/Common/SkillNameAndLevel', skillName=cfg.invtypes.Get(skillTypeID).name, skillLevel=levelTxt)
                lackingSkills.append(lacked)

        if len(lackingSkills) > 0:
            raise UserError('CannotPlacePinNotEnoughSkill', {'requiredSkills': ', '.join(lackingSkills),
             'itemName': cfg.invtypes.Get(typeID).name})



    def PostValidateRemovePin(self, charID, pinID):
        pin = self.GetPin(pinID)
        typeObj = cfg.invtypes.Get(pin.typeID)
        if typeObj.groupID == const.groupExtractorPins:
            self.cumulativePinCreationCost -= typeObj.basePrice



    def PostValidateCommandCenterUpgrade(self, level):
        skill = sm.GetService('skills').GetMySkillsFromTypeID(const.typeCommandCenterUpgrade)
        skillLevel = None
        if skill is not None:
            skillLevel = skill.skillLevel
        if level > skillLevel:
            raise UserError('CantUpgradeCommandCenterSkillRequired', {'skillName': (TYPEID, const.typeCommandCenterUpgrade),
             'currentLevel': skillLevel,
             'requestedLevel': level})
        cost = planetCommon.GetUpgradeCost(self.colonyData.level, level)
        self.cumulativeUpgradeCost += cost



    def PostValidateInstallProgram(self, pinID, typeID, headRadius):
        pin = self.GetPin(pinID)
        if not pin.inEditMode:
            currentTime = blue.os.GetWallclockTime()
            pin.CanInstallProgram(currentTime)



    def ValidateAddExtractorHead(self, pinID, headID):
        if self.colonyData is None:
            raise RuntimeError('Unable to validate new extractor head - no colony data')
        pin = self.GetPin(pinID)
        if not pin:
            raise UserError('PinDoesNotExist')
        if not pin.IsExtractor():
            raise UserError('PinDoesNotHaveHeads')
        if pin.FindHead(headID) is not None:
            raise UserError('CannotAddHeadAlreadyExists')
        if len(pin.heads) > planetCommon.ECU_MAX_HEADS:
            raise UserError('CannotPlaceHeadLimitReached')
        cpuDelta = pin.GetCpuUsage(numHeads=len(pin.heads) + 1) - pin.GetCpuUsage()
        powerDelta = pin.GetPowerUsage(numHeads=len(pin.heads) + 1) - pin.GetPowerUsage()
        if cpuDelta + self.colonyData.GetColonyCpuUsage() > self.colonyData.GetColonyCpuSupply():
            raise UserError('CannotAddToColonyCPUUsageExceeded', {'typeName': localization.GetByLabel('UI/PI/Common/ExtractorHead')})
        if powerDelta + self.colonyData.GetColonyPowerUsage() > self.colonyData.GetColonyPowerSupply():
            raise UserError('CannotAddToColonyPowerUsageExceeded', {'typeName': localization.GetByLabel('UI/PI/Common/ExtractorHead')})



    def OnPinRemoved(self, pinID):
        planet.BaseColony.OnPinRemoved(self, pinID)



    def GetTypeAttribute(self, typeID, attributeID):
        return sm.GetService('godma').GetTypeAttribute2(typeID, attributeID)



    def Dijkstra(self, sourcePin, destinationPin):
        D = {}
        P = {}
        Q = planetCommon.priority_dict()
        Q[sourcePin] = 0.0
        while len(Q) > 0:
            vPin = Q.smallest()
            D[vPin] = Q[vPin]
            if vPin == destinationPin:
                break
            Q.pop_smallest()
            for wDestinationID in self.colonyData.GetLinksForPin(vPin.id):
                wLink = self.GetLink(vPin.id, wDestinationID)
                wPin = self.GetPin(wDestinationID)
                vwLength = D[vPin] + self._GetLinkWeight(wLink, wPin, vPin)
                if wPin in D:
                    if vwLength < D[wPin]:
                        raise ValueError, 'Dijkstra: found better path to already-final vertex'
                elif wPin not in Q or vwLength < Q[wPin]:
                    Q[wPin] = vwLength
                    P[wPin] = vPin


        return (D, P)



    def _GetLinkWeight(self, link, pinA, pinB):
        spA = planet.SurfacePoint(radius=1.0, theta=pinA.longitude, phi=pinA.latitude)
        spB = planet.SurfacePoint(radius=1.0, theta=pinB.longitude, phi=pinB.latitude)
        return spA.GetDistanceToOther(spB)



    def FindShortestPath(self, sourcePin, destinationPin):
        if sourcePin is None or destinationPin is None:
            return 
        if sourcePin == destinationPin:
            return []
        (distanceDict, predecessorDict,) = self.Dijkstra(sourcePin, destinationPin)
        if destinationPin not in distanceDict or destinationPin not in predecessorDict:
            return []
        path = []
        currentPin = destinationPin
        while currentPin is not None:
            path.append(currentPin.id)
            if currentPin is sourcePin:
                break
            if currentPin not in predecessorDict:
                raise RuntimeError("CurrentPin not in predecessor dict. There's no path. How did we get here?!")
            currentPin = predecessorDict[currentPin]

        path.reverse()
        if path[0] != sourcePin.id:
            return []
        return path



    def FindShortestPathIDs(self, sourcePinID, destinationPinID):
        return self.FindShortestPath(self.GetPin(sourcePinID), self.GetPin(destinationPinID))




