import weakref

class BaseCorpObject:
    __guid__ = 'corpObject.base'

    def __init__(self, boundObject):
        self.boundObject = weakref.proxy(boundObject)
        dependencies = self.boundObject.GetDependencies()
        for dependency in dependencies:
            setattr(self, dependency, getattr(self.boundObject, dependency))




    def DoObjectWeakRefConnections(self):
        boundObjectNames = self.boundObject.GetObjectNames()
        for objectName in boundObjectNames:
            setattr(self, 'corp__%s' % objectName, weakref.proxy(getattr(self.boundObject, objectName)))




    def GetCorpRegistry(self):
        return self.boundObject.GetCorpRegistry()



    def GetCorpStationManager(self):
        return self.boundObject.GetCorpStationManager()



    def LogInfo(self, *info):
        self.boundObject.LogInfo(*info)



    def LogWarn(self, *info):
        self.boundObject.LogWarn(*info)



    def LogError(self, *info):
        self.boundObject.LogError(*info)



    def GetAddRemoveFromChange(self, change):
        bAdd = 1
        bRemove = 1
        self.LogInfo(self.__class__.__name__, 'GetAddRemoveFromChange change:', change)
        if not change.items():
            (bAdd, bRemove,) = (0, 0)
        for (old, new,) in change.itervalues():
            if old is None and new is None:
                continue
            if old is not None:
                bAdd = 0
            if new is not None:
                bRemove = 0

        if bAdd and bRemove:
            raise RuntimeError('GetAddRemoveFromChange WTF')
        self.LogInfo(self.__class__.__name__, 'GetAddRemoveFromChange bAdd:', bAdd, 'bRemove:', bRemove)
        return (bAdd, bRemove)




