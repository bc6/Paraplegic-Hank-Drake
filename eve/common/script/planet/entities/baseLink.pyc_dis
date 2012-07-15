#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/planet/entities/baseLink.py
import planet
import weakref
import const
import util
import planetCommon
import math

class BaseLink(object):
    __guid__ = 'planet.BaseLink'
    __name__ = 'BaseLink'
    __slots__ = ['eventHandler',
     'typeID',
     'endpoint1',
     'endpoint2',
     'routesTransiting',
     'level',
     'bandwidthUsage',
     'editModeLink']

    def __init__(self, eventHandler, typeID, endpointPin1, endpointPin2, level = 0):
        if not isinstance(eventHandler, weakref.ProxyType) and eventHandler is not None:
            self.eventHandler = weakref.proxy(eventHandler)
        else:
            self.eventHandler = eventHandler
        self.typeID = typeID
        if cfg.invtypes.Get(typeID).groupID != const.groupPlanetaryLinks:
            raise RuntimeError('Link created with invalid type ID', typeID)
        if endpointPin1 is None or endpointPin2 is None:
            raise RuntimeError('Link created with invalid endpoints', endpointPin1, endpointPin2)
        if endpointPin1.id > endpointPin2.id:
            raise RuntimeError('Data Integrity Error: Endpoint 1 must have pin ID lower than Endpoint 2', endpointPin1.id, endpointPin2.id)
        self.endpoint1 = weakref.proxy(endpointPin1)
        self.endpoint2 = weakref.proxy(endpointPin2)
        self.routesTransiting = []
        self.SetLinkLevel(level)
        self.bandwidthUsage = 0.0
        self.editModeLink = False

    def __str__(self):
        return 'PI Link [%s]-[%s]' % (self.endpoint1.id, self.endpoint2.id)

    def CanRouteBandwidth(self, additionalLoad):
        if self.bandwidthUsage + additionalLoad > self.GetTotalBandwidth():
            return False
        return True

    def IsEditModeLink(self):
        return getattr(self, 'editModeLink', False)

    def AddRoute(self, routeObj):
        if routeObj is None:
            raise RuntimeError('Adding invalid route object', routeObj)
        self.bandwidthUsage += routeObj.GetBandwidthUsage()
        self.routesTransiting.append(routeObj.routeID)

    def RemoveRoute(self, routeID):
        if routeID in self.routesTransiting:
            self.routesTransiting.remove(routeID)
        self.bandwidthUsage = 0.0
        for routeID in self.routesTransiting:
            route = self.eventHandler.GetRoute(routeID)
            if route:
                self.bandwidthUsage += route.GetBandwidthUsage()

    def GetDestination(self, sourcePinID):
        if self.endpoint1.id == sourcePinID:
            return self.endpoint2.id
        if self.endpoint2.id == sourcePinID:
            return self.endpoint1.id
        raise RuntimeError('Queried link', self.endpoint1.id, '<==>', self.endpoint2.id, 'for destination from pin', sourcePinID)

    def HasEndpoint(self, endpointID):
        return self.endpoint1.id == endpointID or self.endpoint2.id == endpointID

    def Serialize(self):
        data = util.KeyVal(typeID=self.typeID, endpoint1=self.endpoint1.id, endpoint2=self.endpoint2.id, level=self.level)
        return data

    def GetOtherPin(self, pinID):
        if pinID == self.endpoint1.id:
            return self.endpoint2
        else:
            return self.endpoint1

    def GetDistance(self):
        planetRadius = self.eventHandler.GetPlanetRadius()
        spA = planet.SurfacePoint(radius=planetRadius, theta=self.endpoint1.longitude, phi=self.endpoint1.latitude)
        spB = planet.SurfacePoint(radius=planetRadius, theta=self.endpoint2.longitude, phi=self.endpoint2.latitude)
        return spA.GetDistanceToOther(spB)

    def GetBandwidthUsage(self):
        return self.bandwidthUsage

    def GetTotalBandwidth(self):
        return self.GetBandwidthForLevel(self.level)

    def GetBaseBandwidth(self):
        return self.eventHandler.GetTypeAttribute(self.typeID, const.attributeLogisticalCapacity)

    def SetLinkLevel(self, level):
        self.level = level

    def GetBandwidthForLevel(self, level):
        return self.GetBaseBandwidth() * 2.0 ** level

    def GetCpuUsage(self, params = None):
        return planetCommon.GetCpuUsageForLink(self.typeID, self.GetDistance(), self.level, params=params)

    def GetPowerUsage(self, params = None):
        return planetCommon.GetPowerUsageForLink(self.typeID, self.GetDistance(), self.level, params=params)