#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/station/pvptrade/pvptradesvc.py
import service
import form
import uicls

class PVPTradeService(service.Service):
    __guid__ = 'svc.pvptrade'
    __exportedcalls__ = {'StartTradeSession': []}
    __notifyevents__ = ['OnTrade']

    def StartTradeSession(self, charID):
        tradeSession = sm.RemoteSvc('trademgr').InitiateTrade(charID)
        self.OnInitiate(charID, tradeSession)

    def OnTrade(self, what, *args):
        self.LogInfo('OnTrade', what, args)
        getattr(self, 'On' + what)(*args)

    def OnInitiate(self, charID, tradeSession):
        self.LogInfo('OnInitiate', charID, tradeSession)
        tradeContainerID = tradeSession.List().tradeContainerID
        checkWnd = uicls.Window.GetIfOpen(windowID='trade_%d' % tradeContainerID)
        if checkWnd:
            checkWnd.Maximize()
            return
        tradew = form.PVPTrade.Open(windowID='trade_%d' % tradeContainerID, tradeSession=tradeSession)

    def OnCancel(self, containerID):
        w = uicls.Window.GetIfOpen(windowID='trade_' + str(containerID))
        if w:
            w.OnCancel()

    def OnStateToggle(self, containerID, state):
        w = uicls.Window.GetIfOpen(windowID='trade_' + str(containerID))
        if w:
            w.OnStateToggle(state)

    def OnMoneyOffer(self, containerID, money):
        w = uicls.Window.GetIfOpen(windowID='trade_' + str(containerID))
        if w:
            w.OnMoneyOffer(money)

    def OnTradeComplete(self, containerID):
        w = uicls.Window.GetIfOpen(windowID='trade_' + str(containerID))
        if w:
            w.OnTradeComplete()