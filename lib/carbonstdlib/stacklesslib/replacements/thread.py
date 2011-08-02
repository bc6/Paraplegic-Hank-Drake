from __future__ import absolute_import
import traceback
import stackless
import stacklesslib.locks

class error(RuntimeError):
    pass
_thread_count = 0

def _count():
    global _thread_count
    return _thread_count



class Thread(stackless.tasklet):
    __slots__ = ['__dict__']

    def __new__(cls):
        return stackless.tasklet.__new__(cls, cls._thread_main)



    @staticmethod
    def _thread_main(func, args, kwargs):
        global _thread_count
        try:
            try:
                try:
                    func(*args, **kwargs)
                except SystemExit:
                    raise TaskletExit
            except Exception:
                traceback.print_exc()

        finally:
            _thread_count -= 1





def start_new_thread(function, args, kwargs = {}):
    global _thread_count
    t = Thread()
    t(function, args, kwargs)
    _thread_count += 1
    return id(t)



def interrupt_main():
    pass



def exit():
    stackless.getcurrent().kill()



def get_ident():
    return id(stackless.getcurrent())


_stack_size = 0

def stack_size(size = None):
    global _stack_size
    old = _stack_size
    if size is not None:
        _stack_size = size
    return old



def allocate_lock(self = None):
    return LockType()



class LockType(stacklesslib.locks.Lock):

    def locked(self):
        return self.owning != None




