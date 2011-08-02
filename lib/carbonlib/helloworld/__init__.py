
def __UpdateBinaries():
    import blue
    import os
    import sys
    if sys.platform == 'win32':
        print 'Clearing _helloworld.dll and _helloworld_d.dll binaries from application directory'
        binpath = blue.os.binpath
        try:
            os.remove(binpath + '_helloworld.dll')
        except:
            sys.exc_clear()
        try:
            os.remove(binpath + '_helloworld_d.dll')
        except:
            sys.exc_clear()
        autoBinariesPath = os.path.normpath(os.path.join(blue.os.binpath, '../../carbon/autobuild/win32/'))
        os.system('copy /Y "' + autoBinariesPath + '\\_helloworld_d.dll" "' + binpath + '"')
        os.system('copy /Y "' + autoBinariesPath + '\\_helloworld_d.pdb" "' + binpath + '"')
        os.system('copy /Y "' + autoBinariesPath + '\\_helloworld.dll" "' + binpath + '"')
        os.system('copy /Y "' + autoBinariesPath + '\\_helloworld.pdb" "' + binpath + '"')


__UpdateBinaries()
from _helloworld import *

def RunUnitTests():
    import unittest

    class HelloWorldTestCase(unittest.TestCase):

        def testRefCountingAndPointerAssignment(self):
            x = Hello()
            y = Hello()
            self.assertEqual(x.GetRefCounts()[1], 1)
            y.next = x
            self.assertEqual(x.GetRefCounts()[1], 2)
            self.assertEqual(id(x), id(y.next))



        def testRefCountingAndVectorAssignment(self):
            x = Hello()
            y = Hello()
            self.assertEqual(x.GetRefCounts()[1], 1)
            y.helloVector.append(x)
            self.assertEqual(x.GetRefCounts()[1], 2)
            self.assertEqual(id(x), id(y.helloVector[0]))



        def testIntegerExposure(self):
            x = Hello()
            self.assertEqual(x.a, 42)
            x.a = 1
            self.assertEqual(x.a, 1)

            def AssignStringToIntTypeErrorExpected():
                x.a = 'a string'


            self.assertRaises(TypeError, AssignStringToIntTypeErrorExpected)
            self.assertEqual(type(x.a), int)



        def testStdStringExposure(self):
            x = Hello()
            self.assertEqual(x.myString, '')
            x.myString = 'Test'
            self.assertEqual(x.myString, 'Test')

            def AssignIntToStringTypeErrorExpected():
                x.myString = 1


            self.assertRaises(TypeError, AssignIntToStringTypeErrorExpected)

            def AssignUnicodeToStringTypeErrorExpected():
                x.myString = u'a unicode string'


            self.assertRaises(TypeError, AssignUnicodeToStringTypeErrorExpected)
            self.assertEqual(type(x.myString), str)
            stringWithNullCharacter = 'Hello /0 Hello'
            x.myString = stringWithNullCharacter
            self.assertEqual(x.myString, stringWithNullCharacter)



        def testCloneTo(self):
            x = Hello()
            testString = 'Test String'
            x.myString = testString
            testInt = 1
            x.a = testInt
            y = x.CloneTo()
            self.assertEqual(y.myString, testString)
            self.assertEqual(y.a, testInt)



        def testSaveToRedLoadFromRed(self):
            import blue
            x = Hello()
            testString = 'Test String'
            x.myString = testString
            testInt = 1
            x.a = testInt
            y = Hello()
            x.next = y
            x.helloVector.append(y)
            blue.os.SaveObject(x, 'cache:/test.red')
            z = blue.os.LoadObject('cache:/test.red')
            self.assertEqual(z.myString, testString)
            self.assertEqual(z.a, testInt)
            self.assertEqual(len(z.helloVector), 1)
            self.assertTrue(x.next is x.helloVector[0], 'Instancing not working')
            self.assertTrue(z.next is z.helloVector[0], 'Instancing not maintained across saves')



        def testSaveToBlueLoadFromBlue(self):
            import blue
            x = Hello()
            testString = 'Test String'
            x.myString = testString
            testInt = 1
            x.a = testInt
            y = Hello()
            x.next = y
            x.helloVector.append(y)
            blue.os.SaveObject(x, 'cache:/test.blue')
            z = blue.os.LoadObject('cache:/test.blue')
            self.assertEqual(z.myString, testString)
            self.assertEqual(z.a, testInt)
            self.assertEqual(len(z.helloVector), 1)
            self.assertTrue(x.next is x.helloVector[0], 'Instancing not working')
            self.assertTrue(z.next is z.helloVector[0], 'Instancing not maintained across saves')



        def testReadOnlyProperty(self):
            x = Hello()

            def AssignReadOnlyErrorExpected():
                x.a2 = 1


            self.assertRaises(AttributeError, AssignReadOnlyErrorExpected)
            self.assertEqual(x.a2, x.a)
            self.assertEqual(type(x.a2), type(x.a))



        def testStdStringMethodExposure(self):
            x = Hello()
            result = x.SayHello()
            self.assertEqual(result, 'Hello World!')
            self.assertEqual(type(result), str)



        def testEnumExposureOldStyle(self):
            moduleNameSpace = globals()
            for i in xrange(1, 7):
                self.assertTrue('HETEST_VALUE' + str(i) in moduleNameSpace, 'Module does not have all registered enum values')




        def testEnumExposureNewStyle(self):
            moduleNameSpace = globals()
            self.assertTrue('HELLO_TEST_ENUM2' in moduleNameSpace)
            for i in xrange(1, 7):
                self.assertTrue(hasattr(HELLO_TEST_ENUM2, 'HETEST2_VALUE' + str(i)), 'Module does not have all registered enum values under the enum type')




    suite = unittest.TestLoader().loadTestsFromTestCase(HelloWorldTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)


RunUnitTests()

