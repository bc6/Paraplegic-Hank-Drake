#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\lib\auth_basic.py
"""This module provides a CherryPy 3.x tool which implements
the server-side of HTTP Basic Access Authentication, as described in :rfc:`2617`.

Example usage, using the built-in checkpassword_dict function which uses a dict
as the credentials store::

    userpassdict = {'bird' : 'bebop', 'ornette' : 'wayout'}
    checkpassword = cherrypy.lib.auth_basic.checkpassword_dict(userpassdict)
    basic_auth = {'tools.auth_basic.on': True,
                  'tools.auth_basic.realm': 'earth',
                  'tools.auth_basic.checkpassword': checkpassword,
    }
    app_config = { '/' : basic_auth }

"""
__author__ = 'visteya'
__date__ = 'April 2009'
import binascii
from cherrypy._cpcompat import base64_decode
import cherrypy

def checkpassword_dict(user_password_dict):

    def checkpassword(realm, user, password):
        p = user_password_dict.get(user)
        return p and p == password or False

    return checkpassword


def basic_auth(realm, checkpassword, debug = False):
    if '"' in realm:
        raise ValueError('Realm cannot contain the " (quote) character.')
    request = cherrypy.serving.request
    auth_header = request.headers.get('authorization')
    if auth_header is not None:
        try:
            scheme, params = auth_header.split(' ', 1)
            if scheme.lower() == 'basic':
                username, password = base64_decode(params).split(':', 1)
                if checkpassword(realm, username, password):
                    if debug:
                        cherrypy.log('Auth succeeded', 'TOOLS.AUTH_BASIC')
                    request.login = username
                    return
        except (ValueError, binascii.Error):
            raise cherrypy.HTTPError(400, 'Bad Request')

    cherrypy.serving.response.headers['www-authenticate'] = 'Basic realm="%s"' % realm
    raise cherrypy.HTTPError(401, 'You are not authorized to access that resource')