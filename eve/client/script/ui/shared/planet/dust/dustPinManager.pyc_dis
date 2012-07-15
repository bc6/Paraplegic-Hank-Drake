#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/planet/dust/dustPinManager.py
import util
import planet
import service
import moniker
import blue
import planetSurfaceCommon
import eveDustCommon.planetSurface
from collections import defaultdict, namedtuple
from service import ROLE_GML
DUST_PIN_CACHE_TIMEOUT = 5 * MIN
PlanetData = namedtuple('PlanetData', ['timestamp', 'pins'])

class PlanetBaseService(service.Service):
    __guid__ = 'svc.planetBaseSvc'
    __notifyevents__ = []
    __exportedcalls__ = {}
    __servicename__ = 'planetBaseSvc'
    __displayname__ = 'Planet Base Client Service'
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.dustPinCache = {}
        service.Service.Run(self, memStream)

    def _InvalidateCache(self, planetID):
        if planetID in self.dustPinCache:
            del self.dustPinCache[planetID]
            sm.ScatterEvent('OnRefreshPins', None)

    def GetPlanetBases(self, planetID):
        if planetID in self.dustPinCache and self.dustPinCache[planetID].timestamp + DUST_PIN_CACHE_TIMEOUT < blue.os.GetWallclockTime():
            del self.dustPinCache[planetID]
        if planetID not in self.dustPinCache:
            planetBaseManager = moniker.GetPlanetBaseManager(planetID)
            bases = planetBaseManager.GetCapsuleerBases()
            self.dustPinCache[planetID] = PlanetData(timestamp=blue.os.GetWallclockTime(), pins=bases)
        return self.dustPinCache[planetID].pins

    def AddPlanetBase(self, planetID, typeID, surfacePoint):
        validPlanetTypes = planetSurfaceCommon.GetValidPlanetTypesForPinType(typeID)
        planetData = sm.GetService('map').GetPlanetInfo(planetID)
        if planetData is None:
            raise RuntimeError('Invalid planetID, unable to get map data')
        if validPlanetTypes is not None and planetData.typeID not in validPlanetTypes:
            raise UserError('CannotPlacePinInvalidPlanetType')
        if session.solarsystemid and session.solarsystemid == planetData.solarSystemID:
            orbitals = sm.GetService('planetInfo').GetOrbitalsForPlanet(planetID, const.groupPlanetaryCustomsOffices)
            ballpark = sm.GetService('michelle').GetBallpark()
            orbitalsByType = defaultdict(list)
            for orbitalID in orbitals:
                orbitalSlimItem = ballpark.GetInvItem(orbitalID)
                if orbitalSlimItem is None:
                    self.LogWarn('AddPlanetBase::Unable to find slimItem for', orbitalID)
                    continue
                orbitalsByType[orbitalSlimItem.typeID].append(orbitalSlimItem)

            orbitalPrerequisite = planetSurfaceCommon.GetOrbitalConstructionPrerequisites(typeID)
            for prerequisiteTypeID in orbitalPrerequisite:
                if prerequisiteTypeID not in orbitalsByType:
                    raise UserError('CannotCreateBaseMissingPrerequisite', {'pinType': (TYPEID, typeID),
                     'missingTypeName': (TYPEID, prerequisiteTypeID)})
                else:
                    for orbitalItem in orbitalsByType[prerequisiteTypeID]:
                        if orbitalItem.ownerID == session.corpid:
                            break
                    else:
                        raise UserError('CannotCreateBaseMissingPrerequisite', {'pinType': (TYPEID, typeID),
                         'missingTypeName': (TYPEID, prerequisiteTypeID)})

        existingBases = self.GetPlanetBases(planetID)
        basesByType = defaultdict(int)
        for base, customInfo in existingBases:
            basesByType[base.typeID] += 1

        maxInstances = planetSurfaceCommon.GetMaximumPinInstances(typeID)
        if basesByType[typeID] >= maxInstances:
            raise UserError('CannotPlacePinMaximumInstancesReached', {'typeName': cfg.invtypes.Get(typeID).typeName,
             'maxInstances': maxInstances})
        for requiredTypeID in planetSurfaceCommon.GetSurfaceConstructionPrerequisites(typeID):
            if requiredTypeID not in basesByType:
                raise UserError('CannotCreateBaseMissingPrerequisite', {'pinType': cfg.invtypes.Get(typeID).typeName,
                 'missingTypeName': cfg.invtypes.Get(requiredTypeID).typeName})

        planetBaseManager = moniker.GetPlanetBaseManager(planetID)
        try:
            pinItem = planetBaseManager.AddCapsuleerBase(typeID, surfacePoint.phi, surfacePoint.theta)
        except UserError as e:
            self._InvalidateCache(planetID)
            raise e

        existingBases.append((pinItem, util.KeyVal(latitude=surfacePoint.phi, longitude=surfacePoint.theta, conflicts=[])))
        return pinItem

    def RemovePlanetBase(self, planetID, itemID):
        existingBases = self.GetPlanetBases(planetID)
        baseExists = False
        for base, customInfo in existingBases:
            if itemID == base.itemID:
                baseExists = True
                break

        if not baseExists:
            raise UserError('CannotRemoveDustPinNotPresent')
        planetBaseManager = moniker.GetPlanetBaseManager(planetID)
        try:
            planetBaseManager.RemoveCapsuleerBase(itemID)
        finally:
            self._InvalidateCache(planetID)

    def AttackPlanetBase(self, planetID, itemID):
        planetBaseManager = moniker.GetPlanetBaseManager(planetID)
        battle = planetBaseManager.AttackBase(itemID)
        if planetID in self.dustPinCache:
            for baseItem, customInfo in self.dustPinCache[planetID].pins:
                if baseItem.itemID == itemID:
                    customInfo.conflicts.append(battle)

    def UpdatePlanetOwnership(self, planetID, pinID):
        pass


class DustPinManager:
    __guid__ = 'planet.ui.DustPinManager'
    __notifyevents__ = ['OnPlanetPinsChanged',
     'OnRefreshPins',
     'OnEditModeBuiltOrDestroyed',
     'OnPlanetPinPlaced']

    def __init__(self):
        sm.RegisterNotify(self)
        self.buildIndicatorPin = None
        self.buildNextPinTypeID = None
        self.pins = {}
        self.selectedPin = None

    def Close(self):
        sm.UnregisterNotify(self)
        self.buildIndicatorPin = None
        self.buildNextPinTypeID = None
        self.pins = None
        self.selectedPin = None

    def OnPlanetViewOpened(self):
        self.planetUISvc = sm.GetService('planetUI')
        self.eventManager = self.planetUISvc.eventManager
        self.RenderPins()

    def OnPlanetViewClosed(self):
        pass

    def OnPlanetZoomChanged(self, zoom):
        pass

    def OnRefreshPins(self, pinIDs = None):
        if pinIDs is None:
            pinIDs = self.pins.keys()
        for pinID in pinIDs:
            if pinID in self.pins:
                self.pins[pinID].Remove()
                del self.pins[pinID]

        self.RenderPins()

    def RenderPins(self):
        planetBases = sm.GetService('planetBaseSvc').GetPlanetBases(self.planetUISvc.planetID)
        for item, customInfo in planetBases:
            surfacePoint = planet.SurfacePoint(phi=customInfo.latitude, theta=customInfo.longitude)
            pinKv = util.KeyVal()
            pinKv.typeID = item.typeID
            pinKv.id = item.itemID
            pinKv.ownerID = item.ownerID
            pinKv.conflicts = customInfo.conflicts
            pinKv.surfacePoint = surfacePoint
            self.RenderPin(pinKv, surfacePoint)

    def RemovePin(self, pinID):
        if pinID in self.pins:
            if eveDustCommon.planetSurface.GetConflictState(self.pins[pinID].pinKv.conflicts) != const.objectiveStateCeasefire:
                raise UserError('CustomNotify', {'notify': '!__ You cannot terminate a contested ground objective! Resolve the battle first you limp-dicked cockbite!'})
            sm.GetService('planetBaseSvc').RemovePlanetBase(self.planetUISvc.planetID, pinID)
            self.pins[pinID].Remove()
            del self.pins[pinID]

    def AttackPin(self, pinID):
        if pinID in self.pins:
            sm.GetService('planetBaseSvc').AttackPlanetBase(self.planetUISvc.planetID, pinID)
            self.pins[pinID].Remove()
            del self.pins[pinID]
            self.RenderPins()

    def AddPin(self, typeID, surfacePoint):
        pinItem = sm.GetService('planetBaseSvc').AddPlanetBase(self.planetUISvc.planetID, typeID, surfacePoint)
        pinKv = util.KeyVal()
        pinKv.typeID = typeID
        pinKv.id = pinItem.itemID
        pinKv.ownerID = pinItem.ownerID
        pinKv.surfacePoint = surfacePoint
        pinKv.conflicts = []
        self.RenderPin(pinKv, surfacePoint)

    def RenderPin(self, pinKv, surfacePoint):
        if pinKv.id not in self.pins:
            pin = planet.ui.PlanetBase(surfacePoint, pinKv, self.planetUISvc.pinTransform)
            pin.SetLocation(surfacePoint)
            self.pins[pinKv.id] = pin

    def PlacePinOnNextClick(self, typeID):
        self.buildNextPinTypeID = typeID
        self.eventManager.PlacePinOnNextClick()

    def MoveIndicatorPin(self, surfacePoint):
        if surfacePoint is None:
            return
        if self.buildIndicatorPin is None:
            self.buildIndicatorPin = planet.ui.DustBuildIndicatorPin(surfacePoint, 2, 2, self.planetUISvc.pinTransform)
        self.buildIndicatorPin.SetLocation(surfacePoint)

    def PlacePin(self, surfacePoint):
        self.CancelPinPlacement()
        self.AddPin(self.buildNextPinTypeID, surfacePoint)

    def CancelPinPlacement(self):
        if self.buildIndicatorPin is not None:
            self.buildIndicatorPin.Remove()
            self.buildIndicatorPin = None
        self.eventManager.SetNormalState()

    def GetPinMenu(self, pinID):
        if pinID in self.pins:
            pin = self.pins[pinID]
            menu = pin.GetMenu()
            if session.role & ROLE_GML == ROLE_GML:
                menu.append(['GM/Debug Menu...', pin.GetGMMenu()])
            return menu
        return []

    def PinSelected(self, pinID):
        if self.selectedPin is not None:
            if self.selectedPin.pinKv.id == pinID:
                return
            self.PinUnselected()
        if pinID in self.pins:
            self.selectedPin = self.pins[pinID]
            self.selectedPin.Selected()

    def PinUnselected(self):
        if self.selectedPin is not None:
            self.selectedPin.Unselected()
            self.selectedPin = None

    def UpdatePlanetControl(self):
        baseManager = moniker.GetPlanetBaseManager(self.planetUISvc.planetID)
        baseManager.TriggerOwnershipChange()

    def GMUpdateControl(self, newOwnerID):
        baseManager = moniker.GetPlanetBaseManager(self.planetUISvc.planetID)
        baseManager.GMOwnershipChange(newOwnerID)