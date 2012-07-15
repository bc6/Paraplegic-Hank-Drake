#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\carbon\staticData\schema\loaders\objectLoader.py
import ctypes
import collections

class ObjectLoader(object):

    def __init__(self, data, offset, schema, extraState):
        self.__data__ = data
        self.__offset__ = offset
        self.__schema__ = schema
        self.__extraState__ = extraState
        self.__hasOptionalAttributes__ = False
        if 'size' not in schema:
            self.__offsetAttributes__ = schema['attributesWithOffsets'][:]
            if self.__schema__['optionalValueLookups']:
                self.__hasOptionalAttributes__ = True
                optionalAttributesField = ctypes.cast(ctypes.byref(data, offset + schema['endOfFixedSizeData']), ctypes.POINTER(ctypes.c_uint32)).contents.value
                for attr, i in schema['optionalValueLookups'].iteritems():
                    if not optionalAttributesField & i:
                        self.__offsetAttributes__.remove(attr)

            offsetAttributeOffsetsType = ctypes.c_uint32 * len(self.__offsetAttributes__)
            self.__variableDataOffsetBase__ = self.__offset__ + self.__schema__.get('endOfFixedSizeData') + 4 + ctypes.sizeof(offsetAttributeOffsetsType)
            self.__offsetAttributesOffsetLookupTable__ = ctypes.cast(ctypes.byref(data, offset + schema.get('endOfFixedSizeData', 0) + 4), ctypes.POINTER(offsetAttributeOffsetsType))

    def __getitem__(self, key):
        if key not in self.__schema__['attributes']:
            if self.__extraState__.cfgObject is None:
                raise KeyError("Schema does not contain this attribute '%s'. It may not be present under the current environment." % key)
            else:
                return getattr(self.__extraState__.cfgObject, key)
        attributeSchema = self.__schema__['attributes'][key]
        if key in self.__schema__['attributeOffsets']:
            return self.__extraState__.RepresentSchemaNode(self.__data__, self.__offset__ + self.__schema__['attributeOffsets'][key], attributeSchema)
        else:
            try:
                index = self.__offsetAttributes__.index(key)
            except ValueError:
                if self.__extraState__.cfgObject is not None:
                    return getattr(self.__extraState__.cfgObject, key)
                if 'default' in attributeSchema:
                    return attributeSchema['default']
                raise KeyError("Object instance does not have this attribute '%s'" % key)

            return self.__extraState__.RepresentSchemaNode(self.__data__, self.__variableDataOffsetBase__ + self.__offsetAttributesOffsetLookupTable__.contents[index], attributeSchema)

    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError as e:
            raise AttributeError(str(e))