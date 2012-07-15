#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/net/httpServer.py
import logging
import os
import sys
import util
import base
import blue
import cherrypy
import macho
import stacklesslib
from httpAuth import AuthController, Require
from httpApps import ServerPageHandler, PolarisController, NodeController, MapController

class StacklessServing(stacklesslib.util.local):
    request = cherrypy._cprequest.Request(cherrypy._httputil.Host('127.0.0.1', 80), cherrypy._httputil.Host('127.0.0.1', 1111))
    response = cherrypy._cprequest.Response()

    def load(self, request, response):
        self.request = request
        self.response = response

    def clear(self):
        self.__dict__.clear()


cherrypy.serving = StacklessServing()

def InitializeEspApp():
    cherrypy.sm = sm
    cherrypy.prefs = prefs
    app = cherrypy.tree.mount(ServerPageRoot(), '')
    logFolder = blue.paths.ResolvePathForWriting(u'cache:/cherryLogs')
    if not os.path.exists(logFolder):
        os.mkdir(logFolder)
    logFileName = os.path.join(logFolder, 'cherrySP_%s' % os.getpid())
    logFileHandler = logging.handlers.TimedRotatingFileHandler(logFileName, 'midnight')
    app.log.access_log.addHandler(logFileHandler)
    app.log.access_log.propagate = False
    return cherrypy.tree


class ServerPageRoot(ServerPageHandler):
    _cp_config = {'tools.staticdir.on': True,
     'tools.staticdir.dir': '/assets',
     'tools.sessions.on': True,
     'tools.auth.on': True,
     'tools.gzip.on': True,
     'tools.gzip.mime_types': ['text/html',
                               'text/plain',
                               'text/javascript',
                               'text/css'],
     'server.environment': 'production',
     'tools.sessions.debug': False,
     'tools.sessions.timeout': 120,
     'request.show_tracebacks': True,
     'request.show_mismatched_params': False}
    auth = AuthController()
    polaris = PolarisController()
    node = NodeController()
    map = MapController()
    cache = cherrypy.tools.staticdir.handler(section='/cache', dir=blue.paths.ResolvePath(u'cache:/'))

    def __init__(self):
        pass

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect('default.py')

    @cherrypy.expose
    @Require()
    def default(self, *args, **kwargs):
        return self.Handle(*args, **kwargs)


exports = {'httpServer.InitializeEspApp': InitializeEspApp}