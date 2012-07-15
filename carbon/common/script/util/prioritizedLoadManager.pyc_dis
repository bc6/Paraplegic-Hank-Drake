#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/prioritizedLoadManager.py
import log
import service
import stackless
import sys
import uthread

class Heap(object):

    def __init__(self, key):
        self.entries = []
        self.key = key

    def sort(self):
        self.entries.sort(key=self.key)

    def push(self, v):
        self.entries.append(v)

    def pop(self):
        self.sort()
        return self.entries.pop()

    def __contains__(self, o):
        return o in self.entries

    def __len__(self):
        return len(self.entries)

    def clear(self):
        self.entries = []

    def remove(self, o):
        self.entries.remove(o)


class PriorityQueue(Heap):

    def __init__(self):
        Heap.__init__(self, lambda entry: entry.GetPriority())
        self.chan = stackless.channel()

    def put(self, x):
        if self.chan.balance < 0:
            self.chan.send(x)
        else:
            self.push(x)

    def get(self):
        if len(self):
            return self.pop()
        else:
            return self.chan.receive()

    def getAll(self):
        self.sort()
        return reversed(self.entries)


class PrioritizedLoadManager(service.Service):
    __guid__ = 'svc.prioritizedLoadManager'
    MAX_TASKLETS = 4

    def __init__(self, *args, **kwargs):
        service.Service.__init__(self, *args, **kwargs)
        self.queue = PriorityQueue()
        self.requestsByOwner = {}
        self.isRunning = True
        self.tasklets = []
        for i in xrange(self.MAX_TASKLETS):
            tasklet = uthread.new(self.Dispatcher)
            tasklet.context = 'svc.prioritizedLoadManager::Dispatcher'
            self.tasklets.append(tasklet)

    def Stop(self, *args, **kwargs):
        self.isRunning = False
        service.Service.Stop(*args, **kwargs)

    def Add(self, owner, request):
        if owner:
            if owner in self.requestsByOwner:
                self.Cancel(owner)
            request.owner = owner
            self.requestsByOwner[owner] = request
        self.queue.put(request)

    def Cancel(self, owner):
        if owner in self.requestsByOwner:
            request = self.requestsByOwner[owner]
            del self.requestsByOwner[owner]
            self.queue.remove(request)

    def Dispatcher(self):
        while self.isRunning:
            try:
                request = self.queue.get()
                self.ProcessRequest(request)
                request = None
            except StandardError:
                log.LogException()
                sys.exc_clear()

    def ProcessRequest(self, request):
        if request.owner:
            del self.requestsByOwner[request.owner]
        request.Process()

    def GetLoadRequestInfo(self):
        return [ (entry.GetName(), entry.GetPriority()) for entry in self.queue.getAll() ]