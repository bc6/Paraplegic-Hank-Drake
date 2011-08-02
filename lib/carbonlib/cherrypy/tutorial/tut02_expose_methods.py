import cherrypy

class HelloWorld:

    def index(self):
        return 'We have an <a href="showMessage">important message</a> for you!'


    index.exposed = True

    def showMessage(self):
        return 'Hello world!'


    showMessage.exposed = True

cherrypy.tree.mount(HelloWorld())
if __name__ == '__main__':
    import os.path
    thisdir = os.path.dirname(__file__)
    cherrypy.quickstart(config=os.path.join(thisdir, 'tutorial.conf'))

