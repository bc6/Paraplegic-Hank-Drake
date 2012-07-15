#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\helloworld\__init__.py
import unittest
import sys
import bluepy
import blue

def __UpdateBinaries():
    import blue
    import os
    import sys
    if sys.platform == 'win32':
        print 'Clearing _helloworld.dll and _helloworld_d.dll binaries from application directory'
        binpath = blue.paths.ResolvePath(u'bin:/')
        try:
            os.remove(binpath + '_helloworld.dll')
        except:
            sys.exc_clear()

        try:
            os.remove(binpath + '_helloworld_d.dll')
        except:
            sys.exc_clear()

        autoBinariesPath = os.path.normpath(os.path.join(blue.paths.ResolvePath(u'bin:/'), '../../../../carbon/autobuild/helloworld/Win32'))
        print autoBinariesPath
        os.system('copy /Y "' + autoBinariesPath + '\\_helloworld_d.dll" "' + binpath + '"')
        os.system('copy /Y "' + autoBinariesPath + '\\_helloworld_d.pdb" "' + binpath + '"')
        print os.system('copy /Y "' + autoBinariesPath + '\\_helloworld.dll" "' + binpath + '"')
        print os.system('copy /Y "' + autoBinariesPath + '\\_helloworld.pdb" "' + binpath + '"')


__UpdateBinaries()
from _helloworld import *

def RunPythonUnitTests():

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
            self.assertEqual(blue.GetID(x), blue.GetID(y.helloVector[0]))

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
            y = x.CloneTo()
            self.assertEqual(y.myString, testString)

        def testSaveToRedLoadFromRed(self):
            x = Hello()
            testString = 'Test String'
            x.myString = testString
            y = Hello()
            x.next = y
            x.helloVector.append(y)
            blue.resMan.SaveObject(x, 'cache:/test.red')
            z = blue.resMan.LoadObject('cache:/test.red')
            self.assertEqual(z.myString, testString)
            self.assertEqual(len(z.helloVector), 1)
            self.assertEqual(blue.GetID(x.next), blue.GetID(x.helloVector[0]), 'Instancing not working')
            self.assertEqual(blue.GetID(z.next), blue.GetID(z.helloVector[0]), 'Instancing not maintained across saves')

        def testSaveToBlueLoadFromBlue(self):
            x = Hello()
            testString = 'Test String'
            x.myString = testString
            y = Hello()
            x.next = y
            x.helloVector.append(y)
            blue.resMan.SaveObject(x, 'cache:/test.blue')
            z = blue.resMan.LoadObject('cache:/test.blue')
            self.assertEqual(z.myString, testString)
            self.assertEqual(len(z.helloVector), 1)
            self.assertEqual(blue.GetID(x.next), blue.GetID(x.helloVector[0]), 'Instancing not working')
            self.assertEqual(blue.GetID(z.next), blue.GetID(z.helloVector[0]), 'Instancing not maintained across saves')

        def testReadOnlyProperty(self):
            x = Hello()

            def AssignReadOnlyErrorExpected():
                x.readOnlyAnswer = 1

            self.assertRaises(AttributeError, AssignReadOnlyErrorExpected)
            self.assertEqual(x.readOnlyAnswer, x.answer)
            self.assertEqual(type(x.readOnlyAnswer), type(x.answer))

        def testStdStringMethodExposure(self):
            x = Hello()
            result = x.SayHello()
            self.assertEqual(result, 'Hello World!')
            self.assertEqual(type(result), str)

    suite = unittest.TestLoader().loadTestsFromTestCase(HelloWorldTestCase)
    from enumerations_unittest import BlueEnumerationSupportTestCase as enum_test_case
    suite.addTests(bluepy.BlueTestLoader().loadTestsFromTestCase(enum_test_case))
    from callbacks_unittest import CallbacksTestCase as callback_test_case
    suite.addTests(bluepy.BlueTestLoader().loadTestsFromTestCase(callback_test_case))
    unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)


def RunBlueUnitTests():
    try:
        suite = bluepy.BlueTestLoader().loadTestsFromModule(unittests)
        unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    except NameError:
        print 'No C++ unit tests defined'


print 'Running Blue unittests...'
RunBlueUnitTests()
import uthread
print 'Running Python unittests...'
uthread.new(RunPythonUnitTests)