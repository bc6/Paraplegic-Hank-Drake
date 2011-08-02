import uthread

def CallInNewThread(context = None, returnValue = None):

    def ContextThread(f):
        if context is not None:
            if context.startswith('^'):
                fullContext = context
            else:
                fullContext = '^%s::%s' % (context, f.__name__)
        else:
            fullContext = f.__name__

        def deco(*args, **kw):
            uthread.worker(fullContext, f, *args, **kw)
            return returnValue


        return deco


    return ContextThread



def Memoized(fn):
    memo = {}

    def deco(*args):
        if args not in memo:
            memo[args] = fn(*args)
        return memo[args]


    return deco


exports = {'funcDeco.CallInNewThread': CallInNewThread,
 'util.Memoized': Memoized}
import unittest
import mock

class TestCallInNewThread(unittest.TestCase):
    THREAD_CONTEXT = 'testContext'

    def setUp(self):
        mock.SetUp(self, globals())

        def mockWorker(funcContext, func, *args, **kwargs):
            self.workerCalled = True
            self.workerContext = funcContext


        self.workerCalled = False
        uthread.worker = mockWorker
        self.value = 'none'
        self.SetUpThreadedFunctions()



    def tearDown(self):
        mock.TearDown(self)



    def SetUpThreadedFunctions(self):

        def NonThreaded():
            self.value = 'non'



        def UglyThreaded():
            self.value = 'ugly'


        UglyThreaded = CallInNewThread()(UglyThreaded)

        @CallInNewThread()
        def NiceThreaded():
            self.value = 'nice'



        @CallInNewThread(self.THREAD_CONTEXT)
        def ContextThread():
            self.value = 'contexted'



        @CallInNewThread()
        def NonContextThread():
            self.value = 'non-contexted'


        self.NonThreaded = NonThreaded
        self.UglyThreaded = UglyThreaded
        self.NiceThreaded = NiceThreaded
        self.ContextThread = ContextThread
        self.NonContextThread = NonContextThread



    def testNonThreaded(self):
        self.NonThreaded()
        self.assertTrue(self.value == 'non', 'NonThreaded should immediately change the value')
        self.assertTrue(not self.workerCalled, 'uthread.worker was called, a thread was queued that should not have been.')



    def testUglyThreaded(self):
        self.UglyThreaded()
        self.assertTrue(self.value == 'none', 'UglyThreaded should not immediately change the value')
        self.assertTrue(self.workerCalled, 'uthread.worker was not called, and thus the thread is not queued.')



    def testNiceThreaded(self):
        self.NiceThreaded()
        self.assertTrue(self.value == 'none', 'NiceThreaded should not immediately change the value')
        self.assertTrue(self.workerCalled, 'uthread.worker was not called, and thus the thread is not queued.')



    def testContextGeneration(self):
        self.ContextThread()
        self.assertTrue(self.value == 'none', 'PRECONDITION: ThreadContext should not immediately change the value')
        self.assertTrue(self.workerCalled, 'PRECONDITION: uthread.worker was not called, and thus the thread is not queued.')
        expectedContext = '^%s::ContextThread' % self.THREAD_CONTEXT
        self.assertTrue(self.workerContext == expectedContext, 'The context thread was not assembled correctly.\nExpected:\n%s\nActual:\n%s' % (expectedContext, self.workerContext))



    def testContextGeneration_Default(self):
        self.NonContextThread()
        self.assertTrue(self.value == 'none', 'PRECONDITION: ThreadContext should not immediately change the value')
        self.assertTrue(self.workerCalled, 'PRECONDITION: uthread.worker was not called, and thus the thread is not queued.')
        expectedContext = 'NonContextThread'
        self.assertTrue(self.workerContext == expectedContext, 'The default context thread is incorrect.\nExpected:\n%s\nActual:\n%s' % (expectedContext, self.workerContext))




