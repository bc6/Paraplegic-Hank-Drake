#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\carbon\staticData\schema\binaryLoader.py
import ctypes
import loaders
import loaders.objectLoader
import loaders.dictLoader
import loaders.listLoader
from carbon.telemetryMarkup import TelemetryContext
defaultLoaderFactories = {'float': loaders.FloatFromBinaryString,
 'vector4': loaders.Vector4FromBinaryString,
 'vector3': loaders.Vector3FromBinaryString,
 'vector2': loaders.Vector2FromBinaryString,
 'string': loaders.StringFromBinaryString,
 'resPath': loaders.StringFromBinaryString,
 'enum': loaders.EnumFromBinaryString,
 'bool': loaders.BoolFromBinaryString,
 'int': loaders.IntFromBinaryString,
 'typeID': loaders.IntFromBinaryString,
 'list': loaders.listLoader.ListFromBinaryString,
 'object': loaders.objectLoader.ObjectLoader,
 'dict': loaders.dictLoader.DictLoader}

class LoaderState(object):

    def __init__(self, factories, logger = None, cfgObject = None):
        self.factories = factories
        self.logger = logger
        self.cfgObject = cfgObject

    def RepresentSchemaNode(self, data, offset, schemaNode):
        schemaType = schemaNode.get('type')
        if schemaType in self.factories:
            return self.factories[schemaType](data, offset, schemaNode, self)
        raise NotImplementedError("Unknown type not supported in binary loader '%s'" % str(schemaType))

    def CreateNewStateWithCfgObject(self, cfgObject):
        return LoaderState(self.factories, self.logger, cfgObject)


def RepresentSchemaNode(data, offset, schemaNode, extraState = None):
    schemaType = schemaNode.get('type')
    if extraState is None:
        extraState = LoaderState(defaultLoaderFactories, None)
    if schemaType in extraState.factories:
        return extraState.factories[schemaType](data, offset, schemaNode, extraState)
    raise NotImplementedError("Unknown type not supported in binary loader '%s'" % str(schemaType))


def LoadFromString(dataString, optimizedSchema, extraState = None):
    dataBuffer = ctypes.create_string_buffer(dataString, len(dataString))
    return RepresentSchemaNode(dataBuffer, 0, optimizedSchema, extraState)


def LoadIndexFromFile(fileObject, optimizedSchema, cacheItems, extraState = None):
    if extraState is None:
        extraState = LoaderState(defaultLoaderFactories, None)
    return loaders.dictLoader.IndexLoader(fileObject, cacheItems, optimizedSchema, extraState)


class BlueResFileIOWrapper(object):

    def __init__(self, resFile):
        self.__resFile__ = resFile

    def seek(self, offset, start = None):
        if start is None:
            return self.__resFile__.Seek(offset)
        else:
            return self.__resFile__.Seek(offset, start)

    def read(self, bytes):
        with TelemetryContext('FSD File Read'):
            return self.__resFile__.Read(bytes)