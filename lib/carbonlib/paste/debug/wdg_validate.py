from cStringIO import StringIO
try:
    import subprocess
except ImportError:
    from paste.util import subprocess24 as subprocess
from paste.response import header_value
import re
import cgi
__all__ = ['WDGValidateMiddleware']

class WDGValidateMiddleware(object):
    _end_body_regex = re.compile('</body>', re.I)

    def __init__(self, app, global_conf = None, wdg_path = 'validate'):
        self.app = app
        self.wdg_path = wdg_path



    def __call__(self, environ, start_response):
        output = StringIO()
        response = []

        def writer_start_response(status, headers, exc_info = None):
            response.extend((status, headers))
            start_response(status, headers, exc_info)
            return output.write


        app_iter = self.app(environ, writer_start_response)
        try:
            for s in app_iter:
                output.write(s)


        finally:
            if hasattr(app_iter, 'close'):
                app_iter.close()

        page = output.getvalue()
        (status, headers,) = response
        v = header_value(headers, 'content-type') or ''
        if not v.startswith('text/html') and not v.startswith('text/xhtml') and not v.startswith('application/xhtml'):
            return [page]
        ops = []
        if v.startswith('text/xhtml+xml'):
            ops.append('--xml')
        html_errors = self.call_wdg_validate(self.wdg_path, ops, page)
        if html_errors:
            page = self.add_error(page, html_errors)[0]
            headers.remove(('Content-Length', str(header_value(headers, 'content-length'))))
            headers.append(('Content-Length', str(len(page))))
        return [page]



    def call_wdg_validate(self, wdg_path, ops, page):
        if subprocess is None:
            raise ValueError('This middleware requires the subprocess module from Python 2.4')
        proc = subprocess.Popen([wdg_path] + ops, shell=False, close_fds=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout = proc.communicate(page)[0]
        proc.wait()
        return stdout



    def add_error(self, html_page, html_errors):
        add_text = '<pre style="background-color: #ffd; color: #600; border: 1px solid #000;">%s</pre>' % cgi.escape(html_errors)
        match = self._end_body_regex.search(html_page)
        if match:
            return [html_page[:match.start()] + add_text + html_page[match.start():]]
        else:
            return [html_page + add_text]




def make_wdg_validate_middleware(app, global_conf, wdg_path = 'validate'):
    return WDGValidateMiddleware(app, global_conf, wdg_path=wdg_path)



