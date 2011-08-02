import cherrypy

class WelcomePage:

    def index(self):
        return '\n            <form action="greetUser" method="GET">\n            What is your name?\n            <input type="text" name="name" />\n            <input type="submit" />\n            </form>'


    index.exposed = True

    def greetUser(self, name = None):
        if name:
            return "Hey %s, what's up?" % name
        else:
            if name is None:
                return 'Please enter your name <a href="./">here</a>.'
            return 'No, really, enter your name <a href="./">here</a>.'


    greetUser.exposed = True

cherrypy.tree.mount(WelcomePage())
if __name__ == '__main__':
    import os.path
    thisdir = os.path.dirname(__file__)
    cherrypy.quickstart(config=os.path.join(thisdir, 'tutorial.conf'))

