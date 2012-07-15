#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/paperDoll/paperDollLOD.py
import blue
import trinity
import paperDoll as PD
import uthread
import weakref
import log
import sys
import util
import locks
import time
LoadingStubPath = 'res:/Graphics/Character/Global/LowLODs/Female/BasicFemale/BasicFemale.red'

class LodQueue(object):
    __guid__ = 'paperDoll.LodQueue'
    instance = None
    magicLOD = 99

    class QueueEntry:

        def __init__(self, avatarBluePythonWeakRef, dollWeakref, factoryWeakref, lodWanted):
            self.avatar = avatarBluePythonWeakRef
            self.doll = dollWeakref
            self.factory = factoryWeakref
            self.lodWanted = lodWanted
            self.timeAddToQueue = time.time()
            self.timeUpdateStarted = 0

    def __init__(self):
        self.queue = []
        self.inCallback = False
        self.updateEvent = locks.Event(name='LodQueueEvent')
        self.__freezeQueue = False
        uthread.new(LodQueue.QueueMonitorThread, weakref.ref(self))
        self.queueSizeStat = blue.statistics.Find('paperDoll/queueSize')
        if not self.queueSizeStat:
            self.queueSizeStat = blue.CcpStatisticsEntry()
            self.queueSizeStat.name = 'paperDoll/queueSize'
            self.queueSizeStat.type = 1
            self.queueSizeStat.resetPerFrame = False
            self.queueSizeStat.description = 'The length of the LOD switching queue'
            blue.statistics.Register(self.queueSizeStat)
        self.queueActiveUpStat = blue.statistics.Find('paperDoll/queueActiveUp')
        if not self.queueActiveUpStat:
            self.queueActiveUpStat = blue.CcpStatisticsEntry()
            self.queueActiveUpStat.name = 'paperDoll/queueActiveUp'
            self.queueActiveUpStat.type = 1
            self.queueActiveUpStat.resetPerFrame = False
            self.queueActiveUpStat.description = 'Number of LOD switches to higher quality in progress'
            blue.statistics.Register(self.queueActiveUpStat)
        self.queueActiveDownStat = blue.statistics.Find('paperDoll/queueActiveDown')
        if not self.queueActiveDownStat:
            self.queueActiveDownStat = blue.CcpStatisticsEntry()
            self.queueActiveDownStat.name = 'paperDoll/queueActiveDown'
            self.queueActiveDownStat.type = 1
            self.queueActiveDownStat.resetPerFrame = False
            self.queueActiveDownStat.description = 'Number of LOD switches to lower quality in progress'
            blue.statistics.Register(self.queueActiveDownStat)

    def getFreezeQueue(self):
        return self.__freezeQueue

    def setFreezeQueue(self, freeze):
        self.__freezeQueue = freeze
        LodQueue.OnDollUpdateDoneStatic()

    freezeQueue = property(getFreezeQueue, setFreezeQueue)

    def __del__(self):
        self.updateEvent.set()

    @staticmethod
    def OnDollUpdateDoneStatic():
        if LodQueue.instance is None:
            return
        LodQueue.instance.updateEvent.set()

    @staticmethod
    def QueueMonitorThread(weakSelf):
        while weakSelf():
            weakSelf().updateEvent.wait()
            wakeUpTime = time.time()
            self = weakSelf()
            if self is None:
                break
            self.updateEvent.clear()
            busyUp, busyDown = self.UpdateQueue(wakeUpTime)
            if not self.__freezeQueue:
                maxBusyUp = PD.PerformanceOptions.maxLodQueueActiveUp
                maxBusyDown = PD.PerformanceOptions.maxLodQueueActiveDown
                scan = 0
                max = len(self.queue)
                while busyDown < maxBusyDown and busyUp < maxBusyUp and scan < max:
                    doll = self.queue[scan].doll()
                    if doll is not None and not doll.busyUpdating:
                        doll = self.queue[scan].doll()
                        goingUp = True
                        if doll is not None:
                            goingUp = self.queue[scan].lodWanted < doll.overrideLod
                        if self.ProcessRequest(self.queue[scan], allowUp=busyUp < maxBusyUp):
                            if goingUp:
                                busyUp = busyUp + 1
                            else:
                                busyDown = busyDown + 1
                    scan = scan + 1

            self.queueActiveUpStat.Set(busyUp)
            self.queueActiveDownStat.Set(busyDown)

    def UpdateQueue(self, wakeUpTime):
        i = 0
        busyUp = 0
        busyDown = 0
        while i < len(self.queue):
            doll = self.queue[i].doll()
            factory = self.queue[i].factory()
            avatar = self.queue[i].avatar.object
            if doll is None:
                self.queue.pop(i)
            elif doll.busyUpdating:
                if doll.previousLOD != LodQueue.magicLOD and doll.previousLOD <= self.queue[i].lodWanted:
                    busyDown = busyDown + 1
                else:
                    busyUp = busyUp + 1
                i = i + 1
            elif doll.overrideLod == self.queue[i].lodWanted:
                q = self.queue.pop(i)
                if PD.PerformanceOptions.logLodPerformance:
                    log.LogInfo('LOD switch to', q.lodWanted, 'took', wakeUpTime - q.timeUpdateStarted, 'secs; wait in queue', q.timeUpdateStarted - q.timeAddToQueue, 'secs')
            else:
                i = i + 1

        self.queueSizeStat.Set(len(self.queue))
        return (busyUp, busyDown)

    def AddToQueue(self, avatarBluePythonWeakRef, dollWeakref, factoryWeakref, lodWanted):
        if type(avatarBluePythonWeakRef) != blue.BluePythonWeakRef:
            avatarBluePythonWeakRef = blue.BluePythonWeakRef(avatarBluePythonWeakRef)
        if type(dollWeakref) != weakref.ref:
            dollWeakref = weakref.ref(dollWeakref)
        if type(factoryWeakref) != weakref.ref:
            factoryWeakref = weakref.ref(factoryWeakref)
        for i in xrange(len(self.queue)):
            q = self.queue[i]
            if q.doll() == dollWeakref() and q.factory() == factoryWeakref() and q.avatar.object == avatarBluePythonWeakRef.object:
                q.lodWanted = lodWanted
                if q.doll().busyUpdating:
                    q.doll().Update(q.factory(), q.avatar.object)
                break
        else:
            entry = self.QueueEntry(avatarBluePythonWeakRef, dollWeakref, factoryWeakref, lodWanted)
            self.queue.append(entry)

        self.updateEvent.set()

    def ProcessRequest(self, queueEntry, allowUp):
        doll = queueEntry.doll()
        factory = queueEntry.factory()
        avatar = queueEntry.avatar.object
        if doll is None or factory is None or avatar is None:
            return False
        if queueEntry.lodWanted == doll.overrideLod:
            return False
        if queueEntry.lodWanted < doll.overrideLod and not allowUp:
            return False
        doll.overrideLod = queueEntry.lodWanted
        doll.AddUpdateDoneListener(LodQueue.OnDollUpdateDoneStatic)
        queueEntry.timeUpdateStarted = time.time()
        doll.Update(factory, avatar)
        return True


def SetupLODFromPaperdoll(avatar, doll, factory, animation, loadStub = True):
    if doll is None or avatar is None:
        return
    stub = None
    if loadStub:
        if type(avatar) == trinity.Tr2IntSkinnedObject:
            stub = blue.resMan.LoadObject(LoadingStubPath)
    if hasattr(stub, 'visualModel'):
        stub = stub.visualModel

    class InPlaceBuilder:

        def __init__(self, avatar, doll, factory, stub):
            self.avatar = blue.BluePythonWeakRef(avatar)
            self.doll = weakref.ref(doll)
            self.factory = weakref.ref(factory)
            doll.overrideLod = LodQueue.magicLOD

            def MakeBuilder(lod):
                lodBuilder = blue.BlueObjectBuilderPython()
                lodBuilder.SetCreateMethod(lambda objectMarker, callingProxy: self.DoCreate(callingProxy, lod))
                lodBuilder.SetSelectedHandler(lambda objectMarker, callingProxy: self.OnSelected(callingProxy, lod))
                proxy = blue.BlueObjectProxy()
                proxy.builder = lodBuilder
                return proxy

            avatar.highDetailModel = MakeBuilder(0)
            avatar.mediumDetailModel = MakeBuilder(1)
            avatar.lowDetailModel = MakeBuilder(2)
            factory.AppendMeshesToVisualModel(avatar.visualModel, stub.meshes)

        def DoCreate(self, callingProxy, lod):
            if self.avatar.object is None:
                return
            return self.avatar.object.visualModel

        def OnSelected(self, callingProxy, lod):
            doll = self.doll()
            factory = self.factory()
            avatar = self.avatar.object
            if doll is None or factory is None or avatar is None:
                return
            if doll.overrideLod != lod:
                if LodQueue.instance is None:
                    doll.overrideLod = lod
                    doll.Update(factory, avatar)
                else:
                    LodQueue.instance.AddToQueue(self.avatar, self.doll, self.factory, lod)

    simpleBuilder = InPlaceBuilder(avatar, doll, factory, stub)


def AbortAllLod(avatar):
    if avatar is None:
        return
    if avatar.highDetailModel is not None:
        avatar.highDetailModel.object = None
    if avatar.mediumDetailModel is not None:
        avatar.mediumDetailModel.object = None
    if avatar.lowDetailModel is not None:
        avatar.lowDetailModel.object = None


exports = util.AutoExports('paperDoll', globals())