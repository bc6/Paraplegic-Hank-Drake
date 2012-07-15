#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\exceptions.py
import sys
from werkzeug._internal import HTTP_STATUS_CODES, _get_environ

class HTTPException(Exception):
    code = None
    description = None

    def __init__(self, description = None):
        Exception.__init__(self, '%d %s' % (self.code, self.name))
        if description is not None:
            self.description = description

    @classmethod
    def wrap(cls, exception, name = None):

        class newcls(cls, exception):

            def __init__(self, arg = None, description = None):
                cls.__init__(self, description)
                exception.__init__(self, arg)

        newcls.__module__ = sys._getframe(1).f_globals.get('__name__')
        newcls.__name__ = name or cls.__name__ + exception.__name__
        return newcls

    @property
    def name(self):
        return HTTP_STATUS_CODES[self.code]

    def get_description(self, environ):
        environ = _get_environ(environ)
        return self.description

    def get_body(self, environ):
        return '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>%(code)s %(name)s</title>\n<h1>%(name)s</h1>\n%(description)s\n' % {'code': self.code,
         'name': escape(self.name),
         'description': self.get_description(environ)}

    def get_headers(self, environ):
        return [('Content-Type', 'text/html')]

    def get_response(self, environ):
        environ = _get_environ(environ)
        from werkzeug.wrappers import BaseResponse
        headers = self.get_headers(environ)
        return BaseResponse(self.get_body(environ), self.code, headers)

    def __call__(self, environ, start_response):
        response = self.get_response(environ)
        return response(environ, start_response)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        if 'description' in self.__dict__:
            txt = self.description
        else:
            txt = self.name
        return '%d: %s' % (self.code, txt)

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self)


class _ProxyException(HTTPException):

    def __init__(self, response):
        Exception.__init__(self, 'proxy exception for %r' % response)
        self.response = response

    def get_response(self, environ):
        return self.response


class BadRequest(HTTPException):
    code = 400
    description = '<p>The browser (or proxy) sent a request that this server could not understand.</p>'


class Unauthorized(HTTPException):
    code = 401
    description = "<p>The server could not verify that you are authorized to access the URL requested.  You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required.</p><p>In case you are allowed to request the document, please check your user-id and password and try again.</p>"


class Forbidden(HTTPException):
    code = 403
    description = "<p>You don't have the permission to access the requested resource. It is either read-protected or not readable by the server.</p>"


class NotFound(HTTPException):
    code = 404
    description = '<p>The requested URL was not found on the server.</p><p>If you entered the URL manually please check your spelling and try again.</p>'


class MethodNotAllowed(HTTPException):
    code = 405

    def __init__(self, valid_methods = None, description = None):
        HTTPException.__init__(self, description)
        self.valid_methods = valid_methods

    def get_headers(self, environ):
        headers = HTTPException.get_headers(self, environ)
        if self.valid_methods:
            headers.append(('Allow', ', '.join(self.valid_methods)))
        return headers

    def get_description(self, environ):
        m = escape(environ.get('REQUEST_METHOD', 'GET'))
        return '<p>The method %s is not allowed for the requested URL.</p>' % m


class NotAcceptable(HTTPException):
    code = 406
    description = '<p>The resource identified by the request is only capable of generating response entities which have content characteristics not acceptable according to the accept headers sent in the request.</p>'


class RequestTimeout(HTTPException):
    code = 408
    description = "<p>The server closed the network connection because the browser didn't finish the request within the specified time.</p>"


class Gone(HTTPException):
    code = 410
    description = '<p>The requested URL is no longer available on this server and there is no forwarding address.</p><p>If you followed a link from a foreign page, please contact the author of this page.'


class LengthRequired(HTTPException):
    code = 411
    description = '<p>A request with this method requires a valid <code>Content-Length</code> header.</p>'


class PreconditionFailed(HTTPException):
    code = 412
    description = '<p>The precondition on the request for the URL failed positive evaluation.</p>'


class RequestEntityTooLarge(HTTPException):
    code = 413
    description = '<p>The data value transmitted exceeds the capacity limit.</p>'


class RequestURITooLarge(HTTPException):
    code = 414
    description = '<p>The length of the requested URL exceeds the capacity limit for this server.  The request cannot be processed.</p>'


class UnsupportedMediaType(HTTPException):
    code = 415
    description = '<p>The server does not support the media type transmitted in the request.</p>'


class InternalServerError(HTTPException):
    code = 500
    description = '<p>The server encountered an internal error and was unable to complete your request.  Either the server is overloaded or there is an error in the application.</p>'


class NotImplemented(HTTPException):
    code = 501
    description = '<p>The server does not support the action requested by the browser.</p>'


class BadGateway(HTTPException):
    code = 502
    description = '<p>The proxy server received an invalid response from an upstream server.</p>'


class ServiceUnavailable(HTTPException):
    code = 503
    description = '<p>The server is temporarily unable to service your request due to maintenance downtime or capacity problems.  Please try again later.</p>'


default_exceptions = {}
__all__ = ['HTTPException']

def _find_exceptions():
    for name, obj in globals().iteritems():
        try:
            if getattr(obj, 'code', None) is not None:
                default_exceptions[obj.code] = obj
                __all__.append(obj.__name__)
        except TypeError:
            continue


_find_exceptions()
del _find_exceptions
HTTPUnicodeError = BadRequest.wrap(UnicodeError, 'HTTPUnicodeError')

class Aborter(object):

    def __init__(self, mapping = None, extra = None):
        if mapping is None:
            mapping = default_exceptions
        self.mapping = dict(mapping)
        if extra is not None:
            self.mapping.update(extra)

    def __call__(self, code, *args, **kwargs):
        if not args and not kwargs and not isinstance(code, (int, long)):
            raise _ProxyException(code)
        if code not in self.mapping:
            raise LookupError('no exception for %r' % code)
        raise self.mapping[code](*args, **kwargs)


abort = Aborter()
from werkzeug.utils import escape