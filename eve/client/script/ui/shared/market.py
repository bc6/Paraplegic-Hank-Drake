from service import Service

class Market(Service):
    __exportedcalls__ = {'GetMarket': []}
    __guid__ = 'svc.market'
    __notifyevents__ = ['ProcessSessionChange']
    __servicename__ = 'Market'
    __displayname__ = 'Market Service'
    __dependencies__ = []
    __notifyevents__ = ['ProcessSessionChange']

    def __init__(self):
        Service.__init__(self)



    def Run(self, memStream = None):
        self.market = None



    def Stop(self, memStream = None):
        self.market = None



    def GetMarket(self):
        if self.market is None:
            self.market = sm.RemoteSvc('marketBroker').GetMarketRegion()
        return self.market



    def ProcessSessionChange(self, isremote, sess, change):
        if change.has_key('regionid'):
            self.market = None




