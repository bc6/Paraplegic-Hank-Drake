import blue
import service
import uthread
import util
import types
import log
from collections import defaultdict
from service import ROLE_SERVICE, ROLE_ADMIN, ROLE_PROGRAMMER
globals().update(service.consts)

def CurrentTimeString():
    (year, month, weekday, day, hour, minute, second, ms,) = util.GetTimeParts()
    line = '%d/%d/%d %d:%d:%d.%d' % (month,
     day,
     year,
     hour,
     minute,
     second,
     ms)
    return line



class Counter:

    def __init__(self, name, parent):
        self.counter = 0
        self.parent = parent
        self.name = name
        self.filename = ''
        import log
        self.logChannel = log.GetChannel('Counters.' + self.name)



    def Add(self, value = 1):
        self.counter += value



    def Dec(self, value = 1):
        self.counter -= value



    def Set(self, value):
        self.counter = value



    def Value(self):
        return self.counter



    def Flush(self):
        self.logChannel.Log(strx(self.Value()), log.LGINFO)




class TrafficCounter(Counter):

    def __init__(self, name, parent):
        Counter.__init__(self, name, parent)
        self.currval = 0
        self.total = 0
        self.minval = 0
        self.maxval = 0
        self.lastcur = 0
        self.lasttot = 0
        self.perfrom = {}
        self.perfrom = defaultdict(lambda : 0)
        self.lastperfrom = {}
        self.lastperfrom = defaultdict(lambda : 0)



    def Add(self, value = 1):
        self.currval += value
        self.total += 1
        if value > self.maxval:
            self.maxval = value
        if (not self.minval or value < self.minval) and value:
            self.minval = value



    def AddFrom(self, nodeID, value = 1):
        self.perfrom[nodeID] += value
        self.Add(value)



    def Dec(self, value = 1):
        raise AttributeError('Dec is cwap on TrafficCounter')



    def Set(self, value):
        raise AttributeError('Set is cwap on TrafficCounter')



    def Current(self):
        return self.currval



    def Count(self):
        return self.total



    def LastFlow(self):
        return self.lastcur



    def LastCount(self):
        return self.lasttot



    def PerSource(self):
        return self.lastperfrom.items()



    def Min(self):
        return self.minval



    def Max(self):
        return self.maxval



    def Value(self):
        if type(self.currval) == types.FloatType:
            avg = 0.0
            if self.total != 0.0:
                avg = float(self.currval / self.total)
            return 'curr=%f, min=%f, max=%f, count=%d, avg=%f' % (self.currval,
             self.minval,
             self.maxval,
             self.total,
             avg)
        else:
            avg = 0
            if self.total != 0:
                avg = long(self.currval / self.total)
            out = 'curr=%d, min=%d, max=%d, count=%d, avg=%d' % (self.currval,
             self.minval,
             self.maxval,
             self.total,
             avg)
            for n in self.perfrom:
                out += ', %s from %s' % (self.perfrom[n], n)

            return out



    def Flush(self):
        self.logChannel.Log(strx(self.Value()), log.LGINFO)
        if self.name == 'dataSent' or self.name == 'dataReceived':
            self.lastcur = self.currval
            self.lasttot = self.total
            self.currval = 0
            self.total = 0
            self.lastperfrom.clear()
            self.lastperfrom = self.perfrom.copy()
            self.perfrom.clear()




class ListCounter(Counter):

    def __init__(self, name, parent):
        Counter.__init__(self, name, parent)
        self.counter = []



    def Add(self, value = 1):
        if len(self.counter) == 0:
            self.counter.append(value)
        else:
            self.counter.append(self.counter[-1] + value)



    def Dec(self, value = 1):
        if len(self.counter) == 0:
            self.counter.append(value)
        else:
            self.counter.append(self.counter[-1] - value)



    def Flush(self):
        Counter.Flush(self)
        self.counter = []



    def Set(self, value):
        self.counter.append(value)



    def Value(self):
        raise RuntimeError('virtual method, must override')




class AvgCounter(ListCounter):

    def __init__(self, name, parent):
        ListCounter.__init__(self, name, parent)



    def Value(self):
        result = 0
        if len(self.counter) == 0:
            result = 0
        else:
            for s in self.counter:
                result += s

            result /= len(self.counter)
        return result




class MaxCounter(ListCounter):

    def __init__(self, name, parent):
        ListCounter.__init__(self, name, parent)



    def Value(self):
        if len(self.counter) == 0:
            return 0
        max = self.counter[0]
        for s in self.counter:
            if s > max:
                max = s

        return max




class MinCounter(ListCounter):

    def __init__(self, name, parent):
        ListCounter.__init__(self, name, parent)



    def Value(self):
        if len(self.counter) == 0:
            return 0
        min = self.counter[0]
        for s in self.counter:
            if s < min:
                min = s

        return min




class CoreCounterService(service.Service):
    __exportedcalls__ = {'CreateCounter': [ROLE_SERVICE | ROLE_ADMIN | ROLE_PROGRAMMER],
     'DestroyCounter': [ROLE_SERVICE | ROLE_ADMIN | ROLE_PROGRAMMER],
     'GetCounter': [ROLE_SERVICE | ROLE_ADMIN | ROLE_PROGRAMMER],
     'SetFlushInterval': [ROLE_SERVICE | ROLE_ADMIN | ROLE_PROGRAMMER],
     'GetFlushInterval': [ROLE_SERVICE | ROLE_ADMIN | ROLE_PROGRAMMER],
     'StartLogging': [ROLE_SERVICE | ROLE_ADMIN | ROLE_PROGRAMMER],
     'StopLogging': [ROLE_SERVICE | ROLE_ADMIN | ROLE_PROGRAMMER],
     'GetCountersList': [ROLE_SERVICE | ROLE_ADMIN | ROLE_PROGRAMMER],
     'IsLogging': [ROLE_SERVICE | ROLE_ADMIN | ROLE_PROGRAMMER]}
    __guid__ = 'svc.counter'
    __configvalues__ = {'countersInterval': 15,
     'logStart': 0}

    def Run(self, memStream = None):
        self.counters = []
        self.timer = None
        if self.logStart:
            self.StartLogging()



    def GetHtmlStateDetails(self, k, v, detailed):
        import htmlwriter
        if k == 'socket':
            if detailed:
                hd = []
                li = []
                li.append(['Listen Port', 80])
                return (k, htmlwriter.GetTable(hd, li, useFilter=True))
        elif k == 'counters':
            if detailed:
                hd = ['Name',
                 'Value',
                 'Parent',
                 'Filename',
                 'Log Channel']
                li = []
                for each in self.counters:
                    li.append([each.name,
                     each.counter,
                     each.parent,
                     each.filename,
                     each.logChannel])

                return (k, htmlwriter.GetTable(hd, li, useFilter=True))
            else:
                v = ''
                comma = ''
                for each in self.counters:
                    v = v + comma + each.name + '=' + strx(each.counter)
                    comma = ', '

                return (k, v)
        elif k == 'countersInterval':
            desc = 'The time in secounds between logging counter values, assuming that counter logging is started in the first place.'
            if self.logStart:
                desc = 'Thus as the service is currently configured, %d seconds will pass between each log operation' % v
            else:
                desc = 'Thus if you would enable counter logging, %d seconds would pass between each log operation as the service is currently configured.' % v
            return ('Counter Interval', desc)
        if k == 'logStart':
            desc = 'Whether or not counter logging should be started up when the service is started.  If 0, then logging will not be started, otherwise it will be.  '
            if v:
                desc = desc + 'The counter service is currently configured in such a manner that logging will be started'
            else:
                desc = desc + 'The counter service is currently configured in such a manner that logging will <b>not</b> be started'
            return ('Start Logging?', desc)



    def Stop(self, memStream):
        pass



    def Flush(self):
        for s in self.counters:
            s.Flush()




    def FindCounter(self, name):
        for s in self.counters:
            if s.name == name:
                return s




    def CreateCounter(self, name, type = 'normal'):
        counter = self.FindCounter(name)
        if counter:
            return counter
        if type == 'normal':
            counter = Counter(name, self)
        elif type == 'traffic':
            counter = TrafficCounter(name, self)
        elif type == 'avg':
            counter = AvgCounter(name, self)
        elif type == 'max':
            counter = MaxCounter(name, self)
        else:
            raise RuntimeError('Countertype %s not supported' % type)
        self.counters.append(counter)
        return counter



    def AddCounter(self, counter):
        self.counters.append(counter)



    def GetCounter(self, name):
        for s in self.counters:
            if s.name == name:
                return s




    def DestroyCounter(self, name):
        found = None
        for s in self.counters:
            if s.name == name:
                found = s
                break

        if found != None:
            self.counters.remove(found)



    def StartLogging(self):
        uthread.new(self.StartLogging_thread).context = 'counterService::FlushDaemon'



    def StartLogging_thread(self):
        self.logStart = 1
        while 1:
            blue.pyos.synchro.Sleep(self.countersInterval * 1000)
            if not self.logStart:
                return 
            self.Flush()




    def StopLogging(self):
        self.logStart = 0



    def IsLogging(self):
        return self.logStart



    def GetFlushInterval(self):
        return self.countersInterval



    def SetFlushInterval(self, interval):
        self.countersInterval = interval



    def GetCountersList(self):
        titleList = []
        valueList = []
        for s in self.counters:
            titleList.append(s.name)
            valueList.append(s.Value())

        return (titleList, valueList)




