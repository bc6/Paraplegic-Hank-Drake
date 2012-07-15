#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\security.py
import hmac
import string
from random import SystemRandom
try:
    from hashlib import sha1, md5
    _hash_funcs = _hash_mods = {'sha1': sha1,
     'md5': md5}
    _sha1_mod = sha1
    _md5_mod = md5
except ImportError:
    import sha as _sha1_mod, md5 as _md5_mod
    _hash_mods = {'sha1': _sha1_mod,
     'md5': _md5_mod}
    _hash_funcs = {'sha1': _sha1_mod.new,
     'md5': _md5_mod.new}

SALT_CHARS = string.letters + string.digits
_sys_rng = SystemRandom()

def gen_salt(length):
    if length <= 0:
        raise ValueError('requested salt of length <= 0')
    return ''.join((_sys_rng.choice(SALT_CHARS) for _ in xrange(length)))


def _hash_internal(method, salt, password):
    if method == 'plain':
        return password
    if salt:
        if method not in _hash_mods:
            return
        if isinstance(salt, unicode):
            salt = salt.encode('utf-8')
        h = hmac.new(salt, None, _hash_mods[method])
    else:
        if method not in _hash_funcs:
            return
        h = _hash_funcs[method]()
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    h.update(password)
    return h.hexdigest()


def generate_password_hash(password, method = 'sha1', salt_length = 8):
    salt = method != 'plain' and gen_salt(salt_length) or ''
    h = _hash_internal(method, salt, password)
    if h is None:
        raise TypeError('invalid method %r' % method)
    return '%s$%s$%s' % (method, salt, h)


def check_password_hash(pwhash, password):
    if pwhash.count('$') < 2:
        return False
    method, salt, hashval = pwhash.split('$', 2)
    return _hash_internal(method, salt, password) == hashval