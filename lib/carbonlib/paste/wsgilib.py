from paste.request import get_cookies, parse_querystring, parse_formvars
from paste.request import construct_url, path_info_split, path_info_pop
from paste.response import HeaderDict, has_header, header_value, remove_header
from paste.response import error_body_response, error_response, error_response_app
from traceback import print_exception
import urllib
from cStringIO import StringIO
import sys
from urlparse import urlsplit
import warnings
__all__ = ['add_close',
 'add_start_close',
 'capture_output',
 'catch_errors',
 'catch_errors_app',
 'chained_app_iters',
 'construct_url',
 'dump_environ',
 'encode_unicode_app_iter',
 'error_body_response',
 'error_response',
 'get_cookies',
 'has_header',
 'header_value',
 'interactive',
 'intercept_output',
 'path_info_pop',
 'path_info_split',
 'raw_interactive',
 'send_file']

class add_close(object):

    def __init__(self, app_iterable, close_func):
        self.app_iterable = app_iterable
        self.app_iter = iter(app_iterable)
        self.close_func = close_func
        self._closed = False



    def __iter__(self):
        return self



    def next(self):
        return self.app_iter.next()



    def close(self):
        self._closed = True
        if hasattr(self.app_iterable, 'close'):
            self.app_iterable.close()
        self.close_func()



    def __del__(self):
        if not self._closed:
            print >> sys.stderr, 'Error: app_iter.close() was not called when finishing WSGI request. finalization function %s not called' % self.close_func




class add_start_close(object):

    def __init__(self, app_iterable, start_func, close_func = None):
        self.app_iterable = app_iterable
        self.app_iter = iter(app_iterable)
        self.first = True
        self.start_func = start_func
        self.close_func = close_func
        self._closed = False



    def __iter__(self):
        return self



    def next(self):
        if self.first:
            self.start_func()
            self.first = False
        return self.app_iter.next()



    def close(self):
        self._closed = True
        if hasattr(self.app_iterable, 'close'):
            self.app_iterable.close()
        if self.close_func is not None:
            self.close_func()



    def __del__(self):
        if not self._closed:
            print >> sys.stderr, 'Error: app_iter.close() was not called when finishing WSGI request. finalization function %s not called' % self.close_func




class chained_app_iters(object):

    def __init__(self, *chained):
        self.app_iters = chained
        self.chained = [ iter(item) for item in chained ]
        self._closed = False



    def __iter__(self):
        return self



    def next(self):
        if len(self.chained) == 1:
            return self.chained[0].next()
        try:
            return self.chained[0].next()
        except StopIteration:
            self.chained.pop(0)
            return self.next()



    def close(self):
        self._closed = True
        got_exc = None
        for app_iter in self.app_iters:
            try:
                if hasattr(app_iter, 'close'):
                    app_iter.close()
            except:
                got_exc = sys.exc_info()

        if got_exc:
            raise got_exc[0], got_exc[1], got_exc[2]



    def __del__(self):
        if not self._closed:
            print >> sys.stderr, 'Error: app_iter.close() was not called when finishing WSGI request. finalization function %s not called' % self.close_func




class encode_unicode_app_iter(object):

    def __init__(self, app_iterable, encoding = sys.getdefaultencoding(), errors = 'strict'):
        self.app_iterable = app_iterable
        self.app_iter = iter(app_iterable)
        self.encoding = encoding
        self.errors = errors



    def __iter__(self):
        return self



    def next(self):
        content = self.app_iter.next()
        if isinstance(content, unicode):
            content = content.encode(self.encoding, self.errors)
        return content



    def close(self):
        if hasattr(self.app_iterable, 'close'):
            self.app_iterable.close()




def catch_errors(application, environ, start_response, error_callback, ok_callback = None):
    try:
        app_iter = application(environ, start_response)
    except:
        error_callback(sys.exc_info())
        raise 
    if type(app_iter) in (list, tuple):
        if ok_callback:
            ok_callback()
        return app_iter
    else:
        return _wrap_app_iter(app_iter, error_callback, ok_callback)



class _wrap_app_iter(object):

    def __init__(self, app_iterable, error_callback, ok_callback):
        self.app_iterable = app_iterable
        self.app_iter = iter(app_iterable)
        self.error_callback = error_callback
        self.ok_callback = ok_callback
        if hasattr(self.app_iterable, 'close'):
            self.close = self.app_iterable.close



    def __iter__(self):
        return self



    def next(self):
        try:
            return self.app_iter.next()
        except StopIteration:
            if self.ok_callback:
                self.ok_callback()
            raise 
        except:
            self.error_callback(sys.exc_info())
            raise 




def catch_errors_app(application, environ, start_response, error_callback_app, ok_callback = None, catch = Exception):
    try:
        app_iter = application(environ, start_response)
    except catch:
        return error_callback_app(environ, start_response, sys.exc_info())
    if type(app_iter) in (list, tuple):
        if ok_callback is not None:
            ok_callback()
        return app_iter
    else:
        return _wrap_app_iter_app(environ, start_response, app_iter, error_callback_app, ok_callback, catch=catch)



class _wrap_app_iter_app(object):

    def __init__(self, environ, start_response, app_iterable, error_callback_app, ok_callback, catch = Exception):
        self.environ = environ
        self.start_response = start_response
        self.app_iterable = app_iterable
        self.app_iter = iter(app_iterable)
        self.error_callback_app = error_callback_app
        self.ok_callback = ok_callback
        self.catch = catch
        if hasattr(self.app_iterable, 'close'):
            self.close = self.app_iterable.close



    def __iter__(self):
        return self



    def next(self):
        try:
            return self.app_iter.next()
        except StopIteration:
            if self.ok_callback:
                self.ok_callback()
            raise 
        except self.catch:
            if hasattr(self.app_iterable, 'close'):
                try:
                    self.app_iterable.close()
                except:
                    pass
            new_app_iterable = self.error_callback_app(self.environ, self.start_response, sys.exc_info())
            app_iter = iter(new_app_iterable)
            if hasattr(new_app_iterable, 'close'):
                self.close = new_app_iterable.close
            self.next = app_iter.next
            return self.next()




def raw_interactive(application, path = '', raise_on_wsgi_error = False, **environ):
    if raise_on_wsgi_error:
        errors = ErrorRaiser()
    else:
        errors = StringIO()
    basic_environ = {'REQUEST_METHOD': 'GET',
     'SCRIPT_NAME': '',
     'PATH_INFO': '',
     'SERVER_NAME': 'localhost',
     'SERVER_PORT': '80',
     'SERVER_PROTOCOL': 'HTTP/1.0',
     'wsgi.version': (1, 0),
     'wsgi.url_scheme': 'http',
     'wsgi.input': StringIO(''),
     'wsgi.errors': errors,
     'wsgi.multithread': False,
     'wsgi.multiprocess': False,
     'wsgi.run_once': False}
    if path:
        (_, _, path_info, query, fragment,) = urlsplit(str(path))
        path_info = urllib.unquote(path_info)
        (path_info, query,) = (str(path_info), str(query))
        basic_environ['PATH_INFO'] = path_info
        if query:
            basic_environ['QUERY_STRING'] = query
    for (name, value,) in environ.items():
        name = name.replace('__', '.')
        basic_environ[name] = value

    if 'SERVER_NAME' in basic_environ and 'HTTP_HOST' not in basic_environ:
        basic_environ['HTTP_HOST'] = basic_environ['SERVER_NAME']
    istream = basic_environ['wsgi.input']
    if isinstance(istream, str):
        basic_environ['wsgi.input'] = StringIO(istream)
        basic_environ['CONTENT_LENGTH'] = len(istream)
    data = {}
    output = []
    headers_set = []
    headers_sent = []

    def start_response(status, headers, exc_info = None):
        if exc_info:
            try:
                if headers_sent:
                    raise exc_info[0], exc_info[1], exc_info[2]

            finally:
                exc_info = None

        elif headers_set:
            raise AssertionError('Headers already set and no exc_info!')
        headers_set.append(True)
        data['status'] = status
        data['headers'] = headers
        return output.append


    app_iter = application(basic_environ, start_response)
    try:
        try:
            for s in app_iter:
                if not isinstance(s, str):
                    raise ValueError('The app_iter response can only contain str (not unicode); got: %r' % s)
                headers_sent.append(True)
                if not headers_set:
                    raise AssertionError('Content sent w/o headers!')
                output.append(s)

        except TypeError as e:
            e.args = (e.args[0] + ' iterable: %r' % app_iter,) + e.args[1:]
            raise 

    finally:
        if hasattr(app_iter, 'close'):
            app_iter.close()

    return (data['status'],
     data['headers'],
     ''.join(output),
     errors.getvalue())



class ErrorRaiser(object):

    def flush(self):
        pass



    def write(self, value):
        if not value:
            return 
        raise AssertionError('No errors should be written (got: %r)' % value)



    def writelines(self, seq):
        raise AssertionError('No errors should be written (got lines: %s)' % list(seq))



    def getvalue(self):
        return ''




def interactive(*args, **kw):
    (status, headers, content, errors,) = raw_interactive(*args, **kw)
    full = StringIO()
    if errors:
        full.write('Errors:\n')
        full.write(errors.strip())
        full.write('\n----------end errors\n')
    full.write(status + '\n')
    for (name, value,) in headers:
        full.write('%s: %s\n' % (name, value))

    full.write('\n')
    full.write(content)
    return full.getvalue()


interactive.proxy = 'raw_interactive'

def dump_environ(environ, start_response):
    output = []
    keys = environ.keys()
    keys.sort()
    for k in keys:
        v = str(environ[k]).replace('\n', '\n    ')
        output.append('%s: %s\n' % (k, v))

    output.append('\n')
    content_length = environ.get('CONTENT_LENGTH', '')
    if content_length:
        output.append(environ['wsgi.input'].read(int(content_length)))
        output.append('\n')
    output = ''.join(output)
    headers = [('Content-Type', 'text/plain'), ('Content-Length', str(len(output)))]
    start_response('200 OK', headers)
    return [output]



def send_file(filename):
    warnings.warn('wsgilib.send_file has been moved to paste.fileapp.FileApp', DeprecationWarning, 2)
    from paste import fileapp
    return fileapp.FileApp(filename)



def capture_output(environ, start_response, application):
    warnings.warn('wsgilib.capture_output has been deprecated in favor of wsgilib.intercept_output', DeprecationWarning, 2)
    data = []
    output = StringIO()

    def replacement_start_response(status, headers, exc_info = None):
        if data:
            data[:] = []
        data.append(status)
        data.append(headers)
        start_response(status, headers, exc_info)
        return output.write


    app_iter = application(environ, replacement_start_response)
    try:
        for item in app_iter:
            output.write(item)


    finally:
        if hasattr(app_iter, 'close'):
            app_iter.close()

    if not data:
        data.append(None)
    if len(data) < 2:
        data.append(None)
    data.append(output.getvalue())
    return data



def intercept_output(environ, application, conditional = None, start_response = None):
    if conditional is not None and start_response is None:
        raise TypeError('If you provide conditional you must also provide start_response')
    data = []
    output = StringIO()

    def replacement_start_response(status, headers, exc_info = None):
        if conditional is not None and not conditional(status, headers):
            data.append(None)
            return start_response(status, headers, exc_info)
        if data:
            data[:] = []
        data.append(status)
        data.append(headers)
        return output.write


    app_iter = application(environ, replacement_start_response)
    if data[0] is None:
        return (None, None, app_iter)
    try:
        for item in app_iter:
            output.write(item)


    finally:
        if hasattr(app_iter, 'close'):
            app_iter.close()

    if not data:
        data.append(None)
    if len(data) < 2:
        data.append(None)
    data.append(output.getvalue())
    return data



class ResponseHeaderDict(HeaderDict):

    def __init__(self, *args, **kw):
        warnings.warn('The class wsgilib.ResponseHeaderDict has been moved to paste.response.HeaderDict', DeprecationWarning, 2)
        HeaderDict.__init__(self, *args, **kw)




def _warn_deprecated(new_func):
    new_name = new_func.func_name
    new_path = new_func.func_globals['__name__'] + '.' + new_name

    def replacement(*args, **kw):
        warnings.warn('The function wsgilib.%s has been moved to %s' % (new_name, new_path), DeprecationWarning, 2)
        return new_func(*args, **kw)


    try:
        replacement.func_name = new_func.func_name
    except:
        pass
    return replacement


for _name in __all__:
    _func = globals()[_name]
    if hasattr(_func, 'func_globals') and _func.func_globals['__name__'] != __name__:
        globals()[_name] = _warn_deprecated(_func)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

