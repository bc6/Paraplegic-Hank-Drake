#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\wsgiserver\ssl_pyopenssl.py
import socket
import threading
import time
from cherrypy import wsgiserver
try:
    from OpenSSL import SSL
    from OpenSSL import crypto
except ImportError:
    SSL = None

class SSL_fileobject(wsgiserver.CP_fileobject):
    ssl_timeout = 3
    ssl_retry = 0.01

    def _safe_call(self, is_reader, call, *args, **kwargs):
        start = time.time()
        while True:
            try:
                return call(*args, **kwargs)
            except SSL.WantReadError:
                time.sleep(self.ssl_retry)
            except SSL.WantWriteError:
                time.sleep(self.ssl_retry)
            except SSL.SysCallError as e:
                if is_reader and e.args == (-1, 'Unexpected EOF'):
                    return ''
                errnum = e.args[0]
                if is_reader and errnum in wsgiserver.socket_errors_to_ignore:
                    return ''
                raise socket.error(errnum)
            except SSL.Error as e:
                if is_reader and e.args == (-1, 'Unexpected EOF'):
                    return ''
                thirdarg = None
                try:
                    thirdarg = e.args[0][0][2]
                except IndexError:
                    pass

                if thirdarg == 'http request':
                    raise wsgiserver.NoSSLError()
                raise wsgiserver.FatalSSLAlert(*e.args)
            except:
                raise 

            if time.time() - start > self.ssl_timeout:
                raise socket.timeout('timed out')

    def recv(self, *args, **kwargs):
        buf = []
        r = super(SSL_fileobject, self).recv
        while True:
            data = self._safe_call(True, r, *args, **kwargs)
            buf.append(data)
            p = self._sock.pending()
            if not p:
                return ''.join(buf)

    def sendall(self, *args, **kwargs):
        return self._safe_call(False, super(SSL_fileobject, self).sendall, *args, **kwargs)

    def send(self, *args, **kwargs):
        return self._safe_call(False, super(SSL_fileobject, self).send, *args, **kwargs)


class SSLConnection:

    def __init__(self, *args):
        self._ssl_conn = SSL.Connection(*args)
        self._lock = threading.RLock()

    for f in ('get_context', 'pending', 'send', 'write', 'recv', 'read', 'renegotiate', 'bind', 'listen', 'connect', 'accept', 'setblocking', 'fileno', 'close', 'get_cipher_list', 'getpeername', 'getsockname', 'getsockopt', 'setsockopt', 'makefile', 'get_app_data', 'set_app_data', 'state_string', 'sock_shutdown', 'get_peer_certificate', 'want_read', 'want_write', 'set_connect_state', 'set_accept_state', 'connect_ex', 'sendall', 'settimeout', 'gettimeout'):
        exec 'def %s(self, *args):\n        self._lock.acquire()\n        try:\n            return self._ssl_conn.%s(*args)\n        finally:\n            self._lock.release()\n' % (f, f)

    def shutdown(self, *args):
        self._lock.acquire()
        try:
            return self._ssl_conn.shutdown()
        finally:
            self._lock.release()


class pyOpenSSLAdapter(wsgiserver.SSLAdapter):
    context = None
    certificate = None
    private_key = None
    certificate_chain = None

    def __init__(self, certificate, private_key, certificate_chain = None):
        if SSL is None:
            raise ImportError('You must install pyOpenSSL to use HTTPS.')
        self.context = None
        self.certificate = certificate
        self.private_key = private_key
        self.certificate_chain = certificate_chain
        self._environ = None

    def bind(self, sock):
        if self.context is None:
            self.context = self.get_context()
        conn = SSLConnection(self.context, sock)
        self._environ = self.get_environ()
        return conn

    def wrap(self, sock):
        return (sock, self._environ.copy())

    def get_context(self):
        c = SSL.Context(SSL.SSLv23_METHOD)
        c.use_privatekey_file(self.private_key)
        if self.certificate_chain:
            c.load_verify_locations(self.certificate_chain)
        c.use_certificate_file(self.certificate)
        return c

    def get_environ(self):
        ssl_environ = {'HTTPS': 'on'}
        if self.certificate:
            cert = open(self.certificate, 'rb').read()
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
            ssl_environ.update({'SSL_SERVER_M_VERSION': cert.get_version(),
             'SSL_SERVER_M_SERIAL': cert.get_serial_number()})
            for prefix, dn in [('I', cert.get_issuer()), ('S', cert.get_subject())]:
                dnstr = str(dn)[18:-2]
                wsgikey = 'SSL_SERVER_%s_DN' % prefix
                ssl_environ[wsgikey] = dnstr
                while dnstr:
                    pos = dnstr.rfind('=')
                    dnstr, value = dnstr[:pos], dnstr[pos + 1:]
                    pos = dnstr.rfind('/')
                    dnstr, key = dnstr[:pos], dnstr[pos + 1:]
                    if key and value:
                        wsgikey = 'SSL_SERVER_%s_DN_%s' % (prefix, key)
                        ssl_environ[wsgikey] = value

        return ssl_environ

    def makefile(self, sock, mode = 'r', bufsize = -1):
        if SSL and isinstance(sock, SSL.ConnectionType):
            timeout = sock.gettimeout()
            f = SSL_fileobject(sock, mode, bufsize)
            f.ssl_timeout = timeout
            return f
        else:
            return wsgiserver.CP_fileobject(sock, mode, bufsize)