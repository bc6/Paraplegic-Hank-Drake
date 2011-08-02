from __future__ import with_statement
import blue
import uthread
import stackless
import sys
import types
import base
import zlib
import weakref
import log
import macho
import service
import bluepy
import const
globals().update(service.consts)
from timerstuff import ClockThis
import iocp
from service import ROLE_SERVICE, ROLE_REMOTESERVICE
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
MACHONETMSG_TYPE__MOVEMENTNOTIFICATION = 100
MACHONETMSG_TYPE_PING_REQ = 20
MACHONETMSG_TYPE_PING_RSP = 21
MACHONETERR_UNMACHODESTINATION = 0
MACHONETERR_UNMACHOCHANNEL = 1
MACHONETERR_WRAPPEDEXCEPTION = 2
MACHONET_LOGMOVEMENT = 0
useBlueNetHeader = iocp.UsingBlueNetHeader()
if '/disablePacketCompression' in blue.pyos.GetArg():
    log.general.Log('Packet Compression: Disabled', log.LGINFO)
    MACHONET_COMPRESSION_DISABLED = True
elif iocp.UsingCompression():
    log.general.Log('Packet Compression: IOCP', log.LGINFO)
    if iocp.UsingIOCP():
        import carbonio
        carbonio.setCompressionThreshold(prefs.GetValue('machoNet.minimumBytesToCompress', 200))
        carbonio.setCompressionMinRatio(prefs.GetValue('packetCompressionMinimumRatio', 75))
        carbonio.setCompressionLevel(prefs.GetValue('packetCompressionLevel', 6))
        MACHONET_COMPRESSION_DISABLED = True
    else:
        log.general.Log('Could not turn on IOCP packet compression as IOCP is not enabled!  Reverting to MachoNet compression...', log.LGERR)
        MACHONET_COMPRESSION_DISABLED = False
else:
    log.general.Log('Packet Compression: MachoNet', log.LGINFO)
    MACHONET_COMPRESSION_DISABLED = False
if prefs.GetValue('machoNet.logMovement', 0) or '/logMovement' in blue.pyos.GetArg():
    MACHONET_LOGMOVEMENT = 1

class MachoTransport(log.LogMixin):
    __guid__ = 'macho.MachoTransport'
    __sessioninitorchangenotification__ = (MACHONETMSG_TYPE_SESSIONINITIALSTATENOTIFICATION, MACHONETMSG_TYPE_SESSIONCHANGENOTIFICATION)

    def __init__(self, transportID, transport, transportName, machoNet):
        self.machoNet = weakref.proxy(machoNet)
        log.LogMixin.__init__(self, '%s transport' % self.machoNet.__guid__)
        self.nodeID = None
        self.transportID = transportID
        self.transport = transport
        self.transportName = transportName
        if self.transportName == 'tcp:packet:client':
            self.userID = None
        self.clientID = 0
        self.clientIDs = {}
        self.dependants = {}
        self.sessions = {}
        self.calls = {}
        self.currentReaders = 0
        if self.transportName == 'tcp:packet:client':
            self.desiredReaders = 2
        else:
            self.desiredReaders = 20
        self.lastPing = None
        self.pinging = False
        self.estimatedRTT = 100 * const.MSEC
        self.timeDiff = 0
        self.compressionThreshold = prefs.GetValue('machoNet.minimumBytesToCompress', 200)
        self.compressionPercentageThreshold = prefs.GetValue('machoNet.maxPercentagePreCompressedToCompress', 75)
        self.largePacketLogSpamThreshold = prefs.GetValue('machoNet.largePacketLogSpamThreshold', None)
        self.dropPacketThreshold = prefs.GetValue('machoNet.dropPacketThreshold', 5000000)



    def __str__(self):
        return repr(self)



    def __repr__(self):
        try:
            return "MachoTransport(nodeID=%s,transportID=%s,transport='%s',transportName='%s',clientID=%s" % (self.nodeID,
             self.transportID,
             str(self.transport),
             self.transportName,
             self.clientID)
        except StandardError:
            sys.exc_clear()
            return 'MachoTransport containing crappy data'



    def LogInfo(self, *args):
        if self.machoNet.isLogInfo:
            log.LogMixin.LogInfo(self, *args)



    def GetMachoAddressOfOtherSide(self):
        if macho.mode == 'client':
            return macho.MachoAddress(nodeID=self.machoNet.myProxyNodeID)
        else:
            if self.clientID:
                return macho.MachoAddress(clientID=self.clientID)
            return macho.MachoAddress(nodeID=self.nodeID)



    def IsClosed(self):
        return self.transport.IsClosed()



    def Close(self, reason, reasonCode = None, reasonArgs = {}, exception = None, noSend = False):
        if self.machoNet.transportsByID.has_key(self.transportID):
            blue.net.PurgeTransport(self.transportID)
            if self.transportName == 'ip:packet:server' and self.machoNet.namedtransports.has_key('ip:packet:server'):
                self.machoNet.ClearAddressCache()
                self.machoNet.ResetAutoResolveCache()
                del self.machoNet.namedtransports['ip:packet:server']
            if self.nodeID is not None and (self.machoNet.transportIDbyProxyNodeID.has_key(self.nodeID) and self.machoNet.transportIDbyProxyNodeID[self.nodeID] == self.transportID or self.machoNet.transportIDbySolNodeID.has_key(self.nodeID) and self.machoNet.transportIDbySolNodeID[self.nodeID] == self.transportID):
                if not self.machoNet.IsClusterShuttingDown():
                    self.machoNet.LogError('Removing transport from transportIDbyProxyNodeID or transportIDbySolNodeID', self.nodeID, self, reason)
                    log.LogTraceback()
                try:
                    if self.nodeID in self.machoNet.transportIDbyProxyNodeID:
                        del self.machoNet.transportIDbyProxyNodeID[self.nodeID]
                except StandardError:
                    sys.exc_clear()
                    self.LogInfo('Exception during MachoTransport::Close ignored.')
                try:
                    if self.nodeID in self.machoNet.transportIDbySolNodeID:
                        del self.machoNet.transportIDbySolNodeID[self.nodeID]
                except StandardError:
                    sys.exc_clear()
                    self.LogInfo('Exception during MachoTransport::Close ignored.')
                self.machoNet.RemoveAllForNode(self.nodeID)
                if macho.mode == 'proxy' and not self.machoNet.IsClusterShuttingDown():
                    self.machoNet.ServerBroadcast('OnNodeDeath', self.nodeID, 1, "The node's transport was detected disconnected by the proxy.   reason code=%s" % strx(reason))
            for each in self.clientIDs.iterkeys():
                try:
                    del self.machoNet.transportIDbyClientID[each]
                except StandardError:
                    sys.exc_clear()
                    self.LogInfo('Exception during MachoTransport::Close ignored.')

            self.clientIDs = {}
            try:
                del self.machoNet.transportsByID[self.transportID]
            except StandardError:
                sys.exc_clear()
                self.LogInfo('Exception during MachoTransport::Close ignored.')
            try:
                self.transport.Close(reason, reasonCode, reasonArgs, exception, noSend)
            except StandardError:
                sys.exc_clear()
                self.LogInfo('Exception during MachoTransport::Close ignored.')
            while self.calls:
                try:
                    (k, v,) = self.calls.items()[0]
                    try:
                        del self.calls[k]

                    finally:
                        v.send_exception(GPSTransportClosed, reason, reasonCode, reasonArgs)

                except Exception:
                    log.LogException('Exception during transport closed broadcast.  (Semi)-silently ignoring this.')
                    sys.exc_clear()

            if not hasattr(self, 'done_broadcasting_close'):
                self.done_broadcasting_close = 1
                if len(self.dependants) and self.transportName == 'tcp:packet:client':
                    msg = macho.TransportClosed(clientID=self.clientID, isRemote=0)
                    msg2 = macho.TransportClosed(clientID=self.clientID, isRemote=1)

                    def CloseTransport(caller, each, msg):
                        if caller.transportsByID.has_key(each):
                            try:
                                caller.transportsByID[each].Write(msg)
                            except StandardError:
                                log.LogTraceback()
                                caller.transportsByID[each].Close('Write failed big time in CloseTransport')
                                sys.exc_clear()
                            except:
                                log.LogTraceback()
                                caller.transportsByID[each].Close('Write failed big time in CloseTransport, non-standard error')
                                raise 


                    for each in self.dependants.iterkeys():
                        uthread.worker('machoNet::CloseTransport', CloseTransport, self.machoNet, each, msg)
                        msg = msg2

                if self.transportName == 'tcp:packet:client':
                    self.machoNet.LogOffClient(self.clientID)
                if self.transportName == 'tcp:packet:machoNet':
                    disco = []
                    for each in self.machoNet.transportIDbyClientID.itervalues():
                        if self.transportID in self.machoNet.transportsByID[each].dependants and each not in disco:
                            disco.append(each)

                    for each in self.dependants:
                        if self.transportID in self.machoNet.transportsByID[each].dependants and each not in disco:
                            disco.append(each)

                    for each in disco:
                        self.machoNet.transportsByID[each].Close('A server node you were using has gone offline.', 'NODEDEATH')

                self.dependants = {}
                while len(self.sessions):
                    for each in self.sessions.keys():
                        if self.transportName == 'tcp:packet:machoNet':
                            reason = 'Session terminated due to local transport closure'
                        self.SessionClosed(each, reason)





    @bluepy.TimedFunction('machoNet::Transport::SessionClosed')
    def SessionClosed(self, clientID, reason, isRemote = 0):
        if self.clientIDs.has_key(clientID):
            del self.clientIDs[clientID]
        if self.machoNet.transportIDbyClientID.has_key(clientID):
            del self.machoNet.transportIDbyClientID[clientID]
        blue.net.PurgeClient(clientID)
        if clientID in self.sessions:
            tmpdude = self.sessions[clientID]
            with MachoCallOrNotification(self, tmpdude, None):
                if clientID in self.sessions:
                    sess = self.sessions[clientID][0]
                    del self.sessions[clientID]
                    mask = sess.Masquerade()
                    try:
                        if self.transportName == 'ip:packet:server':
                            sm.ScatterEvent('OnDisconnect', getattr(self, 'disconnectsilently', 0), reason)
                        if macho.mode != 'client':
                            sess.LogSessionHistory(reason)
                            base.CloseSession(sess, isRemote)
                        else:
                            sess.ClearAttributes(dontSendMessage=True)

                    finally:
                        mask.UnMask()




    @bluepy.TimedFunction('machoNet::MachoTransport::Write')
    def Write(self, message):
        if hasattr(self, 'userID'):
            message.userID = self.userID
        if message.source.addressType == const.ADDRESS_TYPE_ANY and not message.command % 2:
            message.source.nodeID = self.machoNet.nodeID
            message.source.addressType = const.ADDRESS_TYPE_NODE
            message.Changed()
        elif message.source.addressType == const.ADDRESS_TYPE_NODE and message.source.nodeID is None:
            message.source.nodeID = self.machoNet.nodeID
            message.Changed()
        if self.transportName == 'tcp:packet:client':
            sn = message.oob.get('sn', None)
            if type(sn) == types.DictType and self.clientID in sn:
                message.oob['sn'] = sn[self.clientID]
                message.Changed()
                thePickle = message.GetPickle()
                message.oob['sn'] = sn
                message.Changed()
            else:
                thePickle = message.GetPickle()
        else:
            thePickle = message.GetPickle()
        if message.command != MACHONETMSG_TYPE__MOVEMENTNOTIFICATION or MACHONET_LOGMOVEMENT:
            self.LogInfo('Write: ', message)
        if self.transportName != 'tcp:packet:machoNet' and message.compressedPart * 100 / len(thePickle) < self.compressionPercentageThreshold and len(thePickle) - message.compressedPart > self.compressionThreshold and not MACHONET_COMPRESSION_DISABLED:
            before = len(thePickle)
            try:
                with bluepy.Timer('machoNet::MachoTransport::Write::Compress'):
                    compressed = zlib.compress(thePickle, 1)
            except zlib.error as e:
                raise RuntimeError('Compression Failure: ' + strx(e))
            after = len(compressed)
            if after > before:
                self.LogInfo('Compress would have exploded data from ', before, ' to ', after, ' bytes.  Sending uncompressed.')
            elif (before - after) * 100 / before <= 5:
                self.LogInfo("Compress didn't help one bit.  Would have compressed data from ", before, ' to ', after, " bytes, which is insignificant.  Sending uncompressed, rather than wasting the recipient's CPU power for nothing.")
            else:
                thePickle = compressed
                self.machoNet.compressedBytes.Add(before - after)
        if self.transportName == 'tcp:packet:client' and macho.mode == 'proxy':
            for (objectID, refID,) in message.oob.get('OID+', {}).iteritems():
                s = self.sessions.get(self.clientID, [None])[0]
                if s is not None:
                    s.RegisterMachoObject(objectID, None, refID)

        if self.largePacketLogSpamThreshold != None and len(thePickle) > self.largePacketLogSpamThreshold:
            log.LogTraceback(extraText='Packet larger than the %d byte largePacketLogSpamTreshhold being written out to wire (%d > %d)' % (self.largePacketLogSpamThreshold, len(thePickle), self.largePacketLogSpamThreshold))
        if len(thePickle) > self.dropPacketThreshold:
            if self.transportName == 'tcp:packet:client' or macho.mode == 'server' and (message.destination.addressType == const.ADDRESS_TYPE_CLIENT or message.destination.addressType == const.ADDRESS_TYPE_BROADCAST and message.destination.idtype not in ('nodeID', '+nodeID')):
                self.machoNet.LogError('Attempted to send a deadly (len=', len(thePickle), ') packet to client(s), PACKET DROPPED')
                self.machoNet.LogError('Packet=', message)
                self.machoNet.LogError('Pickle starts with=', thePickle[:1000])
                return 
        self.transport.Write(thePickle)
        self.machoNet.dataSent.Add(len(thePickle))



    @bluepy.TimedFunction('machoNet::MachoTransport::Read')
    def Read(self):
        self.currentReaders += 1
        try:
            thePickle = self.transport.Read()

        finally:
            self.currentReaders -= 1

        if getattr(self, 'userID', None) and len(thePickle) > 100000:
            self.machoNet.LogWarn('Read a ', len(thePickle), ' byte packet (before decompression) from userID=', getattr(self, 'userID', 'non-user'), ' on address ', self.transport.address)
        elif len(thePickle) > 5000000:
            self.machoNet.LogWarn('Read a ', len(thePickle), ' byte packet (before decompression) from userID=', getattr(self, 'userID', 'non-user'), ' on address ', self.transport.address)
        if thePickle[0] not in '}~':
            before = len(thePickle)
            try:
                with bluepy.Timer('machoNet::MachoTransport::Read::DeCompress'):
                    thePickle = zlib.decompress(thePickle)
            except zlib.error as e:
                raise RuntimeError('Decompression Failure: ' + strx(e))
            after = len(thePickle)
            if after <= before:
                self.machoNet.LogError('Decompress shrank data from ', before, ' to ', after, ' bytes')
            else:
                self.machoNet.decompressedBytes.Add(after - before)
        if getattr(self, 'userID', None) and len(thePickle) > 100000:
            self.machoNet.LogWarn('Read a ', len(thePickle), ' byte packet (after decompression, if appropriate) from userID=', getattr(self, 'userID', 'non-user'), ' on address ', self.transport.address)
        elif len(thePickle) > 5000000:
            self.machoNet.LogWarn('Read a ', len(thePickle), ' byte packet (after decompression, if appropriate) from userID=', getattr(self, 'userID', 'non-user'), ' on address ', self.transport.address)
        if self.clientID:
            self.machoNet.dataReceived.Add(len(thePickle))
        else:
            self.machoNet.dataReceived.AddFrom(self.nodeID, len(thePickle))
        try:
            message = macho.Loads(thePickle)
        except GPSTransportClosed as e:
            self.transport.Close(**e.GetCloseArgs())
            raise 
        except StandardError:
            if self.transportName == 'tcp:packet:client':
                log.LogTraceback()
                address = self.transport.address
                self.transport.Close('An improperly formed or damaged packet was received from your client')
                db = self.machoNet.session.ConnectToAnyService('DB2')
                db.CallProc('zcluster.Attacks_Insert', getattr(self, 'userID', None), address.split(':')[0], int(address.split(':')[1]), strx(thePickle[:2000].replace('\\', '\\\\').replace('\x00', '\\0')))
            raise 
        message.SetPickle(thePickle)
        if self.transportName == 'tcp:packet:client':
            message.source = macho.MachoAddress(clientID=self.clientID, callID=message.source.callID)
        if hasattr(self, 'userID'):
            message.userID = self.userID
        if message.command != MACHONETMSG_TYPE__MOVEMENTNOTIFICATION or MACHONET_LOGMOVEMENT:
            self.LogInfo('Read: ', message)
        if macho.mode == 'proxy':
            for (objectID, refID,) in message.oob.get('OID-', {}).iteritems():
                s = self.sessions.get(self.clientID, [None])[0]
                if s is None:
                    s = self.sessions.get(self.nodeID, [None])[0]
                if s is not None:
                    s.UnregisterMachoObject(objectID, refID)

        return message



    def TagPacketSizes(self, req, rsp = None):
        ctk = GetLocalStorage().get('calltimer.key', None)
        if ctk is not None:
            ct = base.GetCallTimes()
            try:
                s = session._Obj()
            except:
                sys.exc_clear()
                s = session
            if s:
                if not s.role & ROLE_SERVICE:
                    ct = (ct[0], s.calltimes)
                else:
                    ct = (ct[1], s.calltimes)
            else:
                ct = (ct[1],)
            for calltimes in ct:
                if ctk in calltimes:
                    calltimes[ctk][4] += req.GetPickleSize(self.machoNet)
                    if rsp is not None:
                        with bluepy.Timer('machoNet::HandleMessage::SessionCall::TagPacketSizes::GetPickleSize::Rsp'):
                            calltimes[ctk][5] += rsp.GetPickleSize(self.machoNet)




    def SessionCall(self, packet):
        try:
            while macho.mode == 'client' and self.machoNet.authenticating:
                blue.pyos.synchro.Sleep(250)

            (newsession, channel, theID,) = self._SessionAndChannelAndIDFromPacket(packet)
            with MachoCallOrNotification(self, newsession, packet) as currentcall:
                session = newsession[0]
                mask = session.Masquerade({'base.currentcall': weakref.ref(currentcall)})
                try:
                    ret = None
                    if getattr(packet.destination, 'service', None) is not None:
                        if not newsession[1].has_key(packet.destination.service):
                            try:
                                newsession[1][packet.destination.service] = packet.service = session.ConnectToService(packet.destination.service, remote=1)
                            except ServiceNotFound as e:
                                ret = packet.ErrorResponse(MACHONETERR_WRAPPEDEXCEPTION, (macho.DumpsSanitized(e),))
                                sys.exc_clear()
                        else:
                            packet.service = newsession[1][packet.destination.service]
                    if ret is None:
                        if self.machoNet.channelHandlersUp.has_key(channel):
                            ret = self.machoNet.channelHandlersUp[channel].CallUp(packet)
                        else:
                            ret = packet.ErrorResponse(MACHONETERR_UNMACHOCHANNEL, 'The specified channel is not present on this server')
                    self.TagPacketSizes(packet, ret)
                    return ret

                finally:
                    if session.clientID != theID:
                        if session.clientID is not None:
                            self.machoNet.LogError('Cleaning session ', session.clientID, " because it's ID doesn't match ", theID)
                        self._CleanupSession(theID)
                    mask.UnMask()
                    if hasattr(packet, 'service'):
                        delattr(packet, 'service')

        except Exception as e:
            log.LogException('Error in session call')
            raise 



    def SessionNotification(self, packet):
        while macho.mode == 'client' and self.machoNet.authenticating:
            blue.pyos.synchro.Sleep(250)

        (newsession, channel, theID,) = self._SessionAndChannelAndIDFromPacket(packet)
        with MachoCallOrNotification(self, newsession, packet) as currentcall:
            sess = newsession[0]
            mask = sess.Masquerade({'base.currentcall': weakref.ref(currentcall)})
            try:
                if getattr(packet.destination, 'service', None) is not None:
                    if not newsession[1].has_key(packet.destination.service):
                        newsession[1][packet.destination.service] = sess.ConnectToService(packet.destination.service, remote=1)
                    packet.service = newsession[1][packet.destination.service]
                if self.machoNet.channelHandlersUp.has_key(channel):
                    self.machoNet.channelHandlersUp[channel].NotifyUp(packet)
                else:
                    self.LogInfo('Notification received for channel ', channel, ', but no GPCS handler available for that particular channel of transport', self)
                self.TagPacketSizes(packet)

            finally:
                if sess.clientID != theID:
                    if sess.clientID is not None:
                        self.machoNet.LogError('Cleaning session ', sess.clientID, " because it's ID doesn't match ", theID)
                    self._CleanupSession(theID)
                mask.UnMask()
                if hasattr(packet, 'service'):
                    delattr(packet, 'service')




    def _SessionFromClientID(self, clientID):
        s = self.sessions.get(clientID, None)
        if s is not None:
            return s[0]
        else:
            return 



    def _SessionAndChannelAndIDFromPacket(self, packet):
        clientID = self._AssociateWithSession(packet)
        rsess = self.sessions[clientID]
        channel = None
        if packet is not None:
            channel = macho.packetTypeChannelMap.get(packet.command, None)
        return (rsess, channel, clientID)



    def _CleanupSession(self, theID):
        if theID in self.sessions and macho.mode != 'client':
            tmp = self.sessions[theID][0]
            del self.sessions[theID]
            base.CloseSession(tmp)



    def LockSession(self, sessrec, packrat):
        if packrat is not None and not packrat.command % 2:
            if hasattr(packrat, 'sessionVersion'):
                i = 1
                while packrat.sessionVersion > sessrec[0].version:
                    logargs1 = ('Sleep #',
                     i,
                     '(at least',
                     i / 2,
                     'seconds) while waiting for session change to complete.  The packet is destined for session version ',
                     packrat.sessionVersion,
                     ' but the session(',
                     sessrec[0].sid,
                     ') is currently version ',
                     sessrec[0].version)
                    logargs2 = ('packet=', packrat)
                    if i % 250 == 0:
                        self.LogError(*logargs1)
                        self.LogError(*logargs2)
                    else:
                        self.LogInfo(*logargs1)
                        self.LogInfo(*logargs2)
                    blue.pyos.synchro.Sleep(500)
                    i += 1

            self.machoNet.WaitForSequenceNumber(packrat.source, packrat.oob.get('sn', 0))
        if sessrec[2]:
            if packrat is None or packrat.command in self.__sessioninitorchangenotification__:
                sessrec[2].WRLock()
                if sessrec[0].role & ROLE_SERVICE:
                    sessrec[2].Unlock()
                    sessrec[0].LogSessionError('SESSIONFUXUP', 'Trying to run a session init or change in a service session context')
                    log.LogTraceback()
                    raise RuntimeError('Session map failure, attempting to run a session init or change in a service session context')
            else:
                sessrec[2].RDLock()



    def UnLockSession(self, sessrec, tasklet = None):
        if sessrec[2]:
            sessrec[2].Unlock(tasklet)



    def _AssociateWithSession(self, packet = None, forceNodeID = None):
        if forceNodeID is not None:
            clientID = forceNodeID
            service = 1
        elif macho.mode == 'client':
            clientID = 0
            service = 0
        elif not packet.command % 2:
            if packet.source.addressType == const.ADDRESS_TYPE_CLIENT:
                clientID = packet.source.clientID
                service = 0
            else:
                clientID = packet.source.nodeID
                service = 1
        elif packet.destination.addressType == const.ADDRESS_TYPE_CLIENT:
            clientID = packet.destination.clientID
            service = 0
        else:
            clientID = packet.destination.nodeID
            service = 1
        if not self.sessions.has_key(clientID):
            if macho.mode == 'client':
                self.sessions[clientID] = [session,
                 {},
                 None,
                 session.version]
            elif service:
                s = base.GetServiceSession('remote:%d' % clientID, 1)
                self.sessions[clientID] = [s,
                 {},
                 None,
                 s.version]
            elif not packet.command % 2:
                if macho.mode == 'server' or self.transportName == 'tcp:packet:client':
                    if macho.mode != 'server':
                        self.LogError('Creating user session remotely but not on a sol server. Please check code.')
                    if not isinstance(packet, macho.SessionInitialStateNotification):
                        log.LogTraceback('Packet received before initial session notification. Packet/tasklet reordering?')
                        raise SessionUnavailable('Unable to load session for request')
                    s = base.CreateUserSession(sid=packet.sid)
                else:
                    raise UnMachoDestination("Server's should not send requests on behalf of client's in this manner")
            else:
                raise UnMachoDestination('Could not locate a session for the client of this response ' + str(clientID))
            self.sessions[clientID] = [s,
             {},
             None,
             s.version]
            if not service:
                self.sessions[clientID][2] = self.sessions[clientID][0].rwlock
            self.sessions[clientID][0].__dict__['clientID'] = clientID
            if not service and packet is not None and packet.userID is not None:
                self.sessions[clientID][0].SetAttributes({'userid': packet.userID})
            if service:
                role = self.sessions[clientID][0].__dict__['role'] | ROLE_SERVICE | ROLE_REMOTESERVICE
                self.sessions[clientID][0].SetAttributes({'role': role})
                self.sessions[clientID][0].LogSessionHistory('machoNet associated remote service session with clientID/nodeID %s' % clientID)
            elif packet is None:
                uid = None
            else:
                uid = packet.userID
            self.sessions[clientID][0].LogSessionHistory('machoNet associated session with clientID %s and userID %s' % (clientID, uid))
        self.sessions[clientID][0].lastRemoteCall = blue.os.GetTime()
        return clientID




class MachoCallOrNotification(object):

    def __init__(self, transport, sessrec, packet):
        (self.transport, self.sessrec, self.packet,) = (transport, sessrec, packet)
        self.tasklet = stackless.getcurrent()



    def __enter__(self):
        self.transport.LockSession(self.sessrec, self.packet)
        return self



    def __exit__(self, e, v, tb):
        self.Unlock(None)



    def UnLockSession(self):
        self.Unlock(self.tasklet)



    def Unlock(self, tasklet):
        if self.sessrec:
            s = self.sessrec
            t = self.transport
            self.transport = self.sessrec = self.tasklet = None
            t.UnLockSession(s, tasklet)



    def __repr__(self):
        return '<MachoCallOrNotification, packet=%r>' % (self.packet,)




