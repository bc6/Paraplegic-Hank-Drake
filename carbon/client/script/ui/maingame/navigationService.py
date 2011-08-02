import service
import uiconst
import uthread
import blue

class CoreNavigationService(service.Service):
    __guid__ = 'svc.navigation'
    __notifyevents__ = ['OnSessionChanged', 'OnMapShortcut']

    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        self.hasControl = False
        self.navKeys = None
        self.lastKeyRunning = False
        self.keyDownCookie = None
        self.keyUpCookie = None
        self.appfocusCookie = None
        self.lastStrafe = None
        self.lastRotate = None
        self.cameraClient = sm.GetService('cameraClient')
        uthread.new(self.CheckKeyState).context = 'EveNavigationService::CheckKeyState'



    def Stop(self, stream):
        service.Service.Stop(self)



    def GetConfigValue(self, data, name, default):
        return default



    def OnSessionChanged(self, isRemote, sess, change):
        if 'worldspaceid' in change:
            oldworldspaceid = change['worldspaceid'][0]
            worldspaceid = change['worldspaceid'][1]
            if oldworldspaceid:
                self.UnRegisterKeyEvents()
            if worldspaceid:
                self.RegisterKeyEvents()



    def RecreatePlayerMovement(self):
        raise NotImplementedError(self.RecreatePlayerMovement.__doc__)



    def CheckKeyState(self):
        while self.state == service.SERVICE_RUNNING:
            if self.hasControl:
                self.RecreatePlayerMovement()
            blue.synchro.Yield()




    def RegisterKeyEvents(self):
        self.keyDownCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYDOWN, self.OnGlobalKeyDownCallback)
        self.keyUpCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.OnGlobalKeyUpCallback)
        self.appfocusCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_ACTIVE, self.OnGlobalAppFocusChange)



    def UnRegisterKeyEvents(self):
        if self.keyDownCookie:
            uicore.event.UnregisterForTriuiEvents(self.keyDownCookie)
            self.keyDownCookie = None
        if self.keyUpCookie:
            uicore.event.UnregisterForTriuiEvents(self.keyUpCookie)
            self.keyUpCookie = None
        if self.appfocusCookie:
            uicore.event.UnregisterForTriuiEvents(self.appfocusCookie)
            self.appfocusCookie = None



    def _UpdateMovement(self, vkey):
        raise NotImplementedError(self._UpdateMovement.__doc__)



    def OnGlobalKeyDownCallback(self, *args, **kwds):
        return True



    def OnGlobalKeyUpCallback(self, *args, **kwds):
        self.RecreatePlayerMovement()
        return True



    def OnGlobalAppFocusChange(self, *args, **kwds):
        self.RecreatePlayerMovement()
        return True



    def UpdateMovement(self, direction):
        navKeys = self.PrimeNavKeys()
        vkey = list(navKeys)[direction]
        return self._UpdateMovement(vkey)



    def IsPlayerReady(self):
        return True



    def OnMapShortcut(self, *args):
        self.PrimeNavKeys()




