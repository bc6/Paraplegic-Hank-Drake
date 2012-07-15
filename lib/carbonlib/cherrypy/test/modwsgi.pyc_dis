#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\test\modwsgi.py
import os
curdir = os.path.abspath(os.path.dirname(__file__))
import re
import sys
import time
import cherrypy
from cherrypy.test import helper, webtest

def read_process(cmd, args = ''):
    pipein, pipeout = os.popen4('%s %s' % (cmd, args))
    try:
        firstline = pipeout.readline()
        if re.search('(not recognized|No such file|not found)', firstline, re.IGNORECASE):
            raise IOError('%s must be on your system path.' % cmd)
        output = firstline + pipeout.read()
    finally:
        pipeout.close()

    return output


if sys.platform == 'win32':
    APACHE_PATH = 'httpd'
else:
    APACHE_PATH = 'apache'
CONF_PATH = 'test_mw.conf'
conf_modwsgi = '\n# Apache2 server conf file for testing CherryPy with modpython_gateway.\n\nServerName 127.0.0.1\nDocumentRoot "/"\nListen %(port)s\n\nAllowEncodedSlashes On\nLoadModule rewrite_module modules/mod_rewrite.so\nRewriteEngine on\nRewriteMap escaping int:escape\n\nLoadModule log_config_module modules/mod_log_config.so\nLogFormat "%%h %%l %%u %%t \\"%%r\\" %%>s %%b \\"%%{Referer}i\\" \\"%%{User-agent}i\\"" combined\nCustomLog "%(curdir)s/apache.access.log" combined\nErrorLog "%(curdir)s/apache.error.log"\nLogLevel debug\n\nLoadModule wsgi_module modules/mod_wsgi.so\nLoadModule env_module modules/mod_env.so\n\nWSGIScriptAlias / "%(curdir)s/modwsgi.py"\nSetEnv testmod %(testmod)s\n'

class ModWSGISupervisor(helper.Supervisor):
    using_apache = True
    using_wsgi = True
    template = conf_modwsgi

    def __str__(self):
        return 'ModWSGI Server on %s:%s' % (self.host, self.port)

    def start(self, modulename):
        mpconf = CONF_PATH
        if not os.path.isabs(mpconf):
            mpconf = os.path.join(curdir, mpconf)
        f = open(mpconf, 'wb')
        try:
            output = self.template % {'port': self.port,
             'testmod': modulename,
             'curdir': curdir}
            f.write(output)
        finally:
            f.close()

        result = read_process(APACHE_PATH, '-k start -f %s' % mpconf)
        if result:
            print result
        cherrypy._cpserver.wait_for_occupied_port('127.0.0.1', self.port)
        webtest.openURL('/ihopetheresnodefault', port=self.port)
        time.sleep(1)

    def stop(self):
        read_process(APACHE_PATH, '-k stop')


loaded = False

def application(environ, start_response):
    global loaded
    import cherrypy
    if not loaded:
        loaded = True
        modname = 'cherrypy.test.' + environ['testmod']
        mod = __import__(modname, globals(), locals(), [''])
        mod.setup_server()
        cherrypy.config.update({'log.error_file': os.path.join(curdir, 'test.error.log'),
         'log.access_file': os.path.join(curdir, 'test.access.log'),
         'environment': 'test_suite',
         'engine.SIGHUP': None,
         'engine.SIGTERM': None})
    return cherrypy.tree(environ, start_response)