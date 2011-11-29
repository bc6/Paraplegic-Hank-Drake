import service
import uthread
import socket
import blue
import log
from service import ROLE_SERVICE
from cherrypy import wsgiserver
from cherrypy.wsgiserver.ssl_builtin import BuiltinSSLAdapter

class TaskletThreadPool(object):

    def __init__(self, server, min = 10, max = -1):
        self.server = server
        self.min = min



    def start(self):
        pass



    def stop(self, timeout = None):
        pass



    def put(self, obj):
        if obj is wsgiserver._SHUTDOWNREQUEST:
            return 
        t = uthread.new(self.Run, obj)
        t.run()



    def Run(self, conn):
        conn.socket.setblockingsend(self.server.service.blockingSend)
        try:
            try:
                conn.communicate()

            finally:
                conn.close()

        except (KeyboardInterrupt, SystemExit) as exc:
            self.server.interrupt = exc



wsgiserver.ThreadPool = TaskletThreadPool

class MyCherryPyWSGIServer(wsgiserver.CherryPyWSGIServer):

    def bind(self, family, type, proto = 0):
        super(MyCherryPyWSGIServer, self).bind(family, type, proto)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)




class CherryServerRunner(object):

    def __init__(self, server, ntasks = 2, ssl = False):
        self.server = server
        self.running = False
        self.ntasks = ntasks - 1
        self.listening = 0
        wsgiserver.LogError = self.LogCherryError



    def Start(self):
        self.running = True
        uthread.new(self._ServeFirst)
        if self.ntasks:
            blue.pyos.synchro.SleepWallclock(1)
            for t in xrange(self.ntasks):
                self.listening += 1
                uthread.new(self._ServeOthers)




    def Stop(self):
        self.running = False
        self.server.stop()
        del self.server



    def LogCherryError(self):
        log.LogException('CherryPy server internal error')



    def _ServeFirst(self):
        self.server.start()



    def _ServeOthers(self):
        try:
            while self.running and self.server.ready:
                self.server.tick()


        finally:
            self.running = False
            self.listening -= 1




    def on_wrap_start(self):
        self.listening -= 1
        if self.listening < self.ntasks:
            self.listening += 1
            uthread.new(self.wrap_task)



    def on_wrap_done(self):
        self.listening += 1



    def wrap_task(self):
        try:
            if self.running and self.server.ready:
                self.server.tick()

        finally:
            self.listening -= 1





class SSLAdapter(BuiltinSSLAdapter):
    runner = None

    def wrap(self, socket):
        if self.runner:
            self.runner.on_wrap_start()
        result = super(SSLAdapter, self).wrap(socket)
        if self.runner:
            self.runner.on_wrap_done()
        return result




class WSGIService(service.Service):
    __exportedcalls__ = {'StartServer': [ROLE_SERVICE],
     'StopServer': [ROLE_SERVICE]}
    __guid__ = 'svc.WSGIService'
    __dependencies__ = []
    __configvalues__ = {'blockingSend': False}

    def OnSetConfigValue(self, key, value):
        if key == 'blockingSend':
            value = bool(value)
        return value



    def GetHtmlStateDetails(self, k, v, detailed):
        if k == 'blockingSend':
            return ('block on send', v)



    def Run(self, memStream = None):
        self.runners = {}
        self.state = service.SERVICE_RUNNING
        self.idx = 1
        for key in self.__configvalues__.iterkeys():
            val = getattr(self, key)
            self.OnSetConfigValue(key, val)




    def Stop(self, memStream):
        for runner in self.runners:
            runner.Stop()

        self.runners = {}
        self.state = service.SERVICE_STOPPED



    def Restart(self):
        self.LogInfo('Restarting WSGIService')
        for (idx, (args, runners,),) in self.runners.items():
            self.LogInfo('Restarting WSGI Server ' + repr(args))
            self.StopRunners(runners)
            self.runners[idx] = (args, self.StartServerInt(args))




    def StartServer(self, middleware, port, protocol = 'HTTP/1.1', enableIPv6 = True, serverName = None, ssl = None):
        args = (middleware,
         port,
         protocol,
         enableIPv6,
         serverName,
         ssl)
        runners = self.StartServerInt(args)
        idx = self.idx
        self.idx += 1
        self.runners[idx] = (args, runners)
        return idx



    def StopServer(self, idx):
        self.StopRunners(self.runners[idx][1])
        del self.runners[idx]



    def StartServerInt(self, args):
        runners = self.StartCherry(*args)
        for runner in runners:
            runner.Start()

        self.LogInfo('%s WSGI server running: %r' % (type, args))
        return runners



    def StartCherry(self, middleware, port, protocol = 'HTTP/1.1', enableIPv6 = True, serverName = None, ssl = None):
        if ssl:

            def Adapter(runner):
                (certificate, private_key,) = ssl
                adapter = SSLAdapter(certificate, private_key)
                adapter.runner = runner
                return adapter


        else:

            def Adapter(runner):
                return None


        if enableIPv6:
            addr = ('::', port)
        else:
            addr = ('0.0.0.0', port)
        server = MyCherryPyWSGIServer(addr, middleware, request_queue_size=socket.SOMAXCONN, server_name=serverName)
        server.service = self
        runner = CherryServerRunner(server, ssl=ssl)
        server.ssl_adapter = Adapter(runner)
        runners = (runner,)
        if enableIPv6 and not hasattr(socket, 'IPV6_V6ONLY'):
            addr = ('0.0.0.0', port)
            server = MyCherryPyWSGIServer(addr, middleware, request_queue_size=socket.SOMAXCONN, server_name=serverName)
            server.service = self
            runner = CherryServerRunner(server, ssl=ssl)
            server.ssl_adapter = Adapter(runner)
            runners += (runner,)
        return runners



    def StopRunners(self, runners):
        for runner in runners:
            runner.Stop()





