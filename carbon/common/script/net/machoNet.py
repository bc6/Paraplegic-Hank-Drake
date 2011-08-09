import blue
import uthread
import stackless
import sys
import types
import base
import util
import random
import gps
import weakref
import macho
import copy
import socket
import locks
import log
import service
from hashlib import sha1
import const
import dbutil
import bluepy
import collections
from service import ROLE_SERVICE, ROLE_ADMIN, ROLE_ANY, ROLE_VIPLOGIN, SERVICE_RUNNING, SERVICE_START_PENDING
globals().update(service.consts)
Enter = blue.pyos.taskletTimer.EnterTasklet
Leave = blue.pyos.taskletTimer.ReturnFromTasklet
MACHONETMSG_TYPE_AUTHENTICATION_REQ = 0
MACHONETMSG_TYPE_AUTHENTICATION_RSP = 1
MACHONETMSG_TYPE_IDENTIFICATION_REQ = 2
MACHONETMSG_TYPE_IDENTIFICATION_RSP = 3
MACHONETMSG_TYPE_CALL_REQ = 6
MACHONETMSG_TYPE_CALL_RSP = 7
MACHONETMSG_TYPE_TRANSPORTCLOSED = 8
MACHONETMSG_TYPE_RESOLVE_REQ = 10
MACHONETMSG_TYPE_RESOLVE_RSP = 11
MACHONETMSG_TYPE_NOTIFICATION = 12
MACHONETMSG_TYPE_ERRORRESPONSE = 15
MACHONETMSG_TYPE_SESSIONCHANGENOTIFICATION = 16
MACHONETMSG_TYPE_SESSIONINITIALSTATENOTIFICATION = 18
MACHONETMSG_TYPE_PING_REQ = 20
MACHONETMSG_TYPE_PING_RSP = 21
MSG_TYPE_MOVEMENTNOTIFICATION = 100
MACHONETERR_UNMACHODESTINATION = 0
MACHONETERR_UNMACHOCHANNEL = 1
MACHONETERR_WRAPPEDEXCEPTION = 2
OOB_SESSIONNOTIFICATION = 1
offsetMap = {'tcp:packet:client': 0,
 'tcp:packet:machoNet': 1,
 'tcp:raw:http': 2}
offsetMap = {'client': offsetMap,
 'server': offsetMap,
 'proxy': offsetMap,
 'orchestratorAgent': offsetMap,
 'orchestratorMaster': offsetMap}
offsetStep = {'proxy': 1000,
 'server': 10,
 'client': 10,
 'orchestratorAgent': 10,
 'orchestratorMaster': 10}
gpsMap = {'client': {'tcp:raw:http': 'gps.SocketTransportFactory',
            'tcp:packet:server': 'gps.SecureSocketPacketTransportFactory'},
 'proxy': {'tcp:packet:client': 'gps.SecureSocketPacketTransportFactory',
           'tcp:packet:machoNet': 'gps.SocketPacketTransportFactory',
           'tcp:raw:http': 'gps.SocketTransportFactory'},
 'server': {'tcp:packet:machoNet': 'gps.SocketPacketTransportFactory',
            'tcp:raw:http': 'gps.SocketTransportFactory'},
 'orchestratorAgent': {'tcp:raw:http': 'gps.SocketTransportFactory',
                       'tcp:packet:machoNet': 'gps.SocketPacketTransportFactory'},
 'orchestratorMaster': {'tcp:raw:http': 'gps.SocketTransportFactory',
                        'tcp:packet:machoNet': 'gps.SocketPacketTransportFactory'}}
import iocp
if iocp.UsingSSL():
    log.general.Log('Encryption: SSL', log.LGINFO)
    gpsMap['client']['tcp:packet:server'] = 'gps.SSLSocketPacketTransportFactory'
    gpsMap['proxy']['tcp:packet:client'] = 'gps.SSLSocketPacketTransportFactory'
else:
    log.general.Log('Encryption: MachoNet', log.LGINFO)
if iocp.UsingHTTPS():
    gpsMap['proxy']['tcp:raw:http'] = 'gps.SSLSocketTransportFactory'
    gpsMap['server']['tcp:raw:http'] = 'gps.SSLSocketTransportFactory'
    log.general.Log('Using HTTPS', log.LGINFO)
gpcsMap = {'server': {None: ['gpcs.ExceptionWrapper',
                   'gpcs.ExceptionMapping',
                   'gpcs.Resolve',
                   'gpcs.ObjectCall',
                   'gpcs.ServiceCall',
                   'gpcs.BroadcastStuff'],
            'sessionchange': ['gpcs.SessionChange']},
 'client': {None: ['gpcs.ExceptionWrapper',
                   'gpcs.ExceptionMapping',
                   'gpcs.ObjectCall',
                   'gpcs.ServiceCall',
                   'gpcs.BroadcastStuff'],
            'sessionchange': ['gpcs.SessionChange']},
 'proxy': {None: ['gpcs.ExceptionWrapper',
                  'gpcs.ExceptionMapping',
                  'gpcs.ObjectCall',
                  'gpcs.ServiceCall',
                  'gpcs.BroadcastStuff'],
           'sessionchange': ['gpcs.SessionChange']},
 'orchestratorAgent': {None: ['gpcs.ExceptionWrapper',
                              'gpcs.ExceptionMapping',
                              'gpcs.ObjectCall',
                              'gpcs.ServiceCall',
                              'gpcs.BroadcastStuff']},
 'orchestratorMaster': {None: ['gpcs.ExceptionWrapper',
                               'gpcs.ExceptionMapping',
                               'gpcs.ObjectCall',
                               'gpcs.ServiceCall',
                               'gpcs.BroadcastStuff']}}
packetTypeChannelMap = {MACHONETMSG_TYPE_SESSIONCHANGENOTIFICATION: 'sessionchange',
 MACHONETMSG_TYPE_SESSIONINITIALSTATENOTIFICATION: 'sessionchange'}

def MachoDumps(packet):
    return blue.marshal.Save(packet, None)



def MachoLoads(packet):
    ret = blue.marshal.Load(packet, skipCrcCheck=True)
    if isinstance(ret, GPSTransportClosed):
        log.general.Log('Raising a GPSTransportClosed exception from remote')
        raise ret
    return ret



def MachoSanitizedGetObjectID(object):
    if type(object) == types.InstanceType:
        if not isinstance(object, Exception):
            return strx(object)



def MachoSanitizedParseObjectID(objectID):
    return objectID



def MachoDumpsSanitized(what):
    return blue.marshal.Save(what, MachoSanitizedGetObjectID)



def MachoLoadsSanitized(what):
    ret = blue.marshal.Load(what, MachoSanitizedParseObjectID)
    if isinstance(ret, GPSTransportClosed):
        log.general.Log('Raising a GPSTransportClosed exception from remote')
        raise ret
    return ret



def PasswordHash(userName, password):
    unicodeUserName = unicode(userName).strip()
    unicodePassword = unicode(password)
    salt = buffer(unicodeUserName.lower())
    hash = sha1(buffer(unicodePassword) + salt)
    for i in xrange(1000):
        blue.pyos.BeNice()
        hash = sha1(buffer(hash.digest()) + salt)

    return hash.digest()



class FakeMachoLock():

    def __init__(self):
        self.aquire = self.release = self.__enter__ = lambda *args: self
        self.__exit__ = lambda *args: False




def MachoThrottle(callKey):
    if int(sm.GetService('machoNet').GetClientConfigVals().get('disableClientCallThrottling', 0)):
        return FakeMachoLock()
    return locks.TempLock(callKey, locks.RLock)



class MachoNetService(service.Service):
    __guid__ = 'svc.machoNet'
    __displayname__ = 'MachoNet Service'
    if boot.role == 'server':
        __startupdependencies__ = ['DB2']
    __dependencies__ = []
    __configvalues__ = {'acceptThreadCount': 20,
     'cleanupInterval': 180,
     'defaultClientPortOffset': 15000,
     'defaultServerPortOffset': 10000,
     'defaultProxyPortOffset': 26000,
     'defaultOrchestratorMasterPortOffset': 30000,
     'defaultOrchestratorAgentPortOffset': 40000,
     'defaultTunnelPortOffset': 50000,
     'bannedIPs': [],
     'vipMode': 0,
     'callTimeOutInterval': 480 if boot.role != 'client' else 3600,
     'clientKeepAliveTimerInterval': 240,
     'serverKeepAliveTimerInterval': 60,
     'clientLogonQueuePollTime': 60,
     'minimumSolCount': 0,
     'minimumProxyCount': 0,
     'nodeRefreshInterval': 30,
     'proxyStatPollInterval': 180,
     'proxyStatSmoothie': 10,
     'nodeLoadPush': 300,
     'disconnectUnauthorizedUsersPollInterval': 3600,
     'disconnectUnauthorizedUsersDelayInterval': 15,
     'clientSessionTimeoutGranularity': 60,
     'connectionLimit': 1000,
     'maxLoginsPerMinute': 60,
     'acceptDelay': 10,
     'autoLogoffAuthenticatedTransportInterval': 180,
     'debugHeartBeat': 0}
    __exportedcalls__ = {'CheckACL': [ROLE_SERVICE | ROLE_ADMIN],
     'IsThisDudeCoolForLogin': [ROLE_SERVICE],
     'GetTransport': [ROLE_SERVICE],
     'GetTransportIDByTransport': [ROLE_SERVICE],
     'GetTransportOfNode': [ROLE_SERVICE],
     'GetNodeFromAddress': [ROLE_SERVICE | ROLE_ADMIN],
     'CheckAddressCache': [ROLE_SERVICE | ROLE_ADMIN],
     'ClearNodeOfAddresses': [ROLE_SERVICE | ROLE_ADMIN],
     'GetFullAddressCache': [ROLE_SERVICE | ROLE_ADMIN],
     'GetMyAddresses': [ROLE_SERVICE | ROLE_ADMIN],
     'GetNodeID': [ROLE_SERVICE | ROLE_ADMIN],
     'GetNodeName': [ROLE_SERVICE | ROLE_ADMIN],
     'GetServerStatus': [ROLE_ANY],
     'GetGPCS': [ROLE_SERVICE],
     'GetConnectionProperties': [ROLE_ANY],
     'GetConnectionPropertiesAndTransferHTTPAuthorization': [ROLE_SERVICE],
     'SetConnectionProperty': [ROLE_ADMIN],
     'RefreshConnectivity': [ROLE_ADMIN],
     'ConnectToServer': [ROLE_ANY],
     'ConnectToAddress': [ROLE_SERVICE],
     'RegisterTransportIDForApplication': [ROLE_SERVICE],
     'UnRegisterTransportIDForApplication': [ROLE_SERVICE],
     'StartTransportReader': [ROLE_SERVICE],
     'DisconnectFromServer': [ROLE_ANY],
     'IsConnected': [ROLE_ANY],
     'GetBasePortNumber': [ROLE_ANY],
     'GetClientSessionID': [ROLE_ANY],
     'GetInitVals': [ROLE_ANY],
     'GetTime': [ROLE_ANY],
     'Shutdown': [ROLE_SERVICE],
     'GracefulShutdown': [ROLE_SERVICE],
     'GracefulShutdownStarted': [ROLE_SERVICE],
     'GracefulShutdownComplete': [ROLE_SERVICE],
     'IsClusterShuttingDown': [ROLE_SERVICE],
     'TerminateUnconnectedNodes': [ROLE_SERVICE],
     'TerminateClient': [ROLE_SERVICE],
     'ConnectivityTest': [ROLE_SERVICE],
     'GetCPULoad': [ROLE_SERVICE],
     'GetNetworkStats': [ROLE_SERVICE],
     'GetBlockingCallStats': [ROLE_SERVICE],
     'GetConnectedSolNodes': [ROLE_SERVICE],
     'GetConnectedProxyNodes': [ROLE_SERVICE],
     'GetConnectedNodes': [ROLE_SERVICE],
     'GetClusterSessionStatistics': [ROLE_ANY],
     'GetSessionStatistics': [ROLE_SERVICE],
     'SendProvisionalResponse': [ROLE_SERVICE],
     'GetIDOfAddress': [ROLE_SERVICE],
     'Subscribe': [ROLE_SERVICE],
     'SubscribeMany': [ROLE_SERVICE],
     'UnSubscribe': [ROLE_SERVICE],
     'UnSubscribeMany': [ROLE_SERVICE],
     'GetSubscriptionInfo': [ROLE_SERVICE],
     'PrimeAddressCache': [ROLE_SERVICE],
     'AreTheseServicesRunning': [ROLE_SERVICE],
     'GetValidClientCodeHash': [ROLE_SERVICE],
     'ReloadClientCodeHash': [ROLE_SERVICE],
     'GetLogonQueuePosition': [ROLE_SERVICE],
     'GetLogonQueueStats': [ROLE_SERVICE],
     'GetPolarisExternalTunnelingAddress': [ROLE_SERVICE],
     'IsResurrectedNode': [ROLE_SERVICE],
     'CalculatePortNumber': [ROLE_SERVICE],
     'GetPortOffsetStep': [ROLE_SERVICE],
     'GetClientConfigVals': [ROLE_SERVICE],
     'UpdateClientConfigVals': [ROLE_SERVICE],
     'ForwardNotificationToNode': [ROLE_SERVICE],
     'GetBaseTunnelPortOffset': [ROLE_SERVICE]}
    __counters__ = {'dataSent': 'traffic',
     'dataReceived': 'traffic',
     'blockingCallTimes': 'traffic',
     'compressedBytes': 'traffic',
     'decompressedBytes': 'traffic',
     'broadcastsResolved': 'traffic',
     'broadcastsMissed': 'normal'}
    __notifyevents__ = ['ProcessSessionChange',
     'OnNewNode',
     'OnNodeDeath',
     'OnMachoObjectDisconnect',
     'OnObjectPublicAttributesUpdated',
     'OnClusterStarting',
     'OnRefreshConnectivity',
     'OnNodeLoadPush',
     'OnPeopleWhoShouldntBeLoggedInNotification',
     'OnVIPListChanged',
     'OnTimeReset',
     'OnClientCodeUpdated',
     'OnClearInitVals',
     'OnClientConfigUpdated',
     'OnClusterDesegmentation']
    __gpcsmethodnames__ = ['Objectcast',
     'ObjectcastWithoutTheStars',
     'Queuedcast',
     'QueuedcastWithoutTheStars',
     'Scattercast',
     'ScattercastWithoutTheStars',
     'Broadcast',
     'ClientBroadcast',
     'ClusterBroadcast',
     'ServerBroadcast',
     'ProxyBroadcast',
     'NodeBroadcast',
     'NarrowcastByClientIDs',
     'NarrowcastByClientIDsWithoutTheStars',
     'SequencedNarrowcastByClientIDs',
     'SequencedNarrowcastByClientIDsWithoutTheStars',
     'NarrowcastByCharIDs',
     'NarrowcastByUserIDs',
     'NarrowcastByNodeIDs',
     'SinglecastByServiceMask',
     'SinglecastByClientID',
     'SinglecastByCharID',
     'SinglecastByNodeID',
     'SinglecastByUserID',
     'ConnectToRemoteService',
     'ConnectToAllServices',
     'ConnectToAllNeighboringServices',
     'ConnectToAllSiblingServices',
     'RemoteServiceCallWithoutTheStars',
     'RemoteServiceNotifyWithoutTheStars',
     'ResetAutoResolveCache',
     'RemoteServiceCall',
     'RemoteServiceNotify',
     'OnObjectPublicAttributesUpdated',
     'ReliableSinglecastByCharID',
     'ReliableSinglecastByUserID',
     'SinglecastByWorldSpaceID']
    __pingrequestorresponse__ = (MACHONETMSG_TYPE_PING_RSP, MACHONETMSG_TYPE_PING_REQ)
    __sessioninitorchangenotification__ = (MACHONETMSG_TYPE_SESSIONINITIALSTATENOTIFICATION, MACHONETMSG_TYPE_SESSIONCHANGENOTIFICATION)
    __clientallowedcommands__ = (MACHONETMSG_TYPE_ERRORRESPONSE,
     MACHONETMSG_TYPE_NOTIFICATION,
     MACHONETMSG_TYPE_CALL_RSP,
     MACHONETMSG_TYPE_CALL_REQ,
     MACHONETMSG_TYPE_RESOLVE_REQ,
     MACHONETMSG_TYPE_PING_REQ,
     MACHONETMSG_TYPE_PING_RSP,
     MSG_TYPE_MOVEMENTNOTIFICATION)
    __notificationtypes__ = (MACHONETMSG_TYPE_NOTIFICATION,
     MACHONETMSG_TYPE_SESSIONCHANGENOTIFICATION,
     MACHONETMSG_TYPE_SESSIONINITIALSTATENOTIFICATION,
     MSG_TYPE_MOVEMENTNOTIFICATION)
    __calltypes__ = (MACHONETMSG_TYPE_CALL_REQ, MACHONETMSG_TYPE_RESOLVE_REQ)
    __responsetypes__ = (MACHONETMSG_TYPE_ERRORRESPONSE, MACHONETMSG_TYPE_CALL_RSP, MACHONETMSG_TYPE_RESOLVE_RSP)
    __server_scattercast_session_variables__ = ('userid', 'objectID', 'charid')

    def __init__(self):
        self.shutdown = None
        self.initialAuthData = None
        self.clockReset = False
        self.handlingClientAuthentication = 0
        self.scheduleCount = 0
        if macho.mode == 'server':
            self.__dependencies__.append('DB2')
            self.clusterSessionStatistics = {}
        elif macho.mode == 'proxy':
            self.proxySessionStatistics = []
            self.proxySessionStatistics_Return = None
        self.nodeCPULoadValue = {}
        self.serverNames = {}
        service.Service.__init__(self)
        if macho.mode == 'server' and ('/compileconstants' in blue.pyos.GetArg() or '/compile' in blue.pyos.GetArg()):
            self.connectToCluster = 0
        else:
            self.connectToCluster = 1
        self.acceptStart = None
        self.clientLogonQueue = util.KeyVal(address='', timestamp=None, position=None, history=None, reportedQueued=False)
        self.serverLogonQueue = []
        self.clientHalfBakedTransports = {}
        self.namedtransports = {}
        self.transportsByID = {}
        self.transportIDbyClientID = {}
        self.transportIDbyProxyNodeID = {}
        self.transportIDbySolNodeID = {}
        self.transportIDbyAppNodeID = {}
        self.externalAddressesByNodeID = {}
        self.nodeIDsByServiceMask = collections.defaultdict(set)
        self.channelHandlersUp = {}
        self.channelHandlersDown = {}
        self.polarisExternalTunneling = None
        self.basePortNumber = self.defaultProxyPortOffset
        self.baseTunnelPortOffset = self.defaultTunnelPortOffset
        self.nodeID = None
        self.expectedLoadValue = {}
        self.clientIDOffset = 1
        self.stop = 1
        self.transportID = 1L
        self.calls = {}
        self.callsCountMax = 0
        self.callsCountMin = 0
        self.callID = 1L
        self._addressCache = gps.AddressCache()
        self.myProxyNodeID = None
        self.dontLayTracksTo = {}
        if macho.mode == 'client':
            self.authenticating = 0
            self.gettingServerStatus = 0
            self.clientSessionID = 0
        self.loggedOnUserCount = None
        self.loggedOnUserCountHistory = []
        self.seq = 0L
        self.seqwait = {}
        self.serviceInfo = {}
        self.locks = {}
        self.deadNodes = {}
        self.serviceMappings = {}
        self.serviceMaskByServiceID = {}
        self.serviceNameByServiceID = {}
        self.factories = {}
        self.spam = {}
        self.kickedTick = 0
        self.subscriptionsByClientID = {}
        self.subscriptionsByAddress = {}
        self.subscriptionCountsByAddress = {}
        self.startedWhen = blue.os.GetTime()
        self.paon = None
        self.paonLock = uthread.Semaphore('MachoNet:paonLock')
        self.vipLock = uthread.Semaphore('MachoNet:vipLock')
        self.initValLock = uthread.Semaphore('MachoNet:initValLock')
        self.clusterStartLock = uthread.Semaphore('MachoNet:clusterStartLock')
        for svc in sm.services.itervalues():
            if hasattr(svc, '__machoresolve__'):
                self.serviceInfo[svc.__logname__] = svc.__machoresolve__

        self.clientConfigVals = None
        self.shutdownInProgress = False
        self.serviceMask = const.cluster.SERVICE_NONE
        self.getNodeFromAddressWarnsDone = {}



    def ForwardNotificationToNode(self, source, destination, userID, payload):
        orginalClientID = source.clientID
        localTransport = self.transportsByID[self.transportIDbyClientID[orginalClientID]]
        packet = macho.Notification(source=source, destination=destination, userID=userID, payload=payload)
        self.HandleMessage(localTransport, packet)
        self.SinglecastByClientID(orginalClientID, 'OnUpdateServiceMapping', destination.service, destination.nodeID)



    def GetBaseTunnelPortOffset(self):
        return self.baseTunnelPortOffset



    def IsResurrectedNode(self):
        return self.resurrectedNode



    def GetPolarisExternalTunnelingAddress(self):
        if macho.mode == 'server' and self.polarisExternalTunneling is not None and self.polarisExternalTunneling.proxyNodeID in self.transportIDbyProxyNodeID:
            return self.polarisExternalTunneling.address
        else:
            lastNodeID = None
            last = None
            for (nodeID, transportID,) in self.transportIDbyProxyNodeID.iteritems():
                machoTransport = self.transportsByID.get(transportID, None)
                if machoTransport is not None:
                    (host2, port2,) = machoTransport.transport.GetAddress().split(':')
                    tmp2 = host2.split('.')
                    if last is None or int(tmp2[3]) < last:
                        last = int(tmp2[3])
                        lastNodeID = nodeID

            if macho.mode == 'server':
                self.polarisExternalTunneling = util.KeyVal(proxyNodeID=lastNodeID, address=self.session.ConnectToProxyServerService('machoNet', lastNodeID).GetPolarisExternalTunnelingAddress())
                return self.polarisExternalTunneling.address
            address = self.GetTransport('tcp:packet:client').GetESPAddress()
            (host, port,) = address.split(':')
            tmp = host.split('.')
            last = int(host.split('.')[3])
            host = '.'.join(tmp[:3]) + '.' + str(last)
            return host + ':%d' % (self.defaultTunnelPortOffset + 1)



    def __GetSubscriptionFamily(self, family):
        if family not in self.subscriptionsByClientID:
            self.subscriptionsByClientID[family] = {}
            self.subscriptionsByAddress[family] = {}
            self.subscriptionCountsByAddress[family] = {}
        return (self.subscriptionsByClientID[family], self.subscriptionsByAddress[family], self.subscriptionCountsByAddress[family])



    def Subscribe(self, family, clientID, address, trackCount = 1, visibility = 1):
        if clientID not in self.transportIDbyClientID:
            return 
        (byClientID, byAddress, countsByAddress,) = self._MachoNetService__GetSubscriptionFamily(family)
        if clientID not in byClientID:
            byClientID[clientID] = {address: visibility}
        else:
            byClientID[clientID][address] = visibility
        if address not in byAddress:
            byAddress[address] = {clientID: visibility}
        else:
            byAddress[address][clientID] = visibility
        if trackCount:
            countsByAddress[address] = len(byAddress[address])



    def SubscribeMany(self, family, clientID, addresses, trackCount = 1, visibility = 1):
        self.LogInfo('SubscribeMany:  subscribing to many:  ', (family,
         clientID,
         addresses,
         trackCount,
         visibility))
        for address in addresses:
            self.LogInfo('subscribing to ', address)
            self.Subscribe(family, clientID, address, trackCount, visibility)

        self.LogInfo('SubscribeMany:  done')



    def UnSubscribe(self, family, clientID, address):
        (byClientID, byAddress, countsByAddress,) = self._MachoNetService__GetSubscriptionFamily(family)
        if clientID in byClientID:
            if address in byClientID[clientID]:
                del byClientID[clientID][address]
            if not byClientID[clientID]:
                del byClientID[clientID]
        if address in byAddress:
            if clientID in byAddress[address]:
                del byAddress[address][clientID]
            if not byAddress[address]:
                del byAddress[address]
        if address in countsByAddress:
            if address in byAddress:
                countsByAddress[address] = len(byAddress[address])
            else:
                del countsByAddress[address]



    def UnSubscribeMany(self, family, clientID, addresses):
        for address in addresses:
            self.UnSubscribe(family, clientID, address)




    @bluepy.TimedFunction('machoNet::GetSubscriptionInfo')
    def GetSubscriptionInfo(self, family, address = None):
        (byClientID, byAddress, countsByAddress,) = self._MachoNetService__GetSubscriptionFamily(family)
        if address is None:
            return countsByAddress
        else:
            clientIDs = byAddress.get(address, {})
            subscribers = []
            for (clientID, visibility,) in clientIDs.iteritems():
                if visibility:
                    s = self.GetSessionByClientID(clientID)
                    if s and s.charid:
                        subscribers.append(self._GetSubscriptionInfoRow(s))

            return subscribers



    def _GetSubscriptionInfoRow(self, sess):
        return [sess.charid]



    def SessionsFromClientIDs(self, clientIDs):
        sessions = []
        for clientID in clientIDs:
            transportID = self.transportIDbyClientID.get(clientID, None)
            if transportID is not None:
                transport = self.transportsByID.get(transportID, None)
                if transport is not None:
                    sessions.append(transport._SessionFromClientID(clientID))

        return sessions



    def GetFactory(self, factoryName, args):
        k = args[1]
        if k not in self.factories:
            f = CreateInstance(factoryName, args)
            if 'machoNet' in k:
                f.MaxPacketSize = 1073741824
            self.factories[k] = (factoryName, args, f)
        else:
            (n, a, f,) = self.factories[k]
            if n != factoryName or a != args:
                log.LogTraceback()
                raise RuntimeError('Thou shall not GetFactory with differing factoryName or args')
        return f



    def Run(self, memStream = None):
        self.vipkeys = None
        self.peopleWhoShouldntBeLoggedIn = {}
        self.heartbeatInterval = 60
        self.state = SERVICE_START_PENDING
        service.Service.Run(self, memStream)
        self.LogInfo('Running macho net')
        self.stop = 0
        self.clusterStartupPhase = False
        self.availableLoginSlots = 0
        if macho.mode == 'client' and not int(prefs.GetValue('http', 0)):
            try:
                del offsetMap[macho.mode]['tcp:raw:http']
            except StandardError:
                sys.exc_clear()
        if macho.mode == 'client':
            self.basePortNumber = self.defaultClientPortOffset
        elif macho.mode == 'server':
            self.basePortNumber = self.defaultServerPortOffset
        elif macho.mode == 'proxy':
            self.basePortNumber = self.defaultProxyPortOffset
        elif macho.mode == 'orchestratorMaster':
            self.basePortNumber = self.defaultOrchestratorMasterPortOffset
        elif macho.mode == 'orchestratorAgent':
            self.basePortNumber = self.defaultOrchestratorAgentPortOffset
        else:
            return 
        blue.net.SetMode(macho.mode)
        self.LogInfo('Opening listen ports')
        self.resurrectedNode = False
        fixedhop = None
        for arg in blue.pyos.GetArg():
            if arg.lower().startswith('/machohop='):
                fixedhop = int(arg[len('/machohop='):])
            if arg.lower().startswith('/machoresurrection'):
                self.resurrectedNode = True

        offsets = offsetMap[macho.mode].items()
        offsets = [ (k, v) for (k, v,) in offsets if k in gpsMap[macho.mode] ]
        offsets.sort(key=lambda t: t[1])
        transports = {}
        if fixedhop is not None:
            self.basePortNumber += fixedhop * offsetStep[macho.mode]
            self.baseTunnelPortOffset += fixedhop * offsetStep[macho.mode]
        while True:
            try:
                for (each, offset,) in offsets:
                    port = self.basePortNumber + offset
                    self.LogInfo('Open listen transport for ', each, ' on port ', port)
                    factory = self.GetFactory(gpsMap[macho.mode][each], (macho.mode == 'proxy' and each.endswith(':client'), each))
                    transports[each] = factory.Listen(port)

            except GPSAddressOccupied as e:
                self.LogInfo('port ', port, ' occupied')
                for each in transports.itervalues():
                    each.Close('Desired address occupied in Run')

                transports.clear()
                sys.exc_clear()
            else:
                break
            if fixedhop is not None:
                errreason = 'Failed to acquire the required port range running in fixed hop (=%d) mode.  Terminating process' % (fixedhop,)
                self.LogError(errreason)
                log.Quit(errreason)
            self.basePortNumber += offsetStep[macho.mode]
            self.baseTunnelPortOffset += offsetStep[macho.mode]
            if self.basePortNumber > self.defaultTunnelPortOffset:
                raise RuntimeError("Something is seriously wrong.  I've tried plenty of port number ranges, and still no luck.")
            self.LogInfo('looping, base=', self.basePortNumber)

        self.LogInfo('All transports acquired:  ', transports, ', ', offsetMap[macho.mode])
        self.namedtransports = transports
        if macho.mode == 'proxy':
            self.nodeID = self.GetIDOfAddress(self.GetTransport('tcp:packet:client').GetInternalAddress(), clientMode=False)
            print 'nodeID=',
            print self.nodeID
        elif macho.mode == 'server':
            self.LogInfo('Registering node')
            self.dbzcluster = self.DB2.GetSchema('zcluster')
            self.dbzuser = self.DB2.GetSchema('zuser')
            retry = False
            while True:
                self.dbzcluster.Nodes_TrashLimbos(self.cleanupInterval)
                (host, port,) = self.GetTransport('tcp:packet:machoNet').GetExternalAddress().split(':')
                internalAddress = self.GetTransport('tcp:packet:machoNet').GetInternalAddress().split(':')[0]
                ret = self.dbzcluster.Nodes_Register(host, self.basePortNumber, self.connectToCluster, macho.version, boot.version, boot.build, blue.os.pid, self.resurrectedNode, internalAddress)
                errreason = None
                if ret == -1:
                    errreason = "zcluster.Nodes_Register refused to accept the registration.  The cluster has already passed it's connectivity tests."
                    if not retry:
                        lastHeartBeat = self.DB2.SQL('SELECT lastHeartBeat= MAX(heartbeat) FROM zcluster.nodes')[0].lastHeartBeat
                        countDateTime = self.DB2.SQL("SELECT countDateTime = CONVERT(datetime, [value], 121) FROM zsystem.settings WHERE [group] = 'zcluster' AND [key] = 'TrashLimboNodes-LastCall'")[0].countDateTime
                        if lastHeartBeat is not None:
                            delay = 3000 + (self.cleanupInterval * const.SEC + lastHeartBeat - blue.os.GetTime()) / const.MSEC
                            if countDateTime is not None:
                                delay = max(delay, 3000 + (countDateTime + self.cleanupInterval * const.SEC - blue.os.GetTime()) / const.MSEC)
                            if delay > 0:
                                print errreason
                                self.LogWarn(errreason)
                                print 'The previous run might however be dead, delaying and retrying after ',
                                print delay,
                                print ' ms...'
                                self.LogWarn('The previous run might however be dead, delaying and retrying after ', delay, ' ms...')
                                blue.pyos.synchro.Sleep(delay)
                                retry = True
                                continue
                elif ret == -2:
                    errreason = 'An app lock timeout occurred in zcluster.Nodes_Register'
                elif ret == -3:
                    errreason = 'The host is not a member of the specified cluster.  Configure zcluster.proxies and zcluster.servers correctly.'
                elif type(ret) == types.IntType:
                    errreason = 'An unspecified error occurred while registering the node: %d' % ret
                if errreason:
                    self.LogError(errreason)
                    log.Quit(errreason)
                break

            self.nodeID = ret[0][0].nodeID
            self.serviceMask = ret[0][0].serviceMask
            if self.serviceMask is None:
                self.serviceMask = const.cluster.SERVICE_ALL
            self.premapped = prefs.clusterMode in ('TEST', 'LIVE')
            for each in ret[1]:
                self.serviceMappings[each.serviceName] = [each.serviceID, each.serviceMask]
                self.serviceMaskByServiceID[each.serviceID] = each.serviceMask
                self.serviceNameByServiceID[each.serviceID] = each.serviceName

            for each in ret[2]:
                self.serverNames[each.nodeID] = getattr(each, 'hostName', None)

            if self.connectToCluster and not self.premapped:
                polarisNodeID = self.GetNodeFromAddress(const.cluster.SERVICE_POLARIS, 0)
        elif macho.mode == 'orchestratorAgent':
            customIDData = (self.defaultOrchestratorAgentPortOffset, offsetMap[macho.mode]['tcp:packet:machoNet'], 2000000)
            self.nodeID = self.GetIDOfAddress(self.GetTransport('tcp:packet:machoNet').GetInternalAddress(), clientMode=False, customIDData=customIDData)
            print 'nodeID=',
            print self.nodeID
        elif macho.mode == 'orchestratorMaster':
            address = socket.gethostbyname(socket.gethostname()) + ':%d' % self.CalculatePortNumber('tcp:packet:machoNet', 'orchestratorAgent')
            customIDData = (self.defaultOrchestratorAgentPortOffset, offsetMap[macho.mode]['tcp:packet:machoNet'], 2000000)
            self.nodeID = self.GetIDOfAddress(address, clientMode=False, customIDData=customIDData)
            self.nodeID = self.GetIDOfAddress(address, clientMode=True)
            print 'nodeID=',
            print self.nodeID
        else:
            self.nodeID = None
        if self.nodeID:
            blue.net.SetMyNodeID(self.nodeID)
        if macho.mode == 'server':
            self.LogInfo('Establishing timers')
            uthread.worker('machoNet::OnHeartBeat', self.OnHeartBeat)
            uthread.worker('machoNet::OnCleanUp', self.OnCleanUp)
            uthread.worker('machoNet::GracefulShutdown', self._MachoNetService__GracefulShutdownWorker)
            self.acceptThreadCount = 1
            self.LogInfo('Monkeypatching acceptThreadCount. Value now ' + str(self.acceptThreadCount))
        machoListeners = [ k for k in gpsMap[macho.mode].keys() if k.find(':packet:') >= 0 ]
        machoListeners = [ k for k in machoListeners if k in offsetMap[macho.mode] ]
        for eachTransport in machoListeners:
            threadCount = self.acceptThreadCount
            if 'machoNet' in eachTransport:
                threadCount = 1
            self.LogInfo('Launching ', threadCount, ' listen threads for transport ', eachTransport)
            for eachThread in range(0, threadCount):
                uthread.new(self.AcceptLoop, eachTransport).context = 'machoNet::AcceptLoop'


        self.acceptThreadCount = 20
        self.LogInfo('Restoring value of acceptThreadCount')
        if macho.mode == 'server' and self.connectToCluster:
            self.LogInfo('Connectivity[Startup]:  Establishing communications with proxy servers')
            layTracksTo = self._GetLayTracksTo()
            if not layTracksTo:
                self.LayTracksIfNeeded('127.0.0.1:%d' % (self.defaultProxyPortOffset + offsetMap['proxy']['tcp:packet:machoNet']), None, 'machoNet::Run')
            else:
                layTracksTo = list(layTracksTo)
                random.shuffle(layTracksTo)
                for each in layTracksTo:
                    self.LayTracksIfNeeded('%s:%d' % (each.ipAddress, each.port), each.nodeID, 'machoNet::Run')

        self.LogInfo('Creating handlers')
        machoNet = weakref.proxy(self)
        for each in gpcsMap[macho.mode]:
            nodes = []
            for d in gpcsMap[macho.mode][each]:
                nodes.append(CreateInstance(d))

            for i in range(0, len(nodes)):
                prior = machoNet
                next = None
                if i > 0:
                    prior = nodes[(i - 1)]
                if i + 1 < len(nodes):
                    next = nodes[(i + 1)]
                nodes[i].next = next
                nodes[i].prior = prior
                nodes[i].machoNet = machoNet

            for i in range(0, len(nodes)):
                current = nodes[i]
                while current is not None and current != machoNet:
                    if not hasattr(nodes[i], 'ForwardNotifyDown') and current.prior is not None and hasattr(current.prior, 'NotifyDown'):
                        nodes[i].ForwardNotifyDown = current.prior.NotifyDown
                    if not hasattr(nodes[i], 'ForwardCallDown') and current.prior is not None and hasattr(current.prior, 'CallDown'):
                        nodes[i].ForwardCallDown = current.prior.CallDown
                    current = current.prior

                current = nodes[i]
                while current is not None and current != machoNet:
                    if not hasattr(nodes[i], 'ForwardNotifyUp') and current.next is not None and hasattr(current.next, 'NotifyUp'):
                        nodes[i].ForwardNotifyUp = current.next.NotifyUp
                    if not hasattr(nodes[i], 'ForwardCallUp') and current.next is not None and hasattr(current.next, 'CallUp'):
                        nodes[i].ForwardCallUp = current.next.CallUp
                    current = current.next


            self.channelHandlersUp[each] = nodes[0]
            if not hasattr(self.channelHandlersUp[each], 'CallUp') and hasattr(self.channelHandlersUp[each], 'ForwardCallUp'):
                self.channelHandlersUp[each].CallUp = self.channelHandlersUp[each].ForwardCallUp
            if not hasattr(self.channelHandlersUp[each], 'NotifyUp') and hasattr(self.channelHandlersUp[each], 'ForwardNotifyUp'):
                self.channelHandlersUp[each].NotifyUp = self.channelHandlersUp[each].ForwardNotifyUp
            self.channelHandlersDown[each] = nodes[(len(nodes) - 1)]
            if not hasattr(self.channelHandlersDown[each], 'CallDown') and hasattr(self.channelHandlersDown[each], 'ForwardCallDown'):
                self.channelHandlersDown[each].CallDown = self.channelHandlersDown[each].ForwardCallDown
            if not hasattr(self.channelHandlersDown[each], 'NotifyDown') and hasattr(self.channelHandlersDown[each], 'ForwardNotifyDown'):
                self.channelHandlersDown[each].NotifyDown = self.channelHandlersDown[each].ForwardNotifyDown

        if macho.mode == 'server' and self.connectToCluster:
            uthread.new(self._MachoNetService__NodeWatcher).context = 'machoNet::NodeWatcher'
            uthread.new(self._MachoNetService__SessionStatWatcher).context = 'machoNet::SessionStatWatcher'
            uthread.new(self._MachoNetService__NodeLoadPush).context = 'machoNet::NodeLoadPush'
            uthread.new(self._MachoNetService__DisconnectUnauthorizedUsers).context = 'machoNet::DisconnectUnauthorizedUsers'
        elif macho.mode == 'proxy':
            uthread.new(self._MachoNetService__ClientSessionMaxTimePoll).context = 'machoNet::ClientSessionMaxTimePoll'
        uthread.new(self._MachoNetService__TimeoutCallLoop).context = 'machoNet::TimeoutCallLoop'
        uthread.new(self._MachoNetService__KATLoop).context = 'machoNet::KATLoop'
        self.acceptStart = blue.os.GetTime()
        self.stats = macho.MachoRunTimeStats()
        self.stats.Enable()
        self.LogNotice('MachoNet started with acceptDelay of %d seconds. I will accept connections at %s' % (self.acceptDelay, util.FmtDate(self.acceptStart + self.acceptDelay * const.SEC)))
        self.state = SERVICE_RUNNING
        for each in self.__gpcsmethodnames__:
            current = self.GetGPCS()
            while 1:
                if hasattr(current, each):
                    setattr(self, each, getattr(current, each))
                    break
                if not hasattr(current, 'prior') or current.prior is None:
                    self.LogError("MachoNet GPCS doesn't contain ", each, 'current=', current)
                    break
                current = current.prior


        if macho.mode == 'server' and self.connectToCluster:
            self.dbzclient = self.DB2.GetSchema('zclient')



    def OnClusterStarting(self, polarisNodeID):
        with self.clusterStartLock:
            if self.clusterStartupPhase:
                return 
            if macho.mode == 'proxy':
                uthread.new(self._MachoNetService__LoginQueueUpdater).context = 'machoNet::LoginQueueUpdater'
            if macho.mode == 'server' and (self.GetNodeID() == self.GetNodeFromAddress(const.cluster.SERVICE_POLARIS, 0) or self.IsResurrectedNode()):
                config = self.dbzcluster.Cluster_DowntimeInfo()
                if len(config):
                    when = config[0].shutdownWhen * const.MIN + blue.os.GetTime() / const.DAY * const.DAY
                    if when < blue.os.GetTime():
                        when += const.DAY
                    if self.IsResurrectedNode():
                        self.GracefulShutdown(config[0].shutdownUserID, when, 0, config[0].shutdownReason)
                    else:
                        self.session.ConnectToAllSolServerServices('machoNet').GracefulShutdown(config[0].shutdownUserID, when, 0, config[0].shutdownReason)
            for (transportID, transport,) in self.transportsByID.iteritems():
                nodeID = getattr(transport, 'nodeID', None)
                if nodeID is None:
                    log.LogTraceback('Transport with nodeID == None connected before OnClusterStarting')
                else:
                    isProxy = nodeID in self.transportIDbyProxyNodeID
                    isPolaris = nodeID == polarisNodeID
                    (address, serviceMask,) = self.externalAddressesByNodeID[nodeID]
                    sm.ScatterEvent('OnNewNode', nodeID, address, isProxy, isPolaris, serviceMask)

            sm.ScatterEvent('OnClusterStartup')
            self.clusterStartupPhase = True



    def OnNewNode(self, nodeID, nodeAddress, isProxy, isPolaris, serviceMask):
        if nodeID in self.deadNodes and isProxy:
            self.LogNotice('marking proxy node ', nodeID, ' at ', nodeAddress, ' as not dead anymore')
            del self.deadNodes[nodeID]
        self._LoadNodeToServiceMaskMapping(nodeID, serviceMask)
        if macho.mode == 'server':
            clientListener = self.GetTransport('tcp:packet:client')
            self.namedtransports['tcp:packet:client'] = None
            if clientListener is not None:
                clientListener.Close('The server has accepted a proxy connection, so it is closing all direct client connections.')
            hasSpewed = False
            for transportID in self.transportIDbyClientID.values():
                transportIDs = self.transportIDbyProxyNodeID.values() + self.transportIDbySolNodeID.values()
                if transportID not in transportIDs:
                    if transportIDs:
                        if not hasSpewed:
                            hasSpewed = True
                            self.LogError('Disconnecting a node->node connection!?!  Man do I smell deep shit going on here...')
                            self.LogError('Got a new node, and started iterating over transports to close them.')
                            self.LogError("Found a deadite that isn'it a known node->node transport.")
                            self.LogError('However, that is total crud, and we know it, because this is a sol server with proxy or sol connections.')
                            self.LogError("That means there are NO direct client connections, and we've got a situation here.")
                            self.LogError("Here's a stacktrace:")
                            log.LogTraceback()
                            self.LogError("And here's the new info we got:")
                            self.LogError('nodeID=', nodeID)
                            self.LogError('address=', nodeAddress)
                            self.LogError('isPolaris=', isPolaris)
                            self.LogError('I think I need an Alkaseltzer...')
                            self.LogError('self.transportsByID[transportID]=', self.transportsByID[transportID])
                    else:
                        self.transportsByID[transportID].Close('The server has established communications with a proxy server.  All direct communications are banned.')




    def OnTimeReset(self, oldTime, newTime):
        if self.acceptStart:
            delta = newTime - oldTime
            self.LogInfo('MachoNet (%s) acceptTime adjusted for DB time change' % macho.mode, self.acceptStart, delta, self.acceptStart + delta)
            self.acceptStart += delta
        else:
            self.LogInfo('MachoNet (%s) acceptTime not adjusted for DB time change (not used yet?)' % macho.mode)



    def ConnectivityTest(self, offset, proxyNodeCount, serverNodeCount):
        if offset is not None:
            if offset and not self.clockReset and macho.mode == 'proxy':
                now = blue.os.GetTime(1)
                newnow = now + offset
                print 'Correcting clock... advancing ',
                print float(offset) / float(const.SEC),
                print ' secs'
                blue.pyos.synchro.ResetClock(newnow)
                sm.ScatterEvent('OnTimeReset', now, newnow)
            self.clockReset = True
        if len(self.transportIDbySolNodeID) != serverNodeCount:
            self.LogInfo('ConnectivityTest Failed:  expected ', serverNodeCount, ' server nodes, found ', len(self.transportIDbySolNodeID))
        if len(self.transportIDbyProxyNodeID) != proxyNodeCount:
            self.LogInfo('ConnectivityTest Failed:  expected ', proxyNodeCount, ' proxy nodes, found ', len(self.transportIDbyProxyNodeID))
        return len(self.transportIDbySolNodeID) == serverNodeCount and len(self.transportIDbyProxyNodeID) == proxyNodeCount



    def OnObjectPublicAttributesUpdated(self, *args):
        pass



    def Stop(self, memStream = None):
        self.LogInfo('Stopping macho net node ', self.nodeID)
        self.stop = 1
        self.acceptStart = None
        if macho.mode == 'server':
            if self.nodeID is not None and sm.IsServiceRunning('DB2'):
                self.DB2.SetAllowSynchronousCalls(1)
                self.dbzcluster.Nodes_Trash(self.nodeID, 'The server is stopping', 1)
                self.DB2.SetAllowSynchronousCalls(0)
        while len(self.namedtransports):
            ls = self.namedtransports.values()
            self.namedtransports = {}
            for each in ls:
                if each is not None:
                    try:
                        each.disconnectsilently = getattr(each, 'disconnectsilently', 2)
                        each.Close('The machoNet service is stopping')
                    except StandardError:
                        log.LogException()
                        self.LogInfo('Exception during Close ignored.')
                        sys.exc_clear()


        while len(self.transportsByID):
            ls = self.transportsByID.values()
            self.transportsByID = {}
            for each in ls:
                try:
                    each.disconnectsilently = getattr(each, 'disconnectsilently', 2)
                    each.Close('The machoNet service is stopping')
                except StandardError:
                    log.LogException()
                    self.LogInfo('Exception during Close ignored.')
                    sys.exc_clear()


        self.transportIDbySolNodeID = {}
        self.transportIDbyAppNodeID = {}
        self.transportIDbyProxyNodeID = {}
        self.transportIDbyClientID = {}
        service.Service.Stop(self, memStream)



    def GetHtmlStateDetails(self, k, v, detailed):
        import htmlwriter
        wr = htmlwriter.HtmlWriter()
        if k == 'basePortNumber':
            return ('Base Port', v)
        if k == 'defaultTunnelPortOffset':
            return ('Default Tunneling Port', v)
        if k == '_addressCache':
            if detailed:
                nodeMap = self._addressCache.GetNodeAddressMap()
                hd = ['Node', 'Service', 'Addresses']
                li = []
                for node in sorted(nodeMap.keys()):
                    services = {}
                    for (service, address,) in nodeMap[node]:
                        if service in services:
                            services[service].append(address)
                        else:
                            services[service] = [address]

                    for service in sorted(services.keys()):
                        addresses = sorted(services[service])
                        li.append([node, service, ', '.join((str(addr) for addr in addresses))])


                return ('Address Cache', wr.GetTable(hd, li))
            else:
                return ('Address Cache', self._addressCache.GetSize())
        elif k == 'namedtransports':
            if detailed:
                hd = ['Name', 'GPS Transport']
                li = []
                for each in v.iterkeys():
                    li.append([each, v[each].__class__.__name__])

                return ('Named Transports', wr.GetTable(hd, li))
            else:
                r = ''
                comma = ''
                for each in v.iterkeys():
                    r = r + comma + each + '=' + v[each].__class__.__name__
                    comma = ', '

                return ('Named Transports', r)
        elif k == 'dontLayTracksTo':
            r = ''
            comma = ''
            for (each, at,) in v:
                r = r + comma + '%s at %s' % (each, at)
                comma = ', '

            return ('Currently Laying Tracks to, or have already laid tracks to ', r)
        if k == 'transportsByID':
            if detailed:
                hd = ['TRID',
                 'Type',
                 'Address',
                 'NodeID/<br>ClientID',
                 'Dependants',
                 'Sessions',
                 'Calls',
                 'RTT<br>(ms)',
                 'TDiff<br>(ms)']
                li = []
                for each in v.iterkeys():
                    if v[each].nodeID:
                        theID = v[each].nodeID
                    else:
                        theID = v[each].clientID
                    r = ''
                    comma = ''
                    for sess in v[each].sessions.iterkeys():
                        r = r + comma + strx(sess) + '=' + strx(v[each].sessions[sess][0].sid)
                        comma = ', '

                    if abs(v[each].estimatedRTT / const.MSEC) >= 100:
                        rtt = '%d' % (v[each].estimatedRTT / const.MSEC)
                    else:
                        rtt = '%-2.1f' % (v[each].estimatedRTT / const.MSEC)
                    if abs(v[each].timeDiff / const.MSEC) >= 100:
                        tdiff = '%d' % (v[each].timeDiff / const.MSEC)
                    else:
                        tdiff = '%-2.1f' % (v[each].timeDiff / const.MSEC)
                    li.append([each,
                     v[each].transportName,
                     v[each].transport.address,
                     theID,
                     strx(v[each].dependants),
                     htmlwriter.Swing(r),
                     strx(v[each].calls),
                     rtt,
                     tdiff])
                    li.sort()

                return ('Transports by ID', wr.GetTable(hd, li))
            else:
                r = ''
                comma = ''
                for each in v.iterkeys():
                    r = r + comma + strx(each) + '=' + strx(v[each].transport.address)
                    comma = ', '

                return ('Transports by ID', r)
        elif k == 'transportIDbyClientID':
            if detailed:
                hd = ['ClientID', 'TRID']
                li = []
                for each in v.iterkeys():
                    li.append([each, v[each]])

                return ('TransportID by ClientID', wr.GetTable(hd, li))
            else:
                r = ''
                comma = ''
                for each in v.iterkeys():
                    r = r + comma + strx(each) + '=>' + strx(v[each])
                    comma = ', '

                return ('TransportID by ClientID', r)
        elif k in ('channelHandlersUp', 'channelHandlersDown'):
            inout = 'Inbound'
            if k == 'channelHandlersDown':
                inout = 'Outbound'
            if detailed:
                hd = ['Channel', 'Handler']
                li = []
                for each in v.iterkeys():
                    li.append([each, v[each].__class__.__name__])

                return ('%s Channel Handlers' % inout, wr.GetTable(hd, li))
            else:
                r = ''
                comma = ''
                for each in v.iterkeys():
                    r = r + comma + strx(each) + '=>' + v[each].__class__.__name__
                    comma = ', '

                return ('%s Channel Handlers' % inout, r)
        elif k == 'transportIDbySolNodeID':
            if detailed:
                hd = ['Sol NodeID', 'TRID']
                li = []
                for each in v.iterkeys():
                    li.append([each, v[each]])

                return ('TransportID by Sol NodeID', wr.GetTable(hd, li))
            else:
                r = ''
                comma = ''
                for each in v.iterkeys():
                    r = r + comma + strx(each) + '=>' + strx(v[each])
                    comma = ', '

                return ('TransportID by Sol NodeID', r)
        elif k == 'transportIDbyProxy NodeID':
            if detailed:
                hd = ['Proxy NodeID', 'TRID']
                li = []
                for each in v.iterkeys():
                    li.append([each, v[each]])

                return ('TransportID by Proxy NodeID', wr.GetTable(hd, li))
            else:
                r = ''
                comma = ''
                for each in v.iterkeys():
                    r = r + comma + strx(each) + '=>' + strx(v[each])
                    comma = ', '

                return ('TransportID by Proxy NodeID', r)
        elif k == 'connectionLimit':
            return ('Max Connections', v)
        if k == 'callID':
            return ('Call ID', 'A running number used to identify blocking calls made on this server.  The current value is %d, so %d blocking calls have been made since the service was started.' % (v, v - 1))
        if k == 'transportID':
            return ('Transport ID', 'A running number used to identify transports connected to this server.  The current value is %d, so %d transports have been used by the service so far.' % (v, v - 1))
        if k == 'nodeID':
            return ('Node ID', 'For proxies and sol servers, a unique address that can be used for addressing packets to this server.  Value=%d' % v)
        if k == 'mode':
            return ('Macho Mode', 'Whether this is a client, server, or proxy.  Value=%s' % v)
        if k == 'stop':
            if v:
                v = 'The service is stopping, so it will be doing so.'
            else:
                v = 'The service is running, so it will leave them alone for now.'
            return ('Stop?', "Whether or not the service should shut down it's transports.  %s" % v)



    def __str__(self):
        return '<MachoNet Service>'



    def __repr__(self):
        return str(self)



    def IsConnected(self):
        if self.GetTransport('ip:packet:server') and not self.authenticating:
            return 1
        else:
            return 0



    def DisconnectFromServer(self):
        if macho.mode != 'client':
            raise AttributeError('The DisconnectFromServer method should only be called on the client')
        if self.namedtransports.has_key('ip:packet:server'):
            self.LogInfo('Closing connection to server')
            transport = self.namedtransports['ip:packet:server']
            transport.disconnectsilently = getattr(transport, 'disconnectsilently', 1)
            transport.Close('User disconnected', 'CLIENTDISCONNECTED')



    def GetServerStatus(self, address):
        if self.authenticating or self.gettingServerStatus or address.upper() == self.clientLogonQueue.address and blue.os.GetTime() - (self.clientLogonQueue.timestamp or blue.os.GetTime()) < self.clientLogonQueuePollTime * const.SEC:
            raise UserError('AlreadyConnecting')
        self.gettingServerStatus = 1
        try:
            try:
                transport = None
                if address in self.clientHalfBakedTransports:
                    transport = self.clientHalfBakedTransports[address]
                    del self.clientHalfBakedTransports[address]
                    if transport.IsClosed():
                        transport = None
                if transport is None:
                    factory = self.GetFactory(gpsMap[macho.mode]['tcp:packet:server'], (0, 'tcp:packet:server'))
                    transport = factory.Connect(address)
                serverInfo = transport.Authenticate(None, None)
                self.clientHalfBakedTransports[address] = transport
                return (lambda since = blue.os.GetTime(): sm.GetService('machoNet').GetOKMessage(since), serverInfo)
            except GPSBadAddress as e:
                sys.exc_clear()
                return (mls.MACHONET_GETSERVERSTATUS_BADADDRESS, {})
            except GPSTransportClosed as e:
                sys.exc_clear()
                if str(e.codename) != str(boot.codename) or e.reasonCode == 'HANDSHAKE_INCOMPATIBLERELEASE':
                    reason = mls.MACHONET_GETSERVERSTATUS_INCOMPATIBLE_RELEASE
                elif e.version != boot.version or e.reasonCode == 'HANDSHAKE_INCOMPATIBLEVERSION':
                    reason = mls.MACHONET_GETSERVERSTATUS_INCOMPATIBLE_VERSION
                elif e.machoVersion != macho.version or e.reasonCode == 'HANDSHAKE_INCOMPATIBLEPROTOCOL':
                    reason = mls.MACHONET_GETSERVERSTATUS_INCOMPATIBLE_PROTOCOL
                elif e.build != boot.build or e.reasonCode == 'HANDSHAKE_INCOMPATIBLEBUILD':
                    reason = mls.MACHONET_GETSERVERSTATUS_INCOMPATIBLE_BUILD
                elif str(e.region) != str(boot.region) or e.reasonCode == 'HANDSHAKE_INCOMPATIBLEREGION':
                    reason = mls.MACHONET_GETSERVERSTATUS_INCOMPATIBLE_REGION
                elif e.reasonCode == 'ACL_SHUTTINGDOWN':
                    reason = mls.MACHONET_GETSERVERSTATUS_SHUTTINGDOWN
                    when = blue.os.GetTime() + random.randrange(15, 60) * const.SEC
                    reason = lambda when = when, reason = reason: [None, reason][(blue.os.GetTime() < when)]
                elif e.reasonCode == 'ACL_NOTACCEPTING':
                    reason = mls.MACHONET_GETSERVERSTATUS_NOTACCEPTING
                    when = blue.os.GetTime() + random.randrange(60, 300) * const.SEC
                    reason = lambda when = when, reason = reason: [None, reason][(blue.os.GetTime() < when)]
                elif e.reasonCode == 'ACL_ACCEPTDELAY':
                    when = blue.os.GetTime() + (5 + e.reasonArgs['seconds']) * const.SEC
                    reason = lambda when = when: [None, mls.MACHONET_GETSERVERSTATUS_STARTINGUP % {'progress': util.FmtTimeInterval(when - blue.os.GetTime(), 'sec')}][(blue.os.GetTime() < when)]
                elif e.reasonCode == 'ACL_PROXYFULL':
                    if e.reasonArgs:
                        reason = mls.MACHONET_GETSERVERSTATUS_PROXYFULL + '(%d)' % e.reasonArgs['limit']
                    else:
                        reason = mls.MACHONET_GETSERVERSTATUS_PROXYFULL
                    when = blue.os.GetTime() + random.randrange(30, 120) * const.SEC
                    reason = lambda when = when, reason = reason: [None, reason][(blue.os.GetTime() < when)]
                elif e.reasonCode == 'ACL_PROXYNOTCONNECTED':
                    reason = mls.MACHONET_GETSERVERSTATUS_PROXYNOTCONNECTED
                    when = blue.os.GetTime() + random.randrange(30, 120) * const.SEC
                    reason = lambda when = when, reason = reason: [None, reason][(blue.os.GetTime() < when)]
                elif e.reasonCode == 'ACL_IPADDRESSBAN':
                    reason = mls.MACHONET_GETSERVERSTATUS_IPBANNED
                elif e.origin == 'client':
                    reason = mls.MACHONET_GETSERVERSTATUS_UNKNOWN
                    when = blue.os.GetTime() + random.randrange(60, 300) * const.SEC
                    reason = lambda when = when, reason = reason: [None, reason][(blue.os.GetTime() < when)]
                else:
                    reason = lambda since = blue.os.GetTime(): sm.GetService('machoNet').GetOKMessage(since)
                if e.origin == 'client':
                    return (reason, {})
                else:
                    return (reason, {'boot_version': getattr(e, 'version', None),
                      'boot_build': getattr(e, 'build', None),
                      'boot_codename': str(getattr(e, 'codename', None)),
                      'boot_region': str(getattr(e, 'region', None)),
                      'cluster_usercount': getattr(e, 'loggedOnUserCount', None),
                      'macho_version': getattr(e, 'machoVersion', None)})

        finally:
            self.gettingServerStatus = 0




    def GetValidClientCodeHash(self):
        if not hasattr(self, 'clientHash'):
            self.OnClientCodeUpdated()
        return getattr(self, 'clientHash')



    def ReloadClientCodeHash(self):
        clientUpdate = self.dbzclient.CodeHashes_Select(None, boot.build)
        if len(clientUpdate) > 1:
            self.LogError("Can't have more than one valid client code update")
            return 
        if len(clientUpdate) == 0:
            return 
        row = clientUpdate[0]
        return util.KeyVal(hash=row.hash, fileurl=row.fileUrl, build=row.build)



    def OnClientCodeUpdated(self):
        hs = self.session.ConnectToRemoteService('machoNet').ReloadClientCodeHash()
        setattr(self, 'clientHash', hs)



    def GetOKMessage(self, since):
        if self.clientLogonQueue.position == 1 and self.clientLogonQueue.reportedQueued:
            return mls.MACHONET_GETSERVERSTATUS_HEADOFQUEUE
        else:
            if self.clientLogonQueue.position > 1:
                if not self.gettingServerStatus and blue.os.GetTime() - max(self.clientLogonQueue.timestamp or since, since) > self.clientLogonQueuePollTime * const.SEC:
                    return None
                self.clientLogonQueue.reportedQueued = True
                return mls.MACHONET_GETSERVERSTATUS_INQUEUE % {'position': self.clientLogonQueue.position}
            return mls.MACHONET_GETSERVERSTATUS_OK



    def SetLogonQueuePosition(self, position):
        self.clientLogonQueue.position = position
        self.clientLogonQueue.timestamp = blue.os.GetTime()
        if position is None:
            self.clientLogonQueue.history = None
        elif self.clientLogonQueue.history is None:
            self.clientLogonQueue.history = util.KeyVal(initial=util.KeyVal(time=blue.os.GetTime(), pos=position), prev=util.KeyVal(time=blue.os.GetTime(), pos=position), last=util.KeyVal(time=blue.os.GetTime(), pos=position))
        else:
            self.clientLogonQueue.history.prev = self.clientLogonQueue.history.last
            self.clientLogonQueue.history.last = util.KeyVal(time=blue.os.GetTime(), pos=position)



    def GetPortOffsetStep(self, portTypeName):
        return offsetStep[portTypeName]



    def GetClientConfigVals(self):
        if boot.role != 'client' and self.clientConfigVals is None:
            with locks.TempLock('Getting the values, hold your horses', locks.RLock):
                if self.clientConfigVals is not None:
                    return self.clientConfigVals
                if boot.role == 'proxy':
                    self.clientConfigVals = self.session.ConnectToSolServerService('machoNet').GetClientConfigVals()
                else:
                    self.clientConfigVals = {k:v for (k, v,) in self.DB2.GetSchema('zsystem').ClientConfig_Select()}
                self.LogInfo('Got the following client config values:', self.clientConfigVals)
        elif boot.role == 'client' and self.clientConfigVals is None:
            return {}
        return self.clientConfigVals



    def UpdateClientConfigVals(self, clientConfigVals):
        self.clientConfigVals = clientConfigVals
        self.LogNotice('Got client config values:', clientConfigVals)
        sm.ScatterEvent('OnClientConfigValsChanged', clientConfigVals)



    def CalculatePortNumber(self, mapname, portTypeName):
        attributeName = 'default' + portTypeName[0].upper() + portTypeName[1:] + 'PortOffset'
        basePort = getattr(self, attributeName, None)
        if basePort:
            return basePort + offsetMap[portTypeName][mapname]
        raise StandardError('Unsupported role')



    def ConnectToAddress(self, address, mapname, destMachoRole, destinationNodeID = None, named = False, withReader = True, forcedPortNumber = None):
        port = forcedPortNumber or self.CalculatePortNumber(mapname, destMachoRole)
        address += ':' + str(port)
        factory = self.GetFactory(gpsMap[macho.mode][mapname], (0, mapname))
        transport = factory.Connect(address)
        transportID = self.transportID
        self.transportID = self.transportID + 1
        (discard, destTypeName,) = mapname.split(':', 1)
        ipDestTypeName = 'ip:' + destTypeName
        transport = macho.MachoTransport(transportID, transport, ipDestTypeName, self)
        self.transportsByID[transportID] = transport
        if named:
            self.namedtransports[ipDestTypeName] = transport
        transport._AssociateWithSession(forceNodeID=self.GetNodeID())
        blue.net.EnumerateTransport(transport.transport.socket.getSocketDescriptor(), transport.transportID, transport.transportName, 0, 0, self.GetNodeID())
        if withReader:
            self.StartTransportReader(transport)
        if destinationNodeID:
            self.transportIDbyAppNodeID[destinationNodeID] = transportID
        return transport



    def RegisterTransportIDForApplication(self, appNodeID, transportID):
        self.transportIDbyAppNodeID[appNodeID] = transportID



    def UnRegisterTransportIDForApplication(self, appNodeID):
        if appNodeID in self.transportIDbyAppNodeID:
            del self.transportIDbyAppNodeID[appNodeID]



    def StartTransportReader(self, transport):
        transport.currentReaders += 1
        uthread.new(self.TransportReader, transport).context = 'machoNet::Transport Reader::ConnectToAddress'



    def ConnectToServer(self, address, userName, password, sockettype = 'tcp'):
        if macho.mode != 'client':
            raise AttributeError('The ConnectToServer method should only be called on the client')
        if self.authenticating:
            raise UserError('AlreadyConnecting')
        if address.upper() == self.clientLogonQueue.address and self.clientLogonQueue.position > 1:
            raise UserError('AlreadyConnecting')
        loginProgressSteps = 5
        self.authenticating = 2
        try:
            self.clientSessionID += 1
            try:
                dirty = 0
                for each in session.__persistvars__:
                    if getattr(session, each) != session.GetDefaultValueOfAttribute(each):
                        self.LogError('Connecting with a dirty session.  ', each, ' was ', getattr(session, each), ' but should have been ', session.GetDefaultValueOfAttribute(each))
                        dirty = 1

                if dirty:
                    log.LogTraceback('Connecting with a dirty session')
                    raise UserError('DirtySession')
                self.LogInfo('Connecting to server ', address)
                if self.namedtransports.has_key('ip:packet:server'):
                    transport = self.namedtransports['ip:packet:server']
                    transport.disconnectsilently = getattr(transport, 'disconnectsilently', 1)
                    transport.Close('Reconnecting')
                transport = None
                try:
                    mapname = '%s:packet:server' % sockettype
                    sm.ChainEvent('ProcessLoginProgress', 'loginprogress::connecting', '', 1, loginProgressSteps)
                    transport = None
                    if address in self.clientHalfBakedTransports:
                        transport = self.clientHalfBakedTransports[address]
                        del self.clientHalfBakedTransports[address]
                        if transport.IsClosed():
                            transport = None
                    if transport is None:
                        factory = self.GetFactory(gpsMap[macho.mode][('%s:packet:server' % sockettype)], (0, mapname))
                        transport = factory.Connect(address)
                    sm.ChainEvent('ProcessLoginProgress', 'loginprogress::authenticating', '', 2, loginProgressSteps)
                    self.LogInfo('Authenticating user ', userName)
                    self.clientLogonQueue.address = address.upper()
                    self.clientLogonQueue.timestamp = None
                    self.clientLogonQueue.position = None
                    self.clientLogonQueue.reportedQueued = False
                    response = transport.Authenticate(userName, password)
                    if 'client_hash' in response:
                        try:
                            patchService = sm.StartServiceAndWaitForRunningState('patch')
                            patchService.CheckServerUpgradeInfo(response['client_hash'])
                        except:
                            log.LogException()
                            sys.exc_clear()
                    sm.GetService('objectCaching').LoadCache(transport.address)
                    transportID = self.transportID
                    self.transportID = self.transportID + 1
                    transport = macho.MachoTransport(transportID, transport, 'ip:packet:server', self)
                    self.transportsByID[transportID] = transport
                    self.namedtransports['ip:packet:server'] = transport
                    transport.currentReaders += 1
                    uthread.new(self.TransportReader, self.transportsByID[transportID]).context = 'machoNet::TransportReader::ConnectToServer'
                    transport.userID = response['session_init']['userid']
                    self.myProxyNodeID = response['proxy_nodeid']
                    transport._AssociateWithSession()
                    self.LogInfo('ConnectToServer established transport ', transport)
                    blue.net.EnumerateTransport(transport.transport.socket.getSocketDescriptor(), transport.transportID, transport.transportName, transport.userID, 0, 0)
                except UnMachoDestination as e:
                    sm.ScatterEvent('OnConnectionRefused', e.payload)
                    (exctype, exc, tb,) = sys.exc_info()
                    try:
                        raise UserError('OnConnectionRefused', {'what': e.payload}), None, tb

                    finally:
                        exctype = None
                        exc = None
                        tb = None

                except UserError as e:
                    if e.msg == 'AutLogonFailureTotalUsers':
                        if not transport.IsClosed():
                            self.clientHalfBakedTransports[address] = transport
                        self.SetLogonQueuePosition(e.dict.get('position', None))
                    sm.ScatterEvent('OnConnectionRefused', e.msg)
                    if e.msg != 'AuthenticationFailure':
                        log.LogTraceback()
                    raise 
                except GPSBadAddress as e:
                    sm.ScatterEvent('OnConnectionRefused', e.reason)
                    (exctype, exc, tb,) = sys.exc_info()
                    try:
                        raise UserError('OnConnectionBadAddress', {'what': e.reason}), None, tb

                    finally:
                        exctype = None
                        exc = None
                        tb = None

                except GPSTransportClosed as e:
                    (exctype, exc, tb,) = sys.exc_info()
                    try:
                        if e.reason == 'Connected transport closed':
                            sm.ScatterEvent('OnConnectionRefused', '')
                            raise UserError('OnConnectionFailed', {'what': 'The server was either not running or inaccessible'}), None, tb
                        else:
                            reason = e.reason
                            if getattr(e, 'reasonCode', None) and mls.HasLabel('MACHONET_TRANSPORTCLOSED_' + e.reasonCode):
                                reason = getattr(mls, 'MACHONET_TRANSPORTCLOSED_' + e.reasonCode) % e.reasonArgs
                            err = UserError('OnConnectionFailed', {'what': reason,
                             'exception': e})
                            if reason == 'AutLogonFailureTotalUsers':
                                if not transport.IsClosed():
                                    self.clientHalfBakedTransports[address] = transport
                                self.SetLogonQueuePosition(e.reasonArgs.get('position', None))
                            msg = reason
                            try:
                                msg = cfg.GetMessage(reason, e.reasonArgs, onNotFound='raise')
                                err = UserError(reason, e.reasonArgs)
                            except RuntimeError as e:
                                if not e.args or e.args[0] != 'ErrMessageNotFound':
                                    log.LogException()
                                sys.exc_clear()
                            except:
                                log.LogException()
                                sys.exc_clear()
                            sm.ScatterEvent('OnConnectionRefused', msg)
                            raise err, None, tb

                    finally:
                        exctype = None
                        exc = None
                        tb = None

                except StandardError:
                    self.LogInfo('ConnectToServer blew up big time')
                    log.LogException()
                    raise 
                (self.serviceInfo, initvals,) = self.RemoteServiceCall(session, self.myProxyNodeID, 'machoNet', 'GetInitVals')
                totalIntvals = len(initvals) + 1
                sm.ChainEvent('ProcessLoginProgress', 'loginprogress::gettingbulkdata', '', 3, totalIntvals)
                i = 4
                i = i + 1
                self.getCachedObjectHelperException = None
                for eachCachedDude in initvals.itervalues():
                    self._MachoNetService__GetCachedObjectHelper(eachCachedDude, i, loginProgressSteps + totalIntvals)
                    cachedObjects = sm.GetService('objectCaching').downloadedCachedObjects
                    objectID = eachCachedDude.GetObjectID()
                    if objectID in cachedObjects:
                        level = log.LGERR if blue.pyos.packaged else log.LGINFO
                        log.general.Log('Needed to downloaded bulk data %s to %s' % (objectID, cachedObjects[objectID]), level)
                    i = i + 1
                    sm.ChainEvent('ProcessLoginProgress', 'loginprogress::gettingbulkdata', '', i - 4, totalIntvals)

                if self.getCachedObjectHelperException:
                    transport.Close('Failed to acquire initial cache data')
                    raise UserError('OnConnectionFailed', {'what': 'Failed to acquire initial cache data.'})
                sm.ChainEvent('ProcessLoginProgress', 'loginprogress::done', '', i, loginProgressSteps + totalIntvals, response)

            finally:
                self.authenticating = 1

            sm.ChainEvent('ProcessInitialData', initvals)
            sm.ChainEvent('ProcessLoginProgress', 'loginprogress::processingInitialDataDone', '', i + 1, loginProgressSteps + totalIntvals)
            return response

        finally:
            self.authenticating = 0




    def __GetCachedObjectHelper(self, cachedDude, i = 1, total = 1):
        try:
            cachedDude.GetCachedObject()
        except StandardError:
            self.LogError('An exception occurred while getting an initial cached object')
            log.LogException()
            self.getCachedObjectHelperException = 1
            sys.exc_clear()



    def GetBasePortNumber(self):
        return self.basePortNumber



    def GetClusterSessionStatistics(self):
        return self.proxySessionStatistics_Return or self._GetEmptyProxySessionStatistics()



    def GetConnectionPropertiesAndTransferHTTPAuthorization(self, userID, auth):
        return (self.GetConnectionProperties(), sm.GetService('http').TransferAuthorization(userID, auth))



    def GetConnectionProperties(self):
        retval = {}
        if macho.mode == 'proxy':
            retval['vipMode'] = self.vipMode
            retval['limit'] = self.connectionLimit
            retval['maxLoginsPerMinute'] = self.maxLoginsPerMinute
            retval['pendingConnections'] = len(self.serverLogonQueue)
            retval['availableLoginSlots'] = self.availableLoginSlots
            retval['clients'] = len(self.transportIDbyClientID)
            retval['proxies'] = len(self.transportIDbyProxyNodeID)
            retval['servers'] = len(self.transportIDbySolNodeID)
            retval['solNodeIDs'] = self.transportIDbySolNodeID.keys()
            retval['proxyNodeIDs'] = self.transportIDbyProxyNodeID.keys()
            retval['espaddress'] = self.namedtransports['tcp:packet:client'].GetESPAddress()
            retval['externaladdress'] = self.namedtransports['tcp:packet:client'].GetExternalAddress()
            retval['internaladdress'] = self.namedtransports['tcp:packet:machoNet'].GetInternalAddress()
            retval['bannedIPs'] = self.bannedIPs
            retval['acceptDelay'] = self.acceptDelay
            retval['acceptStart'] = self.acceptStart
        elif macho.mode == 'client':
            retval['bytes_out'] = self.dataSent.Current()
            retval['bytes_in'] = self.dataReceived.Current()
            retval['packets_out'] = self.dataSent.Count()
            retval['packets_in'] = self.dataReceived.Count()
            retval['blocking_calls'] = self.blockingCallTimes.Count()
            retval['blocking_call_times'] = self.blockingCallTimes.Current()
            retval['calls_outstanding'] = len(self.calls)
        else:
            retval['limit'] = self.connectionLimit
            retval['maxLoginsPerMinute'] = self.maxLoginsPerMinute
            retval['proxiedclients'] = len(self.transportIDbyClientID)
            retval['proxies'] = len(self.transportIDbyProxyNodeID)
            retval['servers'] = len(self.transportIDbySolNodeID)
            retval['solNodeIDs'] = self.transportIDbySolNodeID.keys()
            retval['proxyNodeIDs'] = self.transportIDbyProxyNodeID.keys()
            retval['address'] = self.namedtransports['tcp:packet:machoNet'].GetExternalAddress()
            retval['acceptDelay'] = self.acceptDelay
        if macho.mode != 'client':
            retval['blue.os.pid'] = blue.os.pid
            (hd, li,) = blue.pyos.GetThreadTimes()
            created = li[hd.index('created')]
            kernel = li[hd.index('kernel')]
            user = li[hd.index('user')]
            cputime = kernel + user
            uptime = blue.os.GetTime() - created
            retval['blue.os.started'] = util.FmtDate(created)
            retval['blue.os.uptime'] = util.FmtTime(uptime)
            retval['blue.os.cpuload'] = self.GetCPULoad()
            retval['blue.os.cputime'] = util.FmtTime(cputime)
            retval['blue.os.kerneltime'] = util.FmtTime(kernel)
            retval['blue.os.usertime'] = util.FmtTime(user)
            retval['blue.os.ramReal'] = blue.win32.GlobalMemoryStatus()['TotalPhys'] - blue.win32.GlobalMemoryStatus()['AvailPhys']
            import blue.win32 as w32
            retval['blue.w32.PagefileUsage'] = w32.GetProcessMemoryInfo()['PagefileUsage']
        return retval



    def GetCPULoad(self):
        now = blue.os.GetTime()
        then = now - const.MIN * 5
        total = 0L
        lastTime = now
        i = len(blue.pyos.cpuUsage) - 1
        while i > 0 and blue.pyos.cpuUsage[i][0] >= then:
            total += blue.pyos.cpuUsage[i][1][1]
            lastTime = blue.pyos.cpuUsage[i][0]
            i -= 1

        if lastTime == now:
            return 0.0
        return min(100.0 * (float(total) / (float(now) - float(lastTime))), 100.0)



    def GetNetworkStats(self, socketServers):
        import _socket
        if not socketServers:
            stackless.set_schedule_callback(None)
            self.scheduleCount = 0
            return 
        if self.scheduleCount == 0:

            def ScheduleCounter(prev, next):
                self.scheduleCount += 1


            stackless.set_schedule_callback(ScheduleCounter)
        stats = _socket.getstats()
        headings = stats.keys()
        line = [ stats[k] for k in headings ]

        def replace(a, b):
            headings[headings.index(a)] = b


        replace('BytesReceived', 'bytesRecvd')
        replace('BytesSent', 'bytesSent')
        replace('PacketsSent', 'countWrites')
        replace('PacketsReceived', 'countReads')
        stats = {'global socket stats': [headings, line]}
        return util.KeyVal(stats=stats, scheduleCount=self.scheduleCount, taskletCount=len(bluepy.tasklets))



    def GetBlockingCallStats(self):
        min = self.callsCountMin
        max = self.callsCountMax
        self.callsCountMin = self.callsCountMax = len(self.calls)
        return (min, max)



    def SetConnectionProperty(self, k, v, doPersist = True):
        if k == 'limit':
            self.connectionLimit = v
        elif k in ('maxLoginsPerMinute', 'vipMode'):
            if doPersist:
                setattr(self, k, v)
            else:
                self.__dict__[k] = v
            if k == 'maxLoginsPerMinute':
                self.availableLoginSlots = min(self.availableLoginSlots, self.maxLoginsPerMinute)
        elif k == 'maxTrialUsers':
            self.maxTrialUsers = v
        elif k in ('bannedIPs', 'allowedIPs', 'useIPACL', 'acceptDelay'):
            if doPersist:
                setattr(self, k, v)
            else:
                self.__dict__[k] = v
        elif k == 'bannedIPs':
            self.bannedIPs = v
            bannz0red = []
            for (clientID, transportID,) in self.transportIDbyClientID.items():
                if transportID not in self.transportsByID:
                    continue
                transport = self.transportsByID[transportID]
                for bannedIP in v:
                    if transport.transport.address.startswith(bannedIP):
                        bannz0red.append(transport)
                        break


            for transport in bannz0red:
                transport.Close('Your IP address has been banned', 'ACL_IPADDRESSBAN', {'address': transport.transport.address.split(':')[0]})

        elif k == 'acceptDelay':
            self.acceptDelay = v



    def CheckACL(self, address, espCheck = False):
        if not espCheck and self.shutdown is not None:
            if self.shutdown.when < blue.os.GetTime():
                self.LogInfo('Rejecting connection from ', address, " because we're shutting down")
                return ('The cluster is shutting down', 'ACL_SHUTTINGDOWN')
            if self.shutdown.when - blue.os.GetTime() < 3 * const.MIN:
                self.LogInfo('Rejecting connection from ', address, " because we're shutting down in less than 3 minutes")
                return ('The cluster is shutting down in a few moments', 'ACL_SHUTTINGDOWN', {'when': (17, self.shutdown.when)})
        if not espCheck and self.acceptDelay and blue.os.GetTime() - self.acceptStart < const.SEC * self.acceptDelay:
            self.LogInfo('Rejecting connection from ', address, " because we're still starting and our accept delay hasn't passed")
            return ('Starting up...(%d sec.)' % (self.acceptDelay - (blue.os.GetTime() - self.acceptStart) / const.SEC), 'ACL_ACCEPTDELAY', {'seconds': self.acceptDelay - (blue.os.GetTime() - self.acceptStart) / const.SEC})
        if not self.clusterStartupPhase:
            if prefs.clusterMode in ('LIVE', 'TEST'):
                self.LogWarn('Accept Delay too low, the accept delay should represent the time from startup until the first user can connect')
            self.LogInfo('Rejecting connection from ', address, " because we're still starting")
            return ('Starting up...', 'ACL_ACCEPTDELAY', {'seconds': 0})
        if not self.transportIDbySolNodeID:
            self.LogInfo('Rejecting connection from ', address, ' because we do not have a sol server connection')
            return ('Proxy not connected', 'ACL_PROXYNOTCONNECTED')
        if espCheck:
            return 
        if self.connectionLimit == 0 or self.maxLoginsPerMinute == 0:
            self.LogInfo('Rejecting connection from ', address, " because we're not accepting any connections")
            return ('Not accepting', 'ACL_NOTACCEPTING')
        for each in self.bannedIPs:
            if address.startswith(each):
                self.LogInfo('Rejecting connection from ', address, ' because the IP address is banned by the ', each, ' rule')
                return ('Your IP address has been banned', 'ACL_IPADDRESSBAN', {'address': address.split(':')[0]})




    def GetSessionStatistics(self, userCount, clusterSessionStatistics):
        self.proxySessionStatistics.append(clusterSessionStatistics)
        if self.proxySessionStatistics_Return is None:
            self.proxySessionStatistics_Return = self._GetEmptyProxySessionStatistics()
        self.proxySessionStatistics_Return = self._CalculateSessionStatistics(clusterSessionStatistics)
        self.loggedOnUserCount = userCount
        self.loggedOnUserCountHistory.append((blue.os.GetTime(), userCount))
        if not hasattr(self, 'sessionMgr'):
            self.sessionMgr = self.session.ConnectToService('sessionMgr')
        return self.sessionMgr.GetSessionStatistics()



    def _GetEmptyProxySessionStatistics(self):
        return []



    def _CalculateSessionStatistics(self, clusterSessionStatistics):
        return self._GetEmptyProxySessionStatistics()



    def __SessionStatWatcher(self):
        allProxies = None
        while not getattr(self, 'stop', True):
            blue.pyos.synchro.Sleep(1000 * self.proxyStatPollInterval)
            try:
                if allProxies is None:
                    allProxies = self.session.ConnectToAllProxyServerServices('machoNet')
                self._MachoNetService__SessionStatWatcher2(allProxies)
            except StandardError:
                self.LogError('Exception during session stat stuff')
                log.LogException()
                sys.exc_clear()




    def __SessionStatWatcher2(self, allProxies):
        if self.GetNodeFromAddress(const.cluster.SERVICE_CLUSTERSESSIONINFO, 0) == self.GetNodeID():
            if self.transportIDbyProxyNodeID:
                ret = allProxies.GetSessionStatistics(len(self.clusterSessionStatistics.get('userid', {})), self.clusterSessionStatistics)
                summ = {}
                for eachProxy in ret:
                    if eachProxy[0] == 0:
                        statsFromThisProxy = eachProxy[2]
                        for (attribute, tup,) in statsFromThisProxy.iteritems():
                            if attribute not in summ:
                                summ[attribute] = {}
                            for (who, howmany,) in tup[1].iteritems():
                                if who not in summ[attribute]:
                                    summ[attribute][who] = howmany
                                else:
                                    summ[attribute][who] += howmany


                    else:
                        log.LogTraceback('Exception during proxy stat poll: %s' % str(eachProxy))
                        sys.exc_clear()
                        return 

                self.clusterSessionStatistics = summ
                try:
                    playerCount = len(sm.services['machoNet'].clusterSessionStatistics['userid'])
                    trialAccounts = sm.services['machoNet'].clusterSessionStatistics['userType'].get(23, 0)
                    self.dbzuser.OnlineCounts_Insert(playerCount, trialAccounts)
                except StandardError:
                    log.LogException()
                    sys.exc_clear()
                except:
                    log.LogException()
                    raise 



    def _GetLayTracksTo(self):
        with self.paonLock:
            if self.paon is None or blue.os.GetTime() - self.paon[1] > 5 * const.SEC:
                self.LogInfo('Connectivity[PAON]: Fetching node/proxy info')
                rowDescriptor = blue.DBRowDescriptor((('nodeID', const.DBTYPE_I4), ('ipAddress', const.DBTYPE_STR), ('port', const.DBTYPE_I4)))
                layTracksTo = dbutil.CRowset(rowDescriptor, [])
                proxies = self.dbzcluster.Proxies_Select()
                if not proxies and macho.mode == 'server':
                    ip = self.namedtransports['tcp:packet:machoNet'].GetExternalAddress().split(':')[0]
                    clientport = self.defaultProxyPortOffset + offsetMap[macho.mode]['tcp:packet:client']
                    serverport = self.defaultProxyPortOffset + offsetMap[macho.mode]['tcp:packet:machoNet']
                    proxyNodeID = self.GetIDOfAddress(ip + ':%d' % clientport, clientMode=False)
                    layTracksTo.InsertNew([proxyNodeID, ip, serverport])
                    self.LogWarn('Connectivity[PAON]:  Warning:  No proxy servers registered in DB, defaulting to localhost')
                for proxy in proxies:
                    if proxy.enabled == 1:
                        for i in xrange(proxy.nodeCount):
                            clientport = self.defaultProxyPortOffset + offsetMap[macho.mode]['tcp:packet:client'] + 1000 * i
                            serverport = self.defaultProxyPortOffset + offsetMap[macho.mode]['tcp:packet:machoNet'] + 1000 * i
                            proxyNodeID = self.GetIDOfAddress('%s:%d' % (proxy.ipAddress, clientport), clientMode=False)
                            if self.GetNodeID() != proxyNodeID:
                                self.LogInfo('Connectivity[PAON]: Laying tracks to self=', self.GetNodeID(), ' proxy=', proxyNodeID)
                                layTracksTo.InsertNew([proxyNodeID, proxy.ipAddress, serverport])


                for sol in self.dbzcluster.Nodes_SelectOthers(self.nodeID):
                    self.LogInfo('Connectivity[PAON]: Laying tracks to self=', self.GetNodeID(), ' sol=', sol.nodeID)
                    layTracksTo.InsertNew([sol.nodeID, sol.ipAddress, sol.port + offsetMap[macho.mode]['tcp:packet:machoNet']])

                self.paon = (layTracksTo, blue.os.GetTime())
            else:
                self.LogInfo('Connectivity[PAON]: Node/proxy info is up to date')
        self.LogInfo('Connectivity[PAON]: returning ', len(self.paon[0]), ' proxies and servers')
        return self.paon[0]



    def OnRefreshConnectivity(self):
        self.RefreshConnectivity()



    def RefreshConnectivity(self):
        if macho.mode == 'server':
            self.LogInfo('Connectivity[RefreshConnectivity]:  Refreshing communications with proxy servers')
            layTracksTo = self._GetLayTracksTo()
            if not layTracksTo:
                addresses = [('127.0.0.1:%d' % (self.defaultProxyPortOffset + offsetMap['proxy']['tcp:packet:machoNet']), None)]
            else:
                addresses = []
                for each in layTracksTo:
                    addresses.append(('%s:%d' % (each.ipAddress, each.port), each.nodeID))

            current = []
            for each in self.transportsByID.itervalues():
                current.append(each)

            for (node, addr,) in self.LayingTracksTo():
                self.LogInfo('Connectivity[RefreshConnectivity]:  Already laying tracks to node ', node, ' at ', addr)

            random.shuffle(addresses)
            for (address, nodeID,) in addresses:
                self.LayTracksIfNeeded(address, nodeID, 'RefreshConnectivity')

            self.LogInfo('Connectivity[RefreshConnectivity]:  End')
            return len(layTracksTo)



    def GracefulShutdown(self, userID, when, duration, explanation):
        if when:
            self.LogNotice('Graceful Shutdown requested by ', userID, ' to occur at ', util.FmtDate(when), ', duration ', duration or 0, ' minutes, explanation: ', explanation)
            if when < blue.os.GetTime() + const.HOUR:
                notify = blue.os.GetTime()
            else:
                notify = when - const.HOUR
            self.shutdown = util.KeyVal(notify=notify, userID=userID, when=when, duration=duration, explanation=explanation)
        else:
            self.LogNotice('Graceful Shutdown cancelled by ', userID, ', explanation: ', explanation)
            self.shutdown = None
            if self.GetNodeFromAddress(const.cluster.SERVICE_CLUSTERSESSIONINFO, 0) == self.GetNodeID():
                self.Broadcast('OnClusterShutdownCancelled', explanation)
                sm.ScatterEvent('OnClusterShutdownCancelled', explanation)
                self.dbzcluster.Broadcasts_Insert(userID, explanation)



    def __GracefulShutdownWorker(self):
        pollingInterval = 10
        while not getattr(self, 'stop', True):
            try:
                if self.shutdown is not None and self.GetNodeFromAddress(const.cluster.SERVICE_CLUSTERSESSIONINFO, 0) == self.GetNodeID():
                    self.LogInfo('GracefulShutdownWorker:  Probing')
                    now = blue.os.GetTime()
                    if self.shutdown.notify is not None:
                        self.LogInfo('GracefulShutdownWorker:  Checking Notification, now=', now, ', notify=', self.shutdown.notify)
                        sortOfNow = now + pollingInterval * 2 * const.SEC
                        if sortOfNow > self.shutdown.notify:
                            self.LogInfo('GracefulShutdownWorker:  Sending Notification')
                            msg = self.shutdown.explanation % {'when': util.FmtDate(self.shutdown.when, 'ns'),
                             'delay': util.FmtTimeInterval(self.shutdown.when - now, 'min', rounding=True)}
                            if self.shutdown.when - sortOfNow > 15 * const.MIN:
                                self.LogInfo('GracefulShutdownWorker:  Prepping 15 minute Notification')
                                self.shutdown.notify = self.shutdown.when - 15 * const.MIN
                            elif self.shutdown.when - sortOfNow > 5 * const.MIN:
                                self.LogInfo('GracefulShutdownWorker:  Prepping 5 minute Notification')
                                self.shutdown.notify = self.shutdown.when - 5 * const.MIN
                            else:
                                self.LogInfo('GracefulShutdownWorker:  Prepping actual shutdown')
                                self.shutdown.notify = None
                                if self.shutdown.duration:
                                    msg += '  See you again in ' + util.FmtTimeInterval(self.shutdown.duration * const.MIN, 'min')
                            self.Broadcast('OnClusterShutdownInitiated', msg, self.shutdown.when)
                            sm.ScatterEvent('OnClusterShutdownInitiated', msg, self.shutdown.when)
                            self.dbzcluster.Broadcasts_Insert(self.shutdown.userID, msg)
                    elif self.shutdown.when < now:
                        self.LogNotice('GracefulShutdownWorker:  Shutdown Initiated')
                        log.Quit = None
                        try:
                            self.session.ConnectToAllServices('machoNet').GracefulShutdownStarted()
                        except StandardError as e:
                            log.LogException('Exception in shutdown worker - GracefulShutdownStarted phase')
                            sys.exc_clear()
                        try:
                            self.session.ConnectToAllProxyServerServices('machoNet').TerminateClient('The cluster is shutting down')
                        except Exception:
                            log.LogException('Exception in shutdown worker - client disconnection phase')
                            sys.exc_clear()
                        sm.ChainEvent('ProcessClusterShutdown')
                        try:
                            self.session.ConnectToAllServices('machoNet').GracefulShutdownComplete()
                        except Exception:
                            log.LogException('Exception in shutdown worker - GracefulShutdownComplete phase')
                            sys.exc_clear()
                        if macho.mode == 'server':
                            self.dbzcluster.Nodes_Trash(self.nodeID, 'Graceful Cluster Shutdown - Master', 1)
                        blue.pyos.Quit('Graceful Cluster Shutdown')
            except Exception:
                log.LogException('Exception in shutdown worker')
                sys.exc_clear()
            blue.pyos.synchro.Sleep(pollingInterval * 1000)




    def IsClusterShuttingDown(self):
        return self.shutdownInProgress



    def GracefulShutdownStarted(self):
        self.LogNotice('Cluster shutdown started')
        self.shutdownInProgress = True
        if macho.mode == 'proxy':
            self.SetConnectionProperty('vipMode', True, doPersist=False)



    def GracefulShutdownComplete(self):
        self.LogNotice('Node', self.GetNodeID(), 'shutting down')
        sm.DumpBlueInfo()
        if prefs.GetValue('useProcessHealthLog', 0):
            sm.GetService('processHealth').WriteLog()
        if macho.mode == 'server' and self.GetNodeFromAddress(const.cluster.SERVICE_CLUSTERSESSIONINFO, 0) == self.GetNodeID():
            return 
        if macho.mode == 'server':
            self.dbzcluster.Nodes_Trash(self.nodeID, 'Graceful Cluster Shutdown - Slave', 1)
        uthread.worker('Shutdown thread', blue.pyos.Quit, 'Graceful Cluster Shutdown')



    def Shutdown(self, who):
        self.LogError('Shutdown requested by ', who, '.  Shutting down.')
        if macho.mode == 'server':
            self.dbzcluster.Nodes_Trash(self.nodeID, 'Shutdown called by %s' % who, 1)
        blue.pyos.Quit('Shutdown called by %s' % who)



    def TerminateUnconnectedNodes(self):
        if macho.mode == 'proxy':
            for each in self.nodeCPULoadValue.iterkeys():
                if each not in self.transportIDbySolNodeID:
                    self.LogNotice('Terminating unconnected node', each)
                    uthread.worker('machoNet::ServerBroadcast::OnNodeDeath', self.ServerBroadcast, 'OnNodeDeath', each, 1, "It's Terminate Unconnected Nodes' fault")




    def TerminateClient(self, reason, clientID = None):
        if macho.mode == 'proxy':
            if clientID is None:
                while self.transportIDbyClientID:
                    for clientID in self.transportIDbyClientID.keys():
                        self.TerminateClient(reason, clientID)


            else:
                transportID = self.transportIDbyClientID.get(clientID, None)
                if transportID is not None:
                    transport = self.transportsByID.get(transportID, None)
                    if transport is not None:
                        transport.Close(reason)



    def __NodeWatcher(self):
        connectionCount = -1
        while not getattr(self, 'stop', True):
            self.LogInfo('NodeWatcher:  Probing')
            try:
                if len(self.transportIDbyProxyNodeID) + len(self.transportIDbySolNodeID) != connectionCount or macho.mode == 'server' and not len(self.transportIDbyProxyNodeID) or macho.mode == 'proxy' and not len(self.transportIDbySolNodeID):
                    self.LogWarn("I think I've got a connectivity problem.  Attempting autorefresh.")
                    connectionCount = self.RefreshConnectivity()
                self.LogInfo('NodeWatcher:  Sleeping for ', self.nodeRefreshInterval, ' seconds')
            except Exception:
                log.LogException('Exception during NodeWatcher')
                sys.exc_clear()
            blue.pyos.synchro.Sleep(1000 * self.nodeRefreshInterval)




    def __LoginQueueUpdater(self):
        while not getattr(self, 'stop', True):
            self.availableLoginSlots = min(len(self.serverLogonQueue), self.availableLoginSlots) + self.maxLoginsPerMinute
            self.availableLoginSlots = min(self.availableLoginSlots, max(0, self.connectionLimit - len(self.transportIDbyClientID)))
            blue.pyos.synchro.Sleep(const.MIN / const.MSEC)




    def __ClientSessionMaxTimePoll(self):
        while not getattr(self, 'stop', True):
            self.LogInfo('ClientSessionMaxTimePoll:  Sleeping for ', self.clientSessionTimeoutGranularity, ' seconds')
            blue.pyos.synchro.Sleep(1000 * self.clientSessionTimeoutGranularity)
            try:
                transport = None
                s = None
                for transportID in self.transportIDbyClientID.values():
                    if transportID in self.transportsByID:
                        transport = self.transportsByID[transportID]
                        clientID = transport.clientID
                        if clientID in transport.sessions:
                            s = transport.sessions[clientID][0]
                            if s.maxSessionTime and s.maxSessionTime < blue.os.GetTime():
                                transport.Close('Game Time Expired', 'GAMETIMEEXPIRED')

            except Exception:
                log.LogException('Exception during __ClientSessionMaxTimePoll')
                sys.exc_clear()




    def __NodeLoadPush(self):
        while not getattr(self, 'stop', True):
            try:
                blue.pyos.synchro.Sleep(1000 * self.nodeLoadPush)
                if macho.mode == 'server' and self.GetNodeFromAddress(const.cluster.SERVICE_CLUSTERSESSIONINFO, 0) == self.GetNodeID():
                    cluGetNodes = self.dbzcluster.Nodes_Select()
                    self.nodeCPULoadValue = {}
                    for r in cluGetNodes:
                        self.nodeCPULoadValue[r.nodeID] = r.currentCpu or 0.0
                        self.serverNames[r.nodeID] = r.hostName or None

                    self.ClusterBroadcast('OnNodeLoadPush', self.nodeCPULoadValue, self.serverNames)
            except UnMachoDestination as e:
                self.LogWarn('UnMachoDestination (', e, ') while attempting to acquire load stats')
                sys.exc_clear()
            except StandardError:
                self.LogError('Exception while attempting to acquire load stats')
                log.LogException()
                sys.exc_clear()




    def __DisconnectUnauthorizedUsers(self):
        while not getattr(self, 'stop', True):
            try:
                blue.pyos.synchro.Sleep(1000 * self.disconnectUnauthorizedUsersPollInterval)
                if self.GetNodeFromAddress(const.cluster.SERVICE_CLUSTERSESSIONINFO, 0) == self.GetNodeID():
                    peopleWhoShouldntBeLoggedIn = self.dbzuser.OnlineUsers_SelectInactive()
                    if peopleWhoShouldntBeLoggedIn:
                        self.ProxyBroadcast('OnPeopleWhoShouldntBeLoggedInNotification', peopleWhoShouldntBeLoggedIn)
            except StandardError:
                self.LogError('Exception while attempting to disconnect unauthorized users')
                log.LogException()
                sys.exc_clear()




    def OnPeopleWhoShouldntBeLoggedInNotification(self, peopleWhoShouldntBeLoggedIn):
        lastPeopleWhoShouldntBeLoggedIn = self.peopleWhoShouldntBeLoggedIn
        self.peopleWhoShouldntBeLoggedIn = {}
        for (clientID, status,) in peopleWhoShouldntBeLoggedIn:
            if self.GetProxyNodeIDFromClientID(clientID) != self.GetNodeID():
                continue
            transportID = self.transportIDbyClientID.get(clientID, None)
            if transportID is not None:
                transport = self.transportsByID[transportID]
                if status in (5, 12, 13):
                    uthread.worker('machoNet::DelayedClose', self._MachoNetService__DelayedClose, transport, 'ACCOUNTBANNED')
                else:
                    uthread.worker('machoNet::DelayedClose', self._MachoNetService__DelayedClose, transport, 'ACCOUNTNOTACTIVE')
            elif clientID in lastPeopleWhoShouldntBeLoggedIn:
                self.LogOffClient(clientID)
            else:
                self.peopleWhoShouldntBeLoggedIn[clientID] = True




    def __DelayedClose(self, transport, message):
        clientID = transport.clientID
        self.SinglecastByClientID(clientID, 'OnServerMessage', getattr(mls, 'MACHONET_DELAYEDCLOSENOTIFICATION_' + message))
        blue.pyos.synchro.Sleep(self.disconnectUnauthorizedUsersDelayInterval * 1000)
        transport.Close(message, message)



    def OnNodeLoadPush(self, nodeCPULoadValue, serverNames):
        self.nodeCPULoadValue = nodeCPULoadValue
        self.serverNames = serverNames



    def GetNodeName(self, nodeID = None):
        if macho.mode == 'client':
            return 
        nodeID = nodeID or self.GetNodeID()
        if nodeID not in self.serverNames and not (stackless.getcurrent().block_trap or stackless.getcurrent().is_main):
            DB2 = self.session.ConnectToAnyService('DB2')
            try:
                for r in DB2.CallProc('zcluster.Nodes_Select'):
                    nodeID = r.nodeID
                    self.serverNames[nodeID] = r.hostName or None

                if nodeID not in self.serverNames:
                    self.serverNames[nodeID] = None
            except UserError as e:
                if e.msg != 'UnMachoDestination':
                    raise 
        if nodeID == self.GetNodeID() and self.serverNames.get(nodeID, None) is None:
            self.serverNames[nodeID] = blue.pyos.GetEnv().get('COMPUTERNAME', 'LOCALHOST')
        return self.serverNames.get(nodeID, None)



    class Sequencer(uthread.TaskletSequencer):

        def __init__(self, machoNet):
            uthread.TaskletSequencer.__init__(self)
            self.machoNet = machoNet



        def OnSleep(self, sequence):
            self.machoNet.LogInfo('Sequencer: Going to sleep, I am %d, expected %d, queue:%r' % (sequence, self.expected, self.queue))



        def OnWakeUp(self, sequence):
            self.machoNet.LogInfo('Sequencer: Waking up, I am %d, expected %d, queue:%r' % (sequence, self.expected, self.queue))



        def OnWakingUp(self, sequence, target):
            self.machoNet.LogInfo('Sequencer: Waking dude up, I am %d, dude %d, queue:%r' % (sequence, target, self.queue))




    def WaitForSequenceNumber(self, address, seq):
        if not seq or macho.mode != 'client':
            return 
        if address.addressType == const.ADDRESS_TYPE_NODE and address.nodeID:
            try:
                sequencer = self.seqwait[address.nodeID]
            except KeyError:
                sequencer = self.Sequencer(self)
                self.seqwait[address.nodeID] = sequencer
            if sequencer.IsClosed():
                self.LogError('Sequence Tasklet is closed in WaitForSequenceNumber')
            sequencer.Pass(seq)
        else:
            self.LogWarn('Unexpected source address type in wait for sequence number, address=', address)



    def OnNodeDeath(self, nodeID, confirmed, reason = None):
        if nodeID not in self.deadNodes:
            self.LogNotice('Node', self.nodeID, 'received OnNodeDeath for', nodeID, 'confirmed =', confirmed, 'reason =', reason)
            self._addressCache.RemoveAllForNode(nodeID)
            if confirmed:
                self._RemoveNodeFromServiceMaskMapping(nodeID)
                self.deadNodes[nodeID] = 1
                if macho.mode == 'server':
                    if self.nodeID == int(nodeID):
                        self.dbzcluster.Nodes_Trash(self.nodeID, 'Some (proxy) sent me an OnNodeDeath for my own nodeID', 1)
                        log.Quit('Some (proxy) sent me an OnNodeDeath for my own nodeID')
                    else:
                        self.dbzcluster.Nodes_Trash(int(nodeID), 'Killed by node %s, because: %s' % (self.nodeID, reason))
                transport = self.GetTransportOfNode(nodeID)
                if transport is not None:
                    transport.Close(reason=reason, noSend=True)



    def LayTracksIfNeeded(self, address, nodeID, whencemsg):
        if self.DontLayTracksTo(nodeID):
            return 
        self.LogInfo('Connectivity[%s]:  ' % whencemsg, self.nodeID, ' laying tracks to ', nodeID, ' at ', address)
        uthread.worker('machoNet::LayTracksIfNeeded', self.LayTracks, address, nodeID, whencemsg)



    def DontLayTracksTo(self, nodeID):
        if nodeID == self.nodeID:
            return True
        if nodeID in self.transportIDbySolNodeID or nodeID in self.transportIDbyProxyNodeID:
            return True
        if nodeID in self.dontLayTracksTo:
            return True
        return False



    def LayingTracksTo(self):
        return self.dontLayTracksTo.items()



    def LayTracks(self, address, nodeID, whence):
        if self.DontLayTracksTo(nodeID):
            return 
        logname = 'Connectivity[LayTracks tid = %s, %s]:' % (id(stackless.getcurrent()), whence)
        self.LogInfo(logname, 'start', repr(address), 'nodeID=', nodeID)
        self.dontLayTracksTo[nodeID] = address
        try:
            if nodeID == self.GetNodeID():
                self.LogError(logname, 'Trying to lay tracks to self!')
                log.LogTraceback()
                return 
            if self.nodeID is None:
                self.LogError(logname, 'Cannot lay tracks before we have a node ID.  Sleeping...')
                while self.nodeID is None:
                    blue.pyos.synchro.Sleep(100)

                self.LogInfo(logname, 'Woke up, have nodeID', self.nodeID)
            if False:
                nodeType = self.GetNodeTypeFromID(nodeID)
                if nodeType == macho.mode and nodeID <= self.nodeID:
                    self.LogInfo(logname, 'Not laying tracks to a higher ranking node (%d to %d), expecting incoming connection.' % (self.nodeID, nodeID))
                    return 
                if nodeType == 'server' and macho.mode == 'proxy':
                    self.LogInfo(logname, 'Not laying tracks from proxy to server, expecting incoming connection.')
                    return 
            try:
                factory = self.GetFactory(gpsMap[macho.mode]['tcp:packet:machoNet'], (0, 'tcp:packet:machoNet'))
                self.LogInfo(logname, 'Attempting connect to ', repr(address))
                transport = factory.Connect(address)
                self.LogInfo(logname, 'Connect succeeded! [%r->%r]' % (transport.localaddress, transport.address))
                try:
                    transportID = self.transportID
                    self.transportID = self.transportID + 1
                    transport = macho.MachoTransport(transportID, transport, 'tcp:packet:machoNet', self)
                    others = []
                    if macho.mode == 'server':
                        layTracksTo = self._GetLayTracksTo()
                        for each in layTracksTo:
                            others.append(('%s:%d' % (each.ipAddress, each.port), each.nodeID))

                        myaddress = self.GetTransport('tcp:packet:machoNet').GetExternalAddress()
                    else:
                        myaddress = self.GetTransport('tcp:packet:machoNet').GetInternalAddress()
                    self.LogInfo(logname, 'sending idrq to node', nodeID, 'at', address)
                    transport.Write(macho.IdentificationReq(nodeID=self.nodeID, source=macho.MachoAddress(nodeID=self.nodeID), myaddress=myaddress, others=others, isProxy=macho.mode == 'proxy', isApp=False, serviceMask=self.serviceMask))
                    response = transport.Read()
                    self.LogInfo(logname, 'got response to idrq from', nodeID, 'at', address)
                    if response.command != MACHONETMSG_TYPE_IDENTIFICATION_RSP:
                        raise RuntimeError('UnexpectedResponse', 'Got a bad response to IdentificationReq')
                    if nodeID and response.nodeID != nodeID:
                        self.LogError(logname, 'I thought I was connecting to ', nodeID, ', but got a response from ', response.nodeID)
                        log.LogTraceback('Got a misguided response to IdentificationReq (expected: %s, actual: %s)' % (nodeID, response.nodeID))
                        raise RuntimeError('UnexpectedResponse', 'Got a misguided response to IdentificationReq')
                    (accepted, reason,) = response.accepted
                    if not accepted:
                        self.LogInfo(logname, response.nodeID, ' rejected connection: ', repr(reason))
                        transport.Close('%s rejected connection: %r.' % (response.nodeID, reason), noSend=True)
                    elif response.nodeID in self.transportIDbyProxyNodeID or response.nodeID in self.transportIDbySolNodeID:
                        self.LogError(logname, "I've already got a connection established to ", response.nodeID, ".  Two's a crowd in this case.  Ciao.")
                        transport.Close("I've already got a connection established to %s." % response.nodeID)
                    else:
                        self.LogInfo(logname, 'Succesfully established a connection to ', response.nodeID, ' reason: ', repr(reason))
                        transport.nodeID = response.nodeID
                        if response.isProxy:
                            self.transportIDbyProxyNodeID[transport.nodeID] = transportID
                        else:
                            self.transportIDbySolNodeID[transport.nodeID] = transportID
                        self.transportsByID[transportID] = transport
                        transport.currentReaders += 1
                        uthread.worker('machoNet::TransportReader::LayTracks', self.TransportReader, self.transportsByID[transportID])
                        self.externalAddressesByNodeID[response.nodeID] = (address, response.serviceMask)
                        if self.clusterStartupPhase:
                            if boot.role == 'proxy':
                                polarisID = self.session.ConnectToSolServerService('machoNet').GetNodeFromAddress(const.cluster.SERVICE_POLARIS, 0)
                            else:
                                polarisID = self.GetNodeFromAddress(const.cluster.SERVICE_POLARIS, 0)
                            isPolaris = response.nodeID == polarisID
                            sm.ScatterEvent('OnNewNode', response.nodeID, address, response.isProxy, isPolaris, response.serviceMask)
                        blue.net.EnumerateTransport(transport.transport.socket.getSocketDescriptor(), transport.transportID, transport.transportName, 0, 0, transport.nodeID)
                    others = response.others
                    for (otherAddress, otherNodeID,) in others:
                        self.LayTracksIfNeeded(otherAddress, otherNodeID, 'LayTracks::response.others')

                except GPSTransportClosed as e:
                    transport.Close(e.reason)
                    raise 
                except Exception:
                    log.LogException()
                    transport.Close('LayTracks blew up')
            except GPSTransportClosed as e:
                ps = 'proxy' if macho.mode != 'proxy' else 'server'
                self.LogWarn(logname, 'Failed to connect to ', ps, ' on ', address, repr(e))
            except Exception:
                log.LogException()

        finally:
            del self.dontLayTracksTo[nodeID]
            self.LogInfo(logname, 'End')




    def RegisterXmlRpc(self):

        def GracefulShutdownWrapper(whenMinutes, duration, explaination):
            userID = 0
            when = whenMinutes * MIN + blue.os.GetTime()
            self.session.ConnectToAllSolServerServices('machoNet').GracefulShutdown(userID, when, duration, explaination)
            return True


        sm.services['xmlrpcService'].Register(ROLE_ADMIN, GracefulShutdownWrapper, 'machoNet', 'GracefulShutdown')

        def IsReady():
            return self.clusterStartupPhase


        sm.services['xmlrpcService'].Register(ROLE_ANY, IsReady, 'machoNet')

        def SetVIPMode(onoff):
            s = self.session.ConnectToAllProxyServerServices('machoNet')
            s.SetConnectionProperty('vipMode', onoff)
            return self.vipMode


        sm.services['xmlrpcService'].Register(ROLE_ADMIN, SetVIPMode, 'machoNet')

        def SetProxyConnectionLimit(limit):
            s = self.session.ConnectToAllProxyServerServices('machoNet')
            s.SetConnectionProperty('limit', limit)
            return self.connectionLimit


        sm.services['xmlrpcService'].Register(ROLE_ADMIN, SetProxyConnectionLimit, 'machoNet')



    def _MapServiceNameToServiceID(self, serviceName):
        if serviceName in self.serviceMappings:
            serviceID = self.serviceMappings[serviceName][0]
            return serviceID
        return serviceName



    def SetNodeOfAddress(self, service, address, nodeID):
        if nodeID is None:
            self._addressCache.Remove(service, address)
        else:
            self._addressCache.Set(service, address, nodeID)



    def CheckAddressCache(self, service, address, lazyGetIfNotFound = False):
        (suggestedNodeID, service, address,) = self._GetNodeFromAddressAdjustments(service, address)
        if isinstance(service, str):
            calledBy = log.WhoCalledMe()
            if calledBy not in self.getNodeFromAddressWarnsDone:
                self.LogWarn('Passing a string(', service, ') serviceID into CheckAddressCache, will be mapped to a int internally. Please update the usage at:', calledBy)
                self.getNodeFromAddressWarnsDone[calledBy] = 1
            serviceID = self._MapServiceNameToServiceID(service)
            if serviceID:
                service = serviceID
        nodeID = self._addressCache.Get(service, address)
        if not nodeID and lazyGetIfNotFound:
            uthread.new(self.GetNodeFromAddress, service, address)
        return nodeID



    @bluepy.TimedFunction('machoNet::GetNodeFromAddress')
    def GetNodeFromAddress(self, serviceID, address, justQuery = 0):
        if justQuery == 1:
            justQuery = 0
        if justQuery != 0:
            log.LogTraceback('Someone is calling GetNodeFromAddress with a silly justQuery value', justQuery)
        (suggestedNodeID, serviceID, address,) = self._GetNodeFromAddressAdjustments(serviceID, address)
        if isinstance(serviceID, str):
            calledBy = log.WhoCalledMe()
            if calledBy not in self.getNodeFromAddressWarnsDone:
                self.LogWarn('Passing a string(', serviceID, ') serviceID into GetNodeFromAddress, will be mapped to a int internally. Please update the usage at:', calledBy)
                self.getNodeFromAddressWarnsDone[calledBy] = 1
            serviceID = self._MapServiceNameToServiceID(serviceID)
            if not serviceID:
                log.LogTraceback(extraText='Received a servicename into GetNodeFromAddress which did no map to a valid servicemask:' + str(serviceID))
        if address is None:
            raise RuntimeError('GetNodeFromAddress only works if you specify an address...')
        key = (serviceID, address)
        while 1:
            nodeID = self._addressCache.Get(serviceID, address)
            if nodeID is None:
                myNodeID = self.nodeID
                if not self.connectToCluster:
                    myNodeID = -1
                uthread.Lock(self, serviceID, address)
                try:
                    nodeID = self._addressCache.Get(serviceID, address)
                    if nodeID is None:
                        borkPrevention = 10
                        serviceMask = self.serviceMaskByServiceID[serviceID]
                        for i in xrange(100):
                            if serviceMask not in self.expectedLoadValue:
                                uthread.Lock(self, 'CluGetExpectedLoadValue')
                                try:
                                    self.expectedLoadValue[serviceID] = self.dbzcluster.LoadStats_ExpectedLoadValue(serviceID)

                                finally:
                                    uthread.UnLock(self, 'CluGetExpectedLoadValue')

                            nodeID = self._GetNodeFromAddressFromDB(myNodeID, serviceID, int(address), suggestedNodeID, self.expectedLoadValue[serviceID], serviceMask)
                            if nodeID <= 0:
                                if nodeID == -1:
                                    self.LogError('zcluster.Cluster_NodeFromAddress informed us that an app lock timeout occurred')
                                    self.LogError('Sleeping and retrying.  This is very bad.')
                                    blue.pyos.synchro.Sleep(15000)
                                    continue
                                elif nodeID == -2:
                                    self.LogError("zcluster.Cluster_NodeFromAddress informed us that we're dead")
                                    log.LogTraceback()
                                    blue.pyos.synchro.Sleep(60000)
                                    self.dbzcluster.Nodes_Trash(self.nodeID, "zcluster.Cluster_NodeFromAddress informed us that we're dead", 1)
                                    log.Quit("zcluster.Cluster_NodeFromAddress informed us that we're dead")
                                elif nodeID == -3:
                                    if borkPrevention > 0:
                                        self.LogWarn('Cluster Segmentation Initial Fragmentation Prevention for ', key, ':  Sleeping for ', 1 + self.heartbeatInterval / 10, ' seconds to allow other segments to pass the safety time.')
                                        blue.pyos.synchro.Sleep(1000 * (1 + self.heartbeatInterval / 10))
                                        borkPrevention = borkPrevention - 1
                                        continue
                                    if borkPrevention == 0:
                                        log.LogTraceback("Couldn't allocate address on any server.  Cluster borked beyond recognition.  Performing emergency cluster desegmentation.")
                                        self.dbzcluster.Cluster_Desegmentation()
                                        self.ClusterBroadcast('OnClusterDesegmentation')
                                        continue
                                    else:
                                        log.LogTraceback("Couldn't allocate address on any server after desegmentification.  Cluster borked beyond recognition.")
                                        raise RuntimeError('The address you asked for could not be allocated on any server.  This cluster must be seriously borked, to say the least...')
                                elif nodeID == -4:
                                    self.LogWarn('zcluster.Cluster_NodeFromAddress informed us that the address we requested (', serviceID, ',', address, ") was recently mapped on a node that has not yet acknowledged it's death")
                                    self.LogWarn('Sleeping and retrying.')
                                    blue.pyos.synchro.Sleep(15000)
                                    continue
                                else:
                                    self.LogError('zcluster.Cluster_NodeFromAddress went haywire')
                                    log.LogTraceback('Bork Bork in zcluster.Cluster_NodeFromAddress')
                                    self.dbzcluster.Nodes_Trash(self.nodeID, 'zcluster.Cluster_NodeFromAddress went haywire and returned an illegal value', 1)
                                    log.Quit('zcluster.Cluster_NodeFromAddress went haywire and returned an illegal value')
                            if nodeID == 0:
                                log.LogTraceback('zcluster.Cluster_NodeFromAddress returned 0???')
                                nodeID = None
                            if nodeID is not None:
                                self._addressCache.Set(serviceID, address, nodeID)
                                break
                            else:
                                log.LogTraceback('zcluster.Cluster_NodeFromAddress returned 0 or None???  Entering bork-prevention loop')
                                blue.pyos.synchro.Sleep(5000)

                        if nodeID is None:
                            log.LogTraceback('Failing to acquire a nodeID for address (%s).  Raising.' % strx(key))
                            raise RuntimeError('GetNodeFromAddress failed to acquire a nodeID for the address (1)')

                finally:
                    uthread.UnLock(self, serviceID, address)

                if nodeID is None and not justQuery:
                    raise RuntimeError("Couldn't resolve %s:%s to a node" % (serviceID, address))
            if nodeID is None:
                log.LogTraceback('Failed to acquire a nodeID for address (%s).  Raising.' % strx(key))
                raise RuntimeError('GetNodeFromAddress failed to acquire a nodeID for the address (2)')
            if nodeID in self.deadNodes:
                self.LogError('Tried to return a dead mapping: Dead Node ', nodeID, ' has been registered in the address cache for ', key)
                self._addressCache.Remove(serviceID, address)
                blue.pyos.synchro.Sleep(3000)
            else:
                break

        return nodeID



    def ClearNodeOfAddresses(self, addresses):
        totalCleared = 0
        for (service, address,) in addresses:
            try:
                self.LogWarn('ClearNodeOfAddresses: clearing (', service, ', ', address, ')')
                uthread.Lock(self, service, address)
                self.SetNodeOfAddress(service, address, None)
                totalCleared += 1

            finally:
                uthread.UnLock(self, service, address)


        return totalCleared



    def GetFullAddressCache(self):
        return self._addressCache.GetNodeAddressMap()



    def OnClusterDesegmentation(self):
        self.LogWarn('Cluster desegmentation')
        for nodeID in self.transportIDbySolNodeID.iterkeys():
            self._LoadNodeToServiceMaskMapping(nodeID, const.cluster.SERVICE_ALL)

        if macho.mode == 'server':
            self.serviceMask = const.cluster.SERVICE_ALL



    def _RemoveNodeFromServiceMaskMapping(self, nodeID):
        self.LogInfo('Removing servicemask mapping to nodeID', nodeID)
        for mapping in self.nodeIDsByServiceMask.itervalues():
            mapping.discard(nodeID)




    def _LoadNodeToServiceMaskMapping(self, nodeID, serviceMask):
        if serviceMask is None:
            serviceMask = const.cluster.SERVICE_ALL
        self.LogInfo('Loading node to service mask mapping for nodeID', nodeID, 'serviceMask=', serviceMask)
        for bit in util.extractBits(serviceMask):
            self.nodeIDsByServiceMask[bit].add(nodeID)




    def _GetNodeFromAddressFromDB(self, myNodeID, serviceMapping, address, suggestedNodeID, expectedLoadValue, serviceMask):
        return self.dbzcluster.Cluster_NodeFromAddress(myNodeID, serviceMapping, address, suggestedNodeID, expectedLoadValue, serviceMask)



    def GuessNodeIDFromAddress(self, serviceName, address):
        return None



    def _GetNodeFromAddressAdjustments(self, service, address):
        return (None, service, address)



    def PrimeAddressCache(self, allMappings):
        mapped = 0
        for each in allMappings:
            if each.nodeID not in self.deadNodes:
                serviceID = self._MapServiceNameToServiceID(each.serviceName)
                if self._addressCache.Set(serviceID or each.serviceName, each.addressID, each.nodeID):
                    mapped += 1

        if mapped:
            self.LogInfo('PrimeAddressCache mapped %d new addresses' % mapped)



    def ClearAddressCache(self):
        self._addressCache.Clear()



    def RemoveAllForNode(self, nodeId):
        self._RemoveNodeFromServiceMaskMapping(nodeId)
        self._addressCache.RemoveAllForNode(nodeId)



    def HandleUnMachoDestination(self, nodeID, packet):
        self._addressCache.Clear()
        if not self.IsClusterShuttingDown():
            self._RemoveNodeFromServiceMaskMapping(nodeID)
            self.LogWarn('UnMachoDestination received.  Performing node death handling for packet=', packet)
            self.ServerBroadcast('OnNodeDeath', nodeID, 0)



    def AreTheseServicesRunning(self, requiredServices):
        for required in requiredServices:
            if required not in sm.services:
                self.LogInfo('AreTheseServicesRunning:  Waiting for %s to initiate startup' % required)
                return required

        for s in sm.services.itervalues():
            if s.state == service.SERVICE_FAILED:
                self.LogInfo('AreTheseServicesRunning:  %s was SERVICE_FAILED' % s.__guid__)
                if s.__error__:
                    raise s.__error__[1], None, s.__error__[2]
                else:
                    raise RuntimeError, 'Service %s failed' % s.__guid__
            if s.state != service.SERVICE_RUNNING:
                self.LogInfo('AreTheseServicesRunning:  Waiting for %s' % s.__guid__)
                return s.__guid__.split('.')[1]
            for dependant in s.__dependencies__:
                if dependant not in sm.services:
                    self.LogInfo('AreTheseServicesRunning:  Waiting for %s, which is a dependant of %s, to initiate startup' % (dependant, s.__guid__.split('.')[1]))
                    return dependant


        if 'config' in requiredServices:
            import __builtin__
            if 'const' not in dir(__builtin__):
                self.LogInfo('AreTheseServicesRunning:  const not in builtin')
                return 'config::const'
            if 'cfg' not in dir(__builtin__):
                self.LogInfo('AreTheseServicesRunning:  cfg not in builtin')
                return 'config::cfg'



    def GetMyAddresses(self, addressType):
        return self.dbzcluster.Addresses_SelectServiceNode(self.serviceMappings[addressType][0], self.nodeID)



    def GetNodeID(self):
        if not hasattr(self, 'nodeID'):
            return 
        if macho.mode == 'server':
            while self.nodeID is None:
                self.LogError("Some dude is trying to get our nodeID before we're up and running...  Can't have that, now can we?  Let's sleeping on it.")
                log.LogTraceback()
                blue.pyos.synchro.Sleep(1000)

        return self.nodeID



    def GetNodeTypeFromID(self, nodeID):
        if nodeID >= const.maxNodeID:
            return 'proxy'
        else:
            return 'server'



    def GetClientSessionID(self):
        if macho.mode == 'client':
            return (self.clientSessionID, session.userid)
        return 0



    def GetMachoTransportByClientID(self, clientID):
        return self.transportsByID.get(self.transportIDbyClientID.get(clientID, None), None)



    def GetSessionByClientID(self, clientID):
        transport = self.GetMachoTransportByClientID(clientID)
        if transport is None:
            return 
        else:
            return transport.sessions.get(clientID, [None])[0]



    def GetConnectedProxyNodes(self):
        return self.transportIDbyProxyNodeID.keys()



    def GetConnectedSolNodes(self):
        return self.transportIDbySolNodeID.keys()



    def GetConnectedNodes(self):
        return self.GetConnectedProxyNodes() + self.GetConnectedSolNodes()



    def GetTransportOfNode(self, nodeID):
        transportID = self.transportIDbyProxyNodeID.get(nodeID, None) or self.transportIDbySolNodeID.get(nodeID, None) or self.transportIDbyAppNodeID.get(nodeID, None)
        return self.transportsByID.get(transportID, None)



    def GetMachoTransportsByTransportIDs(self, ids):
        retval = []
        for each in ids:
            if self.transportsByID.has_key(each):
                retval.append(self.transportsByID[each])

        return retval



    def GetTransport(self, transportName):
        return self.namedtransports.get(transportName, None)



    def GetTransportIDByTransport(self, transport):
        for (transportID, machoTransport,) in self.transportsByID.iteritems():
            if transport is machoTransport.transport:
                return transportID




    def OnHeartBeat(self):
        while not getattr(self, 'stop', True):
            blue.pyos.synchro.Sleep(int(self.heartbeatInterval * 1000))
            if self.nodeID is not None and (self.shutdown is None or self.shutdown.when > blue.os.GetTime()):
                try:
                    secs = self.dbzcluster.Nodes_HeartBeat(self.nodeID)
                    if self.debugHeartBeat:
                        self.LogNotice('Node', self.nodeID, 'Done sending Heartbeat @ ', util.FmtDate(blue.os.GetTime()), ' result ', repr(secs))
                except StandardError:
                    self.LogError('!! ---------------------------------------------------------- !!')
                    self.LogError('Oh my God!  An exception during zcluster.Nodes_HeartBeat!!!')
                    self.LogError('!! ---------------------------------------------------------- !!')
                    log.LogException()
                    try:
                        self.dbzcluster.Nodes_Trash(self.nodeID, 'Exception during zcluster.Nodes_HeartBeat', 1)
                    except StandardError:
                        pass
                    log.Quit('Exception during zcluster.Nodes_HeartBeat')
                if not __debug__:
                    if secs > self.cleanupInterval:
                        if not hasattr(self, 'slowdeath'):
                            self.slowdeath = 1
                            self.LogError('Node ', self.nodeID, ' is dead.  The server is configured with a ', self.cleanupInterval, " second cleanup interval, but it's been ", secs, ' seconds since')
                            self.LogError("he last performed a heartbeat.  That means every other server on the network have assumed that he's dead")
                            self.LogError('and will remove his entries from the database, effectively turning him into a mummy that wanders around,')
                            self.LogError('borking up everything.')
                        self.LogError("The server is overloaded and dead as far as everybody is concerned.  This may NEVER happen on a live server.  It's heartbeat is supposed to be every ", self.heartbeatInterval, " secs, but it's down to ", secs, '.  Braindeath occurred at ', self.cleanupInterval)
                        self.LogError('A reboot is probably in order.')
                    elif secs > self.cleanupInterval - self.heartbeatInterval:
                        self.LogError("The server is extremely loaded, and basically taking the highway to doom.  It's heartbeat is supposed to be every ", self.heartbeatInterval, " secs, but it's down to ", secs, '.  Braindeath occurs at ', self.cleanupInterval)
                    elif secs > self.heartbeatInterval * 4 / 3:
                        self.LogWarn("The server is very loaded, beware...    It's heartbeat is supposed to be every ", self.heartbeatInterval, " secs, but it's down to ", secs, '.  Braindeath occurs at ', self.cleanupInterval)
                    elif secs < 0:
                        self.LogError('!! ---------------------------------------------------------- !!')
                        self.LogError("Oh my God!  I've been removed from zcluster.nodes!!!  That means I'm already dead, I just didn't know about it!!!!")
                        self.LogError("How embarrassing.  I must be causing all sorts of trouble.  I think I'll just lie down and die of shame.")
                        self.LogError('!! ---------------------------------------------------------- !!')
                        self.dbzcluster.Nodes_Trash(self.nodeID, "zcluster.Nodes_HeartBeat indicated that I've been removed from zcluster.nodes", 1)
                        log.Quit("zcluster.Nodes_HeartBeat indicated that I've been removed from zcluster.nodes")




    def OnCleanUp(self):
        if not __debug__:
            while not getattr(self, 'stop', True):
                try:
                    blue.pyos.synchro.Sleep(int(self.cleanupInterval * 1000))
                    self.dbzcluster.Nodes_TrashLimbos(self.cleanupInterval)
                except Exception:
                    log.LogException('Exception during OnCleanUp.  Ignoring.')
                    sys.exc_clear()




    def GetGPCS(self, channel = None):
        if macho.mode == 'client':
            while self.authenticating == 2:
                blue.pyos.synchro.Sleep(500)

        while not self.state == SERVICE_RUNNING:
            self.LogError("GetGPCS shouldn't be called on machoNet before it's running...")
            log.LogTraceback()
            blue.pyos.synchro.Sleep(500)

        return self.channelHandlersDown.get(channel, None)



    def Ping(self, pingCount = 5, nodeID = None, silent = False):
        if nodeID is None:
            address = macho.MachoAddress()
            daNode = 'random node'
        else:
            address = macho.MachoAddress(nodeID=nodeID)
            daNode = 'node %s' % nodeID

        def prepared_print(prepared):
            lengths = [0] * len(prepared[0])
            for i in range(len(prepared[0])):
                for each in prepared:
                    each[i] = strx(each[i])
                    if len(each[i]) > lengths[i]:
                        lengths[i] = len(each[i]) + 1

                for each in prepared:
                    each[i] += ' ' * (lengths[i] - len(each[i]))


            for i in range(0, len(prepared)):
                each = prepared[i]
                if i < 2:
                    each[1] = each[1][:(-lengths[3] + 1)]
                    each[2] = each[2][:(-lengths[3] + 1)]
                else:
                    each[1] = each[1][(-lengths[3]):]
                    each[2] = each[2][(-lengths[3]):]

            for each in prepared:
                x = ''
                for other in each:
                    x += other

                if not silent:
                    print x



        summaries = []
        for i in range(pingCount):
            if not silent:
                print '---------------------------------------------------------------------------------------------'
                print ' MachoNet Ping statistics for %s' % daNode
                print '---------------------------------------------------------------------------------------------'
            prepared = [['Where',
              'TickID',
              'Time',
              'Time-Tick',
              'curr-start',
              'curr-start',
              'Time-Last Time',
              'Time-Last Time'], ['',
              '',
              '',
              '',
              '(blues)',
              '(millisecs)',
              '(blues)',
              '(millisecs)']]
            retval = self._BlockingCall(macho.PingReq(destination=address, times=[(blue.os.GetTime(), blue.os.GetTime(1), macho.mode + '::start')]))
            retval.times.append((blue.os.GetTime(), blue.os.GetTime(1), macho.mode + '::stop'))
            for n in range(len(retval.times)):
                each = retval.times[n]
                stopminusstartb = ''
                stopminusstartm = ''
                m = 0
                if each[2] in ('proxy::after_tasklet', 'server::after_tasklet', 'client::after_tasklet'):
                    m = 1
                elif each[2] in ('proxy::writing', 'server::turnaround', 'client::stop'):
                    m = 2
                if m:
                    other = retval.times[(n - m)]
                    stopminusstartb = long(round(float(each[1] - other[1])))
                    stopminusstartm = long(round(float(each[1] - other[1]) * 10.0 / float(const.MSEC)))
                    if stopminusstartm:
                        stopminusstartm = str(stopminusstartm / 10) + '.' + str(stopminusstartm % 10)
                    else:
                        stopminusstartm = ''
                tmltb = ''
                tmltm = ''
                if n > 2:
                    tmltb = long(each[1]) - long(retval.times[(n - 1)][1])
                    tmltm = long(round(float(tmltb) * 10.0 / float(const.MSEC)))
                    if tmltm:
                        tmltm = str(tmltm / 10) + '.' + str(tmltm % 10)
                    else:
                        tmltm = ''
                prepared.append([each[2],
                 each[0],
                 each[1],
                 each[1] - each[0],
                 stopminusstartb,
                 stopminusstartm,
                 tmltb,
                 tmltm])

            prepared_print(prepared)
            clientFirst = len(prepared)
            proxyFirst = len(prepared)
            serverFirst = len(prepared)
            for i in reversed(range(len(prepared))):
                if prepared[i][0].startswith('client::'):
                    clientFirst = i
                if prepared[i][0].startswith('proxy::'):
                    proxyFirst = i
                if prepared[i][0].startswith('server::'):
                    serverFirst = i

            clientLast = -1
            proxyLast = -1
            serverLast = -1
            for i in range(len(prepared)):
                if prepared[i][0].startswith('client::'):
                    clientLast = i
                if prepared[i][0].startswith('proxy::'):
                    proxyLast = i
                if prepared[i][0].startswith('server::'):
                    serverLast = i

            cr = 10000000000.0
            if clientFirst < clientLast:
                cr = (float(prepared[clientLast][2].strip()) - float(prepared[clientFirst][2].strip())) / const.MSEC
                if not silent:
                    print 'client roundtrip:  ',
                    print cr,
                    print ' msec'
            pr = 10000000000.0
            if proxyFirst < proxyLast:
                pr = (float(prepared[proxyLast][2].strip()) - float(prepared[proxyFirst][2].strip())) / const.MSEC
                if not silent:
                    print 'proxy roundtrip:   ',
                    print cr,
                    print ' msec'
            server1 = [ p[0].strip() for p in prepared ].index('proxy::writing')
            server2 = [ p[0].strip() for p in prepared ].index('proxy::handle_message', server1)
            diff = float(prepared[server2][2]) - float(prepared[server1][2])
            diff /= const.MSEC
            pspr = diff
            if not silent:
                print 'proxy-server-proxy rountrip: %sms' % pspr
            tickids = []
            for each in prepared[2:]:
                if each[1] not in tickids:
                    tickids.append(each[1])

            if not silent:
                print 'Roundtrip tick count=',
                print len(tickids)
            summaries.append((cr,
             pr,
             pspr,
             len(tickids)))

        average = [ sum([ s[i] for s in summaries ]) / len(summaries) for i in range(len(summaries[0])) ]
        minerage = [ min([ s[i] for s in summaries ]) for i in range(len(summaries[0])) ]
        if not silent:
            print 'Totals for: Client rountrip, proxy roundtrip, proxy-server-proxy roundtrip, tickcount'
            print 'Average: ' + repr(average)
            print 'Minimum: ' + repr(minerage)
        return retval.times



    def GetInitVals(self):
        with self.initValLock:
            if self.initialAuthData is None:
                if macho.mode == 'proxy':
                    self.initialAuthData = self.session.ConnectToRemoteService('machoNet').GetInitVals()
                    tmp = [(self.initialAuthData[0].GetCachedObject, ())]
                    for each in self.initialAuthData[1].itervalues():
                        tmp.append((each.GetCachedObject, ()))

                    uthread.parallel(tmp)
                else:
                    serviceInfo = {}
                    for svc in sm.services.itervalues():
                        if hasattr(svc, '__machoresolve__'):
                            serviceInfo[svc.__logname__] = svc.__machoresolve__

                    initVals = self._GetInitVals()
                    self.initialAuthData = (util.CachedObject(1, 'machoNet.serviceInfo', serviceInfo), initVals)
            return self.initialAuthData



    def _GetInitVals(self):
        return sm.GetService('config').GetInitValsClient()



    def ClearInitVals(self):
        with self.initValLock:
            self.initialAuthData = None
            if macho.mode == 'server':
                self.ProxyBroadcast('OnClearInitVals')



    def OnClearInitVals(self):
        if macho.mode == 'proxy':
            self.ClearInitVals()



    def OnClientConfigUpdated(self, key, value):
        self.LogNotice('OnClientConfigUpdated', key, value)
        if self.clientConfigVals is None:
            self.clientConfigVals = self.GetClientConfigVals() or {}
        if value is None:
            if key in self.clientConfigVals:
                del self.clientConfigVals[key]
        else:
            self.clientConfigVals[key] = value
        if macho.mode == 'client':
            sm.ScatterEvent('OnClientConfigValsChanged', self.clientConfigVals)



    @bluepy.TimedFunction('machoNet::__IsVIP')
    def __IsVIP(self, vipKey):
        if vipKey is None:
            return False
        with self.vipLock:
            if self.vipkeys is None:
                self.vipkeys = {}
                for r in self.session.ConnectToSolServerService('DB2').CallProc('zuser.Users_SelectByRole', ROLE_VIPLOGIN):
                    self.vipkeys[macho.CryptoHash(util.CaseFold(r.userName))] = True

            return vipKey in self.vipkeys



    def OnVIPListChanged(self):
        with self.vipLock:
            self.vipkeys = None



    def IsThisDudeCoolForLogin(self, vipKey):
        if not self.vipMode:
            return True
        return self._MachoNetService__IsVIP(vipKey)



    @bluepy.TimedFunction('machoNet::GetLogonQueuePosition')
    def GetLogonQueuePosition(self, transportID, vipKey):
        if self._MachoNetService__IsVIP(vipKey):
            return 1
        try:
            position = self.serverLogonQueue.index(transportID) + 2
        except ValueError:
            log.LogException()
            position = 2
        position -= self.availableLoginSlots
        return max(1, position)



    def GetLogonQueueStats(self):
        loggedInConnections = len(self.transportIDbyClientID)
        pendingConnections = len(self.serverLogonQueue)
        return (loggedInConnections, pendingConnections, self.availableLoginSlots)



    def PasswordVersion(self, userName):
        return self.session.ConnectToRemoteService('authentication').PasswordVersion(userName)



    def Authenticate(self, transport, request):
        clientID = self.GetIDOfAddress(transport.address, clientMode=True)
        ret = {'user_clientid': clientID,
         'session_init': self.session.ConnectToRemoteService('authentication').Login(request['user_name'], request['user_password'], request['user_password_hash'], const.userConnectTypeClient, transport.address, clientID, request)}
        uthread.worker('machoNet::AutoLogOffClient', self._MachoNetService__AutoLogOffClient, transport, clientID)
        return ret



    def __AutoLogOffClient(self, transport, clientID):
        blue.pyos.synchro.Sleep(self.autoLogoffAuthenticatedTransportInterval * 1000)
        if clientID not in self.transportIDbyClientID and not transport.IsClosed():
            transport.Close('Authentication Timeout', 'HANDSHAKE_TIMEOUT_AUTHENTICATED')
            self.session.ConnectToRemoteService('authentication').Logout(clientID)



    def LogOffClient(self, clientID):
        if clientID:
            uthread.worker('machoNet::LogOffClient', self.session.ConnectToRemoteService('authentication').Logout, clientID)



    def GetTime(self):
        return blue.os.GetTime(1)



    def SendProvisionalResponse(self, method, *args, **keywords):
        if currentcall:
            timeout = keywords.get('machoTimeout', self.callTimeOutInterval)
            response = currentcall.packet.Response(payload=())
            response.oob['provisional'] = (timeout, method, args)
            self.LogInfo('Sending provisional response and updating timeout interval', response)
            self._NonBlockingCall(response)
        else:
            self.LogWarn('Ignoring provisional response request, currentcall=', currentcall)



    def __TimeoutCall(self, channel):
        channel.send_exception(RuntimeError, ('OnMachoTimeout', {'what': 'A low-level timeout occurred during a remote service request'}))



    def __TimeoutCallLoop(self):
        while not getattr(self, 'stop', True):
            try:
                timeout = []
                k = None
                v = None
                blue.pyos.synchro.Sleep(100 * self.callTimeOutInterval)
                for k in self.calls.keys():
                    if blue.os.GetTime() > self.calls[k][1]:
                        v = self.calls[k]
                        timeout.append((self._MachoNetService__TimeoutCall, (v[0],)))
                        del self.calls[k]
                        self.callsCountMin = min(self.callsCountMin, len(self.calls))
                        if k in v[2]:
                            del v[2][k]

                if timeout:
                    uthread.parallel(timeout)
            except Exception:
                log.LogException('Exception during Timeout Call Loop')
                sys.exc_clear()




    def __KATLoop(self):
        if macho.mode == 'client':
            keepAliveTimerInterval = self.clientKeepAliveTimerInterval
        else:
            keepAliveTimerInterval = self.serverKeepAliveTimerInterval
        while not getattr(self, 'stop', True):
            try:
                blue.pyos.synchro.Sleep(keepAliveTimerInterval * 1000 / 4)
                if not self.clockReset:
                    continue
                time = blue.os.GetTime()
                clientCheck = time - self.clientKeepAliveTimerInterval * const.SEC
                clientDead = time - 3 * self.clientKeepAliveTimerInterval * const.SEC
                serverCheck = time - self.serverKeepAliveTimerInterval * const.SEC
                serverDead = time - 3 * self.serverKeepAliveTimerInterval * const.SEC
                for transport in self.transportsByID.itervalues():
                    if not transport.lastPing:
                        continue
                    if transport.clientID:
                        (check, dead,) = (clientCheck, clientDead)
                    else:
                        (check, dead,) = (serverCheck, serverDead)
                    (req, resp,) = transport.lastPing
                    if resp >= check:
                        continue
                    if hasattr(transport, 'done_broadcasting_close'):
                        continue
                    if resp < dead and req > resp:
                        if transport.clientID:
                            transport.Close('Client Transport keep-alive timer has expired', 'KEEPALIVEEXPIRED')
                        else:
                            transport.Close('Proxy/Server Transport keep-alive timer was determined expired by %s #%s' % (macho.mode, self.nodeID))
                    elif not transport.pinging:
                        uthread.worker('machoNet::KATPing', self._MachoNetService__KATPing, transport)

            except Exception:
                log.LogException('Exception during KAT Loop')
                sys.exc_clear()




    def __KATPing(self, transport):
        try:
            transport.pinging = True
            try:
                t0 = blue.os.GetTime(1)
                if not transport.lastPing:
                    transport.lastPing = [0, 0]
                transport.lastPing[0] = t0
                response = self._BlockingCall(macho.PingReq(destination=transport.GetMachoAddressOfOtherSide(), times=[]))
                t1 = blue.os.GetTime(1)
                tResponse = response.times[0][1] - transport.estimatedRTT / 2
                tDiff = t1 - t0
                transport.estimatedRTT = transport.estimatedRTT * 0.85 + (t1 - t0) * 0.15
                transport.timeDiff = transport.timeDiff * 0.85 + (t0 + (t1 - t0) / 2 - tResponse) * 0.15
                transport.lastPing[1] = t1

            finally:
                transport.pinging = False

        except UnMachoDestination as e:
            self.LogWarn('UnMachoDestination encountered while pinging ', transport.GetMachoAddressOfOtherSide(), '.  Probably irrelevant')
            sys.exc_clear()
        except GPSTransportClosed as e:
            self.LogInfo("KATPing detected a closed transport.  That's what it's supposed to do...")
            if transport.transportID in self.transportsByID:
                self.transportsByID[transport.transportID].Close('KATPing detected that the socket was closed', 'KEEPALIVEEXPIRED')
            sys.exc_clear()
        except StandardError:
            self.LogError("Unhandled exception in KATPing.  Shouldn't be a problem, but I wanna see it")
            self.LogError('Worst case, transport keepalive timers should be failing to do their job')
            log.LogException()
            sys.exc_clear()



    def _BlockingCall(self, packet, transport = None):
        if transport is None:
            transports = self._GetTransports(packet.destination)
            if len(transports) > 1:
                raise UnMachoDestination('A blocking call cannot be performed using a forking address.  Use ConnectToAllNeighboringServices instead.')
            transport = transports[0]
        callID = self.callID
        self.callID += 1
        if macho.mode == 'client':
            source = macho.MachoAddress(clientID=0, callID=callID)
        else:
            source = macho.MachoAddress(nodeID=self.nodeID, callID=callID)
        packet.source = source
        self.calls[callID] = [uthread.Channel('machoNet::BlockingCall'),
         blue.os.GetTime() + packet.oob.get('machoTimeout', self.callTimeOutInterval) * const.SEC,
         transport.calls,
         callID]
        self.callsCountMax = max(self.callsCountMax, len(self.calls))
        try:
            try:
                transport.calls[callID] = self.calls[callID][0]
                before = blue.os.GetTime()
                try:
                    transport.Write(packet)
                    while 1:
                        retval = self.calls[callID][0].receive()
                        provisional = retval.oob.get('provisional', None)
                        if provisional is None:
                            break
                        if macho.mode == 'client':
                            self.LogInfo('Received Provisional Response, provisional=', provisional)
                            self.calls[callID][1] = blue.os.GetTime() + provisional[0] * const.SEC
                            if provisional[1].startswith('Process'):
                                sm.ChainEventWithoutTheStars(provisional[1], provisional[2])
                            else:
                                if provisional[1].startswith('Do'):
                                    sm.SendEventWithoutTheStars(provisional[1], provisional[2])
                                else:
                                    sm.ScatterEventWithoutTheStars(provisional[1], provisional[2])


                finally:
                    if transport.calls.has_key(callID):
                        del transport.calls[callID]
                    after = blue.os.GetTime()
                    diff = after - before
                    self.blockingCallTimes.Add(diff)

            except ReferenceError:
                (exctype, exc, tb,) = sys.exc_info()
                try:
                    raise RuntimeError('ReferenceError'), None, tb

                finally:
                    exctype = None
                    xc = None
                    tb = None


        finally:
            if self.calls.has_key(callID):
                del self.calls[callID]
                self.callsCountMin = min(self.callsCountMin, len(self.calls))
            if transport.calls.has_key(callID):
                del transport.calls[callID]

        if retval.command == MACHONETMSG_TYPE_ERRORRESPONSE:
            if retval.code == MACHONETERR_UNMACHODESTINATION:
                raise UnMachoDestination(retval.payload)
            elif retval.code == MACHONETERR_UNMACHOCHANNEL:
                raise UnMachoChannel(retval.payload)
            elif retval.code == MACHONETERR_WRAPPEDEXCEPTION:
                raise MachoWrappedException(retval.payload)
            else:
                raise MachoException(retval.payload)
        return retval


    CallDown = _BlockingCall

    def _NonBlockingCall(self, packet):
        try:
            transports = self._GetTransports(packet.destination)
            for each in transports:
                each.Write(packet)
                each.TagPacketSizes(packet)

        except UnMachoDestination as e:
            self.LogInfo("_NonBlockingCall failed for an UnMachoDestination.  The reason given was '", e.payload, "'.  Generally speaking, this is probably just fine and dandy.")
            self.LogInfo('Packet=', packet)
            sys.exc_clear()
        except GPSTransportClosed as e:
            self.LogInfo("_NonBlockingCall failed for a closed transport.  The reason given was '", e.reason, "'.  Generally speaking, this is probably just fine and dandy.")
            self.LogInfo('Packet=', packet)
            sys.exc_clear()


    NotifyDown = _NonBlockingCall

    def __TransportChoice(self, transportIDs):
        if len(transportIDs) == 1:
            return transportIDs[0]
        options = []
        for transportID in transportIDs:
            try:
                nodeID = self.transportsByID.get(transportID).nodeID
                cpu = self.nodeCPULoadValue.get(nodeID, 1.0)
                weight = 1.0 / float(max(0.01, cpu))
            except:
                weight = 1.0
            options.append([weight, transportID])

        if len(options) > 1:
            options.sort(lambda x, y: cmp(y[0], x[0]))
            options.pop()
        return util.weightedChoice(options)



    @bluepy.TimedFunction('machoNet::_GetTransports')
    def _GetTransports(self, address, transport = None):
        if macho.mode == 'client':
            transport = self.namedtransports.get('tcp:packet:machoNet', None)
            if transport and address.addressType == const.ADDRESS_TYPE_BROADCAST and len(address.narrowcast) == 1:
                appNodeID = address.narrowcast[0]
                if appNodeID in self.transportIDbyAppNodeID:
                    machoTransport = self.transportsByID[self.transportIDbyAppNodeID[appNodeID]]
                    return [machoTransport]
            if not self.namedtransports.has_key('ip:packet:server'):
                raise GPSTransportClosed('The transport has not yet been connected, or authentication was not successful.')
            return [self.namedtransports['ip:packet:server']]
        else:
            transportID = None
            if address.addressType == const.ADDRESS_TYPE_ANY:
                if transport is not None and transport.dependants:
                    (mk, mv,) = ([], 0)
                    for (k, v,) in transport.dependants.iteritems():
                        if v > mv:
                            mk = [k]
                            mv = v
                        elif v == mv:
                            mk.append(k)

                    if mk:
                        transportID = self._MachoNetService__TransportChoice(mk)
                    else:
                        transportID = self._MachoNetService__TransportChoice(transport.dependants.keys())
                elif macho.mode == 'server':
                    if self.transportIDbyProxyNodeID:
                        transportID = random.choice(self.transportIDbyProxyNodeID.values())
                    else:
                        raise UnMachoDestination('Could not connect to any proxy server')
                elif self.transportIDbySolNodeID:
                    transportID = self._MachoNetService__TransportChoice(self.transportIDbySolNodeID.values())
                else:
                    raise UnMachoDestination('Could not connect to any sol server')
            elif address.addressType == const.ADDRESS_TYPE_NODE:
                if address.nodeID in self.deadNodes:
                    raise UnMachoDestination('The specified proxy or server node (%s) is dead' % address.nodeID)
                if self.transportIDbySolNodeID.has_key(address.nodeID):
                    transportID = self.transportIDbySolNodeID[address.nodeID]
                elif self.transportIDbyProxyNodeID.has_key(address.nodeID):
                    transportID = self.transportIDbyProxyNodeID[address.nodeID]
                if self.transportIDbyAppNodeID.has_key(address.nodeID):
                    transportID = self.transportIDbyAppNodeID[address.nodeID]
                elif macho.mode == 'server':
                    if len(self.transportIDbyProxyNodeID):
                        transportID = random.choice(self.transportIDbyProxyNodeID.values())
                elif address.nodeID not in self.deadNodes:
                    self.deadNodes[address.nodeID] = 1
                    self._addressCache.RemoveAllForNode(address.nodeID)
                    self._RemoveNodeFromServiceMaskMapping(address.nodeID)
                    reason = "The node wasn't registered in the proxy's transportIDbySolNodeID or transportIDbyProxyNodeID maps"
                    self.LogNotice('Sending OnNodeDeath for', address.nodeID, 'because', reason)
                    self.ServerBroadcast('OnNodeDeath', address.nodeID, 1, reason)
                raise UnMachoDestination('The specified proxy or server node (%s) could not be reached' % address.nodeID)
            elif address.addressType == const.ADDRESS_TYPE_CLIENT:
                if self.transportIDbyClientID.has_key(address.clientID):
                    transportID = self.transportIDbyClientID[address.clientID]
                else:
                    raise UnMachoDestination('The client (%s) could not be reached' % address.clientID)
            elif address.addressType == const.ADDRESS_TYPE_BROADCAST:
                retval = []
                transportIDs = self.GetTransportIDsFromBroadcastAddress(address)
                for each in transportIDs:
                    retval.append(self.transportsByID[each])

                if not len(retval):
                    self.LogInfo('None of the specified destination addresses could be reached for ', address)
                return retval
            raise UnMachoDestination('The specified address type is invalid')
            if transportID is None:
                self.LogError('Some dude is sending a weird address (', address, ")that doesn't resolve to a transport ID")
                log.LogTraceback()
                raise UnMachoDestination('The transportID is invalid')
            if not self.transportsByID.has_key(transportID):
                raise UnMachoDestination('The transportID does not identify a known transport')
            return [self.transportsByID[transportID]]



    def GetTransportIDsFromBroadcastAddress(self, address):
        return self._GetTransportIDsFromBroadcastAddress(address)



    @bluepy.TimedFunction('machoNet::_GetTransportIDsFromBroadcastAddress')
    def _GetTransportIDsFromBroadcastAddress(self, address):
        if address.idtype is None:
            idtype = None
            scattered = 0
        elif address.idtype[0] in ('*', '+'):
            idtype = address.idtype[1:]
            scattered = 1
        else:
            idtype = address.idtype
            scattered = 0
        if len(address.narrowcast):
            clientIDs = []
            nodeIDs = []
            done = 0
            if idtype == 'clientID':
                if macho.mode == 'server' and len(address.narrowcast) >= 2 * len(self.transportIDbyProxyNodeID):
                    nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                else:
                    clientIDs = address.narrowcast
                done = 1
            elif idtype == 'nodeID':
                nodeIDs = address.narrowcast
                done = 1
            elif idtype == 'serviceMask':
                nodeIDs = self.ResolveServiceMaskToNodeIDs(address.narrowcast[0])
                done = 1
            elif macho.mode == 'server':
                if idtype in self.__server_scattercast_session_variables__:
                    if scattered:
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                        done = 1
                elif len(address.narrowcast) == 1:
                    if idtype == 'multicastID':
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                        done = 1
                    else:
                        (done, nodeIDs,) = self._GetServerBroadcastNodesSingle(idtype, address, scattered)
                        if done is None:
                            self.LogWarn('Sending a packet by some funky address type (', idtype, ').  Resorting to scattercast')
                            nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                            done = 1
                else:
                    (done, nodeIDs,) = self._GetServerBroadcastNodesMultiple(idtype, address, scattered)
                    if done is None:
                        if not scattered:
                            self.LogWarn('Sending a packet via a non-scattered complex address that resorts to a scattercast.  address: ', address)
                        else:
                            self.LogInfo('Sending a packet via a scattered complex address.  address: ', address)
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                        done = 1
            elif macho.mode == 'proxy' and idtype == 'multicastID':
                if len(address.narrowcast) == 1:
                    clientIDs = self.subscriptionsByAddress.get(address.narrowcast[0][0], {}).get(address.narrowcast[0][1], {}).iterkeys()
                else:
                    for (family, multicastID,) in address.narrowcast:
                        clientIDs.extend(self.subscriptionsByAddress.get(family, {}).get(multicastID, {}).keys())

                done = 1
            if not done:
                if len(address.narrowcast) == 1 and (idtype, address.narrowcast[0]) in self.spam:
                    spam = 1
                elif macho.mode == 'server':
                    if self.transportIDbyProxyNodeID:
                        (spam, clientIDs, notfound,) = base.FindClientsAndHoles(idtype, address.narrowcast, len(self.transportIDbyProxyNodeID) * 2)
                    else:
                        (spam, clientIDs, notfound,) = base.FindClientsAndHoles(idtype, address.narrowcast, 20)
                else:
                    (spam, clientIDs, notfound,) = base.FindClientsAndHoles(idtype, address.narrowcast, None)
                if len(address.narrowcast) == 1 and spam:
                    self.LogInfo('Interpreting ', address.narrowcast, ' as a persistant spam address.')
                    if len(self.spam) > 1000:
                        self.spam.clear()
                    self.spam[(idtype, address.narrowcast[0])] = 1
                if spam or macho.mode == 'server' and address.idtype[0] == '*' and len(notfound):
                    clientIDs = []
                    if macho.mode == 'server':
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                    else:
                        nodeIDs = self.transportIDbySolNodeID.iterkeys()
            transportIDs = {}
            if macho.mode == 'server' and self.transportIDbyProxyNodeID:
                for clientID in clientIDs:
                    nodeID = self.GetProxyNodeIDFromClientID(clientID)
                    if nodeID in self.transportIDbyProxyNodeID:
                        transportIDs[self.transportIDbyProxyNodeID[nodeID]] = 1
                        if len(transportIDs) == len(self.transportIDbyProxyNodeID):
                            if len(transportIDs) > 2:
                                self.LogWarn('All proxies targeted in a clientID based routing decision.  If this happens frequently, the caller should resort to a better casting method.')
                            break

            else:
                for each in clientIDs:
                    if self.transportIDbyClientID.has_key(each) and self.transportsByID.has_key(self.transportIDbyClientID[each]):
                        transportIDs[self.transportIDbyClientID[each]] = 1
                    else:
                        self.LogInfo('Transport for client ', each, ' not found while sending narrowcast.')

            for each in nodeIDs:
                if macho.mode == 'server' and self.transportIDbyProxyNodeID.has_key(each) and self.transportsByID.has_key(self.transportIDbyProxyNodeID[each]):
                    transportIDs[self.transportIDbyProxyNodeID[each]] = 1
                elif macho.mode == 'proxy' and self.transportIDbySolNodeID.has_key(each) and self.transportsByID.has_key(self.transportIDbySolNodeID[each]):
                    transportIDs[self.transportIDbySolNodeID[each]] = 1
                elif self.transportIDbyAppNodeID.has_key(each) and self.transportsByID.has_key(self.transportIDbyAppNodeID[each]):
                    transportIDs[self.transportIDbyAppNodeID[each]] = 1
                elif self.transportIDbySolNodeID.has_key(each) and self.transportsByID.has_key(self.transportIDbySolNodeID[each]):
                    transportIDs[self.transportIDbySolNodeID[each]] = 1
                else:
                    self.LogInfo('Transport for node ', each, ' not found while sending narrowcast.')

            transportIDs = transportIDs.keys()
        elif idtype == 'nodeID':
            if address.idtype[0] == '+':
                transportIDs = self.transportIDbyProxyNodeID.values()
            else:
                transportIDs = self.transportIDbySolNodeID.values()
        elif idtype == 'clientID' and macho.mode == 'server':
            transportIDs = self.transportIDbyProxyNodeID.values()
        elif macho.mode == 'server':
            transportIDs = self.transportsByID.keys()
        else:
            transportIDs = self.transportIDbyClientID.values()
        if transportIDs:
            self.broadcastsResolved.Add(len(transportIDs))
        else:
            self.broadcastsMissed.Add()
        return transportIDs



    def __GetServerBroadcastNodesStub(self, idtype, address, scattered):
        done = None
        nodeIDs = None
        return (done, nodeIDs)


    _GetServerBroadcastNodesSingle = _MachoNetService__GetServerBroadcastNodesStub
    _GetServerBroadcastNodesMultiple = _MachoNetService__GetServerBroadcastNodesStub

    def ResolveServiceMaskToNodeIDs(self, serviceMask):
        nodeIDs = set()
        for bit in util.extractBits(serviceMask):
            nodeIDs |= self.nodeIDsByServiceMask[bit]

        return nodeIDs



    def OnMachoObjectDisconnect(self, objectID, clientID, refID):
        sess = None
        if macho.mode == 'client':
            sess = session
        elif clientID in self.transportIDbyClientID:
            transportID = self.transportIDbyClientID[clientID]
            if transportID in self.transportsByID:
                transport = self.transportsByID[transportID]
                sess = transport.sessions.get(clientID, [None])[0]
        if sess is not None:
            sess.UnregisterMachoObject(objectID, refID)



    def ProcessSessionChange(self, isremote, sess, change):
        if 'charid' in change and change['charid'][1] is not None and hasattr(sess, 'clientID'):
            blue.net.MapCharToClient(change['charid'][1], sess.clientID)
        if 'userid' in change and change['userid'][1] is None or 'charid' in change and change['charid'][0] is not None:
            clientID = getattr(sess, 'clientID', 0)
            if not clientID and 'clientID' in change:
                clientID = change['clientID'][0]
            for family in self.subscriptionsByClientID:
                (byClientID, byAddress, countsByAddress,) = self._MachoNetService__GetSubscriptionFamily(family)
                if clientID in byClientID:
                    for address in byClientID[clientID]:
                        try:
                            del byAddress[address][clientID]
                        except StandardError:
                            sys.exc_clear()
                        try:
                            if not byAddress[address]:
                                del byAddress[address]
                        except StandardError:
                            sys.exc_clear()
                        if address in countsByAddress:
                            if address in byAddress:
                                countsByAddress[address] = len(byAddress[address])
                            else:
                                del countsByAddress[address]

                    if not byClientID[clientID]:
                        del byClientID[clientID]

            if clientID:
                if clientID in self.transportIDbyClientID and self.transportIDbyClientID[clientID] not in self.transportIDbyProxyNodeID.itervalues() and self.transportIDbyClientID[clientID] not in self.transportIDbySolNodeID.itervalues():
                    transportID = self.transportIDbyClientID[clientID]
                    if 'userid' in change and change['userid'][1] is None:
                        reason = "The user's connection has been usurped on the " + macho.mode
                    else:
                        reason = 'Hot-swapping characters is not permitted'
                    if macho.mode == 'server' and (len(self.transportIDbyProxyNodeID) or len(self.transportIDbySolNodeID)):
                        self.LogError('Usurping node->node connection!?!  Man do I smell deep shit going on here...')
                        self.LogError('Received a session change notification where userID or charID was disappearing.')
                        self.LogError('The session has a clientID(', clientID, "), so we should disconnect it's transport (", transportID, ').')
                        self.LogError("This should be safe, because the transport isn'it a known node->node transport.")
                        self.LogError('However, that is total crud, and we know it, because this is a sol server with proxy connections.')
                        self.LogError("That means there are NO direct client connections, and we've got a situation here.")
                        self.LogError("Here's a stacktrace:")
                        log.LogTraceback()
                        self.LogError("And here's a session dump:")
                        sess.LogSessionError('USURPSERVER')
                        self.LogError("And here's the change we got:")
                        self.LogError('isremote=', isremote)
                        self.LogError('session=', sess)
                        self.LogError('change=', change)
                        self.LogError("and here's some important info")
                        self.LogError('self.transportIDbyClientID=', self.transportIDbyClientID)
                        self.LogError('self.transportIDbyProxyNodeID=', self.transportIDbyProxyNodeID)
                        self.LogError('self.transportIDbySolNodeID=', self.transportIDbySolNodeID)
                        self.LogError('self.transportsByID[transportID]=', self.transportsByID[transportID])
                        self.LogError('Odds are that this server is going down anyway, and an explanation will be found elsewhere')
                    else:
                        uthread.worker('machoNet::DelayedTransportCloseFromProcessSessionChange', self.transportsByID[transportID].Close, reason)
        elif not isremote and 'charid' in change and change['charid'][1] is not None and self.shutdown is not None and self.shutdown.notify is not None and self.shutdown.when - const.HOUR <= blue.os.GetTime():
            clientID = getattr(sess, 'clientID', 0)
            if not clientID and 'clientID' in change:
                clientID = change['clientID'][1]
            if clientID:
                now = blue.os.GetTime()
                msg = self.shutdown.explanation % {'when': util.FmtDate(self.shutdown.when, 'ns'),
                 'delay': util.FmtTimeInterval(self.shutdown.when - now, 'min')}
                if self.shutdown.notify is None and self.shutdown.duration:
                    msg += '  See you again in ' + util.FmtTimeInterval(self.shutdown.duration * const.MIN, 'min')
                self.SinglecastByClientID(clientID, 'OnClusterShutdownInitiated', msg, self.shutdown.when)



    def HandleAccept(self, transname, transport, llv):
        transportID = self.transportID
        self.serverLogonQueue.append(transportID)
        counter = 0
        try:
            self.transportID = self.transportID + 1
            while not transport.IsClosed():
                if counter > 0:
                    blue.pyos.synchro.Sleep(3000)
                try:
                    if llv:
                        llvresponse = transport.HandleClientAuthentication(self.loggedOnUserCount, transportID)
                        counter += 1
                        if not llvresponse or type(llvresponse) is str and llvresponse != 'OK':
                            self.LogError('Low-level version check failure while accepting from ', transport.address, '.  Undoubtedly a handshake request.')
                            continue
                        elif type(llvresponse) is str:
                            self.LogInfo('Finished dealing with accept from ', transport.address, ', probably a queue request')
                            continue
                    if self.stop:
                        return 
                    machoTransport = macho.MachoTransport(transportID, transport, transname, self)
                    self.transportsByID[transportID] = machoTransport
                    if llv:
                        transport.SetKeepalive(20, 20)
                        machoTransport.clientID = transport.handShake['user_clientid']
                        machoTransport.userID = transport.handShake['session_init']['userid']
                        blue.net.EnumerateTransport(machoTransport.transport.socket.getSocketDescriptor(), machoTransport.transportID, machoTransport.transportName, machoTransport.userID, machoTransport.clientID, 0)
                        blue.net.AddClient(machoTransport.clientID, machoTransport.transportID)
                        s = base.CreateUserSession()
                        s.__dict__['clientID'] = machoTransport.clientID
                        llvresponse['session_init']['role'] |= s.role
                        machoTransport.sessions[machoTransport.clientID] = [s,
                         {},
                         s.rwlock,
                         s.version]
                        self.transportIDbyClientID[machoTransport.clientID] = machoTransport.transportID
                        machoTransport.clientIDs[machoTransport.clientID] = 1
                        s.LogSessionHistory('Authenticating user %s via machoNet from address %s' % (llvresponse['user_name'], transport.address))
                        s.SetAttributes(llvresponse['session_init'])
                        s.LogSessionHistory('Authenticated user %s via machoNet from address %s' % (llvresponse['user_name'], transport.address))
                        if not s.role & ROLE_VIPLOGIN:
                            self.LogInfo('non-vip transport', machoTransport, 'has connected, with session', s, 'There are', self.availableLoginSlots, 'login slots remaining')
                            self.availableLoginSlots -= 1
                    else:
                        blue.net.EnumerateTransport(machoTransport.transport.socket.getSocketDescriptor(), machoTransport.transportID, machoTransport.transportName, 0, 0, 0)
                    machoTransport.currentReaders += 1
                    uthread.worker('machoNet::TransportReader', self.TransportReader, self.transportsByID[transportID])
                except GPSTransportClosed as e:
                    sys.exc_clear()
                except Exception as e:
                    log.LogException()
                    self.LogWarn('Caught %s' % `e`)
                    sys.exc_clear()
                except StandardError:
                    log.LogException()
                    self.LogWarn('Exception in HandleListenTransport')
                    sys.exc_clear()
                return 


        finally:
            try:
                self.serverLogonQueue.remove(transportID)
            except AttributeError:
                pass




    def AcceptLoop(self, transname):
        try:
            listenTransport = self.GetTransport(transname)
            while not getattr(self, 'stop', True):
                try:
                    self.LogInfo('Blocking on accept for ', transname)
                    transport = None
                    transport = listenTransport.Accept()
                    self.LogInfo('Accepted a transport from ', transport.address)
                    uthread.worker('machoNet::HandleAccept', self.HandleAccept, transname, transport, transname != 'tcp:packet:machoNet')
                except GPSTransportClosed:
                    sys.exc_clear()
                    self.LogWarn('ListenTransport closed')
                    return 

        except StandardError:
            log.LogException()
            self.LogError('AcceptLoop bombed')
            sys.exc_clear()



    def TransportReader(self, transport):
        transport.currentReaders -= 1
        try:
            while 1:
                if transport.currentReaders > transport.desiredReaders:
                    return 
                sys.exc_clear()
                try:
                    theMessage = None
                    msgSession = None
                    msgChannel = None
                    msgClientID = None
                    theMessage = transport.Read()
                    if transport.currentReaders < transport.desiredReaders:
                        transport.currentReaders += 1
                        uthread.worker('machoNet::TransportReader', self.TransportReader, transport)
                    if theMessage.command == MACHONETMSG_TYPE_SESSIONCHANGENOTIFICATION and macho.mode == 'proxy':
                        transports = self._GetTransports(theMessage.destination, transport)
                        if len(transports) == 1:
                            if transport.transportName == 'tcp:packet:machoNet':
                                if transport.transportID in transports[0].dependants:
                                    transports[0].dependants[transport.transportID] += 1
                                theMessage.destination = theMessage.source
                                theMessage.source = macho.MachoAddress(clientID=transports[0].clientID)
                                (msgSession, msgChannel, msgClientID,) = transports[0]._SessionAndChannelAndIDFromPacket(theMessage)
                                theMessage.sessionVersion = msgSession[3]
                                msgSession[3] += 1
                                self.LogInfo('Incrementing macho-packet session(', msgSession[0].sid, ")'s version number to ", msgSession[3])
                                try:
                                    self.HandleMessage(transports[0], theMessage, 1)
                                except StandardError:
                                    self.LogError('MAJOR BORKUPP!!!  This is baaaaddddddd')
                                    log.LogTraceback()
                                    msgSession[0].LogSessionError('Session state change bombed')
                                    raise 
                                msgSession[0].version += 1
                                self.LogInfo('Incrementing actual session(', msgSession[0].sid, ")'s version number to ", msgSession[0].version)
                            else:
                                self.LogError('Funky Session Change packet received, ', theMessage)
                        elif len(transports):
                            self.LogError('Received a session change notification destined for ', len(transports), ' transports.  packet=', theMessage)
                        else:
                            self.LogWarn('Ignoring non-routable session change notification.  Hopefully a disconnect event? packet=', theMessage)
                    elif theMessage.command % 2:
                        self.HandleMessage(transport, theMessage)
                    else:
                        (msgSession, msgChannel, msgClientID,) = transport._SessionAndChannelAndIDFromPacket(theMessage)
                        theMessage.sessionVersion = msgSession[3]
                        if theMessage.command in self.__sessioninitorchangenotification__:
                            msgSession[3] += 1
                            self.LogInfo('Incrementing macho-packet session(', msgSession[0].sid, ")'s version number to ", msgSession[3])
                            self.HandleMessage(transport, theMessage)
                            msgSession[0].version += 1
                            self.LogInfo('Incrementing actual session(', msgSession[0].sid, ")'s version number to ", msgSession[0].version)
                        else:
                            sessionNotificationPacket = theMessage.oob.get(OOB_SESSIONNOTIFICATION, None)
                            if sessionNotificationPacket:
                                msgSession[3] += 1
                                self.LogInfo('Incrementing macho-packet session(', msgSession[0].sid, ")'s version number to ", msgSession[3], '. Caused by OOB session notification')
                                self.HandleMessage(transport, sessionNotificationPacket)
                                msgSession[0].version += 1
                                self.LogInfo('Incrementing actual session(', msgSession[0].sid, ")'s version number to ", msgSession[0].version, '. Caused by OOB session notification')
                            self.HandleMessage(transport, theMessage)
                except SessionUnavailable as e:
                    self.LogError('Message abandoned in TransportReader due to unavailable user session')
                    transport.Write(theMessage.ErrorResponse(MACHONETERR_WRAPPEDEXCEPTION, (macho.DumpsSanitized(RuntimeError(e.payload)),)))
                    sys.exc_clear()
                except UnMachoDestination as e:
                    if theMessage.destination.addressType != const.ADDRESS_TYPE_CLIENT or theMessage.command == MACHONETMSG_TYPE_CALL_REQ:
                        transport.Write(theMessage.ErrorResponse(MACHONETERR_UNMACHODESTINATION, e.payload))
                    else:
                        self.LogWarn('Message abandoned in TransportReader due to unroutable destination address, reason=', e.payload)
                        self.LogWarn('Packet=', theMessage)
                    sys.exc_clear()
                except GPSTransportClosed:
                    raise 

        except GPSTransportClosed as e:
            transport.Close(**e.GetCloseArgs())
            sys.exc_clear()
        except TaskletExit:
            self.LogInfo('TransportReader is shutting down - tasklet exit command received.')
            sys.exc_clear()
        except StandardError:
            log.LogException()
            transport.Close('TransportReader is shutting down - an unhandled exception has occurred.', 'UNHANDLEDEXCEPTION')
            sys.exc_clear()
        except:
            log.LogException()
            transport.Close('TransportReader shutting down - a bizzarre low level exception has occurred.', 'UNHANDLEDEXCEPTION')
            sys.exc_clear()



    def IsMessageSane(self, transport, theMessage):
        if transport.transportName == 'tcp:packet:client':
            if theMessage.destination.addressType in self.__borc__:
                transport.Close('Client is trying to send C2C')
                return False
            if theMessage.command not in self.__clientallowedcommands__:
                transport.Close('Client is trying to send disallowed commands')
                return False
            if getattr(transport, 'userID', None) is None:
                transport.Close('Client is trying to send over unauthenticated wire, message=%s' % strx(theMessage))
                return False
            if hasattr(transport, 'userID') and transport.userID != theMessage.userID:
                transport.Close('User is trying to spoof another user')
                return False
        elif macho.mode == 'proxy' or macho.mode == 'server':
            if transport.nodeID is None and theMessage.command != MACHONETMSG_TYPE_IDENTIFICATION_REQ:
                self.LogError('Unidentified or fubarred wire?')
                log.LogTraceback()
                self.LogError('Extra info, tn=', transport.transportName, ', t.node=', transport.nodeID, ', transport=', transport)
                self.LogError('Msg=', theMessage)
                transport.Close('Server or Proxy is trying to send over unidentified wire, message=%s' % strx(theMessage))
                return False
            if macho.mode == 'proxy':
                if transport.nodeID is not None and theMessage.source.addressType == const.ADDRESS_TYPE_NODE and theMessage.source.nodeID != transport.nodeID:
                    if self.ShouldAcceptForwardedMessage(transport, theMessage):
                        pass
                    elif theMessage.command != MACHONETMSG_TYPE_RESOLVE_RSP:
                        raise RuntimeError('Server is trying to pull a fast one.  source=%s, transport=%s' % (theMessage.source.nodeID, transport.nodeID))
        return True


    __borc__ = (const.ADDRESS_TYPE_BROADCAST, const.ADDRESS_TYPE_CLIENT)
    __aorb__ = (const.ADDRESS_TYPE_ANY, const.ADDRESS_TYPE_BROADCAST)

    @bluepy.TimedFunction('machoNet::HandleMessage')
    def HandleMessage(self, transport, theMessage, skipSanityCheck = 0):
        if theMessage.command in self.__pingrequestorresponse__:
            theMessage.times.append((blue.os.GetTime(), blue.os.GetTime(1), macho.mode + '::handle_message'))
            theMessage.Changed()
        try:
            if transport.transportID not in self.transportsByID:
                self.LogWarn("Packet received on a transport that wasn't in transportsByID.  transport=", transport)
                self.LogWarn('Packet=', theMessage)
                transport.Close("Packet received on a transport that wasn't in transportsByID")
                return 
            if self.stop:
                transport.Close('The service is stopping')
                return 
            if not skipSanityCheck:
                if not self.IsMessageSane(transport, theMessage):
                    return 
            if theMessage.source.addressType == const.ADDRESS_TYPE_CLIENT and not self.transportIDbyClientID.has_key(theMessage.source.clientID):
                self.transportIDbyClientID[theMessage.source.clientID] = transport.transportID
                transport.clientIDs[theMessage.source.clientID] = 1
                blue.net.AddClient(theMessage.source.clientID, transport.transportID)
            if theMessage.command % 2:
                if theMessage.destination.addressType in self.__aorb__:
                    transport.Close('A response must be sent to a specific address, not a forking one')
            elif theMessage.source.addressType in self.__aorb__:
                transport.Close('A request must be sent from a specific address, not a forking one')
            forward = 0
            routesTo = theMessage.RoutesTo(macho.MachoAddress(nodeID=self.nodeID))
            if macho.mode == 'client' or routesTo:
                if theMessage.command in self.__notificationtypes__:
                    if macho.mode == 'proxy' or macho.mode == 'orchestratorAgent':
                        if theMessage.command == MACHONETMSG_TYPE_SESSIONCHANGENOTIFICATION:
                            try:
                                transport.SessionNotification(theMessage)
                            except UnMachoDestination as e:
                                self.LogInfo('UnMachoDestination encountered while forwarding session change notification: ', e)
                                sys.exc_clear()
                        elif theMessage.destination.addressType == const.ADDRESS_TYPE_NODE and theMessage.destination.nodeID == self.nodeID:
                            try:
                                transport.SessionNotification(theMessage)
                            except UnMachoDestination as e:
                                self.LogInfo('UnMachoDestination encountered while handling a proxy notification: ', e)
                                sys.exc_clear()
                        elif theMessage.destination.addressType == const.ADDRESS_TYPE_BROADCAST and theMessage.destination.idtype == '+nodeID':
                            try:
                                transport.SessionNotification(theMessage)
                            except UnMachoDestination as e:
                                self.LogInfo('UnMachoDestination encountered while handling a proxy broadcast: ', e)
                                sys.exc_clear()
                        elif routesTo == 2:
                            theMessage2 = copy.deepcopy(theMessage)
                            transport.SessionNotification(theMessage2)
                        forward = 1
                    else:
                        transport.SessionNotification(theMessage)
                elif theMessage.command in self.__calltypes__:
                    if (macho.mode == 'proxy' or macho.mode == 'orchestratorAgent') and not (theMessage.destination.addressType == const.ADDRESS_TYPE_NODE and theMessage.destination.nodeID == self.nodeID):
                        forward = 1
                    else:
                        ret = transport.SessionCall(theMessage)
                        transport.Write(ret)
                elif theMessage.command in self.__responsetypes__ or theMessage.command == MACHONETMSG_TYPE_PING_RSP and (macho.mode != 'proxy' or theMessage.destination.addressType == const.ADDRESS_TYPE_NODE and theMessage.destination.nodeID == self.nodeID):
                    if self.calls.has_key(theMessage.destination.callID):
                        if self.calls[theMessage.destination.callID][0].balance < 0:
                            self.calls[theMessage.destination.callID][0].send(theMessage)
                        else:
                            self.LogWarn("Call Response received, but the call wasn't being waited upon in self.calls, so the response will disappear... ", theMessage)
                    elif theMessage.command == MACHONETMSG_TYPE_ERRORRESPONSE and theMessage.originalCommand == MACHONETMSG_TYPE_NOTIFICATION:
                        self.LogWarn("An error response was received for a notification from us.  Notifcations don't have responses, so this message will disappear... ", theMessage)
                    else:
                        self.LogError('Call Response received on', macho.mode, ", but the call wasn't in self.calls, so the response will disappear... ", theMessage)
                elif theMessage.command == MACHONETMSG_TYPE_TRANSPORTCLOSED:
                    transport.SessionClosed(theMessage.clientID, 'Session terminated due to remote transport closed notification', theMessage.isRemote)
                elif theMessage.command in self.__pingrequestorresponse__:
                    if macho.mode == 'proxy' and not (theMessage.destination.addressType == const.ADDRESS_TYPE_NODE and theMessage.destination.nodeID == self.nodeID):
                        forward = 1
                    elif theMessage.command == MACHONETMSG_TYPE_PING_REQ:
                        theMessage.times.append((blue.os.GetTime(), blue.os.GetTime(1), macho.mode + '::turnaround'))
                        theResponse = theMessage.Response(times=theMessage.times[:])
                        transport.Write(theResponse)
                elif theMessage.command == MACHONETMSG_TYPE_IDENTIFICATION_REQ:
                    if self.nodeID is None:
                        raise RuntimeError, 'no node ID'
                    if macho.mode == 'server':
                        myaddress = self.GetTransport('tcp:packet:machoNet').GetExternalAddress()
                        others = [ ('%s:%d' % (each.ipAddress, each.port), each.nodeID) for each in self._GetLayTracksTo() ]
                    else:
                        myaddress = self.GetTransport('tcp:packet:machoNet').GetInternalAddress()
                        others = []
                    if self.transportIDbyProxyNodeID.has_key(theMessage.nodeID) or self.transportIDbySolNodeID.has_key(theMessage.nodeID):
                        self.LogWarn('Rejecting connection attempt from ', theMessage.nodeID, ' because I already have such a connection')
                        response = (False, 'I already have a socket for this node')
                    elif theMessage.nodeID in self.dontLayTracksTo and theMessage.nodeID > self.nodeID:
                        self.LogInfo('Rejecting connection attempt from ', theMessage.nodeID, ' because I was already establishing such a connection, and I have priority', self.nodeID, 'vs.', theMessage.nodeID)
                        response = (False, 'I am already connecting to this node')
                    else:
                        self.LogInfo('Accepting connection from ', theMessage.nodeID)
                        response = (True, 'OK')
                    if response[0]:
                        transport.nodeID = theMessage.nodeID
                        blue.net.SetTransportNodeID(transport.transportID, theMessage.nodeID)
                        if theMessage.isProxy:
                            thedict = self.transportIDbyProxyNodeID
                        elif theMessage.isApp:
                            thedict = self.transportIDbyAppNodeID
                        else:
                            thedict = self.transportIDbySolNodeID
                        thedict[theMessage.nodeID] = transport.transportID
                        try:
                            isApp = self.nodeID in self.transportIDbyAppNodeID
                            transport.Write(theMessage.Response(response, self.nodeID, others, macho.mode == 'proxy', isApp, self.serviceMask))
                        except:
                            del thedict[theMessage.nodeID]
                            raise 
                        self.externalAddressesByNodeID[theMessage.nodeID] = (theMessage.myaddress, theMessage.serviceMask)
                        if self.clusterStartupPhase:
                            if boot.role == 'proxy':
                                polarisID = self.session.ConnectToSolServerService('machoNet').GetNodeFromAddress(const.cluster.SERVICE_POLARIS, 0)
                            else:
                                polarisID = self.GetNodeFromAddress(const.cluster.SERVICE_POLARIS, 0)
                            isPolaris = theMessage.nodeID == polarisID
                            sm.ScatterEvent('OnNewNode', theMessage.nodeID, theMessage.myaddress, theMessage.isProxy, isPolaris, theMessage.serviceMask)
                    else:
                        isPolaris = macho.mode == 'server' and self.GetNodeID() == self.GetNodeFromAddress(const.cluster.SERVICE_POLARIS, 0)
                        isApp = self.nodeID in self.transportIDbyAppNodeID
                        transport.Write(theMessage.Response(response, self.nodeID, others, macho.mode == 'proxy', isApp, self.serviceMask))
                        transport.Close(response[1], noSend=True)
                    others = list(theMessage.others)
                    random.shuffle(others)
                    for (otherAddress, otherNodeID,) in others:
                        self.LayTracksIfNeeded(otherAddress, otherNodeID, 'IdentificationReq.others')

                else:
                    transport.Close('Command %d is not allowed at this node' % theMessage.command)
            else:
                forward = 1
            if forward:
                if macho.mode != 'proxy' and macho.mode != 'orchestratorAgent':
                    self.LogError('TransportReader is rejecting the message violently')
                    transport.Close("Client and server nodes do not forward packets.  Something's wrong, dude.")
                    return 
                try:
                    transports = self._GetTransports(theMessage.destination, transport)
                    if theMessage.destination.addressType == const.ADDRESS_TYPE_BROADCAST and macho.mode == 'proxy':
                        theMessage.destination.narrowcast = []
                        theMessage.Changed()
                    for each in transports:
                        sessionprops = None
                        if theMessage.source.addressType == const.ADDRESS_TYPE_CLIENT:
                            (rs, rc, theID,) = transport._SessionAndChannelAndIDFromPacket(theMessage)
                            nhk = not transport.dependants.has_key(each.transportID)
                            if nhk or rs[0].version > transport.dependants[each.transportID]:
                                transport.dependants[each.transportID] = rs[0].version
                                if nhk:
                                    sessionprops = {}
                                    for v in rs[0].GetDistributedProps(0):
                                        sessionprops[v] = getattr(rs[0], v)

                                    sessionprops = macho.SessionInitialStateNotification(source=macho.MachoAddress(clientID=theID), destination=macho.MachoAddress(nodeID=each.nodeID), sid=rs[0].sid, initialstate=sessionprops)
                                    if theMessage.command == MACHONETMSG_TYPE_SESSIONCHANGENOTIFICATION:
                                        theMessage = sessionprops
                                        sessionprops = None
                                else:
                                    change = {}
                                    for v in rs[0].GetDistributedProps(1):
                                        change[v] = (None, getattr(rs[0], v))

                                sessionprops = macho.SessionChangeNotification(source=macho.MachoAddress(clientID=theID), destination=macho.MachoAddress(nodeID=each.nodeID), sid=rs[0].sid, change=(1, change))
                        self.FragileWrite(each, theMessage, sessionprops)

                except UnMachoDestination as e:
                    if theMessage.destination.addressType != const.ADDRESS_TYPE_CLIENT or theMessage.command == MACHONETMSG_TYPE_CALL_REQ:
                        transport.Write(theMessage.ErrorResponse(MACHONETERR_UNMACHODESTINATION, e.payload))
                    else:
                        self.LogWarn('Message abandoned due to unroutable destination address, reason=', e.payload)
                        self.LogWarn('Packet=', theMessage)
                    sys.exc_clear()
        except GPSTransportClosed as e:
            transport.Close('Connected transport closed')
            sys.exc_clear()
            return 
        except StandardError:
            log.LogException()
            if transport.transportName == 'tcp:packet:client':
                transport.Close('TransportReader blew up', 'UNHANDLEDEXCEPTION')
            else:
                self.LogError('Playing chicken with a freight train, eh?  Sorry dude, but the show must go on...')
            sys.exc_clear()
        except:
            log.LogTraceback()
            transport.Close('TransportReader blew up - non-standard error', 'UNHANDLEDEXCEPTION')
            raise 



    def ShouldAcceptForwardedMessage(self, transport, theMessage):
        if transport.nodeID in self.transportIDbyAppNodeID:
            return True
        return False



    @bluepy.TimedFunction('machoNet::FragileWrite')
    def FragileWrite(self, transport, message, sessionprops):
        try:
            if sessionprops:
                if prefs.GetValue('inlineSessionJIT', 0):
                    message.oob[OOB_SESSIONNOTIFICATION] = sessionprops
                else:
                    transport.Write(sessionprops)
            if message.command in self.__pingrequestorresponse__:
                message.times.append((blue.os.GetTime(), blue.os.GetTime(1), macho.mode + '::writing'))
                message.Changed()
            transport.Write(message)
        except GPSTransportClosed as e:
            transport.Close('Wrote packet on a closed socket.  Close reason was: ' + strx(e.reason))
            sys.exc_clear()
        except StandardError:
            self.LogWarn("Write died of natural or bizzarre causes.  Could be natural.  Could be bizzarre.  Here's a trace:")
            log.LogException()
            transport.Close('Write died of natural or bizzarre causes.')
            sys.exc_clear()
        except:
            transport.Close('Write died of natural or bizzarre causes, probably shutdown.')
            raise 



    def GetProxyNodeIDFromClientID(self, clientID):
        if clientID is None:
            log.LogTraceback()
            raise UnMachoDestination('None is not a valid clientID')
        proxyNodeID = clientID % 10000000000L
        if macho.mode == 'server' and proxyNodeID not in self.transportIDbyProxyNodeID:
            raise UnMachoDestination('The proxy node in question is not reachable')
        return proxyNodeID



    def GetIDOfAddress(self, address, clientMode = True, customIDData = None):
        (ipaddr, port,) = address.split(':')
        x = ipaddr.split('.')
        if clientMode:
            t = self.clientIDOffset
            self.clientIDOffset += 1
            return t * 10000000000L + self.nodeID
        else:
            if customIDData:
                (basePort, portOffset, idRangeBase,) = customIDData
                hops = (int(port) - basePort - portOffset) / 1000
                if hops < 0:
                    log.LogTraceback('hops (orchestrator agent) fuxx0red')
                    self.LogError('hops: ', hops)
                    self.LogError('port: ', port)
                    self.LogError('dpopo: ', self.defaultOrchestratorAgentPortOffset)
                    self.LogError('om: ', offsetMap[macho.mode]['tcp:packet:machoNet'])
                return idRangeBase + int(x[3]) + hops * 1000
            hops = (int(port) - self.defaultProxyPortOffset - offsetMap[macho.mode]['tcp:packet:client']) / 1000
            if hops < 0:
                log.LogTraceback('hops fuxx0red')
                self.LogError('hops: ', hops)
                self.LogError('port: ', port)
                self.LogError('dpopo: ', self.defaultProxyPortOffset)
                self.LogError('om: ', offsetMap[macho.mode]['tcp:packet:client'])
            return 1000000000 + int(x[3]) + hops * 1000




def WhitelistDumper():
    while True:
        f = file('wl.txt', 'wt')
        vals = blue.marshal.globalsWhitelist.values()
        vals.sort()
        for v in vals:
            print >> f, v[0] + '.' + v[1]

        f.close()
        blue.pyos.synchro.Sleep(5000)




def CollectWhitelist():
    blue.marshal.globalsWhitelist = {}
    blue.marshal.collectWhitelist = True
    uthread.new(WhitelistDumper)



def RegisterPortOffset(mapname, portOffset, modeRoleBootMacho = None):
    if modeRoleBootMacho is None:
        modeRoleBootMacho = boot.role
    offsetMap[modeRoleBootMacho][mapname] = portOffset


exports = {'macho.Loads': MachoLoads,
 'macho.Dumps': MachoDumps,
 'macho.LoadsSanitized': MachoLoadsSanitized,
 'macho.DumpsSanitized': MachoDumpsSanitized,
 'macho.PasswordHash': PasswordHash,
 'macho.MachoException': MachoException,
 'macho.MachoWrappedException': MachoWrappedException,
 'macho.UnMachoDestination': UnMachoDestination,
 'macho.UnMachoChannel': UnMachoChannel,
 'macho.WrongMachoNode': WrongMachoNode,
 'macho.RegisterPortOffset': RegisterPortOffset,
 'macho.offsetMap': offsetMap,
 'macho.gpsMap': gpsMap,
 'macho.Throttle': MachoThrottle,
 'macho.gpcsMap': gpcsMap,
 'macho.packetTypeChannelMap': packetTypeChannelMap}
exports['macho.mode'] = boot.role
util.InitWhitelist()

