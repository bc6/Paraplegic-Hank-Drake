import cherrypy

class PageHandler(object):

    def __init__(self, callable, *args, **kwargs):
        self.callable = callable
        self.args = args
        self.kwargs = kwargs



    def __call__(self):
        try:
            return self.callable(*self.args, **self.kwargs)
        except TypeError as x:
            try:
                test_callable_spec(self.callable, self.args, self.kwargs)
            except cherrypy.HTTPError as error:
                raise error
            except:
                raise x
            raise 




def test_callable_spec(callable, callable_args, callable_kwargs):
    show_mismatched_params = getattr(cherrypy.serving.request, 'show_mismatched_params', False)
    try:
        (args, varargs, varkw, defaults,) = inspect.getargspec(callable)
    except TypeError:
        if isinstance(callable, object) and hasattr(callable, '__call__'):
            (args, varargs, varkw, defaults,) = inspect.getargspec(callable.__call__)
        else:
            raise 
    if args and args[0] == 'self':
        args = args[1:]
    arg_usage = dict([ (arg, 0) for arg in args ])
    vararg_usage = 0
    varkw_usage = 0
    extra_kwargs = set()
    for (i, value,) in enumerate(callable_args):
        try:
            arg_usage[args[i]] += 1
        except IndexError:
            vararg_usage += 1

    for key in callable_kwargs.keys():
        try:
            arg_usage[key] += 1
        except KeyError:
            varkw_usage += 1
            extra_kwargs.add(key)

    args_with_defaults = args[(-len(defaults or [])):]
    for (i, val,) in enumerate(defaults or []):
        if arg_usage[args_with_defaults[i]] == 0:
            arg_usage[args_with_defaults[i]] += 1

    missing_args = []
    multiple_args = []
    for (key, usage,) in arg_usage.items():
        if usage == 0:
            missing_args.append(key)
        elif usage > 1:
            multiple_args.append(key)

    if missing_args:
        message = None
        if show_mismatched_params:
            message = 'Missing parameters: %s' % ','.join(missing_args)
        raise cherrypy.HTTPError(404, message=message)
    if not varargs and vararg_usage > 0:
        raise cherrypy.HTTPError(404)
    body_params = cherrypy.serving.request.body.params or {}
    body_params = set(body_params.keys())
    qs_params = set(callable_kwargs.keys()) - body_params
    if multiple_args:
        if qs_params.intersection(set(multiple_args)):
            error = 404
        else:
            error = 400
        message = None
        if show_mismatched_params:
            message = 'Multiple values for parameters: %s' % ','.join(multiple_args)
        raise cherrypy.HTTPError(error, message=message)
    if not varkw and varkw_usage > 0:
        extra_qs_params = set(qs_params).intersection(extra_kwargs)
        if extra_qs_params:
            message = None
            if show_mismatched_params:
                message = 'Unexpected query string parameters: %s' % ', '.join(extra_qs_params)
            raise cherrypy.HTTPError(404, message=message)
        extra_body_params = set(body_params).intersection(extra_kwargs)
        if extra_body_params:
            message = None
            if show_mismatched_params:
                message = 'Unexpected body parameters: %s' % ', '.join(extra_body_params)
            raise cherrypy.HTTPError(400, message=message)


try:
    import inspect
except ImportError:
    test_callable_spec = lambda callable, args, kwargs: None

class LateParamPageHandler(PageHandler):

    def _get_kwargs(self):
        kwargs = cherrypy.serving.request.params.copy()
        if self._kwargs:
            kwargs.update(self._kwargs)
        return kwargs



    def _set_kwargs(self, kwargs):
        self._kwargs = kwargs


    kwargs = property(_get_kwargs, _set_kwargs, doc='page handler kwargs (with cherrypy.request.params copied in)')


class Dispatcher(object):
    __metaclass__ = cherrypy._AttributeDocstrings
    dispatch_method_name = '_cp_dispatch'
    dispatch_method_name__doc = '\n    The name of the dispatch method that nodes may optionally implement\n    to provide their own dynamic dispatch algorithm.\n    '

    def __init__(self, dispatch_method_name = None):
        if dispatch_method_name:
            self.dispatch_method_name = dispatch_method_name



    def __call__(self, path_info):
        request = cherrypy.serving.request
        (func, vpath,) = self.find_handler(path_info)
        if func:
            vpath = [ x.replace('%2F', '/') for x in vpath ]
            request.handler = LateParamPageHandler(func, *vpath)
        else:
            request.handler = cherrypy.NotFound()



    def find_handler(self, path):
        request = cherrypy.serving.request
        app = request.app
        root = app.root
        dispatch_name = self.dispatch_method_name
        curpath = ''
        nodeconf = {}
        if hasattr(root, '_cp_config'):
            nodeconf.update(root._cp_config)
        if '/' in app.config:
            nodeconf.update(app.config['/'])
        object_trail = [['root',
          root,
          nodeconf,
          curpath]]
        node = root
        names = [ x for x in path.strip('/').split('/') if x ] + ['index']
        iternames = names[:]
        while iternames:
            name = iternames[0]
            objname = name.replace('.', '_')
            nodeconf = {}
            subnode = getattr(node, objname, None)
            if subnode is None:
                dispatch = getattr(node, dispatch_name, None)
                if dispatch and callable(dispatch) and not getattr(dispatch, 'exposed', False):
                    subnode = dispatch(vpath=iternames)
            name = iternames.pop(0)
            node = subnode
            if node is not None:
                if hasattr(node, '_cp_config'):
                    nodeconf.update(node._cp_config)
            curpath = '/'.join((curpath, name))
            if curpath in app.config:
                nodeconf.update(app.config[curpath])
            object_trail.append([name,
             node,
             nodeconf,
             curpath])


        def set_conf():
            base = cherrypy.config.copy()
            for (name, obj, conf, curpath,) in object_trail:
                base.update(conf)
                if 'tools.staticdir.dir' in conf:
                    base['tools.staticdir.section'] = curpath

            return base


        num_candidates = len(object_trail) - 1
        for i in range(num_candidates, -1, -1):
            (name, candidate, nodeconf, curpath,) = object_trail[i]
            if candidate is None:
                continue
            if hasattr(candidate, 'default'):
                defhandler = candidate.default
                if getattr(defhandler, 'exposed', False):
                    conf = getattr(defhandler, '_cp_config', {})
                    object_trail.insert(i + 1, ['default',
                     defhandler,
                     conf,
                     curpath])
                    request.config = set_conf()
                    request.is_index = path.endswith('/')
                    return (defhandler, names[i:-1])
            if getattr(candidate, 'exposed', False):
                request.config = set_conf()
                if i == num_candidates:
                    request.is_index = True
                else:
                    request.is_index = False
                return (candidate, names[i:-1])

        request.config = set_conf()
        return (None, [])




class MethodDispatcher(Dispatcher):

    def __call__(self, path_info):
        request = cherrypy.serving.request
        (resource, vpath,) = self.find_handler(path_info)
        if resource:
            avail = [ m for m in dir(resource) if m.isupper() ]
            if 'GET' in avail and 'HEAD' not in avail:
                avail.append('HEAD')
            avail.sort()
            cherrypy.serving.response.headers['Allow'] = ', '.join(avail)
            meth = request.method.upper()
            func = getattr(resource, meth, None)
            if func is None and meth == 'HEAD':
                func = getattr(resource, 'GET', None)
            if func:
                if hasattr(func, '_cp_config'):
                    request.config.update(func._cp_config)
                vpath = [ x.replace('%2F', '/') for x in vpath ]
                request.handler = LateParamPageHandler(func, *vpath)
            else:
                request.handler = cherrypy.HTTPError(405)
        else:
            request.handler = cherrypy.NotFound()




class RoutesDispatcher(object):

    def __init__(self, full_result = False):
        import routes
        self.full_result = full_result
        self.controllers = {}
        self.mapper = routes.Mapper()
        self.mapper.controller_scan = self.controllers.keys



    def connect(self, name, route, controller, **kwargs):
        self.controllers[name] = controller
        self.mapper.connect(name, route, controller=name, **kwargs)



    def redirect(self, url):
        raise cherrypy.HTTPRedirect(url)



    def __call__(self, path_info):
        func = self.find_handler(path_info)
        if func:
            cherrypy.serving.request.handler = LateParamPageHandler(func)
        else:
            cherrypy.serving.request.handler = cherrypy.NotFound()



    def find_handler(self, path_info):
        import routes
        request = cherrypy.serving.request
        config = routes.request_config()
        config.mapper = self.mapper
        if hasattr(request, 'wsgi_environ'):
            config.environ = request.wsgi_environ
        config.host = request.headers.get('Host', None)
        config.protocol = request.scheme
        config.redirect = self.redirect
        result = self.mapper.match(path_info)
        config.mapper_dict = result
        params = {}
        if result:
            params = result.copy()
        if not self.full_result:
            params.pop('controller', None)
            params.pop('action', None)
        request.params.update(params)
        request.config = base = cherrypy.config.copy()
        curpath = ''

        def merge(nodeconf):
            if 'tools.staticdir.dir' in nodeconf:
                nodeconf['tools.staticdir.section'] = curpath or '/'
            base.update(nodeconf)


        app = request.app
        root = app.root
        if hasattr(root, '_cp_config'):
            merge(root._cp_config)
        if '/' in app.config:
            merge(app.config['/'])
        atoms = [ x for x in path_info.split('/') if x ]
        if atoms:
            last = atoms.pop()
        else:
            last = None
        for atom in atoms:
            curpath = '/'.join((curpath, atom))
            if curpath in app.config:
                merge(app.config[curpath])

        handler = None
        if result:
            controller = result.get('controller', None)
            controller = self.controllers.get(controller)
            if controller:
                if hasattr(controller, '_cp_config'):
                    merge(controller._cp_config)
            action = result.get('action', None)
            if action is not None:
                handler = getattr(controller, action, None)
                if hasattr(handler, '_cp_config'):
                    merge(handler._cp_config)
        if last:
            curpath = '/'.join((curpath, last))
            if curpath in app.config:
                merge(app.config[curpath])
        return handler




def XMLRPCDispatcher(next_dispatcher = Dispatcher()):
    from cherrypy.lib import xmlrpc

    def xmlrpc_dispatch(path_info):
        path_info = xmlrpc.patched_path(path_info)
        return next_dispatcher(path_info)


    return xmlrpc_dispatch



def VirtualHost(next_dispatcher = Dispatcher(), use_x_forwarded_host = True, **domains):
    from cherrypy.lib import httputil

    def vhost_dispatch(path_info):
        request = cherrypy.serving.request
        header = request.headers.get
        domain = header('Host', '')
        if use_x_forwarded_host:
            domain = header('X-Forwarded-Host', domain)
        prefix = domains.get(domain, '')
        if prefix:
            path_info = httputil.urljoin(prefix, path_info)
        result = next_dispatcher(path_info)
        section = request.config.get('tools.staticdir.section')
        if section:
            section = section[len(prefix):]
            request.config['tools.staticdir.section'] = section
        return result


    return vhost_dispatch



