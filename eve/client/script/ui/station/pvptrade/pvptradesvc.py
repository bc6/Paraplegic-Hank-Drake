import service
import form

class PVPTradeService(service.Service):
    __guid__ = 'svc.pvptrade'
    __exportedcalls__ = {'StartTradeSession': [],
     'StartCEOTradeSession': []}
    __notifyevents__ = ['OnTrade']

    def StartTradeSession(self, charID):
        tradeSession = sm.RemoteSvc('trademgr').InitiateTrade(charID)
        self.OnInitiate(charID, tradeSession)



    def StartCEOTradeSession(self, charID, warID = None):
        tradeSession = sm.RemoteSvc('trademgr').InitiateTrade(charID, warID)
        self.OnInitiate(charID, tradeSession)



    def OnTrade(self, what, *args):
        self.LogInfo('OnTrade', what, args)
        getattr(self, 'On' + what)(*args)



    def OnInitiate(self, charID, tradeSession):
        checkWnd = sm.GetService('window').GetWindow('trade_' + str(tradeSession.List().tradeContainerID))
        if checkWnd:
            checkWnd.Maximize()
            return 
        tradew = sm.GetService('window').GetWindow('trade_' + str(tradeSession.List().tradeContainerID), create=1, decoClass=form.PVPTrade, tradeSession=tradeSession)



    def OnCancel(self, containerID):
        w = sm.GetService('window').GetWindow('trade_' + str(containerID))
        if w:
            w.OnCancel()



    def OnStateToggle(self, containerID, state):
        w = sm.GetService('window').GetWindow('trade_' + str(containerID))
        if w:
            w.OnStateToggle(state)



    def OnMoneyOffer(self, containerID, money):
        w = sm.GetService('window').GetWindow('trade_' + str(containerID))
        if w:
            w.OnMoneyOffer(money)



    def OnTradeComplete(self, containerID):
        w = sm.GetService('window').GetWindow('trade_' + str(containerID))
        if w:
            w.OnTradeComplete()




