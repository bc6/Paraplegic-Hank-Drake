import datetime
import os
thisdir = os.path.abspath(os.path.dirname(__file__))
import re
import sys
import time
import warnings
import cherrypy
from cherrypy.lib import httputil, profiler
from cherrypy.test import webtest

class CPWebCase(webtest.WebCase):
    script_name = ''
    scheme = 'http'

    def prefix(self):
        return self.script_name.rstrip('/')



    def base(self):
        if self.scheme == 'http' and self.PORT == 80 or self.scheme == 'https' and self.PORT == 443:
            port = ''
        else:
            port = ':%s' % self.PORT
        return '%s://%s%s%s' % (self.scheme,
         self.HOST,
         port,
         self.script_name.rstrip('/'))



    def exit(self):
        sys.exit()



    def getPage(self, url, headers = None, method = 'GET', body = None, protocol = None):
        if self.script_name:
            url = httputil.urljoin(self.script_name, url)
        return webtest.WebCase.getPage(self, url, headers, method, body, protocol)



    def skip(self, msg = 'skipped '):
        sys.stderr.write(msg)



    def assertErrorPage(self, status, message = None, pattern = ''):
        page = cherrypy._cperror.get_error_page(status, message=message)
        esc = re.escape
        epage = esc(page)
        epage = epage.replace(esc('<pre id="traceback"></pre>'), esc('<pre id="traceback">') + '(.*)' + esc('</pre>'))
        m = re.match(epage, self.body, re.DOTALL)
        if not m:
            self._handlewebError('Error page does not match; expected:\n' + page)
            return 
        if pattern is None:
            if m and m.group(1):
                self._handlewebError('Error page contains traceback')
        elif m is None or not re.search(re.escape(pattern), m.group(1)):
            msg = 'Error page does not contain %s in traceback'
            self._handlewebError(msg % repr(pattern))


    date_tolerance = 2

    def assertEqualDates(self, dt1, dt2, seconds = None):
        if seconds is None:
            seconds = self.date_tolerance
        if dt1 > dt2:
            diff = dt1 - dt2
        else:
            diff = dt2 - dt1
        if not diff < datetime.timedelta(seconds=seconds):
            raise AssertionError('%r and %r are not within %r seconds.' % (dt1, dt2, seconds))



CPTestLoader = webtest.ReloadingTestLoader()
CPTestRunner = webtest.TerseTestRunner(verbosity=2)

def run_test_suite(moduleNames, conf, supervisor):
    test_success = True
    for testmod in moduleNames:
        cherrypy.config.reset()
        cherrypy.config.update(conf)
        setup_client(supervisor)
        if '.' in testmod:
            (package, test_name,) = testmod.rsplit('.', 1)
            p = __import__(package, globals(), locals(), fromlist=[test_name])
            m = getattr(p, test_name)
        else:
            m = __import__(testmod, globals(), locals())
        suite = CPTestLoader.loadTestsFromName(testmod)
        setup = getattr(m, 'setup_server', None)
        if setup:
            supervisor.start(testmod)
        try:
            result = CPTestRunner.run(suite)
            test_success &= result.wasSuccessful()

        finally:
            if setup:
                supervisor.stop()


    if test_success:
        return 0
    else:
        return 1



def setup_client(supervisor):
    webtest.WebCase.PORT = cherrypy.server.socket_port
    webtest.WebCase.HOST = cherrypy.server.socket_host
    if cherrypy.server.ssl_certificate:
        CPWebCase.scheme = 'https'



def testmain(conf = None):
    cherrypy.config.update({'environment': 'test_suite'})
    cherrypy.server.socket_host = '127.0.0.1'
    from cherrypy.test.test import LocalWSGISupervisor
    supervisor = LocalWSGISupervisor(host=cherrypy.server.socket_host, port=cherrypy.server.socket_port)
    setup_client(supervisor)
    supervisor.start('__main__')
    try:
        return webtest.main()

    finally:
        supervisor.stop()




class CPProcess(object):
    pid_file = os.path.join(thisdir, 'test.pid')
    config_file = os.path.join(thisdir, 'test.conf')
    config_template = "[global]\nserver.socket_host: '%(host)s'\nserver.socket_port: %(port)s\nchecker.on: False\nlog.screen: False\nlog.error_file: r'%(error_log)s'\nlog.access_file: r'%(access_log)s'\n%(ssl)s\n%(extra)s\n"
    error_log = os.path.join(thisdir, 'test.error.log')
    access_log = os.path.join(thisdir, 'test.access.log')

    def __init__(self, wait = False, daemonize = False, ssl = False, socket_host = None, socket_port = None):
        self.wait = wait
        self.daemonize = daemonize
        self.ssl = ssl
        self.host = socket_host or cherrypy.server.socket_host
        self.port = socket_port or cherrypy.server.socket_port



    def write_conf(self, extra = ''):
        if self.ssl:
            serverpem = os.path.join(thisdir, 'test.pem')
            ssl = "\nserver.ssl_certificate: r'%s'\nserver.ssl_private_key: r'%s'\n" % (serverpem, serverpem)
        else:
            ssl = ''
        conf = self.config_template % {'host': self.host,
         'port': self.port,
         'error_log': self.error_log,
         'access_log': self.access_log,
         'ssl': ssl,
         'extra': extra}
        f = open(self.config_file, 'wb')
        f.write(conf)
        f.close()



    def start(self, imports = None):
        cherrypy._cpserver.wait_for_free_port(self.host, self.port)
        args = [sys.executable,
         os.path.join(thisdir, '..', 'cherryd'),
         '-c',
         self.config_file,
         '-p',
         self.pid_file]
        if not isinstance(imports, (list, tuple)):
            imports = [imports]
        for i in imports:
            if i:
                args.append('-i')
                args.append(i)

        if self.daemonize:
            args.append('-d')
        if self.wait:
            self.exit_code = os.spawnl(os.P_WAIT, sys.executable, *args)
        else:
            os.spawnl(os.P_NOWAIT, sys.executable, *args)
            cherrypy._cpserver.wait_for_occupied_port(self.host, self.port)
        if self.daemonize:
            time.sleep(2)
        else:
            time.sleep(1)



    def get_pid(self):
        return int(open(self.pid_file, 'rb').read())



    def join(self):
        try:
            try:
                os.wait()
            except AttributeError:
                try:
                    pid = self.get_pid()
                except IOError:
                    pass
                else:
                    os.waitpid(pid, 0)
        except OSError as x:
            if x.args != (10, 'No child processes'):
                raise 




