#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\contrib\cache.py
import os
import re
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

from itertools import izip
from time import time
from cPickle import loads, dumps, load, dump, HIGHEST_PROTOCOL

class BaseCache(object):

    def __init__(self, default_timeout = 300):
        self.default_timeout = default_timeout

    def get(self, key):
        return None

    def delete(self, key):
        pass

    def get_many(self, *keys):
        return map(self.get, keys)

    def get_dict(self, *keys):
        return dict(izip(keys, self.get_many(*keys)))

    def set(self, key, value, timeout = None):
        pass

    def add(self, key, value, timeout = None):
        pass

    def set_many(self, mapping, timeout = None):
        for key, value in mapping.iteritems():
            self.set(key, value, timeout)

    def delete_many(self, *keys):
        for key in keys:
            self.delete(key)

    def clear(self):
        pass

    def inc(self, key, delta = 1):
        self.set(key, (self.get(key) or 0) + delta)

    def dec(self, key, delta = 1):
        self.set(key, (self.get(key) or 0) - delta)


class NullCache(BaseCache):
    pass


class SimpleCache(BaseCache):

    def __init__(self, threshold = 500, default_timeout = 300):
        BaseCache.__init__(self, default_timeout)
        self._cache = {}
        self.clear = self._cache.clear
        self._threshold = threshold

    def _prune(self):
        if len(self._cache) > self._threshold:
            now = time()
            for idx, (key, (expires, _)) in enumerate(self._cache.items()):
                if expires <= now or idx % 3 == 0:
                    self._cache.pop(key, None)

    def get(self, key):
        now = time()
        expires, value = self._cache.get(key, (0, None))
        if expires > time():
            return loads(value)

    def set(self, key, value, timeout = None):
        if timeout is None:
            timeout = self.default_timeout
        self._prune()
        self._cache[key] = (time() + timeout, dumps(value, HIGHEST_PROTOCOL))

    def add(self, key, value, timeout = None):
        if timeout is None:
            timeout = self.default_timeout
        if len(self._cache) > self._threshold:
            self._prune()
        item = (time() + timeout, dumps(value, HIGHEST_PROTOCOL))
        self._cache.setdefault(key, item)

    def delete(self, key):
        self._cache.pop(key, None)


_test_memcached_key = re.compile('[^\\x00-\\x21\\xff]{1,250}$').match

class MemcachedCache(BaseCache):

    def __init__(self, servers, default_timeout = 300, key_prefix = None):
        BaseCache.__init__(self, default_timeout)
        if isinstance(servers, (list, tuple)):
            try:
                import cmemcache as memcache
                is_cmemcache = True
            except ImportError:
                try:
                    import memcache
                    is_cmemcache = False
                except ImportError:
                    raise RuntimeError('no memcache module found')

            if is_cmemcache:
                client = memcache.Client(map(str, servers))
                try:
                    client.debuglog = lambda *a: None
                except:
                    pass

            else:
                client = memcache.Client(servers, False, HIGHEST_PROTOCOL)
        else:
            client = servers
        self._client = client
        self.key_prefix = key_prefix

    def get(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key
        if _test_memcached_key(key):
            return self._client.get(key)

    def get_dict(self, *keys):
        key_mapping = {}
        have_encoded_keys = False
        for idx, key in enumerate(keys):
            if isinstance(key, unicode):
                encoded_key = key.encode('utf-8')
                have_encoded_keys = True
            else:
                encoded_key = key
            if self.key_prefix:
                encoded_key = self.key_prefix + encoded_key
            if _test_memcached_key(key):
                key_mapping[encoded_key] = key

        d = rv = self._client.get_multi(key_mapping.keys())
        if have_encoded_keys or self.key_prefix:
            rv = {}
            for key, value in d.iteritems():
                rv[key_mapping[key]] = value

        if len(rv) < len(keys):
            for key in keys:
                if key not in rv:
                    rv[key] = None

        return rv

    def add(self, key, value, timeout = None):
        if timeout is None:
            timeout = self.default_timeout
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key
        self._client.add(key, value, timeout)

    def set(self, key, value, timeout = None):
        if timeout is None:
            timeout = self.default_timeout
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key
        self._client.set(key, value, timeout)

    def get_many(self, *keys):
        d = self.get_dict(*keys)
        return [ d[key] for key in keys ]

    def set_many(self, mapping, timeout = None):
        if timeout is None:
            timeout = self.default_timeout
        new_mapping = {}
        for key, value in mapping.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if self.key_prefix:
                key = self.key_prefix + key
            new_mapping[key] = value

        self._client.set_multi(new_mapping, timeout)

    def delete(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key
        if _test_memcached_key(key):
            self._client.delete(key)

    def delete_many(self, *keys):
        new_keys = []
        for key in keys:
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if self.key_prefix:
                key = self.key_prefix + key
            if _test_memcached_key(key):
                new_keys.append(key)

        self._client.delete_multi(new_keys)

    def clear(self):
        self._client.flush_all()

    def inc(self, key, delta = 1):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key
        self._client.incr(key, delta)

    def dec(self, key, delta = 1):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key
        self._client.decr(key, delta)


class GAEMemcachedCache(MemcachedCache):

    def __init__(self, default_timeout = 300, key_prefix = None):
        from google.appengine.api import memcache
        MemcachedCache.__init__(self, memcache.Client(), default_timeout, key_prefix)


class FileSystemCache(BaseCache):

    def __init__(self, cache_dir, threshold = 500, default_timeout = 300):
        BaseCache.__init__(self, default_timeout)
        self._path = cache_dir
        self._threshold = threshold
        if not os.path.exists(self._path):
            os.makedirs(self._path)

    def _prune(self):
        entries = os.listdir(self._path)
        if len(entries) > self._threshold:
            now = time()
            for idx, key in enumerate(entries):
                try:
                    f = file(self._get_filename(key))
                    if load(f) > now and idx % 3 != 0:
                        f.close()
                        continue
                except:
                    f.close()

                self.delete(key)

    def _get_filename(self, key):
        hash = md5(key).hexdigest()
        return os.path.join(self._path, hash)

    def get(self, key):
        filename = self._get_filename(key)
        try:
            f = file(filename, 'rb')
            try:
                if load(f) >= time():
                    return load(f)
            finally:
                f.close()

            os.remove(filename)
        except:
            return

    def add(self, key, value, timeout = None):
        filename = self._get_filename(key)
        if not os.path.exists(filename):
            self.set(key, value, timeout)

    def set(self, key, value, timeout = None):
        if timeout is None:
            timeout = self.default_timeout
        filename = self._get_filename(key)
        self._prune()
        try:
            f = file(filename, 'wb')
            try:
                dump(int(time() + timeout), f, 1)
                dump(value, f, HIGHEST_PROTOCOL)
            finally:
                f.close()

        except (IOError, OSError):
            pass

    def delete(self, key):
        try:
            os.remove(self._get_filename(key))
        except (IOError, OSError):
            pass

    def clear(self):
        for key in os.listdir(self._path):
            self.delete(key)