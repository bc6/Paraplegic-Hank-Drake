#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\process\servers.py
import sys
import time

class ServerAdapter(object):

    def __init__(self, bus, httpserver = None, bind_addr = None):
        self.bus = bus
        self.httpserver = httpserver
        self.bind_addr = bind_addr
        self.interrupt = None
        self.running = False

    def subscribe(self):
        self.bus.subscribe('start', self.start)
        self.bus.subscribe('stop', self.stop)

    def unsubscribe(self):
        self.bus.unsubscribe('start', self.start)
        self.bus.unsubscribe('stop', self.stop)

    def start(self):
        if self.bind_addr is None:
            on_what = 'unknown interface (dynamic?)'
        elif isinstance(self.bind_addr, tuple):
            host, port = self.bind_addr
            on_what = '%s:%s' % (host, port)
        else:
            on_what = 'socket file: %s' % self.bind_addr
        if self.running:
            self.bus.log('Already serving on %s' % on_what)
            return
        self.interrupt = None
        if not self.httpserver:
            raise ValueError('No HTTP server has been created.')
        if isinstance(self.bind_addr, tuple):
            wait_for_free_port(*self.bind_addr)
        import threading
        t = threading.Thread(target=self._start_http_thread)
        t.setName('HTTPServer ' + t.getName())
        t.start()
        self.wait()
        self.running = True
        self.bus.log('Serving on %s' % on_what)

    start.priority = 75

    def _start_http_thread(self):
        try:
            self.httpserver.start()
        except KeyboardInterrupt:
            self.bus.log('<Ctrl-C> hit: shutting down HTTP server')
            self.interrupt = sys.exc_info()[1]
            self.bus.exit()
        except SystemExit:
            self.bus.log('SystemExit raised: shutting down HTTP server')
            self.interrupt = sys.exc_info()[1]
            self.bus.exit()
            raise 
        except:
            self.interrupt = sys.exc_info()[1]
            self.bus.log('Error in HTTP server: shutting down', traceback=True, level=40)
            self.bus.exit()
            raise 

    def wait(self):
        while not getattr(self.httpserver, 'ready', False):
            if self.interrupt:
                raise self.interrupt
            time.sleep(0.1)

        if isinstance(self.bind_addr, tuple):
            host, port = self.bind_addr
            wait_for_occupied_port(host, port)

    def stop(self):
        if self.running:
            self.httpserver.stop()
            if isinstance(self.bind_addr, tuple):
                wait_for_free_port(*self.bind_addr)
            self.running = False
            self.bus.log('HTTP Server %s shut down' % self.httpserver)
        else:
            self.bus.log('HTTP Server %s already shut down' % self.httpserver)

    stop.priority = 25

    def restart(self):
        self.stop()
        self.start()


class FlupCGIServer(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.ready = False

    def start(self):
        from flup.server.cgi import WSGIServer
        self.cgiserver = WSGIServer(*self.args, **self.kwargs)
        self.ready = True
        self.cgiserver.run()

    def stop(self):
        self.ready = False


class FlupFCGIServer(object):

    def __init__(self, *args, **kwargs):
        if kwargs.get('bindAddress', None) is None:
            import socket
            if not hasattr(socket, 'fromfd'):
                raise ValueError('Dynamic FCGI server not available on this platform. You must use a static or external one by providing a legal bindAddress.')
        self.args = args
        self.kwargs = kwargs
        self.ready = False

    def start(self):
        from flup.server.fcgi import WSGIServer
        self.fcgiserver = WSGIServer(*self.args, **self.kwargs)
        self.fcgiserver._installSignalHandlers = lambda : None
        self.fcgiserver._oldSIGs = []
        self.ready = True
        self.fcgiserver.run()

    def stop(self):
        self.fcgiserver._keepGoing = False
        self.fcgiserver._threadPool.maxSpare = self.fcgiserver._threadPool._idleCount
        self.ready = False


class FlupSCGIServer(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.ready = False

    def start(self):
        from flup.server.scgi import WSGIServer
        self.scgiserver = WSGIServer(*self.args, **self.kwargs)
        self.scgiserver._installSignalHandlers = lambda : None
        self.scgiserver._oldSIGs = []
        self.ready = True
        self.scgiserver.run()

    def stop(self):
        self.ready = False
        self.scgiserver._keepGoing = False
        self.scgiserver._threadPool.maxSpare = 0


def client_host(server_host):
    if server_host == '0.0.0.0':
        return '127.0.0.1'
    if server_host in ('::', '::0', '::0.0.0.0'):
        return '::1'
    return server_host


def check_port(host, port, timeout = 1.0):
    if not host:
        raise ValueError("Host values of '' or None are not allowed.")
    host = client_host(host)
    port = int(port)
    import socket
    try:
        info = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror:
        if ':' in host:
            info = [(socket.AF_INET6,
              socket.SOCK_STREAM,
              0,
              '',
              (host,
               port,
               0,
               0))]
        else:
            info = [(socket.AF_INET,
              socket.SOCK_STREAM,
              0,
              '',
              (host, port))]

    for res in info:
        af, socktype, proto, canonname, sa = res
        s = None
        try:
            s = socket.socket(af, socktype, proto)
            s.settimeout(timeout)
            s.connect((host, port))
            s.close()
            raise IOError('Port %s is in use on %s; perhaps the previous httpserver did not shut down properly.' % (repr(port), repr(host)))
        except socket.error:
            if s:
                s.close()


def wait_for_free_port(host, port):
    if not host:
        raise ValueError("Host values of '' or None are not allowed.")
    for trial in range(50):
        try:
            check_port(host, port, timeout=0.1)
        except IOError:
            time.sleep(0.1)
        else:
            return

    raise IOError('Port %r not free on %r' % (port, host))


def wait_for_occupied_port(host, port):
    if not host:
        raise ValueError("Host values of '' or None are not allowed.")
    for trial in range(50):
        try:
            check_port(host, port)
        except IOError:
            return

        time.sleep(0.1)

    raise IOError('Port %r not bound on %r' % (port, host))