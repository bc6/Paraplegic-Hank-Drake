from paste.httpexceptions import HTTPUnauthorized
from paste.httpheaders import *

class AuthBasicAuthenticator(object):
    type = 'basic'

    def __init__(self, realm, authfunc):
        self.realm = realm
        self.authfunc = authfunc



    def build_authentication(self):
        head = WWW_AUTHENTICATE.tuples('Basic realm="%s"' % self.realm)
        return HTTPUnauthorized(headers=head)



    def authenticate(self, environ):
        authorization = AUTHORIZATION(environ)
        if not authorization:
            return self.build_authentication()
        (authmeth, auth,) = authorization.split(' ', 1)
        if 'basic' != authmeth.lower():
            return self.build_authentication()
        auth = auth.strip().decode('base64')
        (username, password,) = auth.split(':', 1)
        if self.authfunc(environ, username, password):
            return username
        return self.build_authentication()


    __call__ = authenticate


class AuthBasicHandler(object):

    def __init__(self, application, realm, authfunc):
        self.application = application
        self.authenticate = AuthBasicAuthenticator(realm, authfunc)



    def __call__(self, environ, start_response):
        username = REMOTE_USER(environ)
        if not username:
            result = self.authenticate(environ)
            if isinstance(result, str):
                AUTH_TYPE.update(environ, 'basic')
                REMOTE_USER.update(environ, result)
            else:
                return result.wsgi_application(environ, start_response)
        return self.application(environ, start_response)



middleware = AuthBasicHandler
__all__ = ['AuthBasicHandler']

def make_basic(app, global_conf, realm, authfunc, **kw):
    from paste.util.import_string import eval_import
    import types
    authfunc = eval_import(authfunc)
    return AuthBasicHandler(app, realm, authfunc)


if '__main__' == __name__:
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)

