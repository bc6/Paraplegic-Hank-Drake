import blue
import blue.win32
import service
import cPickle
import sys
import util
from math import sqrt
FILE_BM = 'Benchmark.xml'

class BenchmarkService(service.Service):
    __exportedcalls__ = {'CreateSession': [service.ROLE_SERVICE | service.ROLE_GMH],
     'SaveSession': [service.ROLE_SERVICE | service.ROLE_GMH],
     'LoadSessionFile': [service.ROLE_SERVICE | service.ROLE_GMH],
     'SaveSessionFile': [service.ROLE_SERVICE | service.ROLE_GMH]}
    __guid__ = 'svc.benchmark'
    __displayname__ = 'Benchmark Service'
    defaultDB = 'Provider=SQLOLEDB.1;Data Source=eden;User ID=sa;Password=everlast;Initial Catalog=ebs_BENCHMARK;'

    def CreateSession(self, testbedName = None, description = '', runID = 0):
        self.runID = runID
        return Session(testbedName, description, self.runID)



    def SaveSession(self, session, runID, dbconn):
        output = prefs.GetValue('bmoutput', '0:0')
        try:
            (dbop, fiop,) = output.split(':')
        except:
            sys.exc_clear()
            dbop = 0
            fiop = 0
        if self.runID == 0 or dbconn == None or fiop == 1:
            session.SaveToFile()
            return 0
        if dbop:
            try:
                import db
                dbsess = db.Session(dbconn)
                dbsess.GetSchema(1)
                if dbop:
                    return session.SaveToDB(dbsess, self.runID)
                else:
                    return 0
            except ImportError:
                sys.exc_clear()
                return sm.RemoteSvc('benchmark').SaveSession(session, self.runID, dbconn)



    def SaveSessionFile(self, session, destination = None):
        if not destination:
            destination = 'cache:/BM-%s-%s' % (session.testbedName, session.startTime)
        fn = blue.rot.PathToFilename(destination)
        f = open(fn, 'wb')
        try:
            f.write(cPickle.dumps(session))

        finally:
            f.close()




    def LoadSessionFile(self, filePath):
        fn = blue.rot.PathToFilename(filePath)
        f = open(fn, 'r')
        try:
            session = cPickle.loads(f.read())

        finally:
            f.close()

        return session




class Session(object):
    __guid__ = 'benchmark.Session'

    def __init__(self, testbedName = None, description = '', runID = 0):
        self.platform = 0
        self.testbedName = testbedName or '?'
        self.description = description
        self.startTime = blue.os.GetWallclockTime()
        self.stopTime = self.startTime
        self.version = str(boot.version)
        self.build = boot.build
        self.snapshots = []
        self.data = ValueDict()
        self.testID = 0
        self.runID = runID
        self.runTestID = 0
        self.width = 0
        self.height = 0
        self.testIDFile = 0
        self.runTestIDFile = 0
        self.capturing = False



    def CaptureStart(self):
        self.capturing = True
        while self.capturing:
            self.Snap()
            blue.pyos.synchro.SleepWallclock(1000)




    def CaptureEnd(self):
        self.capturing = False
        self.CreateAverages()



    def Snap(self):
        snapshot = Snapshot()
        self.snapshots.append((blue.os.GetWallclockTime(), snapshot))
        return snapshot



    def CreateAverages(self):
        if len(self.snapshots) > 2:
            lastIdx = -1
        else:
            lastIdx = 1
        (f, l,) = (self.snapshots[0][1], self.snapshots[lastIdx][1])
        dt = (l.timestamp.v - f.timestamp.v) * 1e-07
        df = l.framerate.framesTotal.v - f.framerate.framesTotal.v
        ut = (l.cpuTime.user.v - f.cpuTime.user.v) * 1e-07
        kt = (l.cpuTime.kernel.v - f.cpuTime.kernel.v) * 1e-07
        tt = ut + kt
        fr = df / dt
        fpsVals = []
        for dataset in self.snapshots:
            (timstamp, data,) = dataset
            fpsVals.append(data.framerate.fps.v)

        cfps = len(self.snapshots)
        am = sum(fpsVals) / cfps
        devianceSquaredSum = int()
        for fps in fpsVals:
            devianceFromMean = fps - am
            devianceSquared = devianceFromMean ** 2
            devianceSquaredSum += devianceSquared

        fpsVariance = devianceSquaredSum / cfps
        fsd = sqrt(fpsVariance)
        frCpu = df / tt
        fut = ut / dt
        fkt = kt / dt
        ftt = fut + fkt
        dpf = l.memory.pageFaultCount.v - f.memory.pageFaultCount.v / 2
        dws = max(l.memory.peakWorkingSetSize.v, f.memory.peakWorkingSetSize.v)
        aws = l.memory.peakWorkingSetSize.v - f.memory.peakWorkingSetSize.v / 2
        apf = l.memory.pagefileUsage.v - f.memory.pagefileUsage.v / 2
        ppf = max(l.memory.pagefileUsage.v, f.memory.pagefileUsage.v)
        d = self.data.Sub(['framerate'])
        d['averageFps'] = Value(ValueType(False, 'f', 'average Framerate'), fr)
        d['averageFpsCpu'] = Value(ValueType(False, 'f', 'average Framerate (cpu time)'), frCpu)
        d['fpsStdDev'] = Value(ValueType(False, 'f', 'standard deviation'), fsd)
        d['fpsMean'] = Value(ValueType(False, 'f', 'mean of all framerate samples'), am)
        d['fpsSamplecount'] = Value(ValueType(False, 'i', 'count of fps samples'), cfps)
        d = self.data.Sub(['cpuTime'])
        d['userFraction'] = Value(ValueType(False, 'f', 'user mode fraction of wallclock time'), fut)
        d['kernelFraction'] = Value(ValueType(False, 'f', 'kernel mode fraction of wallclock time'), fkt)
        d['totalFraction'] = Value(ValueType(False, 'f', 'cpu fraction of wallclock time'), ftt)
        self.data['wallclockTime'] = Value(ValueType(False, 'f', 'wallclock time    '), dt)
        d = self.data.Sub(['memory'])
        d['pageFaultCount'] = Value(ValueType(False, 'f', 'average page fault count'), dpf)
        d['peakWorkingSetSize'] = Value(ValueType(False, 'f', 'peak working set size'), dws)
        d['workingSetSize'] = Value(ValueType(False, 'f', 'average working set size'), aws)
        d['pagefileUsage'] = Value(ValueType(False, 'f', 'average page file usage'), apf)
        d['peakPagefileUsage'] = Value(ValueType(False, 'f', 'peak page file usage'), ppf)



    def CreateSnapshot(self):
        self.data.update(self.snapshots[0][1])



    def Start(self):
        self.startTime = blue.os.GetWallclockTime()
        self.data = Snapshot()



    def Stop(self):
        self.stopTime = blue.os.GetWallclockTime()
        s = Snapshot()
        self.data += s



    def AddValue(self, key, platformIndependent, description, format, value):
        self.data[key] = Value(ValueType(platformIndependent, format, description), value)
        self.stopTime = blue.os.GetWallclockTime()



    def GetOrMakeFile(self, *args):
        import os
        invalidChars = '\\/:*?"<>| '
        timestamp = util.FmtDateEng(blue.os.GetWallclockTime())
        for char in invalidChars:
            timestamp = timestamp.replace(char, '.')

        try:
            import benchmark1
            platform = benchmark1.GetPlatform()
            hostname = platform['hostname']
        except:
            sys.exc_clear()
            hostname = 'None'
        filename = settings.public.generic.Get('eveBenchmarkFileName', None)
        if not filename:
            filename = '%s.%s.%s' % (timestamp, hostname, FILE_BM)
            settings.public.generic.Set('eveBenchmarkFileName', filename)
        f = blue.os.CreateInstance('blue.ResFile')
        BENCHMARKDIR = os.path.join(blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL), 'EVE', 'logs', 'Benchmarks')
        TARGET = os.path.join(BENCHMARKDIR, filename)
        if not f.Open(TARGET, 0):
            if f.FileExists(TARGET):
                f.Open(TARGET, 0)
            elif not os.path.exists(BENCHMARKDIR):
                os.mkdir(BENCHMARKDIR)
            f.Create(TARGET)
            f.Write('<?xml version="1.0"?>')
            f.Write('\r\n')
            f.Write('<eveBenchmarking>')
            f.Write('\r\n')
            f.Write('\t<platform>')
            f.Write('\r\n')
            if platform:
                for (k, v,) in platform.iteritems():
                    if v.__class__ in (str, unicode):
                        v = v.encode()
                    f.Write('\t\t')
                    f.Write('<data')
                    f.Write(' key="%s"' % k)
                    f.Write(' value="%s"' % v)
                    f.Write(' />')
                    f.Write('\r\n')

                for (dkey, dvalue,) in self.AppGetTriAppData().iteritems():
                    f.Write('\t\t')
                    f.Write('<data')
                    f.Write(' key="%s"' % dkey)
                    f.Write(' value="%s"' % dvalue)
                    f.Write(' />')
                    f.Write('\r\n')

            f.Write('\t</platform>')
            f.Write('\r\n')
            f.Write('\t<user>')
            f.Write('\r\n')
            for (dkey, dvalue,) in {'charid': session.charid,
             'userid': session.userid,
             'transgaming': blue.win32.IsTransgaming()}.iteritems():
                f.Write('\t\t')
                f.Write('<data')
                f.Write(' key="%s"' % dkey)
                f.Write(' value="%s"' % dvalue)
                f.Write(' />')
                f.Write('\r\n')

            f.Write('\t</user>')
            f.Write('\r\n')
        return f



    def SaveToFile(self):
        data = self.data.copy()
        data.Collapse()
        f = self.GetOrMakeFile()
        f.read()
        f.Write('\t')
        f.Write('<benchmark testName="%s">' % self.testbedName)
        f.Write('\r\n')
        datakeys = data.keys()
        datakeys.sort()
        for key in datakeys:
            value = data[key]
            eType = value.eType
            l = [self.testbedName, key]
            if value.v2 is None:
                l.append(float(value.v))
                f.Write('\t\t')
                f.Write('<data')
                f.Write(' entityName="%s"' % key)
                f.Write(' isPlatformSpecific="%s"' % eType.platformIndependent)
                f.Write(' entityDescription="%s"' % eType.description)
                f.Write(' entityType="%s">' % eType.format)
                f.Write('%s' % value.v)
                f.Write('</data>')
            else:
                l += [float(value.v), float(value.v2)]
            f.Write('\r\n')

        f.Write('\t')
        f.Write('</benchmark>')
        f.Write('\r\n')
        f.Close()



    def SaveToDB(self, dbsess, runID):
        import trinity
        if prefs.clusterMode == 'LIVE':
            liveState = 1
        else:
            liveState = 0
        if self.testID == 0:
            self.testID = dbsess.Execute('dbo.bm2Test_Add', [self.testbedName, liveState, self.description])
        self.width = trinity.app.width
        self.height = trinity.app.height
        try:
            resolutionID = dbsess.Execute('dbo.bm2Resolution_GetBySize', [self.height, self.width])
        except:
            sys.exc_clear()
        fullScreen = trinity.app.fullscreen
        if fullScreen:
            windowed = 0
        else:
            windowed = 1
        if self.runTestID == 0:
            self.runTestID = dbsess.Execute('dbo.bm2RunTest_Add', [runID,
             self.testID,
             self.startTime,
             resolutionID,
             fullScreen])
        dbsess.Execute('dbo.bm2RunTest_Finish', [self.runTestID])
        data = self.data.copy()
        data.Collapse()
        for (key, value,) in data.iteritems():
            eType = value.eType
            entityID = dbsess.Execute('dbo.bm2EntitySelectID', [key,
             eType.platformIndependent,
             eType.description,
             eType.format])
            l = [self.runTestID, entityID]
            if value.v2 is None:
                l.append(float(value.v))
            else:
                l += [float(value.v), float(value.v2)]
            dbsess.Execute('dbo.bm2Results_Add', l)

        return self.runTestID



    def AppGetTriAppData(self):
        import trinity
        return {'width': trinity.app.width,
         'height': trinity.app.height,
         'fullscreen': trinity.app.fullscreen}




class ValueDict(dict):
    __guid__ = 'benchmark.ValueDict'

    def copy(self):
        r = ValueDict()
        for (k, v,) in self.iteritems():
            if isinstance(v, ValueDict):
                v = v.copy()
            r[k] = v

        return r



    def update(self, other):
        for (k, v,) in other.iteritems():
            if isinstance(v, ValueDict):
                if k not in self or not isinstance(self[k], ValueDict):
                    self[k] = ValueDict()
                self[k].update(v)
            else:
                self[k] = v




    def Matchup(self, other):
        for (k, v,) in other.iteritems():
            if k not in self:
                self[k] = v.Default()

        copy = None
        for k in self.iterkeys():
            if k not in other:
                if not copy:
                    copy = other.copy()
                copy[k] = self[k].Default()

        return copy or other



    def __getattr__(self, key):
        if key not in self:
            raise AttributeError, key
        return self[key]



    def __iadd__(self, other):
        other = self.Matchup(other)
        for (k, v,) in other.iteritems():
            self[k] += v

        return self



    def __isub__(self, other):
        other = self.Matchup(other)
        for (k, v,) in other.iteritems():
            self[k] -= v

        return self



    def __imul__(self, value):
        for k in self.iterkeys():
            self[k] *= value

        return self



    def __add__(self, other):
        r = self.copy()
        r += other
        return r



    def __sub__(self, other):
        r = self.copy()
        r -= other
        return r



    def __mul__(self, value):
        r = self.copy()
        r *= value
        return r



    def Sub(self, keys):
        if not keys:
            return self
        if keys[0] not in self:
            self[keys[0]] = ValueDict()
        return self[keys[0]].Sub(keys[1:])



    def Collapse(self):
        d = self.__class__()
        for (k, v,) in self.iteritems():
            if isinstance(v, ValueDict):
                v.Collapse()
                for (k2, v2,) in v.iteritems():
                    d[strx(k) + '::' + strx(k2)] = v2

            else:
                d[k] = v

        self.clear()
        self.update(d)



    def Default(self):
        return ValueDict()




class Snapshot(ValueDict):
    __guid__ = 'benchmark.Snapshot'

    def __init__(self):
        self.Capture()



    def Capture(self):
        self.clear()
        self.update({'timestamp': self.GetTimestamp(),
         'framerate': self.GetFramerate(),
         'memory': self.GetMemory(),
         'cpuTime': self.GetCpuTime()})



    def GetTimestamp(self):
        return Value(ValueType(False, 't'), blue.os.GetWallclockTimeNow())



    def GetFramerate(self):
        return ValueDict({'fps': Value(ValueType(False, 'f'), blue.os.fps),
         'framesTotal': Value(ValueType(False, 'i'), blue.os.framesTotal)})



    def GetMemory(self):
        r = ValueDict()
        info = blue.pyos.ProbeStuff()
        for (k, v,) in zip(info[0], info[1]):
            r[k] = Value(ValueType(False, 'i'), v)

        return r



    def GetCpuTime(self):
        r = {}
        info = blue.pyos.GetThreadTimes()
        for (k, v,) in zip(info[0], info[1]):
            r[k] = v

        kt = r['kernel']
        ut = r['user']
        tt = kt + ut
        return ValueDict(dict([ (k, Value(ValueType(False, 't'), v)) for (k, v,) in [('user', ut), ('kernel', kt), ('total', tt)] ]))



    def GetPyObjects(self):
        d = GetPyObjectCounts()
        for k in d.keys():
            d[k] = Value(ValueType(True, 'i'), d[k])

        return ValueDict(d)



    def GetBlueObjects(self):
        d = blue.rot.LiveCount()
        for k in d.keys():
            d[k] = Value(ValueType(True, 'i'), d[k])

        return ValueDict(d)



    def GetTaskletTimers(self):
        return ValueDict()
        inv_f = 1.0 / blue.pyos.taskletTimer.GetThreadTimes()['timerFreq']
        r = ValueDict()
        for v in blue.pyos.taskletTimer.GetTasklets():
            time = v.time * inv_f
            ctime = v.cTime * inv_f
            calls = v.calls
            if calls:
                tpc = time / calls
                ctpc = ctime / calls
            else:
                tpc = ctpc = 0.0
            r[strx(k)] = ValueDict({'time': Value(ValueType(True, 't'), v.time),
             'ctime': Value(ValueType(True, 't'), v.cTime),
             'time/c': Value(ValueType(True, 'T'), tpc),
             'ctime/c': Value(ValueType(True, 'T'), ctpc),
             'switches': Value(ValueType(False, 'i'), v.switches),
             'calls': Value(ValueType(False, 'i'), v.calls)})

        return r




class Value(object):
    __guid__ = 'benchmark.Value'

    def __init__(self, eType, v = 0, v2 = None):
        self.eType = eType
        self.v = v
        self.v2 = v2



    def copy(self):
        return self.__class__(self.eType, self.v, self.v2)



    def Default(self):
        return self.__class__(self.eType)



    def __iadd__(self, other):
        self.v += other.v
        if self.v2 is not None:
            self.v2 += other.v2
        return self



    def __isub__(self, other):
        self.v -= other.v
        if self.v2 is not None:
            self.v2 -= other.v2
        return self



    def __imul__(self, value):
        self.v *= value
        if self.v2:
            self.v2 *= value
        return self



    def __add__(self, other):
        r = self.copy()
        r += other
        return r



    def __sub__(self, other):
        r = self.copy()
        r -= other
        return r



    def __mul__(self, value):
        r = self.copy()
        r *= value
        return r




class ValueType(object):
    __guid__ = 'benchmark.ValueType'

    def __init__(self, pi = True, format = 0, description = ''):
        self.platformIndependent = pi
        self.format = format
        self.description = description




def Type(obj):
    try:
        return obj.__class__
    except AttributeError:
        sys.exc_clear()
        return type(obj)



def TypeName(t):
    return t.__module__ + '.' + t.__name__



def GetPyObjectsFromGC():
    try:
        import gc
        return gc.get_objects()
    except ImportError:
        sys.exc_clear()
        return []



def Namefy(d):
    r = {}
    for (k, v,) in d.iteritems():
        t = TypeName(k)
        if t in r:
            r[t] += v
        else:
            r[t] = v

    return r



def GetPyObjectLists():
    r = {}
    for o in GetPyObjectsFromGC():
        try:
            t = Type(o)
            if t in r:
                r[t].append(o)
            else:
                r[t] = [o]
        except ReferenceError:
            sys.exc_clear()

    return Namefy(r)



def GetPyObjectCounts():
    r = {}
    for o in GetPyObjectsFromGC():
        try:
            t = Type(o)
            r[t] = r.get(t, 0) + 1
        except ReferenceError:
            sys.exc_clear()

    return Namefy(r)


export = {'benchmark.Session': Session}

