import re
import axiom
import axiom2
from catmaDB import CatmaDBError, CatmaValue
from catmaConfig import INCLUDE_ALL
ERROR_VALUE_NOT_COMPLETE = 100
ERROR_INVALID_TYPE_REFERENCE = 101
DATA_ERROR_ALL = {ERROR_VALUE_NOT_COMPLETE: 'Value Not Complete',
 ERROR_INVALID_TYPE_REFERENCE: 'Invalid Type Reference'}

class WildcardFolderValues(object):
    __slots__ = ['_path',
     '_filteredFolderNode',
     '_filteredAttrValues',
     '_groupNames',
     '_valueTypes']

    def __init__(self, path):
        self._path = path
        self._filteredFolderNode = None
        self._filteredAttrValues = {}
        self._groupNames = []
        self._valueTypes = []



    def SetFolderNode(self, folderNode):
        self._filteredFolderNode = folderNode



    def SetAttrValues(self, attrName, value):
        self._filteredAttrValues[attrName] = value



    def GetFolderNode(self):
        return self._filteredFolderNode



    def GetAttrValues(self):
        return self._filteredAttrValues



    def GetValueTypes(self):
        return self._valueTypes



    def HasAttributes(self):
        return len(self._filteredAttrValues) > 0



    def GetFilteredGroup(self):
        return self._groupNames



    def GetFolderAttrValuesString(self):
        retString = ''
        if self.HasAttributes():
            retString += self._path
            retString += ':'
            attrString = ''
            for attrName in self._filteredAttrValues.keys():
                attrString += '+' if attrString != '' else ''
                attrString += attrName

            retString += attrString
            retString += ';'
        return retString



    def CalFilterGroup(self):
        if type(self._filteredAttrValues) != dict:
            raise AxiomError('CalFilterGroup:: filteredAttrValueNodes is not the dict object.')
        self._groupNames = []
        for (attrName, attrValue,) in self._filteredAttrValues.items():
            if attrValue.group not in self._groupNames:
                self._groupNames.append(attrValue.group)




    def CalValueTypes(self):
        if type(self._filteredAttrValues) != dict:
            raise AxiomError('CalValueTypes:: filteredAttrValueNodes is not the dict object.')
        self._valueTypes = []
        for (attrName, attrValue,) in self._filteredAttrValues.items():
            typeStr = attrValue.valueType.GetBaseType().className
            if typeStr not in self._valueTypes:
                self._valueTypes.append(typeStr)





class ClassGroupInstance(object):
    __slots__ = ['classType', 'folderPaths', 'attrValues']

    def __init__(self, classType):
        self.classType = classType
        self.folderPaths = []
        self.attrValues = {}



    def AddFolderPath(self, path):
        if path not in self.folderPaths:
            self.folderPaths.append(path)



    def AddAttributeValue(self, attrName, value):
        if attrName not in self.attrValues:
            self.attrValues[attrName] = value



    def GetFolderPathStr(self):
        retStr = ''
        for path in self.folderPaths:
            retStr += '+' if retStr != '' else ''
            retStr += path

        return retStr



    def IsClassGroupMember(self, attributeNameList):
        attributeNameList = axiom2.GetPathList(attributeNameList)
        typeInfo = self.classType.GetAttributeTypeInfo(attributeNameList)
        return typeInfo is not None




class WildcardFilterResultInstance(object):
    __slots__ = ['_folderFilterString',
     '_attrFilterString',
     '_filteredFolderValues',
     '_valueFilterString',
     '_ax2',
     '_valueTypes',
     '_classGroupInstances']

    def __init__(self, axiom2, **kw):
        self._folderFilterString = ''
        self._attrFilterString = INCLUDE_ALL
        self._valueFilterString = INCLUDE_ALL
        self._filteredFolderValues = {}
        self._ax2 = axiom2
        self._valueTypes = []
        self._classGroupInstances = {}
        for (k, v,) in kw.items():
            setattr(self, k, v)




    def InitResult(self):
        self._filteredFolderValues = {}
        self._valueTypes = []
        self._classGroupInstances = {}



    def ResetFilterString(self, ax2, folderFilterStr, attrFilterStr, bForceReset = False, valueFilterStr = INCLUDE_ALL):
        if folderFilterStr != self._folderFilterString or attrFilterStr != self._attrFilterString or valueFilterStr != self._valueFilterString or bForceReset:
            self._ax2 = ax2
            self._folderFilterString = folderFilterStr
            self._attrFilterString = attrFilterStr
            self._valueFilterString = valueFilterStr
            self.Filter()



    def GetFilteredFolderString(self):
        retString = ''
        for folderPath in self._filteredFolderValues.keys():
            if self.HasAttributes(folderPath):
                retString += '+' if retString != '' else ''
                retString += folderPath

        return retString



    def GetFolderAttrValuesString(self):
        retString = ''
        for folderPath in self._filteredFolderValues.keys():
            retString += self._filteredFolderValues[folderPath].GetFolderAttrValuesString()

        return retString



    def GetFolderFilterString(self):
        return self._folderFilterString



    def GetAttrFilterString(self):
        return self._attrFilterString



    def GetValueFilterString(self):
        return self._valueFilterString



    def GetFolderValues(self):
        return self._filteredFolderValues



    def IsAllAttr(self):
        return self._attrFilterString == INCLUDE_ALL and self.IsAllValue()



    def IsAllValue(self):
        return self._valueFilterString == INCLUDE_ALL



    def GetAttrValues(self, folderPath):
        if folderPath not in self._filteredFolderValues:
            return {}
        return self._filteredFolderValues[folderPath].GetAttrValues()



    def GetFilteredGroup(self, folderPath):
        if folderPath not in self._filteredFolderValues:
            return []
        return self._filteredFolderValues[folderPath].GetFilteredGroup()



    def HasAttributes(self, folderPath):
        if folderPath not in self._filteredFolderValues:
            return False
        return self._filteredFolderValues[folderPath].HasAttributes()



    def GetUniqueType(self):
        if len(self._valueTypes) == 1:
            return self._valueTypes[0]



    def GetValueTypes(self):
        return self._valueTypes



    def GetClassGroupInstances(self):
        return self._classGroupInstances



    def __repr__(self):
        args = (self._folderFilterString, self._attrFilterString, self._valueFilterString)
        return '_folderFilterString: %s, _attrFilterString: %s, _valueFilterString: %s' % args



    def Filter(self):
        self.InitResult()
        self.FilterFolders()
        if self._attrFilterString != '':
            for (folderPath, filteredFolderValues,) in self._filteredFolderValues.items():
                self.FilterAttrValues(folderPath)
                self.CalFilterGroup(folderPath)
                self.CalValueTypes(folderPath)
                self.GroupByClass(folderPath)




    def GroupByClass(self, folderPath):
        if folderPath not in self._filteredFolderValues:
            raise AxiomError('GroupByClass:: folderPath %s not in the self._filteredFolderValues' % folderPath)
        folderNode = self._filteredFolderValues[folderPath].GetFolderNode()
        attrValues = self.GetAttrValues(folderPath)
        for (attrName, attrValue,) in attrValues.items():
            findvalue = folderNode.FindValueOrContainer(attrName, True)
            typeClass = folderNode.GetClassIncludingAttr(attrName)
            className = typeClass.className if typeClass is not None else ''
            if className not in self._classGroupInstances:
                self._classGroupInstances[className] = ClassGroupInstance(typeClass)
            self._classGroupInstances[className].AddFolderPath(folderPath)
            self._classGroupInstances[className].AddAttributeValue(attrName, attrValue)




    def CalFilterGroup(self, folderPath):
        if type(self._filteredFolderValues) != dict:
            raise AxiomError('CalFilterGroup:: _filteredFolderValues is not the dict object.')
        self._filteredFolderValues[folderPath].CalFilterGroup()



    def CalValueTypes(self, folderPath):
        if type(self._filteredFolderValues) != dict:
            raise AxiomError('CalValueTypes:: _filteredFolderValues is not the dict object.')
        self._filteredFolderValues[folderPath].CalValueTypes()
        valueTypes = self._filteredFolderValues[folderPath].GetValueTypes()
        for valType in valueTypes:
            if valType not in self._valueTypes:
                self._valueTypes.append(valType)




    def FilterFolders(self):
        if self._folderFilterString == '':
            return False
        if type(self._filteredFolderValues) != dict:
            raise AxiomError('FilterFolders:: self._filteredFolderValues is not the dict object.')
        folderStringList = self._folderFilterString.split('.')
        folderStringList = self.PreParseSearchStr(folderStringList)
        allFolderNodes = self._ax2.GetAllFolderNode()
        folderRegularString = self.GenerateRegularString(folderStringList)
        folderRegexObj = re.compile(folderRegularString)
        for (folderPath, folderNode,) in allFolderNodes.items():
            if folderRegexObj.match(folderPath.lower()) is not None:
                self._filteredFolderValues[folderPath] = WildcardFolderValues(folderPath)
                self._filteredFolderValues[folderPath].SetFolderNode(folderNode)

        return True



    def FilterAttrValues(self, folderPath):
        if folderPath is None:
            raise AxiomError('FilterAttrValues:: folderPath is none.')
        if folderPath not in self._filteredFolderValues:
            raise AxiomError('FilterAttrValues:: folderPath is not in filtered results.')
        if self._attrFilterString == '':
            return False
        folderNode = self._ax2.GetNodeByPath(folderPath)
        attrStringList = self._attrFilterString.split('.')
        attrStringList = self.PreParseSearchStr(attrStringList)
        attrRegularString = self.GenerateRegularString(attrStringList)
        attrRegexObj = re.compile(attrRegularString)
        valueStringList = self._valueFilterString.split('.')
        valueStringList = self.PreParseSearchStr(valueStringList)
        valueRegularString = self.GenerateRegularString(valueStringList)
        valueRegexObj = re.compile(valueRegularString)
        valueContainer = folderNode.GetValueContainer()
        allvalues = []
        valueContainer.GetAllValues(allvalues, True, True)
        for (attName, attValue,) in allvalues:
            if attrRegexObj.match(attName.lower()) is not None and (self.IsAllValue() or valueRegexObj.match(str(attValue.calculated).lower()) and attValue.modifier):
                self._filteredFolderValues[folderPath].SetAttrValues(attName, attValue)

        return True



    def PreParseSearchStr(self, folderStringList, wildcardStr = INCLUDE_ALL):
        retList = []
        bPreFolderStrIsWildcard = False
        if type(folderStringList) == list:
            for folderstr in folderStringList:
                if not bPreFolderStrIsWildcard or bPreFolderStrIsWildcard and folderstr != wildcardStr:
                    retList.append(folderstr)
                bPreFolderStrIsWildcard = True if folderstr == wildcardStr else False

        return retList



    def GenerateRegularString(self, stringList, wildcard = '*'):
        if type(stringList) != list:
            raise AxiomError('string list is not the list type object')
        pathRegularString = ''
        for pathStr in stringList:
            pathRegularString += '\\.' if pathRegularString != '' else ''
            pathRegularString += self.ParseWord(pathStr) if pathStr != wildcard else '[\\w\\.]+'

        return pathRegularString



    def ParseWord(self, string, wildcard = '*'):
        string = string.lower()
        regWord = ''
        for letter in string:
            regWord += letter if letter != wildcard else '[\\w]*'

        return regWord



    def IsFilteredContainer(self, folderPath, childContainer):
        if not self.HasAttributes(folderPath):
            return False
        filteredAttrValues = self.GetAttrValues(folderPath)
        fullyQualifiedName = childContainer.GetFullyQualifiedName()
        groupNames = []
        for attrName in filteredAttrValues.keys():
            if attrName.find(fullyQualifiedName) > -1:
                return True

        return False



    def IsInFilteredFolderNodes(self, pathNode, bIncludeParentNode = True):
        if type(pathNode) != axiom2.FolderNode:
            raise AxiomError('IsInFilteredFolderNodes:: pathNode (%s) is not the FolderNode object.' % pathNode)
        if type(self._filteredFolderValues) != dict:
            raise AxiomError('IsInFilteredFolderNodes:: self._filteredFolderValues(%s) is not the dict object' % self._filteredFolderValues)
        path = pathNode.GetPath()
        if len(self._filteredFolderValues) == 0:
            return False
        for (folderPath, filteredFolderValues,) in self._filteredFolderValues.items():
            if path == folderPath or bIncludeParentNode and folderPath.find(path + '.') > -1 and (self.IsAllAttr() or filteredFolderValues.HasAttributes()):
                return True

        return False




class AxiomDataError(object):
    __slots__ = ['folderPath', 'errorsByType']

    def __init__(self, folderPath):
        self.folderPath = folderPath
        self.errorsByType = {}
        for errorType in DATA_ERROR_ALL.keys():
            self.errorsByType[errorType] = []




    def AddError(self, errorType, attName, currValue):
        if not errorType or not attName:
            raise RuntimeError('error type <%s> or attribute name <%s> is invalid' % (errorType, attName))
        if errorType not in self.errorsByType:
            raise RuntimeError('error type is invalid', errorType)
        errors = self.errorsByType[errorType]
        if attName in errors:
            raise RuntimeError('error for attribute <%s> is already saved' % attName)
        errors.append((attName, currValue))



    def Shrink(self):
        hasData = False
        for (errorType, errors,) in self.errorsByType.items():
            if errors:
                hasData = True
            else:
                del self.errorsByType[errorType]

        return hasData




def GetDisplayName(attName):
    attName = attName.replace('_', ' ')
    if len(attName) >= 2:
        if attName[0] == 'm' and attName[1] >= 'A' and attName[1] <= 'Z':
            attName = attName[1:]
    displayName = re.sub('([A-Z][a-z0-9]+)', ' \\1', attName)
    displayName = re.sub('([A-Z]{2,})', ' \\1', displayName)
    displayName = displayName.strip()
    displayName = displayName.lower()
    return displayName



def GetValueDisplayName(attName, valueObj):
    if valueObj.valueType.caption:
        displayName = valueObj.valueType.caption
    else:
        displayName = GetDisplayName(attName)
    return displayName



def GetContainerDisplayName(attName, container):
    containerType = container.GetTypeInstance()
    if containerType and containerType.caption and not container.IsSetElement():
        displayName = containerType.caption
    else:
        displayName = GetDisplayName(attName)
    return displayName



def GetValueForDisplay(attValue, ax2):
    if attValue.calculated is None:
        valueStr = ''
    elif isinstance(attValue.valueType, axiom2.TypeReference):
        typeNode = ax2.GetNodeByID(attValue.calculated)
        if typeNode:
            valueStr = typeNode.GetNodeName()
        else:
            valueStr = 'Null'
    elif isinstance(attValue.calculated, str) or isinstance(attValue.calculated, unicode):
        valueStr = "'%s'" % attValue.calculated
    else:
        valueStr = str(attValue.calculated)
    return valueStr



class DBMerger(object):

    def __init__(self, db, ax2, folderPaths):
        self.mergedFolders = []
        self.db = db
        self.ax2 = ax2
        if folderPaths:
            self.folderPaths = folderPaths.split('+')
        else:
            self.folderPaths = []



    def Merge(self):
        for folderPath in self.folderPaths:
            dbFolder = self.db._GetFolder(folderPath)
            self.MergeFolder(dbFolder)




    def MergeFolder(self, folder):
        folderPath = folder.GetFullyQualifiedPath()
        pathList = folderPath.split('.')
        pathList.pop()
        parentFolderPath = '.'.join(pathList)
        try:
            axiomParentFolder = self.ax2.GetNodeByPath(parentFolderPath)
        except axiom.AxiomError as e:
            raise RuntimeError("Parent folder(%s) doesn't exist in catma." % parentFolderPath)
        self.mergedFolders.append(folder)
        axFolder = None
        try:
            axFolder = self.ax2.GetNodeByPath(folderPath)
        except axiom.AxiomError as e:
            pass
        if axFolder is None:
            axFolder = self.ax2.AddFolder(folderPath, None, folder.GetJoinedClassNames(), '', folder._isType)
            self.MergeValues(folderPath, '', folder)
            for childFolder in folder._childFolders:
                self.MergeFolder(childFolder)

        else:
            raise RuntimeError('Target Path (%s) has already existed' % folderPath)



    def MergeValues(self, folderPath, parentAttName, catmaValue):
        for (valueName, valueObject,) in catmaValue._values.iteritems():
            if parentAttName:
                attName = '%s.%s' % (parentAttName, valueName)
            else:
                attName = valueName
            if isinstance(valueObject[0], CatmaValue):
                self.MergeValues(folderPath, attName, valueObject[0])
            else:
                modifier = valueObject[2]
                if modifier is not None:
                    self.ax2.EditValue(folderPath, attName, valueObject[3], modifier, axiom2.VALUE_EDIT)





