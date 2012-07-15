#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/net/objectCachingUtils.py
import blue
import util
import zlib
from timerstuff import ClockThis
import macho
import sys
import service
import os
globals().update(service.consts)

class CachedObject:
    __guid__ = 'objectCaching.CachedObject'
    __passbyvalue__ = 1

    def __init__(self, s, oid, v, n, o, p, c):
        self.version, self.object, self.nodeID, self.shared, self.pickle, self.compressed, self.objectID = (v,
         o,
         n,
         s,
         p,
         c,
         oid)

    def __getstate__(self):
        if self.pickle is not None:
            o = None
        else:
            o = self.object
        return (self.version,
         o,
         self.nodeID,
         self.shared,
         self.pickle,
         self.compressed,
         self.objectID)

    def __str__(self):
        try:
            return 'objectCaching.CachedObject(objectID=%s, version=%s, nodeID=%s, shared=%s, compressed=%s)' % (self.objectID,
             self.version,
             self.nodeID,
             self.shared,
             self.compressed)
        except:
            sys.exc_clear()
            return 'objectCaching.CachedObject(???)'

    def __setstate__(self, state):
        self.object = None
        self.version, self.object, self.nodeID, self.shared, self.pickle, self.compressed, self.objectID = state

    def GetObject(self):
        if self.object is None:
            if self.pickle is None:
                raise RuntimeError('Getting cached object contents, but both the object and the pickle are none')
            try:
                if self.compressed:
                    try:
                        dasPickle = zlib.decompress(self.pickle)
                    except zlib.error as e:
                        raise RuntimeError('Decompression Failure: ' + strx(e))

                    self.object = blue.marshal.Load(dasPickle)
                else:
                    self.object = blue.marshal.Load(self.pickle)
            except:
                sm.GetService('objectCaching').LogError('Failed to acquire object from objectCaching.CachedObject, self=', self)
                raise 

        return self.object

    def CompressedPart(self):
        if not self.compressed or self.pickle is None:
            return 0
        return len(self.pickle)

    def GetSize(self):
        if self.pickle is None:
            self.pickle = blue.marshal.Save(self.object)
        return len(self.pickle)


class CachedMethodCallResult:
    __guid__ = 'objectCaching.CachedMethodCallResult'
    __passbyvalue__ = 1

    def __init__(self, key, details, result):
        self.details = details
        if isinstance(result, util.CachedObject):
            self.result = result
            self.version = None
        elif sm.services['objectCaching'].IsCachedOnProxy(details) and macho.mode != 'client':
            self.result = util.CachedObject(1, ('Method Call', macho.mode, key), result)
            sm.services['objectCaching'].CacheObject(self.result)
            self.version = None
        else:
            self.result = blue.marshal.Save(result)
            self.version = [blue.os.GetWallclockTime(), zlib.adler32(self.result)]

    def __getstate__(self):
        return (self.details, self.result, self.version)

    def __setstate__(self, state):
        self.details, self.result, self.version = state

    def GetVersion(self):
        if isinstance(self.result, util.CachedObject):
            return list(self.result.__objectVersion__)
        return self.version

    def IsSameVersion(self, machoVersion):
        if machoVersion != 1:
            return self.GetVersion()[1] == machoVersion[1]
        return 0

    def GetResult(self):
        if isinstance(self.result, util.CachedObject):
            return self.result.GetCachedObject()
        else:
            return blue.marshal.Load(self.result)

    def __str__(self):
        try:
            if isinstance(self.result, util.CachedObject):
                return 'objectCaching.CachedMethodCallResult(version=%s, result=%s)' % (self.version, self.result)
            return 'objectCaching.CachedMethodCallResult(version=%s)' % (self.version,)
        except:
            sys.exc_clear()
            return 'objectCaching.CachedMethodCallResult(???)'


class CacheOK(StandardError):
    __guid__ = 'objectCaching.CacheOK'
    __passbyvalue__ = 1

    def __init__(self, value = 'CacheOK', *args):
        StandardError.__init__(self, value, *args)