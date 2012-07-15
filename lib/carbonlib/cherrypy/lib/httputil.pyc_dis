#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\lib\httputil.py
from binascii import b2a_base64
from cherrypy._cpcompat import BaseHTTPRequestHandler, HTTPDate, ntob, ntou, reversed, sorted
from cherrypy._cpcompat import basestring, iteritems, unicodestr, unquote_qs
response_codes = BaseHTTPRequestHandler.responses.copy()
response_codes[500] = ('Internal Server Error', 'The server encountered an unexpected condition which prevented it from fulfilling the request.')
response_codes[503] = ('Service Unavailable', 'The server is currently unable to handle the request due to a temporary overloading or maintenance of the server.')
import re
import urllib

def urljoin(*atoms):
    url = '/'.join([ x for x in atoms if x ])
    while '//' in url:
        url = url.replace('//', '/')

    return url or '/'


def protocol_from_http(protocol_str):
    return (int(protocol_str[5]), int(protocol_str[7]))


def get_ranges(headervalue, content_length):
    if not headervalue:
        return None
    result = []
    bytesunit, byteranges = headervalue.split('=', 1)
    for brange in byteranges.split(','):
        start, stop = [ x.strip() for x in brange.split('-', 1) ]
        if start:
            if not stop:
                stop = content_length - 1
            start, stop = int(start), int(stop)
            if start >= content_length:
                continue
            if stop < start:
                return None
            result.append((start, stop + 1))
        else:
            if not stop:
                return None
            result.append((content_length - int(stop), content_length))

    return result


class HeaderElement(object):

    def __init__(self, value, params = None):
        self.value = value
        if params is None:
            params = {}
        self.params = params

    def __cmp__(self, other):
        return cmp(self.value, other.value)

    def __str__(self):
        p = [ ';%s=%s' % (k, v) for k, v in iteritems(self.params) ]
        return '%s%s' % (self.value, ''.join(p))

    def __unicode__(self):
        return ntou(self.__str__())

    def parse(elementstr):
        atoms = [ x.strip() for x in elementstr.split(';') if x.strip() ]
        if not atoms:
            initial_value = ''
        else:
            initial_value = atoms.pop(0).strip()
        params = {}
        for atom in atoms:
            atom = [ x.strip() for x in atom.split('=', 1) if x.strip() ]
            key = atom.pop(0)
            if atom:
                val = atom[0]
            else:
                val = ''
            params[key] = val

        return (initial_value, params)

    parse = staticmethod(parse)

    def from_str(cls, elementstr):
        ival, params = cls.parse(elementstr)
        return cls(ival, params)

    from_str = classmethod(from_str)


q_separator = re.compile('; *q *=')

class AcceptElement(HeaderElement):

    def from_str(cls, elementstr):
        qvalue = None
        atoms = q_separator.split(elementstr, 1)
        media_range = atoms.pop(0).strip()
        if atoms:
            qvalue = HeaderElement.from_str(atoms[0].strip())
        media_type, params = cls.parse(media_range)
        if qvalue is not None:
            params['q'] = qvalue
        return cls(media_type, params)

    from_str = classmethod(from_str)

    def qvalue(self):
        val = self.params.get('q', '1')
        if isinstance(val, HeaderElement):
            val = val.value
        return float(val)

    qvalue = property(qvalue, doc='The qvalue, or priority, of this value.')

    def __cmp__(self, other):
        diff = cmp(self.qvalue, other.qvalue)
        if diff == 0:
            diff = cmp(str(self), str(other))
        return diff


def header_elements(fieldname, fieldvalue):
    if not fieldvalue:
        return []
    result = []
    for element in fieldvalue.split(','):
        if fieldname.startswith('Accept') or fieldname == 'TE':
            hv = AcceptElement.from_str(element)
        else:
            hv = HeaderElement.from_str(element)
        result.append(hv)

    return list(reversed(sorted(result)))


def decode_TEXT(value):
    from email.Header import decode_header
    atoms = decode_header(value)
    decodedvalue = ''
    for atom, charset in atoms:
        if charset is not None:
            atom = atom.decode(charset)
        decodedvalue += atom

    return decodedvalue


def valid_status(status):
    if not status:
        status = 200
    status = str(status)
    parts = status.split(' ', 1)
    if len(parts) == 1:
        code, = parts
        reason = None
    else:
        code, reason = parts
        reason = reason.strip()
    try:
        code = int(code)
    except ValueError:
        raise ValueError('Illegal response status from server (%s is non-numeric).' % repr(code))

    if code < 100 or code > 599:
        raise ValueError('Illegal response status from server (%s is out of range).' % repr(code))
    if code not in response_codes:
        default_reason, message = ('', '')
    else:
        default_reason, message = response_codes[code]
    if reason is None:
        reason = default_reason
    return (code, reason, message)


def _parse_qs(qs, keep_blank_values = 0, strict_parsing = 0, encoding = 'utf-8'):
    pairs = [ s2 for s1 in qs.split('&') for s2 in s1.split(';') ]
    d = {}
    for name_value in pairs:
        if not name_value and not strict_parsing:
            continue
        nv = name_value.split('=', 1)
        if len(nv) != 2:
            if strict_parsing:
                raise ValueError('bad query field: %r' % (name_value,))
            if keep_blank_values:
                nv.append('')
            else:
                continue
        if len(nv[1]) or keep_blank_values:
            name = unquote_qs(nv[0], encoding)
            value = unquote_qs(nv[1], encoding)
            if name in d:
                if not isinstance(d[name], list):
                    d[name] = [d[name]]
                d[name].append(value)
            else:
                d[name] = value

    return d


image_map_pattern = re.compile('[0-9]+,[0-9]+')

def parse_query_string(query_string, keep_blank_values = True, encoding = 'utf-8'):
    if image_map_pattern.match(query_string):
        pm = query_string.split(',')
        pm = {'x': int(pm[0]),
         'y': int(pm[1])}
    else:
        pm = _parse_qs(query_string, keep_blank_values, encoding=encoding)
    return pm


class CaseInsensitiveDict(dict):

    def __getitem__(self, key):
        return dict.__getitem__(self, str(key).title())

    def __setitem__(self, key, value):
        dict.__setitem__(self, str(key).title(), value)

    def __delitem__(self, key):
        dict.__delitem__(self, str(key).title())

    def __contains__(self, key):
        return dict.__contains__(self, str(key).title())

    def get(self, key, default = None):
        return dict.get(self, str(key).title(), default)

    def has_key(self, key):
        return dict.has_key(self, str(key).title())

    def update(self, E):
        for k in E.keys():
            self[str(k).title()] = E[k]

    def fromkeys(cls, seq, value = None):
        newdict = cls()
        for k in seq:
            newdict[str(k).title()] = value

        return newdict

    fromkeys = classmethod(fromkeys)

    def setdefault(self, key, x = None):
        key = str(key).title()
        try:
            return self[key]
        except KeyError:
            self[key] = x
            return x

    def pop(self, key, default):
        return dict.pop(self, str(key).title(), default)


header_translate_table = ''.join([ chr(i) for i in xrange(256) ])
header_translate_deletechars = ''.join([ chr(i) for i in xrange(32) ]) + chr(127)

class HeaderMap(CaseInsensitiveDict):
    protocol = (1, 1)
    encodings = ['ISO-8859-1']
    use_rfc_2047 = True

    def elements(self, key):
        key = str(key).title()
        value = self.get(key)
        return header_elements(key, value)

    def values(self, key):
        return [ e.value for e in self.elements(key) ]

    def output(self):
        header_list = []
        for k, v in self.items():
            if isinstance(k, unicodestr):
                k = self.encode(k)
            if not isinstance(v, basestring):
                v = str(v)
            if isinstance(v, unicodestr):
                v = self.encode(v)
            k = k.translate(header_translate_table, header_translate_deletechars)
            v = v.translate(header_translate_table, header_translate_deletechars)
            header_list.append((k, v))

        return header_list

    def encode(self, v):
        for enc in self.encodings:
            try:
                return v.encode(enc)
            except UnicodeEncodeError:
                continue

        if self.protocol == (1, 1) and self.use_rfc_2047:
            v = b2a_base64(v.encode('utf-8'))
            return ntob('=?utf-8?b?') + v.strip(ntob('\n')) + ntob('?=')
        raise ValueError('Could not encode header part %r using any of the encodings %r.' % (v, self.encodings))


class Host(object):
    ip = '0.0.0.0'
    port = 80
    name = 'unknown.tld'

    def __init__(self, ip, port, name = None):
        self.ip = ip
        self.port = port
        if name is None:
            name = ip
        self.name = name

    def __repr__(self):
        return 'httputil.Host(%r, %r, %r)' % (self.ip, self.port, self.name)