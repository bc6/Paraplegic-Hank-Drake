#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/primitives/transform.py
import uicls
import uiutil
import uiconst
import blue
import math
import log
import trinity

class Transform(uicls.Container):
    __guid__ = 'uicls.Transform'
    __renderObject__ = trinity.Tr2Sprite2dTransform
    __members__ = uicls.Container.__members__ + ['rotation',
     'rotationCenter',
     'scale',
     'scalingCenter',
     'scalingRotation']
    default_align = uiconst.RELATIVE
    default_state = uiconst.UI_PICKCHILDREN
    default_rotation = 0.0
    default_rotationCenter = (0.5, 0.5)
    default_scale = (1, 1)
    default_scalingCenter = (0, 0)
    default_scalingRotation = 0.0

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.rotation = attributes.get('rotation', self.default_rotation)
        self.rotationCenter = attributes.get('rotationCenter', self.default_rotationCenter)
        self.scale = attributes.get('scale', self.default_scale)
        self.scalingCenter = attributes.get('scalingCenter', self.default_scalingCenter)
        self.scalingRotation = attributes.get('scalingRotation', self.default_scalingRotation)

    def SetRotation(self, rotation = 0):
        self.rotation = rotation

    def GetRotation(self):
        return self.rotation

    @apply
    def scale():
        doc = 'Scale amount tuple (scaleX, scaleY).'

        def fget(self):
            return self._scale

        def fset(self, value):
            self._scale = value
            ro = self.renderObject
            if ro:
                ro.scale = value

        return property(**locals())

    @apply
    def scalingCenter():
        doc = 'Scale center tuple (centerX, centerY). (0.5, 0.5) is the middle of the object.'

        def fget(self):
            return self._scalingCenter

        def fset(self, value):
            self._scalingCenter = value
            ro = self.renderObject
            if ro:
                ro.scalingCenter = value

        return property(**locals())

    @apply
    def scalingRotation():
        doc = "Rotation of scaling. This can be used to achieve a shear effect when\n        scaling is not at it's default (1.0, 1.0)."

        def fget(self):
            return self._scalingRotation

        def fset(self, value):
            self._scalingRotation = value
            ro = self.renderObject
            if ro:
                ro.scalingRotation = value

        return property(**locals())

    @apply
    def rotation():
        doc = 'Counter clockwise rotation in radians'

        def fget(self):
            return self._rotation

        def fset(self, value):
            self._rotation = value
            ro = self.renderObject
            if ro:
                ro.rotation = -value

        return property(**locals())

    @apply
    def rotationCenter():
        doc = 'Center of rotation tuple (centerX, centerY). (0.5, 0.5) is default.'

        def fget(self):
            return self._rotationCenter

        def fset(self, value):
            self._rotationCenter = value
            ro = self.renderObject
            if ro:
                ro.rotationCenter = self._rotationCenter

        return property(**locals())

    def StartRotationCycle(self, direction = 1, cycleTime = 1000.0, cycles = None):
        if getattr(self, '_rotateCycle', False):
            self._rotateCycle = False
            blue.pyos.synchro.Yield()
        self._rotateCycle = True
        fullRotation = math.pi * 2
        start = blue.os.GetWallclockTime()
        ndt = 0.0
        current = self.GetRotation()
        while getattr(self, '_rotateCycle', False):
            try:
                ndt = max(ndt, blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / cycleTime)
            except:
                log.LogWarn('StartRotationCycle::Failed getting time diff. Diff should not exceed %s but is %s' % (cycleTime, start - blue.os.GetWallclockTimeNow()))
                ndt = 1.0

            self.SetRotation(current - fullRotation * ndt * direction)
            blue.pyos.synchro.Yield()
            if self.destroyed:
                return
            if cycles is not None and cycles <= int(ndt):
                return

    def Rotate(self, delta):
        newRotation = self.ClampRotation(self.rotation + delta)
        self.rotation = newRotation

    def ClampRotation(self, rotation):
        if rotation > math.pi * 2:
            rotation -= math.pi * 2
        elif rotation < 0:
            rotation += math.pi * 2
        return rotation

    def StopRotationCycle(self):
        self._rotateCycle = False