import service
import dogmax

class ClientDogmaInstanceManager(service.Service):
    __guid__ = 'svc.clientDogmaIM'
    __startupdependencies__ = ['clientEffectCompiler']

    def Run(self, *args):
        service.Service.Run(self, *args)
        self.dogmaLocation = None
        self.nextKey = 0



    def CreateDogmaLocation(self):
        self.dogmaLocation = dogmax.FakeDogmaLocation(self, None, None)
        return self.dogmaLocation



    def GetDogmaLocation(self):
        return self.dogmaLocation




