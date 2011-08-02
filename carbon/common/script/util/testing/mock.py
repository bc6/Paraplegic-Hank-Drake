import weakref
import types
globalReference = None
neverMockList = ['weakref',
 'types',
 '__builtins__',
 'mock']
_mockAccessLog = {'accessLog': [],
 'callLog': []}
from util import IsStaticMethod
from blue import BlueWrapper

def _MockSetAttrHelper(parent, attrName, attrRef):
    if isinstance(parent, type):
        type.__setattr__(parent, attrName, attrRef)
    elif isinstance(parent, types.ClassType):
        types.ClassType.__setattr__(parent, attrName, attrRef)
    elif isinstance(parent, types.InstanceType):
        types.InstanceType.__setattr__(parent, attrName, attrRef)
    elif isinstance(parent, BlueWrapper):
        raise TypeError, 'You cannot mock attributes of a blue object'
    elif isinstance(parent, object):
        object.__setattr__(parent, attrName, attrRef)
    else:
        print ' *** WARNING: Unknown type being mocked:',
        print type(parent),
        print ':',
        print parent
        setattr(parent, attrName, attrRef)



class Mock(object):

    def __init__(self, mockName = 'unnamed_Mock', insertAsGlobal = False, autoAddAttributes = True):
        global globalReference
        if '*alreadyInited' in self.__dict__:
            return 
        if insertAsGlobal and mockName in neverMockList:
            raise RuntimeError, 'The module "%s" can never be mocked.' % mockName
        object.__setattr__(self, '*name', mockName)
        object.__setattr__(self, '*attributes', {})
        object.__setattr__(self, '*callableObject', None)
        object.__setattr__(self, '*insertAsGlobal', insertAsGlobal)
        object.__setattr__(self, '*globalReplacements', {})
        object.__setattr__(self, '*oldParent', None)
        object.__setattr__(self, '*oldAttribute', None)
        object.__setattr__(self, '*autoAddAttributes', autoAddAttributes)
        object.__setattr__(self, '*alreadyInited', True)
        if insertAsGlobal:

            def InjectGlobalMock(globalReference, mockName, refKey):
                oldReference = globalReference.get(mockName, None)
                if isinstance(oldReference, Mock):
                    object.__setattr__(self, '*insertAsGlobal', False)
                    raise RuntimeError, 'The module "' + mockName + '" is already mocked!  You cannot mock it again!'
                object.__setattr__(self, refKey, oldReference)
                globalReference[mockName] = weakref.proxy(self)


            InjectGlobalMock(globalReference, mockName, '*oldReference')
            if '__oldglobals__' in globalReference:
                InjectGlobalMock(globalReference['__oldglobals__'], mockName, '*oldReference2')
        if insertAsGlobal and mockName == 'blue':
            self.pyos.synchro.Sleep = _Sleep
            self.pyos.synchro.SleepUntil = SetTime
            self.pyos.synchro.Yield = _Yield
            self.os.GetTime = GetTime
            SetTime(0)
            SetYieldDuration(1)



    def __del__(self):

        def GetAttrHelper(obj, name, default):
            if name in object.__getattribute__(obj, '__dict__'):
                return object.__getattribute__(obj, name)
            else:
                return default


        insertAsGlobal = GetAttrHelper(self, '*insertAsGlobal', False)
        if insertAsGlobal:

            def RetractGlobalMock(globalReference, mockName, refKey):
                oldReference = GetAttrHelper(self, refKey, None)
                if oldReference is not None:
                    globalReference[mockName] = oldReference
                else:
                    del globalReference[mockName]


            mockName = GetAttrHelper(self, '*name', '')
            RetractGlobalMock(globalReference, mockName, '*oldReference')
            if '__oldglobals__' in globalReference:
                RetractGlobalMock(globalReference['__oldglobals__'], mockName, '*oldReference2')
        globalReplacements = GetAttrHelper(self, '*globalReplacements', {})
        for name in globalReplacements:
            globalReference[name] = globalReplacements[name]




    def __getattr__(self, name):
        fullName = object.__getattribute__(self, '*name') + '.' + name
        object.__getattribute__(self, '_Log')('accessLog', fullName)
        attributes = object.__getattribute__(self, '*attributes')
        if name in attributes:
            return attributes[name]
        if object.__getattribute__(self, '*autoAddAttributes'):
            child = Mock(fullName, insertAsGlobal=False)
            self._MockAttribute(name, child)
            return child
        raise AttributeError, "mock object '%s' does not have attribute '%s'" % (object.__getattribute__(self, '*name'), name)



    def __call__(self, *args, **kw):
        object.__getattribute__(self, '_Log')('callLog', object.__getattribute__(self, '*name'), *args, **kw)
        callableObject = object.__getattribute__(self, '*callableObject')
        if callableObject is not None:
            if type(callableObject) == types.UnboundMethodType:
                return callableObject(self, *args, **kw)
            else:
                return callableObject(*args, **kw)
        else:
            name = 'mockreturn<' + GetLastCallLogEntry() + '>'
            return Mock(name)



    def __setattr__(self, name, value):
        if callable(value) and not isinstance(value, Mock):
            object.__getattribute__(self, '_MockMethod')(name, value)
        else:
            object.__getattribute__(self, '_MockAttribute')(name, value)



    def __getitem__(self, key):
        if not object.__getattribute__(self, 'HasMockValue')():
            object.__getattribute__(self, 'SetMockValue')({})
        contents = object.__getattribute__(self, '*mockValue')
        try:
            result = contents[key]
        except KeyError:
            name = 'mockcontents[' + repr(key) + ']_' + object.__getattribute__(self, '*name')
            result = Mock(name)
            contents[key] = result
        return result



    def __setitem__(self, key, value):
        if not object.__getattribute__(self, 'HasMockValue')():
            object.__getattribute__(self, 'SetMockValue')({})
        object.__getattribute__(self, '*mockValue')[key] = value



    def __delitem__(self, key):
        if not object.__getattribute__(self, 'HasMockValue')():
            return 
        contents = object.__getattribute__(self, '*mockValue')
        if isinstance(contents, Mock):
            raise TypeError, 'This mock object is mocking a mock object.  This is wrong.'
        try:
            del contents[key]
        except KeyError:
            pass



    def __nonzero__(self):
        if not object.__getattribute__(self, 'HasMockValue')():
            return True
        value = object.__getattribute__(self, '*mockValue')
        if value:
            return True
        return False



    def __len__(self):
        if not object.__getattribute__(self, 'HasMockValue')():
            return 0
        return len(object.__getattribute__(self, '*mockValue'))



    def __iter__(self):
        if object.__getattribute__(self, 'HasMockValue')():
            return iter(object.__getattribute__(self, '*mockValue'))
        else:
            return iter({})



    def __eq__(self, other):
        if '*mockValue' in object.__getattribute__(self, '__dict__'):
            if isinstance(other, Mock):
                if '*mockValue' in object.__getattribute__(other, '__dict__'):
                    return object.__getattribute__(self, '*mockValue') == object.__getattribute__(other, '*mockValue')
                raise TypeError, 'Right operand Mock object cannot be compared unless it has a mock value.'
            else:
                return object.__getattribute__(self, '*mockValue') == other
        else:
            raise TypeError, '"%s" Mock object cannot be compared unless it has a mock value.' % object.__getattribute__(self, '*name')



    def __gt__(self, other):
        if '*mockValue' in object.__getattribute__(self, '__dict__'):
            if isinstance(other, Mock):
                if '*mockValue' in object.__getattribute__(other, '__dict__'):
                    return object.__getattribute__(self, '*mockValue') > object.__getattribute__(other, '*mockValue')
                raise TypeError, 'Right operand Mock object cannot be compared unless it has a mock value.'
            else:
                return object.__getattribute__(self, '*mockValue') > other
        else:
            raise TypeError, 'Left operand Mock object cannot be compared unless it has a mock value.'



    def __ne__(self, other):
        eq = object.__getattribute__(self, '__eq__')(other)
        return not eq



    def __ge__(self, other):
        gt = object.__getattribute__(self, '__gt__')(other)
        eq = object.__getattribute__(self, '__eq__')(other)
        return gt or eq



    def __lt__(self, other):
        ge = object.__getattribute__(self, '__ge__')(other)
        return not ge



    def __le__(self, other):
        gt = object.__getattribute__(self, '__gt__')(other)
        return not gt



    def __str__(self):
        if '*mockValue' in object.__getattribute__(self, '__dict__'):
            return str(object.__getattribute__(self, '*mockValue'))
        else:
            return object.__str__(self)



    def _MockAttribute(self, name, value):
        object.__getattribute__(self, '*attributes')[name] = value



    def _MockMethod(self, name, callableObject, findAndReplace = True):
        fullName = object.__getattribute__(self, '*name') + '.' + name
        child = Mock(fullName, insertAsGlobal=False)
        object.__setattr__(child, '*callableObject', callableObject)
        object.__getattribute__(self, '_MockAttribute')(name, child)
        if globalReference is not None:
            pathList = fullName.split('.')
            currentObject = ByPass(pathList[0])
            if currentObject is not None and not isinstance(currentObject, Mock):
                for name in pathList[1:]:
                    currentObject = getattr(currentObject, name, None)
                    if currentObject is None:
                        break

                for (name, obj,) in globalReference.items():
                    if isinstance(obj, Mock):
                        continue
                    if obj == currentObject:
                        object.__getattribute__(self, '*globalReplacements')[name] = currentObject
                        globalReference[name] = child




    def _Log(self, logSection, attributeName, *args, **kw):
        message = attributeName
        if logSection == 'callLog':
            message += '('
            for arg in args:
                message += repr(arg) + ', '

            for (key, value,) in kw.items():
                message += str(key) + ' = ' + repr(value) + ', '

            if len(args) > 0 or len(kw) > 0:
                message = message[:-2]
            message += ')'
        _mockAccessLog[logSection].append(message)



    def Revert(self):
        global _replacedAttributes
        oldParent = object.__getattribute__(self, '*oldParent')
        oldAttribute = object.__getattribute__(self, '*oldAttribute')
        name = object.__getattribute__(self, '*name')
        if oldParent is None:
            raise RuntimeError, 'Only mocks created with ReplaceAttribute can be reverted.'
        elif IsStaticMethod(oldAttribute) and type(oldParent) in [types.ClassType, type]:
            oldAttribute = staticmethod(oldAttribute)
        _MockSetAttrHelper(oldParent, name, oldAttribute)
        for index in range(len(_replacedAttributes))[None]:
            entry = _replacedAttributes[index]
            try:
                if entry[0]() is oldParent and entry[1] == name:
                    _replacedAttributes.pop(index)
                    break
            except ReferenceError:
                _replacedAttributes.pop(index)




    def SetCallable(self, callableObject):
        object.__setattr__(self, '*callableObject', callableObject)



    def SetMockValue(self, value):
        object.__setattr__(self, '*mockValue', value)



    def RemoveMockValue(self):
        if '*mockValue' in object.__getattribute__(self, '__dict__'):
            object.__delattr__(self, '*mockValue')



    def HasMockValue(self):
        return '*mockValue' in object.__getattribute__(self, '__dict__')




def ByPass(moduleName):
    module = globalReference.get(moduleName)
    if module is None:
        return 
    if not isinstance(module, Mock):
        raise RuntimeError, 'Cannot bypass a non-mock object!'
    else:
        return getattr(module, '*oldReference')


_replacedAttributes = []

def ReplaceAttribute(parent, attributeName, mockValue = None):
    oldAttribute = getattr(parent, attributeName)
    if isinstance(parent, Mock):
        raise TypeError, 'To mock methods or attributes on a mock object, assign to them directly.'
    if isinstance(oldAttribute, Mock):
        RevertAttribute(parent, attributeName)
        oldAttribute = getattr(parent, attributeName)
    newMock = Mock(attributeName, insertAsGlobal=False)
    object.__setattr__(newMock, '*oldParent', parent)
    object.__setattr__(newMock, '*oldAttribute', oldAttribute)
    _MockSetAttrHelper(parent, attributeName, newMock)
    if mockValue is not None:
        if callable(mockValue) and not isinstance(mockValue, Mock):
            newMock.SetCallable(mockValue)
        else:
            newMock.SetMockValue(mockValue)
    if type(parent) in (types.ModuleType, types.ClassType):
        reference = lambda *args, **kwargs: parent
    else:
        reference = weakref.ref(parent)
    _replacedAttributes.append((reference, attributeName))
    return newMock



def ReplaceMethod(parent, methodName, callableObject):
    newMock = ReplaceAttribute(parent, methodName)
    object.__setattr__(newMock, '*callableObject', callableObject)
    return newMock



def RevertAttribute(parent, attributeName):
    oldMock = getattr(parent, attributeName)
    if hasattr(oldMock, 'Revert'):
        oldMock.Revert()
    else:
        errmsg = 'The mock framework tried to revert an an attribute "'
        errmsg += attributeName + '" on object ' + str(parent)
        errmsg += ', but that attribute is not currently mocked!'
        raise AttributeError, errmsg



def RevertMethod(parent, methodName):
    RevertAttribute(parent, methodName)


_builtinSaved = {}

def _ReplaceBuiltin(name, newFunction):
    builtins = globalReference.get('__builtins__')
    newMock = Mock(name)
    object.__setattr__(newMock, '*callableObject', newFunction)
    if name not in _builtinSaved:
        _builtinSaved[name] = builtins[name]
    builtins[name] = newMock



def _RevertBuiltin(name):
    builtins = globalReference.get('__builtins__')
    if name not in _builtinSaved:
        raise KeyError, 'You cannot revert a builtin until after you replace it!.'
    else:
        builtins[name] = _builtinSaved[name]
        del _builtinSaved[name]



def _RevertAllBuiltins():
    for name in _builtinSaved.keys():
        _RevertBuiltin(name)




def SetGlobalReference(reference):
    global globalReference
    globalReference = reference


_mockInternalTime = 0

def SetTime(timeValue):
    global _mockInternalTime
    blueReference = globalReference.get('blue')
    if not isinstance(blueReference, Mock):
        raise RuntimeError, 'blue module must be mocked to use mock.SetTime'
    else:
        _mockInternalTime = timeValue



def _Sleep(timeValue):
    blueReference = globalReference.get('blue')
    if not isinstance(blueReference, Mock):
        raise RuntimeError, 'blue module must be mocked to use mock._Sleep'
    else:
        newTime = GetTime() + timeValue
        SetTime(newTime)


_mockYieldDuration = 1

def _Yield():
    global _mockYieldDuration
    _Sleep(_mockYieldDuration)



def SetYieldDuration(timeValue):
    global _mockYieldDuration
    blueReference = globalReference.get('blue')
    if not isinstance(blueReference, Mock):
        raise RuntimeError, 'blue module must be mocked to use mock.SetYieldDuration'
    else:
        _mockYieldDuration = timeValue



def GetTime():
    return _mockInternalTime


_oldImport = __builtins__['__import__']

def _DoNotImport(moduleName, *args, **kw):
    module = globalReference.get(moduleName)
    if isinstance(module, Mock):
        raise RuntimeError, 'Attempted to import module [' + moduleName + ']: You may not import modules during a unit test!'
    else:
        return _oldImport(moduleName, *args, **kw)



def SetUp(testCase, moduleGlobals, doNotMock = []):
    SetGlobalReference(moduleGlobals)
    for (name, obj,) in globalReference.items():
        if isinstance(obj, types.ModuleType) and name not in neverMockList and name not in doNotMock:
            testCase.__setattr__('*' + name, Mock(name, insertAsGlobal=True))

    testCase.mockOpen = Mock('open', insertAsGlobal=True)
    testCase.mockOpen.SetCallable(_MockOpen)
    ResetFileLog()
    ResetMockLog()
    _ReplaceBuiltin('__import__', _DoNotImport)



def TearDown(testCase):
    for (name, obj,) in testCase.__dict__.items():
        if isinstance(obj, Mock):
            del testCase.__dict__[name]

    _RevertAllBuiltins()
    infiniteLoopGuard = len(_replacedAttributes)
    while len(_replacedAttributes) > 0:
        entry = _replacedAttributes[0]
        RevertAttribute(entry[0](), entry[1])
        if infiniteLoopGuard == len(_replacedAttributes):
            errmsg = 'mock.TearDown appears to be looping infinitely while ' + 'trying to clean up replaced attributes!'
            raise RuntimeError, errmsg
        else:
            infiniteLoopGuard = len(_replacedAttributes)




def ResetMockLog():
    for logSection in _mockAccessLog.keys():
        _mockAccessLog[logSection] = []




def GetAccessLog():
    return _mockAccessLog['accessLog']



def GetCallLog():
    return _mockAccessLog['callLog']



def GetCallLogFor(objectName):
    tempLog = []
    for entry in GetCallLog():
        if entry.startswith(objectName):
            tempLog.append(entry)

    return tempLog



def CountMockCalls(methodName):
    count = 0
    for entry in GetCallLog():
        if entry.startswith(methodName):
            count += 1

    return count



def GetCallLogStripped():
    tempLog = []
    for entry in GetCallLog():
        tempLog.append(entry[:entry.find('(')])

    return tempLog



def GetLastCallLogEntry():
    logRef = GetCallLog()
    if len(logRef) > 0:
        return logRef[-1]



def AddLogMessage(logSection, message):
    _mockAccessLog[logSection].append(message)


_fileAccessLog = {'openLog': [],
 'writeLog': [],
 'readBuffer': []}

def ResetFileLog():
    for logSection in _fileAccessLog.keys():
        _fileAccessLog[logSection] = []




def AddMockFileContents(fileName, data):
    readBuffer = _fileAccessLog['readBuffer']
    for line in data:
        readBuffer.append((fileName, line))




def GetFileLog(logSection, fileName = None):
    if fileName is None:
        logData = _fileAccessLog[logSection]
    else:
        logData = [ line[1] for line in _fileAccessLog[logSection] if line[0] == fileName ]
    return logData



def _MockOpen(path, mode):
    _fileAccessLog['openLog'].append((path, mode))
    mockFile = Mock('mockFile')
    mockFile.fileName = path
    mockFile.write = _MockFileWriteFactory(path)
    mockFile.writelines = _MockFileWriteLinesFactory(path)
    mockFile.read = _MockFileReadFactory(path)
    mockFile.readline = _MockFileReadLineFactory(path)
    mockFile.readlines = _MockFileReadLinesFactory(path)
    return mockFile



def _MockFileWriteFactory(fileName):

    def _MockFileWrite(data):
        _fileAccessLog['writeLog'].append((fileName, data))
        _fileAccessLog['readBuffer'].append((fileName, data))


    return _MockFileWrite



def _MockFileWriteLinesFactory(fileName):

    def _MockFileWriteLines(data):
        writeLog = _fileAccessLog['writeLog']
        readBuffer = _fileAccessLog['readBuffer']
        for line in data:
            writeLog.append((fileName, line))
            readBuffer.append((fileName, data))



    return _MockFileWriteLines



def _MockFileReadFactory(fileName):

    def _MockFileRead():
        readBuffer = _fileAccessLog['readBuffer']
        data = _MockFileReadLinesFactory(fileName)()
        data = ''.join(data)
        index = 0
        while index < len(readBuffer):
            if readBuffer[index][0] == fileName:
                del readBuffer[index]
            else:
                index += 1

        return data


    return _MockFileRead



def _MockFileReadLineFactory(fileName):

    def _MockFileReadLine():
        readBuffer = _fileAccessLog['readBuffer']
        index = 0
        data = None
        while index < len(readBuffer):
            if readBuffer[index][0] == fileName:
                data = readBuffer[index][1]
                del readBuffer[index]
                break
            else:
                index += 1

        if data is None:
            raise IOError, 'No data for file "%s"' % fileName
        return data


    return _MockFileReadLine



def _MockFileReadLinesFactory(fileName):

    def _MockFileReadLines():
        readBuffer = _fileAccessLog['readBuffer']
        data = [ line[1] for line in readBuffer if line[0] == fileName ]
        index = 0
        while index < len(readBuffer):
            if readBuffer[index][0] == fileName:
                del readBuffer[index]
            else:
                index += 1

        return data


    return _MockFileReadLines


import util
exports = util.AutoExports('mock', locals())

