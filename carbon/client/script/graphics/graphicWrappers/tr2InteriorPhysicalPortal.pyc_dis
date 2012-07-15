#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/graphicWrappers/tr2InteriorPhysicalPortal.py
import geo2
import trinity
import util
import weakref

class Tr2InteriorPhysicalPortal(util.BlueClassNotifyWrap('trinity.Tr2InteriorPhysicalPortal')):
    __guid__ = 'graphicWrappers.Tr2InteriorPhysicalPortal'

    @staticmethod
    def Wrap(triObject, resPath):
        Tr2InteriorPhysicalPortal(triObject)
        triObject.AddNotify('position', triObject._TransformChange)
        triObject.AddNotify('rotation', triObject._TransformChange)
        triObject.AddNotify('maxBounds', triObject._TransformChange)
        triObject.AddNotify('minBounds', triObject._TransformChange)
        triObject.scene = None
        return triObject

    def AddToScene(self, scene):
        scene.AddPhysicalPortal(self)
        self.scene = weakref.ref(scene)

    def RemoveFromScene(self, scene):
        scene.RemovePhysicalPortal(self)
        self.scene = None

    def _TransformChange(self, transform):
        self.OnTransformChange()

    def OnTransformChange(self):
        pass

    def GetPosition(self):
        return self.position

    def SetPosition(self, pos):
        self.position = pos

    def GetRotationYawPitchRoll(self):
        return geo2.QuaternionRotationGetYawPitchRoll(self.rotation)

    def SetRotationYawPitchRoll(self, ypr):
        self.rotation = geo2.QuaternionRotationSetYawPitchRoll(*ypr)

    def GetScale(self):
        return (self.maxBounds[0], self.maxBounds[1], self.maxBounds[2])

    def SetScale(self, scale):
        self.maxBounds = scale
        self.minBounds = (-scale[0], -scale[1], -scale[2])

    def GetName(self):
        return self.name

    def SetName(self, name):
        self.name = str(name)

    def GetBoundingBoxInLocalSpace(self):
        min = trinity.TriVector(*self.minBounds)
        max = trinity.TriVector(*self.maxBounds)
        return (min, max)