#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\contrib\kickstart.py
from os import path
from werkzeug.wrappers import Request as RequestBase, Response as ResponseBase
from werkzeug.templates import Template
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RequestRedirect
__all__ = ['Request',
 'Response',
 'TemplateNotFound',
 'TemplateLoader',
 'GenshiTemplateLoader',
 'Application']

class Request(RequestBase):

    def __init__(self, environ, url_map, session_store = None, cookie_name = None):
        RequestBase.__init__(self, environ)
        self.url_adapter = url_map.bind_to_environ(environ)
        self.session_store = session_store
        self.cookie_name = cookie_name
        if session_store is not None and cookie_name is not None:
            if cookie_name in self.cookies:
                self.session = session_store.get(self.cookies[cookie_name])
            else:
                self.session = session_store.new()

    def url_for(self, callback, **values):
        return self.url_adapter.build(callback, values)


class Response(ResponseBase):
    default_mimetype = 'text/html'

    def __call__(self, environ, start_response):
        request = environ['werkzeug.request']
        if request.session_store is not None:
            request.session_store.save_if_modified(request.session)
            if request.cookie_name not in request.cookies:
                self.set_cookie(request.cookie_name, request.session.sid)
        return ResponseBase.__call__(self, environ, start_response)


class Processor(object):

    def process_request(self, request):
        return request

    def process_response(self, request, response):
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        return None

    def process_exception(self, request, exception):
        return None


class Application(object):

    def __init__(self, name, url_map, session = False, processors = None):
        self.name = name
        self.url_map = url_map
        self.processors = processors or []
        if session:
            self.store = session
        else:
            self.store = None

    def __call__(self, environ, start_response):
        if self.store is not None:
            request = Request(environ, self.url_map, session_store=self.store, cookie_name='%s_sid' % self.name)
        else:
            request = Request(environ, self.url_map)
        for processor in self.processors:
            request = processor.process_request(request)

        try:
            callback, args = request.url_adapter.match(request.path)
        except (HTTPException, RequestRedirect) as e:
            response = e
        else:
            for processor in self.processors:
                action = processor.process_view(request, callback, (), args)
                if action is not None:
                    return action(environ, start_response)

            try:
                response = callback(request, **args)
            except Exception as exception:
                for processor in reversed(self.processors):
                    action = processor.process_exception(request, exception)
                    if action is not None:
                        return action(environ, start_response)

                raise 

        for processor in reversed(self.processors):
            response = processor.process_response(request, response)

        return response(environ, start_response)

    def config_session(self, store, expiration = 'session'):
        self.store = store


class TemplateNotFound(IOError, LookupError):

    def __init__(self, name):
        IOError.__init__(self, name)
        self.name = name


class TemplateLoader(object):

    def __init__(self, search_path, encoding = 'utf-8'):
        self.search_path = path.abspath(search_path)
        self.encoding = encoding

    def get_template(self, name):
        filename = path.join(self.search_path, *[ p for p in name.split('/') if p and p[0] != '.' ])
        if not path.exists(filename):
            raise TemplateNotFound(name)
        return Template.from_file(filename, self.encoding)

    def render_to_response(self, *args, **kwargs):
        return Response(self.render_to_string(*args, **kwargs))

    def render_to_string(self, *args, **kwargs):
        try:
            template_name, args = args[0], args[1:]
        except IndexError:
            raise TypeError('name of template required')

        return self.get_template(template_name).render(*args, **kwargs)


class GenshiTemplateLoader(TemplateLoader):

    def __init__(self, search_path, encoding = 'utf-8', **kwargs):
        TemplateLoader.__init__(self, search_path, encoding)
        from genshi.template import TemplateLoader as GenshiLoader
        from genshi.template.loader import TemplateNotFound
        self.not_found_exception = TemplateNotFound
        reload_template = kwargs.pop('auto_reload', True)
        kwargs.pop('default_encoding', None)
        self.loader = GenshiLoader(search_path, default_encoding=encoding, auto_reload=reload_template, **kwargs)
        self.output_type = 'html'
        self.encoding = encoding

    def get_template(self, template_name):
        try:
            return self.loader.load(template_name, encoding=self.encoding)
        except self.not_found_exception as e:
            raise TemplateNotFound(template_name)

    def render_to_string(self, template_name, context = None):
        context = context or {}
        tmpl = self.get_template(template_name)
        return tmpl.generate(**context).render(self.output_type, encoding=None)