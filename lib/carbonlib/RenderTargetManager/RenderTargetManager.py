import blue
import trinity
import weakref
import bluepy
import locks
lock = locks.RLock()

class FrameNumberRequestPair(object):

    def __init__(self, frameNumber, requests):
        self.frameNumber = frameNumber
        self.requests = requests



    def Advance(self):
        if self.requests > 64:
            self.frameNumber = trinity.GetCurrentFrameCounter() + 1
            self.requests = 0
        else:
            self.requests += 1




class RenderTargetManager(object):
    __metaclass__ = bluepy.CCP_STATS_ZONE_PER_METHOD
    _RenderTargetManager__shared_state = {}

    def __init__(self):
        self.__dict__ = self._RenderTargetManager__shared_state
        if not hasattr(self, 'targets'):
            self.frameNumbers = {}
            self.targets = weakref.WeakValueDictionary()
            self.info = {}
            self._RenderTargetManager__maxSimTargets = 16
        trinity.device.RegisterResource(self)



    def OnCreate(self, dev):
        pass



    def OnInvalidate(self, level):
        self.targets.clear()



    def GetRenderTarget(self, format, width, height, level = 0, asTexture = False):
        hashKey = self._RenderTargetManager__hash(format, width, height, level, asTexture)
        while not self.targets.has_key(hashKey) and len(self.targets) > self._RenderTargetManager__maxSimTargets:
            blue.synchro.Yield()

        with lock:
            futureFrameNumber = self._RenderTargetManager__getMyFrameNumber(hashKey)
            rt = self.targets.get(hashKey)
            while not rt:
                try:
                    if asTexture:
                        rt = trinity.device.CreateTexture(width, height, 1, trinity.TRIUSAGE_RENDERTARGET, format, trinity.TRIPOOL_DEFAULT)
                    else:
                        rt = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, width, height, format, trinity.TRIMULTISAMPLE_NONE, 0, 1)
                except (trinity.E_OUTOFMEMORY, trinity.D3DERR_OUTOFVIDEOMEMORY):
                    rt = None
                    width /= 2
                    height /= 2
                    blue.synchro.Sleep(100)
                except trinity.DeviceLostError:
                    rt = None
                    blue.synchro.Sleep(100)

            self.targets[hashKey] = rt
        while trinity.GetCurrentFrameCounter() < futureFrameNumber:
            blue.synchro.Yield()

        return rt



    def __getMyFrameNumber(self, hashKey):
        with lock:
            frp = self.frameNumbers.get(hashKey, FrameNumberRequestPair(trinity.GetCurrentFrameCounter(), 0))
            frp.Advance()
            self.frameNumbers[hashKey] = frp
            return frp.frameNumber



    def __hash(self, format, width, height, level, asTexture):
        with lock:
            k = (format,
             width,
             height,
             level,
             asTexture)
        return hash(k)




