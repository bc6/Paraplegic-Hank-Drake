import uix
import uthread
import blue
import form
import michelle
import xtriui
import util
import types
import traceback
import log
import moniker
import trinity
import sys
import service
globals().update(service.consts)
SEC = 10000000L
MIN = SEC * 60L
HOUR = MIN * 60L

class JumpQueue(service.Service):
    __guid__ = 'svc.jumpQueue'
    __sessionparams__ = []
    __exportedcalls__ = {'IsJumpQueued': [ROLE_SERVICE]}
    __dependencies__ = ['machoNet']
    __notifyevents__ = ['OnJumpQueueUpdate', 'DoSessionChanging']

    def Run(self, ms):
        service.Service.Run(self, ms)
        self.jumpQueue = None
        self.queueCharID = None
        uthread.worker('jumpQueue::Timer', self._JumpQueue__Timer)



    def PrepareQueueForCharID(self, charID):
        self.jumpQueue = None
        self.queueCharID = charID



    def GetPreparedQueueCharID(self):
        return self.queueCharID



    def DoSessionChanging(self, isRemote, session, change):
        if 'solarsystemid2' in change:
            self.LogInfo('Jump Queue:  DoSessionChanging is cleaning jump queue info')
            self.jumpQueue = None



    def __Timer(self):
        while self.state == SERVICE_RUNNING:
            if self.jumpQueue is None:
                blue.pyos.synchro.Sleep(500)
            else:
                try:
                    if self.jumpQueue is not None and eve.session.IsItSafe() and (eve.session.solarsystemid2 is None or eve.session.nextSessionChange is None or blue.os.GetTime() > eve.session.nextSessionChange):
                        if eve.session.solarsystemid2 and eve.session.solarsystemid2 == self.jumpQueue.solarsystemID:
                            self.jumpQueue = None
                        elif self.queueCharID in self.jumpQueue.jumpKeys:
                            expires = self.jumpQueue.jumpKeys[self.queueCharID] + SEC * self.jumpQueue.keyLife
                            if blue.os.GetTime() > expires:
                                sm.ScatterEvent('OnJumpQueueMessage', mls.UI_JUMPQUEUED_KEYEXPIRED % {'system': cfg.evelocations.Get(self.jumpQueue.solarsystemID).name}, False)
                                self.jumpQueue = None
                            else:
                                sm.ScatterEvent('OnJumpQueueMessage', mls.UI_JUMPQUEUED_KEYISSUED % {'system': cfg.evelocations.Get(self.jumpQueue.solarsystemID).name,
                                 'interval': util.FmtTimeInterval(expires - blue.os.GetTime(), 'sec')}, True)
                        else:
                            try:
                                idx = 1 + self.jumpQueue.queue.index(self.queueCharID)
                                position = max(1, idx - self.jumpQueue.space)
                                sm.ScatterEvent('OnJumpQueueMessage', mls.UI_JUMPQUEUED_WAITING % {'system': cfg.evelocations.Get(self.jumpQueue.solarsystemID).name,
                                 'pos': position}, False)
                            except ValueError:
                                sys.exc_clear()
                except:
                    log.LogException()
                    sys.exc_clear()
                blue.pyos.synchro.Sleep(4500)




    def IsJumpQueued(self):
        if self.jumpQueue is None:
            return False
        if self.queueCharID in self.jumpQueue.jumpKeys:
            if blue.os.GetTime() - self.jumpQueue.jumpKeys[self.queueCharID] < SEC * self.jumpQueue.keyLife:
                self.jumpQueue = None
            else:
                return False
        self.LogInfo('Jump Queued, queue=', self.jumpQueue)
        return True



    def OnJumpQueueUpdate(self, solarsystemID, space, queue, jumpKeys, keyLife):
        if self.jumpQueue is None:
            self.LogInfo('Jump Queue:  Entering Queue for ', solarsystemID, ', space=', space, ', queue=', queue)
            self.jumpQueue = util.KeyVal(solarsystemID=solarsystemID, space=space, queue=queue, jumpKeys=jumpKeys, keyLife=keyLife)
        elif self.queueCharID in queue:
            self.LogInfo('Jump Queue:  Queue update for ', solarsystemID, ', space=', space, ', queue=', queue, ', keys=', jumpKeys)
            self.jumpQueue.space = space
            self.jumpQueue.queue = queue
            self.jumpQueue.jumpKeys = jumpKeys
            self.jumpQueue.keyLife = keyLife
        else:
            self.LogInfo('Jump Queue:  ', self.queueCharID, ' is leaving queue for ', solarsystemID)
            self.jumpQueue = None



