import re
import sys
import struct
from json.scanner import make_scanner
try:
    from _json import scanstring as c_scanstring
except ImportError:
    c_scanstring = None
__all__ = ['JSONDecoder']
FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL

def _floatconstants():
    _BYTES = '7FF80000000000007FF0000000000000'.decode('hex')
    if sys.byteorder != 'big':
        _BYTES = _BYTES[:8][None] + _BYTES[8:][None]
    (nan, inf,) = struct.unpack('dd', _BYTES)
    return (nan, inf, -inf)


(NaN, PosInf, NegInf,) = _floatconstants()

def linecol(doc, pos):
    lineno = doc.count('\n', 0, pos) + 1
    if lineno == 1:
        colno = pos
    else:
        colno = pos - doc.rindex('\n', 0, pos)
    return (lineno, colno)



def errmsg(msg, doc, pos, end = None):
    (lineno, colno,) = linecol(doc, pos)
    if end is None:
        fmt = '{0}: line {1} column {2} (char {3})'
        return fmt.format(msg, lineno, colno, pos)
    (endlineno, endcolno,) = linecol(doc, end)
    fmt = '{0}: line {1} column {2} - line {3} column {4} (char {5} - {6})'
    return fmt.format(msg, lineno, colno, endlineno, endcolno, pos, end)


_CONSTANTS = {'-Infinity': NegInf,
 'Infinity': PosInf,
 'NaN': NaN}
STRINGCHUNK = re.compile('(.*?)(["\\\\\\x00-\\x1f])', FLAGS)
BACKSLASH = {'"': u'"',
 '\\': u'\\',
 '/': u'/',
 'b': u'\x08',
 'f': u'\x0c',
 'n': u'\n',
 'r': u'\r',
 't': u'\t'}
DEFAULT_ENCODING = 'utf-8'

def py_scanstring(s, end, encoding = None, strict = True, _b = BACKSLASH, _m = STRINGCHUNK.match):
    if encoding is None:
        encoding = DEFAULT_ENCODING
    chunks = []
    _append = chunks.append
    begin = end - 1
    while 1:
        chunk = _m(s, end)
        if chunk is None:
            raise ValueError(errmsg('Unterminated string starting at', s, begin))
        end = chunk.end()
        (content, terminator,) = chunk.groups()
        if content:
            if not isinstance(content, unicode):
                content = unicode(content, encoding)
            _append(content)
        if terminator == '"':
            break
        elif terminator != '\\':
            if strict:
                msg = 'Invalid control character {0!r} at'.format(terminator)
                raise ValueError(errmsg(msg, s, end))
            else:
                _append(terminator)
            continue
        try:
            esc = s[end]
        except IndexError:
            raise ValueError(errmsg('Unterminated string starting at', s, begin))
        if esc != 'u':
            try:
                char = _b[esc]
            except KeyError:
                msg = 'Invalid \\escape: ' + repr(esc)
                raise ValueError(errmsg(msg, s, end))
            end += 1
        else:
            esc = s[(end + 1):(end + 5)]
            next_end = end + 5
            if len(esc) != 4:
                msg = 'Invalid \\uXXXX escape'
                raise ValueError(errmsg(msg, s, end))
            uni = int(esc, 16)
            if 55296 <= uni <= 56319 and sys.maxunicode > 65535:
                msg = 'Invalid \\uXXXX\\uXXXX surrogate pair'
                if not s[(end + 5):(end + 7)] == '\\u':
                    raise ValueError(errmsg(msg, s, end))
                esc2 = s[(end + 7):(end + 11)]
                if len(esc2) != 4:
                    raise ValueError(errmsg(msg, s, end))
                uni2 = int(esc2, 16)
                uni = 65536 + (uni - 55296 << 10 | uni2 - 56320)
                next_end += 6
            char = unichr(uni)
            end = next_end
        _append(char)

    return (u''.join(chunks), end)


scanstring = c_scanstring or py_scanstring
WHITESPACE = re.compile('[ \\t\\n\\r]*', FLAGS)
WHITESPACE_STR = ' \t\n\r'

def JSONObject(s_and_end, encoding, strict, scan_once, object_hook, object_pairs_hook, _w = WHITESPACE.match, _ws = WHITESPACE_STR):
    (s, end,) = s_and_end
    pairs = []
    pairs_append = pairs.append
    nextchar = s[end:(end + 1)]
    if nextchar != '"':
        if nextchar in _ws:
            end = _w(s, end).end()
            nextchar = s[end:(end + 1)]
        if nextchar == '}':
            return (pairs, end + 1)
        if nextchar != '"':
            raise ValueError(errmsg('Expecting property name', s, end))
    end += 1
    while True:
        (key, end,) = scanstring(s, end, encoding, strict)
        if s[end:(end + 1)] != ':':
            end = _w(s, end).end()
            if s[end:(end + 1)] != ':':
                raise ValueError(errmsg('Expecting : delimiter', s, end))
        end += 1
        try:
            if s[end] in _ws:
                end += 1
                if s[end] in _ws:
                    end = _w(s, end + 1).end()
        except IndexError:
            pass
        try:
            (value, end,) = scan_once(s, end)
        except StopIteration:
            raise ValueError(errmsg('Expecting object', s, end))
        pairs_append((key, value))
        try:
            nextchar = s[end]
            if nextchar in _ws:
                end = _w(s, end + 1).end()
                nextchar = s[end]
        except IndexError:
            nextchar = ''
        end += 1
        if nextchar == '}':
            break
        elif nextchar != ',':
            raise ValueError(errmsg('Expecting , delimiter', s, end - 1))
        try:
            nextchar = s[end]
            if nextchar in _ws:
                end += 1
                nextchar = s[end]
                if nextchar in _ws:
                    end = _w(s, end + 1).end()
                    nextchar = s[end]
        except IndexError:
            nextchar = ''
        end += 1
        if nextchar != '"':
            raise ValueError(errmsg('Expecting property name', s, end - 1))

    if object_pairs_hook is not None:
        result = object_pairs_hook(pairs)
        return (result, end)
    pairs = dict(pairs)
    if object_hook is not None:
        pairs = object_hook(pairs)
    return (pairs, end)



def JSONArray(s_and_end, scan_once, _w = WHITESPACE.match, _ws = WHITESPACE_STR):
    (s, end,) = s_and_end
    values = []
    nextchar = s[end:(end + 1)]
    if nextchar in _ws:
        end = _w(s, end + 1).end()
        nextchar = s[end:(end + 1)]
    if nextchar == ']':
        return (values, end + 1)
    _append = values.append
    while True:
        try:
            (value, end,) = scan_once(s, end)
        except StopIteration:
            raise ValueError(errmsg('Expecting object', s, end))
        _append(value)
        nextchar = s[end:(end + 1)]
        if nextchar in _ws:
            end = _w(s, end + 1).end()
            nextchar = s[end:(end + 1)]
        end += 1
        if nextchar == ']':
            break
        elif nextchar != ',':
            raise ValueError(errmsg('Expecting , delimiter', s, end))
        try:
            if s[end] in _ws:
                end += 1
                if s[end] in _ws:
                    end = _w(s, end + 1).end()
        except IndexError:
            pass

    return (values, end)



class JSONDecoder(object):

    def __init__(self, encoding = None, object_hook = None, parse_float = None, parse_int = None, parse_constant = None, strict = True, object_pairs_hook = None):
        self.encoding = encoding
        self.object_hook = object_hook
        self.object_pairs_hook = object_pairs_hook
        self.parse_float = parse_float or float
        self.parse_int = parse_int or int
        self.parse_constant = parse_constant or _CONSTANTS.__getitem__
        self.strict = strict
        self.parse_object = JSONObject
        self.parse_array = JSONArray
        self.parse_string = scanstring
        self.scan_once = make_scanner(self)



    def decode(self, s, _w = WHITESPACE.match):
        (obj, end,) = self.raw_decode(s, idx=_w(s, 0).end())
        end = _w(s, end).end()
        if end != len(s):
            raise ValueError(errmsg('Extra data', s, end, len(s)))
        return obj



    def raw_decode(self, s, idx = 0):
        try:
            (obj, end,) = self.scan_once(s, idx)
        except StopIteration:
            raise ValueError('No JSON object could be decoded')
        return (obj, end)




