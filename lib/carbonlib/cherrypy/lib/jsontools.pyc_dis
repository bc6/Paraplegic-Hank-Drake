#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\lib\jsontools.py
import sys
import cherrypy
from cherrypy._cpcompat import basestring, ntou, json, json_encode, json_decode

def json_processor(entity):
    if not entity.headers.get(ntou('Content-Length'), ntou('')):
        raise cherrypy.HTTPError(411)
    body = entity.fp.read()
    try:
        cherrypy.serving.request.json = json_decode(body.decode('utf-8'))
    except ValueError:
        raise cherrypy.HTTPError(400, 'Invalid JSON document')


def json_in(content_type = [ntou('application/json'), ntou('text/javascript')], force = True, debug = False, processor = json_processor):
    request = cherrypy.serving.request
    if isinstance(content_type, basestring):
        content_type = [content_type]
    if force:
        if debug:
            cherrypy.log('Removing body processors %s' % repr(request.body.processors.keys()), 'TOOLS.JSON_IN')
        request.body.processors.clear()
        request.body.default_proc = cherrypy.HTTPError(415, 'Expected an entity of content type %s' % ', '.join(content_type))
    for ct in content_type:
        if debug:
            cherrypy.log('Adding body processor for %s' % ct, 'TOOLS.JSON_IN')
        request.body.processors[ct] = processor


def json_handler(*args, **kwargs):
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
    return json_encode(value)


def json_out(content_type = 'application/json', debug = False, handler = json_handler):
    request = cherrypy.serving.request
    if debug:
        cherrypy.log('Replacing %s with JSON handler' % request.handler, 'TOOLS.JSON_OUT')
    request._json_inner_handler = request.handler
    request.handler = handler
    if content_type is not None:
        if debug:
            cherrypy.log('Setting Content-Type to %s' % ct, 'TOOLS.JSON_OUT')
        cherrypy.serving.response.headers['Content-Type'] = content_type