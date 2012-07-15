#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\contrib\sessions.py
import re
import os
import sys
import tempfile
from os import path
from time import time
from random import random
try:
    from hashlib import sha1
except ImportError:
    from sha import new as sha1

from cPickle import dump, load, HIGHEST_PROTOCOL
from werkzeug import ClosingIterator, dump_cookie, parse_cookie, CallbackDict
from werkzeug.posixemulation import rename
_sha1_re = re.compile('^[a-f0-9]{40}$')

def _urandom():
    if hasattr(os, 'urandom'):
        return os.urandom(30)
    return random()


def generate_key(salt = None):
    return sha1('%s%s%s' % (salt, time(), _urandom())).hexdigest()


class ModificationTrackingDict(CallbackDict):
    __slots__ = ('modified',)

    def __init__(self, *args, **kwargs):

        def on_update(self):
            self.modified = True

        self.modified = False
        CallbackDict.__init__(self, on_update=on_update)
        dict.update(self, *args, **kwargs)

    def copy(self):
        missing = object()
        result = object.__new__(self.__class__)
        for name in self.__slots__:
            val = getattr(self, name, missing)
            if val is not missing:
                setattr(result, name, val)

        return result

    def __copy__(self):
        return self.copy()


class Session(ModificationTrackingDict):
    __slots__ = ModificationTrackingDict.__slots__ + ('sid', 'new')

    def __init__(self, data, sid, new = False):
        ModificationTrackingDict.__init__(self, data)
        self.sid = sid
        self.new = new

    def __repr__(self):
        return '<%s %s%s>' % (self.__class__.__name__, dict.__repr__(self), self.should_save and '*' or '')

    @property
    def should_save(self):
        return self.modified


class SessionStore(object):

    def __init__(self, session_class = None):
        if session_class is None:
            session_class = Session
        self.session_class = session_class

    def is_valid_key(self, key):
        return _sha1_re.match(key) is not None

    def generate_key(self, salt = None):
        return generate_key(salt)

    def new(self):
        return self.session_class({}, self.generate_key(), True)

    def save(self, session):
        pass

    def save_if_modified(self, session):
        if session.should_save:
            self.save(session)

    def delete(self, session):
        pass

    def get(self, sid):
        return self.session_class({}, sid, True)


_fs_transaction_suffix = '.__wz_sess'

class FilesystemSessionStore(SessionStore):

    def __init__(self, path = None, filename_template = 'werkzeug_%s.sess', session_class = None, renew_missing = False, mode = 420):
        SessionStore.__init__(self, session_class)
        if path is None:
            path = tempfile.gettempdir()
        self.path = path
        if isinstance(filename_template, unicode):
            filename_template = filename_template.encode(sys.getfilesystemencoding() or 'utf-8')
        self.filename_template = filename_template
        self.renew_missing = renew_missing
        self.mode = mode

    def get_session_filename(self, sid):
        if isinstance(sid, unicode):
            sid = sid.encode(sys.getfilesystemencoding() or 'utf-8')
        return path.join(self.path, self.filename_template % sid)

    def save(self, session):
        fn = self.get_session_filename(session.sid)
        fd, tmp = tempfile.mkstemp(suffix=_fs_transaction_suffix, dir=self.path)
        f = os.fdopen(fd, 'wb')
        try:
            dump(dict(session), f, HIGHEST_PROTOCOL)
        finally:
            f.close()

        try:
            rename(tmp, fn)
            os.chmod(fn, self.mode)
        except (IOError, OSError):
            pass

    def delete(self, session):
        fn = self.get_session_filename(session.sid)
        try:
            os.unlink(fn)
        except OSError:
            pass

    def get(self, sid):
        if not self.is_valid_key(sid):
            return self.new()
        try:
            f = open(self.get_session_filename(sid), 'rb')
        except IOError:
            if self.renew_missing:
                return self.new()
            data = {}
        else:
            try:
                data = load(f)
            except Exception:
                data = {}
            finally:
                f.close()

        return self.session_class(data, sid, False)

    def list(self):
        before, after = self.filename_template.split('%s', 1)
        filename_re = re.compile('%s(.{5,})%s$' % (re.escape(before), re.escape(after)))
        result = []
        for filename in os.listdir(self.path):
            if filename.endswith(_fs_transaction_suffix):
                continue
            match = filename_re.match(filename)
            if match is not None:
                result.append(match.group(1))

        return result


class SessionMiddleware(object):

    def __init__(self, app, store, cookie_name = 'session_id', cookie_age = None, cookie_expires = None, cookie_path = '/', cookie_domain = None, cookie_secure = None, cookie_httponly = False, environ_key = 'werkzeug.session'):
        self.app = app
        self.store = store
        self.cookie_name = cookie_name
        self.cookie_age = cookie_age
        self.cookie_expires = cookie_expires
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.environ_key = environ_key

    def __call__(self, environ, start_response):
        cookie = parse_cookie(environ.get('HTTP_COOKIE', ''))
        sid = cookie.get(self.cookie_name, None)
        if sid is None:
            session = self.store.new()
        else:
            session = self.store.get(sid)
        environ[self.environ_key] = session

        def injecting_start_response(status, headers, exc_info = None):
            if session.should_save:
                self.store.save(session)
                headers.append(('Set-Cookie', dump_cookie(self.cookie_name, session.sid, self.cookie_age, self.cookie_expires, self.cookie_path, self.cookie_domain, self.cookie_secure, self.cookie_httponly)))
            return start_response(status, headers, exc_info)

        return ClosingIterator(self.app(environ, injecting_start_response), lambda : self.store.save_if_modified(session))