#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\utils.py
import re
import os
from time import time
from datetime import datetime, timedelta
from werkzeug._internal import _decode_unicode, _iter_modules, _ExtendedCookie, _ExtendedMorsel, _DictAccessorProperty, _dump_date, _parse_signature, _missing
_format_re = re.compile('\\$(?:(%s)|\\{(%s)\\})' % ('[a-zA-Z_][a-zA-Z0-9_]*', '[a-zA-Z_][a-zA-Z0-9_]*'))
_entity_re = re.compile('&([^;]+);')
_filename_ascii_strip_re = re.compile('[^A-Za-z0-9_.-]')
_windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1', 'LPT2', 'LPT3', 'PRN', 'NUL')

class cached_property(object):

    def __init__(self, func, name = None, doc = None, writeable = False):
        if writeable:
            from warnings import warn
            warn(DeprecationWarning('the writeable argument to the cached property is a noop since 0.6 because the property is writeable by default for performance reasons'))
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type = None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value


class environ_property(_DictAccessorProperty):
    read_only = True

    def lookup(self, obj):
        return obj.environ


class header_property(_DictAccessorProperty):

    def lookup(self, obj):
        return obj.headers


class HTMLBuilder(object):
    from htmlentitydefs import name2codepoint
    _entity_re = re.compile('&([^;]+);')
    _entities = name2codepoint.copy()
    _entities['apos'] = 39
    _empty_elements = set(['area',
     'base',
     'basefont',
     'br',
     'col',
     'frame',
     'hr',
     'img',
     'input',
     'isindex',
     'link',
     'meta',
     'param'])
    _boolean_attributes = set(['selected',
     'checked',
     'compact',
     'declare',
     'defer',
     'disabled',
     'ismap',
     'multiple',
     'nohref',
     'noresize',
     'noshade',
     'nowrap'])
    _plaintext_elements = set(['textarea'])
    _c_like_cdata = set(['script', 'style'])
    del name2codepoint

    def __init__(self, dialect):
        self._dialect = dialect

    def __call__(self, s):
        return escape(s)

    def __getattr__(self, tag):
        if tag[:2] == '__':
            raise AttributeError(tag)

        def proxy(*children, **arguments):
            buffer = ['<' + tag]
            write = buffer.append
            for key, value in arguments.iteritems():
                if value is None:
                    continue
                if key.endswith('_'):
                    key = key[:-1]
                if key in self._boolean_attributes:
                    if not value:
                        continue
                    value = self._dialect == 'xhtml' and '="%s"' % key or ''
                else:
                    value = '="%s"' % escape(value, True)
                write(' ' + key + value)

            if not children and tag in self._empty_elements:
                write(self._dialect == 'xhtml' and ' />' or '>')
                return ''.join(buffer)
            write('>')
            children_as_string = ''.join((unicode(x) for x in children if x is not None))
            if children_as_string:
                if tag in self._plaintext_elements:
                    children_as_string = escape(children_as_string)
                elif tag in self._c_like_cdata and self._dialect == 'xhtml':
                    children_as_string = '/*<![CDATA[*/%s/*]]>*/' % children_as_string
            buffer.extend((children_as_string, '</%s>' % tag))
            return ''.join(buffer)

        return proxy

    def __repr__(self):
        return '<%s for %r>' % (self.__class__.__name__, self._dialect)


html = HTMLBuilder('html')
xhtml = HTMLBuilder('xhtml')

def get_content_type(mimetype, charset):
    if mimetype.startswith('text/') or mimetype == 'application/xml' or mimetype.startswith('application/') and mimetype.endswith('+xml'):
        mimetype += '; charset=' + charset
    return mimetype


def format_string(string, context):

    def lookup_arg(match):
        x = context[match.group(1) or match.group(2)]
        if not isinstance(x, basestring):
            x = type(string)(x)
        return x

    return _format_re.sub(lookup_arg, string)


def secure_filename(filename):
    if isinstance(filename, unicode):
        from unicodedata import normalize
        filename = normalize('NFKD', filename).encode('ascii', 'ignore')
    for sep in (os.path.sep, os.path.altsep):
        if sep:
            filename = filename.replace(sep, ' ')

    filename = str(_filename_ascii_strip_re.sub('', '_'.join(filename.split()))).strip('._')
    if os.name == 'nt' and filename and filename.split('.')[0].upper() in _windows_device_files:
        filename = '_' + filename
    return filename


def escape(s, quote = False):
    if s is None:
        return ''
    if hasattr(s, '__html__'):
        return s.__html__()
    if not isinstance(s, basestring):
        s = unicode(s)
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    if quote:
        s = s.replace('"', '&quot;')
    return s


def unescape(s):

    def handle_match(m):
        name = m.group(1)
        if name in HTMLBuilder._entities:
            return unichr(HTMLBuilder._entities[name])
        try:
            if name[:2] in ('#x', '#X'):
                return unichr(int(name[2:], 16))
            if name.startswith('#'):
                return unichr(int(name[1:]))
        except ValueError:
            pass

        return u''

    return _entity_re.sub(handle_match, s)


def cookie_date(expires = None):
    return _dump_date(expires, '-')


def parse_cookie(header, charset = 'utf-8', errors = 'ignore', cls = None):
    if isinstance(header, dict):
        header = header.get('HTTP_COOKIE', '')
    if cls is None:
        cls = TypeConversionDict
    cookie = _ExtendedCookie()
    cookie.load(header)
    result = {}
    for key, value in cookie.iteritems():
        if value.value is not None:
            result[key] = _decode_unicode(unquote_header_value(value.value), charset, errors)

    return cls(result)


def dump_cookie(key, value = '', max_age = None, expires = None, path = '/', domain = None, secure = None, httponly = False, charset = 'utf-8', sync_expires = True):
    try:
        key = str(key)
    except UnicodeError:
        raise TypeError('invalid key %r' % key)

    if isinstance(value, unicode):
        value = value.encode(charset)
    value = quote_header_value(value)
    morsel = _ExtendedMorsel(key, value)
    if isinstance(max_age, timedelta):
        max_age = max_age.days * 60 * 60 * 24 + max_age.seconds
    if expires is not None:
        if not isinstance(expires, basestring):
            expires = cookie_date(expires)
        morsel['expires'] = expires
    elif max_age is not None and sync_expires:
        morsel['expires'] = cookie_date(time() + max_age)
    for k, v in (('path', path),
     ('domain', domain),
     ('secure', secure),
     ('max-age', max_age),
     ('httponly', httponly)):
        if v is not None and v is not False:
            morsel[k] = str(v)

    return morsel.output(header='').lstrip()


def http_date(timestamp = None):
    return _dump_date(timestamp, ' ')


def redirect(location, code = 302):
    from werkzeug.wrappers import BaseResponse
    display_location = location
    if isinstance(location, unicode):
        from werkzeug.urls import iri_to_uri
        location = iri_to_uri(location)
    response = BaseResponse('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>Redirecting...</title>\n<h1>Redirecting...</h1>\n<p>You should be redirected automatically to target URL: <a href="%s">%s</a>.  If not click the link.' % (location, display_location), code, mimetype='text/html')
    response.headers['Location'] = location
    return response


def append_slash_redirect(environ, code = 301):
    new_path = environ['PATH_INFO'].strip('/') + '/'
    query_string = environ.get('QUERY_STRING')
    if query_string:
        new_path += '?' + query_string
    return redirect(new_path, code)


def import_string(import_name, silent = False):
    if isinstance(import_name, unicode):
        import_name = str(import_name)
    try:
        if ':' in import_name:
            module, obj = import_name.split(':', 1)
        elif '.' in import_name:
            module, obj = import_name.rsplit('.', 1)
        else:
            return __import__(import_name)
        if isinstance(obj, unicode):
            obj = obj.encode('utf-8')
        return getattr(__import__(module, None, None, [obj]), obj)
    except (ImportError, AttributeError):
        if not silent:
            raise 


def find_modules(import_path, include_packages = False, recursive = False):
    module = import_string(import_path)
    path = getattr(module, '__path__', None)
    if path is None:
        raise ValueError('%r is not a package' % import_path)
    basename = module.__name__ + '.'
    for modname, ispkg in _iter_modules(path):
        modname = basename + modname
        if ispkg:
            if include_packages:
                yield modname
            if recursive:
                for item in find_modules(modname, include_packages, True):
                    yield item

        else:
            yield modname


def validate_arguments(func, args, kwargs, drop_extra = True):
    parser = _parse_signature(func)
    args, kwargs, missing, extra, extra_positional = parser(args, kwargs)[:5]
    if missing:
        raise ArgumentValidationError(tuple(missing))
    elif (extra or extra_positional) and not drop_extra:
        raise ArgumentValidationError(None, extra, extra_positional)
    return (tuple(args), kwargs)


def bind_arguments(func, args, kwargs):
    args, kwargs, missing, extra, extra_positional, arg_spec, vararg_var, kwarg_var = _parse_signature(func)(args, kwargs)
    values = {}
    for (name, has_default, default), value in zip(arg_spec, args):
        values[name] = value

    if vararg_var is not None:
        values[vararg_var] = tuple(extra_positional)
    elif extra_positional:
        raise TypeError('too many positional arguments')
    if kwarg_var is not None:
        multikw = set(extra) & set([ x[0] for x in arg_spec ])
        if multikw:
            raise TypeError('got multiple values for keyword argument ' + repr(iter(multikw).next()))
        values[kwarg_var] = extra
    elif extra:
        raise TypeError('got unexpected keyword argument ' + repr(iter(extra).next()))
    return values


class ArgumentValidationError(ValueError):

    def __init__(self, missing = None, extra = None, extra_positional = None):
        self.missing = set(missing or ())
        self.extra = extra or {}
        self.extra_positional = extra_positional or []
        ValueError.__init__(self, 'function arguments invalid.  (%d missing, %d additional)' % (len(self.missing), len(self.extra) + len(self.extra_positional)))


from werkzeug.http import quote_header_value, unquote_header_value
from werkzeug.exceptions import BadRequest
from werkzeug.datastructures import TypeConversionDict
from werkzeug.datastructures import MultiDict, CombinedMultiDict, Headers, EnvironHeaders