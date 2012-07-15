#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\tutorial\tut07_sessions.py
import cherrypy

class HitCounter:
    _cp_config = {'tools.sessions.on': True}

    def index(self):
        count = cherrypy.session.get('count', 0) + 1
        cherrypy.session['count'] = count
        return "\n            During your current session, you've viewed this\n            page %s times! Your life is a patio of fun!\n        " % count

    index.exposed = True


import os.path
tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    cherrypy.quickstart(HitCounter(), config=tutconf)
else:
    cherrypy.tree.mount(HitCounter(), config=tutconf)