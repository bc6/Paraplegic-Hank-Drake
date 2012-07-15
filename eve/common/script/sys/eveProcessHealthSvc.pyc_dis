#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/sys/eveProcessHealthSvc.py
import blue
import svc
import service
import base
import util
import uthread
import log
import sys
import _socket
import datetime
import os

class EveProcessHealthSvc(svc.processHealth):
    __guid__ = 'svc.eveProcessHealth'
    __replaceservice__ = 'processHealth'
    __servicename__ = 'eveProcessHealth'
    __displayname__ = 'Eve Process Health Service'

    def __init__(self, *args):
        svc.processHealth.__init__(self)
        self.columnNames += ('bytesReceived', 'bytesSent', 'packetsReceived', 'packetsSent')
        if boot.role == 'server':
            self.columnNames += ('dogmaLateness', 'maxModules', 'totalModules', 'sessionCount', 'solCount')
        if boot.role != 'client':
            self.columnNames += ('numEvents',)

    def LogDogma(self):
        if boot.role == 'server':
            maxModules = 0
            totalModules = 0
            avgModules = 0
            count = 0
            dogmaLag = [0]
            for bindparam, dogmaLocation in sm.GetService('dogmaIM').boundObjects.items():
                effectList = dogmaLocation.effectTimerList
                count += 1
                if effectList:
                    try:
                        dogmaLag.append(float(effectList[0][0] - blue.os.GetSimTime()) / float(const.SEC))
                    except KeyError:
                        pass

                if len(effectList) > maxModules:
                    maxModules = len(effectList)
                totalModules += len(effectList)

            mostLag = min(0, min(dogmaLag))
            self.logLines[-1].update({'solCount': count,
             'maxModules': maxModules,
             'totalModules': totalModules,
             'dogmaLateness': -1 * mostLag})

    def LogEventCount(self):
        if boot.role != 'client':
            counters = sm.GetService('eventLog').logEventCounter
            num = 0
            for k, v in counters.iteritems():
                num += v[1]

            self.logLines[-1].update({'numEvents': num})

    def DoOnceEvery10Secs(self):
        self.LogCpuMemNet()
        self.LogDogma()
        self.LogEventCount()