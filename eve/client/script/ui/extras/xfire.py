import service
import blue
import ctypes
import uthread
import sys
import extensions

class XFire(service.Service):
    __guid__ = 'svc.xfire'

    def __init__(self, *args):
        service.Service.__init__(self)
        self.messages = {}
        self.delay = prefs.GetValue('xfiredelay', 6000) * 1000
        self.xFireGameClient = extensions.GetXFireGameClient()
        self.state = service.SERVICE_RUNNING
        uthread.new(self.RunXFireLoop)



    def AddKeyValue(self, k, v):
        self.LogInfo('AddKeyValue', k, v)
        self.messages[k] = v



    def RemoveKeyValue(self, k):
        self.LogInfo('RemoveKeyValue', k)
        if self.messages.has_key(k):
            del self.messages[k]



    def RunXFireLoop(self):
        if not self.IsXFireLoaded():
            self.LogInfo('xFire is not loaded.')
            return 
        while self.state == service.SERVICE_RUNNING:
            self.LogInfo('RunXFireLoop Running...')
            try:
                self.DoUpdateXFire()
            except Exception as e:
                self.LogError('RunXFireLoop Error: ', e)
                sys.exc_clear()
            blue.pyos.synchro.Sleep(self.delay)




    def IsXFireLoaded(self):
        return self.xFireGameClient.IsLoaded()



    def DoUpdateXFire(self):
        self.LogInfo('DoUpdateXFire')
        self.xFireGameClient.SetClientData(self.messages)
        k = []
        v = []
        for (key, val,) in self.messages.items():
            k.append(key)
            v.append(val)

        if k:
            cp = ctypes.c_char_p * len(k)
            k_cp = cp(*k)
            v_cp = cp(*v)
            self.LogInfo('Sending', len(k), ' key/val pairs to xFire...')




