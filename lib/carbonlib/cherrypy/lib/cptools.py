import logging
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5
import re
try:
    set
except NameError:
    from sets import Set as set
import cherrypy
from cherrypy.lib import httputil as _httputil

def validate_etags(autotags = False, debug = False):
    response = cherrypy.serving.response
    if hasattr(response, 'ETag'):
        return 
    (status, reason, msg,) = _httputil.valid_status(response.status)
    etag = response.headers.get('ETag')
    if etag:
        if debug:
            cherrypy.log('ETag already set: %s' % etag, 'TOOLS.ETAGS')
    elif not autotags:
        if debug:
            cherrypy.log('Autotags off', 'TOOLS.ETAGS')
    elif status != 200:
        if debug:
            cherrypy.log('Status not 200', 'TOOLS.ETAGS')
    else:
        etag = response.collapse_body()
        etag = '"%s"' % md5(etag).hexdigest()
        if debug:
            cherrypy.log('Setting ETag: %s' % etag, 'TOOLS.ETAGS')
        response.headers['ETag'] = etag
    response.ETag = etag
    if debug:
        cherrypy.log('Status: %s' % status, 'TOOLS.ETAGS')
    if status >= 200 and status <= 299:
        request = cherrypy.serving.request
        conditions = request.headers.elements('If-Match') or []
        conditions = [ str(x) for x in conditions ]
        if debug:
            cherrypy.log('If-Match conditions: %s' % repr(conditions), 'TOOLS.ETAGS')
        if conditions and not (conditions == ['*'] or etag in conditions):
            raise cherrypy.HTTPError(412, 'If-Match failed: ETag %r did not match %r' % (etag, conditions))
        conditions = request.headers.elements('If-None-Match') or []
        conditions = [ str(x) for x in conditions ]
        if debug:
            cherrypy.log('If-None-Match conditions: %s' % repr(conditions), 'TOOLS.ETAGS')
        if conditions == ['*'] or etag in conditions:
            if debug:
                cherrypy.log('request.method: %s' % request.method, 'TOOLS.ETAGS')
            if request.method in ('GET', 'HEAD'):
                raise cherrypy.HTTPRedirect([], 304)
            else:
                raise cherrypy.HTTPError(412, 'If-None-Match failed: ETag %r matched %r' % (etag, conditions))



def validate_since():
    response = cherrypy.serving.response
    lastmod = response.headers.get('Last-Modified')
    if lastmod:
        (status, reason, msg,) = _httputil.valid_status(response.status)
        request = cherrypy.serving.request
        since = request.headers.get('If-Unmodified-Since')
        if since and since != lastmod:
            if status >= 200 and status <= 299 or status == 412:
                raise cherrypy.HTTPError(412)
        since = request.headers.get('If-Modified-Since')
        if since and since == lastmod:
            if status >= 200 and status <= 299 or status == 304:
                if request.method in ('GET', 'HEAD'):
                    raise cherrypy.HTTPRedirect([], 304)
                else:
                    raise cherrypy.HTTPError(412)



def proxy(base = None, local = 'X-Forwarded-Host', remote = 'X-Forwarded-For', scheme = 'X-Forwarded-Proto', debug = False):
    request = cherrypy.serving.request
    if scheme:
        s = request.headers.get(scheme, None)
        if debug:
            cherrypy.log('Testing scheme %r:%r' % (scheme, s), 'TOOLS.PROXY')
        if s == 'on' and 'ssl' in scheme.lower():
            scheme = 'https'
        else:
            scheme = s
    if not scheme:
        scheme = request.base[:request.base.find('://')]
    if local:
        lbase = request.headers.get(local, None)
        if debug:
            cherrypy.log('Testing local %r:%r' % (local, lbase), 'TOOLS.PROXY')
        if lbase is not None:
            base = lbase.split(',')[0]
    if not base:
        port = request.local.port
        if port == 80:
            base = '127.0.0.1'
        else:
            base = '127.0.0.1:%s' % port
    if base.find('://') == -1:
        base = scheme + '://' + base
    request.base = base
    if remote:
        xff = request.headers.get(remote)
        if debug:
            cherrypy.log('Testing remote %r:%r' % (remote, xff), 'TOOLS.PROXY')
        if xff:
            if remote == 'X-Forwarded-For':
                xff = xff.split(',')[-1].strip()
            request.remote.ip = xff



def ignore_headers(headers = ('Range',), debug = False):
    request = cherrypy.serving.request
    for name in headers:
        if name in request.headers:
            if debug:
                cherrypy.log('Ignoring request header %r' % name, 'TOOLS.IGNORE_HEADERS')
            del request.headers[name]




def response_headers(headers = None, debug = False):
    if debug:
        cherrypy.log('Setting response headers: %s' % repr(headers), 'TOOLS.RESPONSE_HEADERS')
    for (name, value,) in headers or []:
        cherrypy.serving.response.headers[name] = value



response_headers.failsafe = True

def referer(pattern, accept = True, accept_missing = False, error = 403, message = 'Forbidden Referer header.', debug = False):
    try:
        ref = cherrypy.serving.request.headers['Referer']
        match = bool(re.match(pattern, ref))
        if debug:
            cherrypy.log('Referer %r matches %r' % (ref, pattern), 'TOOLS.REFERER')
        if accept == match:
            return 
    except KeyError:
        if debug:
            cherrypy.log('No Referer header', 'TOOLS.REFERER')
        if accept_missing:
            return 
    raise cherrypy.HTTPError(error, message)



class SessionAuth(object):
    session_key = 'username'
    debug = False

    def check_username_and_password(self, username, password):
        pass



    def anonymous(self):
        pass



    def on_login(self, username):
        pass



    def on_logout(self, username):
        pass



    def on_check(self, username):
        pass



    def login_screen(self, from_page = '..', username = '', error_msg = '', **kwargs):
        return '<html><body>\nMessage: %(error_msg)s\n<form method="post" action="do_login">\n    Login: <input type="text" name="username" value="%(username)s" size="10" /><br />\n    Password: <input type="password" name="password" size="10" /><br />\n    <input type="hidden" name="from_page" value="%(from_page)s" /><br />\n    <input type="submit" />\n</form>\n</body></html>' % {'from_page': from_page,
         'username': username,
         'error_msg': error_msg}



    def do_login(self, username, password, from_page = '..', **kwargs):
        response = cherrypy.serving.response
        error_msg = self.check_username_and_password(username, password)
        if error_msg:
            body = self.login_screen(from_page, username, error_msg)
            response.body = body
            if 'Content-Length' in response.headers:
                del response.headers['Content-Length']
            return True
        cherrypy.serving.request.login = username
        cherrypy.session[self.session_key] = username
        self.on_login(username)
        raise cherrypy.HTTPRedirect(from_page or '/')



    def do_logout(self, from_page = '..', **kwargs):
        sess = cherrypy.session
        username = sess.get(self.session_key)
        sess[self.session_key] = None
        if username:
            cherrypy.serving.request.login = None
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(from_page)



    def do_check(self):
        sess = cherrypy.session
        request = cherrypy.serving.request
        response = cherrypy.serving.response
        username = sess.get(self.session_key)
        if not username:
            sess[self.session_key] = username = self.anonymous()
            if self.debug:
                cherrypy.log('No session[username], trying anonymous', 'TOOLS.SESSAUTH')
        if not username:
            url = cherrypy.url(qs=request.query_string)
            if self.debug:
                cherrypy.log('No username, routing to login_screen with from_page %r' % url, 'TOOLS.SESSAUTH')
            response.body = self.login_screen(url)
            if 'Content-Length' in response.headers:
                del response.headers['Content-Length']
            return True
        if self.debug:
            cherrypy.log('Setting request.login to %r' % username, 'TOOLS.SESSAUTH')
        request.login = username
        self.on_check(username)



    def run(self):
        request = cherrypy.serving.request
        response = cherrypy.serving.response
        path = request.path_info
        if path.endswith('login_screen'):
            if self.debug:
                cherrypy.log('routing %r to login_screen' % path, 'TOOLS.SESSAUTH')
            return self.login_screen(**request.params)
        else:
            if path.endswith('do_login'):
                if request.method != 'POST':
                    response.headers['Allow'] = 'POST'
                    if self.debug:
                        cherrypy.log('do_login requires POST', 'TOOLS.SESSAUTH')
                    raise cherrypy.HTTPError(405)
                if self.debug:
                    cherrypy.log('routing %r to do_login' % path, 'TOOLS.SESSAUTH')
                return self.do_login(**request.params)
            if path.endswith('do_logout'):
                if request.method != 'POST':
                    response.headers['Allow'] = 'POST'
                    raise cherrypy.HTTPError(405)
                if self.debug:
                    cherrypy.log('routing %r to do_logout' % path, 'TOOLS.SESSAUTH')
                return self.do_logout(**request.params)
            if self.debug:
                cherrypy.log('No special path, running do_check', 'TOOLS.SESSAUTH')
            return self.do_check()




def session_auth(**kwargs):
    sa = SessionAuth()
    for (k, v,) in kwargs.items():
        setattr(sa, k, v)

    return sa.run()


session_auth.__doc__ = 'Session authentication hook.\n\nAny attribute of the SessionAuth class may be overridden via a keyword arg\nto this function:\n\n' + '\n'.join([ '%s: %s' % (k, type(getattr(SessionAuth, k)).__name__) for k in dir(SessionAuth) if not k.startswith('__') ])

def log_traceback(severity = logging.ERROR, debug = False):
    cherrypy.log('', 'HTTP', severity=severity, traceback=True)



def log_request_headers(debug = False):
    h = [ '  %s: %s' % (k, v) for (k, v,) in cherrypy.serving.request.header_list ]
    cherrypy.log('\nRequest Headers:\n' + '\n'.join(h), 'HTTP')



def log_hooks(debug = False):
    request = cherrypy.serving.request
    msg = []
    from cherrypy import _cprequest
    points = _cprequest.hookpoints
    for k in request.hooks.keys():
        if k not in points:
            points.append(k)

    for k in points:
        msg.append('    %s:' % k)
        v = request.hooks.get(k, [])
        v.sort()
        for h in v:
            msg.append('        %r' % h)


    cherrypy.log('\nRequest Hooks for ' + cherrypy.url() + ':\n' + '\n'.join(msg), 'HTTP')



def redirect(url = '', internal = True, debug = False):
    if debug:
        cherrypy.log('Redirecting %sto: %s' % ({True: 'internal ',
          False: ''}[internal], url), 'TOOLS.REDIRECT')
    if internal:
        raise cherrypy.InternalRedirect(url)
    else:
        raise cherrypy.HTTPRedirect(url)



def trailing_slash(missing = True, extra = False, status = None, debug = False):
    request = cherrypy.serving.request
    pi = request.path_info
    if debug:
        cherrypy.log('is_index: %r, missing: %r, extra: %r, path_info: %r' % (request.is_index,
         missing,
         extra,
         pi), 'TOOLS.TRAILING_SLASH')
    if request.is_index is True:
        if missing:
            if not pi.endswith('/'):
                new_url = cherrypy.url(pi + '/', request.query_string)
                raise cherrypy.HTTPRedirect(new_url, status=status or 301)
    elif request.is_index is False:
        if extra:
            if pi.endswith('/') and pi != '/':
                new_url = cherrypy.url(pi[:-1], request.query_string)
                raise cherrypy.HTTPRedirect(new_url, status=status or 301)



def flatten(debug = False):
    import types

    def flattener(input):
        numchunks = 0
        for x in input:
            if not isinstance(x, types.GeneratorType):
                numchunks += 1
                yield x
            else:
                for y in flattener(x):
                    numchunks += 1
                    yield y


        if debug:
            cherrypy.log('Flattened %d chunks' % numchunks, 'TOOLS.FLATTEN')


    response = cherrypy.serving.response
    response.body = flattener(response.body)



def accept(media = None, debug = False):
    if not media:
        return 
    if isinstance(media, basestring):
        media = [media]
    request = cherrypy.serving.request
    ranges = request.headers.elements('Accept')
    if not ranges:
        if debug:
            cherrypy.log('No Accept header elements', 'TOOLS.ACCEPT')
        return media[0]
    for element in ranges:
        if element.qvalue > 0:
            if element.value == '*/*':
                if debug:
                    cherrypy.log('Match due to */*', 'TOOLS.ACCEPT')
                return media[0]
            if element.value.endswith('/*'):
                mtype = element.value[:-1]
                for m in media:
                    if m.startswith(mtype):
                        if debug:
                            cherrypy.log('Match due to %s' % element.value, 'TOOLS.ACCEPT')
                        return m

            elif element.value in media:
                if debug:
                    cherrypy.log('Match due to %s' % element.value, 'TOOLS.ACCEPT')
                return element.value

    ah = request.headers.get('Accept')
    if ah is None:
        msg = 'Your client did not send an Accept header.'
    else:
        msg = 'Your client sent this Accept header: %s.' % ah
    msg += ' But this resource only emits these media types: %s.' % ', '.join(media)
    raise cherrypy.HTTPError(406, msg)



class MonitoredHeaderMap(_httputil.HeaderMap):

    def __init__(self):
        self.accessed_headers = set()



    def __getitem__(self, key):
        self.accessed_headers.add(key)
        return _httputil.HeaderMap.__getitem__(self, key)



    def __contains__(self, key):
        self.accessed_headers.add(key)
        return _httputil.HeaderMap.__contains__(self, key)



    def get(self, key, default = None):
        self.accessed_headers.add(key)
        return _httputil.HeaderMap.get(self, key, default=default)



    def has_key(self, key):
        self.accessed_headers.add(key)
        return _httputil.HeaderMap.has_key(self, key)




def autovary(ignore = None, debug = False):
    request = cherrypy.serving.request
    req_h = request.headers
    request.headers = MonitoredHeaderMap()
    request.headers.update(req_h)
    if ignore is None:
        ignore = set(['Content-Disposition', 'Content-Length', 'Content-Type'])

    def set_response_header():
        resp_h = cherrypy.serving.response.headers
        v = set([ e.value for e in resp_h.elements('Vary') ])
        if debug:
            cherrypy.log('Accessed headers: %s' % request.headers.accessed_headers, 'TOOLS.AUTOVARY')
        v = v.union(request.headers.accessed_headers)
        v = v.difference(ignore)
        v = list(v)
        v.sort()
        resp_h['Vary'] = ', '.join(v)


    request.hooks.attach('before_finalize', set_response_header, 95)



