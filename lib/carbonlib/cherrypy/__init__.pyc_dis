#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\__init__.py
__version__ = '3.2.0'
from cherrypy._cpcompat import urljoin as _urljoin, urlencode as _urlencode
from cherrypy._cpcompat import basestring, unicodestr
from cherrypy._cperror import HTTPError, HTTPRedirect, InternalRedirect
from cherrypy._cperror import NotFound, CherryPyException, TimeoutError
from cherrypy import _cpdispatch as dispatch
from cherrypy import _cptools
tools = _cptools.default_toolbox
Tool = _cptools.Tool
from cherrypy import _cprequest
from cherrypy.lib import httputil as _httputil
from cherrypy import _cptree
tree = _cptree.Tree()
from cherrypy._cptree import Application
from cherrypy import _cpwsgi as wsgi
from cherrypy import process
try:
    from cherrypy.process import win32
    engine = win32.Win32Bus()
    engine.console_control_handler = win32.ConsoleCtrlHandler(engine)
    del win32
except ImportError:
    engine = process.bus

class _TimeoutMonitor(process.plugins.Monitor):

    def __init__(self, bus):
        self.servings = []
        process.plugins.Monitor.__init__(self, bus, self.run)

    def acquire(self):
        self.servings.append((serving.request, serving.response))

    def release(self):
        try:
            self.servings.remove((serving.request, serving.response))
        except ValueError:
            pass

    def run(self):
        for req, resp in self.servings:
            resp.check_timeout()


engine.timeout_monitor = _TimeoutMonitor(engine)
engine.timeout_monitor.subscribe()
engine.autoreload = process.plugins.Autoreloader(engine)
engine.autoreload.subscribe()
engine.thread_manager = process.plugins.ThreadManager(engine)
engine.thread_manager.subscribe()
engine.signal_handler = process.plugins.SignalHandler(engine)
from cherrypy import _cpserver
server = _cpserver.Server()
server.subscribe()

def quickstart(root = None, script_name = '', config = None):
    if config:
        _global_conf_alias.update(config)
    tree.mount(root, script_name, config)
    if hasattr(engine, 'signal_handler'):
        engine.signal_handler.subscribe()
    if hasattr(engine, 'console_control_handler'):
        engine.console_control_handler.subscribe()
    engine.start()
    engine.block()


from cherrypy._cpcompat import threadlocal as _local

class _Serving(_local):
    request = _cprequest.Request(_httputil.Host('127.0.0.1', 80), _httputil.Host('127.0.0.1', 1111))
    response = _cprequest.Response()

    def load(self, request, response):
        self.request = request
        self.response = response

    def clear(self):
        self.__dict__.clear()


serving = _Serving()

class _ThreadLocalProxy(object):
    __slots__ = ['__attrname__', '__dict__']

    def __init__(self, attrname):
        self.__attrname__ = attrname

    def __getattr__(self, name):
        child = getattr(serving, self.__attrname__)
        return getattr(child, name)

    def __setattr__(self, name, value):
        if name in ('__attrname__',):
            object.__setattr__(self, name, value)
        else:
            child = getattr(serving, self.__attrname__)
            setattr(child, name, value)

    def __delattr__(self, name):
        child = getattr(serving, self.__attrname__)
        delattr(child, name)

    def _get_dict(self):
        child = getattr(serving, self.__attrname__)
        d = child.__class__.__dict__.copy()
        d.update(child.__dict__)
        return d

    __dict__ = property(_get_dict)

    def __getitem__(self, key):
        child = getattr(serving, self.__attrname__)
        return child[key]

    def __setitem__(self, key, value):
        child = getattr(serving, self.__attrname__)
        child[key] = value

    def __delitem__(self, key):
        child = getattr(serving, self.__attrname__)
        del child[key]

    def __contains__(self, key):
        child = getattr(serving, self.__attrname__)
        return key in child

    def __len__(self):
        child = getattr(serving, self.__attrname__)
        return len(child)

    def __nonzero__(self):
        child = getattr(serving, self.__attrname__)
        return bool(child)

    __bool__ = __nonzero__


request = _ThreadLocalProxy('request')
response = _ThreadLocalProxy('response')

class _ThreadData(_local):
    pass


thread_data = _ThreadData()

def _cherrypy_pydoc_resolve(thing, forceload = 0):
    if isinstance(thing, _ThreadLocalProxy):
        thing = getattr(serving, thing.__attrname__)
    return _pydoc._builtin_resolve(thing, forceload)


try:
    import pydoc as _pydoc
    _pydoc._builtin_resolve = _pydoc.resolve
    _pydoc.resolve = _cherrypy_pydoc_resolve
except ImportError:
    pass

from cherrypy import _cplogging

class _GlobalLogManager(_cplogging.LogManager):

    def __call__(self, *args, **kwargs):
        if hasattr(request, 'app') and hasattr(request.app, 'log'):
            log = request.app.log
        else:
            log = self
        return log.error(*args, **kwargs)

    def access(self):
        try:
            return request.app.log.access()
        except AttributeError:
            return _cplogging.LogManager.access(self)


log = _GlobalLogManager()
log.screen = True
log.error_file = ''
log.access_file = ''

def _buslog(msg, level):
    log.error(msg, 'ENGINE', severity=level)


engine.subscribe('log', _buslog)

def expose(func = None, alias = None):

    def expose_(func):
        func.exposed = True
        if alias is not None:
            if isinstance(alias, basestring):
                parents[alias.replace('.', '_')] = func
            else:
                for a in alias:
                    parents[a.replace('.', '_')] = func

        return func

    import sys, types
    if isinstance(func, (types.FunctionType, types.MethodType)):
        if alias is None:
            func.exposed = True
            return func
        else:
            parents = sys._getframe(1).f_locals
            return expose_(func)
    elif func is None:
        if alias is None:
            parents = sys._getframe(1).f_locals
            return expose_
        else:
            parents = sys._getframe(1).f_locals
            return expose_
    else:
        parents = sys._getframe(1).f_locals
        alias = func
        return expose_


def popargs(*args, **kwargs):
    handler = None
    handler_call = False
    for k, v in kwargs.items():
        if k == 'handler':
            handler = v
        else:
            raise TypeError("cherrypy.popargs() got an unexpected keyword argument '{0}'".format(k))

    import inspect
    if handler is not None and (hasattr(handler, '__call__') or inspect.isclass(handler)):
        handler_call = True

    def decorated(cls_or_self = None, vpath = None):
        if inspect.isclass(cls_or_self):
            cls = cls_or_self
            setattr(cls, dispatch.Dispatcher.dispatch_method_name, decorated)
            return cls
        self = cls_or_self
        parms = {}
        for arg in args:
            if not vpath:
                break
            parms[arg] = vpath.pop(0)

        if handler is not None:
            if handler_call:
                return handler(**parms)
            else:
                request.params.update(parms)
                return handler
        request.params.update(parms)
        if vpath:
            return getattr(self, vpath.pop(0), None)
        else:
            return self

    return decorated


def url(path = '', qs = '', script_name = None, base = None, relative = None):
    if isinstance(qs, (tuple, list, dict)):
        qs = _urlencode(qs)
    if qs:
        qs = '?' + qs
    if request.app:
        if not path.startswith('/'):
            pi = request.path_info
            if request.is_index is True:
                if not pi.endswith('/'):
                    pi = pi + '/'
            elif request.is_index is False:
                if pi.endswith('/') and pi != '/':
                    pi = pi[:-1]
            if path == '':
                path = pi
            else:
                path = _urljoin(pi, path)
        if script_name is None:
            script_name = request.script_name
        if base is None:
            base = request.base
        newurl = base + script_name + path + qs
    else:
        if base is None:
            base = server.base()
        path = (script_name or '') + path
        newurl = base + path + qs
    if './' in newurl:
        atoms = []
        for atom in newurl.split('/'):
            if atom == '.':
                pass
            elif atom == '..':
                atoms.pop()
            else:
                atoms.append(atom)

        newurl = '/'.join(atoms)
    if relative is None:
        relative = getattr(request.app, 'relative_urls', False)
    if relative == 'server':
        newurl = '/' + '/'.join(newurl.split('/', 3)[3:])
    elif relative:
        old = url().split('/')[:-1]
        new = newurl.split('/')
        while old and new:
            a, b = old[0], new[0]
            if a != b:
                break
            old.pop(0)
            new.pop(0)

        new = ['..'] * len(old) + new
        newurl = '/'.join(new)
    return newurl


from cherrypy import _cpconfig
config = _global_conf_alias = _cpconfig.Config()
config.defaults = {'tools.log_tracebacks.on': True,
 'tools.log_headers.on': True,
 'tools.trailing_slash.on': True,
 'tools.encode.on': True}
config.namespaces['log'] = lambda k, v: setattr(log, k, v)
config.namespaces['checker'] = lambda k, v: setattr(checker, k, v)
config.reset()
from cherrypy import _cpchecker
checker = _cpchecker.Checker()
engine.subscribe('start', checker)