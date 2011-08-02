import types
try:
    import ctypes
except ImportError:
    raise ImportError('You cannot use paste.util.killthread without ctypes installed')
if not hasattr(ctypes, 'pythonapi'):
    raise ImportError('You cannot use paste.util.killthread without ctypes.pythonapi')

def async_raise(tid, exctype):
    if not isinstance(exctype, (types.ClassType, type)):
        raise TypeError('Only types can be raised (not instances)')
    if not isinstance(tid, int):
        raise TypeError('tid must be an integer')
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exctype))
    if res == 0:
        raise ValueError('invalid thread id')
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), 0)
        raise SystemError('PyThreadState_SetAsyncExc failed')



