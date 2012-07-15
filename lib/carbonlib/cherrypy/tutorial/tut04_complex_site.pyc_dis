#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\tutorial\tut04_complex_site.py
import cherrypy

class HomePage:

    def index(self):
        return '\n            <p>Hi, this is the home page! Check out the other\n            fun stuff on this site:</p>\n            \n            <ul>\n                <li><a href="/joke/">A silly joke</a></li>\n                <li><a href="/links/">Useful links</a></li>\n            </ul>'

    index.exposed = True


class JokePage:

    def index(self):
        return '\n            <p>"In Python, how do you create a string of random\n            characters?" -- "Read a Perl file!"</p>\n            <p>[<a href="../">Return</a>]</p>'

    index.exposed = True


class LinksPage:

    def __init__(self):
        self.extra = ExtraLinksPage()

    def index(self):
        return '\n            <p>Here are some useful links:</p>\n            \n            <ul>\n                <li><a href="http://www.cherrypy.org">The CherryPy Homepage</a></li>\n                <li><a href="http://www.python.org">The Python Homepage</a></li>\n            </ul>\n            \n            <p>You can check out some extra useful\n            links <a href="./extra/">here</a>.</p>\n            \n            <p>[<a href="../">Return</a>]</p>\n        '

    index.exposed = True


class ExtraLinksPage:

    def index(self):
        return '\n            <p>Here are some extra useful links:</p>\n            \n            <ul>\n                <li><a href="http://del.icio.us">del.icio.us</a></li>\n                <li><a href="http://www.mornography.de">Hendrik\'s weblog</a></li>\n            </ul>\n            \n            <p>[<a href="../">Return to links page</a>]</p>'

    index.exposed = True


root = HomePage()
root.joke = JokePage()
root.links = LinksPage()
import os.path
tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    cherrypy.quickstart(root, config=tutconf)
else:
    cherrypy.tree.mount(root, config=tutconf)