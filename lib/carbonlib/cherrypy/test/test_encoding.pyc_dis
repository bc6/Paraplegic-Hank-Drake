#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\test\test_encoding.py
import gzip
import sys
import cherrypy
from cherrypy._cpcompat import BytesIO, IncompleteRead, ntob, ntou
europoundUnicode = ntou('\x80\xa3')
sing = u'\u6bdb\u6cfd\u4e1c: Sing, Little Birdie?'
sing8 = sing.encode('utf-8')
sing16 = sing.encode('utf-16')
from cherrypy.test import helper

class EncodingTests(helper.CPWebCase):

    def setup_server():

        class Root:

            def index(self, param):
                yield europoundUnicode

            index.exposed = True

            def mao_zedong(self):
                return sing

            mao_zedong.exposed = True

            def utf8(self):
                return sing8

            utf8.exposed = True
            utf8._cp_config = {'tools.encode.encoding': 'utf-8'}

            def cookies_and_headers(self):
                cherrypy.response.cookie['candy'] = 'bar'
                cherrypy.response.cookie['candy']['domain'] = 'cherrypy.org'
                cherrypy.response.headers['Some-Header'] = 'My d\xc3\xb6g has fleas'
                return 'Any content'

            cookies_and_headers.exposed = True

            def reqparams(self, *args, **kwargs):
                return ntob(', ').join([ ': '.join((k, v)).encode('utf8') for k, v in cherrypy.request.params.items() ])

            reqparams.exposed = True

            def nontext(self, *args, **kwargs):
                cherrypy.response.headers['Content-Type'] = 'application/binary'
                return '\x00\x01\x02\x03'

            nontext.exposed = True
            nontext._cp_config = {'tools.encode.text_only': False,
             'tools.encode.add_charset': True}

        class GZIP:

            def index(self):
                yield 'Hello, world'

            index.exposed = True

            def noshow(self):
                raise IndexError()
                yield 'Here be dragons'

            noshow.exposed = True
            noshow._cp_config = {'tools.encode.on': False}

            def noshow_stream(self):
                raise IndexError()
                yield 'Here be dragons'

            noshow_stream.exposed = True
            noshow_stream._cp_config = {'response.stream': True}

        class Decode:

            def extra_charset(self, *args, **kwargs):
                return ', '.join([ ': '.join((k, v)) for k, v in cherrypy.request.params.items() ])

            extra_charset.exposed = True
            extra_charset._cp_config = {'tools.decode.on': True,
             'tools.decode.default_encoding': ['utf-16']}

            def force_charset(self, *args, **kwargs):
                return ', '.join([ ': '.join((k, v)) for k, v in cherrypy.request.params.items() ])

            force_charset.exposed = True
            force_charset._cp_config = {'tools.decode.on': True,
             'tools.decode.encoding': 'utf-16'}

        root = Root()
        root.gzip = GZIP()
        root.decode = Decode()
        cherrypy.tree.mount(root, config={'/gzip': {'tools.gzip.on': True}})

    setup_server = staticmethod(setup_server)

    def test_query_string_decoding(self):
        europoundUtf8 = europoundUnicode.encode('utf-8')
        self.getPage(ntob('/?param=') + europoundUtf8)
        self.assertBody(europoundUtf8)
        self.getPage('/reqparams?q=%C2%A3')
        self.assertBody(ntob('q: \xc2\xa3'))
        self.getPage('/reqparams?q=%A3')
        self.assertStatus(404)
        self.assertErrorPage(404, "The given query string could not be processed. Query strings for this resource must be encoded with 'utf8'.")

    def test_urlencoded_decoding(self):
        europoundUtf8 = europoundUnicode.encode('utf-8')
        body = ntob('param=') + europoundUtf8
        (self.getPage('/', method='POST', headers=[('Content-Type', 'application/x-www-form-urlencoded'), ('Content-Length', str(len(body)))], body=body),)
        self.assertBody(europoundUtf8)
        body = ntob('q=\xc2\xa3')
        (self.getPage('/reqparams', method='POST', headers=[('Content-Type', 'application/x-www-form-urlencoded'), ('Content-Length', str(len(body)))], body=body),)
        self.assertBody(ntob('q: \xc2\xa3'))
        body = ntob('\xff\xfeq\x00=\xff\xfe\xa3\x00')
        (self.getPage('/reqparams', method='POST', headers=[('Content-Type', 'application/x-www-form-urlencoded;charset=utf-16'), ('Content-Length', str(len(body)))], body=body),)
        self.assertBody(ntob('q: \xc2\xa3'))
        body = ntob('\xff\xfeq\x00=\xff\xfe\xa3\x00')
        (self.getPage('/reqparams', method='POST', headers=[('Content-Type', 'application/x-www-form-urlencoded;charset=utf-8'), ('Content-Length', str(len(body)))], body=body),)
        self.assertStatus(400)
        self.assertErrorPage(400, "The request entity could not be decoded. The following charsets were attempted: ['utf-8']")

    def test_decode_tool(self):
        body = ntob('\xff\xfeq\x00=\xff\xfe\xa3\x00')
        (self.getPage('/decode/extra_charset', method='POST', headers=[('Content-Type', 'application/x-www-form-urlencoded'), ('Content-Length', str(len(body)))], body=body),)
        self.assertBody(ntob('q: \xc2\xa3'))
        body = ntob('q=\xc2\xa3')
        (self.getPage('/decode/extra_charset', method='POST', headers=[('Content-Type', 'application/x-www-form-urlencoded'), ('Content-Length', str(len(body)))], body=body),)
        self.assertBody(ntob('q: \xc2\xa3'))
        body = ntob('q=\xc2\xa3')
        (self.getPage('/decode/force_charset', method='POST', headers=[('Content-Type', 'application/x-www-form-urlencoded'), ('Content-Length', str(len(body)))], body=body),)
        self.assertErrorPage(400, "The request entity could not be decoded. The following charsets were attempted: ['utf-16']")

    def test_multipart_decoding(self):
        body = ntob('\r\n'.join(['--X',
         'Content-Type: text/plain;charset=utf-16',
         'Content-Disposition: form-data; name="text"',
         '',
         '\xff\xfea\x00b\x00\x1c c\x00',
         '--X',
         'Content-Type: text/plain;charset=utf-16',
         'Content-Disposition: form-data; name="submit"',
         '',
         '\xff\xfeC\x00r\x00e\x00a\x00t\x00e\x00',
         '--X--']))
        (self.getPage('/reqparams', method='POST', headers=[('Content-Type', 'multipart/form-data;boundary=X'), ('Content-Length', str(len(body)))], body=body),)
        self.assertBody(ntob('text: ab\xe2\x80\x9cc, submit: Create'))

    def test_multipart_decoding_no_charset(self):
        body = ntob('\r\n'.join(['--X',
         'Content-Disposition: form-data; name="text"',
         '',
         '\xe2\x80\x9c',
         '--X',
         'Content-Disposition: form-data; name="submit"',
         '',
         'Create',
         '--X--']))
        (self.getPage('/reqparams', method='POST', headers=[('Content-Type', 'multipart/form-data;boundary=X'), ('Content-Length', str(len(body)))], body=body),)
        self.assertBody(ntob('text: \xe2\x80\x9c, submit: Create'))

    def test_multipart_decoding_no_successful_charset(self):
        body = ntob('\r\n'.join(['--X',
         'Content-Disposition: form-data; name="text"',
         '',
         '\xff\xfea\x00b\x00\x1c c\x00',
         '--X',
         'Content-Disposition: form-data; name="submit"',
         '',
         '\xff\xfeC\x00r\x00e\x00a\x00t\x00e\x00',
         '--X--']))
        (self.getPage('/reqparams', method='POST', headers=[('Content-Type', 'multipart/form-data;boundary=X'), ('Content-Length', str(len(body)))], body=body),)
        self.assertStatus(400)
        self.assertErrorPage(400, "The request entity could not be decoded. The following charsets were attempted: ['us-ascii', 'utf-8']")

    def test_nontext(self):
        self.getPage('/nontext')
        self.assertHeader('Content-Type', 'application/binary;charset=utf-8')
        self.assertBody('\x00\x01\x02\x03')

    def testEncoding(self):
        self.getPage('/mao_zedong')
        self.assertBody(sing8)
        self.getPage('/mao_zedong', [('Accept-Charset', 'utf-16')])
        self.assertHeader('Content-Type', 'text/html;charset=utf-16')
        self.assertBody(sing16)
        self.getPage('/mao_zedong', [('Accept-Charset', 'iso-8859-1;q=1, utf-16;q=0.5')])
        self.assertBody(sing16)
        self.getPage('/mao_zedong', [('Accept-Charset', '*;q=1, utf-7;q=.2')])
        self.assertBody(sing8)
        self.getPage('/mao_zedong', [('Accept-Charset', 'iso-8859-1, *;q=0')])
        self.assertStatus('406 Not Acceptable')
        self.assertInBody('Your client sent this Accept-Charset header: iso-8859-1, *;q=0. We tried these charsets: iso-8859-1.')
        self.getPage('/mao_zedong', [('Accept-Charset', 'us-ascii, ISO-8859-1, x-mac-ce')])
        self.assertStatus('406 Not Acceptable')
        self.assertInBody('Your client sent this Accept-Charset header: us-ascii, ISO-8859-1, x-mac-ce. We tried these charsets: ISO-8859-1, us-ascii, x-mac-ce.')
        self.getPage('/utf8')
        self.assertBody(sing8)
        self.getPage('/utf8', [('Accept-Charset', 'us-ascii, ISO-8859-1')])
        self.assertStatus('406 Not Acceptable')

    def testGzip(self):
        zbuf = BytesIO()
        zfile = gzip.GzipFile(mode='wb', fileobj=zbuf, compresslevel=9)
        zfile.write(ntob('Hello, world'))
        zfile.close()
        self.getPage('/gzip/', headers=[('Accept-Encoding', 'gzip')])
        self.assertInBody(zbuf.getvalue()[:3])
        self.assertHeader('Vary', 'Accept-Encoding')
        self.assertHeader('Content-Encoding', 'gzip')
        self.getPage('/gzip/', headers=[('Accept-Encoding', 'identity')])
        self.assertHeader('Vary', 'Accept-Encoding')
        self.assertNoHeader('Content-Encoding')
        self.assertBody('Hello, world')
        self.getPage('/gzip/', headers=[('Accept-Encoding', 'gzip;q=0')])
        self.assertHeader('Vary', 'Accept-Encoding')
        self.assertNoHeader('Content-Encoding')
        self.assertBody('Hello, world')
        self.getPage('/gzip/', headers=[('Accept-Encoding', '*;q=0')])
        self.assertStatus(406)
        self.assertNoHeader('Content-Encoding')
        self.assertErrorPage(406, 'identity, gzip')
        self.getPage('/gzip/noshow', headers=[('Accept-Encoding', 'gzip')])
        self.assertNoHeader('Content-Encoding')
        self.assertStatus(500)
        self.assertErrorPage(500, pattern='IndexError\n')
        if cherrypy.server.protocol_version == 'HTTP/1.0' or getattr(cherrypy.server, 'using_apache', False):
            self.getPage('/gzip/noshow_stream', headers=[('Accept-Encoding', 'gzip')])
            self.assertHeader('Content-Encoding', 'gzip')
            self.assertInBody('\x1f\x8b\x08\x00')
        else:
            self.assertRaises((ValueError, IncompleteRead), self.getPage, '/gzip/noshow_stream', headers=[('Accept-Encoding', 'gzip')])

    def test_UnicodeHeaders(self):
        self.getPage('/cookies_and_headers')
        self.assertBody('Any content')