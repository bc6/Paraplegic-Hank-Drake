#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/net/httpGate.py
import service
import log
import macho
import json
import base

class HttpGate(service.Service):
    __dependencies__ = ['machoNet', 'WSGIService']
    __exportedcalls__ = {}
    __configvalues__ = {}
    __guid__ = 'svc.httpGate'
    __notifyevents__ = []
    __counters__ = {}
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.LogInfo('Http Gate Server starting')
        self.server = self.WSGIService.StartServer(self.defaultApp, 8080)

    def Stop(self, memStream = None):
        self.LogInfo('Http Gate Server stopping')
        self.WSGIService.StopServer(self.server)
        self.server = None
        self.LogInfo('Http Gate Server stopped')

    def defaultApp(self, environ, start_response):
        data = None
        try:
            data = sm.RemoteSvc('account').GetCashBalance(0)
        finally:
            pass

        start_response('200 OK', [('content-type', 'text/html')])
        return [json.dumps(data)]