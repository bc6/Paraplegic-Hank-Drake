from cherrypy.test import test
test.prefer_parent_path()
import os
import sys
localDir = os.path.join(os.getcwd(), os.path.dirname(__file__))
import socket
import time
import cherrypy

def setup_server():

    class Root:

        def index(self):
            return cherrypy.request.wsgi_environ['SERVER_PORT']


        index.exposed = True

        def upload(self, file):
            return 'Size: %s' % len(file.file.read())


        upload.exposed = True

        def tinyupload(self):
            return cherrypy.request.body.read()


        tinyupload.exposed = True
        tinyupload._cp_config = {'request.body.maxbytes': 100}

    cherrypy.tree.mount(Root())
    cherrypy.config.update({'server.socket_host': '0.0.0.0',
     'server.socket_port': 9876,
     'server.max_request_body_size': 200,
     'server.max_request_header_size': 500,
     'server.socket_timeout': 0.5,
     'server.2.instance': 'cherrypy._cpwsgi_server.CPWSGIServer',
     'server.2.socket_port': 9877,
     'server.yetanother.socket_port': 9878})


from cherrypy.test import helper

class ServerConfigTests(helper.CPWebCase):
    PORT = 9876

    def testBasicConfig(self):
        self.getPage('/')
        self.assertBody(str(self.PORT))



    def testAdditionalServers(self):
        if self.scheme == 'https':
            return self.skip('not available under ssl')
        self.PORT = 9877
        self.getPage('/')
        self.assertBody(str(self.PORT))
        self.PORT = 9878
        self.getPage('/')
        self.assertBody(str(self.PORT))



    def testMaxRequestSizePerHandler(self):
        if getattr(cherrypy.server, 'using_apache', False):
            return self.skip('skipped due to known Apache differences... ')
        self.getPage('/tinyupload', method='POST', headers=[('Content-Type', 'text/plain'), ('Content-Length', '100')], body='x' * 100)
        self.assertStatus(200)
        self.assertBody('x' * 100)
        self.getPage('/tinyupload', method='POST', headers=[('Content-Type', 'text/plain'), ('Content-Length', '101')], body='x' * 101)
        self.assertStatus(413)



    def testMaxRequestSize(self):
        if getattr(cherrypy.server, 'using_apache', False):
            return self.skip('skipped due to known Apache differences... ')
        for size in (500, 5000, 50000):
            self.getPage('/', headers=[('From', 'x' * 500)])
            self.assertStatus(413)

        lines256 = 'x' * 248
        self.getPage('/', headers=[('Host', '%s:%s' % (self.HOST, self.PORT)), ('From', lines256)])
        body = '\r\n'.join(['--x',
         'Content-Disposition: form-data; name="file"; filename="hello.txt"',
         'Content-Type: text/plain',
         '',
         '%s',
         '--x--'])
        partlen = 200 - len(body)
        b = body % ('x' * partlen)
        h = [('Content-type', 'multipart/form-data; boundary=x'), ('Content-Length', '%s' % len(b))]
        self.getPage('/upload', h, 'POST', b)
        self.assertBody('Size: %d' % partlen)
        b = body % ('x' * 200)
        h = [('Content-type', 'multipart/form-data; boundary=x'), ('Content-Length', '%s' % len(b))]
        self.getPage('/upload', h, 'POST', b)
        self.assertStatus(413)



if __name__ == '__main__':
    helper.testmain()

