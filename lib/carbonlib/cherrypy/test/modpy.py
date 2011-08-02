import os
curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
import re
import time
from cherrypy.test import test

def read_process(cmd, args = ''):
    (pipein, pipeout,) = os.popen4('%s %s' % (cmd, args))
    try:
        firstline = pipeout.readline()
        if re.search('(not recognized|No such file|not found)', firstline, re.IGNORECASE):
            raise IOError('%s must be on your system path.' % cmd)
        output = firstline + pipeout.read()

    finally:
        pipeout.close()

    return output


APACHE_PATH = 'httpd'
CONF_PATH = 'test_mp.conf'
conf_modpython_gateway = '\n# Apache2 server conf file for testing CherryPy with modpython_gateway.\n\nServerName 127.0.0.1\nDocumentRoot "/"\nListen %(port)s\nLoadModule python_module modules/mod_python.so\n\nSetHandler python-program\nPythonFixupHandler cherrypy.test.modpy::wsgisetup\nPythonOption testmod %(modulename)s\nPythonHandler modpython_gateway::handler\nPythonOption wsgi.application cherrypy::tree\nPythonOption socket_host %(host)s\nPythonDebug On\n'
conf_cpmodpy = '\n# Apache2 server conf file for testing CherryPy with _cpmodpy.\n\nServerName 127.0.0.1\nDocumentRoot "/"\nListen %(port)s\nLoadModule python_module modules/mod_python.so\n\nSetHandler python-program\nPythonFixupHandler cherrypy.test.modpy::cpmodpysetup\nPythonHandler cherrypy._cpmodpy::handler\nPythonOption cherrypy.setup cherrypy.test.%(modulename)s::setup_server\nPythonOption socket_host %(host)s\nPythonDebug On\n'

class ModPythonSupervisor(test.Supervisor):
    using_apache = True
    using_wsgi = False
    template = None

    def __str__(self):
        return 'ModPython Server on %s:%s' % (self.host, self.port)



    def start(self, modulename):
        mpconf = CONF_PATH
        if not os.path.isabs(mpconf):
            mpconf = os.path.join(curdir, mpconf)
        f = open(mpconf, 'wb')
        try:
            f.write(self.template % {'port': self.port,
             'modulename': modulename,
             'host': self.host})

        finally:
            f.close()

        result = read_process(APACHE_PATH, '-k start -f %s' % mpconf)
        if result:
            print result



    def stop(self):
        read_process(APACHE_PATH, '-k stop')



loaded = False

def wsgisetup(req):
    global loaded
    if not loaded:
        loaded = True
        options = req.get_options()
        import cherrypy
        cherrypy.config.update({'log.error_file': os.path.join(curdir, 'test.log'),
         'environment': 'test_suite',
         'server.socket_host': options['socket_host']})
        modname = options['testmod']
        mod = __import__(modname, globals(), locals(), [''])
        mod.setup_server()
        cherrypy.server.unsubscribe()
        cherrypy.engine.start()
    from mod_python import apache
    return apache.OK



def cpmodpysetup(req):
    global loaded
    if not loaded:
        loaded = True
        options = req.get_options()
        import cherrypy
        cherrypy.config.update({'log.error_file': os.path.join(curdir, 'test.log'),
         'environment': 'test_suite',
         'server.socket_host': options['socket_host']})
    from mod_python import apache
    return apache.OK



