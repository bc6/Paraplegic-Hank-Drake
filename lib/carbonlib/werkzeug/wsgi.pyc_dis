#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\wsgi.py
import os
import urllib
import urlparse
import posixpath
import mimetypes
from zlib import adler32
from time import time, mktime
from datetime import datetime
from werkzeug._internal import _patch_wrapper

def responder(f):
    return _patch_wrapper(f, lambda *a: f(*a)(*a[-2:]))


def get_current_url(environ, root_only = False, strip_querystring = False, host_only = False):
    tmp = [environ['wsgi.url_scheme'], '://', get_host(environ)]
    cat = tmp.append
    if host_only:
        return ''.join(tmp) + '/'
    cat(urllib.quote(environ.get('SCRIPT_NAME', '').rstrip('/')))
    if root_only:
        cat('/')
    else:
        cat(urllib.quote('/' + environ.get('PATH_INFO', '').lstrip('/')))
        if not strip_querystring:
            qs = environ.get('QUERY_STRING')
            if qs:
                cat('?' + qs)
    return ''.join(tmp)


def get_host(environ):
    if 'HTTP_X_FORWARDED_HOST' in environ:
        return environ['HTTP_X_FORWARDED_HOST']
    if 'HTTP_HOST' in environ:
        return environ['HTTP_HOST']
    result = environ['SERVER_NAME']
    if (environ['wsgi.url_scheme'], environ['SERVER_PORT']) not in (('https', '443'), ('http', '80')):
        result += ':' + environ['SERVER_PORT']
    return result


def pop_path_info(environ):
    path = environ.get('PATH_INFO')
    if not path:
        return None
    script_name = environ.get('SCRIPT_NAME', '')
    old_path = path
    path = path.lstrip('/')
    if path != old_path:
        script_name += '/' * (len(old_path) - len(path))
    if '/' not in path:
        environ['PATH_INFO'] = ''
        environ['SCRIPT_NAME'] = script_name + path
        return path
    segment, path = path.split('/', 1)
    environ['PATH_INFO'] = '/' + path
    environ['SCRIPT_NAME'] = script_name + segment
    return segment


def peek_path_info(environ):
    segments = environ.get('PATH_INFO', '').lstrip('/').split('/', 1)
    if segments:
        return segments[0]


def extract_path_info(environ_or_baseurl, path_or_url, charset = 'utf-8', errors = 'ignore', collapse_http_schemes = True):
    from werkzeug.urls import uri_to_iri, url_fix

    def _as_iri(obj):
        if not isinstance(obj, unicode):
            return uri_to_iri(obj, charset, errors)
        return obj

    def _normalize_netloc(scheme, netloc):
        parts = netloc.split(u'@', 1)[-1].split(u':', 1)
        if len(parts) == 2:
            netloc, port = parts
            if scheme == u'http' and port == u'80' or scheme == u'https' and port == u'443':
                port = None
        else:
            netloc = parts[0]
            port = None
        if port is not None:
            netloc += u':' + port
        return netloc

    path = _as_iri(path_or_url)
    if isinstance(environ_or_baseurl, dict):
        environ_or_baseurl = get_current_url(environ_or_baseurl, root_only=True)
    base_iri = _as_iri(environ_or_baseurl)
    base_scheme, base_netloc, base_path = urlparse.urlsplit(base_iri)[:3]
    cur_scheme, cur_netloc, cur_path = urlparse.urlsplit(urlparse.urljoin(base_iri, path))[:3]
    base_netloc = _normalize_netloc(base_scheme, base_netloc)
    cur_netloc = _normalize_netloc(cur_scheme, cur_netloc)
    if collapse_http_schemes:
        for scheme in (base_scheme, cur_scheme):
            if scheme not in (u'http', u'https'):
                return None

    elif not (base_scheme in (u'http', u'https') and base_scheme == cur_scheme):
        return None
    if base_netloc != cur_netloc:
        return None
    base_path = base_path.rstrip(u'/')
    if not cur_path.startswith(base_path):
        return None
    return u'/' + cur_path[len(base_path):].lstrip(u'/')


class SharedDataMiddleware(object):

    def __init__(self, app, exports, disallow = None, cache = True, cache_timeout = 43200, fallback_mimetype = 'text/plain'):
        self.app = app
        self.exports = {}
        self.cache = cache
        self.cache_timeout = cache_timeout
        for key, value in exports.iteritems():
            if isinstance(value, tuple):
                loader = self.get_package_loader(*value)
            elif isinstance(value, basestring):
                if os.path.isfile(value):
                    loader = self.get_file_loader(value)
                else:
                    loader = self.get_directory_loader(value)
            else:
                raise TypeError('unknown def %r' % value)
            self.exports[key] = loader

        if disallow is not None:
            from fnmatch import fnmatch
            self.is_allowed = lambda x: not fnmatch(x, disallow)
        self.fallback_mimetype = fallback_mimetype

    def is_allowed(self, filename):
        return True

    def _opener(self, filename):
        return lambda : (open(filename, 'rb'), datetime.utcfromtimestamp(os.path.getmtime(filename)), int(os.path.getsize(filename)))

    def get_file_loader(self, filename):
        return lambda x: (os.path.basename(filename), self._opener(filename))

    def get_package_loader(self, package, package_path):
        from pkg_resources import DefaultProvider, ResourceManager, get_provider
        loadtime = datetime.utcnow()
        provider = get_provider(package)
        manager = ResourceManager()
        filesystem_bound = isinstance(provider, DefaultProvider)

        def loader(path):
            path = posixpath.join(package_path, path)
            if path is None or not provider.has_resource(path):
                return (None, None)
            basename = posixpath.basename(path)
            if filesystem_bound:
                return (basename, self._opener(provider.get_resource_filename(manager, path)))
            return (basename, lambda : (provider.get_resource_stream(manager, path), loadtime, 0))

        return loader

    def get_directory_loader(self, directory):

        def loader(path):
            if path is not None:
                path = os.path.join(directory, path)
            else:
                path = directory
            if os.path.isfile(path):
                return (os.path.basename(path), self._opener(path))
            return (None, None)

        return loader

    def generate_etag(self, mtime, file_size, real_filename):
        return 'wzsdm-%d-%s-%s' % (mktime(mtime.timetuple()), file_size, adler32(real_filename) & 4294967295L)

    def __call__(self, environ, start_response):
        cleaned_path = environ.get('PATH_INFO', '').strip('/')
        for sep in (os.sep, os.altsep):
            if sep and sep != '/':
                cleaned_path = cleaned_path.replace(sep, '/')

        path = '/'.join([''] + [ x for x in cleaned_path.split('/') if x and x != '..' ])
        file_loader = None
        for search_path, loader in self.exports.iteritems():
            if search_path == path:
                real_filename, file_loader = loader(None)
                if file_loader is not None:
                    break
            if not search_path.endswith('/'):
                search_path += '/'
            if path.startswith(search_path):
                real_filename, file_loader = loader(path[len(search_path):])
                if file_loader is not None:
                    break

        if file_loader is None or not self.is_allowed(real_filename):
            return self.app(environ, start_response)
        guessed_type = mimetypes.guess_type(real_filename)
        mime_type = guessed_type[0] or self.fallback_mimetype
        f, mtime, file_size = file_loader()
        headers = [('Date', http_date())]
        if self.cache:
            timeout = self.cache_timeout
            etag = self.generate_etag(mtime, file_size, real_filename)
            headers += [('Etag', '"%s"' % etag), ('Cache-Control', 'max-age=%d, public' % timeout)]
            if not is_resource_modified(environ, etag, last_modified=mtime):
                f.close()
                start_response('304 Not Modified', headers)
                return []
            headers.append(('Expires', http_date(time() + timeout)))
        else:
            headers.append(('Cache-Control', 'public'))
        headers.extend((('Content-Type', mime_type), ('Content-Length', str(file_size)), ('Last-Modified', http_date(mtime))))
        start_response('200 OK', headers)
        return wrap_file(environ, f)


class DispatcherMiddleware(object):

    def __init__(self, app, mounts = None):
        self.app = app
        self.mounts = mounts or {}

    def __call__(self, environ, start_response):
        script = environ.get('PATH_INFO', '')
        path_info = ''
        while '/' in script:
            if script in self.mounts:
                app = self.mounts[script]
                break
            items = script.split('/')
            script = '/'.join(items[:-1])
            path_info = '/%s%s' % (items[-1], path_info)
        else:
            app = self.mounts.get(script, self.app)

        original_script_name = environ.get('SCRIPT_NAME', '')
        environ['SCRIPT_NAME'] = original_script_name + script
        environ['PATH_INFO'] = path_info
        return app(environ, start_response)


class ClosingIterator(object):

    def __init__(self, iterable, callbacks = None):
        iterator = iter(iterable)
        self._next = iterator.next
        if callbacks is None:
            callbacks = []
        elif callable(callbacks):
            callbacks = [callbacks]
        else:
            callbacks = list(callbacks)
        iterable_close = getattr(iterator, 'close', None)
        if iterable_close:
            callbacks.insert(0, iterable_close)
        self._callbacks = callbacks

    def __iter__(self):
        return self

    def next(self):
        return self._next()

    def close(self):
        for callback in self._callbacks:
            callback()


def wrap_file(environ, file, buffer_size = 8192):
    return environ.get('wsgi.file_wrapper', FileWrapper)(file, buffer_size)


class FileWrapper(object):

    def __init__(self, file, buffer_size = 8192):
        self.file = file
        self.buffer_size = buffer_size

    def close(self):
        if hasattr(self.file, 'close'):
            self.file.close()

    def __iter__(self):
        return self

    def next(self):
        data = self.file.read(self.buffer_size)
        if data:
            return data
        raise StopIteration()


def make_line_iter(stream, limit = None, buffer_size = 10240):
    if not isinstance(stream, LimitedStream):
        if limit is None:
            raise TypeError('stream not limited and no limit provided.')
        stream = LimitedStream(stream, limit)
    _read = stream.read
    buffer = []
    while 1:
        if len(buffer) > 1:
            yield buffer.pop()
            continue
        chunks = _read(buffer_size).splitlines(True)
        chunks.reverse()
        first_chunk = buffer and buffer[0] or ''
        if chunks:
            first_chunk += chunks.pop()
        if not first_chunk:
            return
        buffer = chunks
        yield first_chunk


class LimitedStream(object):

    def __init__(self, stream, limit, silent = True):
        self._read = stream.read
        self._readline = stream.readline
        self._pos = 0
        self.limit = limit
        self.silent = silent
        if not silent:
            from warnings import warn
            warn(DeprecationWarning('non-silent usage of the LimitedStream is deprecated.  If you want to continue to use the stream in non-silent usage override on_exhausted.'), stacklevel=2)

    def __iter__(self):
        return self

    @property
    def is_exhausted(self):
        return self._pos >= self.limit

    def on_exhausted(self):
        if self.silent:
            return ''
        from werkzeug.exceptions import BadRequest
        raise BadRequest('input stream exhausted')

    def exhaust(self, chunk_size = 16384):
        to_read = self.limit - self._pos
        chunk = chunk_size
        while to_read > 0:
            chunk = min(to_read, chunk)
            self.read(chunk)
            to_read -= chunk

    def read(self, size = None):
        if self._pos >= self.limit:
            return self.on_exhausted()
        if size is None:
            size = self.limit
        read = self._read(min(self.limit - self._pos, size))
        self._pos += len(read)
        return read

    def readline(self, size = None):
        if self._pos >= self.limit:
            return self.on_exhausted()
        if size is None:
            size = self.limit - self._pos
        else:
            size = min(size, self.limit - self._pos)
        line = self._readline(size)
        self._pos += len(line)
        return line

    def readlines(self, size = None):
        last_pos = self._pos
        result = []
        if size is not None:
            end = min(self.limit, last_pos + size)
        else:
            end = self.limit
        while 1:
            if size is not None:
                size -= last_pos - self._pos
            if self._pos >= end:
                break
            result.append(self.readline(size))
            if size is not None:
                last_pos = self._pos

        return result

    def next(self):
        line = self.readline()
        if line is None:
            raise StopIteration()
        return line


from werkzeug.utils import http_date
from werkzeug.http import is_resource_modified