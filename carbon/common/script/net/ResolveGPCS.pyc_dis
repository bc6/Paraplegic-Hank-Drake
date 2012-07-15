#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/net/ResolveGPCS.py
import types
from timerstuff import ClockThis
import macho
import const

class ResolveGPCS:
    __guid__ = 'gpcs.Resolve'

    def CallUp(self, packet):
        if getattr(packet.destination, 'service', 0):
            if packet.payload[1] == 'MachoBindObject':
                nodeID = None
            else:
                nodeID = ClockThis('machoNet::GPCS::gpcs.Resolve::CallUp::MachoResolve', sm.StartServiceAndWaitForRunningState(packet.destination.service).MachoResolve, session.GetActualSession())
            if type(nodeID) == types.StringType:
                if packet.command == const.cluster.MACHONETMSG_TYPE_RESOLVE_REQ:
                    return packet.Response(0, nodeID)
                raise UnMachoDestination("Failed to resolve %s, reason='%s'" % (packet.destination.service, nodeID))
            elif nodeID is None:
                if packet.command == const.cluster.MACHONETMSG_TYPE_RESOLVE_REQ:
                    rsp = packet.Response(1, '')
                    rsp.source = macho.MachoAddress(service=packet.destination.service)
                    return rsp
            else:
                if packet.command == const.cluster.MACHONETMSG_TYPE_RESOLVE_REQ:
                    rsp = packet.Response(1, '')
                    rsp.source = macho.MachoAddress(nodeID=nodeID, service=packet.destination.service)
                    return rsp
                if nodeID != self.machoNet.GetNodeID():
                    raise WrongMachoNode(nodeID)
        return self.ForwardCallUp(packet)

    def NotifyUp(self, packet):
        if getattr(packet.destination, 'service', 0):
            nodeID = sm.StartServiceAndWaitForRunningState(packet.destination.service).MachoResolve(session.GetActualSession())
            if type(nodeID) == types.StringType:
                self.machoNet.LogError('Resolve failed during notification.  Packet lost.  Failure reason=', nodeID)
                raise UnMachoDestination("Failed to resolve %s, reason='%s'" % (packet.destination.service, nodeID))
            elif nodeID is None:
                pass
            else:
                thisNodeID = self.machoNet.GetNodeID()
                if nodeID != thisNodeID:
                    self.machoNet.LogInfo('Notification packet recieved on the wrong node(', thisNodeID, '), forwarding to the correct one ', nodeID)
                    packet.destination = macho.MachoAddress(nodeID=nodeID, service=packet.destination.service)
                    proxyID = self.machoNet.GetProxyNodeIDFromClientID(packet.source.clientID)
                    proxyMachoNet = self.machoNet.session.ConnectToRemoteService('machoNet', nodeID=proxyID)
                    proxyMachoNet.NoBlock.ForwardNotificationToNode(packet.source, packet.destination, packet.userID, packet.payload)
                    return
        return self.ForwardNotifyUp(packet)