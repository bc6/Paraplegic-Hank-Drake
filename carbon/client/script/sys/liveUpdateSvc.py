import service
import marshal
import blue
import types

class LiveUpdateSvc(service.Service):
    __guid__ = 'svc.liveUpdateSvc'
    __displayname__ = 'Client Live-update Service'
    __dependencies__ = ['machoNet']
    __exportedcalls__ = {'GetMethods': [service.ROLE_SERVICE]}
    __notifyevents__ = ['OnLiveClientUpdate']

    def OnLiveClientUpdate(self, theUpdate):
        self.LogInfo('Applying live update - type:', theUpdate.codeType, 'object:', theUpdate.objectID, 'method:', theUpdate.methodName)
        code = marshal.loads(theUpdate.code)
        if theUpdate.codeType == 'globalObjectMethod':
            import __builtin__
            obj = getattr(__builtin__, theUpdate.objectID, None)
            if obj:
                method = getattr(obj, theUpdate.methodName, None)
                if method:
                    method.im_func.func_code = code
                else:
                    self.LogError('Failed to apply live update - Method not found. type:', theUpdate.codeType, 'object:', theUpdate.objectID, 'method:', theUpdate.methodName)
            else:
                self.LogError('Failed to apply live update - Object not found. type:', theUpdate.codeType, 'object:', theUpdate.objectID, 'method:', theUpdate.methodName)
        elif theUpdate.codeType == 'globalFunction':
            import __builtin__
            fullname = '%s.%s' % (theUpdate.objectID, theUpdate.methodName)
            namespace = __builtin__.Import.im_self.globs.get(fullname)
            if namespace:
                function = namespace.get(theUpdate.methodName, None)
                if type(function) is types.FunctionType:
                    function.func_code = code
                else:
                    self.LogError('Failed to apply live update - Function not found. type:', theUpdate.codeType, 'object:', theUpdate.objectID, 'method:', theUpdate.methodName)
            else:
                self.LogError('Failed to apply live update - namespace not found. type:', theUpdate.codeType, 'object:', theUpdate.objectID, 'method:', theUpdate.methodName)
        elif theUpdate.codeType == 'globalClassMethod':
            import __builtin__
            import inspect
            (guid, className,) = theUpdate.objectID.split('::')
            namespace = __builtin__.Import.im_self.globs.get(guid)
            if namespace:
                globalClass = namespace.get(className)
                if globalClass:
                    method = getattr(globalClass, theUpdate.methodName, None)
                    if method:
                        method.im_func.func_code = code
                    else:
                        self.LogError('Failed to apply live update - Method not found. type:', theUpdate.codeType, 'object:', theUpdate.objectID, 'method:', theUpdate.methodName)
                else:
                    self.LogError('Failed to apply live update - Object not found. type:', theUpdate.codeType, 'object:', theUpdate.objectID, 'method:', theUpdate.methodName)
            else:
                self.LogError('Failed to apply live update - namespace not found. type:', theUpdate.codeType, 'object:', theUpdate.objectID, 'method:', theUpdate.methodName)
        else:
            self.LogError('Update methodology', codeType, 'unknown. ', theUpdate.objectID, '::', theUpdate.methodName, 'not repaired')
            return 
        self.LogInfo('Successfully applied live update - type:', theUpdate.codeType, 'object:', theUpdate.objectID, 'method:', theUpdate.methodName)



    def GetMethods(self, codeType, pObjectID = None, pMethod = None):
        import __builtin__
        objectMethods = {}
        code = None
        if codeType == 'globalObjectMethod':
            for objectName in dir(__builtin__):
                object = getattr(__builtin__, objectName)
                if type(object) is types.InstanceType:
                    if objectName not in objectMethods:
                        objectMethods[objectName] = [objectName, []]
                    for methodName in dir(object):
                        method = getattr(object, methodName)
                        if type(method) is types.MethodType:
                            objectMethods[objectName][1].append(method.im_func.func_name)
                            if objectName == pObjectID and pMethod == method.im_func.func_name:
                                code = method.im_func.func_code


        elif codeType == 'globalFunction':
            for (objectName, foo,) in __builtin__.Import.im_self.globs.items():
                (objectID, functionName,) = objectName.rsplit('.', 1)
                function = foo.get(functionName, None)
                if type(function) is types.FunctionType:
                    if objectID not in objectMethods:
                        objectMethods[objectID] = [objectID, []]
                    if type(function) is types.FunctionType:
                        objectMethods[objectID][1].append(function.func_name)
                        if objectID == pObjectID and pMethod == function.func_name:
                            code = function.func_code

        elif codeType == 'globalClassMethod':
            import inspect
            for (namespaceName, namespaceContents,) in __builtin__.Import.im_self.globs.items():
                for (itemName, itemValue,) in namespaceContents.items():
                    if namespaceName == getattr(itemValue, '__guid__', None):
                        for methodName in dir(itemValue):
                            if not methodName.startswith('__'):
                                method = getattr(itemValue, methodName)
                                if type(method) is types.MethodType:
                                    objectID = '%s::%s' % (namespaceName, itemName)
                                    if objectID not in objectMethods:
                                        objectMethods[objectID] = [objectID, []]
                                    objectMethods[objectID][1].append(methodName)
                                    if objectID == pObjectID and pMethod == methodName:
                                        code = method.im_func.func_code



        delum = []
        for objectID in objectMethods:
            if not objectMethods[objectID][1]:
                delum.append(objectID)

        for delit in delum:
            del objectMethods[delit]

        code = marshal.dumps(code)
        return (objectMethods, code)




