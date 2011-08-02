import sys
import blue
import copy
import cPickle
import bluepy
from timerstuff import ClockThis
active = prefs.GetValue('taskletTimers', False)
memActive = prefs.GetValue('taskletTimersMem', False)
if not active:
    memActive = False
if active != blue.pyos.taskletTimer.active:
    blue.pyos.taskletTimer.active = active
if memActive != sys.getmemcontextsactive():
    sys.setmemcontextsactive(memActive)

class Resources(object):
    __slots__ = ['hTime',
     'rTime',
     'kTime',
     'uTime',
     'nCalls',
     'nSwitches',
     'nBlocks',
     'nBytes']

    def __getstate__(self):
        return tuple([ getattr(self, slot, None) for slot in self.__slots__ ])



    def __setstate__(self, state):
        for i in range(len(self.__slots__)):
            setattr(self, self.__slots__[i], state[i])




    @staticmethod
    def CallgrindHeader(f):
        print >> f, 'events: wt, ut, kt, ct, mem, blk'
        print >> f, 'event: wt: wallclock time (ns)'
        print >> f, 'event: ut: user time (us)'
        print >> f, 'event: kt: kernel time (us)'
        print >> f, 'event: ct: cpu time time (us)'
        print >> f, 'event: mem: mem allocated in context (bytes)'
        print >> f, 'event: blk: mem allocated in context (blocks)'



    @staticmethod
    def microseconds(t):
        return int(t * 1000000.0 + 0.5)



    @staticmethod
    def nanoseconds(t):
        return int(t * 1000000000.0 + 0.5)



    def CallgrindPrint(self, f):
        print >> f, self.nanoseconds(self.hTime), self.microseconds(self.uTime), self.microseconds(self.kTime),
        print >> f, self.microseconds(self.uTime + self.kTime),
        print >> f, self.nBytes, self.nBlocks


    modes = ['wallclock',
     'kerneltime',
     'usertime',
     'cputime',
     'real',
     'membytes',
     'memblocks',
     'nocputime']
    types = ['s',
     's',
     's',
     's',
     's',
     'b',
     '',
     's']
    mode = 0

    def GetModes(self):
        return self.modes


    GetModes = classmethod(GetModes)

    def SetMode(self, m = 'wallclock'):
        if m:
            self.mode = self.modes.index(m)
        else:
            self.mode = 0


    SetMode = classmethod(SetMode)

    def GetMode(self):
        return (self.modes[self.mode], self.types[self.mode])


    GetMode = classmethod(GetMode)

    def GetVal(self):
        m = self.mode
        if m == 0:
            return self.hTime
        if m == 1:
            return self.kTime
        if m == 2:
            return self.uTime
        if m == 3:
            return self.kTime + self.uTime
        if m == 4:
            return self.rTime
        if m == 5:
            return self.nBytes
        if m == 6:
            return self.nBlocks
        if m == 7:
            return self.hTime - self.kTime - self.uTime
        raise ValueError



    def GetType(self):
        return self.types[self.mode]



    def __init__(self, o = None):
        for i in self.__slots__:
            setattr(self, i, 0)

        if type(o) is dict:
            for (k, v,) in o.items():
                if k in self.__slots__:
                    setattr(self, k, v)

        elif type(o) is Resources:
            for k in self.__slots__:
                setattr(self, k, getattr(o, k))




    def copy(self):
        r = Resources()
        for n in self.__slots__:
            setattr(r, n, getattr(self, n))

        return r



    def IMax(self, o):
        for k in self.__slots__:
            setattr(self, k, max(getattr(self, k), getattr(o, k)))




    def __iadd__(self, o):
        r = self.rTime
        for k in self.__slots__:
            setattr(self, k, getattr(self, k) + getattr(o, k))

        self.rTime = max(r, o.rTime)
        return self



    def __add__(self, o):
        r = Resources(self)
        r += o
        return r




class Timer(object):
    __slots__ = ['name',
     'key',
     'own',
     'cum',
     'callees',
     'callers']

    def __init__(self, name = 'unset'):
        self.name = self.key = name
        self.own = Resources()
        self.cum = Resources()
        self.callees = {}
        self.callers = {}



    def __getstate__(self):
        return tuple([ getattr(self, slot, None) for slot in self.__slots__ ])



    def __setstate__(self, state):
        for i in range(len(self.__slots__)):
            setattr(self, self.__slots__[i], state[i])




    def copy(self):
        t = Timer(self.name)
        t.own = self.own.copy()
        t.cum = self.cum.copy()
        t.callees = self.callees.copy()
        t.callers = self.callers.copy()
        t.key = self.key
        return t



    def GetTime(self):
        return self.own.GetVal()



    def GetCTime(self):
        return self.cum.GetVal()



    def GetType(self):
        return self.cum.GetType()


    time = property(GetTime)
    ctime = property(GetCTime)

    def GetSwitches(self):
        return self.own.nSwitches


    switches = property(GetSwitches)

    def GetCalls(self):
        return self.own.nCalls


    calls = property(GetCalls)

    def __iadd__(self, other):
        self.own += other.own
        self.cum.IMax(other.cum)
        self.callees = self.callers = {}
        return self



    def __add__(self, other):
        r = self.copy()
        r += other
        return r



    def __le__(self, other):
        return self.key <= other.key




class Callee(object):
    __slots__ = ['ncalls', 'cum']

    def __init__(self, nc, c):
        (self.ncalls, self.cum,) = (nc, c)



    def __getstate__(self):
        return tuple([ getattr(self, slot, None) for slot in self.__slots__ ])



    def __setstate__(self, state):
        for i in range(len(self.__slots__)):
            setattr(self, self.__slots__[i], state[i])




    def GetCTime(self):
        return self.cum.GetVal()



    def GetType(self):
        return self.cum.GetType()


    ctime = property(GetCTime)
    type = property(GetType)

    def __iadd__(self, other):
        self.ncalls += other.ncalls
        self.cum += other.cum
        return self




def GetChains(filter = None, root = True):
    import sys
    if hasattr(sys, 'getmemcontexts'):
        taskletmem = sys.getmemcontexts()
    else:
        taskletmem = {}
    chains = []
    done = {}
    threadTimes = blue.pyos.taskletTimer.GetThreadTimes()
    processTimes = blue.pyos.taskletTimer.GetProcessTimes()
    tasklets = blue.pyos.taskletTimer.GetTasklets()
    for chain in tasklets:
        r = []
        truncate = False
        for i in chain[None]:
            id = i['Id']
            key = i['Key']
            if id not in done:
                res = Resources(i)
                if id in taskletmem:
                    (res.nBytes, res.nBlocks,) = taskletmem[id]
                    del taskletmem[id]
                done[id] = res
            res = done[id]
            r.append((id, key, res))
            if truncate:
                break
            if filter and filter == key:
                truncate = True

        chains.append(r[None])

    if root:
        res = Resources()
        app = [(-2, 'root', res)]
        chains = [ app + chain for chain in chains ]
    if taskletmem and not filter:
        for (key, val,) in taskletmem.iteritems():
            other = Resources()
            (other.nBytes, other.nBlocks,) = val
            chains.append([(key, '[orphaned mem ctxt]::%d' % key, other)])

    return (chains, threadTimes, processTimes)



def TimersFromChains(chains, filter = None):
    timers = {}
    added = {}
    for chain in chains:
        blue.pyos.BeNice(50)
        rec = {}
        for i in chain:
            key = i[1]
            rec[key] = rec.get(key, 0) + 1

        if chain and chain[0][0] == -2:
            rec[chain[0][1]] += 1
        cum = Resources()
        lastKey = None
        found = filter == None
        for i in reversed(chain):
            id = i[0]
            key = i[1]
            own = i[2]
            if key not in timers:
                timers[key] = Timer(key)
            timer = timers[key]
            if id not in added:
                timer.own += own
                cum += own
                added[id] = True
            if rec[key] == 1:
                timer.cum += cum
            else:
                rec[key] -= 1
            if filter and not found:
                found = filter == key
            if lastKey and found:
                if lastKey in timer.callees:
                    timer.callees[lastKey] += callee
                else:
                    timer.callees[lastKey] = callee
            lastKey = key
            callee = Callee(own.nCalls, cum.copy())


    for (caller, timer,) in timers.iteritems():
        for (callee, val,) in timer.callees.iteritems():
            timers[callee].callers[caller] = val


    return timers



def GetTimer(key):
    timers = TimersFromChains(GetChains()[0])
    return timers.get(key, None)


import inifile
taskletWhiteList = []

def InitTaskletWhiteList():
    global taskletWhiteList
    taskletWhiteList = []
    import copy_reg
    taskletWhiteList.append(copy_reg._reconstructor)
    import ttimerutil
    taskletWhiteList.append(ttimerutil.Callee)
    taskletWhiteList.append(ttimerutil.Resources)
    taskletWhiteList.append(ttimerutil.TaskletSnapshot)
    taskletWhiteList.append(ttimerutil.Timer)
    import __builtin__
    taskletWhiteList.append(__builtin__.dict)
    taskletWhiteList.append(__builtin__.object)



def find_global(moduleName, className):
    mod = __import__(moduleName, globals(), locals(), [])
    obj = getattr(mod, className)
    if obj in taskletWhiteList:
        return obj
    raise cPickle.UnpicklingError('%s.%s not in whitelist' % (moduleName, className))



def Unpickler(file):
    if not taskletWhiteList:
        InitTaskletWhiteList()
    u = inifile.old_Unpickler(file)
    u.find_global = find_global
    return u



def LoadPickle(fileObj):
    return Unpickler(fileObj).load()



class TaskletSnapshot(dict):
    __guid__ = 'ttimerutil.TaskletSnapshot'

    def __init__(self):
        (chains, self.threadTimes, self.processTimes,) = ClockThis('TaskletSnapshot::GetChains', GetChains)
        timers = ClockThis('TaskletSnapshot::TimersFromChains', TimersFromChains, chains)
        self.update(timers)



    def Save(self, filename = None):
        if filename:
            file = open(filename, 'wb')
            try:
                cPickle.dump(self, file)

            finally:
                file.close()

        else:
            return cPickle.dumps(self)



    def Load(filename):
        file = open(filename, 'rb')
        try:
            r = LoadPickle(file)

        finally:
            file.close()

        return r


    Load = staticmethod(Load)

    def PrintCallgrindData(self, f):
        print >> f, 'creator: blue tasklet timers'
        Resources.CallgrindHeader(f)

        def splitname(n):
            idx = n.rfind('::')
            if idx >= 0:
                (fl, fn,) = (n[:idx], n[(idx + 2):])
                if not fl:
                    fl = '<none>'
                if not fn:
                    fn = '<none>'
                return (fl.replace(' ', '_'), fn.replace(' ', '_'))
            return ('<none>', n.replace(' ', '_'))


        (mfn, mfl,) = ({}, {})
        ifn = ifl = 1
        for (k, v,) in self.iteritems():
            (fl, fn,) = splitname(v.name.encode('utf_8'))
            if fl not in mfl:
                mfl[fl] = '(%d)' % ifl
                ifl += 1
            if fn not in mfn:
                mfn[fn] = '(%d)' % ifn
                ifn += 1

        print >> f, '#function mapping'
        for (k, v,) in mfn.iteritems():
            print >> f, 'fn=%s %s' % (v, k)

        print >> f, '#filename mapping'
        for (k, v,) in mfl.iteritems():
            print >> f, 'fl=%s %s' % (v, k)

        if False:
            for k in mfl.keys():
                mfl[k] = k

            for k in mfn.keys():
                mfn[k] = k

        print >> f, '\n# call stats'
        lastfn = lastfl = None
        for timer in self.itervalues():
            print >> f
            (fl, fn,) = splitname(timer.name.encode('utf_8'))
            if fl != lastfl:
                print >> f, 'fl=%s' % mfl[fl]
                lastfl = fl
            if fn != lastfn:
                print >> f, 'fn=%s' % mfn[fn]
                lastfn = fn
            print >> f, 0,
            timer.own.CallgrindPrint(f)
            for (key, callee,) in timer.callees.iteritems():
                target = self[key]
                (cfl, cfn,) = splitname(target.name.encode('utf_8'))
                if cfl != fl:
                    print >> f, 'cfl=%s' % mfl[cfl]
                if cfn != fn:
                    print >> f, 'cfn=%s' % mfn[cfn]
                print >> f, 'calls=%d, 0' % callee.ncalls
                print >> f, 0,
                callee.cum.CallgrindPrint(f)


        print >> f, '#end'



exports = {'ttimerutil.Resources': Resources,
 'ttimerutil.Timer': Timer,
 'ttimerutil.TaskletSnapshot': TaskletSnapshot,
 'ttimerutil.Callee': Callee,
 'ttimerutil.SetTimeMode': Resources.SetMode,
 'ttimerutil.GetTimeMode': Resources.GetMode,
 'ttimerutil.GetTimeModes': Resources.GetModes,
 'ttimerutil.GetTimer': GetTimer}

