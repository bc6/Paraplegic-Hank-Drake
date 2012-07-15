#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\slprofile.py
import profile
import stackless
import sys
import blue
import time
import traceback
import thread
import functools
import log
stackless.globaltrace = True

class Profile(profile.Profile):
    base = profile.Profile

    def __init__(self, timer = None, bias = None):
        self.current_tasklet = stackless.getcurrent()
        self.thread_id = thread.get_ident()
        if timer is None:
            timer = Timer()
        self.base.__init__(self, timer, bias)
        self.sleeping = {}

    def __call__(self, *args):
        r = self.dispatcher(*args)

    def _setup(self):
        self.cur, self.timings, self.current_tasklet = None, {}, stackless.getcurrent()
        self.thread_id = thread.get_ident()
        self.simulate_call('profiler')

    def start(self, name = 'start'):
        if getattr(self, 'running', False):
            return
        self._setup()
        self.simulate_call('start')
        self.running = True
        sys.setprofile(self.dispatcher)

    def stop(self):
        sys.setprofile(None)
        self.running = False
        self.TallyTimings()

    def runctx(self, cmd, globals, locals):
        self._setup()
        try:
            profile.Profile.runctx(self, cmd, globals, locals)
        finally:
            self.TallyTimings()

    def runcall(self, func, *args, **kw):
        self._setup()
        try:
            profile.Profile.runcall(self, func, *args, **kw)
        finally:
            self.TallyTimings()

    def trace_dispatch_return_extend_back(self, frame, t):
        if isinstance(self.cur[-2], Profile.fake_frame):
            return False
            self.trace_dispatch_call(frame, 0)
        return self.trace_dispatch_return(frame, t)

    def trace_dispatch_c_return_extend_back(self, frame, t):
        if isinstance(self.cur[-2], Profile.fake_frame):
            return False
            self.trace_dispatch_c_call(frame, 0)
        return self.trace_dispatch_return(frame, t)

    dispatch = dict(profile.Profile.dispatch)
    dispatch.update({'return': trace_dispatch_return_extend_back,
     'c_return': trace_dispatch_c_return_extend_back})

    def SwitchTasklet(self, t0, t1, t):
        pt, it, et, fn, frame, rcur = self.cur
        cur = (pt,
         it + t,
         et,
         fn,
         frame,
         rcur)
        self.sleeping[t0] = (cur, self.timings)
        self.current_tasklet = t1
        try:
            self.cur, self.timings = self.sleeping.pop(t1)
        except KeyError:
            self.cur, self.timings = None, {}
            self.simulate_call('profiler')
            self.simulate_call('new_tasklet')

    def ContextWrap(f):

        @functools.wraps(f)
        def ContextWrapper(self, arg, t):
            current = stackless.getcurrent()
            if current != self.current_tasklet:
                self.SwitchTasklet(self.current_tasklet, current, t)
                t = 0.0
            return f(self, arg, t)

        return ContextWrapper

    dispatch = dict([ (key, ContextWrap(val)) for key, val in dispatch.iteritems() ])

    def TallyTimings(self):
        oldtimings = self.sleeping
        self.sleeping = {}
        self.cur = self.Unwind(self.cur, self.timings)
        for tasklet, (cur, timings) in oldtimings.iteritems():
            self.Unwind(cur, timings)
            for k, v in timings.iteritems():
                if k not in self.timings:
                    self.timings[k] = v
                else:
                    cc, ns, tt, ct, callers = self.timings[k]
                    cc += v[0]
                    tt += v[2]
                    ct += v[3]
                    for k1, v1 in v[4].iteritems():
                        callers[k1] = callers.get(k1, 0) + v1

                    self.timings[k] = (cc,
                     ns,
                     tt,
                     ct,
                     callers)

    def Unwind(self, cur, timings):
        while cur[-1]:
            rpt, rit, ret, rfn, frame, rcur = cur
            frame_total = rit + ret
            if rfn in timings:
                cc, ns, tt, ct, callers = timings[rfn]
            else:
                cc, ns, tt, ct, callers = (0,
                 0,
                 0,
                 0,
                 {})
            if not ns:
                ct = ct + frame_total
                cc = cc + 1
            if rcur:
                ppt, pit, pet, pfn, pframe, pcur = rcur
            else:
                pfn = None
            if pfn in callers:
                callers[pfn] = callers[pfn] + 1
            elif pfn:
                callers[pfn] = 1
            timings[rfn] = (cc,
             ns - 1,
             tt + rit,
             ct,
             callers)
            ppt, pit, pet, pfn, pframe, pcur = rcur
            rcur = (ppt,
             pit + rpt,
             pet + frame_total,
             pfn,
             pframe,
             pcur)
            cur = rcur

        return cur


class Timer(object):

    def __init__(self):
        self.startTime = blue.os.GetWallclockTimeNow()

    def __call__(self):
        return float(blue.os.GetWallclockTimeNow() - self.startTime) * 1e-07