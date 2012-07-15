#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\test\modfastcgi.py
import os
curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
import re
import sys
import time
import cherrypy
from cherrypy.process import plugins, servers
from cherrypy.test import helper

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


APACHE_PATH = 'apache2ctl'
CONF_PATH = 'fastcgi.conf'
conf_fastcgi = '\n# Apache2 server conf file for testing CherryPy with mod_fastcgi.\n# fumanchu: I had to hard-code paths due to crazy Debian layouts :(\nServerRoot /usr/lib/apache2\nUser #1000\nErrorLog %(root)s/mod_fastcgi.error.log\n\nDocumentRoot "%(root)s"\nServerName 127.0.0.1\nListen %(port)s\nLoadModule fastcgi_module modules/mod_fastcgi.so\nLoadModule rewrite_module modules/mod_rewrite.so\n\nOptions +ExecCGI\nSetHandler fastcgi-script\nRewriteEngine On\nRewriteRule ^(.*)$ /fastcgi.pyc [L]\nFastCgiExternalServer "%(server)s" -host 127.0.0.1:4000\n'

def erase_script_name(environ, start_response):
    environ['SCRIPT_NAME'] = ''
    return cherrypy.tree(environ, start_response)


class ModFCGISupervisor(helper.LocalWSGISupervisor):
    httpserver_class = 'cherrypy.process.servers.FlupFCGIServer'
    using_apache = True
    using_wsgi = True
    template = conf_fastcgi

    def __str__(self):
        return 'FCGI Server on %s:%s' % (self.host, self.port)

    def start(self, modulename):
        cherrypy.server.httpserver = servers.FlupFCGIServer(application=erase_script_name, bindAddress=('127.0.0.1', 4000))
        cherrypy.server.httpserver.bind_addr = ('127.0.0.1', 4000)
        cherrypy.server.socket_port = 4000
        self.start_apache()
        cherrypy.engine.start()
        self.sync_apps()

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
        helper.LocalWSGISupervisor.stop(self)

    def sync_apps(self):
        cherrypy.server.httpserver.fcgiserver.application = self.get_app(erase_script_name)