#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/sys/eveBenchmarkSvc.py
import svc
import benchmark

class EveBenchmarkService(svc.benchmark):
    __guid__ = 'svc.eveBenchmark'
    __replaceservice__ = 'benchmark'

    def CreateSession(self, testbedName = None, description = '', runID = 0):
        self.runID = runID
        return EveSession(testbedName, description, self.runID)


class EveSession(benchmark.Session):
    __guid__ = 'benchmark.EveSession'

    def AppGetTriAppData(self):
        import trinity
        return {'width': trinity.app.width,
         'height': trinity.app.height,
         'fullscreen': trinity.app.fullscreen}