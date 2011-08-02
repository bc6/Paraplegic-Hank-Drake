import cherrypy
import warnings

def _getargs(func):
    import types
    if isinstance(func, types.MethodType):
        func = func.im_func
    co = func.func_code
    return co.co_varnames[:co.co_argcount]


_attr_error = 'CherryPy Tools cannot be turned on directly. Instead, turn them on via config, or use them as decorators on your page handlers.'

class Tool(object):
    namespace = 'tools'

    def __init__(self, point, callable, name = None, priority = 50):
        self._point = point
        self.callable = callable
        self._name = name
        self._priority = priority
        self.__doc__ = self.callable.__doc__
        self._setargs()



    def _get_on(self):
        raise AttributeError(_attr_error)



    def _set_on(self, value):
        raise AttributeError(_attr_error)


    on = property(_get_on, _set_on)

    def _setargs(self):
        try:
            for arg in _getargs(self.callable):
                setattr(self, arg, None)

        except (TypeError, AttributeError):
            if hasattr(self.callable, '__call__'):
                for arg in _getargs(self.callable.__call__):
                    setattr(self, arg, None)

        except NotImplementedError:
            pass
        except IndexError:
            pass



    def _merged_args(self, d = None):
        if d:
            conf = d.copy()
        else:
            conf = {}
        tm = cherrypy.serving.request.toolmaps[self.namespace]
        if self._name in tm:
            conf.update(tm[self._name])
        if 'on' in conf:
            del conf['on']
        return conf



    def __call__(self, *args, **kwargs):
        if args:
            raise TypeError('The %r Tool does not accept positional arguments; you must use keyword arguments.' % self._name)

        def tool_decorator(f):
            if not hasattr(f, '_cp_config'):
                f._cp_config = {}
            subspace = self.namespace + '.' + self._name + '.'
            f._cp_config[subspace + 'on'] = True
            for (k, v,) in kwargs.items():
                f._cp_config[subspace + k] = v

            return f


        return tool_decorator



    def _setup(self):
        conf = self._merged_args()
        p = conf.pop('priority', None)
        if p is None:
            p = getattr(self.callable, 'priority', self._priority)
        cherrypy.serving.request.hooks.attach(self._point, self.callable, priority=p, **conf)




class HandlerTool(Tool):

    def __init__(self, callable, name = None):
        Tool.__init__(self, 'before_handler', callable, name)



    def handler(self, *args, **kwargs):

        def handle_func(*a, **kw):
            handled = self.callable(*args, **self._merged_args(kwargs))
            if not handled:
                raise cherrypy.NotFound()
            return cherrypy.serving.response.body


        handle_func.exposed = True
        return handle_func



    def _wrapper(self, **kwargs):
        if self.callable(**kwargs):
            cherrypy.serving.request.handler = None



    def _setup(self):
        conf = self._merged_args()
        p = conf.pop('priority', None)
        if p is None:
            p = getattr(self.callable, 'priority', self._priority)
        cherrypy.serving.request.hooks.attach(self._point, self._wrapper, priority=p, **conf)




class HandlerWrapperTool(Tool):

    def __init__(self, newhandler, point = 'before_handler', name = None, priority = 50):
        self.newhandler = newhandler
        self._point = point
        self._name = name
        self._priority = priority



    def callable(self, debug = False):
        innerfunc = cherrypy.serving.request.handler

        def wrap(*args, **kwargs):
            return self.newhandler(innerfunc, *args, **kwargs)


        cherrypy.serving.request.handler = wrap




class ErrorTool(Tool):

    def __init__(self, callable, name = None):
        Tool.__init__(self, None, callable, name)



    def _wrapper(self):
        self.callable(**self._merged_args())



    def _setup(self):
        cherrypy.serving.request.error_response = self._wrapper



from cherrypy.lib import cptools, encoding, auth, static, jsontools
from cherrypy.lib import sessions as _sessions, xmlrpc as _xmlrpc
from cherrypy.lib import caching as _caching
from cherrypy.lib import auth_basic, auth_digest

class SessionTool(Tool):

    def __init__(self):
        Tool.__init__(self, 'before_request_body', _sessions.init)



    def _lock_session(self):
        cherrypy.serving.session.acquire_lock()



    def _setup(self):
        hooks = cherrypy.serving.request.hooks
        conf = self._merged_args()
        p = conf.pop('priority', None)
        if p is None:
            p = getattr(self.callable, 'priority', self._priority)
        hooks.attach(self._point, self.callable, priority=p, **conf)
        locking = conf.pop('locking', 'implicit')
        if locking == 'implicit':
            hooks.attach('before_handler', self._lock_session)
        elif locking == 'early':
            hooks.attach('before_request_body', self._lock_session, priority=60)
        hooks.attach('before_finalize', _sessions.save)
        hooks.attach('on_end_request', _sessions.close)



    def regenerate(self):
        sess = cherrypy.serving.session
        sess.regenerate()
        conf = dict([ (k, v) for (k, v,) in self._merged_args().items() if k in ('path', 'path_header', 'name', 'timeout', 'domain', 'secure') ])
        _sessions.set_response_cookie(**conf)




class XMLRPCController(object):
    _cp_config = {'tools.xmlrpc.on': True}

    def default(self, *vpath, **params):
        (rpcparams, rpcmethod,) = _xmlrpc.process_body()
        subhandler = self
        for attr in str(rpcmethod).split('.'):
            subhandler = getattr(subhandler, attr, None)

        if subhandler and getattr(subhandler, 'exposed', False):
            body = subhandler(*(vpath + rpcparams), **params)
        else:
            raise Exception('method "%s" is not supported' % attr)
        conf = cherrypy.serving.request.toolmaps['tools'].get('xmlrpc', {})
        _xmlrpc.respond(body, conf.get('encoding', 'utf-8'), conf.get('allow_none', 0))
        return cherrypy.serving.response.body


    default.exposed = True


class SessionAuthTool(HandlerTool):

    def _setargs(self):
        for name in dir(cptools.SessionAuth):
            if not name.startswith('__'):
                setattr(self, name, None)





class CachingTool(Tool):

    def _wrapper(self, **kwargs):
        request = cherrypy.serving.request
        if _caching.get(**kwargs):
            request.handler = None
        elif request.cacheable:
            request.hooks.attach('before_finalize', _caching.tee_output, priority=90)


    _wrapper.priority = 20

    def _setup(self):
        conf = self._merged_args()
        p = conf.pop('priority', None)
        cherrypy.serving.request.hooks.attach('before_handler', self._wrapper, priority=p, **conf)




class Toolbox(object):

    def __init__(self, namespace):
        self.namespace = namespace



    def __setattr__(self, name, value):
        if isinstance(value, Tool):
            if value._name is None:
                value._name = name
            value.namespace = self.namespace
        object.__setattr__(self, name, value)



    def __enter__(self):
        cherrypy.serving.request.toolmaps[self.namespace] = map = {}

        def populate(k, v):
            (toolname, arg,) = k.split('.', 1)
            bucket = map.setdefault(toolname, {})
            bucket[arg] = v


        return populate



    def __exit__(self, exc_type, exc_val, exc_tb):
        map = cherrypy.serving.request.toolmaps.get(self.namespace)
        if map:
            for (name, settings,) in map.items():
                if settings.get('on', False):
                    tool = getattr(self, name)
                    tool._setup()





class DeprecatedTool(Tool):
    _name = None
    warnmsg = 'This Tool is deprecated.'

    def __init__(self, point, warnmsg = None):
        self.point = point
        if warnmsg is not None:
            self.warnmsg = warnmsg



    def __call__(self, *args, **kwargs):
        warnings.warn(self.warnmsg)

        def tool_decorator(f):
            return f


        return tool_decorator



    def _setup(self):
        warnings.warn(self.warnmsg)



default_toolbox = _d = Toolbox('tools')
_d.session_auth = SessionAuthTool(cptools.session_auth)
_d.proxy = Tool('before_request_body', cptools.proxy, priority=30)
_d.response_headers = Tool('on_start_resource', cptools.response_headers)
_d.log_tracebacks = Tool('before_error_response', cptools.log_traceback)
_d.log_headers = Tool('before_error_response', cptools.log_request_headers)
_d.log_hooks = Tool('on_end_request', cptools.log_hooks, priority=100)
_d.err_redirect = ErrorTool(cptools.redirect)
_d.etags = Tool('before_finalize', cptools.validate_etags, priority=75)
_d.decode = Tool('before_request_body', encoding.decode)
_d.encode = Tool('before_handler', encoding.ResponseEncoder, priority=70)
_d.gzip = Tool('before_finalize', encoding.gzip, priority=80)
_d.staticdir = HandlerTool(static.staticdir)
_d.staticfile = HandlerTool(static.staticfile)
_d.sessions = SessionTool()
_d.xmlrpc = ErrorTool(_xmlrpc.on_error)
_d.caching = CachingTool('before_handler', _caching.get, 'caching')
_d.expires = Tool('before_finalize', _caching.expires)
_d.tidy = DeprecatedTool('before_finalize', 'The tidy tool has been removed from the standard distribution of CherryPy. The most recent version can be found at http://tools.cherrypy.org/browser.')
_d.nsgmls = DeprecatedTool('before_finalize', 'The nsgmls tool has been removed from the standard distribution of CherryPy. The most recent version can be found at http://tools.cherrypy.org/browser.')
_d.ignore_headers = Tool('before_request_body', cptools.ignore_headers)
_d.referer = Tool('before_request_body', cptools.referer)
_d.basic_auth = Tool('on_start_resource', auth.basic_auth)
_d.digest_auth = Tool('on_start_resource', auth.digest_auth)
_d.trailing_slash = Tool('before_handler', cptools.trailing_slash, priority=60)
_d.flatten = Tool('before_finalize', cptools.flatten)
_d.accept = Tool('on_start_resource', cptools.accept)
_d.redirect = Tool('on_start_resource', cptools.redirect)
_d.autovary = Tool('on_start_resource', cptools.autovary, priority=0)
_d.json_in = Tool('before_request_body', jsontools.json_in, priority=30)
_d.json_out = Tool('before_handler', jsontools.json_out, priority=30)
_d.auth_basic = Tool('before_handler', auth_basic.basic_auth, priority=1)
_d.auth_digest = Tool('before_handler', auth_digest.digest_auth, priority=1)
del _d
del cptools
del encoding
del auth
del static

