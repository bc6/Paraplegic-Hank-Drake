#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\urls.py
import urlparse
from werkzeug._internal import _decode_unicode
_always_safe = frozenset('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-')
_hextochr = dict((('%02x' % i, chr(i)) for i in xrange(256)))
_hextochr.update((('%02X' % i, chr(i)) for i in xrange(256)))

def _quote(s, safe = '/', _quotechar = '%%%02X'.__mod__):
    safe = _always_safe | set(safe)
    rv = list(s)
    for idx, char in enumerate(s):
        if char not in safe:
            rv[idx] = _quotechar(ord(char))

    return ''.join(rv)


def _quote_plus(s, safe = ''):
    if ' ' in s:
        return _quote(s, safe + ' ').replace(' ', '+')
    return _quote(s, safe)


def _safe_urlsplit(s):
    rv = urlparse.urlsplit(s)
    if type(rv[1]) is not type(s):
        try:
            return tuple(map(type(s), rv))
        except UnicodeError:
            pass

    return rv


def _unquote(s, unsafe = ''):
    unsafe = set(unsafe)
    rv = s.split('%')
    for i in xrange(1, len(rv)):
        item = rv[i]
        try:
            char = _hextochr[item[:2]]
            if char in unsafe:
                raise KeyError()
            rv[i] = char + item[2:]
        except KeyError:
            rv[i] = '%' + item

    return ''.join(rv)


def _unquote_plus(s):
    return _unquote(s.replace('+', ' '))


def _uri_split(uri):
    scheme, netloc, path, query, fragment = _safe_urlsplit(uri)
    port = None
    if '@' in netloc:
        auth, hostname = netloc.split('@', 1)
    else:
        auth = None
        hostname = netloc
    if hostname:
        if ':' in hostname:
            hostname, port = hostname.split(':', 1)
    return (scheme,
     auth,
     hostname,
     port,
     path,
     query,
     fragment)


def iri_to_uri(iri, charset = 'utf-8'):
    iri = unicode(iri)
    scheme, auth, hostname, port, path, query, fragment = _uri_split(iri)
    scheme = scheme.encode('ascii')
    hostname = hostname.encode('idna')
    if auth:
        if ':' in auth:
            auth, password = auth.split(':', 1)
        else:
            password = None
        auth = _quote(auth.encode(charset))
        if password:
            auth += ':' + _quote(password.encode(charset))
        hostname = auth + '@' + hostname
    if port:
        hostname += ':' + port
    path = _quote(path.encode(charset), safe='/:~+')
    query = _quote(query.encode(charset), safe='=%&[]:;$()+,!?*/')
    return urlparse.urlunsplit([scheme,
     hostname,
     path,
     query,
     fragment])


def uri_to_iri(uri, charset = 'utf-8', errors = 'ignore'):
    uri = url_fix(str(uri), charset)
    scheme, auth, hostname, port, path, query, fragment = _uri_split(uri)
    scheme = _decode_unicode(scheme, 'ascii', errors)
    try:
        hostname = hostname.decode('idna')
    except UnicodeError:
        if errors not in ('ignore', 'replace'):
            raise 
        hostname = hostname.decode('ascii', errors)

    if auth:
        if ':' in auth:
            auth, password = auth.split(':', 1)
        else:
            password = None
        auth = _decode_unicode(_unquote(auth), charset, errors)
        if password:
            auth += u':' + _decode_unicode(_unquote(password), charset, errors)
        hostname = auth + u'@' + hostname
    if port:
        hostname += u':' + port.decode(charset, errors)
    path = _decode_unicode(_unquote(path, '/;?'), charset, errors)
    query = _decode_unicode(_unquote(query, ';/?:@&=+,$'), charset, errors)
    return urlparse.urlunsplit([scheme,
     hostname,
     path,
     query,
     fragment])


def url_decode(s, charset = 'utf-8', decode_keys = False, include_empty = True, errors = 'ignore', separator = '&', cls = None):
    if cls is None:
        cls = MultiDict
    result = []
    for pair in str(s).split(separator):
        if not pair:
            continue
        if '=' in pair:
            key, value = pair.split('=', 1)
        else:
            key = pair
            value = ''
        key = _unquote_plus(key)
        if decode_keys:
            key = _decode_unicode(key, charset, errors)
        result.append((key, url_unquote_plus(value, charset, errors)))

    return cls(result)


def url_encode(obj, charset = 'utf-8', encode_keys = False, sort = False, key = None, separator = '&'):
    iterable = iter_multi_items(obj)
    if sort:
        iterable = list(iterable)
        iterable.sort(key=key)
    tmp = []
    for key, value in iterable:
        if encode_keys and isinstance(key, unicode):
            key = key.encode(charset)
        else:
            key = str(key)
        if value is None:
            continue
        elif isinstance(value, unicode):
            value = value.encode(charset)
        else:
            value = str(value)
        tmp.append('%s=%s' % (_quote(key), _quote_plus(value)))

    return separator.join(tmp)


def url_quote(s, charset = 'utf-8', safe = '/:'):
    if isinstance(s, unicode):
        s = s.encode(charset)
    elif not isinstance(s, str):
        s = str(s)
    return _quote(s, safe=safe)


def url_quote_plus(s, charset = 'utf-8', safe = ''):
    if isinstance(s, unicode):
        s = s.encode(charset)
    elif not isinstance(s, str):
        s = str(s)
    return _quote_plus(s, safe=safe)


def url_unquote(s, charset = 'utf-8', errors = 'ignore'):
    if isinstance(s, unicode):
        s = s.encode(charset)
    return _decode_unicode(_unquote(s), charset, errors)


def url_unquote_plus(s, charset = 'utf-8', errors = 'ignore'):
    return _decode_unicode(_unquote_plus(s), charset, errors)


def url_fix(s, charset = 'utf-8'):
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = _safe_urlsplit(s)
    path = _quote(path, '/%')
    qs = _quote_plus(qs, ':&%=')
    return urlparse.urlunsplit((scheme,
     netloc,
     path,
     qs,
     anchor))


class Href(object):

    def __init__(self, base = './', charset = 'utf-8', sort = False, key = None):
        if not base:
            base = './'
        self.base = base
        self.charset = charset
        self.sort = sort
        self.key = key

    def __getattr__(self, name):
        if name[:2] == '__':
            raise AttributeError(name)
        base = self.base
        if base[-1:] != '/':
            base += '/'
        return Href(urlparse.urljoin(base, name), self.charset, self.sort, self.key)

    def __call__(self, *path, **query):
        if path and isinstance(path[-1], dict):
            if query:
                raise TypeError("keyword arguments and query-dicts can't be combined")
            query, path = path[-1], path[:-1]
        elif query:
            query = dict([ (k.endswith('_') and k[:-1] or k, v) for k, v in query.items() ])
        path = '/'.join([ url_quote(x, self.charset) for x in path if x is not None ]).lstrip('/')
        rv = self.base
        if path:
            if not rv.endswith('/'):
                rv += '/'
            rv = urlparse.urljoin(rv, path)
        if query:
            rv += '?' + url_encode(query, self.charset, sort=self.sort, key=self.key)
        return str(rv)


from werkzeug.datastructures import MultiDict, iter_multi_items