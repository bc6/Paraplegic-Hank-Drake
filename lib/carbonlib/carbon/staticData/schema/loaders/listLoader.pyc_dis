#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\carbon\staticData\schema\loaders\listLoader.py
import ctypes
import collections

class FixedSizeListIterator(object):

    def __init__(self, data, offset, itemSchema, itemCount, itemSize, extraState):
        self.data = data
        self.offset = offset
        self.itemSchema = itemSchema
        self.count = itemCount
        self.itemSize = itemSize
        self.index = -1
        self.__extraState__ = extraState

    def __iter__(self):
        return self

    def next(self):
        self.index += 1
        if self.index == self.count:
            raise StopIteration()
        return self.__extraState__.RepresentSchemaNode(self.data, self.offset + self.itemSize * self.index, self.itemSchema)


class FixedSizeListRepresentation(object):

    def __init__(self, data, offset, itemSchema, extraState, knownLength = None):
        self.data = data
        self.offset = offset
        self.itemSchema = itemSchema
        self.__extraState__ = extraState
        if knownLength is None:
            self.count = ctypes.cast(ctypes.byref(data, offset), ctypes.POINTER(ctypes.c_uint32)).contents.value
            self.fixedLength = False
        else:
            self.count = knownLength
            self.fixedLength = True
        self.itemSize = itemSchema['size']

    def __iter__(self):
        countOffset = 0 if self.fixedLength else 4
        return FixedSizeListIterator(self.data, self.offset + countOffset, self.itemSchema, self.count, self.itemSize, self.__extraState__)

    def __len__(self):
        return self.count

    def __getitem__(self, key):
        if type(key) not in (int, long):
            raise TypeError('Invalid key type')
        if key < 0 or key >= self.count:
            raise IndexError('Invalid item index %i for list of length %i' % (key, self.count))
        countOffset = 0 if self.fixedLength else 4
        totalOffset = self.offset + countOffset + self.itemSize * key
        return self.__extraState__.RepresentSchemaNode(self.data, totalOffset, self.itemSchema)


class VariableSizedListRepresentation(object):

    def __init__(self, data, offset, itemSchema, extraState, knownLength = None):
        self.data = data
        self.offset = offset
        self.itemSchema = itemSchema
        self.__extraState__ = extraState
        if knownLength is None:
            self.count = ctypes.cast(ctypes.byref(data, offset), ctypes.POINTER(ctypes.c_uint32)).contents.value
            self.fixedLength = False
        else:
            self.count = knownLength
            self.fixedLength = True

    def __len__(self):
        return self.count

    def __getitem__(self, key):
        if type(key) not in (int, long):
            raise TypeError('Invalid key type')
        if key < 0 or key >= self.count:
            raise IndexError('Invalid item index %i for list of length %i' % (key, self.count))
        countOffset = 0 if self.fixedLength else 4
        dataOffsetFromObjectStart = ctypes.cast(ctypes.byref(self.data, self.offset + countOffset + 4 * key), ctypes.POINTER(ctypes.c_uint32)).contents.value
        return self.__extraState__.RepresentSchemaNode(self.data, self.offset + dataOffsetFromObjectStart, self.itemSchema)


def ListFromBinaryString(data, offset, schema, extraState, knownLength = None):
    knownLength = schema.get('length', knownLength)
    if 'fixedItemSize' in schema:
        return FixedSizeListRepresentation(data, offset, schema['itemTypes'], extraState, knownLength)
    else:
        return VariableSizedListRepresentation(data, offset, schema['itemTypes'], extraState, knownLength)