#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\helloworld\enumerations_unittest.py
import unittest
import sys
import bluepy
import helloworld

class BlueEnumerationSupportTestCase(unittest.TestCase):

    def testEnumExposureOldStyle(self):
        moduleNameSpace = helloworld.__dict__
        for i in xrange(1, 7):
            self.assertTrue('HETEST_VALUE' + str(i) in moduleNameSpace, 'Module does not have all registered enum values')

    def testEnumExposureNewStyle(self):
        moduleNameSpace = helloworld.__dict__
        self.assertTrue('HELLO_TEST_ENUM2' in moduleNameSpace)
        HELLO_TEST_ENUM2 = helloworld.HELLO_TEST_ENUM2
        for i in xrange(1, 7):
            self.assertTrue(hasattr(HELLO_TEST_ENUM2, 'HETEST2_VALUE' + str(i)), 'Module does not have all registered enum values under the enum type')