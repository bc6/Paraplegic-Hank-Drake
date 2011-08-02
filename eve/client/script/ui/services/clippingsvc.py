import service
import log

class ZServer(service.Service):
    __guid__ = 'svc.z'
    __exportedcalls__ = {'GetZ': [],
     'ReleaseZ': []}

    def __init__(self):
        service.Service.__init__(self)
        self.takenZs = []



    def GetZ(self, minZ = None):
        if minZ and minZ <= 20:
            raise RuntimeError('minZs under 20 are reserved!')
        for i in xrange(minZ or 1000, 99998, 4):
            if i not in self.takenZs:
                self.takenZs.append(i)
                return i

        self.takenZs = []
        log.LogWarn("All Z's Done!!!")
        return self.GetZ()



    def ReleaseZ(self, z):
        if z not in self.takenZs:
            return 
        self.takenZs.remove(z)




