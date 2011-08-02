
class classinstancemethod(object):

    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__



    def __get__(self, obj, type = None):
        return _methodwrapper(self.func, obj=obj, type=type)




class _methodwrapper(object):

    def __init__(self, func, obj, type):
        self.func = func
        self.obj = obj
        self.type = type



    def __call__(self, *args, **kw):
        return self.func(*((self.obj, self.type) + args), **kw)



    def __repr__(self):
        if self.obj is None:
            return '<bound class method %s.%s>' % (self.type.__name__, self.func.func_name)
        else:
            return '<bound method %s.%s of %r>' % (self.type.__name__, self.func.func_name, self.obj)




