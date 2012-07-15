#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/net/http.py
from jinja2 import escape
import cherrypy
import macho

def SaveString(s):
    return u''.join([u'<div class="save-string">', unicode(s).encode('unicode_escape'), '</div>'])


def Escape(s):
    return escape(s)


def GetCookie(key):
    cookie = cherrypy.request.cookie
    if key in cookie:
        return cookie[key]


def SetCookie(key, value, path = '/', maxAge = 3600, version = 1):
    cookie = cherrypy.response.cookie
    cookie[key] = value
    cookie[key]['path'] = path
    cookie[key]['max-age'] = maxAge
    cookie[key]['version'] = version


def SetSessionData(key, value):
    if str(key).lower() == 'machosession':
        raise ValueError("The keyword 'machoSession' is reserved!")
    cherrypy.session[key] = value


def GetSessionData(key):
    return cherrypy.session.get(key)


def Session():
    return cherrypy.session


def SPSession():
    return cherrypy.session['machoSession']


def SetSPSessionContents(key, value):
    SPSession().esps.contents[key] = value


def SPSessionServer():
    return SPSessionContents('server')


def SPSessionUsername():
    return SPSessionContents('username')


def SPSessionContents(key):
    return SPSession().esps.contents[key]


def Referer():
    request = cherrypy.request
    return request.headers.get('Referer', '')


def Host():
    request = cherrypy.request
    host = request.headers.get('X-Forwarded-Host', '')
    if not host:
        host = request.headers.get('Host', '')
    return host


def RemoteAddress():
    return ''


def AddHeader(headerKey, headerValue):
    response = cherrypy.response
    response.headers[headerKey] = headerValue


def ESPUrl(session, polarisID = None):
    if macho.mode == 'proxy':
        if polarisID is None:
            polarisID = session.ConnectToSolServerService('DB2').CallProc('zcluster.Nodes_PolarisID')
    elif polarisID is None:
        polarisID = sm.GetService('DB2').CallProc('zcluster.Nodes_PolarisID')
    if cherrypy.request.app is None:
        if sm.IsServiceRunning('tcpRawProxyService'):
            tcpproxy = sm.services['tcpRawProxyService']
        else:
            proxyID = sm.services['machoNet'].GetConnectedProxyNodes()[0]
            tcpproxy = sm.StartService('debug').session.ConnectToRemoteService('tcpRawProxyService', proxyID)
        host, ports = tcpproxy.GetESPTunnelingAddressByNodeID()
        port = ports.get(polarisID)
        return 'http://%s:%s' % (host, port)
    machoNetSvc = session.ConnectToProxyServerService('machoNet', polarisID)
    transport_key = 'tcp:raw:http2' if prefs.GetValue('httpServerMode', 'ccp').lower() == 'ccp' else 'tcp:raw:http'
    host, port = machoNetSvc.GetConnectionProperties()['internaladdress'].split(':')
    refHost = Host().split(':')[0]
    if refHost == 'localhost':
        host = refHost
    sub_number = 1 if cherrypy.request.app else 2
    port = int(port) + macho.offsetMap[macho.mode][transport_key] - sub_number
    return 'http://%s:%s' % (host, port)


exports = {'http.SaveString': SaveString,
 'http.Escape': Escape,
 'http.GetCookie': GetCookie,
 'http.SetCookie': SetCookie,
 'http.SetSessionData': SetSessionData,
 'http.GetSessionData': GetSessionData,
 'http.Session': Session,
 'http.SPSession': SPSession,
 'http.Referer': Referer,
 'http.Host': Host,
 'http.RemoteAddress': RemoteAddress,
 'http.AddHeader': AddHeader,
 'http.ESPUrl': ESPUrl}