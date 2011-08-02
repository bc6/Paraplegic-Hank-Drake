from cStringIO import StringIO
import warnings
__all__ = ['RecursiveMiddleware']
__pudge_all__ = ['RecursiveMiddleware', 'ForwardRequestException']

class RecursionLoop(AssertionError):
    pass

class CheckForRecursionMiddleware(object):

    def __init__(self, app, env):
        self.app = app
        self.env = env



    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        if path_info in self.env.get('paste.recursive.old_path_info', []):
            raise RecursionLoop('Forwarding loop detected; %r visited twice (internal redirect path: %s)' % (path_info, self.env['paste.recursive.old_path_info']))
        old_path_info = self.env.setdefault('paste.recursive.old_path_info', [])
        old_path_info.append(self.env.get('PATH_INFO', ''))
        return self.app(environ, start_response)




class RecursiveMiddleware(object):

    def __init__(self, application, global_conf = None):
        self.application = application



    def __call__(self, environ, start_response):
        environ['paste.recursive.forward'] = Forwarder(self.application, environ, start_response)
        environ['paste.recursive.include'] = Includer(self.application, environ, start_response)
        environ['paste.recursive.include_app_iter'] = IncluderAppIter(self.application, environ, start_response)
        my_script_name = environ.get('SCRIPT_NAME', '')
        environ['paste.recursive.script_name'] = my_script_name
        try:
            return self.application(environ, start_response)
        except ForwardRequestException as e:
            middleware = CheckForRecursionMiddleware(e.factory(self), environ)
            return middleware(environ, start_response)




class ForwardRequestException(Exception):

    def __init__(self, url = None, environ = {}, factory = None, path_info = None):
        if factory and url:
            raise TypeError('You cannot specify factory and a url in ForwardRequestException')
        elif factory and environ:
            raise TypeError('You cannot specify factory and environ in ForwardRequestException')
        if url and environ:
            raise TypeError('You cannot specify environ and url in ForwardRequestException')
        if path_info:
            if not url:
                warnings.warn('ForwardRequestException(path_info=...) has been deprecated; please use ForwardRequestException(url=...)', DeprecationWarning, 2)
            else:
                raise TypeError('You cannot use url and path_info in ForwardRequestException')
            self.path_info = path_info
        if url and '?' not in str(url):
            self.path_info = url

        class ForwardRequestExceptionMiddleware(object):

            def __init__(self, app):
                self.app = app



        if hasattr(self, 'path_info'):
            p = self.path_info

            def factory_(app):

                class PathInfoForward(ForwardRequestExceptionMiddleware):

                    def __call__(self, environ, start_response):
                        environ['PATH_INFO'] = p
                        return self.app(environ, start_response)



                return PathInfoForward(app)


            self.factory = factory_
        elif url:

            def factory_(app):

                class URLForward(ForwardRequestExceptionMiddleware):

                    def __call__(self, environ, start_response):
                        environ['PATH_INFO'] = url.split('?')[0]
                        environ['QUERY_STRING'] = url.split('?')[1]
                        return self.app(environ, start_response)



                return URLForward(app)


            self.factory = factory_
        elif environ:

            def factory_(app):

                class EnvironForward(ForwardRequestExceptionMiddleware):

                    def __call__(self, environ_, start_response):
                        return self.app(environ, start_response)



                return EnvironForward(app)


            self.factory = factory_
        else:
            self.factory = factory




class Recursive(object):

    def __init__(self, application, environ, start_response):
        self.application = application
        self.original_environ = environ.copy()
        self.previous_environ = environ
        self.start_response = start_response



    def __call__(self, path, extra_environ = None):
        environ = self.original_environ.copy()
        if extra_environ:
            environ.update(extra_environ)
        environ['paste.recursive.previous_environ'] = self.previous_environ
        base_path = self.original_environ.get('SCRIPT_NAME')
        if path.startswith('/'):
            path = path[(len(base_path) + 1):]
        path_info = '/' + path
        environ['PATH_INFO'] = path_info
        environ['REQUEST_METHOD'] = 'GET'
        environ['CONTENT_LENGTH'] = '0'
        environ['CONTENT_TYPE'] = ''
        environ['wsgi.input'] = StringIO('')
        return self.activate(environ)



    def activate(self, environ):
        raise NotImplementedError



    def __repr__(self):
        return '<%s.%s from %s>' % (self.__class__.__module__, self.__class__.__name__, self.original_environ.get('SCRIPT_NAME') or '/')




class Forwarder(Recursive):

    def activate(self, environ):
        warnings.warn('recursive.Forwarder has been deprecated; please use ForwardRequestException', DeprecationWarning, 2)
        return self.application(environ, self.start_response)




class Includer(Recursive):

    def activate(self, environ):
        response = IncludedResponse()

        def start_response(status, headers, exc_info = None):
            if exc_info:
                raise exc_info[0], exc_info[1], exc_info[2]
            response.status = status
            response.headers = headers
            return response.write


        app_iter = self.application(environ, start_response)
        try:
            for s in app_iter:
                response.write(s)


        finally:
            if hasattr(app_iter, 'close'):
                app_iter.close()

        response.close()
        return response




class IncludedResponse(object):

    def __init__(self):
        self.headers = None
        self.status = None
        self.output = StringIO()
        self.str = None



    def close(self):
        self.str = self.output.getvalue()
        self.output.close()
        self.output = None



    def write(self, s):
        self.output.write(s)



    def __str__(self):
        return self.body



    def body__get(self):
        if self.str is None:
            return self.output.getvalue()
        else:
            return self.str


    body = property(body__get)


class IncluderAppIter(Recursive):

    def activate(self, environ):
        response = IncludedAppIterResponse()

        def start_response(status, headers, exc_info = None):
            if exc_info:
                raise exc_info[0], exc_info[1], exc_info[2]
            response.status = status
            response.headers = headers
            return response.write


        app_iter = self.application(environ, start_response)
        response.app_iter = app_iter
        return response




class IncludedAppIterResponse(object):

    def __init__(self):
        self.status = None
        self.headers = None
        self.accumulated = []
        self.app_iter = None
        self._closed = False



    def close(self):
        if hasattr(self.app_iter, 'close'):
            self.app_iter.close()



    def write(self, s):
        self.accumulated.append




def make_recursive_middleware(app, global_conf):
    return RecursiveMiddleware(app)


make_recursive_middleware.__doc__ = __doc__

