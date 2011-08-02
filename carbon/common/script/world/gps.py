import GameWorld
import miscUtil
import service
import world
import geo2

class GPS(service.Service):
    __guid__ = 'svc.gps'

    def __init__(self, *args, **kwargs):
        self.worldSpaceSvc = None
        self.worldSpacePortalDistances = {}
        service.Service.__init__(self, *args, **kwargs)



    def Run(self, *etc):
        self.worldSpaceSvc = sm.GetService('worldSpace' + boot.role.title())
        self.gameWorldService = sm.GetService('gameWorld' + boot.role.title())
        self.entityService = sm.GetService('entity' + boot.role.title())
        self.GPS = self.gameWorldService.GetGameWorldManager().gps



    def LoadPathCostsForWorldSpace(self, worldSpaceID):
        return 
        if worldSpaceID not in self.worldSpacePortalDistances:
            filePath = const.world.PATHING_FOLDER + 'worldSpace_' + str(worldSpaceID) + '/'
            filePath += const.world.PATHING_DATA_FILE
            pathData = world.BaseWorldSpaceService.LoadPathingDataFile(filePath)
            if pathData is not None:
                self.worldSpacePortalDistances[worldSpaceID] = pathData['portalCosts']



    def UnloadPathCostsForWorldSpace(self, worldSpaceID):
        if worldSpaceID in self.worldSpacePortalDistances:
            del self.worldSpacePortalDistances[worldSpaceID]



    def AddPortal(self, instanceID, portalID, toInstanceID, toPortalID, pos, aabb, transform):
        worldSpaceTypeID = self.worldSpaceSvc.GetWorldSpaceTypeIDFromWorldSpaceID(instanceID)
        if worldSpaceTypeID in self.worldSpacePortalDistances:
            worldDistances = self.worldSpacePortalDistances[worldSpaceTypeID]
            if portalID in worldDistances:
                portalDistances = worldDistances[portalID]
            else:
                portalDistances = {}
        else:
            portalDistances = {}
        self.GPS.AddPortal(long(instanceID), portalID, long(toInstanceID), toPortalID, pos, aabb, transform, portalDistances)



    def ConvertCoordinate(self, instanceID, pos, toInstanceID):
        return self.GPS.ConvertCoordinateToInstance(instanceID, pos, toInstanceID)



    def ConvertCoordinateToConnectedInstances(self, instanceID, pos, maxDist = -1.0):
        return self.GPS.ConvertCoordinateToConnectedInstances(instanceID, pos, maxDist)



    def GetDistancesToConnectedInstances(self, instanceID, pos, maxDist = -1.0):
        return self.GPS.GetDistanceToConnectedInstances(instanceID, pos, maxDist)



    def _ConvertCoordinate(self, instanceID, point, toInstanceID = None):
        if toInstanceID is None:
            return point
        return self.ConvertCoordinate(instanceID, point, toInstanceID)



    def GetEntityDistanceFromPoint(self, entity, point, instanceID = None):
        if instanceID:
            point = self._ConvertCoordinate(instanceID, point, entity.scene.sceneID)
            if point is None:
                return 
        return geo2.Vec3Distance(point, entity.GetComponent('position').position)



    def GetEntityDistanceSquaredFromPoint(self, entity, point, instanceID = None):
        if instanceID:
            point = self._ConvertCoordinate(instanceID, point, entity.scene.sceneID)
            if point is None:
                return 
        return geo2.Vec3DistanceSq(point, entity.GetComponent('position').position)



    def GetEntityDistanceSquaredFromPoint2D(self, entity, point, instanceID = None):
        if instanceID:
            point = self._ConvertCoordinate(instanceID, point, entity.scene.sceneID)
            if point is None:
                return 
        point = (point[0], entity.GetComponent('position').position[1], point[2])
        return self.GetEntityDistanceSquaredFromPoint(entity, point)



    def GetEntityDistanceToEntity(self, entity, otherEntity):
        otherPos = self._ConvertCoordinate(otherEntity.scene.sceneID, otherEntity.GetComponent('position').position, entity.scene.sceneID)
        if otherPos is None:
            return 
        return self.GetEntityDistanceFromPoint(entity, otherPos)



    def GetEntityDistanceSquaredToEntity(self, entity, otherEntity):
        otherPos = self._ConvertCoordinate(otherEntity.scene.sceneID, otherEntity.GetComponent('position').position, entity.scene.sceneID)
        if otherPos is None:
            return 
        return self.GetEntityDistanceSquaredFromPoint(entity, otherPos)



    def DistanceBetweenEntitiesLessThan(self, entity, otherEntity, dist):
        distToEnt = self.GetEntityDistanceToEntity(entity, otherEntity)
        if distToEnt is None:
            return False
        return distToEnt < dist



    def EntityDistanceFromPointLessThan(self, entity, point, dist, instanceID = None):
        d = self.GetEntityDistanceFromPoint(entity, point, instanceID)
        if d is None:
            return False
        return d < dist



    def EntityDistanceFromPointLessThanOrEq(self, entity, point, dist, instanceID = None):
        d = self.GetEntityDistanceFromPoint(entity, point, instanceID)
        if d is None:
            return False
        return d <= dist



    def EntityDistanceFromPointLessThanOrEq2D(self, entity, point, dist, instanceID = None):
        d = self.GetEntityDistanceSquaredFromPoint2D(entity, point, instanceID)
        if d is None:
            return False
        dist = dist * dist
        return d <= dist




