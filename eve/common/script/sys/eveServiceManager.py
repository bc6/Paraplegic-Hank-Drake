import service

class DustNotEnabledError(Exception):
    __guid__ = 'exceptions.DustNotEnabledError'
    __persistvars__ = []

    def __init__(self):
        self.args = []



    def __repr__(self):
        return 'DUST is not currently enabled.  Please set enableDust=1 in your prefs to use DUST functionality.'




class FakeDustService(object):
    __dependencies__ = []
    __notifyevents__ = []
    __startupdependencies__ = []

    def __init__(self, serviceName):
        self.__guid__ = 'svc.' + serviceName
        self.state = service.SERVICE_STOPPED



    def __getattr__(self, key):
        raise DustNotEnabledError()


    Run = lambda *args: None
    LogInfo = lambda *args: None
    GetHtmlState = lambda *args: 'Fake, dust not enabled'
    GetServiceState = lambda *args: 'Faked'
    isLogInfo = 0
    isLogWarning = 0

    def SetLogInfo(self, b):
        pass



    def SetLogNotice(self, b):
        pass



    def SetLogWarning(self, b):
        pass




class EveServiceManager(service.ServiceManager):
    __guid__ = 'service.EveServiceManager'

    def __init__(self, *args, **kw):
        self._dustEnabled = prefs.GetValue('enableDust', 0)
        service.ServiceManager.__init__(self, *args, **kw)



    def CreateServiceInstance(self, serviceName):
        if serviceName.startswith('dust'):
            if not self._dustEnabled:
                print 'DUST is not enabled.  Starting fake service for',
                print serviceName
                return FakeDustService(serviceName)
        return service.ServiceManager.CreateServiceInstance(self, serviceName)




