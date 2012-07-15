#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\lib\static.py
import logging
import mimetypes
mimetypes.init()
mimetypes.types_map['.dwg'] = 'image/x-dwg'
mimetypes.types_map['.ico'] = 'image/x-icon'
mimetypes.types_map['.bz2'] = 'application/x-bzip2'
mimetypes.types_map['.gz'] = 'application/x-gzip'
import os
import re
import stat
import time
import cherrypy
from cherrypy._cpcompat import ntob, unquote
from cherrypy.lib import cptools, httputil, file_generator_limited

def serve_file(path, content_type = None, disposition = None, name = None, debug = False):
    response = cherrypy.serving.response
    if not os.path.isabs(path):
        msg = "'%s' is not an absolute path." % path
        if debug:
            cherrypy.log(msg, 'TOOLS.STATICFILE')
        raise ValueError(msg)
    try:
        st = os.stat(path)
    except OSError:
        if debug:
            cherrypy.log('os.stat(%r) failed' % path, 'TOOLS.STATIC')
        raise cherrypy.NotFound()

    if stat.S_ISDIR(st.st_mode):
        if debug:
            cherrypy.log('%r is a directory' % path, 'TOOLS.STATIC')
        raise cherrypy.NotFound()
    response.headers['Last-Modified'] = httputil.HTTPDate(st.st_mtime)
    cptools.validate_since()
    if content_type is None:
        ext = ''
        i = path.rfind('.')
        if i != -1:
            ext = path[i:].lower()
        content_type = mimetypes.types_map.get(ext, None)
    if content_type is not None:
        response.headers['Content-Type'] = content_type
    if debug:
        cherrypy.log('Content-Type: %r' % content_type, 'TOOLS.STATIC')
    cd = None
    if disposition is not None:
        if name is None:
            name = os.path.basename(path)
        cd = '%s; filename="%s"' % (disposition, name)
        response.headers['Content-Disposition'] = cd
    if debug:
        cherrypy.log('Content-Disposition: %r' % cd, 'TOOLS.STATIC')
    content_length = st.st_size
    fileobj = open(path, 'rb')
    return _serve_fileobj(fileobj, content_type, content_length, debug=debug)


def serve_fileobj(fileobj, content_type = None, disposition = None, name = None, debug = False):
    response = cherrypy.serving.response
    try:
        st = os.fstat(fileobj.fileno())
    except AttributeError:
        if debug:
            cherrypy.log('os has no fstat attribute', 'TOOLS.STATIC')
        content_length = None
    else:
        response.headers['Last-Modified'] = httputil.HTTPDate(st.st_mtime)
        cptools.validate_since()
        content_length = st.st_size

    if content_type is not None:
        response.headers['Content-Type'] = content_type
    if debug:
        cherrypy.log('Content-Type: %r' % content_type, 'TOOLS.STATIC')
    cd = None
    if disposition is not None:
        if name is None:
            cd = disposition
        else:
            cd = '%s; filename="%s"' % (disposition, name)
        response.headers['Content-Disposition'] = cd
    if debug:
        cherrypy.log('Content-Disposition: %r' % cd, 'TOOLS.STATIC')
    return _serve_fileobj(fileobj, content_type, content_length, debug=debug)


def _serve_fileobj(fileobj, content_type, content_length, debug = False):
    response = cherrypy.serving.response
    request = cherrypy.serving.request
    if request.protocol >= (1, 1):
        response.headers['Accept-Ranges'] = 'bytes'
        r = httputil.get_ranges(request.headers.get('Range'), content_length)
        if r == []:
            response.headers['Content-Range'] = 'bytes */%s' % content_length
            message = 'Invalid Range (first-byte-pos greater than Content-Length)'
            if debug:
                cherrypy.log(message, 'TOOLS.STATIC')
            raise cherrypy.HTTPError(416, message)
        if r:
            if len(r) == 1:
                start, stop = r[0]
                if stop > content_length:
                    stop = content_length
                r_len = stop - start
                if debug:
                    cherrypy.log('Single part; start: %r, stop: %r' % (start, stop), 'TOOLS.STATIC')
                response.status = '206 Partial Content'
                response.headers['Content-Range'] = 'bytes %s-%s/%s' % (start, stop - 1, content_length)
                response.headers['Content-Length'] = r_len
                fileobj.seek(start)
                response.body = file_generator_limited(fileobj, r_len)
            else:
                response.status = '206 Partial Content'
                from mimetools import choose_boundary
                boundary = choose_boundary()
                ct = 'multipart/byteranges; boundary=%s' % boundary
                response.headers['Content-Type'] = ct
                if 'Content-Length' in response.headers:
                    del response.headers['Content-Length']

                def file_ranges():
                    yield ntob('\r\n')
                    for start, stop in r:
                        if debug:
                            cherrypy.log('Multipart; start: %r, stop: %r' % (start, stop), 'TOOLS.STATIC')
                        yield ntob('--' + boundary, 'ascii')
                        yield ntob('\r\nContent-type: %s' % content_type, 'ascii')
                        yield ntob('\r\nContent-range: bytes %s-%s/%s\r\n\r\n' % (start, stop - 1, content_length), 'ascii')
                        fileobj.seek(start)
                        for chunk in file_generator_limited(fileobj, stop - start):
                            yield chunk

                        yield ntob('\r\n')

                    yield ntob('--' + boundary + '--', 'ascii')
                    yield ntob('\r\n')

                response.body = file_ranges()
            return response.body
        if debug:
            cherrypy.log('No byteranges requested', 'TOOLS.STATIC')
    response.headers['Content-Length'] = content_length
    response.body = fileobj
    return response.body


def serve_download(path, name = None):
    return serve_file(path, 'application/x-download', 'attachment', name)


def _attempt(filename, content_types, debug = False):
    if debug:
        cherrypy.log('Attempting %r (content_types %r)' % (filename, content_types), 'TOOLS.STATICDIR')
    try:
        content_type = None
        if content_types:
            r, ext = os.path.splitext(filename)
            content_type = content_types.get(ext[1:], None)
        serve_file(filename, content_type=content_type, debug=debug)
        return True
    except cherrypy.NotFound:
        if debug:
            cherrypy.log('NotFound', 'TOOLS.STATICFILE')
        return False


def staticdir(section, dir, root = '', match = '', content_types = None, index = '', debug = False):
    request = cherrypy.serving.request
    if request.method not in ('GET', 'HEAD'):
        if debug:
            cherrypy.log('request.method not GET or HEAD', 'TOOLS.STATICDIR')
        return False
    if match and not re.search(match, request.path_info):
        if debug:
            cherrypy.log('request.path_info %r does not match pattern %r' % (request.path_info, match), 'TOOLS.STATICDIR')
        return False
    dir = os.path.expanduser(dir)
    if not os.path.isabs(dir):
        if not root:
            msg = 'Static dir requires an absolute dir (or root).'
            if debug:
                cherrypy.log(msg, 'TOOLS.STATICDIR')
            raise ValueError(msg)
        dir = os.path.join(root, dir)
    if section == 'global':
        section = '/'
    section = section.rstrip('\\/')
    branch = request.path_info[len(section) + 1:]
    branch = unquote(branch.lstrip('\\/'))
    filename = os.path.join(dir, branch)
    if debug:
        cherrypy.log('Checking file %r to fulfill %r' % (filename, request.path_info), 'TOOLS.STATICDIR')
    if not os.path.normpath(filename).startswith(os.path.normpath(dir)):
        raise cherrypy.HTTPError(403)
    handled = _attempt(filename, content_types)
    if not handled:
        if index:
            handled = _attempt(os.path.join(filename, index), content_types)
            if handled:
                request.is_index = filename[-1] in '\\/'
    return handled


def staticfile(filename, root = None, match = '', content_types = None, debug = False):
    request = cherrypy.serving.request
    if request.method not in ('GET', 'HEAD'):
        if debug:
            cherrypy.log('request.method not GET or HEAD', 'TOOLS.STATICFILE')
        return False
    if match and not re.search(match, request.path_info):
        if debug:
            cherrypy.log('request.path_info %r does not match pattern %r' % (request.path_info, match), 'TOOLS.STATICFILE')
        return False
    if not os.path.isabs(filename):
        if not root:
            msg = "Static tool requires an absolute filename (got '%s')." % filename
            if debug:
                cherrypy.log(msg, 'TOOLS.STATICFILE')
            raise ValueError(msg)
        filename = os.path.join(root, filename)
    return _attempt(filename, content_types, debug=debug)