#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\_cptree.py
import os
import cherrypy
from cherrypy._cpcompat import ntou
from cherrypy import _cpconfig, _cplogging, _cprequest, _cpwsgi, tools
from cherrypy.lib import httputil

class Application(object):
    root = None
    config = {}
    namespaces = _cpconfig.NamespaceSet()
    toolboxes = {'tools': cherrypy.tools}
    log = None
    wsgiapp = None
    request_class = _cprequest.Request
    response_class = _cprequest.Response
    relative_urls = False

    def __init__(self, root, script_name = '', config = None):
        self.log = _cplogging.LogManager(id(self), cherrypy.log.logger_root)
        self.root = root
        self.script_name = script_name
        self.wsgiapp = _cpwsgi.CPWSGIApp(self)
        self.namespaces = self.namespaces.copy()
        self.namespaces['log'] = lambda k, v: setattr(self.log, k, v)
        self.namespaces['wsgi'] = self.wsgiapp.namespace_handler
        self.config = self.__class__.config.copy()
        if config:
            self.merge(config)

    def __repr__(self):
        return '%s.%s(%r, %r)' % (self.__module__,
         self.__class__.__name__,
         self.root,
         self.script_name)

    script_name_doc = 'The URI "mount point" for this app. A mount point is that portion of\n    the URI which is constant for all URIs that are serviced by this\n    application; it does not include scheme, host, or proxy ("virtual host")\n    portions of the URI.\n    \n    For example, if script_name is "/my/cool/app", then the URL\n    "http://www.example.com/my/cool/app/page1" might be handled by a\n    "page1" method on the root object.\n    \n    The value of script_name MUST NOT end in a slash. If the script_name\n    refers to the root of the URI, it MUST be an empty string (not "/").\n    \n    If script_name is explicitly set to None, then the script_name will be\n    provided for each call from request.wsgi_environ[\'SCRIPT_NAME\'].\n    '

    def _get_script_name(self):
        if self._script_name is None:
            return cherrypy.serving.request.wsgi_environ['SCRIPT_NAME'].rstrip('/')
        return self._script_name

    def _set_script_name(self, value):
        if value:
            value = value.rstrip('/')
        self._script_name = value

    script_name = property(fget=_get_script_name, fset=_set_script_name, doc=script_name_doc)

    def merge(self, config):
        _cpconfig.merge(self.config, config)
        self.namespaces(self.config.get('/', {}))

    def find_config(self, path, key, default = None):
        trail = path or '/'
        while trail:
            nodeconf = self.config.get(trail, {})
            if key in nodeconf:
                return nodeconf[key]
            lastslash = trail.rfind('/')
            if lastslash == -1:
                break
            elif lastslash == 0 and trail != '/':
                trail = '/'
            else:
                trail = trail[:lastslash]

        return default

    def get_serving(self, local, remote, scheme, sproto):
        req = self.request_class(local, remote, scheme, sproto)
        req.app = self
        for name, toolbox in self.toolboxes.items():
            req.namespaces[name] = toolbox

        resp = self.response_class()
        cherrypy.serving.load(req, resp)
        cherrypy.engine.timeout_monitor.acquire()
        cherrypy.engine.publish('acquire_thread')
        return (req, resp)

    def release_serving(self):
        req = cherrypy.serving.request
        cherrypy.engine.timeout_monitor.release()
        try:
            req.close()
        except:
            cherrypy.log(traceback=True, severity=40)

        cherrypy.serving.clear()

    def __call__(self, environ, start_response):
        return self.wsgiapp(environ, start_response)


class Tree(object):
    apps = {}

    def __init__(self):
        self.apps = {}

    def mount(self, root, script_name = '', config = None):
        if script_name is None:
            raise TypeError("The 'script_name' argument may not be None. Application objects may, however, possess a script_name of None (in order to inpect the WSGI environ for SCRIPT_NAME upon each request). You cannot mount such Applications on this Tree; you must pass them to a WSGI server interface directly.")
        script_name = script_name.rstrip('/')
        if isinstance(root, Application):
            app = root
            if script_name != '' and script_name != app.script_name:
                raise ValueError('Cannot specify a different script name and pass an Application instance to cherrypy.mount')
            script_name = app.script_name
        else:
            app = Application(root, script_name)
            if script_name == '' and root is not None and not hasattr(root, 'favicon_ico'):
                favicon = os.path.join(os.getcwd(), os.path.dirname(__file__), 'favicon.ico')
                root.favicon_ico = tools.staticfile.handler(favicon)
        if config:
            app.merge(config)
        self.apps[script_name] = app
        return app

    def graft(self, wsgi_callable, script_name = ''):
        script_name = script_name.rstrip('/')
        self.apps[script_name] = wsgi_callable

    def script_name(self, path = None):
        if path is None:
            try:
                request = cherrypy.serving.request
                path = httputil.urljoin(request.script_name, request.path_info)
            except AttributeError:
                return

        while True:
            if path in self.apps:
                return path
            if path == '':
                return
            path = path[:path.rfind('/')]

    def __call__(self, environ, start_response):
        env1x = environ
        if environ.get(ntou('wsgi.version')) == (ntou('u'), 0):
            env1x = _cpwsgi.downgrade_wsgi_ux_to_1x(environ)
        path = httputil.urljoin(env1x.get('SCRIPT_NAME', ''), env1x.get('PATH_INFO', ''))
        sn = self.script_name(path or '/')
        if sn is None:
            start_response('404 Not Found', [])
            return []
        app = self.apps[sn]
        environ = environ.copy()
        if environ.get(u'wsgi.version') == (u'u', 0):
            enc = environ[u'wsgi.url_encoding']
            environ[u'SCRIPT_NAME'] = sn.decode(enc)
            environ[u'PATH_INFO'] = path[len(sn.rstrip('/')):].decode(enc)
        else:
            environ['SCRIPT_NAME'] = sn
            environ['PATH_INFO'] = path[len(sn.rstrip('/')):]
        return app(environ, start_response)