#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/services/paperdollSvc.py
import service
import uthread

class PaperdollSvc(service.Service):
    __guid__ = 'svc.paperdoll'
    __servicename__ = 'paperdoll service'
    __displayname__ = 'Paperdoll Service'

    def __init__(self):
        service.Service.__init__(self)

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.currentCharsPaperDollData = {}

    def GetMyPaperDollData(self, charID):
        currentCharsPaperDollData = self.currentCharsPaperDollData.get(charID, None)
        if currentCharsPaperDollData is not None:
            return currentCharsPaperDollData
        uthread.Lock(self)
        try:
            if self.currentCharsPaperDollData.get(charID, None) is None:
                self.currentCharsPaperDollData[charID] = sm.RemoteSvc('paperDollServer').GetMyPaperDollData(charID)
            return self.currentCharsPaperDollData.get(charID, None)
        finally:
            uthread.UnLock(self)

    def ClearCurrentPaperDollData(self):
        self.currentCharsPaperDollData = {}