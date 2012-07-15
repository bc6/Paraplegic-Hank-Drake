#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\utils.py
import re
import sys
import errno
try:
    from urllib.parse import quote_from_bytes as url_quote
except ImportError:
    from urllib import quote as url_quote

try:
    from thread import allocate_lock
except ImportError:
    from dummy_thread import allocate_lock

from collections import deque
from itertools import imap
_word_split_re = re.compile('(\\s+)')
_punctuation_re = re.compile('^(?P<lead>(?:%s)*)(?P<middle>.*?)(?P<trail>(?:%s)*)$' % ('|'.join(imap(re.escape, ('(', '<', '&lt;'))), '|'.join(imap(re.escape, ('.', ',', ')', '>', '\n', '&gt;')))))
_simple_email_re = re.compile('^\\S+@[a-zA-Z0-9._-]+\\.[a-zA-Z0-9._-]+$')
_striptags_re = re.compile('(<!--.*?-->|<[^>]*>)')
_entity_re = re.compile('&([^;]+);')
_letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
_digits = '0123456789'
missing = type('MissingType', (), {'__repr__': lambda x: 'missing'})()
internal_code = set()
_concat = u''.join
try:

    def _test_gen_bug():
        raise TypeError(_test_gen_bug)
        yield


    _concat(_test_gen_bug())
except TypeError as _error:
    if not _error.args or _error.args[0] is not _test_gen_bug:

        def concat(gen):
            try:
                return _concat(list(gen))
            except Exception:
                exc_type, exc_value, tb = sys.exc_info()
                raise exc_type, exc_value, tb.tb_next


    else:
        concat = _concat
    del _test_gen_bug
    del _error

try:
    next = next
except NameError:

    def next(x):
        return x.next()


if sys.version_info < (3, 0):

    def _encode_filename(filename):
        if isinstance(filename, unicode):
            return filename.encode('utf-8')
        return filename


else:

    def _encode_filename(filename):
        return filename


from keyword import iskeyword as is_python_keyword

class _C(object):

    def method(self):
        pass


def _func():
    yield


FunctionType = type(_func)
GeneratorType = type(_func())
MethodType = type(_C.method)
CodeType = type(_C.method.func_code)
try:
    raise TypeError()
except TypeError:
    _tb = sys.exc_info()[2]
    TracebackType = type(_tb)
    FrameType = type(_tb.tb_frame)

del _C
del _tb
del _func

def contextfunction(f):
    f.contextfunction = True
    return f


def evalcontextfunction(f):
    f.evalcontextfunction = True
    return f


def environmentfunction(f):
    f.environmentfunction = True
    return f


def internalcode(f):
    internal_code.add(f.func_code)
    return f


def is_undefined(obj):
    from jinja2.runtime import Undefined
    return isinstance(obj, Undefined)


def consume(iterable):
    for event in iterable:
        pass


def clear_caches():
    from jinja2.environment import _spontaneous_environments
    from jinja2.lexer import _lexer_cache
    _spontaneous_environments.clear()
    _lexer_cache.clear()


def import_string(import_name, silent = False):
    try:
        if ':' in import_name:
            module, obj = import_name.split(':', 1)
        elif '.' in import_name:
            items = import_name.split('.')
            module = '.'.join(items[:-1])
            obj = items[-1]
        else:
            return __import__(import_name)
        return getattr(__import__(module, None, None, [obj]), obj)
    except (ImportError, AttributeError):
        if not silent:
            raise 


def open_if_exists(filename, mode = 'rb'):
    try:
        return open(filename, mode)
    except IOError as e:
        if e.errno not in (errno.ENOENT, errno.EISDIR):
            raise 


def object_type_repr(obj):
    if obj is None:
        return 'None'
    if obj is Ellipsis:
        return 'Ellipsis'
    if obj.__class__.__module__ in ('__builtin__', 'builtins'):
        name = obj.__class__.__name__
    else:
        name = obj.__class__.__module__ + '.' + obj.__class__.__name__
    return '%s object' % name


def pformat(obj, verbose = False):
    try:
        from pretty import pretty
        return pretty(obj, verbose=verbose)
    except ImportError:
        from pprint import pformat
        return pformat(obj)


def urlize(text, trim_url_limit = None, nofollow = False):
    trim_url = lambda x, limit = trim_url_limit: limit is not None and x[:limit] + (len(x) >= limit and '...' or '') or x
    words = _word_split_re.split(unicode(escape(text)))
    nofollow_attr = nofollow and ' rel="nofollow"' or ''
    for i, word in enumerate(words):
        match = _punctuation_re.match(word)
        if match:
            lead, middle, trail = match.groups()
            if middle.startswith('www.') or '@' not in middle and not middle.startswith('http://') and len(middle) > 0 and middle[0] in _letters + _digits and (middle.endswith('.org') or middle.endswith('.net') or middle.endswith('.com')):
                middle = '<a href="http://%s"%s>%s</a>' % (middle, nofollow_attr, trim_url(middle))
            if middle.startswith('http://') or middle.startswith('https://'):
                middle = '<a href="%s"%s>%s</a>' % (middle, nofollow_attr, trim_url(middle))
            if '@' in middle and not middle.startswith('www.') and ':' not in middle and _simple_email_re.match(middle):
                middle = '<a href="mailto:%s">%s</a>' % (middle, middle)
            if lead + middle + trail != word:
                words[i] = lead + middle + trail

    return u''.join(words)


def generate_lorem_ipsum(n = 5, html = True, min = 20, max = 100):
    from jinja2.constants import LOREM_IPSUM_WORDS
    from random import choice, randrange
    words = LOREM_IPSUM_WORDS.split()
    result = []
    for _ in xrange(n):
        next_capitalized = True
        last_comma = last_fullstop = 0
        word = None
        last = None
        p = []
        for idx, _ in enumerate(xrange(randrange(min, max))):
            while True:
                word = choice(words)
                if word != last:
                    last = word
                    break

            if next_capitalized:
                word = word.capitalize()
                next_capitalized = False
            if idx - randrange(3, 8) > last_comma:
                last_comma = idx
                last_fullstop += 2
                word += ','
            if idx - randrange(10, 20) > last_fullstop:
                last_comma = last_fullstop = idx
                word += '.'
                next_capitalized = True
            p.append(word)

        p = u' '.join(p)
        if p.endswith(','):
            p = p[:-1] + '.'
        elif not p.endswith('.'):
            p += '.'
        result.append(p)

    if not html:
        return u'\n\n'.join(result)
    return Markup(u'\n'.join((u'<p>%s</p>' % escape(x) for x in result)))


def unicode_urlencode(obj, charset = 'utf-8'):
    if not isinstance(obj, basestring):
        obj = unicode(obj)
    if isinstance(obj, unicode):
        obj = obj.encode(charset)
    return unicode(url_quote(obj))


class LRUCache(object):

    def __init__(self, capacity):
        self.capacity = capacity
        self._mapping = {}
        self._queue = deque()
        self._postinit()

    def _postinit(self):
        self._popleft = self._queue.popleft
        self._pop = self._queue.pop
        if hasattr(self._queue, 'remove'):
            self._remove = self._queue.remove
        self._wlock = allocate_lock()
        self._append = self._queue.append

    def _remove(self, obj):
        for idx, item in enumerate(self._queue):
            if item == obj:
                del self._queue[idx]
                break

    def __getstate__(self):
        return {'capacity': self.capacity,
         '_mapping': self._mapping,
         '_queue': self._queue}

    def __setstate__(self, d):
        self.__dict__.update(d)
        self._postinit()

    def __getnewargs__(self):
        return (self.capacity,)

    def copy(self):
        rv = self.__class__(self.capacity)
        rv._mapping.update(self._mapping)
        rv._queue = deque(self._queue)
        return rv

    def get(self, key, default = None):
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, key, default = None):
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def clear(self):
        self._wlock.acquire()
        try:
            self._mapping.clear()
            self._queue.clear()
        finally:
            self._wlock.release()

    def __contains__(self, key):
        return key in self._mapping

    def __len__(self):
        return len(self._mapping)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self._mapping)

    def __getitem__(self, key):
        rv = self._mapping[key]
        if self._queue[-1] != key:
            try:
                self._remove(key)
            except ValueError:
                pass

            self._append(key)
        return rv

    def __setitem__(self, key, value):
        self._wlock.acquire()
        try:
            if key in self._mapping:
                try:
                    self._remove(key)
                except ValueError:
                    pass

            elif len(self._mapping) == self.capacity:
                del self._mapping[self._popleft()]
            self._append(key)
            self._mapping[key] = value
        finally:
            self._wlock.release()

    def __delitem__(self, key):
        self._wlock.acquire()
        try:
            del self._mapping[key]
            try:
                self._remove(key)
            except ValueError:
                pass

        finally:
            self._wlock.release()

    def items(self):
        result = [ (key, self._mapping[key]) for key in list(self._queue) ]
        result.reverse()
        return result

    def iteritems(self):
        return iter(self.items())

    def values(self):
        return [ x[1] for x in self.items() ]

    def itervalue(self):
        return iter(self.values())

    def keys(self):
        return list(self)

    def iterkeys(self):
        return reversed(tuple(self._queue))

    __iter__ = iterkeys

    def __reversed__(self):
        return iter(tuple(self._queue))

    __copy__ = copy


try:
    from collections import MutableMapping
    MutableMapping.register(LRUCache)
except ImportError:
    pass

class Cycler(object):

    def __init__(self, *items):
        if not items:
            raise RuntimeError('at least one item has to be provided')
        self.items = items
        self.reset()

    def reset(self):
        self.pos = 0

    @property
    def current(self):
        return self.items[self.pos]

    def next(self):
        rv = self.current
        self.pos = (self.pos + 1) % len(self.items)
        return rv


class Joiner(object):

    def __init__(self, sep = u', '):
        self.sep = sep
        self.used = False

    def __call__(self):
        if not self.used:
            self.used = True
            return u''
        return self.sep


try:
    from markupsafe import Markup, escape, soft_unicode
except ImportError:
    from jinja2._markupsafe import Markup, escape, soft_unicode

try:
    from functools import partial
except ImportError:

    class partial(object):

        def __init__(self, _func, *args, **kwargs):
            self._func = _func
            self._args = args
            self._kwargs = kwargs

        def __call__(self, *args, **kwargs):
            kwargs.update(self._kwargs)
            return self._func(*(self._args + args), **kwargs)