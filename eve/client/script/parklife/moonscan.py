import service
import form
import sys

class MoonScanSvc(service.Service):
    __guid__ = 'svc.moonScan'
    __update_on_reload__ = 1
    __exportedcalls__ = {'Clear': [],
     'ClearEntry': [],
     'Refresh': []}
    __notifyevents__ = ['OnMoonScanComplete']

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.scans = {}
        self.wnd = None



    def OnMoonScanComplete(self, result):
        try:
            self.scans[result[0].celestialID] = result
            self.GetWnd(1).SetEntries(self.scans)
        except:
            import traceback
            traceback.print_exc()
            sys.exc_clear()



    def GetWnd(self, create):
        wnd = form.Scanner.GetIfOpen()
        if not wnd and create:
            uicore.cmd.OpenScanner()
            return self.GetWnd(0)
        return wnd



    def Refresh(self):
        self.GetWnd(1).SetEntries(self.scans)



    def Clear(self):
        self.scans = {}
        if self.GetWnd(0):
            self.GetWnd(1).ClearMoons()



    def ClearEntry(self, celestialID):
        if celestialID in self.scans:
            del self.scans[celestialID]
        self.GetWnd(1).SetEntries(self.scans)




