import sys
import paste.util.threadinglocal as threadinglocal
__all__ = ['StackedObjectProxy',
 'RegistryManager',
 'StackedObjectRestorer',
 'restorer']

class NoDefault(object):
    pass

class StackedObjectProxy(object):

    def __init__(self, default = NoDefault, name = 'Default'):
        self.__dict__['____name__'] = name
        self.__dict__['____local__'] = threadinglocal.local()
        if default is not NoDefault:
            self.__dict__['____default_object__'] = default



    def __dir__(self):
        dir_list = dir(self.__class__) + self.__dict__.keys()
        try:
            dir_list.extend(dir(self._current_obj()))
        except TypeError:
            pass
        dir_list.sort()
        return dir_list



    def __getattr__(self, attr):
        return getattr(self._current_obj(), attr)



    def __setattr__(self, attr, value):
        setattr(self._current_obj(), attr, value)



    def __delattr__(self, name):
        delattr(self._current_obj(), name)



    def __getitem__(self, key):
        return self._current_obj()[key]



    def __setitem__(self, key, value):
        self._current_obj()[key] = value



    def __delitem__(self, key):
        del self._current_obj()[key]



    def __call__(self, *args, **kw):
        return self._current_obj()(*args, **kw)



    def __repr__(self):
        try:
            return repr(self._current_obj())
        except (TypeError, AttributeError):
            return '<%s.%s object at 0x%x>' % (self.__class__.__module__, self.__class__.__name__, id(self))



    def __iter__(self):
        return iter(self._current_obj())



    def __len__(self):
        return len(self._current_obj())



    def __contains__(self, key):
        return key in self._current_obj()



    def __nonzero__(self):
        return bool(self._current_obj())



    def _current_obj(self):
        try:
            objects = self.____local__.objects
        except AttributeError:
            objects = None
        if objects:
            return objects[-1]
        obj = self.__dict__.get('____default_object__', NoDefault)
        if obj is not NoDefault:
            return obj
        raise TypeError('No object (name: %s) has been registered for this thread' % self.____name__)



    def _push_object(self, obj):
        try:
            self.____local__.objects.append(obj)
        except AttributeError:
            self.____local__.objects = []
            self.____local__.objects.append(obj)



    def _pop_object(self, obj = None):
        try:
            popped = self.____local__.objects.pop()
            if obj and popped is not obj:
                raise AssertionError('The object popped (%s) is not the same as the object expected (%s)' % (popped, obj))
        except AttributeError:
            raise AssertionError('No object has been registered for this thread')



    def _object_stack(self):
        try:
            try:
                objs = self.____local__.objects
            except AttributeError:
                return []
            return objs[:]
        except AssertionError:
            return []



    def _current_obj_restoration(self):
        request_id = restorer.in_restoration()
        if request_id:
            return restorer.get_saved_proxied_obj(self, request_id)
        return self._current_obj_orig()


    _current_obj_restoration.__doc__ = '%s\n(StackedObjectRestorer restoration enabled)' % _current_obj.__doc__

    def _push_object_restoration(self, obj):
        if not restorer.in_restoration():
            self._push_object_orig(obj)


    _push_object_restoration.__doc__ = '%s\n(StackedObjectRestorer restoration enabled)' % _push_object.__doc__

    def _pop_object_restoration(self, obj = None):
        if not restorer.in_restoration():
            self._pop_object_orig(obj)


    _pop_object_restoration.__doc__ = '%s\n(StackedObjectRestorer restoration enabled)' % _pop_object.__doc__


class Registry(object):

    def __init__(self):
        self.reglist = []



    def prepare(self):
        self.reglist.append({})



    def register(self, stacked, obj):
        myreglist = self.reglist[-1]
        stacked_id = id(stacked)
        if stacked_id in myreglist:
            stacked._pop_object(myreglist[stacked_id][1])
            del myreglist[stacked_id]
        stacked._push_object(obj)
        myreglist[stacked_id] = (stacked, obj)



    def multiregister(self, stacklist):
        myreglist = self.reglist[-1]
        for (stacked, obj,) in stacklist:
            stacked_id = id(stacked)
            if stacked_id in myreglist:
                stacked._pop_object(myreglist[stacked_id][1])
                del myreglist[stacked_id]
            stacked._push_object(obj)
            myreglist[stacked_id] = (stacked, obj)



    replace = register

    def cleanup(self):
        for (stacked, obj,) in self.reglist[-1].itervalues():
            stacked._pop_object(obj)

        self.reglist.pop()




class RegistryManager(object):

    def __init__(self, application, streaming = False):
        self.application = application
        self.streaming = streaming



    def __call__(self, environ, start_response):
        app_iter = None
        reg = environ.setdefault('paste.registry', Registry())
        reg.prepare()
        if self.streaming:
            return self.streaming_iter(reg, environ, start_response)
        try:
            app_iter = self.application(environ, start_response)
        except Exception as e:
            if environ.get('paste.evalexception'):
                expected = False
                for expect in environ.get('paste.expected_exceptions', []):
                    if isinstance(e, expect):
                        expected = True

                if not expected:
                    restorer.save_registry_state(environ)
            reg.cleanup()
            raise 
        except:
            if environ.get('paste.evalexception'):
                restorer.save_registry_state(environ)
            reg.cleanup()
            raise 
        else:
            reg.cleanup()
        return app_iter



    def streaming_iter(self, reg, environ, start_response):
        try:
            for item in self.application(environ, start_response):
                yield item

        except Exception as e:
            if environ.get('paste.evalexception'):
                expected = False
                for expect in environ.get('paste.expected_exceptions', []):
                    if isinstance(e, expect):
                        expected = True

                if not expected:
                    restorer.save_registry_state(environ)
            reg.cleanup()
            raise 
        except:
            if environ.get('paste.evalexception'):
                restorer.save_registry_state(environ)
            reg.cleanup()
            raise 
        else:
            reg.cleanup()




class StackedObjectRestorer(object):

    def __init__(self):
        self.saved_registry_states = {}
        self.restoration_context_id = threadinglocal.local()



    def save_registry_state(self, environ):
        registry = environ.get('paste.registry')
        if not registry or not len(registry.reglist) or self.get_request_id(environ) in self.saved_registry_states:
            return 
        self.saved_registry_states[self.get_request_id(environ)] = (registry, registry.reglist[:])
        for reglist in registry.reglist:
            for (stacked, obj,) in reglist.itervalues():
                self.enable_restoration(stacked)





    def get_saved_proxied_obj(self, stacked, request_id):
        reglist = self.saved_registry_states[request_id][1]
        stack_level = len(reglist) - 1
        stacked_id = id(stacked)
        while True:
            if stack_level < 0:
                return stacked._current_obj_orig()
            context = reglist[stack_level]
            if stacked_id in context:
                break
            stack_level -= 1

        return context[stacked_id][1]



    def enable_restoration(self, stacked):
        if '_current_obj_orig' in stacked.__dict__:
            return 
        for func_name in ('_current_obj', '_push_object', '_pop_object'):
            orig_func = getattr(stacked, func_name)
            restoration_func = getattr(stacked, func_name + '_restoration')
            stacked.__dict__[func_name + '_orig'] = orig_func
            stacked.__dict__[func_name] = restoration_func




    def get_request_id(self, environ):
        from paste.evalexception.middleware import get_debug_count
        return get_debug_count(environ)



    def restoration_begin(self, request_id):
        if request_id in self.saved_registry_states:
            (registry, reglist,) = self.saved_registry_states[request_id]
            registry.reglist = reglist
        self.restoration_context_id.request_id = request_id



    def restoration_end(self):
        try:
            del self.restoration_context_id.request_id
        except AttributeError:
            pass



    def in_restoration(self):
        return getattr(self.restoration_context_id, 'request_id', False)



restorer = StackedObjectRestorer()

def make_registry_manager(app, global_conf):
    return RegistryManager(app)


make_registry_manager.__doc__ = RegistryManager.__doc__

