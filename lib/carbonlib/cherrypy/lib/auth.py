import cherrypy
from cherrypy.lib import httpauth

def check_auth(users, encrypt = None, realm = None):
    request = cherrypy.serving.request
    if 'authorization' in request.headers:
        ah = httpauth.parseAuthorization(request.headers['authorization'])
        if ah is None:
            raise cherrypy.HTTPError(400, 'Bad Request')
        if not encrypt:
            encrypt = httpauth.DIGEST_AUTH_ENCODERS[httpauth.MD5]
        if hasattr(users, '__call__'):
            try:
                users = users()
                if not isinstance(users, dict):
                    raise ValueError('Authentication users must be a dictionary')
                password = users.get(ah['username'], None)
            except TypeError:
                password = users(ah['username'])
        elif not isinstance(users, dict):
            raise ValueError('Authentication users must be a dictionary')
        password = users.get(ah['username'], None)
        if httpauth.checkResponse(ah, password, method=request.method, encrypt=encrypt, realm=realm):
            request.login = ah['username']
            return True
        request.login = False
    return False



def basic_auth(realm, users, encrypt = None, debug = False):
    if check_auth(users, encrypt):
        if debug:
            cherrypy.log('Auth successful', 'TOOLS.BASIC_AUTH')
        return 
    cherrypy.serving.response.headers['www-authenticate'] = httpauth.basicAuth(realm)
    raise cherrypy.HTTPError(401, 'You are not authorized to access that resource')



def digest_auth(realm, users, debug = False):
    if check_auth(users, realm=realm):
        if debug:
            cherrypy.log('Auth successful', 'TOOLS.DIGEST_AUTH')
        return 
    cherrypy.serving.response.headers['www-authenticate'] = httpauth.digestAuth(realm)
    raise cherrypy.HTTPError(401, 'You are not authorized to access that resource')



