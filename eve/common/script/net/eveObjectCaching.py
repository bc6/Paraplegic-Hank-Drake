import blue
import uthread
import types
import util
import zlib
import copy
from timerstuff import ClockThis
import macho
import random
import sys
import service
import base
import binascii
import log
import os
import objectCaching
import svc
globals().update(service.consts)

class EveObjectCachingSvc(svc.objectCaching):
    __guid__ = 'svc.eveObjectCaching'
    __replaceservice__ = 'objectCaching'
    __cachedsessionvariables__ = ['regionid',
     'constellationid',
     'stationid',
     'solarsystemid',
     'locationid',
     'languageID']


