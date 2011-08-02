import uicls
import weakref

class BackgroundList(object):
    __guid__ = 'uicls.BackgroundList'

    def __init__(self, owner):
        self._childrenObjects = []
        self._ownerRef = weakref.ref(owner)



    def GetOwner(self):
        if self._ownerRef:
            return self._ownerRef()



    def append(self, obj):
        if not isinstance(obj, uicls.Base):
            print 'Someone trying to add item which is not of correct type',
            print obj
            return 
        owner = self.GetOwner()
        if owner:
            self._childrenObjects.append(obj)
            obj._parentRef = weakref.ref(owner)
            owner.AppendBackgroundObject(obj)
            return self



    def insert(self, idx, obj):
        if not isinstance(obj, uicls.Base):
            print 'Someone trying to add item which is not of correct type',
            print obj
            return 
        if idx == -1:
            idx = len(self._childrenObjects)
        owner = self.GetOwner()
        if owner:
            self._childrenObjects.insert(idx, obj)
            owner.InsertBackgroundObject(idx, obj)
            obj._parentRef = weakref.ref(owner)
            return self



    def remove(self, obj):
        if obj in self._childrenObjects:
            self._childrenObjects.remove(obj)
        obj._parentRef = None
        owner = self.GetOwner()
        if owner:
            owner.RemoveBackgroundObject(obj)
        return self



    def index(self, obj):
        return self._childrenObjects.index(obj)



    def __getitem__(self, key):
        return self._childrenObjects[key]



    def __len__(self):
        return len(self._childrenObjects)



    def __iter__(self):
        return iter(self._childrenObjects)



    def __getslice__(self, f, t):
        return self._childrenObjects[f:t]



    def __contains__(self, obj):
        return obj in self._childrenObjects



    def __cmp__(self, other):
        return cmp(other, self._childrenObjects)



    def __reversed__(self):
        return reversed(self._childrenObjects)



    def __delitem__(self, key):
        del self._childrenObjects[key]




