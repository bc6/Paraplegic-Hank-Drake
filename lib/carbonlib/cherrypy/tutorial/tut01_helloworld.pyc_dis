#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\tutorial\tut01_helloworld.py
import cherrypy

class HelloWorld:

    def index(self):
        return 'Hello world!'

    index.exposed = True


import os.path
tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    cherrypy.quickstart(HelloWorld(), config=tutconf)
else:
    cherrypy.tree.mount(HelloWorld(), config=tutconf)