from cherrypy.test import test
test.prefer_parent_path()
import cherrypy
script_names = ['', '/path/to/myapp']

def setup_server():
    cherrypy.config.update({'tools.proxy.on': True,
     'tools.proxy.base': 'www.mydomain.test'})

    class Root:

        def __init__(self, sn):
            self.thisnewpage = cherrypy.url('/this/new/page', script_name=sn)



        def pageurl(self):
            return self.thisnewpage


        pageurl.exposed = True

        def index(self):
            raise cherrypy.HTTPRedirect('dummy')


        index.exposed = True

        def remoteip(self):
            return cherrypy.request.remote.ip


        remoteip.exposed = True

        def xhost(self):
            raise cherrypy.HTTPRedirect('blah')


        xhost.exposed = True
        xhost._cp_config = {'tools.proxy.local': 'X-Host',
         'tools.trailing_slash.extra': True}

        def base(self):
            return cherrypy.request.base


        base.exposed = True

        def ssl(self):
            return cherrypy.request.base


        ssl.exposed = True
        ssl._cp_config = {'tools.proxy.scheme': 'X-Forwarded-Ssl'}

        def newurl(self):
            return "Browse to <a href='%s'>this page</a>." % cherrypy.url('/this/new/page')


        newurl.exposed = True

    for sn in script_names:
        cherrypy.tree.mount(Root(sn), sn)



from cherrypy.test import helper

class ProxyTest(helper.CPWebCase):

    def testProxy(self):
        self.getPage('/')
        self.assertHeader('Location', '%s://www.mydomain.test%s/dummy' % (self.scheme, self.prefix()))
        self.getPage('/', headers=[('X-Forwarded-Host', 'http://www.example.test')])
        self.assertHeader('Location', 'http://www.example.test/dummy')
        self.getPage('/', headers=[('X-Forwarded-Host', 'www.example.test')])
        self.assertHeader('Location', '%s://www.example.test/dummy' % self.scheme)
        self.getPage('/', headers=[('X-Forwarded-Host', 'http://www.example.test, www.cherrypy.test')])
        self.assertHeader('Location', 'http://www.example.test/dummy')
        self.getPage('/remoteip', headers=[('X-Forwarded-For', '192.168.0.20')])
        self.assertBody('192.168.0.20')
        self.getPage('/remoteip', headers=[('X-Forwarded-For', '67.15.36.43, 192.168.0.20')])
        self.assertBody('192.168.0.20')
        self.getPage('/xhost', headers=[('X-Host', 'www.example.test')])
        self.assertHeader('Location', '%s://www.example.test/blah' % self.scheme)
        self.getPage('/base', headers=[('X-Forwarded-Proto', 'https')])
        self.assertBody('https://www.mydomain.test')
        self.getPage('/ssl', headers=[('X-Forwarded-Ssl', 'on')])
        self.assertBody('https://www.mydomain.test')
        for sn in script_names:
            self.getPage(sn + '/newurl')
            self.assertBody("Browse to <a href='%s://www.mydomain.test" % self.scheme + sn + "/this/new/page'>this page</a>.")
            self.getPage(sn + '/newurl', headers=[('X-Forwarded-Host', 'http://www.example.test')])
            self.assertBody("Browse to <a href='http://www.example.test" + sn + "/this/new/page'>this page</a>.")
            port = ''
            if self.scheme == 'http' and self.PORT != 80:
                port = ':%s' % self.PORT
            elif self.scheme == 'https' and self.PORT != 443:
                port = ':%s' % self.PORT
            host = self.HOST
            if host in ('0.0.0.0', '::'):
                import socket
                host = socket.gethostname()
            expected = '%s://%s%s%s/this/new/page' % (self.scheme,
             host,
             port,
             sn)
            self.getPage(sn + '/pageurl')
            self.assertBody(expected)

        self.getPage('/xhost/', headers=[('X-Host', 'www.example.test')])
        self.assertHeader('Location', '%s://www.example.test/xhost' % self.scheme)



if __name__ == '__main__':
    helper.testmain()

