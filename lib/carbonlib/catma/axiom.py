from catmaConfig import *
import collections
import weakref
import functools
import os
import time
import inspect

class AxiomError(RuntimeError):
    pass

def Archive(ob):
    return [ getattr(ob, k) for k in ob.__slots__ ]



class BaseType(object):
    __slots__ = ['className',
     'name',
     'range',
     'text',
     'group',
     'modifyFlag',
     'oldName',
     'order',
     'defaultValue',
     'caption',
     'attributeFlag',
     'editorFlag',
     'properties']
    isModifiable = False
    isInstantiatable = True
    type = 'BaseType'
    storageType = None
    serialUID = 0
    FromString = str
    ToString = str
    FromValue = str

    def __init__(self, ax2, className, name):
        self.className = className
        self.name = name
        self.range = None
        self.text = None
        self.group = ax2.DEFAULT_GROUP
        self.modifyFlag = None
        self.oldName = None
        self.defaultValue = None
        self.caption = None
        self.attributeFlag = DEFAULT_ATTRIB_FLAGS | ax2.DEFAULT_CUSTOM_FLAGS
        self.editorFlag = None
        self.properties = {}



    def Nothing__getstate__(self):
        return Archive(self)



    def __getattr__(self, key):
        if key not in self.properties:
            raise AttributeError('No such attribute: {0}'.format(key))
        return self.properties[key]



    def __setattr__(self, key, value):
        if key in self.__slots__:
            object.__setattr__(self, key, value)
        else:
            self.properties[key] = value



    def __delattr__(self, key):
        if key in self.__slots__:
            object.__delattr__(self, key)
        else:
            del self.properties[key]



    @property
    def fullName(self):
        return '%s.%s' % (self.className, self.name)



    def Verify(self, check, text):
        if not check:
            raise RuntimeError('class %s: %s' % (self.__class__.__name__, text))



    def __repr__(self):
        args = (self.name,
         self.type,
         self.range,
         self.text,
         self.modifyFlag,
         self.oldName)
        return '"%s"(%s) range=%s, text=\'%s\', modifyFlag=\'%s\', oldName=\'%s\'' % args



    def GetAllowedValues(self, valueContainer = None):
        return None



    def GetAllowedModifiers(self):
        return []



    def GetAttributeFlag(self):
        return self.attributeFlag



    def IsSimpleType(self):
        return self.serialUID > 0



    def IsSet(self):
        return self._HasFlag(ATTRIB_FLAGS.IS_SET, False)



    def IsPublished(self):
        return self._HasFlag(ATTRIB_FLAGS.PUBLISHED, False)



    def IsModulized(self):
        return self._HasFlag(ATTRIB_FLAGS.MODULIZED, True)



    def IsExported(self):
        return self._HasFlag(ATTRIB_FLAGS.EXPORTED, False)



    def IsHiddenInEditor(self):
        return self._HasFlag(ATTRIB_FLAGS.HIDDEN, False)



    def IsRemoved(self):
        return self.modifyFlag == MODIFY_REMOVED



    def IsTypeChanged(self):
        return self.modifyFlag == MODIFY_TYPE_CHANGED



    def IsRenamed(self):
        return self.modifyFlag == MODIFY_RENAMED



    def _HasFlag(self, flag, considerClassFlag):
        return self.attributeFlag & flag != 0



    def GetBaseType(self):
        return self



    def GetGroup(self):
        return self.group



    def GetAdditionalAttFlag(self):
        return None



    def GetExportedValue(self, inValue):
        return inValue




class Int(BaseType):
    __slots__ = BaseType.__slots__
    isModifiable = True
    type = 'int'
    storageType = 'Int'
    serialUID = SIMPLE_TYPE_SERIAL_UIDS.INT
    FromString = long
    ToString = unicode
    FromValue = long

    def GetAllowedModifiers(self):
        return MODIFIER_ALL




class Float(BaseType):
    __slots__ = BaseType.__slots__ + ['precision']
    isModifiable = True
    type = 'float'
    storageType = 'Float'
    serialUID = SIMPLE_TYPE_SERIAL_UIDS.FLT
    FromString = float
    FromValue = float
    ToString = lambda self, value: '%.{0}f'.format(self.precision) % value

    def __init__(self, ax2, className, name):
        BaseType.__init__(self, ax2, className, name)
        self.precision = 3



    def GetAllowedModifiers(self):
        return MODIFIER_ALL




class Bool(BaseType):
    __slots__ = BaseType.__slots__
    isModifiable = True
    type = 'bool'
    storageType = 'Bool'
    serialUID = SIMPLE_TYPE_SERIAL_UIDS.BOOL
    FromString = lambda self, value: value not in ('false', 'False', 0)
    ToString = unicode
    FromValue = bool

    def GetAllowedValues(self, valueContainer = None):
        return [True, False]



    def GetAllowedModifiers(self):
        return [MODIFIER_BASE]




class String(BaseType):
    type = 'string'
    storageType = 'String'
    serialUID = SIMPLE_TYPE_SERIAL_UIDS.STR
    FromString = str
    ToString = str
    FromValue = str

    def GetAsHTML(self, value):
        pass



    def GetAllowedModifiers(self):
        return [MODIFIER_BASE]




class Unicode(BaseType):
    type = 'unicode'
    storageType = 'String'
    serialUID = SIMPLE_TYPE_SERIAL_UIDS.UNICODE
    FromString = unicode
    ToString = unicode
    FromValue = unicode

    def GetAsHTML(self, value):
        pass



    def GetAllowedModifiers(self):
        return [MODIFIER_BASE]




class Enumerate(BaseType):
    isInstantiatable = False
    type = 'enum'
    storageType = 'Enumerate'
    serialUID = SIMPLE_TYPE_SERIAL_UIDS.ENUM
    FromString = unicode
    ToString = unicode
    FromValue = unicode
    __slots__ = BaseType.__slots__ + ['elements']

    def __init__(self, ax2, className, name):
        BaseType.__init__(self, ax2, className, name)
        self.elements = {}



    def AddElement(self, elementName, description = None):
        if not elementName or not isinstance(elementName, str):
            raise AxiomError('Enum element name must be a valid string')
        if elementName in self.elements:
            raise AxiomError('Enum element already exists: %s' % elementName)
        if not description:
            description = elementName
        self.elements[elementName] = (len(self.elements), description)



    def GetElementDesc(self, elementName):
        if elementName not in self.elements:
            raise AxiomError('Enum element is not found: %s' % elementName)
        return self.elements[elementName][1]



    def GetAllowedValues(self, valueContainer = None):
        values = []
        for each in self.elements.keys():
            values.append(each)

        return values



    def GetAsHTML(self, value):
        pass



    def GetAllowedModifiers(self):
        return [MODIFIER_BASE]




class Value(object):
    __slots__ = ['valueType',
     'value',
     'calculated',
     'modifier',
     'path',
     'lastAction',
     'parentCalculated',
     'group']

    def __init__(self, valueType, strValue, modifier, path):
        self.modifier = modifier
        self.valueType = valueType
        if strValue is not None:
            self.value = self.GetValue(strValue)
            self.calculated = self.valueType.FromValue(self.value)
        else:
            self.value = None
            self.calculated = None
        self.path = path
        self.lastAction = None
        self.parentCalculated = None



    def Nothing__getstate__(self):
        return Archive(self)



    def GetActualType(self):
        if hasattr(self.valueType, 'actualType'):
            return self.valueType.actualType
        else:
            return self.valueType



    def GetValue(self, strValue):
        actualType = self.GetActualType()
        if self.modifier == MODIFIER_MULTIPLY and type(actualType) == Int:
            return float(strValue)
        else:
            return self.valueType.FromString(strValue)



    def __repr__(self):
        return '<Value Object: %s, %s - %s>' % (self.valueType, self.value, self.calculated)



    def ToString(self):
        return self.valueType.ToString(self.value)



    def GetModifierDescription(self):
        desc = ''
        operators = {MODIFIER_MULTIPLY: '*',
         MODIFIER_ADD: '+',
         MODIFIER_BASE: '='}
        if self.modifier is not None:
            desc = '%s %s' % (operators[self.modifier], self.value)
        return desc




class URL(String):
    pass

def GetAttributeID(title):
    id = hash(title)
    id = id & 16777215
    return id



