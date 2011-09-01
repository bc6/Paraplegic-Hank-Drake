import service
import GameWorld
import zaction
import blue
import uthread
import geo2
MOTIONSTATE_NO_CHANGE = 0
MOTIONSTATE_KEY_FRAME = 1
MOTIONSTATE_CHARACTER = 2

class EntityProcSvc(service.Service):
    __guid__ = 'svc.entityProcSvc'
    __machoresolve__ = 'location'

    def Run(self, *args):
        service.Service.Run(self, *args)
        GameWorld.RegisterPythonActionProc('SetEntityPosition', self._SetEntityPosition, ('ENTID', 'ALIGN_POSITION', 'ALIGN_ROTATION', 'MotionState'))
        GameWorld.RegisterPythonActionProc('GetEntitySceneID', self._GetEntitySceneID, ('ENTID',))
        GameWorld.RegisterPythonActionProc('GetBonePosRot', self._GetBonePosRot, ('ENTID', 'boneName', 'posProp', 'rotProp'))
        GameWorld.RegisterPythonActionProc('SetAllowedToMove', self._SetAllowedToMove, ('ENTID', 'allowedToMove'))



    def _GetEntitySceneID(self, ENTID):
        entity = self.entityService.FindEntityByID(ENTID)
        if entity is None:
            self.LogError('GetEntitySceneID: Entity with ID ', ENTID, ' not found!')
            return False
        GameWorld.AddPropertyForCurrentPythonProc({'entitySceneID': entity.scene.sceneID})
        return True



    def _GetBonePosRot(self, ENTID, boneName, posProp, rotProp):
        entity = self.entityService.FindEntityByID(ENTID)
        if entity is None:
            self.LogError('GetBonePosRot: Entity with ID ', ENTID, ' not found!')
            return False
        animClient = entity.GetComponent('animation')
        posComp = entity.GetComponent('position')
        if animClient is not None and posComp is not None:
            if animClient.controller is not None:
                boneTransform = animClient.controller.animationNetwork.GetBoneTransform(boneName)
                if boneTransform:
                    (translation, orientation,) = boneTransform
                    translation = geo2.QuaternionTransformVector(posComp.rotation, translation)
                    translation = geo2.Vec3Add(posComp.position, translation)
                    orientation = geo2.QuaternionMultiply(posComp.rotation, orientation)
                    translation = list(translation)
                    orientation = list(orientation)
                    GameWorld.AddPropertyForCurrentPythonProc({posProp: translation})
                    GameWorld.AddPropertyForCurrentPythonProc({rotProp: orientation})
                    return True
        self.LogError('GetBonePosRot: Missing critical data in entity!')
        return False



    def _SetEntityPosition(self, ENTID, ALIGN_POSITION, ALIGN_ROTATION, MotionState):
        uthread.worker('_SetEntityPosition', self._SetEntityPositionTasklet, ENTID, ALIGN_POSITION, ALIGN_ROTATION, MotionState)
        return True



    def _SetEntityPositionTasklet(self, ENTID, ALIGN_POSITION, ALIGN_ROTATION, MotionState):
        entity = self.entityService.FindEntityByID(ENTID)
        if entity is not None:
            if MotionState is MOTIONSTATE_NO_CHANGE:
                positionComponent = entity.GetComponent('position')
                if positionComponent is not None:
                    positionComponent.rotation = ALIGN_ROTATION
                    positionComponent.position = ALIGN_POSITION
            else:
                movementComponent = entity.GetComponent('movement')
                if movementComponent is not None:
                    if MotionState is MOTIONSTATE_KEY_FRAME:
                        movementComponent.avatar.SetKeyFrameMode(ALIGN_POSITION, ALIGN_ROTATION)
                    elif MotionState is MOTIONSTATE_CHARACTER:
                        movementComponent.avatar.SetCharacterMode(ALIGN_POSITION, ALIGN_ROTATION)



    def _SetAllowedToMove(self, ENTID, allowedToMove):
        entity = self.entityService.FindEntityByID(ENTID)
        if entity is not None:
            movementComponent = entity.GetComponent('movement')
            if movementComponent is not None:
                movementComponent.allowMovement = allowedToMove



MotionStateList = [('No Change', MOTIONSTATE_NO_CHANGE, ''), ('Key Frame', MOTIONSTATE_KEY_FRAME, ''), ('Character', MOTIONSTATE_CHARACTER, '')]

def CreateLocatorList(self):
    from locator import Locator
    locatorList = []
    locatorObjs = Locator.GetAllLocators()
    for loc in locatorObjs:
        locatorList.append((loc.GetName(), loc.GetName(), ''))

    return locatorList


exports = {'actionProperties.MotionState': ('list', MotionStateList),
 'actionProperties.LocatorList': ('listMethod', CreateLocatorList),
 'actionProcTypes.SetEntityPosition': zaction.ProcTypeDef(isMaster=True, procCategory='Entity', properties=[zaction.ProcPropertyTypeDef('MotionState', 'I', userDataType='MotionState', isPrivate=True)]),
 'actionProcTypes.GetEntitySceneID': zaction.ProcTypeDef(isMaster=True, procCategory='Entity'),
 'actionProcTypes.GetBonePosRot': zaction.ProcTypeDef(isMaster=True, procCategory='Entity', properties=[zaction.ProcPropertyTypeDef('boneName', 'S', userDataType='Bone Name', isPrivate=True), zaction.ProcPropertyTypeDef('posProp', 'S', userDataType='Position Property', isPrivate=True), zaction.ProcPropertyTypeDef('rotProp', 'S', userDataType='Rotation Property', isPrivate=True)]),
 'actionProcTypes.TeleportToLocator': zaction.ProcTypeDef(isMaster=True, procCategory='Entity', properties=[zaction.ProcPropertyTypeDef('TargetType', 'I', userDataType='TargetTypeList', isPrivate=True), zaction.ProcPropertyTypeDef('LocatorName', 'S', userDataType='LocatorList', isPrivate=True)]),
 'actionProcTypes.SetAllowedToMove': zaction.ProcTypeDef(isMaster=True, procCategory='Entity', properties=[zaction.ProcPropertyTypeDef('allowedToMove', 'B', userDataType=None, isPrivate=True)])}

