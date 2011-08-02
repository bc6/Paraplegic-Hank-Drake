import sys
from ctypes import *
_array_type = type(c_int * 3)

def _other_endian(typ):
    try:
        return getattr(typ, _OTHER_ENDIAN)
    except AttributeError:
        if type(typ) == _array_type:
            return _other_endian(typ._type_) * typ._length_
        raise TypeError('This type does not support other endian: %s' % typ)



class _swapped_meta(type(Structure)):

    def __setattr__(self, attrname, value):
        if attrname == '_fields_':
            fields = []
            for desc in value:
                name = desc[0]
                typ = desc[1]
                rest = desc[2:]
                fields.append((name, _other_endian(typ)) + rest)

            value = fields
        super(_swapped_meta, self).__setattr__(attrname, value)



if sys.byteorder == 'little':
    _OTHER_ENDIAN = '__ctype_be__'
    LittleEndianStructure = Structure

    class BigEndianStructure(Structure):
        __metaclass__ = _swapped_meta
        _swappedbytes_ = None

elif sys.byteorder == 'big':
    _OTHER_ENDIAN = '__ctype_le__'
    BigEndianStructure = Structure

    class LittleEndianStructure(Structure):
        __metaclass__ = _swapped_meta
        _swappedbytes_ = None

else:
    raise RuntimeError('Invalid byteorder')

