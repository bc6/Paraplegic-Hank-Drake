#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\test\__init__.py
import sys

def newexit():
    raise SystemExit('Exit called')


def setup():
    newexit._old = sys.exit
    sys.exit = newexit


def teardown():
    try:
        sys.exit = sys.exit._old
    except AttributeError:
        sys.exit = sys._exit