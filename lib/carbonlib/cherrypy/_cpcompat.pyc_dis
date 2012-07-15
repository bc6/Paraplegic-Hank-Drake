#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\_cpcompat.py
import os
import sys
if sys.version_info >= (3, 0):
    bytestr = bytes
    unicodestr = str
    nativestr = unicodestr
    basestring = (bytes, str)

    def ntob(n, encoding = 'ISO-8859-1'):
        return n.encode(encoding)


    def ntou(n, encoding = 'ISO-8859-1'):
        return n


    from io import StringIO
    from io import BytesIO
else:
    bytestr = str
    unicodestr = unicode
    nativestr = bytestr
    basestring = basestring

    def ntob(n, encoding = 'ISO-8859-1'):
        return n


    def ntou(n, encoding = 'ISO-8859-1'):
        return n.decode(encoding)


    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

    BytesIO = StringIO
try:
    set = set
except NameError:
    from sets import Set as set

try:
    from base64 import decodebytes as _base64_decodebytes
except ImportError:
    from base64 import decodestring as _base64_decodebytes

def base64_decode(n, encoding = 'ISO-8859-1'):
    if isinstance(n, unicodestr):
        b = n.encode(encoding)
    else:
        b = n
    b = _base64_decodebytes(b)
    if nativestr is unicodestr:
        return b.decode(encoding)
    else:
        return b


try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

try:
    from hashlib import sha1 as sha
except ImportError:
    from sha import new as sha

try:
    sorted = sorted
except NameError:

    def sorted(i):
        i = i[:]
        i.sort()
        return i


try:
    reversed = reversed
except NameError:

    def reversed(x):
        i = len(x)
        while i > 0:
            i -= 1
            yield x[i]


try:
    from urllib.parse import urljoin, urlencode
    from urllib.parse import quote, quote_plus
    from urllib.request import unquote, urlopen
    from urllib.request import parse_http_list, parse_keqv_list
except ImportError:
    from urlparse import urljoin
    from urllib import urlencode, urlopen
    from urllib import quote, quote_plus
    from urllib import unquote
    from urllib2 import parse_http_list, parse_keqv_list

try:
    from threading import local as threadlocal
except ImportError:
    from cherrypy._cpthreadinglocal import local as threadlocal

try:
    dict.iteritems
    iteritems = lambda d: d.iteritems()
    copyitems = lambda d: d.items()
except AttributeError:
    iteritems = lambda d: d.items()
    copyitems = lambda d: list(d.items())

try:
    dict.iterkeys
    iterkeys = lambda d: d.iterkeys()
    copykeys = lambda d: d.keys()
except AttributeError:
    iterkeys = lambda d: d.keys()
    copykeys = lambda d: list(d.keys())

try:
    dict.itervalues
    itervalues = lambda d: d.itervalues()
    copyvalues = lambda d: d.values()
except AttributeError:
    itervalues = lambda d: d.values()
    copyvalues = lambda d: list(d.values())

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

try:
    from Cookie import SimpleCookie, CookieError
    from httplib import BadStatusLine, HTTPConnection, IncompleteRead, NotConnected
    from BaseHTTPServer import BaseHTTPRequestHandler
    try:
        from httplib import HTTPSConnection
    except ImportError:
        pass

except ImportError:
    from http.cookies import SimpleCookie, CookieError
    from http.client import BadStatusLine, HTTPConnection, IncompleteRead, NotConnected
    from http.server import BaseHTTPRequestHandler
    try:
        from http.client import HTTPSConnection
    except ImportError:
        pass

try:
    xrange = xrange
except NameError:
    xrange = range

import threading
if hasattr(threading.Thread, 'daemon'):

    def get_daemon(t):
        return t.daemon


    def set_daemon(t, val):
        t.daemon = val


else:

    def get_daemon(t):
        return t.isDaemon()


    def set_daemon(t, val):
        t.setDaemon(val)


try:
    from email.utils import formatdate

    def HTTPDate(timeval = None):
        return formatdate(timeval, usegmt=True)


except ImportError:
    from rfc822 import formatdate as HTTPDate

try:
    from urllib.parse import unquote as parse_unquote

    def unquote_qs(atom, encoding, errors = 'strict'):
        return parse_unquote(atom.replace('+', ' '), encoding=encoding, errors=errors)


except ImportError:
    from urllib import unquote as parse_unquote

    def unquote_qs(atom, encoding, errors = 'strict'):
        return parse_unquote(atom.replace('+', ' ')).decode(encoding, errors)


try:
    import simplejson as json
    json_decode = json.JSONDecoder().decode
    json_encode = json.JSONEncoder().iterencode
except ImportError:
    if sys.version_info >= (3, 0):
        import json
        json_decode = json.JSONDecoder().decode
        _json_encode = json.JSONEncoder().iterencode

        def json_encode(value):
            for chunk in _json_encode(value):
                yield chunk.encode('utf8')


    elif sys.version_info >= (2, 6):
        import json
        json_decode = json.JSONDecoder().decode
        json_encode = json.JSONEncoder().iterencode
    else:
        json = None

        def json_decode(s):
            raise ValueError('No JSON library is available')


        def json_encode(s):
            raise ValueError('No JSON library is available')


try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    os.urandom(20)
    import binascii

    def random20():
        return binascii.hexlify(os.urandom(20)).decode('ascii')


except (AttributeError, NotImplementedError):
    import random

    def random20():
        return sha('%s' % random.random()).hexdigest()


try:
    from _thread import get_ident as get_thread_ident
except ImportError:
    from thread import get_ident as get_thread_ident

try:
    next = next
except NameError:

    def next(i):
        return i.next()