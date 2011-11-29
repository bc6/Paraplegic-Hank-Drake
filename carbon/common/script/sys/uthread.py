from __future__ import with_statement
__version__ = '0.1'
__license__ = 'Python Microthread Library version 0.1\nCopyright (C)2000  Will Ware, Christian Tismer\n\nPermission to use, copy, modify, and distribute this software and its\ndocumentation for any purpose and without fee is hereby granted,\nprovided that the above copyright notice appear in all copies and that\nboth that copyright notice and this permission notice appear in\nsupporting documentation, and that the names of the authors not be\nused in advertising or publicity pertaining to distribution of the\nsoftware without specific, written prior permission.\n\nWILL WARE AND CHRISTIAN TISMER DISCLAIM ALL WARRANTIES WITH REGARD TO\nTHIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND\nFITNESS. IN NO EVENT SHALL WILL WARE OR CHRISTIAN TISMER BE LIABLE FOR\nANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES\nWHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN\nACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT\nOF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.'
import stackless
import sys
import blue
import bluepy
import types
import weakref
import traceback
import log
import copy
import contextlib
import re
import blue.heapq as heapq
import locks
import threading
from stacklesslib.util import atomic
SEC = 10000000L
MIN = 60 * SEC
tasks = []
schedule = stackless.schedule
stackless.globaltrace = True
ctxtfilter = re.compile('at 0x[0-9A-F]+')

def new(func, *args, **kw):
    ctx = ctxtfilter.sub('at (snip)', repr(func))
    ctx = blue.pyos.taskletTimer.GetCurrent().split('^')[-1] + '^' + ctx
    t = bluepy.TaskletExt(ctx, func)
    t(*args, **kw)
    return t


idIndex = 0

def uniqueId():
    global idIndex
    z = idIndex
    idIndex += 1
    return z



def irandom(n):
    import random
    n = random.randrange(0, n)
    return n


semaphores = weakref.WeakKeyDictionary()

def GetSemaphores():
    return semaphores



class Semaphore:
    __guid__ = 'uthread.Semaphore'

    def __init__(self, semaphoreName = None, maxcount = 1, strict = True):
        self.semaphoreName = semaphoreName
        self.maxcount = maxcount
        self.count = maxcount
        self.waiting = stackless.channel()
        self.waiting.preference = 0
        self.thread = None
        self.lockedWhen = None
        self.strict = strict
        locks.Register(self)



    def IsCool(self):
        return self.count == self.maxcount



    def __repr__(self):
        return '<Semaphore %r, t:%f at %#x>' % (self.semaphoreName, self.LockedFor(), id(self))



    def __del__(self):
        if not self.IsCool():
            log.general.Log("Semaphore '" + str(self.semaphoreName) + "' is being destroyed in a locked or waiting state", 4, 0)



    def acquire(self):
        if self.strict:
            if self.thread is stackless.getcurrent():
                raise RuntimeError, 'tasklet deadlock, acquiring tasklet holds strict semaphore'
        self.count -= 1
        if self.count < 0:
            self.waiting.receive()
        else:
            self.lockedWhen = blue.os.GetWallclockTime()
            self.thread = stackless.getcurrent()


    claim = acquire

    def release(self, override = False):
        if self.strict and not override:
            if self.thread is not stackless.getcurrent():
                raise RuntimeError, 'wrong tasklet releasing strict semaphore'
        self.count += 1
        self.thread = None
        self.lockedWhen = None
        if self.count <= 0:
            self.lockedWhen = blue.os.GetWallclockTime()
            self.thread = self.waiting.queue
            self.waiting.send(None)



    def __enter__(self):
        self.acquire()



    def __exit__(self, exc, val, tb):
        self.release()



    def WaitingTasklets(self):
        r = []
        first = next = self.waiting.queue
        while next:
            r.append(next)
            next = next.next
            if next == first:
                break

        return r



    def HoldingTasklets(self):
        if self.thread:
            return [self.thread]
        return []



    def LockedAt(self):
        return self.lockedWhen



    def LockedFor(self):
        if self.lockedWhen:
            return (blue.os.GetWallclockTime() - self.lockedWhen) * 1e-07
        else:
            return -1.0




class CriticalSection(Semaphore):
    __guid__ = 'uthread.CriticalSection'

    def __init__(self, semaphoreName = None, strict = True):
        Semaphore.__init__(self, semaphoreName)
        self._CriticalSection__reentrantRefs = 0



    def __repr__(self):
        return '<CriticalSection %r, t:%f at %#x>' % (self.semaphoreName, self.LockedFor(), id(self))



    def acquire(self):
        if self.count <= 0 and (self.thread is stackless.getcurrent() or locks.Inherits(self.thread)):
            self._CriticalSection__reentrantRefs += 1
        else:
            Semaphore.acquire(self)



    def release(self):
        if self._CriticalSection__reentrantRefs:
            if not (self.thread is stackless.getcurrent() or locks.Inherits(self.thread)):
                raise RuntimeError, 'wrong tasklet releasing reentrant CriticalSection'
            self._CriticalSection__reentrantRefs -= 1
        else:
            Semaphore.release(self)




def FNext(f):
    first = stackless.getcurrent()
    try:
        cursor = first.next
        while cursor != first:
            if cursor.frame.f_back == f:
                return FNext(cursor.frame)
            cursor = cursor.next

        return f

    finally:
        first = None
        cursor = None




class RWLock(object):
    __guid__ = 'uthread.RWLock'

    def __init__(self, lockName = ''):
        self.name = lockName
        self.rchan = stackless.channel()
        self.wchan = stackless.channel()
        self.rchan.preference = self.wchan.preference = 0
        self.state = 0
        self.tasklets = []
        self.lockedWhen = None
        locks.Register(self)



    def __repr__(self):
        return '<RWLock %r, state:%d, rdwait:%d, wrwait:%d, t:%f at %#x>' % (self.name,
         self.state,
         -self.rchan.balance,
         -self.wchan.balance,
         self.LockedFor(),
         id(self))



    def RDLock(self):
        if not self.TryRDLock():
            self.rchan.receive()



    def TryRDLock(self):
        if self.state >= 0:
            if self.wchan.balance == 0 or stackless.getcurrent() in self.tasklets:
                self.state += 1
                self._AddTasklet()
                return True
            return False
        else:
            return self.TryWRLock()



    def WRLock(self):
        if not self.TryWRLock():
            if stackless.getcurrent() in self.tasklets:
                raise RuntimeError('Deadlock. Trying to WRLock while holding a RDLock')
            self.wchan.receive()



    def TryWRLock(self):
        if self.state == 0 or self.state < 0 and stackless.getcurrent() == self.tasklets[0]:
            self.state -= 1
            self._AddTasklet()
            return True
        return False



    def Unlock(self, tasklet = None):
        if tasklet is None:
            tasklet = stackless.getcurrent()
        try:
            self.tasklets.remove(tasklet)
        except ValueError:
            raise RuntimeError('Trying to release a rwlock without a matching lock!')
        if self.state > 0:
            self.state -= 1
        else:
            self.state += 1
        if self.state == 0:
            self.lockedWhen = None
        self._Pump()



    def _AddTasklet(self, tasklet = None):
        if not tasklet:
            tasklet = stackless.getcurrent()
        self.tasklets.append(tasklet)
        if not self.lockedWhen:
            self.lockedWhen = blue.os.GetWallclockTime()



    def _Pump(self):
        while True:
            chan = self.wchan
            if chan.balance:
                if self.state == 0:
                    self.state = -1
                    self._AddTasklet(chan.queue)
                    chan.send(None)
                    return 
            else:
                chan = self.rchan
                if chan.balance and self.state >= 0:
                    self.state += 1
                    self._AddTasklet(chan.queue)
                    chan.send(None)
                    continue
            return 




    def __enter__(self):
        self.RDLock()



    def __exit__(self, e, v, tb):
        self.Unlock()



    class WRCtxt(object):

        def __init__(self, lock):
            self.lock = lock



        def __enter__(self):
            self.lock.WRLock()



        def __exit__(self, e, v, tb):
            self.lock.Unlock()




    def WRLocked(self):
        return self.WRCtxt(self)



    def RDLocked(self):
        return self



    def IsCool(self):
        return self.state == 0



    @property
    def thread(self):
        if self.tasklets:
            return self.tasklets[0]



    def WaitingTasklets(self):
        r = []
        for chan in (self.rchan, self.wchan):
            first = t = chan.queue
            while t:
                r.append(t)
                t = t.next
                if t is first:
                    break


        return r



    def HoldingTasklets(self):
        return list(self.tasklets)



    def LockedAt(self):
        return self.lockedWhen



    def IsWRLocked(self):
        return self.state < 0



    def IsRDLocked(self):
        return self.state > 0



    def LockedFor(self):
        if self.lockedWhen:
            return (blue.os.GetWallclockTime() - self.lockedWhen) * 1e-07
        else:
            return -1.0



channels = weakref.WeakKeyDictionary()

def GetChannels():
    global channels
    return channels



class Channel(stackless.channel):
    __guid__ = 'uthread.Channel'

    def __new__(cls, channelName = None):
        return stackless.channel.__new__(cls)



    def __init__(self, channelName = None):
        stackless.channel.__init__(self)
        self.channelName = channelName
        channels[self] = 1




class FIFO(object):
    __slots__ = ('data',)

    def __init__(self):
        self.data = [[], []]



    def push(self, v):
        self.data[1].append(v)



    def pop(self):
        d = self.data
        if not d[0]:
            d.reverse()
            d[0].reverse()
        return d[0].pop()



    def front(self):
        d = self.data
        if d[0]:
            return d[0][-1]
        return d[1][0]



    def __contains__(self, o):
        d = self.data
        return o in d[0] or o in d[1]



    def __len__(self):
        d = self.data
        return len(d[0]) + len(d[1])



    def clear(self):
        self.data = [[], []]



    def remove(self, o):
        d = self.data
        if d[0]:
            d[0].reverse()
            d[1] = d[0] + d[1]
            d[0] = []
        d[1].remove(o)




class Queue(FIFO):
    __guid__ = 'uthread.Queue'
    __slots__ = 'chan'

    def __init__(self, preference = 0):
        FIFO.__init__(self)
        self.chan = stackless.channel()
        self.chan.preference = preference



    def put(self, x):
        if self.chan.balance < 0:
            self.chan.send(x)
        else:
            self.push(x)


    non_blocking_put = put

    def get(self):
        if len(self):
            return self.pop()
        else:
            return self.chan.receive()




def LockCheck():
    while 1:
        each = None
        blue.pyos.synchro.SleepWallclock(60660)
        now = blue.os.GetWallclockTime()
        try:
            for each in locks.GetLocks():
                if each.LockedAt() and each.WaitingTasklets():
                    problem = now - each.LockedAt()
                    if problem >= 1 * MIN:
                        break
            else:
                problem = 0

            if not problem:
                continue
            with log.general.open(log.LGERR) as s:
                print >> s, 'Locks have been held for a long time (%ss). Locking conflict log' % (problem / SEC)
                foundCycles = locks.LockCycleReport(out=s, timeLimit=60)
                if not foundCycles:
                    print >> s, 'logical analysis found no cycles.'
                if not foundCycles:
                    print >> s, 'Full dump of locks with waiting tasklets:'
                    locks.OldLockReport(None, out=s)
                print >> s, 'End of locking conflict log'
        except StandardError:
            log.LogException()
            sys.exc_clear()




def PoolWorker(ctx, func, *args, **keywords):
    return PoolWithoutTheStars(ctx, func, args, keywords, True)



def PoolWorkerWithoutTheStars(ctx, func, args, keywords):
    return PoolWithoutTheStars(ctx, func, args, keywords, True)



def PoolWithoutTheStars(ctx, func, args, kw, notls = False):
    if not ctx:
        ctx = ctxtfilter.sub('at (snip)', repr(func))
    if ctx[0] != '^':
        prefix = blue.pyos.taskletTimer.GetCurrent().split('^')[-1]
        ctx = prefix + '^' + ctx
    tasklet = bluepy.TaskletExt(ctx, func)
    if notls:
        tasklet.localStorage.clear()
    tasklet(*args, **kw)
    return tasklet



def Pool(ctx, func, *args, **keywords):
    return PoolWithoutTheStars(ctx, func, args, keywords)



def ParallelHelper(ch, idx, what):
    (queue, parentTasklet,) = ch
    try:
        with locks.Inheritance(parentTasklet):
            if len(what) > 2:
                result = what[0](*what[1], **what[2])
            else:
                result = what[0](*what[1])
            ret = (1, (idx, result))
    except:
        ret = (0, sys.exc_info())
    queue.put(ret)



def Parallel(funcs, exceptionHandler = None, maxcount = 30, contextSuffix = None, funcContextSuffixes = None):
    if not funcs:
        return 
    context = blue.pyos.taskletTimer.GetCurrent()
    if contextSuffix:
        context += '::' + contextSuffix
    ch = (Queue(preference=-1), stackless.getcurrent())
    n = len(funcs)
    ret = [None] * n
    if n > maxcount:
        n = maxcount
    for i in xrange(n):
        funcContext = context
        if funcContextSuffixes is not None:
            funcContext = funcContext + '::' + funcContextSuffixes[i]
        Pool(funcContext, ParallelHelper, ch, i, funcs[i])

    error = None
    try:
        for i in xrange(len(funcs)):
            (ok, bunch,) = ch[0].get()
            if ok:
                (idx, val,) = bunch
                ret[idx] = val
            else:
                error = bunch
            if n < len(funcs):
                funcContext = context
                if funcContextSuffixes is not None:
                    funcContext = funcContext + '::' + funcContextSuffixes[i]
                Pool(funcContext, ParallelHelper, ch, n, funcs[n])
                n += 1

        if error:
            if exceptionHandler:
                exceptionHandler(error[1])
            else:
                raise error[0], error[1], error[2]
        return ret

    finally:
        del error




class TaskletSequencer(object):

    def __init__(self, expected = None):
        self.queue = []
        self.expected = expected
        self.lastThrough = None
        self.closed = False



    def State(self):
        return [self.expected, self.lastThrough, self.closed]



    def IsClosed(self):
        return self.closed



    def close(self):
        self.closed = True
        while self.queue:
            heapq.heappop(self.queue)[1].insert()




    def Assert(self, expression):
        if not expression:
            raise AssertionError(expression)



    def Pass(self, sequenceNo):
        if self.closed:
            return 
        if self.expected is None:
            self.expected = sequenceNo
        if sequenceNo < self.expected:
            return 
        while sequenceNo > self.expected:
            me = (sequenceNo, stackless.getcurrent())
            heapq.heappush(self.queue, me)
            self.OnSleep(sequenceNo)
            stackless.schedule_remove()
            self.OnWakeUp(sequenceNo)
            if self.closed:
                return 

        self.Assert(self.expected == sequenceNo)
        self.expected += 1
        expected = self.expected
        while self.queue and self.queue[0][0] == expected:
            self.OnWakingUp(sequenceNo, expected)
            expected += 1
            other = heapq.heappop(self.queue)
            other[1].insert()

        if self.lastThrough is not None:
            self.Assert(self.lastThrough + 1 == sequenceNo)
        self.lastThrough = sequenceNo



    def OnSleep(self, sequenceNo):
        pass



    def OnWakeUp(self, sequenceNo):
        pass



    def OnWakingUp(self, sequenceNo, target):
        pass




def CallOnThread(cmd, args = (), kwds = {}):
    chan = stackless.channel()

    def Helper():
        try:
            try:
                r = cmd(*args, **kwds)
                chan.send(r)
            except:
                (e, v,) = sys.exc_info()[:2]
                chan.send_exception(e, v)

        finally:
            blue.pyos.NextScheduledEvent(0)



    thread = threading.Thread(target=Helper)
    thread.start()
    return chan.receive()


namedlocks = {}

def Lock(object, *args):
    global namedlocks
    t = (id(object), args)
    if t not in namedlocks:
        namedlocks[t] = Semaphore(t, strict=False)
    namedlocks[t].acquire()



def TryLock(object, *args):
    t = (id(object), args)
    if t not in namedlocks:
        namedlocks[t] = Semaphore(t, strict=False)
    if not namedlocks[t].IsCool():
        return False
    namedlocks[t].acquire()
    return True



def ReentrantLock(object, *args):
    t = (id(object), args)
    if t not in namedlocks:
        namedlocks[t] = CriticalSection(t)
    namedlocks[t].acquire()



def UnLock(object, *args):
    t = (id(object), args)
    namedlocks[t].release()
    if t in namedlocks and namedlocks[t].IsCool():
        del namedlocks[t]



def CheckLock(object, *args):
    t = (id(object), args)
    return t in namedlocks



class BlockTrapSection(object):
    __guid__ = 'uthread.BlockTrapSection'

    def __init__(self):
        self.oldBlocktrap = False



    def __enter__(self):
        self.oldBlockTrap = stackless.getcurrent().block_trap
        stackless.getcurrent().block_trap = True



    def __exit__(self, exc, val, tb):
        stackless.getcurrent().block_trap = self.oldBlockTrap




def ChannelWait(chan, timeout = None):
    if timeout is None:
        return (True, chan.receive())
    waiting_tasklet = stackless.getcurrent()

    def break_wait():
        try:
            blue.pyos.synchro.SleepWallclock(int(timeout * 1000))
        except _TimeoutError:
            return 
        with atomic():
            if waiting_tasklet and waiting_tasklet.blocked:
                waiting_tasklet.raise_exception(_TimeoutError)


    with atomic():
        breaker = new(break_wait)
        try:
            try:
                result = chan.receive()
                if breaker.blocked:
                    breaker.raise_exception(_TimeoutError)
                return (True, result)
            except _TimeoutError:
                return (False, None)

        finally:
            waiting_tasklet = None




class _TimeoutError(Exception):
    pass
exports = {'uthread.parallel': Parallel,
 'uthread.worker': PoolWorker,
 'uthread.workerWithoutTheStars': PoolWorkerWithoutTheStars,
 'uthread.new': new,
 'uthread.pool': Pool,
 'uthread.irandom': irandom,
 'uthread.uniqueId': uniqueId,
 'uthread.schedule': schedule,
 'uthread.GetChannels': GetChannels,
 'uthread.GetSemaphores': GetSemaphores,
 'uthread.FNext': FNext,
 'uthread.Lock': Lock,
 'uthread.TryLock': TryLock,
 'uthread.ReentrantLock': ReentrantLock,
 'uthread.UnLock': UnLock,
 'uthread.TaskletSequencer': TaskletSequencer,
 'uthread.CallOnThread': CallOnThread,
 'uthread.CheckLock': CheckLock,
 'uthread.BlockTrapSection': BlockTrapSection,
 'uthread.ChannelWait': ChannelWait}
new(LockCheck).context = '^uthread::LockCheck'
locks.Startup(new)

