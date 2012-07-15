#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\test\sessiondemo.py
import calendar
from datetime import datetime
import sys
import cherrypy
from cherrypy.lib import sessions
from cherrypy._cpcompat import copyitems
page = '\n<html>\n<head>\n<style type=\'text/css\'>\ntable { border-collapse: collapse; border: 1px solid #663333; }\nth { text-align: right; background-color: #663333; color: white; padding: 0.5em; }\ntd { white-space: pre-wrap; font-family: monospace; padding: 0.5em; \n     border: 1px solid #663333; }\n.warn { font-family: serif; color: #990000; }\n</style>\n<script type="text/javascript">\n<!--\nfunction twodigit(d) { return d < 10 ? "0" + d : d; }\nfunction formattime(t) {\n    var month = t.getUTCMonth() + 1;\n    var day = t.getUTCDate();\n    var year = t.getUTCFullYear();\n    var hours = t.getUTCHours();\n    var minutes = t.getUTCMinutes();\n    return (year + "/" + twodigit(month) + "/" + twodigit(day) + " " +\n            hours + ":" + twodigit(minutes) + " UTC");\n}\n\nfunction interval(s) {\n    // Return the given interval (in seconds) as an English phrase\n    var seconds = s %% 60;\n    s = Math.floor(s / 60);\n    var minutes = s %% 60;\n    s = Math.floor(s / 60);\n    var hours = s %% 24;\n    var v = twodigit(hours) + ":" + twodigit(minutes) + ":" + twodigit(seconds);\n    var days = Math.floor(s / 24);\n    if (days != 0) v = days + \' days, \' + v;\n    return v;\n}\n\nvar fudge_seconds = 5;\n\nfunction init() {\n    // Set the content of the \'btime\' cell.\n    var currentTime = new Date();\n    var bunixtime = Math.floor(currentTime.getTime() / 1000);\n    \n    var v = formattime(currentTime);\n    v += " (Unix time: " + bunixtime + ")";\n    \n    var diff = Math.abs(%(serverunixtime)s - bunixtime);\n    if (diff > fudge_seconds) v += "<p class=\'warn\'>Browser and Server times disagree.</p>";\n    \n    document.getElementById(\'btime\').innerHTML = v;\n    \n    // Warn if response cookie expires is not close to one hour in the future.\n    // Yes, we want this to happen when wit hit the \'Expire\' link, too.\n    var expires = Date.parse("%(expires)s") / 1000;\n    var onehour = (60 * 60);\n    if (Math.abs(expires - (bunixtime + onehour)) > fudge_seconds) {\n        diff = Math.floor(expires - bunixtime);\n        if (expires > (bunixtime + onehour)) {\n            var msg = "Response cookie \'expires\' date is " + interval(diff) + " in the future.";\n        } else {\n            var msg = "Response cookie \'expires\' date is " + interval(0 - diff) + " in the past.";\n        }\n        document.getElementById(\'respcookiewarn\').innerHTML = msg;\n    }\n}\n//-->\n</script>\n</head>\n\n<body onload=\'init()\'>\n<h2>Session Demo</h2>\n<p>Reload this page. The session ID should not change from one reload to the next</p>\n<p><a href=\'../\'>Index</a> | <a href=\'expire\'>Expire</a> | <a href=\'regen\'>Regenerate</a></p>\n<table>\n    <tr><th>Session ID:</th><td>%(sessionid)s<p class=\'warn\'>%(changemsg)s</p></td></tr>\n    <tr><th>Request Cookie</th><td>%(reqcookie)s</td></tr>\n    <tr><th>Response Cookie</th><td>%(respcookie)s<p id=\'respcookiewarn\' class=\'warn\'></p></td></tr>\n    <tr><th>Session Data</th><td>%(sessiondata)s</td></tr>\n    <tr><th>Server Time</th><td id=\'stime\'>%(servertime)s (Unix time: %(serverunixtime)s)</td></tr>\n    <tr><th>Browser Time</th><td id=\'btime\'>&nbsp;</td></tr>\n    <tr><th>Cherrypy Version:</th><td>%(cpversion)s</td></tr>\n    <tr><th>Python Version:</th><td>%(pyversion)s</td></tr>\n</table>\n</body></html>\n'

class Root(object):

    def page(self):
        changemsg = []
        if cherrypy.session.id != cherrypy.session.originalid:
            if cherrypy.session.originalid is None:
                changemsg.append('Created new session because no session id was given.')
            if cherrypy.session.missing:
                changemsg.append('Created new session due to missing (expired or malicious) session.')
            if cherrypy.session.regenerated:
                changemsg.append('Application generated a new session.')
        try:
            expires = cherrypy.response.cookie['session_id']['expires']
        except KeyError:
            expires = ''

        return page % {'sessionid': cherrypy.session.id,
         'changemsg': '<br>'.join(changemsg),
         'respcookie': cherrypy.response.cookie.output(),
         'reqcookie': cherrypy.request.cookie.output(),
         'sessiondata': copyitems(cherrypy.session),
         'servertime': datetime.utcnow().strftime('%Y/%m/%d %H:%M') + ' UTC',
         'serverunixtime': calendar.timegm(datetime.utcnow().timetuple()),
         'cpversion': cherrypy.__version__,
         'pyversion': sys.version,
         'expires': expires}

    def index(self):
        cherrypy.session['color'] = 'green'
        return self.page()

    index.exposed = True

    def expire(self):
        sessions.expire()
        return self.page()

    expire.exposed = True

    def regen(self):
        cherrypy.session.regenerate()
        cherrypy.session['color'] = 'yellow'
        return self.page()

    regen.exposed = True


if __name__ == '__main__':
    cherrypy.config.update({'log.screen': True,
     'tools.sessions.on': True})
    cherrypy.quickstart(Root())