import datetime
import threading
import time
import cherrypy
from cherrypy.lib import cptools, httputil

class Cache(object):

    def get(self):
        raise NotImplemented



    def put(self, obj, size):
        raise NotImplemented



    def delete(self):
        raise NotImplemented



    def clear(self):
        raise NotImplemented




class AntiStampedeCache(dict):

    def wait(self, key, timeout = 5, debug = False):
        value = self.get(key)
        if isinstance(value, threading._Event):
            if timeout is None:
                if debug:
                    cherrypy.log('No timeout', 'TOOLS.CACHING')
                return 
            if debug:
                cherrypy.log('Waiting up to %s seconds' % timeout, 'TOOLS.CACHING')
            value.wait(timeout)
            if value.result is not None:
                if debug:
                    cherrypy.log('Result!', 'TOOLS.CACHING')
                return value.result
            if debug:
                cherrypy.log('Timed out', 'TOOLS.CACHING')
            e = threading.Event()
            e.result = None
            dict.__setitem__(self, key, e)
            return 
        if value is None:
            if debug:
                cherrypy.log('Timed out', 'TOOLS.CACHING')
            e = threading.Event()
            e.result = None
            dict.__setitem__(self, key, e)
        return value



    def __setitem__(self, key, value):
        existing = self.get(key)
        dict.__setitem__(self, key, value)
        if isinstance(existing, threading._Event):
            existing.result = value
            existing.set()




class MemoryCache(Cache):
    maxobjects = 1000
    maxobj_size = 100000
    maxsize = 10000000
    delay = 600
    antistampede_timeout = 5
    expire_freq = 0.1
    debug = False

    def __init__(self):
        self.clear()
        t = threading.Thread(target=self.expire_cache, name='expire_cache')
        self.expiration_thread = t
        if hasattr(threading.Thread, 'daemon'):
            t.daemon = True
        else:
            t.setDaemon(True)
        t.start()



    def clear(self):
        self.store = {}
        self.expirations = {}
        self.tot_puts = 0
        self.tot_gets = 0
        self.tot_hist = 0
        self.tot_expires = 0
        self.tot_non_modified = 0
        self.cursize = 0



    def expire_cache(self):
        while time:
            now = time.time()
            for (expiration_time, objects,) in self.expirations.items():
                if expiration_time <= now:
                    for (obj_size, uri, sel_header_values,) in objects:
                        try:
                            del self.store[uri][sel_header_values]
                            self.tot_expires += 1
                            self.cursize -= obj_size
                        except KeyError:
                            pass

                    del self.expirations[expiration_time]

            time.sleep(self.expire_freq)




    def get(self):
        request = cherrypy.serving.request
        self.tot_gets += 1
        uri = cherrypy.url(qs=request.query_string)
        uricache = self.store.get(uri)
        if uricache is None:
            return 
        header_values = [ request.headers.get(h, '') for h in uricache.selecting_headers ]
        header_values.sort()
        variant = uricache.wait(key=tuple(header_values), timeout=self.antistampede_timeout, debug=self.debug)
        if variant is not None:
            self.tot_hist += 1
        return variant



    def put(self, variant, size):
        request = cherrypy.serving.request
        response = cherrypy.serving.response
        uri = cherrypy.url(qs=request.query_string)
        uricache = self.store.get(uri)
        if uricache is None:
            uricache = AntiStampedeCache()
            uricache.selecting_headers = [ e.value for e in response.headers.elements('Vary') ]
            self.store[uri] = uricache
        if len(self.store) < self.maxobjects:
            total_size = self.cursize + size
            if size < self.maxobj_size and total_size < self.maxsize:
                expiration_time = response.time + self.delay
                bucket = self.expirations.setdefault(expiration_time, [])
                bucket.append((size, uri, uricache.selecting_headers))
                header_values = [ request.headers.get(h, '') for h in uricache.selecting_headers ]
                header_values.sort()
                uricache[tuple(header_values)] = variant
                self.tot_puts += 1
                self.cursize = total_size



    def delete(self):
        uri = cherrypy.url(qs=cherrypy.serving.request.query_string)
        self.store.pop(uri, None)




def get(invalid_methods = ('POST', 'PUT', 'DELETE'), debug = False, **kwargs):
    request = cherrypy.serving.request
    response = cherrypy.serving.response
    if not hasattr(cherrypy, '_cache'):
        cherrypy._cache = kwargs.pop('cache_class', MemoryCache)()
        for (k, v,) in kwargs.items():
            setattr(cherrypy._cache, k, v)

        cherrypy._cache.debug = debug
    if request.method in invalid_methods:
        if debug:
            cherrypy.log('request.method %r in invalid_methods %r' % (request.method, invalid_methods), 'TOOLS.CACHING')
        cherrypy._cache.delete()
        request.cached = False
        request.cacheable = False
        return False
    if 'no-cache' in [ e.value for e in request.headers.elements('Pragma') ]:
        request.cached = False
        request.cacheable = True
        return False
    cache_data = cherrypy._cache.get()
    request.cached = bool(cache_data)
    request.cacheable = not request.cached
    if request.cached:
        max_age = cherrypy._cache.delay
        for v in [ e.value for e in request.headers.elements('Cache-Control') ]:
            atoms = v.split('=', 1)
            directive = atoms.pop(0)
            if directive == 'max-age':
                if len(atoms) != 1 or not atoms[0].isdigit():
                    raise cherrypy.HTTPError(400, 'Invalid Cache-Control header')
                max_age = int(atoms[0])
                break
            else:
                if directive == 'no-cache':
                    if debug:
                        cherrypy.log('Ignoring cache due to Cache-Control: no-cache', 'TOOLS.CACHING')
                    request.cached = False
                    request.cacheable = True
                    return False

        if debug:
            cherrypy.log('Reading response from cache', 'TOOLS.CACHING')
        (s, h, b, create_time,) = cache_data
        age = int(response.time - create_time)
        if age > max_age:
            if debug:
                cherrypy.log('Ignoring cache due to age > %d' % max_age, 'TOOLS.CACHING')
            request.cached = False
            request.cacheable = True
            return False
        response.headers = rh = httputil.HeaderMap()
        for k in h:
            dict.__setitem__(rh, k, dict.__getitem__(h, k))

        response.headers['Age'] = str(age)
        try:
            cptools.validate_since()
        except cherrypy.HTTPRedirect as x:
            if x.status == 304:
                cherrypy._cache.tot_non_modified += 1
            raise 
        response.status = s
        response.body = b
    elif debug:
        cherrypy.log('request is not cached', 'TOOLS.CACHING')
    return request.cached



def tee_output():
    request = cherrypy.serving.request
    if 'no-store' in request.headers.values('Cache-Control'):
        return 

    def tee(body):
        if 'no-cache' in response.headers.values('Pragma') or 'no-store' in response.headers.values('Cache-Control'):
            for chunk in body:
                yield chunk

            return 
        output = []
        for chunk in body:
            output.append(chunk)
            yield chunk

        body = ''.join(output)
        cherrypy._cache.put((response.status,
         response.headers or {},
         body,
         response.time), len(body))


    response = cherrypy.serving.response
    response.body = tee(response.body)



def expires(secs = 0, force = False, debug = False):
    response = cherrypy.serving.response
    headers = response.headers
    cacheable = False
    if not force:
        for indicator in ('Etag', 'Last-Modified', 'Age', 'Expires'):
            if indicator in headers:
                cacheable = True
                break

    if not cacheable and not force:
        if debug:
            cherrypy.log('request is not cacheable', 'TOOLS.EXPIRES')
    elif debug:
        cherrypy.log('request is cacheable', 'TOOLS.EXPIRES')
    if isinstance(secs, datetime.timedelta):
        secs = 86400 * secs.days + secs.seconds
    if secs == 0:
        if force or 'Pragma' not in headers:
            headers['Pragma'] = 'no-cache'
        if cherrypy.serving.request.protocol >= (1, 1):
            if force or 'Cache-Control' not in headers:
                headers['Cache-Control'] = 'no-cache, must-revalidate'
        expiry = httputil.HTTPDate(1169942400.0)
    else:
        expiry = httputil.HTTPDate(response.time + secs)
    if force or 'Expires' not in headers:
        headers['Expires'] = expiry



