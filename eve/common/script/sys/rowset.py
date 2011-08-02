import types
import string
import _weakref
import weakref
import sys
import uthread
import copy
import blue
import __builtin__
import cPickle
import zipfile
import util
import log

def Select(selection, headers, iterator, options):
    if len(selection) == 1:
        i = headers.index(selection[0])
        if options.get('line', False):
            return [ (line, line[i]) for line in iterator ]
        else:
            return [ line[i] for line in iterator ]
    else:
        indices = []
        for header in selection:
            indices.append(headers.index(header))

        if options.get('line', False):
            return [ (line, [ line[i] for i in indices ]) for line in iterator ]
        else:
            return [ [ line[i] for i in indices ] for line in iterator ]



class Rowset():
    __guid__ = 'util.Rowset'
    __passbyvalue__ = 1
    __immutable__ = weakref.WeakKeyDictionary()
    RowClass = util.Row

    def __init__(self, hd = None, li = None, RowClass = util.Row):
        if hd is None:
            hd = []
        if li is None:
            li = []
        self.header = hd
        self.lines = li
        self.RowClass = RowClass



    def Clone(self):
        return Rowset(copy.copy(self.header), copy.copy(self.lines), self.RowClass)



    def IsImmutable(self):
        return self in self.__immutable__



    def MakeImmutable(self):
        if self not in self.__immutable__:
            self.__immutable__[self] = [{}, {}]



    def __str__(self):
        try:
            stuff = []
            for eachRow in self:
                stuff.append(strx(eachRow))

            return '<util.Rowset: header=%s, data=["' % strx(self.header) + string.join(stuff, '","') + '"]>'
        except:
            sys.exc_clear()
            return 'util.Rowset, hd=' + strx(self.header)



    def __len__(self):
        return len(self.lines)



    def RenameField(self, oldName, newName):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        for i in range(len(self.header)):
            if self.header[i] == oldName:
                self.header[i] = newName
                return 

        log.LogTraceback()
        raise RuntimeError('No Such Field')



    def AddField(self, fieldName, value):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        if len(self.lines) and type(self.lines[0]) == type(()):
            raise RuntimeError('CannotAddFieldsToATupleRowset', self)
        self.header.append(fieldName)
        for l in self.lines:
            l.append(value)




    def RemoveField(self, fieldName):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        if len(self.lines) and type(self.lines[0]) == type(()):
            raise RuntimeError('CannotRemoveFieldsFromATupleRowset', self)
        idx = self.header.index(fieldName)
        del self.header[idx]
        for l in self.lines:
            del l[idx]




    def find(self, column, value):
        h = self.header.index(column)
        for i in xrange(len(self.lines)):
            if self.lines[i][h] == value:
                return i

        return -1



    def Select(self, *selection, **options):
        return Select(selection, self.header, self.lines, options)



    def __getitem__(self, index):
        return self.RowClass(self.header, self.lines[index])



    def __setitem__(self, i, v):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        if type(v) == types.InstanceType:
            self[i] = v.line
            return 
        if len(v):
            if len(v) > len(self.header):
                raise RuntimeError('Too many columns, got %s, fields are %s' % (len(v), self.header))
            self.lines[i] = list(v) + [None] * (len(self.header) - len(v))
        else:
            self.lines[i] = [None] * len(self.header)



    def __getslice__(self, i, j):
        return Rowset(self.header, self.lines[i:j], self.RowClass)



    def __delitem__(self, index):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        del self.lines[index]



    def sort(self, f = None):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        if f is not None:
            self.lines.sort(f)
        else:
            self.lines.sort()



    def extend(self, other):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        self.lines.extend(other.lines)



    def remove(self, row):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        try:
            self.lines.remove(row.line)
        except ValueError:
            sys.exc_clear()
        except AttributeError:
            sys.exc_clear()
            self.lines.remove(row)



    def pop(self, idx):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        return self.RowClass(self.header, self.lines.pop(idx))



    def InsertNew(self, *args):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        if len(args):
            if len(args) > len(self.header):
                raise RuntimeError('Too many arguments, got %s, fields are %s' % (len(args), self.header))
            self.lines.append(list(args) + [None] * (len(self.header) - len(args)))
        else:
            self.lines.append([None] * len(self.header))
        return self[-1]



    def Sort(self, colname, asc = 1):
        ret = self[:]
        if asc:
            ret.lines.sort(lambda a, b, colid = self.header.index(colname): -(a[colid] < b[colid]))
        else:
            ret.lines.sort(lambda b, a, colid = self.header.index(colname): -(a[colid] < b[colid]))
        return ret



    def Index(self, colname):
        if self in self.__immutable__:
            uthread.Lock(self, '__immutable__', colname)
            try:
                if colname not in self.__immutable__[self][0]:
                    ret = IndexRowset(self.header, self.lines, colname)
                    self.__immutable__[self][0][colname] = ret
                    ret.MakeImmutable()
                return self.__immutable__[self][0][colname]

            finally:
                uthread.UnLock(self, '__immutable__', colname)

        else:
            return IndexRowset(self.header, self.lines, colname)



    def Filter(self, colname, colname2 = None):
        if self in self.__immutable__:
            k = (colname, colname2)
            uthread.Lock(self, '__immutable__', k)
            try:
                if k not in self.__immutable__[self][1]:
                    ret = FilterRowset(self.header, self.lines, colname, idName2=colname2)
                    ret.MakeImmutable()
                    self.__immutable__[self][1][k] = ret
                return self.__immutable__[self][1][k]

            finally:
                uthread.UnLock(self, '__immutable__', k)

        else:
            return FilterRowset(self.header, self.lines, colname, idName2=colname2)



    def append(self, row):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        if type(row) == type([]):
            if len(row) != len(self.header):
                raise RuntimeError('Invalid row length for appending', self, row)
            self.lines.append(row)
        elif len(self.header) != len(row.header):
            raise RuntimeError('Invalid header for appending', self, row)
        self.lines.append(row.line)




class IndexOrFilterRowsetIterator():

    def __init__(self, rowset, iterator):
        self.rowset = _weakref.proxy(rowset)
        self.iterator = iterator



    def next(self):
        return self.rowset.RowClass(self.rowset.header, self.iterator.next())




class IndexRowset():
    __guid__ = 'util.IndexRowset'
    __passbyvalue__ = 1
    __immutable__ = weakref.WeakKeyDictionary()
    RowClass = util.Row
    stacktraceCnt = 0

    def __init__(self, header = None, li = (), idName = None, RowClass = util.Row, dict = None):
        if dict is not None:
            self.items = dict
        elif header is not None and li is not None:
            idfield = header.index(idName)
            self.items = __builtin__.dict([ (i[idfield], i) for i in li ])
        else:
            self.items = {}
        self.header = header
        self.RowClass = RowClass
        self.idName = idName



    def GetKeyColumn(self):
        return self.idName



    def GetLine(self, key):
        return self.items[key]



    def Clone(self):
        return IndexRowset(copy.copy(self.header), None, self.idName, self.RowClass, copy.copy(self.items))



    def IsImmutable(self):
        return self in self.__immutable__



    def MakeImmutable(self):
        if self not in self.__immutable__:
            self.__immutable__[self] = 1



    def Select(self, *selection, **options):
        return Select(selection, self.header, self.items.itervalues(), options)



    def __iter__(self):
        return iter(self.items)



    def __contains__(self, key):
        return key in self.items



    def __getitem__(self, i):
        return self.RowClass(self.header, self.items[i])



    def __len__(self):
        return len(self.items)



    def values(self):
        return Rowset(self.header, self.items.values(), self.RowClass)



    def itervalues(self):
        return self.values()



    def keys(self):
        return self.items.keys()



    def iterkeys(self):
        return self.items.iterkeys()



    def has_key(self, key):
        return self.items.has_key(key)



    def __setitem__(self, ind, row):
        if self in self.__immutable__:
            raise RuntimeError('Immutable IndexRowsets may not be modified')
        if type(row) == type([]):
            self.items[ind] = row
        elif hasattr(row, '__columns__'):
            rowHeader = row.__columns__
            rowLine = list(row)
        else:
            rowHeader = row.header
            rowLine = row.line
        if len(self.header) != len(rowHeader):
            line = [None] * len(self.header)
            for i in range(len(self.header)):
                cname = self.header[i]
                try:
                    idx = rowHeader.index(cname)
                except ValueError:
                    raise RuntimeError('Mismatched row headers - game is broken', self.header, rowHeader)
                line[i] = rowLine[idx]

            if self.stacktraceCnt < 2:
                log.LogTraceback('rowset')
                self.stacktraceCnt += 1
            self.items[ind] = line
        else:
            self.items[ind] = rowLine



    def __delitem__(self, ind):
        if self in self.__immutable__:
            raise RuntimeError('Immutable IndexRowsets may not be modified')
        del self.items[ind]



    def Sort(self, colname):
        ret = self.values()
        return ret.Sort(colname)



    def get(self, ind, defValue):
        try:
            return self[ind]
        except:
            sys.exc_clear()
            return defValue



    def UpdateLI(self, lines, indexName, overWrite = 0):
        if self in self.__immutable__:
            raise RuntimeError('Immutable IndexRowsets may not be modified')
        ind = self.header.index(indexName)
        for i in lines:
            if not (not overWrite and self.items.has_key(i[ind])):
                self.items[i[ind]] = i




    def Map(self, indexes):
        ret = Rowset(self.header, [])
        for i in indexes:
            if self.has_key(i):
                ret.append(self[i])

        return ret



    def __str__(self):
        stuff = {}
        for key in self.iterkeys():
            eachRow = self[key]
            stuff[key] = eachRow

        return '<util.IndexRowset: header=%s, data=' % strx(self.header) + strx(stuff).replace('"', '') + '>'




class FilterRowset():
    __guid__ = 'util.FilterRowset'
    __passbyvalue__ = 1
    __immutable__ = weakref.WeakKeyDictionary()
    RowClass = util.Row

    def __init__(self, header = None, li = None, idName = None, RowClass = util.Row, idName2 = None, dict = None):
        items = {}
        self.RowClass = RowClass
        if dict is not None:
            items = dict
        elif header is not None:
            if not idName2:
                idfield = header.index(idName)
                for i in li:
                    id = i[idfield]
                    if id in items:
                        items[id].append(i)
                    else:
                        items[id] = [i]

            else:
                idfield = header.index(idName)
                idfield2 = header.index(idName2)
                for i in li:
                    id = i[idfield]
                    if id in items:
                        items[id][i[idfield2]] = i
                    else:
                        items[id] = {i[idfield2]: i}

        self.items = items
        self.header = header
        self.idName = idName
        self.idName2 = idName2



    def Clone(self):
        return FilterRowset(copy.copy(self.header), None, self.idName, self.RowClass, self.idName2, dict=copy.deepcopy(self.items))



    def IsImmutable(self):
        return self in self.__immutable__



    def MakeImmutable(self):
        if self not in self.__immutable__:
            self.__immutable__[self] = 1



    def __iter__(self):
        return IndexOrFilterRowsetIterator(self, self.items.iterkeys())



    def __contains__(self, key):
        return key in self.items



    def has_key(self, key):
        return self.items.has_key(key)



    def get(self, key, val):
        try:
            return self[key]
        except:
            sys.exc_clear()
            return val



    def keys(self):
        return self.items.keys()



    def iterkeys(self):
        return self.items.iterkeys()



    def __getitem__(self, i):
        if self.idName2:
            return IndexRowset(self.header, None, self.idName2, self.RowClass, self.items.get(i, {}))
        return Rowset(self.header, self.items.get(i, []), self.RowClass)



    def __len__(self):
        return len(self.items)



    def Sort(self, colname):
        ret = Rowset(self.header, self.items.values(), self.RowClass)
        return ret.Sort(colname)



    def GetIndexKeys(self):
        if self.idName2 is not None:
            return (self.idName, self.idName2)
        return (self.idName,)



    def GetLines(self, idValue, idValue2 = None):
        if self.idName2 is not None:
            return self.items[idValue][idValue2]
        return self.items[idValue]




class InvRow(util.Row):
    __guid__ = 'util.InvRow'

    def __setitem__(self, key, value):
        if key != const.ixCustomInfo:
            raise RuntimeError('This cannot be done, use inventory2 methods instead')
        self.__dict__['line'][key] = value




class SparseRowsetIterator2():

    def __init__(self, rowset, iterator):
        self.rowset = _weakref.proxy(rowset)
        self.iterator = iterator



    def __iter__(self):
        return self



    def next(self):
        return self.rowset.RowClass(self.rowset.header, self.iterator.next())




class SparseRowsetIterator():
    RowClass = util.Row

    def __init__(self, header, iterator, RowClass = util.Row):
        self.header = header
        self.RowClass = RowClass
        self.iterator = iterator



    def __iter__(self):
        return self



    def next(self):
        return self.RowClass(self.header, self.iterator.next())




class SparseRowsetProvider():
    __guid__ = 'util.SparseRowsetProvider'
    __passbyvalue__ = 0
    __publicattributes__ = ['realRowCount']
    __exportedcalls__ = {'GetPKForIndex': [],
     'ComputePKForLine': [],
     'GeneratePKForLine': [],
     'FireUpdateNotification': [],
     'Fetch': [],
     'FetchByKey': [],
     'SelectByUniqueColumnValues': []}
    RowClass = util.Row

    def __init__(self, hd = None, li = None, primaryKeys = [], RowClass = util.Row):
        if hd is None:
            hd = []
        if li is None:
            li = []
        self.header = hd
        self.primaryKeys = []
        for keyName in primaryKeys:
            columnIndex = -1
            for columnName in self.header:
                columnIndex += 1
                if columnName == keyName:
                    self.primaryKeys.append(columnIndex)
                    break


        self._SparseRowsetProvider__items = {}
        self._SparseRowsetProvider__itemFromPos = []
        self._SparseRowsetProvider__MultiAdd(li, 0)
        self.RowClass = RowClass
        self.realRowCount = len(self)



    def GetPKForIndex(self, index):
        return self._SparseRowsetProvider__itemFromPos[index]



    def ComputePKForLine(self, line):
        primaryKey = []
        if not self.primaryKeys:
            raise RuntimeError('NoPrimaryKeysDefined')
        else:
            for columnIndex in self.primaryKeys:
                primaryKey.append(line[columnIndex])

        if len(primaryKey) == 1:
            return primaryKey[0]
        return primaryKey



    def GeneratePKForLine(self, line):
        primaryKey = []
        if not self.primaryKeys:
            primaryKey = uthread.uniqueId()
        else:
            for columnIndex in self.primaryKeys:
                primaryKey.append(line[columnIndex])

        if len(primaryKey) == 1:
            return primaryKey[0]
        return primaryKey



    def __MultiAdd(self, lines, notify = 1, notificationParams = {}):
        for line in lines:
            primaryKey = self.GeneratePKForLine(line)
            self._SparseRowsetProvider__items[primaryKey] = line
            self._SparseRowsetProvider__itemFromPos.append(primaryKey)
            if notify:
                (old, new,) = (None, self.RowClass(self.header, self._SparseRowsetProvider__items[primaryKey]))
                change = self._SparseRowsetProvider__GetChangeDictFromLines(old, new)
                self.FireUpdateNotification(change, primaryKey, notificationParams)




    def FireUpdateNotification(self, change, changePKIndexValue, notificationParams = {}):
        if not len(change):
            log.LogTraceback('Illegal update notification')
            return False
        self.realRowCount = len(self)
        if hasattr(self, 'UpdatePublicAttributes'):
            self.UpdatePublicAttributes(change=change, changePKIndexValue=changePKIndexValue, notificationParams=notificationParams, partial=['realRowCount'])
        return True



    def Fetch(self, startPos, fetchSize):
        count = 0
        indexesAndLines = []
        maxIndex = len(self._SparseRowsetProvider__itemFromPos) - 1
        while count != fetchSize:
            index = startPos + count
            if index > maxIndex:
                break
            pkIndexValue = self._SparseRowsetProvider__itemFromPos[index]
            indexesAndLines.append((pkIndexValue, self._SparseRowsetProvider__items[pkIndexValue]))
            count += 1

        return indexesAndLines



    def FetchByKey(self, primaryKeys):
        pkIndexLine = []
        for pk in primaryKeys:
            pkIndexLine.append((pk, self._SparseRowsetProvider__itemFromPos.index(pk), self._SparseRowsetProvider__items[pk]))

        return pkIndexLine



    def SelectByUniqueColumnValues(self, columnName, valuesToFind):
        pkIndexLine = []
        if len(valuesToFind):
            columnIndex = self.header.index(columnName)
            for ix in xrange(len(self._SparseRowsetProvider__itemFromPos)):
                pk = self._SparseRowsetProvider__itemFromPos[ix]
                line = self._SparseRowsetProvider__items[pk]
                value = line[columnIndex]
                if value in valuesToFind:
                    pkIndexLine.append((pk, ix, line))
                    valuesToFind.remove(value)
                    if 0 == len(valuesToFind):
                        break

        return pkIndexLine



    def __str__(self):
        try:
            stuff = []
            for eachRow in self._SparseRowsetProvider__items.itervalues():
                stuff.append(strx(eachRow))

            return '<util.SparseRowsetProvider: header=%s, data=["' % strx(self.header) + string.join(stuff, '","') + '"]>'
        except:
            sys.exc_clear()
            return 'util.SparseRowsetProvider, hd=' + strx(self.header)



    def __len__(self):
        return len(self._SparseRowsetProvider__itemFromPos)



    def has_key(self, key):
        return self._SparseRowsetProvider__items.has_key(key)



    def __getitem__(self, pk):
        row = self.RowClass(self.header, self._SparseRowsetProvider__items[pk])
        setattr(row, 'primaryKey', pk)
        return row



    def AddField(self, fieldName, value):
        raise RuntimeError('NotSupported')



    def __getslice__(self, i, j):
        raise RuntimeError('NotSupported')



    def __GetChangeDictFromLines(self, old, new):
        if old is None and new is None:
            raise RuntimeError('__GetChangeDictFromLines Invalid Paramter Combintaion')
        change = {}
        header = self.header
        columnIndex = -1
        for columnName in header:
            columnIndex += 1
            (oldVal, newVal,) = (None, None)
            if old is not None:
                oldVal = old[columnIndex]
            if new is not None:
                newVal = new[columnIndex]
            if old is None or new is None or oldVal != newVal:
                change[columnName] = (oldVal, newVal)

        return change



    def __delitem__(self, pk):
        (old, new,) = (self.RowClass(self.header, self._SparseRowsetProvider__items[pk]), None)
        change = self._SparseRowsetProvider__GetChangeDictFromLines(old, new)
        self._SparseRowsetProvider__itemFromPos.remove(pk)
        del self._SparseRowsetProvider__items[pk]
        self.FireUpdateNotification(change, pk)



    def itervalues(self):
        return SparseRowsetIterator(self.header, self._SparseRowsetProvider__items.itervalues(), self.RowClass)



    def iterkeys(self):
        return self._SparseRowsetProvider__items.iterkeys()



    def __iter__(self):
        return IndexOrFilterRowsetIterator(self, self._SparseRowsetProvider__items.iterkeys())



    def sort(self, f = None):
        raise RuntimeError('NotSupported')



    def extend(self, other):
        raise RuntimeError('NotSupported')



    def remove(self, row, notificationParams = {}):
        pk = row.primaryKey
        (old, new,) = (self.RowClass(self.header, self._SparseRowsetProvider__items[pk]), None)
        change = self._SparseRowsetProvider__GetChangeDictFromLines(old, new)
        self._SparseRowsetProvider__itemFromPos.remove(pk)
        del self._SparseRowsetProvider__items[pk]
        self.FireUpdateNotification(change, pk, notificationParams)



    def update(self, pk, row, notificationParams = {}):
        (old, new,) = (self.RowClass(self.header, self._SparseRowsetProvider__items[pk]), row)
        change = self._SparseRowsetProvider__GetChangeDictFromLines(old, new)
        self._SparseRowsetProvider__items[pk] = row.line
        return self.FireUpdateNotification(change, pk, notificationParams)



    def pop(self, idx):
        raise RuntimeError('NotSupported')



    def InsertNew(self, *args):
        raise RuntimeError('NotSupported')



    def Sort(self, colname, asc = 1):
        raise RuntimeError('NotSupported')



    def Index(self, colname):
        raise RuntimeError('NotSupported')



    def Filter(self, colname, colname2 = None):
        raise RuntimeError('NotSupported')



    def append(self, row, notificationParams = {}):
        if type(row) == type([]):
            if len(row) != len(self.header):
                raise RuntimeError('Invalid row length for appending', self, row)
            self._SparseRowsetProvider__MultiAdd([row], 1, notificationParams)
        elif len(self.header) != len(row.header):
            raise RuntimeError('Invalid header for appending', self, row)
        self._SparseRowsetProvider__MultiAdd([row.line], 1, notificationParams)




class SparseRowset():
    __guid__ = 'util.SparseRowset'
    __passbyvalue__ = 1
    RowClass = util.Row

    def __init__(self, serverRowset, RowClass = util.Row, listener = None):
        self.serverRowset = serverRowset
        self.header = self.serverRowset.header
        self._SparseRowset__linesByKey = {}
        self._SparseRowset__keyFromPos = []
        self.RowClass = RowClass
        self._SparseRowset__listeners = {}
        if listener is not None:
            self.AddListener(listener)



    def __isclass(self, obj):
        dict = dir(obj)
        if dict is None or not len(dict):
            return 
        if '__klass__' in dict:
            return 1
        if '__methods__' in dict:
            return 1
        if '__class__' in dict:
            return 1
        import log
        log.general.Log('__isclass debug info %s' % dict, log.LGINFO)



    def AddListener(self, listener):
        if not self._SparseRowset__isclass(listener):
            raise RuntimeError('AddListener only accepts instances')
        self._SparseRowset__listeners[id(listener)] = _weakref.proxy(listener)



    def RemoveListener(self, listener):
        if type(listener) in (_weakref.ProxyType, _weakref.CallableProxyType):
            raise RuntimeError('RemoveListener does not accept proxy objects')
        if not self._SparseRowset__isclass(listener):
            raise RuntimeError('RemoveListener  only accepts instances')
        try:
            del self._SparseRowset__listeners[id(listener)]
        except ReferenceError as e:
            sys.exc_clear()
        except KeyError as e:
            sys.exc_clear()



    def __getstate__(self):
        return (self.header, self.serverRowset, len(self))



    def __setstate__(self, state):
        (self.header, self.serverRowset, length,) = state
        self._SparseRowset__listeners = {}
        self._SparseRowset__linesByKey = {}
        self._SparseRowset__keyFromPos = [None] * length
        self.serverRowset.RegisterObjectChangeHandler(self)



    def OnObjectChanged(self, conn, old, updatedattributes, *args, **keywords):
        change = keywords['change']
        changePKIndexValue = keywords['changePKIndexValue']
        notificationParams = {}
        if keywords.has_key('notificationParams'):
            notificationParams = keywords['notificationParams']
        (bAdd, bRemove,) = self._SparseRowset__GetAddRemoveFromChange(change)
        if bAdd:
            if len(change) != len(self.header):
                raise RuntimeError('IncorrectNumberOfColumns len(change)', len(change), 'len(self.header)', len(self.header))
            line = []
            for columnName in self.header:
                line.append(change[columnName][1])

            self._SparseRowset__linesByKey[changePKIndexValue] = line
            self._SparseRowset__keyFromPos.append(changePKIndexValue)
        elif not self._SparseRowset__linesByKey.has_key(changePKIndexValue):
            return 
        if bRemove:
            del self._SparseRowset__linesByKey[changePKIndexValue]
            self._SparseRowset__keyFromPos.remove(changePKIndexValue)
        else:
            line = self._SparseRowset__linesByKey[changePKIndexValue]
            columnIndex = -1
            for columnName in self.header:
                columnIndex += 1
                if not change.has_key(columnName):
                    continue
                line[columnIndex] = change[columnName][1]

        toRemove = []
        for (key, listener,) in self._SparseRowset__listeners.iteritems():
            try:
                if hasattr(listener, 'OnDataChanged'):
                    listener.OnDataChanged(self, changePKIndexValue, change, notificationParams)
                else:
                    import log
                    log.general.Log('Listener::OnDataChanged does not exist for %s' % listener, log.LGWARN)
            except ReferenceError as e:
                toRemove.append(key)
                sys.exc_clear()
            except:
                import log
                log.LogException()
                sys.exc_clear()

        for key in toRemove:
            del self._SparseRowset__listeners[key]




    def __GetAddRemoveFromChange(self, change):
        bAdd = bRemove = len(change) == len(self.header)
        if bAdd or bRemove:
            for (old, new,) in change.itervalues():
                if old is None and new is None:
                    continue
                if old is not None:
                    bAdd = 0
                if new is not None:
                    bRemove = 0

        if bAdd and bRemove:
            raise RuntimeError('__GetAddRemoveFromChange Can NOT ADD AND REMOVE TOGETHER')
        return (bAdd, bRemove)



    def __getitem__(self, index):
        line = None
        pk = self._SparseRowset__keyFromPos[index]
        if pk is not None:
            line = self._SparseRowset__linesByKey[pk]
        if not line:
            self.Fetch(index, 1)
            line = self._SparseRowset__linesByKey[self._SparseRowset__keyFromPos[index]]
        return self.RowClass(self.header, line)



    def Fetch(self, startPos, fetchSize):
        for index in range(startPos, startPos + fetchSize):
            pk = self._SparseRowset__keyFromPos[index]
            if pk is None:
                startPos = index
                break
            fetchSize -= 1

        if fetchSize < 1:
            return 
        i = startPos
        for (newIndex, newLine,) in self.serverRowset.Fetch(startPos, fetchSize):
            self._SparseRowset__linesByKey[newIndex] = newLine
            self._SparseRowset__keyFromPos[i] = newIndex
            i += 1




    def FetchByKey(self, primaryKeys):
        request = []
        for pk in primaryKeys:
            if not self._SparseRowset__linesByKey.has_key(pk):
                request.append(pk)

        if not request:
            return 
        for (pk, ix, line,) in self.serverRowset.FetchByKey(request):
            self._SparseRowset__linesByKey[pk] = line
            self._SparseRowset__keyFromPos[ix] = pk




    def GetByKey(self, key):
        if not self._SparseRowset__linesByKey.has_key(key):
            for (key, ix, line,) in self.serverRowset.FetchByKey([key]):
                self._SparseRowset__linesByKey[key] = line
                self._SparseRowset__keyFromPos[ix] = key
                break

        return self.RowClass(self.header, self._SparseRowset__linesByKey[key])



    def SelectByUniqueColumnValues(self, columnName, valuesToFind):
        lines = []
        if len(valuesToFind):
            ix = self.header.index(columnName)
            for (pk, line,) in self._SparseRowset__linesByKey.iteritems():
                currentValue = line[ix]
                if currentValue in valuesToFind:
                    lines.append(line)
                    valuesToFind.remove(currentValue)
                    if 0 == len(valuesToFind):
                        break

            if len(valuesToFind):
                import log
                log.general.Log('SparseRowset tripping on %s' % valuesToFind, log.LGWARN)
                pkIxLine = self.serverRowset.SelectByUniqueColumnValues(columnName, valuesToFind)
                log.general.Log('SparseRowset done tripping for %s' % valuesToFind, log.LGWARN)
                for (pk, ix, line,) in pkIxLine:
                    lines.append(line)
                    self._SparseRowset__linesByKey[pk] = line
                    self._SparseRowset__keyFromPos[ix] = pk

        res = Rowset(self.header, lines)
        return res



    def __str__(self):
        try:
            stuff = []
            for eachRow in self:
                stuff.append(strx(eachRow))

            return '<util.SparseRowset: header=%s, data=["' % strx(self.header) + string.join(stuff, '","') + '"]>'
        except:
            sys.exc_clear()
            return 'util.SparseRowset, hd=' + strx(self.header)



    def __len__(self):
        return self.serverRowset.realRowCount



    def AddField(self, fieldName, value):
        raise RuntimeError('NotSupported')



    def __getslice__(self, i, j):
        raise RuntimeError('NotSupported')



    def __delitem__(self, index):
        raise RuntimeError('NotSupported')



    def sort(self, f = None):
        raise RuntimeError('NotSupported')



    def extend(self, other):
        raise RuntimeError('NotSupported')



    def remove(self, row):
        raise RuntimeError('NotSupported')



    def pop(self, idx):
        raise RuntimeError('NotSupported')



    def InsertNew(self, *args):
        raise RuntimeError('NotSupported')



    def Sort(self, colname, asc = 1):
        raise RuntimeError('NotSupported')



    def Index(self, colname):
        raise RuntimeError('NotSupported')



    def Filter(self, colname, colname2 = None):
        raise RuntimeError('NotSupported')



    def append(self, row):
        raise RuntimeError('NotSupported')




def RowsInit(rows, columns):
    header = None
    if type(rows) is types.TupleType:
        header = rows[0]
        rows = rows[1]
    if rows:
        first = rows[0]
        if type(first) != blue.DBRow:
            raise AttributeError('Not DBRow. Initialization requires a non-empty list of DBRows')
        header = first.__header__
    elif header:
        if type(header) != blue.DBRowDescriptor:
            raise AttributeError('expected (DBRowDesciptor, [])')
    if header:
        columns = header.Keys()
    return (rows, columns, header)



class RowDict(dict):
    __guid__ = 'dbutil.RowDict'
    __passbyvalue__ = 1
    slots = ['columns', 'header', 'key']

    def __init__(self, rowList, key, columns = None):
        dict.__init__(self)
        (rows, self.columns, self.header,) = RowsInit(rowList, columns)
        if key not in self.columns:
            raise AttributeError('Indexing key not found in row')
        self.key = key
        for row in rows:
            self[row[key]] = row




    def ReIndex(self, key):
        if key not in self.columns:
            raise AttributeError('Indexing key not found in columns')
        vals = self.values()
        self.clear()
        self.key = key
        for row in vals:
            self[row[self.key]] = row




    def Add(self, row):
        if type(row) != blue.DBRow:
            raise AttributeError('Not DBRow')
        if row.__columns__ != self.columns:
            raise ValueError('Incompatible rows')
        if self.header is None:
            self.header = row.__header__
        self[row[self.key]] = row




class RowList(list):
    __guid__ = 'dbutil.RowList'
    __passbyvalue__ = 1
    slots = ['header', 'columns']

    def __init__(self, rowList, columns = None):
        list.__init__(self)
        (rows, self.columns, self.header,) = RowsInit(rowList, columns)
        self[:] = rows



    def append(self, row):
        if type(row) != blue.DBRow:
            raise ValueError('Not DBRow')
        if row.__columns__ != self.columns:
            raise ValueError('Incompatible headers')
        if self.header is None:
            self.header = row.__header__
        list.append(self, row)




class IndexedRows(dict):
    __guid__ = 'util.IndexedRows'
    __passbyvalue__ = 1

    def __init__(self, rows = [], keys = None):
        self.InsertMany(keys, rows)



    def InsertMany(self, keys, rows):
        for r in rows:
            self.Insert(keys, r)




    def Insert(self, keys, e):
        (key, rkeys,) = (keys[0], keys[1:])
        if rkeys:
            if e[key] not in self:
                self[e[key]] = IndexedRows()
            self[e[key]].Insert(rkeys, e)
        else:
            self[e[key]] = e




class IndexedRowLists(dict):
    __guid__ = 'util.IndexedRowLists'
    __passbyvalue__ = 1

    def __init__(self, rows = [], keys = None):
        self.header = []
        self.InsertMany(keys, rows)



    def InsertMany(self, keys, rows):
        for r in rows:
            self.Insert(keys, r)




    def Insert(self, keys, e):
        (key, rkeys,) = (keys[0], keys[1:])
        self.header = [key]
        if rkeys:
            if e[key] not in self:
                self[e[key]] = IndexedRowLists()
            self[e[key]].Insert(rkeys, e)
        elif e[key] not in self:
            self[e[key]] = []
        self[e[key]].append(e)



    def GetIndexKeys(self):
        l = self.header[:]
        for v in self.itervalues():
            if isinstance(v, self.__class__):
                l.extend(v.GetIndexKeys())
            break

        return l



    def GetLines(self, firstKey, *nextKeys):
        ret = self[firstKey]
        if len(nextKeys):
            return ret.GetLines(*nextKeys)
        return ret




class DataSet(dict):
    __guid__ = 'util.DataSet'
    __passbyvalue__ = 1
    __columnmap__ = {}

    def __init__(self, dataSetName = None, *args, **kw):
        self.dataSetName = dataSetName



    def Add(self, name, rowset, columnmap):
        for column in columnmap:
            if column in self.__columnmap__ and columnmap[column] != self.__columnmap__[column]:
                raise ValueError('Ambiguous header (%s)' % column)

        self.__columnmap__.update(columnmap)
        self[name] = rowset




