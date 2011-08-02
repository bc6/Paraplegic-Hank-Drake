import cherrypy

class Page:
    title = 'Untitled Page'

    def header(self):
        return '\n            <html>\n            <head>\n                <title>%s</title>\n            <head>\n            <body>\n            <h2>%s</h2>\n        ' % (self.title, self.title)



    def footer(self):
        return '\n            </body>\n            </html>\n        '




class HomePage(Page):
    title = 'Tutorial 5'

    def __init__(self):
        self.another = AnotherPage()



    def index(self):
        return self.header() + '\n            <p>\n            Isn\'t this exciting? There\'s\n            <a href="./another/">another page</a>, too!\n            </p>\n        ' + self.footer()


    index.exposed = True


class AnotherPage(Page):
    title = 'Another Page'

    def index(self):
        return self.header() + '\n            <p>\n            And this is the amazing second page!\n            </p>\n        ' + self.footer()


    index.exposed = True

cherrypy.tree.mount(HomePage())
if __name__ == '__main__':
    import os.path
    thisdir = os.path.dirname(__file__)
    cherrypy.quickstart(config=os.path.join(thisdir, 'tutorial.conf'))

