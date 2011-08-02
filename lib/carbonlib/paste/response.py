import warnings

class HeaderDict(dict):

    def __getitem__(self, key):
        return dict.__getitem__(self, self.normalize(key))



    def __setitem__(self, key, value):
        dict.__setitem__(self, self.normalize(key), value)



    def __delitem__(self, key):
        dict.__delitem__(self, self.normalize(key))



    def __contains__(self, key):
        return dict.__contains__(self, self.normalize(key))


    has_key = __contains__

    def get(self, key, failobj = None):
        return dict.get(self, self.normalize(key), failobj)



    def setdefault(self, key, failobj = None):
        return dict.setdefault(self, self.normalize(key), failobj)



    def pop(self, key, *args):
        return dict.pop(self, self.normalize(key), *args)



    def update(self, other):
        for key in other:
            self[self.normalize(key)] = other[key]




    def normalize(self, key):
        return str(key).lower().strip()



    def add(self, key, value):
        key = self.normalize(key)
        if key in self:
            if isinstance(self[key], list):
                self[key].append(value)
            else:
                self[key] = [self[key], value]
        else:
            self[key] = value



    def headeritems(self):
        result = []
        for (key, value,) in self.items():
            if isinstance(value, list):
                for v in value:
                    result.append((key, str(v)))

            else:
                result.append((key, str(value)))

        return result



    def fromlist(cls, seq):
        self = cls()
        for (name, value,) in seq:
            self.add(name, value)

        return self


    fromlist = classmethod(fromlist)


def has_header(headers, name):
    name = name.lower()
    for (header, value,) in headers:
        if header.lower() == name:
            return True

    return False



def header_value(headers, name):
    name = name.lower()
    result = [ value for (header, value,) in headers if header.lower() == name ]
    if result:
        return ','.join(result)
    else:
        return None



def remove_header(headers, name):
    name = name.lower()
    i = 0
    result = None
    while i < len(headers):
        if headers[i][0].lower() == name:
            result = headers[i][1]
            del headers[i]
            continue
        i += 1

    return result



def replace_header(headers, name, value):
    name = name.lower()
    i = 0
    result = None
    while i < len(headers):
        if headers[i][0].lower() == name:
            result = headers[i][1]
            headers[i] = (name, value)
        i += 1

    if not result:
        headers.append((name, value))
    return result



def error_body_response(error_code, message, __warn = True):
    if __warn:
        warnings.warn('wsgilib.error_body_response is deprecated; use the wsgi_application method on an HTTPException object instead', DeprecationWarning, 2)
    return '<html>\n  <head>\n    <title>%(error_code)s</title>\n  </head>\n  <body>\n  <h1>%(error_code)s</h1>\n  %(message)s\n  </body>\n</html>' % {'error_code': error_code,
     'message': message}



def error_response(environ, error_code, message, debug_message = None, __warn = True):
    if __warn:
        warnings.warn('wsgilib.error_response is deprecated; use the wsgi_application method on an HTTPException object instead', DeprecationWarning, 2)
    if debug_message and environ.get('paste.config', {}).get('debug'):
        message += '\n\n<!-- %s -->' % debug_message
    body = error_body_response(error_code, message, __warn=False)
    headers = [('content-type', 'text/html'), ('content-length', str(len(body)))]
    return (error_code, headers, body)



def error_response_app(error_code, message, debug_message = None, __warn = True):
    if __warn:
        warnings.warn('wsgilib.error_response_app is deprecated; use the wsgi_application method on an HTTPException object instead', DeprecationWarning, 2)

    def application(environ, start_response):
        (status, headers, body,) = error_response(environ, error_code, message, debug_message=debug_message, __warn=False)
        start_response(status, headers)
        return [body]


    return application



