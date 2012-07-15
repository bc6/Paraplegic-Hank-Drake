#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/entities/infoClient.py
import service
import collections

class InfoComponent:
    __guid__ = 'entities.InfoComponent'

    def __init__(self, state):
        self.name = ''
        self.gender = None
        self.spawnID = None
        self.recipeID = None
        name = state.get('name', None)
        if name is not None:
            if type(name) is tuple and boot.appname == 'WOD':
                self.name = name[0]
            else:
                self.name = name
        gender = state.get('gender', None)
        if gender is not None:
            self.gender = gender
        spawnID = state.get('_spawnID', None)
        if spawnID is not None:
            self.spawnID = spawnID
        recipeID = state.get('_recipeID', None)
        if recipeID is not None:
            self.recipeID = recipeID


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
        report['Gender'] = component.gender
        report['SpawnID'] = component.spawnID
        report['RecipeID'] = component.recipeID
        return report