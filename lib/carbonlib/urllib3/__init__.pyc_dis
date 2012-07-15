#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\urllib3\__init__.py
__author__ = 'Andrey Petrov (andrey.petrov@shazow.net)'
__license__ = 'MIT'
__version__ = 'dev'
from .connectionpool import HTTPConnectionPool, HTTPSConnectionPool, connection_from_url
from . import exceptions
from .filepost import encode_multipart_formdata
from .poolmanager import PoolManager, ProxyManager, proxy_from_url
from .response import HTTPResponse
from .util import make_headers, get_host
import logging
try:
    from logging import NullHandler
except ImportError:

    class NullHandler(logging.Handler):

        def emit(self, record):
            pass


logging.getLogger(__name__).addHandler(NullHandler())
del logging
del NullHandler