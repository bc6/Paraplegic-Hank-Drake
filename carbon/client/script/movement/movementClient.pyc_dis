#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/movement/movementClient.py
import svc
import const
import GameWorld
import movement
import blue

class MovementClient(movement.movementService):
    __guid__ = 'svc.movementClient'
    __notifyevents__ = ['ProcessEntityMove', 'OnSessionChanged']
    __dependencies__ = movement.movementService.__dependencies__[:]
    __dependencies__.extend(['gameWorldClient'])
    reportedMissing = False
    TIME_BEFORE_SENDING = 6 * const.SEC / 30

    def Run(self, *etc):
        movement.movementService.Run(self)
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

    def SetupComponent(self, entity, component):
        movement.movementService.SetupComponent(self, entity, component)
        gw = self.gameWorldClient.GetGameWorld(component.sceneID)
        positionComponent = entity.GetComponent('position')
        if entity.entityID == session.charid:
            remoteNodeID = self.LookupWorldSpaceNodeID(entity.scene.sceneID)
            if remoteNodeID is None:
                remoteNodeID = -1
            component.moveModeManager = GameWorld.MoveModeManager(entity.entityID, component.sceneID, const.movement.AVATARTYPE_CLIENT_LOCALPLAYER, component.moveState, positionComponent, component.physics, component.characterController, GameWorld.PlayerInputMode(), remoteNodeID)
        else:
            component.moveModeManager = GameWorld.MoveModeManager(entity.entityID, component.sceneID, const.movement.AVATARTYPE_CLIENT_NPC, component.moveState, positionComponent, component.physics, component.characterController, GameWorld.ClientRemoteMode(), -1)
        component.InitializeCharacterControllerRefs(positionComponent)
        sm.GetService('navigation')

    def RegisterComponent(self, entity, component):
        movement.movementService.RegisterComponent(self, entity, component)

    def UnRegisterComponent(self, entity, component):
        movement.movementService.UnRegisterComponent(self, entity, component)