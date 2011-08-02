import sys
import cherrypy

def process_body():
    try:
        import xmlrpclib
        return xmlrpclib.loads(cherrypy.request.body.read())
    except Exception:
        return (('ERROR PARAMS',), 'ERRORMETHOD')



def patched_path(path):
    if not path.endswith('/'):
        path += '/'
    if path.startswith('/RPC2/'):
        path = path[5:]
    return path



def _set_response(body):
    response = cherrypy.response
    response.status = '200 OK'
    response.body = body
    response.headers['Content-Type'] = 'text/xml'
    response.headers['Content-Length'] = len(body)



def respond(body, encoding = 'utf-8', allow_none = 0):
    from xmlrpclib import Fault, dumps
    if not isinstance(body, Fault):
        body = (body,)
    _set_response(dumps(body, methodresponse=1, encoding=encoding, allow_none=allow_none))



def on_error(*args, **kwargs):
    body = str(sys.exc_info()[1])
    from xmlrpclib import Fault, dumps
    _set_response(dumps(Fault(1, body)))



