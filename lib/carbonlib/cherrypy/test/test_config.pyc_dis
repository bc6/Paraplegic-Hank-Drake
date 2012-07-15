#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\test\test_config.py
import os, sys
localDir = os.path.join(os.getcwd(), os.path.dirname(__file__))
from cherrypy._cpcompat import ntob, StringIO
import unittest
import cherrypy

def setup_server():

    class Root:
        _cp_config = {'foo': 'this',
         'bar': 'that'}

        def __init__(self):
            cherrypy.config.namespaces['db'] = self.db_namespace

        def db_namespace(self, k, v):
            if k == 'scheme':
                self.db = v

        def index(self, key):
            return cherrypy.request.config.get(key, 'None')

        index = cherrypy.expose(index, alias=('global_', 'xyz'))

        def repr(self, key):
            return repr(cherrypy.request.config.get(key, None))

        repr.exposed = True

        def dbscheme(self):
            return self.db

        dbscheme.exposed = True

        def plain(self, x):
            return x

        plain.exposed = True
        plain._cp_config = {'request.body.attempt_charsets': ['utf-16']}
        favicon_ico = cherrypy.tools.staticfile.handler(filename=os.path.join(localDir, '../favicon.ico'))

    class Foo:
        _cp_config = {'foo': 'this2',
         'baz': 'that2'}

        def index(self, key):
            return cherrypy.request.config.get(key, 'None')

        index.exposed = True
        nex = index

        def silly(self):
            return 'Hello world'

        silly.exposed = True
        silly._cp_config = {'response.headers.X-silly': 'sillyval'}

        def bar(self, key):
            return repr(cherrypy.request.config.get(key, None))

        bar.exposed = True
        bar._cp_config = {'foo': 'this3',
         'bax': 'this4'}

    class Another:

        def index(self, key):
            return str(cherrypy.request.config.get(key, 'None'))

        index.exposed = True

    def raw_namespace(key, value):
        if key == 'input.map':
            handler = cherrypy.request.handler

            def wrapper():
                params = cherrypy.request.params
                for name, coercer in list(value.items()):
                    try:
                        params[name] = coercer(params[name])
                    except KeyError:
                        pass

                return handler()

            cherrypy.request.handler = wrapper
        elif key == 'output':
            handler = cherrypy.request.handler

            def wrapper():
                return value(handler())

            cherrypy.request.handler = wrapper

    class Raw:
        _cp_config = {'raw.output': repr}

        def incr(self, num):
            return num + 1

        incr.exposed = True
        incr._cp_config = {'raw.input.map': {'num': int}}

    ioconf = StringIO('\n[/]\nneg: -1234\nfilename: os.path.join(sys.prefix, "hello.py")\nthing1: cherrypy.lib.httputil.response_codes[404]\nthing2: __import__(\'cherrypy.tutorial\', globals(), locals(), [\'\']).thing2\ncomplex: 3+2j\nones: "11"\ntwos: "22"\nstradd: %%(ones)s + %%(twos)s + "33"\n\n[/favicon.ico]\ntools.staticfile.filename = %r\n' % os.path.join(localDir, 'static/dirback.jpg'))
    root = Root()
    root.foo = Foo()
    root.raw = Raw()
    app = cherrypy.tree.mount(root, config=ioconf)
    app.request_class.namespaces['raw'] = raw_namespace
    cherrypy.tree.mount(Another(), '/another')
    cherrypy.config.update({'luxuryyacht': 'throatwobblermangrove',
     'db.scheme': 'sqlite///memory'})


from cherrypy.test import helper

class ConfigTests(helper.CPWebCase):
    setup_server = staticmethod(setup_server)

    def testConfig(self):
        tests = [('/', 'nex', 'None'),
         ('/', 'foo', 'this'),
         ('/', 'bar', 'that'),
         ('/xyz', 'foo', 'this'),
         ('/foo/', 'foo', 'this2'),
         ('/foo/', 'bar', 'that'),
         ('/foo/', 'bax', 'None'),
         ('/foo/bar', 'baz', "'that2'"),
         ('/foo/nex', 'baz', 'that2'),
         ('/another/', 'foo', 'None')]
        for path, key, expected in tests:
            self.getPage(path + '?key=' + key)
            self.assertBody(expected)

        expectedconf = {'tools.log_headers.on': False,
         'tools.log_tracebacks.on': True,
         'request.show_tracebacks': True,
         'log.screen': False,
         'environment': 'test_suite',
         'engine.autoreload_on': False,
         'luxuryyacht': 'throatwobblermangrove',
         'bar': 'that',
         'baz': 'that2',
         'foo': 'this3',
         'bax': 'this4'}
        for key, expected in expectedconf.items():
            self.getPage('/foo/bar?key=' + key)
            self.assertBody(repr(expected))

    def testUnrepr(self):
        self.getPage('/repr?key=neg')
        self.assertBody('-1234')
        self.getPage('/repr?key=filename')
        self.assertBody(repr(os.path.join(sys.prefix, 'hello.py')))
        self.getPage('/repr?key=thing1')
        self.assertBody(repr(cherrypy.lib.httputil.response_codes[404]))
        if not getattr(cherrypy.server, 'using_apache', False):
            self.getPage('/repr?key=thing2')
            from cherrypy.tutorial import thing2
            self.assertBody(repr(thing2))
        self.getPage('/repr?key=complex')
        self.assertBody('(3+2j)')
        self.getPage('/repr?key=stradd')
        self.assertBody(repr('112233'))

    def testRespNamespaces(self):
        self.getPage('/foo/silly')
        self.assertHeader('X-silly', 'sillyval')
        self.assertBody('Hello world')

    def testCustomNamespaces(self):
        self.getPage('/raw/incr?num=12')
        self.assertBody('13')
        self.getPage('/dbscheme')
        self.assertBody('sqlite///memory')

    def testHandlerToolConfigOverride(self):
        self.getPage('/favicon.ico')
        self.assertBody(open(os.path.join(localDir, 'static/dirback.jpg'), 'rb').read())

    def test_request_body_namespace(self):
        self.getPage('/plain', method='POST', headers=[('Content-Type', 'application/x-www-form-urlencoded'), ('Content-Length', '13')], body=ntob('\xff\xfex\x00=\xff\xfea\x00b\x00c\x00'))
        self.assertBody('abc')


class VariableSubstitutionTests(unittest.TestCase):
    setup_server = staticmethod(setup_server)

    def test_config(self):
        from textwrap import dedent
        conf = dedent('\n        [DEFAULT]\n        dir = "/some/dir"\n        my.dir = %(dir)s + "/sub"\n\n        [my]\n        my.dir = %(dir)s + "/my/dir"\n        my.dir2 = %(my.dir)s + \'/dir2\'\n\n        ')
        fp = StringIO(conf)
        cherrypy.config.update(fp)
        self.assertEqual(cherrypy.config['my']['my.dir'], '/some/dir/my/dir')
        self.assertEqual(cherrypy.config['my']['my.dir2'], '/some/dir/my/dir/dir2')