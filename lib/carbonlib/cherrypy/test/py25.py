from cherrypy import expose, tools

class ExposeExamples(object):

    @expose
    def no_call(self):
        return 'Mr E. R. Bradshaw'



    @expose()
    def call_empty(self):
        return 'Mrs. B.J. Smegma'



    @expose('call_alias')
    def nesbitt(self):
        return 'Mr Nesbitt'



    @expose(['alias1', 'alias2'])
    def andrews(self):
        return 'Mr Ken Andrews'



    @expose(alias='alias3')
    def watson(self):
        return 'Mr. and Mrs. Watson'




class ToolExamples(object):

    @expose
    @tools.response_headers(headers=[('Content-Type', 'application/data')])
    def blah(self):
        yield 'blah'


    blah._cp_config['response.stream'] = True


