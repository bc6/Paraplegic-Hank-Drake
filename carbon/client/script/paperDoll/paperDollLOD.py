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

class LodQueue:
    __guid__ = 'paperDoll.LodQueue'
    instance = None

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
        uthread.new(LodQueue.QueueMonitorThread, weakref.ref(self))



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
            busyCount = self.UpdateQueue(wakeUpTime)
            maxBusy = PD.PerformanceOptions.maxLodQueueActive
            scan = 0
            max = len(self.queue)
            while busyCount < maxBusy and scan < max:
                doll = self.queue[scan].doll()
                if doll is not None and not doll.busyUpdating:
                    if self.ProcessRequest(self.queue[scan]):
                        busyCount = busyCount + 1
                scan = scan + 1





    def UpdateQueue(self, wakeUpTime):
        i = 0
        busy = 0
        while i < len(self.queue):
            doll = self.queue[i].doll()
            factory = self.queue[i].factory()
            avatar = self.queue[i].avatar.object
            if doll is None:
                self.queue.pop(i)
            elif doll.busyUpdating:
                busy = busy + 1
                i = i + 1
            elif doll.overrideLod == self.queue[i].lodWanted:
                q = self.queue.pop(i)
                if PD.PerformanceOptions.logLodPerformance:
                    log.LogInfo('LOD switch to', q.lodWanted, 'took', wakeUpTime - q.timeUpdateStarted, 'secs; wait in queue', q.timeUpdateStarted - q.timeAddToQueue, 'secs')
            else:
                i = i + 1

        return busy



    def AddToQueue(self, avatarBluePythonWeakRef, dollWeakref, factoryWeakref, lodWanted):
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



    def ProcessRequest(self, queueEntry):
        doll = queueEntry.doll()
        factory = queueEntry.factory()
        avatar = queueEntry.avatar.object
        if doll is None or factory is None or avatar is None:
            return False
        if doll.overrideLod == queueEntry.lodWanted:
            return False
        if doll.overrideLod != queueEntry.lodWanted:
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
            stub = blue.os.LoadObject(LoadingStubPath)
    if hasattr(stub, 'visualModel'):
        stub = stub.visualModel

    class InPlaceBuilder:

        def __init__(self, avatar, doll, factory, stub):
            self.avatar = blue.BluePythonWeakRef(avatar)
            self.doll = weakref.ref(doll)
            self.factory = weakref.ref(factory)
            doll.overrideLod = 99

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

