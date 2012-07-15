#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\_markupsafe\__init__.py
import re
from itertools import imap
__all__ = ['Markup',
 'soft_unicode',
 'escape',
 'escape_silent']
_striptags_re = re.compile('(<!--.*?-->|<[^>]*>)')
_entity_re = re.compile('&([^;]+);')

class Markup(unicode):
    __slots__ = ()

    def __new__(cls, base = u'', encoding = None, errors = 'strict'):
        if hasattr(base, '__html__'):
            base = base.__html__()
        if encoding is None:
            return unicode.__new__(cls, base)
        return unicode.__new__(cls, base, encoding, errors)

    def __html__(self):
        return self

    def __add__(self, other):
        if hasattr(other, '__html__') or isinstance(other, basestring):
            return self.__class__(unicode(self) + unicode(escape(other)))
        return NotImplemented

    def __radd__(self, other):
        if hasattr(other, '__html__') or isinstance(other, basestring):
            return self.__class__(unicode(escape(other)) + unicode(self))
        return NotImplemented

    def __mul__(self, num):
        if isinstance(num, (int, long)):
            return self.__class__(unicode.__mul__(self, num))
        return NotImplemented

    __rmul__ = __mul__

    def __mod__(self, arg):
        if isinstance(arg, tuple):
            arg = tuple(imap(_MarkupEscapeHelper, arg))
        else:
            arg = _MarkupEscapeHelper(arg)
        return self.__class__(unicode.__mod__(self, arg))

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, unicode.__repr__(self))

    def join(self, seq):
        return self.__class__(unicode.join(self, imap(escape, seq)))

    join.__doc__ = unicode.join.__doc__

    def split(self, *args, **kwargs):
        return map(self.__class__, unicode.split(self, *args, **kwargs))

    split.__doc__ = unicode.split.__doc__

    def rsplit(self, *args, **kwargs):
        return map(self.__class__, unicode.rsplit(self, *args, **kwargs))

    rsplit.__doc__ = unicode.rsplit.__doc__

    def splitlines(self, *args, **kwargs):
        return map(self.__class__, unicode.splitlines(self, *args, **kwargs))

    splitlines.__doc__ = unicode.splitlines.__doc__

    def unescape(self):
        from jinja2._markupsafe._constants import HTML_ENTITIES

        def handle_match(m):
            name = m.group(1)
            if name in HTML_ENTITIES:
                return unichr(HTML_ENTITIES[name])
            try:
                if name[:2] in ('#x', '#X'):
                    return unichr(int(name[2:], 16))
                if name.startswith('#'):
                    return unichr(int(name[1:]))
            except ValueError:
                pass

            return u''

        return _entity_re.sub(handle_match, unicode(self))

    def striptags(self):
        stripped = u' '.join(_striptags_re.sub('', self).split())
        return Markup(stripped).unescape()

    @classmethod
    def escape(cls, s):
        rv = escape(s)
        if rv.__class__ is not cls:
            return cls(rv)
        return rv

    def make_wrapper(name):
        orig = getattr(unicode, name)

        def func(self, *args, **kwargs):
            args = _escape_argspec(list(args), enumerate(args))
            _escape_argspec(kwargs, kwargs.iteritems())
            return self.__class__(orig(self, *args, **kwargs))

        func.__name__ = orig.__name__
        func.__doc__ = orig.__doc__
        return func

    for method in ('__getitem__', 'capitalize', 'title', 'lower', 'upper', 'replace', 'ljust', 'rjust', 'lstrip', 'rstrip', 'center', 'strip', 'translate', 'expandtabs', 'swapcase', 'zfill'):
        locals()[method] = make_wrapper(method)

    if hasattr(unicode, 'partition'):
        partition = (make_wrapper('partition'),)
        rpartition = make_wrapper('rpartition')
    if hasattr(unicode, 'format'):
        format = make_wrapper('format')
    if hasattr(unicode, '__getslice__'):
        __getslice__ = make_wrapper('__getslice__')
    del method
    del make_wrapper


def _escape_argspec(obj, iterable):
    for key, value in iterable:
        if hasattr(value, '__html__') or isinstance(value, basestring):
            obj[key] = escape(value)

    return obj


class _MarkupEscapeHelper(object):

    def __init__(self, obj):
        self.obj = obj

    __getitem__ = lambda s, x: _MarkupEscapeHelper(s.obj[x])
    __str__ = lambda s: str(escape(s.obj))
    __unicode__ = lambda s: unicode(escape(s.obj))
    __repr__ = lambda s: str(escape(repr(s.obj)))
    __int__ = lambda s: int(s.obj)
    __float__ = lambda s: float(s.obj)


try:
    from jinja2._markupsafe._speedups import escape, escape_silent, soft_unicode
except ImportError:
    from jinja2._markupsafe._native import escape, escape_silent, soft_unicode