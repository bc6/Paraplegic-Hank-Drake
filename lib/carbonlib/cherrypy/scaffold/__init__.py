import cherrypy
from cherrypy import tools, url
import os
local_dir = os.path.join(os.getcwd(), os.path.dirname(__file__))

class Root:
    _cp_config = {'tools.log_tracebacks.on': True}

    def index(self):
        return "<html>\n<body>Try some <a href='%s?a=7'>other</a> path,\nor a <a href='%s?n=14'>default</a> path.<br />\nOr, just look at the pretty picture:<br />\n<img src='%s' />\n</body></html>" % (url('other'), url('else'), url('files/made_with_cherrypy_small.png'))


    index.exposed = True

    def default(self, *args, **kwargs):
        return 'args: %s kwargs: %s' % (args, kwargs)


    default.exposed = True

    def other(self, a = 2, b = 'bananas', c = None):
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        if c is None:
            return 'Have %d %s.' % (int(a), b)
        else:
            return 'Have %d %s, %s.' % (int(a), b, c)


    other.exposed = True
    files = cherrypy.tools.staticdir.handler(section='/files', dir=os.path.join(local_dir, 'static'), match='\\.(css|gif|html?|ico|jpe?g|js|png|swf|xml)$')

root = Root()

