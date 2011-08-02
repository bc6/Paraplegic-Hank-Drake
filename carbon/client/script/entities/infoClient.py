import service
import collections

class InfoComponent:
    __guid__ = 'entities.InfoComponent'

    def __init__(self, state):
        self.name = ''
        name = state.get('name', None)
        if name is not None:
            if type(name) is tuple:
                self.name = Tr(*name)
            else:
                self.name = name




class InfoClient(service.Service):
    __guid__ = 'svc.infoClient'
    __exportedcalls__ = {}
    __notifyevents__ = []
    __componentTypes__ = ['info']

    def CreateComponent(self, name, state):
        return InfoComponent(state)



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['Name'] = component.name
        return report




