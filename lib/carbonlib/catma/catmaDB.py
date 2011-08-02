import cPickle
from catmaConfig import ATTRIB_FLAGS, SIMPLE_TYPE_SERIAL_UIDS
import logging
logger = logging.getLogger('CORE.Stims')
USE_CLASSINFO_BASIC = True
SIMPLE_TYPES = {SIMPLE_TYPE_SERIAL_UIDS.INT: 'Int',
 SIMPLE_TYPE_SERIAL_UIDS.STR: 'String',
 SIMPLE_TYPE_SERIAL_UIDS.FLT: 'Float',
 SIMPLE_TYPE_SERIAL_UIDS.BOOL: 'Bool',
 SIMPLE_TYPE_SERIAL_UIDS.ENUM: 'Enum',
 SIMPLE_TYPE_SERIAL_UIDS.UNICODE: 'Unicode'}

class NoDefault():
    pass

class CatmaDBError(RuntimeError):
    pass

def CheckIsValidPath(path):
    if type(path) != str or not path:
        raise CatmaDBError('invalid path:', path)



def GetPackageName(objPath):
    pkgName = None
    if "'" in objPath:
        objPathStrip = objPath.split("'")[1]
    else:
        objPathStrip = objPath
    objPathStrip = objPathStrip.split('.')
    if len(objPathStrip) > 1:
        pkgName = objPathStrip[0]
    return pkgName



class Tokenizer(object):

    def __init__(self):
        self._tokens = {}
        self._strings = {}



    def GetToken(self, string):
        if string in self._tokens:
            return self._tokens[string]
        else:
            token = hash(string) & 16777215
            self._tokens[string] = token
            self._strings[token] = string
            return token



    def GetString(self, token):
        try:
            return self._strings[token]
        except KeyError:
            raise RuntimeError('token not found: %s!' % token)




class ClassInfoBasic(object):
    __slots__ = []

    def __init__(self, className):
        pass



    def _AddMember(self, memberName, memberType, memberFlag):
        pass




class ClassInfo(ClassInfoBasic):
    __slots__ = ClassInfoBasic.__slots__ + ['_members', '_className']

    def __init__(self, className):
        self._members = {}
        self._className = className



    def __repr__(self):
        return 'Class Info, class name: <%s>' % self._className



    def _AddMember(self, memberName, memberType, memberFlag):
        if memberName in self._members:
            raise CatmaDBError('_AddMember, member already exists: %s' % memberName)
        self._members[memberName] = (memberType, memberFlag)



    def GetMembers(self):
        return self._members



    def _DumpReadable(self, log):
        log.write('Class %s\n' % self._className)
        for (memberName, memberInfo,) in self._members.iteritems():
            if memberInfo[0] in SIMPLE_TYPES:
                log.write(' %s %s\n' % (SIMPLE_TYPES[memberInfo[0]], memberName))
            else:
                log.write(' %s %s\n' % (memberInfo[0]._className, memberName))

        log.write('\n\n')




class ValueObject(object):
    __slots__ = ['value', 'attFlag']

    def __init__(self, value, attFlag, *additionArgs):
        self.value = value
        self.attFlag = attFlag




class ValueObjectRangeInfo(ValueObject):
    __slots__ = ValueObject.__slots__ + ['valueRange']

    def __init__(self, value, attFlag, valueRange):
        super(ValueObjectRangeInfo, self).__init__(value, attFlag, valueRange)
        self.valueRange = valueRange




class CatmaValue(object):
    __slots__ = ['_values',
     '_valueNameToken',
     '_tokenizer',
     '_parentValue']

    def __init__(self, valueNameToken, tokenizer, parentValue):
        self._values = {}
        self._valueNameToken = valueNameToken
        self._tokenizer = tokenizer
        self._parentValue = parentValue



    def TearOff(self):
        for valueInfo in self._values.itervalues():
            if isinstance(valueInfo, CatmaValue):
                valueInfo.TearOff()

        self._values.clear()
        self._tokenizer = None
        self._parentValue = None



    def IsIdentical(self, newCatmaValue):
        if len(self._values) != len(newCatmaValue._values):
            return False

        def CompareChildValues(leftValue, rightValue):
            isIdentical = True
            for token in leftValue._values.iterkeys():
                attName = leftValue._tokenizer.GetString(token)
                ownValue = leftValue.GetValue(attName)
                try:
                    newValue = rightValue.GetValue(attName)
                    if type(ownValue) == type(newValue):
                        isIdentical = ownValue.IsIdentical(newValue) if isinstance(ownValue, CatmaValue) else ownValue == newValue
                    else:
                        isIdentical = False
                except CatmaDBError:
                    isIdentical = False
                if not isIdentical:
                    break

            return isIdentical


        return CompareChildValues(self, newCatmaValue) and CompareChildValues(newCatmaValue, self)



    def GetValueName(self):
        if self._valueNameToken:
            return self._tokenizer.GetString(self._valueNameToken)
        else:
            return ''



    def __repr__(self):
        return 'Catma Value, value name: <%s>' % self.GetValueName()



    def GetValueFromParentFolder(self, attributeName):
        currName = self._tokenizer.GetString(self._valueNameToken)
        attributeName.insert(0, currName)
        return self._parentValue.GetValueFromParentFolder(attributeName)



    def CacheInheritedValues(self):
        parentType = self.GetTopParent()
        if not isinstance(parentType, CatmaType):
            raise CatmaDBError('invalid top parent type: %s' % type(parentType))
        allValuesInType = parentType.GetAllValues(None, True, True)
        myPath = self.GetFullyQualifiedPath(False)
        for valueName in allValuesInType.keys():
            if myPath not in valueName:
                del allValuesInType[valueName]

        for (valueName, valueInfo,) in allValuesInType.iteritems():
            valueName = valueName.split('.')
            parentType._AddValue(valueName, ValueObject(valueInfo[0], valueInfo[1], None))




    def GetFullyQualifiedPath(self, includeFolderPath = True):
        parentPath = None
        if self._parentValue:
            parentPath = self._parentValue.GetFullyQualifiedPath(includeFolderPath)
        if parentPath:
            return '.'.join([parentPath, self.GetValueName()])
        return self.GetValueName()



    def GetTopParent(self):
        if self._parentValue:
            return self._parentValue.GetTopParent()
        else:
            return self



    def GetValue(self, attributeName, default = NoDefault):
        if isinstance(attributeName, str):
            attributeName = attributeName.split('.')
        currName = attributeName[0]
        token = self._tokenizer.GetToken(currName)
        if token not in self._values:
            try:
                value = self.GetValueFromParentFolder(attributeName)
            except CatmaDBError:
                value = None
            if value is not None:
                return value
            if default is NoDefault:
                raise CatmaDBError('value name is not found: %s' % currName)
            else:
                return default
        valueInfo = self._values[token]
        if len(attributeName) > 1:
            attributeName.pop(0)
            return valueInfo.GetValue(attributeName)
        else:
            if isinstance(valueInfo, ValueObject):
                return valueInfo.value
            return valueInfo



    def GetValueNames(self):
        valueNames = []
        for token in self._values.iterkeys():
            valueNames.append(self._tokenizer.GetString(token))

        return valueNames



    def _AddValue(self, attNameList, valueObject):
        currName = attNameList.pop(0)
        token = self._tokenizer.GetToken(currName)
        if attNameList:
            if token not in self._values:
                newValue = CatmaValue(token, self._tokenizer, self)
                self._values[token] = newValue
            self._values[token]._AddValue(attNameList, valueObject)
        else:
            self._values[token] = valueObject



    def _DumpReadable(self, log, indent):
        for (token, valueInfo,) in self._values.iteritems():
            valueName = self._tokenizer.GetString(token)
            if isinstance(valueInfo, CatmaValue):
                log.write('%s%s:\n' % (indent, valueName))
                valueInfo._DumpReadable(log, indent + ' ')
            else:
                log.write('%s%s: %s\n' % (indent, valueName, valueInfo.value))




    def GetAllValues(self, attFlag = None, recursive = True, includeAttFlag = False, includeValueRange = False):
        values = {}
        self._GetAllValues(recursive, '', values, attFlag, includeAttFlag, includeValueRange)
        return values



    def _GetAllValues(self, recursive, currentPath, values, attFlag, includeAttFlag, includeValueRange):
        myPath = '%s.%s' % (currentPath, self.GetValueName()) if currentPath else self.GetValueName()
        for (token, valueInfo,) in self._values.iteritems():
            valueName = self._tokenizer.GetString(token)
            if isinstance(valueInfo, CatmaValue) and recursive:
                valueInfo._GetAllValues(recursive, myPath, values, attFlag, includeAttFlag, includeValueRange)
            else:
                if attFlag is not None and not attFlag & valueInfo.attFlag:
                    continue
                absoluteName = '%s.%s' % (myPath, valueName) if myPath else valueName
                valuePack = [valueInfo.value]
                if includeAttFlag:
                    valuePack.append(valueInfo.attFlag)
                if includeValueRange:
                    valuePack.append(valueInfo.valueRange)
                values[absoluteName] = valuePack[0] if len(valuePack) == 1 else valuePack





class CatmaType(CatmaValue):
    __slots__ = CatmaValue.__slots__ + ['_classes',
     '_typeName',
     '_typeID',
     '_parentFolder',
     '_parentFolderPath',
     '_isType',
     '_isPublished',
     '_classNames',
     '_keywords',
     '_tags']

    def __init__(self, parentFolderPath, typeName, typeID, classNames, isType, tokenizer, isPublished):
        CatmaValue.__init__(self, '', tokenizer, None)
        self._classes = []
        self._typeName = typeName
        self._typeID = typeID
        self._parentFolder = None
        self._parentFolderPath = parentFolderPath
        self._isType = isType
        self._isPublished = isPublished
        if classNames:
            self._classNames = classNames.split('+')
        else:
            self._classNames = []
        if isType:
            for className in self._classNames:
                if not className:
                    raise CatmaDBError('invalid class names<%s> when creating folder/type <%s>' % (classNames, typeName))

        typeName = typeName.lower()
        self._keywords = typeName.split('_')
        self._tags = set()



    def TearOff(self):
        super(CatmaType, self).TearOff()
        del self._classes[:]
        self._parentFolder = None



    def HasKeywords(self, kws):
        return set(kws) <= set(self._keywords)



    def GetFullyQualifiedPath(self, includeFolderPath = True):
        if includeFolderPath:
            if self._parentFolderPath:
                return '.'.join([self._parentFolderPath, self._typeName])
            return self._typeName
        else:
            return ''



    def GetJoinedClassNames(self):
        return '+'.join(self._classNames)



    def GetClassNameList(self):
        return self._classNames



    def HasClassName(self, className):
        return className in self._classNames



    def IsIdentical(self, newCatmaType):
        if newCatmaType is None:
            return False
        if self._typeName != newCatmaType._typeName or self._typeID != newCatmaType._typeID or self._classNames != newCatmaType._classNames:
            return False
        if self._parentFolderPath != newCatmaType._parentFolderPath or self._parentFolder and not self._parentFolder.IsIdentical(newCatmaType._parentFolder):
            return False
        return CatmaValue.IsIdentical(self, newCatmaType)



    def __repr__(self):
        args = (self._typeName,
         self._typeID,
         self._parentFolderPath,
         self._classNames)
        return 'Catma Type, type name: <%s>, type id: <%s>, parent folder: <%s>, classes: <%s>' % args



    def GetAllValues(self, attFlag = None, recursive = True, includeAttFlag = False, includeValueRange = False):
        parentValues = {}
        if self._parentFolder:
            parentValues = self._parentFolder.GetAllValues(attFlag, recursive, includeAttFlag, includeValueRange)
        localValues = super(CatmaType, self).GetAllValues(attFlag, recursive, includeAttFlag, includeValueRange)
        if len(parentValues) > len(localValues):
            for (k, v,) in localValues.iteritems():
                parentValues[k] = v

            return parentValues
        else:
            for (k, v,) in parentValues.iteritems():
                if k not in localValues:
                    localValues[k] = v

            return localValues



    def GetValueFromParentFolder(self, attributeName):
        if self._parentFolder:
            return self._parentFolder.GetValue(attributeName)
        raise CatmaDBError()



    def _Cook(self, db):
        if self._parentFolderPath:
            try:
                self._parentFolder = db._GetFolder(self._parentFolderPath)
            except CatmaDBError:
                pass
        for className in self._classNames:
            classInfo = db.GetClassInfo(className)
            if classInfo:
                self._classes.append(classInfo)




    def _DumpReadable(self, log):
        log.write('Type %s(%s)\n' % (self._typeName, self._typeID))
        log.write(' Classes: %s\n' % self._classNames)
        log.write(' Values:\n')
        CatmaValue._DumpReadable(self, log, '  ')
        log.write('\n\n')



    def GetTypeID(self):
        return self._typeID



    def GetTypeName(self):
        return self._typeName



    def GetDisplayName(self):
        return self.GetValue('mDisplayName', '')



    def GetTypeDisplayName(self):
        s = self.GetValue('mDisplayName', '')
        if s != '':
            s = ' (%s)' % s
        return self.GetTypeName() + s



    def GetIsType(self):
        return self._isType



    def GetContentReferences(self, contentTypeQualifier = None):
        references = self.GetAllValues(ATTRIB_FLAGS.CONTENT_REF)
        if contentTypeQualifier:
            contentTypeQualifier = contentTypeQualifier.lower()
            for (k, v,) in references.items():
                if contentTypeQualifier not in v.lower():
                    del references[k]

        return references



    def GetContentPackageSet(self):
        packageSet = set()
        contentReferences = self.GetContentReferences()
        for contentPath in contentReferences.itervalues():
            pkgName = GetPackageName(contentPath)
            if pkgName:
                packageSet.add(pkgName)
            else:
                print 'Warning: Invalid object path in catmaDB <%s>' % contentPath

        return packageSet



    def _AddTag(self, tagID):
        self._tags.add(tagID)



    def _HasTags(self, tags):
        ret = False
        if tags <= self._tags:
            ret = True
        elif self._parentFolder:
            remaining = tags - self._tags
            ret = self._parentFolder._HasTags(remaining)
        return ret



    def IsPublished(self):
        return self._isPublished




class CatmaComparisonResult(object):

    def __init__(self, oldDB, newDB):
        self._deletedTypes = []
        self._modifiedTypes = []
        self._addedTypes = []
        self._Compare(oldDB, newDB)



    def _Compare(self, oldDB, newDB):
        print 'Compare old DB <%s> with new DB <%s>' % (oldDB, newDB)
        oldTypes = oldDB.GetAllTypes()
        newTypes = newDB.GetAllTypes()
        oldTypeNames = set(oldTypes.iterkeys())
        newTypeNames = set(newTypes.iterkeys())
        self._addedTypes = list(newTypeNames - oldTypeNames)
        self._deletedTypes = list(oldTypeNames - newTypeNames)
        sharedTypeNames = oldTypeNames & newTypeNames
        for typeName in sharedTypeNames:
            oldType = oldTypes[typeName]
            newType = newTypes[typeName]
            if not oldType.IsIdentical(newType):
                self._modifiedTypes.append(typeName)

        print 'Added Types:'
        for typeName in self._addedTypes:
            print '  %s' % typeName

        print 'Deleted Types:'
        for typeName in self._deletedTypes:
            print '  %s' % typeName

        print 'Modified Types:'
        for typeName in self._modifiedTypes:
            print '  %s' % typeName




    def GetModifiedTypeNames(self):
        return self._modifiedTypes



    def GetDeletedTypeNames(self):
        return self._deletedTypes



    def GetAddedTypeNames(self):
        return self._addedTypes




class CatmaDB(object):

    def __init__(self, desc = None, bsdChangeID = None):
        self._classes = {}
        self._types = {}
        self._typesByID = {}
        self._folders = {}
        self._tokenizer = Tokenizer()
        self._desc = desc
        self._bsdChangeID = bsdChangeID
        self._tagToID = {}



    def TearOff(self):
        for folder in self._folders.itervalues():
            folder.TearOff()

        self._classes.clear()
        self._types.clear()
        self._typesByID.clear()
        self._folders.clear()
        self._tokenizer = None



    def __repr__(self):
        args = (self._desc,
         len(self._types),
         len(self._folders),
         len(self._classes))
        return 'Catma DB, %s, %s types, %s folders, %s classes' % args



    def GetAllTypeNames(self):
        return [ typeName for typeName in self._types.iterkeys() ]



    def GetClassInfo(self, className):
        try:
            return self._classes[className]
        except KeyError:
            raise CatmaDBError('class info cannot be found: <%s>' % className)



    def _AddTag(self, tagName, tagID):
        if tagName in self._tagToID:
            raise CatmaDBError('Tag already exists: %s' % tagName)
        self._tagToID[tagName] = tagID



    def _CreateClassInfo(self, className):
        if className not in self._classes:
            classInfo = ClassInfoBasic(className) if USE_CLASSINFO_BASIC else ClassInfo(className)
            self._classes[className] = classInfo
        return self._classes[className]



    def _AddFolder(self, _folderPath, folderID, classNames, isType, isPublished):
        CheckIsValidPath(_folderPath)
        if isType and not classNames:
            raise CatmaDBError('_AddType, adding type <%s> with no class names' % _folderPath)
        folderPath = _folderPath.split('.')
        folderName = folderPath.pop()
        parentPath = '.'.join(folderPath) if folderPath else None
        if _folderPath in self._folders:
            raise CatmaDBError('_AddFolder, folder already existed: %s' % _folderPath)
        if isType:
            if folderName in self._types:
                raise CatmaDBError('_AddFolder, type already existed: %s' % folderName)
            if folderID in self._typesByID:
                raise CatmaDBError('_AddFolder, type ID already existed: %s' % folderID)
        newFolder = CatmaType(parentPath, folderName, folderID, classNames, isType, self._tokenizer, isPublished)
        self._folders[_folderPath] = newFolder
        if isType:
            self._types[folderName] = newFolder
            self._typesByID[folderID] = newFolder
        return newFolder



    def _AddValue(self, folderPath, attName, valueObject):
        catmaFolder = self._GetFolder(folderPath)
        CheckIsValidPath(attName)
        attName = attName.split('.')
        catmaFolder._AddValue(attName, valueObject)



    def _Cook(self):
        for folder in self._folders.values():
            folder._Cook(self)




    def GetValueByTypeName(self, typeName, attributeName, default = NoDefault):
        catmaType = self.GetType(typeName)
        return catmaType.GetValue(attributeName, default)



    def GetValueByTypeID(self, typeID, attributeName, default = NoDefault):
        catmaType = self.GetTypeByID(typeID)
        return catmaType.GetValue(attributeName, default)



    def GetType(self, typeName):
        try:
            return self._types[typeName]
        except KeyError:
            kws = typeName.lower().split('_')
            for catmaType in self._types.itervalues():
                if catmaType.HasKeywords(kws):
                    return catmaType

            raise CatmaDBError('type name is not found: %s' % typeName)



    def _GetFolder(self, folderPath):
        try:
            return self._folders[folderPath]
        except KeyError:
            raise CatmaDBError('folder path is not found: %s' % folderPath)



    def GetAllTypes(self):
        return self._types



    def GetAllTypesByID(self):
        return self._typesByID



    def GetTypeByID(self, typeID, default = NoDefault):
        if default is NoDefault and typeID not in self._typesByID:
            raise CatmaDBError('GetTypeByID: Type ID is not found: %s' % typeID)
        return self._typesByID.get(typeID, default)



    def Dump(self, fileObj, useBinary = True):
        cPickle.dump(self, fileObj, -1 if useBinary else 0)



    def DumpReadable(self, fileObj):
        fileObj.write('============== Class Info ==============\n')
        for classInfo in self._classes.values():
            classInfo._DumpReadable(fileObj)

        fileObj.write('\n\n\n\n')
        fileObj.write('============== Folders/Types ==============\n')
        for folderInfo in self._folders.values():
            folderInfo._DumpReadable(fileObj)




    def GetTypeID(self, typeName):
        foundType = self.GetType(typeName)
        return foundType.GetTypeID()



    def GetTypeName(self, typeID):
        try:
            foundType = self._typesByID[typeID]
        except KeyError:
            raise CatmaDBError('type id is not found: %s' % typeID)
        return foundType.GetTypeName()



    def GetTypeOfClass(self, className):
        types = []
        classInfo = self.GetClassInfo(className)
        if classInfo:
            for catmaType in self._types.itervalues():
                if classInfo in catmaType._classes:
                    types.append(catmaType)

        return types



    def GetTypesByTags(self, namedTags):
        if isinstance(namedTags, str):
            namedTags = [namedTags]
        tagIDs = set()
        for tag in namedTags:
            try:
                tagIDs.add(self._tagToID[tag])
            except KeyError:
                raise CatmaDBError('%s is not a valid Tag' % tag)

        types = []
        for catmaType in self._types.itervalues():
            if catmaType._HasTags(tagIDs):
                types.append(catmaType)

        return types



    def GetTypeNamesOfClass(self, className):
        names = []
        classInfo = self.GetClassInfo(className)
        if classInfo:
            for catmaType in self._types.itervalues():
                if classInfo in catmaType._classes:
                    names.append(catmaType._typeName)

        return names



    def GetContentPackageSet(self):
        packageSet = set()
        for folder in self._folders.itervalues():
            packageSet = packageSet.union(folder.GetContentPackageSet())

        return packageSet




def GetTypeByID(typeID, default = NoDefault):
    return GetDB().GetTypeByID(typeID, default)



def GetTypeByName(typeName):
    return GetDB().GetType(typeName)



def GetTypeNameByID(typeID, valueIfNotExists = '???'):
    typesByID = GetDB().GetAllTypesByID()
    if typeID in typesByID:
        return typesByID[typeID].GetTypeName()
    return valueIfNotExists



def GetDisplayNameByID(typeID, valueIfNotExists = '???'):
    obj = GetTypeByID(typeID, None)
    if obj is None:
        return valueIfNotExists
    return obj.GetDisplayName()



def GetTypeDisplayNameByID(typeID, valueIfNotExists = '???'):
    typesByID = GetDB().GetAllTypesByID()
    if typeID in typesByID:
        t = typesByID[typeID]
        s = t.GetValue('mDisplayName', '')
        if s != '':
            s = ' (%s)' % s
        return t.GetTypeName() + s
    return valueIfNotExists



def LoadData(data):
    try:
        import inifile
        Unpickler = inifile.old_Unpickler
    except Exception:
        Unpickler = cPickle.Unpickler
    return Unpickler(data).load()


from extraCatmaConfig import GetCatmaDB, SetCatmaDB

def GetDB():
    return GetCatmaDB()



def SetDB(newCatmaDB):
    SetCatmaDB(newCatmaDB)



