from __future__ import with_statement
import log
import sys
import blue
import uthread
import bluepy
import weakref
import traceback
import functools
import const
import stackless
globals()['ClockThis'] = sys.ClockThis
globals()['ClockThisWithoutTheStars'] = sys.ClockThisWithoutTheStars

def TimeThis(timer):

    def Helper(func):

        @functools.wraps(func)
        def Wrapper(*args, **kwds):
            t = bluepy.PushTimer(timer)
            try:
                return func(*args, **kwds)

            finally:
                bluepy.PopTimer(t)



        return Wrapper


    return Helper



class SimpleTimingContext(object):

    def __enter__(self):
        c = stackless.getcurrent()
        self.t = (c.GetWallclockTime(), c.GetRunTime())



    def __exit__(self, exc_type, exc_value, exc_tb):
        (a, b,) = self.t
        c = stackless.getcurrent()
        self.t = (c.GetWallclockTime() - a, c.GetRunTime() - b)



    def GetWallclockTime(self):
        return self.t[0]



    def GetRunTime(self):
        return self.t[1]




class TracebackTimingContext(SimpleTimingContext):

    def __init__(self, runtime = 1.0, wallclock = None):
        (self.wallclock, self.runtime,) = (wallclock, runtime)



    def __exit__(self, exc_type, exc_val, exc_tb):
        SimpleTimingContext.__exit__(self, exc_type, exc_val, exc_tb)
        if self.wallclock is not None and self.GetWallclockTime() > self.wallclock or self.runtime is not None and self.GetRunTime() > self.runtime:
            log.LogTraceback('TracebackTimingContext exceeded: wallclock=%s, runtime=%s' % (self.GetWallclockTime(), self.GetRunTime()))




def TracebackTimingFunction(runtime = 1.0, wallclock = None):

    def decorator(f):

        @functools.wraps(f)
        def wrapper(*args, **kwds):
            with TracebackTimingContext(runtime=runtime, wallclock=wallclock):
                return f(*args, **kwds)


        return wrapper


    return decorator



class TimerObject:
    __guid__ = 'base.TimerObject'

    def __init__(self):
        self.abort = 0
        self.id = 0
        self.aborts = {}



    def __del__(self):
        self.abort = 1



    def DelayedCall(self, func, time, *args, **kw):
        self.id += 1
        callID = self.id
        if time - blue.os.GetTime() > const.DAY:
            raise RuntimeError('Cannot sleep for more than 24 hours')
        uthread.new(self.DelayedCall_thread, callID, func, time, args, kw)
        return callID



    def DelayedCall_thread(self, callID, func, time, args, kw):
        delay = (time - blue.os.GetTime()) / 10000
        if delay > 0:
            blue.pyos.synchro.Sleep(delay)
        if callID in self.aborts:
            del self.aborts[callID]
        elif not self.abort:
            try:
                func(*args, **kw)
            except:
                log.LogException('Error in delayed call')



    def KillDelayedCall(self, id):
        self.aborts[id] = None



    def KillAllDelayedCalls(self):
        self.abort = 1




def OnTimerResync(old, new):
    diff = new - old
    for timer in AutoTimer.autoTimers.keys():
        timer.wakeupAt += diff / 10000




class AutoTimer(object):
    __guid__ = 'base.AutoTimer'
    autoTimers = weakref.WeakKeyDictionary()
    blue.pyos.synchro.timesyncs.append(OnTimerResync)

    def __init__(self, interval, method, *args, **kw):
        self.run = 1
        self.interval = interval
        (self.method, self.args, self.kw,) = (method, args, kw)
        caller_tb = traceback.extract_stack(limit=2)[0:1]
        caller = traceback.format_list(caller_tb)[0].replace('\n', '')
        methrepr = getattr(method, '__name__', '(no __name__)').replace('<', '&lt;').replace('>', '&gt;')
        ctx = 'AutoTimer::(%s) on %s' % (caller, methrepr)
        self.wakeupAt = blue.os.GetTime() / 10000 + self.interval
        AutoTimer.autoTimers[self] = None
        uthread.pool(ctx, AutoTimer.Loop, weakref.ref(self))



    def KillTimer(self):
        self.run = 0



    def Reset(self, newInterval = None):
        if newInterval is not None:
            self.interval = newInterval
        self.wakeupAt = blue.os.GetTime() / 10000 + self.interval



    def Loop(weakSelf):
        self = weakSelf()
        if not self or not self.run:
            return 
        nap = self.interval
        del self
        while True:
            blue.pyos.synchro.Sleep(nap)
            self = weakSelf()
            if not self or not self.run:
                return 
            now = blue.os.GetTime() / 10000
            if now < self.wakeupAt:
                nap = self.wakeupAt - now
            else:
                self.method(*self.args, **self.kw)
                n = (now - self.wakeupAt) / self.interval
                self.wakeupAt += (n + 1) * self.interval
                nap = self.wakeupAt - now
            del self



    Loop = staticmethod(Loop)


def AutoTimerTest():
    print 'fewbar'



class Stopwatch:

    def __init__(self):
        self.started = blue.os.GetCycles()[0]



    def __str__(self):
        return '%.3f' % ((blue.os.GetCycles()[0] - self.started) / float(blue.os.GetCycles()[1]))



    def Reset(self):
        self.started = blue.os.GetCycles()[0]



exports = {'base.AutoTimerTest': AutoTimerTest,
 'timerstuff.ClockThis': ClockThis,
 'timerstuff.ClockThisWithoutTheStars': ClockThisWithoutTheStars,
 'util.Stopwatch': Stopwatch,
 'timerstuff.TimeThis': TimeThis,
 'timerstuff.SimpleTimingContext': SimpleTimingContext,
 'timerstuff.TracebackTimingContext': TracebackTimingContext,
 'timerstuff.TracebackTimingFunction': TracebackTimingFunction}

