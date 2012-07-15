#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\test.py
import sys
import urllib
import urlparse
import mimetypes
from time import time
from random import random
from itertools import chain
from tempfile import TemporaryFile
from cStringIO import StringIO
from cookielib import CookieJar
from urllib2 import Request as U2Request
from werkzeug._internal import _empty_stream, _get_environ
from werkzeug.wrappers import BaseRequest
from werkzeug.urls import url_encode, url_fix, iri_to_uri
from werkzeug.wsgi import get_host, get_current_url
from werkzeug.datastructures import FileMultiDict, MultiDict, CombinedMultiDict, Headers, FileStorage

def stream_encode_multipart(values, use_tempfile = True, threshold = 1024 * 500, boundary = None, charset = 'utf-8'):
    if boundary is None:
        boundary = '---------------WerkzeugFormPart_%s%s' % (time(), random())
    _closure = [StringIO(), 0, False]
    if use_tempfile:

        def write(string):
            stream, total_length, on_disk = _closure
            if on_disk:
                stream.write(string)
            else:
                length = len(string)
                if length + _closure[1] <= threshold:
                    stream.write(string)
                else:
                    new_stream = TemporaryFile('wb+')
                    new_stream.write(stream.getvalue())
                    new_stream.write(string)
                    _closure[0] = new_stream
                    _closure[2] = True
                _closure[1] = total_length + length

    else:
        write = _closure[0].write
    if not isinstance(values, MultiDict):
        values = MultiDict(values)
    for key, values in values.iterlists():
        for value in values:
            write('--%s\r\nContent-Disposition: form-data; name="%s"' % (boundary, key))
            reader = getattr(value, 'read', None)
            if reader is not None:
                filename = getattr(value, 'filename', getattr(value, 'name', None))
                content_type = getattr(value, 'content_type', None)
                if content_type is None:
                    content_type = filename and mimetypes.guess_type(filename)[0] or 'application/octet-stream'
                if filename is not None:
                    write('; filename="%s"\r\n' % filename)
                else:
                    write('\r\n')
                write('Content-Type: %s\r\n\r\n' % content_type)
                while 1:
                    chunk = reader(16384)
                    if not chunk:
                        break
                    write(chunk)

            else:
                if isinstance(value, unicode):
                    value = value.encode(charset)
                write('\r\n\r\n' + value)
            write('\r\n')

    write('--%s--\r\n' % boundary)
    length = int(_closure[0].tell())
    _closure[0].seek(0)
    return (_closure[0], length, boundary)


def encode_multipart(values, boundary = None, charset = 'utf-8'):
    stream, length, boundary = stream_encode_multipart(values, use_tempfile=False, boundary=boundary, charset=charset)
    return (boundary, stream.read())


def File(fd, filename = None, mimetype = None):
    from warnings import warn
    warn(DeprecationWarning('werkzeug.test.File is deprecated, use the EnvironBuilder or FileStorage instead'))
    return FileStorage(fd, filename=filename, content_type=mimetype)


class _TestCookieHeaders(object):

    def __init__(self, headers):
        self.headers = headers

    def getheaders(self, name):
        headers = []
        name = name.lower()
        for k, v in self.headers:
            if k.lower() == name:
                headers.append(v)

        return headers


class _TestCookieResponse(object):

    def __init__(self, headers):
        self.headers = _TestCookieHeaders(headers)

    def info(self):
        return self.headers


class _TestCookieJar(CookieJar):

    def inject_wsgi(self, environ):
        cvals = []
        for cookie in self:
            cvals.append('%s=%s' % (cookie.name, cookie.value))

        if cvals:
            environ['HTTP_COOKIE'] = ', '.join(cvals)

    def extract_wsgi(self, environ, headers):
        self.extract_cookies(_TestCookieResponse(headers), U2Request(get_current_url(environ)))


def _iter_data(data):
    if isinstance(data, MultiDict):
        for key, values in data.iterlists():
            for value in values:
                yield (key, value)

    else:
        for key, values in data.iteritems():
            if isinstance(values, list):
                for value in values:
                    yield (key, value)

            else:
                yield (key, values)


class EnvironBuilder(object):
    server_protocol = 'HTTP/1.1'
    wsgi_version = (1, 0)
    request_class = BaseRequest

    def __init__(self, path = '/', base_url = None, query_string = None, method = 'GET', input_stream = None, content_type = None, content_length = None, errors_stream = None, multithread = False, multiprocess = False, run_once = False, headers = None, data = None, environ_base = None, environ_overrides = None, charset = 'utf-8'):
        if query_string is None and '?' in path:
            path, query_string = path.split('?', 1)
        self.charset = charset
        if isinstance(path, unicode):
            path = iri_to_uri(path, charset)
        self.path = path
        if base_url is not None:
            if isinstance(base_url, unicode):
                base_url = iri_to_uri(base_url, charset)
            else:
                base_url = url_fix(base_url, charset)
        self.base_url = base_url
        if isinstance(query_string, basestring):
            self.query_string = query_string
        else:
            if query_string is None:
                query_string = MultiDict()
            elif not isinstance(query_string, MultiDict):
                query_string = MultiDict(query_string)
            self.args = query_string
        self.method = method
        if headers is None:
            headers = Headers()
        elif not isinstance(headers, Headers):
            headers = Headers(headers)
        self.headers = headers
        self.content_type = content_type
        if errors_stream is None:
            errors_stream = sys.stderr
        self.errors_stream = errors_stream
        self.multithread = multithread
        self.multiprocess = multiprocess
        self.run_once = run_once
        self.environ_base = environ_base
        self.environ_overrides = environ_overrides
        self.input_stream = input_stream
        self.content_length = content_length
        self.closed = False
        if data:
            if input_stream is not None:
                raise TypeError("can't provide input stream and data")
            if isinstance(data, basestring):
                self.input_stream = StringIO(data)
                if self.content_length is None:
                    self.content_length = len(data)
            else:
                for key, value in _iter_data(data):
                    if isinstance(value, (tuple, dict)) or hasattr(value, 'read'):
                        self._add_file_from_data(key, value)
                    else:
                        self.form.setlistdefault(key).append(value)

    def _add_file_from_data(self, key, value):
        if isinstance(value, tuple):
            self.files.add_file(key, *value)
        elif isinstance(value, dict):
            from warnings import warn
            warn(DeprecationWarning("it's no longer possible to pass dicts as `data`.  Use tuples or FileStorage objects instead"), stacklevel=2)
            args = v
            value = dict(value)
            mimetype = value.pop('mimetype', None)
            if mimetype is not None:
                value['content_type'] = mimetype
            self.files.add_file(key, **value)
        else:
            self.files.add_file(key, value)

    def _get_base_url(self):
        return urlparse.urlunsplit((self.url_scheme,
         self.host,
         self.script_root,
         '',
         '')).rstrip('/') + '/'

    def _set_base_url(self, value):
        if value is None:
            scheme = 'http'
            netloc = 'localhost'
            scheme = 'http'
            script_root = ''
        else:
            scheme, netloc, script_root, qs, anchor = urlparse.urlsplit(value)
            if qs or anchor:
                raise ValueError('base url must not contain a query string or fragment')
        self.script_root = script_root.rstrip('/')
        self.host = netloc
        self.url_scheme = scheme

    base_url = property(_get_base_url, _set_base_url, doc='\n        The base URL is a URL that is used to extract the WSGI\n        URL scheme, host (server name + server port) and the\n        script root (`SCRIPT_NAME`).')
    del _get_base_url
    del _set_base_url

    def _get_content_type(self):
        ct = self.headers.get('Content-Type')
        if ct is None and not self._input_stream:
            if self.method in ('POST', 'PUT'):
                if self._files:
                    return 'multipart/form-data'
                return 'application/x-www-form-urlencoded'
            return
        return ct

    def _set_content_type(self, value):
        if value is None:
            self.headers.pop('Content-Type', None)
        else:
            self.headers['Content-Type'] = value

    content_type = property(_get_content_type, _set_content_type, doc='\n        The content type for the request.  Reflected from and to the\n        :attr:`headers`.  Do not set if you set :attr:`files` or\n        :attr:`form` for auto detection.')
    del _get_content_type
    del _set_content_type

    def _get_content_length(self):
        return self.headers.get('Content-Length', type=int)

    def _set_content_length(self, value):
        if value is None:
            self.headers.pop('Content-Length', None)
        else:
            self.headers['Content-Length'] = str(value)

    content_length = property(_get_content_length, _set_content_length, doc='\n        The content length as integer.  Reflected from and to the\n        :attr:`headers`.  Do not set if you set :attr:`files` or\n        :attr:`form` for auto detection.')
    del _get_content_length
    del _set_content_length

    def form_property(name, storage, doc):
        key = '_' + name

        def getter(self):
            if self._input_stream is not None:
                raise AttributeError('an input stream is defined')
            rv = getattr(self, key)
            if rv is None:
                rv = storage()
                setattr(self, key, rv)
            return rv

        def setter(self, value):
            self._input_stream = None
            setattr(self, key, value)

        return property(getter, setter, doc)

    form = form_property('form', MultiDict, doc='\n        A :class:`MultiDict` of form values.')
    files = form_property('files', FileMultiDict, doc='\n        A :class:`FileMultiDict` of uploaded files.  You can use the\n        :meth:`~FileMultiDict.add_file` method to add new files to the\n        dict.')
    del form_property

    def _get_input_stream(self):
        return self._input_stream

    def _set_input_stream(self, value):
        self._input_stream = value
        self._form = self._files = None

    input_stream = property(_get_input_stream, _set_input_stream, doc='\n        An optional input stream.  If you set this it will clear\n        :attr:`form` and :attr:`files`.')
    del _get_input_stream
    del _set_input_stream

    def _get_query_string(self):
        if self._query_string is None:
            if self._args is not None:
                return url_encode(self._args, charset=self.charset)
            return ''
        return self._query_string

    def _set_query_string(self, value):
        self._query_string = value
        self._args = None

    query_string = property(_get_query_string, _set_query_string, doc='\n        The query string.  If you set this to a string :attr:`args` will\n        no longer be available.')
    del _get_query_string
    del _set_query_string

    def _get_args(self):
        if self._query_string is not None:
            raise AttributeError('a query string is defined')
        if self._args is None:
            self._args = MultiDict()
        return self._args

    def _set_args(self, value):
        self._query_string = None
        self._args = value

    args = property(_get_args, _set_args, doc='\n        The URL arguments as :class:`MultiDict`.')
    del _get_args
    del _set_args

    @property
    def server_name(self):
        return self.host.split(':', 1)[0]

    @property
    def server_port(self):
        pieces = self.host.split(':', 1)
        if len(pieces) == 2 and pieces[1].isdigit():
            return int(pieces[1])
        if self.url_scheme == 'https':
            return 443
        return 80

    def __del__(self):
        self.close()

    def close(self):
        if self.closed:
            return
        try:
            files = self.files.itervalues()
        except AttributeError:
            files = ()

        for f in files:
            try:
                f.close()
            except Exception as e:
                pass

        self.closed = True

    def get_environ(self):
        input_stream = self.input_stream
        content_length = self.content_length
        content_type = self.content_type
        if input_stream is not None:
            start_pos = input_stream.tell()
            input_stream.seek(0, 2)
            end_pos = input_stream.tell()
            input_stream.seek(start_pos)
            content_length = end_pos - start_pos
        elif content_type == 'multipart/form-data':
            values = CombinedMultiDict([self.form, self.files])
            input_stream, content_length, boundary = stream_encode_multipart(values, charset=self.charset)
            content_type += '; boundary="%s"' % boundary
        elif content_type == 'application/x-www-form-urlencoded':
            values = url_encode(self.form, charset=self.charset)
            content_length = len(values)
            input_stream = StringIO(values)
        else:
            input_stream = _empty_stream
        result = {}
        if self.environ_base:
            result.update(self.environ_base)

        def _path_encode(x):
            if isinstance(x, unicode):
                x = x.encode(self.charset)
            return urllib.unquote(x)

        result.update({'REQUEST_METHOD': self.method,
         'SCRIPT_NAME': _path_encode(self.script_root),
         'PATH_INFO': _path_encode(self.path),
         'QUERY_STRING': self.query_string,
         'SERVER_NAME': self.server_name,
         'SERVER_PORT': str(self.server_port),
         'HTTP_HOST': self.host,
         'SERVER_PROTOCOL': self.server_protocol,
         'CONTENT_TYPE': content_type or '',
         'CONTENT_LENGTH': str(content_length or '0'),
         'wsgi.version': self.wsgi_version,
         'wsgi.url_scheme': self.url_scheme,
         'wsgi.input': input_stream,
         'wsgi.errors': self.errors_stream,
         'wsgi.multithread': self.multithread,
         'wsgi.multiprocess': self.multiprocess,
         'wsgi.run_once': self.run_once})
        for key, value in self.headers.to_list(self.charset):
            result['HTTP_%s' % key.upper().replace('-', '_')] = value

        if self.environ_overrides:
            result.update(self.environ_overrides)
        return result

    def get_request(self, cls = None):
        if cls is None:
            cls = self.request_class
        return cls(self.get_environ())


class ClientRedirectError(Exception):
    pass


class Client(object):

    def __init__(self, application, response_wrapper = None, use_cookies = True):
        self.application = application
        if response_wrapper is None:
            response_wrapper = lambda a, s, h: (a, s, h)
        self.response_wrapper = response_wrapper
        if use_cookies:
            self.cookie_jar = _TestCookieJar()
        else:
            self.cookie_jar = None
        self.redirect_client = None

    def open(self, *args, **kwargs):
        as_tuple = kwargs.pop('as_tuple', False)
        buffered = kwargs.pop('buffered', False)
        follow_redirects = kwargs.pop('follow_redirects', False)
        environ = None
        if not kwargs and len(args) == 1:
            if isinstance(args[0], EnvironBuilder):
                environ = args[0].get_environ()
            elif isinstance(args[0], dict):
                environ = args[0]
        if environ is None:
            builder = EnvironBuilder(*args, **kwargs)
            try:
                environ = builder.get_environ()
            finally:
                builder.close()

        if self.cookie_jar is not None:
            self.cookie_jar.inject_wsgi(environ)
        rv = run_wsgi_app(self.application, environ, buffered=buffered)
        if self.cookie_jar is not None:
            self.cookie_jar.extract_wsgi(environ, rv[2])
        redirect_chain = []
        status_code = int(rv[1].split(None, 1)[0])
        while status_code in (301, 302, 303, 305, 307) and follow_redirects:
            if not self.redirect_client:
                self.redirect_client = Client(self.application)
                self.redirect_client.cookie_jar = self.cookie_jar
            redirect = dict(rv[2])['Location']
            scheme, netloc, script_root, qs, anchor = urlparse.urlsplit(redirect)
            base_url = urlparse.urlunsplit((scheme,
             netloc,
             '',
             '',
             '')).rstrip('/') + '/'
            host = get_host(create_environ('/', base_url, query_string=qs)).split(':', 1)[0]
            if get_host(environ).split(':', 1)[0] != host:
                raise RuntimeError('%r does not support redirect to external targets' % self.__class__)
            redirect_chain.append((redirect, status_code))
            redirect_kwargs = {}
            redirect_kwargs.update({'path': script_root,
             'base_url': base_url,
             'query_string': qs,
             'as_tuple': True,
             'buffered': buffered,
             'follow_redirects': False})
            environ, rv = self.redirect_client.open(**redirect_kwargs)
            status_code = int(rv[1].split(None, 1)[0])
            if redirect_chain[-1] in redirect_chain[0:-1]:
                raise ClientRedirectError('loop detected')

        response = self.response_wrapper(*rv)
        if as_tuple:
            return (environ, response)
        return response

    def get(self, *args, **kw):
        kw['method'] = 'GET'
        return self.open(*args, **kw)

    def post(self, *args, **kw):
        kw['method'] = 'POST'
        return self.open(*args, **kw)

    def head(self, *args, **kw):
        kw['method'] = 'HEAD'
        return self.open(*args, **kw)

    def put(self, *args, **kw):
        kw['method'] = 'PUT'
        return self.open(*args, **kw)

    def delete(self, *args, **kw):
        kw['method'] = 'DELETE'
        return self.open(*args, **kw)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.application)


def create_environ(*args, **kwargs):
    builder = EnvironBuilder(*args, **kwargs)
    try:
        return builder.get_environ()
    finally:
        builder.close()


def run_wsgi_app(app, environ, buffered = False):
    environ = _get_environ(environ)
    response = []
    buffer = []

    def start_response(status, headers, exc_info = None):
        if exc_info is not None:
            raise exc_info[0], exc_info[1], exc_info[2]
        response[:] = [status, headers]
        return buffer.append

    app_iter = app(environ, start_response)
    if buffered:
        close_func = getattr(app_iter, 'close', None)
        try:
            app_iter = list(app_iter)
        finally:
            if close_func is not None:
                close_func()

    else:
        while not response:
            buffer.append(app_iter.next())

        if buffer:
            close_func = getattr(app_iter, 'close', None)
            app_iter = chain(buffer, app_iter)
            if close_func is not None:
                app_iter = ClosingIterator(app_iter, close_func)
    return (app_iter, response[0], response[1])


from werkzeug.wsgi import ClosingIterator