import service
import blue
import uthread
import copy
import log
import sys
import util
import types
from functools import partial

class InformationGatheringSvc(service.Service):
    __guid__ = 'svc.infoGatheringSvc'
    serviceName = 'svc.infoGatheringSvc'
    __exportedcalls__ = {'LogInfoEvent': [],
     'GetEventIGSHandle': []}
    __dependencies__ = ['machoNet']

    def __init__(self):
        service.Service.__init__(self)
        self.isEnabled = None
        self.serverEvents = set()
        self.serverOncePerRunEvents = set()
        self.infoTypeParameters = set()
        self.logTypeAggregates = {}
        self.isEnabled = 0
        self.loggedEvents = {}
        self.loggedEventsEmpty = {}
        self.aggregateDict = {}
        self.clientWorkerInterval = 0



    def Run(self, memStream = None):
        stateAndConfig = sm.RemoteSvc('infoGatheringMgr').GetStateAndConfig()
        self.isEnabled = stateAndConfig.isEnabled
        self.serverEvents = stateAndConfig.infoTypes
        self.clientWorkerInterval = stateAndConfig.clientWorkerInterval
        self.serverOncePerRunEvents = stateAndConfig.infoTypesOncePerRun
        self.logTypeAggregates = stateAndConfig.infoTypeAggregates
        self.infoTypeParameters = stateAndConfig.infoTypeParameters
        self.loggedEvents = {}
        if self.isEnabled and self.clientWorkerInterval > 0:
            self.SendInfoWorkerThread = uthread.new(self.SendInfoWorker)
        self.state = service.SERVICE_RUNNING



    def GetEventIGSHandle(self, eventTypeID, **keywords):
        return partial(self.LogInfoEvent, eventTypeID=eventTypeID, **keywords)



    def LogInfoEvent(self, eventTypeID, itemID = None, itemID2 = None, int_1 = None, int_2 = None, int_3 = None, char_1 = None, char_2 = None, char_3 = None, float_1 = None, float_2 = None, float_3 = None):
        try:
            if eventTypeID in self.serverEvents:
                if eventTypeID in self.serverOncePerRunEvents:
                    self.serverOncePerRunEvents.remove(eventTypeID)
                    self.serverEvents.remove(eventTypeID)
                if eventTypeID not in self.loggedEvents:
                    if eventTypeID in self.logTypeAggregates:
                        self.aggregateDict[eventTypeID] = {}
                    self.loggedEvents[eventTypeID] = []
                if eventTypeID in self.logTypeAggregates:
                    if itemID2 is not None:
                        itemID2 = long(itemID2)
                    ln = [util.FmtDate(blue.os.GetTime(), 'ss'),
                     long(itemID),
                     itemID2,
                     int_1,
                     int_2,
                     int_3,
                     char_1,
                     char_2,
                     char_3,
                     float_1,
                     float_2,
                     float_3]
                    aggregatePath = self.aggregateDict[eventTypeID]
                    aggregatePathOld = None
                    lastKey = None
                    for key in self.logTypeAggregates[eventTypeID]:
                        aggregatePathOld = aggregatePath
                        if ln[key] not in aggregatePath:
                            aggregatePath[ln[key]] = {}
                        aggregatePath = aggregatePath[ln[key]]
                        lastKey = ln[key]

                    if not len(aggregatePath):
                        aggregatePathOld[lastKey] = ln
                        self.loggedEvents[eventTypeID].append(aggregatePathOld[lastKey])
                    else:
                        for i in self.infoTypeParameters[eventTypeID].difference(self.logTypeAggregates[eventTypeID]):
                            if type(ln[i]) == types.IntType:
                                if aggregatePathOld[lastKey][i] + ln[i] <= const.maxInt:
                                    aggregatePathOld[lastKey][i] = aggregatePathOld[lastKey][i] + ln[i]
                                else:
                                    log.LogException('Integer Overflow error on event! Event discarded: Consider using float!')
                            elif type(ln[i]) == types.LongType:
                                self.LogInfo('IGS Treating aggregate event parameter at idx=', i, 'as Bigint')
                                if aggregatePathOld[lastKey][i] + ln[i] <= const.maxBigint:
                                    aggregatePathOld[lastKey][i] = aggregatePathOld[lastKey][i] + ln[i]
                                else:
                                    log.LogException('Integer Overflow error on event! Event discared: Consider using float!')
                            elif type(ln[i]) == types.FloatType:
                                aggregatePathOld[lastKey][i] = aggregatePathOld[lastKey][i] + ln[i]
                            elif i > 0:
                                log.LogException('IGS received data of unhandled datatype!')

                else:
                    self.loggedEvents[eventTypeID].append([util.FmtDate(blue.os.GetTime(), 'ss'),
                     itemID,
                     itemID2,
                     int_1,
                     int_2,
                     int_3,
                     char_1,
                     char_2,
                     char_3,
                     float_1,
                     float_2,
                     float_3])
        except Exception:
            log.LogException('Error logging IGS information')
            sys.exc_clear()



    def SendInfoWorker(self):
        while self.isEnabled:
            try:
                eventsToSend = copy.deepcopy(self.loggedEvents)
                self.loggedEvents = {}
                if len(eventsToSend):
                    self.LogInfo('Information Gatherer is shipping collected data over the wire... Interval = %d milliseconds.' % self.clientWorkerInterval)
                    ret = sm.RemoteSvc('infoGatheringMgr').LogInfoEventsFromClient(eventsToSend)
                    for (eventTypeID, status,) in ret.iteritems():
                        if status == const.INFOSERVICE_OFFLINE:
                            self.isEnabled = 0
                            break
                        elif status == const.INFOTYPE_OFFLINE:
                            self.serverEvents.remove(eventTypeID)
                            self.infoTypeParameters.remove(eventTypeID)
                            if eventTypeID in self.serverOncePerRunEvents:
                                self.serverOncePerRunEvents.remove(eventTypeID)
                            if eventTypeID in self.logTypeAggregates:
                                self.logTypeAggregates.remove(eventTypeID)

            except Exception:
                log.LogException('Error while shipping data to server...')
                sys.exc_clear()
            blue.pyos.synchro.Sleep(self.clientWorkerInterval)





