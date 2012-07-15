#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/net/machoNetAddress.py
import service
import macho
import log
globals().update(service.consts)

class MachoAddress:
    __guid__ = 'macho.MachoAddress'
    __passbyvalue__ = 1
    __legalclientaddr__ = ('clientID', 'callID', 'service')
    __legalbroadcastaddr__ = ('broadcastID', 'narrowcast', 'idtype')
    __legalnodeaddr__ = ('nodeID', 'service', 'callID')
    __legalanyaddr__ = ('service', 'callID')

    def __init__(self, *args, **keywords):
        if keywords.has_key('clientID'):
            if len(args) != 0:
                raise GPSBadAddress('A macho client address should contain only keyword arguments')
            self.addressType = const.ADDRESS_TYPE_CLIENT
            self.clientID = keywords['clientID']
            self.callID = keywords.get('callID', None)
            self.service = keywords.get('service', None)
            for each in keywords.iterkeys():
                if each not in self.__legalclientaddr__:
                    raise GPSBadAddress("A macho client address may not contain '%s'" % each)

        elif keywords.has_key('broadcastID'):
            if len(args) != 0:
                raise GPSBadAddress('A macho broadcast address should contain only keyword arguments')
            self.addressType = const.ADDRESS_TYPE_BROADCAST
            self.broadcastID = keywords.get('broadcastID', None)
            self.narrowcast = keywords.get('narrowcast', [])
            self.idtype = keywords.get('idtype', None)
            for each in keywords.iterkeys():
                if each not in self.__legalbroadcastaddr__:
                    raise GPSBadAddress("A macho broadcast address may not contain '%s'" % each)

        elif keywords.has_key('nodeID'):
            if len(args) != 0:
                raise GPSBadAddress('A macho node address should contain only keyword arguments')
            self.addressType = const.ADDRESS_TYPE_NODE
            self.nodeID = keywords['nodeID']
            self.service = keywords.get('service', None)
            self.callID = keywords.get('callID', None)
            for each in keywords.iterkeys():
                if each not in self.__legalnodeaddr__:
                    raise GPSBadAddress("A macho node address may not contain '%s'" % each)

        else:
            if len(args) != 0:
                raise GPSBadAddress("A macho 'any' address should contain only keyword arguments")
            self.addressType = const.ADDRESS_TYPE_ANY
            self.service = keywords.get('service', None)
            self.callID = keywords.get('callID', None)
            for each in keywords.iterkeys():
                if each not in self.__legalanyaddr__:
                    raise GPSBadAddress("A macho any address may not contain '%s'" % each)

    def __getstate__(self):
        if self.addressType == const.ADDRESS_TYPE_CLIENT:
            return (const.ADDRESS_TYPE_CLIENT,
             self.clientID,
             self.callID,
             self.service)
        elif self.addressType == const.ADDRESS_TYPE_BROADCAST:
            return (const.ADDRESS_TYPE_BROADCAST,
             self.broadcastID,
             self.narrowcast,
             self.idtype)
        elif self.addressType == const.ADDRESS_TYPE_ANY:
            return (const.ADDRESS_TYPE_ANY, self.service, self.callID)
        else:
            return (const.ADDRESS_TYPE_NODE,
             self.nodeID,
             self.service,
             self.callID)

    def __setstate__(self, state):
        if state[0] == const.ADDRESS_TYPE_CLIENT:
            self.addressType, self.clientID, self.callID, self.service = state
        elif state[0] == const.ADDRESS_TYPE_BROADCAST:
            self.addressType, self.broadcastID, self.narrowcast, self.idtype = state
        elif state[0] == const.ADDRESS_TYPE_ANY:
            self.addressType, self.service, self.callID = state
        else:
            self.addressType, self.nodeID, self.service, self.callID = state

    def RoutesTo(self, otherAddress, fromAddress = None):
        if self.addressType == const.ADDRESS_TYPE_ANY:
            return 1
        if self.addressType == const.ADDRESS_TYPE_CLIENT and otherAddress.addressType == const.ADDRESS_TYPE_CLIENT and self.clientID == otherAddress.clientID:
            return 1
        if self.addressType == const.ADDRESS_TYPE_BROADCAST and (otherAddress.addressType == const.ADDRESS_TYPE_CLIENT or macho.mode != 'proxy' and macho.mode != 'client' and fromAddress is not None and fromAddress.addressType == const.ADDRESS_TYPE_NODE):
            return 1
        if self.addressType == const.ADDRESS_TYPE_BROADCAST and macho.mode == 'proxy' and self.idtype and self.idtype.startswith('+'):
            return 2
        if self.addressType == const.ADDRESS_TYPE_NODE and otherAddress.addressType == const.ADDRESS_TYPE_NODE and self.nodeID == otherAddress.nodeID:
            return 1
        return 0

    def __repr__(self):
        try:
            if self.addressType == const.ADDRESS_TYPE_CLIENT:
                return 'Address::Client(clientID="%s",callID="%s",service="%s")' % (self.clientID, self.callID, self.service)
            if self.addressType == const.ADDRESS_TYPE_NODE:
                return 'Address::Node(nodeID="%s",service="%s",callID="%s")' % (self.nodeID, self.service, self.callID)
            if self.addressType == const.ADDRESS_TYPE_ANY:
                return 'Address::Any(service="%s",callID="%s")' % (self.service, self.callID)
            if self.addressType == const.ADDRESS_TYPE_BROADCAST:
                return 'Address::BroadCast(broadcastID="%s",narrowcast="%s",idtype="%s")' % (self.broadcastID, strx(self.narrowcast), self.idtype)
            return 'Address::Undefined'
        except Exception:
            log.LogException()
            try:
                return 'Address::Crap(%s)' % strx(self.__dict__)
            except StandardError:
                return 'Address containing crappy data'

    __str__ = __repr__