import world
import graphicWrappers
import trinity

class WorldClientOccluder(world.Occluder):
    __guid__ = 'world.WorldClientOccluder'

    def IsRenderObjectLoaded(self):
        return getattr(self, 'renderObject', None) is not None



    def GetRenderObject(self):
        if not hasattr(self, 'renderObject'):
            self.renderObject = trinity.Tr2InteriorOccluder()
            graphicWrappers.Wrap(self.renderObject)
            self.Refresh()
        return self.renderObject



    def Refresh(self):
        if hasattr(self, 'renderObject'):
            self.renderObject.SetPosition(self.GetPosition())
            self.renderObject.SetRotationYawPitchRoll(self.GetRotation())
            self.renderObject.SetScale(self.GetScale())
            self.renderObject.SetCell(self.GetCellName())




