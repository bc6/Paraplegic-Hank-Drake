#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\http.py
import re
import inspect
try:
    from email.utils import parsedate_tz
except ImportError:
    from email.Utils import parsedate_tz

from urllib2 import parse_http_list as _parse_list_header
from datetime import datetime, timedelta
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

from werkzeug._internal import HTTP_STATUS_CODES
_accept_re = re.compile('([^\\s;,]+)(?:[^,]*?;\\s*q=(\\d*(?:\\.\\d+)?))?')
_token_chars = frozenset("!#$%&'*+-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ^_`abcdefghijklmnopqrstuvwxyz|~")
_etag_re = re.compile('([Ww]/)?(?:"(.*?)"|(.*?))(?:\\s*,\\s*|$)')
_unsafe_header_chars = set('()<>@,;:"/[]?={} \t')
_quoted_string_re = '"[^"\\\\]*(?:\\\\.[^"\\\\]*)*"'
_option_header_piece_re = re.compile(';\\s*([^\\s;=]+|%s)\\s*(?:=\\s*([^;]+|%s))?\\s*' % (_quoted_string_re, _quoted_string_re))
_entity_headers = frozenset(['allow',
 'content-encoding',
 'content-language',
 'content-length',
 'content-location',
 'content-md5',
 'content-range',
 'content-type',
 'expires',
 'last-modified'])
_hop_by_pop_headers = frozenset(['connection',
 'keep-alive',
 'proxy-authenticate',
 'proxy-authorization',
 'te',
 'trailers',
 'transfer-encoding',
 'upgrade'])

def quote_header_value(value, extra_chars = '', allow_token = True):
    value = str(value)
    if allow_token:
        token_chars = _token_chars | set(extra_chars)
        if set(value).issubset(token_chars):
            return value
    return '"%s"' % value.replace('\\', '\\\\').replace('"', '\\"')


def unquote_header_value(value, is_filename = False):
    if value and value[0] == value[-1] == '"':
        value = value[1:-1]
        if not is_filename or value[:2] != '\\\\':
            return value.replace('\\\\', '\\').replace('\\"', '"')
    return value


def dump_options_header(header, options):
    segments = []
    if header is not None:
        segments.append(header)
    for key, value in options.iteritems():
        if value is None:
            segments.append(key)
        else:
            segments.append('%s=%s' % (key, quote_header_value(value)))

    return '; '.join(segments)


def dump_header(iterable, allow_token = True):
    if isinstance(iterable, dict):
        items = []
        for key, value in iterable.iteritems():
            if value is None:
                items.append(key)
            else:
                items.append('%s=%s' % (key, quote_header_value(value, allow_token=allow_token)))

    else:
        items = [ quote_header_value(x, allow_token=allow_token) for x in iterable ]
    return ', '.join(items)


def parse_list_header(value):
    result = []
    for item in _parse_list_header(value):
        if item[:1] == item[-1:] == '"':
            item = unquote_header_value(item[1:-1])
        result.append(item)

    return result


def parse_dict_header(value):
    result = {}
    for item in _parse_list_header(value):
        if '=' not in item:
            result[item] = None
            continue
        name, value = item.split('=', 1)
        if value[:1] == value[-1:] == '"':
            value = unquote_header_value(value[1:-1])
        result[name] = value

    return result


def parse_options_header(value):

    def _tokenize(string):
        for match in _option_header_piece_re.finditer(string):
            key, value = match.groups()
            key = unquote_header_value(key)
            if value is not None:
                value = unquote_header_value(value, key == 'filename')
            yield (key, value)

    if not value:
        return ('', {})
    parts = _tokenize(';' + value)
    name = parts.next()[0]
    extra = dict(parts)
    return (name, extra)


def parse_accept_header(value, cls = None):
    if cls is None:
        cls = Accept
    if not value:
        return cls(None)
    result = []
    for match in _accept_re.finditer(value):
        quality = match.group(2)
        if not quality:
            quality = 1
        else:
            quality = max(min(float(quality), 1), 0)
        result.append((match.group(1), quality))

    return cls(result)


def parse_cache_control_header(value, on_update = None, cls = None):
    if cls is None:
        cls = RequestCacheControl
    if not value:
        return cls(None, on_update)
    return cls(parse_dict_header(value), on_update)


def parse_set_header(value, on_update = None):
    if not value:
        return HeaderSet(None, on_update)
    return HeaderSet(parse_list_header(value), on_update)


def parse_authorization_header(value):
    if not value:
        return
    try:
        auth_type, auth_info = value.split(None, 1)
        auth_type = auth_type.lower()
    except ValueError:
        return

    if auth_type == 'basic':
        try:
            username, password = auth_info.decode('base64').split(':', 1)
        except Exception as e:
            return

        return Authorization('basic', {'username': username,
         'password': password})
    if auth_type == 'digest':
        auth_map = parse_dict_header(auth_info)
        for key in ('username', 'realm', 'nonce', 'uri', 'nc', 'cnonce', 'response'):
            if key not in auth_map:
                return

        return Authorization('digest', auth_map)


def parse_www_authenticate_header(value, on_update = None):
    if not value:
        return WWWAuthenticate(on_update=on_update)
    try:
        auth_type, auth_info = value.split(None, 1)
        auth_type = auth_type.lower()
    except (ValueError, AttributeError):
        return WWWAuthenticate(value.strip().lower(), on_update=on_update)

    return WWWAuthenticate(auth_type, parse_dict_header(auth_info), on_update)


def quote_etag(etag, weak = False):
    if '"' in etag:
        raise ValueError('invalid etag')
    etag = '"%s"' % etag
    if weak:
        etag = 'w/' + etag
    return etag


def unquote_etag(etag):
    if not etag:
        return (None, None)
    etag = etag.strip()
    weak = False
    if etag[:2] in ('w/', 'W/'):
        weak = True
        etag = etag[2:]
    if etag[:1] == etag[-1:] == '"':
        etag = etag[1:-1]
    return (etag, weak)


def parse_etags(value):
    if not value:
        return ETags()
    strong = []
    weak = []
    end = len(value)
    pos = 0
    while pos < end:
        match = _etag_re.match(value, pos)
        if match is None:
            break
        is_weak, quoted, raw = match.groups()
        if raw == '*':
            return ETags(star_tag=True)
        if quoted:
            raw = quoted
        if is_weak:
            weak.append(raw)
        else:
            strong.append(raw)
        pos = match.end()

    return ETags(strong, weak)


def generate_etag(data):
    return md5(data).hexdigest()


def parse_date(value):
    if value:
        t = parsedate_tz(value.strip())
        if t is not None:
            try:
                year = t[0]
                if year >= 0 and year <= 68:
                    year += 2000
                elif year >= 69 and year <= 99:
                    year += 1900
                return datetime(*((year,) + t[1:7])) - timedelta(seconds=t[-1] or 0)
            except (ValueError, OverflowError):
                return


def is_resource_modified(environ, etag = None, data = None, last_modified = None):
    if etag is None and data is not None:
        etag = generate_etag(data)
    elif data is not None:
        raise TypeError('both data and etag given')
    if environ['REQUEST_METHOD'] not in ('GET', 'HEAD'):
        return False
    unmodified = False
    if isinstance(last_modified, basestring):
        last_modified = parse_date(last_modified)
    modified_since = parse_date(environ.get('HTTP_IF_MODIFIED_SINCE'))
    if modified_since and last_modified and last_modified <= modified_since:
        unmodified = True
    if etag:
        if_none_match = parse_etags(environ.get('HTTP_IF_NONE_MATCH'))
        if if_none_match:
            unmodified = if_none_match.contains_raw(etag)
    return not unmodified


def remove_entity_headers(headers, allowed = ('expires', 'content-location')):
    allowed = set((x.lower() for x in allowed))
    headers[:] = [ (key, value) for key, value in headers if not is_entity_header(key) or key.lower() in allowed ]


def remove_hop_by_hop_headers(headers):
    headers[:] = [ (key, value) for key, value in headers if not is_hop_by_hop_header(key) ]


def is_entity_header(header):
    return header.lower() in _entity_headers


def is_hop_by_hop_header(header):
    return header.lower() in _hop_by_pop_headers


from werkzeug.datastructures import Headers, Accept, RequestCacheControl, ResponseCacheControl, HeaderSet, ETags, Authorization, WWWAuthenticate
from werkzeug.datastructures import MIMEAccept, CharsetAccept, LanguageAccept