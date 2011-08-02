import sys as _sys
import cherrypy as _cherrypy
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from cherrypy import _cperror
from cherrypy.lib import httputil

def downgrade_wsgi_ux_to_1x(environ):
    env1x = {}
    url_encoding = environ[u'wsgi.url_encoding']
    for (k, v,) in environ.items():
        if k in (u'PATH_INFO', u'SCRIPT_NAME', u'QUERY_STRING'):
            v = v.encode(url_encoding)
        elif isinstance(v, unicode):
            v = v.encode('ISO-8859-1')
        env1x[k.encode('ISO-8859-1')] = v

    return env1x



class VirtualHost(object):

    def __init__(self, default, domains = None, use_x_forwarded_host = True):
        self.default = default
        self.domains = domains or {}
        self.use_x_forwarded_host = use_x_forwarded_host



    def __call__(self, environ, start_response):
        domain = environ.get('HTTP_HOST', '')
        if self.use_x_forwarded_host:
            domain = environ.get('HTTP_X_FORWARDED_HOST', domain)
        nextapp = self.domains.get(domain)
        if nextapp is None:
            nextapp = self.default
        return nextapp(environ, start_response)




class InternalRedirector(object):

    def __init__(self, nextapp, recursive = False):
        self.nextapp = nextapp
        self.recursive = recursive



    def __call__(self, environ, start_response):
        redirections = []
        while True:
            environ = environ.copy()
            try:
                return self.nextapp(environ, start_response)
            except _cherrypy.InternalRedirect as ir:
                sn = environ.get('SCRIPT_NAME', '')
                path = environ.get('PATH_INFO', '')
                qs = environ.get('QUERY_STRING', '')
                old_uri = sn + path
                if qs:
                    old_uri += '?' + qs
                redirections.append(old_uri)
                if not self.recursive:
                    new_uri = sn + ir.path
                    if ir.query_string:
                        new_uri += '?' + ir.query_string
                    if new_uri in redirections:
                        ir.request.close()
                        raise RuntimeError('InternalRedirector visited the same URL twice: %r' % new_uri)
                environ['REQUEST_METHOD'] = 'GET'
                environ['PATH_INFO'] = ir.path
                environ['QUERY_STRING'] = ir.query_string
                environ['wsgi.input'] = StringIO()
                environ['CONTENT_LENGTH'] = '0'
                environ['cherrypy.previous_request'] = ir.request





class ExceptionTrapper(object):

    def __init__(self, nextapp, throws = (KeyboardInterrupt, SystemExit)):
        self.nextapp = nextapp
        self.throws = throws



    def __call__(self, environ, start_response):
        return _TrappedResponse(self.nextapp, environ, start_response, self.throws)




class _TrappedResponse(object):
    response = iter([])

    def __init__(self, nextapp, environ, start_response, throws):
        self.nextapp = nextapp
        self.environ = environ
        self.start_response = start_response
        self.throws = throws
        self.started_response = False
        self.response = self.trap(self.nextapp, self.environ, self.start_response)
        self.iter_response = iter(self.response)



    def __iter__(self):
        self.started_response = True
        return self



    def next(self):
        return self.trap(self.iter_response.next)



    def close(self):
        if hasattr(self.response, 'close'):
            self.response.close()



    def trap(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except self.throws:
            raise 
        except StopIteration:
            raise 
        except:
            tb = _cperror.format_exc()
            _cherrypy.log(tb, severity=40)
            if not _cherrypy.request.show_tracebacks:
                tb = ''
            (s, h, b,) = _cperror.bare_error(tb)
            if self.started_response:
                self.iter_response = iter([])
            else:
                self.iter_response = iter(b)
            try:
                self.start_response(s, h, _sys.exc_info())
            except:
                _cherrypy.log(traceback=True, severity=40)
                raise 
            if self.started_response:
                return ''.join(b)
            else:
                return b




class AppResponse(object):

    def __init__(self, environ, start_response, cpapp):
        if environ.get(u'wsgi.version') == (u'u', 0):
            environ = downgrade_wsgi_ux_to_1x(environ)
        self.environ = environ
        self.cpapp = cpapp
        try:
            self.run()
        except:
            self.close()
            raise 
        r = _cherrypy.serving.response
        self.iter_response = iter(r.body)
        self.write = start_response(r.output_status, r.header_list)



    def __iter__(self):
        return self



    def next(self):
        return self.iter_response.next()



    def close(self):
        self.cpapp.release_serving()



    def run(self):
        env = self.environ.get
        local = httputil.Host('', int(env('SERVER_PORT', 80)), env('SERVER_NAME', ''))
        remote = httputil.Host(env('REMOTE_ADDR', ''), int(env('REMOTE_PORT', -1)), env('REMOTE_HOST', ''))
        scheme = env('wsgi.url_scheme')
        sproto = env('ACTUAL_SERVER_PROTOCOL', 'HTTP/1.1')
        (request, resp,) = self.cpapp.get_serving(local, remote, scheme, sproto)
        request.login = env('LOGON_USER') or env('REMOTE_USER') or None
        request.multithread = self.environ['wsgi.multithread']
        request.multiprocess = self.environ['wsgi.multiprocess']
        request.wsgi_environ = self.environ
        request.prev = env('cherrypy.previous_request', None)
        meth = self.environ['REQUEST_METHOD']
        path = httputil.urljoin(self.environ.get('SCRIPT_NAME', ''), self.environ.get('PATH_INFO', ''))
        qs = self.environ.get('QUERY_STRING', '')
        rproto = self.environ.get('SERVER_PROTOCOL')
        headers = self.translate_headers(self.environ)
        rfile = self.environ['wsgi.input']
        request.run(meth, path, qs, rproto, headers, rfile)


    headerNames = {'HTTP_CGI_AUTHORIZATION': 'Authorization',
     'CONTENT_LENGTH': 'Content-Length',
     'CONTENT_TYPE': 'Content-Type',
     'REMOTE_HOST': 'Remote-Host',
     'REMOTE_ADDR': 'Remote-Addr'}

    def translate_headers(self, environ):
        for cgiName in environ:
            if cgiName in self.headerNames:
                yield (self.headerNames[cgiName], environ[cgiName])
            elif cgiName[:5] == 'HTTP_':
                translatedHeader = cgiName[5:].replace('_', '-')
                yield (translatedHeader, environ[cgiName])





class CPWSGIApp(object):
    pipeline = [('ExceptionTrapper', ExceptionTrapper), ('InternalRedirector', InternalRedirector)]
    head = None
    config = {}
    response_class = AppResponse

    def __init__(self, cpapp, pipeline = None):
        self.cpapp = cpapp
        self.pipeline = self.pipeline[:]
        if pipeline:
            self.pipeline.extend(pipeline)
        self.config = self.config.copy()



    def tail(self, environ, start_response):
        return self.response_class(environ, start_response, self.cpapp)



    def __call__(self, environ, start_response):
        head = self.head
        if head is None:
            head = self.tail
            for (name, callable,) in self.pipeline[None]:
                conf = self.config.get(name, {})
                head = callable(head, **conf)

            self.head = head
        return head(environ, start_response)



    def namespace_handler(self, k, v):
        if k == 'pipeline':
            self.pipeline.extend(v)
        elif k == 'response_class':
            self.response_class = v
        else:
            (name, arg,) = k.split('.', 1)
            bucket = self.config.setdefault(name, {})
            bucket[arg] = v




