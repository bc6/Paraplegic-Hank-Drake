#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\lib\encoding.py
import struct
import time
import cherrypy
from cherrypy._cpcompat import basestring, BytesIO, ntob, set, unicodestr
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
        for k, v in kwargs.items():
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
                if isinstance(chunk, unicodestr):
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
                    if isinstance(chunk, unicodestr):
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
        else:
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
                            cherrypy.log('Attempting encoding %s (qvalue >0)' % element, 'TOOLS.ENCODE')
                        if encoder(encoding):
                            return encoding

            if '*' not in charsets:
                iso = 'iso-8859-1'
                if iso not in charsets:
                    if self.debug:
                        cherrypy.log('Attempting ISO-8859-1 encoding', 'TOOLS.ENCODE')
                    if encoder(iso):
                        return iso
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
        elif hasattr(self.body, 'read'):
            self.body = file_generator(self.body)
        elif self.body is None:
            self.body = []
        ct = response.headers.elements('Content-Type')
        if self.debug:
            cherrypy.log('Content-Type: %r' % [ str(h) for h in ct ], 'TOOLS.ENCODE')
        if ct:
            ct = ct[0]
            if self.text_only:
                if ct.value.lower().startswith('text/'):
                    if self.debug:
                        cherrypy.log('Content-Type %s starts with "text/"' % ct, 'TOOLS.ENCODE')
                    do_find = True
                else:
                    if self.debug:
                        cherrypy.log('Not finding because Content-Type %s does not start with "text/"' % ct, 'TOOLS.ENCODE')
                    do_find = False
            else:
                if self.debug:
                    cherrypy.log('Finding because not text_only', 'TOOLS.ENCODE')
                do_find = True
            if do_find:
                ct.params['charset'] = self.find_acceptable_charset()
                if self.add_charset:
                    if self.debug:
                        cherrypy.log('Setting Content-Type %s' % ct, 'TOOLS.ENCODE')
                    response.headers['Content-Type'] = str(ct)
        return self.body


def compress(body, compress_level):
    import zlib
    yield ntob('\x1f\x8b')
    yield ntob('\x08')
    yield ntob('\x00')
    yield struct.pack('<L', int(time.time()) & int('FFFFFFFF', 16))
    yield ntob('\x02')
    yield ntob('\xff')
    crc = zlib.crc32(ntob(''))
    size = 0
    zobj = zlib.compressobj(compress_level, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0)
    for line in body:
        size += len(line)
        crc = zlib.crc32(line, crc)
        yield zobj.compress(line)

    yield zobj.flush()
    yield struct.pack('<L', crc & int('FFFFFFFF', 16))
    yield struct.pack('<L', size & int('FFFFFFFF', 16))


def decompress(body):
    import gzip
    zbuf = BytesIO()
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
                cherrypy.log('Non-zero identity qvalue: %s' % coding, context='TOOLS.GZIP')
            return
        if coding.value in ('gzip', 'x-gzip'):
            if coding.qvalue == 0:
                if debug:
                    cherrypy.log('Zero gzip qvalue: %s' % coding, context='TOOLS.GZIP')
                return
            if ct not in mime_types:
                found = False
                if '/' in ct:
                    ct_media_type, ct_sub_type = ct.split('/')
                    for mime_type in mime_types:
                        if '/' in mime_type:
                            media_type, sub_type = mime_type.split('/')
                            if ct_media_type == media_type:
                                if sub_type == '*':
                                    found = True
                                    break
                                elif '+' in sub_type and '+' in ct_sub_type:
                                    ct_left, ct_right = ct_sub_type.split('+')
                                    left, right = sub_type.split('+')
                                    if left == '*' and ct_right == right:
                                        found = True
                                        break

                if not found:
                    if debug:
                        cherrypy.log('Content-Type %s not in mime_types %r' % (ct, mime_types), context='TOOLS.GZIP')
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