import const
import GameWorld
import movement

class MovementClient(movement.movementService):
    __guid__ = 'svc.movementClient'
    __dependencies__ = ['machoNet']
    __notifyevents__ = ['ProcessEntityMove', 'OnSessionChanged']
    __componentTypes__ = ['movement']
    reportedMissing = False
    TIME_BEFORE_SENDING = 6 * const.SEC / 30

    def Run(self, *etc):
        self.lastSentTime = 0
        self.unsentPlayerMoves = []
        self.movementServer = sm.RemoteSvc('movementServer')
        self.addressCache = {}
        GameWorld.SetupCLevelMovement()



    def OnSessionChanged(self, isRemote, sess, change):
        newworldspaceid = change.get('worldspaceid', (None, None))[1]
        self.LookupWorldSpaceNodeID(newworldspaceid)



    def LookupWorldSpaceNodeID(self, newworldspaceid):
        if newworldspaceid and newworldspaceid not in self.addressCache:
            if self.entityService.IsClientSideOnly(newworldspaceid):
                return None
            nodeid = self.movementServer.ResolveNodeID(newworldspaceid)
            if nodeid:
                self.addressCache[newworldspaceid] = nodeid
            else:
                self.LogError('Trying to resolve a unknown worldspaceid to a node', newworldspaceid)
        return self.addressCache.get(newworldspaceid, None)



    def GetPlayerEntity(self):
        raise StandardError('Not implemented')




