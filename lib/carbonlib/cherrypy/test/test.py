import getopt
from httplib import HTTPSConnection
import os
localDir = os.path.dirname(__file__)
serverpem = os.path.join(os.getcwd(), localDir, 'test.pem')
import sys
import warnings
from cherrypy.lib import profiler

class TestHarness(object):

    def __init__(self, supervisor, tests, interactive = True):
        self.supervisor = supervisor
        self.tests = tests
        self.interactive = interactive



    def run(self, conf = None):
        import cherrypy
        v = sys.version.split()[0]
        print 'Python version used to run this test script: %s' % v
        print 'CherryPy version: %s' % cherrypy.__version__
        if self.supervisor.scheme == 'https':
            ssl = ' (ssl)'
        else:
            ssl = ''
        print 'HTTP server version: %s%s' % (self.supervisor.protocol, ssl)
        print 'PID: %s' % os.getpid()
        print ''
        cherrypy.server.using_apache = self.supervisor.using_apache
        cherrypy.server.using_wsgi = self.supervisor.using_wsgi
        if isinstance(conf, basestring):
            parser = cherrypy.config._Parser()
            conf = parser.dict_from_file(conf).get('global', {})
        else:
            conf = conf or {}
        baseconf = conf.copy()
        baseconf.update({'server.socket_host': self.supervisor.host,
         'server.socket_port': self.supervisor.port,
         'server.protocol_version': self.supervisor.protocol,
         'environment': 'test_suite'})
        if self.supervisor.scheme == 'https':
            baseconf['server.ssl_certificate'] = serverpem
            baseconf['server.ssl_private_key'] = serverpem
        from cherrypy.test import helper, webtest
        webtest.WebCase.interactive = self.interactive
        if self.supervisor.scheme == 'https':
            webtest.WebCase.HTTP_CONN = HTTPSConnection
        print ''
        print 'Running tests: %s' % self.supervisor
        return helper.run_test_suite(self.tests, baseconf, self.supervisor)




class Supervisor(object):

    def __init__(self, **kwargs):
        for (k, v,) in kwargs.iteritems():
            setattr(self, k, v)





class LocalSupervisor(Supervisor):
    using_apache = False
    using_wsgi = False

    def __init__(self, **kwargs):
        for (k, v,) in kwargs.iteritems():
            setattr(self, k, v)

        import cherrypy
        cherrypy.server.httpserver = self.httpserver_class
        engine = cherrypy.engine
        if hasattr(engine, 'signal_handler'):
            engine.signal_handler.subscribe()
        if hasattr(engine, 'console_control_handler'):
            engine.console_control_handler.subscribe()



    def start(self, modulename = None):
        import cherrypy
        if modulename:
            cherrypy.tree = cherrypy._cptree.Tree()
            cherrypy.server.httpserver = None
            cherrypy.tree = cherrypy._cptree.Tree()
            if '.' in modulename:
                (package, test_name,) = modulename.rsplit('.', 1)
                p = __import__(package, globals(), locals(), fromlist=[test_name])
                m = getattr(p, test_name)
            else:
                m = __import__(modulename, globals(), locals())
            setup = getattr(m, 'setup_server', None)
            if setup:
                setup()
            self.teardown = getattr(m, 'teardown_server', None)
        cherrypy.engine.start()
        self.sync_apps()



    def sync_apps(self):
        pass



    def stop(self):
        if self.teardown:
            self.teardown()
        import cherrypy
        cherrypy.engine.exit()




class NativeServerSupervisor(LocalSupervisor):
    httpserver_class = 'cherrypy._cpnative_server.CPHTTPServer'
    using_apache = False
    using_wsgi = False

    def __str__(self):
        return 'Builtin HTTP Server on %s:%s' % (self.host, self.port)




class LocalWSGISupervisor(LocalSupervisor):
    httpserver_class = 'cherrypy._cpwsgi_server.CPWSGIServer'
    using_apache = False
    using_wsgi = True

    def __str__(self):
        return 'Builtin WSGI Server on %s:%s' % (self.host, self.port)



    def sync_apps(self):
        import cherrypy
        cherrypy.server.httpserver.wsgi_app = self.get_app()



    def get_app(self):
        import cherrypy
        app = cherrypy.tree
        if self.profile:
            app = profiler.make_app(app, aggregate=False)
        if self.conquer:
            try:
                import wsgiconq
            except ImportError:
                warnings.warn('Error importing wsgiconq. pyconquer will not run.')
            else:
                app = wsgiconq.WSGILogger(app, c_calls=True)
        if self.validate:
            try:
                from wsgiref import validate
            except ImportError:
                warnings.warn('Error importing wsgiref. The validator will not run.')
            else:
                app = validate.validator(app)
        return app




def get_cpmodpy_supervisor(**options):
    from cherrypy.test import modpy
    sup = modpy.ModPythonSupervisor(**options)
    sup.template = modpy.conf_cpmodpy
    return sup



def get_modpygw_supervisor(**options):
    from cherrypy.test import modpy
    sup = modpy.ModPythonSupervisor(**options)
    sup.template = modpy.conf_modpython_gateway
    sup.using_wsgi = True
    return sup



def get_modwsgi_supervisor(**options):
    from cherrypy.test import modwsgi
    return modwsgi.ModWSGISupervisor(**options)



def get_modfcgid_supervisor(**options):
    from cherrypy.test import modfcgid
    return modfcgid.ModFCGISupervisor(**options)



def get_wsgi_u_supervisor(**options):
    import cherrypy
    cherrypy.server.wsgi_version = ('u', 0)
    return LocalWSGISupervisor(**options)



class CommandLineParser(object):
    available_servers = {'wsgi': LocalWSGISupervisor,
     'wsgi_u': get_wsgi_u_supervisor,
     'native': NativeServerSupervisor,
     'cpmodpy': get_cpmodpy_supervisor,
     'modpygw': get_modpygw_supervisor,
     'modwsgi': get_modwsgi_supervisor,
     'modfcgid': get_modfcgid_supervisor}
    default_server = 'wsgi'
    supervisor_factory = None
    supervisor_options = {'scheme': 'http',
     'protocol': 'HTTP/1.1',
     'port': 8080,
     'host': '127.0.0.1',
     'profile': False,
     'validate': False,
     'conquer': False}
    cover = False
    basedir = None
    interactive = True
    shortopts = []
    longopts = ['cover',
     'profile',
     'validate',
     'conquer',
     'dumb',
     '1.0',
     'ssl',
     'help',
     'basedir=',
     'port=',
     'server=',
     'host=']

    def __init__(self, available_tests, args = sys.argv[1:]):
        self.available_tests = available_tests
        self.supervisor_options = self.supervisor_options.copy()
        longopts = self.longopts[:]
        longopts.extend(self.available_tests)
        try:
            (opts, args,) = getopt.getopt(args, self.shortopts, longopts)
        except getopt.GetoptError:
            self.help()
            sys.exit(2)
        self.tests = []
        for (o, a,) in opts:
            if o == '--help':
                self.help()
                sys.exit()
            elif o == '--cover':
                self.cover = True
            elif o == '--profile':
                self.supervisor_options['profile'] = True
            elif o == '--validate':
                self.supervisor_options['validate'] = True
            elif o == '--conquer':
                self.supervisor_options['conquer'] = True
            elif o == '--dumb':
                self.interactive = False
            elif o == '--1.0':
                self.supervisor_options['protocol'] = 'HTTP/1.0'
            elif o == '--ssl':
                self.supervisor_options['scheme'] = 'https'
            elif o == '--basedir':
                self.basedir = a
            elif o == '--port':
                self.supervisor_options['port'] = int(a)
            elif o == '--host':
                self.supervisor_options['host'] = a
            elif o == '--server':
                if a not in self.available_servers:
                    print 'Error: The --server argument must be one of %s.' % '|'.join(self.available_servers.keys())
                    sys.exit(2)
                self.supervisor_factory = self.available_servers[a]
            else:
                o = o[2:]
                if o in self.available_tests and o not in self.tests:
                    self.tests.append(o)

        import cherrypy
        if self.cover and self.supervisor_options['profile']:
            print 'Error: you cannot run the profiler and the coverage tool at the same time.'
            sys.exit(2)
        if not self.supervisor_factory:
            self.supervisor_factory = self.available_servers[self.default_server]
        if not self.tests:
            self.tests = self.available_tests[:]



    def help(self):
        import cherrypy
        print 'CherryPy Test Program\n    Usage:\n        test.py --help --server=* --host=%s --port=%s --1.0 --ssl --cover\n            --basedir=path --profile --validate --conquer --dumb --tests**\n    ' % (self.__class__.supervisor_options['host'], self.__class__.supervisor_options['port'])
        print '    * servers:'
        for name in self.available_servers:
            if name == self.default_server:
                print '        --server=%s (default)' % name
            else:
                print '        --server=%s' % name

        print '\n    --host=<name or IP addr>: use a host other than the default (%s).\n        Not yet available with mod_python servers.\n    --port=<int>: use a port other than the default (%s).\n    --1.0: use HTTP/1.0 servers instead of default HTTP/1.1.\n    \n    --cover: turn on code-coverage tool.\n    --basedir=path: display coverage stats for some path other than cherrypy.\n    \n    --profile: turn on WSGI profiling tool.\n    --validate: use wsgiref.validate (builtin in Python 2.5).\n    --conquer: use wsgiconq (which uses pyconquer) to trace calls.\n    --dumb: turn off the interactive output features.\n    ' % (self.__class__.supervisor_options['host'], self.__class__.supervisor_options['port'])
        print '    ** tests:'
        for name in self.available_tests:
            print '        --' + name




    def start_coverage(self):
        try:
            from coverage import the_coverage as coverage
            c = os.path.join(os.path.dirname(__file__), '../lib/coverage.cache')
            coverage.cache_default = c
            if c and os.path.exists(c):
                os.remove(c)
            coverage.start()
            import cherrypy
            from cherrypy.lib import covercp
            cherrypy.engine.subscribe('start', covercp.start)
        except ImportError:
            coverage = None
        self.coverage = coverage



    def stop_coverage(self):
        import cherrypy
        from cherrypy.lib import covercp
        cherrypy.engine.unsubscribe('start', covercp.start)
        if self.coverage:
            self.coverage.save()
            self.report_coverage()
            print 'run cherrypy/lib/covercp.py as a script to serve coverage results on port 8080'



    def report_coverage(self):
        import cherrypy
        basedir = self.basedir
        if basedir is None:
            basedir = os.path.normpath(os.path.join(os.getcwd(), localDir, '../'))
        elif not os.path.isabs(basedir):
            basedir = os.path.normpath(os.path.join(os.getcwd(), basedir))
        basedir = basedir.lower()
        self.coverage.get_ready()
        morfs = [ x for x in self.coverage.cexecuted if x.lower().startswith(basedir) ]
        total_statements = 0
        total_executed = 0
        print ''
        sys.stdout.write('CODE COVERAGE (this might take a while)')
        for morf in morfs:
            sys.stdout.write('.')
            sys.stdout.flush()
            if morf.find('test') != -1:
                continue
            try:
                (_, statements, _, missing, readable,) = self.coverage.analysis2(morf)
                n = len(statements)
                m = n - len(missing)
                total_statements = total_statements + n
                total_executed = total_executed + m
            except KeyboardInterrupt:
                raise 
            except:
                pass

        pc = 100.0
        if total_statements > 0:
            pc = 100.0 * total_executed / total_statements
        print '\nTotal: %s Covered: %s Percent: %2d%%' % (total_statements, total_executed, pc)



    def run(self, conf = None):
        conf = conf or {}
        if self.cover:
            self.start_coverage()
        supervisor = self.supervisor_factory(**self.supervisor_options)
        if supervisor.using_apache and 'test_conn' in self.tests:
            self.tests.remove('test_conn')
        h = TestHarness(supervisor, self.tests, self.interactive)
        success = h.run(conf)
        if self.supervisor_options['profile']:
            print ''
            print 'run /cherrypy/lib/profiler.py as a script to serve profiling results on port 8080'
        if self.cover:
            self.stop_coverage()
        return success




def prefer_parent_path():
    curpath = os.path.normpath(os.path.join(os.getcwd(), localDir))
    grandparent = os.path.normpath(os.path.join(curpath, '../../'))
    if grandparent not in sys.path:
        sys.path.insert(0, grandparent)



def run():
    prefer_parent_path()
    testList = ['test_auth_basic',
     'test_auth_digest',
     'test_bus',
     'test_proxy',
     'test_caching',
     'test_config',
     'test_conn',
     'test_core',
     'test_tools',
     'test_encoding',
     'test_etags',
     'test_http',
     'test_httpauth',
     'test_httplib',
     'test_json',
     'test_logging',
     'test_objectmapping',
     'test_dynamicobjectmapping',
     'test_misc_tools',
     'test_request_obj',
     'test_static',
     'test_tutorials',
     'test_virtualhost',
     'test_mime',
     'test_session',
     'test_sessionauthenticate',
     'test_states',
     'test_config_server',
     'test_xmlrpc',
     'test_wsgiapps',
     'test_wsgi_ns',
     'test_wsgi_vhost',
     'test_refleaks']
    try:
        import routes
        testList.append('test_routes')
    except ImportError:
        pass
    clp = CommandLineParser(testList)
    success = clp.run()
    import cherrypy
    if clp.interactive:
        print ''
        raw_input('hit enter')
    sys.exit(success)


if __name__ == '__main__':
    run()

