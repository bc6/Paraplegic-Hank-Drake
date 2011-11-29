import blue
import weakref
import types
import stackless
import util
import uthread
import base
from timerstuff import ClockThisWithoutTheStars
import objectCaching
import copy
import macho
import sys
import service
import log
MACHONETMSG_TYPE_AUTHENTICATION_REQ = 0
MACHONETMSG_TYPE_AUTHENTICATION_RSP = 1

class ObjectCall():
    __guid__ = 'gpcs.ObjectCall'

    def __init__(self):
        if macho.mode == 'client':
            self.identifier = 'C=0'
        else:
            self.identifier = 'N=%d' % sm.services['machoNet'].nodeID
        self.releasedObjects = {}
        uthread.new(self._ObjectCall__ReleaseObjectHelper).context = 'machoNet::ObjectCall.ReleaseObjectHelper'



    def __ReleaseObjectHelper(self):
        while not self.machoNet.stop:
            blue.pyos.synchro.SleepWallclock(30000)
            if self.releasedObjects:
                tmp = self.releasedObjects
                self.releasedObjects = {}
                chrto = {}
                for (objectID, v,) in tmp.iteritems():
                    for (refID, sess, destination,) in v:
                        if hasattr(destination, 'nodeID'):
                            if objectID not in sess.machoObjectConnectionsByObjectID:
                                daKey = (sess.sid, destination.nodeID)
                                if daKey in chrto:
                                    chrto[daKey][2].append((objectID, refID))
                                else:
                                    chrto[daKey] = [sess, destination, [(objectID, refID)]]


                for v in chrto.itervalues():
                    oidsminus = {}
                    for each in v[2]:
                        if each[0] in oidsminus:
                            oidsminus[each[0]] = max(each[1], oidsminus[each[0]])
                        else:
                            oidsminus[each[0]] = each[1]

                    oob = {'OID-': oidsminus}
                    self.ObjectCall(oob, 'ClientHasReleasedTheseObjects', -1, v[0], v[1], v[2], 'ClientHasReleasedTheseObjects')





    def CallUp(self, packet):
        if packet.command == MACHONETMSG_TYPE_AUTHENTICATION_REQ:
            retval = self.ForwardCallUp(packet)
            self._ObjectCall__StringifyPayloadForLogging(retval, retval.payload)
            retval.payload = self.ToPickle(retval.payload)
            if self.added_objects:
                retval.oob['OID+'] = self.added_objects
            retval.compressedPart = self.compressedPart
            return retval
        else:
            if packet.payload[0]:
                tup = self.FromPickle(packet.payload[1], packet.source)
                (objectID, method, args,) = (tup[0], tup[1], tup[2])
                if objectID[0] == 'C' and macho.mode == 'client':
                    (cid, oid,) = objectID.split(':')
                    objectID = '%s:%s' % (self.identifier, oid)
                if objectID not in session.machoObjectsByID:
                    session.DumpSession('OBJECTNOTMEMBER', 'The specified object (%s) is not a member of this session' % objectID)
                    raise UnMachoDestination('The specified object (%s) is not a member of this session' % objectID)
                object = session.machoObjectsByID[objectID][1]
                if isinstance(object, base.ObjectConnection):
                    objclass = object.GetObjectConnectionLogClass()
                else:
                    try:
                        try:
                            objclass = object.__logname__
                        except AttributeError:
                            try:
                                objclass = object.__guid__.split('.')
                                if len(objclass) > 1:
                                    objclass = objclass[1]
                                else:
                                    objclass = objclass[0]
                                try:
                                    setattr(object, '__logname__', objclass)
                                except StandardError:
                                    pass
                            except AttributeError:
                                objclass = object.__class__.__name__
                    except StandardError:
                        objclass = 'CrappyClass'
                    sys.exc_clear()
                callTimer = base.CallTimer('%s::%s (ObjectCall\\Server)' % (objclass, method))
                try:
                    func = getattr(object, method)
                    if method in object.__dict__.get('__restrictedcalls__', {}) or method.startswith('_'):
                        raise RuntimeError('This call can only be the result of a hack attack', method)
                    if not isinstance(object, base.ObjectConnection):
                        if 0 == session.role & service.ROLE_SERVICE and hasattr(object, '__exportedcalls__') and method not in object.__exportedcalls__:
                            raise RuntimeError('%s call is not exported from this pass-by-reference object.' % method)
                        if not session.role & service.ROLE_SERVICE:
                            paramList = object.__exportedcalls__.get(method, None)
                            paramDict = None
                            if paramList is not None:
                                if type(paramList) is list:
                                    if len(paramList):
                                        tmp = {}
                                        tmp['role'] = paramList[0]
                                        tmp['preargs'] = paramList[1:]
                                        paramDict = tmp
                                elif type(paramList) is dict:
                                    paramDict = paramList
                            if paramDict is not None:
                                role = paramDict.get('role', service.ROLE_SERVICE)
                                if not role & session.role:
                                    session.LogSessionError("Called %s::%s, which requires role 0x%x, which the user doesn't have. User has role 0x%x" % (object.__class__.__name__,
                                     method,
                                     role,
                                     session.role))
                                    raise RuntimeError('RoleNotAssigned', "%s::%s requires role 0x%x, which the user doesn't have. User has role 0x%x. Calling session: %s" % (object.__class__.__name__,
                                     method,
                                     role,
                                     session.role,
                                     str(session)))
                                preargs = paramDict.get('preargs', [])
                                args2 = len(preargs) * [None] + list(args)
                                for i in range(len(preargs)):
                                    args2[i] = getattr(session, preargs[i])

                                args = tuple(args2)
                        if len(tup) == 4 and 'machoVersion' in tup[3]:
                            if len(tup[3]) == 1:
                                tup = (tup[0], tup[1], tup[2])
                            else:
                                del tup[3]['machoVersion']
                    if len(tup) == 3:
                        retval = ClockThisWithoutTheStars('Remote Object Call::%s::%s' % (objclass, method), func, args)
                    else:
                        retval = ClockThisWithoutTheStars('Remote Object Call::%s::%s' % (objclass, method), func, args, tup[3])
                    retpickle = self.ToPickle(retval)
                    retval = packet.Response(payload=retpickle)
                    if self.added_objects:
                        retval.oob['OID+'] = self.added_objects
                    self._ObjectCall__StringifyPayloadForLogging(retval, retpickle)
                    retval.compressedPart = self.compressedPart

                finally:
                    callTimer.Done()

                return retval
            packet.payload = self.FromPickle(packet.payload[1], packet.source)
            retval = self.ForwardCallUp(packet)
            self._ObjectCall__StringifyPayloadForLogging(retval, retval.payload)
            retval.payload = self.ToPickle(retval.payload)
            if self.added_objects:
                retval.oob['OID+'] = self.added_objects
            retval.compressedPart = self.compressedPart
            return retval



    def CallDown(self, packet):
        if packet.command == MACHONETMSG_TYPE_AUTHENTICATION_REQ:
            retval = self.ForwardCallDown(packet)
            retval.payload = self.FromPickle(retval.payload, packet.destination)
            return retval
        else:
            trace = False
            if packet.oob.get('traceMe', False) is True:
                log.general.Log('ObjectCall::CallDown: ForwardCallDown ist: %s' % str(self.ForwardCallDown), log.LGNOTICE)
            self._ObjectCall__StringifyPayloadForLogging(packet, packet.payload)
            packet.payload = (0, self.ToPickle(packet.payload, 0))
            if self.added_objects:
                packet.oob['OID+'] = self.added_objects
            packet.compressedPart = self.compressedPart
            retval = self.ForwardCallDown(packet)
            retval.payload = self.FromPickle(retval.payload, packet.destination)
            return retval



    def NotifyUp(self, packet):
        if packet.payload[0] == 1:
            tup = self.FromPickle(packet.payload[1], packet.source)
            (objectID, method, args,) = (tup[0], tup[1], tup[2])
            if method == 'ClientHasReleasedTheseObjects':
                oidsandrefs = objectID
                for each in oidsandrefs:
                    (objectID, refID,) = each
                    if objectID in session.machoObjectsByID:
                        object = session.machoObjectsByID[objectID][1]
                        (objectType, guts,) = self._ObjectCall__GetObjectTypeAndGuts(object)
                        session.UnregisterMachoObject(objectID, refID)

                return 
            else:
                if objectID[0] == 'C' and macho.mode == 'client':
                    (cid, oid,) = objectID.split(':')
                    objectID = '%s:%s' % (self.identifier, oid)
                if objectID not in session.machoObjectsByID:
                    raise UnMachoDestination('The specified object (%s) is not a member of this session' % objectID)
                object = session.machoObjectsByID[objectID][1]
                if isinstance(object, base.ObjectConnection):
                    objclass = object.GetObjectConnectionLogClass()
                else:
                    try:
                        try:
                            objclass = object.__logname__
                        except AttributeError:
                            try:
                                objclass = object.__guid__.split('.')
                                if len(objclass) > 1:
                                    objclass = objclass[1]
                                else:
                                    objclass = objclass[0]
                                try:
                                    setattr(object, '__logname__', objclass)
                                except StandardError:
                                    pass
                            except AttributeError:
                                objclass = object.__class__.__name__
                    except StandardError:
                        objclass = 'CrappyClass'
                    sys.exc_clear()
                callTimer = base.CallTimer('%s::%s (ObjectNotify\\Server)' % (objclass, method))
                try:
                    func = getattr(object, method)
                    if method in object.__dict__.get('__restrictedcalls__', {}) or method.startswith('_'):
                        raise RuntimeError('This call can only be the result of a hack attack', method)
                    if not isinstance(object, base.ObjectConnection) and len(tup) == 4 and 'machoVersion' in tup[3]:
                        if len(tup[3]) == 1:
                            tup = (tup[0], tup[1], tup[2])
                        else:
                            del tup[3]['machoVersion']
                    if len(tup) == 3:
                        ClockThisWithoutTheStars('Remote Object Notify::%s::%s' % (objclass, method), func, args)
                    else:
                        ClockThisWithoutTheStars('Remote Object Notify::%s::%s' % (objclass, method), func, args, tup[3])

                finally:
                    callTimer.Done()

                return 
        else:
            packet.payload = self.FromPickle(packet.payload[1], packet.source)
        self.ForwardNotifyUp(packet)



    def NotifyDown(self, packet):
        self._ObjectCall__StringifyPayloadForLogging(packet, packet.payload)
        packet.payload = (0, self.ToPickle(packet.payload))
        if self.added_objects:
            packet.oob['OID+'] = self.added_objects
        packet.compressedPart = self.compressedPart
        self.ForwardNotifyDown(packet)



    def __GetObjectTypeAndGuts(self, object):
        ob = object
        if isinstance(object, base.ObjectConnection):
            ob = object.__dict__['__object__']
            objclass = object.GetObjectConnectionLogClass()
        else:
            try:
                try:
                    objclass = object.__logname__
                except AttributeError:
                    try:
                        objclass = object.__guid__.split('.')
                        if len(objclass) > 1:
                            objclass = objclass[1]
                        else:
                            objclass = objclass[0]
                        try:
                            setattr(object, '__logname__', objclass)
                        except StandardError:
                            pass
                    except AttributeError:
                        objclass = object.__class__.__name__
            except StandardError:
                objclass = 'CrappyClass'
            sys.exc_clear()
        return (objclass, ob)



    def GetObjectID(self, object):
        if type(object) == types.InstanceType:
            if isinstance(object, stackless.tasklet):
                raise RuntimeError('Thou shall not send stackless.tasklet across the wire')
            if not getattr(object, '__passbyvalue__', 0):
                objectID = base.GetObjectUUID(object)
                if objectID in session.machoObjectsByID:
                    session.machoObjectsByID[objectID][0] = blue.os.GetWallclockTime()
                else:
                    (objectType, guts,) = self._ObjectCall__GetObjectTypeAndGuts(object)
                    session.LogSessionHistory('%s object %s added to session' % (objectType, objectID), strx(guts))
                    if objectType is None:
                        raise RuntimeError('NoneType object added by reference, undoubtedly ObjectConnection to None')
                if objectID not in self.added_objects:
                    refID = blue.os.GetWallclockTime()
                    self.added_objects[objectID] = refID
                    session.RegisterMachoObject(objectID, object, refID)
                else:
                    refID = self.added_objects[objectID]
                pa = {}
                for each in getattr(object, '__publicattributes__', []):
                    if hasattr(object, each):
                        pa[each] = getattr(object, each)

                if pa:
                    return blue.marshal.Save((objectID, pa, refID), self.GetObjectID)
                else:
                    return blue.marshal.Save((objectID, refID), self.GetObjectID)
            elif isinstance(object, util.CachedObject):
                sm.services['objectCaching'].CacheObject(object)
            elif isinstance(object, objectCaching.CachedObject):
                self.compressedPart += object.CompressedPart()
            elif isinstance(object, util.Moniker):
                object.QuickResolve()



    def ParseObjectID(self, objectID):
        if session is None:
            self.machoNet.LogError('Session is none during ParseObjectID!!!')
            log.LogTraceback()
        t = blue.marshal.Load(objectID, self.ParseObjectID)
        if len(t) == 2:
            (objectID, refID,) = t
            pa = {}
        else:
            (objectID, pa, refID,) = t
        if objectID not in session.machoObjectsByID:
            (nid, oid,) = objectID.split(':')
            if nid != self.identifier:
                if nid[0] == 'C':
                    if self.otherDudesAddress.addressType == const.ADDRESS_TYPE_CLIENT:
                        objectID = 'C=%d:%s' % (self.otherDudesAddress.clientID, oid)
                return MachoObjectConnection(session.GetActualSession(), self, objectID, pa, refID)
            raise RuntimeError('The specified object (%s) does not exist within this session (%s)' % (strx(objectID), strx(session)))
        return weakref.proxy(session.machoObjectsByID[objectID][1])



    def OnObjectPublicAttributesUpdated(self, uuid, pa, args, keywords):
        for sess in base.GetSessions():
            try:
                if sess.machoObjectConnectionsByObjectID.get(uuid, 0):
                    for conn in sess.machoObjectConnectionsByObjectID[uuid][1].itervalues():
                        k = keywords.get('partial', [])
                        if k:
                            old = {}
                            for each in k:
                                old[each] = conn.__publicattributes__[each]
                                conn.__publicattributes__[each] = pa[each]

                        else:
                            old = conn.__publicattributes__
                            conn.__publicattributes__ = pa
                        for each in conn.objectChangeHandlers.iterkeys():
                            try:
                                func = getattr(each, 'OnObjectChanged')
                            except StandardError:
                                log.LogException()
                                sys.exc_clear()
                                continue
                            theArgs = [conn, old, conn.__publicattributes__] + list(args)
                            uthread.worker('machoNet::OnObjectChanged', func, *theArgs, **keywords)


            except Exception:
                log.LogException('Exception during OnObjectPublicAttributesUpdated')
                sys.exc_clear()




    def ToPickle(self, value, nonblocking = 1):
        try:
            self.compressedPart = 0
            self.added_objects = {}
            ret = blue.marshal.Save(value, self.GetObjectID)
            if nonblocking and len(ret) > 5000000:
                ctk = GetLocalStorage().get('calltimer.key', None)
                if len(ret) > 8000000:
                    if ctk is not None:
                        self.machoNet.LogError('Unacceptably large response from ', ctk, ', ', len(ret), ' bytes')
                    else:
                        try:
                            self.machoNet.LogError('Unacceptably large response from unknown source, ', len(ret), ' bytes - ', value[:256])
                        except TypeError:
                            self.machoNet.LogError('Unacceptably large response from unknown source, ', len(ret), ' bytes - ', ret[:256])
                    log.LogTraceback()
                elif ctk is not None:
                    self.machoNet.LogWarn('Unacceptably large response from ', ctk, ', ', len(ret), ' bytes')
                else:
                    try:
                        self.machoNet.LogWarn('Unacceptably large response from unknown source, ', len(ret), ' bytes - ', value[:256])
                    except TypeError:
                        self.machoNet.LogWarn('Unacceptably large response from unknown source, ', len(ret), ' bytes - ', ret[:256])
            return ret
        except StandardError:
            self.machoNet.LogError("That was NOT a nice thing to do!  Keep yo' unpicklables to yourself.")
            log.LogTraceback()
            raise 



    def __StringifyPayloadForLogging(self, packet, payload):
        if self.machoNet.logChannel.IsOpen(1):
            packet.strayload = strx(payload)



    def FromPickle(self, thePickle, otherDudesAddress):
        try:
            self.otherDudesAddress = otherDudesAddress
            payload = blue.marshal.Load(thePickle, self.ParseObjectID)
        except StandardError:
            self.machoNet.LogError('Failed unpickling buffer of length %d' % len(thePickle))
            self.machoNet.LogError('First 100 bytes: %s' % strx(thePickle[:100]))
            log.LogTraceback()
            raise 
        return payload



    def ObjectCall(self, oob, persistantObjectID, blocking, sess, destination, objectID, method, *args, **keywords):
        return self.ObjectCallWithoutTheStars(oob, persistantObjectID, blocking, sess, destination, objectID, method, args, keywords)



    def ObjectCallWithoutTheStars(self, oob, persistantObjectID, blocking, sess, destination, objectID, method, args, keywords):
        (cachable, versionCheck, throwOK, cachedResultRecord, cacheKey, cacheDetails,) = sm.GetService('objectCaching').PerformCachedMethodCall(None, persistantObjectID, method, args)
        if cachable:
            if not versionCheck:
                if throwOK:
                    sm.GetService('objectCaching').LogInfo('Local cache hit with throw for remote object ', persistantObjectID, '::', method, '(', args, ')')
                    raise objectCaching.CacheOK()
                elif cachedResultRecord:
                    sm.GetService('objectCaching').LogInfo('Local cache hit for remote object ', persistantObjectID, '::', method, '(', args, ')')
                    return cachedResultRecord['lret']
        if keywords:
            kw2 = copy.copy(keywords)
        else:
            kw2 = {}
        if kw2.get('machoVersion', None) is None:
            if cachedResultRecord is not None and cachedResultRecord['version'] is not None:
                kw2['machoVersion'] = cachedResultRecord['version']
            else:
                kw2['machoVersion'] = 1
        if currentcall:
            machoTimeout = kw2.get('machoTimeout', currentcall.packet.oob.get('machoTimeout', None))
        else:
            machoTimeout = kw2.get('machoTimeout', None)
        if 'machoTimeout' in kw2:
            del kw2['machoTimeout']
        payload = (1, self.ToPickle((objectID,
          method,
          args,
          kw2)))
        if blocking == 1:
            packet = macho.CallReq(destination=destination, payload=payload)
            if oob:
                packet.oob = oob
            if machoTimeout is not None:
                packet.oob['machoTimeout'] = machoTimeout
            if self.added_objects:
                if 'OID+' in packet.oob:
                    packet.oob['OID+'].update(self.added_objects)
                else:
                    packet.oob['OID+'] = self.added_objects
            try:
                callTimer = base.CallTimer('Remote Object Call::%s (ObjectCall\\Client)' % (method,))
                try:
                    retval = self.ForwardCallDown(packet)

                finally:
                    callTimer.Done()

                retval = self.FromPickle(retval.payload, packet.destination)
            except objectCaching.CacheOK:
                if cachedResultRecord is None:
                    raise 
                sys.exc_clear()
                sm.GetService('objectCaching').LogInfo('Version matches for remote object ', persistantObjectID, '::', method, '(', args, ')')
                sm.GetService('objectCaching').UpdateVersionCheckPeriod(cacheKey)
                return cachedResultRecord['lret']
            if isinstance(retval, objectCaching.CachedMethodCallResult):
                sm.GetService('objectCaching').CacheMethodCall(persistantObjectID, method, args, retval)
                retval = retval.GetResult()
            return retval
        else:
            packet = macho.Notification(destination=destination, payload=payload)
            if oob:
                packet.oob = oob
            if machoTimeout is not None:
                packet.oob['machoTimeout'] = machoTimeout
            if self.added_objects:
                if 'OID+' in packet.oob:
                    packet.oob['OID+'].update(self.added_objects)
                else:
                    packet.oob['OID+'] = self.added_objects
            self.ForwardNotifyDown(packet)
            return MachoBoobyTrap()




class MachoBoobyTrap():
    __guid__ = 'gpcs.MachoBoobyTrap'

    def __str__(self):
        return 'MachoBoobyTrap'



    def __getattr__(self, attribute):
        try:
            log.LogTraceback()
        except StandardError:
            sys.exc_clear()
        raise RuntimeError("Attempted to access %s from a non-blocking call's result" % attribute)




class MachoObjectConnection():

    def __init__(self, sess, gpcs, objectID, pa, refID):
        try:
            self.__dict__['session'] = weakref.proxy(sess)
        except TypeError:
            self.__dict__['session'] = sess
            sys.exc_clear()
        self.__dict__['objectID'] = objectID
        self.__dict__['sessionCheck'] = None
        self.__dict__['persistantObjectID'] = objectID
        self.__dict__['gpcs'] = weakref.proxy(gpcs)
        self.__dict__['__publicattributes__'] = pa
        self.__dict__['objectChangeHandlers'] = weakref.WeakKeyDictionary({})
        mask = sess.Masquerade()
        try:
            self.__dict__['clisid'] = gpcs.machoNet.GetClientSessionID()

        finally:
            mask.UnMask()

        if objectID[0] == 'C':
            self.__dict__['blocking'] = 0
            (cid, oid,) = objectID.split(':')
            cid = cid.split('=')[1]
            self.__dict__['destination'] = macho.MachoAddress(clientID=long(cid))
        else:
            self.__dict__['blocking'] = 1
            (nid, oid,) = objectID.split(':')
            nid = nid.split('=')[1]
            self.__dict__['destination'] = macho.MachoAddress(nodeID=long(nid))
        self.__dict__['deleted'] = 0
        sess.RegisterMachoObjectConnection(objectID, self, refID)



    def SetSessionCheck(self, sessionCheck):
        self.sessionCheck = sessionCheck



    def PerformSessionCheck(self):
        if self.sessionCheck:
            if macho.mode == 'client' and not session.IsItSafe():
                import log
                log.LogTraceback("Client is using a session bound remote object while the session is mutating or changing.  If the caller isn't careful, this may be really bad....", severity=2)
            for (attribute, expected,) in self.sessionCheck.iteritems():
                if self.session:
                    current = getattr(self.session, attribute, None)
                else:
                    current = None
                if current != expected or not expected:
                    log.LogTraceback()
                    raise RuntimeError('RemoteObjectSessionCheckFailure', {'attribute': attribute,
                     'expected': expected,
                     'current': current,
                     'objectID': self.objectID,
                     'persistantObjectID': self.persistantObjectID})




    def __del__(self):
        if not self.deleted:
            self.deleted = 1
            releaseRefID = self.session.UnregisterMachoObjectConnection(self.objectID, self)
            if releaseRefID:
                try:
                    if self.objectID not in self.gpcs.releasedObjects:
                        self.gpcs.releasedObjects[self.objectID] = []
                    self.gpcs.releasedObjects[self.objectID].append((releaseRefID, self.session, self.destination))
                except ReferenceError:
                    pass



    def __str__(self):
        return '<RemoteObject:' + strx(self.__dict__['objectID']) + '>'



    def __nonzero__(self):
        return 1



    def __repr__(self):
        return '<RemoteObject:' + strx(self.__dict__['objectID']) + '>'



    def RegisterObjectChangeHandler(self, callback):
        self.objectChangeHandlers[callback] = None



    def UnRegisterObjectChangeHandler(self, callback):
        try:
            del self.objectChangeHandlers[callback]
        except ReferenceError as e:
            sys.exc_clear()
        except KeyError as e:
            sys.exc_clear()



    def __getattr__(self, attribute):
        if getattr(self, 'deleted', 0):
            raise AttributeError(attribute, 'This object is being deleted, so the attribute is no longer available')
        if not attribute[0].isupper():
            pa = self.__publicattributes__
            if not pa.has_key(attribute):
                raise AttributeError(attribute)
            return pa[attribute]
        self.PerformSessionCheck()
        return MachoObjectCallWrapper(self.__dict__['persistantObjectID'], self.__dict__['clisid'], self.__dict__['blocking'], self.__dict__['session'], self.__dict__['gpcs'], self.__dict__['destination'], self.__dict__['objectID'], attribute)




class MachoObjectCallWrapper():

    def __init__(self, persistantObjectID, clisid, blocking, sess, gpcs, destination, objectID, method):
        self.persistantObjectID = persistantObjectID
        self.clisid = clisid
        self.blocking = blocking
        self.session = sess
        self.gpcs = gpcs
        self.destination = destination
        self.objectID = objectID
        self.method = method



    def __call__(self, *args, **kwargs):
        mask = self.session.Masquerade()
        try:
            if self.gpcs.machoNet.GetClientSessionID() != self.clisid:
                raise RuntimeError('This object was acquired by a different session')
            if boot.role == 'client':
                if kwargs.get('noCallThrottling', None) is None:
                    key = (self.objectID,
                     self.method,
                     str(args),
                     str(kwargs))
                    return macho.ThrottledCall(key, self.gpcs.ObjectCallWithoutTheStars, {}, self.persistantObjectID, self.blocking, self.session, self.destination, self.objectID, self.method, args, kwargs)
                del kwargs['noCallThrottling']
            return self.gpcs.ObjectCallWithoutTheStars({}, self.persistantObjectID, self.blocking, self.session, self.destination, self.objectID, self.method, args, kwargs)

        finally:
            mask.UnMask()
            self.__dict__.clear()





