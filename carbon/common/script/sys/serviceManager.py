from __future__ import with_statement
import bluepy
import uthread
import service
import blue
import base
import stackless
import types
import weakref
import log
import sys
import time
import collections
import util
import const
import svc
import os
from timerstuff import ClockThis, ClockThisWithoutTheStars

class ServiceNotFound(StandardError):
    __guid__ = 'exceptions.ServiceNotFound'
    __persistvars__ = ['serviceName']

    def __init__(self, serviceName = None):
        self.serviceName = serviceName
        self.args = [serviceName]



    def __repr__(self):
        return 'The service ' + unicode(self.serviceName) + ' was not found.'




class MethodNotCalledFromClient(StandardError):
    __guid__ = 'exception.MethodNotCalledFromClient'
    __persistvars__ = ['methodName']

    def __init__(self, methodName = None):
        self.methodName = methodName
        self.args = [methodName]



    def __repr__(self):
        return 'The method ' + unicode(self.methodName) + ' can be called from the client only.'



import __builtin__
__builtin__.ServiceNotFound = ServiceNotFound
__builtin__.MethodNotCalledFromClient = MethodNotCalledFromClient

class ServiceManager(log.LogMixin):
    __guid__ = 'service.ServiceManager'

    def __init__(self, startInline = []):
        log.LogMixin.__init__(self, 'svc.ServiceManager')
        self.state = service.SERVICE_START_PENDING
        self.services = {}
        self.dependants = {}
        self.notify = {}
        self.notifyObs = {}
        self.startInline = startInline
        self.blockedServices = []
        import __builtin__
        if hasattr(__builtin__, 'sm'):
            log.Quit('Multiple instances of ServiceManager are not allowed in a process')
        __builtin__.sm = self



    def Run(self, servicesToRun, servicesToBlock = []):
        self.run = 1
        if self.state not in (service.SERVICE_START_PENDING, service.SERVICE_RUNNING):
            if self.state == service.SERVICE_STOPPED:
                self.state = service.SERVICE_START_PENDING
            else:
                raise RuntimeError, "can't run a service when state is " + repr(self.state)
        blue.pyos.AddExitProc(self.Stop)
        for block in servicesToBlock:
            if block not in self.blockedServices:
                self.blockedServices.append(block)

        if len(servicesToRun):
            print 'Starting services'
            was = blue.pyos.taskletTimer.timesliceWarning
            try:
                blue.pyos.taskletTimer.timesliceWarning = 5000
                for each in servicesToRun:
                    self.StartService(each)

                for each in sm.services.keys():
                    counter = 0
                    while sm.services[each].state == service.SERVICE_START_PENDING:
                        counter += 1
                        if counter % 100 == 0:
                            print "Service start still pending: '%s', sleeping..." % sm.services[each].__guid__
                        blue.pyos.synchro.Sleep(100)


                for each in sm.services.keys():
                    if hasattr(sm.services[each], 'PostRun'):
                        sm.services[each].PostRun()


            finally:
                blue.pyos.taskletTimer.timesliceWarning = was

            print 'Starting services - Done'
        self.state = service.SERVICE_RUNNING



    def DumpBlueInfo(self):
        if getattr(self, 'blueInfoDumped', False):
            return 
        self.blueInfoDumped = True
        dumpPath = prefs.GetValue('blueDumpPath', None)
        if dumpPath is None:
            log.general.Log('Will not dump blue info since it is not configured in prefs (blueDumpPath)', log.LGINFO)
            return 
        if 'machoNet' not in self.services or not hasattr(self.services['machoNet'], 'nodeID'):
            log.general.Log('Will not dump blue info since machoNet is not available to give me a nodeID', log.LGINFO)
            return 
        try:
            computerName = blue.pyos.GetEnv().get('COMPUTERNAME', 'unknown')
            nodeID = self.services['machoNet'].nodeID
            if nodeID is None:
                nodeID = boot.role
            data = bluepy.GetBlueInfo(isYield=False)
            txt = 'Timestamp\tProcess CPU\tThread CPU\tTotal Memory\tBlue Memory\tPython Memory\tLateness\n'
            for i in xrange(len(data.timeData)):
                txt += '%s\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\n' % (util.FmtDate(data.timeData[i]),
                 data.procCpuData[i],
                 data.threadCpuData[i],
                 data.memData[i],
                 data.bluememData[i],
                 data.pymemData[i],
                 data.latenessData[i])

            if not os.path.exists(dumpPath):
                os.mkdir(dumpPath)
            fileName = 'Blue %s %s %s.txt' % (computerName, nodeID, util.FmtDate(blue.os.GetTime()))
            fileName = os.path.join(dumpPath, fileName.replace(':', '.').replace(' ', '.'))
            f = open(fileName, 'w')
            f.write(txt)
            f.close()
            log.general.Log('Finished dumping out %s entries from blue info into %s' % (len(data.timeData), fileName), log.LGNOTICE)
        except Exception:
            log.LogException('Error in dumping out blue info')
            sys.exc_clear()



    def Stop(self):
        self.DumpBlueInfo()
        self.logChannel.Log('ServiceManager.Stop(), stopping services')
        dag = util.DAG()
        for (k, v,) in self.services.iteritems():
            depends = v.__dependencies__ + getattr(v, '__exitdependencies__', [])
            for d in depends:
                if type(d) is not str:
                    d = d[0]
                if d in self.services:
                    dag.InsertEdge(k, d)


        dag.Invert()
        self.logChannel.Log('== BEGIN SERVICE LIST ==')
        order = []
        while dag.graph:
            leaves = dag.Leaves()
            if not leaves:
                break
            order.extend(leaves)
            for l in leaves:
                dag.RemoveNode(l)

            self.logChannel.Log('==leaves==')
            self.logChannel.Log(','.join(leaves))

        if dag.graph:
            leaves = dag.graph.keys()
            order.extend(leaves)
            self.logChannel.Log('==nonleaves==')
            self.logChannel.Log(','.join(leaves))
        self.logChannel.Log('== ENDOF SERVICE LIST ==')
        self.run = 0
        import blue
        old_block_trap = stackless.getcurrent().block_trap
        stackless.getcurrent().block_trap = 1
        self.state = service.SERVICE_STOP_PENDING
        try:
            for (k, v,) in ((each, self.services[each]) for each in order):
                if not hasattr(v, 'state'):
                    self.logChannel.Log("ServiceManager.Stop(), service '" + str(k) + " doesn't have state therefore has already stopped")
                elif v.state not in (service.SERVICE_STOPPED, service.SERVICE_STOP_PENDING):
                    self.logChannel.Log("ServiceManager.Stop(), stopping service '" + str(k) + "'")
                    try:
                        try:
                            v.state = service.SERVICE_STOP_PENDING
                            for notify in v.__notifyevents__:
                                self.notify[notify].remove(v)

                            v.Stop(blue.MemStream())
                        except StandardError:
                            log.LogException()
                            sys.exc_clear()

                    finally:
                        v.state = service.SERVICE_STOPPED

                else:
                    self.logChannel.Log("ServiceManager.Stop(), service '" + str(k) + "' is already stopping")


        finally:
            stackless.getcurrent().block_trap = old_block_trap
            self.state = service.SERVICE_STOPPED

        for v in self.services.itervalues():
            for a in v.__dict__.keys():
                if a not in ('logChannel', 'logContexts', 'state'):
                    delattr(v, a)


        self.logChannel.Log('ServiceManager.Stop(), services stopped.')



    def ParseServiceClass(self, serviceName):
        return 'svc.' + serviceName



    def Reload(self, serviceList):
        import blue
        if len(serviceList):
            print 'Reloading services'
        for each in serviceList:
            if each not in self.services or each in self.services and getattr(self.services[each], '__update_on_reload__', True):
                continue
            ms = blue.MemStream()
            try:
                try:
                    self.StopService(each, 0, ms)

                finally:
                    if self.services.has_key(each):
                        del self.services[each]

                self.GetService(each, ms)
            except Exception:
                log.LogException("Trying to reload service '%s" % each)
                sys.exc_clear()

        if len(serviceList):
            print 'Reloading services - Done'



    def StartServiceAndWaitForRunningState(self, serviceName, ms = None):
        srv = self.StartService(serviceName, ms=None)
        desiredStates = (service.SERVICE_RUNNING,)
        errorStates = (service.SERVICE_FAILED, service.SERVICE_STOPPED)
        self.WaitForServiceObjectState(srv, desiredStates, errorStates)
        return srv



    def WaitForServiceObjectState(self, svc, desiredStates, errorStates = service.SERVICE_FAILED):
        i = 0
        while svc.state not in desiredStates:
            if svc.state in errorStates:
                svc.LogError('Service ', svc.__logname__, ' got in an unexpected state', 'raising error')
                if svc.__error__:
                    raise svc.__error__[1], None, svc.__error__[2]
                else:
                    raise RuntimeError, 'Service %s made unexpected state transition' % svc.__logname__
            blue.pyos.synchro.Sleep(100)
            if i % 600 == 0 and i > 0:
                svc.LogWarn('WaitForServiceObjectState has been sleeping for a long time waiting for ', svc.__logname__, ' to either get to state ', desiredStates, 'current state is', svc.state)
            i += 1




    def GetServiceIfStarted(self, serviceName):
        if serviceName in self.services:
            srv = self.services[serviceName]
            self.WaitForServiceObjectState(srv, (service.SERVICE_RUNNING,))
            return srv



    def GetService(self, serviceName, ms = None):
        return self.StartServiceAndWaitForRunningState(serviceName, ms)



    def StartService(self, serviceName, ms = None):
        if serviceName in self.services:
            srv = self.services[serviceName]
        elif serviceName in self.blockedServices:
            raise RuntimeError('%s has been blocked from running on this system' % serviceName)
        srv = self.CreateServiceInstance(serviceName)
        self.services[serviceName] = srv
        if srv.state in (service.SERVICE_START_PENDING, service.SERVICE_RUNNING):
            return srv
        if srv.state == service.SERVICE_STARTING_DEPENDENCIES:
            desiredStates = (service.SERVICE_START_PENDING, service.SERVICE_RUNNING)
            errorStates = (service.SERVICE_FAILED, service.SERVICE_STOPPED)
            self.WaitForServiceObjectState(srv, desiredStates, errorStates)
            return srv
        if self.state in (service.SERVICE_STOP_PENDING, service.SERVICE_STOPPED):
            raise RuntimeError, "Can't start service " + serviceName + ' when service manager is shutting down'
        if srv.state == service.SERVICE_FAILED:
            return srv
        srv.state = service.SERVICE_STARTING_DEPENDENCIES
        srv.__error__ = None
        try:
            self.dependants[serviceName] = []
            self.LogInfo('starting startup dependencies for %s, which are: %s' % (serviceName, str(srv.__startupdependencies__)))
            for each in srv.__startupdependencies__:
                if type(each) is str:
                    each = (each, each)
                (depname, asname,) = each
                depService = self.GetService(depname)
                self.dependants[depname].append(serviceName)
                if getattr(boot, 'replaceDependencyServiceWrappers', 'false').lower() != 'true' or not depService.IsRunning():
                    setattr(srv, asname, srv.session.ConnectToService(depname))
                else:
                    setattr(srv, asname, depService)

            srv.state = service.SERVICE_START_PENDING
            uthread.new(self._LoadServiceDependenciesAsych, srv, serviceName)
            for notify in srv.__notifyevents__:
                if not hasattr(srv, notify):
                    raise RuntimeError('MissingSvcExportAttribute', serviceName, 'notify', notify)
                if not self.notify.has_key(notify):
                    self.notify[notify] = []
                self.notify[notify].append(srv)

        except Exception as e:
            srv.state = service.SERVICE_FAILED
            srv.__error__ = sys.exc_info()
            raise 
        if ms:
            ms.Seek(0)
        args = (ms,)
        if serviceName in self.startInline:
            self.StartServiceRun(srv, args, serviceName)
        else:
            uthread.pool('StartService::StartServiceRun', self.StartServiceRun, srv, args, serviceName)
        return srv



    def _LoadServiceDependenciesAsych(self, srv, serviceName):
        self.LogInfo('starting dependencies for %s, which are: %s' % (serviceName, str(srv.__dependencies__)))
        for each in srv.__dependencies__:
            if type(each) is str:
                each = (each, each)
            (depname, asname,) = each
            depService = self.StartService(depname)
            self.dependants[depname].append(serviceName)
            if getattr(boot, 'replaceDependencyServiceWrappers', 'false').lower() != 'true' or not depService.IsRunning():
                setattr(srv, asname, srv.session.ConnectToService(depname))
            else:
                setattr(srv, asname, depService)




    @util.Memoized
    def GetServiceImplementation(self, target):
        classmap = dict([ (name, (name, getattr(svc, name))) for name in dir(svc) ])
        found = target
        foundPriority = -1
        for (name, svcclass,) in classmap.itervalues():
            replaces = getattr(svcclass, '__replaceservice__', None)
            if replaces == target:
                priority = getattr(svcclass, '__replacepriority__', 0)
                if priority > foundPriority:
                    found = name
                    foundPriority = priority

        return found



    def CreateServiceInstance(self, serviceName):
        old_block_trap = stackless.getcurrent().block_trap
        stackless.getcurrent().block_trap = 1
        try:
            classmap = dict([ (name, (name, getattr(svc, name))) for name in dir(svc) ])
            for (name, svcclass,) in classmap.values():
                classmap[name] = (name, getattr(svc, self.GetServiceImplementation(name)))

            try:
                (createName, createClass,) = classmap[serviceName]
            except KeyError:
                raise ServiceNotFound(serviceName)
            if createName != serviceName:
                print 'Replacing service %r with %r' % (serviceName, createName)
            replaceService = getattr(createClass, '__replaceservice__', None)
            if replaceService is not None and replaceService != serviceName:
                raise RuntimeError('Must not start %s directly as it replaces %s' % (serviceName, replaceService))
            srv = createClass()
            if not isinstance(srv, service.Service):
                raise RuntimeError('Service name %r does not resolve to a service class (%r)' % (serviceName, createClass))
            srv.__servicename__ = serviceName
            srv.session = base.GetServiceSession(serviceName)
            self.VerifyServiceExports(srv, serviceName)
            return srv

        finally:
            stackless.getcurrent().block_trap = old_block_trap




    def VerifyServiceExports(self, srv, serviceName):
        for (funcName, paramList,) in srv.__exportedcalls__.iteritems():
            if not hasattr(srv, funcName):
                raise RuntimeError('MissingSvcExportAttribute', serviceName, 'exported call', funcName)
            if type(paramList) == types.ListType:
                tmp = {}
                if len(paramList):
                    tmp['role'] = paramList[0]
                    tmp['preargs'] = paramList[1:]
                paramList = tmp
            if type(paramList) == types.DictType:
                for (k, v,) in paramList.iteritems():
                    if k not in ('role', 'caching', 'preargs', 'fastcall', 'precall', 'postcall', 'callhandlerargs', 'input', 'output') or k == 'role' and type(v) not in (types.IntType, types.LongType):
                        self.LogError('Service %s has illegal function declaration for %s:  %s is not a valid metadata key' % (serviceName, funcName, k))
                    elif k == 'fastcall':
                        if int(v) not in (0, 1):
                            self.LogError('Service %s has illegal function declaration for %s:  %s is not a valid setting for fastcall' % (serviceName, funcName, v))
                    elif k == 'preargs':
                        for eachArg in v:
                            if type(eachArg) != types.StringType or eachArg not in srv.session.__persistvars__ and eachArg not in srv.session.__nonpersistvars__:
                                self.LogError('Service %s has illegal function declaration for %s:  %s is not a valid prearg' % (serviceName, funcName, eachArg))

                    elif k == 'output':
                        if type(v) == types.InstanceType:
                            import dataset
                            setattr(dataset, funcName + 'Result', v)
                    elif k == 'caching' and 'objectCaching' in sm.services:
                        if not v:
                            self.LogError('Service %s has illegal function declaration for %s:  caching must have subinfo' % (serviceName, funcName))
                        for (k2, v2,) in v.iteritems():
                            if k2 not in ('sessionInfo', 'versionCheck', 'client', 'server', 'proxy'):
                                self.LogError('Service %s has illegal function declaration for %s:  %s is not a valid caching subinfo key' % (serviceName, funcName, k2))
                            elif k2 == 'sessionInfo' and v2 not in srv.session.__persistvars__:
                                self.LogError('Service %s has illegal function declaration for %s:  %s is not a valid session info prearg' % (serviceName, funcName, v2))


            else:
                self.LogError('Service %s has illegal function declaration for %s:  %s is not a valid metadata info type' % (serviceName, funcName, type(paramList)))




    def StartServiceRun(self, svc, args, namen):
        try:
            t0 = time.clock()
            try:
                if boot.role == 'client' and getattr(prefs, 'clientServicesWait', 'true').lower() != 'true':
                    svc.state = service.SERVICE_RUNNING
                    svc.Run(*args)
                else:
                    svc.state = service.SERVICE_START_PENDING
                    with bluepy.Timer('StartService::ServiceStartRun::' + namen):
                        svc.Run(*args)
                    svc.state = service.SERVICE_RUNNING
                    if getattr(boot, 'replaceDependencyServiceWrappers', 'false').lower() == 'true':
                        for depName in self.dependants[namen]:
                            depSvc = self.StartService(depName)
                            setattr(depSvc, namen, svc)


            finally:
                t = time.clock() - t0

        except Exception as e:
            svc.state = service.SERVICE_FAILED
            svc.__error__ = sys.exc_info()
            self.LogError('Failed to start service %s' % namen)
            raise 
        if t < 60:
            svc.LogInfo('Service', namen, 'required %-3.3f' % t, ' seconds to startup')
        else:
            svc.LogWarn('Service', namen, 'startup took %-3.3f' % t, ' seconds')
        print 'Service %s: %-3.3fs' % (namen, t)



    def StopService(self, serviceName, halt = 1, ms = None):
        self.LogInfo('Stopping %s' % serviceName)
        if not self.services.has_key(serviceName):
            return 
        srv = self.services[serviceName]
        if srv.state in (service.SERVICE_STOP_PENDING, service.SERVICE_STOPPED):
            return 
        oldstate = srv.state
        srv.state = service.SERVICE_STOP_PENDING
        for notify in srv.__notifyevents__:
            self.notify[notify].remove(srv)

        if halt:
            for each in self.dependants[serviceName]:
                self.StopService(each)

        try:
            srv.Stop(ms)
        except Exception:
            srv.state = oldstate
            log.LogException('Trying to stop service %s ' % serviceName)
            sys.exc_clear()
        if srv.state != service.SERVICE_STOPPED:
            srv.state = service.SERVICE_STOPPED
            del self.services[serviceName]



    def GetDependecyGraph(self, startupDependencies = False):
        depGraph = util.DAG()
        import svc
        depAttr = '__dependencies__'
        if startupDependencies:
            depAttr = '__startupdependencies__'
        for (k, v,) in svc.__dict__.items():
            if hasattr(v, '__guid__'):
                depGraph.AddNode(k)
                for dep in getattr(v, depAttr, []):
                    depGraph.InsertEdge(k, dep)


        return depGraph



    def HotStartService(self, serviceName):
        import blue
        ms = blue.MemStream()
        self.StopService(serviceName, ms)
        nasty.ReloadClass(self.ParseServiceClass(serviceName))
        self.StartService(serviceName, ms)



    def IsServiceRunning(self, serviceName):
        return serviceName in sm.services and self.services[serviceName].IsRunning()



    def RemoteSvc(self, serviceName):
        if boot.role == 'client':
            return session.ConnectToRemoteService(serviceName)
        self.LogError('The method sm.RemoteSvc can be called from the client only.')
        raise MethodNotCalledFromClient('sm.RemoteSvc')



    def ProxySvc(self, serviceName):
        if boot.role == 'client':
            return session.ConnectToRemoteService(serviceName, self.services['machoNet'].myProxyNodeID)
        self.LogError('The method sm.ProxySvc can be called from the client only.')
        raise MethodNotCalledFromClient('sm.ProxySvc')



    def GetActiveServices(self):
        ret = []
        for (k, srv,) in self.services.iteritems():
            if srv.state == service.SERVICE_RUNNING:
                ret.append(k)

        return ret



    def GetServicesState(self):
        ret = {}
        for (k, srv,) in self.services.iteritems():
            ret[k] = srv.state

        return ret



    def SendEvent(self, eventid, *args, **keywords):
        return self.SendEventWithoutTheStars(eventid, args, keywords)



    def SendEventWithoutTheStars(self, eventid, args, keywords = None):
        if keywords is None:
            keywords = {}
        if not eventid.startswith('Do'):
            self.LogError('SendEvent called with event ', eventid, ".  All events sent via SendEvent should start with 'Do'")
            self.LogError("Not only is the programmer responsible for this a 10z3r, but he wears his mother's underwear as well")
            log.LogTraceback()
        if not self.notify.get(eventid, []) and self.notifyObs.get(eventid, []):
            self.LogWarn("Orphan'd event.  ", eventid, "doesn't have any listeners")
        if util.IsFullLogging():
            self.LogMethodCall('SendEvent(', eventid, ',*args=', args, ',**kw=', keywords, ')')
        else:
            self.LogMethodCall('SendEvent(', eventid, ')')
        prefix = blue.pyos.taskletTimer.GetCurrent() + '::SendEvent_' + eventid + '::'
        old_block_trap = stackless.getcurrent().block_trap
        stackless.getcurrent().block_trap = 1
        ret = []
        try:
            for each in self.notify.get(eventid, []):
                try:
                    logname = prefix + getattr(each, '__logname__', '???')
                    if each.state == service.SERVICE_RUNNING:
                        self.LogMethodCall('Calling ', logname)
                        ret.append(ClockThisWithoutTheStars(logname, getattr(each, eventid), args, keywords))
                    else:
                        self.LogMethodCall('Skipping ', logname, ' (service not running)')
                except StandardError:
                    self.LogError('In %s.%s' % (getattr(each, '__guid__', '???'), eventid))
                    log.LogException()
                    sys.exc_clear()

            notifiedToRemove = []
            for each in self.notifyObs.get(eventid, []):
                ob = each()
                if ob is None:
                    notifiedToRemove.append(each)
                else:
                    try:
                        logname = prefix + str(ob)
                        self.LogMethodCall('Calling ', logname)
                        apply(getattr(ob, eventid), args, keywords)
                    except StandardError:
                        self.LogError('In %s.%s' % (getattr(each, '__guid__', '???'), eventid))
                        log.LogException()
                        sys.exc_clear()

            for toRemove in notifiedToRemove:
                if toRemove in self.notifyObs[eventid]:
                    self.notifyObs[eventid].remove(toRemove)


        finally:
            bt = 0
            if old_block_trap:
                bt = 1
            stackless.getcurrent().block_trap = bt
            return tuple(ret)




    def ChainEvent(self, eventid, *args, **keywords):
        return self.ChainEventWithoutTheStars(eventid, args, keywords)



    def ChainEventWithoutTheStars(self, eventid, args, keywords = None):
        if keywords is None:
            keywords = {}
        if not eventid.startswith('Process'):
            self.LogError('ChainEvent called with event ', eventid, ".  All events sent via ChainEvent should start with 'Process'")
            self.LogError("Not only is the programmer responsible for this a 10z3r, but he wears his mother's underwear as well")
            log.LogTraceback()
        if stackless.getcurrent().block_trap or stackless.getcurrent().is_main:
            raise RuntimeError("ChainEvent is blocking by design, but you're block trapped.  You have'll have to find some alternative means to do Your Thing, dude.")
        if not self.notify.get(eventid, []) and not self.notifyObs.get(eventid, []):
            self.LogWarn("Orphan'd event.  ", eventid, "doesn't have any listeners")
        self.LogMethodCall('ChainEvent(', eventid, ',*args=', args, ',**kw=', keywords, ')')
        prefix = blue.pyos.taskletTimer.GetCurrent() + '::ChainEvent_' + eventid + '::'
        ret = []
        for each in self.notify.get(eventid, []):
            try:
                logname = prefix + getattr(each, '__logname__', '???')
                if each.state == service.SERVICE_RUNNING:
                    self.LogMethodCall('Calling ', logname)
                    retval = ClockThisWithoutTheStars(logname, getattr(each, eventid), args, keywords)
                    ret.append(retval)
                else:
                    self.LogMethodCall('Skipping ', logname, ' (service not running)')
            except StandardError:
                self.LogError('In %s.%s' % (getattr(each, '__guid__', '???'), eventid))
                log.LogException()
                sys.exc_clear()

        notifiedToRemove = []
        for each in self.notifyObs.get(eventid, []):
            ob = each()
            if ob is None:
                notifiedToRemove.append(each)
            else:
                try:
                    logname = prefix + str(ob)
                    self.LogMethodCall('Calling ', logname)
                    ClockThisWithoutTheStars(prefix + getattr(each, '__logname__', '???'), getattr(ob, eventid), args, keywords)
                except StandardError:
                    self.LogError('In %s.%s' % (getattr(each, '__guid__', '???'), eventid))
                    log.LogException()
                    sys.exc_clear()

        for toRemove in notifiedToRemove:
            if toRemove in self.notifyObs[eventid]:
                self.notifyObs[eventid].remove(toRemove)

        return tuple(ret)



    def ScatterEvent(self, eventid, *args, **keywords):
        return self.ScatterEventWithoutTheStars(eventid, args, keywords)



    def ScatterEventWithoutTheStars(self, eventid, args, keywords = None):
        if keywords is None:
            keywords = {}
        if not eventid.startswith('On'):
            self.LogError('ScatterEvent called with event ', eventid, ".  All events sent via ScatterEvent should start with 'On'.")
            self.LogError("Not only is the programmer responsible for this a 10z3r, but he wears his mother's underwear as well")
            log.LogTraceback()
        if util.IsFullLogging():
            self.LogMethodCall('ScatterEvent(', eventid, ',*args=', args, ',**kw=', keywords, ')')
        else:
            self.LogMethodCall('ScatterEvent(', eventid, ')')
        prefix = blue.pyos.taskletTimer.GetCurrent() + '::ScatterEvent_' + eventid + '::'
        for each in self.notify.get(eventid, []):
            try:
                logname = prefix + getattr(each, '__logname__', '???')
                if each.state == service.SERVICE_RUNNING:
                    self.LogMethodCall('Calling ', logname)
                    ctx = prefix + getattr(each, '__guid__', '???')
                    uthread.worker(ctx, self.MollycoddledUthread, getattr(each, '__guid__', '???'), eventid, getattr(each, eventid), args, keywords)
                else:
                    self.LogMethodCall('Skipping ', logname, ' (service not running)')
            except Exception:
                log.LogException()

        notifiedToRemove = []
        for wref in self.notifyObs.get(eventid, []):
            try:
                ob = wref()
                func = getattr(ob, eventid, None)
                if ob is None or func is None:
                    notifiedToRemove.append(wref)
                else:
                    logname = prefix + str(ob)
                    self.LogMethodCall('Calling ', logname)
                    uthread.workerWithoutTheStars('', func, args, keywords)
            except Exception:
                log.LogException()

        for toRemove in notifiedToRemove:
            if toRemove in self.notifyObs[eventid]:
                self.notifyObs[eventid].remove(toRemove)




    def MollycoddledUthread(self, guid, eventid, func, args, keywords):
        try:
            apply(func, args, keywords)
        except:
            self.LogError('In %s.%s' % (guid, eventid))
            log.LogException()
            sys.exc_clear()



    def FavourMe(self, fn):
        self.notify[fn.__name__].remove(fn.im_self)
        self.notify[fn.__name__] = [fn.im_self] + self.notify[fn.__name__]



    def UnfavourMe(self, fn):
        if fn.im_self in self.notify[fn.__name__]:
            self.notify[fn.__name__].remove(fn.im_self)
            self.notify[fn.__name__] = self.notify[fn.__name__] + [fn.im_self]
        else:
            self.LogWarn('Cannot unfavour ', fn.im_self, ' from ', fn.__name__, ", since it's not a notification listener")



    def RegisterNotify(self, ob):
        if hasattr(ob, '__notifyevents__'):
            if isinstance(ob, service.Service):
                for notify in ob.__notifyevents__:
                    if not self.notify.has_key(notify):
                        self.notify[notify] = []
                    if ob not in self.notify[notify]:
                        self.notify[notify].append(ob)

            else:
                for notify in ob.__notifyevents__:
                    if not self.notifyObs.has_key(notify):
                        self.notifyObs[notify] = []
                    if weakref.ref(ob) not in self.notifyObs[notify]:
                        self.notifyObs[notify].append(weakref.ref(ob))

        else:
            self.LogError('An object is calling registernotify without there being any notifyevents, the object is ', ob)
            log.LogTraceback()



    def UnregisterNotify(self, ob):
        if hasattr(ob, '__notifyevents__'):
            if isinstance(ob, service.Service):
                for notify in ob.__notifyevents__:
                    if self.notify.has_key(notify):
                        if ob in self.notify[notify]:
                            self.notify[notify].remove(ob)

            else:
                for notify in ob.__notifyevents__:
                    if self.notifyObs.has_key(notify):
                        self.notifyObs[notify] = filter(lambda x: x != weakref.ref(ob) and x() is not None, self.notifyObs[notify])

        else:
            self.LogError('An object is calling unregisternotify without there being any notifyevents, the object is ', ob)
            log.LogTraceback()




