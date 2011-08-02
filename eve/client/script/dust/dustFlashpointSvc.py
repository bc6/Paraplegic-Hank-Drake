import blue
import uthread
import util
import const
import service

class DustFlashpoint(service.Service):
    __guid__ = 'svc.dustFlashpointSvc'
    __notifyevents__ = ['OnNewBombardmentRequest', 'OnBombardmentExplosion']

    def __init__(self):
        service.Service.__init__(self)
        self.requests = {}



    def OnNewBombardmentRequest(self, flashpointID, requestingCharName):
        if flashpointID not in self.requests:
            self.requests[flashpointID] = util.KeyVal(text='', timeout=None, thread=None)
        request = self.requests[flashpointID]
        bracket = sm.GetService('bracket').GetBracket(flashpointID)
        if bracket:
            bracket.ShowBubble(mls.UI_SHARED_DUST_ORBITALSTRIKEREQUEST % {'dustCharacter': requestingCharName})
            request.timeout = blue.os.GetTime() + MIN
            self.requests[flashpointID] = request
            if request.thread is None:
                request.thread = uthread.new(self.OnBombardmentRequestNoLongerNew, flashpointID)



    def OnBombardmentRequestNoLongerNew(self, flashpointID):
        try:
            if not self or self.state != service.SERVICE_RUNNING:
                return 
            request = self.requests.get(flashpointID, None)
            if request is None:
                return 
            while request.timeout > blue.os.GetTime():
                if not self or self.state != service.SERVICE_RUNNING:
                    return 
                timeDiff = request.timeout - blue.os.GetTime()
                if timeDiff <= 0:
                    break
                else:
                    blue.pyos.synchro.Sleep(timeDiff / const.MSEC)

            request.thread = None

        finally:
            bracket = sm.GetService('bracket').GetBracket(flashpointID)
            if bracket:
                bracket.HideBubble()




    def OnBombardmentExplosion(self, planetID, intersectionPoint, phi, theta):
        pass




