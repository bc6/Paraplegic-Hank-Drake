import blue
import stackless
import svc
import service
import log
import zaction
import base
import util

class eveZactionClient(svc.zactionClient):
    __guid__ = 'svc.eveZactionClient'
    __replaceservice__ = 'zactionClient'
    __displayname__ = 'Eve ZActionTree Service'
    __exportedcalls__ = svc.zactionClient.__exportedcalls__.copy()
    __dependencies__ = svc.zactionClient.__dependencies__[:]
    __notifyevents__ = svc.zactionClient.__notifyevents__[:]

    def __init__(self):
        svc.zactionClient.__init__(self)
        self.clientProperties['TargetList'] = []



    def Run(self, *etc):
        svc.zactionClient.Run(self, *etc)
        self.mouseInputService = sm.GetService('mouseInput')
        if self.mouseInputService is not None:
            self.mouseInputService.RegisterCallback(const.INPUT_TYPE_LEFTCLICK, self.OnClick)



    def OnClick(self, entityID):
        if self.mouseInputService.GetSelectedEntityID() is not None:
            targetList = [self.mouseInputService.GetSelectedEntityID()]
        else:
            targetList = []
        self.clientProperties['TargetList'] = targetList



    def ProcessSessionChange(self, isRemote, session, change):
        if 'charid' in change:
            svc.zactionClient.ProcessSessionChange(self, isRemote, session, change)
            self._animTypeData = self.zactionServer.GetAnimationData()
            self.ProcessAnimationDictionary(self.GetAnimationData())



    def GetAnimationData(self):
        return self._animTypeData




