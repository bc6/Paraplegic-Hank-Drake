import world
import graphicWrappers
import trinity

class WorldClientLight(world.WorldLight):
    __guid__ = 'world.WorldClientLight'

    def IsRenderObjectLoaded(self):
        return getattr(self, 'renderObject', None) is not None



    def GetRenderObject(self):
        if not hasattr(self, 'renderObject'):
            if self.GetLightType() == const.world.BASIC_LIGHT:
                self.renderObject = trinity.Tr2InteriorLightSource()
            elif self.GetLightType() == const.world.BOX_LIGHT:
                self.renderObject = trinity.Tr2InteriorBoxLight()
            graphicWrappers.Wrap(self.renderObject)
            self.Refresh()
        return self.renderObject



    def Refresh(self, fromJessica = False):
        if hasattr(self, 'renderObject'):
            self.renderObject.name = str(self.GetName())
            self.renderObject.SetPosition(self.GetPosition())
            self.renderObject.SetColor(self.GetColor())
            if self.GetLightType() == const.world.BASIC_LIGHT:
                self.renderObject.SetRadius(self.GetRadius())
                self.renderObject.coneDirection = self.GetConeDirection()
                self.renderObject.coneAlphaInner = self.GetConeAlphaInner()
                self.renderObject.coneAlphaOuter = self.GetConeAlphaOuter()
            else:
                self.renderObject.SetRotationYawPitchRoll(self.GetRotation())
                self.renderObject.SetScaling(self.GetScaling())
            self.renderObject.SetFalloff(self.GetFalloff())
            self.renderObject.shadowImportance = self.GetShadowImportance()
            self.renderObject.primaryLighting = self.GetPrimaryLighting()
            self.renderObject.secondaryLighting = self.GetSecondaryLighting()
            self.renderObject.secondaryLightingMultiplier = self.GetSecondaryLightingMultiplier()
            self.renderObject.affectTransparentObjects = self.GetAffectTransparentObjects()
            self.renderObject.shadowResolution = self.GetShadowResolution()
            self.renderObject.shadowCasterTypes = self.GetShadowCasterTypes()
            self.renderObject.projectedTexturePath = self.GetProjectedTexturePath().encode()
            self.renderObject.importanceScale = self.GetImportanceScale()
            self.renderObject.importanceBias = self.GetImportanceBias()
            self.renderObject.enableShadowLOD = self.GetEnableShadowLOD()
            self.renderObject.cellIntersectionType = self.GetCellIntersectionType()
            self.renderObject.useKelvinColor = self.GetUseKelvinColor()
            self.renderObject.kelvinColor.temperature = self.GetKelvinColorTemperature()
            self.renderObject.kelvinColor.tint = self.GetKelvinColorTint()
            self.renderObject.kelvinColor.whiteBalance = self.GetKelvinColorWhiteBalance()
            if not fromJessica:
                self.renderObject.isStatic = self.GetIsStatic()




