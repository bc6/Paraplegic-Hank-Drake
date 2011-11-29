import geo2
import log
import math
import world
import localization

class WorldSpace(object):
    __guid__ = 'world.WorldSpace'
    LOADING = 1
    NOT_LOADING = 2

    def __init__(self, worldSpaceTypeID, worldSpaceID):
        self.worldSpaceTypeID = worldSpaceTypeID
        self.worldSpaceID = worldSpaceID
        if not hasattr(self, 'mainRow'):
            self.mainRow = cfg.worldspaces.Get(worldSpaceTypeID)
        if not hasattr(self, 'coreInventoryTypeRow'):
            self.coreInventoryTypeRow = cfg.invtypes.Get(worldSpaceTypeID)
        self.boundingBox = (geo2.Vector(0, 0, 0), geo2.Vector(0, 0, 0))
        self.ground = None



    def GetWorldSpaceID(self):
        return self.worldSpaceID



    def GetWorldSpaceTypeID(self):
        return self.worldSpaceTypeID



    def GetName(self):
        if getattr(self.coreInventoryTypeRow, 'typeNameID', None):
            return localization.GetByMessageID(self.coreInventoryTypeRow.typeNameID)
        else:
            return self.coreInventoryTypeRow.typeName



    def GetNameID(self):
        return getattr(self.coreInventoryTypeRow, 'typeNameID', None)



    def GetDescription(self):
        if getattr(self.coreInventoryTypeRow, 'descriptionID', None):
            return localization.GetByMessageID(self.coreInventoryTypeRow.descriptionID)
        else:
            return self.coreInventoryTypeRow.description



    def GetDescriptionID(self):
        return getattr(self.coreInventoryTypeRow, 'descriptionID', None)



    def GetParentWorldSpaceTypeID(self):
        return self.mainRow.parentWorldSpaceTypeID



    def GetSafeSpotPosition(self):
        return (self.mainRow.safeSpotX, self.mainRow.safeSpotY, self.mainRow.safeSpotZ)



    def SetSafeSpotPosition(self, pos):
        (self.mainRow.safeSpotX, self.mainRow.safeSpotY, self.mainRow.safeSpotZ,) = pos



    def GetSafeSpotYaw(self):
        return self.mainRow.safeSpotRotY



    def GetSafeSpotYawDegrees(self):
        return math.degrees(self.GetSafeSpotYaw())



    def GetDistrictID(self):
        row = self.mainRow
        while row and row.districtID is None and row.parentWorldSpaceTypeID is not None:
            row = cfg.worldspaces.Get(row.parentWorldSpaceTypeID)

        if row:
            return row.districtID
        districtlessWorldSpace = self.worldSpaceTypeID
        row = self.mainRow
        while row and row.districtID is None and row.parentWorldSpaceTypeID is not None:
            districtlessWorldSpace = row.parentWorldSpaceTypeID
            row = cfg.worldspaces.Get(row.parentWorldSpaceTypeID)

        log.LogError("WorldSpace doesn't have a parent or a district worldSpaceTypeID: %d" % districtlessWorldSpace)



    def IsInterior(self):
        return self.mainRow.isInterior



    def SetIsInterior(self, isInterior):
        self.mainRow.isInterior = isInterior



    def GetIsUnique(self):
        return self.mainRow.isUnique



    def IsObsolete(self):
        return self.mainRow.obsolete



    def GetSafeSpotTransformMatrix(self):
        rotQuat = geo2.QuaternionRotationSetYawPitchRoll(self.GetSafeSpotYaw(), 0, 0)
        rotMatrix = geo2.MatrixRotationQuaternion(rotQuat)
        rotMatrix = geo2.MatrixInverse(rotMatrix)
        transMatrix = geo2.MatrixTranslation(*self.GetSafeSpotPosition())
        return geo2.MatrixMultiply(rotMatrix, transMatrix)



    def SetIsUnique(self, isUnique):
        self.isUnique = False



worldSpaceCache = {}

def GetWorldSpace(worldSpaceID):
    global worldSpaceCache
    if worldSpaceID is None:
        return 
    ws = worldSpaceCache.get(worldSpaceID, None)
    if ws is None:
        try:
            ws = world.WorldSpace(worldSpaceID, None)
            worldSpaceCache[worldSpaceID] = ws
        except KeyError:
            return 
    return ws



def GetWorldSpaceName(worldSpaceID):
    if worldSpaceID is None:
        return 
    worldSpace = world.GetWorldSpace(worldSpaceID)
    if worldSpace:
        return worldSpace.GetName()


exports = {'world.GetWorldSpace': GetWorldSpace,
 'world.GetWorldSpaceName': GetWorldSpaceName}

