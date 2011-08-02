from cherrypy.test import test
test.prefer_parent_path()
import os
localDir = os.path.dirname(__file__)
import sys
import types
from httplib import IncompleteRead
import cherrypy
from cherrypy import _cptools, tools
from cherrypy.lib import static, httputil
defined_http_methods = ('OPTIONS',
 'GET',
 'HEAD',
 'POST',
 'PUT',
 'DELETE',
 'TRACE',
 'PROPFIND')

def setup_server():

    class Root:

        def index(self):
            return 'hello'


        index.exposed = True

        def scheme(self):
            return cherrypy.request.scheme


        scheme.exposed = True

    root = Root()

    class TestType(type):

        def __init__(cls, name, bases, dct):
            type.__init__(cls, name, bases, dct)
            for value in dct.itervalues():
                if isinstance(value, types.FunctionType):
                    value.exposed = True

            setattr(root, name.lower(), cls())




    class Test(object):
        __metaclass__ = TestType


    class Params(Test):

        def index(self, thing):
            return repr(thing)



        def ismap(self, x, y):
            return 'Coordinates: %s, %s' % (x, y)



        def default(self, *args, **kwargs):
            return 'args: %s kwargs: %s' % (args, kwargs)


        default._cp_config = {'request.query_string_encoding': 'latin1'}


    class ParamErrorsCallable(object):
        exposed = True

        def __call__(self):
            return 'data'




    class ParamErrors(Test):

        def one_positional(self, param1):
            return 'data'


        one_positional.exposed = True

        def one_positional_args(self, param1, *args):
            return 'data'


        one_positional_args.exposed = True

        def one_positional_args_kwargs(self, param1, *args, **kwargs):
            return 'data'


        one_positional_args_kwargs.exposed = True

        def one_positional_kwargs(self, param1, **kwargs):
            return 'data'


        one_positional_kwargs.exposed = True

        def no_positional(self):
            return 'data'


        no_positional.exposed = True

        def no_positional_args(self, *args):
            return 'data'


        no_positional_args.exposed = True

        def no_positional_args_kwargs(self, *args, **kwargs):
            return 'data'


        no_positional_args_kwargs.exposed = True

        def no_positional_kwargs(self, **kwargs):
            return 'data'


        no_positional_kwargs.exposed = True
        callable_object = ParamErrorsCallable()

        def raise_type_error(self, **kwargs):
            raise TypeError('Client Error')


        raise_type_error.exposed = True

        def raise_type_error_with_default_param(self, x, y = None):
            return '%d' % 'a'


        raise_type_error_with_default_param.exposed = True


    def callable_error_page(status, **kwargs):
        return "Error %s - Well, I'm very sorry but you haven't paid!" % status



    class Error(Test):
        _cp_config = {'tools.log_tracebacks.on': True}

        def reason_phrase(self):
            raise cherrypy.HTTPError("410 Gone fishin'")



        def custom(self, err = '404'):
            raise cherrypy.HTTPError(int(err), 'No, <b>really</b>, not found!')


        custom._cp_config = {'error_page.404': os.path.join(localDir, 'static/index.html'),
         'error_page.401': callable_error_page}

        def custom_default(self):
            return 1 + 'a'


        custom_default._cp_config = {'error_page.default': callable_error_page}

        def noexist(self):
            raise cherrypy.HTTPError(404, 'No, <b>really</b>, not found!')


        noexist._cp_config = {'error_page.404': 'nonexistent.html'}

        def page_method(self):
            raise ValueError()



        def page_yield(self):
            yield 'howdy'
            raise ValueError()



        def page_streamed(self):
            yield 'word up'
            raise ValueError()
            yield 'very oops'


        page_streamed._cp_config = {'response.stream': True}

        def cause_err_in_finalize(self):
            cherrypy.response.status = 'ZOO OK'


        cause_err_in_finalize._cp_config = {'request.show_tracebacks': False}

        def rethrow(self):
            raise ValueError()


        rethrow._cp_config = {'request.throw_errors': True}


    class Expect(Test):

        def expectation_failed(self):
            expect = cherrypy.request.headers.elements('Expect')
            if expect and expect[0].value != '100-continue':
                raise cherrypy.HTTPError(400)
            raise cherrypy.HTTPError(417, 'Expectation Failed')




    class Headers(Test):

        def default(self, headername):
            return cherrypy.request.headers[headername]



        def doubledheaders(self):
            hMap = cherrypy.response.headers
            hMap['content-type'] = 'text/html'
            hMap['content-length'] = 18
            hMap['server'] = 'CherryPy headertest'
            hMap['location'] = '%s://%s:%s/headers/' % (cherrypy.request.local.ip, cherrypy.request.local.port, cherrypy.request.scheme)
            hMap['Expires'] = 'Thu, 01 Dec 2194 16:00:00 GMT'
            return 'double header test'



        def ifmatch(self):
            val = cherrypy.request.headers['If-Match']
            cherrypy.response.headers['ETag'] = val
            return val




    class HeaderElements(Test):

        def get_elements(self, headername):
            e = cherrypy.request.headers.elements(headername)
            return '\n'.join([ unicode(x) for x in e ])




    class Method(Test):

        def index(self):
            m = cherrypy.request.method
            if m in defined_http_methods or m == 'CONNECT':
                return m
            if m == 'LINK':
                raise cherrypy.HTTPError(405)
            else:
                raise cherrypy.HTTPError(501)



        def parameterized(self, data):
            return data



        def request_body(self):
            return cherrypy.request.body



        def reachable(self):
            return 'success'




    class Divorce:
        documents = {}

        def index(self):
            yield '<h1>Choose your document</h1>\n'
            yield '<ul>\n'
            for (id, contents,) in self.documents.items():
                yield "    <li><a href='/divorce/get?ID=%s'>%s</a>: %s</li>\n" % (id, id, contents)

            yield '</ul>'


        index.exposed = True

        def get(self, ID):
            return 'Divorce document %s: %s' % (ID, self.documents.get(ID, 'empty'))


        get.exposed = True

    root.divorce = Divorce()

    class ThreadLocal(Test):

        def index(self):
            existing = repr(getattr(cherrypy.request, 'asdf', None))
            cherrypy.request.asdf = 'rassfrassin'
            return existing



    appconf = {'/method': {'request.methods_with_bodies': ('POST', 'PUT', 'PROPFIND')}}
    cherrypy.tree.mount(root, config=appconf)


from cherrypy.test import helper

class RequestObjectTests(helper.CPWebCase):

    def test_scheme(self):
        self.getPage('/scheme')
        self.assertBody(self.scheme)



    def testParams(self):
        self.getPage('/params/?thing=a')
        self.assertBody("u'a'")
        self.getPage('/params/?thing=a&thing=b&thing=c')
        self.assertBody("[u'a', u'b', u'c']")
        cherrypy.config.update({'request.show_mismatched_params': True})
        self.getPage('/params/?notathing=meeting')
        self.assertInBody('Missing parameters: thing')
        self.getPage('/params/?thing=meeting&notathing=meeting')
        self.assertInBody('Unexpected query string parameters: notathing')
        cherrypy.config.update({'request.show_mismatched_params': False})
        self.getPage('/params/?notathing=meeting')
        self.assertInBody('Not Found')
        self.getPage('/params/?thing=meeting&notathing=meeting')
        self.assertInBody('Not Found')
        self.getPage('/params/%d4%20%e3/cheese?Gruy%E8re=Bulgn%e9ville')
        self.assertBody("args: ('\\xd4 \\xe3', 'cheese') kwargs: {'Gruy\\xe8re': u'Bulgn\\xe9ville'}")
        self.getPage('/params/code?url=http%3A//cherrypy.org/index%3Fa%3D1%26b%3D2')
        self.assertBody("args: ('code',) kwargs: {'url': u'http://cherrypy.org/index?a=1&b=2'}")
        self.getPage('/params/ismap?223,114')
        self.assertBody('Coordinates: 223, 114')
        self.getPage('/params/dictlike?a[1]=1&a[2]=2&b=foo&b[bar]=baz')
        self.assertBody("args: ('dictlike',) kwargs: {'a[1]': u'1', 'b[bar]': u'baz', 'b': u'foo', 'a[2]': u'2'}")



    def testParamErrors(self):
        for uri in ('/paramerrors/one_positional?param1=foo', '/paramerrors/one_positional_args?param1=foo', '/paramerrors/one_positional_args/foo', '/paramerrors/one_positional_args/foo/bar/baz', '/paramerrors/one_positional_args_kwargs?param1=foo&param2=bar', '/paramerrors/one_positional_args_kwargs/foo?param2=bar&param3=baz', '/paramerrors/one_positional_args_kwargs/foo/bar/baz?param2=bar&param3=baz', '/paramerrors/one_positional_kwargs?param1=foo&param2=bar&param3=baz', '/paramerrors/one_positional_kwargs/foo?param4=foo&param2=bar&param3=baz', '/paramerrors/no_positional', '/paramerrors/no_positional_args/foo', '/paramerrors/no_positional_args/foo/bar/baz', '/paramerrors/no_positional_args_kwargs?param1=foo&param2=bar', '/paramerrors/no_positional_args_kwargs/foo?param2=bar', '/paramerrors/no_positional_args_kwargs/foo/bar/baz?param2=bar&param3=baz', '/paramerrors/no_positional_kwargs?param1=foo&param2=bar', '/paramerrors/callable_object'):
            self.getPage(uri)
            self.assertStatus(200)

        error_msgs = ['Missing parameters',
         'Nothing matches the given URI',
         'Multiple values for parameters',
         'Unexpected query string parameters',
         'Unexpected body parameters']
        for (uri, msg,) in (('/paramerrors/one_positional', error_msgs[0]),
         ('/paramerrors/one_positional?foo=foo', error_msgs[0]),
         ('/paramerrors/one_positional/foo/bar/baz', error_msgs[1]),
         ('/paramerrors/one_positional/foo?param1=foo', error_msgs[2]),
         ('/paramerrors/one_positional/foo?param1=foo&param2=foo', error_msgs[2]),
         ('/paramerrors/one_positional_args/foo?param1=foo&param2=foo', error_msgs[2]),
         ('/paramerrors/one_positional_args/foo/bar/baz?param2=foo', error_msgs[3]),
         ('/paramerrors/one_positional_args_kwargs/foo/bar/baz?param1=bar&param3=baz', error_msgs[2]),
         ('/paramerrors/one_positional_kwargs/foo?param1=foo&param2=bar&param3=baz', error_msgs[2]),
         ('/paramerrors/no_positional/boo', error_msgs[1]),
         ('/paramerrors/no_positional?param1=foo', error_msgs[3]),
         ('/paramerrors/no_positional_args/boo?param1=foo', error_msgs[3]),
         ('/paramerrors/no_positional_kwargs/boo?param1=foo', error_msgs[1]),
         ('/paramerrors/callable_object?param1=foo', error_msgs[3]),
         ('/paramerrors/callable_object/boo', error_msgs[1])):
            for show_mismatched_params in (True, False):
                cherrypy.config.update({'request.show_mismatched_params': show_mismatched_params})
                self.getPage(uri)
                self.assertStatus(404)
                if show_mismatched_params:
                    self.assertInBody(msg)
                else:
                    self.assertInBody('Not Found')


        for (uri, body, msg,) in (('/paramerrors/one_positional/foo', 'param1=foo', error_msgs[2]),
         ('/paramerrors/one_positional/foo', 'param1=foo&param2=foo', error_msgs[2]),
         ('/paramerrors/one_positional_args/foo', 'param1=foo&param2=foo', error_msgs[2]),
         ('/paramerrors/one_positional_args/foo/bar/baz', 'param2=foo', error_msgs[4]),
         ('/paramerrors/one_positional_args_kwargs/foo/bar/baz', 'param1=bar&param3=baz', error_msgs[2]),
         ('/paramerrors/one_positional_kwargs/foo', 'param1=foo&param2=bar&param3=baz', error_msgs[2]),
         ('/paramerrors/no_positional', 'param1=foo', error_msgs[4]),
         ('/paramerrors/no_positional_args/boo', 'param1=foo', error_msgs[4]),
         ('/paramerrors/callable_object', 'param1=foo', error_msgs[4])):
            for show_mismatched_params in (True, False):
                cherrypy.config.update({'request.show_mismatched_params': show_mismatched_params})
                self.getPage(uri, method='POST', body=body)
                self.assertStatus(400)
                if show_mismatched_params:
                    self.assertInBody(msg)
                else:
                    self.assertInBody('Bad Request')


        for (uri, body, msg,) in (('/paramerrors/one_positional?param2=foo', 'param1=foo', error_msgs[3]),
         ('/paramerrors/one_positional/foo/bar', 'param2=foo', error_msgs[1]),
         ('/paramerrors/one_positional_args/foo/bar?param2=foo', 'param3=foo', error_msgs[3]),
         ('/paramerrors/one_positional_kwargs/foo/bar', 'param2=bar&param3=baz', error_msgs[1]),
         ('/paramerrors/no_positional?param1=foo', 'param2=foo', error_msgs[3]),
         ('/paramerrors/no_positional_args/boo?param2=foo', 'param1=foo', error_msgs[3]),
         ('/paramerrors/callable_object?param2=bar', 'param1=foo', error_msgs[3])):
            for show_mismatched_params in (True, False):
                cherrypy.config.update({'request.show_mismatched_params': show_mismatched_params})
                self.getPage(uri, method='POST', body=body)
                self.assertStatus(404)
                if show_mismatched_params:
                    self.assertInBody(msg)
                else:
                    self.assertInBody('Not Found')


        for uri in ('/paramerrors/raise_type_error', '/paramerrors/raise_type_error_with_default_param?x=0', '/paramerrors/raise_type_error_with_default_param?x=0&y=0'):
            self.getPage(uri, method='GET')
            self.assertStatus(500)
            self.assertTrue('Client Error', self.body)




    def testErrorHandling(self):
        self.getPage('/error/missing')
        self.assertStatus(404)
        self.assertErrorPage(404, "The path '/error/missing' was not found.")
        ignore = helper.webtest.ignored_exceptions
        ignore.append(ValueError)
        try:
            valerr = '\n    raise ValueError()\nValueError'
            self.getPage('/error/page_method')
            self.assertErrorPage(500, pattern=valerr)
            self.getPage('/error/page_yield')
            self.assertErrorPage(500, pattern=valerr)
            if cherrypy.server.protocol_version == 'HTTP/1.0' or getattr(cherrypy.server, 'using_apache', False):
                self.getPage('/error/page_streamed')
                self.assertStatus(200)
                self.assertBody('word up')
            else:
                self.assertRaises((ValueError, IncompleteRead), self.getPage, '/error/page_streamed')
            self.getPage('/error/cause_err_in_finalize')
            msg = "Illegal response status from server ('ZOO' is non-numeric)."
            self.assertErrorPage(500, msg, None)

        finally:
            ignore.pop()

        self.getPage('/error/reason_phrase')
        self.assertStatus("410 Gone fishin'")
        self.getPage('/error/custom')
        self.assertStatus(404)
        self.assertBody('Hello, world\r\n' + ' ' * 499)
        self.getPage('/error/custom?err=401')
        self.assertStatus(401)
        self.assertBody("Error 401 Unauthorized - Well, I'm very sorry but you haven't paid!")
        self.getPage('/error/custom_default')
        self.assertStatus(500)
        self.assertBody("Error 500 Internal Server Error - Well, I'm very sorry but you haven't paid!".ljust(513))
        self.getPage('/error/noexist')
        self.assertStatus(404)
        msg = "No, &lt;b&gt;really&lt;/b&gt;, not found!<br />In addition, the custom error page failed:\n<br />IOError: [Errno 2] No such file or directory: 'nonexistent.html'"
        self.assertInBody(msg)
        if getattr(cherrypy.server, 'using_apache', False):
            pass
        else:
            self.getPage('/error/rethrow')
            self.assertInBody('raise ValueError()')



    def testExpect(self):
        e = ('Expect', '100-continue')
        self.getPage('/headerelements/get_elements?headername=Expect', [e])
        self.assertBody('100-continue')
        self.getPage('/expect/expectation_failed', [e])
        self.assertStatus(417)



    def testHeaderElements(self):
        h = [('Accept', 'audio/*; q=0.2, audio/basic')]
        self.getPage('/headerelements/get_elements?headername=Accept', h)
        self.assertStatus(200)
        self.assertBody('audio/basic\naudio/*;q=0.2')
        h = [('Accept', 'text/plain; q=0.5, text/html, text/x-dvi; q=0.8, text/x-c')]
        self.getPage('/headerelements/get_elements?headername=Accept', h)
        self.assertStatus(200)
        self.assertBody('text/x-c\ntext/html\ntext/x-dvi;q=0.8\ntext/plain;q=0.5')
        h = [('Accept', 'text/*, text/html, text/html;level=1, */*')]
        self.getPage('/headerelements/get_elements?headername=Accept', h)
        self.assertStatus(200)
        self.assertBody('text/html;level=1\ntext/html\ntext/*\n*/*')
        h = [('Accept-Charset', 'iso-8859-5, unicode-1-1;q=0.8')]
        self.getPage('/headerelements/get_elements?headername=Accept-Charset', h)
        self.assertStatus('200 OK')
        self.assertBody('iso-8859-5\nunicode-1-1;q=0.8')
        h = [('Accept-Encoding', 'gzip;q=1.0, identity; q=0.5, *;q=0')]
        self.getPage('/headerelements/get_elements?headername=Accept-Encoding', h)
        self.assertStatus('200 OK')
        self.assertBody('gzip;q=1.0\nidentity;q=0.5\n*;q=0')
        h = [('Accept-Language', 'da, en-gb;q=0.8, en;q=0.7')]
        self.getPage('/headerelements/get_elements?headername=Accept-Language', h)
        self.assertStatus('200 OK')
        self.assertBody('da\nen-gb;q=0.8\nen;q=0.7')
        self.getPage('/headerelements/get_elements?headername=Content-Type', headers=[('Content-Type', 'text/html; charset=utf-8;')])
        self.assertStatus(200)
        self.assertBody('text/html;charset=utf-8')



    def test_repeated_headers(self):
        self.getPage('/headers/Accept-Charset', headers=[('Accept-Charset', 'iso-8859-5'), ('Accept-Charset', 'unicode-1-1;q=0.8')])
        self.assertBody('iso-8859-5, unicode-1-1;q=0.8')
        self.getPage('/headers/doubledheaders')
        self.assertBody('double header test')
        hnames = [ name.title() for (name, val,) in self.headers ]
        for key in ['Content-Length',
         'Content-Type',
         'Date',
         'Expires',
         'Location',
         'Server']:
            self.assertEqual(hnames.count(key), 1, self.headers)




    def test_encoded_headers(self):
        self.assertEqual(httputil.decode_TEXT(u'=?utf-8?q?f=C3=BCr?='), u'f\xfcr')
        if cherrypy.server.protocol_version == 'HTTP/1.1':
            u = u'\u212bngstr\xf6m'
            c = u'=E2=84=ABngstr=C3=B6m'
            self.getPage('/headers/ifmatch', [('If-Match', u'=?utf-8?q?%s?=' % c)])
            self.assertBody('\xe2\x84\xabngstr\xc3\xb6m')
            self.assertHeader('ETag', u'=?utf-8?b?4oSrbmdzdHLDtm0=?=')
            self.getPage('/headers/ifmatch', [('If-Match', u'=?utf-8?q?%s?=' % (c * 10))])
            self.assertBody('\xe2\x84\xabngstr\xc3\xb6m' * 10)
            etag = self.assertHeader('ETag', '=?utf-8?b?4oSrbmdzdHLDtm3ihKtuZ3N0csO2beKEq25nc3Ryw7Zt4oSrbmdzdHLDtm3ihKtuZ3N0csO2beKEq25nc3Ryw7Zt4oSrbmdzdHLDtm3ihKtuZ3N0csO2beKEq25nc3Ryw7Zt4oSrbmdzdHLDtm0=?=')
            self.assertEqual(httputil.decode_TEXT(etag), u * 10)



    def test_header_presence(self):
        self.getPage('/headers/Content-Type', headers=[])
        self.assertStatus(500)
        self.getPage('/headers/Content-Type', headers=[('Content-type', 'application/json')])
        self.assertBody('application/json')



    def test_basic_HTTPMethods(self):
        helper.webtest.methods_with_bodies = ('POST', 'PUT', 'PROPFIND')
        for m in defined_http_methods:
            self.getPage('/method/', method=m)
            if m == 'HEAD':
                self.assertBody('')
            elif m == 'TRACE':
                self.assertEqual(self.body[:5], 'TRACE')
            else:
                self.assertBody(m)

        self.getPage('/method/parameterized', method='PUT', body='data=on+top+of+other+things')
        self.assertBody('on top of other things')
        b = 'one thing on top of another'
        h = [('Content-Type', 'text/plain'), ('Content-Length', str(len(b)))]
        self.getPage('/method/request_body', headers=h, method='PUT', body=b)
        self.assertStatus(200)
        self.assertBody(b)
        b = 'one thing on top of another'
        self.persistent = True
        try:
            conn = self.HTTP_CONN
            conn.putrequest('PUT', '/method/request_body', skip_host=True)
            conn.putheader('Host', self.HOST)
            conn.putheader('Content-Length', str(len(b)))
            conn.endheaders()
            conn.send(b)
            response = conn.response_class(conn.sock, method='PUT')
            response.begin()
            self.assertEqual(response.status, 200)
            self.body = response.read()
            self.assertBody(b)

        finally:
            self.persistent = False

        h = [('Content-Type', 'text/plain')]
        self.getPage('/method/reachable', headers=h, method='PUT')
        self.assertStatus(411)
        b = '<?xml version="1.0" encoding="utf-8" ?>\n\n<propfind xmlns="DAV:"><prop><getlastmodified/></prop></propfind>'
        h = [('Content-Type', 'text/xml'), ('Content-Length', str(len(b)))]
        self.getPage('/method/request_body', headers=h, method='PROPFIND', body=b)
        self.assertStatus(200)
        self.assertBody(b)
        self.getPage('/method/', method='LINK')
        self.assertStatus(405)
        self.getPage('/method/', method='SEARCH')
        self.assertStatus(501)
        self.getPage('/divorce/get?ID=13')
        self.assertBody('Divorce document 13: empty')
        self.assertStatus(200)
        self.getPage('/divorce/', method='GET')
        self.assertBody('<h1>Choose your document</h1>\n<ul>\n</ul>')
        self.assertStatus(200)



    def test_CONNECT_method(self):
        if getattr(cherrypy.server, 'using_apache', False):
            return self.skip('skipped due to known Apache differences... ')
        self.getPage('/method/', method='CONNECT')
        self.assertBody('CONNECT')



    def testEmptyThreadlocals(self):
        results = []
        for x in xrange(20):
            self.getPage('/threadlocal/')
            results.append(self.body)

        self.assertEqual(results, ['None'] * 20)



if __name__ == '__main__':
    helper.testmain()

