import sys
import service
import blue
import uthread
import base
import socket
from service import ROLE_SERVICE
from StacklessSocketServer import UThreadingMixIn
from paste import httpserver

class UTWSGIServer(UThreadingMixIn, httpserver.WSGIServer):
    request_queue_size = socket.SOMAXCONN


class UTWSGIServer6(UTWSGIServer):
    address_family = socket.AF_INET6

    def server_bind(self):
        return httpserver.WSGIServer.server_bind(self)




class NBRequestHandler(httpserver.WSGIHandler):

    def setup(self):
        httpserver.WSGIHandler.setup(self)
        self.connection.setblockingsend(False)




class ServerRunner:

    def __init__(self, server, ntasks = 2):
        self.server = server
        self.running = False
        self.ntasks = ntasks



    def Start(self):
        self.running = True
        for t in xrange(self.ntasks):
            uthread.new(self._Serve)




    def Stop(self):
        self.running = False
        self.server.server_close()



    def _Serve(self):
        while self.running:
            self.server.handle_request()





class WSGIService(service.Service):
    __exportedcalls__ = {'StartServer': [ROLE_SERVICE],
     'StopServer': [ROLE_SERVICE]}
    __guid__ = 'svc.WSGIService'
    __dependencies__ = []

    def Run(self, memStream = None):
        self.runners = []
        self.state = service.SERVICE_RUNNING



    def Stop(self, memStream):
        for runner in self.runners:
            runner.Stop()

        self.runners = []
        self.state = service.SERVICE_STOPPED



    def StartServer(self, middleware, port):
        server = httpserver.serve(middleware, host='0.0.0.0', port=port, use_threadpool=False, protocol_version='HTTP/1.1', start_loop=False, server_class=UTWSGIServer, handler=NBRequestHandler)
        server6 = httpserver.serve(middleware, host='::', port=port, use_threadpool=False, protocol_version='HTTP/1.1', start_loop=False, server_class=UTWSGIServer6, handler=NBRequestHandler)
        runner = ServerRunner(server)
        self.runners.append(runner)
        runner.Start()
        runner = ServerRunner(server6)
        self.runners.append(runner)
        runner.Start()
        self.LogInfo('http server running on port %s' % port)
        return server



    def StopServer(self, server):
        for runner in self.runners:
            if runner.server is server:
                break
        else:
            raise ValueError, 'server not found'

        self.runners.remove(runner)
        runner.Stop()




