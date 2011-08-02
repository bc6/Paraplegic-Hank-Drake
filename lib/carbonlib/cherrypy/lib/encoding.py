try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
try:
    set
except NameError:
    from sets import Set as set
import struct
import time
import types
import cherrypy
from cherrypy.lib import file_generator
from cherrypy.lib import set_vary_header

def decode(encoding = None, default_encoding = 'utf-8'):
    body = cherrypy.request.body
    if encoding is not None:
        if not isinstance(encoding, list):
            encoding = [encoding]
        body.attempt_charsets = encoding
    elif default_encoding:
        if not isinstance(default_encoding, list):
            default_encoding = [default_encoding]
        body.attempt_charsets = body.attempt_charsets + default_encoding



class ResponseEncoder:
    default_encoding = 'utf-8'
    failmsg = 'Response body could not be encoded with %r.'
    encoding = None
    errors = 'strict'
    text_only = True
    add_charset = True
    debug = False

    def __init__(self, **kwargs):
        for (k, v,) in kwargs.items():
            setattr(self, k, v)

        self.attempted_charsets = set()
        request = cherrypy.serving.request
        if request.handler is not None:
            if self.debug:
                cherrypy.log('Replacing request.handler', 'TOOLS.ENCODE')
            self.oldhandler = request.handler
            request.handler = self



    def encode_stream(self, encoding):
        if encoding in self.attempted_charsets:
            return False
        self.attempted_charsets.add(encoding)

        def encoder(body):
            for chunk in body:
                if isinstance(chunk, unicode):
                    chunk = chunk.encode(encoding, self.errors)
                yield chunk



        self.body = encoder(self.body)
        return True



    def encode_string(self, encoding):
        if encoding in self.attempted_charsets:
            return False
        else:
            self.attempted_charsets.add(encoding)
            try:
                body = []
                for chunk in self.body:
                    if isinstance(chunk, unicode):
                        chunk = chunk.encode(encoding, self.errors)
                    body.append(chunk)

                self.body = body
            except (LookupError, UnicodeError):
                return False
            return True



    def find_acceptable_charset(self):
        request = cherrypy.serving.request
        response = cherrypy.serving.response
        if self.debug:
            cherrypy.log('response.stream %r' % response.stream, 'TOOLS.ENCODE')
        if response.stream:
            encoder = self.encode_stream
        else:
            encoder = self.encode_string
            if 'Content-Length' in response.headers:
                del response.headers['Content-Length']
        encs = request.headers.elements('Accept-Charset')
        charsets = [ enc.value.lower() for enc in encs ]
        if self.debug:
            cherrypy.log('charsets %s' % repr(charsets), 'TOOLS.ENCODE')
        if self.encoding is not None:
            encoding = self.encoding.lower()
            if self.debug:
                cherrypy.log('Specified encoding %r' % encoding, 'TOOLS.ENCODE')
            if not charsets or '*' in charsets or encoding in charsets:
                if self.debug:
                    cherrypy.log('Attempting encoding %r' % encoding, 'TOOLS.ENCODE')
                if encoder(encoding):
                    return encoding
        elif not encs:
            if self.debug:
                cherrypy.log('Attempting default encoding %r' % self.default_encoding, 'TOOLS.ENCODE')
            if encoder(self.default_encoding):
                return self.default_encoding
            raise cherrypy.HTTPError(500, self.failmsg % self.default_encoding)
        elif '*' not in charsets:
            iso = 'iso-8859-1'
            if iso not in charsets:
                if self.debug:
                    cherrypy.log('Attempting ISO-8859-1 encoding', 'TOOLS.ENCODE')
                if encoder(iso):
                    return iso
        for element in encs:
            if element.qvalue > 0:
                if element.value == '*':
                    if self.debug:
                        cherrypy.log('Attempting default encoding due to %r' % element, 'TOOLS.ENCODE')
                    if encoder(self.default_encoding):
                        return self.default_encoding
                else:
                    encoding = element.value
                    if self.debug:
                        cherrypy.log('Attempting encoding %r (qvalue >0)' % element, 'TOOLS.ENCODE')
                    if encoder(encoding):
                        return encoding

        ac = request.headers.get('Accept-Charset')
        if ac is None:
            msg = 'Your client did not send an Accept-Charset header.'
        else:
            msg = 'Your client sent this Accept-Charset header: %s.' % ac
        msg += ' We tried these charsets: %s.' % ', '.join(self.attempted_charsets)
        raise cherrypy.HTTPError(406, msg)



    def __call__(self, *args, **kwargs):
        response = cherrypy.serving.response
        self.body = self.oldhandler(*args, **kwargs)
        if isinstance(self.body, basestring):
            if self.body:
                self.body = [self.body]
            else:
                self.body = []
        elif isinstance(self.body, types.FileType):
            self.body = file_generator(self.body)
        elif self.body is None:
            self.body = []
        ct = response.headers.elements('Content-Type')
        if self.debug:
            cherrypy.log('Content-Type: %r' % ct, 'TOOLS.ENCODE')
        if ct:
            if self.text_only:
                ct = ct[0]
                if ct.value.lower().startswith('text/'):
                    if self.debug:
                        cherrypy.log('Content-Type %r starts with "text/"' % ct, 'TOOLS.ENCODE')
                    do_find = True
                elif self.debug:
                    cherrypy.log('Not finding because Content-Type %r does not start with "text/"' % ct, 'TOOLS.ENCODE')
                do_find = False
            elif self.debug:
                cherrypy.log('Finding because not text_only', 'TOOLS.ENCODE')
            do_find = True
            if do_find:
                ct.params['charset'] = self.find_acceptable_charset()
                if self.add_charset:
                    if self.debug:
                        cherrypy.log('Setting Content-Type %r' % ct, 'TOOLS.ENCODE')
                    response.headers['Content-Type'] = str(ct)
        return self.body




def compress(body, compress_level):
    import zlib
    yield '\x1f\x8b'
    yield '\x08'
    yield '\x00'
    yield struct.pack('<L', int(time.time()) & 4294967295L)
    yield '\x02'
    yield '\xff'
    crc = zlib.crc32('')
    size = 0
    zobj = zlib.compressobj(compress_level, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0)
    for line in body:
        size += len(line)
        crc = zlib.crc32(line, crc)
        yield zobj.compress(line)

    yield zobj.flush()
    yield struct.pack('<L', crc & 4294967295L)
    yield struct.pack('<L', size & 4294967295L)



def decompress(body):
    import gzip
    zbuf = StringIO()
    zbuf.write(body)
    zbuf.seek(0)
    zfile = gzip.GzipFile(mode='rb', fileobj=zbuf)
    data = zfile.read()
    zfile.close()
    return data



def gzip(compress_level = 5, mime_types = ['text/html', 'text/plain'], debug = False):
    request = cherrypy.serving.request
    response = cherrypy.serving.response
    set_vary_header(response, 'Accept-Encoding')
    if not response.body:
        if debug:
            cherrypy.log('No response body', context='TOOLS.GZIP')
        return 
    if getattr(request, 'cached', False):
        if debug:
            cherrypy.log('Not gzipping cached response', context='TOOLS.GZIP')
        return 
    acceptable = request.headers.elements('Accept-Encoding')
    if not acceptable:
        if debug:
            cherrypy.log('No Accept-Encoding', context='TOOLS.GZIP')
        return 
    ct = response.headers.get('Content-Type', '').split(';')[0]
    for coding in acceptable:
        if coding.value == 'identity' and coding.qvalue != 0:
            if debug:
                cherrypy.log('Non-zero identity qvalue: %r' % coding, context='TOOLS.GZIP')
            return 
        if coding.value in ('gzip', 'x-gzip'):
            if coding.qvalue == 0:
                if debug:
                    cherrypy.log('Zero gzip qvalue: %r' % coding, context='TOOLS.GZIP')
                return 
            if ct not in mime_types:
                if debug:
                    cherrypy.log('Content-Type %r not in mime_types %r' % (ct, mime_types), context='TOOLS.GZIP')
                return 
            if debug:
                cherrypy.log('Gzipping', context='TOOLS.GZIP')
            response.headers['Content-Encoding'] = 'gzip'
            response.body = compress(response.body, compress_level)
            if 'Content-Length' in response.headers:
                del response.headers['Content-Length']
            return 

    if debug:
        cherrypy.log('No acceptable encoding found.', context='GZIP')
    cherrypy.HTTPError(406, 'identity, gzip').set_response()



