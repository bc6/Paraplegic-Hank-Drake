#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\lib\auth_digest.py
"""An implementation of the server-side of HTTP Digest Access
Authentication, which is described in :rfc:`2617`.

Example usage, using the built-in get_ha1_dict_plain function which uses a dict
of plaintext passwords as the credentials store::

    userpassdict = {'alice' : '4x5istwelve'}
    get_ha1 = cherrypy.lib.auth_digest.get_ha1_dict_plain(userpassdict)
    digest_auth = {'tools.auth_digest.on': True,
                   'tools.auth_digest.realm': 'wonderland',
                   'tools.auth_digest.get_ha1': get_ha1,
                   'tools.auth_digest.key': 'a565c27146791cfb',
    }
    app_config = { '/' : digest_auth }
"""
__author__ = 'visteya'
__date__ = 'April 2009'
import time
from cherrypy._cpcompat import parse_http_list, parse_keqv_list
import cherrypy
from cherrypy._cpcompat import md5, ntob
md5_hex = lambda s: md5(ntob(s)).hexdigest()
qop_auth = 'auth'
qop_auth_int = 'auth-int'
valid_qops = (qop_auth, qop_auth_int)
valid_algorithms = ('MD5', 'MD5-sess')

def TRACE(msg):
    cherrypy.log(msg, context='TOOLS.AUTH_DIGEST')


def get_ha1_dict_plain(user_password_dict):

    def get_ha1(realm, username):
        password = user_password_dict.get(username)
        if password:
            return md5_hex('%s:%s:%s' % (username, realm, password))

    return get_ha1


def get_ha1_dict(user_ha1_dict):

    def get_ha1(realm, username):
        return user_ha1_dict.get(user)

    return get_ha1


def get_ha1_file_htdigest(filename):

    def get_ha1(realm, username):
        result = None
        f = open(filename, 'r')
        for line in f:
            u, r, ha1 = line.rstrip().split(':')
            if u == username and r == realm:
                result = ha1
                break

        f.close()
        return result

    return get_ha1


def synthesize_nonce(s, key, timestamp = None):
    if timestamp is None:
        timestamp = int(time.time())
    h = md5_hex('%s:%s:%s' % (timestamp, s, key))
    nonce = '%s:%s' % (timestamp, h)
    return nonce


def H(s):
    return md5_hex(s)


class HttpDigestAuthorization(object):

    def errmsg(self, s):
        return 'Digest Authorization header: %s' % s

    def __init__(self, auth_header, http_method, debug = False):
        self.http_method = http_method
        self.debug = debug
        scheme, params = auth_header.split(' ', 1)
        self.scheme = scheme.lower()
        if self.scheme != 'digest':
            raise ValueError('Authorization scheme is not "Digest"')
        self.auth_header = auth_header
        items = parse_http_list(params)
        paramsd = parse_keqv_list(items)
        self.realm = paramsd.get('realm')
        self.username = paramsd.get('username')
        self.nonce = paramsd.get('nonce')
        self.uri = paramsd.get('uri')
        self.method = paramsd.get('method')
        self.response = paramsd.get('response')
        self.algorithm = paramsd.get('algorithm', 'MD5')
        self.cnonce = paramsd.get('cnonce')
        self.opaque = paramsd.get('opaque')
        self.qop = paramsd.get('qop')
        self.nc = paramsd.get('nc')
        if self.algorithm not in valid_algorithms:
            raise ValueError(self.errmsg("Unsupported value for algorithm: '%s'" % self.algorithm))
        has_reqd = self.username and self.realm and self.nonce and self.uri and self.response
        if not has_reqd:
            raise ValueError(self.errmsg('Not all required parameters are present.'))
        if self.qop:
            if self.qop not in valid_qops:
                raise ValueError(self.errmsg("Unsupported value for qop: '%s'" % self.qop))
            if not (self.cnonce and self.nc):
                raise ValueError(self.errmsg('If qop is sent then cnonce and nc MUST be present'))
        elif self.cnonce or self.nc:
            raise ValueError(self.errmsg('If qop is not sent, neither cnonce nor nc can be present'))

    def __str__(self):
        return 'authorization : %s' % self.auth_header

    def validate_nonce(self, s, key):
        try:
            timestamp, hashpart = self.nonce.split(':', 1)
            s_timestamp, s_hashpart = synthesize_nonce(s, key, timestamp).split(':', 1)
            is_valid = s_hashpart == hashpart
            if self.debug:
                TRACE('validate_nonce: %s' % is_valid)
            return is_valid
        except ValueError:
            pass

        return False

    def is_nonce_stale(self, max_age_seconds = 600):
        try:
            timestamp, hashpart = self.nonce.split(':', 1)
            if int(timestamp) + max_age_seconds > int(time.time()):
                return False
        except ValueError:
            pass

        if self.debug:
            TRACE('nonce is stale')
        return True

    def HA2(self, entity_body = ''):
        if self.qop is None or self.qop == 'auth':
            a2 = '%s:%s' % (self.http_method, self.uri)
        elif self.qop == 'auth-int':
            a2 = '%s:%s:%s' % (self.http_method, self.uri, H(entity_body))
        else:
            raise ValueError(self.errmsg('Unrecognized value for qop!'))
        return H(a2)

    def request_digest(self, ha1, entity_body = ''):
        ha2 = self.HA2(entity_body)
        if self.qop:
            req = '%s:%s:%s:%s:%s' % (self.nonce,
             self.nc,
             self.cnonce,
             self.qop,
             ha2)
        else:
            req = '%s:%s' % (self.nonce, ha2)
        if self.algorithm == 'MD5-sess':
            ha1 = H('%s:%s:%s' % (ha1, self.nonce, self.cnonce))
        digest = H('%s:%s' % (ha1, req))
        return digest


def www_authenticate(realm, key, algorithm = 'MD5', nonce = None, qop = qop_auth, stale = False):
    if qop not in valid_qops:
        raise ValueError("Unsupported value for qop: '%s'" % qop)
    if algorithm not in valid_algorithms:
        raise ValueError("Unsupported value for algorithm: '%s'" % algorithm)
    if nonce is None:
        nonce = synthesize_nonce(realm, key)
    s = 'Digest realm="%s", nonce="%s", algorithm="%s", qop="%s"' % (realm,
     nonce,
     algorithm,
     qop)
    if stale:
        s += ', stale="true"'
    return s


def digest_auth(realm, get_ha1, key, debug = False):
    request = cherrypy.serving.request
    auth_header = request.headers.get('authorization')
    nonce_is_stale = False
    if auth_header is not None:
        try:
            auth = HttpDigestAuthorization(auth_header, request.method, debug=debug)
        except ValueError:
            raise cherrypy.HTTPError(400, 'The Authorization header could not be parsed.')

        if debug:
            TRACE(str(auth))
        if auth.validate_nonce(realm, key):
            ha1 = get_ha1(realm, auth.username)
            if ha1 is not None:
                digest = auth.request_digest(ha1, entity_body=request.body)
                if digest == auth.response:
                    if debug:
                        TRACE('digest matches auth.response')
                    nonce_is_stale = auth.is_nonce_stale(max_age_seconds=600)
                    if not nonce_is_stale:
                        request.login = auth.username
                        if debug:
                            TRACE('authentication of %s successful' % auth.username)
                        return
    header = www_authenticate(realm, key, stale=nonce_is_stale)
    if debug:
        TRACE(header)
    cherrypy.serving.response.headers['WWW-Authenticate'] = header
    raise cherrypy.HTTPError(401, 'You are not authorized to access that resource')