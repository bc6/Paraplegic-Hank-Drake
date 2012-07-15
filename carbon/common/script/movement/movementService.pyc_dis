#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/movement/movementService.py
import service
import collections
import geo2
import GameWorld

class CommonMovementComponent(object):
    __guid__ = 'movement.CommonMovementComponent'
    __gwattrs__ = ('pos', 'rot', 'vel', 'localHeading', 'moveMode')

    def __init__(self):
        self.characterControllerInfo = GameWorld.CharacterControllerInfo()
        self.physics = GameWorld.PhysicsComponent()
        self.moveState = GameWorld.MoveStateComponent()
        self.characterController = GameWorld.CharacterController()
        self.moveModeManager = None

    def GetPosition(self):
        return self.characterController.positionComponent.position

    def GetRotation(self):
        return self.characterController.positionComponent.rotation

    def InitializeCapsuleInfo(self, state):
        self.characterControllerInfo.height = state.get('height', const.AVATAR_HEIGHT)
        self.characterControllerInfo.radius = state.get('radius', const.AVATAR_RADIUS)
        self.characterControllerInfo.stepHeight = 0.5
        self.characterControllerInfo.slopeLimitDegrees = 45.0
        self.characterControllerInfo.stickRadius = self.characterControllerInfo.radius * 0.5
        self.characterControllerInfo.stickSharpness = 0.2

    def InitializeCharacterControllerRefs(self, positionComponent):
        self.characterController.positionComponent = positionComponent
        self.characterController.moveState = self.moveState
        self.characterController.physics = self.physics
        self.characterController.SetupPhysXCharacterController(self.characterControllerInfo)


class MovementService(service.Service):
    __guid__ = 'movement.movementService'
    __dependencies__ = ['machoNet']
    __componentTypes__ = ['movement']

    def Run(self, *etc):
        self.MoveModeSysManager = GameWorld.GetMoveModeSysManagerSingleton()

    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        avatarTypes = {const.movement.AVATARTYPE_UNKNOWN: 'Unknown type',
         const.movement.AVATARTYPE_CLIENT_LOCALPLAYER: 'Client local player',
         const.movement.AVATARTYPE_CLIENT_NPC: 'Client NPC',
         const.movement.AVATARTYPE_CLIENT_REMOTEPLAYER: 'Client remote player',
         const.movement.AVATARTYPE_SERVER_PLAYER: 'Server player',
         const.movement.AVATARTYPE_SERVER_NPC: 'Server NPC'}
        report['Avatar Type'] = avatarTypes.get(component.moveModeManager.avatarType, 'Bad Type')
        report['Move Mode'] = str(component.moveModeManager.GetCurrentMode())
        report['Is Allowed To Mode'] = component.moveModeManager.allowedToMove
        report['Is On Ground'] = component.characterController.groundCollision
        report['Capsule Radius'] = '%.2f' % component.characterControllerInfo.radius
        report['Capsule Height'] = '%.2f' % component.characterControllerInfo.height
        metaState = self.movementStates.metaStates[component.moveState.GetMetaStateIndex()]
        report['MoveState MetaState'] = metaState[const.movement.METASTATE_NAME]
        staticState = metaState[const.movement.METASTATE_STATIC_STATES][component.moveState.GetStaticStateIndex()]
        report['MoveState StaticState'] = staticState[const.movement.STATICSTATE_NAME]
        report['MoveState BaseSpeed'] = component.moveState.GetBaseSpeed()
        return report

    def PrepareComponent(self, sceneID, entityID, component):
        component.characterControllerInfo.entityID = entityID
        component.characterControllerInfo.sceneID = sceneID
        component.sceneID = sceneID

    def SetupComponent(self, entity, component):
        pass

    def RegisterComponent(self, entity, component):
        self.MoveModeSysManager.AddEntity(entity.entityID, component.moveModeManager)
        component.moveModeManager.Register()

    def UnRegisterComponent(self, entity, component):
        self.MoveModeSysManager.RemoveEntity(entity.entityID, component.moveModeManager)

    def PreTearDownComponent(self, entity, component):
        component.moveModeManager.Remove()

    def TearDownComponent(self, entity, component):
        component.moveModeManager = None
        component.characterControllerInfo = None
        component.physics = None
        component.moveState = None
        component.characterController = None