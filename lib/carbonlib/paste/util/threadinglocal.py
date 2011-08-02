try:
    import threading
except ImportError:

    class local(object):
        pass
else:
    try:
        local = threading.local
    except AttributeError:
        import thread

        class local(object):

            def __init__(self):
                self.__dict__['__objs'] = {}



            def __getattr__(self, attr, g = thread.get_ident):
                try:
                    return self.__dict__['__objs'][g()][attr]
                except KeyError:
                    raise AttributeError('No variable %s defined for the thread %s' % (attr, g()))



            def __setattr__(self, attr, value, g = thread.get_ident):
                self.__dict__['__objs'].setdefault(g(), {})[attr] = value



            def __delattr__(self, attr, g = thread.get_ident):
                try:
                    del self.__dict__['__objs'][g()][attr]
                except KeyError:
                    raise AttributeError('No variable %s defined for thread %s' % (attr, g()))




