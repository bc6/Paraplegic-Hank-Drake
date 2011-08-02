import time
from paste.wsgilib import catch_errors
DEFAULT_THRESHOLD = 1048576
DEFAULT_TIMEOUT = 300
ENVIRON_RECEIVED = 'paste.bytes_received'
REQUEST_STARTED = 'paste.request_started'
REQUEST_FINISHED = 'paste.request_finished'

class _ProgressFile(object):

    def __init__(self, environ, rfile):
        self._ProgressFile_environ = environ
        self._ProgressFile_rfile = rfile
        self.flush = rfile.flush
        self.write = rfile.write
        self.writelines = rfile.writelines



    def __iter__(self):
        environ = self._ProgressFile_environ
        riter = iter(self._ProgressFile_rfile)

        def iterwrap():
            for chunk in riter:
                environ[ENVIRON_RECEIVED] += len(chunk)
                yield chunk



        return iter(iterwrap)



    def read(self, size = -1):
        chunk = self._ProgressFile_rfile.read(size)
        self._ProgressFile_environ[ENVIRON_RECEIVED] += len(chunk)
        return chunk



    def readline(self):
        chunk = self._ProgressFile_rfile.readline()
        self._ProgressFile_environ[ENVIRON_RECEIVED] += len(chunk)
        return chunk



    def readlines(self, hint = None):
        chunk = self._ProgressFile_rfile.readlines(hint)
        self._ProgressFile_environ[ENVIRON_RECEIVED] += len(chunk)
        return chunk




class UploadProgressMonitor(object):

    def __init__(self, application, threshold = None, timeout = None):
        self.application = application
        self.threshold = threshold or DEFAULT_THRESHOLD
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.monitor = []



    def __call__(self, environ, start_response):
        length = environ.get('CONTENT_LENGTH', 0)
        if length and int(length) > self.threshold:
            self.monitor.append(environ)
            environ[ENVIRON_RECEIVED] = 0
            environ[REQUEST_STARTED] = time.time()
            environ[REQUEST_FINISHED] = None
            environ['wsgi.input'] = _ProgressFile(environ, environ['wsgi.input'])

            def finalizer(exc_info = None):
                environ[REQUEST_FINISHED] = time.time()


            return catch_errors(self.application, environ, start_response, finalizer, finalizer)
        return self.application(environ, start_response)



    def uploads(self):
        return self.monitor




class UploadProgressReporter(object):

    def __init__(self, monitor):
        self.monitor = monitor



    def match(self, search_environ, upload_environ):
        if search_environ.get('REMOTE_USER', None) == upload_environ.get('REMOTE_USER', 0):
            return True
        return False



    def report(self, environ):
        retval = {'started': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(environ[REQUEST_STARTED])),
         'finished': '',
         'content_length': environ.get('CONTENT_LENGTH'),
         'bytes_received': environ[ENVIRON_RECEIVED],
         'path_info': environ.get('PATH_INFO', ''),
         'query_string': environ.get('QUERY_STRING', '')}
        finished = environ[REQUEST_FINISHED]
        if finished:
            retval['finished'] = time.strftime('%Y:%m:%d %H:%M:%S', time.gmtime(finished))
        return retval



    def __call__(self, environ, start_response):
        body = []
        for map in [ self.report(env) for env in self.monitor.uploads() if self.match(environ, env) ]:
            parts = []
            for (k, v,) in map.items():
                v = str(v).replace('\\', '\\\\').replace('"', '\\"')
                parts.append('%s: "%s"' % (k, v))

            body.append('{ %s }' % ', '.join(parts))

        body = '[ %s ]' % ', '.join(body)
        start_response('200 OK', [('Content-Type', 'text/plain'), ('Content-Length', len(body))])
        return [body]



__all__ = ['UploadProgressMonitor', 'UploadProgressReporter']
if '__main__' == __name__:
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)

