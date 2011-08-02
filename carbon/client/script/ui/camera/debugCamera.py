import cameras

class DebugCamera(cameras.WorldspaceCamera):
    __guid__ = 'cameras.DebugCamera'

    def OnMouseMove(self, deltaX, deltaY):
        if self.mouseLeftButtonDown or self.mouseRightButtonDown:
            self.AdjustYaw(deltaX * 0.005)
            self.AdjustPitch(deltaY * 0.005)




