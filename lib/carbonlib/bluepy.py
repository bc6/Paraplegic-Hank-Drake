import stackless
import weakref
import blue
import sys
import traceback
import functools
import types
import util
import time
import os
if blue.pyos.markupZonesInPython:

    def CCP_STATS_ZONE_FUNCTION(func):

        def wrapper(*args, **kwargs):
            try:
                blue.statistics.EnterZone(func.__name__)
                res = func(*args, **kwargs)

            finally:
                blue.statistics.LeaveZone()

            return res


        return wrapper



    def CCP_STATS_ZONE_METHOD(method):
        zoneName = method.__name__

        def wrapper(self, *args, **kwargs):
            try:
                blue.statistics.EnterZone(zoneName)
                res = method(self, *args, **kwargs)

            finally:
                blue.statistics.LeaveZone()

            return res


        return wrapper



    def CCP_STATS_ZONE_METHOD_IN_WAITING(name, method):
        zoneName = name + '::' + method.__name__

        def wrapper(self, *args, **kwargs):
            try:
                blue.statistics.EnterZone(zoneName)
                res = method(self, *args, **kwargs)

            finally:
                blue.statistics.LeaveZone()

            return res


        return wrapper



    class CCP_STATS_ZONE_PER_METHOD(type):

        def __new__(cls, name, bases, dct):
            print 'Marking up class',
            print name
            for key in dct:
                if isinstance(dct[key], types.FunctionType):
                    print 'Method',
                    print dct[key].__name__
                    dct[key] = CCP_STATS_ZONE_METHOD_IN_WAITING(name, dct[key])

            return type.__new__(cls, name, bases, dct)



else:

    def CCP_STATS_ZONE_FUNCTION(func):
        return func



    def CCP_STATS_ZONE_METHOD(method):
        return method



    class CCP_STATS_ZONE_PER_METHOD(type):
        pass

class TaskletExt(stackless.tasklet):
    __slots__ = ['context',
     'localStorage',
     'storedContext',
     'startTime',
     'endTime',
     'runTime']

    @staticmethod
    def GetWrapper(method):
        if not callable(method):
            raise TypeError('TaskletExt::__new__ argument "method" must be callable.')

        def CallWrapper(*args, **kwds):
            current = stackless.getcurrent()
            current.startTime = blue.os.GetTime(1)
            oldtimer = PushTimer(current.context)
            exc = None
            try:
                try:
                    try:
                        return method(*args, **kwds)
                    except TaskletExit as e:
                        import log
                        log.general.Log('tasklet %s exiting with %r' % (stackless.getcurrent(), e), log.LGINFO)
                    except SystemExit as e:
                        import log
                        log.general.Log('system %s exiting with %r' % (stackless.getcurrent(), e), log.LGINFO)
                    except Exception:
                        import log
                        print >> debugFile, 'Unhandled exception in tasklet', repr(stackless.getcurrent())
                        traceback.print_exc(file=debugFile)
                        exc = sys.exc_info()
                        log.LogException('Unhandled exception in %r' % stackless.getcurrent())
                    return 
                except:
                    traceback.print_exc()
                    traceback.print_exc(file=debugFile)
                    if exc:
                        traceback.print_exception(exc[0], exc[1], exc[2])
                        traceback.print_exception(exc[0], exc[1], exc[2], file=debugFile)

            finally:
                exc = None
                PopTimer(oldtimer)
                current.endTime = blue.os.GetTime(1)



        return CallWrapper



    def __new__(self, ctx, method = None):
        if method:
            t = stackless.tasklet.__new__(self, self.GetWrapper(method))
        else:
            t = stackless.tasklet.__new__(self)
        c = stackless.getcurrent()
        ls = getattr(c, 'localStorage', None)
        if ls is None:
            t.localStorage = {}
        else:
            t.localStorage = dict(ls)
        t.storedContext = t.context = ctx
        t.runTime = 0.0
        tasklets[t] = True
        return t



    def bind(self, callableObject):
        return stackless.tasklet.bind(self, self.CallWrapper(callableObject))



    def become(self, *args, **kwds):
        raise RuntimeError, 'become()/capture() has been banned.  Do it differently'


    capture = become

    def __repr__(self):
        abps = [ getattr(self, attr) for attr in ['alive',
         'blocked',
         'paused',
         'scheduled'] ]
        abps = ''.join((str(int(flag)) for flag in abps))
        return '<TaskletExt object at %x, abps=%s, ctxt=%r>' % (id(self), abps, getattr(self, 'storedContext', None))



    def __reduce__(self):
        return (str, ("__reduce__()'d " + repr(self),))



    def PushTimer(self, ctxt):
        blue.pyos.taskletTimer.EnterTasklet(ctxt)



    def PopTimer(self, ctxt):
        blue.pyos.taskletTimer.ReturnFromTasklet(ctxt)



    def GetCurrent(self):
        blue.pyos.taskletTimer.GetCurrent()



    def GetWallclockTime(self):
        return (blue.os.GetTime(1) - self.startTime) * 1e-07



    def GetRunTime(self):
        return self.runTime + blue.pyos.GetTimeSinceSwitch()



tasklets = weakref.WeakKeyDictionary()

def Shutdown(exitprocs):

    def RunAll():
        stackless.getcurrent().block_trap = True
        for proc in exitprocs:
            try:
                proc()
            except Exception:
                import log
                log.LogException('exitproc ' + repr(proc), toAlertSvc=False)
                sys.exc_clear()



    if exitprocs:
        TaskletExt('Shutdown', RunAll)()
        intr = stackless.run(1000000)
        if intr:
            log.general.Log('ExitProcs interrupted at tasklet ' + repr(intr), log.LGERR)
    GetTaskletDump(True)
    if len(tasklets):
        KillTasklets()
        GetTaskletDump(True)



def GetTaskletDump(logIt = True):
    import log
    lines = []
    lines.append('GetTaskletDump:  %s TaskletExt objects alive' % len(tasklets))
    lines.append('[context] - [code] - [stack depth] - [creation context]')
    for t in tasklets.keys():
        try:
            if t.frame:
                stack = traceback.extract_stack(t.frame, 1)
                depth = len(stack)
                f = stack[-1]
                code = '%s(%s)' % (f[0], f[1])
            else:
                (code, depth,) = ('<no frame>', 0)
        except Exception as e:
            (code, depth,) = (repr(e), 0)
        ctx = (getattr(t, 'context', '(unknown)'),)
        sctx = getattr(t, 'storedContext', '(unknown)')
        l = '%s - %s - %s - %s' % (sctx,
         code,
         depth,
         ctx)
        lines.append(l)

    lines.append('End TaskletDump')
    if logIt:
        for l in lines:
            log.general.Log(l, log.LGINFO)

    return '\n'.join(lines) + '\n'



def KillTasklets():
    t = TaskletExt('KillTasklets', KillTasklets_)
    t()
    t.run()



def KillTasklets_():
    import log
    log.general.Log('killing all %s TaskletExt objects' % len(tasklets), log.LGINFO)
    for i in range(3):
        for t in tasklets.keys():
            if t is stackless.getcurrent():
                continue
            try:
                if t.frame:
                    log.general.Log('killing %s' % t, log.LGINFO)
                    t.kill()
                else:
                    log.general.Log('ignoring %r, no frame.' % t, log.LGINFO)
            except RuntimeError as e:
                log.general.Log("couldn't kill %r: %r" % (t, e), log.LGWARN)


    log.general.Log('killing done', log.LGINFO)



class DebugFile(object):

    def __init__(self):
        import blue
        self.ODS = blue.win32.OutputDebugString



    def close(self):
        pass



    def flush(self):
        pass



    def write(self, str):
        self.ODS(str)



    def writelines(self, lines):
        for l in lines:
            self.ODS(l)




debugFile = DebugFile()

class PyResFile(object):
    __slots__ = ['rf',
     'name',
     'mode',
     'softspace']

    def __init__(self, path, mode = 'r', bufsize = -1):
        self.rf = blue.ResFile()
        self.mode = mode
        self.name = path
        if 'w' in mode:
            try:
                self.rf.Create(path)
            except:
                raise IOError, 'could not create ' + path
        else:
            readonly = 'a' not in mode and '+' not in mode
            try:
                self.rf.OpenAlways(path, readonly, mode)
            except:
                raise IOError, 'could not open ' + path



    def read(self, count = 0):
        try:
            return self.rf.read(count)
        except:
            raise IOError, 'could not read %d bytes from %s' % (count, self.rf.filename)



    def write(self, data):
        raise NotImplemented



    def readline(self, size = 0):
        raise NotImplemented



    def readlines(self, sizehint = 0):
        r = []
        while True:
            l = self.readline()
            if not l:
                return r
            r.append(l)




    def writelines(self, iterable):
        for i in iterable:
            self.write(i)




    def seek(self, where, whence = 0):
        if whence == 1:
            where += self.rf.pos
        elif whence == 2:
            where += self.rf.size
        try:
            self.rf.Seek(where)
        except:
            raise IOError, 'could not seek to pos %d in %s' % (where, self.rf.filename)



    def tell(self):
        return self.rf.pos



    def truncate(self, size = None):
        if size is None:
            size = self.rf.pos
        try:
            self.rf.SetSize(size)
        except:
            raise IOError, 'could not trucated file %s to %d bytes' % (self.rf.filename, size)



    def flush():
        pass



    def isatty():
        return False



    def close(self):
        self.rf.close()
        del self.rf



    def next(self):
        l = self.readline()
        if l:
            return l
        raise StopIteration



    def __iter__(self):
        return self




def PushTimer(ctxt):
    return blue.pyos.taskletTimer.EnterTasklet(ctxt)



def PopTimer(old):
    return blue.pyos.taskletTimer.ReturnFromTasklet(old)



def CurrentTimer():
    return blue.pyos.taskletTimer.GetCurrent()


EnterTasklet = blue.pyos.taskletTimer.EnterTasklet
ReturnFromTasklet = blue.pyos.taskletTimer.ReturnFromTasklet

class Timer(object):
    __slots__ = ['ctxt']

    def __init__(self, context):
        self.ctxt = context



    def __enter__(self):
        self.ctxt = EnterTasklet(self.ctxt)



    def __exit__(self, type, value, tb):
        ReturnFromTasklet(self.ctxt)
        return False




class TimerPush(Timer):
    GetCurrent = blue.pyos.taskletTimer.GetCurrent

    def __init__(self, context):
        Timer.__init__(self, '::'.join((self.GetCurrent(), context)))




def TimedFunction(ctxt = None):

    def Helper(func):
        myctxt = ctxt if ctxt else repr(func)

        @functools.wraps(func)
        def Wrapper(*args, **kwargs):
            back = EnterTasklet(ctxt)
            try:
                return func(*args, **kwargs)

            finally:
                ReturnFromTasklet(back)



        return Wrapper


    return Helper


blue.TaskletExt = TaskletExt
blue.tasklets = tasklets
stackless.taskletext = TaskletExt
types.BlueType = type(blue.os)

class DecoMetaclass(type):

    def __new__(mcs, name, bases, dict):
        cls = type.__new__(mcs, name, bases, dict)
        cls.__persistvars__ = cls.CombineLists('__persistvars__')
        cls.__nonpersistvars__ = cls.CombineLists('__nonpersistvars__')
        return cls



    def __call__(cls, inst = None, initDict = None, *args, **kwargs):
        if not inst:
            inst = blue.os.CreateInstance(cls.__cid__)
        inst.__klass__ = cls
        if initDict:
            for (k, v,) in initDict.iteritems():
                setattr(inst, k, v)

        try:
            inst.__init__()
        except AttributeError:
            pass
        return inst



    def CombineLists(cls, name):
        result = []
        for b in cls.__mro__:
            if hasattr(b, name):
                result += list(getattr(b, name))

        return result


    subclasses = {}


def GetDecoMetaclassInst(cid):

    class parentclass(object):
        __metaclass__ = DecoMetaclass
        __cid__ = cid

    return parentclass



def GetBlueInfo(numMinutes = None, isYield = True):
    if numMinutes:
        trend = blue.pyos.cpuUsage[(-numMinutes * 60 / 10):]
    else:
        trend = blue.pyos.cpuUsage[:]
    mega = 1.0 / 1024.0 / 1024.0
    ret = util.KeyVal()
    ret.memData = []
    ret.pymemData = []
    ret.bluememData = []
    ret.othermemData = []
    ret.threadCpuData = []
    ret.procCpuData = []
    ret.timeData = []
    ret.latenessData = []
    ret.schedData = []
    latenessBase = 100000000.0
    if len(trend) >= 1:
        ret.actualmin = int((trend[-1][0] - trend[0][0]) / 10000000.0 / 60.0)
        t1 = trend[0][0]
    benice = blue.pyos.BeNice
    for (t, cpu, mem, sched,) in trend:
        if isYield:
            benice()
        elap = t - t1
        t1 = t
        (mem, pymem, workingset, pagefaults, bluemem,) = mem
        ret.memData.append(mem * mega)
        ret.pymemData.append(pymem * mega)
        ret.bluememData.append(bluemem * mega)
        othermem = (mem - pymem - bluemem) * mega
        if othermem < 0:
            othermem = 0
        ret.othermemData.append(othermem)
        (thread_u, proc_u,) = cpu
        if elap:
            thread_cpupct = thread_u / float(elap) * 100.0
            proc_cpupct = proc_u / float(elap) * 100.0
        else:
            thread_cpupct = proc_cpupct = 0.0
        ret.threadCpuData.append(thread_cpupct)
        ret.procCpuData.append(proc_cpupct)
        ret.schedData.append(sched)
        ret.timeData.append(t)
        late = 0.0
        if elap:
            late = (elap - latenessBase) / latenessBase * 100
        ret.latenessData.append(late)

    ret.proc_cpupct = proc_cpupct
    ret.mem = mem
    return ret


BlueWrappedMetaclass = DecoMetaclass
WrapBlueClass = GetDecoMetaclassInst

def IsRunningStartupTest():
    args = blue.pyos.GetArg()
    for (i, each,) in enumerate(args):
        if each.startswith('/startupTest'):
            return True

    return False



def TerminateStartupTest():
    blue.os.Terminate(31337)



def walk(top, topdown = True, onerror = None):
    try:
        names = blue.os.listdir(top)
    except blue.error as err:
        if onerror is not None:
            onerror(err)
        return 
    (dirs, nondirs,) = ([], [])
    for name in names:
        if blue.os.isdir(top + u'/' + name):
            dirs.append(name)
        else:
            nondirs.append(name)

    if topdown:
        yield (top, dirs, nondirs)
    for name in dirs:
        new_path = top + u'/' + name
        for x in walk(new_path, topdown, onerror):
            yield x


    if not topdown:
        yield (top, dirs, nondirs)



