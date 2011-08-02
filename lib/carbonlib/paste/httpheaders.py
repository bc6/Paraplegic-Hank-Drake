import mimetypes
import urllib2
import re
from rfc822 import formatdate, parsedate_tz, mktime_tz
from time import time as now
from httpexceptions import HTTPBadRequest
__all__ = ['get_header',
 'list_headers',
 'normalize_headers',
 'HTTPHeader',
 'EnvironVariable']

class EnvironVariable(str):

    def __call__(self, environ):
        return environ.get(self, '')



    def __repr__(self):
        return '<EnvironVariable %s>' % self



    def update(self, environ, value):
        environ[self] = value



REMOTE_USER = EnvironVariable('REMOTE_USER')
REMOTE_SESSION = EnvironVariable('REMOTE_SESSION')
AUTH_TYPE = EnvironVariable('AUTH_TYPE')
REQUEST_METHOD = EnvironVariable('REQUEST_METHOD')
SCRIPT_NAME = EnvironVariable('SCRIPT_NAME')
PATH_INFO = EnvironVariable('PATH_INFO')
for (_name, _obj,) in globals().items():
    if isinstance(_obj, EnvironVariable):
        __all__.append(_name)

_headers = {}

class HTTPHeader(object):
    version = '1.1'
    category = 'general'
    reference = ''
    extensions = {}

    def compose(self, **kwargs):
        raise NotImplementedError()



    def parse(self, *args, **kwargs):
        raise NotImplementedError()



    def apply(self, collection, **kwargs):
        self.update(collection, **kwargs)



    def __new__(cls, name, category = None, reference = None, version = None):
        self = get_header(name, raiseError=False)
        if self:
            return self
        self = object.__new__(cls)
        self.name = name
        self.category = category or self.category
        self.version = version or self.version
        self.reference = reference or self.reference
        _headers[self.name.lower()] = self
        self.sort_order = {'general': 1,
         'request': 2,
         'response': 3,
         'entity': 4}[self.category]
        self._environ_name = getattr(self, '_environ_name', 'HTTP_' + self.name.upper().replace('-', '_'))
        self._headers_name = getattr(self, '_headers_name', self.name.lower())
        return self



    def __str__(self):
        return self.name



    def __lt__(self, other):
        if isinstance(other, HTTPHeader):
            if self.sort_order != other.sort_order:
                return self.sort_order < other.sort_order
            return self.name < other.name
        return False



    def __repr__(self):
        ref = self.reference and ' (%s)' % self.reference or ''
        return '<%s %s%s>' % (self.__class__.__name__, self.name, ref)



    def values(self, *args, **kwargs):
        if not args:
            return self.compose(**kwargs)
        if list == type(args[0]):
            result = []
            name = self.name.lower()
            for value in [ value for (header, value,) in args[0] if header.lower() == name ]:
                result.append(value)

            return result
        if dict == type(args[0]):
            value = args[0].get(self._environ_name)
            if not value:
                return ()
            return (value,)
        for item in args:
            pass

        return args



    def __call__(self, *args, **kwargs):
        values = self.values(*args, **kwargs)
        if not values:
            return ''
        return str(values[0]).strip()



    def delete(self, collection):
        if type(collection) == dict:
            if self._environ_name in collection:
                del collection[self._environ_name]
            return self
        i = 0
        while i < len(collection):
            if collection[i][0].lower() == self._headers_name:
                del collection[i]
                continue
            i += 1




    def update(self, collection, *args, **kwargs):
        value = self.__call__(*args, **kwargs)
        if not value:
            self.delete(collection)
            return 
        if type(collection) == dict:
            collection[self._environ_name] = value
            return 
        i = 0
        found = False
        while i < len(collection):
            if collection[i][0].lower() == self._headers_name:
                if found:
                    del collection[i]
                    continue
                collection[i] = (self.name, value)
                found = True
            i += 1

        if not found:
            collection.append((self.name, value))



    def tuples(self, *args, **kwargs):
        value = self.__call__(*args, **kwargs)
        if not value:
            return ()
        return [(self.name, value)]




class _SingleValueHeader(HTTPHeader):
    pass

class _MultiValueHeader(HTTPHeader):

    def __call__(self, *args, **kwargs):
        results = self.values(*args, **kwargs)
        if not results:
            return ''
        return ', '.join([ str(v).strip() for v in results ])



    def parse(self, *args, **kwargs):
        value = self.__call__(*args, **kwargs)
        values = value.split(',')
        return [ v.strip() for v in values if v.strip() ]




class _MultiEntryHeader(HTTPHeader):

    def update(self, collection, *args, **kwargs):
        self.delete(collection)
        collection.extend(self.tuples(*args, **kwargs))



    def tuples(self, *args, **kwargs):
        values = self.values(*args, **kwargs)
        if not values:
            return ()
        return [ (self.name, value.strip()) for value in values ]




def get_header(name, raiseError = True):
    retval = _headers.get(str(name).strip().lower().replace('_', '-'))
    if not retval and raiseError:
        raise AssertionError("'%s' is an unknown header" % name)
    return retval



def list_headers(general = None, request = None, response = None, entity = None):
    if not (general or request or response or entity):
        general = request = response = entity = True
    search = []
    for (bool, strval,) in ((general, 'general'),
     (request, 'request'),
     (response, 'response'),
     (entity, 'entity')):
        if bool:
            search.append(strval)

    return [ head for head in _headers.values() if head.category in search ]



def normalize_headers(response_headers, strict = True):
    category = {}
    for idx in range(len(response_headers)):
        (key, val,) = response_headers[idx]
        head = get_header(key, strict)
        if not head:
            newhead = '-'.join([ x.capitalize() for x in key.replace('_', '-').split('-') ])
            response_headers[idx] = (newhead, val)
            category[newhead] = 4
            continue
        response_headers[idx] = (str(head), val)
        category[str(head)] = head.sort_order


    def compare(a, b):
        ac = category[a[0]]
        bc = category[b[0]]
        if ac == bc:
            return cmp(a[0], b[0])
        return cmp(ac, bc)


    response_headers.sort(compare)



class _DateHeader(_SingleValueHeader):

    def compose(self, time = None, delta = None):
        time = time or now()
        if delta:
            time += delta
        return (formatdate(time),)



    def parse(self, *args, **kwargs):
        value = self.__call__(*args, **kwargs)
        if value:
            try:
                return mktime_tz(parsedate_tz(value))
            except (TypeError, OverflowError):
                raise HTTPBadRequest('Received an ill-formed timestamp for %s: %s\r\n' % (self.name, value))




class _CacheControl(_MultiValueHeader):
    ONE_HOUR = 3600
    ONE_DAY = ONE_HOUR * 24
    ONE_WEEK = ONE_DAY * 7
    ONE_MONTH = ONE_DAY * 30
    ONE_YEAR = ONE_WEEK * 52

    def _compose(self, public = None, private = None, no_cache = None, no_store = False, max_age = None, s_maxage = None, no_transform = False, **extensions):
        expires = 0
        result = []
        if private is True:
            result.append('private')
        elif no_cache is True:
            result.append('no-cache')
        else:
            expires = max_age
            result.append('public')
        if no_store:
            result.append('no-store')
        if no_transform:
            result.append('no-transform')
        if max_age is not None:
            result.append('max-age=%d' % max_age)
        if s_maxage is not None:
            result.append('s-maxage=%d' % s_maxage)
        for (k, v,) in extensions.items():
            if k not in self.extensions:
                raise AssertionError("unexpected extension used: '%s'" % k)
            result.append('%s="%s"' % (k.replace('_', '-'), v))

        return (result, expires)



    def compose(self, **kwargs):
        (result, expires,) = self._compose(**kwargs)
        return result



    def apply(self, collection, **kwargs):
        (result, expires,) = self._compose(**kwargs)
        if expires is not None:
            EXPIRES.update(collection, delta=expires)
        self.update(collection, *result)
        return expires



_CacheControl('Cache-Control', 'general', 'RFC 2616, 14.9')

class _ContentType(_SingleValueHeader):
    version = '1.0'
    _environ_name = 'CONTENT_TYPE'
    UNKNOWN = 'application/octet-stream'
    TEXT_PLAIN = 'text/plain'
    TEXT_HTML = 'text/html'
    TEXT_XML = 'text/xml'

    def compose(self, major = None, minor = None, charset = None):
        if not major:
            if minor in ('plain', 'html', 'xml'):
                major = 'text'
            else:
                return (self.UNKNOWN,)
        if not minor:
            minor = '*'
        result = '%s/%s' % (major, minor)
        if charset:
            result += '; charset=%s' % charset
        return (result,)



_ContentType('Content-Type', 'entity', 'RFC 2616, 14.17')

class _ContentLength(_SingleValueHeader):
    version = '1.0'
    _environ_name = 'CONTENT_LENGTH'

_ContentLength('Content-Length', 'entity', 'RFC 2616, 14.13')

class _ContentDisposition(_SingleValueHeader):

    def _compose(self, attachment = None, inline = None, filename = None):
        result = []
        if inline is True:
            result.append('inline')
        else:
            result.append('attachment')
        if filename:
            filename = filename.split('/')[-1]
            filename = filename.split('\\')[-1]
            result.append('filename="%s"' % filename)
        return (('; '.join(result),), filename)



    def compose(self, **kwargs):
        (result, mimetype,) = self._compose(**kwargs)
        return result



    def apply(self, collection, **kwargs):
        (result, filename,) = self._compose(**kwargs)
        mimetype = CONTENT_TYPE(collection)
        if filename and (not mimetype or CONTENT_TYPE.UNKNOWN == mimetype):
            (mimetype, _,) = mimetypes.guess_type(filename)
            if mimetype and CONTENT_TYPE.UNKNOWN != mimetype:
                CONTENT_TYPE.update(collection, mimetype)
        self.update(collection, *result)
        return mimetype



_ContentDisposition('Content-Disposition', 'entity', 'RFC 2183')

class _IfModifiedSince(_DateHeader):
    version = '1.0'

    def __call__(self, *args, **kwargs):
        return _DateHeader.__call__(self, *args, **kwargs).split(';', 1)[0]



    def parse(self, *args, **kwargs):
        value = _DateHeader.parse(self, *args, **kwargs)
        if value and value > now():
            raise HTTPBadRequest('Please check your system clock.\r\nAccording to this server, the time provided in the\r\n%s header is in the future.\r\n' % self.name)
        return value



_IfModifiedSince('If-Modified-Since', 'request', 'RFC 2616, 14.25')

class _Range(_MultiValueHeader):

    def parse(self, *args, **kwargs):
        value = self.__call__(*args, **kwargs)
        if not value:
            return 
        ranges = []
        last_end = -1
        try:
            (units, range,) = value.split('=', 1)
            units = units.strip().lower()
            for item in range.split(','):
                (begin, end,) = item.split('-')
                if not begin.strip():
                    begin = 0
                else:
                    begin = int(begin)
                if begin <= last_end:
                    raise ValueError()
                if not end.strip():
                    end = None
                else:
                    end = int(end)
                last_end = end
                ranges.append((begin, end))

        except ValueError:
            return 
        return (units, ranges)



_Range('Range', 'request', 'RFC 2616, 14.35')

class _AcceptLanguage(_MultiValueHeader):

    def parse(self, *args, **kwargs):
        header = self.__call__(*args, **kwargs)
        if header is None:
            return []
        langs = [ v for v in header.split(',') if v ]
        qs = []
        for lang in langs:
            pieces = lang.split(';')
            (lang, params,) = (pieces[0].strip().lower(), pieces[1:])
            q = 1
            for param in params:
                if '=' not in param:
                    continue
                (lvalue, rvalue,) = param.split('=')
                lvalue = lvalue.strip().lower()
                rvalue = rvalue.strip()
                if lvalue == 'q':
                    q = float(rvalue)

            qs.append((lang, q))

        qs.sort(lambda a, b: -cmp(a[1], b[1]))
        return [ lang for (lang, q,) in qs ]



_AcceptLanguage('Accept-Language', 'request', 'RFC 2616, 14.4')

class _AcceptRanges(_MultiValueHeader):

    def compose(self, none = None, bytes = None):
        if bytes:
            return ('bytes',)
        return ('none',)



_AcceptRanges('Accept-Ranges', 'response', 'RFC 2616, 14.5')

class _ContentRange(_SingleValueHeader):

    def compose(self, first_byte = None, last_byte = None, total_length = None):
        retval = 'bytes %d-%d/%d' % (first_byte, last_byte, total_length)
        return (retval,)



_ContentRange('Content-Range', 'entity', 'RFC 2616, 14.6')

class _Authorization(_SingleValueHeader):

    def compose(self, digest = None, basic = None, username = None, password = None, challenge = None, path = None, method = None):
        if basic or not challenge:
            userpass = '%s:%s' % (username.strip(), password.strip())
            return 'Basic %s' % userpass.encode('base64').strip()
        path = path or '/'
        (_, realm,) = challenge.split('realm="')
        (realm, _,) = realm.split('"', 1)
        auth = urllib2.AbstractDigestAuthHandler()
        auth.add_password(realm, path, username, password)
        (token, challenge,) = challenge.split(' ', 1)
        chal = urllib2.parse_keqv_list(urllib2.parse_http_list(challenge))

        class FakeRequest(object):

            def get_full_url(self):
                return path



            def has_data(self):
                return False



            def get_method(self):
                return method or 'GET'


            get_selector = get_full_url

        retval = 'Digest %s' % auth.get_authorization(FakeRequest(), chal)
        return (retval,)



_Authorization('Authorization', 'request', 'RFC 2617')
for (name, category, version, style, comment,) in (('Accept',
  'request',
  '1.1',
  'multi-value',
  'RFC 2616, 14.1'),
 ('Accept-Charset',
  'request',
  '1.1',
  'multi-value',
  'RFC 2616, 14.2'),
 ('Accept-Encoding',
  'request',
  '1.1',
  'multi-value',
  'RFC 2616, 14.3'),
 ('Age',
  'response',
  '1.1',
  'singular',
  'RFC 2616, 14.6'),
 ('Allow',
  'entity',
  '1.0',
  'multi-value',
  'RFC 2616, 14.7'),
 ('Cookie',
  'request',
  '1.0',
  'multi-value',
  'RFC 2109/Netscape'),
 ('Connection',
  'general',
  '1.1',
  'multi-value',
  'RFC 2616, 14.10'),
 ('Content-Encoding',
  'entity',
  '1.0',
  'multi-value',
  'RFC 2616, 14.11'),
 ('Content-Language',
  'entity',
  '1.1',
  'multi-value',
  'RFC 2616, 14.12'),
 ('Content-Location',
  'entity',
  '1.1',
  'singular',
  'RFC 2616, 14.14'),
 ('Content-MD5',
  'entity',
  '1.1',
  'singular',
  'RFC 2616, 14.15'),
 ('Date',
  'general',
  '1.0',
  'date-header',
  'RFC 2616, 14.18'),
 ('ETag',
  'response',
  '1.1',
  'singular',
  'RFC 2616, 14.19'),
 ('Expect',
  'request',
  '1.1',
  'multi-value',
  'RFC 2616, 14.20'),
 ('Expires',
  'entity',
  '1.0',
  'date-header',
  'RFC 2616, 14.21'),
 ('From',
  'request',
  '1.0',
  'singular',
  'RFC 2616, 14.22'),
 ('Host',
  'request',
  '1.1',
  'singular',
  'RFC 2616, 14.23'),
 ('If-Match',
  'request',
  '1.1',
  'multi-value',
  'RFC 2616, 14.24'),
 ('If-None-Match',
  'request',
  '1.1',
  'multi-value',
  'RFC 2616, 14.26'),
 ('If-Range',
  'request',
  '1.1',
  'singular',
  'RFC 2616, 14.27'),
 ('If-Unmodified-Since',
  'request',
  '1.1',
  'date-header',
  'RFC 2616, 14.28'),
 ('Last-Modified',
  'entity',
  '1.0',
  'date-header',
  'RFC 2616, 14.29'),
 ('Location',
  'response',
  '1.0',
  'singular',
  'RFC 2616, 14.30'),
 ('Max-Forwards',
  'request',
  '1.1',
  'singular',
  'RFC 2616, 14.31'),
 ('Pragma',
  'general',
  '1.0',
  'multi-value',
  'RFC 2616, 14.32'),
 ('Proxy-Authenticate',
  'response',
  '1.1',
  'multi-value',
  'RFC 2616, 14.33'),
 ('Proxy-Authorization',
  'request',
  '1.1',
  'singular',
  'RFC 2616, 14.34'),
 ('Referer',
  'request',
  '1.0',
  'singular',
  'RFC 2616, 14.36'),
 ('Retry-After',
  'response',
  '1.1',
  'singular',
  'RFC 2616, 14.37'),
 ('Server',
  'response',
  '1.0',
  'singular',
  'RFC 2616, 14.38'),
 ('Set-Cookie',
  'response',
  '1.0',
  'multi-entry',
  'RFC 2109/Netscape'),
 ('TE',
  'request',
  '1.1',
  'multi-value',
  'RFC 2616, 14.39'),
 ('Trailer',
  'general',
  '1.1',
  'multi-value',
  'RFC 2616, 14.40'),
 ('Transfer-Encoding',
  'general',
  '1.1',
  'multi-value',
  'RFC 2616, 14.41'),
 ('Upgrade',
  'general',
  '1.1',
  'multi-value',
  'RFC 2616, 14.42'),
 ('User-Agent',
  'request',
  '1.0',
  'singular',
  'RFC 2616, 14.43'),
 ('Vary',
  'response',
  '1.1',
  'multi-value',
  'RFC 2616, 14.44'),
 ('Via',
  'general',
  '1.1',
  'multi-value',
  'RFC 2616, 14.45'),
 ('Warning',
  'general',
  '1.1',
  'multi-entry',
  'RFC 2616, 14.46'),
 ('WWW-Authenticate',
  'response',
  '1.0',
  'multi-entry',
  'RFC 2616, 14.47')):
    klass = {'multi-value': _MultiValueHeader,
     'multi-entry': _MultiEntryHeader,
     'date-header': _DateHeader,
     'singular': _SingleValueHeader}[style]
    klass(name, category, comment, version).__doc__ = comment
    del klass

for head in _headers.values():
    headname = head.name.replace('-', '_').upper()
    locals()[headname] = head
    __all__.append(headname)

__pudge_all__ = __all__[:]
for (_name, _obj,) in globals().items():
    if isinstance(_obj, type) and issubclass(_obj, HTTPHeader):
        __pudge_all__.append(_name)


