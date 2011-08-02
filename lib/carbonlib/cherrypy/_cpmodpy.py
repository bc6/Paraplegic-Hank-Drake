import logging
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import cherrypy
from cherrypy._cperror import format_exc, bare_error
from cherrypy.lib import httputil

def setup(req):
    from mod_python import apache
    options = req.get_options()
    if 'cherrypy.setup' in options:
        for function in options['cherrypy.setup'].split():
            atoms = function.split('::', 1)
            if len(atoms) == 1:
                mod = __import__(atoms[0], globals(), locals())
            else:
                (modname, fname,) = atoms
                mod = __import__(modname, globals(), locals(), [fname])
                func = getattr(mod, fname)
                func()

    cherrypy.config.update({'log.screen': False,
     'tools.ignore_headers.on': True,
     'tools.ignore_headers.headers': ['Range']})
    engine = cherrypy.engine
    if hasattr(engine, 'signal_handler'):
        engine.signal_handler.unsubscribe()
    if hasattr(engine, 'console_control_handler'):
        engine.console_control_handler.unsubscribe()
    engine.autoreload.unsubscribe()
    cherrypy.server.unsubscribe()

    def _log(msg, level):
        newlevel = apache.APLOG_ERR
        if logging.DEBUG >= level:
            newlevel = apache.APLOG_DEBUG
        elif logging.INFO >= level:
            newlevel = apache.APLOG_INFO
        elif logging.WARNING >= level:
            newlevel = apache.APLOG_WARNING
        apache.log_error(msg, newlevel, req.server)


    engine.subscribe('log', _log)
    engine.start()

    def cherrypy_cleanup(data):
        engine.exit()


    try:
        apache.register_cleanup(cherrypy_cleanup)
    except AttributeError:
        req.server.register_cleanup(req, cherrypy_cleanup)



class _ReadOnlyRequest:
    expose = ('read', 'readline', 'readlines')

    def __init__(self, req):
        for method in self.expose:
            self.__dict__[method] = getattr(req, method)




recursive = False
_isSetUp = False

def handler(req):
    global _isSetUp
    from mod_python import apache
    try:
        if not _isSetUp:
            setup(req)
            _isSetUp = True
        local = req.connection.local_addr
        local = httputil.Host(local[0], local[1], req.connection.local_host or '')
        remote = req.connection.remote_addr
        remote = httputil.Host(remote[0], remote[1], req.connection.remote_host or '')
        scheme = req.parsed_uri[0] or 'http'
        req.get_basic_auth_pw()
        try:
            q = apache.mpm_query
            threaded = q(apache.AP_MPMQ_IS_THREADED)
            forked = q(apache.AP_MPMQ_IS_FORKED)
        except AttributeError:
            bad_value = "You must provide a PythonOption '%s', either 'on' or 'off', when running a version of mod_python < 3.1"
            threaded = options.get('multithread', '').lower()
            if threaded == 'on':
                threaded = True
            elif threaded == 'off':
                threaded = False
            else:
                raise ValueError(bad_value % 'multithread')
            forked = options.get('multiprocess', '').lower()
            if forked == 'on':
                forked = True
            elif forked == 'off':
                forked = False
            else:
                raise ValueError(bad_value % 'multiprocess')
        sn = cherrypy.tree.script_name(req.uri or '/')
        if sn is None:
            send_response(req, '404 Not Found', [], '')
        else:
            app = cherrypy.tree.apps[sn]
            method = req.method
            path = req.uri
            qs = req.args or ''
            reqproto = req.protocol
            headers = req.headers_in.items()
            rfile = _ReadOnlyRequest(req)
            prev = None
            try:
                redirections = []
                while True:
                    (request, response,) = app.get_serving(local, remote, scheme, 'HTTP/1.1')
                    request.login = req.user
                    request.multithread = bool(threaded)
                    request.multiprocess = bool(forked)
                    request.app = app
                    request.prev = prev
                    try:
                        request.run(method, path, qs, reqproto, headers, rfile)
                        break
                    except cherrypy.InternalRedirect as ir:
                        app.release_serving()
                        prev = request
                        if not recursive:
                            if ir.path in redirections:
                                raise RuntimeError('InternalRedirector visited the same URL twice: %r' % ir.path)
                            elif qs:
                                qs = '?' + qs
                            redirections.append(sn + path + qs)
                        method = 'GET'
                        path = ir.path
                        qs = ir.query_string
                        rfile = StringIO()

                send_response(req, response.status, response.header_list, response.body, response.stream)

            finally:
                app.release_serving()

    except:
        tb = format_exc()
        cherrypy.log(tb, 'MOD_PYTHON', severity=logging.ERROR)
        (s, h, b,) = bare_error()
        send_response(req, s, h, b)
    return apache.OK



def send_response(req, status, headers, body, stream = False):
    req.status = int(status[:3])
    req.content_type = 'text/plain'
    for (header, value,) in headers:
        if header.lower() == 'content-type':
            req.content_type = value
            continue
        req.headers_out.add(header, value)

    if stream:
        req.flush()
    if isinstance(body, basestring):
        req.write(body)
    else:
        for seg in body:
            req.write(seg)



import os
import re

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



class ModPythonServer(object):
    template = '\n# Apache2 server configuration file for running CherryPy with mod_python.\n\nDocumentRoot "/"\nListen %(port)s\nLoadModule python_module modules/mod_python.so\n\n<Location %(loc)s>\n    SetHandler python-program\n    PythonHandler %(handler)s\n    PythonDebug On\n%(opts)s\n</Location>\n'

    def __init__(self, loc = '/', port = 80, opts = None, apache_path = 'apache', handler = 'cherrypy._cpmodpy::handler'):
        self.loc = loc
        self.port = port
        self.opts = opts
        self.apache_path = apache_path
        self.handler = handler



    def start(self):
        opts = ''.join([ '    PythonOption %s %s\n' % (k, v) for (k, v,) in self.opts ])
        conf_data = self.template % {'port': self.port,
         'loc': self.loc,
         'opts': opts,
         'handler': self.handler}
        mpconf = os.path.join(os.path.dirname(__file__), 'cpmodpy.conf')
        f = open(mpconf, 'wb')
        try:
            f.write(conf_data)

        finally:
            f.close()

        response = read_process(self.apache_path, '-k start -f %s' % mpconf)
        self.ready = True
        return response



    def stop(self):
        os.popen('apache -k stop')
        self.ready = False




