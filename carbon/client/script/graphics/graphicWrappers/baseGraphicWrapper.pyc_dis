#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/graphicWrappers/baseGraphicWrapper.py
import geo2

class BaseGraphicWrapper(object):
    __guid__ = 'graphicWrappers.BaseWrapper'

    @staticmethod
    def Wrap(triObject):
        raise RuntimeError('Not Implemented')

    def AddToScene(self, scene):
        raise RuntimeError('Not Implemented')

    def RemoveFromScene(self, scene):
        raise RuntimeError('Not Implemented')

    def GetPosition(self):
        raise RuntimeError('Not Implemented')

    def SetPosition(self, pos):
        raise RuntimeError('Not Implemented')

    def GetRotationYawPitchRoll(self):
        raise RuntimeError('Not Implemented')

    def SetRotationYawPitchRoll(self, rot):
        raise RuntimeError('Not Implemented')

    def GetScale(self):
        raise RuntimeError('Not Implemented')

    def SetScale(self, scale):
        raise RuntimeError('Not Implemented')

    def OnChange(self):
        raise RuntimeError('Not Implemented')


import mathCommon
import util

class TrinityTransformMatrixMixinWrapper(object):
    __guid__ = 'graphicWrappers.TrinityTransformMatrixMixinWrapper'

    def InitTransformMatrixMixinWrapper(self):
        pos, rot, scale = mathCommon.DecomposeMatrix(self.transform)
        self._worldPosition = pos
        self._scale = scale
        self._rot = geo2.QuaternionRotationSetYawPitchRoll(*rot)

    def GetPosition(self):
        return self._worldPosition

    def SetPosition(self, pos):
        self._worldPosition = pos
        self._RefreshTransformMatrix()
        if not hasattr(self, 'IsNotifyEnabled') or self.IsNotifyEnabled():
            self.OnPositionChange()

    def GetRotation(self):
        return self._rot

    def SetRotation(self, rot):
        self._rot = rot
        self._RefreshTransformMatrix()
        if not hasattr(self, 'IsNotifyEnabled') or self.IsNotifyEnabled():
            self.OnRotationChange()

    def GetRotationYawPitchRoll(self):
        return geo2.QuaternionRotationGetYawPitchRoll(self._rot)

    def SetRotationYawPitchRoll(self, rot):
        self._rot = geo2.QuaternionRotationSetYawPitchRoll(*rot)
        self._RefreshTransformMatrix()
        if not hasattr(self, 'IsNotifyEnabled') or self.IsNotifyEnabled():
            self.OnRotationChange()

    def GetScale(self):
        return self._scale

    def SetScale(self, scale):
        self._scale = scale
        self._RefreshTransformMatrix()
        if not hasattr(self, 'IsNotifyEnabled') or self.IsNotifyEnabled():
            self.OnScaleChange()

    def _RefreshTransformMatrix(self):
        wasNotified = False
        if hasattr(self, 'IsNotifyEnabled') and self.IsNotifyEnabled():
            self.DisableNotify()
            wasNotified = True
        transform = mathCommon.ComposeMatrix(self.GetPosition(), self.GetRotation(), self.GetScale())
        if type(self.transform) == tuple:
            self.transform = transform
        else:
            self.transform = util.ConvertTupleToTriMatrix(transform)
        if wasNotified:
            self.EnableNotify()


class TrinityTranslationRotationMixinWrapper(object):
    __guid__ = 'graphicWrappers.TrinityTranslationRotationMixinWrapper'

    def GetPosition(self):
        return self.worldPosition

    def SetPosition(self, pos):
        self.worldPosition = pos
        if not hasattr(self, 'IsNotifyEnabled') or self.IsNotifyEnabled():
            self.OnPositionChange()

    def GetRotationYawPitchRoll(self):
        return geo2.QuaternionRotationGetYawPitchRoll(self.rotation)

    def SetRotationYawPitchRoll(self, rot):
        self.rotation = geo2.QuaternionRotationSetYawPitchRoll(*rot)
        if not hasattr(self, 'IsNotifyEnabled') or self.IsNotifyEnabled():
            self.OnRotationChange()

    def GetScale(self):
        return (1.0, 1.0, 1.0)

    def SetScale(self, scale):
        pass


class TrinityTranslationRotationScaleMixinWrapper(object):
    __guid__ = 'graphicWrappers.TrinityTranslationRotationScaleMixinWrapper'

    def GetPosition(self):
        return self.worldPosition

    def SetPosition(self, pos):
        self.worldPosition = pos
        if not hasattr(self, 'IsNotifyEnabled') or self.IsNotifyEnabled():
            self.OnPositionChange()

    def GetRotationYawPitchRoll(self):
        return geo2.QuaternionRotationGetYawPitchRoll(self.rotation)

    def SetRotationYawPitchRoll(self, rot):
        self.rotation = geo2.QuaternionRotationSetYawPitchRoll(*rot)
        if not hasattr(self, 'IsNotifyEnabled') or self.IsNotifyEnabled():
            self.OnRotationChange()

    def GetScale(self):
        return self.scaling

    def SetScale(self, scale):
        self.scaling = scale
        if not hasattr(self, 'IsNotifyEnabled') or self.IsNotifyEnabled():
            self.OnScaleChange()