#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\stdlib\stacklesslib\monkeypatch.py
import sys
import threading as real_threading
from . import main
from . import util
from .replacements import thread, threading, popen
stacklessio = None

def patch_all():
    patch_misc()
    patch_thread()
    patch_threading()
    patch_select()
    patch_socket()
    patch_ssl()


def patch_misc():
    import time
    time.sleep = main.sleep
    import os
    if hasattr(os, 'popen4'):
        os.popen4 = popen.popen4


def patch_thread():
    sys.modules['thread'] = thread


def patch_threading():
    threading.real_threading = real_threading
    sys.modules['threading'] = threading


def patch_select():
    if stacklessio:
        from stacklessio import select
    else:
        from stacklesslib.replacements import select
    sys.modules['select'] = select


def patch_socket(will_be_pumped = True):
    if stacklessio:
        from stacklessio import _socket
        sys.modules['_socket'] = _socket
    else:
        from stacklesslib.replacements import socket
        socket._sleep_func = main.sleep
        socket._schedule_func = lambda : main.sleep(0)
        if will_be_pumped:
            socket._manage_sockets_func = lambda : None
        socket.install()


def patch_ssl():
    try:
        import _ssl
        import socket
        import errno
        from cStringIO import StringIO
    except ImportError:
        return

    class SocketBio(object):
        default_bufsize = 8192

        def __init__(self, sock, rbufsize = -1):
            self.sock = sock
            self.bufsize = self.default_bufsize if rbufsize < 0 else rbufsize
            if self.bufsize:
                self.buf = StringIO()

        def write(self, data):
            return self.wrap_errors('write', self.sock.send, (data,))

        def read(self, want):
            if self.bufsize:
                data = self.buf.read(want)
                if not data:
                    buf = self.wrap_errors('read', self.sock.recv, (self.bufsize,))
                    self.buf = StringIO(buf)
                    data = self.buf.read(want)
            else:
                data = self.wrap_errors('read', self.sock.recv, (want,))
            return data

        def wrap_errors(self, name, call, args):
            try:
                return call(*args)
            except socket.timeout:
                if self.sock.gettimeout() == 0.0:
                    if name == 'read':
                        return None
                    return 0
                raise _ssl.SSLError, 'The %s operation timed out' % (name,)
            except socket.error as e:
                if e.errno == errno.EWOULDBLOCK:
                    if name == 'read':
                        return None
                    return 0
                raise 

        def __getattr__(self, attr):
            return getattr(self.sock, attr)

    realwrap = _ssl.sslwrap

    def wrapbio(sock, *args, **kwds):
        bio = SocketBio(sock)
        return util.call_on_thread(realwrap, (bio,) + args, kwds)

    _ssl.sslwrap = wrapbio