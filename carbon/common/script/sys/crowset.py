import dbutil
import util
import blue
import const
from timerstuff import ClockThis
from service import *
DEBUG = False
ROWSETVERSION = 3

class CRowset(list):
    __guid__ = 'dbutil.CRowset'
    __passbyvalue__ = 1

    def __init__(self, header, rows):
        list.__init__(self, rows)
        self.header = header



    def __getslice__(self, i, j):
        return CRowset(self.header, list.__getslice__(self, i, j))



    def Copy(self):
        return CRowset(self.header, self)



    def GetColumnSchema(self):
        return self.header



    def GetColumnNames(self):
        return self.header.Keys()



    @property
    def columns(self):
        return self.header.Keys()



    def InsertNew(self, listOfValues):
        self.append(blue.DBRow(self.header, listOfValues))



    def Sort(self, columnName, caseInsensitive = False, reverse = False):
        ix = self.header.Keys().index(columnName)
        if caseInsensitive:
            Key = lambda a: a[ix].upper()
        else:
            Key = lambda a: a[ix]
        self.sort(key=Key, reverse=reverse)



    def Index(self, columnName):
        ir = CIndexedRowset(self.header, columnName)
        ir.Build(self)
        return ir



    def Filter(self, columnName, indexName = None, allowDuplicateCompoundKeys = False, giveMeSets = False):
        fr = CFilterRowset(self.header, columnName, indexName, allowDuplicateCompoundKeys, giveMeSets)
        fr.Build(self)
        return fr



    def Rebuild(self, rowset):
        del self[0:len(self)]
        for row in rowset:
            self.append(row)




    def Unpack(self, colsNotToUnpack = []):
        l = []
        for row in self:
            entry = {}
            for col in self.header.Keys():
                if col not in colsNotToUnpack:
                    entry[col] = row[self.header.Index(col)]

            l.append(entry)

        return l


    if DEBUG:

        def __contains__(self, item):
            if not isinstance(item, blue.DBRow):
                raise TypeError("CRowset: 'item' must be of type DBRow, but was type '%s'" % type(item))
            return list.__contains__(self, item)




class CIndexedRowset(dict):
    __guid__ = 'dbutil.CIndexedRowset'

    def __init__(self, header, columnName):
        self.header = header
        self.columnName = columnName



    @property
    def columns(self):
        return self.header.Keys()


    if DEBUG:

        def __setitem__(self, key, value):
            if not isinstance(value, blue.DBRow):
                raise TypeError("CIndexedRowset: 'value' must be of type DBRow, but was type '%s'" % type(value))
            (h1, h2,) = (str(value.__header__), str(self.header))
            if h1 != h2:
                raise TypeError("CIndexedRowset: Header mismatch - This rowset has '%s', 'value' had '%s'" % (h2, h1))
            return dict.__setitem__(self, key, value)



    def Build(self, rowset):
        if '.' in self.columnName:
            keys = self.columnName.split('.')
            c = 0
            for row in rowset:
                combinedKey = []
                for key in keys:
                    combinedKey.append(row[key])

                self[tuple(combinedKey)] = row
                c += 1
                if c == 25000:
                    c = 0
                    blue.pyos.BeNice()

        else:
            blue.pyos.XUtil_Index(rowset, self.columnName, self)



    def Rebuild(self, rowset):
        self.clear()
        self.Build(rowset)




class CFilterRowset(dict):
    __guid__ = 'dbutil.CFilterRowset'

    def __init__(self, header, columnName, indexName = None, allowDuplicateCompoundKeys = False, giveMeSets = False):
        self.header = header
        self.columnName = columnName
        self.indexName = indexName
        self.allowDuplicateCompoundKeys = allowDuplicateCompoundKeys
        self.giveMeSets = giveMeSets



    @property
    def columns(self):
        return self.header.Keys()



    def Build(self, rowset):
        c = 0
        keyIdx = self.header.Keys().index(self.columnName)
        if self.indexName is None:
            for row in rowset:
                key = row[keyIdx]
                if key in self:
                    if self.giveMeSets:
                        self[key].add(row)
                    else:
                        self[key].append(row)
                elif self.giveMeSets:
                    self[key] = set([row])
                else:
                    self[key] = CRowset(row.__header__, [row])
                c += 1
                if c == 10000:
                    c = 0
                    blue.pyos.BeNice()

        else:
            key2Idx = self.header.Keys().index(self.indexName)
            for row in rowset:
                key = row[keyIdx]
                key2 = row[key2Idx]
                if key not in self:
                    self[key] = {}
                if self.allowDuplicateCompoundKeys:
                    if key2 not in self[key]:
                        if self.giveMeSets:
                            self[key][key2] = set()
                        else:
                            self[key][key2] = CRowset(row.__header__, [])
                    if self.giveMeSets:
                        self[key][key2].add(row)
                    else:
                        self[key][key2].append(row)
                else:
                    self[key][key2] = row
                c += 1
                if c == 10000:
                    c = 0
                    blue.pyos.BeNice()




    def Rebuild(self, rowset):
        self.clear()
        self.Build(rowset)



    def RefreshWithList(self, li):
        self.clear()
        if len(li) > 0:
            keyIdx = li[0].__columns__.index(self.columnName)
            for row in li:
                key = row[keyIdx]
                if key in self:
                    self[key].append(row)
                else:
                    self[key] = CRowset(row.__header__, [row])





class LinearDict(list):
    __guid__ = 'dbutil.LinearDict'

    def __contains__(self, keyValue):
        for i in self:
            if i[0] == keyValue:
                return True

        return list.__contains__(self, keyValue)



    def __getitem__(self, keyValue):
        for i in self:
            if i[0] == keyValue:
                return i

        raise KeyError(keyValue)




def SaveRowset(rs, filename, segmented):
    print '>>about to SaveRowset',
    print filename,
    print segmented
    if isinstance(rs, CRowset):
        if segmented:
            raise RuntimeError('SaveRowset: No support for segmented CRowset')
    elif isinstance(rs, CIndexedRowset):
        cdata = True
    elif isinstance(rs, CFilterRowset):
        cdata = False
    else:
        raise RuntimeError("SaveRowset: No support for '%s'" % type(rs))
    dataFile = blue.ResFile()
    if not segmented:
        dataFile.Create(filename + '.cr')
        dataFile.Write(blue.marshal.Save((ROWSETVERSION, rs)))
    else:
        dataFile.Create(filename + '.data.cr')
        offsets = {}
        for (k, v,) in rs.iteritems():
            pos = dataFile.pos
            if cdata:
                blob = blue.marshal.Save(v.__cdata__)
            else:
                blob = blue.marshal.Save(v)
            dataFile.Write(blob)
            offsets[k] = (pos, len(blob))

        indexData = (ROWSETVERSION,
         rs.header,
         rs.columnName,
         offsets)
        indexFile = blue.ResFile()
        indexFile.Create(filename + '.index.cr')
        indexFile.Write(blue.marshal.Save(indexData))



def LoadRowset(filename):
    f = blue.ResFile()
    f.OpenAlways(filename + '.rs.data.cr')
    (version, rs,) = blue.marshal.Load(f.Read())
    if version != ROWSETVERSION:
        msg = 'DiskData: File %s is version %s, but I want %s' % (filename, version, ROWSETVERSION)
        raise RuntimeError(msg)
    return rs



class CRowsetDiskBase(object):
    __guid__ = 'dbutil.CRowsetDiskBase'
    __diskRowsets__ = []

    def __init__(self, filename):
        if isinstance(self, CIndexedRowset):
            parent = CIndexedRowset
            self.cdata = True
        elif isinstance(self, CFilterRowset):
            parent = CFilterRowset
            self.cdata = False
        else:
            raise RuntimeError("CRowsetDiskBase: No support for '%s'" % type(self))
        f = blue.ResFile()
        f.OpenAlways(filename + '.index.cr')
        indexData = blue.marshal.Load(f.Read())
        if indexData[0] != ROWSETVERSION:
            msg = 'DiskData: File %s is version %s, but I want %s' % (filename, indexData.version, ROWSETVERSION)
            raise RuntimeError(msg)
        parent.__init__(self, indexData[1], indexData[2])
        self.offsets = indexData[3]
        self.dataFile = blue.ResFile()
        self.dataFile.OpenAlways(filename + '.data.cr')
        self.maxUsage = 1
        self.minAge = 60
        self.loaded = {}
        self.__diskRowsets__ = weakref(self)



    def __getitem__(self, key):
        if key in self.loaded:
            self.loaded[key][1] = blue.os.GetWallclockTime()
            self.loaded[key][2] += 1
            return dict.__getitem__(self, key)
        (pos, size,) = self.offsets[key]
        self.dataFile.Seek(pos)
        blob = self.dataFile.Read(size)
        data = blue.marshal.Load(blob)
        if self.cdata:
            row = blue.DBRow(self.header)
            row.__cdata__ = data
        else:
            row = data
        self[key] = row
        self.loaded[key] = [blue.os.GetWallclockTime(), blue.os.GetWallclockTime(), 1]
        return row



    def __contains__(self, key):
        return key in self.offsets



    def GetKeys(self):
        return self.offsets.keys()



    def Flush(self):
        expire = blue.os.GetWallclockTime() - self.minAge * const.SEC
        deleted = 0
        for (k, v,) in self.loaded.items():
            if v[2] <= self.maxUsage and v[1] < expire:
                del self[k]
                del self.loaded[k]
                deleted += 1

        return deleted




class CIndexedRowsetDisk(CRowsetDiskBase, CIndexedRowset):
    __guid__ = 'dbutil.CIndexedRowsetDisk'

    def __init__(self, filename):
        CRowsetDiskBase.__init__(self, filename)




class CFilterRowsetDisk(CRowsetDiskBase, CFilterRowset):
    __guid__ = 'dbutil.CFilterRowsetDisk'

    def __init__(self, filename):
        CRowsetDiskBase.__init__(self, filename)



exports = {'dbutil.LoadRowset': LoadRowset,
 'dbutil.SaveRowset': SaveRowset}

