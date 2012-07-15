#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\helloworld\callbacks_unittest.py
import unittest
import helloworld
import blue

class CallbacksTestCase(unittest.TestCase):

    def testBasicCallback(self):
        a = helloworld.HelloPythonDecoratorCallbackExample()
        l = [1]

        def SimpleCallback():
            l.append(2)

        a.callback = SimpleCallback
        a.CallManual()
        self.assertEquals(len(l), 2, 'Callback has not modified the list')

    def testBlockTrappedCallback(self):
        a = helloworld.HelloPythonDecoratorCallbackExample()

        def YieldingCallback():
            blue.pyos.synchro.Yield()

        a.callback = YieldingCallback
        self.assertRaises(RuntimeError, a.CallManual, 'Attempting to yield in the callback did not raise an Exception')

    def testReraisingError(self):
        a = helloworld.HelloPythonDecoratorCallbackExample()

        def RaisingCallback():
            raise Exception('An Error')

        a.callback = RaisingCallback
        self.assertRaises(Exception, a.CallManual, 'Exception was not reraised')

    def testCallableClassCallback(self):
        a = helloworld.HelloPythonDecoratorCallbackExample()

        class MyCallback(object):

            def __init__(self):
                self.c = 1

            def __call__(self):
                self.c += 1

        cb = MyCallback()
        a.callback = cb
        a.CallManual()
        self.assertEquals(cb.c, 2, 'Callback has not modified the object')

    @unittest.expectedFailure
    def testExceptionLeakingBehaviour(self):
        a = helloworld.HelloPythonDecoratorCallbackExample()
        self.assertRaises(SystemError, a.TestRaiseWithoutException, 'Raising an exception without setting an error should cause a SystemError')
        a.TestExceptionWithoutRaise()
        self.assertRaises(SystemError, a.TestRaiseWithoutException, 'Attempting to yield in the callback did not raise an Exception')

    def testExceptionContainment(self):
        a = helloworld.HelloPythonDecoratorCallbackExample()
        a.TestExceptionWithoutRaise()

        class CustomException(Exception):
            pass

        def RaisingCallback():
            raise CustomException('An Error')

        a.callback = RaisingCallback
        self.assertRaises(CustomException, a.CallManual, 'Exception was not raised correctly')

    def testExceptionContainment(self):
        a = helloworld.HelloPythonDecoratorCallbackExample()
        a.TestExceptionWithoutRaise()

        class CustomException(Exception):
            pass

        def RaisingCallback():
            raise CustomException('An Error')

        a.callback = RaisingCallback
        a.Call()
        self.assertRaises(SystemError, a.TestRaiseWithoutException, 'Raising an exception without setting an error should cause a SystemError')

    def testWrappedBlueErrorBehaviour(self):
        a = helloworld.HelloPythonDecoratorCallbackExample()
        a.TestAutoBlueError()
        a.TestRaiseWithoutException()

    @unittest.expectedFailure
    def testWrappedPythonExceptionBehaviour(self):
        a = helloworld.HelloPythonDecoratorCallbackExample()
        a.TestAutoPythonException()
        a.TestRaiseWithoutException()