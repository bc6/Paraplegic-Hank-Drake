import util
import world
import bluepy
import log
import graphicWrappers
import trinity
import device

class WorldSpaceClientObject(world.WorldSpaceObject):
    __guid__ = 'world.WorldSpaceClientObject'

    def __init__(self, *args, **kwargs):
        world.WorldSpaceObject.__init__(self, *args, **kwargs)
        self.renderObject = None



    def IsRenderObjectLoaded(self):
        return self.renderObject is not None



    def GetRenderObject(self):
        if not self.renderObject:
            modelPath = self.GetModelResFilePath()
            if modelPath is None:
                log.LogError('No model path for worldSpaceID %d objectID %d' % (self.GetWorldSpaceTypeID(), self.GetObjectID()))
            elif prefs.ini.HasKey('noModels') and prefs.noModels.lower() == 'true':
                self.renderObject = graphicWrappers.LoadAndWrap(const.BAD_ASSET_PATH_AND_FILE)
            else:
                device.SetEnvMipLevelSkipCount()
                self.renderObject = graphicWrappers.LoadAndWrap(modelPath)
            if not self.renderObject:
                self.renderObject = graphicWrappers.LoadAndWrap(const.BAD_ASSET_PATH_AND_FILE)
                print '!!! WARNING !!! Asset (',
                print modelPath,
                print ') is missing !!! WARNING !!!'
            self.renderObject.objectID = self.GetID()
            self.Refresh()
        self.renderObject.name = str(self.GetName())
        return self.renderObject



    def Refresh(self):
        if self.renderObject:
            self.renderObject.SetPosition(self.GetPosition())
            self.renderObject.SetRotationYawPitchRoll(self.GetRotation())
            self.renderObject.SetScale(self.GetScale())
            if hasattr(self.renderObject, 'SetCell'):
                self.renderObject.SetCell(str(self.GetCellID()))
            if hasattr(self.renderObject, 'SetSystem'):
                self.renderObject.SetSystem(str(self.GetSystemID()))



    def AttachLightOverride(self, lightID):
        self.GetRenderObject()
        if hasattr(self.renderObject, 'lightSources') and len(self.renderObject.lightSources) >= lightID:
            lightRender = self.renderObject.lightSources[(lightID - 1)]
            bluepy.WrapBlueClass(lightRender)
            lightOverride = self.lightOverrides[lightID]
            for (key, value,) in const.world.LIGHT_OVERRIDE_ATTRS.iteritems():
                attrValue = getattr(lightOverride, 'Get' + value)()
                if attrValue is not None:
                    setattr(lightRender, key, attrValue)
                    setattr(lightRender, 'override_' + key, True)




    def AttachEnlightenArea(self, areaName):
        self.GetRenderObject()
        if hasattr(self.renderObject, 'enlightenAreas'):
            for area in self.renderObject.enlightenAreas:
                if areaName == area.name:
                    bluepy.WrapBlueClass(area)
                    enlightenAreaOverride = self.enlightenAreas[areaName]
                    area.name = str(enlightenAreaOverride.GetAreaName())
                    area.isEmissive = enlightenAreaOverride.GetIsEmissive()
                    area.albedoColor = enlightenAreaOverride.GetAlbedoColor()
                    area.emissiveColor = enlightenAreaOverride.GetEmissiveColor()





