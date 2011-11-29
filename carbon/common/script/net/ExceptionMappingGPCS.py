import sys
MESSAGES = {'ACCOUNTBANNED': '/Carbon/MachoNet/TransportClosed/ACCOUNTBANNED',
 'ACCOUNTNOTACTIVE': '/Carbon/MachoNet/TransportClosed/ACCOUNTNOTACTIVE',
 'ACL_ACCEPTDELAY': '/Carbon/MachoNet/TransportClosed/ACL_ACCEPTDELAY',
 'ACL_CLUSTERFULL': '/Carbon/MachoNet/TransportClosed/ACL_CLUSTERFULL',
 'ACL_IPADDRESSBAN': '/Carbon/MachoNet/TransportClosed/ACL_IPADDRESSBAN',
 'ACL_IPADDRESSNOTALLOWED': '/Carbon/MachoNet/TransportClosed/ACL_IPADDRESSNOTALLOWED',
 'ACL_NOTACCEPTING': '/Carbon/MachoNet/TransportClosed/ACL_NOTACCEPTING',
 'ACL_PROXYFULL': '/Carbon/MachoNet/TransportClosed/ACL_PROXYFULL',
 'ACL_PROXYNOTCONNECTED': '/Carbon/MachoNet/TransportClosed/ACL_PROXYNOTCONNECTED',
 'ACL_SHUTTINGDOWN': '/Carbon/MachoNet/TransportClosed/ACL_SHUTTINGDOWN',
 'CLIENTDISCONNECTED': '/Carbon/MachoNet/TransportClosed/CLIENTDISCONNECTED',
 'GAMETIMEEXPIRED': '/Carbon/MachoNet/TransportClosed/GAMETIMEEXPIRED',
 'HANDSHAKE_CORRUPT': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_CORRUPT',
 'HANDSHAKE_FAILEDHASHMISMATCH': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_FAILEDHASHMISMATCH',
 'HANDSHAKE_FAILEDVERIFICATION': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_FAILEDVERIFICATION',
 'HANDSHAKE_FAILEDVIPKEY': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_FAILEDVIPKEY',
 'HANDSHAKE_INCOMPATIBLEBUILD': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_INCOMPATIBLEBUILD',
 'HANDSHAKE_INCOMPATIBLEPROTOCOL': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_INCOMPATIBLEPROTOCOL',
 'HANDSHAKE_INCOMPATIBLEPUBLICKEY': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_INCOMPATIBLEPUBLICKEY',
 'HANDSHAKE_INCOMPATIBLEREGION': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_INCOMPATIBLEREGION',
 'HANDSHAKE_INCOMPATIBLERELEASE': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_INCOMPATIBLERELEASE',
 'HANDSHAKE_INCOMPATIBLEVERSION': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_INCOMPATIBLEVERSION',
 'HANDSHAKE_INCORRECTPADDING': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_INCORRECTPADDING',
 'HANDSHAKE_SERVERFAILURE': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_SERVERFAILURE',
 'HANDSHAKE_TIMEOUT_AUTHENTICATED': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_TIMEOUT_AUTHENTICATED',
 'HANDSHAKE_TIMEOUT_CLIENTCOMPATIBILITYHANDSHAKE': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_TIMEOUT_CLIENTCOMPATIBILITYHANDSHAKE',
 'HANDSHAKE_TIMEOUT_CLIENTRESPONSETOSERVERCHALLENGE': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_TIMEOUT_CLIENTRESPONSETOSERVERCHALLENGE',
 'HANDSHAKE_TIMEOUT_CLIENTSECUREHANDSHAKE': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_TIMEOUT_CLIENTSECUREHANDSHAKE',
 'HANDSHAKE_TIMEOUT_FAILEDSERVERINITIATECOMPATIBILITYHANDSHAKE': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_TIMEOUT_FAILEDSERVERINITIATECOMPATIBILITYHANDSHAKE',
 'HANDSHAKE_TIMEOUT_SERVERDIDNOTACKNOWLEDGECHALLENGERESPONSE': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_TIMEOUT_SERVERDIDNOTACKNOWLEDGECHALLENGERESPONSE',
 'HANDSHAKE_TIMEOUT_SERVERKEYEXCHANGE': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_TIMEOUT_SERVERKEYEXCHANGE',
 'HANDSHAKE_TIMEOUT_SERVERRESPONSETOCLIENTCHALLENGE': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_TIMEOUT_SERVERRESPONSETOCLIENTCHALLENGE',
 'HANDSHAKE_TIMEOUT_SERVERSECUREHANDSHAKE': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_TIMEOUT_SERVERSECUREHANDSHAKE',
 'HANDSHAKE_VERIFICATIONFAILURE': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_VERIFICATIONFAILURE',
 'HANDSHAKE_VERSIONCHECKCOMPLETE': '/Carbon/MachoNet/TransportClosed/HANDSHAKE_VERSIONCHECKCOMPLETE',
 'KEEPALIVEEXPIRED': '/Carbon/MachoNet/TransportClosed/KEEPALIVEEXPIRED',
 'NODEDEATH': '/Carbon/MachoNet/TransportClosed/NODEDEATH',
 'SOCKETCLOSED': '/Carbon/MachoNet/TransportClosed/SOCKETCLOSED',
 'UNHANDLEDEXCEPTION': '/Carbon/MachoNet/TransportClosed/UNHANDLEDEXCEPTION'}

class ExceptionMappingGPCS:
    __guid__ = 'gpcs.ExceptionMapping'

    def _ProcessCall(self, func, packet):
        try:
            return func(packet)
        except GPSTransportClosed as e:
            tb = sys.exc_info()[2]
            try:
                if getattr(e, 'reasonCode', None) and e.reasonCode in MESSAGES:
                    raise UserError('GPSTransportClosed', {'what': (const.UE_LOC, MESSAGES[e.reasonCode], getattr(e, 'reasonDict', {}) or {})}), None, tb
                raise UserError('GPSTransportClosed', {'what': e.reason}), None, tb

            finally:
                del tb

        except UnMachoDestination as e:
            tb = sys.exc_info()[2]
            try:
                raise UserError('UnMachoDestination', {'what': e.payload}), None, tb

            finally:
                del tb




    def CallDown(self, packet):
        return self._ProcessCall(self.ForwardCallDown, packet)



    def NotifyDown(self, packet):
        return self._ProcessCall(self.ForwardNotifyDown, packet)



exports = {'gpcs.TRANSPORT_CLOSED_MESSAGES': MESSAGES}

