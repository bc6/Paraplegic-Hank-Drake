import blue
import unittest
import types
import const
import util
import re
import pstats
import os
import os.path
import log
from cStringIO import StringIO
import copy
import traceback2

class SystemTestResult(unittest.TestResult):

    def __init__(self):
        unittest.TestResult.__init__(self)
        self.previousFailureDate = None
        self.previousFailureChangelist = None
        self.previousFailureCount = None
        self.previousPassDate = None
        self.previousPassChangelist = None
        self.previousPassCount = None
        self.previousRunResult = None



    def _exc_info_to_string(self, err, test):
        out = StringIO()
        traceback2.print_exception(err[0], err[1], err[2], file=out, show_locals=1)
        return out.getvalue()




class SystemTestCategory(object):
    classCategories = {}
    BENCHMARK = 'BENCHMARK'
    CHECKIN = 'CHECKIN'
    CATEGORIES = [BENCHMARK, CHECKIN]

    def __init__(self, testCaseName, categories):
        self.testCaseName = testCaseName
        self.categories = categories



    def __call__(self, f):
        self.testMethodName = f.__name__
        fullname = self.testCaseName + '.' + self.testMethodName
        if not isinstance(self.categories, list):
            self.categories = [self.categories]
        SystemTestCategory.classCategories[fullname] = self.categories

        def wrapped_f(*args):
            f(*args)


        return wrapped_f



    def getTestsByCategory(category):
        ret = []
        for (k, v,) in SystemTestCategory.classCategories.iteritems():
            if category in v:
                ret.append(k)

        return ret



TEST_MANUALLY = 1
TEST_ON_CHECKINS = 2
TEST_ON_BUILDS = 4
TEST_KNOWN_ISSUE = 8
TEST_IN_PROGRESS = 16
GUI_SCREENSHOT_SAVE_FOLDER = '../GUIScreenshots'

def WaitForConditionWithTimeout(condition, timeOut, pollTime = 100):
    start = blue.os.GetWallclockTime() / const.MSEC
    while not condition() and blue.os.GetWallclockTime() / const.MSEC - start < timeOut:
        blue.pyos.synchro.SleepWallclock(pollTime)

    if condition():
        return blue.os.GetWallclockTime() / const.MSEC - start
    else:
        return None



def FindTestsByName(name, partial = False):
    import SystemTests
    lname = name.lower()
    matches = []
    for (k, v,) in SystemTests.__dict__.iteritems():
        if isinstance(v, (type, types.ClassType)) and issubclass(v, unittest.TestCase):
            if partial:
                matched = lname in v.__name__.lower()
            else:
                matched = v.__name__.lower() == lname
            if matched:
                matches.append(v)

    return matches



def FindTestsByRunType(filter):
    import SystemTests
    matches = []
    for (k, v,) in SystemTests.__dict__.iteritems():
        print k,
        print v
        if isinstance(v, (type, types.ClassType)) and issubclass(v, unittest.TestCase):
            runType = getattr(v, 'runType', 0)
            print v.__name__,
            print runType
            if runType & filter:
                matches.append(v)

    return matches



def RunFoundTests(matches):
    for v in matches:
        result = SystemTestResult()
        if isinstance(v, (type, types.ClassType)) and issubclass(v, unittest.TestCase):
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromTestCase(v)
        else:
            suite = unittest.TestSuite([v])
        suite.run(result)
        yield (v, result)




def RunTest(test):
    result = SystemTestResult()
    if isinstance(test, (type, types.ClassType)) and issubclass(test, unittest.TestCase):
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(test)
    else:
        suite = unittest.TestSuite([test])
    suite.run(result)
    return result



def GetPerformanceData(fromTimeStamp, toTimeStamp):
    ret = util.KeyVal()
    USAGE_TIMESTAMP = 0
    USAGE_CPU_THREAD = 1
    USAGE_MEMORY = 2
    USAGE_MEMORY_PYTHON = 3
    USAGE_CPU_PROCESS = 4
    CPU_USAGE_TO_PERCENT = float(1.0 / 1000000.0)
    performanceHistory = []
    numSamples = 0
    avgCpuLoad = 0.0
    avgMemoryConsumption = 0.0
    for trend in blue.pyos.cpuUsage:
        if trend[USAGE_TIMESTAMP] >= fromTimeStamp and trend[USAGE_TIMESTAMP] <= toTimeStamp:
            avgCpuLoad += trend[USAGE_CPU_PROCESS] * CPU_USAGE_TO_PERCENT
            avgMemoryConsumption += trend[USAGE_MEMORY]
            performanceSnapshot = (trend[USAGE_TIMESTAMP] / blue.pyos.performanceUpdateFrequency,
             trend[USAGE_CPU_PROCESS] * CPU_USAGE_TO_PERCENT,
             trend[USAGE_CPU_THREAD] * CPU_USAGE_TO_PERCENT,
             trend[USAGE_MEMORY],
             trend[USAGE_MEMORY_PYTHON],
             trend[USAGE_MEMORY] - trend[USAGE_MEMORY_PYTHON])
            performanceHistory.append(performanceSnapshot)
            numSamples += 1

    if numSamples:
        avgCpuLoad /= numSamples
        avgMemoryConsumption /= numSamples
    ret.avgCpuLoad = avgCpuLoad
    ret.avgMemoryConsumption = avgMemoryConsumption
    ret.performanceHistory = performanceHistory
    return ret



def GetPerformanceDataLabels():
    return ('USAGE_TIMESTAMP', 'USAGE_CPU_PROCESS', 'USAGE_CPU_THREAD', 'USAGE_MEMORY', 'USAGE_MEMORY_PYTHON', 'USAGE_MEMORY_C++')



def GetTaskletTimerLabels():
    return ('key', 'label', 'calls', 'switches', 'time', 'ctime', 'memory', 'blocks')



def MakeString(iterObj):
    if hasattr(iterObj, '__iter__'):
        s = ''
        for i in iterObj:
            if hasattr(i, '__iter__'):
                s += MakeString(i)
            else:
                s += str(i)
                s += ','

        return s
    else:
        return str(iterObj)



def DumpCSV(fileHandle, iterObj):
    if hasattr(iterObj, '__iter__'):
        for i in iterObj:
            fileHandle.write(MakeString(i) + '\n')

    else:
        fileHandle.write(str(iterObj) + '\n')



def ShortStats(stats):
    sdict = {}
    for (k, v,) in stats.items():
        sdict[k] = [v[0],
         v[1],
         v[2],
         v[3]]

    return sdict



def ProcessStats(stats):
    oldstream = stats.stream
    fp = StringIO()
    stats.stream = fp
    try:
        stats.print_stats()

    finally:
        stats.stream = oldstream

    statstxt = fp.getvalue()
    fp.close()
    fp = StringIO()
    stats.stream = fp
    try:
        stats.print_callers()

    finally:
        stats.stream = oldstream

    callerstxt = fp.getvalue()
    fp.close()
    funcpattern = '(\\S*):(\\d+)\\((.+)\\)'
    funcre = re.compile(funcpattern)

    def FmtFunc(f):
        m = funcre.search(f)
        code = m.group(1) + ':' + m.group(2) if m.group(1) else 'c'
        return '%s (%s)' % (m.group(3), code)


    stats = {}
    for l in statstxt.splitlines()[5:]:
        l = l.strip()
        if not l:
            continue
        fields = l.split()
        if len(fields) == 4:
            fields = fields[:2] + ['0'] + fields[2:3] + ['0'] + fields[3:]
        fname = FmtFunc(fields[-1])
        calls = fields[0].split('/')
        (calls, pcalls,) = calls if len(calls) > 1 else (calls[0], calls[0])
        (calls, pcalls,) = (int(calls), int(pcalls))
        time = float(fields[1])
        ctime = float(fields[3])
        stats[fname] = [calls,
         pcalls,
         time,
         ctime,
         [],
         []]

    targetpattern = funcpattern + '\\((\\d+)\\)\\s*(\\S+)'
    targetre = re.compile(targetpattern)
    splitter = re.compile('<-|->')

    def FmtFunc(m):
        code = m.group(1) + ':' + m.group(2) if m.group(1) else 'c'
        return '%s (%s)' % (m.group(3), code)


    for l in callerstxt.splitlines():
        l = l.strip()
        if not l:
            continue
        fields = splitter.split(l)
        if len(fields) == 2:
            (left, right,) = fields
            fname = FmtFunc(funcre.search(left))
        else:
            right = fields[0]
        m = targetre.search(right)
        if not m:
            pass
        else:
            stats[fname][4].append((FmtFunc(m), int(m.group(4))))

    for (func, data,) in stats.iteritems():
        for (c, n,) in data[4]:
            stats[c][5].append((func, n))


    stats = StatsFixup(stats)
    return stats



def StatsFixup(stats):
    stats = copy.deepcopy(stats)
    for v in stats.itervalues():
        v[3] = max(v[2:4])

    roots = []
    for (k, v,) in stats.iteritems():
        if not v[4]:
            roots.append(k)

    if len(roots) > 1:
        rootname = 'metaroot (profile:0)'
        stats[k] = [1,
         1,
         0.0,
         0.0,
         [],
         [ (root, 1) for root in roots ]]
    else:
        rootname = roots[0]
    root = stats[rootname]
    for v in stats.itervalues():
        v[0:2] = [0, 0]

    recursion = {}

    def recurse(stats, recursion, visited, k, n):
        v = stats[k]
        v[0] += n
        if k not in recursion:
            v[1] += n
        if k in visited:
            return 
        visited[k] = True
        recursion[k] = True
        for (callee, n,) in v[5]:
            recurse(stats, recursion, visited, callee, n)

        del recursion[k]


    recurse(stats, {}, {}, rootname, 1)
    ctime = sum([ v[3] for v in [ stats[k[0]] for k in root[5] ] ])
    root[3] = ctime
    ttime = sum((v[2] for v in stats.itervalues()))
    if ttime < ctime:
        diff = ctime - ttime
        root[2] += diff
        ttime += diff
    elif ttime > ctime:
        pass
    return stats



def StripDirs(stats):
    fr = re.compile('(\\S+)\\s+\\((.+):(.+)\\)')
    fmap = {}
    nstats = {}
    for (k, v,) in stats.iteritems():
        (func, file, lineno,) = fr.search(k).group(1, 2, 3)
        nk = '%s (%s:%s)' % (func, os.path.basename(file), lineno)
        fmap[k] = nk
        nstats[nk] = v

    for v in nstats.itervalues():
        v[4] = [ (fmap[k], n) for (k, n,) in v[4] ]
        v[5] = [ (fmap[k], n) for (k, n,) in v[5] ]

    stats.clear()
    stats.update(nstats)



def StripDir(filename):
    return os.path.basename(filename)


import util
exports = util.AutoExports('sysTestUtils', locals())

