#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\stdlib\stacklesslib\replacements\threading.py
from __future__ import absolute_import
import traceback
import weakref
import stackless
from stacklesslib.locks import Lock, RLock, Semaphore, Condition, BoundedSemaphore, Event
from stacklesslib.main import set_channel_pref
from stacklesslib.util import local
import stacklesslib.replacements.thread as thread
_start_new_thread = thread.start_new_thread
_allocate_lock = thread.allocate_lock
_get_ident = thread.get_ident
_thread_count = thread._thread_count
ThreadError = thread.error
stack_size = thread.stack_size
del thread

def _shutdown():
    pass


_active = {}
_limbo = {}

def TaskletDump():
    print 'taskletdump'
    print len(_active)
    for k in _active.values():
        print k
        try:
            traceback.print_stack(k.frame)
        except:
            pass


def enumerate():
    return _active.values()


def activeCount():
    return len(_active)


class Thread(object):
    nTasklet = 0

    def __init__(self, group = None, target = None, name = None, args = (), kwargs = {}):
        self.target = target
        if name is None:
            self.name = 'Tasklet-%d' % Thread.nTasklet
            Thread.nTasklet += 1
        else:
            self.name = name
        self.args, self.kwargs = args, kwargs
        self._join = Event()
        set_channel_pref(self._join)
        self._started = False
        self._alive = False
        self.ident = None
        self._daemon = self._set_daemon()

    def _set_daemon(self):
        self._daemon = current_thread().daemon

    def __repr__(self):
        status = 'initial'
        if self._started:
            status = 'started'
        if self._daemon:
            status += ' daemon'
        if self.ident is not None:
            status += ' %s' % self.ident
        return '<%s(%s, %s)>' % (self.__class__.__name__, self.name, status)

    def start(self):
        if self._started:
            raise RuntimeError, "Can't start a thread more than once."
        tid = _start_new_thread(self._taskfunc, (self,))
        self.ident = tid
        _active[self.ident] = self
        self._alive = True
        self._started = True

    @staticmethod
    def _taskfunc(self):
        try:
            self.run()
        except Exception:
            traceback.print_exc()
        finally:
            self._alive = False
            del _active[self.ident]
            self._join.set()

    def run(self):
        try:
            if self.target:
                self.target(*self.args, **self.kwargs)
        finally:
            self.target = self.args = self.kwargs = None

    def join(self, timeout = None):
        if not self._started:
            raise RuntimeError, "Can't wait on a not-started thread."
        if currentThread() is self:
            raise RuntimeError, "Can't wait on the same thread."
        self._join.wait(timeout)

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def get_daemon(self):
        return self._daemon

    def set_daemon(self, val):
        if self._started:
            raise RuntimeError, "Can't change daemon propery after starting"
        self._daemon = val

    daemon = property(get_daemon, set_daemon)

    def isDaemon(self):
        return self.daemon

    def setDaemon(self, daemon):
        self.daemon = daemon

    def is_alive(self):
        return self._alive

    isAlive = is_alive


def get_ident():
    return id(stackless.getcurrent())


_get_ident = get_ident

def currentThread():
    ident = get_ident()
    try:
        return _active[ident]
    except KeyError:
        pass

    return _DummyThread()


current_thread = currentThread

class _MainThread(Thread):

    def __init__(self):
        Thread.__init__(self, name='MainThread')
        self._started = True
        self._alive = True
        self.ident = stackless.getcurrent()
        _active[self.ident] = self

    def _set_daemon(self):
        return False


class _DummyThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.ident = id(stackless.getcurrent())
        _active[self.ident] = self
        del self._join

    def _set_daemon(self):
        return False

    def join(self, timeout = None):
        raise RuntimeError, 'cannot join a dummy thread'


class Timer(Thread):

    def __init__(self, interval, function, args = (), kwargs = {}):
        self._canceled = False
        self._interval = interval
        self._function = function
        Thread.__init__(self, target=self._function, args=args, kwargs=kwargs)

    def cancel(self):
        self._canceled = True

    def _function(self, *args, **kwargs):
        main.sleep(interval)
        if not self._canceled:
            self.function(*args, **kwargs)


_MainThread()