import service
import blue
import util

class VoucherCache(service.Service):
    __exportedcalls__ = {'GetVoucher': [],
     'OnAdd': []}
    __guid__ = 'svc.voucherCache'
    __notifyevents__ = ['ProcessSessionChange']
    __servicename__ = 'voucherCache'
    __displayname__ = 'Voucher Cache Service'

    def __init__(self):
        service.Service.__init__(self)
        self.data = {}



    def Run(self, memStream = None):
        self.LogInfo('Starting Voucher Cache Service')
        self.data = {}
        self.ReleaseVoucherSvc()



    def Stop(self, memStream = None):
        self.ReleaseVoucherSvc()



    def ProcessSessionChange(self, isremote, session, change):
        if 'charid' in change:
            self.ReleaseVoucherSvc()



    def GetVoucherSvc(self):
        if hasattr(self, 'moniker') and self.moniker is not None:
            return self.moniker
        self.moniker = sm.RemoteSvc('voucher')
        return self.moniker



    def ReleaseVoucherSvc(self):
        if hasattr(self, 'moniker') and self.moniker is not None:
            self.moniker = None
            self.data = {}



    def GetVoucher(self, voucherID):
        while eve.session.mutating:
            self.LogInfo('GetVoucher - hang on session is mutating')
            blue.pyos.synchro.Sleep(1)

        if not self.data.has_key(voucherID):
            voucher = self.GetVoucherSvc().GetObject(voucherID)
            if voucher is None:
                return 
            self.data[voucherID] = voucher
        return self.data[voucherID]



    def OnAdd(self, vouchers):
        for voucher in vouchers:
            self.data[voucher.itemID] = voucher





