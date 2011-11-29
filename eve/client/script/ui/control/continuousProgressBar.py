import xtriui
import uix
import blue
import uiutil
import uicls
import uiconst
import uthread
import math
import mathUtil

class ContinuousProgressBar(uicls.Container):
    __guid__ = 'xtriui.ContinuousProgressBar'

    def init(self):
        self.boxes = []
        self.numBoxes = 20
        self.boxPaddingVertical = 1
        self.boxPaddingHorizontal = 1
        self.knightRiding = False
        self.fadeTime = 1500.0
        self._OnResize()



    def Startup(self, numBoxes = 20, boxColor = None, fadeTime = None, vpad = 1, hpad = 1, *args):
        self.sr.frame = uicls.Frame(parent=self, padding=(-1, -1, -1, -1), color=(0.6, 0.6, 0.6, 1.0), idx=0)
        self.sr.frame.state = uiconst.UI_DISABLED
        self.numBoxes = numBoxes
        self.boxPaddingHorizontal = hpad
        self.boxPaddingVertical = vpad
        if boxColor is None:
            boxColor = (1.0, 0.0, 0.0, 0.95)
        if fadeTime is not None:
            self.fadeTime = fadeTime
        while len(self.boxes) < self.numBoxes:
            self.boxes.append(self.CreateBox(2, 2, boxColor))

        if len(self.boxes) > 0:
            self.boxes[-1].height = 0
            self.boxes[-1].width = 0
            self.boxes[-1].SetAlign(uiconst.TOALL)
        blue.pyos.synchro.Yield()
        self._OnResize()



    def CreateBox(self, height, width, colorTuple):
        newBox = uicls.Container(parent=self, name='progressBox', align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN, pos=(0,
         0,
         height,
         width), padding=(self.boxPaddingHorizontal,
         self.boxPaddingVertical,
         self.boxPaddingHorizontal,
         self.boxPaddingVertical))
        uicls.Fill(parent=newBox, color=colorTuple)
        newBox.opacity = 0.0
        return newBox



    def _OnClose(self, *args):
        self.StopProgress()



    def StartProgress(self):
        self.knightRiding = True
        uthread.new(self._KnightRide)



    def StopProgress(self):
        self.knightRiding = False



    def _KnightRideMotion(self, rideRight):
        numBoxes = float(len(self.boxes))
        negVal = -1.0 + 1.0 / numBoxes
        if rideRight:
            (current, end,) = (1.0, negVal)
        else:
            (current, end,) = (negVal, 1.0)
        (start, ndt,) = (blue.os.GetWallclockTime(), 0.0)
        while ndt != 1.0:
            if not self or self.destroyed or not self.knightRiding:
                break
            ndt = min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / self.fadeTime, 1.0)
            lerpVal = mathUtil.Lerp(current, end, ndt) * math.pi
            for (index, box,) in enumerate(self.boxes):
                box.opacity = min(1.0, max(0.0, math.sin(lerpVal + math.pi * (index / numBoxes)) * 3 - 2))

            blue.pyos.synchro.Yield()




    def _KnightRide(self):
        rideRight = True
        while self and not self.destroyed and self.knightRiding:
            self._KnightRideMotion(rideRight)
            rideRight = not rideRight
            blue.pyos.synchro.Yield()

        if self and not self.destroyed:
            for box in self.boxes:
                box.opacity = 0.0




    def _OnResize(self, *args):
        if len(self.boxes) < 1:
            return 
        (l, t, w, h,) = self.GetAbsolute()
        bw = (w - self.boxPaddingHorizontal * 2 * len(self.boxes)) / len(self.boxes)
        if bw < 2:
            bw = 2
        bh = h - self.boxPaddingVertical * 2
        left = 0
        for box in self.boxes[0:-1]:
            box.height = bh
            box.width = bw





