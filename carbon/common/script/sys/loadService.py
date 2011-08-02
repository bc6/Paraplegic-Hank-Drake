from service import *
import types
import blue
import blue.win32
import util
import uthread
import random
import math
from test.pystone import pystones
import itertools
from time import clock

class LoadService(Service):
    __guid__ = 'svc.loadService'
    __displayname__ = 'Load Service'
    __exportedcalls__ = {'Ping': [ROLE_SERVICE | ROLE_PROGRAMMER],
     'GetTotalStats': [ROLE_SERVICE | ROLE_PROGRAMMER],
     'GatherStats': [ROLE_SERVICE | ROLE_PROGRAMMER],
     'StartLoad': [ROLE_PROGRAMMER],
     'StopLoad': [ROLE_SERVICE | ROLE_PROGRAMMER],
     'StartLoadOnAllNodes': [ROLE_SERVICE | ROLE_PROGRAMMER],
     'StopLoadOnAllNodes': [ROLE_SERVICE | ROLE_PROGRAMMER],
     'GetConfig': [ROLE_PROGRAMMER],
     'SetConfig': [ROLE_SERVICE | ROLE_PROGRAMMER],
     'IsRunning': [ROLE_SERVICE | ROLE_PROGRAMMER],
     'RemainingTime': [ROLE_SERVICE | ROLE_PROGRAMMER],
     'Calibrate': [ROLE_SERVICE | ROLE_PROGRAMMER]}
    __dependencies__ = ['machoNet']
    __notifyevents__ = []

    def __init__(self):
        Service.__init__(self)
        self.configVariables = ['pyStoneTasklets',
         'pyStonesPerSec',
         'pyStonesPerUnit',
         'netTasklets',
         'packetsP2S',
         'packetsS2P',
         'packetsS2S']
        self.pyStoneTasklets = 10
        self.pyStonesPerSec = 20000
        self.pyStonesPerUnit = 500
        self.netTasklets = 5
        self.packetsP2S = 150
        self.packetsS2P = 75
        self.packetsS2S = 50
        self.running = False
        self.ResetCounters()



    def GetConfig(self):
        return dict([ (v, getattr(self, v)) for v in self.configVariables ])



    def SetConfig(self, conf, updateOtherNodes = True):
        for v in self.configVariables:
            if v in conf:
                setattr(self, v, conf[v])

        if updateOtherNodes:
            for node in self.machoNet.GetConnectedNodes():
                self.session.ConnectToRemoteService('loadService', node).SetConfig(conf, False)




    def IsRunning(self):
        return self.running



    def RemainingTime(self):
        if self.duration is not None:
            return self.duration - (blue.os.GetTime() * 1e-07 - self.startTime)



    def StartLoadOnAllNodes(self, duration = None):
        self.session.ConnectToAllServices('loadService').StartLoad(duration)



    def StopLoadOnAllNodes(self):
        self.session.ConnectToAllServices('loadService').StopLoad()



    def TaskletWrap(self, func):

        def Wrapped(*args, **kwds):
            try:
                func(*args, **kwds)

            finally:
                self.nTasklets -= 1
                blue.pyos.synchro.Sleep(0)



        self.nTasklets += 1
        return Wrapped



    def StartLoad(self, duration = None):
        self.running = True
        self.startProcessTime = blue.pyos.taskletTimer.GetProcessTimes()
        self.startThreadTime = blue.pyos.taskletTimer.GetThreadTimes()
        self.ResetCounters()
        self.nTasklets = 0
        for t in range(self.pyStoneTasklets):
            uthread.worker('loadServiceService::CpuLoad::%s' % t, self.TaskletWrap(self.CpuCycleWorker))

        for t in range(self.netTasklets):
            uthread.worker('loadServiceService::NetworkTraffic::%s' % t, self.TaskletWrap(self.Network))

        self.startTime = blue.os.GetTime() * 1e-07
        self.duration = duration
        if duration:
            uthread.worker('loadServiceService::ShutdownCounter', self.ShutdownCounter, duration)



    def ShutdownCounter(self, duration):
        blue.pyos.synchro.Sleep(int(duration * 1000))
        self.StopLoad()



    def StopLoad(self):
        self.running = False
        while self.nTasklets:
            self.LogInfo('Waiting for %d tasklets to finish' % self.nTasklets)
            blue.pyos.synchro.Yield()

        self.LogInfo('All tasklets finished')
        endProcessTime = blue.pyos.taskletTimer.GetProcessTimes()
        endThreadTime = blue.pyos.taskletTimer.GetThreadTimes()
        for (k, v,) in self.startProcessTime.iteritems():
            endProcessTime[k] -= v

        for (k, v,) in self.startThreadTime.iteritems():
            endThreadTime[k] -= v

        self.cpuStats['process'] = endProcessTime
        self.cpuStats['thread'] = endThreadTime



    def IntervalDispatcher(self, interval, stats, func):

        def times(dt):
            start = clock()
            for i in itertools.count():
                yield start + (i + random.random()) * dt



        loopCount = 0
        slowCount = 0
        if interval:
            i = times(interval)
            while self.running:
                now = clock()
                when = i.next()
                ms = int((when - now) * 1000)
                if ms > 0:
                    blue.pyos.synchro.Sleep(ms)
                    now = clock()
                if now > when + interval:
                    slowCount += 1
                    while now > when + interval:
                        when = i.next()

                func()
                loopCount += 1

        else:
            while self.running:
                func()
                loopCount += 1

        stats['loopCount'] += loopCount
        stats['slowCount'] += slowCount
        self.LogInfo('IntervalDispatcher finished. %s of %s %s calls were slow (%s%%)' % (slowCount,
         loopCount,
         func.__name__,
         int(slowCount / float(loopCount) * 100)))



    def Calibrate(self, duration = 2):
        startTime = blue.os.GetTime(1)
        stepCount = 0
        while blue.os.GetTime(1) - startTime < duration * 10000000:
            stepCount += 1
            pystones(self.pyStonesPerUnit)

        return int(stepCount * self.pyStonesPerUnit / duration)



    def CpuCycleWorker(self):
        taskletLoad = float(self.pyStonesPerSec) / self.pyStoneTasklets
        interval = 1.0 / (taskletLoad / self.pyStonesPerUnit)
        self.LogInfo('CPU Tasklet. Will run %s pyStones every %ss' % (self.pyStonesPerUnit, interval))
        blue.pyos.synchro.Sleep(int(random.random() * interval * 1000))

        def CpuWork():
            pystones(self.pyStonesPerUnit)


        self.IntervalDispatcher(interval, self.cpuStats, CpuWork)



    def Network(self):
        if self.machoNet.GetNodeID() > const.maxNodeID:
            solPackets = float(self.packetsP2S) / self.netTasklets
            proxyPackets = 0
        else:
            proxyPackets = float(self.packetsS2P) / self.netTasklets
            solPackets = float(self.packetsS2S) / self.netTasklets
        if solPackets:
            nodes = self.machoNet.GetConnectedSolNodes()
            nodes = [ (node, self.session.ConnectToRemoteService('loadService', node)) for node in nodes ]
            randomNodes = self.NodeRandomizer(nodes)

            def func():
                self.NetworkSendPacket(randomNodes)


            interval = 1.0 / solPackets if solPackets > 0.0 else 0.0
            uthread.worker('loadServiceService::NetworkTraffic::ToSolServers', self.TaskletWrap(self.IntervalDispatcher), interval, self.netStats, func)
        if proxyPackets:
            nodes = self.machoNet.GetConnectedProxyNodes()
            nodes = [ (node, self.session.ConnectToRemoteService('loadService', node)) for node in nodes ]
            randomNodes = self.NodeRandomizer(nodes)

            def func():
                self.NetworkSendPacket(randomNodes)


            interval = 1.0 / proxyPackets if proxyPackets > 0.0 else 0.0
            uthread.worker('loadServiceService::NetworkTraffic::ToProxyServers', self.TaskletWrap(self.IntervalDispatcher), interval, self.netStats, func)



    def NetworkSendPacket(self, randomNodes):
        PACKET_SIZE = 20
        PACKET_VAR = 2
        packet = range(int(random.gauss(PACKET_SIZE, PACKET_VAR)))
        try:
            (node, conn,) = randomNodes.next()
        except StopIteration:
            self.LogWarn('No nodes returned from randomNodes')
            return 
        packetSendTime = blue.os.GetTime(1)
        conn.Ping(packet)
        packetReceiveTime = blue.os.GetTime(1)
        self.UpdateNetworkStats(node, packetReceiveTime - packetSendTime)



    def NodeRandomizer(self, nodes):
        if not nodes:
            return 
        nodes = nodes[:]
        while True:
            random.shuffle(nodes)
            for node in nodes:
                yield node





    def Ping(self, packet):
        return packet



    def ResetCounters(self):
        self.cpuStats = {'loopCount': 0,
         'slowCount': 0,
         'pyStonesPerSec': 0}
        self.netStats = {'loopCount': 0,
         'slowCount': 0}
        self.totalStats = {}



    def UpdateNetworkStats(self, node, latency):
        if node not in self.netStats:
            self.netStats[node] = {}
            self.netStats[node]['totalPackets'] = 0
            self.netStats[node]['totalLatency'] = 0
            self.netStats[node]['totalLatencySq'] = 0
            self.netStats[node]['maxLatency'] = None
            self.netStats[node]['minLatency'] = None
        stats = self.netStats[node]
        latency *= 1e-07
        stats['totalPackets'] += 1
        stats['totalLatency'] += latency
        stats['totalLatencySq'] += latency * latency
        if stats['maxLatency'] is None:
            stats['maxLatency'] = stats['minLatency'] = latency
        elif latency > stats['maxLatency']:
            stats['maxLatency'] = latency
        elif latency < stats['minLatency']:
            stats['minLatency'] = latency



    def GetNetworkStats(self):
        for node in self.netStats:
            if node in ('loopCount', 'slowCount'):
                continue
            self.netStats[node]['average'] = self.netStats[node]['totalLatency'] / self.netStats[node]['totalPackets']
            self.netStats[node]['stdev'] = math.sqrt((self.netStats[node]['totalLatencySq'] - self.netStats[node]['totalLatency'] * self.netStats[node]['average']) / self.netStats[node]['totalPackets'])

        return self.netStats



    def GetCpuStats(self):
        for stats in self.cpuStats.values():
            if type(stats) is not dict:
                continue
            if 'cpu' in stats and 'wallclock' in stats:
                stats['cpuPercentage'] = float(stats['cpu']) / stats['wallclock'] * 100

        if 'loopCount' in self.cpuStats and 'process' in self.cpuStats:
            self.cpuStats['pyStonesPerSec'] = self.pyStonesPerUnit * self.cpuStats['loopCount'] / (self.cpuStats['process']['wallclock'] * 1e-07)
        return self.cpuStats



    def GetTotalStats(self):
        return {'cpu': dict(self.GetCpuStats()),
         'net': dict(self.GetNetworkStats())}



    def GatherStats(self):
        for node in self.machoNet.GetConnectedNodes():
            self.totalStats[node] = self.machoNet.ConnectToRemoteService('loadService', node).GetTotalStats()

        self.totalStats[self.machoNet.GetNodeID()] = self.GetTotalStats()
        return self.totalStats




