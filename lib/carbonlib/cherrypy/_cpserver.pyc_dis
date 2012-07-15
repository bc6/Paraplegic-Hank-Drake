#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\_cpserver.py
import warnings
import cherrypy
from cherrypy.lib import attributes
from cherrypy._cpcompat import basestring
from cherrypy.process.servers import *

class Server(ServerAdapter):
    socket_port = 8080
    _socket_host = '127.0.0.1'

    def _get_socket_host(self):
        return self._socket_host

    def _set_socket_host(self, value):
        if value == '':
            raise ValueError("The empty string ('') is not an allowed value. Use '0.0.0.0' instead to listen on all active interfaces (INADDR_ANY).")
        self._socket_host = value

    socket_host = property(_get_socket_host, _set_socket_host, doc='The hostname or IP address on which to listen for connections.\n        \n        Host values may be any IPv4 or IPv6 address, or any valid hostname.\n        The string \'localhost\' is a synonym for \'127.0.0.1\' (or \'::1\', if\n        your hosts file prefers IPv6). The string \'0.0.0.0\' is a special\n        IPv4 entry meaning "any active interface" (INADDR_ANY), and \'::\'\n        is the similar IN6ADDR_ANY for IPv6. The empty string or None are\n        not allowed.')
    socket_file = None
    socket_queue_size = 5
    socket_timeout = 10
    shutdown_timeout = 5
    protocol_version = 'HTTP/1.1'
    thread_pool = 10
    thread_pool_max = -1
    max_request_header_size = 512000
    max_request_body_size = 104857600
    instance = None
    ssl_context = None
    ssl_certificate = None
    ssl_certificate_chain = None
    ssl_private_key = None
    ssl_module = 'pyopenssl'
    nodelay = True
    wsgi_version = (1, 0)

    def __init__(self):
        self.bus = cherrypy.engine
        self.httpserver = None
        self.interrupt = None
        self.running = False

    def httpserver_from_self(self, httpserver = None):
        if httpserver is None:
            httpserver = self.instance
        if httpserver is None:
            from cherrypy import _cpwsgi_server
            httpserver = _cpwsgi_server.CPWSGIServer(self)
        if isinstance(httpserver, basestring):
            httpserver = attributes(httpserver)(self)
        return (httpserver, self.bind_addr)

    def start(self):
        if not self.httpserver:
            self.httpserver, self.bind_addr = self.httpserver_from_self()
        ServerAdapter.start(self)

    start.priority = 75

    def _get_bind_addr(self):
        if self.socket_file:
            return self.socket_file
        if self.socket_host is None and self.socket_port is None:
            return
        return (self.socket_host, self.socket_port)

    def _set_bind_addr(self, value):
        if value is None:
            self.socket_file = None
            self.socket_host = None
            self.socket_port = None
        elif isinstance(value, basestring):
            self.socket_file = value
            self.socket_host = None
            self.socket_port = None
        else:
            try:
                self.socket_host, self.socket_port = value
                self.socket_file = None
            except ValueError:
                raise ValueError('bind_addr must be a (host, port) tuple (for TCP sockets) or a string (for Unix domain sockets), not %r' % value)

    bind_addr = property(_get_bind_addr, _set_bind_addr, doc='A (host, port) tuple for TCP sockets or a str for Unix domain sockets.')

    def base(self):
        if self.socket_file:
            return self.socket_file
        host = self.socket_host
        if host in ('0.0.0.0', '::'):
            import socket
            host = socket.gethostname()
        port = self.socket_port
        if self.ssl_certificate:
            scheme = 'https'
            if port != 443:
                host += ':%s' % port
        else:
            scheme = 'http'
            if port != 80:
                host += ':%s' % port
        return '%s://%s' % (scheme, host)