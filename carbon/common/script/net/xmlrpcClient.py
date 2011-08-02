from __future__ import with_statement
import service
import contextlib
import xmlrpclib
import urlparse
import socket
import collections
import locks
from service import ROLE_SERVICE

class CachedMultiMap(object):

    def __init__(self, highWater = 10, lowWater = None):
        self.map = collections.defaultdict(list)
        self.times = {}
        self.time = 0
        self.highWater = highWater
        if lowWater is None:
            lowWater = self.highWater / 2
        self.lowWater = min(lowWater, self.highWater)



    def __len__(self):
        return len(self.times)



    def Insert(self, key, val):
        time = self.time
        self.time += 1
        e = (time, val)
        self.map[key].append(e)
        self.times[time] = key
        if len(self.times) > self.highWater:
            self.Trim(self.lowWater)



    def Get(self, key):
        l = self.map[key]
        (t0, v,) = l[-1]
        t = self.time
        self.time += 1
        del self.times[t0]
        self.times[t] = key
        l[-1] = (t, v)
        return v



    def Pop(self, key, first = False):
        l = self.map[key]
        try:
            (t0, v,) = l.pop(0 if first else -1)
        except IndexError:
            raise KeyError, key
        del self.times[t0]
        if not l:
            del self.map[key]
        return v



    def Trim(self, max):
        times = self.times
        if len(times) > max:
            k = self.times.keys()
            k.sort()
            k = k[:(-max)]
            Pop = self.Pop
            for t in k:
                Pop(times[t], True)




    def Clear(self):
        self.map = collections.defaultdict(list)
        self.times = {}
        self.time = self.n = 0




class RetryProxyMethod:

    def __init__(self, send, name, retries = 3):
        self._RetryProxyMethod__send = send
        self._RetryProxyMethod__name = name
        self._RetryProxyMethod__retries = retries



    def __getattr__(self, name):
        return RetryProxyMethod(self._RetryProxyMethod__send, '.'.join((self._RetryProxyMethod__name, name)), self._RetryProxyMethod__retries)



    def __call__(self, *args):
        for i in xrange(self._RetryProxyMethod__retries):
            try:
                return self._RetryProxyMethod__send(self._RetryProxyMethod__name, args)
            except socket.error:
                if i == self._RetryProxyMethod__retries - 1:
                    raise 





class RetryProxy(xmlrpclib.ServerProxy):
    __guid__ = 'xmlrpc.RetryProxy'

    def __init__(self, uri, transport = None, encoding = None, verbose = 0, allow_none = 0, use_datetime = 0, retries = 3):
        xmlrpclib.ServerProxy.__init__(self, uri, transport, encoding, verbose, allow_none, use_datetime)
        self._RetryProxy__retries = retries



    def __getattr__(self, name):
        return RetryProxyMethod(self._ServerProxy__request, name, self._RetryProxy__retries)




class XmlrpcClient(service.Service):
    __exportedcalls__ = {'GetProxy': [ROLE_SERVICE],
     'ReturnProxy': [ROLE_SERVICE],
     'Proxy': [ROLE_SERVICE]}
    __guid__ = 'svc.xmlrpcClient'
    __dependencies__ = []

    def Run(self, memStream = None):
        self.proxiesByKey = CachedMultiMap(10)
        self.dnsMap = {}



    def Stop(self, memStream):
        self.proxiesByKey.Clear()



    def GetProxy(self, uri, proxyClass = xmlrpclib.ServerProxy, proxyArgs = ()):
        key = (uri, proxyClass, proxyArgs)
        try:
            return (key, self.proxiesByKey.Pop(key))
        except KeyError:
            uri = self.FixUri(uri)
            return (key, proxyClass(uri, *proxyArgs))



    def ReturnProxy(self, key, proxy, discard = False):
        if not discard:
            self.proxiesByKey.Insert(key, proxy)



    def FixUri(self, uri):
        parts = urlparse.urlsplit(uri)
        key = parts[1]
        try:
            while True:
                netloc = self.dnsMap[key]
                if isinstance(netloc, locks.Event):
                    netloc.wait()
                else:
                    break

        except KeyError:
            event = locks.Event()
            self.dnsMap[key] = event
            try:
                try:
                    netloc = key
                    hostport = netloc.split(':')
                    if len(hostport) == 2:
                        (host, port,) = hostport
                    else:
                        (host, port,) = (hostport[0], None)
                    try:
                        info = socket.getaddrinfo(host, port)
                        info = [ e for e in info if e[0] == socket.AF_INET ]
                        if info:
                            if port is not None:
                                (host, port,) = info[0][4]
                                netloc = host + ':' + str(port)
                            else:
                                netloc = host
                    except socket.gaierror:
                        pass
                except:
                    del self.dnsMap[key]
                else:
                    self.dnsMap[key] = netloc

            finally:
                event.set()

        if netloc != parts[1]:
            uri = urlparse.urlunsplit((parts[0],) + (netloc,) + parts[2:])
        return uri



    def Call(self, uri, method, *args, **kw):
        with self.ProxyContext(uri, kw.get('proxyClass', xmlrpclib.ServerProxy), kw.get('proxyArgs', ())) as p:
            return getattr(p, method)(*args)



    @contextlib.contextmanager
    def Proxy(self, uri, proxyClass = xmlrpclib.ServerProxy, proxyArgs = ()):
        (k, p,) = self.GetProxy(uri, proxyClass, proxyArgs)
        discard = False
        try:
            try:
                yield p
            except socket.error:
                discard = True
                raise 

        finally:
            self.ReturnProxy(k, p, discard)





