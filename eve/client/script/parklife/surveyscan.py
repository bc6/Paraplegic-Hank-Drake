import service
import form
import sys
import uthread
import blue

class SurveyScanSvc(service.Service):
    __guid__ = 'svc.surveyScan'
    __exportedcalls__ = {'Clear': []}
    __notifyevents__ = ['OnSurveyScanComplete', 'DoBallRemove']

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.scans = {}
        self.isSettingEntries = False



    def DoBallRemove(self, ball, slimItem, terminal):
        if ball.id in self.scans:
            del self.scans[ball.id]
            if not self.isSettingEntries:
                self.isSettingEntries = True
                uthread.pool('SurveyScanSvc::SetEntriesDelayed', self.SetEntriesDelayed)



    def SetEntriesDelayed(self):
        blue.pyos.synchro.SleepSim(2000)
        wnd = form.SurveyScanView.GetIfOpen()
        if wnd:
            wnd.SetEntries(self.scans)
        self.isSettingEntries = False



    def OnSurveyScanComplete(self, l):
        try:
            for (ballID, typeID, quantity,) in l:
                self.scans[ballID] = (typeID, quantity)

            wnd = form.SurveyScanView.Open()
            if wnd:
                wnd.SetEntries(self.scans)
        except:
            import traceback
            traceback.print_exc()
            sys.exc_clear()



    def GetWnd(self, create = 0):
        if create:
            return form.SurveyScanView.Open()
        return form.SurveyScanView.GetIfOpen()



    def Clear(self):
        self.scans = {}
        form.SurveyScanView.CloseIfOpen()




