#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/sys/launcherService.py
import service
import launcherapi

class LauncherService(service.Service):
    __guid__ = 'svc.launcher'
    __displayname__ = 'EVE Launcher Interface Service'

    def __init__(self):
        service.Service.__init__(self)
        self.shared = {}

    def Run(self, memStream = None):
        self.state = service.SERVICE_RUNNING
        self.shared['clientBoot'] = launcherapi.ClientBootManager()

    def SetClientBootProgress(self, percentage):
        progress = self.shared['clientBoot']
        progress.SetPercentage(percentage)