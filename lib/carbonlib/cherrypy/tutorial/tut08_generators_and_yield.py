import cherrypy

class GeneratorDemo:

    def header(self):
        return '<html><body><h2>Generators rule!</h2>'



    def footer(self):
        return '</body></html>'



    def index(self):
        users = ['Remi',
         'Carlos',
         'Hendrik',
         'Lorenzo Lamas']
        yield self.header()
        yield '<h3>List of users:</h3>'
        for user in users:
            yield '%s<br/>' % user

        yield self.footer()


    index.exposed = True

cherrypy.tree.mount(GeneratorDemo())
if __name__ == '__main__':
    import os.path
    thisdir = os.path.dirname(__file__)
    cherrypy.quickstart(config=os.path.join(thisdir, 'tutorial.conf'))

