#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\tutorial\tut03_get_and_post.py
import cherrypy

class WelcomePage:

    def index(self):
        return '\n            <form action="greetUser" method="GET">\n            What is your name?\n            <input type="text" name="name" />\n            <input type="submit" />\n            </form>'

    index.exposed = True

    def greetUser(self, name = None):
        if name:
            return "Hey %s, what's up?" % name
        elif name is None:
            return 'Please enter your name <a href="./">here</a>.'
        else:
            return 'No, really, enter your name <a href="./">here</a>.'

    greetUser.exposed = True


import os.path
tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    cherrypy.quickstart(WelcomePage(), config=tutconf)
else:
    cherrypy.tree.mount(WelcomePage(), config=tutconf)