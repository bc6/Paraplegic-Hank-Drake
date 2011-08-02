import _weakref
import types

class WeakRefAttrObject(object):
    __guid__ = 'util.WeakRefAttrObject'

    def __setattr__(self, name, val):
        if callable(val):
            ref = CallableWeakRef(val)
        else:
            ref = _weakref.ref(val)
        self.__dict__[name] = ref



    def __getattribute__(self, name):
        ret = object.__getattribute__(self, name)
        if type(ret) == _weakref.ReferenceType or getattr(ret, 'isWeakRef', 0):
            ret = ret()
        return ret




def CallableWeakRef(function):
    if not callable(function):
        raise TypeError, 'Function must be callable.'
    if type(function) == types.FunctionType:
        return _weakref.ref(function)
    if hasattr(function, 'im_self'):
        subref = _weakref.ref(function.im_self)
        name = function.im_func.func_name
        ret = lambda : getattr(subref(), name, None)
    elif hasattr(function, '__inst__'):
        subref = _weakref.ref(function.__inst__)
        name = function.__func__.func_name
        ret = lambda : getattr(subref(), name, None)
    elif hasattr(function, '__self__'):
        subref = _weakref.ref(function.__self__)
        name = function.__name__
        ret = lambda : getattr(subref(), name, None)
    elif type(function) == types.InstanceType:
        return _weakref.ref(function)
    raise RuntimeError('%s not supported!' % type(function))
    ret.isWeakRef = 1
    return ret


exports = {'util.CallableWeakRef': CallableWeakRef,
 'util.WeakRefAttrObject': WeakRefAttrObject}

