import os
localDir = os.path.dirname(__file__)
curpath = os.path.normpath(os.path.join(os.getcwd(), localDir))
import cherrypy

class HTTPErrorDemo(object):
    _cp_config = {'error_page.403': os.path.join(curpath, 'custom_error.html')}

    def index(self):
        tracebacks = cherrypy.request.show_tracebacks
        if tracebacks:
            trace = 'off'
        else:
            trace = 'on'
        return '\n        <html><body>\n            <h2><a href="toggleTracebacks">Toggle tracebacks %s</a></h2>\n            <p><a href="/doesNotExist">Click me; I\'m a broken link!</a></p>\n            <p><a href="/error?code=403">Use a custom an error page from a file.</a></p>\n            <p>These errors are explicitly raised by the application:</p>\n            <ul>\n                <li><a href="/error?code=400">400</a></li>\n                <li><a href="/error?code=401">401</a></li>\n                <li><a href="/error?code=402">402</a></li>\n                <li><a href="/error?code=500">500</a></li>\n            </ul>\n            <p><a href="/messageArg">You can also set the response body\n            when you raise an error.</a></p>\n        </body></html>\n        ' % trace


    index.exposed = True

    def toggleTracebacks(self):
        tracebacks = cherrypy.request.show_tracebacks
        cherrypy.config.update({'request.show_tracebacks': not tracebacks})
        raise cherrypy.HTTPRedirect('/')


    toggleTracebacks.exposed = True

    def error(self, code):
        raise cherrypy.HTTPError(status=code)


    error.exposed = True

    def messageArg(self):
        message = "If you construct an HTTPError with a 'message' argument, it wil be placed on the error page (underneath the status line by default)."
        raise cherrypy.HTTPError(500, message=message)


    messageArg.exposed = True

cherrypy.tree.mount(HTTPErrorDemo())
if __name__ == '__main__':
    import os.path
    thisdir = os.path.dirname(__file__)
    cherrypy.quickstart(config=os.path.join(thisdir, 'tutorial.conf'))

