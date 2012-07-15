#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/movement/eveMovementClient.py
import svc
import GameWorld
import blue
import geo2
import log
import sys
import const
import movement

class MovementClientComponent(movement.CommonMovementComponent):
    __guid__ = 'movement.MovementClientComponent'

    def __init__(self):
        movement.CommonMovementComponent.__init__(self)
        self.IsFlyMode = False
        self.flySpeed = 0.15
        self.relay = None


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
        self.movementStates = movement.MovementStates()
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
        component.InitializeCapsuleInfo(state)
        component.characterControllerInfo.stepHeight = const.AVATAR_STEP_HEIGHT
        return component

    def SetupComponent(self, entity, component):
        svc.movementClient.SetupComponent(self, entity, component)
        component.moveModeManager.movementBroadcastEnabled = not self.entityService.IsClientSideOnly(entity.scene.sceneID)
        component.IsFlyMode = False
        component.flySpeed = 0.15

    def UnRegisterComponent(self, entity, component):
        svc.movementClient.UnRegisterComponent(self, entity, component)

    def ToggleFlyMode(self):
        myMovement = self.entityService.GetPlayerEntity().GetComponent('movement')
        myMovement.IsFlyMode = not myMovement.IsFlyMode
        if myMovement.IsFlyMode:
            my_mode = GameWorld.FlyMode()
            my_mode.velocity = (0.0, 0.01, 0.0)
        else:
            my_mode = GameWorld.PlayerInputMode()
        myMovement.moveModeManager.PushMoveMode(my_mode)

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
                    myMovement.moveModeManager.GetCurrentMode().velocity = newVel
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

    def ProcessEntityMove(self, entid):
        pass

    def OnEntityTeleport(self, charid, newPosition, newRotation):
        entity = self.entityService.FindEntityByID(charid)
        if entity:
            positionComponent = entity.GetComponent('position')
            positionComponent.rotation = newRotation
            positionComponent.position = newPosition

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
        playerEntity = self.entityService.GetPlayerEntity()
        if playerEntity is None:
            return
        aoSvc = sm.GetService('actionObjectClientSvc')
        if aoSvc.IsEntityUsingActionObject(playerEntity.entityID) is True:
            return
        myMovement = playerEntity.GetComponent('movement')
        destination = self._PickPointToPath()
        if destination is None:
            return
        sm.GetService('debugRenderClient').ClearAllShapes()
        sm.GetService('debugRenderClient').RenderSphere(destination, 0.2, 65280)
        sm.GetService('infoGatheringSvc').LogInfoEvent(eventTypeID=const.infoEventDoubleclickToMove, itemID=session.charid, int_1=1)
        if isinstance(myMovement.moveModeManager.GetCurrentMode(), GameWorld.PathToMode):
            myMovement.moveModeManager.GetCurrentMode().SetDestination(destination)
        else:
            pathToMode = GameWorld.PathToMode(destination, 0.1, False, True)
            myMovement.moveModeManager.PushMoveMode(pathToMode)

    def ToggleExtrapolation(self):
        for entity in self.entityService.GetEntityScene(session.worldspaceid).entities.values():
            if entity.HasComponent('movement'):
                m = entity.GetComponent('movement')
                mm = m.moveModeManager.GetCurrentMode()
                if hasattr(mm, 'enableExtrapolation'):
                    mm.enableExtrapolation = not mm.enableExtrapolation