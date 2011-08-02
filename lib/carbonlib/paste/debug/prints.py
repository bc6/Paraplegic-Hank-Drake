from cStringIO import StringIO
import re
import cgi
from paste.util import threadedprint
from paste import wsgilib
from paste import response
import sys
_threadedprint_installed = False
__all__ = ['PrintDebugMiddleware']

class TeeFile(object):

    def __init__(self, files):
        self.files = files



    def write(self, v):
        if isinstance(v, unicode):
            v = str(v)
        for file in self.files:
            file.write(v)





class PrintDebugMiddleware(object):
    log_template = '<pre style="width: 40%%; border: 2px solid #000; white-space: normal; background-color: #ffd; color: #000; float: right;"><b style="border-bottom: 1px solid #000">Log messages</b><br>%s</pre>'

    def __init__(self, app, global_conf = None, force_content_type = False, print_wsgi_errors = True, replace_stdout = False):
        self.app = app
        self.force_content_type = force_content_type
        if isinstance(print_wsgi_errors, basestring):
            from paste.deploy.converters import asbool
            print_wsgi_errors = asbool(print_wsgi_errors)
        self.print_wsgi_errors = print_wsgi_errors
        self.replace_stdout = replace_stdout
        self._threaded_print_stdout = None



    def __call__(self, environ, start_response):
        global _threadedprint_installed
        if environ.get('paste.testing'):
            return self.app(environ, start_response)
        if not _threadedprint_installed or self._threaded_print_stdout is not sys.stdout:
            _threadedprint_installed = True
            threadedprint.install(leave_stdout=not self.replace_stdout)
            self._threaded_print_stdout = sys.stdout
        removed = []

        def remove_printdebug():
            removed.append(None)


        environ['paste.remove_printdebug'] = remove_printdebug
        logged = StringIO()
        listeners = [logged]
        environ['paste.printdebug_listeners'] = listeners
        if self.print_wsgi_errors:
            listeners.append(environ['wsgi.errors'])
        replacement_stdout = TeeFile(listeners)
        threadedprint.register(replacement_stdout)
        try:
            (status, headers, body,) = wsgilib.intercept_output(environ, self.app)
            if status is None:
                status = '500 Server Error'
                headers = [('Content-type', 'text/html')]
                start_response(status, headers)
                if not body:
                    body = 'An error occurred'
            content_type = response.header_value(headers, 'content-type')
            if removed or not self.force_content_type and (not content_type or not content_type.startswith('text/html')):
                if replacement_stdout == logged:
                    environ['wsgi.errors'].write(logged.getvalue())
                start_response(status, headers)
                return [body]
            else:
                response.remove_header(headers, 'content-length')
                body = self.add_log(body, logged.getvalue())
                start_response(status, headers)
                return [body]

        finally:
            threadedprint.deregister()



    _body_re = re.compile('<body[^>]*>', re.I)
    _explicit_re = re.compile('<pre\\s*[^>]*id="paste-debug-prints".*?>', re.I + re.S)

    def add_log(self, html, log):
        if not log:
            return html
        else:
            text = cgi.escape(log)
            text = text.replace('\n', '<br>')
            text = text.replace('  ', '&nbsp; ')
            match = self._explicit_re.search(html)
            if not match:
                text = self.log_template % text
                match = self._body_re.search(html)
            if not match:
                return text + html
            return html[:match.end()] + text + html[match.end():]




