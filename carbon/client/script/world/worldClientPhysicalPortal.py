import world
import graphicWrappers
import trinity

class WorldClientPhysicalPortal(world.PhysicalPortal):
    __guid__ = 'world.WorldClientPhysicalPortal'

    def IsRenderObjectLoaded(self):
        return getattr(self, 'renderObject', None) is not None



    def GetRenderObject(self):
        if not hasattr(self, 'renderObject'):
            self.renderObject = trinity.Tr2InteriorPhysicalPortal()
            graphicWrappers.Wrap(self.renderObject)
            self.Refresh()
        return self.renderObject



    def Refresh(self):
        if hasattr(self, 'renderObject'):
            self.renderObject.SetPosition(self.GetPosition())
            self.renderObject.SetRotationYawPitchRoll(self.GetRotation())
            self.renderObject.SetScale(self.GetScale())
            self.renderObject.SetName(self.GetName())




