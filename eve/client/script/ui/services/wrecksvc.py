import blue
import dbg
import log
import service
import state
import sys

class WreckService(service.Service):
    __guid__ = 'svc.wreck'
    __dependencies__ = [('state', 'statesvc'), 'gameui']
    __startupdependencies__ = ['settings']

    def Run(self, *args):
        service.Service.Run(self, *args)
        (expire_hours, expire_mins,) = (2, 5)
        expire_ms = 1000 * (3600 * expire_hours + 60 * expire_mins)
        self.viewedWrecks = {}
        for (itemID, time,) in settings.char.ui.Get('viewedWrecks', {}).iteritems():
            try:
                if blue.os.TimeDiffInMs(time) < expire_ms:
                    self.viewedWrecks[itemID] = time
            except blue.error:
                sys.exc_clear()

        try:
            self._PersistSettings()
        except:
            log.LogException()
            sys.exc_clear()



    def MarkViewed(self, itemID, true):
        self._SetViewed(itemID, true)
        self._MarkVisually(itemID, true)
        self._PersistSettings()



    def IsViewedWreck(self, itemID):
        return itemID in self.viewedWrecks



    def _MarkVisually(self, itemID, true):
        sm.GetService('state').SetState(itemID, state.flagWreckAlreadyOpened, true)



    def _SetViewed(self, itemID, true):
        if true and itemID not in self.viewedWrecks:
            self.viewedWrecks[itemID] = blue.os.GetTime()
        elif not true and itemID in self.viewedWrecks:
            del self.viewedWrecks[itemID]



    def _PersistSettings(self):
        settings.char.ui.Set('viewedWrecks', self.viewedWrecks)
        sm.GetService('settings').SaveSettings()




