#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\wrappers.py
import tempfile
import urlparse
from datetime import datetime, timedelta
from werkzeug.http import HTTP_STATUS_CODES, parse_accept_header, parse_cache_control_header, parse_etags, parse_date, generate_etag, is_resource_modified, unquote_etag, quote_etag, parse_set_header, parse_authorization_header, parse_www_authenticate_header, remove_entity_headers, parse_options_header, dump_options_header
from werkzeug.urls import url_decode, iri_to_uri
from werkzeug.formparser import parse_form_data, default_stream_factory
from werkzeug.utils import cached_property, environ_property, cookie_date, parse_cookie, dump_cookie, http_date, escape, header_property, get_content_type
from werkzeug.wsgi import get_current_url, get_host, LimitedStream, ClosingIterator
from werkzeug.datastructures import MultiDict, CombinedMultiDict, Headers, EnvironHeaders, ImmutableMultiDict, ImmutableTypeConversionDict, ImmutableList, MIMEAccept, CharsetAccept, LanguageAccept, ResponseCacheControl, RequestCacheControl, CallbackDict
from werkzeug._internal import _empty_stream, _decode_unicode, _patch_wrapper, _get_environ

def _run_wsgi_app(*args):
    global _run_wsgi_app
    from werkzeug.test import run_wsgi_app as _run_wsgi_app
    return _run_wsgi_app(*args)


def _warn_if_string(iterable):
    if isinstance(iterable, basestring):
        from warnings import warn
        warn(Warning('response iterable was set to a string.  This appears to work but means that the server will send the data to the client char, by char.  This is almost never intended behavior, use response.data to assign strings to the response object.'), stacklevel=2)


class BaseRequest(object):
    charset = 'utf-8'
    encoding_errors = 'ignore'
    is_behind_proxy = False
    max_content_length = None
    max_form_memory_size = None
    parameter_storage_class = ImmutableMultiDict
    list_storage_class = ImmutableList
    dict_storage_class = ImmutableTypeConversionDict

    def __init__(self, environ, populate_request = True, shallow = False):
        self.environ = environ
        if populate_request and not shallow:
            self.environ['werkzeug.request'] = self
        self.shallow = shallow

    def __repr__(self):
        args = []
        try:
            args.append("'%s'" % self.url)
            args.append('[%s]' % self.method)
        except:
            args.append('(invalid WSGI environ)')

        return '<%s %s>' % (self.__class__.__name__, ' '.join(args))

    @property
    def url_charset(self):
        return self.charset

    @classmethod
    def from_values(cls, *args, **kwargs):
        from werkzeug.test import EnvironBuilder
        charset = kwargs.pop('charset', cls.charset)
        builder = EnvironBuilder(*args, **kwargs)
        try:
            return builder.get_request(cls)
        finally:
            builder.close()

    @classmethod
    def application(cls, f):
        return _patch_wrapper(f, lambda *a: f(*(a[:-2] + (cls(a[-2]),)))(*a[-2:]))

    def _get_file_stream(self, total_content_length, content_type, filename = None, content_length = None):
        return default_stream_factory(total_content_length, content_type, filename, content_length)

    def _load_form_data(self):
        if 'stream' in self.__dict__:
            return
        if self.shallow:
            raise RuntimeError('A shallow request tried to consume form data.  If you really want to do that, set `shallow` to False.')
        data = None
        stream = _empty_stream
        if self.environ['REQUEST_METHOD'] in ('POST', 'PUT'):
            try:
                data = parse_form_data(self.environ, self._get_file_stream, self.charset, self.encoding_errors, self.max_form_memory_size, self.max_content_length, cls=self.parameter_storage_class, silent=False)
            except ValueError as e:
                self._form_parsing_failed(e)

        else:
            content_length = self.headers.get('content-length', type=int)
            if content_length is not None:
                stream = LimitedStream(self.environ['wsgi.input'], content_length)
        if data is None:
            data = (stream, self.parameter_storage_class(), self.parameter_storage_class())
        d = self.__dict__
        d['stream'], d['form'], d['files'] = data

    def _form_parsing_failed(self, error):
        pass

    @cached_property
    def stream(self):
        self._load_form_data()
        return self.stream

    input_stream = environ_property('wsgi.input', "The WSGI input stream.\nIn general it's a bad idea to use this one because you can easily read past the boundary.  Use the :attr:`stream` instead.")

    @cached_property
    def args(self):
        return url_decode(self.environ.get('QUERY_STRING', ''), self.url_charset, errors=self.encoding_errors, cls=self.parameter_storage_class)

    @cached_property
    def data(self):
        return self.stream.read()

    @cached_property
    def form(self):
        self._load_form_data()
        return self.form

    @cached_property
    def values(self):
        args = []
        for d in (self.args, self.form):
            if not isinstance(d, MultiDict):
                d = MultiDict(d)
            args.append(d)

        return CombinedMultiDict(args)

    @cached_property
    def files(self):
        self._load_form_data()
        return self.files

    @cached_property
    def cookies(self):
        return parse_cookie(self.environ, self.charset, cls=self.dict_storage_class)

    @cached_property
    def headers(self):
        return EnvironHeaders(self.environ)

    @cached_property
    def path(self):
        path = '/' + (self.environ.get('PATH_INFO') or '').lstrip('/')
        return _decode_unicode(path, self.url_charset, self.encoding_errors)

    @cached_property
    def script_root(self):
        path = (self.environ.get('SCRIPT_NAME') or '').rstrip('/')
        return _decode_unicode(path, self.url_charset, self.encoding_errors)

    @cached_property
    def url(self):
        return get_current_url(self.environ)

    @cached_property
    def base_url(self):
        return get_current_url(self.environ, strip_querystring=True)

    @cached_property
    def url_root(self):
        return get_current_url(self.environ, True)

    @cached_property
    def host_url(self):
        return get_current_url(self.environ, host_only=True)

    @cached_property
    def host(self):
        return get_host(self.environ)

    query_string = environ_property('QUERY_STRING', '', read_only=True, doc='The URL parameters as raw bytestring.')
    method = environ_property('REQUEST_METHOD', 'GET', read_only=True, doc="The transmission method. (For example ``'GET'`` or ``'POST'``).")

    @cached_property
    def access_route(self):
        if 'HTTP_X_FORWARDED_FOR' in self.environ:
            addr = self.environ['HTTP_X_FORWARDED_FOR'].split(',')
            return self.list_storage_class([ x.strip() for x in addr ])
        if 'REMOTE_ADDR' in self.environ:
            return self.list_storage_class([self.environ['REMOTE_ADDR']])
        return self.list_storage_class()

    @property
    def remote_addr(self):
        if self.is_behind_proxy and self.access_route:
            return self.access_route[0]
        return self.environ.get('REMOTE_ADDR')

    remote_user = environ_property('REMOTE_USER', doc='\n        If the server supports user authentication, and the script is\n        protected, this attribute contains the username the user has\n        authenticated as.')
    is_xhr = property(lambda x: x.environ.get('HTTP_X_REQUESTED_WITH', '').lower() == 'xmlhttprequest', doc='\n        True if the request was triggered via a JavaScript XMLHttpRequest.\n        This only works with libraries that support the `X-Requested-With`\n        header and set it to "XMLHttpRequest".  Libraries that do that are\n        prototype, jQuery and Mochikit and probably some more.')
    is_secure = property(lambda x: x.environ['wsgi.url_scheme'] == 'https', doc='`True` if the request is secure.')
    is_multithread = environ_property('wsgi.multithread', doc='\n        boolean that is `True` if the application is served by\n        a multithreaded WSGI server.')
    is_multiprocess = environ_property('wsgi.multiprocess', doc='\n        boolean that is `True` if the application is served by\n        a WSGI server that spawns multiple processes.')
    is_run_once = environ_property('wsgi.run_once', doc="\n        boolean that is `True` if the application will be executed only\n        once in a process lifetime.  This is the case for CGI for example,\n        but it's not guaranteed that the exeuction only happens one time.")


class BaseResponse(object):
    charset = 'utf-8'
    default_status = 200
    default_mimetype = 'text/plain'
    implicit_sequence_conversion = True

    def __init__(self, response = None, status = None, headers = None, mimetype = None, content_type = None, direct_passthrough = False):
        if isinstance(headers, Headers):
            self.headers = headers
        elif not headers:
            self.headers = Headers()
        else:
            self.headers = Headers(headers)
        if content_type is None:
            if mimetype is None and 'content-type' not in self.headers:
                mimetype = self.default_mimetype
            if mimetype is not None:
                mimetype = get_content_type(mimetype, self.charset)
            content_type = mimetype
        if content_type is not None:
            self.headers['Content-Type'] = content_type
        if status is None:
            status = self.default_status
        if isinstance(status, (int, long)):
            self.status_code = status
        else:
            self.status = status
        self.direct_passthrough = direct_passthrough
        self._on_close = []
        if response is None:
            self.response = []
        elif isinstance(response, basestring):
            self.data = response
        else:
            self.response = response

    def call_on_close(self, func):
        self._on_close.append(func)

    def __repr__(self):
        if self.is_sequence:
            body_info = '%d bytes' % sum(map(len, self.iter_encoded()))
        else:
            body_info = self.is_streamed and 'streamed' or 'likely-streamed'
        return '<%s %s [%s]>' % (self.__class__.__name__, body_info, self.status)

    @classmethod
    def force_type(cls, response, environ = None):
        if not isinstance(response, BaseResponse):
            if environ is None:
                raise TypeError('cannot convert WSGI application into response objects without an environ')
            response = BaseResponse(*_run_wsgi_app(response, environ))
        response.__class__ = cls
        return response

    @classmethod
    def from_app(cls, app, environ, buffered = False):
        return cls(*_run_wsgi_app(app, environ, buffered))

    def _get_status_code(self):
        try:
            return int(self.status.split(None, 1)[0])
        except ValueError:
            return 0

    def _set_status_code(self, code):
        try:
            self.status = '%d %s' % (code, HTTP_STATUS_CODES[code].upper())
        except KeyError:
            self.status = '%d UNKNOWN' % code

    status_code = property(_get_status_code, _set_status_code, 'The HTTP Status code as number')
    del _get_status_code
    del _set_status_code

    def _get_data(self):
        self._ensure_sequence()
        return ''.join(self.iter_encoded())

    def _set_data(self, value):
        if isinstance(value, unicode):
            value = value.encode(self.charset)
        self.response = [value]

    data = property(_get_data, _set_data, doc=_get_data.__doc__)
    del _get_data
    del _set_data

    def _ensure_sequence(self, mutable = False):
        if self.is_sequence:
            if mutable and not isinstance(self.response, list):
                self.response = list(self.response)
            return
        if not self.implicit_sequence_conversion:
            raise RuntimeError('The response object required the iterable to be a sequence, but the implicit conversion was disabled.  Call make_sequence() yourself.')
        self.make_sequence()

    def make_sequence(self):
        if not self.is_sequence:
            close = getattr(self.response, 'close', None)
            self.response = list(self.iter_encoded())
            if close is not None:
                self.call_on_close(close)

    def iter_encoded(self, charset = None):
        if __debug__ and charset is not None:
            from warnings import warn
            warn(DeprecationWarning('charset was deprecated and is ignored.'), stacklevel=2)
        charset = self.charset
        for item in self.response:
            if isinstance(item, unicode):
                yield item.encode(charset)
            else:
                yield str(item)

    def set_cookie(self, key, value = '', max_age = None, expires = None, path = '/', domain = None, secure = None, httponly = False):
        self.headers.add('Set-Cookie', dump_cookie(key, value, max_age, expires, path, domain, secure, httponly, self.charset))

    def delete_cookie(self, key, path = '/', domain = None):
        self.set_cookie(key, expires=0, max_age=0, path=path, domain=domain)

    @property
    def header_list(self):
        return self.headers.to_list(self.charset)

    @property
    def is_streamed(self):
        try:
            len(self.response)
        except TypeError:
            return True

        return False

    @property
    def is_sequence(self):
        return isinstance(self.response, (tuple, list))

    def close(self):
        if hasattr(self.response, 'close'):
            self.response.close()
        for func in self._on_close:
            func()

    def freeze(self):
        self.response = list(self.iter_encoded())
        self.headers['Content-Length'] = str(sum(map(len, self.response)))

    def fix_headers(self, environ):
        self.headers[:] = self.get_wsgi_headers(environ)

    def get_wsgi_headers(self, environ):
        headers = Headers(self.headers)
        location = headers.get('location')
        if location is not None:
            if isinstance(location, unicode):
                location = iri_to_uri(location)
            headers['Location'] = urlparse.urljoin(get_current_url(environ, root_only=True), location)
        content_location = headers.get('content-location')
        if content_location is not None and isinstance(content_location, unicode):
            headers['Content-Location'] = iri_to_uri(content_location)
        if 100 <= self.status_code < 200 or self.status_code == 204:
            headers['Content-Length'] = '0'
        elif self.status_code == 304:
            remove_entity_headers(headers)
        if self.is_sequence and 'content-length' not in self.headers:
            try:
                content_length = sum((len(str(x)) for x in self.response))
            except UnicodeError:
                pass
            else:
                headers['Content-Length'] = str(content_length)

        return headers

    def get_app_iter(self, environ):
        if environ['REQUEST_METHOD'] == 'HEAD' or 100 <= self.status_code < 200 or self.status_code in (204, 304):
            return ()
        if self.direct_passthrough:
            return self.response
        return ClosingIterator(self.iter_encoded(), self.close)

    def get_wsgi_response(self, environ):
        if self.fix_headers.func_code is not BaseResponse.fix_headers.func_code:
            self.fix_headers(environ)
            headers = self.headers
        else:
            headers = self.get_wsgi_headers(environ)
        app_iter = self.get_app_iter(environ)
        return (app_iter, self.status, headers.to_list(self.charset))

    def __call__(self, environ, start_response):
        app_iter, status, headers = self.get_wsgi_response(environ)
        start_response(status, headers)
        return app_iter


class AcceptMixin(object):

    @cached_property
    def accept_mimetypes(self):
        return parse_accept_header(self.environ.get('HTTP_ACCEPT'), MIMEAccept)

    @cached_property
    def accept_charsets(self):
        return parse_accept_header(self.environ.get('HTTP_ACCEPT_CHARSET'), CharsetAccept)

    @cached_property
    def accept_encodings(self):
        return parse_accept_header(self.environ.get('HTTP_ACCEPT_ENCODING'))

    @cached_property
    def accept_languages(self):
        return parse_accept_header(self.environ.get('HTTP_ACCEPT_LANGUAGE'), LanguageAccept)


class ETagRequestMixin(object):

    @cached_property
    def cache_control(self):
        cache_control = self.environ.get('HTTP_CACHE_CONTROL')
        return parse_cache_control_header(cache_control, None, RequestCacheControl)

    @cached_property
    def if_match(self):
        return parse_etags(self.environ.get('HTTP_IF_MATCH'))

    @cached_property
    def if_none_match(self):
        return parse_etags(self.environ.get('HTTP_IF_NONE_MATCH'))

    @cached_property
    def if_modified_since(self):
        return parse_date(self.environ.get('HTTP_IF_MODIFIED_SINCE'))

    @cached_property
    def if_unmodified_since(self):
        return parse_date(self.environ.get('HTTP_IF_UNMODIFIED_SINCE'))


class UserAgentMixin(object):

    @cached_property
    def user_agent(self):
        from werkzeug.useragents import UserAgent
        return UserAgent(self.environ)


class AuthorizationMixin(object):

    @cached_property
    def authorization(self):
        header = self.environ.get('HTTP_AUTHORIZATION')
        return parse_authorization_header(header)


class ETagResponseMixin(object):

    @property
    def cache_control(self):

        def on_update(cache_control):
            if not cache_control and 'cache-control' in self.headers:
                del self.headers['cache-control']
            elif cache_control:
                self.headers['Cache-Control'] = cache_control.to_header()

        return parse_cache_control_header(self.headers.get('cache-control'), on_update, ResponseCacheControl)

    def make_conditional(self, request_or_environ):
        environ = _get_environ(request_or_environ)
        if environ['REQUEST_METHOD'] in ('GET', 'HEAD'):
            self.headers['Date'] = http_date()
            if 'content-length' in self.headers:
                self.headers['Content-Length'] = len(self.data)
            if not is_resource_modified(environ, self.headers.get('etag'), None, self.headers.get('last-modified')):
                self.status_code = 304
        return self

    def add_etag(self, overwrite = False, weak = False):
        if overwrite or 'etag' not in self.headers:
            self.set_etag(generate_etag(self.data), weak)

    def set_etag(self, etag, weak = False):
        self.headers['ETag'] = quote_etag(etag, weak)

    def get_etag(self):
        return unquote_etag(self.headers.get('ETag'))

    def freeze(self, no_etag = False):
        if not no_etag:
            self.add_etag()
        super(ETagResponseMixin, self).freeze()


class ResponseStream(object):
    mode = 'wb+'

    def __init__(self, response):
        self.response = response
        self.closed = False

    def write(self, value):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        self.response._ensure_sequence(mutable=True)
        self.response.response.append(value)

    def writelines(self, seq):
        for item in seq:
            self.write(item)

    def close(self):
        self.closed = True

    def flush(self):
        if self.closed:
            raise ValueError('I/O operation on closed file')

    def isatty(self):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        return False

    @property
    def encoding(self):
        return self.response.charset


class ResponseStreamMixin(object):

    @cached_property
    def stream(self):
        return ResponseStream(self)


class CommonRequestDescriptorsMixin(object):
    content_type = environ_property('CONTENT_TYPE', doc='\n         The Content-Type entity-header field indicates the media type of\n         the entity-body sent to the recipient or, in the case of the HEAD\n         method, the media type that would have been sent had the request\n         been a GET.')
    content_length = environ_property('CONTENT_LENGTH', None, int, str, doc='\n         The Content-Length entity-header field indicates the size of the\n         entity-body in bytes or, in the case of the HEAD method, the size of\n         the entity-body that would have been sent had the request been a\n         GET.')
    referrer = environ_property('HTTP_REFERER', doc='\n        The Referer[sic] request-header field allows the client to specify,\n        for the server\'s benefit, the address (URI) of the resource from which\n        the Request-URI was obtained (the "referrer", although the header\n        field is misspelled).')
    date = environ_property('HTTP_DATE', None, parse_date, doc='\n        The Date general-header field represents the date and time at which\n        the message was originated, having the same semantics as orig-date\n        in RFC 822.')
    max_forwards = environ_property('HTTP_MAX_FORWARDS', None, int, doc='\n         The Max-Forwards request-header field provides a mechanism with the\n         TRACE and OPTIONS methods to limit the number of proxies or gateways\n         that can forward the request to the next inbound server.')

    def _parse_content_type(self):
        if not hasattr(self, '_parsed_content_type'):
            self._parsed_content_type = parse_options_header(self.environ.get('CONTENT_TYPE', ''))

    @property
    def mimetype(self):
        self._parse_content_type()
        return self._parsed_content_type[0]

    @property
    def mimetype_params(self):
        self._parse_content_type()
        return self._parsed_content_type[1]

    @cached_property
    def pragma(self):
        return parse_set_header(self.environ.get('HTTP_PRAGMA', ''))


class CommonResponseDescriptorsMixin(object):

    def _get_mimetype(self):
        ct = self.headers.get('content-type')
        if ct:
            return ct.split(';')[0].strip()

    def _set_mimetype(self, value):
        self.headers['Content-Type'] = get_content_type(value, self.charset)

    def _get_mimetype_params(self):

        def on_update(d):
            self.headers['Content-Type'] = dump_options_header(self.mimetype, d)

        d = parse_options_header(self.headers.get('content-type', ''))[1]
        return CallbackDict(d, on_update)

    mimetype = property(_get_mimetype, _set_mimetype, doc='\n        The mimetype (content type without charset etc.)')
    mimetype_params = property(_get_mimetype_params, doc="\n        The mimetype parameters as dict.  For example if the content\n        type is ``text/html; charset=utf-8`` the params would be\n        ``{'charset': 'utf-8'}``.\n\n        .. versionadded:: 0.5\n        ")
    location = header_property('Location', doc='\n        The Location response-header field is used to redirect the recipient\n        to a location other than the Request-URI for completion of the request\n        or identification of a new resource.')
    age = header_property('Age', None, parse_date, http_date, doc="\n        The Age response-header field conveys the sender's estimate of the\n        amount of time since the response (or its revalidation) was\n        generated at the origin server.\n\n        Age values are non-negative decimal integers, representing time in\n        seconds.")
    content_type = header_property('Content-Type', doc='\n        The Content-Type entity-header field indicates the media type of the\n        entity-body sent to the recipient or, in the case of the HEAD method,\n        the media type that would have been sent had the request been a GET.\n    ')
    content_length = header_property('Content-Length', None, int, str, doc='\n        The Content-Length entity-header field indicates the size of the\n        entity-body, in decimal number of OCTETs, sent to the recipient or,\n        in the case of the HEAD method, the size of the entity-body that would\n        have been sent had the request been a GET.')
    content_location = header_property('Content-Location', doc="\n        The Content-Location entity-header field MAY be used to supply the\n        resource location for the entity enclosed in the message when that\n        entity is accessible from a location separate from the requested\n        resource's URI.")
    content_encoding = header_property('Content-Encoding', doc='\n        The Content-Encoding entity-header field is used as a modifier to the\n        media-type.  When present, its value indicates what additional content\n        codings have been applied to the entity-body, and thus what decoding\n        mechanisms must be applied in order to obtain the media-type\n        referenced by the Content-Type header field.')
    content_md5 = header_property('Content-MD5', doc='\n         The Content-MD5 entity-header field, as defined in RFC 1864, is an\n         MD5 digest of the entity-body for the purpose of providing an\n         end-to-end message integrity check (MIC) of the entity-body.  (Note:\n         a MIC is good for detecting accidental modification of the\n         entity-body in transit, but is not proof against malicious attacks.)\n        ')
    date = header_property('Date', None, parse_date, http_date, doc='\n        The Date general-header field represents the date and time at which\n        the message was originated, having the same semantics as orig-date\n        in RFC 822.')
    expires = header_property('Expires', None, parse_date, http_date, doc='\n        The Expires entity-header field gives the date/time after which the\n        response is considered stale. A stale cache entry may not normally be\n        returned by a cache.')
    last_modified = header_property('Last-Modified', None, parse_date, http_date, doc='\n        The Last-Modified entity-header field indicates the date and time at\n        which the origin server believes the variant was last modified.')

    def _get_retry_after(self):
        value = self.headers.get('retry-after')
        if value is None:
            return
        if value.isdigit():
            return datetime.utcnow() + timedelta(seconds=int(value))
        return parse_date(value)

    def _set_retry_after(self, value):
        if value is None:
            if 'retry-after' in self.headers:
                del self.headers['retry-after']
            return
        if isinstance(value, datetime):
            value = http_date(value)
        else:
            value = str(value)
        self.headers['Retry-After'] = value

    retry_after = property(_get_retry_after, _set_retry_after, doc='\n        The Retry-After response-header field can be used with a 503 (Service\n        Unavailable) response to indicate how long the service is expected\n        to be unavailable to the requesting client.\n\n        Time in seconds until expiration or date.')

    def _set_property(name, doc = None):

        def fget(self):

            def on_update(header_set):
                if not header_set and name in self.headers:
                    del self.headers[name]
                elif header_set:
                    self.headers[name] = header_set.to_header()

            return parse_set_header(self.headers.get(name), on_update)

        return property(fget, doc=doc)

    vary = _set_property('Vary', doc='\n         The Vary field value indicates the set of request-header fields that\n         fully determines, while the response is fresh, whether a cache is\n         permitted to use the response to reply to a subsequent request\n         without revalidation.')
    content_language = _set_property('Content-Language', doc='\n         The Content-Language entity-header field describes the natural\n         language(s) of the intended audience for the enclosed entity.  Note\n         that this might not be equivalent to all the languages used within\n         the entity-body.')
    allow = _set_property('Allow', doc='\n        The Allow entity-header field lists the set of methods supported\n        by the resource identified by the Request-URI. The purpose of this\n        field is strictly to inform the recipient of valid methods\n        associated with the resource. An Allow header field MUST be\n        present in a 405 (Method Not Allowed) response.')
    del _set_property
    del _get_mimetype
    del _set_mimetype
    del _get_retry_after
    del _set_retry_after


class WWWAuthenticateMixin(object):

    @property
    def www_authenticate(self):

        def on_update(www_auth):
            if not www_auth and 'www-authenticate' in self.headers:
                del self.headers['www-authenticate']
            elif www_auth:
                self.headers['WWW-Authenticate'] = www_auth.to_header()

        header = self.headers.get('www-authenticate')
        return parse_www_authenticate_header(header, on_update)


class Request(BaseRequest, AcceptMixin, ETagRequestMixin, UserAgentMixin, AuthorizationMixin, CommonRequestDescriptorsMixin):
    pass


class Response(BaseResponse, ETagResponseMixin, ResponseStreamMixin, CommonResponseDescriptorsMixin, WWWAuthenticateMixin):
    pass