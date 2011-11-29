import weakref
import cPickle
import uthread
import base
import sys
from timerstuff import ClockThisWithoutTheStars
from service import ROLE_SERVICE
import macho
import log
allMonikers = weakref.WeakKeyDictionary({})

class Moniker():
    __guid__ = 'util.Moniker'
    __passbyvalue__ = 1
    __persistvar__ = ['__serviceName',
     '__nodeID',
     '__bindParams',
     '__sessionCheck']

    def __init__(self, serviceName = None, bindParams = None, nodeID = None, quicky = 0):
        global allMonikers
        self._Moniker__serviceName = serviceName
        self._Moniker__bindParams = bindParams
        self._Moniker__nodeID = nodeID
        self._Moniker__quicky = quicky
        self._Moniker__sessionCheck = None
        self.boundObject = None
        allMonikers[self] = 1



    def __del__(self):
        self._Moniker__ClearBoundObject()



    def __str__(self):
        if self.__class__ == Moniker:
            name = 'Generic'
        else:
            name = self.__class__.__name__
        args = (name,
         self._Moniker__serviceName,
         self._Moniker__nodeID,
         self._Moniker__bindParams)
        return '%s moniker on service %s, node %s, params %s' % args



    def SetSessionCheck(self, sessionCheck):
        self._Moniker__sessionCheck = sessionCheck



    def __PerformSessionCheck(self):
        if self._Moniker__sessionCheck:
            for (attribute, expected,) in self._Moniker__sessionCheck.iteritems():
                if session:
                    current = getattr(session, attribute, None)
                else:
                    current = None
                if current != expected or not expected and current:
                    log.LogTraceback('__PerformSessionCheck:  Monikers session has changed. Traceback=', toAlertSvc=0, severity=log.LGWARN)
                    raise RuntimeError('MonikerSessionCheckFailure', {'attribute': attribute,
                     'expected': expected,
                     'current': current,
                     'serviceName': self._Moniker__serviceName,
                     'bindParams': self._Moniker__bindParams})




    def ToURLString(self):
        import binascii
        return binascii.b2a_hex(cPickle.dumps((self._Moniker__serviceName, self._Moniker__bindParams), 1))



    def FromURLString(self, s):
        import binascii
        b = binascii.a2b_hex(s)
        (self._Moniker__serviceName, self._Moniker__bindParams,) = cPickle.loads(b)



    def __getstate__(self):
        ret = []
        for each in self.__persistvar__:
            ret.append(self.__dict__[('_Moniker' + each)])

        return tuple(ret)



    def __setstate__(self, state):
        for i in xrange(len(self.__persistvar__)):
            self.__dict__['_Moniker' + self.__persistvar__[i]] = state[i]

        if self._Moniker__nodeID is not None:
            sm.services['machoNet'].SetNodeOfAddress(self._Moniker__serviceName, self._Moniker__bindParams, self._Moniker__nodeID)
        self.boundObject = None
        self._Moniker__quicky = 2
        allMonikers[self] = 1


    __remobsuppmeth__ = ('RegisterObjectChangeHandler', 'UnRegisterObjectChangeHandler')

    def __getattr__(self, key):
        if key in self.__remobsuppmeth__:
            self.Bind()
            return getattr(self.boundObject, key)
        else:
            if not key[0].isupper():
                if key.startswith('__'):
                    raise AttributeError(key)
                self.Bind()
                return getattr(self.boundObject, key)
            return MonikerCallWrap(self, key)



    def __ClearBoundObject(self, disconnectDelay = 30):
        if self.boundObject is not None and isinstance(self.boundObject, base.ObjectConnection):
            try:
                self.boundObject.DisconnectObject(disconnectDelay)
            except AttributeError:
                pass
        self.boundObject = None



    def Bind(self, sess = None, call = None):
        localKeywords = ('machoTimeout', 'noCallThrottling')
        done = {}
        while 1:
            try:
                if self._Moniker__bindParams is None:
                    raise RuntimeError("Thou shall not use None as a Moniker's __bindParams")
                if '__semaphoreB__' not in self.__dict__:
                    self.__semaphoreB__ = uthread.Semaphore(('moniker::Bind', self._Moniker__serviceName, self._Moniker__bindParams))
                self.__semaphoreB__.acquire()
                try:
                    if not self.boundObject:
                        if self._Moniker__nodeID is None:
                            self._Moniker__ResolveImpl(0, sess)
                        if sess is None:
                            if session and session.role == ROLE_SERVICE:
                                sess = session.GetActualSession()
                            else:
                                sess = base.GetServiceSession('util.Moniker')
                        else:
                            sess = sess.GetActualSession()
                        if self._Moniker__nodeID == sm.services['machoNet'].GetNodeID():
                            service = sess.ConnectToService(self._Moniker__serviceName)
                            lock = service.Lock(self._Moniker__bindParams)
                            try:
                                obj = service.GetCachedObject(self._Moniker__bindParams)
                                if obj is None:
                                    obj = service.MachoBindObject(self._Moniker__bindParams)
                                    service.SetCachedObject(self._Moniker__bindParams, obj)
                                self.boundObject = ClockThisWithoutTheStars('Moniker::ConnectToObject', sess.ConnectToObject, (obj, self._Moniker__serviceName, self._Moniker__bindParams))

                            finally:
                                service.UnLock(self._Moniker__bindParams, lock)

                        else:
                            remotesvc = sess.ConnectToRemoteService(self._Moniker__serviceName, self._Moniker__nodeID)
                            self._Moniker__PerformSessionCheck()
                            if call is not None and call[2]:
                                c2 = {k:v for (k, v,) in call[2].iteritems() if k not in localKeywords}
                                call = (call[0], call[1], c2)
                            (self.boundObject, retval,) = remotesvc.MachoBindObject(self._Moniker__bindParams, call)
                            self.boundObject.persistantObjectID = (self._Moniker__serviceName, self._Moniker__bindParams)
                            return retval

                finally:
                    done[(self._Moniker__serviceName, self._Moniker__bindParams)] = 1
                    self.__semaphoreB__.release()

                if call is not None:
                    return self.MonikeredCall(call, sess)
                else:
                    return 
            except UpdateMoniker as e:
                if (e.serviceName, e.bindParams) in done:
                    log.LogException()
                    raise RuntimeError('UpdateMoniker referred us to the same location twice', (e.serviceName, e.bindParams))
                else:
                    self._Moniker__bindParams = e.bindParams
                    self._Moniker__serviceName = e.serviceName
                    self._Moniker__nodeID = e.nodeID
                    self.Unbind()
                    sys.exc_clear()




    def MonikeredCall(self, call, sess):
        retry = 0
        while 1:
            try:
                self._Moniker__PerformSessionCheck()
                if self.boundObject is None:
                    return self.Bind(sess, call)
                try:
                    return apply(getattr(self.boundObject, call[0]), call[1], call[2])
                except ReferenceError:
                    if prefs.GetValue('ReferenceErrorLogSpamKillswitch', True):
                        log.LogException('This is a fairly unique string with which we can search evelogs for - see defect 61914 for details')
                    self.Unbind()
                    sys.exc_clear()
                except UpdateMoniker as e:
                    self._Moniker__bindParams = e.bindParams
                    self._Moniker__serviceName = e.serviceName
                    self._Moniker__nodeID = e.nodeID
                    self.Unbind()
                    sys.exc_clear()
            except UserError as e:
                if e.msg == 'UnMachoDestination' and not retry:
                    retry = 1
                    self.Unresolve()
                    sys.exc_clear()
                    continue
                raise 
            except UnMachoDestination:
                if not retry:
                    retry = 1
                    self.Unresolve()
                    sys.exc_clear()
                    continue
                raise 




    def IsRunning(self):
        return self._Moniker__ResolveImpl(1)



    def QuickResolve(self):
        if self._Moniker__nodeID is None and self._Moniker__serviceName in sm.services:
            self._Moniker__nodeID = self._Moniker__ResolveImpl(self._Moniker__quicky)



    def Resolve(self, sess = None):
        return self._Moniker__ResolveImpl(0, sess)



    def __ResolveImpl(self, justQuery, sess = None):
        if '__semaphoreR__' not in self.__dict__:
            self.__semaphoreR__ = uthread.Semaphore(('moniker::Resolve', self._Moniker__serviceName, self._Moniker__bindParams))
        self.__semaphoreR__.acquire()
        try:
            if self._Moniker__nodeID is not None:
                return self._Moniker__nodeID
            else:
                if macho.mode == 'client' or base.IsInClientContext():
                    self._Moniker__nodeID = sm.services['machoNet'].GuessNodeIDFromAddress(self._Moniker__serviceName, self._Moniker__bindParams)
                    if self._Moniker__nodeID is not None:
                        return self._Moniker__nodeID
                    if not self._Moniker__nodeID:
                        self._Moniker__nodeID = sm.services['machoNet']._addressCache.Get(self._Moniker__serviceName, self._Moniker__bindParams)
                        if self._Moniker__nodeID is not None:
                            return self._Moniker__nodeID
                if sess is None:
                    if session and session.role == ROLE_SERVICE:
                        sess = session.GetActualSession()
                    else:
                        sess = base.GetServiceSession('util.Moniker')
                else:
                    sess = sess.GetActualSession()
                if justQuery == 2:
                    service = sm.services.get(self._Moniker__serviceName, None)
                    if service is None:
                        return 
                else:
                    service = sess.ConnectToAnyService(self._Moniker__serviceName)
                self._Moniker__nodeID = service.MachoResolveObject(self._Moniker__bindParams, justQuery)
                if self._Moniker__nodeID is None and not justQuery:
                    raise RuntimeError('Resolution failure:  ResolveObject returned None')
                if macho.mode == 'client' or base.IsInClientContext():
                    sm.services['machoNet'].SetNodeOfAddress(self._Moniker__serviceName, self._Moniker__bindParams, self._Moniker__nodeID)
                return self._Moniker__nodeID

        finally:
            self.__semaphoreR__.release()




    def Unresolve(self):
        while 1:
            self.Unbind()
            if '__semaphoreR__' not in self.__dict__:
                self.__semaphoreR__ = uthread.Semaphore(('moniker::Resolve', self._Moniker__serviceName, self._Moniker__bindParams))
            self.__semaphoreR__.acquire()
            try:
                if self.boundObject is None:
                    self._Moniker__nodeID = None
                    sm.services['machoNet'].SetNodeOfAddress(self._Moniker__serviceName, self._Moniker__bindParams, None)
                    return 

            finally:
                self.__semaphoreR__.release()





    def Unbind(self, disconnectDelay = 30):
        if '__semaphoreB__' not in self.__dict__:
            self.__semaphoreB__ = uthread.Semaphore(('moniker::Bind', self._Moniker__serviceName, self._Moniker__bindParams))
        self.__semaphoreB__.acquire()
        try:
            self._Moniker__ClearBoundObject(disconnectDelay)

        finally:
            self.__semaphoreB__.release()




    def GetNodeID(self):
        if self._Moniker__nodeID is None:
            self._Moniker__ResolveImpl(0)
        return self._Moniker__nodeID



    def GetSelfLocal(self):
        if self.GetNodeID() == sm.services['machoNet'].GetNodeID():
            self.Bind()
            return self.boundObject.__object__
        raise RuntimeError('You are not local %d != %d' % (self.GetNodeID(), sm.services['machoNet'].GetNodeID()))




class MonikerCallWrap():

    def __init__(self, moniker, key):
        self.moniker = moniker
        self.key = key
        if key[0] != key[0].upper():
            raise RuntimeError("This moniker has no attribute '%s'. Moniker: %s" % (key, moniker))



    def __call__(self, *args, **kw):
        try:
            return self.moniker.MonikeredCall((self.key, args, kw), None)

        finally:
            self.__dict__.clear()





class UpdateMoniker(StandardError):
    __guid__ = 'util.UpdateMoniker'
    __passbyvalue__ = 1

    def __init__(self, serviceName = None, bindParams = None, nodeID = None):
        Exception.__init__(self, 'Update')
        self.serviceName = serviceName
        self.nodeID = nodeID
        self.bindParams = bindParams




def GetWorldSpace(worldSpaceID):
    moniker = Moniker('worldSpaceServer', worldSpaceID)
    return moniker


exports = {'util.allMonikers': allMonikers,
 'moniker.GetWorldSpace': GetWorldSpace}

