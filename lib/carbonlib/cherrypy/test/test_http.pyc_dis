#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\test\test_http.py
import mimetypes
import cherrypy
from cherrypy._cpcompat import HTTPConnection, HTTPSConnection, ntob

def encode_multipart_formdata(files):
    BOUNDARY = '________ThIs_Is_tHe_bouNdaRY_$'
    L = []
    for key, filename, value in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        ct = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        L.append('Content-Type: %s' % ct)
        L.append('')
        L.append(value)

    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = '\r\n'.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return (content_type, body)


from cherrypy.test import helper

class HTTPTests(helper.CPWebCase):

    def setup_server():

        class Root:

            def index(self, *args, **kwargs):
                return 'Hello world!'

            index.exposed = True

            def no_body(self, *args, **kwargs):
                return 'Hello world!'

            no_body.exposed = True
            no_body._cp_config = {'request.process_request_body': False}

            def post_multipart(self, file):
                contents = file.file.read()
                summary = []
                curchar = ''
                count = 0
                for c in contents:
                    if c == curchar:
                        count += 1
                    else:
                        if count:
                            summary.append('%s * %d' % (curchar, count))
                        count = 1
                        curchar = c

                if count:
                    summary.append('%s * %d' % (curchar, count))
                return ', '.join(summary)

            post_multipart.exposed = True

        cherrypy.tree.mount(Root())
        cherrypy.config.update({'server.max_request_body_size': 30000000})

    setup_server = staticmethod(setup_server)

    def test_no_content_length(self):
        if self.scheme == 'https':
            c = HTTPSConnection('%s:%s' % (self.interface(), self.PORT))
        else:
            c = HTTPConnection('%s:%s' % (self.interface(), self.PORT))
        c.request('POST', '/no_body')
        response = c.getresponse()
        self.body = response.fp.read()
        self.status = str(response.status)
        self.assertStatus(200)
        self.assertBody(ntob('Hello world!'))
        if self.scheme == 'https':
            c = HTTPSConnection('%s:%s' % (self.interface(), self.PORT))
        else:
            c = HTTPConnection('%s:%s' % (self.interface(), self.PORT))
        c.request('POST', '/')
        response = c.getresponse()
        self.body = response.fp.read()
        self.status = str(response.status)
        self.assertStatus(411)

    def test_post_multipart(self):
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        contents = ''.join([ c * 65536 for c in alphabet ])
        files = [('file', 'file.txt', contents)]
        content_type, body = encode_multipart_formdata(files)
        body = body.encode('Latin-1')
        if self.scheme == 'https':
            c = HTTPSConnection('%s:%s' % (self.interface(), self.PORT))
        else:
            c = HTTPConnection('%s:%s' % (self.interface(), self.PORT))
        c.putrequest('POST', '/post_multipart')
        c.putheader('Content-Type', content_type)
        c.putheader('Content-Length', str(len(body)))
        c.endheaders()
        c.send(body)
        response = c.getresponse()
        self.body = response.fp.read()
        self.status = str(response.status)
        self.assertStatus(200)
        self.assertBody(', '.join([ '%s * 65536' % c for c in alphabet ]))

    def test_malformed_request_line(self):
        if getattr(cherrypy.server, 'using_apache', False):
            return self.skip('skipped due to known Apache differences...')
        if self.scheme == 'https':
            c = HTTPSConnection('%s:%s' % (self.interface(), self.PORT))
        else:
            c = HTTPConnection('%s:%s' % (self.interface(), self.PORT))
        c._output(ntob('GET /'))
        c._send_output()
        if hasattr(c, 'strict'):
            response = c.response_class(c.sock, strict=c.strict, method='GET')
        else:
            response = c.response_class(c.sock, method='GET')
        response.begin()
        self.assertEqual(response.status, 400)
        self.assertEqual(response.fp.read(22), ntob('Malformed Request-Line'))
        c.close()

    def test_malformed_header(self):
        if self.scheme == 'https':
            c = HTTPSConnection('%s:%s' % (self.interface(), self.PORT))
        else:
            c = HTTPConnection('%s:%s' % (self.interface(), self.PORT))
        c.putrequest('GET', '/')
        c.putheader('Content-Type', 'text/plain')
        c._output(ntob('Re, 1.2.3.4#015#012'))
        c.endheaders()
        response = c.getresponse()
        self.status = str(response.status)
        self.assertStatus(400)
        self.body = response.fp.read(20)
        self.assertBody('Illegal header line.')