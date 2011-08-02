import blue
import functools
import inspect
import nasty
import sys
GetCurrent = blue.pyos.taskletTimer.GetCurrent

def ContextDeco(func, objName):
    funcName = func.__name__
    contextName = objName + '::' + funcName
    statContextName = objName + '/' + funcName

    @functools.wraps(func)
    def ContextFunc(*args, **kwargs):
        topContext = False
        blue.statistics.EnterZone(statContextName)
        PushMark(contextName)
        try:
            results = func(*args, **kwargs)

        finally:
            PopMark(contextName)
            blue.statistics.LeaveZone(statContextName)

        return results


    return ContextFunc


functionsToNotWrap = ('ContextDeco', 'AddFuncContextsToObject', 'AddFuncContextsToAllServices', 'AddFuncContextsToAllModules', 'PushMark', 'PopMark')

def AddFuncContextsToObject(obj, objName):
    functionTest = inspect.isfunction
    if inspect.isclass(obj):

        def functionTest(o):
            if hasattr(o, 'im_self') and o.im_self is not None:
                return False
            return inspect.ismethod(o)


    for (key, method,) in inspect.getmembers(obj, functionTest):
        if (not key.startswith('__') or key == '__init__') and key not in functionsToNotWrap:
            setattr(obj, key, ContextDeco(method, objName))




def AddFuncContextsToAllServices():
    for (svcName, service,) in sm.services.iteritems():
        AddFuncContextsToObject(service, 'svc.' + svcName)




def AddFuncContextsToAllModules():
    for (modName, module,) in nasty.nasty.mods.iteritems():
        AddFuncContextsToObject(module, modName)

    for (modName, module,) in sys.modules.iteritems():
        if modName not in nasty.nasty.mods and modName.startswith('app'):
            AddFuncContextsToObject(module, modName)



exports = {'util.AddFuncContextsToObject': AddFuncContextsToObject,
 'util.AddFuncContextsToAllServices': AddFuncContextsToAllServices,
 'util.AddFuncContextsToAllModules': AddFuncContextsToAllModules}

