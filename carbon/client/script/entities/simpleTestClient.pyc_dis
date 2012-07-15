#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/entities/simpleTestClient.py
import service
import collections

class SimpleTestClientComponent:
    __guid__ = 'entity.SimpleTestClientComponent'

    def __init__(self):
        self.someState = 'DefaultState'


class SimpleTestClient(service.Service):
    __guid__ = 'svc.simpleTestClient'
    __notifyevents__ = []
    __componentTypes__ = ['simpleTestComponent']

    def Run(self, *etc):
        service.Service.Run(self, etc)
        self.Running = True

    def CreateComponent(self, name, state):
        component = SimpleTestClientComponent()
        component.__dict__.update(state)
        return component

    def PrepareComponent(self, sceneID, entityID, component):
        pass

    def SetupComponent(self, entity, component):
        component.isSetup = True

    def RegisterComponent(self, entity, component):
        pass

    def ReportState(self, component, entity):
        report = collections.OrderedDict(sorted(component.__dict__.items()))
        return report

    def UnRegisterComponent(self, entity, component):
        pass

    def PreTearDownComponent(self, entity, component):
        component.isSetup = False

    def TearDownComponent(self, entity, component):
        pass