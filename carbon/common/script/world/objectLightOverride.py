
class ObjectLightOverride(object):
    __guid__ = 'world.ObjectLightOverride'

    def __init__(self, worldSpaceTypeID, objectID, lightID, row):
        self.worldSpaceTypeID = worldSpaceTypeID
        self.objectID = objectID
        self.lightID = lightID
        self.mainRow = row



    def GetWorldSpaceTypeID(self):
        return self.worldSpaceTypeID



    def GetObjectID(self):
        return self.objectID



    def GetLightID(self):
        return self.lightID



    def GetRadius(self):
        return self.mainRow.radius



    def GetSpecularRadiusMultiplier(self):
        return self.mainRow.specularRadiusMultiplier



    def GetPointLight(self):
        return self.mainRow.pointLight



    def GetSpotlightConeAngle(self):
        return self.mainRow.spotlightConeAngle



    def GetDistanceFalloffKneeValue(self):
        return self.mainRow.distanceFalloffKneeValue



    def GetDistanceFalloffKneeRadius(self):
        return self.mainRow.distanceFalloffKneeRadius



    def GetColor(self):
        if self.mainRow.colorR is None or self.mainRow.colorG is None or self.mainRow.colorB is None or self.mainRow.colorA is None:
            return 
        return (self.mainRow.colorR,
         self.mainRow.colorG,
         self.mainRow.colorB,
         self.mainRow.colorA)



    def GetDirection(self):
        if self.mainRow.directionX is None or self.mainRow.directionY is None or self.mainRow.directionZ is None:
            return 
        return (self.mainRow.directionX, self.mainRow.directionY, self.mainRow.directionZ)




