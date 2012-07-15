#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\carbon\staticData\schema\persistence.py
import yaml
import collections

def orderedDict_constructor(loader, node):
    value = collections.OrderedDict()
    for k, v in node.value:
        value[loader.construct_object(k)] = loader.construct_object(v)

    return value


class SafeSchemaLoader(yaml.SafeLoader):
    pass


SafeSchemaLoader.add_constructor(u'tag:yaml.org,2002:map', orderedDict_constructor)

def LoadSchema(fileStream):
    return yaml.load(fileStream, Loader=SafeSchemaLoader)


def GetEditorSchema(schema):
    editorSchema = schema['editorFileSchema']
    return schema['schemas'][editorSchema]


def GetUnOptimizedRuntimeSchema(schema):
    runtimeSchema = schema['runtimeSchema']
    return schema['schemas'][runtimeSchema]


def GetNewIDForSchemaObject(schemaNode):
    return None