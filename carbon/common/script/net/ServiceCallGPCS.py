import weakref
import blue
import base
import copy
import objectCaching
import uthread
import log
import macho
import util
import sys
import random
import const
from timerstuff import ClockThisWithoutTheStars
from service import ROLE_PLAYER
from collections import defaultdict

class CoreServiceCall():
    __guid__ = 'gpcs.CoreServiceCall'
    __notifyevents__ = ['OnUpdateServiceMapping']
    __recvServiceCallCount__ = defaultdict(lambda : 0)
    __sendServiceCallCount__ = defaultdict(lambda : 0)
    __recvServiceCallSourceCount__ = defaultdict(lambda : defaultdict(lambda : 0))
    __sendNotifyCount__ = defaultdict(lambda : 0)

    def __init__(self):
        self.services = {}
        sm.RegisterNotify(self)



    def UpdateRecvServiceCallStats(self, service, method, source):
        key = str(service) + '.' + str(method)
        if source.addressType == const.ADDRESS_TYPE_NODE:
            sourceId = source.nodeID
        elif source.addressType == const.ADDRESS_TYPE_CLIENT:
            sourceId = 'Client'
        else:
            sourceId = 'Unknown'
        CoreServiceCall.__recvServiceCallCount__[key] += 1
        CoreServiceCall.__recvServiceCallSourceCount__[key][sourceId] += 1



    def UpdateSendNotifyStats(self, method):
        CoreServiceCall.__sendNotifyCount__[method] += 1



    def UpdateSendServiceCallStats(self, service, method):
        key = str(service) + '.' + str(method)
        CoreServiceCall.__sendServiceCallCount__[key] += 1



    def OnUpdateServiceMapping(self, svc, nodeID):
        self.services[svc] = nodeID



    def ResetAutoResolveCache(self):
        self.services.clear()



    def CallUp(self, packet):
        if packet.payload[0]:
            if getattr(packet.destination, 'service', None) is not None:
                if packet.payload[1] in packet.service.__dict__.get('__restrictedcalls__', {}) or packet.payload[1].startswith('_'):
                    raise RuntimeError('This call can only be the result of a hack attack', packet.payload[1])
                try:
                    lock = None
                    boundObject = None
                    if packet.payload[1] == 'MachoBindObject':
                        args = packet.payload[2][:-1]
                        nodeID = packet.service.MachoResolveObject(args[0], 0)
                        if nodeID and nodeID != self.machoNet.GetNodeID():
                            self.machoNet.LogError('MachoBindObject received on wrong node.  Should have gone to ', nodeID, ', bindParams=', args[0], ', packet=', packet)
                            raise WrongMachoNode(nodeID)
                        call = packet.payload[2][-1]
                        lock = packet.service.Lock(packet.payload[2][0])
                        object = packet.service.GetCachedObject(packet.payload[2][0])
                        if object:
                            boundObject = ClockThisWithoutTheStars('Remote Service Call::MachoBindObject::ConnectToObject::%s' % packet.destination.service, session.ConnectToObject, (object, packet.destination.service, packet.payload[2][0]))
                    else:
                        args = packet.payload[2]
                    if boundObject is None:
                        method = getattr(packet.service, packet.payload[1])
                        callTimer = base.CallTimer('%s::%s (ServiceCall\\Server)' % (packet.destination.service, packet.payload[1]))
                        try:
                            self.UpdateRecvServiceCallStats(packet.destination.service, method.__method__, packet.source)
                            if len(packet.payload) == 3:
                                payload = ClockThisWithoutTheStars('Remote Service Call::%s::%s' % (packet.destination.service, packet.payload[1]), method, args)
                            else:
                                payload = ClockThisWithoutTheStars('Remote Service Call::%s::%s' % (packet.destination.service, packet.payload[1]), method, args, packet.payload[3])

                        finally:
                            callTimer.Done()

                        if packet.payload[1] == 'MachoBindObject':
                            packet.service.SetCachedObject(packet.payload[2][0], payload)
                            if session.role & ROLE_PLAYER:
                                packet.service.UnLock(packet.payload[2][0], lock)
                                lock = None
                            boundObject = ClockThisWithoutTheStars('Remote Service Call::MachoBindObject::ConnectToObject::%s' % packet.destination.service, session.ConnectToObject, (payload, packet.destination.service, packet.payload[2][0]))

                finally:
                    if packet.payload[1] == 'MachoBindObject':
                        if lock is not None:
                            packet.service.UnLock(packet.payload[2][0], lock)
                    elif lock is not None:
                        raise RuntimeError('The service lock should only be used in MachoBindObject calls')

                if boundObject is not None:
                    if call is not None:
                        if isinstance(boundObject, base.ObjectConnection):
                            objclass = boundObject.GetObjectConnectionLogClass()
                        else:
                            try:
                                try:
                                    objclass = boundObject.__logname__
                                except AttributeError:
                                    try:
                                        objclass = boundObject.__guid__.split('.')
                                        if len(objclass) > 1:
                                            objclass = objclass[1]
                                        else:
                                            objclass = objclass[0]
                                        try:
                                            setattr(boundObject, '__logname__', objclass)
                                        except StandardError:
                                            pass
                                    except AttributeError:
                                        objclass = boundObject.__class__.__name__
                            except StandardError:
                                objclass = 'CrappyClass'
                            sys.exc_clear()
                        (method, args, keywords,) = call
                        if method in boundObject.__dict__.get('__restrictedcalls__', {}) or method.startswith('_'):
                            raise RuntimeError('This call can only be the result of a hack attack', method)
                        callTimer = base.CallTimer('%s::%s (UnBoundObjectCall\\Server)' % (objclass, method))
                        try:
                            func = getattr(boundObject, method)
                            self.UpdateRecvServiceCallStats(objclass, method, packet.source)
                            if not keywords:
                                retval = ClockThisWithoutTheStars('Remote Unbound Object Call::%s::%s' % (objclass, method), func, args)
                            else:
                                retval = ClockThisWithoutTheStars('Remote Unbound Object Call::%s::%s' % (objclass, method), func, args, keywords)
                            payload = (boundObject, retval)

                        finally:
                            callTimer.Done()

                    else:
                        payload = (boundObject, None)
                return packet.Response(payload=payload)
        else:
            packet.payload = packet.payload[1]
        return self.ForwardCallUp(packet)



    def CallDown(self, packet):
        packet.payload = (0, packet.payload)
        return self.ForwardCallDown(packet)



    def NotifyUp(self, packet):
        if packet.payload[0]:
            if getattr(packet.destination, 'service', None) is not None:
                method = getattr(packet.service, packet.payload[1])
                callTimer = base.CallTimer('%s::%s (ServiceNotify\\Server)' % (packet.destination.service, packet.payload[1]))
                try:
                    if len(packet.payload) == 3:
                        ClockThisWithoutTheStars('Remote Service Notify::%s::%s' % (packet.destination.service, packet.payload[1]), method, packet.payload[2])
                    else:
                        ClockThisWithoutTheStars('Remote Service Notify::%s::%s' % (packet.destination.service, packet.payload[1]), method, packet.payload[2], packet.payload[3])

                finally:
                    callTimer.Done()

                return 
        else:
            packet.payload = packet.payload[1]
        return self.ForwardNotifyUp(packet)



    def NotifyDown(self, packet):
        if packet.destination.broadcastID:
            self.UpdateSendNotifyStats(packet.destination.broadcastID)
        packet.payload = (0, packet.payload)
        return self.ForwardNotifyDown(packet)



    def RemoteServiceCall(self, sess, nodeID, service, method, *args, **keywords):
        return self.RemoteServiceCallWithoutTheStars(sess, nodeID, service, method, args, keywords)



    def RemoteServiceCallWithoutTheStars(self, sess, nodeID, service, method, args, keywords):
        while 1:
            try:
                if sess is None:
                    self.machoNet.LogError('Session is None during RemoteServiceCall')
                    log.LogTraceback()
                sessionVars1 = self._GetRemoteServiceCallVariables(sess)
                mask = sess.Masquerade()
                try:
                    (cachable, versionCheck, throwOK, cachedResultRecord, cacheKey, cacheDetails,) = sm.GetService('objectCaching').PerformCachedMethodCall(None, service, method, args)
                    if cachable:
                        if not versionCheck:
                            if throwOK:
                                self.LogMethodCall(objectCaching.CacheOK(), service, method + '[Cached]', args, keywords)
                                raise objectCaching.CacheOK()
                            elif cachedResultRecord:
                                self.LogMethodCall(cachedResultRecord['lret'], service, method + '[Cached]', args, keywords)
                                return cachedResultRecord['lret']
                    if nodeID is None and macho.mode == 'client':
                        nodeID = self.services.get(service, None)
                        if nodeID is None and service in self.machoNet.serviceInfo:
                            where = self.machoNet.serviceInfo[service]
                            if where:
                                for (k, v,) in self.machoNet.serviceInfo.iteritems():
                                    if k != service and v and (v.startswith(where) or where.startswith(v)):
                                        nodeID = self.services.get(k, None)
                                        break

                        if nodeID is None and self.services and service not in ('DB2',):
                            self.machoNet.LogWarn("I haven't got a clue where ", service, ' should run, although I could guess any of these: ', str(self.services.keys()))
                    if nodeID is None:
                        if macho.mode == 'server':
                            proxies = self.machoNet.GetConnectedProxyNodes()
                            if not proxies:
                                raise UnMachoDestination('No proxy available')
                            destination = macho.MachoAddress(nodeID=random.choice(proxies), service=service)
                        else:
                            destination = macho.MachoAddress(service=service)
                    elif isinstance(nodeID, macho.MachoAddress):
                        destination = nodeID
                    else:
                        destination = macho.MachoAddress(nodeID=nodeID, service=service)
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
                    payload = (1,
                     method,
                     args,
                     kw2)
                    packet = macho.CallReq(destination=destination, payload=payload)
                    if machoTimeout is not None:
                        packet.oob['machoTimeout'] = machoTimeout
                    callTimer = base.CallTimer('%s::%s (ServiceCall\\Client)' % (service, method))
                    try:
                        try:
                            ret = self.ForwardCallDown(packet).payload
                            self.UpdateSendServiceCallStats(service, method)
                            self.LogMethodCall(ret, service, method, args, keywords)
                        except util.UpdateMoniker as e:
                            raise 
                        except RuntimeError:
                            raise 
                        except UserError:
                            raise 
                        except ProxyRedirect:
                            raise 
                        except WrongMachoNode:
                            raise 
                        except objectCaching.CacheOK:
                            if cachedResultRecord is None:
                                raise 
                            sys.exc_clear()
                            self.LogMethodCall(cachedResultRecord['lret'], service, method, args, keywords)
                            sm.GetService('objectCaching').UpdateVersionCheckPeriod(cacheKey)
                            return cachedResultRecord['lret']

                    finally:
                        callTimer.Done()

                    if isinstance(ret, objectCaching.CachedMethodCallResult):
                        sm.GetService('objectCaching').CacheMethodCall(service, method, args, ret)
                        ret = ret.GetResult()
                    return ret

                finally:
                    mask.UnMask()
                    sessionVars2 = self._GetRemoteServiceCallVariables(sess)

            except WrongMachoNode as e:
                sys.exc_clear()
                self._HandleServiceCallWrongNode(e, service, sessionVars1, sessionVars2)
                self.services[service] = e.payload
                if nodeID == e.payload:
                    self.machoNet.LogError('Redirected to same node', nodeID)
                    raise UnMachoDestination('Failed to redirect call, because we were being redirected to the same place we were trying to call in the first place (%s)' % nodeID)
                else:
                    self.machoNet.LogInfo('Redirecting call to node ', e.payload, ' that was originally intended for node ', nodeID)
                nodeID = e.payload
            except UserError as e:
                if e.msg in ('UnMachoDestination', 'GPSTransportClosed'):
                    self.services.clear()
                raise 
            except StandardError:
                if service in self.services:
                    otherNodeID = self.services[service]
                    for (s, n,) in self.services.items()[:]:
                        if n and n in (otherNodeID, nodeID):
                            del self.services[s]

                raise 




    def _GetRemoteServiceCallVariables(self, session):
        return ()



    def _HandleServiceCallWrongNode(self, e, service, sessionVars1, sessionVars2):
        pass



    def RemoteServiceNotify(self, sess, nodeID, service, method, *args, **keywords):
        return self.RemoteServiceNotifyWithoutTheStars(sess, nodeID, service, method, args, keywords)



    def RemoteServiceNotifyWithoutTheStars(self, sess, nodeID, service, method, args, keywords):
        while 1:
            try:
                if sess is None:
                    self.machoNet.LogError('Session is None during RemoteServiceNotify')
                    log.LogTraceback()
                if nodeID is None and macho.mode == 'client':
                    nodeID = self.services.get(service, None)
                    if nodeID is None and service in self.machoNet.serviceInfo:
                        where = self.machoNet.serviceInfo[service]
                        for (k, v,) in self.machoNet.serviceInfo.iteritems():
                            if k != service and v == where:
                                nodeID = self.services.get(k, None)
                                break

                    if nodeID is None and self.machoNet.serviceInfo.get(service, None) is not None:
                        self.machoNet.LogWarn("I haven't got a clue where ", service, ' should run, although I could guess any of these: ', str(self.services.keys()))
                if nodeID is None:
                    if macho.mode == 'server':
                        proxies = self.machoNet.GetConnectedProxyNodes()
                        if not proxies:
                            raise UnMachoDestination('No proxy available')
                        destination = macho.MachoAddress(nodeID=random.choice(proxies), service=service)
                    else:
                        destination = macho.MachoAddress(service=service)
                elif isinstance(nodeID, macho.MachoAddress):
                    destination = nodeID
                else:
                    destination = macho.MachoAddress(nodeID=nodeID, service=service)
                if keywords:
                    kw2 = copy.copy(keywords)
                else:
                    kw2 = {}
                if currentcall:
                    machoTimeout = kw2.get('machoTimeout', currentcall.packet.oob.get('machoTimeout', None))
                else:
                    machoTimeout = kw2.get('machoTimeout', None)
                if 'machoTimeout' in kw2:
                    del kw2['machoTimeout']
                if kw2:
                    payload = (1,
                     method,
                     args,
                     kw2)
                else:
                    payload = (1, method, args)
                packet = macho.Notification(destination=destination, payload=payload)
                if machoTimeout is not None:
                    packet.oob['machoTimeout'] = machoTimeout
                mask = sess.Masquerade()
                try:
                    callTimer = base.CallTimer('%s::%s (ServiceNotify\\Client)' % (service, method))
                    try:
                        self.ForwardNotifyDown(packet)

                    finally:
                        callTimer.Done()


                finally:
                    mask.UnMask()

            except WrongMachoNode as e:
                sys.exc_clear()
                self.services[service] = e.payload
                if nodeID == e.payload:
                    self.machoNet.LogError('Redirected to same node', nodeID)
                    raise UnMachoDestination('Failed to redirect call, because we were being redirected to the same place we were trying to call in the first place (%s)' % nodeID)
                else:
                    self.machoNet.LogInfo('Redirecting call to node ', e.payload, ' that was originally intended for node ', nodeID)
                    nodeID = e.payload
                continue
            except UserError as e:
                if e.msg in ('UnMachoDestination', 'GPSTransportClosed'):
                    self.services.clear()
                raise 
            except StandardError:
                self.services.clear()
                raise 
            return 




    def LogMethodCall(self, result, logname, method, args, keywords):
        logChannel = log.methodcalls
        if logChannel.IsOpen(log.LGINFO):
            if isinstance(result, Exception):
                eorr = ', EXCEPTION='
            else:
                eorr = ', retval='
            if keywords:
                logwhat = [logname,
                 '::',
                 method,
                 ' args=',
                 args,
                 ', keywords={',
                 keywords,
                 '}',
                 eorr,
                 result]
            else:
                logwhat = [logname,
                 '::',
                 method,
                 ' args=',
                 args,
                 eorr,
                 result]
            timer = PushMark(logname + '::LogPseudoMethodCall')
            try:
                s = 'failed to convert'
                for getter in [str, unicode, repr]:
                    try:
                        s = ''.join(map(getter, logwhat))
                        break
                    except:
                        sys.exc_clear()

                if len(s) > 2500:
                    s = s[:2500]
                logChannel.Log(s, log.LGINFO, 1)

            finally:
                PopMark(timer)




    def ConnectToRemoteService(self, servicename, nodeID = None, sess = None):
        if sess is None:
            sess = session.GetActualSession()
        return MachoServiceConnection(self, sess, servicename, nodeID)



    def UberMachoRemoteServiceCall(self, nodeGroup, batchInterval, sess, service, method, *args, **keywords):
        if batchInterval:
            queue = sess.GetSessionVariable(('batchedCallQueue', batchInterval), ({}, {}))
            if not queue[0]:
                uthread.worker('GPCS::BroadcastStuff::BatchedUberMachoRemoteServiceCall', self._CoreServiceCall__BatchedUberMachoRemoteServiceCall, nodeGroup, sess, batchInterval)
            i = len(queue[0])
            queue[0][i] = (service,
             method,
             args,
             keywords)
            queue[1][i] = uthread.Channel()
            return queue[1][i].receive()
        else:
            return self._CoreServiceCall__UberMachoRemoteServiceCall(sess, service, method, self._CoreServiceCall__GetNodeGroup(nodeGroup), *args, **keywords)



    def __GetNodeGroup(self, nodeGroup):
        if nodeGroup == 0:
            if macho.mode == 'proxy':
                return self.machoNet.GetConnectedSolNodes()
            else:
                return self.machoNet.GetConnectedProxyNodes()
        elif nodeGroup == 1:
            if macho.mode == 'proxy':
                return self.machoNet.GetConnectedProxyNodes() + [self.machoNet.GetNodeID()]
            else:
                return self.machoNet.GetConnectedSolNodes() + [self.machoNet.GetNodeID()]
        else:
            return self.machoNet.GetConnectedNodes() + [self.machoNet.GetNodeID()]



    def __BatchedUberMachoRemoteServiceCall(self, nodeGroup, sess, batchInterval):
        blue.pyos.synchro.SleepWallclock(batchInterval / const.MSEC)
        queue = sess.GetSessionVariable(('batchedCallQueue', batchInterval))
        sess.SetSessionVariable(('batchedCallQueue', batchInterval), ({}, {}))
        scatteredRetvals = self._CoreServiceCall__UberMachoRemoteServiceCall(sess, 'sessionMgr', 'BatchedRemoteCall', self._CoreServiceCall__GetNodeGroup(nodeGroup), queue[0])
        gatheredRetvals = {}
        for (isexception, nodeID, retval,) in scatteredRetvals:
            if isexception:
                for callID in queue[0].iterkeys():
                    if callID not in gatheredRetvals:
                        gatheredRetvals[callID] = []
                    gatheredRetvals[callID].append((isexception, nodeID, retval))

            else:
                for (isexception2, callID, retval2,) in retval:
                    if callID not in gatheredRetvals:
                        gatheredRetvals[callID] = []
                    gatheredRetvals[callID].append((isexception2, nodeID, retval2))


        for (callID, channel,) in queue[1].iteritems():
            channel.send(gatheredRetvals[callID])




    def __UberMachoRemoteServiceCall(self, sess, service, method, nodes, *args, **keywords):
        retvals = []
        dude = UberDude(len(nodes), service, method)
        if not len(nodes):
            raise UnMachoDestination('No target nodes available for UberMachoRemoteServiceCall')
        uberMachoRaise = keywords.get('uberMachoRaise', False)
        if 'uberMachoRaise' in keywords:
            keywords = copy.copy(keywords)
            del keywords['uberMachoRaise']
        if 'machoTimeout' in keywords:
            keywords = copy.copy(keywords)
        else:
            keywords['machoTimeout'] = 60
        machoTimeout = keywords.get('machoTimeout', 60)
        for each in nodes:
            uthread.worker(blue.pyos.taskletTimer.GetCurrent() + '::RPC', UnterMachoRemoteServiceCall, self, dude, retvals, sess, each, service, method, args, keywords)

        if dude.Await(machoTimeout) == 2:
            log.LogTraceback('Local Timeout')
            n = copy.copy(nodes)
            for r in retvals:
                n.remove(r[1])

            for nodeID in n:
                self.machoNet.LogError('Node ', nodeID, " has not completed it's uber-macho call")
                retvals.append((1, nodeID, RuntimeError('Local Timeout')))

        if uberMachoRaise:
            for (isexception, nodeID, ret,) in retvals:
                if isexception:
                    raise UberMachoException(retvals)

        return retvals



    def ConnectToAllNeighboringServices(self, servicename, sess, batchInterval):
        return UberMachoServiceConnection(self, sess, servicename, 0, batchInterval)



    def ConnectToAllSiblingServices(self, servicename, sess, batchInterval):
        return UberMachoServiceConnection(self, sess, servicename, 1, batchInterval)



    def ConnectToAllServices(self, servicename, sess, batchInterval):
        return UberMachoServiceConnection(self, sess, servicename, 2, batchInterval)




class UberDude():

    def __init__(self, ubercount, service, method):
        self.ubercount = ubercount
        if ubercount:
            self.channel = uthread.Channel(('UberMachoRemoteServiceCall', service + '::' + method))
        else:
            self.channel = None
        self.tasklet = None



    def Done(self):
        self.ubercount -= 1
        if self.ubercount <= 0:
            if self.channel is not None and self.channel.queue:
                self.channel.send(1)
            self.channel = None
            if self.tasklet:
                self.tasklet.kill()
                self.tasklet = None



    def Await(self, timeoutInterval):
        self.tasklet = uthread.new(self._UberDude__Timeout, timeoutInterval)
        if self.channel:
            return self.channel.receive()
        return 0



    def __Timeout(self, timeoutInterval):
        try:
            blue.pyos.synchro.SleepWallclock(1000L * timeoutInterval)
            self.tasklet = None
            if self.channel:
                self.ubercount = 0
                self.channel.send(2)
        except TaskletExit:
            pass




def UnterMachoRemoteServiceCall(self, dude, retvals, sess, nodeID, service, method, args, keywords):
    try:
        try:
            if nodeID == sm.services['machoNet'].GetNodeID():
                if 'machoTimeout' in keywords:
                    keywords = copy.copy(keywords)
                    del keywords['machoTimeout']
                retvals.append((0, nodeID, apply(getattr(sess.ConnectToService(service), method), args, keywords)))
            else:
                retvals.append((0, nodeID, self.RemoteServiceCallWithoutTheStars(sess, nodeID, service, method, args, keywords)))
        except StandardError as e:
            log.LogException()
            retvals.append((1, nodeID, e))
            sys.exc_clear()
        except Exception as e:
            log.LogTraceback()
            retvals.append((1, nodeID, e))
            raise 

    finally:
        dude.Done()




class UberMachoServiceConnection():

    def __init__(self, gpcs, sess, servicename, nodeGroup, batchInterval):
        try:
            self.__dict__['session'] = weakref.proxy(sess)
        except StandardError:
            self.__dict__['session'] = sess
            sys.exc_clear()
        self.__dict__['servicename'] = servicename
        self.__dict__['gpcs'] = weakref.proxy(gpcs)
        self.__dict__['nodeGroup'] = nodeGroup
        self.__dict__['batchInterval'] = batchInterval



    def __str__(self):
        return '<UberMachoRemoteService:' + strx(self.__dict__['servicename']) + '>'



    def __nonzero__(self):
        return 1



    def __repr__(self):
        return str(self)



    def __getattr__(self, attribute):
        if self.__dict__.has_key(attribute):
            return self.__dict__[attribute]
        if attribute[:2] == '__':
            raise AttributeError(attribute)
        return UberMachoServiceCallWrapper(self.__dict__['gpcs'], self.__dict__['session'], self.__dict__['servicename'], attribute, self.__dict__['nodeGroup'], self.__dict__['batchInterval'])




class UberMachoServiceCallWrapper():

    def __init__(self, gpcs, sess, service, method, nodeGroup, batchInterval):
        self.session = sess
        self.gpcs = gpcs
        self.service = service
        self.method = method
        self.nodeGroup = nodeGroup
        self.batchInterval = batchInterval



    def __call__(self, *args, **keywords):
        mask = self.session.Masquerade()
        try:
            callTimer = base.CallTimer('%s::%s (UberMachoRemoteServiceCall)' % (self.service, self.method))
            try:
                return self.gpcs.UberMachoRemoteServiceCall(self.nodeGroup, self.batchInterval, self.session, self.service, self.method, *args, **keywords)

            finally:
                callTimer.Done()


        finally:
            mask.UnMask()
            self.__dict__.clear()





class MachoServiceConnection():
    blocking = True

    def __init__(self, gpcs, sess, servicename, nodeID = None):
        try:
            self.session = weakref.proxy(sess)
        except TypeError:
            self.session = sess
        self.servicename = servicename
        try:
            self.gpcs = weakref.proxy(gpcs)
        except TypeError:
            self.gpcs = gpcs
        self.nodeID = nodeID



    def __repr__(self):
        return '<RemoteService: %s>' % self.servicename



    def __getattr__(self, attribute):
        if attribute.startswith('__'):
            raise AttributeError(attribute)
        if attribute == 'NoBlock':
            noBlock = MachoServiceConnection(self.gpcs, self.session, self.servicename, self.nodeID)
            noBlock.blocking = False
            return noBlock

        def callable(*args, **kwargs):
            if self.blocking:
                call = self.gpcs.RemoteServiceCallWithoutTheStars
            else:
                call = self.gpcs.RemoteServiceNotifyWithoutTheStars

            def doCall():
                method = attribute
                mask = self.session.Masquerade()
                try:
                    callTimer = base.CallTimer('%s::%s (RemoteServiceCall)' % (self.service, method))
                    try:
                        return call(self.session, self.nodeID, self.servicename, method, args, kwargs)

                    finally:
                        callTimer.Done()


                finally:
                    mask.UnMask()



            if boot.role == 'client':
                if kwargs.get('noCallThrottling', None) is None:
                    key = (self.servicename,
                     attribute,
                     str(args),
                     str(kwargs))
                    return macho.ThrottledCall(key, doCall)
                del kwargs['noCallThrottling']
            return doCall()


        return callable




