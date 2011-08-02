import sys
import stackless
import contextlib
import weakref
from main import mainloop, event_queue
import threading
if hasattr(threading, 'real_threading'):
    _RealThread = threading.realthreading.Thread
else:
    _RealThread = threading.Thread
del threading

@contextlib.contextmanager
def atomic():
    c = stackless.getcurrent()
    old = c.set_atomic(True)
    try:
        yield None

    finally:
        c.set_atomic(old)




@contextlib.contextmanager
def block_trap(trap = True):
    c = stackless.getcurrent()
    old = c.block_trap
    c.block_trap = trap
    try:
        yield None

    finally:
        c.block_trap = old




@contextlib.contextmanager
def ignore_nesting(flag = True):
    c = stackless.getcurrent()
    old = c.set_ignore_nesting(flag)
    try:
        yield None

    finally:
        c.set_ignore_nesting(old)




class local(object):

    def __init__(self):
        object.__getattribute__(self, '__dict__')['_tasklets'] = weakref.WeakKeyDictionary()



    def get_dict(self):
        d = object.__getattribute__(self, '__dict__')['_tasklets']
        try:
            a = d[stackless.getcurrent()]
        except KeyError:
            a = {}
            d[stackless.getcurrent()] = a
        return a



    def __getattribute__(self, name):
        a = object.__getattribute__(self, 'get_dict')()
        if name == '__dict__':
            return a
        else:
            if name in a:
                return a[name]
            return object.__getattribute__(self, name)



    def __setattr__(self, name, value):
        a = object.__getattribute__(self, 'get_dict')()
        a[name] = value



    def __delattr__(self, name):
        a = object.__getattribute__(self, 'get_dict')()
        try:
            del a[name]
        except KeyError:
            raise AttributeError, name




def call_on_thread(target, args = (), kwargs = {}):
    chan = stackless.channel()

    def Helper():
        try:
            try:
                r = target(*args, **kwargs)
                chan.send(r)
            except:
                (e, v,) = sys.exc_info()[:2]
                chan.send_exception(e, v)

        finally:
            mainloop.interrupt_wait()



    thread = _RealThread(target=Helper)
    thread.start()
    return chan.receive()



class WaitTimeoutError(RuntimeError):
    pass

def channel_wait(chan, timeout):
    if timeout is None:
        chan.receive()
        return 
    waiting_tasklet = stackless.getcurrent()

    def break_wait():
        with atomic():
            if waiting_tasklet and waiting_tasklet.blocked:
                waiting_tasklet.raise_exception(WaitTimeoutError)


    with atomic():
        try:
            event_queue.push_after(break_wait, timeout)
            return chan.receive()

        finally:
            waiting_tasklet = None




class ValueEvent(stackless.channel):

    def __new__(cls, timeout = None, timeoutException = None, timeoutExceptionValue = None):
        obj = super(stackless.channel, cls).__new__(cls)
        obj.timeout = timeout
        if timeout > 0.0:
            if timeoutException is None:
                timeoutException = WaitTimeoutError
                timeoutExceptionValue = 'Event timed out'

            def break_wait():
                if not obj.closed:
                    obj.abort(timeoutException, timeoutExceptionValue)


            event_queue.push_after(break_wait, timeout)
        return obj



    def __repr__(self):
        return '<ValueEvent object at 0x%x, balance=%s, queue=%s, timeout=%s>' % (id(self),
         self.balance,
         self.queue,
         self.timeout)



    def set(self, value = None):
        if self.closed:
            raise RuntimeError('ValueEvent object already signaled or aborted.')
        while self.queue:
            self.send(value)

        self.close()
        (self.exception, self.value,) = (RuntimeError, ('Already resumed',))



    def abort(self, exception = None, *value):
        if self.closed:
            raise RuntimeError('ValueEvent object already signaled or aborted.')
        if exception is None:
            (exception, value,) = (self.exception, self.value)
        else:
            (self.exception, self.value,) = (exception, value)
        while self.queue:
            self.send_exception(exception, *value)

        self.close()



    def wait(self):
        if self.closed:
            raise self.exception(*self.value)
        return self.receive()




