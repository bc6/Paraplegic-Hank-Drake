import trinity
import blue

class RenderTargetManager(object):

    def __init__(self):
        trinity.device.RegisterResource(self)
        self.targets = {}



    def OnCreate(self, device):
        pass



    def OnInvalidate(self, level):
        self.targets = {}



    def _Get(self, key, function, *args):
        if self.targets.has_key(key) and self.targets[key].object is not None:
            return self.targets[key].object

        def DeleteObject():
            self.targets.pop(key)


        rt = function(*args)
        self.targets[key] = blue.BluePythonWeakRef(rt)
        self.targets[key].callback = DeleteObject
        return rt



    def GetTexture(self, index, width, height, mipLevels, usage, format, pool):
        key = (trinity.device.CreateTexture,
         index,
         width,
         height,
         mipLevels,
         usage,
         format,
         pool)
        return self._Get(key, trinity.device.CreateTexture, width, height, mipLevels, usage, format, pool)



    def GetRenderTarget(self, index, width, height, format, msType, msQuality, lockable):
        key = (trinity.device.CreateRenderTarget,
         index,
         width,
         height,
         format,
         msType,
         msQuality,
         lockable)
        return self._Get(key, trinity.device.CreateRenderTarget, width, height, format, msType, msQuality, lockable)



    def GetDepthStencil(self, index, width, height, format, msType, msQuality, lockable):
        key = (trinity.device.CreateDepthStencilSurface,
         index,
         width,
         height,
         format,
         msType,
         msQuality,
         lockable)
        return self._Get(key, trinity.device.CreateDepthStencilSurface, width, height, format, msType, msQuality, lockable)



renderTargetManager = RenderTargetManager()

def DeviceSupportsIntZ():
    d3d = trinity.GetDirect3D()
    return d3d.CheckDeviceFormat(0, trinity.TRIDEVTYPE_HAL, d3d.GetAdapterDisplayMode()['Format'], trinity.TRIUSAGE_DEPTHSTENCIL, trinity.TRIRTYPE_SURFACE, trinity.TRIFMT_INTZ)



def DeviceSupportsRenderTargetFormat(format):
    d3d = trinity.GetDirect3D()
    return d3d.CheckDeviceFormat(0, trinity.TRIDEVTYPE_HAL, d3d.GetAdapterDisplayMode()['Format'], trinity.TRIUSAGE_RENDERTARGET, trinity.TRIRTYPE_TEXTURE, format)



