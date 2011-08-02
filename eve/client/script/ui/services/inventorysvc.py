import _weakref
import uthread
import service
import log
import blue
import util
import uix
import sys
import log

class InventorySvc(service.Service):
    __guid__ = 'svc.inv'
    __exportedcalls__ = {'Register': [],
     'Unregister': []}
    __notifyevents__ = []

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.regs = {}



    def Trace(self, *what):
        pass



    def OnItemChange(self, item, change):
        self.LogInfo('OnItemChange', change, item)
        fancyChange = {}
        for (k, v,) in change.iteritems():
            fancyChange[item.__columns__[k]] = (v, '->', item[k])

        self.LogInfo('OnItemChange (fancy)', fancyChange, item)
        old = blue.DBRow(item)
        for (k, v,) in change.iteritems():
            if k == const.ixSingleton and v == 0:
                v = 1
            if k in (const.ixStackSize, const.ixSingleton):
                k = const.ixQuantity
            old[k] = v

        closeContainer = 0
        containerCookie = None
        containerName = ''
        if item.groupID in (const.groupWreck,
         const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer) and item.singleton:
            if const.ixLocationID in change or const.ixOwnerID in change or const.ixFlag in change:
                closeContainer = 1
                containerName = 'loot_%s' % item.itemID
        for (cookie, wr,) in self.regs.items():
            ob = wr()
            if not ob or getattr(ob, '__typename__', None) == 'Tr2Sprite2dContainer' and getattr(ob, 'destroyed') == 1:
                self.Trace('dead dud', ob, cookie)
                self.Unregister(cookie)
                continue
            if not getattr(ob, 'invReady', 0):
                self.Trace('Object not ready yet', ob)
                continue
            if closeContainer == 1:
                if getattr(ob, 'id', 0) == item.itemID:
                    containerCookie = cookie
                    continue
                if getattr(ob, 'name', '') == containerName:
                    containerCookie = cookie
                    continue
            if not hasattr(ob, 'IsMine'):
                continue
            wasHere = old.stacksize != 0 and ob.IsMine(old)
            isHere = item.stacksize != 0 and ob.IsMine(item)
            self.Trace('wasHere', wasHere, 'isHere', isHere)
            wasLocatedIn = wasHere
            if not wasHere and getattr(ob, 'IsLocatedIn', None):
                wasLocatedIn = ob.IsLocatedIn(old)
            isLocatedIn = isHere
            if not isHere and getattr(ob, 'IsLocatedIn', None):
                isLocatedIn = ob.IsLocatedIn(item)
            try:
                if not wasHere and not isHere and not wasLocatedIn and not isLocatedIn:
                    continue
                if wasHere and isHere and getattr(ob, 'UpdateItem', None):
                    ob.UpdateItem(item, change)
                elif wasHere and not isHere and getattr(ob, 'RemoveItem', None):
                    ob.RemoveItem(item)
                elif not wasHere and isHere and getattr(ob, 'AddItem', None):
                    ob.AddItem(item)
                if getattr(ob, 'OnInvChange', None):
                    ob.OnInvChange(item, change)
            except:
                self.Unregister(cookie)
                log.LogException('svc.inv')
                sys.exc_clear()

        if closeContainer == 1:
            if containerCookie is not None:
                self.Unregister(containerCookie)
            sm.GetService('window').CloseContainer(item.itemID)



    def Register(self, callbackObj):
        cookie = uthread.uniqueId() or uthread.uniqueId()
        self.LogInfo('Registering', cookie, callbackObj)
        self.regs[cookie] = _weakref.ref(callbackObj)
        return cookie



    def Unregister(self, cookie):
        if cookie in self.regs:
            del self.regs[cookie]
            self.LogInfo('Unregistered', cookie)
        else:
            log.LogWarn('inv.Unregister: Unknown cookie', cookie)




