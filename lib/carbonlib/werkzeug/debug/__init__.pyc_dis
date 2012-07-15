#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\debug\__init__.py
import mimetypes
from os.path import join, dirname, basename, isfile
from werkzeug.wrappers import BaseRequest as Request, BaseResponse as Response
from werkzeug.debug.repr import debug_repr
from werkzeug.debug.tbtools import get_current_traceback
from werkzeug.debug.console import Console
from werkzeug.debug.utils import render_template

class _ConsoleFrame(object):

    def __init__(self, namespace):
        self.console = Console(namespace)
        self.id = 0


class DebuggedApplication(object):
    __module__ = 'werkzeug'

    def __init__(self, app, evalex = False, request_key = 'werkzeug.request', console_path = '/console', console_init_func = None, show_hidden_frames = False):
        if not console_init_func:
            console_init_func = dict
        self.app = app
        self.evalex = evalex
        self.frames = {}
        self.tracebacks = {}
        self.request_key = request_key
        self.console_path = console_path
        self.console_init_func = console_init_func
        self.show_hidden_frames = show_hidden_frames

    def debug_application(self, environ, start_response):
        app_iter = None
        try:
            app_iter = self.app(environ, start_response)
            for item in app_iter:
                yield item

            if hasattr(app_iter, 'close'):
                app_iter.close()
        except:
            if hasattr(app_iter, 'close'):
                app_iter.close()
            traceback = get_current_traceback(skip=1, show_hidden_frames=self.show_hidden_frames, ignore_system_exceptions=True)
            for frame in traceback.frames:
                self.frames[frame.id] = frame

            self.tracebacks[traceback.id] = traceback
            try:
                start_response('500 INTERNAL SERVER ERROR', [('Content-Type', 'text/html; charset=utf-8')])
            except:
                environ['wsgi.errors'].write('Debugging middleware caught exception in streamed response at a point where response headers were already sent.\n')
            else:
                yield traceback.render_full(evalex=self.evalex).encode('utf-8', 'replace')

            traceback.log(environ['wsgi.errors'])

    def execute_command(self, request, command, frame):
        return Response(frame.console.eval(command), mimetype='text/html')

    def display_console(self, request):
        if 0 not in self.frames:
            self.frames[0] = _ConsoleFrame(self.console_init_func())
        return Response(render_template('console.html'), mimetype='text/html')

    def paste_traceback(self, request, traceback):
        paste_id = traceback.paste()
        return Response('{"url": "http://paste.pocoo.org/show/%s/", "id": %s}' % (paste_id, paste_id), mimetype='application/json')

    def get_source(self, request, frame):
        return Response(frame.render_source(), mimetype='text/html')

    def get_resource(self, request, filename):
        filename = join(dirname(__file__), 'shared', basename(filename))
        if isfile(filename):
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            f = file(filename, 'rb')
            try:
                return Response(f.read(), mimetype=mimetype)
            finally:
                f.close()

        return Response('Not Found', status=404)

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.debug_application
        if self.evalex and self.console_path is not None and request.path == self.console_path:
            response = self.display_console(request)
        elif request.path.rstrip('/').endswith('/__debugger__'):
            cmd = request.args.get('cmd')
            arg = request.args.get('f')
            traceback = self.tracebacks.get(request.args.get('tb', type=int))
            frame = self.frames.get(request.args.get('frm', type=int))
            if cmd == 'resource' and arg:
                response = self.get_resource(request, arg)
            elif cmd == 'paste' and traceback is not None:
                response = self.paste_traceback(request, traceback)
            elif cmd == 'source' and frame:
                response = self.get_source(request, frame)
            elif self.evalex and cmd is not None and frame is not None:
                response = self.execute_command(request, cmd, frame)
        return response(environ, start_response)