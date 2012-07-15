#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/util/devToolsClient.py
import service
import marshal
import types

class DevToolsClient(service.Service):
    __guid__ = 'svc.devToolsClient'
    __displayname__ = 'Dev Tools Client Service'
    __dependencies__ = ['machoNet']
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self):
        service.Service.__init__(self)
        self.isBootstrapped = False
        self.files = set()

    def Bootstrap(self):
        self.LogInfo('Bootstrapping devtools from remote')
        self.dtProvider = sm.RemoteSvc('devToolsProvider')
        res = self.dtProvider.GetLoader()
        res = marshal.loads(res)
        func_code, func_defaults = res['Bootstrap']
        bootstrapper = types.FunctionType(func_code, globals())
        bootstrapper(self, res)
        self.Loader()

    def OnSessionChanged(self, isRemote, sess, change):
        if 'role' in change and change['role'][1] & service.ROLEMASK_ELEVATEDPLAYER:
            if not self.isBootstrapped:
                self.Bootstrap()