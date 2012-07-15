#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/net/httpJinja.py
import cherrypy
import jinja2
from httpSettings import TEMPLATES_DIR

def CherryPyApp():
    return cherrypy.request.app


def TemplateRender(template, **kwargs):
    env = cherrypy.tools.jinja.callable.env
    context = {}
    context.update(kwargs)
    if cherrypy.request.app is not None:
        context.update({'request': cherrypy.request,
         'app_url': cherrypy.request.app.script_name})
    template = env.get_template(template)
    output = template.render(**context)
    return output


class JinjaHandler(cherrypy.dispatch.LateParamPageHandler):

    def __init__(self, env, template_name, next_handler):
        self.env = env
        self.template_name = template_name
        self.next_handler = next_handler

    def __call__(self):
        context = {}
        try:
            r = self.next_handler()
            context.update(r)
        except ValueError as e:
            cherrypy.log('%s (handler for "%s" returned "%s")' % (e, self.template_name, repr(r)), traceback=True)

        context.update({'request': cherrypy.request,
         'app_url': cherrypy.request.app.script_name})
        cherrypy.request.template = template = self.env.get_template(self.template_name)
        output = template.render(**context)
        return output


class JinjaLoader(object):

    def __init__(self):
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATES_DIR))

    def __call__(self, template):
        cherrypy.request.handler = JinjaHandler(self.env, template, cherrypy.request.handler)

    def add_filter(self, func):
        self.env.filters[func.__name__] = func
        return func

    def add_global(self, func):
        self.env.globals[func.__name__] = func
        return func


loader = JinjaLoader()
cherrypy.tools.jinja = cherrypy.Tool('before_handler', loader, priority=70)
exports = {'httpJinja.TemplateRender': TemplateRender,
 'httpJinja.CherryPyApp': CherryPyApp}