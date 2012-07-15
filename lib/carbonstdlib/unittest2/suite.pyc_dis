#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\stdlib\unittest2\suite.py
import unittest
from unittest2 import case
from unittest2 import util

class TestSuite(unittest.TestSuite):

    def __init__(self, tests = ()):
        self._tests = []
        self.addTests(tests)

    def __repr__(self):
        return '<%s tests=%s>' % (util.strclass(self.__class__), list(self))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return list(self) == list(other)

    def __ne__(self, other):
        return not self == other

    __hash__ = None

    def __iter__(self):
        return iter(self._tests)

    def countTestCases(self):
        cases = 0
        for test in self:
            cases += test.countTestCases()

        return cases

    def addTest(self, test):
        if not hasattr(test, '__call__'):
            raise TypeError('%r is not callable' % (test,))
        if isinstance(test, type) and issubclass(test, (unittest.TestCase, unittest.TestSuite)):
            raise TypeError('TestCases and TestSuites must be instantiated before passing them to addTest()')
        self._tests.append(test)

    def addTests(self, tests):
        if isinstance(tests, basestring):
            raise TypeError('tests must be an iterable of tests, not a string')
        for test in tests:
            self.addTest(test)

    def run(self, result):
        for test in self:
            if result.shouldStop:
                break
            test(result)

        return result

    def __call__(self, *args, **kwds):
        return self.run(*args, **kwds)

    def debug(self):
        for test in self:
            test.debug()