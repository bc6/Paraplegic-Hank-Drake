import copy
import types
import macho
import log
MACHONETMSG_TYPE_SESSIONCHANGENOTIFICATION = 16
MACHONETMSG_TYPE_SESSIONINITIALSTATENOTIFICATION = 18

class SessionChange:
    __guid__ = 'gpcs.SessionChange'

    def NotifyUp(self, packet):
        if packet.command == MACHONETMSG_TYPE_SESSIONCHANGENOTIFICATION:
            nodesOfInterest = None
            if macho.mode == 'proxy':
                nodesOfInterest = getattr(packet, 'nodesOfInterest', None)
                transport = self.machoNet.GetMachoTransportByClientID(packet.source.clientID)
                if transport is not None:
                    if nodesOfInterest is None or -1 in nodesOfInterest:
                        if nodesOfInterest is None:
                            nodesOfInterest = []
                        for each in self.machoNet.GetMachoTransportsByTransportIDs(transport.dependants.iterkeys()):
                            if each.nodeID not in nodesOfInterest:
                                nodesOfInterest.append(each.nodeID)

            if not getattr(session, 'clientID', 0) and macho.mode != 'client':
                self.machoNet.LogError('Received a session change notification on a non-client session')
                self.machoNet.LogError('Packet=', packet)
                log.LogTraceback()
                session.DumpSession('NONCLIENT', 'Session change notification received on non-client session')
            else:
                session.ApplyRemoteAttributeChanges(packet.change[0], packet.change[1])
            if macho.mode == 'proxy' and packet.source.clientID != getattr(session, 'clientID', 0):
                self.machoNet.LogError("Session change notification - clientID doesn't match in packet and session")
                self.machoNet.LogError('packet: ', packet.source.clientID, ' details=', packet)
                self.machoNet.LogError('session: ', getattr(session, 'clientID', 0), ' details=', session)
            if getattr(session, 'clientID', 0) and macho.mode == 'proxy':
                if transport is None:
                    self.machoNet.LogWarn('Transport is None in session change, nodesOfInterest is ', nodesOfInterest)
                    self.machoNet.LogWarn('session = ', session)
                elif nodesOfInterest is not None:
                    sessionVersion = session.version + 1
                    self.machoNet.LogInfo('SessionChangeGPCS:  Incrementing session(', session.sid, ")'s version number to ", session.version)
                    for each in nodesOfInterest:
                        if each != packet.destination.nodeID and each != -1:
                            transportOfNode = self.machoNet.GetTransportOfNode(each)
                            transportIsKnown = transport.dependants.has_key(transportOfNode.transportID)
                            if transportIsKnown:
                                transportVersion = transport.dependants[transportOfNode.transportID]
                            if not transportIsKnown:
                                sessionprops = {}
                                for v in session.GetDistributedProps(0):
                                    sessionprops[v] = getattr(session, v)

                                self.ForwardNotifyDown(macho.SessionInitialStateNotification(source=macho.MachoAddress(clientID=session.clientID), destination=macho.MachoAddress(nodeID=each), sid=session.sid, initialstate=sessionprops))
                            elif sessionVersion > transportVersion:
                                change = {}
                                for v in session.GetDistributedProps(1):
                                    change[v] = (None, getattr(session, v))

                                self.ForwardNotifyDown(macho.SessionChangeNotification(source=macho.MachoAddress(clientID=session.clientID), destination=macho.MachoAddress(nodeID=each), sid=session.sid, change=(1, change)))

            if macho.mode == 'proxy':
                (packet.source, packet.destination,) = (packet.destination, packet.source)
                self.ForwardNotifyDown(packet)
        elif packet.command == MACHONETMSG_TYPE_SESSIONINITIALSTATENOTIFICATION:
            if not getattr(session, 'clientID', 0) and macho.mode != 'client':
                self.machoNet.LogError('Received a session initial state notification on a non-client session')
                self.machoNet.LogError('Packet=', packet)
                log.LogTraceback()
            else:
                session.ApplyInitialState(packet.initialstate)



    def SessionChanged(self, clientID, sid, change, nodesOfInterest = None):
        if nodesOfInterest:
            tmp = []
            for each in nodesOfInterest:
                if type(each) == types.ListType or type(each) == types.TupleType:
                    for other in each:
                        if other and other not in tmp:
                            tmp.append(other)

                elif (type(each) == types.IntType or type(each) == types.LongType) and each not in tmp:
                    tmp.append(each)

            nodesOfInterest = tmp
        packet = macho.SessionChangeNotification(destination=macho.MachoAddress(clientID=clientID), sid=sid, change=(0, change), nodesOfInterest=nodesOfInterest)
        if macho.mode == 'proxy':
            transport = self.machoNet.GetMachoTransportByClientID(clientID)
            if transport is not None:
                nodesOfInterest = getattr(packet, 'nodesOfInterest', None)
                if nodesOfInterest is None or -1 in nodesOfInterest:
                    if nodesOfInterest is None:
                        nodesOfInterest = []
                    for each in self.machoNet.GetMachoTransportsByTransportIDs(transport.dependants.iterkeys()):
                        if each.nodeID not in nodesOfInterest:
                            nodesOfInterest.append(each.nodeID)

                for each in nodesOfInterest:
                    if each != -1:
                        c = copy.copy(packet)
                        c.source = macho.MachoAddress(clientID=clientID)
                        c.destination = macho.MachoAddress(nodeID=each)
                        self.ForwardNotifyDown(c)

        self.ForwardNotifyDown(packet)




