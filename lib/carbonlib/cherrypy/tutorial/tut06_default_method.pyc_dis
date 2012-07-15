#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\tutorial\tut06_default_method.py
import cherrypy

class UsersPage:

    def index(self):
        return '\n            <a href="./remi">Remi Delon</a><br/>\n            <a href="./hendrik">Hendrik Mans</a><br/>\n            <a href="./lorenzo">Lorenzo Lamas</a><br/>\n        '

    index.exposed = True

    def default(self, user):
        if user == 'remi':
            out = 'Remi Delon, CherryPy lead developer'
        elif user == 'hendrik':
            out = 'Hendrik Mans, CherryPy co-developer & crazy German'
        elif user == 'lorenzo':
            out = 'Lorenzo Lamas, famous actor and singer!'
        else:
            out = 'Unknown user. :-('
        return '%s (<a href="./">back</a>)' % out

    default.exposed = True


import os.path
tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    cherrypy.quickstart(UsersPage(), config=tutconf)
else:
    cherrypy.tree.mount(UsersPage(), config=tutconf)