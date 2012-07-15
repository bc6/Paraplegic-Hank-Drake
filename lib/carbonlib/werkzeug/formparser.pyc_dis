#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\formparser.py
import re
from cStringIO import StringIO
from tempfile import TemporaryFile
from itertools import chain, repeat
from werkzeug._internal import _decode_unicode, _empty_stream
_empty_string_iter = repeat('')
_multipart_boundary_re = re.compile('^[ -~]{0,200}[!-~]$')
_supported_multipart_encodings = frozenset(['base64', 'quoted-printable'])

def default_stream_factory(total_content_length, filename, content_type, content_length = None):
    if total_content_length > 512000:
        return TemporaryFile('wb+')
    return StringIO()


def parse_form_data(environ, stream_factory = None, charset = 'utf-8', errors = 'ignore', max_form_memory_size = None, max_content_length = None, cls = None, silent = True):
    content_type, extra = parse_options_header(environ.get('CONTENT_TYPE', ''))
    try:
        content_length = int(environ['CONTENT_LENGTH'])
    except (KeyError, ValueError):
        content_length = 0

    if cls is None:
        cls = MultiDict
    if max_content_length is not None and content_length > max_content_length:
        raise RequestEntityTooLarge()
    stream = _empty_stream
    files = ()
    if content_type == 'multipart/form-data':
        try:
            form, files = parse_multipart(environ['wsgi.input'], extra.get('boundary'), content_length, stream_factory, charset, errors, max_form_memory_size=max_form_memory_size)
        except ValueError as e:
            if not silent:
                raise 
            form = cls()
        else:
            form = cls(form)

    elif content_type == 'application/x-www-form-urlencoded' or content_type == 'application/x-url-encoded':
        if max_form_memory_size is not None and content_length > max_form_memory_size:
            raise RequestEntityTooLarge()
        form = url_decode(environ['wsgi.input'].read(content_length), charset, errors=errors, cls=cls)
    else:
        form = cls()
        stream = LimitedStream(environ['wsgi.input'], content_length)
    return (stream, form, cls(files))


def _fix_ie_filename(filename):
    if filename[1:3] == ':\\' or filename[:2] == '\\\\':
        return filename.split('\\')[-1]
    return filename


def _line_parse(line):
    if line[-2:] == '\r\n':
        return (line[:-2], True)
    if line[-1:] in '\r\n':
        return (line[:-1], True)
    return (line, False)


def _find_terminator(iterator):
    for line in iterator:
        if not line:
            break
        line = line.strip()
        if line:
            return line

    return ''


def is_valid_multipart_boundary(boundary):
    return _multipart_boundary_re.match(boundary) is not None


def parse_multipart(file, boundary, content_length, stream_factory = None, charset = 'utf-8', errors = 'ignore', buffer_size = 10240, max_form_memory_size = None):
    if stream_factory is None:
        stream_factory = default_stream_factory
    if not boundary:
        raise ValueError('Missing boundary')
    if not is_valid_multipart_boundary(boundary):
        raise ValueError('Invalid boundary: %s' % boundary)
    if len(boundary) > buffer_size:
        raise ValueError('Boundary longer than buffer size')
    total_content_length = content_length
    next_part = '--' + boundary
    last_part = next_part + '--'
    form = []
    files = []
    in_memory = 0
    file = LimitedStream(file, content_length)
    iterator = chain(make_line_iter(file, buffer_size=buffer_size), _empty_string_iter)
    try:
        terminator = _find_terminator(iterator)
        if terminator != next_part:
            raise ValueError('Expected boundary at start of multipart data')
        while terminator != last_part:
            headers = parse_multipart_headers(iterator)
            disposition = headers.get('content-disposition')
            if disposition is None:
                raise ValueError('Missing Content-Disposition header')
            disposition, extra = parse_options_header(disposition)
            name = extra.get('name')
            transfer_encoding = headers.get('content-transfer-encoding')
            try_decode = transfer_encoding is not None and transfer_encoding in _supported_multipart_encodings
            filename = extra.get('filename')
            if filename is None:
                is_file = False
                container = []
                _write = container.append
                guard_memory = max_form_memory_size is not None
            else:
                content_type = headers.get('content-type')
                content_type = parse_options_header(content_type)[0] or 'text/plain'
                is_file = True
                guard_memory = False
                if filename is not None:
                    filename = _fix_ie_filename(_decode_unicode(filename, charset, errors))
                try:
                    content_length = int(headers['content-length'])
                except (KeyError, ValueError):
                    content_length = 0

                container = stream_factory(total_content_length, content_type, filename, content_length)
                _write = container.write
            buf = ''
            for line in iterator:
                if not line:
                    raise ValueError('unexpected end of stream')
                if line[:2] == '--':
                    terminator = line.rstrip()
                    if terminator in (next_part, last_part):
                        break
                if try_decode:
                    try:
                        line = line.decode(transfer_encoding)
                    except:
                        raise ValueError('could not decode transfer encoded chunk')

                if buf:
                    _write(buf)
                    buf = ''
                if line[-2:] == '\r\n':
                    buf = '\r\n'
                    cutoff = -2
                else:
                    buf = line[-1]
                    cutoff = -1
                _write(line[:cutoff])
                if guard_memory:
                    in_memory += len(line)
                    if in_memory > max_form_memory_size:
                        from werkzeug.exceptions import RequestEntityTooLarge
                        raise RequestEntityTooLarge()
            else:
                raise ValueError('unexpected end of part')

            if is_file:
                container.seek(0)
                files.append((name, FileStorage(container, filename, name, content_type, content_length, headers)))
            else:
                form.append((name, _decode_unicode(''.join(container), charset, errors)))

    finally:
        file.exhaust()

    return (form, files)


def parse_multipart_headers(iterable):
    result = []
    for line in iterable:
        line, line_terminated = _line_parse(line)
        if not line_terminated:
            raise ValueError('unexpected end of line in multipart header')
        if not line:
            break
        elif line[0] in ' \t' and result:
            key, value = result[-1]
            result[-1] = (key, value + '\n ' + line[1:])
        else:
            parts = line.split(':', 1)
            if len(parts) == 2:
                result.append((parts[0].strip(), parts[1].strip()))

    return Headers.linked(result)


from werkzeug.urls import url_decode
from werkzeug.wsgi import LimitedStream, make_line_iter
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.datastructures import Headers, FileStorage, MultiDict
from werkzeug.http import parse_options_header