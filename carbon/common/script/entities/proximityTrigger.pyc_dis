#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/entities/proximityTrigger.py
import collections
import GameWorld
import service
import geo2
import util

class ProximityTriggerComponent:
    __guid__ = 'physics.ProximityTriggerComponent'


class ProximityTriggerScene:

    def __init__(self):
        self.enterCallbacks = {}
        self.exitCallbacks = {}

    def OnEnter(self, causingEntityID, triggerEntityID):
        try:
            self.enterCallbacks[triggerEntityID](causingEntityID, triggerEntityID)
        except KeyError:
            pass

    def OnExit(self, causingEntityID, triggerEntityID):
        try:
            self.exitCallbacks[triggerEntityID](causingEntityID, triggerEntityID)
        except KeyError:
            pass


class ProximityTriggerService(service.Service):
    __guid__ = 'svc.proximityTrigger'
    __componentTypes__ = ['proximityTrigger']

    def Run(self, *memStream):
        self.scenes = {}

    def OnLoadEntityScene(self, sceneID):
        scene = ProximityTriggerScene()
        self.scenes[sceneID] = scene

    def OnEntitySceneLoaded(self, sceneID):
        gw = GameWorld.Manager.GetGameWorld(long(sceneID))
        gw.triggerReportHandler = self.scenes[sceneID]

    def OnUnloadEntityScene(self, sceneID):
        gw = GameWorld.Manager.GetGameWorld(long(sceneID))
        if gw:
            gw.triggerReportHandler = None
        del self.scenes[sceneID]

    def CreateComponent(self, name, state):
        component = ProximityTriggerComponent()
        if 'radius' in state:
            component.radius = state['radius']
        elif 'dimensions' in state:
            if type(state['dimensions']) == type(str()):
                component.dimensions = util.UnpackStringToTuple(state['dimensions'], float)
            else:
                component.dimensions = state['dimensions']
        else:
            self.LogError('Unknown trigger shape')
            return None
        if 'relativepos' in state:
            if type(state['relativepos']) == type(str()):
                component.relativePosition = util.UnpackStringToTuple(state['relativepos'], float)
            else:
                component.relativePosition = state['relativepos']
        else:
            component.relativePosition = (0, 0, 0)
        return component

    def ReportState(self, component, entity):
        state = collections.OrderedDict()
        if hasattr(component, 'radius'):
            state['radius'] = component.radius
        elif hasattr(component, 'dimensions'):
            state['dimensions'] = component.dimensions
        else:
            raise RuntimeError('Unknown trigger shape')
        if hasattr(component, 'relativepos'):
            state['relativepos'] = component.relativepos
        return state

    def PackUpForSceneTransfer(self, component, destinationSceneID):
        return self.PackUpForClientTransfer(component)

    def PackUpForClientTransfer(self, component):
        state = {}
        if hasattr(component, 'radius'):
            state['radius'] = component.radius
        elif hasattr(component, 'dimensions'):
            state['dimensions'] = component.dimensions
        else:
            raise RuntimeError('Unknown trigger shape')
        state['relativepos'] = component.relativePosition
        return state

    def UnPackFromSceneTransfer(self, component, entity, state):
        if 'radius' in state:
            component.radius = state['radius']
        elif 'dimensions' in state:
            component.dimensions = state['dimensions']
        else:
            raise RuntimeError('Unknown trigger shape')
        component.relativePosition = state['relativepos']
        return component

    def SetupComponent(self, entity, component):
        self.LogInfo('Setting up component', component)
        gw = GameWorld.Manager.GetGameWorld(long(entity.scene.sceneID))
        if hasattr(component, 'radius'):
            gw.CreateTriggerSphere(entity.entityID, geo2.Add(entity.position.position, component.relativePosition), entity.position.rotation, component.radius)
        elif hasattr(component, 'dimensions'):
            gw.CreateTriggerAABB(entity.entityID, geo2.Add(entity.position.position, component.relativePosition), entity.position.rotation, component.dimensions)
        else:
            raise RuntimeError('Unknown trigger shape')
        self.LogInfo('Creating trigger shape for component', component)

    def PreTearDownComponent(self, entity, component):
        try:
            del self.scenes[entity.scene.sceneID].enterCallbacks[entity.entityID]
        except KeyError:
            pass

        try:
            del self.scenes[entity.scene.sceneID].exitCallbacks[entity.entityID]
        except KeyError:
            pass

        gw = GameWorld.Manager.GetGameWorld(long(entity.scene.sceneID))
        gw.RemoveTriggerShape(entity.entityID)

    def RegisterExitCallback(self, sceneID, triggerID, callback):
        self.scenes[sceneID].exitCallbacks[triggerID] = callback

    def RegisterEnterCallback(self, sceneID, triggerID, callback):
        self.scenes[sceneID].enterCallbacks[triggerID] = callback