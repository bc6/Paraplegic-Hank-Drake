import sys
import trinity
import blue
import bluepy
import uthread
import weakref
import log
import util
import locks
import itertools
lock = locks.RLock()
DEFAULT_PREPASS_RENDERJOB_NAME = 'RenderTestScene'
import paperDoll as PD

class PerformanceTestResults(dict):
    __guid__ = 'paperDoll.testing.PerformanceTestResults'

    def __init__(self, iterable = None):
        dict.__init__(self)
        if iterable:
            if type(iterable) == PerformanceTestResults:
                self.update(iterable)



    def PunchIn(self, key):
        with lock:
            self[key] = blue.os.GetWallclockTime()



    def PunchOut(self, key):
        with lock:
            self[key] = blue.os.TimeDiffInUs(long(self[key]), blue.os.GetWallclockTime()) / 1000.0




class BenchmarkTest(object):
    __guid__ = 'paperDoll.testing.BenchmarkTest'

    def __init__(self):
        self.testTasklet = None
        self.factory = None
        self.scene = None
        self.usePrepass = False
        self.results = PerformanceTestResults()



    def _StartTest(self):
        with lock:
            self.results.PunchIn('Test execution time')



    def _EndTest(self):
        with lock:
            self.results.PunchOut('Test execution time')



    def Execute_t(self, callBack = None):
        with lock:
            self._StartTest()
            self._EndTest()
            if callBack:
                uthread.new(callBack)



    def Execute(self, callBack = None):
        self.results.clear()
        self.testTasklet = uthread.new(self.Execute_t, callBack)
        uthread.schedule(self.testTasklet)



    def GetResult(self):
        return PerformanceTestResults(self.results)




class SingleDollTest(BenchmarkTest):
    __guid__ = 'paperDoll.testing.SingleDollTest'

    def __init__(self, startLOD, endLOD, resPath = None):
        BenchmarkTest.__init__(self)
        self.resPath = resPath
        self.startLOD = startLOD
        self.endLOD = endLOD
        self.lodDelta = (endLOD - startLOD) / abs(endLOD - startLOD) if endLOD != startLOD else 0



    def _StartTest(self):
        BenchmarkTest._StartTest(self)
        pdc = PD.PaperDollCharacter(self.factory)
        pdc.doll = PD.Doll('TestDoll')
        if self.resPath:
            pdc.doll.Load(self.resPath, self.factory)
        pdc.doll.overrideLod = self.startLOD
        spawnKey = 'Spawning doll at LOD {0}'.format(self.startLOD)
        self.results.PunchIn(spawnKey)
        pdc.Spawn(self.scene, usePrepass=self.usePrepass)
        while pdc.doll.busyUpdating:
            PD.Yield()

        self.results.PunchOut(spawnKey)
        while pdc.doll.overrideLod != self.endLOD:
            nextLOD = pdc.doll.overrideLod + self.lodDelta
            spawnKey = 'Switching from LOD {0} to LOD {1}'.format(pdc.doll.overrideLod, nextLOD)
            self.results.PunchIn(spawnKey)
            pdc.doll.overrideLod = nextLOD
            pdc.Update()
            while pdc.doll.busyUpdating:
                PD.Yield()

            self.results.PunchOut(spawnKey)
            PD.Yield()





class MultiDollTest(BenchmarkTest):
    __guid__ = 'paperDoll.testing.MultiDollTest'

    def __init__(self, numChars = 32, maxLOD0 = 8, maxLOD1 = 16, maxLodQueueActive = None, resPaths = None, debugMode = False):
        BenchmarkTest.__init__(self)
        self.debugMode = debugMode
        self.respathsIterator = itertools.cycle(resPaths) if resPaths else None
        self.numChars = numChars
        self.maxLOD0 = maxLOD0
        self.maxLOD1 = maxLOD1
        self.maxLOD2 = numChars - (maxLOD0 + maxLOD1)
        self.maxLodQueueActive = maxLodQueueActive or 1
        self.paperDollCharacters = []
        self.points = []
        PD.LodQueue.instance = PD.LodQueue()
        PD.PerformanceOptions.maxLodQueueActive = self.maxLodQueueActive
        PD.PerformanceOptions.maxLodQueueActiveUp = self.maxLodQueueActive



    def SpawnDolls(self, lod, count):
        for i in xrange(count):
            pdc = PD.PaperDollCharacter(self.factory)
            pdc.disableDel = self.debugMode
            pdc.doll = PD.Doll('TestDoll')
            if self.respathsIterator:
                spawnKey = 'Loading doll #{0} at LOD {1}'.format(i, lod)
                self.results.PunchIn(spawnKey)
                pdc.doll.Load(self.respathsIterator.next(), self.factory)
                self.results.PunchOut(spawnKey)
            spawnKey = 'Spawning doll #{0} at LOD {1} without call to Update'.format(i, lod)
            self.results.PunchIn(spawnKey)
            pdc.Spawn(self.scene, point=self.points.pop(), lod=99999, updateDoll=False, usePrepass=self.usePrepass)
            self.results.PunchOut(spawnKey)
            self.paperDollCharacters.append(pdc)
            avatar = blue.BluePythonWeakRef(pdc.avatar)
            doll = weakref.ref(pdc.doll)
            factory = weakref.ref(pdc.factory)
            PD.LodQueue.instance.AddToQueue(avatar, doll, factory, lod)




    def _StartTest(self):
        BenchmarkTest._StartTest(self)
        self.points = zip(range(self.numChars / 2) * 2, [0] * self.numChars, [0] * (self.numChars / 2) + [1] * (self.numChars / 2))
        self.SpawnDolls(0, self.maxLOD0)
        self.SpawnDolls(1, self.maxLOD1)
        self.SpawnDolls(2, self.maxLOD2)
        PD.Yield()
        while PD.LodQueue.instance.queue:
            PD.Yield()

        if not self.debugMode:
            del self.paperDollCharacters[:]




class Benchmarker(object):
    _guid__ = 'paperDoll.testing.Benchmarker'

    def __init__(self, factory, scene, usePrepass = False, enablePaperDollOptimizations = True):
        if enablePaperDollOptimizations:
            PD.PerformanceOptions.EnableOptimizations()
        self.factory = factory
        self.scene = scene
        self.usePrepass = usePrepass
        self.test = None
        self.clearCacheOnEachIteration = True
        self.iterations = 20
        self.currentIteration = 0
        self.results = PerformanceTestResults()



    def SetTest(self, test):
        self.test = test
        self.currentIteration = 0
        self.results = PerformanceTestResults()
        test.factory = self.factory
        test.scene = self.scene
        test.usePrepass = self.usePrepass



    def ClearCaches(self):
        blue.motherLode.ClearCached()



    def ExecuteTest(self, onTestExecution = None):

        def OnTestEnd():
            result = self.test.GetResult()
            self.results[self.currentIteration] = result
            if self.currentIteration < self.iterations - 1:
                if onTestExecution:
                    onTestExecution(self.test)
                if self.clearCacheOnEachIteration:
                    self.ClearCaches()
                self.test.Execute(callBack=OnTestEnd)
                self.currentIteration += 1


        if onTestExecution:
            onTestExecution(self.test)
        self.results.PunchIn(self.test.__class__)
        if self.clearCacheOnEachIteration:
            self.ClearCaches()
        self.test.Execute(callBack=OnTestEnd)
        while self.currentIteration < self.iterations - 1:
            PD.Yield()

        self.results.PunchOut(self.test.__class__)



    def SetAndExecuteTest(self, test):
        self.SetTest(test)
        self.ExecuteTest()



    def GetAnalyzedResults(self):
        statisticalData = {}
        keys = self.results.keys()
        for key in keys:
            if type(key) == int:
                testIterationResults = self.results[key]
                for testKey in testIterationResults.keys():
                    record = statisticalData.get(testKey, [])
                    record.append(testIterationResults[testKey])
                    statisticalData[testKey] = record

            else:
                statisticalData[key] = self.results[key]

        for key in statisticalData.keys():
            record = statisticalData[key]
            if type(record) is list:
                total = sum(record)
                count = len(record)
                mean = total / count
                maxVal = max(record)
                minVal = min(record)
                sum2 = sum(((x - mean) ** 2 for x in record))
                sum3 = sum((x - mean for x in record))
                try:
                    variance = (sum2 - sum3 ** 2 / count) / (count - 1)
                except ZeroDivisionError:
                    variance = sum2 - sum3 ** 2 / count
                stdDev = variance ** 0.5
                statisticalData[key] = {'count': count,
                 'total': total,
                 'min': minVal,
                 'max': maxVal,
                 'mean': mean,
                 'variance': variance,
                 'stdDev': stdDev}

        return statisticalData




def CreateEmptyScene():
    scene = trinity.Tr2InteriorScene()
    cell = trinity.Tr2InteriorCell()
    cell.isUnbounded = True
    scene.cells.append(cell)
    light1 = trinity.Tr2InteriorLightSource()
    light1.radius = 100.0
    light1.position = (0.0, 15.0, 50.0)
    scene.lights.append(light1)
    light2 = trinity.Tr2InteriorLightSource()
    light2.radius = 100.0
    light2.position = (0.0, 15.0, -50.0)
    scene.lights.append(light2)
    light3 = trinity.Tr2InteriorLightSource()
    light3.radius = 100.0
    light3.position = (50.0, 15.0, 0.0)
    scene.lights.append(light3)
    return scene



def SetupScene(scene = None, sceneFile = None, usePrepass = False):
    trinity.settings.SetValue('useRootCell', False)
    if not sceneFile:
        scene = CreateEmptyScene()
    else:
        scene = blue.os.LoadObject(sceneFile)
    if usePrepass:
        from trinity.sceneRenderJobInterior import CreateSceneRenderJobInterior
        for rj in trinity.device.scheduledRecurring:
            if rj.name == DEFAULT_PREPASS_RENDERJOB_NAME:
                trinity.device.scheduledRecurring.remove(rj)
                break

        rj = CreateSceneRenderJobInterior(DEFAULT_PREPASS_RENDERJOB_NAME)
        rj.lightingLUT = blue.resMan.GetResource('res:/Graphics/Shared_Texture/Global/prepassLightLookup.dds')
        rj.fresnelLUT = blue.resMan.GetResource('res:/Graphics/Shared_Texture/Global/prepassLightLookupFresnel.dds')
        blue.resMan.Wait()
        trinity.GetVariableStore().RegisterVariable('LightingLUT', rj.lightingLUT)
        trinity.GetVariableStore().RegisterVariable('FresnelLUT', rj.fresnelLUT)
        scene.shadowUpdatesPerFrame = 0
        rj.SetScene(scene)
        rj.CreateBasicRenderSteps()
        rj.EnableSceneUpdate(True)
        rj.EnableVisibilityQuery(True)
        rj.Enable()
    else:
        trinity.device.scene2 = scene
    return scene



def CollectCharacterSelectionPaths():
    respaths = []
    for (root, dirs, files,) in bluepy.walk('res:/graphics/character/dnafiles/characterselect/'):
        for f in files:
            respaths.append(root + '/' + f)


    return respaths



def RunCrowdSpawnTest(coldCache = True, iterations = 20, respaths = None, maxLodQueueActive = 1, debugMode = False, nrPerLod = None):

    def fun():
        results = PerformanceTestResults()
        key = 'Loading Factory'
        results.PunchIn(key)
        sTime = blue.os.GetWallclockTime()
        factory = PD.Factory()
        if respaths:
            factory.clothSimulationActive = True
        factory.WaitUntilLoaded()
        eTime = blue.os.GetWallclockTime()
        results.PunchOut(key)
        scene = SetupScene(usePrepass=True)
        onTestExecution = None
        try:
            import pprint
            bm = Benchmarker(factory, scene, usePrepass=True)
            bm.clearCacheOnEachIteration = coldCache
            bm.iterations = 1 if debugMode else iterations
            totalDolls = sum(nrPerLod) if nrPerLod else 32
            lod0Dolls = nrPerLod[0] if nrPerLod else 8
            lod1Dolls = nrPerLod[1] if nrPerLod else 8
            test0 = MultiDollTest(totalDolls, lod0Dolls, lod1Dolls, maxLodQueueActive=1, resPaths=respaths, debugMode=debugMode)
            bm.SetTest(test0)
            bm.ExecuteTest(onTestExecution)
            pprint.pprint(bm.GetAnalyzedResults())

        finally:
            if not debugMode:
                for rj in trinity.device.scheduledRecurring:
                    if rj.name == DEFAULT_PREPASS_RENDERJOB_NAME:
                        trinity.device.scheduledRecurring.remove(rj)
                        break




    testTasklet = uthread.new(fun)
    uthread.schedule(testTasklet)
    try:
        while testTasklet.alive:
            PD.Yield()

    except RuntimeError:
        PD.BeFrameNice()



def RunIncarnaCrowdTest(coldCache = True, iterations = 20, respaths = None, maxLodQueueActive = 1, debugMode = False):

    def fun():
        results = PerformanceTestResults()
        key = 'Loading Factory'
        results.PunchIn(key)
        sTime = blue.os.GetWallclockTime()
        factory = PD.Factory()
        if respaths:
            factory.clothSimulationActive = True
        factory.WaitUntilLoaded()
        eTime = blue.os.GetWallclockTime()
        results.PunchOut(key)
        scene = SetupScene(sceneFile='res:/Graphics/Character/Global/DataUsedForTests/referenceEstablishment.red', usePrepass=True)
        onTestExecution = None
        try:
            import pprint
            bm = Benchmarker(factory, scene, usePrepass=True)
            bm.clearCacheOnEachIteration = coldCache
            bm.iterations = 1 if debugMode else iterations
            test0 = MultiDollTest(32, 8, 16, maxLodQueueActive=1, resPaths=respaths, debugMode=debugMode)
            bm.SetTest(test0)
            bm.ExecuteTest(onTestExecution)
            pprint.pprint(bm.GetAnalyzedResults())

        finally:
            if not debugMode:
                for rj in trinity.device.scheduledRecurring:
                    if rj.name == DEFAULT_PREPASS_RENDERJOB_NAME:
                        trinity.device.scheduledRecurring.remove(rj)
                        break




    testTasklet = uthread.new(fun)
    uthread.schedule(testTasklet)
    try:
        while testTasklet.alive:
            PD.Yield()

    except RuntimeError:
        PD.BeFrameNice()



def RunClothedSpawnTest(coldCache = True, iterations = 20, maxLodQueueActive = 1, debugMode = False):
    RunCrowdSpawnTest(respaths=CollectCharacterSelectionPaths(), coldCache=coldCache, iterations=iterations, maxLodQueueActive=maxLodQueueActive, debugMode=debugMode)



def RunSymmetricalSingleDollLODTest(coldCache = True, iterations = 20, respaths = None, printStatistics = True):

    def fun():
        results = PerformanceTestResults()
        key = 'Loading Factory'
        results.PunchIn(key)
        sTime = blue.os.GetWallclockTime()
        factory = PD.Factory()
        if respaths:
            factory.clothSimulationActive = True
        factory.WaitUntilLoaded()
        eTime = blue.os.GetWallclockTime()
        results.PunchOut(key)
        scene = SetupScene(usePrepass=True)
        onTestExecution = None
        if respaths:
            respathsIterator = itertools.cycle(respaths)

            def onTestExecution(x):
                x.resPath = respathsIterator.next()


        try:
            bm = Benchmarker(factory, scene, usePrepass=True)
            bm.clearCacheOnEachIteration = coldCache
            bm.iterations = iterations
            test0 = SingleDollTest(0, 2)
            bm.SetTest(test0)
            bm.ExecuteTest(onTestExecution)
            if printStatistics:
                import pprint
                pprint.pprint(bm.GetAnalyzedResults())
            test1 = SingleDollTest(2, 0)
            bm.SetTest(test1)
            bm.ExecuteTest(onTestExecution)
            if printStatistics:
                pprint.pprint(bm.GetAnalyzedResults())
                pprint.pprint(results)

        finally:
            for rj in trinity.device.scheduledRecurring:
                if rj.name == DEFAULT_PREPASS_RENDERJOB_NAME:
                    trinity.device.scheduledRecurring.remove(rj)
                    break




    testTasklet = uthread.new(fun)
    uthread.schedule(testTasklet)
    try:
        while testTasklet.alive:
            PD.Yield()

    except RuntimeError:
        PD.BeFrameNice()



def RunSymmetricalSingleNudeLODTest(iterations = 20, coldCache = True, printStatistics = True):
    RunSymmetricalSingleDollLODTest(iterations=iterations, printStatistics=printStatistics)



def RunSymmetricalSingleClothedDollLODTest(iterations = 20, coldCache = True, printStatistics = True):
    RunSymmetricalSingleDollLODTest(iterations=iterations, respaths=CollectCharacterSelectionPaths(), printStatistics=printStatistics)



def RunComprehensiveSymmetricalDollLODTest(iterations = 20):

    def fun():
        RunSymmetricalSingleNudeLODTest(coldCache=True, iterations=iterations)
        RunSymmetricalSingleClothedDollLODTest(coldCache=True, iterations=iterations)
        RunSymmetricalSingleNudeLODTest(coldCache=False, iterations=iterations)
        RunSymmetricalSingleClothedDollLODTest(coldCache=False, iterations=iterations)


    uthread.new(fun)


exports = util.AutoExports('paperDoll.testing', globals())

