#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/util/godmarowset.py
import dbutil
import util
import blue
import types
import log
from timerstuff import ClockThis
from service import *
DEBUG = True

def rowsetIterator(rowset):
    if isinstance(rowset, (GodmaIndexedRowset, GodmaFilterRowset)):
        for key in rowset.iterkeys():
            yield rowset.__getitem__(key)

    elif isinstance(rowset, (util.GodmaRowset,)):
        for i in xrange(len(rowset)):
            yield rowset.__getitem__(i)

    else:
        raise NotImplementedError('Yikes, what are you? rowsetIterator does not operate on %s (%s)' % (str(type(rowset)), str(rowset.__class__)))
    raise StopIteration


class GodmaRowset(dbutil.CRowset):
    __guid__ = 'util.GodmaRowset'
    __passbyvalue__ = 1

    def __init__(self, header, rows, rowClass = blue.DBRow):
        dbutil.CRowset.__init__(self, header, rows)
        self.rowClass = rowClass

    def __getitem__(self, index):
        ret = dbutil.CRowset.__getitem__(self, index)
        if isinstance(self.rowClass, types.MethodType) or not isinstance(ret, self.rowClass):
            if not isinstance(ret, blue.DBRow):
                ret = blue.DBRow(self.header, ret)
            return self.rowClass(self.header, ret)
        return ret

    def __setitem__(self, idx, row):
        if not isinstance(row, blue.DBRow):
            log.LogTraceback('__setitem__:Storing non-dbrow in GodmaRowset')
        dbutil.CRowset.__setitem__(self, idx, row)

    def __iter__(self):
        if self.rowClass != blue.DBRow:
            return rowsetIterator(self)
        return dbutil.CRowset.__iter__(self)

    def __getslice__(self, i, j):
        return GodmaRowset(self.header, list.__getslice__(self, i, j), rowClass=self.rowClass)

    def pop(self, idx = -1):
        ret = self.__getitem__(idx)
        dbutil.CRowset.pop(self, idx)
        return ret

    def Index(self, columnName):
        return GodmaIndexedRowset(self.header, columnName, dbutil.CRowset.Index(self, columnName), rowClass=self.rowClass)

    def Filter(self, columnName, indexName = None):
        return GodmaFilterRowset(self.header, columnName, indexName, dbutil.CRowset.Filter(self, columnName, indexName), rowClass=self.rowClass)


class GodmaIndexedRowset(dbutil.CIndexedRowset):
    __guid__ = 'util.GodmaIndexedRowset'

    def __init__(self, header, columnName, ccdict = {}, rowClass = blue.DBRow):
        dbutil.CIndexedRowset.__init__(self, header, columnName)
        self.rowClass = rowClass
        if len(ccdict):
            self.update(ccdict)

    def __getitem__(self, key):
        ret = dbutil.CIndexedRowset.__getitem__(self, key)
        if isinstance(self.rowClass, types.MethodType) or not isinstance(ret, self.rowClass):
            if not isinstance(ret, blue.DBRow):
                ret = blue.DBRow(self.header, ret)
            ret = self.rowClass(self.header, ret)
        return ret

    def values(self):
        return util.GodmaRowset(self.header, dbutil.CIndexedRowset.values(self), rowClass=self.rowClass)

    def itervalues(self):
        if self.rowClass != blue.DBRow:
            return rowsetIterator(self)
        return dbutil.CIndexedRowset.itervalues(self)

    def get(self, k, d = None):
        try:
            ret = self.__getitem__(k)
        except KeyError:
            return d

        return ret

    def pop(self, *args):
        if len(args) > 2 or len(args) < 1:
            raise TypeError('pop expected at most 2 arguments, got %d' % len(args))
        try:
            ret = self.__getitem__(args[0])
            del self[args[0]]
        except KeyError:
            if len(args) != 2:
                raise 
            return args[1]

        return ret

    def popitem(self):
        if len(self) == 0:
            raise KeyError
        import random
        key = random.randrange(len(self))
        ret = self.__getitem__(key)
        del self[key]
        return ret


class GodmaFilterRowset(dbutil.CFilterRowset):
    __guid__ = 'util.GodmaFilterRowset'

    def __init__(self, header, columnName, indexName, ccdict = {}, rowClass = blue.DBRow):
        dbutil.CFilterRowset.__init__(self, header, columnName)
        self.indexName = indexName
        self.rowClass = rowClass
        if len(ccdict) > 0:
            self.update(ccdict)

    def __getitem__(self, key):
        ret = dbutil.CFilterRowset.__getitem__(self, key)
        if isinstance(ret, dict):
            if not isinstance(ret, util.GodmaIndexedRowset):
                return util.GodmaIndexedRowset(self.header, self.indexName, ret, rowClass=self.rowClass)
            return ret
        if isinstance(self.rowClass, types.MethodType) or not isinstance(ret, self.rowClass):
            if not isinstance(ret, blue.DBRow):
                print ' _!_ GodmaFilteredRowset storing non-DBRow as leaf-element:', type(ret)
                ret = blue.DBRow(self.header, ret)
            return self.rowClass(self.header, ret)
        return ret

    def values(self):
        v = dbutil.CFilteredRowset.values(self)
        if isinstance(v, list):
            return v
        return util.GodmaIndexedRowset(self.header, self.indexName, v, rowClass=self.rowClass)

    def itervalues(self):
        if self.rowClass != blue.DBRow:
            return rowsetIterator(self)
        return dbutil.CFilterRowset.itervalues(self)

    def get(self, k, d = None):
        try:
            ret = self.__getitem__(k)
        except KeyError:
            return d

        return ret

    def pop(self, *args):
        if len(args) > 2 or len(args) < 1:
            raise TypeError('pop expected at most 2 arguments, got %d' % len(args))
        try:
            ret = self.__getitem__(args[0])
            del self[args[0]]
        except KeyError:
            if len(args) != 2:
                raise 
            return args[1]

        return ret

    def popitem(self):
        if len(self) == 0:
            raise KeyError
        import random
        key = self.keys()[random.randrange(len(self))]
        ret = self.__getitem__(key)
        del self[key]
        return ret