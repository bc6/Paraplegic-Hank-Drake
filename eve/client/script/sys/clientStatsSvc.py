import service
import sys
import os
import blue
import cPickle
import uthread
import collections
import log
from clientStatsCommon import *

class ClientStatsSvc(service.Service):
    __guid__ = 'svc.clientStatsSvc'
    __notifyevents__ = ['OnClientReady',
     'OnDisconnect',
     'OnProcessLoginProgress',
     'ProcessShutdown']
    __displayname__ = 'Client Statistics Service'
    __dependencies__ = ['machoNet']

    def __init__(self):
        service.Service.__init__(self)
        self.entries = {}
        self.currentState = STATE_STARTUP
        self.version = 2
        self.stateMask = 0
        self.lastStageSampleTime = blue.win32.QueryPerformanceCounter()
        self.hasEnteredGame = 0
        self.hasProcessedExit = False
        self.fileStarted = False
        self.filename = os.path.join(blue.os.ResolvePathForWriting(u'cache:/clientStats.dat'))
        if os.path.exists(self.filename):
            setattr(self, 'prevContents', self.ReadFile(self.filename))
        else:
            self.SampleStats(STATE_UNINITIALIZEDSTART)



    def Run(self, memStream = None):
        self.state = service.SERVICE_RUNNING
        self.SampleStats(STATE_STARTUP)



    def Stop(self, ms):
        self.LogInfo('ClientStatsSvc::Stop - Sampling')
        self.OnProcessExit()
        self.LogInfo('ClientStatsSvc::Stop - DONE')
        service.Service.Stop(self)



    def ReadFile(self, filename):
        try:
            try:
                filein = file(filename, 'r')
                datain = cPickle.load(filein)
                return datain
            except Exception as e:
                log.LogException('Error reading file')
                sys.exc_clear()

        finally:
            filein.close()




    def SendContentsToServer(self, contents = None):
        try:
            if not sm.services['machoNet'].IsConnected():
                return 
        except:
            sys.exc_clear()
            return 
        if contents is None:
            contents = self.prevContents
        if contents[0] != self.version:
            contents = {}
        else:
            contents = contents[1]
        build = boot.GetValue('build', None)
        contentType = CONTENT_TYPE_PREMIUM
        operatingSystem = PLATFORM_WINDOWS
        if blue.win32.IsTransgaming():
            operatingSystem = PLATFORM_MACOS
        blendedContents = self.entries
        blendedStateMask = self.stateMask
        self.entries = dict()
        self.stateMask = 0
        if contents.has_key(STATE_DISCONNECT):
            blendedContents[STATE_DISCONNECT] = contents[STATE_DISCONNECT]
            blendedStateMask += STATE_DISCONNECT
        if contents.has_key(STATE_GAMESHUTDOWN):
            blendedContents[STATE_GAMESHUTDOWN] = contents[STATE_GAMESHUTDOWN]
            blendedStateMask += STATE_GAMESHUTDOWN
        header = (self.version,
         blendedStateMask,
         build,
         operatingSystem,
         contentType)
        data = (header, blendedContents)
        try:
            uthread.Lock(self, 'sendContents')
            sm.RemoteSvc('clientStatsMgr').SubmitStats(data)
            if hasattr(self, 'prevContents'):
                delattr(self, 'prevContents')
            return True

        finally:
            uthread.UnLock(self, 'sendContents')




    def Persist(self):
        if not self.fileStarted and os.path.exists(self.filename):
            os.remove(self.filename)
        outfile = file(self.filename, 'w')
        data = (self.version, self.entries)
        cPickle.dump(data, outfile)
        self.fileStarted = True



    def SampleStats(self, state):
        self.currentState = state
        try:
            try:
                uthread.Lock(self, 'sampleStats')
                if self.entries.has_key(state):
                    stats = self.entries[state]
                else:
                    stats = {}
                lastStageSampleTime = self.lastStageSampleTime
                self.lastStageSampleTime = blue.win32.QueryPerformanceCounter()
                stats[STAT_TIME_SINCE_LAST_STATE] = (self.lastStageSampleTime - lastStageSampleTime) / (blue.win32.QueryPerformanceFrequency() / 1000)
                if state < STATE_GAMEEXITING:
                    stats[STAT_MACHONET_AVG_PINGTIME] = self.GetMachoPingTime()
                if len(blue.pyos.cpuUsage) > 0:
                    memdata = blue.pyos.cpuUsage[-1][2]
                    if len(memdata) >= 2:
                        stats[STAT_PYTHONMEMORY] = memdata[0]
                    else:
                        stats[STAT_PYTHONMEMORY] = 0L
                else:
                    stats[STAT_PYTHONMEMORY] = 0L
                cpuProcessTime = blue.win32.GetProcessTimes()
                cpuProcessTime = cpuProcessTime[2] + cpuProcessTime[3]
                stats[STAT_CPU] = cpuProcessTime
                self.entries[state] = stats
                self.stateMask = self.stateMask + state
                if not hasattr(self, 'prevContents'):
                    self.Persist()
            except Exception as e:
                log.LogException('Error while sampling clientStats')
                sys.exc_clear()

        finally:
            uthread.UnLock(self, 'sampleStats')




    def GetMachoPingTime(self):
        if sm.services['machoNet'] is not None and sm.services['machoNet'].IsConnected():
            numSamples = 5
            totalTime = 0
            for i in range(numSamples):
                stat = sm.services['machoNet'].Ping(1, silent=True)
                startTime = stat[0][1]
                endTime = stat[-1][1]
                took = endTime - startTime
                totalTime += took
                blue.pyos.BeNice()

            return totalTime / numSamples
        else:
            return -1



    def OnProcessExit(self):
        if not self.hasProcessedExit:
            self.SampleStats(STATE_GAMESHUTDOWN)
            self.hasProcessedExit = True



    def OnClientReady(self, *args):
        if args[0] == 'login':
            self.SampleStats(STATE_LOGINWINDOW)
        elif args[0] == 'charsel':
            self.SampleStats(STATE_CHARSELECTION)
        elif (args[0] == 'inflight' or args[0] == 'station') and not self.hasEnteredGame:
            self.SampleStats(STATE_GAMEENTERED)
            self.hasEnteredGame = 1
            if hasattr(self, 'prevContents'):
                uthread.new(self.SendContentsToServer)



    def OnLoginStarted(self):
        self.SampleStats(STATE_LOGINSTARTED)



    def OnDisconnect(self, reason = 0, msg = ''):
        self.SampleStats(STATE_DISCONNECT)



    def OnProcessLoginProgress(self, *args):
        if args[0] == 'loginprogress::gettingbulkdata' and STATE_BULKDATASTARTED not in self.entries:
            self.SampleStats(STATE_BULKDATASTARTED)
        elif args[0] == 'loginprogress::gettingbulkdata' and STATE_BULKDATASTARTED in self.entries and args[2] == args[3]:
            self.SampleStats(STATE_BULKDATADONE)
        elif args[0] == 'loginprogress::done':
            self.SampleStats(STATE_LOGINDONE)
        elif args[0] == 'loginprogress::connecting':
            self.SampleStats(STATE_LOGINSTARTED)



    def ProcessShutdown(self):
        self.OnProcessExit()



    def OnFatalDesync(self):
        if not self.entries.has_key(self.currentState):
            self.entries[self.currentState] = {}
        if self.entries[self.currentState].has_key(STAT_FATAL_DESYNCS):
            self.entries[self.currentState][STAT_FATAL_DESYNCS] += 1
        else:
            self.entries[self.currentState][STAT_FATAL_DESYNCS] = 1



    def OnRecoverableDesync(self):
        if not self.entries.has_key(self.currentState):
            self.entries[self.currentState] = {}
        if self.entries[self.currentState].has_key(STAT_RECOVERABLE_DESYNCS):
            self.entries[self.currentState][STAT_RECOVERABLE_DESYNCS] += 1
        else:
            self.entries[self.currentState][STAT_RECOVERABLE_DESYNCS] = 1




