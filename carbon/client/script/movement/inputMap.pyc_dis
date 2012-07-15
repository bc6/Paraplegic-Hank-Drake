#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/movement/inputMap.py
import geo2
STATIC_MOVEMENT_STATES_FILE = 'res:/Animation/movementStates.yaml'

class InputMap:
    __guid__ = 'movement.InputMap'

    def __init__(self):
        self.metaState = None
        self.lastMetaState = 0
        self.lastState = 0
        self.lastSpeed = 0.0
        self.entityClient = sm.GetService('entityClient')
        self.movementClient = sm.GetService('movementClient')
        self.movementStates = self.movementClient.movementStates
        self.timeInCurrentState = 0
        self.timeToTransition = 0
        self.timeToInterrupt = 0
        self.runToggle = False

    def GetDesiredState(self, x, z, mbMove):
        inputState = (int(x), int(z), int(mbMove))
        animState = None
        if inputState in self.metaState[const.movement.METASTATE_KEYMAP]:
            animState = self.metaState[const.movement.METASTATE_KEYMAP][inputState]
        return animState

    def CheckStaticStateOK(self, staticIndex, destYaw):
        return staticIndex

    def SetIntendedState(self, xInput, zInput, mbMove, runToggle, facingYaw):
        ent = self.entityClient.GetPlayerEntity()
        mode = ent.GetComponent('movement').moveModeManager.GetCurrentMode()
        metaStateIndex = self.movementStates.FindCurrentMetaState(ent)
        if metaStateIndex >= 0:
            self.metaState = self.movementStates.metaStates[metaStateIndex]
        else:
            self.metaState = None
        if self.metaState is not None:
            lastYaw, trash, trash = geo2.QuaternionRotationGetYawPitchRoll(ent.GetComponent('position').rotation)
            baseSpeed = self.metaState.get(const.movement.METASTATE_BASE_SPEED, 0.0)
            if not self.metaState.get(const.movement.METASTATE_DISABLE_RUN_TOGGLE, False):
                self.runToggle = runToggle
            if self.runToggle:
                baseSpeed *= self.metaState.get(const.movement.METASTATE_RUNNING_MOD, 1.0)
            animState = self.GetDesiredState(xInput, zInput, mbMove)
            animState = self.CheckStaticStateOK(animState, facingYaw - lastYaw)
            if animState is not None:
                if hasattr(mode, 'CheckNewSetStaticState'):
                    mode.CheckNewSetStaticState(metaStateIndex, animState, baseSpeed, facingYaw - lastYaw)
                    return
            if hasattr(mode, 'SetMetaState'):
                mode.SetMetaState(metaStateIndex, baseSpeed)