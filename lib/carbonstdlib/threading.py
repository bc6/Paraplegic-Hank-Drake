import sys as _sys
try:
    import thread
except ImportError:
    del _sys.modules[__name__]
    raise 
import warnings
from time import time as _time, sleep as _sleep
from traceback import format_exc as _format_exc
from collections import deque
__all__ = ['activeCount',
 'active_count',
 'Condition',
 'currentThread',
 'current_thread',
 'enumerate',
 'Event',
 'Lock',
 'RLock',
 'Semaphore',
 'BoundedSemaphore',
 'Thread',
 'Timer',
 'setprofile',
 'settrace',
 'local',
 'stack_size']
_start_new_thread = thread.start_new_thread
_allocate_lock = thread.allocate_lock
_get_ident = thread.get_ident
ThreadError = thread.error
del thread
warnings.filterwarnings('ignore', category=DeprecationWarning, module='threading', message='sys.exc_clear')
_VERBOSE = False

class _Verbose(object):

    def __init__(self, verbose = None):
        pass



    def _note(self, *args):
        pass



_profile_hook = None
_trace_hook = None

def setprofile(func):
    global _profile_hook
    _profile_hook = func



def settrace(func):
    global _trace_hook
    _trace_hook = func


Lock = _allocate_lock

def RLock(*args, **kwargs):
    return _RLock(*args, **kwargs)



class _RLock(_Verbose):

    def __init__(self, verbose = None):
        _Verbose.__init__(self, verbose)
        self._RLock__block = _allocate_lock()
        self._RLock__owner = None
        self._RLock__count = 0



    def __repr__(self):
        owner = self._RLock__owner
        try:
            owner = _active[owner].name
        except KeyError:
            pass
        return '<%s owner=%r count=%d>' % (self.__class__.__name__, owner, self._RLock__count)



    def acquire(self, blocking = 1):
        me = _get_ident()
        if self._RLock__owner == me:
            self._RLock__count = self._RLock__count + 1
            return 1
        rc = self._RLock__block.acquire(blocking)
        if rc:
            self._RLock__owner = me
            self._RLock__count = 1
        return rc


    __enter__ = acquire

    def release(self):
        if self._RLock__owner != _get_ident():
            raise RuntimeError('cannot release un-acquired lock')
        self._RLock__count = count = self._RLock__count - 1
        if not count:
            self._RLock__owner = None
            self._RLock__block.release()



    def __exit__(self, t, v, tb):
        self.release()



    def _acquire_restore(self, count_owner):
        (count, owner,) = count_owner
        self._RLock__block.acquire()
        self._RLock__count = count
        self._RLock__owner = owner



    def _release_save(self):
        count = self._RLock__count
        self._RLock__count = 0
        owner = self._RLock__owner
        self._RLock__owner = None
        self._RLock__block.release()
        return (count, owner)



    def _is_owned(self):
        return self._RLock__owner == _get_ident()




def Condition(*args, **kwargs):
    return _Condition(*args, **kwargs)



class _Condition(_Verbose):

    def __init__(self, lock = None, verbose = None):
        _Verbose.__init__(self, verbose)
        if lock is None:
            lock = RLock()
        self._Condition__lock = lock
        self.acquire = lock.acquire
        self.release = lock.release
        try:
            self._release_save = lock._release_save
        except AttributeError:
            pass
        try:
            self._acquire_restore = lock._acquire_restore
        except AttributeError:
            pass
        try:
            self._is_owned = lock._is_owned
        except AttributeError:
            pass
        self._Condition__waiters = []



    def __enter__(self):
        return self._Condition__lock.__enter__()



    def __exit__(self, *args):
        return self._Condition__lock.__exit__(*args)



    def __repr__(self):
        return '<Condition(%s, %d)>' % (self._Condition__lock, len(self._Condition__waiters))



    def _release_save(self):
        self._Condition__lock.release()



    def _acquire_restore(self, x):
        self._Condition__lock.acquire()



    def _is_owned(self):
        if self._Condition__lock.acquire(0):
            self._Condition__lock.release()
            return False
        else:
            return True



    def wait(self, timeout = None):
        if not self._is_owned():
            raise RuntimeError('cannot wait on un-acquired lock')
        waiter = _allocate_lock()
        waiter.acquire()
        self._Condition__waiters.append(waiter)
        saved_state = self._release_save()
        try:
            if timeout is None:
                waiter.acquire()
            else:
                endtime = _time() + timeout
                delay = 0.0005
                while True:
                    gotit = waiter.acquire(0)
                    if gotit:
                        break
                    remaining = endtime - _time()
                    if remaining <= 0:
                        break
                    delay = min(delay * 2, remaining, 0.05)
                    _sleep(delay)

                if not gotit:
                    try:
                        self._Condition__waiters.remove(waiter)
                    except ValueError:
                        pass

        finally:
            self._acquire_restore(saved_state)




    def notify(self, n = 1):
        if not self._is_owned():
            raise RuntimeError('cannot notify on un-acquired lock')
        _Condition__waiters = self._Condition__waiters
        waiters = _Condition__waiters[:n]
        if not waiters:
            return 
        self._note('%s.notify(): notifying %d waiter%s', self, n, n != 1 and 's' or '')
        for waiter in waiters:
            waiter.release()
            try:
                _Condition__waiters.remove(waiter)
            except ValueError:
                pass




    def notifyAll(self):
        self.notify(len(self._Condition__waiters))


    notify_all = notifyAll


def Semaphore(*args, **kwargs):
    return _Semaphore(*args, **kwargs)



class _Semaphore(_Verbose):

    def __init__(self, value = 1, verbose = None):
        if value < 0:
            raise ValueError('semaphore initial value must be >= 0')
        _Verbose.__init__(self, verbose)
        self._Semaphore__cond = Condition(Lock())
        self._Semaphore__value = value



    def acquire(self, blocking = 1):
        rc = False
        self._Semaphore__cond.acquire()
        while self._Semaphore__value == 0:
            if not blocking:
                break
            self._Semaphore__cond.wait()
        else:
            self._Semaphore__value = self._Semaphore__value - 1
            rc = True

        self._Semaphore__cond.release()
        return rc


    __enter__ = acquire

    def release(self):
        self._Semaphore__cond.acquire()
        self._Semaphore__value = self._Semaphore__value + 1
        self._Semaphore__cond.notify()
        self._Semaphore__cond.release()



    def __exit__(self, t, v, tb):
        self.release()




def BoundedSemaphore(*args, **kwargs):
    return _BoundedSemaphore(*args, **kwargs)



class _BoundedSemaphore(_Semaphore):

    def __init__(self, value = 1, verbose = None):
        _Semaphore.__init__(self, value, verbose)
        self._initial_value = value



    def release(self):
        if self._Semaphore__value >= self._initial_value:
            raise ValueError, 'Semaphore released too many times'
        return _Semaphore.release(self)




def Event(*args, **kwargs):
    return _Event(*args, **kwargs)



class _Event(_Verbose):

    def __init__(self, verbose = None):
        _Verbose.__init__(self, verbose)
        self._Event__cond = Condition(Lock())
        self._Event__flag = False



    def isSet(self):
        return self._Event__flag


    is_set = isSet

    def set(self):
        self._Event__cond.acquire()
        try:
            self._Event__flag = True
            self._Event__cond.notify_all()

        finally:
            self._Event__cond.release()




    def clear(self):
        self._Event__cond.acquire()
        try:
            self._Event__flag = False

        finally:
            self._Event__cond.release()




    def wait(self, timeout = None):
        self._Event__cond.acquire()
        try:
            if not self._Event__flag:
                self._Event__cond.wait(timeout)
            return self._Event__flag

        finally:
            self._Event__cond.release()




_counter = 0

def _newname(template = 'Thread-%d'):
    global _counter
    _counter = _counter + 1
    return template % _counter


_active_limbo_lock = _allocate_lock()
_active = {}
_limbo = {}

class Thread(_Verbose):
    _Thread__initialized = False
    _Thread__exc_info = _sys.exc_info
    _Thread__exc_clear = _sys.exc_clear

    def __init__(self, group = None, target = None, name = None, args = (), kwargs = None, verbose = None):
        _Verbose.__init__(self, verbose)
        if kwargs is None:
            kwargs = {}
        self._Thread__target = target
        self._Thread__name = str(name or _newname())
        self._Thread__args = args
        self._Thread__kwargs = kwargs
        self._Thread__daemonic = self._set_daemon()
        self._Thread__ident = None
        self._Thread__started = Event()
        self._Thread__stopped = False
        self._Thread__block = Condition(Lock())
        self._Thread__initialized = True
        self._Thread__stderr = _sys.stderr



    def _set_daemon(self):
        return current_thread().daemon



    def __repr__(self):
        status = 'initial'
        if self._Thread__started.is_set():
            status = 'started'
        if self._Thread__stopped:
            status = 'stopped'
        if self._Thread__daemonic:
            status += ' daemon'
        if self._Thread__ident is not None:
            status += ' %s' % self._Thread__ident
        return '<%s(%s, %s)>' % (self.__class__.__name__, self._Thread__name, status)



    def start(self):
        global _active_limbo_lock
        if not self._Thread__initialized:
            raise RuntimeError('thread.__init__() not called')
        if self._Thread__started.is_set():
            raise RuntimeError('threads can only be started once')
        with _active_limbo_lock:
            _limbo[self] = self
        try:
            _start_new_thread(self._Thread__bootstrap, ())
        except Exception:
            with _active_limbo_lock:
                del _limbo[self]
            raise 
        self._Thread__started.wait()



    def run(self):
        try:
            if self._Thread__target:
                self._Thread__target(*self._Thread__args, **self._Thread__kwargs)

        finally:
            del self._Thread__target
            del self._Thread__args
            del self._Thread__kwargs




    def __bootstrap(self):
        try:
            self._Thread__bootstrap_inner()
        except:
            if self._Thread__daemonic and _sys is None:
                return 
            raise 



    def _set_ident(self):
        self._Thread__ident = _get_ident()



    def __bootstrap_inner(self):
        try:
            self._set_ident()
            self._Thread__started.set()
            with _active_limbo_lock:
                _active[self._Thread__ident] = self
                del _limbo[self]
            if _trace_hook:
                self._note('%s.__bootstrap(): registering trace hook', self)
                _sys.settrace(_trace_hook)
            if _profile_hook:
                self._note('%s.__bootstrap(): registering profile hook', self)
                _sys.setprofile(_profile_hook)
            try:
                try:
                    self.run()
                except SystemExit:
                    pass
                except:
                    if _sys:
                        _sys.stderr.write('Exception in thread %s:\n%s\n' % (self.name, _format_exc()))
                    else:
                        (exc_type, exc_value, exc_tb,) = self._Thread__exc_info()
                        try:
                            print >> self._Thread__stderr, 'Exception in thread ' + self.name + ' (most likely raised during interpreter shutdown):'
                            print >> self._Thread__stderr, 'Traceback (most recent call last):'
                            while exc_tb:
                                print >> self._Thread__stderr, '  File "%s", line %s, in %s' % (exc_tb.tb_frame.f_code.co_filename, exc_tb.tb_lineno, exc_tb.tb_frame.f_code.co_name)
                                exc_tb = exc_tb.tb_next

                            print >> self._Thread__stderr, '%s: %s' % (exc_type, exc_value)

                        finally:
                            del exc_type
                            del exc_value
                            del exc_tb


            finally:
                self._Thread__exc_clear()


        finally:
            with _active_limbo_lock:
                self._Thread__stop()
                try:
                    del _active[_get_ident()]
                except:
                    pass




    def __stop(self):
        self._Thread__block.acquire()
        self._Thread__stopped = True
        self._Thread__block.notify_all()
        self._Thread__block.release()



    def __delete(self):
        try:
            with _active_limbo_lock:
                del _active[_get_ident()]
        except KeyError:
            if 'dummy_threading' not in _sys.modules:
                raise 



    def join(self, timeout = None):
        if not self._Thread__initialized:
            raise RuntimeError('Thread.__init__() not called')
        if not self._Thread__started.is_set():
            raise RuntimeError('cannot join thread before it is started')
        if self is current_thread():
            raise RuntimeError('cannot join current thread')
        self._Thread__block.acquire()
        try:
            if timeout is None:
                while not self._Thread__stopped:
                    self._Thread__block.wait()

            else:
                deadline = _time() + timeout
                while not self._Thread__stopped:
                    delay = deadline - _time()
                    if delay <= 0:
                        break
                    self._Thread__block.wait(delay)


        finally:
            self._Thread__block.release()




    @property
    def name(self):
        return self._Thread__name



    @name.setter
    def name(self, name):
        self._Thread__name = str(name)



    @property
    def ident(self):
        return self._Thread__ident



    def isAlive(self):
        return self._Thread__started.is_set() and not self._Thread__stopped


    is_alive = isAlive

    @property
    def daemon(self):
        return self._Thread__daemonic



    @daemon.setter
    def daemon(self, daemonic):
        if not self._Thread__initialized:
            raise RuntimeError('Thread.__init__() not called')
        if self._Thread__started.is_set():
            raise RuntimeError('cannot set daemon status of active thread')
        self._Thread__daemonic = daemonic



    def isDaemon(self):
        return self.daemon



    def setDaemon(self, daemonic):
        self.daemon = daemonic



    def getName(self):
        return self.name



    def setName(self, name):
        self.name = name




def Timer(*args, **kwargs):
    return _Timer(*args, **kwargs)



class _Timer(Thread):

    def __init__(self, interval, function, args = [], kwargs = {}):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()



    def cancel(self):
        self.finished.set()



    def run(self):
        self.finished.wait(self.interval)
        if not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
        self.finished.set()




class _MainThread(Thread):

    def __init__(self):
        Thread.__init__(self, name='MainThread')
        self._Thread__started.set()
        self._set_ident()
        with _active_limbo_lock:
            _active[_get_ident()] = self



    def _set_daemon(self):
        return False



    def _exitfunc(self):
        self._Thread__stop()
        t = _pickSomeNonDaemonThread()
        if t:
            pass
        while t:
            t.join()
            t = _pickSomeNonDaemonThread()

        self._Thread__delete()




def _pickSomeNonDaemonThread():
    for t in enumerate():
        if not t.daemon and t.is_alive():
            return t




class _DummyThread(Thread):

    def __init__(self):
        Thread.__init__(self, name=_newname('Dummy-%d'))
        del self._Thread__block
        self._Thread__started.set()
        self._set_ident()
        with _active_limbo_lock:
            _active[_get_ident()] = self



    def _set_daemon(self):
        return True



    def join(self, timeout = None):
        pass




def currentThread():
    try:
        return _active[_get_ident()]
    except KeyError:
        return _DummyThread()


current_thread = currentThread

def activeCount():
    with _active_limbo_lock:
        return len(_active) + len(_limbo)


active_count = activeCount

def _enumerate():
    return _active.values() + _limbo.values()



def enumerate():
    with _active_limbo_lock:
        return _active.values() + _limbo.values()


from thread import stack_size
_shutdown = _MainThread()._exitfunc
try:
    from thread import _local as local
except ImportError:
    from _threading_local import local

def _after_fork():
    global _active_limbo_lock
    _active_limbo_lock = _allocate_lock()
    new_active = {}
    current = current_thread()
    with _active_limbo_lock:
        for thread in _active.itervalues():
            if thread is current:
                ident = _get_ident()
                thread._Thread__ident = ident
                new_active[ident] = thread
            else:
                thread._Thread__stopped = True

        _limbo.clear()
        _active.clear()
        _active.update(new_active)



def _test():

    class BoundedQueue(_Verbose):

        def __init__(self, limit):
            _Verbose.__init__(self)
            self.mon = RLock()
            self.rc = Condition(self.mon)
            self.wc = Condition(self.mon)
            self.limit = limit
            self.queue = deque()



        def put(self, item):
            self.mon.acquire()
            while len(self.queue) >= self.limit:
                self._note('put(%s): queue full', item)
                self.wc.wait()

            self.queue.append(item)
            self._note('put(%s): appended, length now %d', item, len(self.queue))
            self.rc.notify()
            self.mon.release()



        def get(self):
            self.mon.acquire()
            while not self.queue:
                self._note('get(): queue empty')
                self.rc.wait()

            item = self.queue.popleft()
            self._note('get(): got %s, %d left', item, len(self.queue))
            self.wc.notify()
            self.mon.release()
            return item




    class ProducerThread(Thread):

        def __init__(self, queue, quota):
            Thread.__init__(self, name='Producer')
            self.queue = queue
            self.quota = quota



        def run(self):
            from random import random
            counter = 0
            while counter < self.quota:
                counter = counter + 1
                self.queue.put('%s.%d' % (self.name, counter))
                _sleep(random() * 1e-05)





    class ConsumerThread(Thread):

        def __init__(self, queue, count):
            Thread.__init__(self, name='Consumer')
            self.queue = queue
            self.count = count



        def run(self):
            while self.count > 0:
                item = self.queue.get()
                print item
                self.count = self.count - 1




    NP = 3
    QL = 4
    NI = 5
    Q = BoundedQueue(QL)
    P = []
    for i in range(NP):
        t = ProducerThread(Q, NI)
        t.name = 'Producer-%d' % (i + 1)
        P.append(t)

    C = ConsumerThread(Q, NI * NP)
    for t in P:
        t.start()
        _sleep(1e-06)

    C.start()
    for t in P:
        t.join()

    C.join()


if __name__ == '__main__':
    _test()

