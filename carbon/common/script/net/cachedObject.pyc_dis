#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/net/cachedObject.py
from __future__ import with_statement
import blue
import types
import weakref
import uthread
import binascii
from cStringIO import StringIO
import zlib
from timerstuff import ClockThis
import macho
import sys

class CachedObject:
    __guid__ = 'util.CachedObject'
    __passbyvalue__ = 1
    __persistvar__ = ['__objectID__',
     '__nodeID__',
     '__objectVersion__',
     '__shared__']

    def __init__(self, shared, objectID, cachedObject, objectVersion = None):
        self.__shared__ = shared
        self.__objectID__ = objectID
        self.__nodeID__ = sm.GetService('machoNet').GetNodeID()
        self.__cachedObject__ = cachedObject
        self.__compressed__ = 0
        self.__thePickle__ = None
        self.__objectVersion__ = (blue.os.GetWallclockTimeNow(), objectVersion)
        if (self.__shared__ or objectVersion is None) and macho.mode != 'client':
            self.__thePickle__ = blue.marshal.Save(cachedObject)
            if len(self.__thePickle__) > 170:
                try:
                    t = ClockThis('machoNet::util.CachedObject::compress', zlib.compress, self.__thePickle__, 1)
                except zlib.error as e:
                    raise RuntimeError('Compression Failure: ' + strx(e))

                if len(t) < len(self.__thePickle__):
                    self.__thePickle__ = t
                    self.__compressed__ = 1
            if objectVersion is None:
                self.__objectVersion__ = (self.__objectVersion__[0], binascii.crc_hqx(self.__thePickle__, macho.version + 170472))

    def __getstate__(self):
        ret = [ getattr(self, attr) for attr in self.__persistvar__ ]
        if ret[-1]:
            ret = ret[:-1]
        return tuple(ret)

    def __str__(self):
        try:
            ret = []
            for each in self.__persistvar__ + ['__thePickle__', '__compressed__']:
                if each == '__thePickle__':
                    ret.append(len(each))
                else:
                    ret.append(self.__dict__[each])

            return '<CachedObject %s>' % str(ret)
        except StandardError:
            sys.exc_clear()
            return '<CachedObject ?>'

    def __repr__(self):
        return str(self)

    def __setstate__(self, state):
        for i in xrange(len(self.__persistvar__)):
            if i >= len(state):
                if self.__persistvar__[i] == '__shared__':
                    setattr(self, self.__persistvar__[i], 1)
                else:
                    raise RuntimeError('Cached Object format version mismatch')
            else:
                setattr(self, self.__persistvar__[i], state[i])

        self.__cachedObject__ = None
        self.__thePickle__ = None
        self.__compressed__ = 0

    def __getattr__(self, key):
        if key == '__getinitargs__':
            raise AttributeError(key, "CachedObject's cannot define __getinitargs__")
        self.__UpdateCache()
        c = self.__cachedObject__
        if c is None:
            raise ReferenceError('The specified object is no longer available in cache')
        return getattr(c, key)

    def __getitem__(self, key):
        self.__UpdateCache()
        c = self.__cachedObject__
        if c is None:
            raise ReferenceError('The specified object is no longer available in cache')
        return c[key]

    def __UpdateCache(self):
        if self.__cachedObject__ is not None:
            return
        if '__semaphore__' not in self.__dict__:
            s = uthread.Semaphore(('cachedObject',
             self.__objectID__,
             self.__objectVersion__,
             self.__nodeID__))
            self.__semaphore__ = s
        with self.__semaphore__:
            if self.__cachedObject__ is None:
                self.__cachedObject__ = sm.GetService('objectCaching').GetCachableObject(self.__shared__, self.__objectID__, self.__objectVersion__, self.__nodeID__).GetObject()
        if '__semaphore__' in self.__dict__:
            if self.__semaphore__.IsCool():
                del self.__semaphore__

    def GetCachedObject(self):
        self.__UpdateCache()
        if self.__cachedObject__ is None:
            raise ReferenceError('The specified object is no longer available in cache')
        return self.__cachedObject__

    def GetObjectID(self):
        return self.__objectID__

    def MachoGetCachedObjectGuts(self):
        return (self.__shared__,
         self.__objectID__,
         self.__objectVersion__,
         self.__nodeID__,
         self.__cachedObject__,
         self.__thePickle__,
         self.__compressed__)