import inspect
import service
import trinity

class RenderCallbackManagerService(service.Service):
    __guid__ = 'svc.renderCallbackManager'
    __update_on_reload__ = 0
    __notifyevents__ = []

    def __init__(self):
        service.Service.__init__(self)
        self.callbackFunctionList = []



    def Run(self, *args):
        self.Reset()
        self.pending = None
        self.busy = None



    def Stop(self, stream):
        self.ReleasePostRenderCallback()



    def Reset(self):
        self.SetPostRenderCallback()



    def AddPostRenderCallbackFunction(self, function):
        if function not in self.callbackFunctionList:
            self.ReleasePostRenderCallback()
            self.callbackFunctionList.append(function)
            self.SetPostRenderCallback()



    def RemovePostRenderCallbackFunction(self, function):
        if function in self.callbackFunctionList:
            self.ReleasePostRenderCallback()
            self.callbackFunctionList.remove(function)
            self.SetPostRenderCallback()



    def _RenderCallback(self, evt):
        for renderFunction in self.callbackFunctionList:
            renderFunction(evt)




    def SetPostRenderCallback(self, force = False):
        if trinity.device.postRenderCallback is not None and trinity.device.postRenderCallback != self._RenderCallback and not force:
            return 
        trinity.device.postRenderCallback = self._RenderCallback



    def ReleasePostRenderCallback(self):
        if trinity.device.postRenderCallback == self._RenderCallback:
            trinity.device.postRenderCallback = None



    def IsFunctionInCallbackList(self, function):
        return function in self.callbackFunctionList




