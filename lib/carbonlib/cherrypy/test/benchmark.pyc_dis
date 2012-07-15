#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\test\benchmark.py
import getopt
import os
curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
import re
import sys
import time
import traceback
import cherrypy
from cherrypy._cpcompat import ntob
from cherrypy import _cperror, _cpmodpy
from cherrypy.lib import httputil
AB_PATH = ''
APACHE_PATH = 'apache'
SCRIPT_NAME = '/cpbench/users/rdelon/apps/blog'
__all__ = ['ABSession',
 'Root',
 'print_report',
 'run_standard_benchmarks',
 'safe_threads',
 'size_report',
 'startup',
 'thread_report']
size_cache = {}

class Root:

    def index(self):
        return '<html>\n<head>\n    <title>CherryPy Benchmark</title>\n</head>\n<body>\n    <ul>\n        <li><a href="hello">Hello, world! (14 byte dynamic)</a></li>\n        <li><a href="static/index.html">Static file (14 bytes static)</a></li>\n        <li><form action="sizer">Response of length:\n            <input type=\'text\' name=\'size\' value=\'10\' /></form>\n        </li>\n    </ul>\n</body>\n</html>'

    index.exposed = True

    def hello(self):
        return 'Hello, world\r\n'

    hello.exposed = True

    def sizer(self, size):
        resp = size_cache.get(size, None)
        if resp is None:
            size_cache[size] = resp = 'X' * int(size)
        return resp

    sizer.exposed = True


cherrypy.config.update({'log.error.file': '',
 'environment': 'production',
 'server.socket_host': '127.0.0.1',
 'server.socket_port': 8080,
 'server.max_request_header_size': 0,
 'server.max_request_body_size': 0,
 'engine.deadlock_poll_freq': 0})
del cherrypy.config['tools.log_tracebacks.on']
del cherrypy.config['tools.log_headers.on']
del cherrypy.config['tools.trailing_slash.on']
appconf = {'/static': {'tools.staticdir.on': True,
             'tools.staticdir.dir': 'static',
             'tools.staticdir.root': curdir}}
app = cherrypy.tree.mount(Root(), SCRIPT_NAME, appconf)

class NullRequest:

    def __init__(self, local, remote, scheme = 'http'):
        pass

    def close(self):
        pass

    def run(self, method, path, query_string, protocol, headers, rfile):
        cherrypy.response.status = '200 OK'
        cherrypy.response.header_list = [('Content-Type', 'text/html'),
         ('Server', 'Null CherryPy'),
         ('Date', httputil.HTTPDate()),
         ('Content-Length', '0')]
        cherrypy.response.body = ['']
        return cherrypy.response


class NullResponse:
    pass


class ABSession:
    parse_patterns = [('complete_requests', 'Completed', ntob('^Complete requests:\\s*(\\d+)')),
     ('failed_requests', 'Failed', ntob('^Failed requests:\\s*(\\d+)')),
     ('requests_per_second', 'req/sec', ntob('^Requests per second:\\s*([0-9.]+)')),
     ('time_per_request_concurrent', 'msec/req', ntob('^Time per request:\\s*([0-9.]+).*concurrent requests\\)$')),
     ('transfer_rate', 'KB/sec', ntob('^Transfer rate:\\s*([0-9.]+)'))]

    def __init__(self, path = SCRIPT_NAME + '/hello', requests = 1000, concurrency = 10):
        self.path = path
        self.requests = requests
        self.concurrency = concurrency

    def args(self):
        port = cherrypy.server.socket_port
        return '-k -n %s -c %s http://127.0.0.1:%s%s' % (self.requests,
         self.concurrency,
         port,
         self.path)

    def run(self):
        global AB_PATH
        try:
            self.output = _cpmodpy.read_process(AB_PATH or 'ab', self.args())
        except:
            print _cperror.format_exc()
            raise 

        for attr, name, pattern in self.parse_patterns:
            val = re.search(pattern, self.output, re.MULTILINE)
            if val:
                val = val.group(1)
                setattr(self, attr, val)
            else:
                setattr(self, attr, None)


safe_threads = (25, 50, 100, 200, 400)
if sys.platform in ('win32',):
    safe_threads = (10, 20, 30, 40, 50)

def thread_report(path = SCRIPT_NAME + '/hello', concurrency = safe_threads):
    sess = ABSession(path)
    attrs, names, patterns = list(zip(*sess.parse_patterns))
    avg = dict.fromkeys(attrs, 0.0)
    yield ('threads',) + names
    for c in concurrency:
        sess.concurrency = c
        sess.run()
        row = [c]
        for attr in attrs:
            val = getattr(sess, attr)
            if val is None:
                print sess.output
                row = None
                break
            val = float(val)
            avg[attr] += float(val)
            row.append(val)

        if row:
            yield row

    yield ['Average'] + [ str(avg[attr] / len(concurrency)) for attr in attrs ]


def size_report(sizes = (10, 100, 1000, 10000, 100000, 100000000), concurrency = 50):
    sess = ABSession(concurrency=concurrency)
    attrs, names, patterns = list(zip(*sess.parse_patterns))
    yield ('bytes',) + names
    for sz in sizes:
        sess.path = '%s/sizer?size=%s' % (SCRIPT_NAME, sz)
        sess.run()
        yield [sz] + [ getattr(sess, attr) for attr in attrs ]


def print_report(rows):
    for row in rows:
        print ''
        for i, val in enumerate(row):
            sys.stdout.write(str(val).rjust(10) + ' | ')

    print ''


def run_standard_benchmarks():
    print ''
    print 'Client Thread Report (1000 requests, 14 byte response body, %s server threads):' % cherrypy.server.thread_pool
    print_report(thread_report())
    print ''
    print 'Client Thread Report (1000 requests, 14 bytes via staticdir, %s server threads):' % cherrypy.server.thread_pool
    print_report(thread_report('%s/static/index.html' % SCRIPT_NAME))
    print ''
    print 'Size Report (1000 requests, 50 client threads, %s server threads):' % cherrypy.server.thread_pool
    print_report(size_report())


def startup_modpython(req = None):
    global AB_PATH
    if cherrypy.engine.state == cherrypy._cpengine.STOPPED:
        if req:
            if 'nullreq' in req.get_options():
                cherrypy.engine.request_class = NullRequest
                cherrypy.engine.response_class = NullResponse
            ab_opt = req.get_options().get('ab', '')
            if ab_opt:
                AB_PATH = ab_opt
        cherrypy.engine.start()
    if cherrypy.engine.state == cherrypy._cpengine.STARTING:
        cherrypy.engine.wait()
    return 0


def run_modpython(use_wsgi = False):
    print 'Starting mod_python...'
    pyopts = []
    if '--null' in opts:
        pyopts.append(('nullreq', ''))
    if '--ab' in opts:
        pyopts.append(('ab', opts['--ab']))
    s = _cpmodpy.ModPythonServer
    if use_wsgi:
        pyopts.append(('wsgi.application', 'cherrypy::tree'))
        pyopts.append(('wsgi.startup', 'cherrypy.test.benchmark::startup_modpython'))
        handler = 'modpython_gateway::handler'
        s = s(port=8080, opts=pyopts, apache_path=APACHE_PATH, handler=handler)
    else:
        pyopts.append(('cherrypy.setup', 'cherrypy.test.benchmark::startup_modpython'))
        s = s(port=8080, opts=pyopts, apache_path=APACHE_PATH)
    try:
        s.start()
        run()
    finally:
        s.stop()


if __name__ == '__main__':
    longopts = ['cpmodpy',
     'modpython',
     'null',
     'notests',
     'help',
     'ab=',
     'apache=']
    try:
        switches, args = getopt.getopt(sys.argv[1:], '', longopts)
        opts = dict(switches)
    except getopt.GetoptError:
        print __doc__
        sys.exit(2)

    if '--help' in opts:
        print __doc__
        sys.exit(0)
    if '--ab' in opts:
        AB_PATH = opts['--ab']
    if '--notests' in opts:

        def run():
            port = cherrypy.server.socket_port
            print 'You may now open http://127.0.0.1:%s%s/' % (port, SCRIPT_NAME)
            if '--null' in opts:
                print 'Using null Request object'


    else:

        def run():
            end = time.time() - start
            print 'Started in %s seconds' % end
            if '--null' in opts:
                print '\nUsing null Request object'
            try:
                run_standard_benchmarks()
            except:
                print _cperror.format_exc()
                raise 
            finally:
                cherrypy.engine.exit()


    print 'Starting CherryPy app server...'

    class NullWriter(object):

        def write(self, data):
            pass


    sys.stderr = NullWriter()
    start = time.time()
    if '--cpmodpy' in opts:
        run_modpython()
    elif '--modpython' in opts:
        run_modpython(use_wsgi=True)
    else:
        if '--null' in opts:
            cherrypy.server.request_class = NullRequest
            cherrypy.server.response_class = NullResponse
        cherrypy.engine.start_with_callback(run)
        cherrypy.engine.block()