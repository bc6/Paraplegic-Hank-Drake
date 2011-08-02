import cgi
from Cookie import SimpleCookie, CookieError
from StringIO import StringIO
import urlparse
import urllib
try:
    from UserDict import DictMixin
except ImportError:
    from paste.util.UserDict24 import DictMixin
from paste.util.multidict import MultiDict
__all__ = ['get_cookies',
 'get_cookie_dict',
 'parse_querystring',
 'parse_formvars',
 'construct_url',
 'path_info_split',
 'path_info_pop',
 'resolve_relative_url',
 'EnvironHeaders']

def get_cookies(environ):
    header = environ.get('HTTP_COOKIE', '')
    if environ.has_key('paste.cookies'):
        (cookies, check_header,) = environ['paste.cookies']
        if check_header == header:
            return cookies
    cookies = SimpleCookie()
    try:
        cookies.load(header)
    except CookieError:
        pass
    environ['paste.cookies'] = (cookies, header)
    return cookies



def get_cookie_dict(environ):
    header = environ.get('HTTP_COOKIE')
    if not header:
        return {}
    if environ.has_key('paste.cookies.dict'):
        (cookies, check_header,) = environ['paste.cookies.dict']
        if check_header == header:
            return cookies
    cookies = SimpleCookie()
    try:
        cookies.load(header)
    except CookieError:
        pass
    result = {}
    for name in cookies:
        result[name] = cookies[name].value

    environ['paste.cookies.dict'] = (result, header)
    return result



def parse_querystring(environ):
    source = environ.get('QUERY_STRING', '')
    if not source:
        return []
    if 'paste.parsed_querystring' in environ:
        (parsed, check_source,) = environ['paste.parsed_querystring']
        if check_source == source:
            return parsed
    parsed = cgi.parse_qsl(source, keep_blank_values=True, strict_parsing=False)
    environ['paste.parsed_querystring'] = (parsed, source)
    return parsed



def parse_dict_querystring(environ):
    source = environ.get('QUERY_STRING', '')
    if not source:
        return MultiDict()
    if 'paste.parsed_dict_querystring' in environ:
        (parsed, check_source,) = environ['paste.parsed_dict_querystring']
        if check_source == source:
            return parsed
    parsed = cgi.parse_qsl(source, keep_blank_values=True, strict_parsing=False)
    multi = MultiDict(parsed)
    environ['paste.parsed_dict_querystring'] = (multi, source)
    return multi



def parse_formvars(environ, include_get_vars = True):
    source = environ['wsgi.input']
    if 'paste.parsed_formvars' in environ:
        (parsed, check_source,) = environ['paste.parsed_formvars']
        if check_source == source:
            if include_get_vars:
                parsed.update(parse_querystring(environ))
            return parsed
    type = environ.get('CONTENT_TYPE', '').lower()
    if ';' in type:
        type = type.split(';', 1)[0]
    fake_out_cgi = type not in ('', 'application/x-www-form-urlencoded', 'multipart/form-data')
    if not environ.get('CONTENT_LENGTH'):
        environ['CONTENT_LENGTH'] = '0'
    old_query_string = environ.get('QUERY_STRING', '')
    environ['QUERY_STRING'] = ''
    if fake_out_cgi:
        input = StringIO('')
        old_content_type = environ.get('CONTENT_TYPE')
        old_content_length = environ.get('CONTENT_LENGTH')
        environ['CONTENT_LENGTH'] = '0'
        environ['CONTENT_TYPE'] = ''
    else:
        input = environ['wsgi.input']
    fs = cgi.FieldStorage(fp=input, environ=environ, keep_blank_values=1)
    environ['QUERY_STRING'] = old_query_string
    if fake_out_cgi:
        environ['CONTENT_TYPE'] = old_content_type
        environ['CONTENT_LENGTH'] = old_content_length
    formvars = MultiDict()
    if isinstance(fs.value, list):
        for name in fs.keys():
            values = fs[name]
            if not isinstance(values, list):
                values = [values]
            for value in values:
                if not value.filename:
                    value = value.value
                formvars.add(name, value)


    environ['paste.parsed_formvars'] = (formvars, source)
    if include_get_vars:
        formvars.update(parse_querystring(environ))
    return formvars



def construct_url(environ, with_query_string = True, with_path_info = True, script_name = None, path_info = None, querystring = None):
    url = environ['wsgi.url_scheme'] + '://'
    if environ.get('HTTP_HOST'):
        host = environ['HTTP_HOST']
        port = None
        if ':' in host:
            (host, port,) = host.split(':', 1)
            if environ['wsgi.url_scheme'] == 'https':
                if port == '443':
                    port = None
            elif environ['wsgi.url_scheme'] == 'http':
                if port == '80':
                    port = None
        url += host
        if port:
            url += ':%s' % port
    else:
        url += environ['SERVER_NAME']
        if environ['wsgi.url_scheme'] == 'https':
            if environ['SERVER_PORT'] != '443':
                url += ':' + environ['SERVER_PORT']
        elif environ['SERVER_PORT'] != '80':
            url += ':' + environ['SERVER_PORT']
    if script_name is None:
        url += urllib.quote(environ.get('SCRIPT_NAME', ''))
    else:
        url += urllib.quote(script_name)
    if with_path_info:
        if path_info is None:
            url += urllib.quote(environ.get('PATH_INFO', ''))
        else:
            url += urllib.quote(path_info)
    if with_query_string:
        if querystring is None:
            if environ.get('QUERY_STRING'):
                url += '?' + environ['QUERY_STRING']
        elif querystring:
            url += '?' + querystring
    return url



def resolve_relative_url(url, environ):
    cur_url = construct_url(environ, with_query_string=False)
    return urlparse.urljoin(cur_url, url)



def path_info_split(path_info):
    if not path_info:
        return (None, '')
    else:
        path_info = path_info.lstrip('/')
        if '/' in path_info:
            (first, rest,) = path_info.split('/', 1)
            return (first, '/' + rest)
        return (path_info, '')



def path_info_pop(environ):
    path = environ.get('PATH_INFO', '')
    if not path:
        return None
    else:
        while path.startswith('/'):
            environ['SCRIPT_NAME'] += '/'
            path = path[1:]

        if '/' not in path:
            environ['SCRIPT_NAME'] += path
            environ['PATH_INFO'] = ''
            return path
        (segment, path,) = path.split('/', 1)
        environ['PATH_INFO'] = '/' + path
        environ['SCRIPT_NAME'] += segment
        return segment


_parse_headers_special = {'HTTP_CGI_AUTHORIZATION': 'Authorization',
 'CONTENT_LENGTH': 'Content-Length',
 'CONTENT_TYPE': 'Content-Type'}

def parse_headers(environ):
    for (cgi_var, value,) in environ.iteritems():
        if cgi_var in _parse_headers_special:
            yield (_parse_headers_special[cgi_var], value)
        elif cgi_var.startswith('HTTP_'):
            yield (cgi_var[5:].title().replace('_', '-'), value)




class EnvironHeaders(DictMixin):

    def __init__(self, environ):
        self.environ = environ



    def _trans_name(self, name):
        key = 'HTTP_' + name.replace('-', '_').upper()
        if key == 'HTTP_CONTENT_LENGTH':
            key = 'CONTENT_LENGTH'
        elif key == 'HTTP_CONTENT_TYPE':
            key = 'CONTENT_TYPE'
        return key



    def _trans_key(self, key):
        if key == 'CONTENT_TYPE':
            return 'Content-Type'
        else:
            if key == 'CONTENT_LENGTH':
                return 'Content-Length'
            if key.startswith('HTTP_'):
                return key[5:].replace('_', '-').title()
            return None



    def __getitem__(self, item):
        return self.environ[self._trans_name(item)]



    def __setitem__(self, item, value):
        self.environ[self._trans_name(item)] = value



    def __delitem__(self, item):
        del self.environ[self._trans_name(item)]



    def __iter__(self):
        for key in self.environ:
            name = self._trans_key(key)
            if name is not None:
                yield name




    def keys(self):
        return list(iter(self))



    def __contains__(self, item):
        return self._trans_name(item) in self.environ




def _cgi_FieldStorage__repr__patch(self):
    if self.file:
        return 'FieldStorage(%r, %r)' % (self.name, self.filename)
    return 'FieldStorage(%r, %r, %r)' % (self.name, self.filename, self.value)


cgi.FieldStorage.__repr__ = _cgi_FieldStorage__repr__patch
if __name__ == '__main__':
    import doctest
    doctest.testmod()

