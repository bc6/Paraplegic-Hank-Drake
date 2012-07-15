#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\stdlib\unittest2\test\test_unittest2.py
import os
import re
import sys
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
import unittest2
import types
from copy import deepcopy
from cStringIO import StringIO
import pickle

class LoggingResult(unittest2.TestResult):

    def __init__(self, log):
        self._events = log
        super(LoggingResult, self).__init__()

    def startTest(self, test):
        self._events.append('startTest')
        super(LoggingResult, self).startTest(test)

    def startTestRun(self):
        self._events.append('startTestRun')
        super(LoggingResult, self).startTestRun()

    def stopTest(self, test):
        self._events.append('stopTest')
        super(LoggingResult, self).stopTest(test)

    def stopTestRun(self):
        self._events.append('stopTestRun')
        super(LoggingResult, self).stopTestRun()

    def addFailure(self, *args):
        self._events.append('addFailure')
        super(LoggingResult, self).addFailure(*args)

    def addSuccess(self, *args):
        self._events.append('addSuccess')
        super(LoggingResult, self).addSuccess(*args)

    def addError(self, *args):
        self._events.append('addError')
        super(LoggingResult, self).addError(*args)

    def addSkip(self, *args):
        self._events.append('addSkip')
        super(LoggingResult, self).addSkip(*args)

    def addExpectedFailure(self, *args):
        self._events.append('addExpectedFailure')
        super(LoggingResult, self).addExpectedFailure(*args)

    def addUnexpectedSuccess(self, *args):
        self._events.append('addUnexpectedSuccess')
        super(LoggingResult, self).addUnexpectedSuccess(*args)


class TestEquality(object):

    def test_eq(self):
        for obj_1, obj_2 in self.eq_pairs:
            self.assertEqual(obj_1, obj_2)
            self.assertEqual(obj_2, obj_1)

    def test_ne(self):
        for obj_1, obj_2 in self.ne_pairs:
            self.assertNotEqual(obj_1, obj_2)
            self.assertNotEqual(obj_2, obj_1)


class TestHashing(object):

    def test_hash(self):
        for obj_1, obj_2 in self.eq_pairs:
            try:
                if not hash(obj_1) == hash(obj_2):
                    self.fail('%r and %r do not hash equal' % (obj_1, obj_2))
            except KeyboardInterrupt:
                raise 
            except Exception as e:
                self.fail('Problem hashing %r and %r: %s' % (obj_1, obj_2, e))

        for obj_1, obj_2 in self.ne_pairs:
            try:
                if hash(obj_1) == hash(obj_2):
                    self.fail("%s and %s hash equal, but shouldn't" % (obj_1, obj_2))
            except KeyboardInterrupt:
                raise 
            except Exception as e:
                self.fail('Problem hashing %s and %s: %s' % (obj_1, obj_2, e))


class MyClassSuite(list):

    def __init__(self, tests):
        super(MyClassSuite, self).__init__(tests)


class MyException(Exception):
    pass


class Test_TestLoader(unittest2.TestCase):

    def test_loadTestsFromTestCase(self):

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

            def foo_bar(self):
                pass

        tests = unittest2.TestSuite([Foo('test_1'), Foo('test_2')])
        loader = unittest2.TestLoader()
        self.assertEqual(loader.loadTestsFromTestCase(Foo), tests)

    def test_loadTestsFromTestCase__no_matches(self):

        class Foo(unittest2.TestCase):

            def foo_bar(self):
                pass

        empty_suite = unittest2.TestSuite()
        loader = unittest2.TestLoader()
        self.assertEqual(loader.loadTestsFromTestCase(Foo), empty_suite)

    def test_loadTestsFromTestCase__TestSuite_subclass(self):

        class NotATestCase(unittest2.TestSuite):
            pass

        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromTestCase(NotATestCase)
        except TypeError:
            pass
        else:
            self.fail('Should raise TypeError')

    def test_loadTestsFromTestCase__default_method_name(self):

        class Foo(unittest2.TestCase):

            def runTest(self):
                pass

        loader = unittest2.TestLoader()
        self.assertFalse('runTest'.startswith(loader.testMethodPrefix))
        suite = loader.loadTestsFromTestCase(Foo)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [Foo('runTest')])

    def test_loadTestsFromModule__TestCase_subclass(self):
        m = types.ModuleType('m')

        class MyTestCase(unittest2.TestCase):

            def test(self):
                pass

        m.testcase_1 = MyTestCase
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromModule(m)
        self.assertIsInstance(suite, loader.suiteClass)
        expected = [loader.suiteClass([MyTestCase('test')])]
        self.assertEqual(list(suite), expected)

    def test_loadTestsFromModule__no_TestCase_instances(self):
        m = types.ModuleType('m')
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromModule(m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [])

    def test_loadTestsFromModule__no_TestCase_tests(self):
        m = types.ModuleType('m')

        class MyTestCase(unittest2.TestCase):
            pass

        m.testcase_1 = MyTestCase
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromModule(m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [loader.suiteClass()])

    def test_loadTestsFromModule__not_a_module(self):

        class MyTestCase(unittest2.TestCase):

            def test(self):
                pass

        class NotAModule(object):
            test_2 = MyTestCase

        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromModule(NotAModule)
        reference = [unittest2.TestSuite([MyTestCase('test')])]
        self.assertEqual(list(suite), reference)

    def test_loadTestsFromModule__load_tests(self):
        m = types.ModuleType('m')

        class MyTestCase(unittest2.TestCase):

            def test(self):
                pass

        m.testcase_1 = MyTestCase
        load_tests_args = []

        def load_tests(loader, tests, pattern):
            self.assertIsInstance(tests, unittest2.TestSuite)
            load_tests_args.extend((loader, tests, pattern))
            return tests

        m.load_tests = load_tests
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromModule(m)
        self.assertIsInstance(suite, unittest2.TestSuite)
        self.assertEquals(load_tests_args, [loader, suite, None])
        load_tests_args = []
        suite = loader.loadTestsFromModule(m, use_load_tests=False)
        self.assertEquals(load_tests_args, [])

    def test_loadTestsFromName__empty_name(self):
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromName('')
        except ValueError as e:
            self.assertEqual(str(e), 'Empty module name')
        else:
            self.fail('TestLoader.loadTestsFromName failed to raise ValueError')

    def test_loadTestsFromName__malformed_name(self):
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromName('abc () //')
        except ValueError:
            pass
        except ImportError:
            pass
        else:
            self.fail('TestLoader.loadTestsFromName failed to raise ValueError')

    def test_loadTestsFromName__unknown_module_name(self):
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromName('sdasfasfasdf')
        except ImportError as e:
            self.assertEqual(str(e), 'No module named sdasfasfasdf')
        else:
            self.fail('TestLoader.loadTestsFromName failed to raise ImportError')

    def test_loadTestsFromName__unknown_attr_name(self):
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromName('unittest2.sdasfasfasdf')
        except AttributeError as e:
            self.assertEqual(str(e), "'module' object has no attribute 'sdasfasfasdf'")
        else:
            self.fail('TestLoader.loadTestsFromName failed to raise AttributeError')

    def test_loadTestsFromName__relative_unknown_name(self):
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromName('sdasfasfasdf', unittest2)
        except AttributeError as e:
            self.assertEqual(str(e), "'module' object has no attribute 'sdasfasfasdf'")
        else:
            self.fail('TestLoader.loadTestsFromName failed to raise AttributeError')

    def test_loadTestsFromName__relative_empty_name(self):
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromName('', unittest2)
        except AttributeError:
            pass
        else:
            self.fail('Failed to raise AttributeError')

    def test_loadTestsFromName__relative_malformed_name(self):
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromName('abc () //', unittest2)
        except ValueError:
            pass
        except AttributeError:
            pass
        else:
            self.fail('TestLoader.loadTestsFromName failed to raise ValueError')

    def test_loadTestsFromName__relative_not_a_module(self):

        class MyTestCase(unittest2.TestCase):

            def test(self):
                pass

        class NotAModule(object):
            test_2 = MyTestCase

        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromName('test_2', NotAModule)
        reference = [MyTestCase('test')]
        self.assertEqual(list(suite), reference)

    def test_loadTestsFromName__relative_bad_object(self):
        m = types.ModuleType('m')
        m.testcase_1 = object()
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromName('testcase_1', m)
        except TypeError:
            pass
        else:
            self.fail('Should have raised TypeError')

    def test_loadTestsFromName__relative_TestCase_subclass(self):
        m = types.ModuleType('m')

        class MyTestCase(unittest2.TestCase):

            def test(self):
                pass

        m.testcase_1 = MyTestCase
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromName('testcase_1', m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [MyTestCase('test')])

    def test_loadTestsFromName__relative_TestSuite(self):
        m = types.ModuleType('m')

        class MyTestCase(unittest2.TestCase):

            def test(self):
                pass

        m.testsuite = unittest2.TestSuite([MyTestCase('test')])
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromName('testsuite', m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [MyTestCase('test')])

    def test_loadTestsFromName__relative_testmethod(self):
        m = types.ModuleType('m')

        class MyTestCase(unittest2.TestCase):

            def test(self):
                pass

        m.testcase_1 = MyTestCase
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromName('testcase_1.test', m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [MyTestCase('test')])

    def test_loadTestsFromName__relative_invalid_testmethod(self):
        m = types.ModuleType('m')

        class MyTestCase(unittest2.TestCase):

            def test(self):
                pass

        m.testcase_1 = MyTestCase
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromName('testcase_1.testfoo', m)
        except AttributeError as e:
            self.assertEqual(str(e), "type object 'MyTestCase' has no attribute 'testfoo'")
        else:
            self.fail('Failed to raise AttributeError')

    def test_loadTestsFromName__callable__TestSuite(self):
        m = types.ModuleType('m')
        testcase_1 = unittest2.FunctionTestCase(lambda : None)
        testcase_2 = unittest2.FunctionTestCase(lambda : None)

        def return_TestSuite():
            return unittest2.TestSuite([testcase_1, testcase_2])

        m.return_TestSuite = return_TestSuite
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromName('return_TestSuite', m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [testcase_1, testcase_2])

    def test_loadTestsFromName__callable__TestCase_instance(self):
        m = types.ModuleType('m')
        testcase_1 = unittest2.FunctionTestCase(lambda : None)

        def return_TestCase():
            return testcase_1

        m.return_TestCase = return_TestCase
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromName('return_TestCase', m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [testcase_1])

    def test_loadTestsFromName__callable__TestCase_instance_ProperSuiteClass(self):

        class SubTestSuite(unittest2.TestSuite):
            pass

        m = types.ModuleType('m')
        testcase_1 = unittest2.FunctionTestCase(lambda : None)

        def return_TestCase():
            return testcase_1

        m.return_TestCase = return_TestCase
        loader = unittest2.TestLoader()
        loader.suiteClass = SubTestSuite
        suite = loader.loadTestsFromName('return_TestCase', m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [testcase_1])

    def test_loadTestsFromName__relative_testmethod_ProperSuiteClass(self):

        class SubTestSuite(unittest2.TestSuite):
            pass

        m = types.ModuleType('m')

        class MyTestCase(unittest2.TestCase):

            def test(self):
                pass

        m.testcase_1 = MyTestCase
        loader = unittest2.TestLoader()
        loader.suiteClass = SubTestSuite
        suite = loader.loadTestsFromName('testcase_1.test', m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [MyTestCase('test')])

    def test_loadTestsFromName__callable__wrong_type(self):
        m = types.ModuleType('m')

        def return_wrong():
            return 6

        m.return_wrong = return_wrong
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromName('return_wrong', m)
        except TypeError:
            pass
        else:
            self.fail('TestLoader.loadTestsFromName failed to raise TypeError')

    def test_loadTestsFromName__module_not_loaded(self):
        module_name = 'audioop'
        if module_name in sys.modules:
            del sys.modules[module_name]
        loader = unittest2.TestLoader()
        try:
            suite = loader.loadTestsFromName(module_name)
            self.assertIsInstance(suite, loader.suiteClass)
            self.assertEqual(list(suite), [])
            self.assertIn(module_name, sys.modules)
        finally:
            if module_name in sys.modules:
                del sys.modules[module_name]

    def test_loadTestsFromNames__empty_name_list(self):
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromNames([])
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [])

    def test_loadTestsFromNames__relative_empty_name_list(self):
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromNames([], unittest2)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [])

    def test_loadTestsFromNames__empty_name(self):
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromNames([''])
        except ValueError as e:
            self.assertEqual(str(e), 'Empty module name')
        else:
            self.fail('TestLoader.loadTestsFromNames failed to raise ValueError')

    def test_loadTestsFromNames__malformed_name(self):
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromNames(['abc () //'])
        except ValueError:
            pass
        except ImportError:
            pass
        else:
            self.fail('TestLoader.loadTestsFromNames failed to raise ValueError')

    def test_loadTestsFromNames__unknown_module_name(self):
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromNames(['sdasfasfasdf'])
        except ImportError as e:
            self.assertEqual(str(e), 'No module named sdasfasfasdf')
        else:
            self.fail('TestLoader.loadTestsFromNames failed to raise ImportError')

    def test_loadTestsFromNames__unknown_attr_name(self):
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromNames(['unittest2.sdasfasfasdf', 'unittest2'])
        except AttributeError as e:
            self.assertEqual(str(e), "'module' object has no attribute 'sdasfasfasdf'")
        else:
            self.fail('TestLoader.loadTestsFromNames failed to raise AttributeError')

    def test_loadTestsFromNames__unknown_name_relative_1(self):
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromNames(['sdasfasfasdf'], unittest2)
        except AttributeError as e:
            self.assertEqual(str(e), "'module' object has no attribute 'sdasfasfasdf'")
        else:
            self.fail('TestLoader.loadTestsFromName failed to raise AttributeError')

    def test_loadTestsFromNames__unknown_name_relative_2(self):
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromNames(['TestCase', 'sdasfasfasdf'], unittest2)
        except AttributeError as e:
            self.assertEqual(str(e), "'module' object has no attribute 'sdasfasfasdf'")
        else:
            self.fail('TestLoader.loadTestsFromName failed to raise AttributeError')

    def test_loadTestsFromNames__relative_empty_name(self):
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromNames([''], unittest2)
        except AttributeError:
            pass
        else:
            self.fail('Failed to raise ValueError')

    def test_loadTestsFromNames__relative_malformed_name(self):
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromNames(['abc () //'], unittest2)
        except AttributeError:
            pass
        except ValueError:
            pass
        else:
            self.fail('TestLoader.loadTestsFromNames failed to raise ValueError')

    def test_loadTestsFromNames__relative_not_a_module(self):

        class MyTestCase(unittest2.TestCase):

            def test(self):
                pass

        class NotAModule(object):
            test_2 = MyTestCase

        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromNames(['test_2'], NotAModule)
        reference = [unittest2.TestSuite([MyTestCase('test')])]
        self.assertEqual(list(suite), reference)

    def test_loadTestsFromNames__relative_bad_object(self):
        m = types.ModuleType('m')
        m.testcase_1 = object()
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromNames(['testcase_1'], m)
        except TypeError:
            pass
        else:
            self.fail('Should have raised TypeError')

    def test_loadTestsFromNames__relative_TestCase_subclass(self):
        m = types.ModuleType('m')

        class MyTestCase(unittest2.TestCase):

            def test(self):
                pass

        m.testcase_1 = MyTestCase
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromNames(['testcase_1'], m)
        self.assertIsInstance(suite, loader.suiteClass)
        expected = loader.suiteClass([MyTestCase('test')])
        self.assertEqual(list(suite), [expected])

    def test_loadTestsFromNames__relative_TestSuite(self):
        m = types.ModuleType('m')

        class MyTestCase(unittest2.TestCase):

            def test(self):
                pass

        m.testsuite = unittest2.TestSuite([MyTestCase('test')])
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromNames(['testsuite'], m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [m.testsuite])

    def test_loadTestsFromNames__relative_testmethod(self):
        m = types.ModuleType('m')

        class MyTestCase(unittest2.TestCase):

            def test(self):
                pass

        m.testcase_1 = MyTestCase
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromNames(['testcase_1.test'], m)
        self.assertIsInstance(suite, loader.suiteClass)
        ref_suite = unittest2.TestSuite([MyTestCase('test')])
        self.assertEqual(list(suite), [ref_suite])

    def test_loadTestsFromNames__relative_invalid_testmethod(self):
        m = types.ModuleType('m')

        class MyTestCase(unittest2.TestCase):

            def test(self):
                pass

        m.testcase_1 = MyTestCase
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromNames(['testcase_1.testfoo'], m)
        except AttributeError as e:
            self.assertEqual(str(e), "type object 'MyTestCase' has no attribute 'testfoo'")
        else:
            self.fail('Failed to raise AttributeError')

    def test_loadTestsFromNames__callable__TestSuite(self):
        m = types.ModuleType('m')
        testcase_1 = unittest2.FunctionTestCase(lambda : None)
        testcase_2 = unittest2.FunctionTestCase(lambda : None)

        def return_TestSuite():
            return unittest2.TestSuite([testcase_1, testcase_2])

        m.return_TestSuite = return_TestSuite
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromNames(['return_TestSuite'], m)
        self.assertIsInstance(suite, loader.suiteClass)
        expected = unittest2.TestSuite([testcase_1, testcase_2])
        self.assertEqual(list(suite), [expected])

    def test_loadTestsFromNames__callable__TestCase_instance(self):
        m = types.ModuleType('m')
        testcase_1 = unittest2.FunctionTestCase(lambda : None)

        def return_TestCase():
            return testcase_1

        m.return_TestCase = return_TestCase
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromNames(['return_TestCase'], m)
        self.assertIsInstance(suite, loader.suiteClass)
        ref_suite = unittest2.TestSuite([testcase_1])
        self.assertEqual(list(suite), [ref_suite])

    def test_loadTestsFromNames__callable__call_staticmethod(self):
        m = types.ModuleType('m')

        class Test1(unittest2.TestCase):

            def test(self):
                pass

        testcase_1 = Test1('test')

        class Foo(unittest2.TestCase):

            @staticmethod
            def foo():
                return testcase_1

        m.Foo = Foo
        loader = unittest2.TestLoader()
        suite = loader.loadTestsFromNames(['Foo.foo'], m)
        self.assertIsInstance(suite, loader.suiteClass)
        ref_suite = unittest2.TestSuite([testcase_1])
        self.assertEqual(list(suite), [ref_suite])

    def test_loadTestsFromNames__callable__wrong_type(self):
        m = types.ModuleType('m')

        def return_wrong():
            return 6

        m.return_wrong = return_wrong
        loader = unittest2.TestLoader()
        try:
            loader.loadTestsFromNames(['return_wrong'], m)
        except TypeError:
            pass
        else:
            self.fail('TestLoader.loadTestsFromNames failed to raise TypeError')

    def test_loadTestsFromNames__module_not_loaded(self):
        module_name = 'audioop'
        if module_name in sys.modules:
            del sys.modules[module_name]
        loader = unittest2.TestLoader()
        try:
            suite = loader.loadTestsFromNames([module_name])
            self.assertIsInstance(suite, loader.suiteClass)
            self.assertEqual(list(suite), [unittest2.TestSuite()])
            self.assertIn(module_name, sys.modules)
        finally:
            if module_name in sys.modules:
                del sys.modules[module_name]

    def test_getTestCaseNames(self):

        class Test(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

            def foobar(self):
                pass

        loader = unittest2.TestLoader()
        self.assertEqual(loader.getTestCaseNames(Test), ['test_1', 'test_2'])

    def test_getTestCaseNames__no_tests(self):

        class Test(unittest2.TestCase):

            def foobar(self):
                pass

        loader = unittest2.TestLoader()
        self.assertEqual(loader.getTestCaseNames(Test), [])

    def test_getTestCaseNames__not_a_TestCase(self):

        class BadCase(int):

            def test_foo(self):
                pass

        loader = unittest2.TestLoader()
        names = loader.getTestCaseNames(BadCase)
        self.assertEqual(names, ['test_foo'])

    def test_getTestCaseNames__inheritance(self):

        class TestP(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

            def foobar(self):
                pass

        class TestC(TestP):

            def test_1(self):
                pass

            def test_3(self):
                pass

        loader = unittest2.TestLoader()
        names = ['test_1', 'test_2', 'test_3']
        self.assertEqual(loader.getTestCaseNames(TestC), names)

    def test_testMethodPrefix__loadTestsFromTestCase(self):

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

            def foo_bar(self):
                pass

        tests_1 = unittest2.TestSuite([Foo('foo_bar')])
        tests_2 = unittest2.TestSuite([Foo('test_1'), Foo('test_2')])
        loader = unittest2.TestLoader()
        loader.testMethodPrefix = 'foo'
        self.assertEqual(loader.loadTestsFromTestCase(Foo), tests_1)
        loader.testMethodPrefix = 'test'
        self.assertEqual(loader.loadTestsFromTestCase(Foo), tests_2)

    def test_testMethodPrefix__loadTestsFromModule(self):
        m = types.ModuleType('m')

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

            def foo_bar(self):
                pass

        m.Foo = Foo
        tests_1 = [unittest2.TestSuite([Foo('foo_bar')])]
        tests_2 = [unittest2.TestSuite([Foo('test_1'), Foo('test_2')])]
        loader = unittest2.TestLoader()
        loader.testMethodPrefix = 'foo'
        self.assertEqual(list(loader.loadTestsFromModule(m)), tests_1)
        loader.testMethodPrefix = 'test'
        self.assertEqual(list(loader.loadTestsFromModule(m)), tests_2)

    def test_testMethodPrefix__loadTestsFromName(self):
        m = types.ModuleType('m')

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

            def foo_bar(self):
                pass

        m.Foo = Foo
        tests_1 = unittest2.TestSuite([Foo('foo_bar')])
        tests_2 = unittest2.TestSuite([Foo('test_1'), Foo('test_2')])
        loader = unittest2.TestLoader()
        loader.testMethodPrefix = 'foo'
        self.assertEqual(loader.loadTestsFromName('Foo', m), tests_1)
        loader.testMethodPrefix = 'test'
        self.assertEqual(loader.loadTestsFromName('Foo', m), tests_2)

    def test_testMethodPrefix__loadTestsFromNames(self):
        m = types.ModuleType('m')

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

            def foo_bar(self):
                pass

        m.Foo = Foo
        tests_1 = unittest2.TestSuite([unittest2.TestSuite([Foo('foo_bar')])])
        tests_2 = unittest2.TestSuite([Foo('test_1'), Foo('test_2')])
        tests_2 = unittest2.TestSuite([tests_2])
        loader = unittest2.TestLoader()
        loader.testMethodPrefix = 'foo'
        self.assertEqual(loader.loadTestsFromNames(['Foo'], m), tests_1)
        loader.testMethodPrefix = 'test'
        self.assertEqual(loader.loadTestsFromNames(['Foo'], m), tests_2)

    def test_testMethodPrefix__default_value(self):
        loader = unittest2.TestLoader()
        self.assertTrue(loader.testMethodPrefix == 'test')

    def test_sortTestMethodsUsing__loadTestsFromTestCase(self):

        def reversed_cmp(x, y):
            return -cmp(x, y)

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

        loader = unittest2.TestLoader()
        loader.sortTestMethodsUsing = reversed_cmp
        tests = loader.suiteClass([Foo('test_2'), Foo('test_1')])
        self.assertEqual(loader.loadTestsFromTestCase(Foo), tests)

    def test_sortTestMethodsUsing__loadTestsFromModule(self):

        def reversed_cmp(x, y):
            return -cmp(x, y)

        m = types.ModuleType('m')

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

        m.Foo = Foo
        loader = unittest2.TestLoader()
        loader.sortTestMethodsUsing = reversed_cmp
        tests = [loader.suiteClass([Foo('test_2'), Foo('test_1')])]
        self.assertEqual(list(loader.loadTestsFromModule(m)), tests)

    def test_sortTestMethodsUsing__loadTestsFromName(self):

        def reversed_cmp(x, y):
            return -cmp(x, y)

        m = types.ModuleType('m')

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

        m.Foo = Foo
        loader = unittest2.TestLoader()
        loader.sortTestMethodsUsing = reversed_cmp
        tests = loader.suiteClass([Foo('test_2'), Foo('test_1')])
        self.assertEqual(loader.loadTestsFromName('Foo', m), tests)

    def test_sortTestMethodsUsing__loadTestsFromNames(self):

        def reversed_cmp(x, y):
            return -cmp(x, y)

        m = types.ModuleType('m')

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

        m.Foo = Foo
        loader = unittest2.TestLoader()
        loader.sortTestMethodsUsing = reversed_cmp
        tests = [loader.suiteClass([Foo('test_2'), Foo('test_1')])]
        self.assertEqual(list(loader.loadTestsFromNames(['Foo'], m)), tests)

    def test_sortTestMethodsUsing__getTestCaseNames(self):

        def reversed_cmp(x, y):
            return -cmp(x, y)

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

        loader = unittest2.TestLoader()
        loader.sortTestMethodsUsing = reversed_cmp
        test_names = ['test_2', 'test_1']
        self.assertEqual(loader.getTestCaseNames(Foo), test_names)

    def test_sortTestMethodsUsing__default_value(self):
        loader = unittest2.TestLoader()
        self.assertTrue(loader.sortTestMethodsUsing is cmp)

    def test_sortTestMethodsUsing__None(self):

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

        loader = unittest2.TestLoader()
        loader.sortTestMethodsUsing = None
        test_names = ['test_2', 'test_1']
        self.assertEqual(set(loader.getTestCaseNames(Foo)), set(test_names))

    def test_suiteClass__loadTestsFromTestCase(self):

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

            def foo_bar(self):
                pass

        tests = [Foo('test_1'), Foo('test_2')]
        loader = unittest2.TestLoader()
        loader.suiteClass = list
        self.assertEqual(loader.loadTestsFromTestCase(Foo), tests)

    def test_suiteClass__loadTestsFromModule(self):
        m = types.ModuleType('m')

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

            def foo_bar(self):
                pass

        m.Foo = Foo
        tests = [[Foo('test_1'), Foo('test_2')]]
        loader = unittest2.TestLoader()
        loader.suiteClass = list
        self.assertEqual(loader.loadTestsFromModule(m), tests)

    def test_suiteClass__loadTestsFromName(self):
        m = types.ModuleType('m')

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

            def foo_bar(self):
                pass

        m.Foo = Foo
        tests = [Foo('test_1'), Foo('test_2')]
        loader = unittest2.TestLoader()
        loader.suiteClass = list
        self.assertEqual(loader.loadTestsFromName('Foo', m), tests)

    def test_suiteClass__loadTestsFromNames(self):
        m = types.ModuleType('m')

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

            def foo_bar(self):
                pass

        m.Foo = Foo
        tests = [[Foo('test_1'), Foo('test_2')]]
        loader = unittest2.TestLoader()
        loader.suiteClass = list
        self.assertEqual(loader.loadTestsFromNames(['Foo'], m), tests)

    def test_suiteClass__default_value(self):
        loader = unittest2.TestLoader()
        self.assertTrue(loader.suiteClass is unittest2.TestSuite)


class Foo(unittest2.TestCase):

    def test_1(self):
        pass

    def test_2(self):
        pass

    def test_3(self):
        pass

    def runTest(self):
        pass


def _mk_TestSuite(*names):
    return unittest2.TestSuite((Foo(n) for n in names))


class Test_TestSuite(unittest2.TestCase, TestEquality):
    eq_pairs = [(unittest2.TestSuite(), unittest2.TestSuite()), (unittest2.TestSuite(), unittest2.TestSuite([])), (_mk_TestSuite('test_1'), _mk_TestSuite('test_1'))]
    ne_pairs = [(unittest2.TestSuite(), _mk_TestSuite('test_1')),
     (unittest2.TestSuite([]), _mk_TestSuite('test_1')),
     (_mk_TestSuite('test_1', 'test_2'), _mk_TestSuite('test_1', 'test_3')),
     (_mk_TestSuite('test_1'), _mk_TestSuite('test_2'))]

    def test_init__tests_optional(self):
        suite = unittest2.TestSuite()
        self.assertEqual(suite.countTestCases(), 0)

    def test_init__empty_tests(self):
        suite = unittest2.TestSuite([])
        self.assertEqual(suite.countTestCases(), 0)

    def test_init__tests_from_any_iterable(self):

        def tests():
            yield unittest2.FunctionTestCase(lambda : None)
            yield unittest2.FunctionTestCase(lambda : None)

        suite_1 = unittest2.TestSuite(tests())
        self.assertEqual(suite_1.countTestCases(), 2)
        suite_2 = unittest2.TestSuite(suite_1)
        self.assertEqual(suite_2.countTestCases(), 2)
        suite_3 = unittest2.TestSuite(set(suite_1))
        self.assertEqual(suite_3.countTestCases(), 2)

    def test_init__TestSuite_instances_in_tests(self):

        def tests():
            ftc = unittest2.FunctionTestCase(lambda : None)
            yield unittest2.TestSuite([ftc])
            yield unittest2.FunctionTestCase(lambda : None)

        suite = unittest2.TestSuite(tests())
        self.assertEqual(suite.countTestCases(), 2)

    def test_iter(self):
        test1 = unittest2.FunctionTestCase(lambda : None)
        test2 = unittest2.FunctionTestCase(lambda : None)
        suite = unittest2.TestSuite((test1, test2))
        self.assertEqual(list(suite), [test1, test2])

    def test_countTestCases_zero_simple(self):
        suite = unittest2.TestSuite()
        self.assertEqual(suite.countTestCases(), 0)

    def test_countTestCases_zero_nested(self):

        class Test1(unittest2.TestCase):

            def test(self):
                pass

        suite = unittest2.TestSuite([unittest2.TestSuite()])
        self.assertEqual(suite.countTestCases(), 0)

    def test_countTestCases_simple(self):
        test1 = unittest2.FunctionTestCase(lambda : None)
        test2 = unittest2.FunctionTestCase(lambda : None)
        suite = unittest2.TestSuite((test1, test2))
        self.assertEqual(suite.countTestCases(), 2)

    def test_countTestCases_nested(self):

        class Test1(unittest2.TestCase):

            def test1(self):
                pass

            def test2(self):
                pass

        test2 = unittest2.FunctionTestCase(lambda : None)
        test3 = unittest2.FunctionTestCase(lambda : None)
        child = unittest2.TestSuite((Test1('test2'), test2))
        parent = unittest2.TestSuite((test3, child, Test1('test1')))
        self.assertEqual(parent.countTestCases(), 4)

    def test_run__empty_suite(self):
        events = []
        result = LoggingResult(events)
        suite = unittest2.TestSuite()
        suite.run(result)
        self.assertEqual(events, [])

    def test_run__requires_result(self):
        suite = unittest2.TestSuite()
        try:
            suite.run()
        except TypeError:
            pass
        else:
            self.fail('Failed to raise TypeError')

    def test_run(self):
        events = []
        result = LoggingResult(events)

        class LoggingCase(unittest2.TestCase):

            def run(self, result):
                events.append('run %s' % self._testMethodName)

            def test1(self):
                pass

            def test2(self):
                pass

        tests = [LoggingCase('test1'), LoggingCase('test2')]
        unittest2.TestSuite(tests).run(result)
        self.assertEqual(events, ['run test1', 'run test2'])

    def test_addTest__TestCase(self):

        class Foo(unittest2.TestCase):

            def test(self):
                pass

        test = Foo('test')
        suite = unittest2.TestSuite()
        suite.addTest(test)
        self.assertEqual(suite.countTestCases(), 1)
        self.assertEqual(list(suite), [test])

    def test_addTest__TestSuite(self):

        class Foo(unittest2.TestCase):

            def test(self):
                pass

        suite_2 = unittest2.TestSuite([Foo('test')])
        suite = unittest2.TestSuite()
        suite.addTest(suite_2)
        self.assertEqual(suite.countTestCases(), 1)
        self.assertEqual(list(suite), [suite_2])

    def test_addTests(self):

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

        test_1 = Foo('test_1')
        test_2 = Foo('test_2')
        inner_suite = unittest2.TestSuite([test_2])

        def gen():
            yield test_1
            yield test_2
            yield inner_suite

        suite_1 = unittest2.TestSuite()
        suite_1.addTests(gen())
        self.assertEqual(list(suite_1), list(gen()))
        suite_2 = unittest2.TestSuite()
        for t in gen():
            suite_2.addTest(t)

        self.assertEqual(suite_1, suite_2)

    def test_addTest__noniterable(self):
        suite = unittest2.TestSuite()
        try:
            suite.addTests(5)
        except TypeError:
            pass
        else:
            self.fail('Failed to raise TypeError')

    def test_addTest__noncallable(self):
        suite = unittest2.TestSuite()
        self.assertRaises(TypeError, suite.addTest, 5)

    def test_addTest__casesuiteclass(self):
        suite = unittest2.TestSuite()
        self.assertRaises(TypeError, suite.addTest, Test_TestSuite)
        self.assertRaises(TypeError, suite.addTest, unittest2.TestSuite)

    def test_addTests__string(self):
        suite = unittest2.TestSuite()
        self.assertRaises(TypeError, suite.addTests, 'foo')


class Test_FunctionTestCase(unittest2.TestCase):

    def test_countTestCases(self):
        test = unittest2.FunctionTestCase(lambda : None)
        self.assertEqual(test.countTestCases(), 1)

    def test_run_call_order__error_in_setUp(self):
        events = []
        result = LoggingResult(events)

        def setUp():
            events.append('setUp')
            raise RuntimeError('raised by setUp')

        def test():
            events.append('test')

        def tearDown():
            events.append('tearDown')

        expected = ['startTest',
         'setUp',
         'addError',
         'stopTest']
        unittest2.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_test(self):
        events = []
        result = LoggingResult(events)

        def setUp():
            events.append('setUp')

        def test():
            events.append('test')
            raise RuntimeError('raised by test')

        def tearDown():
            events.append('tearDown')

        expected = ['startTest',
         'setUp',
         'test',
         'addError',
         'tearDown',
         'stopTest']
        unittest2.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    def test_run_call_order__failure_in_test(self):
        events = []
        result = LoggingResult(events)

        def setUp():
            events.append('setUp')

        def test():
            events.append('test')
            self.fail('raised by test')

        def tearDown():
            events.append('tearDown')

        expected = ['startTest',
         'setUp',
         'test',
         'addFailure',
         'tearDown',
         'stopTest']
        unittest2.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_tearDown(self):
        events = []
        result = LoggingResult(events)

        def setUp():
            events.append('setUp')

        def test():
            events.append('test')

        def tearDown():
            events.append('tearDown')
            raise RuntimeError('raised by tearDown')

        expected = ['startTest',
         'setUp',
         'test',
         'tearDown',
         'addError',
         'stopTest']
        unittest2.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    def test_id(self):
        test = unittest2.FunctionTestCase(lambda : None)
        self.assertIsInstance(test.id(), basestring)

    def test_shortDescription__no_docstring(self):
        test = unittest2.FunctionTestCase(lambda : None)
        self.assertEqual(test.shortDescription(), None)

    def test_shortDescription__singleline_docstring(self):
        desc = 'this tests foo'
        test = unittest2.FunctionTestCase(lambda : None, description=desc)
        self.assertEqual(test.shortDescription(), 'this tests foo')


class Test_TestResult(unittest2.TestCase):

    def test_init(self):
        result = unittest2.TestResult()
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(result.shouldStop, False)

    def test_stop(self):
        result = unittest2.TestResult()
        result.stop()
        self.assertEqual(result.shouldStop, True)

    def test_startTest(self):

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

        test = Foo('test_1')
        result = unittest2.TestResult()
        result.startTest(test)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)
        result.stopTest(test)

    def test_stopTest(self):

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

        test = Foo('test_1')
        result = unittest2.TestResult()
        result.startTest(test)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)
        result.stopTest(test)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

    def test_startTestRun_stopTestRun(self):
        result = unittest2.TestResult()
        result.startTestRun()
        result.stopTestRun()

    def test_addSuccess(self):

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

        test = Foo('test_1')
        result = unittest2.TestResult()
        result.startTest(test)
        result.addSuccess(test)
        result.stopTest(test)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

    def test_addFailure(self):

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

        test = Foo('test_1')
        try:
            test.fail('foo')
        except:
            exc_info_tuple = sys.exc_info()

        result = unittest2.TestResult()
        result.startTest(test)
        result.addFailure(test, exc_info_tuple)
        result.stopTest(test)
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)
        test_case, formatted_exc = result.failures[0]
        self.assertTrue(test_case is test)
        self.assertIsInstance(formatted_exc, str)

    def test_addError(self):

        class Foo(unittest2.TestCase):

            def test_1(self):
                pass

        test = Foo('test_1')
        try:
            raise TypeError()
        except:
            exc_info_tuple = sys.exc_info()

        result = unittest2.TestResult()
        result.startTest(test)
        result.addError(test, exc_info_tuple)
        result.stopTest(test)
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)
        test_case, formatted_exc = result.errors[0]
        self.assertTrue(test_case is test)
        self.assertIsInstance(formatted_exc, str)

    def testGetDescriptionWithoutDocstring(self):
        result = unittest2.TextTestResult(None, True, 1)
        self.assertEqual(result.getDescription(self), 'testGetDescriptionWithoutDocstring (' + __name__ + '.Test_TestResult)')

    def testGetDescriptionWithOneLineDocstring(self):
        result = unittest2.TextTestResult(None, True, 1)
        self.assertEqual(result.getDescription(self), 'testGetDescriptionWithOneLineDocstring (' + __name__ + '.Test_TestResult)\nTests getDescription() for a method with a docstring.')

    def testGetDescriptionWithMultiLineDocstring(self):
        result = unittest2.TextTestResult(None, True, 1)
        self.assertEqual(result.getDescription(self), 'testGetDescriptionWithMultiLineDocstring (' + __name__ + '.Test_TestResult)\nTests getDescription() for a method with a longer docstring.')


class Foo(unittest2.TestCase):

    def runTest(self):
        pass

    def test1(self):
        pass


class Bar(Foo):

    def test2(self):
        pass


def GetLoggingTestCase():

    class LoggingTestCase(unittest2.TestCase):

        def __init__(self, events):
            super(LoggingTestCase, self).__init__('test')
            self.events = events

        def setUp(self):
            self.events.append('setUp')

        def test(self):
            self.events.append('test')

        def tearDown(self):
            self.events.append('tearDown')

    return LoggingTestCase


class ResultWithNoStartTestRunStopTestRun(object):

    def __init__(self):
        self.failures = []
        self.errors = []
        self.testsRun = 0
        self.skipped = []
        self.expectedFailures = []
        self.unexpectedSuccesses = []
        self.shouldStop = False

    def startTest(self, test):
        pass

    def stopTest(self, test):
        pass

    def addError(self, test):
        pass

    def addFailure(self, test):
        pass

    def addSuccess(self, test):
        pass

    def wasSuccessful(self):
        return True


class Test_TestCase(unittest2.TestCase, TestEquality, TestHashing):
    eq_pairs = [(Foo('test1'), Foo('test1'))]
    ne_pairs = [(Foo('test1'), Foo('runTest')), (Foo('test1'), Bar('test1')), (Foo('test1'), Bar('test2'))]

    def test_init__no_test_name(self):

        class Test(unittest2.TestCase):

            def runTest(self):
                raise MyException()

            def test(self):
                pass

        self.assertEqual(Test().id()[-13:], '.Test.runTest')

    def test_init__test_name__valid(self):

        class Test(unittest2.TestCase):

            def runTest(self):
                raise MyException()

            def test(self):
                pass

        self.assertEqual(Test('test').id()[-10:], '.Test.test')

    def test_init__test_name__invalid(self):

        class Test(unittest2.TestCase):

            def runTest(self):
                raise MyException()

            def test(self):
                pass

        try:
            Test('testfoo')
        except ValueError:
            pass
        else:
            self.fail('Failed to raise ValueError')

    def test_countTestCases(self):

        class Foo(unittest2.TestCase):

            def test(self):
                pass

        self.assertEqual(Foo('test').countTestCases(), 1)

    def test_defaultTestResult(self):

        class Foo(unittest2.TestCase):

            def runTest(self):
                pass

        result = Foo().defaultTestResult()
        self.assertEqual(type(result), unittest2.TestResult)

    def test_run_call_order__error_in_setUp(self):
        events = []
        result = LoggingResult(events)

        class Foo(GetLoggingTestCase()):

            def setUp(self):
                super(Foo, self).setUp()
                raise RuntimeError('raised by Foo.setUp')

        Foo(events).run(result)
        expected = ['startTest',
         'setUp',
         'addError',
         'stopTest']
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_setUp_default_result(self):
        events = []

        class Foo(GetLoggingTestCase()):

            def defaultTestResult(self):
                return LoggingResult(self.events)

            def setUp(self):
                super(Foo, self).setUp()
                raise RuntimeError('raised by Foo.setUp')

        Foo(events).run()
        expected = ['startTestRun',
         'startTest',
         'setUp',
         'addError',
         'stopTest',
         'stopTestRun']
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_test(self):
        events = []
        result = LoggingResult(events)

        class Foo(GetLoggingTestCase()):

            def test(self):
                super(Foo, self).test()
                raise RuntimeError('raised by Foo.test')

        expected = ['startTest',
         'setUp',
         'test',
         'addError',
         'tearDown',
         'stopTest']
        Foo(events).run(result)
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_test_default_result(self):
        events = []

        class Foo(GetLoggingTestCase()):

            def defaultTestResult(self):
                return LoggingResult(self.events)

            def test(self):
                super(Foo, self).test()
                raise RuntimeError('raised by Foo.test')

        expected = ['startTestRun',
         'startTest',
         'setUp',
         'test',
         'addError',
         'tearDown',
         'stopTest',
         'stopTestRun']
        Foo(events).run()
        self.assertEqual(events, expected)

    def test_run_call_order__failure_in_test(self):
        events = []
        result = LoggingResult(events)

        class Foo(GetLoggingTestCase()):

            def test(self):
                super(Foo, self).test()
                self.fail('raised by Foo.test')

        expected = ['startTest',
         'setUp',
         'test',
         'addFailure',
         'tearDown',
         'stopTest']
        Foo(events).run(result)
        self.assertEqual(events, expected)

    def test_run_call_order__failure_in_test_default_result(self):

        class Foo(GetLoggingTestCase()):

            def defaultTestResult(self):
                return LoggingResult(self.events)

            def test(self):
                super(Foo, self).test()
                self.fail('raised by Foo.test')

        expected = ['startTestRun',
         'startTest',
         'setUp',
         'test',
         'addFailure',
         'tearDown',
         'stopTest',
         'stopTestRun']
        events = []
        Foo(events).run()
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_tearDown(self):
        events = []
        result = LoggingResult(events)

        class Foo(GetLoggingTestCase()):

            def tearDown(self):
                super(Foo, self).tearDown()
                raise RuntimeError('raised by Foo.tearDown')

        Foo(events).run(result)
        expected = ['startTest',
         'setUp',
         'test',
         'tearDown',
         'addError',
         'stopTest']
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_tearDown_default_result(self):

        class Foo(GetLoggingTestCase()):

            def defaultTestResult(self):
                return LoggingResult(self.events)

            def tearDown(self):
                super(Foo, self).tearDown()
                raise RuntimeError('raised by Foo.tearDown')

        events = []
        Foo(events).run()
        expected = ['startTestRun',
         'startTest',
         'setUp',
         'test',
         'tearDown',
         'addError',
         'stopTest',
         'stopTestRun']
        self.assertEqual(events, expected)

    def test_run_call_order_default_result(self):

        class Foo(unittest2.TestCase):

            def defaultTestResult(self):
                return ResultWithNoStartTestRunStopTestRun()

            def test(self):
                pass

        Foo('test').run()

    def test_failureException__default(self):

        class Foo(unittest2.TestCase):

            def test(self):
                pass

        self.assertTrue(Foo('test').failureException is AssertionError)

    def test_failureException__subclassing__explicit_raise(self):
        events = []
        result = LoggingResult(events)

        class Foo(unittest2.TestCase):

            def test(self):
                raise RuntimeError()

            failureException = RuntimeError

        self.assertTrue(Foo('test').failureException is RuntimeError)
        Foo('test').run(result)
        expected = ['startTest', 'addFailure', 'stopTest']
        self.assertEqual(events, expected)

    def test_failureException__subclassing__implicit_raise(self):
        events = []
        result = LoggingResult(events)

        class Foo(unittest2.TestCase):

            def test(self):
                self.fail('foo')

            failureException = RuntimeError

        self.assertTrue(Foo('test').failureException is RuntimeError)
        Foo('test').run(result)
        expected = ['startTest', 'addFailure', 'stopTest']
        self.assertEqual(events, expected)

    def test_setUp(self):

        class Foo(unittest2.TestCase):

            def runTest(self):
                pass

        Foo().setUp()

    def test_tearDown(self):

        class Foo(unittest2.TestCase):

            def runTest(self):
                pass

        Foo().tearDown()

    def test_id(self):

        class Foo(unittest2.TestCase):

            def runTest(self):
                pass

        self.assertIsInstance(Foo().id(), basestring)

    def test_run__uses_defaultTestResult(self):
        events = []

        class Foo(unittest2.TestCase):

            def test(self):
                events.append('test')

            def defaultTestResult(self):
                return LoggingResult(events)

        Foo('test').run()
        expected = ['startTestRun',
         'startTest',
         'test',
         'addSuccess',
         'stopTest',
         'stopTestRun']
        self.assertEqual(events, expected)

    def testShortDescriptionWithoutDocstring(self):
        self.assertIsNone(self.shortDescription())

    def testShortDescriptionWithOneLineDocstring(self):
        self.assertEqual(self.shortDescription(), 'Tests shortDescription() for a method with a docstring.')

    def testShortDescriptionWithMultiLineDocstring(self):
        self.assertEqual(self.shortDescription(), 'Tests shortDescription() for a method with a longer docstring.')

    def testAddTypeEqualityFunc(self):

        class SadSnake(object):
            pass

        s1, s2 = SadSnake(), SadSnake()
        self.assertFalse(s1 == s2)

        def AllSnakesCreatedEqual(a, b, msg = None):
            return type(a) == type(b) == SadSnake

        self.addTypeEqualityFunc(SadSnake, AllSnakesCreatedEqual)
        self.assertEqual(s1, s2)

    def testAssertIs(self):
        thing = object()
        self.assertIs(thing, thing)
        self.assertRaises(self.failureException, self.assertIs, thing, object())

    def testAssertIsNot(self):
        thing = object()
        self.assertIsNot(thing, object())
        self.assertRaises(self.failureException, self.assertIsNot, thing, thing)

    def testAssertIsInstance(self):
        thing = []
        self.assertIsInstance(thing, list)
        self.assertRaises(self.failureException, self.assertIsInstance, thing, dict)

    def testAssertNotIsInstance(self):
        thing = []
        self.assertNotIsInstance(thing, dict)
        self.assertRaises(self.failureException, self.assertNotIsInstance, thing, list)

    def testAssertIn(self):
        animals = {'monkey': 'banana',
         'cow': 'grass',
         'seal': 'fish'}
        self.assertIn('a', 'abc')
        self.assertIn(2, [1, 2, 3])
        self.assertIn('monkey', animals)
        self.assertNotIn('d', 'abc')
        self.assertNotIn(0, [1, 2, 3])
        self.assertNotIn('otter', animals)
        self.assertRaises(self.failureException, self.assertIn, 'x', 'abc')
        self.assertRaises(self.failureException, self.assertIn, 4, [1, 2, 3])
        self.assertRaises(self.failureException, self.assertIn, 'elephant', animals)
        self.assertRaises(self.failureException, self.assertNotIn, 'c', 'abc')
        self.assertRaises(self.failureException, self.assertNotIn, 1, [1, 2, 3])
        self.assertRaises(self.failureException, self.assertNotIn, 'cow', animals)

    def testAssertDictContainsSubset(self):
        self.assertDictContainsSubset({}, {})
        self.assertDictContainsSubset({}, {'a': 1})
        self.assertDictContainsSubset({'a': 1}, {'a': 1})
        self.assertDictContainsSubset({'a': 1}, {'a': 1,
         'b': 2})
        self.assertDictContainsSubset({'a': 1,
         'b': 2}, {'a': 1,
         'b': 2})
        self.assertRaises(unittest2.TestCase.failureException, self.assertDictContainsSubset, {'a': 2}, {'a': 1}, '.*Mismatched values:.*')
        self.assertRaises(unittest2.TestCase.failureException, self.assertDictContainsSubset, {'c': 1}, {'a': 1}, '.*Missing:.*')
        self.assertRaises(unittest2.TestCase.failureException, self.assertDictContainsSubset, {'a': 1,
         'c': 1}, {'a': 1}, '.*Missing:.*')
        self.assertRaises(unittest2.TestCase.failureException, self.assertDictContainsSubset, {'a': 1,
         'c': 1}, {'a': 1}, '.*Missing:.*Mismatched values:.*')
        self.assertRaises(self.failureException, self.assertDictContainsSubset, {1: 'one'}, {})
        one = ''.join((chr(i) for i in range(255)))
        self.assertRaises(self.failureException, self.assertDictContainsSubset, {'foo': one}, {'foo': u'\ufffd'})

    def testAssertEqual(self):
        equal_pairs = [((), ()),
         ({}, {}),
         ([], []),
         (set(), set()),
         (frozenset(), frozenset())]
        for a, b in equal_pairs:
            try:
                self.assertEqual(a, b)
            except self.failureException:
                self.fail('assertEqual(%r, %r) failed' % (a, b))

            try:
                self.assertEqual(a, b, msg='foo')
            except self.failureException:
                self.fail('assertEqual(%r, %r) with msg= failed' % (a, b))

            try:
                self.assertEqual(a, b, 'foo')
            except self.failureException:
                self.fail('assertEqual(%r, %r) with third parameter failed' % (a, b))

        unequal_pairs = [((), []),
         ({}, set()),
         (set([4, 1]), frozenset([4, 2])),
         (frozenset([4, 5]), set([2, 3])),
         (set([3, 4]), set([5, 4]))]
        for a, b in unequal_pairs:
            self.assertRaises(self.failureException, self.assertEqual, a, b)
            self.assertRaises(self.failureException, self.assertEqual, a, b, 'foo')
            self.assertRaises(self.failureException, self.assertEqual, a, b, msg='foo')

    def testEquality(self):
        self.assertListEqual([], [])
        self.assertTupleEqual((), ())
        self.assertSequenceEqual([], ())
        a = [0, 'a', []]
        b = []
        self.assertRaises(unittest2.TestCase.failureException, self.assertListEqual, a, b)
        self.assertRaises(unittest2.TestCase.failureException, self.assertListEqual, tuple(a), tuple(b))
        self.assertRaises(unittest2.TestCase.failureException, self.assertSequenceEqual, a, tuple(b))
        b.extend(a)
        self.assertListEqual(a, b)
        self.assertTupleEqual(tuple(a), tuple(b))
        self.assertSequenceEqual(a, tuple(b))
        self.assertSequenceEqual(tuple(a), b)
        self.assertRaises(self.failureException, self.assertListEqual, a, tuple(b))
        self.assertRaises(self.failureException, self.assertTupleEqual, tuple(a), b)
        self.assertRaises(self.failureException, self.assertListEqual, None, b)
        self.assertRaises(self.failureException, self.assertTupleEqual, None, tuple(b))
        self.assertRaises(self.failureException, self.assertSequenceEqual, None, tuple(b))
        self.assertRaises(self.failureException, self.assertListEqual, 1, 1)
        self.assertRaises(self.failureException, self.assertTupleEqual, 1, 1)
        self.assertRaises(self.failureException, self.assertSequenceEqual, 1, 1)
        self.assertDictEqual({}, {})
        c = {'x': 1}
        d = {}
        self.assertRaises(unittest2.TestCase.failureException, self.assertDictEqual, c, d)
        d.update(c)
        self.assertDictEqual(c, d)
        d['x'] = 0
        self.assertRaises(unittest2.TestCase.failureException, self.assertDictEqual, c, d, 'These are unequal')
        self.assertRaises(self.failureException, self.assertDictEqual, None, d)
        self.assertRaises(self.failureException, self.assertDictEqual, [], d)
        self.assertRaises(self.failureException, self.assertDictEqual, 1, 1)
        self.assertSameElements([1, 2, 3], [3, 2, 1])
        self.assertSameElements([1, 2] + [3] * 100, [1] * 100 + [2, 3])
        self.assertSameElements(['foo', 'bar', 'baz'], ['bar', 'baz', 'foo'])
        self.assertRaises(self.failureException, self.assertSameElements, [10], [10, 11])
        self.assertRaises(self.failureException, self.assertSameElements, [10, 11], [10])
        self.assertSameElements([[1, 2], [3, 4]], [[3, 4], [1, 2]])
        self.assertSameElements([{'a': 1}, {'b': 2}], [{'b': 2}, {'a': 1}])
        self.assertRaises(self.failureException, self.assertSameElements, [[1]], [[2]])

    def testAssertSetEqual(self):
        set1 = set()
        set2 = set()
        self.assertSetEqual(set1, set2)
        self.assertRaises(self.failureException, self.assertSetEqual, None, set2)
        self.assertRaises(self.failureException, self.assertSetEqual, [], set2)
        self.assertRaises(self.failureException, self.assertSetEqual, set1, None)
        self.assertRaises(self.failureException, self.assertSetEqual, set1, [])
        set1 = set(['a'])
        set2 = set()
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)
        set1 = set(['a'])
        set2 = set(['a'])
        self.assertSetEqual(set1, set2)
        set1 = set(['a'])
        set2 = set(['a', 'b'])
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)
        set1 = set(['a'])
        set2 = frozenset(['a', 'b'])
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)
        set1 = set(['a', 'b'])
        set2 = frozenset(['a', 'b'])
        self.assertSetEqual(set1, set2)
        set1 = set()
        set2 = 'foo'
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)
        self.assertRaises(self.failureException, self.assertSetEqual, set2, set1)
        set1 = set([(0, 1), (2, 3)])
        set2 = set([(4, 5)])
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)

    def testInequality(self):
        self.assertGreater(2, 1)
        self.assertGreaterEqual(2, 1)
        self.assertGreaterEqual(1, 1)
        self.assertLess(1, 2)
        self.assertLessEqual(1, 2)
        self.assertLessEqual(1, 1)
        self.assertRaises(self.failureException, self.assertGreater, 1, 2)
        self.assertRaises(self.failureException, self.assertGreater, 1, 1)
        self.assertRaises(self.failureException, self.assertGreaterEqual, 1, 2)
        self.assertRaises(self.failureException, self.assertLess, 2, 1)
        self.assertRaises(self.failureException, self.assertLess, 1, 1)
        self.assertRaises(self.failureException, self.assertLessEqual, 2, 1)
        self.assertGreater(1.1, 1.0)
        self.assertGreaterEqual(1.1, 1.0)
        self.assertGreaterEqual(1.0, 1.0)
        self.assertLess(1.0, 1.1)
        self.assertLessEqual(1.0, 1.1)
        self.assertLessEqual(1.0, 1.0)
        self.assertRaises(self.failureException, self.assertGreater, 1.0, 1.1)
        self.assertRaises(self.failureException, self.assertGreater, 1.0, 1.0)
        self.assertRaises(self.failureException, self.assertGreaterEqual, 1.0, 1.1)
        self.assertRaises(self.failureException, self.assertLess, 1.1, 1.0)
        self.assertRaises(self.failureException, self.assertLess, 1.0, 1.0)
        self.assertRaises(self.failureException, self.assertLessEqual, 1.1, 1.0)
        self.assertGreater('bug', 'ant')
        self.assertGreaterEqual('bug', 'ant')
        self.assertGreaterEqual('ant', 'ant')
        self.assertLess('ant', 'bug')
        self.assertLessEqual('ant', 'bug')
        self.assertLessEqual('ant', 'ant')
        self.assertRaises(self.failureException, self.assertGreater, 'ant', 'bug')
        self.assertRaises(self.failureException, self.assertGreater, 'ant', 'ant')
        self.assertRaises(self.failureException, self.assertGreaterEqual, 'ant', 'bug')
        self.assertRaises(self.failureException, self.assertLess, 'bug', 'ant')
        self.assertRaises(self.failureException, self.assertLess, 'ant', 'ant')
        self.assertRaises(self.failureException, self.assertLessEqual, 'bug', 'ant')
        self.assertGreater(u'bug', u'ant')
        self.assertGreaterEqual(u'bug', u'ant')
        self.assertGreaterEqual(u'ant', u'ant')
        self.assertLess(u'ant', u'bug')
        self.assertLessEqual(u'ant', u'bug')
        self.assertLessEqual(u'ant', u'ant')
        self.assertRaises(self.failureException, self.assertGreater, u'ant', u'bug')
        self.assertRaises(self.failureException, self.assertGreater, u'ant', u'ant')
        self.assertRaises(self.failureException, self.assertGreaterEqual, u'ant', u'bug')
        self.assertRaises(self.failureException, self.assertLess, u'bug', u'ant')
        self.assertRaises(self.failureException, self.assertLess, u'ant', u'ant')
        self.assertRaises(self.failureException, self.assertLessEqual, u'bug', u'ant')
        self.assertGreater('bug', u'ant')
        self.assertGreater(u'bug', 'ant')
        self.assertGreaterEqual('bug', u'ant')
        self.assertGreaterEqual(u'bug', 'ant')
        self.assertGreaterEqual('ant', u'ant')
        self.assertGreaterEqual(u'ant', 'ant')
        self.assertLess('ant', u'bug')
        self.assertLess(u'ant', 'bug')
        self.assertLessEqual('ant', u'bug')
        self.assertLessEqual(u'ant', 'bug')
        self.assertLessEqual('ant', u'ant')
        self.assertLessEqual(u'ant', 'ant')
        self.assertRaises(self.failureException, self.assertGreater, 'ant', u'bug')
        self.assertRaises(self.failureException, self.assertGreater, u'ant', 'bug')
        self.assertRaises(self.failureException, self.assertGreater, 'ant', u'ant')
        self.assertRaises(self.failureException, self.assertGreater, u'ant', 'ant')
        self.assertRaises(self.failureException, self.assertGreaterEqual, 'ant', u'bug')
        self.assertRaises(self.failureException, self.assertGreaterEqual, u'ant', 'bug')
        self.assertRaises(self.failureException, self.assertLess, 'bug', u'ant')
        self.assertRaises(self.failureException, self.assertLess, u'bug', 'ant')
        self.assertRaises(self.failureException, self.assertLess, 'ant', u'ant')
        self.assertRaises(self.failureException, self.assertLess, u'ant', 'ant')
        self.assertRaises(self.failureException, self.assertLessEqual, 'bug', u'ant')
        self.assertRaises(self.failureException, self.assertLessEqual, u'bug', 'ant')

    def testAssertMultiLineEqual(self):
        sample_text = 'http://www.python.org/doc/2.3/lib/module-unittest.html\ntest case\n    A test case is the smallest unit of testing. [...]\n'
        revised_sample_text = 'http://www.python.org/doc/2.4.1/lib/module-unittest.html\ntest case\n    A test case is the smallest unit of testing. [...] You may provide your\n    own implementation that does not subclass from TestCase, of course.\n'
        sample_text_error = '\n- http://www.python.org/doc/2.3/lib/module-unittest.html\n?                             ^\n+ http://www.python.org/doc/2.4.1/lib/module-unittest.html\n?                             ^^^\n  test case\n-     A test case is the smallest unit of testing. [...]\n+     A test case is the smallest unit of testing. [...] You may provide your\n?                                                       +++++++++++++++++++++\n+     own implementation that does not subclass from TestCase, of course.\n'
        for type_changer in (lambda x: x, lambda x: x.decode('utf8')):
            try:
                self.assertMultiLineEqual(type_changer(sample_text), type_changer(revised_sample_text))
            except self.failureException as e:
                self.assertTrue(sample_text_error == str(e).encode('utf8'))

    def testAssertIsNone(self):
        self.assertIsNone(None)
        self.assertRaises(self.failureException, self.assertIsNone, False)
        self.assertIsNotNone('DjZoPloGears on Rails')
        self.assertRaises(self.failureException, self.assertIsNotNone, None)

    def testAssertRegexpMatches(self):
        self.assertRegexpMatches('asdfabasdf', 'ab+')
        self.assertRaises(self.failureException, self.assertRegexpMatches, 'saaas', 'aaaa')

    def testAssertRaisesRegexp(self):

        class ExceptionMock(Exception):
            pass

        def Stub():
            raise ExceptionMock('We expect')

        self.assertRaisesRegexp(ExceptionMock, re.compile('expect$'), Stub)
        self.assertRaisesRegexp(ExceptionMock, 'expect$', Stub)
        self.assertRaisesRegexp(ExceptionMock, u'expect$', Stub)

    def testAssertNotRaisesRegexp(self):
        self.assertRaisesRegexp(self.failureException, '^Exception not raised$', self.assertRaisesRegexp, Exception, re.compile('x'), lambda : None)
        self.assertRaisesRegexp(self.failureException, '^Exception not raised$', self.assertRaisesRegexp, Exception, 'x', lambda : None)
        self.assertRaisesRegexp(self.failureException, '^Exception not raised$', self.assertRaisesRegexp, Exception, u'x', lambda : None)

    def testAssertRaisesRegexpMismatch(self):

        def Stub():
            raise Exception('Unexpected')

        self.assertRaisesRegexp(self.failureException, '"\\^Expected\\$" does not match "Unexpected"', self.assertRaisesRegexp, Exception, '^Expected$', Stub)
        self.assertRaisesRegexp(self.failureException, '"\\^Expected\\$" does not match "Unexpected"', self.assertRaisesRegexp, Exception, u'^Expected$', Stub)
        self.assertRaisesRegexp(self.failureException, '"\\^Expected\\$" does not match "Unexpected"', self.assertRaisesRegexp, Exception, re.compile('^Expected$'), Stub)

    def testSynonymAssertMethodNames(self):
        self.assertNotEquals(3, 5)
        self.assertEquals(3, 3)
        self.assertAlmostEquals(2.0, 2.0)
        self.assertNotAlmostEquals(3.0, 5.0)
        self.assert_(True)

    def testPendingDeprecationMethodNames(self):
        self.failIfEqual(3, 5)
        self.assertEqual(3, 3)
        self.failUnlessAlmostEqual(2.0, 2.0)
        self.failIfAlmostEqual(3.0, 5.0)
        self.assertTrue(True)
        self.failUnlessRaises(TypeError, lambda _: 3.14 + u'spam')
        self.assertFalse(False)

    def testDeepcopy(self):

        class TestableTest(unittest2.TestCase):

            def testNothing(self):
                pass

        test = TestableTest('testNothing')
        deepcopy(test)


class Test_TestSkipping(unittest2.TestCase):

    def test_skipping(self):

        class Foo(unittest2.TestCase):

            def test_skip_me(self):
                self.skipTest('skip')

        events = []
        result = LoggingResult(events)
        test = Foo('test_skip_me')
        test.run(result)
        self.assertEqual(events, ['startTest', 'addSkip', 'stopTest'])
        self.assertEqual(result.skipped, [(test, 'skip')])

        class Foo(unittest2.TestCase):

            def setUp(self):
                self.skipTest('testing')

            def test_nothing(self):
                pass

        events = []
        result = LoggingResult(events)
        test = Foo('test_nothing')
        test.run(result)
        self.assertEqual(events, ['startTest', 'addSkip', 'stopTest'])
        self.assertEqual(result.skipped, [(test, 'testing')])
        self.assertEqual(result.testsRun, 1)

    def test_skipping_decorators(self):
        op_table = ((unittest2.skipUnless, False, True), (unittest2.skipIf, True, False))
        for deco, do_skip, dont_skip in op_table:

            class Foo(unittest2.TestCase):

                @deco(do_skip, 'testing')
                def test_skip(self):
                    pass

                @deco(dont_skip, 'testing')
                def test_dont_skip(self):
                    pass

            test_do_skip = Foo('test_skip')
            test_dont_skip = Foo('test_dont_skip')
            suite = unittest2.TestSuite([test_do_skip, test_dont_skip])
            events = []
            result = LoggingResult(events)
            suite.run(result)
            self.assertEqual(len(result.skipped), 1)
            expected = ['startTest',
             'addSkip',
             'stopTest',
             'startTest',
             'addSuccess',
             'stopTest']
            self.assertEqual(events, expected)
            self.assertEqual(result.testsRun, 2)
            self.assertEqual(result.skipped, [(test_do_skip, 'testing')])
            self.assertTrue(result.wasSuccessful())

    def test_skip_class(self):

        class Foo(unittest2.TestCase):

            def test_1(self):
                record.append(1)

        Foo = unittest2.skip('testing')(Foo)
        record = []
        result = unittest2.TestResult()
        test = Foo('test_1')
        suite = unittest2.TestSuite([test])
        suite.run(result)
        self.assertEqual(result.skipped, [(test, 'testing')])
        self.assertEqual(record, [])

    def test_expected_failure(self):

        class Foo(unittest2.TestCase):

            @unittest2.expectedFailure
            def test_die(self):
                self.fail('help me!')

        events = []
        result = LoggingResult(events)
        test = Foo('test_die')
        test.run(result)
        self.assertEqual(events, ['startTest', 'addExpectedFailure', 'stopTest'])
        self.assertEqual(result.expectedFailures[0][0], test)
        self.assertTrue(result.wasSuccessful())

    def test_unexpected_success(self):

        class Foo(unittest2.TestCase):

            @unittest2.expectedFailure
            def test_die(self):
                pass

        events = []
        result = LoggingResult(events)
        test = Foo('test_die')
        test.run(result)
        self.assertEqual(events, ['startTest', 'addUnexpectedSuccess', 'stopTest'])
        self.assertFalse(result.failures)
        self.assertEqual(result.unexpectedSuccesses, [test])
        self.assertTrue(result.wasSuccessful())


class Test_Assertions(unittest2.TestCase):

    def test_AlmostEqual(self):
        self.assertAlmostEqual(1.00000001, 1.0)
        self.assertNotAlmostEqual(1.0000001, 1.0)
        self.assertRaises(self.failureException, self.assertAlmostEqual, 1.0000001, 1.0)
        self.assertRaises(self.failureException, self.assertNotAlmostEqual, 1.00000001, 1.0)
        self.assertAlmostEqual(1.1, 1.0, places=0)
        self.assertRaises(self.failureException, self.assertAlmostEqual, 1.1, 1.0, places=1)
        self.assertAlmostEqual(0, (0.1+0.1j), places=0)
        self.assertNotAlmostEqual(0, (0.1+0.1j), places=1)
        self.assertRaises(self.failureException, self.assertAlmostEqual, 0, (0.1+0.1j), places=1)
        self.assertRaises(self.failureException, self.assertNotAlmostEqual, 0, (0.1+0.1j), places=0)
        self.assertAlmostEqual(float('inf'), float('inf'))
        self.assertRaises(self.failureException, self.assertNotAlmostEqual, float('inf'), float('inf'))


class TestLongMessage(unittest2.TestCase):

    def setUp(self):

        class TestableTestFalse(unittest2.TestCase):
            longMessage = False
            failureException = self.failureException

            def testTest(self):
                pass

        class TestableTestTrue(unittest2.TestCase):
            longMessage = True
            failureException = self.failureException

            def testTest(self):
                pass

        self.testableTrue = TestableTestTrue('testTest')
        self.testableFalse = TestableTestFalse('testTest')

    def testDefault(self):
        self.assertTrue(unittest2.TestCase.longMessage)

    def test_formatMsg(self):
        self.assertEquals(self.testableFalse._formatMessage(None, 'foo'), 'foo')
        self.assertEquals(self.testableFalse._formatMessage('foo', 'bar'), 'foo')
        self.assertEquals(self.testableTrue._formatMessage(None, 'foo'), 'foo')
        self.assertEquals(self.testableTrue._formatMessage('foo', 'bar'), 'bar : foo')

    def assertMessages(self, methodName, args, errors):

        def getMethod(i):
            useTestableFalse = i < 2
            if useTestableFalse:
                test = self.testableFalse
            else:
                test = self.testableTrue
            return getattr(test, methodName)

        for i, expected_regexp in enumerate(errors):
            testMethod = getMethod(i)
            kwargs = {}
            withMsg = i % 2
            if withMsg:
                kwargs = {'msg': 'oops'}
            self.assertRaisesRegexp(self.failureException, expected_regexp, lambda : testMethod(*args, **kwargs))

    def testAssertTrue(self):
        self.assertMessages('assertTrue', (False,), ['^False is not True$',
         '^oops$',
         '^False is not True$',
         '^False is not True : oops$'])

    def testAssertFalse(self):
        self.assertMessages('assertFalse', (True,), ['^True is not False$',
         '^oops$',
         '^True is not False$',
         '^True is not False : oops$'])

    def testNotEqual(self):
        self.assertMessages('assertNotEqual', (1, 1), ['^1 == 1$',
         '^oops$',
         '^1 == 1$',
         '^1 == 1 : oops$'])

    def testAlmostEqual(self):
        self.assertMessages('assertAlmostEqual', (1, 2), ['^1 != 2 within 7 places$',
         '^oops$',
         '^1 != 2 within 7 places$',
         '^1 != 2 within 7 places : oops$'])

    def testNotAlmostEqual(self):
        self.assertMessages('assertNotAlmostEqual', (1, 1), ['^1 == 1 within 7 places$',
         '^oops$',
         '^1 == 1 within 7 places$',
         '^1 == 1 within 7 places : oops$'])

    def test_baseAssertEqual(self):
        self.assertMessages('_baseAssertEqual', (1, 2), ['^1 != 2$',
         '^oops$',
         '^1 != 2$',
         '^1 != 2 : oops$'])

    def testAssertSequenceEqual(self):
        self.assertMessages('assertSequenceEqual', ([], [None]), ['\\+ \\[None\\]$',
         '^oops$',
         '\\+ \\[None\\]$',
         '\\+ \\[None\\] : oops$'])

    def testAssertSetEqual(self):
        self.assertMessages('assertSetEqual', (set(), set([None])), ['None$',
         '^oops$',
         'None$',
         'None : oops$'])

    def testAssertIn(self):
        self.assertMessages('assertIn', (None, []), ['^None not found in \\[\\]$',
         '^oops$',
         '^None not found in \\[\\]$',
         '^None not found in \\[\\] : oops$'])

    def testAssertNotIn(self):
        self.assertMessages('assertNotIn', (None, [None]), ['^None unexpectedly found in \\[None\\]$',
         '^oops$',
         '^None unexpectedly found in \\[None\\]$',
         '^None unexpectedly found in \\[None\\] : oops$'])

    def testAssertDictEqual(self):
        self.assertMessages('assertDictEqual', ({}, {'key': 'value'}), ["\\+ \\{'key': 'value'\\}$",
         '^oops$',
         "\\+ \\{'key': 'value'\\}$",
         "\\+ \\{'key': 'value'\\} : oops$"])

    def testAssertDictContainsSubset(self):
        self.assertMessages('assertDictContainsSubset', ({'key': 'value'}, {}), ["^Missing: 'key'$",
         '^oops$',
         "^Missing: 'key'$",
         "^Missing: 'key' : oops$"])

    def testAssertSameElements(self):
        self.assertMessages('assertSameElements', ([], [None]), ['\\[None\\]$',
         '^oops$',
         '\\[None\\]$',
         '\\[None\\] : oops$'])

    def testAssertMultiLineEqual(self):
        self.assertMessages('assertMultiLineEqual', ('', 'foo'), ['\\+ foo$',
         '^oops$',
         '\\+ foo$',
         '\\+ foo : oops$'])

    def testAssertLess(self):
        self.assertMessages('assertLess', (2, 1), ['^2 not less than 1$',
         '^oops$',
         '^2 not less than 1$',
         '^2 not less than 1 : oops$'])

    def testAssertLessEqual(self):
        self.assertMessages('assertLessEqual', (2, 1), ['^2 not less than or equal to 1$',
         '^oops$',
         '^2 not less than or equal to 1$',
         '^2 not less than or equal to 1 : oops$'])

    def testAssertGreater(self):
        self.assertMessages('assertGreater', (1, 2), ['^1 not greater than 2$',
         '^oops$',
         '^1 not greater than 2$',
         '^1 not greater than 2 : oops$'])

    def testAssertGreaterEqual(self):
        self.assertMessages('assertGreaterEqual', (1, 2), ['^1 not greater than or equal to 2$',
         '^oops$',
         '^1 not greater than or equal to 2$',
         '^1 not greater than or equal to 2 : oops$'])

    def testAssertIsNone(self):
        self.assertMessages('assertIsNone', ('not None',), ["^'not None' is not None$",
         '^oops$',
         "^'not None' is not None$",
         "^'not None' is not None : oops$"])

    def testAssertIsNotNone(self):
        self.assertMessages('assertIsNotNone', (None,), ['^unexpectedly None$',
         '^oops$',
         '^unexpectedly None$',
         '^unexpectedly None : oops$'])

    def testAssertIs(self):
        self.assertMessages('assertIs', (None, 'foo'), ["^None is not 'foo'$",
         '^oops$',
         "^None is not 'foo'$",
         "^None is not 'foo' : oops$"])

    def testAssertIsNot(self):
        self.assertMessages('assertIsNot', (None, None), ['^unexpectedly identical: None$',
         '^oops$',
         '^unexpectedly identical: None$',
         '^unexpectedly identical: None : oops$'])


class TestCleanUp(unittest2.TestCase):

    def testCleanUp(self):

        class TestableTest(unittest2.TestCase):

            def testNothing(self):
                pass

        test = TestableTest('testNothing')
        self.assertEqual(test._cleanups, [])
        cleanups = []

        def cleanup1(*args, **kwargs):
            cleanups.append((1, args, kwargs))

        def cleanup2(*args, **kwargs):
            cleanups.append((2, args, kwargs))

        test.addCleanup(cleanup1, 1, 2, 3, four='hello', five='goodbye')
        test.addCleanup(cleanup2)
        self.assertEqual(test._cleanups, [(cleanup1, (1, 2, 3), dict(four='hello', five='goodbye')), (cleanup2, (), {})])
        result = test.doCleanups()
        self.assertTrue(result)
        self.assertEqual(cleanups, [(2, (), {}), (1, (1, 2, 3), dict(four='hello', five='goodbye'))])

    def testCleanUpWithErrors(self):

        class TestableTest(unittest2.TestCase):

            def testNothing(self):
                pass

        class MockResult(object):
            errors = []

            def addError(self, test, exc_info):
                self.errors.append((test, exc_info))

        result = MockResult()
        test = TestableTest('testNothing')
        test._resultForDoCleanups = result
        exc1 = Exception('foo')
        exc2 = Exception('bar')

        def cleanup1():
            raise exc1

        def cleanup2():
            raise exc2

        test.addCleanup(cleanup1)
        test.addCleanup(cleanup2)
        self.assertFalse(test.doCleanups())
        (test1, (Type1, instance1, _)), (test2, (Type2, instance2, _)) = reversed(MockResult.errors)
        self.assertEqual((test1, Type1, instance1), (test, Exception, exc1))
        self.assertEqual((test2, Type2, instance2), (test, Exception, exc2))

    def testCleanupInRun(self):
        blowUp = False
        ordering = []

        class TestableTest(unittest2.TestCase):

            def setUp(self):
                ordering.append('setUp')
                if blowUp:
                    raise Exception('foo')

            def testNothing(self):
                ordering.append('test')

            def tearDown(self):
                ordering.append('tearDown')

        test = TestableTest('testNothing')

        def cleanup1():
            ordering.append('cleanup1')

        def cleanup2():
            ordering.append('cleanup2')

        test.addCleanup(cleanup1)
        test.addCleanup(cleanup2)

        def success(some_test):
            self.assertEqual(some_test, test)
            ordering.append('success')

        result = unittest2.TestResult()
        result.addSuccess = success
        test.run(result)
        self.assertEqual(ordering, ['setUp',
         'test',
         'tearDown',
         'cleanup2',
         'cleanup1',
         'success'])
        blowUp = True
        ordering = []
        test = TestableTest('testNothing')
        test.addCleanup(cleanup1)
        test.run(result)
        self.assertEqual(ordering, ['setUp', 'cleanup1'])


class Test_TestProgram(unittest2.TestCase):

    def testNoExit(self):
        result = object()
        test = object()

        class FakeRunner(object):

            def run(self, test):
                self.test = test
                return result

        runner = FakeRunner()
        oldParseArgs = unittest2.TestProgram.parseArgs

        def restoreParseArgs():
            unittest2.TestProgram.parseArgs = oldParseArgs

        unittest2.TestProgram.parseArgs = lambda *args: None
        self.addCleanup(restoreParseArgs)

        def removeTest():
            del unittest2.TestProgram.test

        unittest2.TestProgram.test = test
        self.addCleanup(removeTest)
        program = unittest2.TestProgram(testRunner=runner, exit=False, verbosity=2)
        self.assertEqual(program.result, result)
        self.assertEqual(runner.test, test)
        self.assertEqual(program.verbosity, 2)

    class FooBar(unittest2.TestCase):

        def testPass(self):
            pass

        def testFail(self):
            pass

    class FooBarLoader(unittest2.TestLoader):

        def loadTestsFromModule(self, module):
            return self.suiteClass([self.loadTestsFromTestCase(Test_TestProgram.FooBar)])

    def test_NonExit(self):
        program = unittest2.main(exit=False, argv=['foobar'], testRunner=unittest2.TextTestRunner(stream=StringIO()), testLoader=self.FooBarLoader())
        self.assertTrue(hasattr(program, 'result'))

    def test_Exit(self):
        self.assertRaises(SystemExit, unittest2.main, argv=['foobar'], testRunner=unittest2.TextTestRunner(stream=StringIO()), exit=True, testLoader=self.FooBarLoader())

    def test_ExitAsDefault(self):
        self.assertRaises(SystemExit, unittest2.main, argv=['foobar'], testRunner=unittest2.TextTestRunner(stream=StringIO()), testLoader=self.FooBarLoader())


class Test_TextTestRunner(unittest2.TestCase):

    def test_works_with_result_without_startTestRun_stopTestRun(self):

        class OldTextResult(ResultWithNoStartTestRunStopTestRun):
            separator2 = ''

            def printErrors(self):
                pass

        class Runner(unittest2.TextTestRunner):

            def __init__(self):
                super(Runner, self).__init__(StringIO())

            def _makeResult(self):
                return OldTextResult()

        runner = Runner()
        runner.run(unittest2.TestSuite())

    def test_startTestRun_stopTestRun_called(self):

        class LoggingTextResult(LoggingResult):
            separator2 = ''

            def printErrors(self):
                pass

        class LoggingRunner(unittest2.TextTestRunner):

            def __init__(self, events):
                super(LoggingRunner, self).__init__(StringIO())
                self._events = events

            def _makeResult(self):
                return LoggingTextResult(self._events)

        events = []
        runner = LoggingRunner(events)
        runner.run(unittest2.TestSuite())
        expected = ['startTestRun', 'stopTestRun']
        self.assertEqual(events, expected)

    def test_pickle_unpickle(self):
        import StringIO
        stream = StringIO.StringIO('foo')
        runner = unittest2.TextTestRunner(stream)
        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            s = pickle.dumps(runner, protocol=protocol)
            obj = pickle.loads(s)
            self.assertEqual(obj.stream.getvalue(), stream.getvalue())

    def test_resultclass(self):

        def MockResultClass(*args):
            return args

        STREAM = object()
        DESCRIPTIONS = object()
        VERBOSITY = object()
        runner = unittest2.TextTestRunner(STREAM, DESCRIPTIONS, VERBOSITY, resultclass=MockResultClass)
        self.assertEqual(runner.resultclass, MockResultClass)
        expectedresult = (runner.stream, DESCRIPTIONS, VERBOSITY)
        self.assertEqual(runner._makeResult(), expectedresult)


class TestDiscovery(unittest2.TestCase):

    def test_get_name_from_path(self):
        loader = unittest2.TestLoader()
        loader._top_level_dir = '/foo'
        name = loader._get_name_from_path('/foo/bar/baz.py')
        self.assertEqual(name, 'bar.baz')
        if not __debug__:
            return
        self.assertRaises(AssertionError, loader._get_name_from_path, '/bar/baz.py')

    def test_find_tests(self):
        loader = unittest2.TestLoader()
        original_listdir = os.listdir

        def restore_listdir():
            os.listdir = original_listdir

        original_isfile = os.path.isfile

        def restore_isfile():
            os.path.isfile = original_isfile

        original_isdir = os.path.isdir

        def restore_isdir():
            os.path.isdir = original_isdir

        path_lists = [['test1.py',
          'test2.py',
          'not_a_test.py',
          'test_dir',
          'test.foo',
          'test-not-a-module.py',
          'another_dir'], ['test3.py', 'test4.py']]
        os.listdir = lambda path: path_lists.pop(0)
        self.addCleanup(restore_listdir)

        def isdir(path):
            return path.endswith('dir')

        os.path.isdir = isdir
        self.addCleanup(restore_isdir)

        def isfile(path):
            return not path.endswith('dir') and 'another_dir' not in path

        os.path.isfile = isfile
        self.addCleanup(restore_isfile)
        loader._get_module_from_name = lambda path: path + ' module'
        loader.loadTestsFromModule = lambda module: module + ' tests'
        loader._top_level_dir = '/foo'
        suite = list(loader._find_tests('/foo', 'test*.py'))
        expected = [ name + ' module tests' for name in ('test1', 'test2') ]
        expected.extend([ 'test_dir.%s' % name + ' module tests' for name in ('test3', 'test4') ])
        self.assertEqual(suite, expected)

    def test_find_tests_with_package(self):
        loader = unittest2.TestLoader()
        original_listdir = os.listdir

        def restore_listdir():
            os.listdir = original_listdir

        original_isfile = os.path.isfile

        def restore_isfile():
            os.path.isfile = original_isfile

        original_isdir = os.path.isdir

        def restore_isdir():
            os.path.isdir = original_isdir

        directories = ['a_directory', 'test_directory', 'test_directory2']
        path_lists = [directories,
         [],
         [],
         []]
        os.listdir = lambda path: path_lists.pop(0)
        self.addCleanup(restore_listdir)
        os.path.isdir = lambda path: True
        self.addCleanup(restore_isdir)
        os.path.isfile = lambda path: os.path.basename(path) not in directories
        self.addCleanup(restore_isfile)

        class Module(object):
            paths = []
            load_tests_args = []

            def __init__(self, path):
                self.path = path
                self.paths.append(path)
                if os.path.basename(path) == 'test_directory':

                    def load_tests(loader, tests, pattern):
                        self.load_tests_args.append((loader, tests, pattern))
                        return 'load_tests'

                    self.load_tests = load_tests

            def __eq__(self, other):
                return self.path == other.path

            __hash__ = None

        loader._get_module_from_name = lambda name: Module(name)

        def loadTestsFromModule(module, use_load_tests):
            if use_load_tests:
                raise self.failureException('use_load_tests should be False for packages')
            return module.path + ' module tests'

        loader.loadTestsFromModule = loadTestsFromModule
        loader._top_level_dir = '/foo'
        suite = list(loader._find_tests('/foo', 'test*'))
        self.assertEqual(suite, ['load_tests', 'test_directory2' + ' module tests'])
        self.assertEqual(Module.paths, ['test_directory', 'test_directory2'])
        self.assertEqual(Module.load_tests_args, [(loader, 'test_directory' + ' module tests', 'test*')])

    def test_discover(self):
        loader = unittest2.TestLoader()
        original_isfile = os.path.isfile

        def restore_isfile():
            os.path.isfile = original_isfile

        os.path.isfile = lambda path: False
        self.addCleanup(restore_isfile)
        orig_sys_path = sys.path[:]

        def restore_path():
            sys.path[:] = orig_sys_path

        self.addCleanup(restore_path)
        full_path = os.path.abspath(os.path.normpath('/foo'))
        self.assertRaises(ImportError, loader.discover, '/foo/bar', top_level_dir='/foo')
        self.assertEqual(loader._top_level_dir, full_path)
        self.assertIn(full_path, sys.path)
        os.path.isfile = lambda path: True
        _find_tests_args = []

        def _find_tests(start_dir, pattern):
            _find_tests_args.append((start_dir, pattern))
            return ['tests']

        loader._find_tests = _find_tests
        loader.suiteClass = str
        suite = loader.discover('/foo/bar/baz', 'pattern', '/foo/bar')
        top_level_dir = os.path.abspath(os.path.normpath('/foo/bar'))
        start_dir = os.path.abspath(os.path.normpath('/foo/bar/baz'))
        self.assertEqual(suite, "['tests']")
        self.assertEqual(loader._top_level_dir, top_level_dir)
        self.assertEqual(_find_tests_args, [(start_dir, 'pattern')])
        self.assertIn(top_level_dir, sys.path)

    def test_discover_with_modules_that_fail_to_import(self):
        loader = unittest2.TestLoader()
        listdir = os.listdir
        os.listdir = lambda _: ['test_this_does_not_exist.py']
        isfile = os.path.isfile
        os.path.isfile = lambda _: True
        orig_sys_path = sys.path[:]

        def restore():
            os.path.isfile = isfile
            os.listdir = listdir
            sys.path[:] = orig_sys_path

        self.addCleanup(restore)
        suite = loader.discover('.')
        self.assertIn(os.getcwd(), sys.path)
        self.assertEqual(suite.countTestCases(), 1)
        test = list(list(suite)[0])[0]
        self.assertRaises(ImportError, lambda : test.test_this_does_not_exist())

    def test_command_line_handling_parseArgs(self):
        program = object.__new__(unittest2.TestProgram)
        args = []

        def do_discovery(argv):
            args.extend(argv)

        program._do_discovery = do_discovery
        program.parseArgs(['something', 'discover'])
        self.assertEqual(args, [])
        program.parseArgs(['something',
         'discover',
         'foo',
         'bar'])
        self.assertEqual(args, ['foo', 'bar'])

    def test_command_line_handling_do_discovery_too_many_arguments(self):

        class Stop(Exception):
            pass

        def usageExit():
            raise Stop

        program = object.__new__(unittest2.TestProgram)
        program.usageExit = usageExit
        self.assertRaises(Stop, lambda : program._do_discovery(['one',
         'two',
         'three',
         'four']))

    def test_command_line_handling_do_discovery_calls_loader(self):
        program = object.__new__(unittest2.TestProgram)

        class Loader(object):
            args = []

            def discover(self, start_dir, pattern, top_level_dir):
                self.args.append((start_dir, pattern, top_level_dir))
                return 'tests'

        program._do_discovery(['-v'], Loader=Loader)
        self.assertEqual(program.verbosity, 2)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('.', 'test*.py', None)])
        Loader.args = []
        program = object.__new__(unittest2.TestProgram)
        program._do_discovery(['--verbose'], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('.', 'test*.py', None)])
        Loader.args = []
        program = object.__new__(unittest2.TestProgram)
        program._do_discovery([], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('.', 'test*.py', None)])
        Loader.args = []
        program = object.__new__(unittest2.TestProgram)
        program._do_discovery(['fish'], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('fish', 'test*.py', None)])
        Loader.args = []
        program = object.__new__(unittest2.TestProgram)
        program._do_discovery(['fish', 'eggs'], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('fish', 'eggs', None)])
        Loader.args = []
        program = object.__new__(unittest2.TestProgram)
        program._do_discovery(['fish', 'eggs', 'ham'], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('fish', 'eggs', 'ham')])
        Loader.args = []
        program = object.__new__(unittest2.TestProgram)
        program._do_discovery(['-s', 'fish'], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('fish', 'test*.py', None)])
        Loader.args = []
        program = object.__new__(unittest2.TestProgram)
        program._do_discovery(['-t', 'fish'], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('.', 'test*.py', 'fish')])
        Loader.args = []
        program = object.__new__(unittest2.TestProgram)
        program._do_discovery(['-p', 'fish'], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('.', 'fish', None)])
        Loader.args = []
        program = object.__new__(unittest2.TestProgram)
        program._do_discovery(['-p',
         'eggs',
         '-s',
         'fish',
         '-v'], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('fish', 'eggs', None)])
        self.assertEqual(program.verbosity, 2)


if __name__ == '__main__':
    unittest2.main()