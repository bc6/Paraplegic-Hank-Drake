import service
import macho

class CherryServer(service.Service):
    __guid__ = 'svc.http2'
    __dependencies__ = ['machoNet', 'WSGIService']
    __exportedcalls__ = {}
    __configvalues__ = {}
    __notifyevents__ = []

    def Run(self, memStream = None):
        self.servers = []
        if not prefs.GetValue('http2', 1):
            self.LogNotice('http2 service not booting up CherryPy ESP app because prefs.http2=0')
            return 
        import dust.cherryServerPages
        cherryTree = dust.cherryServerPages.InitializeEspApp()
        port = self.machoNet.CalculatePortNumber('tcp:raw:http', macho.mode) + 1
        server = self.WSGIService.StartServer(cherryTree, port)
        self.servers.append(server)
        self.LogNotice('CherryPy ESP app server running on port %s' % port)



    def Stop(self, memStream):
        for server in self.servers:
            self.WSGIService.StopServer(server)





