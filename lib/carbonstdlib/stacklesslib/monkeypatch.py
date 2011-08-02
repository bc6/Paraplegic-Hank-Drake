import sys
import threading as real_threading
from . import main
from replacements import thread, threading, popen
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
    except ImportError:
        return 

    def wrap_errors(call, args, sock, wouldblock):
        try:
            return call(*args)
        except socket.timeout:
            if sock.gettimeout() == 0.0:
                return wouldblock
            raise _ssl.SSLError, 'call timed out'
        except socket.error as e:
            if e.errno == errno.EWOULDBLOCK:
                return wouldblock
            raise 



    class SocketBio(object):

        def __init__(self, sock):
            self.sock = sock



        def write(self, data):
            return wrap_errors(self.sock.send, (data,), self.sock, 0)



        def read(self, want):
            return wrap_errors(self.sock.recv, (want,), self.sock, None)



        def __getattr__(self, attr):
            return getattr(self.sock, attr)



    realwrap = _ssl.sslwrap

    def wrapbio(sock, *args, **kwds):
        bio = SocketBio(sock)
        return realwrap(bio, *args, **kwds)


    _ssl.sslwrap = wrapbio



