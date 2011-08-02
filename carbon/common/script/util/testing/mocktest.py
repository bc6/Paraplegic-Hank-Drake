import unittest
import mock
import types
import blue
import time
TIME_ZONE_NAME = time.tzname

class ClassWithMethods(object):

    def NormalMethod(self):
        return 'Normal method for ' + self.__class__.__name__



    @classmethod
    def ClassMethod(cls):
        return 'Class method for ' + cls.__name__



    @staticmethod
    def StaticMethod():
        return 'Static method'




class _TestBasicMockObjectFunctionality(unittest.TestCase):
    __priority__ = -1

    def setUp(self):
        mock.SetUp(self, globals())



    def tearDown(self):
        mock.TearDown(self)



    def testHierarchyAndComparators(self):
        m = mock.Mock('mockObj')
        m.a.b.c.d = 3
        self.assertTrue(m.a.b.c.d == 3, 'attribute was not saved')
        try:
            m.b.c.d == 3
            self.fail('attribute appeared in a weird place')
        except TypeError:
            pass
        m.q.r.s.t = lambda : 'a'
        self.assertTrue(m.q.r.s.t() == 'a', 'method was not saved')
        self.assertTrue(isinstance(m.r.s.t(), mock.Mock), 'method appeared in a weird place')



    def testAccessLog(self):
        m = mock.Mock('myMockObj')
        accessLog = mock.GetAccessLog()
        expectedLog = []
        self.assertTrue(accessLog == expectedLog, 'access log did not initialize to empty')
        m.a.b = 3
        x = m.a.b
        accessLog = mock.GetAccessLog()
        expectedLog = ['myMockObj.a', 'myMockObj.a', 'myMockObj.a.b']
        self.assertTrue(accessLog == expectedLog, 'mock attribute accesses were not logged correctly')



    def testCallLog(self):
        m = mock.Mock('newMockObj')
        callLog = mock.GetCallLog()
        expectedLog = []
        self.assertTrue(callLog == expectedLog, 'call log did not initialize to empty')
        m.a.b.c()
        m.a.b = 3
        m.q.r.s()
        m.isValidNumber = lambda *args, **kw: True
        m.isValidNumber(7)
        m.isValidNumber(number=3)
        m.a(1, 2, 3, a=4, b=5)
        callLog = mock.GetCallLog()
        expectedLog = ['newMockObj.a.b.c()',
         'newMockObj.q.r.s()',
         'newMockObj.isValidNumber(7)',
         'newMockObj.isValidNumber(number = 3)',
         'newMockObj.a(1, 2, 3, a = 4, b = 5)']
        self.assertEqual(callLog, expectedLog, 'mock method calls were not logged correctly')
        oldLog = ['newMockObj.a.b.c',
         'newMockObj.q.r.s',
         'newMockObj.isValidNumber',
         'newMockObj.isValidNumber',
         'newMockObj.a']
        self.assertTrue(mock.GetCallLogStripped() == oldLog, 'stripped mock method calls were not logged correctly')



    def testCallLogStringParameters(self):
        m = mock.Mock('newMockObj')
        callLog = mock.GetCallLog()
        expectedLog = []
        self.assertEqual(callLog, expectedLog, 'call log did not initialize to empty')
        m.check('string1', s2='string2')
        expectedLog = ["newMockObj.check('string1', s2 = 'string2')"]
        self.assertEqual(mock.GetCallLog(), expectedLog, 'string parameters were not logged correctly')
        mock.ResetMockLog()
        m.check("str'ing")
        expectedLog = ['newMockObj.check("str\'ing")']
        self.assertTrue(mock.GetCallLog() == expectedLog, 'string parameter with apostrophe was not logged correctly')



    def testCallLogWithVariableParameters(self):
        m = mock.Mock('newMockObj')
        callLog = mock.GetCallLog()
        expectedLog = []
        self.assertEqual(callLog, expectedLog, 'call log did not initialize to empty')
        s1 = 'string1'
        n1 = 7
        m.check(s1, n1)
        expectedLog = ["newMockObj.check('string1', 7)"]
        self.assertEqual(mock.GetCallLog(), expectedLog, 'variable parameters were not logged correctly')



    def testCallLogCounting(self):
        now = blue.os.GetTime()
        self.assertTrue(mock.CountMockCalls('blue.os.GetTime') == 1, 'First count of blue.os.GetTime calls is wrong')
        now = blue.os.GetTime()
        self.assertTrue(mock.CountMockCalls('blue.os.GetTime') == 2, 'Second count of blue.os.GetTime calls is wrong')
        blue.pyos.synchro.Sleep(250)
        self.assertTrue(mock.CountMockCalls('blue.os.GetTime') == 2, 'Third count of blue.os.GetTime calls is wrong')
        self.assertTrue(mock.CountMockCalls('blue') == 3, 'Count of blue calls is wrong')



    def testCallLogFiltering(self):
        blue.os.GetTime()
        blue.pyos.synchro.Sleep(250)
        blue.os.SomeOtherFunction()
        blue.pyos.synchro.SleepUntil(500)
        callLogForBlue = ['blue.os.GetTime()',
         'blue.pyos.synchro.Sleep(250)',
         'blue.os.SomeOtherFunction()',
         'blue.pyos.synchro.SleepUntil(500)']
        callLogForBlueOs = ['blue.os.GetTime()', 'blue.os.SomeOtherFunction()']
        callLogForBluePyos = ['blue.pyos.synchro.Sleep(250)', 'blue.pyos.synchro.SleepUntil(500)']
        self.assertTrue(mock.GetCallLogFor('blue') == callLogForBlue, 'Call log for blue was wrong')
        self.assertTrue(mock.GetCallLogFor('blue.os') == callLogForBlueOs, 'Call log for blue.os was wrong')
        self.assertTrue(mock.GetCallLogFor('blue.pyos') == callLogForBluePyos, 'Call log for blue.pyos was wrong')



    def testCallLogWithBlue(self):
        now = blue.os.GetTime()
        callLog = mock.GetCallLog()
        expectedLog = ['blue.os.GetTime()']
        self.assertTrue(callLog == expectedLog, 'call to blue.os.GetTime was not logged')



    def testAssigningSubMockObjects(self):
        ent = mock.Mock('mockEntity')
        ent.isCharacter = lambda : True
        entityService = mock.Mock('mockEntityService')
        entityService.player = ent
        self.assertTrue(entityService.player.isCharacter(), 'assigning a mock object to an attribute of a mock object did not work')



    def testHasattrEtc(self):
        mockObj = mock.Mock('mockObj')
        self.assertTrue(hasattr(mockObj, 'fakeAttribute'), 'mock object did not have an attribute')
        self.assertTrue(hasattr(mockObj, 'anljdhf833'), 'mock object did not have an attribute')
        mockObj.a = 3
        self.assertEqual(getattr(mockObj, 'a'), 3, 'mocked attribute had the wrong value')
        self.assertTrue(isinstance(getattr(mockObj, 'b'), mock.Mock), 'unmocked attribute was not automatically mocked')
        self.assertTrue(callable(mockObj), 'mock object is not callable')



    def testIndexingMockObject(self):
        mockObj = mock.Mock('mockObj')
        a = mockObj[3]
        b = mockObj['hello']
        self.assertTrue(isinstance(a, mock.Mock), 'missing integer key did not return a new Mock')
        self.assertTrue(isinstance(b, mock.Mock), 'missing string key did not return a new Mock')
        b.method()
        expectedLog = ["mockcontents['hello']_mockObj.method()"]
        self.assertEqual(mock.GetCallLog(), expectedLog, 'autogenerated mock contents had an unexpected name')
        mockObj[5] = 7
        mockObj['hello'] = 'world'
        self.assertEqual(mockObj[5], 7, 'mock indexed by integer did not save value')
        self.assertEqual(mockObj['hello'], 'world', 'mock indexed by string did not save value')



    def testIteratingMockObject(self):
        mockObj = mock.Mock('mockObj')
        count = 0
        for x in mockObj:
            count += 1

        self.assertTrue(count == 0, "mock object iterated when it shouldn't!")
        mockObj['five'] = 5
        mockObj['seven'] = 7
        count = 0
        expectedDict = {'five': 5,
         'seven': 7}
        for x in mockObj:
            self.assertTrue(x in expectedDict.keys(), 'iterated to key %s incorrectly' % str(x))
            self.assertTrue(mockObj[x] == expectedDict[x])
            del expectedDict[x]

        self.assertTrue(len(expectedDict) == 0, 'mock iteration did not get every element!')



    def testIteratingMockObjectWithNoValue(self):
        mockObj = mock.Mock('mockObj')
        count = 0
        for x in mockObj:
            count += 1

        self.assertTrue(count == 0, "mock object iterated when it shouldn't have")



    def testDeletingFromAnIndexOnAMockObject(self):
        mockObj = mock.Mock('mockObj')
        mockObj.SetMockValue({1: 'one',
         2: 'two'})
        self.assertTrue(mockObj[1] is 'one', 'mock object did not SetMockValue with a dictionary correctly')
        del mockObj[1]
        self.assertTrue(isinstance(mockObj[1], mock.Mock), 'mock object did not delete from dictionary correctly')



    def testLengthOfAMockObject(self):
        mockObj = mock.Mock('mockObj')
        self.assertTrue(0 == len(mockObj), 'mock object length was not zero')
        mockObj[1] = 'hello'
        a = mockObj['key']
        self.assertTrue(2 == len(mockObj), 'mock object as dictionary did not have the correct length')
        mockObj.SetMockValue([3,
         1,
         4,
         1,
         5,
         9])
        self.assertTrue(6 == len(mockObj), 'mock object with a mock value did not have the correct length')
        mockObj.SetMockValue(3)
        self.assertRaises(TypeError, len, mockObj)



    def testLocalStorageofMockedModules(self):
        mockObj = getattr(self, '*time')
        self.assertTrue(isinstance(mockObj, mock.Mock), 'reference to mocked module was not stored locally')




def _bluetest():
    return blue.os.GetTime()



class _TestBlueAndMethods(unittest.TestCase):

    def setUp(self):
        mock.SetUp(self, globals())



    def tearDown(self):
        mock.TearDown(self)



    def testExternalFunction(self):
        mock.SetTime(100)
        self.assertTrue(_bluetest() == 100, 'blue.os.GetTime did not mock for the external function')



    def testDirectCall(self):
        mock.SetTime(200)
        self.assertTrue(blue.os.GetTime() == 200, 'blue.os.GetTime did not mock for the direct call')



    def testDefaultTimeValue(self):
        self.assertTrue(blue.os.GetTime() == 0, 'blue.os.GetTime did not have the correct default value')



    def testSleepAndYieldMethods(self):
        mock.SetTime(300)
        self.assertTrue(_bluetest() == 300, 'fail after mock.SetTime in sleep test')
        blue.pyos.synchro.Sleep(50)
        self.assertTrue(_bluetest() == 350, 'fail after blue.pyos.synchro.Sleep in sleep test')
        blue.pyos.synchro.SleepUntil(475)
        self.assertTrue(_bluetest() == 475, 'fail after blue.pyos.synchro.SleepUntil in sleep test')
        blue.pyos.synchro.Yield()
        self.assertTrue(_bluetest() == 476, 'blue.pyos.synchro.Yield did not increment by the default value')
        mock.SetYieldDuration(50)
        blue.pyos.synchro.Yield()
        self.assertTrue(_bluetest() == 526, 'blue.pyos.synchro.Yield did not increment by the custom value')



    def testMockingMethods(self):
        result = blue.crypto.UnjumbleString('data here')
        self.assertTrue(isinstance(result, mock.Mock), 'unmocked method did not return a Mock object')
        mock.ResetMockLog()
        result.upper()
        expectedLog = ["mockreturn<blue.crypto.UnjumbleString('data here')>.upper()"]
        self.assertTrue(mock.GetCallLog() == expectedLog, 'returned mock object did not log properly')
        blue.crypto.UnjumbleString = lambda data: data.upper()
        result = blue.crypto.UnjumbleString('data here')
        self.assertTrue(result == 'DATA HERE', 'mocked method did not get correct functionality')



    def testByPass(self):
        try:
            mock.ByPass('blue').pyos.synchro.Sleep(1)
            self.fail('real fn blocks, and should hit the unit testing block trap raising an error')
        except RuntimeError as e:
            self.assertTrue(e.args[0] == 'this tasklet does not like to be blocked.')




class _TestDoNotMockPartOne(unittest.TestCase):

    def setUp(self):
        mock.SetUp(self, globals())



    def tearDown(self):
        mock.TearDown(self)



    def testAllModulesMocked(self):
        for (name, obj,) in globals().items():
            if name not in mock.neverMockList:
                self.assertFalse(type(obj) == types.ModuleType, 'module ' + repr(name) + ' was not mocked')




    def testServiceMocking(self):
        self.assertTrue(isinstance(time.tzname, mock.Mock), 'time.tzname is not mocked')
        time.tzname = 'new name'
        self.assertTrue(isinstance(time.tzname, str), 'time.tzname did not get the mocked value')
        self.assertTrue(time.tzname == 'new name', 'time.tzname did not mock to the right value')




class _TestDoNotMockPartTwo(unittest.TestCase):

    def setUp(self):
        mock.SetUp(self, globals(), doNotMock=['time'])



    def tearDown(self):
        mock.TearDown(self)



    def testModule(self):
        self.assertTrue(type(time) == types.ModuleType, '"time" is not a module')



    def testConstant(self):
        self.assertTrue(time.tzname == TIME_ZONE_NAME)




def _pickletest(obj):
    obj.pickle('data.pikl')



class _TestMockingDirectly(unittest.TestCase):

    def setUp(self):
        mock.SetGlobalReference(globals())
        self.blue = mock.Mock('blue', insertAsGlobal=True)



    def tearDown(self):
        del self.blue



    def testBlueMocking(self):
        mock.SetTime(500)
        self.assertTrue(blue.os.GetTime() == 500, 'mocking only blue did not work')



    def testInlineModuleMocking(self):
        self.assertTrue(time.tzname == TIME_ZONE_NAME, '"time" got mocked too early')
        self.m = mock.Mock('time', insertAsGlobal=True)
        self.assertTrue(isinstance(time, mock.Mock), 'explicitly mocking "time" did not work')
        del self.m
        self.assertTrue(type(time) == types.ModuleType, 'deleting the "time" mock did not restore the original')



    def testLocalMockObject(self):
        obj = mock.Mock('mockObject')
        obj.concatenate = lambda *args: ''.join(args)
        self.assertTrue(obj.concatenate('this', 'is', 'test') == 'thisistest', 'arbitrary mocked method did not work')



    def testLocalMockObjectComplexFunction(self):
        obj = mock.Mock('mockObj')
        callCount = [0]

        def mockPickle(filename):
            self.assertTrue(type(filename) == types.StringType, 'filenames must be strings!')
            self.assertTrue(filename.endswith('.pikl'), 'you must be writing to a .pikl file')
            callCount[0] += 1


        obj.pickle = mockPickle
        obj.pickle('test.pikl')
        _pickletest(obj)
        self.assertTrue(callCount[0] == 2, 'mockPickle function was called the wrong number of times!')



    def testLocalMockObjectWithSelfAccess(self):
        return 
        obj = mock.Mock('mockObj')
        obj.name = 'objName'

        def mockGetName(self):
            return self.name


        obj.getName = new.instancemethod(mockGetName, mock.Mock)
        self.assertTrue(obj.getName() == 'objName', 'self.name was not mocked properly!')



    def testLocalMockObjectWithFactoryFunction(self):
        obj = mock.Mock('mockObj')
        OBJ_NAME = 'objName'
        obj.name = OBJ_NAME

        def getNameFactory(name):

            def mockGetName():
                return name


            return mockGetName


        obj.getName = getNameFactory(OBJ_NAME)
        self.assertTrue(obj.getName() == OBJ_NAME, 'factory generated getName did not work!')




def _errortest(input):
    if input < 0:
        raise KeyError, "I don't have data for that!"
    else:
        return True



class _TestExceptionRaising(unittest.TestCase):

    def setUp(self):
        mock.SetUp(self, globals())



    def tearDown(self):
        mock.TearDown(self)



    def testExternalFunction(self):
        self.assertRaises(KeyError, _errortest, -1)




class _TestMockFileOperations(unittest.TestCase):

    def setUp(self):
        mock.SetUp(self, globals())
        mock.ResetFileLog()



    def tearDown(self):
        mock.TearDown(self)



    def testOpen(self):
        f = open('myfile.txt', 'r')
        self.assertTrue(isinstance(f, mock.Mock), 'open did not return a mock object')



    def testOpenMultiple(self):
        f1 = open('myfile.txt', 'w')
        f2 = open('yourfile.txt', 'r')
        correctOpenData = [('myfile.txt', 'w'), ('yourfile.txt', 'r')]
        observedOpenData = mock.GetFileLog('openLog')
        self.assertTrue(correctOpenData == observedOpenData, 'open file log was not correct')



    def testWrite(self):
        f = open('myfile.txt', 'w')
        f.write('line1')
        f.write('line2')
        correctData = [('myfile.txt', 'line1'), ('myfile.txt', 'line2')]
        observedData = mock.GetFileLog('writeLog')
        self.assertTrue(correctData == observedData, 'writing to one file log is wrong')
        f2 = open('yourfile.txt', 'w')
        f2.write('data1')
        correctData = [('myfile.txt', 'line1'), ('myfile.txt', 'line2'), ('yourfile.txt', 'data1')]
        observedData = mock.GetFileLog('writeLog')
        self.assertTrue(correctData == observedData, 'writing to second file log is wrong')
        f.writelines(['line3', 'line4'])
        correctData = [('myfile.txt', 'line1'),
         ('myfile.txt', 'line2'),
         ('yourfile.txt', 'data1'),
         ('myfile.txt', 'line3'),
         ('myfile.txt', 'line4')]
        observedData = mock.GetFileLog('writeLog')
        self.assertTrue(correctData == observedData, 'writelines to a file log is wrong')
        correctData = ['data1']
        observedData = mock.GetFileLog('writeLog', 'yourfile.txt')
        self.assertTrue(correctData == observedData, 'log for a single file is wrong')



    def testRead(self):
        f = open('myfile.txt', 'r')
        mock.AddMockFileContents('myfile.txt', ['data1', 'data2'])
        self.assertTrue(f.readline() == 'data1', 'first line was not read correctly for readline()')
        self.assertTrue(f.readline() == 'data2', 'second line was not read correctly for readline()')
        mock.AddMockFileContents('myfile.txt', ['data3', 'data4'])
        self.assertTrue(f.read() == 'data3data4', 'mocked read() did not work')
        mock.AddMockFileContents('myfile.txt', ['data5', 'data6'])
        self.assertTrue(f.readlines() == ['data5', 'data6'], 'mocked readlines() did not work')
        mock.AddMockFileContents('myfile.txt', ['data7', 'data8'])
        mock.AddMockFileContents('yourfile.txt', ['data9', 'data10'])
        f2 = open('yourfile.txt', 'r')
        self.assertTrue(f2.read() == 'data9data10', 'multiple files read() for yourfile.txt did not work')
        self.assertTrue(f.read() == 'data7data8', 'multiple files read() for myfile.txt did not work')
        f.write('data11')
        f.write('data12')
        self.assertTrue(f.read() == 'data11data12', 'write then read back failed')
        self.assertTrue(mock.GetFileLog('readBuffer') == [], 'read buffer was not empty as expected')
        f.write('data13')
        f2.write('data14')
        correctData = [('myfile.txt', 'data13'), ('yourfile.txt', 'data14')]
        observedData = mock.GetFileLog('readBuffer')
        self.assertTrue(correctData == observedData, 'read buffer did not get the correct data after writing')



    def testReadLineException(self):
        f = open('myfile.txt', 'r')
        self.assertTrue(f.read() == '', 'read with no data did not return an empty string')
        self.assertTrue(f.readlines() == [], 'readlines with no data did not return an empty list')
        self.assertRaises(IOError, f.readline)




class _TestReturningAMockObject(unittest.TestCase):

    def setUp(self):
        mock.SetUp(self, globals())



    def tearDown(self):
        mock.TearDown(self)



    def testWithLocalFunction(self):

        def mockGetReadyEntities():
            entList = []
            for index in range(3):
                m = mock.Mock('mockEntity')
                m.IsReadyToAct = lambda : True
                m.entid = index + 1
                entList.append(m)

            return entList


        entList = mockGetReadyEntities()
        self.assertTrue(len(entList) == 3, 'entList is the wrong length')
        for ent in entList:
            self.assertTrue(ent.IsReadyToAct(), 'ent %d is not ready to act' % ent.entid)





class _TestGivingValuesToMockObjects(unittest.TestCase):

    def setUp(self):
        mock.SetUp(self, globals())



    def tearDown(self):
        mock.TearDown(self)



    def testMakeMockCallable(self):
        mockObj = mock.Mock('mockObj')
        self.assertTrue(isinstance(mockObj(), mock.Mock), 'trying to call a mock object did something strange')
        mockObj.SetCallable(lambda : 'Hello')
        self.assertTrue(mockObj() == 'Hello', 'setting mock object as callable did not work')
        mockObj = lambda : 'Goodbye'
        self.assertTrue(mockObj() == 'Goodbye', 'assigning to mock object did not work')
        self.assertTrue(type(mockObj) == types.FunctionType, 'mock object persisted too long')



    def testGiveMockAValue(self):
        mockObj = mock.Mock('mockObj')
        try:
            self.assertFalse(mockObj != 1, 'mock object is equal to 1 when it should not be')
            self.fail('did not generate the expected exception')
        except TypeError:
            pass
        try:
            self.assertFalse(mockObj > 1, 'mock object is greater than 1 when it should not be')
            self.fail('did not generate the expected exception')
        except TypeError:
            pass
        try:
            self.assertFalse(mockObj < 1, 'mock object is less than 1 when it should not be')
            self.fail('did not generate the expected exception')
        except TypeError:
            pass
        try:
            self.assertFalse(mockObj >= 1, 'mock object is greater than or equal to 1 when it should not be')
            self.fail('did not generate the expected exception')
        except TypeError:
            pass
        try:
            self.assertFalse(mockObj <= 1, 'mock object is less than or equal to 1 when it should not be')
            self.fail('did not generate the expected exception')
        except TypeError:
            pass
        try:
            self.assertFalse(mockObj != 1, 'mock object is not equal 1 when it should not be')
            self.fail('did not generate the expected exception')
        except TypeError:
            pass
        mockObj.SetMockValue(1)
        self.assertTrue(mockObj == 1, 'mock equality did not work')
        self.assertTrue(mockObj > 0, 'mock greater than did not work')
        self.assertTrue(mockObj < 2, 'mock less than did not work')
        self.assertTrue(mockObj != 0, 'mock not equal did not work')
        self.assertTrue(mockObj >= 0 and mockObj >= 1, 'mock greater than or equal did not work')
        self.assertTrue(mockObj <= 2 and mockObj <= 1, 'mock less than or equal did not work')
        self.assertTrue(str(mockObj) == '1', 'mock str() did not work')
        self.assertTrue(isinstance(mockObj, mock.Mock), 'mock object is not a mock object')
        mockObj.RemoveMockValue()
        try:
            self.assertFalse(mockObj == 1, "mock object retained it's mock value after remove")
            self.fail('did not generate the expected exception')
        except TypeError:
            pass
        self.assertTrue(isinstance(mockObj, mock.Mock), 'mock object stopped being a mock object')




class _ExistingClass(object):
    existingAttribute = 'a'

    def ExistingMethod(self):
        return 'm'



existingInstance = _ExistingClass()

class _TestReplacingAnAttributeOrMethod(unittest.TestCase):

    def setUp(self):
        mock.SetUp(self, globals())



    def tearDown(self):
        mock.TearDown(self)



    def testReplaceAttribute(self):
        self.assertTrue(existingInstance.existingAttribute == 'a')
        mock.ReplaceAttribute(existingInstance, 'existingAttribute')
        try:
            existingInstance.existingAttribute == 'a'
            self.fail('existing attribute did not get mocked')
        except TypeError:
            pass
        self.assertTrue(isinstance(existingInstance.existingAttribute, mock.Mock), 'existing attribute did not get mocked')
        mock.RevertAttribute(existingInstance, 'existingAttribute')
        self.assertTrue(existingInstance.existingAttribute == 'a', 'existing attribute did not get reverted')
        self.assertFalse(isinstance(existingInstance.existingAttribute, mock.Mock), 'existing attribute did not get reverted')



    def testReplaceAttributeWithValue(self):
        self.assertTrue(existingInstance.existingAttribute == 'a')
        mock.ReplaceAttribute(existingInstance, 'existingAttribute', 1)
        self.assertTrue(existingInstance.existingAttribute == 1, 'existing attribute did not get mocked')
        self.assertTrue(isinstance(existingInstance.existingAttribute, mock.Mock), 'existing attribute did not get mocked')
        existingInstance.existingAttribute.Revert()
        self.assertTrue(existingInstance.existingAttribute == 'a', 'existing attribute did not get reverted')
        self.assertTrue(not isinstance(existingInstance.existingAttribute, mock.Mock), 'existing attribute did not get reverted')



    def testReplaceMethod(self):
        self.assertTrue(existingInstance.ExistingMethod() == 'm')
        mock.ReplaceAttribute(existingInstance, 'ExistingMethod', lambda : 1)
        self.assertTrue(existingInstance.ExistingMethod() == 1, 'existing method did not get mocked')
        self.assertTrue(isinstance(existingInstance.ExistingMethod, mock.Mock), 'existing method did not get mocked')
        mock.RevertAttribute(existingInstance, 'ExistingMethod')
        self.assertTrue(existingInstance.ExistingMethod() == 'm', 'existing method did not get reverted')
        self.assertTrue(not isinstance(existingInstance.ExistingMethod, mock.Mock), 'existing method did not get reverted')




class _TestTeardownOfReplacedMethod(unittest.TestCase):

    def testTeardown(self):

        class testClass(object):

            def increment(self, x):
                return x + 1



        obj = testClass()
        self.assertTrue(obj.increment(1) == 2, 'method did not exist after delcaration')
        mock.SetUp(self, globals())
        self.assertTrue(obj.increment(1) == 2, 'method did not exist after mock.SetUp')

        def increment_two(x):
            return x + 2


        mock.ReplaceMethod(obj, 'increment', increment_two)
        self.assertTrue(obj.increment(1) == 3, 'method did not mock properly')
        mock.TearDown(self)
        self.assertTrue(obj.increment(1) == 2, 'method was not reverted by teardown')



    def testTeardownWithMultipleMethods(self):

        class testClass(object):

            def inc1(self, x):
                return x + 1



            def inc2(self, x):
                return x + 2



        obj = testClass()
        mock.SetUp(self, globals())

        def inc3(x):
            return x + 3


        mock.ReplaceMethod(obj, 'inc1', inc3)
        mock.ReplaceMethod(obj, 'inc2', lambda x: x + 4)
        self.assertTrue(obj.inc1(1) == 4, 'mocking method with object did not work')
        self.assertTrue(obj.inc2(1) == 5, 'mocking method with lambda did not work')
        mock.TearDown(self)
        self.assertTrue(obj.inc1(1) == 2, 'restoring method mocked by object did not work')
        self.assertTrue(obj.inc2(1) == 3, 'restoring method mocked by lambda did not work')



    def testTeardownAfterMultipleReplacements(self):

        class testClass(object):

            def inc1(self, x):
                return x + 1



        obj = testClass()
        mock.SetUp(self, globals())
        mock.ReplaceMethod(obj, 'inc1', lambda x: x + 2)
        mock.ReplaceMethod(obj, 'inc1', lambda x: x + 3)
        self.assertTrue(obj.inc1(1) == 4, 'double replacement did not work')
        mock.TearDown(self)
        self.assertTrue(obj.inc1(1) == 2, 'teardown after double replacement did not work')



gettime = blue.os.GetTime

class _TestGlobalSearchAndReplace(unittest.TestCase):

    def setUp(self):
        pass



    def tearDown(self):
        mock.TearDown(self)



    def testGlobalSearchAndReplace(self):
        try:
            blue.pyos.synchro.Sleep(1)
            self.fail('real fn blocks, and should hit the unit testing block trap raising an error')
        except RuntimeError as e:
            self.assertTrue(e.args[0] == 'this tasklet does not like to be blocked.')
        mock.SetUp(self, globals())
        mock.SetTime(675)
        self.assertTrue(isinstance(gettime, mock.Mock), 'global reference was not replaced')
        self.assertTrue(blue.os.GetTime() == 675, 'blue.os.GetTime has the wrong value')
        self.assertTrue(gettime() == 675, 'global reference gettime has the wrong value')




class _TestReplacingABuiltin(unittest.TestCase):

    def setUp(self):
        mock.SetUp(self, globals())



    def tearDown(self):
        mock.TearDown(self)



    def testReplaceBuiltin(self):
        self.assertTrue(sum([1, 2, 3]) == 6, 'sum() builtin did not work')
        self.sum = mock.Mock('sum', insertAsGlobal=True)
        self.sum.SetCallable(lambda argList: len(argList))
        self.assertTrue(sum([1, 2, 3]) == 3, 'sum() mock did not work')
        del self.sum
        self.assertTrue(sum([1, 2, 3]) == 6, 'sum() builtin was not restored')




class _SimpleTestClass(object):

    def __init__(self):
        self.testValue = 3



    def GetValue(self):
        return self.testValue




class _TestReplacingAClassMethod(unittest.TestCase):

    def setUp(self):
        mock.SetUp(self, globals())



    def tearDown(self):
        mock.TearDown(self)



    def testReplaceInit(self):
        callFlag = [False]

        def SetCallFlag():
            callFlag[0] = True


        mock.ReplaceMethod(_SimpleTestClass, '__init__', SetCallFlag)
        simpleObject = _SimpleTestClass()
        self.assertTrue(callFlag[0], 'new __init__ was not called')
        self.assertTrue(not hasattr(simpleObject, 'testValue'), 'old __init__ was called')
        mock.TearDown(self)
        mock.SetUp(self, globals())
        simpleObject = _SimpleTestClass()
        self.assertTrue(simpleObject.testValue == 3, 'mock.TearDown did not restore __init__')



    def testReplaceOtherMethod(self):

        def ReturnFive():
            return 5


        firstObject = _SimpleTestClass()
        mock.ReplaceMethod(_SimpleTestClass, 'GetValue', ReturnFive)
        secondObject = _SimpleTestClass()
        self.assertTrue(firstObject.GetValue() is 5, 'firstObject.GetValue was not mocked')
        self.assertTrue(secondObject.GetValue() is 5, 'secondObject.GetValue was not mocked')




class _TestBadMocking(unittest.TestCase):

    def setUp(self):
        mock.SetUp(self, globals())



    def tearDown(self):
        mock.TearDown(self)



    def testDoubleMock(self):

        def DoubleMock():
            self.time = mock.Mock('time', insertAsGlobal=True)


        self.assertRaises(RuntimeError, DoubleMock)



    def testMockReservedModule(self):

        def MockTypes():
            self.types = mock.Mock('types', insertAsGlobal=True)


        self.assertRaises(RuntimeError, MockTypes)




class _TestReplacingMethods(unittest.TestCase):

    def setUp(self):
        mock.SetUp(self, globals())



    def testMockNormalMethod(self):
        obj = ClassWithMethods()
        expected = 'Normal method for ClassWithMethods'
        self.assertTrue(expected == obj.NormalMethod(), 'NormalMethod was broken from the beginning!')
        mock.ReplaceMethod(ClassWithMethods, 'NormalMethod', lambda *args: 'mocked')
        expected = 'mocked'
        self.assertTrue(expected == obj.NormalMethod(), 'NormalMethod was not mocked on the class correctly!')
        mock.TearDown(self)
        expected = 'Normal method for ClassWithMethods'
        self.assertTrue(expected == obj.NormalMethod(), 'NormalMethod did not come back after teardown!')



    def testMockStaticMethod(self):
        expected = 'Static method'
        self.assertTrue(expected == ClassWithMethods.StaticMethod(), 'StaticMethod was broken from the beginning!')
        mock.ReplaceMethod(ClassWithMethods, 'StaticMethod', lambda *args: 'mocked')
        expected = 'mocked'
        self.assertTrue(expected == ClassWithMethods.StaticMethod(), 'StaticMethod was not mocked on the class correctly!')
        mock.TearDown(self)
        expected = 'Static method'
        self.assertTrue(expected == ClassWithMethods.StaticMethod(), 'StaticMethod did not come back after teardown!')



    def testMockStaticMethodOnInstance(self):
        testClassInstance = ClassWithMethods()
        expected = 'Static method'
        self.assertTrue(expected == testClassInstance.StaticMethod(), 'StaticMethod was broken from the beginning!')
        mock.ReplaceMethod(testClassInstance, 'StaticMethod', lambda *args: 'mocked')
        expected = 'mocked'
        self.assertTrue(expected == testClassInstance.StaticMethod(), 'StaticMethod was not mocked on the class correctly!')
        mock.TearDown(self)
        expected = 'Static method'
        self.assertTrue(expected == testClassInstance.StaticMethod(), 'StaticMethod did not come back after teardown!')



    def testMockClassMethod(self):
        expected = 'Class method for ClassWithMethods'
        self.assertTrue(expected == ClassWithMethods.ClassMethod(), 'ClassMethod was broken from the beginning!')
        mock.ReplaceMethod(ClassWithMethods, 'ClassMethod', lambda *args: 'mocked')
        expected = 'mocked'
        self.assertTrue(expected == ClassWithMethods.ClassMethod(), 'ClassMethod was not mocked on the class correctly!')
        mock.TearDown(self)
        expected = 'Class method for ClassWithMethods'
        self.assertTrue(expected == ClassWithMethods.ClassMethod(), 'ClassMethod did not come back after teardown!')




