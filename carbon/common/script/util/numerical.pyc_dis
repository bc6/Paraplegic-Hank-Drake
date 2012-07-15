#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/numerical.py
import linalg

class KalmanFilter(object):
    __slots__ = ['A',
     'B',
     'B1',
     'C',
     'M',
     'q']

    def __init__(self, A, B, B1, C):
        self.A, self.B, self.B1, self.C = (A,
         B,
         B1,
         C)
        self.M = linalg.Matrix.I(A.dim[0])
        self.q = linalg.Matrix.Ones((A.dim[0], 1))

    def NextG(self, Rv, Rw):
        G = self.M * self.C.Trans() / (self.C * self.M * self.C.Trans() + Rv)
        P = self.M - G * self.C * self.M
        self.M = self.A * P * self.A.Trans() + self.B1 * Rw * self.B1.Trans()
        return G

    def StepG(self, y, u, G):
        if self.B:
            qbar = self.A * self.q + self.B * u
        else:
            qbar = self.A * self.q
        self.q = qbar + G * (y - self.C * qbar)
        return self.q

    def Step(self, y, u, Rv, Rw):
        return self.StepG(y, u, self.NextG(Rv, Rw))


class KalmanFilterSS(KalmanFilter):
    __slots__ = ['G']

    def __init__(self, A, B, B1, C, Rv, Rw, n = 100, f = 0.001):
        KalmanFilter.__init__(self, A, B, B1, C)
        self.G = self.SteadyG(Rv, Rw, n)

    def SteadyG(self, Rv, Rw, n = 100, f = 0.001):
        self.G = self.NextG(Rv, Rw)
        for i in xrange(n):
            old = self.G
            self.G = self.NextG(Rv, Rw)
            d = old - self.G
            if abs(d) <= f * abs(self.G):
                break

        return self.G

    def Step(self, y, u):
        return self.StepG(y, u, self.G)


import blue

class FrameClock(object):
    __slots__ = ['factor',
     'threshold',
     'filter',
     't0',
     'lastTime',
     'value',
     'step']

    def __init__(self):
        A = linalg.Matrix((2, 2), [1.0,
         1.0,
         0.0,
         1.0])
        B = None
        B1 = linalg.Matrix((2, 1), [1.0, 1.0])
        C = linalg.Matrix((1, 2), [1.0, 0.0])
        self.factor = prefs.GetValue('frameClockFactor', 100000.0)
        self.threshold = prefs.GetValue('frameClockThreshold', 1.0)
        self.threshold = long(self.threshold * 10000000.0)
        self.filter = KalmanFilterSS(A, B, B1, C, self.factor, 1.0)
        self.t0 = blue.os.GetWallclockTimeNow()
        self.lastTime = 0L
        self.step = 0
        self.filter.q[0] = 0.0
        self.filter.q[1] = 1.0 / 50

    def Rebase(self, t = None):
        self.t0 = t or blue.os.GetWallclockTimeNow()
        self.filter.q[0] = 0.0
        self.lastTime = self.t0

    def Sample(self):
        rt = blue.os.GetWallclockTimeNow()
        t = (rt - self.t0) * 1e-07
        q = self.filter.Step(t, None)
        self.step += 1
        t = self.t0 + long(q[0] * 10000000.0)
        if self.step < 20:
            t = rt
        elif rt - t > self.threshold:
            t = rt
            self.Rebase(rt)
        if t < self.lastTime:
            t = self.lastTime
        self.lastTime = t
        self.value = (t, 1.0 / q[1])
        return self.value

    def SetFactor(self, factor):
        self.factor = factor
        self.filter.SteadyG(self.factor, 1.0)

    def GetFactor(self):
        return self.factor


exports = {'numerical.KalmanFilter': KalmanFilter,
 'numerical.KalmanFilterSS': KalmanFilterSS,
 'numerical.FrameClock': FrameClock}