#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\_cperror.py
from cgi import escape as _escape
from sys import exc_info as _exc_info
from traceback import format_exception as _format_exception
from cherrypy._cpcompat import basestring, iteritems, urljoin as _urljoin
from cherrypy.lib import httputil as _httputil

class CherryPyException(Exception):
    pass


class TimeoutError(CherryPyException):
    pass


class InternalRedirect(CherryPyException):

    def __init__(self, path, query_string = ''):
        import cherrypy
        self.request = cherrypy.serving.request
        self.query_string = query_string
        if '?' in path:
            path, self.query_string = path.split('?', 1)
        path = _urljoin(self.request.path_info, path)
        self.path = path
        CherryPyException.__init__(self, path, self.query_string)


class HTTPRedirect(CherryPyException):
    status = None
    urls = None
    encoding = 'utf-8'

    def __init__(self, urls, status = None, encoding = None):
        import cherrypy
        request = cherrypy.serving.request
        if isinstance(urls, basestring):
            urls = [urls]
        abs_urls = []
        for url in urls:
            if isinstance(url, unicode):
                url = url.encode(encoding or self.encoding)
            url = _urljoin(cherrypy.url(), url)
            abs_urls.append(url)

        self.urls = abs_urls
        if status is None:
            if request.protocol >= (1, 1):
                status = 303
            else:
                status = 302
        else:
            status = int(status)
            if status < 300 or status > 399:
                raise ValueError('status must be between 300 and 399.')
        self.status = status
        CherryPyException.__init__(self, abs_urls, status)

    def set_response(self):
        import cherrypy
        response = cherrypy.serving.response
        response.status = status = self.status
        if status in (300, 301, 302, 303, 307):
            response.headers['Content-Type'] = 'text/html;charset=utf-8'
            response.headers['Location'] = self.urls[0]
            msg = {300: "This resource can be found at <a href='%s'>%s</a>.",
             301: "This resource has permanently moved to <a href='%s'>%s</a>.",
             302: "This resource resides temporarily at <a href='%s'>%s</a>.",
             303: "This resource can be found at <a href='%s'>%s</a>.",
             307: "This resource has moved temporarily to <a href='%s'>%s</a>."}[status]
            msgs = [ msg % (u, u) for u in self.urls ]
            response.body = '<br />\n'.join(msgs)
            response.headers.pop('Content-Length', None)
        elif status == 304:
            for key in ('Allow', 'Content-Encoding', 'Content-Language', 'Content-Length', 'Content-Location', 'Content-MD5', 'Content-Range', 'Content-Type', 'Expires', 'Last-Modified'):
                if key in response.headers:
                    del response.headers[key]

            response.body = None
            response.headers.pop('Content-Length', None)
        elif status == 305:
            response.headers['Location'] = self.urls[0]
            response.body = None
            response.headers.pop('Content-Length', None)
        else:
            raise ValueError('The %s status code is unknown.' % status)

    def __call__(self):
        raise self


def clean_headers(status):
    import cherrypy
    response = cherrypy.serving.response
    respheaders = response.headers
    for key in ['Accept-Ranges',
     'Age',
     'ETag',
     'Location',
     'Retry-After',
     'Vary',
     'Content-Encoding',
     'Content-Length',
     'Expires',
     'Content-Location',
     'Content-MD5',
     'Last-Modified']:
        if key in respheaders:
            del respheaders[key]

    if status != 416:
        if 'Content-Range' in respheaders:
            del respheaders['Content-Range']


class HTTPError(CherryPyException):
    status = None
    code = None
    reason = None

    def __init__(self, status = 500, message = None):
        self.status = status
        try:
            self.code, self.reason, defaultmsg = _httputil.valid_status(status)
        except ValueError as x:
            raise self.__class__(500, x.args[0])

        if self.code < 400 or self.code > 599:
            raise ValueError('status must be between 400 and 599.')
        self._message = message or defaultmsg
        CherryPyException.__init__(self, status, message)

    def set_response(self):
        import cherrypy
        response = cherrypy.serving.response
        clean_headers(self.code)
        response.status = self.status
        tb = None
        if cherrypy.serving.request.show_tracebacks:
            tb = format_exc()
        response.headers['Content-Type'] = 'text/html;charset=utf-8'
        response.headers.pop('Content-Length', None)
        content = self.get_error_page(self.status, traceback=tb, message=self._message)
        response.body = content
        _be_ie_unfriendly(self.code)

    def get_error_page(self, *args, **kwargs):
        return get_error_page(*args, **kwargs)

    def __call__(self):
        raise self


class NotFound(HTTPError):

    def __init__(self, path = None):
        if path is None:
            import cherrypy
            request = cherrypy.serving.request
            path = request.script_name + request.path_info
        self.args = (path,)
        HTTPError.__init__(self, 404, "The path '%s' was not found." % path)


_HTTPErrorTemplate = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\n"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html>\n<head>\n    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"></meta>\n    <title>%(status)s</title>\n    <style type="text/css">\n    #powered_by {\n        margin-top: 20px;\n        border-top: 2px solid black;\n        font-style: italic;\n    }\n\n    #traceback {\n        color: red;\n    }\n    </style>\n</head>\n    <body>\n        <h2>%(status)s</h2>\n        <p>%(message)s</p>\n        <pre id="traceback">%(traceback)s</pre>\n    <div id="powered_by">\n    <span>Powered by <a href="http://www.cherrypy.org">CherryPy %(version)s</a></span>\n    </div>\n    </body>\n</html>\n'

def get_error_page(status, **kwargs):
    import cherrypy
    try:
        code, reason, message = _httputil.valid_status(status)
    except ValueError as x:
        raise cherrypy.HTTPError(500, x.args[0])

    if kwargs.get('status') is None:
        kwargs['status'] = '%s %s' % (code, reason)
    if kwargs.get('message') is None:
        kwargs['message'] = message
    if kwargs.get('traceback') is None:
        kwargs['traceback'] = ''
    if kwargs.get('version') is None:
        kwargs['version'] = cherrypy.__version__
    for k, v in iteritems(kwargs):
        if v is None:
            kwargs[k] = ''
        else:
            kwargs[k] = _escape(kwargs[k])

    pages = cherrypy.serving.request.error_page
    error_page = pages.get(code) or pages.get('default')
    if error_page:
        try:
            if hasattr(error_page, '__call__'):
                return error_page(**kwargs)
            return open(error_page, 'rb').read() % kwargs
        except:
            e = _format_exception(*_exc_info())[-1]
            m = kwargs['message']
            if m:
                m += '<br />'
            m += 'In addition, the custom error page failed:\n<br />%s' % e
            kwargs['message'] = m

    return _HTTPErrorTemplate % kwargs


_ie_friendly_error_sizes = {400: 512,
 403: 256,
 404: 512,
 405: 256,
 406: 512,
 408: 512,
 409: 512,
 410: 256,
 500: 512,
 501: 512,
 505: 512}

def _be_ie_unfriendly(status):
    import cherrypy
    response = cherrypy.serving.response
    s = _ie_friendly_error_sizes.get(status, 0)
    if s:
        s += 1
        content = response.collapse_body()
        l = len(content)
        if l and l < s:
            content = content + ' ' * (s - l)
        response.body = content
        response.headers['Content-Length'] = str(len(content))


def format_exc(exc = None):
    if exc is None:
        exc = _exc_info()
    if exc == (None, None, None):
        return ''
    import traceback
    return ''.join(traceback.format_exception(*exc))


def bare_error(extrabody = None):
    body = 'Unrecoverable error in the server.'
    if extrabody is not None:
        if not isinstance(extrabody, str):
            extrabody = extrabody.encode('utf-8')
        body += '\n' + extrabody
    return ('500 Internal Server Error', [('Content-Type', 'text/plain'), ('Content-Length', str(len(body)))], [body])