CRLF = '\r\n'
import os
import Queue
import re
quoted_slash = re.compile('(?i)%2F')
import rfc822
import socket
import sys
if 'win' in sys.platform and not hasattr(socket, 'IPPROTO_IPV6'):
    socket.IPPROTO_IPV6 = 41
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
_fileobject_uses_str_type = isinstance(socket._fileobject(None)._rbuf, basestring)
import threading
import time
import traceback
from urllib import unquote
from urlparse import urlparse
import warnings
import errno

def plat_specific_errors(*errnames):
    errno_names = dir(errno)
    nums = [ getattr(errno, k) for k in errnames if k in errno_names ]
    return dict.fromkeys(nums).keys()


socket_error_eintr = plat_specific_errors('EINTR', 'WSAEINTR')
socket_errors_to_ignore = plat_specific_errors('EPIPE', 'EBADF', 'WSAEBADF', 'ENOTSOCK', 'WSAENOTSOCK', 'ETIMEDOUT', 'WSAETIMEDOUT', 'ECONNREFUSED', 'WSAECONNREFUSED', 'ECONNRESET', 'WSAECONNRESET', 'ECONNABORTED', 'WSAECONNABORTED', 'ENETRESET', 'WSAENETRESET', 'EHOSTDOWN', 'EHOSTUNREACH')
socket_errors_to_ignore.append('timed out')
socket_errors_to_ignore.append('The read operation timed out')
socket_errors_nonblocking = plat_specific_errors('EAGAIN', 'EWOULDBLOCK', 'WSAEWOULDBLOCK')
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
 'TE',
 'Trailer',
 'Transfer-Encoding',
 'Upgrade',
 'Vary',
 'Via',
 'Warning',
 'WWW-Authenticate']

def read_headers(rfile, hdict = None):
    if hdict is None:
        hdict = {}
    while True:
        line = rfile.readline()
        if not line:
            raise ValueError('Illegal end of headers.')
        if line == CRLF:
            break
        if not line.endswith(CRLF):
            raise ValueError('HTTP requires CRLF terminators')
        if line[0] in ' \t':
            v = line.strip()
        else:
            try:
                (k, v,) = line.split(':', 1)
            except ValueError:
                raise ValueError('Illegal header line.')
            k = k.strip().title()
            v = v.strip()
            hname = k
        if k in comma_separated_headers:
            existing = hdict.get(hname)
            if existing:
                v = ', '.join((existing, v))
        hdict[hname] = v

    return hdict



class MaxSizeExceeded(Exception):
    pass

class SizeCheckWrapper(object):

    def __init__(self, rfile, maxlen):
        self.rfile = rfile
        self.maxlen = maxlen
        self.bytes_read = 0



    def _check_length(self):
        if self.maxlen and self.bytes_read > self.maxlen:
            raise MaxSizeExceeded()



    def read(self, size = None):
        data = self.rfile.read(size)
        self.bytes_read += len(data)
        self._check_length()
        return data



    def readline(self, size = None):
        if size is not None:
            data = self.rfile.readline(size)
            self.bytes_read += len(data)
            self._check_length()
            return data
        res = []
        while True:
            data = self.rfile.readline(256)
            self.bytes_read += len(data)
            self._check_length()
            res.append(data)
            if len(data) < 256 or data[-1:] == '\n':
                return ''.join(res)




    def readlines(self, sizehint = 0):
        total = 0
        lines = []
        line = self.readline()
        while line:
            lines.append(line)
            total += len(line)
            if 0 < sizehint <= total:
                break
            line = self.readline()

        return lines



    def close(self):
        self.rfile.close()



    def __iter__(self):
        return self



    def next(self):
        data = self.rfile.next()
        self.bytes_read += len(data)
        self._check_length()
        return data




class KnownLengthRFile(object):

    def __init__(self, rfile, content_length):
        self.rfile = rfile
        self.remaining = content_length



    def read(self, size = None):
        if self.remaining == 0:
            return ''
        if size is None:
            size = self.remaining
        else:
            size = min(size, self.remaining)
        data = self.rfile.read(size)
        self.remaining -= len(data)
        return data



    def readline(self, size = None):
        if self.remaining == 0:
            return ''
        if size is None:
            size = self.remaining
        else:
            size = min(size, self.remaining)
        data = self.rfile.readline(size)
        self.remaining -= len(data)
        return data



    def readlines(self, sizehint = 0):
        total = 0
        lines = []
        line = self.readline(sizehint)
        while line:
            lines.append(line)
            total += len(line)
            if 0 < sizehint <= total:
                break
            line = self.readline(sizehint)

        return lines



    def close(self):
        self.rfile.close()



    def __iter__(self):
        return self



    def __next__(self):
        data = next(self.rfile)
        self.remaining -= len(data)
        return data




class MaxSizeExceeded(Exception):
    pass

class ChunkedRFile(object):

    def __init__(self, rfile, maxlen, bufsize = 8192):
        self.rfile = rfile
        self.maxlen = maxlen
        self.bytes_read = 0
        self.buffer = ''
        self.bufsize = bufsize
        self.closed = False



    def _fetch(self):
        if self.closed:
            return 
        line = self.rfile.readline()
        self.bytes_read += len(line)
        if self.maxlen and self.bytes_read > self.maxlen:
            raise MaxSizeExceeded('Request Entity Too Large', self.maxlen)
        line = line.strip().split(';', 1)
        try:
            chunk_size = line.pop(0)
            chunk_size = int(chunk_size, 16)
        except ValueError:
            raise ValueError('Bad chunked transfer size: ' + repr(chunk_size))
        if chunk_size <= 0:
            self.closed = True
            return 
        if self.maxlen and self.bytes_read + chunk_size > self.maxlen:
            raise IOError('Request Entity Too Large')
        chunk = self.rfile.read(chunk_size)
        self.bytes_read += len(chunk)
        self.buffer += chunk
        crlf = self.rfile.read(2)
        if crlf != CRLF:
            raise ValueError("Bad chunked transfer coding (expected '\\r\\n', got " + repr(crlf) + ')')



    def read(self, size = None):
        data = ''
        while True:
            if size and len(data) >= size:
                return data
            if not self.buffer:
                self._fetch()
                if not self.buffer:
                    return data
            if size:
                remaining = size - len(data)
                data += self.buffer[:remaining]
                self.buffer = self.buffer[remaining:]
            else:
                data += self.buffer




    def readline(self, size = None):
        data = ''
        while True:
            if size and len(data) >= size:
                return data
            if not self.buffer:
                self._fetch()
                if not self.buffer:
                    return data
            newline_pos = self.buffer.find('\n')
            if size:
                if newline_pos == -1:
                    remaining = size - len(data)
                    data += self.buffer[:remaining]
                    self.buffer = self.buffer[remaining:]
                else:
                    remaining = min(size - len(data), newline_pos)
                    data += self.buffer[:remaining]
                    self.buffer = self.buffer[remaining:]
            elif newline_pos == -1:
                data += self.buffer
            else:
                data += self.buffer[:newline_pos]
                self.buffer = self.buffer[newline_pos:]




    def readlines(self, sizehint = 0):
        total = 0
        lines = []
        line = self.readline(sizehint)
        while line:
            lines.append(line)
            total += len(line)
            if 0 < sizehint <= total:
                break
            line = self.readline(sizehint)

        return lines



    def read_trailer_lines(self):
        if not self.closed:
            raise ValueError('Cannot read trailers until the request body has been read.')
        while True:
            line = self.rfile.readline()
            if not line:
                raise ValueError('Illegal end of headers.')
            self.bytes_read += len(line)
            if self.maxlen and self.bytes_read > self.maxlen:
                raise IOError('Request Entity Too Large')
            if line == CRLF:
                break
            if not line.endswith(CRLF):
                raise ValueError('HTTP requires CRLF terminators')
            yield line




    def close(self):
        self.rfile.close()



    def __iter__(self):
        total = 0
        line = self.readline(sizehint)
        while line:
            yield line
            total += len(line)
            if 0 < sizehint <= total:
                break
            line = self.readline(sizehint)





class HTTPRequest(object):

    def __init__(self, server, conn):
        self.server = server
        self.conn = conn
        self.ready = False
        self.started_request = False
        self.scheme = 'http'
        if self.server.ssl_adapter is not None:
            self.scheme = 'https'
        self.inheaders = {}
        self.status = ''
        self.outheaders = []
        self.sent_headers = False
        self.close_connection = False
        self.chunked_write = False



    def parse_request(self):
        self.rfile = SizeCheckWrapper(self.conn.rfile, self.server.max_request_header_size)
        try:
            self._parse_request()
        except MaxSizeExceeded:
            self.simple_response('413 Request Entity Too Large')
            return 



    def _parse_request(self):
        request_line = self.rfile.readline()
        self.started_request = True
        if not request_line:
            self.ready = False
            return 
        if request_line == CRLF:
            request_line = self.rfile.readline()
            if not request_line:
                self.ready = False
                return 
        if not request_line.endswith(CRLF):
            self.simple_response(400, 'HTTP requires CRLF terminators')
            return 
        try:
            (method, uri, req_protocol,) = request_line.strip().split(' ', 2)
        except ValueError:
            self.simple_response(400, 'Malformed Request-Line')
            return 
        self.uri = uri
        self.method = method
        (scheme, authority, path,) = self.parse_request_uri(uri)
        if '#' in path:
            self.simple_response('400 Bad Request', 'Illegal #fragment in Request-URI.')
            return 
        if scheme:
            self.scheme = scheme
        qs = ''
        if '?' in path:
            (path, qs,) = path.split('?', 1)
        try:
            atoms = [ unquote(x) for x in quoted_slash.split(path) ]
        except ValueError as ex:
            self.simple_response('400 Bad Request', ex.args[0])
            return 
        path = '%2F'.join(atoms)
        self.path = path
        self.qs = qs
        rp = (int(req_protocol[5]), int(req_protocol[7]))
        sp = (int(self.server.protocol[5]), int(self.server.protocol[7]))
        if sp[0] != rp[0]:
            self.simple_response('505 HTTP Version Not Supported')
            return 
        self.request_protocol = req_protocol
        self.response_protocol = 'HTTP/%s.%s' % min(rp, sp)
        try:
            read_headers(self.rfile, self.inheaders)
        except ValueError as ex:
            self.simple_response('400 Bad Request', ex.args[0])
            return 
        mrbs = self.server.max_request_body_size
        if mrbs and int(self.inheaders.get('Content-Length', 0)) > mrbs:
            self.simple_response('413 Request Entity Too Large')
            return 
        if self.response_protocol == 'HTTP/1.1':
            if self.inheaders.get('Connection', '') == 'close':
                self.close_connection = True
        elif self.inheaders.get('Connection', '') != 'Keep-Alive':
            self.close_connection = True
        te = None
        if self.response_protocol == 'HTTP/1.1':
            te = self.inheaders.get('Transfer-Encoding')
            if te:
                te = [ x.strip().lower() for x in te.split(',') if x.strip() ]
        self.chunked_read = False
        if te:
            for enc in te:
                if enc == 'chunked':
                    self.chunked_read = True
                else:
                    self.simple_response('501 Unimplemented')
                    self.close_connection = True
                    return 

        if self.inheaders.get('Expect', '') == '100-continue':
            msg = self.server.protocol + ' 100 Continue\r\n\r\n'
            try:
                self.conn.wfile.sendall(msg)
            except socket.error as x:
                if x.args[0] not in socket_errors_to_ignore:
                    raise 
        self.ready = True



    def parse_request_uri(self, uri):
        if uri == '*':
            return (None, None, uri)
        else:
            i = uri.find('://')
            if i > 0 and '?' not in uri[:i]:
                (scheme, remainder,) = (uri[:i].lower(), uri[(i + 3):])
                (authority, path,) = remainder.split('/', 1)
                return (scheme, authority, path)
            if uri.startswith('/'):
                return (None, None, uri)
            return (None, uri, None)



    def respond(self):
        mrbs = self.server.max_request_body_size
        if self.chunked_read:
            self.rfile = ChunkedRFile(self.conn.rfile, mrbs)
        else:
            cl = int(self.inheaders.get('Content-Length', 0))
            if mrbs and mrbs < cl:
                if not self.sent_headers:
                    self.simple_response('413 Request Entity Too Large')
                return 
            self.rfile = KnownLengthRFile(self.conn.rfile, cl)
        self.server.gateway(self).respond()
        if self.ready and not self.sent_headers:
            self.sent_headers = True
            self.send_headers()
        if self.chunked_write:
            self.conn.wfile.sendall('0\r\n\r\n')



    def simple_response(self, status, msg = ''):
        status = str(status)
        buf = [self.server.protocol + ' ' + status + CRLF, 'Content-Length: %s\r\n' % len(msg), 'Content-Type: text/plain\r\n']
        if status[:3] == '413' and self.response_protocol == 'HTTP/1.1':
            self.close_connection = True
            buf.append('Connection: close\r\n')
        buf.append(CRLF)
        if msg:
            if isinstance(msg, unicode):
                msg = msg.encode('ISO-8859-1')
            buf.append(msg)
        try:
            self.conn.wfile.sendall(''.join(buf))
        except socket.error as x:
            if x.args[0] not in socket_errors_to_ignore:
                raise 



    def write(self, chunk):
        if self.chunked_write and chunk:
            buf = [hex(len(chunk))[2:],
             CRLF,
             chunk,
             CRLF]
            self.conn.wfile.sendall(''.join(buf))
        else:
            self.conn.wfile.sendall(chunk)



    def send_headers(self):
        hkeys = [ key.lower() for (key, value,) in self.outheaders ]
        status = int(self.status[:3])
        if status == 413:
            self.close_connection = True
        elif 'content-length' not in hkeys:
            if status < 200 or status in (204, 205, 304):
                pass
            elif self.response_protocol == 'HTTP/1.1' and self.method != 'HEAD':
                self.chunked_write = True
                self.outheaders.append(('Transfer-Encoding', 'chunked'))
            else:
                self.close_connection = True
        if 'connection' not in hkeys:
            if self.response_protocol == 'HTTP/1.1':
                if self.close_connection:
                    self.outheaders.append(('Connection', 'close'))
            elif not self.close_connection:
                self.outheaders.append(('Connection', 'Keep-Alive'))
        if not self.close_connection and not self.chunked_read:
            remaining = getattr(self.rfile, 'remaining', 0)
            if remaining > 0:
                self.rfile.read(remaining)
        if 'date' not in hkeys:
            self.outheaders.append(('Date', rfc822.formatdate()))
        if 'server' not in hkeys:
            self.outheaders.append(('Server', self.server.server_name))
        buf = [self.server.protocol + ' ' + self.status + CRLF]
        for (k, v,) in self.outheaders:
            buf.append(k + ': ' + v + CRLF)

        buf.append(CRLF)
        self.conn.wfile.sendall(''.join(buf))




class NoSSLError(Exception):
    pass

class FatalSSLAlert(Exception):
    pass
if not _fileobject_uses_str_type:

    class CP_fileobject(socket._fileobject):

        def sendall(self, data):
            while data:
                try:
                    bytes_sent = self.send(data)
                    data = data[bytes_sent:]
                except socket.error as e:
                    if e.args[0] not in socket_errors_nonblocking:
                        raise 




        def send(self, data):
            return self._sock.send(data)



        def flush(self):
            if self._wbuf:
                buffer = ''.join(self._wbuf)
                self._wbuf = []
                self.sendall(buffer)



        def recv(self, size):
            while True:
                try:
                    return self._sock.recv(size)
                except socket.error as e:
                    if e.args[0] not in socket_errors_nonblocking and e.args[0] not in socket_error_eintr:
                        raise 




        def read(self, size = -1):
            rbufsize = max(self._rbufsize, self.default_bufsize)
            buf = self._rbuf
            buf.seek(0, 2)
            if size < 0:
                self._rbuf = StringIO.StringIO()
                while True:
                    data = self.recv(rbufsize)
                    if not data:
                        break
                    buf.write(data)

                return buf.getvalue()
            else:
                buf_len = buf.tell()
                if buf_len >= size:
                    buf.seek(0)
                    rv = buf.read(size)
                    self._rbuf = StringIO.StringIO()
                    self._rbuf.write(buf.read())
                    return rv
                self._rbuf = StringIO.StringIO()
                while True:
                    left = size - buf_len
                    data = self.recv(left)
                    if not data:
                        break
                    n = len(data)
                    if n == size and not buf_len:
                        return data
                    if n == left:
                        buf.write(data)
                        del data
                        break
                    buf.write(data)
                    buf_len += n
                    del data

                return buf.getvalue()



        def readline(self, size = -1):
            buf = self._rbuf
            buf.seek(0, 2)
            if buf.tell() > 0:
                buf.seek(0)
                bline = buf.readline(size)
                if bline.endswith('\n') or len(bline) == size:
                    self._rbuf = StringIO.StringIO()
                    self._rbuf.write(buf.read())
                    return bline
                del bline
            if size < 0:
                if self._rbufsize <= 1:
                    buf.seek(0)
                    buffers = [buf.read()]
                    self._rbuf = StringIO.StringIO()
                    data = None
                    recv = self.recv
                    while data != '\n':
                        data = recv(1)
                        if not data:
                            break
                        buffers.append(data)

                    return ''.join(buffers)
                buf.seek(0, 2)
                self._rbuf = StringIO.StringIO()
                while True:
                    data = self.recv(self._rbufsize)
                    if not data:
                        break
                    nl = data.find('\n')
                    if nl >= 0:
                        nl += 1
                        buf.write(data[:nl])
                        self._rbuf.write(data[nl:])
                        del data
                        break
                    buf.write(data)

                return buf.getvalue()
            else:
                buf.seek(0, 2)
                buf_len = buf.tell()
                if buf_len >= size:
                    buf.seek(0)
                    rv = buf.read(size)
                    self._rbuf = StringIO.StringIO()
                    self._rbuf.write(buf.read())
                    return rv
                self._rbuf = StringIO.StringIO()
                while True:
                    data = self.recv(self._rbufsize)
                    if not data:
                        break
                    left = size - buf_len
                    nl = data.find('\n', 0, left)
                    if nl >= 0:
                        nl += 1
                        self._rbuf.write(data[nl:])
                        if buf_len:
                            buf.write(data[:nl])
                            break
                        else:
                            return data[:nl]
                    n = len(data)
                    if n == size and not buf_len:
                        return data
                    if n >= left:
                        buf.write(data[:left])
                        self._rbuf.write(data[left:])
                        break
                    buf.write(data)
                    buf_len += n

                return buf.getvalue()



else:

    class CP_fileobject(socket._fileobject):

        def sendall(self, data):
            while data:
                try:
                    bytes_sent = self.send(data)
                    data = data[bytes_sent:]
                except socket.error as e:
                    if e.args[0] not in socket_errors_nonblocking:
                        raise 




        def send(self, data):
            return self._sock.send(data)



        def flush(self):
            if self._wbuf:
                buffer = ''.join(self._wbuf)
                self._wbuf = []
                self.sendall(buffer)



        def recv(self, size):
            while True:
                try:
                    return self._sock.recv(size)
                except socket.error as e:
                    if e.args[0] not in socket_errors_nonblocking and e.args[0] not in socket_error_eintr:
                        raise 




        def read(self, size = -1):
            if size < 0:
                buffers = [self._rbuf]
                self._rbuf = ''
                if self._rbufsize <= 1:
                    recv_size = self.default_bufsize
                else:
                    recv_size = self._rbufsize
                while True:
                    data = self.recv(recv_size)
                    if not data:
                        break
                    buffers.append(data)

                return ''.join(buffers)
            else:
                data = self._rbuf
                buf_len = len(data)
                if buf_len >= size:
                    self._rbuf = data[size:]
                    return data[:size]
                buffers = []
                if data:
                    buffers.append(data)
                self._rbuf = ''
                while True:
                    left = size - buf_len
                    recv_size = max(self._rbufsize, left)
                    data = self.recv(recv_size)
                    if not data:
                        break
                    buffers.append(data)
                    n = len(data)
                    if n >= left:
                        self._rbuf = data[left:]
                        buffers[-1] = data[:left]
                        break
                    buf_len += n

                return ''.join(buffers)



        def readline(self, size = -1):
            data = self._rbuf
            if size < 0:
                if self._rbufsize <= 1:
                    buffers = []
                    while data != '\n':
                        data = self.recv(1)
                        if not data:
                            break
                        buffers.append(data)

                    return ''.join(buffers)
                nl = data.find('\n')
                if nl >= 0:
                    nl += 1
                    self._rbuf = data[nl:]
                    return data[:nl]
                buffers = []
                if data:
                    buffers.append(data)
                self._rbuf = ''
                while True:
                    data = self.recv(self._rbufsize)
                    if not data:
                        break
                    buffers.append(data)
                    nl = data.find('\n')
                    if nl >= 0:
                        nl += 1
                        self._rbuf = data[nl:]
                        buffers[-1] = data[:nl]
                        break

                return ''.join(buffers)
            else:
                nl = data.find('\n', 0, size)
                if nl >= 0:
                    nl += 1
                    self._rbuf = data[nl:]
                    return data[:nl]
                buf_len = len(data)
                if buf_len >= size:
                    self._rbuf = data[size:]
                    return data[:size]
                buffers = []
                if data:
                    buffers.append(data)
                self._rbuf = ''
                while True:
                    data = self.recv(self._rbufsize)
                    if not data:
                        break
                    buffers.append(data)
                    left = size - buf_len
                    nl = data.find('\n', 0, left)
                    if nl >= 0:
                        nl += 1
                        self._rbuf = data[nl:]
                        buffers[-1] = data[:nl]
                        break
                    n = len(data)
                    if n >= left:
                        self._rbuf = data[left:]
                        buffers[-1] = data[:left]
                        break
                    buf_len += n

                return ''.join(buffers)




class HTTPConnection(object):
    remote_addr = None
    remote_port = None
    ssl_env = None
    rbufsize = -1
    RequestHandlerClass = HTTPRequest

    def __init__(self, server, sock, makefile = CP_fileobject):
        self.server = server
        self.socket = sock
        self.rfile = makefile(sock, 'rb', self.rbufsize)
        self.wfile = makefile(sock, 'wb', -1)



    def communicate(self):
        request_seen = False
        try:
            while True:
                req = None
                req = self.RequestHandlerClass(self.server, self)
                req.parse_request()
                if not req.ready:
                    return 
                request_seen = True
                req.respond()
                if req.close_connection:
                    return 

        except socket.error as e:
            errnum = e.args[0]
            if errnum == 'timed out':
                if not request_seen or req and req.started_request:
                    if req and not req.sent_headers:
                        try:
                            req.simple_response('408 Request Timeout')
                        except FatalSSLAlert:
                            return 
            elif errnum not in socket_errors_to_ignore:
                if req and not req.sent_headers:
                    try:
                        req.simple_response('500 Internal Server Error', format_exc())
                    except FatalSSLAlert:
                        return 
            return 
        except (KeyboardInterrupt, SystemExit):
            raise 
        except FatalSSLAlert:
            return 
        except NoSSLError:
            if req and not req.sent_headers:
                self.wfile = CP_fileobject(self.socket._sock, 'wb', -1)
                req.simple_response('400 Bad Request', 'The client sent a plain HTTP request, but this server only speaks HTTPS on this port.')
                self.linger = True
        except Exception:
            if req and not req.sent_headers:
                try:
                    req.simple_response('500 Internal Server Error', format_exc())
                except FatalSSLAlert:
                    return 


    linger = False

    def close(self):
        self.rfile.close()
        if not self.linger:
            if hasattr(self.socket, '_sock'):
                self.socket._sock.close()
            self.socket.close()




def format_exc(limit = None):
    try:
        (etype, value, tb,) = sys.exc_info()
        return ''.join(traceback.format_exception(etype, value, tb, limit))

    finally:
        etype = value = tb = None



_SHUTDOWNREQUEST = None

class WorkerThread(threading.Thread):
    conn = None

    def __init__(self, server):
        self.ready = False
        self.server = server
        threading.Thread.__init__(self)



    def run(self):
        try:
            self.ready = True
            while True:
                conn = self.server.requests.get()
                if conn is _SHUTDOWNREQUEST:
                    return 
                self.conn = conn
                try:
                    conn.communicate()

                finally:
                    conn.close()
                    self.conn = None


        except (KeyboardInterrupt, SystemExit) as exc:
            self.server.interrupt = exc




class ThreadPool(object):

    def __init__(self, server, min = 10, max = -1):
        self.server = server
        self.min = min
        self.max = max
        self._threads = []
        self._queue = Queue.Queue()
        self.get = self._queue.get



    def start(self):
        for i in range(self.min):
            self._threads.append(WorkerThread(self.server))

        for worker in self._threads:
            worker.setName('CP Server ' + worker.getName())
            worker.start()

        for worker in self._threads:
            while not worker.ready:
                time.sleep(0.1)





    def _get_idle(self):
        return len([ t for t in self._threads if t.conn is None ])


    idle = property(_get_idle, doc=_get_idle.__doc__)

    def put(self, obj):
        self._queue.put(obj)
        if obj is _SHUTDOWNREQUEST:
            return 



    def grow(self, amount):
        for i in range(amount):
            if self.max > 0 and len(self._threads) >= self.max:
                break
            worker = WorkerThread(self.server)
            worker.setName('CP Server ' + worker.getName())
            self._threads.append(worker)
            worker.start()




    def shrink(self, amount):
        for t in self._threads:
            if not t.isAlive():
                self._threads.remove(t)
                amount -= 1

        if amount > 0:
            for i in range(min(amount, len(self._threads) - self.min)):
                self._queue.put(_SHUTDOWNREQUEST)




    def stop(self, timeout = 5):
        for worker in self._threads:
            self._queue.put(_SHUTDOWNREQUEST)

        current = threading.currentThread()
        if timeout and timeout >= 0:
            endtime = time.time() + timeout
        while self._threads:
            worker = self._threads.pop()
            if worker is not current and worker.isAlive():
                try:
                    if timeout is None or timeout < 0:
                        worker.join()
                    else:
                        remaining_time = endtime - time.time()
                        if remaining_time > 0:
                            worker.join(remaining_time)
                        if worker.isAlive():
                            c = worker.conn
                            if c and not c.rfile.closed:
                                try:
                                    c.socket.shutdown(socket.SHUT_RD)
                                except TypeError:
                                    c.socket.shutdown()
                            worker.join()
                except (AssertionError, KeyboardInterrupt) as exc1:
                    pass




try:
    import fcntl
except ImportError:
    try:
        from ctypes import windll, WinError
    except ImportError:

        def prevent_socket_inheritance(sock):
            pass


    else:

        def prevent_socket_inheritance(sock):
            if not windll.kernel32.SetHandleInformation(sock.fileno(), 1, 0):
                raise WinError()


else:

    def prevent_socket_inheritance(sock):
        fd = sock.fileno()
        old_flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFD, old_flags | fcntl.FD_CLOEXEC)



class SSLAdapter(object):

    def __init__(self, certificate, private_key, certificate_chain = None):
        self.certificate = certificate
        self.private_key = private_key
        self.certificate_chain = certificate_chain



    def wrap(self, sock):
        raise NotImplemented



    def makefile(self, sock, mode = 'r', bufsize = -1):
        raise NotImplemented




class HTTPServer(object):
    protocol = 'HTTP/1.1'
    _bind_addr = '127.0.0.1'
    version = 'CherryPy/3.2.0rc1'
    response_header = None
    ready = False
    _interrupt = None
    max_request_header_size = 0
    max_request_body_size = 0
    nodelay = True
    ConnectionClass = HTTPConnection
    ssl_adapter = None

    def __init__(self, bind_addr, gateway, minthreads = 10, maxthreads = -1, server_name = None):
        self.bind_addr = bind_addr
        self.gateway = gateway
        self.requests = ThreadPool(self, min=minthreads or 1, max=maxthreads)
        if not server_name:
            server_name = socket.gethostname()
        self.server_name = server_name



    def __str__(self):
        return '%s.%s(%r)' % (self.__module__, self.__class__.__name__, self.bind_addr)



    def _get_bind_addr(self):
        return self._bind_addr



    def _set_bind_addr(self, value):
        if isinstance(value, tuple) and value[0] in ('', None):
            raise ValueError("Host values of '' or None are not allowed. Use '0.0.0.0' (IPv4) or '::' (IPv6) instead to listen on all active interfaces.")
        self._bind_addr = value


    bind_addr = property(_get_bind_addr, _set_bind_addr, doc='The interface on which to listen for connections.\n        \n        For TCP sockets, a (host, port) tuple. Host values may be any IPv4\n        or IPv6 address, or any valid hostname. The string \'localhost\' is a\n        synonym for \'127.0.0.1\' (or \'::1\', if your hosts file prefers IPv6).\n        The string \'0.0.0.0\' is a special IPv4 entry meaning "any active\n        interface" (INADDR_ANY), and \'::\' is the similar IN6ADDR_ANY for\n        IPv6. The empty string or None are not allowed.\n        \n        For UNIX sockets, supply the filename as a string.')

    def start(self):
        self._interrupt = None
        if self.ssl_adapter is None and getattr(self, 'ssl_certificate', None) and getattr(self, 'ssl_private_key', None):
            warnings.warn('SSL attributes are deprecated in CherryPy 3.2, and will be removed in CherryPy 3.3. Use an ssl_adapter attribute instead.', DeprecationWarning)
            try:
                from cherrypy.wsgiserver.ssl_pyopenssl import pyOpenSSLAdapter
            except ImportError:
                pass
            else:
                self.ssl_adapter = pyOpenSSLAdapter(self.ssl_certificate, self.ssl_private_key, getattr(self, 'ssl_certificate_chain', None))
        if isinstance(self.bind_addr, basestring):
            try:
                os.unlink(self.bind_addr)
            except:
                pass
            try:
                os.chmod(self.bind_addr, 511)
            except:
                pass
            info = [(socket.AF_UNIX,
              socket.SOCK_STREAM,
              0,
              '',
              self.bind_addr)]
        else:
            (host, port,) = self.bind_addr
            try:
                info = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
            except socket.gaierror:
                if ':' in self.bind_addr[0]:
                    info = [(socket.AF_INET6,
                      socket.SOCK_STREAM,
                      0,
                      '',
                      self.bind_addr + (0, 0))]
                else:
                    info = [(socket.AF_INET,
                      socket.SOCK_STREAM,
                      0,
                      '',
                      self.bind_addr)]
        self.socket = None
        msg = 'No socket could be created'
        for res in info:
            (af, socktype, proto, canonname, sa,) = res
            try:
                self.bind(af, socktype, proto)
            except socket.error as msg:
                if self.socket:
                    self.socket.close()
                self.socket = None
                continue
            break

        if not self.socket:
            raise socket.error(msg)
        self.socket.settimeout(1)
        self.socket.listen(self.request_queue_size)
        self.requests.start()
        self.ready = True
        while self.ready:
            self.tick()
            if self.interrupt:
                while self.interrupt is True:
                    time.sleep(0.1)

                if self.interrupt:
                    raise self.interrupt




    def bind(self, family, type, proto = 0):
        self.socket = socket.socket(family, type, proto)
        prevent_socket_inheritance(self.socket)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.nodelay and not isinstance(self.bind_addr, str):
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        if self.ssl_adapter is not None:
            self.socket = self.ssl_adapter.bind(self.socket)
        if family == socket.AF_INET6 and self.bind_addr[0] in ('::', '::0', '::0.0.0.0'):
            try:
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            except (AttributeError, socket.error):
                pass
        self.socket.bind(self.bind_addr)



    def tick(self):
        try:
            (s, addr,) = self.socket.accept()
            if not self.ready:
                return 
            prevent_socket_inheritance(s)
            if hasattr(s, 'settimeout'):
                s.settimeout(self.timeout)
            if self.response_header is None:
                self.response_header = '%s Server' % self.version
            makefile = CP_fileobject
            ssl_env = {}
            if self.ssl_adapter is not None:
                try:
                    (s, ssl_env,) = self.ssl_adapter.wrap(s)
                except NoSSLError:
                    msg = 'The client sent a plain HTTP request, but this server only speaks HTTPS on this port.'
                    buf = ['%s 400 Bad Request\r\n' % self.protocol,
                     'Content-Length: %s\r\n' % len(msg),
                     'Content-Type: text/plain\r\n\r\n',
                     msg]
                    wfile = CP_fileobject(s, 'wb', -1)
                    try:
                        wfile.sendall(''.join(buf))
                    except socket.error as x:
                        if x.args[0] not in socket_errors_to_ignore:
                            raise 
                    return 
                if not s:
                    return 
                makefile = self.ssl_adapter.makefile
            conn = self.ConnectionClass(self, s, makefile)
            if not isinstance(self.bind_addr, basestring):
                if addr is None:
                    if len(s.getsockname()) == 2:
                        addr = ('0.0.0.0', 0)
                    else:
                        addr = ('::', 0)
                conn.remote_addr = addr[0]
                conn.remote_port = addr[1]
            conn.ssl_env = ssl_env
            self.requests.put(conn)
        except socket.timeout:
            return 
        except socket.error as x:
            if x.args[0] in socket_error_eintr:
                return 
            if x.args[0] in socket_errors_nonblocking:
                return 
            if x.args[0] in socket_errors_to_ignore:
                return 
            raise 



    def _get_interrupt(self):
        return self._interrupt



    def _set_interrupt(self, interrupt):
        self._interrupt = True
        self.stop()
        self._interrupt = interrupt


    interrupt = property(_get_interrupt, _set_interrupt, doc='Set this to an Exception instance to interrupt the server.')

    def stop(self):
        self.ready = False
        sock = getattr(self, 'socket', None)
        if sock:
            if not isinstance(self.bind_addr, basestring):
                try:
                    (host, port,) = sock.getsockname()[:2]
                except socket.error as x:
                    if x.args[0] not in socket_errors_to_ignore:
                        raise 
                else:
                    for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
                        (af, socktype, proto, canonname, sa,) = res
                        s = None
                        try:
                            s = socket.socket(af, socktype, proto)
                            s.settimeout(1.0)
                            s.connect((host, port))
                            s.close()
                        except socket.error:
                            if s:
                                s.close()

            if hasattr(sock, 'close'):
                sock.close()
            self.socket = None
        self.requests.stop(self.shutdown_timeout)




class Gateway(object):

    def __init__(self, req):
        self.req = req



    def respond(self):
        raise NotImplemented



ssl_adapters = {'builtin': 'cherrypy.wsgiserver.ssl_builtin.BuiltinSSLAdapter',
 'pyopenssl': 'cherrypy.wsgiserver.ssl_pyopenssl.pyOpenSSLAdapter'}

def get_ssl_adapter_class(name = 'pyopenssl'):
    adapter = ssl_adapters[name.lower()]
    if isinstance(adapter, basestring):
        last_dot = adapter.rfind('.')
        attr_name = adapter[(last_dot + 1):]
        mod_path = adapter[:last_dot]
        try:
            mod = sys.modules[mod_path]
            if mod is None:
                raise KeyError()
        except KeyError:
            mod = __import__(mod_path, globals(), locals(), [''])
        try:
            adapter = getattr(mod, attr_name)
        except AttributeError:
            raise AttributeError("'%s' object has no attribute '%s'" % (mod_path, attr_name))
    return adapter



class CherryPyWSGIServer(HTTPServer):
    wsgi_version = (1, 1)

    def __init__(self, bind_addr, wsgi_app, numthreads = 10, server_name = None, max = -1, request_queue_size = 5, timeout = 10, shutdown_timeout = 5):
        self.requests = ThreadPool(self, min=numthreads or 1, max=max)
        self.wsgi_app = wsgi_app
        self.gateway = wsgi_gateways[self.wsgi_version]
        self.bind_addr = bind_addr
        if not server_name:
            server_name = socket.gethostname()
        self.server_name = server_name
        self.request_queue_size = request_queue_size
        self.timeout = timeout
        self.shutdown_timeout = shutdown_timeout



    def _get_numthreads(self):
        return self.requests.min



    def _set_numthreads(self, value):
        self.requests.min = value


    numthreads = property(_get_numthreads, _set_numthreads)


class WSGIGateway(Gateway):

    def __init__(self, req):
        self.req = req
        self.started_response = False
        self.env = self.get_environ()



    def get_environ(self):
        raise NotImplemented



    def respond(self):
        response = self.req.server.wsgi_app(self.env, self.start_response)
        try:
            for chunk in response:
                if chunk:
                    if isinstance(chunk, unicode):
                        chunk = chunk.encode('ISO-8859-1')
                    self.write(chunk)


        finally:
            if hasattr(response, 'close'):
                response.close()




    def start_response(self, status, headers, exc_info = None):
        if self.started_response and not exc_info:
            raise AssertionError('WSGI start_response called a second time with no exc_info.')
        self.started_response = True
        if self.req.sent_headers:
            try:
                raise exc_info[0], exc_info[1], exc_info[2]

            finally:
                exc_info = None

        self.req.status = status
        for (k, v,) in headers:
            if not isinstance(k, str):
                raise TypeError('WSGI response header key %r is not a byte string.' % k)
            if not isinstance(v, str):
                raise TypeError('WSGI response header value %r is not a byte string.' % v)

        self.req.outheaders.extend(headers)
        return self.write



    def write(self, chunk):
        if not self.started_response:
            raise AssertionError('WSGI write called before start_response.')
        if not self.req.sent_headers:
            self.req.sent_headers = True
            self.req.send_headers()
        self.req.write(chunk)




class WSGIGateway_10(WSGIGateway):

    def get_environ(self):
        req = self.req
        env = {'ACTUAL_SERVER_PROTOCOL': req.server.protocol,
         'PATH_INFO': req.path,
         'QUERY_STRING': req.qs,
         'REMOTE_ADDR': req.conn.remote_addr or '',
         'REMOTE_PORT': str(req.conn.remote_port or ''),
         'REQUEST_METHOD': req.method,
         'REQUEST_URI': req.uri,
         'SCRIPT_NAME': '',
         'SERVER_NAME': req.server.server_name,
         'SERVER_PROTOCOL': req.request_protocol,
         'wsgi.errors': sys.stderr,
         'wsgi.input': req.rfile,
         'wsgi.multiprocess': False,
         'wsgi.multithread': True,
         'wsgi.run_once': False,
         'wsgi.url_scheme': req.scheme,
         'wsgi.version': (1, 0)}
        if isinstance(req.server.bind_addr, basestring):
            env['SERVER_PORT'] = ''
        else:
            env['SERVER_PORT'] = str(req.server.bind_addr[1])
        for (k, v,) in req.inheaders.iteritems():
            env['HTTP_' + k.upper().replace('-', '_')] = v

        ct = env.pop('HTTP_CONTENT_TYPE', None)
        if ct is not None:
            env['CONTENT_TYPE'] = ct
        cl = env.pop('HTTP_CONTENT_LENGTH', None)
        if cl is not None:
            env['CONTENT_LENGTH'] = cl
        if req.conn.ssl_env:
            env.update(req.conn.ssl_env)
        return env




class WSGIGateway_11(WSGIGateway_10):

    def get_environ(self):
        env = WSGIGateway_10.get_environ(self)
        env['wsgi.version'] = (1, 1)
        return env




class WSGIGateway_u0(WSGIGateway_10):

    def get_environ(self):
        req = self.req
        env_10 = WSGIGateway_10.get_environ(self)
        env = dict([ (k.decode('ISO-8859-1'), v) for (k, v,) in env_10.iteritems() ])
        env[u'wsgi.version'] = ('u', 0)
        env.setdefault(u'wsgi.url_encoding', u'utf-8')
        try:
            for key in [u'PATH_INFO', u'SCRIPT_NAME', u'QUERY_STRING']:
                env[key] = env_10[str(key)].decode(env[u'wsgi.url_encoding'])

        except UnicodeDecodeError:
            env[u'wsgi.url_encoding'] = u'ISO-8859-1'
            for key in [u'PATH_INFO', u'SCRIPT_NAME', u'QUERY_STRING']:
                env[key] = env_10[str(key)].decode(env[u'wsgi.url_encoding'])

        for (k, v,) in sorted(env.items()):
            if isinstance(v, str) and k not in ('REQUEST_URI', 'wsgi.input'):
                env[k] = v.decode('ISO-8859-1')

        return env



wsgi_gateways = {(1, 0): WSGIGateway_10,
 (1, 1): WSGIGateway_11,
 ('u', 0): WSGIGateway_u0}

class WSGIPathInfoDispatcher(object):

    def __init__(self, apps):
        try:
            apps = apps.items()
        except AttributeError:
            pass
        apps.sort(cmp=lambda x, y: cmp(len(x[0]), len(y[0])))
        apps.reverse()
        self.apps = [ (p.rstrip('/'), a) for (p, a,) in apps ]



    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'] or '/'
        for (p, app,) in self.apps:
            if path.startswith(p + '/') or path == p:
                environ = environ.copy()
                environ['SCRIPT_NAME'] = environ['SCRIPT_NAME'] + p
                environ['PATH_INFO'] = path[len(p):]
                return app(environ, start_response)

        start_response('404 Not Found', [('Content-Type', 'text/plain'), ('Content-Length', '0')])
        return ['']




