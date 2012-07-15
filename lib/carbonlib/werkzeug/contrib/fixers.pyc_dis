#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\contrib\fixers.py
from urllib import unquote
from werkzeug.http import parse_options_header, parse_cache_control_header, parse_set_header, dump_header
from werkzeug.useragents import UserAgent
from werkzeug.datastructures import Headers, ResponseCacheControl

class LighttpdCGIRootFix(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['PATH_INFO'] = environ.get('SCRIPT_NAME', '') + environ.get('PATH_INFO', '')
        environ['SCRIPT_NAME'] = ''
        return self.app(environ, start_response)


class PathInfoFromRequestUriFix(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        for key in ('REQUEST_URL', 'REQUEST_URI', 'UNENCODED_URL'):
            if key not in environ:
                continue
            request_uri = unquote(environ[key])
            script_name = unquote(environ.get('SCRIPT_NAME', ''))
            if request_uri.startswith(script_name):
                environ['PATH_INFO'] = request_uri[len(script_name):].split('?', 1)[0]
                break

        return self.app(environ, start_response)


class ProxyFix(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        getter = environ.get
        forwarded_for = getter('HTTP_X_FORWARDED_FOR', '').split(',')
        forwarded_host = getter('HTTP_X_FORWARDED_HOST', '')
        environ.update({'werkzeug.proxy_fix.orig_remote_addr': getter('REMOTE_ADDR'),
         'werkzeug.proxy_fix.orig_http_host': getter('HTTP_HOST')})
        if forwarded_for:
            environ['REMOTE_ADDR'] = forwarded_for[0].strip()
        if forwarded_host:
            environ['HTTP_HOST'] = forwarded_host
        return self.app(environ, start_response)


class HeaderRewriterFix(object):

    def __init__(self, app, remove_headers = None, add_headers = None):
        self.app = app
        self.remove_headers = set((x.lower() for x in remove_headers or ()))
        self.add_headers = list(add_headers or ())

    def __call__(self, environ, start_response):

        def rewriting_start_response(status, headers, exc_info = None):
            new_headers = []
            for key, value in headers:
                if key.lower() not in self.remove_headers:
                    new_headers.append((key, value))

            new_headers += self.add_headers
            return start_response(status, new_headers, exc_info)

        return self.app(environ, rewriting_start_response)


class InternetExplorerFix(object):

    def __init__(self, app, fix_vary = True, fix_attach = True):
        self.app = app
        self.fix_vary = fix_vary
        self.fix_attach = fix_attach

    def fix_headers(self, environ, headers, status = None):
        if self.fix_vary:
            header = headers.get('content-type', '')
            mimetype, options = parse_options_header(header)
            if mimetype not in ('text/html', 'text/plain', 'text/sgml'):
                headers.pop('vary', None)
        if self.fix_attach and 'content-disposition' in headers:
            pragma = parse_set_header(headers.get('pragma', ''))
            pragma.discard('no-cache')
            header = pragma.to_header()
            if not header:
                headers.pop('pragma', '')
            else:
                headers['Pragma'] = header
            header = headers.get('cache-control', '')
            if header:
                cc = parse_cache_control_header(header, cls=ResponseCacheControl)
                cc.no_cache = None
                cc.no_store = False
                header = cc.to_header()
                if not header:
                    headers.pop('cache-control', '')
                else:
                    headers['Cache-Control'] = header

    def run_fixed(self, environ, start_response):

        def fixing_start_response(status, headers, exc_info = None):
            self.fix_headers(environ, Headers.linked(headers), status)
            return start_response(status, headers, exc_info)

        return self.app(environ, fixing_start_response)

    def __call__(self, environ, start_response):
        ua = UserAgent(environ)
        if ua.browser != 'msie':
            return self.app(environ, start_response)
        return self.run_fixed(environ, start_response)