import svc
import trinity
import uiconst
import GameWorld

class EveNavigationService(svc.navigation):
    __guid__ = 'svc.eveNavigation'
    __replaceservice__ = 'navigation'
    __dependencies__ = ['entityClient', 'mouseInput']

    def Run(self, memStream = None):
        svc.navigation.Run(self, memStream)
        self.lastHeading = None
        self.leftMouseDown = False
        self.rightMouseDown = False
        self.lastForwardBackward = None
        self.lastLeftRight = None
        self.mouseInput.RegisterCallback(const.INPUT_TYPE_MOUSEDOWN, self.OnMouseDown)
        self.mouseInput.RegisterCallback(const.INPUT_TYPE_MOUSEUP, self.OnMouseUp)



    def Stop(self, stream):
        if sm.IsServiceRunning('mouseInput'):
            self.mouseInput.UnRegisterCallback(const.INPUT_TYPE_MOUSEDOWN, self.OnMouseDown)
            self.mouseInput.UnRegisterCallback(const.INPUT_TYPE_MOUSEUP, self.OnMouseUp)



    def OnMouseDown(self, button, posX, posY, entityID):
        if button is const.INPUT_TYPE_LEFTCLICK:
            self.leftMouseDown = True
        elif button is const.INPUT_TYPE_RIGHTCLICK:
            self.rightMouseDown = True



    def OnMouseUp(self, button, posX, posY, entityID):
        if button is const.INPUT_TYPE_LEFTCLICK:
            self.leftMouseDown = False
        elif button is const.INPUT_TYPE_RIGHTCLICK:
            self.rightMouseDown = False



    def _UpdateMovement(self, vkey):
        focus = uicore.registry.GetFocus()
        if focus and focus != self.controlLayer:
            return False
        (fwdKey, backKey, moveLKey, moveRKey,) = self.PrimeNavKeys()
        if vkey in self.navKeys:
            self.hasControl = True
            if vkey == fwdKey:
                self.lastForwardBackward = const.MOVDIR_FORWARD
            elif vkey == backKey:
                self.lastForwardBackward = const.MOVDIR_BACKWARD
            elif vkey == moveLKey:
                self.lastLeftRight = const.MOVDIR_LEFT
            elif vkey == moveRKey:
                self.lastLeftRight = const.MOVDIR_RIGHT
            return True



    def RecreatePlayerMovement(self):
        if self.navKeys is None:
            self.PrimeNavKeys()
        if getattr(self, '_delayedMouseUpStillPending', False):
            return 
        player = self.entityClient.GetPlayerEntity()
        if player:
            isPathing = isinstance(player.movement.avatar.GetActiveMoveMode(), GameWorld.PathToMode)
            if self.hasControl and trinity.app.IsActive() and player.movement.allowMovement:
                curKeyState = self.GetKeyState()
                (fwdActive, backActive, moveLActive, moveRActive,) = curKeyState
                isKeyPressed = fwdActive or backActive or moveLActive or moveRActive
                if isKeyPressed and isPathing:
                    player.movement.avatar.PushMoveMode(GameWorld.KBMouseMode(0.0))
                    isPathing = False
                y = 0.0
                z = 0.0
                if backActive and fwdActive and self.lastForwardBackward == const.MOVDIR_BACKWARD or backActive and not fwdActive:
                    z = -1.0
                elif fwdActive or self.leftMouseDown and self.rightMouseDown:
                    z = 1.0
                x = 0.0
                if moveLActive and moveRActive and self.lastLeftRight == const.MOVDIR_LEFT or moveLActive and not moveRActive:
                    x = 1.0
                elif moveRActive:
                    x = -1.0
                if not isPathing:
                    player.movement.avatar.localHeading = (x, y, z)
                    mode = player.movement.avatar.GetActiveMoveMode()
                    if isinstance(mode, GameWorld.KBMouseMode):
                        player.movement.avatar.GetActiveMoveMode().localHeading = (x, y, z)
                        if self.lastHeading != (x, y, z):
                            movementComponent = player.GetComponent('movement')
                            if movementComponent and movementComponent.relay:
                                movementComponent.relay.SendCurrentMove()
                            self.lastHeading = (x, y, z)
            elif not isPathing:
                player.movement.avatar.localHeading = (0, 0, 0)



    def _TurnPlayerToCamera(self):
        pass



    def SetMovementKey(self, direction, keyDown = True):
        triapp = trinity.app
        triapp.SetActive()
        (fwdKey, backKey, moveLKey, moveRKey,) = self.PrimeNavKeys()
        movementMaps = {'FORWARD': fwdKey,
         'BACKWARD': backKey,
         'LEFT': moveLKey,
         'RIGHT': moveRKey,
         'SHIFT': uiconst.VK_SHIFT}
        uicore.uilib.SetKey(movementMaps[direction], keyDown)



    def GetKeyState(self):
        (fwdKey, backKey, moveLKey, moveRKey,) = self.navKeys
        fwdActive = uicore.uilib.Key(fwdKey) if fwdKey is not None else False
        backActive = uicore.uilib.Key(backKey) if backKey is not None else False
        moveLActive = uicore.uilib.Key(moveLKey) if moveLKey is not None else False
        moveRActive = uicore.uilib.Key(moveRKey) if moveRKey is not None else False
        return (fwdActive,
         backActive,
         moveLActive,
         moveRActive)



    def PrimeNavKeys(self):
        fwdCommand = uicore.cmd.GetShortcutByFuncName('CmdMoveForward')
        backCommand = uicore.cmd.GetShortcutByFuncName('CmdMoveBackward')
        moveLCommand = uicore.cmd.GetShortcutByFuncName('CmdMoveLeft')
        moveRCommand = uicore.cmd.GetShortcutByFuncName('CmdMoveRight')
        self.navKeys = []
        for each in (fwdCommand,
         backCommand,
         moveLCommand,
         moveRCommand):
            if each is not None:
                self.navKeys.append(each[-1])
            else:
                self.navKeys.append(None)

        return self.navKeys



    def Reset(self):
        self.navKeys = None
        self.leftMouseDown = False
        self.rightMouseDown = False




