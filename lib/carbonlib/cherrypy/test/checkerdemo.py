import os
import cherrypy
thisdir = os.path.dirname(os.path.abspath(__file__))

class Root:
    pass
if __name__ == '__main__':
    conf = {'/base': {'tools.staticdir.root': thisdir,
               'throw_errors': True},
     '/base/static': {'tools.staticdir.on': True,
                      'tools.staticdir.dir': 'static'},
     '/base/js': {'tools.staticdir.on': True,
                  'tools.staticdir.dir': 'js'},
     '/base/static2': {'tools.staticdir.on': True,
                       'tools.staticdir.dir': '/static'},
     '/static3': {'tools.staticdir.on': True,
                  'tools.staticdir.dir': 'static'},
     '/unknown': {'toobles.gzip.on': True},
     '/cpknown': {'cherrypy.tools.encode.on': True},
     '/conftype': {'request.show_tracebacks': 14},
     '/web': {'tools.unknown.on': True},
     '/app1': {'server.socket_host': '0.0.0.0'},
     'global': {'server.socket_host': 'localhost'},
     '[/extra_brackets]': {}}
    cherrypy.quickstart(Root(), config=conf)

