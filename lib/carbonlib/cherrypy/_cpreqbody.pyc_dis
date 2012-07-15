#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\_cpreqbody.py
import re
import sys
import tempfile
from urllib import unquote_plus
import cherrypy
from cherrypy._cpcompat import basestring, ntob, ntou
from cherrypy.lib import httputil

def process_urlencoded(entity):
    qs = entity.fp.read()
    for charset in entity.attempt_charsets:
        try:
            params = {}
            for aparam in qs.split(ntob('&')):
                for pair in aparam.split(ntob(';')):
                    if not pair:
                        continue
                    atoms = pair.split(ntob('='), 1)
                    if len(atoms) == 1:
                        atoms.append(ntob(''))
                    key = unquote_plus(atoms[0]).decode(charset)
                    try:
                        value = unquote_plus(atoms[1]).decode(charset)
                    except Exception:
                        value = unquote_plus(atoms[1])

                    if key in params:
                        if not isinstance(params[key], list):
                            params[key] = [params[key]]
                        params[key].append(value)
                    else:
                        params[key] = value

        except UnicodeDecodeError:
            pass
        else:
            entity.charset = charset
            break

    else:
        raise cherrypy.HTTPError(400, 'The request entity could not be decoded. The following charsets were attempted: %s' % repr(entity.attempt_charsets))

    for key, value in params.items():
        if key in entity.params:
            if not isinstance(entity.params[key], list):
                entity.params[key] = [entity.params[key]]
            entity.params[key].append(value)
        else:
            entity.params[key] = value


def process_multipart(entity):
    ib = ''
    if 'boundary' in entity.content_type.params:
        ib = entity.content_type.params['boundary'].strip('"')
    if not re.match('^[ -~]{0,200}[!-~]$', ib):
        raise ValueError('Invalid boundary in multipart form: %r' % (ib,))
    ib = ('--' + ib).encode('ascii')
    while True:
        b = entity.readline()
        if not b:
            return
        b = b.strip()
        if b == ib:
            break

    while True:
        part = entity.part_class.from_fp(entity.fp, ib)
        entity.parts.append(part)
        part.process()
        if part.fp.done:
            break


def process_multipart_form_data(entity):
    process_multipart(entity)
    kept_parts = []
    for part in entity.parts:
        if part.name is None:
            kept_parts.append(part)
        else:
            if part.filename is None:
                value = part.fullvalue()
            else:
                value = part
            if part.name in entity.params:
                if not isinstance(entity.params[part.name], list):
                    entity.params[part.name] = [entity.params[part.name]]
                entity.params[part.name].append(value)
            else:
                entity.params[part.name] = value

    entity.parts = kept_parts


def _old_process_multipart(entity):
    process_multipart(entity)
    params = entity.params
    for part in entity.parts:
        if part.name is None:
            key = ntou('parts')
        else:
            key = part.name
        if part.filename is None:
            value = part.fullvalue()
        else:
            value = part
        if key in params:
            if not isinstance(params[key], list):
                params[key] = [params[key]]
            params[key].append(value)
        else:
            params[key] = value


class Entity(object):
    attempt_charsets = ['utf-8']
    charset = None
    content_type = None
    default_content_type = 'application/x-www-form-urlencoded'
    filename = None
    fp = None
    headers = None
    length = None
    name = None
    params = None
    processors = {'application/x-www-form-urlencoded': process_urlencoded,
     'multipart/form-data': process_multipart_form_data,
     'multipart': process_multipart}
    parts = None
    part_class = None

    def __init__(self, fp, headers, params = None, parts = None):
        self.processors = self.processors.copy()
        self.fp = fp
        self.headers = headers
        if params is None:
            params = {}
        self.params = params
        if parts is None:
            parts = []
        self.parts = parts
        self.content_type = headers.elements('Content-Type')
        if self.content_type:
            self.content_type = self.content_type[0]
        else:
            self.content_type = httputil.HeaderElement.from_str(self.default_content_type)
        dec = self.content_type.params.get('charset', None)
        if dec:
            self.attempt_charsets = [dec] + [ c for c in self.attempt_charsets if c != dec ]
        else:
            self.attempt_charsets = self.attempt_charsets[:]
        self.length = None
        clen = headers.get('Content-Length', None)
        if clen is not None and 'chunked' not in headers.get('Transfer-Encoding', ''):
            try:
                self.length = int(clen)
            except ValueError:
                pass

        self.name = None
        self.filename = None
        disp = headers.elements('Content-Disposition')
        if disp:
            disp = disp[0]
            if 'name' in disp.params:
                self.name = disp.params['name']
                if self.name.startswith('"') and self.name.endswith('"'):
                    self.name = self.name[1:-1]
            if 'filename' in disp.params:
                self.filename = disp.params['filename']
                if self.filename.startswith('"') and self.filename.endswith('"'):
                    self.filename = self.filename[1:-1]

    type = property(lambda self: self.content_type, doc='A deprecated alias for :attr:`content_type<cherrypy._cpreqbody.Entity.content_type>`.')

    def read(self, size = None, fp_out = None):
        return self.fp.read(size, fp_out)

    def readline(self, size = None):
        return self.fp.readline(size)

    def readlines(self, sizehint = None):
        return self.fp.readlines(sizehint)

    def __iter__(self):
        return self

    def next(self):
        line = self.readline()
        if not line:
            raise StopIteration
        return line

    def read_into_file(self, fp_out = None):
        if fp_out is None:
            fp_out = self.make_file()
        self.read(fp_out=fp_out)
        return fp_out

    def make_file(self):
        return tempfile.TemporaryFile()

    def fullvalue(self):
        if self.file:
            self.file.seek(0)
            value = self.file.read()
            self.file.seek(0)
        else:
            value = self.value
        return value

    def process(self):
        proc = None
        ct = self.content_type.value
        try:
            proc = self.processors[ct]
        except KeyError:
            toptype = ct.split('/', 1)[0]
            try:
                proc = self.processors[toptype]
            except KeyError:
                pass

        if proc is None:
            self.default_proc()
        else:
            proc(self)

    def default_proc(self):
        pass


class Part(Entity):
    attempt_charsets = ['us-ascii', 'utf-8']
    boundary = None
    default_content_type = 'text/plain'
    maxrambytes = 1000

    def __init__(self, fp, headers, boundary):
        Entity.__init__(self, fp, headers)
        self.boundary = boundary
        self.file = None
        self.value = None

    def from_fp(cls, fp, boundary):
        headers = cls.read_headers(fp)
        return cls(fp, headers, boundary)

    from_fp = classmethod(from_fp)

    def read_headers(cls, fp):
        headers = httputil.HeaderMap()
        while True:
            line = fp.readline()
            if not line:
                raise EOFError('Illegal end of headers.')
            if line == ntob('\r\n'):
                break
            if not line.endswith(ntob('\r\n')):
                raise ValueError('MIME requires CRLF terminators: %r' % line)
            if line[0] in ntob(' \t'):
                v = line.strip().decode('ISO-8859-1')
            else:
                k, v = line.split(ntob(':'), 1)
                k = k.strip().decode('ISO-8859-1')
                v = v.strip().decode('ISO-8859-1')
            existing = headers.get(k)
            if existing:
                v = ', '.join((existing, v))
            headers[k] = v

        return headers

    read_headers = classmethod(read_headers)

    def read_lines_to_boundary(self, fp_out = None):
        endmarker = self.boundary + ntob('--')
        delim = ntob('')
        prev_lf = True
        lines = []
        seen = 0
        while True:
            line = self.fp.readline(65536)
            if not line:
                raise EOFError('Illegal end of multipart body.')
            if line.startswith(ntob('--')) and prev_lf:
                strippedline = line.strip()
                if strippedline == self.boundary:
                    break
                if strippedline == endmarker:
                    self.fp.finish()
                    break
            line = delim + line
            if line.endswith(ntob('\r\n')):
                delim = ntob('\r\n')
                line = line[:-2]
                prev_lf = True
            elif line.endswith(ntob('\n')):
                delim = ntob('\n')
                line = line[:-1]
                prev_lf = True
            else:
                delim = ntob('')
                prev_lf = False
            if fp_out is None:
                lines.append(line)
                seen += len(line)
                if seen > self.maxrambytes:
                    fp_out = self.make_file()
                    for line in lines:
                        fp_out.write(line)

            else:
                fp_out.write(line)

        if fp_out is None:
            result = ntob('').join(lines)
            for charset in self.attempt_charsets:
                try:
                    result = result.decode(charset)
                except UnicodeDecodeError:
                    pass
                else:
                    self.charset = charset
                    return result

            else:
                raise cherrypy.HTTPError(400, 'The request entity could not be decoded. The following charsets were attempted: %s' % repr(self.attempt_charsets))

        else:
            fp_out.seek(0)
            return fp_out

    def default_proc(self):
        if self.filename:
            self.file = self.read_into_file()
        else:
            result = self.read_lines_to_boundary()
            if isinstance(result, basestring):
                self.value = result
            else:
                self.file = result

    def read_into_file(self, fp_out = None):
        if fp_out is None:
            fp_out = self.make_file()
        self.read_lines_to_boundary(fp_out=fp_out)
        return fp_out


Entity.part_class = Part

class Infinity(object):

    def __cmp__(self, other):
        return 1

    def __sub__(self, other):
        return self


inf = Infinity()
comma_separated_headers = ['Accept',
 'Accept-Charset',
 'Accept-Encoding',
 'Accept-Language',
 'Accept-Ranges',
 'Allow',
 'Cache-Control',
 'Connection',
 'Content-Encoding',
 'Content-Language',
 'Expect',
 'If-Match',
 'If-None-Match',
 'Pragma',
 'Proxy-Authenticate',
 'Te',
 'Trailer',
 'Transfer-Encoding',
 'Upgrade',
 'Vary',
 'Via',
 'Warning',
 'Www-Authenticate']

class SizedReader:

    def __init__(self, fp, length, maxbytes, bufsize = 8192, has_trailers = False):
        self.fp = fp
        self.length = length
        self.maxbytes = maxbytes
        self.buffer = ntob('')
        self.bufsize = bufsize
        self.bytes_read = 0
        self.done = False
        self.has_trailers = has_trailers

    def read(self, size = None, fp_out = None):
        if self.length is None:
            if size is None:
                remaining = inf
            else:
                remaining = size
        else:
            remaining = self.length - self.bytes_read
            if size and size < remaining:
                remaining = size
        if remaining == 0:
            self.finish()
            if fp_out is None:
                return ntob('')
            else:
                return
        chunks = []
        if self.buffer:
            if remaining is inf:
                data = self.buffer
                self.buffer = ntob('')
            else:
                data = self.buffer[:remaining]
                self.buffer = self.buffer[remaining:]
            datalen = len(data)
            remaining -= datalen
            self.bytes_read += datalen
            if self.maxbytes and self.bytes_read > self.maxbytes:
                raise cherrypy.HTTPError(413)
            if fp_out is None:
                chunks.append(data)
            else:
                fp_out.write(data)
        while remaining > 0:
            chunksize = min(remaining, self.bufsize)
            try:
                data = self.fp.read(chunksize)
            except Exception:
                e = sys.exc_info()[1]
                if e.__class__.__name__ == 'MaxSizeExceeded':
                    raise cherrypy.HTTPError(413, 'Maximum request length: %r' % e.args[1])
                else:
                    raise 

            if not data:
                self.finish()
                break
            datalen = len(data)
            remaining -= datalen
            self.bytes_read += datalen
            if self.maxbytes and self.bytes_read > self.maxbytes:
                raise cherrypy.HTTPError(413)
            if fp_out is None:
                chunks.append(data)
            else:
                fp_out.write(data)

        if fp_out is None:
            return ntob('').join(chunks)

    def readline(self, size = None):
        chunks = []
        while size is None or size > 0:
            chunksize = self.bufsize
            if size is not None and size < self.bufsize:
                chunksize = size
            data = self.read(chunksize)
            if not data:
                break
            pos = data.find(ntob('\n')) + 1
            if pos:
                chunks.append(data[:pos])
                remainder = data[pos:]
                self.buffer += remainder
                self.bytes_read -= len(remainder)
                break
            else:
                chunks.append(data)

        return ntob('').join(chunks)

    def readlines(self, sizehint = None):
        if self.length is not None:
            if sizehint is None:
                sizehint = self.length - self.bytes_read
            else:
                sizehint = min(sizehint, self.length - self.bytes_read)
        lines = []
        seen = 0
        while True:
            line = self.readline()
            if not line:
                break
            lines.append(line)
            seen += len(line)
            if seen >= sizehint:
                break

        return lines

    def finish(self):
        self.done = True
        if self.has_trailers and hasattr(self.fp, 'read_trailer_lines'):
            self.trailers = {}
            try:
                for line in self.fp.read_trailer_lines():
                    if line[0] in ntob(' \t'):
                        v = line.strip()
                    else:
                        try:
                            k, v = line.split(ntob(':'), 1)
                        except ValueError:
                            raise ValueError('Illegal header line.')

                        k = k.strip().title()
                        v = v.strip()
                    if k in comma_separated_headers:
                        existing = self.trailers.get(envname)
                        if existing:
                            v = ntob(', ').join((existing, v))
                    self.trailers[k] = v

            except Exception:
                e = sys.exc_info()[1]
                if e.__class__.__name__ == 'MaxSizeExceeded':
                    raise cherrypy.HTTPError(413, 'Maximum request length: %r' % e.args[1])
                else:
                    raise 


class RequestBody(Entity):
    bufsize = 8192
    default_content_type = ''
    maxbytes = None

    def __init__(self, fp, headers, params = None, request_params = None):
        Entity.__init__(self, fp, headers, params)
        if self.content_type.value.startswith('text/'):
            for c in ('ISO-8859-1', 'iso-8859-1', 'Latin-1', 'latin-1'):
                if c in self.attempt_charsets:
                    break
            else:
                self.attempt_charsets.append('ISO-8859-1')

        self.processors['multipart'] = _old_process_multipart
        if request_params is None:
            request_params = {}
        self.request_params = request_params

    def process(self):
        h = cherrypy.serving.request.headers
        if 'Content-Length' not in h and 'Transfer-Encoding' not in h:
            raise cherrypy.HTTPError(411)
        self.fp = SizedReader(self.fp, self.length, self.maxbytes, bufsize=self.bufsize, has_trailers='Trailer' in h)
        super(RequestBody, self).process()
        request_params = self.request_params
        for key, value in self.params.items():
            if isinstance(key, unicode):
                key = key.encode('ISO-8859-1')
            if key in request_params:
                if not isinstance(request_params[key], list):
                    request_params[key] = [request_params[key]]
                request_params[key].append(value)
            else:
                request_params[key] = value