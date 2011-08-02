import svc
import GameWorld
import blue
import geo2
import log
import sys

class MovementClientComponent:
    __guid__ = 'movement.MovementClientComponent'
    __gwattrs__ = ('pos', 'rot', 'vel', 'localHeading', 'moveMode')

    def __init__(self):
        self.avatarInfo = GameWorld.GWAvatarInfo()
        self.avatar = None
        self.IsFlyMode = False
        self.flySpeed = 0.15
        self.relay = None



    def __getattr__(self, attr):
        if attr in self.__gwattrs__:
            return getattr(self.avatar, attr)
        if self.__dict__.has_key(attr):
            return self.__dict__[attr]
        raise AttributeError(attr)




class EveMovementClient(svc.movementClient):
    __guid__ = 'svc.eveMovementClient'
    __replaceservice__ = 'movementClient'
    __exportedcalls__ = svc.movementClient.__exportedcalls__.copy()
    __exportedcalls__.update({})
    __notifyevents__ = svc.movementClient.__notifyevents__[:]
    __notifyevents__.extend(['OnEntityTeleport'])
    __dependencies__ = svc.movementClient.__dependencies__[:]
    __dependencies__.extend(['worldSpaceClient', 'mouseInput'])

    def Run(self, *etc):
        svc.movementClient.Run(self)
        self.cameraClient = sm.GetService('cameraClient')
        self.gameWorldClient = sm.GetService('gameWorldClient')
        self.mouseInput.RegisterCallback(const.INPUT_TYPE_MOUSEDOWN, self.OnMouseDown)
        self.mouseInput.RegisterCallback(const.INPUT_TYPE_MOUSEUP, self.OnMouseUp)
        self.mouseInput.RegisterCallback(const.INPUT_TYPE_MOUSEMOVE, self.OnMouseMove)
        self.mouseInput.RegisterCallback(const.INPUT_TYPE_DOUBLECLICK, self.OnDoubleClick)



    def Stop(self, stream):
        if sm.IsServiceRunning('mouseInput'):
            self.mouseInput.UnRegisterCallback(const.INPUT_TYPE_MOUSEDOWN, self.OnMouseDown)
            self.mouseInput.UnRegisterCallback(const.INPUT_TYPE_MOUSEUP, self.OnMouseUp)
            self.mouseInput.UnRegisterCallback(const.INPUT_TYPE_MOUSEMOVE, self.OnMouseMove)
            self.mouseInput.UnRegisterCallback(const.INPUT_TYPE_DOUBLECLICK, self.OnDoubleClick)



    def CreateComponent(self, name, state):
        component = MovementClientComponent()
        avatarInfo = GameWorld.GWAvatarInfo()
        avatarInfo.isPosed = False
        avatarInfo.height = const.AVATAR_HEIGHT
        avatarInfo.radius = const.AVATAR_RADIUS
        avatarInfo.slopeLimitDegrees = 45.0
        avatarInfo.stickRadius = const.AVATAR_RADIUS * 0.5
        avatarInfo.stickSharpness = 0.2
        avatarInfo.jumpHeight = 1.0
        avatarInfo.maxRotate = 0.17
        avatarInfo.stepHeight = const.AVATAR_STEP_HEIGHT
        component.avatarInfo = avatarInfo
        return component



    def PrepareComponent(self, sceneID, entityID, component):
        component.avatarInfo.entityID = entityID
        component.avatarInfo.name = 'Avatar_%s' % entityID
        component.sceneID = sceneID



    def SetupComponent(self, entity, component):
        component.avatarInfo.positionComponent = entity.GetComponent('position')
        if entity.entityID == session.charid:
            component.avatarInfo.avatarType = const.movement.AVATARTYPE_CLIENT_LOCALPLAYER
        else:
            component.avatarInfo.avatarType = const.movement.AVATARTYPE_CLIENT_NPC
        gw = self.gameWorldClient.GetGameWorld(component.sceneID)
        component.avatar = gw.CreateAvatar(component.avatarInfo)
        if entity.entityID == session.charid:
            component.avatar.PushMoveMode(GameWorld.KBMouseMode(0.0))
            component.avatar.SetMaxSpeed(const.AVATAR_MOVEMENT_SPEED_MAX)
        else:
            positionComponent = entity.GetComponent('position')
            pos = positionComponent.position
            rot = positionComponent.rotation
            netPredictMode = GameWorld.NetPredictMode(blue.os.GetTime(), 0L, pos, (0, 0, 0), rot)
            netPredictMode.enableExtrapolation = False
            component.avatar.PushMoveMode(netPredictMode)
        component.avatar.movementBroadcastEnabled = not self.entityService.IsClientSideOnly(entity.scene.sceneID)
        component.avatar.SetReady(True)
        if entity.HasComponent('animation'):
            component.avatar.animation = entity.GetComponent('animation').updater
        component.IsFlyMode = False
        component.flySpeed = 0.15
        if entity.entityID == session.charid:
            if not self.entityService.IsClientSideOnly(entity.scene.sceneID):
                relay = GameWorld.MovementRelay()
                relay.remoteNodeID = self.LookupWorldSpaceNodeID(entity.scene.sceneID)
                relay.Setup(component.avatar, entity.GetComponent('position'))
                component.relay = relay



    def UnRegisterComponent(self, entity, component):
        component.avatar.positionComponent = None



    def ToggleFlyMode(self):
        myMovement = self.entityService.GetPlayerEntity().GetComponent('movement')
        myMovement.IsFlyMode = not myMovement.IsFlyMode
        if myMovement.IsFlyMode:
            my_mode = GameWorld.FlyMode()
            my_mode.velocity = (0.0, 0.01, 0.0)
        else:
            my_mode = GameWorld.KBMouseMode(0.0)
        myMovement.avatar.PushMoveMode(my_mode)



    def TryFlyUpdate(self):
        me = self.entityService.GetPlayerEntity()
        if me is not None:
            myMovement = me.GetComponent('movement')
            if myMovement and myMovement.IsFlyMode:
                newVel = (0, 0, 0)
                if self.drive:
                    activeCamera = self.cameraClient.GetActiveCamera()
                    cameraDir = geo2.Vec3Subtract(activeCamera.GetPointOfInterest(), activeCamera.GetPosition())
                    newVel = geo2.Vec3Scale(geo2.Vec3Normalize(cameraDir), myMovement.flySpeed)
                try:
                    myMovement.avatar.GetActiveMoveMode().velocity = newVel
                except AttributeError:
                    log.LogException()
                    sys.exc_clear()
                    myMovement.IsFlyMode = False



    def OnMouseDown(self, button, posX, posY, entityID):
        self.drive = True
        self.TryFlyUpdate()



    def OnMouseMove(self, deltaX, deltaY, entityID):
        self.TryFlyUpdate()



    def OnMouseUp(self, button, posX, posY, entityID):
        self.drive = False
        self.TryFlyUpdate()



    def OnDoubleClick(self, entityID):
        self.PathPlayerToCursorLocation()



    def PreTearDownComponent(self, entity, component):
        gw = self.gameWorldClient.GetGameWorld(entity.scene.sceneID)
        component.avatar.animation = None
        if component.relay:
            component.relay.Teardown()
        gw.RemoveAvatar(component.avatar)



    def ProcessEntityMove(self, entid):
        pass



    def OnEntityTeleport(self, charid, newPosition, newRotation):
        entity = self.entityService.FindEntityByID(charid)
        if entity:
            positionComponent = entity.GetComponent('position')
            positionComponent.rotation = newRotation
            positionComponent.position = newPosition
            entity.movement.avatar.vel = (0.0, 0.0, 0.0)
            entity.movement.avatar.ResetOldPosition()



    def _PickPointToPath(self):
        picked = self.cameraClient.GetActiveCamera().PerformPick(uicore.uilib.x, uicore.uilib.y, session.charid)
        if picked is None:
            return 
        else:
            point = geo2.Vector(*picked[0])
            height = self.gameWorldClient.GetFloorHeight(point, session.worldspaceid)
            destination = geo2.Vector(point.x, height, point.z)
            return destination



    def PathPlayerToCursorLocation(self):
        playerAvatar = self.entityService.GetPlayerEntity()
        if playerAvatar is None:
            return 
        aoSvc = sm.GetService('actionObjectClientSvc')
        if aoSvc.IsEntityUsingActionObject(playerAvatar.entityID) is True:
            return 
        myMovement = playerAvatar.GetComponent('movement')
        destination = self._PickPointToPath()
        if destination is None:
            return 
        sm.GetService('debugRenderClient').ClearAllShapes()
        sm.GetService('debugRenderClient').RenderSphere(destination, 0.2, 65280)
        if isinstance(myMovement.avatar.GetActiveMoveMode(), GameWorld.PathToMode):
            myMovement.avatar.GetActiveMoveMode().SetDestination(destination)
        else:
            pathToMode = GameWorld.PathToMode(destination, 0.1, False, True)
            myMovement.avatar.PushMoveMode(pathToMode)



    def ToggleCharacterController(self):
        myMovement = self.entityService.GetPlayerEntity().GetComponent('movement')
        myMovement.avatar.TogglePogoController()



    def ToggleExtrapolation(self):
        for entity in self.entityService.GetEntityScene(session.worldspaceid).entities.values():
            if entity.HasComponent('movement'):
                m = entity.GetComponent('movement')
                mm = m.avatar.GetActiveMoveMode()
                if hasattr(mm, 'enableExtrapolation'):
                    mm.enableExtrapolation = not mm.enableExtrapolation





