#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\stdlib\unittest2\result.py
import traceback
import unittest
from unittest2 import util

class TestResult(unittest.TestResult):

    def __init__(self):
        self.failures = []
        self.errors = []
        self.testsRun = 0
        self.skipped = []
        self.expectedFailures = []
        self.unexpectedSuccesses = []
        self.shouldStop = False

    def startTest(self, test):
        self.testsRun += 1

    def startTestRun(self):
        pass

    def stopTest(self, test):
        pass

    def stopTestRun(self):
        pass

    def addError(self, test, err):
        self.errors.append((test, self._exc_info_to_string(err, test)))

    def addFailure(self, test, err):
        self.failures.append((test, self._exc_info_to_string(err, test)))

    def addSuccess(self, test):
        pass

    def addSkip(self, test, reason):
        self.skipped.append((test, reason))

    def addExpectedFailure(self, test, err):
        self.expectedFailures.append((test, self._exc_info_to_string(err, test)))

    def addUnexpectedSuccess(self, test):
        self.unexpectedSuccesses.append(test)

    def wasSuccessful(self):
        return len(self.failures) == len(self.errors) == 0

    def stop(self):
        self.shouldStop = True

    def _exc_info_to_string(self, err, test):
        exctype, value, tb = err
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next

        if exctype is test.failureException:
            length = self._count_relevant_tb_levels(tb)
            return ''.join(traceback.format_exception(exctype, value, tb, length))
        return ''.join(traceback.format_exception(exctype, value, tb))

    def _is_relevant_tb_level(self, tb):
        globs = tb.tb_frame.f_globals
        is_relevant = '__name__' in globs and globs['__name__'].startswith('unittest')
        del globs
        return is_relevant

    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next

        return length

    def __repr__(self):
        return '<%s run=%i errors=%i failures=%i>' % (util.strclass(self.__class__),
         self.testsRun,
         len(self.errors),
         len(self.failures))