#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/entities/spawnLocationClient.py
import collections
import service

class SpawnLocationComponent:
    __guid__ = 'component.SpawnLocationComponent'


class SpawnLocationClient(service.Service):
    __guid__ = 'svc.spawnLocationClient'
    __componentTypes__ = ['spawnLocation']

    def __init__(self, *args, **kwargs):
        service.Service.__init__(self, *args, **kwargs)
        self.spawnLocationEntities = collections.defaultdict(list)

    def CreateComponent(self, name, state):
        component = SpawnLocationComponent()
        component.spawnLocationType = state['spawnLocationType']
        component.cameraYaw = state['cameraYaw']
        component.cameraPitch = state['cameraPitch']
        component.cameraZoom = state['cameraZoom']
        return component

    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['spawnLocationType'] = component.spawnLocationType
        return report

    def SetupComponent(self, entity, component):
        self.spawnLocationEntities[entity.scene.sceneID].append(entity)

    def UnRegisterComponent(self, entity, component):
        self.spawnLocationEntities[entity.scene.sceneID].remove(entity)

    def GetSpawnLocationsBySceneID(self, sceneID):
        return self.spawnLocationEntities[sceneID]