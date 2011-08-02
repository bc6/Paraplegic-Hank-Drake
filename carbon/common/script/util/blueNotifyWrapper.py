import bluepy
import weakref

def BlueClassNotifyWrap(blueClassName):

    class BlueNotifyWrapper(bluepy.WrapBlueClass(blueClassName)):
        _alwaysEditableMembers = []

        def AddNotify(self, attrName, callback):
            if not hasattr(self, '_notifyChangeList'):
                self._notifyEnabled = True
                self._notifyChangeListBoundFuncs = weakref.WeakValueDictionary()
                self._notifyChangeListBoundObjects = weakref.WeakValueDictionary()
                self._notifyChangeList = weakref.WeakValueDictionary()
            if getattr(callback, 'im_self'):
                self._notifyChangeListBoundFuncs[attrName] = callback.im_func
                self._notifyChangeListBoundObjects[attrName] = callback.im_self
            else:
                self._notifyChangeList[attrName] = callback



        def EnableNotify(self):
            self._notifyEnabled = True



        def DisableNotify(self):
            self._notifyEnabled = False



        def IsNotifyEnabled(self):
            return self._notifyEnabled



        def IsLocked(self):
            return False



        def __setattr__(self, key, value):
            if key in self.__members__ and key not in self._alwaysEditableMembers and self.IsLocked():
                return 
            if hasattr(self, '_notifyChangeList') and self._notifyEnabled:
                callFunc = self._notifyChangeList.get(key, None)
                if callFunc:
                    callFunc(value)
                unboundFunc = self._notifyChangeListBoundFuncs.get(key, None)
                obj = self._notifyChangeListBoundObjects.get(key, None)
                if unboundFunc:
                    if obj:
                        unboundFunc(obj, value)
                    else:
                        del self._notifyChangeListBoundFuncs[key]
                elif obj:
                    del self._notifyChangeListBoundObjects[key]
            ourSetAttr = BlueNotifyWrapper.__setattr__
            del BlueNotifyWrapper.__setattr__
            setattr(self, key, value)
            BlueNotifyWrapper.__setattr__ = ourSetAttr



    return BlueNotifyWrapper


exports = {'util.BlueClassNotifyWrap': BlueClassNotifyWrap}

