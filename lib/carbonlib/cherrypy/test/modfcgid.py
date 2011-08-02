import os
curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
import re
import sys
import time
import cherrypy
from cherrypy.process import plugins, servers
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
CONF_PATH = 'fcgi.conf'
conf_fcgid = '\n# Apache2 server conf file for testing CherryPy with mod_fcgid.\n\nDocumentRoot "%(root)s"\nServerName 127.0.0.1\nListen %(port)s\nLoadModule fastcgi_module modules/mod_fastcgi.dll\nLoadModule rewrite_module modules/mod_rewrite.so\n\nOptions ExecCGI\nSetHandler fastcgi-script\nRewriteEngine On\nRewriteRule ^(.*)$ /fastcgi.pyc [L]\nFastCgiExternalServer "%(server)s" -host 127.0.0.1:4000\n'

class ModFCGISupervisor(test.LocalSupervisor):
    using_apache = True
    using_wsgi = True
    template = conf_fcgid

    def __str__(self):
        return 'FCGI Server on %s:%s' % (self.host, self.port)



    def start(self, modulename):
        cherrypy.server.httpserver = servers.FlupFCGIServer(application=cherrypy.tree, bindAddress=('127.0.0.1', 4000))
        cherrypy.server.httpserver.bind_addr = ('127.0.0.1', 4000)
        self.start_apache()
        test.LocalServer.start(self, modulename)



    def start_apache(self):
        fcgiconf = CONF_PATH
        if not os.path.isabs(fcgiconf):
            fcgiconf = os.path.join(curdir, fcgiconf)
        f = open(fcgiconf, 'wb')
        try:
            server = repr(os.path.join(curdir, 'fastcgi.pyc'))[1:-1]
            output = self.template % {'port': self.port,
             'root': curdir,
             'server': server}
            output = output.replace('\r\n', '\n')
            f.write(output)

        finally:
            f.close()

        result = read_process(APACHE_PATH, '-k start -f %s' % fcgiconf)
        if result:
            print result



    def stop(self):
        read_process(APACHE_PATH, '-k stop')
        test.LocalServer.stop(self)



    def sync_apps(self):
        cherrypy.server.httpserver.fcgiserver.application = self.get_app()




