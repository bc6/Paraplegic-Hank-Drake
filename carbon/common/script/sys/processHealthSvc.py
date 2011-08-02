from __future__ import with_statement
from base import FindSessions
import service
import base
import util
import blue
import bluepy
import uthread
import log
import sys
import _socket
import datetime
import os
import copy

class ProcessHealthSvc(service.Service):
    __guid__ = 'svc.processHealth'
    __servicename__ = 'processHealth'
    __displayname__ = 'Process Health Service'
    __dependencies__ = ['machoNet']

    def CreateFakeData(self):
        import util
        import random
        import math
        data = util.KeyVal
        data.timeData = []
        data.procCpuData = []
        data.threadCpuData = []
        data.bluememData = []
        data.pymemData = []
        data.memData = []
        data.schedData = []
        t0 = blue.os.GetTime() - 2 * const.DAY
        tp = t0
        delay = 0
        lag = 0
        for i in xrange(0, 5000):
            t0 += 10 * const.SEC
            if i % 400 == 10:
                lag = random.randint(0, 300)
            if lag:
                lag -= 1
            data.timeData.append(t0)
            data.procCpuData.append(math.sin(i / 20.0) * 100)
            data.threadCpuData.append(math.cos(i / 100.0) * 100)
            data.bluememData.append(i)
            data.pymemData.append(math.sin(i / 1000.0) * 1000)
            data.memData.append(i)
            data.schedData.append((math.sin(i * i / 100.0) * 1000,
             math.cos(i / 50.0) * 1000,
             math.sin(i / 10.0) * 100,
             math.sin(i / 100.0) * 100,
             i,
             i))
            if not lag:
                logline = {'pyDateTime': t0 + 5 * const.SEC,
                 'bytesReceived': i * 1000,
                 'bytesSent': i * 1000,
                 'packetsReceived': i * 10,
                 'packetsSent': i * 10,
                 'sessionCount': math.pow(math.sin(i * i / 100.0), 2) * 1000}
            self.data = data
            self.logLines.append(logline)




    def __init__(self, *args):
        service.Service.__init__(self, *args)
        self.logLines = []
        self.startDateTime = util.FmtDate(blue.os.GetTime(), 'ss')
        self.cache = util.KeyVal
        self.cache.cacheTime = 0
        self.cache.minutes = 0
        self.cache.cache = []
        self.lastLoggedLine = 0
        self.lastStartPos = 0
        self.columnNames = ('dateTime', 'pyDateTime', 'procCpu', 'threadCpu', 'blueMem', 'pyMem', 'virtualMem', 'runnable1', 'runnable2', 'watchdog time', 'spf')



    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        uthread.new(self.RunWorkerProcesses).context = 'svc.processHealth'



    def GetSeriesNames(self):
        names = []
        if len(self.logLines) > 0:
            names = self.logLines[0].keys()
            if names.count('dateTime') > 0:
                names.remove('dateTime')
        names.extend(['procCpu',
         'threadCpu',
         'blueMem',
         'pyMem',
         'virtualMem',
         'runnable1',
         'runnable2',
         'watchdog time',
         'spf'])
        return names



    def GetSessionCount(self):
        allsc = base.GetSessions()
        sc = len(filter(lambda x: x.userid is not None and hasattr(x, 'clientID'), allsc))
        return sc



    def FindClosestPythonLine(self, blueLine, startPos = 0):
        logLinesCopy = copy.copy(self.logLines)
        if len(logLinesCopy) == 0:
            return (None, 0)
        if blueLine['dateTime'] <= logLinesCopy[0]['pyDateTime']:
            return (logLinesCopy[0], 0)
        if blueLine['dateTime'] > logLinesCopy[-1]['pyDateTime']:
            return (logLinesCopy[-1], len(logLinesCopy))
        for line in xrange(startPos, len(logLinesCopy) - 1):
            blue.pyos.BeNice()
            t1 = logLinesCopy[line]['pyDateTime']
            t2 = logLinesCopy[(line + 1)]['pyDateTime']
            if t1 <= blueLine['dateTime'] < t2:
                return (logLinesCopy[line], line)

        return (None, 0)



    def GetBlueDataAsDictList(self, minutes = 0):
        data = bluepy.GetBlueInfo(minutes, isYield=False)
        ret = []
        for i in xrange(0, len(data.timeData)):
            (fps, nrRunnable1, nrYielders, nrSleepers, watchDogTime, nrRunnable2,) = data.schedData[i]
            spf = 1.0 / fps if fps > 0.1 else 0
            ret.append({'dateTime': data.timeData[i],
             'procCpu': data.procCpuData[i],
             'threadCpu': data.threadCpuData[i],
             'blueMem': data.bluememData[i],
             'pyMem': data.pymemData[i],
             'virtualMem': data.memData[i],
             'runnable1': nrRunnable1,
             'runnable2': nrRunnable2,
             'watchdog time': watchDogTime,
             'spf': spf})

        return ret



    def GetProcessInfo(self, minutes = 0, useIncrementalStartPos = False):
        if blue.os.GetTime() - self.cache.cacheTime < 25 * const.SEC and self.cache.minutes == minutes:
            return self.cache.cache
        blueLines = self.GetBlueDataAsDictList(minutes)
        lastLine = {}
        if useIncrementalStartPos:
            startPos = self.lastStartPos
        else:
            startPos = 0
        for blueLine in blueLines:
            (pyLine, startPos,) = self.FindClosestPythonLine(blueLine, startPos)
            if pyLine:
                lastLine = pyLine
                blueLine.update(pyLine)
            else:
                blueLine.update(lastLine)

        self.lastStartPos = startPos
        self.cache.minutes = minutes
        self.cache.cacheTime = blue.os.GetTime()
        self.cache.cache = blueLines
        return blueLines



    def RunWorkerProcesses(self):
        seconds = 0
        while self.state == service.SERVICE_RUNNING:
            if prefs.GetValue('disableProcessHealthService', 0):
                self.LogWarn('Process Health Service is disabled in prefs. Disabling loop.')
                return 
            blue.pyos.synchro.Sleep(10000)
            try:
                seconds += 10
                self.DoOnceEvery10Secs()
                if seconds % 600 == 0:
                    self.DoOnceEvery10Minutes()
            except:
                log.LogException()
                sys.exc_clear()




    def LogCpuMemNet(self):
        stats = _socket.getstats()
        netBytesRead = stats['BytesReceived']
        netBytesWritten = stats['BytesSent']
        netReadCalls = stats['PacketsReceived']
        netWriteCalls = stats['PacketsSent']
        sessionCount = self.GetSessionCount()
        logline = {'pyDateTime': blue.os.GetTime(),
         'bytesReceived': netBytesRead,
         'bytesSent': netBytesWritten,
         'packetsReceived': netReadCalls,
         'packetsSent': netWriteCalls,
         'sessionCount': sessionCount}
        self.logLines.append(logline)



    def DoOnceEvery10Secs(self):
        self.LogCpuMemNet()



    def DoOnceEvery10Minutes(self):
        self.WriteLog(20, True)



    def FormatLog(self, logLines):
        txt = ''
        allColumnNames = self.columnNames + tuple(sorted(set(logLines[0].iterkeys()).difference(self.columnNames)))
        if self.lastLoggedLine == 0:
            for name in allColumnNames:
                txt += '%s\t' % name

            txt += '\n'
        for l in xrange(0, len(logLines) - 1):
            logLine = logLines[l]
            if logLine['dateTime'] > self.lastLoggedLine:
                self.lastLoggedLine = logLine['dateTime']
                for name in allColumnNames:
                    if name in ('dateTime', 'pyDateTime'):
                        txt += '%s\t' % util.FmtDate(logLine[name])
                    elif round(logLine[name], 2).is_integer():
                        txt += '%s\t' % str(logLine[name])
                    else:
                        txt += '%.4f\t' % logLine[name]

                txt += '\n'

        return txt



    def WriteLog(self, minutes = 0, useIncrementalStartPos = False):
        dumpPath = prefs.GetValue('ProcessHealthLogPath', None)
        if dumpPath is None:
            self.LogInfo('Will not dump processhealth info since it is not configured in prefs (ProcessHealthLogPath)')
            return 
        computerName = blue.pyos.GetEnv().get('COMPUTERNAME', 'unknown')
        nodeID = sm.GetService('machoNet').GetNodeID()
        if nodeID is None:
            nodeID = boot.role
        logLines = self.GetProcessInfo(minutes, useIncrementalStartPos)
        txt = self.FormatLog(logLines)
        if not os.path.exists(dumpPath):
            os.mkdir(dumpPath)
        fileName = 'PHS %s %s %s.txt' % (computerName, nodeID, self.startDateTime)
        fileName = os.path.join(dumpPath, fileName.replace(':', '.').replace(' ', '.'))
        f = open(fileName, 'a+')
        f.write(txt)
        f.close()
        self.LogInfo('Finished writing out %s entries from processHealth into %s' % (len(logLines), fileName))




