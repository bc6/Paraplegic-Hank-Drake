
class WorldLight(object):
    __guid__ = 'world.WorldLight'

    def __init__(self, mainRow):
        self.worldSpaceTypeID = mainRow.worldSpaceTypeID
        self.lightID = mainRow.lightID
        self.mainRow = mainRow



    def GetWorldSpaceTypeID(self):
        return self.worldSpaceTypeID



    def GetID(self):
        return self.lightID



    def GetLightID(self):
        return self.GetID()



    def GetGroupID(self):
        return self.mainRow.groupID



    def GetPrefabLightID(self):
        return self.mainRow.prefabLightID



    def GetName(self):
        return self.mainRow.lightName



    def GetPosition(self):
        return (self.mainRow.posX, self.mainRow.posY, self.mainRow.posZ)



    def GetRotation(self):
        return (self.mainRow.pitch if self.mainRow.pitch is not None else 0.0, self.mainRow.yaw if self.mainRow.yaw is not None else 0.0, self.mainRow.roll if self.mainRow.roll is not None else 0.0)



    def GetScaling(self):
        return (self.mainRow.scaleX, self.mainRow.scaleY, self.mainRow.scaleZ)



    def GetRadius(self):
        return self.mainRow.radius



    def GetFalloff(self):
        return self.mainRow.falloff



    def GetConeAlphaInner(self):
        return self.mainRow.coneAlphaInner



    def GetConeAlphaOuter(self):
        return self.mainRow.coneAlphaOuter



    def GetConeDirection(self):
        return (self.mainRow.coneDirectionX, self.mainRow.coneDirectionY, self.mainRow.coneDirectionZ)



    def GetColor(self):
        return (self.mainRow.red,
         self.mainRow.green,
         self.mainRow.blue,
         1.0)


    color = property(GetColor)

    def GetIsStatic(self):
        return self.mainRow.isStatic



    def GetIsDynamic(self):
        return not self.mainRow.isStatic


    isDynamic = property(GetIsDynamic)

    def GetShadowImportance(self):
        return self.mainRow.shadowImportance



    def GetPrimaryLighting(self):
        return self.mainRow.primaryLighting



    def GetSecondaryLighting(self):
        return self.mainRow.secondaryLighting



    def GetSecondaryLightingMultiplier(self):
        return self.mainRow.secondaryLightingMultiplier



    def GetAffectTransparentObjects(self):
        return self.mainRow.affectTransparentObjects



    def GetShadowResolution(self):
        return self.mainRow.shadowResolution



    def GetShadowCasterTypes(self):
        return self.mainRow.shadowCasterTypes



    def GetProjectedTexturePath(self):
        return self.mainRow.projectedTexturePath



    def GetLightType(self):
        return self.mainRow.lightType



    def GetImportanceScale(self):
        return self.mainRow.importanceScale



    def GetImportanceBias(self):
        return self.mainRow.importanceBias



    def GetEnableShadowLOD(self):
        return self.mainRow.enableShadowLOD



    def GetCellIntersectionType(self):
        return self.mainRow.cellIntersectionType



    def GetUseKelvinColor(self):
        return self.mainRow.useKelvinColor



    def GetKelvinColorTemperature(self):
        return self.mainRow.kelvinColorTemperature



    def GetKelvinColorTint(self):
        return self.mainRow.kelvinColorTint



    def GetKelvinColorWhiteBalance(self):
        return self.mainRow.kelvinColorWhiteBalance



    def GetPerformanceLevel(self):
        return self.mainRow.performanceLevel



    def IsSpotLight(self):
        return self.mainRow.coneAlphaOuter < 89.0




