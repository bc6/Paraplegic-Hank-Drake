__version__ = (1, 0, 1)
__author__ = 'Tiago Cogumbreiro <cogumbreiro@users.sf.net>'
__credits__ = '\n    Peter van Kampen for its recipe which implement most of Digest authentication:\n    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/302378\n'
__license__ = '\nCopyright (c) 2005, Tiago Cogumbreiro <cogumbreiro@users.sf.net>\nAll rights reserved.\n\nRedistribution and use in source and binary forms, with or without modification, \nare permitted provided that the following conditions are met:\n\n    * Redistributions of source code must retain the above copyright notice, \n      this list of conditions and the following disclaimer.\n    * Redistributions in binary form must reproduce the above copyright notice, \n      this list of conditions and the following disclaimer in the documentation \n      and/or other materials provided with the distribution.\n    * Neither the name of Sylvain Hellegouarch nor the names of his contributors \n      may be used to endorse or promote products derived from this software \n      without specific prior written permission.\n\nTHIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND \nANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED \nWARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE \nDISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE \nFOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL \nDAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR \nSERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER \nCAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, \nOR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE \nOF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.\n'
__all__ = ('digestAuth', 'basicAuth', 'doAuth', 'checkResponse', 'parseAuthorization', 'SUPPORTED_ALGORITHM', 'md5SessionKey', 'calculateNonce', 'SUPPORTED_QOP')
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5
import time
import base64
from urllib2 import parse_http_list, parse_keqv_list
MD5 = 'MD5'
MD5_SESS = 'MD5-sess'
AUTH = 'auth'
AUTH_INT = 'auth-int'
SUPPORTED_ALGORITHM = (MD5, MD5_SESS)
SUPPORTED_QOP = (AUTH, AUTH_INT)
DIGEST_AUTH_ENCODERS = {MD5: lambda val: md5(val).hexdigest(),
 MD5_SESS: lambda val: md5(val).hexdigest()}

def calculateNonce(realm, algorithm = MD5):
    global DIGEST_AUTH_ENCODERS
    try:
        encoder = DIGEST_AUTH_ENCODERS[algorithm]
    except KeyError:
        raise NotImplementedError('The chosen algorithm (%s) does not have an implementation yet' % algorithm)
    return encoder('%d:%s' % (time.time(), realm))



def digestAuth(realm, algorithm = MD5, nonce = None, qop = AUTH):
    if nonce is None:
        nonce = calculateNonce(realm, algorithm)
    return 'Digest realm="%s", nonce="%s", algorithm="%s", qop="%s"' % (realm,
     nonce,
     algorithm,
     qop)



def basicAuth(realm):
    return 'Basic realm="%s"' % realm



def doAuth(realm):
    return digestAuth(realm) + ' ' + basicAuth(realm)



def _parseDigestAuthorization(auth_params):
    items = parse_http_list(auth_params)
    params = parse_keqv_list(items)
    required = ['username',
     'realm',
     'nonce',
     'uri',
     'response']
    for k in required:
        if k not in params:
            return None

    if 'qop' in params and not ('cnonce' in params and 'nc' in params):
        return None
    if ('cnonce' in params or 'nc' in params) and 'qop' not in params:
        return None
    return params



def _parseBasicAuthorization(auth_params):
    (username, password,) = base64.decodestring(auth_params).split(':', 1)
    return {'username': username,
     'password': password}


AUTH_SCHEMES = {'basic': _parseBasicAuthorization,
 'digest': _parseDigestAuthorization}

def parseAuthorization(credentials):
    global AUTH_SCHEMES
    (auth_scheme, auth_params,) = credentials.split(' ', 1)
    auth_scheme = auth_scheme.lower()
    parser = AUTH_SCHEMES[auth_scheme]
    params = parser(auth_params)
    if params is None:
        return 
    params['auth_scheme'] = auth_scheme
    return params



def md5SessionKey(params, password):
    keys = ('username', 'realm', 'nonce', 'cnonce')
    params_copy = {}
    for key in keys:
        params_copy[key] = params[key]

    params_copy['algorithm'] = MD5_SESS
    return _A1(params_copy, password)



def _A1(params, password):
    algorithm = params.get('algorithm', MD5)
    H = DIGEST_AUTH_ENCODERS[algorithm]
    if algorithm == MD5:
        return '%s:%s:%s' % (params['username'], params['realm'], password)
    if algorithm == MD5_SESS:
        h_a1 = H('%s:%s:%s' % (params['username'], params['realm'], password))
        return '%s:%s:%s' % (h_a1, params['nonce'], params['cnonce'])



def _A2(params, method, kwargs):
    qop = params.get('qop', 'auth')
    if qop == 'auth':
        return method + ':' + params['uri']
    if qop == 'auth-int':
        entity_body = kwargs.get('entity_body', '')
        H = kwargs['H']
        return '%s:%s:%s' % (method, params['uri'], H(entity_body))
    raise NotImplementedError("The 'qop' method is unknown: %s" % qop)



def _computeDigestResponse(auth_map, password, method = 'GET', A1 = None, **kwargs):
    params = auth_map
    algorithm = params.get('algorithm', MD5)
    H = DIGEST_AUTH_ENCODERS[algorithm]
    KD = lambda secret, data: H(secret + ':' + data)
    qop = params.get('qop', None)
    H_A2 = H(_A2(params, method, kwargs))
    if algorithm == MD5_SESS and A1 is not None:
        H_A1 = H(A1)
    else:
        H_A1 = H(_A1(params, password))
    if qop in ('auth', 'auth-int'):
        request = '%s:%s:%s:%s:%s' % (params['nonce'],
         params['nc'],
         params['cnonce'],
         params['qop'],
         H_A2)
    elif qop is None:
        request = '%s:%s' % (params['nonce'], H_A2)
    return KD(H_A1, request)



def _checkDigestResponse(auth_map, password, method = 'GET', A1 = None, **kwargs):
    if auth_map['realm'] != kwargs.get('realm', None):
        return False
    response = _computeDigestResponse(auth_map, password, method, A1, **kwargs)
    return response == auth_map['response']



def _checkBasicResponse(auth_map, password, method = 'GET', encrypt = None, **kwargs):
    try:
        return encrypt(auth_map['password'], auth_map['username']) == password
    except TypeError:
        return encrypt(auth_map['password']) == password


AUTH_RESPONSES = {'basic': _checkBasicResponse,
 'digest': _checkDigestResponse}

def checkResponse(auth_map, password, method = 'GET', encrypt = None, **kwargs):
    global AUTH_RESPONSES
    checker = AUTH_RESPONSES[auth_map['auth_scheme']]
    return checker(auth_map, password, method=method, encrypt=encrypt, **kwargs)



