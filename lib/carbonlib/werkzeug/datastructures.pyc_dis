#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\datastructures.py
import re
import codecs
import mimetypes
from werkzeug._internal import _proxy_repr, _missing, _empty_stream
_locale_delim_re = re.compile('[_-]')

def is_immutable(self):
    raise TypeError('%r objects are immutable' % self.__class__.__name__)


def iter_multi_items(mapping):
    if isinstance(mapping, MultiDict):
        for item in mapping.iteritems(multi=True):
            yield item

    elif isinstance(mapping, dict):
        for key, value in mapping.iteritems():
            if isinstance(value, (tuple, list)):
                for value in value:
                    yield (key, value)

            else:
                yield (key, value)

    else:
        for item in mapping:
            yield item


class ImmutableListMixin(object):

    def __reduce_ex__(self, protocol):
        return (type(self), (list(self),))

    def __delitem__(self, key):
        is_immutable(self)

    def __delslice__(self, i, j):
        is_immutable(self)

    def __iadd__(self, other):
        is_immutable(self)

    __imul__ = __iadd__

    def __setitem__(self, key, value):
        is_immutable(self)

    def __setslice__(self, i, j, value):
        is_immutable(self)

    def append(self, item):
        is_immutable(self)

    remove = append

    def extend(self, iterable):
        is_immutable(self)

    def insert(self, pos, value):
        is_immutable(self)

    def pop(self, index = -1):
        is_immutable(self)

    def reverse(self):
        is_immutable(self)

    def sort(self, cmp = None, key = None, reverse = None):
        is_immutable(self)


class ImmutableList(ImmutableListMixin, list):
    __repr__ = _proxy_repr(list)


class ImmutableDictMixin(object):

    def __reduce_ex__(self, protocol):
        return (type(self), (dict(self),))

    def setdefault(self, key, default = None):
        is_immutable(self)

    def update(self, *args, **kwargs):
        is_immutable(self)

    def pop(self, key, default = None):
        is_immutable(self)

    def popitem(self):
        is_immutable(self)

    def __setitem__(self, key, value):
        is_immutable(self)

    def __delitem__(self, key):
        is_immutable(self)

    def clear(self):
        is_immutable(self)


class ImmutableMultiDictMixin(ImmutableDictMixin):

    def __reduce_ex__(self, protocol):
        return (type(self), (self.items(multi=True),))

    def add(self, key, value):
        is_immutable(self)

    def popitemlist(self):
        is_immutable(self)

    def poplist(self, key):
        is_immutable(self)

    def setlist(self, key, new_list):
        is_immutable(self)

    def setlistdefault(self, key, default_list = None):
        is_immutable(self)


class UpdateDictMixin(object):
    on_update = None

    def calls_update(name):

        def oncall(self, *args, **kw):
            rv = getattr(super(UpdateDictMixin, self), name)(*args, **kw)
            if self.on_update is not None:
                self.on_update(self)
            return rv

        oncall.__name__ = name
        return oncall

    __setitem__ = calls_update('__setitem__')
    __delitem__ = calls_update('__delitem__')
    clear = calls_update('clear')
    pop = calls_update('pop')
    popitem = calls_update('popitem')
    setdefault = calls_update('setdefault')
    update = calls_update('update')
    del calls_update


class TypeConversionDict(dict):

    def get(self, key, default = None, type = None):
        try:
            rv = self[key]
            if type is not None:
                rv = type(rv)
        except (KeyError, ValueError):
            rv = default

        return rv


class ImmutableTypeConversionDict(ImmutableDictMixin, TypeConversionDict):

    def copy(self):
        return TypeConversionDict(self)

    def __copy__(self):
        return self


class MultiDict(TypeConversionDict):
    KeyError = None

    def __init__(self, mapping = None):
        if isinstance(mapping, MultiDict):
            dict.__init__(self, ((k, l[:]) for k, l in mapping.iterlists()))
        elif isinstance(mapping, dict):
            tmp = {}
            for key, value in mapping.iteritems():
                if isinstance(value, (tuple, list)):
                    value = list(value)
                else:
                    value = [value]
                tmp[key] = value

            dict.__init__(self, tmp)
        else:
            tmp = {}
            for key, value in mapping or ():
                tmp.setdefault(key, []).append(value)

            dict.__init__(self, tmp)

    def __getstate__(self):
        return dict(self.lists())

    def __setstate__(self, value):
        dict.clear(self)
        dict.update(self, value)

    def __iter__(self):
        return self.iterkeys()

    def __getitem__(self, key):
        if key in self:
            return dict.__getitem__(self, key)[0]
        raise self.KeyError(key)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, [value])

    def add(self, key, value):
        dict.setdefault(self, key, []).append(value)

    def getlist(self, key, type = None):
        try:
            rv = dict.__getitem__(self, key)
        except KeyError:
            return []

        if type is None:
            return list(rv)
        result = []
        for item in rv:
            try:
                result.append(type(item))
            except ValueError:
                pass

        return result

    def setlist(self, key, new_list):
        dict.__setitem__(self, key, list(new_list))

    def setdefault(self, key, default = None):
        if key not in self:
            self[key] = default
        else:
            default = self[key]
        return default

    def setlistdefault(self, key, default_list = None):
        if key not in self:
            default_list = list(default_list or ())
            dict.__setitem__(self, key, default_list)
        else:
            default_list = dict.__getitem__(self, key)
        return default_list

    def items(self, multi = False):
        return list(self.iteritems(multi))

    def lists(self):
        return list(self.iterlists())

    def values(self):
        return [ self[key] for key in self.iterkeys() ]

    def listvalues(self):
        return list(self.iterlistvalues())

    def iteritems(self, multi = False):
        for key, values in dict.iteritems(self):
            if multi:
                for value in values:
                    yield (key, value)

            else:
                yield (key, values[0])

    def iterlists(self):
        for key, values in dict.iteritems(self):
            yield (key, list(values))

    def itervalues(self):
        for values in dict.itervalues(self):
            yield values[0]

    def iterlistvalues(self):
        for values in dict.itervalues(self):
            yield list(values)

    def copy(self):
        return self.__class__(self)

    def to_dict(self, flat = True):
        if flat:
            return dict(self.iteritems())
        return dict(self.lists())

    def update(self, other_dict):
        for key, value in iter_multi_items(other_dict):
            MultiDict.add(self, key, value)

    def pop(self, key, default = _missing):
        try:
            return dict.pop(self, key)[0]
        except KeyError as e:
            if default is not _missing:
                return default
            raise self.KeyError(str(e))

    def popitem(self):
        try:
            item = dict.popitem(self)
            return (item[0], item[1][0])
        except KeyError as e:
            raise self.KeyError(str(e))

    def poplist(self, key):
        return dict.pop(self, key, [])

    def popitemlist(self):
        try:
            return dict.popitem(self)
        except KeyError as e:
            raise self.KeyError(str(e))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.items(multi=True))


class _omd_bucket(object):
    __slots__ = ('prev', 'key', 'value', 'next')

    def __init__(self, omd, key, value):
        self.prev = omd._last_bucket
        self.key = key
        self.value = value
        self.next = None
        if omd._first_bucket is None:
            omd._first_bucket = self
        if omd._last_bucket is not None:
            omd._last_bucket.next = self
        omd._last_bucket = self

    def unlink(self, omd):
        if self.prev:
            self.prev.next = self.next
        if self.next:
            self.next.prev = self.prev
        if omd._first_bucket is self:
            omd._first_bucket = self.next
        if omd._last_bucket is self:
            omd._last_bucket = self.prev


class OrderedMultiDict(MultiDict):
    KeyError = None

    def __init__(self, mapping = None):
        dict.__init__(self)
        self._first_bucket = self._last_bucket = None
        if mapping is not None:
            OrderedMultiDict.update(self, mapping)

    def __eq__(self, other):
        if not isinstance(other, MultiDict):
            return NotImplemented
        if isinstance(other, OrderedMultiDict):
            iter1 = self.iteritems(multi=True)
            iter2 = other.iteritems(multi=True)
            try:
                for k1, v1 in iter1:
                    k2, v2 = iter2.next()
                    if k1 != k2 or v1 != v2:
                        return False

            except StopIteration:
                return False

            try:
                iter2.next()
            except StopIteration:
                return True

            return False
        if len(self) != len(other):
            return False
        for key, values in self.iterlists():
            if other.getlist(key) != values:
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __reduce_ex__(self, protocol):
        return (type(self), (self.items(multi=True),))

    def __getstate__(self):
        return self.items(multi=True)

    def __setstate__(self, values):
        dict.clear(self)
        for key, value in values:
            self.add(key, value)

    def __getitem__(self, key):
        if key in self:
            return dict.__getitem__(self, key)[0].value
        raise self.KeyError(key)

    def __setitem__(self, key, value):
        self.poplist(key)
        self.add(key, value)

    def __delitem__(self, key):
        self.pop(key)

    def iterkeys(self):
        return (key for key, value in self.iteritems())

    def itervalues(self):
        return (value for key, value in self.iteritems())

    def iteritems(self, multi = False):
        ptr = self._first_bucket
        if multi:
            while ptr is not None:
                yield (ptr.key, ptr.value)
                ptr = ptr.next

        else:
            returned_keys = set()
            while ptr is not None:
                if ptr.key not in returned_keys:
                    returned_keys.add(ptr.key)
                    yield (ptr.key, ptr.value)
                ptr = ptr.next

    def iterlists(self):
        returned_keys = set()
        ptr = self._first_bucket
        while ptr is not None:
            if ptr.key not in returned_keys:
                yield (ptr.key, self.getlist(ptr.key))
                returned_keys.add(ptr.key)
            ptr = ptr.next

    def iterlistvalues(self):
        for key, values in self.iterlists():
            yield values

    def add(self, key, value):
        dict.setdefault(self, key, []).append(_omd_bucket(self, key, value))

    def getlist(self, key, type = None):
        try:
            rv = dict.__getitem__(self, key)
        except KeyError:
            return []

        if type is None:
            return [ x.value for x in rv ]
        result = []
        for item in rv:
            try:
                result.append(type(item.value))
            except ValueError:
                pass

        return result

    def setlist(self, key, new_list):
        self.poplist(key)
        for value in new_list:
            self.add(key, value)

    def setlistdefault(self, key, default_list = None):
        raise TypeError('setlistdefault is unsupported for ordered multi dicts')

    def update(self, mapping):
        for key, value in iter_multi_items(mapping):
            OrderedMultiDict.add(self, key, value)

    def poplist(self, key):
        buckets = dict.pop(self, key, ())
        for bucket in buckets:
            bucket.unlink(self)

        return [ x.value for x in buckets ]

    def pop(self, key, default = _missing):
        try:
            buckets = dict.pop(self, key)
        except KeyError as e:
            if default is not _missing:
                return default
            raise self.KeyError(str(e))

        for bucket in buckets:
            bucket.unlink(self)

        return buckets[0].value

    def popitem(self):
        try:
            key, buckets = dict.popitem(self)
        except KeyError as e:
            raise self.KeyError(str(e))

        for bucket in buckets:
            bucket.unlink(self)

        return (key, buckets[0].value)

    def popitemlist(self):
        try:
            key, buckets = dict.popitem(self)
        except KeyError as e:
            raise self.KeyError(str(e))

        for bucket in buckets:
            bucket.unlink(self)

        return (key, [ x.value for x in buckets ])


def _options_header_vkw(value, kw):
    if not kw:
        return value
    return dump_options_header(value, dict(((k.replace('_', '-'), v) for k, v in kw.items())))


class Headers(object):
    KeyError = None

    def __init__(self, defaults = None, _list = None):
        if _list is None:
            _list = []
        self._list = _list
        if defaults is not None:
            if isinstance(defaults, (list, Headers)):
                self._list.extend(defaults)
            else:
                self.extend(defaults)

    @classmethod
    def linked(cls, headerlist):
        return cls(_list=headerlist)

    def __getitem__(self, key, _index_operation = True):
        if _index_operation:
            if isinstance(key, (int, long)):
                return self._list[key]
            if isinstance(key, slice):
                return self.__class__(self._list[key])
        ikey = key.lower()
        for k, v in self._list:
            if k.lower() == ikey:
                return v

        raise self.KeyError(key)

    def __eq__(self, other):
        return other.__class__ is self.__class__ and set(other._list) == set(self._list)

    def __ne__(self, other):
        return not self.__eq__(other)

    def get(self, key, default = None, type = None):
        try:
            rv = self.__getitem__(key, _index_operation=False)
        except KeyError:
            return default

        if type is None:
            return rv
        try:
            return type(rv)
        except ValueError:
            return default

    def getlist(self, key, type = None):
        ikey = key.lower()
        result = []
        for k, v in self:
            if k.lower() == ikey:
                if type is not None:
                    try:
                        v = type(v)
                    except ValueError:
                        continue

                result.append(v)

        return result

    def get_all(self, name):
        return self.getlist(name)

    def iteritems(self, lower = False):
        for key, value in self:
            if lower:
                key = key.lower()
            yield (key, value)

    def iterkeys(self, lower = False):
        for key, _ in self.iteritems(lower):
            yield key

    def itervalues(self):
        for _, value in self.iteritems():
            yield value

    def keys(self, lower = False):
        return list(self.iterkeys(lower))

    def values(self):
        return list(self.itervalues())

    def items(self, lower = False):
        return list(self.iteritems(lower))

    def extend(self, iterable):
        if isinstance(iterable, dict):
            for key, value in iterable.iteritems():
                if isinstance(value, (tuple, list)):
                    for v in value:
                        self.add(key, v)

                else:
                    self.add(key, value)

        else:
            for key, value in iterable:
                self.add(key, value)

    def __delitem__(self, key, _index_operation = True):
        if _index_operation and isinstance(key, (int, long, slice)):
            del self._list[key]
            return
        key = key.lower()
        new = []
        for k, v in self._list:
            if k.lower() != key:
                new.append((k, v))

        self._list[:] = new

    def remove(self, key):
        return self.__delitem__(key, _index_operation=False)

    def pop(self, key = None, default = _missing):
        if key is None:
            return self._list.pop()
        if isinstance(key, (int, long)):
            return self._list.pop(key)
        try:
            rv = self[key]
            self.remove(key)
        except KeyError:
            if default is not _missing:
                return default
            raise 

        return rv

    def popitem(self):
        return self.pop()

    def __contains__(self, key):
        try:
            self.__getitem__(key, _index_operation=False)
        except KeyError:
            return False

        return True

    has_key = __contains__

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def add(self, _key, _value, **kw):
        self._list.append((_key, _options_header_vkw(_value, kw)))

    def add_header(self, _key, _value, **_kw):
        self.add(_key, _value, **_kw)

    def clear(self):
        del self._list[:]

    def set(self, _key, _value, **kw):
        lc_key = _key.lower()
        _value = _options_header_vkw(_value, kw)
        for idx, (old_key, old_value) in enumerate(self._list):
            if old_key.lower() == lc_key:
                self._list[idx] = (_key, _value)
                break
        else:
            return self.add(_key, _value)

        self._list[idx + 1:] = [ (k, v) for k, v in self._list[idx + 1:] if k.lower() != lc_key ]

    def setdefault(self, key, value):
        if key in self:
            return self[key]
        self.set(key, value)
        return value

    def __setitem__(self, key, value):
        if isinstance(key, (slice, int, long)):
            self._list[key] = value
        else:
            self.set(key, value)

    def to_list(self, charset = 'utf-8'):
        result = []
        for k, v in self:
            if isinstance(v, unicode):
                v = v.encode(charset)
            else:
                v = str(v)
            result.append((k, v))

        return result

    def copy(self):
        return self.__class__(self._list)

    def __copy__(self):
        return self.copy()

    def __str__(self, charset = 'utf-8'):
        strs = []
        for key, value in self.to_list(charset):
            strs.append('%s: %s' % (key, value))

        strs.append('\r\n')
        return '\r\n'.join(strs)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, list(self))


class ImmutableHeadersMixin(object):

    def __delitem__(self, key):
        is_immutable(self)

    def __setitem__(self, key, value):
        is_immutable(self)

    set = __setitem__

    def add(self, item):
        is_immutable(self)

    remove = add_header = add

    def extend(self, iterable):
        is_immutable(self)

    def insert(self, pos, value):
        is_immutable(self)

    def pop(self, index = -1):
        is_immutable(self)

    def popitem(self):
        is_immutable(self)

    def setdefault(self, key, default):
        is_immutable(self)


class EnvironHeaders(ImmutableHeadersMixin, Headers):

    def __init__(self, environ):
        self.environ = environ

    @classmethod
    def linked(cls, environ):
        raise TypeError('%r object is always linked to environment, no separate initializer' % cls.__name__)

    def __eq__(self, other):
        return self.environ is other.environ

    def __getitem__(self, key, _index_operation = False):
        key = key.upper().replace('-', '_')
        if key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            return self.environ[key]
        return self.environ['HTTP_' + key]

    def __len__(self):
        return len(list(iter(self)))

    def __iter__(self):
        for key, value in self.environ.iteritems():
            if key.startswith('HTTP_') and key not in ('HTTP_CONTENT_TYPE', 'HTTP_CONTENT_LENGTH'):
                yield (key[5:].replace('_', '-').title(), value)
            elif key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                yield (key.replace('_', '-').title(), value)

    def copy(self):
        raise TypeError('cannot create %r copies' % self.__class__.__name__)


class CombinedMultiDict(ImmutableMultiDictMixin, MultiDict):

    def __reduce_ex__(self, protocol):
        return (type(self), (self.dicts,))

    def __init__(self, dicts = None):
        self.dicts = dicts or []

    @classmethod
    def fromkeys(cls):
        raise TypeError('cannot create %r instances by fromkeys' % cls.__name__)

    def __getitem__(self, key):
        for d in self.dicts:
            if key in d:
                return d[key]

        raise self.KeyError(key)

    def get(self, key, default = None, type = None):
        for d in self.dicts:
            if key in d:
                if type is not None:
                    try:
                        return type(d[key])
                    except ValueError:
                        continue

                return d[key]

        return default

    def getlist(self, key, type = None):
        rv = []
        for d in self.dicts:
            rv.extend(d.getlist(key, type))

        return rv

    def keys(self):
        rv = set()
        for d in self.dicts:
            rv.update(d.keys())

        return list(rv)

    def iteritems(self, multi = False):
        found = set()
        for d in self.dicts:
            for key, value in d.iteritems(multi):
                if multi:
                    yield (key, value)
                elif key not in found:
                    found.add(key)
                    yield (key, value)

    def itervalues(self):
        for key, value in self.iteritems():
            yield value

    def values(self):
        return list(self.itervalues())

    def items(self, multi = False):
        return list(self.iteritems(multi))

    def iterlists(self):
        rv = {}
        for d in self.dicts:
            for key, values in d.iterlists():
                rv.setdefault(key, []).extend(values)

        return rv.iteritems()

    def lists(self):
        return list(self.iterlists())

    def iterlistvalues(self):
        return (x[0] for x in self.lists())

    def listvalues(self):
        return list(self.iterlistvalues())

    def iterkeys(self):
        return iter(self.keys())

    __iter__ = iterkeys

    def copy(self):
        return self.__class__(self.dicts[:])

    def to_dict(self, flat = True):
        rv = {}
        for d in reversed(self.dicts):
            rv.update(d.to_dict(flat))

        return rv

    def __len__(self):
        return len(self.keys())

    def __contains__(self, key):
        for d in self.dicts:
            if key in d:
                return True

        return False

    has_key = __contains__

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.dicts)


class FileMultiDict(MultiDict):

    def add_file(self, name, file, filename = None, content_type = None):
        if isinstance(file, FileStorage):
            self[name] = file
            return
        if isinstance(file, basestring):
            if filename is None:
                filename = file
            file = open(file, 'rb')
        if filename and content_type is None:
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self[name] = FileStorage(file, filename, name, content_type)


class ImmutableDict(ImmutableDictMixin, dict):
    __repr__ = _proxy_repr(dict)

    def copy(self):
        return dict(self)

    def __copy__(self):
        return self


class ImmutableMultiDict(ImmutableMultiDictMixin, MultiDict):

    def copy(self):
        return MultiDict(self)

    def __copy__(self):
        return self


class ImmutableOrderedMultiDict(ImmutableMultiDictMixin, OrderedMultiDict):

    def copy(self):
        return OrderedMultiDict(self)

    def __copy__(self):
        return self


class Accept(ImmutableList):

    def __init__(self, values = ()):
        if values is None:
            list.__init__(self)
            self.provided = False
        elif isinstance(values, Accept):
            self.provided = values.provided
            list.__init__(self, values)
        else:
            self.provided = True
            values = [ (a, b) for b, a in values ]
            values.sort()
            values.reverse()
            list.__init__(self, [ (a, b) for b, a in values ])

    def _value_matches(self, value, item):
        return item == '*' or item.lower() == value.lower()

    def __getitem__(self, key):
        if isinstance(key, basestring):
            return self.quality(key)
        return list.__getitem__(self, key)

    def quality(self, key):
        for item, quality in self:
            if self._value_matches(key, item):
                return quality

        return 0

    def __contains__(self, value):
        for item, quality in self:
            if self._value_matches(value, item):
                return True

        return False

    def __repr__(self):
        return '%s([%s])' % (self.__class__.__name__, ', '.join(('(%r, %s)' % (x, y) for x, y in self)))

    def index(self, key):
        if isinstance(key, basestring):
            for idx, (item, quality) in enumerate(self):
                if self._value_matches(key, item):
                    return idx

            raise ValueError(key)
        return list.index(self, key)

    def find(self, key):
        try:
            return self.index(key)
        except ValueError:
            return -1

    def values(self):
        return list(self.itervalues())

    def itervalues(self):
        for item in self:
            yield item[0]

    def to_header(self):
        result = []
        for value, quality in self:
            if quality != 1:
                value = '%s;q=%s' % (value, quality)
            result.append(value)

        return ','.join(result)

    def __str__(self):
        return self.to_header()

    def best_match(self, matches, default = None):
        best_quality = -1
        result = default
        for server_item in matches:
            for client_item, quality in self:
                if quality <= best_quality:
                    break
                if self._value_matches(client_item, server_item):
                    best_quality = quality
                    result = server_item

        return result

    @property
    def best(self):
        if self:
            return self[0][0]


class MIMEAccept(Accept):

    def _value_matches(self, value, item):

        def _normalize(x):
            x = x.lower()
            return x == '*' and ('*', '*') or x.split('/', 1)

        if '/' not in value:
            raise ValueError('invalid mimetype %r' % value)
        value_type, value_subtype = _normalize(value)
        if value_type == '*' and value_subtype != '*':
            raise ValueError('invalid mimetype %r' % value)
        if '/' not in item:
            return False
        item_type, item_subtype = _normalize(item)
        if item_type == '*' and item_subtype != '*':
            return False
        return item_type == item_subtype == '*' or value_type == value_subtype == '*' or item_type == value_type and (item_subtype == '*' or value_subtype == '*' or item_subtype == value_subtype)

    @property
    def accept_html(self):
        return 'text/html' in self or 'application/xhtml+xml' in self or self.accept_xhtml

    @property
    def accept_xhtml(self):
        return 'application/xhtml+xml' in self or 'application/xml' in self


class LanguageAccept(Accept):

    def _value_matches(self, value, item):

        def _normalize(language):
            return _locale_delim_re.split(language.lower())

        return item == '*' or _normalize(value) == _normalize(item)


class CharsetAccept(Accept):

    def _value_matches(self, value, item):

        def _normalize(name):
            try:
                return codecs.lookup(name).name
            except LookupError:
                return name.lower()

        return item == '*' or _normalize(value) == _normalize(item)


def cache_property(key, empty, type):
    return property(lambda x: x._get_cache_value(key, empty, type), lambda x, v: x._set_cache_value(key, v, type), lambda x: x._del_cache_value(key), 'accessor for %r' % key)


class _CacheControl(UpdateDictMixin, dict):
    no_cache = cache_property('no-cache', '*', None)
    no_store = cache_property('no-store', None, bool)
    max_age = cache_property('max-age', -1, int)
    no_transform = cache_property('no-transform', None, None)

    def __init__(self, values = (), on_update = None):
        dict.__init__(self, values or ())
        self.on_update = on_update
        self.provided = values is not None

    def _get_cache_value(self, key, empty, type):
        if type is bool:
            return key in self
        if key in self:
            value = self[key]
            if value is None:
                return empty
            if type is not None:
                try:
                    value = type(value)
                except ValueError:
                    pass

            return value

    def _set_cache_value(self, key, value, type):
        if type is bool:
            if value:
                self[key] = None
            else:
                self.pop(key, None)
        elif value is None:
            self.pop(key)
        elif value is True:
            self[key] = None
        else:
            self[key] = value

    def _del_cache_value(self, key):
        if key in self:
            del self[key]

    def to_header(self):
        return dump_header(self)

    def __str__(self):
        return self.to_header()

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.to_header())


class RequestCacheControl(ImmutableDictMixin, _CacheControl):
    max_stale = cache_property('max-stale', '*', int)
    min_fresh = cache_property('min-fresh', '*', int)
    no_transform = cache_property('no-transform', None, None)
    only_if_cached = cache_property('only-if-cached', None, bool)


class ResponseCacheControl(_CacheControl):
    public = cache_property('public', None, bool)
    private = cache_property('private', '*', None)
    must_revalidate = cache_property('must-revalidate', None, bool)
    proxy_revalidate = cache_property('proxy-revalidate', None, bool)
    s_maxage = cache_property('s-maxage', None, None)


_CacheControl.cache_property = staticmethod(cache_property)

class CallbackDict(UpdateDictMixin, dict):

    def __init__(self, initial = None, on_update = None):
        dict.__init__(self, initial or ())
        self.on_update = on_update

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict.__repr__(self))


class HeaderSet(object):

    def __init__(self, headers = None, on_update = None):
        self._headers = list(headers or ())
        self._set = set([ x.lower() for x in self._headers ])
        self.on_update = on_update

    def add(self, header):
        self.update((header,))

    def remove(self, header):
        key = header.lower()
        if key not in self._set:
            raise KeyError(header)
        self._set.remove(key)
        for idx, key in enumerate(self._headers):
            if key.lower() == header:
                del self._headers[idx]
                break

        if self.on_update is not None:
            self.on_update(self)

    def update(self, iterable):
        inserted_any = False
        for header in iterable:
            key = header.lower()
            if key not in self._set:
                self._headers.append(header)
                self._set.add(key)
                inserted_any = True

        if inserted_any and self.on_update is not None:
            self.on_update(self)

    def discard(self, header):
        try:
            return self.remove(header)
        except KeyError:
            pass

    def find(self, header):
        header = header.lower()
        for idx, item in enumerate(self._headers):
            if item.lower() == header:
                return idx

        return -1

    def index(self, header):
        rv = self.find(header)
        if rv < 0:
            raise IndexError(header)
        return rv

    def clear(self):
        self._set.clear()
        del self._headers[:]
        if self.on_update is not None:
            self.on_update(self)

    def as_set(self, preserve_casing = False):
        if preserve_casing:
            return set(self._headers)
        return set(self._set)

    def to_header(self):
        return ', '.join(map(quote_header_value, self._headers))

    def __getitem__(self, idx):
        return self._headers[idx]

    def __delitem__(self, idx):
        rv = self._headers.pop(idx)
        self._set.remove(rv.lower())
        if self.on_update is not None:
            self.on_update(self)

    def __setitem__(self, idx, value):
        old = self._headers[idx]
        self._set.remove(old.lower())
        self._headers[idx] = value
        self._set.add(value.lower())
        if self.on_update is not None:
            self.on_update(self)

    def __contains__(self, header):
        return header.lower() in self._set

    def __len__(self):
        return len(self._set)

    def __iter__(self):
        return iter(self._headers)

    def __nonzero__(self):
        return bool(self._set)

    def __str__(self):
        return self.to_header()

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._headers)


class ETags(object):

    def __init__(self, strong_etags = None, weak_etags = None, star_tag = False):
        self._strong = frozenset(not star_tag and strong_etags or ())
        self._weak = frozenset(weak_etags or ())
        self.star_tag = star_tag

    def as_set(self, include_weak = False):
        rv = set(self._strong)
        if include_weak:
            rv.update(self._weak)
        return rv

    def is_weak(self, etag):
        return etag in self._weak

    def contains_weak(self, etag):
        return self.is_weak(etag) or self.contains(etag)

    def contains(self, etag):
        if self.star_tag:
            return True
        return etag in self._strong

    def contains_raw(self, etag):
        etag, weak = unquote_etag(etag)
        if weak:
            return self.contains_weak(etag)
        return self.contains(etag)

    def to_header(self):
        if self.star_tag:
            return '*'
        return ', '.join([ '"%s"' % x for x in self._strong ] + [ 'w/"%s"' % x for x in self._weak ])

    def __call__(self, etag = None, data = None, include_weak = False):
        if [etag, data].count(None) != 1:
            raise TypeError('either tag or data required, but at least one')
        if etag is None:
            etag = generate_etag(data)
        if include_weak:
            if etag in self._weak:
                return True
        return etag in self._strong

    def __nonzero__(self):
        return bool(self.star_tag or self._strong)

    def __str__(self):
        return self.to_header()

    def __iter__(self):
        return iter(self._strong)

    def __contains__(self, etag):
        return self.contains(etag)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, str(self))


class Authorization(ImmutableDictMixin, dict):

    def __init__(self, auth_type, data = None):
        dict.__init__(self, data or {})
        self.type = auth_type

    username = property(lambda x: x.get('username'), doc='\n        The username transmitted.  This is set for both basic and digest\n        auth all the time.')
    password = property(lambda x: x.get('password'), doc='\n        When the authentication type is basic this is the password\n        transmitted by the client, else `None`.')
    realm = property(lambda x: x.get('realm'), doc='\n        This is the server realm sent back for HTTP digest auth.')
    nonce = property(lambda x: x.get('nonce'), doc='\n        The nonce the server sent for digest auth, sent back by the client.\n        A nonce should be unique for every 401 response for HTTP digest\n        auth.')
    uri = property(lambda x: x.get('uri'), doc='\n        The URI from Request-URI of the Request-Line; duplicated because\n        proxies are allowed to change the Request-Line in transit.  HTTP\n        digest auth only.')
    nc = property(lambda x: x.get('nc'), doc='\n        The nonce count value transmitted by clients if a qop-header is\n        also transmitted.  HTTP digest auth only.')
    cnonce = property(lambda x: x.get('cnonce'), doc='\n        If the server sent a qop-header in the ``WWW-Authenticate``\n        header, the client has to provide this value for HTTP digest auth.\n        See the RFC for more details.')
    response = property(lambda x: x.get('response'), doc='\n        A string of 32 hex digits computed as defined in RFC 2617, which\n        proves that the user knows a password.  Digest auth only.')
    opaque = property(lambda x: x.get('opaque'), doc='\n        The opaque header from the server returned unchanged by the client.\n        It is recommended that this string be base64 or hexadecimal data.\n        Digest auth only.')

    @property
    def qop(self):

        def on_update(header_set):
            if not header_set and 'qop' in self:
                del self['qop']
            elif header_set:
                self['qop'] = header_set.to_header()

        return parse_set_header(self.get('qop'), on_update)


class WWWAuthenticate(UpdateDictMixin, dict):
    _require_quoting = frozenset(['domain',
     'nonce',
     'opaque',
     'realm'])

    def __init__(self, auth_type = None, values = None, on_update = None):
        dict.__init__(self, values or ())
        if auth_type:
            self['__auth_type__'] = auth_type
        self.on_update = on_update

    def set_basic(self, realm = 'authentication required'):
        dict.clear(self)
        dict.update(self, {'__auth_type__': 'basic',
         'realm': realm})
        if self.on_update:
            self.on_update(self)

    def set_digest(self, realm, nonce, qop = ('auth',), opaque = None, algorithm = None, stale = False):
        d = {'__auth_type__': 'digest',
         'realm': realm,
         'nonce': nonce,
         'qop': dump_header(qop)}
        if stale:
            d['stale'] = 'TRUE'
        if opaque is not None:
            d['opaque'] = opaque
        if algorithm is not None:
            d['algorithm'] = algorithm
        dict.clear(self)
        dict.update(self, d)
        if self.on_update:
            self.on_update(self)

    def to_header(self):
        d = dict(self)
        auth_type = d.pop('__auth_type__', None) or 'basic'
        return '%s %s' % (auth_type.title(), ', '.join([ '%s=%s' % (key, quote_header_value(value, allow_token=key not in self._require_quoting)) for key, value in d.iteritems() ]))

    def __str__(self):
        return self.to_header()

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.to_header())

    def auth_property(name, doc = None):

        def _set_value(self, value):
            if value is None:
                self.pop(name, None)
            else:
                self[name] = str(value)

        return property(lambda x: x.get(name), _set_value, doc=doc)

    def _set_property(name, doc = None):

        def fget(self):

            def on_update(header_set):
                if not header_set and name in self:
                    del self[name]
                elif header_set:
                    self[name] = header_set.to_header()

            return parse_set_header(self.get(name), on_update)

        return property(fget, doc=doc)

    type = auth_property('__auth_type__', doc='\n        The type of the auth mechanism.  HTTP currently specifies\n        `Basic` and `Digest`.')
    realm = auth_property('realm', doc='\n        A string to be displayed to users so they know which username and\n        password to use.  This string should contain at least the name of\n        the host performing the authentication and might additionally\n        indicate the collection of users who might have access.')
    domain = _set_property('domain', doc='\n        A list of URIs that define the protection space.  If a URI is an\n        absolute path, it is relative to the canonical root URL of the\n        server being accessed.')
    nonce = auth_property('nonce', doc='\n        A server-specified data string which should be uniquely generated\n        each time a 401 response is made.  It is recommended that this\n        string be base64 or hexadecimal data.')
    opaque = auth_property('opaque', doc='\n        A string of data, specified by the server, which should be returned\n        by the client unchanged in the Authorization header of subsequent\n        requests with URIs in the same protection space.  It is recommended\n        that this string be base64 or hexadecimal data.')
    algorithm = auth_property('algorithm', doc='\n        A string indicating a pair of algorithms used to produce the digest\n        and a checksum.  If this is not present it is assumed to be "MD5".\n        If the algorithm is not understood, the challenge should be ignored\n        (and a different one used, if there is more than one).')
    qop = _set_property('qop', doc='\n        A set of quality-of-privacy directives such as auth and auth-int.')

    def _get_stale(self):
        val = self.get('stale')
        if val is not None:
            return val.lower() == 'true'

    def _set_stale(self, value):
        if value is None:
            self.pop('stale', None)
        else:
            self['stale'] = value and 'TRUE' or 'FALSE'

    stale = property(_get_stale, _set_stale, doc='\n        A flag, indicating that the previous request from the client was\n        rejected because the nonce value was stale.')
    del _get_stale
    del _set_stale
    auth_property = staticmethod(auth_property)
    del _set_property


class FileStorage(object):

    def __init__(self, stream = None, filename = None, name = None, content_type = 'application/octet-stream', content_length = -1, headers = None):
        self.name = name
        self.stream = stream or _empty_stream
        self.filename = filename or getattr(stream, 'name', None)
        self.content_type = content_type
        self.content_length = content_length
        if headers is None:
            headers = Headers()
        self.headers = headers

    def save(self, dst, buffer_size = 16384):
        from shutil import copyfileobj
        close_dst = False
        if isinstance(dst, basestring):
            dst = file(dst, 'wb')
            close_dst = True
        try:
            copyfileobj(self.stream, dst, buffer_size)
        finally:
            if close_dst:
                dst.close()

    def close(self):
        try:
            self.stream.close()
        except:
            pass

    def __nonzero__(self):
        return bool(self.filename)

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def __iter__(self):
        return iter(self.readline, '')

    def __repr__(self):
        return '<%s: %r (%r)>' % (self.__class__.__name__, self.filename, self.content_type)


from werkzeug.http import dump_options_header, dump_header, generate_etag, quote_header_value, parse_set_header, unquote_etag
from werkzeug.exceptions import BadRequest
for _cls in (MultiDict,
 OrderedMultiDict,
 CombinedMultiDict,
 Headers,
 EnvironHeaders):
    _cls.KeyError = BadRequest.wrap(KeyError, _cls.__name__ + '.KeyError')

del _cls