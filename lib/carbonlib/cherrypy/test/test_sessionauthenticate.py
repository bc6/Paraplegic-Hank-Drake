from cherrypy.test import test
test.prefer_parent_path()
import cherrypy

def setup_server():

    def check(username, password):
        if username != 'test' or password != 'password':
            return u'Wrong login/password'



    def augment_params():
        cherrypy.request.params['test'] = 'test'


    cherrypy.tools.augment_params = cherrypy.Tool('before_handler', augment_params, None, priority=30)

    class Test:
        _cp_config = {'tools.sessions.on': True,
         'tools.session_auth.on': True,
         'tools.session_auth.check_username_and_password': check,
         'tools.augment_params.on': True}

        def index(self, **kwargs):
            return 'Hi %s, you are logged in' % cherrypy.request.login


        index.exposed = True

    cherrypy.tree.mount(Test())


from cherrypy.test import helper

class SessionAuthenticateTest(helper.CPWebCase):

    def testSessionAuthenticate(self):
        self.getPage('/')
        self.assertInBody('<form method="post" action="do_login">')
        login_body = 'username=test&password=password&from_page=/'
        self.getPage('/do_login', method='POST', body=login_body)
        self.assertStatus((302, 303))
        self.getPage('/', self.cookies)
        self.assertBody('Hi test, you are logged in')
        self.getPage('/do_logout', self.cookies, method='POST')
        self.assertStatus((302, 303))
        self.getPage('/', self.cookies)
        self.assertInBody('<form method="post" action="do_login">')



if __name__ == '__main__':
    helper.testmain()

