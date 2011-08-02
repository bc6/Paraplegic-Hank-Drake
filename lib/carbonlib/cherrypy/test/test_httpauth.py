from cherrypy.test import test
test.prefer_parent_path()
try:
    from hashlib import md5, sha1 as sha
except ImportError:
    from md5 import new as md5
    from sha import new as sha
import cherrypy
from cherrypy.lib import httpauth

def setup_server():

    class Root:

        def index(self):
            return 'This is public.'


        index.exposed = True


    class DigestProtected:

        def index(self):
            return "Hello %s, you've been authorized." % cherrypy.request.login


        index.exposed = True


    class BasicProtected:

        def index(self):
            return "Hello %s, you've been authorized." % cherrypy.request.login


        index.exposed = True


    class BasicProtected2:

        def index(self):
            return "Hello %s, you've been authorized." % cherrypy.request.login


        index.exposed = True


    def fetch_users():
        return {'test': 'test'}



    def sha_password_encrypter(password):
        return sha(password).hexdigest()



    def fetch_password(username):
        return sha('test').hexdigest()


    conf = {'/digest': {'tools.digest_auth.on': True,
                 'tools.digest_auth.realm': 'localhost',
                 'tools.digest_auth.users': fetch_users},
     '/basic': {'tools.basic_auth.on': True,
                'tools.basic_auth.realm': 'localhost',
                'tools.basic_auth.users': {'test': md5('test').hexdigest()}},
     '/basic2': {'tools.basic_auth.on': True,
                 'tools.basic_auth.realm': 'localhost',
                 'tools.basic_auth.users': fetch_password,
                 'tools.basic_auth.encrypt': sha_password_encrypter}}
    root = Root()
    root.digest = DigestProtected()
    root.basic = BasicProtected()
    root.basic2 = BasicProtected2()
    cherrypy.tree.mount(root, config=conf)


from cherrypy.test import helper

class HTTPAuthTest(helper.CPWebCase):

    def testPublic(self):
        self.getPage('/')
        self.assertStatus('200 OK')
        self.assertHeader('Content-Type', 'text/html;charset=utf-8')
        self.assertBody('This is public.')



    def testBasic(self):
        self.getPage('/basic/')
        self.assertStatus(401)
        self.assertHeader('WWW-Authenticate', 'Basic realm="localhost"')
        self.getPage('/basic/', [('Authorization', 'Basic dGVzdDp0ZX60')])
        self.assertStatus(401)
        self.getPage('/basic/', [('Authorization', 'Basic dGVzdDp0ZXN0')])
        self.assertStatus('200 OK')
        self.assertBody("Hello test, you've been authorized.")



    def testBasic2(self):
        self.getPage('/basic2/')
        self.assertStatus(401)
        self.assertHeader('WWW-Authenticate', 'Basic realm="localhost"')
        self.getPage('/basic2/', [('Authorization', 'Basic dGVzdDp0ZX60')])
        self.assertStatus(401)
        self.getPage('/basic2/', [('Authorization', 'Basic dGVzdDp0ZXN0')])
        self.assertStatus('200 OK')
        self.assertBody("Hello test, you've been authorized.")



    def testDigest(self):
        self.getPage('/digest/')
        self.assertStatus(401)
        value = None
        for (k, v,) in self.headers:
            if k.lower() == 'www-authenticate':
                if v.startswith('Digest'):
                    value = v
                    break

        if value is None:
            self._handlewebError('Digest authentification scheme was not found')
        value = value[7:]
        items = value.split(', ')
        tokens = {}
        for item in items:
            (key, value,) = item.split('=')
            tokens[key.lower()] = value

        missing_msg = '%s is missing'
        bad_value_msg = "'%s' was expecting '%s' but found '%s'"
        nonce = None
        if 'realm' not in tokens:
            self._handlewebError(missing_msg % 'realm')
        elif tokens['realm'] != '"localhost"':
            self._handlewebError(bad_value_msg % ('realm', '"localhost"', tokens['realm']))
        if 'nonce' not in tokens:
            self._handlewebError(missing_msg % 'nonce')
        else:
            nonce = tokens['nonce'].strip('"')
        if 'algorithm' not in tokens:
            self._handlewebError(missing_msg % 'algorithm')
        elif tokens['algorithm'] != '"MD5"':
            self._handlewebError(bad_value_msg % ('algorithm', '"MD5"', tokens['algorithm']))
        if 'qop' not in tokens:
            self._handlewebError(missing_msg % 'qop')
        elif tokens['qop'] != '"auth"':
            self._handlewebError(bad_value_msg % ('qop', '"auth"', tokens['qop']))
        base_auth = 'Digest username="test", realm="wrong realm", nonce="%s", uri="/digest/", algorithm=MD5, response="%s", qop=auth, nc=%s, cnonce="1522e61005789929"'
        auth = base_auth % (nonce, '', '00000001')
        params = httpauth.parseAuthorization(auth)
        response = httpauth._computeDigestResponse(params, 'test')
        auth = base_auth % (nonce, response, '00000001')
        self.getPage('/digest/', [('Authorization', auth)])
        self.assertStatus(401)
        base_auth = 'Digest username="test", realm="localhost", nonce="%s", uri="/digest/", algorithm=MD5, response="%s", qop=auth, nc=%s, cnonce="1522e61005789929"'
        auth = base_auth % (nonce, '', '00000001')
        params = httpauth.parseAuthorization(auth)
        response = httpauth._computeDigestResponse(params, 'test')
        auth = base_auth % (nonce, response, '00000001')
        self.getPage('/digest/', [('Authorization', auth)])
        self.assertStatus('200 OK')
        self.assertBody("Hello test, you've been authorized.")



if __name__ == '__main__':
    helper.testmain()

