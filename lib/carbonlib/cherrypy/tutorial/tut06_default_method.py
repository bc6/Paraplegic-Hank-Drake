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

cherrypy.tree.mount(UsersPage())
if __name__ == '__main__':
    import os.path
    thisdir = os.path.dirname(__file__)
    cherrypy.quickstart(config=os.path.join(thisdir, 'tutorial.conf'))

