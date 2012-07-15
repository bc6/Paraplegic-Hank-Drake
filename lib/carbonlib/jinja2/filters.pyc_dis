#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\filters.py
import re
import math
from random import choice
from operator import itemgetter
from itertools import imap, groupby
from jinja2.utils import Markup, escape, pformat, urlize, soft_unicode, unicode_urlencode
from jinja2.runtime import Undefined
from jinja2.exceptions import FilterArgumentError
_word_re = re.compile('\\w+(?u)')

def contextfilter(f):
    f.contextfilter = True
    return f


def evalcontextfilter(f):
    f.evalcontextfilter = True
    return f


def environmentfilter(f):
    f.environmentfilter = True
    return f


def make_attrgetter(environment, attribute):
    if not isinstance(attribute, basestring) or '.' not in attribute:
        return lambda x: environment.getitem(x, attribute)
    attribute = attribute.split('.')

    def attrgetter(item):
        for part in attribute:
            item = environment.getitem(item, part)

        return item

    return attrgetter


def do_forceescape(value):
    if hasattr(value, '__html__'):
        value = value.__html__()
    return escape(unicode(value))


def do_urlencode(value):
    itemiter = None
    if isinstance(value, dict):
        itemiter = value.iteritems()
    elif not isinstance(value, basestring):
        try:
            itemiter = iter(value)
        except TypeError:
            pass

    if itemiter is None:
        return unicode_urlencode(value)
    return u'&'.join((unicode_urlencode(k) + '=' + unicode_urlencode(v) for k, v in itemiter))


@evalcontextfilter
def do_replace(eval_ctx, s, old, new, count = None):
    if count is None:
        count = -1
    if not eval_ctx.autoescape:
        return unicode(s).replace(unicode(old), unicode(new), count)
    if hasattr(old, '__html__') or hasattr(new, '__html__') and not hasattr(s, '__html__'):
        s = escape(s)
    else:
        s = soft_unicode(s)
    return s.replace(soft_unicode(old), soft_unicode(new), count)


def do_upper(s):
    return soft_unicode(s).upper()


def do_lower(s):
    return soft_unicode(s).lower()


@evalcontextfilter
def do_xmlattr(_eval_ctx, d, autospace = True):
    rv = u' '.join((u'%s="%s"' % (escape(key), escape(value)) for key, value in d.iteritems() if value is not None and not isinstance(value, Undefined)))
    if autospace and rv:
        rv = u' ' + rv
    if _eval_ctx.autoescape:
        rv = Markup(rv)
    return rv


def do_capitalize(s):
    return soft_unicode(s).capitalize()


def do_title(s):
    return soft_unicode(s).title()


def do_dictsort(value, case_sensitive = False, by = 'key'):
    if by == 'key':
        pos = 0
    elif by == 'value':
        pos = 1
    else:
        raise FilterArgumentError('You can only sort by either "key" or "value"')

    def sort_func(item):
        value = item[pos]
        if isinstance(value, basestring) and not case_sensitive:
            value = value.lower()
        return value

    return sorted(value.items(), key=sort_func)


@environmentfilter
def do_sort(environment, value, reverse = False, case_sensitive = False, attribute = None):
    if not case_sensitive:

        def sort_func(item):
            if isinstance(item, basestring):
                item = item.lower()
            return item

    else:
        sort_func = None
    if attribute is not None:
        getter = make_attrgetter(environment, attribute)

        def sort_func(item, processor = sort_func or (lambda x: x)):
            return processor(getter(item))

    return sorted(value, key=sort_func, reverse=reverse)


def do_default(value, default_value = u'', boolean = False):
    if boolean and not value or isinstance(value, Undefined):
        return default_value
    return value


@evalcontextfilter
def do_join(eval_ctx, value, d = u'', attribute = None):
    if attribute is not None:
        value = imap(make_attrgetter(eval_ctx.environment, attribute), value)
    if not eval_ctx.autoescape:
        return unicode(d).join(imap(unicode, value))
    if not hasattr(d, '__html__'):
        value = list(value)
        do_escape = False
        for idx, item in enumerate(value):
            if hasattr(item, '__html__'):
                do_escape = True
            else:
                value[idx] = unicode(item)

        if do_escape:
            d = escape(d)
        else:
            d = unicode(d)
        return d.join(value)
    return soft_unicode(d).join(imap(soft_unicode, value))


def do_center(value, width = 80):
    return unicode(value).center(width)


@environmentfilter
def do_first(environment, seq):
    try:
        return iter(seq).next()
    except StopIteration:
        return environment.undefined('No first item, sequence was empty.')


@environmentfilter
def do_last(environment, seq):
    try:
        return iter(reversed(seq)).next()
    except StopIteration:
        return environment.undefined('No last item, sequence was empty.')


@environmentfilter
def do_random(environment, seq):
    try:
        return choice(seq)
    except IndexError:
        return environment.undefined('No random item, sequence was empty.')


def do_filesizeformat(value, binary = False):
    bytes = float(value)
    base = binary and 1024 or 1000
    prefixes = [binary and 'KiB' or 'kB',
     binary and 'MiB' or 'MB',
     binary and 'GiB' or 'GB',
     binary and 'TiB' or 'TB',
     binary and 'PiB' or 'PB',
     binary and 'EiB' or 'EB',
     binary and 'ZiB' or 'ZB',
     binary and 'YiB' or 'YB']
    if bytes == 1:
        return '1 Byte'
    elif bytes < base:
        return '%d Bytes' % bytes
    else:
        for i, prefix in enumerate(prefixes):
            unit = base ** (i + 2)
            if bytes < unit:
                return '%.1f %s' % (base * bytes / unit, prefix)

        return '%.1f %s' % (base * bytes / unit, prefix)


def do_pprint(value, verbose = False):
    return pformat(value, verbose=verbose)


@evalcontextfilter
def do_urlize(eval_ctx, value, trim_url_limit = None, nofollow = False):
    rv = urlize(value, trim_url_limit, nofollow)
    if eval_ctx.autoescape:
        rv = Markup(rv)
    return rv


def do_indent(s, width = 4, indentfirst = False):
    indention = u' ' * width
    rv = (u'\n' + indention).join(s.splitlines())
    if indentfirst:
        rv = indention + rv
    return rv


def do_truncate(s, length = 255, killwords = False, end = '...'):
    if len(s) <= length:
        return s
    if killwords:
        return s[:length] + end
    words = s.split(' ')
    result = []
    m = 0
    for word in words:
        m += len(word) + 1
        if m > length:
            break
        result.append(word)

    result.append(end)
    return u' '.join(result)


@environmentfilter
def do_wordwrap(environment, s, width = 79, break_long_words = True):
    import textwrap
    return environment.newline_sequence.join(textwrap.wrap(s, width=width, expand_tabs=False, replace_whitespace=False, break_long_words=break_long_words))


def do_wordcount(s):
    return len(_word_re.findall(s))


def do_int(value, default = 0):
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default


def do_float(value, default = 0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def do_format(value, *args, **kwargs):
    if args and kwargs:
        raise FilterArgumentError("can't handle positional and keyword arguments at the same time")
    return soft_unicode(value) % (kwargs or args)


def do_trim(value):
    return soft_unicode(value).strip()


def do_striptags(value):
    if hasattr(value, '__html__'):
        value = value.__html__()
    return Markup(unicode(value)).striptags()


def do_slice(value, slices, fill_with = None):
    seq = list(value)
    length = len(seq)
    items_per_slice = length // slices
    slices_with_extra = length % slices
    offset = 0
    for slice_number in xrange(slices):
        start = offset + slice_number * items_per_slice
        if slice_number < slices_with_extra:
            offset += 1
        end = offset + (slice_number + 1) * items_per_slice
        tmp = seq[start:end]
        if fill_with is not None and slice_number >= slices_with_extra:
            tmp.append(fill_with)
        yield tmp


def do_batch(value, linecount, fill_with = None):
    result = []
    tmp = []
    for item in value:
        if len(tmp) == linecount:
            yield tmp
            tmp = []
        tmp.append(item)

    if tmp:
        if fill_with is not None and len(tmp) < linecount:
            tmp += [fill_with] * (linecount - len(tmp))
        yield tmp


def do_round(value, precision = 0, method = 'common'):
    if method not in ('common', 'ceil', 'floor'):
        raise FilterArgumentError('method must be common, ceil or floor')
    if method == 'common':
        return round(value, precision)
    func = getattr(math, method)
    return func(value * 10 ** precision) / 10 ** precision


@environmentfilter
def do_groupby(environment, value, attribute):
    expr = make_attrgetter(environment, attribute)
    return sorted(map(_GroupTuple, groupby(sorted(value, key=expr), expr)))


class _GroupTuple(tuple):
    __slots__ = ()
    grouper = property(itemgetter(0))
    list = property(itemgetter(1))

    def __new__(cls, (key, value)):
        return tuple.__new__(cls, (key, list(value)))


@environmentfilter
def do_sum(environment, iterable, attribute = None, start = 0):
    if attribute is not None:
        iterable = imap(make_attrgetter(environment, attribute), iterable)
    return sum(iterable, start)


def do_list(value):
    return list(value)


def do_mark_safe(value):
    return Markup(value)


def do_mark_unsafe(value):
    return unicode(value)


def do_reverse(value):
    if isinstance(value, basestring):
        return value[::-1]
    try:
        return reversed(value)
    except TypeError:
        try:
            rv = list(value)
            rv.reverse()
            return rv
        except TypeError:
            raise FilterArgumentError('argument must be iterable')


@environmentfilter
def do_attr(environment, obj, name):
    try:
        name = str(name)
    except UnicodeError:
        pass
    else:
        try:
            value = getattr(obj, name)
        except AttributeError:
            pass
        else:
            if environment.sandboxed and not environment.is_safe_attribute(obj, name, value):
                return environment.unsafe_undefined(obj, name)
            return value

    return environment.undefined(obj=obj, name=name)


FILTERS = {'attr': do_attr,
 'replace': do_replace,
 'upper': do_upper,
 'lower': do_lower,
 'escape': escape,
 'e': escape,
 'forceescape': do_forceescape,
 'capitalize': do_capitalize,
 'title': do_title,
 'default': do_default,
 'd': do_default,
 'join': do_join,
 'count': len,
 'dictsort': do_dictsort,
 'sort': do_sort,
 'length': len,
 'reverse': do_reverse,
 'center': do_center,
 'indent': do_indent,
 'title': do_title,
 'capitalize': do_capitalize,
 'first': do_first,
 'last': do_last,
 'random': do_random,
 'filesizeformat': do_filesizeformat,
 'pprint': do_pprint,
 'truncate': do_truncate,
 'wordwrap': do_wordwrap,
 'wordcount': do_wordcount,
 'int': do_int,
 'float': do_float,
 'string': soft_unicode,
 'list': do_list,
 'urlize': do_urlize,
 'format': do_format,
 'trim': do_trim,
 'striptags': do_striptags,
 'slice': do_slice,
 'batch': do_batch,
 'sum': do_sum,
 'abs': abs,
 'round': do_round,
 'groupby': do_groupby,
 'safe': do_mark_safe,
 'xmlattr': do_xmlattr,
 'urlencode': do_urlencode}