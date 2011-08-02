from Cookie import SimpleCookie, CookieError
import os
import sys
import time
import types
import warnings
import cherrypy
from cherrypy import _cpreqbody, _cpconfig
from cherrypy._cperror import format_exc, bare_error
from cherrypy.lib import httputil, file_generator

class Hook(object):
    __metaclass__ = cherrypy._AttributeDocstrings
    callback = None
    callback__doc = '\n    The bare callable that this Hook object is wrapping, which will\n    be called when the Hook is called.'
    failsafe = False
    failsafe__doc = '\n    If True, the callback is guaranteed to run even if other callbacks\n    from the same call point raise exceptions.'
    priority = 50
    priority__doc = '\n    Defines the order of execution for a list of Hooks. Priority numbers\n    should be limited to the closed interval [0, 100], but values outside\n    this range are acceptable, as are fractional values.'
    kwargs = {}
    kwargs__doc = '\n    A set of keyword arguments that will be passed to the\n    callable on each call.'

    def __init__(self, callback, failsafe = None, priority = None, **kwargs):
        self.callback = callback
        if failsafe is None:
            failsafe = getattr(callback, 'failsafe', False)
        self.failsafe = failsafe
        if priority is None:
            priority = getattr(callback, 'priority', 50)
        self.priority = priority
        self.kwargs = kwargs



    def __cmp__(self, other):
        return cmp(self.priority, other.priority)



    def __call__(self):
        return self.callback(**self.kwargs)



    def __repr__(self):
        cls = self.__class__
        return '%s.%s(callback=%r, failsafe=%r, priority=%r, %s)' % (cls.__module__,
         cls.__name__,
         self.callback,
         self.failsafe,
         self.priority,
         ', '.join([ '%s=%r' % (k, v) for (k, v,) in self.kwargs.items() ]))




class HookMap(dict):

    def __new__(cls, points = None):
        d = dict.__new__(cls)
        for p in points or []:
            d[p] = []

        return d



    def __init__(self, *a, **kw):
        pass



    def attach(self, point, callback, failsafe = None, priority = None, **kwargs):
        self[point].append(Hook(callback, failsafe, priority, **kwargs))



    def run(self, point):
        exc = None
        hooks = self[point]
        hooks.sort()
        for hook in hooks:
            if exc is None or hook.failsafe:
                try:
                    hook()
                except (KeyboardInterrupt, SystemExit):
                    raise 
                except (cherrypy.HTTPError, cherrypy.HTTPRedirect, cherrypy.InternalRedirect):
                    exc = sys.exc_info()[1]
                except:
                    exc = sys.exc_info()[1]
                    cherrypy.log(traceback=True, severity=40)

        if exc:
            raise 



    def __copy__(self):
        newmap = self.__class__()
        for (k, v,) in self.items():
            newmap[k] = v[:]

        return newmap


    copy = __copy__

    def __repr__(self):
        cls = self.__class__
        return '%s.%s(points=%r)' % (cls.__module__, cls.__name__, self.keys())




def hooks_namespace(k, v):
    hookpoint = k.split('.', 1)[0]
    if isinstance(v, basestring):
        v = cherrypy.lib.attributes(v)
    if not isinstance(v, Hook):
        v = Hook(v)
    cherrypy.serving.request.hooks[hookpoint].append(v)



def request_namespace(k, v):
    if k[:5] == 'body.':
        setattr(cherrypy.serving.request.body, k[5:], v)
    else:
        setattr(cherrypy.serving.request, k, v)



def response_namespace(k, v):
    if k[:8] == 'headers.':
        cherrypy.serving.response.headers[k.split('.', 1)[1]] = v
    else:
        setattr(cherrypy.serving.response, k, v)



def error_page_namespace(k, v):
    if k != 'default':
        k = int(k)
    cherrypy.serving.request.error_page[k] = v


hookpoints = ['on_start_resource',
 'before_request_body',
 'before_handler',
 'before_finalize',
 'on_end_resource',
 'on_end_request',
 'before_error_response',
 'after_error_response']

class Request(object):
    __metaclass__ = cherrypy._AttributeDocstrings
    prev = None
    prev__doc = '\n    The previous Request object (if any). This should be None\n    unless we are processing an InternalRedirect.'
    local = httputil.Host('127.0.0.1', 80)
    local__doc = 'An httputil.Host(ip, port, hostname) object for the server socket.'
    remote = httputil.Host('127.0.0.1', 1111)
    remote__doc = 'An httputil.Host(ip, port, hostname) object for the client socket.'
    scheme = 'http'
    scheme__doc = "\n    The protocol used between client and server. In most cases,\n    this will be either 'http' or 'https'."
    server_protocol = 'HTTP/1.1'
    server_protocol__doc = '\n    The HTTP version for which the HTTP server is at least\n    conditionally compliant.'
    base = ''
    base__doc = "The (scheme://host) portion of the requested URL.\n    In some cases (e.g. when proxying via mod_rewrite), this may contain\n    path segments which cherrypy.url uses when constructing url's, but\n    which otherwise are ignored by CherryPy. Regardless, this value\n    MUST NOT end in a slash."
    request_line = ''
    request_line__doc = '\n    The complete Request-Line received from the client. This is a\n    single string consisting of the request method, URI, and protocol\n    version (joined by spaces). Any final CRLF is removed.'
    method = 'GET'
    method__doc = '\n    Indicates the HTTP method to be performed on the resource identified\n    by the Request-URI. Common methods include GET, HEAD, POST, PUT, and\n    DELETE. CherryPy allows any extension method; however, various HTTP\n    servers and gateways may restrict the set of allowable methods.\n    CherryPy applications SHOULD restrict the set (on a per-URI basis).'
    query_string = ''
    query_string__doc = "\n    The query component of the Request-URI, a string of information to be\n    interpreted by the resource. The query portion of a URI follows the\n    path component, and is separated by a '?'. For example, the URI\n    'http://www.cherrypy.org/wiki?a=3&b=4' has the query component,\n    'a=3&b=4'."
    query_string_encoding = 'utf8'
    query_string_encoding__doc = "\n    The encoding expected for query string arguments after % HEX HEX decoding).\n    If a query string is provided that cannot be decoded with this encoding,\n    404 is raised (since technically it's a different URI). If you want\n    arbitrary encodings to not error, set this to 'Latin-1'; you can then\n    encode back to bytes and re-decode to whatever encoding you like later.\n    "
    protocol = (1, 1)
    protocol__doc = "The HTTP protocol version corresponding to the set\n        of features which should be allowed in the response. If BOTH\n        the client's request message AND the server's level of HTTP\n        compliance is HTTP/1.1, this attribute will be the tuple (1, 1).\n        If either is 1.0, this attribute will be the tuple (1, 0).\n        Lower HTTP protocol versions are not explicitly supported."
    params = {}
    params__doc = "\n    A dict which combines query string (GET) and request entity (POST)\n    variables. This is populated in two stages: GET params are added\n    before the 'on_start_resource' hook, and POST params are added\n    between the 'before_request_body' and 'before_handler' hooks."
    header_list = []
    header_list__doc = '\n    A list of the HTTP request headers as (name, value) tuples.\n    In general, you should use request.headers (a dict) instead.'
    headers = httputil.HeaderMap()
    headers__doc = "\n    A dict-like object containing the request headers. Keys are header\n    names (in Title-Case format); however, you may get and set them in\n    a case-insensitive manner. That is, headers['Content-Type'] and\n    headers['content-type'] refer to the same value. Values are header\n    values (decoded according to RFC 2047 if necessary). See also:\n    httputil.HeaderMap, httputil.HeaderElement."
    cookie = SimpleCookie()
    cookie__doc = 'See help(Cookie).'
    body = None
    body__doc = 'See help(cherrypy.request.body)'
    rfile = None
    rfile__doc = "\n    If the request included an entity (body), it will be available\n    as a stream in this attribute. However, the rfile will normally\n    be read for you between the 'before_request_body' hook and the\n    'before_handler' hook, and the resulting string is placed into\n    either request.params or the request.body attribute.\n    \n    You may disable the automatic consumption of the rfile by setting\n    request.process_request_body to False, either in config for the desired\n    path, or in an 'on_start_resource' or 'before_request_body' hook.\n    \n    WARNING: In almost every case, you should not attempt to read from the\n    rfile stream after CherryPy's automatic mechanism has read it. If you\n    turn off the automatic parsing of rfile, you should read exactly the\n    number of bytes specified in request.headers['Content-Length'].\n    Ignoring either of these warnings may result in a hung request thread\n    or in corruption of the next (pipelined) request.\n    "
    process_request_body = True
    process_request_body__doc = '\n    If True, the rfile (if any) is automatically read and parsed,\n    and the result placed into request.params or request.body.'
    methods_with_bodies = ('POST', 'PUT')
    methods_with_bodies__doc = '\n    A sequence of HTTP methods for which CherryPy will automatically\n    attempt to read a body from the rfile.'
    body = None
    body__doc = "\n    If the request Content-Type is 'application/x-www-form-urlencoded'\n    or multipart, this will be None. Otherwise, this will contain the\n    request entity body as an open file object (which you can .read());\n    this value is set between the 'before_request_body' and 'before_handler'\n    hooks (assuming that process_request_body is True)."
    body_params = None
    body_params__doc = '\n    If the request Content-Type is \'application/x-www-form-urlencoded\' or\n    multipart, this will be a dict of the params pulled from the entity\n    body; that is, it will be the portion of request.params that come\n    from the message body (sometimes called "POST params", although they\n    can be sent with various HTTP method verbs). This value is set between\n    the \'before_request_body\' and \'before_handler\' hooks (assuming that\n    process_request_body is True).'
    dispatch = cherrypy.dispatch.Dispatcher()
    dispatch__doc = "\n    The object which looks up the 'page handler' callable and collects\n    config for the current request based on the path_info, other\n    request attributes, and the application architecture. The core\n    calls the dispatcher as early as possible, passing it a 'path_info'\n    argument.\n    \n    The default dispatcher discovers the page handler by matching path_info\n    to a hierarchical arrangement of objects, starting at request.app.root.\n    See help(cherrypy.dispatch) for more information."
    script_name = ''
    script_name__doc = '\n    The \'mount point\' of the application which is handling this request.\n    \n    This attribute MUST NOT end in a slash. If the script_name refers to\n    the root of the URI, it MUST be an empty string (not "/").\n    '
    path_info = '/'
    path_info__doc = "\n    The 'relative path' portion of the Request-URI. This is relative\n    to the script_name ('mount point') of the application which is\n    handling this request."
    login = None
    login__doc = "\n    When authentication is used during the request processing this is\n    set to 'False' if it failed and to the 'username' value if it succeeded.\n    The default 'None' implies that no authentication happened."
    app = None
    app__doc = 'The cherrypy.Application object which is handling this request.'
    handler = None
    handler__doc = '\n    The function, method, or other callable which CherryPy will call to\n    produce the response. The discovery of the handler and the arguments\n    it will receive are determined by the request.dispatch object.\n    By default, the handler is discovered by walking a tree of objects\n    starting at request.app.root, and is then passed all HTTP params\n    (from the query string and POST body) as keyword arguments.'
    toolmaps = {}
    toolmaps__doc = '\n    A nested dict of all Toolboxes and Tools in effect for this request,\n    of the form: {Toolbox.namespace: {Tool.name: config dict}}.'
    config = None
    config__doc = '\n    A flat dict of all configuration entries which apply to the\n    current request. These entries are collected from global config,\n    application config (based on request.path_info), and from handler\n    config (exactly how is governed by the request.dispatch object in\n    effect for this request; by default, handler config can be attached\n    anywhere in the tree between request.app.root and the final handler,\n    and inherits downward).'
    is_index = None
    is_index__doc = "\n    This will be True if the current request is mapped to an 'index'\n    resource handler (also, a 'default' handler if path_info ends with\n    a slash). The value may be used to automatically redirect the\n    user-agent to a 'more canonical' URL which either adds or removes\n    the trailing slash. See cherrypy.tools.trailing_slash."
    hooks = HookMap(hookpoints)
    hooks__doc = '\n    A HookMap (dict-like object) of the form: {hookpoint: [hook, ...]}.\n    Each key is a str naming the hook point, and each value is a list\n    of hooks which will be called at that hook point during this request.\n    The list of hooks is generally populated as early as possible (mostly\n    from Tools specified in config), but may be extended at any time.\n    See also: _cprequest.Hook, _cprequest.HookMap, and cherrypy.tools.'
    error_response = cherrypy.HTTPError(500).set_response
    error_response__doc = '\n    The no-arg callable which will handle unexpected, untrapped errors\n    during request processing. This is not used for expected exceptions\n    (like NotFound, HTTPError, or HTTPRedirect) which are raised in\n    response to expected conditions (those should be customized either\n    via request.error_page or by overriding HTTPError.set_response).\n    By default, error_response uses HTTPError(500) to return a generic\n    error response to the user-agent.'
    error_page = {}
    error_page__doc = "\n    A dict of {error code: response filename or callable} pairs.\n    \n    The error code must be an int representing a given HTTP error code,\n    or the string 'default', which will be used if no matching entry\n    is found for a given numeric code.\n    \n    If a filename is provided, the file should contain a Python string-\n    formatting template, and can expect by default to receive format \n    values with the mapping keys %(status)s, %(message)s, %(traceback)s,\n    and %(version)s. The set of format mappings can be extended by\n    overriding HTTPError.set_response.\n    \n    If a callable is provided, it will be called by default with keyword\n    arguments 'status', 'message', 'traceback', and 'version', as for a\n    string-formatting template. The callable must return a string or iterable of\n    strings which will be set to response.body. It may also override headers or\n    perform any other processing.\n    \n    If no entry is given for an error code, and no 'default' entry exists,\n    a default template will be used.\n    "
    show_tracebacks = True
    show_tracebacks__doc = '\n    If True, unexpected errors encountered during request processing will\n    include a traceback in the response body.'
    show_mismatched_params = True
    show_mismatched_params__doc = '\n    If True, mismatched parameters encountered during PageHandler invocation\n    processing will be included in the response body.'
    throws = (KeyboardInterrupt, SystemExit, cherrypy.InternalRedirect)
    throws__doc = 'The sequence of exceptions which Request.run does not trap.'
    throw_errors = False
    throw_errors__doc = "\n    If True, Request.run will not trap any errors (except HTTPRedirect and\n    HTTPError, which are more properly called 'exceptions', not errors)."
    closed = False
    closed__doc = '\n    True once the close method has been called, False otherwise.'
    stage = None
    stage__doc = '\n    A string containing the stage reached in the request-handling process.\n    This is useful when debugging a live server with hung requests.'
    namespaces = _cpconfig.NamespaceSet(**{'hooks': hooks_namespace,
     'request': request_namespace,
     'response': response_namespace,
     'error_page': error_page_namespace,
     'tools': cherrypy.tools})

    def __init__(self, local_host, remote_host, scheme = 'http', server_protocol = 'HTTP/1.1'):
        self.local = local_host
        self.remote = remote_host
        self.scheme = scheme
        self.server_protocol = server_protocol
        self.closed = False
        self.error_page = self.error_page.copy()
        self.namespaces = self.namespaces.copy()
        self.stage = None



    def close(self):
        if not self.closed:
            self.closed = True
            self.stage = 'on_end_request'
            self.hooks.run('on_end_request')
            self.stage = 'close'



    def run(self, method, path, query_string, req_protocol, headers, rfile):
        response = cherrypy.serving.response
        self.stage = 'run'
        try:
            self.error_response = cherrypy.HTTPError(500).set_response
            self.method = method
            path = path or '/'
            self.query_string = query_string or ''
            self.params = {}
            rp = (int(req_protocol[5]), int(req_protocol[7]))
            sp = (int(self.server_protocol[5]), int(self.server_protocol[7]))
            self.protocol = min(rp, sp)
            response.headers.protocol = self.protocol
            url = path
            if query_string:
                url += '?' + query_string
            self.request_line = '%s %s %s' % (method, url, req_protocol)
            self.header_list = list(headers)
            self.headers = httputil.HeaderMap()
            self.rfile = rfile
            self.body = None
            self.cookie = SimpleCookie()
            self.handler = None
            self.script_name = self.app.script_name
            self.path_info = pi = path[len(self.script_name):]
            self.stage = 'respond'
            self.respond(pi)
        except self.throws:
            raise 
        except:
            if self.throw_errors:
                raise 
            else:
                cherrypy.log(traceback=True, severity=40)
                if self.show_tracebacks:
                    body = format_exc()
                else:
                    body = ''
                r = bare_error(body)
                (response.output_status, response.header_list, response.body,) = r
        if self.method == 'HEAD':
            response.body = []
        try:
            cherrypy.log.access()
        except:
            cherrypy.log.error(traceback=True)
        if response.timed_out:
            raise cherrypy.TimeoutError()
        return response



    def respond(self, path_info):
        response = cherrypy.serving.response
        try:
            try:
                try:
                    if self.app is None:
                        raise cherrypy.NotFound()
                    self.stage = 'process_headers'
                    self.process_headers()
                    self.hooks = self.__class__.hooks.copy()
                    self.toolmaps = {}
                    self.stage = 'get_resource'
                    self.get_resource(path_info)
                    self.body = _cpreqbody.RequestBody(self.rfile, self.headers, request_params=self.params)
                    self.namespaces(self.config)
                    self.stage = 'on_start_resource'
                    self.hooks.run('on_start_resource')
                    self.stage = 'process_query_string'
                    self.process_query_string()
                    if self.process_request_body:
                        if self.method not in self.methods_with_bodies:
                            self.process_request_body = False
                    self.stage = 'before_request_body'
                    self.hooks.run('before_request_body')
                    if self.process_request_body:
                        self.body.process()
                    self.stage = 'before_handler'
                    self.hooks.run('before_handler')
                    if self.handler:
                        self.stage = 'handler'
                        response.body = self.handler()
                    self.stage = 'before_finalize'
                    self.hooks.run('before_finalize')
                    response.finalize()
                except (cherrypy.HTTPRedirect, cherrypy.HTTPError) as inst:
                    inst.set_response()
                    self.stage = 'before_finalize (HTTPError)'
                    self.hooks.run('before_finalize')
                    response.finalize()

            finally:
                self.stage = 'on_end_resource'
                self.hooks.run('on_end_resource')

        except self.throws:
            raise 
        except:
            if self.throw_errors:
                raise 
            self.handle_error()



    def process_query_string(self):
        try:
            p = httputil.parse_query_string(self.query_string, encoding=self.query_string_encoding)
        except UnicodeDecodeError:
            raise cherrypy.HTTPError(404, 'The given query string could not be processed. Query strings for this resource must be encoded with %r.' % self.query_string_encoding)
        for (key, value,) in p.items():
            if isinstance(key, unicode):
                del p[key]
                p[key.encode(self.query_string_encoding)] = value

        self.params.update(p)



    def process_headers(self):
        headers = self.headers
        for (name, value,) in self.header_list:
            name = name.title()
            value = value.strip()
            if '=?' in value:
                dict.__setitem__(headers, name, httputil.decode_TEXT(value))
            else:
                dict.__setitem__(headers, name, value)
            if name == 'Cookie':
                try:
                    self.cookie.load(value)
                except CookieError:
                    msg = 'Illegal cookie name %s' % value.split('=')[0]
                    raise cherrypy.HTTPError(400, msg)

        if not dict.__contains__(headers, 'Host'):
            if self.protocol >= (1, 1):
                msg = "HTTP/1.1 requires a 'Host' request header."
                raise cherrypy.HTTPError(400, msg)
        host = dict.get(headers, 'Host')
        if not host:
            host = self.local.name or self.local.ip
        self.base = '%s://%s' % (self.scheme, host)



    def get_resource(self, path):
        dispatch = self.app.find_config(path, 'request.dispatch', self.dispatch)
        dispatch(path)



    def handle_error(self):
        try:
            self.hooks.run('before_error_response')
            if self.error_response:
                self.error_response()
            self.hooks.run('after_error_response')
            cherrypy.serving.response.finalize()
        except cherrypy.HTTPRedirect as inst:
            inst.set_response()
            cherrypy.serving.response.finalize()



    def _get_body_params(self):
        warnings.warn('body_params is deprecated in CherryPy 3.2, will be removed in CherryPy 3.3.', DeprecationWarning)
        return self.body.params


    body_params = property(_get_body_params, doc='\n    If the request Content-Type is \'application/x-www-form-urlencoded\' or\n    multipart, this will be a dict of the params pulled from the entity\n    body; that is, it will be the portion of request.params that come\n    from the message body (sometimes called "POST params", although they\n    can be sent with various HTTP method verbs). This value is set between\n    the \'before_request_body\' and \'before_handler\' hooks (assuming that\n    process_request_body is True).\n    \n    Deprecated in 3.2, will be removed for 3.3')


class ResponseBody(object):

    def __get__(self, obj, objclass = None):
        if obj is None:
            return self
        else:
            return obj._body



    def __set__(self, obj, value):
        if isinstance(value, basestring):
            if value:
                value = [value]
            else:
                value = []
        elif isinstance(value, types.FileType):
            value = file_generator(value)
        elif value is None:
            value = []
        obj._body = value




class Response(object):
    __metaclass__ = cherrypy._AttributeDocstrings
    status = ''
    status__doc = 'The HTTP Status-Code and Reason-Phrase.'
    header_list = []
    header_list__doc = '\n    A list of the HTTP response headers as (name, value) tuples.\n    In general, you should use response.headers (a dict) instead.'
    headers = httputil.HeaderMap()
    headers__doc = "\n    A dict-like object containing the response headers. Keys are header\n    names (in Title-Case format); however, you may get and set them in\n    a case-insensitive manner. That is, headers['Content-Type'] and\n    headers['content-type'] refer to the same value. Values are header\n    values (decoded according to RFC 2047 if necessary). See also:\n    httputil.HeaderMap, httputil.HeaderElement."
    cookie = SimpleCookie()
    cookie__doc = 'See help(Cookie).'
    body = ResponseBody()
    body__doc = 'The body (entity) of the HTTP response.'
    time = None
    time__doc = 'The value of time.time() when created. Use in HTTP dates.'
    timeout = 300
    timeout__doc = 'Seconds after which the response will be aborted.'
    timed_out = False
    timed_out__doc = '\n    Flag to indicate the response should be aborted, because it has\n    exceeded its timeout.'
    stream = False
    stream__doc = 'If False, buffer the response body.'

    def __init__(self):
        self.status = None
        self.header_list = None
        self._body = []
        self.time = time.time()
        self.headers = httputil.HeaderMap()
        dict.update(self.headers, {'Content-Type': 'text/html',
         'Server': 'CherryPy/' + cherrypy.__version__,
         'Date': httputil.HTTPDate(self.time)})
        self.cookie = SimpleCookie()



    def collapse_body(self):
        if isinstance(self.body, basestring):
            return self.body
        newbody = ''.join([ chunk for chunk in self.body ])
        self.body = newbody
        return newbody



    def finalize(self):
        try:
            (code, reason, _,) = httputil.valid_status(self.status)
        except ValueError as x:
            raise cherrypy.HTTPError(500, x.args[0])
        headers = self.headers
        self.output_status = str(code) + ' ' + headers.encode(reason)
        if self.stream:
            if dict.get(headers, 'Content-Length') is None:
                dict.pop(headers, 'Content-Length', None)
        elif code < 200 or code in (204, 205, 304):
            dict.pop(headers, 'Content-Length', None)
            self.body = ''
        elif dict.get(headers, 'Content-Length') is None:
            content = self.collapse_body()
            dict.__setitem__(headers, 'Content-Length', len(content))
        self.header_list = h = headers.output()
        cookie = self.cookie.output()
        if cookie:
            for line in cookie.split('\n'):
                if line.endswith('\r'):
                    line = line[:-1]
                (name, value,) = line.split(': ', 1)
                if isinstance(name, unicode):
                    name = name.encode('ISO-8859-1')
                if isinstance(value, unicode):
                    value = headers.encode(value)
                h.append((name, value))




    def check_timeout(self):
        if time.time() > self.time + self.timeout:
            self.timed_out = True




