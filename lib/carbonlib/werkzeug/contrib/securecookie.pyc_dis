#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\contrib\securecookie.py
import sys
import cPickle as pickle
from hmac import new as hmac
from datetime import datetime
from time import time, mktime, gmtime
from werkzeug import url_quote_plus, url_unquote_plus
from werkzeug._internal import _date_to_unix
from werkzeug.contrib.sessions import ModificationTrackingDict
_default_hash = None
if sys.version_info >= (2, 5):
    try:
        from hashlib import sha1 as _default_hash
    except ImportError:
        pass

if _default_hash is None:
    import sha as _default_hash

class UnquoteError(Exception):
    pass


class SecureCookie(ModificationTrackingDict):
    hash_method = _default_hash
    serialization_method = pickle
    quote_base64 = True

    def __init__(self, data = None, secret_key = None, new = True):
        ModificationTrackingDict.__init__(self, data or ())
        if secret_key is not None:
            secret_key = str(secret_key)
        self.secret_key = secret_key
        self.new = new

    def __repr__(self):
        return '<%s %s%s>' % (self.__class__.__name__, dict.__repr__(self), self.should_save and '*' or '')

    @property
    def should_save(self):
        return self.modified

    @classmethod
    def quote(cls, value):
        if cls.serialization_method is not None:
            value = cls.serialization_method.dumps(value)
        if cls.quote_base64:
            value = ''.join(value.encode('base64').splitlines()).strip()
        return value

    @classmethod
    def unquote(cls, value):
        try:
            if cls.quote_base64:
                value = value.decode('base64')
            if cls.serialization_method is not None:
                value = cls.serialization_method.loads(value)
            return value
        except:
            raise UnquoteError()

    def serialize(self, expires = None):
        if self.secret_key is None:
            raise RuntimeError('no secret key defined')
        if expires:
            self['_expires'] = _date_to_unix(expires)
        result = []
        mac = hmac(self.secret_key, None, self.hash_method)
        for key, value in sorted(self.items()):
            result.append('%s=%s' % (url_quote_plus(key), self.quote(value)))
            mac.update('|' + result[-1])

        return '%s?%s' % (mac.digest().encode('base64').strip(), '&'.join(result))

    @classmethod
    def unserialize(cls, string, secret_key):
        if isinstance(string, unicode):
            string = string.encode('utf-8', 'ignore')
        try:
            base64_hash, data = string.split('?', 1)
        except (ValueError, IndexError):
            items = ()
        else:
            items = {}
            mac = hmac(secret_key, None, cls.hash_method)
            for item in data.split('&'):
                mac.update('|' + item)
                if '=' not in item:
                    items = None
                    break
                key, value = item.split('=', 1)
                key = url_unquote_plus(key)
                try:
                    key = str(key)
                except UnicodeError:
                    pass

                items[key] = value

            try:
                client_hash = base64_hash.decode('base64')
            except Exception:
                items = client_hash = None

            if items is not None and client_hash == mac.digest():
                try:
                    for key, value in items.iteritems():
                        items[key] = cls.unquote(value)

                except UnquoteError:
                    items = ()
                else:
                    if '_expires' in items:
                        if time() > items['_expires']:
                            items = ()
                        else:
                            del items['_expires']
            else:
                items = ()

        return cls(items, secret_key, False)

    @classmethod
    def load_cookie(cls, request, key = 'session', secret_key = None):
        data = request.cookies.get(key)
        if not data:
            return cls(secret_key=secret_key)
        return cls.unserialize(data, secret_key)

    def save_cookie(self, response, key = 'session', expires = None, session_expires = None, max_age = None, path = '/', domain = None, secure = None, httponly = False, force = False):
        if force or self.should_save:
            data = self.serialize(session_expires or expires)
            response.set_cookie(key, data, expires=expires, max_age=max_age, path=path, domain=domain, secure=secure, httponly=httponly)