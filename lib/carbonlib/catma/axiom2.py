from catmaConfig import *
from axiom import BaseType, Int, Float, Bool, String, Unicode, Enumerate, URL, AxiomError, Value
from axiom import GetAttributeID
from . import enum
from . import units
from const import TYPEID_NONE
import re
import weakref
import catmaDB
import axiomUtil
import copy
import catmaTypeVerify
FLAG_RangeCheckEnabled = 1
FLAG_DumpValueRange = 2
FLAG_EnforcingNamingConvention = 3

def TypeOrderComparer(type1, type2):
    return cmp(type1.order, type2.order)



def GetPathList(pathList):
    if isinstance(pathList, list):
        return pathList
    if isinstance(pathList, basestring):
        return str(pathList).split('.')
    raise AxiomError('Path list must be list or string: %s' % `pathList`)



def BuildPath(parentPath, currPath):
    if parentPath:
        return '%s.%s' % (parentPath, currPath)
    return currPath



def InheriteParentAttributeFlag(currFlag, parentFlag):
    newFlag = currFlag
    for flag in ATTRIB_FLAGS:
        if flag & parentFlag != 0 and flag & INHERITABLE_ATTRIB_FLAGS != 0:
            newFlag |= flag

    return newFlag



class TypeReference(Int):
    __slots__ = String.__slots__ + ['_ax2', 'allowedClasses']

    def __init__(self, ax2, className, name):
        String.__init__(self, ax2, className, name)
        self._ax2 = ax2
        self.allowedClasses = None



    def GetAllowedValues(self, valueContainer = None):
        classNames = self.allowedClasses.split('+') if self.allowedClasses else None
        allowedTypes = self._ax2.SelectFolderByClass(classNames, True)
        typeIDs = [TYPEID_NONE]
        for aType in allowedTypes:
            typeIDs.append(aType.GetFolderID())

        return typeIDs



    def GetAdditionalAttFlag(self):
        return ATTRIB_FLAGS.TYPE_REF




class TypeInstance(BaseType):
    __slots__ = BaseType.__slots__ + ['actualType']

    def __init__(self, ax2, actualType):
        BaseType.__init__(self, ax2, '', '')
        self.actualType = actualType
        self.group = actualType.GetGroup()



    def __repr__(self):
        args = (self.actualType,
         self.group,
         self.IsSet(),
         self.IsPublished())
        return 'actual type: <%s>, group: %s, is set: %s, published: %s' % args



    def _HasFlag(self, flag, considerClassFlag):
        hasFlag = False
        if considerClassFlag:
            hasFlag = self.actualType.attributeFlag & flag != 0
        return hasFlag | self.attributeFlag & flag != 0



    def GetBaseType(self):
        return self.actualType



    def FromString(self, strValue):
        return self.actualType.FromString(strValue)



    def ToString(self, rawValue):
        return self.actualType.ToString(rawValue)



    def FromValue(self, rawValue):
        return self.actualType.FromValue(rawValue)




class ClassType(BaseType):
    __slots__ = BaseType.__slots__ + ['_members', '_ax2', 'standalone']
    isInstantiatable = False

    @property
    def type(self):
        return self.className



    @property
    def protoType(self):
        return self.className



    def __init__(self, ax2, className, name):
        BaseType.__init__(self, ax2, className, name)
        self._members = {}
        self._ax2 = ax2
        self.standalone = False
        self.attributeFlag = DEFAULT_ATTRIB_FLAGS | ax2.DEFAULT_CUSTOM_FLAGS_FOR_CLASS_TYPE



    def DumpClassInfo(self, db):
        myInfo = db._CreateClassInfo(self.className)
        for (attName, typeInstance,) in self._members.iteritems():
            if typeInstance.GetBaseType().IsSimpleType():
                classInfo = typeInstance.GetBaseType().serialUID
            else:
                classInfo = db._CreateClassInfo(typeInstance.GetBaseType().className)
            myInfo._AddMember(attName, classInfo, typeInstance.GetAttributeFlag())




    def GetMembers(self):
        return self._members



    def HasAvailableClassMember(self):
        for (attName, typeInstance,) in self._members.items():
            if not typeInstance.GetBaseType().IsRemoved():
                return True

        return False



    def AddMember(self, attrName, **kw):
        defaultValue = None
        try:
            attrName = attrName.replace(' ', '*', 1)
            (typeName, attrName,) = attrName.split('*', 1)
        except Exception:
            raise AxiomError("ClassType AddMember: 'name'(%s), need more than 1 value to unpack" % attrName)
        attrName = attrName.replace(' ', '')
        try:
            (attrName, defaultValue,) = attrName.split('=')
        except Exception:
            pass
        if attrName == '':
            raise AxiomError('ClassType AddMember: attribute name cannot be empty!')
        elif defaultValue == '':
            raise AxiomError('ClassType AddMember: default cannot be empty!')
        if attrName in self._members:
            raise AxiomError('member %s already defined in class %s' % (self.className, attrName))
        typeDef = self._ax2.GetType(typeName)
        kw['defaultValue'] = defaultValue
        if 'attributeFlag' not in kw:
            kw['attributeFlag'] = self.attributeFlag
        if typeDef.isInstantiatable:
            instanceType = copy.copy(typeDef)
            instanceType.properties = copy.copy(instanceType.properties)
        else:
            instanceType = TypeInstance(self._ax2, typeDef)
        for (k, v,) in kw.items():
            setattr(instanceType, k, v)

        self._members[attrName] = instanceType



    def HasClassMember(self):
        for (memberName, memberInstance,) in self.GetMembers().items():
            if isinstance(memberInstance.GetBaseType(), ClassType):
                return True

        return False



    def PopulateValueContainer(self, valueContainer, parentName):
        for (attName, typeInstance,) in self._members.items():
            if typeInstance.IsPublished() and not typeInstance.IsRemoved():
                attName = BuildPath(parentName, attName)
                if typeInstance.GetBaseType().IsSimpleType():
                    if typeInstance.IsSet():
                        dummyValueName = '%s.0' % attName
                        valueContainer.EditValue(dummyValueName, typeInstance, typeInstance.defaultValue, None, VALUE_INIT, None)
                        valueContainer.EditValue(dummyValueName, typeInstance, None, None, VALUE_REMOVE, None)
                    else:
                        valueContainer.EditValue(attName, typeInstance, typeInstance.defaultValue, None, VALUE_INIT, None)
                else:
                    newAttName = attName
                    if typeInstance.IsSet():
                        newAttName = '%s.0' % newAttName
                    typeInstance.GetBaseType().PopulateValueContainer(valueContainer, newAttName)
                    if typeInstance.IsSet():
                        newContainer = valueContainer.FindValueOrContainer(attName, False)
                        if newContainer:
                            newContainer._childContainer = {}
                            newContainer._values = {}




    def GetAttributeTypeInfo(self, attributeNameList, currGroup = None):
        first = attributeNameList[0]
        if currGroup is None:
            currGroup = self.group
        typeInfo = None
        if first in self._members:
            member = self._members[first]
            if member.GetGroup() != self._ax2.DEFAULT_GROUP:
                currGroup = member.GetGroup()
            attributeNameList.pop(0)
            if member.IsSet() and attributeNameList:
                elementName = attributeNameList[0]
                if not member.GetBaseType().IsSimpleType():
                    if elementName not in member.GetBaseType()._members:
                        attributeNameList.pop(0)
                else:
                    attributeNameList.pop(0)
            if not attributeNameList:
                typeInfo = {'typeInstance': member,
                 'group': currGroup}
            elif member.GetBaseType().IsSimpleType():
                raise AxiomError('Invalid attribute name for simple type: %s' % attributeNameList)
            typeInfo = member.GetBaseType().GetAttributeTypeInfo(attributeNameList, currGroup)
        return typeInfo



    def GetAttributeInstance(self, attributeName):
        for (memberName, memberInstance,) in self.GetMembers().items():
            if memberName == attributeName or memberInstance.oldName == attributeName:
                return (memberName, memberInstance)

        return (None, None)




def IsValidNodeName(nodeName):
    if nodeName is None or len(nodeName) == 0:
        raise AxiomError('Node name cannot be empty or None: %s' % nodeName)
    if '.' in nodeName:
        raise AxiomError("Node name cannot contain '.': %s" % nodeName)
    return True



class ValueContainer(object):
    __slots__ = ['_values',
     '_childContainer',
     '_hierarchical',
     '_parent',
     '_name',
     '_typeInstance',
     '_folderNode',
     'setElementIndex',
     '_combinedGroups',
     '_rootClass']

    def __init__(self, parent, hierarchical, name, folderNode):
        self._values = {}
        self._childContainer = {}
        self._hierarchical = hierarchical
        self._parent = parent
        self._name = name
        self._typeInstance = None
        self._folderNode = folderNode
        self._combinedGroups = []
        self.setElementIndex = None
        self._rootClass = None



    def GetAxiomFlag(self, flag):
        return self._folderNode.GetAxiomFlag(flag)



    def GetReferencedTypes(self):
        allReference = []
        containerName = self.GetFullyQualifiedName()
        for (attName, value,) in self._values.iteritems():
            attFullName = BuildPath(containerName, attName)
            if isinstance(value.valueType.GetBaseType(), TypeReference) and value.calculated:
                referencedFolder = self._folderNode._ax2.GetNodeByID(value.calculated) if value.calculated != TYPEID_NONE else None
                if referencedFolder and referencedFolder.IsType():
                    allReference.append((attFullName, referencedFolder.GetNodeName()))

        for childContainer in self._childContainer.itervalues():
            allReference.extend(childContainer.GetReferencedTypes())

        return allReference



    def Verify(self, errorContainer):
        containerName = self.GetFullyQualifiedName()
        for (attName, value,) in self._values.iteritems():
            attFullName = BuildPath(containerName, attName)
            if value.calculated is None and self._folderNode.IsType():
                errorContainer.AddError(axiomUtil.ERROR_VALUE_NOT_COMPLETE, attFullName, value)
            if isinstance(value.valueType.GetBaseType(), TypeReference) and value.calculated:
                ax2 = self._folderNode._ax2
                if not ax2.GetNodeByID(value.calculated):
                    errorContainer.AddError(axiomUtil.ERROR_INVALID_TYPE_REFERENCE, attFullName, value)

        for childContainer in self._childContainer.itervalues():
            childContainer.Verify(errorContainer)




    def AddGroup(self, group):
        if group not in self._combinedGroups:
            self._combinedGroups.append(group)
        if self._parent:
            self._parent.AddGroup(group)



    def HasGroup(self, group):
        return group in self._combinedGroups



    def IsSetType(self):
        typeInstance = self.GetTypeInstance()
        if typeInstance and typeInstance.IsSet():
            return not self.IsSetElement()
        return False



    def IsSetElement(self):
        if self._parent:
            return self._parent.IsSetType()
        return False



    def GetParentContainer(self):
        return self._parent



    def GetValues(self):
        return self._values



    def GetTypeInstance(self):
        if not self._typeInstance:
            fullyQualifiedName = self.GetFullyQualifiedName()
            try:
                typeInfo = self._folderNode.GetAttributeTypeInfo(fullyQualifiedName)
                if typeInfo is not None:
                    self._rootClass = typeInfo['rootClass']
                    self._typeInstance = typeInfo['typeInstance']
            except Exception:
                raise AxiomError("Can't get type instance for value container: <%s>" % fullyQualifiedName)
        return self._typeInstance



    def GetAllValues(self, values, recursive, fullyQualifiedAttributeName):
        nodeName = self.GetFullyQualifiedName()
        for (attName, value,) in self._values.items():
            if fullyQualifiedAttributeName:
                attName = nodeName + '.' + attName if nodeName != '' else attName
            values.append((attName, value))

        if recursive:
            for child in self._childContainer.values():
                child.GetAllValues(values, recursive, fullyQualifiedAttributeName)




    def GetAllContainer(self, containers, recursive):
        containers.append(self)
        if recursive:
            for child in self._childContainer.values():
                child.GetAllContainer(containers, recursive)




    def GetChildContainers(self):
        return self._childContainer



    def GetName(self):
        return self._name



    def EditValue(self, attributeName, typeInstance, value, modifier, action, parentValue):
        attributeNameList = GetPathList(attributeName)
        if not self._hierarchical or len(attributeNameList) == 1:
            if attributeName == '':
                raise AxiomError('Empty attribute name is not allowed.')
            currValue = None
            if typeInstance is None:
                raise AxiomError('typeInstance is None')
            if attributeName in self._values:
                currValue = self._values[attributeName]
                if action == VALUE_ADD and self._values[attributeName].lastAction in (VALUE_ADD, VALUE_EDIT):
                    raise AxiomError('Attribute value already existed: %s' % attributeName)
            if modifier in (MODIFIER_ADD, MODIFIER_MULTIPLY):
                if parentValue is None or parentValue.calculated is None:
                    raise AxiomError('Parent value is missing for add or multiply modifier: %s, parent value is %s' % (attributeName, parentValue))
            if (modifier is None or typeInstance is None or value is None) and action not in (VALUE_INIT, VALUE_PARENT_UPDATE, VALUE_REMOVE):
                raise AxiomError('Modifier(%s), Type Instance(%s) and Value(%s) must be valid when executing action: %s' % (modifier,
                 typeInstance,
                 value,
                 action))
            if currValue:
                group = currValue.group
            elif parentValue:
                group = parentValue.group
            else:
                typeInfo = self._folderNode.GetAttributeTypeInfo(BuildPath(self.GetFullyQualifiedName(), attributeName))
                group = typeInfo['group']
            if action == VALUE_PARENT_UPDATE:
                if currValue is None or currValue.modifier is None:
                    modifier = None
                    typeInstance = parentValue.valueType
                    value = parentValue.calculated
                else:
                    modifier = currValue.modifier
                    typeInstance = currValue.valueType
                    value = currValue.value
            elif action == VALUE_REMOVE:
                modifier = None
                typeInstance = currValue.valueType
                if parentValue:
                    value = parentValue.calculated
                else:
                    value = typeInstance.defaultValue
            if group is None:
                raise AxiomError('group is None when editing value, action: %s, attributeName: %s::%s' % (action, self.GetFullyQualifiedName(), attributeName))
            value = Value(typeInstance, value, modifier, '')
            value.group = group
            if modifier == MODIFIER_ADD:
                value.calculated = parentValue.calculated + value.value
            elif modifier == MODIFIER_MULTIPLY:
                value.calculated = parentValue.calculated * value.value
            if self.GetAxiomFlag(FLAG_RangeCheckEnabled):
                if typeInstance.range is not None and value.calculated is not None:
                    (rangeMin, rangeMax,) = typeInstance.range
                    if rangeMin is not None and value.calculated < rangeMin or rangeMax is not None and value.calculated > rangeMax:
                        raise AxiomError('attribute <%s> value <%s> out of range: [%s, %s]' % (BuildPath(self.GetFullyQualifiedName(), attributeName),
                         value.calculated,
                         rangeMin,
                         rangeMax))
            if action == VALUE_INIT:
                self.AddGroup(value.group)
            if parentValue:
                value.parentCalculated = parentValue.calculated
            value.lastAction = action
            self._values[attributeName] = value
            return value
        else:
            return self.EditValueHierarchical(attributeNameList, typeInstance, value, modifier, action, parentValue)



    def FindValueOrContainer(self, attributeName, findValue):
        attributeNameList = GetPathList(attributeName)
        attributeName = attributeNameList[0]
        if not self._hierarchical or len(attributeNameList) == 1:
            if findValue:
                if attributeName in self._values:
                    return self._values[attributeName]
            elif attributeName in self._childContainer:
                return self._childContainer[attributeName]
        elif attributeName in self._childContainer:
            attributeNameList.pop(0)
            return self._childContainer[attributeName].FindValueOrContainer(attributeNameList, findValue)



    def EditValueHierarchical(self, attributeNameList, typeInstance, value, modifier, action, parentValue):
        containerTypeInstance = self.GetTypeInstance()
        if containerTypeInstance and containerTypeInstance.IsRemoved():
            fullyQualifiedName = self.GetFullyQualifiedName()
            raise AxiomError("Container (%s) doesn't have the container (%s) in the folder (%s)" % (fullyQualifiedName, '.'.join(attributeNameList), self._folderNode.GetNodeName()))
        first = attributeNameList[0]
        if len(attributeNameList) == 1:
            return self.EditValue(first, typeInstance, value, modifier, action, parentValue)
        else:
            if first not in self._childContainer:
                if self.IsSetType():
                    self._CreateSetElement(first)
                else:
                    self._CreateChildContainer(first)
            attributeNameList.pop(0)
            return self._childContainer[first].EditValueHierarchical(attributeNameList, typeInstance, value, modifier, action, parentValue)



    def _CreateChildContainer(self, attributeNameList):
        if self._hierarchical:
            attributeNameList = GetPathList(attributeNameList)
            childName = attributeNameList.pop(0)
            if childName not in self._childContainer:
                child = ValueContainer(self, self._hierarchical, childName, self._folderNode)
                self._childContainer[childName] = child
            if attributeNameList:
                self._childContainer[childName]._CreateChildContainer(attributeNameList)



    def _CreateSetElement(self, elementName):
        containerTypeInstance = self.GetTypeInstance()
        if not containerTypeInstance.IsSet():
            raise AxiomError('_CreateSetElement: creating array element for non-array type is not allowed on attribute <%s>' % self.GetFullyQualifiedName())
        if containerTypeInstance.GetBaseType().IsSimpleType():
            self.EditValue(elementName, containerTypeInstance, None, None, VALUE_INIT, None)
        elif elementName in self._childContainer:
            raise AxiomError('_CreateSetElement: array element with index (%s) already existed on attribute <%s>' % (elementName, self.GetFullyQualifiedName()))
        self._CreateChildContainer(elementName)
        containerTypeInstance.GetBaseType().PopulateValueContainer(self._childContainer[elementName], '')
        self._folderNode._NotifySetElementUpdated(self.GetFullyQualifiedName(), elementName, SET_APPEND)



    def _HasEditedValues(self):
        for eachValue in self._values.values():
            if eachValue.modifier is not None:
                return True

        for childContainer in self._childContainer.values():
            if childContainer._HasEditedValues():
                return True

        return False



    def _DeleteSetElement(self, elementName, operation, onlyDeleteEmptyElement):
        containerFullName = self.GetFullyQualifiedName()
        doesClearAll = operation in (SET_CLEAR, SET_PARENT_CLEAR)
        removedElements = []
        for (attName, child,) in self._childContainer.items():
            if doesClearAll or attName == str(elementName):
                if onlyDeleteEmptyElement and child._HasEditedValues():
                    continue
                removedElements.append(attName)
                child.Destroy(self._folderNode._ax2, self._folderNode.GetFolderID())
                del self._childContainer[attName]
                if not doesClearAll:
                    break

        for (attName, value,) in self._values.items():
            if doesClearAll or attName == str(elementName):
                if onlyDeleteEmptyElement and value.modifier is not None:
                    continue
                if value.lastAction in (VALUE_ADD, VALUE_EDIT):
                    self._folderNode._ax2.NotifyValueDestroyed(self._folderNode.GetFolderID(), containerFullName + '.' + attName)
                removedElements.append(attName)
                del self._values[attName]
                if not doesClearAll:
                    break

        for elementName in removedElements:
            self._folderNode._NotifySetElementUpdated(self.GetFullyQualifiedName(), elementName, SET_DELETE)




    def _UpdateSetNames(self):
        fullAttributeName = self.GetFullyQualifiedName()
        if not self.IsSetType():
            raise AxiomError('_UpdateSetNames: attribute (%s) is not set' % fullAttributeName)
        elementNames = ''
        for setName in self._childContainer.keys():
            if not elementNames:
                elementNames = setName
            else:
                elementNames = '%s+%s' % (elementNames, setName)

        fullAttributeName = BuildPath(fullAttributeName, 'elementNames')
        self.Notify('OnAddValue', (self._folderNode.GetFolderID(), fullAttributeName, newValue))



    def EditSet(self, attributeName, elementName, operation):
        if not self._hierarchical:
            raise AxiomError('Array edit is not supported in non-hierarchical mode yet')
        if not attributeName:
            typeInstance = self.GetTypeInstance()
            if not self.IsSetType():
                raise AxiomError('EditSet: attribute (%s) is not set, type instance: %s' % (attributeName, typeInstance))
            if operation is None:
                raise AxiomError('EditSet: operation is none.')
            if operation == SET_APPEND:
                self._CreateSetElement(elementName)
            elif operation in (SET_DELETE,
             SET_CLEAR,
             SET_PARENT_DELETE,
             SET_PARENT_CLEAR):
                self._DeleteSetElement(elementName, operation, operation in (SET_PARENT_DELETE, SET_PARENT_CLEAR))
            elif operation == SET_PARENT_APPEND:
                if elementName not in self._childContainer:
                    self._CreateSetElement(elementName)
        else:
            attributeNameList = GetPathList(attributeName)
            first = attributeNameList.pop(0)
            if first not in self._childContainer:
                raise AxiomError("EditSet: can't find child container: %s" % first)
            child = self._childContainer[first]
            child.EditSet(attributeNameList, elementName, operation)



    def GetFullyQualifiedName(self, treatSetAsArray = False):
        parentName = ''
        myName = self._name
        if self._parent:
            parentName = self._parent.GetFullyQualifiedName(treatSetAsArray)
            if self._parent.IsSetType() and treatSetAsArray:
                myName = str(self.setElementIndex)
        fullName = BuildPath(parentName, myName)
        return fullName



    def Destroy(self, ax2, folderID):
        for child in self._childContainer.values():
            child.Destroy(ax2, folderID)

        del self._childContainer
        containerName = self.GetFullyQualifiedName()
        for (attName, value,) in self._values.items():
            if value.lastAction in (VALUE_ADD, VALUE_EDIT):
                ax2.NotifyValueDestroyed(folderID, BuildPath(containerName, attName))

        del self._values



    def CopyValues(self, otherContainer):
        parentFolderNode = self._folderNode._parentNode
        containerName = self.GetFullyQualifiedName()
        otherName = otherContainer.GetFullyQualifiedName()
        ax2 = self._folderNode._ax2
        folderPath = self._folderNode.GetPath()
        if containerName != otherName:
            raise AxiomError('CopyValues: copying values between 2 different containers: %s and %s' % (containerName, otherName))
        for (attName, attValue,) in otherContainer._values.items():
            if attValue.modifier:
                ax2.EditValue(folderPath, BuildPath(containerName, attName), attValue.value, attValue.modifier, VALUE_EDIT)

        for (childName, childContainer,) in otherContainer._childContainer.items():
            if childName not in self._childContainer:
                ax2.EditSet(folderPath, containerName, childName, SET_APPEND)
            self._childContainer[childName].CopyValues(otherContainer._childContainer[childName])




    def _TryDumpTags(self, db):
        tagsDumped = False
        if self._name == 'mTags' and isinstance(self.GetTypeInstance(), TypeReference):
            tagsDumped = True
            dbEntry = db._GetFolder(self._folderNode.GetPath())
            for value in self._values.itervalues():
                if value.modifier:
                    dbEntry._AddTag(value.calculated)

        return tagsDumped



    def DumpValues(self, db, parentAttFlag, includeNullVaue):
        if self._TryDumpTags(db):
            return 
        folderPath = self._folderNode.GetPath()
        containerName = self.GetFullyQualifiedName(True)
        attNames = self._values.keys()
        if SORT_VALUE_NAMES:
            attNames.sort()
        setElementIndex = self.IsSetType()
        elementIndex = 0
        dumpValueRange = self.GetAxiomFlag(FLAG_DumpValueRange)
        valueObjectClass = catmaDB.ValueObjectRangeInfo if dumpValueRange else catmaDB.ValueObject
        for attName in attNames:
            value = self._values[attName]
            skipValue = True
            if value.modifier:
                skipValue = False
            elif value.valueType.defaultValue is not None:
                parentFolder = self._folderNode.GetParentNode()
                if parentFolder:
                    containerOrgName = self.GetFullyQualifiedName(False)
                    skipValue = parentFolder.FindValueOrContainer(BuildPath(containerOrgName, attName), True) is not None
                else:
                    skipValue = False
            elif includeNullVaue:
                skipValue = False
            if not skipValue and (value.calculated is not None or includeNullVaue):
                attFullName = BuildPath(containerName, attName)
                typeInfo = self._folderNode.GetAttributeTypeInfo(attFullName)
                if not typeInfo:
                    raise AxiomError("Can't get type instance when dumping values in container <%s> for attribute <%s>" % (self.GetFullyQualifiedName(), attName))
                if setElementIndex:
                    attFullName = BuildPath(containerName, elementIndex)
                valueTypeInstance = typeInfo['typeInstance']
                attFlag = InheriteParentAttributeFlag(valueTypeInstance.GetAttributeFlag(), parentAttFlag)
                additionalFlag = valueTypeInstance.GetBaseType().GetAdditionalAttFlag()
                if additionalFlag:
                    attFlag = attFlag | additionalFlag
                exportedValue = valueTypeInstance.GetBaseType().GetExportedValue(value.calculated)
                db._AddValue(folderPath, attFullName, valueObjectClass(exportedValue, attFlag, valueTypeInstance.range))
                elementIndex += 1

        attNames = self._childContainer.keys()
        if SORT_VALUE_NAMES:
            attNames.sort()
        parentFolderNode = self._folderNode._parentNode
        parentNodeContainer = parentFolderNode.FindValueOrContainer(containerName, False)
        elementIndex = len(parentNodeContainer._childContainer) if parentNodeContainer else 0
        for childName in attNames:
            child = self._childContainer[childName]
            if setElementIndex:
                if child.setElementIndex is None:
                    self._folderNode.SetElementIndex(elementIndex, child.GetFullyQualifiedName())
                    elementIndex += 1
            else:
                child.setElementIndex = None
            attFullName = BuildPath(containerName, childName)
            typeInfo = self._folderNode.GetAttributeTypeInfo(attFullName)
            if not typeInfo:
                raise AxiomError("Can't get type instance when dumping values in container <%s> for attribute <%s>" % (self.GetFullyQualifiedName(), attName))
            valueTypeInstance = typeInfo['typeInstance']
            child.DumpValues(db, InheriteParentAttributeFlag(valueTypeInstance.GetAttributeFlag(), parentAttFlag), includeNullVaue)





class FolderNode(object):
    __slots__ = ['_ID',
     '_path',
     '_classes',
     '_text',
     '_isType',
     '_subNodes',
     '_ax2',
     '_nodeName',
     '_parentNode',
     '_valueContainer']

    def __init__(self, ax2, path):
        self._ID = None
        self._path = path
        self._nodeName = None
        self._classes = []
        self._text = ''
        self._isType = False
        self._parentNode = None
        self._subNodes = {}
        self._ax2 = ax2
        self._valueContainer = ValueContainer(None, HIERARCHICAL_VALUE_CONTAINER, '', self)



    def __repr__(self):
        args = (`(self._ID)`,
         `(self._path)`,
         `(self._classes)`,
         self._isType,
         self._text)
        return '<Entry id=%s, path=%s, classes=%s, isType=%s, text=%s>' % args



    def GetAxiomFlag(self, flag):
        return self._ax2.GetFlag(flag)



    def Verify(self, errors):
        errorContainer = axiomUtil.AxiomDataError(self.GetPath())
        self._valueContainer.Verify(errorContainer)
        if errorContainer.Shrink():
            errors[self.GetPath()] = errorContainer
        else:
            del errorContainer
        for childNode in self._subNodes.values():
            childNode.Verify(errors)




    def GetParentNode(self):
        return self._parentNode



    def GetSubNodes(self):
        return self._subNodes



    def GetFolderID(self):
        return self._ID



    def GetPath(self):
        return self._path



    def GetNodeName(self):
        return self._nodeName



    def GetClasses(self):
        return self._classes



    def IsType(self):
        return self._isType



    def GetValueContainer(self):
        return self._valueContainer



    def IsRootFolder(self):
        return self._path == ''



    def SetElementIndex(self, elementIndex, containerName):
        container = self.FindValueOrContainer(containerName, False)
        if container:
            container.setElementIndex = elementIndex
            for subNode in self._subNodes:
                self._subNodes[subNode].SetElementIndex(elementIndex, containerName)




    def FindValueOrContainer(self, attributeName, findValue):
        value = self._valueContainer.FindValueOrContainer(attributeName, findValue)
        if value is None and self._parentNode:
            value = self._parentNode.FindValueOrContainer(attributeName, findValue)
        return value



    def _GetAllValues(self):
        values = []
        self._valueContainer.GetAllValues(values, True, True)
        return values



    def _GetAllValueContainers(self):
        containers = []
        self._valueContainer.GetAllContainer(containers, True)
        return containers



    def _SetPath(self, path):
        self._path = path



    def _SetNodeName(self, nodeName):
        self._nodeName = nodeName



    def _SetIsType(self, isType):
        self._isType = isType



    def _SetClasses(self, classes):
        self._classes = classes



    def AddClasses(self, classes):
        self._classes.extend(classes)



    def GetClassByAttrName(self, attName):
        for eachClass in self._classes:
            members = eachClass.GetMembers()
            for eachMember in members:
                if attName == eachMember or attName == members[eachMember].oldName:
                    return eachClass





    def AddChild(self, pathList, folderID = 0, classes = [], folderText = '', isType = False):
        pathList = GetPathList(pathList)
        if folderID is None:
            raise AxiomError('AddChild: folderID cannot be none.')
        if classes is None:
            raise AxiomError('AddChild: classes cannot be none')
        if self._isType:
            raise AxiomError('Adding type or folder under type is not allowed: %s' % self._path)
        nodeName = pathList[0]
        if len(pathList) > 1:
            if nodeName not in self._subNodes:
                raise AxiomError("Couldn't find child with name: %s" % nodeName)
            pathList.pop(0)
            return self._subNodes[nodeName].AddChild(pathList, folderID, classes, folderText, isType)
        if self.GetAxiomFlag(FLAG_EnforcingNamingConvention):
            filterName = 'typeNameConvention' if isType else 'folderNameConvention'
            regex = self._valueContainer.FindValueOrContainer(filterName, True)
            if regex and regex.calculated and not re.match(regex.calculated, nodeName):
                raise AxiomError("CATMA name '%s' does not conform to regular expression '%s'" % (nodeName, regex.calculated))
        if IsValidNodeName(nodeName):
            for childName in self._subNodes.keys():
                if childName.lower() == nodeName.lower():
                    raise AxiomError('Node with name already exists: %s' % nodeName)

            if self._parentNode is None:
                path = nodeName
            else:
                path = self._path + '.' + nodeName
            actualClasses = []
            for classname in classes:
                if classname:
                    actualClass = self._ax2.GetType(classname)
                    if not isinstance(actualClass, ClassType):
                        raise AxiomError('Invalid class name: %s' % classname)
                    if not actualClass.standalone:
                        raise AxiomError('Only standalone classes can be added, this one is not: %s' % classname)
                    actualClasses.append(actualClass)

            for eachClass in self._classes:
                if eachClass not in actualClasses:
                    actualClasses.append(eachClass)

            classNames = set((eachClass.className for eachClass in actualClasses))
            if 'Tag' in classNames:
                classNames.discard('Tag')
                classNames.discard('AuthorAssist')
                if classNames:
                    raise AxiomError("'Tag' class is not allowed to be used with other classes: %s" % classNames)
            if not actualClasses and isType:
                raise AxiomError('Adding type with no class is not allowed: %s' % pathList)
            child = self._ax2._CreateFolderNode(path, folderID)
            child._SetClasses(actualClasses)
            child._text = folderText
            child._isType = isType
            child._nodeName = nodeName
            child._parentNode = self
            self._subNodes[nodeName] = child
            child.PopulateValueContainer()
            allValues = self._GetAllValues()
            for (attName, value,) in allValues:
                child._NotifyParentValueUpdated(attName, value)

            return child



    def Copy(self, otherNode):
        self._valueContainer.CopyValues(otherNode._valueContainer)
        for (childName, childNode,) in otherNode._subNodes.iteritems():
            pathList = BuildPath(self._path, childName)
            classNames = ''
            for eachClass in childNode._classes:
                if not classNames:
                    classNames = eachClass.className
                else:
                    classNames = '%s+%s' % (classNames, eachClass.className)

            newNode = self._ax2.AddFolder(pathList, None, classNames, '', childNode.IsType())
            newNode.Copy(childNode)




    def GetChild(self, pathList):
        if not pathList:
            return self
        pathList = GetPathList(pathList)
        nodeName = pathList.pop(0)
        if nodeName not in self._subNodes:
            raise AxiomError("Couldn't find child with name: <%s>" % nodeName)
        return self._subNodes[nodeName].GetChild(pathList)



    def _NotifyParentValueUpdated(self, attributeName, parentValue, dbType = None):
        self.EditValue(attributeName, None, None, VALUE_PARENT_UPDATE, parentValue, dbType)



    def EditValue(self, attributeName, value, modifier, action, parentValue = None, dbType = None):
        if parentValue is None and self._parentNode:
            parentValue = self._parentNode.FindValueOrContainer(attributeName, True)
        attributeNameList = GetPathList(attributeName)
        typeInfo = self.GetAttributeTypeInfo(attributeNameList)
        if not typeInfo:
            raise AxiomError('Attribute(%s) does not exist in node: %s' % (attributeNameList, self._path))
        typeInstance = typeInfo['typeInstance']
        if False and dbType and typeInstance.GetBaseType().storageType != dbType:
            raise AxiomError("Attribute(%s) does not have the same type as DB's type: %s" % (attributeName, dbType))
        if not typeInstance.IsRemoved():
            newValue = self._valueContainer.EditValue(attributeName, typeInstance, value, modifier, action, parentValue)
            if newValue:
                for child in self._subNodes.values():
                    child._NotifyParentValueUpdated(attributeName, newValue, dbType)

            return newValue
        raise AxiomError('Attribute(%s) has been removed in node: %s' % (attributeName, self._path))



    def EditSet(self, attributeName, elementName, operation):
        attributeNameList = GetPathList(attributeName)
        typeInfo = self.GetAttributeTypeInfo(attributeNameList)
        if not typeInfo:
            raise AxiomError('Attribute(%s) does not exist in node: %s' % (attributeNameList, self._path))
        typeInstance = typeInfo['typeInstance']
        if typeInstance.IsRemoved():
            return 
        if not typeInstance.IsSet():
            raise AxiomError('Attribute(%s) is not array' % attributeNameList)
        self._valueContainer.EditSet(attributeName, elementName, operation)



    def _NotifySetElementUpdated(self, attributeName, elementName, operation):
        for child in self._subNodes.values():
            child.EditSet(attributeName, elementName, PARENT_SET_OPERATION[operation])




    def GetAttributeTypeInfo(self, attributeNameList):
        attributeNameList = GetPathList(attributeNameList)
        for eachClass in self._classes:
            typeInfo = eachClass.GetAttributeTypeInfo(attributeNameList)
            if typeInfo:
                typeInfo['rootClass'] = eachClass
                return typeInfo




    def GetClassIncludingAttr(self, attributeNameList):
        typeInfo = self.GetAttributeTypeInfo(attributeNameList)
        if typeInfo:
            return typeInfo['rootClass']
        else:
            return None



    def PopulateValueContainer(self):
        for eachClass in self._classes:
            if isinstance(eachClass, ClassType):
                eachClass.PopulateValueContainer(self._valueContainer, '')

        for child in self._subNodes.values():
            child.PopulateValueContainer()




    def Destroy(self):
        if self._parentNode:
            self._parentNode.NotifyChildDestroyed(self._nodeName)
        for child in self._subNodes.values():
            child.Destroy()

        del self._subNodes
        self._valueContainer.Destroy(self._ax2, self.GetFolderID())
        del self._valueContainer
        self._ax2.DeleteFolderNode(self)



    def NotifyChildDestroyed(self, childName):
        del self._subNodes[childName]



    def SelectFolderByClass(self, folders, classNames, onlyType):
        if not onlyType or self.IsType():
            myClasses = self.GetClassNames()
            myClasses = myClasses.split('+') if myClasses else []
            if not classNames or set(classNames) <= set(myClasses):
                folders.append(self)
                classNames = None
        for child in self._subNodes.itervalues():
            child.SelectFolderByClass(folders, classNames, onlyType)




    def DumpValues(self, db, includeNullVaue):
        classNames = set((classInfo.className for classInfo in self._classes))
        if classNames == set(['Tag', 'AuthorAssist']):
            if self.IsType():
                db._AddTag(self.GetNodeName(), self.GetFolderID())
        else:
            self._valueContainer.DumpValues(db, 0, includeNullVaue)



    def GetClassNames(self):
        classNames = ''
        for eachClass in self._classes:
            if not classNames:
                classNames = eachClass.className
            else:
                classNames = '%s+%s' % (classNames, eachClass.className)

        return classNames



    def IsPublished(self):
        isPublished = self.FindValueOrContainer('mIsPublished', True)
        return isPublished is None or isPublished.calculated or not self.IsType()



    def GetReferencedTypes(self):
        return self._valueContainer.GetReferencedTypes()




class Axiom2(object):

    def __init__(self, extraConfig):
        self._groups = getattr(extraConfig, 'GROUPS', enum.Enum('BUILTIN'))
        self._builtinGroup = getattr(extraConfig, 'BUILTIN_GROUP', self._groups[0])
        self._defaultGroup = getattr(extraConfig, 'DEFAULT_GROUP', self._groups[0])
        self._custonFlags = getattr(extraConfig, 'CUSTOM_FLAGS', enum.Enum('DUMMY'))
        self._defaultCustomFlags = getattr(extraConfig, 'DEFAULT_CUSTOM_FLAGS', self._custonFlags[0])
        self._defaultCustomFlagsForClassType = getattr(extraConfig, 'DEFAULT_CUSTOM_FLAGS_FOR_CLASS_TYPE', self._custonFlags[0])
        self._typeDefs = {}
        self._typeOrder = 0
        self._InitDefaultTypes()
        self._InitUnitTypes()
        self._folderNodes = {}
        self._folderNodesByID = {}
        self._typeNodes = {}
        self._rootNode = self._CreateFolderNode('', 0)
        self._rootNode._nodeName = 'Root'
        self.callbacks = weakref.WeakKeyDictionary()
        self._bsdChangeID = None
        self._bsdDesc = None
        self._AddBuiltinCatmaClasses()
        self._maxFolderID = 0
        self._runtimeFlags = {}
        self._InitRuntimeFlags()



    @property
    def GROUPS(self):
        return self._groups



    @property
    def BUILTIN_GROUP(self):
        return self._builtinGroup



    @property
    def DEFAULT_GROUP(self):
        return self._defaultGroup



    @property
    def CUSTOM_FLAGS(self):
        return self._custonFlags



    @property
    def DEFAULT_CUSTOM_FLAGS(self):
        return self._defaultCustomFlags



    @property
    def DEFAULT_CUSTOM_FLAGS_FOR_CLASS_TYPE(self):
        return self._defaultCustomFlagsForClassType



    def _InitDefaultTypes(self):
        self.CreateType('Int', Int)
        self.CreateType('Float', Float)
        self.CreateType('Bool', Bool)
        self.CreateType('String', String)
        self.CreateType('Unicode', Unicode)
        self.CreateType('TypeReference', TypeReference)
        self.CreateType('URL', URL)
        self.CreateType('Tag', standalone=True, forUE3=False)



    def _InitUnitTypes(self):
        self.CreateType('Meter', units.Meter)
        self.CreateType('Second', units.Second)
        self.CreateType('Kilogram', units.Kilogram)
        self.CreateType('Radian', units.Radian)



    def _InitRuntimeFlags(self):
        self.SetFlag(FLAG_RangeCheckEnabled, True)
        self.SetFlag(FLAG_DumpValueRange, False)
        self.SetFlag(FLAG_EnforcingNamingConvention, True)



    def SetFlag(self, flag, value):
        self._runtimeFlags[flag] = value



    def GetFlag(self, flag):
        return self._runtimeFlags.get(flag, None)



    def _AddBuiltinCatmaClasses(self):
        typeDef = self.CreateType('AuthorAssist', standalone=True, group=self.BUILTIN_GROUP, attributeFlag=0)
        typeDef.AddMember('String typeNameConvention = [a-z_][a-z0-9_]*$', caption='Type Name Filter', text='A regular expression that enforces the CATMA type name convention for the current branch.', group=self.BUILTIN_GROUP, attributeFlag=ATTRIB_FLAGS.PUBLISHED)
        typeDef.AddMember('String folderNameConvention = [A-Z][A-Za-z0-9]*$', caption='Folder Name Filter', text='A regular expression that enforces the CATMA folder name convention for the current branch.', group=self.BUILTIN_GROUP, attributeFlag=ATTRIB_FLAGS.PUBLISHED)
        typeDef.AddMember('URL nameConventionURL = http://dustwiki/index.php/CATMA_TypeNamingConvention', caption='Naming Conventions Reference', group=self.BUILTIN_GROUP, attributeFlag=ATTRIB_FLAGS.PUBLISHED)
        typeDef.AddMember('TypeReference mTags', caption='Tags', allowedClasses='Tag', group=self.BUILTIN_GROUP, attributeFlag=ATTRIB_FLAGS.PUBLISHED | ATTRIB_FLAGS.IS_SET)
        self._rootNode.AddClasses([typeDef])



    def GetTypeDefs(self):
        return self._typeDefs



    def GetType(self, typeName):
        axiomType = None
        if typeName in self._typeDefs:
            axiomType = self._typeDefs[typeName]
        if not axiomType:
            raise AxiomError('Invalid class name: %s' % typeName)
        return axiomType



    def CreateType(self, typeName, typeClass = ClassType, **kw):
        if typeName == '':
            raise RuntimeError('className cannot be empty string')
        if typeName in self._typeDefs:
            raise AxiomError('Type already defined: %s' % typeName)
        if not issubclass(typeClass, BaseType):
            raise AxiomError('Type class must be a sub class of BaseType: %s' % typeClass)
        newType = typeClass(self, typeName, '')
        newType.order = self._typeOrder
        self._typeOrder += 1
        for (k, v,) in kw.items():
            setattr(newType, k, v)

        self._typeDefs[typeName] = newType
        return newType



    def _CreateFolderNode(self, path, folderID):
        if path in self._folderNodes:
            raise AxiomError('Folder with path <%s> already exists' % path)
        if folderID in self._folderNodesByID:
            raise AxiomError('Folder with id <%d> already exists' % folderID)
        newNode = FolderNode(self, path)
        newNode._path = path
        newNode._ID = folderID
        self._folderNodes[path] = newNode
        self._folderNodesByID[folderID] = newNode
        return newNode



    def GetRootNode(self):
        return self._rootNode



    def GetNodeByClassName(self, className, typeOnly):
        nodes = []
        classInfo = self.GetType(className)
        for folderNode in self._folderNodes.itervalues():
            if not typeOnly or folderNode.IsType():
                if classInfo in folderNode._classes:
                    nodes.append(folderNode)

        return nodes



    def GetNodeByPath(self, path):
        return self._folderNodes.get(path, None)



    def GetNodeByID(self, folderID):
        return self._folderNodesByID.get(folderID, None)



    def GetTypeNode(self, typeName):
        if typeName in self._typeNodes:
            return self._typeNodes[typeName]



    def GetAvailableClassNames(self):
        classes = []
        for (className, classType,) in self._typeDefs.iteritems():
            if isinstance(classType, ClassType):
                if classType.standalone:
                    classes.append(className)

        classes.sort()
        return classes



    def AddFolder(self, path, folderID = None, classNames = None, folderText = '', isType = False, copyFrom = ''):
        copySource = None
        if copyFrom:
            typeName = copyFrom.rsplit('.', 1)[-1]
            copySource = self.GetTypeNode(typeName)
        pathList = GetPathList(path)
        folderName = pathList[(len(pathList) - 1)]
        if isType and folderName in self._typeNodes:
            raise AxiomError('AddFolder: Type with name <%s> already exists' % folderName)
        if folderID is None:
            self._maxFolderID += 1
            folderID = self._maxFolderID
        else:
            try:
                folderID = int(folderID) if type(folderID) != int else folderID
            except Exception:
                raise AxiomError("AddFolder: folderID '%s' is not correct." % str(folderID))
            if self._maxFolderID < folderID:
                self._maxFolderID = folderID
        if type(classNames) != str:
            raise AxiomError('AddFolder: classNames is not string type')
        classNameList = classNames.split('+')
        newFolderNode = self._rootNode.AddChild(pathList, folderID, classNameList, folderText, isType)
        if newFolderNode:
            entry = {}
            entry['ID'] = folderID
            entry['path'] = path
            entry['className'] = classNames
            entry['text'] = folderText
            entry['isType'] = isType
            if isType:
                self._typeNodes[folderName] = newFolderNode
            if copySource:
                newFolderNode.Copy(copySource)
            self.Notify('OnAddFolder', entry)
        return newFolderNode



    def RemoveFolder(self, path):
        if path and path not in self._folderNodes:
            raise AxiomError("RemoveFolder: '%s' doesn't exist" % path)
        folderNode = self.GetNodeByPath(path)
        folderNode.Destroy()



    def DeleteFolderNode(self, folderNode):
        self.Notify('OnRemoveFolder', {'ID': folderNode.GetFolderID()})
        if folderNode.IsType() and folderNode.GetNodeName() in self._typeNodes:
            del self._typeNodes[folderNode.GetNodeName()]
        del self._folderNodes[folderNode.GetPath()]
        del self._folderNodesByID[folderNode.GetFolderID()]



    def NotifyValueDestroyed(self, folderID, attributeName):
        self.Notify('OnRemoveValue', {'entryID': folderID,
         'attributeName': attributeName})



    def EditValue(self, path, attributeName, value, modifier, action, dbType = None):
        if path not in self._folderNodes:
            raise AxiomError("AddValue: '%s' does not exist" % path)
        if not path:
            raise AxiomError('AddValue: path name cannot be empty')
        folderNode = self._folderNodes[path]
        newValue = folderNode.EditValue(attributeName, value, modifier, action, dbType=dbType)
        if action == VALUE_REMOVE:
            self.Notify('OnRemoveValue', {'entryID': folderNode.GetFolderID(),
             'attributeName': attributeName})
        else:
            self.Notify('OnAddValue', (folderNode.GetFolderID(), attributeName, newValue))
        return newValue



    def EditSet(self, path, attribute, elementName, operation):
        if path not in self._folderNodes:
            raise AxiomError("EditSet: '%s' does not exist" % path)
        if not path:
            raise AxiomError('EditSet: path name cannot be empty')
        folderNode = self._folderNodes[path]
        folderNode.EditSet(attribute, elementName, operation)



    def SelectFolderByClass(self, classNames, onlyType = False):
        folders = []
        self._rootNode.SelectFolderByClass(folders, classNames, onlyType)
        if folders and not folders[0]:
            folders.pop(0)
        return folders



    def GetAllFolderNode(self):
        return self._folderNodes



    def GenerateTypeDefinition(self, entryPoint):
        entryPoint(self)



    def Notify(self, event, value):
        functionName = 'HandleAxiomCallback'
        for cb in self.callbacks.keys():
            fn = getattr(cb, functionName, None)
            if fn:
                fn(event, value)




    def RegisterCallback(self, callback, unregister = False):
        if not unregister:
            self.callbacks[callback] = 1
        elif callback in self.callbacks:
            del self.callbacks[callback]



    def EndUnitTest(self):
        self.Notify('OnEndUnitTest', [])



    def GenerateDB(self, db, exportOption = EXPORT_ALL, includeNullVaue = False):
        if exportOption not in (EXPORT_ALL, EXPORT_PUBLISHED, EXPORT_VERIFIED):
            raise AxiomError('Invalid export option: %s' % exportOption)
        if exportOption == EXPORT_VERIFIED:
            verifyRunner = catmaTypeVerify.CheckRunner()
            verifyRunner.CheckAll(self)
            errors = verifyRunner.GetErrors()
            verifyErrors = [ typeInstance.GetTypeName() for typeInstance in errors.iterkeys() ]
        else:
            verifyErrors = []
        for typeInfo in self._typeDefs.values():
            if isinstance(typeInfo, ClassType):
                typeInfo.DumpClassInfo(db)

        folderPaths = self._folderNodes.keys()
        folderPaths.sort()
        for folderPath in folderPaths:
            if folderPath:
                folder = self._folderNodes[folderPath]
                if (folder.IsPublished() or exportOption == EXPORT_ALL) and folder.GetNodeName() not in verifyErrors:
                    db._AddFolder(folderPath, folder.GetFolderID(), folder.GetClassNames(), folder.IsType(), folder.IsPublished())
                    folder.DumpValues(db, includeNullVaue)

        db._Cook()



    def Verify(self):
        errors = {}
        self._rootNode.Verify(errors)
        return errors



    def MoveFolderNode(self, oldPath, newParentPath):
        if oldPath == newParentPath:
            raise AxiomError('old path and the new parent path cannot be the same')
        if oldPath in newParentPath:
            raise AxiomError('parent path node cannot be moved to the child path node')
        node = self.GetNodeByPath(oldPath)
        nodeName = node.GetNodeName()
        oldParentNode = node.GetParentNode()
        newParentNode = self.GetNodeByPath(newParentPath)
        newPath = newParentPath + '.' + nodeName
        node._SetPath(newPath)
        del oldParentNode._subNodes[nodeName]
        newParentNode._subNodes[nodeName] = node
        del self._folderNodes[oldPath]
        self._folderNodes[newPath] = node
        entry = {'ID': node.GetFolderID(),
         'path': newPath}
        self.Notify('OnModifyFolderName', entry)
        for subNode in node._subNodes.itervalues():
            self.RenameFolderSubNode(subNode, oldPath, newPath)




    def RenameFolderNode(self, folderPath, newFolderName):
        node = self.GetNodeByPath(folderPath)
        oldFolderName = node.GetNodeName()
        if self.GetFlag(FLAG_EnforcingNamingConvention):
            filterName = 'typeNameConvention' if node.IsType() else 'folderNameConvention'
            regex = node.FindValueOrContainer(filterName, True)
            if regex and regex.calculated and not re.match(regex.calculated, newFolderName):
                raise AxiomError("CATMA name '%s' does not conform to regular expression '%s'" % (newFolderName, regex.calculated))
        if oldFolderName == newFolderName:
            raise AxiomError('the new folder name is the same as the old one')
        parentNode = node.GetParentNode()
        if not parentNode:
            raise AxiomError("couldn't find the parent node, are you trying to rename the root node?")
        if newFolderName in parentNode._subNodes:
            raise AxiomError('the parent node already has a child with the same name: <%s>' % newFolderName)
        if node.IsType() and newFolderName in self._typeNodes:
            raise AxiomError('RenameFolderNode: Type with name <%s> already exists' % newFolderName)
        oldPath = folderPath
        newPath = BuildPath(parentNode.GetPath(), newFolderName)
        node._SetPath(newPath)
        node._SetNodeName(newFolderName)
        del parentNode._subNodes[oldFolderName]
        parentNode._subNodes[newFolderName] = node
        if node.IsType():
            del self._typeNodes[oldFolderName]
            self._typeNodes[newFolderName] = node
        del self._folderNodes[oldPath]
        self._folderNodes[newPath] = node
        entry = {'ID': node.GetFolderID(),
         'path': newPath}
        self.Notify('OnModifyFolderName', entry)
        for subNode in node._subNodes.itervalues():
            self.RenameFolderSubNode(subNode, oldPath, newPath)




    def RenameFolderSubNode(self, node, oldPath, newPath):
        oldNodePath = node.GetPath()
        nodePath = oldNodePath.replace(oldPath, newPath)
        node._SetPath(nodePath)
        del self._folderNodes[oldNodePath]
        self._folderNodes[nodePath] = node
        entry = {}
        entry['ID'] = node.GetFolderID()
        entry['path'] = nodePath
        self.Notify('OnModifyFolderName', entry)
        for subNode in node._subNodes.itervalues():
            self.RenameFolderSubNode(subNode, oldPath, newPath)




    def AddClassesToFolder(self, folderPath, classNames):
        folderNode = self.GetNodeByPath(folderPath)
        if folderNode.IsType():
            raise AxiomError('Adding classes to type is not allowed, the type path is: %s' % folderPath)
        classNames = classNames.split('+')
        neededClasses = []
        for className in classNames:
            aClass = self.GetType(className)
            if not isinstance(aClass, ClassType):
                raise AxiomError('Invalid class name: %s' % className)
            if not aClass.standalone:
                raise AxiomError('Only standalone classes can be added, this one is not: %s' % className)
            if aClass not in folderNode._classes:
                neededClasses.append(aClass)

        if not neededClasses:
            return 
        folderNode.AddClasses(neededClasses)
        entry = {}
        entry['path'] = folderPath
        entry['className'] = folderNode.GetClassNames()
        self.Notify('OnModifyFolderClasses', entry)



    def GetReferencedTypes(self, folderPath):
        folderNode = self.GetNodeByPath(folderPath)
        return folderNode.GetReferencedTypes()



    def GetTypeReferencer(self, _typeName):
        if _typeName not in self._typeNodes:
            raise AxiomError('%s is not a valid type name' % _typeName)
        referencers = {}
        for (typeName, typeNode,) in self._typeNodes.iteritems():
            matches = []
            typeReferences = typeNode.GetReferencedTypes()
            for ref in typeReferences:
                if ref[1] == _typeName:
                    matches.append(ref[0])

            if matches:
                referencers[typeName] = matches

        return referencers



    def ChangeTypeToFolder(self, typeID, folderName):
        node = self.GetNodeByID(typeID)
        typeName = node.GetNodeName()
        if node.IsType() == 0:
            raise AxiomError('node is already a folder')
        parentNode = node.GetParentNod()
        if parentNode is None:
            path = folderName
        else:
            path = parentNode.GetPath() + '.' + folderName
            del parentNode._subNodes[typeName]
        del self._typeNodes[typeName]
        node._SetIsType(0)
        node._SetNodeName(folderName)
        node._SetPath(path)
        self._folderNodes[path] = node
        parentNode._subNodes[folderName] = node
        self.Notify('OnModifyIsType', {'ID': typeID,
         'path': path,
         'isType': 0})




