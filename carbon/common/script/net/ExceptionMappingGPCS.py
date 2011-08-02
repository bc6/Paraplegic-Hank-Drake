import sys

class ExceptionMappingGPCS:
    __guid__ = 'gpcs.ExceptionMapping'

    def _ProcessCall(self, func, packet):
        try:
            return func(packet)
        except GPSTransportClosed as e:
            tb = sys.exc_info()[2]
            try:
                if getattr(e, 'reasonCode', None) and mls.HasLabel('MACHONET_TRANSPORTCLOSED_' + e.reasonCode):
                    raise UserError(getattr(mls, 'MACHONET_TRANSPORTCLOSED_' + e.reasonCode), getattr(e, 'reasonDict', {}) or {}), None, tb
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




