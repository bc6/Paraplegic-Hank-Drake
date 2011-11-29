import graphicWrappers
import trinity
import util
import weakref
import blue

class Tr2InteriorStatic(util.BlueClassNotifyWrap('trinity.Tr2InteriorStatic'), graphicWrappers.TrinityTranslationRotationMixinWrapper):
    __guid__ = 'graphicWrappers.Tr2InteriorStatic'

    @staticmethod
    def Wrap(triObject, resPath):
        Tr2InteriorStatic(triObject)
        triObject.AddNotify('worldPosition', triObject._PositionChange)
        triObject.AddNotify('rotation', triObject._RotationChange)
        triObject.cellName = '0'
        triObject.systemName = 0
        triObject.scene = None
        triObject.resPath = resPath
        return triObject



    def SetCell(self, cellName):
        if self.cellName != cellName:
            self.cellName = cellName
            if self.scene and self.scene():
                self.AddToScene(self.scene())



    def SetSystem(self, systemName):
        if self.systemName != systemName:
            self.systemName = systemName
            if self.scene and self.scene():
                self.AddToScene(self.scene())



    def AddToScene(self, scene):
        if self.scene and self.scene():
            self.RemoveFromScene(scene)
        scene.AddStatic(self, self.cellName, self.systemName)
        self.scene = weakref.ref(scene)
        blue.resMan.Wait()
        self.BindLowLevelShaders()



    def RemoveFromScene(self, scene):
        scene.RemoveStatic(self)
        self.scene = None



    def OnTransformChange(self):
        pass



    def _PositionChange(self, pos):
        self.OnPositionChange()



    def OnPositionChange(self):
        pass



    def _RotationChange(self, rot):
        self.OnRotationChange()



    def OnRotationChange(self):
        pass



    def OnScaleChange(self):
        pass



    def GetBoundingBoxInLocalSpace(self):
        if self.geometry.meshCount > 0:
            (min, max,) = self.geometry.GetBoundingBox(0)
            for i in xrange(self.geometry.meshCount - 1):
                (cMin, cMax,) = self.geometry.GetBoundingBox(i + 1)
                min.Minimize(cMin)
                max.Maximize(cMax)

            return (min, max)
        return (trinity.TriVector(), trinity.TriVector())



    def IsLoading(self):
        for area in self.enlightenAreas:
            if util.IsAreaLoading(area):
                return True

        for mesh in self.detailMeshes:
            if util.IsTr2MeshLoading(mesh):
                return True

        return False




